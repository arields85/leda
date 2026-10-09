"""Delegar por chat: pasarle una tarea a otra persona (C-7).

ADR 0017, enmienda a la decisión 2 (aceptada por el usuario el 2026-10-09); `odd/tasks/fase-c.md`,
decisión 9; constitución §7 (un cambio de responsable se confirma con una vista previa); mecánica §7
(la re-aprobación de un cambio de responsable la da quien decide) y §12 (auditoría); conversación
38. La regla la hace cumplir la cocina (`herramientas`: `pedir_pase_de_tarea`,
`decidir_pase_de_tarea` y `contestar_pase_de_tarea`; `autoridad.regla_del_pase`) y la base
(`pase_de_tarea`, `cambio_de_responsable`, migración 0045); acá está la conversación.

**Quien pide** (`pedir`, la jugada `pedir_reasignacion`): una tarea suya, asignada, en curso o
trabada, a alguien del equipo; el encargado de un sector, también una de alguien de su sector,
que nombra como la dijo porque no está en su lista (`como_la_nombra`; decisión 27 del usuario,
"pasale la de los sensores de Nahuel a Pedro", con las mismas reglas de quién decide y quién la
toma). El encargado también se queda él con la de alguien de su sector ("la del tornillo de
Nahuel la hago yo"; decisión 53): pide, decide y la toma la misma persona, así que al confirmar la
vista previa la tarea pasa a ser suya. Leda muestra la vista previa (de quién a quién, quién lo
decide si es otra persona y que quien la recibe tiene que tomarla) y espera la confirmación, con el
botón "Confirmar" o escrita,
con la guarda de la decisión 2 (`confirmar`): lo último que la persona vio, en un mensaje
anterior, sin cambios desde entonces (la huella de la cocina). Si no se puede, dice por qué: una
tarea en revisión o terminada no se pasa; un integrante no pasa una tarea a otro sector, y Leda le
dice quién lo decide (el encargado de su sector), sin pasarle el pedido a nadie; la tarea de
alguien de otro sector no la pasa quien no es su encargado.

**Al confirmar**, la cocina anota el pase y Leda le pregunta a quien sigue, como Leda, terminado
el margen para corregir (es por lo que pidió otra persona): a quien decide (el encargado del
sector de quien recibe, `PASE_PARA_DECIDIR`) o, si quien pide es ese encargado, directamente a
quien recibe (`PASE_PARA_TOMAR`); si quien recibe es el encargado, decide con su respuesta. Cada
pregunta sale con dos botones (`TipoDeAviso.opciones`), que no son un tema abierto: se contesta
tocando o escribiendo (`contestar`, la jugada `contestar_el_pase`), porque la tarea está en la
lista de esa persona como un pase que espera su decisión o que la tome (`para_contestar`).

**Cómo termina** (`COMO_TERMINO_EL_PASE`): si quien decide dice que no, o quien recibe no la toma,
la tarea sigue con quien la tenía y Leda se lo dice a quien pidió. Si la toma, cambia el
responsable (la cocina; la fecha, el criterio y la evidencia no cambian, y la revisa quien aprueba
el trabajo de quien era la tarea, decisión 28) y Leda le avisa a quien pidió, a quien decidió y,
si lo pidió su encargado, a quien la tenía. Lo que la escalera tenía guardado para quien la tenía
pasa a quien la tiene, y lo que Leda le preguntaba a quien la tenía sobre esa tarea ya no espera
nada de esa persona. A Dirección no le llega nada.

**Nunca un pase abierto sin que todos sepan cómo terminó** (decisión 39 del usuario; `_al_terminar`,
una regla para todo fin de un pase): cada uno se entera una vez y nunca quien lo terminó; quien
pidió, siempre; quien tenía que contestar y no llegó a hacerlo (se le preguntó y el pase terminó
sin su respuesta: nadie contestó, o la tarea ya no se puede pasar), que ya no hace falta que
conteste; y las preguntas del pase, con sus botones, dejan de esperar.

**A alguien sin Leda conectada** (decisión 37, derivada en la 50 del usuario; C-5b): el pase no se
puede hacer (sin su respuesta no hay pase), a quien pide se le dice, el administrador recibe el
aviso para conectarlo, de verdad, por su canal (`persecucion.avisar_para_que_lo_conecte`), y Leda
le ofrece pasársela a otra persona (`en_cambio_puede`). Nada cambia.

**Si nadie contesta** (`seguir_los_pases`, que corre la escalera; decisión 26 del usuario): la
pregunta a quien decide o a quien recibe se repite una sola vez, el día hábil siguiente de haber
salido (`RECORDATORIO_DEL_PASE`). Si al día hábil siguiente de la repetición, a la hora en que
Leda escribe, sigue sin contestar, el pase termina sin respuesta (la cocina,
`terminar_pase`): la tarea sigue con quien la tenía, y Leda se lo dice a quien lo
pidió, que puede pedírselo a otra persona. La cuenta es de cada pregunta: la de quien recibe
empieza cuando sale, después de la decisión. Una ausencia de quien tiene que contestar la pausa.
Si la tarea ya no se puede pasar (se entregó, se cerró), el pase termina sin efecto en la vuelta
siguiente, sin esperar el plazo.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from ..autoridad import encargado_del_sector, regla_del_pase
from ..herramientas import (EstadoCambio, NecesitaConfirmacion, ejecutar,
                            terminar_pase)

from . import entrega, preguntas
from .ancla import candado
from .avisos import (COMO_TERMINO_EL_PASE, PASE_PARA_DECIDIR, PASE_PARA_TOMAR,
                     RECORDATORIO_DEL_PASE, ausente, guardar, integrante)
from .enlace import NINGUNA_CON_ESE_NOMBRE, misma_palabra, que_nombra
from .fichas import (AVISO, FICHAS, LLEGA, Contexto, _duda, _juntar, integrantes_que_coinciden,
                     nombrar_efecto, nombrar_pregunta, palabras, vacio)
from .margen import sale_con_margen
from .persecucion import (SE_LE_AVISO_AL_ADMINISTRADOR, SIN_TELEGRAM, alcanzable,
                          avisar_para_que_lo_conecte)
from .tiempo import sale

# Lo que Leda ofrece en lugar de un pase a alguien sin Leda conectada (decisión 37; C-5b).
PASARSELA_A_OTRA_PERSONA = "pasarsela_a_otra_persona"
# Los resultados de las jugadas del pase y sus motivos (sus significados, en `hechos.py`).
PASE_PARA_CONFIRMAR = "pase_para_confirmar"
PASE_PEDIDO = "pase_pedido"
NO_HAY_UN_PASE = "no_hay_un_pase"
LA_TAREA_CAMBIO = "la_tarea_cambio"
# La tarea nombrada no es de quien escribe ni de alguien de su sector, si es el encargado
# (decisión 27): no la puede pasar.
NO_ES_DE_SU_SECTOR = "no_es_de_su_sector"
# Los botones de las preguntas a quien decide y a quien recibe: cada uno corre `contestar_el_pase`
# con lo que dice (`acepta`).
BOTONES_PARA_DECIDIR = (("Aprobar el pase", True), ("No aprobarlo", False))
BOTONES_PARA_TOMAR = (("La tomo", True), ("No la tomo", False))
# Lo que la escalera tenía guardado para quien tenía la tarea y pasa a quien la toma.
_DE_LA_ESCALERA = ("aviso_previo", "vencimiento_con_prevision", "pedido_de_estado",
                   "reencuadre", "repregunta_de_estado")
_ABIERTO = ("esperando_decision", "esperando_que_la_tome")
# Los estados en que una tarea se pasa (los de la ficha `pedir_reasignacion`; la regla es de la
# cocina, `herramientas.terminar_pase`): una pregunta de un pase de otra tarea ya no sale.
_SE_PASA = ("asignada", "en_curso", "bloqueada")


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

def pedir(ctx: Contexto, datos: dict, tarea: dict | None) -> dict:
    """La vista previa del pase, o por qué no se puede. Nada se escribe en la tarea. La tarea es
    una de su lista (de la que es responsable: lo comprueba la ficha) o, si no está, la que nombra
    (`como_la_nombra`): una de alguien de su sector, si es el encargado (decisión 27)."""
    if tarea is None:
        dicho = datos.get("como_la_nombra")
        if vacio(dicho) or not que_nombra(str(dicho)):
            return _duda(FICHAS["pedir_reasignacion"], ctx, datos)
        tarea = _la_nombrada(ctx, str(dicho))
        if "resultado" in tarea:
            return tarea
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


def tarea_hecho(tarea: dict) -> dict[str, str]:
    """La tarea en los hechos: con su alias si está en la lista de quien escribe; si no (la de
    alguien de su sector), por su título."""
    return {**({"alias": tarea["alias"]} if tarea.get("alias") else {}),
            "titulo": tarea["titulo"]}


def _la_nombrada(ctx: Contexto, dicho: str) -> dict:
    """La tarea abierta que nombra quien escribe por cómo la dijo: cada palabra que dijo está,
    entera, en su título o en el nombre de quien la tiene (como `enlace`). Cuentan las que quien
    escribe puede pasar: las suyas y, si es el encargado, las de alguien de su sector. Si no hay
    ninguna, o varias, o es de otro sector, el hecho que lo dice (con `resultado`)."""
    cur, yo = ctx.cur, ctx.quien.membership_id
    buscadas = que_nombra(dicho)
    cur.execute("""select t.id::text id, t.titulo, t.estado::text estado,
                          t.responsable_membership_id::text la_tiene_id, i.nombre la_tiene
                     from task t
                     join integrante i on i.membership_id = t.responsable_membership_id
                    where t.estado not in ('terminada', 'cancelada')
                    order by t.fecha_objetivo nulls last, t.titulo, t.id""")
    coinciden = []
    for t in cur.fetchall():
        nombre = palabras(t["titulo"]) + palabras(t["la_tiene"])
        if all(any(misma_palabra(b, n) for n in nombre) for b in buscadas):
            coinciden.append(dict(t))
    if not coinciden:
        return {"resultado": "no_se_puede", "motivo": NINGUNA_CON_ESE_NOMBRE}
    suyas = [t for t in coinciden
             if t["la_tiene_id"] == yo or encargado_del_sector(cur, t["la_tiene_id"]) == yo]
    if not suyas:
        hecho: dict[str, Any] = {"resultado": "no_se_puede", "motivo": NO_ES_DE_SU_SECTOR}
        if len({t["la_tiene"] for t in coinciden}) == 1:
            hecho["la_tiene"] = coinciden[0]["la_tiene"]
        return hecho
    if len(suyas) > 1:
        return {"resultado": "falta_dato", "falta": ["tarea"],
                "coinciden": [{"titulo": t["titulo"], "la_tiene": t["la_tiene"]} for t in suyas]}
    una = suyas[0]
    return {"id": una["id"], "titulo": una["titulo"], "estado": una["estado"]}


def _quien_la_tiene(cur, task_id: str) -> str:
    cur.execute("""select i.nombre from task t
                     join integrante i on i.membership_id = t.responsable_membership_id
                    where t.id = %s""", (task_id,))
    return cur.fetchone()["nombre"]


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
            # Sin Leda conectada, el administrador recibe el aviso para conectarlo y Leda ofrece
            # pasársela a otra persona (decisión 37; C-5b).
            hecho = {"resultado": "no_se_puede", "motivo": motivo, "tarea": tarea_hecho(tarea),
                     "no_se_le_puede_escribir_a": {"a": quien["nombre"] if quien else None,
                                                   "motivo": motivo},
                     "en_cambio_puede": [PASARSELA_A_OTRA_PERSONA]}
            if motivo == SIN_TELEGRAM:
                hecho[SE_LE_AVISO_AL_ADMINISTRADOR] = avisar_para_que_lo_conecte(
                    ctx, quien["nombre"], f"para pasarle la tarea «{tarea['titulo']}»")
            return hecho
    nombre = integrante(cur, recibe)["nombre"]
    al_confirmar: dict[str, Any]
    if recibe == ctx.quien.membership_id == decide:
        # Se queda él con la de alguien de su sector (decisión 53): con su confirmación es suya.
        al_confirmar = {"la_toma_al_confirmar": True}
    else:
        al_confirmar = {"la_tiene_que_tomar": nombre}
        if decide == recibe:
            al_confirmar["decide_y_la_toma"] = True
        elif decide != ctx.quien.membership_id:
            al_confirmar["lo_decide"] = integrante(cur, decide)["nombre"]
    hecho: dict[str, Any] = {"resultado": PASE_PARA_CONFIRMAR, "tarea": tarea_hecho(tarea),
                             "pase": {"la_tiene": _quien_la_tiene(cur, tarea["id"]),
                                      "pasaria_a": nombre},
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
        hecho["pase"] = {"la_tiene": _quien_la_tiene(ctx.cur, tarea["id"]),
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
    tarea = _la_del_pase(ctx, str(q["task_id"]))
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
    if r.get("tomada"):
        # El encargado se quedó él con la de alguien de su sector (decisión 53).
        return _la_tomo(ctx, pase, {"resultado": "anotado", "tarea": tarea_hecho(tarea),
                                    "la_toma": True})
    hecho: dict[str, Any] = {"resultado": PASE_PEDIDO, "tarea": tarea_hecho(tarea),
                             "pase": {"la_tiene": pase["la_tiene"],
                                      "pasaria_a": pase["pasaria_a"]}}
    if pase["estado"] == "esperando_decision" and pase["decide_membership_id"] != \
            pase["a_membership_id"]:
        _juntar(hecho, _preguntar(ctx, pase, PASE_PARA_DECIDIR, pase["decide_membership_id"]))
    else:
        _juntar(hecho, _preguntar(ctx, pase, PASE_PARA_TOMAR, pase["a_membership_id"]))
    return hecho


def _la_del_pase(ctx: Contexto, task_id: str) -> dict | None:
    """La tarea de una vista previa de un pase: de su lista o, si es la de alguien de su sector
    (decisión 27), leída de la base, sin alias. `None` si ya no está abierta."""
    tarea = next((t for t in ctx.tareas if t["id"] == task_id), None)
    if tarea is not None:
        return tarea
    ctx.cur.execute("""select id::text id, titulo, estado::text estado from task
                        where id = %s and estado not in ('terminada', 'cancelada')""",
                    (task_id,))
    fila = ctx.cur.fetchone()
    return dict(fila) if fila else None


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
    # La escalera puede estar terminando este pase (`seguir_los_pases`): el turno la espera y
    # recién entonces lee si el pase sigue esperando algo (`ancla.candado`).
    candado(cur, tarea["id"])
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
            return _ya_no_se_puede_pasar(ctx, pase, tarea)
        hecho: dict[str, Any] = {"resultado": "anotado", "tarea": tarea_hecho(tarea),
                                 "aprobo_el_pase": acepta}
        if acepta:
            _juntar(hecho, _preguntar(ctx, _el_pase(cur, pase["id"]), PASE_PARA_TOMAR,
                                      pase["a_membership_id"]))
            return hecho
        hecho["sigue_con"] = pase["la_tiene"]
        _juntar(hecho, _al_terminar(ctx, pase, {"no_lo_aprobo": True, "lo_decidio": pase["decide"],
                                                "la_tiene": pase["la_tiene"],
                                                **({"por_que": por_que} if por_que else {})}))
        return hecho
    r = ejecutar(cur, ctx.quien, "contestar_pase_de_tarea",
                 {"pase_id": pase["id"], "acepta": acepta, **momento}, ya_confirmada=True)
    if r.get("estado") == "sin_efecto":
        return _ya_no_se_puede_pasar(ctx, pase, tarea)
    tambien = pase["decide_membership_id"] == quien
    hecho = {"resultado": "anotado", "tarea": tarea_hecho(tarea), "la_toma": acepta,
             **({"tambien_lo_decidia": True} if tambien else {})}
    if acepta:
        return _la_tomo(ctx, pase, hecho)
    hecho["sigue_con"] = pase["la_tiene"]
    _juntar(hecho, _al_terminar(ctx, pase, {"la_tomo": False, "la_tiene": pase["la_tiene"],
                                            **({"por_que": por_que} if por_que else {})}))
    return hecho


def _la_tomo(ctx: Contexto, pase: dict, hecho: dict) -> dict:
    """Quien escribe tomó la tarea (o se quedó con la de alguien de su sector): ya es suya, y se
    enteran quienes tienen que enterarse (`_al_terminar`)."""
    _al_cambiar_de_manos(ctx, pase)
    if pase["fecha_objetivo"] is not None:
        hecho["vence"] = pase["fecha_objetivo"].astimezone(ctx.calendario.zona).date().isoformat()
    _juntar(hecho, _al_terminar(ctx, pase, {"la_tomo": True, "la_tiene": ctx.quien.nombre}))
    return hecho


def _ya_no_se_puede_pasar(ctx: Contexto, pase: dict, tarea: dict) -> dict:
    """La tarea cambió (se entregó, se cerró) antes de que quien escribe contestara: el pase quedó
    sin efecto, y se enteran quienes tienen que enterarse."""
    hecho = {"resultado": "no_se_puede", "motivo": LA_TAREA_CAMBIO, "tarea": tarea_hecho(tarea)}
    _juntar(hecho, _al_terminar(ctx, pase, {"la_tarea_cambio": True, "la_tiene": pase["la_tiene"]}))
    return hecho


# --- Cómo terminó: una regla para todo fin de un pase (decisión 39) ----------------------------

def _quienes_se_enteran(pase: dict, termino: dict, *, actor: str | None,
                        preguntado: str | None,
                        para_quien_pidio: dict | None = None) -> list[tuple[str, str, dict]]:
    """A quiénes les llega cómo terminó un pase, con lo propio de cada uno (decisión 39 del
    usuario: nunca un tema abierto sin que todos sepan cómo se cerró). Cada persona una vez, y
    nunca quien lo terminó (`actor`):

    - quien lo pidió, siempre;
    - si alguien la tomó, quien decidió y, si lo pidió su encargado, quien la tenía (decisión 27);
    - quien tenía que contestar y no llegó a hacerlo (`preguntado`: se le preguntó y el pase
      terminó sin su respuesta), que ya no hace falta que conteste."""
    lista: list[tuple[str, str, dict]] = []
    vistos = {actor} if actor else set()

    def sumar(persona: str, clave: str, propio: dict) -> None:
        if persona not in vistos:
            vistos.add(persona)
            lista.append((persona, clave, propio))

    sumar(pase["pedido_por_membership_id"], "aviso_a_quien_pidio", para_quien_pidio or {})
    if termino.get("la_tomo"):
        sumar(pase["decide_membership_id"], "aviso_a_quien_decidio", {})
        sumar(pase["de_membership_id"], "aviso_a_quien_la_tenia",
              {"era_suya": True, "pidio": pase["pidio"]})
    if preguntado is not None:
        sumar(preguntado, "aviso_a_quien_se_le_preguntaba",
              {"ya_no_espera_su_respuesta": True, "pidio": pase["pidio"]})
    return lista


def _cerrar_las_preguntas(cur, pase: dict, ahora) -> None:
    """Las preguntas del pase, con sus botones, dejan de esperar: el pase ya no espera nada de
    nadie (un botón viejo, igual, no hace nada y lo dice: `contestar`)."""
    cur.execute("""update conversation_question
                      set cerrada_en = %s, cierre = 'sin_efecto', cierre_detalle = %s
                    where task_id = %s and tipo = any(%s) and cerrada_en is null
                      and jugada ->> 'pase' = %s""",
                (ahora, preguntas.json_de({"tarea": pase["task_id"],
                                           "el_pase_ya_no_espera": True}),
                 pase["task_id"], [preguntas.DECIDIR_EL_PASE, preguntas.TOMAR_LA_TAREA],
                 pase["id"]))


def _al_terminar(ctx: Contexto, pase: dict, termino: dict) -> dict:
    """El fin de un pase en un turno: quien escribe lo terminó (decidió, contestó o se quedó con
    la tarea); los demás se enteran, terminado el margen para corregir. Los hechos para quien
    escribe."""
    _cerrar_las_preguntas(ctx.cur, pase, ctx.ahora)
    hecho: dict[str, Any] = {}
    for persona, clave, propio in _quienes_se_enteran(pase, termino,
                                                       actor=ctx.quien.membership_id,
                                                       preguntado=None):
        _juntar(hecho, _como_termino(ctx, pase, persona, clave, {**termino, **propio}))
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
    """La pregunta a quien decide (y su repetición) sale mientras el pase espere esa decisión; la
    de quien recibe, mientras espere que la tome; cómo terminó, siempre."""
    from .avisos import de_la_clave       # avisos importa este módulo al salir
    if aviso["tipo"] == COMO_TERMINO_EL_PASE:
        return None, dict(aviso["hechos"])
    m.cur.execute("""select p.estado, p.decide_membership_id, p.a_membership_id,
                             t.estado::text = any(%s)
                               and t.responsable_membership_id = p.de_membership_id se_pasa
                        from pase_de_tarea p join task t on t.id = p.task_id
                       where p.id = %s""", (list(_SE_PASA), de_la_clave(aviso)))
    pase = m.cur.fetchone()
    if pase is None:
        return "tarea_inexistente", {}
    if not pase["se_pasa"]:
        return "el_pase_ya_no_espera", {}       # la tarea cambió: el pase termina sin efecto
    decidir = (aviso["tipo"] == PASE_PARA_DECIDIR
               or (aviso["tipo"] == RECORDATORIO_DEL_PASE
                   and (aviso["hechos"] or {}).get("pregunta") == preguntas.DECIDIR_EL_PASE))
    if _lo_que_espera(pase)[0] != (PASE_PARA_DECIDIR if decidir else PASE_PARA_TOMAR):
        return "el_pase_ya_no_espera", {}
    return None, dict(aviso["hechos"])


def _lo_que_espera(pase) -> tuple[str | None, str | None]:
    """Qué pregunta espera un pase y de quién: la decisión del encargado, o que la tome quien la
    recibe (si es quien decide, decide con su respuesta). `(None, None)` si terminó."""
    if pase["estado"] == "esperando_decision" \
            and str(pase["decide_membership_id"]) != str(pase["a_membership_id"]):
        return PASE_PARA_DECIDIR, str(pase["decide_membership_id"])
    if pase["estado"] in _ABIERTO:
        return PASE_PARA_TOMAR, str(pase["a_membership_id"])
    return None, None


def _el_aviso(cur, tipo: str, pase: dict, resto: str = "") -> dict | None:
    """Un aviso del pase por su clave (la de `_guardar`)."""
    cur.execute("select * from scheduled_notice where dedupe_key = %s",
                (f"motor:{tipo}:{pase['task_id']}:p{pase['id']}{resto}",))
    return cur.fetchone()


def _salio(aviso: dict | None) -> bool:
    """Si un aviso ya salió (o se dio por dado: no se pudo mandar, con su incidente)."""
    return aviso is not None and aviso["estado"] != "guardado" and aviso["resuelto_en"] is not None


def seguir_los_pases(m) -> list[str]:
    """Lo que toca de cada pase que espera una respuesta que no llega (decisión 26 del usuario,
    2026-10-09): la pregunta otra vez, una sola, el día hábil siguiente de haber salido; y, al día
    hábil siguiente de la repetición, a la hora en que Leda escribe, el fin del pase sin
    respuesta. Si la tarea ya no se puede pasar, el fin sin efecto, en cualquier vuelta. Lo
    decide la cocina (`terminar_pase`), y de cómo terminó se enteran todos (`_al_terminar_solo`).
    Corre en la escalera (`escalera.correr_escalera`). Los tipos de lo que guardó."""
    cur = m.cur
    cur.execute("select id from pase_de_tarea where estado = any(%s) order by pedido_en, id",
                (list(_ABIERTO),))
    guardados: list[str] = []
    for fila in cur.fetchall():
        pase = _el_pase(cur, str(fila["id"]))
        tipo, espera_de = _lo_que_espera(pase)
        if tipo is None or not candado(cur, pase["task_id"], esperar=False):
            continue                    # un turno la tiene tomada: la vuelta siguiente
        pregunta = _el_aviso(cur, tipo, pase)
        etapa = f":{tipo}"
        otra_vez = _el_aviso(cur, RECORDATORIO_DEL_PASE, pase, etapa)
        pausado = ausente(cur, espera_de, m.hoy)    # no avanza mientras no está
        vencido = (not pausado and _salio(otra_vez)
                   and m.cal.habiles_entre(otra_vez["resuelto_en"], m.ahora) >= 1
                   and sale(m.cal, m.ahora) <= m.ahora)
        termino = terminar_pase(cur, pase["id"], m.ahora, vencido=vencido)
        if termino is not None:
            _al_terminar_solo(m, pase, termino["estado"], espera_de if _salio(pregunta) else None)
            guardados.append(COMO_TERMINO_EL_PASE)
            continue
        if pausado or not _salio(pregunta) or otra_vez is not None:
            continue                    # todavía no se le preguntó, o ya se repitió
        if m.cal.habiles_entre(pregunta["resuelto_en"], m.ahora) >= 1:
            _repetir(m, pase, tipo, espera_de, pregunta, etapa)
            guardados.append(RECORDATORIO_DEL_PASE)
    return guardados


def _repetir(m, pase: dict, tipo: str, espera_de: str, pregunta: dict, etapa: str) -> None:
    """La pregunta del pase otra vez, con lo mismo que la primera, cuándo se le preguntó y qué
    pasa si sigue sin contestar: el día hábil siguiente, la tarea sigue con quien la tiene."""
    hechos = {"aviso": RECORDATORIO_DEL_PASE, "tarea": pase["titulo"],
              **hechos_de_la_pregunta(pase, tipo, m.cal.zona),
              "se_lo_pregunto_el": m.fecha(pregunta["resuelto_en"]).isoformat(),
              "si_sigue_sin_contestar": {
                  "sigue_con": pase["la_tiene"],
                  "fecha": m.cal.proximo_habil(m.hoy + timedelta(days=1)).isoformat()}}
    guardar(m.cur, m.workspace_id, RECORDATORIO_DEL_PASE, task_id=pase["task_id"],
            destinatario=espera_de, hechos=hechos, programado_para=sale(m.cal, m.ahora),
            clave=f"motor:{RECORDATORIO_DEL_PASE}:{pase['task_id']}:p{pase['id']}{etapa}",
            ahora=m.ahora)


def _al_terminar_solo(m, pase: dict, estado: str, preguntado: str | None) -> None:
    """El fin de un pase que da el sistema (`seguir_los_pases`): sin respuesta, la tarea sigue con
    quien la tiene y quien lo pidió puede pedírselo a otra persona; sin efecto, la tarea cambió.
    Se enteran todos (`_quienes_se_enteran`), también a quien se le preguntaba, que ya no hace
    falta que conteste. Información, a la hora en que Leda escribe."""
    _cerrar_las_preguntas(m.cur, pase, m.ahora)
    if estado == "sin_respuesta":
        termino = {"sin_respuesta": True, "la_tiene": pase["la_tiene"]}
        para_quien_pidio = {"no_contesto": integrante(m.cur, preguntado)["nombre"],
                            "puede_pedirselo_a_otra_persona": True} if preguntado else {}
    else:
        termino = {"la_tarea_cambio": True, "la_tiene": pase["la_tiene"]}
        para_quien_pidio = {}
    for persona, clave, propio in _quienes_se_enteran(pase, termino, actor=None,
                                                       preguntado=preguntado,
                                                       para_quien_pidio=para_quien_pidio):
        guardar(m.cur, m.workspace_id, COMO_TERMINO_EL_PASE, task_id=pase["task_id"],
                destinatario=persona,
                hechos={"aviso": COMO_TERMINO_EL_PASE, "tarea": pase["titulo"],
                        "necesita_respuesta": False, "pasaria_a": pase["pasaria_a"],
                        **termino, **propio},
                programado_para=sale(m.cal, m.ahora),
                clave=f"motor:{COMO_TERMINO_EL_PASE}:{pase['task_id']}:p{pase['id']}:{clave}",
                ahora=m.ahora)


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
