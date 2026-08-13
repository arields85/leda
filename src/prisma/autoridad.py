"""Capa de autoridad.

Todo lo que la constitución dice que Prisma no puede hacer se verifica acá,
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
        """select i.app_user_id, i.membership_id, i.area_id,
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
        rol_slug=m["slug"], area_id=str(m["area_id"]),
        autoridad_final=m["autoridad_final"])


def identificar_administrador(cur: psycopg.Cursor,
                              telegram_user_id: int) -> Solicitante:
    """Identifica en el canal de administración. Requiere rol prisma_admin,
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
            """select u.id as app_user_id, m.id as membership_id, m.area_id,
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
    if accion in ("crear_tarea", "actualizar_estado", "registrar_bloqueo",
                  "adjuntar_evidencia", "consultar"):
        return

    raise Denegado("No tenés permiso para eso en este equipo.")


def puede_aprobar_tarea(cur: psycopg.Cursor, quien: Solicitante,
                        responsable_membership_id: str) -> bool:
    """La aprobación sube un nivel: a un integrante lo aprueba su referente,
    a un referente lo aprueba Dirección.

    Tener la decisión final del equipo **no** habilita a firmar trabajo
    técnico de cualquier área. La autoridad final sirve para desempatar y
    fijar prioridades; la autoridad técnica sigue siendo de cada referente.
    """
    cur.execute(
        "select aprobador_membership_id from membership where id = %s",
        (responsable_membership_id,))
    fila = cur.fetchone()
    if not fila:
        return False
    return str(fila["aprobador_membership_id"] or "") == str(quien.membership_id)


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
