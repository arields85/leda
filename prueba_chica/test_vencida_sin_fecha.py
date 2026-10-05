"""Con la tarea vencida, una respuesta sin fecha lleva la pregunta de para cuándo (usuario,
2026-10-05; ADR 0018, 9j; conversación 16).

Con la tarea pasada su fecha de seguimiento (la comprometida o, si es posterior, la previsión),
lo que la persona contesta se anota igual y, si no trae una fecha ("arranqué hoy", "voy bien",
"sigo con eso"), Leda le pregunta en esa misma respuesta para qué día la va a tener: una sola
pregunta. Esa respuesta no es algo cierto sobre cuándo: la espera del estado sigue abierta y,
si no contesta, Leda vuelve a pedir el estado el día hábil siguiente, con la cuenta de nuevo
(como un avance, 9h). Una regla general para toda jugada sobre la tarea vencida, no para una:
una previsión trae la fecha y un bloqueo es algo cierto, así que ésas no la llevan.

El reloj es el de `test_escalera.py`: "Revisar el tablero" (T1) de Marcos vence el viernes 9 de
octubre de 2026; el lunes 12 es feriado.
"""

from __future__ import annotations

import pytest

from prueba_chica.ia import Jugada
from prueba_chica.test_avisos import _dice, _hora
from prueba_chica.test_escalera import (  # noqa: F401 (las fixtures se usan por su nombre)
    _avisos, dias, espacio_con_escalera)
from prueba_chica.test_situaciones import _cuantas, _todos

FECHA = "fecha_de_la_tarea"


def _abierta(conn) -> str | None:
    fila = _todos(conn, """select q.tipo from conversation_state s
                            join conversation_question q on q.id = s.pregunta_abierta_id
                           where q.cerrada_en is null""")
    return fila[0]["tipo"] if fila else None


def _esperas_abiertas(conn) -> int:
    return _cuantas(conn, "pending_reply", "tipo = 'estado_de_la_tarea' and satisfecho_en is null")


def _vencida(dias) -> None:
    """El pedido del vencimiento (viernes 9) y el del martes 13, sin respuesta."""
    dias.ciclo(_hora(9, 10))
    dias.ciclo(_hora(13, 10))


def test_un_inicio_con_la_tarea_vencida_se_anota_y_pregunta_para_cuando(conn, mundo, dias,
                                                                         escribe):
    _vencida(dias)

    r = _dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=_hora(13, 10, 20))

    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["estado"]) == ("anotado", "en_curso")
    assert hecho["vencida"] == {"fecha_comprometida": "2026-10-09", "atraso_dias_habiles": 1}
    assert hecho["pregunta"] == FECHA
    assert r.pregunta["tipo"] == FECHA and _abierta(conn) == FECHA
    # No es algo cierto sobre cuándo: la espera sigue y mañana se vuelve a pedir el estado.
    assert _esperas_abiertas(conn) == 1
    assert hecho["vuelve_a_pedir_el_estado"]["estado"] == "guardado_sin_enviar"
    assert hecho["vuelve_a_pedir_el_estado"]["sale"].startswith("2026-10-14")
    [repregunta] = _avisos(conn, "repregunta_de_estado")
    assert repregunta["estado"] == "guardado"


@pytest.mark.parametrize("jugada", [
    Jugada("informar_avance", {"tarea": "T1", "palabras": "voy bien"}),
    Jugada("anotar_inicio", {"tarea": "T1"}),
], ids=lambda j: j.nombre)
def test_es_una_regla_para_toda_respuesta_sin_fecha(conn, mundo, dias, escribe, jugada):
    _vencida(dias)

    r = _dice(conn, escribe, jugada, at=_hora(13, 10, 20))

    assert r.hechos[0]["resultado"] == "anotado"
    assert r.hechos[0]["pregunta"] == FECHA and r.pregunta["tipo"] == FECHA
    assert _cuantas(conn, "conversation_question",
                    "tipo = %s and cerrada_en is null", FECHA) == 1     # una sola pregunta


def test_la_fecha_contesta_y_el_seguimiento_va_a_ella(conn, mundo, dias, escribe):
    _vencida(dias)
    _dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=_hora(13, 10, 20))

    r = _dice(conn, escribe, Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-16"}),
              at=_hora(13, 10, 25))

    assert r.hechos[0]["atraso_si_se_cumple_la_prevision_dias_habiles"] == 4 and "vencida" not in r.hechos[0]
    assert r.pregunta is None and _abierta(conn) is None and _esperas_abiertas(conn) == 0
    dias.ciclo(_hora(13, 10, 30))                       # el aviso a Ismael
    assert [p for p in dias.ciclo(_hora(14, 10)) if p["persona"] == "Marcos"] == []
    [repregunta] = _avisos(conn, "repregunta_de_estado")
    assert (repregunta["estado"], repregunta["motivo_omision"]) == ("omitido", "ya_respondio")
    [f] = [p for p in dias.ciclo(_hora(16, 10)) if p["persona"] == "Marcos"]
    assert f["hechos"][0]["seguimiento_por"] == "prevision"


def test_sin_vencer_no_se_pregunta_la_fecha(conn, mundo, dias, escribe):
    dias.ciclo(_hora(9, 10))                            # el día del vencimiento todavía no venció

    r = _dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=_hora(9, 10, 20))

    assert "vencida" not in r.hechos[0] and r.pregunta is None
    assert _esperas_abiertas(conn) == 0


def test_un_bloqueo_con_la_tarea_vencida_no_lleva_la_pregunta_de_la_fecha(conn, mundo, dias,
                                                                          escribe):
    """Un bloqueo es algo cierto: lo que sigue es la pregunta de quién lo destraba (9c)."""
    _vencida(dias)

    r = _dice(conn, escribe, Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "falta el PLC"}),
              at=_hora(13, 10, 20))

    assert r.pregunta["tipo"] == "quien_destraba"
    assert _cuantas(conn, "conversation_question", "tipo = %s", FECHA) == 0


def test_con_una_prevision_la_tarea_vence_al_pasar_la_prevision(conn, mundo, dias, escribe):
    """El ancla (9i): pasada la fecha comprometida pero no la prevista, la tarea no está vencida
    para esta regla; pasada la prevista, sí, y los hechos dicen cuál era la previsión. El atraso
    se sigue contando contra la fecha comprometida."""
    _dice(conn, escribe, Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-14"}),
          at=_hora(5, 10))

    r = _dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=_hora(13, 10, 20))
    assert "vencida" not in r.hechos[0] and r.pregunta is None

    dias.ciclo(_hora(14, 10))                           # el pedido del día de la previsión
    r = _dice(conn, escribe, Jugada("informar_avance", {"tarea": "T1", "palabras": "voy bien"}),
              at=_hora(15, 10, 20))

    assert r.hechos[0]["vencida"] == {"fecha_comprometida": "2026-10-09",
                                      "atraso_dias_habiles": 3,
                                      "prevision_vencida": "2026-10-14"}
    assert r.pregunta["tipo"] == FECHA
