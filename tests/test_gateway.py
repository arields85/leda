"""Pruebas del webhook.

Lo que importa acá no es que responda bien, sino que el canal determine el
sombrero y que un desconocido no obtenga información.
"""

from __future__ import annotations

import asyncio
import json
from contextlib import contextmanager, nullcontext

import pytest
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient
from starlette.requests import Request

from leda import gateway
from leda.db import admin
from leda.despachador import TransporteDePrueba
from leda.llm import ProveedorGuionado, Respuesta


@pytest.fixture
def cliente(corework, conn, uri, monkeypatch):
    import dataclasses

    from leda.db import conectar as conectar_de_verdad

    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *args, **kwargs: nullcontext())
    # Despacho inmediato (ADR 0011): un `TransporteDePrueba` propio, nunca
    # el `TransporteTelegram` real -- el token de `corework` es ficticio y
    # no hay nada real a lo que hablarle.
    transporte_falso = TransporteDePrueba()
    monkeypatch.setattr(gateway, "_transporte_de",
                        lambda slug, token: transporte_falso)
    # R3-003: el despacho de fondo abre su PROPIA conexión (`conectar()`,
    # nunca la `_conn()` compartida -- corre en otro hilo). En la prueba
    # apunta a la misma base efímera (`uri`), pero es una conexión real y
    # aparte -- fiel a lo que pasa en producción, y sin pisar `conn` (que
    # la propia prueba sigue usando para sus asserts).
    monkeypatch.setattr(gateway, "conectar", lambda: conectar_de_verdad(uri))
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    monkeypatch.setattr(
        "leda.llm.desde_base",
        lambda cur, ws, key: ProveedorGuionado([Respuesta(texto="Anotado.")]))
    tc = TestClient(gateway.app)
    tc.transporte = transporte_falso
    return tc


def _update(user_id: int, texto: str = "hola", chat: int | None = None):
    return {"message": {"message_id": 1, "text": texto,
                        "chat": {"id": chat or user_id},
                        "from": {"id": user_id}}}


def _request_con_cuerpo(payload: dict) -> Request:
    """Un `Request` de Starlette con el cuerpo ya listo, para llamar a
    `gateway.webhook` directamente (sin pasar por `TestClient`) -- R3-003:
    `TestClient` espera a que las tareas de fondo terminen antes de que
    `.post()` devuelva (verificado empíricamente), así que no sirve para
    probar que el webhook responde SIN esperarlas. Llamar a la función de
    la ruta a mano, con un `BackgroundTasks` real, deja ver exactamente qué
    quedó agendado antes de que la corrutina termine."""
    cuerpo = json.dumps(payload).encode("utf-8")
    entregado = {"listo": False}

    async def receive():
        if entregado["listo"]:
            return {"type": "http.disconnect"}
        entregado["listo"] = True
        return {"type": "http.request", "body": cuerpo, "more_body": False}

    scope = {
        "type": "http", "method": "POST", "path": "/telegram/corework",
        "headers": [(b"content-type", b"application/json")],
    }
    return Request(scope, receive)


def test_rechaza_sin_secreto(cliente):
    r = cliente.post("/telegram/corework", json=_update(9000))
    assert r.status_code == 403


def test_espacio_inexistente(cliente):
    r = cliente.post("/telegram/otro", json=_update(9000),
                     headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})
    assert r.status_code == 404


def test_desconocido_no_recibe_nada(cliente, conn):
    r = cliente.post("/telegram/corework", json=_update(424242),
                     headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})
    assert r.status_code == 200          # ACK, pero sin respuesta
    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox")
        assert cur.fetchone()["n"] == 0
        cur.execute("select count(*) n from inbound_message")
        assert cur.fetchone()["n"] == 0


def test_integrante_conocido_deja_respuesta_en_la_cola(cliente, conn):
    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user "
                    "where nombre = 'Marcos Tarquini'")
        tg = cur.fetchone()["t"]

    r = cliente.post("/telegram/corework", json=_update(tg, "¿qué tengo?"),
                     headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select texto from inbound_message")
        assert cur.fetchone()["texto"] == "¿qué tengo?"
        # Despacho inmediato (ADR 0011): ya salió, no queda 'listo' esperando
        # el próximo tick de fondo.
        cur.execute("select cuerpo, estado from message_outbox")
        fila = cur.fetchone()
        assert fila["cuerpo"] == "Anotado."
        assert fila["estado"] == "enviado"
    assert len(cliente.transporte.enviados) == 1
    assert cliente.transporte.enviados[0].texto == "Anotado."


def test_respuesta_no_espera_al_proximo_tick(cliente, conn):
    """La respuesta ya está despachada apenas vuelve el webhook -- no hace
    falta un `Ciclo.tick()` aparte (ADR 0011, decisión 1)."""
    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user "
                    "where nombre = 'Marcos Tarquini'")
        tg = cur.fetchone()["t"]

    cliente.post("/telegram/corework", json=_update(tg, "¿qué tengo?"),
                headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})

    # Nadie corrió ningún tick de fondo todavía: si esto pasa, es porque el
    # despacho ocurrió adentro del propio pedido del webhook.
    assert len(cliente.transporte.enviados) == 1


