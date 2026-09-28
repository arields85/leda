"""Recorrido conversacional del alta con correo (rama auxiliar, G1b).

`alta_correo.py` (G1a/G1a2) es la capa angosta sobre la base: abre y avanza
el ciclo, emite/reserva/completa el token, guarda el contacto verificado.
Ese módulo dice explícitamente que no manda mensajes ni conoce Telegram --
eso es este módulo: los textos del pack, el puerto de envío de correo, y el
control (`gate`) que se antepone al despacho conversacional de negocio
mientras una membresía en modo `alta` no llegó a `active`.

Con `correo_verificacion.habilitado` apagada en el espacio (el valor por
defecto), `gate()` siempre devuelve `False` de inmediato y nada de lo demás
se ejecuta: la activación por Telegram queda igual que hoy.

Ninguna función de acá hace `conn.commit()`/`conn.rollback()`: corren bajo el
cursor que ya abrió quien llama (`gateway.py`), con la misma disciplina de
transacción que el resto del gateway.
"""

from __future__ import annotations

import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Protocol
from zoneinfo import ZoneInfo

import psycopg

from . import alta_correo as AC
from .salida import enqueue_outbox

# ---------------------------------------------------------------------------
# Textos literales -- `01-INCORPORACION-E-IDENTIDAD.md` §5 y el anexo
# `incorporacion-receive_email.py.txt`. Reproducidos tal cual: no son una
# paráfrasis.
# ---------------------------------------------------------------------------

TEXTO_PEDIDO_CORREO = (
    "Para completar tu perfil de trabajo, ¿podrías pasarme un correo "
    "laboral, por favor? Lo voy a usar únicamente para enviarte "
    "invitaciones, incluirte en calendarios, compartir archivos y "
    "gestionar comunicaciones internas. Después te voy a enviar un "
    "mensaje breve para verificar que sea correcto.")

TEXTO_GRACIAS_ENVIADO = (
    "Gracias. Te envié un mensaje de verificación a ese correo. "
    "Por favor, abrilo y pulsá «Verificar correo». Si no lo encontrás "
    "en la bandeja principal, revisá también la carpeta de spam. Apenas "
    "quede confirmado, vas a poder conversar conmigo normalmente.")

TEXTO_NO_RECONOCIDO = (
    "No pude reconocer un único correo laboral en ese mensaje. "
    "¿Podrías revisarlo y enviármelo nuevamente, por favor?")

TEXTO_DOMINIO_NO_HABILITADO = (
    "Ese correo no pertenece a un dominio laboral habilitado. "
    "¿Podrías revisar la dirección y enviarme otra, por favor?")

TEXTO_DIRECCION_INCOMPLETA = (
    "La dirección parece incompleta. ¿Podrías revisarla y "
    "enviármela nuevamente, por favor?")

TEXTO_CORREO_EN_USO = (
    "Ese correo ya está asociado a otro perfil. Por favor, "
    "revisalo o enviame otra dirección laboral.")

ASUNTO_VERIFICACION = "Confirmá tu correo laboral en Prisma"


def _nombre_preferido(nombre: str) -> str:
    """Primera palabra de `nombre`.

    Nunca cadena vacía: un nombre vacío o de sólo espacios es un ERROR DE
    DATOS (D, "Textos del alta con correo aprobados por el usuario",
    2026-09-28) -- el nombre lo carga la administración al definir el
    equipo y es obligatorio (`nucleo/alta-de-equipo.md`, Bloque 2). Levanta
    `ValueError` a propósito: los handlers que llaman a esto (`abrir_ciclo_
    alta`, `_completar_bienvenida`, `resolver_verificacion_correo`, `gate`,
    `resolver_toque`) corren dentro de la red de contención de
    `gateway.procesar_update`/`_activacion`, que atrapa cualquier excepción
    no prevista y deja un incidente + el aviso neutral -- nunca fallar en
    silencio. Antes (G1b2) esto devolvía "" y tres textos ofrecían una
    variante "sin nombre"; el usuario las quitó explícitamente: la base
    acepta hoy `nombre = ''` (hallazgo para `main`, ver el documento de la
    rama), pero mientras eso no se corrija en origen, acá se trata como la
    falla que es, no como un caso normal a acomodar en el texto."""
    nombre = (nombre or "").strip()
    if not nombre:
        raise ValueError("alta_correo: el nombre de la persona está vacío")
    return nombre.split()[0]


def texto_bienvenida(saludo: str, nombre_preferido: str) -> str:
    return (f"{saludo}, {nombre_preferido}. Soy Prisma, la coordinadora "
            "digital del equipo. Mi función es ayudarlos a mantener claros "
            "los objetivos, organizar tareas, registrar avances y detectar "
            "bloqueos con anticipación. Voy a procurar que el seguimiento "
            "sea útil, breve y agradable.")


def texto_verificado(nombre_preferido: str) -> str:
    return (f"✅ Gracias, {nombre_preferido}. Tu correo quedó verificado y "
            "el registro está completo. Ya podés conversar conmigo "
            "normalmente.")


def texto_verificado_existente(nombre_preferido: str) -> str:
    """C (textos aprobados por el usuario, 2026-09-28): verificación en modo
    `existente` (G1c). El texto del pack ("ya podés conversar conmigo
    normalmente") está pensado para quien recién se está dando de alta -- a
    quien ya estaba trabajando normalmente le suena como si algo la hubiera
    estado bloqueando, cuando C5 exige exactamente lo contrario (nunca
    bloqueada)."""
    return f"✅ Gracias, {nombre_preferido}. Tu correo quedó verificado."


def cuerpo_verificacion(nombre_preferido: str, enlace: str) -> str:
    """Cuerpo del correo de verificación (A, textos aprobados por el
    usuario, 2026-09-28).

    El pack (§5) da el asunto, la etiqueta del botón y describe el
    contenido (vence en 24 horas, un solo uso, misma cuenta de Telegram);
    no da el párrafo literal. Deliberadamente NO ofrece "responder este
    correo" como alternativa: ADR 0010 excluye la verificación por
    respuesta de correo como mecanismo (C7/`01` §7).
    """
    return (
        f"Hola, {nombre_preferido}.\n\n"
        "Para terminar tu alta en Prisma necesito que confirmes que este "
        "es tu correo laboral.\n\n"
        f"Verificar correo: {enlace}\n\n"
        "Este enlace vence en 24 horas, sirve una sola vez y tiene que "
        "abrirse con la misma cuenta de Telegram que usás para hablar con "
        "Prisma.")


# ---------------------------------------------------------------------------
# Textos del alta con correo aprobados por el usuario (2026-09-28) -- letras
# B1-B12, C. Regla general: ningún mensaje termina en "escribime y lo vemos"
# ni deja a la persona sin salida; cada problema trae el paso siguiente
# listo. Cuando se habla del correo, se muestra la dirección.
# ---------------------------------------------------------------------------

ETIQUETA_REENVIAR = "Reenviarlo"
ETIQUETA_CAMBIAR = "Usar otro correo"
ETIQUETA_REENVIAR_ULTIMO = "Reenviar el último"


def texto_recordatorio_pendiente(correo: str) -> str:
    """B2. Otra cosa sin verificar, mientras hay un envío en pie."""
    return f"Te mandé el correo de verificación a {correo}. ¿No te llegó?"


def texto_propone_cambio(nuevo: str, anterior: str) -> str:
    """B3. Otra dirección con verificación pendiente."""
    return f"¿Uso {nuevo} en lugar de {anterior}?"


def etiqueta_usar_nuevo(nuevo: str) -> str:
    return f"Sí, usar {nuevo}"


def etiqueta_dejar_anterior(anterior: str) -> str:
    return f"No, dejar {anterior}"


# B4. Mantiene la anterior.
TEXTO_MANTENER_CONFIRMADO = "Perfecto, seguimos con el correo anterior."


def texto_enlace_vencido_reenviado(correo: str) -> str:
    """B5. Enlace vencido -- Prisma manda uno nuevo sola, respetando los
    límites (sin envíos disponibles: B11 o B12, que se resuelven aparte)."""
    return f"Ese enlace venció, así que te mandé uno nuevo a {correo}."


# B6. Enlace real abierto desde una cuenta de Telegram que no es la de su
# dueño (integrante o no): nunca se consume. Un enlace inexistente de una
# cuenta desconocida no recibe respuesta (como hoy, ver
# `resolver_verificacion_correo`).
TEXTO_CUENTA_INCORRECTA = (
    "Este enlace tiene que abrirse con la cuenta de Telegram que usás con "
    "Prisma.")


def texto_enlace_roto_reenviado(correo: str) -> str:
    """B6. Enlace roto (no existe) de un integrante con verificación
    pendiente: Prisma manda uno nuevo sola."""
    return f"Ese enlace no funciona, así que te mandé uno nuevo a {correo}."


# B7. Enlace ya usado y correo ya verificado.
TEXTO_YA_VERIFICADO = "Tu correo ya está verificado ✅"
# B7b. Enlace viejo reemplazado por uno más nuevo (no consumido, ya no
# vigente): botón "Reenviar el último".
TEXTO_ENLACE_REEMPLAZADO = "Ese enlace ya no sirve porque te mandé uno más nuevo."

