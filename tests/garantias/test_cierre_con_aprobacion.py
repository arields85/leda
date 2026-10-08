"""El cierre con una aprobación ya dada (porción 3b de la C-3; mecánica §5; constitución §11).

Lo que se prueba acá es la cocina (`herramientas.cerrar_tarea_aprobada`), no la conversación: una
aprobación que no alcanzó para cerrar queda anotada, y el sistema cierra la tarea sólo cuando la
comprobación de siempre (`motivo_no_cierra_tarea`) ya no encuentra nada que falte.

- Sin una aprobación de quien revisa ese trabajo, nada se cierra: Leda nunca aprueba.
- La corre sólo quien aprueba ese trabajo; nadie más puede cerrarla en su nombre.
- Con una dependencia bloqueante abierta, o un bloqueo, no se cierra; resuelto eso, sí, con un
  evento del sistema que nombra la aprobación, y nadie tiene que volver a aprobarla.
- Un pedido de cambios posterior deja la aprobación sin efecto.
"""

from __future__ import annotations

import pytest

from leda import herramientas as H
from leda.autoridad import Canal, Denegado, identificar
from leda.db import admin, espacio


def _membresia(cur, ws: str, nombre: str) -> str:
    cur.execute("""select m.id from membership m join app_user u on u.id = m.app_user_id
                    where m.workspace_id = %s and u.nombre = %s""", (ws, nombre))
    return str(cur.fetchone()["id"])


def _quien(cur, ws: str, nombre: str):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _tarea(cur, ws: str, titulo: str, persona: str, estado: str) -> str:
    """Una tarea sin evidencia pedida, con su criterio, en `estado`."""
    cur.execute("""insert into objective (workspace_id, tipo, titulo)
                   values (%s, 'operativo', 'Objetivo de prueba') returning id""", (ws,))
    objetivo = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, criterio_aceptacion)
           values (%s, %s, %s, (select area_id from membership where id = %s), %s,
                   'Tablero cerrado y probado') returning id""",
        (ws, objetivo, titulo, _membresia(cur, ws, persona), _membresia(cur, ws, persona)))
    tarea = str(cur.fetchone()["id"])
    for anterior, nuevo in (("asignada", "en_curso"), ("en_curso", "en_revision")):
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind)
                       values (%s, %s, %s, 'persona')""", (tarea, anterior, nuevo))
        if nuevo == estado:
            break
    return tarea


def _decision(cur, ws: str, tarea: str, decision: str, quien: str = "Ismael Soschinski"):
    cur.execute("""insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                         aprobador_membership_id, decision)
                   values (%s, 'tarea', %s, %s, %s)""",
                (ws, tarea, _membresia(cur, ws, quien), decision))


def _estado(conn, tarea: str) -> str:
    with admin(conn) as cur:
        cur.execute("select estado::text e from task where id = %s", (tarea,))
        estado = cur.fetchone()["e"]
    conn.commit()
    return estado


def _cerrar(conn, ws: str, tarea: str, nombre: str = "Ismael Soschinski") -> dict:
    with espacio(conn, ws) as cur:
        r = H.ejecutar(cur, _quien(cur, ws, nombre), "cerrar_tarea_aprobada", {"tarea_id": tarea})
    conn.commit()
    return r


@pytest.fixture
def entregada(corework, conn) -> tuple[str, str]:
    """Una tarea de Mariano en revisión (lo aprueba Ismael) que espera, con una dependencia
    bloqueante, otra de Lucas en curso."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws, "Cablear el tablero", "Mariano Naim", "en_revision")
        origen = _tarea(cur, ws, "Cambiar el switch", "Lucas Natuche", "en_curso")
        cur.execute("""insert into dependency (workspace_id, origen_task_id, destino_task_id,
                                               tipo)
                       values (%s, %s, %s, 'bloqueante')""", (ws, origen, tarea))
    conn.commit()
    return tarea, origen


def _terminar_el_origen(conn, origen: str) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind, motivo)
                       values (%s, 'en_curso', 'cancelada', 'persona', 'ya no hace falta')""",
                    (origen,))
    conn.commit()


def test_sin_una_aprobacion_nada_se_cierra(corework, conn, entregada):
    tarea, origen = entregada
    _terminar_el_origen(conn, origen)
    r = _cerrar(conn, corework.workspace_id, tarea)
    assert r["cerrada"] is False
    assert _estado(conn, tarea) == "en_revision"


def test_solo_quien_aprueba_ese_trabajo_lo_corre(corework, conn, entregada):
    tarea, origen = entregada
    with admin(conn) as cur:
        _decision(cur, corework.workspace_id, tarea, "aprobado")
    conn.commit()
    _terminar_el_origen(conn, origen)
    with pytest.raises(Denegado):
        _cerrar(conn, corework.workspace_id, tarea, "Marcos Tarquini")
    conn.rollback()
    assert _estado(conn, tarea) == "en_revision"


def test_con_la_dependencia_abierta_no_se_cierra_y_resuelta_se_cierra_sola(corework, conn,
                                                                           entregada):
    ws = corework.workspace_id
    tarea, origen = entregada
    with admin(conn) as cur:
        _decision(cur, ws, tarea, "aprobado")
    conn.commit()
    r = _cerrar(conn, ws, tarea)
    assert r["cerrada"] is False and "dependencias bloqueantes" in r["falta"]
    assert _estado(conn, tarea) == "en_revision"

    _terminar_el_origen(conn, origen)
    r = _cerrar(conn, ws, tarea)
    assert r["cerrada"] is True
    assert _estado(conn, tarea) == "terminada"
    with admin(conn) as cur:
        cur.execute("""select actor_kind::text actor, motivo from task_state_event
                        where task_id = %s and estado_nuevo = 'terminada'""", (tarea,))
        evento = cur.fetchone()
        cur.execute("select count(*) n from approval where sujeto_id = %s", (tarea,))
        aprobaciones = cur.fetchone()["n"]
    conn.commit()
    assert evento["actor"] == "sistema" and r["aprobacion_id"] in evento["motivo"]
    assert aprobaciones == 1                      # nadie tuvo que volver a aprobarla
    # Ya cerrada, otra vuelta no hace nada.
    assert _cerrar(conn, ws, tarea)["cerrada"] is False


def test_un_bloqueo_abierto_no_deja_cerrarla(corework, conn, entregada):
    ws = corework.workspace_id
    tarea, origen = entregada
    _terminar_el_origen(conn, origen)
    with admin(conn) as cur:
        _decision(cur, ws, tarea, "aprobado")
        cur.execute("""insert into blocker (workspace_id, task_id, causa)
                       values (%s, %s, 'falta el repuesto')""", (ws, tarea))
    conn.commit()
    assert _cerrar(conn, ws, tarea)["cerrada"] is False
    assert _estado(conn, tarea) == "en_revision"


def test_un_pedido_de_cambios_posterior_deja_sin_efecto_la_aprobacion(corework, conn,
                                                                      entregada):
    ws = corework.workspace_id
    tarea, origen = entregada
    with admin(conn) as cur:
        _decision(cur, ws, tarea, "aprobado")
        _decision(cur, ws, tarea, "rechazado")
    conn.commit()
    _terminar_el_origen(conn, origen)
    assert _cerrar(conn, ws, tarea)["cerrada"] is False
    assert _estado(conn, tarea) == "en_revision"
