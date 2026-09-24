"""Resolución de referencias a tarea antes de actuar (T3, `aclaracion-con-
botones`; ADR 0005 decisión 6, ADR 0006).

`gateway._turno` resuelve las referencias que separó `route_intent` contra
las tareas activas del espacio, con Jev, antes de decidir si arranca el alta
guiada o pasa a `agente.responder`. Sin credencial, sigue exactamente como
antes de esta unidad -- por eso casi todas las pruebas necesitan un cliente
de Jev guionado y una credencial falsa inyectados por `monkeypatch`, nunca
red ni credencial real.
"""

from __future__ import annotations

import dataclasses

import pytest

from prisma import gateway
from prisma import jev as jev_modulo
from prisma.autoridad import Canal, identificar
from prisma.db import admin, espacio
from prisma.jev import ClienteJevGuionado
from prisma.llm import (IntentAction, IntentRoute, ProveedorGuionado,
                        Respuesta)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


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


@pytest.fixture
def con_credencial(monkeypatch):
    """Fuerza una credencial falsa de Jev, sin tocar el entorno real."""
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


# ---------------------------------------------------------------------------
# Sin credencial: Prisma no adivina (decisión del usuario, 2026-09-24)
# ---------------------------------------------------------------------------

def test_sin_credencial_pregunta_y_registra_incidente(corework, conn, monkeypatch):
    """Sin `PRISMA_OPENROUTER_API_KEY`, un mensaje con referencias se trata
    igual que si Jev hubiera fallado en cada una: se le pide al modelo que
    pregunte, nunca que elija solo, y queda un incidente sin secretos ni
    texto del mensaje para que la falta de configuración no pase
    inadvertida."""
    ws = corework.workspace_id
    monkeypatch.setattr(
        gateway, "config", dataclasses.replace(gateway.config, openrouter_api_key=""))
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=("el tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿cómo va lo del tablero?", ws, chat_id=1)

    sistema, _ = proveedor.recibidos[-1]
    assert "No se pudo resolver" in sistema
    assert "Usá esa tarea" not in sistema

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from incident where resumen_sanitizado like "
            "'%credencial de Jev%'")
        assert cur.fetchone()["n"] == 1
        cur.execute("select resumen_sanitizado from incident limit 1")
        assert "tablero" not in cur.fetchone()["resumen_sanitizado"].lower()

        cur.execute(
            "select detalle from audit_log where accion = 'resolucion_referencias'")
        detalle = cur.fetchone()["detalle"]
        assert detalle == {"referencias": [
            {"tipo": "jev_error", "tarea_id": None, "candidatas": []}]}


def test_sin_credencial_ni_referencias_no_cambia_nada(corework, conn, monkeypatch):
    """Sin referencias en el mensaje, la falta de credencial no importa: el
    turno sigue exactamente como antes de esta unidad."""
    ws = corework.workspace_id
    monkeypatch.setattr(
        gateway, "config", dataclasses.replace(gateway.config, openrouter_api_key=""))
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿qué tengo?", ws, chat_id=1)

    sistema, _ = proveedor.recibidos[-1]
    assert "Referencias a tareas" not in sistema
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident")
        assert cur.fetchone()["n"] == 0
        cur.execute(
            "select count(*) n from audit_log where accion = 'resolucion_referencias'")
        assert cur.fetchone()["n"] == 0


# ---------------------------------------------------------------------------
# Clara
# ---------------------------------------------------------------------------

def test_referencia_clara_llega_como_contexto_al_modelo(
        corework, conn, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea_id = _tarea(cur, ws, titulo="Cablear tablero máq. 3")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea_resp({"T1": 0.9})},
        {"misma": {"noul": 0.8}},
    ])
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿cómo va lo del tablero?", ws, chat_id=2)

    sistema, _ = proveedor.recibidos[-1]
    assert f"«lo del tablero» es la tarea «Cablear tablero máq. 3» ({tarea_id})" in sistema
    assert "Usá esa tarea" in sistema


# ---------------------------------------------------------------------------
# Ambigua
# ---------------------------------------------------------------------------

def test_referencia_ambigua_pregunta_sin_actuar(
        corework, conn, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero máq. 3")
        _tarea(cur, ws, titulo="Revisar tablero máq. 4")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(varias_tareas=0.7),
         "tarea": _tarea_resp({"T1": 0.5, "T2": 0.3})},
    ])
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        resultado = gateway._turno(cur, quien, "avisame de lo del tablero", ws, chat_id=3)

    sistema, _ = proveedor.recibidos[-1]
    assert "puede ser más de una tarea" in sistema
    assert "Cablear tablero máq. 3" in sistema
    assert "Revisar tablero máq. 4" in sistema
    assert "sin elegir" in sistema or "sin actuar" in sistema
    assert "Usá esa tarea" not in sistema
    assert resultado is None            # `_turno` no devuelve nada; nada se ejecutó


# ---------------------------------------------------------------------------
# Ninguna
# ---------------------------------------------------------------------------

