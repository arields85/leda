"""Alta con correo verificado (rama auxiliar/alta-y-google, G1a).

Capa angosta de acceso a lo que vive en `db/esquema.sql`: el ciclo de alta
con correo (`alta_correo_evento` / `alta_correo_estado`), el token de
verificación (`alta_correo_verificacion`, patrón `acceso_tablero`), el
contacto verificado (`alta_correo_contacto`) y los avisos administrativos
(`aviso_administrativo`).

Este módulo no manda mensajes ni conoce Telegram -- eso es G1b/G1c/G1d. Sólo
envuelve las funciones y tablas de la base para que quien las use no tenga
que repetir el hash del token ni la normalización del correo en cada lugar.

Con `correo_verificacion.habilitado` apagada en `workspace_setting` (el
valor por defecto), nada de este módulo se usa: `onboarding.activar` sigue
igual que hoy.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone

import psycopg

CLAVE_HABILITADO = "correo_verificacion.habilitado"

ESTADOS_VALIDOS = (
    "pending_welcome", "awaiting_email", "pending_email_verification",
    "active", "revoked",
)
MODOS_VALIDOS = ("alta", "existente")


def _ahora(valor: datetime | None) -> datetime:
    return valor or datetime.now(timezone.utc)


def normalizar_correo(email: str) -> str:
    """Único lugar donde se normaliza un correo: espacios extremos y minúsculas.

    Cualquier otra función de este módulo asume que el correo que recibe ya
    pasó por acá.
    """
    return email.strip().lower()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def habilitado(cur: psycopg.Cursor, workspace_id: str) -> bool:
    """Si la clave del espacio para pedir y verificar correo está encendida.

    Ausencia de fila = apagada: es la configuración por defecto del
    producto, y `main` no la enciende nunca.

    El espacio se filtra explícitamente, no sólo por la RLS de la sesión: una
    conexión de administración (`admin()`) ve todos los espacios, y sin este
    filtro leería la clave de cualquiera, no la del que llama (G1a2, hallazgo
    de la revisión).
    """
    cur.execute(
        "select valor from workspace_setting where workspace_id = %s and clave = %s",
        (workspace_id, CLAVE_HABILITADO))
    fila = cur.fetchone()
    if not fila:
        return False
    valor = fila["valor"]
    if isinstance(valor, str):
        valor = json.loads(valor)
    return bool(valor)


# ---------------------------------------------------------------------------
# Ciclo de alta: alta_correo_evento / alta_correo_estado
# ---------------------------------------------------------------------------


def estado(cur: psycopg.Cursor, membership_id: str, *,
           bloquear: bool = False) -> dict | None:
    """La proyección vigente de una membresía, o `None` si nunca se abrió un ciclo.

    `bloquear=True` toma el candado de la fila con
    `bloquear_alta_correo_estado()` (G1d, seguimiento de la revisión de
    G1b2): quien necesita decidir con esta lectura si todavía hace falta
    escribir algo -- `_completar_bienvenida`, por ejemplo -- tiene que
    tomar el candado ANTES de decidir, no después. Sin esto, dos mensajes
    simultáneos pueden leer los dos el mismo estado de arranque (ninguno
    escribió nada todavía) y los dos deciden escribir: la fila ya está
    protegida más abajo (`preparar_evento_alta_correo()` toma su propio
    `for update` antes de aplicar cualquier evento), así que nunca corrompe
    nada, pero el segundo revienta contra un índice único o una transición
    inválida en vez de simplemente ver la proyección ya avanzada y no
    hacer nada."""
    if bloquear:
        cur.execute("select bloquear_alta_correo_estado(%s)", (membership_id,))
    cur.execute(
        """select membership_id, workspace_id, ciclo, modo, estado,
                  review_required, review_required_causa, review_required_desde,
                  bienvenida_entregada_en, actualizado_en
             from alta_correo_estado where membership_id = %s""",
        (membership_id,))
    return cur.fetchone()


def iniciar_ciclo(cur: psycopg.Cursor, membership_id: str, modo: str,
                   *, ahora: datetime | None = None) -> int:
    """Abre un ciclo nuevo: el primero de la membresía, o el siguiente tras un `revoked`.

    La base decide si corresponde (el disparador rechaza abrir un ciclo
    nuevo si el anterior no llegó a `revoked`); acá sólo se calcula el
    número de ciclo y el estado de arranque según el modo. Devuelve el
    número de ciclo abierto -- quien llama lo necesita, por ejemplo, para
    que una clave de dedupe por ciclo (G1c2, ítem 1) nunca reutilice la de
    un ciclo anterior.
    """
    if modo not in MODOS_VALIDOS:
        raise ValueError(f"modo inválido: {modo!r}")
    previo = estado(cur, membership_id)
    ciclo = (previo["ciclo"] + 1) if previo else 1
    estado_nuevo = "pending_welcome" if modo == "alta" else "awaiting_email"
    cur.execute(
        """insert into alta_correo_evento
             (membership_id, ciclo, tipo, modo, estado_anterior, estado_nuevo,
              actor_kind, at)
           values (%s, %s, 'transicion', %s, null, %s, 'sistema', %s)""",
        (membership_id, ciclo, modo, estado_nuevo, _ahora(ahora)))
    return ciclo


def transicionar(cur: psycopg.Cursor, membership_id: str, estado_nuevo: str,
                  *, actor_kind: str = "sistema", actor_app_user_id: str | None = None,
                  ahora: datetime | None = None) -> None:
    """Inserta la transición siguiente del ciclo vigente.

    Lee la proyección para completar `estado_anterior`, `ciclo` y `modo`: el
    disparador de la base vuelve a validar todo esto, esto sólo evita que
    quien llama tenga que repetir la lectura.
    """
    actual = estado(cur, membership_id)
    if actual is None:
        raise ValueError(
            f"alta_correo: no hay ciclo abierto para la membresía {membership_id}")
    cur.execute(
        """insert into alta_correo_evento
             (membership_id, ciclo, tipo, modo, estado_anterior, estado_nuevo,
              actor_kind, actor_app_user_id, at)
           values (%s, %s, 'transicion', %s, %s, %s, %s, %s, %s)""",
        (membership_id, actual["ciclo"], actual["modo"], actual["estado"],
         estado_nuevo, actor_kind, actor_app_user_id, _ahora(ahora)))


def marcar_revision(cur: psycopg.Cursor, membership_id: str, causa: str,
                     *, ahora: datetime | None = None) -> None:
    actual = estado(cur, membership_id)
    if actual is None:
        raise ValueError(
            f"alta_correo: no hay ciclo abierto para la membresía {membership_id}")
    cur.execute(
        """insert into alta_correo_evento
             (membership_id, ciclo, tipo, causa, actor_kind, at)
           values (%s, %s, 'marca_revision', %s, 'sistema', %s)""",
        (membership_id, actual["ciclo"], causa, _ahora(ahora)))


def resolver_revision(cur: psycopg.Cursor, membership_id: str,
                       *, actor_app_user_id: str | None = None,
                       ahora: datetime | None = None) -> None:
    actual = estado(cur, membership_id)
    if actual is None:
        raise ValueError(
            f"alta_correo: no hay ciclo abierto para la membresía {membership_id}")
    cur.execute(
        """insert into alta_correo_evento
             (membership_id, ciclo, tipo, actor_kind, actor_app_user_id, at)
           values (%s, %s, 'resuelta_revision', 'persona', %s, %s)""",
        (membership_id, actual["ciclo"], actor_app_user_id, _ahora(ahora)))


def bienvenida_entregada(cur: psycopg.Cursor, membership_id: str,
                          *, ahora: datetime | None = None) -> None:
    actual = estado(cur, membership_id)
    if actual is None:
        raise ValueError(
            f"alta_correo: no hay ciclo abierto para la membresía {membership_id}")
    cur.execute(
        """insert into alta_correo_evento
             (membership_id, ciclo, tipo, actor_kind, at)
           values (%s, %s, 'bienvenida_entregada', 'sistema', %s)""",
        (membership_id, actual["ciclo"], _ahora(ahora)))


# ---------------------------------------------------------------------------
# Token de verificación
# ---------------------------------------------------------------------------


@dataclass
class ResultadoVerificacion:
    ok: bool
    motivo: str | None


def emitir_verificacion(cur: psycopg.Cursor, membership_id: str, email: str,
                         token: str, *, proveedor_referencia: str | None = None,
                         ahora: datetime | None = None) -> ResultadoVerificacion:
    """Emite (o reenvía) un correo de verificación. Devuelve el resultado tipado.

    El valor en claro de `token` no se guarda: sólo viaja hacia quien lo va a
    mandar. La base sólo recibe su hash.
    """
    cur.execute(
        "select ok, motivo, id from emitir_verificacion_correo(%s, %s, %s, %s, %s)",
        (membership_id, normalizar_correo(email), hash_token(token),
         proveedor_referencia, _ahora(ahora)))
    fila = cur.fetchone()
    return ResultadoVerificacion(ok=fila["ok"], motivo=fila["motivo"])


@dataclass
class ResultadoReserva:
    ok: bool
    motivo: str | None
    workspace_id: str | None = None
    ciclo: int | None = None
    email: str | None = None


def reservar_verificacion(cur: psycopg.Cursor, token: str, membership_id: str,
                           *, ahora: datetime | None = None) -> ResultadoReserva:
    """Reserva el token por 5 minutos para esta membresía, o devuelve por qué no."""
    cur.execute(
        "select ok, motivo, workspace_id, ciclo, email "
        "from reservar_verificacion_correo(%s, %s, %s)",
        (hash_token(token), membership_id, _ahora(ahora)))
    fila = cur.fetchone()
    return ResultadoReserva(
        ok=fila["ok"], motivo=fila["motivo"],
        workspace_id=str(fila["workspace_id"]) if fila["workspace_id"] else None,
        ciclo=fila["ciclo"], email=fila["email"])


def completar_verificacion(cur: psycopg.Cursor, token: str, membership_id: str,
                            *, ahora: datetime | None = None) -> ResultadoVerificacion:
    """Escribe el contacto verificado y la transición a `active`, atómico.

    Sólo tiene efecto si el token sigue reservado por esta misma membresía
    (ver `reservar_verificacion`). Un fallo devuelve un motivo tipado y deja
    la reserva liberada para reintentar, nunca a mitad de camino.
    """
    cur.execute(
        "select ok, motivo from completar_verificacion_correo(%s, %s, %s)",
        (hash_token(token), membership_id, _ahora(ahora)))
    fila = cur.fetchone()
    return ResultadoVerificacion(ok=fila["ok"], motivo=fila["motivo"])


def verificacion_vigente(cur: psycopg.Cursor, membership_id: str) -> dict | None:
    """El envío de verificación en pie (email + vencimiento), o `None`.

    Nunca expone el hash del token: sólo lo que el flujo conversacional
    (G1b) necesita para comparar un correo recién tipeado contra el que ya
    se pidió verificar (`verificacion_vigente_correo`, security definer:
    `prisma_app` no tiene ningún privilegio directo sobre
    `alta_correo_verificacion`).
    """
    cur.execute("select email, expira_en from verificacion_vigente_correo(%s)",
                (membership_id,))
    return cur.fetchone()


def dominios_permitidos(cur: psycopg.Cursor, workspace_id: str) -> list[str] | None:
    """Lista de dominios habilitados para el correo laboral, o `None` si el
    espacio no restringió ninguno (`workspace_setting`, clave
    `correo_verificacion.dominios`, lista JSON de dominios en minúsculas)."""
    cur.execute(
        "select valor from workspace_setting where workspace_id = %s and clave = %s",
        (workspace_id, "correo_verificacion.dominios"))
    fila = cur.fetchone()
    if not fila:
        return None
    valor = fila["valor"]
    if isinstance(valor, str):
        valor = json.loads(valor)
    if not valor:
        return None
    return [str(d).strip().lower() for d in valor]


def elegibles_existente(cur: psycopg.Cursor, workspace_id: str) -> list[dict]:
    """Integrantes activos de `workspace_id`, con Telegram vinculado, sin
    correo verificado y sin ningún ciclo de alta con correo abierto todavía
    (o con uno ya `revoked`) -- a quien `correo-verificacion --activar`
    (`cli.py`, G1c) tiene que poner en modo `existente`.

    Filtra explícitamente por `workspace_id`, no sólo por RLS (G1c2, ítem
    4): bajo una conexión de administración (`admin()`, `bypassrls`), sin
    este filtro esta consulta podría devolver integrantes de cualquier
    espacio si la sesión quedara apuntando al equivocado -- mismo motivo
    que ya exige `habilitado()` (G1a2).
    """
    cur.execute(
        """select i.membership_id, i.nombre, i.telegram_user_id
             from integrante i
             left join alta_correo_contacto c
               on c.membership_id = i.membership_id and c.workspace_id = i.workspace_id
             left join alta_correo_estado e
               on e.membership_id = i.membership_id and e.workspace_id = i.workspace_id
            where i.workspace_id = %s
              and i.activo and i.telegram_user_id is not null
              and c.membership_id is null
              and (e.membership_id is null or e.estado = 'revoked')
            order by i.nombre""",
        (workspace_id,))
    return cur.fetchall()


def contacto_verificado(cur: psycopg.Cursor, membership_id: str) -> dict | None:
    """El correo verificado de una membresía y desde cuándo, o `None`."""
    cur.execute(
        """select email, verificado_en, actualizado_en
             from alta_correo_contacto where membership_id = %s""",
        (membership_id,))
    return cur.fetchone()


# ---------------------------------------------------------------------------
# Avisos administrativos -- "🛠️ Administración"
# ---------------------------------------------------------------------------


# Cuántas vueltas de "insertar o nada, si no está leer" tolera `crear_aviso`
# antes de rendirse (G1d-a3, ítem 5): dos alcanza en la práctica para
# cualquier carrera real (perder la carrera de inserción y no encontrar
# tampoco la fila del otro sólo pasa si alguien la resolvió justo en esa
# ventana angosta); una tercera vuelta es margen barato para una carrera
# encima de otra carrera, sin convertir esto en un reintento indefinido.
_MAX_INTENTOS_CREAR_AVISO = 3


def crear_aviso(cur: psycopg.Cursor, tipo: str, texto_saneado: str,
                 *, workspace_id: str | None = None,
                 referencia_tipo: str | None = None,
                 referencia_id: str | None = None,
                 ahora: datetime | None = None) -> str:
    """Crea un aviso administrativo -- o, si ya había uno igual y sin
    resolver, devuelve el id de ese (G1d, ítem 4: insertar o nada,
    garantizado por `aviso_administrativo_pendiente_unico` incluso bajo dos
    disparadores concurrentes del mismo aviso, no por el orden en que
    Python los ejecute).

    Dentro de `espacio()` el disparador `derivar_espacio_registro` fija el
    espacio desde la sesión y descarta lo que se pase acá -- igual que
    `audit_log` e `incident`. `workspace_id` sólo hace falta bajo una
    conexión de administración, donde no hay ningún espacio en la sesión.

    Sin referencia (`referencia_tipo`/`referencia_id` en `None`), el índice
    nunca colisiona -- Postgres trata cada `null` como distinto -- así que
    ese caso siempre inserta una fila nueva, como antes.

    El índice incluye `workspace_id` (G1d-a2, ítem 5): el mismo (tipo,
    referencia) en dos espacios distintos son dos avisos independientes,
    nunca uno pisando al otro.

    Nunca devuelve `None` ni revienta con `TypeError` (G1d-a2, ítem 5,
    hallazgo de la revisión): entre el "insertar o nada" que pierde la
    carrera y la lectura de abajo hay una ventana angosta en la que quien
    ganó la carrera puede haber marcado su aviso resuelto -- ahí ya no
    queda ningún pendiente vivo contra el que haber chocado, así que el
    próximo intento de este mismo bucle vuelve a insertar sin tropezar en
    vez de leer una fila que ya no está.

    Puede levantar `RuntimeError` (G1d-a3, ítem 5: antes esto no estaba
    dicho acá) si agota `_MAX_INTENTOS_CREAR_AVISO` intentos sin poder
    insertar ni encontrar ningún aviso pendiente -- una carrera inusualmente
    persistente, no un caso que quien llama deba esperar en el camino
    normal; nunca devuelve `None` en su lugar ni finge éxito."""
    ahora = _ahora(ahora)
    for _ in range(_MAX_INTENTOS_CREAR_AVISO):
        cur.execute(
            """insert into aviso_administrativo
                 (workspace_id, tipo, texto_saneado, referencia_tipo, referencia_id,
                  creado_en)
               values (%s, %s, %s, %s, %s, %s)
               on conflict (workspace_id, tipo, referencia_tipo, referencia_id)
                 where resuelto_en is null
               do nothing
               returning id""",
            (workspace_id, tipo, texto_saneado, referencia_tipo, referencia_id,
             ahora))
        fila = cur.fetchone()
        if fila is not None:
            return str(fila["id"])

        # Carrera perdida (o alguien se adelantó): ya hay uno pendiente
        # igual. `workspace_id` sólo filtra cuando quien llama lo dio
        # explícito (conexión de administración); dentro de `espacio()` la
        # RLS ya acota esto al espacio de la sesión.
        cur.execute(
            """select id from aviso_administrativo
                where (%s::uuid is null or workspace_id = %s)
                  and tipo = %s and referencia_tipo is not distinct from %s
                  and referencia_id is not distinct from %s and resuelto_en is null
                order by creado_en desc limit 1""",
            (workspace_id, workspace_id, tipo, referencia_tipo, referencia_id))
        fila = cur.fetchone()
        if fila is not None:
            return str(fila["id"])

    raise RuntimeError(
        "crear_aviso: no se pudo crear ni encontrar un aviso pendiente tras "
        "varios intentos (carrera inusual).")


def aviso_pendiente(cur: psycopg.Cursor, tipo: str, referencia_tipo: str,
                     referencia_id: str) -> bool:
    """`True` si ya hay un aviso de este tipo, sobre esta misma referencia,
    todavía sin resolver (G1b2, ítem 5: evita crear un segundo aviso
    idéntico mientras administración no marcó el anterior resuelto --
    "leído ≠ resuelto")."""
    cur.execute(
        """select 1 from aviso_administrativo
            where tipo = %s and referencia_tipo = %s and referencia_id = %s
              and resuelto_en is null
            limit 1""",
        (tipo, referencia_tipo, referencia_id))
    return cur.fetchone() is not None


def avisos(cur: psycopg.Cursor, *, solo_no_leidos: bool = False,
           solo_no_resueltos: bool = False) -> list[dict]:
    condiciones = []
    if solo_no_leidos:
        condiciones.append("leido_en is null")
    if solo_no_resueltos:
        condiciones.append("resuelto_en is null")
    where = f"where {' and '.join(condiciones)}" if condiciones else ""
    cur.execute(
        f"""select id, workspace_id, tipo, texto_saneado, referencia_tipo,
                   referencia_id, creado_en, leido_en, leido_por, resuelto_en,
                   resuelto_por
              from aviso_administrativo {where}
             order by creado_en""")
    return cur.fetchall()


def marcar_leido(cur: psycopg.Cursor, aviso_id: str, app_user_id: str,
                  *, ahora: datetime | None = None) -> None:
    cur.execute(
        """update aviso_administrativo
              set leido_en = %s, leido_por = %s
            where id = %s and leido_en is null""",
        (_ahora(ahora), app_user_id, aviso_id))


def marcar_resuelto(cur: psycopg.Cursor, aviso_id: str, app_user_id: str,
                     *, ahora: datetime | None = None) -> None:
    cur.execute(
        """update aviso_administrativo
              set resuelto_en = %s, resuelto_por = %s
            where id = %s and resuelto_en is null""",
        (_ahora(ahora), app_user_id, aviso_id))
