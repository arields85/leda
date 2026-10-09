"""Delegar por chat: pasarle una tarea a otra persona (C-7).

ADR 0017, enmienda a la decisión 2 (aceptada por el usuario el 2026-10-09); `odd/tasks/fase-c.md`,
decisión 9; constitución §7 (un cambio de responsable se confirma con una vista previa); mecánica §7
(la re-aprobación de un cambio de responsable la da quien decide) y §12 (auditoría); conversación
38. La regla la hace cumplir la cocina (`herramientas`: `pedir_pase_de_tarea`,
`decidir_pase_de_tarea` y `contestar_pase_de_tarea`; `autoridad.regla_del_pase`) y la base
(`pase_de_tarea`, `cambio_de_responsable`, migración 0045); acá está la conversación.

**Quien pide** (`pedir`, la jugada `pedir_reasignacion`): una tarea suya, asignada, en curso o
trabada, a alguien del equipo. Leda muestra la vista previa (de quién a quién, quién lo decide si
es otra persona y que quien la recibe tiene que tomarla) y espera la confirmación, con el botón
"Confirmar" o escrita, con la guarda de la decisión 2 (`confirmar`): lo último que la persona vio,
en un mensaje anterior, sin cambios desde entonces (la huella de la cocina). Si no se puede, dice
por qué: una tarea en revisión o terminada no se pasa; un integrante no pasa una tarea a otro
sector, y Leda le dice quién lo decide (el encargado de su sector), sin pasarle el pedido a nadie.

**Al confirmar**, la cocina anota el pase y Leda le pregunta a quien sigue, como Leda, terminado
el margen para corregir (es por lo que pidió otra persona): a quien decide (el encargado del
sector de quien recibe, `PASE_PARA_DECIDIR`) o, si quien pide es ese encargado, directamente a
quien recibe (`PASE_PARA_TOMAR`); si quien recibe es el encargado, decide con su respuesta. Cada
pregunta sale con dos botones (`TipoDeAviso.opciones`), que no son un tema abierto: se contesta
tocando o escribiendo (`contestar`, la jugada `contestar_el_pase`), porque la tarea está en la
lista de esa persona como un pase que espera su decisión o que la tome (`para_contestar`).

**Cómo termina** (`COMO_TERMINO_EL_PASE`): si quien decide dice que no, o quien recibe no la toma,
la tarea sigue con quien la tenía y Leda se lo dice a quien pidió. Si la toma, cambia el
responsable (la cocina; la fecha, el criterio y la evidencia no cambian, y el trabajo lo sigue
revisando quien lo revisaba) y Leda le avisa a quien pidió y, si es otra persona, a quien decidió.
Lo que la escalera tenía guardado para quien la tenía pasa a quien la tiene, y lo que Leda le
preguntaba a quien la tenía sobre esa tarea ya no espera nada de esa persona. A Dirección no le
llega nada.
"""

from __future__ import annotations

from typing import Any

from ..autoridad import regla_del_pase
from ..herramientas import EstadoCambio, NecesitaConfirmacion, ejecutar

from . import entrega, preguntas
from .avisos import COMO_TERMINO_EL_PASE, PASE_PARA_DECIDIR, PASE_PARA_TOMAR, guardar, integrante
from .fichas import (AVISO, LLEGA, Contexto, _juntar, integrantes_que_coinciden, nombrar_efecto,
                     nombrar_pregunta, tarea_hecho, vacio)
from .margen import sale_con_margen
from .persecucion import alcanzable

# Los resultados de las jugadas del pase y sus motivos (sus significados, en `hechos.py`).
PASE_PARA_CONFIRMAR = "pase_para_confirmar"
PASE_PEDIDO = "pase_pedido"
NO_HAY_UN_PASE = "no_hay_un_pase"
LA_TAREA_CAMBIO = "la_tarea_cambio"
# Los botones de las preguntas a quien decide y a quien recibe: cada uno corre `contestar_el_pase`
# con lo que dice (`acepta`).
BOTONES_PARA_DECIDIR = (("Aprobar el pase", True), ("No aprobarlo", False))
BOTONES_PARA_TOMAR = (("La tomo", True), ("No la tomo", False))
# Lo que la escalera tenía guardado para quien tenía la tarea y pasa a quien la toma.
_DE_LA_ESCALERA = ("aviso_previo", "vencimiento_con_prevision", "pedido_de_estado",
                   "reencuadre", "repregunta_de_estado")
