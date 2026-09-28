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
from .salida import (ETIQUETA_CANCELAR, ETIQUETA_CONFIRMAR, ICONO_SALIR_OPCIONES,
                     ICONO_VER_MAS, con_icono, etiquetas_coinciden,
                     normalize_visible_text, prepare_buttons, prepare_payload)

# Lo que Telegram manda de vuelta al apretar un botón. El tope son 64 bytes,
# así que viaja un token corto y la acción queda en la base.
CALLBACK_PREFIJO = "p:"

# Cuánto espera Prisma la corrección después de un toque en Modificar.
VENTANA_MODIFICACION = timedelta(minutes=30)

# `herramienta` reservada para una acción pendiente armada por
# `ofrecer_opciones` (T1, ADR 0007 "Prisma orienta, no charla"): nunca es un
# nombre real del `REGISTRO` de `herramientas.py` -- lo arma `agente.py`
# (`_encolar_opciones_modelo`) y lo intercepta `gateway._toque` antes de
# llegar a `H.ejecutar`, igual que `_SENTINEL_ACLARACION` en `gateway.py`.
# Vive acá, no en `gateway.py`, porque las dos puntas lo necesitan: la
# herramienta que arma la pregunta está del lado del agente, el toque que la
# resuelve está del lado del gateway.
SENTINEL_OPCIONES_MODELO = "_opciones_modelo"

# T2 (`prisma-orienta`, ADR 0007 §4.6): el menú de acciones de una tarea.
# Dos sentinelas más, viven acá por el mismo motivo que el de arriba -- lo
# arma y lo intercepta `gateway.py`, en dos puntas distintas (armar la
# pregunta / resolver el toque o el próximo mensaje).
#
# `SENTINEL_MENU_TAREA` es el menú en sí -- cada opción es una acción del
# diseño §4.6, calculada por código (`menu_tarea.calcular_menu`), nunca por
# el modelo. Tocar una opción no retoma la conversación: cada acción sigue
# su propio camino (una lectura, la vista previa de una herramienta que ya
# existe, o un dato que hace falta pedir).
#
# `SENTINEL_DATO_MENU_TAREA` es el dato que le falta a una acción del menú
# para armar su vista previa. Tiene dos formas: una elección entre
# candidatos conocidos (qué otra tarea, para una dependencia -- se resuelve
# como cualquier toque, con `campo="eleccion"` y botones) o un texto libre
# que la persona escribe (la causa de un bloqueo, su resolución, la
# evidencia -- capturado con el mismo mecanismo que "Ninguna, lo escribo",
# T4 `aclaracion-con-botones`: `marcar_para_corregir` +
# `reclamar_modificacion_abierta`, sin botones).
SENTINEL_MENU_TAREA = "_menu_tarea"
SENTINEL_DATO_MENU_TAREA = "_dato_menu_tarea"
# Marca en `args` del aviso de entrega al aprobador (ADR 0009), que comparte
# `SENTINEL_MENU_TAREA` con el menú general de la tarea: es lo que permite
# retirarlo sin tocar ese menú (`retirar_avisos_de_entrega`).
AVISO_ENTREGA = "entrega"

# La salida que ofrece siempre una elección con botones (T1, ADR 0007 punto
# 1: "siempre hay una salida"). Vive acá, no repetida en cada lugar que la
# usa, para que el menú de tarea (T2) y `ofrecer_opciones` (T1) muestren
# exactamente la misma etiqueta.
ETIQUETA_SALIR_OPCIONES = con_icono("Quiero consultar otra cosa", ICONO_SALIR_OPCIONES)

# T3 (`prisma-orienta`, ADR 0007 punto 3): la lista de tareas que arma el
# servidor cuando el modelo usa `consultar_tareas` pagina con este botón, sin
# volver a llamar al modelo -- mismo lugar que `ETIQUETA_SALIR_OPCIONES` para
# que `agente.py` (arma la primera página) y `gateway.py` (arma las
# siguientes al tocar "Ver más") muestren la misma etiqueta.
ETIQUETA_VER_MAS = con_icono("Ver más", ICONO_VER_MAS)


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
    a_crear = opciones if opciones is not None else [(ETIQUETA_CONFIRMAR, True),
                                                      (ETIQUETA_CANCELAR, False)]
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
    """Busca una opción por su etiqueta, sin importar el ícono de categoría
    (`salida.etiquetas_coinciden`): así una prueba o el banco que sigue
    tocando "Confirmar" sin ícono encuentra igual el botón real, ya armado
    como "✅ Confirmar"."""
    for o in opciones(cur, pendiente_id):
        if etiquetas_coinciden(o.etiqueta, etiqueta):
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


