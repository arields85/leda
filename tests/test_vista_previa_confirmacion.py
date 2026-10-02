"""Propiedad central de ADR 0005 (decisión 1): ninguna de las 8 herramientas
que escriben cambia la base sin un Confirmar.

Para cada una: invocarla sin confirmar, a través del agente, dice deja la
base intacta y una sola acción pendiente con vista previa humana (con la
huella del estado leído); confirmarla la aplica una sola vez; y si el estado
cambió entre la vista previa y la confirmación -- acá, simulado con una
huella que no coincide, el mismo control que usa `gateway._toque` -- no se
aplica nada.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from leda import herramientas as H
from leda import pendientes as P
from leda.agente import responder
from leda.autoridad import Canal, identificar
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.llm import Llamada, ProveedorGuionado, Respuesta

BA = ZoneInfo("America/Argentina/Buenos_Aires")
AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _tarea(cur, ws, *, titulo="Programar PLC", area="ot",
           persona="Marcos Tarquini", estado_inicial="asignada"):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Integrar comprimidora 3') returning id""",
        (ws,))
    obj = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, fecha_objetivo,
                             criterio_aceptacion, evidencia_requerida)
           values (%s, %s, %s,
                   (select id from area where workspace_id = %s and slug = %s),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                    '2026-08-14', 'Resultado verificado', array['resultado_de_prueba'])
           returning id""",
        (ws, obj, titulo, ws, area, ws, persona))
    t = cur.fetchone()["id"]
    cur.execute(
        "insert into task_state_event (task_id, estado_nuevo, actor_kind, at) "
        "values (%s, %s, 'leda', clock_timestamp())", (t, estado_inicial))
    return str(t)


def _bloquear(cur, ws, tarea_id, *, causa="falta el switch en sala"):
    cur.execute(
        """insert into blocker (workspace_id, task_id, causa, abierto_en)
           values (%s, %s, %s, now()) returning id""",
        (ws, tarea_id, causa))
    bid = cur.fetchone()["id"]
    cur.execute(
        """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                         actor_kind, motivo, at)
           values (%s, (select estado from task where id = %s), 'bloqueada',
                   'sistema', %s, clock_timestamp())""",
        (tarea_id, tarea_id, causa))
    return str(bid)


def _dependencia_previa(cur, ws, origen, destino):
    cur.execute(
        """insert into dependency (workspace_id, origen_task_id, destino_task_id, tipo)
           values (%s, %s, %s, 'bloqueante') returning id""",
        (ws, origen, destino))
    return str(cur.fetchone()["id"])


def _propiedad(cur, ws, quien, herramienta, args, aplicado, *, chat_id=9100):
    """Ejercita la propiedad central para una herramienta que escribe."""
    cal = Calendario.desde_base(cur, ws)
    assert aplicado(cur) is False

    guion = [Respuesta(llamadas=[Llamada("c1", herramienta, dict(args))]),
             Respuesta(texto="listo")]
    r = responder(cur, quien, "hacé esto", ProveedorGuionado(guion), cal,
                  chat_id=chat_id, ahora=AHORA)

    assert r.confirmaciones == [herramienta]
    assert r.acciones == []
    assert aplicado(cur) is False, "no se aplicó nada sin confirmar"

    cur.execute(
        """select count(*) n from pending_action
            where herramienta = %s and estado = 'esperando'""", (herramienta,))
    assert cur.fetchone()["n"] == 1, "exactamente una acción pendiente"

    cur.execute(
        """select id, resumen, huella from pending_action
            where herramienta = %s and estado = 'esperando'""", (herramienta,))
    pendiente = cur.fetchone()
    assert "Todavía no se aplicó ningún cambio." in pendiente["resumen"]
    assert pendiente["huella"], "la vista previa guarda una huella del estado leído"

    # Si el estado cambió entre la vista previa y la confirmación (acá,
    # simulado con una huella que no coincide -- el mismo control que corre
    # `ejecutar` al confirmar de verdad), no se aplica nada.
    with pytest.raises(H.EstadoCambio):
        H.ejecutar(cur, quien, herramienta, args, ya_confirmada=True,
                  chat_id=chat_id, huella_previa="huella-que-no-coincide")
    assert aplicado(cur) is False, "una huella distinta no aplica el cambio"

    pid = str(pendiente["id"])
    confirmar = P.opcion_por_etiqueta(cur, pid, "Confirmar")
    resuelta = P.resolver(cur, confirmar.token, app_user_id=quien.app_user_id,
                          ahora=AHORA)
    assert resuelta is not None
    assert resuelta.huella == pendiente["huella"]

    H.ejecutar(cur, quien, resuelta.herramienta, resuelta.args,
              ya_confirmada=True, chat_id=chat_id, huella_previa=resuelta.huella)
    assert aplicado(cur) is True, "confirmar aplica el cambio"

    # El mismo botón, apretado de nuevo, no vuelve a ejecutar (el token ya se
    # usó: lo prueba a fondo tests/test_pendientes.py y tests/test_botones.py;
    # acá sólo se confirma que el efecto de negocio sigue aplicado una sola
    # vez).
    otra = P.resolver(cur, confirmar.token, app_user_id=quien.app_user_id,
                      ahora=AHORA)
    assert otra is None


# ---------------------------------------------------------------------------

def test_propiedad_registrar_bloqueo(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)

        def aplicado(cur):
            cur.execute("select count(*) n from blocker where task_id = %s", (tid,))
            return cur.fetchone()["n"] > 0

        _propiedad(cur, ws, quien, "registrar_bloqueo",
                  {"tarea_id": tid, "causa": "falta el switch en sala"}, aplicado)


def test_propiedad_resolver_bloqueo(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        bid = _bloquear(cur, ws, tid)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)

        def aplicado(cur):
            cur.execute("select resuelto_en from blocker where id = %s", (bid,))
            return cur.fetchone()["resuelto_en"] is not None

        _propiedad(cur, ws, quien, "resolver_bloqueo",
                  {"bloqueo_id": bid, "resolucion": "llegó el switch"}, aplicado)


def test_propiedad_actualizar_estado(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)

        def aplicado(cur):
            cur.execute("select estado from task where id = %s", (tid,))
            return cur.fetchone()["estado"] == "en_curso"

        _propiedad(cur, ws, quien, "actualizar_estado",
                  {"tarea_id": tid, "estado": "en_curso"}, aplicado)


def test_propiedad_crear_dependencia(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Relevar plano",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero",
                         persona="Marcos Tarquini")
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)

        def aplicado(cur):
            cur.execute(
                """select 1 from dependency
                    where origen_task_id = %s and destino_task_id = %s""",
                (origen, destino))
            return cur.fetchone() is not None

        _propiedad(cur, ws, quien, "crear_dependencia",
                  {"origen_tarea_id": origen, "destino_tarea_id": destino,
                   "tipo": "bloqueante"}, aplicado)


def test_propiedad_quitar_dependencia(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Relevar plano",
                        persona="Nahuel Gimenez")
        destino = _tarea(cur, ws, titulo="Cablear tablero",
                         persona="Marcos Tarquini")
        dep_id = _dependencia_previa(cur, ws, origen, destino)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)

        def aplicado(cur):
            cur.execute("select 1 from dependency where id = %s", (dep_id,))
            return cur.fetchone() is None    # "aplicado" acá es "ya no está"

        _propiedad(cur, ws, quien, "quitar_dependencia",
                  {"dependencia_id": dep_id}, aplicado)


def test_propiedad_adjuntar_evidencia(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)

        def aplicado(cur):
            cur.execute("select count(*) n from evidence where task_id = %s", (tid,))
            return cur.fetchone()["n"] > 0

        _propiedad(cur, ws, quien, "adjuntar_evidencia",
                  {"tarea_id": tid, "tipo": "resultado_de_prueba",
                   "descripcion": "PLC probado en banco"}, aplicado)


def test_propiedad_aprobar_tarea(corework, conn):
    """Marcos es el referente (aprobador) de Nahuel en OT.

    ADR 0009: "Aprobar" ahora exige `en_revision` con la evidencia ya
    registrada (decisión 2) -- esta prueba es sobre la propiedad de
    confirmación (nada se aplica antes de Confirmar), no sobre ese gate, así
    que se lo deja satisfecho de antemano."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Relevar plano", persona="Nahuel Gimenez",
                    estado_inicial="en_revision")
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, uri)
               values (%s, %s, 'resultado_de_prueba', 'ok')""", (ws, tid))
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)

        def aplicado(cur):
            cur.execute("select count(*) n from approval where sujeto_id = %s", (tid,))
            return cur.fetchone()["n"] > 0

        _propiedad(cur, ws, quien, "aprobar_tarea", {"tarea_id": tid}, aplicado)


def test_propiedad_crear_objetivo(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        titulo = "Objetivo de la propiedad de confirmación"

        def aplicado(cur):
            cur.execute(
                "select count(*) n from objective where workspace_id = %s and titulo = %s",
                (ws, titulo))
            return cur.fetchone()["n"] > 0

        _propiedad(cur, ws, quien, "crear_objetivo",
                  {"titulo": titulo, "tipo": "operativo"}, aplicado)
