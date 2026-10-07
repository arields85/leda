"""La IA por la suscripción de ChatGPT del usuario (decisión del usuario, 2026-10-07).

El usuario eligió usar GPT-6 sol con su suscripción paga de ChatGPT, entrando con su cuenta
"como lo hace opencode": el ingreso del cliente oficial de Codex, no la API ni el programa de
socios de OpenAI. Los complementos de la comunidad que lo hacen dicen "sólo para uso personal
de desarrollo"; el usuario lo eligió igual, para sus pruebas con datos ficticios.

Cómo funciona (fuentes, leídas el 2026-10-07; el cliente oficial manda cuando no coinciden):

- **El ingreso** es OAuth con PKCE contra `https://auth.openai.com`, con el cliente público
  del Codex CLI. `openai/codex`, `codex-rs/login/src/server.rs` (emisor, puerto 1455 y el
  1457 de respaldo, retorno `http://127.0.0.1:<puerto>/auth/callback`, los alcances y los
  parámetros `id_token_add_organizations`, `codex_cli_simplified_flow` y `originator`),
  `login/src/oauth/{authorization,pkce,client}.rs` (S256, estado al azar, canje por
  formulario) y `login/src/auth/manager.rs` (`CLIENT_ID`; la renovación va como JSON y se hace
  cinco minutos antes de que venza el acceso, por el `exp` del JWT; sin `exp`, cada ocho días).
  La cuenta de ChatGPT sale del reclamo `https://api.openai.com/auth` → `chatgpt_account_id`
  del `id_token` (`login/src/token_data.rs`). Los complementos de opencode hacen lo mismo
  (`numman-ali/opencode-openai-codex-auth`, `lib/auth/auth.ts`, con retorno en `localhost`).
- **Los pedidos** van a `https://chatgpt.com/backend-api/codex/responses`
  (`model-provider-info/src/lib.rs`, `CHATGPT_CODEX_BASE_URL`), en el formato de respuestas,
  siempre en flujo (`stream: true`, eventos SSE) y sin guardar (`store: false`), con
  `Authorization: Bearer <acceso>`, `ChatGPT-Account-ID` (`model-provider/src/
  bearer_auth_provider.rs`) y `originator: codex_cli_rs` (`login/src/auth/default_client.rs`).
- **Las instrucciones.** El cliente oficial ya no manda el campo `instructions`: sus
  instrucciones de base van como un mensaje `developer` al principio de `input`
  (`core/src/client.rs`, `BaseInstructionsFragment`). Las de Leda van igual, y sin el texto
  de Codex (los complementos viejos lo mandaban en `instructions`). Si el servicio llegara a
  exigirlo, `cuerpo_extra` puede llevar un `instructions`. Cambiar de proveedor cambia la
  conducta de la IA: hay que volver a medir (bitácora de flujos).
- **"Respuestas lite."** Los modelos que el catálogo oficial marca con `use_responses_lite`
  (`models-manager/models.json`; GPT-6 sol entre ellos) reciben las herramientas dentro de
  `input`, en un ítem `additional_tools` con el espacio de nombres `functions`, no en `tools`,
  sin llamadas en paralelo y con la cabecera `x-openai-internal-codex-responses-lite: true`
  (`core/src/client.rs`, `tools/src/tool_spec.rs`). El cliente oficial manda siempre
  `tool_choice: "auto"`; el motor también (`ia_real.IAReal`).
- **Lo que no se manda.** `temperature` y los topes de salida: el cliente oficial nunca los
  manda y los complementos los quitan (el servicio no los recibe). Los topes de los parámetros
  del modelo no tienen efecto acá; una respuesta que el servicio corta igual se lee como
  cortada (`finish_reason: length`).
- **Las fallas** llegan como HTTP (429 con `usage_limit_reached`, 401) o como un evento
  `response.failed` o `error` con su código (`codex-api/src/sse/responses_error.rs`).

La sesión se guarda fuera del repositorio (`~/.leda/chatgpt.json`, o la ruta de
`LEDA_CHATGPT_AUTH`), nunca se imprime y nunca entra a un mensaje de error. Lo que se muestra
es la cuenta enmascarada. La renovación se hace sola; si falla, es `SesionChatGPTVencida`, un
`LookupError`: para el turno, la IA no respondió (incidente y texto fijo), nunca en silencio.
`salir` borra la sesión local; no la revoca en OpenAI (el acceso vence solo).
"""

from __future__ import annotations

import base64
import hashlib
import http.server
import json
import os
import secrets
import threading
import webbrowser
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator
from urllib.parse import parse_qs, urlencode, urlsplit

import httpx

from .ia_real import (PLAZO_S, ClienteCompatible, ParametrosInvalidos, RespuestaInvalida,
                      llamar_con_plazo, validar_parametros)