# B8. Doble clic sobre la misma verificación.
TEXTO_VERIFICACION_OCUPADA = (
    "Ya estoy procesando esa verificación. Esperá un momento y revisá si "
    "te llegó la confirmación.")

# B10. Reenviar sin nada pendiente.
TEXTO_SIN_ENVIO_VIGENTE = "Todavía no tengo tu correo. Pasámelo y te envío la verificación."


def texto_limite_hora(hhmm: str) -> str:
    """B11. Límite por hora -- {hhmm} es cuándo el envío más viejo de la
    última hora deja de contar (`alta_correo.proximo_reenvio`), en la hora
    local del espacio."""
    return (f"Se enviaron varios correos de verificación en la última "
            f"hora. Por seguridad, sólo puedo reenviarte otro a partir de "
            f"las {hhmm}.")


# B12. Cinco envíos agotados -- ya cierto: el aviso se entrega (G1d-a) y
# existe la acción de administración para habilitar un nuevo intento
# (G1d-b, acción F).
TEXTO_LIMITE_AGOTADO = (
    "Se agotaron los envíos de verificación. Ya le avisé a administración "
    "y te escribo apenas lo destrabe.")


def texto_reintento_habilitado(correo: str) -> str:
    """F. Tras "Habilitar un nuevo intento" (acción de la administración),
    a la persona le llega esto sola."""
    return f"¿Te mando la verificación a {correo} otra vez?"


def etiqueta_si_a(correo: str) -> str:
    return f"Sí, a {correo}"


# Textos nuevos, sin equivalente literal en el pack ni en la lista aprobada
# por el usuario -- casos residuales que esa lista no cubre explícitamente
# (B9 sin texto fijo).
TEXTO_MULTIPLES_CORREOS = (
    "Encontré más de un correo en ese mensaje. ¿Cuál de estos es el que "
    "querés usar?")

# G1d-b2, ítem 5 (corrección tras la revisión de G1d-b): `TEXTO_ESTADO_
# CAMBIO` ("...escribime y lo vemos...") y `TEXTO_ENLACE_INVALIDO`
# ("...pedime que te lo reenvíe...") se retiraron -- los dos eran
# callejones sin salida (la regla general aprobada exige que cada problema
# traiga el paso siguiente listo). Cualquier camino que antes caía en uno
# de los dos ahora responde según el estado VIGENTE del ciclo (B9), por
# `_responder_estado_actual` -- ver su docstring.

_TEXTOS_MOTIVO_EMISION = {
    "email_in_use": TEXTO_CORREO_EN_USO,
    "verification_send_limit": TEXTO_LIMITE_AGOTADO,
}

# `verification_token_consumed` NO vive acá (ítem 2): un enlace ya usado
# puede venir de un ciclo anterior al vigente, así que necesita mirar el
# estado ACTUAL antes de responder -- ver la rama dedicada en
# `_responder_falla_verificacion`.
_TEXTOS_VERIFICACION_FALLIDA = {
    "verification_token_busy": TEXTO_VERIFICACION_OCUPADA,
    "email_in_use": TEXTO_CORREO_EN_USO,
}

# ---------------------------------------------------------------------------
# Puerto de envío -- el adaptador real (Gmail) llega en G2 (C4). Acá sólo el
# contrato y "no hay emisor configurado todavía", nunca una simulación.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Recibo:
    message_id: str
    thread_id: str


class EnvioCorreo(Protocol):
    def enviar_verificacion(self, *, destinatario: str, asunto: str, cuerpo: str,
                            nombre_preferido: str, enlace: str,
                            vence_en: datetime) -> Recibo: ...


def obtener_emisor_configurado(cur: psycopg.Cursor,
                               workspace_id: str) -> EnvioCorreo | None:
    """El emisor de correo configurado para el espacio.

    Siempre `None` hoy: el adaptador real de Gmail es G2 (C4, aprobado por
    el usuario). Con `correo_verificacion.habilitado` encendida y sin
    emisor, nada de este módulo simula un envío -- registra un incidente,
    deja a la persona con el aviso neutral y crea un aviso administrativo
    ("Ninguna protección se degrada en silencio").
    """
    return None


class _RefusalTipada(Exception):
    def __init__(self, motivo: str):
        super().__init__(motivo)
        self.motivo = motivo


# ---------------------------------------------------------------------------
# Extracción y validación de correos
# ---------------------------------------------------------------------------

_EMAIL_LAXO = re.compile(r"[^\s<>()\[\]{}\"']+@[^\s<>()\[\]{}\"']+")
_DOMINIO_VALIDO = re.compile(
    r"^[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(\.[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?)+$")
_PUNTUACION_FINAL = ".,;:!?)]}\"'"


def extraer_correos(texto: str) -> list[str]:
    """Candidatos a correo en un mensaje libre, sin duplicados (por valor
    normalizado). Cero, uno o varios -- quien llama decide qué hacer con
    cada caso; esta función no valida formato de dominio, sólo separa."""
    vistos: set[str] = set()
    candidatos: list[str] = []
    for crudo in _EMAIL_LAXO.findall(texto or ""):
        candidato = crudo.rstrip(_PUNTUACION_FINAL)
        if "@" not in candidato:
            continue
        normalizado = AC.normalizar_correo(candidato)
        if normalizado in vistos:
            continue
        vistos.add(normalizado)
        candidatos.append(candidato)
    return candidatos


def _formato_valido(email: str) -> bool:
    local, separador, dominio = email.partition("@")
    if not local or separador != "@" or not dominio:
        return False
    return bool(_DOMINIO_VALIDO.match(dominio))


def _zona_horaria(cur: psycopg.Cursor, workspace_id: str) -> ZoneInfo:
    cur.execute("select zona_horaria from workspace where id = %s", (workspace_id,))
    fila = cur.fetchone()
    if fila and fila.get("zona_horaria"):
        return ZoneInfo(fila["zona_horaria"])
    return ZoneInfo("UTC")


def saludo_para(ahora: datetime, zona: ZoneInfo) -> str:
    """👋 + Buen día / Buenas tardes / Buenas noches, según la hora local del
    espacio (anexo `incorporacion-greeting_for.py.txt`: 5-12, 12-20, resto)."""
    local = ahora.astimezone(zona)
    if 5 <= local.hour < 12:
        base = "Buen día"
    elif 12 <= local.hour < 20:
        base = "Buenas tardes"
    else:
        base = "Buenas noches"
    return f"👋 {base}"


# ---------------------------------------------------------------------------
# Apertura del ciclo (llamada desde `gateway._activacion`)
# ---------------------------------------------------------------------------


def abrir_ciclo_alta(cur: psycopg.Cursor, membership_id: str, workspace_id: str,
                     chat_id: int, nombre: str, ahora: datetime, *,
                     app_user_id: str | None = None) -> None:
    """Activación con la clave encendida: abre `pending_welcome` y completa
    los pasos hasta `awaiting_email`, en la misma transacción que
    `onboarding.activar()` ya viene usando.

    El candado (`bloquear=True`, G1d-a2, ítem 6) se toma ACÁ, antes de
    `AC.iniciar_ciclo`, cuando la proyección todavía no existe para nadie --
    es un advisory lock, no un candado de fila, así que sirve incluso antes
    de que la fila exista. Sin esto, dos activaciones simultáneas de la
    MISMA membresía (dos entregas del mismo enlace, un reintento de
    Telegram) pueden las dos ver que no hay ningún ciclo abierto y las dos
    intentar abrir el primero: la segunda, al desbloquearse, ya encuentra el
    ciclo que abrió y avanzó la primera -- por eso sólo llama a
    `iniciar_ciclo` si todavía no hay ninguna proyección. `_completar_
    bienvenida` ya es idempotente por su cuenta (vuelve a tomar el mismo
    candado y no hace nada si el ciclo ya pasó de `pending_welcome`), así
    que la segunda llamada termina siendo un no-op completo, nunca una
    excepción cruda ni un `UniqueViolation` contra el índice único de
    `bienvenida_entregada`.

    G1d-a3, ítem 1 (regresión corregida): abre el ciclo también cuando la
    proyección existente ya está `revoked` -- no sólo cuando no hay ninguna
    proyección todavía. Antes esto sólo miraba `actual is None`, así que una
    reactivación administrativa tras una revocación (la membresía vuelve a
    activarse, con una proyección de un ciclo anterior ya cerrado) nunca
    abría el ciclo siguiente: `_completar_bienvenida` no encontraba ningún
    `pending_welcome` que completar y el mensaje se perdía en silencio. La
    base es quien decide si corresponde (`preparar_evento_alta_correo()`
    exige `actual.estado = 'revoked'` para aceptar un ciclo `ciclo + 1`) --
    acá sólo se repite esa misma condición para decidir si hay que llamar a
    `iniciar_ciclo`, nunca una regla nueva. La protección contra la carrera
    de la primera activación no cambia: la segunda llamada concurrente, ya
    desbloqueada, encuentra la proyección que dejó la primera (`pending_
    welcome` de un ciclo que no es `revoked`) y no vuelve a abrir nada.

    G1d-c2, ítem 5: si la proyección ya está en `pending_email_verification`
    o `active` -- p. ej. una reactivación administrativa que revincula la
    cuenta de Telegram de alguien que ya venía verificando o ya había
    verificado, sin haber pasado por `revoked` --, esto nunca puede quedar en
    silencio: `_completar_bienvenida` no escribe nada para esos estados (sólo
    actúa sobre `pending_welcome`), así que antes la persona no recibía
    ningún mensaje. Ahora sigue el mismo enrutador por estado (B9,
    `_responder_estado_actual`) que ya usa el resto del recorrido -- nunca
    `onboarding.bienvenida` (la vieja, con tareas abiertas), que C6 excluye
    mientras la clave está encendida, y que además no tiene sentido para
    alguien a mitad de verificar: `pending_email_verification` retoma el
    recordatorio o "todavía no tengo tu correo", y `active` confirma con el
    texto ya verificado (`texto_verificado`/`texto_verificado_existente`).

    `awaiting_email` queda deliberadamente FUERA de este enrutador nuevo, a
    diferencia de los otros dos: es el estado en el que `_completar_
    bienvenida` deja el ciclo al completar la bienvenida, así que dos
    llamadas concurrentes de ESTA MISMA función sobre la primera activación
    (el candado de arriba) legítimamente dejan a la segunda viendo
    `awaiting_email` recién escrito por la primera -- silencioso a propósito
    (`test_dos_abrir_ciclo_alta_concurrentes_de_una_primera_activacion_no_
    revientan`): sólo dos mensajes, nunca un tercero "pedido de correo"
    duplicado por la carrera. Ninguna reactivación real (una persona ya
    verificando, no una carrera del mismo evento) queda entonces en
    silencio: para llegar hasta acá alguien tuvo que escribir un correo
    primero, lo que sólo pasa en un turno posterior, nunca dentro de la
    misma carrera de apertura."""
    actual = AC.estado(cur, membership_id, bloquear=True)
    if actual is None or actual["estado"] == "revoked":
        AC.iniciar_ciclo(cur, membership_id, "alta", ahora=ahora)
        _completar_bienvenida(cur, membership_id, workspace_id, chat_id, nombre, ahora)
        return
    if actual["estado"] in ("pending_welcome", "awaiting_email"):
        _completar_bienvenida(cur, membership_id, workspace_id, chat_id, nombre, ahora)
        return

    from .autoridad import Canal, Solicitante

    if app_user_id is None:
        cur.execute("select app_user_id from membership where id = %s", (membership_id,))
        fila = cur.fetchone()
        app_user_id = str(fila["app_user_id"]) if fila else None
    quien = Solicitante(app_user_id=app_user_id, canal=Canal.ESPACIO,
                        workspace_id=workspace_id, membership_id=membership_id,
                        nombre=nombre)
    _responder_estado_actual(cur, quien, workspace_id, chat_id, ahora)


