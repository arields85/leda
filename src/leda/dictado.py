"""El dictado al cargar una tarea o crear un objetivo en la plataforma, con Gemini en el servidor
(porción J2b de `odd/tasks/plataforma-jerarquias.md`; el objetivo, J3-4b: las instrucciones dicen
qué se dicta, según el formulario).

El navegador graba lo que la persona dicta y lo manda tal cual a la puerta de administración
(`web_app.dictar_al_cargar`); acá se lo pasa a texto con Gemini, como en el otro proyecto
(`docs/research/gemini-voz-del-otro-proyecto.md`, sección 3): el audio en línea y sin convertir,
sin pensar, con temperatura 0 y un tope de salida, y unas instrucciones en castellano con los
nombres del espacio que conviene escribir como están en los datos. Por la API de REST con
`httpx` (sin el SDK), con la clave en su cabecera y nunca en la dirección.

El audio no se guarda ni se registra en ningún lado. Las fallas salen como tres clases con un
motivo saneado (el tipo de la falla o el estado que devolvió Gemini), nunca el audio, el texto,
la clave ni la dirección: quien llama deja el incidente y un aviso humano.

La deuda de la J2b (revisión `review-0f465303e17d9ce6`, J2-26): el plazo de `httpx` es por
operación (conectar, mandar, cada lectura), así que una respuesta que llega de a gotas lo estira
sin fin; la llamada tiene además un plazo total (`PLAZO_TOTAL_S`), debajo del de la web. Y una
transcripción que Gemini cortó por el tope de salida no se devuelve como si fuera todo: vuelve
marcada (`cortada`), para que la persona sepa que falta una parte.

J2-30 (revisión J2-29): el plazo total es real también para el hilo del pedido. Cada operación de
la red (conectar, el TLS, mandar, cada lectura) espera lo suyo o lo que queda del plazo, lo que sea
menos (`_RedConPlazo`, debajo del cliente de `httpx`), así que el hilo no queda colgado después del
plazo (salvo en la búsqueda del nombre del servidor, que el sistema no deja acotar; quien llama
igual deja de esperarlo al vencer).
"""

from __future__ import annotations

import base64
import os
import re
import ssl
import threading
import time
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, NamedTuple

import httpcore
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
# El plazo de la llamada entera, desde que se conecta hasta que llega la respuesta: vencido, Gemini
# no respondió, aunque cada operación haya cumplido el suyo. Debajo de los 45 s de la web.
PLAZO_TOTAL_S = 35.0
# Dos minutos hablados son unas 300 palabras: menos de 1000 fichas.
TOPE_DE_SALIDA = 1024
# Las palabras del espacio para favorecer: las primeras, sin repetir y acotadas.
TOPE_DE_PALABRAS = 80
LARGO_DE_UNA_PALABRA = 120
# Lo que se dicta, según el formulario (J3-4b: `?de=objetivo` en el pedido), y cómo se describe en
# las instrucciones: qué es y qué suele decir la persona. Sin decirlo, una tarea.
LO_QUE_SE_DICTA = {
    "tarea": "una tarea que quiere cargar en la plataforma de gestión de su equipo: qué hay que "
             "hacer, quién, para cuándo y cómo se sabe que quedó hecho",
    "objetivo": "un objetivo que quiere crear en la plataforma de gestión de su equipo: qué se "
                "quiere lograr, de qué es parte, quién lo lleva y para cuándo",
}


def lo_que_se_dicta(de: str | None) -> str:
    """Qué se dicta: `objetivo` si el formulario lo dice; cualquier otra cosa, una tarea."""
    return de if de in LO_QUE_SE_DICTA else "tarea"

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


class Transcripcion(NamedTuple):
    """Lo que se dictó, como texto, y si Gemini lo cortó por el tope de salida (`cortada`): el
    texto es sólo una parte."""

    texto: str
    cortada: bool = False


