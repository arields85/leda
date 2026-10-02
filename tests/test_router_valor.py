"""Contrato del valor normalizado en el ruteo (ADR 0014, M1, etapa 2).

Con una pregunta pendiente que espera un valor, el ruteo suma un objeto
cerrado `valor` (`fecha_iso`, `opcion_id`, `texto`) y le dice al modelo el
tipo esperado, las opciones con sus ids y el día de hoy. Un `valor` mal
formado degrada a "sin valor": nunca tira abajo el ruteo ni inventa un dato.
El modelo está guionado: lo que se prueba es el contrato (esquema, sistema,
validación, degradación), no la comprensión del lenguaje.
"""

from __future__ import annotations

from datetime import date

import pytest

import leda.llm as llm
from leda.llm import (IntentAction, IntentRoute, Llamada, ProveedorGuionado,
                         RespectoPendiente, RouteEnvelope, RoutingError)
from leda.valores import TipoValor, ValorEsperado, opciones_numeradas
from tests.test_router_pendiente import (ADAPTADORES, PENDIENTE, _esquema_y_sistema,
                                         _proveedor)

HOY = date(2026, 9, 30)    # un miércoles
FECHA = ValorEsperado(TipoValor.FECHA, hoy=HOY)
OPCIONES = opciones_numeradas(["Cocina", "Taller", "Oficina"])
OPCION = ValorEsperado(TipoValor.OPCION, OPCIONES)
TEXTO = ValorEsperado(TipoValor.TEXTO)
ENTIDAD = ValorEsperado(TipoValor.ENTIDAD)
NINGUNO = ValorEsperado(TipoValor.NINGUNO)


def _payload(**extra):
    return {"action": "normal_conversation", "respecto_pendiente": "responde",
            **extra}


# --- esquema y sistema -------------------------------------------------------

@pytest.mark.parametrize("adapter", ADAPTADORES)
def test_sin_valor_esperado_el_esquema_no_cambia(adapter):
    capturas: list = []
    proveedor = _proveedor(adapter, _payload(), capturas)
    proveedor.route_intent("x", pendiente=PENDIENTE)

    esquema, sistema = _esquema_y_sistema(adapter, capturas[0])
    assert "valor" not in esquema["properties"]
    assert "valor" not in esquema["required"]
    assert sistema == llm._sistema_del_ruteo(PENDIENTE)


@pytest.mark.parametrize("adapter", ADAPTADORES)
@pytest.mark.parametrize("esperado", [FECHA, OPCION, TEXTO, ENTIDAD],
                         ids=["fecha", "opcion", "texto", "entidad"])
def test_con_valor_esperado_el_esquema_suma_un_valor_cerrado_y_opcional(
        adapter, esperado):
    capturas: list = []
    proveedor = _proveedor(adapter, _payload(), capturas)
    proveedor.route_intent("x", pendiente=PENDIENTE, valor_esperado=esperado)

    esquema, _ = _esquema_y_sistema(adapter, capturas[0])
    valor = esquema["properties"]["valor"]
    assert valor["type"] == "object"
    assert set(valor["properties"]) == {"fecha_iso", "opcion_id", "texto", "falta"}
    assert all(p["type"] == "string" for p in valor["properties"].values())
    assert "valor" not in esquema["required"]       # opcional: sin dato, sin valor
    assert "respecto_pendiente" in esquema["required"]
    if adapter != "gemini":     # Gemini rechaza `additionalProperties`: se limpia
        assert valor["additionalProperties"] is False


@pytest.mark.parametrize("adapter", ADAPTADORES)
def test_con_opciones_el_id_es_de_lista_cerrada_con_ninguna(adapter):
    capturas: list = []
    proveedor = _proveedor(adapter, _payload(), capturas)
    proveedor.route_intent("x", pendiente=PENDIENTE, valor_esperado=OPCION)

    esquema, _ = _esquema_y_sistema(adapter, capturas[0])
    enum = esquema["properties"]["valor"]["properties"]["opcion_id"]["enum"]
    assert enum == ["1", "2", "3", "ninguna"]


