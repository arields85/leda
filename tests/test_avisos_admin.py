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

import os
import uuid
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone

import httpx
import pytest
from fastapi.testclient import TestClient

from prisma import despachador, gateway, incidentes
from prisma.db import admin, espacio, registrar_auditoria
from prisma.despachador import (BACKOFF_MINUTOS_AVISO_ADMIN, MAX_INTENTOS,
                                TransporteDePrueba, despachar_avisos_admin)

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


class _RespuestaGetUpdatesFalsa:
    def __init__(self, updates: list[dict]) -> None:
        self._updates = updates

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {"result": self._updates}


class _HttpAdminFalso:
    """Doble de `self.http` para probar `Escucha.recibir_admin` (T11) sin
    pegarle nunca a la API real de Telegram: registra cada llamada a `.get`
    (URL y params) para poder comprobar el sondeo sin bloqueo (`timeout=0`)
    y el offset propio del bot de administración."""

    def __init__(self, updates: list[dict] | None = None, falla: bool = False) -> None:
        self.updates = updates if updates is not None else []
        self.falla = falla
        self.llamadas: list[dict] = []

    def get(self, url, params=None):
        self.llamadas.append({"url": url, "params": params})
        if self.falla:
            raise ConnectionError("fallo simulado de red")
        return _RespuestaGetUpdatesFalsa(self.updates)


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
    e._transporte_admin = transporte_admin  # ya hay transporte: se salta la búsqueda del token
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


def test_tareas_de_fondo_entrega_avisos_admin_apenas_el_token_aparece(
        conn, corework, monkeypatch):
    """C: `_obtener_transporte_admin` no cachea la AUSENCIA del token -- si
    en la primera pasada `PRISMA_BOT_TOKEN_ADMIN` todavía no está
    configurado, no rompe nada (mismo caso que la prueba anterior) y, apenas
    el token aparece en una pasada posterior (sin reiniciar el proceso), el
    aviso que había quedado encolado se entrega."""
    from prisma import config as config_modulo
    from prisma import local as local_modulo
    from prisma.local import Escucha

    ws = corework.workspace_id
    with admin(conn) as cur:
        # Sin un administrador alcanzable no se encola ningún `admin_notice`
        # (`avisar_incidente_admin` no tiene a quién) -- hace falta uno para
        # que haya algo que la segunda pasada entregue.
        _administrador(cur, "Admin Token Tardio", 659001, chat_id=659001)
        incidentes.registrar_incidente(
            cur, ws, "Falló algo en una prueba.", etapa="prueba_directa")
    conn.commit()

    original = config_modulo.Config.token_bot
    intentos_admin = {"n": 0}

    def _token_admin_recien_en_la_segunda_pasada(self, slug):
        if slug != "admin":
            return original(self, slug)
        intentos_admin["n"] += 1
        if intentos_admin["n"] == 1:
            raise LookupError("Falta PRISMA_BOT_TOKEN_ADMIN en el entorno")
        return original(self, slug)

    monkeypatch.setattr(config_modulo.Config, "token_bot",
                        _token_admin_recien_en_la_segunda_pasada)
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "tok-admin-prueba")

    # `_obtener_transporte_admin` arma un `TransporteTelegram` real con el
    # token apenas aparece -- acá se reemplaza por un doble (mismo motivo
    # que `TransporteDePrueba` en el resto del archivo: sin esto, la
    # segunda pasada le pegaría de verdad a la API de Telegram con un token
    # falso y fallaría por eso, no por el token). Lo que prueba este caso es
    # que SE ARMA el transporte, no cómo entrega Telegram de verdad.
    monkeypatch.setattr(
        local_modulo, "TransporteTelegram",
        lambda token, cliente=None: TransporteDePrueba())
    # T11: apenas el token aparece, `_obtener_transporte_admin` consulta si
    # hay un webhook puesto sobre el bot de administración -- nunca la API
    # real de Telegram desde una prueba.
    _parchar_webhook_admin(monkeypatch, local_modulo)

    e = Escucha(conn, "corework", ws, "tok")
    e.transporte = TransporteDePrueba()
    # No depende de releer .env en esta prueba -- el token ya está en el
    # entorno vía monkeypatch; sólo hace falta que no se cachee la ausencia.
    e._ultimo_reintento_dotenv = datetime.now(timezone.utc)

    resumen1 = e.tareas_de_fondo()
    assert "avisos_admin_enviados" not in resumen1  # primera pasada: sin token, no rompe
    assert e._transporte_admin is None

    e.transporte = TransporteDePrueba()
    resumen2 = e.tareas_de_fondo()
    assert resumen2["avisos_admin_enviados"] == 1    # segunda pasada: ya hay token, entrega
    assert e._transporte_admin is not None
    assert len(e._transporte_admin.enviados) == 1


