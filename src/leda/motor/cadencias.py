"""Los pedidos de estado con ritmo fijo: la cadencia del espacio (C-6, circuito 5).

Decisión 8 del usuario (`odd/tasks/fase-c.md`, 2026-10-08, opción A); ADR 0017, decisión 3b, punto 5
("pedidos de estado según las cadencias del espacio"); mecánica §9, §10 y §12; conversación 37. Las
cadencias del pack (`cadencia`, que el importador carga en `cadence_job`) se retiraron del motor en la
E3-7 con el ciclo viejo; vuelven acá, como una pasada más de la escalera.

**Un pedido de estado por persona con la lista de sus tareas.** El día de una cadencia a cada
integrante en privado (`privado_cada_integrante`), cada persona con tareas abiertas recibe un solo
mensaje (`como_vienen_sus_tareas`) con sus tareas y una sola pregunta, por la lista entera. Van en la
lista las tareas asignadas o en curso sin un bloqueo abierto (`tareas_de`): una trabada la sigue la
persecución del bloqueo (C-5) y una entregada espera la revisión de otra persona.

**El recordatorio del día va adentro** (`avisos._a_la_lista`): lo que la escalera tenía para ese día
sobre una tarea de la lista (el aviso previo, el pedido de estado, el recordatorio del vencimiento con
otro día dado, el reencuadre, el pedido que sigue a un avance; `TipoDeAviso.entra_en_la_lista`) sale
en el mismo mensaje, como un renglón de la lista, y no aparte. Cuenta como dado para su escalera (sale
con la misma fila) y, si pedía el estado, en su espera, sin abrir otra pregunta: la de la lista es la
única. Si la cadencia sale más tarde que la hora en que Leda manda lo suyo (el miércoles a las 11:30),
lo de la escalera de ese día espera y va en la lista.

**Lo contestado cuenta para la escalera de esa tarea** (`preguntas.marcar_en_la_lista`): cada jugada
sobre una tarea de la lista la contesta en la lista, y la jugada hace lo suyo en su tarea, como
siempre (un inicio o una fecha cierran su espera). "Viene bien" de una tarea que todavía no vence se
anota igual, aunque su escalera no haya pedido nada (`fichas._informar_avance`): Leda vuelve a
preguntar en la próxima lista o el día en que vence, lo que llegue antes (`cuando_vuelve_a_preguntar`).
**Si contesta sólo una**, Leda la anota y, en la misma respuesta, pregunta una vez por las otras
(`preguntas.al_terminar_el_turno`); si después contesta otra vez sólo una parte, la lista se cierra:
no vuelve a preguntar. **Si no contesta**, la lista es una pregunta de Leda sin contestar (decisión 21,
`pregunta_sin_contestar.py`): como no es de una tarea, no se repite a las 4 horas y deja de frenar a
las 8.

**A qué hora sale:** a la hora de la cadencia, o a la hora en que Leda manda lo suyo si la cadencia es
antes (`tiempo.sale`: la de las 09:15 sale a las 10:00, con lo de la escalera); dentro del horario y
sin interrumpir una conversación, como todo aviso. Es seguimiento que Leda hace por su cuenta: cuenta
para el tope diario como un mensaje (decisión 17).

**Una vez por día de la cadencia** (mecánica §12): la clave nombra la cadencia, la persona y el día, y
`cadence_job.ultima_corrida` dice hasta qué día de la cadencia se atendió. Un día de la cadencia que
pasó sin atenderse (el ciclo estuvo parado) no se manda tarde: queda omitido con su motivo
(`YA_PASO_SU_MOMENTO`), y también el que llega a salir otro día (la persona estaba ausente o
conversando). Un feriado, igual (`NO_ES_DIA_HABIL`). Antes de la primera vuelta de un espacio no se
repone nada: la primera vuelta marca desde cuándo se cuenta.

**Un ritmo que no se entiende** (un cron editado a mano, `leer_ritmo`) no frena a las demás: deja un
incidente por día mientras siga así, y su cadencia no corre hasta que se corrija.

Las cadencias al grupo (`grupo`) no son un pedido a cada persona: el informe al grupo es otra pieza
(`PENDIENTE`, `odd/tasks/fase-c.md`, C-6).
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any, NamedTuple

from ..incidentes import registrar_incidente

from .ancla import anclaje
from .avisos import ABIERTOS, Momento, guardar, hechos_de_la_escalera, omitir
from .preguntas import COMO_VIENEN_SUS_TAREAS
from .tiempo import sale, sale_el

PRIVADO = "privado_cada_integrante"
# Por qué un pedido de la lista no salió: su día pasó (mecánica §12), era feriado, o la persona ya
# no tenía tareas por las que preguntar.
YA_PASO_SU_MOMENTO = "ya_paso_su_momento"
NO_ES_DIA_HABIL = "no_es_dia_habil"
SIN_TAREAS_ABIERTAS = "sin_tareas_abiertas"
# La etapa de la escalera: la cadencia es una pasada suya.
ETAPA = "motor_escalera"
# Hasta dónde se busca el próximo día de una cadencia (una semana alcanza para cualquier ritmo
# semanal; más, por los feriados seguidos).
_DIAS_HACIA_ADELANTE = 60


class Ritmo(NamedTuple):
    """A qué hora y qué días de la semana (0 = lunes) toca una cadencia."""

    hora: time
    dias: frozenset[int]


def leer_ritmo(cron: str) -> Ritmo | None:
    """El ritmo de un cron como lo escribe el importador del pack (`importador._a_cron`): minuto,
    hora, `*`, `*` y los días de la semana (`*`, uno, una lista o un rango; 0 o 7 es domingo).
    `None` si no se entiende: nunca se adivina."""
    partes = str(cron or "").split()
    if len(partes) != 5 or partes[2] != "*" or partes[3] != "*":
        return None
    minuto, hora, _, _, dias = partes
    if not (minuto.isdigit() and hora.isdigit()) or int(minuto) > 59 or int(hora) > 23:
        return None
    if dias == "*":
        return Ritmo(time(int(hora), int(minuto)), frozenset(range(7)))
    semana: set[int] = set()
    for parte in dias.split(","):
        desde, _, hasta = parte.partition("-")
        if not desde.isdigit() or (hasta and not hasta.isdigit()):
            return None
        a, b = int(desde), int(hasta or desde)
        if a > 7 or b > 7 or a > b:
            return None
        semana |= {(d - 1) % 7 for d in range(a, b + 1)}
    return Ritmo(time(int(hora), int(minuto)), frozenset(semana))


# --- Guardar los pedidos del día --------------------------------------------------------------

def guardar_los_pedidos(m: Momento) -> int:
    """La pasada de la cadencia (una de la escalera): el día de cada cadencia a cada integrante
    en privado, el pedido de cada persona con tareas abiertas, para la hora de la cadencia; un día
    de la cadencia que pasó sin atenderse, omitido. Cuántos pedidos guardó para salir."""
    cur = m.cur
    cur.execute("""select * from cadence_job where activo and audiencia = %s
                    order by nombre, id""", (PRIVADO,))
    guardados = 0
    for cadencia in cur.fetchall():
        ritmo = leer_ritmo(cadencia["cron"])
        if ritmo is None:
            _no_se_entiende(m, cadencia)
            continue
        guardados += _una_cadencia(m, cadencia, ritmo)
    return guardados


def _una_cadencia(m: Momento, cadencia: dict[str, Any], ritmo: Ritmo) -> int:
    ultima = cadencia["ultima_corrida"]
    atendida = None
    guardados = 0
    for dia in (_anterior(ritmo, m.hoy), m.hoy if m.hoy.weekday() in ritmo.dias else None):
        if dia is None:
            continue
        momento = datetime.combine(dia, ritmo.hora, tzinfo=m.cal.zona)
        if ultima is not None and ultima >= momento:
            continue                    # ya se atendió
        if ultima is None and dia < m.hoy:
            continue                    # antes de la primera vuelta: no se repone
        for persona in _con_tareas(m):
            aviso_id, nuevo = guardar(
                m.cur, m.workspace_id, COMO_VIENEN_SUS_TAREAS, task_id=None,
                destinatario=persona,
                hechos={"aviso": COMO_VIENEN_SUS_TAREAS, "necesita_respuesta": True},
                programado_para=sale(m.cal, momento),
                clave=clave(cadencia["id"], persona, dia), ahora=m.ahora)
            if not nuevo:
                continue
            if dia < m.hoy:
                omitir(m.cur, aviso_id, YA_PASO_SU_MOMENTO, m.ahora)
            elif not m.cal.es_habil(dia):
                omitir(m.cur, aviso_id, NO_ES_DIA_HABIL, m.ahora)
            else:
                guardados += 1
        atendida = momento
    if atendida is not None or ultima is None:
        m.cur.execute("update cadence_job set ultima_corrida = %s where id = %s",
                      (atendida or m.ahora, cadencia["id"]))
    return guardados


def _anterior(ritmo: Ritmo, hoy: date) -> date | None:
    """El último día de la cadencia antes de hoy, en la semana anterior."""
    for atras in range(1, 8):
        dia = hoy - timedelta(days=atras)
        if dia.weekday() in ritmo.dias:
            return dia
    return None


def clave(cadencia_id, persona: str, dia: date) -> str:
    """motor:como_vienen_sus_tareas:<cadencia>:<persona>:<día>: uno por persona y por día."""
    return f"motor:{COMO_VIENEN_SUS_TAREAS}:{cadencia_id}:{persona}:{dia.isoformat()}"


def dia_de_la_clave(aviso: dict[str, Any]) -> date:
    return date.fromisoformat(aviso["dedupe_key"].split(":")[4])


def _con_tareas(m: Momento) -> list[str]:
    """Las personas activas con tareas para la lista."""
    m.cur.execute("""select distinct t.responsable_membership_id as persona
                       from task t join integrante i on i.membership_id = t.responsable_membership_id
                      where i.activo and t.estado::text = any(%s)
                        and not exists (select 1 from blocker b
                                         where b.task_id = t.id and b.resuelto_en is null)
                      order by 1""", (list(ABIERTOS),))
    return [str(f["persona"]) for f in m.cur.fetchall()]


def _no_se_entiende(m: Momento, cadencia: dict[str, Any]) -> None:
    """Un incidente por día mientras siga sin entenderse (la cadencia guarda cuándo se miró:
    `ultima_corrida`); cuando se corrija, cuenta desde ahí y no repone lo que no corrió."""
    ultima = cadencia["ultima_corrida"]
    if ultima is not None and m.fecha(ultima) >= m.hoy:
        return
    registrar_incidente(
        m.cur, m.workspace_id,
        f"La cadencia «{cadencia['nombre']}» del espacio tiene un ritmo que no se entiende "
        f"({cadencia['cron']!r}): no corre hasta que se corrija en el pack o en la plataforma. "
        f"Las demás cadencias siguen.", severidad="media", etapa=ETAPA)
    m.cur.execute("update cadence_job set ultima_corrida = %s where id = %s",
                  (m.ahora, cadencia["id"]))


# --- La lista ----------------------------------------------------------------------------------

def tareas_de(cur, persona: str) -> list[dict[str, Any]]:
    """Las tareas de la persona para la lista, por su vencimiento y su título: asignadas o en
    curso, sin un bloqueo abierto."""
    cur.execute("""select t.id, t.titulo, t.estado::text estado, t.fecha_objetivo, t.area_id,
                          t.responsable_membership_id, false as bloqueada
                     from task t
                    where t.responsable_membership_id = %s and t.estado::text = any(%s)
                      and not exists (select 1 from blocker b
                                       where b.task_id = t.id and b.resuelto_en is null)
                    order by t.fecha_objetivo nulls last, t.titulo""", (persona, list(ABIERTOS)))
    return cur.fetchall()


def vigencia(m: Momento, aviso: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    """Si el pedido todavía corresponde: es su día (mecánica §12) y la persona tiene tareas para
    la lista. La lista misma la arma el envío (`avisos._a_la_lista`), con lo que la escalera
    tenía para ese día adentro."""
    if dia_de_la_clave(aviso) != m.hoy:
        return YA_PASO_SU_MOMENTO, {}
    if not tareas_de(m.cur, str(aviso["destinatario_membership_id"])):
        return SIN_TAREAS_ABIERTAS, {}
    return None, {"aviso": COMO_VIENEN_SUS_TAREAS, "necesita_respuesta": True}


def renglon(m: Momento, tarea: dict[str, Any],
            del_dia: list[dict[str, Any]] = ()) -> dict[str, Any]:
    """Lo que la lista dice de una tarea: lo mismo que un pedido de estado de su escalera (cuánto
    falta o el atraso, el estado, el día que dio para terminarla, lo que depende de ella y qué
    espera saber), si vence hoy y, encima, lo que la escalera tenía para ese día sobre ella."""
    if tarea["fecha_objetivo"] is None:
        dicho: dict[str, Any] = {"tarea": tarea["titulo"], "estado": tarea["estado"]}
    else:
        dicho = hechos_de_la_escalera(m, COMO_VIENEN_SUS_TAREAS, tarea,
                                      {"necesita_respuesta": True})
        dicho.pop("necesita_respuesta", None)       # la lista entera la pide, una vez
        if m.fecha(tarea["fecha_objetivo"]) == m.hoy:
            dicho["vence_hoy"] = True
    for hechos in del_dia:
        dicho.update({k: v for k, v in hechos.items()
                      if k not in ("aviso", "necesita_respuesta")})
    return dicho


# --- Cuándo vuelve a preguntar ----------------------------------------------------------------

def cuando_vuelve_a_preguntar(cur, cal, workspace_id: str, tarea: dict[str, Any],
                              ahora: datetime) -> datetime | None:
    """Cuándo Leda vuelve a preguntar por una tarea de la que la persona contó cómo viene sin que
    su escalera lo hubiera pedido: en la próxima lista de una cadencia o el día en que su
    escalera pide el estado, lo que llegue antes. `None` si nada de eso va a pasar."""
    candidatos = [proximo_pedido(cur, cal, ahora)]
    if tarea.get("fecha_objetivo") is not None:
        vence = tarea["fecha_objetivo"].astimezone(cal.zona).date()
        candidatos.append(sale_el(cal, anclaje(cur, tarea["id"], vence).fecha))
    futuros = [c for c in candidatos if c is not None and c > ahora]
    return min(futuros) if futuros else None


def proximo_pedido(cur, cal, ahora: datetime) -> datetime | None:
    """Cuándo sale la próxima lista de una cadencia a cada integrante en privado: el próximo día
    hábil de una cadencia que se entiende, a su hora (o a la hora en que Leda manda lo suyo)."""
    cur.execute("select cron from cadence_job where activo and audiencia = %s", (PRIVADO,))
    ritmos = [r for r in (leer_ritmo(f["cron"]) for f in cur.fetchall()) if r is not None]
    hoy = ahora.astimezone(cal.zona).date()
    proximos = []
    for ritmo in ritmos:
        for adelante in range(_DIAS_HACIA_ADELANTE):
            dia = hoy + timedelta(days=adelante)
            if dia.weekday() not in ritmo.dias or not cal.es_habil(dia):
                continue
            cuando = sale(cal, datetime.combine(dia, ritmo.hora, tzinfo=cal.zona))
            if cuando > ahora and cuando.astimezone(cal.zona).date() == dia:
                proximos.append(cuando)
                break
    return min(proximos) if proximos else None
