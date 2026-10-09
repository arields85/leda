"""Las jugadas de la lista cerrada y sus fichas (`leda.motor.fichas`; E2-3).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Jugadas" y "Aviso al administrador"); ADR
0018, decisiones 1, 4 y 9 (9a: nada se confirma; 9b: el aviso de una nueva previsión; 9c: el
bloqueo; 9g: lo que no está en la lista). Los datos siguen a `tests/conversaciones/`: Marcos es
el responsable e Ismael, que aprueba su trabajo, el referente. La IA es guionada y el reloj,
fijo: el lunes 5 de octubre de 2026, 10:00 en Buenos Aires.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone

import pytest

from leda.db import admin, espacio
from leda.motor import hechos
from leda.motor.fichas import FICHAS, JUGADAS, Contexto
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import ETAPA_FUERA_DE_LA_LISTA, procesar_turno

from tests.motor.ayudantes import AHORA, a_la_vista

VIERNES_9 = datetime(2026, 10, 9, 20, 0, tzinfo=timezone.utc)      # 17:00 en Buenos Aires
OFRECIDAS = ("anotar_inicio", "anotar_prevision", "anotar_bloqueo", "anotar_quien_destraba",
             "destrabar", "consultar_pendientes", "informar_avance", "entregar", "aprobar",
             "pedir_cambios", "ver_entrega", "pedir_enlace")


# --- Ayudas ---------------------------------------------------------------------------------

def _jugar(conn, escribe, nombre: str, *jugadas: Jugada, texto: str = "-") -> list[dict]:
    quien, entrante = escribe(nombre, texto)
    resultado = procesar_turno(conn, quien, entrante,
                               IAGuionada(jugadas=[list(jugadas)], redacciones=["Listo."]),
                               RelojFijo(AHORA))
    conn.commit()
    assert resultado.error is None
    return resultado.hechos


def _uno(conn, sql: str, *params):
    with admin(conn) as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def _todos(conn, sql: str, *params) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def _cuantas(conn, tabla: str) -> int:
    return _uno(conn, f"select count(*) n from {tabla}")["n"]


def _tarea_nueva(conn, mundo, titulo: str, estado: str = "asignada",
                 fecha: datetime = VIERNES_9, responsable: str = "Marcos") -> str:
    with admin(conn) as cur:
        cur.execute("""select objective_id, area_id from task where id = %s""",
                    (mundo["tarea"],))
        base = cur.fetchone()
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado, fecha_objetivo)
               values (%s, %s, %s, %s, %s, %s, %s) returning id""",
            (mundo["id"], base["objective_id"], titulo, base["area_id"],
             mundo["personas"][responsable]["membership_id"], estado, fecha))
        tarea = str(cur.fetchone()["id"])
    conn.commit()
    return tarea


def _estado_de(conn, tarea: str) -> str:
    return str(_uno(conn, "select estado from task where id = %s", tarea)["estado"])


