"""La IA por la suscripción de ChatGPT (`leda.motor.chatgpt`; decisión del usuario, 2026-10-07).

El ingreso es el del cliente oficial de Codex (OAuth con PKCE contra `auth.openai.com`) y los
pedidos van al servicio de Codex de ChatGPT, en el formato de respuestas. Nunca se sale a la
red: el emisor y el servicio son transportes falsos, y el retorno del navegador es un pedido
local al servidor de retorno. Ningún token aparece en lo que se imprime ni en los errores.
"""

from __future__ import annotations

import base64
import hashlib
import json
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from leda.motor import chatgpt
from leda.motor.chatgpt import (CLIENT_ID, LoginFallido, ClienteChatGPT, ErrorDeChatGPT,
                                SesionChatGPT, SesionChatGPTAusente, SesionChatGPTVencida)
from leda.motor.fichas import JUGADAS
from leda.motor.ia import Jugada
from leda.motor.ia_real import (IAReal, ParametrosInvalidos, PlazoAgotado, RespuestaInvalida,
                                desde_base)
from leda.motor.instrucciones import INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION

AHORA = datetime(2026, 10, 7, 12, 0, tzinfo=timezone.utc)
CUENTA = "cuenta-1234-abcd"
CORREO = "ariel.prueba@example.com"

SITUACION = {"hoy": "2026-10-20", "mensaje": "llego el 27, el proveedor se demoró",
             "estado": None, "ultimo_aviso": {"tipo": "aviso_previo", "tarea": "T1"},
             "tareas": [{"alias": "T1", "titulo": "Programar PLC", "estado": "en_curso",
                         "fecha_objetivo": "2026-10-23T20:00:00+00:00"}],
             "ultimos_turnos": [], "jugadas_posibles": sorted(JUGADAS)}


def _b64(datos: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(datos).encode()).decode().rstrip("=")


def jwt(reclamos: dict) -> str:
    """Un JWT de mentira: sólo importa la carga (nadie verifica la firma del lado de Leda)."""
    return f"{_b64({'alg': 'none'})}.{_b64(reclamos)}.firma"


def tokens_del_emisor(*, vence: datetime = AHORA + timedelta(days=10), sufijo: str = "1",
                      con_refresco: bool = True) -> dict:
    respuesta = {
        "id_token": jwt({"email": CORREO,
                         "https://api.openai.com/auth": {"chatgpt_account_id": CUENTA,
                                                         "chatgpt_plan_type": "plus"}}),
        "access_token": jwt({"exp": int(vence.timestamp()), "sufijo": sufijo,
                             "https://api.openai.com/auth": {"chatgpt_account_id": CUENTA}}),
        "expires_in": 864000}
    if con_refresco:
        respuesta["refresh_token"] = f"refresco-secreto-{sufijo}"
    return respuesta


class Emisor:
    """`auth.openai.com`, de mentira: guarda los pedidos al punto de los tokens."""

    def __init__(self, respuestas: list) -> None:
        self.respuestas = list(respuestas)
        self.pedidos: list[dict] = []

    def __call__(self, pedido: httpx.Request) -> httpx.Response:
        tipo = pedido.headers.get("content-type", "")
        cuerpo = (json.loads(pedido.content) if "json" in tipo
                  else {k: v[0] for k, v in parse_qs(pedido.content.decode()).items()})
        self.pedidos.append({"url": str(pedido.url), "tipo": tipo, "cuerpo": cuerpo})
        respuesta = self.respuestas.pop(0)
        if isinstance(respuesta, tuple):
            return httpx.Response(respuesta[0], json=respuesta[1])
        return httpx.Response(200, json=respuesta)


def sesion_guardada(ruta: Path, *, vence: datetime = AHORA + timedelta(days=10),
                    emisor: Emisor | None = None, reloj=lambda: AHORA) -> SesionChatGPT:
    chatgpt.guardar(ruta, chatgpt.tokens_de_la_respuesta(tokens_del_emisor(vence=vence), AHORA))
    return SesionChatGPT(ruta, transporte=httpx.MockTransport(emisor or Emisor([])),
                         reloj=reloj)


# --- El ingreso: PKCE, estado y canje ------------------------------------------------------

