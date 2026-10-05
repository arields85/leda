"""Un turno del motor de conversación (`odd/tasks/prueba-chica-del-motor.md`, sección 4).

(1) Lee el estado de la persona, sus tareas y sus últimos turnos; (2) la IA elige jugadas de
la lista cerrada y nombra las tareas por un alias; (3) el código maneja cada jugada con el
manejador de su ficha; (4) el resultado son hechos; (5) la IA redacta desde los hechos, una
respuesta por mensaje, que sale por el outbox; (6) todo queda en el registro de turnos.

La lista cerrada (`JUGADAS`) la llena la E2-3 con las fichas; lo que la IA elija fuera de ella
no se hace y queda como hecho. Las situaciones generales llegan en la E2-4.

Si la IA no responde (ADR 0018, decisión 8, caso 1): un reintento, enseguida; si vuelve a
fallar, nada se ejecuta, la persona recibe el único texto fijo, se registra un incidente para
el administrador y el turno queda registrado con su error. Vale para los dos pedidos: si la
redacción falla después de manejar las jugadas, lo hecho se deshace (un punto de guardado),
porque sin respuesta de la IA no hay jugada.

El turno corre en una transacción de `db.espacio`; quien llama la confirma.
"""

from __future__ import annotations

import dataclasses
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Any

import psycopg

from leda.autoridad import Solicitante
from leda.db import atar_al_entrante, espacio
from leda.incidentes import (ETAPA_TURNO_CONVERSACION, NOTICIA_NEUTRA_INCIDENTE,
                             REFERENCIA_INBOUND_MESSAGE, registrar_incidente)
from leda.salida import enqueue_outbox

from .ia import IA, Jugada
from .tiempo import Reloj

# El único texto fijo del motor (ADR 0018, decisión 8): sin IA no hay quien lo escriba. Es el
# que ya aprobó el usuario para la constitución §10, y el aviso al administrador lo cita.
TEXTO_SI_LA_IA_FALLA = NOTICIA_NEUTRA_INCIDENTE

INTENTOS_DE_LA_IA = 2          # un reintento
ULTIMOS_TURNOS = 10


@dataclass(frozen=True)
class Contexto:
    """Lo que un manejador de jugada necesita: la transacción del espacio, quién escribió,
    el momento del motor y lo leído al empezar el turno."""

    cur: psycopg.Cursor
    quien: Solicitante
    entrante_id: str
    chat_id: int
    texto: str
    ahora: datetime
    estado: dict[str, Any] | None
    tareas: tuple[dict[str, Any], ...]
    ultimos_turnos: tuple[dict[str, Any], ...]

    def tarea(self, alias: str) -> dict[str, Any] | None:
        return next((t for t in self.tareas if t["alias"] == alias), None)


Manejador = Callable[[Contexto, Jugada], dict[str, Any]]

# La lista cerrada: nombre de la jugada → su manejador. La llena la E2-3.
JUGADAS: Mapping[str, Manejador] = MappingProxyType({})


@dataclass
class ResultadoTurno:
    texto: str
    jugadas: list[Jugada]
    hechos: list[dict[str, Any]]
    error: str | None = None


class IANoRespondio(RuntimeError):
    def __init__(self, causa: BaseException) -> None:
        super().__init__(f"ia_no_respondio: {type(causa).__name__}")
        self.causa = causa


