"""El margen máximo de una fecha (la fecha objetivo de una tarea): `ValorEsperado.hasta`
y los meses de calendario (`sumar_meses`). Puro: el reloj y el límite se pasan."""

from __future__ import annotations

from datetime import date

import pytest

from leda.valores import (Aceptado, MotivoRechazo, Rechazado, TipoValor,
                            ValorEsperado, sumar_meses, validar_valor)

HOY = date(2026, 10, 1)
HASTA = date(2026, 12, 1)


def _validar(iso):
    esperado = ValorEsperado(TipoValor.FECHA, hoy=HOY, hasta=HASTA)
    return validar_valor({"fecha_iso": iso}, esperado, limite_texto=50)


@pytest.mark.parametrize("desde, meses, esperada", [
    (date(2026, 10, 1), 2, date(2026, 12, 1)),
    (date(2026, 11, 15), 2, date(2027, 1, 15)),       # cruza el año
    (date(2026, 12, 31), 2, date(2027, 2, 28)),       # fin de mes: se recorta
    (date(2027, 12, 31), 2, date(2028, 2, 29)),       # recorte en bisiesto
    (date(2026, 8, 31), 1, date(2026, 9, 30)),
    (date(2026, 10, 1), 3, date(2027, 1, 1)),
])
def test_sumar_meses_son_meses_de_calendario_recortados_al_fin_de_mes(
        desde, meses, esperada):
    assert sumar_meses(desde, meses) == esperada


@pytest.mark.parametrize("iso", ["2026-10-01", "2026-11-15", "2026-12-01"])
def test_una_fecha_dentro_del_margen_se_acepta_y_el_limite_se_incluye(iso):
    assert isinstance(_validar(iso), Aceptado)


@pytest.mark.parametrize("iso", ["2026-12-02", "2027-08-15", "2030-01-01"])
def test_una_fecha_pasado_el_margen_se_rechaza_con_su_propia_razon(iso):
    r = _validar(iso)
    assert isinstance(r, Rechazado)
    assert r.motivo is MotivoRechazo.FECHA_LEJANA
    assert "01/12/2026" in r.razon and "ya pasó" not in r.razon
    assert "01/12/2026" in r.se_acepta


def test_una_fecha_pasada_sigue_siendo_pasada_aunque_haya_margen():
    assert _validar("2026-09-30").motivo is MotivoRechazo.FECHA_PASADA


def test_sin_margen_no_hay_limite_superior():
    esperado = ValorEsperado(TipoValor.FECHA, hoy=HOY)
    r = validar_valor({"fecha_iso": "2099-01-01"}, esperado, limite_texto=50)
    assert isinstance(r, Aceptado)


def test_el_rechazo_por_fecha_lejana_no_ofrece_tomarla_como_objetivo():
    # Crear un objetivo desde el alta no existe (roadmap): no se ofrece.
    from leda.valores import MotivoRechazo
    r = _validar("2027-08-15")
    assert r.motivo is MotivoRechazo.FECHA_LEJANA
    assert "objetivo" not in r.se_acepta.lower()
    assert not [p for p in ("dividi", "partir", "tareas más cortas")
                if p in r.se_acepta.lower()]
    assert "01/12/2026" in r.se_acepta
