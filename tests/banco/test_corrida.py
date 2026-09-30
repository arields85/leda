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
from prisma.llm import (IntentAction, IntentRoute, Llamada, ProveedorGuionado,
                         RespectoPendiente, Respuesta)

from tests.banco.comprobadores import comprobar_aclaracion
from tests.test_aclaracion_botones import con_credencial  # noqa: F401
from tests.banco import corrida as corrida_modulo
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


def test_grabador_conserva_la_ruta_que_fallo_y_su_error():
    """El ruteo que falla también queda en la grabación (banco b-0022: un
    `RoutingError` 3/3 sin ninguna huella de qué ruta lo causó): la entrada,
    la pregunta pendiente y el error, y la excepción sigue su camino."""
    from prisma.llm import RouteEnvelope, RoutingError

    sobre_malo = RouteEnvelope(calls=(Llamada("c", "route_intent", {
        "action": "normal_conversation"}),))   # falta `respecto_pendiente`
    interno = ProveedorGuionado(guion=[], rutas=[sobre_malo])
    g = ProveedorGrabador(interno)

    with pytest.raises(RoutingError):
        g.route_intent("objetivo simulado", pendiente="¿Cuál es el objetivo?")

    assert len(g.rutas) == 1
    registro = g.rutas[0]
    assert registro["entrada"] == "objetivo simulado"
    assert registro["pendiente"] == "¿Cuál es el objetivo?"
    assert registro["error"].startswith("RoutingError: ")
    assert "respecto_pendiente" in registro["error"]
    assert "salida" not in registro and registro["latencia_s"] >= 0


def test_replay_de_una_ruta_fallida_vuelve_a_fallar_en_su_lugar():
    """Una grabación con un intento fallido y su reintento exitoso se
    reproduce en el mismo orden: falla y después responde."""
    import json

    from prisma.llm import RoutingError

    grabacion = json.loads(json.dumps({"rutas": [
        {"entrada": "x", "error": "RoutingError: Malformed router payload.",
         "latencia_s": 0.1},
        {"entrada": "x", "salida": {"action": "normal_conversation",
                                    "task": {}}, "latencia_s": 0.1}],
        "respuestas": []}))

    guionado = guionado_desde_grabacion(grabacion)

    with pytest.raises(RoutingError):
        guionado.route_intent("x")
    assert guionado.route_intent("x").action is IntentAction.NORMAL_CONVERSATION


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
    assert ruta.respecto_pendiente is None


def test_grabador_pasa_y_graba_la_pregunta_pendiente_y_su_comando():
    """T9-R1a: con una pregunta pendiente el grabador la pasa al proveedor
    interno, la anota junto a la entrada y redondea el comando devuelto."""
    interno = ProveedorGuionado(guion=[], rutas=[IntentRoute(
        IntentAction.NORMAL_CONVERSATION,
        respecto_pendiente=RespectoPendiente.CHARLA)])
    g = ProveedorGrabador(interno)

    ruta = g.route_intent("hola", pendiente="la evidencia de «X»")

    assert ruta.respecto_pendiente is RespectoPendiente.CHARLA
    assert interno.pendientes == ["la evidencia de «X»"]
    import json
    grabacion = json.loads(json.dumps(g.a_json()))
    assert grabacion["rutas"][0]["pendiente"] == "la evidencia de «X»"
    assert grabacion["rutas"][0]["salida"]["respecto_pendiente"] == "charla"

    guionado = guionado_desde_grabacion(grabacion)
    assert guionado.route_intent(
        "cualquier cosa", pendiente="p").respecto_pendiente is (
            RespectoPendiente.CHARLA)


def test_grabador_sin_pendiente_no_agrega_claves_nuevas():
    interno = ProveedorGuionado(guion=[], rutas=[
        IntentRoute(IntentAction.NORMAL_CONVERSATION)])
    g = ProveedorGrabador(interno)

    g.route_intent("hola")

    assert "pendiente" not in g.rutas[0]
    assert "respecto_pendiente" not in g.rutas[0]["salida"]
    assert interno.pendientes == [None]


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


def test_ejecutar_escenario_aclaracion_elige_por_el_titulo_entero_aunque_el_boton_lo_acorte(
        corework, conn):
    """T10-2b (b-0013): el escenario nombra la candidata por su título entero, pero el
    botón real lo lleva acortado ("Cablear tablero máq. 3…"). Sin reconocer la forma
    ofrecida del título el corredor no encontraba el botón, no tocaba nada y la corrida
    parecía un pedido que Prisma no retomó."""
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
    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini",
        ["ya termine lo del tablero, pasala a revision"], interno,
        escenario_id="b-test-aclaracion-titulo", indice=0, cliente_jev=doble_jev,
        aclaracion_esperada={
            "candidatas": ["Cablear tablero máq. 3 (simulado)",
                           "Revisar tablero máq. 4 (simulado)"],
            "elegir": "Cablear tablero máq. 3 (simulado)"})

    assert r.bloqueado is False, r.motivo_bloqueo
    assert r.herramientas_ejecutadas == ["actualizar_estado"]
    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid_a,))
        assert cur.fetchone()["estado"] == "en_revision"


def test_ejecutar_escenario_aclaracion_con_dos_botones_que_cumplen_no_adivina_cual(
        corework, conn, monkeypatch):
    """T10-2c: si dos botones de la misma pregunta cumplen la etiqueta a elegir, el
    corredor no toca ninguno: la corrida queda bloqueada con el motivo "ambiguo" y
    no se aplica nada (antes tomaba el primero, y un toque equivocado pasaba por
    conducta de Prisma). Los botones reales llevan etiquetas distinguibles entre sí,
    así que la ambigüedad se fuerza repitiendo la primera opción de la pregunta."""
    original = corrida_modulo._opciones_pendiente

    def opciones_con_una_repetida(cur, pendiente_id):
        opciones = original(cur, pendiente_id)
        return [*opciones, opciones[0]] if opciones else opciones

    monkeypatch.setattr(corrida_modulo, "_opciones_pendiente",
                        opciones_con_una_repetida)
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
    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini",
        ["ya termine lo del tablero, pasala a revision"], interno,
        escenario_id="b-test-aclaracion-ambigua", indice=0, cliente_jev=doble_jev,
        aclaracion_esperada={
            "candidatas": ["Cablear tablero máq. 3 (simulado)",
                           "Revisar tablero máq. 4 (simulado)"],
            "elegir": "Cablear tablero máq. 3 (simulado)"})

    assert r.bloqueado is True
    assert "ambiguo" in r.motivo_bloqueo
    assert r.herramientas_ejecutadas == []
    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid_a,))
        assert cur.fetchone()["estado"] != "en_revision"


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
            # (Sin respuesta de cierre: `ofrecer_opciones` cierra el turno sin
            # otra llamada al modelo, T8c-1.)
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


# ---------------------------------------------------------------------------
# ejecutar_escenario con `mensajes_tras_toques` (T9-R1a-2): el corredor puede
# contestar, con texto libre, la pregunta que abrió un toque. La respuesta
# visible que se evalúa es la de esos mensajes (y la del Confirmar que siga),
# no la de la pregunta que ya estaba abierta.
# ---------------------------------------------------------------------------


def _sembrar_evidencia_pedida(conn, ws) -> str:
    with admin(conn) as cur:
        return sembrar_precondiciones(cur, ws, {
            "tareas": [{"id": "t1", "titulo": "Programar PLC (simulado)",
                       "area": "ot", "responsable": "Marcos Tarquini"}],
        })["t1"]


def _interno_con_pregunta_abierta(rutas_pendiente):
    return ProveedorGuionado(
        guion=[
            Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
            Respuesta(texto="Tenés una tarea pendiente."),
        ],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION), *rutas_pendiente],
    )


def test_ejecutar_escenario_mensaje_tras_toques_un_saludo_no_es_la_evidencia(
        corework, conn):
    ws = corework.workspace_id
    tid = _sembrar_evidencia_pedida(conn, ws)
    interno = _interno_con_pregunta_abierta([
        IntentRoute(IntentAction.NORMAL_CONVERSATION,
                    respecto_pendiente=RespectoPendiente.CHARLA)])

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["pasame mis tareas"], interno,
        escenario_id="b-test-tras-toques", indice=0,
        toques=[{"indice": 0}, {"etiqueta": "Ya la terminé"}],
        mensajes_tras_toques=["hola"])

    assert r.bloqueado is False, r.motivo_bloqueo
    # Sólo la respuesta al saludo: ni la lista ni la primera pregunta.
    assert "Tenés una tarea pendiente." not in r.respuesta_texto
    assert r.respuesta_texto.count("pasame un link") == 1
    assert r.conteos_antes_del_toque is None          # ninguna vista previa
    assert r.conteos_despues["evidence"] == r.conteos_antes["evidence"]
    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"


