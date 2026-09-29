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
from .salida import BUTTON_TEXT_LIMIT, TELEGRAM_TEXT_LIMIT, telegram_utf16_units

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


def verificar_migraciones(cur: psycopg.Cursor) -> str | None:
    """El nombre de la migración que falta aplicar para que el saludo diario
    no rompa `despachar`/`enqueue_outbox`, o `None` si ya está todo (R4-003,
    revisión 2026-09-28+3): sin `greeting_state` (migración 0018) o sin
    `message_outbox.es_bienvenida` (migración 0019), CUALQUIER despacho o
    encolado de un mensaje personal levanta `UndefinedTable`/
    `UndefinedColumn` y deja de mandarse todo -- no es un caso que la
    protección de `reclamar_y_anteponer` pueda absorber (esa es para que el
    SALUDO decorativo no tire abajo un envío que por lo demás anda bien; acá
    directamente falta una columna que el `insert` de cualquier mensaje
    necesita). Se llama una sola vez, al arrancar `escuchar`/`servir`
    (`cli.py`) -- nunca en cada `despachar`: no hay fallback en tiempo de
    ejecución para una columna faltante, el proceso no arranca."""
    cur.execute("select to_regclass('prisma.greeting_state') is not null as ok")
    if not cur.fetchone()["ok"]:
        return "0018_saludo_diario.sql"
    cur.execute(
        """select exists (
             select 1 from information_schema.columns
              where table_schema = 'prisma' and table_name = 'message_outbox'
                and column_name = 'es_bienvenida') as ok""")
    if not cur.fetchone()["ok"]:
        return "0019_marca_de_bienvenida.sql"
    # Lo mismo con `message_outbox.bloque_copiable` (migración 0020, T9-R1c-3):
    # el `insert` de `enqueue_outbox` y el `select` del despachador la nombran.
    cur.execute(
        """select exists (
             select 1 from information_schema.columns
              where table_schema = 'prisma' and table_name = 'message_outbox'
                and column_name = 'bloque_copiable') as ok""")
    if not cur.fetchone()["ok"]:
        return "0020_bloque_copiable.sql"
    # Y con `message_outbox.entrante_id` (migración 0021, T9-R2): el control de una
    # respuesta por mensaje la consulta, y el valor por omisión de la columna lee
    # la configuración que deja el gateway en cada mensaje.
    cur.execute(
        """select exists (
             select 1 from information_schema.columns
              where table_schema = 'prisma' and table_name = 'message_outbox'
                and column_name = 'entrante_id') as ok""")
    if not cur.fetchone()["ok"]:
        return "0021_respuesta_atada_al_mensaje.sql"
    return None


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
# Falla protegida (R4-001/R4-002, revisión 2026-09-28+1; R4-002/R3-001,
# revisión 2026-09-28+3): un saludo es decorativo y nunca puede tirar abajo
# un envío real -- ni porque `greeting_state` todavía no exista (el listener
# arrancó antes de aplicar la migración 0018), ni por una `zona_horaria`
# inválida, ni por cualquier otra falla del upsert.
#
# `reclamar_y_anteponer` NUNCA escribe el incidente ella misma: sólo lo
# hacía antes, y como corre dentro del mismo SAVEPOINT (mark-then-send) que
# `despachador._intentar_envio` abre para marcar 'enviado' y llamar a
# Telegram, un envío que fallara DESPUÉS revertía ese SAVEPOINT entero --
# con el incidente adentro -- mientras que la marca "ya reportado" en el
# `set` de memoria NO se revierte (no es parte de la transacción), así que
# la falla real nunca se volvía a reportar. Ahora `reclamar_y_anteponer`
# sólo devuelve la excepción (si la hay); el LLAMADOR la reporta recién
# después de que el envío se resuelva -- éxito o fallo --, en el mismo nivel
# donde `despachador._fallo` ya escribe sin este problema.
#
# `reportar_falla` marca en el `set` recién DESPUÉS de escribir el incidente
# con éxito (mismo patrón de fondo que `ciclo.SupresorDeRepetidos`/
# `reportar_fallo`, sin importarlo de `ciclo.py` para no crear un ciclo de
# imports -- `ciclo -> despachador -> saludo -> ciclo`).
# ---------------------------------------------------------------------------

