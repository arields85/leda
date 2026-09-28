"""Entrega de avisos "🛠️ Administración" por el bot de administración (G1d).

`message_outbox` exige `workspace_id` y se despacha por el bot de CADA
espacio (`despachador.despachar`); el bot de administración es uno solo
para toda la plataforma, así que necesita su propio camino de salida --
reusar `message_outbox` mandaría el aviso por el bot equivocado
(`aviso_administrativo_entrega`, `aviso_administrativo_respuesta`, ver sus
comentarios de tabla en `db/esquema.sql`).

Este módulo no valida autoridad: eso lo hace quien llama (`gateway.py`),
revalidando `platform_role administrador` en el momento del toque -- acá
sólo se asume ya identificado ("el canal manda", `autoridad.py`).
"""

from __future__ import annotations

from datetime import datetime, timezone

import psycopg

from . import alta_correo as AC
from .config import config
from .despachador import MAX_INTENTOS, Boton, Transporte, TransporteTelegram

CALLBACK_PREFIJO = "adm"
ACCION_LEIDO = "leido"
ETIQUETA_MARCAR_LEIDO = "Marcar leído"

TEXTO_ACCION_LIBRE = (
    "Las acciones de administración se hacen desde los botones de cada "
    "aviso, o desde el panel de plataforma. Un mensaje de texto acá no "
    "hace nada.")
TEXTO_MARCADO_LEIDO = "Marcado como leído."


