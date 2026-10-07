"""La frontera del motor de conversación (`leda.motor`; `odd/tasks/motor-definitivo.md`, E3-5).

El motor sólo alcanza la capa sólida de `leda` y sólo toca las tablas que se declaran acá. Es
el patrón que tenía la prueba chica (`prueba_chica/test_frontera.py`), más la lista de tablas,
que reemplaza a la regla de juntar el SQL del motor en un solo módulo (decisiones técnicas de
la E3-5).

- **Módulos.** Lo que un módulo de `leda/motor/` importa de `leda` tiene que estar en
  `PERMITIDOS` (y, si se limita, sólo esos nombres). Nunca importa `prueba_chica`, borrada el
  2026-10-07, por si volviera.
- **Cadena.** Desde ahí se recorren los imports en cadena, incluidos los de dentro de funciones
  (un módulo alcanzado cuenta entero, y un paquete, con todos sus archivos), y ninguno puede
  llegar a `PROHIBIDOS`: los módulos de los flujos A y B. Un módulo alcanzado que no se
  encuentra hace fallar la prueba.
- **Bordes conocidos.** Las funciones que llegan a un prohibido desde adentro y que el motor no
  usa: sólo pueden achicarse.
- **Tablas.** Cada texto SQL de un módulo del motor (un texto con `select`, `insert`, `update`
  o `delete`; los docstrings no cuentan) nombra sus tablas después de `from`, `join`, `into` o
  `update`. Toda tabla del esquema (`db/esquema.sql`) que aparezca así tiene que estar en
  `TABLAS_PERMITIDAS`, y la lista es exacta: una tabla que ya nadie usa se saca. Cada capa que
  se porta la amplía con lo que usa.
"""

from __future__ import annotations

import ast
import pathlib
import re

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[2]
LEDA = RAIZ / "src" / "leda"
ESQUEMA = RAIZ / "db" / "esquema.sql"
PAQUETE = "motor"

# Módulo de `leda` y, cuando sólo se permite una parte, los nombres permitidos. Salió de la
# lista de la prueba chica (`prueba_chica/test_frontera.py`), más `versiones`, con la que el
# motor audita lo que escribe directo (decisiones técnicas de la E3-5), y, desde la entrada del
# motor (E3-7), el barrido de los mensajes sin respuesta (`huerfanos`) y lo que la entrada
# comparte con él: el candado por mensaje y el criterio de "ya tiene respuesta".
PERMITIDOS: dict[str, set[str] | None] = {
    "db": None,
    "autoridad": None,
    "herramientas": {"ejecutar", "NecesitaConfirmacion", "EstadoCambio", "NecesitaElegir",
                     "NecesitaOpciones"},
    "calendario": None,
    "salida": {"enqueue_outbox", "PayloadValidationError"},
    "despachador": None,
    "incidentes": {"registrar_incidente", "NOTICIA_NEUTRA_INCIDENTE",
                   "ETAPA_TURNO_CONVERSACION", "REFERENCIA_INBOUND_MESSAGE"},
    "llm": None,
    "config": None,
    "onboarding": {"activar", "bienvenida", "ActivacionInvalida"},
    "versiones": None,
    "huerfanos": {"barrer"},
    "entrada": {"clave_de_candado_del_mensaje", "sql_respondido"},
}

# Los módulos de los flujos A y B, borrados en la E3-4, por si volvieran. La escalera, el reloj
# y el ciclo viejos de `leda` se borraron en la E3-7: un import de ellos ya no se encuentra y
# hace fallar el recorrido. `huerfanos` ya no: dejó de importar los flujos viejos (E3-2) y el
# ciclo del motor lo corre.
PROHIBIDOS = {"gateway", "agente", "ingreso_tareas", "contexto", "respuesta_unica", "local"}

# (módulo, función que importa adentro, prohibido al que llega): por qué no molesta.
BORDES_CONOCIDOS: dict[tuple[str, str | None, str], str] = {}

