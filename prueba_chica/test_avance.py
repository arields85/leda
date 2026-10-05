"""Un avance sin un hecho cierto: la jugada `informar_avance` (decisión del usuario, 2026-10-05).

`tests/conversaciones/15-avance-vago.md`; ADR 0018, decisión 9b. "Voy bien, la tengo casi lista"
ante un pedido de estado: Leda anota el avance con las palabras de la persona (atribuido y
auditado, sin cambiar estado ni fecha), la espera sigue abierta y al día hábil siguiente vuelve
a pedir el estado. Esa respuesta no es silencio: la escalera cuenta sólo los pedidos sin
respuesta, así que el escalamiento o su aviso no salen por ella. A la segunda respuesta sin nada
cierto, Leda pregunta para cuándo; con una fecha, es una nueva previsión.

El reloj se mueve por días como en `test_escalera.py`: la tarea "Revisar el tablero" de Marcos
vence el viernes 9 de octubre de 2026 y el lunes 12 es feriado. La IA es guionada.
"""

from __future__ import annotations

from datetime import datetime

from prueba_chica.escalera import correr_escalera
from prueba_chica.fichas import GUARDADO_SIN_ENVIAR
from prueba_chica.ia import IAGuionada, Jugada
from prueba_chica.test_avisos import _hora
from prueba_chica.test_escalera import (  # noqa: F401 (las fixtures se usan por su nombre)
    _avisos, _espera, _para, dias, espacio_con_escalera)
from prueba_chica.test_situaciones import T1, _cuantas, _todos, _uno
from prueba_chica.tiempo import RelojFijo
from prueba_chica.turno import procesar_turno

VAGO = "voy bien, la tengo casi lista"
OTRA_VEZ_VAGO = "todo en orden, sigo con eso"


def _escribe(conn, escribe, texto: str, *jugadas: Jugada, at: datetime):
    quien, entrante = escribe("Marcos", texto, at=at)
    resultado = procesar_turno(conn, quien, entrante,
                               IAGuionada(jugadas=[list(jugadas)], redacciones=["Listo."]),
                               RelojFijo(at))
    conn.commit()
    assert resultado.error is None
    return resultado


def _avance(texto: str) -> Jugada:
    return Jugada("informar_avance", {"tarea": "T1", "palabras": texto})


def _repreguntas(conn) -> list[dict]:
    return _avisos(conn, "repregunta_de_estado")


# --- La primera respuesta sin nada cierto -----------------------------------------------------

def test_un_avance_se_anota_con_sus_palabras_y_la_espera_sigue_abierta(conn, mundo, dias,
                                                                       escribe):
    dias.ciclo(_hora(9, 10))                                    # el primer pedido de estado

    resultado = _escribe(conn, escribe, VAGO, _avance(VAGO), at=_hora(9, 10, 30))

    [hecho] = resultado.hechos
    sale = hecho.pop("vuelve_a_pedir_el_estado")
    assert hecho == {"jugada": "informar_avance", "resultado": "anotado", "tarea": T1,
                     "avance": {"dijo": VAGO}, "el_pedido_de_estado": "sigue_abierto",
                     "veces_sin_algo_cierto": 1}
    # Un efecto que pasa después, con su estado: el día hábil siguiente (el lunes es feriado).
    assert sale["estado"] == GUARDADO_SIN_ENVIAR
    assert datetime.fromisoformat(sale["sale"]) == _hora(13, 9)
    assert resultado.pregunta is None                           # la primera vez, no pregunta
    # Ni estado, ni fecha, ni previsión, ni aviso a Ismael.
    assert str(_uno(conn, "select estado from task")["estado"]) == "asignada"
    assert _cuantas(conn, "task_forecast") == 0
    assert _cuantas(conn, "scheduled_notice", "tipo = 'nueva_prevision'") == 0
    # La espera sigue abierta; la pregunta de hoy quedó contestada con el avance.
    assert _espera(conn)["satisfecho_en"] is None
    pregunta = _uno(conn, """select cierre, cierre_detalle from conversation_question
                              where tipo = 'estado_de_la_tarea'""")
    assert pregunta["cierre"] == "respondida"
    assert pregunta["cierre_detalle"]["jugada"] == "informar_avance"
    # Atribuido y auditado, con las palabras tal cual.
    registro = _uno(conn, "select * from audit_log where accion = 'informar_avance'")
    assert registro["actor_kind"] == "persona"
    assert str(registro["actor_app_user_id"]) == mundo["personas"]["Marcos"]["app_user_id"]
    assert (registro["sujeto_tipo"], str(registro["sujeto_id"])) == ("task", mundo["tarea"])
    assert registro["detalle"]["dijo"] == VAGO
    # El pedido del día hábil siguiente, guardado y sin turno: lo manda Leda por su cuenta.
    [repregunta] = _repreguntas(conn)
    assert repregunta["estado"] == "guardado" and repregunta["turno_id"] is None
    assert repregunta["programado_para"] == _hora(13, 9)