@pytest.fixture
def otro_espacio(conn) -> dict:
    """Otro cliente, con una tarea asignada, para el aislamiento."""
    with admin(conn) as cur:
        cur.execute("""insert into workspace (slug, nombre, zona_horaria, activo)
                       values ('otro', 'Otro', 'America/Argentina/Buenos_Aires', true)
                       returning id""")
        ws = str(cur.fetchone()["id"])
        cur.execute("""insert into area (workspace_id, slug, nombre)
                       values (%s, 'campo', 'Campo') returning id""", (ws,))
        area = str(cur.fetchone()["id"])
        cur.execute("""insert into rol (workspace_id, slug, nombre, autoridad_final)
                       values (%s, 'lider', 'lider', true) returning id""", (ws,))
        rol = str(cur.fetchone()["id"])
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (82000, 'Nora') returning id""")
        usuario = str(cur.fetchone()["id"])
        cur.execute("""insert into membership (workspace_id, app_user_id, area_id, rol_id)
                       values (%s, %s, %s, %s) returning id""", (ws, usuario, area, rol))
        persona = str(cur.fetchone()["id"])
        cur.execute("""insert into objective (workspace_id, tipo, titulo, estado)
                       values (%s, 'operativo', 'Ajeno', 'activo') returning id""", (ws,))
        objetivo = str(cur.fetchone()["id"])
        cur.execute("""insert into task (workspace_id, objective_id, titulo, area_id,
                                         responsable_membership_id, estado, fecha_objetivo)
                       values (%s, %s, 'Tarea ajena', %s, %s, 'asignada', %s)
                       returning id""", (ws, objetivo, area, persona, VIERNES_9))
        tarea = str(cur.fetchone()["id"])
    conn.commit()
    return {"id": ws, "tarea": tarea}


# --- La lista cerrada -----------------------------------------------------------------------

SITUACIONES = ("elegir", "corregir", "cancelar", "dejar_para_despues")


def test_la_lista_cerrada_tiene_una_ficha_por_jugada_del_recordatorio():
    """Las del recordatorio y las de las situaciones generales (E2-4), que no se ofrecen como
    algo que Leda puede hacer."""
    assert sorted(JUGADAS) == sorted(FICHAS) == sorted(
        OFRECIDAS + ("pedir_reasignacion",) + SITUACIONES
        + ("confirmar", "guardar_para_la_entrega"))
    assert not any(FICHAS[n].se_ofrece for n in SITUACIONES)
    for ficha in FICHAS.values():
        assert ficha.para_que and ficha.comprueba and ficha.hace and ficha.despues


# --- anotar_inicio --------------------------------------------------------------------------

def test_el_inicio_pasa_la_tarea_a_en_curso_y_contesta_su_espera(conn, mundo, escribe):
    marcos = mundo["personas"]["Marcos"]
    with admin(conn) as cur:
        cur.execute("""insert into pending_reply (workspace_id, membership_id, task_id, tipo,
                                                  vence_en)
                       values (%s, %s, %s, 'estado', %s)""",
                    (mundo["id"], marcos["membership_id"], mundo["tarea"], AHORA))
    conn.commit()

    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("anotar_inicio", {"tarea": "T1"}),
                     texto="arranqué")

    assert hecho == {"jugada": "anotar_inicio", "resultado": "anotado", "estado": "en_curso",
                     "tarea": {"alias": "T1", "titulo": "Revisar el tablero"},
                     "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-09"}}}
    assert _estado_de(conn, mundo["tarea"]) == "en_curso"
    evento = _uno(conn, """select estado_anterior, estado_nuevo, actor_app_user_id
                             from task_state_event where task_id = %s""", mundo["tarea"])
    assert (evento["estado_anterior"], evento["estado_nuevo"]) == ("asignada", "en_curso")
    assert str(evento["actor_app_user_id"]) == marcos["app_user_id"]
    espera = _uno(conn, "select satisfecho_en from pending_reply")
    assert espera["satisfecho_en"] == AHORA


def test_el_inicio_solo_lo_anota_el_responsable(conn, mundo, escribe):
    # Ismael no tiene esa tarea: para él no hay alias T1.
    [hecho] = _jugar(conn, escribe, "Ismael", Jugada("anotar_inicio", {"tarea": "T1"}))
    assert hecho == {"jugada": "anotar_inicio", "resultado": "no_se_puede",
                     "motivo": "tarea_desconocida"}
    # Aunque una tarea ajena le llegara con alias, la operación del dominio lo niega.
    quien, entrante = escribe("Ismael", "arranqué")
    with espacio(conn, mundo["id"]) as cur:
        ctx = _contexto(cur, quien, entrante, mundo["tarea"])
        hecho = JUGADAS["anotar_inicio"](ctx, Jugada("anotar_inicio", {"tarea": "T1"}))
    conn.commit()
    assert hecho["resultado"] == "no_se_puede" and hecho["motivo"] == "no_autorizado"
    assert _estado_de(conn, mundo["tarea"]) == "asignada"
    assert _cuantas(conn, "task_state_event") == 0


def test_el_inicio_de_una_tarea_ya_en_curso_lo_dice_sin_efecto(conn, mundo, escribe):
    _tarea_nueva(conn, mundo, "Armar el tablero", estado="en_curso")

    hechos = _jugar(conn, escribe, "Marcos", Jugada("anotar_inicio", {"tarea": "T1"}))

    assert hechos == [{"jugada": "anotar_inicio", "resultado": "no_se_puede",
                       "motivo": "estado", "estado": "en_curso",
                       # La cargó otro en curso: el motor no sabe desde cuándo.
                       "estado_desde": "desconocido",
                       "tarea": {"alias": "T1", "titulo": "Armar el tablero"}}]
    assert _cuantas(conn, "task_state_event") == 0
    assert _cuantas(conn, "incident") == 0


def test_una_tarea_sin_nombrar_es_un_dato_que_falta(conn, mundo, escribe):
    """Y se pregunta con las tareas como opciones (situación general 5, `test_situaciones`)."""
    hechos = _jugar(conn, escribe, "Marcos", Jugada("anotar_inicio", {}))
    assert hechos == [{"jugada": "anotar_inicio", "resultado": "falta_dato",
                       "falta": ["tarea"], "pregunta": "cual_tarea"}]
    assert _estado_de(conn, mundo["tarea"]) == "asignada"


# --- anotar_prevision -----------------------------------------------------------------------

def test_la_prevision_anota_el_atraso_en_dias_habiles_y_guarda_el_aviso(conn, mundo, escribe):
    """Vence el viernes 9; prevé el martes 13. El sábado, el domingo y el lunes 12 (feriado)
    no cuentan: un día hábil de atraso, calculado por el código (9b)."""
    dependiente = _tarea_nueva(conn, mundo, "Probar el tablero",
                               fecha=datetime(2026, 10, 16, 20, 0, tzinfo=timezone.utc))
    with admin(conn) as cur:
        cur.execute("insert into holiday (workspace_id, fecha, nombre) values (%s, %s, %s)",
                    (mundo["id"], date(2026, 10, 12), "Diversidad cultural"))
        cur.execute("""insert into dependency (workspace_id, origen_task_id, destino_task_id)
                       values (%s, %s, %s)""", (mundo["id"], mundo["tarea"], dependiente))
    conn.commit()

    [hecho] = _jugar(conn, escribe, "Marcos", Jugada(
        "anotar_prevision", {"tarea": "T1", "fecha": "2026-10-13",
                             "motivo": "el proveedor se demoró"}),
        texto="llego el 13, el proveedor se demoró")

    assert hecho == {
        "jugada": "anotar_prevision", "resultado": "anotado",
        "tarea": {"alias": "T1", "titulo": "Revisar el tablero"},
        "prevision": "2026-10-13", "motivo": "el proveedor se demoró",
        "fecha_comprometida": "2026-10-09",
        # El atraso que tendrá la tarea si se cumple la previsión, nunca el de hoy (ronda 1).
        "atraso_si_se_cumple_la_prevision_dias_habiles": 1,
        "dependientes": ["Probar el tablero"],
        # A quién le llega y cuándo se entera, en la hora del espacio (9e): lo que pasa en el
        # mundo, nunca el estado interno del aviso (usuario, 2026-10-06). Con el margen para
        # corregir (10 minutos; `margen.py`): la hora real en que sale.
        "aviso_al_referente": {"a": "Ismael", "llega": "2026-10-05T10:10:00-03:00"},
        # El seguimiento pasa a la previsión (9i): Leda pide el estado el día previsto.
        "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-13"}}}
    prevision = _uno(conn, "select * from task_forecast")
    assert prevision["fecha_prevista"] == date(2026, 10, 13)
    assert prevision["fecha_comprometida"] == VIERNES_9
    assert prevision["atraso_dias_habiles"] == 1 and prevision["reemplaza_id"] is None
    assert str(prevision["dicho_por_membership_id"]) == mundo["personas"]["Marcos"][
        "membership_id"]
    assert prevision["at"] == AHORA and str(prevision["workspace_id"]) == mundo["id"]
    # La fecha comprometida no cambia (ADR 0017, decisión 4).
    assert _uno(conn, "select fecha_objetivo from task where id = %s",
                mundo["tarea"])["fecha_objetivo"] == VIERNES_9

    aviso = _uno(conn, "select * from scheduled_notice")
    assert aviso["tipo"] == "nueva_prevision" and str(aviso["task_id"]) == mundo["tarea"]
    assert str(aviso["destinatario_membership_id"]) == mundo["personas"]["Ismael"][
        "membership_id"]
    # Los hechos del aviso dicen qué aviso son y que no piden respuesta (revisión del contrato).
    assert aviso["hechos"] == {
        "aviso": "nueva_prevision", "necesita_respuesta": False,
        "tarea": "Revisar el tablero", "responsable": "Marcos", "prevision": "2026-10-13",
        "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-09",
        "atraso_si_se_cumple_la_prevision_dias_habiles": 1,
        "dependientes": ["Probar el tablero"]}
    assert aviso["estado"] == "guardado"
    assert aviso["programado_para"] == AHORA + timedelta(minutes=10)
    assert aviso["creado_en"] == AHORA
    # Guardado, no enviado: el envío es de la E2-5. Atado al turno que lo causó.
    assert _cuantas(conn, "message_outbox") == 1          # sólo la respuesta a Marcos
    turno = _uno(conn, "select id from conversation_turn where sentido = 'entrada'")
    assert aviso["turno_id"] == turno["id"]


def test_la_redaccion_recibe_cuando_se_entera_el_referente(conn, mundo, escribe):
    """Primer contacto real (2026-10-05): con sólo `a` y su hora, la IA dijo que Ismael ya
    estaba avisado. Prueba por Telegram real (2026-10-06): con el estado interno del aviso, la
    IA lo repetía. El hecho dice cuándo se entera (`llega`), que todavía no pasó, y nada más."""
    quien, entrante = escribe("Marcos", "llego el 13, el proveedor se demoró")
    ia = IAGuionada(jugadas=[[Jugada("anotar_prevision", {"tarea": "T1",
                                                          "fecha": "2026-10-13",
                                                          "motivo": "el proveedor se demoró"})]],
                    redacciones=["Listo."])
    procesar_turno(conn, quien, entrante, ia, RelojFijo(AHORA))
    conn.commit()

    [hecho] = ia.pedidos_de_redaccion[0]["hechos"]
    assert hecho["aviso_al_referente"] == {"a": "Ismael", "llega": "2026-10-05T10:10:00-03:00"}
    # Y es cierto: el aviso está guardado y nada salió para Ismael.
    assert _uno(conn, "select estado from scheduled_notice")["estado"] == "guardado"
    assert _cuantas(conn, "message_outbox") == 1          # sólo la respuesta a Marcos


def test_la_redaccion_de_un_dia_nuevo_nombra_a_quien_se_le_avisa_solo_si_se_pregunta(
        conn, mundo, escribe):
    """Decisión 11 del usuario (2026-10-08): "✏️ Quedó anotado que la terminás el mar 27/10. La
    nueva fecha queda informada.", sin nombrar a quien aprueba su trabajo; si la persona
    pregunta a quién se le avisó, el nombre está en `solo_si_pregunta`. La cocina lo guarda."""
    [hecho] = _jugar(conn, escribe, "Marcos", Jugada(
        "anotar_prevision", {"tarea": "T1", "fecha": "2026-10-13", "motivo": "faltan cables"}))

    assert hecho["aviso_al_referente"]["a"] == "Ismael"
    redactado = hechos.para_redactar(hecho)
    assert "Ismael" not in a_la_vista(redactado)
    # D8: la hora en que se entera, también sólo si pregunta, como el nombre (el modelo del
    # usuario no la dice).
    assert redactado["aviso_a_quien_aprueba_su_trabajo"] == {
        "solo_si_pregunta": {"a": "Ismael", "llega": "2026-10-05T10:10:00-03:00"}}


def test_el_aviso_al_referente_espera_el_margen_del_espacio(conn, mundo, escribe):
    """El margen para corregir es del espacio (`workspace_setting`, `margen.CLAVE_MARGEN`): el
    aviso se guarda para cuando termina, y el hecho dice esa hora, la real."""
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'margen_para_corregir_minutos', '3')""", (mundo["id"],))
    conn.commit()

    [hecho] = _jugar(conn, escribe, "Marcos", Jugada(
        "anotar_prevision", {"tarea": "T1", "fecha": "2026-10-13", "motivo": "faltan cables"}))

    assert hecho["aviso_al_referente"] == {"a": "Ismael", "llega": "2026-10-05T10:03:00-03:00"}
    aviso = _uno(conn, "select programado_para from scheduled_notice")
    assert aviso["programado_para"] == AHORA + timedelta(minutes=3)


