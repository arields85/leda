"""Con una previsión, el seguimiento se mueve a la previsión (ADR 0018, 9i; usuario, 2026-10-05).

`tests/conversaciones/02-nueva-prevision.md`, pasos 4 a 7. La tarea "Revisar el tablero" de
Marcos vence el viernes 9 de octubre de 2026 (V); el sábado 10 y el domingo 11 no son hábiles y el
lunes 12 es feriado. Con una previsión posterior (F), el día del vencimiento sale un solo
recordatorio que no pide nada; hasta F no se pide nada; el día de F se pide el estado como si fuera
V y, sin respuesta, la escalera sigue desde ahí hasta escalar. La fecha comprometida no cambia y
el atraso se cuenta contra ella.
"""

from __future__ import annotations

import pytest

from prueba_chica.escalera import correr_escalera
from prueba_chica.ia import Jugada
from prueba_chica.test_avisos import _dice, _hora
from prueba_chica.test_escalera import (  # noqa: F401 (las fixtures se usan por su nombre)
    _avisos, _espera, _para, dias, espacio_con_escalera)
from prueba_chica.test_situaciones import _cuantas
from prueba_chica.tiempo import RelojFijo


def _prevision(conn, escribe, fecha: str, at) -> None:
    _dice(conn, escribe, Jugada("anotar_prevision", {"tarea": "T1", "fecha": fecha,
                                                     "motivo": "el proveedor"}), at=at)


def _de_marcos(pedidos: list[dict]) -> list[dict]:
    return [p for p in pedidos if p["persona"] == "Marcos"]


def test_con_una_prevision_el_vencimiento_lleva_un_recordatorio_y_la_escalera_va_a_la_prevision(
        conn, mundo, dias, escribe):
    _prevision(conn, escribe, "2026-10-15", at=_hora(5, 11))
    [al_referente] = dias.ciclo(_hora(5, 11, 30))
    assert al_referente["persona"] == "Ismael"

    # Hasta el vencimiento, nada: el aviso previo era de V, y Marcos ya dio su fecha.
    for dia in (6, 7, 8):
        assert dias.ciclo(_hora(dia, 10)) == []

    [recordatorio] = dias.ciclo(_hora(9, 10))

    assert recordatorio["persona"] == "Marcos" and recordatorio["pregunta"] is None
    hechos = recordatorio["hechos"][0]
    assert hechos["aviso"] == "vencimiento_con_prevision"
    assert hechos["necesita_respuesta"] is False
    assert hechos["vence"] == "2026-10-09" and hechos["atraso_dias_habiles"] == 0
    assert hechos["prevision_vigente"] == {
        "fecha": "2026-10-15", "motivo": "el proveedor", "atraso_dias_habiles": 3,
        "aviso_al_referente": {"a": "Ismael", "estado": "enviado"}}
    assert hechos["pide_el_estado_el"] == {"fecha": "2026-10-15", "estado": "todavia_no"}
    assert _espera(conn) is None
    assert _cuantas(conn, "conversation_question", "cerrada_en is null") == 0
    # Uno solo, y nada cada día hasta la previsión (el lunes 12 es feriado).
    for momento in (_hora(9, 15), _hora(13, 10), _hora(14, 10)):
        assert dias.ciclo(momento) == []

    [v] = dias.ciclo(_hora(15, 10))

    hechos = v["hechos"][0]
    assert (hechos["aviso"], hechos["numero"]) == ("pedido_de_estado", 1)
    assert hechos["seguimiento_por"] == "prevision" and hechos["necesita_respuesta"] is True
    assert hechos["vence"] == "2026-10-09" and hechos["atraso_dias_habiles"] == 3
    assert v["pregunta"]["tipo"] == "estado_de_la_tarea"
    assert _espera(conn)["satisfecho_en"] is None

    # Sin respuesta, la escalera sigue desde la previsión.
    assert dias.ciclo(_hora(16, 10))[0]["hechos"][0]["numero"] == 2
    [tercero] = dias.ciclo(_hora(19, 10))
    assert tercero["hechos"][0]["si_no_hay_respuesta"]["se_avisa_a"] == ["Ismael"]

    [escalamiento] = dias.ciclo(_hora(20, 10))

    assert escalamiento["persona"] == "Ismael"
    hechos = escalamiento["hechos"][0]
    assert hechos["aviso"] == "falta_de_respuesta" and hechos["seguimiento_por"] == "prevision"
    assert hechos["pedido_desde"] == "2026-10-15" and hechos["atraso_dias_habiles"] == 6
    assert hechos["prevision_vigente"]["fecha"] == "2026-10-15"
    assert dias.ciclo(_hora(21, 10)) == []
    # La fecha comprometida no cambió.
    assert all(a["hechos"]["vence"] == "2026-10-09" for a in _avisos(conn)
               if a["tipo"] != "nueva_prevision")


