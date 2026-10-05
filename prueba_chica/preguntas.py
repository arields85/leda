"""Las preguntas de Leda y sus opciones (E2-4).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Las ocho situaciones, una vez"); ADR 0018,
decisiones 3, 4 y 9d. Una pregunta es lo que Leda espera de la persona para completar algo
que ella empezó: la causa de un bloqueo, quién lo destraba, de qué tarea habla. Se guarda en
`conversation_question` con la jugada que espera (`jugada`) y, si es una duda, sus opciones en
`conversation_option`, cada una con un token único: lo único que vuelve con un toque.

Un tema a la vez, para todas las fichas igual:

- **La pregunta abierta** es la de `conversation_state.pregunta_abierta_id`; las demás sin
  cerrar están **para después** (`para_despues_en`).
- **Abrir una:** si no hay otra abierta, queda abierta. Si la abierta salió en este mismo
  mensaje, la nueva queda para después: de a una, en el orden en que la persona las dijo
  (situación general 2). Si la abierta es de antes, Leda sigue a la persona: pregunta lo nuevo y
  la de antes queda para después (9d). Una pregunta igual a una sin cerrar (mismo tipo, tarea y
  jugada) no se repite: es la misma.
- **Contestar:** una jugada que se anota contesta las preguntas que su ficha declara
  (`Ficha.contesta`) sobre esa tarea y la duda que esperaba esa misma jugada si la tarea es una
  de sus opciones.
- **Al terminar el turno**, si no quedó ninguna abierta, vuelve la más vieja de las que
  quedaron para después (salvo la que la persona dejó para después en este mismo mensaje), y la
  redacción recibe la única pregunta que se hace (`al_terminar_el_turno`).

Nada se borra: una pregunta se cierra con su momento, cómo (`respondida`, `cancelada` o
`sin_efecto`) y con qué (`cierre_detalle`), que es lo que se dice si después llega un toque
viejo (situación general 7).
"""

from __future__ import annotations

import json
import re
import secrets
from collections.abc import Sequence
from typing import Any

CUAL_TAREA = "cual_tarea"      # la duda: de qué tarea habla (situación general 5)
# El estado de una tarea, que Leda pide por su cuenta desde el vencimiento (escalera, 9b): no se
# puede dejar sin efecto, y la contestan las jugadas que informan un hecho de la tarea.
ESTADO_DE_LA_TAREA = "estado_de_la_tarea"
# Para cuándo prevé terminar la tarea: Leda la pregunta directo a la segunda respuesta sin un
# hecho cierto (`informar_avance`, decisión del usuario, 2026-10-05). Es parte del pedido de
# estado: no se deja sin efecto, la contestan las jugadas que informan un hecho cierto, y el
# pedido del estado del día hábil siguiente la reemplaza (`avisos._abrir_la_pregunta`).
FECHA_DE_LA_TAREA = "fecha_de_la_tarea"

PREFIJO_TOQUE = "m:"           # el `callback_data` de un botón es el prefijo y el token
_LARGO_ETIQUETA = 80           # `salida.BUTTON_LABEL_LIMIT`


def callback(token: str) -> str:
    return f"{PREFIJO_TOQUE}{token}"


def token_de(data: str) -> str | None:
    """El token de un `callback_data` del motor; `None` si no es uno."""
    if not data.startswith(PREFIJO_TOQUE):
        return None
    return data[len(PREFIJO_TOQUE):] or None


def alias_de_opcion(orden: int) -> str:
    return f"O{orden}"


def orden_de_alias(alias: Any) -> int | None:
    m = re.fullmatch(r"[Oo](\d+)", str(alias).strip())
    return int(m.group(1)) if m else None


# --- Leer -----------------------------------------------------------------------------------

def actual(cur, membership_id: str) -> dict[str, Any] | None:
    """La pregunta abierta de la persona, si hay y no se cerró."""
    cur.execute("""select q.* from conversation_state s
                     join conversation_question q on q.id = s.pregunta_abierta_id
                    where s.membership_id = %s and q.cerrada_en is null""", (membership_id,))
    return cur.fetchone()


