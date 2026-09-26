"""Pruebas de la corrida y grabación del banco: el proveedor grabador (sin
base, con un `ProveedorGuionado` interno) y `ejecutar_escenario` sobre el
circuito real (`gateway.procesar_update`), con la base descartable de las
pruebas. TDD estricto.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import psycopg
import pytest

from prisma import agente, herramientas
from prisma import pendientes as P
from prisma.autoridad import Canal, identificar
from prisma.db import admin, espacio
from prisma.jev import ClienteJevGuionado
from prisma.llm import IntentAction, IntentRoute, Llamada, ProveedorGuionado, Respuesta

from tests.banco.corrida import (
    JevGrabador,
    ProveedorGrabador,
    _MARCA_TURNO_CAIDO,
    _pendiente_para_confirmar,
    conteos_delta,
    ejecutar_escenario,
    filas_respuesta,
    guionado_desde_grabacion,
    jev_guionado_desde_grabacion,
    recolectar_efectos,
    respuesta_ofrecio_opciones,
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
    assert isinstance(jev_guionado, ClienteJevGuionado)
    r1 = jev_guionado.decidir({}, {})
    assert r1["alcance"]["probabilities"]["una_tarea"] == 0.9
    r2 = jev_guionado.decidir({}, {})
    assert r2["misma"]["noul"] == 0.8


def test_jev_grabacion_vieja_sin_clave_jev_sigue_cargando():
    """Una grabación de antes de T6 no tiene la clave 'jev' -- tiene que
    seguir cargando, con un guión vacío (nunca llama a Jev de verdad si el
    escenario no traía ninguna referencia que lo hubiera ejercitado)."""
    grabacion_vieja = {"rutas": [], "respuestas": []}
    jev_guionado = jev_guionado_desde_grabacion(grabacion_vieja)
    assert isinstance(jev_guionado, ClienteJevGuionado)
    assert jev_guionado.guion == []


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

        encontrada = _pendiente_para_confirmar(cur, ws, tg)

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

        encontrada = _pendiente_para_confirmar(cur, ws, tg)

    assert encontrada is None


def test_pendiente_para_confirmar_sin_ninguna_pendiente_es_none(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        _, tg = _quien(cur, ws)
        encontrada = _pendiente_para_confirmar(cur, ws, tg)
    assert encontrada is None


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
                   {"tarea_id": tid_a, "estado": "en_revision"})]),
              Respuesta(texto="listo")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                           trabajos=("lo del tablero",))],
    )

    r = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini",
        ["ya termine lo del tablero, pasala a revision"], interno,
        escenario_id="b-test-aclaracion", indice=0, cliente_jev=doble_jev,
        aclaracion_esperada={
            "candidatas": ["Cablear tablero máq. 3 (simulado)",
                          "Revisar tablero máq. 4 (simulado)"],
            "elegir": "Cablear tablero máq. 3 (simulado)"})

    assert r.bloqueado is False, r.motivo_bloqueo
    assert set(r.etiquetas_aclaracion_ofrecidas) >= {
        "Cablear tablero máq. 3 (simulado)", "Revisar tablero máq. 4 (simulado)"}
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
