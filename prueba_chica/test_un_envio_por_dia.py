"""Los mensajes automáticos del día a una persona salen en un solo envío (mecánica §10).

Hallazgo de la corrida en seco de la E2-7 (conversación 13, paso 1): dos avisos previos a Marcos
el mismo día salían como dos mensajes. Mecánica §10: todos los mensajes automáticos dirigidos a
una persona en un mismo día se consolidan en un envío por espacio; los avisos de coordinación
(los causa el acto de otra persona) y las respuestas quedan fuera. Una regla del envío, para
todos los tipos de aviso: la IA redacta un mensaje desde los hechos de todos.

El reloj es el de `test_escalera.py`: "Revisar el tablero" (T1) y "Probar las comunicaciones"
(T2) vencen el viernes 9 de octubre de 2026; el aviso previo, tres días hábiles antes, sale el
martes 6.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from prueba_chica.ia import Jugada
from prueba_chica.test_avisos import _dice, _hora
from prueba_chica.test_escalera import (  # noqa: F401 (las fixtures se usan por su nombre)
    _avisos, dias, espacio_con_escalera)
from prueba_chica.test_situaciones import (  # noqa: F401
    _cuantas, _tarea, _todos, marcos, tareas)

VIERNES_9 = datetime(2026, 10, 9, 20, 0, tzinfo=timezone.utc)


@pytest.fixture
def dos_que_vencen_juntas(conn, mundo) -> dict[str, str]:
    return {"T1": mundo["tarea"],
            "T2": _tarea(conn, mundo, "Probar las comunicaciones", fecha=VIERNES_9)}


def test_dos_avisos_automaticos_del_dia_salen_en_un_solo_envio(conn, mundo, dias,
                                                              dos_que_vencen_juntas):
    [envio] = dias.ciclo(_hora(6, 10))

    assert envio["persona"] == "Marcos"
    assert sorted(h["tarea"] for h in envio["hechos"]) == ["Probar las comunicaciones",
                                                           "Revisar el tablero"]
    assert {h["aviso"] for h in envio["hechos"]} == {"vencimiento_proximo"}
    [fila] = _todos(conn, "select * from message_outbox where not es_respuesta")
    previos = _avisos(conn, "aviso_previo")
    assert [a["estado"] for a in previos] == ["enviado", "enviado"]
    assert {str(a["outbox_id"]) for a in previos} == {str(fila["id"])}
    assert _cuantas(conn, "conversation_turn", "sentido = 'salida'") == 1


def test_la_respuesta_siguiente_sabe_que_el_ultimo_aviso_fue_de_las_dos(conn, mundo, dias,
                                                                        dos_que_vencen_juntas,
                                                                        marcos):
    dias.ciclo(_hora(6, 10))

    marcos.dice(Jugada("anotar_inicio", {}), texto="arranque con la de la comprimidora")

    assert marcos.situacion["ultimo_aviso"] == {"tipo": "aviso_previo",
                                                "tareas": ["T1", "T2"]}


def test_dos_pedidos_de_estado_juntos_preguntan_de_a_uno(conn, mundo, dias,
                                                        dos_que_vencen_juntas):
    dias.ciclo(_hora(6, 10))

    [envio] = dias.ciclo(_hora(9, 10))

    assert [h["aviso"] for h in envio["hechos"]] == ["pedido_de_estado", "pedido_de_estado"]
    assert envio["pregunta"]["tipo"] == "estado_de_la_tarea"
    abiertas = _todos(conn, """select q.task_id, s.pregunta_abierta_id = q.id as abierta,
                                      q.para_despues_en is not null as para_despues
                                 from conversation_question q
                                 join conversation_state s on s.membership_id = q.membership_id
                                where q.cerrada_en is null order by q.abierta_en""")
    assert [(f["abierta"], f["para_despues"]) for f in abiertas] == [(True, False),
                                                                    (False, True)]


def test_un_aviso_de_coordinacion_sale_aparte(conn, mundo, dias, dos_que_vencen_juntas,
                                              escribe):
    """El escalamiento de T1 (automático) y el aviso de la previsión de T2 (coordinación: lo
    causa Marcos) le llegan a Ismael el mismo día en dos mensajes."""
    for dia in (6, 9, 13, 14):
        dias.ciclo(_hora(dia, 10))
    _dice(conn, escribe, Jugada("anotar_prevision", {"tarea": "T2", "fecha": "2026-10-21"}),
          at=_hora(15, 9, 30))

    a_ismael = [p for p in dias.ciclo(_hora(15, 10)) if p["persona"] == "Ismael"]

    assert sorted(len(p["hechos"]) for p in a_ismael) == [1, 1]
    assert sorted(p["hechos"][0].get("aviso", "nueva_prevision") for p in a_ismael) == [
        "falta_de_respuesta", "nueva_prevision"]
