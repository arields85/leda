"""La API interna de la plataforma web: la puerta del equipo, de sólo lectura (ADR 0022,
decisiones 3, 4, 5, 11, 12, 13, 16.1, 17 y 18; porción 1, tarea P1-3 de
`odd/tasks/plataforma-p1.md`).

Rutas, todas bajo `/app` y servidas por la misma aplicación que la página de la tarea
(`entrada.py`), así la cookie es del mismo origen:

- `GET /app/entrar/{token}`: una página con el botón "Entrar", y nada más. Abrir el enlace no lo
  gasta: Telegram y los revisores de correo lo abren para armar la vista previa antes que la
  persona, y lo gastarían. La página es la misma para cualquier enlace: no dice si sirve.
- `POST /app/entrar/{token}` (el botón): canjea el enlace de un solo uso que manda Leda por una
  sesión y la deja en una cookie `HttpOnly`, `Secure` y `SameSite=Strict`, sólo para `/app`;
  después lleva a la web (303 a `/app/`). Un enlace usado, anulado, inventado o de alguien que
  dejó el equipo muestra siempre la misma página humana, sin detalles técnicos (constitución
  §10). Un pedido que dice venir de otro sitio no canjea nada.
- `GET /app/api/yo`: quién es la persona de la sesión, de qué espacio, qué vistas tiene y, si el
  pack del espacio declara el bot del equipo, la dirección de su chat (`chat_con_leda`, para el
  botón "> consultar a leda"; decisión 8 del usuario, 2026-10-12).
- `GET /app/api/tareas?vista=tus|sector|equipo`: lo que muestra cada vista (decisión 18): el panel
  con un número por estado, la semana del calendario del espacio, cada tarea abierta con su
  estado, sus marcas (trabada y vencida pueden ir juntas), su fecha, la previsión de un atraso ya
  hablado, los días hábiles que quedan, la barra de días hábiles de una tarea en curso y, si está
  trabada, la cadena de esperas en árbol; y aparte, las terminadas de los últimos 30 días con
  quién las hizo (decisiones del usuario del 2026-10-12, 1, 3, 5, 6 y 7).
- `POST /app/salir`: corta la sesión (`cerro_la_sesion`) y borra la cookie.
- La puerta de administración (decisiones 10 y 12; porción 2, tarea P2-1, migración 0061), la de
  un administrador de plataforma, que abarca todos los espacios: `GET` y `POST
  /app/admin/entrar/{token}` (el mismo botón), con su propia cookie `leda_admin`, sólo para
  `/app/admin`; `GET /app/admin/api/yo` (quién es y los espacios que existen) y `POST
  /app/admin/salir`. El rol de plataforma se revalida en la base en cada pedido; las dos puertas
  no se abren con la cookie de la otra (constitución §2).
- La carga de una tarea por la puerta de administración (decisiones 9 y 11; porción 2, tarea
  P2-2, migración 0062): `GET /app/admin/api/espacios/{id}/opciones` (lo que el formulario
  necesita) y `POST /app/admin/api/espacios/{id}/tareas` (JSON, con la misma protección contra
  pedidos de otro sitio que salir). Valida y escribe la base (`opciones_de_la_carga` y
  `cargar_tarea`), que comprueba la sesión y el espacio en cada llamada: este módulo sólo revisa
  la forma de los datos y pone en palabras lo que la base rechaza (422) o avisa.
- `GET /app/` y las demás páginas bajo `/app` (tarea P1-4): la web compilada de `web/dist`
  (React, decisión 17), del mismo origen que la API. `index.html` no se guarda; los archivos con
  huella de `assets/` se guardan un año. Sin compilar, la persona ve un mensaje humano.

**Nada del pedido elige a la persona ni al espacio** (decisión 11): salen del hash del token de la
cookie, por las funciones de la base (`sesion_vigente`, `vistas_de_la_sesion`,
`tareas_de_la_sesion`, `esperas_de_la_sesion` y `terminadas_de_la_sesion`, migraciones 0057 a
0060), que revalidan la membresía en cada pedido y deciden quién ve qué (decisión 13). Si una
tarea está vencida o trabada lo decide la base (de una tarea ajena, lo mismo que el informe al
grupo: el atraso, recién cuando ya se habló en privado): este módulo nunca lo calcula.

**Los tokens** (el del enlace y el de la sesión) nunca se guardan en claro, nunca se imprimen y
nunca vuelven en una respuesta, salvo el de la sesión en su propia cookie. La sesión no vence
(decisión 4): la cookie dura lo más que un navegador acepta y se renueva al pedir `/app/api/yo`;
la que vale es la de la base, que se corta sólo por un administrador, por la persona o porque dejó
el equipo.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import threading
import time
import uuid
from collections.abc import Callable
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from fastapi import APIRouter, Request
from fastapi.responses import (FileResponse, HTMLResponse, JSONResponse, RedirectResponse,
                               Response)
from starlette.concurrency import run_in_threadpool

from .calendario import Calendario
from .db import conectar, sin_espacio
from .importador import BOT_USUARIO, USUARIO_DEL_BOT

router = APIRouter(prefix="/app")

# La cookie de la sesión de la puerta del equipo (decisión 12: cada puerta tendrá la suya).
COOKIE = "leda_sesion"
# La sesión no vence; la cookie, lo más que aceptan los navegadores (400 días): se renueva sola
# cada vez que la web pregunta quién es la persona.
DURACION_DE_LA_COOKIE_S = 400 * 24 * 60 * 60
# Lo más largo que puede ser un token que se acepta mirar (`secrets.token_urlsafe(32)`: 43).
LARGO_MAXIMO_DEL_TOKEN = 128

# Cómo se corta una sesión desde la web, desde la consola y por chat (motivos de la 0057): la
# persona avisa por chat que perdió el celular (`perdi_el_celular`, decisión 3 del usuario).
CERRO_LA_SESION = "cerro_la_sesion"
POR_UN_ADMINISTRADOR = "administrador"
PERDIO_EL_CELULAR = "perdio_el_celular"
# El camino del enlace de entrada (`enlace`) y lo más largo que es su token
# (`secrets.token_urlsafe(32)`: 43): la salida le reserva ese lugar al texto que lo lleva
# (`salida.reserva_del_enlace_de_entrada`).
CAMINO_DE_ENTRADA = "/app/entrar/"
LARGO_DEL_TOKEN_DE_ENTRADA = 43

# Lo que lleva toda respuesta de `/app`, como la página de la tarea: que nada la guarde ni la
# indexe, que no diga de dónde viene quien sigue un enlace, que no se adivine el tipo y que no se
# pueda meter en un marco. La política de contenido es la de una web de una sola página del mismo
# origen: sus scripts, estilos, letras e imágenes, y pedidos sólo a sí misma.
CABECERAS_DE_LA_WEB = {
    "Cache-Control": "no-store",
    "Referrer-Policy": "no-referrer",
    "X-Robots-Tag": "noindex, nofollow",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": ("default-src 'self'; script-src 'self'; style-src 'self'; "
                                "img-src 'self' data:; font-src 'self'; connect-src 'self'; "
                                "object-src 'none'; base-uri 'none'; form-action 'self'; "
                                "frame-ancestors 'none'"),
}
# La página de un enlace que no sirve no ejecuta nada (como la de la tarea).
CABECERAS_DE_UNA_PAGINA = {
    **CABECERAS_DE_LA_WEB,
    "Content-Security-Policy": ("default-src 'none'; style-src 'unsafe-inline'; "
                                "base-uri 'none'; form-action 'none'; frame-ancestors 'none'"),
}
# La página del botón "Entrar": tampoco ejecuta nada, y su formulario sólo va a este sitio. Con
# `no-referrer`, el navegador manda `Origin: null` al apretar el botón y el pedido no se podría
# distinguir de uno de otro sitio; con `same-origin` manda el origen del sitio, y la dirección
# con el token sólo viaja hacia este mismo servidor (la página no carga nada de otro lado).
CABECERAS_DEL_BOTON = {
    **CABECERAS_DE_LA_WEB,
    "Referrer-Policy": "same-origin",
    "Content-Security-Policy": ("default-src 'none'; style-src 'unsafe-inline'; "
                                "base-uri 'none'; form-action 'self'; frame-ancestors 'none'"),
}

# La web compilada (`npm run build` en `web/`): la sirve esta misma aplicación, así la cookie
# sigue siendo del mismo origen (decisión 17). Node hace falta para compilar, no para correr.
CARPETA_DE_LA_WEB = Path(__file__).resolve().parents[2] / "web" / "dist"
# Los archivos de `assets/` llevan una huella en el nombre: cambian de nombre si cambian.
GUARDAR_UN_ANIO = "public, max-age=31536000, immutable"
# El tipo de cada archivo de la web, explícito: con `nosniff`, un script con otro tipo no corre,
# y el registro de Windows no siempre sabe el de `.js`.
TIPOS_DE_LA_WEB = {
    ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css",
    ".woff2": "font/woff2", ".woff": "font/woff", ".svg": "image/svg+xml",
    ".png": "image/png", ".ico": "image/x-icon", ".json": "application/json",
    ".webmanifest": "application/manifest+json", ".txt": "text/plain", ".html": "text/html",
}

VISTAS = {"tus": "Tus tareas", "sector": "Tu sector", "equipo": "El equipo"}
DIAS_CORTOS = ("lun", "mar", "mié", "jue", "vie", "sáb", "dom")

# Los cuatro estados con color de la decisión 18. Trabada y vencida pueden ir juntas (decisión 5
# del usuario, 2026-10-12); entregada y en curso, sólo sin ninguna de ellas.
TRABADA, VENCIDA, ENTREGADA, EN_CURSO = "trabada", "vencida", "entregada", "en_curso"
MARCAS = (VENCIDA, TRABADA, EN_CURSO, ENTREGADA)

# Las páginas se leen de a una, con su conexión: no comparten la del webhook ni la de la página
# de la tarea, ni esperan a un turno de la conversación.
_WEB = threading.Lock()


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _conn_de_la_web():
    """La conexión de la web, una por proceso y reabierta si se cerró."""
    if not hasattr(_conn_de_la_web, "_c") or _conn_de_la_web._c.closed:
        _conn_de_la_web._c = conectar()
    return _conn_de_la_web._c


def _ahora(conn, workspace_id: str) -> datetime:
    """El reloj de Leda para ese espacio (con su adelanto en `leda_motor`), como lo lee la
    entrada para un turno."""
    from .entrada import _reloj_de

    return _reloj_de(conn, workspace_id).ahora()


def _imprimir(linea: str) -> None:
    """En la consola del servidor, sólo las fallas, sin tokens ni datos."""
    print(linea)


def _con_la_version_del_nucleo(cur) -> None:
    """La versión de las reglas del núcleo, para la auditoría de canjear, cortar y emitir
    (constitución §12): la base no lee los archivos del núcleo. Local a la transacción."""
    from . import versiones

    cur.execute("select set_config('leda.nucleo_hash', %s, true)", (versiones.nucleo_hash(),))


def _sin_transaccion(conn) -> None:
    try:
        conn.rollback()
    except Exception:  # noqa: BLE001 -- una conexión rota se reabre en el próximo pedido
        pass


def _json(datos: dict[str, Any], status_code: int = 200) -> JSONResponse:
    return JSONResponse(datos, status_code=status_code, headers=CABECERAS_DE_LA_WEB)


def _sin_sesion() -> JSONResponse:
    """Sin una sesión que entre: 401, y la cookie que no sirve se borra."""
    respuesta = _json({"error": "sin_sesion"}, 401)
    _borrar_la_cookie(respuesta)
    return respuesta


def _borrar_la_cookie(respuesta: Response) -> None:
    respuesta.delete_cookie(COOKIE, path="/app", secure=True, httponly=True, samesite="strict")


def _poner_la_cookie(respuesta: Response, token: str) -> None:
    respuesta.set_cookie(COOKIE, token, max_age=DURACION_DE_LA_COOKIE_S, path="/app",
                         secure=True, httponly=True, samesite="strict")


def _token_de_la_cookie(request: Request) -> str | None:
    token = request.cookies.get(COOKIE) or ""
    return token if 0 < len(token) <= LARGO_MAXIMO_DEL_TOKEN else None


def _con_la_base(trabajo: Callable[[Any], Response]) -> Response:
    """Corre `trabajo(conn)` con la conexión de la web, de a un pedido. Si la base falla, la
    persona recibe un 503 sin detalles (constitución §10) y la consola, sólo el tipo de falla."""
    with _WEB:
        conn = None
        try:
            conn = _conn_de_la_web()
            return trabajo(conn)
        except Exception as falla:  # noqa: BLE001 -- la web nunca muestra un error técnico
            if conn is not None:
                _sin_transaccion(conn)
            _imprimir(f"  ! la web no pudo atender un pedido ({type(falla).__name__}).")
            return _json({"error": "no_disponible"}, 503)


def _sesion(cur, token: str) -> dict[str, Any] | None:
    """La sesión vigente del token (que revalida la membresía y deja fijado su espacio en la
    transacción), o `None`."""
    _con_la_version_del_nucleo(cur)
    cur.execute("select * from sesion_vigente(%s)", (_hash(token),))
    return cur.fetchone()


# --- Entrar -----------------------------------------------------------------------------------

# El aspecto de las dos páginas sin la web (decisión 18): los mismos colores, bordes y sombra.
_ESTILO_DE_UNA_PAGINA = """
body{margin:0;background:#0F1010;color:#E6E6E3;
font:14px/1.5 'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace}
main{max-width:26rem;margin:0 auto;padding:18px 20px 32px}
.marca{font-size:11px;color:#6F7277;margin:0}
h1{font-size:24px;font-weight:800;letter-spacing:-0.02em;margin:10px 0 16px}
p{margin:0 0 12px;color:#B0B2B6}
a{color:#E6E6E3}
button{display:flex;align-items:center;width:100%;height:48px;margin-top:20px;padding:0 14px;
font:inherit;font-size:14px;font-weight:700;color:#E6E6E3;background:#161717;
border:1.5px solid #E6E6E3;border-radius:6px;box-shadow:3px 3px 0 #E6E6E3}
"""


def _pagina(titulo: str, cuerpo: str) -> str:
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Leda</title>
<style>{_ESTILO_DE_UNA_PAGINA}</style></head>
<body><main>
<p class="marca">LEDA</p>
<h1>{titulo}</h1>
{cuerpo}
</main></body></html>
"""


def pagina_de_enlace_que_no_sirve() -> str:
    """La página de un enlace que ya no sirve: humana y sin detalles (constitución §10)."""
    return _pagina("Este enlace ya no sirve.", """<p>Cada enlace abre la página una sola vez, en un solo teléfono o computadora.</p>
<p>Pedile a Leda uno nuevo por Telegram.</p>""")


def pagina_del_boton() -> str:
    """La página que muestra un enlace al abrirlo, igual para cualquier enlace: el botón manda
    el formulario a la misma dirección, así el token no aparece en la página."""
    return _pagina("Acá podés ver tus tareas.", """<p>Este enlace abre la sesión en este teléfono o computadora, una sola vez.</p>
<form method="post"><button type="submit">Entrar</button></form>""")


def _de_otro_sitio(request: Request) -> bool:
    """Además de `SameSite=Strict`: un pedido que dice venir de otro sitio (o de ninguno, con
    `Origin: null`) no cambia nada. Sin la cabecera, decide la cookie."""
    origen = request.headers.get("origin")
    return origen is not None and urlsplit(origen).netloc != request.headers.get("host", "")


def _no_sirve() -> HTMLResponse:
    return HTMLResponse(pagina_de_enlace_que_no_sirve(), status_code=404,
                        headers=CABECERAS_DE_UNA_PAGINA)


@router.get("/entrar/{token}")
def ver_el_boton(token: str):
    """Abrir el enlace no lo canjea: muestra el botón "Entrar", sin mirar el token."""
    return HTMLResponse(pagina_del_boton(), headers=CABECERAS_DEL_BOTON)


@router.post("/entrar/{token}")
def entrar(token: str, request: Request):
    """El botón: canjea el enlace por una sesión, una sola vez, y lleva a la web con la cookie
    puesta."""
    if _de_otro_sitio(request):
        return HTMLResponse(_pagina("No se pudo entrar desde acá.", """<p>Abrí el enlace que te mandó Leda y apretá "Entrar".</p>"""), status_code=403,
                            headers=CABECERAS_DE_UNA_PAGINA)
    if not 0 < len(token) <= LARGO_MAXIMO_DEL_TOKEN:
        return _no_sirve()
    sesion = secrets.token_urlsafe(32)

    def canjear(conn) -> Response:
        with sin_espacio(conn) as cur:
            _con_la_version_del_nucleo(cur)
            cur.execute("select canjear_enlace_de_entrada(%s, %s) as id",
                        (_hash(token), _hash(sesion)))
            fila = cur.fetchone()
        if fila is None or fila["id"] is None:
            return _no_sirve()
        respuesta = RedirectResponse("/app/", status_code=303, headers=CABECERAS_DE_LA_WEB)
        _poner_la_cookie(respuesta, sesion)
        return respuesta

    return _con_la_base(canjear)


# --- Quién es ---------------------------------------------------------------------------------

@router.get("/api/yo")
def yo(request: Request):
    """Quién es la persona de la sesión, de qué espacio y qué vistas tiene."""
    token = _token_de_la_cookie(request)
    if token is None:
        return _sin_sesion()

    def leer(conn) -> Response:
        with sin_espacio(conn) as cur:
            sesion = _sesion(cur, token)
            if sesion is None:
                return _sin_sesion()
            cur.execute("select vistas from vistas_de_la_sesion(%s)", (_hash(token),))
            vistas = cur.fetchone()
            cur.execute("select nombre from integrante where membership_id = %s",
                        (sesion["membership_id"],))
            persona = cur.fetchone()
            cur.execute("select nombre from workspace where id = %s", (sesion["workspace_id"],))
            espacio = cur.fetchone()
            cur.execute("""select valor #>> '{}' as usuario from workspace_setting
                            where workspace_id = %s and clave = %s""",
                        (sesion["workspace_id"], BOT_USUARIO))
            bot = cur.fetchone()
        if vistas is None:
            return _sin_sesion()
        respuesta = _json({
            "persona": persona["nombre"] if persona else "",
            "espacio": espacio["nombre"] if espacio else "",
            "vistas": [{"vista": v, "titulo": VISTAS[v]} for v in vistas["vistas"]
                       if v in VISTAS],
            "chat_con_leda": _chat_con_leda(bot["usuario"] if bot else None)})
        _poner_la_cookie(respuesta, token)
        return respuesta

    return _con_la_base(leer)


def _chat_con_leda(usuario: str | None) -> str | None:
    """La dirección del chat con el bot del equipo, o `None`: sin un usuario válido no hay
    botón (la base ya lo exige; acá, otra vez, porque va en un enlace)."""
    if not usuario or not USUARIO_DEL_BOT.fullmatch(usuario):
        return None
    return f"https://t.me/{usuario}"


# --- Las tareas de una vista ------------------------------------------------------------------

@router.get("/api/tareas")
def tareas(request: Request, vista: str = "tus"):
    """Lo que muestra una vista de la persona de la sesión (decisión 18)."""
    if vista not in VISTAS:
        return _json({"error": "vista_desconocida"}, 404)
    token = _token_de_la_cookie(request)
    if token is None:
        return _sin_sesion()

    def leer(conn) -> Response:
        with sin_espacio(conn) as cur:
            sesion = _sesion(cur, token)
            if sesion is None:
                return _sin_sesion()
            cur.execute("select vistas from vistas_de_la_sesion(%s)", (_hash(token),))
            vistas = cur.fetchone()
        if vistas is None:
            return _sin_sesion()
        if vista not in vistas["vistas"]:
            return _json({"error": "vista_no_disponible"}, 403)
        ws = str(sesion["workspace_id"])
        ahora = _ahora(conn, ws)
        with sin_espacio(conn) as cur:
            # Otra vez la sesión: pudo cortarse mientras se leía el reloj.
            if _sesion(cur, token) is None:
                return _sin_sesion()
            cur.execute("select * from tareas_de_la_sesion(%s, %s, %s)",
                        (_hash(token), vista, ahora))
            filas = cur.fetchall()
            cur.execute("select * from esperas_de_la_sesion(%s, %s, %s)",
                        (_hash(token), vista, ahora))
            esperas = cur.fetchall()
            cur.execute("select * from terminadas_de_la_sesion(%s, %s, %s)",
                        (_hash(token), vista, ahora))
            terminadas = cur.fetchall()
            calendario = Calendario.desde_base(cur, ws)
        return _json(armar_vista(vista, filas, esperas, calendario, ahora, terminadas))

    return _con_la_base(leer)


def armar_vista(vista: str, filas: list[dict[str, Any]], esperas: list[dict[str, Any]],
                calendario, ahora: datetime,
                terminadas: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """La respuesta de una vista con lo que devolvió la base: nada de lo que se arma acá decide
    quién ve qué ni si una tarea está vencida o trabada."""
    hoy = ahora.astimezone(calendario.zona).date()
    arboles = _arboles(esperas)
    tareas_ = [_tarea(f, arboles, calendario, ahora, hoy) for f in filas]
    # Una tarea trabada y vencida cuenta en los dos números: lleva las dos marcas.
    panel = {marca: 0 for marca in MARCAS}
    for t in tareas_:
        for marca in t["marcas"]:
            panel[marca] += 1
    vencen = {t["fecha_objetivo"] for t in tareas_ if t["fecha_objetivo"]}
    return {
        "vista": vista, "titulo": VISTAS[vista],
        "hoy": hoy.isoformat(), "semana_iso": hoy.isocalendar()[1],
        "panel": panel, "activas": len(tareas_),
        "semana": _semana(calendario, hoy, vencen),
        "tareas": tareas_,
        "terminadas": [_terminada(f, calendario) for f in terminadas or []],
    }


def _local(momento: datetime | None, calendario) -> date | None:
    return None if momento is None else momento.astimezone(calendario.zona).date()


def _marcas(fila: dict[str, Any]) -> list[str]:
    """Los estados con color de la tarjeta: trabada y vencida, juntas si son las dos (decisión 5
    del usuario), tal como las dio la base; sin ninguna de ellas, entregada o en curso; las
    demás, ninguno (gris)."""
    marcas = [marca for marca, columna in ((TRABADA, "bloqueo_abierto"), (VENCIDA, "vencida"))
              if fila[columna] is True]
    if marcas:
        return marcas
    if fila["estado"] == "en_revision":
        return [ENTREGADA]
    if fila["estado"] == "en_curso":
        return [EN_CURSO]
    return []


def _tarea(fila: dict[str, Any], arboles: dict[str, list[dict[str, Any]]], calendario,
           ahora: datetime, hoy: date) -> dict[str, Any]:
    vence = _local(fila["fecha_objetivo"], calendario)
    asignada = _local(fila["asignada_en"], calendario)
    bloqueo = fila["bloqueo_abierto"]
    marcas = _marcas(fila)
    prevision = fila.get("prevision")
    return {
        "id": str(fila["task_id"]),
        "titulo": fila["titulo"],
        "estado": fila["estado"],
        # La primera marca da el color del marco; la web muestra todas.
        "marca": marcas[0] if marcas else None,
        "marcas": marcas,
        "fecha_objetivo": vence.isoformat() if vence else None,
        # El día que dio la persona, posterior al vencimiento (un atraso ya hablado).
        "prevision": prevision.isoformat() if prevision else None,
        "asignada_el": asignada.isoformat() if asignada else None,
        "responsable": fila["responsable"],
        "area": fila["area"],
        "papel": fila["papel"],
        "vencida": fila["vencida"],
        # El "+3d" de "[VENCIDA +3d]": días hábiles desde la fecha, sólo para quien la base le
        # mostró el atraso.
        "dias_de_atraso": (calendario.habiles_entre(fila["fecha_objetivo"], ahora)
                           if fila["vencida"] is True and fila["fecha_objetivo"] else None),
        "bloqueo_abierto": bloqueo,
        "ve_la_pagina": fila["ve_la_pagina"],
        # Los días que quedan, sólo mientras la fecha no pasó: contar los de atraso le diría el
        # atraso a quien la base no se lo muestra.
        "quedan_dias_habiles": (calendario.habiles_entre(ahora, fila["fecha_objetivo"])
                                if vence is not None and vence >= hoy else None),
        "barra": (_barra(calendario, asignada, vence, hoy)
                  if fila["estado"] == "en_curso" and asignada and vence else None),
        "esperas": arboles.get(str(fila["task_id"]), []) if bloqueo is True else None,
    }


def _terminada(fila: dict[str, Any], calendario) -> dict[str, Any]:
    """Una terminada de los últimos 30 días: qué, quién la hizo y cuándo se terminó."""
    terminada = _local(fila["terminada_en"], calendario)
    return {
        "id": str(fila["task_id"]),
        "titulo": fila["titulo"],
        "responsable": fila["responsable"],
        "area": fila["area"],
        "terminada_el": terminada.isoformat() if terminada else None,
    }


def _barra(calendario, desde: date, hasta: date, hoy: date) -> list[dict[str, str]]:
    """Un segmento por día hábil desde que se asignó hasta la entrega (decisión 18): mide el
    tiempo, no el trabajo."""
    segmentos = []
    dia = desde
    while dia <= hasta:
        if calendario.es_habil(dia):
            momento = "pasado" if dia < hoy else "hoy" if dia == hoy else "futuro"
            segmentos.append({"fecha": dia.isoformat(), "momento": momento})
        dia += timedelta(days=1)
    return segmentos


def _semana(calendario, hoy: date, vencen: set[str]) -> list[dict[str, Any]]:
    """La semana de hoy, día por día, con los días de trabajo del espacio (de lunes a viernes en
    CoreWork): hoy marcado, si es feriado y si vence algo ese día."""
    lunes = hoy - timedelta(days=hoy.weekday())
    dias = []
    for i in range(7):
        dia = lunes + timedelta(days=i)
        if dia.weekday() not in calendario.dias:
            continue
        dias.append({"fecha": dia.isoformat(), "dia": DIAS_CORTOS[dia.weekday()],
                     "hoy": dia == hoy, "habil": calendario.es_habil(dia),
                     "vence_algo": dia.isoformat() in vencen})
    return dias


def _arboles(esperas: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Las filas de `esperas_de_la_sesion` como un árbol por tarea trabada: cada paso, qué espera
    y de quién, con los que siguen debajo."""
    arboles: dict[str, list[dict[str, Any]]] = {}
    nodos: dict[tuple[str, str], dict[str, Any]] = {}
    for fila in sorted(esperas, key=lambda f: (str(f["raiz"]), f["nivel"], f["ruta"])):
        raiz = str(fila["raiz"])
        nodo = {"que": fila["que"], "quien": fila["quien"], "esperas": []}
        nodos[(raiz, fila["ruta"])] = nodo
        if fila["padre"] is None:
            arboles.setdefault(raiz, []).append(nodo)
        else:
            nodos[(raiz, fila["padre"])]["esperas"].append(nodo)
    for pasos in arboles.values():
        _ordenar(pasos)
    return arboles


def _ordenar(pasos: list[dict[str, Any]]) -> None:
    """Los pasos de un mismo nivel, por lo que esperan y de quién: siempre en el mismo orden."""
    pasos.sort(key=lambda p: ((p["que"] or "").casefold(), (p["quien"] or "").casefold()))
    for paso in pasos:
        _ordenar(paso["esperas"])


# --- Salir ------------------------------------------------------------------------------------

@router.post("/salir")
def salir(request: Request):
    """Corta la sesión de esta cookie (la persona cerró la sesión) y la borra."""
    if _de_otro_sitio(request):
        return _json({"error": "origen_no_verificado"}, 403)
    token = _token_de_la_cookie(request)
    if token is None:
        return _sin_sesion()

    def cortar(conn) -> Response:
        with sin_espacio(conn) as cur:
            sesion = _sesion(cur, token)
            if sesion is None:
                return _sin_sesion()
            cur.execute("select app_user_id from integrante where membership_id = %s",
                        (sesion["membership_id"],))
            persona = cur.fetchone()
            cur.execute("select cortar_sesion(%s, %s, %s) as cortada",
                        (sesion["sesion_id"], CERRO_LA_SESION,
                         persona["app_user_id"] if persona else None))
        respuesta = Response(status_code=204, headers=CABECERAS_DE_LA_WEB)
        _borrar_la_cookie(respuesta)
        return respuesta

    return _con_la_base(cortar)


# --- La puerta de administración --------------------------------------------------------------
#
# La de un administrador de plataforma (decisiones 10 y 12; porción 2, tarea P2-1, migración
# 0061): abarca todos los espacios, con su propio enlace, su propia sesión y su propia cookie,
# sólo para `/app/admin`. Las dos puertas no se mezclan (constitución §2: el canal define el
# sombrero): la cookie del equipo no abre esta puerta ni la de esta abre la API del equipo, y un
# administrador que además es integrante de un equipo tiene las dos sesiones por separado. El rol
# se revalida en la base en cada pedido: revocado, la sesión queda cortada en el siguiente.

COOKIE_DE_ADMINISTRACION = "leda_admin"
CAMINO_DE_ADMINISTRACION = "/app/admin"


def _sin_sesion_de_administracion() -> JSONResponse:
    """Sin una sesión de administración que entre: 401, y se borra sólo la cookie de esta
    puerta (la del equipo, si la hay, sigue)."""
    respuesta = _json({"error": "sin_sesion"}, 401)
    _borrar_la_cookie_de_administracion(respuesta)
    return respuesta


def _borrar_la_cookie_de_administracion(respuesta: Response) -> None:
    respuesta.delete_cookie(COOKIE_DE_ADMINISTRACION, path=CAMINO_DE_ADMINISTRACION, secure=True,
                            httponly=True, samesite="strict")


def _poner_la_cookie_de_administracion(respuesta: Response, token: str) -> None:
    respuesta.set_cookie(COOKIE_DE_ADMINISTRACION, token, max_age=DURACION_DE_LA_COOKIE_S,
                         path=CAMINO_DE_ADMINISTRACION, secure=True, httponly=True,
                         samesite="strict")


def _token_de_administracion(request: Request) -> str | None:
    token = request.cookies.get(COOKIE_DE_ADMINISTRACION) or ""
    return token if 0 < len(token) <= LARGO_MAXIMO_DEL_TOKEN else None


def _sesion_de_administracion(cur, token: str) -> dict[str, Any] | None:
    """La sesión de administración vigente del token (que revalida el rol de plataforma), o
    `None`."""
    _con_la_version_del_nucleo(cur)
    cur.execute("select * from sesion_de_administracion_vigente(%s)", (_hash(token),))
    return cur.fetchone()


def pagina_del_boton_de_administracion() -> str:
    """La página que muestra el enlace de la administración al abrirlo, igual para cualquier
    enlace."""
    return _pagina("Acá entrás a la administración.", """<p>Este enlace abre la sesión de administración en este teléfono o computadora, una sola vez.</p>
<form method="post"><button type="submit">Entrar</button></form>""")


def _enlace_de_administracion_que_no_sirve() -> HTMLResponse:
    return HTMLResponse(_pagina("Este enlace ya no sirve.", """<p>Cada enlace abre la administración una sola vez, en un solo teléfono o computadora.</p>
<p>Pedí uno nuevo.</p>"""), status_code=404, headers=CABECERAS_DE_UNA_PAGINA)


@router.get("/admin/entrar/{token}")
def ver_el_boton_de_administracion(token: str):
    """Abrir el enlace no lo canjea: muestra el botón "Entrar", sin mirar el token."""
    return HTMLResponse(pagina_del_boton_de_administracion(), headers=CABECERAS_DEL_BOTON)


@router.post("/admin/entrar/{token}")
def entrar_a_la_administracion(token: str, request: Request):
    """El botón: canjea el enlace por una sesión de administración, una sola vez, y lleva a la
    administración con su cookie puesta."""
    if _de_otro_sitio(request):
        return HTMLResponse(_pagina("No se pudo entrar desde acá.", """<p>Abrí el enlace de la administración y apretá "Entrar".</p>"""), status_code=403,
                            headers=CABECERAS_DE_UNA_PAGINA)
    if not 0 < len(token) <= LARGO_MAXIMO_DEL_TOKEN:
        return _enlace_de_administracion_que_no_sirve()
    sesion = secrets.token_urlsafe(32)

    def canjear(conn) -> Response:
        with sin_espacio(conn) as cur:
            _con_la_version_del_nucleo(cur)
            cur.execute("select canjear_enlace_de_administracion(%s, %s) as id",
                        (_hash(token), _hash(sesion)))
            fila = cur.fetchone()
        if fila is None or fila["id"] is None:
            return _enlace_de_administracion_que_no_sirve()
        respuesta = RedirectResponse(f"{CAMINO_DE_ADMINISTRACION}/", status_code=303,
                                     headers=CABECERAS_DE_LA_WEB)
        _poner_la_cookie_de_administracion(respuesta, sesion)
        return respuesta

    return _con_la_base(canjear)


@router.get("/admin/api/yo")
def yo_en_la_administracion(request: Request):
    """Quién es el administrador de la sesión y los espacios que existen (todos: la puerta de
    administración no es de un espacio)."""
    token = _token_de_administracion(request)
    if token is None:
        return _sin_sesion_de_administracion()

    def leer(conn) -> Response:
        with sin_espacio(conn) as cur:
            sesion = _sesion_de_administracion(cur, token)
            if sesion is None:
                return _sin_sesion_de_administracion()
            cur.execute("select id, slug, nombre from workspace order by nombre, slug")
            espacios = cur.fetchall()
        respuesta = _json({
            "administrador": sesion["nombre"],
            "espacios": [{"id": str(e["id"]), "slug": e["slug"], "nombre": e["nombre"]}
                         for e in espacios]})
        _poner_la_cookie_de_administracion(respuesta, token)
        return respuesta

    return _con_la_base(leer)


@router.post("/admin/salir")
def salir_de_la_administracion(request: Request):
    """Corta la sesión de administración de esta cookie (cerró la sesión) y la borra. La del
    equipo, si la hay, sigue."""
    if _de_otro_sitio(request):
        return _json({"error": "origen_no_verificado"}, 403)
    token = _token_de_administracion(request)
    if token is None:
        return _sin_sesion_de_administracion()

    def cortar(conn) -> Response:
        with sin_espacio(conn) as cur:
            if _sesion_de_administracion(cur, token) is None:
                return _sin_sesion_de_administracion()
            cur.execute("select cerrar_sesion_de_administracion(%s) as cerrada", (_hash(token),))
        respuesta = Response(status_code=204, headers=CABECERAS_DE_LA_WEB)
        _borrar_la_cookie_de_administracion(respuesta)
        return respuesta

    return _con_la_base(cortar)


# --- La carga de una tarea --------------------------------------------------------------------
#
# Porción 2, tarea P2-2 (decisiones 9 y 11; migración 0062). Lo decide la base: la sesión y el
# espacio se comprueban en cada llamada, y lo que no se carga vuelve todo junto como datos
# (`campo` y `motivo`). Acá sólo se revisa la forma de lo que llegó y se pone en palabras.

# Lo más grande que se acepta leer de una carga: un formulario de una tarea entra de sobra.
TAMANO_MAXIMO_DE_LA_CARGA = 64 * 1024

# Qué se dice de cada rechazo (422) y de cada aviso que no bloquea (constitución §10: nada técnico).
TEXTOS_DE_LA_CARGA = {
    ("objetivo", "falta"): "Elegí el objetivo al que contribuye la tarea.",
    ("objetivo", "no_existe"): "Ese objetivo no está en este espacio.",
    ("objetivo", "no_esta_abierto"): "Ese objetivo ya no está abierto.",
    ("titulo", "falta"): "Falta el título.",
    ("titulo", "demasiado_largo"): "El título es demasiado largo: hasta 200 caracteres.",
    ("descripcion", "demasiado_largo"):
        "La descripción es demasiado larga: hasta 800 caracteres.",
    ("responsable", "falta"): "Elegí quién la va a hacer.",
    ("responsable", "no_es_integrante_activo"):
        "Esa persona no es integrante activo de este espacio.",
    ("responsable", "la_hace_y_la_revisa"):
        "Nadie aprueba el trabajo de esa persona: la revisaría ella misma.",
    ("responsable", "sin_quien_la_revise"):
        "Nadie activo revisa el trabajo de esa persona: nadie podría aprobar la tarea.",
    ("responsable", "sin_conectar"):
        "Esa persona todavía no tiene Leda conectada: no va a recibir avisos ni seguimiento "
        "hasta que la conecte.",
    ("fecha", "falta"): "Elegí la fecha.",
    ("fecha", "en_el_pasado"): "Esa fecha ya pasó.",
    ("fecha", "no_es_dia_habil"): "Ese día no es hábil en este espacio.",
    ("fecha", "ya_cerro_el_dia"):
        "La jornada de hoy ya terminó en este espacio: elegí otro día.",
    ("fecha", "despues_del_objetivo"): "La fecha es posterior a la del objetivo.",
    ("criterio", "falta"):
        "Falta el criterio de aceptación: qué tiene que pasar para darla por terminada.",
    ("criterio", "demasiado_largo"): "El criterio es demasiado largo: hasta 500 caracteres.",
    # Un criterio que se pueda comprobar (J2-9, J2-13, J2-14 y J2-17; `ayuda_al_cargar.
    # juzgar_el_criterio`): sin evidencia del área, que diga cómo se comprueba; con ella, que diga
    # un resultado. Todo rechazo trae, si se pudo, el criterio que propone Leda.
    ("criterio", "sin_comprobacion"): "No dice cómo se sabe que está terminada.",
    ("criterio", "sin_resultado"): "No dice qué tiene que quedar hecho para darla por terminada.",
    ("criterio", "sin_revisar"):
        "No pude revisar el criterio ahora: la tarea quedó cargada con el criterio como lo "
        "escribiste.",
    ("evidencia", "falta"): "Elegí la evidencia que se pide para darla por terminada.",
    ("evidencia", "sin_politica_del_area"):
        "El área de esa persona todavía no tiene definida qué evidencia se pide.",
    ("evidencia", "tipo_no_es_de_la_politica"):
        "Hay una evidencia que el área no conoce: nadie podría entregarla.",
    ("decidio", "falta"): "Elegí quién decidió la tarea.",
    ("decidio", "no_es_integrante_activo"):
        "Quien la decidió tiene que ser integrante activo de este espacio.",
    # La espera (migración 0067; ADR 0023, decisión 2).
    ("espera", "no_existe"): "La tarea que espera no está en este espacio.",
    ("espera", "esta_cerrada"): "La tarea que espera ya está cerrada: no puede trabar a otra.",
    ("espera", "no_esta_comprometida"):
        "La tarea que espera todavía no está comprometida: no puede trabar a otra.",
    ("espera", "haria_un_ciclo"):
        "Esa espera cerraría un círculo: esa tarea ya espera, directa o indirectamente, a esta.",
    ("clave", "falta"): "No se pudo identificar este envío. Recargá la página y probá de nuevo.",
    ("clave", "usada_con_otros_datos"):
        "Este envío ya cargó otra tarea. Recargá la página para cargar una nueva.",
}
TEXTO_DE_UN_DATO_MAL_FORMADO = "Este dato no es válido."

# Cómo se llama cada dato en el cuerpo del pedido, y el `campo` con que lo nombra la base.
_CAMPOS_ID = {"objetivo": "objetivo_id", "responsable": "responsable_id",
              "decidio": "decidio_id", "espera": "espera_id"}
_CAMPOS_TEXTO = {"titulo": "titulo", "descripcion": "descripcion", "criterio": "criterio",
                 "clave": "clave"}
_FEMENINOS = {"descripcion", "fecha", "evidencia", "clave", "espera"}


def _con_texto(fila: dict[str, Any]) -> dict[str, str]:
    campo, motivo = str(fila.get("campo", "")), str(fila.get("motivo", ""))
    texto = TEXTOS_DE_LA_CARGA.get((campo, motivo))
    if texto is None:
        texto = (TEXTO_DE_UN_DATO_MAL_FORMADO if motivo.startswith("mal_formad")
                 else TEXTOS_DE_LA_CARGA.get(("clave", "falta")))
    return {"campo": campo, "motivo": motivo, "texto": texto}


def _mal_formado(campo: str) -> dict[str, str]:
    return {"campo": campo,
            "motivo": "mal_formada" if campo in _FEMENINOS else "mal_formado"}


def leer_la_carga(cuerpo: Any) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Los datos de una carga como los recibe `cargar_tarea`, y los que llegaron con una forma
    que no sirve (`mal_formado`). Lo que falta lo dice la base, todo junto."""
    cuerpo = cuerpo if isinstance(cuerpo, dict) else {}
    datos: dict[str, Any] = {}
    errores: list[dict[str, str]] = []
    for campo, clave in _CAMPOS_ID.items():
        valor = cuerpo.get(clave)
        datos[campo] = None
        if valor in (None, ""):
            continue
        try:
            datos[campo] = str(uuid.UUID(valor)) if isinstance(valor, str) else None
        except ValueError:
            pass
        if datos[campo] is None:
            errores.append(_mal_formado(campo))
    for campo, clave in _CAMPOS_TEXTO.items():
        valor = cuerpo.get(clave)
        datos[campo] = valor if isinstance(valor, str) else None
        if valor is not None and not isinstance(valor, str):
            errores.append(_mal_formado(campo))
    fecha = cuerpo.get("fecha")
    datos["fecha"] = None
    if fecha not in (None, ""):
        try:
            datos["fecha"] = date.fromisoformat(fecha) if isinstance(fecha, str) else None
        except ValueError:
            pass
        if datos["fecha"] is None:
            errores.append(_mal_formado("fecha"))
    evidencia = cuerpo.get("evidencia")
    datos["evidencia"] = None
    if isinstance(evidencia, list) and all(isinstance(e, str) for e in evidencia):
        datos["evidencia"] = evidencia
    elif evidencia is not None:
        errores.append(_mal_formado("evidencia"))
    return datos, errores


def _espacio_de(espacio_id: str) -> str | None:
    try:
        return str(uuid.UUID(espacio_id))
    except ValueError:
        return None


def _espacio_que_no_existe() -> JSONResponse:
    return _json({"error": "espacio_no_existe"}, 404)


def _sin_lo_que_rechaza_la_base(resultado: dict[str, Any]) -> Response | None:
    """Sin sesión (401, se corta la cookie) o sin espacio (404): la base lo dice así."""
    campos = {e.get("campo") for e in resultado.get("errores") or []}
    if "sesion" in campos:
        return _sin_sesion_de_administracion()
    if "espacio" in campos:
        return _espacio_que_no_existe()
    return None


@router.get("/admin/api/espacios/{espacio_id}/opciones")
def opciones_de_la_carga(espacio_id: str, request: Request):
    """Lo que el formulario necesita para cargar una tarea en un espacio: los objetivos abiertos,
    las tareas que una nueva puede esperar (las comprometidas y abiertas, migración 0067), los
    integrantes activos (con quién revisaría sus tareas y si tienen Leda conectada), la
    evidencia de cada área y los días hábiles."""
    token = _token_de_administracion(request)
    if token is None:
        return _sin_sesion_de_administracion()
    espacio = _espacio_de(espacio_id)

    def leer(conn) -> Response:
        with sin_espacio(conn) as cur:
            if _sesion_de_administracion(cur, token) is None:
                return _sin_sesion_de_administracion()
        if espacio is None:
            return _espacio_que_no_existe()
        ahora = _ahora(conn, espacio)
        with sin_espacio(conn) as cur:
            _con_la_version_del_nucleo(cur)
            cur.execute("select opciones_de_la_carga(%s, %s, %s) as r",
                        (_hash(token), espacio, ahora))
            resultado = cur.fetchone()["r"]
        rechazo = _sin_lo_que_rechaza_la_base(resultado)
        if rechazo is not None:
            return rechazo
        return _json({k: v for k, v in resultado.items() if k != "ok"})

    return _con_la_base(leer)


async def _el_pedido_de_la_carga(request: Request):
    """Los controles de la carga (otro sitio, JSON, la sesión de administración, el tamaño) y sus
    datos: el token, los datos y los mal formados, o la respuesta que corta."""
    if _de_otro_sitio(request):
        return _json({"error": "origen_no_verificado"}, 403)
    tipo = request.headers.get("content-type", "").split(";")[0].strip().lower()
    if tipo != "application/json":
        return _json({"error": "se_espera_json"}, 415)
    token = _token_de_administracion(request)
    if token is None:
        return _sin_sesion_de_administracion()
    crudo = await request.body()
    if len(crudo) > TAMANO_MAXIMO_DE_LA_CARGA:
        return _json({"error": "demasiado_grande"}, 413)
    try:
        cuerpo = json.loads(crudo or b"null")
    except (ValueError, RecursionError):
        # Un cuerpo anidado hasta el fondo no tira `ValueError` sino `RecursionError`: es un
        # pedido mal formado más, nunca un 500 (revisión RDD `review-40c4b218bf40f1fa`).
        cuerpo = None
    datos, mal_formados = leer_la_carga(cuerpo)
    return token, datos, mal_formados


@router.post("/admin/api/espacios/{espacio_id}/tareas")
async def cargar_una_tarea(espacio_id: str, request: Request):
    """Carga una tarea comprometida en un espacio (decisión 9): 201 con su id y los avisos; la
    misma clave con los mismos datos, 200 con la misma tarea; lo que no se carga, 422 con todo
    lo que hay que corregir."""
    pedido = await _el_pedido_de_la_carga(request)
    if isinstance(pedido, Response):
        return pedido
    token, datos, mal_formados = pedido
    espacio = _espacio_de(espacio_id)
    juicio = await _juzgar_el_criterio(token, espacio, datos, mal_formados)
    if isinstance(juicio, Response):
        return juicio
    return await run_in_threadpool(_con_la_base, lambda conn: _cargar(
        conn, token, espacio, datos, mal_formados, juicio))


# --- Revisar antes de la ortografía (J2-21) ---------------------------------------------------
#
# La prueba del usuario (2026-10-13): al confirmar, la web corregía primero la ortografía ("No se"
# por "No sé") y sólo en el segundo "confirmar" la carga rechazaba ese criterio: corregir lo que se
# va a rechazar es trabajo perdido y hace confirmar dos veces. Ahora, antes de la ortografía, la web
# pide revisar la carga: el mismo juicio del criterio y la misma `cargar_tarea`, sin la clave (sin
# ella la base nunca escribe) y sin el rechazo de la clave que falta. Lo que no se cargaría vuelve
# como en la carga (422, con el criterio que propone Leda) y la ortografía no corre; si se cargaría,
# 200 con `{"errores": []}` y nada más (los avisos, como "sin conectar", los da la carga: la base no
# los arma cuando hay un rechazo, y la falta de la clave lo es) y la web sigue con la ortografía. El
# juicio queda un rato para la misma sesión (`_JUICIOS_RECIENTES`), así la carga con los mismos
# textos (o con los mismos corregidos por la ortografía, J2-23) no vuelve a llamar a la IA.

@router.post("/admin/api/espacios/{espacio_id}/tareas/revisar")
async def revisar_una_carga(espacio_id: str, request: Request):
    """Lo que la carga rechazaría, sin cargar nada: 200 con `{"errores": []}` si se cargaría (sin
    avisos: los dice la carga), 422 con todo lo que hay que corregir, como la carga. Nunca deja un
    incidente ni una auditoría: no cargó nada."""
    pedido = await _el_pedido_de_la_carga(request)
    if isinstance(pedido, Response):
        return pedido
    token, datos, mal_formados = pedido
    espacio = _espacio_de(espacio_id)
    juicio = await _juzgar_el_criterio(token, espacio, datos, mal_formados)
    if isinstance(juicio, Response):
        return juicio
    return await run_in_threadpool(_con_la_base, lambda conn: _cargar(
        conn, token, espacio, datos, mal_formados, juicio, solo_revisar=True))


# --- Un criterio que se pueda comprobar (J2-9, J2-13 y J2-14) --------------------------------
#
# Mecánica §13: "¿el resultado esperado es concreto y verificable?". Antes de `cargar_tarea`, el
# criterio escrito (con o sin la ayuda) se juzga (`ayuda_al_cargar.juzgar_el_criterio`) por su
# sentido, sin una lista de palabras (J2-13). J2-14: se toma como el que propone Leda, con la
# evidencia que se eligió en el formulario (en palabras de todos los días, de la política del área
# de quien la hace): con evidencia, basta que diga un resultado, y un rechazo trae el criterio que
# propone Leda (el resultado más esa evidencia); sin evidencia, tiene que decir cómo se comprueba.
# Como en la ayuda, el candado de la web nunca espera a la IA: la sesión, la evidencia y la IA con
# el candado, la llamada sin él y la carga con el candado otra vez (que revalida la sesión). Sin la
# IA no se traba ni se finge: se carga con un aviso y un incidente; lo que se rechaza sin ella se
# rechaza sin propuesta, con su incidente.

def _ia_del_criterio(conn, espacio: str):
    """La IA del espacio para juzgar el criterio, la misma que conversa (`entrada._ia_de`)."""
    from .entrada import _ia_de

    return _ia_de(conn, espacio)


def _opciones_para_el_juicio(conn, token: str, espacio: str) -> dict[str, Any]:
    """Las opciones de la carga de ese espacio (`opciones_de_la_carga`), de donde salen la
    evidencia que pide el área y los otros datos de la tarea."""
    ahora = _ahora(conn, espacio)
    with sin_espacio(conn) as cur:
        _con_la_version_del_nucleo(cur)
        cur.execute("select opciones_de_la_carga(%s, %s, %s) as r",
                    (_hash(token), espacio, ahora))
        return cur.fetchone()["r"] or {}


class OpcionesIlegibles(Exception):
    """Las opciones de la carga no se pudieron leer al juzgar un criterio: no se sabe qué
    evidencia pide el área (advertencia de `review-88b227055a98f635`)."""


def _lo_que_sabe_la_tarea(conn, token: str, espacio: str,
                          datos: dict[str, Any]) -> tuple[list[str], list[str]]:
    """La evidencia que se eligió, en palabras de todos los días (`ayuda_al_cargar.
    evidencia_de_la_carga`), y los otros datos de esta tarea que un criterio propuesto puede
    nombrar (quién la hace y su área, el objetivo, la tarea que espera), de las opciones de la
    carga de ese espacio. Si no se pueden leer, `OpcionesIlegibles`: sin ellas no se sabe qué
    regla le toca al criterio, y no se lo juzga con otra."""
    from . import ayuda_al_cargar

    try:
        opciones = _opciones_para_el_juicio(conn, token, espacio)
    except Exception as falla:  # noqa: BLE001 -- cualquier falla es que no se leyeron
        _sin_transaccion(conn)
        raise OpcionesIlegibles(f"{type(falla).__name__}: {falla}") from falla
    if not opciones.get("ok", True):
        raise OpcionesIlegibles(f"opciones_de_la_carga: {opciones.get('error') or 'ok false'}")
    evidencia = ayuda_al_cargar.evidencia_de_la_carga(opciones, datos.get("responsable"),
                                                       datos.get("evidencia"))
    contexto: list[str] = []
    for lista, clave, valor, campos in (
            ("integrantes", "membership_id", datos.get("responsable"), ("nombre", "area")),
            ("objetivos", "id", datos.get("objetivo"), ("titulo",)),
            ("tareas", "id", datos.get("espera"), ("titulo", "responsable"))):
        fila = next((x for x in opciones.get(lista) or [] if str(x.get(clave)) == valor), None)
        if fila is not None:
            contexto += [str(fila[c]) for c in campos if fila.get(c)]
    return evidencia, contexto


def _lo_del_juicio(conn, token: str, espacio: str, datos: dict[str, Any]):
    """Con el candado: la evidencia y lo demás de la tarea (`_lo_que_sabe_la_tarea`) y la IA del
    espacio, sólo con una sesión de administración vigente (sin ella, `None`: nadie gasta una
    llamada sin entrar). Sin las opciones, el juicio ya está decidido (`juicio`) y no se prepara
    la IA. Una IA que no se puede preparar es una que no responde: la carga no se traba por
    eso."""
    from . import ayuda_al_cargar
    from .motor.recibir import IANoConfigurada

    with sin_espacio(conn) as cur:
        if _sesion_de_administracion(cur, token) is None:
            return None
    vacio = ayuda_al_cargar.sin_nada_que_juzgar(datos.get("titulo") or "", datos["criterio"])
    try:
        evidencia, contexto = _lo_que_sabe_la_tarea(conn, token, espacio, datos)
    except OpcionesIlegibles as falla:
        # Sin saber qué evidencia pide el área no se juzga con la regla de otra (la J2-13 pediría
        # decir cómo se comprueba, que quizás ya lo dice el área): lo vacío o igual al título se
        # rechaza como siempre, sin la IA y sin propuesta; lo demás, sin revisar, con su aviso. En
        # los dos casos, con el incidente de las opciones (`_cargar`).
        return {"juicio": ayuda_al_cargar.Juicio("sin_resultado" if vacio else "sin_revisar",
                                                 falla)}
    # J2-17: lo vacío o igual al título también va a la IA, sin evidencia del área: se rechaza
    # igual, y la IA escribe el criterio que Leda propone ("no sé" es un pedido de ayuda).
    try:
        ia = _ia_del_criterio(conn, espacio)
    except Exception as falla:  # noqa: BLE001 -- queda como `sin_revisar`, con su incidente
        _sin_transaccion(conn)
        ia = IANoConfigurada(f"La IA del espacio no se pudo preparar ({type(falla).__name__}).")
    return {"ia": ia, "evidencia": evidencia, "contexto": contexto}


# J2-21: el juicio de un criterio, por un rato y sólo para la misma sesión de administración, el
# mismo espacio y los mismos datos (lo que revisó `revisar_una_carga`, para la carga que sigue).
# Sólo un juicio de la IA que respondió: uno sin revisar se vuelve a pedir. J2-23: la ortografía
# corrige al confirmar y la carga lleva el texto corregido; lo corregido queda el mismo rato, con el
# texto como se escribió, y el juicio se pide (o se lee) con ese texto: sólo cambió la ortografía,
# palabra por palabra, así que es el mismo criterio y la carga no vuelve a llamar a la IA.

def _reloj() -> float:
    """El reloj de lo que se guarda por un rato: monotónico (un cambio de la hora del equipo no lo
    alarga ni lo corta); las pruebas lo reemplazan para ver el vencimiento."""
    return time.monotonic()


class _PorUnRato:
    """Lo que se guarda por un rato (`dura`) y hasta `maximo` (sale lo más viejo), con su candado.
    Cada clave lleva la sesión y el espacio (`_clave_de`): nada guardado sirve a otra sesión ni a
    otro espacio."""

    def __init__(self, dura: timedelta, maximo: int) -> None:
        self.dura, self.maximo = dura.total_seconds(), maximo
        self._guardado: dict[str, tuple[float, Any]] = {}
        self._candado = threading.Lock()

    def leer(self, clave: str):
        ahora = _reloj()
        with self._candado:
            for vieja in [k for k, (cuando, _) in self._guardado.items()
                          if ahora - cuando >= self.dura]:
                del self._guardado[vieja]
            guardado = self._guardado.get(clave)
        return guardado[1] if guardado else None

    def guardar(self, clave: str, valor: Any) -> None:
        with self._candado:
            # Una clave que ya estaba vuelve a ser la más nueva y no saca a otra.
            self._guardado.pop(clave, None)
            while len(self._guardado) >= self.maximo:
                del self._guardado[next(iter(self._guardado))]
            self._guardado[clave] = (_reloj(), valor)

    def vaciar(self) -> None:
        with self._candado:
            self._guardado.clear()

    def __len__(self) -> int:
        with self._candado:
            return len(self._guardado)


_JUICIOS_RECIENTES = _PorUnRato(timedelta(minutes=10), 256)
_CORREGIDOS_RECIENTES = _PorUnRato(timedelta(minutes=10), 256)


def _clave_de(token: str, espacio: str, *partes: Any) -> str:
    plano = json.dumps([_hash(token), espacio, *partes], ensure_ascii=False, sort_keys=True,
                       default=str)
    return hashlib.sha256(plano.encode("utf-8")).hexdigest()


def _clave_del_juicio(token: str, espacio: str, ia, entrada: dict[str, Any]) -> str:
    return _clave_de(token, espacio, "juicio", getattr(ia, "nombre", None), entrada)


def _guardar_el_juicio(clave: str, juicio) -> None:
    if getattr(juicio, "falla", None) is None:
        _JUICIOS_RECIENTES.guardar(clave, juicio)


def _clave_de_lo_corregido(token: str, espacio: str, campo: str, corregido: str) -> str:
    return _clave_de(token, espacio, "ortografia", campo, corregido)


def _como_se_escribio(token: str, espacio: str, campo: str, texto: str) -> str:
    """El texto como lo escribió la persona si es uno que la ortografía de esta misma sesión y
    este espacio acaba de corregir (J2-23); si no, el mismo."""
    original = _CORREGIDOS_RECIENTES.leer(_clave_de_lo_corregido(token, espacio, campo, texto))
    return original if isinstance(original, str) else texto


async def _juzgar_el_criterio(token: str, espacio: str | None, datos: dict[str, Any],
                              mal_formados: list[dict[str, str]]):
    """El juicio del criterio de una carga, o `None` si no se juzga: con un dato mal formado, sin
    espacio, sin sesión o con un criterio que la base ya rechaza (vacío o largo). Un 503 de la
    base vuelve tal cual. Uno reciente de la misma sesión con los mismos datos (J2-21) no se pide
    otra vez; un texto que la ortografía acaba de corregir se juzga como se escribió (J2-23)."""
    from . import ayuda_al_cargar

    criterio, titulo = datos.get("criterio"), datos.get("titulo") or ""
    if (mal_formados or espacio is None or not isinstance(criterio, str) or not criterio.strip()
            or len(criterio.strip()) > ayuda_al_cargar.LARGOS["criterio"]):
        return None
    preparado = await run_in_threadpool(_con_la_base, lambda conn: _lo_del_juicio(
        conn, token, espacio, datos))
    if preparado is None or isinstance(preparado, Response):
        return preparado
    if "juicio" in preparado:
        return preparado["juicio"]
    entrada = {"titulo": _como_se_escribio(token, espacio, "titulo", titulo),
               "descripcion": _como_se_escribio(token, espacio, "descripcion",
                                                datos.get("descripcion") or ""),
               "criterio": _como_se_escribio(token, espacio, "criterio", criterio),
               "evidencia": list(preparado["evidencia"]),
               "contexto": list(preparado["contexto"])}
    clave = _clave_del_juicio(token, espacio, preparado["ia"], entrada)
    reciente = _JUICIOS_RECIENTES.leer(clave)
    if reciente is not None:
        return reciente
    juicio = await run_in_threadpool(
        ayuda_al_cargar.juzgar_el_criterio, preparado["ia"], **entrada)
    _guardar_el_juicio(clave, juicio)
    return juicio


def _sin_revisar(conn, espacio: str, sesion: dict[str, Any], falla: BaseException | None) -> None:
    """El incidente de una carga cuyo criterio no se pudo revisar (sin el criterio ni el error a
    la vista: la referencia técnica queda para la administración). La tarea ya está cargada: si
    el incidente no se puede guardar, la carga no se deshace ni se contesta como una falla (la
    persona igual ve el aviso) y la consola lo dice."""
    from .incidentes import ETAPA_CRITERIO_AL_CARGAR

    if isinstance(falla, OpcionesIlegibles):
        _sin_las_opciones(conn, espacio, sesion, falla, cargada=True)
        return
    causa = type(falla).__name__ if falla else "sin juicio"
    _imprimir(f"  ! no se pudo revisar el criterio de una carga ({causa}).")
    _dejar_el_incidente(
        conn, espacio, sesion, ETAPA_CRITERIO_AL_CARGAR,
        "La IA del espacio no pudo revisar el criterio de una tarea cargada en la plataforma: la "
        "tarea se cargó con el criterio como se escribió y la persona vio un aviso.",
        f"{type(falla).__name__}: {falla}" if falla else None)


def _dejar_el_incidente(conn, espacio: str, sesion: dict[str, Any], etapa: str, resumen: str,
                        referencia: str | None) -> None:
    """Un incidente de la carga, en el espacio y a nombre de quien cargaba (sin el criterio ni el
    error a la vista). Si no se puede guardar, lo que se le contestó a la persona sigue igual y la
    consola lo dice."""
    from .db import espacio as en_el_espacio
    from .incidentes import registrar_incidente

    try:
        with en_el_espacio(conn, espacio) as cur:
            registrar_incidente(cur, espacio, resumen, severidad="baja",
                                referencia_cruda=referencia, etapa=etapa,
                                app_user_id=str(sesion["app_user_id"]))
    except Exception as otra:  # noqa: BLE001 -- la respuesta a la persona no cambia
        _sin_transaccion(conn)
        _imprimir(f"  ! tampoco se pudo guardar su incidente ({type(otra).__name__}).")


def _sin_las_opciones(conn, espacio: str, sesion: dict[str, Any], falla: OpcionesIlegibles, *,
                      cargada: bool) -> None:
    """El incidente de un criterio que no se juzgó porque las opciones de la carga no se pudieron
    leer (advertencia de `review-88b227055a98f635`): nunca en silencio."""
    from .incidentes import ETAPA_EVIDENCIA_DEL_CRITERIO

    _imprimir("  ! no se pudo leer la evidencia del área para revisar el criterio de una carga.")
    que_paso = ("la tarea se cargó con el criterio como se escribió y la persona vio un aviso."
                if cargada else
                "el criterio estaba vacío o era el título, así que no se cargó; la persona vio "
                "qué falta, sin un criterio propuesto.")
    _dejar_el_incidente(
        conn, espacio, sesion, ETAPA_EVIDENCIA_DEL_CRITERIO,
        "No se pudo leer qué evidencia pide el área para revisar el criterio de una tarea que se "
        f"cargaba en la plataforma, y no se revisó: {que_paso}", str(falla))


def _sin_propuesta(conn, espacio: str, sesion: dict[str, Any], falla: BaseException) -> None:
    """El incidente de un criterio rechazado sin un criterio propuesto (J2-14: la IA no respondió
    o su resultado no pasó los controles). La persona igual ve qué falta; si el incidente no se
    puede guardar, el rechazo sigue y la consola lo dice."""
    from .incidentes import ETAPA_PROPUESTA_DEL_CRITERIO

    if isinstance(falla, OpcionesIlegibles):
        _sin_las_opciones(conn, espacio, sesion, falla, cargada=False)
        return
    _imprimir(f"  ! no se pudo proponer un criterio al rechazar uno ({type(falla).__name__}).")
    _dejar_el_incidente(
        conn, espacio, sesion, ETAPA_PROPUESTA_DEL_CRITERIO,
        "Leda rechazó el criterio de una tarea que se cargaba en la plataforma porque no dice qué "
        "tiene que quedar hecho o cómo se sabe, y no pudo proponer otro: la persona vio qué "
        "falta, sin una propuesta.", f"{type(falla).__name__}: {falla}")


# Los rechazos del criterio que decide el juicio antes de la carga (sin la clave, la base nunca
# escribe).
_CRITERIO_RECHAZADO = {"sin_comprobacion", "sin_resultado"}


def _cargar(conn, token: str, espacio: str | None, datos: dict[str, Any],
            mal_formados: list[dict[str, str]], juicio=None, *,
            solo_revisar: bool = False) -> Response:
    """La carga, o con `solo_revisar` (J2-21) lo que la carga rechazaría: sin la clave (la base
    nunca escribe) y sin el rechazo de la clave que falta; 200 si se cargaría."""
    with sin_espacio(conn) as cur:
        sesion = _sesion_de_administracion(cur, token)
    if sesion is None:
        return _sin_sesion_de_administracion()
    if espacio is None:
        return _espacio_que_no_existe()
    motivo = getattr(juicio, "motivo", None)
    if motivo in _CRITERIO_RECHAZADO:
        # Como un dato mal formado: no se carga nada (sin la clave, la base nunca escribe) y la
        # base igual dice todo lo demás.
        mal_formados = [*mal_formados, {"campo": "criterio", "motivo": motivo}]
    ahora = _ahora(conn, espacio)
    # Con un dato mal formado no se carga nada: la base igual dice todo lo demás, y sin la clave
    # nunca escribe (la falta de la clave es un rechazo más). Al sólo revisar, nunca la clave.
    clave = None if mal_formados or solo_revisar else datos["clave"]
    with sin_espacio(conn) as cur:
        _con_la_version_del_nucleo(cur)
        cur.execute(
            """select cargar_tarea(%s, %s, %s, %s, %s, %s, %s, %s, %s::text[], %s, %s, %s,
                                   %s::uuid) as r""",
            (_hash(token), espacio, datos["objetivo"], datos["titulo"], datos["descripcion"],
             datos["responsable"], datos["fecha"], datos["criterio"], datos["evidencia"],
             datos["decidio"], clave, ahora, datos["espera"]))
        resultado = cur.fetchone()["r"]
    rechazo = _sin_lo_que_rechaza_la_base(resultado)
    if rechazo is not None:
        return rechazo
    if solo_revisar:
        resultado = {**resultado, "errores": [
            e for e in resultado.get("errores") or []
            if (e.get("campo"), e.get("motivo")) != ("clave", "falta")]}
        if not resultado["errores"] and not mal_formados:
            return _json({"errores": []})
    if resultado.get("ok") and not mal_formados:
        avisos = [_con_texto(a) for a in resultado.get("avisos") or []]
        if motivo == "sin_revisar" and not resultado.get("repetida"):
            # Una carga repetida ya tuvo su aviso y su incidente, la primera vez.
            _sin_revisar(conn, espacio, sesion, getattr(juicio, "falla", None))
            avisos.append(_con_texto({"campo": "criterio", "motivo": "sin_revisar"}))
        return _json({"task_id": str(resultado["task_id"]), "avisos": avisos,
                      "repetida": bool(resultado.get("repetida"))},
                     200 if resultado.get("repetida") else 201)
    ya_dichos = {e["campo"] for e in mal_formados}
    errores = list(mal_formados)
    for error in resultado.get("errores") or []:
        if error.get("campo") in ya_dichos:
            continue
        if ((mal_formados or solo_revisar)
                and (error.get("campo"), error.get("motivo")) == ("clave", "falta")
                and (datos["clave"] is not None or solo_revisar)):
            continue
        errores.append(error)
    con_texto = [_con_texto(e) for e in errores]
    if motivo in _CRITERIO_RECHAZADO:
        # J2-14 y J2-17: todo rechazo trae el criterio que propone Leda, escrito por la IA con
        # sus palabras, al lado del campo; sin él, el aviso igual dice qué falta, y la
        # administración se entera.
        propuesta = getattr(juicio, "propuesta", None)
        if propuesta:
            for error in con_texto:
                if (error["campo"], error["motivo"]) == ("criterio", motivo):
                    error["propuesta"] = propuesta
        elif getattr(juicio, "falla", None) is not None:
            _sin_propuesta(conn, espacio, sesion, juicio.falla)
    return _json({"errores": con_texto}, 422)


# --- La ayuda de la IA al cargar --------------------------------------------------------------
#
# Porción J2 de `odd/tasks/plataforma-jerarquias.md` (ADR 0023, punto 4; `ayuda_al_cargar.py`): la
# persona cuenta qué quiere hacer y Leda propone lo que el formulario tiene vacío. Nada se carga:
# la propuesta vuelve al formulario, que la muestra marcada. Tres pasos, para que el candado de la
# web nunca espere a la IA: las opciones con el candado; sin él, la llamada y, si la IA dio una
# manera de comprobarla, su juicio por el sentido (J2-13); y los controles con la auditoría (o el
# incidente) con el candado otra vez, en el espacio y con la sesión revalidada.

TAMANO_MAXIMO_DE_LA_AYUDA = 16 * 1024
TEXTO_SI_LA_IA_FALLA = ("Leda no pudo completar ahora. Lo que escribiste sigue acá: completalo "
                        "vos o probá de nuevo en un rato.")
TEXTOS_DE_LA_AYUDA = {
    ("texto", "falta"): "Contame primero qué querés hacer; con eso Leda completa lo que pueda.",
    ("texto", "demasiado_largo"): "Es demasiado largo para completar: hasta 1000 caracteres.",
    ("ayuda", "nada_que_completar"):
        "No queda nada para completar: el formulario ya tiene todo lo que Leda puede proponer.",
}


def _ia_de_la_ayuda(conn, espacio: str):
    """La IA del espacio, la misma que conversa (`entrada._ia_de`); sin una configurada, la que
    no responde."""
    from .entrada import _ia_de

    return _ia_de(conn, espacio)


def _con_texto_de_la_ayuda(fila: dict[str, Any]) -> dict[str, str]:
    texto = TEXTOS_DE_LA_AYUDA.get((fila["campo"], fila["motivo"]))
    return ({"campo": fila["campo"], "motivo": fila["motivo"], "texto": texto} if texto
            else _con_texto(fila))


def _lo_escrito(cuerpo: dict[str, Any], opciones: dict[str, Any]) -> tuple[
        dict[str, Any], list[dict[str, str]]]:
    """Lo que ya tiene el formulario, revisado contra las opciones del espacio: un id que no
    está ahí (de otro espacio, cerrado o inventado) se rechaza como en la carga."""
    from . import ayuda_al_cargar

    escrito: dict[str, Any] = {}
    errores: list[dict[str, str]] = []
    listas = {"objetivo": ("objetivos", "id", "no_existe"),
              "responsable": ("integrantes", "membership_id", "no_es_integrante_activo"),
              "espera": ("tareas", "id", "no_existe")}
    for campo, clave in _CAMPOS_ID.items():
        if campo == "decidio":
            continue
        valor = cuerpo.get(clave)
        escrito[clave] = ""
        if valor in (None, ""):
            continue
        try:
            valor = str(uuid.UUID(valor)) if isinstance(valor, str) else None
        except ValueError:
            valor = None
        lista, id_, motivo = listas[campo]
        if valor is None:
            errores.append(_mal_formado(campo))
        elif not any(str(x.get(id_)) == valor for x in opciones.get(lista) or []):
            errores.append({"campo": campo, "motivo": motivo})
        else:
            escrito[clave] = valor
    for campo in ("titulo", "descripcion", "criterio"):
        valor = cuerpo.get(campo)
        if valor is not None and not isinstance(valor, str):
            errores.append(_mal_formado(campo))
        escrito[campo] = valor if isinstance(valor, str) else ""
    fecha = cuerpo.get("fecha")
    escrito["fecha"] = ""
    if fecha not in (None, ""):
        try:
            escrito["fecha"] = date.fromisoformat(fecha).isoformat() if isinstance(fecha, str) \
                else ""
        except ValueError:
            pass
        if not escrito["fecha"]:
            errores.append(_mal_formado("fecha"))
    # La evidencia ya tildada (J2-18 y J2-19): lo que la persona eligió es suyo, y Leda no propone
    # otra. Se revisa antes de usarla (advertencia de RDD de la J2-18), como en la carga: cada
    # tipo, de los que conoce el área de quien la hace; sin ella, de los del pack del espacio.
    # Un tipo repetido cuenta una vez. Quién la hace y su área, con la misma búsqueda que usa la
    # propuesta (`ayuda_al_cargar.quien_y_su_politica`; advertencia de RDD de la J2-19): nunca se
    # revisa contra un área y se propone con otra.
    evidencia = cuerpo.get("evidencia")
    escrito["evidencia"] = []
    if isinstance(evidencia, list) and all(isinstance(e, str) for e in evidencia):
        integrante, politica = ayuda_al_cargar.quien_y_su_politica(
            opciones, escrito["responsable_id"] or None)
        conocidos = (ayuda_al_cargar.tipos_que_conoce(politica) if integrante is not None
                     else ayuda_al_cargar.tipos_del_espacio(opciones))
        if evidencia and integrante is not None and politica is None:
            errores.append({"campo": "evidencia", "motivo": "sin_politica_del_area"})
        elif any(e not in conocidos for e in evidencia):
            errores.append({"campo": "evidencia", "motivo": "tipo_no_es_de_la_politica"})
        else:
            escrito["evidencia"] = list(dict.fromkeys(evidencia))
    elif evidencia is not None:
        errores.append(_mal_formado("evidencia"))
    return escrito, errores


@router.post("/admin/api/espacios/{espacio_id}/ayuda")
async def ayudar_a_cargar(espacio_id: str, request: Request):
    """Lo que Leda propone para completar una carga a partir de lo que contó la persona: 200 con
    la propuesta (sólo lo vacío), las personas para elegir y lo que no pudo proponer; 422 sin
    texto, con nada para completar o con un dato que no es del espacio; 503 con un texto humano si
    la IA no respondió (y un incidente)."""
    from . import ayuda_al_cargar

    if _de_otro_sitio(request):
        return _json({"error": "origen_no_verificado"}, 403)
    tipo = request.headers.get("content-type", "").split(";")[0].strip().lower()
    if tipo != "application/json":
        return _json({"error": "se_espera_json"}, 415)
    token = _token_de_administracion(request)
    if token is None:
        return _sin_sesion_de_administracion()
    crudo = await request.body()
    if len(crudo) > TAMANO_MAXIMO_DE_LA_AYUDA:
        return _json({"error": "demasiado_grande"}, 413)
    try:
        cuerpo = json.loads(crudo or b"null")
    except (ValueError, RecursionError):
        cuerpo = None
    cuerpo = cuerpo if isinstance(cuerpo, dict) else {}
    espacio = _espacio_de(espacio_id)
    preparada = await run_in_threadpool(_con_la_base, lambda conn: _preparar_la_ayuda(
        conn, token, espacio, cuerpo))
    if isinstance(preparada, Response):
        return preparada
    crudo_de_la_ia, falla, revisada, juicio = None, None, None, None
    try:
        crudo_de_la_ia = await run_in_threadpool(ayuda_al_cargar.pedir, preparada["ia"],
                                                 preparada["entrada"])
    except Exception as e:  # noqa: BLE001 -- cualquier falla de la IA es que no respondió
        falla = e
    if falla is None:
        # J2-17: lo que decide el código (quién la hace, con su área y su evidencia) con el
        # candado; el juicio del criterio que escribió la IA, ya con esa evidencia, sin él.
        revisada = await run_in_threadpool(_con_la_base, lambda conn: _revisar_la_ayuda(
            conn, token, preparada, crudo_de_la_ia))
        if isinstance(revisada, Response):
            return revisada
        # Nunca levanta: una IA que no juzga es `sin_revisar`.
        juicio = await run_in_threadpool(ayuda_al_cargar.juzgar_la_propuesta, preparada["ia"],
                                         revisada)
    return await run_in_threadpool(_con_la_base, lambda conn: _cerrar_la_ayuda(
        conn, token, preparada, revisada, falla, juicio))


def _preparar_la_ayuda(conn, token: str, espacio: str | None, cuerpo: dict[str, Any]):
    """Con el candado: la sesión, las opciones del espacio, lo escrito y la IA del espacio."""
    from . import ayuda_al_cargar

    with sin_espacio(conn) as cur:
        if _sesion_de_administracion(cur, token) is None:
            return _sin_sesion_de_administracion()
    if espacio is None:
        return _espacio_que_no_existe()
    ahora = _ahora(conn, espacio)
    with sin_espacio(conn) as cur:
        _con_la_version_del_nucleo(cur)
        cur.execute("select opciones_de_la_carga(%s, %s, %s) as r",
                    (_hash(token), espacio, ahora))
        opciones = cur.fetchone()["r"]
    rechazo = _sin_lo_que_rechaza_la_base(opciones)
    if rechazo is not None:
        return rechazo
    texto = cuerpo.get("texto")
    texto = " ".join(texto.split()) if isinstance(texto, str) else ""
    escrito, errores = _lo_escrito(cuerpo, opciones)
    if not texto:
        errores.insert(0, {"campo": "texto", "motivo": "falta"})
    elif len(texto) > ayuda_al_cargar.LARGO_DEL_TEXTO:
        errores.insert(0, {"campo": "texto", "motivo": "demasiado_largo"})
    elif not errores and not ayuda_al_cargar.lo_que_se_pide(escrito, opciones):
        errores.append({"campo": "ayuda", "motivo": "nada_que_completar"})
    if errores:
        return _json({"errores": [_con_texto_de_la_ayuda(e) for e in errores]}, 422)
    return {"espacio": espacio, "texto": texto, "escrito": escrito, "opciones": opciones,
            "ia": _la_ia_o_la_que_no_responde(conn, espacio, _ia_de_la_ayuda),
            "entrada": ayuda_al_cargar.entrada_de_la_ia(texto, escrito, opciones)}


def _la_ia_o_la_que_no_responde(conn, espacio: str, preparar: Callable[[Any, str], Any]):
    """La IA del espacio; si no se puede preparar, una que no responde (`IANoConfigurada`): la
    llamada falla como cualquier IA que no responde, con su aviso y su incidente, nunca un error
    de la web sin rastro (advertencia de RDD de la J2-17)."""
    from .motor.recibir import IANoConfigurada

    try:
        return preparar(conn, espacio)
    except Exception as falla:  # noqa: BLE001 -- queda como una IA que no responde
        _sin_transaccion(conn)
        return IANoConfigurada(
            f"La IA del espacio no se pudo preparar ({type(falla).__name__}: {falla}).")


def _revisar_la_ayuda(conn, token: str, preparada: dict[str, Any], crudo: dict[str, Any] | None):
    """Con el candado y en el espacio, entre la propuesta y el juicio del criterio (J2-17): la
    sesión revalidada y lo que decide el código de la propuesta (`ayuda_al_cargar.revisar`:
    quién la hace, con los apodos del espacio, y con eso la evidencia de su área), para que el
    juicio, fuera del candado, juzgue el criterio con esa evidencia."""
    from . import ayuda_al_cargar
    from .db import espacio as en_el_espacio
    from .motor.fichas import integrantes_que_coinciden

    with sin_espacio(conn) as cur:
        if _sesion_de_administracion(cur, token) is None:
            return _sin_sesion_de_administracion()
    with en_el_espacio(conn, preparada["espacio"]) as cur:
        def objetivo_de(task_id: str) -> str | None:
            cur.execute("select objective_id from task where id = %s", (task_id,))
            fila = cur.fetchone()
            return str(fila["objective_id"]) if fila else None

        return ayuda_al_cargar.revisar(
            crudo or {}, texto=preparada["texto"], escrito=preparada["escrito"],
            opciones=preparada["opciones"],
            coinciden=lambda dicho: integrantes_que_coinciden(cur, dicho),
            objetivo_de=objetivo_de)


def _cerrar_la_ayuda(conn, token: str, preparada: dict[str, Any], resultado,
                     falla: BaseException | None, juicio=None) -> Response:
    """Con el candado otra vez y en el espacio: la sesión revalidada (cortada mientras respondía
    la IA, nada), el criterio que se propone (`cerrar_el_criterio`), la auditoría y, si la IA no
    respondió, el incidente (también si el juicio del criterio no respondió o no dejó uno: la
    propuesta sigue, con el criterio de reserva o diciendo que no se pudo, nunca como si se
    hubiera juzgado)."""
    from . import ayuda_al_cargar, versiones
    from .db import espacio as en_el_espacio, registrar_auditoria
    from .incidentes import ETAPA_AYUDA_AL_CARGAR, registrar_incidente

    with sin_espacio(conn) as cur:
        sesion = _sesion_de_administracion(cur, token)
    if sesion is None:
        return _sin_sesion_de_administracion()
    ws, escrito = preparada["espacio"], preparada["escrito"]
    pide = ayuda_al_cargar.lo_que_se_pide(escrito, preparada["opciones"])
    with en_el_espacio(conn, ws) as cur:
        detalle: dict[str, Any] = {
            "origen": "web", "sesion_de_administracion_id": str(sesion["sesion_id"]),
            "ia": getattr(preparada["ia"], "nombre", None), "pide": pide,
            "respondio": falla is None}
        if falla is None:
            ayuda_al_cargar.cerrar_el_criterio(resultado, juicio)
            propuesta = resultado.propuesta
            if juicio is not None and juicio.falla is not None:
                registrar_incidente(
                    cur, ws,
                    "La IA del espacio no juzgó o no escribió el criterio de aceptación que "
                    "propuso al completar una carga en la plataforma: se propuso el criterio de "
                    "reserva o ninguno, y el campo lo dijo."
                    if juicio.motivo == "sin_revisar" else
                    "Leda no pudo escribir un criterio de aceptación al completar una carga en la "
                    "plataforma (la IA no respondió o lo que escribió no pasó los controles): se "
                    "propuso el de reserva o ninguno, y el campo lo dijo.",
                    severidad="baja",
                    referencia_cruda=f"{type(juicio.falla).__name__}: {juicio.falla}",
                    etapa=ETAPA_AYUDA_AL_CARGAR, app_user_id=str(sesion["app_user_id"]))
            detalle.update({
                "juicio_del_criterio": (None if juicio is None
                                        else juicio.motivo or "sirve"),
                "criterio_de": resultado.criterio_de,
                "propuestos": sorted(propuesta),
                "descartados": resultado.descartados,
                "para_elegir": [e["membership_id"] for e in resultado.elegir],
                "huellas": {c: hashlib.sha256(propuesta[c].encode("utf-8")).hexdigest()
                            for c in ("titulo", "descripcion", "criterio") if c in propuesta},
                "responsable_membership_id": propuesta.get("responsable_id"),
                # J2-18: si quién la hace lo nombró la persona o lo propuso Leda, y la evidencia
                # que Leda sumó al mínimo del área.
                "responsable_de": resultado.responsable_de,
                "evidencia_propuesta": propuesta.get("evidencia") or [],
                "espera_task_id": propuesta.get("espera_id"),
                "objective_id": propuesta.get("objetivo_id"),
                "fecha": propuesta.get("fecha")})
        else:
            registrar_incidente(
                cur, ws,
                "La IA del espacio no respondió cuando un administrador pidió completar una "
                "carga en la plataforma: no se propuso ni se cargó nada y la persona vio un "
                "aviso.",
                severidad="baja", referencia_cruda=f"{type(falla).__name__}: {falla}",
                etapa=ETAPA_AYUDA_AL_CARGAR, app_user_id=str(sesion["app_user_id"]))
        registrar_auditoria(
            cur, accion="proponer_al_cargar", workspace_id=ws,
            actor_app_user_id=str(sesion["app_user_id"]), actor_kind="persona",
            sujeto_tipo="workspace", sujeto_id=ws, detalle=detalle,
            pack_hash=versiones.pack_hash(cur, ws), nucleo_hash=versiones.nucleo_hash())
    if falla is not None:
        _imprimir(f"  ! la IA no respondió a una ayuda para cargar ({type(falla).__name__}).")
        return _json({"error": "sin_ayuda", "texto": TEXTO_SI_LA_IA_FALLA}, 503)
    return _json({"propuesta": resultado.propuesta, "elegir": resultado.elegir,
                  "avisos": resultado.avisos})


# --- La ortografía, al confirmar (J2-17 y J2-23) ---------------------------------------------------
#
# El usuario (2026-10-13): Leda corrige la ortografía de lo que la persona escribió a mano y pone
# los nombres como están en los datos del equipo, sin cambiar cómo está redactado. J2-23 ("que lo
# corrija directamente sin resaltarlo, ya dijimos que corrige palabras puntuales, no lo que dice la
# persona"): la web llama acá al tocar "confirmar", después de revisar la carga (J2-21: lo que se
# va a rechazar nunca se corrige) y con los textos que todavía no se revisaron tal como están, y
# carga en el mismo toque lo corregido, sin marcas ni otra confirmación. Lo corregido queda un rato
# para esta sesión (`_CORREGIDOS_RECIENTES`), así la carga juzga el criterio como se escribió y usa
# el juicio de la revisión. Los mismos tres pasos que la ayuda, para que el candado nunca espere a
# la IA. La
# cocina acepta, palabra por palabra, sólo la que es la misma palabra mal escrita
# (`ayuda_al_cargar.palabra_por_palabra`, J2-18); la que no, queda como se escribió, con un
# incidente que cuenta cuántas. Si la IA no responde (o no se puede preparar), nada se bloquea: el
# texto queda como se escribió, con un aviso y un incidente.

TEXTO_SIN_ORTOGRAFIA = "No pude revisar la ortografía ahora: quedó como lo escribiste."


def _ia_de_la_ortografia(conn, espacio: str):
    """La IA del espacio, la misma que conversa (`entrada._ia_de`)."""
    from .entrada import _ia_de

    return _ia_de(conn, espacio)


@router.post("/admin/api/espacios/{espacio_id}/ortografia")
async def revisar_la_ortografia(espacio_id: str, request: Request):
    """La ortografía de los textos de una carga (título, descripción y criterio): 200 con lo que
    se corrigió (`corregidos`: por campo, el texto y sus cambios) y lo que no se pudo revisar
    (`sin_revisar`, con un `aviso` humano y un incidente); 422 con un dato que no es un texto."""
    from . import ayuda_al_cargar

    if _de_otro_sitio(request):
        return _json({"error": "origen_no_verificado"}, 403)
    tipo = request.headers.get("content-type", "").split(";")[0].strip().lower()
    if tipo != "application/json":
        return _json({"error": "se_espera_json"}, 415)
    token = _token_de_administracion(request)
    if token is None:
        return _sin_sesion_de_administracion()
    crudo = await request.body()
    if len(crudo) > TAMANO_MAXIMO_DE_LA_AYUDA:
        return _json({"error": "demasiado_grande"}, 413)
    try:
        cuerpo = json.loads(crudo or b"null")
    except (ValueError, RecursionError):
        cuerpo = None
    cuerpo = cuerpo if isinstance(cuerpo, dict) else {}
    errores = [_mal_formado(c) for c in ayuda_al_cargar.CAMPOS_DE_TEXTO
               if cuerpo.get(c) is not None and not isinstance(cuerpo.get(c), str)]
    textos = {c: cuerpo[c] for c in ayuda_al_cargar.CAMPOS_DE_TEXTO
              if isinstance(cuerpo.get(c), str) and cuerpo[c].strip()}
    espacio = _espacio_de(espacio_id)
    preparada = await run_in_threadpool(_con_la_base, lambda conn: _preparar_la_ortografia(
        conn, token, espacio, textos, errores))
    if isinstance(preparada, Response):
        return preparada
    crudo_de_la_ia, falla = None, None
    try:
        crudo_de_la_ia = await run_in_threadpool(ayuda_al_cargar.pedir_la_ortografia,
                                                 preparada["ia"], preparada["entrada"])
    except Exception as e:  # noqa: BLE001 -- cualquier falla de la IA es que no respondió
        falla = e
    return await run_in_threadpool(_con_la_base, lambda conn: _cerrar_la_ortografia(
        conn, token, preparada, crudo_de_la_ia, falla))


def _preparar_la_ortografia(conn, token: str, espacio: str | None, textos: dict[str, str],
                            errores: list[dict[str, str]]):
    """Con el candado: la sesión, las opciones del espacio (de donde salen los nombres del
    equipo) y la IA del espacio. Sin textos, nada que revisar: no se llama a la IA."""
    from . import ayuda_al_cargar

    with sin_espacio(conn) as cur:
        if _sesion_de_administracion(cur, token) is None:
            return _sin_sesion_de_administracion()
    if espacio is None:
        return _espacio_que_no_existe()
    ahora = _ahora(conn, espacio)
    with sin_espacio(conn) as cur:
        _con_la_version_del_nucleo(cur)
        cur.execute("select opciones_de_la_carga(%s, %s, %s) as r",
                    (_hash(token), espacio, ahora))
        opciones = cur.fetchone()["r"]
    rechazo = _sin_lo_que_rechaza_la_base(opciones)
    if rechazo is not None:
        return rechazo
    if errores:
        return _json({"errores": [_con_texto(e) for e in errores]}, 422)
    if not textos:
        return _json({"corregidos": {}, "sin_revisar": []})
    return {"espacio": espacio, "textos": textos, "opciones": opciones,
            "ia": _la_ia_o_la_que_no_responde(conn, espacio, _ia_de_la_ortografia),
            "entrada": ayuda_al_cargar.entrada_de_la_ortografia(textos, opciones)}


def _cerrar_la_ortografia(conn, token: str, preparada: dict[str, Any],
                          crudo: dict[str, Any] | None, falla: BaseException | None) -> Response:
    """Con el candado otra vez y en el espacio: la sesión revalidada, el control del código, la
    auditoría (con la huella de cada texto corregido, nunca el texto) y, si algo no se pudo
    revisar, el incidente (sin los textos)."""
    from . import ayuda_al_cargar, versiones
    from .db import espacio as en_el_espacio, registrar_auditoria
    from .incidentes import ETAPA_ORTOGRAFIA_AL_CARGAR, registrar_incidente

    with sin_espacio(conn) as cur:
        sesion = _sesion_de_administracion(cur, token)
    if sesion is None:
        return _sin_sesion_de_administracion()
    ws, textos = preparada["espacio"], preparada["textos"]
    palabras: list[dict[str, Any]] = []
    if falla is None:
        revisada = ayuda_al_cargar.revisar_la_ortografia(crudo or {}, textos,
                                                         preparada["opciones"])
        corregidos, rechazados = revisada.corregidos, revisada.rechazados
        palabras = revisada.palabras_rechazadas
        sin_revisar = [r["campo"] for r in rechazados]
        # Sin los textos ni las palabras: cuántas de cada campo (J2-18).
        referencia = "; ".join(
            [*(f"{r['campo']}: {r['motivo']}" for r in rechazados),
             *(f"{p['campo']}: {p['cantidad']} "
               f"{'palabra no aceptada' if p['cantidad'] == 1 else 'palabras no aceptadas'}"
               for p in palabras)]) or None
    else:
        corregidos, rechazados = {}, []
        sin_revisar = list(textos)
        referencia = f"{type(falla).__name__}: {falla}"
    with en_el_espacio(conn, ws) as cur:
        if sin_revisar or palabras:
            registrar_incidente(
                cur, ws,
                ("La IA del espacio no respondió al revisar la ortografía de una carga en la "
                 "plataforma: los textos quedaron como se escribieron y la persona vio un aviso."
                 if falla is not None else
                 "Leda no aceptó la corrección de ortografía de una carga en la plataforma (no "
                 "volvió, cambiaba algo más que la ortografía o cambiaba una palabra por otra): "
                 "lo que no aceptó quedó como se escribió" +
                 (" y la persona vio un aviso." if sin_revisar else
                  "; lo demás se corrigió.")),
                severidad="baja", referencia_cruda=referencia,
                etapa=ETAPA_ORTOGRAFIA_AL_CARGAR, app_user_id=str(sesion["app_user_id"]))
        registrar_auditoria(
            cur, accion="corregir_al_cargar", workspace_id=ws,
            actor_app_user_id=str(sesion["app_user_id"]), actor_kind="persona",
            sujeto_tipo="workspace", sujeto_id=ws,
            detalle={"origen": "web", "sesion_de_administracion_id": str(sesion["sesion_id"]),
                     "ia": getattr(preparada["ia"], "nombre", None), "pide": list(textos),
                     "respondio": falla is None, "corregidos": list(corregidos),
                     "rechazados": rechazados, "sin_revisar": sin_revisar,
                     "palabras_rechazadas": palabras,
                     "huellas": {c: hashlib.sha256(v["texto"].encode("utf-8")).hexdigest()
                                 for c, v in corregidos.items()}},
            pack_hash=versiones.pack_hash(cur, ws), nucleo_hash=versiones.nucleo_hash())
    # J2-23: la carga que sigue juzga el criterio como se escribió (`_como_se_escribio`).
    for campo, corregido in corregidos.items():
        _CORREGIDOS_RECIENTES.guardar(
            _clave_de_lo_corregido(token, ws, campo, corregido["texto"]), textos[campo])
    if sin_revisar:
        causa = type(falla).__name__ if falla is not None else "corrección rechazada"
        _imprimir(f"  ! no se pudo revisar la ortografía de una carga ({causa}).")
        return _json({"corregidos": corregidos, "sin_revisar": sin_revisar,
                      "aviso": TEXTO_SIN_ORTOGRAFIA})
    return _json({"corregidos": corregidos, "sin_revisar": []})


# --- La web -----------------------------------------------------------------------------------

def _no_existe() -> HTMLResponse:
    return HTMLResponse(_pagina("Esta página no existe.", """<p><a href="/app/">Volver a tus tareas</a>.</p>"""), status_code=404,
                        headers=CABECERAS_DE_UNA_PAGINA)


def _archivo_de_la_web(carpeta: Path, ruta: str) -> Path | None:
    """El archivo de la web compilada en esa ruta, o `None`: nunca uno fuera de la carpeta."""
    try:
        base = carpeta.resolve()
        destino = (base / ruta).resolve()
    except (OSError, ValueError):
        return None
    if base not in destino.parents or not destino.is_file():
        return None
    return destino


@router.get("", include_in_schema=False)
def a_la_web():
    return RedirectResponse("/app/", status_code=308, headers=CABECERAS_DE_LA_WEB)


# Va última: las rutas de arriba (la API, entrar y salir) se miran antes.
@router.get("/{ruta:path}", include_in_schema=False)
def la_web(ruta: str):
    """La web compilada: un archivo de `assets/`, o `index.html` para cualquier página."""
    partes = ruta.split("/")
    # Las páginas de `/app/admin/` son de la web (la administración, porción 2); su API, su
    # enlace y salir, igual que los del equipo, nunca caen en el índice.
    primera = partes[1] if partes[0] == "admin" and len(partes) > 1 else partes[0]
    if primera == "api":
        return _json({"error": "no_existe"}, 404)
    if primera in ("entrar", "salir"):
        return _no_existe()
    indice = CARPETA_DE_LA_WEB / "index.html"
    if not indice.is_file():
        _imprimir("  ! falta compilar la web de la plataforma (npm run build, en web/).")
        return HTMLResponse(_pagina("La página todavía no está lista.", """<p>Probá de nuevo más tarde.</p>"""), status_code=503, headers=CABECERAS_DE_UNA_PAGINA)
    if ruta:
        archivo = _archivo_de_la_web(CARPETA_DE_LA_WEB, ruta)
        if archivo is not None and archivo.name != "index.html":
            cabeceras = dict(CABECERAS_DE_LA_WEB)
            if ruta.startswith("assets/"):
                cabeceras["Cache-Control"] = GUARDAR_UN_ANIO
            return FileResponse(archivo, headers=cabeceras, media_type=TIPOS_DE_LA_WEB.get(
                archivo.suffix.lower(), "application/octet-stream"))
        # Lo que parece un archivo y no está no es una página: nunca el índice en su lugar.
        if "." in ruta.rsplit("/", 1)[-1] or ruta.startswith("assets/"):
            return _no_existe()
    return HTMLResponse(indice.read_text(encoding="utf-8"), headers=CABECERAS_DE_LA_WEB)


# --- La consola -------------------------------------------------------------------------------

def emitir_enlace(cur, membership_id: str) -> str | None:
    """Emite el enlace de entrada de una persona del espacio de la transacción (corre como
    `leda_app`, dentro de `espacio()`) y devuelve el token en claro, o `None` si no es un
    integrante activo de ese espacio. El anterior sin usar queda anulado."""
    token = secrets.token_urlsafe(32)
    _con_la_version_del_nucleo(cur)
    cur.execute("select emitir_enlace_de_entrada(%s, %s, null) as id",
                (str(membership_id), _hash(token)))
    fila = cur.fetchone()
    return token if fila and fila["id"] is not None else None


def cortar_sesiones(cur, membership_id: str, *, motivo: str = POR_UN_ADMINISTRADOR,
                    actor_app_user_id: str | None = None) -> int:
    """Corta todas las sesiones abiertas de una persona del espacio de la transacción, y su
    enlace sin usar. Devuelve cuántas sesiones cortó. Por omisión, un administrador desde la
    consola (actor nulo: lo hace Leda por su pedido); por chat, la persona que avisa que perdió
    el celular (`PERDIO_EL_CELULAR`, con su usuario como actor). El corte queda siempre en la
    auditoría, también sin sesiones (0066)."""
    _con_la_version_del_nucleo(cur)
    cur.execute("select cortar_sesiones_de_membresia(%s, %s, %s) as cortadas",
                (str(membership_id), motivo,
                 str(actor_app_user_id) if actor_app_user_id else None))
    cortadas = int(cur.fetchone()["cortadas"])
    _anular_los_enlaces_sin_salir(cur, membership_id)
    return cortadas


# El incidente de un mensaje con el enlace de entrada que no salió porque el acceso se cortó antes
# (la etapa es la del despachador, `despachador.ETAPA_ENLACE_DE_ENTRADA_WEB`).
ETAPA_ENLACE_DE_ENTRADA_WEB = "enlace_de_entrada_web"


def _anular_los_enlaces_sin_salir(cur, membership_id: str) -> None:
    """Con el corte, los mensajes de la persona que llevan su enlace de entrada y todavía no
    salieron (`message_outbox_entrada_web`, esperando su turno o su reintento) se descartan: el
    despachador lo emitiría después del corte, al Telegram que puede estar en el celular perdido
    (advertencia de la revisión de la A-3). El mensaje entero, no sólo el enlace: decía que lo
    llevaba, y `leda_app` no borra la marca. Nunca en silencio: cada uno deja su incidente, sin
    avisar a la administración, porque la respuesta del corte ya le dice a la persona que pida
    otro enlace. Si era el ofrecimiento, se libera, como un envío que falla sin reintento."""
    from .incidentes import registrar_incidente

    cur.execute(
        """update message_outbox o set estado = 'descartado'
             from message_outbox_entrada_web w
            where w.outbox_id = o.id and w.membership_id = %s
              and o.estado in ('pendiente', 'esperando_confirmacion', 'listo')
        returning o.id, o.workspace_id, w.es_ofrecimiento""", (str(membership_id),))
    anulados = cur.fetchall()
    for fila in anulados:
        registrar_incidente(
            cur, str(fila["workspace_id"]),
            "Un mensaje con el enlace de entrada a la web no salió: el acceso de la persona se "
            "cortó antes de mandarlo.",
            severidad="baja", etapa=ETAPA_ENLACE_DE_ENTRADA_WEB,
            referencia_tipo="message_outbox", referencia_id=str(fila["id"]), avisar_admin=False,
            sin_avisar_porque="la respuesta del corte le dice a la persona que pida otro enlace")
    if any(fila["es_ofrecimiento"] for fila in anulados):
        liberar_el_ofrecimiento(cur, membership_id)


def entro_alguna_vez(cur, membership_id: str) -> bool:
    """Si la persona entró alguna vez a la web (canjeó un enlace), en el espacio de la
    transacción: `leda_app` no lee los enlaces ni las sesiones (0066)."""
    cur.execute("select entro_a_la_web(%s) as si", (str(membership_id),))
    return bool(cur.fetchone()["si"])


def entro_alguna_vez_como_administracion(cur, membership_id: str) -> bool:
    """Lo mismo que `entro_alguna_vez` (la definición de `entro_a_la_web`, 0066), con la conexión
    administrativa (`admin()`, `leda_admin`, que lee las dos tablas y no ejecuta la función): la
    bienvenida se escribe desde ahí (`motor.recibir._activar`)."""
    cur.execute("""select exists (select 1 from enlace_de_entrada e
                                   where e.membership_id = %(m)s and e.canjeado_en is not null)
                       or exists (select 1 from sesion_web s where s.membership_id = %(m)s)
                       as si""", {"m": str(membership_id)})
    return bool(cur.fetchone()["si"])


# --- El ofrecimiento, una sola vez (decisión 2 del usuario, 2026-10-12; `ofrecimiento_web`) -----
#
# Se reserva al armar la respuesta que lo lleva (decisión técnica 1: así no salen dos antes de que
# salga el primero), queda ofrecido al mandar y se libera si el envío falla sin reintento.

def tiene_un_enlace_por_salir(cur, membership_id: str) -> bool:
    """Si un mensaje a la persona con su enlace de entrada todavía no salió (esperando su turno o
    su reintento): mientras tanto no se le ofrece otro, que lo anularía."""
    cur.execute("""select exists (select 1 from message_outbox_entrada_web w
                                    join message_outbox o on o.id = w.outbox_id
                                   where w.membership_id = %s
                                     and o.estado in ('pendiente', 'esperando_confirmacion',
                                                      'listo')) as si""",
                (str(membership_id),))
    return bool(cur.fetchone()["si"])


def ya_se_le_ofrecio(cur, membership_id: str) -> bool:
    """Si a la persona ya se le ofreció la web, o está reservado para un mensaje que va a salir."""
    cur.execute("select exists (select 1 from ofrecimiento_web where membership_id = %s) as si",
                (str(membership_id),))
    return bool(cur.fetchone()["si"])


def reservar_el_ofrecimiento(cur, membership_id: str) -> bool:
    """Reserva el ofrecimiento de la web para la persona; `True` sólo si lo reservó esta llamada
    (nunca se le había ofrecido ni estaba reservado). En la transacción que encola el mensaje que
    lo lleva: si se deshace, la reserva también."""
    cur.execute("""insert into ofrecimiento_web (workspace_id, membership_id)
                   select m.workspace_id, m.id from membership m where m.id = %s
                   on conflict (membership_id) do nothing
                   returning true as si""", (str(membership_id),))
    return cur.fetchone() is not None


def quedo_ofrecido(cur, membership_id: str, ahora) -> None:
    """La persona recibió su enlace de entrada (el ofrecimiento, o uno que pidió): ya no se le
    ofrece. Dentro del punto de retorno del envío: si el envío falla, no cuenta."""
    cur.execute("""insert into ofrecimiento_web (workspace_id, membership_id, reservado_en,
                                                 ofrecido_en)
                   select m.workspace_id, m.id, %(ahora)s, %(ahora)s
                     from membership m where m.id = %(m)s
                   on conflict (membership_id) do update
                     set ofrecido_en = coalesce(ofrecimiento_web.ofrecido_en,
                                                excluded.ofrecido_en)""",
                {"m": str(membership_id), "ahora": ahora})


def liberar_el_ofrecimiento(cur, membership_id: str) -> None:
    """El ofrecimiento reservado que no salió (el envío falló sin reintento, o el corte lo
    anuló) se libera: se le vuelve a ofrecer más adelante. Uno que ya salió no se toca."""
    cur.execute("""delete from ofrecimiento_web
                    where membership_id = %s and ofrecido_en is null""", (str(membership_id),))


def tiene_un_enlace_sin_usar(cur, membership_id: str) -> bool:
    """Si la persona tiene un enlace de entrada emitido que nadie usó ni se anuló (vencido o no):
    el que un enlace nuevo deja sin servir (0066)."""
    cur.execute("select tiene_un_enlace_sin_usar(%s) as si", (str(membership_id),))
    return bool(cur.fetchone()["si"])


def enlace(base_url: str, token: str) -> str:
    """La dirección del enlace de entrada, sobre la dirección pública configurada."""
    return f"{base_url.rstrip('/')}{CAMINO_DE_ENTRADA}{token}"


def emitir_enlace_de_administracion(cur, app_user_id: str) -> str | None:
    """Emite el enlace de un solo uso de un administrador de plataforma a la puerta de
    administración (corre como `leda_admin`, dentro de `admin()`: la función sólo la ejecuta la
    consola) y devuelve el token en claro, o `None` si no tiene hoy el rol. El anterior sin usar
    queda anulado."""
    token = secrets.token_urlsafe(32)
    _con_la_version_del_nucleo(cur)
    cur.execute("select emitir_enlace_de_administracion(%s, %s, null) as id",
                (str(app_user_id), _hash(token)))
    fila = cur.fetchone()
    return token if fila and fila["id"] is not None else None


def cortar_sesiones_de_administrador(cur, app_user_id: str) -> int:
    """Corta todas las sesiones de administración abiertas de un administrador, y su enlace sin
    usar, por la consola (`leda_admin`). Devuelve cuántas sesiones cortó."""
    _con_la_version_del_nucleo(cur)
    cur.execute("select cortar_sesiones_de_administrador(%s, %s, null) as cortadas",
                (str(app_user_id), POR_UN_ADMINISTRADOR))
    return int(cur.fetchone()["cortadas"])


def enlace_de_administracion(base_url: str, token: str) -> str:
    """La dirección del enlace de la puerta de administración, sobre la dirección pública."""
    return f"{base_url.rstrip('/')}{CAMINO_DE_ADMINISTRACION}/entrar/{token}"
