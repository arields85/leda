"""La frontera de imports de la prueba chica (E2-2).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Imports"). La prueba chica sólo alcanza la
capa sólida de `src/leda`; nunca la conversación de los flujos congelados ni sus textos fijos.

- Lo que un módulo de `prueba_chica/` importa de `leda` tiene que estar en `PERMITIDOS`.
- Desde ahí se recorren los imports en cadena, incluidos los de dentro de funciones (un
  módulo alcanzado cuenta entero), y ninguno puede llegar a un módulo de `PROHIBIDOS`.
- `BORDES_CONOCIDOS` son las funciones de la capa sólida que llegan a un prohibido desde
  adentro y que la prueba chica no usa, o usa sabiendo a dónde llegan. Sólo puede achicarse
  (patrón de `tests/test_capacidades.py`): si un borde desaparece, la prueba pide sacarlo;
  si aparece uno nuevo, falla.
"""

from __future__ import annotations

import ast
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parents[1]
PRUEBA_CHICA = RAIZ / "prueba_chica"
LEDA = RAIZ / "src" / "leda"

# Módulo de `leda` y, cuando sólo se permite una parte, los nombres permitidos.
PERMITIDOS: dict[str, set[str] | None] = {
    "db": None,
    "autoridad": None,
    "herramientas": {"ejecutar"},
    "calendario": None,
    "salida": {"enqueue_outbox"},
    "despachador": None,
    "incidentes": {"registrar_incidente", "NOTICIA_NEUTRA_INCIDENTE",
                   "ETAPA_TURNO_CONVERSACION", "REFERENCIA_INBOUND_MESSAGE"},
    "llm": None,
    "jev": None,
    "config": None,
}

PROHIBIDOS = {"gateway", "agente", "ingreso_tareas", "contexto", "respuesta_unica",
              "huerfanos", "ciclo", "local", "escalera", "reloj"}

# (módulo, función que importa adentro, prohibido al que llega): por qué no molesta.
BORDES_CONOCIDOS = {
    ("pendientes", "ver_rama_abierta", "ingreso_tareas"):
        "La llama `despachador._rama_activa_de` para retener lo que Leda inicia; con las "
        "tablas de los flujos congelados vacías no retiene nada (test_despacho.py).",
    ("despachador", "_botones", "ingreso_tareas"):
        "Sólo con `intake_choice_set_id`, que el motor nunca pone en el outbox.",
    ("herramientas", "crear_borrador_tarea", "ingreso_tareas"):
        "Crear tareas por chat no es del Motor (ADR 0017); la prueba chica no la usa.",
}


