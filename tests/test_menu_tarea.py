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

import uuid
from contextlib import nullcontext
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import gateway
from prisma import herramientas as H
from prisma import jev as jev_modulo
from prisma import pendientes as P
from prisma.agente import responder
from prisma.autoridad import Canal, identificar
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.llm import Llamada, ProveedorGuionado, Respuesta
from prisma.salida import (ETIQUETA_CANCELAR, ETIQUETA_CONFIRMAR, ICONO_TAREA,
                           con_icono, etiqueta_sin_icono,
                           etiquetas_boton_distinguibles, etiquetas_coinciden)

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
    # Compara sin el ícono de categoría (íconos, decisión del usuario,
    # 2026-09-28): las pruebas siguen pasando el nombre de la acción "pelado"
    # ("Empezar"), y la opción real ya sale armada con su "📋 " -- ver
    # `salida.etiquetas_coinciden`.
    fila = next(f for f in filas if etiquetas_coinciden(f["etiqueta"], etiqueta))
    assert _tocar(cliente, fila["token"], tg).status_code == 200


def _t(*etiquetas: str) -> list[str]:
    """Cada acción del menú con su ícono de tarea (íconos, decisión del
    usuario, 2026-09-28) -- `gateway._encolar_menu_tarea` se lo antepone a
    cada `menu_tarea.AccionMenu.etiqueta`."""
    return [con_icono(e, ICONO_TAREA) for e in etiquetas]


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
    assert etiquetas == _t("Ver detalle", "Empezar", "Ya la terminé",
                        "Informar un bloqueo", "Depende de otra tarea") + [
                        P.ETIQUETA_SALIR_OPCIONES]


