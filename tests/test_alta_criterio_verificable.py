"""F-B7: el criterio de aceptación tiene que ser concreto y verificable
(`nucleo/mecanica-pm.md` §13.2). El modelo, al interpretar la respuesta, también
juzga si lo es (`valor.verificable`, un campo cerrado) y, si no lo es, propone uno
armado con el título y lo que la persona dijo (`valor.propuesta`). El código
valida la propuesta y Prisma nunca compromete un criterio que la persona no
eligió: la propuesta sale con botones para usarla o escribir otro. Una sola
propuesta: si la persona insiste con su texto, se acepta."""

from __future__ import annotations

import json
from datetime import timedelta

import pytest

from prisma import gateway, incidentes, llm
from prisma import pendientes as P
from prisma import ingreso_tareas as I
from prisma.db import admin, espacio
from prisma.llm import IntentAction, IntentRoute, RespectoPendiente
from prisma.valores import TipoValor, ValorEsperado

from tests.test_alta_guiada_flujo import (CHAT, TITULO, _campo, _conjunto_activo,
                                          _elegir, _empezar, _entrante, _slot)
from tests.test_alta_guiada_flujo import _en_la_fecha
from tests.test_alta_guiada_mensaje_entero import _a, _Eco, _intentos, _json
from tests.test_task_intake import NOW, _active_choices

PROPUESTA = ("Los sensores de la línea 2 quedan calibrados y se adjunta el "
             "registro de la calibración")
NO_SE = "no lo sé, voy a ver"


def _en_el_criterio(cur, world):
    """El alta con todo confirmado menos el criterio de aceptación, que espera."""
    actor, rid, ws = _en_la_fecha(cur, world)
    inbound = _entrante(cur, ws, actor, "el 4 de octubre", n=820)
    I.consume_pending_text(cur, actor, chat_id=CHAT, source_inbound_id=inbound,
                           source_raw_text="el 4 de octubre", now=NOW,
                           valor={"fecha_iso": "2028-10-04"})
    assert _slot(cur, rid) == "acceptance_criterion"
    return actor, rid, ws


def _decir(cur, actor, ws, valor, texto=NO_SE, n=830):
    inbound = _entrante(cur, ws, actor, texto, n=n)
    return I.consume_pending_text(
        cur, actor, chat_id=CHAT, source_inbound_id=inbound,
        source_raw_text=texto, now=NOW + timedelta(minutes=1), valor=valor)


def _no_verificable(texto=NO_SE, propuesta=PROPUESTA):
    return {"texto": texto, "verificable": "no", "propuesta": propuesta}


def _incidentes_de(conn, etapa):
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where etapa = %s", (etapa,))
        return cur.fetchone()["n"]


# ------------------------------------------------------------ el criterio

def test_un_criterio_no_verificable_se_propone_otro_y_no_se_compromete(
        intake_world, conn):
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        actor, rid, ws = _en_el_criterio(cur, intake_world)
        resultado = _decir(cur, actor, ws, _no_verificable())
        criterio = _campo(cur, rid, "acceptance_criterion")
        assert criterio["estado"] == "proposed"          # la persona no lo eligió
        assert criterio["valor"] == PROPUESTA
        assert _conjunto_activo(cur, rid) == "acceptance_criterion"
        assert _slot(cur, rid) is None
        assert PROPUESTA in resultado.text
        assert "cómo se comprueba" in resultado.text
        botones = [I.etiqueta_sin_icono(e) for e in _active_choices(cur, rid)]
        assert botones == ["Sí", "No", "Otra opción"]
    assert _incidentes_de(conn, I.ETAPA_VALOR_SIN_INTERPRETAR) == 0


def test_usar_la_propuesta_la_confirma(intake_world, conn):
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        actor, rid, ws = _en_el_criterio(cur, intake_world)
        _decir(cur, actor, ws, _no_verificable())
        _elegir(cur, actor, rid, "Sí")
        criterio = _campo(cur, rid, "acceptance_criterion")
        assert criterio["estado"] == "confirmed" and criterio["valor"] == PROPUESTA


