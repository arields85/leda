"""La llamada del turno del alta conducida de los proveedores (ADR 0014, enmienda
del 2026-10-01, M2).

`conducir_alta(sistema, historial, hechos) -> salida` le pide al modelo UNA llamada
forzada a la herramienta `conducir_alta` (salida estructurada cerrada de
`alta_turno.ESQUEMA_SALIDA`) con la conversación como mensajes previos y los hechos
del turno como último mensaje. Sin red: transportes falsos.

También cubre el armado del historial, a prueba de roles que no se alternan (los
proveedores estrictos rechazan dos mensajes seguidos del mismo lado).
"""

from __future__ import annotations

import json

import httpx
import openai
import pytest

from leda import llm
from leda.alta_turno import ESQUEMA_SALIDA, NOMBRE_HERRAMIENTA
from leda.llm import (ProveedorAnthropic, ProveedorCompatible, ProveedorGemini,
                        ProveedorGuionado, SalidaDeConduccionInvalida)

SALIDA = {"intencion": "continuar", "texto": "Dale. ¿Para cuándo?",
          "pregunta": ["due_date"]}
HISTORIAL = [{"role": "user", "content": "quiero una tarea"},
             {"role": "assistant", "content": "¿Qué hay que hacer?"}]
HECHOS = '{"faltan": ["title"]}'


# --------------------------------------------------------- el historial

def test_el_historial_se_alterna_sin_empezar_por_leda():
    mensajes = llm._alternados([
        {"role": "assistant", "content": "arranque"},
        {"role": "user", "content": "uno"},
        {"role": "user", "content": "dos"},
        {"role": "assistant", "content": "tres"},
        {"role": "assistant", "content": "cuatro"},
        {"role": "user", "content": "cinco"}])
    assert mensajes == [{"role": "user", "content": "uno\ndos"},
                        {"role": "assistant", "content": "tres\ncuatro"},
                        {"role": "user", "content": "cinco"}]


def test_el_historial_vacio_o_sin_texto_no_deja_mensajes():
    assert llm._alternados(None) == []
    assert llm._alternados([{"role": "assistant", "content": "x"}]) == []
    assert llm._alternados([{"role": "user", "content": ""}]) == []


def test_los_mensajes_del_turno_terminan_en_un_mensaje_de_la_persona_con_los_hechos():
    mensajes = llm._mensajes_de_conduccion(HISTORIAL, HECHOS)
    assert [m["role"] for m in mensajes] == ["user", "assistant", "user"]
    assert mensajes[:2] == HISTORIAL
    assert HECHOS in mensajes[2]["content"]


def test_si_la_conversacion_terminó_con_la_persona_los_hechos_se_le_suman():
    mensajes = llm._mensajes_de_conduccion(
        [{"role": "user", "content": "hola"}], HECHOS)
    assert [m["role"] for m in mensajes] == ["user"]
    assert mensajes[0]["content"].startswith("hola") and HECHOS in mensajes[0]["content"]


def test_sin_conversacion_son_solo_los_hechos():
    (mensaje,) = llm._mensajes_de_conduccion([], HECHOS)
    assert mensaje["role"] == "user" and HECHOS in mensaje["content"]


def test_el_historial_del_ruteo_tambien_se_alterna_en_el_medio():
    mensajes = llm._mensajes_del_ruteo("hoy", [
        {"role": "user", "content": "a"}, {"role": "user", "content": "b"},
        {"role": "assistant", "content": "c"}, {"role": "assistant", "content": "d"}])
    assert [m["role"] for m in mensajes] == ["user", "assistant", "user"]
    assert mensajes[0]["content"] == "a\nb" and mensajes[2]["content"] == "hoy"


# --------------------------------------------------------------- guionado

def test_el_guionado_devuelve_las_salidas_en_orden_y_las_registra():
    p = ProveedorGuionado(guion=[], conducciones=[SALIDA, "texto"])
    assert p.conducir_alta("sis", HISTORIAL, "h1") == SALIDA
    assert p.conducir_alta("sis", [], "h2", plazo=3.0) == "texto"
    assert p.conducidos == [("sis", HISTORIAL, "h1"), ("sis", [], "h2")]
    assert p.plazos_de_conduccion == [None, 3.0]


