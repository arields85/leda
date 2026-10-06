"""Menú de acciones de una tarea (T2, `leda-orienta`; ADR 0007, diseño
§4.6).

Tocar una tarea ofrece sólo lo que la persona puede hacer con ella, según su
estado y su relación (responsable, aprobador de la cadena del espacio, otra
persona del equipo) -- calculado por código, nunca por el modelo. Se llega al
menú tocando una opción de `ofrecer_opciones` (T1) con `accion: "menu"`: el
mecanismo que reutilizará T3 para listar tareas como botones.

Las pruebas que abrían el menú tocando por `gateway` se retiraron con los flujos
A y B (E3-4); quedan las que prueban el cálculo directo (`menu_tarea.calcular_menu`).
"""

from __future__ import annotations

from leda.autoridad import Canal, identificar
from leda.db import admin, espacio


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _tarea(cur, ws, *, titulo="Programar HMI línea 2", area="ot",
          persona="Nahuel Gimenez", estado="asignada"):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Objetivo de prueba') returning id""", (ws,))
    obj = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, criterio_aceptacion,
                             evidencia_requerida)
           values (%s, %s, %s,
                   (select id from area where workspace_id = %s and slug = %s),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                    'Criterio de prueba', array['explicacion'])
           returning id""",
        (ws, obj, titulo, ws, area, ws, persona))
    t = cur.fetchone()["id"]
    cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                "values (%s, %s, 'leda')", (t, estado))
    return str(t)


def test_menu_responsable_terminada(conn, corework):
    """Una tarea terminada o cancelada ya no es "activa": `ofrecer_opciones`
    (T1) no la ofrece para abrir su menú por HTTP -- ese es el único camino
    de entrada que existe hoy, antes de T3 -- así que esto prueba el cálculo
    determinístico (`menu_tarea.calcular_menu`) directo, no el toque de
    punta a punta como las demás variantes de este test."""
    from leda import menu_tarea as M

    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, uri)
               values (%s, %s, 'explicacion', 'listo')""", (ws, tid))
        cur.execute(
            """insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                     aprobador_membership_id, decision)
               values (%s, 'tarea', %s,
                       (select m.id from membership m join app_user u on u.id = m.app_user_id
                         where m.workspace_id = %s and u.nombre = 'Marcos Tarquini'),
                       'aprobado')""",
            (ws, tid, ws))
        cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                    "values (%s, 'terminada', 'leda')", (tid,))
    conn.commit()

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        menu = M.calcular_menu(cur, quien, tid)
    assert [a.etiqueta for a in menu.acciones] == ["Ver detalle"]


def test_menu_responsable_en_revision_ofrece_cerrar_tarea_si_ya_alcanza(
        conn, corework):
    """ADR 0008, hallazgo 5 (sesión 2 por Telegram, 2026-09-27): si la
    aprobación llegó antes de que se completara otra condición de cierre --
    acá, la evidencia -- y esa condición se resuelve después, el responsable
    tiene que poder cerrar tocando, no sólo escribiendo."""
    from leda import menu_tarea as M

    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, uri)
               values (%s, %s, 'explicacion', 'ya está')""", (ws, tid))
        cur.execute(
            """insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                     aprobador_membership_id, decision)
               values (%s, 'tarea', %s,
                       (select m.id from membership m join app_user u
                          on u.id = m.app_user_id
                         where m.workspace_id = %s and u.nombre = 'Marcos Tarquini'),
                       'aprobado')""",
            (ws, tid, ws))
    conn.commit()

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        menu = M.calcular_menu(cur, quien, tid)
    assert [a.etiqueta for a in menu.acciones] == [
        "Ver detalle", "Adjuntar evidencia", "Cerrar tarea"]