def test_menu_responsable_en_curso(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_curso")
    conn.commit()

    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez")
    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == _t("Ver detalle", "Ya la terminé", "Informar un bloqueo",
                        "Depende de otra tarea") + [P.ETIQUETA_SALIR_OPCIONES]


# ---------------------------------------------------------------------------
# Encabezado del menú: responsable y estado (hallazgo 4, sesión 2 por
# Telegram, 2026-09-27). Con la lista de tareas movida a botones, el texto
# ya no enumera -- lo único que se perdía era saber DE QUIÉN es la tarea y en
# qué estado está sin abrir "Ver detalle". El encabezado del menú lo agrega,
# corto, en una sola pregunta.
# ---------------------------------------------------------------------------

def _resumen_menu(conn, ws) -> str:
    with admin(conn) as cur:
        cur.execute(
            """select resumen from pending_action
                where workspace_id = %s and herramienta = %s and estado = 'esperando'
                order by creado_en desc limit 1""",
            (ws, P.SENTINEL_MENU_TAREA))
        return cur.fetchone()["resumen"]


def test_encabezado_del_menu_muestra_responsable_y_estado(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Programar HMI línea 2", estado="en_revision",
                    persona="Mariano Naim")
    conn.commit()

    _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez")
    resumen = _resumen_menu(conn, ws)

    assert "Mariano Naim" in resumen
    assert "en revisión" in resumen.lower()
    assert "Programar HMI línea 2" in resumen
    assert resumen.count("?") == 1          # una sola pregunta


def test_encabezado_del_menu_dice_tuya_para_la_propia_responsable(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada", persona="Nahuel Gimenez")
    conn.commit()

    _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez")
    resumen = _resumen_menu(conn, ws)

    assert "tuya" in resumen.lower()
    assert "Nahuel Gimenez" not in resumen   # nunca su propio nombre
    assert resumen.count("?") == 1


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
    assert etiquetas == _t("Ver detalle", "Ya se destrabó") + [P.ETIQUETA_SALIR_OPCIONES]


def test_menu_responsable_en_revision(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
    conn.commit()

    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez")
    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == _t("Ver detalle", "Adjuntar evidencia") + [P.ETIQUETA_SALIR_OPCIONES]


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


def test_menu_responsable_en_revision_ofrece_cerrar_tarea_si_ya_alcanza(
        conn, corework):
    """ADR 0008, hallazgo 5 (sesión 2 por Telegram, 2026-09-27): si la
    aprobación llegó antes de que se completara otra condición de cierre --
    acá, la evidencia -- y esa condición se resuelve después, el responsable
    tiene que poder cerrar tocando, no sólo escribiendo."""
    from prisma import menu_tarea as M

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


def test_menu_responsable_en_revision_sin_aprobacion_no_ofrece_cerrar_tarea(
        cliente, conn, corework, monkeypatch):
    """Mismo escenario de `test_menu_responsable_en_revision`, pero explícito
    sobre el motivo (ADR 0008): sin la aprobación todavía no alcanza, así que
    "Cerrar tarea" no aparece."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, uri)
               values (%s, %s, 'explicacion', 'ya está')""", (ws, tid))
    conn.commit()

    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Nahuel Gimenez")
    etiquetas = [f["etiqueta"] for f in filas]
    assert "Cerrar tarea" not in etiquetas
    assert etiquetas == _t("Ver detalle", "Adjuntar evidencia") + [P.ETIQUETA_SALIR_OPCIONES]


def test_cerrar_tarea_desde_el_menu_termina_en_vista_previa(
        cliente, conn, corework, monkeypatch):
    """"Cerrar tarea" reusa `actualizar_estado` -- pasa por la misma vista
    previa que cualquier acción del menú que escribe (T2); tocarla no aplica
    nada todavía."""
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

    pid_menu, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                      "Nahuel Gimenez")
    assert any(etiquetas_coinciden(f["etiqueta"], "Cerrar tarea") for f in filas)
    _tocar_accion(cliente, conn, ws, filas, "Cerrar tarea", tg)

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"    # todavía vista previa
        cur.execute(
            """select count(*) n from pending_action
                where herramienta = 'actualizar_estado' and estado = 'esperando'""")
        assert cur.fetchone()["n"] == 1


def test_menu_aprobador_en_revision(cliente, conn, corework, monkeypatch):
    """ADR 0009, decisión 2: "Aprobar" sólo se ofrece con la evidencia que
    exige la política ya registrada -- esta tarea la tiene. "Pedir cambios"
    (decisión 4) se ofrece siempre que la tarea esté en revisión."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, uri)
               values (%s, %s, 'explicacion', 'ya está')""", (ws, tid))
    conn.commit()

    # Marcos Tarquini es el aprobador de Nahuel Gimenez (aprobado_por: marcos).
    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Marcos Tarquini")
    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == _t("Ver detalle y evidencia", "Aprobar", "Pedir cambios") + [
                        P.ETIQUETA_SALIR_OPCIONES]