def test_el_guionado_lanza_el_error_guionado_y_avisa_si_se_agota():
    p = ProveedorGuionado(guion=[], conducciones=[TimeoutError("colgado")])
    with pytest.raises(TimeoutError):
        p.conducir_alta("s", [], "h")
    with pytest.raises(RuntimeError):
        p.conducir_alta("s", [], "h")        # un guion que se agota es un defecto de la prueba


# --------------------------------------------------------------- compatible

def _completion(llamadas=None, contenido=None) -> dict:
    mensaje = {"role": "assistant", "content": contenido}
    if llamadas is not None:
        mensaje["tool_calls"] = llamadas
    return {"id": "c1", "object": "chat.completion", "created": 0, "model": "m",
            "choices": [{"index": 0, "finish_reason": "stop", "message": mensaje}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1,
                      "total_tokens": 2}}


def _llamada(argumentos) -> dict:
    return {"id": "t1", "type": "function", "function": {
        "name": NOMBRE_HERRAMIENTA,
        "arguments": argumentos if isinstance(argumentos, str)
        else json.dumps(argumentos)}}


def _compatible(monkeypatch, respond, parametros=None):
    http = httpx.Client(transport=httpx.MockTransport(respond))
    real = openai.OpenAI
    monkeypatch.setattr(openai, "OpenAI", lambda **kw: real(http_client=http, **kw))
    monkeypatch.setattr("time.sleep", lambda s: None)
    return ProveedorCompatible("m", "sk-test", "http://localhost/v1", parametros)


def test_compatible_fuerza_la_herramienta_y_manda_historial_y_hechos(monkeypatch):
    cuerpos = []

    def respond(request: httpx.Request) -> httpx.Response:
        cuerpos.append(json.loads(request.content))
        return httpx.Response(200, json=_completion([_llamada(SALIDA)]))

    salida = _compatible(monkeypatch, respond).conducir_alta("sis", HISTORIAL, HECHOS)

    assert salida == SALIDA
    cuerpo = cuerpos[0]
    assert cuerpo["tool_choice"] == {"type": "function",
                                     "function": {"name": NOMBRE_HERRAMIENTA}}
    (herramienta,) = cuerpo["tools"]
    assert herramienta["function"]["name"] == NOMBRE_HERRAMIENTA
    assert herramienta["function"]["parameters"] == ESQUEMA_SALIDA
    roles = [m["role"] for m in cuerpo["messages"]]
    assert roles == ["system", "user", "assistant", "user"]
    assert cuerpo["messages"][0]["content"] == "sis"
    assert HECHOS in cuerpo["messages"][-1]["content"]
    assert cuerpo["max_tokens"] <= llm.MAX_TOKENS_CONDUCCION


def test_compatible_sin_llamada_pero_con_json_en_el_texto_lo_devuelve(monkeypatch):
    def respond(request):
        return httpx.Response(200, json=_completion(None, json.dumps(SALIDA)))

    assert isinstance(_compatible(monkeypatch, respond).conducir_alta(
        "s", [], "h"), str)


@pytest.mark.parametrize("cuerpo", [
    _completion([_llamada("{no es json")]),
    _completion(None, None),
    _completion(None, "")])
def test_compatible_sin_salida_usable_es_un_error(monkeypatch, cuerpo):
    def respond(request):
        return httpx.Response(200, json=cuerpo)

    with pytest.raises(SalidaDeConduccionInvalida):
        _compatible(monkeypatch, respond).conducir_alta("s", [], "h")


def test_compatible_conserva_el_timeout_http_y_con_plazo_corta_sin_reintentos(
        monkeypatch):
    tiempos = []

    def respond(request: httpx.Request) -> httpx.Response:
        tiempos.append(request.extensions["timeout"]["read"])
        raise httpx.ReadTimeout("colgado", request=request)

    proveedor = _compatible(monkeypatch, respond)
    with pytest.raises(openai.APITimeoutError):
        proveedor.conducir_alta("s", [], "h")
    assert len(tiempos) == 3 and set(tiempos) == {20}      # el del cliente, con reintentos

    tiempos.clear()
    with pytest.raises(openai.APITimeoutError):
        proveedor.conducir_alta("s", [], "h", plazo=2.5)
    assert tiempos == [2.5]


# ------------------------------------------------------------------- gemini

