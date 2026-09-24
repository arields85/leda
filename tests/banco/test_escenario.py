"""Pruebas del cargador de escenarios del banco (formato YAML, protocolo
`docs/validation/README.md`, "Estructura mínima de un escenario"). TDD
estricto."""

from __future__ import annotations

import pytest
import yaml

from tests.banco.escenario import (
    Escenario,
    EscenarioInvalido,
    cargar_escenario,
    cargar_escenarios,
)

_MINIMO = {
    "id": "b-0099",
    "objetivo": "Observar que responde con sus tareas pendientes.",
    "actor": "Marcos Tarquini",
    "mensajes": ["che, ¿qué tengo pendiente esta semana?"],
    "herramientas_esperadas": ["consultar_tareas"],
    "severidad": "media",
}


def _escribir(tmp_path, datos, nombre="escenario.yaml"):
    ruta = tmp_path / nombre
    ruta.write_text(yaml.safe_dump(datos, allow_unicode=True), "utf-8")
    return ruta


def test_carga_el_minimo_con_valores_por_defecto(tmp_path):
    ruta = _escribir(tmp_path, _MINIMO)
    e = cargar_escenario(ruta)
    assert isinstance(e, Escenario)
    assert e.id == "b-0099"
    assert e.actor == "Marcos Tarquini"
    assert e.mensajes == ["che, ¿qué tengo pendiente esta semana?"]
    assert e.herramientas_esperadas == ("consultar_tareas",)
    assert e.herramientas_prohibidas == ()
    assert e.nombres_permitidos == ()
    assert e.precondiciones == {}
    assert e.severidad == "media"
    assert e.efectos == {}
    assert e.respuesta_menciona == ()
    assert e.respuesta_no_contiene_patron == ()


def test_carga_con_precondiciones_completas(tmp_path):
    datos = dict(_MINIMO)
    datos["precondiciones"] = {
        "tareas": [{"id": "t1", "titulo": "Programar PLC", "area": "ot",
                    "responsable": "Marcos Tarquini"}],
        "bloqueos": [{"tarea": "t1", "causa": "falta el switch"}],
        "dependencias": [],
    }
    ruta = _escribir(tmp_path, datos)
    e = cargar_escenario(ruta)
    assert e.precondiciones["tareas"][0]["titulo"] == "Programar PLC"


@pytest.mark.parametrize("campo", ["id", "objetivo", "actor", "mensajes"])
def test_falta_un_campo_obligatorio_es_invalido(tmp_path, campo):
    datos = dict(_MINIMO)
    del datos[campo]
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)


def test_mensajes_vacio_es_invalido(tmp_path):
    datos = dict(_MINIMO)
    datos["mensajes"] = []
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)


def test_severidad_desconocida_es_invalida(tmp_path):
    datos = dict(_MINIMO)
    datos["severidad"] = "catastrofica"
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)


def test_id_repetido_no_da_pistas_pero_tiene_que_estar(tmp_path):
    datos = dict(_MINIMO)
    datos["id"] = ""
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)


def test_cargar_escenarios_de_un_directorio(tmp_path):
    _escribir(tmp_path, _MINIMO, "a.yaml")
    otro = dict(_MINIMO)
    otro["id"] = "b-0098"
    _escribir(tmp_path, otro, "b.yaml")
    (tmp_path / "no-es-yaml.txt").write_text("ignorar", "utf-8")

    escenarios = cargar_escenarios(tmp_path)
    assert {e.id for e in escenarios} == {"b-0099", "b-0098"}


def test_cargar_escenarios_ids_duplicados_es_invalido(tmp_path):
    _escribir(tmp_path, _MINIMO, "a.yaml")
    _escribir(tmp_path, _MINIMO, "b.yaml")
    with pytest.raises(EscenarioInvalido):
        cargar_escenarios(tmp_path)


# ---------------------------------------------------------------------------
# Defecto de revisión: el escenario no declaraba el estado ni el efecto
# esperados (sólo el nombre de la herramienta), así que "sin invertir la
# dependencia" o "la tarea correcta" nunca se verificaba.
# ---------------------------------------------------------------------------


def test_carga_efectos_completos(tmp_path):
    datos = dict(_MINIMO)
    datos["efectos"] = {
        "tareas": {"t1": {"estado": "bloqueada"}},
        "bloqueos_abiertos": {"t1": 1},
        "dependencias": [{"origen": "t1", "destino": "t2", "tipo": "bloqueante"}],
        "conteos_delta": {"blocker": 1, "task_state_event": 1},
    }
    ruta = _escribir(tmp_path, datos)
    e = cargar_escenario(ruta)
    assert e.efectos["tareas"]["t1"]["estado"] == "bloqueada"
    assert e.efectos["conteos_delta"]["blocker"] == 1


def test_efectos_no_es_un_mapeo_es_invalido(tmp_path):
    datos = dict(_MINIMO)
    datos["efectos"] = ["no es un mapeo"]
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)


def test_carga_respuesta_menciona_y_no_contiene_patron(tmp_path):
    datos = dict(_MINIMO)
    datos["respuesta_menciona"] = ["PLC", "comunicaciones industriales"]
    datos["respuesta_no_contiene_patron"] = [r"\d{7,}", r"[\w.+-]+@[\w-]+\.\w+"]
    ruta = _escribir(tmp_path, datos)
    e = cargar_escenario(ruta)
    assert e.respuesta_menciona == ("PLC", "comunicaciones industriales")
    assert e.respuesta_no_contiene_patron == (r"\d{7,}", r"[\w.+-]+@[\w-]+\.\w+")


