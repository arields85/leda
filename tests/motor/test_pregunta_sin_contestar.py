"""Una pregunta de Leda sin contestar (`leda.motor.pregunta_sin_contestar`; decisión 21 del
usuario, 2026-10-08; conversación 30).

Del `PENDIENTE` de la D5: con la regla de un tema a la vez, una pregunta que nunca se contestaba
frenaba para siempre los avisos que piden respuesta. La regla, para todas las preguntas y todos
los circuitos:

1. la pregunta frena los otros temas que piden respuesta hasta que Leda la repite, una sola vez en
   el día, a las 4 horas de haberla hecho (o los minutos del espacio), haya o no otro tema
   esperando (decisión 29 del usuario, 2026-10-09);
2. 4 horas después de la repetición, todavía en horario, sale aparte el tema siguiente más
   urgente, y la pregunta queda para después;
3. la persona contesta cualquiera de las dos, y al cerrarse una el código trae la otra enseguida,
   en un mensaje aparte;
4. al día siguiente la pregunta de ayer ya no frena: lo que espera sale de a uno, primero lo más
   urgente;
5. la pregunta que quedó por un cambio de tema vuelve en un mensaje aparte, justo después de la
   respuesta (decisión 50 del usuario, 2026-10-09): un mensaje, un tema.

El reloj es el de `test_escalera.py`: "Revisar el tablero" (T1) vence el viernes 9 de octubre de
2026 y "Probar las comunicaciones" (T2), el viernes 16; el lunes 12 es feriado.
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from leda.db import admin, espacio
from leda.motor import preguntas
from leda.motor.hechos import significado
from leda.motor.ia import Jugada
from leda.motor.pregunta_sin_contestar import (CLAVE, ESPERA_POR_OMISION, REPETICION_DEL_DIA,
                                               VUELVE_LA_PREGUNTA, espera_para_repetir,
                                               termino_su_turno)
from leda.calendario import Calendario

from tests.motor.ayudantes import (Dias, abierta, avisos_guardados, dice, jugada_bloqueo,
                                   nueva_tarea, octubre, todos)


@pytest.fixture
def dos(conn, mundo, espacio_con_escalera) -> dict[str, str]:
    """Las dos tareas de Marcos: T1 vence el viernes 9 y T2, en curso, el viernes 16."""
    return {"T1": mundo["tarea"],
            "T2": nueva_tarea(conn, mundo, "Probar las comunicaciones", estado="en_curso")}


def _tareas(pedido: dict) -> list[str]:
    return [h["tarea"] for h in pedido["hechos"]]


def _para_despues(conn) -> list[tuple[str, str | None]]:
    return [(q["tipo"], str(q["task_id"]) if q["task_id"] else None)
            for q in todos(conn, """select tipo, task_id from conversation_question
                                     where cerrada_en is null and para_despues_en is not null
                                     order by abierta_en""")]


def _trabada_a_las(conn, escribe, dias: Dias, at) -> None:
    """Marcos dice que T2 está trabada: Leda le pregunta quién la puede destrabar."""
    dice(conn, escribe, jugada_bloqueo("T2", "falta el cable"), at=at)
    assert abierta(conn)[0] == preguntas.QUIEN_DESTRABA


def _las_dos_abiertas(conn, escribe, dias: Dias, dos) -> None:
    """El viernes 9: la pregunta de T2 a las 08:55, el pedido de estado de T1 esperando desde las
    10:00, la repetición a las 12:55 y, a las 16:55, el pedido de T1 aparte."""
    _trabada_a_las(conn, escribe, dias, octubre(9, 8, 55))
    assert dias.ciclo(octubre(9, 10)) == []
    assert dias.ciclo(octubre(9, 12, 55)) != []
    assert dias.ciclo(octubre(9, 16, 55)) != []
    assert abierta(conn) == (preguntas.ESTADO_DE_LA_TAREA, dos["T1"])


# --- Cuánto espera -----------------------------------------------------------------------------

def _configurar(conn, mundo, valor: str) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, %s, %s)""", (mundo["id"], CLAVE, valor))
    conn.commit()


def _espera(conn, mundo) -> timedelta:
    with espacio(conn, mundo["id"]) as cur:
        espera = espera_para_repetir(cur, mundo["id"])
    conn.commit()
    return espera


