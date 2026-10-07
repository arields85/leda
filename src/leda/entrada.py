"""La entrada HTTP de Leda (E3-2, enredos 3 y 4 de `odd/tasks/motor-definitivo.md`; E3-7).

La contraparte de `salida.py`: lo que llega de afuera. La aplicación (`app`), sus rutas
(`POST /telegram/{slug}`, `GET /tablero/{token}`, `GET /salud`), el registro de los webhooks
(`registrar_webhooks`, `python -m leda webhooks`) y lo que la recuperación de un mensaje sin
respuesta comparte con el barrido de huérfanos (`huerfanos.py`): la ventana del turno en curso,
la cota de reentrega, el candado por mensaje y el criterio de "este mensaje ya tiene respuesta".

**El webhook** (E3-7) es la entrada de producción del motor de conversación: lo que hace con
cada update es lo mismo que el escuchador por long polling (`leda.motor.recibir`), importado
dentro de las funciones. Telegram manda en cada entrega el secreto que se le dio al registrar
el webhook; cada bot tiene el suyo, derivado de `LEDA_WEBHOOK_SECRET` y del espacio
(`secreto_del_bot`), así el secreto de un espacio no abre el webhook de otro. Sin secreto
configurado, el webhook no atiende a nadie. Lo despacha el ciclo de fondo de `servir`
(`leda.motor.fondo`).

Es de la capa sólida (`tests/garantias/test_frontera_de_la_entrada.py`).
"""

from __future__ import annotations

import hashlib
import hmac
import threading
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, FastAPI, Header, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse

from .config import config
from .db import admin, conectar, espacio

app = FastAPI(title="Leda", docs_url=None, redoc_url=None)
router = APIRouter()

# T9-H19d: el recibo de la fase 1 significa "recibido", no "respondido". Una
# reentrega del mismo mensaje se absorbe sólo si (a) ya tiene una respuesta visible,
# o (b) su recibo es lo bastante reciente como para que el turno siga corriendo.
# La duración de un turno está acotada: cada llamada al modelo tarda a lo sumo
# `llm.TIMEOUT_MODELO_S` (20 s) x (1 + `REINTENTOS_MODELO` = 2) = 60 s, y un turno
# encadena el enrutamiento (2 intentos) y hasta `agente.MAX_VUELTAS` (5) vueltas:
# ~7 min en el peor caso teórico, 10-30 s en el normal. 10 min queda por encima.
# Un recibo más viejo y sin respuesta es un turno muerto (reinicio, OOM): la
# reentrega es la recuperación.
VENTANA_TURNO_EN_CURSO = timedelta(minutes=10)
# Cota global: la Bot API guarda las actualizaciones a lo sumo 24 horas ("they will
# not be kept longer than 24 hours", getUpdates) y del webhook sólo dice que
# reintenta "una cantidad razonable de veces" (SUPUESTO: no reentrega más allá de
# esa cota). Un recibo más viejo nunca absorbe: si Telegram reinicia la numeración
# (cambia el token del bot), un mensaje nuevo puede chocar con un id viejo.
COTA_REENTREGA = timedelta(hours=24)


def clave_de_candado_del_mensaje(workspace_id: str, chat_id: int,
                                 message_id: int) -> str:
    """La clave del candado de asesor de un mensaje de Telegram. La usa el barrido de
    huérfanos (`huerfanos.barrer`) y la va a compartir la recuperación de la entrada del
    motor (E3-7; la de `gateway` se retiró en la E3-4): así nunca actúan a la vez sobre
    el mismo mensaje."""
    return f"mensaje:{workspace_id}:{chat_id}:{message_id}"


def sql_respondido(recibo: str) -> str:
    """Fragmento SQL: el recibo `recibo` (alias de una fila de `inbound_message`) ya
    tiene respuesta. Es el criterio único de "este turno no murió" (T9-H19f) de
    `huerfanos.barrer`, y el de la recuperación de la entrada del motor (E3-7).

    Cuenta una fila de respuesta en CUALQUIER estado. Lo que el código descarta a
    propósito antes de enviar (un juego de opciones reemplazado, una vista previa que
    ya no es vigente al despachar, el duplicado que `respuesta_unica.controlar`
    suprime) o lo que falló al entregarse (con su propio incidente) es la respuesta de
    un turno que vivió; un turno que murió no deja NINGUNA fila de respuesta (murió
    antes de encolar o su transacción se revirtió). No confundir con
    `respuesta_unica.respuestas_del_mensaje`, que cuenta las visibles para garantizar
    una sola."""
    return (f"exists (select 1 from message_outbox o where o.entrante_id = {recibo}.id"
            f" and o.chat_id = {recibo}.chat_id and o.es_respuesta)")