def test_obtener_transporte_admin_relee_env_cuando_el_token_llega_despues(
        conn, corework, monkeypatch, tmp_path):
    """C: `config._cargar_dotenv` sólo lee `.env` una vez, al importar el
    módulo -- si el token se agrega al archivo después de que el listener ya
    arrancó, sin releerlo nunca se vería hasta reiniciar el proceso.
    `_obtener_transporte_admin` relee `.env` (sin pisar lo que ya está en el
    entorno, throttleado para no pegarle al disco en cada pasada) para
    cubrir ese caso.

    R3-001 (revisión de confiabilidad, 2026-09-28): si esta máquina tiene un
    `.env` real con `PRISMA_BOT_TOKEN_ADMIN` (`config._cargar_dotenv` ya lo
    puso en `os.environ` al importar el módulo, una sola vez), la variable
    llega puesta y `monkeypatch.delenv(..., raising=False)` sí anota un
    undo -- el caso que rompía es el contrario, variable ausente al entrar.
    Se saca a mano ANTES de tocar `monkeypatch` (no con `monkeypatch.delenv`:
    sería la misma línea que se está probando) para ejercer ese caso sin
    depender de si esta máquina tiene el token real cargado, y se restaura
    a mano al final -- nunca queda de este archivo, y nunca se imprime ni se
    compara el valor real en un `assert` (`AssertionError` expone el valor
    de cada operando: repetir la cadena real ahí la dejaría en la salida de
    la prueba)."""
    from prisma import config as config_modulo
    from prisma import local as local_modulo
    from prisma.local import Escucha

    valor_real = os.environ.pop("PRISMA_BOT_TOKEN_ADMIN", None)
    try:
        # `setenv` antes de `delenv` fuerza que monkeypatch anote un undo
        # SIEMPRE, esté o no la variable puesta al entrar (R3-001): un
        # `delenv(..., raising=False)` solo, con la variable ya ausente, no
        # anota nada para deshacer.
        monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "placeholder-antes-de-recargar")
        monkeypatch.delenv("PRISMA_BOT_TOKEN_ADMIN")
        # T11: apenas el token aparece, `_obtener_transporte_admin` consulta
        # si hay un webhook puesto sobre el bot de administración -- nunca
        # la API real de Telegram desde una prueba.
        _parchar_webhook_admin(monkeypatch, local_modulo)
        dotenv = tmp_path / ".env"
        dotenv.write_text("", encoding="utf-8")
        monkeypatch.setattr(config_modulo, "RAIZ", tmp_path)

        ws = corework.workspace_id
        e = Escucha(conn, "corework", ws, "tok")

        assert e._obtener_transporte_admin() is None
        assert e._transporte_admin is None

        # El token se agrega al archivo mientras el proceso sigue corriendo.
        dotenv.write_text("PRISMA_BOT_TOKEN_ADMIN=tok-admin-nuevo\n", encoding="utf-8")
        e._ultimo_reintento_dotenv = None  # sin esperar el throttle real en la prueba

        transporte = e._obtener_transporte_admin()
        assert transporte is not None
        assert e._transporte_admin is transporte

        # `recargar_dotenv` escribe el token en `os.environ` con
        # `setdefault`, por fuera de `monkeypatch` -- si el `setenv`/
        # `delenv` de arriba no dejaran un undo anotado, ese token de
        # prueba se filtraría a cada prueba posterior del mismo proceso.
        # Se fuerza el undo ahora mismo (el fixture lo repite al cerrar la
        # prueba, sin efecto porque ya no queda nada pendiente) para
        # comprobar acá, no en otra prueba, que no quedó nada puesto.
        monkeypatch.undo()
        # Comparación por booleano, nunca `assert "..." not in os.environ`
        # directo: si esta prueba fallara, la introspección de `pytest`
        # imprimiría `os.environ` completo en el diff -- y esta máquina
        # puede tener un token real puesto (regla del proyecto: nunca
        # imprimir un secreto en un diagnóstico).
        quedo_filtrado = "PRISMA_BOT_TOKEN_ADMIN" in os.environ
        assert not quedo_filtrado, (
            "PRISMA_BOT_TOKEN_ADMIN quedó puesto en os.environ tras la "
            "prueba -- se filtraría a cualquier prueba posterior del mismo "
            "proceso")
    finally:
        if valor_real is not None:
            os.environ["PRISMA_BOT_TOKEN_ADMIN"] = valor_real
        else:
            os.environ.pop("PRISMA_BOT_TOKEN_ADMIN", None)


