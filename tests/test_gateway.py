"""Pruebas del webhook.

Lo que importa acá no es que responda bien, sino que el canal determine el
sombrero y que un desconocido no obtenga información.
"""

from __future__ import annotations

from contextlib import contextmanager, nullcontext

import pytest
from fastapi.testclient import TestClient

from prisma import gateway
from prisma.db import admin
from prisma.despachador import TransporteDePrueba
from prisma.llm import ProveedorGuionado, Respuesta


@pytest.fixture
def cliente(corework, conn, monkeypatch):
    import dataclasses

    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *args, **kwargs: nullcontext())
    # Despacho inmediato (ADR 0011): un `TransporteDePrueba` propio, nunca
    # el `TransporteTelegram` real -- el token de `corework` es ficticio y
    # no hay nada real a lo que hablarle.
    transporte_falso = TransporteDePrueba()
    monkeypatch.setattr(gateway, "_transporte_de",
                        lambda slug, token: transporte_falso)
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    monkeypatch.setattr(
        "prisma.llm.desde_base",
        lambda cur, ws, key: ProveedorGuionado([Respuesta(texto="Anotado.")]))
    tc = TestClient(gateway.app)
    tc.transporte = transporte_falso
    return tc


def _update(user_id: int, texto: str = "hola", chat: int | None = None):
    return {"message": {"message_id": 1, "text": texto,
                        "chat": {"id": chat or user_id},
                        "from": {"id": user_id}}}


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