# Lo que dice Gemini cuando se detuvo por el tope de salida (`finishReason`).
_CORTADA_POR_EL_TOPE = "MAX_TOKENS"


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
    áreas y sus objetivos abiertos, sin repetir. Con las opciones de un objetivo (J3-4, la puerta
    del equipo), los referentes de área con sus áreas y los objetivos de los que puede colgar."""
    palabras: list[str] = []
    for lista, claves in (("integrantes", ("nombre", "area")), ("objetivos", ("titulo",)),
                          ("referentes", ("nombre", "areas")), ("padres", ("titulo",))):
        for fila in opciones.get(lista) or []:
            for clave in claves:
                valor = fila.get(clave)
                for v in (valor if isinstance(valor, list) else [valor]):
                    if not isinstance(v, str):
                        continue
                    v = " ".join(v.split())[:LARGO_DE_UNA_PALABRA]
                    if v and v not in palabras:
                        palabras.append(v)
    return palabras[:TOPE_DE_PALABRAS]


def instrucciones(palabras: Sequence[str], de: str = "tarea") -> str:
    """Qué tiene que hacer Gemini, en castellano: describe el trabajo, sin casos. `de`: qué se
    dicta (`tarea` u `objetivo`, J3-4b)."""
    texto = ("Transcribí fielmente este audio. Es una persona que dicta, en castellano rioplatense, "
             + LO_QUE_SE_DICTA[lo_que_se_dicta(de)] + ". Escribí lo que dice tal como lo dice, con "
             "la puntuación de un texto escrito, sin resumir, sin ordenar y sin agregar nada.")
    if palabras:
        texto += (" Si nombra a alguien, un área o un objetivo de esta lista, escribilo como está "
                  "en ella: " + "; ".join(palabras) + ".")
    return texto + (" Devolvé sólo el texto transcripto, sin comentarios ni formato. Si no se "
                    "entiende nada de lo que dice, no devuelvas nada.")


# El reloj del plazo total (las pruebas ponen uno de mentira).
_reloj = time.monotonic


def _lo_que_queda(limite: float, plazo: float | None, falla: type[Exception]) -> float:
    """El plazo de una operación de la red: el suyo o lo que queda hasta `limite`, lo que sea
    menos. Vencido, `falla` en el momento, sin tocar la red."""
    queda = limite - _reloj()
    if queda <= 0:
        raise falla("plazo_total")
    return queda if plazo is None else min(plazo, queda)


class _FlujoConPlazo(httpcore.NetworkStream):
    """Una conexión cuyas operaciones nunca esperan más allá del plazo total."""

    def __init__(self, flujo: httpcore.NetworkStream, limite: float) -> None:
        self._flujo, self._limite = flujo, limite

    def read(self, max_bytes: int, timeout: float | None = None) -> bytes:
        return self._flujo.read(max_bytes, _lo_que_queda(self._limite, timeout,
                                                         httpcore.ReadTimeout))

    def write(self, buffer: bytes, timeout: float | None = None) -> None:
        self._flujo.write(buffer, _lo_que_queda(self._limite, timeout, httpcore.WriteTimeout))

    def close(self) -> None:
        self._flujo.close()

    def start_tls(self, ssl_context: ssl.SSLContext, server_hostname: str | None = None,
                  timeout: float | None = None) -> httpcore.NetworkStream:
        plazo = _lo_que_queda(self._limite, timeout, httpcore.ConnectTimeout)
        return _FlujoConPlazo(self._flujo.start_tls(ssl_context, server_hostname, plazo),
                              self._limite)

    def get_extra_info(self, info: str) -> Any:
        return self._flujo.get_extra_info(info)


class _RedConPlazo(httpcore.NetworkBackend):
    """La red de `httpcore` con el plazo total en cada operación (J2-30)."""

    def __init__(self, limite: float, red: httpcore.NetworkBackend) -> None:
        self._limite, self._red = limite, red

    def connect_tcp(self, host: str, port: int, timeout: float | None = None,
                    local_address: str | None = None,
                    socket_options: Iterable[Any] | None = None) -> httpcore.NetworkStream:
        plazo = _lo_que_queda(self._limite, timeout, httpcore.ConnectTimeout)
        return _FlujoConPlazo(self._red.connect_tcp(host, port, plazo, local_address,
                                                    socket_options), self._limite)

    def connect_unix_socket(self, path: str, timeout: float | None = None,
                            socket_options: Iterable[Any] | None = None) -> httpcore.NetworkStream:
        plazo = _lo_que_queda(self._limite, timeout, httpcore.ConnectTimeout)
        return _FlujoConPlazo(self._red.connect_unix_socket(path, plazo, socket_options),
                              self._limite)

    def sleep(self, seconds: float) -> None:
        self._red.sleep(seconds)


def _red_de_verdad() -> httpcore.NetworkBackend:
    return httpcore.SyncBackend()


class _TransporteConPlazo(httpx.HTTPTransport):
    """El transporte de `httpx` de siempre, con su conjunto de conexiones sobre `_RedConPlazo`
    (`HTTPTransport` manda cada pedido por `_pool`)."""

    def __init__(self, limite: float) -> None:
        super().__init__()
        self._pool = httpcore.ConnectionPool(ssl_context=httpx.create_ssl_context(),
                                             network_backend=_RedConPlazo(limite,
                                                                          _red_de_verdad()))


def _cliente(limite: float) -> httpx.Client:
    return httpx.Client(transport=_TransporteConPlazo(limite),
                        timeout=httpx.Timeout(PLAZO_DEL_PROVEEDOR_S,
                                              connect=PLAZO_DE_CONEXION_S))


def _con_plazo_total(cliente: httpx.Client, url: str, clave: str, cuerpo: Mapping[str, Any],
                     limite: float) -> httpx.Response:
    """El pedido a Gemini, en un hilo aparte que se espera hasta `limite`. Cada operación de la red
    ya está acotada a ese límite (`_RedConPlazo`); el hilo cubre además lo que no se puede acotar
    (buscar el nombre del servidor). Vencido, el cliente se cierra desde otro hilo, sin esperarlo,
    y es `ProveedorNoResponde("plazo_total")`; una respuesta que llega después del límite, también.
    Una falla del pedido se levanta tal cual, como si se hubiera hecho acá."""
    hecho: dict[str, Any] = {}

    def pedir() -> None:
        try:
            hecho["respuesta"] = cliente.post(url, headers={"x-goog-api-key": clave}, json=cuerpo)
        except BaseException as falla:  # noqa: BLE001 -- se levanta en el hilo de quien llama
            hecho["falla"] = falla

    hilo = threading.Thread(target=pedir, name="dictado-gemini", daemon=True)
    hilo.start()
    hilo.join(max(0.0, limite - _reloj()))
    if hilo.is_alive():
        threading.Thread(target=cliente.close, name="dictado-cerrar", daemon=True).start()
        raise ProveedorNoResponde("plazo_total")
    cliente.close()
    if _reloj() >= limite:
        raise ProveedorNoResponde("plazo_total")
    if "falla" in hecho:
        raise hecho["falla"]
    return hecho["respuesta"]


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


def transcribir(audio: bytes, tipo: str, palabras: Sequence[str],
                de: str = "tarea") -> Transcripcion:
    """El texto de lo que se dictó (`de`: una tarea o un objetivo) y si se cortó por el tope. Una
    sola llamada, sin reintento (la persona puede volver a dictar), con el plazo total. Levanta
    `SinClave`, `ProveedorNoResponde` o `TranscripcionVacia`."""
    clave = os.environ.get(VARIABLE_DE_LA_CLAVE, "").strip()
    if not clave:
        raise SinClave(f"falta {VARIABLE_DE_LA_CLAVE}")
    cuerpo = {
        "contents": [{"role": "user", "parts": [
            {"text": instrucciones(palabras, de)},
            {"inline_data": {"mime_type": tipo,
                             "data": base64.b64encode(audio).decode("ascii")}}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": TOPE_DE_SALIDA,
                             "thinkingConfig": {"thinkingBudget": 0}},
    }
    limite = _reloj() + PLAZO_TOTAL_S
    try:
        respuesta = _con_plazo_total(_cliente(limite),
                                     f"{GEMINI_BASE}/models/{MODELO}:generateContent",
                                     clave, cuerpo, limite)
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
    return Transcripcion(texto, cortada=primero.get("finishReason") == _CORTADA_POR_EL_TOPE)
