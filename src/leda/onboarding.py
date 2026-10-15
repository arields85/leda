"""Alta de integrantes en Telegram.

Telegram no deja que un bot escriba primero a alguien que nunca interactuó con
él. Por eso cada persona tiene que abrir un enlace y apretar Iniciar una vez.
Recién ahí Leda puede hacerle seguimiento privado.

El punto delicado es la entrega de esos enlaces. Un enlace contiene un token
que vincula un identificador de Telegram con una persona del equipo: **si se
publica en el grupo, cualquiera puede reclamar la identidad de otro** y pasar
a recibir su seguimiento. Van uno a uno, siempre.

Precauciones que este módulo aplica:
  - token largo y aleatorio;
  - la base guarda sólo su huella (migración 0084): quien lea la tabla no puede canjearlo;
  - un solo uso;
  - vencimiento;
  - un enlace vigente por persona;
  - una cuenta de Telegram que ya es de alguien de este equipo no puede canjear otro token.

Quien ya está en otro espacio (J7-5): al abrir el enlace con su Telegram, la membresía nueva queda
unida a su cuenta (el mismo `app_user`). Lo decide sólo quien abre el enlace, nunca el nombre.

Sin activar, la persona existe igual: tiene tareas, aparece en los informes y
cuenta para el cierre de un objetivo. Lo único que falta es el canal privado.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import psycopg

from .salida import enqueue_outbox

VIGENCIA = timedelta(days=14)


class ActivacionInvalida(Exception):
    pass


@dataclass
class Activacion:
    """Cómo terminó un canje: la persona vinculada, su membresía y si su cuenta ya era de
    alguien de otro espacio (quedó unida)."""
    nombre: str
    membership_id: str
    cuenta_unida: bool


def huella_del_token(token: str) -> str:
    """La huella con que la base guarda el token de un enlace (sha256, en hexadecimal)."""
    return hashlib.sha256(token.encode()).hexdigest()


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
                 (workspace_id, membership_id, token_hash, expira_en, creado_por)
               values (%s, %s, %s, %s, %s)""",
            (workspace_id, p["membership_id"], huella_del_token(token), expira, creado_por))
        enlaces.append(Enlace(
            nombre=p["nombre"], membership_id=str(p["membership_id"]),
            token=token, url=f"https://t.me/{bot_username}?start={token}",
            expira_en=expira))
    return enlaces


def activar(cur: psycopg.Cursor, workspace_id: str, token: str,
            telegram_user_id: int, ahora: datetime | None = None) -> str:
    """Canjea un token. Devuelve el nombre de la persona vinculada."""
    return canjear(cur, workspace_id, token, telegram_user_id, ahora).nombre


def canjear(cur: psycopg.Cursor, workspace_id: str, token: str,
            telegram_user_id: int, ahora: datetime | None = None) -> Activacion:
    """Canjea un token: vincula la cuenta de Telegram de quien lo abrió con la persona del enlace.

    Si esa cuenta ya es de alguien de otro espacio, la membresía del enlace pasa a esa cuenta (el
    mismo `app_user`): una persona, una cuenta. Si ya es de alguien de este equipo, se rechaza. Se
    busca sólo por la cuenta que abrió el enlace, nunca por el nombre.

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
            where t.token_hash = %s and t.workspace_id = %s and m.workspace_id = %s
              for update of t, m""",
        (huella_del_token(token), workspace_id, workspace_id))
    fila = cur.fetchone()

    if not fila:
        raise ActivacionInvalida("Ese enlace no es válido.")
    if fila["usado_en"] is not None:
        raise ActivacionInvalida("Ese enlace ya se usó.")
    if fila["expira_en"] < ahora:
        raise ActivacionInvalida("Ese enlace venció.")
    if fila["telegram_user_id"] is not None:
        raise ActivacionInvalida("Esa persona ya está activada.")

    # Una cuenta de Telegram es de una sola persona. Si ya es de alguien de este equipo, no toma
    # otra identidad; si es de alguien de otro espacio, es la misma persona que ahora también
    # está en este: la membresía nueva pasa a su cuenta (J7-5). La persona que el enlace había
    # creado queda sin membresía y sin Telegram: no se borra (la auditoría la puede nombrar).
    cur.execute("select id, nombre from app_user where telegram_user_id = %s for update",
                (telegram_user_id,))
    ya = cur.fetchone()
    unida = False
    if ya:
        cur.execute("select 1 from membership where workspace_id = %s and app_user_id = %s",
                    (workspace_id, ya["id"]))
        if cur.fetchone():
            raise ActivacionInvalida("Esa cuenta de Telegram ya está en uso.")
        cur.execute("update membership set app_user_id = %s where id = %s",
                    (ya["id"], fila["membership_id"]))
        nombre, unida = ya["nombre"], True
    else:
        cur.execute("update app_user set telegram_user_id = %s where id = %s",
                    (telegram_user_id, fila["app_user_id"]))
        nombre = fila["nombre"]
    cur.execute(
        "update activation_token set usado_en = %s, usado_por = %s where id = %s",
        (ahora, telegram_user_id, fila["id"]))
    return Activacion(nombre=nombre, membership_id=str(fila["membership_id"]),
                      cuenta_unida=unida)