def test_una_prevision_mas_nueva_mueve_el_ancla(conn, mundo, dias, escribe):
    _prevision(conn, escribe, "2026-10-15", at=_hora(5, 11))
    for dia in (5, 9, 13):
        dias.ciclo(_hora(dia, 11))
    correr_escalera(conn, mundo["id"], RelojFijo(_hora(15, 7)))     # el pedido del 15, guardado
    conn.commit()

    _prevision(conn, escribe, "2026-10-20", at=_hora(15, 8))

    assert _de_marcos(dias.ciclo(_hora(15, 10))) == []
    [guardado] = _avisos(conn, "pedido_de_estado")
    assert (guardado["estado"], guardado["motivo_omision"]) == ("omitido", "ya_respondio")
    assert _de_marcos(dias.ciclo(_hora(16, 10))) == []
    assert _de_marcos(dias.ciclo(_hora(19, 10))) == []
    [v] = _de_marcos(dias.ciclo(_hora(20, 10)))
    assert (v["hechos"][0]["aviso"], v["hechos"][0]["numero"]) == ("pedido_de_estado", 1)
    assert v["hechos"][0]["prevision_vigente"]["fecha"] == "2026-10-20"
    # Un solo recordatorio del vencimiento, aunque la previsión haya cambiado.
    assert len(_avisos(conn, "vencimiento_con_prevision")) == 1


def test_una_prevision_que_vuelve_a_la_fecha_comprometida_devuelve_el_ancla(conn, mundo, dias,
                                                                           escribe):
    _prevision(conn, escribe, "2026-10-15", at=_hora(5, 11))
    assert _de_marcos(dias.ciclo(_hora(6, 10))) == []     # sin aviso previo: el ancla es F

    _prevision(conn, escribe, "2026-10-09", at=_hora(7, 9, 30))

    [previo] = _de_marcos(dias.ciclo(_hora(7, 10)))       # vuelve el de V, comprimido
    assert previo["hechos"][0]["aviso"] == "vencimiento_proximo"
    [v] = dias.ciclo(_hora(9, 10))
    assert (v["hechos"][0]["aviso"], v["hechos"][0]["numero"]) == ("pedido_de_estado", 1)
    assert "seguimiento_por" not in v["hechos"][0]
    assert _avisos(conn, "vencimiento_con_prevision") == []


def test_un_recordatorio_guardado_no_sale_si_la_prevision_vuelve_a_la_fecha_comprometida(
        conn, mundo, dias, escribe):
    _prevision(conn, escribe, "2026-10-15", at=_hora(5, 11))
    correr_escalera(conn, mundo["id"], RelojFijo(_hora(9, 7)))
    conn.commit()
    _prevision(conn, escribe, "2026-10-09", at=_hora(9, 8))

    [v] = _de_marcos(dias.ciclo(_hora(9, 10)))

    [recordatorio] = _avisos(conn, "vencimiento_con_prevision")
    assert (recordatorio["estado"], recordatorio["motivo_omision"]) == (
        "omitido", "volvio_a_la_fecha_comprometida")
    assert v["hechos"][0]["aviso"] == "pedido_de_estado"


