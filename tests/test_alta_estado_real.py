"""Decir el estado real al terminar el alta (T9-R3, ADR 0013 regla 3).

Cuando quien termina el alta guiada no es quien la confirma, hasta ahora no le
salía nada: el control de "una respuesta por mensaje" (regla 2) le mandaba "No
pude completar eso" y un incidente aunque todo había salido bien. Ahora la
respuesta dice a quién se le mandó el borrador para que lo confirme, por el
toque y por el mensaje. Los tres resultados del alta que devolvían un texto que
nadie encolaba ("No hay una política de evidencia vigente…", "Alguna opción
confirmada ya no está vigente.", "No hay una autoridad activa…") tampoco caen
en el aviso neutro: su texto específico es la respuesta.

Los ruteos y el modelo se guionan; ninguna prueba toca la red ni el modelo real.
"""

from __future__ import annotations

import pytest

from prisma import gateway
from prisma import ingreso_tareas as I
from prisma.db import admin, espacio
from prisma.llm import RespectoPendiente

from tests.test_alta_eleccion_confirmacion import (_escribir, _nuevas, _ruta,
                                                   _salidas, _usuario)
from tests.test_task_intake import (_RoutingProvider, _active_choices,
                                    _callback_client, _choose,
                                    _post_intake_callback, _start)
from tests.test_una_respuesta import _incidentes

CRITERIO = "Prueba firmada"


def _alta_hasta_el_criterio(conn, world, responsable: str, *,
                            rechazar_el_criterio: bool = False) -> str:
    """El alta con todo confirmado salvo el criterio de aceptación, que espera su
    último toque. Con `rechazar_el_criterio`, ya tocó "No" y el criterio se
    espera escrito. Devuelve el id de la solicitud."""
    user = _usuario(world)
    with espacio(conn, world["north-lab"]["id"]) as cur:
        actor, outcome = _start(cur, world, chat_id=user)
        rid = outcome.request_id
        _choose(cur, actor, rid, "Sí", chat_id=user)
        cur.execute("""select campo from task_intake_choice_set
                        where request_id = %s and estado = 'active'""", (rid,))
        if cur.fetchone()["campo"] == "description":
            _choose(cur, actor, rid, "Sí", chat_id=user)
        for parte in ("Reduce service delay", responsable, "Field Services"):
            etiqueta = next(e for e in _active_choices(cur, rid) if parte in e)
            _choose(cur, actor, rid, etiqueta, chat_id=user)
        _choose(cur, actor, rid, "Sí", chat_id=user)           # la fecha
        if rechazar_el_criterio:
            _choose(cur, actor, rid, "No", chat_id=user)
    conn.commit()
    return rid


def _tocar_si(conn, monkeypatch, rid, user):
    with admin(conn) as cur:
        token = next(t for e, t in _active_choices(cur, rid).items() if e == "Sí")
    client = _callback_client(conn, monkeypatch)
    assert _post_intake_callback(client, token, user).status_code == 200


def _es_respuesta(conn, chat_id, cuerpo) -> bool:
    with admin(conn) as cur:
        cur.execute("select es_respuesta from message_outbox "
                    "where chat_id = %s and cuerpo = %s", (chat_id, cuerpo))
        return cur.fetchone()["es_respuesta"]


APROBADOR = "Morgan Hale"          # quien aprueba lo de Taylor Quinn en el mundo de prueba


def _telegram_del_aprobador(world) -> int:
    return world["north-lab"]["people"][APROBADOR]["telegram"]


def _enviado(conn, world) -> str:
    """El aviso con el nombre real del aprobador, leído de la base."""
    with admin(conn) as cur:
        cur.execute("select nombre from app_user where telegram_user_id = %s",
                    (_telegram_del_aprobador(world),))
        return I.draft_sent_text(cur.fetchone()["nombre"])


# --------------------------------------------- quien pide no es quien confirma

def test_por_el_toque_quien_pide_el_alta_recibe_a_quien_se_le_mando(
        intake_world, conn, monkeypatch):
    rid = _alta_hasta_el_criterio(conn, intake_world, "Para mí")
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    enviado = _enviado(conn, intake_world)

    _tocar_si(conn, monkeypatch, rid, user)

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [enviado]
    assert APROBADOR in enviado
    assert _es_respuesta(conn, user, enviado)
    # La vista previa con los botones sigue siendo del aprobador.
    assert any(f["pending_action_id"]
               for f in _salidas(conn, _telegram_del_aprobador(intake_world)))


def test_por_el_mensaje_quien_pide_el_alta_recibe_una_sola_respuesta_sin_incidente(
        intake_world, conn, monkeypatch):
    rid = _alta_hasta_el_criterio(conn, intake_world, "Para mí",
                                  rechazar_el_criterio=True)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    enviado = _enviado(conn, intake_world)
    provider = _RoutingProvider([_ruta(RespectoPendiente.RESPONDE)])

    _escribir(conn, monkeypatch, intake_world, provider, CRITERIO)

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [enviado]
    assert provider.main_calls == 0
    ws = intake_world["north-lab"]["id"]
    assert _incidentes(conn, ws, "sin_respuesta") == []
    assert _incidentes(conn, ws, "respuesta_duplicada") == []


