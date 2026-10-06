"""Un turno del motor de conversación (`odd/tasks/prueba-chica-del-motor.md`, sección 4).

(1) Lee el estado de la persona, sus tareas y sus últimos turnos; (2) la IA elige jugadas de
la lista cerrada y nombra las tareas por un alias; (3) el código maneja cada jugada con el
manejador de su ficha; (4) el resultado son hechos, con lo que dejan para después como quedó al terminar todas las
jugadas (`efectos.py`); (5) la IA redacta desde los hechos, una
respuesta por mensaje, que sale por el outbox; (6) todo queda en el registro de turnos.

La lista cerrada (`JUGADAS`) y sus fichas están en `fichas.py` (E2-3). Lo que la IA elija fuera
de ella no se hace: queda como hecho, con lo que Leda puede hacer, y se le avisa al
administrador con un incidente que apunta al mensaje (decisión 1 y situación general 8; uno
por turno).

Las situaciones generales (E2-4) son del mismo camino para todas las fichas: las preguntas y su
orden (`preguntas.py`) y las jugadas `elegir`, `corregir`, `cancelar` y `dejar_para_despues`
(`situaciones.py`). Al terminar las jugadas, si no quedó una pregunta abierta vuelve la que
quedó para después, y la redacción recibe la única pregunta que se hace (`pregunta`), con sus
opciones si es una duda: salen como botones (`botones.py`). Un toque (`procesar_toque`) corre
el mismo turno que una elección escrita, sin pedirle a la IA que elija: la jugada es `elegir`
con la opción tocada, y el turno queda registrado con esa opción. Un toque repetido de la misma
opción no hace nada (la señal se la da el escuchador); uno de una pregunta ya cerrada no hace
nada y los hechos dicen con qué se cerró (situación general 7).

Si la IA no responde (ADR 0018, decisión 8, caso 1): un reintento, enseguida; si vuelve a
fallar, nada se ejecuta, la persona recibe el único texto fijo, se registra un incidente para
el administrador y el turno queda registrado con su error. Vale para los dos pedidos: si la
redacción falla después de manejar las jugadas, lo hecho se deshace (un punto de guardado),
porque sin respuesta de la IA no hay jugada.

El turno corre en una transacción de `db.espacio`; quien llama la confirma. Los turnos de una
persona corren de a uno (un candado por persona, de la transacción). Un mensaje corre una sola
vez: si ya tiene su turno de entrada (un reintento del escuchador, dos procesos con el mismo
mensaje), no se le pide nada a la IA ni se ejecuta nada, y el resultado lo dice (`repetido`);
la base lo asegura además con un índice único. Cada turno lleva su número en la conversación
de la persona, que ordena los últimos turnos aunque tengan la misma hora.
"""

from __future__ import annotations

import dataclasses
import json
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import psycopg

from leda.autoridad import Solicitante
from leda.db import atar_al_entrante, espacio
from leda.incidentes import (ETAPA_TURNO_CONVERSACION, NOTICIA_NEUTRA_INCIDENTE,
                             REFERENCIA_INBOUND_MESSAGE, registrar_incidente)
from leda.salida import enqueue_outbox

from . import preguntas
from .fichas import EN_COLA_SIN_ENVIAR, JUGADAS, Contexto, Manejador, lo_que_puede_hacer
from .ia import IA, Jugada
from .situaciones import elegir_opcion
from .tiempo import Reloj

# El único texto fijo del motor (ADR 0018, decisión 8): sin IA no hay quien lo escriba. Es el
# que ya aprobó el usuario para la constitución §10, y el aviso al administrador lo cita.
TEXTO_SI_LA_IA_FALLA = NOTICIA_NEUTRA_INCIDENTE

INTENTOS_DE_LA_IA = 2          # un reintento
ULTIMOS_TURNOS = 10

