"""Pedir por chat el enlace a la página de una tarea (la jugada `pedir_enlace`).

ADR 0019, decisión 7a ("cualquiera de los que pueden verla, cuando lo pide por chat: una jugada
nueva de la lista cerrada, con su ficha") y 7b (quién la ve); ADR 0018, decisión 1 (la IA elige la
jugada y nombra la tarea; el código decide si vale); conversación 31; `odd/tasks/fase-c.md`, lo que
quedó de la porción 4 de la C-3.

**Qué tarea.** La IA la nombra por su alias si está en la lista de la persona (sus tareas abiertas
y las entregas que esperan su revisión) o, si no está, por cómo la dijo (`como_la_nombra`): una
tarea terminada, o una de otra persona que la autoridad final o el referente del área pueden ver.
La cocina la busca entre las tareas del espacio de quien escribe, también las terminadas y las
canceladas: cada palabra que dijo tiene que estar, entera, en el título de la tarea o en el nombre
de quien la tiene (sin mayúsculas ni acentos, y un plural vale por su singular). Las palabras de
unión ("la del tablero de marcos") no cuentan: no nombran nada. Se compara acá, nunca con un patrón
de la base, así nada de lo dicho actúa como comodín (como `fichas.integrantes_que_coinciden`), y la
búsqueda la arma el código, nunca la IA.

**Quién la ve lo decide la base** (`puede_ver_tarea`): la persona responsable, quien aprueba su
trabajo, quien ya decidió sobre esa tarea, el referente del área, la autoridad final y a quien el
encargado del sector de la tarea se la compartió (decisión 33). De las que coinciden con lo dicho
cuentan primero las que la persona puede ver: una, su enlace; varias, pregunta cuál.

**Si no la ve, el resumen** (decisión 33 del usuario, 2026-10-09): el resumen de una tarea (qué
tarea, de quién, para cuándo, cómo quedó) lo ve cualquiera del equipo; el detalle, sólo quienes
tienen que ver con ella. Leda nunca contesta "no la podés ver": le da el resumen, ningún enlace, y
le ofrece pedirle el detalle al encargado del sector de la tarea (`detalle.ofrecer`). Si no ve
ninguna de las que coinciden y son varias, las nombra y pregunta cuál, como siempre. Nada de la
base (constitución §10).

**El enlace nunca pasa por la IA** (ADR 0019, decisión 6): la respuesta lleva la marca `(tarea,
persona)` (`Contexto.enlace_de_la_respuesta`, como `aprobacion.ver_entrega`) y el despachador lo
emite al mandar, después de que la base vuelva a comprobar que la persona puede verla. Uno solo
por mensaje: el de otra tarea en el mismo mensaje no se promete. Sin la dirección pública
configurada no hay enlace, y los hechos lo dicen. Leer no cambia nada.
"""

from __future__ import annotations

from typing import Any

from . import fichas
from .avisos import LLEVA_EL_ENLACE, enlace_a_la_pagina

# Por qué no sale el enlace (sus significados, en `hechos.py`): la persona no ve la tarea y recibe
# su resumen (decisión 33), no hay ninguna con ese nombre, la página no está disponible o el
# mensaje ya lleva el de otra.
SOLO_EL_RESUMEN = "solo_el_resumen"
NINGUNA_CON_ESE_NOMBRE = "ninguna_tarea_con_ese_nombre"
SIN_PAGINA = "la_pagina_no_esta_disponible"
YA_LLEVA_OTRO = "ya_lleva_el_enlace_de_otra_tarea"

# Las palabras que unen y no nombran: artículos, preposiciones y sus contracciones. "La del
# tablero de marcos" nombra el tablero y a Marcos; sin esto, "del" tendría que estar en el título.
PALABRAS_DE_UNION = frozenset({
    "el", "la", "los", "las", "lo", "un", "una", "unos", "unas", "de", "del", "al", "a", "en",
    "con", "para", "por", "y", "e", "o", "u", "que", "su", "sus", "mi", "mis", "tu", "tus"})


def pedir_enlace(ctx, datos: dict, tarea: dict | None) -> dict[str, Any]:
    """La jugada: la tarea nombrada, si la persona puede verla, con la marca del enlace en la
    respuesta; si no, por qué no sale. Nada cambia."""
    yo = ctx.quien.membership_id
    if tarea is not None:
        una = _una_por_id(ctx, tarea["id"])
        if una is None:
            return {"resultado": "no_se_puede", "motivo": NINGUNA_CON_ESE_NOMBRE}
    else:
        dicho = datos.get("como_la_nombra")
        if fichas.vacio(dicho) or not _que_nombra(str(dicho)):
            return {"resultado": "falta_dato", "falta": ["tarea"]}
        una = la_que_nombra(ctx, str(dicho))
        if "resultado" in una:
            return una
    hecho: dict[str, Any] = {"resultado": "leido", "tarea": _tarea(ctx, una)}
    if una["responsable_id"] != yo and una["responsable"]:
        hecho["responsable"] = una["responsable"]
    if not una["ve"]:
        return _resumen(ctx, una, hecho)
    ya = ctx.enlace_de_la_respuesta
    if ya:
        if ya[0][0] != una["id"]:
            return {**hecho, "resultado": "no_se_puede", "motivo": YA_LLEVA_OTRO}
        return {**hecho, LLEVA_EL_ENLACE: True}
    enlace = enlace_a_la_pagina(ctx.cur, una["id"], yo)
    if enlace is None:
        return {**hecho, "resultado": "no_se_puede", "motivo": SIN_PAGINA}
    ya.append(enlace)
    return {**hecho, LLEVA_EL_ENLACE: True}