def test_menu_aprobador_en_revision_sin_evidencia_no_ofrece_aprobar(
        cliente, conn, corework, monkeypatch):
    """Hallazgo 5 (sesión 2 por Telegram, 2026-09-27): Ismael pudo tocar
    "Aprobar" sobre la tarea de Ariel aunque no tenía evidencia -- el menú se
    lo ofrecía igual. Ahora no aparece; "Pedir cambios" sigue disponible."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_revision")   # sin evidencia
    conn.commit()

    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Marcos Tarquini")
    etiquetas = [f["etiqueta"] for f in filas]
    assert not any(etiquetas_coinciden(e, "Aprobar") for e in etiquetas)
    assert etiquetas == _t("Ver detalle y evidencia", "Pedir cambios") + [
                        P.ETIQUETA_SALIR_OPCIONES]


def test_menu_aprobador_otro_estado(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="en_curso")
    conn.commit()

    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Marcos Tarquini")
    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == _t("Ver detalle") + [P.ETIQUETA_SALIR_OPCIONES]


def test_menu_otra_persona(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
    conn.commit()

    # Ariel De Simone (referente de corelabs) no es responsable ni aprobador
    # de una tarea de OT.
    _, filas, _ = _abrir_menu(cliente, conn, ws, monkeypatch, tid, "Ariel De Simone")
    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == _t("Ver detalle", "Mi trabajo depende de esta tarea") + [
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
    assert not any(etiquetas_coinciden(e, "Empezar") for e in etiquetas)
    assert etiquetas == _t("Ver detalle", "Ya la terminé", "Informar un bloqueo",
                        "Depende de otra tarea") + [P.ETIQUETA_SALIR_OPCIONES]


# ---------------------------------------------------------------------------
# Seguimiento (e) a la revisión de la sesión de etiquetas (review-af418dd9):
# las candidatas de una dependencia usan `salida.etiquetas_boton_distinguibles`
# igual que cualquier otro botón server-armado -- títulos largos se cortan en
# límite de palabra, y dos que colisionan se distinguen.
# ---------------------------------------------------------------------------

def test_pedir_eleccion_dependencia_acorta_y_distingue_titulos_largos(
        conn, corework):
    """Seguimiento de review-149a33fa ("asserts"): la aserción original sólo
    comprobaba `len(set(etiquetas)) == 2` y que "3"/"4" aparecieran en algún
    lado -- pasaría igual con un resultado distinto al que arma de verdad
    `salida.etiquetas_boton_distinguibles` (por ejemplo, numerado como
    "... (2)" en vez de extendido con el dígito). Se compara contra el valor
    exacto que devuelve esa función para este mismo par de títulos."""
    ws = corework.workspace_id
    titulo_a = "Revisar tablero de la máquina 3"
    titulo_b = "Revisar tablero de la máquina 4"
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Instalar tablero", persona="Marcos Tarquini")
        a = _tarea(cur, ws, titulo=titulo_a, persona="Marcos Tarquini")
        b = _tarea(cur, ws, titulo=titulo_b, persona="Marcos Tarquini")
    conn.commit()

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._pedir_eleccion_dependencia(
            cur, quien, ws, 1, accion="crear_dependencia_bloqueante",
            tarea_id=origen, titulo="Instalar tablero",
            pregunta="¿De cuál depende?",
            candidatas=[(a, titulo_a), (b, titulo_b)],
            ahora=datetime.now(timezone.utc))
        pid = _pendiente(cur, ws, P.SENTINEL_DATO_MENU_TAREA)
        etiquetas = [f["etiqueta"] for f in _opciones(cur, pid)]

    assert etiquetas == _t(*etiquetas_boton_distinguibles([titulo_a, titulo_b]))
    # los dos títulos enteros entran en el corte duro, con el ícono de tarea aparte
    assert etiquetas == _t(titulo_a, titulo_b)


# ---------------------------------------------------------------------------
# Tocar el menú nunca aplica nada; "Ya la terminé" termina en vista previa
# ---------------------------------------------------------------------------

def test_ya_la_termine_pide_evidencia_si_falta_y_termina_en_vista_previa(
        cliente, conn, corework, monkeypatch):
    """ADR 0009 (hallazgo 8, sesión 2 por Telegram, 2026-09-27): antes,
    "Ya la terminé" pasaba directo a la vista previa aunque la política
    exigiera evidencia y no hubiera ninguna -- exactamente lo que le pasó a
    Ariel. Ahora pide el dato primero (mismo patrón que "Informar un
    bloqueo") y arma UNA sola vista previa que registra la evidencia y
    mueve el estado juntos."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")   # evidencia_requerida = ['explicacion']
    conn.commit()

    pid_menu, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                      "Nahuel Gimenez")
    _tocar_accion(cliente, conn, ws, filas, "Ya la terminé", tg)

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"      # todavía no se pidió nada
        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para desc limit 1""", (tg,))
        assert "qué hiciste" in cur.fetchone()["cuerpo"].lower()
        cur.execute(
            """select count(*) n from pending_action
                where herramienta = %s and modificar_pedido_en is not null
                  and modificacion_consumida_en is null""",
            (P.SENTINEL_DATO_MENU_TAREA,))
        assert cur.fetchone()["n"] == 1

    assert _mensaje(cliente, tg, "Ya lo probé en producción.").status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"      # nada se aplicó todavía
        cur.execute("select count(*) n from evidence where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0                    # tampoco la evidencia

        cur.execute(
            """select id, resumen from pending_action
                where herramienta = 'actualizar_estado' and estado = 'esperando'""")
        fila = cur.fetchone()
        assert fila is not None
        assert "en revisión" in fila["resumen"].lower()
        assert "ya lo probé en producción" in fila["resumen"].lower()

        cur.execute(
            """select etiqueta from pending_action_option
                where pending_action_id = %s order by orden""", (fila["id"],))
        assert [f["etiqueta"] for f in cur.fetchall()] == [
            ETIQUETA_CONFIRMAR, "Modificar", ETIQUETA_CANCELAR]


def test_ya_la_termine_pasa_directo_a_vista_previa_si_ya_tiene_evidencia(
        cliente, conn, corework, monkeypatch):
    """Con la evidencia ya registrada (por ejemplo, "Adjuntar evidencia" se
    usó antes de tocar "Ya la terminé"), no hay nada que pedir: sigue el
    camino de siempre, directo a la vista previa."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada")
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, uri)
               values (%s, %s, 'explicacion', 'ya está')""", (ws, tid))
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
        assert "en revisión" in fila["resumen"].lower()

        cur.execute(
            """select etiqueta from pending_action_option
                where pending_action_id = %s order by orden""", (fila["id"],))
        assert [f["etiqueta"] for f in cur.fetchall()] == [
            ETIQUETA_CONFIRMAR, "Modificar", ETIQUETA_CANCELAR]


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
        # ADR 0009: "Aprobar" sólo se ofrece con la evidencia ya registrada.
        cur.execute(
            """insert into evidence (workspace_id, task_id, tipo, uri)
               values (%s, %s, 'explicacion', 'ya está')""", (ws, tid))
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
        assert [f["etiqueta"] for f in cur.fetchall()] == _t(
            "Ver detalle", "Ya se destrabó") + [P.ETIQUETA_SALIR_OPCIONES]


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
    token = next(f for f in filas if etiquetas_coinciden(f["etiqueta"], "Empezar"))["token"]

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

    assert filas[0]["etiqueta"] == con_icono("Cablear tablero máq. 3", ICONO_TAREA)
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


# ---------------------------------------------------------------------------
# Revisión del orquestador sobre T2 (`0814fa3`), T2b: `_ejecutar_accion_menu`
# tiene que ser correcta por sí sola -- no depender de que quien la llama la
# envuelva bien -- y no puede dejar la transacción abortada cuando la base
# rechaza la operación.
# ---------------------------------------------------------------------------

def test_ejecutar_accion_menu_deniega_sin_romper_la_respuesta(conn, corework):
    """(1) `_ejecutar_accion_menu` no atrapaba `Denegado`: con el chequeo de
    autoridad nuevo de T2b (`herramientas._preparar_actualizar_estado`), si
    alguien sin autoridad llegara hasta acá (una carrera entre abrir el menú
    y tocarlo, o una futura acción del menú sin ese filtro), la excepción se
    escapaba de la función en vez de avisarle a la persona -- las tres
    funciones que la llaman ya la atajan, pero la función tiene que ser
    correcta también sola."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada", persona="Nahuel Gimenez")
    conn.commit()

    with espacio(conn, ws) as cur:
        ajeno = _quien(cur, "Ariel De Simone", ws)   # ni responsable ni aprobador
        gateway._ejecutar_accion_menu(
            cur, ajeno, ws, 9999, "actualizar_estado",
            {"tarea_id": tid, "estado": "en_curso"}, datetime.now(timezone.utc))

        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"      # nada cambió

        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para desc limit 1""", (9999,))
        fila = cur.fetchone()
        assert fila is not None, "la persona se quedó sin ninguna respuesta"
        assert "no es tuya" in fila["cuerpo"].lower()


def test_ejecutar_accion_menu_recupera_de_un_rechazo_de_la_base(
        conn, corework, monkeypatch):
    """(2) El `except psycopg.errors.RaiseException` corría sin el punto de
    retorno (`cur.connection.transaction`) que sí usa `agente._ejecutar_una`:
    una regla de la base (acá, el disparador que rechaza un ciclo de
    dependencias) deja la transacción abortada, y el `_responder` que sigue
    -- un insert -- fallaba en vez de avisarle a la persona por qué se
    rechazó. Se fuerza `ya_confirmada=True` para llegar hasta el handler real
    (`_ejecutar_accion_menu` nunca lo hace por sí sola sin confirmar) y
    ejercitar el rechazo genuino del disparador, no uno simulado."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        a = _tarea(cur, ws, titulo="Instalar tablero", persona="Marcos Tarquini")
        b = _tarea(cur, ws, titulo="Programar HMI línea 2", persona="Marcos Tarquini")
        # B ya depende de A (A bloqueante para B).
        cur.execute(
            """insert into dependency (workspace_id, origen_task_id, destino_task_id, tipo)
               values (%s, %s, %s, 'bloqueante')""", (ws, a, b))
    conn.commit()

    ejecutar_real = H.ejecutar

    def _forzar_confirmada(cur, quien, nombre, args, **kwargs):
        kwargs["ya_confirmada"] = True
        return ejecutar_real(cur, quien, nombre, args, **kwargs)

    monkeypatch.setattr(H, "ejecutar", _forzar_confirmada)

    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        # Ahora A depende de B -- junto con B ya depende de A, cierra el ciclo.
        gateway._ejecutar_accion_menu(
            cur, marcos, ws, 9998, "crear_dependencia",
            {"origen_tarea_id": b, "destino_tarea_id": a, "tipo": "bloqueante"},
            datetime.now(timezone.utc))

        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para desc limit 1""", (9998,))
        fila = cur.fetchone()
        assert fila is not None, (
            "la respuesta no se pudo encolar tras el rechazo de la base -- "
            "la transacción quedó abortada")
        assert "ciclo" in fila["cuerpo"].lower()

        cur.execute("select count(*) n from dependency where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 1    # sólo la que ya existía


def test_mensaje_resultado_menu_no_dice_no_se_aplico_para_algo_no_reconocido(
        conn, corework):
    """(3) `_mensaje_resultado_menu` colapsaba cualquier resultado que no
    reconociera en "No se aplicó ningún cambio.". Hoy eso nunca pasa en la
    práctica -- las cinco herramientas que ofrece el menú declaran
    `preparar`, y `_ejecutar_accion_menu` nunca pasa `ya_confirmada`, así que
    lo único que puede volver sin excepción es el rechazo de negocio de
    `preparar` (`falta`/`error`) -- pero la función no debe asumirlo para
    cualquier entrada: un resultado que no trae ninguna de esas dos claves
    (por ejemplo, el resultado real de un handler que sí aplicó algo) no
    puede reportarse como "nada cambió" sin poder probarlo.

    Decisión del usuario, 2026-09-25: un error nunca pasa en silencio, ni
    siquiera como una `AssertionError` atrapada lejos de acá -- registra su
    propio incidente y contesta con un aviso neutro, nunca "No se aplicó
    ningún cambio."."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        # `prisma_app` sólo tiene `insert` sobre `incident` (`db/esquema.sql`,
        # "grant insert on ... incident ... to prisma_app"), igual que
        # `task_state_event`: se lee por la conexión administrativa.
        cur.execute("select count(*) n from incident where workspace_id = %s", (ws,))
        antes = cur.fetchone()["n"]

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)

        assert gateway._mensaje_resultado_menu(
            cur, quien, "actualizar_estado", {"error": "x"}) == "x"
        assert gateway._mensaje_resultado_menu(
            cur, quien, "actualizar_estado", {"falta": "y"}) == "y"

        for resultado in ({"estado": "en_curso"}, {"bloqueo_id": "1"}, None):
            texto = gateway._mensaje_resultado_menu(
                cur, quien, "actualizar_estado", resultado)
            assert texto == gateway.NOTICIA_NEUTRA_INCIDENTE
            assert "no se aplicó" not in texto.lower()
    conn.commit()

    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == antes + 3
        cur.execute(
            """select etapa from incident where workspace_id = %s
                order by at desc""", (ws,))
        assert [f["etapa"] for f in cur.fetchall()[:3]] == [gateway.ETAPA_ACCION_MENU] * 3


