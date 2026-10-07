"""Las preguntas de Leda y un tema a la vez (`leda.motor.preguntas`; ADR 0018, 4 y 9d).

La primera prueba viene de `prueba_chica/test_preguntas_que_esperan.py`. Las demás fijan, con
un contexto mínimo del turno y sin las fichas (que llegan con la capa 2), las reglas que en la
prueba chica se probaban a través del turno: la pregunta abierta, las que quedan para después,
la espera de las que esperan respuesta, contestar, cerrar y las opciones con su token.
"""

from __future__ import annotations

from datetime import timedelta

from leda.db import admin, espacio
from leda.motor import preguntas

from tests.motor.ayudantes import AHORA, contexto, cuantas, todos

QUIEN_DESTRABA = "quien_destraba"


def test_cada_ficha_de_pregunta_dice_si_espera_respuesta():
    espera = {t.nombre: t.espera for t in preguntas.TIPOS.values()}
    assert espera[QUIEN_DESTRABA] == QUIEN_DESTRABA
    assert espera[preguntas.ESTADO_DE_LA_TAREA] == preguntas.ESTADO_DE_LA_TAREA
    # La fecha es parte del pedido de estado: espera con él.
    assert espera[preguntas.FECHA_DE_LA_TAREA] == preguntas.ESTADO_DE_LA_TAREA
    for se_deja in (preguntas.CUAL_TAREA, "causa_del_bloqueo", preguntas.PROPUESTA):
        assert espera[se_deja] is None


def test_el_token_de_un_toque_y_el_alias_de_una_opcion():
    assert preguntas.token_de(preguntas.callback("abc")) == "abc"
    assert preguntas.token_de("otra:cosa") is None
    assert preguntas.token_de(preguntas.PREFIJO_TOQUE) is None
    assert preguntas.alias_de_opcion(2) == "O2"
    assert preguntas.orden_de_alias(" o3 ") == 3
    assert preguntas.orden_de_alias("T1") is None


def _segunda_tarea(conn, mundo) -> str:
    with admin(conn) as cur:
        cur.execute("""insert into task (workspace_id, objective_id, titulo, area_id,
                                         responsable_membership_id, estado)
                       values (%s, %s, 'Cablear el tablero', %s, %s, 'asignada')
                       returning id""",
                    (mundo["id"], mundo["objetivo"], mundo["area"],
                     mundo["personas"]["Marcos"]["membership_id"]))
        return str(cur.fetchone()["id"])


def _tareas(mundo, otra):
    return [{"id": mundo["tarea"], "alias": "T1", "titulo": "Revisar el tablero"},
            {"id": otra, "alias": "T2", "titulo": "Cablear el tablero"}]


def test_la_primera_pregunta_queda_abierta_y_la_siguiente_del_mismo_mensaje_para_despues(
        conn, mundo):
    with espacio(conn, mundo["id"]) as cur:
        ctx = contexto(cur, mundo)
        assert preguntas.abrir(ctx, preguntas.CAUSA_DEL_BLOQUEO, mundo["tarea"],
                               jugada={"nombre": "registrar_bloqueo"}) is True
        assert preguntas.abrir(ctx, QUIEN_DESTRABA, mundo["tarea"],
                               jugada={"nombre": "quien_destraba"}) is False

        abierta = preguntas.actual(cur, ctx.quien.membership_id)
        despues = preguntas.para_despues(cur, ctx.quien.membership_id)
    assert abierta["tipo"] == preguntas.CAUSA_DEL_BLOQUEO
    assert [q["tipo"] for q in despues] == [QUIEN_DESTRABA]
    # Nadie puede no contestar lo que todavía no se le preguntó: sin espera todavía.
    assert cuantas(conn, "pending_reply") == 0


