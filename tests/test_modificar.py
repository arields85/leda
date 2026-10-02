"""Modificar (T3, ADR 0005 decisión 1).

Tapping Modificar en la vista previa de una herramienta que escribe no aplica
nada: cierra esa propuesta y deja registrado, para esa persona y ese chat, que
el próximo mensaje de texto es una corrección. Ese próximo turno recibe la
propuesta anterior como contexto del servidor -- no como texto de la persona
-- y produce una vista previa nueva por el camino normal de siempre
(preparar → confirmar).
"""

from __future__ import annotations

import dataclasses
from contextlib import nullcontext
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from tests.toques import id_de_mensaje
from leda import gateway
from leda import herramientas as H
from leda import pendientes as P
from leda.salida import (ETIQUETA_CANCELAR, ETIQUETA_CONFIRMAR,
                           ETIQUETA_MODIFICAR)
from leda.agente import responder
from leda.autoridad import Canal, Denegado, identificar
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.llm import Llamada, ProveedorGuionado, Respuesta

BA = ZoneInfo("America/Argentina/Buenos_Aires")
AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _telegram_id(cur, nombre) -> int:
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return cur.fetchone()["t"]


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


def _proponer(cur, ws, quien, herramienta, args, *, chat_id=9100, ahora=AHORA):
    """Deja una vista previa de una herramienta que escribe, sin confirmar."""
    cal = Calendario.desde_base(cur, ws)
    guion = [Respuesta(llamadas=[Llamada("c1", herramienta, dict(args))]),
             Respuesta(texto="listo")]
    r = responder(cur, quien, "hacé esto", ProveedorGuionado(guion), cal,
                  chat_id=chat_id, ahora=ahora)
    assert r.confirmaciones == [herramienta]
    cur.execute(
        """select id from pending_action
            where herramienta = %s and estado = 'esperando'
            order by creado_en desc limit 1""", (herramienta,))
    return str(cur.fetchone()["id"])


# ---------------------------------------------------------------------------
# Los tres botones, en orden -- y sólo en la vista previa de una herramienta
# que escribe.
# ---------------------------------------------------------------------------

