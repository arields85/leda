"""Menú de acciones de una tarea (T2, `prisma-orienta`; ADR 0007, diseño
§4.6).

Tocar una tarea ofrece sólo lo que la persona puede hacer con ella, según su
estado y su relación (responsable, aprobador de la cadena del espacio, otra
persona del equipo) -- calculado por código, nunca por el modelo. Se llega al
menú tocando una opción de `ofrecer_opciones` (T1) con `accion: "menu"`: el
mecanismo que reutilizará T3 para listar tareas como botones.

Los toques se simulan con `gateway.procesar_update` y un `callback_query`,
igual que `tests/test_opciones_modelo.py`; los mensajes de texto libre, con
un `message`, igual que `tests/test_modificar.py`.
"""

from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import gateway
from prisma import jev as jev_modulo
from prisma import pendientes as P
from prisma.agente import responder
from prisma.autoridad import Canal, identificar
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.llm import Llamada, ProveedorGuionado, Respuesta

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _telegram_id(cur, nombre) -> int:
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return cur.fetchone()["t"]


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
                "values (%s, %s, 'prisma')", (t, estado))
    return str(t)


def _con_proveedor(monkeypatch, guion):
    proveedor = ProveedorGuionado(guion=list(guion))
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


def _jev_no_debe_llamarse(monkeypatch):
    def _explota(api_key):
        raise AssertionError("No debería consultarse a Jev acá.")
    monkeypatch.setattr(jev_modulo, "desde_base", _explota)


def _modelo_no_debe_llamarse(monkeypatch):
    def _explota(cur, ws, key):
        raise AssertionError("No debería consultarse al modelo acá.")
    monkeypatch.setattr("prisma.llm.desde_base", _explota)


@pytest.fixture
def cliente(conn, monkeypatch):
    monkeypatch.setattr(gateway, "acusar_toque", lambda *a, **k: None)
    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    import dataclasses
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    return TestClient(gateway.app)


