"""Saludo diario (pack 06).

`docs/decisions/0010-correo-verificado-y-google-en-el-producto.md` deja el
saludo diario explícitamente fuera de su alcance ("unidades de la línea
principal, no de esta decisión"): este módulo vive en `main`, no en la rama
auxiliar de correo y Google.

Un saludo por hora local del espacio (`workspace.zona_horaria`), como mucho
una vez por persona y por fecha local -- nunca de nuevo por una conversación
nueva, `/new`, `/reset` ni un período de inactividad dentro del mismo día. El
mecanismo de referencia
(`PRISMA-PACK-RECONSTRUCCION-20260925/06-SALUDOS-TONO-E-ICONOGRAFIA.md` y sus
anexos `incorporacion-greeting_for.py.txt`/`incorporacion-claim_greeting.py.
txt`/`incorporacion-complete_greeting_claim.py.txt`/`incorporacion-
make_daily_greeting_hooks.py.txt`, la implementación anterior del propio
usuario) le pedía al modelo, con una instrucción de sistema, que no volviera
a saludar -- y el propio pack registra que esa instrucción positiva sola no
alcanzaba: el modelo volvía a saludar por iniciativa propia en una sesión
nueva. Acá "no saludar de nuevo" nunca depende del modelo: el servidor decide
y antepone el saludo de forma determinística, antes de que el texto llegue a
`message_outbox` (`salida.enqueue_outbox`).

Diferencia con el mecanismo de referencia: ahí la reserva era un diccionario
en memoria de un solo proceso, con un `claim`/`complete` en dos pasos porque
"el hook posterior a la generación no es necesariamente un recibo de entrega
de Telegram" (pack 06 §4). Acá la reserva es una fila en PostgreSQL
(`greeting_state`) y el `claim` corre en la MISMA transacción que arma la
respuesta del turno: si el turno se revierte, la reserva se revierte con él,
así que nunca queda alguien marcado como saludado sin que el saludo haya
salido de verdad -- no hace falta un segundo paso "completar" aparte.
Llamarla más de una vez dentro del mismo turno para la misma persona es
segura: sólo la primera gana (Postgres ve sus propios cambios sin confirmar
dentro de la misma transacción), así que ningún punto de salida de
`agente.py`/`gateway.py` necesita acordarse "ya saludé en este turno".
"""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

import psycopg

from .autoridad import Solicitante

SALUDO_MADRUGADA = "👋 Buenas noches"
SALUDO_MANANA = "👋 Buen día"
SALUDO_TARDE = "👋 Buenas tardes"


def saludo_por_hora(hora_local: int) -> str:
    """El saludo exacto de pack 06 §2 por hora local (0-23): 05:00-11:59
    Buen día, 12:00-19:59 Buenas tardes, el resto (20:00-04:59, cruzando
    medianoche) Buenas noches."""
    if 5 <= hora_local < 12:
        return SALUDO_MANANA
    if 12 <= hora_local < 20:
        return SALUDO_TARDE
    return SALUDO_MADRUGADA


def zona_de_workspace(cur: psycopg.Cursor, workspace_id: str) -> ZoneInfo:
    """La zona horaria del espacio, sin depender de que exista
    `work_calendar` (a diferencia de `calendario.Calendario.desde_base`): el
    saludo tiene que poder calcularse incluso antes del alta guiada, en el
    primer `/start` de una persona."""
    cur.execute("select zona_horaria from workspace where id = %s", (workspace_id,))
    fila = cur.fetchone()
    if not fila:
        raise LookupError(f"El espacio {workspace_id} no existe.")
    return ZoneInfo(fila["zona_horaria"])


def fecha_local(momento: datetime, zona: ZoneInfo) -> date:
    return momento.astimezone(zona).date()


