"""Aclaración con botones (T4, `aclaracion-con-botones`; ADR 0005 decisión 3,
ADR 0006).

Antes de esta unidad (T3), una referencia ambigua con candidatas reales hacía
que el modelo preguntara en texto. Acá en cambio se ofrecen botones: uno por
candidata (la propia primero, sin nombre; la ajena con el primer nombre del
responsable), "Es una tarea nueva" en el caso mixto de b-0005, y "Ninguna, lo
escribo" siempre al final. Elegir retoma el mensaje original -- sin aplicar
nada -- y termina en la vista previa de siempre (Confirmar/Modificar/
Cancelar) o, si queda otra referencia ambigua, en la próxima pregunta.

Los toques se simulan con `gateway.procesar_update` y un `callback_query`,
igual que `tests/test_botones.py` y `tests/test_modificar.py`.
"""

from __future__ import annotations

import dataclasses
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import gateway
from prisma import herramientas as H
from prisma import jev as jev_modulo
from prisma import pendientes as P
from prisma.autoridad import Canal, identificar
from prisma.db import admin, espacio
from prisma.jev import ClienteJevGuionado
from prisma.llm import (IntentAction, IntentRoute, Llamada, ProveedorGuionado,
                        Respuesta)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _telegram_id(cur, nombre) -> int:
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return cur.fetchone()["t"]


def _tarea(cur, ws, *, titulo="Cablear tablero máq. 3", area="electricidad",
          persona="Mariano Naim", estado="asignada"):
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


def _alcance(una_tarea=0.0, varias_tareas=0.0, ninguna=0.0):
    return {"probabilities": {"una_tarea": una_tarea, "varias_tareas": varias_tareas,
                              "ninguna": ninguna}}


def _tarea_resp(probabilidades: dict[str, float]):
    return {"probabilities": probabilidades}


def _entrante(cur, ws, quien, chat_id, texto) -> str:
    """Un `inbound_message` persistido, como el que arma `procesar_update`
    antes de rutear -- lo necesita el alta guiada (`_iniciar_alta_guiada`)."""
    cur.execute(
        """insert into inbound_message (workspace_id, chat_id, app_user_id, texto)
           values (%s, %s, %s, %s) returning id""",
        (ws, chat_id, quien.app_user_id, texto))
    return str(cur.fetchone()["id"])


@pytest.fixture
def con_credencial(monkeypatch):
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, openrouter_api_key="sk-test-fake"))


def _con_jev(monkeypatch, doble):
    monkeypatch.setattr(jev_modulo, "desde_base", lambda api_key: doble)


def _con_proveedor(monkeypatch, *, rutas, guion=None):
    proveedor = ProveedorGuionado(guion=list(guion or [Respuesta(texto="Anotado.")]),
                                  rutas=list(rutas))
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


@pytest.fixture
def cliente(conn, monkeypatch):
    """Como en `test_botones.py`: sin esto, cada toque de verdad intenta
    hablar con `api.telegram.org` con un token de mentira."""
    monkeypatch.setattr(gateway, "acusar_toque", lambda *a, **k: None)
    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t",
                           openrouter_api_key="sk-test-fake"))
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


def _aclaracion_esperando(cur, ws) -> str:
    cur.execute(
        """select id from pending_action
            where workspace_id = %s and herramienta = %s and estado = 'esperando'
            order by creado_en desc limit 1""",
        (ws, gateway._SENTINEL_ACLARACION))
    return str(cur.fetchone()["id"])


# ---------------------------------------------------------------------------
# quien_escribe llega a Jev desde el turno (decisión 1, §5.10)
# ---------------------------------------------------------------------------

