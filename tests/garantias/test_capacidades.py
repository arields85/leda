"""El esquema no promete capacidades que nadie implementa.

Cada entrada de `PROMESAS_SIN_CUMPLIR` es algo que `db/esquema.sql` le declara
a quien lo lee y que ningún código cumple. La lista está acá, ejecutable, para
que la brecha sea deliberada y visible en vez de olvidarse: un documento con
este inventario se desactualiza en silencio, una prueba no puede.

Funciona en los dos sentidos.

- Si alguien **implementa** una de estas capacidades, la prueba falla y le
  pide que la saque de la lista. La deuda se salda de forma explícita.
- Si alguien **agrega esquema nuevo** que nadie usa, la prueba falla y le
  obliga a decidir: o lo implementa, o lo declara deuda aceptada acá.

Inventario levantado el 2026-09-22 auditando `nucleo/`, la especificación
funcional y el código completo.
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
ESQUEMA = ROOT / "db" / "esquema.sql"
FUENTE = ROOT / "src" / "leda"

# Qué le promete cada uno a quien lee el esquema.
PROMESAS_SIN_CUMPLIR = {
    "conversation_access_log":
        "Auditoría de qué administrador leyó la conversación de qué persona, "
        "con su motivo. Control de privacidad diseñado y nunca conectado.",
    "learning":
        "Memoria de aprendizaje con confianza y alcance (documento maestro §17, "
        "mecánica §14).",
    "parent_task_id":
        "Subtareas: el quinto nivel de la jerarquía (mecánica §1).",
    "prioridad":
        "Prioridad de una tarea, campo obligatorio según §8. Hoy toda tarea la "
        "tiene nula.",
    "drive_file_id":
        "Evidencia almacenada en Drive (§11 de la especificación funcional).",
    "intencion":
        "Clasificación de intención persistida del mensaje entrante.",
    "bot_token_ref":
        "Referencia al secreto del bot de un espacio.",
    "source_draft_id":
        "Trazabilidad de la tarea hacia el borrador que la originó.",
    "converted_task_id":
        "Trazabilidad del borrador hacia la tarea que produjo.",
    "otorgado_por":
        "Quién otorgó un rol de plataforma. Se inserta por defecto y nadie lo lee.",
    "otorgado_en":
        "Cuándo se otorgó un rol de plataforma.",
    "importado_en":
        "Cuándo se importó una versión de paquete.",
    "importado_por":
        "Quién aprobó una versión de paquete.",
    # `apodo.borrado_por_app_user_id` salió de esta lista con la decisión 67 del usuario: corregir
    # un apodo que ya tiene dueño lo retira por chat (`apodos.dejar_de_usar`), con quién y cuándo.
    # `admin_notice.destinatario_app_user_id` salió de esta lista con la migración 0054: la
    # respuesta del bot de administración la escribe (`despachador.encolar_respuesta_admin`,
    # a quien se le contesta).
    "confirmado_por":
        "Quién confirmó un mensaje que esperaba confirmación humana en la cola "
        "(`message_outbox`, estado `esperando_confirmacion`, mecánica §12). La "
        "función que lo confirmaba (`despachador.confirmar`) nadie la llamaba y se "
        "retiró en la E3-3; vuelve con el primer mensaje que necesite confirmarse.",
    "confirmado_en":
        "Cuándo se confirmó ese mensaje (ver `confirmado_por`).",
    "resuelta_por":
        "Quién resolvió una acción pendiente. La escribe `resolver_pendiente`, en "
        "la base; el código de `src/leda` que la leía era de los flujos A y B "
        "(E3-3).",
    "resuelta_en":
        "Cuándo se resolvió una acción pendiente (ver `resuelta_por`).",
}

# Tablas enteras sin implementación: sus columnas tampoco se referencian, y
# fijarlas una por una sería ruido. Alcanza con la tabla.
TABLAS_MUERTAS = ("conversation_access_log", "learning")

# `acceso_tablero` se toca únicamente desde sus dos funciones `security
# definer`, por diseño: `leda_app` no tiene ningún privilegio sobre ella.
# Que sus columnas no aparezcan en `src/` es la señal de que eso se respeta.
TABLAS_POR_FUNCION = ("acceso_tablero", "acceso_tarea", "vista_de_tarea",
                      "enlace_de_entrada", "sesion_web",
                      # La puerta de administración (migración 0061).
                      "enlace_de_administracion", "sesion_de_administracion",
                      # La clave de cada carga desde la web (migración 0062): la toca sólo
                      # `cargar_tarea`.
                      "carga_de_tarea",
                      # La reapertura de una tarea pedida (migración 0071, J4): la escribe sólo
                      # `reabrir_tarea`, y la leen `motivo_no_cierra_tarea` y
                      # `tipos_de_evidencia_que_faltan`.
                      "reapertura_de_tarea")

# Columnas sueltas de una tabla que sí usa `src/`, que sólo escriben y leen funciones de la base:
# `(tabla, columna)` → las funciones que la usan. Se exime el par, nunca el nombre (la misma
# columna en otra tabla tiene que usarse o declararse aparte), y cada función nombrada tiene que
# existir en el esquema y nombrar la columna en su cuerpo
# (`test_las_columnas_por_funcion_se_usan_en_esas_funciones`): no es una lista de promesas.
COLUMNAS_POR_FUNCION: dict[tuple[str, str], tuple[str, ...]] = {
    # `task.pedida_por_membership_id` (migración 0071, J4; decisiones D1b y D14): la escribe
    # `cargar_tarea_web` y la leen `puede_ver_tarea`, `pedidas_que_ve` y `reabrir_tarea`.
    ("task", "pedida_por_membership_id"): ("cargar_tarea_web", "puede_ver_tarea",
                                           "pedidas_que_ve", "reabrir_tarea"),
}

# Las tablas del motor de conversación (migraciones 0030 y 0031) estuvieron
# exentas mientras `conversation_state.mostrado_para_confirmar` no la leía nadie.
# Desde la entrega con evidencia (porción 2 de la C-3, `motor/entrega.py`) es lo
# último mostrado para confirmar, con su huella: la guarda de la confirmación
# escrita (ADR 0018, decisión 2). Ya no hay ninguna exenta.
TABLAS_DEL_MOTOR: tuple[str, ...] = ()


def _fuente() -> str:
    """Todo `src/leda`, con sus paquetes: desde la E3-7 el motor de conversación
    (`src/leda/motor/`) es quien lee y escribe buena parte del esquema."""
    return "\n".join(p.read_text("utf-8") for p in sorted(FUENTE.rglob("*.py")))


def _columnas_por_tabla() -> dict[str, set[str]]:
    esquema = ESQUEMA.read_text("utf-8")
    palabras_de_restriccion = {
        "primary", "unique", "foreign", "check", "constraint", "exclude"}
    tablas: dict[str, set[str]] = {}
    for bloque in re.finditer(r"create table (\w+) \((.*?)\n\);", esquema, re.S):
        columnas = set()
        for linea in bloque.group(2).splitlines():
            m = re.match(r"\s{2}(\w+)\s+\S", linea)
            if m and m.group(1) not in palabras_de_restriccion:
                columnas.add(m.group(1))
        tablas[bloque.group(1)] = columnas
    return tablas


def _referenciado(identificador: str, fuente: str) -> bool:
    # Con límite de palabra a propósito: `prioridad` no debe darse por usada
    # porque exista `definir_prioridad_general`, que es un nombre de permiso.
    return re.search(rf"\b{re.escape(identificador)}\b", fuente) is not None


def _esquema_nuevo_sin_uso(tablas: dict[str, set[str]], fuente: str) -> list[str]:
    """Las columnas que ningún código usa y nadie declaró: ni promesas, ni de una tabla exenta,
    ni el par `(tabla, columna)` que usan sólo funciones de la base."""
    exentas = (set(TABLAS_MUERTAS) | set(TABLAS_POR_FUNCION)
               | set(TABLAS_DEL_MOTOR))
    return sorted(
        f"{tabla}.{columna}"
        for tabla, columnas in tablas.items() if tabla not in exentas
        for columna in columnas
        if not _referenciado(columna, fuente) and columna not in PROMESAS_SIN_CUMPLIR
        and (tabla, columna) not in COLUMNAS_POR_FUNCION)


def _cuerpo_de_la_funcion(esquema: str, nombre: str) -> str | None:
    """El cuerpo de la última definición de una función en el esquema (la vigente), desde su
    nombre hasta el `$$` que la cierra."""
    definiciones = list(re.finditer(
        rf"create (?:or replace )?function {re.escape(nombre)}\((.*?)\$\$(.*?)\$\$",
        esquema, re.S))
    return definiciones[-1].group(2) if definiciones else None


def test_las_columnas_por_funcion_se_usan_en_esas_funciones():
    """Cada columna eximida por usarse sólo en funciones de la base es de esa tabla, y cada
    función nombrada existe y la nombra en su cuerpo: si una deja de usarla o cambia de nombre,
    la exención no queda como una promesa vacía (revisión de la J4a)."""
    esquema = ESQUEMA.read_text("utf-8")
    tablas = _columnas_por_tabla()
    problemas = []
    for (tabla, columna), funciones in COLUMNAS_POR_FUNCION.items():
        if columna not in tablas.get(tabla, set()):
            problemas.append(f"{tabla}.{columna}: la tabla no tiene esa columna")
        for funcion in funciones:
            cuerpo = _cuerpo_de_la_funcion(esquema, funcion)
            if cuerpo is None:
                problemas.append(f"{tabla}.{columna}: {funcion} no está en el esquema")
            elif not _referenciado(columna, cuerpo):
                problemas.append(f"{tabla}.{columna}: {funcion} no la usa")
    assert not problemas, "\n  ".join(["Exenciones que no se cumplen:", *problemas])


def test_eximir_una_columna_por_funcion_no_exime_su_nombre_en_otra_tabla():
    """La exención es del par: la misma columna en otra tabla, sin uso, sigue siendo esquema
    nuevo sin uso (revisión de la J4a)."""
    (tabla, columna), = list(COLUMNAS_POR_FUNCION)[:1]
    tablas = {tabla: {columna}, "otra_tabla": {columna}}
    assert _esquema_nuevo_sin_uso(tablas, fuente="") == [f"otra_tabla.{columna}"]


def test_las_promesas_sin_cumplir_siguen_sin_cumplirse():
    """Si una se implementó, hay que sacarla de la lista."""
    fuente = _fuente()
    implementadas = [
        f"{nombre}: {promesa}"
        for nombre, promesa in PROMESAS_SIN_CUMPLIR.items()
        if _referenciado(nombre, fuente)
    ]
    assert not implementadas, (
        "Estas capacidades ya no están sin implementar. Saquelas de "
        "PROMESAS_SIN_CUMPLIR y actualizá docs/capacidades.md:\n  "
        + "\n  ".join(implementadas))


def test_no_hay_esquema_nuevo_sin_uso_ni_declarado():
    """Esquema nuevo que nadie usa tiene que ser una decisión, no un olvido."""
    nuevas = _esquema_nuevo_sin_uso(_columnas_por_tabla(), _fuente())
    assert not nuevas, (
        "Estas columnas se declararon y ningún código las usa. O se "
        "implementan, o se agregan a PROMESAS_SIN_CUMPLIR diciendo qué "
        "prometen:\n  " + "\n  ".join(nuevas))


def test_el_umbral_de_reaprobacion_se_guarda_y_nadie_lo_lee():
    """Caso aparte: no está sin referencias, está sólo escrito.

    `importador.py` lo persiste en `workspace_setting` y ningún otro módulo lo
    consulta. La mecánica §7 lo vuelve el único freno para que aprobar el plan
    no degenere en aprobar tarea por tarea, así que el lector que falta es una
    capacidad ausente, no una columna muerta.
    """
    lectores = [
        p.name for p in sorted(FUENTE.glob("*.py"))
        if p.name != "importador.py"
        and _referenciado("umbral_reaprobacion", p.read_text("utf-8"))
    ]
    assert not lectores, (
        "Alguien lee el umbral de re-aprobación en "
        f"{', '.join(lectores)}: la capacidad existe. Sacá esta prueba y "
        "actualizá docs/capacidades.md.")