def test_ejecutar_escenario_mensaje_tras_toques_un_link_llega_a_la_vista_previa(
        corework, conn):
    ws = corework.workspace_id
    tid = _sembrar_evidencia_pedida(conn, ws)
    interno = _interno_con_pregunta_abierta([
        IntentRoute(IntentAction.NORMAL_CONVERSATION,
                    respecto_pendiente=RespectoPendiente.RESPONDE)])

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["pasame mis tareas"], interno,
        escenario_id="b-test-tras-toques-link", indice=0,
        toques=[{"indice": 0}, {"etiqueta": "Ya la terminé"}],
        mensajes_tras_toques=["https://ejemplo.com/pr/12"])

    assert r.bloqueado is False, r.motivo_bloqueo
    assert "https://ejemplo.com/pr/12" in r.respuesta_texto
    # Nada se aplicó antes del Confirmar automático.
    assert r.herramientas_antes_del_toque == ("consultar_tareas",)
    assert r.conteos_antes_del_toque is not None
    assert r.conteos_antes_del_toque["evidence"] == r.conteos_antes["evidence"]
    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"


def test_ejecutar_escenario_da_a_cada_mensaje_un_id_de_telegram_distinto(
        corework, conn):
    # Seguimiento de review-dd7cd3c9cb7e8575: todos los mensajes de
    # `mensajes_tras_toques` salían con el mismo `message_id` (1), cosa que
    # Telegram nunca hace y que un dedupe por id dejaría como un solo mensaje.
    ws = corework.workspace_id
    _sembrar_evidencia_pedida(conn, ws)
    interno = _interno_con_pregunta_abierta([
        IntentRoute(IntentAction.NORMAL_CONVERSATION,
                    respecto_pendiente=RespectoPendiente.CHARLA),
        IntentRoute(IntentAction.NORMAL_CONVERSATION,
                    respecto_pendiente=RespectoPendiente.CHARLA)])

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["pasame mis tareas"], interno,
        escenario_id="b-test-ids-unicos", indice=0,
        toques=[{"indice": 0}, {"etiqueta": "Ya la terminé"}],
        mensajes_tras_toques=["hola", "gracias"])

    assert r.bloqueado is False, r.motivo_bloqueo
    with admin(conn) as cur:
        cur.execute(
            """select telegram_message_id from inbound_message
                where workspace_id = %s and texto is not null
                order by at""", (ws,))       # los toques dejan una fila sin texto
        ids = [f["telegram_message_id"] for f in cur.fetchall()]
    assert len(ids) == 3
    assert len(set(ids)) == 3


def test_ejecutar_escenario_modificar_tocado_un_saludo_no_es_la_correccion(
        corework, conn):
    # La mecánica de la familia b-0020 (banco real): el corredor toca
    # "Modificar" en la vista previa que dejó el primer mensaje y el mensaje
    # siguiente se interpreta contra "¿Qué querés cambiar?" -- un saludo no la
    # consume ni deja efectos.
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {
            "tareas": [{"id": "t1", "titulo": "Cablear tablero (simulado)",
                       "area": "ot", "responsable": "Nahuel Gimenez"}]})
    interno = ProveedorGuionado(
        guion=[Respuesta(llamadas=[Llamada("c1", "registrar_bloqueo", {
                   "tarea_id": ids["t1"], "causa": "falta el plano"})]),
               Respuesta(texto="Listo, te lo dejo para confirmar.")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION),
               IntentRoute(IntentAction.NORMAL_CONVERSATION,
                           respecto_pendiente=RespectoPendiente.CHARLA)])

    r = ejecutar_escenario(
        conn, ws, "corework", "Nahuel Gimenez", ["quedé trabado con el cableado"],
        interno, escenario_id="b-test-modificar-saludo", indice=0,
        toques=[{"etiqueta": "Modificar"}], mensajes_tras_toques=["hola"])

    assert r.bloqueado is False, r.motivo_bloqueo
    assert "cambiar" in r.respuesta_texto.lower()        # se vuelve a preguntar
    assert r.conteos_antes_del_toque is None             # ninguna vista previa nueva
    assert r.herramientas_ejecutadas == []               # nada se aplicó
    assert r.conteos_despues["blocker"] == r.conteos_antes["blocker"]


# ---------------------------------------------------------------------------
# La familia del alta guiada (T9-R1c-1, ADR 0013 regla 1): el corredor tiene
# que poder llegar a la pregunta de texto libre del alta -- tocando las
# opciones del alta, que no son filas de `pending_action` -- y mandar los
# mensajes como los de un chat privado, como Telegram.
# ---------------------------------------------------------------------------


def _interno_con_alta(rutas_pendiente):
    return ProveedorGuionado(
        guion=[],
        rutas=[IntentRoute(IntentAction.START_TASK_INTAKE), *rutas_pendiente])


def _sembrar_objetivo_para_el_alta(conn, ws):
    with admin(conn) as cur:
        sembrar_precondiciones(cur, ws, {
            "tareas": [{"id": "t1", "titulo": "Cablear tablero (simulado)",
                        "area": "ot", "responsable": "Marcos Tarquini"}]})


def test_resolver_toque_generico_alcanza_las_opciones_del_alta(corework, conn):
    from prisma import ingreso_tareas as I

    ws = corework.workspace_id
    _sembrar_objetivo_para_el_alta(conn, ws)
    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws)
        cur.execute(
            """insert into inbound_message
                 (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
               values (%s, 1, %s, %s, 'armame una tarea') returning id""",
            (ws, tg, quien.app_user_id))
        I.start(cur, quien, chat_id=tg, source_inbound_id=str(cur.fetchone()["id"]),
                source_raw_text="armame una tarea", proposals={},
                now=datetime.now(timezone.utc), buttons_first=True)

        origen, opcion = _resolver_toque_generico(cur, ws, tg, {"indice": 0},
                                                  _MUY_ANTES)

    assert opcion["token"]
    assert opcion["prefijo"] == I.CALLBACK_PREFIX
    assert opcion["etiqueta"]                       # el objetivo sembrado


def test_ejecutar_escenario_llega_a_la_pregunta_del_alta_y_la_interpreta(
        corework, conn):
    ws = corework.workspace_id
    _sembrar_objetivo_para_el_alta(conn, ws)
    interno = _interno_con_alta([
        IntentRoute(IntentAction.NORMAL_CONVERSATION,
                    respecto_pendiente=RespectoPendiente.CHARLA)])

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["armame una tarea nueva"],
        interno, escenario_id="b-test-alta", indice=0,
        toques=[{"indice": 0}], mensajes_tras_toques=["hola"])

    assert r.bloqueado is False, r.motivo_bloqueo
    # El mensaje llegó a la pregunta abierta del alta y no se tomó como título.
    assert "título" in r.respuesta_texto
    assert r.respuesta_texto.count("Escribí el título") == 1
    assert len(interno.pendientes) == 2 and "título" in interno.pendientes[1]
    with admin(conn) as cur:
        cur.execute("""select estado from task_intake_field
                        where campo = 'title'""")
        assert cur.fetchone()["estado"] == "missing"


# ---------------------------------------------------------------------------
# La familia b-0022 (T9-R1c-2, ADR 0013 regla 1): con una elección del alta o
# el borrador esperando confirmación, el mensaje se interpreta. El corredor
# tiene que poder llegar a los dos estados: la elección del objetivo queda
# abierta apenas empieza el alta; el borrador, tocando cada paso.
# ---------------------------------------------------------------------------

_TITULO_OBJETIVO_ALTA = "Objetivo simulado de Cablear tablero (simulado)"

_TOQUES_HASTA_EL_BORRADOR = [
    {"indice": 0},                  # el objetivo (la única candidata)
    {"etiqueta": "Sí"},             # el título propuesto
    {"indice": 0},                  # la persona responsable
    {"indice": 0},                  # el área
    {"etiqueta": "Sí"},             # la fecha objetivo propuesta
    {"etiqueta": "Sí"},             # el criterio de aceptación propuesto
]


def _interno_con_borrador(comando):
    """El alta con todos los datos propuestos en el primer mensaje (así sólo
    pide confirmar cada uno con botones) y después un mensaje interpretado
    con el comando dado."""
    return ProveedorGuionado(guion=[], rutas=[
        IntentRoute(IntentAction.START_TASK_INTAKE, {
            "title": "Cablear tablero norte", "objective": "Cablear tablero",
            "responsible": "Marcos", "area": "OT", "due_date": "2030-12-30",
            "acceptance_criterion": "Prueba firmada"}),
        IntentRoute(IntentAction.NORMAL_CONVERSATION,
                    respecto_pendiente=comando)])


def test_ejecutar_escenario_escribir_la_opcion_de_la_eleccion_abierta_del_alta(
        corework, conn):
    ws = corework.workspace_id
    _sembrar_objetivo_para_el_alta(conn, ws)
    interno = _interno_con_alta([
        IntentRoute(IntentAction.NORMAL_CONVERSATION,
                    respecto_pendiente=RespectoPendiente.RESPONDE)])

    # Sin ningún toque: la elección del objetivo ya está abierta.
    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["armame una tarea nueva"],
        interno, escenario_id="b-test-eleccion", indice=0,
        mensajes_tras_toques=[_TITULO_OBJETIVO_ALTA])

    assert r.bloqueado is False, r.motivo_bloqueo
    assert "Escribí el título" in r.respuesta_texto       # el alta siguió
    assert len(interno.pendientes) == 2 and "elección" in interno.pendientes[1]
    with admin(conn) as cur:
        cur.execute("""select estado from task_intake_field
                        where campo = 'objective'""")
        assert cur.fetchone()["estado"] == "confirmed"