def test_el_margen_que_termina_fuera_del_horario_espera_al_dia_habil_siguiente(conn, mundo,
                                                                              escribe):
    """El horario sigue valiendo encima del margen (9e): a las 16:55, el margen termina después
    de las 17:00, así que el aviso sale el martes a la hora de salida, y el hecho lo dice."""
    quien, entrante = escribe("Marcos", "llego el 13")
    a_las = datetime(2026, 10, 5, 19, 55, tzinfo=timezone.utc)          # 16:55
    resultado = procesar_turno(
        conn, quien, entrante,
        IAGuionada(jugadas=[[Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-13",
                                                         "motivo": "faltan cables"})]],
                   redacciones=["Listo."]), RelojFijo(a_las))
    conn.commit()

    [hecho] = resultado.hechos
    assert hecho["aviso_al_referente"] == {"a": "Ismael", "llega": "2026-10-06T10:00:00-03:00"}
    assert _uno(conn, "select programado_para from scheduled_notice")["programado_para"] ==         datetime(2026, 10, 6, 13, 0, tzinfo=timezone.utc)


def test_una_prevision_en_la_fecha_comprometida_no_avisa(conn, mundo, escribe):
    [hecho] = _jugar(conn, escribe, "Marcos", Jugada(
        "anotar_prevision", {"tarea": "T1", "fecha": "2026-10-09"}))

    assert hecho["resultado"] == "anotado"
    assert hecho["atraso_si_se_cumple_la_prevision_dias_habiles"] == 0
    assert hecho["aviso_al_referente"] is None
    assert hecho["sin_aviso"] == "misma_fecha_comprometida"
    assert _cuantas(conn, "task_forecast") == 1
    assert _cuantas(conn, "scheduled_notice") == 0