@pytest.mark.parametrize("adapter", ADAPTADORES)
def test_una_pregunta_sin_valor_esperado_no_suma_el_campo(adapter):
    capturas: list = []
    proveedor = _proveedor(adapter, _payload(), capturas)
    proveedor.route_intent("x", pendiente=PENDIENTE, valor_esperado=NINGUNO)

    esquema, sistema = _esquema_y_sistema(adapter, capturas[0])
    assert "valor" not in esquema["properties"]
    assert sistema == llm._sistema_del_ruteo(PENDIENTE)


def test_el_esquema_global_no_se_muta():
    llm._herramienta_del_ruteo(PENDIENTE, FECHA)
    assert "valor" not in llm.ROUTER_TOOL["input_schema"]["properties"]
    assert "respecto_pendiente" not in llm.ROUTER_TOOL["input_schema"]["properties"]


def test_el_sistema_de_fecha_trae_el_dia_de_hoy_y_como_normalizar():
    sistema = llm._sistema_del_ruteo(PENDIENTE, FECHA)
    assert sistema.startswith(llm._sistema_del_ruteo(PENDIENTE))
    assert "2026-09-30" in sistema
    assert "miércoles" in sistema
    assert "fecha_iso" in sistema and "AAAA-MM-DD" in sistema
    # Las formas sueltas se nombran como ejemplos de lo que el modelo resuelve.
    for forma in ("mañana", "el viernes", "4 de octubre", "04 / 10"):
        assert forma in sistema
    assert "no inventes" in sistema.lower()


@pytest.mark.parametrize("hoy, dia", [
    (date(2026, 9, 28), "lunes"), (date(2026, 9, 29), "martes"),
    (date(2026, 10, 1), "jueves"), (date(2026, 10, 2), "viernes"),
    (date(2026, 10, 3), "sábado"), (date(2026, 10, 4), "domingo"),
])
def test_el_dia_de_la_semana_sale_de_hoy_sin_depender_del_idioma_del_sistema(
        hoy, dia):
    sistema = llm._sistema_del_ruteo(
        PENDIENTE, ValorEsperado(TipoValor.FECHA, hoy=hoy))
    assert dia in sistema


def test_el_sistema_de_opcion_lista_cada_id_con_su_etiqueta():
    sistema = llm._sistema_del_ruteo(PENDIENTE, OPCION)
    for opcion in OPCIONES:
        assert f"{opcion.id}" in sistema and f"«{opcion.etiqueta}»" in sistema
    assert "opcion_id" in sistema and "ninguna" in sistema


def test_el_sistema_de_texto_pide_lo_que_la_persona_quiso_decir():
    sistema = llm._sistema_del_ruteo(PENDIENTE, TEXTO)
    assert "valor.texto" in sistema
    assert "fecha_iso" not in sistema


def test_el_sistema_de_entidad_pide_la_referencia_tal_como_la_escribio():
    sistema = llm._sistema_del_ruteo(PENDIENTE, ENTIDAD)
    assert "valor.texto" in sistema and "referencia" in sistema


def test_la_fecha_sin_hoy_es_un_defecto_y_no_un_sistema_a_medias():
    with pytest.raises(ValueError):
        llm._sistema_del_ruteo(PENDIENTE, ValorEsperado(TipoValor.FECHA))


# --- validación del sobre ----------------------------------------------------

@pytest.mark.parametrize("adapter", ADAPTADORES)
@pytest.mark.parametrize("valor", [
    {"fecha_iso": "2026-10-04"},
    {"opcion_id": "2"},
    {"opcion_id": "ninguna"},
    {"texto": "faltó el repuesto"},
    {"fecha_iso": "2026-10-04", "texto": "el cuatro"},
])
def test_un_valor_bien_formado_llega_en_la_ruta(adapter, valor):
    proveedor = _proveedor(adapter, _payload(valor=valor), [])
    route = proveedor.route_intent("x", pendiente=PENDIENTE, valor_esperado=FECHA)
    assert route.valor == valor
    assert route.respecto_pendiente is RespectoPendiente.RESPONDE


@pytest.mark.parametrize("adapter", ADAPTADORES)
def test_sin_valor_la_ruta_trae_un_valor_vacio(adapter):
    proveedor = _proveedor(adapter, _payload(), [])
    route = proveedor.route_intent("x", pendiente=PENDIENTE, valor_esperado=FECHA)
    assert route.valor == {}


