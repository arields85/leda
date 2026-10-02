"""Despachador de la cola de salida.

Leda nunca llama a Telegram: escribe en `message_outbox` y este worker
entrega. Eso da tres cosas de una sola vez:

  - idempotencia, porque la clave de deduplicación sobrevive a un reinicio;
  - confirmación humana, que es un estado de la misma tabla;
  - tope de mensajes por persona, que se aplica al despachar y no al generar,
    así se cuenta lo que efectivamente llega.

El transporte está detrás de una interfaz para poder probar todo el circuito
sin tocar Telegram.
"""

from __future__ import annotations

import contextvars
import json
import random
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import NamedTuple, Protocol

import psycopg
from psycopg.types.json import Jsonb

from . import saludo
from .calendario import Calendario
from .incidentes import (ETAPA_ENTREGA_AVISO_ADMIN, ETAPA_ENTREGA_MENSAJE,
                         REFERENCIA_ADMIN_NOTICE, redactar_secreto_telegram,
                         registrar_incidente)
from .salida import (ETIQUETA_COPIAR, cabe_en_boton_de_copiar, entidad_de_bloque,
                     prepare_buttons, prepare_payload)


class ErrorTelegram(RuntimeError):
    """Error al llamar a la API de Telegram, ya traducido: nunca lleva la
    URL del pedido -- la URL de la API de Telegram lleva el token del bot
    (`/bot<token>/`), y el mensaje de httpx (y su `repr`) la incluye
    entera. Sólo el tipo de error original, el estado HTTP si lo hay, y la
    `description` que Telegram manda en el cuerpo cuando la hay. Seguro de
    guardar, imprimir o auditar tal cual (R1-001, revisión 2026-09-28)."""


def _descripcion_telegram(respuesta) -> str | None:
    """La `description` del cuerpo de una respuesta de error de Telegram,
    si la hay y el cuerpo es JSON -- nunca nada más de la respuesta ni del
    pedido que la originó."""
    try:
        cuerpo = respuesta.json()
    except Exception:  # noqa: BLE001 -- el cuerpo puede no ser JSON
        return None
    return cuerpo.get("description") if isinstance(cuerpo, dict) else None


def _mensaje_seguro_http(e: Exception) -> str:
    """Describe cualquier error de red sin su mensaje original -- el de
    httpx incluye la URL entera. Sirve para un error de la API de
    Telegram o de cualquier otra: sin `.response`, sólo queda el tipo."""
    respuesta = getattr(e, "response", None)
    if respuesta is None:
        return type(e).__name__
    base = f"{type(e).__name__} HTTP {respuesta.status_code}"
    detalle = _descripcion_telegram(respuesta)
    return f"{base}: {detalle}" if detalle else base


def texto_error_seguro(e: Exception) -> str:
    """Texto de un error seguro de imprimir o guardar -- nunca la URL de
    la API de Telegram. Sirve tanto para un `ErrorTelegram` ya traducido
    (por `pedido_telegram`) como para cualquier otro error que todavía no
    pasó por ahí."""
    return str(e) if isinstance(e, ErrorTelegram) else _mensaje_seguro_http(e)


def pedido_telegram(fn, *args, **kwargs):
    """Ejecuta `fn(*args, **kwargs)` -- un pedido a la API de Telegram, o
    su `raise_for_status` -- y traduce cualquier excepción a
    `ErrorTelegram` antes de dejarla salir. Es el único lugar por donde
    puede escaparse un error con la URL (y el token) sin traducir, así que
    toda llamada a la API de Telegram pasa por acá (R1-001, revisión
    2026-09-28). `from None` corta la cadena: ni el `repr` ni un traceback
    del error ya traducido arrastran el original."""
    try:
        return fn(*args, **kwargs)
    except Exception as e:  # noqa: BLE001 -- se traduce, nunca se deja escapar
        raise ErrorTelegram(_mensaje_seguro_http(e)) from None


class Boton(NamedTuple):
    """Un botón inline. Con `copiar` es el botón de copiar de Telegram
    (`copy_text`, T9-R1c-3): no lleva callback."""
    etiqueta: str
    callback_data: str
    copiar: str | None = None


class Entregado(NamedTuple):
    """Lo que se entregó. Es tupla para que `(chat_id, texto)` siga sirviendo.
    `bloque` es el bloque que se copia con un toque, si el mensaje lo llevaba."""
    chat_id: int
    texto: str
    botones: list[Boton]
    bloque: str | None = None


class Transporte(Protocol):
    def enviar(self, chat_id: int, texto: str,
               botones: list[Boton] | None = None) -> int:
        """Devuelve el identificador del mensaje entregado. Un mensaje con un
        bloque copiable (T9-R1c-3) se entrega con `bloque=...` además: sólo los
        mensajes que lo llevan pasan ese argumento."""

    def quitar_botones(self, chat_id: int, message_id: int) -> None:
        """Le saca los botones a un mensaje ya entregado (C0-6). Una falla sale
        como excepción; `_quitar_botones_resueltos` decide qué significa."""


@dataclass
class TransporteDePrueba:
    enviados: list[Entregado] = field(default_factory=list)
    falla_en: set[int] = field(default_factory=set)
    # C0-6: `(chat_id, message_id)` de cada mensaje al que se le quitaron los
    # botones, y la excepción con que falla quitarlos, si se quiere probar una.
    quitados: list[tuple[int, int]] = field(default_factory=list)
    falla_al_quitar: Exception | None = None

    def enviar(self, chat_id: int, texto: str,
               botones: list[Boton] | None = None,
               bloque: str | None = None) -> int:
        prepared_buttons = prepare_buttons(botones or [])
        payload = prepare_payload(
            texto, dedupe_key="transport", has_buttons=bool(prepared_buttons),
        )[0]
        if bloque is not None:
            entidad_de_bloque(payload.text, bloque)
        if chat_id in self.falla_en:
            raise ConnectionError(f"no se pudo entregar a {chat_id}")
        self.enviados.append(Entregado(
            chat_id, payload.text, [Boton(*button) for button in prepared_buttons],
            bloque))
        return len(self.enviados)

    def quitar_botones(self, chat_id: int, message_id: int) -> None:
        if self.falla_al_quitar is not None:
            raise self.falla_al_quitar
        self.quitados.append((chat_id, message_id))


class TransporteTelegram:
    def __init__(self, token: str, cliente=None) -> None:
        import httpx
        self._url = f"https://api.telegram.org/bot{token}/sendMessage"
        self._url_botones = (
            f"https://api.telegram.org/bot{token}/editMessageReplyMarkup")
        self._cliente = cliente or httpx.Client(timeout=15)

    def enviar(self, chat_id: int, texto: str,
               botones: list[Boton] | None = None,
               bloque: str | None = None) -> int:
        prepared_buttons = prepare_buttons(botones or [])
        payload = prepare_payload(
            texto, dedupe_key="transport", has_buttons=bool(prepared_buttons),
        )[0]
        cuerpo: dict = {"chat_id": chat_id, "text": payload.text,
                         "disable_notification": False}
        if bloque is not None:
            # El bloque que se copia con un toque (T9-R1c-3): una entidad `pre`
            # sobre el final del texto que de verdad se manda.
            cuerpo["entities"] = [entidad_de_bloque(payload.text, bloque)]
        if prepared_buttons:
            # Uno por fila: las etiquetas son nombres de personas o frases
            # cortas, y en el teléfono dos por fila se cortan.
            cuerpo["reply_markup"] = {"inline_keyboard": [
                [{"text": label, "copy_text": {"text": resto[0]}} if resto
                 else {"text": label, "callback_data": callback}]
                for label, callback, *resto in prepared_buttons]}
        r = pedido_telegram(self._cliente.post, self._url, json=cuerpo)
        pedido_telegram(r.raise_for_status)
        return r.json()["result"]["message_id"]

    def quitar_botones(self, chat_id: int, message_id: int) -> None:
        """Un teclado vacío saca los botones; el texto del mensaje no cambia."""
        r = pedido_telegram(
            self._cliente.post, self._url_botones,
            json={"chat_id": chat_id, "message_id": message_id,
                  "reply_markup": {"inline_keyboard": []}})
        pedido_telegram(r.raise_for_status)

    def cerrar(self) -> None:
        """Cierra el cliente HTTP propio. Lo usa `ciclo.Ciclo` al reemplazar
        un transporte cacheado cuyo token cambió."""
        try:
            self._cliente.close()
        except Exception:  # noqa: BLE001 -- cierre best-effort
            pass