def _tocar(cliente, token, user_id):
    return cliente.post(
        "/telegram/corework",
        json={"callback_query": {
            "id": "cb1", "from": {"id": user_id}, "data": f"p:{token}",
            "message": {"message_id": 7, "chat": {"id": user_id}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _mensaje(cliente, user_id, texto):
    return cliente.post(
        "/telegram/corework",
        json={"message": {"message_id": 2, "text": texto,
                          "chat": {"id": user_id}, "from": {"id": user_id}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _opciones(cur, pid):
    cur.execute(
        """select token, etiqueta, valor from pending_action_option
            where pending_action_id = %s order by orden""", (pid,))
    return cur.fetchall()


def _pendiente(cur, ws, herramienta) -> str:
    cur.execute(
        """select id from pending_action
            where workspace_id = %s and herramienta = %s and estado = 'esperando'
            order by creado_en desc limit 1""",
        (ws, herramienta))
    return str(cur.fetchone()["id"])


def _abrir_menu(cliente, conn, ws, monkeypatch, tarea_id, quien_nombre, *,
                chat_id=None):
    """Arma el guion de `ofrecer_opciones` con `accion: "menu"` sobre
    `tarea_id`, toca esa opción y devuelve (pid_menu, opciones_del_menu,
    telegram_id). El primer toque abre el menú -- nunca retoma al modelo."""
    guion = [Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿De qué tarea hablamos?",
        "opciones": [{"tarea_id": tarea_id, "accion": "menu"}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, quien_nombre, ws)
        cal = Calendario.desde_base(cur, ws)
        cid = chat_id if chat_id is not None else _telegram_id(cur, quien_nombre)
        responder(cur, quien, "tarea", proveedor, cal, chat_id=cid,
                 ahora=datetime.now(timezone.utc))
        pid_opciones = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        token = _opciones(cur, pid_opciones)[0]["token"]
        tg = _telegram_id(cur, quien_nombre)

    assert _tocar(cliente, token, tg).status_code == 200

    with espacio(conn, ws) as cur:
        pid_menu = _pendiente(cur, ws, P.SENTINEL_MENU_TAREA)
        filas = _opciones(cur, pid_menu)
    return pid_menu, filas, tg


def _tocar_accion(cliente, conn, ws, filas, etiqueta, tg):
    fila = next(f for f in filas if f["etiqueta"] == etiqueta)
    assert _tocar(cliente, fila["token"], tg).status_code == 200


# ---------------------------------------------------------------------------
# El menú según estado y relación (§4.6)
# ---------------------------------------------------------------------------

def test_menu_responsable_asignada(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
    conn.commit()

    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez")
    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == ["Ver detalle", "Empezar", "Ya la terminé",
                        "Informar un bloqueo", "Depende de otra tarea",
                        P.ETIQUETA_SALIR_OPCIONES]


def test_menu_responsable_en_curso(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_curso")
    conn.commit()

    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez")
    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == ["Ver detalle", "Ya la terminé", "Informar un bloqueo",
                        "Depende de otra tarea", P.ETIQUETA_SALIR_OPCIONES]


def _bloquear(cur, ws, tarea_id, *, causa="Falta un repuesto"):
    cur.execute(
        "insert into blocker (workspace_id, task_id, causa) values (%s, %s, %s)",
        (ws, tarea_id, causa))
    cur.execute(
        """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                         actor_kind, motivo)
           values (%s, (select estado from task where id = %s), 'bloqueada',
                   'sistema', %s)""",
        (tarea_id, tarea_id, causa))


def test_menu_responsable_bloqueada(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
        _bloquear(cur, ws, tid)
    conn.commit()

    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez")
    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == ["Ver detalle", "Ya se destrabó", P.ETIQUETA_SALIR_OPCIONES]


def test_menu_responsable_en_revision(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
    conn.commit()

    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez")
    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == ["Ver detalle", "Adjuntar evidencia", P.ETIQUETA_SALIR_OPCIONES]


def test_menu_responsable_terminada(conn, corework):
    """Una tarea terminada o cancelada ya no es "activa": `ofrecer_opciones`
    (T1) no la ofrece para abrir su menú por HTTP -- ese es el único camino
    de entrada que existe hoy, antes de T3 -- así que esto prueba el cálculo
    determinístico (`menu_tarea.calcular_menu`) directo, no el toque de
    punta a punta como las demás variantes de este test."""
    from prisma import menu_tarea as M

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
                    "values (%s, 'terminada', 'prisma')", (tid,))
    conn.commit()

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        menu = M.calcular_menu(cur, quien, tid)
    assert [a.etiqueta for a in menu.acciones] == ["Ver detalle"]


def test_menu_aprobador_en_revision(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
    conn.commit()

    # Marcos Tarquini es el aprobador de Nahuel Gimenez (aprobado_por: marcos).
    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Marcos Tarquini")
    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == ["Ver detalle y evidencia", "Aprobar", P.ETIQUETA_SALIR_OPCIONES]


def test_menu_aprobador_otro_estado(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_curso")
    conn.commit()

    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Marcos Tarquini")
    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == ["Ver detalle", P.ETIQUETA_SALIR_OPCIONES]


def test_menu_otra_persona(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
    conn.commit()

    # Ariel De Simone (referente de corelabs) no es responsable ni aprobador
    # de una tarea de OT.
    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Ariel De Simone")
    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == ["Ver detalle", "Mi trabajo depende de esta tarea",
                        P.ETIQUETA_SALIR_OPCIONES]


# ---------------------------------------------------------------------------
# "Empezar" no se ofrece con una dependencia bloqueante sin terminar (§4)
# ---------------------------------------------------------------------------

def test_empezar_no_se_ofrece_con_dependencia_bloqueante_sin_terminar(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Instalar tablero", estado="asignada",
                        persona="Marcos Tarquini", area="ot")
        destino = _tarea(cur, ws, titulo="Programar HMI línea 2", estado="asignada")
        cur.execute(
            """insert into dependency (workspace_id, origen_task_id, destino_task_id, tipo)
               values (%s, %s, %s, 'bloqueante')""", (ws, origen, destino))
    conn.commit()

    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, destino, "Nahuel Gimenez")
    etiquetas = [f["etiqueta"] for f in filas]
    assert "Empezar" not in etiquetas
    assert etiquetas == ["Ver detalle", "Ya la terminé", "Informar un bloqueo",
                        "Depende de otra tarea", P.ETIQUETA_SALIR_OPCIONES]


# ---------------------------------------------------------------------------
# Tocar el menú nunca aplica nada; "Ya la terminé" termina en vista previa
# ---------------------------------------------------------------------------

def test_ya_la_termine_pasa_a_en_revision_por_vista_previa(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
    conn.commit()

    pid_menu, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                      "Nahuel Gimenez")
    _tocar_accion(cliente, conn, ws, filas, "Ya la terminé", tg)

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"      # nada se aplicó todavía

        cur.execute(
            """select id, resumen from pending_action
                where herramienta = 'actualizar_estado' and estado = 'esperando'""")
        fila = cur.fetchone()
        assert fila is not None
        assert "en revisión" in fila["resumen"].lower() or \
               "en_revision" in fila["resumen"].lower()

        cur.execute(
            """select etiqueta from pending_action_option
                where pending_action_id = %s order by orden""", (fila["id"],))
        assert [f["etiqueta"] for f in cur.fetchall()] == [
            "Confirmar", "Modificar", "Cancelar"]


def test_empezar_termina_en_vista_previa_a_en_curso(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
    conn.commit()

    pid_menu, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                      "Nahuel Gimenez")
    _tocar_accion(cliente, conn, ws, filas, "Empezar", tg)

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"
        cur.execute(
            """select count(*) n from pending_action
                where herramienta = 'actualizar_estado' and estado = 'esperando'""")
        assert cur.fetchone()["n"] == 1


def test_aprobar_termina_en_vista_previa(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
    conn.commit()

    pid_menu, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                      "Marcos Tarquini")
    _tocar_accion(cliente, conn, ws, filas, "Aprobar", tg)

    with admin(conn) as cur:
        cur.execute("select count(*) n from approval where sujeto_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0     # nada se aplicó todavía
        cur.execute(
            """select count(*) n from pending_action
                where herramienta = 'aprobar_tarea' and estado = 'esperando'""")
        assert cur.fetchone()["n"] == 1


# ---------------------------------------------------------------------------
# Un bloqueo pide la causa por escrito y termina en vista previa
# ---------------------------------------------------------------------------

def test_informar_bloqueo_pide_la_causa_y_arma_vista_previa(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
    conn.commit()

    pid_menu, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                      "Nahuel Gimenez")
    _tocar_accion(cliente, conn, ws, filas, "Informar un bloqueo", tg)

    with admin(conn) as cur:
        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para desc limit 1""", (tg,))
        assert "causa" in cur.fetchone()["cuerpo"].lower()
        cur.execute(
            """select count(*) n from pending_action
                where herramienta = %s and modificar_pedido_en is not null
                  and modificacion_consumida_en is null""",
            (P.SENTINEL_DATO_MENU_TAREA,))
        assert cur.fetchone()["n"] == 1

    assert _mensaje(cliente, tg, "Falta un repuesto que no llegó todavía").status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"    # sigue sin aplicarse
        cur.execute(
            """select resumen from pending_action
                where herramienta = 'registrar_bloqueo' and estado = 'esperando'""")
        fila = cur.fetchone()
        assert fila is not None
        assert "falta un repuesto" in fila["resumen"].lower()


# ---------------------------------------------------------------------------
# "Ver detalle" es una lectura determinística: no llama al modelo
# ---------------------------------------------------------------------------

def test_ver_detalle_no_llama_al_modelo(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Programar HMI línea 2", estado="asignada")
        _bloquear(cur, ws, tid)
    conn.commit()

    pid_menu, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                      "Nahuel Gimenez")

    _jev_no_debe_llamarse(monkeypatch)
    _modelo_no_debe_llamarse(monkeypatch)

    _tocar_accion(cliente, conn, ws, filas, "Ver detalle", tg)

    with admin(conn) as cur:
        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para desc limit 1""", (tg,))
        cuerpo = cur.fetchone()["cuerpo"]
        assert "Programar HMI línea 2" in cuerpo
        assert "Falta un repuesto" in cuerpo
        # Reabre el menú vigente en el mismo mensaje.
        cur.execute(
            """select id from pending_action
                where workspace_id = %s and herramienta = %s and estado = 'esperando'
                order by creado_en desc limit 1""",
            (ws, P.SENTINEL_MENU_TAREA))
        nuevo_pid = str(cur.fetchone()["id"])
        assert nuevo_pid != pid_menu
        cur.execute(
            """select etiqueta from pending_action_option
                where pending_action_id = %s order by orden""", (nuevo_pid,))
        assert [f["etiqueta"] for f in cur.fetchall()] == [
            "Ver detalle", "Ya se destrabó", P.ETIQUETA_SALIR_OPCIONES]


# ---------------------------------------------------------------------------
# La salida cierra sin efecto
# ---------------------------------------------------------------------------

def test_salida_del_menu_cierra_sin_efecto(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
    conn.commit()

    pid_menu, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                      "Nahuel Gimenez")
    _tocar_accion(cliente, conn, ws, filas, P.ETIQUETA_SALIR_OPCIONES, tg)

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid_menu,))
        assert cur.fetchone()["estado"] == "resuelta"
        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para desc limit 1""", (tg,))
        assert "escrib" in cur.fetchone()["cuerpo"].lower()


# ---------------------------------------------------------------------------
# Garantías reusadas del mecanismo de acción pendiente
# ---------------------------------------------------------------------------

def test_toque_de_otro_integrante_no_resuelve(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
    conn.commit()

    pid_menu, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                     "Nahuel Gimenez")
    token = filas[0]["token"]
    with espacio(conn, ws) as cur:
        ajeno = _telegram_id(cur, "Ariel De Simone")

    assert _tocar(cliente, token, ajeno).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid_menu,))
        assert cur.fetchone()["estado"] == "esperando"


def test_toque_vencido_no_aplica(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
    conn.commit()

    pid_menu, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                      "Nahuel Gimenez")
    token = filas[0]["token"]
    with admin(conn) as cur:
        cur.execute(
            "update pending_action set vence_en = now() - interval '1 hour' where id = %s",
            (pid_menu,))
    conn.commit()

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid_menu,))
        assert cur.fetchone()["estado"] == "vencida"


def test_toque_repetido_no_aplica_dos_veces(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
    conn.commit()

    pid_menu, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                      "Nahuel Gimenez")
    token = next(f for f in filas if f["etiqueta"] == "Empezar")["token"]

    assert _tocar(cliente, token, tg).status_code == 200
    assert _tocar(cliente, token, tg).status_code == 200    # de nuevo, no rompe

    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from pending_action
                where herramienta = 'actualizar_estado' and estado = 'esperando'""")
        assert cur.fetchone()["n"] == 1


# ---------------------------------------------------------------------------
# Auditoría: tipo de acción e id de tarea, nunca texto libre
# ---------------------------------------------------------------------------

def test_auditoria_de_una_accion_del_menu_sin_texto(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Programar HMI (secreto)", estado="asignada")
    conn.commit()

    pid_menu, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                      "Nahuel Gimenez")
    _tocar_accion(cliente, conn, ws, filas, "Informar un bloqueo", tg)
    assert _mensaje(cliente, tg, "Falta un repuesto secreto").status_code == 200

    with admin(conn) as cur:
        cur.execute(
            """select detalle from audit_log where accion = 'accion_menu_tarea'
                order by at""")
        filas_audit = cur.fetchall()
        assert filas_audit
        for f in filas_audit:
            crudo = str(f["detalle"])
            assert "secreto" not in crudo.lower()
            assert f["detalle"].get("tarea_id") == tid


# ---------------------------------------------------------------------------
# Revisión del orquestador sobre T1 (a): un id de tarea en mayúsculas coincide
# ---------------------------------------------------------------------------

def test_tarea_id_en_mayusculas_coincide_al_validar(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero máq. 3", estado="asignada",
                    persona="Marcos Tarquini", area="ot")
    conn.commit()

    guion = [Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿Cuál tarea?", "opciones": [{"tarea_id": tid.upper()}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "elegí una tarea", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        filas = _opciones(cur, pid)

    assert filas[0]["etiqueta"] == "Cablear tablero máq. 3"
    assert filas[0]["valor"]["tarea_id"] == tid.lower()


# ---------------------------------------------------------------------------
# Revisión del orquestador sobre T1 (b): la respuesta al retomar una opción
# siempre se entrega, incluso si falla el proveedor/modelo
# ---------------------------------------------------------------------------

def test_retomar_una_opcion_entrega_respuesta_aunque_falle_el_proveedor(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero máq. 3", estado="asignada",
                    persona="Marcos Tarquini", area="ot")
    conn.commit()

    guion = [Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿De cuál tarea hablamos?",
        "opciones": [{"tarea_id": tid}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "¿cómo va?", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        token = _opciones(cur, pid)[0]["token"]
        tg = _telegram_id(cur, "Marcos Tarquini")

    # Al retomar, construir el proveedor explota -- antes de llegar a
    # `agente.responder`, que es quien atrapa la falla del modelo en sí.
    def _explota(cur, ws, key):
        raise RuntimeError("proveedor caído")
    monkeypatch.setattr("prisma.llm.desde_base", _explota)

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid,))
        assert cur.fetchone()["estado"] == "resuelta"
        cur.execute(
            "select cuerpo from message_outbox where chat_id = %s order by programado_para desc limit 1",
            (tg,))
        fila = cur.fetchone()
        assert fila is not None, "la persona se quedó sin ninguna respuesta"
        cur.execute(
            "select count(*) n from incident where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] >= 1
