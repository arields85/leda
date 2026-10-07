"""El día de cada fecha lo da el código (tercera vuelta de ajuste, usuario, 2026-10-06; ADR 0018,
decisión 9).

Ronda 2: la IA calculó mal el día de la semana o el "mañana" desde una fecha AAAA-MM-DD (lo que
sale el martes lo contó como del miércoles). El código los sabe: cada pedido a la IA lleva, para
cada fecha que trae, su día de la semana y, si corresponde, si es hoy, ayer, mañana o pasado
mañana (`dias`); para elegir jugadas, también los de las dos semanas que vienen, para que una
fecha que la persona nombra por su día salga de ahí. Las instrucciones dicen que se usan tal
cual, nunca se calculan.

Portadas de `prueba_chica/test_dias.py`.
"""

from __future__ import annotations

import json
from datetime import date

from leda.motor import hechos
from leda.motor.ia_real import DIAS_PROXIMOS
from leda.motor.instrucciones import INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION

from tests.motor.ayudantes import (SITUACION, ProveedorFalso, ia_real_falsa, llamada_de_jugadas,
                                   respuesta_de_texto)


def test_cada_fecha_del_pedido_lleva_su_dia_y_su_relacion_con_hoy():
    pedido = {"hoy": "2026-10-26", "hechos": [
        {"vencida": {"fecha_comprometida": "2026-10-23"},
         "vuelve_a_pedir_el_estado": {"llega": "2026-10-27T09:00:00-03:00"},
         "prevision": "2026-10-28"}],
        "ultimos_turnos": [{"at": "2026-10-25T10:00:00-03:00"}]}

    assert hechos.dias(pedido) == [
        "2026-10-23: viernes 23 de octubre",
        "2026-10-25: domingo 25 de octubre, ayer",
        "2026-10-26: lunes 26 de octubre, hoy",
        "2026-10-27: martes 27 de octubre, mañana",
        "2026-10-28: miércoles 28 de octubre, pasado mañana"]


def test_para_elegir_jugadas_van_tambien_los_dias_que_vienen():
    dias = hechos.dias({"hoy": "2026-10-30"}, proximos=3)

    assert dias == ["2026-10-30: viernes 30 de octubre, hoy",
                    "2026-10-31: sábado 31 de octubre, mañana",
                    "2026-11-01: domingo 1 de noviembre, pasado mañana",
                    "2026-11-02: lunes 2 de noviembre"]


def test_lo_que_no_es_una_fecha_no_lleva_dia():
    assert hechos.dias({"mensaje": "llego el 2026-99-99 o el 27", "hechos": []}) == []


def test_los_dos_pedidos_a_la_ia_llevan_los_dias():
    proveedor = ProveedorFalso([llamada_de_jugadas({"jugadas": []}), respuesta_de_texto("Listo.")])
    ia = ia_real_falsa(proveedor)

    ia.elegir_jugadas(SITUACION)
    ia.redactar({"hoy": "2026-10-20", "hechos": [{"prevision": "2026-10-27"}]})

    eleccion, redaccion = (json.loads(p["cuerpo"]["messages"][1]["content"])
                           for p in proveedor.pedidos)
    assert len(eleccion["dias"]) == DIAS_PROXIMOS + 1          # hoy y los que vienen
    assert "2026-10-23: viernes 23 de octubre" in eleccion["dias"]
    assert "2026-10-21: miércoles 21 de octubre, mañana" in eleccion["dias"]
    # La redacción los recibe en la forma corta con que se escriben (segunda vuelta del
    # formato, 2026-10-07); para elegir jugadas siguen largos, como los nombra la persona.
    assert redaccion["dias"] == ["2026-10-20: mar 20/10, hoy", "2026-10-27: mar 27/10"]
    for pedido in proveedor.pedidos:
        assert "- dias:" in pedido["cuerpo"]["messages"][0]["content"]   # con su significado


def test_para_redactar_cada_dia_va_en_su_forma_corta_con_su_relacion_con_hoy():
    """Segunda vuelta del formato (usuario, 2026-10-07): fechas cortas, el día abreviado y el
    número con el mes, sin ceros. Lo da el código, para que la IA lo copie y no lo calcule; la
    relación con hoy se conserva."""
    pedido = {"hoy": "2026-11-03", "hechos": [{"prevision": "2026-11-04"},
                                              {"vence": "2026-11-09"}, {"vencio": "2026-11-02"},
                                              {"llega": "2026-11-05T10:00:00-03:00"}]}

    largos = hechos.dias(pedido)
    cortos = hechos.para_redactar({**pedido, "dias": largos})["dias"]

    assert cortos == ["2026-11-02: lun 2/11, ayer", "2026-11-03: mar 3/11, hoy",
                      "2026-11-04: mié 4/11, mañana", "2026-11-05: jue 5/11, pasado mañana",
                      "2026-11-09: lun 9/11"]
    assert [hechos.dia_corto(date(2026, 10, d)) for d in range(23, 30)] == [
        "vie 23/10", "sáb 24/10", "dom 25/10", "lun 26/10", "mar 27/10", "mié 28/10",
        "jue 29/10"]
    # Lo que la persona escribió no se toca, aunque se llame igual.
    assert hechos.para_redactar({"mensaje": "dias", "dias": ["no es un día"]})["dias"] == [
        "no es un día"]


def test_las_instrucciones_dicen_que_los_dias_se_usan_sin_calcularlos():
    for texto in (INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION):
        assert "dias" in texto and "sin calcular" in texto
    for dia in ("lunes", "viernes", "miércoles"):
        assert dia not in INSTRUCCIONES_JUGADAS + INSTRUCCIONES_REDACCION, dia


def test_una_fecha_a_mas_de_dos_semanas_tambien_sale_de_la_lista():
    """E3-8: con la lista de dos semanas, "el miércoles 4" a 15 días quedaba afuera y la IA
    perdía la fecha (misma falla en dos rondas). La lista cubre ocho semanas: una previsión
    realista se nombra por su día y su día lo da el código."""
    proveedor = ProveedorFalso([llamada_de_jugadas({"jugadas": []})])
    ia = ia_real_falsa(proveedor)

    ia.elegir_jugadas(SITUACION)

    eleccion = json.loads(proveedor.pedidos[0]["cuerpo"]["messages"][1]["content"])
    assert "2026-11-04: miércoles 4 de noviembre" in eleccion["dias"]
    assert "2026-12-14: lunes 14 de diciembre" in eleccion["dias"]
