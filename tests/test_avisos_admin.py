"""Aviso de cada incidente a la administración de plataforma (T28,
Constitución §10, decisión del usuario 2026-09-28, corregida el mismo día).

`incidentes.registrar_incidente` es el punto único de escritura en
`incident`; estas pruebas cubren el fan-out a cada administrador alcanzable
(`admin_notice`), que el aviso SÍ incluye qué lo disparó (Constitución §2:
el administrador ya accede a las conversaciones privadas) pero nunca un
secreto de la aplicación, el `audit_log` que deja cada aviso (§12), el caso
sin espacio (incidente global), que no avisarle a nadie no rompe nada, el
dedupe al reprocesar, y que el despachador entrega el aviso por el bot de
administración -- en la corrida directa y dentro del mismo ciclo que hoy usa
el modo local (`local.Escucha.tareas_de_fondo`).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import httpx

from leda import despachador, incidentes
from leda.db import admin, registrar_auditoria
from leda.despachador import (BACKOFF_MINUTOS_AVISO_ADMIN, MAX_INTENTOS,
                                TransporteDePrueba, despachar_avisos_admin)

# Token de bot falso, sólo para probar que un error de Telegram no lo
# filtra -- nunca se compara contra `os.environ` (regla de seguridad del
# proyecto, ya establecida más abajo en este archivo: comparación por
# booleano, nunca `assert ... not in os.environ`).
TOKEN_FALSO = "123456789:AAAA-SECRETO-DE-PRUEBA-FALSO"


class _ClienteTelegramQueFalla:
    """Doble de `httpx.Client` para `TransporteTelegram`: cualquier pedido
    responde un error real de httpx (401 por default), con el mismo cuerpo
    JSON que manda Telegram, para probar la traducción de R1-001 sin pegarle
    nunca a la API real."""

    def __init__(self, status_code: int = 401,
                descripcion: str | None = "Unauthorized") -> None:
        self.status_code = status_code
        self.descripcion = descripcion

    def post(self, url, json=None):
        pedido = httpx.Request("POST", url)
        cuerpo = {"ok": False, "error_code": self.status_code}
        if self.descripcion:
            cuerpo["description"] = self.descripcion
        raise httpx.HTTPStatusError(
            "fallo", request=pedido,
            response=httpx.Response(self.status_code, request=pedido, json=cuerpo))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _administrador(cur, nombre: str, telegram_id: int, *,
                   chat_id: int | None = None) -> str:
    """Da de alta un administrador de plataforma. Con `chat_id`, además lo
    deja "vinculado" -- como si ya le hubiera escrito al bot de
    administración (`gateway.procesar_update`, canal ADMINISTRACION,
    `accion='mensaje_admin'`), que es lo que `avisar_incidente_admin` exige
    para poder mandarle algo (Telegram no deja que un bot le escriba primero
    a quien nunca le escribió)."""
    cur.execute(
        "insert into app_user (telegram_user_id, nombre) values (%s, %s) returning id",
        (telegram_id, nombre))
    app_user_id = str(cur.fetchone()["id"])
    cur.execute(
        "insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
        (app_user_id,))
    if chat_id is not None:
        registrar_auditoria(
            cur, accion="mensaje_admin", actor_app_user_id=app_user_id,
            actor_kind="persona", detalle={"chat_id": chat_id})
    return app_user_id


# ---------------------------------------------------------------------------
# R1-001 (revisión 2026-09-28): segunda capa de defensa -- `redactar_secreto_
# telegram` oculta un token de bot que haya llegado sin traducir hasta
# `referencia_cruda`, sin tocar ningún otro secreto (p. ej. la cadena de
# conexión de arriba, que el diseño SÍ deja en `referencia_cruda` a
# propósito -- ver el test anterior).
# ---------------------------------------------------------------------------

def test_redactar_secreto_telegram_oculta_la_url_completa():
    from leda.incidentes import redactar_secreto_telegram

    texto = (f"Client error '401 Unauthorized' for url "
            f"'https://api.telegram.org/bot{TOKEN_FALSO}/sendMessage'")
    redactado = redactar_secreto_telegram(texto)

    filtra = TOKEN_FALSO in redactado
    assert not filtra, "la redacción no ocultó la URL completa"
    assert "bot<oculto>" in redactado


def test_redactar_secreto_telegram_oculta_el_token_suelto():
    from leda.incidentes import redactar_secreto_telegram

    texto = f"token filtrado en un log: bot{TOKEN_FALSO}"
    redactado = redactar_secreto_telegram(texto)

    filtra = TOKEN_FALSO in redactado
    assert not filtra, "la redacción no ocultó el token suelto"
    assert "bot<oculto>" in redactado


def test_redactar_secreto_telegram_no_toca_texto_sin_token():
    from leda.incidentes import redactar_secreto_telegram

    texto = "Un mensaje no se pudo entregar tras 5 intentos."
    assert redactar_secreto_telegram(texto) == texto


def test_redactar_secreto_telegram_no_toca_otros_secretos():
    """Sólo el patrón de Telegram -- la cadena de conexión de arriba sigue
    intacta en `referencia_cruda`: es el diseño del test anterior, no un
    olvido de esta redacción."""
    from leda.incidentes import redactar_secreto_telegram

    texto = "no se pudo conectar: postgresql://leda_app:s3cr3t-p4ss@db.interno:5432/leda"
    assert redactar_secreto_telegram(texto) == texto


def test_redactar_secreto_telegram_pasa_none_y_vacio_sin_cambios():
    from leda.incidentes import redactar_secreto_telegram

    assert redactar_secreto_telegram(None) is None
    assert redactar_secreto_telegram("") == ""


def test_registrar_incidente_redacta_referencia_cruda(conn, corework):
    """Segunda capa de defensa: aunque algo aguas arriba se olvide de
    traducir un error de Telegram antes de llamar a `registrar_incidente`,
    el token no llega a `incident.referencia_cruda`."""
    ws = corework.workspace_id
    referencia_con_token = (
        f"HTTPStatusError: Client error for url "
        f"'https://api.telegram.org/bot{TOKEN_FALSO}/sendMessage'")

    with admin(conn) as cur:
        incident_id = incidentes.registrar_incidente(
            cur, ws, "Falló algo en una prueba.", etapa="prueba_directa",
            referencia_cruda=referencia_con_token, avisar_admin=False)
        cur.execute("select referencia_cruda from incident where id = %s",
                    (incident_id,))
        fila = cur.fetchone()
    conn.commit()

    filtra = TOKEN_FALSO in (fila["referencia_cruda"] or "")
    assert not filtra, "registrar_incidente guarda el token del bot"
    assert "bot<oculto>" in fila["referencia_cruda"]


def test_ningun_administrador_alcanzable_no_rompe_y_queda_anotado(conn, corework):
    """Si nadie tiene el bot de administración vinculado, el incidente se
    registra igual, sin `notificado_admin_en`, y sin fingir que se avisó a
    nadie (mismo criterio que ya rige para `notificado_en` de la persona)."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        incident_id = incidentes.registrar_incidente(
            cur, ws, "Falló algo en una prueba.", severidad="media",
            etapa="prueba_directa")
        cur.execute(
            """select notificado_admin_en, resumen_sanitizado from incident
                where id = %s""", (incident_id,))
        fila = cur.fetchone()
        cur.execute(
            "select count(*) n from admin_notice where incident_id = %s",
            (incident_id,))
        avisos = cur.fetchone()["n"]
    conn.commit()

    assert fila["notificado_admin_en"] is None
    assert avisos == 0
    assert "no se avisó a la administración" in fila["resumen_sanitizado"].lower()


