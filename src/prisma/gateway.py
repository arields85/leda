"""Webhook de Telegram.

Un bot por espacio de trabajo. La ruta lleva el slug, así que el espacio queda
determinado por el canal de entrada y no hay que deducirlo del mensaje: si
alguien pertenece a dos equipos, no existe ambigüedad.

El secreto de Telegram se verifica en cada llamada. Sin eso, cualquiera que
conozca la URL podría hacerse pasar por el gateway.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI, Header, HTTPException, Request

from .autoridad import (Canal, Denegado, identificar, identificar_en_espacio)
from .config import config
from .db import (admin, autoridad, conectar, conectar_autoridad, espacio,
                 registrar_auditoria)
from .despachador import acusar_toque

app = FastAPI(title="Prisma", docs_url=None, redoc_url=None)
router = APIRouter()


def _conn():
    if not hasattr(_conn, "_c") or _conn._c.closed:
        _conn._c = conectar()
    return _conn._c


def _authority_conn():
    if not config.authority_db_url:
        raise RuntimeError("Falta PRISMA_AUTHORITY_DB_URL.")
    if not hasattr(_authority_conn, "_c") or _authority_conn._c.closed:
        _authority_conn._c = conectar_autoridad(config.authority_db_url)
    return _authority_conn._c


def _espacio_por_slug(cur, slug: str) -> dict[str, Any] | None:
    cur.execute("select id, slug, activo from workspace where slug = %s", (slug,))
    return cur.fetchone()


@router.post("/telegram/{slug}")
async def webhook(slug: str, request: Request,
                  x_telegram_bot_api_secret_token: str = Header(default="")):
    if config.webhook_secret and x_telegram_bot_api_secret_token != config.webhook_secret:
        raise HTTPException(status_code=403, detail="origen no verificado")

    update = await request.json()
    return procesar_update(_conn(), slug, update)


def procesar_update(conn, slug: str, update: dict,
                    authority_conn=None) -> dict:
    """Atiende un update de Telegram.

    La usan el webhook y el modo local por polling. Que sea la misma función
    es lo que hace que pasar de una máquina a la VPS no cambie el
    comportamiento.
    """
    mensaje = update.get("message") or update.get("edited_message")
    toque = update.get("callback_query")
    if not mensaje and not toque:
        return {"ok": True}

    texto = mensaje.get("text", "") if mensaje else ""
    chat_id = mensaje["chat"]["id"] if mensaje else None
    tg_user = (mensaje or toque).get("from", {}).get("id")

    canal = Canal.ADMINISTRACION if slug == "admin" else Canal.ESPACIO

    if canal is Canal.ADMINISTRACION:
        if not mensaje:
            return {"ok": True}
        with conn.cursor() as cur:
            cur.execute("set role prisma_admin")
            try:
                quien = identificar(cur, tg_user, canal, None)
            except Denegado:
                return {"ok": True}
            registrar_auditoria(
                cur, accion="mensaje_admin", actor_app_user_id=quien.app_user_id,
                actor_kind="persona", detalle={"chat_id": chat_id})
        conn.commit()
        return {"ok": True}

    with conn.cursor() as cur:
        cur.execute("set role prisma_admin")
        ws = _espacio_por_slug(cur, slug)
    if ws is None or not ws["activo"]:
        raise HTTPException(status_code=404, detail="espacio no disponible")
    workspace_id = str(ws["id"])

    if toque:
        return _toque(conn, workspace_id, slug, toque, tg_user,
                      authority_conn=authority_conn)

    # /start va antes de identificar: quien lo manda todavía no está vinculado.
    if texto.startswith("/start"):
        return _activacion(conn, workspace_id, texto, tg_user, chat_id)

    with espacio(conn, workspace_id) as cur:
        try:
            # Por la vista, que ya está acotada al espacio: si la persona no
            # es de este equipo, sencillamente no aparece.
            quien = identificar_en_espacio(cur, tg_user, workspace_id)
        except Denegado:
            # A un desconocido no se le explica por qué no se le responde.
            desconocido = True
        else:
            desconocido = False

        if desconocido:
            return {"ok": True}

        cur.execute(
            """insert into inbound_message
                 (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
               values (%s, %s, %s, %s, %s) returning id""",
            (workspace_id, mensaje.get("message_id"), chat_id,
             quien.app_user_id, texto))
        entrante_id = str(cur.fetchone()["id"])
        registrar_auditoria(
            cur, accion="mensaje_recibido", workspace_id=workspace_id,
            actor_app_user_id=quien.app_user_id, actor_kind="persona",
            detalle={"chat_id": chat_id})

        if texto.strip():
            _turno(cur, quien, texto, workspace_id, chat_id, entrante_id)

    conn.commit()
    # La respuesta sale por la cola, no por acá: Telegram espera un ACK rápido
    # y así el envío conserva idempotencia y auditoría.
    return {"ok": True}


def _activacion(conn, workspace_id: str, texto: str, tg_user: int,
                chat_id: int) -> dict:
    """Canjea el token de un enlace de activación.

    Requiere permisos de administración porque escribe en app_user, que es
    global. Es la única operación de un bot de espacio que los necesita, y
    está acotada a esto.
    """
    from .onboarding import ActivacionInvalida, activar, bienvenida

    partes = texto.split(maxsplit=1)

    if len(partes) < 2:
        # /start sin token. Si la persona ya está vinculada —porque su
        # identificador vino en el pack— igual corresponde saludarla: ese
        # primer mensaje es lo que habilita a Telegram a escribirle después.
        from .onboarding import bienvenida

        with admin(conn) as cur:
            cur.execute(
                """select u.nombre from membership m
                     join app_user u on u.id = m.app_user_id
                    where m.workspace_id = %s and u.telegram_user_id = %s
                      and m.activo""",
                (workspace_id, tg_user))
            fila = cur.fetchone()
            if not fila:
                return {"ok": True}      # desconocido: no se le responde
            cur.execute(
                """insert into message_outbox
                     (workspace_id, chat_id, tipo, cuerpo, estado,
                      programado_para, dedupe_key, es_respuesta)
                   values (%s, %s, 'informativo', %s, 'listo', now(), %s, true)
                   on conflict (dedupe_key) do nothing""",
                (workspace_id, chat_id, bienvenida(cur, workspace_id, fila["nombre"]),
                 f"{workspace_id}:alta:{tg_user}"))
        conn.commit()
        return {"ok": True}

    with admin(conn) as cur:
        try:
            nombre = activar(cur, workspace_id, partes[1].strip(), tg_user)
        except ActivacionInvalida as e:
            cuerpo = str(e) + " Pedile uno nuevo a quien te lo pasó."
        else:
            cuerpo = bienvenida(cur, workspace_id, nombre)
            registrar_auditoria(
                cur, accion="activacion", workspace_id=workspace_id,
                actor_kind="persona", detalle={"nombre": nombre})

        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, tipo, cuerpo, estado, programado_para,
                  dedupe_key, es_respuesta)
               values (%s, %s, 'informativo', %s, 'listo', now(), %s, true)
               on conflict (dedupe_key) do nothing""",
            (workspace_id, chat_id, cuerpo, f"{workspace_id}:alta:{tg_user}"))
    return {"ok": True}


