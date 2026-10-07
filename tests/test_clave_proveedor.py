"""La credencial del modelo conversacional depende del proveedor configurado
(T8a): `openrouter` usa `LEDA_OPENROUTER_API_KEY` y el resto
`LEDA_LLM_API_KEY`. Nunca se manda la clave de un proveedor a otro. Fakes
puros, sin red ni credencial real; ninguna aserción imprime una clave.

Las pruebas de `llm.desde_base` se retiraron con él (E3-3); la prueba chica arma su
cliente con `config.clave_llm` (`prueba_chica/ia_real.py`)."""

from __future__ import annotations

from leda.config import Config

CLAVE_LLM = "sk-llm-test"
CLAVE_OPENROUTER = "sk-or-test"


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
