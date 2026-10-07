"""Los motores de conversación que corre el corredor (E3-8).

`odd/tasks/motor-definitivo.md`, E3-5, "Un solo corredor para los dos motores": la regresión de
la E3-8 corre las mismas conversaciones sobre el motor de la prueba chica (`prueba_chica`) y sobre
el definitivo (`leda.motor`), con el mismo corredor. Lo que el corredor usa de un motor se toma
de su paquete una sola vez, acá, y viaja en un `Motor`: ningún otro módulo del corredor importa
un motor por su nombre.

Los dos motores cumplen el mismo contrato (el definitivo se portó fiel de la prueba chica): las
mismas funciones de turno y de toque, el mismo ciclo, la misma lista cerrada de jugadas y la
misma IA real. Cuando se borre `prueba_chica/`, sale de `MOTORES`.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any, Callable, Mapping

MOTORES = ("leda.motor", "prueba_chica")
POR_OMISION = "leda.motor"


@dataclass(frozen=True)
class Motor:
    """Lo que el corredor usa de un motor de conversación."""

    nombre: str
    procesar_turno: Callable[..., Any]
    procesar_toque: Callable[..., Any]
    Ciclo: type
    FICHAS: Mapping[str, Any]
    palabras: Callable[[str], list[str]]
    sin_significado: Callable[[Any], set[str]]
    IAReal: type
    Tono: type
    Jugada: type


_CARGADOS: dict[str, Motor] = {}


def cargar(nombre: str = POR_OMISION) -> Motor:
    """El motor `nombre` (uno de `MOTORES`), importado una sola vez por proceso."""
    if nombre not in MOTORES:
        raise ValueError(f"No hay un motor {nombre!r}: los que hay son {', '.join(MOTORES)}.")
    if nombre not in _CARGADOS:
        def de(modulo: str):
            return importlib.import_module(f"{nombre}.{modulo}")

        turno, ciclo, fichas, hechos = de("turno"), de("ciclo"), de("fichas"), de("hechos")
        _CARGADOS[nombre] = Motor(
            nombre=nombre,
            procesar_turno=turno.procesar_turno,
            procesar_toque=turno.procesar_toque,
            Ciclo=ciclo.Ciclo,
            FICHAS=fichas.FICHAS,
            palabras=fichas.palabras,
            # Lee el vocabulario del módulo en cada llamada: una prueba que lo cambia, lo ve.
            sin_significado=hechos.sin_significado,
            IAReal=de("ia_real").IAReal,
            Tono=de("instrucciones").Tono,
            Jugada=de("ia").Jugada,
        )
    return _CARGADOS[nombre]