def test_una_prevision_que_vuelve_a_la_fecha_retira_el_aviso_que_no_salio(conn, mundo,
                                                                          escribe):
    """9b: para el referente no cambió nada. La historia guarda las dos previsiones y el
    aviso que no salió, con su motivo."""
    _jugar(conn, escribe, "Marcos", Jugada(
        "anotar_prevision", {"tarea": "T1", "fecha": "2026-10-14", "motivo": "faltan cables"}))
    [hecho] = _jugar(conn, escribe, "Marcos", Jugada(
        "anotar_prevision", {"tarea": "T1", "fecha": "2026-10-09"}))

    assert hecho["sin_aviso"] == "misma_fecha_comprometida"
    primera, segunda = _todos(conn, """select id, reemplaza_id, atraso_dias_habiles
                                         from task_forecast
                                        order by atraso_dias_habiles desc""")
    assert primera["atraso_dias_habiles"] == 3 and segunda["atraso_dias_habiles"] == 0
    assert segunda["reemplaza_id"] == primera["id"]
    [aviso] = _todos(conn, "select estado, motivo_omision, resuelto_en from scheduled_notice")
    assert aviso["estado"] == "omitido" and aviso["resuelto_en"] == AHORA
    assert aviso["motivo_omision"] == "hay_una_prevision_mas_nueva"


def test_una_fecha_que_no_es_fecha_no_anota_nada(conn, mundo, escribe):
    hechos = _jugar(conn, escribe, "Marcos", Jugada(
        "anotar_prevision", {"tarea": "T1", "fecha": "el martes"}))
    assert hechos[0]["resultado"] == "falta_dato" and hechos[0]["falta"] == ["fecha"]
    assert _cuantas(conn, "task_forecast") == 0


# --- anotar_bloqueo y anotar_quien_destraba -------------------------------------------------

def test_un_bloqueo_sin_causa_pregunta_la_causa_y_no_anota_nada(conn, mundo, escribe):
    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("anotar_bloqueo", {"tarea": "T1"}),
                     texto="estoy trabado")

    assert hecho == {"jugada": "anotar_bloqueo", "resultado": "falta_dato",
                     "falta": ["causa"], "pregunta": "causa_del_bloqueo",
                     "tarea": {"alias": "T1", "titulo": "Revisar el tablero"}}
    assert _cuantas(conn, "blocker") == 0 and _estado_de(conn, mundo["tarea"]) == "asignada"
    pregunta = _uno(conn, "select * from conversation_question")
    assert pregunta["tipo"] == "causa_del_bloqueo" and pregunta["se_puede_dejar"] is True
    assert str(pregunta["task_id"]) == mundo["tarea"] and pregunta["abierta_en"] == AHORA
    estado = _uno(conn, "select pregunta_abierta_id from conversation_state")
    assert estado["pregunta_abierta_id"] == pregunta["id"]


def test_un_bloqueo_con_causa_se_anota_y_pregunta_quien_destraba(conn, mundo, escribe):
    [hecho] = _jugar(conn, escribe, "Marcos", Jugada(
        "anotar_bloqueo", {"tarea": "T1", "causa": "falta el repuesto"}))

    assert hecho == {"jugada": "anotar_bloqueo", "resultado": "anotado",
                     "causa": "falta el repuesto", "pregunta": "quien_destraba",
                     "tarea": {"alias": "T1", "titulo": "Revisar el tablero"},
                     "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}
    bloqueo = _uno(conn, "select id, causa, resuelto_en from blocker")
    assert bloqueo["causa"] == "falta el repuesto" and bloqueo["resuelto_en"] is None
    assert _estado_de(conn, mundo["tarea"]) == "bloqueada"
    pregunta = _uno(conn, "select * from conversation_question")
    assert pregunta["tipo"] == "quien_destraba" and pregunta["se_puede_dejar"] is False
    assert pregunta["jugada"]["bloqueo_id"] == str(bloqueo["id"])
    # Ningún aviso al referente por un bloqueo (9c, paso 4).
    assert _cuantas(conn, "scheduled_notice") == 0
    assert _cuantas(conn, "message_outbox") == 1          # sólo la respuesta a Marcos


@pytest.mark.parametrize("datos", [
    {"causa": "no sé configurar el protocolo"},
    # La IA ya no juzga si depende de otro (9c, corregida el 2026-10-05): si lo manda, no
    # cuenta. En el primer contacto real lo puso en falso y Leda no preguntó.
    {"causa": "falta el repuesto", "depende_de_otro": False},
])
def test_todo_bloqueo_con_causa_pregunta_quien_lo_puede_destrabar(conn, mundo, escribe, datos):
    """Lo que decide es la respuesta de la persona, no un juicio de la IA sobre la causa."""
    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("anotar_bloqueo", {"tarea": "T1", **datos}))
    assert hecho["resultado"] == "anotado" and hecho["pregunta"] == "quien_destraba"
    assert "salidas" not in hecho
    [pregunta] = _todos(conn, "select tipo, se_puede_dejar from conversation_question")
    assert pregunta == {"tipo": "quien_destraba", "se_puede_dejar": False}


@pytest.mark.parametrize("dicho, esperado, columna", [
    ({"quien": "Ismael"}, {"integrante": "Ismael"}, "destraba_membership_id"),
    ({"quien": "el de compras"}, {"externo": "el de compras"}, "destraba_externo"),
    ({"no_sabe": True}, {"no_sabe": True}, "no_sabe"),
    # "Nadie, me falta saber cómo": le toca a la persona, que queda como quien destraba.
    ({"nadie_mas": True}, {"nadie_mas": True}, "destraba_membership_id"),
    # Nombrarse a sí misma es lo mismo.
    ({"quien": "Marcos"}, {"nadie_mas": True}, "destraba_membership_id"),
])
def test_quien_destraba_se_anota_y_cierra_la_pregunta(conn, mundo, escribe, dicho, esperado,
                                                      columna):
    _jugar(conn, escribe, "Marcos", Jugada(
        "anotar_bloqueo", {"tarea": "T1", "causa": "falta el repuesto"}))

    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("anotar_quien_destraba", dicho))

    assert hecho["resultado"] == "anotado" and hecho["quien_destraba"] == esperado
    assert hecho["tarea"] == {"alias": "T1", "titulo": "Revisar el tablero"}
    # Las salidas, sólo si no hay otra persona que lo destrabe (9c, corregida el 2026-10-05):
    # con un nombre, seguir a esa persona es la persecución, de la prueba siguiente.
    sin_otra_persona = "no_sabe" in esperado or "nadie_mas" in esperado
    assert hecho.get("salidas") == (["que_alguien_ayude", "anotar_prevision"]
                                    if sin_otra_persona else None)
    fila = _uno(conn, "select * from blocker_unblocker")
    assert fila[columna] not in (None, False)
    assert [c for c in ("destraba_membership_id", "destraba_externo")
            if fila[c] is not None and c != columna] == []
    if columna == "destraba_membership_id":
        assert str(fila[columna]) == mundo["personas"][
            "Marcos" if "nadie_mas" in esperado else "Ismael"]["membership_id"]
    assert fila["at"] == AHORA
    pregunta = _uno(conn, """select cerrada_en, cierre, cierre_detalle from conversation_question
                              where tipo = 'quien_destraba'""")
    assert pregunta["cerrada_en"] == AHORA and pregunta["cierre"] == "respondida"
    assert pregunta["cierre_detalle"] == {"blocker_unblocker_id": str(fila["id"])}
    # Las salidas quedan como tema abierto (decisión del usuario, 2026-10-05); con otra persona
    # que lo destraba no queda ninguno.
    abierta = _uno(conn, """select q.tipo from conversation_state s
                              join conversation_question q on q.id = s.pregunta_abierta_id""")
    assert (abierta or {}).get("tipo") == ("propuesta" if sin_otra_persona else None)


