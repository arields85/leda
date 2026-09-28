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

ETIQUETA_REENVIAR = "Reenviar correo"
ETIQUETA_CAMBIAR = "Cambiar correo"
ETIQUETA_MANTENER = "Mantener correo anterior"


def etiqueta_cambiar_a(email: str) -> str:
    return f"Cambiar correo a {email}"


def _nombre_preferido(nombre: str) -> str:
    """Primera palabra de `nombre`, o cadena vacía si no hay ninguna (nombre
    vacío o de sólo espacios) -- nunca `IndexError` (G1b2, ítem 5: antes,
    `nombre.split()[0]` reventaba con ese `nombre`).

    Con cadena vacía, los textos que la reciben saludan sin nombre: el pack
    (`06-SALUDOS-TONO-E-ICONOGRAFIA.md`, §"Uso del nombre") admite
    explícitamente "si no está disponible, saludar sin nombre"."""
    partes = nombre.split()
    return partes[0] if partes else ""


def texto_bienvenida(saludo: str, nombre_preferido: str) -> str:
    quien_saluda = f", {nombre_preferido}" if nombre_preferido else ""
    return (f"{saludo}{quien_saluda}. Soy Prisma, la coordinadora "
            "digital del equipo. Mi función es ayudarlos a mantener claros "
            "los objetivos, organizar tareas, registrar avances y detectar "
            "bloqueos con anticipación. Voy a procurar que el seguimiento "
            "sea útil, breve y agradable.")


def texto_verificado(nombre_preferido: str) -> str:
    quien_agradece = f", {nombre_preferido}" if nombre_preferido else ""
    return (f"✅ Gracias{quien_agradece}. Tu correo quedó verificado y "
            "el registro está completo. Ya podés conversar conmigo "
            "normalmente.")


def cuerpo_verificacion(nombre_preferido: str, enlace: str) -> str:
    """Cuerpo del correo de verificación.

    El pack (§5) da el asunto, el saludo, la etiqueta del botón y describe
    el contenido (vence en 24 horas, un solo uso, misma cuenta de Telegram);
    no da el párrafo literal. Este texto es NUEVO -- reportado para revisión
    del usuario -- y deliberadamente NO ofrece "responder este correo" como
    alternativa: ADR 0010 excluye la verificación por respuesta de correo
    como mecanismo (C7/`01` §7).
    """
    saludo = f"Hola, {nombre_preferido}." if nombre_preferido else "Hola."
    return (
        f"{saludo}\n\n"
        "Para terminar tu alta en Prisma necesito que confirmes que este es "
        "tu correo laboral.\n\n"
        f"Verificar correo: {enlace}\n\n"
        "Este enlace vence en 24 horas, sirve una sola vez y tiene que "
        "abrirse con la misma cuenta de Telegram que usás para hablar con "
        "Prisma.")


# Textos nuevos, sin equivalente literal en el pack -- reportados aparte
# para revisión del usuario (no hay una frase original para estos casos).
TEXTO_MULTIPLES_CORREOS = (
    "Encontré más de un correo en ese mensaje. ¿Cuál de estos es el que "
    "querés usar?")
TEXTO_RECORDATORIO_PENDIENTE = (
    "Todavía estoy esperando que verifiques tu correo. Podés reenviarte el "
    "mensaje de verificación o cambiar la dirección.")
TEXTO_PROPONE_CAMBIO = (
    "Encontré una dirección distinta a la que ya te pedí verificar. "
    "¿Querés que te mande la verificación a esta nueva?")
TEXTO_MANTENER_CONFIRMADO = "Dale, seguimos con el correo anterior."
TEXTO_ENLACE_VENCIDO = "Ese enlace de verificación venció."
TEXTO_ENLACE_INVALIDO = (
    "Ese enlace no es válido. Si necesitás verificar tu correo, pedime "
    "que te lo reenvíe.")
TEXTO_ENLACE_USADO = (
    "Ese enlace ya se usó. Si necesitás verificar tu correo, pedime que "
    "te lo reenvíe.")
TEXTO_VERIFICACION_OCUPADA = (
    "Ya estoy procesando esa verificación. Esperá un momento y fijate si "
    "te llegó la confirmación.")
TEXTO_ESTADO_CAMBIO = (
    "El estado de tu registro cambió mientras verificabas ese correo. "
    "Escribime y lo vemos de nuevo.")
TEXTO_SIN_ENVIO_VIGENTE = (
    "No encontré ningún envío pendiente para reenviar. Escribime tu "
    "correo laboral y te mando uno nuevo.")

