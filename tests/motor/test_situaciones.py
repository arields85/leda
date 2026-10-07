"""Las situaciones generales, una vez para todas las fichas (`leda.motor.situaciones`; E2-4).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Las ocho situaciones, una vez"); ADR 0018,
decisiones 4, 9d y 9f; conversaciones 05 a 11 de `tests/conversaciones/`, al nivel de jugadas,
efectos en la base, preguntas y opciones, y hechos que recibe la redacción (no el texto). Los
toques y los botones, en `test_toques.py`. La IA es guionada y el reloj, fijo: el lunes 5 de
octubre de 2026, 10:00 en Buenos Aires. Marcos tiene dos tareas: "Revisar el tablero" (T1,
vence el viernes 9) y "Probar las comunicaciones" (T2, vence el viernes 16).
"""

from __future__ import annotations

from datetime import datetime, timezone

from leda.db import admin
from leda.motor.ia import Jugada

from tests.motor.ayudantes import (AHORA, T1, T2, cuantas, estado_de, jugada_bloqueo, nueva_tarea,
                                   poner_estado, abierta, todos, uno)

# --- Ayudas ---------------------------------------------------------------------------------

def _para_despues(conn) -> list[tuple[str, str | None]]:
    return [(f["tipo"], str(f["task_id"]) if f["task_id"] else None) for f in todos(
        conn, """select tipo, task_id from conversation_question
                  where cerrada_en is null and para_despues_en is not null
                  order by abierta_en""")]


# --- Situación 2: varias cosas en un mensaje (conversación 05) -----------------------------------

def test_varias_cosas_directas_se_anotan_todas_en_una_respuesta(conn, tareas, marcos):
    r = marcos.dice(Jugada("anotar_inicio", {"tarea": "T1"}),
                    Jugada("anotar_prevision", {"tarea": "T2", "fecha": "2026-10-21",
                                                "motivo": "espera el switch nuevo"}))

    assert [(h["jugada"], h["resultado"], h["tarea"]) for h in r.hechos] == [
        ("anotar_inicio", "anotado", T1), ("anotar_prevision", "anotado", T2)]
    assert estado_de(conn, tareas["T1"]) == "en_curso"
    assert cuantas(conn, "task_forecast", "task_id = %s", tareas["T2"]) == 1
    assert cuantas(conn, "scheduled_notice") == 1          # sólo el de la previsión
    assert cuantas(conn, "message_outbox") == 1            # una sola respuesta
    assert r.pregunta is None and marcos.redaccion["pregunta"] is None
    assert cuantas(conn, "conversation_question") == 0


def test_de_varias_cosas_se_anota_lo_directo_y_se_pregunta_una(conn, tareas, marcos):
    r = marcos.dice(jugada_bloqueo("T1"),
                    Jugada("anotar_prevision", {"tarea": "T2", "fecha": "2026-10-22"}))

    bloqueo, prevision = r.hechos
    assert prevision["resultado"] == "anotado"
    assert bloqueo == {"jugada": "anotar_bloqueo", "resultado": "falta_dato",
                       "falta": ["causa"], "tarea": T1, "pregunta": "causa_del_bloqueo"}
    assert r.pregunta == {"tipo": "causa_del_bloqueo", "tarea": T1, "desde_antes": False}
    assert marcos.redaccion["pregunta"] == r.pregunta
    assert cuantas(conn, "blocker") == 0
    assert abierta(conn) == ("causa_del_bloqueo", tareas["T1"]) and _para_despues(conn) == []


def test_la_causa_y_quien_destraba_en_un_mensaje_cierran_las_dos_preguntas(conn, tareas, marcos):
    marcos.dice(jugada_bloqueo("T1"))

    r = marcos.dice(jugada_bloqueo("T1", "falta que me habiliten el acceso a la red"),
                    Jugada("anotar_quien_destraba", {"quien": "martin de IT"}))

    assert [h["resultado"] for h in r.hechos] == ["anotado", "anotado"]
    assert r.hechos[1]["quien_destraba"] == {"externo": "martin de IT"}
    assert "salidas" not in r.hechos[1]             # hay otra persona que lo destraba (9c)
    assert estado_de(conn, tareas["T1"]) == "bloqueada"
    assert [q["cierre"] for q in todos(
        conn, "select cierre from conversation_question order by abierta_en")] == [
        "respondida", "respondida"]
    assert r.pregunta is None and abierta(conn) is None and _para_despues(conn) == []


