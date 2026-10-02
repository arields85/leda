"""Qué valor espera cada pregunta pendiente y cómo llega al ruteo (ADR 0014, M1).

Cada adaptador de `gateway._pregunta_de` declara el tipo de valor que espera
(`fecha | opcion | texto | entidad | ninguno`) y, si ofrece botones, las
opciones con sus ids. El turno se lo pasa al ruteo junto con el día de hoy en
la zona del espacio. No cambia qué consume cada pregunta (ADR 0013 regla 1):
sólo le da al modelo con qué completar `valor`. Sin base: las preguntas se
arman a mano, como en `test_alta_eleccion_confirmacion`.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from leda import gateway, pendientes as P
from leda.ingreso_tareas import FREE_TEXT_NAMES, MODIFY_PICKER_KIND
from leda.llm import IntentAction, IntentRoute, ProveedorGuionado
from leda.valores import Opcion, TipoValor, ValorEsperado


def _abierta(herramienta, args=None, resumen="¿Cuál?"):
    return P.ModificacionAbierta(
        pregunta_id="p1", herramienta=herramienta, args=args or {},
        resumen=resumen)


def _esperado(abierta):
    return gateway._pregunta_de(abierta).valor_esperado


# --- alta guiada --------------------------------------------------------------

@pytest.mark.parametrize("campo, tipo", [
    ("title", TipoValor.TEXTO),
    ("description", TipoValor.TEXTO),
    ("objective", TipoValor.ENTIDAD),
    ("responsible", TipoValor.ENTIDAD),
    ("area", TipoValor.ENTIDAD),
    ("due_date", TipoValor.FECHA),
])
def test_cada_campo_de_texto_libre_del_alta_declara_su_tipo(campo, tipo):
    abierta = _abierta(gateway._SENTINEL_ALTA_TEXTO_LIBRE,
                       {"campo": campo, "titulo": None})
    assert _esperado(abierta) == ValorEsperado(tipo)


def test_el_criterio_de_aceptacion_es_texto_y_se_juzga_si_es_verificable():
    abierta = _abierta(gateway._SENTINEL_ALTA_TEXTO_LIBRE,
                       {"campo": "acceptance_criterion", "titulo": None})
    assert _esperado(abierta) == ValorEsperado(TipoValor.TEXTO,
                                               juzga_verificable=True)


def test_todos_los_campos_del_alta_declaran_un_tipo():
    for campo in FREE_TEXT_NAMES:
        abierta = _abierta(gateway._SENTINEL_ALTA_TEXTO_LIBRE,
                           {"campo": campo, "titulo": None})
        assert _esperado(abierta) is not None, campo


def test_la_eleccion_del_alta_ofrece_sus_opciones_con_ids():
    abierta = _abierta(gateway._SENTINEL_ALTA_ELECCION, {
        "campo": "area", "titulo": "T", "opciones": ["Cocina", "Taller"],
        "clase": None})
    assert _esperado(abierta) == ValorEsperado(
        TipoValor.OPCION, (Opcion("1", "Cocina"), Opcion("2", "Taller")))


def test_el_selector_de_que_modificar_es_una_eleccion():
    abierta = _abierta(gateway._SENTINEL_ALTA_ELECCION, {
        "campo": None, "titulo": "T", "opciones": ["El título", "La fecha"],
        "clase": MODIFY_PICKER_KIND})
    esperado = _esperado(abierta)
    assert esperado.tipo is TipoValor.OPCION
    assert [o.etiqueta for o in esperado.opciones] == ["El título", "La fecha"]


def test_una_eleccion_sin_opciones_no_espera_valor():
    abierta = _abierta(gateway._SENTINEL_ALTA_ELECCION,
                       {"campo": None, "titulo": "T"})
    assert _esperado(abierta) == ValorEsperado(TipoValor.NINGUNO)


@pytest.mark.parametrize("revision", [False, True])
def test_la_confirmacion_del_borrador_no_espera_valor(revision):
    args = {"titulo": "T"}
    if revision:
        args["revision"] = True
    abierta = _abierta(gateway._SENTINEL_ALTA_CONFIRMACION, args)
    assert _esperado(abierta) == ValorEsperado(TipoValor.NINGUNO)


# --- dato de una acción del menú ------------------------------------------------

@pytest.mark.parametrize("accion", sorted(gateway._PREGUNTAS_DATO_MENU))
def test_el_dato_de_una_accion_del_menu_es_un_texto(accion):
    abierta = _abierta(P.SENTINEL_DATO_MENU_TAREA,
                       {"accion": accion, "titulo": "Revisar PLC"})
    assert _esperado(abierta) == ValorEsperado(TipoValor.TEXTO)


def test_un_dato_del_menu_con_accion_desconocida_es_un_texto():
    abierta = _abierta(P.SENTINEL_DATO_MENU_TAREA,
                       {"accion": "otra", "titulo": "Revisar PLC"})
    assert _esperado(abierta) == ValorEsperado(TipoValor.TEXTO)


# --- otras ramas -----------------------------------------------------------------

def test_la_eleccion_con_botones_ofrece_sus_opciones_con_ids():
    abierta = _abierta(gateway._SENTINEL_ELECCION, {
        "herramienta": "actualizar_estado", "argumentos": {},
        "campo": None, "opciones": ["Revisar PLC", "Revisar tablero"]})
    assert _esperado(abierta) == ValorEsperado(
        TipoValor.OPCION,
        (Opcion("1", "Revisar PLC"), Opcion("2", "Revisar tablero")))


def test_la_vista_previa_de_un_cambio_no_espera_valor():
    abierta = _abierta(gateway._SENTINEL_VISTA_PREVIA, {
        "herramienta": "actualizar_estado", "argumentos": {}})
    assert _esperado(abierta) == ValorEsperado(TipoValor.NINGUNO)


def test_ninguna_lo_escribo_espera_la_referencia_como_entidad():
    abierta = _abierta(gateway._SENTINEL_ACLARACION, {
        "referencia_actual": "el plc", "mensaje": "cerrá lo del plc"})
    assert _esperado(abierta) == ValorEsperado(TipoValor.ENTIDAD)


def test_la_correccion_de_modificar_espera_un_texto():
    abierta = _abierta("actualizar_estado", {"tarea_id": "t1"},
                       resumen="Voy a cerrar la tarea.")
    assert _esperado(abierta) == ValorEsperado(TipoValor.TEXTO)


# --- el ruteo recibe el valor esperado con el día de hoy ----------------------

BA = ZoneInfo("America/Argentina/Buenos_Aires")


class _Cal:
    zona = BA


def test_el_valor_esperado_lleva_el_dia_de_hoy_de_la_zona_del_espacio():
    # 01:30 UTC del 1/10 es todavía el 30/9 en Buenos Aires.
    ahora = datetime(2026, 10, 1, 1, 30, tzinfo=timezone.utc)
    esperado = gateway._valor_esperado_de(
        ValorEsperado(TipoValor.FECHA), _Cal(), ahora)
    assert esperado == ValorEsperado(TipoValor.FECHA, hoy=date(2026, 9, 30))


def test_sin_valor_esperado_no_hay_nada_que_completar():
    assert gateway._valor_esperado_de(None, _Cal(), datetime.now(timezone.utc)) is None


def test_el_turno_con_pregunta_pendiente_pasa_el_valor_esperado_al_ruteo(
        monkeypatch):
    llamadas = []

    def rutear(proveedor, texto, pendiente=None, valor_esperado=None,
               historial=None):
        llamadas.append((texto, pendiente, valor_esperado))
        return None, RuntimeError("sin ruteo")

    avisos = []
    monkeypatch.setattr(gateway, "_rutear", rutear)
    monkeypatch.setattr(gateway, "_avisar_ruteo_caido",
                        lambda *a, **k: avisos.append(a))
    abierta = _abierta(gateway._SENTINEL_ALTA_TEXTO_LIBRE,
                       {"campo": "due_date", "titulo": None})
    ahora = datetime(2026, 9, 30, 15, 0, tzinfo=timezone.utc)

    resultado = gateway._atender_pregunta_pendiente(
        None, None, "4de octubre", abierta, ProveedorGuionado(guion=[]), _Cal(),
        1, "ws", ahora)

    assert resultado is None and len(avisos) == 1
    (texto, pendiente, esperado), = llamadas
    assert texto == "4de octubre"
    assert pendiente == gateway._pregunta_de(abierta).para_ruteo
    assert esperado == ValorEsperado(TipoValor.FECHA, hoy=date(2026, 9, 30))


def test_la_descripcion_para_el_ruteo_no_cambia():
    # El valor esperado viaja aparte: `para_ruteo` sigue siendo lo de siempre.
    abierta = _abierta(gateway._SENTINEL_ALTA_TEXTO_LIBRE,
                       {"campo": "due_date", "titulo": None})
    pregunta = gateway._pregunta_de(abierta)
    assert pregunta.para_ruteo == gateway._para_ruteo(
        "la fecha objetivo de la tarea nueva, un dato del alta guiada que se "
        "le pidió", abierta.resumen)
