"""El ciclo del motor detrás del webhook (E3-7): `python -m leda servir`.

Con el escuchador (`escucha.py`), el ciclo (`ciclo.py`) corre en cada vuelta del long polling.
Con el webhook (`leda.entrada`), los mensajes llegan por HTTP y nadie da vueltas: este hilo de
fondo corre el mismo ciclo, cada `CADA_S` segundos, para cada espacio activo con su bot. Es lo
que antes hacían el reloj y el ciclo viejos de `leda` (`reloj.montar`, `ciclo.Ciclo.tick`),
retirados con su escalera y sus cadencias (E3-7).

- **Cada espacio activo con token de bot** tiene su `Ciclo`, con su IA (`ia_real.desde_base`;
  sin una configurada, `recibir.IANoConfigurada`, y cada aviso deja su incidente), el reloj de
  Leda (`reloj.RelojDeLeda`, que fuera de `leda_motor` es el real) y el transporte de su bot.
  La lista de espacios se relee en cada vuelta: un espacio o un bot nuevos se suman solos.
- **Los avisos a la administración** salen una vez por vuelta (con el primer espacio), si hay
  `LEDA_BOT_TOKEN_ADMIN`.
- **Nunca en silencio:** un espacio activo sin token deja un incidente (`ETAPA_SIN_BOT`, una vez
  por proceso) y se dice en la consola; si la base no contesta, se dice en la consola, se
  descarta la conexión y la vuelta siguiente reconecta. Cada paso de cada ciclo ya va aislado
  (`Ciclo._paso`).
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import Any

from ..config import config
from ..db import admin, espacio
from ..despachador import Transporte, TransporteTelegram, texto_error_seguro
from ..incidentes import registrar_incidente

from .ciclo import Ciclo
from .ia import IA
from .recibir import IANoConfigurada
from .reloj import RelojDeLeda
from .tiempo import Reloj

CADA_S = 5.0
ETAPA_SIN_BOT = "motor_sin_bot"


def _tokens() -> dict[str, str]:
    return config.espacios_con_token()


def _ia_de(cur, workspace_id: str) -> IA:
    from .ia_real import desde_base

    try:
        return desde_base(cur, workspace_id, config)
    except LookupError as e:
        return IANoConfigurada(str(e))


class Fondo:
    def __init__(self, conectar: Callable[[], Any], *,
                 tokens: Callable[[], dict[str, str]] = _tokens,
                 ia_de: Callable[[Any, str], IA] = _ia_de,
                 transporte_de: Callable[[str], Transporte] = TransporteTelegram,
                 reloj_de: Callable[[], Reloj] = RelojDeLeda,
                 imprimir: Callable[[str], None] = print) -> None:
        self.conectar = conectar
        self.tokens = tokens
        self.ia_de = ia_de
        self.transporte_de = transporte_de
        self.reloj_de = reloj_de
        self.imprimir = imprimir
        self._conn = None
        self._ciclos: dict[str, tuple[str, Ciclo]] = {}     # slug → (token, ciclo)
        self._admin: tuple[str, Transporte] | None = None
        self._sin_bot: set[str] = set()

    def vuelta(self) -> dict[str, Any]:
        """Una vuelta por todos los espacios activos con bot: el resultado de cada ciclo, por
        espacio."""
        try:
            conn = self._conexion()
            with admin(conn) as cur:
                cur.execute("select id, slug from workspace where activo order by slug")
                activos = cur.fetchall()
            conn.commit()
        except Exception as e:  # noqa: BLE001 -- se reconecta en la vuelta siguiente
            self.imprimir(f"  ! el ciclo de fondo no pudo leer los espacios activos "
                          f"({texto_error_seguro(e)}); reconecta en la vuelta siguiente")
            self._descartar()
            return {}
        tokens = self.tokens()
        transporte_admin = self._transporte_admin(tokens.get("admin"))
        resultados: dict[str, Any] = {}
        for fila in activos:
            slug, ws = fila["slug"], str(fila["id"])
            token = tokens.get(slug)
            if not token:
                self._avisar_sin_bot(conn, ws, slug)
                continue
            self._sin_bot.discard(slug)
            ciclo = self._ciclo(conn, ws, slug, token, transporte_admin)
            self._refrescar_reloj(ciclo)
            resultados[slug] = ciclo.vuelta(admin=not resultados)
        return resultados

    def correr(self, parar: threading.Event, cada_s: float = CADA_S) -> None:
        while not parar.is_set():
            inicio = time.monotonic()
            try:
                self.vuelta()
            except Exception as e:  # noqa: BLE001 -- el hilo de fondo nunca se muere
                self.imprimir(f"  ! el ciclo de fondo se cayó ({texto_error_seguro(e)})")
                self._descartar()
            parar.wait(max(0.0, cada_s - (time.monotonic() - inicio)))

    # -- lo de cada espacio ------------------------------------------------------------------

    def _ciclo(self, conn, ws: str, slug: str, token: str,
               transporte_admin: Transporte | None) -> Ciclo:
        actual = self._ciclos.get(slug)
        if actual is not None and actual[0] == token:
            actual[1].transporte_admin = transporte_admin
            return actual[1]
        with espacio(conn, ws) as cur:
            ia = self.ia_de(cur, ws)
        conn.commit()
        ciclo = Ciclo(conn, ws, ia, self.reloj_de(), self.transporte_de(token),
                      transporte_admin=transporte_admin, imprimir=self.imprimir)
        self._ciclos[slug] = (token, ciclo)
        return ciclo

    def _refrescar_reloj(self, ciclo: Ciclo) -> None:
        """El reloj de Leda vuelve a leer su adelanto en cada vuelta, como en el escuchador."""
        refrescar = getattr(ciclo.reloj, "refrescar", None)
        if refrescar is None:
            return
        try:
            refrescar(ciclo.conn, ciclo.ws)
            ciclo.conn.commit()
        except Exception:  # noqa: BLE001 -- sigue con el adelanto que tenía
            ciclo.conn.rollback()

    def _transporte_admin(self, token: str | None) -> Transporte | None:
        if not token:
            return None
        if self._admin is None or self._admin[0] != token:
            self._admin = (token, self.transporte_de(token))
        return self._admin[1]

    def _avisar_sin_bot(self, conn, ws: str, slug: str) -> None:
        if slug in self._sin_bot:
            return
        variable = f"LEDA_BOT_TOKEN_{slug.upper()}"
        self.imprimir(f"  ! '{slug}' está activo sin {variable}: su ciclo no corre hasta "
                      f"que se configure.")
        try:
            with espacio(conn, ws) as cur:
                registrar_incidente(
                    cur, ws, f"El espacio '{slug}' está activo sin {variable} en el entorno "
                             f"del servidor: su ciclo (escalera, avisos guardados y despacho) "
                             f"no corre y su webhook no atiende.",
                    severidad="alta", etapa=ETAPA_SIN_BOT)
            conn.commit()
            self._sin_bot.add(slug)
        except Exception as e:  # noqa: BLE001 -- se reintenta en la vuelta siguiente
            conn.rollback()
            self.imprimir(f"  ! tampoco se pudo registrar el incidente: {texto_error_seguro(e)}")

    # -- la conexión -------------------------------------------------------------------------

    def _conexion(self):
        if self._conn is None or self._conn.closed:
            self._conn = self.conectar()
            self._ciclos = {}           # cada ciclo guarda su conexión: se rehacen
        return self._conn

    def _descartar(self) -> None:
        conn, self._conn = self._conn, None
        self._ciclos = {}
        if conn is not None:
            try:
                conn.close()
            except Exception:  # noqa: BLE001 -- ya estaba rota
                pass


def montar(conectar: Callable[[], Any], *, cada_s: float = CADA_S,
           parar: threading.Event | None = None, **opciones) -> threading.Thread:
    """El hilo de fondo de `servir`, sin arrancar (`.start()`)."""
    fondo = Fondo(conectar, **opciones)
    return threading.Thread(target=fondo.correr, args=(parar or threading.Event(), cada_s),
                            name="leda-motor-fondo", daemon=True)