# El aviso al administrador de lo que no está en la lista (plan, sección 4): un incidente de
# severidad baja con etapa propia, que `registrar_incidente` lleva al bot de administración.
ETAPA_FUERA_DE_LA_LISTA = "motor_fuera_de_la_lista"

# Dentro de un hecho, lo que Leda sabe y dice sólo si la persona lo pregunta (decisión 9g;
# la misma lógica que la constitución §9). Un mecanismo para cualquier hecho, no una frase.
SOLO_SI_PREGUNTA = "solo_si_pregunta"


@dataclass
class ResultadoTurno:
    texto: str
    jugadas: list[Jugada]
    hechos: list[dict[str, Any]]
    error: str | None = None
    repetido: bool = False      # el mensaje (o el toque) ya tenía su turno: no se hizo nada
    pregunta: dict[str, Any] | None = None      # la única que se hace en la respuesta
    # Lo que un turno anterior anunció y ya no va a pasar, que la redacción recibió (9m.3).
    ya_no_sale: list[dict[str, Any]] = dataclasses.field(default_factory=list)


class IANoRespondio(RuntimeError):
    def __init__(self, causa: BaseException) -> None:
        super().__init__(f"ia_no_respondio: {type(causa).__name__}")
        self.causa = causa


def procesar_turno(conn: psycopg.Connection, quien: Solicitante, entrante_id: str, ia: IA,
                   reloj: Reloj, jugadas: Mapping[str, Manejador] = JUGADAS) -> ResultadoTurno:
    with espacio(conn, quien.workspace_id) as cur:
        atar_al_entrante(cur, entrante_id)
        if _ya_tiene_turno(cur, quien, entrante_id):
            return ResultadoTurno("", [], [], repetido=True)
        ctx = _leer(cur, quien, reloj.ahora(), entrante_id=entrante_id, jugadas=jugadas)

        def elegir() -> list[Jugada]:
            return pedir_a_la_ia(lambda: ia.elegir_jugadas(_situacion(ctx, jugadas)))

        def manejar(elegidas: list[Jugada]) -> list[dict[str, Any]]:
            hechos = [_manejar(ctx, jugada, jugadas) for jugada in elegidas]
            _avisar_fuera_de_la_lista(ctx, elegidas, jugadas)
            return hechos

        return _turno(conn, cur, ctx, ia, reloj, elegir, manejar,
                      clave_respuesta=f"motor:respuesta:{entrante_id}")


def procesar_toque(conn: psycopg.Connection, quien: Solicitante, token: str, chat_id: int,
                   ia: IA, reloj: Reloj) -> ResultadoTurno | None:
    """Un toque de una opción: el mismo turno que la elección escrita (situación general 6).
    `None` si el token no es de una pregunta de esta persona (no se atiende); `repetido` si
    esa opción ya se tocó con su turno."""
    with espacio(conn, quien.workspace_id) as cur:
        _bloquear_persona(cur, quien)
        opcion = preguntas.opcion_por_token(cur, token)
        if opcion is None or str(opcion["membership_id"]) != quien.membership_id:
            return None
        cur.execute("""select 1 from conversation_turn
                        where option_id = %s and sentido = 'entrada' and error is null""",
                    (opcion["id"],))
        if cur.fetchone() is not None:
            return ResultadoTurno("", [], [], repetido=True)
        ctx = _leer(cur, quien, reloj.ahora(), chat_id=chat_id, toque=opcion["etiqueta"])
        jugada = Jugada("elegir", {"opcion": preguntas.alias_de_opcion(opcion["orden"])})
        return _turno(conn, cur, ctx, ia, reloj, lambda: [jugada],
                      lambda _: [elegir_opcion(ctx, opcion)],
                      clave_respuesta=f"motor:toque:{opcion['id']}:{uuid.uuid4().hex}",
                      option_id=str(opcion["id"]))


