"""Entrar a la web con Telegram: la Mini App en el celular y el QR en la computadora (ADR 0024,
decisiones 4, 5, 7, 8 y 9; unidad MA de `odd/tasks/plataforma-jerarquias.md`; migración 0073).

Rutas, todas bajo `/app` y del mismo origen que la web (la cookie de cada puerta sigue siendo
`HttpOnly`, `Secure` y `SameSite=Strict`):

- `POST /app/api/entrar-telegram` (la puerta del equipo) y `POST /app/admin/api/entrar-telegram`
  (la de administración): la web, abierta como Mini App, manda lo que Telegram le pasó
  (`initData`). **La firma se comprueba acá**, siempre: HMAC-SHA256 con la clave que deriva del
  token del bot de esa puerta (https://core.telegram.org/bots/webapps#validating-data-received-
  via-the-mini-app). Para la del equipo, el token es el del bot del espacio que dice la dirección
  de la Mini App (`/app/e/<espacio>/`): ese dato solo no abre nada, porque la firma tiene que
  verificar con el token de ese bot, y nunca se prueban varios tokens hasta que uno coincida. Para
  la de administración, sólo `LEDA_BOT_TOKEN_ADMIN`. La firma vale 10 minutos (`auth_date`) y una
  sola vez (la base guarda su huella). Después la base busca la membresía activa del espacio (o
  el rol de plataforma) por el usuario de Telegram y abre la sesión, auditada con su origen.
- `POST /app/api/entrar/qr` y `POST /app/admin/api/entrar/qr`: la computadora pide entrar. Recibe
  el enlace `t.me/<bot>?start=compu_<código>` y la matriz del QR (`qr.modulos`), y en una cookie
  propia el secreto con el que después pregunta (así sólo esa computadora lo canjea, aunque otro
  vea el QR). Vence a los 5 minutos.
- `GET /app/api/entrar/qr/{id}` y `GET /app/admin/api/entrar/qr/{id}`: la computadora pregunta
  cada pocos segundos. Cuando alguien tocó "Entrar en la compu" en Telegram (`bot_entrar`), la
  base le da su sesión una sola vez, y queda la cookie de esa puerta.
- `GET` y `POST /app/admin/api/espacios/{id}/sesion-en-la-compu`: cuánto queda recordada una
  computadora en ese espacio (1, 7, 30 o 90 días, o sin vencimiento; decisión 5).
- `GET /app/abrir/e/<espacio>/` y `GET /app/abrir/admin/`: el lanzador que abren los botones de la
  Mini App y el del menú (`despachador.direccion_de_la_mini_app`). En el celular sigue a la web
  dentro de Telegram; en Telegram de la computadora, que muestra la Mini App dentro de un marco,
  abre la web en el navegador, donde se entra con el QR (decisión del usuario, 2026-10-14). Es lo
  único que se deja enmarcar, y sólo por Telegram: no tiene sesión, ni datos, ni formularios.

**Nunca se registran** `initData`, la firma, los tokens de los bots ni los de las sesiones: en la
consola, sólo el tipo de una falla.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qsl

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response

from . import qr
from .config import config
from .db import admin as conexion_admin
from .db import espacio as en_el_espacio
from .db import sin_espacio
from .web_app import (BOT_USUARIO, CAMINO_DE_ADMINISTRACION, COOKIE, COOKIE_DE_ADMINISTRACION,
                      LARGO_MAXIMO_DEL_TOKEN, USUARIO_DEL_BOT, _con_la_base,
                      _con_la_version_del_nucleo, _de_otro_sitio, _hash, _imprimir, _json,
                      _no_existe, _sin_sesion_de_administracion, _token_de_administracion)

router = APIRouter(prefix="/app")

PUERTA_DEL_EQUIPO = "equipo"
PUERTA_DE_ADMINISTRACION = "administracion"

# Cuánto vale una firma de Telegram desde que se emitió (decisión 7), y cuánto puede venir del
# futuro por la diferencia de relojes. La base exige lo mismo (migración 0074,
# `abrir_sesion_por_telegram`): el vencimiento que recibe es `auth_date` más 10 minutos, así que
# nunca está a más de 11 minutos de su reloj (los 10 de la vigencia más el minuto de adelanto). El
# comentario de esa función dice "vale 10 minutos" y compara con 11: los dos valores son estos.
VIGENCIA_DE_LA_FIRMA_S = 10 * 60
ADELANTO_TOLERADO_S = 60
# Lo más largo que se acepta mirar de `initData` (Telegram manda unos 500 caracteres).
LARGO_MAXIMO_DE_INIT_DATA = 4096
# Un espacio, como lo escribe la dirección de la Mini App.
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
# El código que va en el enlace del QR (`start`, de 1 a 64 caracteres A-Z, a-z, 0-9, _ y -).
PREFIJO_DEL_CODIGO = "compu_"
CODIGO = re.compile(r"^compu_[A-Za-z0-9_-]{20,58}$")

# La sesión de la Mini App se renueva en cada apertura: la cookie dura lo que la sesión (24 horas,
# la base la corta igual). La de la computadora, lo más que aceptan los navegadores: la que vale es
# la de la base, que vence con el ajuste del espacio.
DURACION_DE_LA_MINI_APP_S = 24 * 60 * 60
DURACION_DE_LA_COOKIE_S = 400 * 24 * 60 * 60
# El secreto de la computadora que pidió entrar por el QR: una cookie por puerta, sólo para sus
# rutas del QR, que vence con el pedido.
COOKIE_DEL_QR = {PUERTA_DEL_EQUIPO: "leda_qr", PUERTA_DE_ADMINISTRACION: "leda_qr_admin"}
CAMINO_DEL_QR = {PUERTA_DEL_EQUIPO: "/app/api/entrar/qr",
                 PUERTA_DE_ADMINISTRACION: f"{CAMINO_DE_ADMINISTRACION}/api/entrar/qr"}
VIGENCIA_DEL_QR_S = 5 * 60

# Los días que se pueden elegir para la sesión de la computadora (`None`: sin vencimiento).
DIAS_DE_LA_SESION_EN_LA_COMPU = (1, 7, 30, 90)
AJUSTE_DE_LA_SESION_EN_LA_COMPU = "sesion_en_la_compu_dias"

TEXTO_SIN_MEMBRESIA = ("Esta cuenta de Telegram no es de este equipo. Abrí Leda desde el chat "
                       "de tu equipo.")
TEXTO_SIN_ROL = "Esta cuenta de Telegram no tiene acceso a la administración de Leda."
TEXTO_FIRMA_INVALIDA = "No se pudo comprobar que vengas de Telegram. Cerrá y volvé a abrir Leda."


# --- La firma de Telegram (decisión 7) ----------------------------------------------------------

@dataclass(frozen=True)
class FirmaDeTelegram:
    """Lo que vale de una firma ya comprobada: quién es en Telegram, la huella de la firma (para
    gastarla una sola vez) y hasta cuándo vale."""
    telegram_user_id: int
    huella: str
    vence_en: datetime


def validar_init_data(init_data: str, token_del_bot: str,
                      ahora: float | None = None) -> FirmaDeTelegram | None:
    """La firma de `initData` comprobada con el token de ESE bot, o `None`: mal formada, de otro
    bot, vencida (más de 10 minutos) o sin un usuario. La cadena que se firma son todos los
    campos menos `hash`, ordenados, `clave=valor` separados por un salto de línea; la clave
    secreta es HMAC-SHA256 del token con la clave "WebAppData"."""
    if (not init_data or not token_del_bot or len(init_data) > LARGO_MAXIMO_DE_INIT_DATA):
        return None
    try:
        pares = parse_qsl(init_data, keep_blank_values=True, strict_parsing=True)
    except ValueError:
        return None
    campos: dict[str, str] = {}
    for clave, valor in pares:
        if clave in campos:
            return None                 # un campo repetido no se firma de una sola manera
        campos[clave] = valor
    recibido = campos.pop("hash", "")
    if not re.fullmatch(r"[0-9a-f]{64}", recibido):
        return None
    a_revisar = "\n".join(f"{clave}={campos[clave]}" for clave in sorted(campos))
    secreto = hmac.new(b"WebAppData", token_del_bot.encode(), hashlib.sha256).digest()
    esperado = hmac.new(secreto, a_revisar.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(esperado, recibido):
        return None
    try:
        emitida = int(campos["auth_date"])
        usuario = json.loads(campos["user"])
        telegram_user_id = int(usuario["id"])
    except (KeyError, ValueError, TypeError):
        return None
    ahora = time.time() if ahora is None else ahora
    if ahora - emitida > VIGENCIA_DE_LA_FIRMA_S or emitida - ahora > ADELANTO_TOLERADO_S:
        return None
    if telegram_user_id <= 0 or isinstance(usuario.get("is_bot"), bool) and usuario["is_bot"]:
        return None
    return FirmaDeTelegram(
        telegram_user_id, hashlib.sha256(recibido.encode()).hexdigest(),
        datetime.fromtimestamp(emitida + VIGENCIA_DE_LA_FIRMA_S, tz=timezone.utc))


def es_un_espacio(slug: Any) -> bool:
    """Si `slug` puede ser el espacio de la puerta del equipo: con la forma de un espacio y nunca
    el del bot de administración (revisión R3-team-door-accepts-admin-slug: su firma no abre
    nunca la puerta del equipo)."""
    return isinstance(slug, str) and bool(SLUG.match(slug)) and slug != "admin"


def _token_del_bot(slug: str) -> str | None:
    try:
        return config.token_bot(slug)
    except LookupError:
        return None


async def _cuerpo(request: Request) -> dict[str, Any] | None:
    """El cuerpo JSON de un pedido, o `None` si no lo es."""
    if (request.headers.get("content-type") or "").split(";")[0].strip() != "application/json":
        return None
    try:
        cuerpo = await request.json()
    except ValueError:
        return None
    return cuerpo if isinstance(cuerpo, dict) else None


def _poner_cookie(respuesta: Response, puerta: str, token: str, duracion_s: int) -> None:
    if puerta == PUERTA_DEL_EQUIPO:
        respuesta.set_cookie(COOKIE, token, max_age=duracion_s, path="/app", secure=True,
                             httponly=True, samesite="strict")
    else:
        respuesta.set_cookie(COOKIE_DE_ADMINISTRACION, token, max_age=duracion_s,
                             path=CAMINO_DE_ADMINISTRACION, secure=True, httponly=True,
                             samesite="strict")


@router.post("/api/entrar-telegram")
async def entrar_con_la_mini_app(request: Request):
    """La puerta del equipo abierta como Mini App del bot de un espacio."""
    if _de_otro_sitio(request):
        return _json({"error": "origen_no_verificado"}, 403)
    cuerpo = await _cuerpo(request)
    if cuerpo is None:
        return _json({"error": "cuerpo_invalido"}, 415)
    slug = cuerpo.get("espacio")
    init_data = cuerpo.get("init_data")
    if not es_un_espacio(slug) or not isinstance(init_data, str):
        return _json({"error": "cuerpo_invalido"}, 422)
    token = _token_del_bot(slug)
    firma = validar_init_data(init_data, token or "")
    if firma is None:
        return _json({"error": "firma_invalida", "texto": TEXTO_FIRMA_INVALIDA}, 401)
    sesion = secrets.token_urlsafe(32)

    def abrir(conn) -> Response:
        with sin_espacio(conn) as cur:
            _con_la_version_del_nucleo(cur)
            cur.execute("select abrir_sesion_por_telegram(%s, %s, %s, %s, %s) as r",
                        (slug, firma.telegram_user_id, firma.huella, firma.vence_en,
                         _hash(sesion)))
            resultado = cur.fetchone()["r"]
        return _respuesta_de_la_apertura(resultado, PUERTA_DEL_EQUIPO, sesion)

    return await _en_la_base(abrir)


@router.post("/admin/api/entrar-telegram")
async def entrar_a_la_administracion_con_la_mini_app(request: Request):
    """La puerta de administración abierta como Mini App del bot de administración: sólo su
    token (`LEDA_BOT_TOKEN_ADMIN`)."""
    if _de_otro_sitio(request):
        return _json({"error": "origen_no_verificado"}, 403)
    cuerpo = await _cuerpo(request)
    if cuerpo is None:
        return _json({"error": "cuerpo_invalido"}, 415)
    init_data = cuerpo.get("init_data")
    if not isinstance(init_data, str):
        return _json({"error": "cuerpo_invalido"}, 422)
    firma = validar_init_data(init_data, _token_del_bot("admin") or "")
    if firma is None:
        return _json({"error": "firma_invalida", "texto": TEXTO_FIRMA_INVALIDA}, 401)
    sesion = secrets.token_urlsafe(32)

    def abrir(conn) -> Response:
        with sin_espacio(conn) as cur:
            _con_la_version_del_nucleo(cur)
            cur.execute("select abrir_sesion_de_administracion_por_telegram(%s, %s, %s, %s) as r",
                        (firma.telegram_user_id, firma.huella, firma.vence_en, _hash(sesion)))
            resultado = cur.fetchone()["r"]
        return _respuesta_de_la_apertura(resultado, PUERTA_DE_ADMINISTRACION, sesion)

    return await _en_la_base(abrir)


def _respuesta_de_la_apertura(resultado: dict[str, Any], puerta: str, sesion: str) -> Response:
    if resultado.get("ok"):
        respuesta = _json({"ok": True})
        _poner_cookie(respuesta, puerta, sesion, DURACION_DE_LA_MINI_APP_S)
        return respuesta
    motivo = resultado.get("motivo")
    if motivo == "firma_usada":
        # La misma apertura otra vez (la Mini App se recargó): la web sigue con la sesión que ya
        # tiene, si la tiene.
        return _json({"error": "firma_usada"}, 409)
    if motivo == "sin_membresia":
        return _json({"error": "sin_membresia", "texto": TEXTO_SIN_MEMBRESIA}, 403)
    if motivo == "sin_rol":
        return _json({"error": "sin_rol", "texto": TEXTO_SIN_ROL}, 403)
    if motivo == "sin_espacio":
        return _json({"error": "sin_espacio"}, 404)
    if motivo in ("mal_formado", "firma_vencida"):
        return _json({"error": "firma_invalida", "texto": TEXTO_FIRMA_INVALIDA}, 401)
    # Un motivo que este código no conoce no es una firma inválida (revisión R2-catchall): la
    # persona ve que no se pudo, sin detalles, y la consola, el motivo.
    _imprimir(f"  ! la entrada con Telegram devolvió un motivo desconocido ({motivo!r}).")
    return _json({"error": "no_disponible"}, 503)


async def _en_la_base(trabajo) -> Response:
    return await _en_un_hilo(_con_la_base, trabajo)


async def _en_un_hilo(funcion, *args):
    from starlette.concurrency import run_in_threadpool

    return await run_in_threadpool(funcion, *args)


# --- El lanzador de la Mini App (Telegram en la computadora; MA-2) ------------------------------
#
# Telegram de escritorio y Telegram Web muestran la Mini App dentro de un marco cuya página es de
# `https://web.telegram.org` (en Linux, Telegram de escritorio carga ahí su propio marco; en
# Windows y en Mac, según la versión, la abre directo en su navegador interno, sin marco). La web
# no se deja enmarcar, así que el botón abre este lanzador, que sí, y sólo por ese origen. En un
# celular (`ios`, `android`) sigue a la web dentro de Telegram, con lo que Telegram le pasó en el
# fragmento (la firma); en la computadora abre la web en el navegador (`openLink`), sin la firma,
# y muestra "Abrí Leda en el navegador" con un botón para volver a abrirla. La lógica está en
# `web/public/abrir.js`; esta página no tiene nada del pedido, ni sesión, ni datos.

ORIGENES_QUE_ENMARCAN_EL_LANZADOR = ("https://web.telegram.org",)
# A dónde puede llevar: la puerta del equipo de un espacio, o la de administración.
DESTINO_DEL_LANZADOR = re.compile(r"^(?:e/([a-z0-9][a-z0-9-]{0,63})/|admin/)$")
CABECERAS_DEL_LANZADOR = {
    "Cache-Control": "no-store",
    "Referrer-Policy": "no-referrer",
    "X-Robots-Tag": "noindex, nofollow",
    "X-Content-Type-Options": "nosniff",
    # Sin `X-Frame-Options`: no admite una lista de orígenes, y `frame-ancestors` la reemplaza.
    "Content-Security-Policy": ("default-src 'none'; script-src 'self'; "
                                "style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; "
                                "connect-src 'none'; frame-ancestors "
                                + " ".join(ORIGENES_QUE_ENMARCAN_EL_LANZADOR)),
}
PAGINA_DEL_LANZADOR = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Leda</title>
<style>
html,body{margin:0;min-height:100%;background:#0F1010;color:#E4E4E4}
body{font-family:"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace;font-size:15px}
main{max-width:28rem;margin:0 auto;padding:3rem 1.25rem}
p{margin:0 0 1.5rem;line-height:1.5}
button{font:inherit;color:#E4E4E4;background:#1C1D1D;border:1px solid #3A3B3B;border-radius:6px;padding:.6rem 1rem;cursor:pointer}
button:hover{border-color:#6B6C6C}
</style>
<script src="/app/telegram-web-app.js"></script>
<script src="/app/abrir.js" defer></script>
</head>
<body>
<main id="lanzador"></main>
</body>
</html>
"""


