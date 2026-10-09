"""Los bloqueos encadenados y los avisos hacia abajo (C-5, porción 4).

Decisión 6 del usuario (`odd/tasks/fase-c.md`, 2026-10-08): los bloqueos se enlazan solos (Marcos
← Juan ← Pedro) y Leda avisa hacia abajo al destrabar; quien está más lejos se entera de todo
avance del medio con avisos informativos que no piden respuesta ("llegó el repuesto, Juan da
fecha, Juan terminó"). ADR 0017, decisión 3a; mecánica §4 (dependencias) y §8 (bloqueos);
conversación 35.

**El enlace no se guarda: se deriva de lo que ya está** (`aguas_abajo`). Un bloqueo abierto de
Marcos espera la tarea de Juan cuando lo último que se dijo de él es que lo destraba Juan, y esa
tarea de Juan es lo que le falta:

- **la estructura lo dice:** la tarea de Marcos depende de la de Juan (`dependency`, que carga la
  plataforma: por la web, la estructura); o
- **Juan lo dijo:** al contestar por lo de Marcos, dijo que está trabado con una tarea suya
  (`dicho_de_quien_destraba.espera_su_bloqueo_id`, migración 0044; la jugada
  `decir_cuando_destraba` con `su_tarea_trabada`).

Sin una de las dos no hay enlace: nunca por adivinar. La cadena sigue hacia abajo (quien espera a
Marcos espera también lo de Juan) y nunca da vueltas.

**Cada avance del medio** en la tarea de Juan le llega a cada persona trabada que la espera, más
abajo, salvo a quien lo hizo (`avisar_hacia_abajo`, el aviso `novedad_de_lo_que_espera`): que se
trabó (con qué y quién lo destraba), lo que dice quien la destraba, que pudo seguir, un día nuevo
para terminarla, que la entregó y que quedó terminada. Son información: no piden respuesta. Los
causa el acto de otra persona: son de coordinación (mecánica §10, precisión del 2026-09-30: fuera
del tope diario) y, cuando los causa lo que alguien dijo, salen terminado el margen para corregir
(`margen.py`); una aprobación no se corrige por chat y sale enseguida (decisión 19). Salen dentro
del horario y sin interrumpir una conversación (decisión 13), como todo aviso. Al salir se vuelve
a mirar que la tarea siga esperando eso y que el avance siga valiendo (`vigencia`).

**Quien se traba con lo que destraba a otra persona ya contestó** "para cuándo": su pregunta por
la tarea de la otra persona y su espera se cierran (`se_trabo`), y Leda sigue con quien lo
destraba a él, como con cualquier bloqueo. Nunca da por destrabada una tarea porque se destrabó
la que la frenaba: eso lo dice la persona trabada (`destrabar`).
"""

from __future__ import annotations

import time
from typing import Any

from . import preguntas
from .avisos import (DIJO_ALGO_MAS_NUEVO, NOVEDAD_DE_LO_QUE_ESPERA, PREGUNTA_A_QUIEN_DESTRABA,
                     YA_NO_ESTA_ENTREGADA, YA_SE_DESTRABO, Momento, guardar, integrante,
                     leer_tarea, omitir, ultimo_quien_destraba)
from .fichas import AVISO, LLEGA, NO_LE_VA_A_LLEGAR, Contexto, nombrar_efecto
from .margen import sale_con_margen
from .tiempo import sale

# Hasta dónde se sigue la cadena hacia abajo: alcanza para cualquier equipo y corta una que, por
# un error de los datos, fuera interminable.
PROFUNDIDAD = 10

# Por qué un aviso de un avance ya no sale.
YA_NO_ESPERA_ESA_TAREA = "ya_no_espera_esa_tarea"
NO_SE_ENTERO_QUE_SE_TRABO = "no_se_entero_que_se_trabo"
HAY_UNA_PREVISION_MAS_NUEVA = "hay_una_prevision_mas_nueva"
# Quien destraba nombró una tarea suya que no está trabada.
SU_TAREA_NO_ESTA_TRABADA = "su_tarea_no_esta_trabada"

# La letra de cada avance en la clave del aviso (`motor:<tipo>:<tarea que espera>:<letra><id>`):
# el bloqueo que se abrió o se cerró, lo dicho, el día nuevo, la entrega y la aprobación.
SE_TRABO, SE_DESTRABO, DIJO, OTRO_DIA, ENTREGO, TERMINADA = "y", "r", "d", "p", "e", "t"


# --- El enlace --------------------------------------------------------------------------------

