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
    "destinatario_app_user_id":
        "Qué administrador de plataforma en particular recibió un aviso de "
        "incidente (`admin_notice`). El despacho manda por chat_id, sin "
        "necesitarla; queda para auditoría o soporte (\"¿le llegó a Ariel?\"), "
        "igual que otorgado_por en platform_role.",
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
    "ultima_corrida":
        "Cuándo corrió por última vez una cadencia (`cadence_job`). La escribía el "
        "ciclo viejo de `leda`, retirado en la E3-7 con las cadencias; vuelve con el "
        "circuito 5 (el pedido de estado de las cadencias), después de M3.",
}

# Tablas enteras sin implementación: sus columnas tampoco se referencian, y
# fijarlas una por una sería ruido. Alcanza con la tabla.
TABLAS_MUERTAS = ("conversation_access_log", "learning")

# `acceso_tablero` se toca únicamente desde sus dos funciones `security
# definer`, por diseño: `leda_app` no tiene ningún privilegio sobre ella.
# Que sus columnas no aparezcan en `src/` es la señal de que eso se respeta.
TABLAS_POR_FUNCION = ("acceso_tablero",)

# Las tablas del motor de conversación (migraciones 0030 y 0031). Nacieron con
# la prueba chica, borrada el 2026-10-07, y hoy las usa `src/leda/motor/`.
# Siguen exentas porque una columna todavía no la lee nadie
# (`conversation_state.mostrado_para_confirmar`); sacarlas pide decidir qué
# promete esa columna (`PROMESAS_SIN_CUMPLIR`) o borrarla.
TABLAS_DEL_MOTOR = (
    "conversation_state", "conversation_turn", "conversation_question",
    "conversation_option", "scheduled_notice", "task_forecast",
    "blocker_unblocker")


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
    fuente = _fuente()
    tablas = _columnas_por_tabla()

    exentas = (set(TABLAS_MUERTAS) | set(TABLAS_POR_FUNCION)
               | set(TABLAS_DEL_MOTOR))
    sin_uso = {
        columna
        for tabla, columnas in tablas.items() if tabla not in exentas
        for columna in columnas if not _referenciado(columna, fuente)
    }

    nuevas = sorted(sin_uso - set(PROMESAS_SIN_CUMPLIR))
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