def abrir_ciclo_existente(cur: psycopg.Cursor, membership_id: str, workspace_id: str,
                          chat_id: int, ahora: datetime) -> None:
    """Encender la clave (comando `correo-verificacion --activar` de
    `cli.py`, G1c) para quien ya estaba activo sin correo: abre el ciclo
    directamente en `awaiting_email` -- C5, sin bienvenida, que ya recibió
    cuando activó por enlace -- y encola el mismo pedido de correo del pack,
    con su propia clave de dedupe (nunca la de `abrir_ciclo_alta`, para que
    nunca puedan pisarse).

    No hay ningún guardia de idempotencia acá adentro: lo pone quien llama
    (`cli.py`), que sólo invoca esto para membresías sin ningún ciclo
    abierto todavía -- una segunda corrida del comando ya no las vuelve a
    encontrar elegibles.

    La clave de dedupe incluye el ciclo (G1c2, ítem 1): sin él, un ciclo
    `existente` revocado antes de verificar (nunca crea
    `alta_correo_contacto`, así que la elegibilidad vuelve a contar a esa
    membresía) reabre el ciclo siguiente en la próxima corrida, pero el
    pedido nuevo se deduplicaría en silencio contra la clave del ciclo
    anterior (`enqueue_outbox` hace `on conflict (dedupe_key) do nothing`)
    y nunca saldría -- una falla silenciosa que ninguna excepción
    delataría."""
    ciclo = AC.iniciar_ciclo(cur, membership_id, "existente", ahora=ahora)
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id, text=TEXTO_PEDIDO_CORREO,
        message_type="informativo", scheduled_for=ahora,
        dedupe_key=f"{workspace_id}:alta-correo:pedido-existente:{membership_id}:{ciclo}",
        is_response=True, allow_split=True)


def _completar_bienvenida(cur: psycopg.Cursor, membership_id: str, workspace_id: str,
                          chat_id: int, nombre: str, ahora: datetime) -> None:
    """Bienvenida + pedido de correo (dos entregas, claves de dedupe propias)
    y paso a `awaiting_email`. Idempotente: si algo dejó el ciclo a mitad en
    `pending_welcome` (un reinicio, una llamada concurrente que se
    adelantó), repetir esto no hace nada -- ni el outbox ni el evento de
    bienvenida entregada se duplican, y no revienta contra el índice único
    de `alta_correo_evento` (G1b2, ítem 5, hallazgo de la revisión: antes
    del guardia de abajo, una segunda llamada sobre un ciclo ya avanzado
    reventaba con `UniqueViolation` o con la transición inválida sobre el
    disparador de la base).

    G1d, seguimiento de la revisión de G1b2: la lectura toma el candado de
    fila (`bloquear=True`) antes de decidir -- si dos mensajes simultáneos
    llegan hasta acá, el segundo espera a que el primero termine y confirme,
    y entonces ve la proyección ya en `awaiting_email` (no `pending_welcome`)
    y devuelve sin escribir nada, en vez de reventar contra el índice único
    de `bienvenida_entregada` o la transición inválida.

    G1d-a3, ítem 1: las claves de dedupe de las dos entregas incluyen el
    ciclo, igual que ya hace `abrir_ciclo_existente` para su propio pedido
    (G1c2, ítem 1) -- `dedupe_key` es única en toda `message_outbox`
    (`db/esquema.sql`), no por membresía. Sin el ciclo, una reactivación tras
    `revoked` (ciclo 2) reusaría la MISMA clave que ya gastó la bienvenida o
    el pedido del ciclo 1, y `enqueue_outbox` la descartaría en silencio
    (`on conflict (dedupe_key) do nothing`) -- el evento `bienvenida_
    entregada` quedaría igual registrado, como si el mensaje hubiera salido,
    cuando en realidad nunca llegó a encolarse de nuevo."""
    actual = AC.estado(cur, membership_id, bloquear=True)
    if actual is not None and actual["estado"] != "pending_welcome":
        return
    ciclo = actual["ciclo"] if actual is not None else 1
    nombre_preferido = _nombre_preferido(nombre)
    zona = _zona_horaria(cur, workspace_id)
    saludo = saludo_para(ahora, zona)
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id,
        text=texto_bienvenida(saludo, nombre_preferido),
        message_type="informativo", scheduled_for=ahora,
        dedupe_key=f"{workspace_id}:alta-correo:bienvenida:{membership_id}:{ciclo}",
        is_response=True, allow_split=True)
    # Un microsegundo después, no al mismo instante: son dos llamadas
    # separadas a `enqueue_outbox` (no dos partes de un mismo mensaje
    # partido), así que sin este desplazamiento `programado_para` empataría
    # y el orden de entrega del despachador quedaría al azar -- el pedido de
    # correo podría llegar antes que la bienvenida.
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id, text=TEXTO_PEDIDO_CORREO,
        message_type="informativo", scheduled_for=ahora + timedelta(microseconds=1),
        dedupe_key=f"{workspace_id}:alta-correo:pedido:{membership_id}:{ciclo}",
        is_response=True, allow_split=True)
    AC.bienvenida_entregada(cur, membership_id, ahora=ahora)
    AC.transicionar(cur, membership_id, "awaiting_email", actor_kind="sistema",
                    ahora=ahora)


# ---------------------------------------------------------------------------
# El control (gate) -- antepuesto al despacho conversacional
# ---------------------------------------------------------------------------

# Estados abiertos que comparten los dos modos (G1c2, ítem 5: una sola
# fuente, en vez de repetir la tupla en `atender_existente`): mientras la
# proyección esté en uno de éstos, todavía no hay contacto verificado.
# `pending_welcome` sólo existe en modo `alta` -- `existente` arranca
# directo en `awaiting_email` (C5: a quien ya estaba activo no se le repite
# la bienvenida) y nunca lo atraviesa, así que no entra en el conjunto
# compartido.
_ESTADOS_ABIERTOS_COMUNES = ("awaiting_email", "pending_email_verification")
# Los tres estados por debajo de `active` en modo `alta` -- mientras la
# proyección esté en uno de éstos, ninguna herramienta de negocio puede
# correr para esta membresía, sea el chat que sea (G1b2, ítem 1).
_ESTADOS_BLOQUEANTES = ("pending_welcome",) + _ESTADOS_ABIERTOS_COMUNES


def _gateada(actual: dict | None) -> bool:
    return (actual is not None and actual["modo"] == "alta"
            and actual["estado"] in _ESTADOS_BLOQUEANTES)


