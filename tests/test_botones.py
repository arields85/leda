"""Pruebas de los botones: de la cola a Telegram y del toque de vuelta.

Un botón cierra el circuito que las acciones pendientes dejaron preparado. Lo
que se prueba acá es el camino completo — que el mensaje salga con sus
opciones dibujadas, y que el toque de la persona correcta ejecute la acción
que estaba congelada.

El toque de la persona equivocada es el caso que más importa: en un grupo el
botón lo ve todo el equipo.
"""

from __future__ import annotations

import dataclasses
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from prisma import gateway
from prisma import pendientes as P
from prisma.autoridad import Canal, identificar
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.despachador import TransporteDePrueba, despachar
from prisma.llm import ProveedorGuionado, Respuesta

BA = ZoneInfo("America/Argentina/Buenos_Aires")
AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _telegram_id(cur, nombre) -> int:
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return cur.fetchone()["t"]


def _tarea(cur, ws, persona="Marcos Tarquini"):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Integrar comprimidora 3') returning id""",
        (ws,))
    obj = cur.fetchone()["id"]
    cur.execute("set local role prisma_admin")
    # Por la vista y no por app_user: bajo el rol del agente esa tabla no se
    # toca, que es exactamente lo que el esquema quiere.
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, fecha_objetivo,
                             criterio_aceptacion, evidencia_requerida)
           values (%s, %s, 'Programar PLC',
                   (select id from area where workspace_id = %s and slug = 'ot'),
                   (select membership_id from integrante where nombre = %s),
                   '2026-08-14', 'PLC probado', array['resultado_de_prueba'])
           returning id""",
        (ws, obj, ws, persona))
    t = cur.fetchone()["id"]
    cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                "values (%s, 'asignada', 'prisma')", (t,))
    cur.execute("set local role prisma_app")
    return str(t)


# ---------------------------------------------------------------------------
# Salida: el mensaje sale con sus botones
# ---------------------------------------------------------------------------

def test_un_mensaje_con_accion_pendiente_sale_con_sus_opciones(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        p = P.registrar(
            cur, quien, herramienta="cambiar_fecha",
            args={"tarea_id": _tarea(cur, ws), "fecha_objetivo": "2026-08-20"},
            resumen="mover la fecha al 20/08",
            vence_en=AHORA + timedelta(days=1), chat_id=500)

        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, cuerpo, estado, dedupe_key,
                  es_respuesta, programado_para, pending_action_id)
               values (%s, 500, 'Confirmame esto', 'listo', 'b1', true, %s, %s)""",
            (ws, AHORA, p.id))

        cal = Calendario.desde_base(cur, ws)
        transporte = TransporteDePrueba()
        despachar(cur, ws, transporte, cal, AHORA)

        assert transporte.enviados[0].texto == "Confirmame esto"
        etiquetas = [b.etiqueta for b in transporte.enviados[0].botones]
        assert etiquetas == ["Confirmar", "Cancelar"]


def test_un_mensaje_comun_sale_sin_botones(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, cuerpo, estado, dedupe_key,
                  es_respuesta, programado_para)
               values (%s, 500, 'buen día', 'listo', 'b2', true, %s)""",
            (ws, AHORA))

        cal = Calendario.desde_base(cur, ws)
        transporte = TransporteDePrueba()
        despachar(cur, ws, transporte, cal, AHORA)

        assert transporte.enviados[0].botones == []


# ---------------------------------------------------------------------------
# Entrada: el toque
# ---------------------------------------------------------------------------

@pytest.fixture
def cliente(corework, conn, monkeypatch):
    # Sin esto cada toque sale de verdad a api.telegram.org con un token de
    # mentira: la prueba pasa igual —el acuse se ignora si falla— pero tarda
    # segundos y depende de que haya red. Los tests que miran el acuse lo
    # vuelven a reemplazar por el suyo.
    monkeypatch.setattr(gateway, "acusar_toque", lambda *a, **k: None)
    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    monkeypatch.setattr(
        "prisma.llm.desde_base",
        lambda cur, ws, key: ProveedorGuionado([Respuesta(texto="Anotado.")]))
    return TestClient(gateway.app)


def _tocar(cliente, token, user_id):
    return cliente.post(
        "/telegram/corework",
        json={"callback_query": {
            "id": "cb1", "from": {"id": user_id}, "data": f"p:{token}",
            "message": {"message_id": 7, "chat": {"id": user_id}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def test_el_toque_ejecuta_la_accion_congelada(cliente, conn, corework):
    """Lo que hoy no pasa: confirmar tiene que ejecutar."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        tarea = _tarea(cur, ws)
        p = P.registrar(
            cur, quien, herramienta="actualizar_estado",
            args={"tarea_id": tarea, "estado": "en_curso"},
            resumen="poner Programar PLC en curso",
            vence_en=datetime.now(timezone.utc) + timedelta(days=1),
            chat_id=500)
        token = P.opcion_por_etiqueta(cur, p.id, "Confirmar").token
        tg = _telegram_id(cur, "Marcos Tarquini")
    conn.commit()

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tarea,))
        assert cur.fetchone()["estado"] == "en_curso"
        cur.execute("select estado from pending_action where id = %s", (p.id,))
        assert cur.fetchone()["estado"] == "resuelta"