@pytest.mark.parametrize(("comando", "texto", "estado", "dice"), [
    (RespectoPendiente.RESPONDE, "sí, dale", "active", "esperando confirmación"),
    (RespectoPendiente.CORRIGE, "cambiale la fecha", "active",
     "Qué dato querés cambiar"),
    (RespectoPendiente.CANCELA, "no, cancelalo", "cancelled", "dejé de lado"),
])
def test_ejecutar_escenario_llega_al_borrador_esperando_y_lo_interpreta(
        comando, texto, estado, dice, corework, conn):
    ws = corework.workspace_id
    _sembrar_objetivo_para_el_alta(conn, ws)

    # Quien escribe es quien confirma (Ismael aprueba lo de Marcos): sólo
    # entonces el borrador esperando es una pregunta abierta suya (ADR 0013
    # regla 1, enmienda: una rama está abierta para quien debe responderla).
    r = ejecutar_escenario(
        conn, ws, "corework", "Ismael Soschinski", ["armame una tarea nueva"],
        _interno_con_borrador(comando), escenario_id="b-test-borrador",
        indice=0, toques=_TOQUES_HASTA_EL_BORRADOR, mensajes_tras_toques=[texto])

    assert r.bloqueado is False, r.motivo_bloqueo
    assert dice in r.respuesta_texto
    # Ningún mensaje convierte el borrador: no hay tarea nueva.
    assert r.conteos_despues["task"] == r.conteos_antes["task"]
    with admin(conn) as cur:
        cur.execute("select estado from task_intake_request")
        assert cur.fetchone()["estado"] == estado


# ---------------------------------------------------------------------------
# Precondición `borrador_de_alta` (T9-R1c-2b): el borrador del alta ya
# esperando confirmación, sembrado en la base con las mismas filas que crea el
# alta real -- en vez de recorrerla con el modelo (armar todo de un mensaje) y
# seis toques que dependen de encontrar sus botones.
# ---------------------------------------------------------------------------

# Quien escribe es quien confirma: Ismael aprueba lo de Marcos.
_BORRADOR_DE_ALTA = {
    "solicitante": "Ismael Soschinski", "titulo": "Cablear tablero norte",
    "objetivo": _TITULO_OBJETIVO_ALTA, "responsable": "Marcos Tarquini",
    "area": "ot", "fecha_objetivo": "2030-12-30",
    "criterio_aceptacion": "Prueba firmada"}


def _sembrar_borrador_de_alta(conn, ws, **cambios):
    with admin(conn) as cur:
        return sembrar_precondiciones(cur, ws, {
            "tareas": [{"id": "t1", "titulo": "Cablear tablero (simulado)",
                        "area": "ot", "responsable": "Marcos Tarquini"}],
            "borrador_de_alta": {**_BORRADOR_DE_ALTA, **cambios}})


def test_sembrar_borrador_de_alta_deja_la_vista_previa_esperando(corework, conn):
    from prisma import ingreso_tareas as I

    ws = corework.workspace_id
    _sembrar_borrador_de_alta(conn, ws)

    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws, "Ismael Soschinski")
        pregunta = I.open_intake_question(cur, quien, tg)
        assert pregunta["tipo"] == I.QUESTION_CONFIRMATION
        assert pregunta["titulo"] == "Cablear tablero norte"
        cur.execute("select estado, chat_id from task_intake_request")
        solicitud = cur.fetchone()
        assert solicitud["estado"] == "active" and solicitud["chat_id"] == tg
        cur.execute(
            """select o.pending_action_id, o.cuerpo, o.chat_id,
                      (select count(*) from pending_action_option po
                        where po.pending_action_id = o.pending_action_id) botones
                 from message_outbox o where o.pending_action_id = %s""",
            (pregunta["id"],))
        salida = cur.fetchone()
        cur.execute("select count(*) n from task where titulo = %s",
                    ("Cablear tablero norte",))
        tareas = cur.fetchone()["n"]
    assert "Cablear tablero norte" in salida["cuerpo"]
    assert salida["botones"] == 3            # Confirmar, Modificar y Cancelar
    assert tareas == 0                               # el borrador no es una tarea


# Quien escribe (Marcos) no es quien confirma lo suyo (Ismael): T9-R1c-4.
_BORRADOR_DE_OTRO_APROBADOR = {**_BORRADOR_DE_ALTA, "solicitante": "Marcos Tarquini"}


def _acciones_del_borrador(conn) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(
            """select p.estado, p.chat_id, p.herramienta,
                      array(select etiqueta from pending_action_option o
                             where o.pending_action_id = p.id order by o.orden) botones
                 from pending_action p where p.draft_id is not null
                order by p.creado_en, p.id""")
        return cur.fetchall()


def test_sembrar_borrador_de_otro_aprobador_deja_el_resumen_de_quien_pide_esperando(
        corework, conn):
    from prisma import ingreso_tareas as I
    from prisma.salida import etiqueta_sin_icono

    ws = corework.workspace_id
    _sembrar_borrador_de_alta(conn, ws, **_BORRADOR_DE_OTRO_APROBADOR)

    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws, "Marcos Tarquini")
        pregunta = I.open_intake_question(cur, quien, tg)
        _, tg_ismael = _quien(cur, ws, "Ismael Soschinski")
        cur.execute("select count(*) n from message_outbox where chat_id = %s",
                    (tg_ismael,))
        al_aprobador = cur.fetchone()["n"]
    assert pregunta["tipo"] == I.QUESTION_CONFIRMATION and pregunta["revision"]
    (accion,) = _acciones_del_borrador(conn)
    assert accion["estado"] == "esperando" and accion["chat_id"] == tg
    assert [etiqueta_sin_icono(e) for e in accion["botones"]] == [
        "Enviar a aprobación", "Modificar", "Cancelar"]
    assert al_aprobador == 0                     # todavía no le llega nada


def test_sembrar_borrador_enviado_a_aprobacion_lo_deja_esperando_a_quien_confirma(
        corework, conn):
    from prisma import ingreso_tareas as I
    from prisma.salida import etiqueta_sin_icono

    ws = corework.workspace_id
    _sembrar_borrador_de_alta(conn, ws, **_BORRADOR_DE_OTRO_APROBADOR,
                              enviado_a_aprobacion=True)

    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws, "Marcos Tarquini")
        assert I.open_intake_question(cur, quien, tg) is None   # ya no es su rama
        _, tg_ismael = _quien(cur, ws, "Ismael Soschinski")
    # Las dos filas se crean en la misma transacción: se distinguen por su herramienta.
    por_herramienta = {a["herramienta"]: a for a in _acciones_del_borrador(conn)}
    revision = por_herramienta["revisar_borrador_tarea"]
    confirmacion = por_herramienta["confirmar_borrador_tarea"]
    assert revision["estado"] == "cancelada"
    assert confirmacion["estado"] == "esperando"
    assert confirmacion["chat_id"] == tg_ismael
    assert [etiqueta_sin_icono(e) for e in confirmacion["botones"]] == [
        "Confirmar", "Cancelar"]


def test_sembrar_borrador_enviado_a_aprobacion_por_quien_lo_confirma_falla(
        corework, conn):
    ws = corework.workspace_id

    with pytest.raises(LookupError, match="enviado_a_aprobacion"):
        _sembrar_borrador_de_alta(conn, ws, enviado_a_aprobacion=True)


def test_sembrar_borrador_de_alta_sin_un_dato_falla_nombrandolo(corework, conn):
    ws = corework.workspace_id
    borrador = {k: v for k, v in _BORRADOR_DE_ALTA.items() if k != "area"}

    with admin(conn) as cur, pytest.raises(LookupError, match="area"):
        sembrar_precondiciones(cur, ws, {"borrador_de_alta": borrador})


def test_sembrar_borrador_de_alta_con_un_objetivo_inexistente_falla(corework, conn):
    ws = corework.workspace_id

    with pytest.raises(LookupError, match="Objetivo que no existe"):
        _sembrar_borrador_de_alta(conn, ws, objetivo="Objetivo que no existe")


def test_ejecutar_escenario_sobre_el_borrador_sembrado_no_lo_convierte(
        corework, conn):
    ws = corework.workspace_id
    _sembrar_borrador_de_alta(conn, ws)
    interno = ProveedorGuionado(guion=[], rutas=[
        IntentRoute(IntentAction.NORMAL_CONVERSATION,
                    respecto_pendiente=RespectoPendiente.RESPONDE)])

    r = ejecutar_escenario(
        conn, ws, "corework", "Ismael Soschinski", [], interno,
        escenario_id="b-test-sembrado", indice=0,
        mensajes_tras_toques=["sí, dale"])

    assert r.bloqueado is False, r.motivo_bloqueo
    # Ismael es quien confirma: el mensaje no convierte el borrador y la
    # respuesta dice cómo se confirma.
    assert "esperando confirmación" in r.respuesta_texto
    assert len(interno.pendientes) == 1 and "borrador" in interno.pendientes[0]
    # Lo sembrado no cuenta como respuesta ni se confirma solo.
    assert r.conteos_antes_del_toque is None
    assert r.conteos_despues["task"] == r.conteos_antes["task"]
    with admin(conn) as cur:
        cur.execute("select estado from task_intake_request")
        assert cur.fetchone()["estado"] == "active"


