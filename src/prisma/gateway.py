"""Webhook de Telegram.

Un bot por espacio de trabajo. La ruta lleva el slug, así que el espacio queda
determinado por el canal de entrada y no hay que deducirlo del mensaje: si
alguien pertenece a dos equipos, no existe ambigüedad.

El secreto de Telegram se verifica en cada llamada. Sin eso, cualquiera que
conozca la URL podría hacerse pasar por el gateway.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from fastapi import (APIRouter, BackgroundTasks, FastAPI, Header,
                     HTTPException, Request)
from fastapi.responses import HTMLResponse

from .autoridad import (Canal, Denegado, identificar, identificar_en_espacio)
from .calendario import Calendario
from .config import config
from .db import (admin, atar_al_entrante, autoridad, conectar,
                 conectar_autoridad, espacio, registrar_auditoria)
from .despachador import (TransporteTelegram, acusar_toque, despachar,
                          mantener_chat_activo, pedido_telegram,
                          texto_error_seguro)
from .incidentes import (REFERENCIA_INBOUND_MESSAGE, REFERENCIA_PENDING_ACTION,
                         registrar_incidente)
from .ingreso_tareas import (QUESTION_CHOICE, QUESTION_CONFIRMATION,
                             QUESTION_FREE_TEXT)
from .respuesta_unica import controlar as controlar_una_respuesta
from .salida import TRUNCAR_ETIQUETA_BOTON as TRUNCAR_TITULO_BOTON
from .salida import (ETIQUETA_CANCELAR, ETIQUETA_CONFIRMAR, ICONO_CANCELAR,
                     ICONO_CONFIRMAR, ICONO_OTRA_OPCION, ICONO_TAREA,
                     cabe_en_mensaje, con_icono, enqueue_outbox,
                     etiqueta_sin_icono, etiquetas_de_tarea,
                     normalize_visible_text, truncar_etiqueta_boton,
                     with_no_effect_status)

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
# El campo de texto libre que espera el alta guiada de una tarea: no es una
# fila de `pending_action` sino un `task_intake_free_text_slot`; el centinela
# sólo nombra el tipo de pregunta abierta (`_pregunta_de`).
_SENTINEL_ALTA_TEXTO_LIBRE = "_alta_texto_libre"
# Las otras dos preguntas abiertas del alta (T9-R1c-2): una elección con
# botones (`task_intake_choice_set`) y el borrador esperando su confirmación
# (la `pending_action` de la vista previa). Tampoco son una fila de
# `pending_action` que se consuma como Modificar.
_SENTINEL_ALTA_ELECCION = "_alta_eleccion"
_SENTINEL_ALTA_CONFIRMACION = "_alta_confirmacion"
# Qué `tipo` de pregunta del alta (`ingreso_tareas.QUESTION_*`) es cada centinela.
_TIPO_DE_ALTA = {
    _SENTINEL_ALTA_TEXTO_LIBRE: QUESTION_FREE_TEXT,
    _SENTINEL_ALTA_ELECCION: QUESTION_CHOICE,
    _SENTINEL_ALTA_CONFIRMACION: QUESTION_CONFIRMATION,
}
_SENTINEL_DE_ALTA = {tipo: centinela for centinela, tipo in _TIPO_DE_ALTA.items()}
# La vista previa de un cambio que la persona pidió y espera su Confirmar
# (T9-R1d-1b): tampoco es una pregunta de `pending_action` que se consuma como
# Modificar. Su `args` lleva la herramienta real y sus argumentos.
_SENTINEL_VISTA_PREVIA = "_vista_previa_cambio"
# La elección con botones que Prisma le pidió a la persona y espera su respuesta
# (T9-R1d-1c): la aclaración "¿A cuál te referís?", la de la otra tarea de una
# dependencia, la de una herramienta con un argumento ambiguo. Su `args` lleva la
# `herramienta` real de la fila (o su centinela) y sus `argumentos`.
_SENTINEL_ELECCION = "_eleccion_abierta"
_OPCION_NINGUNA = "__ninguna__"
_OPCION_NUEVA = "__nueva__"
_ETIQUETA_NINGUNA = "Ninguna, lo escribo"
_ETIQUETA_NUEVA = "Es una tarea nueva"
_TIPO_ELECCION = {_OPCION_NINGUNA: "ninguna", _OPCION_NUEVA: "nueva"}

# El dato que una acción del menú de una tarea pide escribir (T9-R1a, ADR 0013
# regla 1): la pregunta que se hace y cómo se la describe al ruteo. Un solo
# lugar para las dos, así volver a preguntar repite exactamente la pregunta.
# Redacción pendiente de revisión de voz en T10.
PREGUNTA_DATO_EVIDENCIA_ENTREGA = "Contame brevemente qué hiciste o pasame un link."
_PREGUNTAS_DATO_MENU = {
    "terminar": PREGUNTA_DATO_EVIDENCIA_ENTREGA,
    "pedir_cambios": "¿Qué falta corregir en «{titulo}»?",
    "informar_bloqueo": "¿Cuál es la causa del bloqueo de «{titulo}»?",
    "destrabar": "¿Cómo se destrabó «{titulo}»?",
    "adjuntar_evidencia": "Contame la evidencia de «{titulo}» (o pegá el enlace).",
}
_DESCRIPCIONES_DATO_MENU = {
    "terminar": "la evidencia de la entrega de «{titulo}»",
    "pedir_cambios": "qué hay que corregir en «{titulo}»",
    "informar_bloqueo": "la causa del bloqueo de «{titulo}»",
    "destrabar": "cómo se destrabó «{titulo}»",
    "adjuntar_evidencia": "la evidencia de «{titulo}»",
}
_DESCRIPCION_DATO_MENU_GENERICA = "un dato sobre «{titulo}»"
# Redacción pendiente de revisión de voz en T10.
AVISO_DATO_DEJADO_DE_LADO = "Listo, dejé de lado {descripcion}."
# Redacción pendiente de revisión de voz en T10.
AVISO_NO_PUEDO_DATO_PENDIENTE = "Eso todavía no lo puedo hacer."
# Cuando la pregunta ya la consumió otro turno o un toque (una carrera, o un
# segundo toque tardío): se dice sin afirmar que "no cambió nada", porque el
# otro camino pudo haber dejado su propia vista previa.
# Redacción pendiente de revisión de voz en T10.
AVISO_DATO_YA_NO_PENDIENTE = (
    "Esa pregunta ya no estaba pendiente, así que no hice nada con tu mensaje.")
# Comando `dudoso`: una sola pregunta con dos botones para saber si el mensaje
# era el dato pendiente. Redacción pendiente de revisión de voz en T10.
PREGUNTA_ES_EL_DATO = "¿Esto es {descripcion}?"
ETIQUETA_ES_EL_DATO = con_icono("Sí, es eso", ICONO_CONFIRMAR)
ETIQUETA_NO_ES_EL_DATO = con_icono("No, es otra cosa", ICONO_OTRA_OPCION)
# Comando `otro_tema` con una pregunta abierta (T9-R1d-1a, ADR 0013 regla 1,
# enmienda "una sola rama de conversación abierta"): Prisma no atiende el
# mensaje; pregunta una vez, con dos botones, si se sigue con lo pendiente o se
# lo deja para ver lo otro. Redacción pendiente de revisión de voz en T10.
PREGUNTA_RAMA_ABIERTA = "Estábamos con {nombre}. ¿Seguimos con eso?"
ETIQUETA_SEGUIR_RAMA = con_icono("Seguir con eso", ICONO_CONFIRMAR)
ETIQUETA_DEJAR_RAMA = con_icono("Dejarlo y ver lo otro", ICONO_CANCELAR)
# "Seguir" tocado cuando la pregunta ya la cerró otro camino. Redacción
# pendiente de revisión de voz en T10.
AVISO_RAMA_YA_CERRADA = (
    "Esa pregunta ya no estaba pendiente, así que no hay nada que retomar.")
# El botón ya se usó, venció o es de antes de que existiera lo que hacía.
# Redacción pendiente de revisión de voz en T10.
AVISO_PEDIDO_NO_VIGENTE = (
    "Ese pedido ya no está vigente. Si sigue haciendo falta, escribime y lo "
    "vemos de nuevo.")
_ELECCION_DATO_SI = "si"
_ELECCION_DATO_SEGUIR = "seguir"
_ELECCION_DATO_DEJAR = "dejar"
# "Dejarlo y ver lo otro", y "No, es otra cosa" de `dudoso`, que hasta T9-R1d
# guardaba "no": la misma salida.
_ELECCIONES_DE_DEJAR = (_ELECCION_DATO_DEJAR, "no")

# Las otras dos preguntas que dejan el mensaje siguiente como respuesta
# (T9-R1b, ADR 0013 regla 1): la de Modificar y la de "Ninguna, lo escribo".
# La pregunta es la que sale al abrirlas, la misma al volver a hacerla. Los
# avisos son lo que se dice al dejarlas de lado. Redacción pendiente de
# revisión de voz en T10.
PREGUNTA_MODIFICAR = "¿Qué querés cambiar?"
PREGUNTA_ACLARACION_NINGUNA = "¿A qué tarea te referís? Decime cuál es."
AVISO_MODIFICACION_DEJADA = (
    "Listo, dejé de lado la corrección: la propuesta quedó sin aplicar.")
AVISO_ACLARACION_DEJADA = (
    "Listo, dejé de lado la aclaración: no hice nada con tu pedido.")
# El campo de texto libre del alta guiada de una tarea (T9-R1c-1): dejarlo
# cancela el borrador, porque el alta no sigue sin ese dato. Redacción
# pendiente de revisión de voz en T10.
AVISO_ALTA_DEJADA = "Listo, dejé de lado el borrador de la tarea{titulo}."
# El borrador ya armado y esperando confirmación (T9-R1c-2): un mensaje que
# corrige abre el selector de Modificar (T9-R1c-3), el mismo camino que su
# botón, y el selector se nombra así ante el ruteo y la pregunta de la rama.
# Redacción pendiente de revisión de voz en T10.
NOMBRE_SELECTOR_DEL_ALTA = "qué dato cambiar del borrador de la tarea nueva"
# La vista previa de un cambio que la persona pidió y espera su Confirmar
# (T9-R1d-1b, ADR 0013 regla 1, enmienda): el cambio se aplica sólo con el
# botón Confirmar. Un mensaje que dice "sí" no lo aplica: se dice y se le
# vuelve a mostrar la vista previa con sus botones. Redacción pendiente de
# revisión de voz en T10.
NOMBRE_VISTA_PREVIA = "el cambio que te mostré"
AVISO_VISTA_PREVIA_SE_CONFIRMA_CON_EL_BOTON = (
    "Ese cambio se confirma con el botón Confirmar, no con un mensaje.")
AVISO_VISTA_PREVIA_DEJADA = (
    "Listo, dejé de lado el cambio que te mostré: no apliqué nada.")
# La elección con botones que la persona no respondió (T9-R1d-1c): la de la
# aclaración de una referencia tiene su propio aviso (`AVISO_ACLARACION_DEJADA`).
# Redacción pendiente de revisión de voz en T10.
NOMBRE_ELECCION_PENDIENTE = "la elección que te pedí"
AVISO_ELECCION_DEJADA = "Listo, dejé de lado la elección: no hice nada."
# Cuánto de la vista previa que se corrige le llega al ruteo como contexto.
_LIMITE_PROPUESTA_PARA_RUTEO = 400

# `TRUNCAR_TITULO_BOTON` es un alias de `salida.TRUNCAR_ETIQUETA_BOTON`
# (importado arriba): la regla de truncado vive ahí, reusada por
# `ofrecer_opciones` (T1, ADR 0007); este nombre se conserva porque las
# pruebas de la aclaración con botones ya lo referencian.


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


# Despacho inmediato (ADR 0011, decisión 1): un `TransporteTelegram` cacheado
# por slug -- mismo criterio que `ciclo.Ciclo._transporte_de` -- para no abrir
# un cliente HTTP nuevo en cada webhook. `_transporte_de` es un nombre de
# módulo, no un método, justamente para que las pruebas lo reemplacen entero
# (mismo patrón que `_conn`/`mantener_chat_activo`) sin tocar el cliente HTTP
# real.
_transportes: dict[str, tuple[str, TransporteTelegram]] = {}


def _transporte_de(slug: str, token: str) -> TransporteTelegram:
    actual = _transportes.get(slug)
    if actual is not None and actual[0] == token:
        return actual[1]
    if actual is not None:
        actual[1].cerrar()
    nuevo = TransporteTelegram(token)
    _transportes[slug] = (token, nuevo)
    return nuevo


def _despachar_ahora(conn, slug: str) -> None:
    """Despacha lo que ya está `listo` en la cola de este espacio apenas se
    procesó un update, en vez de esperar el resto de la pasada de `escuchar`
    o el próximo tick de `servir` (`ciclo.INTERVALO_SEGUNDOS`).

    Best-effort a propósito (ADR 0011, decisión 1): nunca puede impedir el
    ACK a Telegram ni duplicar un envío -- `despachador.despachar` ya es
    seguro de llamar más de una vez (`for update skip locked`, marca-antes-
    de-enviar), y el tick de fondo (`ciclo.Ciclo.tick` /
    `Escucha.tareas_de_fondo`) sigue siendo la red de contención que
    reintenta y, si hace falta, registra el incidente de lo que esto no
    llegue a despachar. Por eso una falla acá se descarta en silencio, sin
    incidente propio -- sería redundante con ese camino.

    Nunca revierte (`conn.rollback()`): algunos caminos de
    `procesar_update` (`_activacion`, sin token) dejan su propio trabajo ya
    encolado pero todavía sin un `commit` explícito propio -- confían en
    que lo confirme el próximo `with ...conn.transaction()` sobre la misma
    conexión. Revertir acá de vuelta esa transacción ambiente borraría ese
    trabajo, que no tiene nada que ver con esta llamada. Cualquier falla
    DENTRO de `despachar` ya se aisló sola (el `with espacio(...)` de abajo
    es su propio `conn.transaction()`, que revierte sólo lo suyo al
    propagar la excepción); lo único que queda por resolver acá es dejar la
    conexión sin una transacción a medias, y la forma segura de hacerlo sin
    tirar nada por la borda es confirmar, no revertir.

    No fatal no es en silencio (regla del proyecto, revisión del padre
    sobre el commit e2a094e): una falla se imprime, con el tipo y el estado
    HTTP si lo hay (`texto_error_seguro`), nunca texto crudo, URL ni token.
    Sin incidente propio -- sería redundante con el que ya deja el tick de
    fondo si el envío de verdad se agota."""
    try:
        with conn.cursor() as cur:
            cur.execute("set role prisma_admin")
            ws = _espacio_por_slug(cur, slug)
        if ws is not None and ws["activo"]:
            workspace_id = str(ws["id"])
            token = config.token_bot(slug)
            transporte = _transporte_de(slug, token)
            ahora = datetime.now(timezone.utc)
            with espacio(conn, workspace_id) as cur:
                cal = Calendario.desde_base(cur, workspace_id)
                despachar(cur, workspace_id, transporte, cal, ahora)
    except Exception as e:  # noqa: BLE001 -- best-effort, ver docstring
        print(f"  ! el despacho inmediato no llegó a completarse "
             f"({texto_error_seguro(e)}).")
    finally:
        try:
            conn.commit()
        except Exception:  # noqa: BLE001
            pass


def _despachar_ahora_en_fondo(slug: str) -> None:
    """Corre `_despachar_ahora` como tarea de FastAPI de fondo, DESPUÉS de
    que la respuesta ya salió (R3-003, revisión 2026-09-28 sobre el commit
    e2a094e): antes, `webhook()` llamaba a `_despachar_ahora` en línea,
    ANTES del `return` -- un envío lento a Telegram bloqueaba el bucle de
    eventos entero (nada más se atendía mientras tanto) y corría el riesgo
    de que Telegram reintente la entrega del update por no recibir el ACK a
    tiempo. `BackgroundTasks` corre las tareas sync en su propio hilo
    (`anyio.to_thread.run_sync`) recién después de mandar la respuesta.

    Conexión propia (`conectar()`), nunca la `_conn()` cacheada que usa el
    resto del pedido: una tarea de fondo corre en otro hilo, y una conexión
    de psycopg no es segura de usar desde dos hilos a la vez. Se cierra
    siempre, sea o no que el despacho haya salido bien -- es de un solo
    uso."""
    try:
        conn = conectar()
    except Exception as e:  # noqa: BLE001 -- best-effort, nunca en silencio
        print(f"  ! el despacho inmediato de fondo no pudo conectar a la "
             f"base ({texto_error_seguro(e)}).")
        return
    try:
        _despachar_ahora(conn, slug)
    finally:
        try:
            conn.close()
        except Exception:  # noqa: BLE001
            pass


@router.post("/telegram/{slug}")
async def webhook(slug: str, request: Request, background_tasks: BackgroundTasks,
                  x_telegram_bot_api_secret_token: str = Header(default="")):
    if config.webhook_secret and x_telegram_bot_api_secret_token != config.webhook_secret:
        raise HTTPException(status_code=403, detail="origen no verificado")

    update = await request.json()
    resultado = procesar_update(_conn(), slug, update)
    # R3-003: se agenda, no se llama en línea -- corre DESPUÉS del ACK, en
    # un hilo aparte, para que un envío lento nunca bloquee el bucle de
    # eventos (ver `_despachar_ahora_en_fondo`).
    background_tasks.add_task(_despachar_ahora_en_fondo, slug)
    return resultado


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

    # El epígrafe de una foto o un archivo se procesa como el texto del mensaje
    # (T9-R2, H15, ADR 0013 regla 2); `adjunto` dice de qué tipo es lo que vino.
    adjunto = _tipo_de_adjunto(mensaje) if mensaje else None
    texto = (mensaje.get("text") or mensaje.get("caption") or "") if mensaje else ""
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
        except Exception as e:  # noqa: BLE001
            # Decisión del usuario, 2026-09-25: un error nunca pasa en
            # silencio. Antes se revertía y se volvía a levantar -- sin
            # incidente ni aviso, el toque simplemente se perdía. Revertir y
            # confirmar viven acá, no en `_toque`: `conn.commit()`/
            # `conn.rollback()` no se pueden llamar dentro del contexto de
            # `conn.transaction()` que abre `espacio()`, y un `return`
            # temprano de `_toque` nunca llegaría a un commit puesto
            # después. `_toque` deja la referencia a la `pending_action`
            # (si la conocía) puesta en la excepción, para que el incidente
            # quede trazable hasta ahí (T2b, trazabilidad).
            conn.rollback()
            chat_id_toque = (toque.get("message") or {}).get("chat", {}).get("id")
            pending_action_id = getattr(e, "pending_action_id", None)
            reportar_incidente_no_manejado(
                conn, workspace_id=workspace_id, chat_id=chat_id_toque,
                tg_user=tg_user, error=e, etapa=ETAPA_TOQUE_BOTON,
                referencia_tipo=(REFERENCIA_PENDING_ACTION
                                if pending_action_id else None),
                referencia_id=pending_action_id)
            return {"ok": True}
        return resultado

    # Un mensaje que no es de una persona (un aviso del servicio, como el cambio
    # de título del grupo) no trae texto ni adjunto: no hay nada que responder.
    if not texto.strip() and adjunto is None:
        return {"ok": True}

    # /start va antes de identificar: quien lo manda todavía no está vinculado.
    if adjunto is None and texto.startswith("/start"):
        try:
            return _activacion(conn, workspace_id, texto, tg_user, chat_id)
        except Exception as e:  # noqa: BLE001
            conn.rollback()
            reportar_incidente_no_manejado(
                conn, workspace_id=workspace_id, chat_id=chat_id,
                tg_user=tg_user, error=e, etapa=ETAPA_ACTIVACION)
            return {"ok": True}

    # Fase 1: identificar y dejar constancia del mensaje recibido. Se
    # confirma acá, aparte de lo que sigue (T2b, punto 2, corrección sobre
    # trazabilidad): `inbound_message` es el recibo de lo que llegó, no un
    # efecto de negocio -- si la fase 2 (interpretarlo) falla, el incidente
    # todavía tiene a qué apuntar para que el administrador abra el texto
    # exacto, en vez de perderlo junto con la reversión.
    quien = None
    entrante_id = None
    try:
        with espacio(conn, workspace_id) as cur:
            try:
                # Por la vista, que ya está acotada al espacio: si la persona
                # no es de este equipo, sencillamente no aparece.
                quien = identificar_en_espacio(cur, tg_user, workspace_id)
            except Denegado:
                # A un desconocido no se le explica por qué no se le responde.
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
                detalle={"chat_id": chat_id,
                         **({"adjunto": adjunto} if adjunto else {})})
        conn.commit()
    except Exception as e:  # noqa: BLE001
        conn.rollback()
        reportar_incidente_no_manejado(
            conn, workspace_id=workspace_id, chat_id=chat_id, tg_user=tg_user,
            error=e, etapa=ETAPA_TURNO_TEXTO)
        return {"ok": True}

    # Fase 2: interpretarlo. Esto sí puede fallar y revertirse entero sin
    # perder el recibo de la fase 1.
    try:
        with espacio(conn, workspace_id) as cur:
            # Todo lo que se encole de acá hasta el commit responde a este
            # mensaje (T9-R2): el control de una respuesta por mensaje lo ve.
            atar_al_entrante(cur, entrante_id)
            handled_intake_text = False
            privado = chat_type == "private"
            if texto.strip() and privado:
                from .ingreso_tareas import handle_active_text, open_intake_question

                # Una pregunta abierta del alta (un campo de texto libre, una
                # elección con botones o el borrador esperando su
                # confirmación) no se toma acá: `_turno` la interpreta como
                # cualquier pregunta pendiente (T9-R1c-1 y T9-R1c-2).
                if open_intake_question(cur, quien, chat_id) is None:
                    handled_intake_text = handle_active_text(
                        cur, quien, chat_id=chat_id, source_inbound_id=entrante_id,
                        source_raw_text=texto, now=datetime.now(timezone.utc),
                    ) is not None

            if texto.strip() and not handled_intake_text:
                with mantener_chat_activo(config.token_bot(slug), chat_id,
                                          chat_type=chat_type, cur=cur,
                                          workspace_id=workspace_id):
                    _turno(cur, quien, texto, workspace_id, chat_id, entrante_id,
                           alta_privada=privado)

            # Control estructural (T9-R2, ADR 0013 regla 2): un mensaje, una
            # respuesta visible, sea cual sea el camino que la encoló.
            ahora = datetime.now(timezone.utc)
            if not texto.strip():
                # Un adjunto sin epígrafe: nada que interpretar, pero la
                # persona recibe su respuesta (H15).
                _responder_sin_texto(cur, quien, workspace_id, chat_id,
                                     entrante_id, ahora, alta_privada=privado)
            controlar_una_respuesta(
                cur, quien, workspace_id=workspace_id, chat_id=chat_id,
                entrante_id=entrante_id, ahora=ahora,
                aviso_neutro=NOTICIA_NEUTRA_INCIDENTE,
                nota_de_la_respuesta=(NOTA_ADJUNTO_NO_GUARDADO
                                      if adjunto and texto.strip() else None))

        conn.commit()
    except Exception as e:  # noqa: BLE001
        # Red de contención final (decisión del usuario, 2026-09-25):
        # evidencia de la sesión real, un `UndefinedColumn` hacía que Prisma
        # saltara el mensaje entero sin ninguna respuesta ni incidente. Lo
        # que ya atajan `_turno`/`agente.responder` por su cuenta (con su
        # propio incidente y disculpa) nunca llega hasta acá; esto es sólo
        # para lo que ningún camino específico previó.
        conn.rollback()
        reportar_incidente_no_manejado(
            conn, workspace_id=workspace_id, chat_id=chat_id, tg_user=tg_user,
            error=e, etapa=ETAPA_TURNO_TEXTO,
            referencia_tipo=REFERENCIA_INBOUND_MESSAGE, referencia_id=entrante_id)
        return {"ok": True}
    # La respuesta sale por la cola, no por acá: Telegram espera un ACK rápido
    # y así el envío conserva idempotencia y auditoría.
    return {"ok": True}


# Lo que trae un mensaje de una persona además del texto (Bot API: los campos de
# `Message` con contenido). Los avisos del servicio (cambio de título, alguien
# que entra al grupo) no están: no son de una persona.
_ADJUNTOS = ("photo", "document", "audio", "voice", "video", "video_note",
             "animation", "sticker", "contact", "location", "venue", "poll",
             "dice")

# Pendiente de revisión de voz (T10).
AVISO_SIN_ADJUNTOS = ("Todavía no puedo recibir fotos, archivos ni audios. "
                      "Mandame el texto o un link.")
NOTA_ADJUNTO_NO_GUARDADO = ("Todavía no guardo adjuntos: tomé sólo el texto que "
                            "lo acompañaba.")


def _tipo_de_adjunto(mensaje: dict) -> str | None:
    """Qué adjunto trae el mensaje (foto, archivo, audio, ...), o `None`."""
    return next((tipo for tipo in _ADJUNTOS if mensaje.get(tipo)), None)


def _responder_sin_texto(cur, quien, workspace_id: str, chat_id: int,
                         entrante_id: str, ahora, *, alta_privada: bool) -> None:
    """Un adjunto sin epígrafe (T9-R2, H15): una sola respuesta que dice que
    todavía no se reciben y pide el texto o un link. Si hay una pregunta abierta
    (una sola rama, ADR 0013 regla 1), la respuesta la vuelve a hacer: el mismo
    manejo que `no puedo`, sin llamar al modelo."""
    abierta = _ver_pregunta_abierta(cur, quien, chat_id, ahora, alta=alta_privada)
    if abierta is None:
        _responder(cur, workspace_id, chat_id, quien, AVISO_SIN_ADJUNTOS, ahora)
        return
    _repreguntar(cur, quien, workspace_id, chat_id, abierta, _pregunta_de(abierta),
                 ahora, entrante_id, prefijo=f"{AVISO_SIN_ADJUNTOS} ")


def _membership_activa(cur, workspace_id: str, tg_user: int) -> dict | None:
    """La membresía activa de una cuenta de Telegram ya vinculada, con su
    nombre -- usada dos veces en `_activacion` (R2-003, revisión
    2026-09-28+2: antes cada rama tenía su propia copia de esta consulta)."""
    cur.execute(
        """select m.id as membership_id, u.nombre from membership m
             join app_user u on u.id = m.app_user_id
            where m.workspace_id = %s and u.telegram_user_id = %s
              and m.activo""",
        (workspace_id, tg_user))
    return cur.fetchone()


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
            fila = _membership_activa(cur, workspace_id, tg_user)
            if not fila:
                return {"ok": True}      # desconocido: no se le responde
            # La bienvenida cuenta como el saludo del día (pack 06 §3, T28),
            # pero el saludo se decide al DESPACHAR, no acá (decisión del
            # usuario, 2026-09-28+2: cadencias, recordatorios y avisos
            # también pueden ser el primer contacto del día, así que el único
            # punto que sabe cuál mensaje sale primero de verdad es
            # `despachador._intentar_envio`). `es_bienvenida=True` le dice al
            # despachador que reclame la reserva del día SIN anteponer nada
            # -- este texto ya es su propio saludo fijo.
            enqueue_outbox(
                cur, workspace_id=workspace_id, chat_id=chat_id,
                text=bienvenida(cur, workspace_id, fila["nombre"]),
                recipient_membership_id=str(fila["membership_id"]),
                message_type="informativo", dedupe_key=f"{workspace_id}:alta:{tg_user}",
                is_response=True, allow_split=True, es_bienvenida=True,
            )
        conn.commit()
        return {"ok": True}

    with admin(conn) as cur:
        membership_id = None
        try:
            nombre = activar(cur, workspace_id, partes[1].strip(), tg_user)
        except ActivacionInvalida as e:
            cuerpo = str(e) + " Pedile uno nuevo a quien te lo pasó."
        else:
            cuerpo = bienvenida(cur, workspace_id, nombre)
            registrar_auditoria(
                cur, accion="activacion", workspace_id=workspace_id,
                actor_kind="persona", detalle={"nombre": nombre})
            # Recién activada: hace falta su membership_id para que el
            # despachador pueda reclamarle la reserva del día como bienvenida
            # (mismo criterio que arriba).
            fila_membership = _membership_activa(cur, workspace_id, tg_user)
            membership_id = (str(fila_membership["membership_id"])
                            if fila_membership else None)

        enqueue_outbox(
            cur, workspace_id=workspace_id, chat_id=chat_id, text=cuerpo,
            recipient_membership_id=membership_id,
            message_type="informativo", dedupe_key=f"{workspace_id}:alta:{tg_user}",
            is_response=True, allow_split=True,
            es_bienvenida=membership_id is not None,
        )
    return {"ok": True}


def _registrar_toque(cur, workspace_id: str, chat_id: int, quien) -> None:
    """Deja constancia de que esta persona tocó un botón en este chat (T9-R1d-2b):
    es actividad, igual que un mensaje escrito, para la ventana que acota la
    retención de lo que Prisma inicia (`despachador.VENTANA_DE_ACTIVIDAD`). Es una
    fila de `inbound_message` sin texto ni id de mensaje de Telegram (no se le
    inventa una clasificación): el historial de la conversación sólo
    lee las que tienen texto."""
    cur.execute(
        """insert into inbound_message
             (workspace_id, chat_id, app_user_id)
           values (%s, %s, %s)""",
        (workspace_id, chat_id, quien.app_user_id))


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
    quien = None
    resuelta = None
    pending_action_id = None

    try:
        with espacio(conn, workspace_id) as cur:
            try:
                quien = identificar_en_espacio(cur, tg_user, workspace_id)
            except Denegado:
                return {"ok": True}      # desconocido: no se le responde

            _registrar_toque(cur, workspace_id, chat_id, quien)
            if intake_token:
                resultado_alta = I.resolve_choice(cur, quien, token=intake_token,
                                                  chat_id=chat_id, now=ahora)
                if resultado_alta.stale:
                    # El selector de Modificar ya usado o reemplazado: se
                    # contesta como cualquier otro toque que no está vigente.
                    _responder(cur, workspace_id, chat_id, quien,
                               AVISO_PEDIDO_NO_VIGENTE, ahora)
                return {"ok": True}

            try:
                draft_token = P.es_borrador(cur, token)
                if draft_token and I.es_modificar_de_borrador(
                        cur, quien, token, ahora):
                    # Modificar en la vista previa del borrador (T9-R1c-3): no
                    # confirma nada -- la conversión es sólo del botón Confirmar --
                    # y nunca llega a la autoridad del borrador.
                    if I.modify_from_preview(cur, quien, token=token,
                                             chat_id=chat_id, now=ahora) is None:
                        _responder(cur, workspace_id, chat_id, quien,
                                   AVISO_PEDIDO_NO_VIGENTE, ahora)
                    return {"ok": True}
                if not draft_token:
                    resuelta = P.resolver(cur, token,
                                          app_user_id=quien.app_user_id, ahora=ahora)
                    # `Resuelta` no trae el id de la `pending_action` (T2b,
                    # trazabilidad): se busca aparte, por el mismo token --
                    # la fila de `pending_action_option` sigue ahí después de
                    # resolver, sólo cambia el estado de la acción, no se
                    # borra la opción.
                    if resuelta is not None:
                        pending_action_id = P.pending_action_id_de(cur, token)
            except NoPuede as e:
                # Se le contesta, pero la acción sigue esperando a quien sí
                # puede. La frontera exterior confirma el mensaje encolado y
                # nada más.
                _responder(cur, workspace_id, chat_id, quien, str(e), ahora)
                return {"ok": True}

            if not draft_token and resuelta is None:
                # Vencida, ya usada, o de otro espacio. Para la persona es lo
                # mismo: ese pedido ya no está en pie.
                _responder(cur, workspace_id, chat_id, quien,
                           AVISO_PEDIDO_NO_VIGENTE, ahora)
            elif not draft_token and resuelta.cancelada:
                _responder(cur, workspace_id, chat_id, quien,
                           "Listo, no lo hago.", ahora)
            elif not draft_token and resuelta.modificada:
                # No se aplica nada (T3, ADR 0005 decisión 1): la fila ya
                # quedó cerrada por `resolver_pendiente`, con `herramienta`,
                # `args` y `resumen` guardados como el contexto que va a leer
                # el próximo turno de esta persona en este chat -- `_turno`
                # lo lee con `pendientes.ver_modificacion_abierta` y el ruteo
                # decide si el mensaje es la corrección (T9-R1b).
                registrar_auditoria(
                    cur, accion=f"modificar:{resuelta.herramienta}",
                    workspace_id=workspace_id, actor_app_user_id=quien.app_user_id,
                    actor_kind="persona", detalle={"args": resuelta.args, "via": "boton"})
                _responder(cur, workspace_id, chat_id, quien,
                           PREGUNTA_MODIFICAR, ahora)
            elif not draft_token:
                _seguir_resuelta(cur, quien, workspace_id, chat_id, token,
                                 resuelta, pending_action_id, ahora)
    except Exception as e:  # noqa: BLE001
        # `conn.commit()`/`conn.rollback()` no se pueden llamar todavía acá
        # adentro -- psycopg3 los rechaza mientras el contexto de
        # `conn.transaction()` de `espacio()` sigue abierto (y un `return`
        # temprano de arriba nunca llegaría a un commit puesto después del
        # `with` igual). Por eso el resguardo real -- revertir, registrar el
        # incidente y no volver a levantar -- vive en `procesar_update`,
        # como antes de T2b; lo único que se hace acá, mientras `resuelta`
        # todavía está en alcance, es dejar la referencia a la
        # `pending_action` puesta en la excepción para que ese resguardo la
        # use al registrar el incidente (T2b, trazabilidad).
        e.pending_action_id = pending_action_id
        raise

    if draft_token:
        return _resolver_toque_borrador(
            conn, authority_conn or _authority_conn(), workspace_id, token,
            tg_user, chat_id, quien, ahora)

    return {"ok": True}


def _seguir_resuelta(cur, quien, workspace_id: str, chat_id: int, token: str,
                     resuelta, pending_action_id: str | None, ahora) -> None:
    """Lo que sigue a una opción ya resuelta (`pendientes.resolver`) que no se
    cerró ni se corrige: cada centinela sigue su camino y una herramienta real
    se ejecuta con la elección completada. Lo comparten el toque (`_toque`) y la
    opción de una elección dicha por escrito (`_tomar_opcion`, T9-R1d-1c): dos
    caminos para una misma cosa, sin copiar la lista."""
    from . import herramientas as H
    from . import pendientes as P

    if resuelta.task_id:
        _responder(cur, workspace_id, chat_id, quien,
                   "Hecho. La tarea quedó comprometida.", ahora)
    elif resuelta.herramienta == _SENTINEL_ACLARACION:
        # T4: no es una herramienta real -- `H.ejecutar` la
        # rechazaría -- es la elección de un botón de aclaración.
        _resolver_toque_aclaracion(
            cur, quien, workspace_id, chat_id, token, resuelta.args, ahora)
    elif resuelta.herramienta == P.SENTINEL_OPCIONES_MODELO:
        # T1, ADR 0007: tampoco es una herramienta real -- es la
        # elección de una opción que ofreció el modelo con
        # `ofrecer_opciones`. No vuelve a llamarla: retoma la
        # conversación con el modelo.
        _resolver_toque_opcion_modelo(
            cur, quien, workspace_id, chat_id, resuelta.args, ahora)
    elif resuelta.herramienta == P.SENTINEL_MENU_TAREA:
        # T2, ADR 0007 §4.6: el menú de acciones de una tarea.
        # Cada opción es una acción calculada por código, no una
        # herramienta -- `_resolver_toque_menu_tarea` la
        # despacha. Se le pasa el id de la `pending_action` ya
        # resuelta (T2b, trazabilidad): si algo revienta más
        # adelante, el incidente apunta a esta fila.
        _resolver_toque_menu_tarea(
            cur, quien, workspace_id, chat_id, resuelta.args, ahora,
            pending_action_id=pending_action_id)
    elif resuelta.herramienta == P.SENTINEL_RESPUESTA_DATO_MENU:
        # T9-R1a-2 y T9-R1d: los botones de `dudoso` y de la
        # pregunta de la rama (`otro_tema`) sobre una pregunta
        # pendiente que sigue abierta.
        _resolver_toque_respuesta_dato_menu(
            cur, quien, workspace_id, chat_id, resuelta.args, ahora)
    elif resuelta.herramienta == P.SENTINEL_DATO_MENU_TAREA:
        # T2: la elección, con botones, de con cuál otra tarea se
        # declara una dependencia -- la única forma de este
        # sentinel que se resuelve por toque (la otra, un dato en
        # texto libre, la retoma `_turno` cuando llega el mensaje).
        _resolver_toque_dato_menu_tarea(
            cur, quien, workspace_id, chat_id, resuelta.args, ahora,
            pending_action_id=pending_action_id)
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
            # La situación cambió entre la vista previa y el
            # toque (ADR 0005, decisión 1): no se aplica nada, se
            # arma una vista previa nueva y una acción pendiente
            # nueva. Sigue siendo la vista previa de una
            # herramienta que escribe, así que conserva sus tres
            # botones (T3).
            nueva = P.registrar(
                cur, quien, herramienta=e.herramienta,
                args=e.argumentos, resumen=e.resumen,
                vence_en=ahora + VIGENCIA_PENDIENTE, chat_id=chat_id,
                huella=e.huella,
                opciones=[(ETIQUETA_CONFIRMAR, True), ("Modificar", "modificar"),
                         (ETIQUETA_CANCELAR, False)])
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
            # `aprobar_tarea` (ADR 0008, hallazgo 5 de sesión 2
            # por Telegram) siempre escribe la aprobación, aun
            # cuando `cerrada` sea `False` -- a diferencia de
            # `actualizar_estado`/`preparar` en general, donde
            # `cerrada`/`iniciada` en `False` significa que
            # `preparar` frenó ANTES de escribir nada. Sin este
            # distingo, el rechazo genérico de abajo auditaría la
            # aprobación como `herramienta_rechazada` y nunca le
            # confirmaría a quien aprobó que sí quedó registrada.
            aprobacion_registrada = (
                resuelta.herramienta == "aprobar_tarea"
                and isinstance(resultado, dict)
                and resultado.get("aprobada"))
            if not aprobacion_registrada and isinstance(resultado, dict) and (
                    resultado.get("error")
                    or resultado.get("cerrada") is False
                    or resultado.get("iniciada") is False
                    or resultado.get("en_revision") is False):
                # La preparación se corrió de nuevo al confirmar
                # (`ya_confirmada=True`) y encontró un
                # impedimento de negocio -- la situación cambió
                # entre la vista previa y el toque (sin llegar a
                # `EstadoCambio`, porque la huella puede seguir
                # coincidiendo aunque el estado ya no admita la
                # transición), o el propio handler encontró la
                # misma condición al aplicar. Mismo defecto de
                # fondo que el corregido en `agente._ejecutar_una`
                # (banco b-0005-a): nunca auditar como ejecutado
                # (`herramienta:<nombre>`) lo que no escribió
                # nada, y nunca decirle "Hecho" a la persona por
                # algo que no pasó. Mismo mensaje específico que
                # ya usa `_mensaje_resultado_menu` para el mismo
                # tipo de rechazo, en vez de un genérico "No se
                # aplicó el cambio.".
                registrar_auditoria(
                    cur, accion=f"herramienta_rechazada:{resuelta.herramienta}",
                    workspace_id=workspace_id,
                    actor_app_user_id=quien.app_user_id,
                    actor_kind="persona",
                    detalle={"args": resuelta.args, "via": "boton",
                            "rechazo": resultado})
                _responder(
                    cur, workspace_id, chat_id, quien,
                    resultado.get("falta") or resultado.get("error")
                    or "No se aplicó el cambio.", ahora)
            else:
                registrar_auditoria(
                    cur, accion=f"herramienta:{resuelta.herramienta}",
                    workspace_id=workspace_id,
                    actor_app_user_id=quien.app_user_id,
                    actor_kind="persona",
                    detalle={"args": resuelta.args, "via": "boton"})
                if isinstance(resultado, dict) and resultado.get("draft_id"):
                    if resultado.get("pendiente_revision"):
                        texto = ("Guardé el borrador y envié la vista previa "
                                 "a quien puede confirmarlo.")
                    else:
                        texto = ("Guardé el pedido como borrador; todavía "
                                 "está incompleto.")
                    _responder(cur, workspace_id, chat_id, quien, texto, ahora)
                elif aprobacion_registrada:
                    # Hallazgo 5, sesión 2 por Telegram,
                    # 2026-09-27: acá el bot decía "Hecho. Tarea:
                    # X · Estado actual: En revisión · se aprueba
                    # el trabajo" -- la vista previa, no lo que
                    # pasó. El resultado, en pasado, corto.
                    titulo = resultado.get("titulo") or "esa tarea"
                    if resultado.get("cerrada"):
                        texto = f"Listo: aprobaste «{titulo}». Quedó terminada."
                    else:
                        texto = (f"Listo: aprobaste «{titulo}»; para cerrarla "
                                 f"todavía: {resultado.get('falta')}")
                    _responder(cur, workspace_id, chat_id, quien, texto, ahora)
                elif (resuelta.herramienta == "actualizar_estado"
                      and isinstance(resultado, dict) and "estado" in resultado):
                    # Mismo hallazgo: acá decía "... Estado actual:
                    # Asignada · Nuevo estado: En revisión" -- el
                    # estado VIEJO, después de aplicar el cambio.
                    # `_actualizar_estado` no devuelve el título
                    # (otros tests comparan su resultado con
                    # `{"estado": ...}` exacto), así que se lee acá.
                    cur.execute(
                        "select titulo from task where id = %s",
                        (resuelta.args.get("tarea_id"),))
                    fila_tarea = cur.fetchone()
                    titulo = fila_tarea["titulo"] if fila_tarea else "esa tarea"
                    _responder(
                        cur, workspace_id, chat_id, quien,
                        f"Listo: «{titulo}» pasó a "
                        f"{H._estado_legible(resultado['estado'])}.", ahora)
                elif prep_capturada.get("cambio"):
                    # El recibo cuenta qué cambió, no un "Hecho."
                    # solo (T2, punto 3): reusa la descripción
                    # que ya se había mostrado en la vista
                    # previa, porque la huella coincidió -- el
                    # estado sigue siendo ese. Sigue así para
                    # cualquier otra herramienta del menú: sólo
                    # `aprobar_tarea` y `actualizar_estado` (arriba)
                    # tienen fraseo específico del resultado.
                    _responder(cur, workspace_id, chat_id, quien,
                              f"Hecho. {prep_capturada['cambio']}", ahora)
                else:
                    _responder(cur, workspace_id, chat_id, quien, "Hecho.", ahora)


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
               ahora, bloque: str | None = None, *,
               grupo: str | None = None) -> None:
    """La respuesta al toque sale por la cola, como cualquier otra. Con `bloque`
    (lo que la persona tenía, para copiarlo con un toque) el texto termina en él
    y no se parte. Con `grupo`, es una parte de una respuesta que se encola en
    varias llamadas (`enqueue_outbox`, `grupo_respuesta`)."""
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id, text=texto,
        recipient_membership_id=quien.membership_id, scheduled_for=ahora,
        dedupe_key=f"{workspace_id}:toque:{quien.app_user_id}:{ahora.timestamp()}",
        is_response=True, allow_split=bloque is None, bloque_copiable=bloque,
        grupo_respuesta=grupo,
    )


def _turno(cur, quien, texto: str, workspace_id: str, chat_id: int,
           entrante_id: str | None = None, *, alta_privada: bool = False) -> None:
    from datetime import datetime, timezone

    from .calendario import Calendario
    from .llm import desde_base

    now = datetime.now(timezone.utc)
    cal = Calendario.desde_base(cur, workspace_id)
    proveedor = desde_base(cur, workspace_id, config)

    # Estas preguntas dejan el mensaje siguiente como su respuesta: el dato que
    # pidió una acción del menú (la causa de un bloqueo, su resolución, la
    # evidencia), Modificar (T3, ADR 0005 decisión 1: "¿Qué querés cambiar?"),
    # "Ninguna, lo escribo" (T4, decisión 4) y las del alta guiada (T9-R1c: un
    # campo de texto libre, una elección con botones, el borrador esperando
    # su confirmación; sólo en un chat privado: `alta_privada`) y la vista
    # previa de un cambio que la persona pidió y espera su Confirmar
    # (T9-R1d-1b; la precedencia está en `_ver_pregunta_abierta`). Ninguna se
    # toma ya sin mirar el mensaje (T9-R1a, T9-R1b y T9-R1c, ADR 0013 regla 1):
    # se lee la pregunta abierta sin consumirla y el ruteo tipado la relaciona
    # con el mensaje. Con una pregunta abierta, `otro_tema` no se atiende
    # (T9-R1d, enmienda de la regla 1): sólo sigue por el camino normal, con la
    # ruta ya obtenida, una pregunta que otro turno ya consumió.
    route = None
    abierta = _ver_pregunta_abierta(cur, quien, chat_id, now, alta=alta_privada)
    if abierta is not None:
        route = _atender_pregunta_pendiente(cur, quien, texto, abierta, proveedor,
                                            cal, chat_id, workspace_id, now,
                                            entrante_id)
        if route is None:
            return

    if route is None:
        route, last_error = _rutear(proveedor, texto)
        if route is None:
            _avisar_ruteo_caido(cur, quien, last_error, workspace_id, chat_id, now)
            return

    _seguir_camino_normal(cur, quien, texto, route, proveedor, cal, chat_id,
                          workspace_id, now, entrante_id)


def _seguir_camino_normal(cur, quien, texto: str, route, proveedor, cal,
                          chat_id: int, workspace_id: str, ahora,
                          entrante_id: str | None, *, modificacion=None,
                          no_proponer: dict | None = None) -> None:
    """El camino de siempre para un mensaje ya ruteado: resolver las
    referencias, y aclarar con botones, dar el alta guiada o responder.

    `no_proponer`, si viene, es lo que la persona acaba de dejar de lado
    (`_lo_dejado_de`): el responder no lo vuelve a proponer en este turno
    (T9-R1d-1a-fix, banco b-0020-f: las instrucciones solas no alcanzan)."""
    # Resolver antes de actuar (T3, ADR 0005 decisión 6 / ADR 0006): las
    # referencias a tarea que separó el enrutador se resuelven contra las
    # tareas activas del espacio, bajo el mismo cursor con RLS que ya tiene
    # `cur`. Sin referencias no hay nada que resolver. Sin credencial de Jev
    # (`PRISMA_OPENROUTER_API_KEY` vacía) Prisma no adivina igual: se pide
    # aclaración como si Jev hubiera fallado (decisión del usuario,
    # 2026-09-24; ver `_resolver_referencias_del_turno`).
    #
    # Contestar una pregunta pendiente no abre una aclaración (T9-R1b-2, ADR
    # 0013 regla 1, banco b-0020-b): con `modificacion` la tarea de la
    # propuesta es el sujeto por defecto y Jev sigue resolviendo las
    # referencias (una corrección puede cambiar de tarea), pero sólo una
    # resolución CLARA lo cambia; una ambigua o sin resolver ("el variador
    # roto") se ignora, sin botones ni texto.
    referencias = _resolver_referencias_del_turno(
        cur, quien, texto, route, workspace_id,
        solo_claras=modificacion is not None)

    estado = _estado_inicial_aclaracion(texto, entrante_id, route, referencias,
                                        modificacion)
    estado["no_proponer"] = no_proponer
    _avanzar_aclaracion(cur, quien, workspace_id, chat_id, ahora, proveedor, cal,
                       estado)


def _rutear(proveedor, texto: str, pendiente: str | None = None):
    """El ruteo tipado con dos intentos: (ruta, None), o (None, último
    error) si los dos fallan. `pendiente` es la descripción de la pregunta
    abierta, si la hay (T9-R1a)."""
    from .llm import IntentRoute

    last_error = None
    for _ in range(2):
        try:
            candidate = (proveedor.route_intent(texto) if pendiente is None
                         else proveedor.route_intent(texto, pendiente=pendiente))
            if not isinstance(candidate, IntentRoute):
                raise TypeError("The provider returned an untyped route.")
            return candidate, None
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    return None, last_error


def _avisar_ruteo_caido(cur, quien, error, workspace_id: str, chat_id: int,
                        ahora) -> None:
    """El ruteo falló dos veces: incidente y el aviso de siempre, sin efecto."""
    _routing_incident(cur, quien, error)
    _responder(
        cur, workspace_id, chat_id, quien,
        with_no_effect_status(
            "No pude entender si querías crear una tarea. "
            "Decime de otra forma qué necesitás."), ahora,
    )


def _pregunta_dato_menu(accion: str | None, titulo: str) -> str:
    """La pregunta del dato que pide una acción del menú, la misma al pedirlo
    y al volver a pedirlo."""
    plantilla = _PREGUNTAS_DATO_MENU.get(accion or "")
    if plantilla is None:
        plantilla = _PREGUNTAS_DATO_MENU["adjuntar_evidencia"]
    return plantilla.format(titulo=titulo)


def _descripcion_dato_menu(args: dict) -> str:
    """Descripción corta del dato pendiente, para el ruteo: sale de la acción
    y el título guardados al abrir la pregunta."""
    plantilla = _DESCRIPCIONES_DATO_MENU.get(
        args.get("accion") or "", _DESCRIPCION_DATO_MENU_GENERICA)
    return plantilla.format(titulo=args.get("titulo", ""))


@dataclass(frozen=True)
class _Pregunta:
    """Lo que hace falta saber de una pregunta pendiente para tratarla igual
    sea cual sea (T9-R1b, ADR 0013 regla 1): es el adaptador mínimo de cada
    tipo. Todo lo demás (el ruteo, los siete comandos, los botones) es común.
    `nombre` es la frase corta con que se la nombra en las preguntas con
    botones ("¿Esto es …?", "Estábamos con …"); `para_ruteo` es lo que recibe el
    modelo; `pregunta` es la que se le hizo a la persona, la misma al volver a
    hacerla; `dejada` es lo que se dice al dejarla de lado. `corrige_responde`
    dice si un mensaje que corrige algo anterior es la respuesta: en una
    corrección, sí; en un dato del menú no hay propuesta anterior que
    corregir, y queda como `dudoso`. `corrige_abre_selector` dice que en ese
    tipo el mensaje que corrige abre el selector "qué dato cambiar" (el borrador
    ya armado, T9-R1c-3): el mismo camino que su botón Modificar, sin aplicar
    nada. `corrige_modifica` dice que en ese tipo el
    mensaje que corrige es el de Modificar sin haber tocado el botón (la vista
    previa de un cambio): la propuesta se cierra como Modificar y el mensaje es
    la corrección."""
    nombre: str
    para_ruteo: str
    pregunta: str
    dejada: str
    corrige_responde: bool
    corrige_abre_selector: bool = False
    corrige_modifica: bool = False


def _para_ruteo(descripcion: str, pregunta: str) -> str:
    """Lo que recibe el ruteo como pregunta pendiente: la descripción y la
    pregunta tal como se le hizo a la persona. Con sólo la descripción, el
    banco real (b-0019-d) marcó un link suelto como `dudoso` porque el modelo
    no veía que se había pedido un link (ADR 0013 regla 1: se interpreta
    contra la pregunta real)."""
    return f"{descripcion} (la pregunta que se le hizo fue: «{pregunta}»)"


# Qué herramienta produce, sobre qué id de sus argumentos, cada acción del menú
# que pide un dato (`_resumir_dato_menu_tarea`): lo que la persona deja de lado
# al soltar esa pregunta.
_HERRAMIENTA_DE_DATO_MENU = {
    "informar_bloqueo": ("registrar_bloqueo", "tarea_id"),
    "destrabar": ("resolver_bloqueo", "bloqueo_id"),
    "adjuntar_evidencia": ("adjuntar_evidencia", "tarea_id"),
    "terminar": ("actualizar_estado", "tarea_id"),
    "pedir_cambios": ("pedir_cambios_tarea", "tarea_id"),
}


# Los argumentos que identifican sobre qué actúa una herramienta que escribe.
# `_no_proponer_de` toma el primero que esté presente, en este orden de
# preferencia. Hoy ninguna herramienta trae dos de estos ids a la vez, así que
# el orden no decide nada: `crear_dependencia` usa `origen_tarea_id` y
# `destino_tarea_id` (ninguno está en la lista: sin guarda) y
# `quitar_dependencia` sólo `dependencia_id`. Una herramienta nueva con dos de
# estos ids tomaría el primero de la lista: revisar el orden al agregarla.
_CAMPOS_DE_ID = ("tarea_id", "bloqueo_id", "dependencia_id")


def _no_proponer_de(abierta) -> dict | None:
    """La guarda de "Dejarlo y ver lo otro" (T9-R1d-1a-fix, ADR 0013 regla 1):
    la herramienta y el id que la pregunta que se deja de lado tenía
    pendientes, como datos (`NoProponer` de `agente`, guardado como dict para
    que viaje en el estado de la aclaración). Modificar: la herramienta de la
    propuesta y su id (igual la vista previa de un cambio, T9-R1d-1b); dato del
    menú: la herramienta a la que lleva la acción.
    "Ninguna, lo escribo" y las preguntas del alta no tienen tarea conocida:
    sin guarda."""
    from . import pendientes as P

    if abierta.herramienta == _SENTINEL_ELECCION:
        # La elección con botones (T9-R1d-1c) guarda la fila que la abrió: se
        # trata como esa pregunta -- la aclaración y la dependencia no tienen
        # guarda; una herramienta, la de sus argumentos si ya llevan el id.
        return _no_proponer_de(_fila_de_la_eleccion(abierta))
    if abierta.herramienta == _SENTINEL_ACLARACION or (
            abierta.herramienta in _TIPO_DE_ALTA):
        return None
    args = abierta.args
    if abierta.herramienta == P.SENTINEL_DATO_MENU_TAREA:
        herramienta, campo = _HERRAMIENTA_DE_DATO_MENU.get(
            args.get("accion"), (None, None))
    else:
        # Modificar, o la vista previa de un cambio (T9-R1d-1b, que guarda su
        # herramienta y sus argumentos en `args`): el id de la propuesta es el
        # de su herramienta -- `bloqueo_id` en `resolver_bloqueo`,
        # `dependencia_id` al quitar una dependencia, `tarea_id` en el resto.
        # Una herramienta con dos ids (`crear_dependencia`) o ninguno conocido
        # queda sin guarda.
        if abierta.herramienta == _SENTINEL_VISTA_PREVIA:
            herramienta, args = args["herramienta"], args["argumentos"]
        else:
            herramienta = abierta.herramienta
        campo = next((c for c in _CAMPOS_DE_ID if c in args), None)
    valor = args.get(campo) if campo else None
    if not herramienta or valor is None:
        return None
    return {"herramienta": herramienta, "campo": campo, "valor": str(valor)}


def _lo_dejado_de(abierta) -> dict:
    """Todo lo que el responder tiene que saber de la pregunta que la persona
    acaba de dejar de lado para ver otra cosa (T9-R2b, banco real b-0021-i),
    como datos (`NoProponer` de `agente`; dict para que viaje en el estado de la
    aclaración): la guarda de herramienta e id de `_no_proponer_de` cuando la
    hay, `dejado` (cómo se la nombra ante el modelo, que en ese turno no ve el
    aviso "dejé de lado" ni la pregunta en el historial) y `alta`, si era una
    pregunta del alta: sin herramienta ni id, lo que no se puede volver a
    proponer es armar una tarea nueva."""
    guarda = _no_proponer_de(abierta) or {
        "herramienta": None, "campo": None, "valor": None}
    return {**guarda, "dejado": _pregunta_de(abierta).nombre,
            "alta": abierta.herramienta in _TIPO_DE_ALTA}


def _pregunta_de(abierta) -> _Pregunta:
    """El adaptador de la pregunta abierta, según lo que la abrió: el dato de
    una acción del menú (`_PREGUNTAS_DATO_MENU`, por acción), "Ninguna, lo
    escribo" (el pedido original y la referencia, guardados en sus `args`), una
    pregunta del alta guiada (un campo de texto libre, una elección con
    botones o el borrador esperando confirmación; su `resumen` es la pregunta
    que se hizo), la vista previa de un cambio que la persona pidió (su
    `resumen` es la vista previa) o, con cualquier otra `herramienta`, una
    corrección de Modificar (la vista previa que se corrige es su `resumen`)."""
    from . import pendientes as P

    args = abierta.args
    if abierta.herramienta in _TIPO_DE_ALTA:
        return _pregunta_del_alta(abierta)
    if abierta.herramienta == _SENTINEL_ELECCION:
        return _pregunta_de_la_eleccion(abierta)
    if abierta.herramienta == _SENTINEL_VISTA_PREVIA:
        propuesta = abierta.resumen[:_LIMITE_PROPUESTA_PARA_RUTEO]
        descripcion = (
            "la vista previa de un cambio que la persona pidió, con los "
            "botones Confirmar, Modificar y Cancelar: el cambio se aplica sólo "
            f"con Confirmar. La vista previa dice: «{propuesta}»")
        return _Pregunta(
            nombre=NOMBRE_VISTA_PREVIA,
            para_ruteo=_para_ruteo(descripcion, "¿Lo confirmás?"),
            pregunta=abierta.resumen, dejada=AVISO_VISTA_PREVIA_DEJADA,
            corrige_responde=False, corrige_modifica=True)
    if abierta.herramienta == P.SENTINEL_DATO_MENU_TAREA:
        descripcion = _descripcion_dato_menu(args)
        pregunta = _pregunta_dato_menu(args.get("accion"), args.get("titulo", ""))
        return _Pregunta(
            nombre=descripcion, para_ruteo=_para_ruteo(descripcion, pregunta),
            pregunta=pregunta,
            dejada=AVISO_DATO_DEJADO_DE_LADO.format(descripcion=descripcion),
            corrige_responde=False)
    if abierta.herramienta == _SENTINEL_ACLARACION:
        referencia = args.get("referencia_actual", "")
        descripcion = (f"a qué tarea se refería con «{referencia}» en su "
                       f"mensaje «{args.get('mensaje', '')}»")
        return _Pregunta(
            nombre=f"la tarea a la que te referías con «{referencia}»",
            para_ruteo=_para_ruteo(descripcion, PREGUNTA_ACLARACION_NINGUNA),
            pregunta=PREGUNTA_ACLARACION_NINGUNA,
            dejada=AVISO_ACLARACION_DEJADA, corrige_responde=True)
    propuesta = abierta.resumen[:_LIMITE_PROPUESTA_PARA_RUTEO]
    descripcion = f"qué cambiar de la propuesta que se le mostró: «{propuesta}»"
    return _Pregunta(
        nombre="la corrección de la propuesta",
        para_ruteo=_para_ruteo(descripcion, PREGUNTA_MODIFICAR),
        pregunta=PREGUNTA_MODIFICAR, dejada=AVISO_MODIFICACION_DEJADA,
        corrige_responde=True)


def _fila_de_la_eleccion(abierta):
    """La pregunta abierta tal como la guarda la fila que abrió la elección:
    su `herramienta` (real o un centinela), sus `argumentos` y su resumen."""
    from . import pendientes as P

    return P.ModificacionAbierta(
        pregunta_id=abierta.pregunta_id, herramienta=abierta.args["herramienta"],
        args=abierta.args["argumentos"], resumen=abierta.resumen)


def _pregunta_de_la_eleccion(abierta) -> _Pregunta:
    """El adaptador de la elección con botones (T9-R1d-1c). Al ruteo le llegan
    la pregunta y sus opciones: el mensaje responde sólo si dice una de ellas.
    `corrige` no es la respuesta: lo decide la persona con los botones de
    `dudoso`. Dejarla de lado la cancela sin hacer nada."""
    from . import pendientes as P

    fila = _fila_de_la_eleccion(abierta)
    opciones = ", ".join(f"«{o}»" for o in abierta.args.get("opciones") or [])
    con_opciones = f"{abierta.resumen} (las opciones son: {opciones})"
    if fila.herramienta == _SENTINEL_ACLARACION:
        referencia = fila.args.get("referencia_actual", "")
        nombre = f"la tarea a la que te referías con «{referencia}»"
        descripcion = (f"a qué tarea se refería con «{referencia}» en su "
                       f"mensaje «{fila.args.get('mensaje', '')}»")
        dejada = AVISO_ACLARACION_DEJADA
    elif fila.herramienta == P.SENTINEL_DATO_MENU_TAREA:
        nombre = f"la elección de la otra tarea para «{fila.args.get('titulo', '')}»"
        descripcion = f"{nombre}, una pregunta con botones"
        dejada = AVISO_ELECCION_DEJADA
    else:
        nombre = NOMBRE_ELECCION_PENDIENTE
        descripcion = f"{nombre}, una pregunta con botones"
        dejada = AVISO_ELECCION_DEJADA
    return _Pregunta(
        nombre=nombre, para_ruteo=_para_ruteo(descripcion, con_opciones),
        pregunta=abierta.resumen, dejada=dejada, corrige_responde=False)


def _pregunta_del_alta(abierta) -> _Pregunta:
    """El adaptador de las tres preguntas del alta guiada (T9-R1c). Dejarlas de
    lado cancela el borrador: sin ese dato, esa elección o esa confirmación el
    alta no sigue."""
    from .ingreso_tareas import FREE_TEXT_NAMES, MODIFY_PICKER_KIND

    args = abierta.args
    titulo = args.get("titulo")
    dejada = AVISO_ALTA_DEJADA.format(titulo=f" «{titulo}»" if titulo else "")
    if abierta.herramienta == _SENTINEL_ALTA_TEXTO_LIBRE:
        # Un campo de texto libre sin nombre es un defecto del alta: falla
        # fuerte, no se inventa un nombre.
        nombre = f"{FREE_TEXT_NAMES[args['campo']]} de la tarea nueva"
        descripcion = f"{nombre}, un dato del alta guiada que se le pidió"
        corrige_abre_selector = False
    elif abierta.herramienta == _SENTINEL_ALTA_ELECCION:
        # Una elección sin campo (la de "ya hay un borrador en curso") no tiene
        # nombre de campo y se nombra en general.
        campo = FREE_TEXT_NAMES.get(args.get("campo"))
        nombre = (f"la elección sobre {campo} de la tarea nueva" if campo
                  else "la elección pendiente de la tarea nueva")
        if args.get("clase") == MODIFY_PICKER_KIND:
            nombre = NOMBRE_SELECTOR_DEL_ALTA
        descripcion = f"{nombre}, una pregunta con botones del alta guiada"
        opciones = args.get("opciones") or []
        if opciones:
            descripcion += (" (las opciones son: "
                            + ", ".join(f"«{o}»" for o in opciones) + ")")
        corrige_abre_selector = False
    else:
        nombre = "la confirmación del borrador de la tarea nueva"
        descripcion = (f"{nombre}: se le mostró el resumen del borrador con los "
                       "botones Confirmar, Modificar y Cancelar, y la tarea se "
                       "crea sólo con Confirmar")
        corrige_abre_selector = True
    return _Pregunta(
        nombre=nombre, para_ruteo=_para_ruteo(descripcion, abierta.resumen),
        pregunta=abierta.resumen, dejada=dejada, corrige_responde=False,
        corrige_abre_selector=corrige_abre_selector)


def _atender_pregunta_pendiente(cur, quien, texto: str, abierta, proveedor, cal,
                                chat_id: int, workspace_id: str, ahora,
                                entrante_id: str | None = None):
    """Interpreta el mensaje que llega con una pregunta abierta (T9-R1a y
    T9-R1b, ADR 0013 regla 1): el ruteo tipado devuelve un comando de la lista
    cerrada y acá hay un manejo determinista por comando, igual para todos los
    tipos de pregunta (`_pregunta_de`), sean una fila de `pending_action` o una
    pregunta del alta guiada (T9-R1c). Todo camino deja
    exactamente una respuesta visible.

    Devuelve `None` cuando el turno ya terminó, o la ruta ya obtenida cuando
    el mensaje sigue por el camino normal (una pregunta que otro turno
    consumió antes) -- sin un segundo ruteo. La pregunta se consume sólo con
    `responde` (y `corrige`, si en ese tipo corregir es responder) y
    `cancela`, o con los botones que dejan `dudoso` y `otro_tema`; si el
    ruteo falla, queda abierta."""
    from .llm import RespectoPendiente

    pregunta = _pregunta_de(abierta)
    route, error = _rutear(proveedor, texto, pendiente=pregunta.para_ruteo)
    if route is None:
        _avisar_ruteo_caido(cur, quien, error, workspace_id, chat_id, ahora)
        return None

    comando = route.respecto_pendiente
    if comando is RespectoPendiente.RESPONDE or (
            comando is RespectoPendiente.CORRIGE and pregunta.corrige_responde):
        if _consumir_pregunta(cur, quien, abierta, ahora):
            _seguir_con_la_respuesta(cur, quien, texto, abierta, route, proveedor,
                                     cal, chat_id, workspace_id, ahora,
                                     entrante_id)
            return None
        return route
    if comando is RespectoPendiente.CORRIGE and pregunta.corrige_modifica:
        # El camino de Modificar sin haber tocado el botón: la vista previa se
        # cierra sin aplicar nada y este mensaje es la corrección. Si otro
        # camino ya la había cerrado, el mensaje sigue por el camino normal.
        modificacion = _cerrar_como_modificar(cur, quien, abierta, ahora)
        if modificacion is None:
            return route
        _seguir_camino_normal(cur, quien, texto, route, proveedor, cal, chat_id,
                              workspace_id, ahora, entrante_id,
                              modificacion=modificacion)
        return None
    if comando is RespectoPendiente.CORRIGE and pregunta.corrige_abre_selector:
        # Corregir el borrador ya armado (T9-R1c-3): lo mismo que tocar
        # Modificar. La vista previa se cierra sin aplicar nada y sigue el
        # selector, dentro de la misma rama. Si otro camino ya la había
        # cerrado, el mensaje sigue por el camino normal.
        from .ingreso_tareas import open_modify_picker

        if open_modify_picker(cur, quien, abierta.pregunta_id, ahora,
                              via="texto") is None:
            return route
        return None
    if comando is RespectoPendiente.CANCELA:
        _dejar_pregunta_pendiente(cur, quien, workspace_id, chat_id, abierta,
                                  ahora)
        return None
    if comando is RespectoPendiente.OTRO_TEMA:
        # Una sola rama abierta (T9-R1d, enmienda de la regla 1): el mensaje
        # no se atiende hasta que la persona decida qué pasa con lo pendiente.
        _preguntar_por_la_rama(cur, quien, workspace_id, chat_id, texto, abierta,
                               entrante_id, ahora)
        return None
    if comando is RespectoPendiente.NO_PUEDO:
        _repreguntar(cur, quien, workspace_id, chat_id, abierta, pregunta, ahora,
                     entrante_id, prefijo=f"{AVISO_NO_PUEDO_DATO_PENDIENTE} ")
        return None
    if comando is RespectoPendiente.CHARLA:
        _repreguntar(cur, quien, workspace_id, chat_id, abierta, pregunta, ahora,
                     entrante_id)
        return None
    # `dudoso`, y también `corrige` donde corregir no es responder: lo decide
    # la persona con los botones.
    _preguntar_si_es_el_dato(cur, quien, workspace_id, chat_id, texto, abierta,
                             entrante_id, ahora)
    return None


def _repreguntar(cur, quien, workspace_id: str, chat_id: int, abierta,
                 pregunta: _Pregunta, ahora, entrante_id: str | None, *,
                 prefijo: str = "") -> None:
    """Vuelve a hacer la pregunta abierta (`charla`, `no_puedo`, un mensaje que
    no era la opción). Una elección del alta la vuelve a mandar con sus
    botones: sus opciones son las únicas respuestas. Las demás, como texto."""
    if abierta.herramienta in (_SENTINEL_VISTA_PREVIA, _SENTINEL_ELECCION):
        _mostrar_pregunta_con_botones(
            cur, quien, workspace_id, chat_id, abierta, ahora, entrante_id,
            prefijo=prefijo.strip())
        return
    if abierta.herramienta == _SENTINEL_ALTA_ELECCION:
        from .ingreso_tareas import resend_choice_prompt

        if resend_choice_prompt(cur, quien, abierta.pregunta_id, ahora,
                                entrante_id, prefix=prefijo):
            return
        texto = AVISO_DATO_YA_NO_PENDIENTE
    elif abierta.args.get("bloque"):
        # El dato que se corrige (Modificar): vuelve con lo que la persona tenía,
        # en el bloque que se copia con un toque.
        from .ingreso_tareas import modify_text_prompt

        bloque = abierta.args["bloque"]
        _responder(cur, workspace_id, chat_id, quien,
                   f"{prefijo}{modify_text_prompt(abierta.args['campo'], bloque)}",
                   ahora, bloque=bloque)
        return
    else:
        texto = f"{prefijo}{pregunta.pregunta}"
    _responder(cur, workspace_id, chat_id, quien, texto, ahora)


def _seguir_con_la_respuesta(cur, quien, texto: str, abierta, route, proveedor,
                             cal, chat_id: int, workspace_id: str, ahora,
                             entrante_id: str | None) -> None:
    """El mensaje es la respuesta a la pregunta, ya consumida: sigue el camino
    propio de cada tipo, el de siempre. `route` es la que ya se obtuvo al
    interpretar el mensaje, o `None` si todavía no se rutea (el botón "Sí, es
    eso"); el dato del menú y el campo del alta no la necesitan."""
    from . import pendientes as P

    if abierta.herramienta == _SENTINEL_ALTA_TEXTO_LIBRE:
        _seguir_con_el_campo_del_alta(cur, quien, texto, abierta, chat_id,
                                      workspace_id, ahora, entrante_id)
        return
    if abierta.herramienta == _SENTINEL_ALTA_ELECCION:
        _seguir_con_la_eleccion_del_alta(cur, quien, texto, abierta, chat_id,
                                         workspace_id, ahora, entrante_id)
        return
    if abierta.herramienta == _SENTINEL_ALTA_CONFIRMACION:
        # El mensaje no confirma el borrador: la conversión es explícita, con
        # el botón Confirmar (AGENTS.md, invariantes). Se dice cómo se
        # confirma y el borrador sigue esperando.
        _responder(cur, workspace_id, chat_id, quien, abierta.resumen, ahora)
        return
    if abierta.herramienta == _SENTINEL_VISTA_PREVIA:
        # Lo mismo con la vista previa de un cambio: sólo el botón Confirmar
        # lo aplica. Se dice y se la vuelve a mostrar con sus botones.
        _mostrar_pregunta_con_botones(
            cur, quien, workspace_id, chat_id, abierta, ahora, entrante_id,
            prefijo=AVISO_VISTA_PREVIA_SE_CONFIRMA_CON_EL_BOTON)
        return
    if abierta.herramienta == _SENTINEL_ELECCION:
        _seguir_con_la_eleccion_abierta(cur, quien, texto, abierta, chat_id,
                                        workspace_id, ahora, entrante_id)
        return
    if abierta.herramienta == P.SENTINEL_DATO_MENU_TAREA:
        _resumir_dato_menu_tarea(cur, quien, texto, abierta, chat_id,
                                 workspace_id, ahora)
        return
    if route is None:
        route, error = _rutear(proveedor, texto)
        if route is None:
            _avisar_ruteo_caido(cur, quien, error, workspace_id, chat_id, ahora)
            return
    if abierta.herramienta == _SENTINEL_ACLARACION:
        _resumir_aclaracion_ninguna(cur, quien, texto, abierta, route, proveedor,
                                    cal, chat_id, workspace_id, ahora, entrante_id)
        return
    # Modificar: la corrección pasa por el ruteo ya obtenido, las referencias
    # y Jev como cualquier turno, y llega al agente con la propuesta.
    _seguir_camino_normal(cur, quien, texto, route, proveedor, cal, chat_id,
                          workspace_id, ahora, entrante_id, modificacion=abierta)


def _dejar_pregunta_pendiente(cur, quien, workspace_id: str, chat_id: int,
                              abierta, ahora) -> None:
    """La persona deja de lado la pregunta abierta (`cancela` o el botón
    "Dejarlo"). Sólo dice que la dejó si de verdad la consumió ahora: si otro
    camino ya la había consumido, lo dice así, sin afirmar nada más."""
    if _dejar_de_lado(cur, quien, abierta, ahora):
        texto = _pregunta_de(abierta).dejada
    else:
        texto = AVISO_DATO_YA_NO_PENDIENTE
    _responder(cur, workspace_id, chat_id, quien, texto, ahora)


def _cerrar_como_modificar(cur, quien, abierta, ahora):
    """La corrección escrita de la vista previa de un cambio (T9-R1d-1b): la
    cierra como el botón Modificar (`pendientes.modificar_vista_previa`, sin
    aplicar nada) y devuelve lo que ese toque dejaría para el turno, o `None`
    si otro camino ya la había cerrado. Audita lo mismo que el botón."""
    from . import pendientes as P

    modificacion = P.modificar_vista_previa(cur, quien, abierta.pregunta_id,
                                            ahora)
    if modificacion is not None:
        registrar_auditoria(
            cur, accion=f"modificar:{modificacion.herramienta}",
            workspace_id=quien.workspace_id, actor_app_user_id=quien.app_user_id,
            actor_kind="persona",
            detalle={"args": modificacion.args, "via": "texto"})
    return modificacion


def _mostrar_pregunta_con_botones(cur, quien, workspace_id: str, chat_id: int,
                                  abierta, ahora, entrante_id: str | None, *,
                                  prefijo: str = "") -> None:
    """Vuelve a mostrar, con sus botones, la vista previa de un cambio o la
    elección con botones que la persona no respondió (`charla`, `no_puedo`,
    "Seguir", un mensaje que quiso confirmar sin el botón o que no dijo una de
    las opciones), con `prefijo` delante si viene. Es un solo mensaje: el mismo texto
    con los mismos botones de siempre (`despachador` arma los botones de la
    `pending_action`; el toque de cualquiera de los dos mensajes resuelve una
    sola vez). Si el prefijo no deja entrar la vista previa con sus botones, la
    respuesta sale en dos partes, con un solo juego de botones: primero el
    prefijo y después la vista previa sola, completa y con sus botones (así
    salió la primera vez, así que entra). Nunca sale el prefijo solo: dejaría a
    la persona sin ver lo que espera. Si ya no esperaba, se dice."""
    from datetime import timedelta

    from . import pendientes as P
    from .agente import _TEXTO_BOTONES_GENERICO

    if not P.vista_previa_esperando(cur, abierta.pregunta_id, ahora):
        _responder(cur, workspace_id, chat_id, quien, AVISO_DATO_YA_NO_PENDIENTE,
                   ahora)
        return
    texto = f"{prefijo}\n\n{abierta.resumen}" if prefijo else abierta.resumen
    # Las partes de esta respuesta comparten grupo (T9-R2): son UNA respuesta.
    grupo = (f"{workspace_id}:vista-previa:{abierta.pregunta_id}:"
             f"{entrante_id or ahora.timestamp()}")
    if prefijo and not cabe_en_mensaje(texto, has_buttons=True):
        # Dos milisegundos antes, para que salga delante de la vista previa.
        _responder(cur, workspace_id, chat_id, quien, prefijo,
                   ahora - timedelta(milliseconds=2), grupo=grupo)
        texto = abierta.resumen
    if not cabe_en_mensaje(texto, has_buttons=True):
        # Lo guardado entró con sus botones sin el margen del saludo diario y
        # ahora ya no entra: mismo criterio que
        # `agente._encolar_texto_con_opciones`. El texto entero sale antes, en
        # partes, y la pregunta sigue con un texto corto y sus mismos botones.
        # Nunca falla ni sale sin lo que la persona espera.
        _responder(cur, workspace_id, chat_id, quien, texto,
                   ahora - timedelta(milliseconds=1), grupo=grupo)
        texto = _TEXTO_BOTONES_GENERICO
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id,
        recipient_membership_id=quien.membership_id, text=texto,
        scheduled_for=ahora,
        dedupe_key=(f"{workspace_id}:vista-previa:{abierta.pregunta_id}:"
                    f"{entrante_id or ahora.timestamp()}"),
        is_response=True, pending_action_id=abierta.pregunta_id,
        grupo_respuesta=grupo)