@pytest.mark.parametrize("dicho, esperado", [
    # Mayúsculas y acentos no cuentan; un nombre de pila o un apellido entero, sí.
    ("ismaél", {"integrante": "Ismael"}),
    ("ISMAEL", {"integrante": "Ismael"}),
    # Un pedazo de un nombre no es ese nombre, y `%` o `_` no son comodines.
    ("Mar", {"externo": "Mar"}),
    ("%", {"externo": "%"}),
    ("_", {"externo": "_"}),
    ("el de compras", {"externo": "el de compras"}),
])
def test_quien_destraba_reconoce_un_integrante_por_nombre_entero(conn, mundo, escribe, dicho,
                                                                 esperado):
    """Revisión de la E2-3: el nombre se compara por palabras enteras, sin mayúsculas ni
    acentos, nunca como un patrón de la base."""
    _jugar(conn, escribe, "Marcos", Jugada(
        "anotar_bloqueo", {"tarea": "T1", "causa": "falta el repuesto"}))

    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("anotar_quien_destraba",
                                                     {"quien": dicho}))

    assert hecho["resultado"] == "anotado" and hecho["quien_destraba"] == esperado


def test_quien_destraba_con_dos_integrantes_que_coinciden_es_un_dato_que_falta(conn, mundo,
                                                                               escribe):
    with admin(conn) as cur:
        cur.execute("""select area_id, rol_id from membership where id = %s""",
                    (mundo["personas"]["Ismael"]["membership_id"],))
        base = cur.fetchone()
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (81500, 'Ismael Otero') returning id""")
        usuario = cur.fetchone()["id"]
        cur.execute("""insert into membership (workspace_id, app_user_id, area_id, rol_id)
                       values (%s, %s, %s, %s)""",
                    (mundo["id"], usuario, base["area_id"], base["rol_id"]))
    conn.commit()
    _jugar(conn, escribe, "Marcos", Jugada(
        "anotar_bloqueo", {"tarea": "T1", "causa": "falta el repuesto"}))

    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("anotar_quien_destraba",
                                                     {"quien": "Ismael"}))

    assert hecho == {"jugada": "anotar_quien_destraba", "resultado": "falta_dato",
                     "falta": ["integrante"], "coinciden": ["Ismael", "Ismael Otero"]}
    assert _cuantas(conn, "blocker_unblocker") == 0


@pytest.mark.parametrize("dicho", [
    {}, {"quien": "Ismael", "no_sabe": True}, {"quien": "Ismael", "nadie_mas": True},
    {"no_sabe": True, "nadie_mas": True},
])
def test_quien_destraba_es_exactamente_una_respuesta(conn, mundo, escribe, dicho):
    _jugar(conn, escribe, "Marcos", Jugada(
        "anotar_bloqueo", {"tarea": "T1", "causa": "falta el repuesto"}))
    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("anotar_quien_destraba", dicho))
    # Las tres respuestas que puede ser, también "nadie más" (revisión de la E2-3b).
    assert hecho == {"jugada": "anotar_quien_destraba", "resultado": "falta_dato",
                     "falta": ["quien_destraba"],
                     "puede_ser": ["alguien", "no_sabe", "nadie_mas"]}
    assert _cuantas(conn, "blocker_unblocker") == 0


def test_quien_destraba_sin_bloqueo_abierto_no_anota_nada(conn, mundo, escribe):
    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("anotar_quien_destraba",
                                                     {"no_sabe": True}))
    assert hecho == {"jugada": "anotar_quien_destraba", "resultado": "no_se_puede",
                     "motivo": "sin_bloqueo_abierto"}
    assert _cuantas(conn, "blocker_unblocker") == 0


# --- destrabar (decisión del usuario, 2026-10-05; ADR 0018, 9l; conversación 17) -----------

T1 = {"alias": "T1", "titulo": "Revisar el tablero"}


@pytest.mark.parametrize("antes", ["asignada", "en_curso"])
def test_destrabar_cierra_el_bloqueo_y_la_tarea_vuelve_a_su_estado_de_antes(conn, mundo,
                                                                           escribe, antes):
    """Mecánica §3: salir de `bloqueada` devuelve la tarea al estado que tenía antes. Se anota
    directo, como el bloqueo, y cierra la pregunta de quién lo destraba y su espera."""
    if antes == "en_curso":
        _jugar(conn, escribe, "Marcos", Jugada("anotar_inicio", {"tarea": "T1"}))
    _jugar(conn, escribe, "Marcos", Jugada("anotar_bloqueo",
                                           {"tarea": "T1", "causa": "espero el switch"}))

    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("destrabar", {"tarea": "T1"}),
                     texto="llego el switch, sigo")

    # Antes de su fecha, la escalera sigue sola: no se guarda ningún pedido.
    assert hecho == {"jugada": "destrabar", "resultado": "anotado", "tarea": T1,
                     "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": antes,
                     "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-09"}}}
    assert _estado_de(conn, mundo["tarea"]) == antes
    bloqueo = _uno(conn, "select resuelto_en, resolucion from blocker")
    assert bloqueo["resuelto_en"] is not None
    assert bloqueo["resolucion"] == "llego el switch, sigo"
    [salida] = _todos(conn, """select estado_nuevo from task_state_event
                                where estado_anterior = 'bloqueada'""")
    assert salida["estado_nuevo"] == antes
    pregunta = _uno(conn, """select cerrada_en, cierre from conversation_question
                              where tipo = 'quien_destraba'""")
    assert pregunta == {"cerrada_en": AHORA, "cierre": "respondida"}
    assert _cuantas(conn, "pending_reply where satisfecho_en is null") == 0
    assert _uno(conn, "select pregunta_abierta_id from conversation_state")[
        "pregunta_abierta_id"] is None
    assert _cuantas(conn, "scheduled_notice") == 0      # ni pedido ni aviso a nadie


def test_destrabar_cierra_lo_propuesto_para_salir_del_bloqueo(conn, mundo, escribe):
    """Las salidas de un bloqueo sin otra persona que lo destrabe (9c, paso 3) ya no corresponden
    cuando el bloqueo se cierra."""
    _jugar(conn, escribe, "Marcos", Jugada("anotar_bloqueo",
                                           {"tarea": "T1", "causa": "falta el repuesto"}))
    _jugar(conn, escribe, "Marcos", Jugada("anotar_quien_destraba", {"no_sabe": True}))

    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("destrabar", {"tarea": "T1"}))

    assert hecho["resultado"] == "anotado" and "pregunta" not in hecho
    assert _cuantas(conn, "conversation_question where cerrada_en is null") == 0
    propuesta = _uno(conn, """select cierre from conversation_question
                               where tipo = 'propuesta'""")
    assert propuesta["cierre"] == "sin_efecto"


def test_destrabar_una_tarea_que_no_esta_trabada_no_hace_nada(conn, mundo, escribe):
    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("destrabar", {"tarea": "T1"}))

    assert hecho == {"jugada": "destrabar", "resultado": "no_se_puede", "motivo": "estado",
                     "tarea": T1, "estado": "asignada"}
    assert _cuantas(conn, "task_state_event") == 0


def test_destrabar_con_dos_bloqueos_abiertos_no_adivina_cual(conn, mundo, escribe):
    """Leda no elige por la persona qué causa desapareció: lo dice, con las causas, y no
    cierra ninguno."""
    for causa in ("espero el switch", "falta la fuente"):
        _jugar(conn, escribe, "Marcos", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": causa}))

    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("destrabar", {"tarea": "T1"}))

    assert hecho == {"jugada": "destrabar", "resultado": "no_se_puede",
                     "motivo": "varios_bloqueos_abiertos", "tarea": T1,
                     "causas": ["espero el switch", "falta la fuente"]}
    assert _cuantas(conn, "blocker where resuelto_en is null") == 2
    assert _estado_de(conn, mundo["tarea"]) == "bloqueada"


def test_destrabar_el_dia_del_vencimiento_vuelve_a_pedir_el_estado(conn, mundo, escribe):
    """Con el seguimiento ya empezado (hoy es su fecha), destrabarse no es algo cierto sobre
    cuándo la termina: la espera del estado queda abierta y Leda vuelve a pedirlo el día hábil
    siguiente, con la cuenta de nuevo, como después de un avance (9h). Todavía no está vencida:
    sin la pregunta de para cuándo (9j)."""
    # La fecha comprometida no cambia (la base lo impide): una tarea que vence hoy, que es T1.
    _tarea_nueva(conn, mundo, "Cablear el tablero",
                 fecha=datetime(2026, 10, 5, 20, 0, tzinfo=timezone.utc))      # hoy, 17:00
    _jugar(conn, escribe, "Marcos", Jugada("anotar_bloqueo",
                                           {"tarea": "T1", "causa": "se quemo la fuente"}))

    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("destrabar", {"tarea": "T1"}),
                     texto="ya cambie la fuente, sigo")

    assert hecho["resultado"] == "anotado" and hecho["estado"] == "asignada"
    assert list(hecho["vuelve_a_pedir_el_estado"]) == ["llega"]
    assert hecho["vuelve_a_pedir_el_estado"]["llega"].startswith("2026-10-06")
    assert hecho["veces_sin_algo_cierto"] == 1
    assert "vencida" not in hecho and "pregunta" not in hecho
    [pedido] = _todos(conn, "select tipo, estado, hechos from scheduled_notice")
    assert (pedido["tipo"], pedido["estado"]) == ("repregunta_de_estado", "guardado")
    assert pedido["hechos"]["avance_anterior"]["jugada"] == "destrabar"
    assert pedido["hechos"]["avance_anterior"]["dijo"] == "ya cambie la fuente, sigo"
    espera = _uno(conn, """select tipo from pending_reply where satisfecho_en is null""")
    assert espera["tipo"] == "estado_de_la_tarea"


def test_destrabar_una_tarea_vencida_pregunta_para_cuando(conn, mundo, escribe):
    """La regla de la tarea vencida (9j) vale también para destrabar: no es una fecha."""
    _tarea_nueva(conn, mundo, "Cablear el tablero",
                 fecha=datetime(2026, 10, 2, 20, 0, tzinfo=timezone.utc))      # el viernes
    _jugar(conn, escribe, "Marcos", Jugada("anotar_bloqueo",
                                           {"tarea": "T1", "causa": "espero el switch"}))

    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("destrabar", {"tarea": "T1"}))

    assert hecho["vencida"]["atraso_dias_habiles"] == 1
    assert hecho["pregunta"] == "fecha_de_la_tarea"
    assert hecho["vuelve_a_pedir_el_estado"]["llega"].startswith("2026-10-06")
    assert _cuantas(conn, "scheduled_notice where tipo = 'repregunta_de_estado'") == 1


# --- consultar_pendientes, entregar y pedir_reasignacion ------------------------------------

def test_consultar_pendientes_solo_lee(conn, mundo, escribe):
    _tarea_nueva(conn, mundo, "Cablear el tablero", estado="en_curso",
                 fecha=datetime(2026, 10, 16, 20, 0, tzinfo=timezone.utc))
    _tarea_nueva(conn, mundo, "Pedir los cables", estado="terminada")
    _tarea_nueva(conn, mundo, "Tarea de Ismael", responsable="Ismael")
    tablas = ("task_state_event", "blocker", "task_forecast", "scheduled_notice",
              "conversation_question", "conversation_state", "incident", "pending_reply")
    antes = {t: _cuantas(conn, t) for t in tablas}

    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("consultar_pendientes"))

    assert hecho == {"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [
        {"alias": "T1", "titulo": "Revisar el tablero", "estado": "asignada",
         "vence": "2026-10-09"},
        {"alias": "T2", "titulo": "Cablear el tablero", "estado": "en_curso",
         "vence": "2026-10-16"}]}
    assert {t: _cuantas(conn, t) for t in tablas} == antes


def test_entregar_muestra_la_entrega_y_no_escribe_ni_avisa_nada_hasta_confirmar(
        conn, mundo, escribe):
    """La entrega se recibe por chat desde la porción 2 de la C-3 (ADR 0019, decisión 5): sin
    política de evidencia, lo que escribió es la entrega y espera la confirmación. Los detalles,
    en `test_entrega.py`."""
    _tarea_nueva(conn, mundo, "Armar el tablero", estado="en_curso")
    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("entregar", {"tarea": "T1"}),
                     texto="ya la terminé")

    assert hecho["jugada"] == "entregar" and hecho["resultado"] == "para_confirmar"
    assert hecho["entrega"] == [{"pieza": "P1", "es": "lo_que_escribio",
                                 "dice": "ya la terminé", "cubre": []}]
    assert hecho["pregunta"] == "confirmar_la_entrega"
    assert _cuantas(conn, "task_state_event") == 0 and _cuantas(conn, "incident") == 0
    assert _cuantas(conn, "evidence") == 0 and _cuantas(conn, "scheduled_notice") == 0


def test_una_tarea_sin_arrancar_se_entrega_con_su_vista_previa(conn, mundo, escribe):
    """Decisión 14 del usuario (2026-10-08): "la terminé" sobre una tarea asignada se recibe
    igual; al confirmar, la historia dice que arrancó y se entregó en ese momento."""
    [hecho] = _jugar(conn, escribe, "Marcos", Jugada("entregar", {"tarea": "T1"}),
                     texto="ya la terminé")
    assert hecho["resultado"] == "para_confirmar"
    assert hecho["al_confirmar"]["arranca_al_entregarla"] is True


def test_una_reasignacion_dice_quien_decide_y_no_avisa_a_nadie(conn, mundo, escribe):
    [hecho] = _jugar(conn, escribe, "Marcos", Jugada(
        "pedir_reasignacion", {"tarea": "T1", "a": "Nahuel"}),
        texto="me la podés pasar a Nahuel?")

    # La previsión ofrecida queda como tema abierto (decisión del usuario, 2026-10-05).
    assert hecho == {"jugada": "pedir_reasignacion", "resultado": "no_por_chat",
                     "motivo": "cambiar_el_responsable_no_es_por_chat",
                     "quien_decide": "Ismael", "alternativa": "anotar_prevision",
                     "tarea": {"alias": "T1", "titulo": "Revisar el tablero"},
                     "pregunta": "propuesta"}
    assert _uno(conn, "select responsable_membership_id r from task where id = %s",
                mundo["tarea"])["r"] is not None
    assert _cuantas(conn, "incident") == 0 and _cuantas(conn, "scheduled_notice") == 0


# --- Fuera de la lista ----------------------------------------------------------------------

def test_lo_que_no_esta_en_la_lista_no_hace_nada_y_avisa_al_administrador(conn, mundo,
                                                                         escribe):
    with admin(conn) as cur:
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (90000, 'Admin') returning id""")
        administrador = str(cur.fetchone()["id"])
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (administrador,))
        cur.execute("""insert into audit_log (actor_app_user_id, actor_kind, accion, detalle)
                       values (%s, 'persona', 'mensaje_admin', %s)""",
                    (administrador, json.dumps({"chat_id": 90000})))
    conn.commit()
    pedido = "me recordás el viernes que tengo turno con el médico?"

    hechos = _jugar(conn, escribe, "Marcos",
                    Jugada("recordar_algo_personal", {"cuando": "viernes"}),
                    Jugada("otra_cosa_nueva", {}), texto=pedido)

    assert hechos == [
        {"jugada": nombre, "resultado": "fuera_de_la_lista",
         "lo_que_puede_hacer": [FICHAS[n].para_que for n in sorted(OFRECIDAS)],
         # Leda lo sabe, pero lo dice sólo si la persona lo pregunta (9g).
         # El aviso sale enseguida por el bot de administración: cuándo le llega.
         "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-05T10:00:00-03:00"}}}
        for nombre in ("recordar_algo_personal", "otra_cosa_nueva")]
    assert _estado_de(conn, mundo["tarea"]) == "asignada"
    # Un solo aviso por mensaje, que apunta al mensaje que lo provocó.
    [incidente] = _todos(conn, "select * from incident")
    assert incidente["etapa"] == ETAPA_FUERA_DE_LA_LISTA and incidente["severidad"] == "baja"
    entrante = _uno(conn, "select id from inbound_message where texto = %s", pedido)["id"]
    assert incidente["referencia_tipo"] == "inbound_message"
    assert incidente["referencia_id"] == entrante
    assert incidente["notificado_en"] is None          # a la persona no se le dice (9g)
    [aviso] = _todos(conn, "select cuerpo, chat_id from admin_notice")
    assert aviso["chat_id"] == 90000
    assert pedido in aviso["cuerpo"] and "lista cerrada de jugadas" in aviso["cuerpo"]
    # Su título no dice que Leda no pudo responder: respondió, con lo que puede hacer.
    assert aviso["cuerpo"].splitlines()[0] == (
        "Leda recibió de Marcos un pedido que todavía no sabe hacer")
    assert "no pudo responder" not in aviso["cuerpo"]
    # Si después pregunta, la IA ve en los últimos turnos que se avisó (conversación 12).
    quien, siguiente = escribe("Marcos", "y eso le avisaste a alguien?")
    ia = IAGuionada(jugadas=[[]], redacciones=["Sí."])
    procesar_turno(conn, quien, siguiente, ia, RelojFijo(AHORA))
    [entrada] = [t for t in ia.pedidos_de_jugadas[0]["ultimos_turnos"]
                 if t["sentido"] == "entrada"]
    assert entrada["hechos"][0]["solo_si_pregunta"] == {
        "aviso_al_administrador": {"llega": "2026-10-05T10:00:00-03:00"}}


