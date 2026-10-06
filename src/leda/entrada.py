"""La entrada HTTP de Leda (E3-2, enredos 3 y 4 de `odd/tasks/motor-definitivo.md`).

La contraparte de `salida.py`: lo que llega de afuera. La aplicación (`app`), sus rutas
(`POST /telegram/{slug}`, `GET /tablero/{token}`, `GET /salud`), el registro de los webhooks
en Telegram y lo que la recuperación de un mensaje sin respuesta comparte con el barrido de
huérfanos (`huerfanos.py`): la ventana del turno en curso, la cota de reentrega, el candado
por mensaje y el criterio de "este mensaje ya tiene respuesta".

Es de la capa sólida: no importa la conversación de los flujos A y B
(`tests/garantias/test_frontera_de_la_entrada.py`). Su único borde conocido es la ruta
`/telegram/{slug}`, que hasta la entrada del motor (E3-7) le pasa el update a
`gateway.webhook` con un import de dentro de la función.

Un bot por espacio de trabajo. La ruta lleva el slug, así que el espacio queda
determinado por el canal de entrada y no hay que deducirlo del mensaje: si
alguien pertenece a dos equipos, no existe ambigüedad.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, FastAPI, Header, Request
from fastapi.responses import HTMLResponse

from .config import config
from .db import conectar, espacio
from .despachador import pedido_telegram

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
    """La clave del candado de asesor de un mensaje de Telegram. La comparten la
    recuperación del gateway (`_estado_de_entrega`) y el barrido de huérfanos
    (`huerfanos.barrer`): así nunca actúan a la vez sobre el mismo mensaje."""
    return f"mensaje:{workspace_id}:{chat_id}:{message_id}"


def sql_respondido(recibo: str) -> str:
    """Fragmento SQL: el recibo `recibo` (alias de una fila de `inbound_message`) ya
    tiene respuesta. Es el criterio único de "este turno no murió" (T9-H19f) que
    comparten `gateway._estado_de_entrega` y `huerfanos.barrer`.

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
    """La conexión de la aplicación, una por proceso y reabierta si se cerró. `gateway`
    usa esta misma para atender el webhook."""
    if not hasattr(_conn, "_c") or _conn._c.closed:
        _conn._c = conectar()
    return _conn._c


@router.post("/telegram/{slug}")
async def webhook(slug: str, request: Request, background_tasks: BackgroundTasks,
                  x_telegram_bot_api_secret_token: str = Header(default="")):
    """El update de un bot. Hasta la entrada del motor (E3-7) lo atiende la
    conversación de los flujos A y B, entera: la verificación del secreto, el turno y
    el despacho inmediato de fondo viven en `gateway.webhook`.

    Borde conocido (`tests/garantias/test_frontera_de_la_entrada.py`): el import es de
    dentro de la función, para que importar la entrada no cargue `gateway`."""
    from . import gateway

    return await gateway.webhook(
        slug, request, background_tasks,
        x_telegram_bot_api_secret_token=x_telegram_bot_api_secret_token)


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
    """Le dice a Telegram dónde entregar, un bot por espacio."""
    import httpx

    cliente = cliente or httpx.Client(timeout=15)
    resultado: dict[str, bool] = {}
    for slug, token in config.espacios_con_token().items():
        r = pedido_telegram(
            cliente.post, f"https://api.telegram.org/bot{token}/setWebhook",
            json={"url": f"{config.base_url}/telegram/{slug}",
                  "secret_token": config.webhook_secret,
                  "allowed_updates": ["message", "callback_query"]})
        resultado[slug] = r.status_code == 200 and r.json().get("ok", False)
    return resultado
