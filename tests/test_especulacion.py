"""Ruteo en paralelo con la primera llamada del responder (T8c-3, ADR 0012).

En el caso simple -- sin corrección abierta, ruteo a conversación normal y sin
referencias a tareas -- la primera llamada del responder arranca en otro hilo
mientras corre el ruteo. Cualquier otro camino descarta esa llamada sin usar
su resultado. Un proveedor sólo la admite si lo declara
(`admite_especulacion`).
"""

from __future__ import annotations

import dataclasses
import threading

from prisma import agente
from prisma import gateway
from prisma import jev as jev_modulo
from prisma import pendientes as P
from prisma.autoridad import Canal, identificar
from prisma.db import admin, espacio
from prisma.jev import ClienteJevGuionado
from prisma.llm import (IntentAction, IntentRoute, ProveedorGuionado,
                        Respuesta)

from tests.banco.corrida import ProveedorGrabador, guionado_desde_grabacion


class ProveedorEspecula(ProveedorGuionado):
    """Guionado que registra el hilo de cada llamada y puede frenar el ruteo
    hasta que el responder haya arrancado."""

    def __init__(self, *args, esperar_responder: bool = False,
                 falla_responder: Exception | None = None, **kw) -> None:
        super().__init__(*args, **kw)
        self.admite_especulacion = True
        self.hilos_responder: list[threading.Thread] = []
        self.arranco_responder = threading.Event()
        self.esperar_responder = esperar_responder
        self.falla_responder = falla_responder
        self.ruteo_vio_responder: bool | None = None

    def route_intent(self, text):
        if self.esperar_responder:
            self.ruteo_vio_responder = self.arranco_responder.wait(timeout=5)
        return super().route_intent(text)

    def responder(self, sistema, mensajes, herramientas):
        self.hilos_responder.append(threading.current_thread())
        self.arranco_responder.set()
        if self.falla_responder is not None:
            raise self.falla_responder
        return super().responder(sistema, mensajes, herramientas)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _tarea(cur, ws, titulo="Cablear tablero máq. 3"):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Objetivo de prueba') returning id""", (ws,))
    obj = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, criterio_aceptacion,
                             evidencia_requerida)
           values (%s, %s, %s,
                   (select id from area where workspace_id = %s and slug = 'electricidad'),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = 'Mariano Naim'),
                    'Criterio de prueba', array['explicacion'])
           returning id""", (ws, obj, titulo, ws, ws))
    t = cur.fetchone()["id"]
    cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                "values (%s, 'asignada', 'prisma')", (t,))
    return str(t)


def _con(monkeypatch, proveedor):
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


def _turno(conn, corework, texto="hola", chat_id=1, con_entrante=False):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        entrante = None
        if con_entrante:
            cur.execute(
                """insert into inbound_message (workspace_id, chat_id, app_user_id, texto)
                   values (%s, %s, %s, %s) returning id""",
                (ws, chat_id, quien.app_user_id, texto))
            entrante = str(cur.fetchone()["id"])
        gateway._turno(cur, quien, texto, ws, chat_id=chat_id, entrante_id=entrante)


def _mensajes_salientes(conn, ws):
    with admin(conn) as cur:
        cur.execute("select cuerpo from message_outbox where workspace_id = %s", (ws,))
        return [f["cuerpo"] for f in cur.fetchall()]


def _incidentes(conn) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident")
        return cur.fetchone()["n"]


def test_la_primera_llamada_arranca_antes_de_que_termine_el_ruteo(
        corework, conn, monkeypatch):
    p = _con(monkeypatch, ProveedorEspecula(
        guion=[Respuesta(texto="Hola.")], esperar_responder=True))
    _turno(conn, corework)
    # Secuencial: el ruteo esperaría 5 s a un responder que nunca arranca.
    assert p.ruteo_vio_responder is True
    assert len(p.recibidos) == 1
    assert p.hilos_responder[0] is not threading.main_thread()
    assert any("Hola." in t for t in _mensajes_salientes(conn, corework.workspace_id))


def test_el_hilo_trabajador_recibe_solo_datos_preparados(corework, conn, monkeypatch):
    p = _con(monkeypatch, ProveedorEspecula(guion=[Respuesta(texto="Hola.")]))
    _turno(conn, corework, "¿qué tal?")
    sistema, mensajes = p.recibidos[0]
    assert isinstance(sistema, str) and isinstance(mensajes, list)
    assert mensajes[-1] == {"role": "user", "content": "¿qué tal?"}


def test_sin_la_bandera_no_hay_especulacion(corework, conn, monkeypatch):
    p = _con(monkeypatch, ProveedorEspecula(guion=[Respuesta(texto="Hola.")]))
    p.admite_especulacion = False
    _turno(conn, corework)
    assert p.hilos_responder == [threading.main_thread()]


def test_el_guionado_por_defecto_no_admite_especulacion():
    assert ProveedorGuionado(guion=[]).admite_especulacion is False


def test_los_proveedores_reales_admiten_especulacion():
    from prisma.llm import (ProveedorAnthropic, ProveedorCompatible,
                            ProveedorGemini)
    for clase in (ProveedorAnthropic, ProveedorCompatible, ProveedorGemini):
        assert clase.admite_especulacion is True


def test_ruteo_a_alta_guiada_descarta_la_especulacion(corework, conn, monkeypatch):
    p = _con(monkeypatch, ProveedorEspecula(
        guion=[Respuesta(texto="No debería salir.")], esperar_responder=True,
        rutas=[IntentRoute(IntentAction.START_TASK_INTAKE,
                           {"objective": "service delay"})]))
    _turno(conn, corework, "creá una tarea: revisar la bomba", con_entrante=True)
    ws = corework.workspace_id
    assert p.ruteo_vio_responder is True
    assert "No debería salir." not in _mensajes_salientes(conn, ws)
    with admin(conn) as cur:
        cur.execute("select count(*) n from task_intake_choice_set")
        assert cur.fetchone()["n"] >= 1  # arrancó el alta guiada, como siempre


def test_con_referencias_se_descarta_y_el_responder_recibe_el_bloque(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, openrouter_api_key="sk-test-fake"))
    with admin(conn) as cur:
        tarea = _tarea(cur, ws)
    conn.commit()
    monkeypatch.setattr(jev_modulo, "desde_base", lambda api_key: ClienteJevGuionado(
        guion=[{"alcance": {"probabilities": {"una_tarea": 0.95, "varias_tareas": 0.0,
                                               "ninguna": 0.0}},
                "tarea": {"probabilities": {"T1": 0.9}}},
               {"misma": {"noul": 0.8}}]))
    p = _con(monkeypatch, ProveedorEspecula(
        guion=[Respuesta(texto="especulativa"), Respuesta(texto="Con el bloque.")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                           trabajos=("lo del tablero",))]))
    _turno(conn, corework, "¿cómo va lo del tablero?")

    assert len(p.recibidos) == 2
    sistema_especulativo, _ = p.recibidos[0]
    sistema_real, _ = p.recibidos[1]
    assert "Referencias a tareas" not in sistema_especulativo
    assert "Referencias a tareas" in sistema_real
    salientes = _mensajes_salientes(conn, ws)
    assert not any("especulativa" in t for t in salientes)
    assert any("Con el bloque." in t for t in salientes)


def test_si_la_llamada_especulativa_falla_es_el_mismo_camino_de_incidente(
        corework, conn, monkeypatch):
    _con(monkeypatch, ProveedorEspecula(
        guion=[], falla_responder=RuntimeError("boom")))
    antes = _incidentes(conn)
    _turno(conn, corework)
    assert _incidentes(conn) == antes + 1
    assert agente.DISCULPA in _mensajes_salientes(conn, corework.workspace_id)


def test_si_falla_el_ruteo_se_descarta_y_sale_el_camino_de_siempre(
        corework, conn, monkeypatch):
    p = _con(monkeypatch, ProveedorEspecula(guion=[Respuesta(texto="no")]))

    def rota(texto):
        raise RuntimeError("sin ruteo")
    p.route_intent = rota
    _turno(conn, corework)
    salientes = _mensajes_salientes(conn, corework.workspace_id)
    assert any("No pude entender" in t for t in salientes)
    assert "no" not in salientes


def test_con_una_modificacion_abierta_no_hay_especulacion(
        corework, conn, monkeypatch):
    p = _con(monkeypatch, ProveedorEspecula(guion=[Respuesta(texto="Ok.")]))
    lanzadas = []
    real = agente.especular
    monkeypatch.setattr(agente, "especular",
                        lambda *a, **k: lanzadas.append(1) or real(*a, **k))
    modificacion = P.ModificacionAbierta(
        pending_action_id="", herramienta="crear_tarea",
        args={"titulo": "x"}, resumen="x")
    monkeypatch.setattr(P, "reclamar_modificacion_abierta",
                        lambda *a, **k: modificacion)
    _turno(conn, corework, "mejor para el viernes")
    assert lanzadas == []
    assert p.hilos_responder == [threading.main_thread()]


# ---------------------------------------------------------------------------
# Grabador del banco
# ---------------------------------------------------------------------------

def _grabador(*textos):
    interno = ProveedorGuionado(
        guion=[Respuesta(texto=t) for t in textos], admite_especulacion=True)
    return ProveedorGrabador(interno=interno)


def test_el_grabador_reenvia_la_bandera_del_proveedor_interno():
    assert _grabador("a").admite_especulacion is True
    assert ProveedorGrabador(
        interno=ProveedorGuionado(guion=[])).admite_especulacion is False


def test_el_grabador_quita_la_respuesta_descartada_y_conserva_la_usada_una_vez():
    g = _grabador("descartada", "usada")
    r1 = g.responder("s", [], [])
    r2 = g.responder("s", [], [])
    g.descartar_respuesta(r1)
    g.descartar_respuesta(r1)  # idempotente
    textos = [e["salida"]["texto"] for e in g.a_json()["respuestas"]]
    assert textos == ["usada"]
    assert r2.texto == "usada"


def test_el_replay_de_una_grabacion_con_descarte_no_consume_la_descartada():
    g = _grabador("descartada", "usada")
    r1 = g.responder("s", [], [])
    g.responder("s", [], [])
    g.descartar_respuesta(r1)
    replay = guionado_desde_grabacion(g.a_json())
    assert replay.admite_especulacion is False
    assert replay.responder("s", [], []).texto == "usada"


def test_gateway_avisa_al_grabador_de_la_respuesta_descartada(
        corework, conn, monkeypatch):
    interno = ProveedorEspecula(
        guion=[Respuesta(texto="descartada")],
        rutas=[IntentRoute(IntentAction.START_TASK_INTAKE,
                           {"objective": "service delay"})])
    g = ProveedorGrabador(interno=interno)
    _con(monkeypatch, g)
    _turno(conn, corework, "creá una tarea: t", con_entrante=True)
    grabacion = g.a_json()
    assert grabacion["respuestas"] == []
    assert len(grabacion["rutas"]) == 1