EMISOR = "https://auth.openai.com"
URL_AUTORIZACION = f"{EMISOR}/oauth/authorize"
URL_TOKEN = f"{EMISOR}/oauth/token"
# El cliente público del Codex CLI (`login/src/auth/manager.rs`).
CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"
ALCANCES = "openid profile email offline_access api.connectors.read api.connectors.invoke"
ORIGINADOR = "codex_cli_rs"
# El puerto del retorno y el de respaldo, los dos en la lista del emisor (`server.rs`).
PUERTOS = (1455, 1457)
HOST_DE_RETORNO = "127.0.0.1"
BASE_URL = "https://chatgpt.com/backend-api/codex"
RECLAMO_AUTH = "https://api.openai.com/auth"
RECLAMO_PERFIL = "https://api.openai.com/profile"
RENOVAR_ANTES = timedelta(minutes=5)
RENOVAR_SIN_VENCIMIENTO = timedelta(days=8)
ESPERA_DEL_NAVEGADOR_S = 300.0
PLAZO_DEL_EMISOR_S = 30.0
VARIABLE_RUTA = "LEDA_CHATGPT_AUTH"
CABECERA_LITE = "x-openai-internal-codex-responses-lite"
ESPACIO_DE_FUNCIONES = "functions"
# Los modelos del catálogo oficial (`models-manager/models.json`, 2026-10-07) que van por
# "respuestas lite", y los que el catálogo muestra (los ocultos no se listan).
MODELOS_LITE = frozenset({
    "gpt-6-astra", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna", "gpt-5.6-sol", "gpt-5.6-terra",
    "gpt-5.6-luna", "gpt-daybreak-blue-latest", "gpt-daybreak-red-latest",
    "codex-auto-review"})
MODELOS_CONOCIDOS = ("gpt-6-astra", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna", "gpt-5.6-sol",
                     "gpt-5.6-terra", "gpt-5.6-luna", "gpt-5.5")
# Lo que arma este cliente en cada pedido: `cuerpo_extra` no lo puede pisar (además de lo que
# ya rechaza `ia_real.validar_parametros`).
DEL_PEDIDO_DE_RESPUESTAS = frozenset({"model", "input", "tools", "tool_choice",
                                      "parallel_tool_calls", "stream", "store", "include"})
# Los que el servicio no recibe: pedirlos es un error de escritura, no algo que se ignora.
NO_LOS_RECIBE = frozenset({"temperature"})
COMO_ENTRAR = "python -m leda chatgpt login"

RAIZ_DEL_REPOSITORIO = Path(__file__).resolve().parents[3]


class LoginFallido(RuntimeError):
    """El ingreso no terminó: el estado no coincide, el emisor lo rechazó o no llegó el código."""


class SesionChatGPTAusente(LookupError):
    """No hay una sesión guardada que se pueda leer: la IA no está configurada."""


class SesionChatGPTVencida(LookupError):
    """La sesión no se pudo renovar: hace falta volver a entrar."""


class ErrorDeChatGPT(RuntimeError):
    """El servicio no completó la respuesta (un evento `response.failed` o `error`)."""


# --- PKCE, estado y la dirección de autorización -----------------------------------------

def _b64url(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).decode("ascii").rstrip("=")


@dataclass(frozen=True)
class Pkce:
    verificador: str = field(repr=False)
    desafio: str


def generar_pkce() -> Pkce:
    """64 bytes al azar como verificador y su SHA-256 como desafío (S256), en base64url sin
    relleno, como `login/src/oauth/pkce.rs`."""
    verificador = _b64url(secrets.token_bytes(64))
    return Pkce(verificador, _b64url(hashlib.sha256(verificador.encode("ascii")).digest()))


def generar_estado() -> str:
    return _b64url(secrets.token_bytes(32))


def direccion_de_retorno(puerto: int) -> str:
    return f"http://{HOST_DE_RETORNO}:{puerto}/auth/callback"


def url_de_autorizacion(pkce: Pkce, estado: str, retorno: str) -> str:
    """La dirección para el navegador, con los parámetros del cliente oficial y en su orden."""
    return f"{URL_AUTORIZACION}?" + urlencode([
        ("response_type", "code"), ("client_id", CLIENT_ID), ("redirect_uri", retorno),
        ("code_challenge", pkce.desafio), ("code_challenge_method", "S256"),
        ("state", estado), ("scope", ALCANCES), ("id_token_add_organizations", "true"),
        ("codex_cli_simplified_flow", "true"), ("originator", ORIGINADOR)])


def codigo_del_retorno(retorno: str, estado: str) -> str:
    """El código de la dirección a la que volvió el navegador (entera o sólo su consulta). El
    estado se mira primero: un retorno con otro estado no es de este ingreso."""
    texto = (retorno or "").strip()
    consulta = urlsplit(texto).query or (texto.lstrip("?") if "=" in texto else "")
    datos = {k: v[0] for k, v in parse_qs(consulta).items()}
    if datos.get("state") != estado:
        raise LoginFallido("El estado del retorno no coincide con el de este ingreso.")
    if datos.get("error"):
        raise LoginFallido(f"El emisor no dio el ingreso ({datos['error']}).")
    if not datos.get("code"):
        raise LoginFallido("El retorno no trae el código de autorización.")
    return datos["code"]