def pending_action_id_de(cur: psycopg.Cursor, token: str) -> str | None:
    """El id de la acción pendiente dueña de un token de opción.

    Lo necesita "Ninguna, lo escribo" (T4, `aclaracion-con-botones`,
    decisión 4): esa fila ya se resolvió por el camino de siempre (con
    `campo="eleccion"`, para que la elección vuelva en `args`), así que hace
    falta el id aparte para poder marcarla como el contexto que retoma el
    próximo turno (`marcar_para_corregir`)."""
    cur.execute(
        "select pending_action_id from pending_action_option where token = %s",
        (token,))
    fila = cur.fetchone()
    return str(fila["pending_action_id"]) if fila else None


def marcar_para_corregir(cur: psycopg.Cursor, quien: Solicitante,
                         pending_action_id: str, chat_id: int,
                         ahora: datetime) -> None:
    """Deja `pending_action_id` como el contexto que va a leer el próximo
    turno de esta persona en este chat -- el mismo mecanismo que Modificar
    (T3): `modificar_pedido_en`/`modificacion_consumida_en`/
    `VENTANA_MODIFICACION` y `reclamar_modificacion_abierta`, que no
    distinguen de qué acción pendiente salió la marca.

    No se puede reusar la rama de `resolver_pendiente` que hace esto mismo
    para Modificar tal cual: esa rama exige `campo is null` para reconocer
    el valor especial `"modificar"`, y esta fila ya usa `campo="eleccion"`
    para que la elección del botón vuelva en `args`. Se marca acá, después
    de resolver, con el mismo efecto en las dos columnas que usa
    `reclamar_modificacion_abierta` -- esa consulta no mira `estado`, así
    que no importa que esta fila haya quedado `resuelta` y no `cancelada`."""
    cur.execute(
        "update pending_action set modificar_pedido_en = %s where id = %s",
        (ahora, pending_action_id))
    cur.execute(
        """update pending_action
              set modificacion_consumida_en = %s
            where workspace_id = %s and membership_id = %s and chat_id = %s
              and modificar_pedido_en is not null
              and modificacion_consumida_en is null and id <> %s""",
        (ahora, quien.workspace_id, quien.membership_id, chat_id,
         pending_action_id))


def retirar_avisos_de_entrega(cur: psycopg.Cursor, workspace_id: str, tarea_id: str,
                              aprobador_membership_id: str,
                              ahora: datetime) -> list[str]:
    """T6i (`odd/tasks/prisma-orienta.md`; ADR 0009, enmienda 2026-09-27):
    vence cualquier aviso de entrega que el aprobador todavía tenga
    `esperando` sobre esta tarea -- lo llama `herramientas` cuando evidencia
    nueva reemplaza uno vigente. Mismo criterio que
    `despachador._preview_vigente` para una vista previa superada (queda
    'vencida', no 'resuelta' ni 'cancelada': nadie decidió nada, la vista
    previa dejó de ser la que corresponde mostrar) y mismo patrón de dos
    pasos que `ingreso_tareas._cancel` (la fila y, después, sus opciones).

    Nunca toca el menú general de la tarea (`_encolar_menu_tarea`), aunque
    use el mismo `herramienta=SENTINEL_MENU_TAREA` con el mismo
    `tarea_id` en `args`: sólo el aviso de entrega lleva
    `args.aviso = AVISO_ENTREGA` (lo pone `herramientas._notificar_entrega_
    al_aprobador`), y el filtro es por esa marca, no por las etiquetas de
    los botones. Alcance estricto por `workspace_id` + `membership_id` (el
    aprobador) + `tarea_id`: nunca una acción pendiente de otra persona ni
    de otra tarea.

    Devuelve los ids retirados (vacío si no había ninguno esperando, el caso
    normal fuera de este escenario)."""
    cur.execute(
        """update pending_action p
              set estado = 'vencida', resuelta_en = %(ahora)s
            where p.workspace_id = %(ws)s
              and p.membership_id = %(mid)s
              and p.herramienta = %(herramienta)s
              and p.estado = 'esperando'
              and p.args ->> 'tarea_id' = %(tarea_id)s
              and p.args ->> 'aviso' = %(aviso)s
            returning p.id""",
        {"ahora": ahora, "ws": workspace_id, "mid": aprobador_membership_id,
         "herramienta": SENTINEL_MENU_TAREA, "tarea_id": str(tarea_id),
         "aviso": AVISO_ENTREGA})
    ids = [str(f["id"]) for f in cur.fetchall()]
    if ids:
        cur.execute(
            "update pending_action_option set activa = false "
            "where pending_action_id = any(%s::uuid[])",
            (ids,))
    return ids


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
