"""T8c-4: cada intento al modelo tiene un tiempo máximo y un reintento acotado.

Evidencia: NaN colgó ~93-95 s el 1,3 % de las llamadas y el cliente esperaba
hasta 600 s. Sin red: transportes falsos de `httpx`.
"""

from __future__ import annotations

import anthropic
import httpx
import openai
import pytest

import prisma.llm as llm
from prisma.llm import ProveedorAnthropic, ProveedorCompatible, ProveedorGemini


def _completion(texto: str) -> dict:
    return {
        "id": "c1", "object": "chat.completion", "created": 0, "model": "m",
        "choices": [{"index": 0, "finish_reason": "stop",
                     "message": {"role": "assistant", "content": texto}}],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }


def test_valores_por_defecto_documentados():
    assert llm.TIMEOUT_MODELO_S == 20
    assert llm.REINTENTOS_MODELO == 2


def test_compatible_usa_los_valores_por_defecto():
    p = ProveedorCompatible("m", "sk-test", "http://localhost/v1")
    assert p._c.timeout == 20
    assert p._c.max_retries == 2


def test_compatible_toma_timeout_y_reintentos_de_los_parametros():
    p = ProveedorCompatible("m", "sk-test", "http://localhost/v1",
                            {"timeout_s": 7, "reintentos": 1})
    assert p._c.timeout == 7
    assert p._c.max_retries == 1


def test_anthropic_usa_defaults_y_parametros():
    assert ProveedorAnthropic("m", "sk-test")._c.timeout == 20
    assert ProveedorAnthropic("m", "sk-test")._c.max_retries == 2
    p = ProveedorAnthropic("m", "sk-test", {"timeout_s": 7, "reintentos": 0})
    assert p._c.timeout == 7
    assert p._c.max_retries == 0


def test_gemini_usa_timeout_por_defecto_y_de_parametros():
    assert ProveedorGemini("m", "sk-test")._http.timeout.read == 20
    p = ProveedorGemini("m", "sk-test", {"timeout_s": 7})
    assert p._http.timeout.read == 7


def test_gemini_reintenta_un_timeout():
    intentos = []

    def respond(request: httpx.Request) -> httpx.Response:
        intentos.append(1)
        if len(intentos) == 1:
            raise httpx.ReadTimeout("colgado", request=request)
        return httpx.Response(200, json={"candidates": [
            {"content": {"parts": [{"text": "hola"}]}}]})

    http = httpx.Client(transport=httpx.MockTransport(respond))
    r = ProveedorGemini("m", "sk-test", cliente=http).responder("s", [], [])
    assert r.texto == "hola"
    assert len(intentos) == 2


def test_gemini_agota_reintentos_y_propaga_el_timeout():
    def respond(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("colgado", request=request)

    http = httpx.Client(transport=httpx.MockTransport(respond))
    p = ProveedorGemini("m", "sk-test", {"reintentos": 1}, cliente=http)
    with pytest.raises(httpx.TimeoutException):
        p.responder("s", [], [])


def test_compatible_reintenta_un_timeout_y_responde(monkeypatch):
    intentos = []

    def respond(request: httpx.Request) -> httpx.Response:
        intentos.append(1)
        if len(intentos) == 1:
            raise httpx.ReadTimeout("colgado", request=request)
        return httpx.Response(200, json=_completion("hola"))

    http = httpx.Client(transport=httpx.MockTransport(respond))
    real = openai.OpenAI
    monkeypatch.setattr(
        openai, "OpenAI", lambda **kw: real(http_client=http, **kw))
    monkeypatch.setattr("time.sleep", lambda s: None)

    r = ProveedorCompatible(
        "m", "sk-test", "http://localhost/v1").responder("s", [], [])

    assert r.texto == "hola"
    assert len(intentos) == 2


def test_compatible_agotado_lanza_error_de_timeout(monkeypatch):
    def respond(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("colgado", request=request)

    http = httpx.Client(transport=httpx.MockTransport(respond))
    real = openai.OpenAI
    monkeypatch.setattr(
        openai, "OpenAI", lambda **kw: real(http_client=http, **kw))
    monkeypatch.setattr("time.sleep", lambda s: None)

    p = ProveedorCompatible("m", "sk-test", "http://localhost/v1",
                            {"reintentos": 1})
    with pytest.raises(openai.APITimeoutError):
        p.responder("s", [], [])


class _Cur:
    def __init__(self, fila):
        self._fila = fila

    def execute(self, *a):
        pass

    def fetchone(self):
        return self._fila


class _Claves:
    def clave_llm(self, proveedor):
        return "sk-test"

    def variable_clave_llm(self, proveedor):
        return "X"


@pytest.mark.parametrize("proveedor,extra", [("nan", {}), ("anthropic", {})])
def test_desde_base_pasa_los_parametros_al_cliente(proveedor, extra):
    fila = {"proveedor": proveedor, "modelo": "m",
            "parametros": {"timeout_s": 9, "reintentos": 0, **extra}}
    p = llm.desde_base(_Cur(fila), "ws", _Claves())
    assert p._c.timeout == 9
    assert p._c.max_retries == 0