# --- Los tokens -----------------------------------------------------------------------------

@dataclass(frozen=True)
class Tokens:
    id_token: str = field(repr=False)
    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    cuenta: str
    correo: str | None = field(default=None, repr=False)
    expira: datetime | None = None
    renovado: datetime | None = None

    def necesita_renovar(self, ahora: datetime) -> bool:
        if self.expira is not None:
            return self.expira - RENOVAR_ANTES <= ahora
        return self.renovado is None or self.renovado + RENOVAR_SIN_VENCIMIENTO < ahora


def _reclamos(token: str | None) -> dict[str, Any]:
    """La carga de un JWT, sin verificar la firma (sólo para leer la cuenta y el vencimiento;
    quien valida el token es el servicio). Un token que no es un JWT no tiene reclamos."""
    try:
        carga = token.split(".")[1]
        datos = json.loads(base64.urlsafe_b64decode(carga + "=" * (-len(carga) % 4)))
    except (AttributeError, IndexError, ValueError):
        return {}
    return datos if isinstance(datos, dict) else {}


def tokens_de_la_respuesta(datos: Any, ahora: datetime,
                           anteriores: Tokens | None = None) -> Tokens:
    """Los tokens de una respuesta del emisor (canje o renovación). Lo que una renovación no
    trae (el `id_token`, un token de refresco nuevo) se conserva de `anteriores`. Sin el
    acceso, el refresco o la cuenta, `ValueError`, sin mostrar ninguno."""
    if not isinstance(datos, dict) or not isinstance(datos.get("access_token"), str):
        raise ValueError("La respuesta del emisor no trae el token de acceso.")
    acceso = datos["access_token"]
    id_token = datos.get("id_token") or (anteriores.id_token if anteriores else None)
    refresco = datos.get("refresh_token") or (anteriores.refresh_token if anteriores else None)
    if not id_token or not refresco:
        raise ValueError("La respuesta del emisor no trae el id_token o el token de refresco.")
    de_id, de_acceso = _reclamos(id_token), _reclamos(acceso)
    cuenta = ((de_id.get(RECLAMO_AUTH) or {}).get("chatgpt_account_id")
              or (de_acceso.get(RECLAMO_AUTH) or {}).get("chatgpt_account_id")
              or (anteriores.cuenta if anteriores else None))
    if not cuenta:
        raise ValueError("Los tokens no dicen la cuenta de ChatGPT.")
    correo = (de_id.get("email") or (de_id.get(RECLAMO_PERFIL) or {}).get("email")
              or (anteriores.correo if anteriores else None))
    exp, dura = de_acceso.get("exp"), datos.get("expires_in")
    if isinstance(exp, (int, float)) and not isinstance(exp, bool):
        expira = datetime.fromtimestamp(exp, timezone.utc)
    elif isinstance(dura, (int, float)) and not isinstance(dura, bool):
        expira = ahora + timedelta(seconds=dura)
    else:
        expira = None
    return Tokens(id_token, acceso, refresco, cuenta, correo, expira, ahora)


def _codigo_de_error(respuesta: httpx.Response) -> str:
    """El código de error de una respuesta (`error` como texto, o su `code` o `type`), nunca el
    cuerpo entero: un cuerpo puede repetir lo que se mandó."""
    try:
        error = respuesta.json().get("error")
    except (ValueError, AttributeError):
        return ""
    if isinstance(error, dict):
        error = error.get("code") or error.get("type")
    return str(error)[:80] if isinstance(error, (str, int)) and error else ""


def canjear_codigo(http: httpx.Client, codigo: str, pkce: Pkce, retorno: str, *,
                   ahora: datetime) -> Tokens:
    """El canje del código por los tokens, por formulario, como el cliente oficial."""
    try:
        r = http.post(URL_TOKEN, data={
            "grant_type": "authorization_code", "client_id": CLIENT_ID, "code": codigo,
            "code_verifier": pkce.verificador, "redirect_uri": retorno})
    except httpx.HTTPError as e:
        raise LoginFallido(f"No se pudo hablar con el emisor ({type(e).__name__}).") from None
    if r.status_code >= 400:
        codigo_de_error = _codigo_de_error(r)
        raise LoginFallido(f"El emisor rechazó el canje del código (HTTP {r.status_code}"
                           f"{', ' + codigo_de_error if codigo_de_error else ''}).")
    try:
        return tokens_de_la_respuesta(r.json(), ahora)
    except ValueError as e:
        raise LoginFallido(str(e)) from None


# --- Dónde se guarda la sesión ------------------------------------------------------------

def _dentro_del_repositorio(ruta: Path) -> bool:
    ruta_ = os.path.normcase(str(Path(ruta).resolve()))
    raiz = os.path.normcase(str(RAIZ_DEL_REPOSITORIO.resolve()))
    return ruta_ == raiz or ruta_.startswith(raiz.rstrip(os.sep) + os.sep)