def test_dos_cosas_que_preguntan_van_de_a_una_en_el_orden_dicho(conn, tareas, marcos):
    r = marcos.dice(jugada_bloqueo("T1"), jugada_bloqueo("T2"))
    assert r.hechos[0]["pregunta"] == "causa_del_bloqueo"
    assert r.hechos[1]["pregunta_para_despues"] == "causa_del_bloqueo"
    assert "pregunta" not in r.hechos[1]
    assert r.pregunta == {"tipo": "causa_del_bloqueo", "tarea": T1, "desde_antes": False}
    assert _para_despues(conn) == [("causa_del_bloqueo", tareas["T2"])]

    r = marcos.dice(jugada_bloqueo("T1", "no llegó el programa"))
    assert r.pregunta == {"tipo": "quien_destraba", "tarea": T1, "desde_antes": False}
    assert _para_despues(conn) == [("causa_del_bloqueo", tareas["T2"])]

    # Con alguien que lo destraba no hay salidas que propone (que serían el tema nuevo).
    r = marcos.dice(Jugada("anotar_quien_destraba", {"quien": "el de compras"}))
    # Cerrada la de T1, vuelve la que quedó para después: retomarla (9d).
    assert r.pregunta == {"tipo": "causa_del_bloqueo", "tarea": T2, "desde_antes": True}
    assert abierta(conn) == ("causa_del_bloqueo", tareas["T2"]) and _para_despues(conn) == []


# --- Situación 1: cambio de tema (conversación 08) ----------------------------------------------

def test_un_cambio_de_tema_se_anota_y_vuelve_a_la_pregunta_pendiente(conn, tareas, marcos):
    marcos.dice(jugada_bloqueo("T1"))

    r = marcos.dice(Jugada("anotar_prevision", {"tarea": "T2", "fecha": "2026-10-21"}))

    assert [(h["jugada"], h["resultado"]) for h in r.hechos] == [("anotar_prevision", "anotado")]
    assert r.pregunta == {"tipo": "causa_del_bloqueo", "tarea": T1, "desde_antes": True}
    assert abierta(conn) == ("causa_del_bloqueo", tareas["T1"]) and _para_despues(conn) == []
    assert cuantas(conn, "blocker") == 0 and cuantas(conn, "conversation_question") == 1

    r = marcos.dice(jugada_bloqueo("T1", "no me mandaron el programa del fabricante"))
    assert r.hechos[0]["resultado"] == "anotado" and estado_de(conn, tareas["T1"]) == "bloqueada"
    assert r.pregunta == {"tipo": "quien_destraba", "tarea": T1, "desde_antes": False}


def test_si_lo_nuevo_tambien_pregunta_leda_sigue_a_la_persona(conn, tareas, marcos):
    marcos.dice(jugada_bloqueo("T1"))

    r = marcos.dice(jugada_bloqueo("T2"))
    assert r.pregunta == {"tipo": "causa_del_bloqueo", "tarea": T2, "desde_antes": False}
    assert _para_despues(conn) == [("causa_del_bloqueo", tareas["T1"])]

    r = marcos.dice(jugada_bloqueo("T2", "falta el cable"),
                    Jugada("anotar_quien_destraba", {"tarea": "T2", "quien": "el de compras"}))
    # Cerrado lo nuevo, Leda vuelve a la pendiente.
    assert r.pregunta == {"tipo": "causa_del_bloqueo", "tarea": T1, "desde_antes": True}
    assert abierta(conn) == ("causa_del_bloqueo", tareas["T1"]) and _para_despues(conn) == []