_ABIERTO = ("esperando_decision", "esperando_que_la_tome")


# --- Lo que ve quien decide o recibe -------------------------------------------------------------

def para_contestar(cur, membership_id: str, desde: int) -> tuple[dict[str, Any], ...]:
    """Las tareas de otras personas cuyo pase espera algo de quien escribe: su decisión
    (`espera_su_decision_del_pase`) o que la tome (`espera_que_la_tome`), con su alias (siguiendo
    los anteriores, desde `desde`), quién la pidió pasar, quién la tiene y a quién pasaría. No son
    tareas suyas todavía."""
    cur.execute(
        """select t.id, t.titulo, t.estado::text estado, t.fecha_objetivo,
                  p.decide_membership_id, p.a_membership_id, p.estado pase,
                  pide.nombre pidio, tiene.nombre la_tiene, recibe.nombre pasaria_a
             from pase_de_tarea p
             join task t on t.id = p.task_id
             join integrante pide on pide.membership_id = p.pedido_por_membership_id
             join integrante tiene on tiene.membership_id = p.de_membership_id
             join integrante recibe on recibe.membership_id = p.a_membership_id
            where p.estado = any(%s)
              and ((p.estado = 'esperando_decision' and p.decide_membership_id = %s)
                   or (p.a_membership_id = %s
                       and (p.estado = 'esperando_que_la_tome'
                            or p.decide_membership_id = p.a_membership_id)))
            order by t.fecha_objetivo nulls last, t.titulo""",
        (list(_ABIERTO), membership_id, membership_id))
    lista = []
    for i, f in enumerate(cur.fetchall(), desde + 1):
        una: dict[str, Any] = {
            "alias": f"T{i}", "id": str(f["id"]), "titulo": f["titulo"], "estado": f["estado"],
            "fecha_objetivo": f["fecha_objetivo"].isoformat() if f["fecha_objetivo"] else None,
            "pidio": f["pidio"], "la_tiene": f["la_tiene"]}
        if str(f["a_membership_id"]) == membership_id:
            una["espera_que_la_tome"] = True
            if str(f["decide_membership_id"]) == membership_id:
                una["tambien_lo_decide"] = True
        else:
            una["espera_su_decision_del_pase"] = True
            una["pasaria_a"] = f["pasaria_a"]
        lista.append(una)
    return tuple(lista)


# --- Pedirlo: la vista previa ------------------------------------------------------------------

def pedir(ctx: Contexto, datos: dict, tarea: dict) -> dict:
    """La vista previa del pase, o por qué no se puede. Nada se escribe en la tarea."""
    if vacio(datos.get("a")):
        return {"resultado": "falta_dato", "falta": ["a"], "tarea": tarea_hecho(tarea)}
    coinciden = integrantes_que_coinciden(ctx.cur, str(datos["a"]).strip())
    if len(coinciden) > 1:
        return {"resultado": "falta_dato", "falta": ["a"], "tarea": tarea_hecho(tarea),
                "coinciden": [c["nombre"] for c in coinciden]}
    if not coinciden:
        return {"resultado": "no_se_puede", "motivo": "persona_desconocida",
                "tarea": tarea_hecho(tarea)}
    return _mostrar(ctx, tarea, str(coinciden[0]["membership_id"]))