def _fuera_del_repositorio(ruta: Path) -> Path:
    if _dentro_del_repositorio(ruta):
        raise ValueError(f"La sesión de ChatGPT se guarda fuera del repositorio; {ruta} está "
                         f"dentro (cambiá {VARIABLE_RUTA}).")
    return Path(ruta)


def ruta_de_la_sesion() -> Path:
    """`LEDA_CHATGPT_AUTH`, o `~/.leda/chatgpt.json`; nunca dentro del repositorio."""
    elegida = os.environ.get(VARIABLE_RUTA, "").strip()
    return _fuera_del_repositorio(Path(elegida) if elegida else
                                  Path.home() / ".leda" / "chatgpt.json")


def guardar(ruta: Path, tokens: Tokens) -> None:
    """La sesión, entera o nada (un temporal que se renombra), con permisos sólo para el dueño
    donde el sistema los tiene."""
    ruta = _fuera_del_repositorio(Path(ruta))
    ruta.parent.mkdir(parents=True, exist_ok=True)
    datos = {k: (v.isoformat() if isinstance(v, datetime) else v)
             for k, v in asdict(tokens).items()}
    temporal = ruta.with_name(ruta.name + ".tmp")
    descriptor = os.open(temporal, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo)
    try:
        os.chmod(temporal, 0o600)
    except OSError:
        pass
    os.replace(temporal, ruta)


def cargar(ruta: Path) -> Tokens:
    datos = json.loads(Path(ruta).read_text("utf-8"))
    for campo in ("expira", "renovado"):
        if datos.get(campo):
            datos[campo] = datetime.fromisoformat(datos[campo])
    return Tokens(**datos)


def enmascarar(tokens: Tokens) -> str:
    """La cuenta para mostrar: el correo con sólo sus dos primeras letras y el final de la
    cuenta de ChatGPT."""
    final = f"…{tokens.cuenta[-4:]}"
    if not tokens.correo or "@" not in tokens.correo:
        return final
    usuario, _, dominio = tokens.correo.partition("@")
    return f"{usuario[:2]}***@{dominio} ({final})"


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


# --- La sesión en uso: credenciales y renovación ----------------------------------------

class SesionChatGPT:
    """La sesión guardada, con la renovación automática. Segura entre hilos; entre procesos
    (la escucha y el corredor a la vez), antes de renovar vuelve a leer el archivo, por si otro
    ya renovó."""

    def __init__(self, ruta: Path, *, transporte: httpx.BaseTransport | None = None,
                 reloj: Callable[[], datetime] | None = None,
                 plazo_s: float = PLAZO_DEL_EMISOR_S) -> None:
        self.ruta = Path(ruta)
        self._transporte = transporte
        self._reloj = reloj or _ahora
        self._plazo_s = plazo_s
        self._tokens: Tokens | None = None
        self._rechazado: str | None = None
        self._candado = threading.Lock()

    @classmethod
    def abrir(cls, ruta: Path | None = None, **opciones: Any) -> SesionChatGPT:
        """La sesión guardada (por omisión, la de `ruta_de_la_sesion`), ya leída: sin ella,
        `SesionChatGPTAusente`."""
        sesion = cls(ruta or ruta_de_la_sesion(), **opciones)
        sesion._tokens = sesion._leer()
        return sesion

    def _leer(self) -> Tokens:
        try:
            return cargar(self.ruta)
        except FileNotFoundError:
            raise SesionChatGPTAusente(
                f"No hay sesión de ChatGPT iniciada ({COMO_ENTRAR}).") from None
        except (OSError, ValueError, TypeError) as e:
            raise SesionChatGPTAusente(
                f"No se pudo leer la sesión de ChatGPT guardada ({type(e).__name__}); volvé a "
                f"iniciarla: {COMO_ENTRAR}.") from None

    def _vencida(self, tokens: Tokens, ahora: datetime) -> bool:
        return tokens.necesita_renovar(ahora) or tokens.access_token == self._rechazado

    def credenciales(self) -> tuple[str, str]:
        """El token de acceso vigente y la cuenta, renovando antes de que venza o después de
        un 401. Si no se puede renovar, `SesionChatGPTVencida`."""
        with self._candado:
            ahora = self._reloj()
            tokens = self._tokens or self._leer()
            if self._vencida(tokens, ahora):
                tokens = self._leer()               # otro proceso pudo haber renovado
                if self._vencida(tokens, ahora):
                    tokens = self._renovar(tokens, ahora)
                self._rechazado = None
            self._tokens = tokens
            return tokens.access_token, tokens.cuenta

    def forzar_renovacion(self, acceso: str) -> None:
        """El servicio rechazó este acceso (401): el pedido siguiente renueva."""
        with self._candado:
            self._rechazado = acceso

    def _renovar(self, tokens: Tokens, ahora: datetime) -> Tokens:
        def vencida(por: str) -> SesionChatGPTVencida:
            return SesionChatGPTVencida(
                f"No se pudo renovar la sesión de ChatGPT ({por}); si sigue fallando, volvé "
                f"a iniciarla: {COMO_ENTRAR}.")

        try:
            with httpx.Client(transport=self._transporte, timeout=self._plazo_s) as http:
                r = http.post(URL_TOKEN, json={"client_id": CLIENT_ID,
                                               "grant_type": "refresh_token",
                                               "refresh_token": tokens.refresh_token})
        except httpx.HTTPError as e:
            raise vencida(f"sin respuesta del emisor: {type(e).__name__}") from None
        if r.status_code >= 400:
            codigo = _codigo_de_error(r)
            raise vencida(f"HTTP {r.status_code}{', ' + codigo if codigo else ''}")
        try:
            nuevos = tokens_de_la_respuesta(r.json(), ahora, anteriores=tokens)
        except ValueError as e:
            raise vencida(str(e).rstrip(".")) from None
        guardar(self.ruta, nuevos)
        return nuevos


