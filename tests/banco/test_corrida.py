"""Pruebas de la corrida y grabación del banco: el proveedor grabador (sin
base, con un `ProveedorGuionado` interno) y `ejecutar_escenario` sobre el
circuito real (`gateway.procesar_update`), con la base descartable de las
pruebas. TDD estricto.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import psycopg
import pytest

import prisma.jev as jev
from prisma import agente, herramientas
from prisma import pendientes as P
from prisma.salida import etiqueta_sin_icono
from prisma.autoridad import Canal, identificar
from prisma.db import admin, espacio
from prisma.jev import ClienteJevGuionado
from prisma.llm import IntentAction, IntentRoute, Llamada, ProveedorGuionado, Respuesta

from tests.banco.comprobadores import comprobar_aclaracion
from tests.banco.corrida import (
    ClienteJevGuionadoPorReferencia,
    JevGrabador,
    ProveedorGrabador,
    _MARCA_TURNO_CAIDO,
    _candidatas_tarea_por_titulo,
    _pendiente_para_confirmar,
    _resolver_opcion_toque,
    _resolver_toque_generico,
    conteos_delta,
    ejecutar_escenario,
    filas_respuesta,
    guionado_desde_grabacion,
    jev_guionado_desde_grabacion,
    recolectar_efectos,
    respuesta_ofrecio_opciones,
    sembrar_precondiciones,
)

# Cuando la prueba no le importa el filtro `desde` de esta unidad (restringir
# la unión a lo creado durante la corrida actual), una fecha bien anterior
# incluye cualquier fila que la prueba haya sembrado.
_MUY_ANTES = datetime(2000, 1, 1, tzinfo=timezone.utc)


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


def test_grabacion_json_redondea_trabajos_y_personas():
    interno = ProveedorGuionado(
        guion=[],
        rutas=[IntentRoute(
            IntentAction.NORMAL_CONVERSATION,
            trabajos=("lo del tablero",), personas=("Lucas", "Nahuel"))],
    )
    g = ProveedorGrabador(interno)
    g.route_intent("¿lucas y nahuel vieron lo del tablero?")

    import json
    grabacion = json.loads(json.dumps(g.a_json()))
    assert grabacion["rutas"][0]["salida"]["trabajos"] == ["lo del tablero"]
    assert grabacion["rutas"][0]["salida"]["personas"] == ["Lucas", "Nahuel"]

    guionado = guionado_desde_grabacion(grabacion)
    ruta = guionado.route_intent("cualquier cosa")
    assert ruta.trabajos == ("lo del tablero",)
    assert ruta.personas == ("Lucas", "Nahuel")


def test_grabacion_vieja_sin_trabajos_ni_personas_sigue_cargando():
    """Una grabación guardada antes de T2 no tiene las claves nuevas -- tiene
    que seguir cargando, con referencias vacías por defecto."""
    grabacion_vieja = {
        "rutas": [{"entrada": "listo", "salida": {
            "action": "normal_conversation", "task": {}}, "latencia_s": 0.1}],
        "respuestas": [],
    }

    guionado = guionado_desde_grabacion(grabacion_vieja)
    ruta = guionado.route_intent("cualquier cosa")
    assert ruta.trabajos == ()
    assert ruta.personas == ()


# ---------------------------------------------------------------------------
# JevGrabador: grabación y round-trip a JSON / ClienteJevGuionado (T6,
# `aclaracion-con-botones`) -- mismo patrón que ProveedorGrabador, para que
# una corrida contra un Jev real se pueda repetir después sin red.
# ---------------------------------------------------------------------------


def test_jev_grabador_registra_pedido_y_respuesta():
    interno = ClienteJevGuionado(guion=[{"alcance": {"probabilities": {"ninguna": 0.9}}}])
    g = JevGrabador(interno)

    respuesta = g.decidir({"mensaje": "hola"}, {"alcance": {"type": "choice"}})

    assert respuesta == {"alcance": {"probabilities": {"ninguna": 0.9}}}
    assert len(g.pedidos) == 1
    assert g.pedidos[0]["state"] == {"mensaje": "hola"}
    assert g.pedidos[0]["preguntas"] == {"alcance": {"type": "choice"}}
    assert g.pedidos[0]["respuesta"] == respuesta


def test_jev_grabacion_json_es_serializable_y_recargable():
    """Las dos llamadas grabadas comparten la misma referencia (ninguna trae
    `"referencia"` en su `state`, así que las dos caen bajo la misma clave
    `None`) -- se devuelven en el mismo orden en que se grabaron, dentro de
    esa referencia."""
    interno = ClienteJevGuionado(guion=[
        {"alcance": {"probabilities": {"una_tarea": 0.9}},
         "tarea": {"probabilities": {"T1": 0.9}}},
        {"misma": {"noul": 0.8}},
    ])
    g = JevGrabador(interno)
    g.decidir({"mensaje": "a"}, {"alcance": {}, "tarea": {}})
    g.decidir({"mensaje": "a", "tarea": "x"}, {"misma": {}})

    import json
    grabacion = json.loads(json.dumps(g.a_json()))

    jev_guionado = jev_guionado_desde_grabacion({"jev": grabacion})
    assert isinstance(jev_guionado, ClienteJevGuionadoPorReferencia)
    r1 = jev_guionado.decidir({}, {})
    assert r1["alcance"]["probabilities"]["una_tarea"] == 0.9
    r2 = jev_guionado.decidir({}, {})
    assert r2["misma"]["noul"] == 0.8


def test_jev_grabacion_vieja_sin_clave_jev_sigue_cargando():
    """Una grabación de antes de T6 no tiene la clave 'jev' -- tiene que
    seguir cargando, sin ningún pedido grabado (nunca llama a Jev de verdad
    si el escenario no traía ninguna referencia que lo hubiera ejercitado)."""
    grabacion_vieja = {"rutas": [], "respuestas": []}
    jev_guionado = jev_guionado_desde_grabacion(grabacion_vieja)
    assert isinstance(jev_guionado, ClienteJevGuionadoPorReferencia)
    assert jev_guionado.pedidos_grabados == []
    with pytest.raises(jev.JevError):
        jev_guionado.decidir({"referencia": "lo que sea"}, {})


# ---------------------------------------------------------------------------
# ClienteJevGuionadoPorReferencia (esta unidad, hallazgo del orquestador,
# investigación de b-0005-b): agrupa por `state["referencia"]`, no una cola
# FIFO única -- `gateway._resolver_en_paralelo` resuelve cada referencia en
# su propio hilo, así que el orden real de llegada a `decidir()` no tiene
# por qué coincidir con el orden de grabación cuando un mensaje trae más de
# un `trabajo`.
# ---------------------------------------------------------------------------

def test_cliente_jev_guionado_por_referencia_devuelve_lo_de_cada_una_sin_importar_el_orden():
    pedidos_grabados = [
        {"state": {"referencia": "el plc"}, "respuesta": {"tarea": "respuesta-A-1"}},
        {"state": {"referencia": "lo del cableado"}, "respuesta": {"tarea": "respuesta-B-1"}},
        {"state": {"referencia": "lo del cableado", "tarea": "x"},
         "respuesta": {"misma": "respuesta-B-2-verificacion"}},
    ]
    cliente = ClienteJevGuionadoPorReferencia(pedidos_grabados=pedidos_grabados)

    # Orden de llamada DELIBERADAMENTE distinto al de grabación -- "lo del
    # cableado" pide primero, dos veces (su ronda inicial y su verificación),
    # y "el plc" pide después: con una cola FIFO única esto habría devuelto
    # las respuestas de "el plc"/"lo del cableado" cruzadas.
    r_cableado_1 = cliente.decidir({"referencia": "lo del cableado"}, {})
    r_cableado_2 = cliente.decidir({"referencia": "lo del cableado", "tarea": "x"}, {})
    r_plc = cliente.decidir({"referencia": "el plc"}, {})

    assert r_cableado_1 == {"tarea": "respuesta-B-1"}
    assert r_cableado_2 == {"misma": "respuesta-B-2-verificacion"}
    assert r_plc == {"tarea": "respuesta-A-1"}


def test_cliente_jev_guionado_por_referencia_agotada_para_una_referencia_no_afecta_otra():
    pedidos_grabados = [
        {"state": {"referencia": "A"}, "respuesta": {"tarea": "respuesta-A"}},
    ]
    cliente = ClienteJevGuionadoPorReferencia(pedidos_grabados=pedidos_grabados)

    assert cliente.decidir({"referencia": "A"}, {}) == {"tarea": "respuesta-A"}
    with pytest.raises(jev.JevError, match="'B'"):
        cliente.decidir({"referencia": "B"}, {})


def test_cliente_jev_guionado_por_referencia_registra_todos_los_pedidos():
    pedidos_grabados = [{"state": {"referencia": "A"}, "respuesta": {"tarea": "r"}}]
    cliente = ClienteJevGuionadoPorReferencia(pedidos_grabados=pedidos_grabados)
    cliente.decidir({"referencia": "A"}, {"p": 1})
    assert cliente.pedidos == [({"referencia": "A"}, {"p": 1})]


def test_resolver_en_paralelo_con_guionado_por_referencia_no_cruza_las_dos_referencias():
    """Prueba de punta a punta del hallazgo real (b-0005-b): dos referencias
    del mismo mensaje, resueltas por `gateway._resolver_en_paralelo` (el
    mismo `ThreadPoolExecutor` de producción), cada una tiene que recibir su
    propia probabilidad grabada -- nunca la de la otra."""
    from prisma.gateway import _resolver_en_paralelo
    from prisma.jev import TareaCandidata

    pedidos_grabados = [
        {"state": {"referencia": "el plc"},
         "respuesta": {"alcance": {"probabilities": {"una_tarea": 0.58, "ninguna": 0.13,
                                                     "varias_tareas": 0.29}},
                       "tarea": {"probabilities": {"T1": 0.76, "T2": 0.24}}}},
        {"state": {"referencia": "lo del cableado del tablero"},
         "respuesta": {"alcance": {"probabilities": {"una_tarea": 0.9, "ninguna": 0,
                                                     "varias_tareas": 0.1}},
                       "tarea": {"probabilities": {"T1": 0.01, "T2": 0.99}}}},
        {"state": {"referencia": "lo del cableado del tablero", "tarea": "x"},
         "respuesta": {"misma": {"noul": 0.93}, "rival": {"noul": 0.11}}},
    ]
    tareas = [
        TareaCandidata(id="t1", titulo="Programar PLC de la comprimidora (simulado)",
                       area="ot", responsable="Nahuel Gimenez"),
        TareaCandidata(id="t2", titulo="Cablear tablero de la máquina 3 (simulado)",
                       area="ot", responsable="Marcos Tarquini"),
    ]

    for _ in range(20):     # repetido: el cruce por scheduling era intermitente
        # Un cliente fresco por vuelta: cada uno sólo tiene una respuesta
        # grabada por referencia (más su verificación).
        cliente = ClienteJevGuionadoPorReferencia(pedidos_grabados=list(pedidos_grabados))
        resultados = _resolver_en_paralelo(
            cliente, texto="che, anota que depende...",
            referencias=("lo del cableado del tablero", "el plc"),
            tareas=tareas, vocabulario="")
        resolucion_plc, error_plc = resultados["el plc"]
        resolucion_cab, error_cab = resultados["lo del cableado del tablero"]
        assert error_plc is None and error_cab is None
        assert resolucion_plc.tipo is jev.TipoResolucion.AMBIGUA
        assert resolucion_cab.tipo is jev.TipoResolucion.CLARA
        assert resolucion_cab.tarea_id == "t2"


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
# ejecutar_escenario: el proveedor caído (evidencia real, 2026-09-26: un
# corrida real contra un proveedor que devolvía 404 quedó `aprobado` porque
# `gateway.procesar_update` atajó el fallo adentro y nunca propagó nada que
# `ejecutar_escenario` capturara como `bloqueado`). "No poder consultar no
# equivale a que no haya nada que hacer" (AGENTS.md): la corrida tiene que
# quedar `bloqueado`, no aprobada por default, cuando el proveedor no
# contestó -- ni al enrutar (`gateway._routing_incident`) ni en la
# conversación (`agente._incidente` + `agente.DISCULPA`).
# ---------------------------------------------------------------------------


class _ProveedorCaidoAlRutear:
    """El proveedor no contesta ni una vez a `route_intent` -- el mismo
    síntoma que un 404 sostenido del proveedor real."""

    def route_intent(self, text):
        raise RuntimeError("Proveedor caído: sin ruta.")

    def responder(self, sistema, mensajes, herramientas):  # pragma: no cover
        raise AssertionError("no debería llegar a responder sin haber ruteado")


class _ProveedorCaidoAlResponder:
    """El ruteo contesta bien, pero la llamada principal del agente
    (`agente.responder` -> `proveedor.responder`) es la que cae."""

    def route_intent(self, text):
        return IntentRoute(IntentAction.NORMAL_CONVERSATION)

    def responder(self, sistema, mensajes, herramientas):
        raise RuntimeError("Proveedor caído: sin respuesta.")


def test_ejecutar_escenario_proveedor_caido_al_rutear_queda_bloqueado(corework, conn):
    ws = corework.workspace_id
    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["hola"],
        _ProveedorCaidoAlRutear(), escenario_id="b-test", indice=0)

    assert r.bloqueado is True
    assert r.motivo_bloqueo
    assert "secreto" not in r.motivo_bloqueo.lower()


def test_ejecutar_escenario_proveedor_caido_al_responder_queda_bloqueado(corework, conn):
    ws = corework.workspace_id
    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["hola"],
        _ProveedorCaidoAlResponder(), escenario_id="b-test", indice=0)

    assert r.bloqueado is True
    assert r.motivo_bloqueo
    # El bloqueo tiene que venir de la marca de `agente._incidente` (turno
    # caído), no de cualquier incidente que haya quedado en el espacio --
    # `agente._incidente` también se usa para un `psycopg.Error` de una sola
    # herramienta que no bloquea (ver
    # `test_ejecutar_escenario_incidente_de_herramienta_sin_disculpa_no_bloquea`).
    assert r.motivo_bloqueo.startswith(_MARCA_TURNO_CAIDO)


def test_ejecutar_escenario_corrida_sana_no_queda_bloqueada_por_el_chequeo_nuevo(corework, conn):
    """El chequeo de incidentes de proveedor caído no debe marcar `bloqueado`
    una corrida sana -- una corrida guionada normal sigue pasando igual."""
    ws = corework.workspace_id
    interno = ProveedorGuionado(
        guion=[Respuesta(texto="Anotado.")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )
    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["hola"], interno,
        escenario_id="b-test", indice=0)

    assert r.bloqueado is False
    assert r.motivo_bloqueo == ""


def test_ejecutar_escenario_incidente_de_herramienta_sin_disculpa_no_bloquea(
        corework, conn, monkeypatch):
    """Cobertura sugerida por la revisión del orquestador del 2026-09-26
    (`tests/banco/test_corrida.py`, ~309-316 de esa revisión): la marca de
    `agente._incidente` (`_MARCA_TURNO_CAIDO`) también aparece cuando falla
    una sola herramienta dentro de un turno que sigue con normalidad
    (`agente._ejecutar_una`, `except psycopg.Error`) -- eso NO es "el
    proveedor no contestó", así que no puede bloquear la corrida. La marca
    sólo cuenta como proveedor caído si además la respuesta visible es
    `agente.DISCULPA` (el `except` que envuelve a `proveedor.responder`
    entero, nunca el de una herramienta individual).

    El turno rutea bien (`ProveedorGuionado.route_intent` por defecto, sin
    `rutas`, ya devuelve conversación normal): la única vuelta guionada llama
    a `consultar_tareas`, que acá se hace fallar con un `psycopg.Error`
    (`herramientas.ejecutar` reemplazado por `monkeypatch`); la segunda
    vuelta, con el resultado de error ya en `mensajes`, cierra con un texto
    común, sin `DISCULPA`."""
    ws = corework.workspace_id

    def falla(*args, **kwargs):
        raise psycopg.OperationalError("boom")

    monkeypatch.setattr(herramientas, "ejecutar", falla)

    interno = ProveedorGuionado(guion=[
        Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
        Respuesta(texto="Ya reviso y te aviso."),
    ])
    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["hola"], interno,
        escenario_id="b-test", indice=0)

    assert agente.DISCULPA not in r.respuesta_texto
    assert r.bloqueado is False
    assert r.motivo_bloqueo == ""

    with admin(conn) as cur:
        cur.execute(
            "select resumen_sanitizado from incident where workspace_id = %s", (ws,))
        resumenes = [f["resumen_sanitizado"] for f in cur.fetchall()]
    assert any(resumen.startswith(_MARCA_TURNO_CAIDO) for resumen in resumenes)


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
                  {"bloqueo_id": bloqueo_id, "resolucion": "listo (simulado)"},
                  ya_confirmada=True)
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


# ---------------------------------------------------------------------------
# respuesta_ofrecio_opciones (odd/tasks/banco-mensajes-humanos.md, T1): si
# una respuesta ofreció botones, `message_outbox` tiene `pending_action_id`
# (confirmación o elección, `agente.py::_encolar_confirmacion`/
# `_encolar_eleccion`) o `intake_choice_set_id` (alta guiada de tarea,
# `ingreso_tareas.py::_open_choices`) no nulo -- lo que lee
# `despachador.py::_botones` para armar los botones al despachar.
# ---------------------------------------------------------------------------


def test_ofrecio_opciones_con_pending_action_id_es_true():
    filas = [{"id": "1", "cuerpo": "¿Confirmás?", "pending_action_id": "p1",
             "intake_choice_set_id": None}]
    assert respuesta_ofrecio_opciones(filas) is True


def test_ofrecio_opciones_con_intake_choice_set_id_es_true():
    filas = [{"id": "1", "cuerpo": "¿Cuál es el objetivo?", "pending_action_id": None,
             "intake_choice_set_id": "c1"}]
    assert respuesta_ofrecio_opciones(filas) is True


def test_ofrecio_opciones_sin_ninguno_de_los_dos_es_false():
    filas = [{"id": "1", "cuerpo": "Tenés dos tareas pendientes.",
             "pending_action_id": None, "intake_choice_set_id": None}]
    assert respuesta_ofrecio_opciones(filas) is False


def test_ofrecio_opciones_lista_vacia_es_false():
    assert respuesta_ofrecio_opciones([]) is False


def test_ejecutar_escenario_recolecta_ofrecio_opciones_false_por_defecto(corework, conn):
    ws = corework.workspace_id
    interno = ProveedorGuionado(
        guion=[Respuesta(texto="Anotado.")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )
    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["hola"], interno,
        escenario_id="b-test", indice=0)
    assert r.ofrecio_opciones is False


def test_filas_respuesta_trae_pending_action_id_e_intake_choice_set_id(corework, conn):
    """Prueba directa contra el esquema real: `message_outbox` tiene las dos
    columnas que `despachador.py::_botones` usa para armar los botones al
    despachar (`pending_action_id`: confirmación/elección de
    `agente.py`; `intake_choice_set_id`: alta guiada de tarea,
    `ingreso_tareas.py::_open_choices`). No pasa por `gateway.procesar_update`
    -- es una prueba de la consulta de `corrida.py`, no del circuito."""
    from datetime import datetime, timedelta, timezone

    from prisma.autoridad import Canal, identificar
    from prisma.pendientes import registrar
    from prisma.salida import enqueue_outbox

    from tests.banco.corrida import _telegram_id

    ws = corework.workspace_id
    chat = _telegram_id(conn, ws, "Marcos Tarquini")
    with admin(conn) as cur:
        cur.execute("select id from message_outbox where workspace_id = %s", (ws,))
        previos = {f["id"] for f in cur.fetchall()}

        quien = identificar(cur, chat, Canal.ESPACIO, ws)
        pendiente = registrar(
            cur, quien, herramienta="actualizar_estado", args={},
            resumen="¿Confirmás que la paso a revisión?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1), chat_id=chat)
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=chat, text="¿Confirmás que la paso a revisión?",
            dedupe_key="test:oferta-en-corrida", is_response=True,
            pending_action_id=pendiente.id)

        filas = filas_respuesta(cur, ws, chat, previos)

    assert len(filas) == 1
    assert str(filas[0]["pending_action_id"]) == pendiente.id
    assert filas[0]["intake_choice_set_id"] is None
    assert respuesta_ofrecio_opciones(filas) is True


# ---------------------------------------------------------------------------
# _pendiente_para_confirmar (T4): la última acción pendiente 'esperando' de
# un chat que ofrece un botón Confirmar -- la vista previa de una herramienta
# que escribe (T1). Una `NecesitaElegir` (candidatos ambiguos) no lo tiene y
# no se toca acá.
# ---------------------------------------------------------------------------


def _quien(cur, ws, nombre="Marcos Tarquini"):
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    tg = cur.fetchone()["t"]
    return identificar(cur, tg, Canal.ESPACIO, ws), tg


def test_pendiente_para_confirmar_encuentra_la_que_ofrece_confirmar(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws)
        p = P.registrar(
            cur, quien, herramienta="actualizar_estado", args={"a": 1},
            resumen="¿Confirmás?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1), chat_id=tg)

        encontrada = _pendiente_para_confirmar(cur, ws, tg, _MUY_ANTES)

    assert encontrada is not None
    pid, token = encontrada
    assert pid == p.id
    assert token


def test_pendiente_para_confirmar_ignora_una_eleccion_entre_candidatos(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws)
        P.registrar(
            cur, quien, herramienta="crear_tarea", args={"titulo": "Relevar tablero"},
            resumen="¿a quién?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1),
            campo="responsable_membership_id", chat_id=tg,
            opciones=[("Marcos Tarquini", "m1"), ("Martín Forte", "m2")])

        encontrada = _pendiente_para_confirmar(cur, ws, tg, _MUY_ANTES)

    assert encontrada is None


def test_pendiente_para_confirmar_sin_ninguna_pendiente_es_none(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        _, tg = _quien(cur, ws)
        encontrada = _pendiente_para_confirmar(cur, ws, tg, _MUY_ANTES)
    assert encontrada is None


# ---------------------------------------------------------------------------
# `desde` en `_pendiente_para_confirmar` (esta unidad, hallazgo del
# orquestador): restringe la unión a lo creado durante ESTA corrida, para que
# una acción que quedó esperando de un turno ANTERIOR del mismo chat no
# vuelva ambigua (o gane por casualidad) una confirmación de ahora.
# ---------------------------------------------------------------------------

def test_pendiente_para_confirmar_ignora_una_pendiente_anterior_a_desde(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws)
        # "Anterior" (de un turno de otra corrida, o de antes en el mismo
        # chat): queda esperando, pero es de ANTES de `desde`.
        P.registrar(
            cur, quien, herramienta="actualizar_estado", args={"a": 1},
            resumen="¿Confirmás la vieja?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1), chat_id=tg)

        # El reloj de la base, no el de Python (mismo motivo que la
        # producción usa `clock_timestamp()`, no `now()`): `now()` queda
        # fijo al inicio de la transacción y no serviría para desempatar acá.
        cur.execute("select clock_timestamp() as ahora")
        desde = cur.fetchone()["ahora"]

        encontrada = _pendiente_para_confirmar(cur, ws, tg, desde)

    assert encontrada is None, "una pendiente de antes de `desde` no cuenta"


def test_pendiente_para_confirmar_dos_pendientes_de_esta_corrida_es_ambiguo(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws)
        P.registrar(
            cur, quien, herramienta="actualizar_estado", args={"a": 1},
            resumen="¿Confirmás la primera?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1), chat_id=tg)
        P.registrar(
            cur, quien, herramienta="registrar_bloqueo", args={"a": 2},
            resumen="¿Confirmás la segunda?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1), chat_id=tg)

        with pytest.raises(LookupError, match="ambiguo"):
            _pendiente_para_confirmar(cur, ws, tg, _MUY_ANTES)


# ---------------------------------------------------------------------------
# ejecutar_escenario confirma automáticamente (T4): una propuesta de una
# herramienta que escribe se toca sola por el mismo camino que un toque real
# de Telegram (`gateway.procesar_update` con un `callback_query`), y antes de
# ese toque no hay ningún efecto en la base.
# ---------------------------------------------------------------------------


def test_ejecutar_escenario_confirma_una_propuesta_de_herramienta_que_escribe(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {
            "tareas": [{"id": "t1", "titulo": "Programar PLC (simulado)",
                       "area": "ot", "responsable": "Marcos Tarquini"}],
        })
    tid = ids["t1"]

    interno = ProveedorGuionado(
        guion=[Respuesta(llamadas=[Llamada(
                   "c1", "actualizar_estado", {"tarea_id": tid, "estado": "en_curso"})]),
              Respuesta(texto="listo")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["pasala a en curso"], interno,
        escenario_id="b-test-confirmar", indice=0)

    assert r.bloqueado is False, r.motivo_bloqueo
    assert r.herramientas_ejecutadas == ["actualizar_estado"]
    assert r.conteos_antes_del_toque is not None
    # Nada de lo que las 8 herramientas escriben cambió antes del toque; el
    # único delta esperado es la vista previa, que sale por la cola.
    for tabla in ("task", "blocker", "dependency", "task_state_event",
                 "objective", "evidence", "approval"):
        assert r.conteos_antes_del_toque[tabla] == r.conteos_antes[tabla], (
            f"'{tabla}' cambió antes de tocar Confirmar")
    assert r.conteos_antes_del_toque["message_outbox"] > r.conteos_antes["message_outbox"], (
        "la vista previa tiene que haber salido por la cola antes del toque")
    # `actualizar_estado` sólo dejó su entrada en audit_log al confirmar
    # (después del toque, no antes) -- señal primaria de la propiedad
    # central (T4, revisión del orquestador).
    assert r.herramientas_antes_del_toque == ()

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"
        cur.execute("select estado from pending_action where herramienta = 'actualizar_estado'")
        assert cur.fetchone()["estado"] == "resuelta"


def test_ejecutar_escenario_sin_propuesta_deja_conteos_antes_del_toque_en_none(
        corework, conn):
    interno = ProveedorGuionado(
        guion=[Respuesta(texto="Anotado.")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )
    r = ejecutar_escenario(
        conn, corework.workspace_id, "corework", "Marcos Tarquini", ["hola"], interno,
        escenario_id="b-test-sin-propuesta", indice=0)

    assert r.bloqueado is False, r.motivo_bloqueo
    assert r.conteos_antes_del_toque is None
    assert r.herramientas_antes_del_toque == ()


# ---------------------------------------------------------------------------
# aclaracion_esperada en ejecutar_escenario (T6, `aclaracion-con-botones`):
# el corredor tapea la candidata elegida para poder retomar el pedido
# original hasta la vista previa, y graba lo que le pidió a Jev en el
# camino.
# ---------------------------------------------------------------------------


def test_ejecutar_escenario_sin_referencias_graba_jev_vacio(corework, conn):
    ws = corework.workspace_id
    interno = ProveedorGuionado(
        guion=[Respuesta(texto="Anotado.")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )
    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["hola"], interno,
        escenario_id="b-test-jev-vacio", indice=0)
    assert r.grabacion["jev"] == {"pedidos": []}
    assert r.etiquetas_aclaracion_ofrecidas == ()


def test_ejecutar_escenario_aclaracion_tapea_la_candidata_elegida_sin_aplicar_nada(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {
            "tareas": [
                {"id": "t1", "titulo": "Cablear tablero máq. 3 (simulado)",
                 "area": "ot", "responsable": "Marcos Tarquini"},
                {"id": "t2", "titulo": "Revisar tablero máq. 4 (simulado)",
                 "area": "ot", "responsable": "Marcos Tarquini"},
            ],
        })
    tid_a = ids["t1"]

    doble_jev = ClienteJevGuionado(guion=[
        {"alcance": {"probabilities": {"una_tarea": 0.8}},
         "tarea": {"probabilities": {"T1": 0.5, "T2": 0.3}}},
    ])
    interno = ProveedorGuionado(
        guion=[Respuesta(llamadas=[Llamada(
                   "c1", "actualizar_estado",
                   {"tarea_id": tid_a, "estado": "en_revision",
                    "evidencia_texto": "Ya quedó cableado."})]),
              Respuesta(texto="listo")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                           trabajos=("lo del tablero",))],
    )

    # Adaptación deliberada (hallazgo 2, sesión 2 por Telegram): la
    # aclaración con botones (`_SENTINEL_ACLARACION`) ahora arma la etiqueta
    # con `salida.acortar_etiqueta_boton` (límite de palabra, objetivo ~30),
    # no con el título completo -- acá los dos títulos superan el objetivo y
    # su "(simulado)" queda afuera, igual que en una corrida real (el propio
    # hallazgo del usuario: "los títulos de sesión terminan en
    # '(simulado)', el corte por palabra normalmente lo deja afuera").
    etiqueta_a = "Cablear tablero máq. 3…"
    etiqueta_b = "Revisar tablero máq. 4…"
    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini",
        ["ya termine lo del tablero, pasala a revision"], interno,
        escenario_id="b-test-aclaracion", indice=0, cliente_jev=doble_jev,
        aclaracion_esperada={
            "candidatas": [etiqueta_a, etiqueta_b],
            "elegir": etiqueta_a})

    assert r.bloqueado is False, r.motivo_bloqueo
    # Ícono de tarea aparte (íconos, decisión del usuario, 2026-09-28): las
    # candidatas de aclaración son botones de tarea.
    ofrecidas_sin_icono = {etiqueta_sin_icono(e) for e in r.etiquetas_aclaracion_ofrecidas}
    assert ofrecidas_sin_icono >= {etiqueta_a, etiqueta_b}
    assert r.herramientas_ejecutadas == ["actualizar_estado"]
    # Nada de lo que las 8 herramientas escriben cambió mientras se
    # preguntaba con botones ni antes del toque en Confirmar -- la
    # propiedad central de T4 tiene que seguir valiendo con el paso nuevo
    # de la mitad.
    for tabla in ("task", "blocker", "dependency", "task_state_event",
                 "objective", "evidence", "approval"):
        assert r.conteos_antes_del_toque[tabla] == r.conteos_antes[tabla], (
            f"'{tabla}' cambió antes de tocar Confirmar")
    assert r.herramientas_antes_del_toque == ()
    assert r.grabacion["jev"]["pedidos"], "tiene que haber grabado el pedido a Jev"

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid_a,))
        assert cur.fetchone()["estado"] == "en_revision"


def test_ejecutar_escenario_sin_aclaracion_esperada_no_junta_etiquetas(corework, conn):
    ws = corework.workspace_id
    interno = ProveedorGuionado(
        guion=[Respuesta(texto="Anotado.")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )
    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["hola"], interno,
        escenario_id="b-test-sin-aclaracion", indice=0)
    assert r.etiquetas_aclaracion_ofrecidas == ()


# ---------------------------------------------------------------------------
# aclaracion_esperada reconoce `ofrecer_opciones` del modelo (T1, ADR 0007),
# no sólo la aclaración con botones de siempre (revisión del orquestador,
# T4, 2026-09-26): una corrida real (b-0013) donde el modelo resolvió una
# referencia ambigua ofreciendo las dos tareas con `ofrecer_opciones` -- el
# comportamiento correcto -- quedaba marcada `falla` en `aclaracion` porque
# el corredor nunca la tapeaba.
# ---------------------------------------------------------------------------


def test_ejecutar_escenario_opciones_modelo_ofrece_tareas_y_tapea_para_actualizar_estado(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {
            "tareas": [
                {"id": "t1", "titulo": "Actualizar el dashboard de HMI (simulado)",
                 "area": "ot", "responsable": "Marcos Tarquini"},
                {"id": "t2", "titulo": "Revisar gráficos del dashboard HMI (simulado)",
                 "area": "ot", "responsable": "Marcos Tarquini"},
            ],
        })
    tid_a, tid_b = ids["t1"], ids["t2"]

    interno = ProveedorGuionado(
        guion=[
            Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
                "pregunta": "¿Cuál de las dos tareas del dashboard paso a revisión?",
                "opciones": [{"tarea_id": tid_a}, {"tarea_id": tid_b}]})]),
            Respuesta(texto="Ya te mostré las opciones."),
            Respuesta(llamadas=[Llamada(
                       "c2", "actualizar_estado",
                       {"tarea_id": tid_a, "estado": "en_revision",
                        "evidencia_texto": "Ya lo arreglé."})]),
            Respuesta(texto="listo"),
        ],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini",
        ["ya arregle lo del dashboard, pasalo a revision"], interno,
        escenario_id="b-test-opciones-modelo-aclaracion", indice=0,
        aclaracion_esperada={
            "candidatas": ["Actualizar el dashboard de HMI (simulado)",
                          "Revisar gráficos del dashboard HMI (simulado)"],
            "elegir": "Actualizar el dashboard de HMI (simulado)"})

    assert r.bloqueado is False, r.motivo_bloqueo
    assert set(r.etiquetas_aclaracion_ofrecidas) == {
        "Actualizar el dashboard de HMI (simulado)",
        "Revisar gráficos del dashboard HMI (simulado)"}
    assert comprobar_aclaracion(
        r.etiquetas_aclaracion_ofrecidas,
        candidatas_esperadas=["Actualizar el dashboard de HMI (simulado)",
                              "Revisar gráficos del dashboard HMI (simulado)"],
    ).resultado == "aprobado"
    # El tap sobre la opción de tarea retomó la conversación con el modelo
    # (`gateway._resolver_toque_opcion_modelo`) y llegó a ejecutar la
    # herramienta esperada, con la vista previa de siempre confirmada sola.
    assert r.herramientas_ejecutadas == ["actualizar_estado"]
    assert r.herramientas_antes_del_toque == ()

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid_a,))
        assert cur.fetchone()["estado"] == "en_revision"


def test_ejecutar_escenario_opcion_de_texto_no_cuenta_como_tarea_ofrecida(
        corework, conn):
    """La otra mitad de la corrida real b-0013: el modelo ofreció una tarea
    por `tarea_id` (cuenta) y la otra por `texto` (no cuenta, aunque nombre
    la tarea) -- `comprobar_aclaracion` sigue marcando `falla` para la que
    sólo se nombró en texto, porque el servidor no puede resolverla como esa
    tarea."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {
            "tareas": [
                {"id": "t1", "titulo": "Actualizar el dashboard de HMI (simulado)",
                 "area": "ot", "responsable": "Marcos Tarquini"},
                {"id": "t2", "titulo": "Revisar gráficos del dashboard HMI (simulado)",
                 "area": "ot", "responsable": "Marcos Tarquini"},
            ],
        })
    tid_a = ids["t1"]

    interno = ProveedorGuionado(
        guion=[
            Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
                "pregunta": "¿Cuál de las dos tareas del dashboard paso a revisión?",
                "opciones": [
                    {"tarea_id": tid_a,
                     "etiqueta": "Actualizar el dashboard de HMI (simulado)"},
                    {"texto": "Revisar gráficos del dashboard HMI (simulado)"}]})]),
            Respuesta(texto="Ya te mostré las opciones."),
        ],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini",
        ["ya arregle lo del dashboard, pasalo a revision"], interno,
        escenario_id="b-test-opciones-modelo-texto-no-cuenta", indice=0,
        aclaracion_esperada={
            "candidatas": ["Actualizar el dashboard de HMI (simulado)",
                          "Revisar gráficos del dashboard HMI (simulado)"],
            "elegir": "Actualizar el dashboard de HMI (simulado)"})

    assert r.bloqueado is False, r.motivo_bloqueo
    assert r.etiquetas_aclaracion_ofrecidas == (
        "Actualizar el dashboard de HMI (simulado)",)
    resultado = comprobar_aclaracion(
        r.etiquetas_aclaracion_ofrecidas,
        candidatas_esperadas=["Actualizar el dashboard de HMI (simulado)",
                              "Revisar gráficos del dashboard HMI (simulado)"])
    assert resultado.resultado == "falla"
    assert "Revisar gráficos del dashboard HMI (simulado)" in resultado.diferencia


