"""Las jugadas de las situaciones generales: `elegir`, `corregir`, `cancelar` y
`dejar_para_despues`.

Diseño probado en la Etapa 2 (E2-4; `odd/tasks/prueba-chica-del-motor.md`, sección 4, "Las
ocho situaciones, una vez"); ADR 0018, decisiones 4, 9d y 9f. Valen igual para todas las
fichas: ninguna sabe de qué circuito es la pregunta o el hecho que toca. Lo que es propio de
cada ficha lo declara la ficha (qué pregunta contesta, cómo se deshace lo que anotó,
`fichas.Ficha`); acá sólo se usa.

- **elegir** (situaciones 5, 6 y 7): una opción de una duda, escrita (por su alias) o tocada
  (por su token), por el mismo camino (`elegir_opcion`): cierra la pregunta con esa opción y
  hace la jugada que esperaba, con la opción como dato; si la pregunta ya se cerró, no hace
  nada y los hechos dicen con qué se cerró. Si la opción ya no se puede usar, la pregunta
  sigue abierta y los hechos lo dicen (`pregunta_sigue_abierta`).
- **corregir** (situación 3; 9f): agrega un hecho de corrección, nunca borra: la tarea vuelve a
  como estaba (lo hace el `deshacer` de la ficha) y, si la persona dice cuál era, el hecho va a
  la tarea correcta, con los mismos datos y las mismas comprobaciones de su ficha.
- **cancelar** (situación 4): deja sin efecto la pregunta abierta si se puede dejar; la de
  quién destraba espera respuesta como un pedido de estado (9c) y sigue abierta.
- **dejar_para_despues** (situación 1): la pregunta abierta queda para después, sin cerrarse.
"""

from __future__ import annotations

from typing import Any

from . import preguntas
from .ia import Jugada


def _fichas():
    from . import fichas            # se importan entre sí: fichas declara estas jugadas
    return fichas


# --- elegir ---------------------------------------------------------------------------------

def elegir(ctx, datos: dict, tarea: dict | None) -> dict:
    """Una opción escrita: su alias es de la pregunta abierta. Sin una pregunta abierta con
    opciones, es un toque viejo escrito: los hechos dicen con qué se cerró la última."""
    orden = preguntas.orden_de_alias(datos.get("opcion"))
    abierta = preguntas.actual(ctx.cur, ctx.quien.membership_id)
    opcion = None
    if abierta is not None and orden is not None:
        ctx.cur.execute("""select o.id, o.orden, o.etiqueta, o.valor, o.question_id,
                                  q.membership_id, q.cerrada_en
                             from conversation_option o
                             join conversation_question q on q.id = o.question_id
                            where o.question_id = %s and o.orden = %s""",
                        (abierta["id"], orden))
        opcion = ctx.cur.fetchone()
    if opcion is not None:
        return elegir_opcion(ctx, opcion)
    if abierta is not None and preguntas.opciones(ctx.cur, abierta["id"]):
        # Hay una duda abierta, pero lo elegido no es una de sus opciones.
        return {"resultado": "falta_dato", "falta": ["opcion"]}
    ctx.cur.execute("""select q.id from conversation_question q
                        where q.membership_id = %s and q.cerrada_en is not null
                          and exists (select 1 from conversation_option o
                                       where o.question_id = q.id)
                        order by q.cerrada_en desc limit 1""", (ctx.quien.membership_id,))
    cerrada = ctx.cur.fetchone()
    if cerrada is None:
        return {"resultado": "no_se_puede", "motivo": "sin_opciones"}
    return {"resultado": "sin_efecto", "motivo": "pregunta_cerrada",
            "cerrada_con": preguntas.con_que_se_cerro(ctx, str(cerrada["id"]))}


