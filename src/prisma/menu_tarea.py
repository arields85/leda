"""Menú de acciones de una tarea (T2, `prisma-orienta`; ADR 0007, diseño
§4.6, `docs/architecture/interpretacion-y-confirmacion.md`).

Tocar una tarea ofrece sólo lo que la persona puede hacer con ella, según su
estado (`nucleo/mecanica-pm.md` §3) y su relación con ella -- responsable,
aprobador de la cadena del espacio (§7), u otra persona del equipo. Lo
calcula el código, no el modelo: eso es lo que distingue este menú de
`herramientas.ofrecer_opciones` (T1), donde el modelo elige QUÉ preguntar.
Acá el servidor decide QUÉ SE PUEDE hacer, sin preguntarle nada al modelo.

Sólo se ofrecen las acciones que ya tienen herramienta: las marcadas con *
en §4.6 son "aportes sobre tareas", una unidad posterior, y no se muestran
hasta que exista. Ofrecer nunca autoriza -- cada acción que cambia algo pasa
igual por `herramientas.ejecutar`, que vuelve a verificar autoridad al
preparar la vista previa (§4.6: "ofrecer no autoriza").
"""

from __future__ import annotations

from dataclasses import dataclass

import psycopg

from .autoridad import Solicitante, puede_aprobar_tarea
from .herramientas import _estado_legible

# Cuántas tareas candidatas ofrece, como máximo, la elección de "de cuál de
# mis tareas depende" / "cuál de mis tareas depende de ésta" (mismo tope que
# `herramientas.MAX_OPCIONES_MODELO`, ADR 0007: "hasta cuatro opciones más
# la salida").
MAX_CANDIDATAS_DEPENDENCIA = 4


@dataclass(frozen=True)
class AccionMenu:
    codigo: str
    etiqueta: str


@dataclass(frozen=True)
class MenuTarea:
    tarea_id: str
    titulo: str
    estado: str
    relacion: str      # "responsable" | "aprobador" | "otra"
    acciones: list[AccionMenu]


def _tarea_para_menu(cur: psycopg.Cursor, tarea_id: str) -> dict | None:
    cur.execute(
        """select id, titulo, estado, responsable_membership_id
             from task where id = %s""", (tarea_id,))
    return cur.fetchone()


def _relacion(cur: psycopg.Cursor, quien: Solicitante,
             responsable_membership_id) -> str:
    """A quién le corresponde qué fila de §4.6. Un aprobador de la cadena de
    aprobación (`puede_aprobar_tarea`, un solo nivel: a un integrante lo
    aprueba su referente) usa la tabla de aprobador aunque la tarea no esté
    en revisión -- ahí sólo se le ofrece Ver detalle (§4.6, fila "Otro")."""
    if responsable_membership_id is not None and (
            str(responsable_membership_id) == str(quien.membership_id)):
        return "responsable"
    if responsable_membership_id is not None and puede_aprobar_tarea(
            cur, quien, responsable_membership_id):
        return "aprobador"
    return "otra"


def _puede_empezar(cur: psycopg.Cursor, tarea_id: str) -> bool:
    """Reusa `motivo_no_arranca_tarea` (la misma función SQL que ya
    verifica `herramientas._actualizar_estado` antes de intentar el pase a
    `en_curso`): si hay una dependencia bloqueante sin terminar, no la
    reimplementa acá -- una sola fuente de verdad para "puede empezar"."""
    cur.execute("select motivo_no_arranca_tarea(%s) as m", (tarea_id,))
    return cur.fetchone()["m"] is None


