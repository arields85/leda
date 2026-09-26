"""Cierre genérico de una pregunta sin opciones (T4b, `prisma-orienta`; ADR
0007 "Prisma orienta, no charla").

Decisión del usuario (2026-09-26, evidencia
`tests/banco/reportes/replay-candidato-b-0007-*.json`): cuando Prisma
necesita algo de la persona pero termina el turno preguntando en texto
abierto sin ofrecer ningún botón propio, el servidor agrega un juego FIJO de
tres botones -- "Es una tarea nueva", "Es sobre una tarea existente",
"Quiero consultar otra cosa" -- en vez de dejar pasar la pregunta abierta.
Reusa el mecanismo de T1 (`pendientes.SENTINEL_OPCIONES_MODELO`); las tres
opciones se resuelven en `gateway._resolver_toque_opcion_modelo` por su
`tipo`.

Los toques se simulan con `gateway.procesar_update` y un `callback_query`,
igual que `tests/test_opciones_modelo.py`.
"""

from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import gateway
from prisma import pendientes as P
from prisma.agente import responder
from prisma.autoridad import Canal, identificar
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.llm import Llamada, ProveedorGuionado, Respuesta
from prisma.salida import BUTTON_TEXT_LIMIT, telegram_utf16_units

ETIQUETAS_CIERRE_GENERICO = ["Es una tarea nueva", "Es sobre una tarea existente",
                            "Quiero consultar otra cosa"]


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _telegram_id(cur, nombre) -> int:
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return cur.fetchone()["t"]


def _tarea(cur, ws, *, titulo="Cablear tablero máq. 3", area="electricidad",
          persona="Marcos Tarquini", estado="asignada", dias_para_vencer=None):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Objetivo de prueba') returning id""", (ws,))
    obj = cur.fetchone()["id"]
    vence = (datetime.now(timezone.utc) + timedelta(days=dias_para_vencer)
             if dias_para_vencer is not None else None)
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, criterio_aceptacion,
                             evidencia_requerida, fecha_objetivo)
           values (%s, %s, %s,
                   (select id from area where workspace_id = %s and slug = %s),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                    'Criterio de prueba', array['explicacion'], %s)
           returning id""",
        (ws, obj, titulo, ws, area, ws, persona, vence))
    t = cur.fetchone()["id"]
    cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                "values (%s, %s, 'prisma')", (t, estado))
    return str(t)


def _entrante(cur, ws, quien, chat_id, texto) -> str:
    """Un `inbound_message` persistido, como el que arma `procesar_update`
    antes de rutear -- lo necesita el alta guiada al tocar "Es una tarea
    nueva" (`gateway._iniciar_alta_guiada`), igual que
    `tests/test_aclaracion_botones.py`."""
    cur.execute(
        """insert into inbound_message (workspace_id, chat_id, app_user_id, texto)
           values (%s, %s, %s, %s) returning id""",
        (ws, chat_id, quien.app_user_id, texto))
    return str(cur.fetchone()["id"])


def _con_proveedor(monkeypatch, guion):
    proveedor = ProveedorGuionado(guion=list(guion))
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


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


def _opciones(cur, pid):
    cur.execute(
        """select token, etiqueta, valor from pending_action_option
            where pending_action_id = %s order by orden""", (pid,))
    return cur.fetchall()


def _pendiente_opciones(cur, ws) -> str:
    cur.execute(
        """select id from pending_action
            where workspace_id = %s and herramienta = %s and estado = 'esperando'
            order by creado_en desc limit 1""",
        (ws, P.SENTINEL_OPCIONES_MODELO))
    return str(cur.fetchone()["id"])


# ---------------------------------------------------------------------------
# El cierre genérico se agrega sólo cuando el turno cierra preguntando
# ---------------------------------------------------------------------------

def test_pregunta_abierta_sin_botones_agrega_el_cierre_generico(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    guion = [Respuesta(texto="¿De qué se trata? Contame por lo del proveedor.")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        entrante_id = _entrante(cur, ws, quien, 1, "necesito el contacto del proveedor")
        r = responder(cur, quien, "necesito el contacto del proveedor", proveedor,
                     cal, chat_id=1, ahora=datetime.now(timezone.utc),
                     entrante_id=entrante_id)
        assert r.texto == "¿De qué se trata? Contame por lo del proveedor."

        pid = _pendiente_opciones(cur, ws)
        etiquetas = [f["etiqueta"] for f in _opciones(cur, pid)]

    assert etiquetas == ETIQUETAS_CIERRE_GENERICO


def test_aviso_sin_pregunta_no_agrega_botones(corework, conn, monkeypatch):
    ws = corework.workspace_id
    guion = [Respuesta(texto="Listo, ya quedó anotado.")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "avisame", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        assert r.texto == "Listo, ya quedó anotado."

        cur.execute("select count(*) n from pending_action where herramienta = %s",
                    (P.SENTINEL_OPCIONES_MODELO,))
        assert cur.fetchone()["n"] == 0


def test_pedido_de_eleccion_en_imperativo_tambien_agrega_el_cierre(
        corework, conn, monkeypatch):
    """Sin "?": "Decime cuál..." ya cuenta como pregunta (misma detección
    que el banco, `deteccion_pregunta.hace_pregunta`)."""
    ws = corework.workspace_id
    guion = [Respuesta(texto="Decime cuál de las dos preferís y seguimos.")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "algo", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        etiquetas = [f["etiqueta"] for f in _opciones(cur, pid)]

    assert etiquetas == ETIQUETAS_CIERRE_GENERICO


# ---------------------------------------------------------------------------
# Nunca dos juegos de botones en el mismo turno
# ---------------------------------------------------------------------------

def test_lista_de_tareas_con_pregunta_no_agrega_el_cierre_generico(
        corework, conn, monkeypatch):
    """T3 (lista de tareas) y T4b (cierre genérico) compiten por el mismo
    turno cuando el modelo lista tareas Y cierra preguntando -- T3 tiene que
    ganar siempre (rama `elif` en `agente.responder`), nunca dos
    `pending_action` de `SENTINEL_OPCIONES_MODELO` en el mismo turno."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Tarea 1", dias_para_vencer=1)
        _tarea(cur, ws, titulo="Tarea 2", dias_para_vencer=2)
    conn.commit()

    guion = [Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
            Respuesta(texto="Tenés 2 tareas. ¿Cuál encarás primero?")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "qué tengo pendiente", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))

        cur.execute("select count(*) n from pending_action where herramienta = %s",
                    (P.SENTINEL_OPCIONES_MODELO,))
        assert cur.fetchone()["n"] == 1

        pid = _pendiente_opciones(cur, ws)
        etiquetas = [f["etiqueta"] for f in _opciones(cur, pid)]

    # La lista de T3, no el cierre genérico de T4b.
    assert etiquetas == ["Tarea 1", "Tarea 2", "Quiero consultar otra cosa"]


