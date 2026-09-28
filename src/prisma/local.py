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
from .db import admin, conectar_autoridad, espacio
from .despachador import (Transporte, TransporteTelegram, despachar,
                          despachar_avisos_admin)
from .gateway import (ETAPA_TOQUE_BOTON, ETAPA_TURNO_TEXTO, procesar_update,
                      reportar_incidente_no_manejado)
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
        self._transporte_admin: Transporte | None = None
        self._transporte_admin_probado = False

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
                # Un mensaje que rompe no puede frenar la escucha. Decisión
                # del usuario, 2026-09-25: un error nunca pasa en silencio
                # -- `procesar_update` ya atrapa casi todo por su cuenta
                # (incidente + aviso neutro), así que llegar hasta acá es lo
                # que queda para una falla estructural previa a eso (p. ej.
                # un update malformado). `self.ws` es el único espacio que
                # escucha este proceso, así que se sabe igual sin haberlo
                # resuelto adentro de `procesar_update`.
                self.conn.rollback()
                mensaje_o_toque = origen if "callback_query" not in u else (
                    u["callback_query"].get("message") or {})
                chat_id = mensaje_o_toque.get("chat", {}).get("id")
                tg_user = origen.get("from", {}).get("id")
                etapa = ETAPA_TOQUE_BOTON if "callback_query" in u else ETAPA_TURNO_TEXTO
                reportar_incidente_no_manejado(
                    self.conn, workspace_id=self.ws, chat_id=chat_id,
                    tg_user=tg_user, error=e, etapa=etapa)
                _imprimir(f"  ! no se pudo procesar: {type(e).__name__}")
        return len(updates)

    def _obtener_transporte_admin(self) -> Transporte | None:
        """El bot de administración es opcional en desarrollo local: si
        `PRISMA_BOT_TOKEN_ADMIN` no está configurado, los avisos de
        incidente quedan encolados en `admin_notice` igual (los arma
        `incidentes.registrar_incidente`) y se entregan solos en cuanto se
        configure el token, sin perder nada mientras tanto."""
        if self._transporte_admin_probado:
            return self._transporte_admin
        self._transporte_admin_probado = True
        try:
            token = config.token_bot("admin")
        except LookupError:
            return None
        self._transporte_admin = TransporteTelegram(
            token, cliente=httpx.Client(timeout=15))
        return self._transporte_admin

    def tareas_de_fondo(self, ahora: datetime | None = None) -> dict[str, int]:
        ahora = ahora or datetime.now(timezone.utc)
        with espacio(self.conn, self.ws) as cur:
            cal = Calendario.desde_base(cur, self.ws)
            ejecutar_escalera(cur, self.ws, cal, ahora)
            resumen = despachar(cur, self.ws, self.transporte, cal, ahora)
        self.conn.commit()
        for _ in range(resumen["enviados"]):
            _imprimir("  → enviado")

        # El aviso a la administración (T28, Constitución §10) no está
        # acotado a este espacio -- puede venir de cualquiera, o de ninguno
        # -- así que se despacha aparte, bajo rol `prisma_admin`.
        transporte_admin = self._obtener_transporte_admin()
        if transporte_admin is not None:
            with admin(self.conn) as cur:
                resumen_admin = despachar_avisos_admin(cur, transporte_admin, ahora)
            self.conn.commit()
            resumen["avisos_admin_enviados"] = resumen_admin["enviados"]
            for _ in range(resumen_admin["enviados"]):
                _imprimir("  → aviso admin enviado")
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