def procesar_turno(conn: psycopg.Connection, quien: Solicitante, entrante_id: str, ia: IA,
                   reloj: Reloj, jugadas: Mapping[str, Manejador] = JUGADAS) -> ResultadoTurno:
    with espacio(conn, quien.workspace_id) as cur:
        atar_al_entrante(cur, entrante_id)
        ctx = _leer(cur, quien, entrante_id, reloj.ahora())
        inicio = reloj.medir()
        elegidas: list[Jugada] | None = None    # None: la IA no llegó a elegir
        try:
            elegidas = _pedir(lambda: ia.elegir_jugadas(_situacion(ctx, jugadas)))
            with conn.transaction():
                hechos = [_manejar(ctx, jugada, jugadas) for jugada in elegidas]
                texto = _pedir(lambda: _no_vacio(ia.redactar(
                    {"hoy": ctx.ahora.date().isoformat(), "mensaje": ctx.texto,
                     "hechos": hechos})))
        except IANoRespondio as falla:
            return _si_la_ia_falla(cur, ctx, ia, reloj, inicio, elegidas, falla)
        latencia = _ms(reloj.medir() - inicio)
        _registrar_entrada(cur, ctx, reloj.ahora(), elegidas, {"hechos": hechos}, ia.nombre,
                           latencia, None)
        _responder(cur, ctx, texto, reloj.ahora(), ia.nombre)
        return ResultadoTurno(texto, elegidas, hechos)


# --- (1) Lo que se lee ------------------------------------------------------------------

def _leer(cur, quien: Solicitante, entrante_id: str, ahora: datetime) -> Contexto:
    cur.execute("select texto, chat_id, app_user_id from inbound_message where id = %s",
                (entrante_id,))
    entrante = cur.fetchone()
    if entrante is None or str(entrante["app_user_id"]) != quien.app_user_id:
        raise LookupError("El mensaje no es de esta persona en este espacio.")

    cur.execute("""select q.tipo, q.task_id
                     from conversation_state s
                     left join conversation_question q on q.id = s.pregunta_abierta_id
                    where s.membership_id = %s""", (quien.membership_id,))
    estado = cur.fetchone()

    cur.execute("""select id, titulo, estado, fecha_objetivo from task
                    where responsable_membership_id = %s
                      and estado not in ('terminada', 'cancelada')
                    order by fecha_objetivo nulls last, titulo""", (quien.membership_id,))
    tareas = tuple(
        {"alias": f"T{i}", "id": str(t["id"]), "titulo": t["titulo"],
         "estado": str(t["estado"]),
         "fecha_objetivo": t["fecha_objetivo"].isoformat() if t["fecha_objetivo"] else None}
        for i, t in enumerate(cur.fetchall(), 1))

    cur.execute("""select t.sentido, coalesce(i.texto, o.cuerpo) texto, t.jugadas, t.at
                     from conversation_turn t
                     left join inbound_message i on i.id = t.inbound_message_id
                     left join message_outbox o on o.id = t.outbox_id
                    where t.membership_id = %s
                    order by t.at desc, t.sentido = 'salida' desc
                    limit %s""", (quien.membership_id, ULTIMOS_TURNOS))
    ultimos = tuple(
        {"sentido": t["sentido"], "texto": t["texto"], "jugadas": t["jugadas"],
         "at": t["at"].isoformat()}
        for t in reversed(cur.fetchall()))

    return Contexto(cur=cur, quien=quien, entrante_id=entrante_id,
                    chat_id=entrante["chat_id"], texto=entrante["texto"] or "", ahora=ahora,
                    estado=_estado(estado, tareas), tareas=tareas, ultimos_turnos=ultimos)


def _estado(fila, tareas) -> dict[str, Any] | None:
    if fila is None or fila["tipo"] is None:
        return None
    alias = next((t["alias"] for t in tareas if t["id"] == str(fila["task_id"])), None)
    return {"pregunta_abierta": {"tipo": fila["tipo"], "tarea": alias}}


def _situacion(ctx: Contexto, jugadas: Mapping[str, Manejador]) -> dict[str, Any]:
    """Lo que la IA recibe para elegir: nunca un id de la base, sólo alias."""
    return {
        "hoy": ctx.ahora.date().isoformat(),
        "mensaje": ctx.texto,
        "estado": ctx.estado,
        "tareas": [{k: v for k, v in t.items() if k != "id"} for t in ctx.tareas],
        "ultimos_turnos": list(ctx.ultimos_turnos),
        "jugadas_posibles": sorted(jugadas),
    }


# --- (2) y (5) Los pedidos a la IA ---------------------------------------------------------