@router.get("/abrir/{destino:path}", include_in_schema=False)
def el_lanzador(destino: str):
    """El lanzador de la Mini App: la misma página para cualquiera, sin sesión. Un destino que no
    es una puerta no existe (y no se deja enmarcar)."""
    encontrado = DESTINO_DEL_LANZADOR.match(destino)
    if encontrado is None or (encontrado.group(1) is not None
                              and not es_un_espacio(encontrado.group(1))):
        return _no_existe()
    return HTMLResponse(PAGINA_DEL_LANZADOR, headers=CABECERAS_DEL_LANZADOR)


# --- El QR de la computadora (decisiones 4 y 8) -------------------------------------------------

def desde_donde(request: Request) -> str:
    """Desde dónde se pidió, en palabras para el chat: el navegador, el sistema y la dirección
    IP (la del túnel, si la manda; sólo para mostrar, nunca para decidir nada)."""
    agente = request.headers.get("user-agent") or ""
    navegador = next((nombre for marca, nombre in (
        ("Edg/", "Edge"), ("OPR/", "Opera"), ("Firefox/", "Firefox"), ("Chrome/", "Chrome"),
        ("Safari/", "Safari")) if marca in agente), "un navegador")
    sistema = next((nombre for marca, nombre in (
        ("Windows", "Windows"), ("iPhone", "un iPhone"), ("iPad", "un iPad"),
        ("Android", "Android"), ("CrOS", "ChromeOS"), ("Mac OS X", "una Mac"),
        ("Linux", "Linux")) if marca in agente), None)
    ip = _ip_de_quien_pide(request)
    texto = navegador + (f" en {sistema}" if sistema else "")
    return (texto + (f", IP {ip}" if ip else ""))[:120]