def _mostrar(ctx: Contexto, tarea: dict, recibe: str) -> dict:
    """La cocina comprueba el pedido sin escribir nada (su preparación): si vale, la vista previa
    queda como lo último mostrado para confirmar, con su huella; si no, por qué."""
    cur = ctx.cur
    try:
        r = ejecutar(cur, ctx.quien, "pedir_pase_de_tarea",
                     {"tarea_id": tarea["id"], "a_membership_id": recibe})
    except NecesitaConfirmacion as e:
        huella = e.huella
    else:
        return _no_se_puede(ctx, r, tarea)
    decide = regla_del_pase(cur, ctx.quien.membership_id, recibe).decide
    for persona in dict.fromkeys(p for p in (recibe, decide) if p != ctx.quien.membership_id):
        quien, motivo = alcanzable(cur, persona)
        if motivo is not None:
            # A quien no tiene un chat con Leda no se le puede preguntar: sin su respuesta, el
            # pase no se puede hacer (constitución §7: nunca se promete un mensaje que no sale).
            return {"resultado": "no_se_puede", "motivo": motivo, "tarea": tarea_hecho(tarea),
                    "no_se_le_puede_escribir_a": {"a": quien["nombre"] if quien else None,
                                                  "motivo": motivo}}
    nombre = integrante(cur, recibe)["nombre"]
    al_confirmar: dict[str, Any] = {"la_tiene_que_tomar": nombre}
    if decide == recibe:
        al_confirmar["decide_y_la_toma"] = True
    elif decide != ctx.quien.membership_id:
        al_confirmar["lo_decide"] = integrante(cur, decide)["nombre"]
    hecho: dict[str, Any] = {"resultado": PASE_PARA_CONFIRMAR, "tarea": tarea_hecho(tarea),
                             "pase": {"la_tiene": ctx.quien.nombre, "pasaria_a": nombre},
                             "al_confirmar_el_pase": al_confirmar}
    # Una vista previa anterior de un pase de esta tarea deja de valer: la reemplaza ésta.
    preguntas.cerrar_de_tipo(ctx, preguntas.CONFIRMAR_EL_PASE, tarea["id"], "sin_efecto",
                             {"reemplazada": True, "tarea": tarea["id"]})
    ahora, pregunta_id = preguntas.abrir_con_id(
        ctx, preguntas.CONFIRMAR_EL_PASE, tarea["id"],
        jugada={"nombre": "pedir_reasignacion", "a_membership_id": recibe, "huella": huella},
        opciones=[(entrega.BOTON_CONFIRMAR, {"tarea": tarea["id"], "jugada": "confirmar"})])
    entrega.que_sea_lo_mostrado(ctx, pregunta_id, huella)
    nombrar_pregunta(hecho, "pregunta" if ahora else "pregunta_para_despues",
                     preguntas.CONFIRMAR_EL_PASE, pregunta_id)
    return hecho


def _no_se_puede(ctx: Contexto, rechazo: dict, tarea: dict) -> dict:
    """Un rechazo de la cocina, en hechos: nunca su texto ni un id."""
    motivo = str(rechazo.get("error"))
    hecho: dict[str, Any] = {"resultado": "no_se_puede", "motivo": motivo,
                             "tarea": tarea_hecho(tarea)}
    if motivo == "estado":
        hecho["estado"] = rechazo.get("estado")
    if rechazo.get("lo_decide"):
        # Un integrante pidió pasarla a otro sector: lo decide el encargado de su sector, una
        # persona concreta (ADR 0017, decisión 1). No se le pasa el pedido.
        hecho["quien_decide"] = integrante(ctx.cur, rechazo["lo_decide"])["nombre"]
    if rechazo.get("pase_id"):
        ctx.cur.execute("""select i.nombre from pase_de_tarea p
                             join integrante i on i.membership_id = p.a_membership_id
                            where p.id = %s""", (rechazo["pase_id"],))
        fila = ctx.cur.fetchone()
        hecho["pase"] = {"la_tiene": ctx.quien.nombre,
                         "pasaria_a": fila["nombre"] if fila else None}
    return hecho


# --- Confirmarlo -------------------------------------------------------------------------------

def la_que_se_confirma(ctx: Contexto, datos: dict, tarea: dict | None) -> dict | None:
    """La vista previa de un pase que confirma la persona, si es eso lo que confirma: la del botón
    que tocó; o, escrito, la de la tarea que nombra o la que está abierta. Si no, `None` (la
    confirmación es de una entrega, `entrega.confirmar`)."""
    cur = ctx.cur
    tocada = datos.get("de_la_pregunta")
    if tocada:
        cur.execute("select * from conversation_question where id = %s", (tocada,))
        q = cur.fetchone()
        return q if q is not None and q["tipo"] == preguntas.CONFIRMAR_EL_PASE else None
    if tarea is not None:
        cur.execute("""select * from conversation_question
                        where membership_id = %s and tipo = %s and task_id = %s
                          and cerrada_en is null
                        order by abierta_en desc limit 1""",
                    (ctx.quien.membership_id, preguntas.CONFIRMAR_EL_PASE, tarea["id"]))
        return cur.fetchone()
    abierta = preguntas.actual(cur, ctx.quien.membership_id)
    if abierta is not None and abierta["tipo"] == preguntas.CONFIRMAR_EL_PASE:
        return abierta
    return None


