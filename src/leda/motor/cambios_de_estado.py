"""Desde cuándo una tarea está en su estado, por lo que anotó el motor.

Cuarta vuelta de ajuste (2026-10-06), después de la ronda 3: el pedido de estado de una tarea en
curso no decía desde cuándo (conversación 01, paso 4: "está en curso desde el martes"), y la IA
no lo puede saber si la cocina no se lo pasa (la regla del mozo).

`task_state_event` sabe cuándo cambió cada estado, pero `leda_app` no lo lee (es un registro
append-only; `db/esquema.sql`) y lo fecha la base en hora real, no con el reloj del motor (plan,
sección 11). Por eso el motor anota lo suyo:

- **Al terminar cada turno**, los cambios de estado que dejó en las tareas de la persona (de qué
  estado a cuál), en su resultado registrado (`CLAVE`), fuera de los hechos, como lo anunciado
  (`efectos.ANUNCIADOS`): ni la IA ni los últimos turnos los ven. Un solo paso para todas las
  jugadas, sin una rama por jugada: compara el estado de cada tarea al empezar y al terminar.
- **`desde`** lee esos cambios, del más nuevo al más viejo, y da el día en que la tarea entró en
  su estado actual. Salir de `bloqueada` devuelve el estado que tenía (mecánica §3): el bloqueo
  y su salida no cambian desde cuándo está en ese estado. Si el estado vino de antes del motor
  (lo cargó otro) o de algo que el motor no anotó, el código no lo sabe y lo dice
  (`DESCONOCIDO`): nunca lo adivina. `asignada` es como llega una tarea: desde cuándo lo está es
  de quien la cargó, y no se dice.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from datetime import tzinfo
from typing import Any

CLAVE = "cambios_de_estado"
DESCONOCIDO = "desconocido"
COMO_LLEGA = "asignada"
BLOQUEADA = "bloqueada"


def del_turno(cur, tareas: Iterable[Mapping[str, Any]]) -> list[dict[str, str]]:
    """Los cambios de estado de las tareas de la persona entre el principio del turno
    (`tareas`, como se leyeron) y ahora: `task_id`, `de` y `a`."""
    antes = {str(t["id"]): str(t["estado"]) for t in tareas if t.get("id")}
    if not antes:
        return []
    cur.execute("select id, estado::text estado from task where id = any(%s::uuid[])",
                (list(antes),))
    return [{"task_id": str(f["id"]), "de": antes[str(f["id"])], "a": f["estado"]}
            for f in sorted(cur.fetchall(), key=lambda f: str(f["id"]))
            if f["estado"] != antes[str(f["id"])]]


def desde(cur, task_id: Any, responsable_membership_id: Any, estado: str,
          zona: tzinfo) -> str | None:
    """El día (AAAA-MM-DD) en que la tarea entró en `estado`, según los turnos de su
    responsable; `DESCONOCIDO` si el motor no lo anotó; `None` si está como llegó."""
    if estado == COMO_LLEGA:
        return None
    tarea = str(task_id)
    cur.execute("""select at, resultado -> %s as cambios from conversation_turn
                    where membership_id = %s and sentido = 'entrada'
                      and resultado ? %s
                    order by numero desc""",
                (CLAVE, str(responsable_membership_id), CLAVE))
    for fila in cur.fetchall():
        cambios = fila["cambios"]
        if isinstance(cambios, str):
            cambios = json.loads(cambios)
        for cambio in reversed(cambios or []):
            if cambio.get("task_id") != tarea:
                continue
            de, a = cambio.get("de"), cambio.get("a")
            if a == estado and de != BLOQUEADA:
                return fila["at"].astimezone(zona).date().isoformat()
            if (a == estado and de == BLOQUEADA) or (de == estado and a == BLOQUEADA):
                continue        # un bloqueo y su salida: sigue en el mismo estado
            return DESCONOCIDO
    return DESCONOCIDO
