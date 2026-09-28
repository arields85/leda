"""Siembra reproducible de datos ficticios (T7, `odd/tasks/prisma-orienta.md`).

Carga un archivo de semilla versionado (por ejemplo
`espacios/corework.semilla-ficticia.yaml`) en un espacio recién importado y
activo, para poder probar sin depender de tareas cargadas a mano -- eso fue
lo que dejó las 12 tareas ficticias de las sesiones 1 y 2 con el título
terminado en " (simulado)", un campo de compromiso que después no se pudo
renombrar (`bloquear_estado_directo`, `db/esquema.sql`).

Corre bajo `admin(conn)`, igual que `importador.importar`: `prisma_admin`
tiene `bypassrls` y `grant all` sobre `task`/`task_state_event`/`dependency`,
así que puede escribir directo sin pasar por `confirmar_borrador_tarea` --
esa función es la ruta de compromiso para un borrador real que llegó por
Telegram (revalida la vista previa, resuelve la identidad autenticada por el
webhook, corre con `prisma_gateway` sobre una conexión de autoridad separada)
y no tiene sentido para cargar un lote de fixtures administrativos; el
importador del pack ya crea `objective`/`objective_state_event` del mismo
modo, directo, bajo `admin(conn)`.

Ninguna escritura salta los disparadores: el estado de una tarea sigue sin
poder fijarse directo (`bloquear_estado_directo` lo rechaza incluso para
`prisma_admin`, que no es dueño de esa regla) y se alcanza insertando
`task_state_event`, como el resto del producto. El orden importa para que
ningún disparador tenga que saltearse:

  1. Cada tarea entra a su estado inicial con un solo evento (sin evento
     `estado_anterior`), antes de que exista ninguna dependencia que la
     nombre como destino -- `exigir_dependencias_resueltas` sólo evalúa el
     freno de arranque al INSERTAR el evento hacia `en_curso`, así que una
     tarea que la semilla arranca `en_curso` sin dependencias todavía
     pendientes lo pasa limpio.
  2. Recién después se insertan las dependencias bloqueantes de la semilla.
     Insertar en `dependency` no dispara `exigir_dependencias_resueltas` (ese
     disparador vive en `task_state_event`, no en `dependency`): una
     dependencia bloqueante que apunta a una tarea que ya está `en_curso` no
     la mueve retroactivamente, igual que
     `test_crear_dependencia_bloqueante_sobre_destino_ya_en_curso_lo_menciona`
     en `tests/test_dependencias.py`.

`task.evidencia_policy_version` se llena igual que un compromiso real: cuando
el intake por Telegram resuelve el paso de evidencia
(`ingreso_tareas.py`, función `_finalize`) lee `version` de
`task_evidence_policy` para el área del borrador y la copia a
`task_draft.evidencia_policy_version`; `confirmar_borrador_tarea`
(`db/esquema.sql`) la copia sin tocarla de ahí a `task.evidencia_policy_version`
al confirmar. La siembra no pasa por ningún borrador, así que lee la misma
fila (`task_evidence_policy` de esa área, en este mismo espacio) al momento de
sembrar y la fija en el `insert` -- nunca queda en `null` como quedaron las 12
tareas cargadas a mano en las sesiones 1 y 2 (el hallazgo lateral del
Experimento 1 de invariantes, `odd/tasks/prisma-orienta.md`, que no es cómo el
producto crea una tarea real).

Cada siembra exitosa se audita con una sola fila en `audit_log`
(`registrar_auditoria`, `db.py`), en la misma transacción -- AGENTS.md,
"Invariantes vigentes": ningún efecto relevante queda sin auditoría. El
`actor_kind` es `'sistema'` (no hay una persona detrás) y el detalle sólo
lleva conteos y el nombre del archivo de semilla, nunca títulos de tarea ni
nombres de personas. Una siembra rechazada (guardas de arriba) no escribe
nada, tampoco esa fila: no hubo ningún efecto que auditar.

Seguimientos de la revisión review-943484ef642de774 (T7b,
`odd/tasks/prisma-orienta.md`): `sembrar` valida toda la semilla contra el
espacio -- archivo legible y YAML válido, claves requeridas de cada tarea,
títulos repetidos, referencias de `dependencias` a títulos que no están en
la misma semilla, y un `estado_inicial` dentro de `asignada`/`en_curso`
solamente -- antes de insertar la primera fila, así una semilla inválida no
escribe nada sin depender de que quien llama revierta. Si de todos modos la
base rechaza una escritura ya validada (un error que esta validación no
anticipó), `sembrar` no abre su propio SAVEPOINT para revertir: quien la
llama tiene que correrla dentro de una transacción que se revierta sola ante
una excepción -- `admin(conn)` (`db.py`) ya lo hace, igual que la CLI
(`cli.py`, rama `sembrar`) y las pruebas de este módulo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import psycopg
import yaml

from .db import registrar_auditoria


class SiembraInvalida(Exception):
    """El espacio no está en condiciones de sembrarse, o la semilla es inválida."""


@dataclass
class ResultadoSiembra:
    tareas: int
    dependencias: int
    estados: dict[str, int] = field(default_factory=dict)


# Claves que cada tarea de la semilla tiene que traer: sin ellas no hay
# forma de resolver área, objetivo ni responsable contra el espacio.
CLAVES_TAREA_REQUERIDAS = ("titulo", "area", "objetivo", "responsable")

# T7b (`odd/tasks/prisma-orienta.md`): el único allow-list posible para
# `estado_inicial` de una siembra -- "nada preaprobado, nada en revisión"
# (ADR 0009) queda en código, no sólo en la semilla. Ni `pendiente_aprobacion`
# ni `en_revision`, tampoco `terminada`, `bloqueada`, `cancelada` o
# `propuesta`.
ESTADOS_INICIALES_PERMITIDOS = frozenset({"asignada", "en_curso"})


def sembrar(
    cur: psycopg.Cursor,
    workspace_id: str,
    ruta: Path,
    *,
    dia_semilla: date | None = None,
) -> ResultadoSiembra:
    """Carga `ruta` en `workspace_id`. Tiene que correr bajo `admin(conn)`.

    Rechaza si el espacio no existe, o si ya tiene alguna tarea (de
    cualquier estado): la siembra nunca se mezcla con datos reales ni con
    una siembra anterior. `dia_semilla` es el día contra el que se resuelven
    las fechas relativas (`fecha_objetivo.dias`); por defecto, hoy en la
    zona horaria del espacio -- nunca la fecha local del host que corre el
    comando (T7b, `odd/tasks/prisma-orienta.md`).

    Valida toda la semilla contra el espacio antes de insertar la primera
    fila (ver el docstring del módulo): si algo es inválido, no se escribe
    nada, sin depender de que quien llama revierta.
    """
    cur.execute("select zona_horaria from workspace where id = %s", (workspace_id,))
    fila = cur.fetchone()
    if not fila:
        raise SiembraInvalida("El espacio no existe. Corré 'importar' primero.")
    zona = ZoneInfo(fila["zona_horaria"])

    cur.execute("select count(*) as n from task where workspace_id = %s", (workspace_id,))
    if cur.fetchone()["n"] > 0:
        raise SiembraInvalida(
            "El espacio ya tiene tareas: la siembra no se mezcla con datos "
            "existentes. Usá un espacio recién importado, sin sembrar todavía.")

    semilla = _cargar_semilla(ruta)
    dia = dia_semilla or datetime.now(zona).date()

    tareas_spec = semilla.get("tareas") or []
    dependencias_spec = semilla.get("dependencias") or []

    # --- Validación completa contra el espacio, antes del primer insert ---
    titulos_vistos: set[str] = set()
    preparadas: list[dict[str, Any]] = []
    for t in tareas_spec:
        if not isinstance(t, dict):
            raise SiembraInvalida("Cada tarea de la semilla tiene que ser un mapeo.")
        _validar_claves_requeridas(t)

        titulo = t["titulo"]
        if titulo in titulos_vistos:
            raise SiembraInvalida(f"Título repetido en la semilla: '{titulo}'.")
        titulos_vistos.add(titulo)

        estado_inicial = t.get("estado_inicial", "asignada")
        if estado_inicial not in ESTADOS_INICIALES_PERMITIDOS:
            raise SiembraInvalida(
                f"Estado inicial '{estado_inicial}' no permitido para la siembra: "
                f"sólo {' o '.join(sorted(ESTADOS_INICIALES_PERMITIDOS))} -- nada "
                "preaprobado, nada en revisión (ADR 0009).")

        area_id = _area_id(cur, workspace_id, t["area"])
        objetivo_id = _objetivo_id(cur, workspace_id, t["objetivo"])
        responsable_id = _membership_id(cur, workspace_id, t["responsable"])
        version_evidencia = _version_politica_evidencia(cur, workspace_id, area_id, t["area"])
        fecha = _fecha_objetivo(dia, zona, t.get("fecha_objetivo"))

        preparadas.append({
            "spec": t, "titulo": titulo, "area_id": area_id,
            "objetivo_id": objetivo_id, "responsable_id": responsable_id,
            "version_evidencia": version_evidencia, "fecha": fecha,
            "estado_inicial": estado_inicial,
        })

    for d in dependencias_spec:
        if not isinstance(d, dict):
            raise SiembraInvalida("Cada dependencia de la semilla tiene que ser un mapeo.")
        origen, destino = d.get("origen"), d.get("destino")
        if origen not in titulos_vistos or destino not in titulos_vistos:
            raise SiembraInvalida(
                f"La dependencia {origen!r} -> {destino!r} nombra un título "
                "que no está en esta misma semilla.")

    # --- Escritura: recién acá, con todo ya validado ----------------------
    por_titulo: dict[str, str] = {}
    estados: dict[str, int] = {}

    for p in preparadas:
        t = p["spec"]
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, descripcion,
                                 area_id, responsable_membership_id, fecha_objetivo,
                                 criterio_aceptacion, evidencia_requerida,
                                 evidencia_policy_version)
               values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               returning id""",
            (workspace_id, p["objetivo_id"], p["titulo"], t.get("descripcion"),
             p["area_id"], p["responsable_id"], p["fecha"], t.get("criterio_aceptacion"),
             list(t.get("evidencia_requerida") or []), p["version_evidencia"]),
        )
        tarea_id = str(cur.fetchone()["id"])
        por_titulo[p["titulo"]] = tarea_id

        cur.execute(
            """insert into task_state_event (task_id, estado_nuevo, actor_kind, motivo)
               values (%s, %s, 'sistema', %s)""",
            (tarea_id, p["estado_inicial"], t.get("motivo_estado_inicial")),
        )
        estados[p["estado_inicial"]] = estados.get(p["estado_inicial"], 0) + 1

    n_dependencias = 0
    for d in dependencias_spec:
        origen_id = por_titulo[d["origen"]]
        destino_id = por_titulo[d["destino"]]
        cur.execute(
            """insert into dependency (workspace_id, origen_task_id, destino_task_id, tipo)
               values (%s, %s, %s, %s)""",
            (workspace_id, origen_id, destino_id, d.get("tipo", "bloqueante")),
        )
        n_dependencias += 1

    registrar_auditoria(
        cur, accion="siembra_ficticia", workspace_id=workspace_id, actor_kind="sistema",
        sujeto_tipo="workspace", sujeto_id=workspace_id,
        detalle={"archivo": ruta.name, "tareas": len(por_titulo),
                 "dependencias": n_dependencias, "estados": estados})

    return ResultadoSiembra(
        tareas=len(por_titulo), dependencias=n_dependencias, estados=estados)


