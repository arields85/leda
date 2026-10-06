"""La frontera de la entrada HTTP y del ciclo de fondo (E3-2).

`odd/tasks/motor-definitivo.md`, tarea E3-2: la entrada HTTP (`leda.entrada`), el ciclo de
fondo (`leda.ciclo`), el reloj (`leda.reloj`) y el barrido de mensajes huérfanos
(`leda.huerfanos`) son de la capa sólida y no dependen de la conversación de los flujos A y
B, que se borra en la E3-4. Dos controles, con el patrón de `test_frontera.py`:

- Estático. Desde esos cuatro módulos se recorren, en cadena, los módulos de `leda` que
  importan, también los imports de dentro de funciones. Ningún import de nivel de módulo
  llega a un módulo de `PROHIBIDOS`; los de dentro de funciones sólo si están en
  `BORDES_CONOCIDOS`, cada uno con su motivo y la tarea que lo retira. Esa lista sólo puede
  achicarse: si un borde desaparece, la prueba pide sacarlo; si aparece uno nuevo, falla.
- En ejecución. Un proceso aparte importa los cuatro módulos y, al terminar, ningún módulo de
  `PROHIBIDOS` quedó cargado.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

from tests.garantias.test_frontera import _imports_de

RAIZ = pathlib.Path(__file__).resolve().parents[2]

# La conversación de los flujos A y B, que se borró en la E3-4: no puede volver.
PROHIBIDOS = {"gateway", "ingreso_tareas", "agente", "contexto", "respuesta_unica",
              "deteccion_pregunta", "jev", "local"}

# Los módulos de la capa sólida desde los que se recorre.
INICIOS = ("entrada", "ciclo", "reloj", "huerfanos")

# (archivo, función que importa adentro, prohibido al que llega): por qué sigue. Vacía
# desde la E3-4, que borró los flujos A y B y cortó los cuatro bordes que quedaban.
BORDES_CONOCIDOS: dict[tuple[str, str | None, str], str] = {}

# Lo que corre el proceso aparte: importa los inicios y dice qué quedó cargado.
_SONDA = r"""
import importlib
import json
import sys

PROHIBIDOS, INICIOS = json.loads(sys.argv[1]), json.loads(sys.argv[2])
for nombre in INICIOS:
    importlib.import_module("leda." + nombre)
cargados = sorted(m for m in sys.modules
                  if m.split(".")[0] == "leda" and len(m.split(".")) > 1
                  and m.split(".")[1] in PROHIBIDOS)
