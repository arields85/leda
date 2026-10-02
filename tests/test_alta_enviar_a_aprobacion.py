"""Quien pide revisa antes de enviar a aprobación (T9-R1c-4, ADR 0005 decisión 1,
precisión del 2026-09-29; ADR 0013 reglas 1, 2 y 4).

Cuando el borrador del alta lo confirma otra persona, quien lo pidió ve primero su
propio resumen con Enviar a aprobación, Modificar y Cancelar, como respuesta a su
acto. Hasta que lo envía es SU rama abierta y a quien confirma no le llega nada.
Modificar es el de T9-R1c-3 (mismo selector) pero cada cambio vuelve al resumen de
quien pide. Enviar a aprobación lo intercepta el gateway (nunca llega a la
autoridad): cierra la revisión de una vez, le manda el borrador a quien confirma
con Confirmar y Rechazar y le dice a quien pide a quién se lo mandó.

Los ruteos y el modelo se guionan; ninguna prueba toca la red ni el modelo real.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from psycopg.types.json import Jsonb

from leda import ingreso_tareas as I
from leda import pendientes as P
from leda.autoridad import Canal, identificar
from leda.db import admin, autoridad, espacio
from leda.calendario import Calendario
from leda.despachador import TransporteDePrueba, despachar
from leda.llm import RespectoPendiente
from leda.salida import etiqueta_sin_icono

from tests.test_alta_eleccion_confirmacion import (_alta_en_confirmacion,
                                                   _alta_enviada, _escribir,
                                                   _nuevas, _ruta, _salidas,
                                                   _solicitud, _tocar_boton,
                                                   _usuario)
from tests.test_alta_modificar import (AVISO_TOQUE_YA_USADO, _elegir_dato,
                                       _opciones_activas, _responder_con, _tareas,
                                       _tocar_volver)
from tests.test_task_intake import NOW, _RoutingProvider, _callback_client
from tests.toques import FUERA_DE_LA_VENTANA, envejecer_toques

APROBADOR = "Morgan Hale"          # quien aprueba lo de Taylor Quinn en el mundo de prueba
ETIQUETAS_DE_LA_REVISION = ["Enviar a aprobación", "Modificar", "Cancelar"]
ETIQUETAS_DEL_APROBADOR = ["Confirmar", "Rechazar"]


# ----------------------------------------------------------------- ayudas

def _tg_aprobador(world) -> int:
    return world["north-lab"]["people"][APROBADOR]["telegram"]


def _alta_en_revision(conn, world) -> tuple[str, str]:
    """El alta completa cuyo borrador confirma otra persona: (id de la solicitud,
    id de la revisión de quien pide)."""
    return _alta_en_confirmacion(conn, world, responsable="Para mí")


def _etiquetas(conn, pid) -> list[str]:
    with admin(conn) as cur:
        return [etiqueta_sin_icono(o.etiqueta) for o in P.opciones(cur, pid)]


def _token(conn, pid, etiqueta) -> str:
    """El token del botón, aunque la acción ya esté cerrada (un toque tardío usa el
    mismo botón de siempre)."""
    with admin(conn) as cur:
        cur.execute("select token from pending_action_option "
                    "where pending_action_id = %s and etiqueta like %s",
                    (pid, f"%{etiqueta}"))
        return cur.fetchone()["token"]


def _tocar(client, conn, user, pid, etiqueta):
    response = _tocar_boton(client, conn, _token(conn, pid, etiqueta), user)
    assert response.status_code == 200
    return response


def _acciones(conn, rid) -> list[dict]:
    """Las acciones del borrador de la solicitud, la más vieja primero, con su
    dueño y su chat."""
    with admin(conn) as cur:
        cur.execute(
            """select p.id, p.estado, p.resumen, p.membership_id, p.chat_id,
                      p.draft_version, p.preview, p.herramienta, p.args
                 from pending_action p
                 join task_intake_request r on r.task_draft_id = p.draft_id
                where r.id = %s order by p.creado_en, p.id""", (rid,))
        return cur.fetchall()


def _fila(conn, pid) -> dict:
    with admin(conn) as cur:
        cur.execute("select cuerpo, es_respuesta, pending_action_id, chat_id "
                    "from message_outbox where pending_action_id = %s", (pid,))
        return cur.fetchone()


def _pregunta_abierta(conn, world, user):
    ws = world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        quien = identificar(cur, user, Canal.ESPACIO, ws)
        return I.open_intake_question(cur, quien, user)


def _linea_de_quien_pide(conn, world) -> str:
    """La primera línea del pedido de aprobación (hallazgo (d), 2026-10-01)."""
    with admin(conn) as cur:
        cur.execute("select nombre from app_user where telegram_user_id = %s",
                    (_usuario(world),))
        return I.request_line(cur.fetchone()["nombre"])


def _nombre_del_aprobador(conn, world) -> str:
    with admin(conn) as cur:
        cur.execute("select nombre from app_user where telegram_user_id = %s",
                    (_tg_aprobador(world),))
        return cur.fetchone()["nombre"]


def _revision_tocada(conn, monkeypatch, world):
    """El alta en revisión con Modificar ya tocado: el selector abierto."""
    rid, pid = _alta_en_revision(conn, world)
    user = _usuario(world)
    client = _callback_client(conn, monkeypatch)
    _tocar(client, conn, user, pid, "Modificar")
    return rid, pid, client, user


# ------------------------------------- lo primero que ve quien pide: su resumen

def test_quien_pide_ve_primero_su_resumen_con_enviar_modificar_y_cancelar(
        intake_world, conn):
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    rid, pid = _alta_en_revision(conn, intake_world)

    assert _etiquetas(conn, pid) == ETIQUETAS_DE_LA_REVISION
    (accion,) = _acciones(conn, rid)
    assert str(accion["id"]) == str(pid) and accion["estado"] == "esperando"
    # Es de quien pidió el borrador y en su chat.
    with admin(conn) as cur:
        cur.execute("select membership_id from task_intake_request where id = %s",
                    (rid,))
        assert accion["membership_id"] == cur.fetchone()["membership_id"]
    assert accion["chat_id"] == user
    # Como respuesta a su acto (ADR 0013 regla 2), con el resumen de siempre.
    (salida,) = [f for f in _nuevas(conn, user, antes) if f["pending_action_id"]]
    fila = _fila(conn, pid)
    assert fila["es_respuesta"] is True and fila["chat_id"] == user
    assert fila["cuerpo"] == accion["resumen"]
    assert accion["resumen"].startswith("Resumen para revisar")
    assert str(salida["pending_action_id"]) == str(pid)


def test_el_pedido_de_aprobacion_dice_quien_lo_manda_y_su_resumen_no_cambia(
        intake_world, conn):
    """Hallazgo (d) del 2026-10-01: a quien confirma le llegaba el resumen sin decir
    de quién era. Ahora arranca nombrando a quien pidió; el de quien pidió, igual."""
    rid, pid = _alta_enviada(conn, intake_world)
    linea = _linea_de_quien_pide(conn, intake_world)

    (aprobador,) = [a for a in _acciones(conn, rid)
                    if a["herramienta"] == "confirmar_borrador_tarea"]
    assert linea.endswith(" te manda esta tarea para que la confirmes.")
    assert aprobador["resumen"].startswith(linea + "\n\nResumen para revisar\n")
    assert _fila(conn, pid)["cuerpo"] == aprobador["resumen"]
    (suyo,) = [a for a in _acciones(conn, rid)
               if a["herramienta"] != "confirmar_borrador_tarea"]
    assert suyo["resumen"].startswith("Resumen para revisar\n")


def test_hasta_enviarlo_a_quien_confirma_no_le_llega_nada(intake_world, conn):
    rid, pid = _alta_en_revision(conn, intake_world)

    assert _salidas(conn, _tg_aprobador(intake_world)) == []
    assert _tareas(conn) == 0 and _solicitud(conn, rid) == "active"


def test_la_revision_es_la_rama_abierta_de_quien_pide(intake_world, conn):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)

    pregunta = _pregunta_abierta(conn, intake_world, user)

    assert pregunta["tipo"] == I.QUESTION_CONFIRMATION
    assert pregunta["request_id"] == rid and str(pregunta["id"]) == str(pid)
    # El recordatorio nombra los botones que de verdad tiene, no los de quien confirma.
    assert pregunta["resumen"] == I.DRAFT_AWAITING_SEND
    assert "Enviar a aprobación" in I.DRAFT_AWAITING_SEND
    assert "Confirmar" not in I.DRAFT_AWAITING_SEND


def test_la_revision_retiene_lo_que_leda_inicia_como_cualquier_rama(
        intake_world, conn):
    from leda import herramientas as H

    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    ws = intake_world["north-lab"]["id"]

    # A la hora del armado (`NOW`), no al reloj real: la revisión vence 8 h después.
    with espacio(conn, ws) as cur:
        quien = identificar(cur, user, Canal.ESPACIO, ws)
        rama = P.ver_rama_abierta(cur, quien, user, NOW, H.REGISTRO, alta=True)

    assert rama is not None and rama.tipo == P.RAMA_ALTA


def test_la_revision_no_se_descarta_al_despachar_aunque_su_dueno_no_sea_el_aprobador(
        intake_world, conn):
    """El despachador descarta la vista previa de un borrador cuyo destinatario ya
    no es quien aprueba (`_preview_vigente`): la revisión de quien pide es de
    alguien que nunca lo es y tiene que salir."""
    rid, pid = _alta_en_revision(conn, intake_world)
    ws = intake_world["north-lab"]["id"]
    transporte = TransporteDePrueba()

    # El armado del alta usa un reloj fijo (`NOW`): se despacha a esa hora.
    with espacio(conn, ws) as cur:
        despachar(cur, ws, transporte, Calendario.desde_base(cur, ws),
                  ahora=NOW + timedelta(minutes=1))

    enviados = [e for e in transporte.enviados
                if [b.etiqueta for b in e.botones] and any(
                    "Enviar a aprobación" in b.etiqueta for b in e.botones)]
    assert len(enviados) == 1
    assert [etiqueta_sin_icono(b.etiqueta) for b in enviados[0].botones] == (
        ETIQUETAS_DE_LA_REVISION)
    assert _acciones(conn, rid)[0]["estado"] == "esperando"


# ---------------------------------------------------- Enviar a aprobación

def test_enviar_arma_el_texto_de_quien_confirma_con_el_cuerpo_guardado_no_cortando_el_texto(
        intake_world, conn, monkeypatch):
    """R8: el cuerpo del resumen se guarda aparte del cierre. Aunque el texto
    visible de la revisión no tenga la forma `cuerpo + párrafo de cierre`
    (otra redacción), quien confirma recibe el cuerpo completo, nunca sólo el
    cierre."""
    rid, pid = _alta_en_revision(conn, intake_world)
    (revision, *_) = _acciones(conn, rid)
    cuerpo = revision["args"]["cuerpo_resumen"]
    assert cuerpo and I.cierre_enviar("Morgan Hale 1") not in cuerpo
    with admin(conn) as cur:
        cur.execute("update pending_action set resumen = %s where id = %s",
                    ("Un resumen en un solo párrafo, sin cierre aparte.", pid))
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)

    _tocar(client, conn, user, pid, "Enviar a aprobación")

    (_, confirmacion) = _acciones(conn, rid)
    assert _fila(conn, confirmacion["id"])["cuerpo"] == (
        _linea_de_quien_pide(conn, intake_world) + "\n\n" + cuerpo + "\n\n"
        + I.CIERRE_CONFIRMAR)


def test_enviar_le_manda_el_borrador_a_quien_confirma_y_le_dice_a_quien_pide(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    antes = _salidas(conn, user)
    tg_aprobador = _tg_aprobador(intake_world)

    _tocar(client, conn, user, pid, "Enviar a aprobación")

    # A quien pide, UNA respuesta: a quién se le mandó y que la tarea todavía no existe.
    nuevas = _nuevas(conn, user, antes)
    assert [f["cuerpo"] for f in nuevas] == [
        I.draft_sent_text(_nombre_del_aprobador(conn, intake_world))]
    with admin(conn) as cur:
        cur.execute("select es_respuesta from message_outbox where id = %s",
                    (nuevas[0]["id"],))
        assert cur.fetchone()["es_respuesta"] is True
    # A quien confirma, el mismo resumen con Confirmar y Rechazar, iniciado por Leda.
    (revision, confirmacion) = _acciones(conn, rid)
    assert revision["estado"] == "cancelada" and confirmacion["estado"] == "esperando"
    assert confirmacion["chat_id"] == tg_aprobador
    assert confirmacion["herramienta"] != revision["herramienta"]
    assert _etiquetas(conn, confirmacion["id"]) == ETIQUETAS_DEL_APROBADOR
    fila = _fila(conn, confirmacion["id"])
    assert fila["chat_id"] == tg_aprobador and fila["es_respuesta"] is False
    # Los mismos datos; el cierre dice lo que hace el botón de cada uno (R4c-H9).
    cuerpo = revision["args"]["cuerpo_resumen"]
    assert fila["cuerpo"] == (
        _linea_de_quien_pide(conn, intake_world) + "\n\n"
        + I._con_cierre(cuerpo, I.CIERRE_CONFIRMAR))
    assert revision["resumen"].endswith(I.cierre_enviar("Morgan Hale 1"))
    # La versión y la vista previa son las del borrador vigente al enviar.
    assert confirmacion["draft_version"] == revision["draft_version"]
    assert confirmacion["preview"] == revision["preview"]
    # Enviar no convierte ni cancela nada: la solicitud sigue activa.
    assert _tareas(conn) == 0 and _solicitud(conn, rid) == "active"
    with admin(conn) as cur:
        cur.execute("select d.estado from task_draft d join task_intake_request r "
                    "on r.task_draft_id = d.id where r.id = %s", (rid,))
        assert cur.fetchone()["estado"] != "cancelled"


def test_despues_de_enviar_la_rama_pasa_a_quien_confirma(intake_world, conn,
                                                         monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)

    _tocar(client, conn, user, pid, "Enviar a aprobación")

    assert _pregunta_abierta(conn, intake_world, user) is None
    # Sólo la fila de quien confirma sigue esperando (nunca dos: `limit 1`).
    assert [a["estado"] for a in _acciones(conn, rid)].count("esperando") == 1


def test_quien_confirma_convierte_el_borrador_recien_despues_de_enviarlo(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    ws = intake_world["north-lab"]["id"]
    client = _callback_client(conn, monkeypatch)
    _tocar(client, conn, user, pid, "Enviar a aprobación")
    (_, confirmacion) = _acciones(conn, rid)
    tg_aprobador = _tg_aprobador(intake_world)

    with autoridad(authority_conn) as cur:
        resuelta = P.resolver_borrador(
            cur, ws, _token(conn, confirmacion["id"], "Confirmar"),
            tg_aprobador, tg_aprobador)

    assert resuelta and resuelta.task_id and _tareas(conn) == 1
    assert _solicitud(conn, rid) == "converted"


def test_el_toque_repetido_de_enviar_no_lo_manda_dos_veces(intake_world, conn,
                                                          monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    _tocar(client, conn, user, pid, "Enviar a aprobación")
    de_quien_pide = _salidas(conn, user)
    del_aprobador = _salidas(conn, _tg_aprobador(intake_world))

    _tocar(client, conn, user, pid, "Enviar a aprobación")       # dentro de la ventana

    assert _salidas(conn, user) == de_quien_pide                 # absorbido: nada nuevo
    assert _salidas(conn, _tg_aprobador(intake_world)) == del_aprobador
    assert len(_acciones(conn, rid)) == 2


def test_un_toque_tardio_de_enviar_no_lo_manda_de_nuevo_y_dice_que_ya_no_esta_vigente(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    _tocar(client, conn, user, pid, "Enviar a aprobación")
    del_aprobador = _salidas(conn, _tg_aprobador(intake_world))
    envejecer_toques(conn, FUERA_DE_LA_VENTANA)
    antes = _salidas(conn, user)

    _tocar(client, conn, user, pid, "Enviar a aprobación")

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [AVISO_TOQUE_YA_USADO]
    assert _salidas(conn, _tg_aprobador(intake_world)) == del_aprobador
    assert len(_acciones(conn, rid)) == 2


def _opciones_de(conn, pid) -> list[str]:
    """Las opciones activas de la acción (las de una acción cerrada, ninguna)."""
    with admin(conn) as cur:
        cur.execute("select etiqueta from pending_action_option "
                    "where pending_action_id = %s and activa", (pid,))
        return [etiqueta_sin_icono(f["etiqueta"]) for f in cur.fetchall()]


def _dejar_atras_el_resumen(conn, rid, titulo="Inspect pressure valve"):
    """El borrador siguió después de que quien pide vio su resumen: cambia un dato
    (en el dato de la solicitud y en el borrador) y sube la versión."""
    with admin(conn) as cur:
        cur.execute("update task_intake_field set valor = to_jsonb(%s::text) "
                    "where request_id = %s and campo = 'title'", (titulo, rid))
        cur.execute(
            """update task_draft set titulo = %s, version = version + 1
                where id = (select task_draft_id from task_intake_request
                             where id = %s)""", (titulo, rid))
    conn.commit()


def test_enviar_un_resumen_que_el_borrador_dejo_atras_ofrece_la_revision_vigente(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    _dejar_atras_el_resumen(conn, rid)
    antes = _salidas(conn, user)

    _tocar(client, conn, user, pid, "Enviar a aprobación")

    # UNA respuesta atada al toque: el resumen vigente con sus tres botones, y no
    # sólo "ya no está vigente" (ADR 0013 reglas 2 y 3).
    (unica,) = _nuevas(conn, user, antes)
    (vieja, nueva) = _acciones(conn, rid)
    assert vieja["estado"] == "vencida" and nueva["estado"] == "esperando"
    assert str(unica["pending_action_id"]) == str(nueva["id"])
    assert unica["cuerpo"].startswith(I.DRAFT_CHANGED_REVIEW_AGAIN)
    assert nueva["resumen"] in unica["cuerpo"]
    assert "Inspect pressure valve" in nueva["resumen"]
    assert nueva["preview"]["titulo"] == "Inspect pressure valve"
    assert nueva["chat_id"] == user and _fila(conn, nueva["id"])["es_respuesta"] is True
    assert _etiquetas(conn, nueva["id"]) == ETIQUETAS_DE_LA_REVISION
    assert _opciones_de(conn, pid) == []          # los botones viejos ya no valen
    # Nada llegó a quien confirma, y la revisión vigente es la rama abierta.
    assert _salidas(conn, _tg_aprobador(intake_world)) == []
    assert str(_pregunta_abierta(conn, intake_world, user)["id"]) == str(nueva["id"])
    assert _tareas(conn) == 0 and _solicitud(conn, rid) == "active"


def test_el_toque_repetido_sobre_el_resumen_que_quedo_atras_no_ofrece_dos_revisiones(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    _dejar_atras_el_resumen(conn, rid)
    _tocar(client, conn, user, pid, "Enviar a aprobación")
    de_quien_pide = _salidas(conn, user)

    _tocar(client, conn, user, pid, "Enviar a aprobación")       # dentro de la ventana

    assert _salidas(conn, user) == de_quien_pide
    assert [a["estado"] for a in _acciones(conn, rid)] == ["vencida", "esperando"]
    assert _salidas(conn, _tg_aprobador(intake_world)) == []


def test_despues_de_la_revision_vigente_enviar_manda_lo_que_quien_pide_reviso(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    _dejar_atras_el_resumen(conn, rid)
    _tocar(client, conn, user, pid, "Enviar a aprobación")
    (_, nueva) = _acciones(conn, rid)
    antes = _salidas(conn, user)

    _tocar(client, conn, user, nueva["id"], "Enviar a aprobación")

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [
        I.draft_sent_text(_nombre_del_aprobador(conn, intake_world))]
    (_, _, confirmacion) = _acciones(conn, rid)
    assert confirmacion["estado"] == "esperando"
    assert confirmacion["chat_id"] == _tg_aprobador(intake_world)
    assert confirmacion["preview"] == nueva["preview"]
    assert "Inspect pressure valve" in confirmacion["resumen"]
    assert _etiquetas(conn, confirmacion["id"]) == ETIQUETAS_DEL_APROBADOR


def _pasar_la_aprobacion_a_quien_pide(conn, world, rid, pid):
    """Al momento de enviar, quien aprueba lo del borrador es quien lo pidió: la
    persona responsable pasa a ser alguien a quien Taylor Quinn aprueba (Sam North).
    Sólo cambia la persona responsable: el resumen que quien pide revisó sigue siendo
    el vigente (su vista previa se actualiza con el borrador)."""
    sam = world["north-lab"]["people"]["Sam North"]["membership_id"]
    with admin(conn) as cur:
        cur.execute(
            "update task_draft set responsable_membership_id = %s "
            "where id = (select task_draft_id from task_intake_request where id = %s)",
            (sam, rid))
        cur.execute("select task_draft_id from task_intake_request where id = %s",
                    (rid,))
        vigente, _ = I._current_preview(cur, cur.fetchone()["task_draft_id"])
        cur.execute("update pending_action set preview = %s where id = %s",
                    (Jsonb(vigente), pid))
    conn.commit()


def test_si_al_enviar_quien_aprueba_paso_a_ser_quien_pide_recibe_una_sola_respuesta(
        intake_world, conn, monkeypatch):
    """La revisión se armó con otra persona como aprobadora; al enviar, quien aprueba
    es quien pidió: el resumen con Confirmar, Modificar y Cancelar es LA respuesta a
    su toque, sin aviso neutro encima y sin mandarle nada a la otra persona."""
    user = _usuario(intake_world)
    rid, pid = _alta_en_revision(conn, intake_world)
    assert _etiquetas(conn, pid) == ETIQUETAS_DE_LA_REVISION
    _pasar_la_aprobacion_a_quien_pide(conn, intake_world, rid, pid)
    client = _callback_client(conn, monkeypatch)
    antes = _salidas(conn, user)

    _tocar(client, conn, user, pid, "Enviar a aprobación")

    (unica,) = _nuevas(conn, user, antes)
    (revision, confirmacion) = _acciones(conn, rid)
    assert revision["estado"] == "cancelada" and confirmacion["estado"] == "esperando"
    assert str(unica["pending_action_id"]) == str(confirmacion["id"])
    assert unica["cuerpo"] == I._con_cierre(
        revision["args"]["cuerpo_resumen"], I.CIERRE_CONFIRMAR)
    assert not unica["cuerpo"].startswith("No pude completar eso")
    assert confirmacion["chat_id"] == user
    assert _etiquetas(conn, confirmacion["id"]) == [
        "Confirmar", "Modificar", "Cancelar"]
    assert _fila(conn, confirmacion["id"])["es_respuesta"] is True
    assert _salidas(conn, _tg_aprobador(intake_world)) == []


def test_los_otros_botones_de_la_revision_ya_enviada_no_valen(intake_world, conn,
                                                              monkeypatch,
                                                              authority_conn):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    ws = intake_world["north-lab"]["id"]
    client = _callback_client(conn, monkeypatch)
    _tocar(client, conn, user, pid, "Enviar a aprobación")
    envejecer_toques(conn, FUERA_DE_LA_VENTANA)

    with autoridad(authority_conn) as cur:
        assert P.resolver_borrador(
            cur, ws, _token(conn, pid, "Cancelar"), user, user) is None
    _tocar(client, conn, user, pid, "Modificar")

    assert _solicitud(conn, rid) == "active"               # nada se canceló ni se abrió
    assert _pregunta_abierta(conn, intake_world, user) is None


def test_enviar_lo_toca_solo_su_dueno(intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    ajena = intake_world["north-lab"]["people"]["Sam Noble"]["telegram"]
    client = _callback_client(conn, monkeypatch)
    antes = _salidas(conn, ajena)

    _tocar(client, conn, ajena, pid, "Enviar a aprobación")

    assert [f["cuerpo"] for f in _nuevas(conn, ajena, antes)] == [
        "Eso se lo pregunté a otra persona del equipo."]
    assert [a["estado"] for a in _acciones(conn, rid)] == ["esperando"]
    assert _salidas(conn, _tg_aprobador(intake_world)) == []


def test_sin_autoridad_al_enviar_lo_dice_y_la_revision_sigue_abierta(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    with admin(conn) as cur:
        cur.execute("update app_user set telegram_user_id = null "
                    "where telegram_user_id = %s", (_tg_aprobador(intake_world),))
    conn.commit()
    antes = _salidas(conn, user)

    _tocar(client, conn, user, pid, "Enviar a aprobación")

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [
        I.NO_ACTIVE_AUTHORITY]
    assert [a["estado"] for a in _acciones(conn, rid)] == ["esperando"]


# ------------------------------------------------------------- Cancelar

def test_cancelar_la_revision_cancela_el_borrador_sin_avisarle_a_quien_confirma(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    ws = intake_world["north-lab"]["id"]

    with autoridad(authority_conn) as cur:
        resuelta = P.resolver_borrador(
            cur, ws, _token(conn, pid, "Cancelar"), user, user)

    assert resuelta is not None and resuelta.cancelada
    assert _solicitud(conn, rid) == "cancelled" and _tareas(conn) == 0
    assert _salidas(conn, _tg_aprobador(intake_world)) == []


# ------------------------------------------------------------- Modificar

def test_modificar_en_la_revision_abre_el_mismo_selector_y_no_le_manda_nada_a_quien_confirma(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _revision_tocada(conn, monkeypatch, intake_world)

    assert [a["estado"] for a in _acciones(conn, rid)] == ["cancelada"]
    assert list(_opciones_activas(conn, rid)) == [
        "Título", "Descripción", "Objetivo", "Responsable",
        "Fecha objetivo", "Criterio de aceptación", "Volver al resumen"]
    assert _salidas(conn, _tg_aprobador(intake_world)) == []
    assert _tareas(conn) == 0


def test_un_dato_corregido_vuelve_a_la_revision_de_quien_pide_y_no_va_a_quien_confirma(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _revision_tocada(conn, monkeypatch, intake_world)
    _elegir_dato(conn, client, user, rid, "Título")
    antes = _salidas(conn, user)

    _responder_con(conn, monkeypatch, intake_world, "Inspect pressure valve")

    (vieja, nueva) = _acciones(conn, rid)
    assert vieja["estado"] == "cancelada" and nueva["estado"] == "esperando"
    assert "Inspect pressure valve" in nueva["resumen"]
    assert _etiquetas(conn, nueva["id"]) == ETIQUETAS_DE_LA_REVISION
    assert nueva["chat_id"] == user
    assert [str(f["pending_action_id"]) for f in _nuevas(conn, user, antes)] == [
        str(nueva["id"])]
    assert _fila(conn, nueva["id"])["es_respuesta"] is True
    assert _salidas(conn, _tg_aprobador(intake_world)) == []


def test_un_dato_con_opciones_corregido_tambien_vuelve_a_la_revision(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _revision_tocada(conn, monkeypatch, intake_world)
    _elegir_dato(conn, client, user, rid, "Objetivo")
    otro = next(t for e, t in _opciones_activas(conn, rid).items()
                if "Raise delivery quality" in e)
    from tests.test_task_intake import _post_intake_callback

    assert _post_intake_callback(client, otro, user).status_code == 200

    (vieja, nueva) = _acciones(conn, rid)
    assert nueva["estado"] == "esperando" and nueva["chat_id"] == user
    assert "Raise delivery quality 1" in nueva["resumen"]
    assert _etiquetas(conn, nueva["id"]) == ETIQUETAS_DE_LA_REVISION
    assert _salidas(conn, _tg_aprobador(intake_world)) == []


def test_volver_al_resumen_vuelve_a_la_revision_de_quien_pide(intake_world, conn,
                                                             monkeypatch):
    rid, pid, client, user = _revision_tocada(conn, monkeypatch, intake_world)
    antes = _salidas(conn, user)

    _tocar_volver(conn, client, user, rid)

    (vieja, nueva) = _acciones(conn, rid)
    assert nueva["estado"] == "esperando" and nueva["chat_id"] == user
    assert nueva["resumen"] == vieja["resumen"]
    assert _etiquetas(conn, nueva["id"]) == ETIQUETAS_DE_LA_REVISION
    assert [str(f["pending_action_id"]) for f in _nuevas(conn, user, antes)] == [
        str(nueva["id"])]
    assert _salidas(conn, _tg_aprobador(intake_world)) == []


def test_despues_de_corregir_enviar_le_manda_a_quien_confirma_lo_corregido(
        intake_world, conn, monkeypatch):
    rid, pid, client, user = _revision_tocada(conn, monkeypatch, intake_world)
    _elegir_dato(conn, client, user, rid, "Título")
    _responder_con(conn, monkeypatch, intake_world, "Inspect pressure valve")
    (_, nueva) = _acciones(conn, rid)

    _tocar(client, conn, user, nueva["id"], "Enviar a aprobación")

    (_, _, confirmacion) = _acciones(conn, rid)
    assert confirmacion["estado"] == "esperando"
    assert "Inspect pressure valve" in confirmacion["resumen"]
    assert confirmacion["preview"]["titulo"] == "Inspect pressure valve"
    (fila,) = [f for f in _salidas(conn, _tg_aprobador(intake_world))
               if f["pending_action_id"]]
    assert "Inspect pressure valve" in fila["cuerpo"]


def test_las_claves_de_la_revision_y_de_la_vista_previa_de_quien_confirma_son_distintas(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    _tocar(client, conn, user, pid, "Enviar a aprobación")
    (revision, confirmacion) = _acciones(conn, rid)

    with admin(conn) as cur:
        cur.execute("select pending_action_id, dedupe_key from message_outbox "
                    "where pending_action_id = any(%s)",
                    ([revision["id"], confirmacion["id"]],))
        claves = {str(f["pending_action_id"]): f["dedupe_key"] for f in cur.fetchall()}

    assert len(claves) == 2
    assert claves[str(revision["id"])] != claves[str(confirmacion["id"])]


# ------------------------------------- lo que escribe quien pide con la revisión abierta

@pytest.mark.parametrize("comando", [RespectoPendiente.CHARLA,
                                     RespectoPendiente.RESPONDE])
def test_lo_que_escribe_con_la_revision_abierta_nombra_sus_botones_y_no_envia_nada(
        comando, intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(comando)])

    _escribir(conn, monkeypatch, intake_world, provider, "sí, dale, mandalo")

    (unica,) = _nuevas(conn, user, antes)
    assert unica["cuerpo"] == I.DRAFT_AWAITING_SEND
    assert provider.main_calls == 0
    assert [a["estado"] for a in _acciones(conn, rid)] == ["esperando"]
    assert _salidas(conn, _tg_aprobador(intake_world)) == []
    assert _tareas(conn) == 0


def test_corregir_por_escrito_con_la_revision_abierta_abre_el_selector(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    provider = _RoutingProvider([_ruta(RespectoPendiente.CORRIGE)])

    _escribir(conn, monkeypatch, intake_world, provider, "el título está mal")

    assert [a["estado"] for a in _acciones(conn, rid)] == ["cancelada"]
    assert "Volver al resumen" in _opciones_activas(conn, rid)
    assert _salidas(conn, _tg_aprobador(intake_world)) == []


def test_cancelar_por_escrito_con_la_revision_abierta_cancela_el_borrador(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    provider = _RoutingProvider([_ruta(RespectoPendiente.CANCELA)])

    _escribir(conn, monkeypatch, intake_world, provider, "no, cancelalo")

    assert _solicitud(conn, rid) == "cancelled"
    assert _salidas(conn, _tg_aprobador(intake_world)) == []


def test_despues_de_enviar_lo_que_escribe_quien_pide_sigue_el_camino_normal(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    _tocar(client, conn, user, pid, "Enviar a aprobación")
    antes = _salidas(conn, user)
    from leda.llm import IntentAction, IntentRoute

    provider = _RoutingProvider([IntentRoute(IntentAction.NORMAL_CONVERSATION)],
                                answer="Un bloqueo frena una tarea.")

    _escribir(conn, monkeypatch, intake_world, provider, "¿qué es un bloqueo?")

    assert provider.pending_calls == [None]        # ruteado sin pregunta pendiente
    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [
        "Un bloqueo frena una tarea."]


# ------------------- F-B3: lo enviado a otra persona no es la rama abierta de quien pide

def _pedir_otra_tarea(conn, monkeypatch, world, user):
    """"quiero crear otra tarea" como lo rutea el modelo sin pregunta pendiente."""
    from leda.llm import IntentAction, IntentRoute

    provider = _RoutingProvider([IntentRoute(IntentAction.START_TASK_INTAKE)])
    _escribir(conn, monkeypatch, world, provider, "quiero crear otra tarea")
    return provider


def _entrante(cur, quien, user) -> str:
    cur.execute(
        """insert into inbound_message
             (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
           values (%s, 99001, %s, %s, 'otra') returning id""",
        (quien.workspace_id, user, quien.app_user_id))
    return str(cur.fetchone()["id"])


def _solicitudes(conn, user) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("""select id, estado, enviada_en is not null enviada
                         from task_intake_request where chat_id = %s
                        order by creado_en, id""", (user,))
        return cur.fetchall()


def test_despues_de_enviar_pedir_otra_tarea_la_empieza_sin_tocar_la_enviada(
        intake_world, conn, monkeypatch):
    """F-B3 (ADR 0013, enmienda): el borrador que espera a otra persona no es la
    rama abierta de quien lo pidió. Antes: "Ya hay un borrador en curso" y, con
    Cancelar, quedaba cancelado el que esperaba aprobación."""
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    _tocar(client, conn, user, pid, "Enviar a aprobación")
    (_, confirmacion) = _acciones(conn, rid)
    antes = _salidas(conn, user)

    _pedir_otra_tarea(conn, monkeypatch, intake_world, user)

    (ultimo,) = _nuevas(conn, user, antes)
    assert "Ya hay un borrador" not in ultimo["cuerpo"]
    assert ultimo["cuerpo"] == "¿Qué hay que hacer?"        # empezó la nueva alta
    enviada, nueva = _solicitudes(conn, user)
    assert str(enviada["id"]) == rid and enviada["estado"] == "active"
    assert enviada["enviada"] and not nueva["enviada"] and nueva["estado"] == "active"
    # El borrador enviado sigue esperando a quien lo confirma.
    assert [a["estado"] for a in _acciones(conn, rid)] == ["cancelada", "esperando"]
    assert str(_acciones(conn, rid)[1]["id"]) == str(confirmacion["id"])


def test_la_nueva_alta_y_la_enviada_conviven_y_quien_confirma_convierte_la_enviada(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    ws = intake_world["north-lab"]["id"]
    client = _callback_client(conn, monkeypatch)
    _tocar(client, conn, user, pid, "Enviar a aprobación")
    (_, confirmacion) = _acciones(conn, rid)
    _pedir_otra_tarea(conn, monkeypatch, intake_world, user)
    tg_aprobador = _tg_aprobador(intake_world)

    with autoridad(authority_conn) as cur:
        resuelta = P.resolver_borrador(
            cur, ws, _token(conn, confirmacion["id"], "Confirmar"),
            tg_aprobador, tg_aprobador)

    assert resuelta and resuelta.task_id and _tareas(conn) == 1
    enviada, nueva = _solicitudes(conn, user)
    assert enviada["estado"] == "converted" and nueva["estado"] == "active"
    # La pregunta abierta de quien pide es la de la alta nueva.
    assert _pregunta_abierta(conn, intake_world, user)["resumen"] == (
        "¿Qué hay que hacer?")


def test_la_pregunta_abierta_de_quien_pide_es_de_la_alta_nueva_no_de_la_enviada(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    _tocar(client, conn, user, pid, "Enviar a aprobación")
    _pedir_otra_tarea(conn, monkeypatch, intake_world, user)
    antes = _salidas(conn, user)
    from leda.llm import IntentAction, IntentRoute

    # Un mensaje con la nueva alta abierta es de ESA rama: el ruteo recibe su
    # pregunta, no la de la enviada.
    provider = _RoutingProvider([IntentRoute(
        IntentAction.NORMAL_CONVERSATION,
        respecto_pendiente=RespectoPendiente.CHARLA)])
    _escribir(conn, monkeypatch, intake_world, provider, "gracias")

    assert "¿Qué hay que hacer?" in provider.pending_calls[0]
    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == ["¿Qué hay que hacer?"]


def test_con_la_revision_todavia_abierta_empezar_otra_sigue_siendo_el_conflicto(
        intake_world, conn):
    """Sin enviar, el borrador SÍ es su rama abierta: nada cambia."""
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        quien = identificar(cur, user, Canal.ESPACIO, intake_world["north-lab"]["id"])
        outcome = I.start(cur, quien, chat_id=user,
                          source_inbound_id=_entrante(cur, quien, user),
                          source_raw_text="otra", proposals={}, now=NOW)
    assert "Ya hay un borrador" in outcome.text
    assert len(_solicitudes(conn, user)) == 1


# ----------------------------------------- quien pide es quien confirma: no cambia

def test_si_quien_pide_es_quien_confirma_nada_cambia(intake_world, conn):
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")

    assert _etiquetas(conn, pid) == ["Confirmar", "Modificar", "Cancelar"]
    assert _pregunta_abierta(conn, intake_world, user)["resumen"] == (
        I.DRAFT_AWAITING_CONFIRMATION)
    assert [str(f["pending_action_id"]) for f in _nuevas(conn, user, antes)
            if f["pending_action_id"]] == [str(pid)]


def test_un_resumen_que_el_borrador_dejo_atras_no_se_envia(intake_world, conn,
                                                           monkeypatch):
    """Lo que recibe quien confirma es lo que quien pide revisó: si el borrador
    cambió después de ese resumen, enviarlo no manda nada a quien confirma (quien
    pide recibe el resumen vigente para revisarlo: T9-R1c-4b)."""
    rid, pid = _alta_en_revision(conn, intake_world)
    user = _usuario(intake_world)
    client = _callback_client(conn, monkeypatch)
    with admin(conn) as cur:
        cur.execute("update task_draft set titulo = 'Otro título' where id = "
                    "(select task_draft_id from task_intake_request where id = %s)",
                    (rid,))
    conn.commit()
    antes = _salidas(conn, user)

    _tocar(client, conn, user, pid, "Enviar a aprobación")

    assert len(_nuevas(conn, user, antes)) == 1
    assert _salidas(conn, _tg_aprobador(intake_world)) == []
    assert [a["estado"] for a in _acciones(conn, rid)] == ["vencida", "esperando"]
    assert _tareas(conn) == 0
