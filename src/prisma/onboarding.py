"""Alta de integrantes en Telegram.

Telegram no deja que un bot escriba primero a alguien que nunca interactuó con
él. Por eso cada persona tiene que abrir un enlace y apretar Iniciar una vez.
Recién ahí Prisma puede hacerle seguimiento privado.

El punto delicado es la entrega de esos enlaces. Un enlace contiene un token
que vincula un identificador de Telegram con una persona del equipo: **si se
publica en el grupo, cualquiera puede reclamar la identidad de otro** y pasar
a recibir su seguimiento. Van uno a uno, siempre.

Precauciones que este módulo aplica:
  - token largo y aleatorio;
  - un solo uso;
  - vencimiento;
  - un enlace vigente por persona;
  - una cuenta de Telegram ya vinculada no puede canjear otro token.

Sin activar, la persona existe igual: tiene tareas, aparece en los informes y
cuenta para el cierre de un objetivo. Lo único que falta es el canal privado.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import psycopg

VIGENCIA = timedelta(days=14)


class ActivacionInvalida(Exception):
    pass


@dataclass
class Enlace:
    nombre: str
    membership_id: str
    token: str
    url: str
    expira_en: datetime


def generar_enlaces(cur: psycopg.Cursor, workspace_id: str, bot_username: str,
                    *, creado_por: str | None = None,
                    solo: list[str] | None = None,
                    ahora: datetime | None = None) -> list[Enlace]:
    """Un enlace por persona sin activar. Invalida los anteriores."""
    ahora = ahora or datetime.now(timezone.utc)
    expira = ahora + VIGENCIA

    # Consulta directa, no la vista: esto corre bajo permisos de
    # administración y la vista sólo devuelve filas cuando hay un espacio
    # activo declarado en la sesión.
    cur.execute(
        """select m.id as membership_id, u.nombre
             from membership m join app_user u on u.id = m.app_user_id
            where m.workspace_id = %s and m.activo
              and u.telegram_user_id is null
            order by u.nombre""",
        (workspace_id,))
    personas = cur.fetchall()
    if solo:
        buscados = {s.lower() for s in solo}
        personas = [p for p in personas
                    if any(b in p["nombre"].lower() for b in buscados)]

    enlaces: list[Enlace] = []
    for p in personas:
        # Regenerar invalida el anterior: el índice parcial sólo admite uno
        # sin usar por persona.
        cur.execute(
            "delete from activation_token where membership_id = %s and usado_en is null",
            (p["membership_id"],))
        token = secrets.token_urlsafe(24)
        cur.execute(
            """insert into activation_token
                 (workspace_id, membership_id, token, expira_en, creado_por)
               values (%s, %s, %s, %s, %s)""",
            (workspace_id, p["membership_id"], token, expira, creado_por))
        enlaces.append(Enlace(
            nombre=p["nombre"], membership_id=str(p["membership_id"]),
            token=token, url=f"https://t.me/{bot_username}?start={token}",
            expira_en=expira))
    return enlaces


def activar(cur: psycopg.Cursor, workspace_id: str, token: str,
            telegram_user_id: int, ahora: datetime | None = None) -> str:
    """Canjea un token. Devuelve el nombre de la persona vinculada.

    Corre con permisos de administración: tiene que escribir en app_user, que
    es una tabla global.
    """
    ahora = ahora or datetime.now(timezone.utc)

    cur.execute(
        """select t.id, t.membership_id, t.expira_en, t.usado_en,
                  m.app_user_id, u.nombre, u.telegram_user_id
             from activation_token t
             join membership m on m.id = t.membership_id
             join app_user u on u.id = m.app_user_id
            where t.token = %s and t.workspace_id = %s""",
        (token, workspace_id))
    fila = cur.fetchone()

    if not fila:
        raise ActivacionInvalida("Ese enlace no es válido.")
    if fila["usado_en"] is not None:
        raise ActivacionInvalida("Ese enlace ya se usó.")
    if fila["expira_en"] < ahora:
        raise ActivacionInvalida("Ese enlace venció.")
    if fila["telegram_user_id"] is not None:
        raise ActivacionInvalida("Esa persona ya está activada.")

    # Una cuenta de Telegram no puede quedar vinculada a dos personas.
    cur.execute("select nombre from app_user where telegram_user_id = %s",
                (telegram_user_id,))
    ya = cur.fetchone()
    if ya:
        raise ActivacionInvalida("Esa cuenta de Telegram ya está en uso.")

    cur.execute("update app_user set telegram_user_id = %s where id = %s",
                (telegram_user_id, fila["app_user_id"]))
    cur.execute(
        "update activation_token set usado_en = %s, usado_por = %s where id = %s",
        (ahora, telegram_user_id, fila["id"]))
    return fila["nombre"]


def bienvenida(cur: psycopg.Cursor, workspace_id: str, nombre: str) -> str:
    cur.execute(
        """select p.nombre_visible, w.nombre as equipo
             from persona_config p join workspace w on w.id = p.workspace_id
            where p.workspace_id = %s""",
        (workspace_id,))
    c = cur.fetchone() or {}
    visible = c.get("nombre_visible", "Prisma")
    equipo = c.get("equipo", "el equipo")

    cur.execute(
        """select count(*) n from task t
            where t.workspace_id = %s
              and t.responsable_membership_id in
                  (select m.id from membership m join app_user u on u.id = m.app_user_id
                    where m.workspace_id = %s and u.nombre = %s)
              and t.estado in ('asignada','en_curso','bloqueada')""",
        (workspace_id, workspace_id, nombre))
    abiertas = (cur.fetchone() or {}).get("n", 0)

    texto = (f"Listo, {nombre.split()[0]}. Soy {visible} y desde acá te voy a "
             f"hacer el seguimiento de {equipo}.\n\n"
             f"Te voy a escribir un par de veces por semana para ver cómo "
             f"venís y si algo te está trabando. Si un mensaje no necesita "
             f"respuesta te lo aclaro.")
    if abiertas:
        texto += f"\n\nAhora mismo tenés {abiertas} tarea(s) abierta(s). "\
                 f"Escribime «qué tengo» cuando quieras verlas."
    return texto


def presentacion(cur: psycopg.Cursor, workspace_id: str) -> str | None:
    cur.execute("select presentacion from persona_config where workspace_id = %s",
                (workspace_id,))
    fila = cur.fetchone()
    return fila["presentacion"] if fila else None


def encolar_presentacion(cur: psycopg.Cursor, workspace_id: str,
                         ahora: datetime | None = None) -> bool:
    """Publica la presentación en el grupo. Sin los enlaces: esos van aparte."""
    ahora = ahora or datetime.now(timezone.utc)
    texto = presentacion(cur, workspace_id)
    if not texto:
        return False
    cur.execute("select grupo_chat_id from workspace where id = %s", (workspace_id,))
    fila = cur.fetchone()
    if not fila or not fila["grupo_chat_id"]:
        return False
    cur.execute(
        """insert into message_outbox
             (workspace_id, chat_id, tipo, cuerpo, estado, programado_para, dedupe_key)
           values (%s, %s, 'informativo', %s, 'listo', %s, %s)
           on conflict (dedupe_key) do nothing""",
        (workspace_id, fila["grupo_chat_id"], texto, ahora,
         f"{workspace_id}:presentacion"))
    return cur.rowcount > 0


def pendientes_de_activar(cur: psycopg.Cursor, workspace_id: str) -> list[str]:
    cur.execute(
        """select u.nombre from membership m join app_user u on u.id = m.app_user_id
            where m.workspace_id = %s and m.activo
              and u.telegram_user_id is null
            order by u.nombre""",
        (workspace_id,))
    return [f["nombre"] for f in cur.fetchall()]
