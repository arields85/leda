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
    ("evidencia", "falta"): "Elegí la evidencia que se pide para darla por terminada.",
    ("evidencia", "sin_politica_del_area"):
        "El área de esa persona todavía no tiene definida qué evidencia se pide.",
    ("evidencia", "tipo_no_es_de_la_politica"):
        "Hay una evidencia que el área no conoce: nadie podría entregarla.",
    ("decidio", "falta"): "Elegí quién decidió la tarea.",
    ("decidio", "no_es_integrante_activo"):
        "Quien la decidió tiene que ser integrante activo de este espacio.",
    ("clave", "falta"): "No se pudo identificar este envío. Recargá la página y probá de nuevo.",
    ("clave", "usada_con_otros_datos"):
        "Este envío ya cargó otra tarea. Recargá la página para cargar una nueva.",
}
TEXTO_DE_UN_DATO_MAL_FORMADO = "Este dato no es válido."

# Cómo se llama cada dato en el cuerpo del pedido, y el `campo` con que lo nombra la base.
_CAMPOS_ID = {"objetivo": "objetivo_id", "responsable": "responsable_id",
              "decidio": "decidio_id"}
_CAMPOS_TEXTO = {"titulo": "titulo", "descripcion": "descripcion", "criterio": "criterio",
                 "clave": "clave"}
_FEMENINOS = {"descripcion", "fecha", "evidencia", "clave"}


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
    los integrantes activos (con quién revisaría sus tareas y si tienen Leda conectada), la
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


@router.post("/admin/api/espacios/{espacio_id}/tareas")
async def cargar_una_tarea(espacio_id: str, request: Request):
    """Carga una tarea comprometida en un espacio (decisión 9): 201 con su id y los avisos; la
    misma clave con los mismos datos, 200 con la misma tarea; lo que no se carga, 422 con todo
    lo que hay que corregir."""
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
    espacio = _espacio_de(espacio_id)
    return await run_in_threadpool(_con_la_base, lambda conn: _cargar(
        conn, token, espacio, datos, mal_formados))


def _cargar(conn, token: str, espacio: str | None, datos: dict[str, Any],
            mal_formados: list[dict[str, str]]) -> Response:
    with sin_espacio(conn) as cur:
        if _sesion_de_administracion(cur, token) is None:
            return _sin_sesion_de_administracion()
    if espacio is None:
        return _espacio_que_no_existe()
    ahora = _ahora(conn, espacio)
    # Con un dato mal formado no se carga nada: la base igual dice todo lo demás, y sin la clave
    # nunca escribe (la falta de la clave es un rechazo más).
    clave = None if mal_formados else datos["clave"]
    with sin_espacio(conn) as cur:
        _con_la_version_del_nucleo(cur)
        cur.execute(
            """select cargar_tarea(%s, %s, %s, %s, %s, %s, %s, %s, %s::text[], %s, %s, %s)
                      as r""",
            (_hash(token), espacio, datos["objetivo"], datos["titulo"], datos["descripcion"],
             datos["responsable"], datos["fecha"], datos["criterio"], datos["evidencia"],
             datos["decidio"], clave, ahora))
        resultado = cur.fetchone()["r"]
    rechazo = _sin_lo_que_rechaza_la_base(resultado)
    if rechazo is not None:
        return rechazo
    if resultado.get("ok") and not mal_formados:
        return _json({"task_id": str(resultado["task_id"]),
                      "avisos": [_con_texto(a) for a in resultado.get("avisos") or []],
                      "repetida": bool(resultado.get("repetida"))},
                     200 if resultado.get("repetida") else 201)
    ya_dichos = {e["campo"] for e in mal_formados}
    errores = list(mal_formados)
    for error in resultado.get("errores") or []:
        if error.get("campo") in ya_dichos:
            continue
        if (mal_formados and (error.get("campo"), error.get("motivo")) == ("clave", "falta")
                and datos["clave"] is not None):
            continue
        errores.append(error)
    return _json({"errores": [_con_texto(e) for e in errores]}, 422)


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
