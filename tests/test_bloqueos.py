"""Ciclo de vida de un bloqueo: abrir, resolver y escalar por antigüedad.

Implementa la sección 8 de `nucleo/mecanica-pm.md`. Antes de esto un bloqueo
se abría y quedaba abierto para siempre: ninguna ruta de código escribía
`resuelto_en`, `resolucion`, `escalado_a` ni `escalado_en`.

El escalamiento por antigüedad era de la escalera vieja de `leda` (`escalera.py`), retirada
con sus pruebas en la E3-7: la persecución de un bloqueo vuelve con el motor (ADR 0017, 3a).
"""

from __future__ import annotations

import pytest

from leda import herramientas as H
from leda.autoridad import Canal, Denegado, identificar
from leda.db import admin, espacio


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _membership(cur, ws, nombre):
    cur.execute(
        """select m.id from membership m join app_user u on u.id = m.app_user_id
            where m.workspace_id = %s and u.nombre = %s""", (ws, nombre))
    return cur.fetchone()["id"]


def _tarea(cur, ws, *, area="ot", persona="Marcos Tarquini",
           estado_inicial="asignada"):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Integrar comprimidora 3') returning id""", (ws,))
    obj = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, fecha_objetivo,
                             criterio_aceptacion, evidencia_requerida)
           values (%s, %s, 'Programar PLC',
                   (select id from area where workspace_id = %s and slug = %s),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                    '2026-08-14', 'Resultado verificado', array['resultado_de_prueba'])
           returning id""",
        (ws, obj, ws, area, ws, persona))
    t = cur.fetchone()["id"]
    # `clock_timestamp()` y no `now()`: dos inserts en la misma transacción
    # comparten el `now()` de la transacción, y el orden de `task_state_event`
    # —de qué depende cuál es "el estado previo"— quedaría indefinido.
    cur.execute(
        "insert into task_state_event (task_id, estado_nuevo, actor_kind, at) "
        "values (%s, %s, 'leda', clock_timestamp())", (t, estado_inicial))
    return str(t)


def _bloquear(cur, ws, tarea_id, *, causa="falta el switch en sala",
              abierto_por=None, abierto_en=None):
    cur.execute(
        """insert into blocker (workspace_id, task_id, causa, abierto_por, abierto_en)
           values (%s, %s, %s, %s, coalesce(%s, now())) returning id""",
        (ws, tarea_id, causa, abierto_por, abierto_en))
    bid = cur.fetchone()["id"]
    cur.execute(
        """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                         actor_kind, motivo, at)
           values (%s, (select estado from task where id = %s), 'bloqueada',
                   'sistema', %s, clock_timestamp())""",
        (tarea_id, tarea_id, causa))
    return str(bid)


# ---------------------------------------------------------------------------
# T1 — resolver_bloqueo
# ---------------------------------------------------------------------------

def test_resolver_bloqueo_devuelve_la_tarea_al_estado_previo(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado_inicial="en_curso")
        bid = _bloquear(cur, ws, tid)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "resolver_bloqueo",
                       {"bloqueo_id": bid, "resolucion": "llegó el switch"}, ya_confirmada=True)
        assert r == {"resuelto": True, "tarea_desbloqueada": True}

        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"

        cur.execute("select resuelto_en, resolucion from blocker where id = %s", (bid,))
        f = cur.fetchone()
        assert f["resuelto_en"] is not None
        assert f["resolucion"] == "llegó el switch"


def test_resolver_bloqueo_con_otro_abierto_no_saca_a_la_tarea_de_bloqueada(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado_inicial="en_curso")
        b1 = _bloquear(cur, ws, tid, causa="falta el switch")
        cur.execute(
            "insert into blocker (workspace_id, task_id, causa) values (%s, %s, %s)",
            (ws, tid, "falta el plano"))

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "resolver_bloqueo",
                       {"bloqueo_id": b1, "resolucion": "llegó el switch"}, ya_confirmada=True)
        assert r["tarea_desbloqueada"] is False

        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "bloqueada"


def test_resolver_bloqueo_requiere_ser_responsable_quien_lo_abrio_o_escalado(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        bid = _bloquear(cur, ws, tid)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ariel De Simone", ws)   # ajeno a la tarea
        with pytest.raises(Denegado):
            H.ejecutar(cur, quien, "resolver_bloqueo",
                       {"bloqueo_id": bid, "resolucion": "listo"}, ya_confirmada=True)


def test_resolver_bloqueo_lo_puede_quien_lo_abrio_aunque_no_sea_el_responsable(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        ariel_mid = _membership(cur, ws, "Ariel De Simone")
        bid = _bloquear(cur, ws, tid, abierto_por=ariel_mid)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ariel De Simone", ws)
        r = H.ejecutar(cur, quien, "resolver_bloqueo",
                       {"bloqueo_id": bid, "resolucion": "listo"}, ya_confirmada=True)
        assert r["resuelto"] is True


def test_resolver_bloqueo_lo_puede_a_quien_se_escalo(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        ismael_mid = _membership(cur, ws, "Ismael Soschinski")
        bid = _bloquear(cur, ws, tid)
        cur.execute(
            "update blocker set escalado_a = %s, escalado_en = now() where id = %s",
            (ismael_mid, bid))

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        r = H.ejecutar(cur, quien, "resolver_bloqueo",
                       {"bloqueo_id": bid, "resolucion": "lo resolvió dirección"}, ya_confirmada=True)
        assert r["resuelto"] is True


def test_resolver_bloqueo_exige_contar_la_resolucion(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        bid = _bloquear(cur, ws, tid)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        with pytest.raises(Denegado):
            H.ejecutar(cur, quien, "resolver_bloqueo",
                       {"bloqueo_id": bid, "resolucion": "   "}, ya_confirmada=True)


def test_resolver_bloqueo_inexistente_dice_que_no_existe(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "resolver_bloqueo",
                       {"bloqueo_id": "00000000-0000-0000-0000-000000000000",
                        "resolucion": "listo"}, ya_confirmada=True)
        assert "no existe" in r["error"]


def test_resolver_bloqueo_ya_resuelto_no_se_vuelve_a_resolver(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        bid = _bloquear(cur, ws, tid)
        cur.execute(
            "update blocker set resuelto_en = now(), resolucion = 'x' where id = %s",
            (bid,))

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "resolver_bloqueo",
                       {"bloqueo_id": bid, "resolucion": "otra vez"}, ya_confirmada=True)
        assert "ya estaba resuelto" in r["error"]


def test_resolver_bloqueo_de_otro_espacio_dice_que_no_existe(conn, intake_world):
    north = intake_world["north-lab"]
    west = intake_world["west-studio"]

    with admin(conn) as cur:
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, criterio_aceptacion)
               values (%s, %s, 'Task', %s, %s, 'done') returning id""",
            (north["id"], north["objectives"][0], north["areas"]["field"],
             north["people"]["Morgan Hale"]["membership_id"]))
        tid = cur.fetchone()["id"]
        cur.execute(
            "insert into task_state_event (task_id, estado_nuevo, actor_kind) "
            "values (%s, 'asignada', 'sistema')", (tid,))
        cur.execute(
            "insert into blocker (workspace_id, task_id, causa) values (%s, %s, %s) "
            "returning id", (north["id"], tid, "algo"))
        bid = cur.fetchone()["id"]
        cur.execute(
            """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                             actor_kind)
               values (%s, 'asignada', 'bloqueada', 'sistema')""", (tid,))

    with espacio(conn, west["id"]) as cur:
        quien = identificar(cur, west["people"]["Morgan Hale"]["telegram"],
                            Canal.ESPACIO, west["id"])
        r = H.ejecutar(cur, quien, "resolver_bloqueo",
                       {"bloqueo_id": str(bid), "resolucion": "x"}, ya_confirmada=True)
        assert "no existe" in r["error"]