def bloqueada_para_negocio(cur: psycopg.Cursor, membership_id: str,
                           workspace_id: str) -> bool:
    """`True` si esta membresía sigue en modo `alta` por debajo de `active`.

    La usan los chats que no son privados -- `gate()` sólo corre en privado
    (G1b2, ítem 1: antes corría para cualquier chat, y en un grupo llegaba a
    pedir/mostrar/procesar un correo, o dejaba pasar el mensaje a una
    herramienta de negocio para quien todavía no verificó el suyo). En un
    grupo no hay recorrido de correo que ofrecer: la respuesta correcta es
    no hacer nada -- ni responder ni rutear a ningún lado.

    G1c: la clave apagada corta esto también -- ver el docstring de `gate`,
    mismo motivo."""
    if not AC.habilitado(cur, workspace_id):
        return False
    return _gateada(AC.estado(cur, membership_id))


def gate(cur: psycopg.Cursor, quien: Any, texto: str, *, chat_id: int,
         workspace_id: str, ahora: datetime,
         bot_username_resolver: Callable[[], str]) -> bool:
    """`True` si el mensaje quedó atendido por el recorrido de alta con
    correo -- no hay que rutearlo a intake ni al agente. `False` si esta
    membresía no está en modo `alta` con un ciclo abierto por debajo de
    `active` (incluye la clave apagada, donde nunca hay ciclo). Sólo tiene
    sentido llamarla en un chat privado -- ver `bloqueada_para_negocio`
    para lo que corresponde en cualquier otro tipo de chat.

    G1c: la clave apagada corta el control de inmediato, incluso si quedó
    un ciclo `alta` abierto de cuando estaba encendida -- comando
    `correo-verificacion --desactivar` de `cli.py`: "con la clave apagada,
    NO corre ningún gate ni recorrido de correo para nadie". Antes esta
    función no comprobaba la clave, sólo el ciclo, así que alguien a mitad
    de verificar quedaba bloqueado para siempre aunque administración
    apagara la clave después."""
    if not AC.habilitado(cur, workspace_id):
        return False
    actual = AC.estado(cur, quien.membership_id)
    if not _gateada(actual):
        return False

    estado = actual["estado"]
    if estado == "pending_welcome":
        # Sólo alcanzable si algo dejó el ciclo a mitad -- ver
        # `_completar_bienvenida`. Se completa y se sigue con este mismo
        # mensaje como si ya estuviera en `awaiting_email`.
        _completar_bienvenida(cur, quien.membership_id, workspace_id, chat_id,
                              quien.nombre, ahora)
        estado = "awaiting_email"

    nombre_preferido = _nombre_preferido(quien.nombre)
    if estado == "awaiting_email":
        _atender_awaiting_email(cur, quien, texto, workspace_id, chat_id, ahora,
                                bot_username_resolver, nombre_preferido)
    else:
        _atender_pending_verification(cur, quien, texto, workspace_id, chat_id,
                                      ahora, bot_username_resolver, nombre_preferido)
    return True


# ---------------------------------------------------------------------------
# G1c -- modo `existente`: nunca bloquea (C5); sólo intercepta un mensaje que
# ES un correo, de punta a punta.
# ---------------------------------------------------------------------------

# Parte local estricta (G1c2, ítem 2; punto interno endurecido en G1d): a
# diferencia de `extraer_correos` (que sólo separa candidatos DENTRO de una
# frase libre, sin validar formato), esto tiene que decidir por sí solo si
# el mensaje ENTERO es "exactamente una dirección de correo" -- así que no
# puede aceptar nada que sirva para otra cosa.
#
# Deliberadamente sin "/" ni ":" en ningún átomo: eso es lo que hace que
# `http://usuario@host` (donde la parte local, antes del único `@`, queda
# siendo `http://usuario`) se rechace acá. `usuario@host:8080` y
# `usuario@host/ruta`, en cambio, tienen una parte local válida (`usuario`)
# -- ahí el `:` y el `/` caen del lado del dominio, y es `_DOMINIO_VALIDO`
# quien los rechaza, no esta regla.
#
# Un punto separa átomos, nunca puede ir al principio, al final, ni dos
# seguidos (RFC 5321; un correo real nunca los tiene) -- de ahí la forma
# "átomo(.átomo)*" en vez de aceptar cualquier `.` suelto en la clase de
# caracteres.
_ATOMO_LOCAL = r"[A-Za-z0-9!#$%&'*+=?^_`{|}~-]+"
_LOCAL_ESTRICTO = re.compile(rf"^{_ATOMO_LOCAL}(\.{_ATOMO_LOCAL})*$")


def _solo_un_correo(texto: str) -> str | None:
    """El texto recortado (sin espacios en los extremos) si es, de punta a
    punta, un único candidato a correo -- ni antes ni después hay otra
    palabra. `None` para cualquier otra cosa: vacío, varias palabras, un
    correo en medio de una frase.

    A diferencia de `extraer_correos` (que busca candidatos DENTRO de una
    frase libre, para el modo `alta` donde cada mensaje tiene que
    responderse de un modo u otro), esto es lo único que en modo `existente`
    distingue "la persona me está dando su correo" de un mensaje cualquiera
    que tiene que seguir su curso hacia intake/el agente.

    Regla única y estricta (G1c2, ítem 2, corrigiendo el regex laxo
    anterior, que aceptaba URLs con `@`, `usuario@host:ruta`, dos `@` y
    puntuación final): el mensaje entero tiene que ser una parte local
    (`_LOCAL_ESTRICTO`) seguida de exactamente un `@` y un dominio con
    puntos (`_DOMINIO_VALIDO`, el mismo que ya exige `_formato_valido` para
    el modo `alta`) -- ese dominio, por construcción, nunca termina en un
    separador (`.`, `,`, etc.), así que un solo punto o coma final ya
    alcanza para rechazar el mensaje entero: más seguro y consistente que
    aceptarlo y confiar en que quien lo tipeó no quiso decir otra cosa."""
    candidato = (texto or "").strip()
    if not candidato or any(c.isspace() for c in candidato):
        return None
    if candidato.count("@") != 1:
        return None
    # Sin chequeo de vacío aparte para `local`/`dominio`: los dos regex
    # exigen como mínimo un carácter (`+`), así que una parte vacía ya cae
    # por no matchear -- un chequeo previo sería redundante (seguimiento a
    # la revisión de G1c2).
    local, _, dominio = candidato.partition("@")
    if not _LOCAL_ESTRICTO.match(local) or not _DOMINIO_VALIDO.match(dominio):
        return None
    return candidato


def atender_existente(cur: psycopg.Cursor, quien: Any, texto: str, *, chat_id: int,
                      workspace_id: str, ahora: datetime,
                      bot_username_resolver: Callable[[], str]) -> bool:
    """`True` si el mensaje quedó atendido por el recorrido de correo en
    modo `existente` -- `False` para cualquier otro caso, que sigue como
    cualquier mensaje normal hacia intake/el agente (C5: a quien ya estaba
    activo Prisma le pide el correo una vez, SIN bloquearlo; "se les pide
    una vez" -- nunca un recordatorio ni una segunda pedida).

    A diferencia de `gate` (modo `alta`, bloqueante, que tiene que responder
    algo a CADA mensaje mientras esté gateada), esta función nunca contesta
    "no reconocí un correo" ni ofrece un recordatorio con botones: eso sería
    fastidiar a alguien que ya venía trabajando con normalidad. Sólo actúa
    cuando el mensaje, de punta a punta, es un correo (`_solo_un_correo`);
    cualquier otra cosa -- incluida la clave apagada, o cualquier estado que
    no sea modo `existente` por debajo de `active` -- devuelve `False` de
    inmediato sin tocar nada. Sólo tiene sentido llamarla en un chat privado
    (nunca se procesa un correo en un grupo); quien llama (`gateway.py`) ya
    lo garantiza, igual que con `gate`."""
    if not AC.habilitado(cur, workspace_id):
        return False
    actual = AC.estado(cur, quien.membership_id)
    if (actual is None or actual["modo"] != "existente"
            or actual["estado"] not in _ESTADOS_ABIERTOS_COMUNES):
        return False
    correo = _solo_un_correo(texto)
    if correo is None:
        return False

    nombre_preferido = _nombre_preferido(quien.nombre)
    if actual["estado"] == "awaiting_email":
        _validar_y_emitir(cur, quien, correo, workspace_id, chat_id, ahora,
                          bot_username_resolver, nombre_preferido)
        return True

    # `pending_email_verification`: mismo criterio de comparación que
    # `_atender_pending_verification`, pero sin caer nunca en
    # `_recordatorio` -- ver el docstring. Si el correo es exactamente el
    # que ya está vigente, no hay ninguna instrucción nueva que atender: se
    # deja pasar como cualquier mensaje (nunca un recordatorio).
    vigente = AC.verificacion_vigente(cur, quien.membership_id)
    if vigente is not None and AC.normalizar_correo(correo) == vigente["email"]:
        return False
    _proponer_cambio(cur, quien, correo, workspace_id, chat_id, ahora)
    return True


def _atender_awaiting_email(cur, quien, texto: str, workspace_id: str, chat_id: int,
                            ahora: datetime, bot_username_resolver, nombre_preferido: str
                            ) -> None:
    from .gateway import _responder

    correos = extraer_correos(texto)
    if not correos:
        _responder(cur, workspace_id, chat_id, quien, TEXTO_NO_RECONOCIDO, ahora)
        return
    if len(correos) > 1:
        _ofrecer_eleccion_correo(cur, quien, correos, workspace_id, chat_id, ahora)
        return
    _validar_y_emitir(cur, quien, correos[0], workspace_id, chat_id, ahora,
                      bot_username_resolver, nombre_preferido)


