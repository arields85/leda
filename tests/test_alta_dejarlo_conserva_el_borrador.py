"""Dejar una rama para ver otra cosa no destruye el trabajo (F-C6).

"Dejarlo y ver lo otro" (y "No, es otra cosa") cancelaba el borrador entero
detrás de una clasificación que puede fallar: con "ayudame, que puedo poner?" y
"por que anda" se perdió el borrador "calibrar los sensores". Ahora el borrador
queda guardado, pausado (sin ninguna pregunta abierta que tome los mensajes
siguientes), y el próximo "quiero crear una tarea" ofrece continuarlo. Sólo un
Cancelar explícito (el botón, o "cancelá todo" por escrito) lo cancela.

Los ruteos y el modelo se guionan; ninguna prueba toca la red ni el modelo real.
"""

from __future__ import annotations

import pytest

from leda import gateway
from leda import ingreso_tareas as I
from leda.db import admin, espacio
from leda.llm import IntentAction, IntentRoute, RespectoPendiente

from tests.test_alta_eleccion_confirmacion import (
    TITULO, _alta_con_eleccion, _alta_en_confirmacion, _callback_client,
    _conjunto_activo, _escribir, _nuevas, _RoutingProvider, _ruta, _salidas,
    _solicitud, _tocar_boton, _token_de, _usuario)
from tests.test_task_intake import NOW, _actor, _choose


def _pausado(conn, rid) -> bool:
    with admin(conn) as cur:
        cur.execute("select terminal_result from task_intake_request "
                    "where id = %s", (rid,))
        fila = cur.fetchone()
    return bool((fila["terminal_result"] or {}).get("pausado"))


def _abiertas(conn, rid) -> int:
    """Las preguntas del alta que siguen esperando una respuesta."""
    with admin(conn) as cur:
        cur.execute("""select
              (select count(*) from task_intake_choice_set
                where request_id = %(r)s and estado = 'active')
            + (select count(*) from task_intake_free_text_slot
                where request_id = %(r)s and estado = 'active')
            + (select count(*) from pending_action p
                 join task_intake_request q on q.task_draft_id = p.draft_id
                where q.id = %(r)s and p.estado = 'esperando') n""",
                    {"r": rid})
        return cur.fetchone()["n"]


def _dejar_para_ver_otra_cosa(conn, monkeypatch, world, rid):
    """La persona escribe otra cosa con el alta abierta, y toca "Dejarlo y ver lo
    otro". Devuelve el cliente de los toques, lo que salió y el proveedor."""
    user = _usuario(world)
    provider = _RoutingProvider(
        [_ruta(RespectoPendiente.OTRO_TEMA),
         IntentRoute(IntentAction.NORMAL_CONVERSATION)],
        answer="Un bloqueo frena una tarea.")
    _escribir(conn, monkeypatch, world, provider, "¿qué es un bloqueo?")
    client = _callback_client(conn, monkeypatch)
    antes = _salidas(conn, user)
    assert _tocar_boton(client, conn, _token_de(conn, "Dejarlo"),
                        user).status_code == 200
    return client, _nuevas(conn, user, antes), provider


def test_dejarlo_con_una_eleccion_abierta_guarda_el_borrador_y_atiende_el_mensaje(
        intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)

    _, nuevas, _ = _dejar_para_ver_otra_cosa(conn, monkeypatch, intake_world, rid)

    assert _solicitud(conn, rid) == "active"             # no se perdió nada
    assert _pausado(conn, rid)
    assert _abiertas(conn, rid) == 0                     # ninguna rama abierta
    assert [f["cuerpo"] for f in nuevas] == [
        gateway.AVISO_ALTA_PAUSADA.format(titulo=f" «{TITULO}»"),
        "Un bloqueo frena una tarea."]
    assert "dejé de lado" not in nuevas[0]["cuerpo"]     # no se dice que se borró


