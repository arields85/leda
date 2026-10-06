"""Modificar (T3, ADR 0005 decisión 1).

Tapping Modificar en la vista previa de una herramienta que escribe no aplica
nada: cierra esa propuesta y deja registrado, para esa persona y ese chat, que
el próximo mensaje de texto es una corrección. Ese próximo turno recibe la
propuesta anterior como contexto del servidor -- no como texto de la persona
-- y produce una vista previa nueva por el camino normal de siempre
(preparar → confirmar).

Ese recorrido pasaba por `gateway` y se retiró con los flujos A y B (E3-4); queda la
elección entre personas que guarda `pendientes.registrar`.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from leda import pendientes as P
from leda.autoridad import Canal, identificar
from leda.db import espacio

BA = ZoneInfo("America/Argentina/Buenos_Aires")

AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def test_elegir_entre_personas_no_lleva_los_botones_de_confirmacion(
        corework, conn):
    """`NecesitaElegir` (candidatos ambiguos) mantiene sus propios botones:
    un nombre por opción, no Confirmar/Modificar/Cancelar."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        p = P.registrar(
            cur, quien, herramienta="crear_tarea",
            args={"titulo": "Relevar tablero"}, resumen="¿a quién?",
            vence_en=AHORA + timedelta(hours=2), campo="responsable_membership_id",
            opciones=[("Marcos Tarquini", "m1"), ("Martín Forte", "m2")])

        cur.execute(
            """select etiqueta from pending_action_option
                where pending_action_id = %s order by orden""", (p.id,))
        etiquetas = [f["etiqueta"] for f in cur.fetchall()]
        assert etiquetas == ["Marcos Tarquini", "Martín Forte"]
