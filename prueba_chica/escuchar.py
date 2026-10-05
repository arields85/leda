"""El escuchador de la prueba chica, por long polling (E2-3b).

    python -m prueba_chica.escuchar corework

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Entrada propia"). `leda.local` no se puede
usar (importa `gateway`): acá está lo mínimo, reescrito.

- **Bot del equipo:** saca un webhook si lo hay (bloquea `getUpdates`) y pide los mensajes.
  Cada mensaje escrito en un chat privado, de alguien del equipo (`identificar_en_espacio`),
  se guarda en `inbound_message` con el bot que lo recibió y `on conflict do nothing`: un
  mensaje repetido no se guarda dos veces, y el turno (`procesar_turno`) no corre dos veces
  sobre el mismo mensaje. Si un mensaje quedó guardado sin turno (el proceso se cortó en el
  medio), al volver a llegar se atiende. Después del turno, se confirma y se despacha.
- **Activación:** `/start <enlace>` canjea el enlace de `python -m leda enlaces` y `/start`
  solo saluda a quien ya está vinculado, con el mecanismo de siempre (`leda.onboarding`, que no
  alcanza a los flujos congelados) y su texto de bienvenida.
- **Bot de administración:** se lo sondea sin esperar, sólo para registrar el chat de un
  administrador de plataforma que le escribe (como `local.recibir_admin`), y por él salen los
  avisos de incidentes (`despachador.despachar_avisos_admin`). Un bot de administración con
  webhook puesto no se toca ni se sondea.

Lo que no es un mensaje escrito de alguien del equipo (un grupo, un mensaje editado, una foto
sin texto, un desconocido) no se atiende. Si un turno se cae por algo que no es la IA, queda un
incidente y la persona recibe el texto fijo de la falla (nunca en silencio). Si falla recibir un
update (guardarlo, activar), se deshace lo suyo, la escucha sigue y el offset no pasa de él:
Telegram lo vuelve a entregar; a los `INTENTOS_POR_UPDATE` se deja, con un incidente y el texto
fijo a la persona (revisión de la E2-3b). El token de los
bots nunca se imprime: los errores de Telegram pasan por `despachador.pedido_telegram`.
Ctrl+C corta al terminar la vuelta en curso.
"""

from __future__ import annotations

import argparse
import signal
import sys
import time
from typing import Any, Callable

import httpx

from leda.autoridad import Canal, Denegado, identificar, identificar_en_espacio
from leda.calendario import Calendario
from leda.db import admin, espacio, registrar_auditoria
from leda.despachador import (Transporte, despachar, despachar_avisos_admin, pedido_telegram,
                              texto_error_seguro)
from leda.incidentes import (ETAPA_TURNO_CONVERSACION, REFERENCIA_INBOUND_MESSAGE,
                             registrar_incidente)
from leda.onboarding import ActivacionInvalida, activar, bienvenida
from leda.salida import enqueue_outbox

from .ia import IA
from .tiempo import Reloj
from .turno import TEXTO_SI_LA_IA_FALLA, procesar_turno

ESPERA_S = 25
INTENTOS_POR_UPDATE = 3     # un update que falla al recibirse se reintenta; después, se deja


class BotTelegram:
    """Lo mínimo de la API de un bot. El token vive sólo en la dirección."""

    def __init__(self, token: str, http: httpx.Client) -> None:
        self._base = f"https://api.telegram.org/bot{token}"
        self._http = http

    def llamar(self, metodo: str, **parametros: Any) -> Any:
        r = pedido_telegram(self._http.post, f"{self._base}/{metodo}", json=parametros)
        pedido_telegram(r.raise_for_status)
        cuerpo = r.json()
        if not cuerpo.get("ok"):
            raise RuntimeError(f"Telegram respondió ok=false a {metodo}.")
        return cuerpo["result"]


