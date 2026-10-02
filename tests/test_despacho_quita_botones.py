"""Una vista previa o una elección resuelta deja de mostrar sus botones (C0-6).

Ronda C0-C (2026-10-02, hallazgo H4): el resumen ya confirmado siguió mostrando
Confirmar, Modificar y Cancelar en Telegram, y Leda ofrecía así lo que ya no se podía
hacer (ADR 0013, regla 3: sólo opciones posibles). Cuando la acción pendiente o la
elección del alta de un mensaje ya enviado se resuelve (confirmada, cancelada,
enviada, rechazada o vencida), el despachador le quita los botones con
`editMessageReplyMarkup`, por el mismo camino y bajo el mismo espacio que el resto de
la salida. La marca `message_outbox.botones_quitados_en` lo hace una sola vez. Que
Telegram diga que el mensaje ya no tiene botones o ya no existe es lo mismo que
haberlos quitado; cualquier otra falla deja un incidente, nunca un silencio. Un toque
que llegue antes o a pesar de esto lo contesta C0-5 con el estado real.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from leda import pendientes as P
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.despachador import ErrorTelegram, TransporteDePrueba, despachar
from leda.salida import enqueue_outbox

from tests.test_alta_eleccion_confirmacion import _alta_con_eleccion
from tests.test_task_intake import NOW, _actor

ETAPA = "quitar_botones"


def _ahora():
    return datetime.now(timezone.utc)


def _pasada(conn, ws, transporte, ahora=None) -> None:
    with espacio(conn, ws) as cur:
        despachar(cur, ws, transporte, Calendario.desde_base(cur, ws),
                  ahora or _ahora())
    conn.commit()


def _pregunta_enviada(conn, world, transporte, slug="north-lab") -> tuple[str, str]:
    """Una pregunta con dos botones, ya entregada a Telegram: (espacio, acción)."""
    ws = world[slug]["id"]
    with espacio(conn, ws) as cur:
        quien = _actor(cur, world, slug)
        chat = world[slug]["people"]["Taylor Quinn"]["telegram"]
        p = P.registrar(
            cur, quien, herramienta=P.SENTINEL_OPCIONES_MODELO, args={},
            resumen="¿Cuál?", vence_en=_ahora() + timedelta(hours=1),
            campo="eleccion", opciones=[("Una", "1"), ("Otra", "2")], chat_id=chat)
        enqueue_outbox(cur, workspace_id=ws, chat_id=chat, text="¿Cuál?",
                       dedupe_key=f"prueba:{p.id}", is_response=True,
                       recipient_membership_id=quien.membership_id,
                       scheduled_for=_ahora(), pending_action_id=p.id)
    conn.commit()
    _pasada(conn, ws, transporte)
    assert transporte.enviados and transporte.enviados[-1].botones
    return ws, str(p.id)


def _resolver(conn, pid, estado="resuelta") -> None:
    with admin(conn) as cur:
        cur.execute("update pending_action set estado = %s where id = %s",
                    (estado, pid))
    conn.commit()


def _fila(conn, pid) -> dict:
    with admin(conn) as cur:
        cur.execute("""select chat_id, telegram_message_id, botones_quitados_en
                         from message_outbox where pending_action_id = %s""", (pid,))
        return cur.fetchone()


def _incidentes(conn) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select * from incident where etapa = %s", (ETAPA,))
        return cur.fetchall()


# ------------------------------------------------------------------ el mecanismo

def test_una_pregunta_resuelta_pierde_sus_botones_una_sola_vez(intake_world, conn):
    transporte = TransporteDePrueba()
    ws, pid = _pregunta_enviada(conn, intake_world, transporte)
    _resolver(conn, pid)

    _pasada(conn, ws, transporte)
    _pasada(conn, ws, transporte)                                # idempotente

    fila = _fila(conn, pid)
    assert transporte.quitados == [(fila["chat_id"], fila["telegram_message_id"])]
    assert fila["botones_quitados_en"] is not None
    assert _incidentes(conn) == []


def test_una_pregunta_que_sigue_esperando_conserva_sus_botones(intake_world, conn):
    transporte = TransporteDePrueba()
    ws, pid = _pregunta_enviada(conn, intake_world, transporte)

    _pasada(conn, ws, transporte)

    assert transporte.quitados == []
    assert _fila(conn, pid)["botones_quitados_en"] is None


def test_una_pregunta_vencida_tambien_pierde_sus_botones(intake_world, conn):
    transporte = TransporteDePrueba()
    ws, pid = _pregunta_enviada(conn, intake_world, transporte)
    with admin(conn) as cur:
        cur.execute("update pending_action set vence_en = now() - interval '1 minute' "
                    "where id = %s", (pid,))
    conn.commit()

    _pasada(conn, ws, transporte)

    assert len(transporte.quitados) == 1


def test_una_eleccion_del_alta_ya_usada_pierde_sus_botones(intake_world, conn):
    rid = _alta_con_eleccion(conn, intake_world)
    ws = intake_world["north-lab"]["id"]
    transporte = TransporteDePrueba()
    despues = NOW + timedelta(minutes=1)          # el alta de prueba usa un reloj fijo
    _pasada(conn, ws, transporte, despues)
    with admin(conn) as cur:
        cur.execute("""select id from task_intake_choice_set
                        where request_id = %s and estado = 'active'""", (rid,))
        conjunto = cur.fetchone()["id"]
        cur.execute("update task_intake_choice_set set estado = 'consumed' "
                    "where id = %s", (conjunto,))
    conn.commit()

    _pasada(conn, ws, transporte, despues)

    with admin(conn) as cur:
        cur.execute("""select chat_id, telegram_message_id, botones_quitados_en
                         from message_outbox where intake_choice_set_id = %s""",
                    (conjunto,))
        filas = cur.fetchall()
    assert filas and all(f["botones_quitados_en"] is not None for f in filas)
    assert sorted(transporte.quitados) == sorted(
        (f["chat_id"], f["telegram_message_id"]) for f in filas)


def test_no_toca_los_mensajes_de_otro_espacio(intake_world, conn):
    del_norte, del_oeste = TransporteDePrueba(), TransporteDePrueba()
    ws_norte, _ = _pregunta_enviada(conn, intake_world, del_norte)
    _, pid_oeste = _pregunta_enviada(conn, intake_world, del_oeste,
                                     slug="west-studio")
    _resolver(conn, pid_oeste)

    _pasada(conn, ws_norte, del_norte)

    assert del_norte.quitados == []
    assert _fila(conn, pid_oeste)["botones_quitados_en"] is None


# ------------------------------------------------------------------ las fallas

def test_si_telegram_dice_que_ya_no_hay_nada_que_quitar_queda_hecho(intake_world,
                                                                    conn):
    for i, descripcion in enumerate((
            "HTTPStatusError HTTP 400: Bad Request: message is not modified",
            "HTTPStatusError HTTP 400: Bad Request: message to edit not found")):
        transporte = TransporteDePrueba()
        ws, pid = _pregunta_enviada(conn, intake_world, transporte)
        transporte.falla_al_quitar = ErrorTelegram(descripcion)
        _resolver(conn, pid)

        _pasada(conn, ws, transporte)

        assert _fila(conn, pid)["botones_quitados_en"] is not None, descripcion
    assert _incidentes(conn) == []


def test_otra_falla_deja_un_incidente_y_no_se_reintenta_sin_fin(intake_world, conn):
    transporte = TransporteDePrueba()
    ws, pid = _pregunta_enviada(conn, intake_world, transporte)
    transporte.falla_al_quitar = ErrorTelegram("ConnectTimeout")
    _resolver(conn, pid)

    _pasada(conn, ws, transporte)
    _pasada(conn, ws, transporte)

    (incidente,) = _incidentes(conn)
    assert str(incidente["workspace_id"]) == ws
    assert incidente["referencia_tipo"] == "message_outbox"
    assert "ConnectTimeout" in incidente["referencia_cruda"]
    assert _fila(conn, pid)["botones_quitados_en"] is not None
