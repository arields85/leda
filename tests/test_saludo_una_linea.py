"""Un saludo suelto se contesta en UNA línea (R4-H1, R3-H8; ADR 0013).

Cuarta ronda por Telegram: a "hola", primer mensaje del día, Leda mandó "👋 Buen
día", una línea en blanco y "Hola Ariel, ¿en qué te ayudo?", con los tres botones
genéricos. Regla del usuario (2026-09-30): una sola línea, "👋 Buen día Ariel, ¿en
qué te ayudo?"; y (R3-H8) un saludo sin rama abierta se contesta con un saludo y una
pregunta abierta, nunca repitiendo la lista de tareas.

Es un comando de la lista cerrada del ruteo (`IntentAction.GREETING`): el modelo sólo
clasifica; el texto lo arma el código, sin texto libre del modelo. Cuando el saludo
del día le corresponde a la persona, la línea lleva el saludo del día (`saludo.py`) y
el despachador no lo antepone otra vez; si ya lo recibió hoy, "Hola {nombre}, ...".
"""

from __future__ import annotations

import pytest

from leda import saludo as S
from leda.llm import (IntentAction, Llamada, RouteEnvelope, RoutingError, ROUTER_TOOL,
                      ROUTER_SYSTEM)


def test_el_saludo_suelto_es_un_comando_de_la_lista_cerrada_del_ruteo():
    assert IntentAction.GREETING.value in ROUTER_TOOL["input_schema"][
        "properties"]["action"]["enum"]
    ruta = RouteEnvelope(calls=(Llamada(
        "r", "route_intent", {"action": IntentAction.GREETING.value}),)).validate()
    assert ruta.action is IntentAction.GREETING
    assert IntentAction.GREETING.value in ROUTER_SYSTEM


def test_un_saludo_con_propuestas_de_tarea_sigue_siendo_invalido():
    sobre = RouteEnvelope(calls=(Llamada("r", "route_intent", {
        "action": IntentAction.GREETING.value, "task": {"title": "X"}}),))
    with pytest.raises(RoutingError, match="Only task creation can contain task "
                                           "proposals"):
        sobre.validate()


def test_una_persona_sin_nombre_no_lo_inventa():
    assert S.linea_de_saludo(None, None) == "Hola, ¿en qué te ayudo?"
    assert S.linea_de_saludo("Ariel De Simone", None) == (
        "Hola Ariel, ¿en qué te ayudo?")
    assert S.linea_de_saludo("Ariel De Simone", S.SALUDO_MANANA) == (
        "👋 Buen día Ariel, ¿en qué te ayudo?")
    assert S.linea_de_saludo(None, S.SALUDO_TARDE) == (
        "👋 Buenas tardes, ¿en qué te ayudo?")
