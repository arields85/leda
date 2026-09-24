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
from prisma.llm import (IntentAction, IntentRoute, Llamada, ProveedorGuionado,
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


class _JevPorReferencia:
    """Doble de Jev que responde según `state["referencia"]`, no según el
    orden global de llamadas (T7, punto A2): `_resolver_en_paralelo` corre
    las referencias de un mismo turno en hilos, así que el orden real en que
    llegan las llamadas a la red no es determinístico -- un guión FIFO único
    (como `ClienteJevGuionado`) no sirve para escenarios con más de una
    referencia que necesiten cantidades de llamadas distintas."""

    def __init__(self, guiones: dict[str, list[dict]]):
        self._guiones = {referencia: list(pasos) for referencia, pasos in guiones.items()}
        self.pedidos: list[tuple[dict, dict]] = []

    def decidir(self, state, preguntas):
        self.pedidos.append((state, preguntas))
        cola = self._guiones[state["referencia"]]
        if not cola:
            raise jev_modulo.JevError(
                f"Guión agotado para {state['referencia']!r}.")
        return cola.pop(0)


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
    assert "nombrala por su título exacto" in sistema


def test_referencia_clara_protege_la_respuesta_que_no_nombra_la_tarea(
        corework, conn, monkeypatch, con_credencial):
    """T5: la protección determinística llega hasta el turno completo, no
    sólo hasta el sistema que ve el modelo -- `gateway._turno` tiene que
    pasarle a `agente.responder` los ids que resolvió CLARA para que, si el
    modelo consulta la tarea y no la nombra en su respuesta, la respuesta
    visible la nombre igual."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea_id = _tarea(cur, ws, titulo="Cablear tablero máq. 3",
                          persona="Marcos Tarquini")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea_resp({"T1": 0.9})},
        {"misma": {"noul": 0.8}},
    ])
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=("lo del tablero",))],
        guion=[Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
              Respuesta(texto="Va bien, sin bloqueos.")])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿cómo va lo del tablero?", ws, chat_id=9)

    with admin(conn) as cur:
        cur.execute("select cuerpo from message_outbox where chat_id = 9")
        cuerpo = cur.fetchone()["cuerpo"]
    assert cuerpo == "Sobre «Cablear tablero máq. 3»:\n\nVa bien, sin bloqueos."


# ---------------------------------------------------------------------------
# Ambigua
# ---------------------------------------------------------------------------

def test_referencia_ambigua_sin_candidatas_pregunta_en_texto(
        corework, conn, monkeypatch, con_credencial):
    """Ambigua SIN candidatas por encima del corte sigue el texto de T3 (T4,
    requisito 7): sin candidatos reales no hay botones que ofrecer."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero máq. 3")
        _tarea(cur, ws, titulo="Revisar tablero máq. 4")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea_resp({"T1": 0.05, "T2": 0.03})},
    ])
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        resultado = gateway._turno(cur, quien, "avisame de lo del tablero", ws, chat_id=3)

    sistema, _ = proveedor.recibidos[-1]
    assert "ambigua y no quedó ninguna candidata" in sistema
    assert "sin adivinar" in sistema or "sin actuar" in sistema
    assert "Usá esa tarea" not in sistema
    assert resultado is None            # `_turno` no devuelve nada; nada se ejecutó

    with admin(conn) as cur:
        cur.execute("select count(*) n from pending_action")
        assert cur.fetchone()["n"] == 0, "sin candidatas no hay botones que ofrecer"


# ---------------------------------------------------------------------------
# Varias tareas (T7, punto C): abarca varias, nunca abre botones
# ---------------------------------------------------------------------------

