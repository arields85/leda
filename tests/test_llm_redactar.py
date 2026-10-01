"""La llamada de redacción sin herramientas de los proveedores (ADR 0014, F6a).

`redactar(sistema, hechos) -> str` le pide al modelo el texto visible de un
turno. No lleva herramientas (el modelo no actúa, sólo escribe) y tiene el
mismo tiempo máximo y reintento que las otras llamadas. Sin red: transportes
falsos.
"""

from __future__ import annotations

import json

import httpx
import openai
import pytest

from prisma.llm import (ProveedorAnthropic, ProveedorCompatible, ProveedorGemini,
                        ProveedorGuionado)


def _completion(texto: str) -> dict:
    return {
        "id": "c1", "object": "chat.completion", "created": 0, "model": "m",
        "choices": [{"index": 0, "finish_reason": "stop",
                     "message": {"role": "assistant", "content": texto}}],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }


# ---------------------------------------------------------------- guionado

def test_el_guionado_devuelve_los_borradores_en_orden_y_los_registra():
    p = ProveedorGuionado(guion=[], borradores=["uno", "dos"])
    assert p.redactar("sistema", "hechos 1") == "uno"
    assert p.redactar("sistema", "hechos 2") == "dos"
    assert p.redactados == [("sistema", "hechos 1"), ("sistema", "hechos 2")]


def test_el_guionado_lanza_el_error_guionado():
    p = ProveedorGuionado(guion=[], borradores=[TimeoutError("colgado")])
    with pytest.raises(TimeoutError):
        p.redactar("s", "h")


def test_el_guionado_sin_borrador_devuelve_texto_vacio():
    assert ProveedorGuionado(guion=[]).redactar("s", "h") == ""


# ---------------------------------------------------------------- compatible

def _compatible(monkeypatch, respond, parametros=None):
    http = httpx.Client(transport=httpx.MockTransport(respond))
    real = openai.OpenAI
    monkeypatch.setattr(openai, "OpenAI", lambda **kw: real(http_client=http, **kw))
    monkeypatch.setattr("time.sleep", lambda s: None)
    return ProveedorCompatible("m", "sk-test", "http://localhost/v1", parametros)


def test_compatible_redacta_sin_herramientas(monkeypatch):
    cuerpos = []

    def respond(request: httpx.Request) -> httpx.Response:
        cuerpos.append(json.loads(request.content))
        return httpx.Response(200, json=_completion("  Listo, quedó.  "))

    texto = _compatible(monkeypatch, respond).redactar("sistema", "hechos")

    assert texto == "Listo, quedó."
    assert "tools" not in cuerpos[0] and "tool_choice" not in cuerpos[0]
    assert cuerpos[0]["messages"][0] == {"role": "system", "content": "sistema"}
    assert cuerpos[0]["messages"][1] == {"role": "user", "content": "hechos"}


def test_compatible_reintenta_un_timeout_al_redactar(monkeypatch):
    intentos = []

    def respond(request: httpx.Request) -> httpx.Response:
        intentos.append(1)
        if len(intentos) == 1:
            raise httpx.ReadTimeout("colgado", request=request)
        return httpx.Response(200, json=_completion("hola"))

    assert _compatible(monkeypatch, respond).redactar("s", "h") == "hola"
    assert len(intentos) == 2


def test_compatible_agotado_al_redactar_lanza_el_timeout(monkeypatch):
    def respond(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("colgado", request=request)

    with pytest.raises(openai.APITimeoutError):
        _compatible(monkeypatch, respond, {"reintentos": 1}).redactar("s", "h")


# ---------------------------------------------------------------- gemini

def test_gemini_redacta_sin_herramientas_y_reintenta_un_timeout():
    cuerpos = []

    def respond(request: httpx.Request) -> httpx.Response:
        cuerpos.append(json.loads(request.content))
        if len(cuerpos) == 1:
            raise httpx.ReadTimeout("colgado", request=request)
        return httpx.Response(200, json={"candidates": [
            {"content": {"parts": [{"text": " Hola. "}]}}]})

    http = httpx.Client(transport=httpx.MockTransport(respond))
    texto = ProveedorGemini("m", "sk-test", cliente=http).redactar("sis", "hechos")

    assert texto == "Hola."
    assert len(cuerpos) == 2
    assert "tools" not in cuerpos[1] and "toolConfig" not in cuerpos[1]
    assert cuerpos[1]["system_instruction"]["parts"][0]["text"] == "sis"


def test_gemini_sin_candidatos_devuelve_texto_vacio():
    http = httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json={"candidates": []})))
    assert ProveedorGemini("m", "sk-test", cliente=http).redactar("s", "h") == ""


# ---------------------------------------------------------------- anthropic

class _Bloque:
    type = "text"

    def __init__(self, text):
        self.text = text


class _Mensajes:
    def __init__(self):
        self.llamadas = []

    def create(self, **kw):
        self.llamadas.append(kw)

        class _R:
            content = [_Bloque(" Hola. ")]

        return _R()


class _Cliente:
    def __init__(self):
        self.messages = _Mensajes()


def test_anthropic_redacta_sin_herramientas():
    cliente = _Cliente()
    texto = ProveedorAnthropic("m", "sk-test", cliente=cliente).redactar("sis", "hechos")

    assert texto == "Hola."
    (llamada,) = cliente.messages.llamadas
    assert "tools" not in llamada and "tool_choice" not in llamada
    assert llamada["system"] == "sis"
    assert llamada["messages"] == [{"role": "user", "content": "hechos"}]