def _ver_pregunta_abierta(cur, quien, chat_id: int, ahora, *, alta: bool):
    """La pregunta abierta de esta persona en este chat, sin consumirla.

    El campo `pregunta_id` de lo que devuelve no siempre es una fila de
    la Modificación: según `herramienta` es el id de la fila de
    `pending_action` o, con uno de los centinelas del alta (`_TIPO_DE_ALTA`),
    el del campo de texto libre (`task_intake_free_text_slot`), el de la
    elección (`task_intake_choice_set`) o el de la vista previa del borrador
    (su `pending_action`). Sólo lo usan `_consumir_pregunta`, `_dejar_de_lado`
    y las funciones del alta, y cada una mira `herramienta` primero.

    Con `alta` (un chat privado), primero la pregunta abierta del alta guiada
    (campo de texto libre, elección con botones o borrador esperando su
    confirmación): si hay una y también una pregunta de `pending_action`, el
    alta tiene precedencia, como antes de T9-R1c-1 (el alta leía el mensaje antes
    de que `_turno` mirara nada); la otra queda abierta y se retoma cuando el
    alta termina o se deja. Sin `alta`, sólo las de `pending_action`.

    Después, la elección con botones que Prisma le pidió y ella no respondió
    (T9-R1d-1c, `pendientes.ver_eleccion_abierta`: la aclaración "¿A cuál te
    referís?", la de la otra tarea de una dependencia, la de una herramienta) y,
    última, la vista previa de un cambio que la persona pidió y espera su
    Confirmar (T9-R1d-1b, `pendientes.ver_vista_previa_abierta`). Precedencia:
    alta, después el dato o la corrección que se pidió por escrito (Modificar,
    "Ninguna, lo escribo", el dato de una acción del menú), después la elección
    y por último la vista previa. Las que piden un dato consumen el mensaje
    siguiente y son lo último que la persona abrió; una elección abre al
    terminar el turno y es más nueva que una vista previa que sigue esperando su
    Confirmar, que vuelve a ser la rama abierta cuando esas se cierran. No son
    una rama las ofertas de camino (listas de tareas, el menú de una tarea,
    "Quiero consultar otra cosa"), la vista previa o la elección de otra persona
    ni lo que le llega a alguien para decidir (el aviso de entrega, el borrador
    que espera a otro aprobador): ese es un mensaje que inicia Prisma."""
    from . import herramientas as H
    from . import pendientes as P

    rama = P.ver_rama_abierta(cur, quien, chat_id, ahora, H.REGISTRO, alta=alta)
    if rama is None:
        return None
    if rama.tipo == P.RAMA_ALTA:
        pregunta = rama.alta
        args = {"campo": pregunta["campo"], "titulo": pregunta["titulo"],
                "request_id": pregunta["request_id"]}
        if pregunta["opciones"] is not None:
            args["opciones"] = pregunta["opciones"]
            args["clase"] = pregunta.get("clase")
        if pregunta.get("bloque"):
            args["bloque"] = pregunta["bloque"]
        return P.ModificacionAbierta(
            pregunta_id=pregunta["id"],
            herramienta=_SENTINEL_DE_ALTA[pregunta["tipo"]], args=args,
            resumen=pregunta["resumen"])
    if rama.tipo == P.RAMA_DATO:
        return rama.modificacion
    pendiente = rama.pendiente
    if rama.tipo == P.RAMA_ELECCION:
        return P.ModificacionAbierta(
            pregunta_id=pendiente.id, herramienta=_SENTINEL_ELECCION,
            args={"herramienta": pendiente.herramienta,
                  "argumentos": pendiente.args, "campo": pendiente.campo,
                  "opciones": [etiqueta_sin_icono(o.etiqueta)
                               for o in pendiente.opciones]},
            resumen=pendiente.resumen)
    return P.ModificacionAbierta(
        pregunta_id=pendiente.id, herramienta=_SENTINEL_VISTA_PREVIA,
        args={"herramienta": pendiente.herramienta,
              "argumentos": pendiente.args},
        resumen=pendiente.resumen)


