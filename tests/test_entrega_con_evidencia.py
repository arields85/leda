"""Entrega con evidencia y revisión (ADR 0009).

Sesión 2 por Telegram real, 2026-09-27 (hallazgos 8 y 9): Ariel tocó "Ya la
terminé" y la tarea pasó a `en_revision` sin ninguna evidencia, aunque su
política la exige (`evidencia_requerida = ['explicacion']`). Ismael, el
aprobador, aprobó a ciegas -- el menú y la herramienta se lo permitían -- y
el texto de la vista previa mostró "para cerrarla todavía falta: Falta la
evidencia requerida.", con la palabra "falta" repetida.

Estas pruebas cubren:
  1. `actualizar_estado(estado="en_revision")` pide la evidencia que falta
     -- nunca mueve la tarea sin ella -- y la registra junto con el cambio
     de estado cuando llega en el mismo pedido.
  2. `aprobar_tarea`/`pedir_cambios_tarea` sólo se permiten sobre una tarea
     `en_revision`; `aprobar_tarea` además exige que la evidencia ya esté.
  3. Quien aprueba se entera de la entrega con botones ("Aprobar"/"Pedir
     cambios"), no sólo el responsable con un aviso de texto.
  4. `pedir_cambios_tarea` devuelve la tarea a `en_curso` con el comentario
     como motivo, y avisa al responsable.
"""

from __future__ import annotations

from datetime import datetime, timezone

import psycopg
import pytest

from prisma import herramientas as H
from prisma.autoridad import Canal, Denegado, identificar
from prisma.db import admin, espacio


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _tarea(cur, ws, *, titulo="Programar HMI línea 2", persona="Nahuel Gimenez",
          estado="en_curso", criterio_aceptacion="Criterio de prueba",
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
         list(evidencia_requerida) if evidencia_requerida else []))
    t = cur.fetchone()["id"]
    if estado == "en_revision":
        # T6c (`odd/tasks/prisma-orienta.md`): `_pedir_cambios_tarea` ahora
        # consulta `estado_previo_a_revision` -- el `estado_anterior` de la
        # ÚLTIMA entrada a `en_revision` -- para decidir a qué estado
        # vuelve la tarea. Sin un `en_curso` real antes, ese valor sería
        # nulo y "Pedir cambios" volvería a `asignada`, rompiendo todas las
        # pruebas de este archivo que asumen la entrega típica (desde
        # `en_curso`). Una entrega sin haber arrancado nunca tiene su propio
        # helper (sección 8, más abajo).
        cur.execute("insert into task_state_event (task_id, estado_nuevo, "
                   "actor_kind) values (%s, 'en_curso', 'prisma')", (t,))
        cur.execute(
            "insert into task_state_event (task_id, estado_anterior, "
            "estado_nuevo, actor_kind) values (%s, 'en_curso', 'en_revision', "
            "'prisma')", (t,))
    else:
        cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                    "values (%s, %s, 'prisma')", (t, estado))
    return str(t)


def _evidencia(cur, ws, tarea_id, *, tipo="explicacion"):
    cur.execute(
        """insert into evidence (workspace_id, task_id, tipo, uri)
           values (%s, %s, %s, 'lista')""", (ws, tarea_id, tipo))


def _outbox_ultimo(cur, ws, tg) -> str:
    cur.execute(
        """select cuerpo from message_outbox
            where workspace_id = %s and chat_id = %s
           order by programado_para desc limit 1""", (ws, tg))
    return cur.fetchone()["cuerpo"]


def _tg(cur, nombre) -> int:
    # `integrante` es una vista filtrada por `prisma.workspace_id`
    # (`db/esquema.sql`), que sólo fija `espacio()` -- bajo `admin()` queda
    # sin definir y no devuelve filas (mismo gotcha que documentó la sesión
    # de T2b sobre `test_veracidad.py`). `app_user` es la tabla real, sin
    # ese filtro.
    cur.execute("select telegram_user_id t from app_user where nombre = %s", (nombre,))
    return cur.fetchone()["t"]


# ---------------------------------------------------------------------------
# 1. Entrega con evidencia (hallazgo 8)
# ---------------------------------------------------------------------------

