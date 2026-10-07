"""Un toque de una opción, en el turno (`leda.motor.turno.procesar_toque`; E2-4).

`odd/tasks/prueba-chica-del-motor.md`, sección 4; ADR 0018, decisiones 3 y 4 (situaciones 5, 6
y 7); ADR 0013, regla 4 (toque con señal e idempotente); conversaciones 09 y 11. El toque corre
el mismo camino que la elección escrita, sin pedirle a la IA que elija, y queda en el registro
de turnos como la opción tocada. El escuchador y los botones, en `test_escuchar.py`.
"""

from __future__ import annotations

import pytest

from leda.motor.ia import IAGuionada, Jugada
from leda.motor.turno import TEXTO_SI_LA_IA_FALLA

from tests.motor.ayudantes import T1, T2, Charla, estado_de, toca, todos, uno


def _turnos_de_toque(conn) -> list[dict]:
    return todos(conn, """select option_id, inbound_message_id, jugadas, resultado, error
                             from conversation_turn
                            where sentido = 'entrada' and option_id is not null
                            order by numero""")


def test_un_toque_corre_el_mismo_camino_que_la_eleccion_escrita(conn, mundo, duda):
    r, ia = toca(conn, mundo, duda["O2"])

    assert ia.pedidos_de_jugadas == []              # la jugada es el toque, no la elige la IA
    assert r.hechos == [{"jugada": "anotar_inicio", "resultado": "anotado",
                         "estado": "en_curso", "tarea": T2,
                         "eligio": {"opcion": "O2", "etiqueta": T2["titulo"], "tarea": T2},
                         "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-16"}}}]
    assert estado_de(conn, duda["T2"]) == "en_curso"
    assert estado_de(conn, duda["T1"]) == "asignada"
    [turno] = _turnos_de_toque(conn)
    opcion = uno(conn, "select id from conversation_option where token = %s", duda["O2"])
    assert turno["option_id"] == opcion["id"] and turno["inbound_message_id"] is None
    assert turno["jugadas"] == [{"nombre": "elegir", "datos": {"opcion": "O2"}}]
    [pedido] = ia.pedidos_de_redaccion
    assert pedido["toco"] == T2["titulo"] and pedido["mensaje"] is None
    assert pedido["pregunta"] is None
    respuesta = uno(conn, """select o.cuerpo, o.es_respuesta, o.chat_id from message_outbox o
                               join conversation_turn t on t.outbox_id = o.id
                              order by t.numero desc limit 1""")
    assert respuesta["cuerpo"] == "Listo." and respuesta["es_respuesta"] is True
    assert respuesta["chat_id"] == mundo["personas"]["Marcos"]["telegram"]


def test_un_toque_repetido_no_hace_nada_dos_veces(conn, mundo, duda):
    toca(conn, mundo, duda["O2"])
    salidas = uno(conn, "select count(*) n from message_outbox")["n"]

    r, ia = toca(conn, mundo, duda["O2"])

    assert r.repetido and ia.pedidos_de_redaccion == []
    assert len(_turnos_de_toque(conn)) == 1
    assert uno(conn, "select count(*) n from message_outbox")["n"] == salidas
    assert uno(conn, "select count(*) n from task_state_event")["n"] == 1


def test_un_toque_de_una_pregunta_ya_cerrada_no_hace_nada_y_dice_con_que_se_cerro(
        conn, mundo, escribe, duda):
    """Conversación 11, paso 1: la pregunta se contestó escribiendo y después llega un toque
    de su otro botón."""
    marcos = Charla(conn, escribe)
    marcos.dice(Jugada("elegir", {"opcion": "O1"}), texto="la del tablero")

    r, _ = toca(conn, mundo, duda["O2"])

    assert r.hechos == [{"jugada": "elegir", "resultado": "sin_efecto",
                         "motivo": "pregunta_cerrada",
                         "eligio": {"opcion": "O2", "etiqueta": T2["titulo"], "tarea": T2},
                         "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-05",
                                         "tarea": T1}}]
    assert estado_de(conn, duda["T2"]) == "asignada"
    assert len(_turnos_de_toque(conn)) == 1          # el toque queda registrado
    # En el turno siguiente, la IA ve qué tocó ("esa", conversación 11, paso 2).
    marcos.dice()
    assert marcos.situacion["ultimos_turnos"][-2]["toco"] == T2["titulo"]


def test_el_toque_de_una_opcion_ajena_no_se_atiende(conn, mundo, duda):
    r, ia = toca(conn, mundo, duda["O1"], nombre="Ismael")

    assert r is None and ia.pedidos_de_redaccion == []
    assert _turnos_de_toque(conn) == []
    assert estado_de(conn, duda["T1"]) == "asignada"


def test_un_token_que_no_existe_no_se_atiende(conn, mundo, duda):
    r, _ = toca(conn, mundo, "no-existe")
    assert r is None and _turnos_de_toque(conn) == []


def test_si_la_ia_falla_en_un_toque_nada_cambia_y_se_puede_volver_a_tocar(conn, mundo, duda):
    falla = IAGuionada(redacciones=[TimeoutError("x"), TimeoutError("x")])

    r, _ = toca(conn, mundo, duda["O2"], ia=falla)

    assert r.texto == TEXTO_SI_LA_IA_FALLA and r.error
    assert estado_de(conn, duda["T2"]) == "asignada"
    assert uno(conn, "select cerrada_en from conversation_question")["cerrada_en"] is None
    [turno] = _turnos_de_toque(conn)
    assert turno["error"]

    r, _ = toca(conn, mundo, duda["O2"])
    assert r.error is None and estado_de(conn, duda["T2"]) == "en_curso"