def _cargar_semilla(ruta: Path) -> dict[str, Any]:
    """Lee y parsea el YAML de la semilla, sin dejar pasar una traza cruda
    (T7b, `odd/tasks/prisma-orienta.md`): archivo faltante o YAML roto o
    vacío terminan en `SiembraInvalida`, nunca en una excepción de
    `pathlib`/`yaml` sin traducir."""
    try:
        texto = ruta.read_text(encoding="utf-8")
    except OSError as e:
        raise SiembraInvalida(
            f"No se pudo leer el archivo de semilla '{ruta}' ({type(e).__name__}).") from e
    try:
        semilla = yaml.safe_load(texto)
    except yaml.YAMLError as e:
        raise SiembraInvalida(
            f"El archivo de semilla '{ruta}' no es un YAML válido.") from e
    if not isinstance(semilla, dict):
        raise SiembraInvalida(
            f"El archivo de semilla '{ruta}' está vacío o no tiene el formato "
            "esperado (se esperaba un mapeo con 'tareas' y, opcionalmente, "
            "'dependencias').")
    return semilla


def _validar_claves_requeridas(t: dict[str, Any]) -> None:
    faltantes = [c for c in CLAVES_TAREA_REQUERIDAS if c not in t]
    if not faltantes:
        return
    if len(faltantes) == 1:
        raise SiembraInvalida(f"Falta la clave '{faltantes[0]}' en una tarea de la semilla.")
    claves = ", ".join(f"'{c}'" for c in faltantes)
    raise SiembraInvalida(f"Faltan las claves {claves} en una tarea de la semilla.")