# --- Del pedido de chat al de respuestas, y vuelta ---------------------------------------

def validar_parametros_chatgpt(parametros: dict[str, Any]) -> dict[str, Any]:
    """Los de `ia_real.validar_parametros`, más lo que el servicio de Codex no recibe
    (`temperature`) y lo que este cliente arma (`input`, `store`...): rechazados nombrándolos."""
    validos = validar_parametros(parametros)
    no_van = sorted(set(parametros) & NO_LOS_RECIBE)
    if no_van:
        raise ParametrosInvalidos(
            f"{', '.join(no_van)} no va con la suscripción de ChatGPT: el servicio de Codex no "
            f"lo recibe.")
    pisados = sorted(set(validos["cuerpo_extra"]) & DEL_PEDIDO_DE_RESPUESTAS)
    if pisados:
        raise ParametrosInvalidos(
            f"cuerpo_extra no puede llevar {', '.join(map(repr, pisados))}: lo arma el código.")
    return validos


def _contenido(rol: str, contenido: Any) -> list[dict[str, Any]]:
    tipo = "output_text" if rol == "assistant" else "input_text"
    if isinstance(contenido, str):
        return [{"type": tipo, "text": contenido}]
    return [{"type": tipo, "text": p.get("text", "")} for p in contenido or []
            if isinstance(p, dict) and p.get("type") in ("text", "input_text", "output_text")]


def _mensaje(mensaje: dict[str, Any]) -> dict[str, Any]:
    rol = {"system": "developer"}.get(mensaje["role"], mensaje["role"])
    if rol not in ("developer", "user", "assistant"):
        raise ValueError(f"Un mensaje con el rol {mensaje['role']!r} no se traduce.")
    return {"type": "message", "role": rol, "content": _contenido(rol, mensaje.get("content"))}


def _herramienta(herramienta: dict[str, Any]) -> dict[str, Any]:
    funcion = herramienta.get("function", herramienta)
    return {"type": "function", "name": funcion["name"],
            "description": funcion.get("description", ""), "strict": False,
            "parameters": funcion.get("parameters", {"type": "object", "properties": {}})}


def _eleccion(eleccion: Any) -> Any:
    if isinstance(eleccion, dict) and isinstance(eleccion.get("function"), dict):
        return {"type": "function", "name": eleccion["function"]["name"]}
    return eleccion