def _conn():
    """La conexión de la aplicación, una por proceso y reabierta si se cerró."""
    if not hasattr(_conn, "_c") or _conn._c.closed:
        _conn._c = conectar()
    return _conn._c


# --- El webhook del motor (E3-7) ------------------------------------------------------------

# Los updates se atienden de a uno: comparten la conexión de la aplicación.
_ATENCION = threading.Lock()
# Las fallas al recibir cada update, por bot (`recibir.IntentosPorUpdate`).
_INTENTOS: dict[str, Any] = {}


def secreto_del_bot(slug: str) -> str:
    """El secreto que Telegram manda en cada entrega al webhook del bot de `slug` (cabecera
    `X-Telegram-Bot-Api-Secret-Token`): derivado de `LEDA_WEBHOOK_SECRET` y del espacio, con
    los caracteres que Telegram acepta. Sin secreto configurado, ninguno."""
    if not config.webhook_secret:
        return ""
    return hmac.new(config.webhook_secret.encode(), f"telegram:{slug}".encode(),
                    hashlib.sha256).hexdigest()


def _secreto_valido(slug: str, recibido: str) -> bool:
    esperado = secreto_del_bot(slug)
    return bool(esperado) and hmac.compare_digest(recibido.encode(), esperado.encode())


@router.post("/telegram/{slug}")
async def webhook(slug: str, request: Request,
                  x_telegram_bot_api_secret_token: str = Header(default="")):
    """Un update de Telegram para el bot de `slug`. Sin el secreto de ese bot no se mira ni el
    cuerpo. Un error 503 le pide a Telegram que lo reentregue (la base no contestó)."""
    if not _secreto_valido(slug, x_telegram_bot_api_secret_token):
        raise HTTPException(status_code=403, detail="origen no verificado")
    try:
        update = await request.json()
    except ValueError:
        raise HTTPException(status_code=400, detail="cuerpo inválido") from None
    if not isinstance(update, dict) or not isinstance(update.get("update_id"), int):
        raise HTTPException(status_code=400, detail="cuerpo inválido")
    return await run_in_threadpool(atender_update, slug, update)


def atender_update(slug: str, update: dict[str, Any]) -> dict[str, bool]:
    """Lo que el webhook hace con un update, ya verificado su origen: el del bot de
    administración registra el chat de un administrador; el del bot de un espacio pasa por el
    motor (`recibir.recibir_update`), igual que en el escuchador."""
    from .motor.recibir import (IntentosPorUpdate, Recepcion, bot_id_del_token,
                                recibir_update, registrar_admin)

    with _ATENCION:
        conn = _conn()
        try:
            token = _token_de(slug)
        except LookupError:
            raise HTTPException(status_code=404, detail="bot desconocido") from None
        if slug == "admin":
            registrar_admin(conn, update, _imprimir)
            return {"ok": True}
        with admin(conn) as cur:
            cur.execute("select id from workspace where slug = %s and activo", (slug,))
            fila = cur.fetchone()
        conn.commit()
        if fila is None:
            raise HTTPException(status_code=404, detail="espacio desconocido")
        ws = str(fila["id"])
        recepcion = Recepcion(conn, ws, _ia_de(conn, ws), _reloj_de(conn, ws),
                              bot_id=bot_id_del_token(token), senal=_senal(token),
                              imprimir=_imprimir)
        intentos = _INTENTOS.setdefault(slug, IntentosPorUpdate())
        if not recibir_update(recepcion, intentos, update):
            raise HTTPException(status_code=503, detail="no se pudo recibir; reentregar")
    return {"ok": True}


def _token_de(slug: str) -> str:
    return config.token_bot(slug)


def _ia_de(conn, workspace_id: str):
    """La IA del espacio; sin una configurada, la que no responde (el turno deja el incidente
    y la persona recibe el texto fijo)."""
    from .motor.ia_real import desde_base
    from .motor.recibir import IANoConfigurada

    try:
        with espacio(conn, workspace_id) as cur:
            return desde_base(cur, workspace_id, config)
    except LookupError as e:
        return IANoConfigurada(str(e))
    finally:
        conn.commit()


