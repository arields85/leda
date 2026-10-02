"""Pruebas de la credencial de Jev del banco (T6, `aclaracion-con-botones`):
sin `LEDA_OPENROUTER_API_KEY`, una corrida contra un modelo real no puede
degradar en silencio a un Jev guionado vacío -- tiene que fallar fuerte, con
un mensaje claro. Fakes puros, sin red ni credencial real."""

from __future__ import annotations

import pytest

from leda.config import Config

from tests.banco.conftest import _cliente_jev_real_o_falla


def test_sin_credencial_falla_fuerte_en_vez_de_degradar():
    config_sin_credencial = Config(openrouter_api_key="")
    with pytest.raises(pytest.fail.Exception) as exc:
        _cliente_jev_real_o_falla(config_sin_credencial)
    assert "LEDA_OPENROUTER_API_KEY" in str(exc.value)


def test_con_credencial_arma_el_cliente_desde_la_funcion_inyectada():
    config_con_credencial = Config(openrouter_api_key="sk-test")
    llamados = []

    def desde_base_falso(api_key):
        llamados.append(api_key)
        return "cliente-de-mentira"

    resultado = _cliente_jev_real_o_falla(
        config_con_credencial, desde_base=desde_base_falso)

    assert resultado == "cliente-de-mentira"
    assert llamados == ["sk-test"]
