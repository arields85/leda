"""Contrato del ruteo con una pregunta pendiente (T9-R1a, ADR 0013 regla 1).

Sin pregunta pendiente, el pedido, el esquema y la validación son los de
siempre. Con una, el ruteo pide un campo obligatorio `respecto_pendiente` de
una lista cerrada de comandos y lo valida tipado. Todo con clientes falsos:
nunca hay red.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

import prisma.llm as llm
from prisma.llm import (IntentAction, IntentRoute, Llamada, ProveedorAnthropic,
                         ProveedorCompatible, ProveedorGemini, ProveedorGuionado,
                         RespectoPendiente, RouteEnvelope, RoutingError)

PENDIENTE = "la evidencia de la entrega de «Dashboard de lotes»"
COMANDOS = ["responde", "corrige", "cancela", "otro_tema", "charla", "dudoso",
            "no_puedo"]
ADAPTADORES = ["anthropic", "gemini", "openai"]


def _proveedor(adapter, payload, capturas: list):
    """Un proveedor real con un cliente falso que anota cada pedido y
    contesta con una llamada `route_intent` con `payload`."""
    if adapter == "anthropic":
        def create(**kwargs):
            capturas.append(kwargs)
            return SimpleNamespace(content=[SimpleNamespace(
                type="tool_use", id="c0", name="route_intent", input=payload)])
        cliente = SimpleNamespace(messages=SimpleNamespace(create=create))
        return ProveedorAnthropic("mock-model", "unused", cliente=cliente)
    if adapter == "gemini":
        class Http:
            def post(self, url, json=None, **kwargs):
                capturas.append(json)
                return SimpleNamespace(
                    raise_for_status=lambda: None,
                    json=lambda: {"candidates": [{"content": {"parts": [
                        {"functionCall": {"name": "route_intent",
                                          "args": payload}}]}}]})
        return ProveedorGemini("mock-model", "unused", cliente=Http())

    def create(**kwargs):
        capturas.append(kwargs)
        message = SimpleNamespace(content=None, tool_calls=[SimpleNamespace(
            id="c0", function=SimpleNamespace(
                name="route_intent", arguments=json.dumps(payload)))])
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])
    cliente = SimpleNamespace(chat=SimpleNamespace(
        completions=SimpleNamespace(create=create)))
    return ProveedorCompatible(
        "mock-model", "unused", "https://example.invalid", cliente=cliente)


def _esquema_y_sistema(adapter, pedido):
    if adapter == "anthropic":
        return pedido["tools"][0]["input_schema"], pedido["system"]
    if adapter == "gemini":
        declaracion = pedido["tools"][0]["function_declarations"][0]
        return declaracion["parameters"], pedido["system_instruction"]["parts"][0]["text"]
    return (pedido["tools"][0]["function"]["parameters"],
            pedido["messages"][0]["content"])


@pytest.mark.parametrize("adapter", ADAPTADORES)
def test_sin_pendiente_el_pedido_y_el_esquema_son_los_de_siempre(adapter):
    capturas: list = []
    proveedor = _proveedor(adapter, {"action": "normal_conversation"}, capturas)

    route = proveedor.route_intent("hola")

    esquema, sistema = _esquema_y_sistema(adapter, capturas[0])
    assert "respecto_pendiente" not in esquema["properties"]
    assert esquema["required"] == ["action"]
    assert sistema == llm.ROUTER_SYSTEM
    assert route.respecto_pendiente is None


@pytest.mark.parametrize("adapter", ADAPTADORES)
def test_con_pendiente_el_campo_es_obligatorio_y_de_lista_cerrada(adapter):
    capturas: list = []
    proveedor = _proveedor(
        adapter, {"action": "normal_conversation",
                  "respecto_pendiente": "charla"}, capturas)

    route = proveedor.route_intent("hola", pendiente=PENDIENTE)

    esquema, sistema = _esquema_y_sistema(adapter, capturas[0])
    assert esquema["properties"]["respecto_pendiente"]["enum"] == COMANDOS
    assert "respecto_pendiente" in esquema["required"]
    assert "action" in esquema["required"]
    assert sistema.startswith(llm.ROUTER_SYSTEM)
    assert PENDIENTE in sistema
    for comando in COMANDOS:
        assert comando in sistema           # cada comando está explicado
    assert route.respecto_pendiente is RespectoPendiente.CHARLA
    assert route.action is IntentAction.NORMAL_CONVERSATION


@pytest.mark.parametrize("adapter", ADAPTADORES)
def test_con_pendiente_el_esquema_global_no_se_muta(adapter):
    capturas: list = []
    proveedor = _proveedor(
        adapter, {"action": "normal_conversation",
                  "respecto_pendiente": "responde"}, capturas)
    proveedor.route_intent("un link", pendiente=PENDIENTE)

    assert "respecto_pendiente" not in llm.ROUTER_TOOL["input_schema"]["properties"]
    assert llm.ROUTER_TOOL["input_schema"]["required"] == ["action"]


@pytest.mark.parametrize("adapter", ADAPTADORES)
@pytest.mark.parametrize("comando", COMANDOS)
def test_con_pendiente_cada_comando_de_la_lista_se_acepta(adapter, comando):
    proveedor = _proveedor(
        adapter, {"action": "normal_conversation",
                  "respecto_pendiente": comando}, [])

    assert proveedor.route_intent(
        "x", pendiente=PENDIENTE).respecto_pendiente.value == comando


@pytest.mark.parametrize("adapter", ADAPTADORES)
@pytest.mark.parametrize("respecto", [
    pytest.param(None, id="ausente"),
    pytest.param("otra_cosa", id="valor-desconocido"),
    pytest.param("", id="vacio"),
    pytest.param(3, id="no-texto"),
    pytest.param(["responde"], id="lista"),
    pytest.param("RESPONDE", id="mayusculas"),
])
def test_con_pendiente_la_validacion_rechaza_un_campo_faltante_o_invalido(
        adapter, respecto):
    payload = {"action": "normal_conversation"}
    if respecto is not None:
        payload["respecto_pendiente"] = respecto
    proveedor = _proveedor(adapter, payload, [])

    with pytest.raises(RoutingError):
        proveedor.route_intent("hola", pendiente=PENDIENTE)


@pytest.mark.parametrize("adapter", ADAPTADORES)
def test_sin_pendiente_un_campo_respecto_pendiente_se_rechaza(adapter):
    proveedor = _proveedor(
        adapter, {"action": "normal_conversation",
                  "respecto_pendiente": "responde"}, [])

    with pytest.raises(RoutingError):
        proveedor.route_intent("hola")


def test_el_sobre_valida_con_y_sin_pendiente():
    sobre = RouteEnvelope(calls=(Llamada("c", "route_intent", {
        "action": "normal_conversation", "respecto_pendiente": "cancela"}),))

    assert sobre.validate(con_pendiente=True).respecto_pendiente is (
        RespectoPendiente.CANCELA)
    with pytest.raises(RoutingError):
        sobre.validate()


def test_el_guionado_anota_la_pregunta_pendiente_y_devuelve_el_comando():
    proveedor = ProveedorGuionado([], rutas=[
        IntentRoute(IntentAction.NORMAL_CONVERSATION,
                    respecto_pendiente=RespectoPendiente.CHARLA)])

    route = proveedor.route_intent("hola", pendiente=PENDIENTE)

    assert route.respecto_pendiente is RespectoPendiente.CHARLA
    assert proveedor.pendientes == [PENDIENTE]
    assert proveedor.ruteados == ["hola"]


def test_el_guionado_sin_comando_escrito_trata_el_mensaje_como_el_dato():
    """Un guion que no dice nada sobre la pregunta pendiente conserva el
    comportamiento de antes de T9-R1a: el mensaje es el dato."""
    proveedor = ProveedorGuionado([])

    route = proveedor.route_intent("un link", pendiente=PENDIENTE)

    assert route.respecto_pendiente is RespectoPendiente.RESPONDE


def test_el_guionado_con_sobre_valida_estricto_con_pendiente():
    sobre = RouteEnvelope(calls=(Llamada("c", "route_intent", {
        "action": "normal_conversation"}),))
    proveedor = ProveedorGuionado([], rutas=[sobre])

    with pytest.raises(RoutingError):
        proveedor.route_intent("hola", pendiente=PENDIENTE)


def test_el_guionado_sin_pendiente_no_agrega_el_campo():
    proveedor = ProveedorGuionado([], rutas=[
        IntentRoute(IntentAction.NORMAL_CONVERSATION)])

    assert proveedor.route_intent("hola").respecto_pendiente is None
    assert proveedor.pendientes == [None]


# Un mensaje que responde a una pregunta pendiente puede parecer el título de
# una tarea ("Objetivo simulado de Cablear tablero…"): el modelo lo ruteó como
# `normal_conversation` con propuestas de tarea (banco b-0022, RoutingError).
# Con la pregunta pendiente la decisión es `respecto_pendiente`; las propuestas
# que sobran no tiran abajo la ruta.
PAYLOAD_CON_PROPUESTAS_SOBRANTES = {
    "action": "normal_conversation", "respecto_pendiente": "responde",
    "trabajos": ["cablear tablero"],
    "task": {"title": "Cablear tablero", "objective": "Objetivo simulado"}}


@pytest.mark.parametrize("adapter", ADAPTADORES)
def test_con_pendiente_las_propuestas_sobrantes_de_una_conversacion_se_descartan(
        adapter):
    proveedor = _proveedor(adapter, dict(PAYLOAD_CON_PROPUESTAS_SOBRANTES), [])

    route = proveedor.route_intent("objetivo simulado", pendiente=PENDIENTE)

    assert route.action is IntentAction.NORMAL_CONVERSATION
    assert route.respecto_pendiente is RespectoPendiente.RESPONDE
    assert route.task == {}
    assert route.trabajos == ("cablear tablero",)


@pytest.mark.parametrize("adapter", ADAPTADORES)
def test_sin_pendiente_una_conversacion_con_propuestas_sigue_rechazada(adapter):
    payload = dict(PAYLOAD_CON_PROPUESTAS_SOBRANTES)
    del payload["respecto_pendiente"]
    proveedor = _proveedor(adapter, payload, [])

    with pytest.raises(RoutingError):
        proveedor.route_intent("objetivo simulado")


def test_con_pendiente_las_propuestas_malformadas_siguen_rechazadas():
    for task in ({"campo_inventado": "x"}, {"title": 3}):
        sobre = RouteEnvelope(calls=(Llamada("c", "route_intent", {
            "action": "normal_conversation", "respecto_pendiente": "responde",
            "task": task}),))
        with pytest.raises(RoutingError):
            sobre.validate(con_pendiente=True)


def test_con_pendiente_una_accion_de_tarea_conserva_sus_propuestas():
    sobre = RouteEnvelope(calls=(Llamada("c", "route_intent", {
        "action": "start_task_intake", "respecto_pendiente": "otro_tema",
        "task": {"title": "Cablear tablero"}}),))

    route = sobre.validate(con_pendiente=True)

    assert route.task == {"title": "Cablear tablero"}
