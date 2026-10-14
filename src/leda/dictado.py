"""El dictado al cargar una tarea en la plataforma, con Gemini en el servidor (porción J2b de
`odd/tasks/plataforma-jerarquias.md`).

El navegador graba lo que la persona dicta y lo manda tal cual a la puerta de administración
(`web_app.dictar_al_cargar`); acá se lo pasa a texto con Gemini, como en el otro proyecto
(`docs/research/gemini-voz-del-otro-proyecto.md`, sección 3): el audio en línea y sin convertir,
sin pensar, con temperatura 0 y un tope de salida, y unas instrucciones en castellano con los
nombres del espacio que conviene escribir como están en los datos. Por la API de REST con
`httpx` (sin el SDK), con la clave en su cabecera y nunca en la dirección.

El audio no se guarda ni se registra en ningún lado. Las fallas salen como tres clases con un
motivo saneado (el tipo de la falla o el estado que devolvió Gemini), nunca el audio, el texto,
la clave ni la dirección: quien llama deja el incidente y un aviso humano.
"""

from __future__ import annotations

import base64
import os
import re
from collections.abc import Mapping, Sequence
from typing import Any

import httpx

from .llm import GEMINI_BASE

MODELO = "gemini-3.8-flash"
VARIABLE_DE_LA_CLAVE = "LEDA_GEMINI_API_KEY"

# Dos minutos de dictado en opus o aac son menos de 2 MB; 10 MB deja margen para un formato sin
# comprimir, y en base64 queda debajo del tope de 20 MB de un pedido en línea de Gemini.
TAMANO_MAXIMO = 10 * 1024 * 1024
# Los formatos que dan los celulares al grabar (`MediaRecorder`: webm/opus en Android y en las
# computadoras, mp4/aac en el iPhone) y los que Gemini nombra como audio. Se mandan sin sus
# parámetros (`;codecs=opus`).
TIPOS_DE_AUDIO = frozenset({
    "audio/webm", "audio/ogg", "audio/mp4", "audio/x-m4a", "audio/m4a", "audio/aac",
    "audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/wave", "audio/flac",
    "audio/aiff", "audio/x-aiff"})
# El plazo de Gemini queda debajo del de la web, que corta a los 45 s (`web/src/admin/api.ts`,
# `DICTATION_TIMEOUT_MS`): una llamada trabada nunca sobrevive a quien espera.
PLAZO_DEL_PROVEEDOR_S = 30.0
PLAZO_DE_CONEXION_S = 5.0
# Dos minutos hablados son unas 300 palabras: menos de 1000 fichas.
TOPE_DE_SALIDA = 1024
# Las palabras del espacio para favorecer: las primeras, sin repetir y acotadas.
TOPE_DE_PALABRAS = 80
LARGO_DE_UNA_PALABRA = 120

_ESTADO_DE_GEMINI = re.compile(r"^[A-Z_]{1,40}$")


class SinClave(Exception):
    """Falta la clave de Gemini en el entorno del servidor."""


class ProveedorNoResponde(Exception):
    """Gemini no respondió o su respuesta no se pudo leer; `motivo` está saneado."""

    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


class TranscripcionVacia(Exception):
    """Gemini respondió, pero sin texto: no se entendió nada."""


def tipo_de_audio(content_type: str | None) -> str | None:
    """El tipo del audio sin sus parámetros y en minúsculas, si es uno de los admitidos."""
    tipo = (content_type or "").split(";")[0].strip().lower()
    return tipo if tipo in TIPOS_DE_AUDIO else None


def tramo_de_tamano(n: int) -> str:
    """El tamaño del audio para la auditoría, por tramos (nunca el audio)."""
    for tope, nombre in ((256 * 1024, "hasta_256_kb"), (1024 * 1024, "hasta_1_mb"),
                         (4 * 1024 * 1024, "hasta_4_mb")):
        if n <= tope:
            return nombre
    return "hasta_10_mb"