def _consumir_pregunta(cur, quien, abierta, ahora) -> bool:
    """Reclama la pregunta abierta para la respuesta que se va a tomar: `True`
    si esta llamada la consumió, `False` si otro camino ya lo había hecho. El
    campo del alta no se consume acá sino en `consume_pending_text`, junto con
    su validación (un texto vacío o demasiado largo deja el campo abierto), y
    la elección en `resolve_choice`; el borrador esperando confirmación no se
    consume nunca con un mensaje: acá sólo se comprueba que siga esperando. Lo
    mismo la vista previa de un cambio (T9-R1d-1b): sólo su botón la aplica; y
    la elección con botones (T9-R1d-1c): se resuelve al tomar una opción."""
    from . import pendientes as P
    from .ingreso_tareas import intake_question_active

    if abierta.herramienta in _TIPO_DE_ALTA:
        return intake_question_active(cur, quien,
                                      _TIPO_DE_ALTA[abierta.herramienta],
                                      abierta.pregunta_id)
    if abierta.herramienta in (_SENTINEL_VISTA_PREVIA, _SENTINEL_ELECCION):
        return P.vista_previa_esperando(cur, abierta.pregunta_id, ahora)
    return P.consumir_modificacion(cur, abierta.pregunta_id, ahora)


def _dejar_de_lado(cur, quien, abierta, ahora) -> bool:
    """Deja de lado la pregunta abierta: `True` si esta llamada la cerró. Una
    fila de `pending_action` se consume; una pregunta del alta cancela su
    borrador, porque sin ese dato, esa elección o esa confirmación el alta no
    sigue. La vista previa de un cambio (T9-R1d-1b) se cancela por el mismo
    camino que su botón Cancelar: no se aplica nada; la elección con botones
    (T9-R1d-1c), por el mismo (queda `cancelada` y sus botones ya no valen)."""
    from . import pendientes as P
    from .ingreso_tareas import cancel_from_intake_question

    if abierta.herramienta in _TIPO_DE_ALTA:
        return cancel_from_intake_question(
            cur, quien, _TIPO_DE_ALTA[abierta.herramienta],
            abierta.pregunta_id, ahora)
    if abierta.herramienta in (_SENTINEL_VISTA_PREVIA, _SENTINEL_ELECCION):
        return P.cancelar_vista_previa(cur, quien, abierta.pregunta_id, ahora)
    return P.consumir_modificacion(cur, abierta.pregunta_id, ahora)


