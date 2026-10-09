"""Los pedidos de estado con ritmo fijo: la cadencia del espacio (C-6, circuito 5).

Decisión 8 del usuario (`odd/tasks/fase-c.md`, 2026-10-08, opción A); ADR 0017, decisión 3b, punto 5
("pedidos de estado según las cadencias del espacio"); mecánica §9, §10 y §12; conversación 37. Las
cadencias del pack (`cadencia`, que el importador carga en `cadence_job`) se retiraron del motor en la
E3-7 con el ciclo viejo; vuelven acá, como una pasada más de la escalera.

**Un pedido de estado por persona con la lista de sus tareas.** El día de una cadencia a cada
integrante en privado (`privado_cada_integrante`), cada persona con tareas abiertas recibe un solo
mensaje (`como_vienen_sus_tareas`) con sus tareas y una sola pregunta, por la lista entera. Van en la
lista todas sus tareas abiertas, cada una con su situación (`tareas_de`, `renglon`; decisión 32 del
usuario, 2026-10-09): también la trabada (con lo que la traba) y la entregada (esperando revisión),
para que vea todo junto y avise si algo cambió. Leda pregunta cómo vienen sólo por las que se pueden
mover (asignadas o en curso, sin un bloqueo: `se_puede_mover`); si no hay ninguna, la lista sale sin
pregunta.

**La primera lista de la semana es completa; las otras, sólo lo que falta** (decisión 46; `armar`).
Cada lista que sale guarda, fuera de los hechos, las tareas abiertas de la persona con su situación
(`situacion`: el estado, los bloqueos abiertos, el día que dio para terminarla y si ya quedó atrasada)
y si se preguntó por cada una (`scheduled_notice.tareas_de_la_lista`, migración 0047). La siguiente de
la misma semana lleva sólo las tareas nuevas, las que se preguntaron y no contestó (con desde cuándo,
`sin_respuesta_desde`), las que cambiaron y las que traen algo de la escalera de ese día; si no hay
ninguna, no sale (`SIN_NOVEDADES`).

**Lo contestado no se vuelve a preguntar** (decisión 31; `anotar_lo_que_conto`, `ya_lo_conto`). Lo
que la persona cuenta de una tarea suya la deja contestada en la última lista que le salió, con la
situación de después: una sola regla, en la lista o fuera de ella (corrección de la C-6, del
coordinador). Con eso, la lista siguiente no la trae si no cambió, y el pedido de estado del día
del vencimiento (el primero de su escalera) no sale si la contó después de esa lista y no cambió
nada: cubre hasta la lista siguiente. Una respuesta vaga ("ya casi") también es contar cómo viene.
Ese pedido queda dado, con su motivo (`YA_LO_CONTO`), como el primer paso de la escalera, que sigue
anclada al vencimiento (mecánica §9): el día hábil siguiente, si sigue sin entregar, sale el
segundo pedido, y el escalamiento llega el mismo día que sin la lista. Si ese día sale una lista,
el pedido va en ella. Un día que dio la persona (una previsión, también dicha en la lista) se sigue
como toda previsión: ese día se le pregunta. Que llegue el día en que vence no es un cambio;
quedar atrasada sin entregar, sí.

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
preguntar en la próxima lista completa o cuando su escalera lo pida (el día del vencimiento, o el
siguiente si lo contestado lo cubre), lo que llegue antes; y si su aviso previo todavía no salió, lo
próximo es ese aviso, como siempre (decisión 44; `cuando_vuelve_a_preguntar`). Con un día dado por
la persona, Leda pregunta ese día.
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

Las cadencias al grupo (`grupo`) no son un pedido a cada persona: son el informe al grupo
(`informe_al_grupo.py`, decisión 25), que usa la misma cuenta de los días de una cadencia
(`atender`).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any, NamedTuple

from ..incidentes import registrar_incidente

from .ancla import anclaje, prevision_vigente
from .avisos import ABIERTOS, Momento, guardar, hechos_de_la_escalera, leer_tarea, omitir
from .preguntas import COMO_VIENEN_SUS_TAREAS
from .tiempo import sale, sale_el

PRIVADO = "privado_cada_integrante"
# Por qué un pedido de la lista no salió: su día pasó (mecánica §12), era feriado, o la persona ya
# no tenía tareas por las que preguntar.
YA_PASO_SU_MOMENTO = "ya_paso_su_momento"
NO_ES_DIA_HABIL = "no_es_dia_habil"
SIN_TAREAS_ABIERTAS = "sin_tareas_abiertas"
# El pedido de estado del día del vencimiento que no sale porque la persona ya contó cómo viene
# la tarea (decisión 31): queda dado, con este motivo, como el primer paso de su escalera.
YA_LO_CONTO = "ya_conto_como_viene"
# Una lista de la semana que no es la primera y no tiene nada que no se haya contestado ni que haya
# cambiado: no sale (decisión 46).
SIN_NOVEDADES = "sin_novedades_para_la_lista"
# Lo que dicen los hechos de una lista que no es la primera de la semana, y de una tarea que la
# persona no contestó en la lista anterior (decisión 46); y, después de "viene bien", cuándo le
# llega antes el aviso previo (decisión 44).
SOLO_LO_QUE_FALTA = "solo_lo_que_cambio_o_falta"
SIN_RESPUESTA_DESDE = "sin_respuesta_desde"
ANTES_LE_RECUERDA = "antes_le_recuerda_que_vence"
# Las tareas de la lista: todas las abiertas de la persona (decisión 32).
ABIERTAS = ("asignada", "en_curso", "bloqueada", "en_revision")
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
    def del_dia(dia: date, momento: datetime) -> list[tuple[str, bool]]:
        return [guardar(m.cur, m.workspace_id, COMO_VIENEN_SUS_TAREAS, task_id=None,
                        destinatario=persona,
                        hechos={"aviso": COMO_VIENEN_SUS_TAREAS, "necesita_respuesta": True},
                        programado_para=sale(m.cal, momento),
                        clave=clave(cadencia["id"], persona, dia), ahora=m.ahora)
                for persona in _con_tareas(m)]

    return atender(m, cadencia, ritmo, del_dia)


def atender(m: Momento, cadencia: dict[str, Any], ritmo: Ritmo, del_dia) -> int:
    """Los días de una cadencia que tocan ahora: el último antes de hoy y hoy, si es su día.
    `del_dia(dia, momento)` guarda lo de ese día y devuelve cada aviso (id, si es nuevo). Uno de
    un día que pasó sin atenderse queda omitido (mecánica §12), uno de un feriado también; antes
    de la primera vuelta no se repone nada. `cadence_job.ultima_corrida` dice hasta qué día se
    atendió. Cuántos quedaron para salir."""
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
        for aviso_id, nuevo in del_dia(dia, momento):
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
    """Las personas activas con tareas abiertas para la lista."""
    m.cur.execute("""select distinct t.responsable_membership_id as persona
                       from task t join integrante i on i.membership_id = t.responsable_membership_id
                      where i.activo and t.estado::text = any(%s)
                      order by 1""", (list(ABIERTAS),))
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
    """Las tareas abiertas de la persona para la lista, por su vencimiento y su título: asignadas,
    en curso, trabadas o entregadas (decisión 32)."""
    cur.execute("""select t.id, t.titulo, t.estado::text estado, t.fecha_objetivo, t.area_id,
                          t.responsable_membership_id,
                          exists (select 1 from blocker b
                                   where b.task_id = t.id and b.resuelto_en is null) bloqueada
                     from task t
                    where t.responsable_membership_id = %s and t.estado::text = any(%s)
                    order by t.fecha_objetivo nulls last, t.titulo""", (persona, list(ABIERTAS)))
    return cur.fetchall()


def se_puede_mover(tarea: dict[str, Any]) -> bool:
    """Si Leda pregunta cómo viene: asignada o en curso, sin un bloqueo abierto. La trabada la sigue
    la persecución del bloqueo (C-5) y la entregada espera la revisión de otra persona."""
    return tarea["estado"] in ABIERTOS and not tarea["bloqueada"]


def vigencia(m: Momento, aviso: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    """Si el pedido todavía corresponde: es su día (mecánica §12) y la persona tiene tareas para
    la lista. La lista misma la arma el envío (`avisos._a_la_lista`, `armar`), con lo que la
    escalera tenía para ese día adentro."""
    if dia_de_la_clave(aviso) != m.hoy:
        return YA_PASO_SU_MOMENTO, {}
    if not tareas_de(m.cur, str(aviso["destinatario_membership_id"])):
        return SIN_TAREAS_ABIERTAS, {}
    return None, {"aviso": COMO_VIENEN_SUS_TAREAS, "necesita_respuesta": True}


def renglon(m: Momento, tarea: dict[str, Any],
            del_dia: list[dict[str, Any]] = ()) -> dict[str, Any]:
    """Lo que la lista dice de una tarea: lo mismo que un pedido de estado de su escalera (cuánto
    falta o el atraso, el estado, el día que dio para terminarla, lo que depende de ella y qué
    espera saber), si vence hoy, lo que la traba si está trabada y, encima, lo que la escalera
    tenía para ese día sobre ella."""
    if tarea["fecha_objetivo"] is None:
        dicho: dict[str, Any] = {"tarea": tarea["titulo"], "estado": tarea["estado"]}
    else:
        dicho = hechos_de_la_escalera(m, COMO_VIENEN_SUS_TAREAS, tarea,
                                      {"necesita_respuesta": True})
        dicho.pop("necesita_respuesta", None)       # la lista entera la pide, una vez
        if m.fecha(tarea["fecha_objetivo"]) == m.hoy:
            dicho["vence_hoy"] = True
    if tarea["bloqueada"]:
        # Trabada (decisión 32): con lo que la traba, como lo dijo la persona.
        if dicho.get("estado") != "bloqueada":
            dicho.pop("estado_desde", None)         # era desde cuándo tenía el otro estado
        dicho["estado"] = "bloqueada"
        m.cur.execute("""select causa from blocker where task_id = %s and resuelto_en is null
                          order by abierto_en, id""", (str(tarea["id"]),))
        dicho["causas"] = [f["causa"] for f in m.cur.fetchall()]
    for hechos in del_dia:
        dicho.update({k: v for k, v in hechos.items()
                      if k not in ("aviso", "necesita_respuesta")})
    return dicho


def situacion(cur, cal, ahora: datetime, tarea: dict[str, Any]) -> dict[str, Any]:
    """La situación de una tarea, para saber si cambió desde la lista anterior o desde que la
    persona la contó (decisiones 31 y 46): su estado (trabada si tiene un bloqueo abierto), sus
    bloqueos abiertos, el día que dio para terminarla y si pasó el día de su seguimiento (la fecha
    comprometida, o la que dio si es posterior) sin entregarse. Que llegue el día en que vence no
    la cambia."""
    cur.execute("""select id from blocker where task_id = %s and resuelto_en is null
                    order by id""", (str(tarea["id"]),))
    bloqueos = [str(f["id"]) for f in cur.fetchall()]
    prevision = prevision_vigente(cur, tarea["id"])
    atrasada = False
    if tarea["fecha_objetivo"] is not None:
        vence = tarea["fecha_objetivo"].astimezone(cal.zona).date()
        atrasada = ahora.astimezone(cal.zona).date() > anclaje(cur, tarea["id"], vence).fecha
    return {"estado": "bloqueada" if tarea["bloqueada"] or bloqueos else tarea["estado"],
            "bloqueos": bloqueos,
            "prevision": prevision["fecha_prevista"].isoformat() if prevision else None,
            "atrasada": atrasada}


@dataclass(frozen=True)
class Armada:
    """La lista de una persona, armada al salir: sus renglones, las tareas por las que pregunta,
    si es la primera de la semana y lo que lleva (lo que se guarda fuera de los hechos)."""

    renglones: list[dict[str, Any]]
    preguntadas: tuple[str, ...]
    completa: bool
    lleva: dict[str, Any]


def armar(m: Momento, persona: str, del_dia: dict[str, list[dict[str, Any]]]) -> Armada:
    """La lista de la persona (decisiones 32 y 46). La primera de la semana, con todas sus tareas
    abiertas. Las otras, sólo con las tareas nuevas, las que se preguntaron en la anterior y no
    contestó, las que cambiaron desde la anterior (o desde que las contó) y las que traen algo de
    la escalera de ese día (`del_dia`, por tarea). Pregunta por las que se pueden mover."""
    anterior = _la_anterior_de_la_semana(m, persona)
    completa = anterior is None
    ya = (anterior or {}).get("tareas") or {}
    renglones: list[dict[str, Any]] = []
    preguntadas: list[str] = []
    lleva: dict[str, Any] = {}
    for tarea in tareas_de(m.cur, persona):
        tid = str(tarea["id"])
        ahora = situacion(m.cur, m.cal, m.ahora, tarea)
        antes = ya.get(tid)
        sin_respuesta = bool(antes and antes.get("preguntada") and not antes.get("contestada_en"))
        va = (completa or tid in del_dia or antes is None or sin_respuesta
              or ahora != antes.get("situacion"))
        pregunta = va and se_puede_mover(tarea)
        desde = None
        if pregunta:
            desde = antes["sin_respuesta_desde"] if sin_respuesta else m.hoy.isoformat()
        lleva[tid] = {"situacion": ahora, "mostrada": va, "preguntada": pregunta,
                      "sin_respuesta_desde": desde, "contestada_en": None}
        if not va:
            continue
        dicho = renglon(m, tarea, del_dia.get(tid, []))
        if pregunta and sin_respuesta:
            dicho[SIN_RESPUESTA_DESDE] = desde
        renglones.append(dicho)
        if pregunta:
            preguntadas.append(tid)
    return Armada(renglones, tuple(preguntadas), completa, {"tareas": lleva})


def _la_anterior_de_la_semana(m: Momento, persona: str) -> dict[str, Any] | None:
    """Lo que llevó la última lista que le salió a la persona esta semana, o `None` si ésta es la
    primera (o si la anterior es de antes de la migración 0047: ésta va completa)."""
    fila = _la_ultima_que_salio(m.cur, persona)
    if fila is None or fila["tareas_de_la_lista"] is None:
        return None
    if m.fecha(fila["resuelto_en"]).isocalendar()[:2] != m.hoy.isocalendar()[:2]:
        return None
    return fila["tareas_de_la_lista"]


def _la_ultima_que_salio(cur, persona: str) -> dict[str, Any] | None:
    cur.execute("""select id, resuelto_en, tareas_de_la_lista from scheduled_notice
                    where destinatario_membership_id = %s and tipo = %s and estado = 'enviado'
                    order by resuelto_en desc limit 1""", (persona, COMO_VIENEN_SUS_TAREAS))
    return cur.fetchone()


def sin_contestar_en_la_lista(cur, persona: str, task_id, antes_del: date) -> bool:
    """Si la lista le pregunta a la persona por la tarea desde antes del día `antes_del` y no
    contestó: la última que le salió la preguntó sin respuesta desde un día anterior (el informe al
    grupo: lo que Leda no sabe, decisión 55)."""
    fila = _la_ultima_que_salio(cur, persona)
    lleva = (fila["tareas_de_la_lista"] if fila is not None else None) or {}
    dicha = (lleva.get("tareas") or {}).get(str(task_id))
    if not dicha or not dicha.get("preguntada") or dicha.get("contestada_en"):
        return False
    desde = dicha.get("sin_respuesta_desde")
    return desde is not None and date.fromisoformat(desde) < antes_del


# --- Lo contestado (decisión 31) ----------------------------------------------------------------

def anotar_lo_que_conto(ctx, task_id) -> None:
    """La persona contó algo de una tarea suya (una jugada sobre ella, en la lista o fuera de
    ella, con el mismo efecto): en la última lista que le salió, la tarea queda contestada, con su
    situación de después. Así la lista siguiente no se la vuelve a preguntar si no cambió
    (decisión 46), y el pedido del día del vencimiento no sale si nada cambió (decisión 31,
    `ya_lo_conto`)."""
    cur = ctx.cur
    fila = _la_ultima_que_salio(cur, ctx.quien.membership_id)
    lleva = fila["tareas_de_la_lista"] if fila is not None else None
    if not lleva or str(task_id) not in (lleva.get("tareas") or {}):
        return
    tarea = leer_tarea(cur, task_id)
    if tarea is None:
        return
    tareas = dict(lleva["tareas"])
    antes = tareas[str(task_id)]
    tareas[str(task_id)] = {**antes, "contestada_en": ctx.ahora.isoformat(),
                            "situacion": situacion(cur, ctx.calendario, ctx.ahora, tarea)}
    cur.execute("update scheduled_notice set tareas_de_la_lista = %s where id = %s",
                (json.dumps({**lleva, "tareas": tareas}, ensure_ascii=False), fila["id"]))


def ya_lo_conto(m: Momento, tarea: dict[str, Any]) -> bool:
    """Si el pedido de estado del día del vencimiento de la tarea no sale porque la persona ya
    contó cómo viene (decisión 31): después de la última lista que le salió, en la lista o fuera
    de ella, y no cambió nada desde lo último que contó. Si hoy le sale una lista, no: el pedido
    va en ella. Con un día dado por la persona (una previsión vigente), tampoco: ese día se sigue
    como toda previsión."""
    cur, persona = m.cur, str(tarea["responsable_membership_id"])
    if prevision_vigente(cur, tarea["id"]) is not None:
        return False
    cur.execute("""select programado_para from scheduled_notice
                    where destinatario_membership_id = %s and tipo = %s and estado = 'guardado'""",
                (persona, COMO_VIENEN_SUS_TAREAS))
    if any(m.fecha(f["programado_para"]) == m.hoy for f in cur.fetchall()):
        return False
    fila = _la_ultima_que_salio(cur, persona)
    lleva = (fila["tareas_de_la_lista"] if fila is not None else None) or {}
    dicha = (lleva.get("tareas") or {}).get(str(tarea["id"]))
    if not dicha or not dicha.get("contestada_en"):
        return False
    return dicha.get("situacion") == situacion(cur, m.cal, m.ahora, tarea)


# --- Cuándo vuelve a preguntar ----------------------------------------------------------------

def cuando_vuelve_a_preguntar(cur, cal, workspace_id: str, tarea: dict[str, Any],
                              ahora: datetime) -> tuple[datetime | None, datetime | None]:
    """Cuándo Leda vuelve a preguntar por una tarea de la que la persona contó cómo viene en la
    lista sin que su escalera lo hubiera pedido, y cuándo le llega antes el aviso previo, si
    todavía no salió (decisión 44). Pregunta en la próxima lista completa (la primera de otra
    semana) o cuando su escalera lo pida, lo que llegue antes: el día de su seguimiento si sale
    una lista en el medio (lo contestado cubre hasta la lista siguiente, decisión 31) o si es un
    día que dio la persona (`ya_lo_conto`) y, si no, el día hábil siguiente. `None` si nada de eso
    va a pasar."""
    candidatos = [proxima_lista_completa(cur, cal, ahora)]
    antes = None
    if tarea.get("fecha_objetivo") is not None:
        hoy = ahora.astimezone(cal.zona).date()
        vence = tarea["fecha_objetivo"].astimezone(cal.zona).date()
        hasta = anclaje(cur, tarea["id"], vence).fecha
        cubre = prevision_vigente(cur, tarea["id"]) is None and not _hay_una_lista(
            cur, cal, hoy, hasta)
        dia = cal.proximo_habil(hasta + timedelta(days=1)) if cubre else hasta
        candidatos.append(sale_lo_del_dia(cur, cal, dia))
        if hasta == vence:
            antes = _el_aviso_previo_por_salir(cur, cal, workspace_id, tarea, vence, ahora)
    futuros = [c for c in candidatos if c is not None and c > ahora]
    vuelve = min(futuros) if futuros else None
    if antes is not None and vuelve is not None and antes >= vuelve:
        antes = None
    return vuelve, antes


def _ritmos(cur) -> list[Ritmo]:
    cur.execute("select cron from cadence_job where activo and audiencia = %s", (PRIVADO,))
    return [r for r in (leer_ritmo(f["cron"]) for f in cur.fetchall()) if r is not None]


def _listas_del_dia(cur, cal, dia: date) -> list[datetime]:
    """A qué hora salen las listas de ese día, si es hábil y tiene una cadencia."""
    if not cal.es_habil(dia):
        return []
    horas = [sale(cal, datetime.combine(dia, r.hora, tzinfo=cal.zona))
             for r in _ritmos(cur) if dia.weekday() in r.dias]
    return [h for h in horas if h.astimezone(cal.zona).date() == dia]


def _hay_una_lista(cur, cal, desde: date, hasta: date) -> bool:
    """Si sale una lista después del día `desde` y hasta el día `hasta`, inclusive."""
    dia = desde + timedelta(days=1)
    while dia <= hasta:
        if _listas_del_dia(cur, cal, dia):
            return True
        dia += timedelta(days=1)
    return False


def sale_lo_del_dia(cur, cal, dia: date) -> datetime:
    """Cuándo sale lo que la escalera tiene para ese día: a la hora de salida o, si ese día sale
    una lista más tarde, con ella (lo espera y va adentro, `avisos._a_la_lista`)."""
    return max([sale_el(cal, dia), *_listas_del_dia(cur, cal, dia)])


def _el_aviso_previo_por_salir(cur, cal, workspace_id: str, tarea: dict[str, Any], vence: date,
                               ahora: datetime) -> datetime | None:
    """Cuándo sale el aviso previo de la tarea, si todavía no salió y su día no pasó."""
    from .escalera import BLOQUEO_ABIERTO, MINIMO_DEL_NUCLEO, clave, dias_de_aviso_previo

    base = clave("aviso_previo", tarea["id"], vence)
    cur.execute("""select 1 from scheduled_notice
                    where (dedupe_key = %s or dedupe_key like %s)
                      and not (estado = 'omitido' and motivo_omision = %s)""",
                (base, base + ":b%", BLOQUEO_ABIERTO))
    if cur.fetchone() is not None:
        return None
    dia, faltan = vence, dias_de_aviso_previo(cur, workspace_id) or MINIMO_DEL_NUCLEO
    while faltan > 0:
        dia -= timedelta(days=1)
        if cal.es_habil(dia):
            faltan -= 1
    cuando = sale_lo_del_dia(cur, cal, dia)
    return cuando if cuando > ahora else None


def proxima_lista_completa(cur, cal, ahora: datetime) -> datetime | None:
    """Cuándo sale la próxima lista completa: la primera de una semana que no es ésta (decisión
    46), a su hora (o a la hora en que Leda manda lo suyo)."""
    hoy = ahora.astimezone(cal.zona).date()
    dia = hoy + timedelta(days=7 - hoy.weekday())
    for _ in range(_DIAS_HACIA_ADELANTE):
        listas = _listas_del_dia(cur, cal, dia)
        if listas:
            return min(listas)
        dia += timedelta(days=1)
    return None