# ---------------------------------------------------------------------------
# Decisión del usuario, 2026-09-25: un error nunca pasa en silencio. Evidencia
# de la sesión real por Telegram: un `UndefinedColumn` hacía que Prisma
# saltara un mensaje sin ninguna respuesta ni incidente -- invisible hasta que
# alguien lo notaba por otro lado.
# ---------------------------------------------------------------------------

def test_excepcion_no_manejada_en_un_turno_registra_incidente_y_avisa(
        cliente, conn, corework, monkeypatch):
    """Una excepción inesperada dentro de un turno de texto tiene que (a)
    revertir la transacción que falló, (b) registrar un incidente que apunte
    a la causa y (c) avisarle a la persona con un texto neutro, sin ningún
    detalle técnico.

    Corrección del usuario sobre trazabilidad (2026-09-25): el
    `inbound_message` (el recibo de lo que llegó) sobrevive la reversión a
    propósito -- se confirma en su propia fase, antes de interpretar el
    texto -- así el incidente tiene a qué apuntar; lo que se revierte es la
    interpretación (`_turno`), no la constancia de haber recibido algo."""
    ws = corework.workspace_id

    def _explota(cur, quien, texto, workspace_id, chat_id, entrante_id=None):
        raise RuntimeError("falla inesperada de prueba")

    monkeypatch.setattr(gateway, "_turno", _explota)

    with espacio(conn, ws) as cur:
        tg = _telegram_id(cur, "Nahuel Gimenez")
    conn.commit()

    r = _mensaje(cliente, tg, "arranco con esto")
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute(
            "select id from inbound_message where workspace_id = %s", (ws,))
        filas_entrantes = cur.fetchall()
        assert len(filas_entrantes) == 1, (
            "el recibo del mensaje (inbound_message) tiene que sobrevivir: "
            "es la referencia que el incidente necesita para ser trazable")
        entrante_id = str(filas_entrantes[0]["id"])

        cur.execute(
            """select severidad, resumen_sanitizado, referencia_cruda, etapa,
                      referencia_tipo, referencia_id, chat_id, app_user_id,
                      notificado_en, at
                 from incident where workspace_id = %s
                order by at desc limit 1""", (ws,))
        incidente = cur.fetchone()
        assert incidente is not None
        assert incidente["etapa"] == gateway.ETAPA_TURNO_TEXTO
        assert incidente["referencia_tipo"] == gateway.REFERENCIA_INBOUND_MESSAGE
        assert incidente["referencia_id"] == filas_entrantes[0]["id"]
        assert "RuntimeError" in incidente["resumen_sanitizado"]
        assert "falla inesperada de prueba" in incidente["referencia_cruda"]
        assert incidente["chat_id"] == tg
        assert incidente["notificado_en"] is not None    # se avisó
        assert incidente["at"] is not None                # fecha y hora

        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para desc limit 1""", (tg,))
        fila = cur.fetchone()
        assert fila is not None, "la persona se quedó sin ningún aviso"
        assert fila["cuerpo"] == gateway.NOTICIA_NEUTRA_INCIDENTE
        assert entrante_id    # referenciable: el admin puede abrir el texto desde ahí


def test_excepcion_no_manejada_en_un_toque_registra_incidente_y_avisa(
        cliente, conn, corework, monkeypatch):
    """Lo mismo que el turno de texto, pero para un toque de botón: una
    excepción inesperada dentro de `_toque` (acá, dentro del despacho de una
    acción del menú) no puede perderse -- ni la acción pendiente ni la tarea
    quedan a medio aplicar, y la persona recibe un aviso neutro. El
    incidente tiene que apuntar a la `pending_action` que se estaba
    resolviendo (corrección del usuario sobre trazabilidad)."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, estado="asignada", persona="Nahuel Gimenez")
    conn.commit()

    pid_menu, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                      "Nahuel Gimenez")

    def _explota(*args, **kwargs):
        raise RuntimeError("falla inesperada de prueba")

    monkeypatch.setattr(gateway, "_resolver_toque_menu_tarea", _explota)

    token = next(f for f in filas if etiquetas_coinciden(f["etiqueta"], "Empezar"))["token"]
    r = _tocar(cliente, token, tg)
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid_menu,))
        assert cur.fetchone()["estado"] == "esperando"     # nada quedó a medio aplicar

        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"

        cur.execute(
            """select severidad, resumen_sanitizado, referencia_cruda, etapa,
                      referencia_tipo, referencia_id, chat_id, notificado_en
                 from incident where workspace_id = %s
                order by at desc limit 1""", (ws,))
        incidente = cur.fetchone()
        assert incidente is not None
        assert incidente["etapa"] == gateway.ETAPA_TOQUE_BOTON
        assert incidente["referencia_tipo"] == gateway.REFERENCIA_PENDING_ACTION
        assert incidente["referencia_id"] == uuid.UUID(pid_menu)
        assert "RuntimeError" in incidente["resumen_sanitizado"]
        assert "falla inesperada de prueba" in incidente["referencia_cruda"]
        assert incidente["notificado_en"] is not None

        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para desc limit 1""", (tg,))
        fila = cur.fetchone()
        assert fila is not None, "la persona se quedó sin ningún aviso"
        assert fila["cuerpo"] == gateway.NOTICIA_NEUTRA_INCIDENTE


def test_reportar_incidente_no_manejado_no_levanta_si_tambien_falla_el_aviso(
        conn, corework, monkeypatch):
    """Si hasta el intento de avisar falla (p. ej. `enqueue_outbox` levanta),
    el resguardo no puede levantar ni reintentar -- se registra un único
    incidente, con una nota de que el aviso también falló y sin
    `notificado_en`, y no hay ningún loop."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        tg = _telegram_id(cur, "Nahuel Gimenez")
    conn.commit()

    def _explota(*args, **kwargs):
        raise RuntimeError("el envío también falla")

    monkeypatch.setattr(gateway, "enqueue_outbox", _explota)

    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id = %s", (ws,))
        antes = cur.fetchone()["n"]

    # No debe levantar ninguna excepción.
    gateway.reportar_incidente_no_manejado(
        conn, workspace_id=ws, chat_id=tg, tg_user=tg,
        error=RuntimeError("falla original de prueba"), etapa=gateway.ETAPA_TURNO_TEXTO)

    with admin(conn) as cur:
        cur.execute(
            """select resumen_sanitizado, notificado_en, etapa
                 from incident where workspace_id = %s
                order by at""", (ws,))
        filas = cur.fetchall()
        assert len(filas) == antes + 1    # una sola fila, no dos
        nueva = filas[-1]
        assert "Excepción no manejada" in nueva["resumen_sanitizado"]
        assert "también falló el aviso" in nueva["resumen_sanitizado"].lower() \
            or "falló el envío del aviso" in nueva["resumen_sanitizado"].lower()
        assert nueva["notificado_en"] is None
        assert nueva["etapa"] == gateway.ETAPA_TURNO_TEXTO