# ---------------------------------------------------------------------------
# Incidente global (sin espacio) -- validador de invariantes futuro
# ---------------------------------------------------------------------------

def test_incidente_global_sin_espacio_encola_aviso_admin(conn):
    """`workspace_id=None` es un hecho de plataforma, sin cliente en
    particular (p. ej. lo que va a producir el validador de invariantes
    diario, `odd/tasks/validador-invariantes.md`). El aviso a la
    administración sigue funcionando -- el texto dice "global", no un slug."""
    with admin(conn) as cur:
        _administrador(cur, "Admin Global", 622001, chat_id=622001)
        incident_id = incidentes.registrar_incidente(
            cur, None, "Violación de invariante detectada.",
            severidad="alta", etapa="validador_invariantes")
        cur.execute(
            "select workspace_id, notificado_admin_en from incident where id = %s",
            (incident_id,))
        incidente = cur.fetchone()
        cur.execute(
            "select chat_id, cuerpo from admin_notice where incident_id = %s",
            (incident_id,))
        avisos = cur.fetchall()
    conn.commit()

    assert incidente["workspace_id"] is None
    assert incidente["notificado_admin_en"] is not None
    assert len(avisos) == 1
    assert avisos[0]["chat_id"] == 622001
    assert "global" in avisos[0]["cuerpo"]


