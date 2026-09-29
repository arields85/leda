"""Autorización OAuth de Google desde la computadora del administrador (G2c).

Flujo de "aplicación de escritorio" con redirección a loopback y PKCE, sin
librerías de Google: sólo `httpx` contra los endpoints REST.

    1. Se levanta un servidor HTTP en 127.0.0.1 (puerto efímero).
    2. Se arma la URL de autorización (S256, `state`, acceso sin conexión) y el
       administrador la abre en su navegador.
    3. Google redirige a `http://127.0.0.1:<puerto>/?code=...&state=...`.
    4. Se canjea el código por tokens en el endpoint de Google.
    5. Se validan la respuesta (refresh token, permisos concedidos) y la
       identidad (claims del `id_token`).

Este módulo no toca la base ni el cifrado: `autorizar` devuelve una
`Autorizacion` y quien la llama (`cli.py`) la guarda por `credenciales`.
Nunca se imprime ni se guarda el código, ningún token, el secreto del
cliente ni el `code_verifier`; los mensajes de error llevan sólo el código
`error` que devuelve Google, jamás su cuerpo crudo.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import secrets
import time
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable
from urllib.parse import parse_qs, urlencode, urlsplit

import httpx

VARIABLE_CLIENT_ID = "PRISMA_GOOGLE_CLIENT_ID"
VARIABLE_CLIENT_SECRET = "PRISMA_GOOGLE_CLIENT_SECRET"

URL_AUTORIZACION = "https://accounts.google.com/o/oauth2/v2/auth"
URL_TOKEN = "https://oauth2.googleapis.com/token"

SCOPE_GMAIL_ENVIO = "https://www.googleapis.com/auth/gmail.send"
SCOPE_CALENDARIO_EVENTOS = "https://www.googleapis.com/auth/calendar.events"

# Única fuente de los permisos que se piden.
SCOPES = ("openid", "email", SCOPE_GMAIL_ENVIO, SCOPE_CALENDARIO_EVENTOS)

# Los que no pueden faltar entre los concedidos (con consentimiento granular
# la persona puede destildar casillas), con cómo se nombran en el mensaje.
SCOPES_OBLIGATORIOS = {
    SCOPE_GMAIL_ENVIO: "enviar correos desde tu cuenta",
    SCOPE_CALENDARIO_EVENTOS: "crear y editar eventos de tu calendario",
}

EMISORES_GOOGLE = ("accounts.google.com", "https://accounts.google.com")

# Cuánto se espera que el administrador termine en el navegador.
ESPERA_MAXIMA_SEGUNDOS = 300.0

_TIMEOUT_HTTP = httpx.Timeout(15.0, connect=5.0)
_CODIGO_ERROR = re.compile(r"[a-z][a-z0-9_]{0,63}")


class ErrorOAuth(Exception):
    """Falla del flujo. El mensaje es apto para mostrarse tal cual: nunca
    lleva tokens, códigos, secretos ni el cuerpo crudo de Google."""


@dataclass(frozen=True)
class ClienteOAuth:
    client_id: str
    client_secret: str = field(repr=False)


@dataclass(frozen=True)
class Autorizacion:
    """Lo validado que salió del flujo. `refresh_token` y `access_token` son
    secretos: no aparecen en `repr`."""

    refresh_token: str = field(repr=False)
    access_token: str | None = field(repr=False)
    # Instante en que vence el access token (UTC), si Google informó la
    # duración; G2d puede usarlo para no renovar de más.
    access_token_expira_en: datetime | None
    cuenta_email: str
    scopes: tuple[str, ...]


def cargar_cliente(entorno=None) -> ClienteOAuth:
    """Lee el cliente OAuth del entorno (`prisma.config` ya cargó `.env`).
    Nombra la variable que falta, nunca su valor."""
    entorno = os.environ if entorno is None else entorno
    faltan = [v for v in (VARIABLE_CLIENT_ID, VARIABLE_CLIENT_SECRET)
              if not (entorno.get(v) or "").strip()]
    if faltan:
        raise ErrorOAuth(
            "Falta configurar " + " y ".join(faltan) + " en .env: son las "
            "credenciales del cliente OAuth de Google (tipo aplicación de "
            "escritorio).")
    return ClienteOAuth(entorno[VARIABLE_CLIENT_ID].strip(),
                        entorno[VARIABLE_CLIENT_SECRET].strip())


# ---------------------------------------------------------------------------
# PKCE y URL de autorización
# ---------------------------------------------------------------------------


def _b64url(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode("ascii")


def nuevo_pkce() -> tuple[str, str]:
    """`(code_verifier, code_challenge)` según RFC 7636: 32 bytes aleatorios
    (43 caracteres) y desafío S256."""
    verificador = _b64url(secrets.token_bytes(32))
    desafio = _b64url(hashlib.sha256(verificador.encode("ascii")).digest())
    return verificador, desafio


def construir_url(cliente: ClienteOAuth, redirect_uri: str, desafio: str,
                  state: str) -> str:
    return URL_AUTORIZACION + "?" + urlencode({
        "client_id": cliente.client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "code_challenge": desafio,
        "code_challenge_method": "S256",
        "state": state,
    })


# ---------------------------------------------------------------------------
# Servidor de loopback: exactamente una devolución de llamada
# ---------------------------------------------------------------------------

_PAGINA = (
    "<!doctype html><html lang=\"es\"><meta charset=\"utf-8\">"
    "<title>Prisma</title><body style=\"font-family:sans-serif;margin:3em\">"
    "<p>Ya podés cerrar esta pestaña y volver a la terminal.</p></body></html>"
).encode("utf-8")


class _Servidor(HTTPServer):
    resultado: dict[str, str] | None = None


class _Manejador(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 (API de http.server)
        partes = urlsplit(self.path)
        params = {k: v[0] for k, v in parse_qs(partes.query).items()}
        # Sólo cuenta la devolución de Google: `/` con `state`. Un pedido de
        # favicon o cualquier otra cosa se descarta sin cerrar la espera.
        cuenta = partes.path == "/" and "state" in params
        self.send_response(200 if cuenta else 404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(_PAGINA) if cuenta else 0))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if cuenta:
            self.wfile.write(_PAGINA)
            self.server.resultado = params

    def log_message(self, *args):  # el código llega en la URL: no se registra
        pass


def _esperar_devolucion(servidor: _Servidor, segundos: float,
                        reloj: Callable[[], float]) -> dict[str, str] | None:
    limite = reloj() + segundos
    while servidor.resultado is None:
        restante = limite - reloj()
        if restante <= 0:
            return None
        servidor.timeout = restante
        servidor.handle_request()
    return servidor.resultado


# ---------------------------------------------------------------------------
# Canje del código y validación
# ---------------------------------------------------------------------------


def _codigo_de_error(cuerpo) -> str:
    """Sólo el campo `error` de Google, y sólo si tiene la forma de un
    código; cualquier otra cosa es "desconocido"."""
    valor = cuerpo.get("error") if isinstance(cuerpo, dict) else None
    if isinstance(valor, str) and _CODIGO_ERROR.fullmatch(valor):
        return valor
    return "desconocido"


def _canjear(http: httpx.Client, cliente: ClienteOAuth, codigo: str,
             redirect_uri: str, verificador: str) -> dict:
    try:
        r = http.post(URL_TOKEN, timeout=_TIMEOUT_HTTP, data={
            "code": codigo,
            "client_id": cliente.client_id,
            "client_secret": cliente.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "code_verifier": verificador,
        })
    except httpx.HTTPError:
        raise ErrorOAuth(
            "No se pudo conectar con Google para completar la "
            "autorización. Revisá tu conexión y volvé a intentar.") from None
    try:
        cuerpo = r.json()
    except ValueError:
        cuerpo = None
    if not r.is_success:
        raise ErrorOAuth(
            "Google rechazó la autorización (error: "
            f"{_codigo_de_error(cuerpo)}).")
    if not isinstance(cuerpo, dict):
        raise ErrorOAuth("Google devolvió una respuesta que no se entiende.")
    return cuerpo


def _claims_id_token(id_token) -> dict:
    """Los claims del `id_token`, SIN verificar la firma.

    El token vino directo del endpoint de tokens de Google por TLS: según
    OpenID Connect Core §3.1.3.7 esa validación TLS puede reemplazar la de la
    firma. Igual se comprueban emisor, audiencia, vencimiento y correo en
    `_identidad`."""
    try:
        cuerpo = id_token.split(".")[1]
        cuerpo += "=" * (-len(cuerpo) % 4)
        claims = json.loads(base64.urlsafe_b64decode(cuerpo))
    except (AttributeError, IndexError, ValueError):
        raise ErrorOAuth("Google no devolvió una identidad válida.") from None
    if not isinstance(claims, dict):
        raise ErrorOAuth("Google no devolvió una identidad válida.")
    return claims


def _identidad(id_token, cliente: ClienteOAuth, ahora: datetime) -> str:
    claims = _claims_id_token(id_token)
    audiencia = claims.get("aud")
    exp = claims.get("exp")
    correo = claims.get("email")
    if claims.get("iss") not in EMISORES_GOOGLE:
        raise ErrorOAuth("La identidad no viene de Google.")
    if not (audiencia == cliente.client_id or (
            isinstance(audiencia, list) and cliente.client_id in audiencia)):
        raise ErrorOAuth("La identidad es de otro cliente OAuth.")
    if (not isinstance(exp, (int, float)) or isinstance(exp, bool)
            or exp <= ahora.timestamp()):
        raise ErrorOAuth("La identidad que devolvió Google ya venció.")
    if not isinstance(correo, str) or not correo.strip():
        raise ErrorOAuth("Google no informó el correo de la cuenta.")
    if claims.get("email_verified") is not True:
        raise ErrorOAuth("Google no verificó el correo de esa cuenta.")
    return correo.strip().lower()


def validar(respuesta: dict, cliente: ClienteOAuth,
            ahora: datetime) -> Autorizacion:
    refresh = respuesta.get("refresh_token")
    if not isinstance(refresh, str) or not refresh:
        raise ErrorOAuth(
            "Google no devolvió un permiso de larga duración. Sacá el acceso "
            "de Prisma en https://myaccount.google.com/permissions y volvé a "
            "correr el comando.")
    concedidos = tuple(str(respuesta.get("scope") or "").split())
    faltan = [texto for scope, texto in SCOPES_OBLIGATORIOS.items()
              if scope not in concedidos]
    if faltan:
        raise ErrorOAuth(
            "No se guardó nada: faltó aceptar el permiso para "
            + " y para ".join(faltan)
            + ". Volvé a correr el comando y dejá todas las casillas "
              "tildadas.")
    correo = _identidad(respuesta.get("id_token"), cliente, ahora)

    acceso = respuesta.get("access_token")
    acceso = acceso if isinstance(acceso, str) and acceso else None
    duracion = respuesta.get("expires_in")
    expira = None
    if acceso and isinstance(duracion, (int, float)) and not isinstance(
            duracion, bool):
        expira = ahora + timedelta(seconds=duracion)
    return Autorizacion(refresh, acceso, expira, correo, concedidos)


# ---------------------------------------------------------------------------
# Flujo completo
# ---------------------------------------------------------------------------


def _abrir_navegador(url: str) -> None:
    webbrowser.open(url)


def _nuevo_http() -> httpx.Client:
    return httpx.Client()


def autorizar(cliente: ClienteOAuth, *,
              http: httpx.Client | None = None,
              abrir_navegador: Callable[[str], object] | None = None,
              esperar_segundos: float | None = None,
              imprimir: Callable[[str], object] = print,
              reloj: Callable[[], float] = time.monotonic,
              ahora: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
              ) -> Autorizacion:
    """Corre el flujo completo y devuelve la autorización validada, o lanza
    `ErrorOAuth`. `abrir_navegador=None` sólo imprime la URL. El transporte
    HTTP, el navegador, los relojes y el plazo son inyectables."""
    esperar = ESPERA_MAXIMA_SEGUNDOS if esperar_segundos is None else esperar_segundos
    verificador, desafio = nuevo_pkce()
    state = _b64url(secrets.token_bytes(24))

    servidor = _Servidor(("127.0.0.1", 0), _Manejador)
    propio = http is None
    http = http or _nuevo_http()
    try:
        redirect_uri = f"http://127.0.0.1:{servidor.server_address[1]}/"
        url = construir_url(cliente, redirect_uri, desafio, state)
        imprimir("Abrí este enlace en tu navegador para autorizar a Prisma "
                 "(tenés unos minutos):")
        imprimir(url)
        if abrir_navegador is not None:
            abrir_navegador(url)

        params = _esperar_devolucion(servidor, esperar, reloj)
        if params is None:
            raise ErrorOAuth(
                "Se agotó el tiempo de espera sin recibir la autorización. "
                "Volvé a correr el comando.")
        if not secrets.compare_digest(params.get("state", ""), state):
            raise ErrorOAuth(
                "La respuesta no corresponde a esta autorización (state "
                "distinto). No se guardó nada.")
        if "error" in params:
            raise ErrorOAuth(
                "Google no concedió la autorización (error: "
                f"{_codigo_de_error(params)}).")
        codigo = params.get("code")
        if not codigo:
            raise ErrorOAuth("La respuesta de Google no trajo el código.")
        respuesta = _canjear(http, cliente, codigo, redirect_uri, verificador)
        return validar(respuesta, cliente, ahora())
    finally:
        servidor.server_close()
        if propio:
            http.close()