def test_referencia_varias_tareas_no_abre_botones_y_llega_como_contexto(
        corework, conn, monkeypatch, con_credencial):
    """El banco real medía botones de más para un pedido genérico ("algo
    pendiente esta semana", b-0001-b): alcance "varias_tareas" es un tipo
    aparte de la ambigüedad de una sola tarea (T4 reserva los botones para
    esa), así que nunca abre botones -- se le pasa al modelo la lista de
    candidatas como contexto, con la instrucción de responder sobre todas si
    consultan y de preguntar cuál (en texto) si piden un cambio."""
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
                                        trabajos=("algo pendiente esta semana",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿qué tengo pendiente esta semana?", ws, chat_id=6)

    sistema, _ = proveedor.recibidos[-1]
    assert "abarca varias tareas" in sistema
    assert "Cablear tablero máq. 3" in sistema and "Revisar tablero máq. 4" in sistema
    assert "contestá sobre todas" in sistema
    assert "preguntá" in sistema.lower()
    assert "Usá esa tarea" not in sistema

    with admin(conn) as cur:
        cur.execute("select count(*) n from pending_action")
        assert cur.fetchone()["n"] == 0, "alcance varias nunca abre botones"


# ---------------------------------------------------------------------------
# Dedupe determinístico (T7, punto A2)
# ---------------------------------------------------------------------------

def test_referencia_ambigua_redundante_con_una_clara_se_descarta(
        corework, conn, monkeypatch, con_credencial):
    """Cuando el enrutador separa dos referencias para la misma tarea (una
    queda CLARA y la otra queda ambigua con esa misma tarea como única
    candidata -- p. ej. un estado que se coló como "trabajo" pese al ajuste
    del enrutador), la segunda no suma nada para preguntar: se descarta
    entera, sin botón y sin línea en el bloque de contexto."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea_id = _tarea(cur, ws, titulo="Cablear tablero máq. 3")
    conn.commit()

    doble = _JevPorReferencia({
        "lo del tablero": [
            {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea_resp({"T1": 0.9})},
            {"misma": {"noul": 0.8}},                   # verificación de la CLARA
        ],
        "revisión": [
            {"alcance": _alcance(una_tarea=0.9), "tarea": _tarea_resp({"T1": 0.6})},
        ],
    })
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(
            IntentAction.NORMAL_CONVERSATION,
            trabajos=("lo del tablero", "revisión"))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿cómo va lo del tablero, ya está en revisión?",
                       ws, chat_id=7)

    sistema, _ = proveedor.recibidos[-1]
    assert f"«lo del tablero» es la tarea «Cablear tablero máq. 3» ({tarea_id})" in sistema
    assert "«revisión»" not in sistema           # se descartó, no suma nada para preguntar

    with admin(conn) as cur:
        cur.execute("select count(*) n from pending_action")
        assert cur.fetchone()["n"] == 0, "candidata ya resuelta CLARA: nada que preguntar"


def test_referencia_ambigua_con_una_candidata_sin_resolver_no_se_descarta(
        corework, conn, monkeypatch, con_credencial):
    """El dedupe es seguro: si a la referencia ambigua le queda aunque sea
    una candidata que ninguna otra referencia resolvió CLARA, se queda --
    nunca se descarta "por las dudas"."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea_id = _tarea(cur, ws, titulo="Cablear tablero máq. 3")
        _tarea(cur, ws, titulo="Revisar tablero máq. 4")
    conn.commit()

    doble = _JevPorReferencia({
        "lo del tablero": [
            {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea_resp({"T1": 0.9})},
            {"misma": {"noul": 0.8}},
        ],
        "lo otro": [
            {"alcance": _alcance(una_tarea=0.9),
             "tarea": _tarea_resp({"T1": 0.6, "T2": 0.4})},
        ],
    })
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(
            IntentAction.NORMAL_CONVERSATION,
            trabajos=("lo del tablero", "lo otro"))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿cómo va lo del tablero y lo otro?", ws, chat_id=8)

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from pending_action where herramienta = %s",
            (gateway._SENTINEL_ACLARACION,))
        assert cur.fetchone()["n"] == 1, "tiene una candidata sin resolver: no se descarta"


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
    assert "no la inventes ni la trates como una" in sistema
    assert "preguntá" in sistema.lower()
    assert not doble.pedidos                       # nunca llamó a Jev


