"""Toda operación de la cocina deja su fila en `audit_log` (Constitución §12).

Quién la originó, cuándo, sobre qué y con qué versión de las reglas del núcleo
(`nucleo_hash`) y del pack del espacio (`pack_hash`). La fila la escribe
`herramientas.ejecutar`, en la misma transacción que el efecto, para cualquier
canal que la llame: antes la escribía `agente.py`, que se borró con los flujos A
y B (E3-4), y desde entonces ninguna operación quedaba auditada.

La regla es la de siempre (`agente._ejecutar_una` y la confirmación por botón de
`gateway`, antes de `d002c99`):

- lo que se ejecutó, también una consulta, deja `herramienta:<nombre>`;
- lo que la cocina rechazó por una regla de negocio sin escribir nada deja
  `herramienta_rechazada:<nombre>`, nunca `herramienta:<nombre>`;
- lo que no llegó a ejecutarse (sin permiso, argumentos inválidos, esperando la
  confirmación de la persona) no deja ninguna.
"""

from __future__ import annotations

import psycopg
import pytest

from leda import herramientas as H
from leda.autoridad import Canal, identificar
from leda.db import admin, espacio


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _tarea(cur, ws, *, estado="asignada", persona="Marcos Tarquini"):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Integrar comprimidora 3') returning id""",
        (ws,))
    obj = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, fecha_objetivo,
                             criterio_aceptacion, evidencia_requerida)
           values (%s, %s, 'Programar PLC',
                   (select id from area where workspace_id = %s and slug = 'ot'),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                   '2026-08-14', 'Resultado verificado', array['resultado_de_prueba'])
           returning id""",
        (ws, obj, ws, ws, persona))
    t = cur.fetchone()["id"]
    cur.execute(
        "insert into task_state_event (task_id, estado_nuevo, actor_kind, at) "
        "values (%s, %s, 'leda', clock_timestamp())", (t, estado))
    return str(t)


def _filas(conn, *, ws=None):
    with admin(conn) as cur:
        cur.execute(
            """select workspace_id, actor_app_user_id, actor_kind, accion,
                      sujeto_tipo, sujeto_id, detalle, pack_hash, nucleo_hash
                 from audit_log
                where accion like 'herramienta%%'
                  and (%s::uuid is null or workspace_id = %s::uuid)
                order by at""", (ws, ws))
        return cur.fetchall()


def _pack_hash(conn, ws):
    with admin(conn) as cur:
        cur.execute("""select pack_hash from workspace_version
                        where workspace_id = %s order by version desc limit 1""",
                    (ws,))
        return cur.fetchone()["pack_hash"]


def test_una_operacion_con_efecto_deja_una_sola_fila_con_la_version_de_las_reglas(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    args = {"tarea_id": tid, "estado": "en_curso"}
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        with pytest.raises(H.NecesitaConfirmacion):
            H.ejecutar(cur, quien, "actualizar_estado", dict(args))
    assert _filas(conn) == [], "pedir la confirmación no ejecuta ni audita nada"

    with espacio(conn, ws) as cur:
        H.ejecutar(cur, quien, "actualizar_estado", dict(args), ya_confirmada=True)

    filas = _filas(conn)
    assert len(filas) == 1
    fila = filas[0]
    assert fila["accion"] == "herramienta:actualizar_estado"
    assert str(fila["workspace_id"]) == ws
    assert str(fila["actor_app_user_id"]) == quien.app_user_id
    assert fila["actor_kind"] == "persona", "la persona confirmó el efecto"
    assert (fila["sujeto_tipo"], str(fila["sujeto_id"])) == ("task", tid)
    assert fila["detalle"]["args"] == args
    assert fila["pack_hash"] == _pack_hash(conn, ws)
    assert fila["nucleo_hash"] and len(fila["nucleo_hash"]) == 64


def test_el_efecto_y_su_auditoria_van_en_la_misma_transaccion(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()

    class Revertir(Exception):
        pass

    with pytest.raises(Revertir):
        with espacio(conn, ws) as cur:
            quien = _quien(cur, "Marcos Tarquini", ws)
            H.ejecutar(cur, quien, "actualizar_estado",
                       {"tarea_id": tid, "estado": "en_curso"}, ya_confirmada=True)
            raise Revertir

    assert _filas(conn) == [], "si el efecto se revierte, su auditoría también"
    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"


def test_una_consulta_tambien_queda_auditada(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        H.ejecutar(cur, quien, "consultar_tareas", {})

    filas = _filas(conn)
    assert [f["accion"] for f in filas] == ["herramienta:consultar_tareas"]
    assert filas[0]["actor_kind"] == "leda", "nadie confirmó: la pidió Leda"
    assert str(filas[0]["actor_app_user_id"]) == quien.app_user_id
    assert filas[0]["sujeto_id"] is None
    assert filas[0]["pack_hash"] and filas[0]["nucleo_hash"]


def test_un_rechazo_de_negocio_se_audita_como_rechazo_y_no_como_ejecutado(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_curso")
    args = {"tarea_id": tid, "estado": "en_revision"}
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, quien, "actualizar_estado", dict(args))
    assert resultado["en_revision"] is False, "sin evidencia no se entrega"

    filas = _filas(conn)
    assert [f["accion"] for f in filas] == ["herramienta_rechazada:actualizar_estado"]
    assert filas[0]["detalle"]["args"] == args
    assert filas[0]["detalle"]["rechazo"]["falta_tipo"] == H.FALTA_EVIDENCIA_DE_ENTREGA
    assert filas[0]["pack_hash"] and filas[0]["nucleo_hash"]


def test_lo_que_no_se_ejecuto_no_deja_fila(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        with pytest.raises(H.Denegado):
            H.ejecutar(cur, quien, "no_existe", {})
        with pytest.raises(H.Denegado):
            H.ejecutar(cur, quien, "consultar_tareas", {"inventado": 1})
    assert _filas(conn) == []


def test_la_auditoria_de_un_espacio_no_se_ve_desde_otro(intake_world, conn):
    north = intake_world["north-lab"]
    west = intake_world["west-studio"]
    with espacio(conn, north["id"]) as cur:
        quien = identificar(cur, north["people"]["Sam North"]["telegram"],
                            Canal.ESPACIO, north["id"])
        H.ejecutar(cur, quien, "consultar_tareas", {})

    filas = _filas(conn)
    assert len(filas) == 1
    assert str(filas[0]["workspace_id"]) == north["id"]
    assert filas[0]["pack_hash"] == "hash-0", "el pack del espacio que operó"

    # La aplicación sólo escribe la auditoría: no la lee, desde ningún espacio.
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        with espacio(conn, west["id"]) as cur:
            cur.execute("select count(*) n from audit_log")

    # Y si alguna vez la leyera, la política de aislamiento deja ver sólo lo
    # del espacio activo. La concesión se deshace con la transacción.
    with conn.transaction(force_rollback=True):
        with conn.cursor() as cur:
            cur.execute("grant select on audit_log to leda_app")
            cur.execute("set local role leda_app")
            vistas = {}
            for ws in (west["id"], north["id"]):
                cur.execute("select set_config('leda.workspace_id', %s, true)", (ws,))
                cur.execute("""select count(*) n from audit_log
                                where accion like 'herramienta%%'""")
                vistas[ws] = cur.fetchone()["n"]
    assert vistas == {west["id"]: 0, north["id"]: 1}


def test_sin_los_archivos_del_nucleo_la_huella_no_se_inventa(tmp_path, monkeypatch):
    """Una huella calculada sobre un núcleo que no está registraría una versión de
    las reglas que no existe: falta un archivo y la huella falla, nunca en silencio."""
    import types

    from leda import versiones

    (tmp_path / "constitucion.md").write_text("reglas", encoding="utf-8")
    monkeypatch.setattr(versiones, "config", types.SimpleNamespace(nucleo=tmp_path))
    versiones.nucleo_hash.cache_clear()
    try:
        with pytest.raises(FileNotFoundError):
            versiones.nucleo_hash()
    finally:
        versiones.nucleo_hash.cache_clear()
