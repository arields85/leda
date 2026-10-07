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

Lo que no es un mensaje escrito de alguien del equipo (un grupo, un mensaje editado, una foto
sin texto, un desconocido) no se atiende.

**El indicador de actividad** (ADR 0011, decisión 2; pedido del usuario, 2026-10-07): mientras
corre el turno de alguien del equipo (un mensaje o un toque), `indicador` muestra el
"escribiendo…", los tres puntos del borrador y, cuando la IA redacta, el texto que va
escribiendo (`despachador.mantener_chat_activo`). Se apaga al terminar el turno, salga lo que
salga, y antes de que se despache la respuesta: el borrador se retira primero. Lo que Leda manda
por su cuenta (avisos, escalera) no pasa por acá y nunca lo muestra. Una falla del indicador no
cambia el turno.

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

from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from typing import Any

from ..autoridad import Canal, Denegado, identificar, identificar_en_espacio
from ..db import admin, atar_al_entrante, espacio, registrar_auditoria
from ..despachador import texto_error_seguro
from ..entrada import clave_de_candado_del_mensaje, sql_respondido
from ..incidentes import (ETAPA_TURNO_CONVERSACION, REFERENCIA_INBOUND_MESSAGE,
                          registrar_incidente)
from ..onboarding import ActivacionInvalida, activar, bienvenida
from ..salida import enqueue_outbox

from .ia import IA
from .preguntas import token_de
from .tiempo import Reloj
from .turno import TEXTO_SI_LA_IA_FALLA, procesar_toque, procesar_turno

INTENTOS_POR_UPDATE = 3     # un update que falla al recibirse se reintenta; después, se deja

# El indicador de un turno: con el chat, un contexto que lo muestra mientras dura y da algo con
# `actualizar_borrador` y `admite_borrador` (`despachador.IndicadorDeActividad`), o `None`.
AbrirIndicador = Callable[[int], AbstractContextManager[Any]]


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