_TEXTOS_MOTIVO_EMISION = {
    "email_in_use": TEXTO_CORREO_EN_USO,
    "verification_rate_limited": (
        "Probaste varias veces en la última hora. Esperá un poco antes de "
        "volver a pedir el correo de verificación."),
    "verification_send_limit": (
        "Ya alcanzaste el máximo de reenvíos para este intento de "
        "verificación. Quedó registrado para que administración te ayude."),
}

_TEXTOS_VERIFICACION_FALLIDA = {
    "verification_token_invalid": TEXTO_ENLACE_INVALIDO,
    "verification_token_consumed": TEXTO_ENLACE_USADO,
    "verification_token_busy": TEXTO_VERIFICACION_OCUPADA,
    "verification_state_changed": TEXTO_ESTADO_CAMBIO,
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
                     chat_id: int, nombre: str, ahora: datetime) -> None:
    """Activación con la clave encendida: abre `pending_welcome` y completa
    los pasos hasta `awaiting_email`, en la misma transacción que
    `onboarding.activar()` ya viene usando."""
    AC.iniciar_ciclo(cur, membership_id, "alta", ahora=ahora)
    _completar_bienvenida(cur, membership_id, workspace_id, chat_id, nombre, ahora)


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
    disparador de la base)."""
    actual = AC.estado(cur, membership_id)
    if actual is not None and actual["estado"] != "pending_welcome":
        return
    nombre_preferido = _nombre_preferido(nombre)
    zona = _zona_horaria(cur, workspace_id)
    saludo = saludo_para(ahora, zona)
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id,
        text=texto_bienvenida(saludo, nombre_preferido),
        message_type="informativo", scheduled_for=ahora,
        dedupe_key=f"{workspace_id}:alta-correo:bienvenida:{membership_id}",
        is_response=True, allow_split=True)
    # Un microsegundo después, no al mismo instante: son dos llamadas
    # separadas a `enqueue_outbox` (no dos partes de un mismo mensaje
    # partido), así que sin este desplazamiento `programado_para` empataría
    # y el orden de entrega del despachador quedaría al azar -- el pedido de
    # correo podría llegar antes que la bienvenida.
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id, text=TEXTO_PEDIDO_CORREO,
        message_type="informativo", scheduled_for=ahora + timedelta(microseconds=1),
        dedupe_key=f"{workspace_id}:alta-correo:pedido:{membership_id}",
        is_response=True, allow_split=True)
    AC.bienvenida_entregada(cur, membership_id, ahora=ahora)
    AC.transicionar(cur, membership_id, "awaiting_email", actor_kind="sistema",
                    ahora=ahora)


# ---------------------------------------------------------------------------
# El control (gate) -- antepuesto al despacho conversacional
# ---------------------------------------------------------------------------

# Los tres estados por debajo de `active` en modo `alta` -- mientras la
# proyección esté en uno de éstos, ninguna herramienta de negocio puede
# correr para esta membresía, sea el chat que sea (G1b2, ítem 1).
_ESTADOS_BLOQUEANTES = ("pending_welcome", "awaiting_email",
                       "pending_email_verification")


def _gateada(actual: dict | None) -> bool:
    return (actual is not None and actual["modo"] == "alta"
            and actual["estado"] in _ESTADOS_BLOQUEANTES)


def bloqueada_para_negocio(cur: psycopg.Cursor, membership_id: str) -> bool:
    """`True` si esta membresía sigue en modo `alta` por debajo de `active`.

    La usan los chats que no son privados -- `gate()` sólo corre en privado
    (G1b2, ítem 1: antes corría para cualquier chat, y en un grupo llegaba a
    pedir/mostrar/procesar un correo, o dejaba pasar el mensaje a una
    herramienta de negocio para quien todavía no verificó el suyo). En un
    grupo no hay recorrido de correo que ofrecer: la respuesta correcta es
    no hacer nada -- ni responder ni rutear a ningún lado."""
    return _gateada(AC.estado(cur, membership_id))


def gate(cur: psycopg.Cursor, quien: Any, texto: str, *, chat_id: int,
         workspace_id: str, ahora: datetime,
         bot_username_resolver: Callable[[], str]) -> bool:
    """`True` si el mensaje quedó atendido por el recorrido de alta con
    correo -- no hay que rutearlo a intake ni al agente. `False` si esta
    membresía no está en modo `alta` con un ciclo abierto por debajo de
    `active` (incluye la clave apagada, donde nunca hay ciclo). Sólo tiene
    sentido llamarla en un chat privado -- ver `bloqueada_para_negocio`
    para lo que corresponde en cualquier otro tipo de chat."""
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


def _validar_y_emitir(cur, quien, correo_crudo: str, workspace_id: str, chat_id: int,
                      ahora: datetime, bot_username_resolver, nombre_preferido: str
                      ) -> None:
    from .gateway import _responder

    email = AC.normalizar_correo(correo_crudo)
    if not _formato_valido(email):
        _responder(cur, workspace_id, chat_id, quien, TEXTO_DIRECCION_INCOMPLETA, ahora)
        return
    permitidos = AC.dominios_permitidos(cur, workspace_id)
    dominio = email.rpartition("@")[2]
    if permitidos is not None and dominio not in permitidos:
        _responder(cur, workspace_id, chat_id, quien, TEXTO_DOMINIO_NO_HABILITADO, ahora)
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
    enlace que la base terminó sin registrar."""
    from .gateway import ETAPA_ALTA_CORREO, NOTICIA_NEUTRA_INCIDENTE, _registrar_incidente, _responder

    sender = obtener_emisor_configurado(cur, workspace_id)
    if sender is None:
        _registrar_incidente(
            cur, workspace_id,
            "La verificación de correo está encendida pero no hay emisor "
            "de correo configurado.",
            severidad="alta", app_user_id=quien.app_user_id, chat_id=chat_id,
            etapa=ETAPA_ALTA_CORREO)
        AC.crear_aviso(
            cur, "correo_sin_emisor",
            "La verificación de correo está encendida pero no hay un emisor "
            "de correo configurado para el espacio.",
            workspace_id=workspace_id, referencia_tipo="membership",
            referencia_id=quien.membership_id, ahora=ahora)
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
        texto = _TEXTOS_MOTIVO_EMISION.get(exc.motivo)
        if texto is None:
            _registrar_incidente(
                cur, workspace_id,
                f"La emisión de verificación se rechazó ({exc.motivo}).",
                severidad="media", app_user_id=quien.app_user_id, chat_id=chat_id,
                etapa=ETAPA_ALTA_CORREO)
            _responder(cur, workspace_id, chat_id, quien, NOTICIA_NEUTRA_INCIDENTE, ahora)
            return
        if (exc.motivo == "verification_send_limit"
                and not AC.aviso_pendiente(cur, "correo_limite_agotado",
                                          "membership", quien.membership_id)):
            # "Exactamente una vez" (G1b2, ítem 5): mientras el aviso siga
            # sin resolver, un nuevo golpe contra el mismo límite no crea
            # otro -- leído ≠ resuelto, y resolverlo es tarea de
            # administración (G1d).
            AC.crear_aviso(
                cur, "correo_limite_agotado",
                "Se agotaron los reenvíos del ciclo de verificación de correo.",
                workspace_id=workspace_id, referencia_tipo="membership",
                referencia_id=quien.membership_id, ahora=ahora)
        _responder(cur, workspace_id, chat_id, quien, texto, ahora)
        return
    except Exception:  # noqa: BLE001
        _registrar_incidente(
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
    from . import pendientes as P

    pendiente = P.registrar(
        cur, quien, herramienta=SENTINEL_RECORDATORIO, args={}, campo="eleccion",
        resumen=TEXTO_RECORDATORIO_PENDIENTE, vence_en=ahora + VIGENCIA_BOTONES,
        chat_id=chat_id,
        opciones=[(ETIQUETA_REENVIAR, {"accion": "reenviar"}),
                 (ETIQUETA_CAMBIAR, {"accion": "cambiar"})])
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id,
        text=TEXTO_RECORDATORIO_PENDIENTE, scheduled_for=ahora,
        dedupe_key=(f"{workspace_id}:alta-correo:recordatorio:{quien.membership_id}:"
                   f"{ahora.timestamp()}"),
        is_response=True, allow_split=True, pending_action_id=pendiente.id)


