"""Seguimientos de `review-3ebe127d376a4d18` sobre la retención de lo que Prisma
inicia (T9-R1d-2 y T9-R1d-2b, cerrados en T9-R1c-3).

- Lo que MUESTRA la propia pregunta abierta del alta nunca se retiene contra su
  propia rama: la elección lleva su `intake_choice_set_id` (`rama.id` es el id de su
  conjunto de opciones). La vista previa del propio borrador es una respuesta al acto
  de quien la confirma (T9-R1c-3b, ADR 0013 regla 2), así que una respuesta nunca se
  retiene y ya no necesita una excepción contra su rama.
- `retenidos` cuenta lo que de verdad queda esperando: no lo vencido, no una vista
  previa que ya no es la vigente, no lo que otro despachador tiene bloqueado. Y lo
  vencido de alguien retenido se descarta igual, sin esperar a que se libere.
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from prisma import ingreso_tareas as I
from prisma import pendientes as P
from prisma.autoridad import Canal, identificar
from prisma.calendario import Calendario
from prisma.db import admin, conectar, espacio
from prisma.despachador import TransporteDePrueba, despachar
from prisma.salida import enqueue_outbox

from tests.test_alta_eleccion_confirmacion import (_alta_con_eleccion,
                                                   _alta_en_confirmacion,
                                                   _alta_enviada)
from tests.test_retencion_por_rama import (AHORA, AVISO, _abrir_vista_previa,
                                           _despachar, _encolar, _estados,
                                           _preparar)
from tests.test_task_intake import NOW

# El armado del alta usa el reloj fijo `NOW`: se despacha un minuto después.
DESPUES = NOW + timedelta(minutes=1)


def _persona_del_alta(cur, world, nombre="Taylor Quinn"):
    item = world["north-lab"]
    tg = item["people"][nombre]["telegram"]
    return identificar(cur, tg, Canal.ESPACIO, item["id"]), tg


def _activa(cur, quien, tg, cuando) -> None:
    cur.execute(
        """insert into inbound_message (workspace_id, chat_id, app_user_id, texto, at)
           values (%s, %s, %s, 'hola', %s)""",
        (quien.workspace_id, tg, quien.app_user_id, cuando))


def _control(cur, ws, quien, tg, ahora=DESPUES) -> None:
    """Un aviso de Prisma a la misma persona que no es lo que muestra su rama: sí
    se retiene, y prueba que la retención está en marcha."""
    enqueue_outbox(
        cur, workspace_id=ws, chat_id=tg, text=f"{AVISO} de control",
        recipient_membership_id=quien.membership_id,
        scheduled_for=ahora - timedelta(minutes=3),
        dedupe_key="retencion:control")


def _despachar_alta(conn, ws, ahora=DESPUES):
    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        resumen = despachar(cur, ws, transporte, Calendario.desde_base(cur, ws),
                            ahora)
    conn.commit()
    return resumen, transporte


# ---------------------------- lo que muestra la propia rama no se retiene

def test_el_mensaje_que_muestra_la_eleccion_del_alta_no_se_retiene_contra_su_rama(
        conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    _alta_con_eleccion(conn, intake_world)
    with espacio(conn, ws) as cur:
        quien, tg = _persona_del_alta(cur, intake_world)
        pregunta = I.open_intake_question(cur, quien, tg)
        assert pregunta["tipo"] == I.QUESTION_CHOICE
        # `rama.id` de una elección es el id de su conjunto de opciones...
        rama = P.ver_rama_abierta(cur, quien, tg, DESPUES, (), alta=True)
        assert rama.id == pregunta["id"]
        cur.execute(
            """update message_outbox set es_respuesta = false
                where intake_choice_set_id = %s returning id""", (pregunta["id"],))
        # ...que es exactamente el que lleva el mensaje que la muestra.
        assert cur.rowcount == 1
        _activa(cur, quien, tg, DESPUES - timedelta(minutes=1))
        _control(cur, ws, quien, tg)
    conn.commit()

    resumen, transporte = _despachar_alta(conn, ws)

    assert [e.texto for e in transporte.enviados
            if e.botones and e.botones[0].callback_data.startswith("i:")]
    assert resumen["enviados"] == 1 and resumen["retenidos"] == 1
    assert _estados(conn) == {"control": "listo"}


def test_la_vista_previa_del_propio_borrador_es_una_respuesta_y_no_se_retiene(
        conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    with espacio(conn, ws) as cur:
        quien, tg = _persona_del_alta(cur, intake_world)
        rama = P.ver_rama_abierta(cur, quien, tg, DESPUES, (), alta=True)
        assert rama.id == pid                       # la `pending_action` de la vista previa
        cur.execute("select es_respuesta from message_outbox "
                    "where pending_action_id = %s", (pid,))
        assert cur.fetchone()["es_respuesta"] is True   # contesta al acto de quien confirma
        _activa(cur, quien, tg, DESPUES - timedelta(minutes=1))
        _control(cur, ws, quien, tg)
    conn.commit()

    resumen, transporte = _despachar_alta(conn, ws)

    enviados = [e for e in transporte.enviados if e.botones]
    assert len(enviados) == 1 and resumen["retenidos"] == 1
    assert [b.etiqueta.split(" ")[-1] for b in enviados[0].botones] == [
        "Confirmar", "Modificar", "Cancelar"]
    assert _estados(conn) == {"control": "listo"}


# ------------------------------------------------------ `retenidos` honesto

@pytest.mark.parametrize("cuando_del_vencido", [
    AHORA - timedelta(minutes=10),     # antes del aviso retenido en la cola
    AHORA - timedelta(minutes=1),      # después
])
def test_lo_vencido_de_alguien_retenido_se_descarta_igual_y_no_se_cuenta(
        cuando_del_vencido, corework, conn):
    ws = corework.workspace_id
    quien, tg, _pid = _preparar(conn, ws, _abrir_vista_previa)   # "aviso", retenido
    with espacio(conn, ws) as cur:
        _encolar(cur, ws, quien, tg, clave="vencido", cuando=cuando_del_vencido,
                 expires_at=AHORA - timedelta(minutes=2))
    conn.commit()

    resumen, transporte = _despachar(conn, ws)

    assert transporte.enviados == []
    assert _estados(conn) == {"aviso": "listo", "vencido": "descartado"}
    assert resumen["descartados"] == 1 and resumen["retenidos"] == 1


def test_lo_que_otro_despachador_tiene_bloqueado_no_se_cuenta_como_retenido(
        corework, conn, uri):
    ws = corework.workspace_id
    quien, tg, _pid = _preparar(conn, ws, _abrir_vista_previa)   # "aviso", retenido
    with espacio(conn, ws) as cur:
        for clave, minutos in (("b1", 4), ("b2", 3)):
            _encolar(cur, ws, quien, tg, clave=clave,
                     cuando=AHORA - timedelta(minutes=minutos))
    conn.commit()

    otro = conectar(uri)
    try:
        with espacio(otro, ws) as cur:          # otro despachador, a mitad de b2
            cur.execute("select id from message_outbox where dedupe_key = %s "
                        "for update", ("retencion:b2",))
            resumen, _ = _despachar(conn, ws)
    finally:
        otro.close()
    assert resumen["retenidos"] == 2            # el aviso y b1; b2 no es de este pasaje

    resumen, _ = _despachar(conn, ws)           # liberado: ahora sí
    assert resumen["retenidos"] == 3


def test_una_vista_previa_que_ya_no_es_la_vigente_se_descarta_y_no_se_cuenta(
        conn, intake_world):
    """Un aprobador con su propia rama abierta recibe la vista previa del borrador
    de otra persona; el borrador se cancela mientras espera. Ya no es la vista
    previa vigente: se descarta como siempre, no queda contada como retenida."""
    world = intake_world
    ws = world["north-lab"]["id"]
    rid, pid = _alta_enviada(conn, world)
    with espacio(conn, ws) as cur:
        morgan, tg = _persona_del_alta(cur, world, "Morgan Hale")
        _activa(cur, morgan, tg, DESPUES - timedelta(minutes=1))
        P.registrar(cur, morgan, herramienta="registrar_bloqueo", args={},
                    resumen="¿Confirmás?", vence_en=DESPUES + timedelta(hours=8),
                    chat_id=tg)                        # su rama abierta
        _control(cur, ws, morgan, tg)
    conn.commit()

    resumen, transporte = _despachar_alta(conn, ws)
    assert [e for e in transporte.enviados if e.chat_id == tg] == []
    assert resumen["retenidos"] == 2                       # control y vista previa

    with admin(conn) as cur:                           # el borrador se cancela
        cur.execute("update pending_action set estado = 'cancelada' where id = %s",
                    (pid,))
    resumen, transporte = _despachar_alta(conn, ws)

    # A quien pidió el borrador sí le sale su respuesta (T9-R3): el aviso de
    # quién lo confirma. Lo que no sale es lo dirigido a Morgan.
    assert [e for e in transporte.enviados if e.chat_id == tg] == []
    assert resumen["descartados"] == 1 and resumen["retenidos"] == 1
    with admin(conn) as cur:
        cur.execute("select estado from message_outbox where pending_action_id = %s",
                    (pid,))
        assert cur.fetchone()["estado"] == "descartado"


def test_el_reloj_de_la_pasada_decide_la_vigencia_de_la_vista_previa_y_su_conteo(
        conn, intake_world):
    """Un solo reloj, el `ahora` del despachador, para el vencimiento del mensaje y
    para la vigencia de la vista previa. Con un reloj inyectado distinto del de la
    pared (la vista previa vence 8 horas después de `NOW`, en 2028), a esa hora la
    vista previa ya no es la vigente: se descarta y no cuenta como retenida."""
    world = intake_world
    ws = world["north-lab"]["id"]
    rid, pid = _alta_enviada(conn, world)
    ahora = NOW + timedelta(hours=9)
    with espacio(conn, ws) as cur:
        morgan, tg = _persona_del_alta(cur, world, "Morgan Hale")
        _activa(cur, morgan, tg, ahora - timedelta(minutes=1))
        P.registrar(cur, morgan, herramienta="registrar_bloqueo", args={},
                    resumen="¿Confirmás?", vence_en=ahora + timedelta(hours=8),
                    chat_id=tg)                        # su rama abierta
        _control(cur, ws, morgan, tg, ahora)
    conn.commit()

    resumen, transporte = _despachar_alta(conn, ws, ahora)

    assert [e for e in transporte.enviados if e.chat_id == tg] == []
    # Se descartan la vista previa vencida y el resumen de quien pidió el borrador,
    # que ya no está esperando desde que lo envió (T9-R1c-4) y nadie despachó a
    # tiempo; sólo queda retenido el control.
    assert resumen["descartados"] == 2 and resumen["retenidos"] == 1
    with admin(conn) as cur:
        cur.execute("select estado from message_outbox where pending_action_id = %s",
                    (pid,))
        assert cur.fetchone()["estado"] == "descartado"
    assert _estados(conn) == {"control": "listo"}