class Recepcion:
    """Lo que se hace con un update del bot de un espacio, con la conexión, la IA y el reloj de
    quien recibe. `bot_id` es el del bot que lo recibió; `senal`, el acuse de un toque."""

    def __init__(self, conn, workspace_id: str, ia: IA, reloj: Reloj, *,
                 bot_id: int | None = None, senal: Callable[[str], Any] | None = None,
                 imprimir: Callable[[str], None] = print,
                 indicador: AbrirIndicador | None = None) -> None:
        self.conn = conn
        self.ws = workspace_id
        self.ia = ia
        self.reloj = reloj
        self.bot_id = bot_id
        self.senal = senal
        self.imprimir = imprimir
        self.indicador = indicador

    def procesar(self, u: dict[str, Any]) -> None:
        if u.get("callback_query"):
            self._toque(u["callback_query"])
            return
        mensaje = u.get("message")
        if not mensaje or (mensaje.get("chat") or {}).get("type") != "private":
            return
        texto = (mensaje.get("text") or "").strip()
        if not texto:
            return
        tg_user = mensaje["from"]["id"]
        chat_id = mensaje["chat"]["id"]
        if texto.startswith("/start"):
            self._activar(texto, tg_user, chat_id, mensaje["message_id"])
            self.conn.commit()
            return

        guardado = self._guardar(mensaje, tg_user, chat_id, texto)
        if guardado is None:
            return
        quien, entrante = guardado
        self.imprimir(f"  ← {quien.nombre}: {texto[:70]}")
        with self._indicador_del_turno(chat_id) as al_avanzar:
            try:
                # El candado por mensaje se suelta con el commit, al terminar el turno.
                with self.conn.transaction():
                    if self._ya_respondido(entrante, chat_id, mensaje["message_id"]):
                        self.imprimir("  (ese mensaje ya tiene respuesta: no se vuelve a "
                                      "atender)")
                        return
                    resultado = procesar_turno(self.conn, quien, entrante, self.ia, self.reloj,
                                               al_avanzar=al_avanzar)
            except Exception as e:  # noqa: BLE001 -- nunca en silencio: incidente y texto fijo
                self.conn.rollback()
                self._turno_caido(quien, chat_id, e, entrante=entrante,
                                  clave=f"motor:respuesta:{entrante}")
                return
        if not resultado.repetido:
            self.imprimir(f"  → {resultado.texto[:70]}")

    @contextmanager
    def _indicador_del_turno(self, chat_id: int) -> Iterator[Callable[[str], None] | None]:
        """El indicador mientras dura el turno; da con qué mostrar la redacción en vivo, o
        `None` si no hay borrador donde mostrarla. Una falla al abrirlo o al cerrarlo queda en
        la consola y el turno sigue igual: es cosmético (constitución §10). Lo que falle adentro
        del turno sale tal cual, después de apagar el indicador."""
        if self.indicador is None:
            yield None
            return
        try:
            contexto = self.indicador(chat_id)
            abierto = contexto.__enter__()
        except Exception as e:  # noqa: BLE001 -- sin indicador, el turno igual
            self.imprimir(f"  ! el indicador de actividad no arrancó: {texto_error_seguro(e)}")
            yield None
            return
        al_avanzar = (getattr(abierto, "actualizar_borrador", None)
                      if getattr(abierto, "admite_borrador", False) else None)
        try:
            yield al_avanzar
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
        with self._indicador_del_turno(chat["id"]) as al_avanzar:
            try:
                resultado = procesar_toque(self.conn, quien, token, chat["id"], self.ia,
                                           self.reloj, al_avanzar=al_avanzar)
                self.conn.commit()
            except Exception as e:  # noqa: BLE001 -- nunca en silencio: incidente y texto fijo
                self.conn.rollback()
                self._turno_caido(quien, chat["id"], e,
                                  clave=f"motor:toque_caido:{toque['id']}")
                return
        if resultado is not None and not resultado.repetido:
            self.imprimir(f"  → {resultado.texto[:70]}")

    def _guardar(self, mensaje, tg_user: int, chat_id: int, texto: str):
        """(quien, id del mensaje guardado), o `None` si no es de alguien del equipo. Un
        mensaje repetido devuelve el que ya estaba: el turno decide si falta atenderlo."""
        with espacio(self.conn, self.ws) as cur:
            try:
                quien = identificar_en_espacio(cur, tg_user, self.ws)
            except Denegado:
                self.imprimir("  (un mensaje de alguien que no es del equipo: no se atiende)")
                return None
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
                (self.ws, self.bot_id, mensaje["message_id"], chat_id, quien.app_user_id,
                 texto))
            fila = cur.fetchone()
            if fila is None:
                cur.execute("""select id from inbound_message
                                where workspace_id = %s and telegram_bot_id = %s
                                  and chat_id = %s and telegram_message_id = %s""",
                            (self.ws, self.bot_id, chat_id, mensaje["message_id"]))
                fila = cur.fetchone()
        self.conn.commit()
        return quien, str(fila["id"])

    def _turno_caido(self, quien, chat_id: int, error: Exception, *, clave: str,
                     entrante: str | None = None) -> None:
        """Un turno (de un mensaje o de un toque) que se cayó por algo que no es la IA."""
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
        self.imprimir(f"  ! el turno se cayó: {type(error).__name__}")

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


def _origen(u: dict[str, Any]) -> tuple[dict[str, Any], int | None]:
    """El chat y quién escribió o tocó, de un mensaje o de un toque: los dos se tratan igual
    cuando no se pueden recibir (revisión de la E2-4)."""
    toque = u.get("callback_query") or {}
    mensaje = u.get("message") or toque.get("message") or {}
    de = (u.get("message") or toque).get("from") or {}
    return mensaje.get("chat") or {}, de.get("id")
