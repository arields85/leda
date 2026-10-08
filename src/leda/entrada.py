"""La entrada HTTP de Leda (E3-2, enredos 3 y 4 de `odd/tasks/motor-definitivo.md`; E3-7).

La contraparte de `salida.py`: lo que llega de afuera. La aplicación (`app`), sus rutas
(`POST /telegram/{slug}`, `GET /tablero/{token}`, `GET /tarea/{token}`, `GET /salud`), el registro
de los webhooks
(`registrar_webhooks`, `python -m leda webhooks`) y lo que la recuperación de un mensaje sin
respuesta comparte con el barrido de huérfanos (`huerfanos.py`): la ventana del turno en curso,
la cota de reentrega, el candado por mensaje y el criterio de "este mensaje ya tiene respuesta".

**El webhook** (E3-7) es la entrada de producción del motor de conversación: lo que hace con
cada update es lo mismo que el escuchador por long polling (`leda.motor.recibir`), importado
dentro de las funciones. Telegram manda en cada entrega el secreto que se le dio al registrar
el webhook; cada bot tiene el suyo, derivado de `LEDA_WEBHOOK_SECRET` y del espacio
(`secreto_del_bot`), así el secreto de un espacio no abre el webhook de otro. Sin secreto
configurado, el webhook no atiende a nadie. La respuesta de cada update sale al atenderlo, por
el bot que lo recibió (`recibir.Recepcion.despachar_ahora`); el ciclo de fondo de `servir`
(`leda.motor.fondo`) despacha lo demás, y lo que no haya salido ahí.

**La página de una tarea** (ADR 0019, decisión 7): de sólo lectura, con un enlace personal que
no vence. Lee sólo por las funciones de la base que reciben el hash del token y deciden quién ve
qué (`pagina_de_tarea.py`); usa su propia conexión, bajo su propio candado, para no esperar a un
turno de la conversación ni compartir su transacción.

**Un álbum** (ADR 0019, decisión 4): cada foto llega en un update aparte y se guarda al
atenderlo; el turno del álbum corre una vez. Después de guardar una foto de un álbum, el pedido
espera `recibir.ESPERA_ALBUM_S` fuera del candado que atiende los updates (así entran las demás
fotos) y vuelve a tomarlo para atender los álbumes que ya esperaron
(`recibir.Recepcion.atender_albumes`): el de la última foto lo atiende; los demás no encuentran
nada que hacer.

Es de la capa sólida (`tests/garantias/test_frontera_de_la_entrada.py`).
"""

from __future__ import annotations

import hashlib
import hmac
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, FastAPI, Header, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse, Response

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
    huérfanos (`huerfanos.barrer`) y el turno de la entrada del motor
    (`motor.recibir.Recepcion`, E3-7): así nunca actúan a la vez sobre el mismo mensaje."""
    return f"mensaje:{workspace_id}:{chat_id}:{message_id}"


def sql_respondido(recibo: str) -> str:
    """Fragmento SQL: el recibo `recibo` (alias de una fila de `inbound_message`) ya
    tiene respuesta. Es el criterio único de "este turno no murió" (T9-H19f) de
    `huerfanos.barrer`, y el de la entrada del motor, que no vuelve a atender un mensaje
    que ya tiene respuesta (`motor.recibir`, E3-7).

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
# La espera de un álbum, fuera del candado (las pruebas la cambian).
_esperar = time.sleep


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
    from .motor import recibir
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
                              imprimir=_imprimir, indicador=_indicador(token),
                              transporte=_transporte_de(token), bajar=_bajar_de(token))
        intentos = _INTENTOS.setdefault(slug, IntentosPorUpdate())
        if not recibir_update(recepcion, intentos, update):
            raise HTTPException(status_code=503, detail="no se pudo recibir; reentregar")
    if recepcion.albumes_en_espera:
        # Una foto de un álbum: las demás entran mientras ésta espera, fuera del candado.
        _esperar(recibir.ESPERA_ALBUM_S)
        with _ATENCION:
            recepcion.conn = _conn()
            recepcion.atender_albumes()
            recepcion.despachar_ahora()
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


def _indicador(token: str):
    """El indicador de actividad de un turno (ADR 0011, decisión 2), por el bot que recibió el
    mensaje y con el cliente HTTP de la aplicación: el "escribiendo…", los tres puntos y la
    redacción en vivo. El motor sólo atiende chats privados, así que lleva borrador. La
    respuesta sale al terminar de atender el update (`_transporte_de`) y reemplaza al borrador,
    sin retiro."""
    from .despachador import mantener_chat_activo

    def abrir(chat_id: int):
        return mantener_chat_activo(token, chat_id, cliente=_cliente_http(), chat_type="private")
    return abrir


def _transporte_de(token: str):
    """Por dónde sale enseguida la respuesta de un update: el bot que lo recibió, con el
    cliente HTTP de la aplicación. El mismo despacho del outbox que el de fondo."""
    from .despachador import TransporteTelegram

    return TransporteTelegram(token, cliente=_cliente_http())


def _bajar_de(token: str):
    """Cómo se baja un archivo recibido (`recibir.Bajar`): por el bot que lo recibió, con el
    cliente HTTP de la aplicación."""
    from .motor.escucha import BotTelegram

    def bajar(file_id: str, maximo: int) -> bytes:
        return BotTelegram(token, _cliente_http()).bajar(file_id, maximo)
    return bajar


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