def test_la_ia_recibe_la_pregunta_abierta_y_las_que_quedaron_para_despues(conn, tareas, marcos):
    marcos.dice(jugada_bloqueo("T1"))
    marcos.dice(jugada_bloqueo("T2"))

    marcos.dice()

    assert marcos.situacion["estado"] == {
        "pregunta_abierta": {"tipo": "causa_del_bloqueo", "tarea": "T2"},
        "para_despues": [{"tipo": "causa_del_bloqueo", "tarea": "T1"}]}


def test_dejar_para_despues_no_la_cierra_y_vuelve_en_un_mensaje_siguiente(conn, tareas, marcos):
    marcos.dice(jugada_bloqueo("T1"))

    r = marcos.dice(Jugada("dejar_para_despues"))
    assert r.hechos == [{"jugada": "dejar_para_despues", "resultado": "para_despues",
                         "pregunta": {"tipo": "causa_del_bloqueo", "tarea": T1}}]
    assert r.pregunta is None
    assert abierta(conn) is None and _para_despues(conn) == [("causa_del_bloqueo", tareas["T1"])]
    assert cuantas(conn, "conversation_question", "cerrada_en is not null") == 0

    r = marcos.dice()
    assert r.pregunta == {"tipo": "causa_del_bloqueo", "tarea": T1, "desde_antes": True}


def test_dejar_para_despues_sin_pregunta_abierta_no_hace_nada(conn, tareas, marcos):
    r = marcos.dice(Jugada("dejar_para_despues"))
    assert r.hechos == [{"jugada": "dejar_para_despues", "resultado": "no_se_puede",
                         "motivo": "sin_pregunta_abierta"}]


# --- Situación 4: cancelar (conversación 07) --------------------------------------------------

def test_cancelar_deja_sin_efecto_la_pregunta_y_no_insiste(conn, tareas, marcos):
    poner_estado(conn, tareas["T1"], "en_curso")
    marcos.dice(jugada_bloqueo("T1"))

    r = marcos.dice(Jugada("cancelar"), texto="dejá, no importa")

    assert r.hechos == [{"jugada": "cancelar", "resultado": "cancelado",
                         "pregunta": {"tipo": "causa_del_bloqueo", "tarea": T1},
                         "no_se_anoto_nada": True}]
    pregunta = uno(conn, "select cierre, cerrada_en, cierre_detalle from conversation_question")
    assert pregunta["cierre"] == "cancelada" and pregunta["cerrada_en"] == AHORA
    assert cuantas(conn, "blocker") == 0 and estado_de(conn, tareas["T1"]) == "en_curso"
    assert r.pregunta is None and abierta(conn) is None and _para_despues(conn) == []

    assert marcos.dice().pregunta is None           # no vuelve a preguntar (9b)


def test_la_pregunta_de_quien_destraba_no_se_cancela(conn, tareas, marcos):
    marcos.dice(jugada_bloqueo("T1", "falta el repuesto"))

    r = marcos.dice(Jugada("cancelar"))

    assert r.hechos == [{"jugada": "cancelar", "resultado": "no_se_puede",
                         "motivo": "la_pregunta_espera_respuesta",
                         "pregunta": {"tipo": "quien_destraba", "tarea": T1}}]
    assert abierta(conn) == ("quien_destraba", tareas["T1"])
    assert r.pregunta == {"tipo": "quien_destraba", "tarea": T1, "desde_antes": True}


def test_cancelar_sin_pregunta_abierta_no_hace_nada(conn, tareas, marcos):
    r = marcos.dice(Jugada("cancelar"))
    assert r.hechos == [{"jugada": "cancelar", "resultado": "no_se_puede",
                         "motivo": "sin_pregunta_abierta"}]


# --- Situación 5: duda (conversación 09) ------------------------------------------------------

