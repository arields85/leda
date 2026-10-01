"""Los valores que un mensaje trae para la pregunta pendiente (ADR 0014,
mecanismo M1).

El modelo interpreta el mensaje y devuelve el valor ya normalizado (una
fecha ISO, el id de una opción, un texto); acá el código lo valida, sin
interpretar nunca texto libre: ni expresiones regulares ni coincidencia de
etiquetas. Son funciones puras: ningún reloj escondido (el día de hoy viaja
en `ValorEsperado.hoy`), ninguna base, ningún transporte.

Un valor que no sirve se rechaza con la razón real y qué sirve, en castellano
neutro y sin jerga. Un valor que falta nunca se inventa: es `SIN_VALOR` y la
pregunta queda abierta (quien llama registra el incidente).

Hay un tercer resultado cerrado entre el valor y la falla: la respuesta es de
verdad una respuesta pero está incompleta o es ambigua para el tipo esperado
("la semana que viene": ¿qué día?). El modelo lo dice con `falta`, una lista
cerrada por tipo (`FALTAS_POR_TIPO`); el código lo trata como conversación
normal (`VALOR_INCOMPLETO`): la misma pregunta sigue abierta y se repregunta con
palabras propias, sin incidente. El incidente queda para una falla real del
contrato: salida mal formada, o ni valor ni `falta`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class TipoValor(str, Enum):
    """Qué tipo de valor espera la pregunta pendiente."""
    FECHA = "fecha"
    OPCION = "opcion"
    TEXTO = "texto"
    ENTIDAD = "entidad"
    NINGUNO = "ninguno"


OPCION_NINGUNA = "ninguna"
"""El id con que el modelo dice que el mensaje rechaza todas las opciones."""

CAMPOS_DEL_VALOR = ("fecha_iso", "opcion_id", "texto", "falta")
"""Las únicas claves de `valor`, el objeto cerrado que devuelve el ruteo."""

FALTA_DIA = "dia"
FALTA_CUAL = "cual"
FALTA_DETALLE = "detalle"

FALTAS_POR_TIPO = {
    TipoValor.FECHA: (FALTA_DIA,),
    TipoValor.OPCION: (FALTA_CUAL,),
    TipoValor.TEXTO: (FALTA_DETALLE,),
    TipoValor.ENTIDAD: (FALTA_DETALLE,),
}
"""Qué puede decir el modelo que falta, por tipo esperado: una fecha dada como
período sin un día concreto, una opción que podría ser más de una, un texto o
una referencia demasiado general para servir. Lista cerrada: la palabra que
diga la persona nunca entra acá."""

FALTA_POR_DEFECTO = {TipoValor.FECHA: FALTA_DIA, TipoValor.OPCION: FALTA_CUAL}
"""Lo que falta cuando la persona confirmó que su mensaje es la respuesta y el
modelo no pudo resolverlo a un valor del tipo: una respuesta que no se puede
tomar tal cual es una respuesta incompleta, no una falla."""

FALTAS_VALIDAS = tuple(dict.fromkeys(
    f for faltas in FALTAS_POR_TIPO.values() for f in faltas))
"""Todas las faltas que acepta el sobre del ruteo (la de cada tipo la valida
`validar_valor`)."""


@dataclass(frozen=True)
class Opcion:
    """Una opción ofrecida en pantalla, con el id con el que el modelo la
    nombra (nunca por su etiqueta)."""
    id: str
    etiqueta: str


def opciones_numeradas(etiquetas) -> tuple[Opcion, ...]:
    """Las opciones ofrecidas con ids estables: "1", "2", ... en el orden en
    que se mostraron."""
    return tuple(Opcion(str(n), etiqueta)
                 for n, etiqueta in enumerate(etiquetas, start=1))


@dataclass(frozen=True)
class ValorEsperado:
    """Qué espera la pregunta pendiente: el tipo, las opciones ofrecidas (con
    `OPCION`) y el día de hoy en la zona del espacio (con `FECHA`: es lo que
    deja resolver "mañana" y lo que separa una fecha pasada de una vigente).
    `confirmado`: la persona ya confirmó con un botón que el mensaje es la
    respuesta a esta pregunta (el modelo no vuelve a dudar de eso)."""
    tipo: TipoValor
    opciones: tuple[Opcion, ...] = ()
    hoy: date | None = None
    confirmado: bool = False


class MotivoRechazo(str, Enum):
    SIN_VALOR = "sin_valor"
    VALOR_INCOMPLETO = "valor_incompleto"
    FECHA_INVALIDA = "fecha_invalida"
    FECHA_PASADA = "fecha_pasada"
    OPCION_DESCONOCIDA = "opcion_desconocida"
    TEXTO_VACIO = "texto_vacio"
    TEXTO_LARGO = "texto_largo"


@dataclass(frozen=True)
class Aceptado:
    """El valor ya validado: una `date` para `FECHA`, el id de la opción (o
    `OPCION_NINGUNA`) para `OPCION`, el texto recortado para `TEXTO` y
    `ENTIDAD`, y `None` si la pregunta no esperaba ninguno."""
    tipo: TipoValor
    valor: date | str | None


@dataclass(frozen=True)
class Rechazado:
    """Por qué no sirve (`razon`) y qué sirve (`se_acepta`), ya en las
    palabras que lee la persona."""
    motivo: MotivoRechazo
    razon: str
    se_acepta: str

    @property
    def mensaje(self) -> str:
        return f"{self.razon} {self.se_acepta}"


def _se_acepta_fecha() -> str:
    return "Decime una fecha desde hoy en adelante."


def _se_acepta_opcion(opciones: tuple[Opcion, ...]) -> str:
    etiquetas = ", ".join(f"«{o.etiqueta}»" for o in opciones)
    return f"Elegí una de estas: {etiquetas}."


def _se_acepta_texto() -> str:
    return "Escribilo de nuevo."


def _incompleto(falta: str | None, esperado: ValorEsperado) -> Rechazado | None:
    """La respuesta incompleta o ambigua que dijo el modelo (`falta`), con lo
    que falta y qué sirve en palabras propias; `None` si no hay `falta` o no es
    una de las del tipo esperado (eso es un valor que falta, no una respuesta
    parcial)."""
    if falta not in FALTAS_POR_TIPO.get(esperado.tipo, ()):
        return None
    if falta == FALTA_DIA:
        return Rechazado(
            MotivoRechazo.VALOR_INCOMPLETO,
            "Con eso no me alcanza para fijar un día.",
            "Decime el día exacto, por ejemplo «el viernes» o «el 4 de octubre».")
    if falta == FALTA_CUAL:
        return Rechazado(
            MotivoRechazo.VALOR_INCOMPLETO,
            "Lo que dijiste puede ser más de una de las opciones.",
            _se_acepta_opcion(esperado.opciones))
    return Rechazado(
        MotivoRechazo.VALOR_INCOMPLETO, "Eso es muy general para usarlo así.",
        "Contame un poco más de detalle, con tus palabras.")


def _cadena(valor, campo: str) -> str | None:
    """El campo del valor como texto recortado, o `None` si no hay o no es un
    texto: una forma inesperada es lo mismo que no traer valor."""
    if not isinstance(valor, dict):
        return None
    dato = valor.get(campo)
    return dato.strip() if isinstance(dato, str) else None


def _fecha(valor, esperado: ValorEsperado) -> Aceptado | Rechazado:
    if esperado.hoy is None:
        raise ValueError("Validar una fecha necesita el día de hoy.")
    iso = _cadena(valor, "fecha_iso")
    if not iso:
        incompleto = _incompleto(_cadena(valor, "falta"), esperado)
        if incompleto:
            return incompleto
        return Rechazado(MotivoRechazo.SIN_VALOR,
                         "No pude entender qué fecha querés.", _se_acepta_fecha())
    try:
        # ISO extendido y nada más: `fromisoformat` también acepta formas
        # compactas y semanales que el modelo no tiene por qué devolver.
        if len(iso) != 10 or iso[4] != "-" or iso[7] != "-":
            raise ValueError(iso)
        fecha = datetime.strptime(iso, "%Y-%m-%d").date()
    except ValueError:
        return Rechazado(MotivoRechazo.FECHA_INVALIDA,
                         "Esa fecha no existe.", _se_acepta_fecha())
    if fecha < esperado.hoy:
        return Rechazado(MotivoRechazo.FECHA_PASADA,
                         "Esa fecha ya pasó.", _se_acepta_fecha())
    return Aceptado(TipoValor.FECHA, fecha)


def _opcion(valor, esperado: ValorEsperado) -> Aceptado | Rechazado:
    se_acepta = _se_acepta_opcion(esperado.opciones)
    opcion_id = _cadena(valor, "opcion_id")
    if not opcion_id:
        incompleto = _incompleto(_cadena(valor, "falta"), esperado)
        if incompleto:
            return incompleto
        return Rechazado(MotivoRechazo.SIN_VALOR,
                         "No pude saber cuál elegiste.", se_acepta)
    if opcion_id == OPCION_NINGUNA or any(
            o.id == opcion_id for o in esperado.opciones):
        return Aceptado(TipoValor.OPCION, opcion_id)
    return Rechazado(MotivoRechazo.OPCION_DESCONOCIDA,
                     "Esa opción no está entre las que te ofrecí.", se_acepta)


def _texto(valor, esperado: ValorEsperado,
           limite_texto: int) -> Aceptado | Rechazado:
    texto = _cadena(valor, "texto")
    if texto is None:
        incompleto = _incompleto(_cadena(valor, "falta"), esperado)
        if incompleto:
            return incompleto
        return Rechazado(MotivoRechazo.SIN_VALOR,
                         "No pude tomar ese texto.", _se_acepta_texto())
    if not texto:
        return Rechazado(MotivoRechazo.TEXTO_VACIO,
                         "Ese texto está vacío.", _se_acepta_texto())
    if len(texto) > limite_texto:
        return Rechazado(
            MotivoRechazo.TEXTO_LARGO,
            f"Ese texto pasa de {limite_texto} caracteres.",
            "Acortalo y mandámelo de nuevo.")
    return Aceptado(esperado.tipo, texto)


def validar_valor(valor, esperado: ValorEsperado, *,
                  limite_texto: int) -> Aceptado | Rechazado:
    """Valida el `valor` del ruteo contra lo que la pregunta pendiente
    esperaba. `valor` es el objeto cerrado del ruteo (o `None`/vacío si el
    modelo no trajo ninguno); sólo se mira el campo que corresponde al tipo
    esperado."""
    if esperado.tipo is TipoValor.FECHA:
        return _fecha(valor, esperado)
    if esperado.tipo is TipoValor.OPCION:
        return _opcion(valor, esperado)
    if esperado.tipo in (TipoValor.TEXTO, TipoValor.ENTIDAD):
        return _texto(valor, esperado, limite_texto)
    return Aceptado(TipoValor.NINGUNO, None)