def test_ofrecer_opciones_no_agrega_el_cierre_generico(corework, conn, monkeypatch):
    """El turno cierra por `elecciones` (T1, `ofrecer_opciones`) antes de
    llegar al cálculo de `salida`/`hace_pregunta` -- nunca compite."""
    ws = corework.workspace_id
    guion = [Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿Cuál preferís?",
        "opciones": [{"texto": "A"}, {"texto": "B"}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "algo", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        assert r.elecciones == ["ofrecer_opciones"]

        cur.execute("select count(*) n from pending_action where herramienta = %s",
                    (P.SENTINEL_OPCIONES_MODELO,))
        assert cur.fetchone()["n"] == 1

        pid = _pendiente_opciones(cur, ws)
        etiquetas = [f["etiqueta"] for f in _opciones(cur, pid)]

    assert etiquetas == ["A", "B", "Quiero consultar otra cosa"]


# ---------------------------------------------------------------------------
# Una respuesta larga se parte; los botones cortos van aparte
# ---------------------------------------------------------------------------

def test_pregunta_larga_se_parte_y_los_botones_van_aparte(corework, conn, monkeypatch):
    oracion = "No encuentro ninguna tarea que coincida con lo que contás. "
    texto_largo = (oracion * 70) + "¿De qué se trata?"
    assert telegram_utf16_units(texto_largo) > BUTTON_TEXT_LIMIT

    ws = corework.workspace_id
    guion = [Respuesta(texto=texto_largo)]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "lo del proveedor", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        assert not r.incidente

        cur.execute(
            """select cuerpo, pending_action_id, programado_para
                 from message_outbox where workspace_id = %s and chat_id = %s
                order by programado_para""", (ws, 1))
        filas = cur.fetchall()
        pid = _pendiente_opciones(cur, ws)
        etiquetas = [f["etiqueta"] for f in _opciones(cur, pid)]

    partes_texto = [f for f in filas if f["pending_action_id"] is None]
    mensajes_botones = [f for f in filas if f["pending_action_id"] is not None]

    assert len(partes_texto) >= 2
    assert len(mensajes_botones) == 1
    assert mensajes_botones[0]["cuerpo"] == "Elegí una opción:"
    assert (max(f["programado_para"] for f in partes_texto)
           < mensajes_botones[0]["programado_para"])
    assert etiquetas == ETIQUETAS_CIERRE_GENERICO


def test_pregunta_corta_sigue_yendo_junto_con_los_botones(corework, conn, monkeypatch):
    ws = corework.workspace_id
    guion = [Respuesta(texto="¿De qué se trata?")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "lo del proveedor", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        cur.execute(
            """select cuerpo, pending_action_id from message_outbox
                where workspace_id = %s and chat_id = %s""", (ws, 1))
        filas = cur.fetchall()

    assert len(filas) == 1
    assert filas[0]["pending_action_id"] is not None
    assert filas[0]["cuerpo"] == "¿De qué se trata?"


# ---------------------------------------------------------------------------
# "Es una tarea nueva": arranca la misma alta guiada
# ---------------------------------------------------------------------------

def test_tocar_es_una_tarea_nueva_arranca_el_alta_guiada(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    guion = [Respuesta(texto="¿De qué tarea hablamos? No la encuentro.")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        tg = _telegram_id(cur, "Marcos Tarquini")
        cal = Calendario.desde_base(cur, ws)
        entrante_id = _entrante(cur, ws, quien, tg, "lo del proveedor")
        responder(cur, quien, "lo del proveedor", proveedor, cal, chat_id=tg,
                 ahora=datetime.now(timezone.utc), entrante_id=entrante_id)
        pid = _pendiente_opciones(cur, ws)
        nueva = next(o for o in _opciones(cur, pid)
                    if o["etiqueta"] == "Es una tarea nueva")

    assert _tocar(cliente, nueva["token"], tg).status_code == 200

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from task_intake_request where workspace_id = %s",
            (ws,))
        assert cur.fetchone()["n"] == 1


def test_tocar_es_una_tarea_nueva_sin_entrante_id_no_falla_en_silencio(
        cliente, conn, corework, monkeypatch):
    """Si el turno que armó el cierre genérico no tenía un `inbound_message`
    propio (p. ej. retomó otra opción), el alta guiada no se puede arrancar
    -- `gateway._iniciar_alta_guiada` ya registra incidente + aviso neutro
    (patrón existente); nunca se inventa un mensaje de origen ni se cae en
    silencio."""
    ws = corework.workspace_id
    guion = [Respuesta(texto="¿De qué tarea hablamos?")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        tg = _telegram_id(cur, "Marcos Tarquini")
        cal = Calendario.desde_base(cur, ws)
        # Sin `entrante_id`: simula un turno que no vino de un mensaje
        # persistido (por ejemplo, al retomar otra opción).
        responder(cur, quien, "lo del proveedor", proveedor, cal, chat_id=tg,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        nueva = next(o for o in _opciones(cur, pid)
                    if o["etiqueta"] == "Es una tarea nueva")

    with admin(conn) as cur:
        cur.execute("select count(*) n from incident")
        incidentes_antes = cur.fetchone()["n"]

    assert _tocar(cliente, nueva["token"], tg).status_code == 200

    with admin(conn) as cur:
        cur.execute("select count(*) n from task_intake_request where workspace_id = %s",
                    (ws,))
        assert cur.fetchone()["n"] == 0

        cur.execute("select count(*) n from incident")
        assert cur.fetchone()["n"] == incidentes_antes + 1

        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para desc limit 1""", (tg,))
        aviso = cur.fetchone()["cuerpo"]
    assert "no pude" in aviso.lower()


# ---------------------------------------------------------------------------
# "Es sobre una tarea existente": lista las tareas activas de la persona
# ---------------------------------------------------------------------------

def test_tocar_es_sobre_una_tarea_existente_lista_las_propias_y_abre_el_menu(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero máq. 3", dias_para_vencer=1)
        _tarea(cur, ws, titulo="Revisar accesos VPN", dias_para_vencer=2)
    conn.commit()

    guion = [Respuesta(texto="¿De qué tarea hablamos?")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        tg = _telegram_id(cur, "Marcos Tarquini")
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "lo del proveedor", proveedor, cal, chat_id=tg,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        existente = next(o for o in _opciones(cur, pid)
                         if o["etiqueta"] == "Es sobre una tarea existente")

    assert _tocar(cliente, existente["token"], tg).status_code == 200

    with admin(conn) as cur:
        pid2 = _pendiente_opciones(cur, ws)
        filas = _opciones(cur, pid2)
    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == ["Cablear tablero máq. 3", "Revisar accesos VPN",
                        "Quiero consultar otra cosa"]
    tarea1 = next(f for f in filas if f["etiqueta"] == "Cablear tablero máq. 3")
    assert tarea1["valor"] == {"tipo": "tarea", "tarea_id": tid,
                              "titulo": "Cablear tablero máq. 3", "accion": "menu"}

    # Tocarla abre el menú de T2, no retoma la conversación con el modelo.
    llamadas_antes = len(proveedor.recibidos)
    assert _tocar(cliente, tarea1["token"], tg).status_code == 200
    assert len(proveedor.recibidos) == llamadas_antes

    with admin(conn) as cur:
        cur.execute(
            """select id from pending_action
                where workspace_id = %s and herramienta = %s and estado = 'esperando'
                order by creado_en desc limit 1""",
            (ws, P.SENTINEL_MENU_TAREA))
        pid_menu = str(cur.fetchone()["id"])
        etiquetas_menu = [f["etiqueta"] for f in _opciones(cur, pid_menu)]
    assert "Ver detalle" in etiquetas_menu


def test_tocar_es_sobre_una_tarea_existente_pagina_con_mas_de_cuatro(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        for n in range(1, 7):
            _tarea(cur, ws, titulo=f"Tarea propia {n}", dias_para_vencer=n)
    conn.commit()

    guion = [Respuesta(texto="¿De qué tarea hablamos?")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        tg = _telegram_id(cur, "Marcos Tarquini")
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "lo del proveedor", proveedor, cal, chat_id=tg,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        existente = next(o for o in _opciones(cur, pid)
                         if o["etiqueta"] == "Es sobre una tarea existente")

    assert _tocar(cliente, existente["token"], tg).status_code == 200

    with admin(conn) as cur:
        pid2 = _pendiente_opciones(cur, ws)
        etiquetas = [f["etiqueta"] for f in _opciones(cur, pid2)]
    assert etiquetas == ["Tarea propia 1", "Tarea propia 2", "Tarea propia 3",
                        "Tarea propia 4", "Ver más", "Quiero consultar otra cosa"]


def test_tocar_es_sobre_una_tarea_existente_sin_tareas_activas_dice_que_no_hay(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    guion = [Respuesta(texto="¿De qué tarea hablamos?")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        tg = _telegram_id(cur, "Marcos Tarquini")
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "lo del proveedor", proveedor, cal, chat_id=tg,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        existente = next(o for o in _opciones(cur, pid)
                         if o["etiqueta"] == "Es sobre una tarea existente")

    assert _tocar(cliente, existente["token"], tg).status_code == 200

    with admin(conn) as cur:
        pid2 = _pendiente_opciones(cur, ws)
        filas = _opciones(cur, pid2)
        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para desc limit 1""", (tg,))
        cuerpo = cur.fetchone()["cuerpo"]
    assert [f["etiqueta"] for f in filas] == ["Quiero consultar otra cosa"]
    assert "no ten" in cuerpo.lower()


# ---------------------------------------------------------------------------
# "Quiero consultar otra cosa": el mismo cierre de siempre (T1)
# ---------------------------------------------------------------------------

def test_tocar_salida_del_cierre_generico_cierra_sin_efecto(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    guion = [Respuesta(texto="¿De qué se trata?")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        tg = _telegram_id(cur, "Marcos Tarquini")
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "algo", proveedor, cal, chat_id=tg,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        salir = next(o for o in _opciones(cur, pid)
                    if o["etiqueta"] == "Quiero consultar otra cosa")

    llamadas_antes = len(proveedor.recibidos)
    assert _tocar(cliente, salir["token"], tg).status_code == 200
    assert len(proveedor.recibidos) == llamadas_antes

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid,))
        assert cur.fetchone()["estado"] == "resuelta"


# ---------------------------------------------------------------------------
# Auditoría de los toques: sólo el tipo, nunca texto
# ---------------------------------------------------------------------------

def test_auditoria_de_los_toques_del_cierre_generico_no_lleva_texto(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    guion = [Respuesta(texto="¿De qué tarea hablamos con el secreto de más?")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        tg = _telegram_id(cur, "Marcos Tarquini")
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "algo con el secreto de más", proveedor, cal,
                 chat_id=tg, ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        existente = next(o for o in _opciones(cur, pid)
                         if o["etiqueta"] == "Es sobre una tarea existente")

    assert _tocar(cliente, existente["token"], tg).status_code == 200

    with admin(conn) as cur:
        cur.execute(
            "select detalle from audit_log where accion = 'eleccion_opciones_modelo'")
        fila = cur.fetchone()
    assert fila["detalle"] == {"tipo": "tarea_existente", "tarea_id": None}
    assert "secreto" not in str(fila["detalle"]).lower()