def _imports_de(ruta: pathlib.Path) -> list[tuple[str, str | None, set[str]]]:
    """(módulo de `leda`, función de primer nivel que lo importa o `None`, nombres)."""
    arbol = ast.parse(ruta.read_text("utf-8"))
    dentro_de_leda = ruta.parent == LEDA
    hallados: list[tuple[str, str | None, set[str]]] = []

    def visitar(nodo: ast.AST, funcion: str | None) -> None:
        for hijo in ast.iter_child_nodes(nodo):
            actual = funcion
            if funcion is None and isinstance(hijo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                actual = hijo.name
            if isinstance(hijo, ast.ImportFrom):
                nombres = {a.name for a in hijo.names}
                if hijo.level == 1 and dentro_de_leda:
                    partes = hijo.module.split(".") if hijo.module else []
                elif hijo.level == 0 and hijo.module and hijo.module.split(".")[0] == "leda":
                    partes = hijo.module.split(".")[1:]
                else:
                    partes = None
                if partes:
                    hallados.append((partes[0], actual, nombres))
                elif partes == []:          # `from leda import x` / `from . import x`
                    for nombre in nombres:
                        hallados.append((nombre, actual, set()))
            elif isinstance(hijo, ast.Import):
                for alias in hijo.names:
                    partes = alias.name.split(".")
                    if partes[0] == "leda":
                        hallados.append((partes[1] if len(partes) > 1 else "leda",
                                         actual, set()))
            visitar(hijo, actual)

    visitar(arbol, None)
    return hallados


def _modulos_de_la_prueba_chica() -> list[pathlib.Path]:
    return sorted(PRUEBA_CHICA.rglob("*.py"))


def _bordes_hacia_prohibidos() -> tuple[set[tuple[str, str | None, str]], set[str]]:
    """Recorre la cadena desde lo que importa `prueba_chica/` y devuelve los bordes que
    llegan a un prohibido y los módulos alcanzados. No sigue más allá de un prohibido."""
    pendientes: list[str] = []
    alcanzados: set[str] = set()
    bordes: set[tuple[str, str | None, str]] = set()
    for ruta in _modulos_de_la_prueba_chica():
        for destino, funcion, _ in _imports_de(ruta):
            if destino in PROHIBIDOS:
                bordes.add((f"prueba_chica/{ruta.name}", funcion, destino))
            else:
                pendientes.append(destino)
    while pendientes:
        modulo = pendientes.pop()
        if modulo in alcanzados or modulo in PROHIBIDOS:
            continue
        alcanzados.add(modulo)
        ruta = LEDA / f"{modulo}.py"
        if not ruta.exists():
            continue
        for destino, funcion, _ in _imports_de(ruta):
            if destino in PROHIBIDOS:
                bordes.add((modulo, funcion, destino))
            else:
                pendientes.append(destino)
    return bordes, alcanzados


def test_la_prueba_chica_importa_de_leda_solo_lo_permitido():
    fuera = []
    for ruta in _modulos_de_la_prueba_chica():
        for modulo, _, nombres in _imports_de(ruta):
            if modulo not in PERMITIDOS:
                fuera.append(f"{ruta.name}: leda.{modulo}")
                continue
            permitidos = PERMITIDOS[modulo]
            if permitidos is not None and not nombres <= permitidos:
                fuera.append(f"{ruta.name}: leda.{modulo} {sorted(nombres - permitidos)}")
    assert not fuera, "Imports de leda fuera de la lista permitida:\n  " + "\n  ".join(fuera)


def test_la_cadena_de_imports_no_llega_a_los_flujos_congelados():
    bordes, _ = _bordes_hacia_prohibidos()
    nuevos = sorted(map(str, bordes - set(BORDES_CONOCIDOS)))
    assert not nuevos, (
        "La prueba chica llega a un módulo prohibido por un camino nuevo:\n  "
        + "\n  ".join(nuevos))


def test_los_bordes_conocidos_solo_pueden_achicarse():
    bordes, _ = _bordes_hacia_prohibidos()
    viejos = sorted(map(str, set(BORDES_CONOCIDOS) - bordes))
    assert not viejos, (
        "Estos bordes ya no existen: sacalos de BORDES_CONOCIDOS:\n  " + "\n  ".join(viejos))


def test_el_motor_no_usa_las_funciones_de_los_bordes():
    """Sólo el código del motor; las pruebas pueden nombrarlas para explicarlas."""
    usos = []
    for ruta in _modulos_de_la_prueba_chica():
        if ruta.name.startswith("test_") or ruta.name == "conftest.py":
            continue
        texto = ruta.read_text("utf-8")
        for palabra in ("crear_borrador_tarea", "intake_choice_set_id", "ver_rama_abierta"):
            if palabra in texto:
                usos.append(f"{ruta.name}: {palabra}")
    assert not usos, "La prueba chica usa una función de un borde:\n  " + "\n  ".join(usos)


def test_el_recorrido_ve_los_imports_dentro_de_funciones():
    """Control del propio recorrido: `despachador._rama_activa_de` importa `pendientes`
    adentro de la función, y por eso `pendientes` aparece alcanzado."""
    importados = {(m, f) for m, f, _ in _imports_de(LEDA / "despachador.py")}
    assert ("pendientes", "_rama_activa_de") in importados
    _, alcanzados = _bordes_hacia_prohibidos()
    assert {"despachador", "pendientes", "herramientas"} <= alcanzados