def _close_client_bounded(client, timeout: float) -> None:
    def close() -> None:
        try:
            client.close()
        except Exception:  # noqa: BLE001 - cleanup must not affect the turn
            pass

    try:
        thread = threading.Thread(
            target=close, name="leda-typing-client-close", daemon=True)
        thread.start()
        thread.join(timeout=timeout)
    except Exception:  # noqa: BLE001 - cosmetic cleanup remains best effort
        pass


# Indicador de actividad (ADR 0011, decisión 2): "escribiendo…"
# (`sendChatAction`) y, en chat privado, un borrador nativo
# (`sendMessageDraft`), sembrado con el carácter invisible U+2063. Nunca
# texto vacío, aunque la API admita un placeholder vacío desde Bot API
# 10.0 -- cambiar la semilla es una decisión visual aparte, no un reemplazo
# silencioso (pack recuperado LEDA-PACK-RECONSTRUCCION-20260925/05).
SEMILLA_INDICADOR = "⁣"


def _enviar_chat_action(http, token: str, chat_id: int) -> None:
    pedido_telegram(
        http.post, f"https://api.telegram.org/bot{token}/sendChatAction",
        json={"chat_id": chat_id, "action": "typing"})


def _enviar_borrador_semilla(http, token: str, chat_id: int, draft_id: int) -> None:
    pedido_telegram(
        http.post, f"https://api.telegram.org/bot{token}/sendMessageDraft",
        json={"chat_id": chat_id, "draft_id": draft_id, "text": SEMILLA_INDICADOR})


class _RitmoTelegram(Exception):
    """Telegram pidió ir más despacio (HTTP 429): no es una falla del stream, se
    espera lo que pide y se sigue."""

    def __init__(self, espera: float) -> None:
        super().__init__(f"Telegram pidió esperar {espera} s")
        self.espera = espera


# Lo más que se espera ante un 429 antes de volver a intentar el borrador: el
# mensaje real sale igual, así que no vale la pena esperar más.
ESPERA_MAXIMA_RITMO = 2.0


def _enviar_borrador_texto(http, token: str, chat_id: int, draft_id: int,
                           texto: str) -> None:
    """El mismo borrador nativo de la semilla, con texto: Telegram lo reemplaza
    (mismo `draft_id`) y lo muestra creciendo. Un 429 se distingue (`_RitmoTelegram`)
    y cualquier otro error HTTP se levanta: antes se ignoraban en silencio."""
    r = pedido_telegram(
        http.post, f"https://api.telegram.org/bot{token}/sendMessageDraft",
        json={"chat_id": chat_id, "draft_id": draft_id,
              "text": texto[:LIMITE_DE_BORRADOR]})
    codigo = getattr(r, "status_code", 200)
    if codigo == 429:
        try:
            espera = float(((r.json() or {}).get("parameters") or {}).get(
                "retry_after", 1))
        except Exception:  # noqa: BLE001 - sin cuerpo legible, un segundo
            espera = 1.0
        raise _RitmoTelegram(espera)
    if codigo >= 400:
        raise ErrorTelegram(f"HTTP {codigo}: {_descripcion_telegram(r) or ''}".strip())


# Un mensaje de Telegram admite hasta 4096 caracteres; el borrador, también.
LIMITE_DE_BORRADOR = 4096
# Cada cuánto se actualiza el borrador con el texto que llega (respuesta en stream).
# El primero sale enseguida; después, a lo sumo cada 0,15 s (pedido del usuario,
# 2026-10-01: "que apenas tenga algo para mostrar lo muestre", y más seguido para
# ver cómo escribe). Si Telegram pide ir más despacio (429) se espera lo que pide,
# acotado, y se sigue con lo último; otro error corta el stream del turno y se
# reporta. El mensaje final sale igual. Valor a configurar desde la plataforma.
INTERVALO_DE_BORRADOR = 0.15


class IndicadorDeActividad:
    """Lo que `mantener_chat_activo` le da a quien atiende el turno: el borrador
    nativo que abrió el indicador, para escribirle el texto que el modelo va
    redactando (respuesta en stream, ADR 0011, experimento del 2026-10-01).

    Efímero: es el borrador, nunca un mensaje; no pasa por la cola ni lleva
    botones. El mensaje real sale por la cola cuando está verificado y el
    indicador retira el borrador igual que siempre. Seguro entre hilos: lo llama
    el hilo del turno (o el del cliente del modelo) mientras el hilo del indicador
    manda la semilla y el typing; el `candado` los ordena."""

    def __init__(self, http, token: str, chat_id: int, draft_id: int,
                 admite_borrador: bool, impresos: set[str], reloj=time.monotonic,
                 intervalo: float = INTERVALO_DE_BORRADOR) -> None:
        self._http, self._token, self._chat_id = http, token, chat_id
        self.draft_id = draft_id
        self.admite_borrador = admite_borrador
        self._impresos, self._reloj, self._intervalo = impresos, reloj, intervalo
        self.candado = threading.Lock()
        self.cerrado = threading.Event()
        # Con texto en el borrador, la semilla ya no se manda: lo taparia.
        self.con_texto = threading.Event()
        self.intentado = threading.Event()
        self.activado = threading.Event()
        self._ultimo_texto: str | None = None
        self._ultimo_envio: float | None = None
        self._fallo = False
        # El último texto que tiene que mostrar el borrador y si hay un trabajador
        # mandándolo (`_trabajar`): uno solo por indicador.
        self._estado = threading.Lock()
        self._pendiente: str | None = None
        self._trabajando = False

    def actualizar_borrador(self, texto: str) -> None:
        """Deja `texto` como lo último que tiene que mostrar el borrador. Nunca espera
        a Telegram (lo llama el hilo que lee lo que escribe el modelo) y nunca lanza:
        un solo trabajador en segundo plano manda siempre el texto MÁS RECIENTE, a lo
        sumo una vez cada `INTERVALO_DE_BORRADOR`; lo que llega mientras hay un envío
        en vuelo o antes del intervalo queda pendiente y sale apenas se puede (prueba
        real del 2026-10-01: descartarlo dejaba ver sólo las primeras letras). Una
        falla se reporta una vez por turno y no se insiste en el resto de ese turno."""
        if (not self.admite_borrador or not texto or self._fallo
                or self.cerrado.is_set()):
            return
        with self._estado:
            self._pendiente = texto
            if self._trabajando:
                return
            self._trabajando = True
        self.con_texto.set()
        self.activado.set()
        try:
            threading.Thread(target=self._trabajar, name="leda-stream",
                             daemon=True).start()
        except Exception:  # noqa: BLE001 - cosmético: sin hilo no hay stream
            with self._estado:
                self._trabajando = False

    def _trabajar(self) -> None:
        while True:
            with self._estado:
                texto = self._pendiente
                if (texto is None or texto == self._ultimo_texto or self._fallo
                        or self.cerrado.is_set()):
                    self._trabajando = False
                    return
            if self._ultimo_envio is not None:
                espera = self._intervalo - (self._reloj() - self._ultimo_envio)
                if espera > 0 and self.cerrado.wait(espera):
                    with self._estado:
                        self._trabajando = False
                    return
                with self._estado:
                    texto = self._pendiente      # lo más nuevo después de esperar
            # El candado ordena el envío con la semilla y con el cierre: el cierre
            # lo toma antes de retirar, así nunca se cruzan.
            with self.candado:
                if self.cerrado.is_set() or self._fallo:
                    with self._estado:
                        self._trabajando = False
                    return
                self._ultimo_envio = self._reloj()
                ritmo = None
                try:
                    _enviar_borrador_texto(self._http, self._token, self._chat_id,
                                           self.draft_id, texto)
                    self._ultimo_texto = texto
                except _RitmoTelegram as e:
                    ritmo = e.espera
                except Exception as e:  # noqa: BLE001 - no fatal, se reporta
                    self._fallo = True
                    _reportar_falla_indicador(self._impresos, "stream", e)
                finally:
                    self.intentado.set()
            if ritmo is not None and self.cerrado.wait(
                    min(max(ritmo, 0.0), ESPERA_MAXIMA_RITMO)):
                with self._estado:
                    self._trabajando = False
                return