def test_resolver_bloqueo_no_reingresa_a_bloqueada_si_ya_salio_por_otro_camino(
        corework, conn):
    """Corrección tras revisión (defecto 2).

    `actualizar_estado` no exige tener los bloqueos cerrados para salir de
    `bloqueada` — es una deuda conocida, `docs/STATUS.md` "Pendiente": no hay
    todavía un disparador que valide qué transiciones son legítimas. Si eso ya
    movió la tarea a otro estado, resolver el último bloqueo abierto no tiene
    que "volver" a ningún lado: la tarea ya no está en `bloqueada`, y antes de
    esta corrección la reingresaba a la fuerza (o rompía, según qué evento
    quedara último).
    """
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        bid = _bloquear(cur, ws, tid)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        H.ejecutar(cur, quien, "actualizar_estado",
                   {"tarea_id": tid, "estado": "en_curso"}, ya_confirmada=True)
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"

        r = H.ejecutar(cur, quien, "resolver_bloqueo",
                       {"bloqueo_id": bid, "resolucion": "listo"}, ya_confirmada=True)
        assert r == {"resuelto": True, "tarea_desbloqueada": False}

        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"

    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from task_state_event
                where task_id = %s and estado_nuevo = 'bloqueada'""", (tid,))
        assert cur.fetchone()["n"] == 1   # sólo el ingreso original


def test_estado_previo_a_bloqueo_respeta_el_aislamiento_entre_espacios(
        conn, intake_world):
    """Corrección tras revisión (defecto 3, invariante #1 de AGENTS.md).

    `estado_previo_a_bloqueo` es `security definer`. Que su dueño no salte la
    RLS (`leda_owner nobypassrls`) no alcanza como evidencia si nadie
    ejercita la política desde una sesión de otro espacio: se comprueba acá.
    """
    north = intake_world["north-lab"]
    west = intake_world["west-studio"]

    with admin(conn) as cur:
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, criterio_aceptacion)
               values (%s, %s, 'Task', %s, %s, 'done') returning id""",
            (north["id"], north["objectives"][0], north["areas"]["field"],
             north["people"]["Morgan Hale"]["membership_id"]))
        tid = cur.fetchone()["id"]
        cur.execute(
            "insert into task_state_event (task_id, estado_nuevo, actor_kind) "
            "values (%s, 'asignada', 'sistema')", (tid,))
        cur.execute(
            "insert into blocker (workspace_id, task_id, causa) values (%s, %s, %s)",
            (north["id"], tid, "algo"))
        cur.execute(
            """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                             actor_kind)
               values (%s, 'asignada', 'bloqueada', 'sistema')""", (tid,))

    with espacio(conn, west["id"]) as cur:
        cur.execute("select estado_previo_a_bloqueo(%s) as previo", (str(tid),))
        assert cur.fetchone()["previo"] is None