def reclamar_saludo(cur: psycopg.Cursor, *, workspace_id: str,
                    membership_id: str, fecha: date) -> bool:
    """Reclama, de forma atómica, el derecho a saludar a esta persona en esta
    fecha local. Devuelve `True` sólo para quien gana la reserva -- la
    primera vez que se llama para esta persona y esta fecha, sea en este
    turno o en cualquier otro anterior (incluida la bienvenida de
    incorporación, que reclama esta misma reserva -- T28,
    `onboarding.bienvenida` cuenta como el saludo del día, pack 06 §3).

    Un `upsert` con `on conflict ... where` alcanza sin ningún bloqueo
    explícito: dos turnos concurrentes para la misma persona compiten por la
    fila real de `greeting_state`, PostgreSQL serializa el segundo detrás del
    primero, y sólo gana el que de verdad avanza `ultima_fecha_local` -- el
    mismo problema y la misma forma que ya resuelve
    `pendientes.reclamar_modificacion_abierta` para "una sola de dos
    concurrentes gana". `>` en vez de `is distinct from`: un mensaje
    reintentado con una fecha ANTERIOR a la ya guardada (un reintento tardío
    cruzando medianoche, por ejemplo) nunca hace retroceder el estado ni
    reclama un saludo que ya salió."""
    if not membership_id:
        return False
    cur.execute(
        """insert into greeting_state (membership_id, workspace_id, ultima_fecha_local)
           values (%(mid)s, %(ws)s, %(fecha)s)
           on conflict (membership_id) do update
             set ultima_fecha_local = excluded.ultima_fecha_local
           where excluded.ultima_fecha_local > greeting_state.ultima_fecha_local
           returning true""",
        {"mid": membership_id, "ws": workspace_id, "fecha": fecha})
    return cur.fetchone() is not None


def saludo_pendiente_ws(cur: psycopg.Cursor, *, workspace_id: str | None,
                        membership_id: str | None, ahora: datetime) -> str | None:
    """Como `saludo_pendiente`, con `workspace_id`/`membership_id` sueltos en
    vez de un `Solicitante` -- para un punto de salida que sólo tiene la fila
    de la base a mano (`ingreso_tareas._enqueue`), no un `Solicitante`
    armado."""
    if not membership_id or not workspace_id:
        return None
    zona = zona_de_workspace(cur, workspace_id)
    saludo = saludo_por_hora(ahora.astimezone(zona).hour)
    ganado = reclamar_saludo(
        cur, workspace_id=workspace_id, membership_id=membership_id,
        fecha=fecha_local(ahora, zona))
    return saludo if ganado else None


def saludo_pendiente(cur: psycopg.Cursor, quien: Solicitante,
                     ahora: datetime) -> str | None:
    """El saludo de este turno para `quien`, o `None` si ya lo recibió en su
    fecha local vigente (`workspace.zona_horaria`) -- por este turno o por
    cualquier otro anterior del mismo día, incluida la bienvenida."""
    return saludo_pendiente_ws(
        cur, workspace_id=quien.workspace_id, membership_id=quien.membership_id,
        ahora=ahora)


def anteponer_si_corresponde(cur: psycopg.Cursor, quien: Solicitante,
                             ahora: datetime, texto: str) -> str:
    """Antepone el saludo del turno a `texto`, si corresponde. La forma que
    usan los puntos de salida de `agente.py`/`gateway.py`: ninguno de ellos
    decide si corresponde saludar, sólo envuelven el texto que ya iban a
    mandar -- la decisión y la reserva atómica quedan enteras acá."""
    saludo = saludo_pendiente(cur, quien, ahora)
    return f"{saludo}\n\n{texto}" if saludo else texto


def anteponer_si_corresponde_ws(cur: psycopg.Cursor, *, workspace_id: str | None,
                                membership_id: str | None, ahora: datetime,
                                texto: str) -> str:
    """Como `anteponer_si_corresponde`, con `workspace_id`/`membership_id`
    sueltos -- ver `saludo_pendiente_ws`."""
    saludo = saludo_pendiente_ws(
        cur, workspace_id=workspace_id, membership_id=membership_id, ahora=ahora)
    return f"{saludo}\n\n{texto}" if saludo else texto


def reclamar_para_bienvenida(cur: psycopg.Cursor, *, workspace_id: str,
                             membership_id: str, ahora: datetime) -> None:
    """La bienvenida de incorporación cuenta como el saludo de esa fecha
    (pack 06 §3: "La bienvenida de incorporación cuenta como saludo de esa
    fecha"; T28). Se llama al encolar la bienvenida (`gateway._activacion`),
    nunca antepone nada -- la bienvenida ya tiene su propio saludo fijo
    (`onboarding.bienvenida`, "Listo, <nombre>...") -- sólo reclama la
    reserva para que el resto del mismo día no vuelva a saludar. Sin
    `membership_id` (una activación que no pudo resolverlo) no reclama nada:
    mejor un saludo de más en un caso ya anómalo que reventar la
    bienvenida."""
    if not membership_id:
        return
    zona = zona_de_workspace(cur, workspace_id)
    reclamar_saludo(cur, workspace_id=workspace_id, membership_id=membership_id,
                    fecha=fecha_local(ahora, zona))
