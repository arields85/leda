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
trabajo, quien ya decidió sobre esa tarea, el referente del área y la autoridad final. De las que
coinciden con lo dicho cuentan sólo las que la persona puede ver; si no puede ver ninguna, Leda le
dice que ese enlace no se lo puede pasar, sin decir quién sí la ve (decisión 11 del usuario) ni
nada de la base (constitución §10), y ningún enlace sale. Si puede ver varias, pregunta cuál.

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

# Por qué no sale el enlace (sus significados, en `hechos.py`).
NO_PUEDE_VER = "no_puede_ver_esa_tarea"
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
    else:
        dicho = datos.get("como_la_nombra")
        if fichas.vacio(dicho) or not _que_nombra(str(dicho)):
            return {"resultado": "falta_dato", "falta": ["tarea"]}
        coinciden = _las_que_coinciden(ctx, str(dicho))
        visibles = [t for t in coinciden if t["ve"]]
        if not coinciden:
            return {"resultado": "no_se_puede", "motivo": NINGUNA_CON_ESE_NOMBRE}
        if not visibles:
            # Sin el título: de una tarea que no puede ver, sólo lo que la persona ya dijo.
            return {"resultado": "no_se_puede", "motivo": NO_PUEDE_VER}
        if len(visibles) > 1:
            return {"resultado": "falta_dato", "falta": ["tarea"],
                    "coinciden": [{"titulo": t["titulo"], "responsable": t["responsable"]}
                                  for t in visibles]}
        una = visibles[0]
    if una is None or not una["ve"]:
        return {"resultado": "no_se_puede", "motivo": NO_PUEDE_VER}
    hecho: dict[str, Any] = {"resultado": "leido", "tarea": _tarea(ctx, una)}
    if una["responsable_id"] != yo and una["responsable"]:
        hecho["responsable"] = una["responsable"]
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
    buscadas = _que_nombra(dicho)
    cur = ctx.cur
    cur.execute("""select t.id::text id, t.titulo, t.responsable_membership_id::text
                          responsable_id, i.nombre responsable
                     from task t
                     left join integrante i on i.membership_id = t.responsable_membership_id
                    where t.workspace_id = %s
                    order by t.titulo, t.id""", (ctx.quien.workspace_id,))
    coinciden = []
    for t in cur.fetchall():
        nombre = fichas.palabras(t["titulo"]) + fichas.palabras(t["responsable"] or "")
        if all(any(_misma_palabra(b, n) for n in nombre) for b in buscadas):
            coinciden.append(dict(t))
    for t in coinciden:
        t["ve"] = _puede_verla(cur, ctx.quien.membership_id, t["id"])
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