def test_dejarlo_con_el_borrador_esperando_confirmacion_lo_guarda(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_en_confirmacion(conn, intake_world)

    _, nuevas, _ = _dejar_para_ver_otra_cosa(conn, monkeypatch, intake_world, rid)

    assert _solicitud(conn, rid) == "active" and _pausado(conn, rid)
    assert _abiertas(conn, rid) == 0
    with admin(conn) as cur:
        cur.execute("select count(*) n from task where titulo = %s", (TITULO,))
        assert cur.fetchone()["n"] == 0                  # y no se creó la tarea
    assert nuevas[0]["cuerpo"] == gateway.AVISO_ALTA_PAUSADA.format(
        titulo=f" «{TITULO}»")


def test_no_es_otra_cosa_del_dudoso_tambien_guarda_el_borrador(
        intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    user = _usuario(intake_world)
    provider = _RoutingProvider(
        [_ruta(RespectoPendiente.DUDOSO),
         IntentRoute(IntentAction.NORMAL_CONVERSATION)],
        answer="Un bloqueo frena una tarea.")
    _escribir(conn, monkeypatch, intake_world, provider, "¿qué es un bloqueo?")
    client = _callback_client(conn, monkeypatch)

    assert _tocar_boton(client, conn, _token_de(conn, "No, es otra cosa"),
                        user).status_code == 200

    assert _solicitud(conn, rid) == "active" and _pausado(conn, rid)
    assert _abiertas(conn, rid) == 0


def test_con_el_borrador_pausado_el_mensaje_siguiente_sigue_el_camino_normal(
        intake_world, conn, monkeypatch):
    """Un borrador pausado no es una rama abierta: no se traga lo que escribe la
    persona ("El borrador está esperando…") ni la deja sin respuesta."""
    rid = _alta_con_eleccion(conn, intake_world)
    _dejar_para_ver_otra_cosa(conn, monkeypatch, intake_world, rid)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([IntentRoute(IntentAction.NORMAL_CONVERSATION)],
                                answer="Hay dos tareas abiertas.")

    _escribir(conn, monkeypatch, intake_world, provider, "¿qué tengo pendiente?")

    assert provider.route_calls == ["¿qué tengo pendiente?"]
    assert provider.main_calls == 1
    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [
        "Hay dos tareas abiertas."]
    assert _solicitud(conn, rid) == "active"


def test_el_proximo_pedido_de_una_tarea_ofrece_continuar_el_borrador_guardado(
        intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    _dejar_para_ver_otra_cosa(conn, monkeypatch, intake_world, rid)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _RoutingProvider([IntentRoute(IntentAction.START_TASK_INTAKE)])

    _escribir(conn, monkeypatch, intake_world, provider, "quiero crear una tarea")

    nuevas = _nuevas(conn, user, antes)
    assert len(nuevas) == 1
    assert "Ya hay un borrador de tarea en curso" in nuevas[0]["cuerpo"]
    with admin(conn) as cur:
        cur.execute("""select o.etiqueta from task_intake_choice o
                         join task_intake_choice_set s on s.id = o.choice_set_id
                        where s.id = %s order by o.orden""",
                    (nuevas[0]["intake_choice_set_id"],))
        etiquetas = [f["etiqueta"] for f in cur.fetchall()]
    assert I.CONTINUAR_BORRADOR in etiquetas

    # Continuar retoma el borrador donde estaba, ya sin la marca de pausa.
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor = _actor(cur, intake_world)
        _choose(cur, actor, rid, "Continuar borrador", chat_id=user)
    conn.commit()
    assert _solicitud(conn, rid) == "active" and not _pausado(conn, rid)
    assert _conjunto_activo(conn, rid) is not None       # la elección, de nuevo


@pytest.mark.parametrize("texto", ["mejor dejalo", "no, cancelá todo"])
def test_el_cancelar_explicito_por_escrito_sigue_cancelando(
        texto, intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    provider = _RoutingProvider([_ruta(RespectoPendiente.CANCELA)])

    _escribir(conn, monkeypatch, intake_world, provider, texto)

    assert _solicitud(conn, rid) == "cancelled"


def test_pausar_sólo_actua_sobre_una_pregunta_abierta_de_quien_la_tiene(
        intake_world, conn):
    """`pause_from_intake_question` sólo actúa sobre la pregunta de quien la
    tiene abierta, como `cancel_from_intake_question`."""
    rid = _alta_con_eleccion(conn, intake_world)
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor = _actor(cur, intake_world)
        pregunta = I.open_intake_question(cur, actor, _usuario(intake_world))
        assert I.pause_from_intake_question(
            cur, actor, "choice", "00000000-0000-0000-0000-000000000000",
            NOW) is False
        assert I.pause_from_intake_question(
            cur, actor, pregunta["tipo"], pregunta["id"], NOW) is True
    conn.commit()
    assert _pausado(conn, rid)