# ---------------------------------------------------------------------------
# `toques_tras_mensajes` (T9-R1d, ADR 0013 regla 1, enmienda): tocar la
# pregunta de la rama que abrió un mensaje de `mensajes_tras_toques`. La
# respuesta que se evalúa es la de ese toque, no la pregunta que ya salió.
# ---------------------------------------------------------------------------


def _interno_con_otro_tema_y_su_respuesta():
    return ProveedorGuionado(
        guion=[Respuesta(texto="Tenés una tarea abierta.")],
        rutas=[IntentRoute(IntentAction.START_TASK_INTAKE),
               IntentRoute(IntentAction.NORMAL_CONVERSATION,
                           respecto_pendiente=RespectoPendiente.OTRO_TEMA),
               IntentRoute(IntentAction.NORMAL_CONVERSATION)])


def test_ejecutar_escenario_toca_dejar_despues_del_otro_tema_y_evalua_esa_respuesta(
        corework, conn):
    ws = corework.workspace_id
    _sembrar_objetivo_para_el_alta(conn, ws)
    interno = _interno_con_otro_tema_y_su_respuesta()

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["armame una tarea nueva"],
        interno, escenario_id="b-test-rama", indice=0, toques=[{"indice": 0}],
        mensajes_tras_toques=["¿qué tareas tengo abiertas?"],
        toques_tras_mensajes=[{"etiqueta": "Dejarlo y ver lo otro"}])

    assert r.bloqueado is False, r.motivo_bloqueo
    # Lo que se evalúa: lo que se dejó de lado y lo que se atendió. La pregunta
    # de la rama, que ya había salido, queda fuera.
    assert "dejé de lado" in r.respuesta_texto
    assert "Tenés una tarea abierta." in r.respuesta_texto
    assert "Estábamos con" not in r.respuesta_texto
    with admin(conn) as cur:
        cur.execute("select estado from task_intake_request")
        assert cur.fetchone()["estado"] == "cancelled"


def test_ejecutar_escenario_toca_seguir_y_evalua_la_pregunta_repetida(
        corework, conn):
    ws = corework.workspace_id
    _sembrar_objetivo_para_el_alta(conn, ws)
    interno = _interno_con_otro_tema_y_su_respuesta()

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["armame una tarea nueva"],
        interno, escenario_id="b-test-rama", indice=0, toques=[{"indice": 0}],
        mensajes_tras_toques=["¿qué tareas tengo abiertas?"],
        toques_tras_mensajes=[{"etiqueta": "Seguir con eso"}])

    assert r.bloqueado is False, r.motivo_bloqueo
    assert "Escribí el título" in r.respuesta_texto           # la pregunta pendiente
    assert "Estábamos con" not in r.respuesta_texto
    assert interno.recibidos == []                            # el otro tema no se atendió
    with admin(conn) as cur:
        cur.execute("select estado from task_intake_request")
        assert cur.fetchone()["estado"] == "active"


def test_ejecutar_escenario_con_un_toque_tras_mensajes_que_no_existe_queda_bloqueado(
        corework, conn):
    ws = corework.workspace_id
    _sembrar_objetivo_para_el_alta(conn, ws)

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["armame una tarea nueva"],
        _interno_con_otro_tema_y_su_respuesta(), escenario_id="b-test-rama",
        indice=0, toques=[{"indice": 0}],
        mensajes_tras_toques=["¿qué tareas tengo abiertas?"],
        toques_tras_mensajes=[{"etiqueta": "Un botón que no existe"}])

    assert r.bloqueado is True
    assert "no lo ofrece" in r.motivo_bloqueo


# ---------------------------------------------------------------------------
# La familia b-0023 (T9-R1d-1b, ADR 0013 regla 1, enmienda): con la vista
# previa de un cambio esperando su Confirmar (sin ningún toque), el mensaje
# siguiente se interpreta. El corredor tiene que llegar a ese estado con el
# primer mensaje, evaluar lo que pasa con el segundo y, si la vista previa
# sigue esperando, confirmarla sólo al final.
# ---------------------------------------------------------------------------


def _interno_con_vista_previa(comando, guion_extra=(), rutas_extra=()):
    """El primer mensaje deja la vista previa de un bloqueo (el turno termina
    ahí, sin otra vuelta del modelo); el segundo se interpreta con `comando`
    contra ella y, si llega al modelo, consume `guion_extra`."""
    return ProveedorGuionado(
        guion=[Respuesta(llamadas=[Llamada("c1", "registrar_bloqueo", {
                   "tarea_id": "PLACEHOLDER", "causa": "falta el plano"})]),
               *guion_extra],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION),
               IntentRoute(IntentAction.NORMAL_CONVERSATION,
                           respecto_pendiente=comando),
               *rutas_extra])


def _sembrar_bloqueo_pedido(conn, ws, interno) -> str:
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {
            "tareas": [{"id": "t1", "titulo": "Cablear tablero (simulado)",
                       "area": "ot", "responsable": "Nahuel Gimenez"}]})
    interno.guion[0].llamadas[0].args["tarea_id"] = ids["t1"]
    return ids["t1"]


def _correr_con_vista_previa(conn, ws, interno, texto, **kwargs):
    return ejecutar_escenario(
        conn, ws, "corework", "Nahuel Gimenez", ["quedé trabado con el cableado"],
        interno, escenario_id="b-test-vista-previa", indice=0,
        mensajes_tras_toques=[texto], **kwargs)


def test_ejecutar_escenario_si_dale_escrito_no_aplica_antes_de_confirmar(
        corework, conn):
    ws = corework.workspace_id
    interno = _interno_con_vista_previa(RespectoPendiente.RESPONDE)
    _sembrar_bloqueo_pedido(conn, ws, interno)

    r = _correr_con_vista_previa(conn, ws, interno, "sí, dale")

    assert r.bloqueado is False, r.motivo_bloqueo
    assert "botón Confirmar" in r.respuesta_texto
    # Antes del Confirmar del corredor no se había aplicado nada, y ese toque
    # sí aplica la vista previa original (siguió esperando).
    assert r.herramientas_antes_del_toque == ()
    assert r.conteos_antes_del_toque["blocker"] == r.conteos_antes["blocker"]
    assert r.conteos_despues["blocker"] == r.conteos_antes["blocker"] + 1


def test_ejecutar_escenario_cancelar_escrito_deja_sin_vista_previa_que_confirmar(
        corework, conn):
    ws = corework.workspace_id
    interno = _interno_con_vista_previa(RespectoPendiente.CANCELA)
    _sembrar_bloqueo_pedido(conn, ws, interno)

    r = _correr_con_vista_previa(conn, ws, interno, "no, mejor no")

    assert r.bloqueado is False, r.motivo_bloqueo
    assert "dejé de lado" in r.respuesta_texto
    assert r.conteos_antes_del_toque is None             # nada que confirmar
    assert r.herramientas_ejecutadas == []
    assert r.conteos_despues["blocker"] == r.conteos_antes["blocker"]


def test_ejecutar_escenario_correccion_escrita_llega_a_una_vista_previa_nueva(
        corework, conn):
    ws = corework.workspace_id
    interno = _interno_con_vista_previa(
        RespectoPendiente.CORRIGE, guion_extra=[
            Respuesta(llamadas=[Llamada("c2", "registrar_bloqueo", {
                "tarea_id": "PLACEHOLDER", "causa": "se rompió el variador"})])])
    tid = _sembrar_bloqueo_pedido(conn, ws, interno)
    interno.guion[1].llamadas[0].args["tarea_id"] = tid

    r = _correr_con_vista_previa(conn, ws, interno,
                                 "el motivo real es que se rompió el variador")

    assert r.bloqueado is False, r.motivo_bloqueo
    assert "variador" in r.respuesta_texto
    assert r.conteos_antes_del_toque["blocker"] == r.conteos_antes["blocker"]
    # Sólo la vista previa corregida se confirma: un único bloqueo.
    assert r.conteos_despues["blocker"] == r.conteos_antes["blocker"] + 1