def test_sin_un_pedido_de_estado_no_hay_avance_que_anotar(conn, mundo, dias, escribe):
    """La ficha comprueba que Leda haya pedido el estado: sin una espera ni una pregunta
    abierta, no se anota nada ni se guarda un pedido."""
    resultado = _escribe(conn, escribe, VAGO, _avance(VAGO), at=_hora(6, 11))

    assert resultado.hechos == [{"jugada": "informar_avance", "resultado": "no_se_puede",
                                 "motivo": "nadie_pidio_el_estado", "tarea": T1}]
    assert _cuantas(conn, "audit_log", "accion = 'informar_avance'") == 0
    assert _repreguntas(conn) == []


def test_sin_las_palabras_de_la_ia_queda_el_mensaje_de_la_persona(conn, mundo, dias, escribe):
    dias.ciclo(_hora(9, 10))

    resultado = _escribe(conn, escribe, VAGO, Jugada("informar_avance", {"tarea": "T1"}),
                         at=_hora(9, 10, 30))

    assert resultado.hechos[0]["avance"] == {"dijo": VAGO}


# --- La escalera escala sólo el silencio --------------------------------------------------------

def test_un_avance_no_es_silencio_la_escalera_vuelve_a_preguntar_sin_escalar(conn, mundo, dias,
                                                                            escribe):
    """Conversación 15, pasos 1 a 4: el avance llega después del pedido que avisa que se va a
    escalar. Al día siguiente, en lugar del escalamiento, Leda vuelve a pedir el estado, sin
    avisar que va a escalar: la cuenta de pedidos sin respuesta empieza de nuevo. Si tampoco
    contesta ése, es silencio y la escalera sigue desde ahí."""
    for dia in (9, 13):
        dias.ciclo(_hora(dia, 10))
    [tercero] = dias.ciclo(_hora(14, 10))
    assert tercero["hechos"][0]["si_no_hay_respuesta"]["se_avisa_a"] == ["Ismael"]
    _escribe(conn, escribe, VAGO, _avance(VAGO), at=_hora(14, 10, 30))

    [otra_vez] = dias.ciclo(_hora(15, 10))

    assert otra_vez["persona"] == "Marcos"
    hechos = otra_vez["hechos"][0]
    assert hechos["aviso"] == "repregunta_de_estado" and hechos["necesita_respuesta"] is True
    assert hechos["avance_anterior"] == {"dijo": VAGO, "el": "2026-10-14"}
    assert hechos["espera_algo_cierto"] == ["si_la_termino", "para_cuando_la_termina",
                                            "si_esta_trabada"]
    assert "si_no_hay_respuesta" not in hechos
    assert otra_vez["pregunta"]["tipo"] == "estado_de_la_tarea"
    assert _para(conn, mundo, "Ismael") == []                   # no escaló
    assert _avisos(conn, "escalamiento") == []

    # Sin respuesta a la repregunta: el silencio cuenta de nuevo, un paso por día hábil.
    [segundo] = dias.ciclo(_hora(16, 10))
    assert segundo["hechos"][0]["aviso"] == "pedido_de_estado"
    assert segundo["hechos"][0]["numero"] == 2
    assert "si_no_hay_respuesta" not in segundo["hechos"][0]
    [tercero] = dias.ciclo(_hora(19, 10))
    assert tercero["hechos"][0]["numero"] == 3
    assert tercero["hechos"][0]["si_no_hay_respuesta"]["se_avisa_a"] == ["Ismael"]

    [escalamiento] = dias.ciclo(_hora(20, 10))

    assert escalamiento["persona"] == "Ismael"
    hechos = escalamiento["hechos"][0]
    assert hechos["pedidos_de_estado_sin_respuesta"] == 3
    assert hechos["pedido_desde"] == "2026-10-15"
    # Honesto: Marcos sí contestó antes, sin nada cierto.
    assert hechos["avance_sin_algo_cierto"] == {"dijo": VAGO, "el": "2026-10-14"}


def test_un_escalamiento_guardado_no_sale_si_llega_un_avance(conn, mundo, dias, escribe):
    """El escalamiento quedó guardado antes del horario y Marcos contesta antes de que salga:
    no sale (ya no es silencio) y lo reemplaza el pedido del día hábil siguiente."""
    for dia in (9, 13, 14):
        dias.ciclo(_hora(dia, 10))
    correr_escalera(conn, mundo["id"], RelojFijo(_hora(15, 7)))
    conn.commit()
    [escalamiento] = _avisos(conn, "escalamiento")
    assert escalamiento["estado"] == "guardado"

    _escribe(conn, escribe, VAGO, _avance(VAGO), at=_hora(15, 8))

    assert dias.ciclo(_hora(15, 10)) == []
    [escalamiento] = _avisos(conn, "escalamiento")
    assert (escalamiento["estado"], escalamiento["motivo_omision"]) == (
        "omitido", "reemplazado_por_un_avance")
    [otra_vez] = dias.ciclo(_hora(16, 10))
    assert otra_vez["hechos"][0]["aviso"] == "repregunta_de_estado"
    assert _para(conn, mundo, "Ismael") == []