def elegir_opcion(ctx, opcion: dict[str, Any]) -> dict[str, Any]:
    """El camino de una opción elegida, escrita o tocada (situación general 6)."""
    eligio = {"opcion": preguntas.alias_de_opcion(opcion["orden"]),
              "etiqueta": opcion["etiqueta"]}
    task_id = (opcion["valor"] or {}).get("tarea")
    if task_id:
        eligio["tarea"] = preguntas.tarea_dicha(ctx, task_id)
    pregunta_id = str(opcion["question_id"])
    if opcion["cerrada_en"] is not None:
        # Situación general 7: no hace nada y lo dice, con qué se cerró; nunca en silencio.
        return {"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada",
                "eligio": eligio, "cerrada_con": preguntas.con_que_se_cerro(ctx, pregunta_id)}

    try:
        # La opción queda elegida y la duda cerrada sólo si la jugada que esperaba se pudo
        # correr con ella; si no se puede, el punto de guardado deshace las dos cosas y la
        # duda sigue abierta, con sus opciones (revisión de la E2-4).
        with ctx.cur.connection.transaction():
            hecho = _elegir_y_correr(ctx, opcion, pregunta_id, task_id, eligio)
            if hecho.get("resultado") == "no_se_puede":
                raise _NoSirve(hecho)
    except _NoSirve as no_sirve:
        return {**no_sirve.hecho, "pregunta_sigue_abierta": True}
    return hecho


class _NoSirve(Exception):
    """La opción elegida no se puede usar: lleva los hechos de por qué."""

    def __init__(self, hecho: dict[str, Any]) -> None:
        super().__init__(hecho.get("motivo"))
        self.hecho = hecho


def _elegir_y_correr(ctx, opcion, pregunta_id: str, task_id, eligio: dict) -> dict[str, Any]:
    """Marca la opción, cierra la duda y corre la jugada que esperaba, con la tarea elegida.
    Un dato que todavía falta (la causa de un bloqueo) no la deja abierta: la tarea quedó
    elegida, y lo que falta es la pregunta siguiente, que la ficha abre y los hechos dicen."""
    ctx.cur.execute("update conversation_option set elegida_en = %s where id = %s",
                    (ctx.ahora, opcion["id"]))
    ctx.cur.execute("select jugada from conversation_question where id = %s", (pregunta_id,))
    esperaba = ctx.cur.fetchone()["jugada"] or {}
    preguntas.cerrar(ctx, pregunta_id, "respondida",
                     {"opcion": str(opcion["id"]), "tarea": task_id})
    fichas = _fichas()
    # Una opción puede correr su propia jugada (el "Confirmar" de una entrega), con sus datos y
    # la pregunta que contesta; si no, corre la que esperaba la pregunta, con la tarea elegida.
    valor = opcion["valor"] or {}
    nombre = valor.get("jugada") or esperaba.get("nombre")
    if nombre is None:
        return {"jugada": "elegir", "resultado": "elegida", "eligio": eligio}
    # La jugada que esperaba corre por el manejador de la lista cerrada del turno, el mismo que
    # una jugada escrita, con las comprobaciones de su ficha: la opción no es otra puerta.
    jugadas = ctx.jugadas if ctx.jugadas is not None else fichas.JUGADAS
    manejador = jugadas.get(nombre)
    if manejador is None:
        return {"jugada": nombre, "resultado": "no_se_puede", "motivo": "fuera_de_la_lista",
                "eligio": eligio}
    alias = eligio.get("tarea", {}).get("alias")
    if alias is None:
        # La tarea ya no está abierta entre las de la persona.
        return {"jugada": nombre, "resultado": "no_se_puede", "motivo": "tarea_cerrada",
                "eligio": eligio}
    datos = ({**(valor.get("datos") or {}), "de_la_pregunta": pregunta_id}
             if valor.get("jugada") else dict(esperaba.get("datos") or {}))
    hecho = manejador(ctx, Jugada(nombre, {**datos, "tarea": alias}))
    return {**hecho, "eligio": eligio}


# --- cancelar y dejar para después ----------------------------------------------------------

