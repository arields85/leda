"""Modo local (`local.Escucha`): despacho inmediato (ADR 0011).

`gateway.procesar_update` es la misma función que usa `servir`
(`tests/test_gateway.py`); acá sólo se prueba que `Escucha.recibir()`
despacha apenas procesa cada update del lote, sin esperar el resto de la
vuelta (`recibir_admin` + `tareas_de_fondo`).
"""

from __future__ import annotations

import contextlib

import pytest

from prisma import gateway
from prisma.db import admin
from prisma.despachador import TransporteDePrueba
from prisma.llm import ProveedorGuionado, Respuesta


class _Updates:
    """Doble de `httpx.Client` sólo para `getUpdates` -- nunca se usa para
    enviar nada: el envío real pasa por `Escucha.transporte`, reemplazado
    por un `TransporteDePrueba` en cada prueba."""

    def __init__(self, updates: list[dict]) -> None:
        self._updates = updates

    def get(self, url, params=None):
        return self

    def raise_for_status(self):
        return None

    def json(self):
        return {"result": self._updates}


@pytest.fixture
def escucha(corework, conn, monkeypatch):
    from prisma.local import Escucha

    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *a, **k: contextlib.nullcontext())
    monkeypatch.setattr(
        "prisma.llm.desde_base",
        lambda cur, ws, key: ProveedorGuionado([Respuesta(texto="Anotado.")]))

    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user "
                    "where nombre = 'Marcos Tarquini'")
        tg = cur.fetchone()["t"]

    update = {
        "update_id": 41,
        "message": {"message_id": 1, "text": "¿qué tengo?",
                    "chat": {"id": tg}, "from": {"id": tg}},
    }
    e = Escucha(conn, "corework", corework.workspace_id, "prueba:token",
               cliente=_Updates([update]))
    e.transporte = TransporteDePrueba()
    return e


def test_recibir_despacha_de_inmediato_sin_esperar_tareas_de_fondo(escucha, conn):
    n = escucha.recibir(espera=0)

    assert n == 1
    with admin(conn) as cur:
        cur.execute("select estado from message_outbox")
        fila = cur.fetchone()
        # Ya salió apenas terminó `recibir()` -- nadie corrió
        # `tareas_de_fondo()` (que en `una_vuelta()` va DESPUÉS de
        # `recibir()`/`recibir_admin()`) ni ningún tick de fondo.
        assert fila["estado"] == "enviado"
    assert len(escucha.transporte.enviados) == 1
    assert escucha.transporte.enviados[0].texto == "Anotado."


def test_despacho_inmediato_no_frena_la_escucha_si_falla(escucha, conn, monkeypatch):
    """Best-effort (ADR 0011): una falla al despachar temprano no puede
    tirar abajo `recibir()` -- el mensaje queda 'listo' para el próximo
    tick de fondo, que sigue siendo la red de contención."""
    def _revienta(*a, **k):
        raise RuntimeError("falla simulada del despacho inmediato")

    monkeypatch.setattr("prisma.local.despachar", _revienta)

    n = escucha.recibir(espera=0)

    assert n == 1
    with admin(conn) as cur:
        cur.execute("select estado from message_outbox")
        assert cur.fetchone()["estado"] == "listo"