def test_una_duda_pregunta_con_las_tareas_posibles_como_opciones(conn, mundo, tareas, marcos):
    nueva_tarea(conn, mundo, "Medir la planta", estado="en_curso",      # no se puede arrancar
                fecha=datetime(2026, 10, 23, 20, 0, tzinfo=timezone.utc))

    r = marcos.dice(Jugada("anotar_inicio", {}), texto="hoy arranque")

    assert r.hechos == [{"jugada": "anotar_inicio", "resultado": "falta_dato",
                         "falta": ["tarea"], "pregunta": "cual_tarea"}]
    assert r.pregunta == {"tipo": "cual_tarea", "desde_antes": False, "opciones": [
        {"opcion": "O1", "etiqueta": T1["titulo"], "tarea": T1},
        {"opcion": "O2", "etiqueta": T2["titulo"], "tarea": T2}]}
    opciones = todos(conn, "select token, etiqueta, valor, orden, elegida_en "
                            "from conversation_option order by orden")
    assert [(o["orden"], o["valor"]) for o in opciones] == [
        (1, {"tarea": tareas["T1"]}), (2, {"tarea": tareas["T2"]})]
    assert len({o["token"] for o in opciones}) == 2 and all(o["token"] for o in opciones)
    assert cuantas(conn, "task_state_event") == 0
    assert abierta(conn) == ("cual_tarea", None)
    # El registro del turno guarda la pregunta que se hizo.
    entrada = uno(conn, "select resultado from conversation_turn where sentido = 'entrada'")
    assert entrada["resultado"]["pregunta"] == r.pregunta

    marcos.dice()
    assert marcos.situacion["estado"]["pregunta_abierta"] == {
        "tipo": "cual_tarea", "tarea": None, "opciones": [
            {"opcion": "O1", "etiqueta": T1["titulo"], "tarea": "T1"},
            {"opcion": "O2", "etiqueta": T2["titulo"], "tarea": "T2"}]}


def test_sin_ninguna_tarea_posible_lo_dice_sin_preguntar(conn, tareas, marcos):
    poner_estado(conn, tareas["T1"], "en_curso")
    poner_estado(conn, tareas["T2"], "en_curso")

    r = marcos.dice(Jugada("anotar_inicio", {}))

    assert r.hechos == [{"jugada": "anotar_inicio", "resultado": "no_se_puede",
                         "motivo": "ninguna_tarea_posible"}]
    assert cuantas(conn, "conversation_question") == 0 and r.pregunta is None


# --- Situación 6: escribir en lugar de tocar (conversación 10) -------------------------------

def test_elegir_escribiendo_completa_la_jugada_que_esperaba(conn, tareas, marcos):
    marcos.dice(Jugada("anotar_inicio", {}))

    r = marcos.dice(Jugada("elegir", {"opcion": "O1"}), texto="la del tablero")

    assert r.hechos == [{"jugada": "anotar_inicio", "resultado": "anotado",
                         "estado": "en_curso", "tarea": T1,
                         "eligio": {"opcion": "O1", "etiqueta": T1["titulo"], "tarea": T1},
                         "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-09"}}}]
    assert estado_de(conn, tareas["T1"]) == "en_curso"
    assert estado_de(conn, tareas["T2"]) == "asignada"
    pregunta = uno(conn, "select cierre, cierre_detalle from conversation_question")
    opcion = uno(conn, "select id from conversation_option where orden = 1")
    assert pregunta["cierre"] == "respondida"
    assert pregunta["cierre_detalle"] == {"opcion": str(opcion["id"]), "tarea": tareas["T1"]}
    assert uno(conn, "select elegida_en from conversation_option where orden = 1")[
        "elegida_en"] == AHORA
    assert r.pregunta is None and abierta(conn) is None


def test_contestar_la_duda_nombrando_la_tarea_tambien_la_cierra(conn, tareas, marcos):
    marcos.dice(Jugada("anotar_inicio", {}))

    r = marcos.dice(Jugada("anotar_inicio", {"tarea": "T2"}))

    assert r.hechos[0]["resultado"] == "anotado" and estado_de(conn, tareas["T2"]) == "en_curso"
    pregunta = uno(conn, "select cierre, cierre_detalle from conversation_question")
    assert pregunta["cierre"] == "respondida"
    assert pregunta["cierre_detalle"] == {"jugada": "anotar_inicio", "tarea": tareas["T2"]}
    assert r.pregunta is None