def para_despues(cur, membership_id: str) -> list[dict[str, Any]]:
    cur.execute("""select * from conversation_question
                    where membership_id = %s and cerrada_en is null
                      and para_despues_en is not null
                    order by abierta_en""", (membership_id,))
    return cur.fetchall()


def opciones(cur, pregunta_id: str) -> list[dict[str, Any]]:
    cur.execute("""select * from conversation_option where question_id = %s order by orden""",
                (pregunta_id,))
    return cur.fetchall()


def opcion_por_token(cur, token: str) -> dict[str, Any] | None:
    """La opción de un toque y su pregunta, bajo la RLS del espacio: un token de otro espacio
    no se encuentra."""
    cur.execute("""select o.id, o.orden, o.etiqueta, o.valor, o.question_id,
                          q.membership_id, q.cerrada_en
                     from conversation_option o
                     join conversation_question q on q.id = o.question_id
                    where o.token = %s""", (token,))
    return cur.fetchone()


def estado_para_la_ia(cur, membership_id: str, tareas) -> dict[str, Any] | None:
    """Lo que la IA recibe del estado de la conversación: la pregunta abierta (con sus
    opciones por alias) y las que quedaron para después. `None` si no hay ninguna."""
    abierta = actual(cur, membership_id)
    despues = para_despues(cur, membership_id)
    if abierta is None and not despues:
        return None
    return {"pregunta_abierta": _para_la_ia(cur, abierta, tareas) if abierta else None,
            "para_despues": [{"tipo": q["tipo"], "tarea": _alias(tareas, q["task_id"])}
                             for q in despues]}


def _para_la_ia(cur, q, tareas) -> dict[str, Any]:
    dicha = {"tipo": q["tipo"], "tarea": _alias(tareas, q["task_id"])}
    ops = opciones(cur, q["id"])
    if ops:
        dicha["opciones"] = [{"opcion": alias_de_opcion(o["orden"]), "etiqueta": o["etiqueta"],
                              "tarea": _alias(tareas, (o["valor"] or {}).get("tarea"))}
                             for o in ops]
    return dicha


def _alias(tareas, task_id) -> str | None:
    if task_id is None:
        return None
    return next((t["alias"] for t in tareas if t["id"] == str(task_id)), None)


# --- Abrir, cerrar y retomar ------------------------------------------------------------------

def abrir(ctx, tipo: str, task_id: str | None, *, se_puede_dejar: bool,
          jugada: dict[str, Any], opciones_de_tareas: Sequence[dict[str, Any]] = ()) -> bool:
    """Abre una pregunta (o reconoce la misma sin cerrar) y la ordena con las demás (ver el
    módulo). `opciones_de_tareas`: las tareas de una duda, que se ofrecen como opciones.
    Devuelve si es la que se pregunta ahora (`False`: quedó para después)."""
    cur, persona = ctx.cur, ctx.quien.membership_id
    cur.execute("""select id from conversation_question
                    where membership_id = %s and cerrada_en is null and tipo = %s
                      and task_id is not distinct from %s
                      and jugada ->> 'nombre' is not distinct from %s
                    order by abierta_en limit 1""",
                (persona, tipo, task_id, jugada.get("nombre")))
    misma = cur.fetchone()
    if misma is not None:
        pregunta = str(misma["id"])
        cur.execute("update conversation_question set jugada = %s where id = %s",
                    (_json(jugada), pregunta))
    else:
        cur.execute(
            """insert into conversation_question (workspace_id, membership_id, tipo, task_id,
                                                  jugada, se_puede_dejar, abierta_en)
               values (%s, %s, %s, %s, %s, %s, %s) returning id""",
            (ctx.quien.workspace_id, persona, tipo, task_id, _json(jugada), se_puede_dejar,
             ctx.ahora))
        pregunta = str(cur.fetchone()["id"])
        for orden, tarea in enumerate(opciones_de_tareas, 1):
            cur.execute(
                """insert into conversation_option (workspace_id, question_id, token,
                                                    etiqueta, valor, orden)
                   values (%s, %s, %s, %s, %s, %s)""",
                (ctx.quien.workspace_id, pregunta, secrets.token_urlsafe(9),
                 _etiqueta(tarea["titulo"]), _json({"tarea": tarea["id"]}), orden))

    vigente = actual(cur, persona)
    if vigente is None or str(vigente["id"]) == pregunta:
        _que_sea_la_abierta(ctx, pregunta)
        ahora_si = True
    elif str(vigente["id"]) in ctx.preguntas_del_turno:
        _dejar_para_despues(ctx, pregunta)
        ahora_si = False
    else:
        _dejar_para_despues(ctx, str(vigente["id"]))
        _que_sea_la_abierta(ctx, pregunta)
        ahora_si = True
    if pregunta not in ctx.preguntas_del_turno:
        ctx.preguntas_del_turno.append(pregunta)
    return ahora_si