class Escucha:
    def __init__(self, conn, workspace_id: str, ia: IA, reloj: Reloj, *, bot: BotTelegram,
                 transporte: Transporte, bot_admin: BotTelegram | None = None,
                 transporte_admin: Transporte | None = None,
                 imprimir: Callable[[str], None] = print) -> None:
        self.conn = conn
        self.ws = workspace_id
        self.ia = ia
        self.reloj = reloj
        self.bot = bot
        self.transporte = transporte
        self.bot_admin = bot_admin
        self.transporte_admin = transporte_admin
        self.imprimir = imprimir
        self.bot_id: int | None = None
        self.offset = 0
        self.fallas: dict[int, int] = {}       # update → veces que falló al recibirlo
        self.offset_admin = 0
        self.admin_listo = False

    # -- arranque ------------------------------------------------------------------------

    def preparar(self) -> str:
        """El id y el nombre del bot; saca un webhook del bot del equipo. Del bot de
        administración sólo pregunta: con webhook, no se lo sondea."""
        yo = self.bot.llamar("getMe")
        self.bot_id = int(yo["id"])
        self.bot.llamar("deleteWebhook")
        if self.bot_admin is not None:
            webhook = (self.bot_admin.llamar("getWebhookInfo") or {}).get("url")
            self.admin_listo = not webhook
            if webhook:
                self.imprimir("  ! el bot de administración tiene un webhook puesto: no se "
                              "sondea, para no robarle los mensajes a quien lo sirve.")
        return yo.get("username", "?")

    # -- una vuelta ----------------------------------------------------------------------

    def una_vuelta(self, espera: int = ESPERA_S) -> int:
        recibidos = self.recibir(espera)
        self.recibir_admin()
        self.despachar()
        return recibidos

    def recibir(self, espera: int) -> int:
        try:
            updates = self.bot.llamar("getUpdates", offset=self.offset, timeout=espera,
                                      allowed_updates=["message"])
        except Exception as e:  # noqa: BLE001 -- sin conexión, se reintenta en la vuelta
            self.imprimir(f"  (sin conexión con Telegram: {texto_error_seguro(e)})")
            time.sleep(min(espera, 5))
            return 0
        for u in updates:
            try:
                self.procesar(u)
            except Exception as e:  # noqa: BLE001 -- la escucha sigue; el update no se pierde
                self.conn.rollback()
                if not self._fallo_al_recibir(u, e):
                    break       # se vuelve a pedir desde éste en la vuelta siguiente
            self.fallas.pop(u["update_id"], None)
            self.offset = u["update_id"] + 1
        return len(updates)

    def _fallo_al_recibir(self, u: dict[str, Any], error: Exception) -> bool:
        """Una falla al recibir un update (la base que se cae al guardarlo, por ejemplo). Las
        primeras veces no se avanza: Telegram lo vuelve a entregar y se reintenta, y un
        mensaje que quedó guardado sin turno se atiende al volver. A los
        `INTENTOS_POR_UPDATE`, se deja: nunca en silencio, con un incidente y, si es de
        alguien del equipo, el texto fijo de la falla. `True` si se deja."""
        uid = u["update_id"]
        self.fallas[uid] = self.fallas.get(uid, 0) + 1
        self.imprimir(f"  ! no se pudo recibir el update {uid} ({type(error).__name__}), "
                      f"intento {self.fallas[uid]} de {INTENTOS_POR_UPDATE}")
        if self.fallas[uid] < INTENTOS_POR_UPDATE:
            return False
        mensaje = u.get("message") or {}
        chat_id = (mensaje.get("chat") or {}).get("id")
        tg_user = (mensaje.get("from") or {}).get("id")
        try:
            with espacio(self.conn, self.ws) as cur:
                quien = None
                if tg_user is not None and (mensaje.get("chat") or {}).get("type") == "private":
                    try:
                        quien = identificar_en_espacio(cur, tg_user, self.ws)
                    except Denegado:
                        quien = None
                registrar_incidente(
                    cur, self.ws,
                    f"El escuchador del motor no pudo recibir un update de Telegram tras "
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
        except Exception as e:  # noqa: BLE001 -- queda en la consola; la escucha sigue
            self.conn.rollback()
            self.imprimir(f"  ! tampoco se pudo registrar la falla: {texto_error_seguro(e)}")
        return True

    def procesar(self, u: dict[str, Any]) -> None:
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
        try:
            resultado = procesar_turno(self.conn, quien, entrante, self.ia, self.reloj)
            self.conn.commit()
        except Exception as e:  # noqa: BLE001 -- nunca en silencio: incidente y texto fijo
            self.conn.rollback()
            self._turno_caido(quien, entrante, chat_id, e)
            return
        if not resultado.repetido:
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
            cur.execute(
                """insert into inbound_message (workspace_id, telegram_bot_id,
                                                telegram_message_id, chat_id, app_user_id,
                                                texto, at)
                   values (%s, %s, %s, %s, %s, %s, %s)
                   on conflict (workspace_id, telegram_bot_id, chat_id, telegram_message_id)
                      where telegram_bot_id is not null and telegram_message_id is not null
                      do nothing
                   returning id""",
                (self.ws, self.bot_id, mensaje["message_id"], chat_id, quien.app_user_id,
                 texto, self.reloj.ahora()))
            fila = cur.fetchone()
            if fila is None:
                cur.execute("""select id from inbound_message
                                where workspace_id = %s and telegram_bot_id = %s
                                  and chat_id = %s and telegram_message_id = %s""",
                            (self.ws, self.bot_id, chat_id, mensaje["message_id"]))
                fila = cur.fetchone()
        self.conn.commit()
        return quien, str(fila["id"])

    def _turno_caido(self, quien, entrante: str, chat_id: int, error: Exception) -> None:
        ahora = self.reloj.ahora()
        try:
            with espacio(self.conn, self.ws) as cur:
                registrar_incidente(
                    cur, self.ws,
                    "Un turno del motor de conversación se cayó por algo que no es la IA: "
                    "la persona recibió el texto fijo de la falla.",
                    severidad="alta", referencia_cruda=texto_error_seguro(error),
                    etapa=ETAPA_TURNO_CONVERSACION, referencia_tipo=REFERENCIA_INBOUND_MESSAGE,
                    referencia_id=entrante, chat_id=chat_id, app_user_id=quien.app_user_id,
                    notificado_en=ahora)
                enqueue_outbox(cur, workspace_id=self.ws, chat_id=chat_id,
                               text=TEXTO_SI_LA_IA_FALLA, dedupe_key=f"motor:respuesta:{entrante}",
                               recipient_membership_id=quien.membership_id, is_response=True,
                               scheduled_for=ahora)
            self.conn.commit()
        except Exception as e:  # noqa: BLE001 -- la escucha sigue; queda en la consola
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

    # -- el bot de administración --------------------------------------------------------

    def recibir_admin(self) -> int:
        if self.bot_admin is None or not self.admin_listo:
            return 0
        try:
            updates = self.bot_admin.llamar("getUpdates", offset=self.offset_admin, timeout=0,
                                            allowed_updates=["message"])
        except Exception as e:  # noqa: BLE001
            self.imprimir(f"  (sin conexión con el bot de administración: "
                          f"{texto_error_seguro(e)})")
            return 0
        for u in updates:
            self.offset_admin = u["update_id"] + 1
            mensaje = u.get("message") or {}
            tg_user = (mensaje.get("from") or {}).get("id")
            chat_id = (mensaje.get("chat") or {}).get("id")
            if tg_user is None or chat_id is None:
                continue
            with admin(self.conn) as cur:
                try:
                    quien = identificar(cur, tg_user, Canal.ADMINISTRACION, None)
                except Denegado:
                    continue
                registrar_auditoria(cur, accion="mensaje_admin",
                                    actor_app_user_id=quien.app_user_id,
                                    actor_kind="persona", detalle={"chat_id": chat_id})
            self.conn.commit()
            self.imprimir("  ← [admin] chat registrado para los avisos de incidentes")
        return len(updates)

    # -- lo que sale ---------------------------------------------------------------------

    def despachar(self) -> None:
        ahora = self.reloj.ahora()
        try:
            with espacio(self.conn, self.ws) as cur:
                r = despachar(cur, self.ws, self.transporte,
                              Calendario.desde_base(cur, self.ws), ahora)
            self.conn.commit()
            if r["pospuestos"]:
                self.imprimir(f"  … {r['pospuestos']} pospuesto(s) hasta la próxima jornada")
        except Exception as e:  # noqa: BLE001 -- lo que no salió, sale en otra vuelta
            self.conn.rollback()
            self.imprimir(f"  ! no se pudo despachar: {texto_error_seguro(e)}")
        if self.transporte_admin is None or not self.admin_listo:
            return
        try:
            # Con el reloj real: `admin_notice` lo fecha la base, no el motor.
            with admin(self.conn) as cur:
                despachar_avisos_admin(cur, self.transporte_admin)
            self.conn.commit()
        except Exception as e:  # noqa: BLE001
            self.conn.rollback()
            self.imprimir(f"  ! no se pudo avisar a la administración: "
                          f"{texto_error_seguro(e)}")


_seguir = True


def _parar(*_) -> None:
    global _seguir
    _seguir = False
    print("\nCortando al terminar esta vuelta…")


def main(argv: list[str] | None = None) -> int:
    from leda.config import config
    from leda.db import conectar
    from leda.despachador import TransporteTelegram

    from .ia_real import desde_base
    from .tiempo import RelojDelSistema

    p = argparse.ArgumentParser(prog="python -m prueba_chica.escuchar")
    p.add_argument("slug")
    a = p.parse_args(argv)

    conn = conectar()
    with admin(conn) as cur:
        cur.execute("select id from workspace where slug = %s and activo", (a.slug,))
        fila = cur.fetchone()
    conn.commit()
    if fila is None:
        print(f"No hay un espacio activo '{a.slug}'.")
        return 1
    ws = str(fila["id"])
    try:
        with espacio(conn, ws) as cur:
            ia = desde_base(cur, ws, config)
        token = config.token_bot(a.slug)
    except LookupError as e:
        print(e)
        return 1
    try:
        token_admin = config.token_bot("admin")
    except LookupError:
        token_admin = None
        print("(sin LEDA_BOT_TOKEN_ADMIN: los avisos de incidentes quedan encolados)")

    escucha = Escucha(
        conn, ws, ia, RelojDelSistema(),
        bot=BotTelegram(token, httpx.Client(timeout=ESPERA_S + 15)),
        transporte=TransporteTelegram(token),
        bot_admin=BotTelegram(token_admin, httpx.Client(timeout=15)) if token_admin else None,
        transporte_admin=TransporteTelegram(token_admin) if token_admin else None)
    try:
        usuario = escucha.preparar()
    except Exception as e:  # noqa: BLE001
        print(f"No se pudo hablar con Telegram: {texto_error_seguro(e)}")
        return 1

    signal.signal(signal.SIGINT, _parar)
    print(f"Escuchando como @{usuario}, espacio '{a.slug}', con {ia.nombre}. Ctrl+C corta.")
    while _seguir:
        escucha.una_vuelta()
    return 0


if __name__ == "__main__":
    sys.exit(main())