# ---------------------------------------------------------------------------
# T1 — correcciones a registrar_bloqueo
# ---------------------------------------------------------------------------

def test_registrar_bloqueo_en_tarea_inexistente_no_inserta(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "registrar_bloqueo",
                       {"tarea_id": "00000000-0000-0000-0000-000000000000",
                        "causa": "algo"}, ya_confirmada=True)
        assert "no existe" in r["error"]
        cur.execute("select count(*) n from blocker")
        assert cur.fetchone()["n"] == 0


def test_registrar_bloqueo_sobre_tarea_ya_bloqueada_no_duplica_el_evento(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        _bloquear(cur, ws, tid, causa="primero")

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        H.ejecutar(cur, quien, "registrar_bloqueo",
                   {"tarea_id": tid, "causa": "segundo"}, ya_confirmada=True)

        cur.execute("select count(*) n from blocker where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 2

    # task_state_event es append-only y leda_app no lo lee: se verifica
    # por la conexión administrativa, igual que el resto del esquema.
    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from task_state_event
                where task_id = %s and estado_nuevo = 'bloqueada'""", (tid,))
        assert cur.fetchone()["n"] == 1


def test_registrar_bloqueo_en_tarea_cancelada_se_rechaza(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        cur.execute(
            """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                             actor_kind, motivo)
               values (%s, 'asignada', 'cancelada', 'sistema', 'ya no aplica')""",
            (tid,))

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "registrar_bloqueo",
                       {"tarea_id": tid, "causa": "algo"}, ya_confirmada=True)
        assert "error" in r
        cur.execute("select count(*) n from blocker where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0