# --- Aislamiento ----------------------------------------------------------------------------

def _contexto(cur, quien, entrante: str, tarea_id: str) -> Contexto:
    """Un contexto con una tarea que no es de la persona, como si le llegara con alias."""
    return Contexto(cur=cur, quien=quien, entrante_id=entrante, chat_id=0, texto="-",
                    ahora=AHORA, estado=None, ultimos_turnos=(),
                    tareas=({"alias": "T1", "id": tarea_id, "titulo": "Ajena",
                             "estado": "asignada", "fecha_objetivo": None},))


@pytest.mark.parametrize("jugada", [
    Jugada("anotar_inicio", {"tarea": "T1"}),
    Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-13"}),
    Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "faltan cables"}),
])
def test_una_jugada_nunca_toca_una_tarea_de_otro_espacio(conn, mundo, escribe, otro_espacio,
                                                         jugada):
    quien, entrante = escribe("Marcos", "-")
    with espacio(conn, mundo["id"]) as cur:
        hecho = JUGADAS[jugada.nombre](_contexto(cur, quien, entrante, otro_espacio["tarea"]),
                                       jugada)
    conn.commit()

    assert hecho["resultado"] == "no_se_puede"
    assert hecho["motivo"] in ("tarea_desconocida", "no_autorizado")
    assert _estado_de(conn, otro_espacio["tarea"]) == "asignada"
    for tabla in ("task_state_event", "task_forecast", "blocker", "scheduled_notice",
                  "conversation_question"):
        assert _cuantas(conn, tabla) == 0, tabla