# ---------------------------------------------------------------------------
# T11: el modo local también sondea el bot de administración
#
# Hasta acá nadie podía volverse "alcanzable" (`db/esquema.sql`,
# `avisar_incidente_admin`) en desarrollo local: nada leía los updates del
# bot de administración fuera del webhook de `servir`. `Escucha.recibir_admin`
# cierra ese circuito -- estas pruebas nunca pegan a la API real de Telegram
# (`_HttpAdminFalso` para `self.http`, y `local_modulo.httpx.get` parchado
# para el `getWebhookInfo` que `_obtener_transporte_admin` consulta la
# primera vez que el token aparece, antes de sondear).
# ---------------------------------------------------------------------------

def _fijar_token_admin(monkeypatch, config_modulo, token: str = "tok-admin-prueba"):
    """Parcha `Config.token_bot` en vez de tocar variables de entorno, para
    no depender de si esta máquina tiene un `.env` real con
    `PRISMA_BOT_TOKEN_ADMIN` puesto."""
    original = config_modulo.Config.token_bot

    def _con_token_admin(self, slug):
        if slug == "admin":
            return token
        return original(self, slug)

    monkeypatch.setattr(config_modulo.Config, "token_bot", _con_token_admin)


class _RespuestaHttpFalsa:
    """Doble mínimo de `httpx.Response` para las pruebas de
    `getWebhookInfo` sobre el bot de administración -- sólo lo que
    `_obtener_transporte_admin` usa (`raise_for_status`, `json`)."""

    def __init__(self, *, status_code: int = 200,
                cuerpo: dict | None = None) -> None:
        self.status_code = status_code
        self._cuerpo = cuerpo if cuerpo is not None else {
            "ok": True, "result": {"url": ""}}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            pedido = httpx.Request(
                "GET", "https://api.telegram.org/botX/getWebhookInfo")
            raise httpx.HTTPStatusError(
                "fallo", request=pedido,
                response=httpx.Response(self.status_code, request=pedido))

    def json(self) -> dict:
        return self._cuerpo


def _parchar_webhook_admin(monkeypatch, local_modulo, *,
                           url_webhook: str = "", ok: bool = True,
                           status_code: int = 200) -> None:
    """Reemplaza la consulta a `getWebhookInfo` sobre el bot de
    administración por un doble -- nunca la API real de Telegram desde una
    prueba (mismo motivo que `_HttpAdminFalso`). Por default responde
    'sin webhook puesto', el caso que deja seguir sondeando."""
    def _get(url, timeout=None):
        return _RespuestaHttpFalsa(
            status_code=status_code,
            cuerpo={"ok": ok, "result": {"url": url_webhook}})

    monkeypatch.setattr(local_modulo.httpx, "get", _get)


