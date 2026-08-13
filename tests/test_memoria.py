"""Pruebas de la memoria conversacional.

Hasta acá cada turno empezaba con un solo mensaje: el que la persona acababa
de escribir. Prisma preguntaba algo y, cuando le contestaban, ya no sabía qué
había preguntado. Ningún intercambio de dos turnos podía funcionar.

Lo que se prueba: que el turno traiga lo que se dijeron hace un rato, que no
traiga lo ajeno, y que no se atribuya a sí misma nada que la persona no haya
recibido.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from prisma.agente import responder
from prisma.autoridad import Canal, identificar
from prisma.calendario import Calendario
from prisma.contexto import historial
from prisma.db import espacio
from prisma.llm import ProveedorGuionado, Respuesta

BA = ZoneInfo("America/Argentina/Buenos_Aires")
AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)
CHAT = 9004


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _entra(cur, ws, quien, texto, cuando, chat=CHAT):
    cur.execute(
        """insert into inbound_message (workspace_id, chat_id, app_user_id,
                                        texto, at)
           values (%s, %s, %s, %s, %s) returning id""",
        (ws, chat, quien.app_user_id, texto, cuando))
    return str(cur.fetchone()["id"])


def _salio(cur, ws, texto, cuando, chat=CHAT, estado="enviado"):
    cur.execute(
        """insert into message_outbox (workspace_id, chat_id, cuerpo, estado,
                                       dedupe_key, programado_para, enviado_en)
           values (%s, %s, %s, %s, %s, %s, %s)""",
        (ws, chat, texto, estado, f"k{cuando.timestamp()}{texto[:8]}", cuando,
         cuando if estado == "enviado" else None))


def _turno(cur, ws, quien, texto, cal, prov):
    return responder(cur, quien, texto, prov, cal, chat_id=CHAT, ahora=AHORA)


# ---------------------------------------------------------------------------

def test_el_turno_trae_lo_que_se_dijeron_antes(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)

        _entra(cur, ws, quien, "creá una tarea para Mar", AHORA - timedelta(minutes=3))
        _salio(cur, ws, "¿Marcos, Mariano o Martín?", AHORA - timedelta(minutes=2))

        prov = ProveedorGuionado([Respuesta(texto="Dale.")])
        _turno(cur, ws, quien, "Martín", cal, prov)

        _, mensajes = prov.recibidos[0]
        textos = [m["content"] for m in mensajes]
        assert "creá una tarea para Mar" in textos
        assert "¿Marcos, Mariano o Martín?" in textos
        assert textos[-1] == "Martín"


def test_el_mensaje_actual_no_viaja_dos_veces(corework, conn):
    """El gateway lo guarda antes de llamar al agente."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)

        eid = _entra(cur, ws, quien, "Martín", AHORA)

        prov = ProveedorGuionado([Respuesta(texto="Dale.")])
        responder(cur, quien, "Martín", prov, cal, chat_id=CHAT, ahora=AHORA,
                  entrante_id=eid)

        _, mensajes = prov.recibidos[0]
        assert [m["content"] for m in mensajes].count("Martín") == 1


def test_no_trae_la_conversacion_de_otro_chat(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)

        _entra(cur, ws, quien, "algo de otro chat", AHORA - timedelta(minutes=2),
               chat=7777)

        prov = ProveedorGuionado([Respuesta(texto="Dale.")])
        _turno(cur, ws, quien, "hola", cal, prov)

        _, mensajes = prov.recibidos[0]
        assert "algo de otro chat" not in [m["content"] for m in mensajes]


def test_no_trae_lo_de_ayer(corework, conn):
    """Una conversación vieja no es contexto: es ruido que confunde."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)

        _entra(cur, ws, quien, "lo de ayer", AHORA - timedelta(days=1))

        prov = ProveedorGuionado([Respuesta(texto="Dale.")])
        _turno(cur, ws, quien, "hola", cal, prov)

        _, mensajes = prov.recibidos[0]
        assert "lo de ayer" not in [m["content"] for m in mensajes]


def test_no_se_atribuye_lo_que_nunca_salio(corework, conn):
    """Un mensaje que quedó en la cola, la persona no lo leyó.

    Si Prisma lo diera por dicho, seguiría una conversación que del otro lado
    no ocurrió.
    """
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)

        _salio(cur, ws, "esto quedó trabado", AHORA - timedelta(minutes=2),
               estado="listo")

        prov = ProveedorGuionado([Respuesta(texto="Dale.")])
        _turno(cur, ws, quien, "hola", cal, prov)

        _, mensajes = prov.recibidos[0]
        assert "esto quedó trabado" not in [m["content"] for m in mensajes]


def test_el_historial_arranca_con_la_persona_y_alterna(corework, conn):
    """Los proveedores rechazan dos mensajes seguidos del mismo lado.

    Si Prisma escribió primero —un recordatorio de la cadencia— el historial
    empezaría por ella, y la llamada fallaría entera.
    """
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)

        _salio(cur, ws, "buen día, ¿cómo venís?", AHORA - timedelta(minutes=9))
        _salio(cur, ws, "te recuerdo la tarea", AHORA - timedelta(minutes=8))
        _entra(cur, ws, quien, "ahí voy", AHORA - timedelta(minutes=7))
        _entra(cur, ws, quien, "mañana la cierro", AHORA - timedelta(minutes=6))

        h = historial(cur, CHAT, AHORA)

        assert h[0]["role"] == "user"
        roles = [m["role"] for m in h]
        assert all(a != b for a, b in zip(roles, roles[1:])), roles
        assert "ahí voy" in h[0]["content"] and "mañana la cierro" in h[0]["content"]