# ---------------------------------------------------------------------------
# Dedupe
# ---------------------------------------------------------------------------

def test_reprocesar_el_mismo_incidente_no_duplica_el_aviso(conn, corework):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _administrador(cur, "Admin Repetido", 633001, chat_id=633001)
    conn.commit()

    incident_id = str(uuid.uuid4())
    with admin(conn) as cur:
        primero = incidentes.avisar_incidente_admin(
            cur, incident_id, workspace_id=ws, cuerpo="Incidente de prueba.")
        segundo = incidentes.avisar_incidente_admin(
            cur, incident_id, workspace_id=ws, cuerpo="Incidente de prueba.")
        cur.execute(
            "select count(*) n from admin_notice where incident_id = %s",
            (incident_id,))
        total = cur.fetchone()["n"]
    conn.commit()

    assert len(primero) == 1     # recién avisado
    assert primero[0]            # el app_user_id del administrador
    assert segundo == []         # ya estaba avisado: nada nuevo, ninguna fila para auditar de nuevo
    assert total == 1            # pero no se le duplicó el aviso


# ---------------------------------------------------------------------------
# Despacho: el bot de administración entrega de verdad
# ---------------------------------------------------------------------------

def test_despachar_avisos_admin_entrega_por_el_transporte_del_bot_de_administracion(
        conn, corework):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _administrador(cur, "Admin Despacho", 644001, chat_id=644001)
        incident_id = incidentes.registrar_incidente(
            cur, ws, "Falló algo en una prueba.", etapa="prueba_directa",
            severidad="media")
    conn.commit()

    transporte = TransporteDePrueba()
    with admin(conn) as cur:
        resumen = despachar_avisos_admin(cur, transporte, datetime.now(timezone.utc))
        cur.execute(
            "select estado, enviado_en from admin_notice where incident_id = %s",
            (incident_id,))
        fila = cur.fetchone()
    conn.commit()

    assert resumen == {"enviados": 1, "fallidos": 0, "agotados": 0,
                       "incidentes_sin_registrar": 0}
    assert len(transporte.enviados) == 1
    assert transporte.enviados[0].chat_id == 644001
    assert fila["estado"] == "enviado"
    assert fila["enviado_en"] is not None


def test_despachar_avisos_admin_reintenta_si_el_transporte_falla(conn, corework):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _administrador(cur, "Admin Fallido", 655001, chat_id=655001)
        incidentes.registrar_incidente(
            cur, ws, "Falló algo en una prueba.", etapa="prueba_directa")
    conn.commit()

    transporte = TransporteDePrueba(falla_en={655001})
    with admin(conn) as cur:
        resumen = despachar_avisos_admin(cur, transporte, datetime.now(timezone.utc))
        cur.execute("select estado, intentos, ultimo_error from admin_notice limit 1")
        fila = cur.fetchone()
    conn.commit()

    assert resumen == {"enviados": 0, "fallidos": 1, "agotados": 0,
                       "incidentes_sin_registrar": 0}
    assert fila["estado"] == "listo"          # menos de MAX_INTENTOS: reintenta
    assert fila["intentos"] == 1
    assert fila["ultimo_error"]