# El indicador del turno en curso: `mantener_chat_activo` lo deja aca mientras dura
# el bloque, asi quien conduce el turno lo encuentra sin que cada capa intermedia
# lo pase (el turno corre en el mismo hilo que abrio el bloque).
_INDICADOR_ACTUAL: contextvars.ContextVar[IndicadorDeActividad | None] = (
    contextvars.ContextVar("indicador_de_actividad", default=None))


def indicador_actual() -> IndicadorDeActividad | None:
    """El indicador del turno en curso, o `None` fuera de `mantener_chat_activo`."""
    return _INDICADOR_ACTUAL.get()


def _retirar_borrador(http, token: str, chat_id: int) -> None:
    """Retira el borrador nativo materializando la semilla como mensaje
    normal -- silencioso, para no sonar ni vibrar por un mensaje que se
    borra al instante -- y borrándolo enseguida por su `message_id` real:
    `sendMessageDraft` no tiene uno propio (mecanismo recuperado del pack
    05, sección 5)."""
    r = pedido_telegram(
        http.post, f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": SEMILLA_INDICADOR,
              "disable_notification": True})
    cuerpo = r.json()
    message_id = (cuerpo.get("result") or {}).get("message_id")
    if message_id is not None:
        pedido_telegram(
            http.post, f"https://api.telegram.org/bot{token}/deleteMessage",
            json={"chat_id": chat_id, "message_id": message_id})


def _reportar_falla_indicador(impresos: set[str], kind: str, error: Exception) -> None:
    """Imprime a lo sumo una vez por `kind` (`typing`/`borrador`/`retiro`) y
    por invocación de `mantener_chat_activo` -- `impresos` es local a cada
    invocación, así que el refresco de typing cada `intervalo` nunca
    imprime más de una vez por turno, aunque seguido falle (regla del
    proyecto: nunca en silencio, pero tampoco en aluvión). Nunca texto
    crudo, URL ni token: sólo lo que ya deja `texto_error_seguro`."""
    if kind in impresos:
        return
    impresos.add(kind)
    print(f"  ! indicador de actividad ({kind}): {texto_error_seguro(error)}")


# Un borrador que no se pudo retirar puede quedar visible para la persona --
# pesa más que un typing o un borrador que no salió, así que además del
# print de arriba, se registra un incidente. Deduplicado por `(workspace_id,
# 'retiro_borrador')` mientras el proceso siga vivo -- mismo patrón que
# `saludo._FALLAS_SALUDO_REPORTADAS`/`saludo.reportar_falla`: un incidente
# por falla persistente, no uno por turno.
_FALLAS_RETIRO_REPORTADAS: set[tuple[str | None, str]] = set()


def _reportar_falla_retiro(cur, workspace_id: str | None, error: Exception) -> None:
    """Registra el incidente de una falla al retirar el borrador, si hay
    cursor -- `cur` es opcional porque no toda invocación de
    `mantener_chat_activo` tiene una transacción a mano (pruebas, u otro
    llamador futuro sin base). Nunca texto crudo de la excepción en el
    resumen (Constitución §10); `referencia_cruda` lleva lo mismo que ya
    imprime `_reportar_falla_indicador`, seguro de guardar.

    El `insert` corre en su propio SAVEPOINT (`cur.connection.transaction()`)
    -- mismo patrón que `_reportar_falla_saludo_aislada` (R3-002, revisión
    2026-09-28): `cur` es la MISMA transacción que ya procesa el turno
    (`gateway.procesar_update` le pasa su propio cursor), así que si el
    `insert` fallara sin este aislamiento, PostgreSQL deja la transacción
    entera abortada -- la respuesta que el turno ya encoló se perdería al
    llegar al `commit`, por un incidente que ni siquiera es sobre ella."""
    if cur is None:
        return
    clave = (workspace_id, "retiro_borrador")
    if clave in _FALLAS_RETIRO_REPORTADAS:
        return
    try:
        with cur.connection.transaction():
            registrar_incidente(
                cur, workspace_id,
                "El borrador nativo del indicador de actividad no se pudo "
                "retirar; puede haber quedado visible para la persona.",
                referencia_cruda=texto_error_seguro(error),
                etapa="indicador_actividad", severidad="media")
    except Exception as exc:  # noqa: BLE001 -- ni esto puede tirar el turno
        print(f"  ! no se pudo registrar el incidente del indicador de "
             f"actividad ({type(exc).__name__}).")
        return
    _FALLAS_RETIRO_REPORTADAS.add(clave)


# Timeout del cliente HTTP propio de `mantener_chat_activo` (typing, borrador
# y el cliente dedicado del retiro) -- una sola constante para que las tres
# llamadas nunca queden desincronizadas entre sí, y para que
# `timeout_borrador` (más abajo) tenga el mismo valor por defecto que el
# cliente al que le pone cota: nunca tiene sentido esperar más de lo que esa
# llamada puede tardar en resolverse sola.
_TIMEOUT_CLIENTE_INDICADOR = 5.0


