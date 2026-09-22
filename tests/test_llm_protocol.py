from __future__ import annotations

import json
from types import SimpleNamespace

import anthropic
import httpx
import pytest

from prisma.llm import (IntentAction, IntentRoute, Llamada, ProveedorAnthropic,
                         ProveedorCompatible, ProveedorGemini, ProveedorGuionado,
                         RouteEnvelope, RoutingError)


def _message(content):
    return {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "model": "mock-model",
        "content": content,
        "stop_reason": "tool_use",
        "stop_sequence": None,
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }


def test_anthropic_router_forces_one_typed_tool_over_http():
    requests = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=_message([{
            "type": "tool_use",
            "id": "route_1",
            "name": "route_intent",
            "input": {
                "action": "start_task_intake",
                "task": {"title": "Inspect the backup pump"},
            },
        }]))

    http = httpx.Client(transport=httpx.MockTransport(respond))
    client = anthropic.Anthropic(api_key="test-key", http_client=http)
    provider = ProveedorAnthropic("mock-model", "unused", cliente=client)

    route = provider.route_intent("Could you turn the pump check into work?")

    assert route == IntentRoute(
        IntentAction.START_TASK_INTAKE,
        {"title": "Inspect the backup pump"},
    )
    body = requests[0]
    assert body["tool_choice"] == {"type": "tool", "name": "route_intent"}
    assert [tool["name"] for tool in body["tools"]] == ["route_intent"]
    assert body["tools"][0]["input_schema"]["properties"]["action"]["enum"] == [
        "start_task_intake", "normal_conversation",
    ]


@pytest.mark.parametrize("content", [
    [{"type": "text", "text": "start_task_intake"}],
    [{"type": "tool_use", "id": "x", "name": "another_tool",
      "input": {"action": "start_task_intake"}}],
    [{"type": "tool_use", "id": "x", "name": "route_intent",
      "input": {"action": "delete_everything"}}],
])
def test_anthropic_router_rejects_raw_text_wrong_tool_and_wrong_action(content):
    class Messages:
        def create(self, **kwargs):
            return SimpleNamespace(content=[SimpleNamespace(**block)
                                            for block in content])

    client = type("Client", (), {"messages": Messages()})()
    provider = ProveedorAnthropic("mock-model", "unused", cliente=client)

    with pytest.raises(RoutingError):
        provider.route_intent("adversarial input")


def test_guided_provider_exposes_typed_routes_separately_from_main_turns():
    expected = IntentRoute(IntentAction.NORMAL_CONVERSATION)
    provider = ProveedorGuionado([], rutas=[expected])

    assert provider.route_intent("what is open?") == expected
    assert provider.ruteados == ["what is open?"]


class _GeminiHttp:
    def __init__(self, parts):
        self.parts = parts

    def post(self, *args, **kwargs):
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"candidates": [{"content": {"parts": self.parts}}]},
        )


def _protocol_provider(adapter, calls, *, text=None):
    if adapter == "anthropic":
        content = []
        if text is not None:
            content.append(SimpleNamespace(type="text", text=text))
        content.extend(SimpleNamespace(
            type="tool_use", id=f"call-{index}", name=name, input=args,
        ) for index, (name, args) in enumerate(calls))
        client = SimpleNamespace(messages=SimpleNamespace(
            create=lambda **kwargs: SimpleNamespace(content=content)))
        return ProveedorAnthropic("mock-model", "unused", cliente=client)
    if adapter == "gemini":
        parts = []
        if text is not None:
            parts.append({"text": text})
        parts.extend({"functionCall": {"name": name, "args": args}}
                     for name, args in calls)
        return ProveedorGemini(
            "mock-model", "unused", cliente=_GeminiHttp(parts))
    if adapter == "openai":
        tool_calls = [SimpleNamespace(
            id=f"call-{index}",
            function=SimpleNamespace(name=name, arguments=json.dumps(args)),
        ) for index, (name, args) in enumerate(calls)]
        message = SimpleNamespace(content=text, tool_calls=tool_calls)
        completions = SimpleNamespace(create=lambda **kwargs: SimpleNamespace(
            choices=[SimpleNamespace(message=message)]))
        client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
        return ProveedorCompatible(
            "mock-model", "unused", "https://example.invalid", cliente=client)
    envelope = RouteEnvelope(
        content=(() if text is None else (text,)),
        calls=tuple(Llamada(f"call-{index}", name, args)
                    for index, (name, args) in enumerate(calls)),
    )
    return ProveedorGuionado([], rutas=[envelope])


@pytest.mark.parametrize("adapter", ["anthropic", "gemini", "openai", "guided"])
def test_every_router_adapter_accepts_the_same_strict_valid_envelope(adapter):
    provider = _protocol_provider(adapter, [(
        "route_intent",
        {"action": "start_task_intake", "task": {"title": "Check pump"}},
    )])

    assert provider.route_intent("Create the task") == IntentRoute(
        IntentAction.START_TASK_INTAKE, {"title": "Check pump"})


INVALID_ENVELOPES = [
    pytest.param([("route_intent", {"action": "normal_conversation"})],
                 "I chose a route", id="mixed-text"),
    pytest.param([], None, id="missing-call"),
    pytest.param([("unknown_tool", {"action": "normal_conversation"})],
                 None, id="unknown-tool"),
    pytest.param([
        ("route_intent", {"action": "normal_conversation"}),
        ("route_intent", {"action": "normal_conversation"}),
    ], None, id="multiple-calls"),
    pytest.param([("route_intent", "not-an-object")], None, id="malformed-args"),
    pytest.param([("route_intent", {})], None, id="missing-action"),
    pytest.param([("route_intent", {"action": "unknown"})],
                 None, id="unknown-action"),
    pytest.param([("route_intent", {
        "action": "normal_conversation", "extra": True,
    })], None, id="extra-envelope-field"),
    pytest.param([("route_intent", {
        "action": "start_task_intake", "task": None,
    })], None, id="null-task"),
    pytest.param([("route_intent", {
        "action": "start_task_intake", "task": False,
    })], None, id="false-task"),
    pytest.param([("route_intent", {
        "action": "start_task_intake", "task": [],
    })], None, id="list-task"),
    pytest.param([("route_intent", {
        "action": "start_task_intake", "task": "title",
    })], None, id="string-task"),
    pytest.param([("route_intent", {
        "action": "start_task_intake", "task": {"unknown": "value"},
    })], None, id="extra-task-field"),
]


@pytest.mark.parametrize("adapter", ["anthropic", "gemini", "openai", "guided"])
@pytest.mark.parametrize(("calls", "text"), INVALID_ENVELOPES)
def test_every_router_adapter_rejects_the_same_invalid_protocol_matrix(
        adapter, calls, text):
    provider = _protocol_provider(adapter, calls, text=text)

    with pytest.raises(RoutingError):
        provider.route_intent("adversarial input")


def test_openai_router_rejects_malformed_json_arguments():
    call = SimpleNamespace(
        id="call-1",
        function=SimpleNamespace(name="route_intent", arguments="{"),
    )
    message = SimpleNamespace(content=None, tool_calls=[call])
    completions = SimpleNamespace(create=lambda **kwargs: SimpleNamespace(
        choices=[SimpleNamespace(message=message)]))
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    provider = ProveedorCompatible(
        "mock-model", "unused", "https://example.invalid", cliente=client)

    with pytest.raises(RoutingError):
        provider.route_intent("adversarial input")