def _seguir_con_el_campo_del_alta(cur, quien, texto: str, abierta, chat_id: int,
                                  workspace_id: str, ahora,
                                  entrante_id: str | None) -> None:
    """El mensaje es el campo que esperaba el alta: sigue el camino de siempre
    (`consume_pending_text`: validación, fecha, entidad y el próximo paso).
    Si el campo ya no estaba abierto, lo dice y no hace nada."""
    from .ingreso_tareas import consume_pending_text

    resultado = consume_pending_text(
        cur, quien, chat_id=chat_id, source_inbound_id=entrante_id,
        source_raw_text=texto, now=ahora, slot_id=abierta.pregunta_id)
    if resultado is None:
        _responder(cur, workspace_id, chat_id, quien, AVISO_DATO_YA_NO_PENDIENTE,
                   ahora)


def _seguir_con_la_eleccion_abierta(cur, quien, texto: str, abierta,
                                    chat_id: int, workspace_id: str, ahora,
                                    entrante_id: str | None) -> None:
    """El mensaje responde a una elección con botones (T9-R1d-1c): si dice
    exactamente UNA de sus opciones, sigue como el toque (`_tomar_opcion`); si
    no, la elección vuelve a mostrarse con sus botones, porque las opciones son
    las únicas respuestas y el modelo nunca elige por la persona (igual que la
    elección del alta)."""
    from . import pendientes as P

    fila = _fila_de_la_eleccion(abierta)
    # El botón de una candidata muestra el título acortado: el título entero
    # también la identifica.
    nombres = {c["id"]: c["titulo"]
               for candidatas in (fila.args.get("candidatas") or {}).values()
               for c in candidatas if c.get("id") and c.get("titulo")}
    opcion = P.opcion_escrita(cur, abierta.pregunta_id, texto, nombres=nombres)
    if opcion is None:
        _repreguntar(cur, quien, workspace_id, chat_id, abierta,
                     _pregunta_de(abierta), ahora, entrante_id)
        return
    _tomar_opcion(cur, quien, workspace_id, chat_id, opcion.token, ahora)


