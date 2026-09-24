"""Fixtures y opciones de pytest del banco conversacional.

Las corridas contra el modelo real (`test_banco.py`, marcador `modelo_real`)
quedan fuera de la suite por defecto (`pyproject.toml`, `addopts`). Este
archivo agrega las opciones `--banco-*`, arma el proveedor real a partir de
ellas, y junta el reporte de sesión al terminar (sólo cuando algo se corrió
contra un modelo real: la suite por defecto no escribe nada acá).
"""

from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

import pytest

from tests.banco.escenario import cargar_escenarios
from tests.banco.reporte import EntradaReporte, armar_reporte, resumen_texto

DIR_BANCO = pathlib.Path(__file__).resolve().parent
DIR_ESCENARIOS = DIR_BANCO / "escenarios"
DIR_REPLAYS = DIR_BANCO / "replays"
DIR_REPORTES = DIR_BANCO / "reportes"   # git-ignored: ver .gitignore

_ENTRADAS_SESION: list[EntradaReporte] = []


def pytest_addoption(parser: pytest.Parser) -> None:
    grupo = parser.getgroup("banco", "Banco conversacional con el modelo real")
    grupo.addoption("--banco-n", action="store", type=int, default=3,
                    help="Corridas por escenario del banco (default: 3).")
    grupo.addoption("--banco-proveedor", action="store", default="nan",
                    help="Proveedor del modelo real del banco (default: nan).")
    grupo.addoption("--banco-modelo", action="store", default="deepseek-v4-flash",
                    help="Modelo real del banco (default: deepseek-v4-flash).")
    grupo.addoption("--banco-escenario", action="store", default=None,
                    help="Restringe el banco a un único ID de escenario.")


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "escenario_y_corrida" in metafunc.fixturenames:
        n = metafunc.config.getoption("--banco-n")
        filtro = metafunc.config.getoption("--banco-escenario")
        escenarios = cargar_escenarios(DIR_ESCENARIOS)
        if filtro:
            escenarios = [e for e in escenarios if e.id == filtro]
        casos = [(e, i) for e in escenarios for i in range(n)]
        metafunc.parametrize(
            "escenario_y_corrida", casos,
            ids=[f"{e.id}-{i}" for e, i in casos] or ["sin-escenarios"])

    if "archivo_replay" in metafunc.fixturenames:
        archivos = sorted(DIR_REPLAYS.glob("*.json"))
        metafunc.parametrize("archivo_replay", archivos, ids=[a.stem for a in archivos])


@pytest.fixture
def proveedor_real(request: pytest.FixtureRequest):
    """Arma el proveedor real desde `--banco-proveedor`/`--banco-modelo` y la
    credencial de `prisma.config.config`. Nunca desde `model_config`: el
    proveedor de la corrida lo decide el banco, no el espacio."""
    from prisma import llm
    from prisma.config import config

    if not config.llm_api_key:
        pytest.skip(
            "Falta la credencial del modelo (PRISMA_LLM_API_KEY): no se puede "
            "correr el banco contra un modelo real.")

    proveedor = request.config.getoption("--banco-proveedor")
    modelo = request.config.getoption("--banco-modelo")

    if proveedor == "gemini":
        return llm.ProveedorGemini(modelo, config.llm_api_key)
    if proveedor == "anthropic":
        return llm.ProveedorAnthropic(modelo, config.llm_api_key)
    base = llm.BASE_URLS.get(proveedor)
    if not base:
        pytest.fail(f"No sé a qué dirección hablarle a '{proveedor}' (ver llm.BASE_URLS).")
    return llm.ProveedorCompatible(modelo, config.llm_api_key, base)


def registrar_entrada_sesion(entrada: EntradaReporte) -> None:
    """Junta una corrida evaluada para el reporte de fin de sesión.
    La llama `test_banco.py`, nunca `test_replays.py` -- un replay no es una
    corrida nueva del banco, es la regresión de una que ya se reportó."""
    _ENTRADAS_SESION.append(entrada)


def guardar_candidato_replay(entrada: EntradaReporte, escenario_id: str) -> pathlib.Path:
    """Guarda una corrida no aprobada como candidato de replay en el
    directorio de reportes (git-ignored). Promoverla a regresión versionada
    -- copiarla a `tests/banco/replays/` -- es una decisión humana, no
    automática (feature doc, alcance: 'cada falla real se registra y se
    trata como unidad propia')."""
    DIR_REPORTES.mkdir(exist_ok=True)
    datos = {
        "escenario_id": escenario_id,
        "resultado_esperado": entrada.resultado,
        "comprobaciones": entrada.comprobaciones,
        "motivo_bloqueo": entrada.motivo_bloqueo,
        "grabacion": entrada.grabacion,
    }
    ruta = DIR_REPORTES / f"replay-candidato-{escenario_id}-{entrada.indice}.json"
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), "utf-8")
    return ruta


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if not _ENTRADAS_SESION:
        return
    DIR_REPORTES.mkdir(exist_ok=True)
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    # `variante_de` agrupa una redacción desprolija con su escenario base en
    # el reporte (odd/tasks/banco-mensajes-humanos.md, T1). Se recarga acá
    # -- no en cada corrida -- porque el reporte de sesión junta corridas de
    # todos los escenarios recién al final.
    variantes = {e.id: e.variante_de for e in cargar_escenarios(DIR_ESCENARIOS)}
    reporte = armar_reporte(
        _ENTRADAS_SESION,
        proveedor=session.config.getoption("--banco-proveedor"),
        modelo=session.config.getoption("--banco-modelo"),
        marca_de_tiempo=ahora, variantes=variantes)
    nombre = ahora.replace(":", "").replace("-", "")
    ruta = DIR_REPORTES / f"banco-{nombre}.json"
    ruta.write_text(json.dumps(reporte, ensure_ascii=False, indent=2), "utf-8")

    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    if reporter is not None:
        reporter.write_sep("=", "banco conversacional")
        reporter.write_line(resumen_texto(reporte))
        reporter.write_line(f"reporte completo: {ruta}")
