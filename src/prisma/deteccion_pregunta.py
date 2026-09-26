"""Detectar si un texto le pregunta algo a la persona.

Una sola implementación, compartida por dos lados que antes la tenían cada
uno por su cuenta:

  - el servidor (`agente.responder`, T4b, ADR 0007 "Prisma orienta, no
    charla"): si el turno cierra con una pregunta en texto abierto y sin
    ningún juego de botones propio, agrega el cierre genérico de tres
    botones;
  - el banco conversacional (`tests/banco/comprobadores.py::
    comprobar_pregunta_con_opciones`, T4): falla un escenario si Prisma
    pregunta sin ofrecer botones.

Vive en `src/prisma/` porque el servidor la necesita en tiempo de ejecución
-- `tests/banco` puede importar de `src/prisma/`, nunca al revés
(`AGENTS.md`).
"""

from __future__ import annotations

import re
import unicodedata

# Pedido directo de la elección faltante en imperativo, sin "?" (T7, banco
# conversacional, puntos I y N): "Decime cuál de las dos y lo hago" (b-0011),
# "decime cuál doy por resuelto" (b-0012), "Contame qué la está frenando"
# (b-0010), "decime qué preferís y lo muevo" (b-0011). Lista chica y cerrada,
# a propósito: "decime"/"contame"/"confirmame" (verbos genéricos de pedir
# información) sólo cuentan cuando además aparece "cuál" o "qué" -- si no,
# cualquier cierre cordial ("decime si necesitás algo más") contaría como
# pregunta. "Elegí" es la excepción: el verbo mismo ya es un pedido de
# elección. "qué" se busca con borde de palabra (`\bque\b`), no como
# subcadena, para no disparar con "porque"/"aunque".
_VERBOS_PEDIDO_ELECCION = ("decime", "decinos", "contame", "confirmame")
_MARCADOR_CUAL = "cual"
_MARCADOR_QUE = re.compile(r"\bque\b")


def _normalizar(texto: str) -> str:
    """Minúsculas y sin acentos, para comparar sin depender de tildes."""
    texto = unicodedata.normalize("NFKD", texto.strip().lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def pide_elegir_en_imperativo(texto: str) -> bool:
    normalizado = _normalizar(texto)
    if "elegi" in normalizado:
        return True
    if not any(verbo in normalizado for verbo in _VERBOS_PEDIDO_ELECCION):
        return False
    return _MARCADOR_CUAL in normalizado or bool(_MARCADOR_QUE.search(normalizado))


def hace_pregunta(texto: str) -> bool:
    """Detecta si el texto le pregunta algo a la persona: signo de
    interrogación, o un pedido de elección en imperativo
    (`pide_elegir_en_imperativo`)."""
    return "?" in texto or pide_elegir_en_imperativo(texto)