def test_recibir_admin_sondea_con_timeout_0_y_offset_propio(
        conn, corework, monkeypatch, capsys):
    from prisma import config as config_modulo
    from prisma import local as local_modulo
    from prisma.local import Escucha

    ws = corework.workspace_id
    with admin(conn) as cur:
        _administrador(cur, "Admin Sondeo", 681001)  # todavía no le escribió al bot
    conn.commit()

    _fijar_token_admin(monkeypatch, config_modulo)
    _parchar_webhook_admin(monkeypatch, local_modulo)  # sin webhook: puede sondear

    update = {
        "update_id": 900,
        "message": {"message_id": 1, "text": "hola, soy administrador",
                   "chat": {"id": 681001}, "from": {"id": 681001, "first_name": "Admin"}},
    }
    http_admin = _HttpAdminFalso(updates=[update])
    e = Escucha(conn, "corework", ws, "tok", cliente=http_admin)

    recibidos = e.recibir_admin()

    assert recibidos == 1
    assert len(http_admin.llamadas) == 1
    llamada = http_admin.llamadas[0]
    assert llamada["url"] == "https://api.telegram.org/bottok-admin-prueba/getUpdates"
    assert llamada["params"] == {"offset": 0, "timeout": 0,
                                 "allowed_updates": '["message"]'}
    assert e.offset_admin == 901  # update_id + 1, offset propio del bot de administración

    salida = capsys.readouterr().out
    assert "[admin]" in salida
    assert "Admin" in salida
    assert "hola, soy administrador" in salida

    # Reachability de punta a punta (T11): el sondeo dejó el `mensaje_admin`
    # que `avisar_incidente_admin` exige -- un incidente posterior SÍ le
    # encola un aviso a este administrador.
    with admin(conn) as cur:
        cur.execute(
            """select actor_app_user_id, detalle from audit_log
                where accion = 'mensaje_admin'""")
        filas = cur.fetchall()
        assert len(filas) == 1
        assert filas[0]["detalle"]["chat_id"] == 681001

        incidentes.registrar_incidente(
            cur, ws, "Falló algo en una prueba.", etapa="prueba_directa")
        cur.execute("select chat_id from admin_notice")
        avisos = cur.fetchall()
    conn.commit()

    assert [a["chat_id"] for a in avisos] == [681001]


def test_recibir_admin_sin_token_no_sondea_y_no_rompe(conn, corework, monkeypatch):
    from prisma import config as config_modulo
    from prisma.local import Escucha

    def _sin_token(self, slug):
        raise LookupError(f"Falta PRISMA_BOT_TOKEN_{slug.upper()} en el entorno")

    monkeypatch.setattr(config_modulo.Config, "token_bot", _sin_token)

    ws = corework.workspace_id
    http_admin = _HttpAdminFalso()
    e = Escucha(conn, "corework", ws, "tok", cliente=http_admin)

    recibidos = e.recibir_admin()  # no debe levantar

    assert recibidos == 0
    assert http_admin.llamadas == []  # nunca sondeó: ni un solo GET
    assert e.offset_admin == 0
    assert e._transporte_admin is None


def test_obtener_transporte_admin_consulta_getwebhookinfo_una_sola_vez_cuando_esta_vacio(
        conn, corework, monkeypatch):
    """Mismo motivo que en `escuchar()` para el bot del espacio: un webhook
    activo bloquea `getUpdates`, así que antes de sondear por primera vez
    hay que confirmar que el bot de administración no tiene uno puesto. La
    consulta corre una sola vez por proceso -- una vez que
    `_transporte_admin` queda cacheado (webhook vacío), las vueltas
    siguientes no vuelven a pegarle a la API de Telegram para esto."""
    from prisma import config as config_modulo
    from prisma import local as local_modulo
    from prisma.local import Escucha

    ws = corework.workspace_id
    _fijar_token_admin(monkeypatch, config_modulo, token="tok-admin-sin-webhook")
    llamadas_get: list[str] = []

    def _get(url, timeout=None):
        llamadas_get.append(url)
        return _RespuestaHttpFalsa()  # ok=True, sin webhook, por default

    monkeypatch.setattr(local_modulo.httpx, "get", _get)

    e = Escucha(conn, "corework", ws, "tok", cliente=_HttpAdminFalso())

    e.recibir_admin()
    assert llamadas_get == [
        "https://api.telegram.org/bottok-admin-sin-webhook/getWebhookInfo"]

    e.recibir_admin()  # segunda vuelta: no la vuelve a consultar
    assert llamadas_get == [
        "https://api.telegram.org/bottok-admin-sin-webhook/getWebhookInfo"]