def cerrar(ctx, pregunta_id: str, cierre: str, detalle: dict[str, Any]) -> None:
    ctx.cur.execute(
        """update conversation_question
              set cerrada_en = %s, cierre = %s, cierre_detalle = %s
            where id = %s and cerrada_en is null""",
        (ctx.ahora, cierre, _json(detalle), pregunta_id))
    ctx.cur.execute(
        """update conversation_state set pregunta_abierta_id = null, actualizado_en = %s
            where membership_id = %s and pregunta_abierta_id = %s""",
        (ctx.ahora, ctx.quien.membership_id, pregunta_id))


def cerrar_de_tipo(ctx, tipo: str, task_id: str, cierre: str, detalle: dict[str, Any]) -> None:
    ctx.cur.execute("""select id from conversation_question
                        where membership_id = %s and tipo = %s and task_id = %s
                          and cerrada_en is null""",
                    (ctx.quien.membership_id, tipo, task_id))
    for fila in ctx.cur.fetchall():
        cerrar(ctx, str(fila["id"]), cierre, detalle)


def cerrar_las_de_una_jugada(ctx, nombre: str, task_id: str, cierre: str,
                             detalle: dict[str, Any]) -> None:
    """Las preguntas sin cerrar que esperaban algo de esa jugada sobre esa tarea."""
    ctx.cur.execute("""select id from conversation_question
                        where membership_id = %s and task_id = %s and cerrada_en is null
                          and jugada ->> 'nombre' = %s""",
                    (ctx.quien.membership_id, task_id, nombre))
    for fila in ctx.cur.fetchall():
        cerrar(ctx, str(fila["id"]), cierre, detalle)


def contestar(ctx, nombre: str, tipos: Sequence[str], task_id: str) -> None:
    """Una jugada que se anotó sobre una tarea contesta las preguntas de los tipos que su
    ficha declara sobre esa tarea y la duda que esperaba esa jugada, si la tarea era una de
    sus opciones."""
    ctx.cur.execute(
        """select q.id from conversation_question q
            where q.membership_id = %s and q.cerrada_en is null
              and ((q.tipo = any(%s) and q.task_id = %s)
                   or (q.tipo = %s and q.jugada ->> 'nombre' = %s
                       and exists (select 1 from conversation_option o
                                    where o.question_id = q.id
                                      and o.valor ->> 'tarea' = %s)))""",
        (ctx.quien.membership_id, list(tipos), task_id, CUAL_TAREA, nombre, task_id))
    for fila in ctx.cur.fetchall():
        cerrar(ctx, str(fila["id"]), "respondida", {"jugada": nombre, "tarea": task_id})


def dejar_para_despues(ctx, pregunta_id: str) -> None:
    """La persona deja la pregunta para más tarde: no vuelve en este mismo mensaje."""
    _dejar_para_despues(ctx, pregunta_id)
    ctx.dejadas.append(pregunta_id)