@contextmanager
def mantener_chat_activo(token: str, chat_id: int, *, cliente=None,
                         chat_type: str | None = None,
                         umbral: float = 1.5, intervalo: float = 3.0,
                         nombre_hilo: str = "leda-typing",
                         espera_cierre: float = 0.25,
                         timeout_borrador: float = _TIMEOUT_CLIENTE_INDICADOR,
                         cur=None, workspace_id: str | None = None,
                         intervalo_borrador: float = INTERVALO_DE_BORRADOR,
                         reloj=time.monotonic):
    """Indicador de actividad mientras se procesa un turno: "escribiendo…"
    y, en chat privado, un borrador nativo -- ninguno de los dos aparece si
    la respuesta está lista antes de `umbral` segundos (decisión del
    usuario, 2026-09-27: nunca un destello en una respuesta rápida; ADR
    0011, decisión 2).

    El borrador sólo se intenta si `chat_type` es `"private"` -- Bot API
    9.5 sólo lo abrió ahí; en grupo o canal degrada en silencio a sólo
    typing. Al salir del bloque -- éxito, excepción o sin ninguna respuesta
    nueva --, si el borrador se llegó a mostrar, se retira (ADR 0011,
    decisión 3): queda indistinguible de una respuesta sin botones, y es
    estrictamente más seguro que un borrador visible justo antes de
    botones, el caso difícil del pack recuperado.

    El `draft_id` es aleatorio por invocación -- nunca un contador de
    proceso (el código recuperado lo marcaba como pendiente: un contador no
    garantiza unicidad entre varios workers).

    Toda falla de red acá es no fatal (Constitución §10): nunca bloquea ni
    duplica la respuesta real. Pero "no fatal" no es "en silencio" (regla
    del proyecto): cada una se imprime, a lo sumo una vez por tipo
    (`typing`/`borrador`/`retiro`) y por invocación -- el refresco de
    typing cada `intervalo` nunca inunda la consola --, y nunca con texto
    crudo, URL ni token (`texto_error_seguro`). Una falla al RETIRAR pesa
    más -- el borrador puede quedar visible para la persona --, así que
    además se registra un incidente si hay `cur` (mismo cursor/transacción
    que ya procesa el turno), deduplicado por proceso
    (`_reportar_falla_retiro`).

    El retiro nunca puede llegar antes que el propio borrador (R3-001,
    revisión 2026-09-28 sobre el commit e2a094e): el hilo marca `activado`
    ANTES de llamar a `sendMessageDraft`, así que un `hilo.join` que agotó
    `espera_cierre` no prueba que esa llamada ya volvió -- si el turno
    termina justo cuando recién empezaba, y la llamada es lenta, retirar de
    inmediato podía llegar a Telegram primero y dejar el borrador visible.
    Antes de intentar retirar, se espera (acotado a `timeout_borrador`, el
    mismo timeout que ya tiene el cliente HTTP: nunca más de lo que esa
    llamada puede tardar en resolverse sola) a que el intento de mandar el
    borrador -- éxito o falla -- termine de verdad. Si ni con ese margen
    resolvió, se abandona el retiro en vez de arriesgar el orden."""
    import httpx

    try:
        http = cliente or httpx.Client(timeout=_TIMEOUT_CLIENTE_INDICADOR)
    except Exception:  # noqa: BLE001 - cosmetic
        yield None
        return
    owned_client = cliente is None
    detener = threading.Event()
    intenta_borrador = (chat_type or "").lower() == "private"
    draft_id = random.randint(1, 2**31 - 1)
    impresos: set[str] = set()
    indicador = IndicadorDeActividad(http, token, chat_id, draft_id,
                                     intenta_borrador, impresos, reloj,
                                     intervalo_borrador)
    # Son los mismos eventos de siempre, ahora compartidos con el indicador: el
    # texto en stream tambien "activa" el borrador y resuelve su intento.
    activado = indicador.activado
    borrador_intentado = indicador.intentado

    def ciclo() -> None:
        try:
            if detener.wait(umbral):
                return  # ya terminó antes del umbral: nunca se muestra nada
            activado.set()
            if intenta_borrador:
                try:
                    with indicador.candado:
                        # Con el texto de la respuesta ya en el borrador, la
                        # semilla lo taparia: no se manda.
                        if not indicador.con_texto.is_set():
                            _enviar_borrador_semilla(http, token, chat_id,
                                                     draft_id)
                except Exception as e:  # noqa: BLE001 - no fatal, se reporta
                    _reportar_falla_indicador(impresos, "borrador", e)
                finally:
                    # Se marca pase lo que pase (éxito o falla): es lo que
                    # el retiro espera para saber que ya no está en vuelo
                    # (R3-001, ver docstring).
                    borrador_intentado.set()
            while not detener.is_set():
                try:
                    _enviar_chat_action(http, token, chat_id)
                except Exception as e:  # noqa: BLE001 - no fatal, se reporta
                    _reportar_falla_indicador(impresos, "typing", e)
                detener.wait(intervalo)
        finally:
            if owned_client:
                try:
                    indicador.cerrado.set()
                    with indicador.candado:     # espera un texto en vuelo
                        http.close()
                except Exception:  # noqa: BLE001 - cosmetic cleanup is isolated
                    pass

    try:
        hilo = threading.Thread(target=ciclo, name=nombre_hilo, daemon=True)
        hilo.start()
    except Exception:  # noqa: BLE001 - cosmetic
        if owned_client:
            _close_client_bounded(http, espera_cierre)
        yield None
        return
    marca = _INDICADOR_ACTUAL.set(indicador)
    try:
        yield indicador
    finally:
        _INDICADOR_ACTUAL.reset(marca)
        # Ningun texto mas: el mensaje real ya esta (o no va a estar) y el retiro
        # no puede cruzarse con una actualizacion del borrador.
        indicador.cerrado.set()
        if indicador.candado.acquire(timeout=timeout_borrador):
            indicador.candado.release()
        detener.set()
        try:
            hilo.join(timeout=espera_cierre)
        except Exception:  # noqa: BLE001 - cosmetic
            pass
        # El cliente que refresca typing se cierra adentro del propio hilo
        # (si es propio, arriba de `ciclo`, sin cambios respecto de antes) --
        # el retiro del borrador usa un cliente PROPIO y de corta vida
        # cuando el llamador no inyectó uno, así que nunca compite por el
        # mismo cliente que el hilo de typing todavía puede estar cerrando.
        if activado.is_set() and intenta_borrador:
            if not borrador_intentado.wait(timeout_borrador):
                # Ni con ese margen se resolvió (cliente colgado más allá
                # de su propio timeout) -- abandonar el retiro en vez de
                # arriesgar que llegue antes que un borrador que todavía no
                # se sabe si se mandó (R3-001).
                falla = TimeoutError(
                    "el borrador no terminó de intentarse a tiempo para retirarlo")
                _reportar_falla_indicador(impresos, "retiro", falla)
                _reportar_falla_retiro(cur, workspace_id, falla)
            else:
                try:
                    if owned_client:
                        with httpx.Client(timeout=_TIMEOUT_CLIENTE_INDICADOR) as http_retiro:
                            _retirar_borrador(http_retiro, token, chat_id)
                            _escribiendo_tras_el_retiro(http_retiro, token, chat_id,
                                                        impresos)
                    else:
                        _retirar_borrador(http, token, chat_id)
                        _escribiendo_tras_el_retiro(http, token, chat_id, impresos)
                except Exception as e:  # noqa: BLE001 - no fatal, pero pesa más
                    _reportar_falla_indicador(impresos, "retiro", e)
                    _reportar_falla_retiro(cur, workspace_id, e)


def _escribiendo_tras_el_retiro(http, token: str, chat_id: int,
                               impresos: set[str]) -> None:
    """El retiro manda (y borra) un mensaje, y cualquier mensaje del bot apaga el
    "escribiendo…" en Telegram; la respuesta real sale después (guardar,
    controlar, despachar), y ese hueco se veía como "aparece y se va antes de la
    respuesta" (prueba real del 2026-10-01). Un typing más lo cubre hasta que la
    respuesta llega y lo reemplaza. Falla como cualquier typing: no fatal, se
    reporta."""
    try:
        _enviar_chat_action(http, token, chat_id)
    except Exception as e:  # noqa: BLE001 - no fatal, se reporta
        _reportar_falla_indicador(impresos, "typing", e)


def acusar_toque(token: str, callback_id: str, cliente=None) -> None:
    """Le avisa a Telegram que el toque de un botón llegó.

    **Es la única llamada a Telegram que no pasa por la cola, y tiene que
    seguir siéndolo.**

    La regla del proyecto es que Leda escribe en `message_outbox` y un
    worker entrega. Eso da reintentos, auditoría e idempotencia, y vale para
    todo lo que Leda le dice a una persona.

    Esto no es eso. Es un acuse del protocolo, entre máquinas: no aparece en
    el chat, nadie lo lee, y Telegram lo exige en un par de segundos o le deja
    el reloj girando a quien apretó. La cola corre cada treinta: por ahí no
    llega a tiempo.

    Lo que la limita, y lo que hay que sostener si mañana aparece otro caso
    parecido:

      - no lleva contenido: sólo dice "llegó";
      - no cambia nada en la base;
      - si falla, no se pierde trabajo — quien llama la ignora.

    Todo lo que la persona sí tiene que leer sigue saliendo por la cola.
    """
    import httpx

    cliente = cliente or httpx.Client(timeout=5)
    pedido_telegram(
        cliente.post, f"https://api.telegram.org/bot{token}/answerCallbackQuery",
        json={"callback_query_id": callback_id})


MAX_INTENTOS = 5

# Backoff entre reintentos de un aviso admin -- hallazgo de la revisión
# review-1b0a5a47 (2026-09-28): sin esto, un intento fallido queda con `estado='listo'` y
# `programado_para` sin mover, así que el listener (corre cada unos
# segundos) lo reintenta de inmediato y agota MAX_INTENTOS en un par de
# minutos frente a un blip de Telegram, en vez de dejar pasar el blip.
# Geométrico simple (1, 2, 4, 8 minutos) para los intentos 1 a 4 -- el
# intento 5 ya cae en `fallido`, así que no hace falta un quinto valor.
BACKOFF_MINUTOS_AVISO_ADMIN = (1, 2, 4, 8)


def _proximo_intento_admin(intentos: int, ahora: datetime) -> datetime:
    """`intentos` ya incluye el que acaba de fallar (1-indexado)."""
    indice = min(intentos, len(BACKOFF_MINUTOS_AVISO_ADMIN)) - 1
    return ahora + timedelta(minutes=BACKOFF_MINUTOS_AVISO_ADMIN[indice])


def _botones(cur, m) -> list[Boton]:
    """Las opciones de la acción pendiente que el mensaje está preguntando.

    Se leen al despachar, no al encolar: entre que Leda pregunta y el
    mensaje sale puede pasar tiempo, y lo que vale es lo vigente al entregar.
    """
    if m.get("bloque_copiable"):
        # El mensaje que muestra lo que la persona había escrito (T9-R1c-3): el
        # botón de copiar sólo si entra en el límite de Telegram; el bloque sale
        # igual, marcado en el texto.
        if cabe_en_boton_de_copiar(m["bloque_copiable"]):
            return [Boton(ETIQUETA_COPIAR, "", m["bloque_copiable"])]
        return []
    if m.get("intake_choice_set_id"):
        from .ingreso_tareas import callback_data

        cur.execute(
            """select etiqueta, token from task_intake_choice
                where choice_set_id = %s and activa order by orden""",
            (m["intake_choice_set_id"],),
        )
        return [Boton(row["etiqueta"], callback_data(row["token"]))
                for row in cur.fetchall()]
    if not m["pending_action_id"]:
        return []

    from .pendientes import callback_data, opciones

    return [Boton(o.etiqueta, callback_data(o))
            for o in opciones(cur, m["pending_action_id"])]