def test_recibir_admin_no_sondea_si_el_bot_de_administracion_ya_tiene_webhook(
        conn, corework, monkeypatch, capsys):
    """R1-001/R4-001/R3-002 (revisión de riesgo y confiabilidad,
    2026-09-28): si el token puesto en `PRISMA_BOT_TOKEN_ADMIN` es el de un
    bot que YA está servido por un webhook en otro lado (p. ej. el de
    producción reusado por error acá), `escuchar` nunca puede tocarlo ni
    sondearlo -- le robaría los updates a quien lo está sirviendo. Sólo
    avisa por consola, una sola vez aunque pasen varias vueltas."""
    from prisma import config as config_modulo
    from prisma import local as local_modulo
    from prisma.local import Escucha

    ws = corework.workspace_id
    _fijar_token_admin(monkeypatch, config_modulo, token="tok-admin-prod-reusado")
    llamadas_post: list[str] = []
    monkeypatch.setattr(
        local_modulo.httpx, "post",
        lambda url, timeout=None: llamadas_post.append(url))
    _parchar_webhook_admin(
        monkeypatch, local_modulo,
        url_webhook="https://prisma-vps.example.com/telegram/admin")

    http_admin = _HttpAdminFalso()
    e = Escucha(conn, "corework", ws, "tok", cliente=http_admin)

    recibidos = e.recibir_admin()

    assert recibidos == 0
    assert http_admin.llamadas == []  # nunca sondeó al bot de administración
    assert llamadas_post == []        # y nunca le llamó a `deleteWebhook`
    assert e._transporte_admin is None

    salida = capsys.readouterr().out
    assert salida.count("ya tiene un webhook puesto") == 1
    assert "prisma-vps.example.com" in salida  # el host es útil
    assert "tok-admin-prod-reusado" not in salida  # el token nunca

    e.recibir_admin()  # segunda vuelta: sigue sin sondear y no repite el aviso
    assert http_admin.llamadas == []
    salida2 = capsys.readouterr().out
    assert "ya tiene un webhook puesto" not in salida2


def test_obtener_transporte_admin_si_falla_getwebhookinfo_avisa_y_reintenta_despues(
        conn, corework, monkeypatch, capsys):
    """Si la consulta a `getWebhookInfo` sobre el bot de administración
    falla (red, HTTP), nunca se asume que no hay webhook puesto -- se avisa
    (regla del proyecto: nunca en silencio) y NO se cachea la falla: una
    vuelta posterior, una vez que la consulta responde bien, resuelve el
    transporte sin reiniciar el proceso."""
    from prisma import config as config_modulo
    from prisma import local as local_modulo
    from prisma.local import Escucha

    ws = corework.workspace_id
    _fijar_token_admin(monkeypatch, config_modulo)

    def _get_que_falla(url, timeout=None):
        raise ConnectionError("fallo simulado consultando getWebhookInfo")

    monkeypatch.setattr(local_modulo.httpx, "get", _get_que_falla)

    e = Escucha(conn, "corework", ws, "tok", cliente=_HttpAdminFalso())

    transporte = e._obtener_transporte_admin()
    assert transporte is None
    salida = capsys.readouterr().out
    assert "no se pudo confirmar" in salida

    # Vuelta posterior (sin esperar el throttle real): la falla nunca se
    # cachea como si el chequeo hubiera pasado.
    e._ultimo_chequeo_webhook_admin = None
    _parchar_webhook_admin(monkeypatch, local_modulo)  # esta vez responde bien

    transporte2 = e._obtener_transporte_admin()
    assert transporte2 is not None


