"""El informe al grupo (C-6; decisión 25 del usuario, 2026-10-09, opción A; decisiones 8, 35, 45 y
49; constitución §8 y §13; mecánica §10 y §12; conversación 41).

**Qué es.** El día de una cadencia al grupo del espacio (`cadence_job.audiencia = 'grupo'`, como
`resumen_grupal` e `informe_semanal` de CoreWork), Leda le manda al grupo del equipo lo que pasó con
las tareas, para que todos estén al tanto y puedan ayudar ("lucas lee eso y se entera que marcos
estaba frenado porque le falta el cable y el tiene un cable extra"). Informa avances y problemas, no
juzga (decisión 8). Cada renglón lleva el nombre de quien tiene la tarea (`la_tiene`, decisión 25):

- las **terminadas** desde el informe anterior (o, el primero, desde el lunes de esa semana);
- los **atrasos ya hablados en privado** (`atrasadas`): la tarea con el día en que vencía, el día
  que dio la persona y su motivo, si los dio, como información, nunca como acusación ("• PLC
  (Marcos): vencía el lun 26/10, la termina el mié 28/10 (falta que llegue el cable)"). Es hablado
  en privado (constitución §8: los atrasos, primero en privado) si la persona le dio a Leda un día
  posterior al vencimiento (su previsión vigente), o si quedó asentado que está atrasada porque no
  contestó (el escalamiento por falta de respuesta salió; decisiones 21, 35 y 49). Un atraso que la
  persona todavía no habló no figura en ninguna parte del informe, ni como algo que sigue: nunca
  algo de lo que no se enteró primero ella;
- las **trabadas**, con lo que las traba como lo dijo la persona, desde cuándo, cuántos días hábiles
  lleva y, si quien la destraba dijo un día, ese día (decisión 8: "Trabadas: …, esperando un
  repuesto que llega el lunes"); lo asentado de un bloqueo viejo o de una cadena que nadie toma
  figura acá (decisiones 35, 36 y 49);
- las **entregadas**, que esperan la revisión;
- las que **siguen**, con su estado y el día en que vencen.

Sin nada de eso, no sale nada: queda omitido con su motivo (`NADA_PARA_INFORMAR`), nunca un
mensaje vacío. La tarea de un integrante inactivo no figura.

**A dónde.** Al grupo del espacio (`workspace.grupo_chat_id`, del pack `telegram.grupo_gestion_id`),
por el outbox, como la presentación (`onboarding.encolar_presentacion`). El aviso se guarda en
`scheduled_notice` como cualquier otro, sin destinatario y con `al_grupo` (migración 0048); el chat
no se guarda ahí (`docs/architecture/frontera.md`, regla 2): sale del espacio al encolarlo. El RLS
del espacio (constitución §13) rige igual: un informe lee sólo las tareas de su espacio y va sólo a
su grupo.

**Cuándo.** El día de la cadencia, a su hora o a la hora en que Leda manda lo suyo si es antes
(`tiempo.sale`; decisión 45), dentro del horario. Una vez por día de la cadencia, con la misma
cuenta que la lista a cada persona (`cadencias.atender`): un día que pasó sin atenderse, o un
informe que no llegó a salir ese día, queda omitido (mecánica §12: no se manda tarde); su fila del
outbox vence al terminar ese día. No interrumpe a nadie: no es de ninguna persona.

**Lo redacta la IA** (regla del mozo), desde los hechos (`hechos.SIGNIFICADOS` dice qué es cada
uno). Si no lo redacta, se reintenta a los 1, 2, 4 y 8 minutos (`avisos.ESPERAS_TRAS_UN_FALLO`); al
quinto fallo queda `fallido` con sus hechos y un incidente para la administración. Nunca sale un
texto armado a mano.

**Leda no conversa en el grupo** en esta etapa: el informe no pide respuesta, no abre ninguna
pregunta, no es el último aviso de nadie ni entra en el registro de turnos de una persona. No
cuenta para el tope diario (no va a una persona; mecánica §10). Queda en la auditoría como un envío
de Leda (constitución §12), sobre el aviso.

**Si el espacio tiene informe al grupo** es un solo predicado (`asentado.hay_informe_al_grupo`):
el grupo y una cadencia al grupo activa con un ritmo que se entiende. Lo usa este módulo para
guardar el informe y la decisión 35 para decir "para que el equipo esté al tanto" sólo cuando es
verdad.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date, datetime, timedelta
from typing import Any

from ..incidentes import registrar_incidente
from ..salida import PayloadValidationError, enqueue_outbox
from .ancla import prevision_vigente
from .asentado import AL_GRUPO, hay_informe_al_grupo
from .auditoria import auditar
from .avisos import (ESPERAS_TRAS_UN_FALLO, ETAPA_AVISO_GUARDADO, ETAPA_AVISO_REINTENTO, INTENTOS,
                     Momento, guardar, omitir)
from .cadencias import YA_PASO_SU_MOMENTO, atender, leer_ritmo
from .registro import no_vacio
from .tiempo import sale

INFORME_AL_GRUPO = "informe_al_grupo"
# Por qué un informe al grupo no salió: no había nada que informar, o el espacio ya no tiene grupo.
NADA_PARA_INFORMAR = "nada_para_el_informe"
SIN_GRUPO = "sin_grupo"
# Lo que dice el informe además de sus listas (decisión 55).
SIN_SABER = "sin_saber_como_vienen"
TODO_EN_ORDEN = "todo_en_orden"
SEMANA_BUENA = "semana_buena"
SIN_NOVEDADES = "sin_novedades_para_el_grupo"
# Las tareas abiertas del informe y las que siguen su curso (comprometidas, sin entregar).
ABIERTAS = ("asignada", "en_curso", "bloqueada", "en_revision")
SIGUEN = ("asignada", "en_curso")


# --- Guardar ----------------------------------------------------------------------------------

def guardar_los_informes(m: Momento) -> int:
    """La pasada del informe al grupo (una de la escalera): el día de cada cadencia al grupo, el
    informe de ese día, para su hora. Sólo si el espacio tiene informe al grupo
    (`asentado.hay_informe_al_grupo`). Cuántos quedaron para salir."""
    if not hay_informe_al_grupo(m.cur, m.workspace_id):
        return 0
    m.cur.execute("""select * from cadence_job where activo and audiencia = %s
                      order by nombre, id""", (AL_GRUPO,))
    guardados = 0
    for cadencia in m.cur.fetchall():
        ritmo = leer_ritmo(cadencia["cron"])
        if ritmo is None:
            continue        # el predicado lo deja fuera; la lista a cada persona ya lo avisa

        def del_dia(dia: date, momento: datetime, cadencia=cadencia) -> list[tuple[str, bool]]:
            return [guardar(m.cur, m.workspace_id, INFORME_AL_GRUPO, task_id=None,
                            destinatario=None, al_grupo=True,
                            hechos={"aviso": INFORME_AL_GRUPO, "necesita_respuesta": False},
                            programado_para=sale(m.cal, momento),
                            clave=clave(cadencia["id"], dia), ahora=m.ahora)]

        guardados += atender(m, cadencia, ritmo, del_dia)
    return guardados


def clave(cadencia_id, dia: date) -> str:
    """motor:informe_al_grupo:<cadencia>:<día>: uno por cadencia y por día."""
    return f"motor:{INFORME_AL_GRUPO}:{cadencia_id}:{dia.isoformat()}"


def _dia_de_la_clave(aviso: dict[str, Any]) -> date:
    return date.fromisoformat(aviso["dedupe_key"].split(":")[3])


# --- Enviar -----------------------------------------------------------------------------------

def enviar(m: Momento, ia) -> Counter:
    """Los informes al grupo cuya hora llegó (dentro del horario: lo llama `avisos.enviar_avisos`).
    Cómo terminó cada uno (`enviado`, `omitido`, `reintento`, `fallido`)."""
    cur = m.cur
    cur.execute("""select * from scheduled_notice
                    where al_grupo and estado = 'guardado' and programado_para <= %s
                      and (proximo_intento_en is null or proximo_intento_en <= %s)
                    order by programado_para, dedupe_key
                    for update skip locked""", (m.ahora, m.ahora))
    resumen: Counter[str] = Counter()
    for aviso in cur.fetchall():
        resumen[_uno(m, aviso, ia)] += 1
    return resumen


def _uno(m: Momento, aviso: dict[str, Any], ia) -> str:
    cur, aviso_id = m.cur, str(aviso["id"])
    if _dia_de_la_clave(aviso) != m.hoy:
        omitir(cur, aviso_id, YA_PASO_SU_MOMENTO, m.ahora)
        return "omitido"
    cur.execute("select grupo_chat_id from workspace where id = %s", (m.workspace_id,))
    fila = cur.fetchone()
    if fila is None or fila["grupo_chat_id"] is None:
        omitir(cur, aviso_id, SIN_GRUPO, m.ahora)
        return "omitido"
    hechos = armar(m, _desde(m))
    if hechos is None:
        omitir(cur, aviso_id, NADA_PARA_INFORMAR, m.ahora)
        return "omitido"
    pedido = {"hoy": m.hoy.isoformat(), "persona": None, "mensaje": None, "hechos": [hechos],
              "pregunta": None, "ultimos_turnos": []}
    try:
        texto = no_vacio(ia.redactar(pedido))
    except Exception as falla:     # la IA es un servicio externo: cualquier falla es no redactar
        return _si_no_lo_redacta(m, aviso, falla)
    clave_salida = f"motor:aviso:{aviso_id}"
    try:
        enqueue_outbox(cur, workspace_id=m.workspace_id, chat_id=fila["grupo_chat_id"],
                       text=texto, dedupe_key=clave_salida, recipient_membership_id=None,
                       message_type="informativo", scheduled_for=m.ahora,
                       expires_at=_fin_del_dia(m), allow_split=True)
    except PayloadValidationError as falla:
        return _si_no_lo_redacta(m, aviso, falla)
    cur.execute("select id from message_outbox where workspace_id = %s and dedupe_key = %s",
                (m.workspace_id, clave_salida))
    outbox_id = str(cur.fetchone()["id"])
    cur.execute("""update scheduled_notice
                      set estado = 'enviado', outbox_id = %s, resuelto_en = %s, hechos = %s,
                          intentos = intentos + 1, proximo_intento_en = null
                    where id = %s""",
                (outbox_id, m.ahora, json.dumps(hechos, ensure_ascii=False, default=str),
                 aviso_id))
    auditar(cur, accion="enviar_aviso", workspace_id=m.workspace_id,
            sujeto_tipo="scheduled_notice", sujeto_id=aviso_id,
            detalle={"aviso_id": aviso_id, "tipo": INFORME_AL_GRUPO, "al_grupo": True,
                     "outbox_id": outbox_id, "at": m.ahora.isoformat()})
    return "enviado"


def _fin_del_dia(m: Momento) -> datetime:
    """Hasta cuándo puede salir la fila del outbox: el cierre del horario de ese día (mecánica
    §12: un mensaje de cadencia cuya ventana pasó no se manda tarde)."""
    return datetime.combine(m.hoy, m.cal.hora_fin, tzinfo=m.cal.zona)


def _si_no_lo_redacta(m: Momento, aviso: dict[str, Any], falla: Exception) -> str:
    """Decisión 8, caso 2, como los demás avisos: se reintenta a los 1, 2, 4 y 8 minutos, con un
    rastro por intento; al quinto fallo queda `fallido` con sus hechos y un incidente para la
    administración. Al grupo nunca le llega un texto armado a mano."""
    cur, aviso_id = m.cur, str(aviso["id"])
    intentos = aviso["intentos"] + 1
    if intentos < INTENTOS:
        proximo = m.ahora + ESPERAS_TRAS_UN_FALLO[intentos - 1]
        cur.execute("""update scheduled_notice set intentos = %s, proximo_intento_en = %s
                        where id = %s""", (intentos, proximo, aviso_id))
        registrar_incidente(
            cur, m.workspace_id,
            f"La IA no redactó el informe al grupo del espacio en el intento {intentos}: se "
            f"reintenta a las {proximo.astimezone(m.cal.zona).strftime('%H:%M')}, con sus "
            f"hechos guardados.",
            severidad="baja", referencia_cruda=f"{type(falla).__name__}: {falla}",
            etapa=ETAPA_AVISO_REINTENTO, avisar_admin=False,
            sin_avisar_porque="un intento que se reintenta queda sólo como rastro; el quinto "
                              "fallo sí la avisa.")
        return "reintento"
    cur.execute("""update scheduled_notice
                      set estado = 'fallido', intentos = %s, resuelto_en = %s,
                          proximo_intento_en = null
                    where id = %s""", (intentos, m.ahora, aviso_id))
    registrar_incidente(
        cur, m.workspace_id,
        f"La IA no redactó el informe al grupo del espacio tras {INTENTOS} intentos, a los 1, 2, "
        f"4 y 8 minutos: quedó guardado con sus hechos y no salió.",
        referencia_cruda=f"{type(falla).__name__}: {falla}", etapa=ETAPA_AVISO_GUARDADO)
    return "fallido"


# --- Lo que dice ------------------------------------------------------------------------------

def _desde(m: Momento) -> datetime:
    """Desde cuándo cuentan las terminadas: el informe anterior que salió o, si no hubo, el
    lunes de esta semana."""
    m.cur.execute("""select max(resuelto_en) as desde from scheduled_notice
                      where al_grupo and tipo = %s and estado = 'enviado'""",
                  (INFORME_AL_GRUPO,))
    fila = m.cur.fetchone()
    if fila and fila["desde"] is not None:
        return fila["desde"]
    lunes = m.hoy - timedelta(days=m.hoy.weekday())
    return datetime.combine(lunes, datetime.min.time(), tzinfo=m.cal.zona)


def armar(m: Momento, desde: datetime) -> dict[str, Any] | None:
    """Los hechos del informe, o `None` si no hay nada que informar. Cada lista, por el día en que
    vence la tarea y su título; las vacías no van. Cuándo quedó terminada una tarea es su última
    actualización: la proyección de su evento de estado la pone (`task.actualizado_en`), y una
    terminada ya no cambia."""
    cur = m.cur
    cur.execute("""select t.id, t.titulo, t.estado::text estado, t.fecha_objetivo,
                          i.nombre la_tiene
                     from task t join integrante i on i.membership_id = t.responsable_membership_id
                    where i.activo
                      and (t.estado::text = any(%s)
                           or (t.estado = 'terminada' and t.actualizado_en > %s))
                    order by t.fecha_objetivo nulls last, t.titulo, t.id""",
                (list(ABIERTAS), desde))
    informe: dict[str, list[dict[str, Any]]] = {
        "terminadas": [], "atrasadas": [], "trabadas": [], "entregadas": [], "siguen": []}
    for t in cur.fetchall():
        renglon = {"tarea": t["titulo"], "la_tiene": t["la_tiene"]}
        if t["estado"] == "terminada":
            informe["terminadas"].append(renglon)
            continue
        trabada = _trabada(m, t)
        if trabada is not None:
            informe["trabadas"].append({**renglon, **trabada})
        elif t["estado"] == "en_revision":
            informe["entregadas"].append(renglon)
        elif t["estado"] in SIGUEN:
            _sin_entregar(m, t, renglon, informe)
    hechos = {k: v for k, v in informe.items() if v}
    if not hechos:
        return None
    return {"aviso": INFORME_AL_GRUPO, "necesita_respuesta": False, **hechos}


def _sin_entregar(m: Momento, t: dict[str, Any], renglon: dict[str, Any],
                  informe: dict[str, list[dict[str, Any]]]) -> None:
    """Una tarea comprometida sin entregar: sigue su curso, es un atraso ya hablado en privado o,
    si está atrasada y la persona todavía no lo habló con Leda, no figura (constitución §8)."""
    if t["fecha_objetivo"] is None:
        informe["siguen"].append({**renglon, "estado": t["estado"]})
        return
    vence = m.fecha(t["fecha_objetivo"])
    prevision = prevision_vigente(m.cur, t["id"])
    dio_otro_dia = prevision is not None and prevision["fecha_prevista"] > vence
    if dio_otro_dia:
        atraso = {**renglon, "vence": vence.isoformat(),
                  "prevision": prevision["fecha_prevista"].isoformat()}
        if prevision["motivo"]:
            atraso["motivo"] = prevision["motivo"]
        informe["atrasadas"].append(atraso)
    elif m.hoy > vence and _quedo_asentado_el_atraso(m, t["id"], vence):
        informe["atrasadas"].append({**renglon, "vence": vence.isoformat()})
    elif m.hoy <= vence:
        informe["siguen"].append({**renglon, "estado": t["estado"], "vence": vence.isoformat()})


def _quedo_asentado_el_atraso(m: Momento, task_id, vence: date) -> bool:
    """Si quedó asentado que la tarea está atrasada: salió el escalamiento por falta de respuesta
    de ese vencimiento (decisiones 21 y 35)."""
    m.cur.execute("""select 1 from scheduled_notice
                      where task_id = %s and tipo = 'escalamiento' and estado = 'enviado'
                        and hechos ->> 'vence' = %s limit 1""", (str(task_id), vence.isoformat()))
    return m.cur.fetchone() is not None


def _trabada(m: Momento, t: dict[str, Any]) -> dict[str, Any] | None:
    """Lo que traba la tarea, si tiene bloqueos abiertos: las causas como las dijo la persona,
    desde cuándo, cuántos días hábiles lleva y el día que dio quien la destraba, si dio uno y no
    dijo después que ya está."""
    cur = m.cur
    cur.execute("""select id, causa, abierto_en from blocker
                    where task_id = %s and resuelto_en is null
                    order by abierto_en, id""", (str(t["id"]),))
    bloqueos = cur.fetchall()
    if not bloqueos:
        return None
    desde = bloqueos[0]["abierto_en"]
    trabada: dict[str, Any] = {"causas": [b["causa"] for b in bloqueos],
                               "trabada_desde": m.fecha(desde).isoformat(),
                               "dias_habiles_trabada": m.cal.habiles_entre(desde, m.ahora)}
    cur.execute("""select d.para_cuando from dicho_de_quien_destraba d
                     join blocker_unblocker u on u.id = d.blocker_unblocker_id
                    where u.blocker_id = any(%s::uuid[])
                      and (d.para_cuando is not null or d.ya_esta)
                    order by d.at desc limit 1""", ([str(b["id"]) for b in bloqueos],))
    dicho = cur.fetchone()
    if dicho is not None and dicho["para_cuando"] is not None:
        trabada["para_cuando"] = dicho["para_cuando"].isoformat()
    return trabada