def _texto_rechazo_formato_o_dominio(cur, workspace_id: str, email: str) -> str | None:
    """Única validación de formato + dominios habilitados (G1d-c2, ítem 1):
    antes, "Cambiar correo a X" (`resolver_toque`, `SENTINEL_CAMBIO`) saltaba
    directo a `_emitir_y_enviar` sin pasar por acá, así que una dirección con
    un dominio no habilitado (o mal formada) podía colarse por ese botón
    aunque `_validar_y_emitir` la hubiera rechazado si hubiera llegado como
    texto libre. Ahora los dos únicos caminos que emiten una verificación por
    una dirección nueva -- un correo tipeado y "Cambiar correo a X" -- llaman
    a esta misma función antes de `_emitir_y_enviar`.

    Devuelve el texto de rechazo que corresponde, o `None` si el correo pasa
    las dos validaciones."""
    if not _formato_valido(email):
        return TEXTO_DIRECCION_INCOMPLETA
    permitidos = AC.dominios_permitidos(cur, workspace_id)
    dominio = email.rpartition("@")[2]
    if permitidos is not None and dominio not in permitidos:
        return TEXTO_DOMINIO_NO_HABILITADO
    return None


def _validar_y_emitir(cur, quien, correo_crudo: str, workspace_id: str, chat_id: int,
                      ahora: datetime, bot_username_resolver, nombre_preferido: str
                      ) -> None:
    from .gateway import _responder

    email = AC.normalizar_correo(correo_crudo)
    rechazo = _texto_rechazo_formato_o_dominio(cur, workspace_id, email)
    if rechazo is not None:
        _responder(cur, workspace_id, chat_id, quien, rechazo, ahora)
        return
    _emitir_y_enviar(cur, quien, email, workspace_id, chat_id, ahora,
                     bot_username_resolver, nombre_preferido, TEXTO_GRACIAS_ENVIADO)


def _emitir_y_enviar(cur, quien, email: str, workspace_id: str, chat_id: int,
                     ahora: datetime, bot_username_resolver, nombre_preferido: str,
                     texto_exito: str, *, transicion_previa: str | None = None) -> None:
    """Núcleo compartido por un correo nuevo válido, Reenviar y Cambiar
    correo: intenta un envío y responde según lo que haya pasado.

    Sin emisor configurado, nunca se llega a gastar un intento de envío
    (regla "no silent safety fallbacks"). Con emisor, todas las escrituras
    (la transición previa si la hay, el registro del envío con
    `AC.emitir_verificacion` y la transición hacia adelante) y el envío en
    sí viven en un solo savepoint (`cur.connection.transaction()`, mismo
    patrón que `gateway._iniciar_alta_guiada`): si cualquier parte falla, se
    revierte todo junto -- nunca queda el ciclo movido a mitad de camino
    (G1b2, ítem 2) -- y la transacción de afuera sigue en pie para dejar el
    incidente y el aviso neutral.

    `transicion_previa` es sólo para "Cambiar correo a X" desde
    `pending_email_verification`: hace que el ciclo pase primero por
    `awaiting_email` (mismo camino narrado que un correo nuevo), dentro del
    mismo savepoint que el resto -- nunca suelto antes, que es lo que
    dejaba el ciclo varado en `awaiting_email` si después algo rechazaba o
    fallaba (G1b2, ítem 2).

    Dentro del savepoint, el envío es lo ÚLTIMO que pasa (G1b2, ítem 4): si
    una escritura posterior fallara, ya no hay nada posterior que pueda
    fallar sin haber mandado el correo -- nunca un correo entregado con un
    enlace que la base terminó sin registrar.

    Límite conocido, documentado honestamente en vez de resuelto (G1d-c2,
    ítem 11): el envío ocurre DENTRO de la transacción de la petición, no
    después de su `commit`. El savepoint de arriba sólo aísla los pasos de
    ESTA función entre sí -- protege contra que el registro del envío quede
    sin el correo salido, o viceversa, DENTRO de esta llamada -- pero no
    protege contra que el `commit` externo (de quien llama, `gateway.
    procesar_update`) falle DESPUÉS de que el correo ya salió: en ese caso
    poco frecuente, el enlace que la persona recibió referencia un token que
    la base nunca terminó de confirmar. Esto no deja a la persona varada ni
    en silencio: abrir ese enlace más tarde no encuentra el token
    (`verification_token_invalid`, B6 -- "roto/inexistente"), y si el ciclo
    sigue en `pending_email_verification` Prisma le manda uno nuevo sola
    (`_reenviar_por_enlace_roto_o_vencido`) sin que tenga que pedirlo; y el
    fallo del `commit` en sí ya pasa por la misma red de contención de
    `gateway.procesar_update` (incidente + aviso neutral), nunca sin
    registrar. Mover el envío a DESPUÉS del `commit` evitaría este límite,
    pero exige una reconciliación propia -- encolar el envío como un hecho
    aparte, con su propio reintento e idempotencia, para no perderlo si el
    proceso cae entre el `commit` y el envío -- que esta unidad no construye;
    queda para cuando haga falta, no se inventa acá."""
    from .gateway import ETAPA_ALTA_CORREO, NOTICIA_NEUTRA_INCIDENTE, _responder
    from .incidentes import registrar_incidente

    sender = obtener_emisor_configurado(cur, workspace_id)
    if sender is None:
        # G1d-c2, ítem 2: "sin emisor configurado" es un problema del
        # ESPACIO, no de la persona que justo lo pisó -- antes la referencia
        # era `quien.membership_id`, así que cada integrante distinto que
        # tropezaba con esto abría su propio incidente y su propio aviso
        # (el índice único de `crear_aviso` sólo dedupea dentro de la MISMA
        # referencia). Ahora la referencia es el espacio: un solo aviso
        # pendiente por espacio, sin importar quién lo dispare, y mientras
        # siga sin resolver tampoco se registra un incidente nuevo por cada
        # intento (`registrar_incidente` no tiene ningún dedupe propio). La
        # persona sigue recibiendo el aviso neutral en cada intento -- nunca
        # silencio para ella, sólo se deja de repetir el ruido administrativo.
        if not AC.aviso_pendiente(cur, AC.TIPO_CORREO_SIN_EMISOR, "workspace", workspace_id):
            registrar_incidente(
                cur, workspace_id,
                "La verificación de correo está encendida pero no hay emisor "
                "de correo configurado.",
                severidad="alta", app_user_id=quien.app_user_id, chat_id=chat_id,
                etapa=ETAPA_ALTA_CORREO)
            AC.crear_aviso(
                cur, AC.TIPO_CORREO_SIN_EMISOR,
                "La verificación de correo está encendida pero no hay un emisor "
                "de correo configurado para el espacio.",
                workspace_id=workspace_id, referencia_tipo="workspace",
                referencia_id=workspace_id, ahora=ahora)
        _responder(cur, workspace_id, chat_id, quien, NOTICIA_NEUTRA_INCIDENTE, ahora)
        return

    token = secrets.token_urlsafe(24)
    try:
        with cur.connection.transaction():
            if transicion_previa is not None:
                AC.transicionar(cur, quien.membership_id, transicion_previa,
                                actor_kind="persona",
                                actor_app_user_id=quien.app_user_id, ahora=ahora)
            resultado = AC.emitir_verificacion(cur, quien.membership_id, email, token,
                                               ahora=ahora)
            if not resultado.ok:
                raise _RefusalTipada(resultado.motivo)
            # Sólo el primer envío de un correo (desde `awaiting_email`)
            # avanza el ciclo; un reenvío desde `pending_email_verification`
            # se queda en el mismo estado -- no hay transición
            # `pending_email_verification -> pending_email_verification` en
            # el grafo de la base (con motivo: nunca cambió de estado).
            actual = AC.estado(cur, quien.membership_id)
            if actual and actual["estado"] == "awaiting_email":
                AC.transicionar(cur, quien.membership_id, "pending_email_verification",
                                actor_kind="sistema", ahora=ahora)
            # El envío va al final a propósito -- ver el docstring (ítem 4).
            bot_username = bot_username_resolver()
            enlace = f"https://t.me/{bot_username}?start=pv_{token}"
            vence_en = ahora + timedelta(hours=24)
            sender.enviar_verificacion(
                destinatario=email, asunto=ASUNTO_VERIFICACION,
                cuerpo=cuerpo_verificacion(nombre_preferido, enlace),
                nombre_preferido=nombre_preferido, enlace=enlace, vence_en=vence_en)
    except _RefusalTipada as exc:
        if exc.motivo == "verification_rate_limited":
            # B11: {hhmm} es cuándo el envío más viejo de la última hora
            # deja de contar -- nunca un genérico "más tarde".
            proximo = AC.proximo_reenvio(cur, quien.membership_id, ahora=ahora)
            if proximo is None:
                # G1d-b2, ítem 4: nunca "??:??" -- `proximo_reenvio_correo`
                # usa exactamente el mismo borde que el límite de 3/hora de
                # `emitir_verificacion_correo` (`emitido_en > ahora - 1h`,
                # sin filtrar por ciclo), así que esto no debería pasar
                # mientras las dos sigan alineadas; sin ninguna garantía en
                # tiempo de compilación, un hueco en el texto es peor que un
                # aviso neutral -- se registra el incidente y se corta acá.
                registrar_incidente(
                    cur, workspace_id,
                    "No se pudo calcular la próxima hora de reenvío tras "
                    "el límite por hora de verificación de correo.",
                    severidad="media", app_user_id=quien.app_user_id, chat_id=chat_id,
                    etapa=ETAPA_ALTA_CORREO)
                _responder(cur, workspace_id, chat_id, quien, NOTICIA_NEUTRA_INCIDENTE, ahora)
                return
            zona = _zona_horaria(cur, workspace_id)
            hhmm = proximo.astimezone(zona).strftime("%H:%M")
            _responder(cur, workspace_id, chat_id, quien, texto_limite_hora(hhmm), ahora)
            return
        texto = _TEXTOS_MOTIVO_EMISION.get(exc.motivo)
        if texto is None:
            registrar_incidente(
                cur, workspace_id,
                f"La emisión de verificación se rechazó ({exc.motivo}).",
                severidad="media", app_user_id=quien.app_user_id, chat_id=chat_id,
                etapa=ETAPA_ALTA_CORREO)
            _responder(cur, workspace_id, chat_id, quien, NOTICIA_NEUTRA_INCIDENTE, ahora)
            return
        if (exc.motivo == "verification_send_limit"
                and not AC.aviso_pendiente(cur, AC.TIPO_CORREO_LIMITE_AGOTADO,
                                          "membership", quien.membership_id)):
            # "Exactamente una vez" (G1b2, ítem 5): mientras el aviso siga
            # sin resolver, un nuevo golpe contra el mismo límite no crea
            # otro -- leído ≠ resuelto; resolverlo (F, G1d-b) es "Habilitar
            # un nuevo intento" desde el bot de administración. El nombre
            # (nunca el correo) identifica a la persona para quien
            # administra -- ver `_texto_aviso` (`avisos_admin.py`) para el
            # encabezado completo.
            AC.crear_aviso(
                cur, AC.TIPO_CORREO_LIMITE_AGOTADO,
                f"{quien.nombre} agotó los 5 envíos del correo de verificación.",
                workspace_id=workspace_id, referencia_tipo="membership",
                referencia_id=quien.membership_id, ahora=ahora)
        _responder(cur, workspace_id, chat_id, quien, texto, ahora)
        return
    except Exception:  # noqa: BLE001
        registrar_incidente(
            cur, workspace_id, "Falló el envío del correo de verificación.",
            severidad="alta", app_user_id=quien.app_user_id, chat_id=chat_id,
            etapa=ETAPA_ALTA_CORREO)
        _responder(cur, workspace_id, chat_id, quien, NOTICIA_NEUTRA_INCIDENTE, ahora)
        return

    _responder(cur, workspace_id, chat_id, quien, texto_exito, ahora)