# --- La página de una tarea (ADR 0019, decisión 7) ------------------------------------------

# Las páginas se leen de a una, con su conexión: no comparten la del webhook ni esperan a un turno.
_PAGINAS = threading.Lock()

# Lo que lleva toda respuesta de la página, también la genérica (7a y 7c): que nada la guarde ni
# la indexe, que no diga de dónde viene quien sigue un enlace, que el navegador no adivine el
# tipo y que no se ejecute nada.
CABECERAS_DE_LA_PAGINA = {
    "Cache-Control": "no-store",
    "Referrer-Policy": "no-referrer",
    "X-Robots-Tag": "noindex, nofollow",
    "X-Content-Type-Options": "nosniff",
    "Content-Security-Policy": ("default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; "
                                "base-uri 'none'; form-action 'none'; frame-ancestors 'none'"),
}
# Un archivo no es una página: no carga nada y, si un navegador lo abriera como una, queda aislado.
POLITICA_DE_UN_ARCHIVO = "default-src 'none'; sandbox"


def _conn_de_paginas():
    """La conexión de las páginas, una por proceso y reabierta si se cerró."""
    if not hasattr(_conn_de_paginas, "_c") or _conn_de_paginas._c.closed:
        _conn_de_paginas._c = conectar()
    return _conn_de_paginas._c


def _no_se_puede_abrir(status_code: int = 404) -> HTMLResponse:
    from .tarea_vista import no_se_puede_abrir

    return HTMLResponse(no_se_puede_abrir(), status_code=status_code,
                        headers=CABECERAS_DE_LA_PAGINA)


@router.get("/tarea/{token}", response_class=HTMLResponse)
def pagina_de_tarea_web(token: str):
    """La página de una tarea. La tarea, el espacio y la persona salen del token, y de ningún
    otro lado. Un token inexistente, revocado o de alguien que ya no puede verla devuelven lo
    mismo."""
    from . import pagina_de_tarea
    from .db import sin_espacio
    from .tarea_vista import pagina

    # La página se arma dentro de la misma transacción que la lee: si algo falla al leerla o al
    # armarla, la persona ve la página genérica (constitución §10) y la vista no queda
    # registrada, porque no se sirvió (7e).
    with _PAGINAS:
        conn = _conn_de_paginas()
        try:
            with sin_espacio(conn) as cur:
                datos = pagina_de_tarea.leer(cur, token)
                html = None if datos is None else pagina(datos, token=token)
        except Exception as falla:  # noqa: BLE001 -- la página nunca muestra un error técnico
            _sin_transaccion(conn)
            _imprimir(f"  ! la página de una tarea no se pudo abrir ({type(falla).__name__}).")
            return _no_se_puede_abrir(503)
    if html is None:
        return _no_se_puede_abrir()
    return HTMLResponse(html, headers=CABECERAS_DE_LA_PAGINA)


@router.get("/tarea/{token}/evidencia/{evidencia}")
def archivo_de_tarea_web(token: str, evidencia: str):
    """El archivo de una evidencia de la tarea del token, con el tipo que detectó el código: una
    imagen que el navegador muestra, para verla; lo demás, como adjunto para bajar. La evidencia
    de otra tarea, o de otro espacio, devuelve la misma página que un enlace que no sirve."""
    from . import pagina_de_tarea
    from .db import sin_espacio

    # Como la página: la respuesta se arma dentro de la transacción que lee el archivo.
    with _PAGINAS:
        conn = _conn_de_paginas()
        try:
            with sin_espacio(conn) as cur:
                archivo = pagina_de_tarea.leer_archivo(cur, token, evidencia)
                respuesta = None if archivo is None else _respuesta_de_archivo(archivo)
        except Exception as falla:  # noqa: BLE001 -- la página nunca muestra un error técnico
            _sin_transaccion(conn)
            _imprimir(f"  ! un archivo de una tarea no se pudo abrir ({type(falla).__name__}).")
            return _no_se_puede_abrir(503)
    return _no_se_puede_abrir() if respuesta is None else respuesta


def _respuesta_de_archivo(archivo: dict[str, Any]) -> Response:
    """El archivo con el tipo que detectó el código: una imagen que se ve; lo demás, adjunto."""
    from urllib.parse import quote

    from .tarea_vista import IMAGENES_QUE_SE_VEN

    modo = "inline" if archivo["tipo"] in IMAGENES_QUE_SE_VEN else "attachment"
    nombre = archivo["nombre"] or "archivo"
    return Response(archivo["contenido"], media_type=archivo["tipo"], headers={
        **CABECERAS_DE_LA_PAGINA,
        "Content-Security-Policy": POLITICA_DE_UN_ARCHIVO,
        "Content-Disposition": f"{modo}; filename*=UTF-8''{quote(nombre, safe='')}"})


def _sin_transaccion(conn) -> None:
    """Después de una falla, la conexión de las páginas vuelve a quedar lista."""
    try:
        conn.rollback()
    except Exception:  # noqa: BLE001 -- una conexión rota se reabre en el próximo pedido
        pass


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