def _area_id(cur: psycopg.Cursor, ws: str, slug: str) -> str:
    cur.execute("select id from area where workspace_id = %s and slug = %s", (ws, slug))
    fila = cur.fetchone()
    if not fila:
        raise SiembraInvalida(f"El área '{slug}' no existe en este espacio.")
    return str(fila["id"])


def _objetivo_id(cur: psycopg.Cursor, ws: str, titulo: str) -> str:
    """`objective.titulo` no tiene `unique` en `db/esquema.sql` (ni solo, ni
    junto a `workspace_id`): un pack mal armado puede tener dos objetivos con
    el mismo título en el mismo espacio. Buscar por título y quedarse con
    `fetchone()` sería arbitrario -- el orden sin `order by` no está
    garantizado -- así que una siembra que lo haga rechaza en vez de adivinar
    cuál de los dos es (T7b, `odd/tasks/prisma-orienta.md`)."""
    cur.execute(
        "select id from objective where workspace_id = %s and titulo = %s", (ws, titulo))
    filas = cur.fetchall()
    if not filas:
        raise SiembraInvalida(
            f"El objetivo '{titulo}' no existe en este espacio. "
            "¿Se importó el pack con 'importar --activar'?")
    if len(filas) > 1:
        raise SiembraInvalida(
            f"El objetivo '{titulo}' es ambiguo en este espacio: hay "
            f"{len(filas)} objetivos con ese título y 'objective.titulo' no es "
            "único por esquema. Corregí los títulos del pack antes de sembrar.")
    return str(filas[0]["id"])