def confirmar(ctx: Contexto, datos: dict, q: dict) -> dict:
    """La confirmación de la vista previa del pase, tocada o escrita. Escrita vale la guarda de la
    decisión 2: lo último que la persona vio, en un mensaje anterior. Tocada o escrita, la cocina
    comprueba que no cambió nada desde la vista previa (su huella); si cambió, Leda la muestra de
    nuevo y no pide nada."""
    cur = ctx.cur
    tarea = next((t for t in ctx.tareas if t["id"] == str(q["task_id"])), None)
    tocada = bool(datos.get("de_la_pregunta"))
    # Un botón tocado ya cerró su pregunta al elegirse (`situaciones.elegir_opcion`); escrita, la
    # vista previa tiene que seguir abierta.
    if tarea is None or (q["cerrada_en"] is not None and not tocada):
        return {"resultado": "no_se_puede", "motivo": entrega.NADA_PARA_CONFIRMAR}
    jugada = q["jugada"] or {}
    if not tocada:
        mostrada, _ = entrega.lo_mostrado(ctx)
        vigente = preguntas.actual(cur, ctx.quien.membership_id)
        if (mostrada != str(q["id"]) or vigente is None or str(vigente["id"]) != str(q["id"])
                or str(q["id"]) in ctx.preguntas_del_turno):
            return {"resultado": entrega.NO_VALE_LA_CONFIRMACION,
                    "motivo": entrega.NO_ES_LO_ULTIMO_QUE_VIO, "tarea": tarea_hecho(tarea),
                    "como_queda": PASE_PARA_CONFIRMAR}
    try:
        r = ejecutar(cur, ctx.quien, "pedir_pase_de_tarea",
                     {"tarea_id": tarea["id"], "a_membership_id": jugada["a_membership_id"],
                      "at": ctx.ahora.isoformat()},
                     ya_confirmada=True, huella_previa=jugada.get("huella"))
    except EstadoCambio:
        hecho = _mostrar(ctx, _vigente(ctx, tarea), jugada["a_membership_id"])
        hecho.update({"resultado": entrega.NO_VALE_LA_CONFIRMACION,
                      "motivo": entrega.CAMBIO_LO_QUE_SE_MOSTRO,
                      "como_queda": hecho.pop("resultado")})
        return hecho
    if "error" in r:
        if q["cerrada_en"] is None:
            preguntas.cerrar(ctx, str(q["id"]), "sin_efecto", {"tarea": tarea["id"]})
        entrega.que_sea_lo_mostrado(ctx, None, None)
        return _no_se_puede(ctx, r, tarea)
    if q["cerrada_en"] is None:
        preguntas.cerrar(ctx, str(q["id"]), "respondida",
                         {"jugada": "confirmar", "tarea": tarea["id"]})
    entrega.que_sea_lo_mostrado(ctx, None, None)
    pase = _el_pase(cur, r["pase_id"])
    hecho: dict[str, Any] = {"resultado": PASE_PEDIDO, "tarea": tarea_hecho(tarea),
                             "pase": {"la_tiene": ctx.quien.nombre,
                                      "pasaria_a": pase["pasaria_a"]}}
    if pase["estado"] == "esperando_decision" and pase["decide_membership_id"] != \
            pase["a_membership_id"]:
        _juntar(hecho, _preguntar(ctx, pase, PASE_PARA_DECIDIR, pase["decide_membership_id"]))
    else:
        _juntar(hecho, _preguntar(ctx, pase, PASE_PARA_TOMAR, pase["a_membership_id"]))
    return hecho


def _vigente(ctx: Contexto, tarea: dict) -> dict:
    """La tarea con su estado de ahora (otra jugada del mismo mensaje pudo cambiarlo)."""
    ctx.cur.execute("select estado::text estado from task where id = %s", (tarea["id"],))
    return {**tarea, "estado": ctx.cur.fetchone()["estado"]}