def _tomar_opcion(cur, quien, workspace_id: str, chat_id: int, token: str,
                  ahora) -> None:
    """La opción de una elección dicha por escrito se toma como el toque
    (`_toque`): se resuelve la acción por su token y sigue el camino de
    `_seguir_resuelta`. Si otro camino la había resuelto en el medio, se dice."""
    from . import pendientes as P

    resuelta = P.resolver(cur, token, app_user_id=quien.app_user_id, ahora=ahora)
    if resuelta is None:
        _responder(cur, workspace_id, chat_id, quien, AVISO_DATO_YA_NO_PENDIENTE,
                   ahora)
        return
    _seguir_resuelta(cur, quien, workspace_id, chat_id, token, resuelta,
                     P.pending_action_id_de(cur, token), ahora)


def _seguir_con_la_eleccion_del_alta(cur, quien, texto: str, abierta,
                                     chat_id: int, workspace_id: str, ahora,
                                     entrante_id: str | None) -> None:
    """El mensaje responde a una elección con botones del alta: si es
    exactamente una de sus opciones, sigue como el toque (`resolve_choice`); si
    no, la elección vuelve a mostrarse con sus botones, porque las opciones son
    las únicas respuestas y el modelo nunca elige por la persona."""
    from .ingreso_tareas import resolve_typed_choice

    resultado = resolve_typed_choice(
        cur, quien, choice_set_id=abierta.pregunta_id, text=texto,
        chat_id=chat_id, now=ahora)
    if resultado is None or resultado.inert:
        _repreguntar(cur, quien, workspace_id, chat_id, abierta,
                     _pregunta_de(abierta), ahora, entrante_id)


def _preguntar_si_es_el_dato(cur, quien, workspace_id: str, chat_id: int,
                             texto: str, abierta, entrante_id: str | None,
                             ahora) -> None:
    """Comando `dudoso`: una sola pregunta con dos botones. No consume la
    pregunta abierta; el texto original y la pregunta (id, tipo y datos) quedan
    en los `args` de la acción de un solo uso que resuelve el toque
    (`_resolver_toque_respuesta_dato_menu`)."""
    _preguntar_con_botones_sobre_la_rama(
        cur, quien, workspace_id, chat_id, texto, abierta, entrante_id, ahora,
        resumen=PREGUNTA_ES_EL_DATO.format(
            descripcion=_pregunta_de(abierta).nombre),
        opciones=[(ETIQUETA_ES_EL_DATO, _ELECCION_DATO_SI),
                  (ETIQUETA_NO_ES_EL_DATO, _ELECCION_DATO_DEJAR)],
        clave="dato-dudoso")


def _preguntar_por_la_rama(cur, quien, workspace_id: str, chat_id: int,
                           texto: str, abierta, entrante_id: str | None,
                           ahora) -> None:
    """Comando `otro_tema` con una pregunta abierta (T9-R1d, enmienda de la
    regla 1 del ADR 0013): el mensaje no se atiende; una sola pregunta con dos
    botones sobre lo pendiente. El mensaje (su texto y su id de mensaje
    entrante) queda guardado con los botones para atenderlo si la persona deja
    lo pendiente, sin pedirle que lo repita."""
    _preguntar_con_botones_sobre_la_rama(
        cur, quien, workspace_id, chat_id, texto, abierta, entrante_id, ahora,
        resumen=PREGUNTA_RAMA_ABIERTA.format(
            nombre=_pregunta_de(abierta).nombre),
        opciones=[(ETIQUETA_SEGUIR_RAMA, _ELECCION_DATO_SEGUIR),
                  (ETIQUETA_DEJAR_RAMA, _ELECCION_DATO_DEJAR)],
        clave="rama-abierta")


def _preguntar_con_botones_sobre_la_rama(cur, quien, workspace_id: str,
                                         chat_id: int, texto: str, abierta,
                                         entrante_id: str | None, ahora, *,
                                         resumen: str, opciones: list,
                                         clave: str) -> None:
    """La pregunta con botones que deja `dudoso` u `otro_tema`. Sólo hay una
    viva por persona y chat: los botones de la anterior pierden vigencia (un
    toque tardío se contesta como cualquier pedido que ya no está vigente)."""
    from . import pendientes as P
    from .agente import VIGENCIA_PENDIENTE

    P.retirar_preguntas_de_rama(cur, quien, chat_id, ahora)
    p = P.registrar(
        cur, quien, herramienta=P.SENTINEL_RESPUESTA_DATO_MENU,
        args={**_args_de_la_pregunta(abierta), "texto": texto,
              "entrante_id": entrante_id},
        resumen=resumen, vence_en=ahora + VIGENCIA_PENDIENTE, campo="eleccion",
        opciones=opciones, chat_id=chat_id)
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id,
        recipient_membership_id=quien.membership_id, text=p.resumen,
        scheduled_for=ahora, dedupe_key=f"{workspace_id}:{clave}:{p.id}",
        is_response=True, pending_action_id=p.id)


def _args_de_la_pregunta(abierta) -> dict:
    """Lo que un botón de `SENTINEL_RESPUESTA_DATO_MENU` guarda para volver a
    armar la pregunta abierta al tocarlo (`_pregunta_abierta_de_toque`)."""
    return {"pregunta_id": abierta.pregunta_id, "dato": abierta.args,
            "herramienta": abierta.herramienta, "resumen": abierta.resumen}


def _pregunta_abierta_de_toque(args: dict):
    """Vuelve a armar la pregunta abierta desde los `args` de un botón. Una
    fila sin `herramienta` es de antes de T9-R1b: sólo existía el dato del
    menú."""
    from . import pendientes as P

    return P.ModificacionAbierta(
        pregunta_id=args.get("pregunta_id"),
        herramienta=args.get("herramienta") or P.SENTINEL_DATO_MENU_TAREA,
        args=args.get("dato") or {}, resumen=args.get("resumen") or "")


def _resolver_toque_respuesta_dato_menu(cur, quien, workspace_id: str,
                                        chat_id: int, args: dict, ahora) -> None:
    """Alguien tocó un botón de `SENTINEL_RESPUESTA_DATO_MENU` (T9-R1a-2,
    generalizado en T9-R1b a cualquier pregunta pendiente): "Sí, es eso" y "No,
    es otra cosa" del comando `dudoso`, o "Seguir" y "Dejarlo y ver lo otro" de
    la pregunta de la rama (`otro_tema`, T9-R1d). Cada uno deja exactamente una
    respuesta."""
    from . import pendientes as P
    from .calendario import Calendario
    from .llm import desde_base

    eleccion = args.get("eleccion")
    abierta = _pregunta_abierta_de_toque(args)
    texto = args.get("texto")

    if texto is None:
        # El botón "Dejarlo" del retome de antes de T9-R1d: ya no hay retome ni
        # mensaje guardado que atender. Se contesta como un pedido que ya no
        # está vigente, sin cerrar la pregunta.
        _responder(cur, workspace_id, chat_id, quien, AVISO_PEDIDO_NO_VIGENTE,
                   ahora)
        return

    # Auditoría: la elección y la tarea, nunca el texto de la persona.
    registrar_auditoria(
        cur, accion="respuesta_dato_menu", workspace_id=workspace_id,
        actor_app_user_id=quien.app_user_id, actor_kind="persona",
        detalle={"eleccion": eleccion, "tarea_id": abierta.args.get("tarea_id")})

    if eleccion == _ELECCION_DATO_SEGUIR:
        _seguir_con_la_pregunta(cur, quien, workspace_id, chat_id, abierta, ahora)
        return

    proveedor = desde_base(cur, workspace_id, config)
    cal = Calendario.desde_base(cur, workspace_id)

    if eleccion == _ELECCION_DATO_SI:
        # Igual que `responde`. La corrección y la aclaración necesitan la
        # ruta del mensaje: se obtiene antes de consumir, así un ruteo caído
        # no pierde la pregunta. Si otro camino ya la consumió, se dice y no
        # se hace nada.
        route = None
        if (abierta.herramienta != P.SENTINEL_DATO_MENU_TAREA
                and abierta.herramienta not in (_SENTINEL_VISTA_PREVIA,
                                                _SENTINEL_ELECCION)
                and abierta.herramienta not in _TIPO_DE_ALTA):
            route, error = _rutear(proveedor, texto)
            if route is None:
                _avisar_ruteo_caido(cur, quien, error, workspace_id, chat_id,
                                    ahora)
                return
        if not _consumir_pregunta(cur, quien, abierta, ahora):
            _responder(cur, workspace_id, chat_id, quien,
                       AVISO_DATO_YA_NO_PENDIENTE, ahora)
            return
        _seguir_con_la_respuesta(cur, quien, texto, abierta, route, proveedor,
                                 cal, chat_id, workspace_id, ahora,
                                 args.get("entrante_id"))
        return

    if eleccion not in _ELECCIONES_DE_DEJAR:
        # Un valor que ningún botón de hoy deja: no es "dejar" (review R3). Se
        # contesta como un pedido que ya no está vigente, sin cerrar nada.
        _responder(cur, workspace_id, chat_id, quien, AVISO_PEDIDO_NO_VIGENTE,
                   ahora)
        return

    _dejar_y_ver_lo_otro(cur, quien, workspace_id, chat_id, abierta, texto,
                         args.get("entrante_id"), proveedor, cal, ahora)


def _sigue_abierta(cur, quien, chat_id: int, abierta, ahora) -> bool:
    """Si la pregunta de un botón sigue siendo la abierta de esta persona: no
    la cerró ni la reemplazó otro camino. Sin consumirla."""
    from . import pendientes as P
    from .ingreso_tareas import intake_question_active

    if abierta.herramienta in _TIPO_DE_ALTA:
        return intake_question_active(cur, quien,
                                      _TIPO_DE_ALTA[abierta.herramienta],
                                      abierta.pregunta_id)
    if abierta.herramienta in (_SENTINEL_VISTA_PREVIA, _SENTINEL_ELECCION):
        return P.vista_previa_esperando(cur, abierta.pregunta_id, ahora)
    vigente = P.ver_modificacion_abierta(cur, quien, chat_id, ahora)
    return vigente is not None and vigente.pregunta_id == abierta.pregunta_id


def _seguir_con_la_pregunta(cur, quien, workspace_id: str, chat_id: int,
                            abierta, ahora) -> None:
    """"Seguir" de la pregunta de la rama: vuelve a hacer la pregunta pendiente
    (una elección del alta, con sus botones). Si ya no estaba abierta, lo dice
    y no manda nada más."""
    if not _sigue_abierta(cur, quien, chat_id, abierta, ahora):
        _responder(cur, workspace_id, chat_id, quien, AVISO_RAMA_YA_CERRADA,
                   ahora)
        return
    _repreguntar(cur, quien, workspace_id, chat_id, abierta,
                 _pregunta_de(abierta), ahora, None)


def _dejar_y_ver_lo_otro(cur, quien, workspace_id: str, chat_id: int, abierta,
                         texto: str, entrante_id: str | None, proveedor, cal,
                         ahora) -> None:
    """"Dejarlo y ver lo otro": cierra lo pendiente por el mismo camino que
    `cancela` y, en la misma respuesta, atiende el mensaje guardado por el
    camino normal, como si no hubiera pregunta abierta. Se rutea antes de
    cerrar, así un ruteo caído no pierde la pregunta. Si otro camino ya la
    había cerrado, el mensaje se atiende igual (nunca se pierde lo que la
    persona pidió) y no se dice que se dejó nada de lado."""
    from datetime import timedelta

    route, error = _rutear(proveedor, texto)
    if route is None:
        _avisar_ruteo_caido(cur, quien, error, workspace_id, chat_id, ahora)
        return
    if _dejar_de_lado(cur, quien, abierta, ahora):
        # La primera parte de la misma respuesta: un milisegundo antes, para
        # que salga delante de lo que diga el camino normal.
        _responder(cur, workspace_id, chat_id, quien,
                   _pregunta_de(abierta).dejada,
                   ahora - timedelta(milliseconds=1))
    # Lo que se acaba de dejar no se propone de nuevo en este turno: el modelo
    # lo ve en el historial y lo repetía (T9-R1d-1a-fix), o no lo ve (el alta,
    # T9-R2b): la guarda de código y el contexto salen de la misma pregunta.
    _seguir_camino_normal(cur, quien, texto, route, proveedor, cal, chat_id,
                          workspace_id, ahora, entrante_id,
                          no_proponer=_lo_dejado_de(abierta))


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


def _resumir_aclaracion_ninguna(cur, quien, texto: str, modificacion, route,
                                proveedor, cal, chat_id: int, workspace_id: str,
                                ahora, entrante_id) -> None:
    """Retoma después de "Ninguna, lo escribo" (T4, decisión 4). La persona
    declinó las tareas ofrecidas para una referencia; este mensaje NO es un
    Modificar (nadie tocó Modificar, no hay vista previa de una herramienta
    que corregir) así que nunca pasa por `_bloque_modificacion` -- eso le
    diría al modelo que vuelva a llamar a una herramienta que ni siquiera es
    real (el centinela interno).

    En T4, este mensaje se rutea y resuelve como
    cualquier turno -- el mismo camino que ya usa una corrección real de
    Modificar -- porque puede traer su propia referencia dicha con otras
    palabras ("es la de máq. 3"). El bloque de contexto es propio: nombra la
    referencia que quedó sin resolver y el mensaje original, y conserva lo
    que ya se había resuelto de otras referencias en ese mismo turno
    (`bloque_base` guardado en `args` al armar la pregunta)."""
    from .llm import IntentAction

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
        "no_proponer": None,
    }


def _estado_de_aclaracion_ambigua(cur, quien, workspace_id: str, texto: str,
                                  referencia: str,
                                  candidatas_ids: list[str]) -> dict:
    """El estado que deja un turno cuya única referencia ambigua es `referencia`
    (con las tareas `candidatas_ids` en el orden de Jev) y nada más resuelto,
    armado con las mismas piezas que el turno real
    (`_resolver_referencias_del_turno`: `_candidatas_para_botones` y
    `_estado_inicial_aclaracion`), listo para `_preguntar_por_botones`. Lo usa
    el banco para sembrar esa aclaración sin copiar a mano su estado privado
    (T9-R1d-2, `tests/banco/corrida.py`)."""
    from .jev import ResolucionReferencia, TipoResolucion
    from .llm import IntentAction, IntentRoute

    por_id = {t.id: t for t in _tareas_activas(cur, workspace_id)}
    resolucion = ResolucionReferencia(TipoResolucion.AMBIGUA,
                                      candidatas=tuple(candidatas_ids))
    referencias = _ReferenciasResueltas(
        bloque=_bloque_contexto_referencias({}, por_id), hay_clara=False,
        pendientes_boton=((
            referencia,
            _candidatas_para_botones(por_id, resolucion, quien.membership_id)),))
    return _estado_inicial_aclaracion(
        texto, None, IntentRoute(IntentAction.NORMAL_CONVERSATION), referencias,
        None)


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
            pregunta_id="", herramienta=mod["herramienta"],
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

    from .agente import NoProponer, responder
    guarda = estado.get("no_proponer")
    responder(cur, quien, estado["mensaje"], proveedor, cal, chat_id,
             ahora=ahora, entrante_id=estado["entrante_id"],
             contexto_referencias=contexto,
             tareas_resueltas_claras=estado["titulos_resueltas"],
             no_proponer=NoProponer(**guarda) if guarda else None)


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
                  PREGUNTA_ACLARACION_NINGUNA, ahora)
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
    proveedor = desde_base(cur, workspace_id, config)
    _avanzar_aclaracion(cur, quien, workspace_id, chat_id, ahora, proveedor, cal,
                       estado)


