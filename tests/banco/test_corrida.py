"""Pruebas de la corrida y grabación del banco: el proveedor grabador (sin
base, con un `ProveedorGuionado` interno) y `ejecutar_escenario` sobre el
circuito real (`gateway.procesar_update`), con la base descartable de las
pruebas. TDD estricto.
"""

from __future__ import annotations

import pytest

from prisma.autoridad import Canal, identificar
from prisma.db import admin
from prisma.llm import IntentAction, IntentRoute, Llamada, ProveedorGuionado, Respuesta

from tests.banco.corrida import (
    ProveedorGrabador,
    conteos_delta,
    ejecutar_escenario,
    guionado_desde_grabacion,
    recolectar_efectos,
    sembrar_precondiciones,
)

# ---------------------------------------------------------------------------
# ProveedorGrabador: grabación y round-trip a JSON / ProveedorGuionado
# ---------------------------------------------------------------------------


def test_grabador_registra_ruta_y_respuesta_con_latencia():
    interno = ProveedorGuionado(
        guion=[Respuesta(texto="Tenés dos tareas.")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )
    g = ProveedorGrabador(interno)
    ruta = g.route_intent("¿qué tengo?")
    r = g.responder("sistema", [{"role": "user", "content": "hola"}], [])

    assert ruta.action is IntentAction.NORMAL_CONVERSATION
    assert r.texto == "Tenés dos tareas."
    assert len(g.rutas) == 1 and g.rutas[0]["latencia_s"] >= 0
    assert len(g.respuestas) == 1 and g.respuestas[0]["latencia_s"] >= 0


def test_grabacion_json_es_serializable_y_recargable():
    interno = ProveedorGuionado(
        guion=[Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
              Respuesta(texto="Tenés dos tareas.")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )
    g = ProveedorGrabador(interno)
    g.route_intent("¿qué tengo?")
    g.responder("sistema", [], [])
    g.responder("sistema", [], [])

    import json
    grabacion = json.loads(json.dumps(g.a_json()))

    guionado = guionado_desde_grabacion(grabacion)
    assert isinstance(guionado, ProveedorGuionado)
    ruta = guionado.route_intent("cualquier cosa")
    assert ruta.action is IntentAction.NORMAL_CONVERSATION
    r1 = guionado.responder("s", [], [])
    assert r1.llamadas[0].nombre == "consultar_tareas"
    r2 = guionado.responder("s", [], [])
    assert r2.texto == "Tenés dos tareas."


# ---------------------------------------------------------------------------
# sembrar_precondiciones
# ---------------------------------------------------------------------------


def test_sembrar_precondiciones_crea_tarea_bloqueo_y_dependencia(corework, conn):
    ws = corework.workspace_id
    precondiciones = {
        "tareas": [
            {"id": "t1", "titulo": "Programar PLC (simulado)", "area": "ot",
             "responsable": "Marcos Tarquini"},
            {"id": "t2", "titulo": "Cablear tablero (simulado)", "area": "ot",
             "responsable": "Nahuel Gimenez"},
        ],
        "bloqueos": [{"tarea": "t1", "causa": "falta un repuesto (simulado)"}],
        "dependencias": [{"origen": "t1", "destino": "t2", "tipo": "bloqueante"}],
    }
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, precondiciones)
        cur.execute("select estado from task where id = %s", (ids["t1"],))
        assert cur.fetchone()["estado"] == "bloqueada"
        cur.execute("select count(*) n from blocker where task_id = %s", (ids["t1"],))
        assert cur.fetchone()["n"] == 1
        cur.execute(
            "select count(*) n from dependency where origen_task_id = %s", (ids["t1"],))
        assert cur.fetchone()["n"] == 1


# ---------------------------------------------------------------------------
# ejecutar_escenario: circuito real vía gateway.procesar_update
# ---------------------------------------------------------------------------


def test_ejecutar_escenario_conversacion_normal_recolecta_evidencia(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {
            "tareas": [{"id": "t1", "titulo": "Programar PLC (simulado)",
                       "area": "ot", "responsable": "Marcos Tarquini"}],
        })

    interno = ProveedorGuionado(
        guion=[
            Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
            Respuesta(texto="Tenés una tarea pendiente: Programar PLC."),
        ],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini",
        ["che, ¿qué tengo pendiente?"], interno,
        escenario_id="b-test", indice=0)

    assert r.bloqueado is False
    assert r.herramientas_ejecutadas == ["consultar_tareas"]
    assert "Programar PLC" in r.respuesta_texto
    assert r.conteos_antes["task"] == 1
    assert r.conteos_despues["task"] == 1
    assert r.conteos_despues["message_outbox"] == r.conteos_antes["message_outbox"] + 1
    assert r.latencia_total_s >= 0
    assert r.grabacion["rutas"] and r.grabacion["respuestas"]


def test_ejecutar_escenario_guarda_latencia_por_llamada_en_la_grabacion(corework, conn):
    ws = corework.workspace_id
    interno = ProveedorGuionado(
        guion=[Respuesta(texto="Anotado.")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )
    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["hola"], interno,
        escenario_id="b-test", indice=0)

    assert r.grabacion["rutas"][0]["latencia_s"] >= 0
    assert r.grabacion["respuestas"][0]["latencia_s"] >= 0


def test_ejecutar_escenario_slug_inexistente_queda_bloqueado(corework, conn):
    """`procesar_update` resuelve el espacio por el slug, no por el
    `workspace_id` que arma la evidencia: un slug que no existe hace que el
    webhook levante `HTTPException(404)`, y eso es justo lo que
    `ejecutar_escenario` tiene que capturar como corrida bloqueada, no dejar
    caer sin evidencia."""
    ws = corework.workspace_id
    interno = ProveedorGuionado(guion=[Respuesta(texto="no debería usarse")])
    r = ejecutar_escenario(
        conn, ws, "espacio-que-no-existe", "Marcos Tarquini", ["hola"], interno,
        escenario_id="b-test", indice=0)
    assert r.bloqueado is True
    assert r.motivo_bloqueo


def test_ejecutar_escenario_actor_desconocido_levanta_lookup_error(corework, conn):
    ws = corework.workspace_id
    interno = ProveedorGuionado(guion=[])
    with pytest.raises(LookupError):
        ejecutar_escenario(
            conn, ws, "corework", "Persona Que No Existe", ["hola"], interno,
            escenario_id="b-test", indice=0)


# ---------------------------------------------------------------------------
# recolectar_efectos / conteos_delta (defecto de revisión: el objetivo del
# escenario -- estado, bloqueo o dependencia correctos -- nunca se
# verificaba contra la base)
# ---------------------------------------------------------------------------


def test_recolectar_efectos_estado_y_bloqueos_abiertos_por_id_de_semilla(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {
            "tareas": [{"id": "t1", "titulo": "Programar PLC (simulado)",
                       "area": "ot", "responsable": "Marcos Tarquini"}],
            "bloqueos": [{"tarea": "t1", "causa": "falta un repuesto (simulado)"}],
        })
        efectos = recolectar_efectos(cur, ids)
    assert efectos["tareas"]["t1"]["estado"] == "bloqueada"
    assert efectos["bloqueos_abiertos"]["t1"] == 1


def test_recolectar_efectos_bloqueos_abiertos_baja_al_resolver(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {
            "tareas": [{"id": "t1", "titulo": "Programar PLC (simulado)",
                       "area": "ot", "responsable": "Marcos Tarquini"}],
            "bloqueos": [{"tarea": "t1", "causa": "falta un repuesto (simulado)"}],
        })
    from prisma import herramientas as H
    from prisma.db import espacio
    with espacio(conn, ws) as cur:
        cur.execute("select bloqueo_id from (select id as bloqueo_id from blocker "
                    "where task_id = %s) x", (ids["t1"],))
        bloqueo_id = str(cur.fetchone()["bloqueo_id"])
        cur.execute("select telegram_user_id t from integrante where nombre = %s",
                    ("Marcos Tarquini",))
        tg = cur.fetchone()["t"]
        quien = identificar(cur, tg, Canal.ESPACIO, ws)
        H.ejecutar(cur, quien, "resolver_bloqueo",
                  {"bloqueo_id": bloqueo_id, "resolucion": "listo (simulado)"})
    with admin(conn) as cur:
        efectos = recolectar_efectos(cur, ids)
    assert efectos["bloqueos_abiertos"]["t1"] == 0
    assert efectos["tareas"]["t1"]["estado"] == "asignada"


def test_recolectar_efectos_dependencias_en_ids_de_semilla(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {
            "tareas": [
                {"id": "t1", "titulo": "Programar PLC (simulado)", "area": "ot",
                 "responsable": "Nahuel Gimenez"},
                {"id": "t2", "titulo": "Cablear tablero (simulado)", "area": "ot",
                 "responsable": "Marcos Tarquini"},
            ],
            "dependencias": [{"origen": "t1", "destino": "t2", "tipo": "bloqueante"}],
        })
        efectos = recolectar_efectos(cur, ids)
    assert efectos["dependencias"] == [{"origen": "t1", "destino": "t2", "tipo": "bloqueante"}]


def test_conteos_delta_resta_antes_de_despues():
    antes = {"task": 1, "blocker": 0}
    despues = {"task": 1, "blocker": 1}
    assert conteos_delta(antes, despues) == {"task": 0, "blocker": 1}
