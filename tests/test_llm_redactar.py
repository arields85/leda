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

from leda.llm import (ProveedorAnthropic, ProveedorCompatible, ProveedorGemini,
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
        self.opciones = []

    def with_options(self, **kw):
        self.opciones.append(kw)
        return self


def test_anthropic_redacta_sin_herramientas():
    cliente = _Cliente()
    texto = ProveedorAnthropic("m", "sk-test", cliente=cliente).redactar("sis", "hechos")

    assert texto == "Hola."
    (llamada,) = cliente.messages.llamadas
    assert "tools" not in llamada and "tool_choice" not in llamada
    assert llamada["system"] == "sis"
    assert llamada["messages"] == [{"role": "user", "content": "hechos"}]


# ---------------------------------------------------------------- el plazo propio

def test_el_guionado_registra_el_plazo_con_que_se_lo_llamo():
    p = ProveedorGuionado(guion=[], borradores=["a", "b"])
    p.redactar("s", "h", plazo=3.0)
    p.redactar("s", "h")
    assert p.plazos == [3.0, None]


def test_compatible_con_plazo_corta_a_tiempo_y_no_reintenta(monkeypatch):
    intentos, plazos = [], []

    def respond(request: httpx.Request) -> httpx.Response:
        intentos.append(1)
        plazos.append(request.extensions["timeout"]["read"])
        raise httpx.ReadTimeout("colgado", request=request)

    with pytest.raises(openai.APITimeoutError):
        _compatible(monkeypatch, respond).redactar("s", "h", plazo=2.5)

    assert len(intentos) == 1                      # sin reintentos (el cliente tiene 2)
    assert plazos == [2.5]                         # el plazo propio, no el de 20 s


def test_compatible_sin_plazo_conserva_su_tiempo_y_sus_reintentos(monkeypatch):
    intentos = []

    def respond(request: httpx.Request) -> httpx.Response:
        intentos.append(request.extensions["timeout"]["read"])
        raise httpx.ReadTimeout("colgado", request=request)

    with pytest.raises(openai.APITimeoutError):
        _compatible(monkeypatch, respond).redactar("s", "h")

    assert len(intentos) == 3 and set(intentos) == {20}


def test_gemini_con_plazo_corta_a_tiempo_y_no_reintenta():
    intentos = []

    def respond(request: httpx.Request) -> httpx.Response:
        intentos.append(request.extensions["timeout"]["read"])
        raise httpx.ReadTimeout("colgado", request=request)

    http = httpx.Client(transport=httpx.MockTransport(respond))
    with pytest.raises(httpx.ReadTimeout):
        ProveedorGemini("m", "sk-test", cliente=http).redactar("s", "h", plazo=1.5)

    assert intentos == [1.5]


def test_anthropic_con_plazo_pide_un_cliente_sin_reintentos():
    cliente = _Cliente()
    ProveedorAnthropic("m", "sk-test", cliente=cliente).redactar("s", "h", plazo=2.0)
    assert cliente.opciones == [{"timeout": 2.0, "max_retries": 0}]


def test_el_tope_de_la_redaccion_es_corto():
    from leda.llm import MAX_TOKENS_REDACCION

    # Un mensaje de pocas oraciones más el JSON cabe de sobra: un tope mayor sólo
    # alarga una redacción descontrolada.
    assert MAX_TOKENS_REDACCION <= 256
