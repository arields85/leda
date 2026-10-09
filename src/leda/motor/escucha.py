"""El escuchador del motor de conversación, por long polling (E3-7; diseño probado en la
Etapa 2, E2-3b).

    python -m leda.motor.escucha corework
    python -m leda escuchar corework

Portado de `prueba_chica/escuchar.py`, borrada el 2026-10-07. Lo que se hace con cada
update es lo mismo que en el webhook de `leda.entrada` (`recibir.py`); acá queda lo propio de
escuchar:

- **Bot del equipo:** saca un webhook si lo hay (bloquea `getUpdates`) y pide los mensajes y
  los toques. Después de recibirlos, el ciclo despacha lo que quedó en el outbox.
- **Bot de administración:** se lo sondea sin esperar, sólo para registrar el chat de un
  administrador de plataforma que le escribe, y por él salen los avisos de incidentes
  (`despachador.despachar_avisos_admin`). Un bot de administración con webhook puesto no se
  toca ni se sondea.
- **El reloj de Leda** (`reloj.py`): el comando lo prende con el adelanto que se guarda en
  `leda_motor` con `python -m leda.motor.reloj`; se vuelve a leer en cada vuelta.
- **El indicador de actividad** (`recibir.py`; ADR 0011, decisión 2): mientras corre el turno de
  alguien del equipo, el "escribiendo…", los tres puntos del borrador y el texto que la IA va
  redactando (`despachador.mantener_chat_activo`). Apenas termina el turno, la respuesta se
  despacha (decisión 1; `recibir.Recepcion.despachar_ahora`): no espera al resto del lote ni de
  la vuelta, y el indicador no la demora (el mensaje reemplaza al borrador, sin retiro). La
  consola dice cuánto tardó en salir desde que su texto estuvo listo.
- **Los archivos** (`recibir.py`; ADR 0019, decisión 4): se bajan por la API del bot
  (`BotTelegram.bajar`), cortando en el tamaño máximo. Mientras un álbum espera su turno, los
  updates se piden con la espera del álbum (`recibir.ESPERA_ALBUM_S`) y, después de recibirlos,
  se atienden los álbumes que ya esperaron (`recibir.Recepcion.atender_albumes`). Al arrancar
  se mira si quedó alguno de antes.
- **El ciclo** (`ciclo.py`): en cada vuelta, el despacho y los avisos a la administración; con
  `seguimiento` (el comando lo prende), la escalera y los avisos guardados una vez por minuto.
  Cada paso aislado: si uno se cae, un incidente y los demás siguen.

Si falla recibir un update, se deshace lo suyo, la escucha sigue y el offset no pasa de él:
Telegram lo vuelve a entregar; a los `INTENTOS_POR_UPDATE` se deja, con un incidente y el texto
fijo a quien escribió o tocó (`recibir.recibir_update`). El token de los bots nunca se imprime:
los errores de Telegram pasan por `despachador.pedido_telegram`. Ctrl+C corta al terminar la
vuelta en curso.
"""

from __future__ import annotations

import argparse
import signal
import sys
import time
from typing import Any, Callable

import httpx

from ..db import admin, espacio
from ..despachador import Transporte, pedido_telegram, texto_error_seguro

from . import archivos, recibir
from .ciclo import Ciclo
from .ia import IA
from .recibir import (INTENTOS_POR_UPDATE, AbrirIndicador, Bajar, IntentosPorUpdate,
                      Recepcion, recibir_update, registrar_admin)
from .tiempo import Reloj

ESPERA_S = 25

__all__ = ["BotTelegram", "Escucha", "INTENTOS_POR_UPDATE", "main"]


class BotTelegram:
    """Lo mínimo de la API de un bot. El token vive sólo en la dirección."""

    def __init__(self, token: str, http: httpx.Client) -> None:
        self._base = f"https://api.telegram.org/bot{token}"
        self._base_archivos = f"https://api.telegram.org/file/bot{token}"
        self._http = http

    def llamar(self, metodo: str, **parametros: Any) -> Any:
        r = pedido_telegram(self._http.post, f"{self._base}/{metodo}", json=parametros)
        pedido_telegram(r.raise_for_status)
        cuerpo = r.json()
        if not cuerpo.get("ok"):
            raise RuntimeError(f"Telegram respondió ok=false a {metodo}.")
        return cuerpo["result"]

    def bajar(self, file_id: str, maximo: int) -> bytes:
        """El contenido de un archivo recibido (`getFile` y su descarga; `recibir.Bajar`). Si
        Telegram dice que pasa de `maximo`, o la descarga pasa de ahí, no se baja más:
        `archivos.Rechazo(DEMASIADO_GRANDE)`. Los errores no llevan la dirección, que lleva el
        token (`pedido_telegram`)."""
        datos = self.llamar("getFile", file_id=file_id)
        if (datos.get("file_size") or 0) > maximo:
            raise archivos.Rechazo(archivos.DEMASIADO_GRANDE)
        ruta = datos.get("file_path")
        if not ruta:
            raise RuntimeError("Telegram no dijo de dónde bajar el archivo.")

        def leer() -> bytes | None:
            partes, total = [], 0
            with self._http.stream("GET", f"{self._base_archivos}/{ruta}") as r:
                r.raise_for_status()
                for trozo in r.iter_bytes():
                    total += len(trozo)
                    if total > maximo:
                        return None
                    partes.append(trozo)
            return b"".join(partes)

        contenido = pedido_telegram(leer)
        if contenido is None:
            raise archivos.Rechazo(archivos.DEMASIADO_GRANDE)
        return contenido


