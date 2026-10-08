"""Lo que la cocina le pasa a la IA: la hora de lo que Leda manda y lo que sabe de la tarea.

Cuarta vuelta de ajuste (2026-10-06), después de la ronda 3: la regla del mozo (`AGENTS.md`,
"Cómo pensamos juntos", punto 11): si dice algo mal, primero se mira si la cocina le pasó el
hecho correcto. Mecanismos generales, sin frases ni ramas por conversación:

1. **Una sola hora** para lo que Leda manda por su cuenta (`tiempo.HORA_DE_SALIDA`): la usan la
   escalera, los avisos guardados, el reloj adelantado y los hechos que dicen cuándo sale algo.
   Antes, el pedido que sigue a un avance decía "mañana a las 9" y el reloj adelantado (y las
   conversaciones) llegaban a las 10.
2. **Desde cuándo la tarea está en su estado**, cuando el código lo sabe por lo que anotó el
   motor (`cambios_de_estado.py`), o `desconocido` (conversaciones 01, paso 4, y 12, paso 3).
3. **El vencimiento** también en la escalera de una pregunta (la repregunta y su escalamiento).
4. **El estado real** en un pedido de estado: lo que se espera saber depende del estado
   (`espera_algo_cierto`), y una tarea que espera a otra lo dice (`espera_a`).
5. **Una entrega que no se recibe por chat** dice si hay otra forma definida de hacerla.

El reloj es el de `test_escalera.py`: "Revisar el tablero" (T1) de Marcos vence el viernes 9 de
octubre de 2026; el lunes 12 es feriado.

Portadas de `prueba_chica/test_lo_que_sabe_la_cocina.py`.
"""

from __future__ import annotations

from datetime import datetime, time

from leda.db import admin
from leda.motor import tiempo
from leda.motor.ia import Jugada

from tests.motor.ayudantes import (T1, avisos_guardados, dice, jugada_bloqueo, nueva_tarea,
                                   octubre, poner_estado)


VIERNES_9 = datetime.fromisoformat("2026-10-09T17:00:00-03:00")


def _de(envio: dict, titulo: str) -> dict:
    """El hecho de un envío que habla de esa tarea."""
    [hecho] = [h for h in envio["hechos"] if h["tarea"] == titulo]
    return hecho


# --- 1. Una sola hora ---------------------------------------------------------------------------

def test_lo_que_leda_manda_por_su_cuenta_sale_a_la_hora_de_salida(conn, mundo, dias):
    """La escalera corre desde que empieza la jornada (09:00), pero lo que guarda sale a la
    hora de salida, la misma que el reloj adelantado y las conversaciones."""
    assert tiempo.HORA_DE_SALIDA == time(10, 0)

    assert dias.ciclo(octubre(6, 9)) == []          # guardado, todavía no sale
    [aviso] = avisos_guardados(conn)
    assert aviso["tipo"] == "aviso_previo" and aviso["programado_para"] == octubre(6, 10)

    assert len(dias.ciclo(octubre(6, 10))) == 1
    # Ya pasada la hora, dentro de la jornada, lo que se guarda sale enseguida.
    assert dias.ciclo(octubre(9, 11)) and avisos_guardados(conn, "pedido_de_estado")[0][
        "programado_para"] == octubre(9, 11)


def test_el_pedido_que_sigue_a_un_avance_dice_la_hora_en_que_de_verdad_sale(conn, mundo, dias,
                                                                         escribe):
    dias.ciclo(octubre(9, 10))
    r = dice(conn, escribe, Jugada("informar_avance", {"tarea": "T1", "palabras": "voy bien"}),
             at=octubre(9, 11))

    llega = r.hechos[0]["vuelve_a_pedir_el_estado"]["llega"]
    assert datetime.fromisoformat(llega) == octubre(13, 10)    # el lunes 12 es feriado
    [pedido] = avisos_guardados(conn, "repregunta_de_estado")
    assert pedido["programado_para"] == octubre(13, 10)


def test_el_aviso_al_referente_fuera_de_horario_sale_a_la_hora_de_salida(conn, mundo, escribe):
    r = dice(conn, escribe, Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-14", "motivo": "el proveedor"}),
             at=octubre(5, 17, 20))

    llega = r.hechos[0]["aviso_al_referente"]["llega"]
    assert datetime.fromisoformat(llega) == octubre(6, 10)


# --- 2. Desde cuándo está en su estado ---------------------------------------------------------

def test_el_pedido_de_estado_dice_desde_cuando_esta_en_curso(conn, mundo, dias, escribe):
    """Conversación 01, paso 4: arrancó el martes; el viernes el pedido lo dice."""
    dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(6, 11))

    [envio] = dias.ciclo(octubre(9, 10))

    hecho = _de(envio, "Revisar el tablero")
    assert hecho["aviso"] == "pedido_de_estado" and hecho["estado"] == "en_curso"
    assert hecho["estado_desde"] == "2026-10-06"
    assert hecho["espera_algo_cierto"] == ["si_la_termino", "para_cuando_la_termina",
                                           "si_esta_trabada"]