def test_el_pkce_es_s256_del_verificador_y_cambia_cada_vez():
    pkce, otro = chatgpt.generar_pkce(), chatgpt.generar_pkce()

    esperado = base64.urlsafe_b64encode(
        hashlib.sha256(pkce.verificador.encode()).digest()).decode().rstrip("=")
    assert pkce.desafio == esperado
    assert 43 <= len(pkce.verificador) <= 128 and "=" not in pkce.verificador
    assert pkce.verificador != otro.verificador
    assert pkce.verificador not in repr(pkce)          # el verificador es un secreto
    assert chatgpt.generar_estado() != chatgpt.generar_estado()


def test_la_url_de_autorizacion_lleva_los_parametros_del_cliente_oficial():
    pkce = chatgpt.generar_pkce()
    url = urlparse(chatgpt.url_de_autorizacion(pkce, "estado-1",
                                               "http://127.0.0.1:1455/auth/callback"))
    q = {k: v[0] for k, v in parse_qs(url.query).items()}

    assert f"{url.scheme}://{url.netloc}{url.path}" == "https://auth.openai.com/oauth/authorize"
    assert q == {"response_type": "code", "client_id": CLIENT_ID,
                 "redirect_uri": "http://127.0.0.1:1455/auth/callback",
                 "code_challenge": pkce.desafio, "code_challenge_method": "S256",
                 "state": "estado-1", "scope": chatgpt.ALCANCES,
                 "id_token_add_organizations": "true", "codex_cli_simplified_flow": "true",
                 "originator": "codex_cli_rs"}
    assert "offline_access" in chatgpt.ALCANCES.split()       # sin él no hay renovación


def test_el_retorno_se_acepta_solo_con_el_mismo_estado():
    base = "http://127.0.0.1:1455/auth/callback"
    assert chatgpt.codigo_del_retorno(f"{base}?code=abc&state=e1", "e1") == "abc"
    with pytest.raises(LoginFallido, match="estado"):
        chatgpt.codigo_del_retorno(f"{base}?code=abc&state=otro", "e1")
    with pytest.raises(LoginFallido, match="access_denied"):
        chatgpt.codigo_del_retorno(f"{base}?error=access_denied&state=e1", "e1")
    with pytest.raises(LoginFallido, match="código"):
        chatgpt.codigo_del_retorno(f"{base}?state=e1", "e1")
    # El estado se mira antes que el error: un error con otro estado no es de este ingreso.
    with pytest.raises(LoginFallido, match="estado"):
        chatgpt.codigo_del_retorno(f"{base}?error=access_denied&state=otro", "e1")


def test_el_canje_manda_el_codigo_y_el_verificador_y_lee_la_cuenta():
    emisor = Emisor([tokens_del_emisor()])
    pkce = chatgpt.generar_pkce()
    with httpx.Client(transport=httpx.MockTransport(emisor)) as http:
        tokens = chatgpt.canjear_codigo(http, "codigo-1", pkce,
                                        "http://127.0.0.1:1455/auth/callback", ahora=AHORA)

    [pedido] = emisor.pedidos
    assert pedido["url"] == "https://auth.openai.com/oauth/token"
    assert pedido["tipo"].startswith("application/x-www-form-urlencoded")
    assert pedido["cuerpo"] == {"grant_type": "authorization_code", "client_id": CLIENT_ID,
                                "code": "codigo-1", "code_verifier": pkce.verificador,
                                "redirect_uri": "http://127.0.0.1:1455/auth/callback"}
    assert tokens.cuenta == CUENTA and tokens.correo == CORREO
    assert tokens.expira == AHORA + timedelta(days=10)
    assert "refresco-secreto" not in repr(tokens)


def test_un_canje_rechazado_no_muestra_el_cuerpo():
    emisor = Emisor([(400, {"error": "invalid_grant", "detalle": "codigo-1 secreto"})])
    with httpx.Client(transport=httpx.MockTransport(emisor)) as http, \
            pytest.raises(LoginFallido) as e:
        chatgpt.canjear_codigo(http, "codigo-1", chatgpt.generar_pkce(),
                               "http://127.0.0.1:1455/auth/callback", ahora=AHORA)
    assert "invalid_grant" in str(e.value) and "secreto" not in str(e.value)


# --- Dónde se guarda la sesión ------------------------------------------------------------