print("SONDA " + json.dumps(cargados))
"""


def _prohibido(modulo: str) -> str | None:
    """El módulo de `PROHIBIDOS` que alcanza un import de `leda`, o `None`."""
    partes = modulo.split(".")
    if partes[0] == "leda" and len(partes) > 1 and partes[1] in PROHIBIDOS:
        return partes[1]
    return None


def _archivo_de(modulo: str, fuentes: pathlib.Path) -> pathlib.Path | None:
    """El archivo de un módulo de `leda` (`leda.ciclo` → `src/leda/ciclo.py`), o `None` si
    el import no es de `leda` o nombra algo que no es un módulo (`leda.ciclo.Ciclo`)."""
    partes = modulo.split(".")
    if partes[0] != "leda":
        return None
    archivo = fuentes.joinpath(*partes).with_suffix(".py")
    if archivo.is_file():
        return archivo
    paquete = fuentes.joinpath(*partes) / "__init__.py"
    return paquete if paquete.is_file() else None


def _bordes_desde_la_capa_solida(raiz: pathlib.Path = RAIZ, inicios=INICIOS):
    """Recorre los inicios y, en cadena, los módulos de `leda` que importan (también desde
    adentro de funciones). Devuelve los bordes `(archivo, función, prohibido)`, los archivos
    recorridos y los inicios que no existen."""
    fuentes = raiz / "src"
    faltantes = [n for n in inicios if not (fuentes / "leda" / f"{n}.py").is_file()]
    pendientes = [fuentes / "leda" / "__init__.py"] + [
        fuentes / "leda" / f"{n}.py" for n in inicios if n not in faltantes]
    recorridos: set[pathlib.Path] = set()
    bordes: set[tuple[str, str | None, str]] = set()
    while pendientes:
        ruta = pendientes.pop()
        if ruta in recorridos or not ruta.is_file():
            continue
        recorridos.add(ruta)
        relativa = ruta.relative_to(raiz).as_posix()
        for modulo, funcion in _imports_de(ruta, fuentes):
            prohibido = _prohibido(modulo)
            if prohibido is not None:
                bordes.add((relativa, funcion, prohibido))
                continue
            archivo = _archivo_de(modulo, fuentes)
            if archivo is not None:
                pendientes.append(archivo)
    return bordes, recorridos, faltantes


def test_la_capa_solida_existe_entera():
    _, _, faltantes = _bordes_desde_la_capa_solida()
    assert not faltantes, "No existen estos módulos de la capa sólida: " + ", ".join(
        f"leda.{n}" for n in faltantes)


def test_la_entrada_y_el_ciclo_no_importan_la_conversacion_de_los_flujos_viejos():
    bordes, _, _ = _bordes_desde_la_capa_solida()
    nuevos = sorted(map(str, bordes - set(BORDES_CONOCIDOS)))
    assert not nuevos, (
        "La entrada, el ciclo, el reloj o el barrido de huérfanos llegan a la conversación "
        "de los flujos viejos:\n  " + "\n  ".join(nuevos))


def test_los_bordes_conocidos_de_la_capa_solida_solo_pueden_achicarse():
    bordes, _, _ = _bordes_desde_la_capa_solida()
    viejos = sorted(map(str, set(BORDES_CONOCIDOS) - bordes))
    assert not viejos, (
        "Estos bordes ya no existen: sacalos de BORDES_CONOCIDOS:\n  " + "\n  ".join(viejos))


def test_ningun_borde_conocido_es_un_import_de_nivel_de_modulo():
    """Un import de nivel de módulo carga la conversación vieja con sólo importar el
    módulo: ése no se tolera nunca, ni anotado."""
    de_modulo = sorted(map(str, (b for b in BORDES_CONOCIDOS if b[1] is None)))
    assert not de_modulo, "Bordes de nivel de módulo:\n  " + "\n  ".join(de_modulo)


def test_el_recorrido_sigue_imports_dentro_de_funciones_en_cadena(tmp_path):
    """Control del propio recorrido, sobre un árbol de juguete: un inicio que importa
    adentro de una función un módulo sólido, que a su vez llega a uno prohibido, cuenta; y
    un import de nivel de módulo se informa sin función."""
    archivos = {
        "src/leda/__init__.py": "",
        "src/leda/inicio.py": "def montar():\n    from .medio import Algo\n",
        "src/leda/medio.py": "from . import otro\n",
        "src/leda/otro.py": "from .gateway import x\n\ndef f():\n    import leda.jev\n",
    }
    for nombre, codigo in archivos.items():
        ruta = tmp_path / nombre
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(codigo, "utf-8")
    bordes, recorridos, faltantes = _bordes_desde_la_capa_solida(tmp_path, ("inicio", "nada"))
    assert bordes == {("src/leda/otro.py", None, "gateway"),
                      ("src/leda/otro.py", "f", "jev")}
    assert tmp_path / "src" / "leda" / "medio.py" in recorridos
    assert faltantes == ["nada"]


def test_importar_la_capa_solida_no_carga_la_conversacion_de_los_flujos_viejos():
    """En un proceso aparte, para que lo que ya cargó esta sesión de pytest no cuente."""
    entorno = {**os.environ, "PYTHONPATH": os.pathsep.join(
        filter(None, [str(RAIZ / "src"), os.environ.get("PYTHONPATH")]))}
    proceso = subprocess.run(
        [sys.executable, "-c", _SONDA, json.dumps(sorted(PROHIBIDOS)), json.dumps(INICIOS)],
        cwd=RAIZ, env=entorno, capture_output=True, text=True, encoding="utf-8",
        timeout=300)
    lineas = [l for l in proceso.stdout.splitlines() if l.startswith("SONDA ")]
    assert lineas, "La sonda no informó nada.\n" + proceso.stdout[-3000:] + proceso.stderr[-3000:]
    cargados = json.loads(lineas[-1].removeprefix("SONDA "))
    assert cargados == [], (
        "Importar la capa sólida cargó la conversación de los flujos viejos: "
        + ", ".join(cargados))
