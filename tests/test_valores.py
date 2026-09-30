"""Validación de los valores normalizados que trae el ruteo (ADR 0014, M1).

`valores.validar_valor` es puro: el reloj (`hoy`) y el límite de texto se
pasan. El modelo interpreta el lenguaje; acá sólo se comprueba el contrato, por
eso las pruebas cubren familias de formas de un mismo valor y no una frase.
"""

from __future__ import annotations

from datetime import date

import pytest

from prisma.valores import (
    OPCION_NINGUNA, Aceptado, MotivoRechazo, Opcion, Rechazado, TipoValor,
    ValorEsperado, opciones_numeradas, validar_valor,
)

HOY = date(2026, 9, 30)
LIMITE = 50
OPCIONES = opciones_numeradas(["Cocina", "Taller", "Oficina"])


def _validar(esperado, valor):
    return validar_valor(valor, esperado, limite_texto=LIMITE)


# --- fecha -------------------------------------------------------------------

@pytest.mark.parametrize("iso, esperada", [
    ("2026-10-04", date(2026, 10, 4)),
    ("2026-09-30", date(2026, 9, 30)),       # hoy vale
    ("2026-12-31", date(2026, 12, 31)),
    ("2028-02-29", date(2028, 2, 29)),       # bisiesto
    ("  2026-10-04  ", date(2026, 10, 4)),   # el borde se recorta
])
def test_una_fecha_iso_valida_desde_hoy_se_acepta(iso, esperada):
    esperado = ValorEsperado(TipoValor.FECHA, hoy=HOY)
    assert _validar(esperado, {"fecha_iso": iso}) == Aceptado(
        TipoValor.FECHA, esperada)


@pytest.mark.parametrize("iso", ["2026-09-29", "2025-12-31", "2020-01-01"])
def test_una_fecha_pasada_se_rechaza_con_la_razon_real(iso):
    esperado = ValorEsperado(TipoValor.FECHA, hoy=HOY)
    r = _validar(esperado, {"fecha_iso": iso})
    assert isinstance(r, Rechazado)
    assert r.motivo is MotivoRechazo.FECHA_PASADA
    assert r.razon == "Esa fecha ya pasó."
    assert r.se_acepta == "Decime una fecha desde hoy en adelante."
    assert r.mensaje == ("Esa fecha ya pasó. "
                         "Decime una fecha desde hoy en adelante.")


@pytest.mark.parametrize("iso", [
    "2027-02-29",        # no bisiesto
    "2026-13-01",
    "2026-00-10",
    "2026-09-31",
    "2026-2-3",          # sin ceros: no es ISO
    "20261004",          # ISO básico, no extendido
    "2026-W40-7",        # ISO semanal
    "04/10/2026",        # no normalizada: el modelo debía devolver ISO
    "4 de octubre",
    "2026-10-04T10:00",
    "mañana",
    "",
    "   ",
])
def test_una_fecha_que_no_es_iso_valida_se_rechaza(iso):
    esperado = ValorEsperado(TipoValor.FECHA, hoy=HOY)
    r = _validar(esperado, {"fecha_iso": iso})
    assert isinstance(r, Rechazado)
    assert r.motivo in (MotivoRechazo.FECHA_INVALIDA, MotivoRechazo.SIN_VALOR)
    assert r.se_acepta == "Decime una fecha desde hoy en adelante."


def test_una_fecha_que_no_existe_dice_que_no_existe():
    esperado = ValorEsperado(TipoValor.FECHA, hoy=HOY)
    r = _validar(esperado, {"fecha_iso": "2027-02-29"})
    assert r.motivo is MotivoRechazo.FECHA_INVALIDA
    assert r.razon == "Esa fecha no existe."


def test_la_fecha_sin_reloj_es_un_defecto_de_quien_llama():
    with pytest.raises(ValueError):
        validar_valor({"fecha_iso": "2026-10-04"},
                      ValorEsperado(TipoValor.FECHA), limite_texto=LIMITE)


@pytest.mark.parametrize("valor", [
    None, {}, {"texto": "mañana"}, {"opcion_id": "1"}, {"fecha_iso": None},
    {"fecha_iso": 20261004}, {"fecha_iso": ["2026-10-04"]},
])
def test_sin_fecha_es_sin_valor_y_nunca_se_inventa(valor):
    esperado = ValorEsperado(TipoValor.FECHA, hoy=HOY)
    r = _validar(esperado, valor)
    assert isinstance(r, Rechazado)
    assert r.motivo is MotivoRechazo.SIN_VALOR
    assert r.se_acepta == "Decime una fecha desde hoy en adelante."


# --- opción ------------------------------------------------------------------

@pytest.mark.parametrize("opcion_id", ["1", "2", "3", " 2 "])
def test_una_opcion_ofrecida_se_acepta_por_su_id(opcion_id):
    esperado = ValorEsperado(TipoValor.OPCION, OPCIONES)
    r = _validar(esperado, {"opcion_id": opcion_id})
    assert r == Aceptado(TipoValor.OPCION, opcion_id.strip())