def test_obtener_transporte_admin_si_getwebhookinfo_responde_ok_false_avisa_y_reintenta(
        conn, corework, monkeypatch, capsys):
    """Mismo caso que una falla de red: Telegram puede responder 200 con
    `ok: false` -- tampoco ahí se asume que no hay webhook puesto."""
    from prisma import config as config_modulo
    from prisma import local as local_modulo
    from prisma.local import Escucha

    ws = corework.workspace_id
    _fijar_token_admin(monkeypatch, config_modulo)
    _parchar_webhook_admin(monkeypatch, local_modulo, ok=False)

    e = Escucha(conn, "corework", ws, "tok", cliente=_HttpAdminFalso())

    transporte = e._obtener_transporte_admin()
    assert transporte is None
    salida = capsys.readouterr().out
    assert "no se pudo confirmar" in salida

    e._ultimo_chequeo_webhook_admin = None
    _parchar_webhook_admin(monkeypatch, local_modulo)  # ok=True esta vez

    transporte2 = e._obtener_transporte_admin()
    assert transporte2 is not None


def test_recibir_admin_error_de_procesamiento_registra_incidente_global_y_sigue(
        conn, corework, monkeypatch, capsys):
    """Un update del bot de administración que rompe al procesarse nunca se
    pierde en silencio -- pero acá no hay espacio
    (`gateway.reportar_incidente_no_manejado` haría `if workspace_id is
    None: return` y perdería el incidente), así que
    `_reportar_incidente_admin_no_manejado` registra uno global."""
    from prisma import config as config_modulo
    from prisma import local as local_modulo
    from prisma.local import Escucha

    ws = corework.workspace_id
    _fijar_token_admin(monkeypatch, config_modulo)
    _parchar_webhook_admin(monkeypatch, local_modulo)
    monkeypatch.setattr(
        local_modulo, "procesar_update",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("fallo simulado admin")))

    update = {
        "update_id": 950,
        "message": {"message_id": 2, "text": "esto rompe",
                   "chat": {"id": 691001}, "from": {"id": 691001, "first_name": "Rota"}},
    }
    e = Escucha(conn, "corework", ws, "tok",
               cliente=_HttpAdminFalso(updates=[update]))

    recibidos = e.recibir_admin()  # no debe levantar la excepción

    assert recibidos == 1
    salida = capsys.readouterr().out
    assert "no se pudo procesar [admin]: RuntimeError" in salida

    with admin(conn) as cur:
        cur.execute(
            """select severidad, etapa, chat_id, referencia_cruda from incident
                where workspace_id is null and etapa = 'mensaje_admin'""")
        incidente = cur.fetchone()

    assert incidente is not None
    assert incidente["severidad"] == "alta"
    assert incidente["chat_id"] == 691001
    assert "fallo simulado admin" in incidente["referencia_cruda"]
    # El offset ya avanzó aunque el procesamiento haya fallado: no reintenta
    # el mismo update para siempre (mismo criterio que `recibir`).
    assert e.offset_admin == 951


def test_error_de_red_se_describe_sin_la_url_que_lleva_el_token():
    """El mensaje de un error de httpx incluye la URL, y la URL de la API de
    Telegram lleva el token del bot: la consola del listener no lo muestra."""
    import httpx

    from prisma.local import _error_sin_url

    pedido = httpx.Request("GET", "https://api.telegram.org/bot123:SECRETO/getUpdates")
    respuesta = httpx.Response(401, request=pedido)
    error = httpx.HTTPStatusError("fallo", request=pedido, response=respuesta)
    error_con_url = httpx.ConnectError(f"sin red para {pedido.url}", request=pedido)

    descripcion = _error_sin_url(error)
    descripcion_conexion = _error_sin_url(error_con_url)

    filtra_token = "SECRETO" in descripcion or "SECRETO" in descripcion_conexion
    assert not filtra_token, "la descripción del error incluye el token"
    assert descripcion == "HTTPStatusError HTTP 401"
    assert descripcion_conexion == "ConnectError"
