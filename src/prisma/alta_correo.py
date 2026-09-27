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


def habilitado(cur: psycopg.Cursor) -> bool:
    """Si la clave del espacio para pedir y verificar correo está encendida.

    Ausencia de fila = apagada: es la configuración por defecto del
    producto, y `main` no la enciende nunca.
    """
    cur.execute("select valor from workspace_setting where clave = %s",
                (CLAVE_HABILITADO,))
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


def estado(cur: psycopg.Cursor, membership_id: str) -> dict | None:
    """La proyección vigente de una membresía, o `None` si nunca se abrió un ciclo."""
    cur.execute(
        """select membership_id, workspace_id, ciclo, modo, estado,
                  review_required, review_required_causa, review_required_desde,
                  bienvenida_entregada_en, actualizado_en
             from alta_correo_estado where membership_id = %s""",
        (membership_id,))
    return cur.fetchone()


def iniciar_ciclo(cur: psycopg.Cursor, membership_id: str, modo: str,
                   *, ahora: datetime | None = None) -> None:
    """Abre un ciclo nuevo: el primero de la membresía, o el siguiente tras un `revoked`.

    La base decide si corresponde (el disparador rechaza abrir un ciclo
    nuevo si el anterior no llegó a `revoked`); acá sólo se calcula el
    número de ciclo y el estado de arranque según el modo.
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


def crear_aviso(cur: psycopg.Cursor, tipo: str, texto_saneado: str,
                 *, workspace_id: str | None = None,
                 referencia_tipo: str | None = None,
                 referencia_id: str | None = None,
                 ahora: datetime | None = None) -> str:
    """Crea un aviso administrativo.

    Dentro de `espacio()` el disparador `derivar_espacio_registro` fija el
    espacio desde la sesión y descarta lo que se pase acá -- igual que
    `audit_log` e `incident`. `workspace_id` sólo hace falta bajo una
    conexión de administración, donde no hay ningún espacio en la sesión.
    """
    cur.execute(
        """insert into aviso_administrativo
             (workspace_id, tipo, texto_saneado, referencia_tipo, referencia_id,
              creado_en)
           values (%s, %s, %s, %s, %s, %s)
           returning id""",
        (workspace_id, tipo, texto_saneado, referencia_tipo, referencia_id,
         _ahora(ahora)))
    return str(cur.fetchone()["id"])


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
