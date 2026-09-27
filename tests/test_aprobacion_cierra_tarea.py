"""Aprobar registra la aprobación y, si alcanza, cierra en el mismo acto
(ADR 0008).

Sesión 2 por Telegram real, 2026-09-27 (hallazgo 5): Ismael aprobó por el
menú de una tarea y Prisma contestó "se aprueba el trabajo", pero la tarea
quedó en `en_revision` -- `herramientas._aprobar_tarea` sólo insertaba en
`approval`, nunca corría `motivo_no_cierra_tarea` ni escribía en
`task_state_event`. El responsable de la tarea (Ariel) nunca se enteró, y su
menú en `en_revision` no ofrecía ningún botón para cerrarla.

Estas pruebas cubren la corrección: `aprobar_tarea` siempre escribe la
aprobación; si con ella alcanzan las condiciones de cierre
(`nucleo/mecanica-pm.md` §5), la misma llamada también cierra -- dos filas
distintas (`approval` y `task_state_event`), un solo acto -- y avisa al
responsable en cualquier caso. También cubre el mensaje posterior a
confirmar por botón, que antes repetía el texto de la vista previa en vez de
describir el resultado.
"""

from __future__ import annotations

import dataclasses
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from prisma import gateway
from prisma import herramientas as H
from prisma import pendientes as P
from prisma.autoridad import Canal, identificar
from prisma.db import admin, espacio
from prisma.llm import ProveedorGuionado, Respuesta

BA = ZoneInfo("America/Argentina/Buenos_Aires")
AHORA = datetime(2026, 9, 27, 10, 0, tzinfo=BA)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _telegram_id(cur, nombre) -> int:
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return cur.fetchone()["t"]