def pedido_de_respuestas(modelo: str, cuerpo: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """El pedido de chat de `ia_real` (`messages`, `tools`, `tool_choice`) en el formato de
    respuestas del servicio de Codex, y si va por "respuestas lite". Las instrucciones van como
    mensaje `developer`; `temperature` y los topes no van (ver el docstring del módulo)."""
    lite = modelo in MODELOS_LITE
    herramientas = [_herramienta(h) for h in cuerpo.get("tools") or []]
    entrada: list[dict[str, Any]] = []
    if herramientas and lite:
        entrada.append({"type": "additional_tools", "role": "developer", "tools": [
            {"type": "namespace", "name": ESPACIO_DE_FUNCIONES, "description": "",
             "tools": herramientas}]})
    entrada += [_mensaje(m) for m in cuerpo.get("messages") or []]
    pedido = {"model": modelo, "stream": True, "input": entrada,
              "tool_choice": _eleccion(cuerpo.get("tool_choice", "auto")),
              "parallel_tool_calls": False, "store": False,
              "include": ["reasoning.encrypted_content"]}
    if herramientas and not lite:
        pedido["tools"] = herramientas
    if lite:
        # El servicio lo exige para "respuestas lite" (HTTP 400 sin él; primera llamada real,
        # 2026-10-07). Lo que pida `cuerpo_extra` en `reasoning` se suma (`completar`).
        pedido["reasoning"] = {"context": "all_turns"}
    return pedido, lite


def cabeceras(acceso: str, cuenta: str, *, lite: bool) -> dict[str, str]:
    resultado = {"Authorization": f"Bearer {acceso}", "ChatGPT-Account-ID": cuenta,
                 "originator": ORIGINADOR, "OpenAI-Beta": "responses=experimental",
                 "accept": "text/event-stream"}
    if lite:
        resultado[CABECERA_LITE] = "true"
    return resultado


def leer_eventos(lineas: Iterable[str]) -> Iterator[dict[str, Any]]:
    """Los eventos de un flujo SSE: cada bloque de líneas `data:` hasta una línea vacía."""
    datos: list[str] = []

    def evento() -> dict[str, Any] | None:
        texto = "\n".join(datos)
        datos.clear()
        if not texto or texto == "[DONE]":
            return None
        try:
            leido = json.loads(texto)
        except ValueError:
            raise RespuestaInvalida("Un evento del flujo no es JSON.") from None
        return leido if isinstance(leido, dict) else None

    for linea in lineas:
        if linea == "":
            if (e := evento()) is not None:
                yield e
            continue
        if linea.startswith(":"):
            continue
        campo, _, valor = linea.partition(":")
        if campo == "data":
            datos.append(valor[1:] if valor.startswith(" ") else valor)
    if (e := evento()) is not None:
        yield e


def _error(error: Any) -> ErrorDeChatGPT:
    error = error if isinstance(error, dict) else {}
    codigo = error.get("code") or error.get("type") or "sin código"
    mensaje = str(error.get("message") or "")[:200]
    return ErrorDeChatGPT(f"ChatGPT no completó la respuesta ({codigo}"
                          f"{': ' + mensaje if mensaje else ''}).")


def _a_chat(salida: list[Any], por_partes: str, final: dict[str, Any]) -> dict[str, Any]:
    """La respuesta en la forma de chat que leen `ia_real.leer_jugadas` y `IAReal.redactar`."""
    textos: list[str] = []
    llamadas: list[dict[str, Any]] = []
    for item in salida:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "message" and item.get("role", "assistant") == "assistant":
            textos += [c.get("text") or "" for c in item.get("content") or []
                       if isinstance(c, dict) and c.get("type") in ("output_text", "text")]
        elif item.get("type") == "function_call":
            nombre = str(item.get("name") or "")
            espacio = item.get("namespace")
            if espacio and nombre.startswith(f"{espacio}."):
                nombre = nombre[len(espacio) + 1:]
            llamadas.append({"id": item.get("call_id") or item.get("id"), "type": "function",
                             "function": {"name": nombre,
                                          "arguments": item.get("arguments") or ""}})
    if final.get("status") == "incomplete":
        motivo = (final.get("incomplete_details") or {}).get("reason")
        if motivo not in ("max_output_tokens", "max_tokens"):
            raise RespuestaInvalida(f"La respuesta quedó incompleta ({motivo}).")
        fin = "length"
    else:
        fin = "tool_calls" if llamadas else "stop"
    texto = "".join(textos) if textos else por_partes
    mensaje: dict[str, Any] = {"role": "assistant", "content": texto or None}
    if llamadas:
        mensaje["tool_calls"] = llamadas
    uso = final.get("usage") or {}
    return {"model": final.get("model"),
            "choices": [{"index": 0, "message": mensaje, "finish_reason": fin}],
            "usage": {"prompt_tokens": uso.get("input_tokens"),
                      "completion_tokens": uso.get("output_tokens")}}


def respuesta_de_eventos(eventos: Iterable[dict[str, Any]],
                         al_avanzar: Callable[[str], None] | None = None) -> dict[str, Any]:
    """La respuesta del flujo. Con `al_avanzar`, cada parte de texto que llega se avisa con todo
    lo escrito hasta ahí (la respuesta en vivo, pedido del usuario del 2026-10-07). Un aviso que
    falla no cambia la respuesta: es lo que se muestra mientras tanto, no lo que vale."""
    items: list[Any] = []
    partes: list[str] = []
    final: dict[str, Any] | None = None
    for evento in eventos:
        tipo = evento.get("type")
        if tipo == "response.output_item.done":
            items.append(evento.get("item"))
        elif tipo == "response.output_text.delta":
            partes.append(str(evento.get("delta") or ""))
            if al_avanzar is not None:
                try:
                    al_avanzar("".join(partes))
                except Exception:  # noqa: BLE001 -- lo que se muestra nunca rompe la respuesta
                    pass
        elif tipo in ("response.completed", "response.incomplete"):
            final = evento.get("response") or {}
        elif tipo == "response.failed":
            raise _error((evento.get("response") or {}).get("error"))
        elif tipo == "error":
            raise _error(evento.get("error") or evento)
    if final is None:
        raise RespuestaInvalida("El flujo terminó sin completarse.")
    return _a_chat(items or final.get("output") or [], "".join(partes), final)


def respuesta_de_salida(cuerpo: Any) -> dict[str, Any]:
    """Una respuesta entera, sin flujo (por si el servicio contesta con JSON)."""
    if not isinstance(cuerpo, dict):
        raise RespuestaInvalida("Respuesta ilegible.")
    if cuerpo.get("error") or cuerpo.get("status") == "failed":
        raise _error(cuerpo.get("error"))
    return _a_chat(cuerpo.get("output") or [], "", cuerpo)


@dataclass
class ClienteChatGPT(ClienteCompatible):
    """El cliente de la IA por la suscripción: el mismo contrato que `ClienteCompatible`
    (`completar` recibe un pedido de chat y devuelve una respuesta de chat), sobre el servicio
    de Codex. Sin reintentos propios: el reintento es uno y lo hace el turno (decisión 8)."""

    sesion: SesionChatGPT | None = None

    @classmethod
    def crear(cls, modelo: str, sesion: SesionChatGPT, parametros: dict[str, Any],
              transporte: httpx.BaseTransport | None = None) -> ClienteChatGPT:
        parametros = validar_parametros_chatgpt(parametros)
        http = httpx.Client(timeout=parametros["timeout_s"], transport=transporte)
        return cls(modelo=modelo, base_url=(parametros.get("base_url") or BASE_URL).rstrip("/"),
                   http=http, parametros=parametros, sesion=sesion)

    def completar(self, cuerpo: dict[str, Any],
                  al_avanzar: Callable[[str], None] | None = None) -> dict[str, Any]:
        """Con `al_avanzar`, el texto que el servicio va escribiendo se avisa a medida que llega
        (`respuesta_de_eventos`). Corre en el hilo de `llamar_con_plazo`: si el plazo se agota,
        el aviso puede seguir llegando después; quien lo recibe lo ignora (el borrador ya se
        cerró, `despachador.IndicadorDeActividad`)."""
        plazo = float(self.parametros.get("plazo_s", PLAZO_S))
        extra = self.parametros.get("cuerpo_extra") or {}
        pedido, lite = pedido_de_respuestas(self.modelo, cuerpo)
        if isinstance(extra.get("reasoning"), dict) and "reasoning" in pedido:
            pedido = {**pedido, "reasoning": {**extra["reasoning"], **pedido["reasoning"]}}

        def pedir() -> dict[str, Any]:
            acceso, cuenta = self.sesion.credenciales()
            with self.http.stream("POST", f"{self.base_url}/responses",
                                  json={**extra, **pedido},
                                  headers=cabeceras(acceso, cuenta, lite=lite)) as r:
                if r.status_code == 401:
                    self.sesion.forzar_renovacion(acceso)
                if r.status_code >= 400:
                    r.read()
                    codigo = _codigo_de_error(r)
                    raise httpx.HTTPStatusError(
                        f"ChatGPT respondió HTTP {r.status_code}"
                        f"{' (' + codigo + ')' if codigo else ''}.",
                        request=r.request, response=r)
                # Sin `content-type`, lo pedido manda: el pedido siempre es un flujo (el servicio
                # real no declara el tipo; primera llamada real, 2026-10-07).
                tipo = r.headers.get("content-type", "")
                if "text/event-stream" in tipo or (not tipo and pedido.get("stream")):
                    return respuesta_de_eventos(leer_eventos(r.iter_lines()), al_avanzar)
                r.read()
                try:
                    return respuesta_de_salida(r.json())
                except ValueError:
                    raise RespuestaInvalida("Respuesta ilegible.") from None

        return llamar_con_plazo(pedir, plazo)


# --- Los comandos: entrar, ver el estado, salir ------------------------------------------

class _Retorno(http.server.BaseHTTPRequestHandler):
    estado = ""
    recibido: list[str]
    llego: threading.Event

    def do_GET(self) -> None:  # noqa: N802 -- nombre de http.server
        if urlsplit(self.path).path != "/auth/callback":
            self.send_response(404)
            self.end_headers()
            return
        try:
            codigo_del_retorno(self.path, self.estado)
            pagina = "Listo: Leda ya tiene la sesión de ChatGPT. Podés cerrar esta ventana."
        except LoginFallido as e:
            pagina = f"No se pudo iniciar la sesión: {e}"
        self.recibido.append(self.path)
        cuerpo = (f"<!doctype html><meta charset='utf-8'><title>Leda</title>"
                  f"<p>{pagina}</p>").encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)
        self.llego.set()

    def log_message(self, *argumentos: Any) -> None:
        pass            # la línea del pedido lleva el código: nunca se imprime


