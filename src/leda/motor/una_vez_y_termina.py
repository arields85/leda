"""Una pregunta a otra persona que nadie contesta: se repite una vez y termina.

Decisión 26 del usuario (2026-10-09, opción A; `odd/tasks/fase-c.md`), nacida de los pases (C-7) y
aplicada a todo pedido que espera la respuesta de otra persona para que algo pase: el pase de una
tarea (`pase.seguir_los_pases`) y el pedido del detalle de una tarea al encargado de su sector
(`detalle.seguir_los_pedidos`; derivado de la decisión 33 por el coordinador, 2026-10-09). Una
regla de la cocina, la misma para los dos:

- **La pregunta otra vez, una sola** (`toca_repetir`): el día hábil siguiente de haber salido, si
  sigue sin contestar.
- **El fin sin respuesta** (`vencio`): al día hábil siguiente de la repetición, a la hora en que
  Leda escribe, si sigue sin contestar. Quien pidió se entera, y quien tenía que contestar, que ya
  no hace falta (decisión 39: nunca un tema abierto sin que todos sepan cómo se cerró).
- Una ausencia de quien tiene que contestar la pausa (mecánica §9): ni se repite ni vence.

No es la pregunta de quien destraba, que nunca se abandona (decisión 38): ésa espera algo que
alguien necesita para seguir trabajando; éstas, una decisión que se puede pedir otra vez.
"""

from __future__ import annotations

from typing import Any

from .tiempo import sale


def salio(aviso: dict[str, Any] | None) -> bool:
    """Si un aviso ya salió (o se dio por dado: no se pudo mandar, con su incidente)."""
    return aviso is not None and aviso["estado"] != "guardado" and aviso["resuelto_en"] is not None


def toca_repetir(m, pregunta: dict[str, Any] | None, otra_vez: dict[str, Any] | None, *,
                 pausado: bool) -> bool:
    """Si toca repetir la pregunta: salió, no se repitió todavía y pasó un día hábil."""
    return (not pausado and salio(pregunta) and otra_vez is None
            and m.cal.habiles_entre(pregunta["resuelto_en"], m.ahora) >= 1)


def vencio(m, otra_vez: dict[str, Any] | None, *, pausado: bool) -> bool:
    """Si el plazo terminó: la repetición salió hace un día hábil y ya es la hora en que Leda
    escribe."""
    return (not pausado and salio(otra_vez)
            and m.cal.habiles_entre(otra_vez["resuelto_en"], m.ahora) >= 1
            and sale(m.cal, m.ahora) <= m.ahora)