def test_la_jugada_que_espera_una_eleccion_conserva_sus_datos(conn, tareas, marcos):
    r = marcos.dice(Jugada("anotar_prevision", {"fecha": "2026-10-21",
                                                "motivo": "espera el switch"}))
    assert r.hechos[0]["pregunta"] == "cual_tarea"

    r = marcos.dice(Jugada("elegir", {"opcion": "O2"}))

    assert r.hechos[0]["jugada"] == "anotar_prevision" and r.hechos[0]["resultado"] == "anotado"
    prevision = uno(conn, "select task_id, fecha_prevista, motivo from task_forecast")
    assert str(prevision["task_id"]) == tareas["T2"]
    assert (prevision["fecha_prevista"].isoformat(), prevision["motivo"]) == (
        "2026-10-21", "espera el switch")


def test_una_opcion_que_no_es_de_la_pregunta_abierta_es_un_dato_que_falta(conn, tareas, marcos):
    marcos.dice(Jugada("anotar_inicio", {}))

    r = marcos.dice(Jugada("elegir", {"opcion": "O9"}))

    assert r.hechos == [{"jugada": "elegir", "resultado": "falta_dato", "falta": ["opcion"]}]
    assert abierta(conn) == ("cual_tarea", None)
    assert r.pregunta["tipo"] == "cual_tarea" and r.pregunta["desde_antes"] is True


def test_una_opcion_que_ya_no_se_puede_usar_deja_la_duda_abierta(conn, tareas, marcos):
    """Revisión de la E2-4: elegir no cierra la duda antes de que la ficha diga si se pudo. Si
    la opción elegida ya no sirve (la tarea cambió de estado entre la pregunta y la
    respuesta), la duda sigue abierta con sus opciones y la opción no queda elegida."""
    marcos.dice(Jugada("anotar_inicio", {}))
    poner_estado(conn, tareas["T1"], "en_curso")

    r = marcos.dice(Jugada("elegir", {"opcion": "O1"}))

    assert r.hechos == [{"jugada": "anotar_inicio", "resultado": "no_se_puede",
                         "motivo": "estado", "tarea": T1, "estado": "en_curso",
                         "estado_desde": "desconocido",
                         "eligio": {"opcion": "O1", "etiqueta": T1["titulo"], "tarea": T1},
                         "pregunta_sigue_abierta": True}]
    assert abierta(conn) == ("cual_tarea", None)
    assert cuantas(conn, "conversation_option", "elegida_en is not null") == 0
    assert r.pregunta["tipo"] == "cual_tarea" and r.pregunta["desde_antes"] is True

    r = marcos.dice(Jugada("elegir", {"opcion": "O2"}))         # la otra sí sirve
    assert r.hechos[0]["resultado"] == "anotado" and abierta(conn) is None


def test_una_opcion_elegida_a_la_que_le_falta_un_dato_cierra_la_duda_y_lo_dice(conn, tareas,
                                                                              marcos):
    """La tarea quedó elegida: la duda se contesta, y lo que falta es la pregunta siguiente
    (la causa de un bloqueo), dicha en los hechos."""
    marcos.dice(Jugada("anotar_bloqueo", {}))

    r = marcos.dice(Jugada("elegir", {"opcion": "O2"}))

    assert r.hechos[0]["resultado"] == "falta_dato" and r.hechos[0]["falta"] == ["causa"]
    assert r.hechos[0]["eligio"]["tarea"] == T2
    assert abierta(conn) == ("causa_del_bloqueo", tareas["T2"])
    assert uno(conn, "select cierre from conversation_question where tipo = 'cual_tarea'")[
        "cierre"] == "respondida"


