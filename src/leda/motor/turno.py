"""Un turno del motor de conversación (diseño probado en la Etapa 2;
`odd/tasks/prueba-chica-del-motor.md`, sección 4).

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
de la persona, que ordena los últimos turnos aunque tengan la misma hora; el registro de turnos
vive en `registro.py`, que también usan los avisos guardados.
"""

from __future__ import annotations

import dataclasses
import json
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import psycopg

from ..autoridad import Solicitante
from ..db import atar_al_entrante, espacio
from ..incidentes import (ETAPA_TURNO_CONVERSACION, NOTICIA_NEUTRA_INCIDENTE,
                          REFERENCIA_INBOUND_MESSAGE, registrar_incidente)
from ..salida import enqueue_outbox

from . import cambios_de_estado, preguntas, registro
from .efectos import ANUNCIADOS, YA_NO_VA_A_PASAR, al_final_del_turno
from .fichas import JUGADAS, LLEGA, Contexto, Manejador, lo_que_puede_hacer
from .ia import IA, Jugada
from .registro import leer_ultimos_turnos, no_vacio, registrar_salida
from .situaciones import elegir_opcion
from .tiempo import Reloj

# El único texto fijo del motor (ADR 0018, decisión 8): sin IA no hay quien lo escriba. Es el
# que ya aprobó el usuario para la constitución §10, y el aviso al administrador lo cita.
TEXTO_SI_LA_IA_FALLA = NOTICIA_NEUTRA_INCIDENTE

INTENTOS_DE_LA_IA = 2          # un reintento

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
    # Lo que un turno anterior anunció y ya no va a pasar, que la redacción recibió (9m.3), en
    # `ya_no_va_a_pasar`. El atributo conserva su nombre: el corredor de las conversaciones lo
    # lee igual en los dos motores.
    ya_no_sale: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    # Cuándo estuvo listo el texto (`time.monotonic`): al volver la redacción, o al elegir el
    # texto fijo. Desde ahí mide el escuchador cuánto tarda en salir la respuesta.
    listo_en: float | None = None


class IANoRespondio(RuntimeError):
    def __init__(self, causa: BaseException) -> None:
        super().__init__(f"ia_no_respondio: {type(causa).__name__}")
        self.causa = causa


def procesar_turno(conn: psycopg.Connection, quien: Solicitante, entrante_id: str, ia: IA,
                   reloj: Reloj, jugadas: Mapping[str, Manejador] = JUGADAS, *,
                   al_avanzar: Callable[[str], None] | None = None) -> ResultadoTurno:
    """Un mensaje escrito. Con `al_avanzar`, la redacción se ve en vivo (`_redactar`)."""
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
                      clave_respuesta=f"motor:respuesta:{entrante_id}", al_avanzar=al_avanzar)


def procesar_toque(conn: psycopg.Connection, quien: Solicitante, token: str, chat_id: int,
                   ia: IA, reloj: Reloj, *,
                   al_avanzar: Callable[[str], None] | None = None) -> ResultadoTurno | None:
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
                      option_id=str(opcion["id"]), al_avanzar=al_avanzar)


def _turno(conn, cur, ctx: Contexto, ia: IA, reloj: Reloj,
           elegir: Callable[[], list[Jugada]],
           manejar: Callable[[list[Jugada]], list[dict[str, Any]]], *,
           clave_respuesta: str, option_id: str | None = None,
           al_avanzar: Callable[[str], None] | None = None) -> ResultadoTurno:
    """(2) a (6), iguales para un mensaje y un toque."""
    inicio = reloj.medir()
    elegidas: list[Jugada] | None = None    # None: la IA no llegó a elegir
    try:
        elegidas = elegir()
        with conn.transaction():
            hechos = manejar(elegidas)
            # Desde cuándo cada tarea está en su estado lo sabe el motor por lo que anota
            # (`cambios_de_estado.py`): los cambios de este turno, fuera de los hechos.
            cambios = cambios_de_estado.del_turno(cur, ctx.tareas)
            pregunta = preguntas.al_terminar_el_turno(ctx)
            # Lo que los hechos dejaron para después, como quedó después de todas las jugadas
            # (9k). También lo que un turno anterior dejó anunciado y ya no va a pasar, y lo
            # que sigue.
            final = al_final_del_turno(ctx, hechos)
            texto = pedir_a_la_ia(lambda: no_vacio(_redactar(
                ia, _pedido_de_redaccion(ctx, hechos, pregunta, final.ya_no_sale), al_avanzar)))
            listo_en = time.monotonic()
    except IANoRespondio as falla:
        return _si_la_ia_falla(cur, ctx, ia, reloj, inicio, elegidas, falla, clave_respuesta,
                               option_id)
    latencia = _ms(reloj.medir() - inicio)
    # Lo anunciado y pendiente va en el resultado, fuera de los hechos: la IA no lo recibe en
    # los últimos turnos (sólo los hechos), y el turno siguiente lo vuelve a mirar.
    resultado = {"hechos": hechos, **({"pregunta": pregunta} if pregunta else {}),
                 **({YA_NO_VA_A_PASAR: final.ya_no_sale} if final.ya_no_sale else {}),
                 **({ANUNCIADOS: final.anunciados} if final.anunciados else {}),
                 **({cambios_de_estado.CLAVE: cambios} if cambios else {})}
    turno = _registrar_entrada(cur, ctx, reloj.ahora(), elegidas, resultado, ia.nombre,
                               latencia, None, option_id)
    if ctx.avisos_guardados:
        cur.execute("update scheduled_notice set turno_id = %s where id = any(%s)",
                    (turno, ctx.avisos_guardados))
    _responder(cur, ctx, texto, reloj.ahora(), ia.nombre, clave_respuesta)
    return ResultadoTurno(texto, elegidas, hechos, pregunta=pregunta,
                          ya_no_sale=final.ya_no_sale, listo_en=listo_en)


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