def test_la_sesion_se_guarda_fuera_del_repositorio(tmp_path, monkeypatch):
    monkeypatch.delenv(chatgpt.VARIABLE_RUTA, raising=False)
    assert chatgpt.ruta_de_la_sesion() == Path.home() / ".leda" / "chatgpt.json"
    monkeypatch.setenv(chatgpt.VARIABLE_RUTA, str(tmp_path / "otra.json"))
    assert chatgpt.ruta_de_la_sesion() == tmp_path / "otra.json"

    tokens = chatgpt.tokens_de_la_respuesta(tokens_del_emisor(), AHORA)
    dentro = Path(chatgpt.__file__).resolve().parents[3] / "sesion-de-prueba.json"
    with pytest.raises(ValueError, match="fuera del repositorio"):
        chatgpt.guardar(dentro, tokens)
    assert not dentro.exists()
    monkeypatch.setenv(chatgpt.VARIABLE_RUTA, str(dentro))
    with pytest.raises(ValueError, match="fuera del repositorio"):
        chatgpt.ruta_de_la_sesion()


def test_lo_guardado_se_vuelve_a_leer_igual(tmp_path):
    ruta = tmp_path / "sub" / "chatgpt.json"
    tokens = chatgpt.tokens_de_la_respuesta(tokens_del_emisor(), AHORA)
    chatgpt.guardar(ruta, tokens)

    assert chatgpt.cargar(ruta) == tokens
    assert not list(ruta.parent.glob("*.tmp"))          # se escribe entero o nada


def test_sin_sesion_es_una_ia_no_configurada(tmp_path):
    with pytest.raises(SesionChatGPTAusente, match="chatgpt login") as e:
        SesionChatGPT.abrir(tmp_path / "no-existe.json")
    assert isinstance(e.value, LookupError)


# --- La renovación ------------------------------------------------------------------------

def test_no_renueva_mientras_el_acceso_vale(tmp_path):
    emisor = Emisor([])
    sesion = sesion_guardada(tmp_path / "s.json", emisor=emisor)

    acceso, cuenta = sesion.credenciales()

    assert cuenta == CUENTA and acceso == chatgpt.cargar(tmp_path / "s.json").access_token
    assert emisor.pedidos == []


def test_renueva_antes_de_que_venza_y_guarda_lo_nuevo(tmp_path):
    nuevos = tokens_del_emisor(vence=AHORA + timedelta(days=10), sufijo="2")
    emisor = Emisor([nuevos])
    ruta = tmp_path / "s.json"
    sesion = sesion_guardada(ruta, vence=AHORA + timedelta(minutes=3), emisor=emisor)

    acceso, _ = sesion.credenciales()

    [pedido] = emisor.pedidos
    assert pedido["url"] == "https://auth.openai.com/oauth/token"
    assert pedido["tipo"].startswith("application/json")
    assert pedido["cuerpo"] == {"client_id": CLIENT_ID, "grant_type": "refresh_token",
                                "refresh_token": "refresco-secreto-1"}
    assert acceso == nuevos["access_token"]
    guardado = chatgpt.cargar(ruta)
    assert guardado.access_token == nuevos["access_token"]
    assert guardado.refresh_token == "refresco-secreto-2"


def test_una_renovacion_sin_token_de_refresco_nuevo_conserva_el_anterior(tmp_path):
    emisor = Emisor([tokens_del_emisor(sufijo="2", con_refresco=False)])
    ruta = tmp_path / "s.json"
    sesion_guardada(ruta, vence=AHORA + timedelta(minutes=1), emisor=emisor).credenciales()
    assert chatgpt.cargar(ruta).refresh_token == "refresco-secreto-1"


def test_si_otro_proceso_ya_renovo_usa_lo_del_archivo(tmp_path):
    emisor = Emisor([])
    ruta = tmp_path / "s.json"
    reloj = [AHORA]
    sesion = sesion_guardada(ruta, vence=AHORA + timedelta(hours=1), emisor=emisor,
                             reloj=lambda: reloj[0])
    sesion.credenciales()               # la sesión ya leyó el archivo de antes
    otro = chatgpt.tokens_de_la_respuesta(
        tokens_del_emisor(vence=AHORA + timedelta(days=10), sufijo="3"), AHORA)
    chatgpt.guardar(ruta, otro)         # otro proceso renovó
    reloj[0] = AHORA + timedelta(minutes=58)

    acceso, _ = sesion.credenciales()

    assert acceso == otro.access_token and emisor.pedidos == []