def test_gemini_fuerza_la_herramienta_con_un_esquema_que_acepta():
    cuerpos = []

    def respond(request: httpx.Request) -> httpx.Response:
        cuerpos.append(json.loads(request.content))
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [
            {"functionCall": {"name": NOMBRE_HERRAMIENTA, "args": SALIDA}}]}}]})

    http = httpx.Client(transport=httpx.MockTransport(respond))
    salida = ProveedorGemini("m", "sk-test", cliente=http).conducir_alta(
        "sis", HISTORIAL, HECHOS)

    assert salida == SALIDA
    cuerpo = cuerpos[0]
    assert cuerpo["system_instruction"]["parts"][0]["text"] == "sis"
    assert [c["role"] for c in cuerpo["contents"]] == ["user", "model", "user"]
    assert HECHOS in cuerpo["contents"][-1]["parts"][0]["text"]
    assert cuerpo["toolConfig"]["functionCallingConfig"] == {
        "mode": "ANY", "allowedFunctionNames": [NOMBRE_HERRAMIENTA]}
    parametros = cuerpo["tools"][0]["function_declarations"][0]["parameters"]
    botones = parametros["properties"]["botones"]
    # Gemini no admite un tipo en lista ni un nulo en el enum: se traduce.
    assert botones["type"] == "string" and botones["nullable"] is True
    assert None not in botones["enum"]
    assert "additionalProperties" not in json.dumps(parametros)


def test_gemini_sin_llamada_es_un_error():
    http = httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json={"candidates": []})))
    with pytest.raises(SalidaDeConduccionInvalida):
        ProveedorGemini("m", "sk-test", cliente=http).conducir_alta("s", [], "h")


def test_gemini_con_plazo_no_reintenta():
    tiempos = []

    def respond(request: httpx.Request) -> httpx.Response:
        tiempos.append(request.extensions["timeout"]["read"])
        raise httpx.ReadTimeout("colgado", request=request)

    http = httpx.Client(transport=httpx.MockTransport(respond))
    with pytest.raises(httpx.ReadTimeout):
        ProveedorGemini("m", "sk-test", cliente=http).conducir_alta(
            "s", [], "h", plazo=1.5)
    assert tiempos == [1.5]


# ---------------------------------------------------------------- anthropic

class _Bloque:
    def __init__(self, tipo, **datos):
        self.type = tipo
        self.__dict__.update(datos)


class _Mensajes:
    def __init__(self, bloques):
        self.llamadas, self.bloques = [], bloques

    def create(self, **kw):
        self.llamadas.append(kw)
        bloques = self.bloques

        class _R:
            content = bloques

        return _R()


class _Cliente:
    def __init__(self, bloques):
        self.messages = _Mensajes(bloques)
        self.opciones = []

    def with_options(self, **kw):
        self.opciones.append(kw)
        return self


def test_anthropic_fuerza_la_herramienta():
    cliente = _Cliente([_Bloque("tool_use", id="t1", name=NOMBRE_HERRAMIENTA,
                                input=SALIDA)])
    salida = ProveedorAnthropic("m", "sk-test", cliente=cliente).conducir_alta(
        "sis", HISTORIAL, HECHOS)

    assert salida == SALIDA
    (llamada,) = cliente.messages.llamadas
    assert llamada["system"] == "sis"
    assert llamada["tool_choice"] == {"type": "tool", "name": NOMBRE_HERRAMIENTA}
    (herramienta,) = llamada["tools"]
    assert herramienta["name"] == NOMBRE_HERRAMIENTA
    assert herramienta["input_schema"] == ESQUEMA_SALIDA
    assert [m["role"] for m in llamada["messages"]] == ["user", "assistant", "user"]
    assert HECHOS in llamada["messages"][-1]["content"]
    assert llamada["max_tokens"] <= llm.MAX_TOKENS_CONDUCCION


def test_anthropic_sin_llamada_es_un_error_y_con_plazo_usa_un_cliente_sin_reintentos():
    cliente = _Cliente([_Bloque("text", text="hola")])
    with pytest.raises(SalidaDeConduccionInvalida):
        ProveedorAnthropic("m", "sk-test", cliente=cliente).conducir_alta(
            "s", [], "h", plazo=2.0)
    assert cliente.opciones == [{"timeout": 2.0, "max_retries": 0}]