def _el_pase(cur, pase_id: str) -> dict:
    """Un pase con los nombres de quién lo pidió, quién la tiene, a quién pasaría y quién decide."""
    cur.execute(
        """select p.*, t.titulo, t.fecha_objetivo, t.estado::text estado_de_la_tarea,
                  pide.nombre pidio, tiene.nombre la_tiene, recibe.nombre pasaria_a,
                  decide.nombre decide
             from pase_de_tarea p
             join task t on t.id = p.task_id
             join integrante pide on pide.membership_id = p.pedido_por_membership_id
             join integrante tiene on tiene.membership_id = p.de_membership_id
             join integrante recibe on recibe.membership_id = p.a_membership_id
             join integrante decide on decide.membership_id = p.decide_membership_id
            where p.id = %s""", (str(pase_id),))
    pase = dict(cur.fetchone())
    for clave in ("id", "task_id", "de_membership_id", "a_membership_id",
                  "pedido_por_membership_id", "decide_membership_id"):
        pase[clave] = str(pase[clave])
    return pase


# --- Las preguntas a quien decide y a quien recibe, y cómo terminó ------------------------------

def _guardar(ctx: Contexto, pase: dict, tipo: str, destinatario: str, hechos: dict,
             clave: str) -> tuple[str, Any]:
    """Un aviso del pase, terminado el margen para corregir: lo causa lo que dijo otra persona."""
    sale = sale_con_margen(ctx.cur, ctx.calendario, ctx.quien.workspace_id, ctx.ahora)
    aviso_id, _ = guardar(
        ctx.cur, ctx.quien.workspace_id, tipo, task_id=pase["task_id"], destinatario=destinatario,
        hechos={"aviso": tipo, "tarea": pase["titulo"], **hechos}, programado_para=sale,
        clave=f"motor:{tipo}:{pase['task_id']}:p{pase['id']}{clave}", ahora=ctx.ahora)
    ctx.avisos_guardados.append(aviso_id)
    return aviso_id, sale


def hechos_de_la_pregunta(pase: dict, tipo: str, zona) -> dict[str, Any]:
    """Lo que lleva la pregunta del pase a quien decide o a quien recibe."""
    hechos: dict[str, Any] = {
        "necesita_respuesta": True,
        "pregunta": (preguntas.DECIDIR_EL_PASE if tipo == PASE_PARA_DECIDIR
                     else preguntas.TOMAR_LA_TAREA),
        "pidio": pase["pidio"], "la_tiene": pase["la_tiene"]}
    if pase["fecha_objetivo"] is not None:
        hechos["vence"] = pase["fecha_objetivo"].astimezone(zona).date().isoformat()
    if tipo == PASE_PARA_DECIDIR:
        hechos["pasaria_a"] = pase["pasaria_a"]
    elif pase["decide_membership_id"] == pase["a_membership_id"]:
        hechos["tambien_lo_decide"] = True
    elif pase["decide_membership_id"] != pase["pedido_por_membership_id"]:
        hechos["lo_aprobo"] = pase["decide"]
    return hechos


def _preguntar(ctx: Contexto, pase: dict, tipo: str, a: str) -> dict:
    """La pregunta a quien decide o a quien recibe, como Leda; los hechos para quien escribe."""
    aviso_id, sale = _guardar(ctx, pase, tipo, a,
                              hechos_de_la_pregunta(pase, tipo, ctx.calendario.zona), "")
    hecho: dict[str, Any] = {"le_pregunta_a": {"a": integrante(ctx.cur, a)["nombre"],
                                               LLEGA: sale.isoformat()}}
    nombrar_efecto(hecho, "le_pregunta_a", AVISO, aviso_id)
    return hecho


def _como_termino(ctx: Contexto, pase: dict, a: str, clave: str, hechos: dict) -> dict:
    """Cómo terminó el pase, a quien pidió o a quien decidió: información."""
    aviso_id, sale = _guardar(ctx, pase, COMO_TERMINO_EL_PASE, a,
                              {"necesita_respuesta": False, "pasaria_a": pase["pasaria_a"],
                               **hechos}, f":{clave}")
    hecho = {clave: {"a": integrante(ctx.cur, a)["nombre"], LLEGA: sale.isoformat()}}
    nombrar_efecto(hecho, clave, AVISO, aviso_id)
    return hecho


