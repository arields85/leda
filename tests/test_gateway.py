"""Pruebas del webhook.

Lo que importa acá no es que responda bien, sino que el canal determine el
sombrero y que un desconocido no obtenga información.
"""

from __future__ import annotations

from contextlib import contextmanager, nullcontext

import pytest
from fastapi.testclient import TestClient

from prisma import gateway
from prisma.db import admin
from prisma.llm import ProveedorGuionado, Respuesta


@pytest.fixture
def cliente(corework, conn, monkeypatch):
    import dataclasses

    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    monkeypatch.setattr(
        "prisma.llm.desde_base",
        lambda cur, ws, key: ProveedorGuionado([Respuesta(texto="Anotado.")]))
    return TestClient(gateway.app)


def _update(user_id: int, texto: str = "hola", chat: int | None = None):
    return {"message": {"message_id": 1, "text": texto,
                        "chat": {"id": chat or user_id},
                        "from": {"id": user_id}}}


def test_rechaza_sin_secreto(cliente):
    r = cliente.post("/telegram/corework", json=_update(9000))
    assert r.status_code == 403


def test_espacio_inexistente(cliente):
    r = cliente.post("/telegram/otro", json=_update(9000),
                     headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})
    assert r.status_code == 404


def test_desconocido_no_recibe_nada(cliente, conn):
    r = cliente.post("/telegram/corework", json=_update(424242),
                     headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})
    assert r.status_code == 200          # ACK, pero sin respuesta
    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox")
        assert cur.fetchone()["n"] == 0
        cur.execute("select count(*) n from inbound_message")
        assert cur.fetchone()["n"] == 0


def test_integrante_conocido_deja_respuesta_en_la_cola(cliente, conn):
    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user "
                    "where nombre = 'Marcos Tarquini'")
        tg = cur.fetchone()["t"]

    r = cliente.post("/telegram/corework", json=_update(tg, "¿qué tengo?"),
                     headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select texto from inbound_message")
        assert cur.fetchone()["texto"] == "¿qué tengo?"
        cur.execute("select cuerpo, estado from message_outbox")
        fila = cur.fetchone()
        assert fila["cuerpo"] == "Anotado."
        assert fila["estado"] == "listo"


def test_webhook_mantiene_typing_solo_durante_el_turno(
        cliente, conn, monkeypatch):
    eventos = []

    @contextmanager
    def activo(token, chat_id):
        eventos.append(("inicio", chat_id))
        try:
            yield
        finally:
            eventos.append(("fin", chat_id))

    monkeypatch.setattr(gateway, "mantener_chat_activo", activo)
    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user "
                    "where nombre = 'Marcos Tarquini'")
        tg = cur.fetchone()["t"]

    r = cliente.post("/telegram/corework", json=_update(tg, "hola", chat=812),
                     headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})

    assert r.status_code == 200
    assert eventos == [("inicio", 812), ("fin", 812)]
    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox")
        assert cur.fetchone()["n"] == 1


def test_bot_de_administracion_no_atiende_al_equipo(cliente, conn):
    """Marcos es integrante, no administrador: por el canal de administración
    no existe."""
    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user "
                    "where nombre = 'Marcos Tarquini'")
        tg = cur.fetchone()["t"]

    r = cliente.post("/telegram/admin", json=_update(tg, "cambiá el modelo"),
                     headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select count(*) n from audit_log where accion = 'mensaje_admin'")
        assert cur.fetchone()["n"] == 0