@pytest.mark.parametrize("boton", ["Otra opción", "No"])
def test_si_prefiere_escribir_otro_y_insiste_con_su_texto_se_acepta(
        boton, intake_world, conn):
    """Una sola propuesta, sin bucle: lo que la persona escribe después se toma
    aunque el modelo vuelva a juzgarlo no verificable."""
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        actor, rid, ws = _en_el_criterio(cur, intake_world)
        _decir(cur, actor, ws, _no_verificable())
        _elegir(cur, actor, rid, boton)
        assert _slot(cur, rid) == "acceptance_criterion"
        resultado = _decir(cur, actor, ws, _no_verificable(
            "por fotos", "Se adjuntan fotos del tablero ya calibrado"),
            texto="por fotos", n=831)
        criterio = _campo(cur, rid, "acceptance_criterion")
        assert criterio["estado"] == "confirmed" and criterio["valor"] == "por fotos"
        assert _conjunto_activo(cur, rid) != "acceptance_criterion"
        assert resultado is not None


def test_un_criterio_verificable_se_acepta_tal_cual(intake_world, conn):
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        actor, rid, ws = _en_el_criterio(cur, intake_world)
        _decir(cur, actor, ws, {"texto": "Registro de calibración firmado",
                                "verificable": "si"}, texto="registro firmado")
        criterio = _campo(cur, rid, "acceptance_criterion")
        assert criterio["estado"] == "confirmed"
        assert criterio["valor"] == "Registro de calibración firmado"


def test_sin_juicio_del_modelo_el_texto_se_acepta_como_siempre(intake_world, conn):
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        actor, rid, ws = _en_el_criterio(cur, intake_world)
        _decir(cur, actor, ws, {"texto": "Prueba firmada"})
        assert _campo(cur, rid, "acceptance_criterion")["estado"] == "confirmed"


@pytest.mark.parametrize("propuesta", [
    None, "", "   ", "x" * 501, NO_SE])
def test_una_propuesta_que_no_sirve_no_se_ofrece_y_queda_registrado(
        propuesta, intake_world, conn):
    """El código valida la propuesta: vacía, demasiado larga o igual a lo que dijo
    la persona no sirve. Se toma lo que la persona escribió y queda registrado."""
    valor = {"texto": NO_SE, "verificable": "no"}
    if propuesta is not None:
        valor["propuesta"] = propuesta
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        actor, rid, ws = _en_el_criterio(cur, intake_world)
        _decir(cur, actor, ws, valor)
        criterio = _campo(cur, rid, "acceptance_criterion")
        assert criterio["estado"] == "confirmed" and criterio["valor"] == NO_SE
    assert _incidentes_de(conn, incidentes.ETAPA_CRITERIO_SIN_PROPUESTA) == 1


@pytest.mark.parametrize("campo", ["title", "description"])
def test_otros_campos_de_texto_no_se_juzgan(campo):
    esperado = gateway._pregunta_de(P.ModificacionAbierta(
        pregunta_id="p", herramienta=gateway._SENTINEL_ALTA_TEXTO_LIBRE,
        args={"campo": campo, "titulo": TITULO}, resumen="?")).valor_esperado
    assert esperado == ValorEsperado(TipoValor.TEXTO)


def test_el_criterio_declara_que_se_juzga_y_pasa_el_titulo():
    esperado = gateway._pregunta_de(P.ModificacionAbierta(
        pregunta_id="p", herramienta=gateway._SENTINEL_ALTA_TEXTO_LIBRE,
        args={"campo": "acceptance_criterion", "titulo": TITULO},
        resumen="?")).valor_esperado
    assert esperado == ValorEsperado(TipoValor.TEXTO, juzga_verificable=True,
                                     contexto=TITULO)


# ----------------------------------------------- el contrato del ruteo

JUZGA = ValorEsperado(TipoValor.TEXTO, juzga_verificable=True, contexto=TITULO)


def test_el_esquema_del_valor_pide_el_juicio_solo_cuando_se_juzga():
    con = llm._herramienta_del_ruteo("p", JUZGA)["input_schema"]["properties"]["valor"]
    assert con["properties"]["verificable"]["enum"] == ["si", "no"]
    assert con["properties"]["propuesta"]["type"] == "string"
    sin = llm._herramienta_del_ruteo(
        "p", ValorEsperado(TipoValor.TEXTO))["input_schema"]["properties"]["valor"]
    assert "verificable" not in sin["properties"] and "propuesta" not in sin["properties"]


