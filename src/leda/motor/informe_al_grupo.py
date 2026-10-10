"""El informe al grupo (C-6; decisión 25 del usuario, 2026-10-09, opción A; decisiones 8, 35, 45,
49, 54 y 55; ADR 0021, reglas 1 a 3; constitución §4, §8 y §13; mecánica §10 y §12; conversación
41).

**Qué es.** El día de una cadencia al grupo del espacio (`cadence_job.audiencia = 'grupo'`, como
`resumen_grupal` e `informe_semanal` de CoreWork), Leda le manda al grupo del equipo lo que pasó con
las tareas, para que todos estén al tanto y puedan ayudar ("lucas lee eso y se entera que marcos
estaba frenado porque le falta el cable y el tiene un cable extra"). Informa avances y problemas, no
juzga (decisión 8). Cada renglón lleva el nombre de quien tiene la tarea (`la_tiene`, decisión 25):

- las **terminadas** desde el informe anterior (o, el primero, desde el lunes de esa semana), con
  quién la hizo: una sola vez cada una (la buena noticia, decisión 55);
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
- las que **no se sabe cómo vienen** (`sin_saber_como_vienen`): Leda le preguntó a quien la tiene
  otro día y no contestó; no está "bien" ni "atrasada" (decisión 55; constitución §4), y va sin el
  día en que vence;
- las que **siguen**, con su estado y el día en que vencen.

Lo que sigue igual se repite en cada informe (decisión 54: "no es exponer, es informar"); cada
cuánto sale se ajusta en la plataforma.

**Sale siempre** a su cadencia (decisión 55), también como señal de que Leda funciona. Sin nada
malo (ningún atraso, ninguna trabada, nada que Leda no sepa ni un atraso que la persona todavía
no habló), dice que está todo en orden (`todo_en_orden`), sólo cuando los hechos lo prueban. Si
la semana fue buena por reglas fijas del código (`_semana_buena`), lo dice (`semana_buena`), y la
IA lo reconoce con el tono de Leda, sin frases armadas. Nunca hay un conteo ni una comparación por
persona ("es un equipo, no una competencia"). Sin nada que contar y sin poder decir que está todo
en orden, lo dice así (`sin_novedades_para_el_grupo`). `NADA_PARA_INFORMAR` queda sólo como el
motivo de los informes omitidos antes de la decisión 55. La tarea de un integrante inactivo no
figura.

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
uno). Si no lo redacta, si el texto no se puede mandar o si armarlo se cae, se reintenta a los 1,
2, 4 y 8 minutos (`avisos.ESPERAS_TRAS_UN_FALLO`), con sus hechos guardados en el aviso; al quinto
fallo queda `fallido` y un incidente para la administración. Cada informe corre en su savepoint:
si se cae, lo que sale a cada persona en la misma pasada sale igual. El reintento a mano
(`avisos.enviar_avisos(solo=…, forzar=True)`) también lo alcanza. Nunca sale un texto armado a
mano.

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
from datetime import date, datetime, time, timedelta
from typing import Any

from ..incidentes import registrar_incidente
from ..salida import PayloadValidationError, enqueue_outbox
from . import cambios_de_estado
from .ancla import prevision_vigente
from .asentado import AL_GRUPO, hay_informe_al_grupo
from .auditoria import auditar
from .avisos import (ESPERA_DE_ESTADO, ESPERAS_TRAS_UN_FALLO, ETAPA_AVISO_GUARDADO,
                     ETAPA_AVISO_REINTENTO, INTENTOS, Momento, guardar, omitir)
from .cadencias import YA_PASO_SU_MOMENTO, atender, leer_ritmo, sin_contestar_en_la_lista
from .registro import no_vacio
from .tiempo import sale

INFORME_AL_GRUPO = "informe_al_grupo"
# Por qué un informe al grupo no salió: el espacio ya no tiene grupo, o (antes de la decisión 55)
# no había nada que informar.
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
# Los pasos de la escalera que preguntan por una tarea o avisan que no contestó: uno que sale con
# la tarea ya vencida es un atraso que Leda tuvo que perseguir (`_semana_buena`).
PASOS_DE_LA_ESCALERA = ("pedido_de_estado", "repregunta_de_estado", "escalamiento")


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

def enviar(m: Momento, ia, *, solo: str | None = None, forzar: bool = False) -> Counter:
    """Los informes al grupo cuya hora llegó (dentro del horario: lo llama `avisos.enviar_avisos`).
    `solo` acota a un aviso y `forzar` no espera su próximo intento (el reintento a mano). Cada
    uno en su propio savepoint: si uno se cae, ni los avisos a cada persona de la misma pasada ni
    el otro informe se caen con él; se reintenta como uno que la IA no redactó, con su incidente.
    Cómo terminó cada uno (`enviado`, `omitido`, `reintento`, `fallido`)."""
    cur = m.cur
    cur.execute("""select * from scheduled_notice
                    where al_grupo and estado = 'guardado' and programado_para <= %s
                      and (%s or proximo_intento_en is null or proximo_intento_en <= %s)
                      and (%s::uuid is null or id = %s::uuid)
                    order by programado_para, dedupe_key
                    for update skip locked""", (m.ahora, forzar, m.ahora, solo, solo))
    resumen: Counter[str] = Counter()
    for aviso in cur.fetchall():
        try:
            with cur.connection.transaction():
                resultado = _uno(m, aviso, ia)
        except Exception as falla:  # noqa: BLE001 -- un informe que se cae no frena lo demás
            resultado = _si_no_sale(m, aviso, falla, se_cayo=True)
        resumen[resultado] += 1
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
    hechos, lleva = armar(m, _desde(m))
    pedido = {"hoy": m.hoy.isoformat(), "persona": None, "mensaje": None, "hechos": [hechos],
              "pregunta": None, "ultimos_turnos": []}
    try:
        texto = no_vacio(ia.redactar(pedido))
    except Exception as falla:     # la IA es un servicio externo: cualquier falla es no redactar
        return _si_no_sale(m, aviso, falla, hechos)
    clave_salida = f"motor:aviso:{aviso_id}"
    try:
        enqueue_outbox(cur, workspace_id=m.workspace_id, chat_id=fila["grupo_chat_id"],
                       text=texto, dedupe_key=clave_salida, recipient_membership_id=None,
                       message_type="informativo", scheduled_for=m.ahora,
                       expires_at=_fin_del_dia(m), allow_split=True)
    except PayloadValidationError as falla:
        return _si_no_sale(m, aviso, falla, hechos)
    cur.execute("select id from message_outbox where workspace_id = %s and dedupe_key = %s",
                (m.workspace_id, clave_salida))
    outbox_id = str(cur.fetchone()["id"])
    cur.execute("""update scheduled_notice
                      set estado = 'enviado', outbox_id = %s, resuelto_en = %s, hechos = %s,
                          tareas_de_la_lista = %s, intentos = intentos + 1,
                          proximo_intento_en = null
                    where id = %s""",
                (outbox_id, m.ahora, _json(hechos), _json(lleva), aviso_id))
    auditar(cur, accion="enviar_aviso", workspace_id=m.workspace_id,
            sujeto_tipo="scheduled_notice", sujeto_id=aviso_id,
            detalle={"aviso_id": aviso_id, "tipo": INFORME_AL_GRUPO, "al_grupo": True,
                     "outbox_id": outbox_id, "at": m.ahora.isoformat()})
    return "enviado"


def _json(hechos: dict[str, Any]) -> str:
    return json.dumps(hechos, ensure_ascii=False, default=str)


def _fin_del_dia(m: Momento) -> datetime:
    """Hasta cuándo puede salir la fila del outbox: el cierre del horario de ese día (mecánica
    §12: un mensaje de cadencia cuya ventana pasó no se manda tarde)."""
    return datetime.combine(m.hoy, m.cal.hora_fin, tzinfo=m.cal.zona)


def _si_no_sale(m: Momento, aviso: dict[str, Any], falla: Exception,
                hechos: dict[str, Any] | None = None, *, se_cayo: bool = False) -> str:
    """Decisión 8, caso 2, como los demás avisos: si la IA no lo redacta, si el texto no se puede
    mandar o si armarlo se cayó, se reintenta a los 1, 2, 4 y 8 minutos, con un rastro por
    intento; al quinto fallo queda `fallido` y un incidente para la administración. Los hechos de
    ese momento quedan guardados en el aviso (lo que iba a decir), si se llegaron a armar. Al
    grupo nunca le llega un texto armado a mano."""
    cur, aviso_id = m.cur, str(aviso["id"])
    intentos = aviso["intentos"] + 1
    que = ("No se pudo armar el informe al grupo del espacio (se cayó al armarlo o al guardarlo)"
           if se_cayo else "La IA no redactó el informe al grupo del espacio")
    from .ciclo import ETAPA_CICLO      # el ciclo importa la escalera, que importa este módulo

    etapa_reintento, etapa_final = ((ETAPA_CICLO, ETAPA_CICLO) if se_cayo
                                    else (ETAPA_AVISO_REINTENTO, ETAPA_AVISO_GUARDADO))
    if hechos is not None:
        cur.execute("update scheduled_notice set hechos = %s where id = %s",
                    (_json(hechos), aviso_id))
    if intentos < INTENTOS:
        proximo = m.ahora + ESPERAS_TRAS_UN_FALLO[intentos - 1]
        cur.execute("""update scheduled_notice set intentos = %s, proximo_intento_en = %s
                        where id = %s""", (intentos, proximo, aviso_id))
        registrar_incidente(
            cur, m.workspace_id,
            f"{que} en el intento {intentos}: se reintenta a las "
            f"{proximo.astimezone(m.cal.zona).strftime('%H:%M')}.",
            severidad="baja", referencia_cruda=f"{type(falla).__name__}: {falla}",
            etapa=etapa_reintento, avisar_admin=False,
            sin_avisar_porque="un intento que se reintenta queda sólo como rastro; el quinto "
                              "fallo sí la avisa.")
        return "reintento"
    cur.execute("""update scheduled_notice
                      set estado = 'fallido', intentos = %s, resuelto_en = %s,
                          proximo_intento_en = null
                    where id = %s""", (intentos, m.ahora, aviso_id))
    registrar_incidente(
        cur, m.workspace_id,
        f"{que} tras {INTENTOS} intentos, a los 1, 2, 4 y 8 minutos: quedó guardado"
        f"{' con sus hechos' if hechos is not None else ''} y no salió.",
        referencia_cruda=f"{type(falla).__name__}: {falla}", etapa=etapa_final)
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


def armar(m: Momento, desde: datetime) -> tuple[dict[str, Any], dict[str, Any]]:
    """Los hechos del informe: cada lista, por el día en que vence la tarea y su título; las
    vacías no van. Siempre hay informe (decisión 55): sin nada malo, `todo_en_orden`; si además la
    semana fue buena por las reglas fijas de `_semana_buena`, `semana_buena`; sin nada que se
    pueda contar y sin poder decir que está todo en orden (un atraso que la persona todavía no
    habló), `sin_novedades_para_el_grupo`. Devuelve también las tareas terminadas que lleva, que
    se guardan al salir fuera de los hechos (`scheduled_notice.tareas_de_la_lista`).

    Una terminada figura una sola vez: la que quedó terminada después del informe anterior (su
    última actualización, que pone la proyección del evento que la terminó) y que ningún informe
    anterior llevó. Así, una terminada que se toque después no vuelve a figurar (revisión
    `review-f4d7f683f853df7c`); `leda_app` no lee los eventos de estado (`db/esquema.sql`)."""
    cur = m.cur
    cur.execute("""select t.id, t.titulo, t.estado::text estado, t.fecha_objetivo,
                          t.responsable_membership_id, i.nombre la_tiene
                     from task t join integrante i on i.membership_id = t.responsable_membership_id
                    where i.activo
                      and (t.estado::text = any(%s)
                           or (t.estado = 'terminada' and t.actualizado_en > %s
                               and not exists (
                                   select 1 from scheduled_notice a
                                    where a.al_grupo and a.tipo = %s and a.estado = 'enviado'
                                      and a.tareas_de_la_lista -> 'terminadas' ? t.id::text)))
                    order by t.fecha_objetivo nulls last, t.titulo, t.id""",
                (list(ABIERTAS), desde, INFORME_AL_GRUPO))
    informe: dict[str, list[dict[str, Any]]] = {
        "terminadas": [], "atrasadas": [], "trabadas": [], "entregadas": [], SIN_SABER: [],
        "siguen": []}
    sin_hablar = 0
    terminadas: list[str] = []
    for t in cur.fetchall():
        renglon = {"tarea": t["titulo"], "la_tiene": t["la_tiene"]}
        if t["estado"] == "terminada":
            informe["terminadas"].append(renglon)
            terminadas.append(str(t["id"]))
            continue
        trabada = _trabada(m, t)
        if trabada is not None:
            informe["trabadas"].append({**renglon, **trabada})
        elif t["estado"] == "en_revision":
            informe["entregadas"].append(renglon)
        elif t["estado"] in SIGUEN:
            sin_hablar += _sin_entregar(m, t, renglon, informe)
    hechos: dict[str, Any] = {k: v for k, v in informe.items() if v}
    en_orden = not (informe["atrasadas"] or informe["trabadas"] or informe[SIN_SABER]
                    or sin_hablar)
    if en_orden:
        hechos[TODO_EN_ORDEN] = True
    elif not hechos:
        hechos[SIN_NOVEDADES] = True
    # La semana buena es un reconocimiento cuando está todo en orden: con un atraso que sigue de
    # antes, algo que no se sabe o algo trabado, no (decisión 55; revisión
    # `review-f4d7f683f853df7c`, `informe_al_grupo.py:334-335`).
    if en_orden and _semana_buena(m, desde, bool(informe["terminadas"])):
        hechos[SEMANA_BUENA] = True
    return ({"aviso": INFORME_AL_GRUPO, "necesita_respuesta": False, **hechos},
            {"terminadas": terminadas})


def _sin_entregar(m: Momento, t: dict[str, Any], renglon: dict[str, Any],
                  informe: dict[str, list[dict[str, Any]]]) -> int:
    """Una tarea comprometida sin entregar: un atraso ya hablado en privado, algo que Leda no sabe
    (le preguntó otro día y la persona no contestó: ni bien ni atrasada, decisión 55), o que sigue
    su curso. Si está atrasada y la persona todavía no lo habló con Leda, no figura (constitución
    §8): devuelve 1, para que el informe no diga que está todo en orden."""
    vence = m.fecha(t["fecha_objetivo"]) if t["fecha_objetivo"] is not None else None
    if vence is not None:
        prevision = prevision_vigente(m.cur, t["id"])
        if prevision is not None and prevision["fecha_prevista"] > vence:
            atraso = {**renglon, "vence": vence.isoformat(),
                      "prevision": prevision["fecha_prevista"].isoformat()}
            if prevision["motivo"]:
                atraso["motivo"] = prevision["motivo"]
            informe["atrasadas"].append(atraso)
            return 0
        if m.hoy > vence and _quedo_asentado_el_atraso(m, t["id"], vence):
            informe["atrasadas"].append({**renglon, "vence": vence.isoformat()})
            return 0
    if _no_contesto(m, t):
        informe[SIN_SABER].append(renglon)
        return 0
    if vence is not None and m.hoy > vence:
        return 1
    informe["siguen"].append({**renglon, "estado": t["estado"],
                              **({"vence": vence.isoformat()} if vence is not None else {})})
    return 0


def _no_contesto(m: Momento, t: dict[str, Any]) -> bool:
    """Si Leda le preguntó a la persona cómo viene la tarea un día anterior y no contestó desde
    entonces: su espera del estado sigue abierta desde antes de hoy, o la lista se la pregunta sin
    respuesta desde antes de hoy."""
    persona = str(t["responsable_membership_id"])
    inicio_de_hoy = datetime.combine(m.hoy, time.min, tzinfo=m.cal.zona)
    m.cur.execute("""select 1 from pending_reply
                      where task_id = %s and membership_id = %s and tipo = %s
                        and satisfecho_en is null and preguntado_en < %s limit 1""",
                  (str(t["id"]), persona, ESPERA_DE_ESTADO, inicio_de_hoy))
    if m.cur.fetchone() is not None:
        return True
    return sin_contestar_en_la_lista(m.cur, persona, t["id"], m.hoy)


def _semana_buena(m: Momento, desde: datetime, hubo_terminadas: bool) -> bool:
    """Si la semana (desde el informe anterior) fue buena, por reglas fijas (decisión 55); la IA
    sólo lo cuenta. Sin bloqueos abiertos (lo mira quien llama), y además:

    - **ningún atraso nuevo:** nadie dio en el período un día posterior al vencimiento de una
      tarea; toda tarea que vencía en el período (antes de hoy) está entregada; y por ninguna de
      ellas Leda tuvo que preguntar después de su vencimiento (un paso de su escalera que salió
      con la tarea ya vencida);
    - **algo hecho:** se terminó o se entregó alguna tarea en el período. Sin eso, todo en orden
      no es una semana buena (sin exagerar).

    Es un dato del equipo, nunca de una persona: no cuenta ni compara a nadie."""
    cur, zona = m.cur, str(m.cal.zona)
    cur.execute("""select 1 from task_forecast f join task t on t.id = f.task_id
                     join integrante i on i.membership_id = t.responsable_membership_id
                    where i.activo and t.estado <> 'cancelada' and f.at > %s
                      and t.fecha_objetivo is not null
                      and f.fecha_prevista > (t.fecha_objetivo at time zone %s)::date
                    limit 1""", (desde, zona))
    if cur.fetchone() is not None:
        return False
    cur.execute("""select t.id, t.fecha_objetivo, t.estado::text estado
                     from task t join integrante i on i.membership_id = t.responsable_membership_id
                    where i.activo and t.estado <> 'cancelada'
                      and (t.fecha_objetivo at time zone %s)::date >= %s
                      and (t.fecha_objetivo at time zone %s)::date < %s""",
                (zona, m.fecha(desde), zona, m.hoy))
    vencian = cur.fetchall()
    if any(t["estado"] not in ("en_revision", "terminada") for t in vencian):
        return False
    for t in vencian:
        cur.execute("""select resuelto_en from scheduled_notice
                        where task_id = %s and estado = 'enviado' and tipo = any(%s)
                          and resuelto_en > %s""",
                    (str(t["id"]), list(PASOS_DE_LA_ESCALERA), desde))
        vence = m.fecha(t["fecha_objetivo"])
        if any(m.fecha(a["resuelto_en"]) > vence for a in cur.fetchall()):
            return False
    if hubo_terminadas:
        return True
    # Por el momento, no por el día: lo entregado el mismo día que el informe anterior, después
    # de él, es de este período; lo de antes ya contó en aquél (revisión
    # `review-f4d7f683f853df7c`, `informe_al_grupo.py:424`).
    return any(_entregada_en(m, t) > desde for t in _entregadas(m))


def _entregadas(m: Momento) -> list[dict[str, Any]]:
    m.cur.execute("""select t.id, t.responsable_membership_id, t.actualizado_en
                       from task t
                       join integrante i on i.membership_id = t.responsable_membership_id
                      where i.activo and t.estado = 'en_revision'""")
    return m.cur.fetchall()


def _entregada_en(m: Momento, t: dict[str, Any]) -> datetime:
    """El momento en que la tarea quedó entregada: el del turno de quien la entregó, que anotó el
    motor (`cambios_de_estado`, con su reloj) o, si la entregó otro camino, su última
    actualización (la proyección del evento que la puso en revisión)."""
    momento = cambios_de_estado.momento_desde(m.cur, t["id"], t["responsable_membership_id"],
                                              "en_revision")
    return momento if isinstance(momento, datetime) else t["actualizado_en"]


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