_FALLAS_SALUDO_REPORTADAS: set[tuple[str | None, str]] = set()


def reportar_falla(cur: psycopg.Cursor, workspace_id: str,
                   error: Exception) -> None:
    """Reporta una falla que devolvió `reclamar_y_anteponer`, deduplicado
    por `(workspace_id, tipo de error)`. Llamarla recién DESPUÉS de que el
    envío del mensaje se resolvió (éxito o fallo) -- nunca todavía dentro
    del SAVEPOINT que lo intenta, o un envío fallido se la lleva puesta."""
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
                        membership_id: str, zona: ZoneInfo, ahora: datetime,
                        texto: str, has_buttons: bool,
                        chequear_ajuste: bool
                        ) -> tuple[str | None, Exception | None]:
    """El saludo que corresponde, o `None`, y la excepción, si algo falló --
    nunca la reporta, eso lo hace el llamador después de resolver el envío
    (ver el comentario de arriba). Todo en un SAVEPOINT propio: si algo
    falla, se revierte SOLO este punto -- el resto de la transacción de
    despacho (la marca 'enviado' que ya corrió antes) sigue intacta.

    `chequear_ajuste` (R3-003, revisión 2026-09-28+3): si anteponer el
    saludo empujaría `texto` fuera del límite real de Telegram -- una fila
    ya encolada sin el margen reservado (`salida.MARGEN_SALUDO`), por
    ejemplo -- ni siquiera intenta reclamar la reserva: el mensaje tiene que
    salir igual, sin saludo, y sin haber gastado la reserva del día por un
    mensaje que en definitiva no la llevó. Se chequea ANTES del `upsert`
    (nunca hace falta deshacerlo). No aplica a la bienvenida
    (`chequear_ajuste=False`): nunca antepone nada, así que ningún ajuste de
    texto puede hacerla superar el límite."""
    punto = cur.connection.transaction(force_rollback=False)
    try:
        with punto:
            saludo = saludo_por_hora(ahora.astimezone(zona).hour)
            if chequear_ajuste:
                limite = BUTTON_TEXT_LIMIT if has_buttons else TELEGRAM_TEXT_LIMIT
                if telegram_utf16_units(f"{saludo}\n\n{texto}") > limite:
                    return None, None
            ganado = reclamar_saludo(
                cur, workspace_id=workspace_id, membership_id=membership_id,
                fecha=fecha_local(ahora, zona))
            return (saludo if ganado else None), None
    except Exception as exc:  # noqa: BLE001 -- decorativo, nunca tira el envío
        return None, exc


def reclamar_y_anteponer(cur: psycopg.Cursor, *, workspace_id: str,
                         membership_id: str | None, zona: ZoneInfo,
                         ahora: datetime, texto: str,
                         has_buttons: bool = False,
                         es_bienvenida: bool = False
                         ) -> tuple[str, Exception | None]:
    """Lo que llama `despachador._intentar_envio`, dentro de su propio
    SAVEPOINT (mark-then-send): decide si corresponde el saludo para
    `membership_id` en la fecha local de `ahora` (zona del espacio) y lo
    antepone a `texto` -- o lo reclama sin anteponer nada, si `es_bienvenida`
    (pack 06 §3, T28: la bienvenida ya es su propio saludo).

    Devuelve `(texto_final, falla)`: `falla` es la excepción que hubo, si la
    hubo -- el LLAMADOR es quien decide cuándo reportarla (`reportar_falla`,
    recién después de que el envío se resuelva; ver el comentario de más
    arriba), nunca esta función.

    `membership_id=None` -- un mensaje de grupo -- nunca reclama ni antepone
    nada (decisión del usuario, 2026-09-28+2: los mensajes de grupo ni llevan
    ni consumen el saludo personal)."""
    if not membership_id:
        return texto, None
    saludo, falla = _reclamar_protegido(
        cur, workspace_id=workspace_id, membership_id=membership_id,
        zona=zona, ahora=ahora, texto=texto, has_buttons=has_buttons,
        chequear_ajuste=not es_bienvenida)
    if es_bienvenida or not saludo:
        return texto, falla
    return f"{saludo}\n\n{texto}", falla