def _lo_esperan(cur, task_id: str) -> list[dict[str, Any]]:
    """Los bloqueos abiertos de otras personas que esperan directamente esta tarea (ver el
    módulo), con su tarea, su causa y quién la tiene."""
    cur.execute(
        """select b.id as bloqueo_id, b.causa, t.id as task_id, t.titulo,
                  t.responsable_membership_id, i.nombre as responsable
             from task o
             join blocker b on b.resuelto_en is null and b.task_id <> o.id
             join task t on t.id = b.task_id
             join integrante i on i.membership_id = t.responsable_membership_id
             join lateral (select u.destraba_membership_id from blocker_unblocker u
                            where u.blocker_id = b.id
                            order by u.at desc, u.id desc limit 1) u on true
            where o.id = %(t)s
              and t.estado not in ('terminada', 'cancelada')
              and u.destraba_membership_id = o.responsable_membership_id
              and t.responsable_membership_id <> o.responsable_membership_id
              and (exists (select 1 from dependency d
                            where d.origen_task_id = o.id and d.destino_task_id = t.id)
                   or exists (select 1 from dicho_de_quien_destraba d
                                join blocker_unblocker x on x.id = d.blocker_unblocker_id
                                join blocker y on y.id = d.espera_su_bloqueo_id
                               where x.blocker_id = b.id and y.task_id = o.id
                                 and d.dicho_por_membership_id = o.responsable_membership_id))
            order by t.fecha_objetivo nulls last, t.titulo, b.id""", {"t": str(task_id)})
    return cur.fetchall()


def aguas_abajo(cur, task_id: str) -> list[dict[str, Any]]:
    """Las tareas trabadas que esperan esta, directa o indirectamente, cada una una vez: su
    bloqueo, su tarea, quién la tiene y lo que espera, de la más cercana a esta
    (`esperando_a`: quién tiene cada tarea del medio y cuál, terminando en ésta)."""
    cur.execute("""select t.titulo, i.nombre from task t
                     join integrante i on i.membership_id = t.responsable_membership_id
                    where t.id = %s""", (str(task_id),))
    origen = cur.fetchone()
    if origen is None:
        return []
    vistas = {str(task_id)}
    resultado: list[dict[str, Any]] = []
    frente = [(str(task_id), [{"de": origen["nombre"], "tarea": origen["titulo"]}])]
    while frente:
        tarea, camino = frente.pop(0)
        for f in _lo_esperan(cur, tarea):
            espera = str(f["task_id"])
            if espera in vistas:
                continue
            vistas.add(espera)
            resultado.append({**f, "esperando_a": camino})
            if len(camino) < PROFUNDIDAD:
                frente.append((espera, [{"de": f["responsable"], "tarea": f["titulo"]}]
                               + camino))
    return resultado


def quien_lo_destraba(cur, bloqueo_id) -> str | None:
    """Quién destraba un bloqueo, según lo último que se dijo: su nombre, o como lo nombró la
    persona si es de afuera; `None` si no se dijo o no se sabe."""
    ultimo = ultimo_quien_destraba(cur, bloqueo_id)
    if ultimo is None:
        return None
    if ultimo["destraba_membership_id"] is not None:
        persona = integrante(cur, ultimo["destraba_membership_id"])
        return persona["nombre"] if persona else None
    return ultimo["destraba_externo"]


# --- Los avisos hacia abajo -------------------------------------------------------------------

def avisar_hacia_abajo(ctx: Contexto, task_id: str, novedad: dict[str, Any], clave: str, *,
                       con_margen: bool = True) -> dict[str, Any]:
    """Un avance en esta tarea le llega, como información, a cada persona trabada que la
    espera más abajo, salvo a quien lo hizo (ver el módulo). `clave`: lo que lo identifica (su
    letra y su id), para no guardarlo dos veces. Los hechos para quien escribe: a quién y
    cuándo se entera (`avisos_a_quienes_esperan`), o nada si nadie espera."""
    cur = ctx.cur
    abajo = [f for f in aguas_abajo(cur, task_id)
             if str(f["responsable_membership_id"]) != ctx.quien.membership_id]
    if not abajo:
        return {}
    llega = (sale_con_margen(cur, ctx.calendario, ctx.quien.workspace_id, ctx.ahora)
             if con_margen else sale(ctx.calendario, ctx.ahora))
    avisos: list[dict[str, Any]] = []
    for f in abajo:
        persona = integrante(cur, f["responsable_membership_id"])
        if persona is None or not persona["activo"] or persona["telegram_user_id"] is None:
            # Nunca se promete un mensaje que no va a salir (constitución §7).
            avisos.append({"aviso_a_quien_espera": {
                "a": f["responsable"], "tarea": f["titulo"], LLEGA: NO_LE_VA_A_LLEGAR,
                "motivo": ("destinatario_sin_telegram" if persona is not None
                           and persona["activo"] else "destinatario_inactivo")}})
            continue
        hechos = {"aviso": NOVEDAD_DE_LO_QUE_ESPERA, "necesita_respuesta": False,
                  "tarea": f["titulo"], "causa": f["causa"], "esperando_a": f["esperando_a"],
                  "novedad": {**f["esperando_a"][-1], **novedad}}
        aviso_id, _ = guardar(
            cur, ctx.quien.workspace_id, NOVEDAD_DE_LO_QUE_ESPERA, task_id=str(f["task_id"]),
            destinatario=str(f["responsable_membership_id"]), hechos=hechos,
            programado_para=llega,
            clave=f"motor:{NOVEDAD_DE_LO_QUE_ESPERA}:{f['task_id']}:{clave}", ahora=ctx.ahora)
        ctx.avisos_guardados.append(aviso_id)
        item: dict[str, Any] = {"aviso_a_quien_espera": {"a": f["responsable"],
                                                         "tarea": f["titulo"],
                                                         LLEGA: llega.isoformat()}}
        nombrar_efecto(item, "aviso_a_quien_espera", AVISO, aviso_id)
        avisos.append(item)
    return {"avisos_a_quienes_esperan": avisos}


