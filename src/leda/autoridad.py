"""Capa de autoridad.

Todo lo que la constitución dice que Leda no puede hacer se verifica acá,
del lado del servidor, antes de tocar la base. No es una instrucción en el
prompt: es una función que se ejecuta sí o sí.

La regla que ordena todo el módulo: **el sombrero lo define el canal.** Quien
escribe por el bot de un espacio es tratado según su rol en ese espacio,
aunque sea administrador de plataforma. Las acciones de administración sólo
existen en el canal de administración.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import psycopg


class Canal(str, Enum):
    ESPACIO = "espacio"
    ADMINISTRACION = "administracion"


class Denegado(Exception):
    pass


@dataclass(frozen=True)
class Solicitante:
    app_user_id: str
    canal: Canal
    workspace_id: str | None = None
    membership_id: str | None = None
    nombre: str | None = None
    rol_slug: str | None = None
    area_id: str | None = None
    autoridad_final: bool = False


# Acciones que sólo existen en el canal de administración.
ACCIONES_PLATAFORMA = {
    "crear_espacio", "importar_pack", "activar_espacio", "editar_configuracion",
    "cambiar_modelo", "ver_incidentes", "leer_conversaciones", "ejecutar_respaldo",
}

# Acciones que la constitución prohíbe siempre, en cualquier canal.
PROHIBIDAS = {
    "operar_maquina", "modificar_plc", "cambiar_produccion", "modificar_infraestructura",
    "acceder_credenciales", "modificar_base_productiva", "comprometer_comercialmente",
    "comunicar_externo", "ampliar_autoridad_propia",
}

# Acciones que exigen confirmación humana antes de ejecutarse.
REQUIEREN_CONFIRMACION = {
    "enviar_mensaje_no_rutinario", "enviar_correo", "crear_evento",
    "cambiar_responsable", "cambiar_fecha", "cerrar_objetivo",
}


def identificar_en_espacio(cur: psycopg.Cursor, telegram_user_id: int,
                           workspace_id: str) -> Solicitante:
    """Identifica a un integrante dentro del espacio activo.

    Consulta la vista `integrante`, que ya está acotada al espacio. Así el
    gateway no necesita permisos de administración para atender una
    conversación de equipo: si la persona no es de este equipo, sencillamente
    no aparece.
    """
    cur.execute(
        """select i.app_user_id, i.membership_id, i.nombre, i.area_id,
                  r.slug, r.autoridad_final
             from integrante i join rol r on r.id = i.rol_id
            where i.telegram_user_id = %s and i.activo""",
        (telegram_user_id,))
    m = cur.fetchone()
    if not m:
        raise Denegado("No pertenecés a este equipo.")

    return Solicitante(
        app_user_id=str(m["app_user_id"]), canal=Canal.ESPACIO,
        workspace_id=workspace_id, membership_id=str(m["membership_id"]),
        nombre=m["nombre"],
        rol_slug=m["slug"], area_id=str(m["area_id"]),
        autoridad_final=m["autoridad_final"])


def identificar_administrador(cur: psycopg.Cursor,
                              telegram_user_id: int) -> Solicitante:
    """Identifica en el canal de administración. Requiere rol leda_admin,
    porque tiene que leer tablas globales."""
    cur.execute(
        """select u.id from app_user u
             join platform_role p on p.app_user_id = u.id
            where u.telegram_user_id = %s and p.rol = 'administrador'""",
        (telegram_user_id,))
    fila = cur.fetchone()
    if not fila:
        raise Denegado("No sos administrador de plataforma.")
    return Solicitante(app_user_id=str(fila["id"]), canal=Canal.ADMINISTRACION)


def identificar(cur: psycopg.Cursor, telegram_user_id: int, canal: Canal,
                workspace_id: str | None) -> Solicitante:
    """Despacha según el canal. El canal define el sombrero, siempre."""
    if canal is Canal.ADMINISTRACION:
        return identificar_administrador(cur, telegram_user_id)
    if workspace_id is None:
        raise Denegado("Falta el espacio de trabajo.")
    try:
        return identificar_en_espacio(cur, telegram_user_id, workspace_id)
    except Denegado:
        pass

    # La vista sólo devuelve filas cuando hay un espacio activo declarado.
    # Bajo rol de administración eso no pasa, así que se consulta directo; si
    # no hay privilegio para hacerlo, la persona sencillamente no es de acá.
    try:
        cur.execute(
            """select u.id as app_user_id, u.nombre, m.id as membership_id, m.area_id,
                      r.slug, r.autoridad_final
                 from membership m
                 join app_user u on u.id = m.app_user_id
                 join rol r on r.id = m.rol_id
                where m.workspace_id = %s and u.telegram_user_id = %s and m.activo""",
            (workspace_id, telegram_user_id))
    except psycopg.errors.InsufficientPrivilege:
        raise Denegado("No pertenecés a este equipo.") from None

    m = cur.fetchone()
    if not m:
        raise Denegado("No pertenecés a este equipo.")
    return Solicitante(
        app_user_id=str(m["app_user_id"]), canal=canal,
        workspace_id=workspace_id, membership_id=str(m["membership_id"]),
        nombre=m["nombre"],
        rol_slug=m["slug"], area_id=str(m["area_id"]),
        autoridad_final=m["autoridad_final"])


def verificar(cur: psycopg.Cursor, quien: Solicitante, accion: str,
              *, area_id: str | None = None) -> None:
    """Lanza Denegado si la acción no está permitida. No devuelve nada:
    o pasa, o corta."""

    if accion in PROHIBIDAS:
        raise Denegado(
            "Eso está fuera de lo que puedo hacer, en cualquier caso.")

    if accion in ACCIONES_PLATAFORMA:
        if quien.canal is not Canal.ADMINISTRACION:
            # Puede ser administrador y estar escribiendo por el bot del
            # equipo. El canal manda.
            raise Denegado(
                "Eso se hace desde la consola de administración, no por acá.")
        return

    if quien.canal is Canal.ADMINISTRACION:
        raise Denegado(
            "Esta acción pertenece a un espacio de trabajo y este canal no lo es.")

    if accion in ("aprobar_tarea", "aprobar_objetivo"):
        _verificar_aprobacion(cur, quien, accion, area_id)
        return

    if accion in ("definir_prioridad_general", "aprobar_plan", "declarar_urgencia"):
        if not quien.autoridad_final:
            raise Denegado(
                "Eso lo define quien tiene la decisión final en el equipo.")
        return

    cur.execute(
        """select 1 from permission p join membership m on m.rol_id = p.rol_id
            where m.id = %s and p.accion = %s""",
        (quien.membership_id, accion))
    if cur.fetchone():
        return

    # Sin regla explícita, las acciones de gestión corriente están permitidas
    # a cualquier integrante; las de decisión, no.
    #
    # "crear_objetivo" se agregó acá al separarla de "crear_tarea"
    # (`herramientas.py`, `_crear_objetivo`): antes compartían acción, así
    # que un permiso o una restricción sobre "crear_tarea" alcanzaba también
    # a crear objetivos sin que nadie lo hubiera decidido así. Separarlas sin
    # agregar "crear_objetivo" acá le habría cambiado el comportamiento a
    # cualquier equipo existente, de permitido a denegado, sin que fuera la
    # intención de esta corrección.
    if accion in ("crear_tarea", "crear_objetivo", "actualizar_estado",
                  "registrar_bloqueo", "adjuntar_evidencia", "consultar"):
        return

    raise Denegado("No tenés permiso para eso en este equipo.")


def quien_revisa_la_tarea(cur: psycopg.Cursor, task_id) -> str | None:
    """Quién revisa el trabajo de una tarea: el que quedó escrito en ella cuando cambió de manos
    o, si nunca cambió, quien aprueba el trabajo de su responsable (C-7, delegar). La regla es
    una sola y vive en la base (`quien_revisa_la_tarea`)."""
    cur.execute("select quien_revisa_la_tarea(%s) as quien", (str(task_id),))
    fila = cur.fetchone()
    return str(fila["quien"]) if fila and fila["quien"] else None


def puede_revisar_la_tarea(cur: psycopg.Cursor, quien: Solicitante, task_id) -> bool:
    """Si quien escribe revisa el trabajo de esa tarea: aprueba su entrega o le pide cambios.

    La aprobación sube un nivel: a un integrante lo aprueba su referente, a un referente lo
    aprueba Dirección (`membership.aprobador_membership_id`). Tener la decisión final del equipo
    **no** habilita a firmar trabajo técnico de cualquier área: la autoridad final sirve para
    desempatar y fijar prioridades; la autoridad técnica sigue siendo de cada referente. Una
    tarea que pasó a otra persona la sigue revisando quien la revisaba (ADR 0017, enmienda a la
    decisión 2: "el trabajo lo sigue revisando el aprobador de la tarea original")."""
    return quien_revisa_la_tarea(cur, task_id) == str(quien.membership_id)


@dataclass(frozen=True)
class ReglaDelPase:
    """Lo que dice la regla de un pase entre dos personas (ADR 0017, enmienda a la decisión 2):
    quién lo decide o, si no se puede, por qué y, si un integrante pide pasarla a otro sector, el
    encargado de su sector, que es quien lo decide."""

    decide: str | None = None
    no_se_puede: str | None = None
    lo_decide: str | None = None


def encargado_del_sector(cur: psycopg.Cursor, membership_id: str) -> str | None:
    """El encargado del sector de una persona: el referente del área de su membresía."""
    cur.execute("""select a.referente_membership_id from membership m
                     join area a on a.id = m.area_id where m.id = %s""", (membership_id,))
    fila = cur.fetchone()
    return str(fila["referente_membership_id"]) if fila and fila["referente_membership_id"] \
        else None


def regla_del_pase(cur: psycopg.Cursor, pide: str, recibe: str) -> ReglaDelPase:
    """Quién puede pedir un pase y quién lo decide (ADR 0017, enmienda a la decisión 2).

    - El encargado de un sector (el referente de su área) le puede pasar una tarea a cualquiera;
      un integrante, sólo a alguien de su sector. Si pide pasarla a otro sector, no se puede, y
      lo decide el encargado de su sector, una persona concreta.
    - Decide el encargado del sector de quien recibe (si es quien pide, su pedido es la
      decisión; si es quien recibe, decide con su respuesta). Sin encargado, no hay quien
      decida: no se puede. Dirección no interviene por ser Dirección."""
    cur.execute("select id, area_id from membership where id = any(%s::uuid[])",
                ([pide, recibe],))
    areas = {str(f["id"]): str(f["area_id"]) for f in cur.fetchall()}
    encargado_de_quien_pide = encargado_del_sector(cur, pide)
    if encargado_de_quien_pide != pide and areas.get(pide) != areas.get(recibe):
        return ReglaDelPase(no_se_puede="otro_sector", lo_decide=encargado_de_quien_pide)
    decide = encargado_del_sector(cur, recibe)
    if decide is None:
        return ReglaDelPase(no_se_puede="sin_encargado")
    return ReglaDelPase(decide=decide)


def _verificar_aprobacion(cur, quien: Solicitante, accion: str,
                          area_id: str | None) -> None:
    if accion == "aprobar_tarea":
        # El chequeo real necesita saber de quién es la tarea, así que lo hace
        # la herramienta con el responsable ya resuelto.
        return

    # Objetivos e hitos sí van por política de área.
    cur.execute(
        """select p.id from approval_policy p
            where p.workspace_id = %s and p.sujeto = 'objetivo_operativo'""",
        (quien.workspace_id,))
    pol = cur.fetchone()
    if not pol:
        raise Denegado("No hay política de aprobación definida para eso.")

    cur.execute(
        """select 1 from approval_requirement r
            where r.approval_policy_id = %s
              and ((r.tipo = 'rol'
                    and r.rol_id = (select rol_id from membership where id = %s)
                    and (r.area_id is null
                         or r.area_id = (select area_id from membership where id = %s)))
                or (r.tipo = 'area'
                    and r.area_id = (select area_id from membership where id = %s))
                or (r.tipo = 'cada_area_participante'))""",
        (pol["id"], quien.membership_id, quien.membership_id, quien.membership_id))
    if not cur.fetchone():
        raise Denegado("No sos quien aprueba este tipo de trabajo.")


def requiere_confirmacion(accion: str) -> bool:
    return accion in REQUIEREN_CONFIRMACION