def test_el_toque_de_otro_integrante_no_ejecuta(cliente, conn, corework):
    """En un grupo el botón lo ve todo el equipo. Verlo no es poder apretarlo."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        tarea = _tarea(cur, ws)
        p = P.registrar(
            cur, marcos, herramienta="actualizar_estado",
            args={"tarea_id": tarea, "estado": "en_curso"},
            resumen="poner Programar PLC en curso",
            vence_en=datetime.now(timezone.utc) + timedelta(days=1),
            chat_id=500)
        token = P.opcion_por_etiqueta(cur, p.id, "Confirmar").token
        ajeno = _telegram_id(cur, "Ariel De Simone")
    conn.commit()

    assert _tocar(cliente, token, ajeno).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tarea,))
        assert cur.fetchone()["estado"] == "asignada"      # intacta
        cur.execute("select estado from pending_action where id = %s", (p.id,))
        assert cur.fetchone()["estado"] == "esperando"     # sigue esperando


def test_confirmar_una_preparacion_que_rechaza_no_se_audita_como_ejecutada(
        cliente, conn, corework):
    """Mismo defecto que el corregido en `agente._ejecutar_una` (banco
    b-0005-a), acá en el camino de Confirmar por botón: `preparar` se corre
    de nuevo al confirmar (`ya_confirmada=True`) y puede rechazar aunque la
    huella no cambió -- acá, simulado con una dependencia bloqueante que se
    agrega DESPUÉS de armar la vista previa, sin tocar el estado de la tarea
    (mismo `tarea_id`/`estado` que arma la huella). Confirmar no puede
    auditarse como `herramienta:actualizar_estado` (no escribió nada) ni
    decirle "Hecho" a la persona."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        destino = _tarea(cur, ws, persona="Marcos Tarquini")
        origen = _tarea(cur, ws, persona="Nahuel Gimenez")
        p = P.registrar(
            cur, quien, herramienta="actualizar_estado",
            args={"tarea_id": destino, "estado": "en_curso"},
            resumen="poner Programar PLC en curso",
            vence_en=datetime.now(timezone.utc) + timedelta(days=1),
            chat_id=500)
        token = P.opcion_por_etiqueta(cur, p.id, "Confirmar").token
        tg = _telegram_id(cur, "Marcos Tarquini")
        cur.execute("set local role prisma_admin")
        cur.execute(
            """insert into dependency (workspace_id, origen_task_id,
                                       destino_task_id, tipo)
               values (%s, %s, %s, 'bloqueante')""", (ws, origen, destino))
        cur.execute("set local role prisma_app")
    conn.commit()

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (destino,))
        assert cur.fetchone()["estado"] == "asignada"          # no se aplicó
        cur.execute(
            "select count(*) n from audit_log where accion = 'herramienta:actualizar_estado'")
        assert cur.fetchone()["n"] == 0
        cur.execute(
            """select detalle from audit_log
                where accion = 'herramienta_rechazada:actualizar_estado'""")
        f = cur.fetchone()
        assert f is not None
        assert f["detalle"]["rechazo"]["iniciada"] is False
        cur.execute(
            """select cuerpo from message_outbox
                where workspace_id = %s and chat_id = %s
               order by programado_para desc limit 1""", (ws, tg))
        cuerpo = cur.fetchone()["cuerpo"]
    assert cuerpo != "Hecho."
    assert "bloqueante" in cuerpo.lower() or "dependencia" in cuerpo.lower()


def test_cancelar_no_ejecuta_pero_cierra_la_accion(cliente, conn, corework):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        tarea = _tarea(cur, ws)
        p = P.registrar(
            cur, quien, herramienta="actualizar_estado",
            args={"tarea_id": tarea, "estado": "en_curso"},
            resumen="poner Programar PLC en curso",
            vence_en=datetime.now(timezone.utc) + timedelta(days=1),
            chat_id=500)
        token = P.opcion_por_etiqueta(cur, p.id, "Cancelar").token
        tg = _telegram_id(cur, "Marcos Tarquini")
    conn.commit()

    _tocar(cliente, token, tg)

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tarea,))
        assert cur.fetchone()["estado"] == "asignada"
        cur.execute("select estado from pending_action where id = %s", (p.id,))
        assert cur.fetchone()["estado"] == "cancelada"