def _atender_pending_verification(cur, quien, texto: str, workspace_id: str,
                                  chat_id: int, ahora: datetime,
                                  bot_username_resolver, nombre_preferido: str
                                  ) -> None:
    correos = extraer_correos(texto)
    if len(correos) == 1:
        vigente = AC.verificacion_vigente(cur, quien.membership_id)
        candidato = AC.normalizar_correo(correos[0])
        if vigente is None or candidato != vigente["email"]:
            _proponer_cambio(cur, quien, correos[0], workspace_id, chat_id, ahora)
            return
    _recordatorio(cur, quien, workspace_id, chat_id, ahora)


# ---------------------------------------------------------------------------
# Botones -- sentinelas interceptados por `gateway._toque`, mismo mecanismo
# que `_SENTINEL_ACLARACION`/`P.SENTINEL_OPCIONES_MODELO`: nunca son un
# nombre real de `herramientas.REGISTRO`.
# ---------------------------------------------------------------------------

SENTINEL_ELEGIR_CORREO = "_alta_correo_elegir"
SENTINEL_RECORDATORIO = "_alta_correo_recordatorio"
SENTINEL_CAMBIO = "_alta_correo_cambio"

SENTINELS = (SENTINEL_ELEGIR_CORREO, SENTINEL_RECORDATORIO, SENTINEL_CAMBIO)

VIGENCIA_BOTONES = timedelta(hours=1)


def _ofrecer_eleccion_correo(cur, quien, candidatos: list[str], workspace_id: str,
                             chat_id: int, ahora: datetime) -> None:
    # `campo="eleccion"` es lo que hace que `resolver_pendiente` devuelva, en
    # `args["eleccion"]`, el valor de la opción tocada -- mismo mecanismo que
    # documenta `gateway.py` para `_SENTINEL_ACLARACION` (sin `campo`, el
    # valor del botón se descarta y sólo sobrevive `Confirmar`/`Cancelar`).
    from . import pendientes as P

    opciones = [(c, {"email": AC.normalizar_correo(c)}) for c in candidatos]
    pendiente = P.registrar(
        cur, quien, herramienta=SENTINEL_ELEGIR_CORREO, args={}, campo="eleccion",
        resumen=TEXTO_MULTIPLES_CORREOS, vence_en=ahora + VIGENCIA_BOTONES,
        chat_id=chat_id, opciones=opciones)
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id, text=TEXTO_MULTIPLES_CORREOS,
        scheduled_for=ahora,
        dedupe_key=(f"{workspace_id}:alta-correo:elegir:{quien.membership_id}:"
                   f"{ahora.timestamp()}"),
        is_response=True, allow_split=True, pending_action_id=pendiente.id)


def _recordatorio(cur, quien, workspace_id: str, chat_id: int, ahora: datetime) -> None:
    """B2. El correo mostrado es el que sigue vigente -- si por alguna
    razón no hubiera ninguno (no debería pasar en `pending_email_
    verification`), el texto queda sin dirección antes que reventar."""
    from . import pendientes as P

    vigente = AC.verificacion_vigente(cur, quien.membership_id)
    correo = vigente["email"] if vigente else "esa dirección"
    texto = texto_recordatorio_pendiente(correo)
    pendiente = P.registrar(
        cur, quien, herramienta=SENTINEL_RECORDATORIO, args={}, campo="eleccion",
        resumen=texto, vence_en=ahora + VIGENCIA_BOTONES,
        chat_id=chat_id,
        opciones=[(ETIQUETA_REENVIAR, {"accion": "reenviar"}),
                 (ETIQUETA_CAMBIAR, {"accion": "cambiar"})])
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id,
        text=texto, scheduled_for=ahora,
        dedupe_key=(f"{workspace_id}:alta-correo:recordatorio:{quien.membership_id}:"
                   f"{ahora.timestamp()}"),
        is_response=True, allow_split=True, pending_action_id=pendiente.id)


def _proponer_cambio(cur, quien, correo_crudo: str, workspace_id: str, chat_id: int,
                     ahora: datetime) -> None:
    """B3. `anterior` es el correo hoy vigente -- lo muestran tanto el
    texto como el botón de "dejar la anterior" (aprobado por el usuario,
    2026-09-28)."""
    from . import pendientes as P

    email = AC.normalizar_correo(correo_crudo)
    vigente = AC.verificacion_vigente(cur, quien.membership_id)
    anterior = vigente["email"] if vigente else "la anterior"
    texto = texto_propone_cambio(correo_crudo, anterior)
    pendiente = P.registrar(
        cur, quien, herramienta=SENTINEL_CAMBIO, args={}, campo="eleccion",
        resumen=texto, vence_en=ahora + VIGENCIA_BOTONES,
        chat_id=chat_id,
        opciones=[(etiqueta_usar_nuevo(correo_crudo), {"accion": "cambiar", "email": email}),
                 (etiqueta_dejar_anterior(anterior), {"accion": "mantener"})])
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id, text=texto,
        scheduled_for=ahora,
        dedupe_key=(f"{workspace_id}:alta-correo:proponer:{quien.membership_id}:"
                   f"{ahora.timestamp()}"),
        is_response=True, allow_split=True, pending_action_id=pendiente.id)


def _enlace_reemplazado(cur, quien, workspace_id: str, chat_id: int, ahora: datetime) -> None:
    """B7b. Reusa el mismo sentinel que `_recordatorio`
    (`SENTINEL_RECORDATORIO`): un solo botón, "Reenviar el último", cuya
    acción (`"reenviar"`) `resolver_toque` ya sabe resolver -- reenvía al
    correo hoy vigente. No hace falta un sentinel propio."""
    from . import pendientes as P

    pendiente = P.registrar(
        cur, quien, herramienta=SENTINEL_RECORDATORIO, args={}, campo="eleccion",
        resumen=TEXTO_ENLACE_REEMPLAZADO, vence_en=ahora + VIGENCIA_BOTONES,
        chat_id=chat_id,
        opciones=[(ETIQUETA_REENVIAR_ULTIMO, {"accion": "reenviar"})])
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id, text=TEXTO_ENLACE_REEMPLAZADO,
        scheduled_for=ahora,
        dedupe_key=(f"{workspace_id}:alta-correo:reemplazado:{quien.membership_id}:"
                   f"{ahora.timestamp()}"),
        is_response=True, allow_split=True, pending_action_id=pendiente.id)