def _proponer_cambio(cur, quien, correo_crudo: str, workspace_id: str, chat_id: int,
                     ahora: datetime) -> None:
    from . import pendientes as P

    email = AC.normalizar_correo(correo_crudo)
    pendiente = P.registrar(
        cur, quien, herramienta=SENTINEL_CAMBIO, args={}, campo="eleccion",
        resumen=TEXTO_PROPONE_CAMBIO, vence_en=ahora + VIGENCIA_BOTONES,
        chat_id=chat_id,
        opciones=[(etiqueta_cambiar_a(correo_crudo), {"accion": "cambiar", "email": email}),
                 (ETIQUETA_MANTENER, {"accion": "mantener"})])
    enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id, text=TEXTO_PROPONE_CAMBIO,
        scheduled_for=ahora,
        dedupe_key=(f"{workspace_id}:alta-correo:proponer:{quien.membership_id}:"
                   f"{ahora.timestamp()}"),
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
    transiciona, ni intenta nada -- y devuelve un texto neutral ya
    existente (`TEXTO_ESTADO_CAMBIO`), nunca un incidente por un toque
    viejo normal.

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
        _responder(cur, workspace_id, chat_id, quien, TEXTO_ESTADO_CAMBIO, ahora)
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
        # La transición a `awaiting_email` va DENTRO del savepoint de
        # `_emitir_y_enviar` (`transicion_previa`), no antes -- G1b2, ítem 2.
        _emitir_y_enviar(cur, quien, eleccion["email"], workspace_id, chat_id, ahora,
                         bot_username_resolver, nombre_preferido, TEXTO_GRACIAS_ENVIADO,
                         transicion_previa="awaiting_email")
        return