def test_el_toque_de_un_desconocido_no_hace_nada(cliente, conn, corework):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        p = P.registrar(
            cur, quien, herramienta="actualizar_estado",
            args={"tarea_id": _tarea(cur, ws), "estado": "en_curso"},
            resumen="poner Programar PLC en curso",
            vence_en=datetime.now(timezone.utc) + timedelta(days=1))
        token = P.opcion_por_etiqueta(cur, p.id, "Confirmar").token
    conn.commit()

    assert _tocar(cliente, token, 424242).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (p.id,))
        assert cur.fetchone()["estado"] == "esperando"


def test_el_toque_se_acusa_para_que_no_quede_el_reloj_girando(
        cliente, conn, corework, monkeypatch):
    """El único lugar donde Prisma le habla a Telegram sin pasar por la cola."""
    acusados = []
    monkeypatch.setattr(
        gateway, "acusar_toque",
        lambda token, callback_id, cliente=None: acusados.append(callback_id))

    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        p = P.registrar(
            cur, quien, herramienta="actualizar_estado",
            args={"tarea_id": _tarea(cur, ws), "estado": "en_curso"},
            resumen="poner Programar PLC en curso",
            vence_en=datetime.now(timezone.utc) + timedelta(days=1),
            chat_id=500)
        token = P.opcion_por_etiqueta(cur, p.id, "Confirmar").token
        tg = _telegram_id(cur, "Marcos Tarquini")
    conn.commit()

    _tocar(cliente, token, tg)

    assert acusados == ["cb1"]


def test_si_falla_el_acuse_la_accion_igual_se_ejecuta(
        cliente, conn, corework, monkeypatch):
    """El acuse es cosmético. Que se caiga la red no puede perder el trabajo."""
    def explota(token, callback_id, cliente=None):
        raise ConnectionError("telegram no responde")

    monkeypatch.setattr(gateway, "acusar_toque", explota)

    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        tarea = _tarea(cur, ws)
        p = P.registrar(
            cur, quien, herramienta="actualizar_estado",
            args={"tarea_id": tarea, "estado": "en_curso"},
            resumen="poner Programar PLC en curso",
            vence_en=datetime.now(timezone.utc) + timedelta(days=1),
            chat_id=500)
        token = P.opcion_por_etiqueta(cur, p.id, "Confirmar").token
        tg = _telegram_id(cur, "Marcos Tarquini")
    conn.commit()

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tarea,))
        assert cur.fetchone()["estado"] == "en_curso"


class _HttpFalso:
    """Responde a getUpdates sin salir a la red, y guarda qué se pidió."""

    def __init__(self) -> None:
        self.params: dict = {}

    def get(self, url, params=None):
        self.params = params or {}
        return self

    def raise_for_status(self):
        return None

    def json(self):
        return {"result": []}


def test_el_modo_local_pide_los_toques_de_boton(corework, conn):
    """Con polling hay que pedir callback_query explícitamente.

    Telegram no manda lo que no se le pide. Sin esto, en la prueba local los
    botones se dibujan y al tocarlos no pasa nada — y el problema no se ve por
    ningún lado, porque no hay error: el toque nunca llega.
    """
    from prisma.local import Escucha

    http = _HttpFalso()
    e = Escucha(conn, "corework", corework.workspace_id, "tok", cliente=http,
                authority_conn=conn)
    e.recibir(espera=0)

    assert "callback_query" in http.params["allowed_updates"]


def test_un_toque_repetido_no_ejecuta_dos_veces(cliente, conn, corework):
    """Telegram reintrega updates. Y la gente toca dos veces cuando duda."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        tarea = _tarea(cur, ws)
        p = P.registrar(
            cur, quien, herramienta="actualizar_estado",
            args={"tarea_id": tarea, "estado": "en_curso"},
            resumen="poner Programar PLC en curso",
            vence_en=datetime.now(timezone.utc) + timedelta(days=1),
            chat_id=500)
        token = P.opcion_por_etiqueta(cur, p.id, "Confirmar").token
        tg = _telegram_id(cur, "Marcos Tarquini")
    conn.commit()

    _tocar(cliente, token, tg)
    _tocar(cliente, token, tg)

    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from task_state_event
                where task_id = %s and estado_nuevo = 'en_curso'""", (tarea,))
        assert cur.fetchone()["n"] == 1
