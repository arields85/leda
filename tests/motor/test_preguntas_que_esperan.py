"""Las preguntas que esperan respuesta y lo que Leda propone (decisiones del usuario, 2026-10-05).

Hallazgos de la corrida en seco de la E2-7 (`odd/tasks/prueba-chica-del-motor.md`), resueltos
como reglas generales y no para una pregunta:

- **Una pregunta cuya ficha dice que espera respuesta abre una espera** (`pending_reply`) y, si
  no llega la respuesta, la escalera la repite: el día hábil siguiente, otra vez al otro avisando
  a quién se va a escalar, y al siguiente escala (ADR 0018, 9b y 9c; conversación 03, pasos 2 a
  4). No se puede dejar sin efecto. La de quién destraba es una de ellas.
- **Todo lo que Leda le propone a la persona queda como tema abierto** (ADR 0013: la pregunta
  pendiente es el contexto): las salidas de un bloqueo (conversación 03, paso 5) y la previsión
  que ofrece en lugar de una reasignación (conversación 12, paso 2). Se contesta haciendo una de
  las cosas propuestas, se puede cancelar, y sigue la regla de un tema a la vez.

El reloj de la escalera es el de `test_escalera.py`: la tarea "Revisar el tablero" (T1) de Marcos
vence el viernes 9 de octubre de 2026; el bloqueo se anota el lunes 5.

Portadas de `prueba_chica/test_preguntas_que_esperan.py`; la primera está en `test_preguntas.py`.
"""

from __future__ import annotations

from leda.motor import preguntas
from leda.motor.escalera import correr_escalera
from leda.motor.ia import Jugada
from leda.motor.tiempo import RelojFijo

from tests.motor.ayudantes import (T1, abierta, avisos_guardados, cuantas, dice, jugada_bloqueo,
                                   octubre, todos)


QUIEN_DESTRABA = "quien_destraba"


def _esperas(conn, tipo: str) -> list[dict]:
    return todos(conn, "select * from pending_reply where tipo = %s order by preguntado_en",
                 tipo)


# --- Una pregunta que espera respuesta ---------------------------------------------------------


def test_la_pregunta_de_quien_destraba_abre_una_espera(conn, tareas, marcos):
    marcos.dice(jugada_bloqueo("T1", "falta el repuesto"))

    [espera] = _esperas(conn, QUIEN_DESTRABA)
    assert str(espera["task_id"]) == tareas["T1"] and espera["satisfecho_en"] is None


def test_sin_respuesta_la_pregunta_se_repite_y_sigue_la_escalera_hasta_escalar(
        conn, tareas, marcos, dias):
    marcos.dice(jugada_bloqueo("T1", "falta el repuesto"))    # lunes 5, 10:00

    # El mismo día, sólo la repetición del día, a las 4 horas (decisión 29 del usuario).
    [repeticion] = dias.ciclo(octubre(5, 16))
    assert repeticion["hechos"][0]["aviso"] == "repeticion_del_dia"
    assert dias.ciclo(octubre(5, 16, 30)) == []

    [otra_vez] = dias.ciclo(octubre(6, 10))
    hechos = otra_vez["hechos"][0]
    assert otra_vez["persona"] == "Marcos"
    assert (hechos["aviso"], hechos["pregunta"], hechos["numero"]) == (
        "repregunta", QUIEN_DESTRABA, 2)
    assert hechos["sobre"] == {"jugada": "anotar_bloqueo", "causa": "falta el repuesto"}
    assert hechos["necesita_respuesta"] is True and "si_no_hay_respuesta" not in hechos
    assert otra_vez["pregunta"]["tipo"] == QUIEN_DESTRABA
    assert abierta(conn) == (QUIEN_DESTRABA, tareas["T1"])

    [tercera] = dias.ciclo(octubre(7, 10))
    assert tercera["hechos"][0]["numero"] == 3
    assert tercera["hechos"][0]["si_no_hay_respuesta"] == {"se_avisa_a": ["Ismael"]}

    [escalamiento] = dias.ciclo(octubre(8, 10))
    hechos = escalamiento["hechos"][0]
    assert escalamiento["persona"] == "Ismael"
    assert (hechos["aviso"], hechos["pregunta"], hechos["responsable"]) == (
        "falta_de_respuesta", QUIEN_DESTRABA, "Marcos")
    assert hechos["preguntas_sin_respuesta"] == 3

    assert dias.ciclo(octubre(9, 10)) == []                   # terminó al escalar
    [espera] = _esperas(conn, QUIEN_DESTRABA)
    assert espera["escalado_en"] is not None and espera["satisfecho_en"] is None