def _ip_de_quien_pide(request: Request) -> str | None:
    """La IP que se muestra (revisión R1-001): la de quien se conecta; la que manda el túnel
    (`CF-Connecting-IP`) sólo si quien se conecta es el túnel en esta misma máquina (una dirección
    local), porque cualquiera puede escribir esa cabecera. `X-Forwarded-For` no se cree. Nunca
    algo que no sea una IP."""
    import ipaddress

    def ip(valor: str | None) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
        try:
            return ipaddress.ip_address((valor or "").strip())
        except ValueError:
            return None

    directa = ip(request.client.host if request.client else None)
    if directa is not None and directa.is_loopback:
        del_tunel = ip(request.headers.get("cf-connecting-ip"))
        if del_tunel is not None:
            return str(del_tunel)
    return str(directa) if directa is not None else None


_USUARIO_DEL_BOT_DE_ADMINISTRACION: dict[str, str] = {}
_CANDADO_DEL_USUARIO = threading.Lock()


def usuario_del_bot_de_administracion() -> str | None:
    """El usuario público del bot de administración, para el enlace del QR: el de
    `LEDA_BOT_USUARIO_ADMIN`, o el que contesta Telegram (`getMe`) con su token, una vez por
    proceso. `None` si no se sabe."""
    import os

    configurado = os.environ.get("LEDA_BOT_USUARIO_ADMIN", "").lstrip("@")
    if configurado:
        return configurado if USUARIO_DEL_BOT.fullmatch(configurado) else None
    token = _token_del_bot("admin")
    if not token:
        return None
    clave = hashlib.sha256(token.encode()).hexdigest()
    with _CANDADO_DEL_USUARIO:
        if clave not in _USUARIO_DEL_BOT_DE_ADMINISTRACION:
            usuario = _pedir_el_usuario(token)
            if usuario is None:
                return None
            _USUARIO_DEL_BOT_DE_ADMINISTRACION[clave] = usuario
        return _USUARIO_DEL_BOT_DE_ADMINISTRACION[clave]