def test_una_pregunta_nueva_de_otro_mensaje_pasa_adelante(conn, mundo):
    with espacio(conn, mundo["id"]) as cur:
        primera = contexto(cur, mundo)
        preguntas.abrir(primera, preguntas.CAUSA_DEL_BLOQUEO, mundo["tarea"],
                        jugada={"nombre": "registrar_bloqueo"})
        segunda = contexto(cur, mundo, ahora=AHORA + timedelta(minutes=5))
        assert preguntas.abrir(segunda, preguntas.ESTADO_DE_LA_TAREA, mundo["tarea"],
                               jugada={"nombre": "pedido_de_estado"}) is True
        abierta = preguntas.actual(cur, segunda.quien.membership_id)
        despues = preguntas.para_despues(cur, segunda.quien.membership_id)

    assert abierta["tipo"] == preguntas.ESTADO_DE_LA_TAREA
    assert [q["tipo"] for q in despues] == [preguntas.CAUSA_DEL_BLOQUEO]
    # La pregunta que espera respuesta abre su espera, que vence al día hábil siguiente.
    [espera] = todos(conn, "select * from pending_reply")
    assert espera["tipo"] == preguntas.ESTADO_DE_LA_TAREA
    assert str(espera["task_id"]) == mundo["tarea"]
    assert espera["preguntado_en"] == AHORA + timedelta(minutes=5)
    assert espera["vence_en"] > espera["preguntado_en"]


def test_una_pregunta_igual_a_una_sin_cerrar_no_se_repite(conn, mundo):
    with espacio(conn, mundo["id"]) as cur:
        ctx = contexto(cur, mundo)
        jugada = {"nombre": "registrar_bloqueo"}
        _, una = preguntas.abrir_con_id(ctx, preguntas.CAUSA_DEL_BLOQUEO, mundo["tarea"],
                                        jugada=jugada)
        otro = contexto(cur, mundo, ahora=AHORA + timedelta(hours=1))
        _, otra = preguntas.abrir_con_id(otro, preguntas.CAUSA_DEL_BLOQUEO, mundo["tarea"],
                                         jugada={**jugada, "datos": {"causa": "x"}})
    assert una == otra
    assert cuantas(conn, "conversation_question") == 1


def test_contestar_cierra_y_al_terminar_vuelve_la_que_quedo_para_despues(conn, mundo):
    with espacio(conn, mundo["id"]) as cur:
        antes = contexto(cur, mundo)
        preguntas.abrir(antes, preguntas.CAUSA_DEL_BLOQUEO, mundo["tarea"],
                        jugada={"nombre": "registrar_bloqueo"})
        ahora = contexto(cur, mundo, ahora=AHORA + timedelta(minutes=5),
                         tareas=[{"id": mundo["tarea"], "alias": "T1",
                                  "titulo": "Revisar el tablero"}])
        preguntas.abrir(ahora, QUIEN_DESTRABA, mundo["tarea"],
                        jugada={"nombre": "quien_destraba"})
        preguntas.contestar(ahora, "quien_destraba", [QUIEN_DESTRABA], mundo["tarea"])
        pregunta = preguntas.al_terminar_el_turno(ahora)

    assert pregunta == {"tipo": preguntas.CAUSA_DEL_BLOQUEO,
                        "tarea": {"alias": "T1", "titulo": "Revisar el tablero"},
                        "desde_antes": True}
    [cerrada] = todos(conn, "select * from conversation_question where cerrada_en is not null")
    assert (cerrada["tipo"], cerrada["cierre"]) == (QUIEN_DESTRABA, "respondida")
    assert cerrada["cierre_detalle"] == {"jugada": "quien_destraba", "tarea": mundo["tarea"]}