# Cuánto de la pregunta cerrada entra en el mensaje de "Quiero consultar
# otra cosa" (hallazgo 10, sesión 2 por Telegram, 2026-09-27): nombrarla ahí,
# en el propio `message_outbox`, es lo que deja el cierre como un hecho en
# `contexto.historial` -- no hace falta una tabla nueva, es el mismo
# mecanismo que ya arma el historial de cualquier otro turno. Corte por
# caracteres (no por palabra): esto es un mensaje, no un botón -- lo normal
# (T1: "una frase corta") entra entero de sobra; el corte es sólo una red de
# seguridad para el texto largo que T3/T4b guardan en el mismo `pregunta`.
LIMITE_PREGUNTA_CERRADA = 160


def _texto_cierre_opciones(pregunta: str) -> str:
    """Texto de "Quiero consultar otra cosa" (hallazgo 10, sesión 2 por
    Telegram, 2026-09-27, evidencia real: Marcos tocó la salida sobre "¿Sobre
    cuál de tus tareas avanzaste?", escribió "hols" y Prisma volvió a
    preguntar lo mismo). Causa real: el cierre salía con un texto fijo que no
    nombraba qué se cerró ("Dale, escribime qué necesitás.") -- el historial
    que arma `contexto.historial` guarda literalmente lo que salió por
    `message_outbox`, así que el turno siguiente veía dos mensajes de Prisma
    seguidos (la pregunta y el cierre) sin ninguna marca de que la persona la
    descartó, y un saludo alcanzaba para que el modelo la retomara.

    Nombrar acá la pregunta cerrada deja ese hecho en el propio historial --
    el mismo mecanismo que ya lee `contexto.historial`, sin una tabla ni un
    campo nuevo -- y la regla nueva de `contexto.PREAMBULO` le dice al modelo
    que no la retome sin que la persona la traiga de nuevo."""
    pregunta = (pregunta or "").strip()
    if not pregunta:
        return "Dale, escribime qué necesitás."
    corta = truncar_etiqueta_boton(pregunta, limite=LIMITE_PREGUNTA_CERRADA)
    return f"Dale, dejamos de lado «{corta}». Escribime qué necesitás."


def _resolver_toque_opcion_modelo(cur, quien, workspace_id: str, chat_id: int,
                                  args: dict, ahora) -> None:
    """Alguien tocó una opción de `ofrecer_opciones` (T1, ADR 0007), de una
    lista de tareas que armó el servidor (T3, ADR 0007 punto 3), o del cierre
    genérico de una pregunta sin opciones (T4b) -- las tres comparten el
    mismo sentinel, `pendientes.SENTINEL_OPCIONES_MODELO`.

    A diferencia de `_resolver_toque_aclaracion`, ninguna elección acá vuelve
    a llamar a una herramienta: "Quiero consultar otra cosa" cierra sin
    efecto e invita a escribir, nombrando qué pregunta quedó cerrada
    (`_texto_cierre_opciones`, hallazgo 10) para que el historial de
    `contexto.py` lo vea (el próximo mensaje se rutea como un turno común);
    una tarea con `accion: "menu"` abre el menú de T2 sin retomar nada; "Ver
    más" (T3) pagina en `_mostrar_mas_tareas`, también sin retomar; "Es una
    tarea nueva" (T4b) arranca el alta guiada en
    `_iniciar_alta_guiada`; "Es sobre una tarea existente" (T4b) lista en
    `_mostrar_tareas_propias`; cualquier otra opción sí retoma la
    conversación con el modelo, pasándole la elección como si fuera lo que
    escribió la persona -- para una tarea, ya resuelta, sin pasar por Jev ni
    por el enrutador.
    """
    eleccion = args.get("eleccion") or {}
    pregunta = args.get("pregunta", "")
    tipo = eleccion.get("tipo")

    # Auditoría (T1, punto 4): el tipo de elección y, si es una tarea, su id
    # -- nunca la pregunta ni el texto de una opción de texto libre.
    registrar_auditoria(
        cur, accion="eleccion_opciones_modelo", workspace_id=workspace_id,
        actor_app_user_id=quien.app_user_id, actor_kind="persona",
        detalle={"tipo": tipo,
                 "tarea_id": eleccion.get("tarea_id") if tipo == "tarea" else None})

    if tipo == "salida":
        _responder(cur, workspace_id, chat_id, quien,
                  _texto_cierre_opciones(pregunta), ahora)
        return

    if tipo == "ver_mas":
        # T3: pagina sin volver a llamar al modelo, a Jev ni a `route_intent`.
        _mostrar_mas_tareas(cur, quien, workspace_id, chat_id,
                           eleccion.get("tarea_ids") or [], ahora)
        return

    if tipo == "tarea_nueva":
        # T4b (ADR 0007, cierre genérico de una pregunta sin opciones):
        # arranca la misma alta guiada que ya usa "Es una tarea nueva" de la
        # aclaración con botones (T4, `aclaracion-con-botones`) --
        # `_iniciar_alta_guiada` ya se encarga de registrar incidente + aviso
        # neutro si `entrante_id` falta o algo falla, sin inventar un mensaje
        # de origen. Sin propuestas del enrutador (nunca se llegó a rutear
        # este turno): el alta guiada las pide todas.
        _iniciar_alta_guiada(cur, quien, chat_id, args.get("entrante_id"),
                            args.get("mensaje_original", pregunta), {},
                            workspace_id, ahora)
        return

    if tipo == "tarea_existente":
        # T4b: lista las tareas activas de la propia persona, con el mismo
        # armado de página + "Ver más" que T3.
        _mostrar_tareas_propias(cur, quien, workspace_id, chat_id, ahora)
        return

    if tipo == "tarea":
        titulo = eleccion.get("titulo", "")
        tarea_id = eleccion.get("tarea_id")
        if eleccion.get("accion") == "menu":
            # T2, ADR 0007 §4.6: esta tarea se ofreció para abrir su menú de
            # acciones, no para resolver la pregunta del modelo -- el menú
            # lo calcula el código (`menu_tarea.calcular_menu`), así que acá
            # nunca se retoma la conversación.
            _abrir_menu_tarea(cur, quien, workspace_id, chat_id, tarea_id, ahora)
            return
        texto_entrante = eleccion.get("etiqueta") or titulo
        contexto = (
            "# Elección de una opción\n\n"
            f"Prisma había preguntado: «{pregunta}»\n\n"
            f"La persona tocó la tarea «{titulo}» ({tarea_id}): es su "
            "respuesta a esa pregunta. Usá esa tarea directamente; no la "
            "vuelvas a resolver ni preguntes de nuevo cuál es.")
        tareas_resueltas = {tarea_id: titulo} if titulo and tarea_id else None
    else:
        texto_entrante = eleccion.get("texto", "")
        contexto = (
            "# Elección de una opción\n\n"
            f"Prisma había preguntado: «{pregunta}»\n\n"
            f"La persona tocó «{texto_entrante}»: es su respuesta a esa "
            "pregunta, tratala como tal.")
        tareas_resueltas = None

    try:
        from .agente import responder
        from .calendario import Calendario
        from .llm import desde_base

        cal = Calendario.desde_base(cur, workspace_id)
        proveedor = desde_base(cur, workspace_id, config)
        responder(cur, quien, texto_entrante, proveedor, cal, chat_id, ahora=ahora,
                 contexto_referencias=contexto,
                 tareas_resueltas_claras=tareas_resueltas)
    except Exception as e:  # noqa: BLE001
        # En T1, `agente.responder` ya atrapa
        # que falle el proveedor DENTRO de la conversación (constante
        # `DISCULPA`, ahí adentro), pero construir el calendario o el
        # proveedor pasa ACÁ, antes de llamarla. Sin este resguardo, esa
        # falla se escapaba hasta `procesar_update`, que revierte toda la
        # transacción -- incluido el toque ya resuelto -- y no queda
        # ninguna respuesta en la cola: la persona se quedaba sin nada, y
        # el toque podía volver a dispararse en un reintento del webhook.
        _routing_incident(cur, quien, e)
        _responder(cur, workspace_id, chat_id, quien,
                  "Perdón, no pude retomar la conversación. Ya quedó "
                  "registrado para que lo revisen. Escribime de nuevo si "
                  "hace falta.", ahora)


def _mostrar_mas_tareas(cur, quien, workspace_id: str, chat_id: int,
                        tarea_ids: list, ahora) -> None:
    """"Ver más" de una lista de tareas (T3, ADR 0007 punto 3).

    Nunca confía en los ids que trae el botón: los revalida contra
    PostgreSQL bajo el cursor con RLS de este toque, con
    `herramientas._tareas_existentes_por_id` -- existencia y espacio, sin
    filtrar por estado. No es `_tareas_activas_por_id` (la que usa T1 para
    validar tareas ofrecidas por el modelo) a propósito: la primera página de
    esta misma lista ya salió tal cual la devolvió `consultar_tareas`, que
    acepta pedir tareas terminadas y no las filtra, así que la página
    siguiente tiene que ser consistente con la primera -- una tarea que se
    cierra entre que se listó y que se tocó "Ver más" se queda en la lista,
    no desaparece. Sólo un id que no es un UUID válido, que no existe, o que
    es de otro espacio queda afuera. No llama al modelo, a Jev ni a
    `route_intent`: es la misma página que ya se había armado, sólo que la
    persona todavía no la había pedido."""
    from . import herramientas as H
    from . import pendientes as P
    from .agente import VIGENCIA_PENDIENTE

    titulos = H._tareas_existentes_por_id(cur, workspace_id, tarea_ids)
    normalizados = [H._uuid_normalizado(tid) for tid in tarea_ids]
    vigentes = [(nid, titulos[nid]) for nid in normalizados
               if nid is not None and nid in titulos]

    if not vigentes:
        resumen = "Esas tareas ya no están disponibles."
        opciones = [(P.ETIQUETA_SALIR_OPCIONES, {"tipo": "salida"})]
    else:
        pagina, resto = (vigentes[:H.MAX_OPCIONES_MODELO],
                        vigentes[H.MAX_OPCIONES_MODELO:])
        resumen = "Más tareas:"
        # Mismas etiquetas cortas y distinguibles que la primera página
        # (`agente._opciones_lista_tareas`) -- esta es la página siguiente
        # de la misma lista, calculada aparte porque no vuelve a llamar al
        # modelo. `salida.etiquetas_de_tarea` es la receta única (R2-002,
        # revisión 2026-09-28+1).
        etiquetas = etiquetas_de_tarea(
            [normalize_visible_text(titulo) for _, titulo in pagina])
        opciones = [
            (etiqueta,
             {"tipo": "tarea", "tarea_id": tid, "titulo": titulo, "accion": "menu"})
            for (tid, titulo), etiqueta in zip(pagina, etiquetas)]
        if resto:
            opciones.append((P.ETIQUETA_VER_MAS,
                             {"tipo": "ver_mas",
                              "tarea_ids": [tid for tid, _ in resto]}))
        opciones.append((P.ETIQUETA_SALIR_OPCIONES, {"tipo": "salida"}))

    p = P.registrar(cur, quien, herramienta=P.SENTINEL_OPCIONES_MODELO,
                    args={"pregunta": resumen}, resumen=resumen,
                    vence_en=ahora + VIGENCIA_PENDIENTE, campo="eleccion",
                    opciones=opciones, chat_id=chat_id)
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id,
        recipient_membership_id=quien.membership_id, text=p.resumen,
        scheduled_for=ahora,
        dedupe_key=f"{workspace_id}:ver-mas:{p.id}",
        is_response=True, pending_action_id=p.id,
    )


def _mostrar_tareas_propias(cur, quien, workspace_id: str, chat_id: int,
                            ahora) -> None:
    """"Es sobre una tarea existente" (T4b, ADR 0007, cierre genérico de una
    pregunta sin opciones): lista las tareas ACTIVAS de la propia persona
    como botones -- misma regla compartida de "activa" que la elección de
    dependencia de T2 (`menu_tarea.tareas_activas_de_persona`; antes cada
    una tenía su propia copia de la consulta), bajo el cursor con RLS de
    este toque, así que nunca puede traer una tarea de otro espacio ni de
    otra persona. Orden determinístico (`fecha_objetivo nulls last, id`):
    mismo motivo que `tareas_activas_de_persona` -- `id` desempata cuando
    dos tareas comparten `fecha_objetivo` (o no tienen), para que el orden
    sea siempre el mismo en vez de depender del orden físico con el que
    Postgres las devuelva.

    Sin tope: se piden TODAS las activas -- `agente._opciones_lista_tareas`
    ya arma "Ver más" con el resto cuando son más de `H.MAX_OPCIONES_MODELO`
    (T3), y esos ids viajan en `pending_action_option.valor` (columna
    jsonb del servidor), nunca en el `callback_data` de Telegram (ese sigue
    siendo sólo el token corto `p:<uuid>`) -- así que no hay límite de
    tamaño de payload que un "Ver más" de más páginas pueda superar. Antes
    se cortaba en silencio a las primeras 25 sin decirlo; ahora se pagina
    todo, igual que la lista que arma T3 para una respuesta de
    `consultar_tareas`."""
    from . import menu_tarea as M
    from . import pendientes as P
    from .agente import VIGENCIA_PENDIENTE, _opciones_lista_tareas

    tareas = M.tareas_activas_de_persona(cur, workspace_id, quien.membership_id)

    if not tareas:
        resumen = "No tenés tareas activas por ahora."
        opciones = [(P.ETIQUETA_SALIR_OPCIONES, {"tipo": "salida"})]
    else:
        resumen = "Elegí una tarea:"
        opciones = _opciones_lista_tareas(tareas)
        opciones.append((P.ETIQUETA_SALIR_OPCIONES, {"tipo": "salida"}))

    p = P.registrar(cur, quien, herramienta=P.SENTINEL_OPCIONES_MODELO,
                    args={"pregunta": resumen}, resumen=resumen,
                    vence_en=ahora + VIGENCIA_PENDIENTE, campo="eleccion",
                    opciones=opciones, chat_id=chat_id)
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id,
        recipient_membership_id=quien.membership_id, text=p.resumen,
        scheduled_for=ahora,
        dedupe_key=f"{workspace_id}:tarea-existente:{p.id}",
        is_response=True, pending_action_id=p.id,
    )


# ---------------------------------------------------------------------------
# Menú de acciones de una tarea (T2, `prisma-orienta`; ADR 0007 §4.6)
# ---------------------------------------------------------------------------
#
# Se llega al menú tocando una tarea que se ofreció con `accion: "menu"`
# (`_resolver_toque_opcion_modelo`, arriba) -- el mismo mecanismo que
# reusará T3 para listar tareas como botones. El menú lo calcula
# `menu_tarea.calcular_menu`, nunca el modelo; tocar una de sus opciones
# jamás resume la conversación: cada acción sigue su propio camino --una
# lectura determinística, la vista previa de una herramienta que ya existe,
# o un dato que hace falta pedir.


def _encolar_menu_tarea(cur, quien, workspace_id: str, chat_id: int,
                        tarea_id: str, ahora, *, encabezado: str | None) -> None:
    """Arma (o rearma) el menú de una tarea y lo encola con sus botones.
    `encabezado`, si viene, se antepone al mensaje -- es cómo "Ver detalle"
    cierra con el menú de nuevo en el mismo mensaje (T2, punto 3)."""
    from . import menu_tarea as M
    from . import pendientes as P
    from .agente import VIGENCIA_PENDIENTE

    menu = M.calcular_menu(cur, quien, tarea_id)
    if menu is None:
        _responder(cur, workspace_id, chat_id, quien,
                  "Esa tarea ya no está disponible.", ahora)
        return

    # Cada acción del menú es una acción SOBRE una tarea -- mismo ícono que
    # cualquier otro botón de tarea (íconos, decisión del usuario,
    # 2026-09-28); `menu_tarea.calcular_menu` calcula el menú en sí, sin
    # conocer presentación, así que el ícono se agrega acá, en el adaptador.
    opciones = [(con_icono(a.etiqueta, ICONO_TAREA), {"accion": a.codigo})
               for a in menu.acciones]
    opciones.append((P.ETIQUETA_SALIR_OPCIONES, {"accion": "salir"}))
    # Encabezado corto -- responsable y estado (T2, hallazgo 4 de sesión 2
    # por Telegram) -- y una sola pregunta debajo, nunca dos.
    pregunta = f"{M.encabezado_menu(menu)}\n¿Qué querés hacer?"
    resumen = f"{encabezado}\n\n{pregunta}" if encabezado else pregunta

    p = P.registrar(cur, quien, herramienta=P.SENTINEL_MENU_TAREA,
                    args={"tarea_id": menu.tarea_id, "titulo": menu.titulo},
                    resumen=resumen, vence_en=ahora + VIGENCIA_PENDIENTE,
                    campo="eleccion", opciones=opciones, chat_id=chat_id)
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id,
        recipient_membership_id=quien.membership_id, text=p.resumen,
        scheduled_for=ahora,
        # El id de `p` (fresco por cada `registrar`) identifica el mensaje,
        # no la marca de tiempo: dos toques seguidos del mismo menú pueden
        # caer en el mismo microsegundo y perderse por `on conflict do
        # nothing` si la clave sólo dependiera de `ahora`.
        dedupe_key=f"{workspace_id}:menu-tarea:{p.id}",
        is_response=True, pending_action_id=p.id,
    )


def _abrir_menu_tarea(cur, quien, workspace_id: str, chat_id: int,
                      tarea_id: str, ahora) -> None:
    _encolar_menu_tarea(cur, quien, workspace_id, chat_id, tarea_id, ahora,
                        encabezado=None)


def _encolar_vista_previa_menu(cur, quien, workspace_id: str, chat_id: int,
                               e, ahora) -> None:
    """La vista previa de una acción del menú (T2): los mismos tres botones
    y la misma huella que cualquier confirmación (ADR 0005, decisión 1;
    `agente._encolar_confirmacion`). Se arma acá y no ahí porque el menú
    nunca pasa por `agente.responder`: no hay una vuelta del modelo a la
    que devolverle el resultado."""
    from . import pendientes as P
    from .agente import VIGENCIA_PENDIENTE

    opciones = ([(ETIQUETA_CONFIRMAR, True), ("Modificar", "modificar"),
                (ETIQUETA_CANCELAR, False)]
               if e.huella is not None else None)
    p = P.registrar(cur, quien, herramienta=e.herramienta, args=e.argumentos,
                    resumen=e.resumen, vence_en=ahora + VIGENCIA_PENDIENTE,
                    chat_id=chat_id, huella=e.huella, opciones=opciones)
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id,
        recipient_membership_id=quien.membership_id, text=e.resumen,
        scheduled_for=ahora,
        dedupe_key=f"{workspace_id}:confirmar-menu:{p.id}",
        is_response=True, pending_action_id=p.id,
    )


