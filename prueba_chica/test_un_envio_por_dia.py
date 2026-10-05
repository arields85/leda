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


# --- Si la IA no redacta un envío que junta avisos (revisión de la corrida en seco) ----------

def _guardar_los_avisos_previos(conn, mundo) -> None:
    from prueba_chica.escalera import correr_escalera
    from prueba_chica.tiempo import RelojFijo
    correr_escalera(conn, mundo["id"], RelojFijo(_hora(6, 10)))
    conn.commit()


def _ya_fallo(conn, veces: int) -> None:
    """Uno de los dos avisos ya había fallado `veces` en otra vuelta, solo."""
    from leda.db import admin
    with admin(conn) as cur:
        cur.execute("""update scheduled_notice set intentos = %s
                        where id = (select id from scheduled_notice order by dedupe_key
                                     limit 1)""", (veces,))
    conn.commit()


def test_un_envio_que_la_ia_no_redacto_se_reintenta_entero(conn, mundo, dias,
                                                           dos_que_vencen_juntas):
    """Cada aviso lleva su propia cuenta de intentos (decisión 8, caso 2), pero el envío vuelve
    a intentarse junto, al próximo intento más cercano de sus avisos: si cada uno esperara el
    suyo, saldrían en mensajes separados."""
    from prueba_chica.ia import IAGuionada
    from prueba_chica.test_avisos import _enviar
    _guardar_los_avisos_previos(conn, mundo)
    _ya_fallo(conn, 2)
    caida = IAGuionada(redacciones=[RuntimeError("caída")])

    assert _enviar(conn, mundo, caida, _hora(6, 10)) == {"reintento": 2}

    previos = _avisos(conn, "aviso_previo")
    assert sorted(a["intentos"] for a in previos) == [1, 3]       # la cuenta de cada uno
    assert {a["proximo_intento_en"] for a in previos} == {_hora(6, 10, 1)}   # el más cercano
    bien = IAGuionada(redacciones=["Las dos vencen el viernes."])
    assert _enviar(conn, mundo, bien, _hora(6, 10, 1)) == {"enviado": 2}
    assert len(bien.pedidos_de_redaccion) == 1          # un solo mensaje con las dos
    assert _cuantas(conn, "message_outbox", "not es_respuesta") == 1


def test_un_aviso_que_ya_habia_fallado_no_le_quita_intentos_al_otro(conn, mundo, dias,
                                                                     dos_que_vencen_juntas):
    """Si uno llega a su quinto fallo, queda fallido él solo; el otro sigue con sus intentos y
    sale cuando la IA redacte."""
    from prueba_chica.ia import IAGuionada
    from prueba_chica.test_avisos import _enviar
    _guardar_los_avisos_previos(conn, mundo)
    _ya_fallo(conn, 4)

    assert _enviar(conn, mundo, IAGuionada(redacciones=[RuntimeError("caída")]),
                   _hora(6, 10)) == {"fallido": 1, "reintento": 1}

    fallido, sigue = sorted(_avisos(conn, "aviso_previo"), key=lambda a: a["intentos"],
                            reverse=True)
    assert (fallido["estado"], fallido["intentos"]) == ("fallido", 5)
    assert (sigue["estado"], sigue["intentos"]) == ("guardado", 1)
    assert _cuantas(conn, "incident") == 1
    bien = IAGuionada(redacciones=["Vence el viernes."])
    assert _enviar(conn, mundo, bien, _hora(6, 10, 1)) == {"enviado": 1}


def test_un_texto_que_el_canal_no_lleva_se_reintenta_y_no_corta_la_vuelta(conn, mundo, dias,
                                                                          dos_que_vencen_juntas):
    from prueba_chica.ia import IAGuionada
    from prueba_chica.test_avisos import _enviar
    _guardar_los_avisos_previos(conn, mundo)
    larguisimo = IAGuionada(redacciones=["Recordatorio. " * 500])

    assert _enviar(conn, mundo, larguisimo, _hora(6, 10)) == {"reintento": 2}

    assert [a["estado"] for a in _avisos(conn, "aviso_previo")] == ["guardado", "guardado"]
    assert _cuantas(conn, "message_outbox", "not es_respuesta") == 0


def test_un_texto_largo_cuenta_como_un_intento_y_al_quinto_falla(conn, mundo, dias,
                                                                dos_que_vencen_juntas):
    from prueba_chica.ia import IAGuionada
    from prueba_chica.test_avisos import _enviar
    _guardar_los_avisos_previos(conn, mundo)
    momento = _hora(6, 10)
    for espera in (1, 2, 4, 8):
        largo = IAGuionada(redacciones=["Recordatorio. " * 500])
        assert _enviar(conn, mundo, largo, momento) == {"reintento": 2}
        momento = momento.__class__.fromtimestamp(momento.timestamp() + 60 * espera,
                                                  momento.tzinfo)

    assert _enviar(conn, mundo, IAGuionada(redacciones=["Recordatorio. " * 500]),
                   momento) == {"fallido": 2}
    assert _cuantas(conn, "message_outbox", "not es_respuesta") == 0