def test_los_tres_botones_aparecen_en_orden_en_la_herramienta_que_escribe(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        pid = _proponer(cur, ws, quien, "registrar_bloqueo",
                        {"tarea_id": tid, "causa": "falta el switch"})

        cur.execute(
            """select etiqueta from pending_action_option
                where pending_action_id = %s order by orden""", (pid,))
        etiquetas = [f["etiqueta"] for f in cur.fetchall()]
        assert etiquetas == [ETIQUETA_CONFIRMAR, ETIQUETA_MODIFICAR, ETIQUETA_CANCELAR]


def test_la_confirmacion_vieja_sin_preparar_sigue_con_dos_botones(
        corework, conn):
    """Una NecesitaConfirmacion sin huella (herramienta sin `preparar`, la
    lista `REQUIEREN_CONFIRMACION` que hoy no usa ninguna de las 8) no gana
    el botón Modificar: sigue siendo Confirmar/Cancelar, como antes de T3."""
    from leda.agente import _encolar_confirmacion

    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        e = H.NecesitaConfirmacion("algo para confirmar", "cambiar_fecha",
                                   {"tarea_id": "x"})
        assert e.huella is None
        _encolar_confirmacion(cur, quien, 9100, e, cal, AHORA)

        cur.execute(
            """select o.etiqueta from pending_action_option o
                 join pending_action p on p.id = o.pending_action_id
                where p.herramienta = 'cambiar_fecha' order by o.orden""")
        etiquetas = [f["etiqueta"] for f in cur.fetchall()]
        assert etiquetas == [ETIQUETA_CONFIRMAR, ETIQUETA_CANCELAR]


def test_elegir_entre_personas_no_lleva_los_botones_de_confirmacion(
        corework, conn):
    """`NecesitaElegir` (candidatos ambiguos) mantiene sus propios botones:
    un nombre por opción, no Confirmar/Modificar/Cancelar."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        p = P.registrar(
            cur, quien, herramienta="crear_tarea",
            args={"titulo": "Relevar tablero"}, resumen="¿a quién?",
            vence_en=AHORA + timedelta(hours=2), campo="responsable_membership_id",
            opciones=[("Marcos Tarquini", "m1"), ("Martín Forte", "m2")])

        cur.execute(
            """select etiqueta from pending_action_option
                where pending_action_id = %s order by orden""", (p.id,))
        etiquetas = [f["etiqueta"] for f in cur.fetchall()]
        assert etiquetas == ["Marcos Tarquini", "Martín Forte"]


# ---------------------------------------------------------------------------
# Modificar no aplica nada y cierra la propuesta.
# ---------------------------------------------------------------------------

def test_modificar_no_aplica_nada_y_cierra_la_propuesta(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        pid = _proponer(cur, ws, quien, "registrar_bloqueo",
                        {"tarea_id": tid, "causa": "falta el switch"})
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")

        r = P.resolver(cur, modificar.token, app_user_id=quien.app_user_id,
                       ahora=AHORA)

        assert r is not None
        assert r.modificada is True
        assert r.cancelada is False
        assert r.herramienta == "registrar_bloqueo"
        assert r.args["causa"] == "falta el switch"

        cur.execute("select count(*) n from blocker where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0, "Modificar no crea el bloqueo"

        cur.execute(
            "select estado, modificar_pedido_en from pending_action where id = %s",
            (pid,))
        fila = cur.fetchone()
        assert fila["estado"] == "cancelada"
        assert fila["modificar_pedido_en"] is not None


def test_modificar_dos_veces_no_hace_nada_la_segunda(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        pid = _proponer(cur, ws, quien, "registrar_bloqueo",
                        {"tarea_id": tid, "causa": "falta el switch"})
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")

        primera = P.resolver(cur, modificar.token,
                             app_user_id=quien.app_user_id, ahora=AHORA)
        segunda = P.resolver(cur, modificar.token,
                             app_user_id=quien.app_user_id, ahora=AHORA)

        assert primera is not None
        assert segunda is None


def test_modificar_de_otro_integrante_no_se_puede(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        marcos = _quien(cur, "Marcos Tarquini", ws)
        otro = _quien(cur, "Ariel De Simone", ws)
        pid = _proponer(cur, ws, marcos, "registrar_bloqueo",
                        {"tarea_id": tid, "causa": "falta el switch"})
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")

        with pytest.raises(Denegado):
            P.resolver(cur, modificar.token, app_user_id=otro.app_user_id,
                      ahora=AHORA)

        assert P.buscar(cur, pid).estado == "esperando"


def test_modificar_vencida_no_se_puede(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        pid = _proponer(cur, ws, quien, "registrar_bloqueo",
                        {"tarea_id": tid, "causa": "falta el switch"})
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")

        r = P.resolver(cur, modificar.token, app_user_id=quien.app_user_id,
                       ahora=AHORA + timedelta(hours=9))

        assert r is None
        assert P.buscar(cur, pid).estado == "vencida"


# ---------------------------------------------------------------------------
# El contexto de modificación: un solo uso, y desaparece si no se usa.
# ---------------------------------------------------------------------------

def test_reclamar_modificacion_abierta_es_de_un_solo_uso(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        pid = _proponer(cur, ws, quien, "registrar_bloqueo",
                        {"tarea_id": tid, "causa": "falta el switch"},
                        chat_id=9100)
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")
        P.resolver(cur, modificar.token, app_user_id=quien.app_user_id,
                  ahora=AHORA)

        primera = P.reclamar_modificacion_abierta(cur, quien, 9100, AHORA)
        segunda = P.reclamar_modificacion_abierta(cur, quien, 9100, AHORA)

        assert primera is not None
        assert primera.pregunta_id == pid
        assert primera.herramienta == "registrar_bloqueo"
        assert primera.args["causa"] == "falta el switch"
        assert "Todavía no se aplicó ningún cambio." in primera.resumen
        assert segunda is None, "se consume la primera vez que se lee"


def test_reclamar_modificacion_abierta_ignora_una_ya_vencida(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        pid = _proponer(cur, ws, quien, "registrar_bloqueo",
                        {"tarea_id": tid, "causa": "falta el switch"},
                        chat_id=9100)
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")
        P.resolver(cur, modificar.token, app_user_id=quien.app_user_id,
                  ahora=AHORA)

        tarde = P.reclamar_modificacion_abierta(
            cur, quien, 9100, AHORA + timedelta(hours=9))
        assert tarde is None


def _reclamar_despues_de(conn, ws, espera: timedelta):
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        pid = _proponer(cur, ws, quien, "registrar_bloqueo",
                        {"tarea_id": tid, "causa": "falta el switch"}, chat_id=9100)
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")
        P.resolver(cur, modificar.token, app_user_id=quien.app_user_id, ahora=AHORA)
        return P.reclamar_modificacion_abierta(cur, quien, 9100, AHORA + espera)


def test_la_modificacion_sigue_abierta_dentro_de_la_ventana(corework, conn):
    abierta = _reclamar_despues_de(conn, corework.workspace_id, timedelta(minutes=29))
    assert abierta is not None


def test_la_modificacion_se_cierra_pasada_la_ventana(corework, conn):
    # La propuesta vence a las 8 h, pero la corrección tiene que llegar pronto:
    # un mensaje de horas después es otra conversación y no puede saltear el
    # enrutador de intención.
    tarde = _reclamar_despues_de(conn, corework.workspace_id, timedelta(minutes=31))
    assert tarde is None


def test_reclamar_modificacion_abierta_solo_ve_la_mas_reciente(corework, conn):
    """Una Modificación nueva invalida cualquier otra que quedó sin leer: un
    mensaje posterior nunca se aplica a una propuesta vieja."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        t1 = _tarea(cur, ws, titulo="Programar PLC")
        t2 = _tarea(cur, ws, titulo="Cablear tablero")
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        p1 = _proponer(cur, ws, quien, "registrar_bloqueo",
                       {"tarea_id": t1, "causa": "primera"}, chat_id=9100)
        m1 = P.opcion_por_etiqueta(cur, p1, "Modificar")
        P.resolver(cur, m1.token, app_user_id=quien.app_user_id, ahora=AHORA)

        p2 = _proponer(cur, ws, quien, "registrar_bloqueo",
                       {"tarea_id": t2, "causa": "segunda"}, chat_id=9100)
        m2 = P.opcion_por_etiqueta(cur, p2, "Modificar")
        P.resolver(cur, m2.token, app_user_id=quien.app_user_id,
                  ahora=AHORA + timedelta(seconds=1))

        reclamada = P.reclamar_modificacion_abierta(
            cur, quien, 9100, AHORA + timedelta(seconds=2))
        assert reclamada is not None
        assert reclamada.pregunta_id == p2
        assert reclamada.args["causa"] == "segunda"

        otra_vez = P.reclamar_modificacion_abierta(
            cur, quien, 9100, AHORA + timedelta(seconds=3))
        assert otra_vez is None, "la primera quedó invalidada, no disponible después"


# ---------------------------------------------------------------------------
# El próximo turno: la corrección produce una vista previa nueva.
# ---------------------------------------------------------------------------

def test_la_correccion_produce_una_vista_previa_nueva_con_el_cambio_corregido(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        pid = _proponer(cur, ws, quien, "registrar_bloqueo",
                        {"tarea_id": tid, "causa": "falta el switch"},
                        chat_id=9100)
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")
        P.resolver(cur, modificar.token, app_user_id=quien.app_user_id,
                  ahora=AHORA)

        modificacion = P.reclamar_modificacion_abierta(cur, quien, 9100, AHORA)
        assert modificacion is not None

        cal = Calendario.desde_base(cur, ws)
        guion = [Respuesta(llamadas=[Llamada(
                     "c2", "registrar_bloqueo",
                     {"tarea_id": tid, "causa": "falta el cable, no el switch"})]),
                 Respuesta(texto="listo")]
        r = responder(cur, quien, "en realidad es el cable", ProveedorGuionado(guion),
                     cal, chat_id=9100, ahora=AHORA, modificacion=modificacion)

        assert r.confirmaciones == ["registrar_bloqueo"]
        cur.execute(
            """select id, resumen from pending_action
                where herramienta = 'registrar_bloqueo' and estado = 'esperando'""")
        filas = cur.fetchall()
        assert len(filas) == 1, "exactamente una vista previa nueva"
        assert "falta el cable, no el switch" in filas[0]["resumen"]

        cur.execute("select count(*) n from blocker where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0, "la corrección tampoco aplica nada sola"

        nuevo_pid = str(filas[0]["id"])
        confirmar = P.opcion_por_etiqueta(cur, nuevo_pid, "Confirmar")
        resuelta = P.resolver(cur, confirmar.token,
                             app_user_id=quien.app_user_id, ahora=AHORA)
        H.ejecutar(cur, quien, resuelta.herramienta, resuelta.args,
                  ya_confirmada=True, chat_id=9100, huella_previa=resuelta.huella)

        cur.execute("select causa from blocker where task_id = %s", (tid,))
        assert cur.fetchone()["causa"] == "falta el cable, no el switch"


def test_un_mensaje_sin_relacion_no_aplica_la_propuesta_vieja(corework, conn):
    """Si la respuesta al turno con contexto de modificación no vuelve a
    llamar a la herramienta, la propuesta vieja sigue cerrada y no hay
    ningún efecto: el modelo decidió que el mensaje era sobre otra cosa."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        pid = _proponer(cur, ws, quien, "registrar_bloqueo",
                        {"tarea_id": tid, "causa": "falta el switch"},
                        chat_id=9100)
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")
        P.resolver(cur, modificar.token, app_user_id=quien.app_user_id,
                  ahora=AHORA)
        modificacion = P.reclamar_modificacion_abierta(cur, quien, 9100, AHORA)

        cal = Calendario.desde_base(cur, ws)
        guion = [Respuesta(texto="¿cómo viene el resto del día?")]
        responder(cur, quien, "¿cómo viene el resto del día?",
                 ProveedorGuionado(guion), cal, chat_id=9100, ahora=AHORA,
                 modificacion=modificacion)

        cur.execute("select count(*) n from blocker where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0
        cur.execute(
            "select estado from pending_action where herramienta = 'registrar_bloqueo'")
        assert [f["estado"] for f in cur.fetchall()] == ["cancelada"]


# ---------------------------------------------------------------------------
# De punta a punta por el webhook.
# ---------------------------------------------------------------------------

@pytest.fixture
def cliente(corework, conn, monkeypatch):
    monkeypatch.setattr(gateway, "acusar_toque", lambda *a, **k: None)
    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
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
        json={"message": {"message_id": id_de_mensaje(), "text": texto,
                          "chat": {"id": user_id}, "from": {"id": user_id}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def test_de_punta_a_punta_tocar_modificar_pregunta_y_la_correccion_arma_vista_previa(
        cliente, conn, corework, monkeypatch):
    from datetime import timezone as _tz

    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea = _tarea(cur, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        pid = _proponer(cur, ws, quien, "registrar_bloqueo",
                        {"tarea_id": tarea, "causa": "falta el switch"},
                        chat_id=_telegram_id(cur, "Marcos Tarquini"),
                        ahora=datetime.now(_tz.utc))
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")
        tg = _telegram_id(cur, "Marcos Tarquini")
    conn.commit()

    assert _tocar(cliente, modificar.token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado, modificar_pedido_en from pending_action where id = %s",
                    (pid,))
        fila = cur.fetchone()
        assert fila["estado"] == "cancelada"
        assert fila["modificar_pedido_en"] is not None
        cur.execute(
            "select cuerpo from message_outbox where chat_id = %s order by programado_para desc limit 1",
            (tg,))
        assert cur.fetchone()["cuerpo"] == "¿Qué querés cambiar?"
        cur.execute("select count(*) n from blocker where task_id = %s", (tarea,))
        assert cur.fetchone()["n"] == 0

    guion = [Respuesta(llamadas=[Llamada(
                 "c2", "registrar_bloqueo",
                 {"tarea_id": tarea, "causa": "falta el cable"})]),
             Respuesta(texto="listo")]
    monkeypatch.setattr(
        "leda.llm.desde_base",
        lambda cur, ws, key: ProveedorGuionado(guion))

    assert _mensaje(cliente, tg, "en realidad es el cable").status_code == 200

    with admin(conn) as cur:
        cur.execute(
            """select id, resumen from pending_action
                where herramienta = 'registrar_bloqueo' and estado = 'esperando'""")
        filas = cur.fetchall()
        assert len(filas) == 1
        assert "falta el cable" in filas[0]["resumen"]
        cur.execute("select count(*) n from blocker where task_id = %s", (tarea,))
        assert cur.fetchone()["n"] == 0, "la corrección tampoco aplica sola"
