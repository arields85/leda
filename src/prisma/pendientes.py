"""Acciones pendientes: trabajo entendido que todavía no se ejecutó.

Una acción pendiente es una herramienta con sus argumentos, congelada hasta
que una persona hace un acto explícito: confirmarla, o elegir entre opciones.

Las dos cosas son la misma. "¿Confirmás que muevo la fecha?" y "¿Marcos o
Martín?" se diferencian sólo en qué completa la respuesta: la primera decide
si la acción va, la segunda le llena un argumento que faltaba.

Por qué importa para que Prisma no invente: una opción elegida devuelve un
identificador exacto. Cuando la persona escribe "marcos", hay que adivinar de
nuevo entre Marcos y Martín. Cuando elige, no hay nada que adivinar.

Este módulo no ejecuta nada. Resuelve quién puede, si todavía vale, y qué
había que hacer; ejecutar sigue siendo trabajo de `herramientas.ejecutar`, que
es el único camino a la base y el que verifica la autoridad.
"""

from __future__ import annotations

import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import psycopg

from .autoridad import Denegado, Solicitante
from .salida import normalize_visible_text, prepare_buttons, prepare_payload

# Lo que Telegram manda de vuelta al apretar un botón. El tope son 64 bytes,
# así que viaja un token corto y la acción queda en la base.
CALLBACK_PREFIJO = "p:"

# Cuánto espera Prisma la corrección después de un toque en Modificar.
VENTANA_MODIFICACION = timedelta(minutes=30)


@dataclass(frozen=True)
class Opcion:
    token: str
    etiqueta: str
    valor: Any = None


@dataclass(frozen=True)
class Pendiente:
    id: str
    herramienta: str
    args: dict[str, Any]
    resumen: str
    estado: str
    campo: str | None = None
    opciones: list[Opcion] = field(default_factory=list)
    huella: str | None = None


@dataclass(frozen=True)
class Resuelta:
    """Lo que quedó para ejecutar. `herramienta` es None si se canceló."""
    herramienta: str | None
    args: dict[str, Any]
    cancelada: bool
    task_id: str | None = None
    replay: bool = False
    pending_action_id: str | None = None
    # La huella que se guardó al mostrar la vista previa (ADR 0005, decisión
    # 1). `ejecutar` la vuelve a comparar antes de aplicar nada.
    huella: str | None = None
    # Modificar (T3): cierra sin aplicar nada, igual que `cancelada`, pero
    # además queda registrado que el próximo mensaje de esta persona en este
    # chat es una corrección -- ver `reclamar_modificacion_abierta`.
    modificada: bool = False


@dataclass(frozen=True)
class ModificacionAbierta:
    """El contexto de una Modificación todavía no leída por ningún turno.

    Reusa lo que ya quedó en la fila de `pending_action` desde que se armó la
    vista previa original: no hace falta guardarlo aparte.
    """
    pending_action_id: str
    herramienta: str
    args: dict[str, Any]
    resumen: str


def callback_data(opcion: Opcion) -> str:
    return f"{CALLBACK_PREFIJO}{opcion.token}"


def token_de(callback: str) -> str | None:
    """Extrae el token de un callback_data. None si no es nuestro."""
    if not callback.startswith(CALLBACK_PREFIJO):
        return None
    return callback[len(CALLBACK_PREFIJO):] or None