def _turno(conn, cur, ctx: Contexto, ia: IA, reloj: Reloj,
           elegir: Callable[[], list[Jugada]],
           manejar: Callable[[list[Jugada]], list[dict[str, Any]]], *,
           clave_respuesta: str, option_id: str | None = None) -> ResultadoTurno:
    """(2) a (6), iguales para un mensaje y un toque."""
    inicio = reloj.medir()
    elegidas: list[Jugada] | None = None    # None: la IA no llegó a elegir
    try:
        elegidas = elegir()
        with conn.transaction():
            hechos = manejar(elegidas)
            pregunta = preguntas.al_terminar_el_turno(ctx)
            # Lo que los hechos dejaron para después, como quedó después de todas las jugadas
            # (9k). `efectos` usa los avisos, que importan este módulo: se importa acá.
            # También lo que un turno anterior dejó anunciado y ya no va a pasar, y lo que sigue.
            from .efectos import ANUNCIADOS, YA_NO_SALE, al_final_del_turno
            final = al_final_del_turno(ctx, hechos)
            texto = pedir_a_la_ia(lambda: no_vacio(
                ia.redactar(_pedido_de_redaccion(ctx, hechos, pregunta, final.ya_no_sale))))
    except IANoRespondio as falla:
        return _si_la_ia_falla(cur, ctx, ia, reloj, inicio, elegidas, falla, clave_respuesta,
                               option_id)
    latencia = _ms(reloj.medir() - inicio)
    # Lo anunciado y pendiente va en el resultado, fuera de los hechos: la IA no lo recibe en
    # los últimos turnos (sólo los hechos), y el turno siguiente lo vuelve a mirar.
    resultado = {"hechos": hechos, **({"pregunta": pregunta} if pregunta else {}),
                 **({YA_NO_SALE: final.ya_no_sale} if final.ya_no_sale else {}),
                 **({ANUNCIADOS: final.anunciados} if final.anunciados else {})}
    turno = _registrar_entrada(cur, ctx, reloj.ahora(), elegidas, resultado, ia.nombre,
                               latencia, None, option_id)
    if ctx.avisos_guardados:
        cur.execute("update scheduled_notice set turno_id = %s where id = any(%s)",
                    (turno, ctx.avisos_guardados))
    _responder(cur, ctx, texto, reloj.ahora(), ia.nombre, clave_respuesta)
    return ResultadoTurno(texto, elegidas, hechos, pregunta=pregunta,
                          ya_no_sale=final.ya_no_sale)


# --- (1) Lo que se lee ------------------------------------------------------------------