def test_ejecutar_escenario_toca_dejar_con_la_vista_previa_esperando(
        corework, conn):
    ws = corework.workspace_id
    interno = _interno_con_vista_previa(
        RespectoPendiente.OTRO_TEMA,
        guion_extra=[Respuesta(texto="Tenés una tarea abierta.")],
        rutas_extra=[IntentRoute(IntentAction.NORMAL_CONVERSATION)])
    _sembrar_bloqueo_pedido(conn, ws, interno)

    r = _correr_con_vista_previa(
        conn, ws, interno, "¿qué tareas tengo abiertas?",
        toques_tras_mensajes=[{"etiqueta": "Dejarlo y ver lo otro"}])

    assert r.bloqueado is False, r.motivo_bloqueo
    assert "dejé de lado" in r.respuesta_texto
    assert "Tenés una tarea abierta." in r.respuesta_texto
    assert "Estábamos con" not in r.respuesta_texto
    assert r.conteos_antes_del_toque is None             # la vista previa se cerró
    assert r.conteos_despues["blocker"] == r.conteos_antes["blocker"]


def test_ejecutar_escenario_otro_tema_con_la_vista_previa_esperando_pregunta_por_la_rama(
        corework, conn):
    ws = corework.workspace_id
    interno = _interno_con_vista_previa(RespectoPendiente.OTRO_TEMA)
    _sembrar_bloqueo_pedido(conn, ws, interno)

    r = _correr_con_vista_previa(conn, ws, interno, "¿qué tareas tengo abiertas?")

    assert r.bloqueado is False, r.motivo_bloqueo
    assert "Estábamos con el cambio que te mostré" in r.respuesta_texto
    assert r.herramientas_antes_del_toque == ()          # el otro tema no se atendió
    # La vista previa original siguió esperando: el Confirmar del corredor la aplica.
    assert r.conteos_despues["blocker"] == r.conteos_antes["blocker"] + 1


# ---------------------------------------------------------------------------
# Preguntas sembradas (T9-R1d-1c): la vista previa de un cambio y la aclaración
# con botones ya esperando, sembradas por el corredor por el mismo camino real
# (`agente._encolar_confirmacion`, `gateway._preguntar_por_botones`) en vez de
# depender de que el modelo (y Jev) abran exactamente una cosa con el primer
# mensaje: banco real b-0023, donde una referencia ambigua abría la aclaración
# y no la vista previa. Se siembran DESPUÉS de marcar el arranque de la corrida,
# así el Confirmar automático del final todavía encuentra la vista previa.
# ---------------------------------------------------------------------------

_VISTA_PREVIA_SEMBRADA = {
    "herramienta": "registrar_bloqueo", "tarea": "Cablear tablero (simulado)",
    "args": {"causa": "falta el plano"}}
_ACLARACION_SEMBRADA = {
    "mensaje": "quedé trabado con el cableado", "referencia": "el cableado",
    "tareas": ["Cablear tablero (simulado)", "Revisar variador (simulado)"]}


def _sembrar_dos_tareas(conn, ws):
    with admin(conn) as cur:
        sembrar_precondiciones(cur, ws, {"tareas": [
            {"id": "t1", "titulo": "Cablear tablero (simulado)", "area": "ot",
             "responsable": "Nahuel Gimenez"},
            {"id": "t2", "titulo": "Revisar variador (simulado)", "area": "ot",
             "responsable": "Nahuel Gimenez"}]})


def _ruta_con(comando):
    return IntentRoute(IntentAction.NORMAL_CONVERSATION,
                       respecto_pendiente=comando)


def test_ejecutar_escenario_siembra_la_vista_previa_y_el_confirmar_final_la_aplica(
        corework, conn):
    ws = corework.workspace_id
    _sembrar_dos_tareas(conn, ws)
    interno = ProveedorGuionado(guion=[], rutas=[_ruta_con(RespectoPendiente.RESPONDE)])

    r = ejecutar_escenario(
        conn, ws, "corework", "Nahuel Gimenez", [], interno,
        escenario_id="b-test-sembrada", indice=0,
        mensajes_tras_toques=["sí, dale"],
        preguntas_sembradas={"vista_previa": _VISTA_PREVIA_SEMBRADA})

    assert r.bloqueado is False, r.motivo_bloqueo
    assert "botón Confirmar" in r.respuesta_texto            # sólo lo de ese mensaje
    assert interno.recibidos == []                            # el agente no habló
    # Nada se aplicó antes del Confirmar del corredor, y ese toque sí la aplica.
    assert r.herramientas_antes_del_toque == ()
    assert r.conteos_antes_del_toque["blocker"] == r.conteos_antes["blocker"]
    assert r.conteos_despues["blocker"] == r.conteos_antes["blocker"] + 1
    assert r.herramientas_ejecutadas == ["registrar_bloqueo"]


def test_ejecutar_escenario_con_una_vista_previa_sembrada_sobre_una_tarea_inexistente_queda_bloqueado(
        corework, conn):
    ws = corework.workspace_id
    _sembrar_dos_tareas(conn, ws)
    interno = ProveedorGuionado(guion=[], rutas=[])

    r = ejecutar_escenario(
        conn, ws, "corework", "Nahuel Gimenez", [], interno,
        escenario_id="b-test-sembrada", indice=0,
        mensajes_tras_toques=["sí, dale"],
        preguntas_sembradas={"vista_previa": {
            **_VISTA_PREVIA_SEMBRADA, "tarea": "Una tarea que no existe"}})

    assert r.bloqueado is True
    assert "Una tarea que no existe" in r.motivo_bloqueo


def test_ejecutar_escenario_con_una_aclaracion_sembrada_otro_tema_pregunta_por_la_rama(
        corework, conn):
    ws = corework.workspace_id
    _sembrar_dos_tareas(conn, ws)
    interno = ProveedorGuionado(guion=[], rutas=[_ruta_con(RespectoPendiente.OTRO_TEMA)])

    r = ejecutar_escenario(
        conn, ws, "corework", "Nahuel Gimenez", [], interno,
        escenario_id="b-test-sembrada", indice=0,
        mensajes_tras_toques=["¿qué tareas tengo abiertas?"],
        preguntas_sembradas={"aclaracion": _ACLARACION_SEMBRADA})

    assert r.bloqueado is False, r.motivo_bloqueo
    assert ("Estábamos con la tarea a la que te referías con «el cableado»"
            in r.respuesta_texto)
    assert "Revisar variador" not in r.respuesta_texto       # lo otro no se atendió
    assert interno.recibidos == []
    assert r.conteos_antes_del_toque is None                 # nada que confirmar
    assert r.conteos_despues["blocker"] == r.conteos_antes["blocker"]


def test_ejecutar_escenario_con_una_aclaracion_sembrada_toca_dejar_y_atiende_lo_otro(
        corework, conn):
    ws = corework.workspace_id
    _sembrar_dos_tareas(conn, ws)
    interno = ProveedorGuionado(
        guion=[Respuesta(texto="Tenés dos tareas abiertas: Revisar variador.")],
        rutas=[_ruta_con(RespectoPendiente.OTRO_TEMA),
               IntentRoute(IntentAction.NORMAL_CONVERSATION)])

    r = ejecutar_escenario(
        conn, ws, "corework", "Nahuel Gimenez", [], interno,
        escenario_id="b-test-sembrada", indice=0,
        mensajes_tras_toques=["¿qué tareas tengo abiertas?"],
        toques_tras_mensajes=[{"etiqueta": "Dejarlo y ver lo otro"}],
        preguntas_sembradas={"aclaracion": _ACLARACION_SEMBRADA})

    assert r.bloqueado is False, r.motivo_bloqueo
    assert "dejé de lado la aclaración" in r.respuesta_texto
    assert "Revisar variador" in r.respuesta_texto
    assert "Estábamos con" not in r.respuesta_texto


def test_ejecutar_escenario_sin_preguntas_sembradas_no_siembra_nada(corework, conn):
    ws = corework.workspace_id
    _sembrar_dos_tareas(conn, ws)
    interno = ProveedorGuionado(guion=[Respuesta(texto="Hola.")],
                                rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)])

    r = ejecutar_escenario(conn, ws, "corework", "Nahuel Gimenez", ["hola"], interno,
                           escenario_id="b-test-sin-sembrar", indice=0)

    assert r.bloqueado is False, r.motivo_bloqueo
    with admin(conn) as cur:
        cur.execute("select count(*) n from pending_action")
        assert cur.fetchone()["n"] == 0