def _ejecutar_accion_menu(cur, quien, workspace_id: str, chat_id: int,
                          herramienta: str, call_args: dict, ahora, *,
                          pending_action_id: str | None = None) -> None:
    """Corre una herramienta que ya existe con lo que ya se sabe -- sin
    `ya_confirmada`, así que si declara `preparar` siempre frena primero en
    una vista previa (ADR 0005, decisión 1): nada se aplica todavía.

    Desde `0814fa3` (T2b): las tres funciones que
    llaman a ésta (`_resolver_toque_menu_tarea`, `_resolver_toque_dato_menu_
    tarea`, `_resumir_dato_menu_tarea`) ya atajan `Denegado` en su propio
    `try`/`except` -- pero esta función tiene que ser correcta por sí sola,
    no depender de que quien la llama la envuelva bien. Un `Denegado` de
    `preparar` (p. ej. el chequeo de autoridad nuevo de T2b sobre una tarea
    que no es de quien tocó) se atrapa acá y se responde con el mismo texto
    humano que ya usa `agente._ejecutar_una`.

    El `try` corre dentro de un punto de retorno (`cur.connection.
    transaction`, mismo patrón que `agente._ejecutar_una`): si la base
    rechaza la operación (`psycopg.errors.RaiseException`, p. ej. un ciclo
    de dependencias), la transacción queda abortada y el `_responder` que
    sigue -- un insert -- fallaría sin este resguardo."""
    import psycopg

    from . import herramientas as H

    punto = cur.connection.transaction(force_rollback=False)
    try:
        with punto:
            resultado = H.ejecutar(cur, quien, herramienta, call_args, chat_id=chat_id)
    except Denegado as e:
        _responder(cur, workspace_id, chat_id, quien, str(e), ahora)
        return
    except H.NecesitaConfirmacion as e:
        _encolar_vista_previa_menu(cur, quien, workspace_id, chat_id, e, ahora)
        return
    except psycopg.errors.RaiseException as e:
        # Una regla de la base rechazó la operación (p. ej. un ciclo de
        # dependencias) -- mismo tratamiento que `agente._ejecutar_una`: el
        # texto de esas excepciones está escrito para una persona, no es
        # una falla del sistema que amerite un incidente.
        _responder(cur, workspace_id, chat_id, quien,
                  str(e).split("\n")[0], ahora)
        return
    _responder(cur, workspace_id, chat_id, quien,
              _mensaje_resultado_menu(cur, quien, herramienta, resultado,
                                      pending_action_id=pending_action_id), ahora)


def _mensaje_resultado_menu(cur, quien, herramienta: str, resultado, *,
                            pending_action_id: str | None = None) -> str:
    """El mensaje tras correr una acción del menú sin `ya_confirmada`
    (desde `0814fa3`, T2b, punto 3).

    Como TODAS las herramientas que ofrece el menú declaran `preparar`, y
    `_ejecutar_accion_menu` nunca pasa `ya_confirmada`, `herramientas.
    ejecutar` corta siempre en `NecesitaConfirmacion` antes de tocar el
    handler (ver ese código: con `preparar` devolviendo una `Preparacion` y
    `ya_confirmada=False`, siempre levanta esa excepción) -- lo que llega
    hasta acá sin excepción es siempre el rechazo de negocio que devolvió
    `preparar` (`{"falta": ...}` o `{"error": ...}`), nunca el resultado de
    un handler que sí aplicó algo.

    Decisión del usuario, 2026-09-25: un error nunca pasa en silencio -- ni
    siquiera como una `AssertionError` que se atrapa lejos de acá. Un
    resultado que no se reconoce (por ejemplo, si una herramienta nueva del
    menú alguna vez deja de declarar `preparar`) registra su propio
    incidente, sanitizado, y le contesta a la persona con un aviso neutro --
    nunca "No se aplicó ningún cambio.", que sería afirmar algo que acá no
    se sabe si es cierto."""
    if isinstance(resultado, dict) and ("falta" in resultado or "error" in resultado):
        return resultado.get("falta") or resultado.get("error")
    registrar_incidente(
        cur, quien.workspace_id,
        f"_ejecutar_accion_menu: resultado inesperado sin excepción de "
        f"'{herramienta}' (ninguna herramienta del menú debería llegar "
        f"hasta acá sin haber frenado antes en preparar).",
        referencia_cruda=repr(resultado)[:2000], etapa=ETAPA_ACCION_MENU,
        referencia_tipo=(REFERENCIA_PENDING_ACTION if pending_action_id else None),
        referencia_id=pending_action_id, app_user_id=quien.app_user_id)
    return NOTICIA_NEUTRA_INCIDENTE


def _pedir_dato_menu_tarea(cur, quien, workspace_id: str, chat_id: int, *,
                           accion: str, tarea_id: str, titulo: str,
                           ahora, extra: dict | None = None) -> None:
    """Pide un dato que ninguna herramienta puede adivinar -- la causa de un
    bloqueo, su resolución, la evidencia -- con el mismo mecanismo que
    "Ninguna, lo escribo" (T4, `aclaracion-con-botones`, decisión 4):
    `marcar_para_corregir`, dentro de la ventana de
    `pendientes.VENTANA_MODIFICACION`. Sin botones -- la respuesta es texto
    libre -- y `_turno` la recibe por el sentinel `SENTINEL_DATO_MENU_TAREA`:
    el ruteo tipado la relaciona con el mensaje antes de consumirla (T9-R1a,
    ADR 0013 regla 1, `_atender_dato_pendiente`). La pregunta sale de
    `_pregunta_dato_menu`, la misma con la que se vuelve a preguntar."""
    from . import pendientes as P
    from .agente import VIGENCIA_PENDIENTE

    pregunta = _pregunta_dato_menu(accion, titulo)
    args = {"accion": accion, "tarea_id": tarea_id, "titulo": titulo}
    if extra:
        args.update(extra)
    p = P.registrar(cur, quien, herramienta=P.SENTINEL_DATO_MENU_TAREA,
                    args=args, resumen=pregunta, vence_en=ahora + VIGENCIA_PENDIENTE,
                    chat_id=chat_id, opciones=[])
    P.marcar_para_corregir(cur, quien, p.id, chat_id, ahora)
    # Sin `pending_action_id`: esta fila no tiene botones (se responde
    # escribiendo), pero el id de `p` sigue siendo lo que identifica el
    # mensaje -- no la marca de tiempo, igual que arriba.
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id,
        recipient_membership_id=quien.membership_id, text=pregunta,
        scheduled_for=ahora, dedupe_key=f"{workspace_id}:dato-menu:{p.id}",
        is_response=True,
    )


def _pedir_eleccion_dependencia(cur, quien, workspace_id: str, chat_id: int, *,
                                accion: str, tarea_id: str, titulo: str,
                                pregunta: str, candidatas: list[tuple[str, str]],
                                ahora) -> None:
    """La elección, con botones, de con cuál otra tarea se declara la
    dependencia (T2, punto 3: "cuando la respuesta es un dato de tarea, con
    botones"). Se resuelve como cualquier toque -- `campo="eleccion"` trae
    el id de la tarea elegida en `args["eleccion"]`, igual que
    `NecesitaElegir` -- no como un texto libre."""
    from . import pendientes as P
    from .agente import VIGENCIA_PENDIENTE

    # Etiquetas cortas y distinguibles entre sí (hallazgo de sesión 2 por
    # Telegram): las candidatas de dependencia son títulos de tarea como
    # cualquier otro botón server-armado -- `salida.etiquetas_de_tarea` es la
    # receta única (R2-002, revisión 2026-09-28+1).
    etiquetas = etiquetas_de_tarea([t for _, t in candidatas])
    opciones = [(etiqueta, tid)
               for (tid, _), etiqueta in zip(candidatas, etiquetas)]
    p = P.registrar(cur, quien, herramienta=P.SENTINEL_DATO_MENU_TAREA,
                    args={"accion": accion, "tarea_id": tarea_id, "titulo": titulo},
                    resumen=pregunta, vence_en=ahora + VIGENCIA_PENDIENTE,
                    campo="eleccion", opciones=opciones, chat_id=chat_id)
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id,
        recipient_membership_id=quien.membership_id, text=p.resumen,
        scheduled_for=ahora,
        dedupe_key=f"{workspace_id}:dependencia-menu:{p.id}",
        is_response=True, pending_action_id=p.id,
    )


def _resolver_toque_menu_tarea(cur, quien, workspace_id: str, chat_id: int,
                               args: dict, ahora, *,
                               pending_action_id: str | None = None) -> None:
    """Alguien tocó una acción del menú de una tarea (T2). El menú ya
    calculó qué se puede hacer; acá cada acción sigue su camino.

    `pending_action_id` (T2b, trazabilidad): la `pending_action` del propio
    menú que se está resolviendo, para que un incidente en
    `_ejecutar_accion_menu` quede trazable hasta acá."""
    from . import menu_tarea as M

    eleccion = args.get("eleccion") or {}
    accion = eleccion.get("accion")
    tarea_id = args.get("tarea_id")
    titulo = args.get("titulo", "")

    # Auditoría (T2, punto 5): tipo de acción e id de tarea, nunca texto.
    registrar_auditoria(
        cur, accion="accion_menu_tarea", workspace_id=workspace_id,
        actor_app_user_id=quien.app_user_id, actor_kind="persona",
        detalle={"accion": accion, "tarea_id": tarea_id})

    if accion == "salir":
        _responder(cur, workspace_id, chat_id, quien,
                  "Dale, escribime qué necesitás.", ahora)
        return

    try:
        if accion in ("ver_detalle", "ver_detalle_evidencia"):
            detalle = M.detalle_tarea(
                cur, tarea_id, incluir_evidencia=accion == "ver_detalle_evidencia")
            _encolar_menu_tarea(cur, quien, workspace_id, chat_id, tarea_id, ahora,
                                encabezado=detalle)
            return

        if accion == "empezar":
            _ejecutar_accion_menu(cur, quien, workspace_id, chat_id,
                                  "actualizar_estado",
                                  {"tarea_id": tarea_id, "estado": "en_curso"}, ahora,
                                  pending_action_id=pending_action_id)
            return
        if accion == "terminar":
            # ADR 0009 (hallazgo 8, sesión 2 por Telegram, 2026-09-27): si la
            # política de la tarea exige evidencia y todavía no tiene
            # ninguna, se pide antes -- mismo patrón que "Informar un
            # bloqueo" -- y recién con ese dato se arma UNA sola vista
            # previa que registra la evidencia y mueve el estado en el mismo
            # Confirmar (`_resumir_dato_menu_tarea`, más abajo).
            if M.evidencia_pendiente(cur, tarea_id):
                _pedir_dato_menu_tarea(
                    cur, quien, workspace_id, chat_id, accion="terminar",
                    tarea_id=tarea_id, titulo=titulo, ahora=ahora)
                return
            _ejecutar_accion_menu(cur, quien, workspace_id, chat_id,
                                  "actualizar_estado",
                                  {"tarea_id": tarea_id, "estado": "en_revision"}, ahora,
                                  pending_action_id=pending_action_id)
            return
        if accion == "aprobar":
            _ejecutar_accion_menu(cur, quien, workspace_id, chat_id,
                                  "aprobar_tarea", {"tarea_id": tarea_id}, ahora,
                                  pending_action_id=pending_action_id)
            return
        if accion == "pedir_cambios":
            _pedir_dato_menu_tarea(
                cur, quien, workspace_id, chat_id, accion="pedir_cambios",
                tarea_id=tarea_id, titulo=titulo, ahora=ahora)
            return
        if accion == "cerrar_tarea":
            # ADR 0008: mismo `actualizar_estado` que "Ya la terminé" usa
            # para `en_revision` -- `calcular_menu` (`_puede_cerrar`) sólo
            # ofrece este botón cuando `motivo_no_cierra_tarea` ya está
            # vacío, y el handler lo vuelve a comprobar antes de escribir.
            _ejecutar_accion_menu(cur, quien, workspace_id, chat_id,
                                  "actualizar_estado",
                                  {"tarea_id": tarea_id, "estado": "terminada"}, ahora,
                                  pending_action_id=pending_action_id)
            return

        if accion == "informar_bloqueo":
            _pedir_dato_menu_tarea(
                cur, quien, workspace_id, chat_id, accion="informar_bloqueo",
                tarea_id=tarea_id, titulo=titulo, ahora=ahora)
            return

        if accion == "destrabar":
            abiertos = M.bloqueos_abiertos(cur, tarea_id)
            if not abiertos:
                _encolar_menu_tarea(
                    cur, quien, workspace_id, chat_id, tarea_id, ahora,
                    encabezado="No hay ningún bloqueo abierto para destrabar.")
                return
            if len(abiertos) > 1:
                # Más de un bloqueo abierto a la vez es el caso raro
                # (`registrar_bloqueo` los suma en vez de reemplazarlos): no
                # se inventa cuál -- se lo pide completo, en texto libre, y
                # ese mensaje se rutea como un turno común (el modelo tiene
                # `consultar_bloqueos` y `resolver_bloqueo`).
                _responder(
                    cur, workspace_id, chat_id, quien,
                    f"Hay más de un bloqueo abierto en «{titulo}». Contame "
                    "cuál se destrabó y cómo, y lo registro.", ahora)
                return
            _pedir_dato_menu_tarea(
                cur, quien, workspace_id, chat_id, accion="destrabar",
                tarea_id=tarea_id, titulo=titulo, ahora=ahora,
                extra={"bloqueo_id": str(abiertos[0]["id"])})
            return

        if accion == "adjuntar_evidencia":
            _pedir_dato_menu_tarea(
                cur, quien, workspace_id, chat_id, accion="adjuntar_evidencia",
                tarea_id=tarea_id, titulo=titulo, ahora=ahora)
            return

        if accion in ("depende_de_otra", "mi_trabajo_depende"):
            if accion == "depende_de_otra":
                fila = M._tarea_para_menu(cur, tarea_id)
                membership_id = fila["responsable_membership_id"] if fila else None
                clave_eleccion = "crear_dependencia_origen"
                pregunta = f"¿De cuál de tus tareas depende «{titulo}»?"
            else:
                membership_id = quien.membership_id
                clave_eleccion = "crear_dependencia_destino"
                pregunta = f"¿Cuál de tus tareas depende de «{titulo}»?"

            candidatas = (
                M.tareas_activas_de(cur, workspace_id, membership_id,
                                    excluir_tarea_id=tarea_id)
                if membership_id else [])
            if not candidatas:
                _encolar_menu_tarea(
                    cur, quien, workspace_id, chat_id, tarea_id, ahora,
                    encabezado="No encontré otras tareas activas para elegir. "
                              "Escribime cuál es y lo vemos.")
                return
            _pedir_eleccion_dependencia(
                cur, quien, workspace_id, chat_id, accion=clave_eleccion,
                tarea_id=tarea_id, titulo=titulo, pregunta=pregunta,
                candidatas=candidatas, ahora=ahora)
            return

        # No debería pasar: `calcular_menu` sólo ofrece los códigos que este
        # bloque conoce. No se inventa nada -- se vuelve a mostrar el menú.
        _encolar_menu_tarea(cur, quien, workspace_id, chat_id, tarea_id, ahora,
                            encabezado=None)
    except Denegado as e:
        _responder(cur, workspace_id, chat_id, quien, str(e), ahora)
    except Exception as e:  # noqa: BLE001
        _routing_incident(cur, quien, e)
        _responder(cur, workspace_id, chat_id, quien,
                  "Perdón, no pude completar eso. Ya quedó registrado para "
                  "que lo revisen.", ahora)


def _resolver_toque_dato_menu_tarea(cur, quien, workspace_id: str, chat_id: int,
                                    args: dict, ahora, *,
                                    pending_action_id: str | None = None) -> None:
    """Alguien tocó una tarea candidata para una dependencia, dentro del
    menú (T2). A diferencia de `_resolver_toque_menu_tarea`, lo que vuelve
    por `campo="eleccion"` no es el código de una acción: es el id de la
    otra tarea elegida -- el mismo patrón que `NecesitaElegir`.

    `pending_action_id` (T2b, trazabilidad): igual que en
    `_resolver_toque_menu_tarea`."""
    accion = args.get("accion")
    otra_tarea_id = args.get("eleccion")
    tarea_id = args.get("tarea_id")

    registrar_auditoria(
        cur, accion="accion_menu_tarea", workspace_id=workspace_id,
        actor_app_user_id=quien.app_user_id, actor_kind="persona",
        detalle={"accion": accion, "tarea_id": tarea_id,
                 "otra_tarea_id": otra_tarea_id})

    if accion == "crear_dependencia_origen":
        call_args = {"origen_tarea_id": otra_tarea_id, "destino_tarea_id": tarea_id,
                    "tipo": "bloqueante"}
    else:
        call_args = {"origen_tarea_id": tarea_id, "destino_tarea_id": otra_tarea_id,
                    "tipo": "bloqueante"}

    try:
        _ejecutar_accion_menu(cur, quien, workspace_id, chat_id,
                              "crear_dependencia", call_args, ahora,
                              pending_action_id=pending_action_id)
    except Denegado as e:
        _responder(cur, workspace_id, chat_id, quien, str(e), ahora)
    except Exception as e:  # noqa: BLE001
        _routing_incident(cur, quien, e)
        _responder(cur, workspace_id, chat_id, quien,
                  "Perdón, no pude completar eso. Ya quedó registrado para "
                  "que lo revisen.", ahora)