def test_sin_configurar_espera_cuatro_horas(conn, mundo):
    assert ESPERA_POR_OMISION == timedelta(hours=4)
    assert _espera(conn, mundo) == timedelta(hours=4)


@pytest.mark.parametrize("valor, minutos", [("120", 120), ("300", 300)])
def test_el_espacio_cambia_cuanto_espera(conn, mundo, valor, minutos):
    _configurar(conn, mundo, valor)
    assert _espera(conn, mundo) == timedelta(minutes=minutos)


@pytest.mark.parametrize("valor", ['"cuatro"', "-5", "0", "true", "null"])
def test_un_valor_que_no_vale_usa_el_del_producto(conn, mundo, valor):
    """0 no vale: una pregunta repetida al instante no es una repetición."""
    _configurar(conn, mundo, valor)
    assert _espera(conn, mundo) == ESPERA_POR_OMISION


# --- 1. La repetición del día ------------------------------------------------------------------

def test_con_un_tema_esperando_la_repite_a_las_cuatro_horas_una_vez(conn, mundo, escribe, dos):
    dias = Dias(conn, mundo)
    _trabada_a_las(conn, escribe, dias, octubre(9, 8, 55))
    assert dias.ciclo(octubre(9, 10)) == []                 # el pedido de T1 espera
    assert dias.ciclo(octubre(9, 12, 54)) == []
    [repeticion] = dias.ciclo(octubre(9, 12, 55))
    assert _tareas(repeticion) == ["Probar las comunicaciones"]
    assert repeticion["pregunta"]["tipo"] == preguntas.QUIEN_DESTRABA
    assert repeticion["hechos"][0]["aviso"] == REPETICION_DEL_DIA
    assert dias.ciclo(octubre(9, 16, 54)) == []             # una sola vez en el día
    assert len(avisos_guardados(conn, REPETICION_DEL_DIA)) == 1
    assert abierta(conn) == (preguntas.QUIEN_DESTRABA, dos["T2"])


def test_sin_nada_esperando_tambien_la_repite_a_las_cuatro_horas(conn, mundo, escribe, dos):
    """Decisión 29 del usuario (2026-10-09, opción B): la repetición sale haya o no otro tema
    esperando ("si no tiene nada esperando, con más sentido tendría que repetírsela")."""
    dias = Dias(conn, mundo)
    _trabada_a_las(conn, escribe, dias, octubre(5, 8, 55))  # el lunes 5 no vence nada
    assert dias.ciclo(octubre(5, 10)) == []
    assert dias.ciclo(octubre(5, 12, 54)) == []
    [repeticion] = dias.ciclo(octubre(5, 12, 55))
    assert repeticion["hechos"][0]["aviso"] == REPETICION_DEL_DIA
    assert repeticion["pregunta"]["tipo"] == preguntas.QUIEN_DESTRABA
    assert _tareas(repeticion) == ["Probar las comunicaciones"]
    assert dias.ciclo(octubre(5, 16, 59)) == []             # una sola vez en el día
    assert len(avisos_guardados(conn, REPETICION_DEL_DIA)) == 1


def test_una_pregunta_que_vuelve_en_una_respuesta_cuenta_las_cuatro_horas_desde_ahi(
        conn, mundo, escribe, dos):
    """Lo que la persona escribe sobre la pregunta la vuelve a hacer en la respuesta: las 4
    horas de la repetición cuentan desde ahí, así que nunca interrumpe esa conversación."""
    dias = Dias(conn, mundo)
    _trabada_a_las(conn, escribe, dias, octubre(5, 8, 55))
    dice(conn, escribe, at=octubre(5, 12, 40))              # un mensaje sin jugada
    assert dias.ciclo(octubre(5, 12, 55)) == []
    assert dias.ciclo(octubre(5, 16, 39)) == []
    [repeticion] = dias.ciclo(octubre(5, 16, 40))
    assert repeticion["hechos"][0]["aviso"] == REPETICION_DEL_DIA


def test_fuera_del_horario_la_repeticion_no_sale(conn, mundo, escribe, dos):
    """La pregunta a las 14:00: las 4 horas caen fuera del horario; ese día no se repite y al
    día hábil siguiente sigue su escalera."""
    dias = Dias(conn, mundo)
    _trabada_a_las(conn, escribe, dias, octubre(5, 14))
    assert dias.ciclo(octubre(5, 16, 59)) == []
    assert avisos_guardados(conn, REPETICION_DEL_DIA) == []