# ---------------------------------------------------------------------------
# `/start pv_{token}` -- llamada desde `gateway._activacion`
# ---------------------------------------------------------------------------


def resolver_verificacion_correo(conn, workspace_id: str, token: str, tg_user: int,
                                 chat_id: int) -> dict:
    """La persona volvió del correo con `/start pv_{token}`.

    Nunca revela de quién es un token ajeno (A04): un desconocido y un
    token que no le pertenece a quien lo aprieta se tratan igual, con el
    mismo motivo genérico devuelto por `reservar_verificacion_correo`. Las
    fallas inesperadas (no las rechazadas por motivo tipado) las atrapa
    `gateway.procesar_update`, igual que el resto de `_activacion`."""
    from datetime import datetime, timezone

    from .autoridad import Denegado, identificar_en_espacio
    from .db import espacio
    from .gateway import _responder

    # `espacio()` abre con `conn.transaction()`, que ya confirma sola al
    # salir limpio del `with` -- ningún `conn.commit()` manual acá adentro
    # (psycopg3 lo rechaza mientras ese contexto sigue abierto; mismo motivo
    # documentado en `gateway._toque`).
    ahora = datetime.now(timezone.utc)
    with espacio(conn, workspace_id) as cur:
        try:
            quien = identificar_en_espacio(cur, tg_user, workspace_id)
        except Denegado:
            return {"ok": True}

        reserva = AC.reservar_verificacion(cur, token, quien.membership_id, ahora=ahora)
        if not reserva.ok:
            _responder_falla_verificacion(cur, quien, workspace_id, chat_id, ahora,
                                          reserva.motivo)
            return {"ok": True}

        completado = AC.completar_verificacion(cur, token, quien.membership_id,
                                               ahora=ahora)
        if not completado.ok:
            _responder_falla_verificacion(cur, quien, workspace_id, chat_id, ahora,
                                          completado.motivo)
            return {"ok": True}

        _responder(cur, workspace_id, chat_id, quien,
                  texto_verificado(_nombre_preferido(quien.nombre)), ahora)
    return {"ok": True}


def _responder_falla_verificacion(cur, quien, workspace_id: str, chat_id: int,
                                  ahora: datetime, motivo: str) -> None:
    from .gateway import ETAPA_ALTA_CORREO, NOTICIA_NEUTRA_INCIDENTE, _registrar_incidente, _responder

    if motivo == "verification_token_expired":
        actual = AC.estado(cur, quien.membership_id)
        if actual and actual["estado"] == "pending_email_verification":
            _recordatorio(cur, quien, workspace_id, chat_id, ahora)
        else:
            _responder(cur, workspace_id, chat_id, quien, TEXTO_ENLACE_VENCIDO, ahora)
        return

    texto = _TEXTOS_VERIFICACION_FALLIDA.get(motivo)
    if texto is None:
        _registrar_incidente(
            cur, workspace_id, f"Verificación de correo rechazada ({motivo}).",
            severidad="media", app_user_id=quien.app_user_id, chat_id=chat_id,
            etapa=ETAPA_ALTA_CORREO)
        _responder(cur, workspace_id, chat_id, quien, NOTICIA_NEUTRA_INCIDENTE, ahora)
        return
    _responder(cur, workspace_id, chat_id, quien, texto, ahora)
