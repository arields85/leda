"""La frontera de las pruebas de garantías (E3-1).

`odd/tasks/motor-definitivo.md`, tarea E3-1: las pruebas de la capa sólida viven en
`tests/garantias/` y no dependen de la conversación de los flujos A y B, que se borra en la
E3-4. Dos controles, con el patrón de `prueba_chica/test_frontera.py`:

- Estático. Ningún archivo de `tests/garantias/`, ni los módulos auxiliares de `tests/` que
  esos archivos importan (en cadena, también los imports de dentro de funciones), importa un
  módulo de `PROHIBIDOS`. `tests/conftest.py` se carga siempre: sólo puede llegar a un
  prohibido desde las fixtures de `BORDES_CONOCIDOS`, que no hacen nada en las pruebas de esta
  carpeta. Esa lista sólo puede achicarse: si un borde desaparece, la prueba pide sacarlo; si
  aparece uno nuevo, falla.
- En ejecución. Un proceso aparte corre `pytest tests/garantias` (sin este archivo) y, al
  terminar, ningún módulo de `PROHIBIDOS` quedó cargado. Cubre lo que el control estático no
  ve: los imports en cadena dentro de `src/leda`, incluidos los que una función hace al
  correr.
"""

from __future__ import annotations

import ast
import json
import os
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[2]
PRUEBAS = RAIZ / "tests"
GARANTIAS = PRUEBAS / "garantias"
ESTE_ARCHIVO = pathlib.Path(__file__).resolve()

# La conversación de los flujos A y B, que se borró en la E3-4: no puede volver.
# `huerfanos` ya no está: no importa la conversación vieja y su garantía se queda (E3-2).
PROHIBIDOS = {"gateway", "ingreso_tareas", "agente", "contexto", "respuesta_unica",
              "deteccion_pregunta", "jev", "local"}

# (archivo, fixture que importa adentro, prohibido al que llega): por qué no molesta.
# Vacía desde la E3-4: `tests/conftest.py` ya no importa la conversación vieja.
BORDES_CONOCIDOS: dict[tuple[str, str | None, str], str] = {}

# Lo que corre el proceso aparte: las pruebas de garantías y, al final, qué quedó cargado.
_SONDA = r"""
import json
import sys

import pytest

PROHIBIDOS = json.loads(sys.argv[1])


class _Cuenta:
    pasaron = 0

    def pytest_runtest_logreport(self, report):
        if report.when == "call" and report.passed:
            self.pasaron += 1


cuenta = _Cuenta()
codigo = pytest.main(sys.argv[2:], plugins=[cuenta])
cargados = sorted(m for m in sys.modules
                  if m.split(".")[0] == "leda" and len(m.split(".")) > 1
                  and m.split(".")[1] in PROHIBIDOS)
print("SONDA " + json.dumps({"codigo": int(codigo), "pasaron": cuenta.pasaron,
                             "cargados": cargados}))
"""


def _paquete_de(ruta: pathlib.Path, raiz: pathlib.Path) -> tuple[str, ...]:
    """El paquete de un archivo, relativo a la raíz: `("tests", "garantias")`."""
    return ruta.parent.relative_to(raiz).parts


