"""Dónde y cuánto esperar a la IA: lo que queda del proveedor de modelo.

Qué modelo usar sale de `model_config`, en la base, editable desde la consola.
La credencial sale del entorno (`config.clave_llm`). Ninguno de los dos está en el
pack ni en el núcleo.

Los proveedores y el ruteo de intención de los flujos A y B se retiraron con ellos
(E3-3). Quedan las direcciones de los proveedores (`cli modelos`, el motor y la prueba
chica) y la validación del tiempo máximo y los reintentos (`tiempos`), que usa el
cliente de la IA real del motor (`leda.motor.ia_real`). `_tiempos` es el mismo, con el
nombre que usan la prueba chica y su prueba (`tests/test_tiempo_maximo_modelo.py`).
"""

from __future__ import annotations

import math


# Tiempo máximo por intento y reintentos de los proveedores conversacionales,
# ajustables con `timeout_s` y `reintentos` en `model_config.parametros`. NaN
# colgó ~93-95 s el 1,3 % de las llamadas (5 de 385) y el SDK esperaba hasta
# 600 s; las llamadas normales tardan 1-4 s (p90 ~5 s).
TIMEOUT_MODELO_S = 20
REINTENTOS_MODELO = 2


def tiempos(parametros: dict) -> tuple[float, int]:
    """Valida los dos parámetros: un `timeout_s` nulo desactivaría el tiempo
    máximo y un texto rompería el reintento. Un valor inválido falla
    nombrando el parámetro (como una clave faltante), nunca se reemplaza en
    silencio por el valor por defecto."""
    timeout = parametros.get("timeout_s", TIMEOUT_MODELO_S)
    reintentos = parametros.get("reintentos", REINTENTOS_MODELO)
    if (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout) or timeout <= 0):
        raise ValueError(
            f"timeout_s debe ser un número de segundos mayor que 0; vino {timeout!r}.")
    # Un JSON escrito `2.0` es un entero lógico: se acepta y se normaliza.
    if (isinstance(reintentos, float) and math.isfinite(reintentos)
            and reintentos.is_integer()):
        reintentos = int(reintentos)
    if (isinstance(reintentos, bool) or not isinstance(reintentos, int)
            or reintentos < 0):
        raise ValueError(
            f"reintentos debe ser un entero de 0 o más; vino {reintentos!r}.")
    return timeout, reintentos


_tiempos = tiempos


GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"


BASE_URLS = {
    "openai":     "https://api.openai.com/v1",
    "groq":       "https://api.groq.com/openai/v1",
    "deepseek":   "https://api.deepseek.com/v1",
    "mistral":    "https://api.mistral.ai/v1",
    "xai":        "https://api.x.ai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "nan":        "https://api.nan.builders/v1",
    "local":      "http://localhost:11434/v1",
}