def ofrecer_reintento_habilitado(cur, quien, workspace_id: str, chat_id: int,
                                 ahora: datetime, correo: str) -> None:
    """F (G1d-b, acción de la administración sobre "envíos agotados"): tras
    "Habilitar un nuevo intento", esto es lo que le llega a la persona
    -- llamado desde `avisos_admin.confirmar_habilitar`, nunca desde el
    gateway del espacio (por eso es público, sin guión bajo). Mismo
    mecanismo de botones que `_recordatorio` (`SENTINEL_RECORDATORIO`): "Sí,
    a {correo}" reenvía al vigente, "Usar otro correo" vuelve a
    `awaiting_email` -- ambos ya resueltos por `resolver_toque`."""
    from . import pendientes as P

    texto = texto_reintento_habilitado(correo)
    pendiente = P.registrar(
        cur, quien, herramienta=SENTINEL_RECORDATORIO, args={}, campo="eleccion",
        resumen=texto, vence_en=ahora + VIGENCIA_BOTONES, chat_id=chat_id,
        opciones=[(etiqueta_si_a(correo), {"accion": "reenviar"}),
                 (ETIQUETA_CAMBIAR, {"accion": "cambiar"})])
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id, text=texto,
        scheduled_for=ahora,
        dedupe_key=(f"{workspace_id}:alta-correo:reintento-habilitado:"
                   f"{quien.membership_id}:{ahora.timestamp()}"),
        is_response=True, allow_split=True, pending_action_id=pendiente.id)


def _estado_esperado_por_boton(herramienta: str) -> str | None:
    """El estado del ciclo bajo el que se ofreció cada botón -- ninguno de
    éstos tiene sentido en otro estado. `None` para cualquier otro
    `herramienta` (no es un sentinel de este módulo)."""
    if herramienta == SENTINEL_ELEGIR_CORREO:
        return "awaiting_email"
    if herramienta in (SENTINEL_RECORDATORIO, SENTINEL_CAMBIO):
        return "pending_email_verification"
    return None


def resolver_toque(cur, quien, workspace_id: str, chat_id: int, herramienta: str,
                   args: dict, ahora: datetime,
                   bot_username_resolver: Callable[[], str]) -> None:
    """Despacha el botón apretado -- `gateway._toque` ya validó que le
    corresponde a esta membresía (`pendientes.resolver`, motivo `ajena` si
    no) antes de llegar acá.

    Antes de actuar, relee el estado del ciclo (G1b2, ítem 3): el botón
    quedó congelado con el estado que tenía cuando se ofreció, pero el
    ciclo puede haber avanzado por otro camino mientras tanto (otro correo
    ya enviado, la verificación ya completada). Si el estado actual ya no
    es el que ese botón esperaba, no hace nada dañino -- ni emite, ni
    transiciona, ni intenta nada -- y responde según el estado VIGENTE
    (B9, `_responder_estado_actual`; G1d-b2, ítem 5: antes era el texto
    fijo `TEXTO_ESTADO_CAMBIO`, un callejón sin salida), nunca un
    incidente por un toque viejo normal.

    `args` llega como `{"eleccion": <valor de la opción tocada>}`: así
    registró la opción `_ofrecer_eleccion_correo`/`_recordatorio`/
    `_proponer_cambio`, con `campo="eleccion"` (`resolver_pendiente` sólo
    fusiona el valor de la opción en `args` cuando la acción declaró un
    `campo`; sin él, se pierde -- ver `pendientes.registrar`)."""
    from .gateway import _responder

    nombre_preferido = _nombre_preferido(quien.nombre)
    eleccion = args.get("eleccion") or {}

    esperado = _estado_esperado_por_boton(herramienta)
    actual = AC.estado(cur, quien.membership_id)
    estado_actual = actual["estado"] if actual else None
    if esperado is not None and estado_actual != esperado:
        # G1d-b2, ítem 5: antes esto respondía el texto fijo
        # `TEXTO_ESTADO_CAMBIO` ("...escribime y lo vemos...") -- un
        # callejón sin salida. Ahora sigue el mismo estado vigente (B9) que
        # cualquier otro caso de "lo que esperaba ya no está" --
        # `_responder_estado_actual`.
        _responder_estado_actual(cur, quien, workspace_id, chat_id, ahora)
        return

    if herramienta == SENTINEL_ELEGIR_CORREO:
        _validar_y_emitir(cur, quien, eleccion["email"], workspace_id, chat_id, ahora,
                          bot_username_resolver, nombre_preferido)
        return

    if herramienta == SENTINEL_RECORDATORIO:
        if eleccion.get("accion") == "cambiar":
            AC.transicionar(cur, quien.membership_id, "awaiting_email",
                            actor_kind="persona", actor_app_user_id=quien.app_user_id,
                            ahora=ahora)
            _responder(cur, workspace_id, chat_id, quien, TEXTO_PEDIDO_CORREO, ahora)
            return
        vigente = AC.verificacion_vigente(cur, quien.membership_id)
        if vigente is None:
            _responder(cur, workspace_id, chat_id, quien, TEXTO_SIN_ENVIO_VIGENTE, ahora)
            return
        _emitir_y_enviar(cur, quien, vigente["email"], workspace_id, chat_id, ahora,
                         bot_username_resolver, nombre_preferido, TEXTO_GRACIAS_ENVIADO)
        return

    if herramienta == SENTINEL_CAMBIO:
        if eleccion.get("accion") == "mantener":
            _responder(cur, workspace_id, chat_id, quien, TEXTO_MANTENER_CONFIRMADO, ahora)
            return
        # G1d-c2, ítem 1: misma validación de formato + dominios habilitados
        # que cualquier otro correo nuevo -- antes este botón saltaba directo
        # a `_emitir_y_enviar` y se saltaba el filtro de dominios.
        email = AC.normalizar_correo(eleccion["email"])
        rechazo = _texto_rechazo_formato_o_dominio(cur, workspace_id, email)
        if rechazo is not None:
            _responder(cur, workspace_id, chat_id, quien, rechazo, ahora)
            return
        # La transición a `awaiting_email` va DENTRO del savepoint de
        # `_emitir_y_enviar` (`transicion_previa`), no antes -- G1b2, ítem 2.
        _emitir_y_enviar(cur, quien, email, workspace_id, chat_id, ahora,
                         bot_username_resolver, nombre_preferido, TEXTO_GRACIAS_ENVIADO,
                         transicion_previa="awaiting_email")
        return


# ---------------------------------------------------------------------------
# `/start pv_{token}` -- llamada desde `gateway._activacion`
# ---------------------------------------------------------------------------


def resolver_verificacion_correo(conn, workspace_id: str, token: str, tg_user: int,
                                 chat_id: int, *,
                                 bot_username_resolver: Callable[[], str] | None = None
                                 ) -> dict:
    """La persona volvió del correo con `/start pv_{token}`.

    B6 (textos aprobados por el usuario, 2026-09-28): un token REAL abierto
    por la cuenta equivocada (integrante o no) recibe `TEXTO_CUENTA_
    INCORRECTA`, sin consumirse; un token que no existe, de una cuenta
    desconocida, no recibe respuesta (como siempre). `AC.existe_
    verificacion` es la única fuente de "existe/no existe" -- nunca revela
    nada más (ni dueño, ni correo, ni estado).

    Las fallas inesperadas (no las rechazadas por motivo tipado) las atrapa
    `gateway.procesar_update`, igual que el resto de `_activacion`."""
    from datetime import datetime, timezone

    from .autoridad import Denegado, identificar_en_espacio
    from .db import espacio

    # `espacio()` abre con `conn.transaction()`, que ya confirma sola al
    # salir limpio del `with` -- ningún `conn.commit()` manual acá adentro
    # (psycopg3 lo rechaza mientras ese contexto sigue abierto; mismo motivo
    # documentado en `gateway._toque`).
    ahora = datetime.now(timezone.utc)
    with espacio(conn, workspace_id) as cur:
        try:
            quien = identificar_en_espacio(cur, tg_user, workspace_id)
        except Denegado:
            quien = None

        if quien is None:
            if AC.existe_verificacion(cur, token):
                _responder_cuenta_incorrecta(cur, workspace_id, chat_id, ahora)
            return {"ok": True}

        reserva = AC.reservar_verificacion(cur, token, quien.membership_id, ahora=ahora)
        if not reserva.ok:
            _responder_falla_verificacion(
                cur, quien, workspace_id, chat_id, ahora, reserva.motivo,
                bot_username_resolver=bot_username_resolver,
                token_existe=lambda: AC.existe_verificacion(cur, token))
            return {"ok": True}

        completado = AC.completar_verificacion(cur, token, quien.membership_id,
                                               ahora=ahora)
        if not completado.ok:
            _responder_falla_verificacion(
                cur, quien, workspace_id, chat_id, ahora, completado.motivo,
                bot_username_resolver=bot_username_resolver,
                token_existe=lambda: True)
            return {"ok": True}

        # G1c: el texto final difiere por modo -- `texto_verificado` (el del
        # pack) da por hecho que la persona recién se está dando de alta;
        # quien ya estaba activa (`existente`) necesita la variante propia
        # (ver su docstring). El modo no cambia dentro de un ciclo, así que
        # leer la proyección ya actualizada alcanza.
        from .gateway import _responder

        nombre_preferido = _nombre_preferido(quien.nombre)
        proyeccion = AC.estado(cur, quien.membership_id)
        texto_exito = (texto_verificado_existente(nombre_preferido)
                       if proyeccion and proyeccion["modo"] == "existente"
                       else texto_verificado(nombre_preferido))
        _responder(cur, workspace_id, chat_id, quien, texto_exito, ahora)
    return {"ok": True}