def test_actualizar_estado_a_en_revision_pide_evidencia_si_falta(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)   # evidencia_requerida = ('explicacion',), sin evidencia
    conn.commit()

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(cur, nahuel, "actualizar_estado",
                               {"tarea_id": tid, "estado": "en_revision"},
                               ya_confirmada=True)

    assert resultado["en_revision"] is False
    assert "evidencia" in resultado["falta"].lower()

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"     # nunca se movió
        cur.execute("select count(*) n from evidence where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0


def test_actualizar_estado_a_en_revision_registra_evidencia_y_mueve_en_el_mismo_acto(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(
            cur, nahuel, "actualizar_estado",
            {"tarea_id": tid, "estado": "en_revision",
             "evidencia_texto": "Ya lo probé en el HMI de la línea."},
            ya_confirmada=True)

    assert resultado == {"estado": "en_revision"}

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"
        cur.execute(
            "select tipo, uri, entregado_por from evidence where task_id = %s", (tid,))
        fila = cur.fetchone()
        assert fila["tipo"] == "texto"
        assert fila["uri"] == "Ya lo probé en el HMI de la línea."


def test_actualizar_estado_a_en_revision_sin_evidencia_requerida_no_pide_nada(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, evidencia_requerida=None)
    conn.commit()

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(cur, nahuel, "actualizar_estado",
                               {"tarea_id": tid, "estado": "en_revision"},
                               ya_confirmada=True)

    assert resultado == {"estado": "en_revision"}
    with admin(conn) as cur:
        cur.execute("select count(*) n from evidence where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0


def test_actualizar_estado_a_en_revision_notifica_al_aprobador_con_botones(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        H.ejecutar(
            cur, nahuel, "actualizar_estado",
            {"tarea_id": tid, "estado": "en_revision", "evidencia_texto": "Listo."},
            ya_confirmada=True)

    with admin(conn) as cur:
        tg_marcos = _tg(cur, "Marcos Tarquini")   # aprobador de Nahuel
        cuerpo = _outbox_ultimo(cur, ws, tg_marcos)
        assert "Nahuel Gimenez entregó" in cuerpo
        assert "Programar HMI línea 2" in cuerpo
        assert "Listo." in cuerpo

        cur.execute(
            """select po.etiqueta from pending_action pa
                 join pending_action_option po on po.pending_action_id = pa.id
                where pa.workspace_id = %s and pa.chat_id = %s and pa.estado = 'esperando'
               order by po.orden""", (ws, tg_marcos))
        etiquetas = [f["etiqueta"] for f in cur.fetchall()]
    assert etiquetas == ["Aprobar", "Pedir cambios"]


def test_tocar_aprobar_de_la_notificacion_de_entrega_llega_a_la_vista_previa(
        corework, conn):
    """Tocar "Aprobar" desde la notificación de entrega reusa el mismo
    camino que el menú de tarea (T2): `SENTINEL_MENU_TAREA` ->
    `_resolver_toque_menu_tarea` -> vista previa de `aprobar_tarea` (ADR
    0008), nunca aplica nada por sí solo."""
    import dataclasses
    from contextlib import nullcontext

    from fastapi.testclient import TestClient

    from prisma import gateway

    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        H.ejecutar(
            cur, nahuel, "actualizar_estado",
            {"tarea_id": tid, "estado": "en_revision", "evidencia_texto": "Listo."},
            ya_confirmada=True)
    conn.commit()

    monkeypatch_targets = []

    class _MP:
        def setattr(self, obj, name, value):
            monkeypatch_targets.append((obj, name, getattr(obj, name)))
            setattr(obj, name, value)

        def undo(self):
            for obj, name, old in monkeypatch_targets:
                setattr(obj, name, old)

    mp = _MP()
    mp.setattr(gateway, "acusar_toque", lambda *a, **k: None)
    mp.setattr(gateway, "mantener_chat_activo", lambda *a, **k: nullcontext())
    mp.setattr(gateway, "_conn", lambda: conn)
    mp.setattr(gateway, "config",
              dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    try:
        cliente = TestClient(gateway.app)
        with admin(conn) as cur:
            tg_marcos = _tg(cur, "Marcos Tarquini")
            cur.execute(
                """select po.token from pending_action pa
                     join pending_action_option po on po.pending_action_id = pa.id
                    where pa.workspace_id = %s and pa.chat_id = %s
                      and pa.estado = 'esperando' and po.etiqueta = 'Aprobar'""",
                (ws, tg_marcos))
            token = cur.fetchone()["token"]

        resp = cliente.post(
            "/telegram/corework",
            json={"callback_query": {
                "id": "cb1", "from": {"id": tg_marcos}, "data": f"p:{token}",
                "message": {"message_id": 9, "chat": {"id": tg_marcos}}}},
            headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})
        assert resp.status_code == 200

        with admin(conn) as cur:
            cur.execute("select estado from task where id = %s", (tid,))
            assert cur.fetchone()["estado"] == "en_revision"   # todavía vista previa
            cur.execute(
                """select count(*) n from pending_action
                    where herramienta = 'aprobar_tarea' and estado = 'esperando'""")
            assert cur.fetchone()["n"] == 1
    finally:
        mp.undo()


# ---------------------------------------------------------------------------
# 2. El gate de "Aprobar" (decisión 2)
# ---------------------------------------------------------------------------

def test_aprobar_tarea_rechaza_si_la_tarea_no_esta_en_revision(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada", evidencia_requerida=None)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        try:
            H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": tid},
                      ya_confirmada=True)
            assert False, "tenía que rechazar"
        except Denegado as e:
            assert "en revisión" in str(e).lower()
            assert "asignada" in str(e).lower()

    with admin(conn) as cur:
        cur.execute("select count(*) n from approval where sujeto_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0


def test_aprobar_tarea_rechaza_si_falta_la_evidencia_que_exige(corework, conn):
    """Hallazgo 5 (sesión 2 por Telegram, 2026-09-27): antes de ADR 0009,
    Ismael pudo aprobar a ciegas una tarea sin evidencia -- la aprobación se
    registraba igual. Ahora ni siquiera llega a registrarse."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")   # sin evidencia
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        try:
            H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": tid},
                      ya_confirmada=True)
            assert False, "tenía que rechazar"
        except Denegado as e:
            assert "evidencia" in str(e).lower()
            assert "Nahuel Gimenez" in str(e)

    with admin(conn) as cur:
        cur.execute("select count(*) n from approval where sujeto_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0


def test_aprobar_tarea_permite_si_esta_en_revision_y_con_evidencia(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": tid},
                               ya_confirmada=True)
    assert resultado["aprobada"] is True


# ---------------------------------------------------------------------------
# 3. "Pedir cambios" (decisión 4)
# ---------------------------------------------------------------------------

def test_pedir_cambios_devuelve_a_en_curso_con_el_comentario_y_avisa(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(
            cur, marcos, "pedir_cambios_tarea",
            {"tarea_id": tid, "comentario": "Falta probarlo con carga real."},
            ya_confirmada=True)

    assert resultado == {"pedido": True, "titulo": "Programar HMI línea 2"}

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"
        cur.execute(
            """select decision, comentario from approval where sujeto_id = %s""", (tid,))
        fila = cur.fetchone()
        assert fila["decision"] == "rechazado"
        assert fila["comentario"] == "Falta probarlo con carga real."
        cur.execute(
            """select motivo from task_state_event
                where task_id = %s and estado_nuevo = 'en_curso'
               order by at desc limit 1""", (tid,))
        assert cur.fetchone()["motivo"] == "Falta probarlo con carga real."

        tg_nahuel = _tg(cur, "Nahuel Gimenez")
        cuerpo = _outbox_ultimo(cur, ws, tg_nahuel)
    assert "Marcos Tarquini pidió cambios" in cuerpo
    assert "Falta probarlo con carga real." in cuerpo


def test_pedir_cambios_rechaza_si_la_tarea_no_esta_en_revision(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada", evidencia_requerida=None)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        try:
            H.ejecutar(cur, marcos, "pedir_cambios_tarea",
                      {"tarea_id": tid, "comentario": "algo"}, ya_confirmada=True)
            assert False, "tenía que rechazar"
        except Denegado as e:
            assert "en revisión" in str(e).lower()


def test_pedir_cambios_exige_comentario(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        try:
            H.ejecutar(cur, marcos, "pedir_cambios_tarea",
                      {"tarea_id": tid, "comentario": "   "}, ya_confirmada=True)
            assert False, "tenía que rechazar"
        except Denegado as e:
            assert "corregir" in str(e).lower()


# ---------------------------------------------------------------------------
# 4. La palabra "falta" no queda repetida (hallazgo 9)
# ---------------------------------------------------------------------------

def test_aprobar_tarea_no_repite_la_palabra_falta_en_el_mensaje(corework, conn):
    """`motivo_no_cierra_tarea` devuelve un texto que ya empieza diciendo qué
    falta ("Falta el criterio de aceptación."); antes de esta corrección el
    conector agregaba "falta:" delante -- "para cerrarla todavía falta:
    Falta el criterio..." -- con la palabra repetida (hallazgo 9). El gate
    de evidencia (decisión 2) exige que la evidencia ya esté para aprobar,
    así que esta tarea la tiene -- lo único que falta es el criterio."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        destino = _tarea(cur, ws, titulo="Programar HMI línea 3",
                         estado="en_revision", criterio_aceptacion=None)
        _evidencia(cur, ws, destino)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": destino},
                               ya_confirmada=True)

    assert resultado["cerrada"] is False
    assert "criterio" in resultado["falta"].lower()
    with admin(conn) as cur:
        tg_nahuel = _tg(cur, "Nahuel Gimenez")
        cuerpo = _outbox_ultimo(cur, ws, tg_nahuel)
    assert cuerpo.lower().count("falta") == 1


# ---------------------------------------------------------------------------
# 5. Una aprobación anterior no sobrevive a "Pedir cambios" (T6a,
#    review-c112506a)
# ---------------------------------------------------------------------------

def test_pedir_cambios_invalida_una_aprobacion_anterior_que_no_habia_cerrado(
        corework, conn):
    """Antes de esta corrección, `motivo_no_cierra_tarea` contaba cualquier
    `approval` 'aprobado' del aprobador, de cualquier momento. Escenario
    completo: Marcos aprueba una entrega que no cierra porque queda un
    bloqueo abierto (registrado directo en `blocker`, no vía
    `registrar_bloqueo` -- ese cambia el estado a `bloqueada`, y acá la
    tarea tiene que seguir `en_revision` para poder aprobarse); pide
    cambios (ADR 0009, decisión 4); Nahuel vuelve a entregar; se resuelve el
    bloqueo -- la aprobación vieja ya no puede contar: falta una aprobación
    NUEVA, y cerrar sigue bloqueado hasta que llegue."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
        cur.execute(
            """insert into blocker (workspace_id, task_id, causa)
               values (%s, %s, 'permiso pendiente de otro equipo') returning id""",
            (ws, tid))
        bloqueo_id = cur.fetchone()["id"]
    conn.commit()

    # Marcos aprueba: la aprobación se registra, pero el bloqueo todavía
    # abierto impide cerrar.
    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": tid},
                               ya_confirmada=True)
    assert resultado["aprobada"] is True
    assert resultado["cerrada"] is False
    assert "bloqueo" in resultado["falta"].lower()

    # Marcos pide cambios: la tarea vuelve a en_curso; esa aprobación queda
    # invalidada por el `approval` 'rechazado' que acaba de insertarse.
    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        H.ejecutar(cur, marcos, "pedir_cambios_tarea",
                   {"tarea_id": tid, "comentario": "Falta ajustar el HMI."},
                   ya_confirmada=True)

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"

    # Nahuel vuelve a entregar. Con "Pedir cambios" de por medio, la
    # evidencia vieja ya no cuenta (T6b): sin `evidencia_texto` en este
    # mismo pedido, la reentrega quedaría pidiendo evidencia de nuevo
    # (cubierto aparte en la sección 6, más abajo) -- acá manda la
    # evidencia nueva y se resuelve el bloqueo.
    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(
            cur, nahuel, "actualizar_estado",
            {"tarea_id": tid, "estado": "en_revision",
             "evidencia_texto": "Ya ajusté el HMI que pidió Marcos."},
            ya_confirmada=True)
    assert resultado == {"estado": "en_revision"}

    with admin(conn) as cur:
        cur.execute(
            "update blocker set resuelto_en = now(), resolucion = 'listo' "
            "where id = %s", (bloqueo_id,))

        # El bloqueo ya no cuenta, pero la aprobación vieja tampoco: todavía
        # falta una aprobación.
        cur.execute("select motivo_no_cierra_tarea(%s) as m", (tid,))
        assert (cur.fetchone()["m"] ==
               "Falta la aprobación de quien revisa ese trabajo.")

    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException, match="aprobación"):
            cur.execute(
                """insert into task_state_event (task_id, estado_anterior,
                                                 estado_nuevo, actor_kind)
                   values (%s, 'en_revision', 'terminada', 'sistema')""", (tid,))

    # Una aprobación nueva -- posterior al "Pedir cambios" -- sí alcanza.
    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": tid},
                               ya_confirmada=True)
    assert resultado == {"aprobada": True, "cerrada": True, "falta": None,
                         "titulo": "Programar HMI línea 2"}

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "terminada"


def test_motivo_no_cierra_tarea_empate_de_at_no_cuenta_como_aprobada(
        corework, conn):
    """Regla explícita de la corrección: un 'aprobado' y un 'rechazado' del
    mismo aprobador con el mismo `at` -- dos filas insertadas en la misma
    transacción, donde `now()` es estable en PostgreSQL -- son un empate, y
    el empate falla cerrado: nunca cuenta como aprobada.

    Con T6b de por medio, el 'rechazado' también invalida la evidencia
    vieja (la de `_evidencia`, insertada antes) -- así que se manda una
    evidencia nueva, en su propia transacción para que su `at` quede
    después del empate, y así la comprobación llega hasta la de la
    aprobación en vez de quedarse antes, en la de evidencia."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        cur.execute(
            """insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                     aprobador_membership_id, decision)
               values (%s, 'tarea', %s, %s, 'aprobado')""",
            (ws, tid, marcos.membership_id))
        cur.execute(
            """insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                     aprobador_membership_id, decision, comentario)
               values (%s, 'tarea', %s, %s, 'rechazado', 'empate')""",
            (ws, tid, marcos.membership_id))
    conn.commit()

    with admin(conn) as cur:
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        cur.execute("select motivo_no_cierra_tarea(%s) as m", (tid,))
        motivo = cur.fetchone()["m"]
    assert motivo == "Falta la aprobación de quien revisa ese trabajo."


def test_aprobar_tarea_plana_sigue_alcanzando_para_cerrar(corework, conn):
    """Regresión: una aprobación sin ningún 'pedir cambios' de por medio
    sigue contando -- el arreglo de T6a no exige nada nuevo cuando no hubo
    'rechazado'."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": tid},
                               ya_confirmada=True)
    assert resultado == {"aprobada": True, "cerrada": True, "falta": None,
                         "titulo": "Programar HMI línea 2"}


# ---------------------------------------------------------------------------
# 6. Después de "Pedir cambios", la entrega pide evidencia nueva (T6b,
#    review-c112506a). Decisión del usuario (2026-09-27): la evidencia vieja
#    deja de contar -- hay que volver a mandar evidencia (ejemplo: pintar
#    una pared, al aprobador le faltó una parte, la evidencia nueva muestra
#    esa parte pintada).
# ---------------------------------------------------------------------------

def test_evidencia_pendiente_vuelve_a_pedir_tras_pedir_cambios(corework, conn):
    """Antes de esta corrección, `evidencia_pendiente` contaba cualquier
    fila de `evidence` de la tarea, aunque fuera de antes del "Pedir
    cambios" -- la evidencia de la primera entrega alcanzaba para que
    `actualizar_estado(en_revision)` no pidiera nada. Ahora vuelve a ser
    verdadero después de un `approval` 'rechazado', y sin evidencia nueva
    en el mismo pedido la tarea nunca se mueve."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        H.ejecutar(cur, marcos, "pedir_cambios_tarea",
                   {"tarea_id": tid, "comentario": "Falta un detalle."},
                   ya_confirmada=True)

    with admin(conn) as cur:
        cur.execute("select evidencia_pendiente(%s) as f", (tid,))
        assert cur.fetchone()["f"] is True

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(cur, nahuel, "actualizar_estado",
                               {"tarea_id": tid, "estado": "en_revision"},
                               ya_confirmada=True)
    assert resultado["en_revision"] is False
    assert "evidencia" in resultado["falta"].lower()

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"      # nunca se movió
        cur.execute("select count(*) n from evidence where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 1                    # sigue sólo la vieja


def test_redelivery_con_evidencia_texto_registra_fila_nueva_y_notifica(
        corework, conn):
    """La evidencia nueva de la reentrega se registra siempre (corrección
    del descarte): antes, con alguna fila de `evidence` ya existente,
    `_actualizar_estado` ni siquiera intentaba el insert, aunque la vista
    previa y el aviso al aprobador ya mostraban el texto nuevo."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        H.ejecutar(cur, marcos, "pedir_cambios_tarea",
                   {"tarea_id": tid, "comentario": "Falta un detalle."},
                   ya_confirmada=True)

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(
            cur, nahuel, "actualizar_estado",
            {"tarea_id": tid, "estado": "en_revision",
             "evidencia_texto": "Ahora sí, con el detalle corregido."},
            ya_confirmada=True)
    assert resultado == {"estado": "en_revision"}

    with admin(conn) as cur:
        cur.execute("select count(*) n from evidence where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 2     # la vieja (que ya no cuenta) + la nueva

        tg_marcos = _tg(cur, "Marcos Tarquini")
        cuerpo = _outbox_ultimo(cur, ws, tg_marcos)
    assert "Ahora sí, con el detalle corregido." in cuerpo


def test_ya_la_termine_pide_evidencia_de_nuevo_tras_pedir_cambios(corework, conn):
    """Mismo patrón que
    `test_ya_la_termine_pide_evidencia_si_falta_y_termina_en_vista_previa`
    (`tests/test_menu_tarea.py`), pero con "Pedir cambios" de por medio: la
    entrega anterior dejó una fila de `evidence`, y como después el
    aprobador pidió cambios esa evidencia ya no cuenta -- el menú vuelve a
    pedirla. Llama a `gateway._resolver_toque_menu_tarea` directo, sin
    pasar por HTTP ni por el token del menú (que T2 ya prueba de punta a
    punta): lo que importa acá es que la acción "terminar" recalcule
    `evidencia_pendiente` y no la vieja lectura descartada."""
    from prisma import gateway
    from prisma import pendientes as P

    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        H.ejecutar(cur, marcos, "pedir_cambios_tarea",
                   {"tarea_id": tid, "comentario": "Falta un detalle."},
                   ya_confirmada=True)

    with admin(conn) as cur:
        tg_nahuel = _tg(cur, "Nahuel Gimenez")

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        gateway._resolver_toque_menu_tarea(
            cur, nahuel, ws, tg_nahuel,
            {"eleccion": {"accion": "terminar"}, "tarea_id": tid,
             "titulo": "Programar HMI línea 2"},
            datetime.now(timezone.utc))

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"      # todavía no se pidió nada

        cuerpo = _outbox_ultimo(cur, ws, tg_nahuel)
        assert "qué hiciste" in cuerpo.lower()

        cur.execute(
            """select count(*) n from pending_action
                where herramienta = %s and modificar_pedido_en is not null
                  and modificacion_consumida_en is null""",
            (P.SENTINEL_DATO_MENU_TAREA,))
        assert cur.fetchone()["n"] == 1


def test_aprobar_tarea_rechaza_tras_pedir_cambios_sin_evidencia_nueva(
        corework, conn):
    """El gate de "Aprobar" (`_exigir_puede_aprobarse`, ADR 0009 decisión 2)
    reusa la misma `evidencia_pendiente`: si la tarea llega a `en_revision`
    sin evidencia posterior al "Pedir cambios" -- acá insertada directo en
    la base, nunca por `actualizar_estado`, que ya la exigiría (prueba de
    arriba) --, "Aprobar" sigue rechazando; con evidencia nueva, se
    permite."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        H.ejecutar(cur, marcos, "pedir_cambios_tarea",
                   {"tarea_id": tid, "comentario": "Falta un detalle."},
                   ya_confirmada=True)

    with admin(conn) as cur:
        cur.execute(
            """insert into task_state_event (task_id, estado_anterior,
                                             estado_nuevo, actor_kind)
               values (%s, 'en_curso', 'en_revision', 'sistema')""", (tid,))

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        try:
            H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": tid},
                      ya_confirmada=True)
            assert False, "tenía que rechazar"
        except Denegado as e:
            assert "evidencia" in str(e).lower()

    with admin(conn) as cur:
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, uri)
               values (%s, %s, 'texto', 'Ahora sí, corregido.')""", (ws, tid))
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, marcos, "aprobar_tarea", {"tarea_id": tid},
                               ya_confirmada=True)
    assert resultado["aprobada"] is True


def test_evidencia_texto_se_registra_aunque_ya_exista_evidencia_sin_pedir_cambios(
        corework, conn):
    """Regresión y corrección del descarte, sin ningún "Pedir cambios" de
    por medio: si la tarea ya tiene evidencia y de todos modos llega
    `evidencia_texto` en un `actualizar_estado(en_revision)` -- por
    ejemplo, alguien que la manda de nuevo sin que se la hayan pedido --,
    el texto se registra. Antes se descartaba en silencio porque
    `evidencia_pendiente` ya era falso."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_curso")
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(
            cur, nahuel, "actualizar_estado",
            {"tarea_id": tid, "estado": "en_revision",
             "evidencia_texto": "Mandé esto de nuevo, por si acaso."},
            ya_confirmada=True)
    assert resultado == {"estado": "en_revision"}

    with admin(conn) as cur:
        cur.execute("select count(*) n from evidence where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 2
        cur.execute(
            """select uri from evidence where task_id = %s order by at desc limit 1""",
            (tid,))
        assert cur.fetchone()["uri"] == "Mandé esto de nuevo, por si acaso."


# ---------------------------------------------------------------------------
# 7. Dedupe estable del aviso de entrega (T6d, `odd/tasks/prisma-orienta.md`)
# ---------------------------------------------------------------------------

def _dedupe_keys_entrega(cur, ws, tg) -> list[str]:
    cur.execute(
        """select dedupe_key from message_outbox
            where workspace_id = %s and chat_id = %s
              and dedupe_key like %s
           order by programado_para""",
        (ws, tg, f"{ws}:entrega:%"))
    return [f["dedupe_key"] for f in cur.fetchall()]


def test_notificar_entrega_repetido_en_la_misma_transaccion_no_duplica_el_aviso(
        corework, conn):
    """La clave de dedupe ancla en la transacción (`pg_current_xact_id()`),
    no en los hechos de la vista previa: dos llamadas al handler DENTRO de
    la misma transacción -- sin commit entre medio, ej. un código que se
    invoca dos veces por error antes de terminar -- comparten la misma
    transacción y tienen que colapsar en un solo aviso. Se llama al handler
    directo -- no a `H.ejecutar` -- porque el chequeo de huella de
    `ejecutar` ya impide un replay con el mismo `huella_previa` una vez que
    el estado cambió; lo que hay que probar acá es la clave de dedupe en sí,
    sin depender de esa otra protección."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_curso", evidencia_requerida=None)
    conn.commit()

    handler = H.REGISTRO["actualizar_estado"].handler

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado_1 = handler(cur, nahuel, tarea_id=tid, estado="en_revision")
        assert resultado_1 == {"estado": "en_revision"}

        # Fuerza la tarea de vuelta al mismo estado de origen, DENTRO de
        # esta misma transacción -- sin pasar por "Pedir cambios" y sin
        # commit --, para invocar el handler otra vez para lo que, a los
        # ojos de esta clave, es el mismo acto: la misma transacción.
        cur.execute(
            """insert into task_state_event (task_id, estado_anterior,
                                             estado_nuevo, actor_kind)
               values (%s, 'en_revision', 'en_curso', 'sistema')""", (tid,))
        resultado_2 = handler(cur, nahuel, tarea_id=tid, estado="en_revision")
        assert resultado_2 == {"estado": "en_revision"}

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"   # el acto sí se aplicó las dos veces

        tg_marcos = _tg(cur, "Marcos Tarquini")
        claves = _dedupe_keys_entrega(cur, ws, tg_marcos)
    # Un solo aviso: la segunda inserción chocó con `on conflict (dedupe_key)
    # do nothing` porque las dos llamadas comparten la misma transacción.
    assert len(claves) == 1


def test_entrega_sin_politica_de_evidencia_tras_pedir_cambios_notifica_dos_veces(
        corework, conn):
    """Corrección tras revisión del orquestador sobre la primera versión de
    este arreglo: usaba `_huella(tarea_id, fila["estado"], evidencia_texto)`
    -- los mismos hechos de la vista previa -- como ancla cuando no había
    evidencia nueva. Eso identifica el ESTADO DE ORIGEN, no el acto: dos
    entregas REALMENTE distintas (entrega -> "Pedir cambios" -> reentrega)
    que arrancan las dos desde `en_curso` sin evidencia nueva en ninguna de
    las dos -- el camino real de una tarea sin política de evidencia --
    producían la MISMA clave. El resultado no era "no duplica": la segunda
    entrega se quedaba sin avisar, en silencio (`AGENTS.md` lo prohíbe:
    "nunca falla en silencio"), con el `pending_action` de los botones
    "Aprobar"/"Pedir cambios" ya registrado para un mensaje que nunca salía
    -- y `message_outbox.dedupe_key` es `unique` para siempre, así que esa
    colisión no se arreglaba sola más adelante. Con la clave anclada en la
    transacción, cada entrega -- en su propia transacción -- avisa la suya."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_curso", evidencia_requerida=[])
    conn.commit()

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(cur, nahuel, "actualizar_estado",
                               {"tarea_id": tid, "estado": "en_revision"},
                               ya_confirmada=True)
    assert resultado == {"estado": "en_revision"}

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        H.ejecutar(cur, marcos, "pedir_cambios_tarea",
                   {"tarea_id": tid, "comentario": "Falta un detalle."},
                   ya_confirmada=True)

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(cur, nahuel, "actualizar_estado",
                               {"tarea_id": tid, "estado": "en_revision"},
                               ya_confirmada=True)
    assert resultado == {"estado": "en_revision"}

    with admin(conn) as cur:
        tg_marcos = _tg(cur, "Marcos Tarquini")
        claves = _dedupe_keys_entrega(cur, ws, tg_marcos)
    assert len(claves) == 2
    assert claves[0] != claves[1]