# --- Situación 7: algo vencido, escrito (conversación 11) -----------------------------------

def test_elegir_de_una_pregunta_cerrada_no_hace_nada_y_dice_con_que_se_cerro(conn, tareas,
                                                                            marcos):
    marcos.dice(Jugada("anotar_inicio", {}))
    marcos.dice(Jugada("elegir", {"opcion": "O1"}))

    r = marcos.dice(Jugada("elegir", {"opcion": "O2"}))

    assert r.hechos == [{"jugada": "elegir", "resultado": "sin_efecto",
                         "motivo": "pregunta_cerrada",
                         "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-05",
                                         "tarea": T1}}]
    assert estado_de(conn, tareas["T2"]) == "asignada"


# --- Situación 3: corrección (conversación 06; 9f) ------------------------------------------

def test_corregir_un_inicio_lo_devuelve_y_lo_anota_en_la_correcta(conn, mundo, tareas, marcos):
    marcos.dice(Jugada("anotar_inicio", {"tarea": "T1"}))

    r = marcos.dice(Jugada("corregir", {"corrige": "anotar_inicio", "tarea": "T1",
                                        "tarea_correcta": "T2"}),
                    texto="nono era la otra")

    [hecho] = r.hechos
    assert {k: v for k, v in hecho.items() if k != "aplicado"} == {
        "jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio",
        "tarea": T1, "vuelve_a": {"estado": "asignada"}}
    assert hecho["aplicado"] == {"jugada": "anotar_inicio", "resultado": "anotado",
                                 "estado": "en_curso", "tarea": T2}
    assert estado_de(conn, tareas["T1"]) == "asignada"
    assert estado_de(conn, tareas["T2"]) == "en_curso"
    # Nada se borra: los tres hechos en la historia, de Marcos.
    eventos = todos(conn, """select task_id, estado_anterior::text a, estado_nuevo::text n,
                                     actor_app_user_id from task_state_event order by at, id""")
    assert sorted((str(e["task_id"]), e["a"], e["n"]) for e in eventos) == sorted([
        (tareas["T1"], "asignada", "en_curso"), (tareas["T1"], "en_curso", "asignada"),
        (tareas["T2"], "asignada", "en_curso")])
    assert {str(e["actor_app_user_id"]) for e in eventos} == {
        mundo["personas"]["Marcos"]["app_user_id"]}


def test_corregir_algo_que_no_paso_solo_lo_devuelve(conn, tareas, marcos):
    marcos.dice(Jugada("anotar_inicio", {"tarea": "T1"}))

    r = marcos.dice(Jugada("corregir", {"corrige": "anotar_inicio", "tarea": "T1"}))

    assert r.hechos[0]["resultado"] == "corregido" and "aplicado" not in r.hechos[0]
    assert estado_de(conn, tareas["T1"]) == "asignada"
    assert estado_de(conn, tareas["T2"]) == "asignada"


def test_corregir_una_prevision_retira_su_aviso_y_la_anota_en_la_correcta(conn, tareas, marcos):
    marcos.dice(Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-21",
                                            "motivo": "espera el switch"}))

    r = marcos.dice(Jugada("corregir", {"corrige": "anotar_prevision", "tarea": "T1",
                                        "tarea_correcta": "T2"}))

    [hecho] = r.hechos
    assert hecho["resultado"] == "corregido"
    assert hecho["vuelve_a"] == {"fecha_comprometida": "2026-10-09"}
    assert hecho["prevision_corregida"] == "2026-10-21"
    assert hecho["aviso_de_la_prevision_corregida"] == {"a": "Ismael",
                                                        "llega": "no_le_va_a_llegar"}
    assert hecho["aplicado"]["resultado"] == "anotado" and hecho["aplicado"]["tarea"] == T2
    equivocada, correccion = todos(
        conn, """select id, fecha_prevista, es_correccion, reemplaza_id, atraso_dias_habiles
                   from task_forecast where task_id = %s order by es_correccion""",
        tareas["T1"])
    assert correccion["es_correccion"] and correccion["reemplaza_id"] == equivocada["id"]
    assert correccion["fecha_prevista"].isoformat() == "2026-10-09"
    assert correccion["atraso_dias_habiles"] == 0
    correcta = uno(conn, "select fecha_prevista, motivo from task_forecast where task_id = %s",
                   tareas["T2"])
    assert (correcta["fecha_prevista"].isoformat(), correcta["motivo"]) == (
        "2026-10-21", "espera el switch")
    avisos = {str(a["task_id"]): a for a in todos(
        conn, "select task_id, estado, motivo_omision from scheduled_notice")}
    assert avisos[tareas["T1"]]["estado"] == "omitido"
    assert avisos[tareas["T1"]]["motivo_omision"] == "prevision_corregida"
    assert avisos[tareas["T2"]]["estado"] == "guardado"