def se_trabo(ctx: Contexto, task_id: str, bloqueo_id: str, causa: str) -> dict[str, Any]:
    """La tarea de quien escribe se trabó. Si es lo que destraba la tarea de otra persona, la
    pregunta de para cuándo la destraba ya tiene respuesta (está trabado con eso): se cierra con
    su espera, y si todavía no le llegó, ya no sale; y quien espera, más abajo, se entera."""
    for f in _lo_esperan(ctx.cur, task_id):
        ctx.cur.execute("""select id from scheduled_notice
                            where task_id = %s and tipo = %s and estado = 'guardado'
                              and destinatario_membership_id = %s""",
                        (str(f["task_id"]), PREGUNTA_A_QUIEN_DESTRABA, ctx.quien.membership_id))
        for guardada in ctx.cur.fetchall():
            omitir(ctx.cur, str(guardada["id"]), "ya_respondio", ctx.ahora)
        detalle = {"jugada": "anotar_bloqueo", "tarea": str(f["task_id"]),
                   "su_tarea_se_trabo": str(task_id)}
        preguntas.cerrar_de_tipo(ctx, preguntas.CUANDO_SE_DESTRABA, str(f["task_id"]),
                                 "respondida", detalle)
        ctx.cur.execute("""update pending_reply set satisfecho_en = %s
                            where membership_id = %s and task_id = %s and tipo = %s
                              and satisfecho_en is null""",
                        (ctx.ahora, ctx.quien.membership_id, str(f["task_id"]),
                         preguntas.CUANDO_SE_DESTRABA))
    return avisar_hacia_abajo(ctx, task_id, {"se_trabo": {"causa": causa}},
                              f"{SE_TRABO}{bloqueo_id}")


def se_destrabo(ctx: Contexto, task_id: str, bloqueo_id: str) -> dict[str, Any]:
    """La tarea de quien escribe se destrabó: quien espera, más abajo, se entera. La suya sigue
    trabada hasta que lo diga."""
    return avisar_hacia_abajo(ctx, task_id, {"se_destrabo": True}, f"{SE_DESTRABO}{bloqueo_id}")


def dio_otro_dia(ctx: Contexto, task_id: str, prevision_id: str, fecha: str) -> dict[str, Any]:
    """Quien escribe dio un día nuevo para terminar su tarea: quien espera se entera."""
    return avisar_hacia_abajo(ctx, task_id, {"prevision": fecha}, f"{OTRO_DIA}{prevision_id}")


def la_entrego(ctx: Contexto, task_id: str, entrega: str | None) -> dict[str, Any]:
    """Quien escribe entregó su tarea (pasa a revisión): quien espera se entera."""
    return avisar_hacia_abajo(ctx, task_id, {"la_entrego": True},
                              f"{ENTREGO}{task_id}:{entrega or int(time.time() * 1000)}")


def quedo_terminada(ctx: Contexto, task_id: str, aprobacion_id: str) -> dict[str, Any]:
    """La tarea quedó terminada con la aprobación de quien escribe: quien espera se entera,
    enseguida (una decisión no se corrige por chat, decisión 19)."""
    return avisar_hacia_abajo(ctx, task_id, {"quedo_terminada": True},
                              f"{TERMINADA}{task_id}:{aprobacion_id}", con_margen=False)