def test_referencia_ninguna_no_ordena_preguntar_sin_condicion_cuando_hay_clara(
        corework, conn, monkeypatch, con_credencial):
    """T7, punto B: "ninguna" no fuerza a preguntar cuando el resto del
    mensaje ya quedó claro -- el bloque de contexto dice que esa referencia
    no es una tarea activa y que no se la invente, pero ya no manda
    "preguntá" sin condición como antes de esta unidad."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea_id = _tarea(cur, ws, titulo="Cablear tablero máq. 3")
    conn.commit()

    doble = _JevPorReferencia({
        "lo del tablero": [
            {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea_resp({"T1": 0.9})},
            {"misma": {"noul": 0.8}},
        ],
        "el horno": [
            {"alcance": _alcance(ninguna=0.9), "tarea": _tarea_resp({"T1": 0.02})},
        ],
    })
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(
            IntentAction.NORMAL_CONVERSATION,
            trabajos=("lo del tablero", "el horno"))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿cómo va lo del tablero? ¿y el horno?", ws, chat_id=9)

    sistema, _ = proveedor.recibidos[-1]
    assert f"«lo del tablero» es la tarea «Cablear tablero máq. 3» ({tarea_id})" in sistema
    assert "no coincide con ninguna tarea activa" in sistema
    assert "No inventes una tarea para eso: preguntá." not in sistema


# ---------------------------------------------------------------------------
# Referencias de sólo estado (T7, punto E): nunca llegan a Jev
# ---------------------------------------------------------------------------

def test_referencia_de_solo_estado_nunca_llega_a_jev(
        corework, conn, monkeypatch, con_credencial):
    """El banco real mostraba a Jev resolviendo "revisión" (separada como
    "trabajo" pese al ajuste del enrutador) contra "Revisar tablero de la
    máquina 4" -- un falso positivo porque el nombre de la tarea comparte
    raíz con la palabra de estado. Una referencia cuyo texto normalizado es
    sólo un estado de tarea (vocabulario cerrado del producto) nunca se manda
    a Jev: no abre botón, no deja línea en el bloque de contexto, no gasta
    una llamada."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea_id = _tarea(cur, ws, titulo="Cablear tablero máq. 3")
        _tarea(cur, ws, titulo="Revisar tablero máq. 4")
    conn.commit()

    doble = _JevPorReferencia({
        "lo del tablero": [
            {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea_resp({"T1": 0.9})},
            {"misma": {"noul": 0.8}},
        ],
        # Ninguna entrada para "revisión": si algo la manda a Jev, el doble
        # tira `JevError` por guión agotado y la prueba lo delata.
    })
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(
            IntentAction.NORMAL_CONVERSATION,
            trabajos=("lo del tablero", "revisión"))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿cómo va lo del tablero, ya está en revisión?",
                       ws, chat_id=10)

    sistema, _ = proveedor.recibidos[-1]
    assert f"«lo del tablero» es la tarea «Cablear tablero máq. 3» ({tarea_id})" in sistema
    assert "«revisión»" not in sistema
    assert not any(state["referencia"] == "revisión" for state, _preguntas in doble.pedidos)

    with admin(conn) as cur:
        cur.execute("select count(*) n from pending_action")
        assert cur.fetchone()["n"] == 0, "una referencia de estado nunca abre botón"


@pytest.mark.parametrize("referencia", [
    "revisión", "en revisión", "en revision", "terminado", "terminada",
    "listo", "hecho", "bloqueado", "bloqueada", "pendiente", "resuelto",
    "cancelado", "la revisión", "el terminado", "a resuelto",
])
def test_mensaje_con_una_sola_referencia_de_estado_no_toca_jev_ni_la_red(
        corework, conn, monkeypatch, con_credencial, referencia):
    """Si la única referencia del mensaje es de estado, el turno sigue
    exactamente como si no hubiera ninguna referencia: sin bloque de
    contexto, sin llamar a Jev."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero máq. 3")
    conn.commit()

    doble = ClienteJevGuionado(guion=[])            # cualquier llamada la delata
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=(referencia,))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, f"¿ya está {referencia}?", ws, chat_id=11)

    sistema, _ = proveedor.recibidos[-1]
    assert "Referencias a tareas" not in sistema
    assert not doble.pedidos
    with admin(conn) as cur:
        cur.execute("select count(*) n from audit_log where accion = 'resolucion_referencias'")
        assert cur.fetchone()["n"] == 0


def test_referencia_de_estado_no_confunde_una_referencia_real(
        corework, conn, monkeypatch, con_credencial):
    """El filtro es un vocabulario cerrado, no una heurística amplia: "el
    switch" (una causa/cosa que falta, no un estado) sigue viajando a Jev tal
    cual -- éste es justamente el caso que la corrección de A2/A1 ya cubre
    por otro lado, y E no debe interferir con él."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Cablear tablero máq. 3")
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(ninguna=0.9), "tarea": _tarea_resp({"T1": 0.02})},
    ])
    _con_jev(monkeypatch, doble)
    proveedor = _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=("el switch",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "ya llegó el switch", ws, chat_id=12)

    assert len(doble.pedidos) == 1                  # sí se mandó a Jev


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
# Bloqueos abiertos en el criterio de Jev (T7, punto H; decisión del
# usuario, 2026-09-24: las causas de bloqueo pueden viajar a TypeSafe vía
# OpenRouter)
# ---------------------------------------------------------------------------