MALFORMADOS = [
    pytest.param("2026-10-04", id="texto-suelto"),
    pytest.param(["2026-10-04"], id="lista"),
    pytest.param(None, id="nulo"),
    pytest.param(7, id="numero"),
    pytest.param({"fecha_iso": 20261004}, id="campo-no-texto"),
    pytest.param({"fecha_iso": ""}, id="campo-vacio"),
    pytest.param({"fecha_iso": "   "}, id="campo-en-blanco"),
    pytest.param({"fecha": "2026-10-04"}, id="campo-desconocido"),
    pytest.param({"fecha_iso": "2026-10-04", "otro": "x"}, id="campo-de-mas"),
    pytest.param({"texto": "x" * (llm.MAX_LONGITUD_VALOR + 1)}, id="enorme"),
    pytest.param({"opcion_id": ["1"]}, id="opcion-lista"),
    pytest.param({"falta": "no-existe"}, id="falta-desconocida"),
    pytest.param({"falta": ["dia"]}, id="falta-lista"),
]


@pytest.mark.parametrize("adapter", ADAPTADORES)
@pytest.mark.parametrize("valor", MALFORMADOS)
def test_un_valor_mal_formado_degrada_a_sin_valor_y_no_tira_el_ruteo(
        adapter, valor):
    proveedor = _proveedor(adapter, _payload(valor=valor), [])
    route = proveedor.route_intent("x", pendiente=PENDIENTE, valor_esperado=FECHA)
    assert route.valor == {}
    # La decisión válida del resto del sobre se conserva.
    assert route.respecto_pendiente is RespectoPendiente.RESPONDE
    assert route.action is IntentAction.NORMAL_CONVERSATION


def test_un_valor_sin_haberlo_pedido_es_un_campo_desconocido():
    envelope = RouteEnvelope(calls=(Llamada(
        "c", "route_intent", _payload(valor={"texto": "x"})),))
    with pytest.raises(RoutingError):
        envelope.validate(con_pendiente=True)          # sin con_valor
    with pytest.raises(RoutingError):
        RouteEnvelope(calls=(Llamada(
            "c", "route_intent",
            {"action": "normal_conversation", "valor": {"texto": "x"}}),
        )).validate()


def test_el_valor_se_recorta_en_la_ruta():
    envelope = RouteEnvelope(calls=(Llamada(
        "c", "route_intent",
        _payload(valor={"texto": "  el repuesto  "})),))
    assert envelope.validate(con_pendiente=True, con_valor=True).valor == {
        "texto": "el repuesto"}


# --- el proveedor guionado ---------------------------------------------------

def test_el_guionado_deja_guionar_el_valor_y_anota_lo_que_esperaba():
    proveedor = ProveedorGuionado(guion=[], rutas=[IntentRoute(
        IntentAction.NORMAL_CONVERSATION, valor={"fecha_iso": "2026-10-04"})])

    route = proveedor.route_intent("4de octubre", pendiente=PENDIENTE,
                                   valor_esperado=FECHA)

    assert route.valor == {"fecha_iso": "2026-10-04"}
    assert route.respecto_pendiente is RespectoPendiente.RESPONDE
    assert proveedor.esperados == [FECHA]
    assert proveedor.pendientes == [PENDIENTE]


def test_el_guionado_sin_valor_esperado_ignora_el_valor_guionado():
    proveedor = ProveedorGuionado(guion=[], rutas=[IntentRoute(
        IntentAction.NORMAL_CONVERSATION, valor={"texto": "x"})])
    route = proveedor.route_intent("x", pendiente=PENDIENTE)
    assert route.valor == {}
    assert proveedor.esperados == [None]


def test_el_guionado_pasa_por_la_validacion_un_sobre_con_valor_mal_formado():
    sobre = RouteEnvelope(calls=(Llamada(
        "c", "route_intent", _payload(valor="mañana")),))
    proveedor = ProveedorGuionado(guion=[], rutas=[sobre])
    route = proveedor.route_intent("x", pendiente=PENDIENTE, valor_esperado=FECHA)
    assert route.valor == {}