def _preview_vigente(cur, m, ahora: datetime) -> bool:
    """Si la vista previa que lleva `m` sigue siendo la vigente al `ahora` de la
    pasada: el mismo reloj que decide el vencimiento del mensaje y lo que se
    retendría (`_SE_RETENDRIA`)."""
    if not m["pending_action_id"]:
        return True
    cur.execute(
        """select p.estado, p.draft_id, p.membership_id, p.herramienta,
                  p.vence_en > %s as no_vencida,
                  d.responsable_membership_id
             from pending_action p
             left join task_draft d on d.id = p.draft_id
            where p.id = %s
            for update of p""",
        (ahora, m["pending_action_id"]))
    accion = cur.fetchone()
    if not accion or accion["draft_id"] is None:
        return True
    from .pendientes import HERRAMIENTA_REVISION_BORRADOR

    if accion["herramienta"] == HERRAMIENTA_REVISION_BORRADOR:
        # El resumen de quien pidió el borrador (T9-R1c-4) es suyo aunque no sea
        # quien aprueba: sigue vigente mientras espera, sin vencer, y su dueño
        # esté activo.
        cur.execute("select activo from membership where id = %s for share",
                    (accion["membership_id"],))
        dueno = cur.fetchone()
        vigente = (accion["estado"] == "esperando" and accion["no_vencida"]
                   and bool(dueno and dueno["activo"]))
        if not vigente:
            cur.execute(
                """update pending_action set estado = 'vencida'
                    where id = %s and estado = 'esperando'""",
                (m["pending_action_id"],))
            cur.execute(
                "update message_outbox set estado = 'descartado' where id = %s",
                (m["id"],))
        return vigente
    cur.execute(
        """select destinatario.activo as destinatario_activo,
                  responsable.aprobador_membership_id as aprobador_actual
             from membership destinatario, membership responsable
            where destinatario.id = %s and responsable.id = %s
            for share of destinatario, responsable""",
        (accion["membership_id"], accion["responsable_membership_id"]))
    autoridad = cur.fetchone()
    if not autoridad:
        autoridad = {"destinatario_activo": False, "aprobador_actual": None}
    accion.update(autoridad)
    if accion["aprobador_actual"] is None:
        cur.execute(
            """select raiz.id
                 from membership raiz join rol r on r.id = raiz.rol_id
                where raiz.workspace_id = %s and raiz.activo
                  and r.autoridad_final
                for share of raiz""", (m["workspace_id"],))
        raiz = cur.fetchone()
        accion["aprobador_actual"] = raiz["id"] if raiz else None
    vigente = (
        accion["estado"] == "esperando"
        and accion["no_vencida"]
        and accion["destinatario_activo"]
        and accion["membership_id"] == accion["aprobador_actual"]
    )
    if vigente:
        return True
    cur.execute(
        """update pending_action set estado = 'vencida'
            where id = %s and estado = 'esperando'""",
        (m["pending_action_id"],))
    cur.execute("update message_outbox set estado = 'descartado' where id = %s",
                (m["id"],))
    return False


def _tope_diario(cur, workspace_id: str) -> int | None:
    cur.execute(
        "select valor from workspace_setting "
        "where workspace_id = %s and clave = 'limites_de_contacto'",
        (workspace_id,))
    fila = cur.fetchone()
    if not fila:
        return None
    valor = fila["valor"]
    if isinstance(valor, str):
        valor = json.loads(valor)
    return valor.get("max_mensajes_automaticos_por_persona_por_dia")


VENTANA_DE_ACTIVIDAD = timedelta(minutes=30)
"""Cuánto cuenta como "activa en la rama" una persona que escribió o tocó algo en
ese chat (T9-R1d-2b, ADR 0013 regla 1, "Precisión (2026-09-29, decisión del
usuario)"): lo que Leda inicia se retiene sólo mientras haya pasado menos que
esto desde su última actividad. Una rama abandonada no retiene nada, ni un aviso
urgente: sale en el momento y la rama sigue abierta para cuando vuelva."""


def _activa_en_el_chat(cur, workspace_id: str, app_user_id: str, chat_id: int,
                       ahora: datetime) -> bool:
    """Si la persona escribió o tocó algo en ese chat dentro de
    `VENTANA_DE_ACTIVIDAD`. La actividad es lo que ya guarda `inbound_message`:
    su mensaje (`gateway.procesar_update`) o su toque (`gateway._registrar_toque`,
    una fila sin texto)."""
    cur.execute(
        """select 1 from inbound_message
            where workspace_id = %s and chat_id = %s and app_user_id = %s
              and at >= %s
            limit 1""",
        (workspace_id, chat_id, app_user_id, ahora - VENTANA_DE_ACTIVIDAD))
    return cur.fetchone() is not None


def _rama_activa_de(cur, m, ahora: datetime):
    """La rama abierta del destinatario de `m` en el chat de `m`
    (`pendientes.ver_rama_abierta`, la misma definición que usa la conversación,
    con las preguntas del alta), pero sólo si él está activo en ese chat
    (`VENTANA_DE_ACTIVIDAD`); si no, `None`.

    Sin la fila de su membresía (no visible en el espacio o ya no existe) no hay a
    quién atribuirle una rama: se decide `None`, es decir, no se retiene. Retener
    a nombre de un `Solicitante` vacío dejaría un mensaje esperando por una rama
    que nadie puede cerrar; sale, como antes de que existiera la retención."""
    from . import herramientas as H
    from .autoridad import Canal, Solicitante
    from .pendientes import ver_rama_abierta

    cur.execute("select app_user_id from membership where id = %s",
                (m["destinatario_membership_id"],))
    persona = cur.fetchone()
    if persona is None:
        return None
    workspace_id = str(m["workspace_id"])
    app_user_id = str(persona["app_user_id"])
    if not _activa_en_el_chat(cur, workspace_id, app_user_id, m["chat_id"], ahora):
        return None
    quien = Solicitante(
        app_user_id=app_user_id, canal=Canal.ESPACIO, workspace_id=workspace_id,
        membership_id=str(m["destinatario_membership_id"]))
    return ver_rama_abierta(cur, quien, m["chat_id"], ahora, H.REGISTRO,
                            alta=True)


def _rama_que_retiene(cur, m, ahora: datetime, cache: dict):
    """La rama abierta que retiene a `m`, o `None` si `m` sale (T9-R1d-2 y
    T9-R1d-2b, ADR 0013 regla 1, enmienda "una sola rama abierta"). Sólo un
    mensaje que inicia Leda a una persona se retiene, y mientras ella esté
    activa en la rama (`VENTANA_DE_ACTIVIDAD`): una respuesta nunca. El mensaje
    que muestra la propia rama (`pending_action_id` o `intake_choice_set_id` igual
    al de la pregunta abierta) no espera a su propio cierre. Se consulta una vez
    por persona y chat en cada pasada (`cache`)."""
    if m["es_respuesta"]:
        return None
    membership_id = m["destinatario_membership_id"]
    if not membership_id:
        return None
    clave = (str(membership_id), m["chat_id"])
    if clave not in cache:
        cache[clave] = _rama_activa_de(cur, m, ahora)
    rama = cache[clave]
    if rama is None:
        return None
    propia = rama.id in (str(m["pending_action_id"] or ""),
                         str(m["intake_choice_set_id"] or ""))
    return None if propia else rama


@dataclass
class _Pasada:
    """Lo que una pasada de `despachar` va aprendiendo: las filas ya examinadas,
    la rama de cada persona y chat, y a quién dejó de pedirle filas porque lo que
    Leda le inicia se retiene. `chats_en_falla` son los chats donde un envío
    falló en esta pasada: no se les envía nada más hasta la próxima, para que lo
    que falló salga primero (F-A1)."""
    vistos: list[str] = field(default_factory=list)
    ramas: dict = field(default_factory=dict)
    retenidos: list[dict] = field(default_factory=list)
    chats_en_falla: list[int] = field(default_factory=list)


