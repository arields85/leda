"""Lo que el motor de conversación le pide a la IA (ADR 0018, decisión 1).

Dos pedidos por turno: elegir jugadas de la lista cerrada y redactar desde los hechos. Acá
están el contrato y una IA guionada para las pruebas deterministas; la IA sobre un proveedor
real, con la llamada estructurada que fuerza la herramienta, va en `ia_real.py`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class Jugada:
    """Una jugada que eligió la IA: su nombre en la lista cerrada y sus datos (las tareas,
    por el alias que recibió)."""

    nombre: str
    datos: dict[str, Any] = field(default_factory=dict)


class IA(Protocol):
    nombre: str

    def elegir_jugadas(self, situacion: dict[str, Any]) -> list[Jugada]:
        """Las jugadas que corresponden al mensaje, de `situacion["jugadas_posibles"]`."""

    def redactar(self, pedido: dict[str, Any],
                 al_avanzar: Callable[[str], None] | None = None) -> str:
        """La respuesta a la persona, escrita desde `pedido["hechos"]`. Con `al_avanzar`, quien
        escribe en vivo avisa todo lo escrito hasta ahí cada vez que crece (lo muestra el
        borrador de Telegram, pedido del usuario del 2026-10-07); quien no, no avisa nada. El
        turno lo pasa sólo cuando alguien mira, así una IA sin ese argumento sigue sirviendo."""


class GuionAgotado(RuntimeError):
    pass


@dataclass
class IAGuionada:
    """Devuelve lo preparado, en orden. Una excepción en el guion se levanta, como una IA
    que no responde; guarda cada pedido para que la prueba vea qué recibió la IA."""

    jugadas: list[list[Jugada] | BaseException] = field(default_factory=list)
    redacciones: list[str | BaseException] = field(default_factory=list)
    nombre: str = "guionada"
    pedidos_de_jugadas: list[dict[str, Any]] = field(default_factory=list)
    pedidos_de_redaccion: list[dict[str, Any]] = field(default_factory=list)

    def elegir_jugadas(self, situacion: dict[str, Any]) -> list[Jugada]:
        self.pedidos_de_jugadas.append(situacion)
        return list(self._siguiente(self.jugadas))

    def redactar(self, pedido: dict[str, Any],
                 al_avanzar: Callable[[str], None] | None = None) -> str:
        """Con `al_avanzar`, avisa el texto preparado entero, como una IA en vivo que lo
        escribió de una vez."""
        self.pedidos_de_redaccion.append(pedido)
        texto = self._siguiente(self.redacciones)
        if al_avanzar is not None:
            al_avanzar(texto)
        return texto

    @staticmethod
    def _siguiente(guion: list):
        if not guion:
            raise GuionAgotado("El guion de la IA se terminó.")
        siguiente = guion.pop(0)
        if isinstance(siguiente, BaseException):
            raise siguiente
        return siguiente
