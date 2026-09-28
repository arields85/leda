"""Fixtures y helpers compartidos por `test_alta_correo_flujo.py` (G1b/G1b2)
y `test_alta_correo_existente.py` (G1c/G1c2).

G1c2, ítem 5: antes, `test_alta_correo_existente.py` importaba estas piezas
directamente desde `test_alta_correo_flujo.py`. Vivir acá, en un módulo sin
pruebas propias, deja claro que son infraestructura compartida y no ata un
archivo de pruebas al otro.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import alta_correo as AC
from prisma import gateway
from prisma.db import admin, espacio
from prisma.llm import ProveedorGuionado, Respuesta

# UTC 14:00 -> America/Argentina/Buenos_Aires 11:00 -> "Buen día" (5-12).
AHORA = datetime(2028, 3, 15, 14, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Doble del puerto de correo
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class EnvioRegistrado:
    destinatario: str
    asunto: str
    cuerpo: str
    nombre_preferido: str
    enlace: str
    vence_en: datetime


class DobleEnvioCorreo:
    """Registra cada envío; puede fallar a pedido -- nunca manda nada real."""

    def __init__(self, falla: bool = False):
        self.enviados: list[EnvioRegistrado] = []
        self.falla = falla

    def enviar_verificacion(self, *, destinatario, asunto, cuerpo, nombre_preferido,
                            enlace, vence_en):
        from prisma import alta_correo_flujo as ACF

        if self.falla:
            raise ConnectionError("el doble está configurado para fallar")
        self.enviados.append(EnvioRegistrado(
            destinatario, asunto, cuerpo, nombre_preferido, enlace, vence_en))
        return ACF.Recibo(message_id="doble-msg", thread_id="doble-thread")


def _token_de_enlace(enlace: str) -> str:
    return enlace.rsplit("pv_", 1)[1]


# ---------------------------------------------------------------------------
# Fixtures y helpers -- mundo ligero (`intake_world`, gente ya vinculada)
# ---------------------------------------------------------------------------


def _no_debe_llamarse(*_args, **_kwargs):
    raise AssertionError("no debía llamarse al proveedor de LLM: el control "
                         "de alta con correo tiene que interceptar antes")


@pytest.fixture
def cliente(intake_world, conn, monkeypatch):
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    monkeypatch.setattr("prisma.llm.desde_base", _no_debe_llamarse)
    monkeypatch.setattr(gateway, "_bot_username", lambda slug: "prisma_bot")
    # Sólo lo necesita el camino que SÍ llega a `_turno` (mantiene el
    # indicador de "escribiendo" con el token del bot): las pruebas del
    # control de alta con correo nunca deberían llegar hasta ahí, pero
    # `test_sin_ciclo_abierto_el_turno_llega_al_agente` sí, a propósito.
    monkeypatch.setenv("PRISMA_BOT_TOKEN_NORTH-LAB", "prueba:token")
    return TestClient(gateway.app)


@pytest.fixture
def con_agente(cliente, monkeypatch):
    """Variante donde SÍ hay un agente conversacional detrás -- para probar
    que, una vez `active`, la conversación de negocio vuelve a llegar."""
    monkeypatch.setattr(
        "prisma.llm.desde_base",
        lambda cur, ws, key: ProveedorGuionado([Respuesta(texto="Anotado.")]))
    return cliente


def _habilitar(conn, ws: str) -> None:
    with admin(conn) as cur:
        cur.execute(
            "insert into workspace_setting (workspace_id, clave, valor) "
            "values (%s, %s, 'true')", (ws, AC.CLAVE_HABILITADO))
    conn.commit()


def _sender(conn, ws: str, monkeypatch, doble) -> None:
    from prisma import alta_correo_flujo as ACF

    monkeypatch.setattr(ACF, "obtener_emisor_configurado",
                        lambda cur, workspace_id: doble)


def _post(cliente, texto, user_id, slug="north-lab"):
    # `type: "private"` porque todas estas pruebas simulan un chat directo
    # con la persona -- Telegram siempre lo manda; `gate()` (G1b2, ítem 1)
    # pasó a exigirlo explícitamente. Las pruebas de grupo usan `_post_grupo`.
    return cliente.post(
        f"/telegram/{slug}",
        json={"message": {"message_id": 1, "text": texto,
                          "chat": {"id": user_id, "type": "private"},
                          "from": {"id": user_id}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _post_grupo(cliente, texto, user_id, chat_id, slug="north-lab"):
    """Mismo mensaje, pero en un chat de grupo -- `chat_id` (el grupo) puede
    ser distinto del `from.id` (quien escribió)."""
    return cliente.post(
        f"/telegram/{slug}",
        json={"message": {"message_id": 1, "text": texto,
                          "chat": {"id": chat_id, "type": "group"},
                          "from": {"id": user_id}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _post_toque(cliente, token, user_id, slug="north-lab"):
    return cliente.post(
        f"/telegram/{slug}",
        json={"callback_query": {"id": "cb1", "data": f"p:{token}",
                                 "from": {"id": user_id},
                                 "message": {"chat": {"id": user_id}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _membership_id(intake_world, workspace_key: str, persona: str) -> str:
    return intake_world[workspace_key]["people"][persona]["membership_id"]


def _abrir_awaiting_email(conn, ws: str, m: str, ahora=AHORA) -> None:
    with espacio(conn, ws) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=ahora)
        AC.transicionar(cur, m, "awaiting_email", ahora=ahora)
    conn.commit()


def _estado(conn, ws: str, m: str) -> dict | None:
    with espacio(conn, ws) as cur:
        return AC.estado(cur, m)


def _outbox_textos(conn, chat_id: int) -> list[str]:
    with admin(conn) as cur:
        cur.execute(
            "select cuerpo from message_outbox where chat_id = %s "
            "order by programado_para, id", (chat_id,))
        return [f["cuerpo"] for f in cur.fetchall()]


def _token_boton(conn, ws: str, m: str, etiqueta: str) -> str | None:
    with admin(conn) as cur:
        cur.execute(
            """select o.token from pending_action_option o
                 join pending_action p on p.id = o.pending_action_id
                where p.workspace_id = %s and p.membership_id = %s
                  and o.etiqueta = %s and o.activa and p.estado = 'esperando'
                order by p.creado_en desc limit 1""",
            (ws, m, etiqueta))
        fila = cur.fetchone()
        return fila["token"] if fila else None


def _avisos(conn, ws: str) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(
            "select tipo, texto_saneado from aviso_administrativo "
            "where workspace_id = %s", (ws,))
        return cur.fetchall()