# --- La segunda respuesta sin nada cierto: pregunta para cuándo ---------------------------------

def test_a_la_segunda_pregunta_la_fecha_y_con_la_fecha_es_una_prevision(conn, mundo, dias,
                                                                       escribe):
    """Conversación 15, pasos 4 a 7."""
    dias.ciclo(_hora(9, 10))
    _escribe(conn, escribe, VAGO, _avance(VAGO), at=_hora(9, 10, 30))
    [otra_vez] = dias.ciclo(_hora(13, 10))
    assert otra_vez["hechos"][0]["aviso"] == "repregunta_de_estado"

    resultado = _escribe(conn, escribe, OTRA_VEZ_VAGO, _avance(OTRA_VEZ_VAGO),
                         at=_hora(13, 10, 40))

    [hecho] = resultado.hechos
    assert hecho["veces_sin_algo_cierto"] == 2 and hecho["pregunta"] == "fecha_de_la_tarea"
    assert hecho["vuelve_a_pedir_el_estado"]["estado"] == GUARDADO_SIN_ENVIAR
    assert resultado.pregunta["tipo"] == "fecha_de_la_tarea"   # la única de la respuesta
    assert resultado.pregunta["tarea"] == T1
    assert _espera(conn)["satisfecho_en"] is None
    assert [r["estado"] for r in _repreguntas(conn)] == ["enviado", "guardado"]

    con_fecha = _escribe(conn, escribe, "para el martes 20 la tengo",
                         Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-20"}),
                         at=_hora(13, 10, 45))

    assert con_fecha.hechos[0]["resultado"] == "anotado"
    assert con_fecha.pregunta is None
    assert _espera(conn)["satisfecho_en"] == _hora(13, 10, 45)
    assert _cuantas(conn, "conversation_question", "cerrada_en is null") == 0
    # El pedido guardado no sale, con su motivo, y nada más hasta la previsión (9i).
    for dia in (14, 15, 16, 19):
        assert [p for p in dias.ciclo(_hora(dia, 10)) if p["persona"] == "Marcos"] == []
    assert (_repreguntas(conn)[-1]["estado"], _repreguntas(conn)[-1]["motivo_omision"]) == (
        "omitido", "ya_respondio")
    assert _avisos(conn, "escalamiento") == []
    # El día de la previsión, el pedido de estado de su escalera.
    [f] = [p for p in dias.ciclo(_hora(20, 10)) if p["persona"] == "Marcos"]
    assert (f["hechos"][0]["numero"], f["hechos"][0]["seguimiento_por"]) == (1, "prevision")


def test_dos_avances_el_mismo_dia_dejan_un_solo_pedido_para_manana(conn, mundo, dias, escribe):
    """El segundo reemplaza al pedido guardado por el primero (nunca dos pedidos el mismo día) y
    pregunta para cuándo. Al día siguiente, el pedido del estado reemplaza a la pregunta de la
    fecha, que se cierra sin efecto: un tema a la vez."""
    dias.ciclo(_hora(9, 10))
    _escribe(conn, escribe, VAGO, _avance(VAGO), at=_hora(9, 10, 30))

    resultado = _escribe(conn, escribe, OTRA_VEZ_VAGO, _avance(OTRA_VEZ_VAGO),
                         at=_hora(9, 11))

    assert resultado.pregunta["tipo"] == "fecha_de_la_tarea"
    estados = [(r["estado"], r["motivo_omision"]) for r in _repreguntas(conn)]
    assert estados == [("omitido", "reemplazado_por_un_avance"), ("guardado", None)]

    [otra_vez] = dias.ciclo(_hora(13, 10))

    assert otra_vez["hechos"][0]["avance_anterior"]["dijo"] == OTRA_VEZ_VAGO
    abiertas = _todos(conn, """select tipo from conversation_question
                                where cerrada_en is null""")
    assert abiertas == [{"tipo": "estado_de_la_tarea"}]
    fecha = _uno(conn, """select cierre from conversation_question
                           where tipo = 'fecha_de_la_tarea'""")
    assert fecha["cierre"] == "sin_efecto"
    # Sin respuesta, el silencio cuenta desde el pedido que sí salió.
    [segundo] = dias.ciclo(_hora(14, 10))
    assert segundo["hechos"][0]["numero"] == 2
