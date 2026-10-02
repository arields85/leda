"""F-B8: lo que un mensaje propone queda ligado a la tarea que ese mensaje pedía.
Cuando la persona responde "¿qué hay que hacer?" con un mensaje que es en sí un
pedido de tarea nueva, esa tarea es otra: lo que propuso otro mensaje (el que se
dejó de lado para ver otra cosa, "para Nahuel") y nadie confirmó no sobrevive. Lo
que la persona ya confirmó para esta alta, sí; y lo que propone el mensaje nuevo,
también."""

from __future__ import annotations

from leda import ingreso_tareas as I
from leda.db import admin, espacio
from leda.llm import IntentAction, IntentRoute, RespectoPendiente

from tests.test_alta_guiada_flujo import (_empezar, _escribir, _estado, _salidas,
                                          _slot, _usuario)
from tests.test_task_intake import _RoutingProvider

TITULO_NUEVO = "calibrar los sensores de la línea 2"
PARA_OTRO = "Sam North 1"


def _alta_sin_titulo_para_otro(conn, world):
    """Lo que deja atender un mensaje dejado de lado, "otra tarea para Sam": una
    alta sin título, con el responsable propuesto por ese mensaje."""
    user = _usuario(world)
    with espacio(conn, world["north-lab"]["id"]) as cur:
        _, outcome = _empezar(cur, world, chat=user, responsible=PARA_OTRO)
        rid = outcome.request_id
        assert _slot(cur, rid) == "title"
    conn.commit()
    assert _estado(conn, rid, "responsible")["estado"] == "proposed"
    return user, rid


def _responde_el_titulo(accion, task=None):
    return IntentRoute(accion, task=task or {},
                       respecto_pendiente=RespectoPendiente.RESPONDE,
                       valor={"texto": TITULO_NUEVO})


def test_un_titulo_que_es_otro_pedido_de_tarea_no_hereda_lo_propuesto_por_otro_mensaje(
        intake_world, conn, monkeypatch):
    user, rid = _alta_sin_titulo_para_otro(conn, intake_world)
    provider = _RoutingProvider([_responde_el_titulo(
        IntentAction.START_TASK_INTAKE, {"title": TITULO_NUEVO})])

    _escribir(conn, monkeypatch, intake_world, provider,
              f"necesito crear una tarea: {TITULO_NUEVO}")

    assert _estado(conn, rid, "title")["valor"] == TITULO_NUEVO
    responsable = _estado(conn, rid, "responsible")
    assert responsable["estado"] == "missing" and responsable["valor"] is None
    # Nada de «Sam North 1» en lo que se le dijo después.
    cuerpos = " ".join(f["cuerpo"] for f in _salidas(conn, user))
    assert PARA_OTRO not in cuerpos.split("¿Qué hay que hacer?")[-1]


def test_un_titulo_que_no_pide_otra_tarea_conserva_lo_propuesto(
        intake_world, conn, monkeypatch):
    """"para Sam" y después "calibrar los sensores" es UNA tarea: la propuesta
    sigue ligada a ella."""
    _, rid = _alta_sin_titulo_para_otro(conn, intake_world)
    provider = _RoutingProvider([_responde_el_titulo(
        IntentAction.NORMAL_CONVERSATION)])

    _escribir(conn, monkeypatch, intake_world, provider, TITULO_NUEVO)

    assert _estado(conn, rid, "title")["valor"] == TITULO_NUEVO
    responsable = _estado(conn, rid, "responsible")
    assert responsable["estado"] == "proposed" and responsable["valor"] == PARA_OTRO


def test_lo_que_propone_el_mensaje_nuevo_queda_ligado_a_la_tarea_nueva(
        intake_world, conn, monkeypatch):
    _, rid = _alta_sin_titulo_para_otro(conn, intake_world)
    provider = _RoutingProvider([_responde_el_titulo(
        IntentAction.START_TASK_INTAKE,
        {"title": TITULO_NUEVO, "responsible": "Sam Noble 1"})])

    _escribir(conn, monkeypatch, intake_world, provider,
              f"necesito crear una tarea para Sam Noble: {TITULO_NUEVO}")

    responsable = _estado(conn, rid, "responsible")
    assert responsable["estado"] == "proposed"
    assert responsable["valor"] == "Sam Noble 1"
    with admin(conn) as cur:
        cur.execute(
            """select i.texto from task_intake_field f
                 join inbound_message i on i.id = f.source_inbound_id
                where f.request_id = %s and f.campo = 'responsible'""", (rid,))
        assert "Sam Noble" in cur.fetchone()["texto"]


def test_lo_que_la_persona_ya_confirmo_para_esta_alta_no_se_toca(
        intake_world, conn, monkeypatch):
    """Sólo caen las propuestas sin confirmar de otro mensaje: un dato confirmado
    (acá la descripción, que el alta completa sola) queda como está."""
    _, rid = _alta_sin_titulo_para_otro(conn, intake_world)
    with admin(conn) as cur:
        cur.execute(
            """update task_intake_field set estado = 'confirmed', valor = to_jsonb(%s::text),
                      proposed_by = 'user' where request_id = %s and campo = 'description'""",
            ("Detalle ya confirmado", rid))
    conn.commit()
    provider = _RoutingProvider([_responde_el_titulo(
        IntentAction.START_TASK_INTAKE, {"title": TITULO_NUEVO})])

    _escribir(conn, monkeypatch, intake_world, provider,
              f"necesito crear una tarea: {TITULO_NUEVO}")

    assert _estado(conn, rid, "description")["valor"] == "Detalle ya confirmado"
    assert _estado(conn, rid, "responsible")["estado"] == "missing"
