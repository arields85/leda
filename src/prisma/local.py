"""Modo local: escuchar por long polling en lugar de webhook.

Telegram entrega mensajes de dos maneras. El webhook necesita que tu máquina
sea alcanzable desde internet con HTTPS; el polling no necesita nada — el
proceso pregunta cada tanto si hay algo nuevo.

Para probar en tu computadora, polling. Al pasar a la VPS se cambia por
webhook y no se toca nada más: los dos caminos llaman a la misma función.

Este comando hace el circuito completo en un solo proceso: escucha, procesa,
corre la escalera y despacha la cola. Es más simple de seguir que cuatro
servicios, y para dos o tres personas alcanza de sobra.
"""

from __future__ import annotations

import signal
import sys
import time
from datetime import datetime, timezone

import httpx

from .calendario import Calendario
from .config import config
from .db import conectar_autoridad, espacio
from .despachador import TransporteTelegram, despachar
from .gateway import procesar_update
from .reloj import ejecutar_cadencia, ejecutar_escalera

_seguir = True


def _imprimir(texto: str = "") -> None:
    """No deja caer el listener si la consola no representa Unicode."""
    salida = sys.stdout
    try:
        salida.write(texto + "\n")
    except UnicodeEncodeError:
        encoding = getattr(salida, "encoding", None) or "ascii"
        seguro = texto.encode(encoding, errors="backslashreplace").decode(encoding)
        salida.write(seguro + "\n")
    salida.flush()


def _parar(*_):
    global _seguir
    _seguir = False
    _imprimir("\nCortando…")


class Escucha:
    def __init__(self, conn, slug: str, workspace_id: str, token: str,
                 cliente: httpx.Client | None = None,
                 authority_conn=None) -> None:
        self.conn = conn
        self.slug = slug
        self.ws = workspace_id
        self.token = token
        self.http = cliente or httpx.Client(timeout=40)
        self.offset = 0
        self.transporte = TransporteTelegram(token, cliente=httpx.Client(timeout=15))
        self.authority_conn = authority_conn

    # -- ciclo -------------------------------------------------------------

    def una_vuelta(self, espera: int = 25) -> int:
        recibidos = self.recibir(espera)
        self.tareas_de_fondo()
        return recibidos

    def recibir(self, espera: int = 25) -> int:
        try:
            r = self.http.get(
                f"https://api.telegram.org/bot{self.token}/getUpdates",
                # callback_query va sí o sí: Telegram no entrega lo que no se
                # le pide, y sin esto los botones se dibujan pero el toque no
                # llega nunca. No da error: sencillamente no pasa nada.
                params={"offset": self.offset, "timeout": espera,
                        "allowed_updates": '["message","callback_query"]'})
            r.raise_for_status()
            updates = r.json().get("result", [])
        except Exception as e:  # noqa: BLE001
            _imprimir(f"  (sin conexión con Telegram: {e})")
            time.sleep(5)
            return 0

        for u in updates:
            self.offset = u["update_id"] + 1
            origen = u.get("message") or u.get("callback_query") or {}
            quien = origen.get("from", {}).get("first_name", "?")
            if "callback_query" in u:
                _imprimir(f"  ← {quien}: [tocó un botón]")
            else:
                _imprimir(f"  ← {quien}: {origen.get('text', '')[:70]}")
            try:
                procesar_update(self.conn, self.slug, u,
                                authority_conn=self.authority_conn)
            except Exception as e:  # noqa: BLE001
                # Un mensaje que rompe no puede frenar la escucha.
                self.conn.rollback()
                _imprimir(f"  ! no se pudo procesar: {type(e).__name__}")
        return len(updates)

    def tareas_de_fondo(self, ahora: datetime | None = None) -> dict[str, int]:
        ahora = ahora or datetime.now(timezone.utc)
        with espacio(self.conn, self.ws) as cur:
            cal = Calendario.desde_base(cur, self.ws)
            ejecutar_escalera(cur, self.ws, cal, ahora)
            resumen = despachar(cur, self.ws, self.transporte, cal, ahora)
        self.conn.commit()
        for _ in range(resumen["enviados"]):
            _imprimir("  → enviado")
        return resumen

    def correr_cadencia(self, nombre: str, ahora: datetime | None = None) -> int:
        """Dispara una cadencia a mano, para no esperar al lunes 09:15."""
        with espacio(self.conn, self.ws) as cur:
            cal = Calendario.desde_base(cur, self.ws)
            n = ejecutar_cadencia(cur, self.ws, nombre, cal, ahora)
        self.conn.commit()
        return n


def escuchar(conn, slug: str, workspace_id: str) -> None:
    global _seguir
    _seguir = True
    signal.signal(signal.SIGINT, _parar)

    token = config.token_bot(slug)
    if not config.authority_db_url:
        raise RuntimeError("Falta PRISMA_AUTHORITY_DB_URL.")
    authority_conn = conectar_autoridad(config.authority_db_url)
    e = Escucha(conn, slug, workspace_id, token,
                authority_conn=authority_conn)

    r = httpx.get(f"https://api.telegram.org/bot{token}/getMe", timeout=15).json()
    if not r.get("ok"):
        raise SystemExit("El token del bot no es válido.")
    usuario = r["result"]["username"]

    # Un webhook activo bloquea getUpdates: si quedó de una prueba anterior,
    # se saca.
    httpx.post(f"https://api.telegram.org/bot{token}/deleteWebhook", timeout=15)

    _imprimir(f"Escuchando como @{usuario} — espacio '{slug}'.")
    _imprimir("Ctrl+C para cortar.\n")

    while _seguir:
        e.una_vuelta()
