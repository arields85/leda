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

from datetime import datetime, timedelta, timezone

import psycopg

from . import alta_correo as AC
from .config import config
from .db import admin
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


# Una sola definición de "administrador de plataforma con Telegram
# vinculado" (G1d-a3, ítem 3): antes, `_admins_con_telegram` (despachar) y
# `_reconciliar_entregas` repetían cada una su propio filtro en SQL -- los
# dos coincidían hoy, pero nada impedía que se separaran con el tiempo (un
# administrador sin Telegram contando como disponible para uno de los dos
# caminos y no para el otro). Las dos funciones de abajo ejecutan
# textualmente esta misma subconsulta, nunca una copia editada a mano.
_ADMINS_CON_TELEGRAM_SQL = """select u.id as app_user_id, u.telegram_user_id
                                from app_user u
                                join platform_role p on p.app_user_id = u.id
                               where p.rol = 'administrador'
                                 and u.telegram_user_id is not null"""


def _admins_con_telegram(cur: psycopg.Cursor) -> list[dict]:
    cur.execute(_ADMINS_CON_TELEGRAM_SQL)
    return cur.fetchall()


def _reconciliar_entregas(cur: psycopg.Cursor, ahora: datetime) -> int:
    """Una fila de entrega por (aviso no resuelto, administrador con
    Telegram) que todavía no la tiene -- una sola sentencia de conjunto
    (`insert ... select ... on conflict do nothing`), no un `insert` por
    combinación en Python (G1d-a2, ítem 3): así no recorre toda la
    historia de avisos, incluidos los ya resueltos, en cada vuelta del
    loop -- el universo que importa acotarse es "lo que todavía está
    abierto", no "todo lo que existió alguna vez". Leído no es resuelto
    (`aviso_administrativo`, comentario de tabla): un administrador nuevo
    sigue recibiendo cualquier aviso todavía abierto, lo haya leído ya
    otro administrador o no, sin importar cuánto tiempo lleve abierto.
    Correr esto muchas veces (cada vuelta del loop) nunca duplica nada: el
    índice único (`aviso_administrativo_entrega_unica`) es la garantía
    bajo carrera, no el orden en que Python lo ejecute.

    `cross join (_ADMINS_CON_TELEGRAM_SQL)` (G1d-a3, ítem 3): la misma
    subconsulta que usa `_admins_con_telegram`, nunca un filtro propio --
    un administrador sin Telegram no cuenta como disponible acá tampoco."""
    cur.execute(
        f"""insert into aviso_administrativo_entrega
             (workspace_id, aviso_id, app_user_id, estado, creado_en)
           select a.workspace_id, a.id, admins.app_user_id, 'listo', %s
             from aviso_administrativo a
            cross join ({_ADMINS_CON_TELEGRAM_SQL}) as admins
            where a.resuelto_en is null
           on conflict (aviso_id, app_user_id) do nothing""",
        (ahora,))
    return cur.rowcount


def _incidente_plataforma(cur: psycopg.Cursor, resumen: str, *,
                          ahora: datetime | None = None,
                          referencia_cruda: str | None = None) -> None:
    """Incidente sin espacio propio -- concierne a la plataforma entera, no
    a uno en particular (mismo patrón que otras filas globales de
    `incident`, `workspace_id` en `null`).

    `referencia_cruda` es el detalle diagnóstico opcional (p. ej. el texto
    de una excepción, truncado) -- nunca entra en `resumen_sanitizado`, que
    es la clave exacta de deduplicación de `_incidente_plataforma_
    persistente` (G1d-a3, ítem 2/5): dos ocurrencias de la MISMA condición
    con un detalle distinto (un timeout con otro mensaje de red, por
    ejemplo) tienen que seguir deduplicando entre sí."""
    cur.execute(
        """insert into incident
             (workspace_id, severidad, resumen_sanitizado, referencia_cruda, at)
           values (null, 'alta', %s, %s, %s)""",
        (resumen, referencia_cruda, _ahora(ahora)))


VENTANA_DEDUPE_INCIDENTE_PLATAFORMA = timedelta(hours=24)