def registrar(cur: psycopg.Cursor, quien: Solicitante, *, herramienta: str,
              args: dict[str, Any], resumen: str, vence_en: datetime,
              campo: str | None = None,
              opciones: list[tuple[str, Any]] | None = None,
              chat_id: int | None = None, draft_id: str | None = None,
              draft_version: int | None = None,
              preview: dict[str, Any] | None = None,
              huella: str | None = None) -> Pendiente:
    """Congela una acción y deja preparadas sus opciones.

    Sin `opciones` la pregunta es confirmar o cancelar. Con `campo` y
    `opciones`, cada elección completa ese argumento con su valor.

    `huella` es la del estado que se leyó para armar la vista previa (ADR
    0005, decisión 1). La ponen las herramientas que escriben; el resto de
    los llamados a `registrar` (elegir, borrador) no la usan.
    """
    resumen = normalize_visible_text(resumen)
    a_crear = opciones if opciones is not None else [("Confirmar", True),
                                                      ("Cancelar", False)]
    prepare_payload(resumen, dedupe_key="pending", has_buttons=True)
    prepare_buttons([(etiqueta, "p:placeholder") for etiqueta, _ in a_crear])
    cur.execute(
        """insert into pending_action
             (workspace_id, membership_id, herramienta, args, campo, resumen,
               vence_en, chat_id, draft_id, draft_version, preview, huella)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           returning id, estado""",
        (quien.workspace_id, quien.membership_id, herramienta,
         json.dumps(args, ensure_ascii=False), campo, resumen, vence_en,
          chat_id, draft_id, draft_version,
          json.dumps(preview, ensure_ascii=False) if preview is not None else None,
          huella))
    fila = cur.fetchone()
    pid = str(fila["id"])

    creadas = [
        _crear_opcion(cur, quien.workspace_id, pid, etiqueta, valor, orden)
        for orden, (etiqueta, valor) in enumerate(a_crear)]

    return Pendiente(id=pid, herramienta=herramienta, args=args,
                     resumen=resumen, estado=fila["estado"], campo=campo,
                     opciones=creadas, huella=huella)


def _crear_opcion(cur, workspace_id: str, pending_action_id: str,
                  etiqueta: str, valor: Any, orden: int) -> Opcion:
    token = secrets.token_urlsafe(12)
    etiqueta = normalize_visible_text(etiqueta)
    prepare_buttons([(etiqueta, callback_data(Opcion(token, etiqueta)))])
    cur.execute(
        """insert into pending_action_option
             (workspace_id, pending_action_id, token, etiqueta, valor, orden)
           values (%s, %s, %s, %s, %s, %s)""",
        (workspace_id, pending_action_id, token, etiqueta,
         json.dumps(valor, ensure_ascii=False), orden))
    return Opcion(token=token, etiqueta=etiqueta, valor=valor)


def buscar(cur: psycopg.Cursor, pendiente_id: str) -> Pendiente | None:
    cur.execute(
        """select id, herramienta, args, campo, resumen, estado, huella
             from pending_action where id = %s""",
        (pendiente_id,))
    f = cur.fetchone()
    if not f:
        return None
    return Pendiente(id=str(f["id"]), herramienta=f["herramienta"],
                     args=f["args"], resumen=f["resumen"], estado=f["estado"],
                     campo=f["campo"], opciones=opciones(cur, pendiente_id),
                     huella=f["huella"])


def opciones(cur: psycopg.Cursor, pendiente_id: str) -> list[Opcion]:
    cur.execute(
        """select token, etiqueta, valor from pending_action_option
            where pending_action_id = %s and activa order by orden""",
        (pendiente_id,))
    return [Opcion(token=f["token"], etiqueta=f["etiqueta"], valor=f["valor"])
            for f in cur.fetchall()]


def opcion_por_etiqueta(cur: psycopg.Cursor, pendiente_id: str,
                        etiqueta: str) -> Opcion:
    for o in opciones(cur, pendiente_id):
        if o.etiqueta == etiqueta:
            return o
    raise LookupError(f"La acción {pendiente_id} no ofrece '{etiqueta}'.")


def resolver(cur: psycopg.Cursor, token: str, *, app_user_id: str,
             ahora: datetime) -> Resuelta | None:
    """Resuelve por el token de una opción.

    Devuelve None cuando no hay nada que ejecutar — el token no existe, ya se
    usó, o la acción venció — y lanza `Denegado` cuando la aprieta alguien
    que no es su destinatario. Son casos distintos a propósito: lo primero se
    le cuenta a la persona con naturalidad, lo segundo es un intento de actuar
    en nombre de otro.
    """
    cur.execute(
        """select p.draft_id
             from pending_action_option o
             join pending_action p on p.id = o.pending_action_id
            where o.token = %s""", (token,))
    pendiente = cur.fetchone()
    if pendiente and pendiente["draft_id"] is not None:
        raise Denegado("La confirmación de tareas requiere el canal autenticado.")

    cur.execute("select * from resolver_pendiente(%s, %s, %s)",
                (token, app_user_id, ahora))
    f = cur.fetchone()

    if f["resultado"] == "ajena":
        raise Denegado("Eso se lo pregunté a otra persona del equipo.")
    if f["resultado"] in ("inexistente", "usada", "vencida"):
        return None
    if f["resultado"] == "modificada":
        return Resuelta(herramienta=f["herramienta"], args=f["args"] or {},
                        cancelada=False, modificada=True, huella=f.get("huella"))

    return Resuelta(herramienta=f["herramienta"], args=f["args"] or {},
                    cancelada=f["cancelada"], huella=f.get("huella"))


