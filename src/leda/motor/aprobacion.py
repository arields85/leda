"""La hoja de aprobación: aprobar o pedir cambios sobre una entrega (circuito 8).

Porción 3b de la C-3 (`odd/tasks/fase-c.md`, preguntas 2 y 3, decididas por el usuario el
2026-10-07); ADR 0017, decisión 3b; ADR 0018, decisiones 1, 2 y 4; mecánica §5 y §7; constitución
§3, §4 y §11.

**Quién decide.** Sólo quien aprueba el trabajo del responsable (`membership.
aprobador_membership_id`, la autoridad un nivel arriba; la cocina lo exige en `aprobar_tarea` y
`pedir_cambios_tarea`). Quien escribe ve, además de sus tareas, las entregas que esperan su
decisión (`para_decidir`), con su alias: así nombra una. Una que no ve la nombra por su
responsable (`de`): si no es quien aprueba ese trabajo, Leda le dice quién es, sin mostrarle
nada de la tarea, y nada cambia. Nadie aprueba su propio trabajo, y Leda nunca cuenta como
aprobadora.

**Lo claro va directo,** sin vista previa: es la decisión de quien aprueba (usuario, 2026-10-07).
Aprobar anota la aprobación con su comentario y la cocina comprueba el cierre en el mismo acto
(mecánica §5: la evidencia que pide la política, sin bloqueos ni dependencias bloqueantes
abiertas, y la aprobación): si se cumple, la tarea queda terminada; si no, la aprobación queda
anotada y los hechos dicen qué frena el cierre. Pedir cambios sin decir qué falta lo pregunta (un
tema abierto, `QUE_CAMBIOS_PIDE`); con lo que falta, la tarea vuelve al estado que tenía antes de
entregarla. "Terminé" nunca llega acá: la entrega lleva a revisión (constitución §11).

**Lo que admite dos lecturas** ("aprobado, pero que revise el cable") son dos jugadas opuestas
sobre la misma tarea en un mensaje: ninguna se hace y Leda pregunta una sola vez cuál, con dos
botones (`fichas.dos_lecturas`, una regla general para toda ficha que declara su opuesta).

**El aviso de una entrega ofrece los botones** "Aprobar" y "Pedir cambios" como atajos
(`avisos`, `entrega_para_aprobar`, `preguntas.DECISION_DE_LA_ENTREGA`); escribir vale igual. El
botón corre la misma jugada que lo escrito, con la guarda de la decisión 2: lo que se decide es
lo que mostró el aviso (`entrega.huella_de_lo_entregado`); si la entrega cambió, no vale. Un
botón de un aviso ya decidido o reemplazado no hace nada y lo dice (situación general 7), y un
toque repetido no repite nada.

**Los avisos al responsable** (aprobada, aprobada con lo que falta, cambios pedidos con su
comentario) los redacta el motor desde los hechos, como el de la entrega: son de coordinación
(fuera del tope diario, mecánica §10) y salen enseguida, dentro del horario. A diferencia de lo
que alguien cuenta (una fecha, una entrega), una decisión no se corrige por chat: un margen para
corregir sólo la demoraría.

**La aprobación que todavía no puede cerrar** queda anotada; cuando lo que faltaba se resuelve,
el sistema vuelve a comprobar el cierre y la cierra solo, sin otra aprobación
(`cerrar_las_que_ya_pueden`, en cada vuelta del ciclo; la cocina, `cerrar_tarea_aprobada`), con
aviso al responsable y a quien aprobó. Es una regla general: vale para lo que se haya resuelto
(una dependencia que terminó o se canceló, un bloqueo que se cerró) y por el camino que sea.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import psycopg

from ..autoridad import Canal, Solicitante
from ..calendario import Calendario
from ..db import espacio
from ..herramientas import ejecutar

from . import entrega, fichas, preguntas
from .avisos import (CERRADA_CON_LA_APROBACION, PEDIDO_DE_CAMBIOS, TAREA_APROBADA, guardar)
from .tiempo import Reloj, sale

# Los códigos de por qué no se decide.
SU_PROPIO_TRABAJO = "su_propio_trabajo"
NO_ES_QUIEN_APRUEBA = "no_es_quien_aprueba"
NADA_PARA_DECIDIR = "nada_para_decidir"
PERSONA_DESCONOCIDA = "persona_desconocida"
YA_LA_APROBO = "ya_la_aprobo"
FALTA_EVIDENCIA = "falta_evidencia"
CAMBIO_LA_ENTREGA = "cambio_la_entrega"
# Lo que se resolvió cuando el sistema cierra solo una tarea aprobada.
TAREAS_QUE_ESPERABA = "tareas_que_esperaba"
BLOQUEOS_QUE_SE_CERRARON = "bloqueos_que_se_cerraron"

# Una cadena de tareas aprobadas que se cierran una detrás de otra en una vuelta, con un tope.
_VUELTAS_DE_CIERRE = 20


# --- Las entregas que esperan la decisión de quien escribe --------------------------------------

def para_decidir(cur, quien: Solicitante, desde: int, zona) -> tuple[dict[str, Any], ...]:
    """Las tareas en revisión de las personas cuyo trabajo aprueba quien escribe, con su alias
    (siguiendo los de sus tareas, desde `desde`), su responsable, lo que entregó y, si ya la
    aprobó y espera que se resuelva lo que falta, desde cuándo."""
    cur.execute("""select t.id, t.titulo, t.estado::text estado, t.fecha_objetivo,
                          i.nombre as responsable
                     from task t
                     join membership m on m.id = t.responsable_membership_id
                     join integrante i on i.membership_id = t.responsable_membership_id
                    where m.aprobador_membership_id = %s and t.estado = 'en_revision'
                    order by t.fecha_objetivo nulls last, t.titulo""", (quien.membership_id,))
    tareas = []
    for i, t in enumerate(cur.fetchall(), desde + 1):
        una: dict[str, Any] = {
            "alias": f"T{i}", "id": str(t["id"]), "titulo": t["titulo"], "estado": t["estado"],
            "fecha_objetivo": t["fecha_objetivo"].isoformat() if t["fecha_objetivo"] else None,
            "para_decidir": True, "responsable": t["responsable"]}
        lo = lo_que_entrego(cur, str(t["id"]), zona)
        if lo:
            una["lo_que_entrego"] = lo
        vigente = aprobacion_vigente(cur, str(t["id"]), quien.membership_id)
        if vigente is not None:
            una["ya_la_aprobo_el"] = aprobada_el(cur, vigente, zona)
        tareas.append(una)
    return tuple(tareas)


def lo_que_entrego(cur, task_id: str, zona) -> list[dict[str, Any]]:
    """Lo entregado vigente de la tarea, pieza por pieza, como lo recibe la IA, sin los alias de
    las piezas (sacar una es del responsable)."""
    piezas = entrega._lo_entregado(cur, task_id)
    vistas = entrega.mostrar(piezas, entrega.politica(cur, task_id), zona)
    for vista in vistas:
        vista.pop("pieza", None)
    return vistas


def aprobacion_vigente(cur, task_id: str, aprobador: str) -> dict[str, Any] | None:
    """La última aprobación de esa persona sobre la tarea que ningún pedido de cambios suyo
    posterior dejó sin efecto (la misma regla que `motivo_no_cierra_tarea`)."""
    cur.execute("""select a.id, a.at from approval a
                    where a.sujeto_tipo = 'tarea' and a.sujeto_id = %s
                      and a.decision = 'aprobado' and a.aprobador_membership_id = %s
                      and not exists (select 1 from approval r
                                       where r.sujeto_tipo = 'tarea'
                                         and r.sujeto_id = a.sujeto_id
                                         and r.aprobador_membership_id = %s
                                         and r.decision = 'rechazado' and r.at >= a.at)
                    order by a.at desc limit 1""", (task_id, aprobador, aprobador))
    return cur.fetchone()


def aprobada_el(cur, aprobacion: dict[str, Any], zona) -> str:
    """El día en que se dio una aprobación, en el reloj del motor: el del aviso que la contó al
    responsable (lo guardó el turno que la anotó); sin él, el de la fila, que fecha la base."""
    cur.execute("select creado_en from scheduled_notice where dedupe_key = %s",
                (f"motor:{TAREA_APROBADA}:{aprobacion['id']}",))
    fila = cur.fetchone()
    return (fila["creado_en"] if fila else aprobacion["at"]).astimezone(zona).date().isoformat()


# --- Las jugadas ---------------------------------------------------------------------------

def aprobar(ctx, datos: dict, tarea: dict | None) -> dict:
    """Aprobar, escrito o tocado: lo claro va directo; la cocina comprueba el cierre."""
    tarea, no = _la_tarea(ctx, "aprobar", datos, tarea)
    if no is not None:
        return no
    no = _la_guarda(ctx, datos, tarea)
    if no is not None:
        return no
    cur = ctx.cur
    vigente = aprobacion_vigente(cur, tarea["id"], ctx.quien.membership_id)
    if vigente is not None:
        return {"resultado": "no_se_puede", "motivo": YA_LA_APROBO, "tarea": _tarea(tarea),
                "ya_la_aprobo_el": aprobada_el(cur, vigente, ctx.calendario.zona),
                **_frena(cur, tarea["id"])}
    faltan = entrega._faltan(cur, tarea["id"], [])
    if faltan:
        pol = entrega.politica(cur, tarea["id"])
        return {"resultado": "no_se_puede", "motivo": FALTA_EVIDENCIA, "tarea": _tarea(tarea),
                "todavia_le_falta": [pol.en_palabras(t) for t in faltan]}
    comentario = _comentario(datos)
    r = ejecutar(cur, ctx.quien, "aprobar_tarea",
                 {"tarea_id": tarea["id"], **({"comentario": comentario} if comentario else {})},
                 ya_confirmada=True)
    if not r.get("aprobada"):
        return fichas.no_hecho(r, tarea)
    responsable = _responsable(cur, tarea["id"])
    hecho: dict[str, Any] = {"resultado": "anotado", "tarea": _tarea(tarea),
                             **({"comentario": comentario} if comentario else {})}
    if r["cerrada"]:
        hecho["quedo_terminada"] = True
    else:
        hecho.update(_frena(cur, tarea["id"]))
        hecho["se_cierra_sola"] = {"se_avisa_a": [responsable["nombre"], ctx.quien.nombre]}
    del_aviso = {k: v for k, v in hecho.items() if k in ("comentario", "quedo_terminada",
                                                          "no_se_cierra_todavia",
                                                          "se_cierra_sola")}
    _avisar_al_responsable(ctx, hecho, TAREA_APROBADA, tarea, responsable,
                           {"aprobada_por": ctx.quien.nombre, **del_aviso},
                           clave=f"motor:{TAREA_APROBADA}:{r['aprobacion_id']}")
    return hecho


def pedir_cambios(ctx, datos: dict, tarea: dict | None) -> dict:
    """Pedir cambios, escrito o tocado: sin decir qué falta, lo pregunta y nada cambia; con lo
    que falta, la tarea vuelve a quien la tiene, con el comentario."""
    tarea, no = _la_tarea(ctx, "pedir_cambios", datos, tarea)
    if no is not None:
        return no
    no = _la_guarda(ctx, datos, tarea)
    if no is not None:
        return no
    comentario = _comentario(datos)
    if comentario is None:
        hecho = {"resultado": "falta_dato", "falta": ["comentario"], "tarea": _tarea(tarea)}
        fichas.abrir_pregunta(ctx, hecho, preguntas.QUE_CAMBIOS_PIDE, tarea["id"],
                              jugada={"nombre": "pedir_cambios", "datos": {}})
        return hecho
    cur = ctx.cur
    r = ejecutar(cur, ctx.quien, "pedir_cambios_tarea",
                 {"tarea_id": tarea["id"], "comentario": comentario}, ya_confirmada=True)
    if not r.get("pedido"):
        return fichas.no_hecho(r, tarea)
    hecho = {"resultado": "anotado", "tarea": _tarea(tarea), "comentario": comentario,
             "estado": r["estado"]}
    _avisar_al_responsable(ctx, hecho, PEDIDO_DE_CAMBIOS, tarea, _responsable(cur, tarea["id"]),
                           {"pidio_cambios": ctx.quien.nombre, "comentario": comentario,
                            "puede_volver_a_entregarla": True},
                           clave=f"motor:{PEDIDO_DE_CAMBIOS}:{r['decision_id']}")
    return hecho


# --- Lo que comparten ----------------------------------------------------------------------

def _la_tarea(ctx, nombre: str, datos: dict, tarea: dict | None
              ) -> tuple[dict | None, dict | None]:
    """La entrega sobre la que se decide, o por qué no hay una: la nombrada por su alias; si no,
    la de la persona que se nombra (`de`), si es la única suya que espera; si no, la duda, con
    las entregas que esperan como opciones (situación general 5)."""
    cur, yo = ctx.cur, ctx.quien.membership_id
    if tarea is not None:
        if ctx.suya(tarea["alias"]) is not None:
            return None, _su_propio_trabajo(ctx, tarea)
        if not tarea.get("para_decidir"):
            return None, {"resultado": "no_se_puede", "motivo": "tarea_desconocida"}
        return tarea, None
    candidatas = list(ctx.para_aprobar)
    de = None if fichas.vacio(datos.get("de")) else str(datos["de"]).strip()
    if de is not None:
        coinciden = fichas.integrantes_que_coinciden(cur, de)
        if len(coinciden) > 1:
            return None, {"resultado": "falta_dato", "falta": ["de"],
                          "coinciden": [c["nombre"] for c in coinciden]}
        if not coinciden:
            return None, {"resultado": "no_se_puede", "motivo": PERSONA_DESCONOCIDA}
        persona = str(coinciden[0]["membership_id"])
        if persona == yo:
            return None, _su_propio_trabajo(ctx, None)
        quien_aprueba = fichas.referente(cur, persona)
        if quien_aprueba is None or quien_aprueba["membership_id"] != yo:
            return None, {"resultado": "no_se_puede", "motivo": NO_ES_QUIEN_APRUEBA,
                          "responsable": coinciden[0]["nombre"],
                          **({"quien_aprueba": quien_aprueba["nombre"]}
                             if quien_aprueba is not None else {})}
        cur.execute("""select id from task where responsable_membership_id = %s
                          and id = any(%s::uuid[])""",
                    (persona, [t["id"] for t in candidatas]))
        suyas = {str(f["id"]) for f in cur.fetchall()}
        candidatas = [t for t in candidatas if t["id"] in suyas]
        if len(candidatas) == 1:
            return candidatas[0], None
        if not candidatas:
            return None, {"resultado": "no_se_puede", "motivo": NADA_PARA_DECIDIR,
                          "responsable": coinciden[0]["nombre"]}
    if not candidatas:
        return None, {"resultado": "no_se_puede", "motivo": NADA_PARA_DECIDIR}
    hecho = {"resultado": "falta_dato", "falta": ["tarea"]}
    ahora, pregunta_id = preguntas.abrir_con_id(
        ctx, preguntas.CUAL_TAREA, None, jugada={"nombre": nombre, "datos": dict(datos)},
        opciones_de_tareas=candidatas)
    fichas.nombrar_pregunta(hecho, "pregunta" if ahora else "pregunta_para_despues",
                            preguntas.CUAL_TAREA, pregunta_id)
    return None, hecho


def _su_propio_trabajo(ctx, tarea: dict | None) -> dict:
    quien_aprueba = fichas.referente(ctx.cur, ctx.quien.membership_id)
    return {"resultado": "no_se_puede", "motivo": SU_PROPIO_TRABAJO,
            **({"tarea": _tarea(tarea)} if tarea else {}),
            **({"quien_aprueba": quien_aprueba["nombre"]} if quien_aprueba else {})}


def _la_guarda(ctx, datos: dict, tarea: dict) -> dict | None:
    """El botón de un aviso decide sobre lo que el aviso mostró (ADR 0018, decisión 2): si la
    entrega cambió desde entonces, no vale. Lo escrito, y una opción de una pregunta sin huella,
    deciden sobre lo que vale ahora."""
    tocada = datos.get("de_la_pregunta")
    if not tocada:
        return None
    ctx.cur.execute("select tipo, jugada from conversation_question where id = %s", (tocada,))
    q = ctx.cur.fetchone()
    huella = ((q or {}).get("jugada") or {}).get("huella")
    if huella is None or huella == entrega.huella_de_lo_entregado(ctx.cur, tarea["id"]):
        return None
    return {"resultado": "no_se_puede", "motivo": CAMBIO_LA_ENTREGA, "tarea": _tarea(tarea)}


def _frena(cur, task_id: str) -> dict[str, Any]:
    """Lo que frena el cierre de una tarea aprobada, en hechos (la regla es la de la base,
    `motivo_no_cierra_tarea`): las tareas que tienen que terminar antes, sus bloqueos abiertos,
    el criterio de aceptación que falta o, si es otra cosa, que falta algo más. Vacío si nada
    lo frena."""
    cur.execute("select motivo_no_cierra_tarea(%s) as m", (task_id,))
    if cur.fetchone()["m"] is None:
        return {}
    frena: dict[str, Any] = {}
    cur.execute("""select o.titulo, o.estado::text estado, i.nombre
                     from dependency d
                     join task o on o.id = d.origen_task_id
                     left join integrante i on i.membership_id = o.responsable_membership_id
                    where d.destino_task_id = %s and d.tipo = 'bloqueante'
                      and o.estado not in ('terminada', 'cancelada')
                    order by o.titulo""", (task_id,))
    espera = [{"tarea": f["titulo"], "estado": f["estado"], "responsable": f["nombre"]}
              for f in cur.fetchall()]
    if espera:
        frena["espera_que_terminen"] = espera
    cur.execute("""select causa from blocker where task_id = %s and resuelto_en is null
                    order by abierto_en""", (task_id,))
    causas = [f["causa"] for f in cur.fetchall()]
    if causas:
        frena["bloqueos_abiertos"] = causas
    cur.execute("""select t.criterio_aceptacion,
                          coalesce((select s.valor::text::boolean from workspace_setting s
                                     where s.workspace_id = t.workspace_id
                                       and s.clave = 'exigir_criterio_aceptacion'), true) exige
                     from task t where t.id = %s""", (task_id,))
    fila = cur.fetchone()
    if fila["exige"] and not (fila["criterio_aceptacion"] or "").strip():
        frena["falta_el_criterio_de_aceptacion"] = True
    if not frena:
        frena["falta_algo_mas"] = True
    return {"no_se_cierra_todavia": frena}


def _responsable(cur, task_id: str) -> dict[str, Any]:
    cur.execute("""select i.membership_id, i.nombre from task t
                     join integrante i on i.membership_id = t.responsable_membership_id
                    where t.id = %s""", (task_id,))
    fila = cur.fetchone()
    return {"membership_id": str(fila["membership_id"]), "nombre": fila["nombre"]}


def _avisar_al_responsable(ctx, hecho: dict, tipo: str, tarea: dict, responsable: dict,
                           hechos: dict[str, Any], *, clave: str) -> None:
    """El aviso de la decisión al responsable: de coordinación, sale enseguida dentro del
    horario, y el hecho dice esa hora (`llega`)."""
    cuando = sale(ctx.calendario, ctx.ahora)
    aviso_id, _ = guardar(
        ctx.cur, ctx.quien.workspace_id, tipo, task_id=tarea["id"],
        destinatario=responsable["membership_id"],
        hechos={"aviso": tipo, "necesita_respuesta": False, "tarea": tarea["titulo"], **hechos},
        programado_para=cuando, clave=clave, ahora=ctx.ahora)
    ctx.avisos_guardados.append(aviso_id)
    hecho["aviso_al_responsable"] = {"a": responsable["nombre"],
                                     fichas.LLEGA: cuando.isoformat()}
    fichas.nombrar_efecto(hecho, "aviso_al_responsable", fichas.AVISO, aviso_id)


def _comentario(datos: dict) -> str | None:
    valor = datos.get("comentario")
    return None if fichas.vacio(valor) else str(valor).strip()


def _tarea(tarea: dict) -> dict[str, str]:
    return {"alias": tarea["alias"], "titulo": tarea["titulo"]}


# --- El cierre que hace el sistema cuando se resuelve lo que faltaba ---------------------------

def cerrar_las_que_ya_pueden(conn: psycopg.Connection, workspace_id: str, reloj: Reloj) -> int:
    """Las tareas en revisión cuya aprobación ya está y que ahora cumplen el resto de lo que pide
    el cierre (`motivo_no_cierra_tarea` sin motivo): el sistema las cierra con esa aprobación
    (`cerrar_tarea_aprobada`, a nombre de quien aprobó) y les avisa al responsable y a quien
    aprobó. Una que se cierra puede destrabar a otra que la esperaba: se vuelve a mirar, con un
    tope. Corre en una transacción de `db.espacio`; quien llama la confirma. Devuelve cuántas
    cerró."""
    ahora = reloj.ahora()
    cerradas = 0
    with espacio(conn, workspace_id) as cur:
        cal = Calendario.desde_base(cur, workspace_id)
        for _ in range(_VUELTAS_DE_CIERRE):
            cur.execute("""select t.id, t.titulo, m.aprobador_membership_id
                             from task t
                             join membership m on m.id = t.responsable_membership_id
                            where t.estado = 'en_revision'
                              and m.aprobador_membership_id is not null
                              and motivo_no_cierra_tarea(t.id) is null
                            order by t.titulo, t.id""")
            listas = cur.fetchall()
            de_esta = 0
            for fila in listas:
                quien = _solicitante(cur, workspace_id, str(fila["aprobador_membership_id"]))
                if quien is None:
                    continue
                r = ejecutar(cur, quien, "cerrar_tarea_aprobada", {"tarea_id": str(fila["id"])})
                if r.get("cerrada"):
                    de_esta += 1
                    _avisar_el_cierre(cur, cal, workspace_id, str(fila["id"]), quien, r, ahora)
            cerradas += de_esta
            if not de_esta:
                break
    return cerradas


def _solicitante(cur, workspace_id: str, membership_id: str) -> Solicitante | None:
    """Quien aprobó, como solicitante del espacio: el cierre corre a su nombre. Si ya no está
    activo, nada se cierra en su nombre."""
    cur.execute("""select app_user_id, membership_id, nombre, area_id from integrante
                    where membership_id = %s and activo""", (membership_id,))
    fila = cur.fetchone()
    if fila is None:
        return None
    return Solicitante(app_user_id=str(fila["app_user_id"]), canal=Canal.ESPACIO,
                       workspace_id=workspace_id, membership_id=str(fila["membership_id"]),
                       nombre=fila["nombre"], area_id=str(fila["area_id"]))


def _avisar_el_cierre(cur, cal, workspace_id: str, task_id: str, quien: Solicitante,
                      r: dict[str, Any], ahora) -> None:
    """El aviso del cierre, al responsable y a quien aprobó: con la aprobación que lo cerró, de
    qué día, y lo que se resolvió. Sale enseguida, dentro del horario."""
    responsable = _responsable(cur, task_id)
    cur.execute("""select o.titulo, o.estado::text estado from dependency d
                     join task o on o.id = d.origen_task_id
                    where d.destino_task_id = %s and d.tipo = 'bloqueante'
                    order by o.titulo""", (task_id,))
    se_resolvio: dict[str, Any] = {}
    esperaba = [{"tarea": f["titulo"], "estado": f["estado"]} for f in cur.fetchall()]
    if esperaba:
        se_resolvio[TAREAS_QUE_ESPERABA] = esperaba
    cur.execute("""select causa from blocker where task_id = %s and resuelto_en >= %s
                    order by resuelto_en""", (task_id, r["aprobada_en"]))
    bloqueos = [f["causa"] for f in cur.fetchall()]
    if bloqueos:
        se_resolvio[BLOQUEOS_QUE_SE_CERRARON] = bloqueos
    el = aprobada_el(cur, {"id": r["aprobacion_id"],
                           "at": datetime.fromisoformat(r["aprobada_en"])}, cal.zona)
    hechos = {"aviso": CERRADA_CON_LA_APROBACION, "necesita_respuesta": False,
              "tarea": r["titulo"], "responsable": responsable["nombre"],
              "aprobada_por": quien.nombre, "aprobada_el": el,
              "quedo_terminada": True, **({"se_resolvio": se_resolvio} if se_resolvio else {})}
    cuando = sale(cal, ahora)
    for destinatario in dict.fromkeys((responsable["membership_id"], quien.membership_id)):
        guardar(cur, workspace_id, CERRADA_CON_LA_APROBACION, task_id=task_id,
                destinatario=destinatario, hechos=hechos, programado_para=cuando,
                clave=f"motor:{CERRADA_CON_LA_APROBACION}:{r['aprobacion_id']}:{destinatario}",
                ahora=ahora)
