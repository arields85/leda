"""La credencial del modelo conversacional depende del proveedor configurado
(T8a): `openrouter` usa `LEDA_OPENROUTER_API_KEY` y el resto
`LEDA_LLM_API_KEY`. Nunca se manda la clave de un proveedor a otro. Fakes
puros, sin red ni credencial real; ninguna aserción imprime una clave."""

from __future__ import annotations

import pytest

from leda import llm
from leda.config import Config

CLAVE_LLM = "sk-llm-test"
CLAVE_OPENROUTER = "sk-or-test"


class _CursorFalso:
    def __init__(self, fila):
        self._fila = fila

    def execute(self, sql, params=None):
        pass

    def fetchone(self):
        return self._fila


def _fila(proveedor: str) -> dict:
    return {"proveedor": proveedor, "modelo": "modelo-x", "parametros": {}}


def _config(**kw) -> Config:
    base = {"llm_api_key": CLAVE_LLM, "openrouter_api_key": CLAVE_OPENROUTER}
    base.update(kw)
    return Config(**base)


def test_clave_llm_segun_proveedor():
    c = _config()
    assert c.clave_llm("openrouter") == CLAVE_OPENROUTER
    assert c.clave_llm("nan") == CLAVE_LLM
    assert c.clave_llm("gemini") == CLAVE_LLM


def test_variable_clave_llm_segun_proveedor():
    c = _config()
    assert c.variable_clave_llm("openrouter") == "LEDA_OPENROUTER_API_KEY"
    assert c.variable_clave_llm("nan") == "LEDA_LLM_API_KEY"
    assert c.variable_clave_llm("gemini") == "LEDA_LLM_API_KEY"


def test_desde_base_openrouter_usa_su_clave_y_su_direccion():
    p = llm.desde_base(_CursorFalso(_fila("openrouter")), "ws", _config())
    assert isinstance(p, llm.ProveedorCompatible)
    assert (p._c.api_key == CLAVE_OPENROUTER) is True
    assert (p._c.api_key != CLAVE_LLM) is True
    assert str(p._c.base_url).rstrip("/") == "https://openrouter.ai/api/v1"


def test_desde_base_openrouter_sin_su_clave_no_cae_a_la_otra():
    c = _config(openrouter_api_key="")
    with pytest.raises(LookupError) as exc:
        llm.desde_base(_CursorFalso(_fila("openrouter")), "ws", c)
    mensaje = str(exc.value)
    assert "LEDA_OPENROUTER_API_KEY" in mensaje
    assert "openrouter" in mensaje
    assert CLAVE_LLM not in mensaje


def test_desde_base_nan_sigue_usando_la_clave_llm():
    p = llm.desde_base(_CursorFalso(_fila("nan")), "ws", _config())
    assert isinstance(p, llm.ProveedorCompatible)
    assert (p._c.api_key == CLAVE_LLM) is True
    assert str(p._c.base_url).rstrip("/") == "https://api.nan.builders/v1"


def test_desde_base_sin_clave_llm_nombra_la_variable():
    c = _config(llm_api_key="")
    with pytest.raises(LookupError) as exc:
        llm.desde_base(_CursorFalso(_fila("nan")), "ws", c)
    assert "LEDA_LLM_API_KEY" in str(exc.value)
