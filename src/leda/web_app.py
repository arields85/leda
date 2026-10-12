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
- `GET /app/api/yo`: quién es la persona de la sesión, de qué espacio y qué vistas tiene.
- `GET /app/api/tareas?vista=tus|sector|equipo`: lo que muestra cada vista (decisión 18): el panel
  con un número por estado, la semana del calendario del espacio, y cada tarea con su estado, su
  fecha, los días hábiles que quedan, la barra de días hábiles de una tarea en curso y, si es una
  tarea trabada cuyo bloqueo ve la persona, la cadena de esperas en árbol.
- `POST /app/salir`: corta la sesión (`cerro_la_sesion`) y borra la cookie.
- `GET /app/` y las demás páginas bajo `/app` (tarea P1-4): la web compilada de `web/dist`
  (React, decisión 17), del mismo origen que la API. `index.html` no se guarda; los archivos con
  huella de `assets/` se guardan un año. Sin compilar, la persona ve un mensaje humano.

**Nada del pedido elige a la persona ni al espacio** (decisión 11): salen del hash del token de la
cookie, por las funciones de la base (`sesion_vigente`, `vistas_de_la_sesion`,
`tareas_de_la_sesion` y `esperas_de_la_sesion`, migraciones 0057 a 0059), que revalidan la
membresía en cada pedido y deciden quién ve qué (decisión 13). El atraso y el bloqueo de una tarea
llegan nulos para quien no puede verlos y quedan nulos: este módulo nunca los calcula.

**Los tokens** (el del enlace y el de la sesión) nunca se guardan en claro, nunca se imprimen y
nunca vuelven en una respuesta, salvo el de la sesión en su propia cookie. La sesión no vence
(decisión 4): la cookie dura lo más que un navegador acepta y se renueva al pedir `/app/api/yo`;
la que vale es la de la base, que se corta sólo por un administrador, por la persona o porque dejó
el equipo.
"""

from __future__ import annotations

import hashlib
import secrets
import threading
from collections.abc import Callable
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from fastapi import APIRouter, Request
from fastapi.responses import (FileResponse, HTMLResponse, JSONResponse, RedirectResponse,
                               Response)

from .calendario import Calendario
from .db import conectar, sin_espacio

router = APIRouter(prefix="/app")

# La cookie de la sesión de la puerta del equipo (decisión 12: cada puerta tendrá la suya).
COOKIE = "leda_sesion"
# La sesión no vence; la cookie, lo más que aceptan los navegadores (400 días): se renueva sola
# cada vez que la web pregunta quién es la persona.
DURACION_DE_LA_COOKIE_S = 400 * 24 * 60 * 60
# Lo más largo que puede ser un token que se acepta mirar (`secrets.token_urlsafe(32)`: 43).
LARGO_MAXIMO_DEL_TOKEN = 128

# Cómo se corta una sesión desde la web y desde la consola (motivos de la 0057).
CERRO_LA_SESION = "cerro_la_sesion"
POR_UN_ADMINISTRADOR = "administrador"

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

# Los cuatro estados con color de la decisión 18, en el orden en que una tarea toma uno solo.
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
        if vistas is None:
            return _sin_sesion()
        respuesta = _json({
            "persona": persona["nombre"] if persona else "",
            "espacio": espacio["nombre"] if espacio else "",
            "vistas": [{"vista": v, "titulo": VISTAS[v]} for v in vistas["vistas"]
                       if v in VISTAS]})
        _poner_la_cookie(respuesta, token)
        return respuesta

    return _con_la_base(leer)


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
            calendario = Calendario.desde_base(cur, ws)
        return _json(armar_vista(vista, filas, esperas, calendario, ahora))

    return _con_la_base(leer)


def armar_vista(vista: str, filas: list[dict[str, Any]], esperas: list[dict[str, Any]],
                calendario, ahora: datetime) -> dict[str, Any]:
    """La respuesta de una vista con lo que devolvió la base: nada de lo que se arma acá decide
    quién ve qué; el atraso y el bloqueo nulos siguen nulos."""
    hoy = ahora.astimezone(calendario.zona).date()
    arboles = _arboles(esperas)
    tareas_ = [_tarea(f, arboles, calendario, ahora, hoy) for f in filas]
    panel = {marca: 0 for marca in MARCAS}
    for t in tareas_:
        if t["marca"] is not None:
            panel[t["marca"]] += 1
    vencen = {t["fecha_objetivo"] for t in tareas_ if t["fecha_objetivo"]}
    return {
        "vista": vista, "titulo": VISTAS[vista],
        "hoy": hoy.isoformat(), "semana_iso": hoy.isocalendar()[1],
        "panel": panel, "activas": len(tareas_),
        "semana": _semana(calendario, hoy, vencen),
        "tareas": tareas_,
    }


def _local(momento: datetime | None, calendario) -> date | None:
    return None if momento is None else momento.astimezone(calendario.zona).date()


def _marca(fila: dict[str, Any]) -> str | None:
    """El estado con color de la tarjeta, uno solo: trabada, vencida, entregada o en curso; las
    demás, ninguno (gris). Trabada y vencida sólo si la base las mostró a esta persona."""
    if fila["bloqueo_abierto"] is True:
        return TRABADA
    if fila["vencida"] is True:
        return VENCIDA
    if fila["estado"] == "en_revision":
        return ENTREGADA
    if fila["estado"] == "en_curso":
        return EN_CURSO
    return None


def _tarea(fila: dict[str, Any], arboles: dict[str, list[dict[str, Any]]], calendario,
           ahora: datetime, hoy: date) -> dict[str, Any]:
    vence = _local(fila["fecha_objetivo"], calendario)
    asignada = _local(fila["asignada_en"], calendario)
    bloqueo = fila["bloqueo_abierto"]
    return {
        "id": str(fila["task_id"]),
        "titulo": fila["titulo"],
        "estado": fila["estado"],
        "marca": _marca(fila),
        "fecha_objetivo": vence.isoformat() if vence else None,
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
    primera = ruta.split("/", 1)[0]
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


def cortar_sesiones(cur, membership_id: str) -> int:
    """Corta todas las sesiones abiertas de una persona del espacio de la transacción, y su
    enlace sin usar, por un administrador. Devuelve cuántas sesiones cortó."""
    _con_la_version_del_nucleo(cur)
    cur.execute("select cortar_sesiones_de_membresia(%s, %s, null) as cortadas",
                (str(membership_id), POR_UN_ADMINISTRADOR))
    return int(cur.fetchone()["cortadas"])


def enlace(base_url: str, token: str) -> str:
    """La dirección del enlace de entrada, sobre la dirección pública configurada."""
    return f"{base_url.rstrip('/')}/app/entrar/{token}"