def test_una_prevision_despues_del_vencimiento_lleva_la_escalera_a_la_prevision(conn, mundo, dias,
                                                                              escribe):
    """El pedido de V ya salió: no hay recordatorio del vencimiento. La previsión contesta la
    espera, y la escalera nueva empieza el día de la previsión."""
    [v] = dias.ciclo(_hora(9, 10))
    assert v["hechos"][0]["numero"] == 1

    _prevision(conn, escribe, "2026-10-16", at=_hora(9, 11))

    for dia in (13, 14, 15):
        assert _de_marcos(dias.ciclo(_hora(dia, 10))) == []
    [f] = _de_marcos(dias.ciclo(_hora(16, 10)))
    assert (f["hechos"][0]["numero"], f["hechos"][0]["seguimiento_por"]) == (1, "prevision")
    assert _avisos(conn, "vencimiento_con_prevision") == []
    assert _para(conn, mundo, "Ismael") == ["Aviso 2."]       # sólo el de la previsión


@pytest.mark.parametrize("fecha", ["2026-10-08", "2026-10-09"])
def test_una_prevision_que_no_pasa_la_fecha_comprometida_deja_el_ancla_en_el_vencimiento(
        conn, mundo, dias, escribe, fecha):
    _prevision(conn, escribe, fecha, at=_hora(5, 11))

    [previo] = _de_marcos(dias.ciclo(_hora(6, 10)))
    assert previo["hechos"][0]["aviso"] == "vencimiento_proximo"
    [v] = _de_marcos(dias.ciclo(_hora(9, 10)))
    assert v["hechos"][0]["aviso"] == "pedido_de_estado"


# --- Cada anclaje es una escalera nueva (revisión del ancla, 2026-10-05) ----------------------
#
# El ancla iba en la clave sólo por su fecha: volver a una fecha ya usada reusaba los pasos de
# aquella escalera (contestada o escalada) y el seguimiento quedaba muerto. Ahora cada anclaje
# (la previsión con que empieza una racha de la misma fecha) es una escalera nueva; repetir la
# misma fecha no lo es.


def test_volver_a_la_fecha_comprometida_despues_de_empezar_su_escalera_es_una_escalera_nueva(
        conn, mundo, dias, escribe):
    [v] = dias.ciclo(_hora(9, 10))                           # el pedido de V, sin respuesta
    assert v["hechos"][0]["numero"] == 1
    _prevision(conn, escribe, "2026-10-16", at=_hora(9, 11))  # contesta: el ancla va al 16
    assert _de_marcos(dias.ciclo(_hora(13, 9, 30))) == []

    _prevision(conn, escribe, "2026-10-09", at=_hora(13, 9, 40))   # vuelve a V, ya vencida

    [otra_vez] = _de_marcos(dias.ciclo(_hora(13, 10)))
    hechos = otra_vez["hechos"][0]
    assert (hechos["aviso"], hechos["numero"]) == ("pedido_de_estado", 1)
    assert "seguimiento_por" not in hechos
    assert _cuantas(conn, "pending_reply", "satisfecho_en is null") == 1   # su propia espera
    # Sin respuesta, sigue hasta escalar, como cualquier escalera.
    assert dias.ciclo(_hora(14, 10))[0]["hechos"][0]["numero"] == 2


def test_volver_a_una_prevision_ya_usada_es_una_escalera_nueva(conn, mundo, dias, escribe):
    _prevision(conn, escribe, "2026-10-15", at=_hora(5, 11))
    for dia in (5, 9, 13):
        dias.ciclo(_hora(dia, 11))
    [f] = _de_marcos(dias.ciclo(_hora(15, 10)))              # el pedido del día de la previsión
    assert f["hechos"][0]["numero"] == 1
    _prevision(conn, escribe, "2026-10-20", at=_hora(15, 11))  # contesta y mueve el ancla

    _prevision(conn, escribe, "2026-10-15", at=_hora(16, 9, 30))  # vuelve al 15, ya pasado

    [otra_vez] = _de_marcos(dias.ciclo(_hora(16, 10)))
    hechos = otra_vez["hechos"][0]
    assert (hechos["aviso"], hechos["numero"]) == ("pedido_de_estado", 1)
    assert hechos["prevision_vigente"]["fecha"] == "2026-10-15"