def test_turno_pasa_quien_escribe_a_jev(corework, conn, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero máq. 3")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea_resp({"T1": 0.9})},
        {"misma": {"noul": 0.8}},
    ])
    _con_jev(monkeypatch, doble)
    _con_proveedor(monkeypatch, rutas=[IntentRoute(
        IntentAction.NORMAL_CONVERSATION, trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿cómo va lo del tablero?", ws, chat_id=1)

    assert doble.pedidos[0][0]["quien_escribe"] == "Marcos Tarquini"
    assert doble.pedidos[1][0]["quien_escribe"] == "Marcos Tarquini"


# ---------------------------------------------------------------------------
# Botones: orden (propia primero) y etiqueta (ajena con nombre, truncado)
# ---------------------------------------------------------------------------

def test_botones_propia_primero_ajena_con_nombre_y_titulo_truncado(
        corework, conn, monkeypatch, con_credencial):
    ws = corework.workspace_id
    titulo_largo = "Actualizar toda la documentación técnica del área completa"
    assert len(titulo_largo) > gateway.TRUNCAR_TITULO_BOTON
    with admin(conn) as cur:
        propia = _tarea(cur, ws, titulo="Programar PLC", persona="Marcos Tarquini")
        ajena = _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Mariano Naim")
        larga = _tarea(cur, ws, titulo=titulo_largo, persona="Mariano Naim")
    conn.commit()

    # Jev las devuelve en un orden que NO es "propia primero": el resolutor
    # tiene que reordenar, no confiar en el orden de Jev para eso.
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea_resp({"T2": 0.5, "T1": 0.3, "T3": 0.15})},
    ])
    _con_jev(monkeypatch, doble)
    _con_proveedor(monkeypatch, rutas=[IntentRoute(
        IntentAction.NORMAL_CONVERSATION, trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "avisame de lo del tablero", ws, chat_id=2)
        pid = _aclaracion_esperando(cur, ws)
        filas = _opciones(cur, pid)

    etiquetas = [f["etiqueta"] for f in filas]
    valores = [f["valor"] for f in filas]

    corto = titulo_largo[:gateway.TRUNCAR_TITULO_BOTON - 1] + "…"
    assert etiquetas == ["Programar PLC", "Cablear tablero máq. 3 — Mariano",
                        f"{corto} — Mariano", "Ninguna, lo escribo"]
    assert valores[0] == propia
    assert valores[1] == ajena
    assert valores[2] == larga


# ---------------------------------------------------------------------------
# Elegir una candidata retoma el mensaje: preview, cero efecto antes de Confirmar
# ---------------------------------------------------------------------------

def test_elegir_candidata_retoma_y_llega_a_la_vista_previa_sin_aplicar_nada(
        cliente, conn, corework, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid_a = _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
        tid_b = _tarea(cur, ws, titulo="Revisar tablero máq. 4", persona="Marcos Tarquini")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea_resp({"T1": 0.5, "T2": 0.3})},
    ])
    _con_jev(monkeypatch, doble)
    guion_respuesta = [Respuesta(llamadas=[Llamada(
        "c1", "actualizar_estado", {"tarea_id": "PLACEHOLDER", "estado": "en_revision"})])]
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=("lo del tablero",))],
        guion=guion_respuesta)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "ya termine lo del tablero, pasala a revision", ws,
                       chat_id=3)
        pid = _aclaracion_esperando(cur, ws)
        filas = _opciones(cur, pid)
        primera = filas[0]                     # "Cablear tablero máq. 3" (T1, 0.5)
        assert primera["etiqueta"] == "Cablear tablero máq. 3"
        token = primera["token"]
        tg = _telegram_id(cur, "Marcos Tarquini")

    # El guion de la herramienta usa el id real, resuelto recién ahora.
    proveedor.guion[0].llamadas[0].args["tarea_id"] = tid_a

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid,))
        assert cur.fetchone()["estado"] == "resuelta"
        cur.execute("select estado from task where id = %s", (tid_a,))
        assert cur.fetchone()["estado"] == "asignada"      # sin tocar: sólo hay preview
        cur.execute(
            """select resumen from pending_action
                where herramienta = 'actualizar_estado' and estado = 'esperando'""")
        filas = cur.fetchall()
        assert len(filas) == 1, "la vista previa de la herramienta, esperando Confirmar"

    sistema, _ = proveedor.recibidos[-1]
    assert f"«lo del tablero» es la tarea «Cablear tablero máq. 3» ({tid_a})" in sistema
    assert "Usá esa tarea" in sistema


# ---------------------------------------------------------------------------
# Dos referencias ambiguas: una pregunta a la vez
# ---------------------------------------------------------------------------

