"""La frontera de imports de la prueba chica (E2-2).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Imports"). La prueba chica sólo alcanza la
capa sólida de `src/leda`; nunca la conversación de los flujos congelados ni sus textos fijos.

- Lo que un módulo de `prueba_chica/` importa de `leda` tiene que estar en `PERMITIDOS`.
- Desde ahí se recorren los imports en cadena, incluidos los de dentro de funciones (un
  módulo alcanzado cuenta entero), y ninguno puede llegar a un módulo de `PROHIBIDOS`.
- Un módulo alcanzado es `leda/<nombre>.py` o, si es un paquete, todos los archivos de
  `leda/<nombre>/`; uno que no se encuentra hace fallar la prueba, nunca se saltea.
- `BORDES_CONOCIDOS` son las funciones de la capa sólida que llegan a un prohibido desde
  adentro y que la prueba chica no usa, o usa sabiendo a dónde llegan. Sólo puede achicarse
  (patrón de `tests/garantias/test_capacidades.py`): si un borde desaparece, la prueba pide sacarlo;
  si aparece uno nuevo, falla.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
PRUEBA_CHICA = RAIZ / "prueba_chica"
LEDA = RAIZ / "src" / "leda"

# Módulo de `leda` y, cuando sólo se permite una parte, los nombres permitidos.
PERMITIDOS: dict[str, set[str] | None] = {
    "db": None,
    "autoridad": None,
    # `ejecutar` y lo que levanta como respuesta del dominio (revisión de la E2-3).
    "herramientas": {"ejecutar", "NecesitaConfirmacion", "EstadoCambio", "NecesitaElegir",
                     "NecesitaOpciones"},
    "calendario": None,
    # `enqueue_outbox` y lo que levanta si el texto no se puede llevar (revisión de la corrida en
    # seco con las 16).
    "salida": {"enqueue_outbox", "PayloadValidationError"},
    "despachador": None,
    "incidentes": {"registrar_incidente", "NOTICIA_NEUTRA_INCIDENTE",
                   "ETAPA_TURNO_CONVERSACION", "REFERENCIA_INBOUND_MESSAGE"},
    "llm": None,
    "jev": None,
    "config": None,
    # La activación de siempre, para el escuchador (E2-3b); `onboarding` sólo importa `salida`.
    "onboarding": {"activar", "bienvenida", "ActivacionInvalida"},
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
    paquete = _paquete_en_leda(ruta)
    hallados: list[tuple[str, str | None, set[str]]] = []

    def visitar(nodo: ast.AST, funcion: str | None) -> None:
        for hijo in ast.iter_child_nodes(nodo):
            actual = funcion
            if funcion is None and isinstance(hijo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                actual = hijo.name
            if isinstance(hijo, ast.ImportFrom):
                nombres = {a.name for a in hijo.names}
                if hijo.level >= 1 and paquete is not None:
                    # Relativo: `.` es el paquete del archivo; cada punto más sube uno.
                    subir = hijo.level - 1
                    partes = (list(paquete[:len(paquete) - subir])
                              + (hijo.module.split(".") if hijo.module else [])
                              if subir <= len(paquete) else None)
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


def _paquete_en_leda(ruta: pathlib.Path) -> tuple[str, ...] | None:
    """El paquete de `ruta` dentro de `leda`: `()` en la raíz, `("paquete",)` dentro de
    `leda/paquete/`; `None` fuera de `leda`."""
    try:
        return ruta.parent.relative_to(LEDA).parts
    except ValueError:
        return None


def _archivos_del_modulo(modulo: str) -> list[pathlib.Path]:
    """Los archivos de un módulo de primer nivel de `leda`: `leda/<modulo>.py`, o todos los
    de un paquete `leda/<modulo>/` (cuenta entero, como un módulo). Uno que no se encuentra
    falla: saltearlo dejaría sin mirar lo que importa (revisión de la E2-2)."""
    if modulo == "leda":
        return [LEDA / "__init__.py"]
    archivo = LEDA / f"{modulo}.py"
    if archivo.exists():
        return [archivo]
    paquete = LEDA / modulo
    if (paquete / "__init__.py").exists():
        return sorted(paquete.rglob("*.py"))
    raise AssertionError(
        f"El recorrido de imports no encuentra leda.{modulo} (ni leda/{modulo}.py ni el "
        f"paquete leda/{modulo}/): revisá cómo se importa.")


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
        for ruta in _archivos_del_modulo(modulo):
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


def _leda_de_juguete(tmp_path, monkeypatch, prueba: str, modulos: dict[str, str]):
    """Un `leda` y una `prueba_chica` de juguete para probar el propio recorrido."""
    leda = tmp_path / "leda"
    for nombre, codigo in {"__init__.py": "", **modulos}.items():
        ruta = leda / nombre
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(codigo, "utf-8")
    archivo = tmp_path / "prueba_chica" / "motor.py"
    archivo.parent.mkdir()
    archivo.write_text(prueba, "utf-8")
    import prueba_chica.test_frontera as este
    monkeypatch.setattr(este, "LEDA", leda)
    monkeypatch.setattr(este, "_modulos_de_la_prueba_chica", lambda: [archivo])
    return este


def test_el_recorrido_entra_en_los_paquetes(tmp_path, monkeypatch):
    """Revisión de la E2-2: un módulo de `leda` que es un paquete (`leda/<nombre>/`) no se
    puede saltear en silencio; sus imports, también los relativos, cuentan."""
    este = _leda_de_juguete(tmp_path, monkeypatch, "from leda.paquete import algo\n", {
        "paquete/__init__.py": "from .interno import algo\n",
        "paquete/interno.py": "def algo():\n    from ..gateway import procesar_update\n",
        "gateway.py": "",
    })
    bordes, alcanzados = este._bordes_hacia_prohibidos()
    assert ("paquete", "algo", "gateway") in bordes
    assert "paquete" in alcanzados


def test_el_recorrido_falla_si_no_encuentra_un_modulo(tmp_path, monkeypatch):
    """Revisión de la E2-2: un módulo alcanzado que no se encuentra no se saltea: falla."""
    este = _leda_de_juguete(tmp_path, monkeypatch, "from leda.fantasma import algo\n", {})
    with pytest.raises(AssertionError, match="fantasma"):
        este._bordes_hacia_prohibidos()