def test_repetir_la_misma_fecha_no_empieza_otra_escalera(conn, mundo, dias, escribe):
    _prevision(conn, escribe, "2026-10-15", at=_hora(5, 11))
    for dia in (5, 9, 13):
        dias.ciclo(_hora(dia, 11))
    dias.ciclo(_hora(15, 10))                                # el pedido del 15

    _prevision(conn, escribe, "2026-10-15", at=_hora(15, 11))  # "sigo para hoy": contesta

    for momento in (_hora(15, 12), _hora(16, 10), _hora(19, 10)):
        assert _de_marcos(dias.ciclo(momento)) == []


# --- Revisión de la E2-7 ---------------------------------------------------------------------


class _Fila(dict):
    """Una fila que cuenta cuántas veces se la recorre: un ciclo en la cadena no termina."""

    lecturas = 0

    def __getitem__(self, clave):
        type(self).lecturas += 1
        if type(self).lecturas > 1000:
            raise AssertionError("la cadena de previsiones no termina")
        return super().__getitem__(clave)


class _CursorDeUnaCadena:
    """Dos previsiones que se reemplazan una a la otra con la misma fecha: una cadena rota."""

    def __init__(self) -> None:
        from datetime import date
        self.a = _Fila(id="a", fecha_prevista=date(2026, 10, 15), reemplaza_id="b")
        self.b = _Fila(id="b", fecha_prevista=date(2026, 10, 15), reemplaza_id="a")
        self._ultimo = None

    def execute(self, sql, params=None):
        self._ultimo = sql

    def fetchone(self):
        return self.a

    def fetchall(self):
        return [self.a, self.b]


def test_una_cadena_de_previsiones_con_un_ciclo_no_cuelga_el_ancla():
    from datetime import date

    from prueba_chica.ancla import anclaje

    _Fila.lecturas = 0
    de = anclaje(_CursorDeUnaCadena(), "tarea", date(2026, 10, 9))

    assert de.fecha == date(2026, 10, 15)
    assert de.clave.startswith("2026-10-15+")


def test_un_paso_guardado_con_la_clave_de_antes_sigue_siendo_de_su_ancla(conn, mundo, dias,
                                                                         escribe):
    """Antes de la revisión del ancla, la clave de un paso anclado en una previsión era la
    fecha sola. Un paso así, guardado en una base de antes, sigue siendo de la escalera de esa
    previsión: sale, y la escalera sigue contándolo."""
    from leda.db import admin

    _prevision(conn, escribe, "2026-10-15", at=_hora(5, 11))
    for dia in (5, 9, 13):
        dias.ciclo(_hora(dia, 11))
    correr_escalera(conn, mundo["id"], RelojFijo(_hora(15, 7)))     # el pedido del 15, guardado
    conn.commit()
    with admin(conn) as cur:
        cur.execute("""update scheduled_notice
                          set dedupe_key = regexp_replace(dedupe_key, '[+][^:]+', '')
                        where tipo = 'pedido_de_estado'""")
    conn.commit()

    [f] = _de_marcos(dias.ciclo(_hora(15, 10)))

    assert f["hechos"][0]["numero"] == 1
    [pedido] = _avisos(conn, "pedido_de_estado")
    assert pedido["estado"] == "enviado"
    assert _de_marcos(dias.ciclo(_hora(16, 10)))[0]["hechos"][0]["numero"] == 2


def test_un_ciclo_que_no_pasa_la_fecha_comprometida_deja_la_escalera_de_siempre():
    """Un ciclo es el final de la cadena: si sus previsiones no pasan la fecha comprometida,
    ninguna movió el ancla y la clave es la del vencimiento, no una escalera nueva."""
    from datetime import date

    from prueba_chica.ancla import anclaje

    cursor = _CursorDeUnaCadena()
    cursor.a["fecha_prevista"] = cursor.b["fecha_prevista"] = date(2026, 10, 5)
    _Fila.lecturas = 0
    de = anclaje(cursor, "tarea", date(2026, 10, 9))

    assert (de.fecha, de.clave, de.legado) == (date(2026, 10, 9), "2026-10-09", None)