def palabras_del_espacio(opciones: Mapping[str, Any]) -> list[str]:
    """Los nombres de ese espacio (de `opciones_de_la_carga`, nada de otro): sus integrantes, sus
    áreas y sus objetivos abiertos, sin repetir."""
    palabras: list[str] = []
    for lista, claves in (("integrantes", ("nombre", "area")), ("objetivos", ("titulo",))):
        for fila in opciones.get(lista) or []:
            for clave in claves:
                valor = fila.get(clave)
                if not isinstance(valor, str):
                    continue
                valor = " ".join(valor.split())[:LARGO_DE_UNA_PALABRA]
                if valor and valor not in palabras:
                    palabras.append(valor)
    return palabras[:TOPE_DE_PALABRAS]


def instrucciones(palabras: Sequence[str]) -> str:
    """Qué tiene que hacer Gemini, en castellano: describe el trabajo, sin casos."""
    texto = ("Transcribí fielmente este audio. Es una persona que dicta, en castellano rioplatense, "
             "una tarea que quiere cargar en la plataforma de gestión de su equipo: qué hay que "
             "hacer, quién, para cuándo y cómo se sabe que quedó hecho. Escribí lo que dice tal "
             "como lo dice, con la puntuación de un texto escrito, sin resumir, sin ordenar y sin "
             "agregar nada.")
    if palabras:
        texto += (" Si nombra a alguien, un área o un objetivo de esta lista, escribilo como está "
                  "en ella: " + "; ".join(palabras) + ".")
    return texto + (" Devolvé sólo el texto transcripto, sin comentarios ni formato. Si no se "
                    "entiende nada de lo que dice, no devuelvas nada.")


def _cliente() -> httpx.Client:
    return httpx.Client(timeout=httpx.Timeout(PLAZO_DEL_PROVEEDOR_S,
                                              connect=PLAZO_DE_CONEXION_S))


def _motivo_de_la_respuesta(respuesta: httpx.Response) -> str:
    """`status_429 RESOURCE_EXHAUSTED`: el código y, si viene, el estado de Gemini (una palabra
    en mayúsculas); nunca su mensaje, que puede repetir lo que se mandó."""
    motivo = f"status_{respuesta.status_code}"
    try:
        estado = (respuesta.json().get("error") or {}).get("status")
    except (ValueError, AttributeError):
        estado = None
    if isinstance(estado, str) and _ESTADO_DE_GEMINI.match(estado):
        motivo += f" {estado}"
    return motivo


def transcribir(audio: bytes, tipo: str, palabras: Sequence[str]) -> str:
    """El texto de lo que se dictó. Una sola llamada, sin reintento (la persona puede volver a
    dictar). Levanta `SinClave`, `ProveedorNoResponde` o `TranscripcionVacia`."""
    clave = os.environ.get(VARIABLE_DE_LA_CLAVE, "").strip()
    if not clave:
        raise SinClave(f"falta {VARIABLE_DE_LA_CLAVE}")
    cuerpo = {
        "contents": [{"role": "user", "parts": [
            {"text": instrucciones(palabras)},
            {"inline_data": {"mime_type": tipo,
                             "data": base64.b64encode(audio).decode("ascii")}}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": TOPE_DE_SALIDA,
                             "thinkingConfig": {"thinkingBudget": 0}},
    }
    try:
        with _cliente() as cliente:
            respuesta = cliente.post(f"{GEMINI_BASE}/models/{MODELO}:generateContent",
                                     headers={"x-goog-api-key": clave}, json=cuerpo)
    except httpx.HTTPError as falla:
        # Sólo el tipo: el mensaje de `httpx` puede traer la dirección.
        raise ProveedorNoResponde(type(falla).__name__) from None
    if respuesta.status_code != 200:
        raise ProveedorNoResponde(_motivo_de_la_respuesta(respuesta))
    try:
        datos = respuesta.json()
    except ValueError:
        raise ProveedorNoResponde("respuesta_ilegible") from None
    candidatos = datos.get("candidates") if isinstance(datos, dict) else None
    if not isinstance(candidatos, list) or not candidatos:
        raise ProveedorNoResponde("sin_candidatos")
    primero = candidatos[0] if isinstance(candidatos[0], dict) else {}
    contenido = primero.get("content") if isinstance(primero.get("content"), dict) else {}
    partes = contenido.get("parts") if isinstance(contenido.get("parts"), list) else []
    texto = "".join(p.get("text", "") for p in partes
                    if isinstance(p, dict) and isinstance(p.get("text"), str)).strip()
    if not texto:
        raise TranscripcionVacia("sin texto")
    return texto