def _bloquear_persona(cur, quien: Solicitante) -> None:
    """Los turnos de una persona corren de a uno: el candado hace esperar a otro turno de la
    misma persona hasta que éste termine."""
    cur.execute("select pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (f"motor:persona:{quien.membership_id}",))


def _ya_tiene_turno(cur, quien: Solicitante, entrante_id: str) -> bool:
    """Con el mismo mensaje, al pasar el candado ve el turno ya registrado."""
    _bloquear_persona(cur, quien)
    cur.execute("""select 1 from conversation_turn
                    where inbound_message_id = %s and sentido = 'entrada'""", (entrante_id,))
    return cur.fetchone() is not None


def _leer(cur, quien: Solicitante, ahora: datetime, *, entrante_id: str | None = None,
          chat_id: int | None = None, toque: str | None = None,
          jugadas: Mapping[str, Manejador] = JUGADAS) -> Contexto:
    """Lo leído al empezar el turno: el mensaje (o el toque y su chat), las tareas abiertas de
    la persona con su alias, el estado de su conversación y sus últimos turnos."""
    texto = ""
    if entrante_id is not None:
        cur.execute("select texto, chat_id, app_user_id from inbound_message where id = %s",
                    (entrante_id,))
        entrante = cur.fetchone()
        if entrante is None or str(entrante["app_user_id"]) != quien.app_user_id:
            raise LookupError("El mensaje no es de esta persona en este espacio.")
        texto, chat_id = entrante["texto"] or "", entrante["chat_id"]

    # El último aviso es un envío: con sus tareas, que pueden ser varias si juntó avisos del
    # día (mecánica §10).
    cur.execute("""select a.tipo as aviso_tipo,
                          array(select b.task_id from scheduled_notice b
                                 where b.outbox_id = a.outbox_id and b.task_id is not null
                                 order by b.creado_en, b.dedupe_key) as aviso_tareas,
                          a.task_id as aviso_tarea
                     from conversation_state s
                     left join scheduled_notice a on a.id = s.ultimo_aviso_id
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

    ultimos = leer_ultimos_turnos(cur, quien.membership_id)
    return Contexto(cur=cur, quien=quien, entrante_id=entrante_id, chat_id=chat_id,
                    texto=texto, ahora=ahora,
                    estado=preguntas.estado_para_la_ia(cur, quien.membership_id, tareas),
                    tareas=tareas, ultimos_turnos=ultimos,
                    ultimo_aviso=_ultimo_aviso(estado, tareas), toque=toque,
                    jugadas=jugadas)


def _alias(tareas, task_id) -> str | None:
    return next((t["alias"] for t in tareas if t["id"] == str(task_id)), None)


def leer_ultimos_turnos(cur, membership_id: str) -> tuple[dict[str, Any], ...]:
    """Los últimos turnos de la persona, del más viejo al más nuevo, con su texto; un toque,
    con la etiqueta de la opción que tocó (`toco`)."""
    cur.execute("""select t.sentido, coalesce(i.texto, o.cuerpo) texto, t.jugadas,
                          t.resultado -> 'hechos' as hechos, t.at, op.etiqueta toco
                     from conversation_turn t
                     left join inbound_message i on i.id = t.inbound_message_id
                     left join message_outbox o on o.id = t.outbox_id
                     left join conversation_option op on op.id = t.option_id
                    where t.membership_id = %s
                    order by t.numero desc
                    limit %s""", (membership_id, ULTIMOS_TURNOS))
    return tuple(
        {"sentido": t["sentido"], "texto": t["texto"], "jugadas": t["jugadas"],
         "hechos": t["hechos"], "at": t["at"].isoformat(),
         **({"toco": t["toco"]} if t["toco"] else {})}
        for t in reversed(cur.fetchall()))


def _ultimo_aviso(fila, tareas) -> dict[str, Any] | None:
    """El último aviso que Leda le mandó y su tarea (la tarea sale del aviso, plan, sección
    5): dice de qué tarea habla una respuesta que no la nombra. Si el envío juntó avisos de
    varias tareas, las dice todas (`tareas`): ninguna es la del último aviso."""
    if fila is None or fila["aviso_tipo"] is None:
        return None
    de_las = list(dict.fromkeys(str(t) for t in fila["aviso_tareas"] or []))
    if len(de_las) > 1:
        # En el orden de la lista de tareas de la persona, el mismo con que se las presenta.
        return {"tipo": fila["aviso_tipo"],
                "tareas": [t["alias"] for t in tareas if t["id"] in de_las]}
    return {"tipo": fila["aviso_tipo"], "tarea": _alias(tareas, fila["aviso_tarea"])}


def _situacion(ctx: Contexto, jugadas: Mapping[str, Manejador]) -> dict[str, Any]:
    """Lo que la IA recibe para elegir: nunca un id de la base, sólo alias."""
    return {
        "hoy": ctx.ahora.date().isoformat(),
        "mensaje": ctx.texto,
        "estado": ctx.estado,       # la pregunta abierta, con sus opciones, y las de después
        "ultimo_aviso": ctx.ultimo_aviso,
        "tareas": [{k: v for k, v in t.items() if k != "id"} for t in ctx.tareas],
        "ultimos_turnos": list(ctx.ultimos_turnos),
        "jugadas_posibles": sorted(jugadas),
    }


def _pedido_de_redaccion(ctx: Contexto, hechos: list[dict[str, Any]],
                         pregunta: dict[str, Any] | None = None,
                         ya_no_sale: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Lo que la IA recibe para redactar: hoy, a quién le escribe, su mensaje (o la opción que
    tocó), los hechos (con lo que se dice sólo si se pregunta, `SOLO_SI_PREGUNTA`), lo que un
    mensaje anterior anunció y ya no va a pasar (`ya_no_sale`, si hay), la única pregunta que
    se hace, si hay, y los últimos turnos."""
    return {"hoy": ctx.ahora.date().isoformat(), "persona": ctx.quien.nombre,
            "mensaje": ctx.texto if ctx.toque is None else None,
            **({"toco": ctx.toque} if ctx.toque is not None else {}),
            "hechos": hechos, **({"ya_no_sale": ya_no_sale} if ya_no_sale else {}),
            "pregunta": pregunta, "ultimos_turnos": list(ctx.ultimos_turnos)}


# --- (2) y (5) Los pedidos a la IA ---------------------------------------------------------

def pedir_a_la_ia(pedido: Callable[[], Any]) -> Any:
    """El pedido, con un reintento enseguida (decisión 8); si falla dos veces,
    `IANoRespondio`."""
    ultima: BaseException | None = None
    for _ in range(INTENTOS_DE_LA_IA):
        try:
            return pedido()
        except Exception as e:     # la IA es un servicio externo: cualquier falla es no responder
            ultima = e
    raise IANoRespondio(ultima)


def no_vacio(texto: str) -> str:
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("La IA devolvió una respuesta vacía.")
    return texto.strip()


# --- (3) y (4) Las jugadas ----------------------------------------------------------------

def _manejar(ctx: Contexto, jugada: Jugada, jugadas: Mapping[str, Manejador]) -> dict:
    manejador = jugadas.get(jugada.nombre)
    if manejador is None:
        # Que se avisó al administrador es cierto, pero se dice sólo si la persona lo
        # pregunta (9g): va en `solo_si_pregunta`, que la redacción trata siempre igual. Con
        # su estado, como todo aviso: queda en la cola del bot de administración.
        return {"jugada": jugada.nombre, "resultado": "fuera_de_la_lista",
                "lo_que_puede_hacer": lo_que_puede_hacer(jugadas),
                SOLO_SI_PREGUNTA: {
                    "aviso_al_administrador": {"estado": EN_COLA_SIN_ENVIAR}}}
    return manejador(ctx, jugada)


def _avisar_fuera_de_la_lista(ctx: Contexto, elegidas: list[Jugada],
                              jugadas: Mapping[str, Manejador]) -> None:
    """Uno por mensaje, con la referencia al mensaje que lo provocó (decisiones 1 y 9g). A la
    persona no se le dice, salvo que lo pregunte: el hecho queda en el registro de turnos."""
    fuera = [dataclasses.asdict(j) for j in elegidas if j.nombre not in jugadas]
    if not fuera:
        return
    registrar_incidente(
        ctx.cur, ctx.quien.workspace_id,
        "Un mensaje pidió algo que no está en la lista cerrada de jugadas del motor de "
        "conversación: no se hizo nada y la IA le dijo a la persona qué puede hacer. Para "
        "analizar si hace falta una jugada nueva (ADR 0018, decisión 1).",
        severidad="baja", referencia_cruda=_json(fuera), etapa=ETAPA_FUERA_DE_LA_LISTA,
        referencia_tipo=REFERENCIA_INBOUND_MESSAGE, referencia_id=ctx.entrante_id,
        chat_id=ctx.chat_id, app_user_id=ctx.quien.app_user_id)


# --- (6) El registro de turnos y la respuesta ---------------------------------------------

def _si_la_ia_falla(cur, ctx: Contexto, ia: IA, reloj: Reloj, inicio: float,
                    elegidas: list[Jugada] | None, falla: IANoRespondio, clave: str,
                    option_id: str | None) -> ResultadoTurno:
    error = str(falla)
    ahora = reloj.ahora()
    registrar_incidente(
        cur, ctx.quien.workspace_id,
        "La IA no respondió en un turno del motor de conversación (dos intentos): no se "
        "ejecutó nada y la persona recibió el texto fijo.",
        referencia_cruda=f"{type(falla.causa).__name__}: {falla.causa}",
        etapa=ETAPA_TURNO_CONVERSACION,
        referencia_tipo=REFERENCIA_INBOUND_MESSAGE if ctx.entrante_id else None,
        referencia_id=ctx.entrante_id, chat_id=ctx.chat_id,
        app_user_id=ctx.quien.app_user_id, notificado_en=ahora)
    _registrar_entrada(cur, ctx, ahora, elegidas, None, ia.nombre,
                       _ms(reloj.medir() - inicio), error, option_id)
    _responder(cur, ctx, TEXTO_SI_LA_IA_FALLA, ahora, None, clave)
    return ResultadoTurno(TEXTO_SI_LA_IA_FALLA, [], [], error)


def _responder(cur, ctx: Contexto, texto: str, ahora: datetime, ia_nombre: str | None,
               clave: str) -> None:
    enqueue_outbox(cur, workspace_id=ctx.quien.workspace_id, chat_id=ctx.chat_id, text=texto,
                   dedupe_key=clave, recipient_membership_id=ctx.quien.membership_id,
                   is_response=True, scheduled_for=ahora)
    cur.execute("select id from message_outbox where dedupe_key = %s", (clave,))
    registrar_salida(cur, ctx.quien.workspace_id, ctx.quien.membership_id,
                     str(cur.fetchone()["id"]), ia_nombre, ahora)


def registrar_salida(cur, workspace_id: str, membership_id: str, outbox_id: str,
                     ia_nombre: str | None, ahora: datetime) -> None:
    """Un mensaje de Leda a la persona, en su registro de turnos."""
    cur.execute(
        """insert into conversation_turn (workspace_id, membership_id, sentido, outbox_id,
                                          ia, at, numero)
           values (%s, %s, 'salida', %s, %s, %s, %s)""",
        (workspace_id, membership_id, outbox_id, ia_nombre, ahora,
         _siguiente_numero(cur, membership_id)))


def _registrar_entrada(cur, ctx: Contexto, ahora: datetime, jugadas: list[Jugada] | None,
                       resultado: dict | None, ia_nombre: str, latencia_ms: int,
                       error: str | None, option_id: str | None = None) -> str:
    """Un mensaje o un toque de la persona, en su registro de turnos (un toque, con la opción
    tocada)."""
    cur.execute(
        """insert into conversation_turn (workspace_id, membership_id, sentido,
                                          inbound_message_id, option_id, jugadas, resultado,
                                          ia, latencia_ms, error, at, numero)
           values (%s, %s, 'entrada', %s, %s, %s, %s, %s, %s, %s, %s, %s)
           returning id""",
        (ctx.quien.workspace_id, ctx.quien.membership_id, ctx.entrante_id, option_id,
         _json([dataclasses.asdict(j) for j in jugadas] if jugadas is not None else None),
         _json(resultado), ia_nombre, latencia_ms, error, ahora,
         _siguiente_numero(cur, ctx.quien.membership_id)))
    return str(cur.fetchone()["id"])


def _siguiente_numero(cur, membership_id: str) -> int:
    """El número del próximo turno de la persona; el candado del turno lo hace único."""
    cur.execute("""select coalesce(max(numero), 0) + 1 as n from conversation_turn
                    where membership_id = %s""", (membership_id,))
    return cur.fetchone()["n"]


def _json(valor: Any) -> str | None:
    return None if valor is None else json.dumps(valor, ensure_ascii=False, default=str)


def _ms(segundos: float) -> int:
    return max(0, round(segundos * 1000))