# --- Lo que la operación del dominio contesta (revisión de la E2-3) -------------------------

def _tarea_cerrada_con_alias(conn, mundo, estado: str) -> str:
    """Una tarea de Marcos ya cerrada que, como si se hubiera cerrado durante el turno,
    todavía le llega a la ficha con alias."""
    return _tarea_nueva(conn, mundo, "Tarea cerrada", estado=estado)


@pytest.mark.parametrize("estado", ["terminada", "cancelada"])
@pytest.mark.parametrize("jugada", [
    Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-13"}),
    Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "faltan cables"}),
])
def test_una_tarea_cerrada_no_acepta_prevision_ni_bloqueo(conn, mundo, escribe, estado,
                                                          jugada):
    tarea = _tarea_cerrada_con_alias(conn, mundo, estado)
    quien, entrante = escribe("Marcos", "-")
    with espacio(conn, mundo["id"]) as cur:
        hecho = JUGADAS[jugada.nombre](_contexto(cur, quien, entrante, tarea), jugada)
    conn.commit()

    assert hecho["resultado"] == "no_se_puede" and hecho["motivo"] == "estado"
    assert hecho["estado"] == estado
    for tabla in ("task_forecast", "scheduled_notice", "blocker", "conversation_question"):
        assert _cuantas(conn, tabla) == 0, tabla