def test_despachar_avisos_admin_pospone_con_backoff_creciente(conn, corework):
    """A: un aviso admin que falla no se reintenta de inmediato -- eso
    agotaría MAX_INTENTOS en un par de minutos frente a un blip de Telegram
    (el listener corre cada unos segundos). Cada intento fallido pospone
    `programado_para` con un backoff creciente
    (`despachador.BACKOFF_MINUTOS_AVISO_ADMIN`), así que con el mismo
    "ahora" una pasada inmediatamente posterior no lo vuelve a tomar."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _administrador(cur, "Admin Backoff", 656001, chat_id=656001)
        incidentes.registrar_incidente(
            cur, ws, "Falló algo en una prueba.", etapa="prueba_directa")
    conn.commit()

    transporte = TransporteDePrueba(falla_en={656001})
    ahora = datetime.now(timezone.utc)

    for minutos_esperados in BACKOFF_MINUTOS_AVISO_ADMIN:
        with admin(conn) as cur:
            resumen = despachar_avisos_admin(cur, transporte, ahora)
            cur.execute(
                "select programado_para, intentos, estado from admin_notice limit 1")
            fila = cur.fetchone()
        conn.commit()

        assert resumen["fallidos"] == 1
        assert fila["estado"] == "listo"
        assert fila["programado_para"] == ahora + timedelta(minutes=minutos_esperados)

        # Con el mismo "ahora", como en la pasada del listener unos segundos
        # después, el backoff lo protege: no se vuelve a tomar.
        with admin(conn) as cur:
            resumen_inmediato = despachar_avisos_admin(cur, transporte, ahora)
        conn.commit()
        assert resumen_inmediato == {"enviados": 0, "fallidos": 0, "agotados": 0,
                                     "incidentes_sin_registrar": 0}

        ahora = fila["programado_para"]  # simula que pasó el backoff


def test_despachar_avisos_admin_agotado_registra_incidente_sin_avisar_de_nuevo(
        conn, corework):
    """B: un aviso admin que agota MAX_INTENTOS no desaparece en silencio
    (regla del proyecto: "nunca fallar en silencio") -- deja un incidente de
    severidad alta apuntando a la fila `admin_notice` que se agotó.

    Guarda contra el loop: `registrar_incidente` siempre llama a
    `avisar_incidente_admin`, que encolaría un `admin_notice` NUEVO a cada
    administrador alcanzable por el mismo canal que justo falló -- ese aviso
    fallaría también, y encadenaría incidentes sin fin. Por eso este
    incidente se registra con `avisar_admin=False`: nunca deja
    `notificado_admin_en` puesto, y no se encola ningún `admin_notice`
    nuevo (`total_avisos` sigue en 1)."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _administrador(cur, "Admin Agotado", 658001, chat_id=658001)
        incidentes.registrar_incidente(
            cur, ws, "Falló algo en una prueba.", etapa="prueba_directa")
        cur.execute("select id from admin_notice limit 1")
        notice_id = cur.fetchone()["id"]
    conn.commit()

    transporte = TransporteDePrueba(falla_en={658001})
    ahora = datetime.now(timezone.utc)
    resumen = None
    fila = None
    for _ in range(MAX_INTENTOS):
        with admin(conn) as cur:
            resumen = despachar_avisos_admin(cur, transporte, ahora)
            cur.execute(
                """select estado, intentos, programado_para from admin_notice
                    where id = %s""", (notice_id,))
            fila = cur.fetchone()
        conn.commit()
        if fila["estado"] == "fallido":
            break
        ahora = fila["programado_para"]

    assert fila["estado"] == "fallido"
    assert fila["intentos"] == MAX_INTENTOS
    assert resumen["agotados"] == 1
    assert resumen["fallidos"] == 1
    assert resumen["incidentes_sin_registrar"] == 0  # el registro sí funcionó acá

    with admin(conn) as cur:
        cur.execute(
            """select id, workspace_id, severidad, resumen_sanitizado,
                      referencia_tipo, referencia_id, notificado_admin_en
                 from incident where referencia_id = %s""", (notice_id,))
        incidente = cur.fetchone()
        cur.execute("select count(*) n from admin_notice")
        total_avisos = cur.fetchone()["n"]
    conn.commit()

    assert incidente is not None
    assert str(incidente["workspace_id"]) == ws
    assert incidente["severidad"] == "alta"
    assert incidente["referencia_tipo"] == incidentes.REFERENCIA_ADMIN_NOTICE
    assert incidente["notificado_admin_en"] is None  # nunca se reenvía por el mismo canal
    assert "no se avisó a la administración" in incidente["resumen_sanitizado"].lower()
    assert total_avisos == 1  # el guard: NO se encoló un admin_notice nuevo