# Lo que, al examinarlo, se retendría en vez de descartarse: no vencido (la regla de
# `_despachar_fila`: `vence_en < ahora` se descarta) y, si es la vista previa de un
# borrador, todavía la vigente (`_preview_vigente`: esperando y sin vencer; el cambio
# de aprobador sólo lo ve el examen). Ambos con el `ahora` de la pasada: un solo reloj
# para la cuenta, la exclusión y el examen. Lo vencido de alguien retenido no espera a que
# se libere: se examina y se descarta como siempre, y no se cuenta como retenido
# (T9-R1c-3, seguimiento de `review-3ebe127d376a4d18`).
_SE_RETENDRIA = """
                and (message_outbox.vence_en is null
                     or message_outbox.vence_en >= %(ahora)s)
                and not exists (
                      select 1 from pending_action p
                       where p.id = message_outbox.pending_action_id
                         and p.draft_id is not null
                         and not (p.estado = 'esperando'
                                  and p.vence_en > %(ahora)s))"""

# Lo retenido sigue `listo` y encabezaría la cola de siempre. Para que no deje sin
# servicio a lo que viene detrás sin agrandar la pasada, la primera fila que se
# retiene de una persona en un chat la excluye del resto de la pasada (salvo sus
# respuestas, la pregunta de la propia rama y lo que se descartaría al examinarlo,
# que nunca se retienen): esa fila cuesta una del lote y lo demás suyo ya no se pide.
_SIN_LO_RETENIDO = f"""
       and not exists (
             select 1 from jsonb_to_recordset(%(retenidos)s::jsonb)
                      as x(m uuid, c bigint, rama text)
              where not message_outbox.es_respuesta
                and x.m = message_outbox.destinatario_membership_id
                and x.c = message_outbox.chat_id
                and message_outbox.pending_action_id::text is distinct from x.rama
                and message_outbox.intake_choice_set_id::text is distinct from x.rama
                {_SE_RETENDRIA})
"""


