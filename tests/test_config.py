"""`Config` guarda credenciales (`src/leda/config.py`). Su repr por
defecto las mostraba en texto plano -- mismo problema que `ClienteJev`
(`tests/test_jev.py::test_cliente_jev_repr_no_incluye_la_clave`), y con el
mismo riesgo: una excepción sin capturar que traiga esta instancia en la
traza las imprime enteras."""

from __future__ import annotations

from leda.config import Config


def test_config_repr_no_incluye_credenciales():
    cfg = Config(
        db_url="postgresql://usuario:clave-db@host/base",
        authority_db_url="postgresql://usuario:clave-auth@host/base2",
        llm_api_key="clave-llm-de-prueba",
        openrouter_api_key="clave-openrouter-de-prueba",
        webhook_secret="secreto-webhook-de-prueba",
    )

    representacion = repr(cfg)

    for valor in ("clave-db", "clave-auth", "clave-llm-de-prueba",
                  "clave-openrouter-de-prueba", "secreto-webhook-de-prueba"):
        assert valor not in representacion