def test_referencia_sin_coincidencia_no_inventa(corework, conn, monkeypatch, con_credencial):
    ws = corework.workspace_id
    # Sin tareas sembradas: `resolver_referencia_tarea` da NINGUNA sin tocar
    # la red -- ni siquiera hace falta encolar una respuesta guionada.
    doble = ClienteJevGuionado(guion=[])
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=("el horno",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿qué onda el horno?", ws, chat_id=4)

    sistema, _ = proveedor.recibidos[-1]
    assert "no coincide con ninguna tarea activa" in sistema
    assert not doble.pedidos                       # nunca llamó a Jev


# ---------------------------------------------------------------------------
# Jev caído / respuesta malformada
# ---------------------------------------------------------------------------

def test_jev_caido_pide_la_referencia(corework, conn, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws)
    conn.commit()

    doble = ClienteJevGuionado(guion=[])          # se agota en la primera llamada
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿cómo va lo del tablero?", ws, chat_id=5)

    sistema, _ = proveedor.recibidos[-1]
    assert "No se pudo resolver" in sistema
    assert "preguntale" in sistema.lower() or "pedile" in sistema.lower()

    # El turno sigue funcionando: la respuesta del modelo guionado salió.
    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox")
        assert cur.fetchone()["n"] == 1


# ---------------------------------------------------------------------------
# b-0005: una referencia clara a una tarea existente no arranca el alta
# ---------------------------------------------------------------------------

def test_b0005_referencia_clara_evita_alta_guiada(
        corework, conn, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea_id = _tarea(cur, ws, titulo="Cablear tablero máq. 3")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea_resp({"T1": 0.9})},
        {"misma": {"noul": 0.8}},
    ])
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch,
        rutas=[IntentRoute(IntentAction.START_TASK_INTAKE,
                           trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "esto depende de lo del tablero", ws,
                       chat_id=6, entrante_id=None)

    # No arrancó el alta guiada de tarea nueva.
    with admin(conn) as cur:
        cur.execute("select count(*) n from task_intake_request")
        assert cur.fetchone()["n"] == 0

    # Fue al agente, con la tarea resuelta como contexto.
    assert proveedor.recibidos, "tiene que haber pasado por agente.responder"
    sistema, _ = proveedor.recibidos[-1]
    assert f"({tarea_id})" in sistema
    assert "Usá esa tarea" in sistema


# ---------------------------------------------------------------------------
# RLS: sólo viajan las tareas del espacio actual
# ---------------------------------------------------------------------------

def test_solo_viajan_tareas_del_espacio_actual(intake_world, conn, monkeypatch):
    a = intake_world["north-lab"]
    b = intake_world["west-studio"]

    def _tarea_en(cur, ws, objetivo, area, membership, titulo):
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, criterio_aceptacion,
                                 evidencia_requerida)
               values (%s, %s, %s, %s, %s, 'Criterio de prueba', array['explicacion'])
               returning id""",
            (ws, objetivo, titulo, area, membership))
        tid = cur.fetchone()["id"]
        cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                    "values (%s, 'asignada', 'prisma')", (tid,))
        return str(tid)

    with admin(conn) as cur:
        cur.execute("set role prisma_admin")
        _tarea_en(cur, a["id"], a["objectives"][0], a["areas"]["field"],
                 a["people"]["Sam North"]["membership_id"], "Reparar bomba del norte")
        _tarea_en(cur, b["id"], b["objectives"][0], b["areas"]["field"],
                 b["people"]["Sam North"]["membership_id"], "Reparar bomba del oeste")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(ninguna=0.9), "tarea": _tarea_resp({"T1": 0.05})},
    ])
    monkeypatch.setattr(jev_modulo, "desde_base", lambda api_key: doble)
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, openrouter_api_key="sk-test-fake"))
    proveedor = ProveedorGuionado(
        guion=[Respuesta(texto="ok")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION, trabajos=("la bomba",))])
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)

    with espacio(conn, a["id"]) as cur:
        quien = identificar(cur, a["people"]["Morgan Hale"]["telegram"],
                            Canal.ESPACIO, a["id"])
        gateway._turno(cur, quien, "avisame de la bomba", a["id"], chat_id=7)

    criterios = doble.pedidos[0][1]["tarea"]["criteria"]
    valores = " ".join(criterios.values())
    assert "Reparar bomba del norte" in valores
    assert "Reparar bomba del oeste" not in valores
    assert len(criterios) == 1


# ---------------------------------------------------------------------------
# Auditoría sin cuerpo de mensaje
# ---------------------------------------------------------------------------

def test_auditoria_no_guarda_el_texto_del_mensaje_ni_de_la_referencia(
        corework, conn, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea_id = _tarea(cur, ws, titulo="Cablear tablero máq. 3")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea_resp({"T1": 0.9})},
        {"misma": {"noul": 0.8}},
    ])
    _con_jev(monkeypatch, doble)
    _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=("lo del tablero, urgente",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien,
                       "secreto: lo del tablero, urgente, avisale a fulano", ws, chat_id=8)

    with admin(conn) as cur:
        cur.execute(
            "select detalle from audit_log where accion = 'resolucion_referencias'")
        filas = cur.fetchall()

    assert len(filas) == 1
    detalle = filas[0]["detalle"]
    crudo = str(detalle)
    assert "lo del tablero" not in crudo
    assert "secreto" not in crudo
    assert detalle == {"referencias": [
        {"tipo": "clara", "tarea_id": tarea_id, "candidatas": []}]}
