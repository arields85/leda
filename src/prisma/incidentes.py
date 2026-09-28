"""Registro de incidentes y aviso a la administración de plataforma.

Constitución §10: "Los incidentes se registran sanitizados y se avisan al
administrador de plataforma por su canal." Hasta esta unidad (T28, decisión
del usuario, 2026-09-28) eso último no pasaba: cada módulo armaba su propio
`insert into incident` a mano y sólo la persona afectada se enteraba
(`gateway.NOTICIA_NEUTRA_INCIDENTE`) -- quien administra la plataforma recién
se enteraba corriendo `python -m prisma incidentes <slug>`.

`registrar_incidente` es el punto único de escritura en `incident`: inserta
la fila y, en la misma llamada, encola un aviso para cada administrador de
plataforma que tenga el bot de administración vinculado. El fan-out corre del
lado de la base (`avisar_incidente_admin`, `security definer`, migración
0017): necesita leer `platform_role` y `audit_log`, sin concesión de lectura
a `prisma_app`.

El texto del aviso SÍ incluye qué lo disparó -- el mensaje de la persona, o
la acción que tocó -- corrección del usuario sobre el alcance original de
esta unidad (2026-09-28, mismo día): la Constitución §2 ya le da al
administrador de plataforma acceso a las conversaciones privadas entre
Prisma y los integrantes, y §12 dice que ESE acceso se audita, no que haya
que ocultárselo. Lo que §10 exige es que el incidente quede sanitizado --
sin secretos -- no que el aviso salga sin disparador. Por eso este módulo
nunca manda `referencia_cruda` (la traza técnica cruda, que puede traer algo
parecido a un secreto): arma el disparador leyendo `inbound_message` o
`pending_action`, ya con retención por cliente y sin nada de la aplicación.

Cada aviso deja además una fila en `audit_log` (Constitución §12, "el acceso
del administrador a conversaciones también se registra"): una por
administrador realmente avisado, nunca al reprocesar el mismo incidente.

Reusable por el validador de invariantes diario que se agregue después
(`odd/tasks/validador-invariantes.md`): cualquier violación que ese proceso
detecte pasa por este mismo `registrar_incidente`, con `workspace_id` en
`None` cuando el hallazgo no es de un cliente en particular.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from .db import registrar_auditoria

# Qué tipo de fila referencia `incident.referencia_id` -- mismo patrón
# polimórfico que `audit_log.sujeto_tipo`/`sujeto_id`, sin clave foránea:
# apunta a texto o a un toque, nunca lo copia (docs/ROADMAP.md: la retención
# de `inbound_message` es por cliente). Viven acá, no en `gateway.py`, porque
# `_texto_disparador` también los necesita; `gateway` los sigue exponiendo
# con el mismo nombre (los importa de acá) para no romper a quien ya los usa.
REFERENCIA_INBOUND_MESSAGE = "inbound_message"
REFERENCIA_PENDING_ACTION = "pending_action"

# Tope del texto disparador en el aviso -- decisión del usuario, 2026-09-28:
# acotado, y el aviso dice cuándo lo recortó.
LIMITE_TEXTO_DISPARADOR = 1000


def _quien_disparo(cur, app_user_id: str | None) -> str | None:
    """El nombre de la persona identificada, si la hay. Por la vista
    `integrante` (acotada al espacio activo de la sesión): nunca consulta
    `app_user` directo, que es global."""
    if not app_user_id:
        return None
    cur.execute("select nombre from integrante where app_user_id = %s", (app_user_id,))
    fila = cur.fetchone()
    return fila["nombre"] if fila else None


def _texto_disparador(cur, referencia_tipo: str | None,
                      referencia_id: str | None) -> str:
    """Qué disparó el incidente: el texto del mensaje, o la acción que se
    estaba resolviendo cuando falló un toque. Nunca `referencia_cruda` --
    eso es la traza técnica, no el disparador, y puede traer algo parecido
    a un secreto."""
    texto = None
    if referencia_tipo == REFERENCIA_INBOUND_MESSAGE and referencia_id:
        cur.execute("select texto from inbound_message where id = %s",
                    (referencia_id,))
        fila = cur.fetchone()
        texto = fila["texto"] if fila else None
    elif referencia_tipo == REFERENCIA_PENDING_ACTION and referencia_id:
        cur.execute("select resumen from pending_action where id = %s",
                    (referencia_id,))
        fila = cur.fetchone()
        texto = fila["resumen"] if fila else None

    if texto is None:
        return "(sin referencia al mensaje o la acción que lo disparó)"
    if len(texto) > LIMITE_TEXTO_DISPARADOR:
        return (texto[:LIMITE_TEXTO_DISPARADOR]
                + f"… (recortado -- {len(texto)} caracteres en total)")
    return texto


def _texto_aviso_admin(cur, incident_id: str, workspace_id: str | None, *,
                       etapa: str | None, severidad: str, resumen: str,
                       referencia_tipo: str | None,
                       referencia_id: str | None,
                       app_user_id: str | None) -> str:
    slug = None
    if workspace_id is not None:
        cur.execute("select slug from workspace where id = %s", (workspace_id,))
        fila = cur.fetchone()
        slug = fila["slug"] if fila else None

    ahora = datetime.now(timezone.utc)
    return "\n".join((
        f"Incidente {incident_id[:8]} · espacio={slug or 'global'} · "
        f"etapa={etapa or 'sin etapa'} · severidad={severidad} · "
        f"{ahora.strftime('%d/%m %H:%M')} UTC",
        f"Quién: {_quien_disparo(cur, app_user_id) or '(no identificado)'}",
        f"Resumen: {resumen}",
        f"Disparador: {_texto_disparador(cur, referencia_tipo, referencia_id)}",
    ))


def avisar_incidente_admin(cur, incident_id: str, *, workspace_id: str | None,
                           cuerpo: str, referencia_tipo: str | None = None,
                           referencia_id: str | None = None) -> list[str]:
    """Encola `cuerpo` para cada administrador de plataforma alcanzable y
    deja un `audit_log` por cada uno realmente avisado ahora (Constitución
    §12) -- nunca duplicado al reprocesar el mismo incidente: la base sólo
    devuelve el administrador cuando el `insert` en `admin_notice` fue
    nuevo, no cuando ya existía.

    "Alcanzable" es haberle escrito al menos una vez al bot de
    administración (`gateway.procesar_update`, canal ADMINISTRACION,
    `accion='mensaje_admin'` en `audit_log`): Telegram no deja que un bot le
    escriba primero a alguien que nunca le escribió.

    `referencia_tipo`/`referencia_id` -- el `inbound_message` o la
    `pending_action` que `cuerpo` ya cita como disparador -- quedan en el
    `audit_log` como `sujeto_tipo`/`sujeto_id` (Constitución §12: "el acceso
    del administrador a conversaciones también se registra"), nunca su
    texto: eso ya está en `admin_notice.cuerpo`, no hace falta copiarlo acá.

    Devuelve el `app_user_id` de cada administrador recién avisado."""
    cur.execute(
        "select app_user_id from avisar_incidente_admin(%s, %s, %s)",
        (incident_id, workspace_id, cuerpo))
    avisados = [str(fila["app_user_id"]) for fila in cur.fetchall()]

    for admin_app_user_id in avisados:
        registrar_auditoria(
            cur, accion="aviso_incidente_admin", workspace_id=workspace_id,
            actor_app_user_id=admin_app_user_id, actor_kind="prisma",
            sujeto_tipo=referencia_tipo, sujeto_id=referencia_id,
            detalle={"incident_id": incident_id})
    return avisados


def registrar_incidente(cur, workspace_id: str | None, resumen: str, *,
                        severidad: str = "media",
                        referencia_cruda: str | None = None,
                        etapa: str | None = None,
                        referencia_tipo: str | None = None,
                        referencia_id: str | None = None,
                        chat_id: int | None = None,
                        app_user_id: str | None = None,
                        notificado_en=None) -> str:
    """Inserta un incidente sanitizado y avisa a la administración de
    plataforma (Constitución §10). Helper compartido para que quien necesite
    registrar un incidente no arme el insert a mano en cada lugar nuevo.

    `resumen` es legible para una persona y no lleva texto de mensajes;
    `referencia_cruda` es la traza técnica completa (tipo y mensaje de la
    excepción), sólo para quien administra -- nunca sale en el aviso a la
    administración tampoco: puede traer algo parecido a un secreto, y el
    disparador que el aviso SÍ muestra sale de `inbound_message`/
    `pending_action`, no de la excepción. `referencia_tipo` + `referencia_id`
    apuntan a la fila que originó esto -- el `inbound_message` o la
    `pending_action` -- sin copiar su contenido acá: el texto se abre desde
    ahí, bajo la retención por cliente que define `docs/ROADMAP.md`.
    `workspace_id` puede ser `None` para un hecho global, sin cliente en
    particular (p. ej. el validador de invariantes).

    `notificado_en` es sobre el aviso a la PERSONA afectada -- lo resuelve
    quien llama, como ya hacía `gateway.reportar_incidente_no_manejado`. El
    aviso a la administración lo resuelve esta función sola y queda en
    `notificado_admin_en`, sin mentir si nadie era alcanzable: se lo nota
    dentro del propio `resumen`, igual que ya se hacía para la persona.

    Devuelve el id del incidente insertado."""
    incident_id = str(uuid.uuid4())

    cuerpo_aviso = _texto_aviso_admin(
        cur, incident_id, workspace_id, etapa=etapa, severidad=severidad,
        resumen=resumen, referencia_tipo=referencia_tipo,
        referencia_id=referencia_id, app_user_id=app_user_id)
    avisados = avisar_incidente_admin(
        cur, incident_id, workspace_id=workspace_id, cuerpo=cuerpo_aviso,
        referencia_tipo=referencia_tipo, referencia_id=referencia_id)

    resumen_final = resumen
    notificado_admin_en = None
    if avisados:
        notificado_admin_en = datetime.now(timezone.utc)
    else:
        resumen_final += (" No se avisó a la administración: ningún "
                          "administrador de plataforma tiene el bot de "
                          "administración vinculado.")

    cur.execute(
        """insert into incident (id, workspace_id, severidad, resumen_sanitizado,
                                 referencia_cruda, etapa, referencia_tipo,
                                 referencia_id, chat_id, app_user_id,
                                 notificado_en, notificado_admin_en)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (incident_id, workspace_id, severidad, resumen_final, referencia_cruda,
         etapa, referencia_tipo, referencia_id, chat_id, app_user_id,
         notificado_en, notificado_admin_en))
    return incident_id