class _ServidorExclusivo(http.server.HTTPServer):
    # En Windows, `SO_REUSEADDR` deja escuchar en un puerto que otro ya usa: así un puerto
    # ocupado (otro ingreso de Codex abierto) falla y se pasa al de respaldo.
    allow_reuse_address = False


class ServidorDeRetorno:
    """El servidor local que recibe la vuelta del navegador, en el primer puerto libre."""

    def __init__(self, servidor: http.server.HTTPServer, recibido: list[str],
                 llego: threading.Event) -> None:
        self._servidor, self._recibido, self._llego = servidor, recibido, llego
        self.puerto = servidor.server_address[1]
        threading.Thread(target=servidor.serve_forever, daemon=True).start()

    @classmethod
    def abrir(cls, estado: str, puertos: Iterable[int] = PUERTOS) -> ServidorDeRetorno | None:
        recibido: list[str] = []
        llego = threading.Event()
        manejador = type("Retorno", (_Retorno,),
                         {"estado": estado, "recibido": recibido, "llego": llego})
        for puerto in puertos:
            try:
                return cls(_ServidorExclusivo((HOST_DE_RETORNO, puerto), manejador),
                           recibido, llego)
            except OSError:
                continue
        return None

    def esperar(self, segundos: float) -> str | None:
        return self._recibido[0] if self._llego.wait(segundos) else None

    def cerrar(self) -> None:
        self._servidor.shutdown()
        self._servidor.server_close()