def _ahora(valor: datetime | None) -> datetime:
    return valor or datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Botones -- prefijo genérico, para que agregar otra acción después (p. ej.
# Reenviar/Cambiar correo, fuera de alcance de G1d) sea sumar un valor a
# `ACCION_*`, nunca un esquema de callback nuevo.
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
    encolar_respuesta(
        cur, chat_id, TEXTO_MARCADO_LEIDO,
        dedupe_key=f"adm:leido:{aviso_id}:{app_user_id}", ahora=ahora)


def responder_texto_libre(cur: psycopg.Cursor, chat_id: int, mensaje_id: int | None,
                          *, ahora: datetime | None = None) -> None:
    """Cualquier texto libre en el bot de administración nunca concede una
    acción -- decisión del usuario, "Decisiones del usuario para G1": sólo
    una respuesta breve que remite a los botones del aviso o al panel."""
    ahora = _ahora(ahora)
    encolar_respuesta(
        cur, chat_id, TEXTO_ACCION_LIBRE,
        dedupe_key=f"adm:libre:{chat_id}:{mensaje_id}", ahora=ahora)


def encolar_respuesta(cur: psycopg.Cursor, chat_id: int, texto: str, *,
                      dedupe_key: str, ahora: datetime | None = None) -> None:
    cur.execute(
        """insert into aviso_administrativo_respuesta
             (chat_id, texto, dedupe_key, creado_en)
           values (%s, %s, %s, %s)
           on conflict (dedupe_key) do nothing""",
        (chat_id, texto, dedupe_key, _ahora(ahora)))


# ---------------------------------------------------------------------------
# Despacho -- "el mismo loop que despacha la cola" (local.py, cli.py)
# ---------------------------------------------------------------------------


def _admins_con_telegram(cur: psycopg.Cursor) -> list[dict]:
    cur.execute(
        """select u.id as app_user_id, u.telegram_user_id from app_user u
             join platform_role p on p.app_user_id = u.id
            where p.rol = 'administrador' and u.telegram_user_id is not null""")
    return cur.fetchall()


def _reconciliar_entregas(cur: psycopg.Cursor, ahora: datetime,
                          admins: list[dict]) -> int:
    """Una fila de entrega por (aviso, administrador) que todavía no la
    tiene -- insertar-o-nada (`on conflict do nothing`), así correr esto
    muchas veces (cada vuelta del loop) nunca duplica nada ni pisa una
    entrega que ya estaba en curso."""
    if not admins:
        return 0
    cur.execute("select id, workspace_id from aviso_administrativo")
    avisos = cur.fetchall()
    creadas = 0
    for aviso in avisos:
        for adm in admins:
            cur.execute(
                """insert into aviso_administrativo_entrega
                     (workspace_id, aviso_id, app_user_id, estado, creado_en)
                   values (%s, %s, %s, 'listo', %s)
                   on conflict (aviso_id, app_user_id) do nothing""",
                (aviso["workspace_id"], aviso["id"], adm["app_user_id"], ahora))
            creadas += cur.rowcount
    return creadas


def _incidente_plataforma(cur: psycopg.Cursor, resumen: str) -> None:
    """Incidente sin espacio propio -- concierne a la plataforma entera, no
    a uno en particular (mismo patrón que otras filas globales de
    `incident`, `workspace_id` en `null`)."""
    cur.execute(
        """insert into incident (workspace_id, severidad, resumen_sanitizado)
           values (null, 'alta', %s)""",
        (resumen,))


def _incidente_plataforma_persistente(cur: psycopg.Cursor, resumen: str) -> None:
    """Como `_incidente_plataforma`, pero una sola vez por causa exacta:
    "falta el token" o "no hay ningún administrador vinculado" son
    condiciones de configuración que persisten mientras nadie las
    resuelve -- sin este guardia, cada vuelta del loop que despacha
    (`local.Escucha.tareas_de_fondo`, cada `cli.py despachar`) dejaría un
    incidente nuevo, en vez de uno solo hasta que se corrija. Distinto de
    los incidentes de `_fallo` por fila agotada: esos sí son uno por fila,
    igual que ya hace `despachador._fallo`."""
    cur.execute(
        """select 1 from incident
            where workspace_id is null and resumen_sanitizado = %s limit 1""",
        (resumen,))
    if cur.fetchone() is None:
        _incidente_plataforma(cur, resumen)


def _texto_aviso(workspace_nombre: str, texto_saneado: str) -> str:
    return f"🛠️ Administración\n\n{workspace_nombre}\n{texto_saneado}"


def _fallo(cur: psycopg.Cursor, tabla: str, fila_id: str, intentos_previos: int,
           error: Exception, ahora: datetime, *, incidente: str) -> bool:
    """Aplica el mismo backoff que `despachador._fallo`: reintenta hasta
    `MAX_INTENTOS`, después queda `fallido` y deja un incidente saneado --
    nunca el texto del aviso ni un cuerpo de conversación. Devuelve `True`
    si esta fue la falla definitiva (para que quien llama cuente bien)."""
    intentos = intentos_previos + 1
    definitiva = intentos >= MAX_INTENTOS
    estado = "fallido" if definitiva else "listo"
    cur.execute(
        f"""update {tabla}
              set intentos = %s, ultimo_error = %s, estado = %s
            where id = %s""",
        (intentos, str(error)[:500], estado, fila_id))
    if definitiva:
        _incidente_plataforma(cur, incidente)
    return definitiva


def despachar_avisos(cur: psycopg.Cursor, transporte: Transporte, *,
                     ahora: datetime | None = None, lote: int = 50) -> dict[str, int]:
    """Entrega los avisos "🛠️ Administración" pendientes a cada
    administrador con Telegram vinculado.

    Sin ningún administrador con Telegram vinculado, o sin el token del
    bot de administración: un solo incidente por causa (no uno por vuelta
    del loop mientras la condición siga sin resolverse) y se sigue sin
    reventar; los avisos quedan sin entregar hasta que alguna de las dos
    condiciones se resuelva."""
    ahora = _ahora(ahora)
    resumen = {"reconciliados": 0, "enviados": 0, "fallidos": 0}

    admins = _admins_con_telegram(cur)
    resumen["reconciliados"] = _reconciliar_entregas(cur, ahora, admins)

    if not admins:
        cur.execute("select count(*) n from aviso_administrativo")
        if cur.fetchone()["n"] > 0:
            _incidente_plataforma_persistente(
                cur, "Hay avisos administrativos sin ningún administrador "
                "de plataforma con Telegram vinculado.")
        return resumen

    cur.execute("select count(*) n from aviso_administrativo_entrega "
               "where estado = 'listo'")
    if cur.fetchone()["n"] == 0:
        return resumen

    try:
        token = config.token_bot("admin")
    except LookupError:
        _incidente_plataforma_persistente(
            cur, "Falta el token del bot de administración: no se pudieron "
            "entregar avisos pendientes.")
        return resumen

    if transporte is None:
        transporte = TransporteTelegram(token)

    cur.execute(
        """select e.id, e.aviso_id, e.intentos, u.telegram_user_id,
                  a.texto_saneado, w.nombre as workspace_nombre
             from aviso_administrativo_entrega e
             join app_user u on u.id = e.app_user_id
             join aviso_administrativo a on a.id = e.aviso_id
             join workspace w on w.id = a.workspace_id
            where e.estado = 'listo'
            order by e.creado_en
            limit %s
            for update of e skip locked""",
        (lote,))
    pendientes = cur.fetchall()

    for fila in pendientes:
        texto = _texto_aviso(fila["workspace_nombre"], fila["texto_saneado"])
        boton = boton_marcar_leido(str(fila["aviso_id"]))
        try:
            tg_id = transporte.enviar(fila["telegram_user_id"], texto, [boton])
        except Exception as e:  # noqa: BLE001 -- el error se registra, no se propaga
            _fallo(cur, "aviso_administrativo_entrega", fila["id"], fila["intentos"],
                  e, ahora,
                  incidente="Un aviso administrativo no se pudo entregar "
                            f"tras {MAX_INTENTOS} intentos.")
            resumen["fallidos"] += 1
            continue
        cur.execute(
            """update aviso_administrativo_entrega
                  set estado = 'enviado', delivered_at = %s, telegram_message_id = %s
                where id = %s""",
            (ahora, tg_id, fila["id"]))
        resumen["enviados"] += 1

    return resumen


def despachar_respuestas(cur: psycopg.Cursor, transporte: Transporte, *,
                         ahora: datetime | None = None, lote: int = 50) -> dict[str, int]:
    """Entrega las respuestas puntuales en cola (confirmaciones, guía de
    texto libre). Mismo patrón de reintentos que `despachar_avisos`."""
    ahora = _ahora(ahora)
    resumen = {"enviados": 0, "fallidos": 0}

    cur.execute("select count(*) n from aviso_administrativo_respuesta "
               "where estado = 'listo'")
    if cur.fetchone()["n"] == 0:
        return resumen

    try:
        token = config.token_bot("admin")
    except LookupError:
        _incidente_plataforma_persistente(
            cur, "Falta el token del bot de administración: no se pudieron "
            "entregar respuestas pendientes.")
        return resumen

    if transporte is None:
        transporte = TransporteTelegram(token)

    cur.execute(
        """select id, chat_id, texto, intentos from aviso_administrativo_respuesta
            where estado = 'listo'
            order by creado_en
            limit %s
            for update skip locked""",
        (lote,))
    pendientes = cur.fetchall()

    for fila in pendientes:
        try:
            tg_id = transporte.enviar(fila["chat_id"], fila["texto"])
        except Exception as e:  # noqa: BLE001 -- el error se registra, no se propaga
            _fallo(cur, "aviso_administrativo_respuesta", fila["id"], fila["intentos"],
                  e, ahora,
                  incidente="Una respuesta del bot de administración no se pudo "
                            f"entregar tras {MAX_INTENTOS} intentos.")
            resumen["fallidos"] += 1
            continue
        cur.execute(
            """update aviso_administrativo_respuesta
                  set estado = 'enviado', enviado_en = %s, telegram_message_id = %s
                where id = %s""",
            (ahora, tg_id, fila["id"]))
        resumen["enviados"] += 1

    return resumen


def despachar_todo(cur: psycopg.Cursor, transporte: Transporte | None = None, *,
                   ahora: datetime | None = None, lote: int = 50) -> dict[str, dict]:
    """Punto de entrada único para el loop que ya despacha `message_outbox`
    (`local.py`, `cli.py`): un solo lugar que hookear, en vez de dos.

    `transporte=None` resuelve el token real del bot de administración y
    construye un `TransporteTelegram` -- las pruebas pasan un doble
    (`despachador.TransporteDePrueba`) explícito."""
    ahora = _ahora(ahora)
    return {
        "avisos": despachar_avisos(cur, transporte, ahora=ahora, lote=lote),
        "respuestas": despachar_respuestas(cur, transporte, ahora=ahora, lote=lote),
    }
