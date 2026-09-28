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
de forma determinística.

Decisión del usuario, 2026-09-28+2 (revisión de e83a280, T7b/T7b-follow-up):
**el primer mensaje que Prisma le manda a una persona en su fecha local lleva
el saludo, sea cual sea** -- una respuesta, una cadencia (el objetivo del
lunes 09:15), un recordatorio de la escalera, o un aviso que disparó otra
persona (una entrega para el aprobador, por ejemplo). Nunca se repite ese
día, ni siquiera si la persona contesta.

Por eso la decisión y la reserva NO viven en `agente.py`/`gateway.py`
(versión anterior de este módulo, hasta e83a280): esos puntos arman la
respuesta mucho antes de saber si de verdad va a ser lo primero que la
persona reciba hoy -- una cadencia encolada más tarde, o un mensaje pospuesto
por horario, podían terminar entregándose antes. El único lugar que sabe qué
sale primero DE VERDAD es `despachador._intentar_envio`, en el momento del
envío: `reclamar_y_anteponer` vive acá para que `despachador.py` la llame ahí
mismo, dentro del mismo punto de retorno (SAVEPOINT) que ya marca 'enviado'
antes de llamar a Telegram -- si el envío falla, ese SAVEPOINT entero se
revierte y con él la reserva del saludo, para que el reintento pueda volver a
reclamarlo (nunca se quema el saludo del día en un mensaje que no llegó).

Un mensaje de grupo (`destinatario_membership_id` nulo: `resumen_grupal`,
`informe_semanal`, la presentación del espacio) nunca reclama ni lleva el
saludo -- es la posición por omisión del usuario; puede cambiar más adelante,
pero hoy es así en todos los casos.

La bienvenida de incorporación (`onboarding.bienvenida`, encolada con
`message_outbox.es_bienvenida = true`) cuenta como el saludo de esa fecha
(pack 06 §3, T28): el despachador reclama la reserva por ella sin anteponerle
nada -- ese texto ya es su propio saludo fijo ("Listo, <nombre>...").

Reserva atómica: la fila es `greeting_state` (`membership_id` primary key,
`workspace_id`, `ultima_fecha_local`), y `reclamar_saludo` hace un `upsert`
con `on conflict ... where` -- dos despachos concurrentes de la misma persona
compiten por la fila real, PostgreSQL serializa el segundo detrás del
primero, y sólo gana el que de verdad avanza `ultima_fecha_local`.
"""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

import psycopg

from .incidentes import registrar_incidente
from .salida import telegram_utf16_units

SALUDO_MANANA = "👋 Buen día"
SALUDO_TARDE = "👋 Buenas tardes"
SALUDO_NOCHE = "👋 Buenas noches"


def saludo_por_hora(hora_local: int) -> str:
    """El saludo exacto de pack 06 §2 por hora local (0-23): 05:00-11:59
    Buen día, 12:00-19:59 Buenas tardes, el resto (20:00-04:59, cruzando
    medianoche) Buenas noches."""
    if 5 <= hora_local < 12:
        return SALUDO_MANANA
    if 12 <= hora_local < 20:
        return SALUDO_TARDE
    return SALUDO_NOCHE


def zona_de_workspace(cur: psycopg.Cursor, workspace_id: str) -> ZoneInfo:
    """La zona horaria del espacio, sin depender de que exista
    `work_calendar` (a diferencia de `calendario.Calendario.desde_base`).
    `despachador._intentar_envio` no la usa -- ya tiene `cal.zona`, validada
    de antes -- pero queda disponible para cualquier otro punto que necesite
    la zona sin construir un `Calendario` completo."""
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
    primera vez que se llama para esta persona y esta fecha, sea por la
    bienvenida o por cualquier mensaje despachado antes.

    Un `upsert` con `on conflict ... where` alcanza sin ningún bloqueo
    explícito: dos despachos concurrentes de la misma persona compiten por
    la fila real de `greeting_state`, PostgreSQL serializa el segundo detrás
    del primero, y sólo gana el que de verdad avanza `ultima_fecha_local` --
    el mismo problema y la misma forma que ya resuelve
    `pendientes.reclamar_modificacion_abierta` para "una sola de dos
    concurrentes gana". `>` en vez de `is distinct from`: un reintento con
    una fecha ANTERIOR a la ya guardada (cruzando medianoche, por ejemplo)
    nunca hace retroceder el estado ni reclama un saludo que ya salió."""
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