def _pedir(pedido: Callable[[], Any]) -> Any:
    ultima: BaseException | None = None
    for _ in range(INTENTOS_DE_LA_IA):
        try:
            return pedido()
        except Exception as e:     # la IA es un servicio externo: cualquier falla es no responder
            ultima = e
    raise IANoRespondio(ultima)


def _no_vacio(texto: str) -> str:
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("La IA devolvió una respuesta vacía.")
    return texto.strip()


# --- (3) y (4) Las jugadas ----------------------------------------------------------------

def _manejar(ctx: Contexto, jugada: Jugada, jugadas: Mapping[str, Manejador]) -> dict:
    manejador = jugadas.get(jugada.nombre)
    if manejador is None:
        return {"jugada": jugada.nombre, "resultado": "fuera_de_la_lista"}
    return manejador(ctx, jugada)


# --- (6) El registro de turnos y la respuesta ---------------------------------------------

def _si_la_ia_falla(cur, ctx: Contexto, ia: IA, reloj: Reloj, inicio: float,
                    elegidas: list[Jugada] | None, falla: IANoRespondio) -> ResultadoTurno:
    error = str(falla)
    ahora = reloj.ahora()
    registrar_incidente(
        cur, ctx.quien.workspace_id,
        "La IA no respondió en un turno del motor de conversación (dos intentos): no se "
        "ejecutó nada y la persona recibió el texto fijo.",
        referencia_cruda=f"{type(falla.causa).__name__}: {falla.causa}",
        etapa=ETAPA_TURNO_CONVERSACION, referencia_tipo=REFERENCIA_INBOUND_MESSAGE,
        referencia_id=ctx.entrante_id, chat_id=ctx.chat_id,
        app_user_id=ctx.quien.app_user_id, notificado_en=ahora)
    _registrar_entrada(cur, ctx, ahora, elegidas, None, ia.nombre,
                       _ms(reloj.medir() - inicio), error)
    _responder(cur, ctx, TEXTO_SI_LA_IA_FALLA, ahora, None)
    return ResultadoTurno(TEXTO_SI_LA_IA_FALLA, [], [], error)


def _responder(cur, ctx: Contexto, texto: str, ahora: datetime, ia_nombre: str | None) -> None:
    clave = f"motor:respuesta:{ctx.entrante_id}"
    enqueue_outbox(cur, workspace_id=ctx.quien.workspace_id, chat_id=ctx.chat_id, text=texto,
                   dedupe_key=clave, recipient_membership_id=ctx.quien.membership_id,
                   is_response=True, scheduled_for=ahora)
    cur.execute("select id from message_outbox where dedupe_key = %s", (clave,))
    cur.execute(
        """insert into conversation_turn (workspace_id, membership_id, sentido, outbox_id,
                                          ia, at)
           values (%s, %s, 'salida', %s, %s, %s)""",
        (ctx.quien.workspace_id, ctx.quien.membership_id, cur.fetchone()["id"], ia_nombre,
         ahora))


def _registrar_entrada(cur, ctx: Contexto, ahora: datetime, jugadas: list[Jugada] | None,
                       resultado: dict | None, ia_nombre: str, latencia_ms: int,
                       error: str | None) -> None:
    cur.execute(
        """insert into conversation_turn (workspace_id, membership_id, sentido,
                                          inbound_message_id, jugadas, resultado, ia,
                                          latencia_ms, error, at)
           values (%s, %s, 'entrada', %s, %s, %s, %s, %s, %s, %s)""",
        (ctx.quien.workspace_id, ctx.quien.membership_id, ctx.entrante_id,
         _json([dataclasses.asdict(j) for j in jugadas] if jugadas is not None else None),
         _json(resultado), ia_nombre, latencia_ms, error, ahora))


def _json(valor: Any) -> str | None:
    return None if valor is None else json.dumps(valor, ensure_ascii=False, default=str)


def _ms(segundos: float) -> int:
    return max(0, round(segundos * 1000))