def calcular_menu(cur: psycopg.Cursor, quien: Solicitante,
                  tarea_id: str) -> MenuTarea | None:
    """El menú de una tarea para quien la toca, ya filtrado por lo que
    puede hacer (§4.6). `None` si la tarea ya no existe bajo el RLS de este
    cursor -- defensivo: para cuando se llega acá la tarea siempre existió
    (la validó `ofrecer_opciones` contra la misma base), pero el tiempo
    entre ofrecerla y tocarla no está acotado."""
    fila = _tarea_para_menu(cur, tarea_id)
    if not fila:
        return None

    estado = fila["estado"]
    relacion = _relacion(cur, quien, fila["responsable_membership_id"])
    acciones: list[AccionMenu] = []

    if relacion == "responsable":
        acciones.append(AccionMenu("ver_detalle", "Ver detalle"))
        if estado == "asignada" and _puede_empezar(cur, tarea_id):
            acciones.append(AccionMenu("empezar", "Empezar"))
        if estado in ("asignada", "en_curso"):
            acciones.append(AccionMenu("terminar", "Ya la terminé"))
            acciones.append(AccionMenu("informar_bloqueo", "Informar un bloqueo"))
            acciones.append(AccionMenu("depende_de_otra", "Depende de otra tarea"))
        elif estado == "bloqueada":
            acciones.append(AccionMenu("destrabar", "Ya se destrabó"))
        elif estado == "en_revision":
            acciones.append(AccionMenu("adjuntar_evidencia", "Adjuntar evidencia"))
        # terminada/cancelada: sólo Ver detalle, ya agregado arriba.
    elif relacion == "aprobador":
        if estado == "en_revision":
            acciones.append(AccionMenu("ver_detalle_evidencia", "Ver detalle y evidencia"))
            acciones.append(AccionMenu("aprobar", "Aprobar"))
        else:
            acciones.append(AccionMenu("ver_detalle", "Ver detalle"))
    else:
        acciones.append(AccionMenu("ver_detalle", "Ver detalle"))
        acciones.append(AccionMenu("mi_trabajo_depende", "Mi trabajo depende de esta tarea"))

    return MenuTarea(tarea_id=str(tarea_id), titulo=fila["titulo"], estado=estado,
                     relacion=relacion, acciones=acciones)


def bloqueos_abiertos(cur: psycopg.Cursor, tarea_id: str) -> list[dict]:
    cur.execute(
        """select id, causa from blocker
            where task_id = %s and resuelto_en is null order by abierto_en""",
        (tarea_id,))
    return [dict(f) for f in cur.fetchall()]


def tareas_activas_de_persona(
        cur: psycopg.Cursor, workspace_id: str, membership_id: str, *,
        excluir_tarea_id: str | None = None,
        limite: int | None = None) -> list[dict]:
    """La regla compartida de "tarea activa de una persona"
    (`estado not in ('terminada', 'cancelada')`), en un único lugar --
    `tareas_activas_de` (la elección de con cuál otra tarea depende, T2) y
    `gateway._mostrar_tareas_propias` (T4b, "Es sobre una tarea existente")
    la necesitan igual, y antes cada una tenía su propia copia de la
    consulta.

    Orden determinístico: `fecha_objetivo nulls last` no alcanza sola para
    desempatar entre tareas sin fecha o con la misma fecha -- se agrega
    `id` como segundo criterio, siempre el mismo para el mismo conjunto de
    filas, en vez de depender del orden físico con el que Postgres las
    devuelva."""
    condiciones = ["workspace_id = %s", "responsable_membership_id = %s",
                  "estado not in ('terminada', 'cancelada')"]
    parametros: list = [workspace_id, membership_id]
    if excluir_tarea_id is not None:
        condiciones.append("id <> %s")
        parametros.append(excluir_tarea_id)
    sql = ("select id, titulo from task where " + " and ".join(condiciones)
          + " order by fecha_objetivo nulls last, id")
    if limite is not None:
        sql += " limit %s"
        parametros.append(limite)
    cur.execute(sql, parametros)
    return [dict(f) for f in cur.fetchall()]


