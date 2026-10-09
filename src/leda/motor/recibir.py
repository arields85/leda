"""Lo que el motor hace con un update de Telegram (E3-7; diseño probado en la Etapa 2, E2-3b).

Es el mismo camino por long polling (`escucha.py`, el escuchador) y por webhook (la ruta
`POST /telegram/{slug}` de `leda.entrada`): una sola copia, para que pasar de una máquina a un
servidor no cambie el comportamiento. Portado de `prueba_chica/escuchar.py`, borrada el
2026-10-07.

- **Un mensaje escrito** en un chat privado, de alguien del equipo (`identificar_en_espacio`),
  se guarda en `inbound_message` con el bot que lo recibió y `on conflict do nothing`: un
  mensaje repetido no se guarda dos veces, y el turno (`procesar_turno`) no corre dos veces
  sobre el mismo mensaje. Si un mensaje quedó guardado sin turno (el proceso se cortó en el
  medio), al volver a llegar se atiende.
- **Un toque** recibe primero su señal (`senal`, el acuse que Telegram espera) y después, si es
  de una opción del motor y de alguien del equipo, el mismo turno que la elección escrita.
- **Activación:** `/start <enlace>` canjea el enlace de `python -m leda enlaces` y `/start`
  solo saluda a quien ya está vinculado (`leda.onboarding`).
- **El bot de administración** (`registrar_admin`): un administrador de plataforma que le
  escribe deja registrado su chat para los avisos de incidentes.

- **Un archivo** (ADR 0019, decisión 4): una foto (la de mayor resolución), un documento o un
  video, con o sin texto, de alguien del equipo. El adaptador lo baja antes del turno
  (`bajar`), comprueba tamaño y tipo (`archivos.revisar`), lo guarda en `archivo` y lo ata al
  mensaje entrante (`archivos.anotar`). El tamaño máximo es el del espacio o, si es menor, el
  del canal: la API de bots de Telegram deja bajar hasta 20 MB (`LIMITE_DE_TELEGRAM`), un
  límite del adaptador y no del negocio. Lo que no se puede recibir (demasiado grande, que ni
  se baja si Telegram ya dice su tamaño, o de un tipo fuera de la lista) queda anotado con su
  motivo, y el turno corre igual: la IA lo cuenta con lo que la persona puede hacer en cambio.
  Si la descarga falla, es una falla al recibir el update, como cualquier otra (abajo). Un
  archivo que vuelve a llegar no se vuelve a bajar.
- **Un álbum es un solo mensaje** (decisión 4; ADR 0013, una respuesta por mensaje). Telegram
  manda cada foto de un álbum como un update aparte, con el mismo grupo: la primera crea el
  mensaje entrante y las demás se atan a él (y su texto, si lo traen, se le suma). El turno no
  corre al recibirlas: corre una vez, en `atender_albumes`, cuando pasaron `ESPERA_ALBUM_S`
  segundos (la hora de la base) desde la última foto del álbum. El escuchador la llama en cada
  vuelta y, mientras hay un álbum en espera, pide los updates con esa espera; el webhook, al
  terminar la espera, fuera del candado que atiende los updates. Una foto que llega cuando el
  álbum ya tiene su turno empieza un mensaje nuevo: nunca se pierde.

Lo que no es un mensaje de alguien del equipo (un grupo, un mensaje editado, un sticker, una nota
de voz, un desconocido) no se atiende.

**El indicador de actividad** (ADR 0011, decisión 2; pedido del usuario, 2026-10-07): mientras
corre el turno de alguien del equipo (un mensaje o un toque), `indicador` muestra el
"escribiendo…", los tres puntos del borrador y, cuando la IA redacta, el texto que va
escribiendo (`despachador.mantener_chat_activo`). Se apaga al terminar el turno, salga lo que
salga, y nunca demora la respuesta ("La función del escribiendo y el '…' es mostrar que Leda está
activa, no generar demora en la respuesta"): cuando el turno dejó un mensaje confirmado en el
outbox, se le avisa (`sigue_la_respuesta`) y el cierre no retira nada antes del mensaje; sólo
espera a que vuelva el envío del borrador que estaba en vuelo, para que ninguno llegue después
del mensaje, y el borrador se retira después de despacharlo, salga o no (`despachar_ahora`; D8,
prueba por Telegram del 2026-10-08: los tres puntos quedaban a la vista). Un turno sin mensaje
lo retira al cerrar. Lo que Leda manda
por su cuenta (avisos, escalera) no pasa por acá y nunca lo muestra. Una falla del indicador no
cambia el turno.

**La respuesta sale enseguida** (ADR 0011, decisión 1), por el escuchador y por el webhook: con
`transporte`, apenas se recibió un update se despacha el outbox (`despachar_ahora`), el mismo
despacho idempotente del ciclo. Lo que no salga ahí sale en el despacho siguiente. En la consola
queda cuánto tardó la respuesta desde que su texto estuvo listo hasta que Telegram la aceptó.

Si un turno se cae por algo que no es la IA, queda un incidente y la persona recibe el texto fijo
de la falla (nunca en silencio). Si falla recibir un update (guardarlo, activar, atender un
toque), quien llama deshace lo suyo y lo reintenta; a los `INTENTOS_POR_UPDATE` lo deja, con un
incidente y el texto fijo a quien escribió o tocó (`recibir_update`).

**Nunca en silencio** (con el barrido de `leda.huerfanos`, que corre en el ciclo): el mensaje se
guarda con la hora de la base, que es con la que el barrido mide la ventana del turno en curso
(el reloj de Leda puede estar adelantado días). El texto fijo de un turno caído queda atado al
mensaje: es su respuesta, y el barrido no manda otro aviso. El turno toma el mismo candado por
mensaje que el barrido (`entrada.clave_de_candado_del_mensaje`) y no corre si el mensaje ya tiene
respuesta (`entrada.sql_respondido`; por ejemplo, el aviso neutro del barrido): el aviso y una
respuesta tardía nunca salen los dos.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from datetime import timedelta
from typing import Any

from ..autoridad import Canal, Denegado, identificar, identificar_en_espacio
from ..calendario import Calendario
from ..db import admin, atar_al_entrante, espacio, registrar_auditoria
from ..despachador import (Transporte, despachar, registrar_falla_del_retiro,
                           texto_error_seguro)
from ..entrada import VENTANA_TURNO_EN_CURSO, clave_de_candado_del_mensaje, sql_respondido
from ..incidentes import (ETAPA_TURNO_CONVERSACION, REFERENCIA_INBOUND_MESSAGE,
                          registrar_incidente)
from ..onboarding import ActivacionInvalida, activar, bienvenida
from ..salida import enqueue_outbox

from . import archivos
from .botones import ConOpciones
from .ia import IA
from .preguntas import token_de
from .tiempo import Reloj
from .turno import TEXTO_SI_LA_IA_FALLA, procesar_toque, procesar_turno

INTENTOS_POR_UPDATE = 3     # un update que falla al recibirse se reintenta; después, se deja

# Lo que deja bajar la API de bots de Telegram (core.telegram.org/bots/api, objeto `File`),
# mientras no haya un servidor propio de esa API (ADR 0019, decisión 2).
LIMITE_DE_TELEGRAM = 20 * archivos.MB

# Cuánto se espera, desde la última foto de un álbum, antes de atenderlo como un solo mensaje
# (ADR 0019, decisión 4, "el valor de la espera se fija en el plan"). Telegram manda las fotos
# de un álbum casi juntas, en menos de un segundo; dos segundos las juntan y la respuesta no se
# demora de más.
ESPERA_ALBUM_S = 2

# El indicador de un turno: con el chat, un contexto que lo muestra mientras dura y da algo con
# `actualizar_borrador` y `admite_borrador` (`despachador.IndicadorDeActividad`), o `None`.
AbrirIndicador = Callable[[int], AbstractContextManager[Any]]

# La descarga de un archivo del canal: con su identificador y el tamaño máximo, el contenido.
# Si pasa del máximo, `archivos.Rechazo(DEMASIADO_GRANDE)`; cualquier otra falla es una falla al
# recibir el update.
Bajar = Callable[[str, int], bytes]


def bot_id_del_token(token: str) -> int:
    """El id del bot, que es la parte de su token antes de los dos puntos (así los arma
    Telegram). Lo usa el webhook, que no le pregunta a Telegram quién es (`getMe`)."""
    prefijo = token.split(":", 1)[0]
    if not prefijo.isdigit():
        raise LookupError("El token del bot no tiene la forma de Telegram.")
    return int(prefijo)


class IANoConfigurada:
    """La IA de un espacio que no tiene una configurada (`ia_real.desde_base` no la encontró):
    no responde nunca. El turno sigue su camino de siempre cuando la IA no responde (ADR 0018,
    decisión 8): nada se ejecuta, la persona recibe el texto fijo y queda un incidente con el
    motivo. Así un servidor mal configurado nunca deja a nadie sin respuesta."""

    nombre = "sin_configurar"

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo

    def elegir_jugadas(self, situacion: dict[str, Any]) -> list:
        raise LookupError(self.motivo)

    def redactar(self, pedido: dict[str, Any], al_avanzar=None) -> str:
        raise LookupError(self.motivo)


class IntentosPorUpdate:
    """Las veces que falló recibir cada update. Las primeras veces se reintenta; a los
    `INTENTOS_POR_UPDATE`, se deja."""

    def __init__(self, intentos: int = INTENTOS_POR_UPDATE) -> None:
        self.intentos = intentos
        self.fallas: dict[int, int] = {}

    def fallo(self, update_id: int) -> int:
        """Anota una falla y devuelve cuántas van."""
        self.fallas[update_id] = self.fallas.get(update_id, 0) + 1
        return self.fallas[update_id]

    def agotado(self, update_id: int) -> bool:
        return self.fallas.get(update_id, 0) >= self.intentos

    def olvidar(self, update_id: int) -> None:
        self.fallas.pop(update_id, None)


class IndicadorDelTurno:
    """Lo que el turno usa del indicador abierto: con qué mostrar la redacción en vivo
    (`al_avanzar`, o `None` si no hay borrador) y el aviso de que le sigue un mensaje
    (`sigue_la_respuesta`). Sin indicador, o con uno que no sabe de avisos, no hace nada."""

    def __init__(self, abierto: Any = None) -> None:
        self._abierto = abierto
        self.al_avanzar: Callable[[str], None] | None = (
            getattr(abierto, "actualizar_borrador", None)
            if getattr(abierto, "admite_borrador", False) else None)

    def sigue_la_respuesta(self) -> None:
        avisar = getattr(self._abierto, "sigue_la_respuesta", None)
        if avisar is not None:
            avisar()

    def tras_la_respuesta(self) -> Exception | None:
        """Ya salió la respuesta (o falló al salir): el borrador se retira, si se mostró
        (`despachador.IndicadorDeActividad.retirar_tras_la_respuesta`). La falla del retiro, o
        `None`; uno que no sabe de retiros no hace nada."""
        retirar = getattr(self._abierto, "retirar_tras_la_respuesta", None)
        return retirar() if retirar is not None else None


class _ConHoraDeEnvio:
    """El transporte del despacho inmediato, que anota cuándo Telegram aceptó el último
    mensaje de cada chat (`time.monotonic`): es el final de la línea de la consola.

    Es el mismo transporte: todo lo que sabe hacer pasa tal cual (`__getattr__`), y lo que
    manda algo a un chat (un mensaje o un álbum) anota además su hora. Sin la delegación, cada
    álbum de una respuesta fallaba en el despacho inmediato y salía una vuelta más tarde (prueba
    por Telegram del 2026-10-08, D8)."""

    def __init__(self, transporte: Transporte) -> None:
        self.transporte = transporte
        self.enviado_en: dict[int, float] = {}

    def enviar(self, chat_id: int, texto: str, botones=None, **mas: Any) -> int:
        tg_id = self.transporte.enviar(chat_id, texto, botones, **mas)
        self.enviado_en[chat_id] = time.monotonic()
        return tg_id

    def enviar_album(self, chat_id: int, adjuntos, **mas: Any) -> int:
        tg_id = self.transporte.enviar_album(chat_id, adjuntos, **mas)
        self.enviado_en[chat_id] = time.monotonic()
        return tg_id

    def __getattr__(self, nombre: str) -> Any:
        # Sólo lo que no está definido acá: el resto del transporte, tal cual.
        return getattr(self.transporte, nombre)


class Recepcion:
    """Lo que se hace con un update del bot de un espacio, con la conexión, la IA y el reloj de
    quien recibe. `bot_id` es el del bot que lo recibió; `senal`, el acuse de un toque;
    `transporte`, por dónde sale enseguida la respuesta (`despachar_ahora`); `bajar`, cómo se
    baja un archivo del canal (sin ella, un archivo es una falla al recibir el update)."""

    def __init__(self, conn, workspace_id: str, ia: IA, reloj: Reloj, *,
                 bot_id: int | None = None, senal: Callable[[str], Any] | None = None,
                 imprimir: Callable[[str], None] = print,
                 indicador: AbrirIndicador | None = None,
                 transporte: Transporte | None = None, bajar: Bajar | None = None) -> None:
        self.conn = conn
        self.ws = workspace_id
        self.ia = ia
        self.reloj = reloj
        self.bot_id = bot_id
        self.senal = senal
        self.imprimir = imprimir
        self.indicador = indicador
        self.transporte = transporte
        self.bajar = bajar
        # Si quedó un álbum esperando su turno (`atender_albumes`): el escuchador espera poco.
        self.albumes_en_espera = False
        # El chat y la hora (`time.monotonic`) en que estuvo listo el texto de la respuesta del
        # último turno, hasta que `despachar_ahora` la mide.
        self._listo: tuple[int, float] | None = None
        # Los indicadores de los turnos cuya respuesta sigue: su borrador se retira después de
        # despacharla (`despachar_ahora`, D8).
        self._por_retirar: list[IndicadorDelTurno] = []

    def procesar(self, u: dict[str, Any]) -> None:
        if u.get("callback_query"):
            self._toque(u["callback_query"])
            return
        mensaje = u.get("message")
        if not mensaje or (mensaje.get("chat") or {}).get("type") != "private":
            return
        llegada = _llegada(mensaje)
        texto = (mensaje.get("text") or mensaje.get("caption") or "").strip()
        if not texto and llegada is None:
            return
        tg_user = mensaje["from"]["id"]
        chat_id = mensaje["chat"]["id"]
        if llegada is None and texto.startswith("/start"):
            self._activar(texto, tg_user, chat_id, mensaje["message_id"])
            self.conn.commit()
            return

        if llegada is None:
            guardado = self._guardar(mensaje, tg_user, chat_id, texto)
        else:
            guardado = self._guardar_con_archivo(mensaje, tg_user, chat_id, texto, llegada)
        if guardado is None:
            return
        quien, entrante, message_id = guardado
        if llegada is not None and llegada.media_group_id is not None:
            # Un álbum: su turno corre una vez, después de la espera (`atender_albumes`).
            self.albumes_en_espera = True
            self.imprimir(f"  ← {quien.nombre}: {_que_llego(llegada)} de un álbum")
            return
        resumen = texto[:70] if llegada is None else f"{_que_llego(llegada)} {texto[:50]}"
        self._atender(quien, chat_id, entrante, message_id, resumen)

    def _atender(self, quien, chat_id: int, entrante: str, message_id: int,
                 resumen: str) -> None:
        """El turno de un mensaje guardado, con el indicador mientras dura. Si se cae, un
        incidente y el texto fijo (`_turno_caido`)."""
        self.imprimir(f"  ← {quien.nombre}: {resumen}")
        with self._indicador_del_turno(chat_id) as indicador:
            try:
                # El candado por mensaje se suelta con el commit, al terminar el turno.
                with self.conn.transaction():
                    if self._ya_respondido(entrante, chat_id, message_id):
                        self.imprimir("  (ese mensaje ya tiene respuesta: no se vuelve a "
                                      "atender)")
                        return
                    resultado = procesar_turno(self.conn, quien, entrante, self.ia, self.reloj,
                                               al_avanzar=indicador.al_avanzar,
                                               limite_del_canal=LIMITE_DE_TELEGRAM)
            except Exception as e:  # noqa: BLE001 -- nunca en silencio: incidente y texto fijo
                self.conn.rollback()
                self._turno_caido(quien, chat_id, e, entrante=entrante,
                                  clave=f"motor:respuesta:{entrante}", indicador=indicador)
                return
            if not resultado.repetido:
                # La respuesta ya está confirmada en el outbox: el indicador se apaga sin
                # demorarla.
                self._sigue_la_respuesta(indicador, chat_id, resultado.listo_en)
        if not resultado.repetido:
            self.imprimir(f"  → {resultado.texto[:70]}")

    def atender_albumes(self) -> int:
        """Atiende, como un solo mensaje cada uno, los álbumes cuya última foto llegó hace
        `ESPERA_ALBUM_S` segundos o más (la hora de la base) y que todavía no tienen turno ni
        respuesta. Devuelve cuántos siguen en la espera. Los de más de
        `entrada.VENTANA_TURNO_EN_CURSO` quedan para el barrido de huérfanos. Si falla la
        lectura, queda en la consola y se vuelve a mirar en la vuelta siguiente."""
        try:
            with espacio(self.conn, self.ws) as cur:
                cur.execute(
                    f"""select i.id, i.chat_id, i.telegram_message_id, g.telegram_user_id,
                               max(m.at) <= clock_timestamp() - %s as lista
                          from inbound_message i
                          join archivo_de_mensaje m on m.inbound_message_id = i.id
                          join integrante g on g.app_user_id = i.app_user_id
                         where m.telegram_media_group_id is not null
                           and i.telegram_bot_id is not distinct from %s
                           and i.at > clock_timestamp() - %s
                           and not {sql_respondido('i')}
                           and not exists (select 1 from conversation_turn t
                                            where t.inbound_message_id = i.id
                                              and t.sentido = 'entrada')
                         group by i.id, i.chat_id, i.telegram_message_id, g.telegram_user_id
                         order by min(m.at)""",
                    (timedelta(seconds=ESPERA_ALBUM_S), self.bot_id, VENTANA_TURNO_EN_CURSO))
                albumes = cur.fetchall()
            self.conn.commit()
        except Exception as e:  # noqa: BLE001 -- se vuelve a mirar en la vuelta siguiente
            self.conn.rollback()
            self.imprimir(f"  ! no se pudieron mirar los álbumes en espera: "
                          f"{texto_error_seguro(e)}")
            self.albumes_en_espera = True
            return 1
        en_espera = sum(1 for a in albumes if not a["lista"])
        for album in albumes:
            if not album["lista"]:
                continue
            with espacio(self.conn, self.ws) as cur:
                try:
                    quien = identificar_en_espacio(cur, album["telegram_user_id"], self.ws)
                except Denegado:
                    quien = None        # dejó el equipo en la espera: no se le responde
            self.conn.commit()
            if quien is not None:
                self._atender(quien, album["chat_id"], str(album["id"]),
                              album["telegram_message_id"], "un álbum")
        self.albumes_en_espera = en_espera > 0
        return en_espera

    def _sigue_la_respuesta(self, indicador: IndicadorDelTurno, chat_id: int,
                            listo_en: float | None) -> None:
        """Al turno le sigue un mensaje, ya confirmado en el outbox: el indicador se apaga sin
        esperar ni retirar nada, y `despachar_ahora` mide desde `listo_en`."""
        self._listo = (chat_id, listo_en if listo_en is not None else time.monotonic())
        try:
            indicador.sigue_la_respuesta()
        except Exception as e:  # noqa: BLE001 -- cosmético: el turno ya terminó
            self.imprimir(f"  ! el indicador de actividad no recibió el aviso: "
                          f"{texto_error_seguro(e)}")
        self._por_retirar.append(indicador)

    @contextmanager
    def _indicador_del_turno(self, chat_id: int) -> Iterator[IndicadorDelTurno]:
        """El indicador mientras dura el turno (`IndicadorDelTurno`). Una falla al abrirlo o al
        cerrarlo queda en la consola y el turno sigue igual: es cosmético (constitución §10).
        Lo que falle adentro del turno sale tal cual, después de apagar el indicador."""
        if self.indicador is None:
            yield IndicadorDelTurno()
            return
        try:
            contexto = self.indicador(chat_id)
            abierto = contexto.__enter__()
        except Exception as e:  # noqa: BLE001 -- sin indicador, el turno igual
            self.imprimir(f"  ! el indicador de actividad no arrancó: {texto_error_seguro(e)}")
            yield IndicadorDelTurno()
            return
        try:
            yield IndicadorDelTurno(abierto)
        except BaseException as e:
            self._apagar(contexto, e)
            raise
        else:
            self._apagar(contexto, None)

    def _apagar(self, contexto: AbstractContextManager[Any],
                error: BaseException | None) -> None:
        try:
            if error is None:
                contexto.__exit__(None, None, None)
            else:
                contexto.__exit__(type(error), error, error.__traceback__)
        except Exception as e:  # noqa: BLE001 -- el turno ya terminó; queda en la consola
            self.imprimir(f"  ! el indicador de actividad no se apagó: {texto_error_seguro(e)}")

    def _ya_respondido(self, entrante: str, chat_id: int, message_id: int) -> bool:
        """Toma el candado del mensaje (el mismo del barrido de huérfanos; espera si el
        barrido lo tiene) y dice si el mensaje ya tiene una respuesta, en cualquier estado."""
        with espacio(self.conn, self.ws) as cur:
            cur.execute("select pg_advisory_xact_lock(hashtextextended(%s, 0))",
                        (clave_de_candado_del_mensaje(self.ws, chat_id, message_id),))
            cur.execute(f"select {sql_respondido('i')} as respondido "
                        f"from inbound_message i where i.id = %s", (entrante,))
            return bool(cur.fetchone()["respondido"])

    def _toque(self, toque: dict[str, Any]) -> None:
        """Un botón tocado: primero la señal (el acuse que Telegram espera; si falla, no se
        pierde nada) y después, si es de una opción del motor y de alguien del equipo, el mismo
        turno que la elección escrita (`procesar_toque`). Un toque repetido de la misma opción
        sólo recibe la señal (ADR 0013, regla 4)."""
        if self.senal is not None:
            try:
                self.senal(toque["id"])
            except Exception as e:  # noqa: BLE001 -- un acuse: si falla, el toque se atiende igual
                self.imprimir(f"  (no se pudo dar la señal del toque: {texto_error_seguro(e)})")
        token = token_de(str(toque.get("data") or ""))
        chat = (toque.get("message") or {}).get("chat") or {}
        tg_user = (toque.get("from") or {}).get("id")
        if token is None or chat.get("type") != "private" or tg_user is None:
            return
        with espacio(self.conn, self.ws) as cur:
            try:
                quien = identificar_en_espacio(cur, tg_user, self.ws)
            except Denegado:
                quien = None
        self.conn.commit()
        if quien is None:
            self.imprimir("  (un toque de alguien que no es del equipo: no se atiende)")
            return
        self.imprimir(f"  ← {quien.nombre} tocó una opción")
        with self._indicador_del_turno(chat["id"]) as indicador:
            try:
                resultado = procesar_toque(self.conn, quien, token, chat["id"], self.ia,
                                           self.reloj, al_avanzar=indicador.al_avanzar)
                self.conn.commit()
            except Exception as e:  # noqa: BLE001 -- nunca en silencio: incidente y texto fijo
                self.conn.rollback()
                self._turno_caido(quien, chat["id"], e,
                                  clave=f"motor:toque_caido:{toque['id']}",
                                  indicador=indicador)
                return
            if resultado is not None and not resultado.repetido:
                self._sigue_la_respuesta(indicador, chat["id"], resultado.listo_en)
        if resultado is not None and not resultado.repetido:
            self.imprimir(f"  → {resultado.texto[:70]}")

    def _guardar(self, mensaje, tg_user: int, chat_id: int, texto: str):
        """(quien, id del mensaje guardado, su número en Telegram), o `None` si no es de alguien
        del equipo. Un mensaje repetido devuelve el que ya estaba: el turno decide si falta
        atenderlo."""
        with espacio(self.conn, self.ws) as cur:
            try:
                quien = identificar_en_espacio(cur, tg_user, self.ws)
            except Denegado:
                self.imprimir("  (un mensaje de alguien que no es del equipo: no se atiende)")
                return None
            entrante = self._insertar_entrante(cur, quien, mensaje["message_id"], chat_id,
                                               texto)
        self.conn.commit()
        return quien, entrante, mensaje["message_id"]

    def _insertar_entrante(self, cur, quien, message_id: int, chat_id: int, texto: str) -> str:
        """El mensaje entrante, o el que ya estaba si Telegram lo vuelve a entregar."""
        # `at` es la hora de la base (el valor por omisión), no la del reloj de Leda: con
        # ella mide el barrido de huérfanos.
        cur.execute(
            """insert into inbound_message (workspace_id, telegram_bot_id,
                                            telegram_message_id, chat_id, app_user_id,
                                            texto)
               values (%s, %s, %s, %s, %s, %s)
               on conflict (workspace_id, telegram_bot_id, chat_id, telegram_message_id)
                  where telegram_bot_id is not null and telegram_message_id is not null
                  do nothing
               returning id""",
            (self.ws, self.bot_id, message_id, chat_id, quien.app_user_id, texto))
        fila = cur.fetchone()
        if fila is None:
            cur.execute("""select id from inbound_message
                            where workspace_id = %s and telegram_bot_id = %s
                              and chat_id = %s and telegram_message_id = %s""",
                        (self.ws, self.bot_id, chat_id, message_id))
            fila = cur.fetchone()
        return str(fila["id"])

    def _guardar_con_archivo(self, mensaje, tg_user: int, chat_id: int, texto: str,
                             llegada: archivos.Llegada):
        """Como `_guardar`, para un mensaje que trae un archivo: lo baja (fuera de toda
        transacción), lo revisa y, en una sola transacción, guarda el mensaje (o lo ata al de
        su álbum), el archivo y lo que trajo el mensaje. A alguien que no es del equipo no se
        le baja nada; un archivo que ya está atado no se vuelve a bajar. (quien, id del
        mensaje, su número en Telegram), o `None`."""
        with espacio(self.conn, self.ws) as cur:
            try:
                quien = identificar_en_espacio(cur, tg_user, self.ws)
            except Denegado:
                self.imprimir("  (un archivo de alguien que no es del equipo: no se atiende)")
                return None
            ya_estaba = self._entrante_con(cur, chat_id, llegada.message_id)
            limite = min(archivos.limite(cur, self.ws), LIMITE_DE_TELEGRAM)
        self.conn.commit()
        if ya_estaba is not None:
            return quien, ya_estaba[0], ya_estaba[1]

        contenido, tipo, rechazo = None, None, None
        if llegada.tamano_declarado is not None and llegada.tamano_declarado > limite:
            rechazo = archivos.DEMASIADO_GRANDE
        else:
            if self.bajar is None:
                raise RuntimeError("La entrada no tiene cómo bajar archivos del canal.")
            try:
                contenido = self.bajar(llegada.file_id, limite)
                tipo = archivos.revisar(contenido, llegada.nombre, limite)
            except archivos.Rechazo as r:
                rechazo = r.motivo

        with espacio(self.conn, self.ws) as cur:
            entrante, message_id = self._entrante_del_mensaje(cur, quien, chat_id, texto,
                                                              llegada)
            archivo_id = None
            if rechazo is None:
                archivo_id = archivos.guardar(
                    cur, workspace_id=self.ws, contenido=contenido, tipo=tipo,
                    nombre=llegada.nombre, enviado_por=quien.membership_id,
                    ahora=self.reloj.ahora())
            archivos.anotar(cur, workspace_id=self.ws, entrante_id=entrante, llegada=llegada,
                            archivo_id=archivo_id, rechazo=rechazo)
        self.conn.commit()
        return quien, entrante, message_id

    def _entrante_con(self, cur, chat_id: int, message_id: int) -> tuple[str, int] | None:
        """El mensaje entrante (y su número en Telegram) al que ya se ató el archivo de ese
        mensaje de Telegram, si Telegram lo vuelve a entregar."""
        cur.execute("""select i.id, i.telegram_message_id
                         from archivo_de_mensaje m
                         join inbound_message i on i.id = m.inbound_message_id
                        where i.telegram_bot_id is not distinct from %s and i.chat_id = %s
                          and m.telegram_message_id = %s
                        limit 1""", (self.bot_id, chat_id, message_id))
        fila = cur.fetchone()
        return (str(fila["id"]), fila["telegram_message_id"]) if fila else None

    def _entrante_del_mensaje(self, cur, quien, chat_id: int, texto: str,
                              llegada: archivos.Llegada) -> tuple[str, int]:
        """El mensaje entrante de un archivo: el de su álbum, si el álbum todavía espera su
        turno (y su texto, si trae, se le suma), o uno nuevo. Las fotos de un mismo álbum se
        atan de a una (un candado por álbum)."""
        if llegada.media_group_id is not None:
            cur.execute("select pg_advisory_xact_lock(hashtextextended(%s, 0))",
                        (f"album:{self.ws}:{self.bot_id}:{chat_id}:{llegada.media_group_id}",))
            cur.execute(
                f"""select i.id, i.telegram_message_id
                      from archivo_de_mensaje m
                      join inbound_message i on i.id = m.inbound_message_id
                     where m.telegram_media_group_id = %s and i.chat_id = %s
                       and i.telegram_bot_id is not distinct from %s
                       and not {sql_respondido('i')}
                       and not exists (select 1 from conversation_turn t
                                        where t.inbound_message_id = i.id
                                          and t.sentido = 'entrada')
                     limit 1""", (llegada.media_group_id, chat_id, self.bot_id))
            fila = cur.fetchone()
            if fila is not None:
                if texto:
                    cur.execute("""update inbound_message
                                      set texto = case when coalesce(texto, '') = '' then %s
                                                       else texto || E'\\n' || %s end
                                    where id = %s""", (texto, texto, fila["id"]))
                return str(fila["id"]), fila["telegram_message_id"]
        return (self._insertar_entrante(cur, quien, llegada.message_id, chat_id, texto),
                llegada.message_id)

    def _turno_caido(self, quien, chat_id: int, error: Exception, *, clave: str,
                     entrante: str | None = None,
                     indicador: IndicadorDelTurno | None = None) -> None:
        """Un turno (de un mensaje o de un toque) que se cayó por algo que no es la IA. El
        texto fijo, ya confirmado en el outbox, reemplaza al borrador como cualquier respuesta:
        se le avisa al indicador (`_sigue_la_respuesta`). Si ni eso se pudo guardar, no sigue
        ningún mensaje y el indicador retira el borrador."""
        listo_en = time.monotonic()
        ahora = self.reloj.ahora()
        try:
            with espacio(self.conn, self.ws) as cur:
                registrar_incidente(
                    cur, self.ws,
                    "Un turno del motor de conversación se cayó por algo que no es la IA: "
                    "la persona recibió el texto fijo de la falla.",
                    severidad="alta", referencia_cruda=texto_error_seguro(error),
                    etapa=ETAPA_TURNO_CONVERSACION,
                    referencia_tipo=REFERENCIA_INBOUND_MESSAGE if entrante else None,
                    referencia_id=entrante, chat_id=chat_id, app_user_id=quien.app_user_id,
                    notificado_en=ahora)
                # El texto fijo es la respuesta de ese mensaje (`entrada.sql_respondido`).
                atar_al_entrante(cur, entrante)
                enqueue_outbox(cur, workspace_id=self.ws, chat_id=chat_id,
                               text=TEXTO_SI_LA_IA_FALLA, dedupe_key=clave,
                               recipient_membership_id=quien.membership_id, is_response=True,
                               scheduled_for=ahora)
            self.conn.commit()
        except Exception as e:  # noqa: BLE001 -- la recepción sigue; queda en la consola
            self.conn.rollback()
            self.imprimir(f"  ! no se pudo registrar la falla: {texto_error_seguro(e)}")
        else:
            if indicador is not None:
                self._sigue_la_respuesta(indicador, chat_id, listo_en)
        self.imprimir(f"  ! el turno se cayó: {type(error).__name__}")

    def despachar_ahora(self) -> None:
        """Lo que quedó en el outbox sale enseguida (ADR 0011, decisión 1): la respuesta del
        update que se acaba de recibir no espera al resto del lote, a la vuelta del escuchador
        ni al despacho de fondo del servidor. Es el mismo despacho del ciclo, idempotente (cada
        fila se toma con `for update skip locked` y se marca antes de enviarse): si falla, se
        deshace y sale en el despacho siguiente, que es el que registra el incidente si la
        caída sigue. Sin `transporte`, no hace nada.

        Si el update dejó una respuesta, imprime cuánto tardó en salir desde que su texto
        estuvo listo; sin datos de la conversación."""
        listo, self._listo = self._listo, None
        try:
            self._despachar_ya(listo)
        finally:
            self._retirar_los_borradores()

    def _despachar_ya(self, listo: tuple[int, float] | None) -> None:
        if self.transporte is None:
            return
        salida = _ConHoraDeEnvio(self.transporte)
        try:
            with espacio(self.conn, self.ws) as cur:
                despachar(cur, self.ws, ConOpciones(salida, cur),
                          Calendario.desde_base(cur, self.ws), self.reloj.ahora())
            self.conn.commit()
        except Exception as e:  # noqa: BLE001 -- lo despacha la vuelta siguiente
            self.conn.rollback()
            self.imprimir(f"  (no se pudo despachar enseguida: {texto_error_seguro(e)}; sale "
                          f"en el despacho siguiente)")
            return
        if listo is not None and listo[0] in salida.enviado_en:
            ms = max(0, round((salida.enviado_en[listo[0]] - listo[1]) * 1000))
            self.imprimir(f"  ⏱ respuesta: texto listo → enviado en {ms} ms")

    def _retirar_los_borradores(self) -> None:
        """Después del despacho, salga o no la respuesta, el borrador de cada turno que la dejó
        se retira, si se mostró (D8: los tres puntos quedaban a la vista cuando el mensaje no
        los reemplazaba, o cuando la respuesta falló al salir). Una falla queda en la consola y
        en un incidente; el despacho no cambia."""
        por_retirar, self._por_retirar = self._por_retirar, []
        for indicador in por_retirar:
            try:
                falla = indicador.tras_la_respuesta()
            except Exception as e:  # noqa: BLE001 -- cosmético, pero nunca en silencio
                falla = e
            if falla is None:
                continue
            self.imprimir(f"  ! el borrador no se pudo retirar: {texto_error_seguro(falla)}")
            try:
                with espacio(self.conn, self.ws) as cur:
                    registrar_falla_del_retiro(cur, self.ws, falla)
                self.conn.commit()
            except Exception as e:  # noqa: BLE001 -- queda en la consola
                self.conn.rollback()
                self.imprimir(f"  ! tampoco se pudo registrar: {texto_error_seguro(e)}")

    def _activar(self, texto: str, tg_user: int, chat_id: int, message_id: int) -> None:
        """El mecanismo de activación de siempre (`leda.onboarding`), con permisos de
        administración: escribe en `app_user`, que es global."""
        partes = texto.split(maxsplit=1)
        with admin(self.conn) as cur:
            membership_id = None
            if len(partes) == 2:
                try:
                    nombre = activar(cur, self.ws, partes[1].strip(), tg_user,
                                     self.reloj.ahora())
                except ActivacionInvalida as e:
                    cuerpo = f"{e} Pedile uno nuevo a quien te lo pasó."
                else:
                    registrar_auditoria(cur, accion="activacion", workspace_id=self.ws,
                                        actor_kind="persona", detalle={"nombre": nombre})
                    cuerpo = bienvenida(cur, self.ws, nombre)
                    membership_id = self._membresia(cur, tg_user)
            else:
                membership_id = self._membresia(cur, tg_user)
                if membership_id is None:
                    return                  # un desconocido sin enlace: no se le responde
                cur.execute("""select u.nombre from membership m
                                 join app_user u on u.id = m.app_user_id
                                where m.id = %s""", (membership_id,))
                cuerpo = bienvenida(cur, self.ws, cur.fetchone()["nombre"])
            enqueue_outbox(cur, workspace_id=self.ws, chat_id=chat_id, text=cuerpo,
                           recipient_membership_id=membership_id, message_type="informativo",
                           dedupe_key=f"motor:alta:{self.bot_id}:{chat_id}:{message_id}",
                           is_response=True, allow_split=True,
                           es_bienvenida=membership_id is not None,
                           scheduled_for=self.reloj.ahora())
        self.imprimir("  ← /start")

    def _membresia(self, cur, tg_user: int) -> str | None:
        cur.execute("""select m.id from membership m join app_user u on u.id = m.app_user_id
                        where m.workspace_id = %s and u.telegram_user_id = %s and m.activo""",
                    (self.ws, tg_user))
        fila = cur.fetchone()
        return str(fila["id"]) if fila else None

    def dejar(self, u: dict[str, Any], error: Exception) -> None:
        """Un update que no se pudo recibir tras los intentos: nunca en silencio, con un
        incidente y, si es de alguien del equipo, el texto fijo de la falla."""
        uid = u["update_id"]
        chat, tg_user = _origen(u)
        chat_id = chat.get("id")
        try:
            with espacio(self.conn, self.ws) as cur:
                quien = None
                if tg_user is not None and chat.get("type") == "private":
                    try:
                        quien = identificar_en_espacio(cur, tg_user, self.ws)
                    except Denegado:
                        quien = None
                registrar_incidente(
                    cur, self.ws,
                    f"La entrada del motor no pudo recibir un update de Telegram tras "
                    f"{INTENTOS_POR_UPDATE} intentos y lo dejó"
                    + (": la persona recibió el texto fijo de la falla." if quien else "."),
                    severidad="alta",
                    referencia_cruda=f"update {uid}: {texto_error_seguro(error)}",
                    etapa=ETAPA_TURNO_CONVERSACION, chat_id=chat_id,
                    app_user_id=quien.app_user_id if quien else None,
                    notificado_en=self.reloj.ahora() if quien else None)
                if quien is not None:
                    enqueue_outbox(cur, workspace_id=self.ws, chat_id=chat_id,
                                   text=TEXTO_SI_LA_IA_FALLA,
                                   dedupe_key=f"motor:sin_recibir:{self.bot_id}:{uid}",
                                   recipient_membership_id=quien.membership_id,
                                   is_response=True, scheduled_for=self.reloj.ahora())
            self.conn.commit()
        except Exception as e:  # noqa: BLE001 -- queda en la consola; la recepción sigue
            self.conn.rollback()
            self.imprimir(f"  ! tampoco se pudo registrar la falla: {texto_error_seguro(e)}")


def recibir_update(recepcion: Recepcion, intentos: IntentosPorUpdate,
                   u: dict[str, Any]) -> bool:
    """Un update, con su falla aislada. `True` si quedó recibido (atendido, descartado o
    dejado tras los intentos) y quien llama puede pasar al siguiente; `False` si falló y hay
    que volver a pedirlo (el escuchador no avanza el offset; el webhook contesta un error y
    Telegram lo reentrega)."""
    uid = u["update_id"]
    try:
        recepcion.procesar(u)
    except Exception as e:  # noqa: BLE001 -- la recepción sigue; el update no se pierde
        recepcion.conn.rollback()
        veces = intentos.fallo(uid)
        recepcion.imprimir(f"  ! no se pudo recibir el update {uid} ({type(e).__name__}), "
                           f"intento {veces} de {intentos.intentos}")
        if not intentos.agotado(uid):
            return False
        recepcion.dejar(u, e)
    intentos.olvidar(uid)
    # La respuesta (o el texto fijo) sale ya, en el escuchador y en el webhook.
    recepcion.despachar_ahora()
    return True


def registrar_admin(conn, u: dict[str, Any], imprimir: Callable[[str], None] = print) -> bool:
    """Un mensaje al bot de administración: si es de un administrador de plataforma, deja su
    chat registrado (auditoría `mensaje_admin`) para los avisos de incidentes. `True` si lo
    registró."""
    mensaje = u.get("message") or {}
    tg_user = (mensaje.get("from") or {}).get("id")
    chat_id = (mensaje.get("chat") or {}).get("id")
    if tg_user is None or chat_id is None:
        return False
    with admin(conn) as cur:
        try:
            quien = identificar(cur, tg_user, Canal.ADMINISTRACION, None)
        except Denegado:
            return False
        registrar_auditoria(cur, accion="mensaje_admin", actor_app_user_id=quien.app_user_id,
                            actor_kind="persona", detalle={"chat_id": chat_id})
    conn.commit()
    imprimir("  ← [admin] chat registrado para los avisos de incidentes")
    return True


def _llegada(mensaje: dict[str, Any]) -> archivos.Llegada | None:
    """El archivo que trae un mensaje de Telegram, o `None`: de una foto, la de mayor
    resolución (Telegram manda varios tamaños de la misma); si no, el video o el documento."""
    message_id, grupo = mensaje["message_id"], mensaje.get("media_group_id")
    if mensaje.get("photo"):
        mayor = max(mensaje["photo"],
                    key=lambda p: ((p.get("width") or 0) * (p.get("height") or 0),
                                   p.get("file_size") or 0))
        return archivos.Llegada(archivos.FOTO, mayor["file_id"], mayor["file_unique_id"], None,
                                mayor.get("file_size"), message_id, grupo)
    for clave, que_llego in (("video", archivos.UN_VIDEO), ("document", archivos.UN_ARCHIVO)):
        dato = mensaje.get(clave)
        if dato:
            return archivos.Llegada(que_llego, dato["file_id"], dato["file_unique_id"],
                                    dato.get("file_name"), dato.get("file_size"), message_id,
                                    grupo)
    return None


def _que_llego(llegada: archivos.Llegada) -> str:
    """Para la consola, sin el nombre del archivo."""
    return {archivos.FOTO: "una foto", archivos.UN_VIDEO: "un video"}.get(
        llegada.que_llego, "un archivo")


def _origen(u: dict[str, Any]) -> tuple[dict[str, Any], int | None]:
    """El chat y quién escribió o tocó, de un mensaje o de un toque: los dos se tratan igual
    cuando no se pueden recibir (revisión de la E2-4)."""
    toque = u.get("callback_query") or {}
    mensaje = u.get("message") or toque.get("message") or {}
    de = (u.get("message") or toque).get("from") or {}
    return mensaje.get("chat") or {}, de.get("id")
