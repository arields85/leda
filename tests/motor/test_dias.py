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

from leda.motor import hechos
from leda.motor.ia_real import DIAS_PROXIMOS
from leda.motor.instrucciones import INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION

from tests.motor.ayudantes import (SITUACION, ProveedorFalso, ia_real_falsa, llamada_de_jugadas,
                                   respuesta_de_texto)


def test_cada_fecha_del_pedido_lleva_su_dia_y_su_relacion_con_hoy():
    pedido = {"hoy": "2026-10-26", "hechos": [
        {"vencida": {"fecha_comprometida": "2026-10-23"},
         "vuelve_a_pedir_el_estado": {"sale": "2026-10-27T09:00:00-03:00"},
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
    assert redaccion["dias"] == ["2026-10-20: martes 20 de octubre, hoy",
                                 "2026-10-27: martes 27 de octubre"]
    for pedido in proveedor.pedidos:
        assert "- dias:" in pedido["cuerpo"]["messages"][0]["content"]   # con su significado


def test_las_instrucciones_dicen_que_los_dias_se_usan_sin_calcularlos():
    for texto in (INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION):
        assert "dias" in texto and "sin calcular" in texto
    for dia in ("lunes", "viernes", "miércoles"):
        assert dia not in INSTRUCCIONES_JUGADAS + INSTRUCCIONES_REDACCION, dia