# Cuánto le hace falta a un saludo, con su separador, en el peor caso -- para
# que `salida.enqueue_outbox` le reserve ese margen a CUALQUIER mensaje
# dirigido a una persona (revisión 2026-09-28+2): el texto ya se guarda
# partido/recortado al encolar, mucho antes de saber si el despachador le va
# a anteponer el saludo, así que el margen tiene que reservarse siempre, no
# sólo cuando se sabe que va a hacer falta. Calculado, no copiado a mano: si
# el texto de un saludo cambia, el margen se ajusta solo. `salida.py` importa
# esto adentro de `enqueue_outbox`, nunca al nivel del módulo -- si lo hiciera
# arriba, `salida.py` y este módulo se importarían en ciclo (este módulo ya
# importa `telegram_utf16_units` de `salida.py` arriba).
MARGEN_SALUDO = (
    max(telegram_utf16_units(s) for s in (SALUDO_MANANA, SALUDO_TARDE, SALUDO_NOCHE))
    + telegram_utf16_units("\n\n"))


# ---------------------------------------------------------------------------
# Falla protegida (R4-001/R4-002, revisión 2026-09-28+1): un saludo es
# decorativo y nunca puede tirar abajo un envío real -- ni porque
# `greeting_state` todavía no exista (el listener arrancó antes de aplicar la
# migración 0019), ni por una `zona_horaria` inválida, ni por cualquier otra
# falla del upsert. Mismo patrón de fondo que `ciclo.SupresorDeRepetidos`/
# `reportar_fallo` (marcar recién DESPUÉS de escribir el incidente, para que
# un incidente que no se pudo registrar se reintente la próxima vez) -- sin
# importarlo de `ciclo.py` para no crear un ciclo de imports
# (`ciclo -> despachador -> saludo -> ciclo`).
# ---------------------------------------------------------------------------

_FALLAS_SALUDO_REPORTADAS: set[tuple[str | None, str]] = set()


def _reportar_falla_saludo(cur: psycopg.Cursor, workspace_id: str,
                           error: Exception) -> None:
    clave = (workspace_id, type(error).__name__)
    if clave in _FALLAS_SALUDO_REPORTADAS:
        return
    try:
        registrar_incidente(
            cur, workspace_id,
            "El saludo diario falló al despachar un mensaje; salió sin saludo.",
            referencia_cruda=str(error)[:2000], etapa="saludo_diario")
    except Exception as exc:  # noqa: BLE001 -- ni esto puede tirar el envío
        print(f"  ! no se pudo registrar el incidente del saludo diario "
             f"({type(exc).__name__}): {type(error).__name__}")
        return
    _FALLAS_SALUDO_REPORTADAS.add(clave)


def _reclamar_protegido(cur: psycopg.Cursor, *, workspace_id: str,
                        membership_id: str, zona: ZoneInfo,
                        ahora: datetime) -> str | None:
    """El saludo que corresponde, o `None`, en su propio SAVEPOINT: si algo
    falla (tabla faltante, zona inválida, lo que sea), se revierte SOLO este
    punto -- el resto de la transacción de despacho (la marca 'enviado' que
    ya corrió antes) sigue intacta -- se reporta una vez, deduplicado, y se
    devuelve `None` para que el mensaje salga sin saludo."""
    punto = cur.connection.transaction(force_rollback=False)
    try:
        with punto:
            saludo = saludo_por_hora(ahora.astimezone(zona).hour)
            ganado = reclamar_saludo(
                cur, workspace_id=workspace_id, membership_id=membership_id,
                fecha=fecha_local(ahora, zona))
            return saludo if ganado else None
    except Exception as exc:  # noqa: BLE001 -- decorativo, nunca tira el envío
        _reportar_falla_saludo(cur, workspace_id, exc)
        return None


def reclamar_y_anteponer(cur: psycopg.Cursor, *, workspace_id: str,
                         membership_id: str | None, zona: ZoneInfo,
                         ahora: datetime, texto: str,
                         es_bienvenida: bool = False) -> str:
    """Lo que llama `despachador._intentar_envio`, dentro de su propio
    SAVEPOINT (mark-then-send): decide si corresponde el saludo para
    `membership_id` en la fecha local de `ahora` (zona del espacio) y lo
    antepone a `texto` -- o lo reclama sin anteponer nada, si `es_bienvenida`
    (pack 06 §3, T28: la bienvenida ya es su propio saludo).

    `membership_id=None` -- un mensaje de grupo -- nunca reclama ni antepone
    nada (decisión del usuario, 2026-09-28+2: los mensajes de grupo ni llevan
    ni consumen el saludo personal)."""
    if not membership_id:
        return texto
    saludo = _reclamar_protegido(
        cur, workspace_id=workspace_id, membership_id=membership_id,
        zona=zona, ahora=ahora)
    if es_bienvenida or not saludo:
        return texto
    return f"{saludo}\n\n{texto}"
