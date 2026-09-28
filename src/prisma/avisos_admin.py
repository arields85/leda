"""Entrega de avisos "🛠️ Administración" por el bot de administración (G1d).

Unificado con T28 (decisión del usuario, 2026-09-28): un solo camino hacia la
administración de plataforma. Este módulo ya no tiene su propia cola de
salida (`aviso_administrativo_entrega`/`aviso_administrativo_respuesta` se
retiraron) -- entrega por `admin_notice`, la misma cola que
`incidentes.avisar_incidente_admin` ya usaba para los avisos de incidente
(migración 0017, extendida por 0100 para que una fila también pueda
referenciar un `aviso_administrativo` en vez de un incidente, y para que
lleve botones opcionales). El despacho en sí -- reintentos, backoff, qué pasa
si se agotan -- es `despachador.despachar_avisos_admin`, sin ninguna copia
propia acá.

Este módulo no valida autoridad: eso lo hace quien llama (`gateway.py`),
revalidando `platform_role administrador` en el momento del toque -- acá
sólo se asume ya identificado ("el canal manda", `autoridad.py`).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import psycopg

from . import alta_correo as AC
from .despachador import Boton

CALLBACK_PREFIJO = "adm"
ACCION_LEIDO = "leido"
ETIQUETA_MARCAR_LEIDO = "Marcar leído"

# G1d-b, acción F: "Habilitar un nuevo intento" sobre el aviso de envíos
# agotados -- vista previa, Confirmar, Cancelar. El estado del aviso mismo
# (`resuelto_en`) es la única fuente de idempotencia: no hace falta ninguna
# tabla de "pendiente de confirmar" propia del canal de administración (a
# diferencia de `pendientes.py`, que exige `workspace_id`/`membership_id` --
# un administrador de plataforma no necesariamente los tiene).
ACCION_HABILITAR = "habilitar"
ACCION_CONFIRMAR_HABILITAR = "confirmar_habilitar"
ACCION_CANCELAR_HABILITAR = "cancelar_habilitar"
ETIQUETA_HABILITAR = "Habilitar un nuevo intento"
ETIQUETA_CONFIRMAR = "Confirmar"
ETIQUETA_CANCELAR = "Cancelar"

TEXTO_ACCION_LIBRE = (
    "Las acciones de administración se hacen desde los botones de cada "
    "aviso, o desde el panel de plataforma. Un mensaje de texto acá no "
    "hace nada.")
TEXTO_MARCADO_LEIDO = "Marcado como leído."
TEXTO_HABILITAR_YA_RESUELTO = "Ese aviso ya estaba resuelto."
TEXTO_HABILITAR_CONFIRMADO = "Listo, habilitado."
TEXTO_HABILITAR_CANCELADO = "No se habilitó nada."

# G1d-b2, ítem 3 (revisión de G1d-b): resultados de `confirmar_habilitar` --
# antes devolvía un `bool` que confundía "ya estaba resuelto" (un doble tap
# genuino) con "no corresponde" (el ciclo ya no es el que el aviso
# describía). Los tres textos aprobados por el usuario (F, 2026-09-28) son
# ciertos cada uno sólo para su propio caso -- `TEXTO_HABILITAR_CANCELADO`
# ("No se habilitó nada.") es la única frase de las tres que sigue siendo
# cierta tanto si no correspondía aplicar nada como si la situación ya se
# resolvió sola (la persona quedó `active`): en los dos casos, ningún
# intento nuevo se habilitó.
RESULTADO_HABILITAR_APLICADO = "aplicado"
RESULTADO_HABILITAR_YA_RESUELTO = "ya_resuelto"
RESULTADO_HABILITAR_NO_APLICA = "no_aplica"

_TEXTOS_RESULTADO_HABILITAR = {
    RESULTADO_HABILITAR_APLICADO: TEXTO_HABILITAR_CONFIRMADO,
    RESULTADO_HABILITAR_YA_RESUELTO: TEXTO_HABILITAR_YA_RESUELTO,
    RESULTADO_HABILITAR_NO_APLICA: TEXTO_HABILITAR_CANCELADO,
}


def _ahora(valor: datetime | None) -> datetime:
    return valor or datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Botones -- prefijo genérico, para que agregar otra acción después sea
# sumar un valor a `ACCION_*`, nunca un esquema de callback nuevo.
# ---------------------------------------------------------------------------


def callback_data(accion: str, aviso_id: str) -> str:
    return f"{CALLBACK_PREFIJO}:{accion}:{aviso_id}"


def partes_de_callback(data: str) -> tuple[str, str] | None:
    """`(accion, aviso_id)` si `data` es un callback de este módulo, o
    `None` -- un callback ajeno (u otro botón viejo) no es un error, es
    sencillamente de otro lado."""
    partes = (data or "").split(":", 2)
    if len(partes) != 3 or partes[0] != CALLBACK_PREFIJO or not partes[2]:
        return None
    return partes[1], partes[2]


def boton_marcar_leido(aviso_id: str) -> Boton:
    return Boton(ETIQUETA_MARCAR_LEIDO, callback_data(ACCION_LEIDO, aviso_id))


def boton_habilitar(aviso_id: str) -> Boton:
    return Boton(ETIQUETA_HABILITAR, callback_data(ACCION_HABILITAR, aviso_id))


def boton_confirmar_habilitar(aviso_id: str) -> Boton:
    return Boton(ETIQUETA_CONFIRMAR, callback_data(ACCION_CONFIRMAR_HABILITAR, aviso_id))


def boton_cancelar_habilitar(aviso_id: str) -> Boton:
    return Boton(ETIQUETA_CANCELAR, callback_data(ACCION_CANCELAR_HABILITAR, aviso_id))


def _botones_para(tipo: str, aviso_id: str) -> list[Boton]:
    """Qué botones lleva un aviso ya entregado, según su tipo (F, "Textos
    del alta con correo aprobados por el usuario", 2026-09-28): "envíos
    agotados" suma "Habilitar un nuevo intento"; el resto de los tipos --
    "falta configurar el envío" y "quiénes no dieron su correo" -- quedan
    informativos, sólo con "Marcar leído"."""
    if tipo == AC.TIPO_CORREO_LIMITE_AGOTADO:
        return [boton_habilitar(aviso_id), boton_marcar_leido(aviso_id)]
    return [boton_marcar_leido(aviso_id)]


def _botones_a_jsonb(botones: list[Boton] | None) -> str | None:
    if not botones:
        return None
    return json.dumps([{"etiqueta": b.etiqueta, "callback_data": b.callback_data}
                       for b in botones])


# ---------------------------------------------------------------------------
# Entrega -- el fan-out a TODOS los administradores alcanzables va en
# `admin_notice` (`despachador.despachar_avisos_admin`); una respuesta
# puntual a UN administrador va en `admin_reply`
# (`despachador.despachar_respuestas_admin`) -- nunca la cola propia de este
# módulo que existía antes de esta unificación (decisión del usuario,
# 2026-09-28). Ver el comentario de tabla de `admin_reply`
# (`db/esquema.sql`) para el porqué de la tabla aparte: una respuesta
# puntual mezclada en `admin_notice` rompería la cuenta, sin filtrar, que ya
# hacían las pruebas de T28 sobre esa tabla.
# ---------------------------------------------------------------------------


def _encolar_respuesta_admin(cur: psycopg.Cursor, *, chat_id: int, cuerpo: str,
                             dedupe_key: str,
                             aviso_administrativo_id: str | None = None,
                             botones: list[Boton] | None = None,
                             ahora: datetime | None = None) -> None:
    """Encola una respuesta puntual del bot de administración (confirmación
    de un botón, guía de texto libre, aviso neutral de la red de contención)
    en `admin_reply`. Inserción directa, sin función `security definer`:
    quien llama ya sabe exactamente a qué chat responder -- esto corre bajo
    `prisma_admin`, que tiene `insert` directo sobre `admin_reply`
    (migración 0100).

    `aviso_administrativo_id` sólo se pasa cuando quien llama ya confirmó que
    la fila existe todavía (la referencia lleva `on delete cascade`, así que
    un id que ya no existe rompería el insert) -- `None` para una respuesta
    que no cita ningún aviso en particular (texto libre) o cuyo aviso no se
    pudo confirmar."""
    cur.execute(
        """insert into admin_reply
             (aviso_administrativo_id, chat_id, cuerpo, botones, dedupe_key,
              programado_para)
           values (%s, %s, %s, %s, %s, %s)
           on conflict (dedupe_key) do nothing""",
        (aviso_administrativo_id, chat_id, cuerpo, _botones_a_jsonb(botones),
         dedupe_key, _ahora(ahora)))


def _texto_aviso(workspace_nombre: str, texto_saneado: str) -> str:
    """F ("Textos del alta con correo aprobados por el usuario",
    2026-09-28): encabezado unificado "🛠️ Administración · {equipo}" seguido
    del texto propio de cada aviso -- ej. "{nombre} agotó los 5 envíos del
    correo de verificación."."""
    return f"🛠️ Administración · {workspace_nombre}\n{texto_saneado}"


def avisar_aviso_administrativo(cur: psycopg.Cursor, aviso_id: str, *,
                                ahora: datetime | None = None) -> list[str]:
    """Fan-out de UN aviso administrativo a cada administrador de plataforma
    alcanzable (`avisar_aviso_administrativo_admin`, `security definer`,
    migración 0100) -- mismo patrón que `incidentes.avisar_incidente_admin`.
    Un aviso ya resuelto, o que ya no existe, no encola nada -- resolverlo es
    justamente lo que hace que deje de reconciliarse
    (`reconciliar_avisos_admin_notice`).

    Devuelve el `app_user_id` de cada administrador al que recién se le
    encoló un aviso NUEVO (el `security definer` ya deduplica por
    `(aviso, administrador)`)."""
    ahora = _ahora(ahora)
    aviso = _cargar_aviso(cur, aviso_id)
    if aviso is None or aviso["resuelto_en"] is not None:
        return []

    cur.execute("select nombre from workspace where id = %s", (aviso["workspace_id"],))
    fila = cur.fetchone()
    workspace_nombre = fila["nombre"] if fila else "—"

    cuerpo = _texto_aviso(workspace_nombre, aviso["texto_saneado"])
    botones_json = _botones_a_jsonb(_botones_para(aviso["tipo"], aviso_id))

    cur.execute(
        "select app_user_id from avisar_aviso_administrativo_admin(%s, %s, %s, %s)",
        (aviso_id, aviso["workspace_id"], cuerpo, botones_json))
    return [str(f["app_user_id"]) for f in cur.fetchall()]


def reconciliar_avisos_admin_notice(cur: psycopg.Cursor, *,
                                    ahora: datetime | None = None) -> int:
    """Le da a cada administrador que se volvió alcanzable mientras tanto
    (le escribió al bot de administración por primera vez) cualquier aviso
    "🛠️ Administración" que siga sin resolver -- mismo papel que cumplía
    `_reconciliar_entregas` antes de esta unificación (decisión del usuario,
    2026-09-28), ahora sobre `admin_notice`: `avisar_aviso_administrativo`
    dedupea por `(aviso, administrador)`, así que correr esto en cada pasada
    del despacho nunca duplica nada, sea o no la primera vez que ve un aviso
    dado. La llama `ciclo.despachar_admin`, bajo el mismo `admin()` y antes
    de vaciar `admin_notice`, así el mismo lote de esta pasada ya incluye lo
    que se acaba de reconciliar.

    Devuelve cuántos avisos nuevos se encolaron en total (no cuántos avisos
    abiertos había)."""
    ahora = _ahora(ahora)
    cur.execute("select id from aviso_administrativo where resuelto_en is null")
    abiertos = [str(f["id"]) for f in cur.fetchall()]
    total = 0
    for aviso_id in abiertos:
        total += len(avisar_aviso_administrativo(cur, aviso_id, ahora=ahora))
    return total


# ---------------------------------------------------------------------------
# Acciones del webhook -- quien llama ya revalidó `identificar_administrador`
# ---------------------------------------------------------------------------


def marcar_leido_por_toque(cur: psycopg.Cursor, aviso_id: str, app_user_id: str,
                           chat_id: int, *, ahora: datetime | None = None) -> None:
    """"Marcar leído": marca el aviso (nunca resuelto) y encola la
    confirmación breve. Si el aviso ya no existe o ya estaba leído,
    `AC.marcar_leido` simplemente no toca nada (`where leido_en is null`) --
    de cualquier modo se confirma lo mismo, así quien tocó un botón viejo no
    ve una diferencia visible entre "ya estaba leído" y "lo acabás de
    marcar"."""
    ahora = _ahora(ahora)
    AC.marcar_leido(cur, aviso_id, app_user_id, ahora=ahora)
    aviso = _cargar_aviso(cur, aviso_id)
    _encolar_respuesta_admin(
        cur, chat_id=chat_id,
        cuerpo=TEXTO_MARCADO_LEIDO,
        aviso_administrativo_id=(aviso_id if aviso else None),
        dedupe_key=f"adm:leido:{aviso_id}:{app_user_id}", ahora=ahora)


def _cargar_aviso(cur: psycopg.Cursor, aviso_id: str, *,
                  bloquear: bool = False) -> dict | None:
    """`bloquear=True` toma el candado de la fila: dos administradores que
    confirman a la vez se serializan acá, y el segundo ve el aviso ya
    resuelto en vez de aplicar la acción otra vez."""
    cur.execute(
        f"""select id, workspace_id, tipo, texto_saneado, referencia_tipo,
                   referencia_id, resuelto_en
              from aviso_administrativo where id = %s
              {"for update" if bloquear else ""}""",
        (aviso_id,))
    return cur.fetchone()


class NoSePuedeAvisar(Exception):
    """La persona del aviso no se puede avisar (sin Telegram vinculado o sin
    un envío previo del que retomar la dirección): no se aplica nada."""


def _texto_preview_habilitar(nombre: str) -> str:
    return (f"¿Habilitar un nuevo intento de verificación de correo para "
            f"{nombre}? Le vuelvo a preguntar por su correo y este aviso "
            "queda resuelto.")


# G1d-b2, ítem 3 (revisión de G1d-b): resultado de comprobar si "Habilitar
# un nuevo intento" tiene sentido para el ciclo VIGENTE de la membresía --
# antes, ni la vista previa ni la confirmación miraban el ciclo en
# absoluto, así que las dos podían ofrecerse (o aplicarse) sobre una
# membresía que ya se verificó sola, cambió de correo, o fue revocada
# mientras el aviso seguía sin resolver.
_HABILITAR_APLICA = "aplica"
_HABILITAR_RESUELTO_SIN_ACCION = "resuelto_sin_accion"
_HABILITAR_NO_APLICA = "no_aplica"


def _estado_habilitable(cur: psycopg.Cursor, membership_id: str) -> str:
    """Un solo lugar para la comprobación de ciclo que usan la vista previa
    y la confirmación (ítem 7: nunca dos copias del mismo criterio).

    Devuelve `_HABILITAR_APLICA` sólo si el ciclo vigente sigue en
    `pending_email_verification` con el cupo de envíos realmente agotado
    (la misma cuenta que `emitir_verificacion_correo`: envíos posteriores
    al último `intento_habilitado` del ciclo, o todos si nunca hubo uno).

    `_HABILITAR_RESUELTO_SIN_ACCION` si la membresía ya está `active`: lo
    que motivaba el aviso ya no existe -- la persona se verificó sola --
    así que resolverlo es correcto y sin ningún efecto sobre ella (quien
    llama es responsable de marcarlo resuelto; esta función sólo lee).

    `_HABILITAR_NO_APLICA` para cualquier otro estado (`awaiting_email`,
    `pending_welcome`, `revoked`, sin ciclo) o si el cupo no está
    realmente agotado -- ahí NO se resuelve nada: el aviso queda tal cual
    estaba, para que alguien lo revise.

    Bajo `prisma_admin` (`admin(conn)`, `bypassrls`), las dos consultas de
    abajo leen `alta_correo_evento`/`alta_correo_verificacion` directo,
    sin declarar ningún espacio -- mismo privilegio que ya usa `AC.avisos`
    y el resto de este módulo (`grant all ... to prisma_admin`,
    `db/esquema.sql`); no hace falta ninguna función `security definer`
    nueva."""
    actual = AC.estado(cur, membership_id, bloquear=True)
    if actual is not None and actual["estado"] == "active":
        return _HABILITAR_RESUELTO_SIN_ACCION
    if actual is None or actual["estado"] != "pending_email_verification":
        return _HABILITAR_NO_APLICA
    cur.execute(
        """select max(at) as desde from alta_correo_evento
            where membership_id = %s and ciclo = %s and tipo = 'intento_habilitado'""",
        (membership_id, actual["ciclo"]))
    desde_habilitado = cur.fetchone()["desde"]
    cur.execute(
        """select count(*) as n from alta_correo_verificacion
            where membership_id = %s and ciclo = %s
              and (%s::timestamptz is null or emitido_en > %s)""",
        (membership_id, actual["ciclo"], desde_habilitado, desde_habilitado))
    if cur.fetchone()["n"] < 5:
        return _HABILITAR_NO_APLICA
    return _HABILITAR_APLICA


def mostrar_preview_habilitar(cur: psycopg.Cursor, aviso_id: str, chat_id: int,
                              admin_app_user_id: str, toque_id: str, *,
                              ahora: datetime | None = None) -> None:
    """Primer toque de "Habilitar un nuevo intento" (G1d-b, acción F): sólo
    muestra la vista previa con Confirmar/Cancelar -- todavía no aplica
    ningún intento nuevo. Un aviso inexistente, ya resuelto, de otro tipo o
    cuyo ciclo ya no corresponde (ítem 3) recibe una respuesta breve y
    ninguna acción nueva -- `TEXTO_HABILITAR_YA_RESUELTO` sólo cuando el
    aviso REALMENTE ya estaba resuelto (ítem 7): cualquier otro motivo usa
    `TEXTO_HABILITAR_CANCELADO`, cierto en los dos casos (nada se
    habilitó)."""
    ahora = _ahora(ahora)
    dedupe_key = f"adm:habilitar-preview:{aviso_id}:{admin_app_user_id}:{toque_id}"
    aviso = _cargar_aviso(cur, aviso_id)
    if (aviso is None or aviso["tipo"] != AC.TIPO_CORREO_LIMITE_AGOTADO
            or aviso["referencia_tipo"] != "membership"):
        _encolar_respuesta_admin(
            cur, chat_id=chat_id,
            cuerpo=TEXTO_HABILITAR_CANCELADO,
            aviso_administrativo_id=(aviso_id if aviso else None),
            dedupe_key=dedupe_key, ahora=ahora)
        return
    if aviso["resuelto_en"] is not None:
        _encolar_respuesta_admin(
            cur, chat_id=chat_id,
            cuerpo=TEXTO_HABILITAR_YA_RESUELTO, aviso_administrativo_id=aviso_id,
            dedupe_key=dedupe_key, ahora=ahora)
        return

    resultado = _estado_habilitable(cur, str(aviso["referencia_id"]))
    if resultado != _HABILITAR_APLICA:
        if resultado == _HABILITAR_RESUELTO_SIN_ACCION:
            AC.marcar_resuelto(cur, aviso_id, admin_app_user_id, ahora=ahora)
        _encolar_respuesta_admin(
            cur, chat_id=chat_id,
            cuerpo=TEXTO_HABILITAR_CANCELADO, aviso_administrativo_id=aviso_id,
            dedupe_key=dedupe_key, ahora=ahora)
        return

    cur.execute(
        """select u.nombre from membership m join app_user u on u.id = m.app_user_id
            where m.id = %s""", (aviso["referencia_id"],))
    fila = cur.fetchone()
    nombre = fila["nombre"] if fila else "esa persona"
    texto = _texto_preview_habilitar(nombre)
    _encolar_respuesta_admin(
        cur, chat_id=chat_id,
        cuerpo=texto, aviso_administrativo_id=aviso_id, dedupe_key=dedupe_key,
        ahora=ahora,
        botones=[boton_confirmar_habilitar(aviso_id), boton_cancelar_habilitar(aviso_id)])


def confirmar_habilitar(cur: psycopg.Cursor, aviso_id: str, admin_app_user_id: str, *,
                        ahora: datetime | None = None) -> str:
    """Aplica "Habilitar un nuevo intento": todo bajo la misma transacción
    que ya trae quien llama. Devuelve `RESULTADO_HABILITAR_APLICADO`,
    `RESULTADO_HABILITAR_YA_RESUELTO` (el aviso REALMENTE ya estaba
    resuelto -- doble tap, u otro administrador que confirmó primero: no
    se aplica una segunda vez ni se manda un segundo aviso a la persona) o
    `RESULTADO_HABILITAR_NO_APLICA` (ítem 3: el ciclo vigente ya no es
    `pending_email_verification` con el cupo agotado, o el aviso no existe
    o no es de este tipo -- si la membresía ya está `active`, el aviso se
    resuelve solo, sin ningún efecto sobre ella; para cualquier otro
    estado no se resuelve nada, el aviso queda tal cual estaba)."""
    from . import alta_correo_flujo as ACF
    from .autoridad import Canal, Solicitante

    ahora = _ahora(ahora)
    aviso = _cargar_aviso(cur, aviso_id, bloquear=True)
    if (aviso is None or aviso["tipo"] != AC.TIPO_CORREO_LIMITE_AGOTADO
            or aviso["referencia_tipo"] != "membership"):
        return RESULTADO_HABILITAR_NO_APLICA
    if aviso["resuelto_en"] is not None:
        return RESULTADO_HABILITAR_YA_RESUELTO

    workspace_id = str(aviso["workspace_id"])
    membership_id = str(aviso["referencia_id"])

    resultado = _estado_habilitable(cur, membership_id)
    if resultado != _HABILITAR_APLICA:
        if resultado == _HABILITAR_RESUELTO_SIN_ACCION:
            AC.marcar_resuelto(cur, aviso_id, admin_app_user_id, ahora=ahora)
        return RESULTADO_HABILITAR_NO_APLICA

    cur.execute(
        """select u.id as app_user_id, u.telegram_user_id, u.nombre
             from membership m join app_user u on u.id = m.app_user_id
            where m.id = %s""", (membership_id,))
    persona = cur.fetchone()

    # Primero se comprueba que a la persona le va a llegar el aviso; si no,
    # no se aplica nada ni se resuelve el aviso (nunca fallar en silencio:
    # el administrador no recibe "Listo, habilitado." si a la persona no le
    # va a llegar nada).
    if persona is None or not persona["telegram_user_id"]:
        raise NoSePuedeAvisar("sin cuenta de Telegram vinculada")
    vigente = AC.verificacion_vigente(cur, membership_id)
    if vigente is None:
        raise NoSePuedeAvisar("sin un envío previo del que retomar la dirección")

    # Recién ahora se declara el espacio (después de comprobar que se puede
    # avisar, así un incidente por no poder avisar queda como incidente de
    # plataforma, sin espacio). `alta_correo_evento`/`alta_correo_estado`
    # llevan RLS forzada y sus funciones de escritura corren
    # `security definer` como `prisma_owner`
    # (`nobypassrls`) -- sin este espacio declarado en la sesión, no
    # encontrarían nada, aunque `prisma_admin` (bypassrls) sí vea la fila
    # directamente. Mismo patrón que `gateway._activacion`.
    cur.execute("select set_config('prisma.workspace_id', %s, true)", (workspace_id,))

    AC.habilitar_intento(cur, membership_id, actor_app_user_id=admin_app_user_id, ahora=ahora)
    AC.marcar_resuelto(cur, aviso_id, admin_app_user_id, ahora=ahora)

    quien = Solicitante(
        app_user_id=str(persona["app_user_id"]), canal=Canal.ESPACIO,
        workspace_id=workspace_id, membership_id=membership_id, nombre=persona["nombre"])
    ACF.ofrecer_reintento_habilitado(
        cur, quien, workspace_id, persona["telegram_user_id"], ahora, vigente["email"])
    return RESULTADO_HABILITAR_APLICADO


def confirmar_habilitar_por_toque(cur: psycopg.Cursor, aviso_id: str, admin_app_user_id: str,
                                  chat_id: int, toque_id: str, *,
                                  ahora: datetime | None = None) -> None:
    from .gateway import NOTICIA_NEUTRA_INCIDENTE
    from .incidentes import registrar_incidente

    ahora = _ahora(ahora)
    # `aviso_administrativo_id` en la respuesta sólo si la fila sigue
    # existiendo -- `confirmar_habilitar` puede devolver `NO_APLICA` tanto
    # porque el aviso no existe como por cualquier otro motivo, y esa
    # columna lleva `on delete cascade` (un id que ya no existe rompería el
    # insert de la respuesta).
    aviso_valido = _cargar_aviso(cur, aviso_id) is not None
    try:
        resultado = confirmar_habilitar(cur, aviso_id, admin_app_user_id, ahora=ahora)
    except NoSePuedeAvisar as e:
        # T28 unificado con G1d (decisión del usuario, 2026-09-28):
        # `incidentes.registrar_incidente` es el único punto de escritura en
        # `incident` -- nunca un insert a mano -- y ya arma su propio aviso a
        # la administración; acá sólo queda encolar la respuesta neutra para
        # quien tocó el botón.
        registrar_incidente(
            cur, None,
            "No se habilitó un nuevo intento de verificación de correo: "
            f"no se puede avisar a la persona ({e}).",
            severidad="alta", etapa="admin_habilitar_sin_aviso")
        _encolar_respuesta_admin(
            cur, chat_id=chat_id,
            cuerpo=NOTICIA_NEUTRA_INCIDENTE,
            aviso_administrativo_id=(aviso_id if aviso_valido else None),
            dedupe_key=f"adm:habilitar-sin-aviso:{aviso_id}:{admin_app_user_id}:{toque_id}",
            ahora=ahora)
        return
    texto = _TEXTOS_RESULTADO_HABILITAR[resultado]
    _encolar_respuesta_admin(
        cur, chat_id=chat_id,
        cuerpo=texto, aviso_administrativo_id=(aviso_id if aviso_valido else None),
        dedupe_key=f"adm:habilitar-confirmado:{aviso_id}:{admin_app_user_id}:{toque_id}",
        ahora=ahora)


def cancelar_habilitar_por_toque(cur: psycopg.Cursor, aviso_id: str, admin_app_user_id: str,
                                 chat_id: int, toque_id: str, *,
                                 ahora: datetime | None = None) -> None:
    """Cancelar no aplica nada -- ni siquiera revisa si el aviso sigue sin
    resolver: declinar una vista previa nunca es una acción que necesite
    idempotencia propia. La única comprobación de la fila acá es si el id
    sigue existiendo, para saber si la respuesta puede citarlo
    (`aviso_administrativo_id`, `on delete cascade`) -- nunca su estado.

    G1d-b2, ítem 6 (revisión de G1d-b): la clave de dedupe incluye el
    administrador y el toque (`callback_query.id` de Telegram) -- antes
    era sólo `aviso_id`, así que un segundo Cancelar sobre el MISMO aviso
    (otro administrador, o el mismo tras una vista previa nueva) se
    perdía en silencio contra `on conflict (dedupe_key) do nothing`: la
    fila ya existía con la respuesta del primero. `toque_id` sigue
    protegiendo contra una redelivery exacta del mismo webhook (Telegram
    reenvía el mismo `callback_query.id`), que sí tiene que deduplicarse a
    una sola respuesta."""
    ahora = _ahora(ahora)
    aviso_valido = _cargar_aviso(cur, aviso_id) is not None
    _encolar_respuesta_admin(
        cur, chat_id=chat_id,
        cuerpo=TEXTO_HABILITAR_CANCELADO,
        aviso_administrativo_id=(aviso_id if aviso_valido else None),
        dedupe_key=f"adm:habilitar-cancelado:{aviso_id}:{admin_app_user_id}:{toque_id}",
        ahora=ahora)


def responder_texto_libre(cur: psycopg.Cursor, chat_id: int, mensaje_id: int | None,
                          *, ahora: datetime | None = None) -> None:
    """Cualquier texto libre en el bot de administración nunca concede una
    acción -- decisión del usuario, "Decisiones del usuario para G1": sólo
    una respuesta breve que remite a los botones del aviso o al panel."""
    ahora = _ahora(ahora)
    _encolar_respuesta_admin(
        cur, chat_id=chat_id,
        cuerpo=TEXTO_ACCION_LIBRE,
        dedupe_key=f"adm:libre:{chat_id}:{mensaje_id}", ahora=ahora)