# --- Contestarlo: quien decide y quien recibe ------------------------------------------------------

def contestar(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    """Quien decide dice si lo aprueba; quien recibe, si la toma (con su "sí", si es quien
    decide, vale por las dos). La cocina lo anota y, si la toma, cambia el responsable."""
    cur, quien = ctx.cur, ctx.quien.membership_id
    if tarea is None:
        if len(ctx.pases) > 1:
            return {"resultado": "falta_dato", "falta": ["tarea"]}
        tarea = ctx.pases[0] if ctx.pases else None
    if tarea is None or not any(t["id"] == tarea["id"] for t in ctx.pases):
        return {"resultado": "no_se_puede", "motivo": NO_HAY_UN_PASE,
                **({"tarea": tarea_hecho(tarea)} if tarea else {})}
    acepta = datos.get("acepta")
    if not isinstance(acepta, bool):
        return {"resultado": "falta_dato", "falta": ["acepta"], "tarea": tarea_hecho(tarea)}
    cur.execute("""select id from pase_de_tarea where task_id = %s and estado = any(%s)
                    order by pedido_en desc limit 1""", (tarea["id"], list(_ABIERTO)))
    fila = cur.fetchone()
    if fila is None or (datos.get("pase") and str(datos["pase"]) != str(fila["id"])):
        # El botón de un pase que ya terminó: no hace nada y lo dice.
        return {"resultado": "no_se_puede", "motivo": NO_HAY_UN_PASE,
                "tarea": tarea_hecho(tarea)}
    pase = _el_pase(cur, str(fila["id"]))
    por_que = None if vacio(datos.get("por_que")) else str(datos["por_que"]).strip()
    momento = {"at": ctx.ahora.isoformat(), **({"motivo": por_que} if por_que else {})}
    if pase["decide_membership_id"] == quien and pase["a_membership_id"] != quien:
        r = ejecutar(cur, ctx.quien, "decidir_pase_de_tarea",
                     {"pase_id": pase["id"], "aprueba": acepta, **momento}, ya_confirmada=True)
        if r.get("estado") == "sin_efecto":
            return {"resultado": "no_se_puede", "motivo": LA_TAREA_CAMBIO,
                    "tarea": tarea_hecho(tarea)}
        hecho: dict[str, Any] = {"resultado": "anotado", "tarea": tarea_hecho(tarea),
                                 "aprobo_el_pase": acepta}
        if acepta:
            _juntar(hecho, _preguntar(ctx, _el_pase(cur, pase["id"]), PASE_PARA_TOMAR,
                                      pase["a_membership_id"]))
            return hecho
        hecho["sigue_con"] = pase["la_tiene"]
        _juntar(hecho, _como_termino(ctx, pase, pase["pedido_por_membership_id"],
                                     "aviso_a_quien_pidio",
                                     {"no_lo_aprobo": True, "lo_decidio": pase["decide"],
                                      "la_tiene": pase["la_tiene"],
                                      **({"por_que": por_que} if por_que else {})}))
        return hecho
    r = ejecutar(cur, ctx.quien, "contestar_pase_de_tarea",
                 {"pase_id": pase["id"], "acepta": acepta, **momento}, ya_confirmada=True)
    if r.get("estado") == "sin_efecto":
        return {"resultado": "no_se_puede", "motivo": LA_TAREA_CAMBIO,
                "tarea": tarea_hecho(tarea)}
    tambien = pase["decide_membership_id"] == quien
    hecho = {"resultado": "anotado", "tarea": tarea_hecho(tarea), "la_toma": acepta,
             **({"tambien_lo_decidia": True} if tambien else {})}
    if acepta:
        _al_cambiar_de_manos(ctx, pase)
        if pase["fecha_objetivo"] is not None:
            hecho["vence"] = pase["fecha_objetivo"].astimezone(
                ctx.calendario.zona).date().isoformat()
        termino = {"la_tomo": True, "la_tiene": ctx.quien.nombre}
    else:
        hecho["sigue_con"] = pase["la_tiene"]
        termino = {"la_tomo": False, "la_tiene": pase["la_tiene"],
                   **({"por_que": por_que} if por_que else {})}
    _juntar(hecho, _como_termino(ctx, pase, pase["pedido_por_membership_id"],
                                 "aviso_a_quien_pidio", termino))
    if acepta and pase["decide_membership_id"] not in (pase["pedido_por_membership_id"], quien):
        _juntar(hecho, _como_termino(ctx, pase, pase["decide_membership_id"],
                                     "aviso_a_quien_decidio", termino))
    return hecho


def _al_cambiar_de_manos(ctx: Contexto, pase: dict) -> None:
    """La tarea ya es de quien la tomó: lo que Leda le preguntaba a quien la tenía sobre ella ya
    no espera nada de esa persona, y lo que la escalera tenía guardado para quien la tenía y no
    salió le llega a quien la tiene (su vigencia lo exige: va al responsable)."""
    cur, anterior, task_id = ctx.cur, pase["de_membership_id"], pase["task_id"]
    cur.execute("""update conversation_question
                      set cerrada_en = %s, cierre = 'sin_efecto', cierre_detalle = %s
                    where membership_id = %s and task_id = %s and cerrada_en is null
                returning id""",
                (ctx.ahora, preguntas.json_de({"tarea": task_id, "cambio_quien_la_tiene": True}),
                 anterior, task_id))
    cerradas = [str(f["id"]) for f in cur.fetchall()]
    cur.execute("""update conversation_state set pregunta_abierta_id = null, actualizado_en = %s
                    where membership_id = %s and pregunta_abierta_id = any(%s::uuid[])""",
                (ctx.ahora, anterior, cerradas))
    cur.execute("""update pending_reply set satisfecho_en = %s
                    where membership_id = %s and task_id = %s and satisfecho_en is null""",
                (ctx.ahora, anterior, task_id))
    cur.execute("""update scheduled_notice set destinatario_membership_id = %s
                    where task_id = %s and destinatario_membership_id = %s
                      and estado = 'guardado' and tipo = any(%s)""",
                (ctx.quien.membership_id, task_id, anterior, list(_DE_LA_ESCALERA)))


# --- Lo que un aviso del pase necesita al salir ---------------------------------------------------

def vigencia(m, aviso) -> tuple[str | None, dict[str, Any]]:
    """La pregunta a quien decide sale mientras el pase espere esa decisión; la de quien recibe,
    mientras espere que la tome; cómo terminó, siempre."""
    from .avisos import de_la_clave       # avisos importa este módulo al salir
    if aviso["tipo"] == COMO_TERMINO_EL_PASE:
        return None, dict(aviso["hechos"])
    m.cur.execute("""select estado, decide_membership_id, a_membership_id from pase_de_tarea
                      where id = %s""", (de_la_clave(aviso),))
    pase = m.cur.fetchone()
    if pase is None:
        return "tarea_inexistente", {}
    espera = (pase["estado"] == "esperando_decision" if aviso["tipo"] == PASE_PARA_DECIDIR
              else pase["estado"] == "esperando_que_la_tome"
              or (pase["estado"] == "esperando_decision"
                  and pase["decide_membership_id"] == pase["a_membership_id"]))
    if not espera:
        return "el_pase_ya_no_espera", {}
    return None, dict(aviso["hechos"])


def opciones(m, aviso) -> tuple[str, dict[str, Any], list[tuple[str, dict[str, Any]]]]:
    """La decisión que ofrece la pregunta del pase al salir, con sus dos botones."""
    from .avisos import de_la_clave
    task_id, pase_id = str(aviso["task_id"]), de_la_clave(aviso)
    tipo, botones = ((preguntas.DECIDIR_EL_PASE, BOTONES_PARA_DECIDIR)
                     if aviso["tipo"] == PASE_PARA_DECIDIR
                     else (preguntas.TOMAR_LA_TAREA, BOTONES_PARA_TOMAR))
    return tipo, {"nombre": "contestar_el_pase", "del_aviso": str(aviso["id"]),
                  "pase": pase_id}, [
        (etiqueta, {"tarea": task_id, "jugada": "contestar_el_pase",
                    "datos": {"acepta": acepta, "pase": pase_id}})
        for etiqueta, acepta in botones]
