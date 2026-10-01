"""Al comprometerse una tarea cuyo responsable es otra persona, el responsable se
entera (hallazgo de la prueba real del 2026-10-01: Ismael creó una tarea para Ariel y
Marcos una para Nahuel; ni Ariel ni Nahuel recibieron nada).

Es un aviso de coordinación (mecánica §10: fuera del tope diario), una sola vez por
solicitud, auditado, de código y sin modelo, por el mismo camino que el aviso de
aprobación. Va al chat privado del responsable sólo si lo activó (constitución §7).
No se manda si el responsable es quien confirma o quien pidió (a quien pidió ya le
llega el aviso de aprobación). Cubre el alta guiada y la conversacional, y los dos
caminos de confirmación: Confirmar de quien pidió y Confirmar del aprobador tras
"Enviar a aprobación".

Todo por el webhook real.
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from prisma import gateway
from prisma.db import admin

from tests.test_alta_conducida import (Chat, _en, _modelo,  # noqa: F401
                                       conversada, salida)
from tests.test_alta_eleccion_confirmacion import (_alta_en_confirmacion,
                                                   _alta_enviada, _nuevas,
                                                   _salidas, _usuario)
from tests.test_alta_enviar_a_aprobacion import _tg_aprobador, _token, _tocar
from tests.test_alta_modificar import _tareas
from tests.test_aviso_de_aprobacion import _avisos, _cliente
from tests.test_rechazar_borrador import _nombre
from tests.test_task_intake import NOW


def _chat(world, persona) -> int:
    return world["north-lab"]["people"][persona]["telegram"]


def _asignaciones(conn, chat_id) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select id, cuerpo, es_respuesta, es_coordinacion "
                    "from message_outbox where chat_id = %s "
                    "and cuerpo like %s", (chat_id, "%te asignó%"))
        return cur.fetchall()


def _texto_esperado(conn, quien_pidio: int, rid: str) -> str:
    """El aviso tal como lo dice el código, con los datos de la tarea creada."""
    with admin(conn) as cur:
        cur.execute(
            """select t.titulo, t.criterio_aceptacion,
                      (t.fecha_objetivo at time zone w.zona_horaria)::date fecha
                 from task t join task_draft d on d.converted_task_id = t.id
                 join task_intake_request r on r.task_draft_id = d.id
                 join workspace w on w.id = t.workspace_id
                where r.id = %s""", (rid,))
        t = cur.fetchone()
    assert t["criterio_aceptacion"] and t["fecha"]
    return (f"{_nombre(conn, quien_pidio)} te asignó la tarea «{t['titulo']}», "
            f"para el {t['fecha'].strftime('%d/%m/%Y')}. "
            f"Se da por hecha cuando: {t['criterio_aceptacion']}.")


# ------------------------------------------------ Confirmar directo de quien pidió

def test_al_confirmar_quien_pidio_el_responsable_recibe_el_aviso_de_asignacion(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    client = _cliente(conn, monkeypatch, authority_conn)
    pide = _usuario(intake_world)
    responsable = _chat(intake_world, "Sam North")
    antes = _salidas(conn, responsable)

    _tocar(client, conn, pide, pid, "Confirmar")

    assert _tareas(conn) == 1
    (aviso,) = _nuevas(conn, responsable, antes)
    assert aviso["cuerpo"] == _texto_esperado(conn, pide, rid)
    assert aviso["cuerpo"].startswith(f"{_nombre(conn, pide)} te asignó la tarea «")
    (fila,) = _asignaciones(conn, responsable)
    assert fila["es_respuesta"] is False and fila["es_coordinacion"] is True
    assert _avisos(conn, pide) == []        # a quien pidió no le llega un aviso de más


def test_el_toque_repetido_de_confirmar_no_avisa_dos_veces_al_responsable(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    client = _cliente(conn, monkeypatch, authority_conn)
    pide = _usuario(intake_world)
    responsable = _chat(intake_world, "Sam North")
    _tocar(client, conn, pide, pid, "Confirmar")
    despues = _salidas(conn, responsable)

    _tocar(client, conn, pide, pid, "Confirmar")

    assert _salidas(conn, responsable) == despues
    assert len(_asignaciones(conn, responsable)) == 1


def test_el_aviso_de_asignacion_queda_en_la_auditoria(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    client = _cliente(conn, monkeypatch, authority_conn)
    _tocar(client, conn, _usuario(intake_world), pid, "Confirmar")
    _tocar(client, conn, _usuario(intake_world), pid, "Confirmar")

    with admin(conn) as cur:
        cur.execute("select detalle from audit_log "
                    "where accion = 'avisar_asignacion_ingreso_tarea'")
        filas = cur.fetchall()
    assert len(filas) == 1 and filas[0]["detalle"]["request_id"] == rid


def test_el_aviso_de_asignacion_sale_por_el_despachador_fuera_del_tope(
        intake_world, conn, monkeypatch, authority_conn):
    from datetime import timedelta

    from prisma.calendario import Calendario
    from prisma.db import espacio
    from prisma.despachador import TransporteDePrueba, despachar
    from tests.test_task_intake import NOW

    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    client = _cliente(conn, monkeypatch, authority_conn)
    _tocar(client, conn, _usuario(intake_world), pid, "Confirmar")
    ws = intake_world["north-lab"]["id"]
    transporte = TransporteDePrueba()

    with espacio(conn, ws) as cur:
        despachar(cur, ws, transporte, Calendario.desde_base(cur, ws),
                  ahora=NOW + timedelta(minutes=1))

    al_responsable = [e.texto for e in transporte.enviados
                      if e.chat_id == _chat(intake_world, "Sam North")]
    assert any("te asignó la tarea" in t for t in al_responsable)


# ------------------------------------------- Enviar a aprobación y confirma el aprobador

def test_confirmando_una_tercera_persona_el_responsable_recibe_la_asignacion_y_quien_pidio_no(
        intake_world, conn, monkeypatch, authority_conn):
    """Un responsable distinto de quien pide Y de quien confirma no sale hoy de la
    interfaz: el selector sólo ofrece a quien pide y a sus reportes, y la autoridad
    exige que confirme el aprobador del responsable (que para esos reportes es quien
    pide). La regla igual se prueba a nivel de la función, con Morgan como tercera
    persona que convierte el borrador de Taylor para Sam North; el aviso de
    aprobación a quien pidió es el de siempre y no lo cubre esta función."""
    from prisma import ingreso_tareas as I
    from prisma.autoridad import Canal, identificar
    from prisma.db import autoridad, espacio
    from prisma.pendientes import resolver_borrador

    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    ws = intake_world["north-lab"]["id"]
    pide = _usuario(intake_world)
    with autoridad(authority_conn) as acur:      # Taylor confirma por la autoridad...
        resuelta = resolver_borrador(acur, ws, _token(conn, pid, "Confirmar"),
                                     pide, pide)
    assert resuelta.task_id and not resuelta.replay
    morgan = _tg_aprobador(intake_world)
    with espacio(conn, ws) as cur:               # ...y la función la corre un tercero
        tercero = identificar(cur, morgan, Canal.ESPACIO, ws)
        assert I.notify_responsible_of_assignment(
            cur, tercero, pending_action_id=resuelta.pending_action_id,
            now=NOW) is True
        assert I.notify_responsible_of_assignment(      # una sola vez
            cur, tercero, pending_action_id=resuelta.pending_action_id,
            now=NOW) is False
    (aviso,) = _asignaciones(conn, _chat(intake_world, "Sam North"))
    assert aviso["cuerpo"] == _texto_esperado(conn, pide, rid)
    assert _asignaciones(conn, pide) == [] and _asignaciones(conn, morgan) == []


def test_si_el_responsable_es_quien_pidio_sale_sólo_el_aviso_de_aprobacion(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_enviada(conn, intake_world, responsable="Para mí")
    client = _cliente(conn, monkeypatch, authority_conn)
    pide = _usuario(intake_world)

    _tocar(client, conn, _tg_aprobador(intake_world), pid, "Confirmar")

    assert len(_avisos(conn, pide)) == 1
    assert _asignaciones(conn, pide) == []
    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox "
                    "where cuerpo like '%te asignó%'")
        assert cur.fetchone()["n"] == 0
        cur.execute("select count(*) n from audit_log "
                    "where accion like '%asignacion_ingreso_tarea'")
        assert cur.fetchone()["n"] == 0


def _con_autoridad_final(conn, world, persona):
    """`persona` pasa a ser la única autoridad final del espacio, sin aprobador:
    confirma lo suyo ella misma (Morgan queda inactiva)."""
    ws = world["north-lab"]["people"]
    with admin(conn) as cur:
        cur.execute(
            """update membership set aprobador_membership_id = null,
                      rol_id = (select rol_id from membership where id = %s)
                where id = %s""",
            (ws["Morgan Hale"]["membership_id"], ws[persona]["membership_id"]))
        cur.execute("update membership set activo = false where id = %s",
                    (ws["Morgan Hale"]["membership_id"],))
    conn.commit()


def test_la_autoasignacion_de_quien_se_confirma_a_si_mismo_no_manda_nada(
        intake_world, conn, monkeypatch, authority_conn):
    """Quien pide es responsable y confirma lo suyo (es quien lo pidió, lo asignó y lo
    confirmó): nada que avisar, ni aprobación ni asignación."""
    _con_autoridad_final(conn, intake_world, "Taylor Quinn")
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Para mí")
    client = _cliente(conn, monkeypatch, authority_conn)

    _tocar(client, conn, _usuario(intake_world), pid, "Confirmar")

    assert _tareas(conn) == 1
    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox "
                    "where cuerpo like '%te asignó%' or cuerpo like '%confirmó%'")
        assert cur.fetchone()["n"] == 0
        cur.execute("select count(*) n from audit_log "
                    "where accion like '%asignacion_ingreso_tarea'")
        assert cur.fetchone()["n"] == 0


# ---------------------------------------------------------- sin chat privado

def test_un_responsable_sin_chat_activado_no_recibe_nada_y_queda_registrado(
        intake_world, conn, monkeypatch, authority_conn):
    """Igual que los demás avisos (`herramientas._avisar`): no se encola nada para un
    chat que no existe; además queda en la auditoría, así no se pierde en silencio."""
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    with admin(conn) as cur:
        cur.execute("update app_user set telegram_user_id = null where id = %s",
                    (intake_world["north-lab"]["people"]["Sam North"]
                     ["app_user_id"],))
    conn.commit()
    client = _cliente(conn, monkeypatch, authority_conn)

    _tocar(client, conn, _usuario(intake_world), pid, "Confirmar")

    assert _tareas(conn) == 1
    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox "
                    "where cuerpo like '%te asignó%'")
        assert cur.fetchone()["n"] == 0
        cur.execute("select detalle from audit_log "
                    "where accion = 'omitir_aviso_asignacion_ingreso_tarea'")
        (fila,) = cur.fetchall()
    assert fila["detalle"]["request_id"] == rid
    assert fila["detalle"]["motivo"] == "sin_chat"


# ---------------------------------------------------------- el alta conversacional

def test_en_el_alta_conversacional_el_responsable_tambien_recibe_el_aviso(
        conversada, conn, monkeypatch, authority_conn):
    c = Chat(conn, monkeypatch, conversada, _modelo(salida(
        "Anotado. ¿Quién la hace?",
        valores={"title": {"texto": "Calibrar los sensores"},
                 "due_date": {"fecha_iso": _en(3)},
                 "objective": {"opcion_id": "O3"}},
        pregunta=["responsible"])))
    c.escribir("necesito crear una tarea: calibrar los sensores")
    c.modelo.conducciones.append(salida(
        "Dale. ¿Cómo se sabe que está terminada?",
        valores={"responsible": {"opcion_id": c.id_de("responsible", "Sam North")}},
        pregunta=["acceptance_criterion"]))
    c.escribir("la hace Sam North")
    c.modelo.conducciones.append(salida(
        "Listo, revisalo.", valores={"acceptance_criterion": {
            "texto": "Informe firmado por calidad", "verificable": "si"}}))
    c.escribir("el informe firmado por calidad")
    rid = c.rid
    with admin(conn) as cur:
        cur.execute(
            """select o.pending_action_id pid from message_outbox o
                where o.pending_action_id is not null and o.chat_id = %s
                order by o.programado_para desc limit 1""", (c.usuario,))
        pid = str(cur.fetchone()["pid"])
    client = _cliente(conn, monkeypatch, authority_conn)
    responsable = _chat(conversada, "Sam North")

    _tocar(client, conn, c.usuario, pid, "Confirmar")

    assert _tareas(conn) == 1
    (aviso,) = _asignaciones(conn, responsable)
    assert aviso["cuerpo"] == _texto_esperado(conn, c.usuario, rid)



# ------------------------------------------------------------ el texto, sin fecha

def test_el_aviso_sin_fecha_no_la_nombra_y_no_duplica_el_punto():
    from datetime import date

    from prisma import ingreso_tareas as I

    con = I.assignment_notice_text("Morgan", "Medir", date(2026, 10, 15), "Anda.")
    assert con == ("Morgan te asignó la tarea «Medir», para el 15/10/2026. "
                   "Se da por hecha cuando: Anda.")
    sin = I.assignment_notice_text("Morgan", "Medir", None, "Anda")
    assert sin == "Morgan te asignó la tarea «Medir». Se da por hecha cuando: Anda."


# ------------------------------- un aviso que falla no se lleva la respuesta

def test_si_un_aviso_falla_quien_confirma_igual_recibe_su_respuesta_y_queda_un_incidente(
        intake_world, conn, monkeypatch, authority_conn):
    from prisma import ingreso_tareas as I

    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    client = _cliente(conn, monkeypatch, authority_conn)
    pide = _usuario(intake_world)
    antes = _salidas(conn, pide)

    def _rompe(*_a, **_k):
        raise RuntimeError("falla de prueba")
    monkeypatch.setattr(I, "notify_responsible_of_assignment", _rompe)

    _tocar(client, conn, pide, pid, "Confirmar")

    assert _tareas(conn) == 1
    assert any("comprometida" in s["cuerpo"] for s in _nuevas(conn, pide, antes))
    with admin(conn) as cur:
        cur.execute("select resumen_sanitizado, referencia_tipo, referencia_id "
                    "from incident where etapa = 'aviso_coordinacion'")
        (inc,) = cur.fetchall()
    # Dice cuál aviso falló y de qué pedido, para poder avisar a mano.
    assert "al responsable" in inc["resumen_sanitizado"]
    assert inc["referencia_tipo"] == "pending_action"
    assert str(inc["referencia_id"]) == str(pid)


# ------------------------------- (h) quien confirma sabe si, y cuándo, se enteran

HECHO = "Hecho. La tarea quedó comprometida."
# El calendario del espacio de prueba: lunes a viernes de 08:00 a 18:00, Buenos Aires
# (UTC-3).
LUNES_A_LAS_12 = datetime(2028, 2, 28, 15, 0, tzinfo=timezone.utc)
LUNES_A_LAS_1830 = datetime(2028, 2, 28, 21, 30, tzinfo=timezone.utc)
VIERNES_A_LAS_1830 = datetime(2028, 3, 3, 21, 30, tzinfo=timezone.utc)


def _reloj(monkeypatch, momento) -> None:
    """El `datetime.now` que ve el gateway, fijo en `momento`."""
    real = gateway.datetime

    class _Fijo(real):
        @classmethod
        def now(cls, tz=None):
            return momento.astimezone(tz) if tz else momento

    monkeypatch.setattr(gateway, "datetime", _Fijo)


def _respuesta_a(conn, chat_id, antes) -> str:
    """El único mensaje visible que recibió quien confirmó, con su texto."""
    (fila,) = _nuevas(conn, chat_id, antes)
    return fila["cuerpo"]


@pytest.mark.parametrize("momento, cuando", [
    (LUNES_A_LAS_1830, "mañana a las 08:00"),
    (VIERNES_A_LAS_1830, "el lunes a las 08:00"),
])
def test_fuera_de_horario_quien_confirma_sabe_cuando_lo_va_a_ver_el_responsable(
        momento, cuando, intake_world, conn, monkeypatch, authority_conn):
    """Caso real: Ismael confirmó a las 18:00 y el aviso a Ariel quedó para el
    02/10 a las 09:00; Ismael no lo sabía. Una sola respuesta, con la hora real."""
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    client = _cliente(conn, monkeypatch, authority_conn)
    _reloj(monkeypatch, momento)
    pide = _usuario(intake_world)
    responsable = _chat(intake_world, "Sam North")
    antes = _salidas(conn, pide)

    _tocar(client, conn, pide, pid, "Confirmar")

    assert _respuesta_a(conn, pide, antes) == (
        f"{HECHO}\n{_nombre(conn, responsable)} lo va a ver {cuando}, "
        "cuando empiece el horario.")
    with admin(conn) as cur:     # la hora dicha es la de la fila encolada
        cur.execute("select programado_para from message_outbox "
                    "where chat_id = %s and cuerpo like '%%te asignó%%'",
                    (responsable,))
        (fila,) = cur.fetchall()
    assert fila["programado_para"].astimezone(ZoneInfo(
        "America/Argentina/Buenos_Aires")).strftime("%H:%M") == "08:00"


def test_sin_chat_activado_quien_confirma_sabe_que_no_se_le_pudo_avisar(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    app_user = intake_world["north-lab"]["people"]["Sam North"]["app_user_id"]
    with admin(conn) as cur:
        cur.execute("select nombre from app_user where id = %s", (app_user,))
        nombre = cur.fetchone()["nombre"]
        cur.execute("update app_user set telegram_user_id = null where id = %s",
                    (app_user,))
    conn.commit()
    client = _cliente(conn, monkeypatch, authority_conn)
    _reloj(monkeypatch, LUNES_A_LAS_12)
    pide = _usuario(intake_world)
    antes = _salidas(conn, pide)

    _tocar(client, conn, pide, pid, "Confirmar")

    assert _respuesta_a(conn, pide, antes) == (
        f"{HECHO}\n{nombre} todavía no activó su chat con Prisma, así que no le "
        "pude avisar.")


def test_dentro_de_horario_y_con_chat_la_respuesta_no_agrega_nada(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    client = _cliente(conn, monkeypatch, authority_conn)
    _reloj(monkeypatch, LUNES_A_LAS_12)
    pide = _usuario(intake_world)
    antes = _salidas(conn, pide)

    _tocar(client, conn, pide, pid, "Confirmar")

    assert _respuesta_a(conn, pide, antes) == HECHO


def test_fuera_de_horario_quien_confirma_sabe_cuando_se_entera_quien_pidio(
        intake_world, conn, monkeypatch, authority_conn):
    """El aviso de aprobación es igual de simple: mismo estado, misma respuesta."""
    rid, pid = _alta_enviada(conn, intake_world, responsable="Para mí")
    client = _cliente(conn, monkeypatch, authority_conn)
    _reloj(monkeypatch, LUNES_A_LAS_1830)
    aprobador = _tg_aprobador(intake_world)
    pide = _usuario(intake_world)
    antes = _salidas(conn, aprobador)

    _tocar(client, conn, aprobador, pid, "Confirmar")

    assert _respuesta_a(conn, aprobador, antes) == (
        f"{HECHO}\n{_nombre(conn, pide)} lo va a ver mañana a las 08:00, "
        "cuando empiece el horario.")


def test_si_el_aviso_falla_la_respuesta_no_agrega_nada_y_queda_el_incidente(
        intake_world, conn, monkeypatch, authority_conn):
    """El aislamiento sigue: un aviso que no se pudo encolar no deja una línea de
    estado inventada; su incidente ya lo cubre."""
    from prisma import ingreso_tareas as I

    def _rompe(*args, **kwargs):
        raise RuntimeError("falla del aviso")

    monkeypatch.setattr(I, "notify_responsible_of_assignment", _rompe)
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    client = _cliente(conn, monkeypatch, authority_conn)
    _reloj(monkeypatch, LUNES_A_LAS_1830)
    pide = _usuario(intake_world)
    antes = _salidas(conn, pide)

    _tocar(client, conn, pide, pid, "Confirmar")

    assert _respuesta_a(conn, pide, antes) == HECHO