# --- 2. El tema siguiente ------------------------------------------------------------------------

def test_cuatro_horas_despues_de_la_repeticion_sale_aparte_el_tema_siguiente(conn, mundo,
                                                                             escribe, dos):
    dias = Dias(conn, mundo)
    _trabada_a_las(conn, escribe, dias, octubre(9, 8, 55))
    dias.ciclo(octubre(9, 10))
    dias.ciclo(octubre(9, 12, 55))
    assert dias.ciclo(octubre(9, 16, 54)) == []
    [pedido] = dias.ciclo(octubre(9, 16, 55))
    assert _tareas(pedido) == ["Revisar el tablero"]
    assert pedido["pregunta"]["tipo"] == preguntas.ESTADO_DE_LA_TAREA
    assert abierta(conn) == (preguntas.ESTADO_DE_LA_TAREA, dos["T1"])
    assert _para_despues(conn) == [(preguntas.QUIEN_DESTRABA, dos["T2"])]


def test_una_repeticion_que_no_salio_no_frena_los_otros_temas_todo_el_dia(conn, mundo, escribe,
                                                                         dos):
    """Si la repetición del día quedó guardada pero no salió (omitida, fallida), el turno de la
    pregunta termina igual a las 4 horas de cuando hubiera salido: nunca frena el resto del día."""
    dias = Dias(conn, mundo)
    _trabada_a_las(conn, escribe, dias, octubre(9, 8, 55))
    dias.ciclo(octubre(9, 10))
    with admin(conn) as cur:
        cur.execute("""select q.* from conversation_state s
                         join conversation_question q on q.id = s.pregunta_abierta_id""")
        pregunta = cur.fetchone()
    conn.commit()
    with espacio(conn, mundo["id"]) as cur:
        cal = Calendario.desde_base(cur, mundo["id"])
        antes = termino_su_turno(cur, cal, mundo["id"], pregunta, octubre(9, 16, 54))
        despues = termino_su_turno(cur, cal, mundo["id"], pregunta, octubre(9, 16, 55))
    conn.commit()
    assert avisos_guardados(conn, REPETICION_DEL_DIA) == []
    assert (antes, despues) == (False, True)


def test_si_ya_no_es_horario_lo_que_espera_sale_el_dia_habil_siguiente(conn, mundo, escribe,
                                                                         dos):
    """La pregunta a las 09:30, la repetición a las 13:30: a las 17:30 ya no es horario. El
    martes 13 (el lunes es feriado) la pregunta del viernes ya no frena: sale primero lo más
    urgente, el pedido de T1, que venció; la repetición de T2 por su escalera espera."""
    dias = Dias(conn, mundo)
    _trabada_a_las(conn, escribe, dias, octubre(9, 9, 30))
    dias.ciclo(octubre(9, 10))
    assert len(dias.ciclo(octubre(9, 13, 30))) == 1
    assert dias.ciclo(octubre(9, 16, 59)) == []
    [primero] = dias.ciclo(octubre(13, 10))
    assert _tareas(primero) == ["Revisar el tablero"]
    assert abierta(conn) == (preguntas.ESTADO_DE_LA_TAREA, dos["T1"])
    assert [a["estado"] for a in avisos_guardados(conn, "repregunta")] == ["guardado"]


# --- 3. La otra vuelve aparte ------------------------------------------------------------------

def test_al_contestar_la_segunda_el_codigo_trae_la_primera_aparte(conn, mundo, escribe, dos):
    dias = Dias(conn, mundo)
    _las_dos_abiertas(conn, escribe, dias, dos)
    r = dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(9, 16, 57))
    assert r.pregunta is None                               # no va en la respuesta
    assert abierta(conn) == (preguntas.QUIEN_DESTRABA, dos["T2"])
    # Enseguida, aunque Marcos escribió hace un minuto.
    [vuelve] = dias.ciclo(octubre(9, 16, 58))
    assert vuelve["hechos"][0]["aviso"] == VUELVE_LA_PREGUNTA
    assert _tareas(vuelve) == ["Probar las comunicaciones"]
    assert vuelve["pregunta"]["tipo"] == preguntas.QUIEN_DESTRABA
    assert vuelve["pregunta"]["desde_antes"] is True
    assert abierta(conn) == (preguntas.QUIEN_DESTRABA, dos["T2"])
    assert _para_despues(conn) == []