def test_dos_referencias_ambiguas_preguntan_una_por_vez(
        cliente, conn, corework, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid_tablero = _tarea(cur, ws, titulo="Cablear tablero máq. 3",
                             persona="Marcos Tarquini")
        tid_hmi = _tarea(cur, ws, titulo="Actualizar HMI", persona="Marcos Tarquini")
    conn.commit()

    # Las dos referencias dan la misma forma de respuesta ambigua: el orden
    # de qué hilo consume qué entrada del guion no importa para esta prueba.
    resp = {"alcance": _alcance(una_tarea=0.8),
           "tarea": _tarea_resp({"T1": 0.5, "T2": 0.3})}
    doble = ClienteJevGuionado(guion=[dict(resp), dict(resp)])
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(
            IntentAction.NORMAL_CONVERSATION,
            trabajos=("lo del tablero", "lo del hmi"))],
        guion=[Respuesta(texto="Anotado.")])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "avisame de lo del tablero y lo del hmi", ws, chat_id=4)
        pid1 = _aclaracion_esperando(cur, ws)
        assert "lo del tablero" in P.buscar(cur, pid1).resumen
        opcion1 = _opciones(cur, pid1)[0]
        tg = _telegram_id(cur, "Marcos Tarquini")

    with admin(conn) as cur:
        cur.execute("select count(*) n from pending_action where estado = 'esperando'")
        assert cur.fetchone()["n"] == 1, "sólo una pregunta a la vez"

    assert _tocar(cliente, opcion1["token"], tg).status_code == 200

    with admin(conn) as cur:
        cur.execute(
            """select id, resumen from pending_action
                where herramienta = %s and estado = 'esperando'""",
            (gateway._SENTINEL_ACLARACION,))
        filas = cur.fetchall()
        assert len(filas) == 1, "la segunda pregunta reemplaza a la primera"
        assert "lo del hmi" in filas[0]["resumen"]
        pid2 = str(filas[0]["id"])
        opcion2 = _opciones(cur, pid2)[0]

    assert _tocar(cliente, opcion2["token"], tg).status_code == 200

    with admin(conn) as cur:
        cur.execute("select count(*) n from pending_action where estado = 'esperando'")
        assert cur.fetchone()["n"] == 0, "ya no queda ninguna pregunta pendiente"

    sistema, _ = proveedor.recibidos[-1]
    assert "lo del tablero" in sistema and "lo del hmi" in sistema
    assert sistema.count("Usá esa tarea") == 2


# ---------------------------------------------------------------------------
# "Ninguna, lo escribo"
# ---------------------------------------------------------------------------