@pytest.mark.parametrize("respuesta", [
    (401, {"error": {"code": "refresh_token_expired", "message": "expired"}}),
    (400, {"error": "invalid_grant"}),
    (500, {"error": "server_error"}),
])
def test_una_renovacion_fallida_es_un_lookup_error_que_pide_volver_a_entrar(tmp_path,
                                                                            respuesta):
    emisor = Emisor([respuesta])
    sesion = sesion_guardada(tmp_path / "s.json", vence=AHORA - timedelta(minutes=1),
                             emisor=emisor)
    with pytest.raises(SesionChatGPTVencida) as e:
        sesion.credenciales()
    assert isinstance(e.value, LookupError)
    assert "python -m leda chatgpt login" in str(e.value)
    assert str(respuesta[0]) in str(e.value)
    assert "refresco-secreto" not in str(e.value)


def test_una_renovacion_sin_red_tambien_es_un_lookup_error(tmp_path):
    def sin_red(pedido):
        raise httpx.ConnectError("sin red", request=pedido)

    chatgpt.guardar(tmp_path / "s.json", chatgpt.tokens_de_la_respuesta(
        tokens_del_emisor(vence=AHORA - timedelta(minutes=1)), AHORA))
    sesion = SesionChatGPT(tmp_path / "s.json", transporte=httpx.MockTransport(sin_red),
                           reloj=lambda: AHORA)
    with pytest.raises(SesionChatGPTVencida, match="ConnectError"):
        sesion.credenciales()


# --- Los pedidos al servicio de Codex -----------------------------------------------------