def _tarea(cur, ws, *, titulo="Programar HMI línea 2", persona="Nahuel Gimenez",
          estado="en_revision", criterio_aceptacion="Criterio de prueba",
          evidencia_requerida=("explicacion",)):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Objetivo de prueba') returning id""", (ws,))
    obj = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, criterio_aceptacion,
                             evidencia_requerida)
           values (%s, %s, %s,
                   (select id from area where workspace_id = %s and slug = 'ot'),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                   %s, %s)
           returning id""",
        (ws, obj, titulo, ws, ws, persona, criterio_aceptacion,
         list(evidencia_requerida) if evidencia_requerida else None))
    t = cur.fetchone()["id"]
    cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                "values (%s, %s, 'prisma')", (t, estado))
    return str(t)


def _evidencia(cur, ws, tarea_id, *, tipo="explicacion"):
    cur.execute(
        """insert into evidence (workspace_id, task_id, tipo, uri)
           values (%s, %s, %s, 'lista')""", (ws, tarea_id, tipo))


# ---------------------------------------------------------------------------
# El handler: aprueba y, si alcanza, cierra
# ---------------------------------------------------------------------------

def test_aprobar_tarea_cierra_cuando_las_condiciones_estan(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": tid},
                               ya_confirmada=True)

    assert resultado == {"aprobada": True, "cerrada": True, "falta": None,
                         "titulo": "Programar HMI línea 2"}

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "terminada"
        cur.execute("select count(*) n from approval where sujeto_id = %s", (tid,))
        assert cur.fetchone()["n"] == 1
        cur.execute(
            """select count(*) n from task_state_event
                where task_id = %s and estado_nuevo = 'terminada'""", (tid,))
        assert cur.fetchone()["n"] == 1

        cur.execute("select telegram_user_id from app_user where nombre = %s",
                   ("Nahuel Gimenez",))
        tg_nahuel = cur.fetchone()["telegram_user_id"]
        cur.execute(
            """select cuerpo from message_outbox
                where workspace_id = %s and chat_id = %s
               order by programado_para desc limit 1""", (ws, tg_nahuel))
        aviso = cur.fetchone()["cuerpo"]
    assert aviso == "Marcos Tarquini aprobó «Programar HMI línea 2»; quedó terminada."


def test_aprobar_tarea_registra_pero_no_cierra_si_falta_evidencia(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)   # sin evidencia
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": tid},
                               ya_confirmada=True)

    assert resultado == {"aprobada": True, "cerrada": False,
                         "falta": "Falta la evidencia requerida.",
                         "titulo": "Programar HMI línea 2"}

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"    # nada se cerró
        cur.execute("select count(*) n from approval where sujeto_id = %s", (tid,))
        assert cur.fetchone()["n"] == 1                     # pero sí se aprobó
        cur.execute(
            """select count(*) n from task_state_event
                where task_id = %s and estado_nuevo = 'terminada'""", (tid,))
        assert cur.fetchone()["n"] == 0

        cur.execute("select telegram_user_id from app_user where nombre = %s",
                   ("Nahuel Gimenez",))
        tg_nahuel = cur.fetchone()["telegram_user_id"]
        cur.execute(
            """select cuerpo from message_outbox
                where workspace_id = %s and chat_id = %s
               order by programado_para desc limit 1""", (ws, tg_nahuel))
        aviso = cur.fetchone()["cuerpo"]
    assert aviso == ("Marcos Tarquini aprobó «Programar HMI línea 2»; "
                     "para cerrarla falta: Falta la evidencia requerida.")


def test_aprobar_tarea_no_cierra_con_dependencia_bloqueante_sin_resolver(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Instalar tablero",
                        persona="Marcos Tarquini", estado="asignada")
        destino = _tarea(cur, ws, titulo="Programar HMI línea 3")
        _evidencia(cur, ws, destino)
        cur.execute(
            """insert into dependency (workspace_id, origen_task_id,
                                       destino_task_id, tipo)
               values (%s, %s, %s, 'bloqueante')""", (ws, origen, destino))
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": destino},
                               ya_confirmada=True)

    assert resultado["aprobada"] is True
    assert resultado["cerrada"] is False
    assert "dependencia" in resultado["falta"].lower()

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (destino,))
        assert cur.fetchone()["estado"] == "en_revision"
        cur.execute("select count(*) n from approval where sujeto_id = %s", (destino,))
        assert cur.fetchone()["n"] == 1


# ---------------------------------------------------------------------------
# El mensaje después de confirmar por botón describe el resultado
# ---------------------------------------------------------------------------

def _tocar(cliente, token, user_id):
    return cliente.post(
        "/telegram/corework",
        json={"callback_query": {
            "id": "cb1", "from": {"id": user_id}, "data": f"p:{token}",
            "message": {"message_id": 7, "chat": {"id": user_id}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _cliente(conn, monkeypatch):
    monkeypatch.setattr(gateway, "acusar_toque", lambda *a, **k: None)
    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    monkeypatch.setattr(
        "prisma.llm.desde_base",
        lambda cur, ws, key: ProveedorGuionado([Respuesta(texto="Anotado.")]))
    return TestClient(gateway.app)


def test_mensaje_post_confirmacion_aprobar_tarea_que_cierra(
        corework, conn, monkeypatch):
    cliente = _cliente(conn, monkeypatch)
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        _evidencia(cur, ws, tid)
    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        p = P.registrar(cur, marcos, herramienta="aprobar_tarea",
                        args={"tarea_id": tid}, resumen="aprobar",
                        vence_en=AHORA + timedelta(days=1), chat_id=500)
        token = P.opcion_por_etiqueta(cur, p.id, "Confirmar").token
        tg = _telegram_id(cur, "Marcos Tarquini")
    conn.commit()

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute(
            """select cuerpo from message_outbox
                where workspace_id = %s and chat_id = %s
               order by programado_para desc limit 1""", (ws, tg))
        cuerpo = cur.fetchone()["cuerpo"]
    assert cuerpo == "Listo: aprobaste «Programar HMI línea 2». Quedó terminada."


def test_mensaje_post_confirmacion_aprobar_tarea_que_no_cierra(
        corework, conn, monkeypatch):
    cliente = _cliente(conn, monkeypatch)
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)   # sin evidencia: no va a cerrar
    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        p = P.registrar(cur, marcos, herramienta="aprobar_tarea",
                        args={"tarea_id": tid}, resumen="aprobar",
                        vence_en=AHORA + timedelta(days=1), chat_id=500)
        token = P.opcion_por_etiqueta(cur, p.id, "Confirmar").token
        tg = _telegram_id(cur, "Marcos Tarquini")
    conn.commit()

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute(
            """select cuerpo from message_outbox
                where workspace_id = %s and chat_id = %s
               order by programado_para desc limit 1""", (ws, tg))
        cuerpo = cur.fetchone()["cuerpo"]
    assert cuerpo == ("Listo: aprobaste «Programar HMI línea 2»; para cerrarla "
                      "falta: Falta la evidencia requerida.")
    # Nunca "Estado actual: En revisión" -- la vista previa, no el resultado.
    assert "Estado actual" not in cuerpo


def test_mensaje_post_confirmacion_actualizar_estado(corework, conn, monkeypatch):
    cliente = _cliente(conn, monkeypatch)
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, persona="Marcos Tarquini", estado="asignada")
    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        p = P.registrar(cur, marcos, herramienta="actualizar_estado",
                        args={"tarea_id": tid, "estado": "en_revision"},
                        resumen="pasar a revisión",
                        vence_en=AHORA + timedelta(days=1), chat_id=500)
        token = P.opcion_por_etiqueta(cur, p.id, "Confirmar").token
        tg = _telegram_id(cur, "Marcos Tarquini")
    conn.commit()

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute(
            """select cuerpo from message_outbox
                where workspace_id = %s and chat_id = %s
               order by programado_para desc limit 1""", (ws, tg))
        cuerpo = cur.fetchone()["cuerpo"]
    assert cuerpo == "Listo: «Programar HMI línea 2» pasó a En revisión."
    # Nunca el estado viejo después de aplicar el cambio.
    assert "Asignada" not in cuerpo