def despachar(cur: psycopg.Cursor, workspace_id: str, transporte: Transporte,
              cal: Calendario, ahora: datetime | None = None,
              lote: int = 50) -> dict[str, int]:
    """Una pasada del despachador: examina a lo sumo `lote` filas, de a una,
    retenidas o no. Lo que queda por despachar sale en la pasada siguiente."""
    ahora = ahora or datetime.now(timezone.utc)
    # Una pasada por espacio a la vez (F-A1). El orden por `programado_para` sólo
    # vale dentro de una pasada: con dos a la vez (el despacho inmediato de
    # después del webhook y el tick de fondo), mientras una envía la primera fila
    # con su lock la otra la saltea (`skip locked`) y envía la segunda, y las
    # partes de una misma respuesta salen invertidas. La que llega espera a que la
    # otra termine y retoma desde el orden de la cola. El lock se suelta con la
    # transacción de quien llama.
    cur.execute("select pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (f"despachar:{workspace_id}",))
    tope = _tope_diario(cur, workspace_id)
    resumen = {"enviados": 0, "pospuestos": 0, "fallidos": 0, "descartados": 0,
               "retenidos": 0}
    pasada = _Pasada()
    while len(pasada.vistos) < lote:
        cur.execute(
            f"""
             select id, workspace_id, chat_id, cuerpo, tipo,
                    destinatario_membership_id, intentos,
                    vence_en, es_respuesta, pending_action_id, intake_choice_set_id,
                    es_bienvenida, bloque_copiable, es_coordinacion
              from message_outbox
             where workspace_id = %(ws)s
               and estado = 'listo'
               and programado_para <= %(ahora)s
               and id <> all(%(vistos)s::uuid[])
               and chat_id <> all(%(chats_en_falla)s::bigint[])
               {_SIN_LO_RETENIDO}
             order by programado_para
             limit 1
             for update skip locked
            """,
            {"ws": workspace_id, "ahora": ahora, "vistos": pasada.vistos,
             "retenidos": Jsonb(pasada.retenidos),
             "chats_en_falla": pasada.chats_en_falla})
        m = cur.fetchone()
        if m is None:
            break
        pasada.vistos.append(str(m["id"]))
        fallidos = resumen["fallidos"]
        _despachar_fila(cur, workspace_id, transporte, cal, ahora, tope, m,
                        resumen, pasada)
        if resumen["fallidos"] > fallidos:
            # Un envío que falla se reintenta en la próxima pasada: seguir con lo que
            # viene detrás en el mismo chat lo dejaría salir primero (el aviso de una
            # respuesta detrás de su pregunta, F-A1).
            pasada.chats_en_falla.append(m["chat_id"])
    _quitar_botones_resueltos(cur, workspace_id, transporte, ahora, lote)
    return resumen


# C0-6: lo que Telegram contesta cuando ya no hay botones que quitar (alguien ya
# los quitó, o el mensaje se borró). Es el mismo resultado que haberlos quitado.
_YA_SIN_BOTONES = ("message is not modified", "message to edit not found")
ETAPA_QUITAR_BOTONES = "quitar_botones"
REFERENCIA_MESSAGE_OUTBOX = "message_outbox"


def _quitar_botones_resueltos(cur, workspace_id: str, transporte: Transporte,
                              ahora: datetime, lote: int) -> int:
    """Le saca los botones a los mensajes ya entregados de este espacio cuya acción
    pendiente o elección del alta ya no vale: resuelta, cancelada, enviada,
    rechazada o vencida (C0-6, ADR 0013 regla 3: Leda no ofrece lo que ya no se
    puede hacer). Corre en la pasada del despachador, bajo su mismo espacio y su
    mismo candado. `botones_quitados_en` lo hace una sola vez por mensaje: queda
    puesta si se quitaron, si Telegram dice que ya no había nada que quitar y
    también si falló de otra manera, porque entonces queda un incidente (nunca un
    silencio) y reintentar sin fin sólo repetiría el incidente. Un toque que
    llegue antes o a pesar de esto lo contesta el gateway con el estado real
    (C0-5). Devuelve cuántos mensajes resolvió."""
    cur.execute(
        """select m.id, m.chat_id, m.telegram_message_id
             from message_outbox m
             left join pending_action p on p.id = m.pending_action_id
             left join task_intake_choice_set s on s.id = m.intake_choice_set_id
            where m.workspace_id = %(ws)s and m.estado = 'enviado'
              and m.botones_quitados_en is null
              and m.telegram_message_id is not null
              and (m.pending_action_id is not null
                   or m.intake_choice_set_id is not null)
              and ((p.id is not null
                    and (p.estado <> 'esperando' or p.vence_en <= %(ahora)s))
                   or (s.id is not null and s.estado <> 'active'))
            order by m.enviado_en
            limit %(lote)s
            for update of m skip locked""",
        {"ws": workspace_id, "ahora": ahora, "lote": lote})
    filas = cur.fetchall()
    for m in filas:
        try:
            transporte.quitar_botones(m["chat_id"], m["telegram_message_id"])
        except Exception as e:  # noqa: BLE001 -- se registra, no se propaga
            detalle = texto_error_seguro(e)
            if not any(s in detalle.lower() for s in _YA_SIN_BOTONES):
                registrar_incidente(
                    cur, workspace_id,
                    "No se pudieron quitar los botones de un mensaje que ya no "
                    "vale: siguen visibles en Telegram.",
                    severidad="baja", etapa=ETAPA_QUITAR_BOTONES,
                    referencia_cruda=redactar_secreto_telegram(detalle)[:500],
                    referencia_tipo=REFERENCIA_MESSAGE_OUTBOX,
                    referencia_id=str(m["id"]), chat_id=m["chat_id"])
        cur.execute(
            "update message_outbox set botones_quitados_en = %s where id = %s",
            (ahora, m["id"]))
    return len(filas)


def _retener(cur, workspace_id: str, ahora: datetime, m, rama, resumen: dict,
             pasada: _Pasada) -> None:
    """`m` no se envía ni se descarta: sigue `listo` en su lugar de la cola y se
    cuenta en `retenidos`. La primera vez que se retiene a una persona en un chat
    se cuenta también lo suyo que la consulta ya no va a pedir, y sólo lo que de
    verdad se retendría (`_SE_RETENDRIA`) y no está bloqueado por otro despachador:
    con `skip locked` la cuenta no incluye lo que esa otra pasada tiene en sus manos
    (y lo que cuenta queda bloqueado hasta cerrar esta pasada, como lo examinado)."""
    resumen["retenidos"] += 1
    clave = {"m": str(m["destinatario_membership_id"]), "c": m["chat_id"],
             "rama": rama.id}
    if clave in pasada.retenidos:
        return
    pasada.retenidos.append(clave)
    cur.execute(
        f"""select count(*) n from (
              select 1 from message_outbox
               where workspace_id = %(ws)s and estado = 'listo'
                 and programado_para <= %(ahora)s
                 and id <> all(%(vistos)s::uuid[])
                 and destinatario_membership_id = %(m)s and chat_id = %(c)s
                 and not es_respuesta
                 and pending_action_id::text is distinct from %(rama)s
                 and intake_choice_set_id::text is distinct from %(rama)s
                 {_SE_RETENDRIA}
                 for update skip locked) retenidas""",
        {"ws": workspace_id, "ahora": ahora, "vistos": pasada.vistos, **clave})
    resumen["retenidos"] += cur.fetchone()["n"]


def _despachar_fila(cur, workspace_id: str, transporte: Transporte,
                    cal: Calendario, ahora: datetime, tope, m, resumen: dict,
                    pasada: _Pasada) -> None:
    if not _preview_vigente(cur, m, ahora):
        resumen["descartados"] += 1
        return
    # Contestarle a quien escribió no es "escribir fuera de horario", ni
    # cuenta contra el tope de mensajes automáticos: no es automático.
    if m["es_respuesta"]:
        if _intentar_envio(cur, workspace_id, transporte, cal, ahora, m):
            resumen["enviados"] += 1
        else:
            resumen["fallidos"] += 1
        return

    # Un mensaje de cadencia cuya ventana ya pasó no se manda tarde.
    if m["vence_en"] and m["vence_en"] < ahora:
        cur.execute(
            "update message_outbox set estado = 'descartado' where id = %s",
            (m["id"],))
        resumen["descartados"] += 1
        return

    # Lo que inicia Leda espera mientras su destinatario esté activo en una rama
    # abierta en ese chat (T9-R1d-2, T9-R1d-2b): no se envía ni se descarta, sigue
    # `listo` en su lugar de la cola y se cuenta en `retenidos`.
    rama = _rama_que_retiene(cur, m, ahora, pasada.ramas)
    if rama is not None:
        _retener(cur, workspace_id, ahora, m, rama, resumen, pasada)
        return

    # Fuera de horario se pospone, no se descarta. La urgencia autorizada
    # es la única que sale igual.
    if m["tipo"] != "urgente" and not cal.en_horario(ahora):
        cur.execute(
            "update message_outbox set programado_para = %s where id = %s",
            (cal.dentro_de_jornada(ahora), m["id"]))
        resumen["pospuestos"] += 1
        return

    # Un aviso de coordinación (`es_coordinacion`) llega siempre: el tope es de los
    # seguimientos (decisión del usuario, 2026-09-30).
    if (tope and not m["es_coordinacion"] and m["destinatario_membership_id"]
            and _ya_recibio(cur, m["destinatario_membership_id"], ahora)
            >= tope):
        cur.execute(
            "update message_outbox set programado_para = %s where id = %s",
            (cal.dentro_de_jornada(cal.sumar_habiles(ahora, 1)), m["id"]))
        resumen["pospuestos"] += 1
        return

    if _intentar_envio(cur, workspace_id, transporte, cal, ahora, m):
        resumen["enviados"] += 1
    else:
        resumen["fallidos"] += 1


def _marcar_enviado(cur: psycopg.Cursor, ahora: datetime, outbox_id) -> None:
    """El cambio de estado durable: se llama ANTES de intentar el envío
    (ver `_intentar_envio`), no después."""
    cur.execute(
        """update message_outbox set estado = 'enviado', enviado_en = %s
            where id = %s""",
        (ahora, outbox_id))


def _guardar_id_telegram(cur: psycopg.Cursor, tg_id: int, outbox_id) -> None:
    """Guarda el id que devolvió Telegram, en su propio punto de retorno
    (ver `_intentar_envio`): si este UPDATE falla, no puede deshacer la
    marca 'enviado' de arriba -- el mensaje ya se entregó de verdad."""
    cur.execute(
        "update message_outbox set telegram_message_id = %s where id = %s",
        (tg_id, outbox_id))


def _intentar_envio(cur: psycopg.Cursor, workspace_id: str, transporte: Transporte,
                    cal: Calendario, ahora: datetime, m) -> bool:
    """Marca 'enviado' y envía, en ese orden, dentro de un punto de retorno
    propio. Devuelve si se entregó.

    Antes se enviaba primero y se marcaba después: si el UPDATE de la marca
    fallaba, Telegram ya había entregado el mensaje, el punto de retorno
    deshacía la marca, `_fallo` lo contaba como fallido y la próxima pasada
    lo reenviaba -- un duplicado seguro (R3-001, revisión 2026-09-28).

    Ahora la marca -- el cambio de estado durable -- va PRIMERO: si falla,
    nunca se llega a enviar. Si la marca sale bien y el envío falla, el
    punto de retorno deshace la marca y `_fallo` lo cuenta como fallido,
    igual que antes. `telegram_message_id` sólo se conoce después de
    enviar: se guarda en un punto de retorno propio, anidado, cuyo fallo NO
    puede deshacer la marca 'enviado' de la fila -- el mensaje ya se
    entregó, y perder ese id no amerita reenviarlo. Ese fallo se imprime por
    consola (sin el texto crudo de la excepción) y la fila queda con
    `telegram_message_id` nulo; no se registra un incidente.

    El saludo diario (revisión 2026-09-28+2) se decide y reclama ACÁ, entre
    la marca y el envío: es el único punto que sabe qué mensaje sale primero
    de verdad en la fecha local de la persona -- una cadencia pospuesta o un
    mensaje que agotó su tope diario nunca llegan hasta acá. Si el envío
    falla, el mismo punto de retorno que deshace la marca deshace la reserva
    del saludo con él (`saludo.reclamar_y_anteponer` ya corre en su propio
    SAVEPOINT anidado, así que una falla SÓLO del saludo -- tabla faltante,
    zona inválida -- no le impide a este mensaje salir sin saludo). Si
    anteponerlo no entraría en el límite real de Telegram, tampoco reclama
    la reserva (R3-003, revisión 2026-09-28+3) -- el mensaje sale igual, sin
    saludo.

    `saludo.reclamar_y_anteponer` nunca reporta su propia falla: la
    reportamos ACÁ, DESPUÉS de que el punto de retorno de arriba se resolvió
    -- éxito o fallo -- nunca todavía adentro (R4-002/R3-001, revisión
    2026-09-28+3): reportarla ahí se perdía si el envío fallaba después, el
    SAVEPOINT entero se revertía con el incidente adentro, y la marca "ya
    reportado" en memoria no se revierte con él -- la falla real nunca se
    volvía a reportar."""
    falla_saludo: Exception | None = None
    try:
        with cur.connection.transaction():
            _marcar_enviado(cur, ahora, m["id"])
            botones = _botones(cur, m)
            texto, falla_saludo = saludo.reclamar_y_anteponer(
                cur, workspace_id=workspace_id,
                membership_id=m["destinatario_membership_id"], zona=cal.zona,
                ahora=ahora, texto=m["cuerpo"], has_buttons=bool(botones),
                es_bienvenida=m["es_bienvenida"])
            if m["bloque_copiable"]:
                tg_id = transporte.enviar(m["chat_id"], texto, botones,
                                          bloque=m["bloque_copiable"])
            else:
                tg_id = transporte.enviar(m["chat_id"], texto, botones)
            try:
                with cur.connection.transaction():
                    _guardar_id_telegram(cur, tg_id, m["id"])
            except Exception as exc_id:  # noqa: BLE001 -- se aísla, no deshace la marca
                print(f"  ! no se pudo guardar el id de Telegram del mensaje "
                     f"{m['id']} ({type(exc_id).__name__}).")
    except Exception as e:  # noqa: BLE001 — se registra, no se propaga
        _fallo(cur, workspace_id, m, e, cal, ahora)
        enviado = False
    else:
        enviado = True
    if falla_saludo is not None:
        _reportar_falla_saludo_aislada(cur, workspace_id, falla_saludo)
    return enviado


def _reportar_falla_saludo_aislada(cur, workspace_id: str,
                                   falla: Exception) -> None:
    """Reporta la falla del saludo en su propio savepoint: si el reporte
    también falla, no puede deshacer la marca de un mensaje ya entregado."""
    try:
        with cur.connection.transaction():
            saludo.reportar_falla(cur, workspace_id, falla)
    except Exception as e:  # noqa: BLE001 — el mensaje ya salió
        print(f"  ! no se pudo reportar la falla del saludo "
              f"({type(e).__name__}).")


def despachar_avisos_admin(cur: psycopg.Cursor, transporte: Transporte,
                           ahora: datetime | None = None,
                           lote: int = 50) -> dict[str, int]:
    """Entrega los avisos de incidente encolados para la administración de
    plataforma (`admin_notice`, T28, Constitución §10).

    Corre bajo rol `leda_admin`: un aviso no tiene un único espacio dueño
    -- puede venir de cualquiera, o de ninguno (incidente global) -- así que
    no hay un `espacio()` que lo acote, a diferencia de `despachar`.

    No aplica el calendario ni el tope diario de `despachar`: esa mecánica
    protege a un integrante de un equipo de mensajes automáticos fuera de
    horario; esto es una alerta operativa para quien administra la
    plataforma, no un mensaje de cadencia.

    Un intento fallido no se reintenta de inmediato: se pospone
    `programado_para` con backoff creciente (`BACKOFF_MINUTOS_AVISO_ADMIN`),
    igual motivo que `_fallo` para `message_outbox` pero sin su calendario
    -- acá no hay jornada laboral que respetar, sólo un blip de Telegram que
    dejar pasar. Un aviso que agota `MAX_INTENTOS` no desaparece en
    silencio (regla del proyecto: nunca fallar en silencio): deja un
    incidente de severidad alta apuntando a esa fila, con
    `avisar_admin=False` -- avisar por el mismo canal que justo falló
    encadenaría incidentes sin fin (ver `incidentes.registrar_incidente`).

    Reusable por el validador de invariantes diario que se agregue después
    (`odd/tasks/validador-invariantes.md`): el mismo camino que entrega un
    aviso de incidente entrega cualquier otro aviso que ese proceso encole
    en `admin_notice`.

    El registro de ESE incidente corre en un punto de retorno propio
    (SAVEPOINT, mismo patrón que `agente._ejecutar_una`) -- hallazgo R3-002
    de la revisión, 2026-09-28. Quien llama hace un único `commit` al final
    del lote: si la escritura del incidente fallara sin este aislamiento, el
    lote entero se revertiría y los avisos ya entregados volverían a
    `'listo'` y se reenviarían. Con él se deshace sólo esa escritura, y el
    fallo no queda en silencio: se cuenta en
    `resumen["incidentes_sin_registrar"]` y deja una marca en el
    `ultimo_error` del aviso."""
    ahora = ahora or datetime.now(timezone.utc)
    resumen = {"enviados": 0, "fallidos": 0, "agotados": 0,
               "incidentes_sin_registrar": 0}

    cur.execute(
        """select id, workspace_id, chat_id, cuerpo, intentos
             from admin_notice
            where estado = 'listo' and programado_para <= %s
            order by programado_para
            limit %s
            for update skip locked""",
        (ahora, lote))
    pendientes = cur.fetchall()

    for n in pendientes:
        try:
            tg_id = transporte.enviar(n["chat_id"], n["cuerpo"])
        except Exception as e:  # noqa: BLE001 — se registra, no se propaga
            intentos = n["intentos"] + 1
            agotado = intentos >= MAX_INTENTOS
            estado = "fallido" if agotado else "listo"
            proximo = None if agotado else _proximo_intento_admin(intentos, ahora)
            # Redactado antes de recortar (R1-001, revisión 2026-09-28):
            # recortar primero podría cortar un token a la mitad y dejar
            # el resto sin que el patrón lo reconozca.
            ultimo_error = redactar_secreto_telegram(str(e))[:500]
            cur.execute(
                """update admin_notice
                      set intentos = %s, ultimo_error = %s, estado = %s,
                          programado_para = coalesce(%s, programado_para)
                    where id = %s""",
                (intentos, ultimo_error, estado, proximo, n["id"]))
            resumen["fallidos"] += 1
            if agotado:
                resumen["agotados"] += 1
                try:
                    with cur.connection.transaction(force_rollback=False):
                        registrar_incidente(
                            cur, n["workspace_id"],
                            f"Un aviso a la administración no se pudo entregar "
                            f"tras {MAX_INTENTOS} intentos.",
                            severidad="alta", referencia_cruda=ultimo_error,
                            etapa=ETAPA_ENTREGA_AVISO_ADMIN,
                            referencia_tipo=REFERENCIA_ADMIN_NOTICE,
                            referencia_id=n["id"], chat_id=n["chat_id"],
                            avisar_admin=False)
                except Exception as exc_incidente:  # noqa: BLE001 — se aísla, no se propaga
                    resumen["incidentes_sin_registrar"] += 1
                    cur.execute(
                        """update admin_notice
                              set ultimo_error = ultimo_error || %s
                            where id = %s""",
                        (f" · incidente no registrado: "
                         f"{type(exc_incidente).__name__}", n["id"]))
            continue

        cur.execute(
            """update admin_notice
                  set estado = 'enviado', enviado_en = %s, telegram_message_id = %s
                where id = %s""",
            (ahora, tg_id, n["id"]))
        resumen["enviados"] += 1

    return resumen


def _fallo(cur, workspace_id: str, m, error: Exception, cal: Calendario,
           ahora: datetime) -> None:
    intentos = m["intentos"] + 1
    estado = "fallido" if intentos >= MAX_INTENTOS else "listo"
    # Una respuesta conserva su lugar en la cola (F-A1): reprogramada al `ahora` de
    # la pasada saldría detrás de las partes que la siguen. El resto de lo que
    # Leda envía se reprograma como siempre.
    proximo = (cal.dentro_de_jornada(ahora)
               if estado == "listo" and not m["es_respuesta"] else None)
    # Redactado antes de recortar (R1-001, revisión 2026-09-28): recortar
    # primero podría cortar un token a la mitad y dejar el resto sin que
    # el patrón lo reconozca.
    ultimo_error = redactar_secreto_telegram(str(error))[:500]
    cur.execute(
        """update message_outbox
              set intentos = %s, ultimo_error = %s, estado = %s,
                  programado_para = coalesce(%s, programado_para)
            where id = %s""",
        (intentos, ultimo_error, estado, proximo, m["id"]))
    if estado == "fallido":
        registrar_incidente(
            cur, workspace_id,
            f"Un mensaje no se pudo entregar tras {MAX_INTENTOS} intentos.",
            severidad="alta", etapa=ETAPA_ENTREGA_MENSAJE)


def _ya_recibio(cur, membership_id: str, ahora: datetime) -> int:
    """Cuántos mensajes automáticos le llegaron hoy a esta persona.

    El tope es por persona, no por espacio: alguien en tres equipos no debería
    recibir tres seguimientos el mismo día.

    Sólo cuenta lo que Leda inicia: una respuesta a lo que la persona escribió o
    tocó (`es_respuesta`) "no es automática" y nunca cuenta contra el tope
    (`_despachar_fila`, ADR 0011). Contarlas dejaba sin su aviso a quien
    conversaba con Leda: tres respuestas del día alcanzaban para posponer al
    día hábil siguiente el "X entregó…" o el "X pidió cambios…" (R4-H7).

    Tampoco cuentan los avisos de coordinación (`es_coordinacion`: lo que otra
    persona hizo sobre trabajo compartido y esta necesita para actuar o
    enterarse): no consumen la cuota de los seguimientos, que es lo único que el
    tope limita (decisión del usuario, 2026-09-30).
    """
    cur.execute(
        """
        select count(*) n
          from message_outbox o
          join membership m  on m.id = o.destinatario_membership_id
          join membership m2 on m2.app_user_id = m.app_user_id
         where m2.id = %s
           and o.estado = 'enviado'
           and not o.es_respuesta
           and not o.es_coordinacion
           and o.enviado_en::date = %s
        """,
        (membership_id, ahora.date()))
    return cur.fetchone()["n"]


def confirmar(cur: psycopg.Cursor, outbox_id: str, app_user_id: str) -> bool:
    """Pasa un mensaje de 'esperando_confirmacion' a 'listo'.

    Las acciones que el núcleo obliga a confirmar entran a la cola en ese
    estado y no salen hasta que una persona las aprueba.
    """
    cur.execute(
        """update message_outbox
              set estado = 'listo', confirmado_por = %s, confirmado_en = now()
            where id = %s and estado = 'esperando_confirmacion'""",
        (app_user_id, outbox_id))
    return cur.rowcount > 0
