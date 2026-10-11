"""Lo retirado por la administración deja de contar, y Leda avisa (decisión 58 del usuario,
2026-10-10; porción 5b de la C-3).

Cuando la administración retira el contenido de una pieza (`pagina_de_tarea.retirar_contenido`,
por la consola), la pieza deja de contar para la política de evidencia, como cualquier retirada.
Antes nadie se enteraba, y la aprobación quedaba trabada ("Falta la evidencia requerida") sin
que nadie supiera por qué. Ahora, en la misma transacción que el retiro, se guardan dos avisos
de coordinación del motor (los causa el acto de otra persona: fuera del tope diario, mecánica
§10), que redacta la IA desde los hechos de la cocina y salen dentro del horario, como todos
(`avisos.enviar_avisos`):

- **A quien entregó la pieza** (`CONTENIDO_RETIRADO_POR_LA_ADMINISTRACION`), si la tarea no está
  aprobada: que la administración retiró esa pieza, con el motivo que dio, y, si la entrega en
  revisión quedó sin cubrir (`entrega.falta_algo_de_lo_entregado`, la misma regla de la decisión
  15), lo que falta para que la revisen. Una pieza que ya había retirado esa persona no se le
  vuelve a contar.
- **A quien revisa la tarea** (`LA_ENTREGA_ESPERA_OTRA_PIEZA`), si está en revisión y quedó sin
  cubrir: que la entrega espera esa pieza nueva. Sin el motivo, que es para quien la entregó; si
  quien la revisa es quien la entregó, le llega sólo el primero. Si a quien revisa todavía no le
  llegó la entrega (el retiro cayó dentro del margen para corregir), no le llega nada: cuando
  llegue la pieza nueva, recibe la entrega como siempre (decisión 60).

Nunca se nombra a quien retiró: la administración, sin nombre (decisión 59; quién fue queda en
la auditoría). Una tarea aprobada (terminada, o con la aprobación vigente de quien la revisa) o
cancelada no avisa a nadie. Varias piezas a la vez (la misma foto en dos piezas es un solo
archivo, y se retiran todas) dan un aviso por persona, con cada tarea adentro.

Al salir, cada aviso se relee (`vigencia_*`): lo retirado sigue retirado, pero lo que falta es lo
de ese momento. Si la persona ya mandó la pieza nueva, a quien la entregó le llega igual que se
retiró, sin pedirle nada, y a quien la revisa no le llega nada (queda omitido con su motivo): la
entrega completa le llega como siempre (`avisos.ENTREGA_PARA_APROBAR`, decisión 15). Con la pieza
nueva, la persona completa la entrega por el camino de siempre (`entrega.entregar` sobre una
tarea en revisión).

Lo que se guarda en el aviso son los hechos de la cocina y sus referencias internas
(`REFERENCIAS`, que nunca le llegan a la IA): qué piezas de qué tarea. El envío queda auditado
como todo envío de Leda (`avisos._enviar`); guardar un aviso no se audita (`auditoria.py`), y el
retiro mismo queda en la auditoría de la administración (`retirar_contenido_de_evidencia`, con
cuántos avisos se guardaron).
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from psycopg.pq import TransactionStatus

from . import entrega
from .avisos import (CONTENIDO_RETIRADO_POR_LA_ADMINISTRACION, ENTREGA_PARA_APROBAR,
                     LA_ENTREGA_ESPERA_OTRA_PIEZA,
                     LA_ENTREGA_YA_ESTA_COMPLETA, YA_ESTA_APROBADA, YA_NO_ESTA_ENTREGADA,
                     Momento, aprobacion_vigente, aviso_de_la_entrega, guardar, leer_tarea)
from .fichas import quien_revisa

# Las claves de los hechos (sus significados, en `hechos.SIGNIFICADOS`).
MOTIVO_DEL_RETIRO = "motivo_del_retiro"
EN_CADA_TAREA = "piezas_retiradas_por_tarea"
QUE_ESPERAN = "entregas_que_esperan_otra_pieza"
PIEZAS_RETIRADAS = "piezas_retiradas"
LA_REVISION_ESPERA_OTRA_PIEZA = "la_revision_espera_otra_pieza"
# Qué piezas de qué tarea: referencias internas del aviso, que la IA nunca recibe.
REFERENCIAS = "referencias"


# --- Guardar --------------------------------------------------------------------------------

def avisar(cur, workspace_id: str, piezas: Sequence[str], motivo: str,
           ahora: datetime) -> int:
    """Guarda los avisos del retiro de `piezas` por la administración y devuelve cuántos. Corre
    en la transacción del retiro, bajo la conexión administrativa: el espacio de la
    transacción se fija acá para leer a sus personas (y se devuelve como estaba). Si guardar
    falla con la transacción abortada, el espacio no se devuelve a mano (fallaría también y
    taparía el error de verdad): lo devuelve el rollback, porque `set_config` es local a la
    transacción (revisión de la porción 5b)."""
    cur.execute("select coalesce(current_setting('leda.workspace_id', true), '') as previo")
    previo = cur.fetchone()["previo"]
    cur.execute("select set_config('leda.workspace_id', %s, true)", (workspace_id,))
    try:
        return _avisar(cur, workspace_id, list(piezas), motivo, ahora)
    finally:
        if cur.connection.info.transaction_status != TransactionStatus.INERROR:
            cur.execute("select set_config('leda.workspace_id', %s, true)", (previo,))


def _avisar(cur, workspace_id: str, piezas: list[str], motivo: str, ahora: datetime) -> int:
    if not piezas:
        return 0
    cur.execute("""select e.id, e.task_id, e.entregado_por,
                          exists (select 1 from evidencia_retirada w
                                   where w.evidence_id = e.id
                                     and w.retirada_por_membership_id is not null) as ya_la_retiro
                     from evidence e
                    where e.id = any(%s::uuid[]) and e.workspace_id = %s
                    order by e.at, e.id""", (piezas, workspace_id))
    # A quien entregó: persona -> tarea -> piezas, en el orden en que se entregaron.
    entregadas: dict[str, dict[str, list[str]]] = {}
    for f in cur.fetchall():
        if f["entregado_por"] is None or f["ya_la_retiro"]:
            continue
        tarea = leer_tarea(cur, f["task_id"])
        if tarea is None or _aprobada_o_cerrada(cur, tarea):
            continue
        entregadas.setdefault(str(f["entregado_por"]), {}).setdefault(
            str(f["task_id"]), []).append(str(f["id"]))
    # A quien revisa: revisor -> tareas en revisión que quedaron sin cubrir.
    esperan: dict[str, list[str]] = {}
    for persona, por_tarea in entregadas.items():
        for task_id in por_tarea:
            if not _espera_otra_pieza(cur, task_id):
                continue
            quien = quien_revisa(cur, task_id)
            if quien is None or quien["membership_id"] == persona:
                continue
            if not _le_llego_la_entrega(cur, task_id, quien["membership_id"]):
                continue
            if task_id not in esperan.setdefault(quien["membership_id"], []):
                esperan[quien["membership_id"]].append(task_id)

    zona = _zona(cur, workspace_id)
    primera = piezas[0]
    guardados = 0
    for persona, por_tarea in entregadas.items():
        referencias = [{"tarea": t, "piezas": p} for t, p in por_tarea.items()]
        hechos = {"aviso": CONTENIDO_RETIRADO_POR_LA_ADMINISTRACION,
                  "necesita_respuesta": False, MOTIVO_DEL_RETIRO: motivo,
                  EN_CADA_TAREA: [_de_una_tarea(cur, r, zona) for r in referencias],
                  REFERENCIAS: referencias}
        _, nuevo = guardar(cur, workspace_id, CONTENIDO_RETIRADO_POR_LA_ADMINISTRACION,
                           task_id=_una_sola(por_tarea), destinatario=persona, hechos=hechos,
                           programado_para=ahora, ahora=ahora,
                           clave=f"motor:{CONTENIDO_RETIRADO_POR_LA_ADMINISTRACION}:"
                                 f"{primera}:{persona}")
        guardados += nuevo
    for revisor, tareas in esperan.items():
        referencias = [{"tarea": t} for t in tareas]
        hechos = {"aviso": LA_ENTREGA_ESPERA_OTRA_PIEZA, "necesita_respuesta": False,
                  QUE_ESPERAN: [_lo_que_espera(cur, t) for t in tareas],
                  REFERENCIAS: referencias}
        _, nuevo = guardar(cur, workspace_id, LA_ENTREGA_ESPERA_OTRA_PIEZA,
                           task_id=_una_sola(tareas), destinatario=revisor, hechos=hechos,
                           programado_para=ahora, ahora=ahora,
                           clave=f"motor:{LA_ENTREGA_ESPERA_OTRA_PIEZA}:{primera}:{revisor}")
        guardados += nuevo
    return guardados


def _le_llego_la_entrega(cur, task_id: str, revisor: str) -> bool:
    """Si a quien revisa ya le llegó el aviso de la última entrega de la tarea. Si el retiro cae
    antes (dentro del margen para corregir), no se le avisa de una entrega que nunca vio: cuando
    llegue la pieza nueva, le llega la entrega como siempre (decisión 60 del usuario)."""
    aviso = aviso_de_la_entrega(cur, task_id)
    return (aviso is not None and aviso["estado"] == "enviado"
            and str(aviso["destinatario_membership_id"]) == revisor)


def _una_sola(tareas) -> str | None:
    """La tarea del aviso, si es una sola; con varias, ninguna (cada una va en sus hechos)."""
    tareas = list(tareas)
    return tareas[0] if len(tareas) == 1 else None


def _zona(cur, workspace_id: str) -> ZoneInfo:
    cur.execute("select zona_horaria from workspace where id = %s", (workspace_id,))
    return ZoneInfo(cur.fetchone()["zona_horaria"])


# --- La regla ---------------------------------------------------------------------------------

def _aprobada_o_cerrada(cur, tarea: dict[str, Any]) -> bool:
    """Si la tarea está aprobada (terminada, o con la aprobación vigente de quien la revisa) o
    cancelada: un retiro no le cambia nada a nadie."""
    if tarea["estado"] in ("terminada", "cancelada"):
        return True
    quien = quien_revisa(cur, str(tarea["id"]))
    return quien is not None and aprobacion_vigente(cur, str(tarea["id"]),
                                                    quien["membership_id"]) is not None


def _espera_otra_pieza(cur, task_id: str) -> bool:
    """Si la entrega de una tarea en revisión quedó sin cubrir (la política o lo que describía
    el criterio): la revisión espera otra pieza (decisión 15)."""
    tarea = leer_tarea(cur, task_id)
    return (tarea is not None and tarea["estado"] == "en_revision"
            and entrega.falta_algo_de_lo_entregado(cur, task_id))


def _lo_que_falta(cur, task_id: str) -> dict[str, Any]:
    """Lo que le falta a la entrega para que la revisen, en palabras de todos los días."""
    pol = entrega.politica(cur, task_id)
    cur.execute("select tipos_de_evidencia_que_faltan(%s) as t", (task_id,))
    falta: dict[str, Any] = {"le_falta": [pol.en_palabras(t)
                                          for t in cur.fetchone()["t"] or []]}
    del_criterio = entrega.falta_del_criterio_de_lo_entregado(cur, task_id)
    if del_criterio:
        falta["le_falta_del_criterio"] = del_criterio
    return falta


# --- Los hechos -------------------------------------------------------------------------------

def _piezas(cur, ids: Sequence[str], zona: ZoneInfo, pol) -> list[dict[str, Any]]:
    """Cada pieza retirada como la recibe la IA: qué era, qué cubría y qué día la entregó. Nunca
    su contenido, su nombre ni quién la retiró.

    El día es el del reloj de Leda, como `aprobacion.aprobada_el`: el del aviso de esa entrega a
    quien la revisa, que guardó el turno que la confirmó. La fila de la evidencia la fecha la
    base (`clock_timestamp()`), porque su orden frente a las decisiones sobre la tarea lo exige
    (T6j); en una corrida con el reloj movido, esa fecha no es la de Leda. El aviso se ata a la
    primera pieza del acto (`herramientas._entregar_tarea`, `entrega`), y las piezas de un mismo
    acto se escriben en una sola transacción, la misma `xmin` (una evidencia no se modifica).
    Sin ese aviso (nadie la revisa, o la entregó quien la revisa), el de la fila."""
    cur.execute("""select e.clase, e.cubre, e.at, e.es_ejemplo_aceptado,
                          a.clase as clase_del_archivo,
                          (select min(n.creado_en)
                             from evidence f
                             join scheduled_notice n
                               on n.dedupe_key = %s || f.id::text
                            where f.task_id = e.task_id and f.xmin = e.xmin) as en_el_reloj
                     from evidence e
                     left join archivo a on a.workspace_id = e.workspace_id
                                        and a.id = e.archivo_id
                    where e.id = any(%s::uuid[])
                    order by e.at, e.id""",
                (f"motor:{ENTREGA_PARA_APROBAR}:", list(ids)))
    vistas = []
    for f in cur.fetchall():
        es = {"texto": entrega.LO_QUE_ESCRIBIO, "enlace": entrega.UN_ENLACE,
              "imagen": entrega.UNA_FOTO}.get(
            f["clase"], entrega.UN_VIDEO if f["clase_del_archivo"] == "video"
            else entrega.UN_ARCHIVO)
        if f["es_ejemplo_aceptado"]:
            es = entrega.EL_EJEMPLO_QUE_ACEPTO
        vistas.append({"es": es, "cubria": [pol.en_palabras(t) for t in f["cubre"] or []],
                       "la_entrego_el": (f["en_el_reloj"] or f["at"]).astimezone(zona)
                                        .date().isoformat()})
    return vistas


def _de_una_tarea(cur, referencia: dict[str, Any], zona: ZoneInfo) -> dict[str, Any] | None:
    """Lo que se le dice a quien entregó, de una tarea: sus piezas retiradas y, si la entrega en
    revisión quedó sin cubrir, lo que falta para que la revisen."""
    tarea = leer_tarea(cur, referencia["tarea"])
    if tarea is None:
        return None
    pol = entrega.politica(cur, str(tarea["id"]))
    hecho: dict[str, Any] = {"tarea": tarea["titulo"],
                             PIEZAS_RETIRADAS: _piezas(cur, referencia["piezas"], zona, pol)}
    if _espera_otra_pieza(cur, str(tarea["id"])):
        hecho[LA_REVISION_ESPERA_OTRA_PIEZA] = True
        hecho.update(_lo_que_falta(cur, str(tarea["id"])))
    return hecho


def _lo_que_espera(cur, task_id: str) -> dict[str, Any]:
    """Lo que se le dice a quien revisa, de una tarea: quién la entregó y lo que le falta."""
    tarea = leer_tarea(cur, task_id)
    cur.execute("select nombre from integrante where membership_id = %s",
                (str(tarea["responsable_membership_id"]),))
    fila = cur.fetchone()
    return {"tarea": tarea["titulo"], "responsable": fila["nombre"] if fila else None,
            **_lo_que_falta(cur, task_id)}


# --- Al salir ---------------------------------------------------------------------------------

def vigencia_a_quien_la_entrego(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    """El aviso a quien entregó sale mientras alguna de sus tareas siga sin aprobar, con lo que
    falta de ese momento."""
    guardados = dict(aviso["hechos"] or {})
    zona = m.cal.zona
    tareas = []
    for referencia in guardados.get(REFERENCIAS) or []:
        tarea = leer_tarea(m.cur, referencia["tarea"])
        if tarea is None or _aprobada_o_cerrada(m.cur, tarea):
            continue
        hecho = _de_una_tarea(m.cur, referencia, zona)
        if hecho is not None:
            tareas.append(hecho)
    if not tareas:
        return YA_ESTA_APROBADA, {}
    return None, {"aviso": CONTENIDO_RETIRADO_POR_LA_ADMINISTRACION,
                  "necesita_respuesta": False,
                  MOTIVO_DEL_RETIRO: guardados.get(MOTIVO_DEL_RETIRO), EN_CADA_TAREA: tareas}


def vigencia_a_quien_la_revisa(m: Momento, aviso) -> tuple[str | None, dict[str, Any]]:
    """El aviso a quien revisa sale mientras alguna de sus tareas siga en revisión, sin cubrir,
    sin su aprobación y revisada por quien lo recibe. Si ya se completó, no sale: la entrega
    completa le llega en su propio aviso."""
    persona = str(aviso["destinatario_membership_id"])
    esperan, motivo = [], YA_NO_ESTA_ENTREGADA
    for referencia in (dict(aviso["hechos"] or {})).get(REFERENCIAS) or []:
        task_id = str(referencia["tarea"])
        tarea = leer_tarea(m.cur, task_id)
        if tarea is None or tarea["estado"] != "en_revision":
            continue
        quien = quien_revisa(m.cur, task_id)
        if quien is None or quien["membership_id"] != persona:
            continue
        if aprobacion_vigente(m.cur, task_id, persona) is not None:
            motivo = YA_ESTA_APROBADA
            continue
        if not entrega.falta_algo_de_lo_entregado(m.cur, task_id):
            motivo = LA_ENTREGA_YA_ESTA_COMPLETA
            continue
        esperan.append(_lo_que_espera(m.cur, task_id))
    if not esperan:
        return motivo, {}
    return None, {"aviso": LA_ENTREGA_ESPERA_OTRA_PIEZA, "necesita_respuesta": False,
                  QUE_ESPERAN: esperan}