# ---------------------------------------------------------------------------
# _resolver_opcion_toque (T4, `prisma-orienta`): resuelve un toque genérico
# de escenario contra las opciones REALES de la propuesta vigente -- nunca
# inventa un token.
# ---------------------------------------------------------------------------


def test_resolver_opcion_toque_por_etiqueta_exacta():
    opciones = [{"token": "t1", "etiqueta": "Ver detalle"},
               {"token": "t2", "etiqueta": "Empezar"}]
    o = _resolver_opcion_toque(opciones, {"etiqueta": "Empezar"})
    assert o["token"] == "t2"


def test_resolver_opcion_toque_por_indice():
    opciones = [{"token": "t1", "etiqueta": "Ver detalle"},
               {"token": "t2", "etiqueta": "Empezar"}]
    o = _resolver_opcion_toque(opciones, {"indice": 1})
    assert o["token"] == "t2"


def test_resolver_opcion_toque_etiqueta_inexistente_es_none():
    opciones = [{"token": "t1", "etiqueta": "Ver detalle"}]
    assert _resolver_opcion_toque(opciones, {"etiqueta": "No existe"}) is None


def test_resolver_opcion_toque_indice_fuera_de_rango_es_none():
    opciones = [{"token": "t1", "etiqueta": "Ver detalle"}]
    assert _resolver_opcion_toque(opciones, {"indice": 5}) is None
    assert _resolver_opcion_toque([], {"indice": 0}) is None