def iniciar(*, ruta: Path | None = None, manual: bool = False,
            abrir: Callable[[str], Any] = webbrowser.open,
            entrada: Callable[[str], str] = input,
            transporte: httpx.BaseTransport | None = None,
            reloj: Callable[[], datetime] | None = None,
            puertos: Iterable[int] = PUERTOS,
            espera_s: float = ESPERA_DEL_NAVEGADOR_S) -> int:
    """`python -m leda chatgpt login`: el ingreso en el navegador, con un servidor local para
    la vuelta o, con `manual` (o si no hay puerto libre), pegando la dirección a la que volvió.
    Muestra sólo la cuenta enmascarada; 0 si quedó guardada, 1 si no."""
    reloj = reloj or _ahora
    try:
        ruta = _fuera_del_repositorio(ruta) if ruta else ruta_de_la_sesion()
    except ValueError as e:
        print(e)
        return 1
    pkce, estado = generar_pkce(), generar_estado()
    servidor = None if manual else ServidorDeRetorno.abrir(estado, puertos)
    if not manual and servidor is None:
        print("No se pudo abrir el puerto local del retorno: se sigue a mano.")
    retorno = direccion_de_retorno(servidor.puerto if servidor else PUERTOS[0])
    url = url_de_autorizacion(pkce, estado, retorno)
    print("Abrí esta dirección en el navegador (si no se abrió sola) y entrá con tu cuenta de "
          "ChatGPT:")
    print(url)
    try:
        abrir(url)
    except Exception:  # noqa: BLE001 -- sin navegador, la dirección ya está impresa
        pass
    try:
        if servidor is not None:
            vuelta = servidor.esperar(espera_s)
            if vuelta is None:
                raise LoginFallido(f"No volvió el navegador en {espera_s:g} s; probá con "
                                   f"--manual.")
        else:
            vuelta = entrada("Pegá acá la dirección completa a la que te llevó el navegador "
                             "(aunque la página dé error): ")
        codigo = codigo_del_retorno(vuelta, estado)
        with httpx.Client(transport=transporte, timeout=PLAZO_DEL_EMISOR_S) as cliente:
            tokens = canjear_codigo(cliente, codigo, pkce, retorno, ahora=reloj())
        guardar(ruta, tokens)
    except (LoginFallido, ValueError, OSError) as e:
        print(f"No se pudo iniciar la sesión: {e}")
        return 1
    finally:
        if servidor is not None:
            servidor.cerrar()
    print(f"Sesión iniciada para la cuenta {enmascarar(tokens)}. Quedó guardada fuera del "
          f"repositorio, en {ruta}.")
    return 0


def estado(ruta: Path | None = None, *, reloj: Callable[[], datetime] | None = None) -> int:
    """`python -m leda chatgpt estado`: si hay sesión, de qué cuenta y cuándo vence el acceso;
    nunca un token. 0 si hay sesión, 1 si no."""
    try:
        ruta = ruta or ruta_de_la_sesion()
        tokens = cargar(ruta)
    except FileNotFoundError:
        print(f"No hay sesión de ChatGPT iniciada ({COMO_ENTRAR}).")
        return 1
    except (OSError, ValueError, TypeError) as e:
        print(f"No se pudo leer la sesión de ChatGPT ({type(e).__name__}); volvé a iniciarla: "
              f"{COMO_ENTRAR}.")
        return 1
    ahora = (reloj or _ahora)()
    if tokens.expira is None:
        vence = "sin fecha de vencimiento; se renueva sola cada ocho días"
    elif tokens.expira <= ahora:
        vence = (f"el acceso venció el {tokens.expira:%Y-%m-%d %H:%M} UTC; se renueva en el "
                 f"próximo pedido")
    else:
        vence = (f"el acceso vence el {tokens.expira:%Y-%m-%d %H:%M} UTC y se renueva solo "
                 f"antes")
    print(f"Sesión de ChatGPT iniciada para la cuenta {enmascarar(tokens)}: {vence}.")
    return 0


def salir(ruta: Path | None = None) -> int:
    """`python -m leda chatgpt salir`: borra la sesión guardada (no la revoca en OpenAI)."""
    try:
        ruta = ruta or ruta_de_la_sesion()
    except ValueError as e:
        print(e)
        return 1
    if not Path(ruta).exists():
        print("No había sesión de ChatGPT iniciada.")
        return 0
    Path(ruta).unlink()
    print(f"Sesión de ChatGPT cerrada: se borró {ruta}.")
    return 0
