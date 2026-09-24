"""Webhook de Telegram.

Un bot por espacio de trabajo. La ruta lleva el slug, así que el espacio queda
determinado por el canal de entrada y no hay que deducirlo del mensaje: si
alguien pertenece a dos equipos, no existe ambigüedad.

El secreto de Telegram se verifica en cada llamada. Sin eso, cualquiera que
conozca la URL podría hacerse pasar por el gateway.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from fastapi import APIRouter, FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse

from .autoridad import (Canal, Denegado, identificar, identificar_en_espacio)
from .config import config
from .db import (admin, autoridad, conectar, conectar_autoridad, espacio,
                 registrar_auditoria)
from .despachador import acusar_toque, mantener_chat_activo
from .salida import enqueue_outbox, with_no_effect_status

app = FastAPI(title="Prisma", docs_url=None, redoc_url=None)
router = APIRouter()

# Aclaración con botones (T4, `aclaracion-con-botones`; ADR 0005 decisión 3).
#
# `herramienta` de una acción pendiente de aclaración: nunca es un nombre
# real del `REGISTRO` de `herramientas.py`, así que `_toque` la intercepta
# antes de llegar a `H.ejecutar` (que si no, la rechazaría con "no existe la
# herramienta"). `campo="eleccion"` es lo que hace que `resolver_pendiente`
# devuelva, en `args["eleccion"]`, qué botón se tocó -- el id real de una
# tarea, o uno de estos dos valores reservados que nunca puede ser un id
# (los ids de tarea son UUID).
_SENTINEL_ACLARACION = "_aclarar_referencia"
_OPCION_NINGUNA = "__ninguna__"
_OPCION_NUEVA = "__nueva__"
_ETIQUETA_NINGUNA = "Ninguna, lo escribo"
_ETIQUETA_NUEVA = "Es una tarea nueva"
_TIPO_ELECCION = {_OPCION_NINGUNA: "ninguna", _OPCION_NUEVA: "nueva"}

# Cuántos caracteres del título entran en un botón antes de truncar con
# "…" (medido a ojo para que entre cómodo en una pantalla de teléfono; el
# sufijo " — <nombre>" nunca se recorta, se agrega después de truncar).
TRUNCAR_TITULO_BOTON = 48


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
    chat_type = mensaje.get("chat", {}).get("type") if mensaje else None
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
        try:
            resultado = _toque(conn, workspace_id, slug, toque, tg_user,
                               authority_conn=authority_conn)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return resultado

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

        handled_intake_text = False
        if texto.strip() and chat_type == "private":
            from datetime import datetime, timezone
            from .ingreso_tareas import handle_active_text

            handled_intake_text = handle_active_text(
                cur, quien, chat_id=chat_id, source_inbound_id=entrante_id,
                source_raw_text=texto, now=datetime.now(timezone.utc),
            ) is not None

        if texto.strip() and not handled_intake_text:
            with mantener_chat_activo(config.token_bot(slug), chat_id):
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
            enqueue_outbox(
                cur, workspace_id=workspace_id, chat_id=chat_id,
                text=bienvenida(cur, workspace_id, fila["nombre"]),
                message_type="informativo", dedupe_key=f"{workspace_id}:alta:{tg_user}",
                is_response=True, allow_split=True,
            )
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

        enqueue_outbox(
            cur, workspace_id=workspace_id, chat_id=chat_id, text=cuerpo,
            message_type="informativo", dedupe_key=f"{workspace_id}:alta:{tg_user}",
            is_response=True, allow_split=True,
        )
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

    from . import ingreso_tareas as I

    callback = toque.get("data") or ""
    intake_token = I.token_de(callback)
    token = P.token_de(callback)
    chat_id = (toque.get("message") or {}).get("chat", {}).get("id")
    if (not token and not intake_token) or tg_user is None or chat_id is None:
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

        if intake_token:
            I.resolve_choice(cur, quien, token=intake_token,
                             chat_id=chat_id, now=ahora)
            return {"ok": True}

        try:
            draft_token = P.es_borrador(cur, token)
            if not draft_token:
                resuelta = P.resolver(cur, token,
                                      app_user_id=quien.app_user_id, ahora=ahora)
        except NoPuede as e:
            # Se le contesta, pero la acción sigue esperando a quien sí puede.
            # La frontera exterior confirma el mensaje encolado y nada más.
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
        elif not draft_token and resuelta.modificada:
            # No se aplica nada (T3, ADR 0005 decisión 1): la fila ya quedó
            # cerrada por `resolver_pendiente`, con `herramienta`, `args` y
            # `resumen` guardados como el contexto que va a leer el próximo
            # turno de esta persona en este chat -- `_turno` lo reclama con
            # `pendientes.reclamar_modificacion_abierta` antes de rutear.
            registrar_auditoria(
                cur, accion=f"modificar:{resuelta.herramienta}",
                workspace_id=workspace_id, actor_app_user_id=quien.app_user_id,
                actor_kind="persona", detalle={"args": resuelta.args, "via": "boton"})
            _responder(cur, workspace_id, chat_id, quien,
                       "¿Qué querés cambiar?", ahora)
        elif not draft_token:
            if resuelta.task_id:
                _responder(cur, workspace_id, chat_id, quien,
                           "Hecho. La tarea quedó comprometida.", ahora)
            elif resuelta.herramienta == _SENTINEL_ACLARACION:
                # T4: no es una herramienta real -- `H.ejecutar` la
                # rechazaría -- es la elección de un botón de aclaración.
                _resolver_toque_aclaracion(
                    cur, quien, workspace_id, chat_id, token, resuelta.args, ahora)
            else:
                from .agente import VIGENCIA_PENDIENTE

                prep_capturada: dict = {}
                try:
                    resultado = H.ejecutar(
                        cur, quien, resuelta.herramienta, resuelta.args,
                        ya_confirmada=True, chat_id=chat_id,
                        huella_previa=resuelta.huella,
                        preparacion=prep_capturada)
                except Denegado as e:
                    _responder(cur, workspace_id, chat_id, quien, str(e), ahora)
                except H.EstadoCambio as e:
                    # La situación cambió entre la vista previa y el toque
                    # (ADR 0005, decisión 1): no se aplica nada, se arma una
                    # vista previa nueva y una acción pendiente nueva. Sigue
                    # siendo la vista previa de una herramienta que escribe,
                    # así que conserva sus tres botones (T3).
                    nueva = P.registrar(
                        cur, quien, herramienta=e.herramienta,
                        args=e.argumentos, resumen=e.resumen,
                        vence_en=ahora + VIGENCIA_PENDIENTE, chat_id=chat_id,
                        huella=e.huella,
                        opciones=[("Confirmar", True), ("Modificar", "modificar"),
                                 ("Cancelar", False)])
                    enqueue_outbox(
                        cur, workspace_id=workspace_id, chat_id=chat_id,
                        recipient_membership_id=quien.membership_id,
                        text=("La situación cambió desde que te mostré esto. "
                              f"Vista previa nueva:\n\n{e.resumen}"),
                        scheduled_for=ahora,
                        dedupe_key=(f"{workspace_id}:cambio:{e.herramienta}:"
                                   f"{ahora.timestamp()}"),
                        is_response=True, pending_action_id=nueva.id,
                    )
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
                    elif isinstance(resultado, dict) and (
                            resultado.get("error")
                            or resultado.get("cerrada") is False
                            or resultado.get("iniciada") is False):
                        # La preparación había pasado, pero el handler encontró
                        # un impedimento de negocio al aplicar (p. ej. una
                        # condición de cierre que cambió en el mismo instante).
                        _responder(cur, workspace_id, chat_id, quien,
                                  "No se aplicó el cambio.", ahora)
                    elif prep_capturada.get("cambio"):
                        # El recibo cuenta qué cambió, no un "Hecho." solo
                        # (T2, punto 3): reusa la descripción que ya se había
                        # mostrado en la vista previa, porque la huella
                        # coincidió -- el estado sigue siendo ese.
                        _responder(cur, workspace_id, chat_id, quien,
                                  f"Hecho. {prep_capturada['cambio']}", ahora)
                    else:
                        _responder(cur, workspace_id, chat_id, quien, "Hecho.", ahora)

    if draft_token:
        return _resolver_toque_borrador(
            conn, authority_conn or _authority_conn(), workspace_id, token,
            tg_user, chat_id, quien, ahora)

    return {"ok": True}


def _resolver_toque_borrador(conn, authority_conn, workspace_id, token,
                             tg_user, chat_id, quien, ahora) -> dict:
    """Resolve outside the app transaction, then enqueue its response."""
    from . import pendientes as P

    try:
        with autoridad(authority_conn) as authority_cur:
            resuelta = P.resolver_borrador(
                authority_cur, workspace_id, token, tg_user, chat_id)
    except Denegado as e:
        resuelta = None
        texto = str(e)
    else:
        texto = None

    if resuelta is not None:
        # The Unit 1A authority function persisted the terminal visible outbox
        # row in the same transaction as cancel/convert. Replays reuse it.
        return {"ok": True}

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
    return {"ok": True}


def _responder(cur, workspace_id: str, chat_id: int, quien, texto: str,
               ahora) -> None:
    """La respuesta al toque sale por la cola, como cualquier otra."""
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id, text=texto,
        recipient_membership_id=quien.membership_id, scheduled_for=ahora,
        dedupe_key=f"{workspace_id}:toque:{quien.app_user_id}:{ahora.timestamp()}",
        is_response=True, allow_split=True,
    )


def _turno(cur, quien, texto: str, workspace_id: str, chat_id: int,
           entrante_id: str | None = None) -> None:
    from datetime import datetime, timezone

    from . import pendientes as P
    from .calendario import Calendario
    from .llm import IntentRoute, desde_base

    now = datetime.now(timezone.utc)
    cal = Calendario.desde_base(cur, workspace_id)
    proveedor = desde_base(cur, workspace_id, config.llm_api_key)

    # Modificar (T3, ADR 0005 decisión 1) y "Ninguna, lo escribo" (T4,
    # decisión 4) comparten el mismo mecanismo: si esta persona, en este
    # chat, tiene una corrección abierta y todavía sin leer, este mensaje es
    # esa corrección -- no un pedido nuevo a rutear. `reclamar_modificacion_
    # abierta` la consume de un solo uso, se haya usado o no.
    #
    # Se distinguen por `herramienta`: `_SENTINEL_ACLARACION` es "Ninguna, lo
    # escribo" -- la persona declinó los botones ofrecidos, así que este
    # mensaje sigue en texto libre con el original como contexto, sin volver
    # a rutear ni a llamar a Jev (ya protegido igual por la vista previa de
    # siempre). Cualquier otro valor es un Modificar real: T4 (revisión de
    # T3) hace que esa corrección también pase por enrutador y Jev, como
    # cualquier turno, antes de llegar a `agente.responder` con el contexto
    # de la propuesta que se está corrigiendo.
    modificacion = P.reclamar_modificacion_abierta(cur, quien, chat_id, now)
    if modificacion is not None and modificacion.herramienta == _SENTINEL_ACLARACION:
        _resumir_aclaracion_ninguna(cur, quien, texto, modificacion, proveedor,
                                    cal, chat_id, workspace_id, now, entrante_id)
        return

    route = None
    last_error = None
    for _ in range(2):
        try:
            candidate = proveedor.route_intent(texto)
            if not isinstance(candidate, IntentRoute):
                raise TypeError("The provider returned an untyped route.")
            route = candidate
            break
        except Exception as exc:  # noqa: BLE001
            last_error = exc

    if route is None:
        _routing_incident(cur, quien, last_error)
        _responder(
            cur, workspace_id, chat_id, quien,
            with_no_effect_status(
                "No pude entender si querías crear una tarea. "
                "Decime de otra forma qué necesitás."), now,
        )
        return

    # Resolver antes de actuar (T3, ADR 0005 decisión 6 / ADR 0006): las
    # referencias a tarea que separó el enrutador se resuelven contra las
    # tareas activas del espacio, bajo el mismo cursor con RLS que ya tiene
    # `cur`. Sin referencias no hay nada que resolver. Sin credencial de Jev
    # (`PRISMA_OPENROUTER_API_KEY` vacía) Prisma no adivina igual: se pide
    # aclaración como si Jev hubiera fallado (decisión del usuario,
    # 2026-09-24; ver `_resolver_referencias_del_turno`).
    referencias = _resolver_referencias_del_turno(cur, quien, texto, route,
                                                   workspace_id)

    estado = _estado_inicial_aclaracion(texto, entrante_id, route, referencias,
                                        modificacion)
    _avanzar_aclaracion(cur, quien, workspace_id, chat_id, now, proveedor, cal,
                       estado)


def _iniciar_alta_guiada(cur, quien, chat_id: int, entrante_id: str | None,
                         texto: str, route_task: dict, workspace_id: str,
                         now) -> None:
    """El alta guiada de tarea nueva, tal como la arrancaba `_turno` antes de
    T4 -- extraída para que también la use la opción "Es una tarea nueva"
    del caso mixto (decisión 2, ADR 0005) sin duplicar el camino."""
    try:
        if entrante_id is None:
            raise ValueError("Task routing requires a persisted inbound message.")
        from .ingreso_tareas import start

        with cur.connection.transaction(force_rollback=False):
            outcome = start(
                cur, quien, chat_id=chat_id, source_inbound_id=entrante_id,
                source_raw_text=texto, proposals=route_task, now=now,
                buttons_first=True,
            )
            if not outcome.changed:
                raise RuntimeError("Task capture did not open a server-owned prompt.")
    except Exception as exc:  # noqa: BLE001
        _routing_incident(cur, quien, exc)
        _responder(
            cur, workspace_id, chat_id, quien,
            with_no_effect_status(
                "No pude iniciar el borrador de la tarea. "
                "Probá de nuevo en un chat privado."), now,
        )


def _resumir_aclaracion_ninguna(cur, quien, texto: str, modificacion, proveedor,
                                cal, chat_id: int, workspace_id: str, ahora,
                                entrante_id) -> None:
    """Retoma después de "Ninguna, lo escribo" (T4, decisión 4). La persona
    declinó las tareas ofrecidas para una referencia; este mensaje NO es un
    Modificar (nadie tocó Modificar, no hay vista previa de una herramienta
    que corregir) así que nunca pasa por `_bloque_modificacion` -- eso le
    diría al modelo que vuelva a llamar a una herramienta que ni siquiera es
    real (el centinela interno).

    Revisión del orquestador sobre T4: este mensaje se rutea y resuelve como
    cualquier turno -- el mismo camino que ya usa una corrección real de
    Modificar -- porque puede traer su propia referencia dicha con otras
    palabras ("es la de máq. 3"). El bloque de contexto es propio: nombra la
    referencia que quedó sin resolver y el mensaje original, y conserva lo
    que ya se había resuelto de otras referencias en ese mismo turno
    (`bloque_base` guardado en `args` al armar la pregunta)."""
    from .llm import IntentAction, IntentRoute

    args = modificacion.args
    referencia = args.get("referencia_actual", "")
    mensaje_original = args.get("mensaje", "")
    declive = (
        "# Aclaración de una referencia a tarea\n\n"
        f"La persona no encontró entre las opciones la tarea a la que se "
        f"refería con «{referencia}» en su mensaje anterior: «{mensaje_original}». "
        "Su próximo mensaje dice cuál es. Seguí con el pedido original usando "
        "esa tarea; si no queda claro, preguntá. No apliques nada sin la "
        "vista previa."
    )
    bloque_previo = args.get("bloque_base", "")
    bloque_previo = f"{bloque_previo}\n\n{declive}" if bloque_previo else declive

    route = None
    last_error = None
    for _ in range(2):
        try:
            candidate = proveedor.route_intent(texto)
            if not isinstance(candidate, IntentRoute):
                raise TypeError("The provider returned an untyped route.")
            route = candidate
            break
        except Exception as exc:  # noqa: BLE001
            last_error = exc

    if route is None:
        _routing_incident(cur, quien, last_error)
        _responder(
            cur, workspace_id, chat_id, quien,
            with_no_effect_status(
                "No pude entender si querías crear una tarea. "
                "Decime de otra forma qué necesitás."), ahora,
        )
        return

    referencias = _resolver_referencias_del_turno(cur, quien, texto, route,
                                                   workspace_id)

    estado = _estado_inicial_aclaracion(texto, entrante_id, route, referencias, None)
    estado["bloque_base"] = (
        f"{bloque_previo}\n\n{estado['bloque_base']}"
        if estado["bloque_base"] else bloque_previo)
    # Nunca arranca alta guiada acá: la persona estaba aclarando una
    # referencia, no pidiendo una tarea nueva, así que este retomo siempre
    # termina en el agente (nunca en `_iniciar_alta_guiada`), aunque el
    # enrutador haya leído este mensaje suelto como intención de alta.
    estado["route_action"] = IntentAction.NORMAL_CONVERSATION.value
    _avanzar_aclaracion(cur, quien, workspace_id, chat_id, ahora, proveedor,
                       cal, estado)


def _estado_inicial_aclaracion(texto: str, entrante_id: str | None, route,
                               referencias, modificacion) -> dict:
    """El estado que sigue `_avanzar_aclaracion` para retomar el mensaje
    original una vez resueltas -- desde el arranque o botón por botón -- las
    referencias que separó el enrutador (T4). Es lo que se guarda en
    `pending_action.args` de una fila de aclaración: nunca en logs ni
    auditoría, y siempre sin secretos (sólo lo que ya viajaba en el turno)."""
    pendientes_boton = referencias.pendientes_boton if referencias else ()
    return {
        "mensaje": texto,
        "entrante_id": entrante_id,
        "route_action": route.action.value,
        "route_task": dict(route.task),
        "resueltas": dict(referencias.resueltas_claras) if referencias else {},
        "titulos_resueltas": (
            dict(referencias.titulos_resueltas) if referencias else {}),
        "bloque_base": referencias.bloque if referencias else "",
        "hay_clara": referencias.hay_clara if referencias else False,
        "pendientes": [referencia for referencia, _candidatas in pendientes_boton],
        "candidatas": dict(pendientes_boton),
        "modificacion": (
            {"herramienta": modificacion.herramienta, "args": modificacion.args,
             "resumen": modificacion.resumen}
            if modificacion is not None else None),
    }


def _avanzar_aclaracion(cur, quien, workspace_id: str, chat_id: int, ahora,
                       proveedor, cal, estado: dict) -> None:
    """Sigue el estado de la aclaración con botones (T4, decisión 2 y 3): si
    queda una referencia ambigua con candidatas por preguntar, la siguiente
    pregunta con botones y el turno termina ahí -- una pregunta a la vez. Si
    no queda ninguna, retoma el mensaje original: a la corrección de
    Modificar si la hay, al alta guiada (b-0005, sólo sin ninguna referencia
    resuelta) o al agente, con el contexto acumulado."""
    if estado["pendientes"]:
        _preguntar_por_botones(cur, quien, workspace_id, chat_id, ahora, estado)
        return

    from .llm import IntentAction

    contexto = estado["bloque_base"] or None
    mod = estado["modificacion"]
    if mod is not None:
        from . import pendientes as P
        from .agente import responder

        modificacion = P.ModificacionAbierta(
            pending_action_id="", herramienta=mod["herramienta"],
            args=mod["args"], resumen=mod["resumen"])
        responder(cur, quien, estado["mensaje"], proveedor, cal, chat_id,
                 ahora=ahora, entrante_id=estado["entrante_id"],
                 modificacion=modificacion, contexto_referencias=contexto,
                 tareas_resueltas_claras=estado["titulos_resueltas"])
        return

    # b-0005: una referencia resuelta -- clara desde el arranque, o elegida
    # por botón, que cuenta más todavía -- a una tarea existente no es un
    # pedido de tarea nueva, aunque el enrutador haya elegido esa acción.
    if (estado["route_action"] == IntentAction.START_TASK_INTAKE.value
            and not estado["hay_clara"]):
        _iniciar_alta_guiada(cur, quien, chat_id, estado["entrante_id"],
                            estado["mensaje"], estado["route_task"],
                            workspace_id, ahora)
        return

    from .agente import responder
    responder(cur, quien, estado["mensaje"], proveedor, cal, chat_id,
             ahora=ahora, entrante_id=estado["entrante_id"],
             contexto_referencias=contexto,
             tareas_resueltas_claras=estado["titulos_resueltas"])


def _preguntar_por_botones(cur, quien, workspace_id: str, chat_id: int, ahora,
                           estado: dict) -> None:
    """Encola la pregunta con botones de la próxima referencia ambigua con
    candidatas pendiente (T4, decisión 2): una tarea por botón, más "Es una
    tarea nueva" en el caso mixto de b-0005 (sólo sin Modificar de por medio
    y con el enrutador pidiendo alta de tarea) y "Ninguna, lo escribo" al
    final, siempre."""
    from . import pendientes as P
    from .agente import VIGENCIA_PENDIENTE
    from .llm import IntentAction

    referencia = estado["pendientes"][0]
    candidatas = estado["candidatas"].get(referencia, [])
    opciones = [(c["etiqueta"], c["id"]) for c in candidatas]
    mostrar_nueva = (estado["modificacion"] is None
                     and estado["route_action"] == IntentAction.START_TASK_INTAKE.value)
    if mostrar_nueva:
        opciones.append((_ETIQUETA_NUEVA, _OPCION_NUEVA))
    opciones.append((_ETIQUETA_NINGUNA, _OPCION_NINGUNA))

    siguiente = dict(estado)
    siguiente["pendientes"] = estado["pendientes"][1:]
    siguiente["referencia_actual"] = referencia

    pregunta = f"¿A cuál te referís con «{referencia}»?"
    p = P.registrar(cur, quien, herramienta=_SENTINEL_ACLARACION, args=siguiente,
                    resumen=pregunta, vence_en=ahora + VIGENCIA_PENDIENTE,
                    campo="eleccion", opciones=opciones, chat_id=chat_id)
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id,
        recipient_membership_id=quien.membership_id, text=p.resumen,
        scheduled_for=ahora,
        dedupe_key=f"{workspace_id}:aclarar:{quien.app_user_id}:{ahora.timestamp()}",
        is_response=True, pending_action_id=p.id,
    )


def _resolver_toque_aclaracion(cur, quien, workspace_id: str, chat_id: int,
                               token: str, args: dict, ahora) -> None:
    """Alguien apretó un botón de aclaración (T4). Tres casos:

    - "Ninguna, lo escribo": no se aplica nada; se marca para que el próximo
      mensaje de esta persona en este chat, dentro de la ventana de
      Modificar, se lea como la aclaración (decisión 4).
    - "Es una tarea nueva": el caso mixto de b-0005 -- sigue al alta guiada
      con la misma propuesta que hubiera usado el enrutador.
    - Una candidata: retoma el mensaje original con esa referencia resuelta;
      si queda otra referencia ambigua, la siguiente pregunta; si no, sigue
      al agente (o a Modificar, o al alta guiada) con todo lo resuelto.
    """
    eleccion = args.get("eleccion")
    referencia = args.get("referencia_actual")

    # Auditoría (decisión 6): qué tipo de elección y, si aplica, qué tarea --
    # nunca el mensaje ni el texto de la referencia.
    registrar_auditoria(
        cur, accion="aclaracion_referencia", workspace_id=workspace_id,
        actor_app_user_id=quien.app_user_id, actor_kind="persona",
        detalle={"tipo": _TIPO_ELECCION.get(eleccion, "candidata"),
                 "tarea_id": eleccion if eleccion not in _TIPO_ELECCION else None})

    if eleccion == _OPCION_NINGUNA:
        from . import pendientes as P

        pid = P.pending_action_id_de(cur, token)
        if pid is not None:
            P.marcar_para_corregir(cur, quien, pid, chat_id, ahora)
        _responder(cur, workspace_id, chat_id, quien,
                  "¿A qué tarea te referís? Decime cuál es.", ahora)
        return

    if eleccion == _OPCION_NUEVA:
        _iniciar_alta_guiada(cur, quien, chat_id, args.get("entrante_id"),
                            args.get("mensaje", ""), args.get("route_task", {}),
                            workspace_id, ahora)
        return

    from .calendario import Calendario
    from .llm import desde_base

    estado = dict(args)
    if referencia is not None and eleccion is not None:
        candidatos = args.get("candidatas", {}).get(referencia, [])
        titulo = next((c["titulo"] for c in candidatos if c["id"] == eleccion),
                      eleccion)
        estado["resueltas"] = {**args.get("resueltas", {}), referencia: eleccion}
        estado["titulos_resueltas"] = {
            **args.get("titulos_resueltas", {}), eleccion: titulo}
        estado["hay_clara"] = True
        estado["bloque_base"] = args.get("bloque_base", "") + (
            f"\n- «{referencia}» es la tarea «{titulo}» ({eleccion}). Usá "
            "esa tarea; no la vuelvas a resolver. Si contestás algo sobre "
            "ella, nombrala por su título exacto.")

    cal = Calendario.desde_base(cur, workspace_id)
    proveedor = desde_base(cur, workspace_id, config.llm_api_key)
    _avanzar_aclaracion(cur, quien, workspace_id, chat_id, ahora, proveedor, cal,
                       estado)


@dataclass(frozen=True)
class _ReferenciasResueltas:
    """Lo que le queda al turno después de resolver, listo para pasarle a
    `agente.responder` como contexto de confianza del servidor -- o, si algo
    quedó ambiguo con candidatas reales, para preguntar con botones (T4)
    antes de llegar al agente.

    `bloque` sólo cubre lo que ya es terminal en este turno (clara, ninguna,
    ambigua sin candidatas, Jev caído): una referencia ambigua CON
    candidatas no entra ahí, entra en `pendientes_boton` -- eso es lo que
    reemplaza el texto de siempre por botones.
    """
    bloque: str
    hay_clara: bool
    resueltas_claras: dict[str, str] = field(default_factory=dict)
    # id de tarea -> título, por cada tarea de `resueltas_claras` (T5, ADR
    # 0006): lo que necesita `agente.responder` para nombrarla si la
    # respuesta visible no lo hace, sin depender de qué herramienta corrió.
    titulos_resueltas: dict[str, str] = field(default_factory=dict)
    pendientes_boton: tuple[tuple[str, list[dict]], ...] = ()


def _resolver_referencias_del_turno(cur, quien, texto: str, route,
                                    workspace_id: str) -> _ReferenciasResueltas | None:
    """Resuelve, con Jev, cada referencia a tarea que separó `route_intent`
    contra las tareas activas del espacio (T3, `aclaracion-con-botones`).

    `None` sólo cuando no hay ninguna referencia: ahí no hay nada que
    resolver y el turno sigue exactamente como antes de esta unidad, sin
    tocar la base ni la red.

    Sin credencial de Jev (`Config.openrouter_api_key` vacía) Prisma **no
    adivina** (decisión del usuario, 2026-09-24): con referencias en el
    mensaje, se trata igual que si Jev hubiera respondido `JevError` en cada
    una -- se le pide al modelo que pregunte, nunca que elija por su cuenta
    -- y se registra un incidente (sin secretos ni texto del mensaje) para
    que la falta de configuración quede visible.
    """
    if not route.trabajos:
        return None

    from . import jev as jev_modulo

    cliente_jev = jev_modulo.desde_base(config.openrouter_api_key)
    if cliente_jev is None:
        _incidente_jev_no_configurado(cur, workspace_id)
        resultados = {referencia: (None, jev_modulo.JevError(
            "No hay credencial de Jev configurada."))
            for referencia in route.trabajos}
        _auditar_resolucion(cur, quien, workspace_id, resultados)
        return _ReferenciasResueltas(
            bloque=_bloque_contexto_referencias(resultados, {}), hay_clara=False)

    from .contexto import vocabulario as vocabulario_del_equipo

    tareas = _tareas_activas(cur, workspace_id)
    por_id = {t.id: t for t in tareas}
    vocab = vocabulario_del_equipo(cur, workspace_id)

    resultados = _resolver_en_paralelo(
        cliente_jev, texto=texto, referencias=route.trabajos, tareas=tareas,
        vocabulario=vocab, quien_escribe=quien.nombre)

    _auditar_resolucion(cur, quien, workspace_id, resultados)

    # Ambigua CON candidatas (T4, decisión 2): botones, no el texto de
    # siempre. El resto -- clara, ninguna, ambigua sin candidatas, Jev caído
    # -- sigue exactamente como en T3.
    con_botones = {
        referencia for referencia, (resolucion, error) in resultados.items()
        if error is None and resolucion.tipo is jev_modulo.TipoResolucion.AMBIGUA
        and resolucion.candidatas}
    sin_boton = {referencia: par for referencia, par in resultados.items()
                if referencia not in con_botones}

    hay_clara = any(
        resolucion is not None and resolucion.tipo is jev_modulo.TipoResolucion.CLARA
        for resolucion, _error in resultados.values())
    resueltas_claras = {
        referencia: resolucion.tarea_id
        for referencia, (resolucion, error) in resultados.items()
        if error is None and resolucion.tipo is jev_modulo.TipoResolucion.CLARA}
    titulos_resueltas = {tarea_id: por_id[tarea_id].titulo
                        for tarea_id in resueltas_claras.values()
                        if tarea_id in por_id}
    pendientes_boton = tuple(
        (referencia, _candidatas_para_botones(
            por_id, resultados[referencia][0], quien.membership_id))
        for referencia in route.trabajos if referencia in con_botones)

    return _ReferenciasResueltas(
        bloque=_bloque_contexto_referencias(sin_boton, por_id),
        hay_clara=hay_clara, resueltas_claras=resueltas_claras,
        titulos_resueltas=titulos_resueltas, pendientes_boton=pendientes_boton)


def _etiqueta_boton(titulo: str, responsable: str, *, ajena: bool) -> str:
    """El texto de un botón de aclaración (T4, decisión 2): el título, y el
    primer nombre del responsable agregado con " — " sólo cuando la tarea es
    de otra persona (§5.10: "quién escribe" aporta ahí, no como pista para
    Jev). El título se trunca antes de agregar el sufijo -- el sufijo nunca
    se recorta."""
    corto = (titulo if len(titulo) <= TRUNCAR_TITULO_BOTON
             else titulo[:TRUNCAR_TITULO_BOTON - 1].rstrip() + "…")
    if not ajena or not responsable:
        return corto
    primer_nombre = responsable.split()[0]
    return f"{corto} — {primer_nombre}"


def _candidatas_para_botones(tareas_por_id: dict, resolucion, membership_id: str | None
                             ) -> list[dict]:
    """Las candidatas de una referencia ambigua, en el orden de los botones
    (T4, decisión 2): las tareas propias de quien escribe primero, después
    el resto -- dentro de cada grupo, en el orden que mandó Jev
    (`resolucion.candidatas` ya viene ordenada por probabilidad). Una
    candidata que Jev haya devuelto fuera de las tareas leídas no rompe,
    igual que en `jev.resolver_referencia_tarea`: se descarta."""
    propias, ajenas = [], []
    for cid in resolucion.candidatas:
        tarea = tareas_por_id.get(cid)
        if tarea is None:
            continue
        es_propia = (membership_id is not None
                    and tarea.responsable_membership_id == membership_id)
        etiqueta = _etiqueta_boton(tarea.titulo, tarea.responsable, ajena=not es_propia)
        item = {"id": tarea.id, "etiqueta": etiqueta, "titulo": tarea.titulo}
        (propias if es_propia else ajenas).append(item)
    return propias + ajenas


def _tareas_activas(cur, workspace_id: str) -> list:
    """Tareas activas del espacio (no `terminada` ni `cancelada`), con lo
    que necesita la receta de Jev -- título, área y responsable -- leídas
    con el mismo cursor con RLS que ya tiene el turno: nunca otra conexión,
    nunca otro espacio. `responsable_membership_id` no viaja a Jev (no entra
    en `criterio()`): sólo sirve, del lado de acá, para ordenar los botones
    (T4, decisión 2)."""
    from . import jev as jev_modulo

    cur.execute(
        """select t.id, t.titulo, a.nombre as area,
                  coalesce(i.nombre, '') as responsable,
                  t.responsable_membership_id
             from task t
             join area a on a.id = t.area_id
             left join integrante i on i.membership_id = t.responsable_membership_id
            where t.workspace_id = %s and t.estado not in ('terminada', 'cancelada')
            order by t.creado_en""",
        (workspace_id,))
    return [jev_modulo.TareaCandidata(
                id=str(f["id"]), titulo=f["titulo"], area=f["area"],
                responsable=f["responsable"],
                responsable_membership_id=(str(f["responsable_membership_id"])
                                          if f["responsable_membership_id"] else None))
            for f in cur.fetchall()]


def _resolver_en_paralelo(cliente_jev, *, texto: str, referencias, tareas,
                          vocabulario: str, quien_escribe: str | None = None) -> dict:
    """Resuelve cada referencia con Jev. Ninguna llamada toca la base, así
    que corren en un pool chico de hilos en vez de una detrás de otra (T3).

    Una referencia cuyo Jev se cae, o responde con una forma que
    `resolver_referencia_tarea` no puede leer, no corta a las demás: queda
    con su propio `JevError`, capturado acá."""
    from concurrent.futures import ThreadPoolExecutor

    from . import jev as jev_modulo

    def _una(referencia: str):
        try:
            return referencia, jev_modulo.resolver_referencia_tarea(
                cliente_jev, mensaje=texto, referencia=referencia,
                tareas=tareas, vocabulario=vocabulario,
                quien_escribe=quien_escribe), None
        except jev_modulo.JevError as exc:
            return referencia, None, exc

    resultados: dict = {}
    with ThreadPoolExecutor(max_workers=min(len(referencias), 4)) as pool:
        for referencia, resolucion, error in pool.map(_una, referencias):
            resultados[referencia] = (resolucion, error)
    return resultados


def _bloque_contexto_referencias(resultados: dict, tareas_por_id: dict) -> str:
    """Sistema de confianza del servidor (nunca texto de la persona) con lo
    que Jev resolvió de cada referencia, para que el modelo use la tarea
    correcta, pregunte, o no invente (T3; ADR 0005 decisión 6, ADR 0006)."""
    from . import jev as jev_modulo

    lineas = ["# Referencias a tareas en este mensaje", ""]
    for referencia, (resolucion, error) in resultados.items():
        if error is not None:
            lineas.append(
                f"- No se pudo resolver «{referencia}» en este momento. No "
                "adivines a qué tarea se refiere: preguntale a la persona "
                "cuál es, sin elegir por tu cuenta.")
        elif resolucion.tipo is jev_modulo.TipoResolucion.CLARA:
            tarea = tareas_por_id[resolucion.tarea_id]
            lineas.append(
                f"- «{referencia}» es la tarea «{tarea.titulo}» "
                f"({tarea.id}). Usá esa tarea; no la vuelvas a resolver. Si "
                "contestás algo sobre ella, nombrala por su título exacto.")
        elif resolucion.tipo is jev_modulo.TipoResolucion.AMBIGUA and resolucion.candidatas:
            candidatas = "; ".join(
                f"«{tareas_por_id[cid].titulo}» ({cid})"
                for cid in resolucion.candidatas if cid in tareas_por_id)
            lineas.append(
                f"- «{referencia}» puede ser más de una tarea: {candidatas}. "
                "Preguntale cuál es, sin elegir ni actuar por tu cuenta.")
        elif resolucion.tipo is jev_modulo.TipoResolucion.AMBIGUA:
            lineas.append(
                f"- «{referencia}» es ambigua y no quedó ninguna candidata "
                "para ofrecer. Preguntale a qué tarea se refiere, sin "
                "adivinar ni actuar.")
        else:  # NINGUNA
            lineas.append(
                f"- «{referencia}» no coincide con ninguna tarea activa del "
                "espacio. No inventes una tarea para eso: preguntá.")
    return "\n".join(lineas)


def _auditar_resolucion(cur, quien, workspace_id: str, resultados: dict) -> None:
    """Una entrada de auditoría por turno resuelto. Nunca el mensaje ni el
    texto de la referencia (`AGENTS.md`: nada de cuerpos de conversación en
    los registros) -- sólo el tipo de resultado y los ids de tarea o
    candidatas, por referencia."""
    detalle = {"referencias": [
        {"tipo": ("jev_error" if error is not None else resolucion.tipo.value),
         "tarea_id": resolucion.tarea_id if resolucion is not None else None,
         "candidatas": list(resolucion.candidatas) if resolucion is not None else []}
        for resolucion, error in resultados.values()
    ]}
    registrar_auditoria(
        cur, accion="resolucion_referencias", workspace_id=workspace_id,
        actor_app_user_id=quien.app_user_id, actor_kind="prisma",
        detalle=detalle)


def _incidente_jev_no_configurado(cur, workspace_id: str) -> None:
    """El mensaje traía referencias a tarea pero no hay credencial de Jev
    (`PRISMA_OPENROUTER_API_KEY`): Prisma le pide al modelo que pregunte en
    vez de adivinar (decisión del usuario, 2026-09-24), y esto queda
    registrado para que la falta de configuración no pase inadvertida. Sin
    secretos ni texto del mensaje, igual que `_routing_incident`."""
    cur.execute(
        """insert into incident (workspace_id, severidad, resumen_sanitizado)
           values (%s, 'media', %s)""",
        (workspace_id,
         "El mensaje tenía referencias a tarea, pero no hay credencial de "
         "Jev configurada (PRISMA_OPENROUTER_API_KEY)."))


def _routing_incident(cur, quien, error) -> None:
    cur.execute(
        """insert into incident (workspace_id, severidad, resumen_sanitizado)
           values (%s, 'media', %s)""",
        (quien.workspace_id,
         f"Falló el enrutamiento tipado ({type(error).__name__})."),
    )


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

    from datetime import datetime, timezone
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
        r = cliente.post(
            f"https://api.telegram.org/bot{token}/setWebhook",
            json={"url": f"{config.base_url}/telegram/{slug}",
                  "secret_token": config.webhook_secret,
                  "allowed_updates": ["message", "callback_query"]})
        resultado[slug] = r.status_code == 200 and r.json().get("ok", False)
    return resultado