def _membership_id(cur: psycopg.Cursor, ws: str, nombre: str) -> str:
    cur.execute(
        """select m.id from membership m join app_user u on u.id = m.app_user_id
            where m.workspace_id = %s and u.nombre = %s""", (ws, nombre))
    fila = cur.fetchone()
    if not fila:
        raise SiembraInvalida(
            f"'{nombre}' no está entre las personas del pack de este espacio.")
    return str(fila["id"])


def _version_politica_evidencia(
    cur: psycopg.Cursor, ws: str, area_id: str, area_slug: str
) -> int:
    """La misma fila que `ingreso_tareas.py` lee al resolver el paso de
    evidencia de un borrador real, para que `task.evidencia_policy_version`
    quede como si esta tarea hubiera pasado por `confirmar_borrador_tarea`."""
    cur.execute(
        "select version from task_evidence_policy where workspace_id = %s and area_id = %s",
        (ws, area_id))
    fila = cur.fetchone()
    if not fila:
        raise SiembraInvalida(
            f"No hay una política de evidencia vigente para el área '{area_slug}'. "
            "¿Se importó el pack con 'importar --activar'?")
    return fila["version"]


def _fecha_objetivo(
    dia_semilla: date, zona: ZoneInfo, spec: dict[str, Any] | None
) -> datetime | None:
    if not spec or spec.get("dias") is None:
        return None
    return datetime.combine(
        dia_semilla + timedelta(days=int(spec["dias"])), time(0, 0), tzinfo=zona)