def _incidente_plataforma_persistente(cur: psycopg.Cursor, resumen: str,
                                      ahora: datetime, *,
                                      referencia_cruda: str | None = None) -> None:
    """Como `_incidente_plataforma`, pero deduplicado por causa exacta
    (`resumen`) mientras el anterior siga vigente. Tres causas la usan hoy:
    "falta el token" y "no hay ningún administrador vinculado" (condiciones
    de configuración que persisten mientras nadie las resuelve, evaluadas en
    cada `despachar_avisos`/`despachar_respuestas`) y, desde G1d-a3, ítem 2,
    cualquier excepción no manejada dentro de `despachar_todo` en sí (vía
    `reportar_fallo_despacho`, llamada desde la contención de
    `local.Escucha.tareas_de_fondo` y `cli.py despachar`) -- sin este
    guardia, cada vuelta del loop que despacha dejaría un incidente nuevo,
    en vez de uno solo hasta que se corrija. Distinto de los incidentes de
    `_fallo` por fila agotada: esos sí son uno por fila, igual que ya hace
    `despachador._fallo`.

    `incident` no tiene ningún estado de "resuelto" (sólo `at` y
    `notificado_en`, `db/esquema.sql`) -- G1d-a2, ítem 4: en vez de eso, se
    usa una ventana de tiempo (`VENTANA_DEDUPE_INCIDENTE_PLATAFORMA`, 24
    horas, documentada acá porque es una aproximación, no una fecha de
    resolución real): dentro de la ventana, un incidente reciente con la
    misma causa exacta alcanza; pasada la ventana, si el problema sigue (o
    volvió después de haberse arreglado), se registra uno nuevo -- nunca
    fallar en silencio dejando que la condición persista sin ningún rastro
    nuevo.

    El candado transaccional por causa exacta (`pg_advisory_xact_lock`)
    serializa dos vueltas del loop que evalúan la MISMA causa casi al
    mismo tiempo: sin él, las dos pueden ver "no hay ninguno reciente"
    antes de que ninguna inserte, y duplicar el incidente -- el `select`
    de abajo no es, por sí solo, una garantía bajo carrera. La clave del
    candado lleva un prefijo namespaced (G1d-a3, ítem 5) -- antes usaba
    `hashtext(resumen)` a secas, en el mismo espacio de claves de 64 bits
    que `hashtextextended(texto, 0)` (son la misma función para semilla 0),
    así que un `resumen` que por coincidencia fuera igual a la clave de
    otro candado de este mismo espacio (`bloquear_alta_correo_estado`,
    `cli._correo_verificacion`) los haría chocar entre sí. El prefijo
    (`"incidente-plataforma:"`) evita esa colisión sin cambiar la
    deduplicación misma, que sigue siendo por `resumen` exacto."""
    cur.execute("select pg_advisory_xact_lock(hashtextextended(%s, 0))",
               (f"incidente-plataforma:{resumen}",))
    cur.execute(
        """select 1 from incident
            where workspace_id is null and resumen_sanitizado = %s
              and at >= %s
            limit 1""",
        (resumen, ahora - VENTANA_DEDUPE_INCIDENTE_PLATAFORMA))
    if cur.fetchone() is None:
        _incidente_plataforma(cur, resumen, ahora=ahora,
                              referencia_cruda=referencia_cruda)


def reportar_fallo_despacho(conn: psycopg.Connection, error: Exception, etapa: str,
                            *, ahora: datetime | None = None) -> None:
    """Incidente de la contención alrededor de `despachar_todo` (G1d-a3,
    ítem 2), llamado desde `local.Escucha.tareas_de_fondo` y `cli.py
    despachar` cuando esa llamada revienta -- ninguno de los dos puede
    reusar la conexión de `espacio()`/`admin()` que ya se cerró sola al
    salir por la excepción, así que abre la suya propia acá.

    Deduplicado con la misma ventana que un incidente de plataforma
    persistente (`_incidente_plataforma_persistente`), por etapa + tipo de
    error -- nunca el mensaje crudo de la excepción, que puede variar entre
    pasadas de la misma condición (el mismo timeout con un detalle de red
    distinto cada vez, por ejemplo) y rompería la deduplicación por
    igualdad exacta de `resumen_sanitizado`. Antes, la contención llamaba
    directamente a `gateway._reportar_incidente_admin`, que inserta sin
    deduplicar: mientras el error persistiera, cada vuelta del loop de
    despacho dejaba un incidente nuevo."""
    ahora = _ahora(ahora)
    resumen = f"Excepción no manejada en '{etapa}' ({type(error).__name__})."
    try:
        with admin(conn) as cur:
            _incidente_plataforma_persistente(
                cur, resumen, ahora, referencia_cruda=str(error)[:2000])
    except Exception:  # noqa: BLE001 -- ni el incidente se pudo registrar
        try:
            conn.rollback()
        except Exception:  # noqa: BLE001
            pass


