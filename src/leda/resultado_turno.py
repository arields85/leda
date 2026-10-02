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

# El nombre con que Leda se presenta: siempre es un nombre conocido del turno.
NOMBRE_ASISTENTE = "Leda"


@dataclass(frozen=True)
class Cambio:
    """Algo que este turno cambió de verdad."""
    sujeto: str   # "la tarea «Revisar PLC»"
    que: str      # "quedó en curso"
    # Identificador cerrado del efecto: el modelo lo devuelve en `afirma` para
    # decir qué efectos cuenta su texto, y el verificador lo compara con los
    # hechos. Sin uno propio se numera por posición (`ids_de_cambios`).
    id: str = ""


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
    # Identificador cerrado del dato (el campo): el modelo lo devuelve en
    # `pregunta` para decir qué dato pide su texto. Sin uno propio, `dato`.
    campo: str = ""

    @property
    def clave(self) -> str:
        return self.campo or self.dato


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
class Rechazo:
    """Un valor que el código no aceptó: por qué no sirve y qué sirve, ya en
    las palabras que lee la persona (`valores.Rechazado`)."""
    razon: str       # "Esa fecha ya pasó."
    se_acepta: str   # "Decime una fecha desde hoy en adelante."


@dataclass(frozen=True)
class Resumen:
    """El resumen de algo para que la persona lo revise: un título, una línea
    "dato: valor" por cada dato que tiene y lo que pasa con el botón que
    sigue. Una línea sin valor no se arma: no se muestra un dato que nadie
    dio."""
    titulo: str
    lineas: tuple[tuple[str, str], ...]
    cierre: str


@dataclass(frozen=True)
class ResultadoTurno:
    cambios: tuple[Cambio, ...] = ()
    sin_cambios: tuple[SinCambio, ...] = ()
    estado: tuple[Estado, ...] = ()
    falta: Falta | None = None
    opciones: tuple[OpcionDisponible, ...] = ()
    valores_aceptados: tuple[ValorAceptado, ...] = ()
    rechazo: Rechazo | None = None
    resumen: Resumen | None = None
    # Lo que el turno entendió de la persona (un valor ya validado, mostrado como
    # se va a ver). Es contexto para que el modelo lo diga en su mensaje: la
    # plantilla de B no lo dice, así que B no cambia.
    entendido: tuple[ValorAceptado, ...] = ()
    # Lo que la persona dijo cuando era otra cosa que lo pedido (un saludo, un
    # agradecimiento): contexto para que el modelo conteste en pocas palabras
    # antes de pedir el dato. B no lo dice.
    charla: str | None = None
    # Los nombres que el turno ya conoce (quien escribe): el verificador los deja
    # decir sin que estén entre los hechos. No se le cuentan al modelo.
    nombres_conocidos: tuple[str, ...] = ()

    @property
    def vacio(self) -> bool:
        """Sin ningún hecho que decir: las opciones solas no son un mensaje."""
        return not (self.cambios or self.sin_cambios or self.estado
                    or self.falta or self.valores_aceptados or self.rechazo
                    or self.resumen)


def ids_de_cambios(resultado: ResultadoTurno) -> tuple[str, ...]:
    """Los identificadores cerrados de los efectos del turno, en orden: el `id`
    de cada cambio o, si no tiene, `c1`, `c2`, ..."""
    return tuple(c.id or f"c{i}" for i, c in enumerate(resultado.cambios, 1))