def la_que_nombra(ctx, dicho: str) -> dict[str, Any]:
    """La tarea del espacio que nombra lo dicho, con si la persona la ve, o el hecho de por qué no
    hay una (con `resultado`): ninguna, o varias. Cuentan primero las que la persona ve; si no ve
    ninguna, todas, porque el resumen lo ve cualquiera del equipo (decisión 33)."""
    coinciden = _las_que_coinciden(ctx, dicho)
    if not coinciden:
        return {"resultado": "no_se_puede", "motivo": NINGUNA_CON_ESE_NOMBRE}
    visibles = [t for t in coinciden if t["ve"]] or coinciden
    if len(visibles) > 1:
        return {"resultado": "falta_dato", "falta": ["tarea"],
                "coinciden": [{"titulo": t["titulo"], "responsable": t["responsable"]}
                              for t in visibles]}
    return visibles[0]


def _resumen(ctx, una: dict[str, Any], hecho: dict[str, Any]) -> dict[str, Any]:
    """El resumen de una tarea que la persona no ve (decisión 33): cómo quedó y cuándo vence,
    nunca su detalle ni su enlace, y lo que puede hacer para verlo (`detalle.ofrecer`)."""
    from . import detalle                # detalle importa este módulo al pedir
    cur = ctx.cur
    cur.execute("select estado::text estado, fecha_objetivo from task where id = %s",
                (una["id"],))
    fila = cur.fetchone()
    hecho = {**hecho, "resultado": SOLO_EL_RESUMEN, "estado": fila["estado"]}
    if fila["fecha_objetivo"] is not None:
        hecho["vence"] = fila["fecha_objetivo"].astimezone(ctx.calendario.zona).date().isoformat()
    detalle.ofrecer(ctx, una["id"], hecho)
    return hecho


def puede_verla(cur, persona: str, task_id: str) -> bool:
    """Si la persona ve la tarea: la regla vive en la base (`puede_ver_tarea`)."""
    return _puede_verla(cur, persona, task_id)


def _que_nombra(dicho: str) -> list[str]:
    """Las palabras de lo dicho que nombran algo: sin mayúsculas, acentos ni palabras de unión."""
    return [p for p in fichas.palabras(dicho) if p not in PALABRAS_DE_UNION]


def _misma_palabra(a: str, b: str) -> bool:
    """La misma palabra, o una el plural de la otra ("tablero" y "tableros", "comunicacion" y
    "comunicaciones"): nunca un pedazo ("tab" no es "tablero")."""
    return a == b or a + "s" == b or a + "es" == b or b + "s" == a or b + "es" == a


def _las_que_coinciden(ctx, dicho: str) -> list[dict[str, Any]]:
    """Las tareas del espacio de quien escribe que tienen cada palabra de lo dicho en su título
    o en el nombre de su responsable, con si la persona puede verla (la regla, en la base)."""
    coinciden = tareas_que_nombra(ctx.cur, ctx.quien.workspace_id, dicho)
    for t in coinciden:
        t["ve"] = _puede_verla(ctx.cur, ctx.quien.membership_id, t["id"])
    return coinciden


def tareas_que_nombra(cur, workspace_id: str, dicho: str) -> list[dict[str, Any]]:
    """Las tareas del espacio, también las terminadas y canceladas, que tienen cada palabra de lo
    dicho en su título o en el nombre de su responsable (la misma regla para la jugada y para el
    bot de administración, `administracion.py`). Corre en la transacción del espacio
    (`db.espacio`): la vista `integrante` y la RLS la acotan a él."""
    buscadas = _que_nombra(dicho)
    cur.execute("""select t.id::text id, t.titulo, t.responsable_membership_id::text
                          responsable_id, i.nombre responsable
                     from task t
                     left join integrante i on i.membership_id = t.responsable_membership_id
                    where t.workspace_id = %s
                    order by t.titulo, t.id""", (str(workspace_id),))
    coinciden = []
    for t in cur.fetchall():
        nombre = fichas.palabras(t["titulo"]) + fichas.palabras(t["responsable"] or "")
        if all(any(_misma_palabra(b, n) for n in nombre) for b in buscadas):
            coinciden.append(dict(t))
    return coinciden


def _una_por_id(ctx, task_id: str) -> dict[str, Any] | None:
    """La tarea nombrada por su alias, del espacio de quien escribe, con si puede verla."""
    cur = ctx.cur
    cur.execute("""select t.id::text id, t.titulo, t.responsable_membership_id::text
                          responsable_id, i.nombre responsable
                     from task t
                     left join integrante i on i.membership_id = t.responsable_membership_id
                    where t.id = %s and t.workspace_id = %s""",
                (task_id, ctx.quien.workspace_id))
    fila = cur.fetchone()
    if fila is None:
        return None
    return {**fila, "ve": _puede_verla(cur, ctx.quien.membership_id, fila["id"])}


# Para nombrar una tarea por cómo la dijo la persona en otra jugada (`pase.pedir`, decisión 27).
que_nombra = _que_nombra
misma_palabra = _misma_palabra


def _puede_verla(cur, persona: str, task_id: str) -> bool:
    cur.execute("select puede_ver_tarea(%s, %s) as ve", (persona, task_id))
    return bool(cur.fetchone()["ve"])


def _tarea(ctx, una: dict[str, Any]) -> dict[str, str]:
    """La tarea en los hechos: con su alias si está en la lista de la persona; si no, por su
    título."""
    alias = next((t["alias"] for t in ctx.tareas + ctx.para_aprobar if t["id"] == una["id"]),
                 None)
    return {**({"alias": alias} if alias else {}), "titulo": una["titulo"]}