def test_un_proveedor_sin_valor_esperado_sigue_llamandose_como_antes():
    # Los que no saben de valores (`route_intent(text, pendiente)`) no se
    # rompen: el gateway sólo pasa `valor_esperado` cuando hay uno.
    from leda import gateway

    visto = {}

    class Viejo:
        def route_intent(self, text, pendiente=None):
            visto["args"] = (text, pendiente)
            return IntentRoute(IntentAction.NORMAL_CONVERSATION)

    ruta, error = gateway._rutear(Viejo(), "hola", pendiente="p")
    assert error is None and visto["args"] == ("hola", "p")


def test_el_gateway_pasa_el_valor_esperado_al_ruteo():
    from leda import gateway

    proveedor = ProveedorGuionado(guion=[], rutas=[IntentRoute(
        IntentAction.NORMAL_CONVERSATION, valor={"fecha_iso": "2026-10-04"})])
    ruta, error = gateway._rutear(proveedor, "x", pendiente=PENDIENTE,
                                  valor_esperado=FECHA)
    assert error is None
    assert proveedor.esperados == [FECHA]
    assert ruta.valor == {"fecha_iso": "2026-10-04"}


# --- el banco graba y reproduce el valor -------------------------------------

def test_el_grabador_del_banco_pasa_el_valor_esperado_y_graba_el_valor():
    from tests.banco.corrida import ProveedorGrabador, guionado_desde_grabacion

    interno = ProveedorGuionado(guion=[], rutas=[IntentRoute(
        IntentAction.NORMAL_CONVERSATION, valor={"fecha_iso": "2026-10-04"})])
    grabador = ProveedorGrabador(interno)

    route = grabador.route_intent("4de octubre", pendiente=PENDIENTE,
                                  valor_esperado=FECHA)

    assert interno.esperados == [FECHA]
    assert route.valor == {"fecha_iso": "2026-10-04"}
    (registro,) = grabador.rutas
    assert registro["valor_esperado"]["tipo"] == "fecha"
    # El replay devuelve el mismo valor.
    replay = guionado_desde_grabacion(grabador.a_json())
    assert replay.route_intent("x", pendiente=PENDIENTE,
                               valor_esperado=FECHA).valor == {
        "fecha_iso": "2026-10-04"}


def test_el_grabador_sigue_llamando_como_antes_sin_valor_esperado():
    from tests.banco.corrida import ProveedorGrabador

    visto = {}

    class Viejo:
        def route_intent(self, text, pendiente=None):
            visto["args"] = (text, pendiente)
            return IntentRoute(IntentAction.NORMAL_CONVERSATION)

    ProveedorGrabador(Viejo()).route_intent("hola", pendiente="p")
    assert visto["args"] == ("hola", "p")


# --- el valor incompleto (F-B1) ---------------------------------------------

@pytest.mark.parametrize("adapter", ADAPTADORES)
@pytest.mark.parametrize(("esperado", "faltas"), [
    (FECHA, ["dia"]), (OPCION, ["cual"]), (TEXTO, ["detalle"]),
    (ENTIDAD, ["detalle"]),
], ids=["fecha", "opcion", "texto", "entidad"])
def test_la_falta_es_de_lista_cerrada_segun_el_tipo(adapter, esperado, faltas):
    capturas: list = []
    proveedor = _proveedor(adapter, _payload(), capturas)
    proveedor.route_intent("x", pendiente=PENDIENTE, valor_esperado=esperado)

    esquema, _ = _esquema_y_sistema(adapter, capturas[0])
    assert esquema["properties"]["valor"]["properties"]["falta"]["enum"] == faltas


@pytest.mark.parametrize(("esperado", "falta"), [
    (FECHA, "dia"), (OPCION, "cual"), (TEXTO, "detalle")])
def test_el_sistema_explica_cuando_usar_la_falta(esperado, falta):
    sistema = llm._sistema_del_ruteo(PENDIENTE, esperado)
    assert f'valor.falta = "{falta}"' in sistema


@pytest.mark.parametrize("adapter", ADAPTADORES)
@pytest.mark.parametrize("valor", [{"falta": "dia"}, {"falta": "cual"},
                                   {"falta": "detalle"}])
def test_una_falta_bien_formada_llega_en_la_ruta(adapter, valor):
    proveedor = _proveedor(adapter, _payload(valor=valor), [])
    route = proveedor.route_intent("x", pendiente=PENDIENTE, valor_esperado=FECHA)
    assert route.valor == valor