def test_la_aclaracion_sembrada_es_la_misma_fila_que_crea_el_flujo_real(
        corework, conn, monkeypatch, con_credencial):
    """La siembra (`_sembrar_aclaracion`) no copia a mano el estado privado de
    `gateway._preguntar_por_botones` (review-faccc0e9d83561b3): la fila que deja
    esperando -- herramienta, pregunta, `campo`, `args`, botones con su orden,
    etiqueta y valor -- es la que crea el flujo real de un turno con una
    referencia ambigua, con tareas propias y ajenas."""
    from prisma import gateway
    from tests.banco.corrida import _sembrar_aclaracion
    from tests.test_aclaracion_botones import (_alcance, _con_jev, _con_proveedor,
                                               _quien, _tarea, _tarea_resp)

    ws = corework.workspace_id
    mensaje = "avisame de lo del tablero"
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Programar PLC", persona="Marcos Tarquini")
        _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Mariano Naim")
    conn.commit()
    _con_jev(monkeypatch, ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea_resp({"T1": 0.5, "T2": 0.3})}]))
    _con_proveedor(monkeypatch, rutas=[IntentRoute(
        IntentAction.NORMAL_CONVERSATION, trabajos=("lo del tablero",))])

    def _fila_esperando(cur) -> dict:
        cur.execute(
            """select id, herramienta, resumen, campo, args, chat_id
                 from pending_action
                where herramienta = %s and estado = 'esperando'""",
            (gateway._SENTINEL_ACLARACION,))
        (fila,) = cur.fetchall()
        cur.execute(
            """select etiqueta, valor from pending_action_option
                where pending_action_id = %s order by orden""", (fila["id"],))
        fila["opciones"] = [(o["etiqueta"], o["valor"]) for o in cur.fetchall()]
        del fila["id"]
        return fila

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        gateway._turno(cur, quien, mensaje, ws, chat_id=2)
        real = _fila_esperando(cur)
        cur.execute("update pending_action set estado = 'cancelada'")
        _sembrar_aclaracion(cur, quien, ws, 2, {
            "mensaje": mensaje, "referencia": "lo del tablero",
            "tareas": ["Programar PLC", "Cablear tablero máq. 3"]})
        sembrada = _fila_esperando(cur)

    assert sembrada == real
    assert [e for e, _v in real["opciones"]][1].endswith("— Mariano")  # la ajena


# ---------------------------------------------------------------------------
# La familia b-0025 (T9-R1c-3): Modificar en la vista previa del borrador del
# alta. El borrador sembrado tiene que existir DENTRO de la corrida para que sus
# botones cuenten como de ella (`toques`), y el banco no convierte nunca un
# borrador: sólo su botón Confirmar, por el canal de autoridad.
# ---------------------------------------------------------------------------

_DOS_TAREAS_PARA_EL_ALTA = [
    {"id": "t1", "titulo": "Cablear tablero (simulado)", "area": "ot",
     "responsable": "Marcos Tarquini"},
    {"id": "t2", "titulo": "Revisar tablero eléctrico (simulado)", "area": "ot",
     "responsable": "Marcos Tarquini"}]
_OBJETIVO_OTRO = "Objetivo simulado de Revisar tablero eléctrico (simulado)"


def _con_dos_tareas(conn, ws) -> None:
    with admin(conn) as cur:
        sembrar_precondiciones(cur, ws, {"tareas": _DOS_TAREAS_PARA_EL_ALTA},)
    conn.commit()


def _responde(*textos) -> ProveedorGuionado:
    return ProveedorGuionado(guion=[], rutas=[
        IntentRoute(IntentAction.NORMAL_CONVERSATION, respecto_pendiente=comando)
        for comando in textos])


def _estados_de_las_vistas_previas(conn) -> list[str]:
    with admin(conn) as cur:
        cur.execute("select estado from pending_action where draft_id is not null "
                    "order by creado_en, id")
        return [f["estado"] for f in cur.fetchall()]


def test_sembrar_precondiciones_sin_borrador_de_alta_no_lo_siembra(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        sembrar_precondiciones(cur, ws, {
            "tareas": _DOS_TAREAS_PARA_EL_ALTA[:1],
            "borrador_de_alta": {**_BORRADOR_DE_ALTA}},
            sin_borrador_de_alta=True)
        cur.execute("select count(*) n from task_intake_request")
        assert cur.fetchone()["n"] == 0


def test_el_borrador_sembrado_en_la_corrida_se_toca_por_sus_botones(corework, conn):
    ws = corework.workspace_id
    _con_dos_tareas(conn, ws)
    interno = _responde(RespectoPendiente.RESPONDE)

    r = ejecutar_escenario(
        conn, ws, "corework", "Ismael Soschinski", [], interno,
        escenario_id="b-test-0025", indice=0,
        preguntas_sembradas={"borrador_de_alta": _BORRADOR_DE_ALTA},
        toques=[{"etiqueta": "Modificar"}, {"etiqueta": "Título"}],
        mensajes_tras_toques=["Cablear tablero sur"])

    assert r.bloqueado is False, r.motivo_bloqueo
    # Lo que se evalúa: la vista previa que vuelve, con el dato corregido y sólo ese.
    assert "Título: Cablear tablero sur" in r.respuesta_texto
    assert "Fecha objetivo: 30/12/2030" in r.respuesta_texto
    assert "Cablear tablero norte" not in r.respuesta_texto
    assert _estados_de_las_vistas_previas(conn) == ["cancelada", "esperando"]
    # El banco no confirma el borrador: no hay tarea nueva.
    assert r.conteos_despues["task"] == r.conteos_antes["task"]
    assert r.conteos_antes_del_toque is None


def test_el_borrador_sembrado_en_la_corrida_cambia_un_dato_con_opciones(
        corework, conn):
    ws = corework.workspace_id
    _con_dos_tareas(conn, ws)
    interno = _responde(RespectoPendiente.RESPONDE)

    r = ejecutar_escenario(
        conn, ws, "corework", "Ismael Soschinski", [], interno,
        escenario_id="b-test-0025", indice=1,
        preguntas_sembradas={"borrador_de_alta": {
            **_BORRADOR_DE_ALTA, "objetivo": _TITULO_OBJETIVO_ALTA}},
        toques=[{"etiqueta": "Modificar"}, {"etiqueta": "Objetivo"}],
        mensajes_tras_toques=[_OBJETIVO_OTRO])

    assert r.bloqueado is False, r.motivo_bloqueo
    assert f"Objetivo: {_OBJETIVO_OTRO}" in r.respuesta_texto
    assert _estados_de_las_vistas_previas(conn) == ["cancelada", "esperando"]
    assert r.conteos_despues["task"] == r.conteos_antes["task"]


def test_un_mensaje_que_corrige_la_vista_previa_lleva_al_selector_y_de_ahi_al_dato(
        corework, conn):
    ws = corework.workspace_id
    _con_dos_tareas(conn, ws)
    interno = _responde(RespectoPendiente.CORRIGE, RespectoPendiente.RESPONDE)

    r = ejecutar_escenario(
        conn, ws, "corework", "Ismael Soschinski", [], interno,
        escenario_id="b-test-0025", indice=2,
        preguntas_sembradas={"borrador_de_alta": _BORRADOR_DE_ALTA},
        toques=[], mensajes_tras_toques=["cambiale la fecha", "Fecha objetivo"])

    assert r.bloqueado is False, r.motivo_bloqueo
    # Lo que queda abierto es la pregunta del dato, con lo que tenía para copiar.
    assert "30/12/2030" in r.respuesta_texto
    assert "Esto tenías en la fecha objetivo" in r.respuesta_texto
    assert _estados_de_las_vistas_previas(conn) == ["cancelada"]
    assert r.conteos_despues["task"] == r.conteos_antes["task"]


def test_el_corredor_no_confirma_solo_la_vista_previa_de_un_borrador(corework, conn):
    """Aunque se haya creado durante la corrida y ofrezca Confirmar: convertir un
    borrador es del botón de su aprobador, por el canal de autoridad."""
    ws = corework.workspace_id
    _con_dos_tareas(conn, ws)
    ahora = datetime.now(timezone.utc)
    with admin(conn) as cur:
        sembrar_precondiciones(cur, ws, {"borrador_de_alta": _BORRADOR_DE_ALTA})
        cur.execute("select telegram_user_id t from integrante where nombre = %s",
                    ("Ismael Soschinski",))
        chat = cur.fetchone()["t"]
        assert _pendiente_para_confirmar(cur, ws, chat, ahora - timedelta(days=1)) is None


@pytest.mark.parametrize("escenario_id, comandos", [
    ("b-0025", [RespectoPendiente.RESPONDE]),
    ("b-0025-b", [RespectoPendiente.RESPONDE]),
    ("b-0025-c", [RespectoPendiente.CORRIGE, RespectoPendiente.RESPONDE]),
    ("b-0025-d", []),                                   # sólo toques: nada que rutear
    ("b-0025-e", [RespectoPendiente.RESPONDE]),
])
def test_los_escenarios_de_b_0025_cumplen_lo_que_declaran_con_un_modelo_guionado(
        escenario_id, comandos, corework, conn):
    """Los escenarios de la familia, corridos por el mismo camino que el banco
    real (`test_banco.py`) pero con el ruteo guionado: lo que declaran
    (`respuesta_menciona`, `respuesta_no_contiene_patron`, `efectos`) tiene que
    cumplirse con lo que produce el código, así el banco real sólo mide al
    modelo."""
    from tests.banco.comprobadores import Evidencia, comprobar_contenido, comprobar_efectos
    from tests.banco.conftest import DIR_ESCENARIOS
    from tests.banco.escenario import cargar_escenario

    escenario = cargar_escenario(DIR_ESCENARIOS / f"{escenario_id}.yaml")
    ws = corework.workspace_id
    en_la_corrida = bool(escenario.toques
                         and escenario.precondiciones.get("borrador_de_alta"))
    with admin(conn) as cur:
        sembrar_precondiciones(cur, ws, escenario.precondiciones,
                               sin_borrador_de_alta=en_la_corrida)

    r = ejecutar_escenario(
        conn, ws, "corework", escenario.actor, escenario.mensajes,
        _responde(*comandos), escenario_id=escenario.id, indice=0,
        toques=list(escenario.toques) or None,
        mensajes_tras_toques=list(escenario.mensajes_tras_toques) or None,
        preguntas_sembradas=(
            {"borrador_de_alta": escenario.precondiciones["borrador_de_alta"]}
            if en_la_corrida else None))

    assert r.bloqueado is False, r.motivo_bloqueo
    evidencia = Evidencia(respuesta_texto=r.respuesta_texto,
                          herramientas_ejecutadas=tuple(r.herramientas_ejecutadas),
                          ofrecio_opciones=r.ofrecio_opciones)
    contenido = comprobar_contenido(
        evidencia, menciona=escenario.respuesta_menciona,
        no_contiene_patron=escenario.respuesta_no_contiene_patron)
    assert contenido.resultado == "aprobado", contenido.diferencia
    efectos = comprobar_efectos(
        {"conteos_delta": conteos_delta(r.conteos_antes, r.conteos_despues)},
        escenario.efectos)
    assert efectos.resultado == "aprobado", efectos.diferencia


# ---------------------------------------------------------------------------
# Una respuesta visible por mensaje (T9-R2): la corrida cuenta las respuestas
# de cada mensaje entrante y manda mensajes con adjunto.
# ---------------------------------------------------------------------------


def _correr_con(conn, ws, mensajes, **kw):
    interno = ProveedorGuionado(
        guion=[Respuesta(texto="Anotado.")] * 4,
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)] * 4)
    return ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", mensajes, interno,
        escenario_id="b-test", indice=0, **kw)