def _texto_aviso(workspace_nombre: str, texto_saneado: str) -> str:
    return f"🛠️ Administración\n\n{workspace_nombre}\n{texto_saneado}"


def _retraso_reintento(intentos: int) -> timedelta:
    """Espera creciente real antes del próximo intento (G1d-a2, ítem 2): 1,
    2, 4, 8 minutos según cuántos intentos ya se gastaron. A diferencia de
    `despachador._fallo` -- que reprograma para la próxima ventana de
    horario laboral, porque ahí "reintentar" significa "esperar a que
    alguien esté despierto" -- acá no hay calendario (el bot de
    administración manda en cualquier momento): lo que se toma prestado de
    `despachador._fallo` es la idea, no la fórmula -- una marca de "próximo
    intento" que el despacho respeta, en vez de reintentar en cada vuelta
    del loop."""
    return timedelta(minutes=2 ** (intentos - 1))


def _fallo(cur: psycopg.Cursor, tabla: str, fila_id: str, intentos_previos: int,
           error: Exception, ahora: datetime, *, incidente: str) -> None:
    """Reintenta hasta `MAX_INTENTOS`, con una espera creciente real entre
    intentos (`_retraso_reintento`) en vez de en cada vuelta del loop;
    agotados los intentos, la fila queda `fallido` y deja un incidente
    saneado -- nunca el texto del aviso ni un cuerpo de conversación.

    `resumen['fallidos']` (de quien llama) cuenta cada intento que falló en
    esta pasada, sea o no el definitivo -- no sólo las filas que terminaron
    `fallido` (G1d-a2, ítem 2: antes, esta función devolvía si la falla
    había sido definitiva, pero ningún llamador usaba ese valor -- un
    retorno muerto que además insinuaba, al revés de la realidad, que
    `fallidos` sólo contaba fallas definitivas)."""
    intentos = intentos_previos + 1
    definitiva = intentos >= MAX_INTENTOS
    estado = "fallido" if definitiva else "listo"
    proximo = None if definitiva else ahora + _retraso_reintento(intentos)
    cur.execute(
        f"""update {tabla}
              set intentos = %s, ultimo_error = %s, estado = %s,
                  proximo_intento_en = %s
            where id = %s""",
        (intentos, str(error)[:500], estado, proximo, fila_id))
    if definitiva:
        _incidente_plataforma(cur, incidente, ahora=ahora)


def despachar_avisos(cur: psycopg.Cursor, transporte: Transporte | None, *,
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
    resumen["reconciliados"] = _reconciliar_entregas(cur, ahora)

    if not admins:
        cur.execute("select count(*) n from aviso_administrativo")
        if cur.fetchone()["n"] > 0:
            _incidente_plataforma_persistente(
                cur, "Hay avisos administrativos sin ningún administrador "
                "de plataforma con Telegram vinculado.", ahora)
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
            "entregar avisos pendientes.", ahora)
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
              and (e.proximo_intento_en is null or e.proximo_intento_en <= %s)
            order by e.creado_en
            limit %s
            for update of e skip locked""",
        (ahora, lote))
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


def despachar_respuestas(cur: psycopg.Cursor, transporte: Transporte | None, *,
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
            "entregar respuestas pendientes.", ahora)
        return resumen

    if transporte is None:
        transporte = TransporteTelegram(token)

    cur.execute(
        """select id, chat_id, texto, intentos from aviso_administrativo_respuesta
            where estado = 'listo'
              and (proximo_intento_en is null or proximo_intento_en <= %s)
            order by creado_en
            limit %s
            for update skip locked""",
        (ahora, lote))
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
