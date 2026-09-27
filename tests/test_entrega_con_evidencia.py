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

    # Nahuel vuelve a entregar (la evidencia ya estaba, no hace falta de
    # nuevo) y se resuelve el bloqueo.
    with espacio(conn, ws) as cur:
        nahuel = _quien(cur, "Nahuel Gimenez", ws)
        resultado = H.ejecutar(cur, nahuel, "actualizar_estado",
                               {"tarea_id": tid, "estado": "en_revision"},
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
    el empate falla cerrado: nunca cuenta como aprobada."""
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