def _toque(conn, workspace_id: str, slug: str, toque: dict,
           tg_user: int | None, authority_conn=None) -> dict:
    """Alguien apretó un botón.

    El botón trae el token de una opción; la acción que ejecuta estaba
    congelada desde antes. Lo que decide si corre no es el botón sino la
    autoridad de quien lo apretó, verificada acá y otra vez en la herramienta.

    Ejecutar sigue pasando por `herramientas.ejecutar`: un botón no es un
    segundo portón a la base.
    """
    from datetime import datetime, timezone

    from . import herramientas as H
    from . import pendientes as P
    from .autoridad import Denegado as NoPuede

    token = P.token_de(toque.get("data") or "")
    chat_id = (toque.get("message") or {}).get("chat", {}).get("id")
    if not token or tg_user is None or chat_id is None:
        return {"ok": True}

    # Antes de trabajar: Telegram quiere el acuse en un par de segundos y lo
    # que sigue puede tardar más. Si falla, es sólo el reloj girando en el
    # teléfono de alguien; el trabajo se hace igual.
    try:
        acusar_toque(config.token_bot(slug), toque.get("id", ""))
    except Exception:  # noqa: BLE001
        pass

    ahora = datetime.now(timezone.utc)
    draft_token = False

    with espacio(conn, workspace_id) as cur:
        try:
            quien = identificar_en_espacio(cur, tg_user, workspace_id)
        except Denegado:
            return {"ok": True}      # desconocido: no se le responde

        try:
            draft_token = P.es_borrador(cur, token)
            if not draft_token:
                resuelta = P.resolver(cur, token,
                                      app_user_id=quien.app_user_id, ahora=ahora)
        except NoPuede as e:
            # Se le contesta, pero la acción sigue esperando a quien sí puede.
            # Salir del `with` confirma el mensaje encolado y nada más.
            _responder(cur, workspace_id, chat_id, quien, str(e), ahora)
            return {"ok": True}

        if not draft_token and resuelta is None:
            # Vencida, ya usada, o de otro espacio. Para la persona es lo
            # mismo: ese pedido ya no está en pie.
            _responder(cur, workspace_id, chat_id, quien,
                       "Ese pedido ya no está vigente. Si sigue haciendo "
                       "falta, escribime y lo vemos de nuevo.", ahora)
        elif not draft_token and resuelta.cancelada:
            _responder(cur, workspace_id, chat_id, quien,
                       "Listo, no lo hago.", ahora)
        elif not draft_token:
            if resuelta.task_id:
                _responder(cur, workspace_id, chat_id, quien,
                           "Hecho. La tarea quedó comprometida.", ahora)
            else:
                try:
                    resultado = H.ejecutar(
                        cur, quien, resuelta.herramienta, resuelta.args,
                        ya_confirmada=True)
                except Denegado as e:
                    _responder(cur, workspace_id, chat_id, quien, str(e), ahora)
                else:
                    registrar_auditoria(
                        cur, accion=f"herramienta:{resuelta.herramienta}",
                        workspace_id=workspace_id,
                        actor_app_user_id=quien.app_user_id, actor_kind="persona",
                        detalle={"args": resuelta.args, "via": "boton"})
                    if isinstance(resultado, dict) and resultado.get("draft_id"):
                        if resultado.get("pendiente_revision"):
                            texto = ("Guardé el borrador y envié la vista previa a "
                                     "quien puede confirmarlo.")
                        else:
                            texto = ("Guardé el pedido como borrador; todavía "
                                     "está incompleto.")
                        _responder(cur, workspace_id, chat_id, quien, texto, ahora)
                    else:
                        _responder(cur, workspace_id, chat_id, quien, "Hecho.", ahora)

    if draft_token:
        return _resolver_toque_borrador(
            conn, authority_conn or _authority_conn(), workspace_id, token,
            tg_user, chat_id, quien, ahora)

    conn.commit()
    return {"ok": True}