def _imports_de(ruta: pathlib.Path, raiz: pathlib.Path) -> list[tuple[str, str | None]]:
    """(módulo importado con su nombre completo, función de primer nivel que lo importa o
    `None`). Con `from a import b` cuenta `a` y también `a.b`, por si `b` es un módulo."""
    arbol = ast.parse(ruta.read_text("utf-8"))
    paquete = _paquete_de(ruta, raiz)
    hallados: list[tuple[str, str | None]] = []

    def visitar(nodo: ast.AST, funcion: str | None) -> None:
        for hijo in ast.iter_child_nodes(nodo):
            actual = funcion
            if funcion is None and isinstance(hijo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                actual = hijo.name
            if isinstance(hijo, ast.ImportFrom):
                if hijo.level:
                    # Relativo: `.` es el paquete del archivo; cada punto más sube uno.
                    base = list(paquete[:len(paquete) - (hijo.level - 1)])
                    partes = base + (hijo.module.split(".") if hijo.module else [])
                else:
                    partes = (hijo.module or "").split(".")
                modulo = ".".join(partes)
                if modulo:
                    hallados.append((modulo, actual))
                for alias in hijo.names:
                    hallados.append((f"{modulo}.{alias.name}" if modulo else alias.name,
                                     actual))
            elif isinstance(hijo, ast.Import):
                for alias in hijo.names:
                    hallados.append((alias.name, actual))
            visitar(hijo, actual)

    visitar(arbol, None)
    return hallados


def _prohibido(modulo: str) -> str | None:
    """El módulo de `PROHIBIDOS` que alcanza un import de `leda`, o `None`."""
    partes = modulo.split(".")
    if partes[0] == "leda" and len(partes) > 1 and partes[1] in PROHIBIDOS:
        return partes[1]
    return None


def _auxiliar(modulo: str, raiz: pathlib.Path) -> pathlib.Path | None:
    """El archivo de un módulo de `tests` (`tests.toques` → `tests/toques.py`), o `None` si
    el import no es de `tests` o nombra algo que no es un módulo."""
    partes = modulo.split(".")
    if partes[0] != "tests":
        return None
    archivo = raiz.joinpath(*partes).with_suffix(".py")
    if archivo.is_file():
        return archivo
    paquete = raiz.joinpath(*partes) / "__init__.py"
    return paquete if paquete.is_file() else None


def _archivos_de_partida(raiz: pathlib.Path) -> list[pathlib.Path]:
    """Los archivos de `tests/garantias/` y los `conftest.py` que pytest carga para ellos."""
    garantias = raiz / "tests" / "garantias"
    return sorted(garantias.rglob("*.py")) + [raiz / "tests" / "conftest.py"]


def _bordes_hacia_prohibidos(raiz: pathlib.Path = RAIZ):
    """Recorre los archivos de partida y, en cadena, los auxiliares de `tests` que importan.
    Devuelve los bordes `(archivo, función, prohibido)` y los archivos recorridos."""
    pendientes = [p for p in _archivos_de_partida(raiz) if p.is_file()]
    recorridos: set[pathlib.Path] = set()
    bordes: set[tuple[str, str | None, str]] = set()
    while pendientes:
        ruta = pendientes.pop()
        if ruta in recorridos:
            continue
        recorridos.add(ruta)
        relativa = ruta.relative_to(raiz).as_posix()
        for modulo, funcion in _imports_de(ruta, raiz):
            prohibido = _prohibido(modulo)
            if prohibido is not None:
                bordes.add((relativa, funcion, prohibido))
                continue
            auxiliar = _auxiliar(modulo, raiz)
            if auxiliar is not None:
                pendientes.append(auxiliar)
    return bordes, recorridos


def test_las_garantias_no_importan_la_conversacion_de_los_flujos_viejos():
    bordes, _ = _bordes_hacia_prohibidos()
    nuevos = sorted(map(str, bordes - set(BORDES_CONOCIDOS)))
    assert not nuevos, (
        "Las pruebas de garantías llegan a la conversación de los flujos viejos:\n  "
        + "\n  ".join(nuevos))


def test_los_bordes_conocidos_solo_pueden_achicarse():
    bordes, _ = _bordes_hacia_prohibidos()
    viejos = sorted(map(str, set(BORDES_CONOCIDOS) - bordes))
    assert not viejos, (
        "Estos bordes ya no existen: sacalos de BORDES_CONOCIDOS:\n  " + "\n  ".join(viejos))


def test_el_recorrido_sigue_auxiliares_e_imports_dentro_de_funciones(tmp_path):
    """Control del propio recorrido, sobre un árbol de juguete: un auxiliar de `tests` que
    una prueba importa adentro de una función, con un import relativo, cuenta entero."""
    archivos = {
        "tests/__init__.py": "",
        "tests/conftest.py": "",
        "tests/garantias/__init__.py": "",
        "tests/garantias/test_algo.py":
            "def test_algo():\n    from tests.ayuda import armar\n",
        "tests/ayuda.py": "from .otra import x\n",
        "tests/otra.py": "def x():\n    from leda import gateway\n",
    }
    for nombre, codigo in archivos.items():
        ruta = tmp_path / nombre
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(codigo, "utf-8")
    bordes, recorridos = _bordes_hacia_prohibidos(tmp_path)
    assert bordes == {("tests/otra.py", "x", "gateway")}
    assert tmp_path / "tests" / "ayuda.py" in recorridos


def test_correr_las_garantias_no_carga_la_conversacion_de_los_flujos_viejos():
    """En un proceso aparte, para que lo que ya cargó esta sesión de pytest no cuente."""
    entorno = {**os.environ, "PYTHONPATH": os.pathsep.join(
        filter(None, [str(RAIZ / "src"), str(RAIZ), os.environ.get("PYTHONPATH")]))}
    proceso = subprocess.run(
        [sys.executable, "-c", _SONDA, json.dumps(sorted(PROHIBIDOS)),
         str(GARANTIAS), "-q", "-p", "no:cacheprovider", "--ignore", str(ESTE_ARCHIVO)],
        cwd=RAIZ, env=entorno, capture_output=True, text=True, encoding="utf-8",
        timeout=1800)
    lineas = [l for l in proceso.stdout.splitlines() if l.startswith("SONDA ")]
    assert lineas, (
        "La sonda no informó nada.\n" + proceso.stdout[-3000:] + proceso.stderr[-3000:])
    resultado = json.loads(lineas[-1].removeprefix("SONDA "))
    # Una corrida que no pasó ninguna prueba no prueba nada sobre lo que se carga al correr.
    assert resultado["pasaron"] > 0, proceso.stdout[-3000:]
    assert resultado["codigo"] == 0, (
        "Las pruebas de garantías fallaron en el proceso aparte:\n" + proceso.stdout[-3000:])
    assert resultado["cargados"] == [], (
        "Correr las pruebas de garantías cargó la conversación de los flujos viejos: "
        + ", ".join(resultado["cargados"]))
