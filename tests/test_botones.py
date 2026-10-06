"""Pruebas de los botones: de la cola a Telegram y del toque de vuelta.

Un botón cierra el circuito que las acciones pendientes dejaron preparado. Lo
que se prueba acá es el camino completo — que el mensaje salga con sus
opciones dibujadas, y que el toque de la persona correcta ejecute la acción
que estaba congelada.

El toque de la persona equivocada es el caso que más importa: en un grupo el
botón lo ve todo el equipo.

El toque entraba por `gateway` y se retiró con los flujos A y B (E3-4); quedan las
pruebas de la salida, que dibuja las opciones al despachar.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from leda import pendientes as P
from leda.autoridad import Canal, identificar
from leda.calendario import Calendario
from leda.db import espacio
from leda.despachador import TransporteDePrueba, despachar
from leda.salida import ETIQUETA_CANCELAR, ETIQUETA_CONFIRMAR

BA = ZoneInfo("America/Argentina/Buenos_Aires")

AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _tarea(cur, ws, persona="Marcos Tarquini"):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Integrar comprimidora 3') returning id""",
        (ws,))
    obj = cur.fetchone()["id"]
    cur.execute("set local role leda_admin")
    # Por la vista y no por app_user: bajo el rol del agente esa tabla no se
    # toca, que es exactamente lo que el esquema quiere.
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, fecha_objetivo,
                             criterio_aceptacion, evidencia_requerida)
           values (%s, %s, 'Programar PLC',
                   (select id from area where workspace_id = %s and slug = 'ot'),
                   (select membership_id from integrante where nombre = %s),
                   '2026-08-14', 'PLC probado', array['resultado_de_prueba'])
           returning id""",
        (ws, obj, ws, persona))
    t = cur.fetchone()["id"]
    cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                "values (%s, 'asignada', 'leda')", (t,))
    cur.execute("set local role leda_app")
    return str(t)


# ---------------------------------------------------------------------------
# Salida: el mensaje sale con sus botones
# ---------------------------------------------------------------------------

def test_un_mensaje_con_accion_pendiente_sale_con_sus_opciones(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        p = P.registrar(
            cur, quien, herramienta="cambiar_fecha",
            args={"tarea_id": _tarea(cur, ws), "fecha_objetivo": "2026-08-20"},
            resumen="mover la fecha al 20/08",
            vence_en=AHORA + timedelta(days=1), chat_id=500)

        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, cuerpo, estado, dedupe_key,
                  es_respuesta, programado_para, pending_action_id)
               values (%s, 500, 'Confirmame esto', 'listo', 'b1', true, %s, %s)""",
            (ws, AHORA, p.id))

        cal = Calendario.desde_base(cur, ws)
        transporte = TransporteDePrueba()
        despachar(cur, ws, transporte, cal, AHORA)

        assert transporte.enviados[0].texto == "Confirmame esto"
        etiquetas = [b.etiqueta for b in transporte.enviados[0].botones]
        assert etiquetas == [ETIQUETA_CONFIRMAR, ETIQUETA_CANCELAR]


def test_un_mensaje_comun_sale_sin_botones(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, cuerpo, estado, dedupe_key,
                  es_respuesta, programado_para)
               values (%s, 500, 'buen día', 'listo', 'b2', true, %s)""",
            (ws, AHORA))

        cal = Calendario.desde_base(cur, ws)
        transporte = TransporteDePrueba()
        despachar(cur, ws, transporte, cal, AHORA)

        assert transporte.enviados[0].botones == []