def test_la_corrida_cuenta_una_respuesta_por_cada_mensaje(corework, conn):
    r = _correr_con(conn, corework.workspace_id, ["hola", "gracias"])

    assert r.bloqueado is False
    assert r.respuestas_por_mensaje == (1, 1)
    assert r.incidentes_de_respuesta == ()


@pytest.mark.parametrize("adjunto, epigrafe", [
    ("foto", None), ("nota_de_voz", None), ("sticker", None),
    ("foto", "el tablero de la máquina 3")])
def test_la_corrida_manda_mensajes_con_adjunto_y_cuenta_su_respuesta(
        adjunto, epigrafe, corework, conn):
    mensaje = {"adjunto": adjunto, **({"epigrafe": epigrafe} if epigrafe else {})}

    r = _correr_con(conn, corework.workspace_id, [mensaje])

    assert r.bloqueado is False
    assert r.respuestas_por_mensaje == (1,)
    if epigrafe is None:
        assert "fotos, archivos ni audios" in r.respuesta_texto
    else:
        assert "Todavía no guardo adjuntos" in r.respuesta_texto


def test_un_toque_no_cuenta_como_mensaje_en_la_corrida(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        sembrar_precondiciones(cur, ws, {"tareas": [
            {"id": "t1", "titulo": "Programar PLC (simulado)", "area": "ot",
             "responsable": "Marcos Tarquini"}]})
    conn.commit()
    interno = ProveedorGuionado(
        guion=[Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
               Respuesta(texto="Tenés una tarea pendiente.")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)])

    # Tocar la tarea de la lista abre su menú: el toque deja su fila de
    # actividad (un `inbound_message` sin texto) y una salida propia.
    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["pasame mis tareas"], interno,
        escenario_id="b-test-toque-no-cuenta", indice=0, toques=[{"indice": 0}])

    assert r.bloqueado is False, r.motivo_bloqueo
    with admin(conn) as cur:
        cur.execute("select count(*) n from inbound_message "
                    "where workspace_id = %s and texto is null", (ws,))
        filas_de_toque = cur.fetchone()["n"]
        cur.execute(
            """select count(*) n from message_outbox
                where workspace_id = %s and es_respuesta
                  and entrante_id in (select id from inbound_message
                                       where texto is null)
                  and pending_action_id is not null""", (ws,))
        salidas_del_toque = cur.fetchone()["n"]
    # El toque ocurrió de verdad, y con salida visible (el menú de la tarea)...
    assert filas_de_toque >= 1 and salidas_del_toque >= 1
    # ...pero ni su fila de actividad ni su salida cuentan: un solo mensaje, una
    # sola respuesta.
    assert r.respuestas_por_mensaje == (1,)


def test_la_corrida_ve_un_camino_que_encola_dos_respuestas_aunque_el_control_lo_arregle(
        corework, conn, monkeypatch):
    from datetime import timedelta as _td

    from prisma import gateway

    def turno_doble(cur, quien, texto, workspace_id, chat_id, entrante_id=None, **k):
        ahora = datetime.now(timezone.utc)
        gateway._responder(cur, workspace_id, chat_id, quien, "Primera.", ahora)
        gateway._responder(cur, workspace_id, chat_id, quien, "Segunda.",
                           ahora + _td(seconds=1))

    monkeypatch.setattr(gateway, "_turno", turno_doble)

    r = _correr_con(conn, corework.workspace_id, ["hola"])

    assert r.respuestas_por_mensaje == (2,)
    assert len(r.incidentes_de_respuesta) == 1
    assert "se suprimieron 1" in r.incidentes_de_respuesta[0]


@pytest.mark.parametrize("id_", ["b-0026-b", "b-0026-c", "b-0026-d", "b-0026-e"])
def test_la_familia_b_0026_sin_texto_se_cumple_sin_llamar_al_modelo(
        id_, corework, conn):
    """Los escenarios de mensajes sin texto no necesitan al modelo: un proveedor
    sin guion (que fallaría al usarse) alcanza, y todas las comprobaciones del
    banco -- la de una respuesta por mensaje incluida -- aprueban."""
    import pathlib

    from tests.banco.comprobadores import (Evidencia, comprobar_contenido,
                                           comprobar_efectos,
                                           comprobar_herramientas,
                                           comprobar_una_respuesta_por_entrada,
                                           resultado_general)
    from tests.banco.escenario import cargar_escenario

    escenario = cargar_escenario(
        pathlib.Path(__file__).parent / "escenarios" / f"{id_}.yaml")
    ws = corework.workspace_id
    en_la_corrida = bool(escenario.toques
                         and escenario.precondiciones.get("borrador_de_alta"))
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, escenario.precondiciones,
                                     sin_borrador_de_alta=en_la_corrida)
    conn.commit()

    r = ejecutar_escenario(
        conn, ws, "corework", escenario.actor, escenario.mensajes,
        ProveedorGuionado(guion=[], rutas=[]), escenario_id=id_, indice=0,
        toques=list(escenario.toques) or None,
        mensajes_tras_toques=list(escenario.mensajes_tras_toques) or None,
        preguntas_sembradas=(
            {"borrador_de_alta": escenario.precondiciones["borrador_de_alta"]}
            if en_la_corrida else None))

    assert not r.bloqueado, r.motivo_bloqueo
    evidencia = Evidencia(respuesta_texto=r.respuesta_texto,
                          herramientas_ejecutadas=tuple(r.herramientas_ejecutadas),
                          ofrecio_opciones=r.ofrecio_opciones)
    comprobaciones = [
        comprobar_herramientas(evidencia, esperadas=escenario.herramientas_esperadas,
                               prohibidas=escenario.herramientas_prohibidas),
        comprobar_contenido(
            evidencia, menciona=escenario.respuesta_menciona,
            no_contiene_patron=escenario.respuesta_no_contiene_patron),
        comprobar_una_respuesta_por_entrada(
            r.respuestas_por_mensaje, incidentes=r.incidentes_de_respuesta),
    ]
    assert resultado_general(comprobaciones) == "aprobado", [
        (c.nombre, c.diferencia) for c in comprobaciones]


# ---------------------------------------------------------------------------
# T9-R3 (familia b-0027): estados reales. `criterio_por_confirmar` deja el último
# dato del alta esperando su Sí/No; `cambios_pedidos` deja una tarea como la deja
# "Pedir cambios".
# ---------------------------------------------------------------------------

# Nahuel pide el alta de lo suyo: lo confirma Marcos, su aprobador.
_ALTA_DE_OTRO_APROBADOR = {
    "solicitante": "Nahuel Gimenez", "titulo": "Cablear tablero norte",
    "objetivo": _TITULO_OBJETIVO_ALTA, "responsable": "Nahuel Gimenez",
    "area": "ot", "fecha_objetivo": "2030-12-30",
    "criterio_aceptacion": "Prueba firmada", "criterio_por_confirmar": True}


def test_sembrar_criterio_por_confirmar_deja_esperando_el_ultimo_dato(corework, conn):
    from prisma import ingreso_tareas as I

    ws = corework.workspace_id
    _sembrar_objetivo_para_el_alta(conn, ws)
    with admin(conn) as cur:
        sembrar_precondiciones(cur, ws, {"borrador_de_alta": _ALTA_DE_OTRO_APROBADOR})

    with espacio(conn, ws) as cur:
        quien, tg = _quien(cur, ws, "Nahuel Gimenez")
        pregunta = I.open_intake_question(cur, quien, tg)
        cur.execute("select count(*) n from pending_action where draft_id is not null")
        vistas_previas = cur.fetchone()["n"]
    assert pregunta["tipo"] == I.QUESTION_CHOICE
    assert vistas_previas == 0                 # todavía nadie tiene qué confirmar


