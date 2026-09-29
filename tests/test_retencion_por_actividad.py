"""La retención acotada por la actividad de la persona y por una pasada acotada
(T9-R1d-2b, ADR 0013 regla 1, "Precisión (2026-09-29, decisión del usuario)").

Lo que inicia Prisma se retiene sólo mientras la persona está ACTIVA en la rama:
escribió o tocó algo en ese chat en los últimos `VENTANA_DE_ACTIVIDAD` (30
minutos). Una rama abierta pero abandonada no retiene nada, ni siquiera un aviso
urgente: sale en el momento y la rama sigue abierta. Con esa ventana también
retienen las preguntas del alta guiada, que no vencen.

Además, la pasada de `despachar` examina a lo sumo `lote` filas, retenidas o no,
y lo retenido no deja sin servicio a lo que viene detrás.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from prisma import pendientes as P
from prisma.db import admin, espacio
from prisma.despachador import (VENTANA_DE_ACTIVIDAD, _rama_que_retiene,
                                despachar)

from tests.test_alta_eleccion_confirmacion import (_alta_con_eleccion,
                                                   _alta_en_confirmacion,
                                                   _usuario)
from tests.test_alta_pregunta_pendiente import _abrir_alta
from tests.test_menu_tarea import _quien, _tocar, cliente  # noqa: F401
from tests.test_retencion_por_rama import (AHORA, AVISO, OTRA, PERSONA,
                                           _abrir_dato, _abrir_eleccion,
                                           _abrir_vista_previa, _despachar,
                                           _encolar, _estados, _preparar,
                                           _telegram_id)


def _escribio(cur, quien, tg: int, cuando: datetime) -> None:
    """La persona escribió algo en ese chat a las `cuando`."""
    cur.execute(
        """insert into inbound_message
             (workspace_id, chat_id, app_user_id, texto, at)
           values (%s, %s, %s, 'hola', %s)""",
        (quien.workspace_id, tg, quien.app_user_id, cuando))


def _sin_actividad(conn, ws, *, desde: datetime) -> None:
    """Deja como única actividad de PERSONA una a las `desde` (los helpers de
    `test_retencion_por_rama` la dejan en `AHORA`)."""
    with admin(conn) as cur:
        cur.execute("delete from inbound_message where workspace_id = %s", (ws,))
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        _escribio(cur, quien, _telegram_id(cur, PERSONA), desde)
    conn.commit()


def test_la_ventana_de_actividad_es_de_30_minutos():
    assert VENTANA_DE_ACTIVIDAD == timedelta(minutes=30)


# ---------------------------------------------------------------------------
# Se retiene mientras está activa; se libera al pasar la ventana
# ---------------------------------------------------------------------------

def test_retiene_mientras_la_persona_esta_activa_en_la_rama(corework, conn):
    ws = corework.workspace_id
    _preparar(conn, ws, _abrir_vista_previa)      # escribió a las AHORA

    dentro = AHORA + VENTANA_DE_ACTIVIDAD - timedelta(minutes=1)
    resumen, transporte = _despachar(conn, ws, dentro)

    assert transporte.enviados == [] and resumen["retenidos"] == 1


def test_una_rama_abandonada_libera_lo_retenido_y_sigue_abierta(corework, conn):
    ws = corework.workspace_id
    quien, tg, _pid = _preparar(conn, ws, _abrir_eleccion,
                                vence=AHORA + timedelta(hours=8))

    tarde = AHORA + VENTANA_DE_ACTIVIDAD + timedelta(minutes=1)
    resumen, transporte = _despachar(conn, ws, tarde)

    assert len(transporte.enviados) == 1 and resumen["retenidos"] == 0
    with espacio(conn, ws) as cur:      # la rama sigue abierta para cuando vuelva
        assert P.ver_rama_abierta(cur, quien, tg, tarde, ()) is not None


def test_volver_a_escribir_reabre_la_ventana(corework, conn):
    ws = corework.workspace_id
    quien, tg, _pid = _preparar(conn, ws, _abrir_vista_previa)
    with espacio(conn, ws) as cur:
        _escribio(cur, quien, tg, AHORA + timedelta(minutes=40))
    conn.commit()

    resumen, transporte = _despachar(conn, ws, AHORA + timedelta(minutes=50))

    assert transporte.enviados == [] and resumen["retenidos"] == 1


def test_lo_que_escribieron_otra_persona_u_otro_chat_no_cuenta(corework, conn):
    ws = corework.workspace_id
    quien, tg, _pid = _preparar(conn, ws, _abrir_dato)
    _sin_actividad(conn, ws, desde=AHORA - timedelta(hours=2))
    with espacio(conn, ws) as cur:
        otra = _quien(cur, OTRA, ws)
        _escribio(cur, otra, tg, AHORA)                   # otra persona, mismo chat
        _escribio(cur, quien, -1001, AHORA)               # ella, en otro chat
    conn.commit()

    resumen, transporte = _despachar(conn, ws)

    assert len(transporte.enviados) == 1 and resumen["retenidos"] == 0


def test_sin_ninguna_actividad_registrada_no_retiene(corework, conn):
    ws = corework.workspace_id
    _preparar(conn, ws, _abrir_vista_previa)
    with admin(conn) as cur:
        cur.execute("delete from inbound_message where workspace_id = %s", (ws,))
    conn.commit()

    resumen, transporte = _despachar(conn, ws)

    assert len(transporte.enviados) == 1 and resumen["retenidos"] == 0


def test_cerrar_la_rama_libera_aunque_siga_activa(corework, conn):
    ws = corework.workspace_id
    quien, _tg, pid = _preparar(conn, ws, _abrir_vista_previa)
    assert _despachar(conn, ws)[0]["retenidos"] == 1

    with espacio(conn, ws) as cur:
        assert P.cancelar_vista_previa(cur, quien, pid, AHORA)
    conn.commit()
    _resumen, transporte = _despachar(conn, ws, AHORA + timedelta(seconds=30))

    assert len(transporte.enviados) == 1


# ---------------------------------------------------------------------------
# Un urgente: retenido si está activa, en el momento si no
# ---------------------------------------------------------------------------

def test_un_urgente_a_una_persona_inactiva_sale_en_el_momento(corework, conn):
    ws = corework.workspace_id
    quien, tg, _pid = _preparar(conn, ws, _abrir_vista_previa)
    _sin_actividad(conn, ws, desde=AHORA - timedelta(hours=3))
    with espacio(conn, ws) as cur:
        _encolar(cur, ws, quien, tg, clave="urgente", message_type="urgente")
    conn.commit()

    resumen, transporte = _despachar(conn, ws)

    assert _estados(conn) == {"aviso": "enviado", "urgente": "enviado"}
    assert resumen["retenidos"] == 0 and len(transporte.enviados) == 2


def test_un_urgente_a_una_persona_activa_se_retiene(corework, conn):
    ws = corework.workspace_id
    quien, tg, _pid = _preparar(conn, ws, _abrir_vista_previa)
    with espacio(conn, ws) as cur:
        _encolar(cur, ws, quien, tg, clave="urgente", message_type="urgente")
    conn.commit()

    resumen, transporte = _despachar(conn, ws)

    assert transporte.enviados == [] and resumen["retenidos"] == 2


# ---------------------------------------------------------------------------
# Un toque también es actividad
# ---------------------------------------------------------------------------

def test_un_toque_cuenta_como_actividad_en_ese_chat(corework, conn, cliente):
    ws = corework.workspace_id
    quien, tg, _pid = _preparar(
        conn, ws, _abrir_vista_previa,
        vence=datetime.now(timezone.utc) + timedelta(hours=8))
    _sin_actividad(conn, ws, desde=AHORA - timedelta(hours=3))
    assert _despachar(conn, ws)[0]["retenidos"] == 0    # inactiva: no retiene

    with espacio(conn, ws) as cur:
        _encolar(cur, ws, quien, tg, clave="despues",
                 cuando=datetime.now(timezone.utc) - timedelta(minutes=1))
    conn.commit()
    _tocar(cliente, "ya-no-vigente", tg)      # un botón viejo también es un toque

    resumen, _transporte = _despachar(conn, ws, datetime.now(timezone.utc))

    assert resumen["retenidos"] == 1
    assert _estados(conn)["despues"] == "listo"


# ---------------------------------------------------------------------------
# Las preguntas del alta también retienen (sin vencimiento, acotadas por la ventana)
# ---------------------------------------------------------------------------

def _aviso_para(conn, ws, membership_id: str, tg: int, clave="alta"):
    with espacio(conn, ws) as cur:
        from prisma.salida import enqueue_outbox
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=tg, text=f"{AVISO} {clave}",
            recipient_membership_id=membership_id,
            scheduled_for=datetime.now(timezone.utc) - timedelta(minutes=1),
            dedupe_key=f"retencion:{clave}", message_type="urgente")
    conn.commit()


def _retencion_del_alta(conn, ws, membership_id, tg):
    """Con la pregunta del alta abierta y actividad reciente retiene; pasada la
    ventana, sale."""
    _aviso_para(conn, ws, membership_id, tg)
    ahora = datetime.now(timezone.utc)
    resumen, transporte = _despachar(conn, ws, ahora)
    assert resumen["retenidos"] == 1
    assert _estados(conn) == {"alta": "listo"}

    resumen, transporte = _despachar(
        conn, ws, ahora + VENTANA_DE_ACTIVIDAD + timedelta(minutes=1))
    assert resumen["retenidos"] == 0
    assert _estados(conn) == {"alta": "enviado"}


def test_la_pregunta_de_texto_libre_del_alta_retiene(corework, conn):
    ws = corework.workspace_id
    tg, _rid = _abrir_alta(conn, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
    _retencion_del_alta(conn, ws, quien.membership_id, tg)


def test_la_eleccion_del_alta_retiene(conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    _alta_con_eleccion(conn, intake_world)
    from tests.test_task_intake import _actor
    with espacio(conn, ws) as cur:
        actor = _actor(cur, intake_world)
    _retencion_del_alta(conn, ws, actor.membership_id, _usuario(intake_world))


def test_el_borrador_propio_esperando_confirmacion_retiene(conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    _alta_en_confirmacion(conn, intake_world)
    from tests.test_task_intake import _actor
    with espacio(conn, ws) as cur:
        actor = _actor(cur, intake_world)
    _retencion_del_alta(conn, ws, actor.membership_id, _usuario(intake_world))


# ---------------------------------------------------------------------------
# Una pasada acotada: retenido o no, examina a lo sumo `lote` filas
# ---------------------------------------------------------------------------

def test_la_pasada_examina_a_lo_sumo_un_lote_y_lo_retenido_no_deja_sin_servicio(
        corework, conn):
    """40 retenidas de PERSONA repartidas entre 30 de OTRA: con `lote=6` cada
    pasada examina 6 filas como máximo; la primera retenida de PERSONA cuesta una
    fila y el resto de lo suyo ya no se pide. Lo de OTRA sale entero, en su orden,
    a lo largo de las pasadas."""
    ws = corework.workspace_id
    quien, tg, _pid = _preparar(conn, ws, _abrir_vista_previa)
    with admin(conn) as cur:          # sin el tope diario: sólo se prueba el lote
        cur.execute("delete from workspace_setting where workspace_id = %s "
                    "and clave = 'limites_de_contacto'", (ws,))
    with espacio(conn, ws) as cur:
        otra = _quien(cur, OTRA, ws)
        tg_otra = _telegram_id(cur, OTRA)
        for i in range(40):
            _encolar(cur, ws, quien, tg, clave=f"ret{i:02d}",
                     cuando=AHORA - timedelta(minutes=200 - 3 * i))
        for i in range(30):
            _encolar(cur, ws, otra, tg_otra, clave=f"otra{i:02d}",
                     cuando=AHORA - timedelta(minutes=199 - 4 * i))
    conn.commit()

    enviados: list[str] = []
    for _ in range(3):
        resumen, transporte = _despachar(conn, ws, lote=6)
        assert (resumen["enviados"] + resumen["descartados"]
                + resumen["pospuestos"] + resumen["fallidos"]) <= 6
        enviados += [e.texto for e in transporte.enviados]

    # Cinco por pasada (una fila del lote la gasta encontrar lo retenido), en orden.
    assert enviados == [f"{AVISO} otra{i:02d}" for i in range(15)]
    assert resumen["retenidos"] == 41           # las 40 y el aviso, contadas todas


def test_lo_retenido_se_examina_una_vez_por_pasada_no_una_por_fila(corework, conn):
    ws = corework.workspace_id
    quien, tg, _pid = _preparar(conn, ws, _abrir_vista_previa)
    with espacio(conn, ws) as cur:
        for i in range(20):
            _encolar(cur, ws, quien, tg, clave=f"ret{i:02d}",
                     cuando=AHORA - timedelta(minutes=100 - i))
    conn.commit()

    resumen, transporte = _despachar(conn, ws, lote=4)

    assert transporte.enviados == [] and resumen["retenidos"] == 21


# ---------------------------------------------------------------------------
# Explícito: una respuesta nunca se retiene; sin membresía, no se retiene
# ---------------------------------------------------------------------------

def test_una_respuesta_nunca_se_retiene_ni_se_consulta_la_rama():
    """La decisión es local y explícita: con `es_respuesta` ni siquiera se abre
    la base (`cur=None` fallaría al primer uso)."""
    m = {"es_respuesta": True, "destinatario_membership_id": str(uuid.uuid4()),
         "chat_id": 1, "workspace_id": str(uuid.uuid4()),
         "pending_action_id": None, "intake_choice_set_id": None}

    assert _rama_que_retiene(None, m, AHORA, {}) is None


def test_sin_la_membresia_del_destinatario_no_se_retiene(corework, conn):
    """Si la fila de la membresía no está (no visible en el espacio, o ya no
    existe), no hay a quién atribuirle una rama: no se arma un `Solicitante`
    vacío, el mensaje no se retiene."""
    ws = corework.workspace_id
    m = {"es_respuesta": False, "destinatario_membership_id": str(uuid.uuid4()),
         "chat_id": 1, "workspace_id": ws, "pending_action_id": None,
         "intake_choice_set_id": None}

    with espacio(conn, ws) as cur:
        assert _rama_que_retiene(cur, m, AHORA, {}) is None