def reclamar_modificacion_abierta(cur: psycopg.Cursor, quien: Solicitante,
                                  chat_id: int,
                                  ahora: datetime) -> ModificacionAbierta | None:
    """Reclama, de forma atómica y de un solo uso, la última Modificación
    abierta de esta persona en este chat (T3, ADR 0005 decisión 1).

    Sólo puede haber una vigente a la vez -- `resolver_pendiente` invalida
    cualquier otra al abrir una nueva --, así que "la más reciente sin leer y
    sin vencer" identifica una sola fila sin ambigüedad. `for update skip
    locked` la reclama sin bloquear: dos turnos concurrentes para la misma
    persona no pueden leer -- ni consumir -- la misma Modificación dos veces.

    La corrección tiene que llegar dentro de `VENTANA_MODIFICACION` desde que
    se tocó Modificar, aunque la propuesta en sí venza mucho después: un
    mensaje de horas más tarde ya es otra conversación, y tratarlo como
    corrección le haría saltear el enrutador de intención.
    """
    cur.execute(
        """update pending_action
              set modificacion_consumida_en = %(ahora)s
            where id = (
                    select id from pending_action
                     where workspace_id = %(ws)s and membership_id = %(mid)s
                       and chat_id = %(chat)s and modificar_pedido_en is not null
                       and vence_en > %(ahora)s and modificacion_consumida_en is null
                       and modificar_pedido_en > %(ahora)s - %(ventana)s
                     order by modificar_pedido_en desc
                     limit 1
                     for update skip locked)
            returning id, herramienta, args, resumen""",
        {"ahora": ahora, "ws": quien.workspace_id, "mid": quien.membership_id,
         "chat": chat_id, "ventana": VENTANA_MODIFICACION})
    f = cur.fetchone()
    if not f:
        return None
    return ModificacionAbierta(pending_action_id=str(f["id"]),
                               herramienta=f["herramienta"],
                               args=f["args"] or {}, resumen=f["resumen"])


def es_borrador(cur: psycopg.Cursor, token: str) -> bool:
    cur.execute(
        """select p.draft_id is not null as es_borrador
             from pending_action_option o
             join pending_action p on p.id = o.pending_action_id
            where o.token = %s""", (token,))
    fila = cur.fetchone()
    return bool(fila and fila["es_borrador"])


def resolver_borrador(cur: psycopg.Cursor, workspace_id: str, token: str,
                       telegram_user_id: int, chat_id: int) -> Resuelta | None:
    """Commit through prisma_gateway using DB identity and DB time."""
    cur.execute("select * from resolver_ingreso_borrador(%s, %s, %s, %s)",
                (workspace_id, token, telegram_user_id, chat_id))
    f = cur.fetchone()
    if f["resultado"] == "ajena":
        raise Denegado("Eso se lo pregunté a otra persona del equipo.")
    if f["resultado"] in ("inexistente", "usada", "vencida", "obsoleta"):
        return None
    if f["resultado"] == "cancelada":
        return Resuelta(herramienta=None, args={}, cancelada=True,
                        replay=f.get("replay", False),
                        pending_action_id=str(f["pending_action_id"])
                        if f.get("pending_action_id") else None)
    return Resuelta(herramienta=None, args={}, cancelada=False,
                    task_id=str(f["task_id"]), replay=f.get("replay", False),
                    pending_action_id=str(f["pending_action_id"])
                    if f.get("pending_action_id") else None)
