"""El reloj del motor de conversación.

Los momentos de las tablas del motor los pone el motor con su reloj, nunca un valor por
omisión de la base (diseño probado en la Etapa 2, `odd/tasks/prueba-chica-del-motor.md`,
sección 5): así una corrida con reloj simulado (sección 6) y el comando que adelanta el reloj
en Telegram (decisión 10.2) ven el mismo tiempo en todo lo que el motor escribe.

**La hora de salida** (cuarta vuelta de ajuste, 2026-10-06; ronda 3): lo que Leda manda por su
cuenta (la escalera, los avisos guardados, el pedido que sigue a un avance) sale a una sola
hora, `HORA_DE_SALIDA`, la de las conversaciones de prueba (`tests/conversaciones/README.md`).
La usan quienes guardan un aviso (`sale`, `sale_el`), el reloj adelantado (`reloj.py`) y, por
eso, los hechos que dicen cuándo sale algo: la hora que se le cuenta a la persona es la que de
verdad se usa. Antes, el pedido que sigue a un avance salía al empezar la jornada (09:00) y se
le contaba "mañana a las 9", mientras el reloj adelantado y las conversaciones llegaban a las
10:00. Es un valor fijo del motor, el mismo que pasó la prueba real; tiene que pasar a ser
del espacio (`PENDIENTE`).
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, time as hora, timedelta, timezone
from typing import Protocol


HORA_DE_SALIDA = hora(10, 0)


class Reloj(Protocol):
    def ahora(self) -> datetime:
        """El momento del motor, con zona horaria."""

    def medir(self) -> float:
        """Segundos de un contador monótono, para la latencia de la IA."""


class RelojDelSistema:
    def ahora(self) -> datetime:
        return datetime.now(timezone.utc)

    def medir(self) -> float:
        return time.perf_counter()


@dataclass
class RelojFijo:
    """Siempre el mismo momento y latencia cero: para las pruebas deterministas."""

    momento: datetime

    def ahora(self) -> datetime:
        return self.momento

    def medir(self) -> float:
        return 0.0


def sale_el(cal, dia) -> datetime:
    """La hora de salida de ese día; si el horario del espacio no la incluye, el próximo
    momento hábil (`Calendario.dentro_de_jornada`)."""
    return cal.dentro_de_jornada(datetime.combine(dia, HORA_DE_SALIDA, tzinfo=cal.zona))


def sale(cal, momento: datetime) -> datetime:
    """Cuándo sale lo que Leda guarda en `momento` para mandar por su cuenta: a la hora de
    salida de ese día hábil si todavía no llegó; enseguida, si ya pasó y sigue la jornada; si
    no, a la hora de salida del próximo día hábil."""
    local = momento.astimezone(cal.zona)
    if cal.es_habil(local.date()):
        a_la_hora = sale_el(cal, local.date())
        if local <= a_la_hora:
            return a_la_hora
        if cal.en_horario(local):
            return local
    return sale_el(cal, cal.proximo_habil(local.date() + timedelta(days=1)))