# Las tablas que toca el SQL del motor, exactas. Capa 1: las preguntas y sus opciones, el
# estado y el registro de turnos (con el mensaje y la salida que nombran), la espera de una
# respuesta, los pasos guardados de la escalera y las previsiones que mueven el ancla, el
# estado de las tareas y el tono del espacio. Capa 2, las fichas: los bloqueos y quién los
# destraba, las tareas que dependen de otra, los integrantes por su nombre y el referente de
# quien escribe (`membership.aprobador_membership_id`). Capa 2, los avisos guardados: las
# ausencias, que los dejan esperando, y la ruta de escalamiento por falta de respuesta. Capa 3:
# la configuración del espacio (`workspace_setting`: los días del aviso previo de la escalera y
# el adelanto del reloj de Leda), el espacio por su nombre corto (el comando del reloj) y el
# modelo configurado del espacio o el global (`model_config`, la IA real). La entrada (E3-7):
# el nombre de quien se activa o ya está vinculado (`app_user`, en la activación). Los archivos
# recibidos (ADR 0019, decisiones 2 a 4): el contenido y lo que trajo cada mensaje
# (`archivos.py`).
TABLAS_PERMITIDAS = {
    "absence", "app_user", "archivo", "archivo_de_mensaje",
    "blocker", "blocker_unblocker", "conversation_option", "conversation_question",
    "conversation_state", "conversation_turn", "dependency", "escalation_route",
    "inbound_message", "integrante", "membership", "message_outbox", "model_config",
    "pending_reply", "persona_config", "scheduled_notice", "task", "task_forecast",
    "workspace", "workspace_setting",
}

_SQL = re.compile(r"\b(select|insert|update|delete)\b", re.IGNORECASE)
_TABLA = re.compile(r"\b(?:from|join|into|update)\s+([a-z_][a-z0-9_]*)", re.IGNORECASE)
_CREA = re.compile(r"^create\s+(?:table|(?:or\s+replace\s+)?view)\s+([a-z_][a-z0-9_]*)",
                   re.IGNORECASE | re.MULTILINE)


# --- El recorrido ---------------------------------------------------------------------------

def _paquete(ruta: pathlib.Path, leda: pathlib.Path) -> tuple[str, ...]:
    """El paquete de un archivo de `leda`, con `leda` adelante: `("leda", "motor")`."""
    return ("leda", *ruta.parent.relative_to(leda).parts)


