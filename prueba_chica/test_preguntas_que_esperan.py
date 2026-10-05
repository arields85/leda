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
"""

from __future__ import annotations

from prueba_chica import preguntas
from prueba_chica.ia import Jugada
from prueba_chica.test_avisos import _dice, _hora
from prueba_chica.test_escalera import (  # noqa: F401 (las fixtures se usan por su nombre)
    _avisos, dias, espacio_con_escalera)
from prueba_chica.test_situaciones import (  # noqa: F401
    T1, _abierta, _bloqueo, _cuantas, _todos, marcos, tareas)

QUIEN_DESTRABA = "quien_destraba"


def _esperas(conn, tipo: str) -> list[dict]:
    return _todos(conn, "select * from pending_reply where tipo = %s order by preguntado_en",
                  tipo)


# --- Una pregunta que espera respuesta ---------------------------------------------------------

def test_cada_ficha_de_pregunta_dice_si_espera_respuesta():
    espera = {t.nombre: t.espera for t in preguntas.TIPOS.values()}
    assert espera[QUIEN_DESTRABA] == QUIEN_DESTRABA
    assert espera[preguntas.ESTADO_DE_LA_TAREA] == preguntas.ESTADO_DE_LA_TAREA
    # La fecha es parte del pedido de estado: espera con él.
    assert espera[preguntas.FECHA_DE_LA_TAREA] == preguntas.ESTADO_DE_LA_TAREA
    for se_deja in (preguntas.CUAL_TAREA, "causa_del_bloqueo", preguntas.PROPUESTA):
        assert espera[se_deja] is None


def test_la_pregunta_de_quien_destraba_abre_una_espera(conn, tareas, marcos):
    marcos.dice(_bloqueo("T1", "falta el repuesto"))

    [espera] = _esperas(conn, QUIEN_DESTRABA)
    assert str(espera["task_id"]) == tareas["T1"] and espera["satisfecho_en"] is None


def test_sin_respuesta_la_pregunta_se_repite_y_sigue_la_escalera_hasta_escalar(
        conn, tareas, marcos, dias):
    marcos.dice(_bloqueo("T1", "falta el repuesto"))          # lunes 5, 10:00

    assert dias.ciclo(_hora(5, 16)) == []                     # el mismo día, nada

    [otra_vez] = dias.ciclo(_hora(6, 10))
    hechos = otra_vez["hechos"][0]
    assert otra_vez["persona"] == "Marcos"
    assert (hechos["aviso"], hechos["pregunta"], hechos["numero"]) == (
        "repregunta", QUIEN_DESTRABA, 2)
    assert hechos["sobre"] == {"jugada": "anotar_bloqueo", "causa": "falta el repuesto"}
    assert hechos["necesita_respuesta"] is True and "si_no_hay_respuesta" not in hechos
    assert otra_vez["pregunta"]["tipo"] == QUIEN_DESTRABA
    assert _abierta(conn) == (QUIEN_DESTRABA, tareas["T1"])

    [tercera] = dias.ciclo(_hora(7, 10))
    assert tercera["hechos"][0]["numero"] == 3
    assert tercera["hechos"][0]["si_no_hay_respuesta"] == {"se_avisa_a": ["Ismael"],
                                                           "estado": "todavia_no"}

    [escalamiento] = dias.ciclo(_hora(8, 10))
    hechos = escalamiento["hechos"][0]
    assert escalamiento["persona"] == "Ismael"
    assert (hechos["aviso"], hechos["pregunta"], hechos["responsable"]) == (
        "falta_de_respuesta", QUIEN_DESTRABA, "Marcos")
    assert hechos["preguntas_sin_respuesta"] == 3

    assert dias.ciclo(_hora(9, 10)) == []                     # terminó al escalar
    [espera] = _esperas(conn, QUIEN_DESTRABA)
    assert espera["escalado_en"] is not None and espera["satisfecho_en"] is None


def test_la_respuesta_cierra_la_espera_y_la_escalera_de_la_pregunta(conn, tareas, marcos, dias,
                                                                   escribe):
    marcos.dice(_bloqueo("T1", "falta el repuesto"))
    [_] = dias.ciclo(_hora(6, 10))

    _dice(conn, escribe, Jugada("anotar_quien_destraba", {"no_sabe": True}), at=_hora(6, 11))

    [espera] = _esperas(conn, QUIEN_DESTRABA)
    assert espera["satisfecho_en"] is not None
    for dia in (7, 8, 9):
        assert dias.ciclo(_hora(dia, 10)) == []


def test_una_repregunta_guardada_no_sale_si_ya_se_contesto(conn, mundo, tareas, marcos, dias,
                                                           escribe):
    from prueba_chica.escalera import correr_escalera
    from prueba_chica.tiempo import RelojFijo

    marcos.dice(_bloqueo("T1", "falta el repuesto"))
    correr_escalera(conn, mundo["id"], RelojFijo(_hora(6, 9)))     # guardada, sin salir
    conn.commit()
    _dice(conn, escribe, Jugada("anotar_quien_destraba", {"quien": "Ismael"}), at=_hora(6, 9, 30))

    assert dias.ciclo(_hora(6, 10)) == []
    [guardada] = _avisos(conn, "repregunta")
    assert (guardada["estado"], guardada["motivo_omision"]) == ("omitido", "ya_respondio")


# --- Lo que Leda propone queda como tema abierto -------------------------------------------------

def test_las_salidas_de_un_bloqueo_quedan_como_tema_abierto(conn, tareas, marcos):
    marcos.dice(_bloqueo("T1", "falta el repuesto"))

    r = marcos.dice(Jugada("anotar_quien_destraba", {"no_sabe": True}))

    assert r.hechos[0]["salidas"] == ["que_alguien_ayude", "anotar_prevision"]
    assert r.pregunta == {"tipo": preguntas.PROPUESTA, "tarea": T1,
                          "propone": ["que_alguien_ayude", "anotar_prevision"],
                          "desde_antes": False}
    assert _abierta(conn) == (preguntas.PROPUESTA, tareas["T1"])
    # La situación de la IA en el mensaje siguiente la trae como contexto.
    marcos.dice(Jugada("cancelar"))
    assert marcos.situacion["estado"]["pregunta_abierta"] == {
        "tipo": preguntas.PROPUESTA, "tarea": "T1",
        "propone": ["que_alguien_ayude", "anotar_prevision"]}


def test_lo_propuesto_se_puede_cancelar(conn, tareas, marcos):
    marcos.dice(_bloqueo("T1", "falta el repuesto"))
    marcos.dice(Jugada("anotar_quien_destraba", {"no_sabe": True}))

    r = marcos.dice(Jugada("cancelar"))

    assert r.hechos[0]["resultado"] == "cancelado"
    assert r.pregunta is None and _abierta(conn) is None
    assert _cuantas(conn, "blocker", "resuelto_en is null") == 1    # el bloqueo sigue


def test_lo_propuesto_se_contesta_haciendolo(conn, tareas, marcos):
    r = marcos.dice(Jugada("pedir_reasignacion", {"tarea": "T1", "a": "nahuel"}))
    assert r.hechos[0]["alternativa"] == "anotar_prevision"
    assert _abierta(conn) == (preguntas.PROPUESTA, tareas["T1"])

    r = marcos.dice(Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-14"}))

    assert r.hechos[0]["resultado"] == "anotado"
    assert r.pregunta is None and _abierta(conn) is None
    [cerrada] = _todos(conn, "select cierre from conversation_question where tipo = %s",
                       preguntas.PROPUESTA)
    assert cerrada["cierre"] == "respondida"


def test_lo_propuesto_sigue_la_regla_de_un_tema_a_la_vez(conn, tareas, marcos):
    marcos.dice(Jugada("pedir_reasignacion", {"tarea": "T1", "a": "nahuel"}))

    r = marcos.dice(_bloqueo("T2"))           # lo nuevo también pregunta: Leda sigue a Marcos

    assert r.pregunta["tipo"] == "causa_del_bloqueo"
    assert _todos(conn, """select tipo from conversation_question
                            where cerrada_en is null and para_despues_en is not null""") == [
        {"tipo": preguntas.PROPUESTA}]