def test_corregir_una_prevision_cuyo_aviso_ya_salio_guarda_una_correccion(conn, mundo, tareas,
                                                                         marcos):
    marcos.dice(Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-21"}))
    with admin(conn) as cur:
        cur.execute("update scheduled_notice set estado = 'enviado', resuelto_en = %s",
                    (AHORA,))
    conn.commit()

    r = marcos.dice(Jugada("corregir", {"corrige": "anotar_prevision", "tarea": "T1"}))

    assert r.hechos[0]["correccion_al_referente"]["a"] == "Ismael"
    assert set(r.hechos[0]["correccion_al_referente"]) == {"a", "llega"}
    aviso = uno(conn, """select destinatario_membership_id, hechos, estado
                            from scheduled_notice where tipo = 'correccion_de_prevision'""")
    assert str(aviso["destinatario_membership_id"]) == \
        mundo["personas"]["Ismael"]["membership_id"]
    assert aviso["estado"] == "guardado"
    assert aviso["hechos"]["prevision_que_no_vale"] == "2026-10-21"
    assert aviso["hechos"]["fecha_comprometida"] == "2026-10-09"


def test_corregir_un_bloqueo_lo_resuelve_y_lo_anota_en_la_correcta(conn, tareas, marcos):
    marcos.dice(jugada_bloqueo("T1", "falta el repuesto"))
    assert estado_de(conn, tareas["T1"]) == "bloqueada"

    r = marcos.dice(Jugada("corregir", {"corrige": "anotar_bloqueo", "tarea": "T1",
                                        "tarea_correcta": "T2"}))

    assert r.hechos[0]["vuelve_a"] == {"estado": "asignada"}
    assert r.hechos[0]["aplicado"]["causa"] == "falta el repuesto"
    assert estado_de(conn, tareas["T1"]) == "asignada"
    assert estado_de(conn, tareas["T2"]) == "bloqueada"
    viejo = uno(conn, "select resuelto_en, resolucion from blocker where task_id = %s",
                tareas["T1"])
    assert viejo["resuelto_en"] is not None and viejo["resolucion"].startswith("corrección")
    # La pregunta sobre el bloqueo equivocado se cierra sin efecto; la del correcto, abierta.
    cerrada = uno(conn, """select cierre from conversation_question
                             where task_id = %s""", tareas["T1"])
    assert cerrada["cierre"] == "sin_efecto"
    assert r.pregunta == {"tipo": "quien_destraba", "tarea": T2, "desde_antes": False}


def test_no_se_corrige_lo_que_no_se_anoto(conn, tareas, marcos):
    poner_estado(conn, tareas["T1"], "en_curso")

    r = marcos.dice(Jugada("corregir", {"corrige": "anotar_inicio", "tarea": "T1",
                                        "tarea_correcta": "T2"}))

    assert r.hechos == [{"jugada": "corregir", "resultado": "no_se_puede",
                         "motivo": "nada_que_corregir", "corrige": "anotar_inicio",
                         "tarea": T1}]
    assert estado_de(conn, tareas["T1"]) == "en_curso"
    assert estado_de(conn, tareas["T2"]) == "asignada"