def tareas_activas_de(cur: psycopg.Cursor, workspace_id: str, membership_id: str,
                      *, excluir_tarea_id: str,
                      limite: int = MAX_CANDIDATAS_DEPENDENCIA) -> list[tuple[str, str]]:
    """Las otras tareas activas de una persona (id, título), para elegir con
    botones cuál es la que depende / de la que depende (T2, punto 3: "cuando
    la respuesta es un dato... con botones"). Nunca más de
    `MAX_CANDIDATAS_DEPENDENCIA` (ADR 0007, mismo tope que el modelo)."""
    filas = tareas_activas_de_persona(
        cur, workspace_id, membership_id, excluir_tarea_id=excluir_tarea_id,
        limite=limite)
    return [(str(f["id"]), f["titulo"]) for f in filas]


def detalle_tarea(cur: psycopg.Cursor, tarea_id: str, *,
                  incluir_evidencia: bool = False) -> str:
    """Lectura determinística de una tarea (T2, punto 3: "ver detalle: una
    lectura determinística... no necesita llamada al modelo"): título,
    estado, responsable, fecha objetivo, bloqueos abiertos, dependencias y
    aprobador. `incluir_evidencia` suma la evidencia registrada -- es lo
    que distingue "Ver detalle" de "Ver detalle y evidencia" (§4.6, fila del
    aprobador)."""
    cur.execute(
        """select t.titulo, t.estado, t.fecha_objetivo, t.criterio_aceptacion,
                  i.nombre as responsable_nombre,
                  ap.nombre as aprobador_nombre
             from task t
             left join integrante i on i.membership_id = t.responsable_membership_id
             left join membership m on m.id = t.responsable_membership_id
             left join integrante ap on ap.membership_id = m.aprobador_membership_id
            where t.id = %s""", (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return "Esa tarea ya no está disponible."

    lineas = [f"«{fila['titulo']}»", f"Estado: {_estado_legible(fila['estado'])}",
             f"Responsable: {fila['responsable_nombre'] or 'sin asignar'}"]
    if fila["fecha_objetivo"]:
        lineas.append(f"Fecha objetivo: {fila['fecha_objetivo']:%Y-%m-%d}")
    if fila["criterio_aceptacion"]:
        lineas.append(f"Criterio de aceptación: {fila['criterio_aceptacion']}")
    lineas.append(f"Aprobador: {fila['aprobador_nombre'] or 'sin definir'}")

    bloqueos = bloqueos_abiertos(cur, tarea_id)
    if bloqueos:
        lineas.append("Bloqueos abiertos:")
        lineas.extend(f"- {b['causa']}" for b in bloqueos)

    cur.execute(
        """select d.tipo, o.titulo, o.estado from dependency d
             join task o on o.id = d.origen_task_id
            where d.destino_task_id = %s""", (tarea_id,))
    depende_de = cur.fetchall()
    if depende_de:
        lineas.append("Depende de:")
        lineas.extend(
            f"- «{d['titulo']}» ({_estado_legible(d['estado'])}, {d['tipo']})"
            for d in depende_de)

    cur.execute(
        """select d.tipo, t2.titulo, t2.estado from dependency d
             join task t2 on t2.id = d.destino_task_id
            where d.origen_task_id = %s""", (tarea_id,))
    de_esta_dependen = cur.fetchall()
    if de_esta_dependen:
        lineas.append("De esta tarea dependen:")
        lineas.extend(
            f"- «{d['titulo']}» ({_estado_legible(d['estado'])}, {d['tipo']})"
            for d in de_esta_dependen)

    if incluir_evidencia:
        cur.execute(
            """select tipo, uri from evidence
                where task_id = %s order by at""", (tarea_id,))
        evidencias = cur.fetchall()
        if evidencias:
            lineas.append("Evidencia:")
            lineas.extend(f"- ({e['tipo']}) {e['uri'] or 'sin detalle'}"
                         for e in evidencias)
        else:
            lineas.append("Evidencia: ninguna registrada todavía.")

    return "\n".join(lineas)