def _reloj_de(conn, workspace_id: str):
    """El reloj de Leda (fuera de `leda_motor`, el real), con su adelanto leído."""
    from .motor.reloj import RelojDeLeda

    reloj = RelojDeLeda()
    try:
        reloj.refrescar(conn, workspace_id)
        conn.commit()
    except Exception:  # noqa: BLE001 -- sin adelanto: el tiempo real
        conn.rollback()
    return reloj


def _cliente_http():
    """El cliente HTTP de la aplicación hacia Telegram, uno por proceso."""
    import httpx

    if not hasattr(_cliente_http, "_c") or _cliente_http._c.is_closed:
        _cliente_http._c = httpx.Client(timeout=15)
    return _cliente_http._c


def _senal(token: str):
    """El acuse de un toque (`answerCallbackQuery`), por el bot que lo recibió."""
    from .motor.escucha import BotTelegram

    def senal(callback_query_id: str) -> None:
        BotTelegram(token, _cliente_http()).llamar("answerCallbackQuery",
                                                   callback_query_id=callback_query_id)
    return senal


def _imprimir(linea: str) -> None:
    """En la consola del servidor, sólo las fallas: nunca el texto de una conversación."""
    if linea.lstrip().startswith("!"):
        print(linea)


@router.get("/tablero/{token}", response_class=HTMLResponse)
def tablero_web(token: str):
    """La pantalla del tablero.

    El espacio sale del token y de ningún otro lado. No hay parámetro de
    consulta, cabecera ni segmento de URL que lo indique: si lo hubiera,
    cambiarlo sería todo lo que hace falta para mirar el espacio de otro.

    Un token inválido, vencido, o de alguien que dejó el equipo, devuelven lo
    mismo. Distinguirlos le diría a quien prueba enlaces cuáles existieron.
    """
    return _servir_tablero(_conn(), token)


def _servir_tablero(conn, token: str) -> HTMLResponse:
    from . import lectura
    from . import tablero
    from .db import sin_espacio
    from .tablero_vista import enlace_vencido, pagina

    with sin_espacio(conn) as cur:
        acceso = tablero.resolver(cur, token)

    if acceso is None:
        return HTMLResponse(enlace_vencido(), status_code=401)

    ahora = datetime.now(timezone.utc)

    with espacio(conn, acceso["workspace_id"]) as cur:
        cur.execute("select nombre from workspace")
        fila = cur.fetchone()
        nombre_espacio = fila["nombre"] if fila else "Tu equipo"
        cur.execute("select nombre from integrante where membership_id = %s",
                    (acceso["membership_id"],))
        fila = cur.fetchone()
        persona = fila["nombre"] if fila else ""
        datos = {
            "objetivos": lectura.avance_de_objetivos(cur),
            "estados": lectura.tareas_por_estado(cur),
            "carga": lectura.carga_por_persona(cur),
            "vencidas": lectura.tareas_vencidas(cur, ahora),
            "bloqueos": lectura.bloqueos_abiertos(cur, ahora),
            "aprobacion": lectura.trabajo_esperando_aprobacion(cur),
        }

    return HTMLResponse(
        pagina(datos, espacio=nombre_espacio, persona=persona))


@router.get("/salud")
def salud():
    return {"ok": True}


app.include_router(router)


def registrar_webhooks(cliente=None) -> dict[str, bool]:
    """Le dice a Telegram dónde entregar, un bot por espacio y el de administración, cada uno
    con su secreto (`secreto_del_bot`). Se niega sin `LEDA_BASE_URL` o sin
    `LEDA_WEBHOOK_SECRET`. Devuelve, por espacio, si Telegram lo aceptó; nunca el token."""
    import httpx

    from .despachador import pedido_telegram

    if not config.base_url or not config.webhook_secret:
        raise LookupError("Faltan LEDA_BASE_URL o LEDA_WEBHOOK_SECRET en el entorno: sin "
                          "ellos no se registra ningún webhook.")
    cliente = cliente or httpx.Client(timeout=15)
    base = config.base_url.rstrip("/")
    resultado: dict[str, bool] = {}
    for slug, token in sorted(config.espacios_con_token().items()):
        r = pedido_telegram(
            cliente.post, f"https://api.telegram.org/bot{token}/setWebhook",
            json={"url": f"{base}/telegram/{slug}", "secret_token": secreto_del_bot(slug),
                  "allowed_updates": (["message"] if slug == "admin"
                                      else ["message", "callback_query"])})
        resultado[slug] = r.status_code == 200 and bool(r.json().get("ok", False))
    return resultado