def _hoy(ctx: Contexto) -> str:
    """La fecha de hoy en el espacio, no en UTC: de noche, en UTC ya es mañana y la IA
    contaría un día de más."""
    return ctx.ahora.astimezone(ctx.calendario.zona).date().isoformat()


def _alias(tareas, task_id) -> str | None:
    return next((t["alias"] for t in tareas if t["id"] == str(task_id)), None)


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
        "hoy": _hoy(ctx),
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
    mensaje anterior anunció y ya no va a pasar (`ya_no_va_a_pasar`, si hay), la única
    pregunta que se hace, si hay, y los últimos turnos."""
    return {"hoy": _hoy(ctx), "persona": ctx.quien.nombre,
            "mensaje": ctx.texto if ctx.toque is None else None,
            **({"toco": ctx.toque} if ctx.toque is not None else {}),
            "hechos": hechos, **({YA_NO_VA_A_PASAR: ya_no_sale} if ya_no_sale else {}),
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


def _redactar(ia: IA, pedido: dict[str, Any],
              al_avanzar: Callable[[str], None] | None) -> str:
    """La redacción, la única parte del turno que se ve mientras la IA la escribe (pedido del
    usuario, 2026-10-07): con `al_avanzar`, la IA avisa lo escrito hasta ahí y el escuchador lo
    muestra en el borrador de Telegram. La elección de jugadas nunca se muestra. Lo que sale es
    siempre el texto que devuelve, por el outbox; lo visto en vivo es efímero. Un reintento
    vuelve a escribir desde el principio, y el borrador lo muestra igual. Sin nadie que mire,
    se le pide como siempre: una IA sin ese argumento sigue sirviendo."""
    if al_avanzar is None:
        return ia.redactar(pedido)
    return ia.redactar(pedido, al_avanzar=al_avanzar)


# --- (3) y (4) Las jugadas ----------------------------------------------------------------

def _manejar(ctx: Contexto, jugada: Jugada, jugadas: Mapping[str, Manejador]) -> dict:
    manejador = jugadas.get(jugada.nombre)
    if manejador is None:
        # Que se avisó al administrador es cierto, pero se dice sólo si la persona lo
        # pregunta (9g): va en `solo_si_pregunta`, que la redacción trata siempre igual. Con
        # cuándo le llega, como todo aviso: sale enseguida por el bot de administración.
        return {"jugada": jugada.nombre, "resultado": "fuera_de_la_lista",
                "lo_que_puede_hacer": lo_que_puede_hacer(jugadas),
                SOLO_SI_PREGUNTA: {
                    "aviso_al_administrador": {
                        LLEGA: ctx.ahora.astimezone(ctx.calendario.zona).isoformat()}}}
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
    listo_en = time.monotonic()
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
    return ResultadoTurno(TEXTO_SI_LA_IA_FALLA, [], [], error, listo_en=listo_en)


def _responder(cur, ctx: Contexto, texto: str, ahora: datetime, ia_nombre: str | None,
               clave: str) -> None:
    enqueue_outbox(cur, workspace_id=ctx.quien.workspace_id, chat_id=ctx.chat_id, text=texto,
                   dedupe_key=clave, recipient_membership_id=ctx.quien.membership_id,
                   is_response=True, scheduled_for=ahora)
    cur.execute("select id from message_outbox where dedupe_key = %s", (clave,))
    registrar_salida(cur, ctx.quien.workspace_id, ctx.quien.membership_id,
                     str(cur.fetchone()["id"]), ia_nombre, ahora)


def _registrar_entrada(cur, ctx: Contexto, ahora: datetime, jugadas: list[Jugada] | None,
                       resultado: dict | None, ia_nombre: str, latencia_ms: int,
                       error: str | None, option_id: str | None = None) -> str:
    """Un mensaje o un toque de la persona, en su registro de turnos (un toque, con la opción
    tocada; `registro.registrar_entrada`)."""
    return registro.registrar_entrada(
        cur, workspace_id=ctx.quien.workspace_id, membership_id=ctx.quien.membership_id,
        entrante_id=ctx.entrante_id, ahora=ahora, jugadas=jugadas, resultado=resultado,
        ia_nombre=ia_nombre, latencia_ms=latencia_ms, error=error, option_id=option_id)


def _json(valor: Any) -> str | None:
    return None if valor is None else json.dumps(valor, ensure_ascii=False, default=str)


def _ms(segundos: float) -> int:
    return max(0, round(segundos * 1000))