# ---------------------------------------------------------------------------
# _resolver_toque_generico (T4, revisión del orquestador): un toque genérico
# de escenario se resuelve contra la UNIÓN de las opciones de TODAS las
# acciones pendientes 'esperando' de un chat -- nunca contra "la última"
# elegida por `creado_en`/`ctid` (ninguno de los dos desata un empate real
# entre filas creadas en la misma transacción; `ctid` tampoco es una
# garantía general de Postgres bajo escritura concurrente). A diferencia de
# `_pendiente_para_confirmar` (T1), que sólo encuentra una que ofrezca el
# botón Confirmar.
# ---------------------------------------------------------------------------


def test_resolver_toque_generico_encuentra_la_unica_esperando(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws)
        p = P.registrar(
            cur, quien, herramienta=P.SENTINEL_MENU_TAREA, args={},
            resumen="¿Qué querés hacer?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1),
            campo="eleccion", chat_id=tg,
            opciones=[("Ver detalle", {"accion": "ver_detalle"})])

        pid, opcion = _resolver_toque_generico(cur, ws, tg, {"etiqueta": "Ver detalle"}, _MUY_ANTES)

    assert pid == p.id
    assert opcion["etiqueta"] == "Ver detalle"


def test_resolver_toque_generico_sin_ninguna_pendiente_bloquea(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        _, tg = _quien(cur, ws)
        with pytest.raises(LookupError, match="no hay ninguna acción pendiente"):
            _resolver_toque_generico(cur, ws, tg, {"etiqueta": "Confirmar"}, _MUY_ANTES)


def test_resolver_toque_generico_sin_coincidencia_bloquea(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws)
        P.registrar(
            cur, quien, herramienta=P.SENTINEL_MENU_TAREA, args={},
            resumen="¿Qué querés hacer?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1),
            campo="eleccion", chat_id=tg,
            opciones=[("Ver detalle", {"accion": "ver_detalle"})])

        with pytest.raises(LookupError, match="no lo ofrece"):
            _resolver_toque_generico(cur, ws, tg, {"etiqueta": "No existe"}, _MUY_ANTES)


def test_resolver_toque_generico_ignora_una_pendiente_anterior_a_desde(corework, conn):
    """`desde` (esta unidad, hallazgo del orquestador): una acción pendiente
    que quedó esperando de un turno ANTERIOR (otra corrida del mismo
    escenario, u otro escenario que comparta chat) no cuenta -- ni para
    resolver el toque ni para armar ambigüedad."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws)
        P.registrar(
            cur, quien, herramienta=P.SENTINEL_MENU_TAREA, args={},
            resumen="¿Qué querés hacer (de otra corrida)?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1),
            campo="eleccion", chat_id=tg,
            opciones=[("Ver detalle", {"accion": "ver_detalle"})])

        cur.execute("select clock_timestamp() as ahora")
        desde = cur.fetchone()["ahora"]

        with pytest.raises(LookupError, match="no hay ninguna acción pendiente"):
            _resolver_toque_generico(cur, ws, tg, {"etiqueta": "Ver detalle"}, desde)


def test_resolver_toque_generico_dos_pendientes_de_esta_corrida_es_ambiguo(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws)
        P.registrar(
            cur, quien, herramienta=P.SENTINEL_MENU_TAREA, args={},
            resumen="¿Cuál, primera?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1),
            campo="eleccion", chat_id=tg,
            opciones=[("Confirmar", {"accion": "a"})])
        P.registrar(
            cur, quien, herramienta=P.SENTINEL_MENU_TAREA, args={},
            resumen="¿Cuál, segunda?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1),
            campo="eleccion", chat_id=tg,
            opciones=[("Confirmar", {"accion": "b"})])

        with pytest.raises(LookupError, match="ambiguo"):
            _resolver_toque_generico(cur, ws, tg, {"etiqueta": "Confirmar"}, _MUY_ANTES)


def test_resolver_toque_generico_tapea_la_correcta_sin_importar_el_orden_fisico(
        corework, conn):
    """Revisión del orquestador (T4, 2026-09-26, `corrida.py:467-471`): dos
    `pending_action` 'esperando' creadas en la MISMA transacción comparten
    `creado_en` (`now()` es constante dentro de una transacción), con
    etiquetas DISTINTAS -- se tapea la que corresponde por etiqueta, sin
    adivinar por orden físico de inserción."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws)
        primera = P.registrar(
            cur, quien, herramienta=P.SENTINEL_MENU_TAREA, args={},
            resumen="¿Cuál de las dos, primera?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1),
            campo="eleccion", chat_id=tg,
            opciones=[("Primera", {"accion": "a"})])
        segunda = P.registrar(
            cur, quien, herramienta=P.SENTINEL_MENU_TAREA, args={},
            resumen="¿Cuál de las dos, segunda?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1),
            campo="eleccion", chat_id=tg,
            opciones=[("Segunda", {"accion": "b"})])

        # Las dos comparten `creado_en`: son la misma transacción.
        cur.execute(
            "select count(distinct creado_en) n from pending_action "
            "where id in (%s, %s)", (primera.id, segunda.id))
        assert cur.fetchone()["n"] == 1

        pid1, opcion1 = _resolver_toque_generico(cur, ws, tg, {"etiqueta": "Primera"}, _MUY_ANTES)
        pid2, opcion2 = _resolver_toque_generico(cur, ws, tg, {"etiqueta": "Segunda"}, _MUY_ANTES)

    assert pid1 == primera.id and opcion1["etiqueta"] == "Primera"
    assert pid2 == segunda.id and opcion2["etiqueta"] == "Segunda"


def test_resolver_toque_generico_misma_etiqueta_en_dos_pendientes_bloquea(
        corework, conn):
    """Dos acciones pendientes DISTINTAS ofrecen la MISMA etiqueta: ambiguo,
    no se adivina cuál -- tiene que levantar, no elegir cualquiera de las
    dos al azar (la corrida queda `bloqueada`, con un motivo legible)."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws)
        P.registrar(
            cur, quien, herramienta=P.SENTINEL_MENU_TAREA, args={},
            resumen="¿Cuál de las dos, primera?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1),
            campo="eleccion", chat_id=tg,
            opciones=[("Confirmar", {"accion": "a"})])
        P.registrar(
            cur, quien, herramienta=P.SENTINEL_MENU_TAREA, args={},
            resumen="¿Cuál de las dos, segunda?",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=1),
            campo="eleccion", chat_id=tg,
            opciones=[("Confirmar", {"accion": "b"})])

        with pytest.raises(LookupError, match="ambiguo"):
            _resolver_toque_generico(cur, ws, tg, {"etiqueta": "Confirmar"}, _MUY_ANTES)


# ---------------------------------------------------------------------------
# _candidatas_tarea_por_titulo (T1/T4, revisión del orquestador): las
# opciones de tarea de una aclaración por `ofrecer_opciones`, por título --
# una opción sin título no cuenta, no rompe la corrida.
# ---------------------------------------------------------------------------


def test_candidatas_tarea_por_titulo_ignora_una_opcion_sin_titulo():
    opciones = [
        {"token": "t1", "etiqueta": "Programar PLC",
         "valor": {"tipo": "tarea", "tarea_id": "id-1", "titulo": "Programar PLC"}},
        {"token": "t2", "etiqueta": "Revisar comunicaciones",
         "valor": {"tipo": "tarea", "tarea_id": "id-2"}},   # sin "titulo"
        {"token": "t3", "etiqueta": "Otra cosa", "valor": {"tipo": "texto", "texto": "Otra cosa"}},
    ]
    assert _candidatas_tarea_por_titulo(opciones) == [("Programar PLC", "t1")]


# ---------------------------------------------------------------------------
# ejecutar_escenario con `toques` (T4, `prisma-orienta`): simula, en orden,
# tocar una tarea de la lista (T3) y después una acción de su menú (T2) --
# extremo a extremo, hasta la vista previa y su Confirmar automático de
# siempre -- sin que nada de lo que las 8 herramientas escriben cambie antes
# de ese Confirmar.
# ---------------------------------------------------------------------------


def test_ejecutar_escenario_toques_lista_tarea_menu_accion_llega_a_la_vista_previa(
        corework, conn):
    """`evidencia_requerida: []` (ADR 0009): "Ya la terminé" ahora pide la
    evidencia antes de la vista previa cuando la política la exige, y el
    corredor no tiene un tipo de paso para responder ese pedido con texto
    libre entre dos toques -- `toques` sólo resuelve botones
    (`_resolver_toque_generico`). Esta tarea no la exige a propósito, para
    seguir cubriendo lo que el escenario prueba de verdad: que un toque
    genérico llega hasta el Confirmar automático de siempre. Extender el
    corredor con un paso de texto libre intercalado queda **pendiente**,
    fuera del alcance de esta unidad."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {
            "tareas": [{"id": "t1", "titulo": "Programar PLC (simulado)",
                       "area": "ot", "responsable": "Marcos Tarquini",
                       "evidencia_requerida": []}],
        })
    tid = ids["t1"]

    interno = ProveedorGuionado(
        guion=[
            Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
            Respuesta(texto="Tenés una tarea pendiente."),
        ],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["pasame mis tareas"], interno,
        escenario_id="b-test-toques", indice=0,
        toques=[{"indice": 0}, {"etiqueta": "Ya la terminé"}])

    assert r.bloqueado is False, r.motivo_bloqueo
    # `consultar_tareas` (el turno del modelo) corrió antes de cualquier
    # toque; `actualizar_estado` (la acción del menú) recién al Confirmar
    # automático de siempre -- ninguna de las dos antes de ese toque salvo la
    # de consulta, que no escribe nada (no está en `_HERRAMIENTAS_QUE_
    # ESCRIBEN`, ver `comprobadores.py`).
    assert r.herramientas_antes_del_toque == ("consultar_tareas",)
    assert r.herramientas_ejecutadas == ["consultar_tareas", "actualizar_estado"]
    assert r.conteos_antes_del_toque is not None
    for tabla in ("task", "blocker", "dependency", "task_state_event",
                 "objective", "evidence", "approval"):
        assert r.conteos_antes_del_toque[tabla] == r.conteos_antes[tabla], (
            f"'{tabla}' cambió antes de tocar Confirmar")

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"


def test_ejecutar_escenario_toque_con_etiqueta_no_ofrecida_queda_bloqueado(
        corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        sembrar_precondiciones(cur, ws, {
            "tareas": [{"id": "t1", "titulo": "Programar PLC (simulado)",
                       "area": "ot", "responsable": "Marcos Tarquini"}],
        })

    interno = ProveedorGuionado(
        guion=[
            Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
            Respuesta(texto="Tenés una tarea pendiente."),
        ],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["pasame mis tareas"], interno,
        escenario_id="b-test-toque-invalido", indice=0,
        toques=[{"etiqueta": "Un botón que no existe"}])

    assert r.bloqueado is True
    assert "no lo ofrece" in r.motivo_bloqueo


def test_ejecutar_escenario_toque_sin_ninguna_pendiente_queda_bloqueado(corework, conn):
    interno = ProveedorGuionado(
        guion=[Respuesta(texto="Anotado.")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )

    r = ejecutar_escenario(
        conn, corework.workspace_id, "corework", "Marcos Tarquini", ["hola"], interno,
        escenario_id="b-test-toque-sin-pendiente", indice=0,
        toques=[{"indice": 0}])

    assert r.bloqueado is True
    assert "no hay ninguna acción pendiente" in r.motivo_bloqueo