def dijo_quien_destraba(ctx: Contexto, task_id: str, dicho_id: str,
                        dice: dict[str, Any]) -> dict[str, Any]:
    """Quien destraba esta tarea dijo algo de su bloqueo: a quien la tiene le llega lo de
    siempre (`persecucion`); a quien espera, más abajo, como un avance del medio."""
    return avisar_hacia_abajo(ctx, task_id,
                              {"quien_destraba": ctx.quien.nombre, "dice_quien_destraba": dice},
                              f"{DIJO}{dicho_id}")


# --- Al salir ---------------------------------------------------------------------------------

def vigencia(m: Momento, aviso: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    """Si el aviso de un avance todavía corresponde: la tarea sigue abierta y esperando la del
    avance, y el avance sigue valiendo (el bloqueo sigue trabado, lo dicho es lo último, el día
    es el que vale, sigue entregada). Los hechos de este momento: quién destraba ahora lo que se
    trabó."""
    cur = m.cur
    tarea = leer_tarea(cur, aviso["task_id"])
    if tarea is None:
        return "tarea_inexistente", {}
    if tarea["estado"] in ("terminada", "cancelada"):
        return "tarea_cerrada", {}
    parte = aviso["dedupe_key"].split(":")[3]
    letra, ident = parte[0], parte[1:]
    hechos = dict(aviso["hechos"] or {})
    if letra in (SE_TRABO, SE_DESTRABO):
        cur.execute("select task_id, resuelto_en from blocker where id = %s", (ident,))
        bloqueo = cur.fetchone()
        if bloqueo is None:
            return "tarea_inexistente", {}
        origen = str(bloqueo["task_id"])
        if letra == SE_TRABO:
            if bloqueo["resuelto_en"] is not None:
                return YA_SE_DESTRABO, {}
            novedad = dict(hechos.get("novedad") or {})
            se_trabo_con = dict(novedad.get("se_trabo") or {})
            lo_destraba = quien_lo_destraba(cur, ident)
            if lo_destraba:
                se_trabo_con["lo_destraba"] = lo_destraba
            hechos["novedad"] = {**novedad, "se_trabo": se_trabo_con}
        elif _no_se_entero(cur, aviso, ident):
            return NO_SE_ENTERO_QUE_SE_TRABO, {}
    elif letra == DIJO:
        cur.execute("""select b.id, b.task_id, b.resuelto_en from dicho_de_quien_destraba d
                         join blocker_unblocker u on u.id = d.blocker_unblocker_id
                         join blocker b on b.id = u.blocker_id
                        where d.id = %s""", (ident,))
        dicho = cur.fetchone()
        if dicho is None:
            return "tarea_inexistente", {}
        if dicho["resuelto_en"] is not None:
            return YA_SE_DESTRABO, {}
        cur.execute("""select d.id from dicho_de_quien_destraba d
                         join blocker_unblocker u on u.id = d.blocker_unblocker_id
                        where u.blocker_id = %s order by d.at desc, d.id desc limit 1""",
                    (dicho["id"],))
        if str(cur.fetchone()["id"]) != ident:
            return DIJO_ALGO_MAS_NUEVO, {}
        origen = str(dicho["task_id"])
    elif letra == OTRO_DIA:
        cur.execute("""select f.task_id,
                              exists (select 1 from task_forecast g where g.reemplaza_id = f.id)
                                as reemplazada
                         from task_forecast f where f.id = %s""", (ident,))
        prevision = cur.fetchone()
        if prevision is None:
            return "tarea_inexistente", {}
        if prevision["reemplazada"]:
            return HAY_UNA_PREVISION_MAS_NUEVA, {}
        origen = str(prevision["task_id"])
    else:
        origen = ident
        if letra == ENTREGO:
            de = leer_tarea(cur, origen)
            if de is None or de["estado"] != "en_revision":
                return YA_NO_ESTA_ENTREGADA, {}
    if not any(str(f["task_id"]) == str(aviso["task_id"])
               and str(f["responsable_membership_id"]) == str(aviso["destinatario_membership_id"])
               for f in aguas_abajo(cur, origen)):
        return YA_NO_ESPERA_ESA_TAREA, {}
    return None, {**hechos, "tarea": tarea["titulo"]}


def _no_se_entero(cur, aviso: dict[str, Any], bloqueo_id: str) -> bool:
    """Si a esa persona no le llegó que ese bloqueo se abrió (el aviso de que se trabó no
    salió): que se destrabó no le dice nada."""
    clave = aviso["dedupe_key"].split(":")
    clave[3] = f"{SE_TRABO}{bloqueo_id}"
    cur.execute("""select estado from scheduled_notice where workspace_id = %s
                     and dedupe_key = %s""", (str(aviso["workspace_id"]), ":".join(clave)))
    fila = cur.fetchone()
    return fila is not None and fila["estado"] == "omitido"