def sse(*eventos: dict) -> bytes:
    return "".join(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n" for e in eventos).encode()


def completada(salida: list, *, entrada: int = 120, sale: int = 30) -> dict:
    return {"type": "response.completed",
            "response": {"id": "resp_1", "status": "completed", "output": salida,
                         "usage": {"input_tokens": entrada, "output_tokens": sale}}}


def llamada(argumentos: dict, nombre: str = "elegir_jugadas") -> dict:
    return {"type": "function_call", "id": "fc_1", "call_id": "call_1", "name": nombre,
            "namespace": "functions", "arguments": json.dumps(argumentos)}


def mensaje(texto: str) -> dict:
    return {"type": "message", "role": "assistant", "id": "msg_1",
            "content": [{"type": "output_text", "text": texto}]}


class Codex:
    """`chatgpt.com/backend-api/codex`, de mentira: contesta en orden y guarda los pedidos."""

    def __init__(self, respuestas: list, demora: float = 0.0) -> None:
        self.respuestas = list(respuestas)
        self.pedidos: list[dict] = []
        self.demora = demora

    def __call__(self, pedido: httpx.Request) -> httpx.Response:
        self.pedidos.append({"url": str(pedido.url), "cabeceras": dict(pedido.headers),
                             "cuerpo": json.loads(pedido.content)})
        if self.demora:
            time.sleep(self.demora)
        respuesta = self.respuestas.pop(0)
        if isinstance(respuesta, httpx.Response):
            return respuesta
        if isinstance(respuesta, dict):
            return httpx.Response(200, json=respuesta)
        return httpx.Response(200, content=respuesta,
                              headers={"content-type": "text/event-stream"})


def ia_por_suscripcion(tmp_path, codex: Codex, *, modelo: str = "gpt-6-sol",
                       parametros: dict | None = None, emisor: Emisor | None = None,
                       vence: datetime = AHORA + timedelta(days=10)) -> IAReal:
    sesion = sesion_guardada(tmp_path / "s.json", vence=vence, emisor=emisor)
    cliente = ClienteChatGPT.crear(modelo, sesion, {"plazo_s": 5, **(parametros or {})},
                                   transporte=httpx.MockTransport(codex))
    return IAReal(cliente, None, nombre=f"chatgpt/{modelo}")


def test_la_eleccion_va_en_formato_de_respuestas_con_la_herramienta_y_la_cuenta(tmp_path):
    codex = Codex([sse({"type": "response.created", "response": {"id": "resp_1"}},
                       {"type": "response.output_item.done", "item": llamada({"jugadas": [
                           {"nombre": "anotar_prevision", "tarea": "T1",
                            "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]})},
                       completada([]))])

    jugadas = ia_por_suscripcion(tmp_path, codex).elegir_jugadas(SITUACION)

    assert jugadas == [Jugada("anotar_prevision", {
        "tarea": "T1", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"})]
    [pedido] = codex.pedidos
    assert pedido["url"] == "https://chatgpt.com/backend-api/codex/responses"
    cab = pedido["cabeceras"]
    acceso = chatgpt.cargar(tmp_path / "s.json").access_token
    assert cab["authorization"] == f"Bearer {acceso}"
    assert cab["chatgpt-account-id"] == CUENTA
    assert cab["originator"] == "codex_cli_rs"
    assert cab["accept"] == "text/event-stream"
    assert cab["x-openai-internal-codex-responses-lite"] == "true"     # gpt-6-sol es "lite"
    cuerpo = pedido["cuerpo"]
    assert cuerpo["model"] == "gpt-6-sol"
    assert cuerpo["stream"] is True and cuerpo["store"] is False
    assert cuerpo["tool_choice"] == "auto" and cuerpo["parallel_tool_calls"] is False
    # Ni las instrucciones oficiales de Codex, ni los campos que el servicio no recibe.
    for campo in ("instructions", "temperature", "max_tokens", "max_output_tokens", "messages",
                  "tools"):
        assert campo not in cuerpo
    herramientas, instrucciones, usuario = cuerpo["input"]
    assert herramientas["type"] == "additional_tools" and herramientas["role"] == "developer"
    [espacio] = herramientas["tools"]
    assert (espacio["type"], espacio["name"]) == ("namespace", "functions")
    [funcion] = espacio["tools"]
    assert (funcion["type"], funcion["name"]) == ("function", "elegir_jugadas")
    assert funcion["parameters"]["properties"]["jugadas"]["type"] == "array"
    assert instrucciones["type"] == "message" and instrucciones["role"] == "developer"
    assert instrucciones["content"][0]["type"] == "input_text"
    assert instrucciones["content"][0]["text"].startswith(INSTRUCCIONES_JUGADAS)
    assert usuario["role"] == "user"
    assert json.loads(usuario["content"][0]["text"])["mensaje"] == SITUACION["mensaje"]


def test_un_modelo_que_no_es_lite_lleva_la_herramienta_arriba(tmp_path):
    codex = Codex([sse({"type": "response.output_item.done", "item": llamada({"jugadas": []})},
                       completada([]))])

    assert ia_por_suscripcion(tmp_path, codex, modelo="gpt-5.5").elegir_jugadas(SITUACION) == []

    cuerpo = codex.pedidos[0]["cuerpo"]
    assert "x-openai-internal-codex-responses-lite" not in codex.pedidos[0]["cabeceras"]
    [funcion] = cuerpo["tools"]
    assert (funcion["type"], funcion["name"]) == ("function", "elegir_jugadas")
    assert [m["role"] for m in cuerpo["input"]] == ["developer", "user"]


def test_la_redaccion_lee_el_texto_del_mensaje(tmp_path):
    codex = Codex([sse({"type": "response.output_text.delta", "delta": "Anoté "},
                       {"type": "response.output_text.delta", "delta": "el 27."},
                       {"type": "response.output_item.done", "item": mensaje("Anoté el 27.")},
                       completada([]))])

    texto = ia_por_suscripcion(tmp_path, codex).redactar(
        {"hoy": "2026-10-20", "persona": "Marcos", "mensaje": "llego el 27", "hechos": [],
         "pregunta": None, "ultimos_turnos": []})

    assert texto == "Anoté el 27."
    [instrucciones, _] = codex.pedidos[0]["cuerpo"]["input"]
    assert instrucciones["content"][0]["text"].startswith(INSTRUCCIONES_REDACCION)


def test_sin_el_mensaje_entero_vale_el_texto_que_llego_por_partes(tmp_path):
    codex = Codex([sse({"type": "response.output_text.delta", "delta": "Hola, "},
                       {"type": "response.output_text.delta", "delta": "Marcos."},
                       completada([]))])
    assert ia_por_suscripcion(tmp_path, codex).redactar({"hoy": "2026-10-20"}) == "Hola, Marcos."


def test_una_respuesta_json_sin_flujo_tambien_se_lee(tmp_path):
    codex = Codex([{"status": "completed", "output": [mensaje("Listo.")],
                    "usage": {"input_tokens": 1, "output_tokens": 1}}])
    assert ia_por_suscripcion(tmp_path, codex).redactar({"hoy": "2026-10-20"}) == "Listo."


def test_el_uso_vuelve_con_los_nombres_de_siempre(tmp_path):
    codex = Codex([sse({"type": "response.output_item.done", "item": mensaje("Listo.")},
                       completada([], entrada=321, sale=12))])
    ia = ia_por_suscripcion(tmp_path, codex)
    respuesta = ia.cliente.completar({"messages": [{"role": "user", "content": "hola"}]})
    assert respuesta["usage"] == {"prompt_tokens": 321, "completion_tokens": 12}
    assert respuesta["choices"][0]["message"]["content"] == "Listo."
    assert respuesta["choices"][0]["finish_reason"] == "stop"


def test_una_respuesta_cortada_por_el_tope_es_no_responder(tmp_path):
    codex = Codex([sse({"type": "response.output_text.delta", "delta": "Ano"},
                       {"type": "response.incomplete",
                        "response": {"status": "incomplete", "output": [],
                                     "incomplete_details": {"reason": "max_output_tokens"}}})])
    with pytest.raises(RespuestaInvalida, match="tope"):
        ia_por_suscripcion(tmp_path, codex).redactar({"hoy": "2026-10-20"})


def test_un_flujo_que_termina_sin_completarse_es_no_responder(tmp_path):
    codex = Codex([sse({"type": "response.output_text.delta", "delta": "Ano"})])
    with pytest.raises(RespuestaInvalida, match="completarse"):
        ia_por_suscripcion(tmp_path, codex).redactar({"hoy": "2026-10-20"})


def test_un_texto_en_lugar_de_la_herramienta_es_no_responder(tmp_path):
    codex = Codex([sse({"type": "response.output_item.done", "item": mensaje("Anotado.")},
                       completada([]))])
    with pytest.raises(RespuestaInvalida, match="herramienta"):
        ia_por_suscripcion(tmp_path, codex).elegir_jugadas(SITUACION)


def test_una_falla_dentro_del_flujo_se_levanta_con_su_codigo(tmp_path):
    codex = Codex([sse({"type": "response.failed", "response": {
        "status": "failed", "error": {"code": "server_is_overloaded", "message": "busy"}}})])
    with pytest.raises(ErrorDeChatGPT, match="server_is_overloaded"):
        ia_por_suscripcion(tmp_path, codex).redactar({"hoy": "2026-10-20"})


def test_el_limite_de_uso_se_levanta_como_error_http_con_su_codigo(tmp_path):
    codex = Codex([httpx.Response(429, json={"error": {
        "type": "usage_limit_reached", "message": "límite", "resets_at": 1}})])
    with pytest.raises(httpx.HTTPStatusError, match="usage_limit_reached") as e:
        ia_por_suscripcion(tmp_path, codex).redactar({"hoy": "2026-10-20"})
    assert e.value.response.status_code == 429


def test_un_401_renueva_la_sesion_en_el_pedido_siguiente(tmp_path):
    nuevos = tokens_del_emisor(sufijo="2")
    emisor = Emisor([nuevos])
    codex = Codex([httpx.Response(401, json={"error": {"code": "token_expired"}}),
                   sse({"type": "response.output_item.done", "item": mensaje("Listo.")},
                       completada([]))])
    ia = ia_por_suscripcion(tmp_path, codex, emisor=emisor)

    with pytest.raises(httpx.HTTPStatusError):
        ia.redactar({"hoy": "2026-10-20"})
    assert ia.redactar({"hoy": "2026-10-20"}) == "Listo."     # el reintento del turno

    assert len(emisor.pedidos) == 1
    assert codex.pedidos[1]["cabeceras"]["authorization"] == f"Bearer {nuevos['access_token']}"


def test_una_sesion_vencida_sin_renovar_es_lookup_error_en_el_pedido(tmp_path):
    emisor = Emisor([(401, {"error": {"code": "refresh_token_reused"}})])
    codex = Codex([])
    ia = ia_por_suscripcion(tmp_path, codex, emisor=emisor, vence=AHORA - timedelta(hours=1))
    with pytest.raises(LookupError, match="chatgpt login"):
        ia.redactar({"hoy": "2026-10-20"})
    assert codex.pedidos == []


def test_el_plazo_acota_la_llamada_entera(tmp_path):
    codex = Codex([sse(completada([mensaje("tarde")]))], demora=1.0)
    ia = ia_por_suscripcion(tmp_path, codex, parametros={"plazo_s": 0.2})
    inicio = time.monotonic()
    with pytest.raises(PlazoAgotado):
        ia.redactar({"hoy": "2026-10-20"})
    assert time.monotonic() - inicio < 0.9


def test_los_campos_extra_viajan_y_no_pisan_lo_que_arma_el_codigo(tmp_path):
    codex = Codex([sse({"type": "response.output_item.done", "item": mensaje("Listo.")},
                       completada([]))])
    ia = ia_por_suscripcion(tmp_path, codex, parametros={
        "cuerpo_extra": {"reasoning": {"effort": "low"}}, "timeout_s": 30})
    ia.redactar({"hoy": "2026-10-20"})
    assert codex.pedidos[0]["cuerpo"]["reasoning"] == {"effort": "low", "context": "all_turns"}
    assert ia.cliente.http.timeout.read == 30


@pytest.mark.parametrize(("parametros", "nombrado"), [
    ({"temperature": 0.2}, "temperature"),
    ({"cuerpo_extra": {"input": []}}, "input"),
    ({"cuerpo_extra": {"store": True}}, "store"),
])
def test_lo_que_el_servicio_no_recibe_o_arma_el_codigo_se_rechaza(tmp_path, parametros,
                                                                  nombrado):
    sesion = sesion_guardada(tmp_path / "s.json")
    with pytest.raises(ParametrosInvalidos, match=nombrado):
        ClienteChatGPT.crear("gpt-6-sol", sesion, parametros)


# --- El servidor de retorno y el ingreso de punta a punta ---------------------------------

def _estado_de(url: str) -> str:
    return parse_qs(urlparse(url).query)["state"][0]


def _retorno_de(url: str) -> str:
    return parse_qs(urlparse(url).query)["redirect_uri"][0]


def test_el_ingreso_a_mano_guarda_la_sesion_y_muestra_solo_la_cuenta_enmascarada(
        tmp_path, capsys):
    emisor = Emisor([tokens_del_emisor()])
    abiertas: list[str] = []
    ruta = tmp_path / "s.json"

    codigo = chatgpt.iniciar(
        ruta=ruta, manual=True, abrir=abiertas.append,
        entrada=lambda _: f"{_retorno_de(abiertas[0])}?code=c1&state={_estado_de(abiertas[0])}",
        transporte=httpx.MockTransport(emisor), reloj=lambda: AHORA)

    assert codigo == 0
    assert chatgpt.cargar(ruta).cuenta == CUENTA
    assert emisor.pedidos[0]["cuerpo"]["code"] == "c1"
    salida = capsys.readouterr().out
    assert "ar" in salida and CORREO not in salida and "***" in salida
    tokens = tokens_del_emisor()
    for secreto in (tokens["access_token"], tokens["id_token"], tokens["refresh_token"]):
        assert secreto not in salida


def test_el_ingreso_con_otro_estado_no_guarda_nada(tmp_path, capsys):
    abiertas: list[str] = []
    codigo = chatgpt.iniciar(
        ruta=tmp_path / "s.json", manual=True, abrir=abiertas.append,
        entrada=lambda _: f"{_retorno_de(abiertas[0])}?code=c1&state=ajeno",
        transporte=httpx.MockTransport(Emisor([])), reloj=lambda: AHORA)
    assert codigo == 1 and not (tmp_path / "s.json").exists()
    assert "estado" in capsys.readouterr().out


def test_el_servidor_de_retorno_recibe_el_codigo_del_navegador(tmp_path):
    emisor = Emisor([tokens_del_emisor()])
    ruta = tmp_path / "s.json"
    respuestas: list[int] = []

    def navegador(url: str) -> None:
        def volver():
            r = httpx.get(f"{_retorno_de(url)}?code=c2&state={_estado_de(url)}", timeout=5)
            respuestas.append(r.status_code)
        threading.Thread(target=volver, daemon=True).start()

    codigo = chatgpt.iniciar(ruta=ruta, manual=False, abrir=navegador, puertos=(0,),
                             transporte=httpx.MockTransport(emisor), reloj=lambda: AHORA,
                             espera_s=5)

    assert codigo == 0 and respuestas == [200]
    assert emisor.pedidos[0]["cuerpo"]["code"] == "c2"
    assert emisor.pedidos[0]["cuerpo"]["redirect_uri"].startswith("http://127.0.0.1:")


def test_un_puerto_ocupado_pasa_al_de_respaldo():
    import socket

    with socket.socket() as ocupado:
        ocupado.bind(("127.0.0.1", 0))
        ocupado.listen()
        puerto = ocupado.getsockname()[1]
        servidor = chatgpt.ServidorDeRetorno.abrir("e1", (puerto, 0))
        try:
            assert servidor is not None and servidor.puerto not in (puerto, 0)
        finally:
            servidor.cerrar()
        assert chatgpt.ServidorDeRetorno.abrir("e1", (puerto,)) is None


def test_el_estado_y_la_salida_no_muestran_tokens(tmp_path, capsys):
    ruta = tmp_path / "s.json"
    assert chatgpt.estado(ruta, reloj=lambda: AHORA) == 1
    assert "python -m leda chatgpt login" in capsys.readouterr().out

    sesion_guardada(ruta)
    assert chatgpt.estado(ruta, reloj=lambda: AHORA) == 0
    salida = capsys.readouterr().out
    assert "2026-10-17" in salida and CORREO not in salida
    assert chatgpt.cargar(ruta).access_token not in salida

    assert chatgpt.salir(ruta) == 0 and not ruta.exists()
    assert chatgpt.salir(ruta) == 0          # ya no había: nada que borrar, no es un error


def test_la_cli_tiene_los_comandos_de_la_sesion(tmp_path, monkeypatch, capsys):
    from leda import cli

    monkeypatch.setenv(chatgpt.VARIABLE_RUTA, str(tmp_path / "s.json"))
    assert cli.main(["chatgpt", "estado"]) == 1
    assert "No hay sesión" in capsys.readouterr().out
    assert cli.main(["modelos", "--proveedor", "chatgpt"]) == 0
    assert "gpt-6-sol" in capsys.readouterr().out


# --- El modelo configurado --------------------------------------------------------------

def test_el_modelo_por_suscripcion_sale_de_la_configuracion_sin_clave(conn, mundo, tmp_path,
                                                                     monkeypatch):
    from leda.db import espacio

    from tests.motor.test_ia_real import _modelo

    class SinClaves:
        def clave_llm(self, proveedor):
            raise AssertionError("la suscripción no usa una clave")

    ruta = tmp_path / "s.json"
    monkeypatch.setenv(chatgpt.VARIABLE_RUTA, str(ruta))
    _modelo(conn, "chatgpt", "gpt-6-sol", parametros={"timeout_s": 45})

    with espacio(conn, mundo["id"]) as cur, pytest.raises(LookupError, match="chatgpt login"):
        desde_base(cur, mundo["id"], SinClaves())

    sesion_guardada(ruta)
    with espacio(conn, mundo["id"]) as cur:
        ia = desde_base(cur, mundo["id"], SinClaves())
    assert ia.nombre == "chatgpt/gpt-6-sol"
    assert isinstance(ia.cliente, ClienteChatGPT)
    assert ia.cliente.base_url == "https://chatgpt.com/backend-api/codex"
    assert ia.cliente.http.timeout.read == 45


def test_parametros_que_la_suscripcion_no_recibe_son_un_modelo_no_configurado(
        conn, mundo, tmp_path, monkeypatch):
    from leda.db import espacio

    from tests.motor.test_ia_real import _modelo

    monkeypatch.setenv(chatgpt.VARIABLE_RUTA, str(tmp_path / "s.json"))
    sesion_guardada(tmp_path / "s.json")
    _modelo(conn, "chatgpt", "gpt-6-sol", parametros={"temperature": 0.5})
    with espacio(conn, mundo["id"]) as cur, pytest.raises(LookupError, match="temperature"):
        desde_base(cur, mundo["id"], object())


def test_un_flujo_sin_tipo_de_contenido_tambien_se_lee(tmp_path):
    """Primera llamada real (2026-10-07): el servicio manda el flujo de eventos sin
    `content-type`; leerlo como JSON lo daba por ilegible."""
    flujo = sse({"type": "response.output_text.delta", "delta": "Hola."}, completada([]))
    codex = Codex([httpx.Response(200, content=flujo)])
    assert ia_por_suscripcion(tmp_path, codex).redactar({"hoy": "2026-10-20"}) == "Hola."


def test_un_modelo_lite_pide_el_razonamiento_de_todos_los_turnos(tmp_path):
    """Primera llamada real (2026-10-07): "Responses-Lite requires `reasoning.context` to be
    `all_turns`" (HTTP 400). Va siempre, y un esfuerzo pedido por `cuerpo_extra` se conserva."""
    codex = Codex([sse(completada([mensaje("Listo.")]))] * 2)
    ia_por_suscripcion(tmp_path, codex).redactar({"hoy": "2026-10-20"})
    ia_por_suscripcion(tmp_path, codex, parametros={
        "cuerpo_extra": {"reasoning": {"effort": "low"}}}).redactar({"hoy": "2026-10-20"})

    assert codex.pedidos[0]["cuerpo"]["reasoning"] == {"context": "all_turns"}
    assert codex.pedidos[1]["cuerpo"]["reasoning"] == {"context": "all_turns", "effort": "low"}
