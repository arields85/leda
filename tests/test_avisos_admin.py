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
from contextlib import nullcontext
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import gateway, incidentes
from prisma.db import admin, espacio, registrar_auditoria
from prisma.despachador import TransporteDePrueba, despachar_avisos_admin

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def cliente(conn, monkeypatch):
    monkeypatch.setattr(gateway, "acusar_toque", lambda *a, **k: None)
    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    import dataclasses
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    return TestClient(gateway.app)


def _mensaje(cliente, user_id, texto):
    return cliente.post(
        "/telegram/corework",
        json={"message": {"message_id": 2, "text": texto,
                          "chat": {"id": user_id}, "from": {"id": user_id}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _telegram_id(cur, nombre) -> int:
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return cur.fetchone()["t"]


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
# Fan-out a cada administrador alcanzable
# ---------------------------------------------------------------------------

def test_excepcion_no_manejada_en_un_turno_avisa_a_cada_administrador_vinculado(
        cliente, conn, corework, monkeypatch):
    """Decisión del usuario, 2026-09-28 (corregida el mismo día): un
    incidente ya no sólo avisa a la persona afectada -- también a cada
    administrador de plataforma que tenga el bot de administración
    vinculado, y ese aviso SÍ incluye qué lo disparó (el mensaje de la
    persona, Constitución §2: el administrador ya accede a las
    conversaciones privadas). La persona sigue recibiendo su aviso neutro
    exactamente igual que antes -- nunca el disparador ni nada técnico; el
    administrador sin vincular no recibe nada (no hay a qué chat
    mandarle)."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _administrador(cur, "Admin Uno", 611001, chat_id=611001)
        _administrador(cur, "Admin Dos", 611002, chat_id=611002)
        _administrador(cur, "Admin Sin Vincular", 611003)  # nunca le escribió al bot
    conn.commit()

    def _explota(cur, quien, texto, workspace_id, chat_id, entrante_id=None):
        raise RuntimeError("falla inesperada de prueba")

    monkeypatch.setattr(gateway, "_turno", _explota)

    with espacio(conn, ws) as cur:
        tg = _telegram_id(cur, "Nahuel Gimenez")
    conn.commit()

    r = _mensaje(cliente, tg, "arranco con esto")
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute(
            """select id, resumen_sanitizado, notificado_en, notificado_admin_en
                 from incident where workspace_id = %s
                order by at desc limit 1""", (ws,))
        incidente = cur.fetchone()
        assert incidente["notificado_en"] is not None       # la persona, igual que antes
        assert incidente["notificado_admin_en"] is not None  # y ahora también la administración

        # El aviso neutro a la persona no cambió: nunca el disparador ni nada técnico.
        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para desc limit 1""", (tg,))
        assert cur.fetchone()["cuerpo"] == gateway.NOTICIA_NEUTRA_INCIDENTE

        cur.execute(
            """select destinatario_app_user_id, chat_id, cuerpo
                 from admin_notice where incident_id = %s
                order by chat_id""", (incidente["id"],))
        avisos = cur.fetchall()
        assert {a["chat_id"] for a in avisos} == {611001, 611002}  # nunca el sin vincular

        for a in avisos:
            cuerpo = a["cuerpo"]
            # El disparador (el mensaje de la persona) SÍ está -- eso es lo
            # que corrigió el usuario: el administrador tiene que ver qué
            # pasó, no sólo que algo pasó.
            assert "arranco con esto" in cuerpo
            # El tipo de excepción también (viene en resumen_sanitizado,
            # nunca un secreto). El texto crudo de la excepción
            # (`referencia_cruda`, sólo para `python -m prisma incidentes`)
            # nunca sale acá -- por eso "falla inesperada de prueba" (el
            # `str(error)`) no aparece, aunque "RuntimeError" (el tipo) sí.
            assert "RuntimeError" in cuerpo
            assert "falla inesperada de prueba" not in cuerpo
            # Quién: la persona identificada.
            assert "Nahuel Gimenez" in cuerpo
            # Prefijo del incidente, espacio, etapa, severidad y hora -- lo
            # mínimo para encontrar el detalle con
            # `python -m prisma incidentes corework`.
            assert str(incidente["id"])[:8] in cuerpo
            assert "corework" in cuerpo
            assert gateway.ETAPA_TURNO_TEXTO in cuerpo
            assert "alta" in cuerpo


def test_el_aviso_nunca_lleva_referencia_cruda_ni_algo_parecido_a_un_secreto(
        cliente, conn, corework, monkeypatch):
    """Corrección del usuario, 2026-09-28: el disparador (el mensaje de la
    persona) SÍ va en el aviso, pero nunca `referencia_cruda` -- la traza
    técnica cruda de la excepción, que puede traer algo parecido a un
    token o una cadena de conexión. Aunque la excepción la lleve adentro,
    el aviso a la administración no la repite: sólo manda el tipo de
    excepción (vía resumen_sanitizado), nunca su `str()`."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _administrador(cur, "Admin Secreto", 612001, chat_id=612001)
    conn.commit()

    secreto = "postgresql://prisma_app:s3cr3t-p4ss@db.interno:5432/prisma"

    def _explota(cur, quien, texto, workspace_id, chat_id, entrante_id=None):
        raise RuntimeError(f"no se pudo conectar: {secreto}")

    monkeypatch.setattr(gateway, "_turno", _explota)

    with espacio(conn, ws) as cur:
        tg = _telegram_id(cur, "Nahuel Gimenez")
    conn.commit()

    assert _mensaje(cliente, tg, "probando la conexión").status_code == 200

    with admin(conn) as cur:
        cur.execute(
            """select id, referencia_cruda from incident where workspace_id = %s
                order by at desc limit 1""", (ws,))
        incidente = cur.fetchone()
        assert secreto in incidente["referencia_cruda"]  # sí queda para `incidentes <slug>`

        cur.execute("select cuerpo from admin_notice where incident_id = %s",
                    (incidente["id"],))
        cuerpo = cur.fetchone()["cuerpo"]

    assert secreto not in cuerpo
    assert "s3cr3t-p4ss" not in cuerpo
    assert "postgresql://" not in cuerpo
    assert "no se pudo conectar" not in cuerpo    # el str() completo, no sólo el secreto
    assert "probando la conexión" in cuerpo        # el disparador sí sale


def test_cada_aviso_admin_deja_un_acceso_a_conversacion_en_audit_log(
        cliente, conn, corework, monkeypatch):
    """Constitución §12: "El acceso del administrador a conversaciones
    también se registra." Cada aviso que de verdad se encoló deja una fila
    en `audit_log` -- una por administrador, nunca el texto del mensaje,
    sólo la acción, el incidente y el mensaje referenciado."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _administrador(cur, "Admin Auditado Uno", 613001, chat_id=613001)
        _administrador(cur, "Admin Auditado Dos", 613002, chat_id=613002)
    conn.commit()

    def _explota(cur, quien, texto, workspace_id, chat_id, entrante_id=None):
        raise RuntimeError("falla inesperada de prueba")

    monkeypatch.setattr(gateway, "_turno", _explota)

    with espacio(conn, ws) as cur:
        tg = _telegram_id(cur, "Nahuel Gimenez")
    conn.commit()

    assert _mensaje(cliente, tg, "arranco con esto").status_code == 200

    with admin(conn) as cur:
        cur.execute(
            """select id, referencia_tipo, referencia_id from incident
                where workspace_id = %s order by at desc limit 1""", (ws,))
        incidente = cur.fetchone()

        cur.execute(
            """select actor_app_user_id, actor_kind, sujeto_tipo, sujeto_id, detalle
                 from audit_log where accion = 'aviso_incidente_admin'
                order by actor_app_user_id""")
        filas = cur.fetchall()

    assert len(filas) == 2   # uno por administrador avisado, nunca por incidente
    admins_auditados = {str(f["actor_app_user_id"]) for f in filas}
    with admin(conn) as cur:
        cur.execute(
            "select id from app_user where telegram_user_id in (613001, 613002)")
        ids_esperados = {str(f["id"]) for f in cur.fetchall()}
    assert admins_auditados == ids_esperados
    for f in filas:
        assert f["actor_kind"] == "prisma"   # Prisma lo mandó, no un click del admin
        assert f["sujeto_tipo"] == incidente["referencia_tipo"]
        assert f["sujeto_id"] == incidente["referencia_id"]
        assert f["detalle"]["incident_id"] == str(incidente["id"])
        assert "arranco con esto" not in str(f["detalle"])  # nunca el texto, sólo la referencia


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

    assert resumen == {"enviados": 1, "fallidos": 0}
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

    assert resumen == {"enviados": 0, "fallidos": 1}
    assert fila["estado"] == "listo"          # menos de MAX_INTENTOS: reintenta
    assert fila["intentos"] == 1
    assert fila["ultimo_error"]


def test_tareas_de_fondo_despacha_los_avisos_admin_en_el_modo_local(conn, corework):
    """El mismo ciclo que hoy corre la escalera y despacha la cola de un
    espacio (`local.Escucha.tareas_de_fondo`) también despacha los avisos de
    administración -- no están acotados a ningún espacio en particular, así
    que se despachan aparte, bajo rol `prisma_admin`."""
    from prisma.local import Escucha

    ws = corework.workspace_id
    with admin(conn) as cur:
        _administrador(cur, "Admin Local", 666001, chat_id=666001)
        incidentes.registrar_incidente(
            cur, ws, "Falló algo en una prueba.", etapa="prueba_directa")
    conn.commit()

    e = Escucha(conn, "corework", ws, "tok")
    transporte_admin = TransporteDePrueba()
    e._transporte_admin = transporte_admin
    e._transporte_admin_probado = True   # se salta la búsqueda de PRISMA_BOT_TOKEN_ADMIN
    e.transporte = TransporteDePrueba()  # el de la cola del espacio, sin usar acá

    resumen = e.tareas_de_fondo()

    assert resumen["avisos_admin_enviados"] == 1
    assert len(transporte_admin.enviados) == 1
    assert transporte_admin.enviados[0].chat_id == 666001


def test_tareas_de_fondo_sin_token_de_administracion_no_rompe(conn, corework, monkeypatch):
    """Sin `PRISMA_BOT_TOKEN_ADMIN` configurado (desarrollo local sin el bot
    de administración levantado), los avisos quedan encolados en
    `admin_notice` sin que nada se caiga -- se entregan solos en cuanto se
    configure el token."""
    from prisma import config as config_modulo
    from prisma.local import Escucha

    ws = corework.workspace_id
    with admin(conn) as cur:
        incidentes.registrar_incidente(
            cur, ws, "Falló algo en una prueba.", etapa="prueba_directa")
    conn.commit()

    def _sin_token(self, slug):
        raise LookupError(f"Falta PRISMA_BOT_TOKEN_{slug.upper()} en el entorno")

    monkeypatch.setattr(config_modulo.Config, "token_bot", _sin_token)

    e = Escucha(conn, "corework", ws, "tok")
    e.transporte = TransporteDePrueba()

    resumen = e.tareas_de_fondo()   # no debe levantar ninguna excepción

    assert "avisos_admin_enviados" not in resumen
