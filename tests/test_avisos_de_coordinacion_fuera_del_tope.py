"""Los avisos de coordinación quedan fuera del tope diario (decisión del usuario,
2026-09-30: "deben llegar todos los avisos").

`nucleo/mecanica-pm.md` §10 (volumen de contacto) limita los mensajes
automáticos por persona y por día (3 en corework). Ese tope es para los
seguimientos: cadencias, recordatorios de la escalera. Lo que una persona hizo
sobre trabajo compartido y otra necesita para actuar o enterarse -- una entrega
para revisar, cambios pedidos, una aprobación, un borrador para confirmar, un
borrador rechazado -- no cuenta contra el tope ni lo posterga (`es_coordinacion`).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from prisma import herramientas as H
from prisma import pendientes as P
from prisma.db import admin, espacio
from prisma.salida import enqueue_outbox

from tests.test_ramas_cerradas_al_terminar_el_flujo import (  # noqa: F401
    _activa, _enviados_a, _pasada, _quien, reloj)


def _seguimientos(cur, ws, tg, membership_id, n, *, prefijo):
    for i in range(n):
        enqueue_outbox(cur, workspace_id=ws, chat_id=tg, text=f"Seguimiento {i}",
                       recipient_membership_id=membership_id,
                       message_type="seguimiento",
                       scheduled_for=datetime.now(timezone.utc)
                       - timedelta(minutes=2), dedupe_key=f"{prefijo}:s{i}")


def _avisos(cur, ws, quien, membership_id, n, *, prefijo):
    for i in range(n):
        H._avisar(cur, quien, membership_id, f"Aviso de coordinación {i}",
                  dedupe_key=f"{ws}:{prefijo}:c{i}")


def _nahuel(conn, ws):
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        cur.execute("select telegram_user_id t from integrante where nombre = %s",
                    ("Nahuel Gimenez",))
        return quien, cur.fetchone()["t"]


def test_cinco_avisos_de_coordinacion_en_un_dia_salen_todos(corework, conn, reloj):
    ws = corework.workspace_id
    nahuel, tg = _nahuel(conn, ws)
    with espacio(conn, ws) as cur:
        _avisos(cur, ws, nahuel, nahuel.membership_id, 5, prefijo="tope-c")
    conn.commit()

    resumen, transporte = _pasada(conn, ws, reloj.en_horario())

    enviados = [t for t in _enviados_a(transporte, tg) if "coordinación" in t]
    assert len(enviados) == 5
    assert resumen["pospuestos"] == 0


def test_los_seguimientos_siguen_deteniendose_en_el_tope(corework, conn, reloj):
    ws = corework.workspace_id
    nahuel, tg = _nahuel(conn, ws)
    with espacio(conn, ws) as cur:
        _seguimientos(cur, ws, tg, nahuel.membership_id, 5, prefijo="tope-s")
    conn.commit()

    resumen, transporte = _pasada(conn, ws, reloj.en_horario())

    assert len([t for t in _enviados_a(transporte, tg)
                if t.startswith("Seguimiento")]) == 3
    assert resumen["pospuestos"] == 2


def test_un_aviso_de_coordinacion_no_consume_la_cuota_de_los_seguimientos(
        corework, conn, reloj):
    """La lectura conservadora: no cuenta en absoluto. Cinco avisos de coordinación
    ya enviados hoy no le quitan a la persona ninguno de sus tres seguimientos."""
    ws = corework.workspace_id
    nahuel, tg = _nahuel(conn, ws)
    ahora = reloj.en_horario()
    with espacio(conn, ws) as cur:
        _avisos(cur, ws, nahuel, nahuel.membership_id, 5, prefijo="cuota")
    conn.commit()
    _pasada(conn, ws, ahora)
    with espacio(conn, ws) as cur:
        _seguimientos(cur, ws, tg, nahuel.membership_id, 4, prefijo="cuota")
    ahora = reloj.en_horario()

    resumen, transporte = _pasada(conn, ws, ahora)

    assert len([t for t in _enviados_a(transporte, tg)
                if t.startswith("Seguimiento")]) == 3
    assert resumen["pospuestos"] == 1


def test_la_retencion_por_rama_abierta_alcanza_a_los_dos_tipos(corework, conn, reloj):
    """T9-R1d-2: mientras la persona está activa en una rama abierta, lo que Prisma
    le inicia espera, sea seguimiento o aviso de coordinación."""
    ws = corework.workspace_id
    nahuel, tg = _nahuel(conn, ws)
    ahora = datetime.now(timezone.utc)
    with espacio(conn, ws) as cur:
        cur.execute(
            """insert into inbound_message (workspace_id, chat_id, app_user_id, texto)
               values (%s, %s, %s, 'hola')""", (ws, tg, nahuel.app_user_id))
        P.registrar(cur, nahuel, herramienta="actualizar_estado", args={},
                    resumen="¿Qué estado?", vence_en=ahora + timedelta(hours=8),
                    campo="estado", chat_id=tg)
        _seguimientos(cur, ws, tg, nahuel.membership_id, 1, prefijo="rama")
        _avisos(cur, ws, nahuel, nahuel.membership_id, 1, prefijo="rama")
    conn.commit()

    resumen, transporte = _pasada(conn, ws, reloj.en_horario())

    assert resumen["retenidos"] == 2
    assert _enviados_a(transporte, tg) == []


def test_las_herramientas_que_avisan_de_un_acto_ajeno_marcan_el_aviso(
        corework, conn):
    ws = corework.workspace_id
    nahuel, tg = _nahuel(conn, ws)
    with espacio(conn, ws) as cur:
        H._avisar(cur, nahuel, nahuel.membership_id, "Marcos aprobó «X»",
                  dedupe_key=f"{ws}:marca:1")
        cur.execute("select es_coordinacion from message_outbox "
                    "where dedupe_key = %s", (f"{ws}:marca:1",))
        assert cur.fetchone()["es_coordinacion"] is True
        enqueue_outbox(cur, workspace_id=ws, chat_id=tg, text="Recordatorio",
                       dedupe_key=f"{ws}:marca:2")
        cur.execute("select es_coordinacion from message_outbox "
                    "where dedupe_key = %s", (f"{ws}:marca:2",))
        assert cur.fetchone()["es_coordinacion"] is False