def cancelar(ctx, datos: dict, tarea: dict | None) -> dict:
    abierta = preguntas.actual(ctx.cur, ctx.quien.membership_id)
    if abierta is None:
        return {"resultado": "no_se_puede", "motivo": "sin_pregunta_abierta"}
    dicha = preguntas.describir(ctx, abierta)
    if not abierta["se_puede_dejar"]:
        return {"resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta",
                "pregunta": dicha}
    preguntas.cerrar(ctx, str(abierta["id"]), "cancelada", {"jugada": "cancelar"})
    return {"resultado": "cancelado", "pregunta": dicha, "no_se_anoto_nada": True}


def dejar_para_despues(ctx, datos: dict, tarea: dict | None) -> dict:
    abierta = preguntas.actual(ctx.cur, ctx.quien.membership_id)
    if abierta is None:
        return {"resultado": "no_se_puede", "motivo": "sin_pregunta_abierta"}
    preguntas.dejar_para_despues(ctx, str(abierta["id"]))
    return {"resultado": "para_despues", "pregunta": preguntas.describir(ctx, abierta)}


# --- corregir -------------------------------------------------------------------------------

def corregir(ctx, datos: dict, tarea: dict) -> dict:
    fichas = _fichas()
    corrige = str(datos["corrige"])
    ficha = fichas.FICHAS.get(corrige)
    if ficha is not None and ficha.corregir is not None:
        # Lo que se corrige es lo que la jugada dejó a la vista (una vista previa) o lo que ya
        # escribió con ella: lo sabe su ficha (la entrega, `entrega.corregir`).
        return ficha.corregir(ctx, datos, tarea)
    if ficha is None or ficha.deshacer is None:
        return {"resultado": "no_se_puede", "motivo": "no_se_corrige", "corrige": corrige}
    correcta = None if fichas.vacio(datos.get("tarea_correcta")) \
        else str(datos["tarea_correcta"]).strip()
    if correcta is not None and correcta == tarea["alias"]:
        return {"resultado": "no_se_puede", "motivo": "misma_tarea",
                "tarea": fichas.tarea_hecho(tarea)}
    if correcta is not None and ctx.tarea(correcta) is None:
        return {"resultado": "no_se_puede", "motivo": "tarea_desconocida", "corrige": corrige}
    if not lo_anoto_hace_poco(ctx, corrige, tarea):
        return {"resultado": "no_se_puede", "motivo": "nada_que_corregir", "corrige": corrige,
                "tarea": fichas.tarea_hecho(tarea)}
    deshecho = ficha.deshacer(ctx, tarea)
    if deshecho is None:
        return {"resultado": "no_se_puede", "motivo": "nada_que_corregir", "corrige": corrige,
                "tarea": fichas.tarea_hecho(tarea)}
    # Lo que esperaba una respuesta sobre el hecho corregido ya no la espera.
    preguntas.cerrar_las_de_una_jugada(ctx, corrige, tarea["id"], "sin_efecto",
                                       {"jugada": "corregir"})
    hecho = {"resultado": "corregido", "corrige": corrige, "tarea": fichas.tarea_hecho(tarea),
             **deshecho["hechos"]}
    if correcta is not None:
        hecho["aplicado"] = fichas.correr(
            ficha, ctx, Jugada(corrige, {**deshecho["datos"], "tarea": correcta}))
    return hecho


def lo_anoto_hace_poco(ctx, corrige: str, tarea: dict) -> bool:
    """Si en sus últimos turnos quedó anotado eso en esa tarea: se corrige lo que la persona
    acaba de decir o lo que Leda tomó mal, no un hecho viejo."""
    for turno in reversed(ctx.ultimos_turnos):
        for hecho in turno.get("hechos") or []:
            for h in (hecho, hecho.get("aplicado") or {}):
                if (h.get("jugada") == corrige and h.get("resultado") == "anotado"
                        and (h.get("tarea") or {}).get("titulo") == tarea["titulo"]):
                    return True
    return False