def test_tarea_activa_con_bloqueo_abierto_lleva_la_causa_al_criterio(
        corework, conn, monkeypatch, con_credencial):
    """b-0003: "ya llegó el switch que faltaba para el tablero, dalo por
    resuelto" nombra la tarea por su bloqueo, no por su título -- sin la
    causa en el criterio, Jev no tiene con qué reconocerla."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea_id = _tarea(cur, ws, titulo="Cablear tablero máq. 3")
        cur.execute(
            "insert into blocker (workspace_id, task_id, causa) values (%s, %s, %s)",
            (ws, tarea_id, "falta el switch industrial en sala"))
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea_resp({"T1": 0.9})},
        {"misma": {"noul": 0.8}},
    ])
    _con_jev(monkeypatch, doble)
    _con_proveedor(
        monkeypatch, rutas=[IntentRoute(
            IntentAction.NORMAL_CONVERSATION,
            trabajos=("el switch que faltaba",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "ya llegó el switch que faltaba, dalo por resuelto",
                       ws, chat_id=14)

    criterio_alcance = doble.pedidos[0][1]["tarea"]["criteria"]["T1"]
    criterio_verificacion = doble.pedidos[1][0]["tarea"]
    assert "bloqueada: falta el switch industrial en sala" in criterio_alcance
    assert "bloqueada: falta el switch industrial en sala" in criterio_verificacion


def test_tarea_sin_bloqueo_abierto_no_cambia_el_criterio(
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
                                        trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿cómo va lo del tablero?", ws, chat_id=15)

    criterio = doble.pedidos[0][1]["tarea"]["criteria"]["T1"]
    assert "bloqueada" not in criterio


def test_bloqueo_resuelto_no_viaja_al_criterio(
        corework, conn, monkeypatch, con_credencial):
    """Sólo los bloqueos abiertos (`resuelto_en is null`) cuentan -- uno ya
    resuelto es historia, no una razón activa para reconocer la tarea."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea_id = _tarea(cur, ws, titulo="Cablear tablero máq. 3")
        cur.execute(
            """insert into blocker (workspace_id, task_id, causa, resuelto_en)
               values (%s, %s, %s, now())""",
            (ws, tarea_id, "ya resuelto hace tiempo"))
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea_resp({"T1": 0.9})},
        {"misma": {"noul": 0.8}},
    ])
    _con_jev(monkeypatch, doble)
    _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿cómo va lo del tablero?", ws, chat_id=16)

    criterio = doble.pedidos[0][1]["tarea"]["criteria"]["T1"]
    assert "bloqueada" not in criterio


def test_varios_bloqueos_abiertos_se_unen_en_el_criterio(
        corework, conn, monkeypatch, con_credencial):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tarea_id = _tarea(cur, ws, titulo="Cablear tablero máq. 3")
        cur.execute(
            "insert into blocker (workspace_id, task_id, causa) values (%s, %s, %s)",
            (ws, tarea_id, "falta el switch industrial en sala"))
        cur.execute(
            "insert into blocker (workspace_id, task_id, causa) values (%s, %s, %s)",
            (ws, tarea_id, "falta aprobación del plano"))
    conn.commit()

    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea_resp({"T1": 0.9})},
        {"misma": {"noul": 0.8}},
    ])
    _con_jev(monkeypatch, doble)
    _con_proveedor(
        monkeypatch, rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                        trabajos=("lo del tablero",))])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, "¿cómo va lo del tablero?", ws, chat_id=17)

    criterio = doble.pedidos[0][1]["tarea"]["criteria"]["T1"]
    assert "falta el switch industrial en sala" in criterio
    assert "falta aprobación del plano" in criterio


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