def bienvenida(cur: psycopg.Cursor, workspace_id: str, nombre: str) -> str:
    cur.execute(
        """select p.nombre_visible, w.nombre as equipo
             from persona_config p join workspace w on w.id = p.workspace_id
            where p.workspace_id = %s""",
        (workspace_id,))
    c = cur.fetchone() or {}
    visible = c.get("nombre_visible", "Leda")
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
             f"venís y si te falta algo para seguir. Si un mensaje no necesita "
             f"respuesta te lo aclaro.")
    if abiertas:
        # Singular or plural as a person says it, never "tarea(s) abierta(s)".
        tareas = "1 tarea abierta" if abiertas == 1 else f"{abiertas} tareas abiertas"
        texto += f"\n\nAhora tenés {tareas}. Escribime «qué tengo» cuando quieras verlas."
    return texto


# El ofrecimiento de la web en la bienvenida (decisión 2 del usuario, 2026-10-12; ADR 0024,
# decisiones 1 y 2), texto fijo como la bienvenida: el despachador pone el botón debajo, "Mi
# espacio" (MA-4; a Dirección la abre en "Mi área"), que abre la web como Mini App. En pocas palabras, sin
# explicar dónde se abre (MA-4).
# Una plantilla, nunca un texto para mandar tal cual (revisión R3-welcome-template): se arma con
# `ofrecimiento_de_la_web`.
_PLANTILLA_DEL_OFRECIMIENTO = "También podés ver {que} en la web: tocá «{boton}» cuando quieras."


def ofrecimiento_de_la_web(destino: str) -> str:
    """El ofrecimiento de la bienvenida, con lo que dice su botón."""
    from .despachador import ETIQUETA_DEL_BOTON_DE_LA_WEB

    return _PLANTILLA_DEL_OFRECIMIENTO.format(
        que="lo que hace el equipo" if destino == "equipo" else "tus tareas",
        boton=ETIQUETA_DEL_BOTON_DE_LA_WEB[destino])


def destino_de_la_bienvenida(cur: psycopg.Cursor, membership_id: str) -> str:
    """A Dirección, el equipo; a los demás, sus tareas (ADR 0024, decisión 2)."""
    cur.execute("""select r.autoridad_final from membership m join rol r on r.id = m.rol_id
                    where m.id = %s""", (membership_id,))
    fila = cur.fetchone()
    return "equipo" if fila and fila["autoridad_final"] else "inicio"


def ofrecer_la_web_en_la_bienvenida(cur: psycopg.Cursor, membership_id: str) -> bool:
    """Si la bienvenida lleva el ofrecimiento de la web, y entonces lo reserva (`ofrecimiento_
    web`, en la misma transacción que la encola): a quien nunca entró ni se le ofreció, con la
    dirección pública configurada y sin otro mensaje con su enlace por salir. Corre con la
    conexión administrativa (`admin()`), como la bienvenida."""
    from . import web_app
    from .config import config

    return bool(config.base_url) and not (
        web_app.ya_se_le_ofrecio(cur, membership_id)
        or web_app.entro_alguna_vez_como_administracion(cur, membership_id)
        or web_app.tiene_un_enlace_por_salir(cur, membership_id)
    ) and web_app.reservar_el_ofrecimiento(cur, membership_id)


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
    return enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=fila["grupo_chat_id"], text=texto,
        message_type="informativo", scheduled_for=ahora,
        dedupe_key=f"{workspace_id}:presentacion", allow_split=True,
    ) > 0


def pendientes_de_activar(cur: psycopg.Cursor, workspace_id: str) -> list[str]:
    cur.execute(
        """select u.nombre from membership m join app_user u on u.id = m.app_user_id
            where m.workspace_id = %s and m.activo
              and u.telegram_user_id is null
            order by u.nombre""",
        (workspace_id,))
    return [f["nombre"] for f in cur.fetchall()]