def _pedir_el_usuario(token: str) -> str | None:
    """`getMe` del bot; nunca imprime el token ni el error crudo."""
    try:
        from .motor.escucha import BotTelegram

        resultado = BotTelegram(token).llamar("getMe") or {}
    except Exception as falla:  # noqa: BLE001 -- sin el usuario no hay QR, y se dice
        _imprimir(f"  ! no se pudo saber el usuario del bot de administración "
                  f"({type(falla).__name__}).")
        return None
    usuario = resultado.get("username") if isinstance(resultado, dict) else None
    return usuario if isinstance(usuario, str) and USUARIO_DEL_BOT.fullmatch(usuario) else None


def _usuario_del_bot_del_espacio(conn, slug: str) -> str | None:
    with sin_espacio(conn) as cur:
        cur.execute("select id from workspace where slug = %s and activo", (slug,))
        fila = cur.fetchone()
    if fila is None:
        return None
    with en_el_espacio(conn, str(fila["id"])) as cur:
        cur.execute("""select valor #>> '{}' as usuario from workspace_setting
                        where workspace_id = %s and clave = %s""", (str(fila["id"]), BOT_USUARIO))
        bot = cur.fetchone()
    usuario = bot["usuario"] if bot else None
    return usuario if usuario and USUARIO_DEL_BOT.fullmatch(usuario) else None