def test_webhook_no_despacha_en_linea_lo_deja_de_tarea_de_fondo(
        cliente, conn, monkeypatch):
    """R3-003 (revisión del padre sobre commit e2a094e): `webhook()` es
    `async def` y antes llamaba a `_despachar_ahora` -- síncrono, puede
    hacer un POST real a Telegram -- ANTES de devolver el ACK, bloqueando
    el bucle de eventos si el envío es lento (y arriesgando que Telegram
    reintregue el update por falta de un ACK a tiempo). Ahora el despacho
    corre como tarea de FastAPI de fondo, después de la respuesta.

    `TestClient` no sirve para probar esto (espera a que las tareas de
    fondo terminen antes de que `.post()` devuelva, verificado
    empíricamente) -- se llama a la función de la ruta directamente, con
    un `BackgroundTasks` real, y se comprueba que nada corrió todavía."""
    corridos = []
    monkeypatch.setattr(gateway, "_despachar_ahora_en_fondo",
                        lambda slug: corridos.append(slug))

    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user "
                    "where nombre = 'Marcos Tarquini'")
        tg = cur.fetchone()["t"]

    async def _pedir():
        tareas = BackgroundTasks()
        request = _request_con_cuerpo(_update(tg, "¿qué tengo?"))
        resultado = await gateway.webhook(
            "corework", request, tareas,
            x_telegram_bot_api_secret_token="s3cr3t")
        return tareas, resultado

    tareas, resultado = asyncio.run(_pedir())

    assert resultado == {"ok": True}
    # Todavía no corrió -- sólo quedó agendada para después de la respuesta.
    assert corridos == []
    assert len(tareas.tasks) == 1

    asyncio.run(tareas())   # lo que Starlette haría después de mandar el ACK
    assert corridos == ["corework"]


def test_webhook_mantiene_typing_solo_durante_el_turno(
        cliente, conn, monkeypatch):
    eventos = []

    @contextmanager
    def activo(token, chat_id, **kwargs):
        eventos.append(("inicio", chat_id))
        try:
            yield
        finally:
            eventos.append(("fin", chat_id))

    monkeypatch.setattr(gateway, "mantener_chat_activo", activo)
    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user "
                    "where nombre = 'Marcos Tarquini'")
        tg = cur.fetchone()["t"]

    r = cliente.post("/telegram/corework", json=_update(tg, "hola", chat=812),
                     headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})

    assert r.status_code == 200
    assert eventos == [("inicio", 812), ("fin", 812)]
    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox")
        assert cur.fetchone()["n"] == 1


def test_webhook_pasa_el_tipo_de_chat_al_indicador_de_actividad(
        cliente, conn, monkeypatch):
    """`chat_type` decide si el indicador intenta el borrador nativo
    (ADR 0011, decisión 2) -- acá sólo se prueba que el webhook se lo pasa
    tal como Telegram lo mandó, no el comportamiento del indicador en sí
    (cubierto en `tests/test_smoke_runtime.py`)."""
    vistos = []

    @contextmanager
    def activo(token, chat_id, **kwargs):
        vistos.append(kwargs.get("chat_type"))
        yield

    monkeypatch.setattr(gateway, "mantener_chat_activo", activo)
    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user "
                    "where nombre = 'Marcos Tarquini'")
        tg = cur.fetchone()["t"]

    update = _update(tg, "hola")
    update["message"]["chat"]["type"] = "private"
    cliente.post("/telegram/corework", json=update,
                headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})

    assert vistos == ["private"]


def test_bot_de_administracion_no_atiende_al_equipo(cliente, conn):
    """Marcos es integrante, no administrador: por el canal de administración
    no existe."""
    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user "
                    "where nombre = 'Marcos Tarquini'")
        tg = cur.fetchone()["t"]

    r = cliente.post("/telegram/admin", json=_update(tg, "cambiá el modelo"),
                     headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select count(*) n from audit_log where accion = 'mensaje_admin'")
        assert cur.fetchone()["n"] == 0
