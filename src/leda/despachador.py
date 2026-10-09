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

import json
import random
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable, NamedTuple, Protocol

import psycopg

from . import saludo
from .calendario import Calendario
from .incidentes import (ETAPA_ENTREGA_AVISO_ADMIN, ETAPA_ENTREGA_MENSAJE,
                         ETAPA_ENTREGA_REINTENTO, REFERENCIA_ADMIN_NOTICE, redactar_secreto_telegram,
                         registrar_incidente)
from .salida import (ETIQUETA_COPIAR, cabe_en_boton_de_copiar, formatear, prepare_buttons,
                     prepare_payload, texto_y_entidades)


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
    `bloque` es el bloque que se copia con un toque, si el mensaje lo llevaba.
    `texto` es el que vio la persona, ya sin las marcas de formato, y `entidades`, las de
    Telegram (`salida.texto_y_entidades`), o `None` si el mensaje no tenía ninguna. Un álbum
    (`enviar_album`) se entrega sin texto, con el nombre de cada foto en `fotos`."""
    chat_id: int
    texto: str
    botones: list[Boton]
    bloque: str | None = None
    entidades: list[dict] | None = None
    fotos: list[str | None] | None = None
    # Si salió con la vista previa de los enlaces desactivada (el de la página de una tarea).
    sin_vista_previa: bool = False


class Adjunto(NamedTuple):
    """Una foto de un álbum, como la recibe el transporte (ADR 0019, decisión 6): su nombre y su
    tipo, el identificador que el canal le dio al recibirla, si sirve para mandarla otra vez
    (`file_id`, del mismo bot del espacio), y cómo leer la copia propia (`contenido`), que se lee
    sólo si hay que subirla."""
    nombre: str | None
    tipo: str
    file_id: str | None
    contenido: Callable[[], bytes]


class Transporte(Protocol):
    def enviar(self, chat_id: int, texto: str,
               botones: list[Boton] | None = None) -> int:
        """Devuelve el identificador del mensaje entregado. Un mensaje con un
        bloque copiable (T9-R1c-3) se entrega con `bloque=...` además: sólo los
        mensajes que lo llevan pasan ese argumento. Uno que lleva el enlace a la
        página de una tarea (ADR 0019, decisión 6) se entrega con
        `sin_vista_previa=True`: sólo ésos lo pasan."""

    def enviar_album(self, chat_id: int, adjuntos: list[Adjunto]) -> int:
        """Manda las fotos de una fila con adjuntos, sin texto, y devuelve el identificador
        del primer mensaje (ADR 0019, decisión 6)."""


@dataclass
class TransporteDePrueba:
    enviados: list[Entregado] = field(default_factory=list)
    falla_en: set[int] = field(default_factory=set)
    albumes: list[list[Adjunto]] = field(default_factory=list)

    def enviar(self, chat_id: int, texto: str,
               botones: list[Boton] | None = None,
               bloque: str | None = None, sin_vista_previa: bool = False) -> int:
        prepared_buttons = prepare_buttons(botones or [])
        payload = prepare_payload(
            texto, dedupe_key="transport", has_buttons=bool(prepared_buttons),
        )[0]
        plano, entidades = texto_y_entidades(payload.text, bloque)
        if chat_id in self.falla_en:
            raise ConnectionError(f"no se pudo entregar a {chat_id}")
        self.enviados.append(Entregado(
            chat_id, plano, [Boton(*button) for button in prepared_buttons],
            bloque, entidades or None, sin_vista_previa=sin_vista_previa))
        return len(self.enviados)

    def enviar_album(self, chat_id: int, adjuntos: list[Adjunto]) -> int:
        if chat_id in self.falla_en:
            raise ConnectionError(f"no se pudo entregar a {chat_id}")
        self.albumes.append(list(adjuntos))
        self.enviados.append(Entregado(chat_id, "", [], fotos=[a.nombre for a in adjuntos]))
        return len(self.enviados)


class TransporteTelegram:
    def __init__(self, token: str, cliente=None) -> None:
        import httpx
        self._base = f"https://api.telegram.org/bot{token}/"
        self._url = self._base + "sendMessage"
        self._cliente = cliente or httpx.Client(timeout=15)

    def enviar(self, chat_id: int, texto: str,
               botones: list[Boton] | None = None,
               bloque: str | None = None, sin_vista_previa: bool = False) -> int:
        prepared_buttons = prepare_buttons(botones or [])
        payload = prepare_payload(
            texto, dedupe_key="transport", has_buttons=bool(prepared_buttons),
        )[0]
        # El formato de los mensajes (2026-10-07): texto plano y entidades, nunca
        # `parse_mode`. El bloque que se copia con un toque (T9-R1c-3) es una entidad
        # `pre` sobre el final del texto que de verdad se manda. Sin ninguna, el cuerpo
        # no lleva `entities`.
        plano, entidades = texto_y_entidades(payload.text, bloque)
        cuerpo: dict = {"chat_id": chat_id, "text": plano,
                         "disable_notification": False}
        if entidades:
            cuerpo["entities"] = entidades
        if sin_vista_previa:
            # El enlace a la página de una tarea (ADR 0019, decisión 6): que Telegram no la
            # abra por su cuenta para armar una vista previa.
            cuerpo["link_preview_options"] = {"is_disabled": True}
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

    def enviar_album(self, chat_id: int, adjuntos: list[Adjunto]) -> int:
        """Las fotos de una fila con adjuntos (ADR 0019, decisión 6): una sola, como foto; de
        dos a diez, como álbum. Primero con el identificador que Telegram le dio a cada una al
        recibirla, que es del mismo bot del espacio y no vuelve a subir nada; si Telegram no lo
        acepta (otro bot, un identificador vencido), sube la copia propia de todas. El error de
        la segunda vuelta es el que queda."""
        if not any(a.file_id for a in adjuntos):
            return self._album(chat_id, adjuntos, reusar=False)
        try:
            return self._album(chat_id, adjuntos, reusar=True)
        except ErrorTelegram:
            return self._album(chat_id, adjuntos, reusar=False)

    def _album(self, chat_id: int, adjuntos: list[Adjunto], *, reusar: bool) -> int:
        subidas: dict[str, tuple[str, bytes, str]] = {}
        medios = []
        for i, a in enumerate(adjuntos):
            if reusar and a.file_id:
                medios.append({"type": "photo", "media": a.file_id})
                continue
            clave = f"foto{i}"
            subidas[clave] = (a.nombre or f"{clave}.jpg", a.contenido(), a.tipo)
            medios.append({"type": "photo", "media": f"attach://{clave}"})
        datos: dict = {"chat_id": chat_id}
        if len(medios) == 1:
            metodo = "sendPhoto"
            if subidas:
                subidas = {"photo": next(iter(subidas.values()))}
            else:
                datos["photo"] = medios[0]["media"]
        else:
            metodo = "sendMediaGroup"
            datos["media"] = json.dumps(medios)
        r = pedido_telegram(self._cliente.post, self._base + metodo, data=datos,
                            files=subidas or None)
        pedido_telegram(r.raise_for_status)
        resultado = r.json()["result"]
        return (resultado[0] if isinstance(resultado, list) else resultado)["message_id"]

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
    """Telegram pidió ir más despacio (HTTP 429): no es una falla del borrador, se espera lo
    que pide y se sigue."""

    def __init__(self, espera: float) -> None:
        super().__init__(f"Telegram pidió esperar {espera} s")
        self.espera = espera


# Lo más que se espera ante un 429 antes de volver a mandar el borrador: el mensaje de verdad
# sale igual, así que no vale la pena esperar más.
ESPERA_MAXIMA_RITMO = 2.0

# Un mensaje de Telegram admite hasta 4096 caracteres; el borrador, también.
LIMITE_DE_BORRADOR = 4096

# Cada cuánto, a lo sumo, se actualiza el borrador con el texto que la IA va escribiendo. El
# primero sale enseguida; lo que llega antes se junta y sale lo último. Es el valor que pidió
# el usuario en la prueba real del 2026-10-01 ("que apenas tenga algo para mostrar lo
# muestre"), en la rama congelada; un 429 de Telegram se respeta igual. Valor a configurar
# desde la plataforma.
INTERVALO_DE_BORRADOR = 0.15


def texto_del_borrador(texto: str) -> str:
    """Lo que muestra el borrador de un texto a medio escribir: texto plano, sin las marcas del
    formato (`salida.formatear`), que llegan como negritas con el mensaje de verdad. Una marca
    que todavía no se cerró tampoco se ve."""
    plano = formatear(texto)[0].replace("**", "").rstrip("*")
    return plano[:LIMITE_DE_BORRADOR]


def _enviar_borrador_texto(http, token: str, chat_id: int, draft_id: int,
                           texto: str) -> None:
    """El mismo borrador nativo de la semilla, con texto: Telegram lo reemplaza (mismo
    `draft_id`) y lo muestra creciendo. Un 429 se distingue (`_RitmoTelegram`) y cualquier otro
    error HTTP se levanta."""
    r = pedido_telegram(
        http.post, f"https://api.telegram.org/bot{token}/sendMessageDraft",
        json={"chat_id": chat_id, "draft_id": draft_id, "text": texto})
    codigo = getattr(r, "status_code", 200)
    if codigo == 429:
        try:
            espera = float(((r.json() or {}).get("parameters") or {}).get("retry_after", 1))
        except Exception:  # noqa: BLE001 - sin cuerpo legible, un segundo
            espera = 1.0
        raise _RitmoTelegram(espera)
    if codigo >= 400:
        raise ErrorTelegram(f"HTTP {codigo}: {_descripcion_telegram(r) or ''}".strip())


class IndicadorDeActividad:
    """Lo que `mantener_chat_activo` le da a quien atiende el turno: el borrador nativo que
    abrió el indicador, para mostrarle el texto que la IA va redactando (respuesta en vivo,
    pedido del usuario del 2026-10-07; mecanismo de la rama congelada, probado en Telegram real
    el 2026-10-01).

    Efímero: es el borrador, nunca un mensaje; no pasa por el outbox, no se audita y no lleva
    botones. El mensaje de verdad sale por el outbox, con su texto: la Bot API dice que el
    borrador es una vista previa efímera y que, al terminar, se manda el mensaje completo con
    `sendMessage`. Cuando sigue un mensaje (quien atiende el turno llama a `sigue_la_respuesta`),
    el cierre no retira nada antes de él (pedido del usuario, 2026-10-07: "La función del
    escribiendo y el '…' es mostrar que Leda está activa, no generar demora en la respuesta");
    sólo espera, acotado, a que termine el envío del borrador que esté en vuelo, y el retiro
    queda para después del mensaje (`retirar_tras_la_respuesta`; D8: el mensaje no siempre
    reemplazaba al borrador y los tres puntos quedaban a la vista). Seguro entre hilos: lo llama el hilo que
    lee lo que escribe la IA mientras el hilo del indicador manda la semilla y el
    "escribiendo…"; `candado` ordena los envíos del borrador, y cada uno mira `cerrado` justo
    antes de salir."""

    def __init__(self, http, token: str, chat_id: int, draft_id: int,
                 admite_borrador: bool, impresos: set[str], reloj=time.monotonic,
                 intervalo: float = INTERVALO_DE_BORRADOR) -> None:
        self._http, self._token, self._chat_id = http, token, chat_id
        self.draft_id = draft_id
        self.admite_borrador = admite_borrador
        self._impresos, self._reloj, self._intervalo = impresos, reloj, intervalo
        self.candado = threading.Lock()
        self.cerrado = threading.Event()
        # Con texto en el borrador, la semilla ya no se manda: lo taparía.
        self.con_texto = threading.Event()
        self.intentado = threading.Event()
        self.activado = threading.Event()
        # Se le pidió a Telegram un borrador (semilla o texto), haya vuelto bien o no: es lo que
        # puede haber quedado a la vista y hay que retirar. Se marca con el candado tomado, justo
        # antes del pedido (D8).
        self.pedido = threading.Event()
        # Al turno le sigue un mensaje, que reemplaza al borrador: el cierre no lo retira.
        self.sigue_respuesta = threading.Event()
        self._ultimo_texto: str | None = None
        self._ultimo_envio: float | None = None
        self._fallo = False
        # El último texto que tiene que mostrar el borrador y si hay un trabajador mandándolo
        # (`_trabajar`): uno solo por indicador.
        self._estado = threading.Lock()
        self._pendiente: str | None = None
        self._trabajando = False
        # El retiro del borrador que queda para después de la respuesta (`mantener_chat_activo`
        # lo deja al cerrar, si sigue un mensaje): `retirar_tras_la_respuesta` lo hace una vez.
        self._retiro: Callable[[], Exception | None] | None = None

    def retirar_tras_la_respuesta(self) -> Exception | None:
        """Después de que salió el mensaje de verdad (o de que falló al salir), el borrador se
        retira igual que en un turno sin mensaje (`_cerrar_sin_respuesta`), si se llegó a mostrar:
        en la prueba por Telegram del 2026-10-08 (D8) los tres puntos quedaron a la vista en
        varios chats, porque el mensaje no siempre lo reemplaza y un envío del borrador que estaba
        en vuelo podía llegar después del mensaje. Lo llama quien despachó la respuesta, una sola
        vez; sin retiro pendiente, no hace nada. Nunca lanza: devuelve la falla del retiro (ya
        reportada en la consola) para que quien llama deje el incidente, o `None`."""
        retiro, self._retiro = self._retiro, None
        if retiro is None:
            return None
        try:
            return retiro()
        except Exception as e:  # noqa: BLE001 - cosmético, pero nunca en silencio
            _reportar_falla_indicador(self._impresos, "retiro", e)
            return e

    def sigue_la_respuesta(self) -> None:
        """Avisa que al turno le sigue un mensaje de verdad (ya confirmado en el outbox): el
        cierre no lo retira antes del mensaje (el retiro antes de la respuesta se veía como "aparece
        y se va"), espera a que termine el envío del borrador que esté en vuelo, para que ninguno
        llegue después del mensaje, y deja el retiro para después de la respuesta
        (`retirar_tras_la_respuesta`). Sin este aviso, el cierre retira el borrador enseguida,
        porque no sigue ningún mensaje."""
        self.sigue_respuesta.set()

    def actualizar_borrador(self, texto: str) -> None:
        """Deja `texto` (lo escrito hasta ahora) como lo último que tiene que mostrar el
        borrador. Nunca espera a Telegram y nunca lanza: un solo trabajador en segundo plano
        manda siempre el texto más reciente, a lo sumo una vez cada `intervalo`, y sólo si
        cambió; lo que llega mientras hay un envío en vuelo o antes del intervalo queda
        pendiente y sale apenas se puede. Una falla se reporta una vez por turno y no se
        insiste en el resto del turno. Después del cierre no hace nada: la respuesta de una IA
        que llega tarde nunca reabre un borrador."""
        if not self.admite_borrador or self._fallo or self.cerrado.is_set():
            return
        try:
            texto = texto_del_borrador(texto)
        except Exception:  # noqa: BLE001 - cosmético: sin texto, quedan los tres puntos
            return
        if not texto.strip():
            return
        with self._estado:
            self._pendiente = texto
            if self._trabajando:
                return
            self._trabajando = True
        self.con_texto.set()
        self.activado.set()
        try:
            threading.Thread(target=self._trabajar, name="leda-borrador",
                             daemon=True).start()
        except Exception:  # noqa: BLE001 - cosmético: sin hilo no hay texto en vivo
            self._terminar()

    def _terminar(self) -> None:
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
                    self._terminar()
                    return
                with self._estado:
                    texto = self._pendiente      # lo más nuevo después de esperar
            with self.candado:
                if self.cerrado.is_set() or self._fallo:
                    self._terminar()
                    return
                self._ultimo_envio = self._reloj()
                ritmo = None
                self.pedido.set()
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
                self._terminar()
                return


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
                         umbral: float = 1.5, intervalo: float = 4.0,
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

    Da el `IndicadorDeActividad` del turno: con `actualizar_borrador`, quien
    atiende el turno muestra en el borrador el texto que la IA va
    redactando (pedido del usuario, 2026-10-07). Sin texto, el borrador
    queda con la semilla: los tres puntos. Si no se pudo armar el
    indicador, da `None`.

    El borrador sólo se intenta si `chat_type` es `"private"` -- Bot API
    9.5 sólo lo abrió ahí; en grupo o canal degrada en silencio a sólo
    typing.

    Al salir del bloque, el indicador no retira nada antes de la respuesta
    (pedido del usuario, 2026-10-07). Si quien atiende el turno avisó que
    sigue un mensaje (`IndicadorDeActividad.sigue_la_respuesta`), el cierre
    marca el indicador cerrado (ningún envío del borrador empieza después)
    y espera, acotado a `timeout_borrador`, a que termine el que esté en
    vuelo: así ningún borrador le llega a Telegram después del
    `sendMessage` de la respuesta (D8; antes eran dos pedidos en paralelo y
    uno tardío volvía a mostrar el borrador). El retiro queda para después
    del mensaje: quien lo despachó llama a
    `IndicadorDeActividad.retirar_tras_la_respuesta`, que retira el
    borrador como un turno sin mensaje, si se llegó a mostrar (el mensaje
    no siempre lo reemplazaba, y una respuesta que no salió lo dejaba a la
    vista sin nada). Si no avisó -- un turno sin mensaje nuevo, o un
    llamador que no sabe --, se retira al cerrar (ADR 0011, decisión 3;
    `_cerrar_sin_respuesta`).

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
    `espera_cierre` no prueba que esa llamada ya volvió. Antes de retirar,
    se espera (acotado a `timeout_borrador`, el mismo timeout que ya tiene
    el cliente HTTP) a que el intento de mandar el borrador termine de
    verdad. Con un mensaje que sigue, la misma espera va antes del mensaje
    (y otra vez antes del retiro, por si la primera se agotó)."""
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
    indicador = IndicadorDeActividad(http, token, chat_id, draft_id, intenta_borrador,
                                     impresos, reloj, intervalo_borrador)
    # Los mismos eventos de siempre, compartidos con el indicador: el texto en vivo también
    # "activa" el borrador y resuelve su intento.
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
                        # semilla lo taparía: no se manda. Después del cierre
                        # tampoco: la respuesta ya puede estar saliendo.
                        if not (indicador.con_texto.is_set()
                                or indicador.cerrado.is_set()):
                            indicador.pedido.set()
                            _enviar_borrador_semilla(http, token, chat_id, draft_id)
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
    try:
        yield indicador
    finally:
        # Ningún texto más: lo que la IA mande después se descarta, y ningún envío del
        # borrador empieza desde acá (cada uno mira `cerrado` justo antes de salir).
        indicador.cerrado.set()
        detener.set()
        if not indicador.sigue_respuesta.is_set():
            _cerrar_sin_respuesta(indicador, hilo, http, token, chat_id, owned_client,
                                  impresos, espera_cierre, timeout_borrador, cur,
                                  workspace_id)
        else:
            # Sigue un mensaje de verdad. Ningún envío del borrador EMPIEZA después del cierre
            # (cada uno mira `cerrado` con el candado tomado), y acá se espera, acotado, a que
            # vuelva el que estaba en vuelo: el cierre es anterior al despacho de la respuesta,
            # así que ningún borrador le llega a Telegram después del mensaje (D8: uno tardío
            # volvía a mostrar el borrador). La espera es la de un pedido ya en vuelo, nunca un
            # retiro antes del mensaje (pedido del usuario, 2026-10-07).
            if indicador.candado.acquire(timeout=timeout_borrador):
                indicador.candado.release()
            # El retiro, después del mensaje (o de su falla): lo pide quien lo despachó. Sin
            # "escribiendo…" después: ya no hay respuesta que esperar.
            indicador._retiro = lambda: _cerrar_sin_respuesta(
                indicador, hilo, http, token, chat_id, owned_client, impresos, espera_cierre,
                timeout_borrador, cur, workspace_id, escribiendo_despues=False)


def _cerrar_sin_respuesta(indicador: IndicadorDeActividad, hilo: threading.Thread, http,
                          token: str, chat_id: int, owned_client: bool, impresos: set[str],
                          espera_cierre: float, timeout_borrador: float, cur,
                          workspace_id: str | None, *,
                          escribiendo_despues: bool = True) -> Exception | None:
    """El retiro del borrador, si se llegó a mostrar (ADR 0011, decisión 3): al cerrar un turno
    al que no le sigue ningún mensaje (o de un llamador que no avisa que le sigue uno), y después
    del mensaje de un turno que sí lo tiene (`IndicadorDeActividad.retirar_tras_la_respuesta`,
    D8). Nunca va antes de un mensaje, así que no demora ninguno. Después del retiro de un turno
    sin mensaje sale un "escribiendo…" (`_escribiendo_tras_el_retiro`); después de la respuesta,
    no (`escribiendo_despues=False`): ya no hay nada que esperar.

    El retiro nunca puede llegar antes que el propio borrador (R3-001, revisión 2026-09-28
    sobre el commit e2a094e): se espera, acotado a `timeout_borrador`, a que el envío en vuelo
    del borrador (semilla o texto) termine; si ni con ese margen resolvió, se abandona el
    retiro en vez de arriesgar el orden. Devuelve la falla del retiro, ya reportada (en la
    consola y, con `cur`, en un incidente), o `None`."""
    import httpx

    if indicador.candado.acquire(timeout=timeout_borrador):
        indicador.candado.release()
    try:
        hilo.join(timeout=espera_cierre)
    except Exception:  # noqa: BLE001 - cosmetic
        pass
    # El cliente que refresca typing se cierra adentro del propio hilo (si es propio, arriba
    # de `ciclo`): el retiro usa un cliente PROPIO y de corta vida cuando el llamador no
    # inyectó uno, así que nunca compite por el mismo cliente que el hilo de typing todavía
    # puede estar cerrando.
    #
    # Sólo si se le pidió algún borrador a Telegram: con el indicador cerrado y el candado ya
    # tomado una vez, ningún pedido del borrador empieza después, así que si no hubo ninguno
    # no hay nada a la vista (antes se miraba `activado`, que se marca también cuando el
    # borrador nunca llegó a pedirse, y el retiro esperaba en vano su tope, D8).
    if not (indicador.pedido.is_set() and indicador.admite_borrador):
        return None
    if not indicador.intentado.wait(timeout_borrador):
        # Ni con ese margen se resolvió (cliente colgado más allá de su propio timeout):
        # abandonar el retiro en vez de arriesgar que llegue antes que un borrador que
        # todavía no se sabe si se mandó (R3-001).
        falla = TimeoutError("el borrador no terminó de intentarse a tiempo para retirarlo")
        _reportar_falla_indicador(impresos, "retiro", falla)
        _reportar_falla_retiro(cur, workspace_id, falla)
        return falla
    try:
        if owned_client:
            with httpx.Client(timeout=_TIMEOUT_CLIENTE_INDICADOR) as http_retiro:
                _retirar_borrador(http_retiro, token, chat_id)
                if escribiendo_despues:
                    _escribiendo_tras_el_retiro(http_retiro, token, chat_id, impresos)
        else:
            _retirar_borrador(http, token, chat_id)
            if escribiendo_despues:
                _escribiendo_tras_el_retiro(http, token, chat_id, impresos)
    except Exception as e:  # noqa: BLE001 - no fatal, pero pesa más
        _reportar_falla_indicador(impresos, "retiro", e)
        _reportar_falla_retiro(cur, workspace_id, e)
        return e
    return None


def registrar_falla_del_retiro(cur, workspace_id: str | None, error: Exception) -> None:
    """El incidente de un borrador que no se pudo retirar después de la respuesta (D8), para
    quien la despachó y tiene la base a mano: el mismo de `_cerrar_sin_respuesta`, deduplicado
    por proceso (`_reportar_falla_retiro`)."""
    _reportar_falla_retiro(cur, workspace_id, error)


def _escribiendo_tras_el_retiro(http, token: str, chat_id: int, impresos: set[str]) -> None:
    """El retiro manda (y borra) un mensaje, y cualquier mensaje del bot apaga el
    "escribiendo…" en Telegram; la respuesta de verdad sale después, por el outbox, y ese
    hueco se veía como "aparece y se va antes de la respuesta" (prueba real del 2026-10-01, en
    la rama congelada). Un "escribiendo…" más lo cubre hasta que la respuesta llega y lo
    reemplaza. Falla como cualquier typing: no fatal, se reporta."""
    try:
        _enviar_chat_action(http, token, chat_id)
    except Exception as e:  # noqa: BLE001 - no fatal, se reporta
        _reportar_falla_indicador(impresos, "typing", e)


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
    if not m["pending_action_id"]:
        return []

    from .pendientes import callback_data, opciones

    return [Boton(o.etiqueta, callback_data(o))
            for o in opciones(cur, m["pending_action_id"])]


def _preview_vigente(cur, m, ahora: datetime) -> bool:
    """Si la vista previa que lleva `m` sigue siendo la vigente al `ahora` de la
    pasada: el mismo reloj que decide el vencimiento del mensaje."""
    if not m["pending_action_id"]:
        return True
    cur.execute(
        """select p.estado, p.draft_id, p.membership_id,
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


def despachar(cur: psycopg.Cursor, workspace_id: str, transporte: Transporte,
              cal: Calendario, ahora: datetime | None = None,
              lote: int = 50) -> dict[str, int]:
    """Una pasada del despachador: examina a lo sumo `lote` filas, de a una. Lo
    que queda por despachar sale en la pasada siguiente."""
    ahora = ahora or datetime.now(timezone.utc)
    tope = _tope_diario(cur, workspace_id)
    resumen = {"enviados": 0, "pospuestos": 0, "fallidos": 0, "descartados": 0}
    vistos: list[str] = []
    # Los álbumes que esperan a su texto: si en esta pasada sale un mensaje, se vuelven a mirar
    # (su texto pudo ser ése), así el álbum sale enseguida después y no en la pasada siguiente.
    esperan: list[str] = []
    while len(vistos) < lote:
        cur.execute(
            """
             select id, workspace_id, chat_id, cuerpo, tipo,
                    destinatario_membership_id, intentos,
                    vence_en, es_respuesta, pending_action_id,
                    es_bienvenida, bloque_copiable, es_coordinacion, respuesta_grupo,
                    array(select a.archivo_id from message_outbox_adjunto a
                           where a.outbox_id = message_outbox.id
                           order by a.orden) as adjuntos,
                    (select e.task_id from message_outbox_enlace e
                      where e.outbox_id = message_outbox.id) as enlace_tarea,
                    (select e.membership_id from message_outbox_enlace e
                      where e.outbox_id = message_outbox.id) as enlace_persona
              from message_outbox
             where workspace_id = %(ws)s
               and estado = 'listo'
               and programado_para <= %(ahora)s
               and id <> all(%(vistos)s::uuid[])
             order by programado_para,
                      exists (select 1 from message_outbox_adjunto a
                               where a.outbox_id = message_outbox.id)
             limit 1
             for update skip locked
            """,
            {"ws": workspace_id, "ahora": ahora, "vistos": vistos})
        m = cur.fetchone()
        if m is None:
            break
        vistos.append(str(m["id"]))
        enviados = resumen["enviados"]
        if _despachar_fila(cur, workspace_id, transporte, cal, ahora, tope, m,
                           resumen) == "espera":
            esperan.append(str(m["id"]))
        elif resumen["enviados"] > enviados and esperan:
            vistos = [v for v in vistos if v not in esperan]
            esperan = []
    return resumen


def _despachar_fila(cur, workspace_id: str, transporte: Transporte,
                    cal: Calendario, ahora: datetime, tope, m,
                    resumen: dict) -> str | None:
    if not _preview_vigente(cur, m, ahora):
        resumen["descartados"] += 1
        return
    if m["adjuntos"]:
        # El álbum de una respuesta sale después de su texto (ADR 0019, decisión 6): mientras
        # el texto no salió, espera (sin contar como pospuesto: no se movió de hora); si el
        # texto ya no va a salir, el álbum tampoco, porque solo no se entiende. La falla del
        # texto ya dejó su incidente (`_fallo`).
        antes = _el_texto_del_album(cur, workspace_id, m)
        if antes == "no_sale":
            cur.execute(
                "update message_outbox set estado = 'descartado' where id = %s", (m["id"],))
            resumen["descartados"] += 1
            return
        if antes == "espera":
            return "espera"
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


def _el_texto_del_album(cur, workspace_id: str, m) -> str:
    """Cómo está el texto de la respuesta de un álbum: las filas sin adjuntos de su mismo
    `respuesta_grupo`. `sale`, si ya salieron todas (o no hay ninguna); `espera`, si alguna
    todavía no salió; `no_sale`, si alguna ya no va a salir."""
    if not m["respuesta_grupo"]:
        return "sale"
    cur.execute(
        """select o.estado::text estado from message_outbox o
            where o.workspace_id = %s and o.respuesta_grupo = %s and o.id <> %s
              and not exists (select 1 from message_outbox_adjunto a
                               where a.outbox_id = o.id)""",
        (workspace_id, m["respuesta_grupo"], m["id"]))
    estados = {f["estado"] for f in cur.fetchall()}
    if estados & {"fallido", "descartado"}:
        return "no_sale"
    return "espera" if estados - {"enviado"} else "sale"


def _adjuntos(cur, m) -> list[Adjunto]:
    """Las fotos de una fila con adjuntos, en su orden, cada una con el identificador que
    Telegram le dio al recibirla como foto en este espacio (del mismo bot), si lo hay. El
    contenido se lee sólo si el transporte tiene que subir la copia propia."""
    cur.execute(
        """select a.id, a.nombre_original, a.tipo,
                  (select d.telegram_file_id from archivo_de_mensaje d
                    where d.workspace_id = a.workspace_id and d.archivo_id = a.id
                      and d.que_llego = 'foto'
                    order by d.at desc limit 1) as file_id
             from message_outbox_adjunto x
             join archivo a on a.workspace_id = x.workspace_id and a.id = x.archivo_id
            where x.outbox_id = %s
            order by x.orden""", (m["id"],))

    def leer(archivo_id):
        def contenido() -> bytes:
            cur.execute("select contenido from archivo where id = %s", (archivo_id,))
            return bytes(cur.fetchone()["contenido"])
        return contenido

    return [Adjunto(f["nombre_original"], f["tipo"], f["file_id"], leer(f["id"]))
            for f in cur.fetchall()]


ETAPA_ENLACE_DE_TAREA = "enlace_de_tarea"


def _enlace_de_la_tarea(cur, workspace_id: str, m) -> str | None:
    """El enlace a la página de la tarea que lleva la fila (`message_outbox_enlace`), emitido
    ahora para esa persona (ADR 0019, decisiones 6 y 7a): la base guarda sólo su hash, y como se
    emite dentro del punto de retorno del envío, un envío que falla no deja ningún acceso. Sin la
    dirección pública configurada, ninguno: nunca se inventa una dirección (constitución §4).
    Si la persona ya no puede ver la tarea, el mensaje sale sin enlace y queda un incidente, sin
    avisar a la administración: el mensaje salió."""
    if not m.get("enlace_tarea"):
        return None
    from . import pagina_de_tarea
    from .config import config

    if not config.base_url:
        return None
    token = pagina_de_tarea.emitir(cur, m["enlace_persona"], m["enlace_tarea"])
    if token is None:
        registrar_incidente(
            cur, workspace_id,
            "Un mensaje salió sin el enlace a la página de su tarea: la persona ya no la ve.",
            severidad="baja", etapa=ETAPA_ENLACE_DE_TAREA, referencia_tipo="message_outbox",
            referencia_id=str(m["id"]), avisar_admin=False,
            sin_avisar_porque="el mensaje salió igual; sólo le falta el enlace")
        return None
    return pagina_de_tarea.enlace(config.base_url, token)


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
            if m.get("adjuntos"):
                # Un álbum sale sin texto, sin botones y sin el saludo del día: el saludo, si
                # toca, ya lo llevó el texto de su respuesta, que salió antes.
                tg_id = transporte.enviar_album(m["chat_id"], _adjuntos(cur, m))
                try:
                    with cur.connection.transaction():
                        _guardar_id_telegram(cur, tg_id, m["id"])
                except Exception as exc_id:  # noqa: BLE001 -- se aísla, no deshace la marca
                    print(f"  ! no se pudo guardar el id de Telegram del mensaje "
                          f"{m['id']} ({type(exc_id).__name__}).")
                return True
            botones = _botones(cur, m)
            # El enlace a la página de la tarea, si la fila lo lleva: al final del texto, nunca
            # en la salida ni en el registro de turnos (ADR 0019, decisión 6).
            enlace = _enlace_de_la_tarea(cur, workspace_id, m)
            cuerpo = f"{m['cuerpo']}\n{enlace}" if enlace else m["cuerpo"]
            texto, falla_saludo = saludo.reclamar_y_anteponer(
                cur, workspace_id=workspace_id,
                membership_id=m["destinatario_membership_id"], zona=cal.zona,
                ahora=ahora, texto=cuerpo, has_buttons=bool(botones),
                es_bienvenida=m["es_bienvenida"])
            if m["bloque_copiable"]:
                tg_id = transporte.enviar(m["chat_id"], texto, botones,
                                          bloque=m["bloque_copiable"])
            elif enlace:
                tg_id = transporte.enviar(m["chat_id"], texto, botones,
                                          sin_vista_previa=True)
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
    proximo = cal.dentro_de_jornada(ahora) if estado == "listo" else None
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
    else:
        _rastro_del_intento(cur, workspace_id, m, intentos,
                            f"{type(error).__name__}: {ultimo_error}")


def _rastro_del_intento(cur, workspace_id: str, m, intentos: int, falla: str) -> None:
    """Un intento fallido que se reintenta deja su rastro (D8, G4; nunca en silencio): un
    incidente de severidad baja, sin avisar a la administración (un reintento no es para
    molestarla; el quinto fallo la avisa con el suyo), con la falla ya saneada en la referencia
    técnica y la fila de la salida como referencia, el mismo criterio que los avisos que la IA no
    redactó (`motor.avisos`). Una falla esperando la respuesta de Telegram puede querer decir que
    el mensaje llegó: no hay cómo saberlo (la API no tiene una clave para no repetir un envío), y
    la explicación de la etapa lo dice. En su propio punto de retorno: si no se puede escribir, no
    deshace el resto de la pasada (los mensajes ya marcados como enviados)."""
    que = "una respuesta" if m.get("es_respuesta") else "un mensaje"
    try:
        with cur.connection.transaction():
            registrar_incidente(
                cur, workspace_id,
                f"No se pudo entregar {que} por Telegram en el intento {intentos} de "
                f"{MAX_INTENTOS}: se reintenta en el despacho siguiente.",
                severidad="baja", referencia_cruda=falla, etapa=ETAPA_ENTREGA_REINTENTO,
                referencia_tipo="message_outbox", referencia_id=str(m["id"]),
                chat_id=m.get("chat_id"), avisar_admin=False,
                sin_avisar_porque="un intento que se reintenta queda sólo como rastro; el "
                                  "quinto fallo sí la avisa.")
    except Exception as e:  # noqa: BLE001 -- el rastro no puede tirar la pasada
        print(f"  ! no se pudo registrar el rastro del envío {m['id']} ({type(e).__name__}).")


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