def test_la_instruccion_del_criterio_lleva_el_titulo_y_la_regla():
    sistema = llm._sistema_del_ruteo("p", JUZGA)
    assert TITULO in sistema and "verificable" in sistema and "propuesta" in sistema
    assert "verificable" not in llm._sistema_del_ruteo(
        "p", ValorEsperado(TipoValor.TEXTO))


@pytest.mark.parametrize("valor", [
    {"texto": "x", "verificable": "si"},
    {"texto": "x", "verificable": "no", "propuesta": "Algo concreto"},
])
def test_el_valor_con_juicio_pasa_la_validacion_del_sobre(valor):
    assert llm._valor_o_vacio(valor) == valor


@pytest.mark.parametrize("valor", [
    {"texto": "x", "verificable": "quizás"},        # fuera de la lista cerrada
    {"texto": "x", "verificable": True},
    {"texto": "x", "propuesta": ""},
])
def test_un_juicio_fuera_de_la_lista_cerrada_es_sin_valor(valor):
    assert llm._valor_o_vacio(valor) == {}


# ---------------------------------- "Sí, es eso" también se juzga (F-B2)

class _Proveedor:
    def __init__(self, ruta=None, error=None):
        self.ruta, self.error, self.llamadas = ruta, error, []

    def route_intent(self, text, pendiente=None, valor_esperado=None):
        self.llamadas.append(valor_esperado)
        if self.error:
            raise self.error
        return self.ruta


def _abierta_del_criterio():
    return P.ModificacionAbierta(
        pregunta_id="p", herramienta=gateway._SENTINEL_ALTA_TEXTO_LIBRE,
        args={"campo": "acceptance_criterion", "titulo": TITULO}, resumen="¿Cómo?")


def _cal_hoy():
    from types import SimpleNamespace
    from zoneinfo import ZoneInfo
    return SimpleNamespace(zona=ZoneInfo("America/Argentina/Buenos_Aires"))


def test_confirmar_con_si_es_eso_pasa_por_el_juicio_del_modelo():
    ruta = IntentRoute(IntentAction.NORMAL_CONVERSATION,
                       respecto_pendiente=RespectoPendiente.RESPONDE,
                       valor=_no_verificable())
    proveedor = _Proveedor(ruta)
    route, error = gateway._ruta_de_lo_confirmado(
        proveedor, NO_SE, _abierta_del_criterio(), _cal_hoy(), NOW)
    assert error is None and route.valor == _no_verificable()
    assert proveedor.llamadas[0].juzga_verificable
    assert proveedor.llamadas[0].confirmado


@pytest.mark.parametrize("proveedor", [
    _Proveedor(error=RuntimeError("caído")),
    _Proveedor(IntentRoute(IntentAction.NORMAL_CONVERSATION,
                           respecto_pendiente=RespectoPendiente.RESPONDE)),
])
def test_si_el_modelo_no_puede_juzgar_lo_confirmado_se_toma_tal_cual(proveedor):
    route, error = gateway._ruta_de_lo_confirmado(
        proveedor, NO_SE, _abierta_del_criterio(), _cal_hoy(), NOW)
    assert error is None and route.valor == {"texto": NO_SE}


# ------------------------------------------------------- con la variante A

class _ModeloEco(_Eco):
    pass


def test_con_la_variante_a_el_modelo_redacta_la_propuesta_y_sale_tal_cual(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    modelo = _ModeloEco()
    with espacio(conn, ws) as cur:
        actor, rid, ws_ = _en_el_criterio(cur, intake_world)
    conn.commit()
    _a(conn, ws, monkeypatch, modelo)
    with espacio(conn, ws) as cur:
        resultado = _decir(cur, actor, ws, _no_verificable())
        assert PROPUESTA in resultado.text
    hechos = modelo.hechos[-1]
    assert hechos["valores_aceptados"] == [
        {"dato": "el criterio de aceptación", "mostrado": PROPUESTA}]
    assert "rechazo" in hechos
    assert [i["resultado"] for i in _intentos(conn, ws)] == ["aceptada"]