def test_una_duda_ofrece_las_tareas_como_opciones_con_su_token(conn, mundo):
    otra = _segunda_tarea(conn, mundo)
    tareas = _tareas(mundo, otra)
    with espacio(conn, mundo["id"]) as cur:
        ctx = contexto(cur, mundo, tareas=tareas)
        preguntas.abrir(ctx, preguntas.CUAL_TAREA, None, jugada={"nombre": "iniciar_tarea"},
                        opciones_de_tareas=tareas)
        para_la_ia = preguntas.estado_para_la_ia(cur, ctx.quien.membership_id, tareas)
        abierta = preguntas.actual(cur, ctx.quien.membership_id)
        [o1, o2] = preguntas.opciones(cur, abierta["id"])
        tocada = preguntas.opcion_por_token(cur, o2["token"])

    assert para_la_ia == {"pregunta_abierta": {
        "tipo": preguntas.CUAL_TAREA, "tarea": None,
        "opciones": [{"opcion": "O1", "etiqueta": "Revisar el tablero", "tarea": "T1"},
                     {"opcion": "O2", "etiqueta": "Cablear el tablero", "tarea": "T2"}]},
        "para_despues": []}
    assert (o1["orden"], o2["orden"]) == (1, 2) and o1["token"] != o2["token"]
    assert str(tocada["question_id"]) == str(abierta["id"])
    assert tocada["valor"] == {"tarea": otra}

    # Elegir la tarea con la jugada que la duda esperaba la contesta.
    with espacio(conn, mundo["id"]) as cur:
        ctx = contexto(cur, mundo, tareas=tareas)
        preguntas.contestar(ctx, "iniciar_tarea", [], otra)
        assert preguntas.actual(cur, ctx.quien.membership_id) is None


def test_un_toque_viejo_sabe_con_que_se_cerro_la_pregunta(conn, mundo):
    with espacio(conn, mundo["id"]) as cur:
        ctx = contexto(cur, mundo, tareas=[{"id": mundo["tarea"], "alias": "T1",
                                            "titulo": "Revisar el tablero"}])
        _, pregunta = preguntas.abrir_con_id(ctx, preguntas.CAUSA_DEL_BLOQUEO, mundo["tarea"],
                                             jugada={"nombre": "registrar_bloqueo"})
        preguntas.cerrar(ctx, pregunta, "cancelada", {"tarea": mundo["tarea"]})
        dicho = preguntas.con_que_se_cerro(ctx, pregunta)
        assert preguntas.actual(cur, ctx.quien.membership_id) is None

    assert dicho == {"cierre": "cancelada", "cuando": "2026-10-05",
                     "tarea": {"alias": "T1", "titulo": "Revisar el tablero"}}


def test_lo_que_leda_propone_lo_contesta_hacer_una_de_las_cosas_propuestas(conn, mundo):
    with espacio(conn, mundo["id"]) as cur:
        ctx = contexto(cur, mundo)
        preguntas.abrir(ctx, preguntas.PROPUESTA, mundo["tarea"],
                        jugada={"nombre": "registrar_bloqueo",
                                "propone": ["informar_prevision", "destrabar"]})
        descrita = preguntas.describir(ctx, preguntas.actual(cur, ctx.quien.membership_id))
        preguntas.contestar(ctx, "destrabar", [], mundo["tarea"])
        assert preguntas.actual(cur, ctx.quien.membership_id) is None

    assert descrita["propone"] == ["informar_prevision", "destrabar"]


def test_dejar_para_despues_no_vuelve_en_el_mismo_mensaje(conn, mundo):
    with espacio(conn, mundo["id"]) as cur:
        ctx = contexto(cur, mundo)
        _, pregunta = preguntas.abrir_con_id(ctx, preguntas.CAUSA_DEL_BLOQUEO, mundo["tarea"],
                                             jugada={"nombre": "registrar_bloqueo"})
        preguntas.dejar_para_despues(ctx, pregunta)
        assert preguntas.al_terminar_el_turno(ctx) is None

        siguiente = contexto(cur, mundo, ahora=AHORA + timedelta(hours=1))
        vuelve = preguntas.al_terminar_el_turno(siguiente)
    assert vuelve["tipo"] == preguntas.CAUSA_DEL_BLOQUEO and vuelve["desde_antes"] is True