def test_reportar_incidente_no_manejado_no_marca_avisado_si_no_identifica(
        conn, corework):
    """Si la persona no se identifica en el espacio, nadie recibió el aviso:
    el incidente no puede quedar con `notificado_en` (observación de la
    revisión de T2b -- marcarlo sería mentir) y no se encola nada."""
    ws = corework.workspace_id
    desconocido = 987654321012

    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox where chat_id = %s",
                    (desconocido,))
        outbox_antes = cur.fetchone()["n"]

    gateway.reportar_incidente_no_manejado(
        conn, workspace_id=ws, chat_id=desconocido, tg_user=desconocido,
        error=RuntimeError("falla original de prueba"), etapa=gateway.ETAPA_TURNO_TEXTO)

    with admin(conn) as cur:
        cur.execute(
            """select resumen_sanitizado, notificado_en, app_user_id
                 from incident where workspace_id = %s
                order by at desc limit 1""", (ws,))
        nueva = cur.fetchone()
        assert nueva["notificado_en"] is None
        assert nueva["app_user_id"] is None
        assert "no se identificó en el espacio" in nueva["resumen_sanitizado"]

        cur.execute("select count(*) n from message_outbox where chat_id = %s",
                    (desconocido,))
        assert cur.fetchone()["n"] == outbox_antes