def test_dos_entregas_distintas_con_evidencia_notifican_dos_veces_con_claves_distintas(
        corework, conn):
    """Dos actos de entrega REALMENTE distintos -- separados por "Pedir
    cambios", cada uno con su propio texto de evidencia -- siguen avisando
    dos veces, con dos claves de dedupe distintas: la corrección de T6d no
    junta lo que es distinto, sólo deja de inventar una clave al azar donde
    antes no había ninguna identidad estable."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_curso")   # evidencia_requerida por defecto
    conn.commit()

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        H.ejecutar(
            cur, nahuel, "actualizar_estado",
            {"tarea_id": tid, "estado": "en_revision",
             "evidencia_texto": "Primera entrega."},
            ya_confirmada=True)

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        H.ejecutar(cur, marcos, "pedir_cambios_tarea",
                   {"tarea_id": tid, "comentario": "Falta un detalle."},
                   ya_confirmada=True)

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        H.ejecutar(
            cur, nahuel, "actualizar_estado",
            {"tarea_id": tid, "estado": "en_revision",
             "evidencia_texto": "Segunda entrega, corregida."},
            ya_confirmada=True)

    with admin(conn) as cur:
        tg_marcos = _tg(cur, "Marcos Tarquini")
        claves = _dedupe_keys_entrega(cur, ws, tg_marcos)
    assert len(claves) == 2
    assert claves[0] != claves[1]


# ---------------------------------------------------------------------------
# 8. "Pedir cambios" con una dependencia bloqueante abierta (T6c,
#    `odd/tasks/prisma-orienta.md`; enmienda a la decisión 4 de ADR 0009).
#    Antes de esta corrección, el disparador `exigir_dependencias_resueltas`
#    (`db/esquema.sql`) rechazaba CUALQUIER llegada a `en_curso` con una
#    dependencia bloqueante todavía abierta, incluida la restauración que
#    hace "Pedir cambios" -- el aprobador no podía pedir cambios en absoluto
#    mientras esa dependencia siguiera abierta. Decisión del usuario
#    (2026-09-27): la tarea vuelve al estado que tenía antes de la ÚLTIMA
#    entrada a `en_revision` -- `en_curso` si estaba en curso (una
#    restauración, exenta del gate igual que salir de `bloqueada`),
#    `asignada` si se entregó sin haber arrancado nunca.
# ---------------------------------------------------------------------------

def _dependencia_bloqueante(cur, ws, destino):
    """Una dependencia bloqueante abierta sobre `destino`: la origen se crea
    `asignada` y esta prueba nunca la cierra, así que `motivo_no_arranca_
    tarea` sigue frenando cualquier llegada a `en_curso` de `destino` que no
    sea una restauración exenta."""
    origen = _tarea(cur, ws, titulo="Programar PLC", estado="asignada",
                    evidencia_requerida=None)
    cur.execute(
        """insert into dependency (workspace_id, origen_task_id, destino_task_id, tipo)
           values (%s, %s, %s, 'bloqueante')""", (ws, origen, destino))
    return origen


def test_pedir_cambios_con_dependencia_bloqueante_abierta_vuelve_a_en_curso(
        corework, conn):
    """Antes de esta corrección, este mismo `pedir_cambios_tarea` levantaba
    `psycopg.errors.RaiseException` ("No se puede pasar la tarea a en
    curso...") porque el insert a `en_curso` chocaba con el disparador:
    exactamente el hallazgo anotado al cerrar T6a (`odd/tasks/
    prisma-orienta.md`)."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
        _dependencia_bloqueante(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(
            cur, marcos, "pedir_cambios_tarea",
            {"tarea_id": tid, "comentario": "Falta ajustar el HMI."},
            ya_confirmada=True)
    assert resultado == {"pedido": True, "titulo": "Programar HMI línea 2"}

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"

        tg_nahuel = _tg(cur, "Nahuel Gimenez")
        cuerpo = _outbox_ultimo(cur, ws, tg_nahuel)
    assert "vuelve a en curso" in cuerpo.lower()


def test_pedir_cambios_entregada_sin_arrancar_con_dependencia_abierta_vuelve_a_asignada(
        corework, conn):
    """"Ya la terminé" se ofrece desde `asignada` (`menu_tarea.py`): una
    tarea puede llegar a `en_revision` sin haber pasado nunca por
    `en_curso`. "Pedir cambios" no puede devolverla a un `en_curso` que
    nunca tuvo -- vuelve a `asignada`, y el gate de arranque sigue
    aplicando después: con la dependencia todavía abierta, `asignada` ->
    `en_curso` se rechaza igual que siempre. T6c exime la RESTAURACIÓN,
    nunca un arranque real."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
        cur.execute(
            """insert into task_state_event (task_id, estado_anterior,
                                             estado_nuevo, actor_kind)
               values (%s, 'asignada', 'en_revision', 'prisma')""", (tid,))
        _evidencia(cur, ws, tid)
        _dependencia_bloqueante(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(
            cur, marcos, "pedir_cambios_tarea",
            {"tarea_id": tid, "comentario": "Todavía falta empezar bien."},
            ya_confirmada=True)
    assert resultado == {"pedido": True, "titulo": "Programar HMI línea 2"}

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(cur, nahuel, "actualizar_estado",
                               {"tarea_id": tid, "estado": "en_curso"},
                               ya_confirmada=True)
    assert resultado["iniciada"] is False
    assert "dependencia" in resultado["falta"].lower()


def test_pedir_cambios_sin_dependencia_sigue_volviendo_a_en_curso(corework, conn):
    """Regresión: sin ninguna dependencia bloqueante de por medio, "Pedir
    cambios" sigue devolviendo la tarea a `en_curso` -- T6c sólo agrega la
    excepción que faltaba, no cambia el caso que ya cubría la sección 3."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        # `estado_previo_a_revision` sólo tiene `execute` concedido a
        # `prisma_app` (`db/esquema.sql`) -- bajo `prisma_admin` (helper
        # `admin(conn)`) el permiso está revocado, igual que
        # `estado_previo_a_bloqueo`. Se comprueba bajo el mismo rol que usa
        # `_pedir_cambios_tarea`.
        cur.execute("select estado_previo_a_revision(%s) as previo", (tid,))
        assert cur.fetchone()["previo"] == "en_curso"

        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, marcos, "pedir_cambios_tarea",
                               {"tarea_id": tid, "comentario": "Ajustar algo."},
                               ya_confirmada=True)
    assert resultado == {"pedido": True, "titulo": "Programar HMI línea 2"}

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"


def test_pedir_cambios_vista_previa_nombra_el_destino_real(corework, conn):
    """La vista previa (hoy siempre "vuelve a en curso") tiene que nombrar
    el destino real: `en curso` para una restauración, `asignada` para una
    entrega que nunca arrancó."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid_en_curso = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid_en_curso)

        tid_asignada = _tarea(cur, ws, titulo="Cablear tablero", estado="asignada")
        cur.execute(
            """insert into task_state_event (task_id, estado_anterior,
                                             estado_nuevo, actor_kind)
               values (%s, 'asignada', 'en_revision', 'prisma')""", (tid_asignada,))
        _evidencia(cur, ws, tid_asignada)
    conn.commit()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        try:
            H.ejecutar(cur, marcos, "pedir_cambios_tarea",
                      {"tarea_id": tid_en_curso, "comentario": "Ajustar algo."})
            assert False, "tenía que pedir confirmación"
        except H.NecesitaConfirmacion as e:
            assert "vuelve a en curso" in e.resumen.lower()

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        try:
            H.ejecutar(cur, marcos, "pedir_cambios_tarea",
                      {"tarea_id": tid_asignada, "comentario": "Ajustar algo."})
            assert False, "tenía que pedir confirmación"
        except H.NecesitaConfirmacion as e:
            assert "vuelve a asignada" in e.resumen.lower()


def test_actualizar_estado_en_curso_desde_en_revision_con_previo_en_curso_no_rechaza(
        corework, conn):
    """Consistencia entre el chequeo proactivo de `_actualizar_estado`/
    `_preparar_actualizar_estado` y el disparador: la misma restauración que
    exime `pedir_cambios_tarea` del gate de arranque tiene que eximir
    también una llamada directa a `actualizar_estado(estado="en_curso")` --
    sin la rama de T6c en el chequeo de Python, esto devolvía un `falta` que
    la base, con el disparador ya corregido, no habría rechazado."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
        _dependencia_bloqueante(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(cur, nahuel, "actualizar_estado",
                               {"tarea_id": tid, "estado": "en_curso"},
                               ya_confirmada=True)
    assert resultado == {"estado": "en_curso"}

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"


def test_estado_previo_a_revision_no_es_ejecutable_por_public(corework, conn):
    """Catálogo efectivo, no el texto del SQL (mismo criterio que
    `test_task_intake.py::test_0007_estado_previo_a_bloqueo_llega_por_
    migracion_con_dueno_correcto`): `security definer`, dueño
    `prisma_owner`, sin `execute` para `public`, con `execute` para
    `prisma_app`."""
    with admin(conn) as cur:
        cur.execute(
            """select r.rolname dueno, p.prosecdef definer,
                      has_function_privilege('public',
                        'prisma.estado_previo_a_revision(uuid)', 'execute') publico,
                      has_function_privilege('prisma_app',
                        'prisma.estado_previo_a_revision(uuid)', 'execute') app
                 from pg_proc p join pg_roles r on r.oid = p.proowner
                where p.oid = 'prisma.estado_previo_a_revision(uuid)'::regprocedure""")
        fila = cur.fetchone()
    assert fila["dueno"] == "prisma_owner"
    assert fila["definer"] is True
    assert fila["publico"] is False
    assert fila["app"] is True


# ---------------------------------------------------------------------------
# 9. Entrega repetida en_revision y empate de evidencia (T6g,
#    `odd/tasks/prisma-orienta.md`; review-e719d807, review-09452c69).
#    Decisión del usuario (2026-09-27): "ya la terminé" sobre una tarea que
#    YA está en_revision no registra ningún evento de estado -- antes, ese
#    evento `en_revision -> en_revision` hacía que `estado_previo_a_revision`
#    devolviera `en_revision` y que "Pedir cambios" mandara a `asignada` una
#    tarea que en realidad estaba `en_curso`.
# ---------------------------------------------------------------------------

def test_actualizar_estado_repetido_sobre_en_revision_sin_evidencia_solo_avisa(
        corework, conn):
    """Sin evidencia_texto en el pedido repetido, no hay nada que sumar: ni
    fila de evidencia ni fila de task_state_event nuevas -- sólo el aviso de
    que ya está en revisión."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
        cur.execute("select count(*) n from task_state_event where task_id = %s", (tid,))
        eventos_antes = cur.fetchone()["n"]
    conn.commit()

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(cur, nahuel, "actualizar_estado",
                               {"tarea_id": tid, "estado": "en_revision"},
                               ya_confirmada=True)

    assert "error" in resultado
    assert "en revisión" in resultado["error"].lower()

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"
        cur.execute("select count(*) n from evidence where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 1                     # sigue sólo la que ya tenía
        cur.execute("select count(*) n from task_state_event where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == eventos_antes         # ningún evento nuevo


def test_actualizar_estado_repetido_sobre_en_revision_con_evidencia_suma_fila_sin_evento(
        corework, conn):
    """Con evidencia_texto, se suma como un adjunto más -- igual que
    "Adjuntar evidencia" (`_preparar_adjuntar_evidencia`) -- pero nunca un
    segundo evento de estado."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
        cur.execute("select count(*) n from task_state_event where task_id = %s", (tid,))
        eventos_antes = cur.fetchone()["n"]
    conn.commit()

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(
            cur, nahuel, "actualizar_estado",
            {"tarea_id": tid, "estado": "en_revision",
             "evidencia_texto": "Una captura más, por si sirve."},
            ya_confirmada=True)

    assert "evidencia_id" in resultado
    assert "en revisión" in resultado["aviso"].lower()
    assert "evidencia" in resultado["aviso"].lower()

    with admin(conn) as cur:
        cur.execute("select count(*) n from evidence where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 2                     # la que ya tenía + la nueva
        cur.execute(
            """select uri from evidence where task_id = %s order by at desc limit 1""",
            (tid,))
        assert cur.fetchone()["uri"] == "Una captura más, por si sirve."
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"
        cur.execute("select count(*) n from task_state_event where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == eventos_antes         # ningún evento nuevo


def test_actualizar_estado_repetido_sobre_en_revision_con_evidencia_pide_confirmacion(
        corework, conn):
    """La vista previa describe lo que realmente va a pasar -- se suma
    evidencia, nunca "vuelve a en revisión" (no hay ningún cambio de
    estado que confirmar)."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        try:
            H.ejecutar(cur, nahuel, "actualizar_estado",
                      {"tarea_id": tid, "estado": "en_revision",
                       "evidencia_texto": "Otra vez, con más detalle."})
            assert False, "tenía que pedir confirmación"
        except H.NecesitaConfirmacion as e:
            assert "ya está en revisión" in e.resumen.lower()
            assert "se suma la evidencia" in e.resumen.lower()
            assert "Otra vez, con más detalle." in e.resumen


def test_pedir_cambios_tras_entrega_repetida_en_en_revision_sigue_volviendo_a_en_curso(
        corework, conn):
    """Regresión del hallazgo de review-09452c69: antes de esta corrección,
    la entrega repetida insertaba un evento `en_revision -> en_revision` que
    hacía que `estado_previo_a_revision` devolviera `en_revision` -- "Pedir
    cambios" mandaba a `asignada` una tarea que en realidad seguía en curso.
    Con la corrección, la entrega repetida no deja ningún evento nuevo, así
    que el previo real (`en_curso`) sigue intacto."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")   # previo real: en_curso
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(
            cur, nahuel, "actualizar_estado",
            {"tarea_id": tid, "estado": "en_revision",
             "evidencia_texto": "Ahí va de nuevo, por si no llegó."},
            ya_confirmada=True)
    assert "evidencia_id" in resultado

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, marcos, "pedir_cambios_tarea",
                               {"tarea_id": tid, "comentario": "Ajustar algo."},
                               ya_confirmada=True)
    assert resultado == {"pedido": True, "titulo": "Programar HMI línea 2"}

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"       # nunca `asignada`


def test_pedir_cambios_con_previo_en_revision_nulo_vuelve_a_asignada(corework, conn):
    """`estado_previo_a_revision` puede devolver NULL cuando no hay ningún
    evento anterior de entrada a en_revision registrado -- `_destino_pedir_
    cambios` trata ese caso igual que cualquier otro que no sea `en_curso`:
    vuelve a `asignada`, nunca supone un arranque que no se puede probar."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero", estado="asignada",
                    evidencia_requerida=None)
        # Reemplaza el único evento por uno sin `estado_anterior` -- mismo
        # patrón que usa `_tarea` para el estado inicial de cualquier tarea
        # -- para que `estado_previo_a_revision` no encuentre ninguna fila.
        cur.execute("delete from task_state_event where task_id = %s", (tid,))
        cur.execute(
            "insert into task_state_event (task_id, estado_nuevo, actor_kind) "
            "values (%s, 'en_revision', 'prisma')", (tid,))
        _evidencia(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        # `estado_previo_a_revision` sólo tiene `execute` concedido a
        # `prisma_app` -- bajo `prisma_admin` el permiso está revocado
        # (mismo gotcha documentado en la sección 8), así que la premisa se
        # comprueba bajo el mismo rol que usa `_pedir_cambios_tarea`.
        cur.execute("select estado_previo_a_revision(%s) as previo", (tid,))
        assert cur.fetchone()["previo"] is None

        marcos = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, marcos, "pedir_cambios_tarea",
                               {"tarea_id": tid, "comentario": "Ajustar algo."},
                               ya_confirmada=True)
    assert resultado == {"pedido": True, "titulo": "Cablear tablero"}

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"


def test_preparar_actualizar_estado_en_curso_desde_en_revision_pide_confirmacion_no_falta(
        corework, conn):
    """Sin `ya_confirmada`, la restauración a `en_curso` exenta del gate
    (T6c) tiene que llegar a la vista previa -- nunca a un `falta` --
    incluso con una dependencia bloqueante todavía abierta: eso es
    justamente lo que exime el disparador para esta restauración."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        _evidencia(cur, ws, tid)
        _dependencia_bloqueante(cur, ws, tid)
    conn.commit()

    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        try:
            H.ejecutar(cur, nahuel, "actualizar_estado",
                      {"tarea_id": tid, "estado": "en_curso"})
            assert False, "tenía que pedir confirmación"
        except H.NecesitaConfirmacion as e:
            assert "en curso" in e.resumen.lower()


def test_evidencia_pendiente_empate_de_at_en_la_misma_transaccion_falla_cerrado(
        corework, conn):
    """Sugerencia pendiente de review-e719d807: `evidencia_pendiente`
    compara con `>` estricto contra el último `rechazado` -- si el
    `approval` y la `evidence` nueva quedan con el mismo `at` (los dos
    insertados en la misma transacción, mismo `now()`), el empate tiene que
    fallar cerrado: sigue pendiente, para que un cambio futuro de `>` a `>=`
    no pase inadvertido."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        cur.execute(
            """select m.id from membership m join app_user u on u.id = m.app_user_id
                where m.workspace_id = %s and u.nombre = %s""",
            (ws, "Marcos Tarquini"))
        marcos_id = cur.fetchone()["id"]
        cur.execute(
            """insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                     aprobador_membership_id, decision, comentario)
               values (%s, 'tarea', %s, %s, 'rechazado', 'Ajustar algo')""",
            (ws, tid, marcos_id))
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, uri)
               values (%s, %s, 'texto', 'Ya corregido.')""", (ws, tid))

        # Confirma la premisa del empate antes de comprobar el resultado:
        # los dos inserts, en la misma transacción, comparten el mismo
        # `now()`.
        cur.execute(
            """select (select at from approval where sujeto_id = %s
                        order by at desc limit 1)
                     = (select at from evidence where task_id = %s
                        order by at desc limit 1) as mismo_at""",
            (tid, tid))
        assert cur.fetchone()["mismo_at"] is True

        cur.execute("select evidencia_pendiente(%s) as f", (tid,))
        assert cur.fetchone()["f"] is True