def test_ejecutar_escenario_termina_el_alta_por_toque_y_dice_quien_confirma(
        corework, conn):
    ws = corework.workspace_id
    _sembrar_objetivo_para_el_alta(conn, ws)
    interno = _responde(RespectoPendiente.RESPONDE)

    # Terminar el alta le deja a quien pide su resumen para revisar (T9-R1c-4); recién
    # al enviarlo se le dice a quién se le mandó.
    r = ejecutar_escenario(
        conn, ws, "corework", "Nahuel Gimenez", [], interno,
        escenario_id="b-test-0027", indice=0,
        preguntas_sembradas={"borrador_de_alta": _ALTA_DE_OTRO_APROBADOR},
        toques=[{"etiqueta": "Sí"}, {"etiqueta": "Enviar a aprobación"}])

    assert r.bloqueado is False, r.motivo_bloqueo
    assert "Marcos Tarquini" in r.respuesta_texto
    assert "No pude completar" not in r.respuesta_texto
    assert r.conteos_despues["task"] == r.conteos_antes["task"]


def test_sembrar_cambios_pedidos_deja_la_tarea_por_hacer_con_su_motivo(corework, conn):
    from prisma import menu_tarea as M

    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {"tareas": [{
            "id": "t1", "titulo": "Programar PLC (simulado)", "area": "ot",
            "responsable": "Nahuel Gimenez",
            "cambios_pedidos": {"por": "Marcos Tarquini",
                                "motivo": "falta la captura con la hora"}}]})

    with espacio(conn, ws) as cur:
        cur.execute("select estado from task where id = %s", (ids["t1"],))
        assert cur.fetchone()["estado"] == "asignada"
        assert M.cambios_pedidos(cur, ids["t1"]) == (
            "Cambios pedidos por Marcos Tarquini: falta la captura con la hora")


def test_sembrar_cambios_pedidos_sin_el_motivo_falla_nombrandolo(corework, conn):
    ws = corework.workspace_id

    with admin(conn) as cur, pytest.raises(LookupError, match="motivo"):
        sembrar_precondiciones(cur, ws, {"tareas": [{
            "id": "t1", "titulo": "Programar PLC (simulado)", "area": "ot",
            "responsable": "Nahuel Gimenez",
            "cambios_pedidos": {"por": "Marcos Tarquini"}}]})


# ---------------------------------------------------------------------------
# Tocar dos veces el mismo botón (T9-R4, ADR 0013 regla 4): `veces` y `cada_s`
# en un toque, y `confirmar` para el Confirmar automático. El reloj de la corrida
# es real: el intervalo se simula envejeciendo los toques ya registrados
# (`inbound_message.at`), sin dormir.
# ---------------------------------------------------------------------------


def _sembrar_tarea_en_curso_posible(conn, ws) -> str:
    with admin(conn) as cur:
        return sembrar_precondiciones(cur, ws, {
            "tareas": [{"id": "t1", "titulo": "Programar PLC (simulado)",
                       "area": "ot", "responsable": "Marcos Tarquini",
                       "evidencia_requerida": []}]})["t1"]


def _lista_de_tareas():
    return ProveedorGuionado(
        guion=[Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
               Respuesta(texto="Tenés una tarea pendiente.")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)])


def _absorbidos(conn, ws) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from audit_log where workspace_id = %s "
                    "and accion = 'toque_repetido_absorbido'", (ws,))
        return cur.fetchone()["n"]


def test_la_corrida_toca_dos_veces_el_mismo_boton_dentro_de_la_ventana(
        corework, conn):
    ws = corework.workspace_id
    _sembrar_tarea_en_curso_posible(conn, ws)

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["pasame mis tareas"],
        _lista_de_tareas(), escenario_id="b-test-doble-toque", indice=0,
        toques=[{"indice": 0, "veces": 2, "cada_s": 3}])

    assert r.bloqueado is False, r.motivo_bloqueo
    assert _absorbidos(conn, ws) == 1
    assert r.respuestas_por_toque == (1,)            # el absorbido no cuenta
    assert "ya no está vigente" not in r.respuesta_texto
    assert r.incidentes_de_respuesta == ()


def test_la_corrida_toca_dos_veces_el_mismo_boton_fuera_de_la_ventana(
        corework, conn):
    ws = corework.workspace_id
    _sembrar_tarea_en_curso_posible(conn, ws)

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["pasame mis tareas"],
        _lista_de_tareas(), escenario_id="b-test-doble-toque-lento", indice=0,
        toques=[{"indice": 0, "veces": 2, "cada_s": 12}])

    assert r.bloqueado is False, r.motivo_bloqueo
    assert _absorbidos(conn, ws) == 0
    assert r.respuestas_por_toque == (1, 1)           # cada uno, su respuesta
    assert "ya no está vigente" in r.respuesta_texto


def test_la_corrida_confirma_dos_veces_y_la_herramienta_corre_una_sola_vez(
        corework, conn):
    ws = corework.workspace_id
    tid = _sembrar_tarea_en_curso_posible(conn, ws)

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini", ["pasame mis tareas"],
        _lista_de_tareas(), escenario_id="b-test-doble-confirmar", indice=0,
        toques=[{"indice": 0}, {"etiqueta": "Ya la terminé"}],
        confirmar={"veces": 2, "cada_s": 3})

    assert r.bloqueado is False, r.motivo_bloqueo
    assert _absorbidos(conn, ws) == 1
    assert r.herramientas_ejecutadas.count("actualizar_estado") == 1
    assert r.conteos_despues["task_state_event"] == (
        r.conteos_antes["task_state_event"] + 1)
    assert r.incidentes_de_respuesta == ()
    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_revision"


# ---------------------------------------------------------------------------
# La familia b-0029 (T9-R1c-4): quien pide revisa su resumen antes de enviarlo a
# aprobación. Con el ruteo guionado, lo que declaran los escenarios tiene que
# cumplirse con lo que produce el código; el banco real sólo mide al modelo.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("escenario_id, comandos", [
    ("b-0029", []),                                     # sólo el toque de Sí
    ("b-0029-b", [RespectoPendiente.RESPONDE]),         # el título corregido
    ("b-0029-c", [RespectoPendiente.OTRO_TEMA]),
    ("b-0029-d", [RespectoPendiente.RESPONDE]),
])
def test_los_escenarios_de_b_0029_cumplen_lo_que_declaran_con_un_modelo_guionado(
        escenario_id, comandos, corework, conn):
    from tests.banco.comprobadores import (Evidencia, comprobar_contenido,
                                           comprobar_efectos,
                                           comprobar_una_respuesta_por_entrada)
    from tests.banco.conftest import DIR_ESCENARIOS
    from tests.banco.escenario import cargar_escenario

    escenario = cargar_escenario(DIR_ESCENARIOS / f"{escenario_id}.yaml")
    ws = corework.workspace_id
    en_la_corrida = bool(escenario.toques
                         and escenario.precondiciones.get("borrador_de_alta"))
    with admin(conn) as cur:
        sembrar_precondiciones(cur, ws, escenario.precondiciones,
                               sin_borrador_de_alta=en_la_corrida)

    r = ejecutar_escenario(
        conn, ws, "corework", escenario.actor, escenario.mensajes,
        _responde(*comandos), escenario_id=escenario.id, indice=0,
        toques=list(escenario.toques) or None,
        mensajes_tras_toques=list(escenario.mensajes_tras_toques) or None,
        toques_tras_mensajes=list(escenario.toques_tras_mensajes) or None,
        preguntas_sembradas=(
            {"borrador_de_alta": escenario.precondiciones["borrador_de_alta"]}
            if en_la_corrida else None))

    assert r.bloqueado is False, r.motivo_bloqueo
    evidencia = Evidencia(respuesta_texto=r.respuesta_texto,
                          herramientas_ejecutadas=tuple(r.herramientas_ejecutadas),
                          ofrecio_opciones=r.ofrecio_opciones)
    contenido = comprobar_contenido(
        evidencia, menciona=escenario.respuesta_menciona,
        no_contiene_patron=escenario.respuesta_no_contiene_patron)
    assert contenido.resultado == "aprobado", contenido.diferencia
    efectos = comprobar_efectos(
        {"conteos_delta": conteos_delta(r.conteos_antes, r.conteos_despues)},
        escenario.efectos)
    assert efectos.resultado == "aprobado", efectos.diferencia
    comprobacion = comprobar_una_respuesta_por_entrada(
        r.respuestas_por_mensaje, incidentes=r.incidentes_de_respuesta)
    assert comprobacion.resultado == "aprobado", comprobacion.diferencia
    # Cada toque recibió una sola respuesta.
    assert all(n == 1 for n in r.respuestas_por_toque), r.respuestas_por_toque