def test_ninguna_cierra_sin_efecto_y_marca_para_corregir(
        cliente, conn, corework, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
        _tarea(cur, ws, titulo="Revisar tablero máq. 4", persona="Marcos Tarquini")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea_resp({"T1": 0.5, "T2": 0.3})},
    ])
    _con_jev(monkeypatch, doble)
    _con_proveedor(monkeypatch, rutas=[IntentRoute(
        IntentAction.NORMAL_CONVERSATION, trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "avisame de lo del tablero", ws, chat_id=5)
        pid = _aclaracion_esperando(cur, ws)
        ninguna = next(o for o in _opciones(cur, pid) if o["etiqueta"] == "Ninguna, lo escribo")
        tg = _telegram_id(cur, "Marcos Tarquini")

    assert _tocar(cliente, ninguna["token"], tg).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado, modificar_pedido_en from pending_action where id = %s",
                    (pid,))
        fila = cur.fetchone()
        assert fila["estado"] == "resuelta"
        assert fila["modificar_pedido_en"] is not None
        cur.execute("select count(*) n from task_state_event")   # nada aplicado
        # (sólo los dos "asignada" del alta de las tareas de prueba)
        assert cur.fetchone()["n"] == 2
        cur.execute("select count(*) n from message_outbox where cuerpo like %s",
                    ("%A qué tarea te referís%",))
        assert cur.fetchone()["n"] == 1


def test_ninguna_dentro_de_la_ventana_el_siguiente_mensaje_usa_el_original(
        conn, corework, monkeypatch, con_credencial):
    """Revisión del orquestador sobre T4: el bloque de contexto de este
    camino NO es `_bloque_modificacion` (nadie tocó Modificar, no hay vista
    previa de una herramienta que corregir, y esa herramienta ni siquiera es
    real -- es el centinela interno) -- es un bloque propio que nombra la
    referencia sin resolver y el mensaje original, y pide seguir el pedido
    original con la tarea que la persona aclare."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
        _tarea(cur, ws, titulo="Revisar tablero máq. 4", persona="Marcos Tarquini")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea_resp({"T1": 0.5, "T2": 0.3})},
    ])
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=("lo del tablero",))],
        guion=[Respuesta(texto="listo"), Respuesta(texto="listo")])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "avisame de lo del tablero", ws, chat_id=6)
        pid = _aclaracion_esperando(cur, ws)
        ninguna = next(o for o in _opciones(cur, pid) if o["etiqueta"] == "Ninguna, lo escribo")

        r = P.resolver(cur, ninguna["token"], app_user_id=quien.app_user_id,
                       ahora=datetime.now(timezone.utc))
        assert r.herramienta == gateway._SENTINEL_ACLARACION
        P.marcar_para_corregir(cur, quien, pid, 6, datetime.now(timezone.utc))

        gateway._turno(cur, quien, "es la de máq. 3", ws, chat_id=6)

    # El mensaje de ahora se ruteó como cualquier turno -- antes de esta
    # corrección, `_resumir_aclaracion_ninguna` no llamaba a `route_intent`
    # en absoluto.
    assert proveedor.ruteados[-1] == "es la de máq. 3"

    sistema, _ = proveedor.recibidos[-1]
    assert "no encontró entre las opciones" in sistema
    assert "lo del tablero" in sistema
    assert "avisame de lo del tablero" in sistema
    # No es el bloque real de Modificar (T7 agregó "Confirmar, Modificar y
    # Cancelar" al preámbulo general, así que la palabra sola ya no alcanza
    # para distinguirlo): el marcador propio de `_bloque_modificacion` tiene
    # que estar ausente.
    assert "# Corrección a una propuesta anterior" not in sistema
    assert "apretó Modificar" not in sistema
    assert gateway._SENTINEL_ACLARACION not in sistema
    assert "vista previa" in sistema.lower()


def test_ninguna_el_siguiente_mensaje_puede_traer_su_propia_referencia(
        conn, corework, monkeypatch, con_credencial):
    """Lo que aclara la persona puede nombrar otra tarea con sus propias
    palabras: ese mensaje se rutea y esa referencia nueva se resuelve con
    Jev, mismo camino que cualquier turno (revisión del orquestador -- el
    mismo que ya se usa para una corrección real de Modificar)."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
        _tarea(cur, ws, titulo="Revisar tablero máq. 4", persona="Marcos Tarquini")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea_resp({"T1": 0.5, "T2": 0.3})},
        {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea_resp({"T1": 0.9})},
        {"misma": {"noul": 0.8}},
    ])
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[
            IntentRoute(IntentAction.NORMAL_CONVERSATION, trabajos=("lo del tablero",)),
            IntentRoute(IntentAction.NORMAL_CONVERSATION, trabajos=("la de máq. 3",)),
        ],
        guion=[Respuesta(texto="listo"), Respuesta(texto="listo")])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "avisame de lo del tablero", ws, chat_id=6)
        pid = _aclaracion_esperando(cur, ws)
        ninguna = next(o for o in _opciones(cur, pid) if o["etiqueta"] == "Ninguna, lo escribo")
        P.resolver(cur, ninguna["token"], app_user_id=quien.app_user_id,
                  ahora=datetime.now(timezone.utc))
        P.marcar_para_corregir(cur, quien, pid, 6, datetime.now(timezone.utc))

        gateway._turno(cur, quien, "es la de máq. 3", ws, chat_id=6)

    sistema, _ = proveedor.recibidos[-1]
    assert f"«la de máq. 3» es la tarea «Cablear tablero máq. 3» ({tid})" in sistema
    assert "Usá esa tarea" in sistema