def test_respuesta_menciona_no_es_una_lista_es_invalido(tmp_path):
    datos = dict(_MINIMO)
    datos["respuesta_menciona"] = "PLC"
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)


def test_respuesta_no_contiene_patron_no_es_una_lista_es_invalido(tmp_path):
    datos = dict(_MINIMO)
    datos["respuesta_no_contiene_patron"] = r"\d{7,}"
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)


# ---------------------------------------------------------------------------
# variante_de / debe_preguntar / permite_borrador_de_tarea
# (odd/tasks/banco-mensajes-humanos.md, T1): agrupar variantes desprolijas en
# el reporte y la comprobación nueva "ante la duda, preguntó".
# ---------------------------------------------------------------------------


def test_carga_sin_variante_de_ni_debe_preguntar_usa_los_valores_por_defecto(tmp_path):
    ruta = _escribir(tmp_path, _MINIMO)
    e = cargar_escenario(ruta)
    assert e.variante_de is None
    assert e.debe_preguntar is False
    assert e.permite_borrador_de_tarea is False


def test_carga_variante_de_debe_preguntar_y_permite_borrador_de_tarea(tmp_path):
    datos = dict(_MINIMO)
    datos["variante_de"] = "b-0001"
    datos["debe_preguntar"] = True
    datos["permite_borrador_de_tarea"] = True
    ruta = _escribir(tmp_path, datos)
    e = cargar_escenario(ruta)
    assert e.variante_de == "b-0001"
    assert e.debe_preguntar is True
    assert e.permite_borrador_de_tarea is True


def test_variante_de_vacio_es_invalido(tmp_path):
    datos = dict(_MINIMO)
    datos["variante_de"] = ""
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)


def test_variante_de_no_es_texto_es_invalido(tmp_path):
    datos = dict(_MINIMO)
    datos["variante_de"] = 123
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)


def test_debe_preguntar_no_es_booleano_es_invalido(tmp_path):
    datos = dict(_MINIMO)
    datos["debe_preguntar"] = "si"
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)


def test_permite_borrador_de_tarea_no_es_booleano_es_invalido(tmp_path):
    datos = dict(_MINIMO)
    datos["permite_borrador_de_tarea"] = "si"
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)


def test_cargar_escenarios_variante_de_referencia_un_id_existente(tmp_path):
    base = dict(_MINIMO)
    _escribir(tmp_path, base, "a.yaml")
    variante = dict(_MINIMO)
    variante["id"] = "b-0098"
    variante["variante_de"] = "b-0099"
    _escribir(tmp_path, variante, "b.yaml")

    escenarios = cargar_escenarios(tmp_path)
    por_id = {e.id: e for e in escenarios}
    assert por_id["b-0098"].variante_de == "b-0099"


def test_cargar_escenarios_variante_de_id_inexistente_es_invalido(tmp_path):
    base = dict(_MINIMO)
    _escribir(tmp_path, base, "a.yaml")
    variante = dict(_MINIMO)
    variante["id"] = "b-0098"
    variante["variante_de"] = "b-no-existe"
    _escribir(tmp_path, variante, "b.yaml")

    with pytest.raises(EscenarioInvalido):
        cargar_escenarios(tmp_path)


# ---------------------------------------------------------------------------
# aclaracion_esperada (T6, `aclaracion-con-botones`): qué candidatas tiene
# que ofrecer una referencia ambigua y cuál tocar, para que el corredor
# pueda seguir la aclaración con botones en vez de quedarse en la pregunta.
# ---------------------------------------------------------------------------


def test_carga_sin_aclaracion_esperada_usa_diccionario_vacio(tmp_path):
    ruta = _escribir(tmp_path, _MINIMO)
    e = cargar_escenario(ruta)
    assert e.aclaracion_esperada == {}


def test_carga_aclaracion_esperada_completa(tmp_path):
    datos = dict(_MINIMO)
    datos["aclaracion_esperada"] = {
        "candidatas": ["Cablear tablero máq. 3", "Revisar tablero máq. 4"],
        "elegir": "Cablear tablero máq. 3",
    }
    ruta = _escribir(tmp_path, datos)
    e = cargar_escenario(ruta)
    assert e.aclaracion_esperada["candidatas"] == [
        "Cablear tablero máq. 3", "Revisar tablero máq. 4"]
    assert e.aclaracion_esperada["elegir"] == "Cablear tablero máq. 3"


def test_aclaracion_esperada_no_es_mapeo_es_invalido(tmp_path):
    datos = dict(_MINIMO)
    datos["aclaracion_esperada"] = ["no es un mapeo"]
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)


def test_aclaracion_esperada_candidatas_vacia_es_invalido(tmp_path):
    datos = dict(_MINIMO)
    datos["aclaracion_esperada"] = {"candidatas": [], "elegir": "Lo que sea"}
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)


def test_aclaracion_esperada_sin_elegir_es_invalido(tmp_path):
    datos = dict(_MINIMO)
    datos["aclaracion_esperada"] = {"candidatas": ["Tarea A", "Tarea B"]}
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)


def test_aclaracion_esperada_elegir_fuera_de_candidatas_es_invalido(tmp_path):
    datos = dict(_MINIMO)
    datos["aclaracion_esperada"] = {
        "candidatas": ["Tarea A", "Tarea B"], "elegir": "Tarea C"}
    ruta = _escribir(tmp_path, datos)
    with pytest.raises(EscenarioInvalido):
        cargar_escenario(ruta)