def al_terminar_el_turno(ctx) -> dict[str, Any] | None:
    """Si no quedó una pregunta abierta, vuelve la más vieja de las que quedaron para
    después. Devuelve la única que se hace en la respuesta, descrita para la redacción, con
    `desde_antes` si no salió de este mensaje (volver a ella es retomarla, 9d)."""
    cur, persona = ctx.cur, ctx.quien.membership_id
    abierta = actual(cur, persona)
    if abierta is None:
        cur.execute("""select * from conversation_question
                        where membership_id = %s and cerrada_en is null
                          and para_despues_en is not null and not (id = any(%s::uuid[]))
                        order by abierta_en limit 1""", (persona, list(ctx.dejadas)))
        abierta = cur.fetchone()
        if abierta is None:
            return None
        _que_sea_la_abierta(ctx, str(abierta["id"]))
    return {**describir(ctx, abierta),
            "desde_antes": str(abierta["id"]) not in ctx.preguntas_del_turno}


def describir(ctx, q) -> dict[str, Any]:
    """Una pregunta para la redacción: su tipo, su tarea y sus opciones (las tareas, por su
    título; van como botones)."""
    dicha: dict[str, Any] = {"tipo": q["tipo"]}
    if q["task_id"] is not None:
        dicha["tarea"] = tarea_dicha(ctx, q["task_id"])
    ops = opciones(ctx.cur, q["id"])
    if ops:
        dicha["opciones"] = [{"opcion": alias_de_opcion(o["orden"]), "etiqueta": o["etiqueta"],
                              **_tarea_de_opcion(ctx, o)} for o in ops]
    return dicha


def con_que_se_cerro(ctx, pregunta_id: str) -> dict[str, Any]:
    """Cómo y con qué se cerró una pregunta: lo que Leda dice ante un toque viejo."""
    ctx.cur.execute("select cerrada_en, cierre, cierre_detalle from conversation_question "
                    "where id = %s", (pregunta_id,))
    q = ctx.cur.fetchone()
    detalle = q["cierre_detalle"] or {}
    dicho: dict[str, Any] = {"cierre": q["cierre"],
                             "cuando": q["cerrada_en"].astimezone(
                                 ctx.calendario.zona).date().isoformat()}
    if detalle.get("tarea"):
        dicho["tarea"] = tarea_dicha(ctx, detalle["tarea"])
    return dicho


def tarea_dicha(ctx, task_id) -> dict[str, str]:
    """Una tarea para los hechos: su alias si está entre las de la persona, y su título."""
    tarea = next((t for t in ctx.tareas if t["id"] == str(task_id)), None)
    if tarea is not None:
        return {"alias": tarea["alias"], "titulo": tarea["titulo"]}
    ctx.cur.execute("select titulo from task where id = %s", (str(task_id),))
    fila = ctx.cur.fetchone()
    return {"titulo": fila["titulo"]} if fila else {}


def _tarea_de_opcion(ctx, opcion) -> dict[str, Any]:
    task_id = (opcion["valor"] or {}).get("tarea")
    return {"tarea": tarea_dicha(ctx, task_id)} if task_id else {}


def _que_sea_la_abierta(ctx, pregunta_id: str) -> None:
    ctx.cur.execute("update conversation_question set para_despues_en = null where id = %s",
                    (pregunta_id,))
    ctx.cur.execute(
        """insert into conversation_state (membership_id, workspace_id, pregunta_abierta_id,
                                           actualizado_en)
           values (%s, %s, %s, %s)
           on conflict (membership_id) do update
              set pregunta_abierta_id = excluded.pregunta_abierta_id,
                  actualizado_en = excluded.actualizado_en""",
        (ctx.quien.membership_id, ctx.quien.workspace_id, pregunta_id, ctx.ahora))


def _dejar_para_despues(ctx, pregunta_id: str) -> None:
    ctx.cur.execute("""update conversation_question set para_despues_en = %s
                        where id = %s and cerrada_en is null""", (ctx.ahora, pregunta_id))
    ctx.cur.execute(
        """update conversation_state set pregunta_abierta_id = null, actualizado_en = %s
            where membership_id = %s and pregunta_abierta_id = %s""",
        (ctx.ahora, ctx.quien.membership_id, pregunta_id))


def _etiqueta(titulo: str) -> str:
    return titulo if len(titulo) <= _LARGO_ETIQUETA else titulo[:_LARGO_ETIQUETA - 1] + "…"


def _json(valor: Any) -> str:
    return json.dumps(valor, ensure_ascii=False, default=str)