def enlace_del_qr(usuario_del_bot: str, codigo: str) -> str:
    return f"https://t.me/{usuario_del_bot}?start={codigo}"


async def _pedir_el_qr(request: Request, puerta: str) -> Response:
    if _de_otro_sitio(request):
        return _json({"error": "origen_no_verificado"}, 403)
    cuerpo = await _cuerpo(request)
    if cuerpo is None:
        return _json({"error": "cuerpo_invalido"}, 415)
    slug = cuerpo.get("espacio") if puerta == PUERTA_DEL_EQUIPO else None
    if puerta == PUERTA_DEL_EQUIPO and not es_un_espacio(slug):
        return _json({"error": "cuerpo_invalido"}, 422)
    codigo = PREFIJO_DEL_CODIGO + secrets.token_urlsafe(24)
    secreto = secrets.token_urlsafe(32)
    desde = desde_donde(request)
    # El usuario del bot de administración se averigua antes de tomar el candado de la web: puede
    # ser una llamada a Telegram (revisión R4-getme-under-lock-in-db-work).
    usuario_admin = (await _en_un_hilo(usuario_del_bot_de_administracion)
                     if puerta == PUERTA_DE_ADMINISTRACION else None)

    def pedir(conn) -> Response:
        usuario = (_usuario_del_bot_del_espacio(conn, slug) if puerta == PUERTA_DEL_EQUIPO
                   else usuario_admin)
        if usuario is None:
            return _json({"error": "sin_bot"}, 404)
        with sin_espacio(conn) as cur:
            cur.execute("select pedir_entrada_por_qr(%s, %s, %s, %s, %s) as r",
                        (puerta, slug, _hash(codigo), _hash(secreto), desde))
            resultado = cur.fetchone()["r"]
        if not resultado.get("ok"):
            motivo = resultado.get("motivo")
            if motivo == "demasiados":
                return _json({"error": "demasiados"}, 429)
            return _json({"error": motivo or "no_disponible"},
                         404 if motivo == "sin_espacio" else 422)
        enlace = enlace_del_qr(usuario, codigo)
        respuesta = _json({"pedido_id": resultado["pedido_id"], "enlace": enlace,
                           "qr": qr.modulos(enlace), "vence_en": resultado["vence_en"]}, 201)
        respuesta.set_cookie(COOKIE_DEL_QR[puerta], secreto, max_age=VIGENCIA_DEL_QR_S,
                             path=CAMINO_DEL_QR[puerta], secure=True, httponly=True,
                             samesite="strict")
        return respuesta

    return await _en_la_base(pedir)


