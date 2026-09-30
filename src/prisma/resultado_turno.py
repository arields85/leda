"""El resultado de un turno: los hechos, sin redactar (ADR 0014, etapa 6,
mecanismo M2).

Lo produce el código después de validar y ejecutar; de acá salen el texto
(`redaccion.redactar`) y las opciones (los botones), nunca del texto del
modelo. No lleva chat, ni teclado, ni formato de ningún transporte
(`docs/architecture/frontera.md`, regla 2): el transporte lo dibuja.

Los textos de cada hecho (`sujeto`, `que`, `motivo`, ...) son frases cortas
ya legibles para una persona, sin claves internas: el resultado se arma con
lo que el código leyó de la base, no con lo que el modelo dijo.
"""

from __future__ import annotations

from dataclasses import dataclass

from .valores import TipoValor


@dataclass(frozen=True)
class Cambio:
    """Algo que este turno cambió de verdad."""
    sujeto: str   # "la tarea «Revisar PLC»"
    que: str      # "quedó en curso"


@dataclass(frozen=True)
class SinCambio:
    """Algo que se pidió y no cambió, con la razón real."""
    sujeto: str
    motivo: str   # "ya estaba en curso"


@dataclass(frozen=True)
class Estado:
    """Cómo está algo ahora, leído de la base."""
    sujeto: str   # "«Revisar PLC»"
    estado: str   # "en curso"


@dataclass(frozen=True)
class Falta:
    """El dato que se está pidiendo y qué tipo de valor se espera."""
    dato: str                    # "la fecha objetivo"
    tipo: TipoValor
    pregunta: str | None = None  # la pregunta tal como se hace, si ya existe


@dataclass(frozen=True)
class OpcionDisponible:
    """Algo que el sistema puede hacer de verdad a continuación: el
    transporte la dibuja como un botón."""
    etiqueta: str
    accion: str


@dataclass(frozen=True)
class ValorAceptado:
    """Un valor que el código interpretó y validó, mostrado para que la
    persona lo confirme (por ejemplo la fecha ya resuelta)."""
    dato: str        # "la fecha objetivo"
    mostrado: str    # "04/10/2026"


@dataclass(frozen=True)
class ResultadoTurno:
    cambios: tuple[Cambio, ...] = ()
    sin_cambios: tuple[SinCambio, ...] = ()
    estado: tuple[Estado, ...] = ()
    falta: Falta | None = None
    opciones: tuple[OpcionDisponible, ...] = ()
    valores_aceptados: tuple[ValorAceptado, ...] = ()

    @property
    def vacio(self) -> bool:
        """Sin ningún hecho que decir: las opciones solas no son un mensaje."""
        return not (self.cambios or self.sin_cambios or self.estado
                    or self.falta or self.valores_aceptados)