def test_ninguna_pasada_la_ventana_el_siguiente_mensaje_es_un_turno_normal(
        conn, corework, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
        _tarea(cur, ws, titulo="Revisar tablero máq. 4", persona="Marcos Tarquini")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea_resp({"T1": 0.5, "T2": 0.3})},
    ])
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[
            IntentRoute(IntentAction.NORMAL_CONVERSATION, trabajos=("lo del tablero",)),
            IntentRoute(IntentAction.NORMAL_CONVERSATION),
        ],
        guion=[Respuesta(texto="listo"), Respuesta(texto="otra cosa")])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "avisame de lo del tablero", ws, chat_id=7)
        pid = _aclaracion_esperando(cur, ws)
        ninguna = next(o for o in _opciones(cur, pid) if o["etiqueta"] == "Ninguna, lo escribo")
        P.resolver(cur, ninguna["token"], app_user_id=quien.app_user_id,
                  ahora=datetime.now(timezone.utc))
        P.marcar_para_corregir(cur, quien, pid, 7, datetime.now(timezone.utc))
        # Simula que pasó la ventana sin esperar de verdad.
        cur.execute(
            "update pending_action set modificar_pedido_en = modificar_pedido_en - %s "
            "where id = %s", (P.VENTANA_MODIFICACION + timedelta(minutes=1), pid))

        gateway._turno(cur, quien, "otro mensaje, sin relación", ws, chat_id=7)

    assert proveedor.ruteados[-1] == "otro mensaje, sin relación", (
        "pasada la ventana, vuelve a rutear como un turno común")


# ---------------------------------------------------------------------------
# "Es una tarea nueva" (caso mixto de b-0005)
# ---------------------------------------------------------------------------