def test_un_bloqueo_que_se_destrabo_no_cambia_desde_cuando_esta_en_curso(conn, mundo, dias,
                                                                         escribe):
    """Salir de `bloqueada` devuelve el estado que tenía (mecánica §3): sigue en curso desde
    que arrancó."""
    dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(6, 11))
    dice(conn, escribe, jugada_bloqueo("T1", "falta el repuesto"), at=octubre(7, 11))
    dice(conn, escribe, Jugada("destrabar", {"tarea": "T1"}), at=octubre(8, 11))

    [envio] = dias.ciclo(octubre(9, 10))

    assert _de(envio, "Revisar el tablero")["estado_desde"] == "2026-10-06"


def test_un_estado_que_el_motor_no_anoto_es_desconocido(conn, mundo, dias):
    """Una tarea que ya estaba en curso cuando llegó al motor (la cargó otro): el código no sabe
    desde cuándo, y lo dice."""
    poner_estado(conn, mundo["tarea"], "en_curso")

    [envio] = dias.ciclo(octubre(9, 10))

    assert _de(envio, "Revisar el tablero")["estado_desde"] == "desconocido"


def test_un_inicio_que_no_se_puede_anotar_dice_desde_cuando_esta_en_curso(conn, mundo, escribe):
    """Conversación 12, paso 3: "ya la arranqué" de una tarea en curso."""
    dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(6, 11))

    r = dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(7, 11))

    assert r.hechos == [{"jugada": "anotar_inicio", "resultado": "no_se_puede",
                         "motivo": "estado", "tarea": T1, "estado": "en_curso",
                         "estado_desde": "2026-10-06"}]


# --- 3. El vencimiento en la escalera de una pregunta ---------------------------------------

def test_la_repregunta_y_su_escalamiento_dicen_el_vencimiento(conn, mundo, dias, escribe):
    dice(conn, escribe, jugada_bloqueo("T1", "falta el repuesto"), at=octubre(5, 10))

    [otra_vez] = dias.ciclo(octubre(6, 10))
    assert otra_vez["hechos"][0]["vence"] == "2026-10-09"
    dias.ciclo(octubre(7, 10))
    [escalamiento] = dias.ciclo(octubre(8, 10))
    assert escalamiento["persona"] == "Ismael"
    assert escalamiento["hechos"][0]["vence"] == "2026-10-09"


# --- 4. El estado real en un pedido de estado -------------------------------------------------

def test_lo_que_espera_saber_un_pedido_de_estado_depende_del_estado(conn, mundo, dias):
    """Una tarea sin empezar no se pregunta si se terminó; una que espera a otra lo dice, con
    esa tarea y su estado, y no se le pregunta si la empezó (no puede arrancar)."""
    t2 = nueva_tarea(conn, mundo, "Probar las comunicaciones", fecha=VIERNES_9)
    with admin(conn) as cur:
        cur.execute("""insert into dependency (workspace_id, origen_task_id, destino_task_id,
                                               tipo)
                       values (%s, %s, %s, 'bloqueante')""", (mundo["id"], mundo["tarea"], t2))
    conn.commit()

    [envio] = dias.ciclo(octubre(9, 10))

    sin_empezar = _de(envio, "Revisar el tablero")
    assert sin_empezar["estado"] == "asignada"
    assert sin_empezar["espera_algo_cierto"] == ["si_la_empezo", "para_cuando_la_termina",
                                                 "si_esta_trabada"]
    assert "espera_a" not in sin_empezar and "estado_desde" not in sin_empezar
    esperando = _de(envio, "Probar las comunicaciones")
    assert esperando["estado"] == "asignada"
    assert esperando["espera_a"] == [{"tarea": "Revisar el tablero", "estado": "asignada"}]
    assert esperando["espera_algo_cierto"] == ["para_cuando_la_termina", "si_esta_trabada"]


# --- 5. Una entrega que no se recibe por chat -------------------------------------------------

def test_una_entrega_que_no_se_recibe_dice_que_no_hay_otra_forma_definida(conn, mundo, escribe):
    """Conversación 12, paso 6: la IA dijo "presentala por fuera de este chat", un canal que
    nadie definió. El hecho lo dice: no hay otra forma definida (ADR 0018, 9g)."""
    dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(6, 11))

    r = dice(conn, escribe, Jugada("entregar", {"tarea": "T1"}), at=octubre(6, 16))

    assert r.hechos == [{"jugada": "entregar", "resultado": "no_por_chat",
                         "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": T1,
                         "otra_forma_de_hacerlo": "ninguna_definida"}]