def test_al_contestar_la_primera_el_codigo_trae_la_segunda_aparte(conn, mundo, escribe, dos):
    dias = Dias(conn, mundo)
    _las_dos_abiertas(conn, escribe, dias, dos)
    r = dice(conn, escribe, Jugada("anotar_quien_destraba", {"tarea": "T2", "quien": "pedro"}),
             at=octubre(9, 16, 57))
    assert r.pregunta is None
    [vuelve] = dias.ciclo(octubre(9, 16, 58))
    assert vuelve["hechos"][0]["aviso"] == VUELVE_LA_PREGUNTA
    assert _tareas(vuelve) == ["Revisar el tablero"]
    assert vuelve["pregunta"]["tipo"] == preguntas.ESTADO_DE_LA_TAREA
    assert abierta(conn) == (preguntas.ESTADO_DE_LA_TAREA, dos["T1"])


def test_la_que_vuelve_no_repite_lo_mismo_dos_veces_el_dia_siguiente(conn, mundo, escribe, dos):
    """Contestada la segunda fuera del horario, la primera vuelve el día hábil siguiente; si su
    escalera también la repite ese día, sale una sola vez."""
    dias = Dias(conn, mundo)
    _las_dos_abiertas(conn, escribe, dias, dos)
    dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(9, 17, 5))
    assert dias.ciclo(octubre(9, 17, 6)) == []              # fuera del horario
    [una] = dias.ciclo(octubre(13, 10))
    assert una["pregunta"]["tipo"] == preguntas.QUIEN_DESTRABA
    assert dias.ciclo(octubre(13, 10, 1)) == []


# --- 5. La pregunta que quedó por un cambio de tema (decisión 50) ----------------------------------

def _vuelve(pedido: dict) -> bool:
    return pedido["hechos"][0]["aviso"] == VUELVE_LA_PREGUNTA


def _de_marcos(pedidos: list[dict]) -> list[dict]:
    return [p for p in pedidos if p["persona"].startswith("Marcos")]


def test_un_cambio_de_tema_contesta_lo_nuevo_y_la_pregunta_vuelve_aparte(conn, mundo, escribe,
                                                                         dos):
    """Decisión 50 del usuario (2026-10-09, opción A; conversación 08): Marcos habla de otra
    tarea mientras Leda le preguntaba por la trabada. La respuesta es sólo lo nuevo; la pregunta
    vuelve en otro mensaje, justo después, aunque Marcos acaba de escribir."""
    dias = Dias(conn, mundo)
    _trabada_a_las(conn, escribe, dias, octubre(5, 10, 30))
    r = dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(5, 10, 40))
    assert r.pregunta is None                               # un mensaje, un tema
    assert abierta(conn) == (preguntas.QUIEN_DESTRABA, dos["T2"])
    [guardado] = avisos_guardados(conn, VUELVE_LA_PREGUNTA)
    assert guardado["estado"] == "guardado"
    [vuelve] = dias.ciclo(octubre(5, 10, 41))
    assert _vuelve(vuelve) and _tareas(vuelve) == ["Probar las comunicaciones"]
    assert vuelve["pregunta"]["tipo"] == preguntas.QUIEN_DESTRABA
    assert vuelve["pregunta"]["desde_antes"] is True
    assert abierta(conn) == (preguntas.QUIEN_DESTRABA, dos["T2"])


def test_la_pregunta_que_quedo_para_despues_vuelve_aparte(conn, mundo, escribe, dos):
    """Dos preguntas que abrió la conversación, no un aviso (decisión 9d): cerrada la de ahora,
    la que quedó para después vuelve en un mensaje aparte (hasta la decisión 50, en la misma
    respuesta). Enseguida, aunque sea antes de la hora en que Leda escribe por su cuenta."""
    dias = Dias(conn, mundo)
    dice(conn, escribe, jugada_bloqueo("T2", "falta el cable"), at=octubre(5, 9))
    dice(conn, escribe, Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-14"}),
         at=octubre(5, 9, 5))
    assert abierta(conn) == (preguntas.MOTIVO_DEL_ATRASO, dos["T1"])
    r = dice(conn, escribe, Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-14",
                                                        "motivo": "el proveedor"}),
             at=octubre(5, 9, 10))
    assert r.pregunta is None
    assert abierta(conn) == (preguntas.QUIEN_DESTRABA, dos["T2"])
    [vuelve] = _de_marcos(dias.ciclo(octubre(5, 9, 11)))
    assert _vuelve(vuelve) and vuelve["pregunta"]["tipo"] == preguntas.QUIEN_DESTRABA