def _preguntar_por_el_qr(request: Request, puerta: str, pedido_id: str) -> Response:
    secreto = request.cookies.get(COOKIE_DEL_QR[puerta]) or ""
    if not 0 < len(secreto) <= LARGO_MAXIMO_DEL_TOKEN or not es_un_uuid(pedido_id):
        return _json({"estado": "no_esta"}, 404)
    sesion = secrets.token_urlsafe(32)

    def canjear(conn) -> Response:
        with sin_espacio(conn) as cur:
            _con_la_version_del_nucleo(cur)
            cur.execute("select canjear_pedido_de_entrada(%s, %s, %s, %s) as r",
                        (pedido_id, puerta, _hash(secreto), _hash(sesion)))
            resultado = cur.fetchone()["r"]
        estado = resultado.get("estado")
        if estado == "adentro":
            respuesta = _json({"estado": "adentro"})
            _poner_cookie(respuesta, puerta, sesion, DURACION_DE_LA_COOKIE_S)
            respuesta.delete_cookie(COOKIE_DEL_QR[puerta], path=CAMINO_DEL_QR[puerta],
                                    secure=True, httponly=True, samesite="strict")
            return respuesta
        if estado == "pendiente":
            return _json({"estado": "pendiente"})
        if estado == "vencido":
            return _json({"estado": "vencido"})
        return _json({"estado": "no_esta"}, 404)

    return _con_la_base(canjear)