def test_es_una_tarea_nueva_sigue_al_alta_guiada(
        cliente, conn, corework, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
        _tarea(cur, ws, titulo="Revisar tablero máq. 4", persona="Marcos Tarquini")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea_resp({"T1": 0.5, "T2": 0.3})},
    ])
    _con_jev(monkeypatch, doble)
    _con_proveedor(monkeypatch, rutas=[IntentRoute(
        IntentAction.START_TASK_INTAKE, task={"title": "Instalar tablero nuevo"},
        trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        tg = _telegram_id(cur, "Marcos Tarquini")
        # El `chat_id` del alta guiada tiene que ser el mismo con el que se
        # guardó `inbound_message` (`task_intake_request_source_workspace_
        # chat`, en `db/esquema.sql`) -- y el toque simulado usa el id de
        # Telegram de quien lo aprieta como chat, igual que `_tocar`.
        entrante_id = _entrante(cur, ws, quien, tg, "esto depende de lo del tablero")
        gateway._turno(cur, quien, "esto depende de lo del tablero", ws, chat_id=tg,
                       entrante_id=entrante_id)
        pid = _aclaracion_esperando(cur, ws)
        etiquetas = [o["etiqueta"] for o in _opciones(cur, pid)]
        assert etiquetas[-2:] == ["Es una tarea nueva", "Ninguna, lo escribo"]
        nueva = next(o for o in _opciones(cur, pid) if o["etiqueta"] == "Es una tarea nueva")

    assert _tocar(cliente, nueva["token"], tg).status_code == 200

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from task_intake_request where workspace_id = %s",
            (ws,))
        assert cur.fetchone()["n"] == 1


def test_normal_conversation_no_ofrece_es_una_tarea_nueva(
        corework, conn, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
        _tarea(cur, ws, titulo="Revisar tablero máq. 4", persona="Marcos Tarquini")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea_resp({"T1": 0.5, "T2": 0.3})},
    ])
    _con_jev(monkeypatch, doble)
    _con_proveedor(monkeypatch, rutas=[IntentRoute(
        IntentAction.NORMAL_CONVERSATION, trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "avisame de lo del tablero", ws, chat_id=9)
        pid = _aclaracion_esperando(cur, ws)
        etiquetas = [o["etiqueta"] for o in _opciones(cur, pid)]
        assert etiquetas[-1] == "Ninguna, lo escribo"
        assert "Es una tarea nueva" not in etiquetas


def test_alta_de_tarea_con_referencia_varias_pregunta_en_vez_de_arrancar_sola(
        corework, conn, monkeypatch, con_credencial):
    """T7, punto G -- regresión de C: b-0009 ("lo mio depende de q mar
    termine su parte, dejalo anotado") terminaba abriendo un borrador de
    tarea en silencio, porque una referencia VARIAS nunca entraba en
    `estado["pendientes"]` (T7, punto C la sacó de los botones a propósito
    para el caso de sólo consulta) y el enrutador leyó el mensaje como alta.
    Con el enrutador pidiendo alta y nada CLARA, una VARIAS también tiene que
    frenar el alta silenciosa y preguntar con los botones de T4 -- las
    candidatas que Jev listó (>= 0,1, propias primero) más "Es una tarea
    nueva" y "Ninguna, lo escribo"."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        propia = _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
        ajena = _tarea(cur, ws, titulo="Revisar accesos VPN", persona="Mariano Naim")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(varias_tareas=0.7),
         "tarea": _tarea_resp({"T2": 0.5, "T1": 0.3})},
    ])
    _con_jev(monkeypatch, doble)
    _con_proveedor(monkeypatch, rutas=[IntentRoute(
        IntentAction.START_TASK_INTAKE, task={"title": "Anotar dependencia"},
        trabajos=("lo mio",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(
            cur, quien, "lo mio depende de q mar termine su parte, dejalo anotado",
            ws, chat_id=13)
        pid = _aclaracion_esperando(cur, ws)
        filas = _opciones(cur, pid)

    etiquetas = [f["etiqueta"] for f in filas]
    valores = [f["valor"] for f in filas]
    assert etiquetas[-2:] == ["Es una tarea nueva", "Ninguna, lo escribo"]
    assert etiquetas[0] == "Cablear tablero máq. 3"          # propia primero, sin nombre
    assert valores[0] == propia
    assert "Revisar accesos VPN — Mariano" in etiquetas
    assert valores[1] == ajena

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from task_intake_request where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0, "no arranca el alta en silencio"


# ---------------------------------------------------------------------------
# La corrección después de Modificar también pasa por Jev (revisión de T3)
# ---------------------------------------------------------------------------

def test_correccion_de_modificar_pasa_por_route_intent_y_jev(
        corework, conn, monkeypatch, con_credencial):
    from prisma.agente import responder
    from prisma.calendario import Calendario

    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
    conn.commit()

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        guion_propuesta = [Respuesta(llamadas=[Llamada(
            "c1", "registrar_bloqueo", {"tarea_id": tid, "causa": "falta el switch"})])]
        r = responder(cur, quien, "hacé esto", ProveedorGuionado(guion_propuesta), cal,
                     chat_id=10, ahora=datetime.now(timezone.utc))
        assert r.confirmaciones == ["registrar_bloqueo"]
        cur.execute(
            """select id from pending_action
                where herramienta = 'registrar_bloqueo' and estado = 'esperando'""")
        pid = str(cur.fetchone()["id"])
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")
        P.resolver(cur, modificar.token, app_user_id=quien.app_user_id,
                  ahora=datetime.now(timezone.utc))
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea_resp({"T1": 0.9})},
        {"misma": {"noul": 0.8}},
    ])
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=("lo del tablero",))],
        guion=[Respuesta(llamadas=[Llamada(
            "c2", "registrar_bloqueo",
            {"tarea_id": tid, "causa": "falta el cable, no el switch"})]),
              Respuesta(texto="listo")])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "en realidad es lo del tablero, el cable", ws,
                       chat_id=10)

    assert proveedor.ruteados == ["en realidad es lo del tablero, el cable"], (
        "la corrección se rutea, como cualquier turno (revisión de T3)")
    assert doble.pedidos, "y se resuelve con Jev"
    sistema, _ = proveedor.recibidos[-1]
    assert "Corrección a una propuesta anterior" in sistema
    assert f"«lo del tablero» es la tarea «Cablear tablero máq. 3» ({tid})" in sistema


# ---------------------------------------------------------------------------
# Garantías existentes reusadas: otro integrante, vencida, doble toque
# ---------------------------------------------------------------------------

def test_toque_de_otro_integrante_no_resuelve_la_aclaracion(
        cliente, conn, corework, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
        _tarea(cur, ws, titulo="Revisar tablero máq. 4", persona="Marcos Tarquini")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea_resp({"T1": 0.5, "T2": 0.3})},
    ])
    _con_jev(monkeypatch, doble)
    _con_proveedor(monkeypatch, rutas=[IntentRoute(
        IntentAction.NORMAL_CONVERSATION, trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "avisame de lo del tablero", ws, chat_id=11)
        pid = _aclaracion_esperando(cur, ws)
        token = _opciones(cur, pid)[0]["token"]
        ajeno = _telegram_id(cur, "Ariel De Simone")

    assert _tocar(cliente, token, ajeno).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid,))
        assert cur.fetchone()["estado"] == "esperando"


def test_toque_vencido_no_aplica(cliente, conn, corework, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
        _tarea(cur, ws, titulo="Revisar tablero máq. 4", persona="Marcos Tarquini")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea_resp({"T1": 0.5, "T2": 0.3})},
    ])
    _con_jev(monkeypatch, doble)
    _con_proveedor(monkeypatch, rutas=[IntentRoute(
        IntentAction.NORMAL_CONVERSATION, trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "avisame de lo del tablero", ws, chat_id=12)
        pid = _aclaracion_esperando(cur, ws)
        token = _opciones(cur, pid)[0]["token"]
        tg = _telegram_id(cur, "Marcos Tarquini")
        cur.execute(
            "update pending_action set vence_en = now() - interval '1 hour' where id = %s",
            (pid,))
    conn.commit()

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid,))
        assert cur.fetchone()["estado"] == "vencida"


def test_toque_repetido_no_aplica_dos_veces(
        cliente, conn, corework, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
        _tarea(cur, ws, titulo="Revisar tablero máq. 4", persona="Marcos Tarquini")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea_resp({"T1": 0.5, "T2": 0.3})},
    ])
    _con_jev(monkeypatch, doble)
    _con_proveedor(monkeypatch, rutas=[IntentRoute(
        IntentAction.NORMAL_CONVERSATION, trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "avisame de lo del tablero", ws, chat_id=13)
        pid = _aclaracion_esperando(cur, ws)
        ninguna = next(o for o in _opciones(cur, pid) if o["etiqueta"] == "Ninguna, lo escribo")
        tg = _telegram_id(cur, "Marcos Tarquini")

    assert _tocar(cliente, ninguna["token"], tg).status_code == 200
    assert _tocar(cliente, ninguna["token"], tg).status_code == 200   # de nuevo, no rompe

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from audit_log where accion = 'aclaracion_referencia'")
        assert cur.fetchone()["n"] == 1, "el segundo toque no vuelve a auditar nada"


# ---------------------------------------------------------------------------
# Auditoría de la elección, sin mensaje ni texto de la referencia
# ---------------------------------------------------------------------------

def test_auditoria_de_la_eleccion_sin_mensaje_ni_referencia(
        cliente, conn, corework, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
        _tarea(cur, ws, titulo="Revisar tablero máq. 4", persona="Marcos Tarquini")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea_resp({"T1": 0.5, "T2": 0.3})},
    ])
    _con_jev(monkeypatch, doble)
    _con_proveedor(monkeypatch, rutas=[IntentRoute(
        IntentAction.NORMAL_CONVERSATION, trabajos=("secreto: lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "secreto: pasame lo del tablero, urgente", ws,
                       chat_id=14)
        pid = _aclaracion_esperando(cur, ws)
        primera = _opciones(cur, pid)[0]
        tg = _telegram_id(cur, "Marcos Tarquini")

    assert _tocar(cliente, primera["token"], tg).status_code == 200

    with admin(conn) as cur:
        cur.execute(
            "select detalle from audit_log where accion = 'aclaracion_referencia'")
        fila = cur.fetchone()
        assert fila["detalle"] == {"tipo": "candidata", "tarea_id": tid}
        crudo = str(fila["detalle"])
        assert "secreto" not in crudo
        assert "tablero" not in crudo.lower()