def test_si_quien_pide_es_quien_confirma_su_respuesta_es_la_vista_previa(
        intake_world, conn, monkeypatch):
    rid = _alta_hasta_el_criterio(conn, intake_world, "Sam North")
    user = _usuario(intake_world)
    antes = _salidas(conn, user)

    _tocar_si(conn, monkeypatch, rid, user)

    (unica,) = _nuevas(conn, user, antes)
    assert unica["pending_action_id"]                  # la vista previa con botones
    assert I.DRAFT_SENT_TO_APPROVER.split("{")[0] not in unica["cuerpo"]


@pytest.mark.parametrize("nombre", [None, "", "   "])
def test_sin_un_nombre_legible_el_aviso_no_inventa_ninguno(nombre):
    texto = I.draft_sent_text(nombre)

    assert texto == I.DRAFT_SENT_TO_SOMEONE_ELSE
    assert "None" not in texto and "{" not in texto


def test_el_aviso_dice_que_la_tarea_todavia_no_existe():
    # Regla 3: cómo quedó y qué falta -- la tarea se crea cuando la confirme.
    assert "confirm" in I.draft_sent_text("Morgan Hale").lower()
    assert "Morgan Hale" in I.draft_sent_text("Morgan Hale")


# ------------------------------------- los resultados del alta que nadie decía

def _sin_politica_de_evidencia(conn, world):
    with admin(conn) as cur:
        cur.execute("delete from task_evidence_policy where workspace_id = %s",
                    (world["north-lab"]["id"],))


def _sin_telegram_el_aprobador(conn, world):
    with admin(conn) as cur:
        cur.execute("update app_user set telegram_user_id = null "
                    "where telegram_user_id = %s", (_telegram_del_aprobador(world),))


@pytest.mark.parametrize("sabotaje, texto", [
    (_sin_politica_de_evidencia,
     "No hay una política de evidencia vigente para esa área."),
    (_sin_telegram_el_aprobador,
     "No hay una autoridad activa que pueda revisar el borrador."),
], ids=["sin_politica_de_evidencia", "sin_autoridad_activa"])
def test_por_el_toque_el_resultado_inerte_del_alta_es_la_respuesta(
        sabotaje, texto, intake_world, conn, monkeypatch):
    rid = _alta_hasta_el_criterio(conn, intake_world, "Para mí")
    user = _usuario(intake_world)
    sabotaje(conn, intake_world)
    antes = _salidas(conn, user)

    _tocar_si(conn, monkeypatch, rid, user)

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [texto]
    assert _es_respuesta(conn, user, texto)


@pytest.mark.parametrize("sabotaje, texto", [
    (_sin_politica_de_evidencia,
     "No hay una política de evidencia vigente para esa área."),
    (_sin_telegram_el_aprobador,
     "No hay una autoridad activa que pueda revisar el borrador."),
], ids=["sin_politica_de_evidencia", "sin_autoridad_activa"])
def test_por_el_mensaje_el_resultado_inerte_del_alta_es_la_respuesta_sin_aviso_neutro(
        sabotaje, texto, intake_world, conn, monkeypatch):
    rid = _alta_hasta_el_criterio(conn, intake_world, "Para mí",
                                  rechazar_el_criterio=True)
    user = _usuario(intake_world)
    sabotaje(conn, intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(RespectoPendiente.RESPONDE)])

    _escribir(conn, monkeypatch, intake_world, provider, CRITERIO)

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [texto]
    assert gateway.NOTICIA_NEUTRA_INCIDENTE not in [
        f["cuerpo"] for f in _salidas(conn, user)]
    assert _incidentes(conn, intake_world["north-lab"]["id"], "sin_respuesta") == []


def test_una_opcion_confirmada_que_ya_no_vale_es_la_respuesta(
        intake_world, conn, monkeypatch):
    rid = _alta_hasta_el_criterio(conn, intake_world, "Para mí")
    user = _usuario(intake_world)
    with admin(conn) as cur:                    # el objetivo elegido se canceló
        cur.execute("update objective set estado = 'cancelado' "
                    "where workspace_id = %s", (intake_world["north-lab"]["id"],))
    antes = _salidas(conn, user)

    _tocar_si(conn, monkeypatch, rid, user)

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [
        "Alguna opción confirmada ya no está vigente."]


def test_una_eleccion_escrita_con_un_resultado_inerte_no_repregunta(
        intake_world, conn, monkeypatch):
    """Escribir "Sí" con la última elección abierta sigue como el toque: si el
    alta termina en un estado real, ese texto es la respuesta y la pregunta no
    se vuelve a hacer encima."""
    _alta_hasta_el_criterio(conn, intake_world, "Para mí")
    user = _usuario(intake_world)
    _sin_politica_de_evidencia(conn, intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([_ruta(RespectoPendiente.RESPONDE)])

    _escribir(conn, monkeypatch, intake_world, provider, "Sí")

    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [
        "No hay una política de evidencia vigente para esa área."]