def test_despachar_avisos_admin_agotado_no_guarda_el_token_ni_en_ultimo_error_ni_en_incidente(
        conn, corework):
    """R1-001 (revisión 2026-09-28): `admin_notice.ultimo_error` e
    `incident.referencia_cruda` -- lo que deja un aviso admin que agota
    MAX_INTENTOS contra el transporte REAL de Telegram -- nunca llevan el
    token del bot. Antes, `TransporteTelegram.enviar` dejaba escapar el
    `HTTPStatusError` de httpx tal cual, y su `str()` lleva la URL completa
    con el token."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _administrador(cur, "Admin R1-001", 659001, chat_id=659001)
        incidentes.registrar_incidente(
            cur, ws, "Falló algo en una prueba.", etapa="prueba_directa")
        cur.execute("select id from admin_notice limit 1")
        notice_id = cur.fetchone()["id"]
    conn.commit()

    transporte = despachador.TransporteTelegram(
        TOKEN_FALSO, cliente=_ClienteTelegramQueFalla())
    ahora = datetime.now(timezone.utc)
    fila = None
    for _ in range(MAX_INTENTOS):
        with admin(conn) as cur:
            despachar_avisos_admin(cur, transporte, ahora)
            cur.execute(
                """select estado, ultimo_error, programado_para from admin_notice
                    where id = %s""", (notice_id,))
            fila = cur.fetchone()
        conn.commit()

        filtra = TOKEN_FALSO in (fila["ultimo_error"] or "")
        assert not filtra, "admin_notice.ultimo_error guarda el token del bot"
        if fila["estado"] == "fallido":
            break
        ahora = fila["programado_para"]

    assert fila["estado"] == "fallido"
    assert "401" in fila["ultimo_error"]

    with admin(conn) as cur:
        cur.execute(
            """select referencia_cruda from incident
                where referencia_tipo = %s and referencia_id = %s""",
            (incidentes.REFERENCIA_ADMIN_NOTICE, notice_id))
        incidente = cur.fetchone()
    conn.commit()

    assert incidente is not None
    filtra_incidente = TOKEN_FALSO in (incidente["referencia_cruda"] or "")
    assert not filtra_incidente, "incident.referencia_cruda guarda el token del bot"
    assert "401" in incidente["referencia_cruda"]


def test_despachar_avisos_admin_si_registrar_incidente_falla_no_pierde_el_lote(
        conn, corework, monkeypatch):
    """R3-002 (revisión de confiabilidad, 2026-09-28, aceptado): antes, si
    `registrar_incidente` (la propia escritura del incidente cuando un
    aviso agota MAX_INTENTOS) fallaba, la excepción salía de
    `despachar_avisos_admin` sin nada que la atajara -- la transacción del
    lote quedaba sin `commit`, así que quien llama (`local.tareas_de_fondo`)
    nunca confirmaba nada: un aviso YA entregado en el mismo lote volvía a
    'listo' en la base y Telegram lo recibía de nuevo, y el aviso agotado ni
    siquiera guardaba su intento actualizado.

    El registro del incidente corre ahora en un punto de retorno (mismo
    patrón que `agente._ejecutar_una`/`gateway._iniciar_alta_guiada`:
    `cur.connection.transaction(force_rollback=False)` como SAVEPOINT
    anidado dentro de la transacción abierta): si falla, sólo se deshace
    esa escritura -- el resto del lote, incluido el `update` que ya dejó el
    aviso agotado en 'fallido' con su intento al día, sigue en pie. Nunca en
    silencio (regla del proyecto): se cuenta en el resumen.

    R3-001 (revisión de confiabilidad, 2026-09-28): el `registrar_incidente`
    falso falla DENTRO de la base (`select 1/0`), no con una excepción de
    Python antes de tocar SQL -- así la prueba sólo pasa si el SAVEPOINT
    realmente aísla la falla. Con una excepción de Python la transacción
    de PostgreSQL ni se entera y esta prueba pasaría igual sin el
    SAVEPOINT; con un error de base real, sin el SAVEPOINT la transacción
    abierta queda abortada y el `update` que sigue (dejar el aviso agotado
    en 'fallido') también fallaría, sin nada que lo atajara."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        # Los dos administradores YA existen antes del único incidente que
        # se registra: `avisar_incidente_admin` fanea a cada administrador
        # alcanzable, sin filtrar por espacio -- si se creara el segundo
        # admin después de un primer `registrar_incidente`, un segundo
        # llamado volvería a avisarle también al primero (dedupe por
        # incidente + administrador, no por administrador solo) y el lote
        # quedaría con tres avisos en vez de dos.
        _administrador(cur, "Admin Lote Ok", 671001, chat_id=671001)
        _administrador(cur, "Admin Lote Agotado", 671002, chat_id=671002)
        incidentes.registrar_incidente(
            cur, ws, "Falló algo en una prueba (lote con dos avisos).",
            etapa="prueba_directa")
        cur.execute(
            "select id, chat_id from admin_notice where chat_id in (671001, 671002)")
        por_chat = {f["chat_id"]: f["id"] for f in cur.fetchall()}
        ok_id = por_chat[671001]
        agotado_id = por_chat[671002]
        # Ya viene con MAX_INTENTOS - 1: este intento lo agota.
        cur.execute("update admin_notice set intentos = %s where id = %s",
                    (MAX_INTENTOS - 1, agotado_id))
    conn.commit()

    transporte = TransporteDePrueba(falla_en={671002})

    def _registrar_incidente_falla_en_la_base(cur, *args, **kwargs):
        cur.execute("select 1/0")

    monkeypatch.setattr(
        despachador, "registrar_incidente", _registrar_incidente_falla_en_la_base)

    ahora = datetime.now(timezone.utc)
    with admin(conn) as cur:
        resumen = despachar_avisos_admin(cur, transporte, ahora)
        cur.execute(
            """select id, estado, intentos, ultimo_error from admin_notice
                where id in (%s, %s)""",
            (ok_id, agotado_id))
        filas = {f["id"]: f for f in cur.fetchall()}
    conn.commit()  # si el savepoint no aislara la falla, este commit no llegaría a correr

    assert resumen["enviados"] == 1
    assert resumen["agotados"] == 1
    assert resumen["incidentes_sin_registrar"] == 1

    # El aviso entregado bien en el mismo lote quedó 'enviado' -- no volvió
    # a 'listo' para que Telegram lo reciba dos veces.
    assert filas[ok_id]["estado"] == "enviado"
    # El agotado quedó 'fallido' con su intento actualizado, aunque el
    # incidente no se haya podido registrar.
    assert filas[agotado_id]["estado"] == "fallido"
    assert filas[agotado_id]["intentos"] == MAX_INTENTOS
    # La marca queda en el propio `ultimo_error`, inspeccionable desde
    # PostgreSQL además de en el resumen que ve el proceso.
    assert "incidente no registrado" in filas[agotado_id]["ultimo_error"]
    # El que se entregó bien nunca falló: sigue sin `ultimo_error`.
    assert filas[ok_id]["ultimo_error"] is None

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from incident where referencia_id = %s",
            (agotado_id,))
        total_incidentes = cur.fetchone()["n"]
    conn.commit()
    assert total_incidentes == 0  # el insert del incidente se deshizo, sólo ese