def _resumir_dato_menu_tarea(cur, quien, texto: str, modificacion, chat_id: int,
                             workspace_id: str, ahora) -> None:
    """Retoma después de pedir un dato del menú de una tarea (T2): la causa
    de un bloqueo, su resolución o la evidencia. El texto de la persona pasa
    directo como argumento de la herramienta correspondiente -- no hay
    modelo ni Jev de por medio: es un dato que se pidió, no una referencia
    que interpretar."""
    args = modificacion.args
    accion = args.get("accion")
    tarea_id = args.get("tarea_id")
    dato = normalize_visible_text(texto)

    registrar_auditoria(
        cur, accion="accion_menu_tarea", workspace_id=workspace_id,
        actor_app_user_id=quien.app_user_id, actor_kind="persona",
        detalle={"accion": accion, "tarea_id": tarea_id})

    if not dato:
        _responder(cur, workspace_id, chat_id, quien,
                  "Contame un poco más, así lo registro.", ahora)
        return

    if accion == "informar_bloqueo":
        herramienta, call_args = "registrar_bloqueo", {
            "tarea_id": tarea_id, "causa": dato}
    elif accion == "destrabar":
        herramienta, call_args = "resolver_bloqueo", {
            "bloqueo_id": args.get("bloqueo_id"), "resolucion": dato}
    elif accion == "adjuntar_evidencia":
        herramienta, call_args = "adjuntar_evidencia", {
            "tarea_id": tarea_id, "tipo": "texto", "descripcion": dato}
    elif accion == "terminar":
        # ADR 0009: la evidencia que se acaba de pedir viaja en el mismo
        # pedido que el cambio de estado -- una sola vista previa, un solo
        # Confirmar, que registra las dos cosas juntas
        # (`herramientas._actualizar_estado`).
        herramienta, call_args = "actualizar_estado", {
            "tarea_id": tarea_id, "estado": "en_revision", "evidencia_texto": dato}
    elif accion == "pedir_cambios":
        herramienta, call_args = "pedir_cambios_tarea", {
            "tarea_id": tarea_id, "comentario": dato}
    else:
        # No debería pasar: sólo estas acciones abren esta pregunta.
        _responder(cur, workspace_id, chat_id, quien,
                  "Perdón, no encontré a qué acción corresponde esto. Volvé "
                  "a intentarlo desde el menú de la tarea.", ahora)
        return

    try:
        _ejecutar_accion_menu(cur, quien, workspace_id, chat_id, herramienta,
                              call_args, ahora,
                              pending_action_id=modificacion.pregunta_id)
    except Denegado as e:
        _responder(cur, workspace_id, chat_id, quien, str(e), ahora)
    except Exception as e:  # noqa: BLE001
        _routing_incident(cur, quien, e)
        _responder(cur, workspace_id, chat_id, quien,
                  "Perdón, no pude completar eso. Ya quedó registrado para "
                  "que lo revisen.", ahora)


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
                                    workspace_id: str, *,
                                    solo_claras: bool = False
                                    ) -> _ReferenciasResueltas | None:
    """Resuelve, con Jev, cada referencia a tarea que separó `route_intent`
    contra las tareas activas del espacio (T3, `aclaracion-con-botones`).

    `None` sólo cuando no hay ninguna referencia: ahí no hay nada que
    resolver y el turno sigue exactamente igual que sin resolución de
    referencias (T3), sin tocar la base ni la red.

    Sin credencial de Jev (`Config.openrouter_api_key` vacía) Prisma **no
    adivina** (decisión del usuario, 2026-09-24): con referencias en el
    mensaje, se trata igual que si Jev hubiera respondido `JevError` en cada
    una -- se le pide al modelo que pregunte, nunca que elija por su cuenta
    -- y se registra un incidente (sin secretos ni texto del mensaje) para
    que la falta de configuración quede visible.

    `solo_claras` (T9-R1b-2): al contestar una pregunta pendiente sólo cuenta
    una resolución CLARA; el resto (ambigua, varias, ninguna, Jev caído) no
    abre botones ni deja bloque, como si la referencia no estuviera.
    """
    # T7, punto E: una referencia cuyo texto entero es sólo un estado de
    # tarea ("revisión", "en curso"...) nunca es un trabajo -- se descarta
    # antes de tocar Jev o la base, con el mismo criterio que "sin
    # referencias" si no queda ninguna otra.
    trabajos = tuple(t for t in route.trabajos if not _es_referencia_de_estado(t))
    if not trabajos:
        return None

    from . import jev as jev_modulo

    cliente_jev = jev_modulo.desde_base(config.openrouter_api_key)
    if cliente_jev is None:
        _incidente_jev_no_configurado(cur, workspace_id, quien.app_user_id)
        resultados = {referencia: (None, jev_modulo.JevError(
            "No hay credencial de Jev configurada."))
            for referencia in trabajos}
        _auditar_resolucion(cur, quien, workspace_id, resultados)
        if solo_claras:
            return None
        return _ReferenciasResueltas(
            bloque=_bloque_contexto_referencias(resultados, {}), hay_clara=False)

    from .contexto import vocabulario as vocabulario_del_equipo

    tareas = _tareas_activas(cur, workspace_id)
    por_id = {t.id: t for t in tareas}
    vocab = vocabulario_del_equipo(cur, workspace_id)

    resultados = _resolver_en_paralelo(
        cliente_jev, texto=texto, referencias=trabajos, tareas=tareas,
        vocabulario=vocab, quien_escribe=quien.nombre)
    # `resolucion` sólo es `None` con un error; un `(None, None)` rompe el
    # contrato y se trata como una resolución que falló, no como un dato.
    resultados = {
        referencia: ((resolucion, error)
                     if resolucion is not None or error is not None
                     else (None, jev_modulo.JevError(
                         "Jev no devolvió una resolución.")))
        for referencia, (resolucion, error) in resultados.items()}

    _auditar_resolucion(cur, quien, workspace_id, resultados)

    if solo_claras:
        resultados = {
            referencia: (resolucion, error)
            for referencia, (resolucion, error) in resultados.items()
            if error is None and resolucion is not None
            and resolucion.tipo is jev_modulo.TipoResolucion.CLARA
            and resolucion.tarea_id in por_id}
        if not resultados:
            return None

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

    # Dedupe determinístico (T7, punto A2): una referencia ambigua cuyas
    # candidatas son, todas, la tarea CLARA de otra referencia de este mismo
    # mensaje no suma nada para preguntar -- p. ej. un estado que se coló
    # como "trabajo" pese al ajuste del enrutador, y que Jev termina
    # resolviendo ambiguo hacia la misma tarea que otra referencia ya dejó
    # clara. Se descarta entera (ni botón ni línea de texto). Seguro: si le
    # queda aunque sea una candidata sin resolver, se queda -- nunca se
    # descarta "por las dudas".
    claras_ids = set(resueltas_claras.values())
    redundantes = {
        referencia for referencia, (resolucion, error) in resultados.items()
        if error is None and resolucion.tipo is jev_modulo.TipoResolucion.AMBIGUA
        and resolucion.candidatas and set(resolucion.candidatas) <= claras_ids}
    visibles = {referencia: par for referencia, par in resultados.items()
               if referencia not in redundantes}

    # Ambigua CON candidatas (T4, decisión 2): botones, no el texto de
    # siempre. "Varias tareas" (T7, punto C) nunca abre botones para una
    # consulta -- son reservados para la ambigüedad de una sola tarea
    # concreta. El resto -- clara, ninguna, varias tareas, ambigua sin
    # candidatas, Jev caído -- sigue por el bloque de texto.
    #
    # T7, punto G (regresión de C): si el enrutador pide alta de tarea y
    # nada quedó CLARA, una VARIAS sin botón dejaba pasar el alta guiada en
    # silencio (b-0009, "lo mio depende de q mar termine su parte, dejalo
    # anotado") -- acá, y sólo acá, sus candidatas (ya recortadas por Jev a
    # >= 0,1) también entran a botón, para que el caso mixto de b-0005
    # (`_avanzar_aclaracion`, "Es una tarea nueva") las ofrezca en vez de
    # arrancar sola.
    from .llm import IntentAction

    varias_bloquea_alta = (route.action is IntentAction.START_TASK_INTAKE
                           and not hay_clara)
    con_botones = {
        referencia for referencia, (resolucion, error) in visibles.items()
        if error is None and resolucion.candidatas and (
            resolucion.tipo is jev_modulo.TipoResolucion.AMBIGUA
            or (varias_bloquea_alta
                and resolucion.tipo is jev_modulo.TipoResolucion.VARIAS))}
    sin_boton = {referencia: par for referencia, par in visibles.items()
                if referencia not in con_botones}

    pendientes_boton = tuple(
        (referencia, _candidatas_para_botones(
            por_id, resultados[referencia][0], quien.membership_id))
        for referencia in trabajos if referencia in con_botones)

    return _ReferenciasResueltas(
        bloque=_bloque_contexto_referencias(sin_boton, por_id),
        hay_clara=hay_clara, resueltas_claras=resueltas_claras,
        titulos_resueltas=titulos_resueltas, pendientes_boton=pendientes_boton)


def _etiqueta_boton(titulo_corto: str, responsable: str, *, ajena: bool) -> str:
    """El texto de un botón de aclaración (T4, decisión 2): el título YA
    acortado -- las colisiones del conjunto entero ya se resolvieron en
    `_candidatas_para_botones` con `salida.etiquetas_boton_distinguibles`,
    antes de llegar acá -- y el primer nombre del responsable agregado con
    " — " sólo cuando la tarea es de otra persona (§5.10: "quién escribe"
    aporta ahí, no como pista para Jev). El sufijo nunca se recorta."""
    if not ajena or not responsable:
        return titulo_corto
    primer_nombre = responsable.split()[0]
    return f"{titulo_corto} — {primer_nombre}"


def _candidatas_para_botones(tareas_por_id: dict, resolucion, membership_id: str | None
                             ) -> list[dict]:
    """Las candidatas de una referencia ambigua, en el orden de los botones
    (T4, decisión 2): las tareas propias de quien escribe primero, después
    el resto -- dentro de cada grupo, en el orden que mandó Jev
    (`resolucion.candidatas` ya viene ordenada por probabilidad). Una
    candidata que Jev haya devuelto fuera de las tareas leídas no rompe,
    igual que en `jev.resolver_referencia_tarea`: se descarta.

    Los títulos se acortan y desambiguan como UN SOLO conjunto (hallazgo de
    sesión 2 por Telegram: dos candidatas con títulos parecidos no pueden
    cortar igual), antes de repartirlas entre propias y ajenas -- el sufijo
    con el nombre del responsable se agrega recién después, en
    `_etiqueta_boton`, sobre el título ya corto."""
    entradas = []
    for cid in resolucion.candidatas:
        tarea = tareas_por_id.get(cid)
        if tarea is None:
            continue
        es_propia = (membership_id is not None
                    and tarea.responsable_membership_id == membership_id)
        entradas.append((es_propia, tarea))

    # `salida.etiquetas_de_tarea` es la receta única (R2-002, revisión
    # 2026-09-28+1): el ícono de tarea queda antepuesto ANTES del sufijo de
    # responsable que agrega `_etiqueta_boton` más abajo, que tampoco se
    # recorta.
    cortos = etiquetas_de_tarea([tarea.titulo for _, tarea in entradas])

    propias, ajenas = [], []
    for (es_propia, tarea), corto in zip(entradas, cortos):
        etiqueta = _etiqueta_boton(corto, tarea.responsable, ajena=not es_propia)
        item = {"id": tarea.id, "etiqueta": etiqueta, "titulo": tarea.titulo}
        (propias if es_propia else ajenas).append(item)
    return propias + ajenas


# Referencias de sólo estado (T7, punto E): vocabulario cerrado a partir de
# `estado_tarea` (`db/esquema.sql`) y sus formas humanas habituales -- nunca
# frases de los escenarios del banco. El banco real mostraba a Jev
# resolviendo "revisión" (separada como "trabajo" por el enrutador) contra
# una tarea cuyo título comparte raíz ("Revisar tablero..."), un falso
# positivo que nunca debería haber llegado a la red: una referencia que sólo
# nombra un estado no es un trabajo.
ESTADOS_REFERENCIA_SOLA = frozenset({
    # `estado_tarea` tal cual (improbable en lenguaje natural, pero es la
    # fuente formal del vocabulario).
    "propuesta", "pendiente_aprobacion", "asignada", "en_curso", "bloqueada",
    "en_revision", "terminada", "cancelada",
    # Formas humanas habituales de esos estados. "en revisión"/"en curso" se
    # reducen a "revision"/"curso" porque el "en" líder se recorta antes de
    # comparar, igual que "a"/"la"/"el" (ver `_normalizar_referencia_estado`).
    "revision", "curso", "terminado", "terminada", "listo", "lista",
    "hecho", "hecha", "bloqueado", "bloqueada", "pendiente",
    "resuelto", "resuelta", "cancelado", "cancelada",
})
# Artículos y preposiciones líderes que no cambian que una referencia sea "de
# estado" -- "la revisión", "a resuelto".
_ARTICULOS_LIDER_ESTADO = ("a", "la", "el", "en")


def _normalizar_referencia_estado(texto: str) -> str:
    """Minúsculas, sin acentos, sin artículo/preposición líder -- para
    comparar contra `ESTADOS_REFERENCIA_SOLA` sin depender de cómo separó el
    enrutador la referencia."""
    sin_acentos = unicodedata.normalize("NFKD", texto.strip().casefold())
    sin_acentos = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    palabras = sin_acentos.split()
    while palabras and palabras[0] in _ARTICULOS_LIDER_ESTADO:
        palabras = palabras[1:]
    return " ".join(palabras)


def _es_referencia_de_estado(texto: str) -> bool:
    """Verdadero si toda la referencia -- ya sin artículo/preposición líder --
    es sólo un estado de tarea, nunca un trabajo real (T7, punto E)."""
    return _normalizar_referencia_estado(texto) in ESTADOS_REFERENCIA_SOLA


def _tareas_activas(cur, workspace_id: str) -> list:
    """Tareas activas del espacio (no `terminada` ni `cancelada`), con lo
    que necesita la receta de Jev -- título, área, responsable y, si tiene,
    la causa de sus bloqueos abiertos (T7, punto H) -- leídas con el mismo
    cursor con RLS que ya tiene el turno: nunca otra conexión, nunca otro
    espacio. `responsable_membership_id` no viaja a Jev (no entra en
    `criterio()`): sólo sirve, del lado de acá, para ordenar los botones
    (T4, decisión 2)."""
    from . import jev as jev_modulo

    cur.execute(
        """select t.id, t.titulo, a.nombre as area,
                  coalesce(i.nombre, '') as responsable,
                  t.responsable_membership_id,
                  (select string_agg(b.causa, '; ' order by b.abierto_en)
                     from blocker b
                    where b.task_id = t.id and b.resuelto_en is null) as causas_bloqueo
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
                                          if f["responsable_membership_id"] else None),
                causas_bloqueo=f["causas_bloqueo"])
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
        elif resolucion.tipo is jev_modulo.TipoResolucion.VARIAS:
            # T7, punto C: abarca varias tareas de verdad (un área, lo de una
            # persona, algo genérico) -- nunca botones, nunca elegir por su
            # cuenta. Si consultan, contesta sobre todas; si piden cambiar
            # algo, pregunta cuál es (en texto).
            candidatas = "; ".join(
                f"«{tareas_por_id[cid].titulo}» ({cid})"
                for cid in resolucion.candidatas if cid in tareas_por_id)
            if candidatas:
                lineas.append(
                    f"- «{referencia}» abarca varias tareas: {candidatas}. Si "
                    "te preguntan o consultan por ellas, contestá sobre "
                    "todas. Si piden cambiar algo, preguntá primero a cuál "
                    "se refieren, en texto -- nunca elijas ni actúes por tu "
                    "cuenta.")
            else:
                lineas.append(
                    f"- «{referencia}» abarca varias tareas, pero ninguna "
                    "coincide con las activas del espacio. No inventes: "
                    "preguntá si hace falta para responder o actuar.")
        else:  # NINGUNA
            lineas.append(
                f"- «{referencia}» no coincide con ninguna tarea activa del "
                "espacio. No es una tarea: no la inventes ni la trates como "
                "una. Si hace falta para responder o actuar y no tenés otra "
                "cosa clara para usar, preguntá.")
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


def _incidente_jev_no_configurado(cur, workspace_id: str,
                                  app_user_id: str | None) -> None:
    """El mensaje traía referencias a tarea pero no hay credencial de Jev
    (`PRISMA_OPENROUTER_API_KEY`): Prisma le pide al modelo que pregunte en
    vez de adivinar (decisión del usuario, 2026-09-24), y esto queda
    registrado para que la falta de configuración no pase inadvertida. Sin
    secretos, igual que `_routing_incident` -- el aviso a la administración
    SÍ lleva el mensaje que disparó esto (Constitución §2/§10/§12,
    corrección del usuario, 2026-09-28), nunca la persona."""
    registrar_incidente(
        cur, workspace_id,
        "El mensaje tenía referencias a tarea, pero no hay credencial de "
        "Jev configurada (PRISMA_OPENROUTER_API_KEY).",
        app_user_id=app_user_id)


def _routing_incident(cur, quien, error) -> None:
    cur.execute(
        """insert into incident (workspace_id, severidad, resumen_sanitizado)
           values (%s, 'media', %s)""",
        (quien.workspace_id,
         f"Falló el enrutamiento tipado ({type(error).__name__})."),
    )


NOTICIA_NEUTRA_INCIDENTE = "No pude completar eso. Ya quedó registrado para revisarlo."

# Etapas nombradas (T2b, corrección de trazabilidad, 2026-09-25): en qué
# punto de entrada se atrapó la excepción no manejada. No pretenden cubrir
# cada paso interno posible (enrutar, resolver referencias, armar la vista
# previa, el turno del modelo, correr una herramienta, mandar la respuesta)
# -- eso ya tiene su propio incidente puntual donde corresponde
# (`_routing_incident`, `agente._incidente`, etc.), sin tocar. Éstas son las
# etapas de la red de contención general en el punto de entrada, no en el
# paso interno.
ETAPA_TURNO_TEXTO = "turno_texto"
ETAPA_TOQUE_BOTON = "toque_boton"
ETAPA_ACTIVACION = "activacion"
ETAPA_ACCION_MENU = "accion_menu"

def _routing_incident(cur, quien, error) -> None:
    registrar_incidente(
        cur, quien.workspace_id,
        f"Falló el enrutamiento tipado ({type(error).__name__}).",
        app_user_id=quien.app_user_id)


def reportar_incidente_no_manejado(conn, *, workspace_id: str | None,
                                   chat_id: int | None, tg_user: int | None,
                                   error: Exception, etapa: str,
                                   referencia_tipo: str | None = None,
                                   referencia_id: str | None = None) -> None:
    """Red de contención final para un update de Telegram (mensaje o toque)
    que levantó algo que ningún camino específico atajó -- decisión del
    usuario, 2026-09-25: un error nunca pasa en silencio. Evidencia de la
    sesión real: un `UndefinedColumn` hacía que Prisma saltara el mensaje
    sin ninguna respuesta ni incidente, invisible hasta que alguien lo
    notaba por otro lado.

    Quien llama ya revirtió la transacción que falló (`conn.rollback()`);
    ésta abre una nueva -- la vieja ya no sirve. Nunca deja escapar una
    excepción propia: si hasta este resguardo falla (por ejemplo, la base
    sigue caída), el aviso se pierde pero no se reintenta ni se cuelga el
    ciclo que sigue escuchando updates (`local.Escucha.recibir` reusa esta
    misma función).

    Corrección del usuario sobre trazabilidad (2026-09-25): el incidente
    tiene que poder encontrarse. Se intenta avisar a la persona PRIMERO --
    sin tocar `incident` todavía -- porque `prisma_app` sólo tiene `insert`
    sobre esa tabla (`db/esquema.sql`, "grant insert on ... incident ... to
    prisma_app"): no hay una segunda pasada que la actualice con si el
    aviso funcionó. El incidente se registra una sola vez, al final, ya con
    el resultado del aviso resuelto (`notificado_en`, y una nota en el
    resumen si no se pudo avisar) -- nunca dos filas para un mismo fallo."""
    if workspace_id is None:
        return

    from datetime import datetime, timezone

    ahora = datetime.now(timezone.utc)
    app_user_id = None
    notificado_en = None
    nota_aviso = None

    if chat_id is None or tg_user is None:
        nota_aviso = "No se avisó: no se identificó chat o usuario."
    else:
        try:
            avisado = False
            with espacio(conn, workspace_id) as cur:
                try:
                    quien = identificar_en_espacio(cur, tg_user, workspace_id)
                except Denegado:
                    quien = None
                if quien is None:
                    nota_aviso = ("No se avisó: la persona no se identificó "
                                  "en el espacio.")
                else:
                    app_user_id = quien.app_user_id
                    # El aviso es la respuesta al mensaje que falló (T9-R2).
                    if referencia_tipo == REFERENCIA_INBOUND_MESSAGE:
                        atar_al_entrante(cur, referencia_id)
                    enqueue_outbox(
                        cur, workspace_id=workspace_id, chat_id=chat_id,
                        recipient_membership_id=quien.membership_id,
                        text=NOTICIA_NEUTRA_INCIDENTE, scheduled_for=ahora,
                        dedupe_key=(f"{workspace_id}:incidente-no-manejado:"
                                   f"{chat_id}:{ahora.timestamp()}"),
                        is_response=True)
                    avisado = True
            conn.commit()
            # Sólo cuenta como avisado si de verdad se encoló el aviso: marcar
            # `notificado_en` sin haber avisado a nadie sería mentir.
            if avisado:
                notificado_en = ahora
        except Exception:  # noqa: BLE001
            try:
                conn.rollback()
            except Exception:  # noqa: BLE001
                pass
            nota_aviso = "No se avisó: falló el envío del aviso."

    resumen = f"Excepción no manejada en '{etapa}' ({type(error).__name__})."
    if nota_aviso:
        resumen += f" {nota_aviso}"

    try:
        with espacio(conn, workspace_id) as cur:
            registrar_incidente(
                cur, workspace_id, resumen, severidad="alta",
                referencia_cruda=str(error)[:2000], etapa=etapa,
                referencia_tipo=referencia_tipo, referencia_id=referencia_id,
                chat_id=chat_id, app_user_id=app_user_id,
                notificado_en=notificado_en)
        conn.commit()
    except Exception:  # noqa: BLE001
        # Ni siquiera el incidente se pudo registrar (decisión del usuario,
        # T2b): no se reintenta ni se propaga -- se pierde el registro, no
        # el ciclo que sigue escuchando.
        try:
            conn.rollback()
        except Exception:  # noqa: BLE001
            pass


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
        r = pedido_telegram(
            cliente.post, f"https://api.telegram.org/bot{token}/setWebhook",
            json={"url": f"{config.base_url}/telegram/{slug}",
                  "secret_token": config.webhook_secret,
                  "allowed_updates": ["message", "callback_query"]})
        resultado[slug] = r.status_code == 200 and r.json().get("ok", False)
    return resultado