class Escucha(Recepcion):
    def __init__(self, conn, workspace_id: str, ia: IA, reloj: Reloj, *, bot: BotTelegram,
                 transporte: Transporte, bot_admin: BotTelegram | None = None,
                 transporte_admin: Transporte | None = None, seguimiento: bool = False,
                 imprimir: Callable[[str], None] = print,
                 indicador: AbrirIndicador | None = None, bajar: Bajar | None = None) -> None:
        super().__init__(conn, workspace_id, ia, reloj, bot_id=None, senal=self._senal,
                         imprimir=imprimir, indicador=indicador, transporte=transporte,
                         bajar=bajar or bot.bajar)
        # Al arrancar se mira si quedó un álbum esperando su turno de antes.
        self.albumes_en_espera = True
        self.bot = bot
        self.bot_admin = bot_admin
        self.transporte_admin = transporte_admin
        self.offset = 0
        self.intentos = IntentosPorUpdate()
        self.offset_admin = 0
        self.admin_listo = False
        # Lo que sale: el despacho en cada vuelta y, con `seguimiento`, la escalera y los
        # avisos guardados cada minuto (`ciclo.py`).
        self.ciclo = Ciclo(conn, workspace_id, ia, reloj, transporte,
                           transporte_admin=transporte_admin, seguimiento=seguimiento,
                           imprimir=imprimir)

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
        self.refrescar_reloj()
        # Con un álbum en espera, los updates se piden con la espera del álbum: al volver, se
        # atiende el que ya esperó.
        hay_album = self.albumes_en_espera
        recibidos = self.recibir(min(espera, recibir.ESPERA_ALBUM_S) if hay_album else espera)
        if self.albumes_en_espera:
            self.atender_albumes()
            # Como en el webhook: la respuesta de un álbum sale ya, y su borrador se retira.
            self.despachar_ahora()
        self.recibir_admin()
        self.despachar()
        return recibidos

    def refrescar_reloj(self) -> None:
        """El reloj de Leda (`reloj.RelojDeLeda`) vuelve a leer su adelanto al empezar cada
        vuelta: el comando que lo adelanta se nota en la vuelta siguiente. Un reloj sin
        adelanto (el del sistema, el fijo de las pruebas) no tiene qué leer."""
        refrescar = getattr(self.reloj, "refrescar", None)
        if refrescar is None:
            return
        try:
            cambio = refrescar(self.conn, self.ws)
            self.conn.commit()
        except Exception as e:  # noqa: BLE001 -- sigue con el adelanto que tenía
            self.conn.rollback()
            self.imprimir(f"  ! no se pudo leer el reloj de Leda ({texto_error_seguro(e)}); "
                          "sigue con el de antes")
            return
        if cambio:
            self.imprimir(f"  ⏰ reloj de Leda: {self.reloj.ahora():%Y-%m-%d %H:%M} UTC")

    def recibir(self, espera: int) -> int:
        try:
            updates = self.bot.llamar("getUpdates", offset=self.offset, timeout=espera,
                                      allowed_updates=["message", "callback_query"])
        except Exception as e:  # noqa: BLE001 -- sin conexión, se reintenta en la vuelta
            self.imprimir(f"  (sin conexión con Telegram: {texto_error_seguro(e)})")
            time.sleep(min(espera, 5))
            return 0
        for u in updates:
            # Con el update recibido, su respuesta ya salió (`recibir_update`, que despacha
            # enseguida): no espera al resto del lote ni a la vuelta.
            if not recibir_update(self, self.intentos, u):
                break       # se vuelve a pedir desde éste en la vuelta siguiente
            self.offset = u["update_id"] + 1
        return len(updates)

    def _senal(self, callback_query_id: str) -> None:
        self.bot.llamar("answerCallbackQuery", callback_query_id=callback_query_id)

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
            registrar_admin(self.conn, u, self.imprimir)
        return len(updates)

    # -- lo que sale ---------------------------------------------------------------------

    def despachar(self) -> None:
        """El ciclo (`ciclo.py`): cada paso aislado, con un incidente si se cae. Los avisos a
        la administración, sólo si su bot está listo."""
        self.ciclo.vuelta(admin=self.admin_listo)


_seguir = True


def _parar(*_) -> None:
    global _seguir
    _seguir = False
    print("\nCortando al terminar esta vuelta…")


def main(argv: list[str] | None = None) -> int:
    from ..config import config
    from ..db import conectar
    from ..despachador import TransporteTelegram, mantener_chat_activo

    from .ia_real import desde_base
    from .reloj import RelojDeLeda

    p = argparse.ArgumentParser(prog="python -m leda.motor.escucha")
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
        conn, ws, ia, RelojDeLeda(),
        bot=BotTelegram(token, httpx.Client(timeout=ESPERA_S + 15)),
        transporte=TransporteTelegram(token),
        bot_admin=BotTelegram(token_admin, httpx.Client(timeout=15)) if token_admin else None,
        transporte_admin=TransporteTelegram(token_admin) if token_admin else None,
        seguimiento=True,
        # El motor sólo atiende chats privados (`recibir.py`): con borrador.
        indicador=lambda chat_id: mantener_chat_activo(token, chat_id, chat_type="private"))
    try:
        usuario = escucha.preparar()
    except Exception as e:  # noqa: BLE001
        print(f"No se pudo hablar con Telegram: {texto_error_seguro(e)}")
        return 1

    signal.signal(signal.SIGINT, _parar)
    print(f"Escuchando como @{usuario}, espacio '{a.slug}', con {ia.nombre}; la escalera y "
          f"los avisos guardados corren cada minuto. Ctrl+C corta.")
    while _seguir:
        escucha.una_vuelta()
    return 0


if __name__ == "__main__":
    sys.exit(main())