def _responder_cuenta_incorrecta(cur, workspace_id: str, chat_id: int,
                                 ahora: datetime) -> None:
    """B6: sale igual para un desconocido que para un integrante -- no hace
    falta identificar a quien escribe para decirle esto, así que no usa
    `_responder` (que exige un `quien` ya identificado en el espacio)."""
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id, text=TEXTO_CUENTA_INCORRECTA,
        scheduled_for=ahora,
        dedupe_key=f"{workspace_id}:alta-correo:cuenta-incorrecta:{chat_id}:{ahora.timestamp()}",
        is_response=True, allow_split=True)


def _responder_estado_actual(cur, quien, workspace_id: str, chat_id: int,
                             ahora: datetime) -> None:
    """B9: sin texto fijo -- Prisma sigue desde el estado ACTUAL del ciclo,
    no del que esperaba quien llama. Es el único router de "lo que
    esperaba ya no está": lo usan el motivo tipado `verification_state_
    changed`, el reenvío sin nada que reenviar (`_reenviar_por_enlace_
    roto_o_vencido`, cuando no hay ningún envío vigente) y un botón viejo
    (`resolver_toque`) cuyo estado esperado ya no coincide (G1d-b2, ítem 5:
    antes estos tres caminos terminaban en `TEXTO_ESTADO_CAMBIO`, un
    callejón sin salida retirado en esta corrección).

    - `awaiting_email`: pide el correo (igual que siempre).
    - `active`: confirma que ya está verificado (el texto del pack, o el
      de `existente` si corresponde).
    - `pending_email_verification`: retoma el mismo camino que un reenvío
      pedido a mano -- recordatorio con botones (B2) si hay un envío
      vigente, o "todavía no tengo tu correo" (B10) si no.
    - `pending_welcome`: completa la bienvenida pendiente (mismo mecanismo
      idempotente que ya usa `gate()` para este mismo estado residual).
    - `revoked` o sin ningún ciclo abierto: ningún texto aprobado cubre
      este caso (no debería ser alcanzable desde ninguno de los tres
      caminos de arriba) -- nunca fallar en silencio: incidente saneado y
      el aviso neutral de siempre, nunca un texto inventado.
    """
    from .gateway import ETAPA_ALTA_CORREO, NOTICIA_NEUTRA_INCIDENTE, _responder
    from .incidentes import registrar_incidente

    actual = AC.estado(cur, quien.membership_id)
    estado = actual["estado"] if actual else None
    if estado == "awaiting_email":
        _responder(cur, workspace_id, chat_id, quien, TEXTO_PEDIDO_CORREO, ahora)
        return
    if estado == "active":
        nombre_preferido = _nombre_preferido(quien.nombre)
        texto = (texto_verificado_existente(nombre_preferido)
                 if actual["modo"] == "existente" else texto_verificado(nombre_preferido))
        _responder(cur, workspace_id, chat_id, quien, texto, ahora)
        return
    if estado == "pending_email_verification":
        vigente = AC.verificacion_vigente(cur, quien.membership_id)
        if vigente is not None:
            _recordatorio(cur, quien, workspace_id, chat_id, ahora)
        else:
            _responder(cur, workspace_id, chat_id, quien, TEXTO_SIN_ENVIO_VIGENTE, ahora)
        return
    if estado == "pending_welcome":
        _completar_bienvenida(cur, quien.membership_id, workspace_id, chat_id,
                              quien.nombre, ahora)
        return
    registrar_incidente(
        cur, workspace_id,
        f"alta_correo: no hay ningún texto aprobado para el estado {estado!r}.",
        severidad="media", app_user_id=quien.app_user_id, chat_id=chat_id,
        etapa=ETAPA_ALTA_CORREO)
    _responder(cur, workspace_id, chat_id, quien, NOTICIA_NEUTRA_INCIDENTE, ahora)


def _reenviar_por_enlace_roto_o_vencido(cur, quien, workspace_id: str, chat_id: int,
                                        ahora: datetime, bot_username_resolver,
                                        texto_reenviado: Callable[[str], str]) -> bool:
    """B5/B6 (G1d-b2, ítem 7): rama única para "Prisma manda uno nuevo
    sola" -- antes duplicada, casi idéntica, entre el enlace vencido y el
    roto; sólo cambiaba el texto de aviso. `True` si efectivamente reenvió
    (el ciclo sigue en `pending_email_verification` con un envío vigente
    del que retomar la dirección); `False` si no corresponde -- quien
    llama sigue por el estado actual (B9, `_responder_estado_actual`)."""
    actual = AC.estado(cur, quien.membership_id)
    if not (actual and actual["estado"] == "pending_email_verification"):
        return False
    vigente = AC.verificacion_vigente(cur, quien.membership_id)
    if vigente is None:
        return False
    nombre_preferido = _nombre_preferido(quien.nombre)
    _emitir_y_enviar(cur, quien, vigente["email"], workspace_id, chat_id, ahora,
                     bot_username_resolver, nombre_preferido, texto_reenviado(vigente["email"]))
    return True


def _responder_falla_verificacion(cur, quien, workspace_id: str, chat_id: int,
                                  ahora: datetime, motivo: str, *,
                                  bot_username_resolver: Callable[[], str] | None = None,
                                  token_existe: Callable[[], bool] | None = None) -> None:
    from .gateway import ETAPA_ALTA_CORREO, NOTICIA_NEUTRA_INCIDENTE, _responder
    from .incidentes import registrar_incidente

    if motivo == "verification_token_expired":
        # B5: Prisma manda uno nuevo sola, respetando los límites (sin
        # envíos disponibles, `_emitir_y_enviar` cae sola en B11 o B12). Sin
        # nada que reenviar (edge case: el ciclo ya no está en `pending_
        # email_verification`, o no hay ningún envío vigente), sigue el
        # estado actual (B9) en vez del texto fijo retirado (ítem 5).
        if _reenviar_por_enlace_roto_o_vencido(
                cur, quien, workspace_id, chat_id, ahora, bot_username_resolver,
                texto_enlace_vencido_reenviado):
            return
        _responder_estado_actual(cur, quien, workspace_id, chat_id, ahora)
        return

    if motivo == "verification_token_superseded":
        _enlace_reemplazado(cur, quien, workspace_id, chat_id, ahora)
        return

    if motivo == "verification_state_changed":
        _responder_estado_actual(cur, quien, workspace_id, chat_id, ahora)
        return

    if motivo == "verification_token_consumed":
        # G1d-c2, ítem 9: un enlace YA usado no siempre significa que el
        # ciclo ACTUAL siga verificado -- puede venir de un ciclo anterior
        # al vigente (revocación y reactivación, por ejemplo). B7 ("Tu
        # correo ya está verificado ✅") sólo es cierto si el ciclo de HOY
        # está `active`; para cualquier otro estado se sigue el mismo
        # enrutador único (B9, `_responder_estado_actual`) que ya usan
        # `resolver_toque` y el resto de este motivo tipado -- antes había
        # acá una copia desalineada de ese mismo enrutador (`awaiting_email`
        # y `pending_email_verification` repetidos a mano) que, a diferencia
        # del original, nunca comprobaba si había un envío vigente: un enlace
        # consumido sobre un ciclo `pending_email_verification` SIN ningún
        # envío vigente caía en `_recordatorio` (que arma "esa dirección" sin
        # avisar de nada raro) en vez de "Todavía no tengo tu correo"
        # (`TEXTO_SIN_ENVIO_VIGENTE`, B10) -- la misma copia nunca llegaba a
        # exhibir la falla, sólo la disimulaba.
        actual = AC.estado(cur, quien.membership_id)
        if actual is not None and actual["estado"] == "active":
            _responder(cur, workspace_id, chat_id, quien, TEXTO_YA_VERIFICADO, ahora)
            return
        _responder_estado_actual(cur, quien, workspace_id, chat_id, ahora)
        return

    if motivo == "verification_token_invalid":
        if token_existe is not None and token_existe():
            # B6: real, pero no es el dueño.
            _responder(cur, workspace_id, chat_id, quien, TEXTO_CUENTA_INCORRECTA, ahora)
            return
        # B6: roto/inexistente -- un integrante con verificación pendiente
        # recibe uno nuevo sola; si no corresponde, sigue el estado actual
        # (B9) en vez del texto fijo retirado (ítem 5).
        if _reenviar_por_enlace_roto_o_vencido(
                cur, quien, workspace_id, chat_id, ahora, bot_username_resolver,
                texto_enlace_roto_reenviado):
            return
        _responder_estado_actual(cur, quien, workspace_id, chat_id, ahora)
        return

    texto = _TEXTOS_VERIFICACION_FALLIDA.get(motivo)
    if texto is None:
        registrar_incidente(
            cur, workspace_id, f"Verificación de correo rechazada ({motivo}).",
            severidad="media", app_user_id=quien.app_user_id, chat_id=chat_id,
            etapa=ETAPA_ALTA_CORREO)
        _responder(cur, workspace_id, chat_id, quien, NOTICIA_NEUTRA_INCIDENTE, ahora)
        return
    _responder(cur, workspace_id, chat_id, quien, texto, ahora)
