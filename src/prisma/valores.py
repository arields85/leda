"""Los valores que un mensaje trae para la pregunta pendiente (ADR 0014,
mecanismo M1).

El modelo interpreta el mensaje y devuelve el valor ya normalizado (una
fecha ISO, el id de una opción, un texto); acá el código lo valida, sin
interpretar nunca texto libre. Son funciones puras: ningún reloj escondido,
ninguna base, ningún transporte.
"""

from __future__ import annotations

from enum import Enum


class TipoValor(str, Enum):
    """Qué tipo de valor espera la pregunta pendiente."""
    FECHA = "fecha"
    OPCION = "opcion"
    TEXTO = "texto"
    ENTIDAD = "entidad"
    NINGUNO = "ninguno"
