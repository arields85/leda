"""El reloj del motor de conversación.

Los momentos de las tablas del motor los pone el motor con su reloj, nunca un valor por
omisión de la base (`odd/tasks/prueba-chica-del-motor.md`, sección 5): así una corrida con
reloj simulado (sección 6) y el comando que adelanta el reloj en Telegram (decisión 10.2)
ven el mismo tiempo en todo lo que el motor escribe.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol


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