def test_la_respuesta_cierra_la_espera_y_la_escalera_de_la_pregunta(conn, tareas, marcos, dias,
                                                                   escribe):
    marcos.dice(jugada_bloqueo("T1", "falta el repuesto"))
    [_] = dias.ciclo(octubre(6, 10))

    dice(conn, escribe, Jugada("anotar_quien_destraba", {"no_sabe": True}), at=octubre(6, 11))

    [espera] = _esperas(conn, QUIEN_DESTRABA)
    assert espera["satisfecho_en"] is not None
    for dia in (7, 8, 9):
        assert dias.ciclo(octubre(dia, 10)) == []


def test_una_repregunta_guardada_no_sale_si_ya_se_contesto(conn, mundo, tareas, marcos, dias,
                                                           escribe):
    marcos.dice(jugada_bloqueo("T1", "falta el repuesto"))
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(6, 9)))   # guardada, sin salir
    conn.commit()
    dice(conn, escribe, Jugada("anotar_quien_destraba", {"quien": "Ismael"}), at=octubre(6, 9, 30))

    # A Marcos no le sale nada. A Ismael, que lo destraba, Leda le pregunta para cuándo (C-5,
    # `test_persecucion.py`).
    assert [p["persona"] for p in dias.ciclo(octubre(6, 10))] == ["Ismael"]
    [guardada] = avisos_guardados(conn, "repregunta")
    assert (guardada["estado"], guardada["motivo_omision"]) == ("omitido", "ya_respondio")


# --- Lo que Leda propone queda como tema abierto -------------------------------------------------

def test_las_salidas_de_un_bloqueo_quedan_como_tema_abierto(conn, tareas, marcos):
    marcos.dice(jugada_bloqueo("T1", "falta el repuesto"))

    r = marcos.dice(Jugada("anotar_quien_destraba", {"no_sabe": True}))

    assert r.hechos[0]["salidas"] == ["que_alguien_ayude", "anotar_prevision"]
    assert r.pregunta == {"tipo": preguntas.PROPUESTA, "tarea": T1,
                          "propone": ["que_alguien_ayude", "anotar_prevision"],
                          "desde_antes": False}
    assert abierta(conn) == (preguntas.PROPUESTA, tareas["T1"])
    # La situación de la IA en el mensaje siguiente la trae como contexto.
    marcos.dice(Jugada("cancelar"))
    assert marcos.situacion["estado"]["pregunta_abierta"] == {
        "tipo": preguntas.PROPUESTA, "tarea": "T1",
        "propone": ["que_alguien_ayude", "anotar_prevision"]}


def test_lo_propuesto_se_puede_cancelar(conn, tareas, marcos):
    marcos.dice(jugada_bloqueo("T1", "falta el repuesto"))
    marcos.dice(Jugada("anotar_quien_destraba", {"no_sabe": True}))

    r = marcos.dice(Jugada("cancelar"))

    assert r.hechos[0]["resultado"] == "cancelado"
    assert r.pregunta is None and abierta(conn) is None
    assert cuantas(conn, "blocker", "resuelto_en is null") == 1     # el bloqueo sigue


def _sin_quien_destrabe(marcos) -> None:
    """Marcos se traba con la T1 y no sabe quién la destraba: Leda le propone salidas."""
    marcos.dice(jugada_bloqueo("T1", "falta el repuesto"))
    r = marcos.dice(Jugada("anotar_quien_destraba", {"tarea": "T1", "no_sabe": True}))
    assert "anotar_prevision" in r.hechos[0]["salidas"]


def test_lo_propuesto_se_contesta_haciendolo(conn, tareas, marcos):
    # Lo que Leda propone cuando nadie más destraba un bloqueo (9c); hasta la C-7, la previsión
    # que ofrecía en lugar de pasar la tarea a otra persona.
    _sin_quien_destrabe(marcos)
    assert abierta(conn) == (preguntas.PROPUESTA, tareas["T1"])

    r = marcos.dice(Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-14",
                                                "motivo": "el proveedor"}))

    assert r.hechos[0]["resultado"] == "anotado"
    assert r.pregunta is None and abierta(conn) is None
    [cerrada] = todos(conn, "select cierre from conversation_question where tipo = %s",
                      preguntas.PROPUESTA)
    assert cerrada["cierre"] == "respondida"


def test_lo_propuesto_sigue_la_regla_de_un_tema_a_la_vez(conn, tareas, marcos):
    _sin_quien_destrabe(marcos)

    r = marcos.dice(jugada_bloqueo("T2"))     # lo nuevo también pregunta: Leda sigue a Marcos

    assert r.pregunta["tipo"] == "causa_del_bloqueo"
    assert todos(conn, """select tipo from conversation_question
                            where cerrada_en is null and para_despues_en is not null""") == [
        {"tipo": preguntas.PROPUESTA}]