def _resolver_toque_borrador(conn, authority_conn, workspace_id, token,
                             tg_user, chat_id, quien, ahora) -> dict:
    """Resolve outside the app transaction, then enqueue its response."""
    from . import pendientes as P

    try:
        with autoridad(authority_conn) as authority_cur:
            resuelta = P.resolver_borrador(
                authority_cur, workspace_id, token, tg_user)
    except Denegado as e:
        resuelta = None
        texto = str(e)
    else:
        texto = None

    with espacio(conn, workspace_id) as cur:
        if texto is not None:
            pass
        elif resuelta is None:
            texto = ("Ese pedido ya no está vigente. Si sigue haciendo falta, "
                     "escribime y lo vemos de nuevo.")
        elif resuelta.cancelada:
            texto = "Listo, no lo hago."
        else:
            texto = "Hecho. La tarea quedó comprometida."
        _responder(cur, workspace_id, chat_id, quien, texto, ahora)
    conn.commit()
    return {"ok": True}


def _responder(cur, workspace_id: str, chat_id: int, quien, texto: str,
               ahora) -> None:
    """La respuesta al toque sale por la cola, como cualquier otra."""
    cur.execute(
        """insert into message_outbox
             (workspace_id, chat_id, destinatario_membership_id, tipo, cuerpo,
              estado, programado_para, dedupe_key, es_respuesta)
           values (%s, %s, %s, 'normal', %s, 'listo', %s, %s, true)
           on conflict (dedupe_key) do nothing""",
        (workspace_id, chat_id, quien.membership_id, texto, ahora,
         f"{workspace_id}:toque:{quien.app_user_id}:{ahora.timestamp()}"))


def _turno(cur, quien, texto: str, workspace_id: str, chat_id: int,
           entrante_id: str | None = None) -> None:
    from .agente import responder
    from .calendario import Calendario
    from .llm import desde_base

    cal = Calendario.desde_base(cur, workspace_id)
    proveedor = desde_base(cur, workspace_id, config.llm_api_key)
    responder(cur, quien, texto, proveedor, cal, chat_id,
              entrante_id=entrante_id)


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
        r = cliente.post(
            f"https://api.telegram.org/bot{token}/setWebhook",
            json={"url": f"{config.base_url}/telegram/{slug}",
                  "secret_token": config.webhook_secret,
                  "allowed_updates": ["message", "callback_query"]})
        resultado[slug] = r.status_code == 200 and r.json().get("ok", False)
    return resultado