def es_un_uuid(valor: str) -> bool:
    return re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                        valor or "") is not None


@router.post("/api/entrar/qr")
async def pedir_el_qr_del_equipo(request: Request):
    return await _pedir_el_qr(request, PUERTA_DEL_EQUIPO)


@router.get("/api/entrar/qr/{pedido_id}")
def preguntar_por_el_qr_del_equipo(pedido_id: str, request: Request):
    return _preguntar_por_el_qr(request, PUERTA_DEL_EQUIPO, pedido_id)


@router.post("/admin/api/entrar/qr")
async def pedir_el_qr_de_la_administracion(request: Request):
    return await _pedir_el_qr(request, PUERTA_DE_ADMINISTRACION)


@router.get("/admin/api/entrar/qr/{pedido_id}")
def preguntar_por_el_qr_de_la_administracion(pedido_id: str, request: Request):
    return _preguntar_por_el_qr(request, PUERTA_DE_ADMINISTRACION, pedido_id)


# --- Cuánto dura la sesión de la computadora (decisión 5) ---------------------------------------

@router.get("/admin/api/espacios/{espacio_id}/sesion-en-la-compu")
def leer_la_sesion_en_la_compu(espacio_id: str, request: Request):
    """Los días que queda recordada una computadora en ese espacio, o `null` (sin vencimiento)."""
    token = _token_de_administracion(request)
    if token is None or not es_un_uuid(espacio_id):
        return _sin_sesion_de_administracion() if token is None else _json(
            {"error": "no_existe"}, 404)

    def leer(conn) -> Response:
        with sin_espacio(conn) as cur:
            cur.execute("select sesion_en_la_compu(%s, %s) as r", (_hash(token), espacio_id))
            resultado = cur.fetchone()["r"]
        return _respuesta_del_ajuste(resultado)

    return _con_la_base(leer)