def test_lo_que_habla_de_la_pregunta_la_deja_en_la_misma_respuesta(conn, mundo, escribe, dos):
    """Un mensaje sobre la pregunta misma, que no la contesta (conversación 27, "y que pongo?"),
    no es un cambio de tema: la pregunta va en la respuesta, como siempre."""
    _trabada_a_las(conn, escribe, Dias(conn, mundo), octubre(5, 10, 30))
    r = dice(conn, escribe, at=octubre(5, 10, 40))           # ninguna jugada
    assert r.pregunta is not None and r.pregunta["tipo"] == preguntas.QUIEN_DESTRABA
    assert r.pregunta["desde_antes"] is True
    assert avisos_guardados(conn, VUELVE_LA_PREGUNTA) == []


def test_un_hecho_de_la_misma_tarea_la_deja_en_la_misma_respuesta(conn, mundo, escribe, dos):
    """El tema es la tarea: lo que la persona dice de la tarea de la pregunta, sin contestarla,
    sigue ese tema y la pregunta va en la misma respuesta."""
    _trabada_a_las(conn, escribe, Dias(conn, mundo), octubre(5, 10, 30))
    r = dice(conn, escribe, Jugada("informar_avance", {"tarea": "T2",
                                                       "palabras": "voy con lo demas"}),
             at=octubre(5, 10, 40))
    assert r.pregunta is not None and r.pregunta["tipo"] == preguntas.QUIEN_DESTRABA
    assert avisos_guardados(conn, VUELVE_LA_PREGUNTA) == []


def test_dos_cambios_de_tema_seguidos_traen_la_pregunta_una_sola_vez(conn, mundo, escribe, dos):
    dias = Dias(conn, mundo)
    _trabada_a_las(conn, escribe, dias, octubre(5, 10, 30))
    dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(5, 10, 40))
    dice(conn, escribe, Jugada("consultar_pendientes", {}), at=octubre(5, 10, 40))
    assert len(avisos_guardados(conn, VUELVE_LA_PREGUNTA)) == 1
    assert len(_de_marcos(dias.ciclo(octubre(5, 10, 41)))) == 1


def test_un_cambio_de_tema_fuera_del_horario_trae_la_pregunta_el_dia_habil_siguiente(
        conn, mundo, escribe, dos):
    """Leda contesta a cualquier hora (9e), pero lo que manda por su cuenta espera el horario:
    la pregunta vuelve el día hábil siguiente, una sola vez aunque su escalera también la
    repita (lectura de la decisión 21, que la 50 no cambia)."""
    dias = Dias(conn, mundo)
    _trabada_a_las(conn, escribe, dias, octubre(5, 16))
    r = dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(5, 20))
    assert r.pregunta is None
    assert dias.ciclo(octubre(5, 20, 1)) == []
    # El martes también sale el aviso previo de T1, que no pregunta nada.
    salen = [p for p in _de_marcos(dias.ciclo(octubre(6, 10))) if p["pregunta"]]
    assert [p["pregunta"]["tipo"] for p in salen] == [preguntas.QUIEN_DESTRABA]
    assert _de_marcos(dias.ciclo(octubre(6, 10, 1))) == []


# --- Lo que lee la IA ----------------------------------------------------------------------------

@pytest.mark.parametrize("codigo", [REPETICION_DEL_DIA, VUELVE_LA_PREGUNTA])
def test_los_avisos_nuevos_tienen_su_significado(codigo):
    assert significado(codigo) is not None


def test_lo_que_pasa_si_no_contesta_es_informar():
    """Punto 5 de la regla: el aviso de que se va a escalar informa que la tarea está atrasada,
    nunca que se la pasa a alguien para que la destrabe; el nombre de a quién, sólo si lo
    pregunta (`hechos.NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO`, decisión 11)."""
    from leda.motor.hechos import NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO

    dicho = significado("si_no_hay_respuesta")
    assert "se informa que la tarea está atrasada" in dicho
    assert "nadie toma la tarea" in dicho
    assert NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO["si_no_hay_respuesta"] == "se_avisa_a"