def _imports_de(ruta: pathlib.Path, leda: pathlib.Path
                ) -> list[tuple[tuple[str, ...], str | None, set[str]]]:
    """(módulo importado, en partes absolutas; función de primer nivel que lo importa o
    `None`; nombres). `from <paquete> import x` cuenta como importar el módulo `x`."""
    arbol = ast.parse(ruta.read_text("utf-8"))
    paquete = _paquete(ruta, leda)
    hallados: list[tuple[tuple[str, ...], str | None, set[str]]] = []

    def visitar(nodo: ast.AST, funcion: str | None) -> None:
        for hijo in ast.iter_child_nodes(nodo):
            actual = funcion
            if funcion is None and isinstance(hijo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                actual = hijo.name
            if isinstance(hijo, ast.ImportFrom):
                nombres = {a.name for a in hijo.names}
                if hijo.level >= 1:
                    base = paquete[:len(paquete) - (hijo.level - 1)]
                    partes = (*base, *(hijo.module.split(".") if hijo.module else ()))
                else:
                    partes = tuple((hijo.module or "").split("."))
                if partes in {("leda",), ("leda", PAQUETE)}:
                    for nombre in nombres:      # `from . import x`: x es un módulo
                        hallados.append(((*partes, nombre), actual, set()))
                else:
                    hallados.append((partes, actual, nombres))
            elif isinstance(hijo, ast.Import):
                for alias in hijo.names:
                    hallados.append((tuple(alias.name.split(".")), actual, set()))
            visitar(hijo, actual)

    visitar(arbol, None)
    return hallados


def _archivos_del_motor(leda: pathlib.Path) -> list[pathlib.Path]:
    return sorted((leda / PAQUETE).rglob("*.py"))


def _archivos_del_modulo(modulo: str, leda: pathlib.Path) -> list[pathlib.Path]:
    """`leda/<modulo>.py`, o todos los archivos del paquete `leda/<modulo>/`. Uno que no se
    encuentra falla: saltearlo dejaría sin mirar lo que importa."""
    if modulo == "leda":
        return [leda / "__init__.py"]
    archivo = leda / f"{modulo}.py"
    if archivo.exists():
        return [archivo]
    paquete = leda / modulo
    if (paquete / "__init__.py").exists():
        return sorted(paquete.rglob("*.py"))
    raise AssertionError(
        f"El recorrido de imports no encuentra leda.{modulo} (ni leda/{modulo}.py ni el "
        f"paquete leda/{modulo}/): revisá cómo se importa.")


def _de_leda_fuera_del_motor(partes: tuple[str, ...]) -> str | None:
    """El módulo de primer nivel de `leda` que nombra un import, salvo el propio motor."""
    if partes[0] != "leda":
        return None
    modulo = partes[1] if len(partes) > 1 else "leda"
    return None if modulo == PAQUETE else modulo


def _bordes_hacia_prohibidos(leda: pathlib.Path = LEDA
                             ) -> tuple[set[tuple[str, str | None, str]], set[str]]:
    """Los bordes que llegan a un prohibido, desde lo que importa el motor, y los módulos de
    `leda` alcanzados. No sigue más allá de un prohibido, ni vuelve a entrar en el motor."""
    pendientes: list[str] = []
    alcanzados: set[str] = set()
    bordes: set[tuple[str, str | None, str]] = set()
    for ruta in _archivos_del_motor(leda):
        for partes, funcion, _ in _imports_de(ruta, leda):
            destino = _de_leda_fuera_del_motor(partes)
            if destino is None:
                continue
            if destino in PROHIBIDOS:
                bordes.add((f"{PAQUETE}/{ruta.name}", funcion, destino))
            else:
                pendientes.append(destino)
    while pendientes:
        modulo = pendientes.pop()
        if modulo in alcanzados or modulo in PROHIBIDOS:
            continue
        alcanzados.add(modulo)
        for ruta in _archivos_del_modulo(modulo, leda):
            for partes, funcion, _ in _imports_de(ruta, leda):
                destino = _de_leda_fuera_del_motor(partes)
                if destino is None:
                    continue
                if destino in PROHIBIDOS:
                    bordes.add((modulo, funcion, destino))
                else:
                    pendientes.append(destino)
    return bordes, alcanzados


def _docstrings(arbol: ast.AST) -> set[int]:
    ids = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            cuerpo = nodo.body
            if (cuerpo and isinstance(cuerpo[0], ast.Expr)
                    and isinstance(cuerpo[0].value, ast.Constant)
                    and isinstance(cuerpo[0].value.value, str)):
                ids.add(id(cuerpo[0].value))
    return ids


def _tablas_del_esquema(esquema: pathlib.Path = ESQUEMA) -> set[str]:
    return {nombre.lower() for nombre in _CREA.findall(esquema.read_text("utf-8"))}


def _tablas_usadas(leda: pathlib.Path = LEDA, esquema: pathlib.Path = ESQUEMA
                   ) -> set[tuple[str, str]]:
    """(archivo del motor, tabla del esquema) por cada tabla que nombra un texto SQL."""
    tablas = _tablas_del_esquema(esquema)
    usadas: set[tuple[str, str]] = set()
    for ruta in _archivos_del_motor(leda):
        arbol = ast.parse(ruta.read_text("utf-8"))
        docstrings = _docstrings(arbol)
        for nodo in ast.walk(arbol):
            if (not isinstance(nodo, ast.Constant) or not isinstance(nodo.value, str)
                    or id(nodo) in docstrings or not _SQL.search(nodo.value)):
                continue
            for nombre in _TABLA.findall(nodo.value):
                if nombre.lower() in tablas:
                    usadas.add((ruta.relative_to(leda / PAQUETE).as_posix(), nombre.lower()))
    return usadas


# --- Las pruebas ---------------------------------------------------------------------------

def test_el_motor_importa_de_leda_solo_lo_permitido():
    fuera = []
    for ruta in _archivos_del_motor(LEDA):
        for partes, _, nombres in _imports_de(ruta, LEDA):
            if partes[0] == "prueba_chica":
                fuera.append(f"{ruta.name}: {'.'.join(partes)}")
                continue
            modulo = _de_leda_fuera_del_motor(partes)
            if modulo is None:
                continue
            if modulo not in PERMITIDOS:
                fuera.append(f"{ruta.name}: leda.{modulo}")
                continue
            permitidos = PERMITIDOS[modulo]
            if permitidos is not None and not nombres <= permitidos:
                fuera.append(f"{ruta.name}: leda.{modulo} {sorted(nombres - permitidos)}")
    assert not fuera, "Imports fuera de la lista permitida:\n  " + "\n  ".join(fuera)


def test_la_cadena_de_imports_no_llega_a_lo_prohibido():
    bordes, _ = _bordes_hacia_prohibidos()
    nuevos = sorted(map(str, bordes - set(BORDES_CONOCIDOS)))
    assert not nuevos, ("El motor llega a un módulo prohibido por un camino nuevo:\n  "
                        + "\n  ".join(nuevos))


def test_los_bordes_conocidos_solo_pueden_achicarse():
    bordes, _ = _bordes_hacia_prohibidos()
    viejos = sorted(map(str, set(BORDES_CONOCIDOS) - bordes))
    assert not viejos, ("Estos bordes ya no existen: sacalos de BORDES_CONOCIDOS:\n  "
                        + "\n  ".join(viejos))


def test_el_motor_toca_solo_las_tablas_permitidas():
    fuera = sorted(f"{archivo}: {tabla}" for archivo, tabla in _tablas_usadas()
                   if tabla not in TABLAS_PERMITIDAS)
    assert not fuera, "SQL del motor sobre tablas fuera de la lista:\n  " + "\n  ".join(fuera)


def test_la_lista_de_tablas_es_exacta():
    esquema = _tablas_del_esquema()
    inexistentes = sorted(TABLAS_PERMITIDAS - esquema)
    assert not inexistentes, f"No son tablas del esquema: {inexistentes}"
    sin_uso = sorted(TABLAS_PERMITIDAS - {tabla for _, tabla in _tablas_usadas()})
    assert not sin_uso, f"Ningún módulo del motor las usa: sacalas de la lista: {sin_uso}"


def test_el_paquete_existe_y_el_recorrido_lo_ve():
    """Control del propio recorrido sobre el árbol real: hay módulos del motor, se ven sus
    imports relativos hacia `leda` y sus tablas."""
    archivos = {r.name for r in _archivos_del_motor(LEDA)}
    assert {"preguntas.py", "registro.py", "ancla.py"} <= archivos
    _, alcanzados = _bordes_hacia_prohibidos()
    assert "calendario" in alcanzados               # `preguntas` lo importa con `..`
    assert ("registro.py", "conversation_turn") in _tablas_usadas()


# --- Control del recorrido con un árbol de juguete -------------------------------------------

def _arbol_de_juguete(tmp_path: pathlib.Path, archivos: dict[str, str]
                      ) -> tuple[pathlib.Path, pathlib.Path]:
    leda = tmp_path / "leda"
    for nombre, codigo in {"__init__.py": "", f"{PAQUETE}/__init__.py": "",
                           **archivos}.items():
        ruta = leda / nombre
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(codigo, "utf-8")
    esquema = tmp_path / "esquema.sql"
    esquema.write_text("create table permitida (id int);\n"
                       "create table secreta (id int);\n"
                       "create or replace view vista_secreta as select 1;\n", "utf-8")
    return leda, esquema


def test_el_recorrido_sigue_la_cadena_y_entra_en_las_funciones(tmp_path):
    leda, _ = _arbol_de_juguete(tmp_path, {
        f"{PAQUETE}/x.py": "from ..db import algo\nfrom . import y\n",
        f"{PAQUETE}/y.py": "def f():\n    from ..paquete import otra\n",
        "db.py": "def algo():\n    from .gateway import correr\n",
        "paquete/__init__.py": "from .interno import otra\n",
        "paquete/interno.py": "def otra():\n    from ..agente import montar\n",
        "gateway.py": "", "agente.py": "",
    })
    bordes, alcanzados = _bordes_hacia_prohibidos(leda)
    assert bordes == {("db", "algo", "gateway"), ("paquete", "otra", "agente")}
    assert {"db", "paquete"} <= alcanzados
    assert "motor" not in alcanzados, "el motor se mira entero, no se recorre como un módulo"


def test_el_recorrido_falla_si_no_encuentra_un_modulo(tmp_path):
    leda, _ = _arbol_de_juguete(tmp_path, {f"{PAQUETE}/x.py": "from ..fantasma import algo\n"})
    with pytest.raises(AssertionError, match="fantasma"):
        _bordes_hacia_prohibidos(leda)


def test_la_lista_de_tablas_ve_el_sql_y_no_los_docstrings(tmp_path):
    leda, esquema = _arbol_de_juguete(tmp_path, {f"{PAQUETE}/x.py": '''\
"""Habla de select * from secreta, pero es un docstring."""

def leer(cur, clave):
    """Tampoco: delete from secreta."""
    cur.execute("select a.id from permitida a join secreta b on b.id = a.id")
    cur.execute(f"""update vista_secreta set id = {clave}""")
    cur.execute("insert into otra_cosa values (1)")     # no es del esquema
    return "las tareas from secreta"                    # sin un verbo de SQL no es SQL
'''})
    assert _tablas_del_esquema(esquema) == {"permitida", "secreta", "vista_secreta"}
    assert _tablas_usadas(leda, esquema) == {
        ("x.py", "permitida"), ("x.py", "secreta"), ("x.py", "vista_secreta")}