def test_ninguna_es_un_valor_aceptado():
    esperado = ValorEsperado(TipoValor.OPCION, OPCIONES)
    assert _validar(esperado, {"opcion_id": OPCION_NINGUNA}) == Aceptado(
        TipoValor.OPCION, OPCION_NINGUNA)


@pytest.mark.parametrize("opcion_id", [
    "4", "0", "Cocina", "cocina", "uno", "NINGUNA", "", "1.0"])
def test_una_opcion_que_no_se_ofrecio_se_rechaza_y_dice_cuales_sirven(opcion_id):
    esperado = ValorEsperado(TipoValor.OPCION, OPCIONES)
    r = _validar(esperado, {"opcion_id": opcion_id})
    assert isinstance(r, Rechazado)
    assert r.motivo in (MotivoRechazo.OPCION_DESCONOCIDA,
                        MotivoRechazo.SIN_VALOR)
    assert "«Cocina»" in r.se_acepta
    assert "«Taller»" in r.se_acepta and "«Oficina»" in r.se_acepta


@pytest.mark.parametrize("valor", [
    None, {}, {"texto": "la cocina"}, {"opcion_id": None}, {"opcion_id": 1},
])
def test_sin_opcion_es_sin_valor(valor):
    esperado = ValorEsperado(TipoValor.OPCION, OPCIONES)
    r = _validar(esperado, valor)
    assert isinstance(r, Rechazado)
    assert r.motivo is MotivoRechazo.SIN_VALOR


def test_opciones_numeradas_da_ids_estables_desde_uno():
    assert OPCIONES == (Opcion("1", "Cocina"), Opcion("2", "Taller"),
                        Opcion("3", "Oficina"))


# --- texto y entidad ---------------------------------------------------------

@pytest.mark.parametrize("tipo", [TipoValor.TEXTO, TipoValor.ENTIDAD])
@pytest.mark.parametrize("texto, esperado_texto", [
    ("faltó el repuesto", "faltó el repuesto"),
    ("  con espacios  ", "con espacios"),
    ("x", "x"),
    ("a" * LIMITE, "a" * LIMITE),
    ("línea 1\nlínea 2", "línea 1\nlínea 2"),
])
def test_un_texto_no_vacio_dentro_del_limite_se_acepta(
        tipo, texto, esperado_texto):
    r = _validar(ValorEsperado(tipo), {"texto": texto})
    assert r == Aceptado(tipo, esperado_texto)


@pytest.mark.parametrize("texto", ["", "   ", "\n\t"])
def test_un_texto_vacio_se_rechaza(texto):
    r = _validar(ValorEsperado(TipoValor.TEXTO), {"texto": texto})
    assert isinstance(r, Rechazado)
    assert r.motivo in (MotivoRechazo.TEXTO_VACIO, MotivoRechazo.SIN_VALOR)


def test_un_texto_largo_se_rechaza_con_el_limite_real():
    r = _validar(ValorEsperado(TipoValor.TEXTO), {"texto": "a" * (LIMITE + 1)})
    assert isinstance(r, Rechazado)
    assert r.motivo is MotivoRechazo.TEXTO_LARGO
    assert str(LIMITE) in r.razon
    assert "Acortalo" in r.se_acepta


@pytest.mark.parametrize("valor", [
    None, {}, {"fecha_iso": "2026-10-04"}, {"texto": None}, {"texto": 5},
])
def test_sin_texto_es_sin_valor(valor):
    r = _validar(ValorEsperado(TipoValor.TEXTO), valor)
    assert isinstance(r, Rechazado)
    assert r.motivo is MotivoRechazo.SIN_VALOR


# --- ninguno -----------------------------------------------------------------

@pytest.mark.parametrize("valor", [None, {}, {"texto": "lo que sea"}])
def test_una_pregunta_sin_valor_esperado_no_exige_nada(valor):
    assert _validar(ValorEsperado(TipoValor.NINGUNO), valor) == Aceptado(
        TipoValor.NINGUNO, None)


# --- los mensajes no llevan jerga --------------------------------------------

@pytest.mark.parametrize("esperado, valor", [
    (ValorEsperado(TipoValor.FECHA, hoy=HOY), {"fecha_iso": "2020-01-01"}),
    (ValorEsperado(TipoValor.FECHA, hoy=HOY), {"fecha_iso": "xx"}),
    (ValorEsperado(TipoValor.FECHA, hoy=HOY), None),
    (ValorEsperado(TipoValor.OPCION, OPCIONES), {"opcion_id": "9"}),
    (ValorEsperado(TipoValor.OPCION, OPCIONES), None),
    (ValorEsperado(TipoValor.TEXTO), None),
    (ValorEsperado(TipoValor.TEXTO), {"texto": "a" * 99}),
])
def test_los_rechazos_hablan_en_neutro_y_sin_jerga(esperado, valor):
    r = _validar(esperado, valor)
    assert isinstance(r, Rechazado)
    for marca in ("fecha_iso", "opcion_id", "None", "null", "ISO", "(hasta",
                  "MotivoRechazo", "_"):
        assert marca not in r.mensaje, (marca, r.mensaje)
    assert r.razon.strip() and r.se_acepta.strip()
