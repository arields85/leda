"""Pruebas de la agregación de sesión del banco: tasa por escenario, fallas
por comprobación y latencias -- baseline sin umbrales inventados
(`docs/validation/README.md`, "Criterios de aprobación y baseline"). TDD
estricto.
"""

from __future__ import annotations

from tests.banco.reporte import EntradaReporte, armar_reporte, resumen_texto


def _entrada(escenario_id, indice, resultado, comprobaciones=(), latencia=1.0):
    return EntradaReporte(
        escenario_id=escenario_id, indice=indice, resultado=resultado,
        comprobaciones=list(comprobaciones), latencia_total_s=latencia,
        grabacion={"rutas": [], "respuestas": []})


def test_tasa_de_aprobacion_por_escenario():
    entradas = [
        _entrada("b-0001", 0, "aprobado"),
        _entrada("b-0001", 1, "aprobado"),
        _entrada("b-0001", 2, "falla"),
    ]
    r = armar_reporte(entradas, proveedor="nan", modelo="deepseek-v4-flash",
                      marca_de_tiempo="2026-09-23T00:00:00Z")
    datos = r["escenarios"]["b-0001"]
    assert datos["corridas"] == 3
    assert datos["conteos"] == {"aprobado": 2, "falla": 1, "no_concluyente": 0,
                                "bloqueado": 0}
    assert datos["tasa_aprobacion"] == 2 / 3


def test_fallas_por_comprobacion_se_cuentan():
    entradas = [
        _entrada("b-0002", 0, "falla",
                comprobaciones=[{"nombre": "herramientas", "resultado": "falla",
                                 "diferencia": "x"}]),
        _entrada("b-0002", 1, "falla",
                comprobaciones=[{"nombre": "herramientas", "resultado": "falla",
                                 "diferencia": "x"},
                                {"nombre": "accion_sin_herramienta",
                                 "resultado": "falla", "diferencia": "y"}]),
    ]
    r = armar_reporte(entradas, proveedor="nan", modelo="m", marca_de_tiempo="t")
    assert r["escenarios"]["b-0002"]["fallas_por_comprobacion"] == {
        "herramientas": 2, "accion_sin_herramienta": 1}


def test_latencias_min_mediana_max_por_escenario_y_globales():
    entradas = [
        _entrada("b-0001", 0, "aprobado", latencia=1.0),
        _entrada("b-0001", 1, "aprobado", latencia=3.0),
        _entrada("b-0001", 2, "aprobado", latencia=2.0),
    ]
    r = armar_reporte(entradas, proveedor="nan", modelo="m", marca_de_tiempo="t")
    lat = r["escenarios"]["b-0001"]["latencia_s"]
    assert lat == {"min": 1.0, "mediana": 2.0, "max": 3.0}
    assert r["latencia_global_s"] == {"min": 1.0, "mediana": 2.0, "max": 3.0}


def test_sin_corridas_no_rompe_el_calculo_de_latencias():
    r = armar_reporte([], proveedor="nan", modelo="m", marca_de_tiempo="t")
    assert r["latencia_global_s"] == {"min": None, "mediana": None, "max": None}
    assert r["escenarios"] == {}
    assert r["total_corridas"] == 0


def test_metadatos_de_proveedor_modelo_y_marca_de_tiempo():
    r = armar_reporte([], proveedor="nan", modelo="deepseek-v4-flash",
                      marca_de_tiempo="2026-09-23T12:00:00Z")
    assert r["proveedor"] == "nan"
    assert r["modelo"] == "deepseek-v4-flash"
    assert r["marca_de_tiempo"] == "2026-09-23T12:00:00Z"


def test_resumen_texto_incluye_escenario_y_tasa():
    entradas = [_entrada("b-0001", 0, "aprobado"), _entrada("b-0001", 1, "falla")]
    r = armar_reporte(entradas, proveedor="nan", modelo="deepseek-v4-flash",
                      marca_de_tiempo="t")
    texto = resumen_texto(r)
    assert "b-0001" in texto
    assert "nan/deepseek-v4-flash" in texto


# ---------------------------------------------------------------------------
# Agrupación de variantes (odd/tasks/banco-mensajes-humanos.md, T1): el
# reporte agrupa un escenario base y sus variantes -- tasa de aprobación por
# grupo además de las filas por escenario -- para comparar la redacción
# limpia contra la desprolija del mismo objetivo.
# ---------------------------------------------------------------------------


def test_grupo_agrega_base_y_variantes():
    entradas = [
        _entrada("b-0001", 0, "aprobado"),
        _entrada("b-0001", 1, "aprobado"),
        _entrada("b-0001-a", 0, "aprobado"),
        _entrada("b-0001-a", 1, "falla"),
        _entrada("b-0001-b", 0, "falla"),
    ]
    variantes = {"b-0001": None, "b-0001-a": "b-0001", "b-0001-b": "b-0001"}
    r = armar_reporte(entradas, proveedor="nan", modelo="m", marca_de_tiempo="t",
                      variantes=variantes)
    grupo = r["grupos"]["b-0001"]
    assert grupo["corridas"] == 5
    assert grupo["aprobado"] == 3
    assert grupo["tasa_aprobacion"] == 3 / 5
    assert grupo["escenarios"] == ["b-0001", "b-0001-a", "b-0001-b"]


def test_grupo_de_un_escenario_sin_variantes_es_el_mismo():
    entradas = [_entrada("b-0002", 0, "aprobado"), _entrada("b-0002", 1, "aprobado")]
    r = armar_reporte(entradas, proveedor="nan", modelo="m", marca_de_tiempo="t",
                      variantes={"b-0002": None})
    assert r["grupos"]["b-0002"]["corridas"] == 2
    assert r["grupos"]["b-0002"]["tasa_aprobacion"] == 1.0


def test_sin_variantes_declaradas_cada_escenario_es_su_propio_grupo():
    entradas = [_entrada("b-0001", 0, "aprobado"), _entrada("b-0002", 0, "falla")]
    r = armar_reporte(entradas, proveedor="nan", modelo="m", marca_de_tiempo="t")
    assert set(r["grupos"]) == {"b-0001", "b-0002"}
    assert r["grupos"]["b-0001"]["corridas"] == 1
    assert r["grupos"]["b-0002"]["corridas"] == 1


def test_resumen_texto_incluye_tasa_por_grupo_cuando_hay_variantes():
    entradas = [
        _entrada("b-0001", 0, "aprobado"),
        _entrada("b-0001-a", 0, "falla"),
    ]
    variantes = {"b-0001": None, "b-0001-a": "b-0001"}
    r = armar_reporte(entradas, proveedor="nan", modelo="m", marca_de_tiempo="t",
                      variantes=variantes)
    texto = resumen_texto(r)
    assert "grupo b-0001" in texto
