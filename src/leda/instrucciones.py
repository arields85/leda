"""Las instrucciones de cada circuito, armadas por el código desde una sola fuente
(C0-13 y C0-15, `odd/tasks/circuitos-al-flujo-nuevo.md`).

El código, no el modelo, decide qué lleva cada circuito. Hoy lo usa sólo el alta
conversada; el camino general sigue con su contexto (`contexto.construir`) hasta que
sus circuitos pasen al flujo nuevo.

Orden estable, de lo fijo a lo que cambia, por si el proveedor reutiliza el comienzo
idéntico del texto:

  1. La mecánica del circuito (para el alta, `alta_turno.MECANICA_ALTA`): el
     contrato de salida, lo propio del circuito y las reglas de la personalidad de
     Leda escritas como reglas concretas de ese contrato.
  2. El tono del espacio, desde su pack (`persona_config`): trato, formalidad,
     longitud, emojis. El trato de cada cliente nunca se escribe en el código.

La personalidad (`nucleo/personalidad.md`) no se le manda a la IA: es la referencia
con la que se escribe la mecánica de cada circuito (flujo C3, C0-15). Lo que cambia en
cada turno (los hechos, la conversación) no va acá: viaja aparte.

Cada armado lleva la huella del texto entero, para registrar en la auditoría qué
instrucciones recibió el modelo.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from functools import lru_cache

from . import alta_turno as T

SEPARADOR_DE_BLOQUES = "\n\n---\n\n"

# Tope de las instrucciones estables del alta, en tokens estimados (caracteres / 4).
# Una prueba falla a la vista si se pasa (`tests/test_personalidad_en_mecanica.py`).
TOPE_TOKENS_ALTA = 1300


def tokens_estimados(texto: str) -> int:
    """Estimación barata y determinista: cuatro caracteres por token."""
    return len(texto) // 4


def _huella(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Tono:
    """El tono de un espacio, tal como lo define su pack (`persona`)."""
    nombre_visible: str | None = None
    registro: str | None = None
    formalidad: str | None = None
    longitud: str | None = None
    emojis: bool | None = None


def tono_del_espacio(cur, workspace_id: str) -> Tono | None:
    """El tono del pack del espacio; `None` si el pack no lo define."""
    cur.execute(
        """select nombre_visible, registro, formalidad, longitud, emojis
             from persona_config where workspace_id = %s""",
        (workspace_id,))
    fila = cur.fetchone()
    if fila is None:
        return None
    return Tono(nombre_visible=fila["nombre_visible"], registro=fila["registro"],
                formalidad=fila["formalidad"], longitud=fila["longitud"],
                emojis=fila["emojis"])


def regla_de_emojis(emojis: bool) -> str:
    """La regla de emojis del pack (`persona.emojis`), una sola redacción para
    todos los circuitos que la usan (el alta y la redacción de `redaccion.py`)."""
    if emojis:
        return ("algún emoji ocasional cuando suma calidez o claridad, no en cada "
                "respuesta ni como adorno")
    return "sin emojis"


def _sin_guiones(valor: str) -> str:
    return valor.replace("_", " ")


def bloque_de_tono(tono: Tono | None) -> str:
    """El tono del espacio en instrucciones. Sólo dice lo que el pack define: sin
    tono configurado no inventa un trato."""
    lineas = ["# Tono de este equipo", ""]
    if tono is None:
        lineas.append("Este equipo no definió un tono propio: Leda usa un trato "
                      "neutro y cordial.")
        return "\n".join(lineas)
    if tono.nombre_visible:
        lineas.append(f"- Se presenta como {tono.nombre_visible}.")
    if tono.registro:
        lineas.append(f"- Trata a las personas de {tono.registro}, en todos sus "
                      "mensajes.")
    if tono.formalidad:
        lineas.append(f"- Tono {_sin_guiones(tono.formalidad)}.")
    if tono.longitud:
        lineas.append(f"- Longitud {_sin_guiones(tono.longitud)}.")
    if tono.emojis is not None:
        regla = regla_de_emojis(tono.emojis)
        lineas.append(f"- {regla[0].upper()}{regla[1:]}.")
    return "\n".join(lineas)


@dataclass(frozen=True)
class Instrucciones:
    texto: str
    hash: str          # del texto entero que recibe el modelo

    def auditoria(self) -> dict:
        """Lo que se registra en la auditoría del turno."""
        return {"instrucciones_hash": self.hash}


@lru_cache(maxsize=32)
def instrucciones_alta(tono: Tono | None) -> Instrucciones:
    """Las instrucciones del alta conversada: la mecánica del alta (con las reglas de
    la personalidad adentro) y el tono del pack."""
    texto = SEPARADOR_DE_BLOQUES.join([T.MECANICA_ALTA, bloque_de_tono(tono)])
    return Instrucciones(texto=texto, hash=_huella(texto))


def instrucciones_alta_del_espacio(cur, workspace_id: str) -> Instrucciones:
    return instrucciones_alta(tono_del_espacio(cur, workspace_id))
