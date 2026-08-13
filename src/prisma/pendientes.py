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
from datetime import datetime
from typing import Any

import psycopg

from .autoridad import Denegado, Solicitante

# Lo que Telegram manda de vuelta al apretar un botón. El tope son 64 bytes,
# así que viaja un token corto y la acción queda en la base.
CALLBACK_PREFIJO = "p:"


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


@dataclass(frozen=True)
class Resuelta:
    """Lo que quedó para ejecutar. `herramienta` es None si se canceló."""
    herramienta: str | None
    args: dict[str, Any]
    cancelada: bool
    task_id: str | None = None


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
              preview: dict[str, Any] | None = None) -> Pendiente:
    """Congela una acción y deja preparadas sus opciones.

    Sin `opciones` la pregunta es confirmar o cancelar. Con `campo` y
    `opciones`, cada elección completa ese argumento con su valor.
    """
    cur.execute(
        """insert into pending_action
             (workspace_id, membership_id, herramienta, args, campo, resumen,
               vence_en, chat_id, draft_id, draft_version, preview)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           returning id, estado""",
        (quien.workspace_id, quien.membership_id, herramienta,
         json.dumps(args, ensure_ascii=False), campo, resumen, vence_en,
          chat_id, draft_id, draft_version,
          json.dumps(preview, ensure_ascii=False) if preview is not None else None))
    fila = cur.fetchone()
    pid = str(fila["id"])

    a_crear = opciones if opciones is not None else [("Confirmar", True),
                                                     ("Cancelar", False)]
    creadas = [
        _crear_opcion(cur, quien.workspace_id, pid, etiqueta, valor, orden)
        for orden, (etiqueta, valor) in enumerate(a_crear)]

    return Pendiente(id=pid, herramienta=herramienta, args=args,
                     resumen=resumen, estado=fila["estado"], campo=campo,
                     opciones=creadas)


def _crear_opcion(cur, workspace_id: str, pending_action_id: str,
                  etiqueta: str, valor: Any, orden: int) -> Opcion:
    token = secrets.token_urlsafe(12)
    cur.execute(
        """insert into pending_action_option
             (workspace_id, pending_action_id, token, etiqueta, valor, orden)
           values (%s, %s, %s, %s, %s, %s)""",
        (workspace_id, pending_action_id, token, etiqueta,
         json.dumps(valor, ensure_ascii=False), orden))
    return Opcion(token=token, etiqueta=etiqueta, valor=valor)


def buscar(cur: psycopg.Cursor, pendiente_id: str) -> Pendiente | None:
    cur.execute(
        """select id, herramienta, args, campo, resumen, estado
             from pending_action where id = %s""",
        (pendiente_id,))
    f = cur.fetchone()
    if not f:
        return None
    return Pendiente(id=str(f["id"]), herramienta=f["herramienta"],
                     args=f["args"], resumen=f["resumen"], estado=f["estado"],
                     campo=f["campo"], opciones=opciones(cur, pendiente_id))


def opciones(cur: psycopg.Cursor, pendiente_id: str) -> list[Opcion]:
    cur.execute(
        """select token, etiqueta, valor from pending_action_option
            where pending_action_id = %s order by orden""",
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

    return Resuelta(herramienta=f["herramienta"], args=f["args"] or {},
                    cancelada=f["cancelada"])


def es_borrador(cur: psycopg.Cursor, token: str) -> bool:
    cur.execute(
        """select p.draft_id is not null as es_borrador
             from pending_action_option o
             join pending_action p on p.id = o.pending_action_id
            where o.token = %s""", (token,))
    fila = cur.fetchone()
    return bool(fila and fila["es_borrador"])


def resolver_borrador(cur: psycopg.Cursor, workspace_id: str, token: str,
                      telegram_user_id: int) -> Resuelta | None:
    """Commit through prisma_gateway using DB identity and DB time."""
    cur.execute("select * from confirmar_borrador_tarea(%s, %s, %s)",
                (workspace_id, token, telegram_user_id))
    f = cur.fetchone()
    if f["resultado"] == "ajena":
        raise Denegado("Eso se lo pregunté a otra persona del equipo.")
    if f["resultado"] in ("inexistente", "usada", "vencida", "obsoleta"):
        return None
    if f["resultado"] == "cancelada":
        return Resuelta(herramienta=None, args={}, cancelada=True)
    return Resuelta(herramienta=None, args={}, cancelada=False,
                    task_id=str(f["task_id"]))