@router.post("/admin/api/espacios/{espacio_id}/sesion-en-la-compu")
async def fijar_la_sesion_en_la_compu(espacio_id: str, request: Request):
    """Lo cambia la administración: `{"dias": 1 | 7 | 30 | 90 | null}`."""
    if _de_otro_sitio(request):
        return _json({"error": "origen_no_verificado"}, 403)
    token = _token_de_administracion(request)
    if token is None:
        return _sin_sesion_de_administracion()
    cuerpo = await _cuerpo(request)
    if cuerpo is None:
        return _json({"error": "cuerpo_invalido"}, 415)
    dias = cuerpo.get("dias")
    if not es_un_uuid(espacio_id) or "dias" not in cuerpo or not (
            dias is None or (type(dias) is int and dias in DIAS_DE_LA_SESION_EN_LA_COMPU)):
        return _json({"error": "cuerpo_invalido"}, 422)

    def fijar(conn) -> Response:
        with sin_espacio(conn) as cur:
            _con_la_version_del_nucleo(cur)
            cur.execute("select fijar_sesion_en_la_compu(%s, %s, %s) as r",
                        (_hash(token), espacio_id, dias))
            resultado = cur.fetchone()["r"]
        return _respuesta_del_ajuste(resultado)

    return await _en_la_base(fijar)


def _respuesta_del_ajuste(resultado: dict[str, Any]) -> Response:
    if resultado.get("ok"):
        return _json({"dias": resultado.get("dias")})
    if resultado.get("motivo") == "sin_sesion":
        return _sin_sesion_de_administracion()
    if resultado.get("motivo") == "sin_espacio":
        return _json({"error": "no_existe"}, 404)
    return _json({"error": "cuerpo_invalido"}, 422)


# --- Lo que usa el bot (`motor.bot_entrar`) ---------------------------------------------------

def ver_pedido(cur, codigo: str, puerta: str, slug: str | None) -> dict[str, Any] | None:
    """El pedido pendiente de ese código, de esa puerta (y, la del equipo, del espacio de ese
    bot), o `None`."""
    if not CODIGO.match(codigo or ""):
        return None
    cur.execute("select * from ver_pedido_de_entrada(%s, %s, %s)",
                (_hash(codigo), puerta, slug))
    return cur.fetchone()


def aprobar_pedido(cur, pedido_id: str, puerta: str, slug: str | None,
                   telegram_user_id: int) -> dict[str, Any]:
    """Quien tocó "Entrar en la compu" aprueba el pedido (`{"ok": ...}`, con su motivo)."""
    _con_la_version_del_nucleo(cur)
    cur.execute("select aprobar_pedido_de_entrada(%s, %s, %s, %s) as r",
                (pedido_id, puerta, slug, telegram_user_id))
    return cur.fetchone()["r"]


def con_la_conexion_de_administracion(conn):
    """La transacción de la consola (`leda_admin`), para el bot de administración."""
    return conexion_admin(conn)