def _falla_de_la_base(mensaje: str):
    import psycopg

    return psycopg.errors.RaiseException(mensaje)


@pytest.mark.parametrize("jugada", [
    Jugada("anotar_inicio", {"tarea": "T1"}),
    Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "faltan cables"}),
    Jugada("consultar_pendientes"),
])
@pytest.mark.parametrize("levanta, resultado, motivo", [
    (lambda: _falla_de_la_base("No se puede pasar la tarea a en curso: depende de otra"),
     "no_se_puede", "regla_del_trabajo"),
    (lambda: _de_herramientas("NecesitaConfirmacion")("resumen", "x", {}),
     "no_se_puede", "pide_otro_paso"),
    (lambda: _de_herramientas("EstadoCambio")("resumen", "x", {}, "huella"),
     "no_se_puede", "pide_otro_paso"),
    (lambda: _de_herramientas("NecesitaOpciones")("¿cuál?", []),
     "no_se_puede", "pide_otro_paso"),
    (lambda: _de_herramientas("NecesitaElegir")("¿cuál?", "responsable", [("Ana", "1")]),
     "falta_dato", None),
])
def test_lo_que_levanta_la_operacion_del_dominio_es_un_hecho_nunca_un_turno_caido(
        conn, mundo, escribe, monkeypatch, jugada, levanta, resultado, motivo):
    import leda.motor.fichas as fichas

    def ejecutar(*_, **__):
        raise levanta()

    monkeypatch.setattr(fichas, "ejecutar", ejecutar)
    [hecho] = _jugar(conn, escribe, "Marcos", jugada)

    assert hecho["jugada"] == jugada.nombre and hecho["resultado"] == resultado
    if motivo is not None:
        assert hecho["motivo"] == motivo
    else:
        assert hecho["falta"] == ["responsable"] and hecho["coinciden"] == ["Ana"]
    # Ningún texto de la base ni de la operación llega a la IA (constitución §10).
    assert "depende de otra" not in json.dumps(hecho, ensure_ascii=False)
    assert _estado_de(conn, mundo["tarea"]) == "asignada"
    assert _cuantas(conn, "blocker") == 0 and _cuantas(conn, "incident") == 0


def _de_herramientas(nombre: str):
    import leda.motor.fichas as fichas

    return getattr(fichas, nombre)


@pytest.mark.parametrize("devuelve, motivo", [
    ({"error": "esa tarea no existe en este equipo"}, "tarea_desconocida"),
    ({"error": "esa tarea ya está cerrada, no se le puede agregar un bloqueo"},
     "tarea_cerrada"),
])
def test_un_rechazo_de_la_operacion_del_bloqueo_dice_su_motivo(conn, mundo, escribe,
                                                              monkeypatch, devuelve, motivo):
    import leda.motor.fichas as fichas

    monkeypatch.setattr(fichas, "ejecutar", lambda *_, **__: devuelve)
    [hecho] = _jugar(conn, escribe, "Marcos", Jugada(
        "anotar_bloqueo", {"tarea": "T1", "causa": "faltan cables"}))

    assert hecho["resultado"] == "no_se_puede" and hecho["motivo"] == motivo
    assert _cuantas(conn, "conversation_question") == 0
