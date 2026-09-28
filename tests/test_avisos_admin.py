"""Entrega de avisos "🛠️ Administración" por el bot de administración
(rama auxiliar, G1d).

`message_outbox` exige `workspace_id` y se despacha por el bot de cada
espacio; estas pruebas ejercitan el camino de salida propio del bot de
administración (`avisos_admin.py`) directo contra la base, con el doble de
transporte que ya usa `despachador.py` -- nunca Telegram real.
"""

from __future__ import annotations

import dataclasses
import threading
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import alta_correo as AC
from prisma import alta_correo_flujo as ACF
from prisma import avisos_admin as AA
from prisma import gateway
from prisma.db import admin, conectar, espacio
from prisma.despachador import TransporteDePrueba

AHORA = datetime(2028, 3, 15, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def cliente_admin(conn, monkeypatch):
    """`TestClient` contra el webhook del bot de administración
    (`/telegram/admin`) -- nunca Telegram real."""
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    return TestClient(gateway.app)


def _post_admin_texto(cliente_admin, texto, user_id, chat_id=None, message_id=1):
    return cliente_admin.post(
        "/telegram/admin",
        json={"message": {"message_id": message_id, "text": texto,
                          "chat": {"id": chat_id or user_id, "type": "private"},
                          "from": {"id": user_id}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _post_admin_toque(cliente_admin, callback, user_id, chat_id=None):
    return cliente_admin.post(
        "/telegram/admin",
        json={"callback_query": {"id": "cb1", "data": callback,
                                 "from": {"id": user_id},
                                 "message": {"chat": {"id": chat_id or user_id}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _hacer_administrador(conn, intake_world, workspace_key: str, persona: str) -> tuple[str, int]:
    """Da rol de plataforma `administrador` a alguien que ya tiene Telegram
    vinculado (por `intake_world`). Devuelve `(app_user_id, telegram_user_id)`."""
    datos = intake_world[workspace_key]["people"][persona]
    with admin(conn) as cur:
        cur.execute(
            "insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
            (datos["app_user_id"],))
    conn.commit()
    return datos["app_user_id"], datos["telegram"]


def _crear_aviso(conn, ws: str, tipo: str = "correo_existente_pendientes",
                 texto: str = "3 integrantes todavía no dieron su correo.") -> str:
    with espacio(conn, ws) as cur:
        aviso_id = AC.crear_aviso(cur, tipo, texto, ahora=AHORA)
    conn.commit()
    return aviso_id


def _dejar_pending_verification_con_aviso_agotado(
        conn, ws: str, m: str, nombre: str,
        correo: str = "persona@empresa.com") -> str:
    """Deja una membresía en `pending_email_verification` con un envío
    vigente, y el aviso `correo_limite_agotado` ya creado -- el escenario de
    partida de "Habilitar un nuevo intento" (G1d-b, acción F)."""
    with espacio(conn, ws) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m, correo, "token-agotado", ahora=AHORA)
        aviso_id = AC.crear_aviso(
            cur, AC.TIPO_CORREO_LIMITE_AGOTADO,
            f"{nombre} agotó los 5 envíos del correo de verificación.",
            referencia_tipo="membership", referencia_id=m, ahora=AHORA)
    conn.commit()
    return aviso_id


# ===========================================================================
# G1d-b/F: "Habilitar un nuevo intento" sobre el aviso de envíos agotados
# ===========================================================================


def test_aviso_de_limite_agotado_trae_habilitar_y_marcar_leido(
        conn, intake_world, monkeypatch):
    """F (textos aprobados por el usuario, 2026-09-28): este tipo de aviso
    suma "Habilitar un nuevo intento" -- los demás siguen sólo con "Marcar
    leído" (`test_despachar_avisos_entrega_a_cada_administrador_con_
    telegram`, arriba, ya cubre ese caso general)."""
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        AA.despachar_avisos(cur, doble, ahora=AHORA)
    conn.commit()

    [entrega] = doble.enviados
    assert entrega.texto.startswith("🛠️ Administración · North Lab")
    assert "Taylor Quinn agotó los 5 envíos del correo de verificación." in entrega.texto
    assert [b.etiqueta for b in entrega.botones] == [
        AA.ETIQUETA_HABILITAR, AA.ETIQUETA_MARCAR_LEIDO]


def test_habilitar_muestra_vista_previa_sin_aplicar_nada(
        cliente_admin, conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    _, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")

    r = _post_admin_toque(cliente_admin, AA.callback_data(AA.ACCION_HABILITAR, aviso_id), tg)
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select texto, botones from aviso_administrativo_respuesta")
        [fila] = cur.fetchall()
        assert "Taylor Quinn" in fila["texto"]
        assert "@" not in fila["texto"]       # nunca el correo -- administración no lo necesita
        etiquetas = {b["etiqueta"] for b in fila["botones"]}
        assert etiquetas == {AA.ETIQUETA_CONFIRMAR, AA.ETIQUETA_CANCELAR}
        [aviso] = AC.avisos(cur)
        assert aviso["resuelto_en"] is None
        cur.execute(
            "select count(*) n from alta_correo_evento where tipo = 'intento_habilitado'")
        assert cur.fetchone()["n"] == 0


def test_habilitar_sobre_aviso_ya_resuelto_no_ofrece_confirmar(
        cliente_admin, conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    admin_id, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")
    with admin(conn) as cur:
        AC.marcar_resuelto(cur, aviso_id, admin_id, ahora=AHORA)
    conn.commit()

    r = _post_admin_toque(cliente_admin, AA.callback_data(AA.ACCION_HABILITAR, aviso_id), tg)
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select texto, botones from aviso_administrativo_respuesta")
        [fila] = cur.fetchall()
        assert fila["texto"] == AA.TEXTO_HABILITAR_YA_RESUELTO
        assert not fila["botones"]


def test_confirmar_habilitar_aplica_evento_resuelve_aviso_y_avisa_a_la_persona(
        cliente_admin, conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    tg_persona = intake_world["north-lab"]["people"]["Taylor Quinn"]["telegram"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    admin_id, tg_admin = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _dejar_pending_verification_con_aviso_agotado(
        conn, ws, m, "Taylor Quinn", correo="taylor.quinn@empresa.com")

    r = _post_admin_toque(
        cliente_admin, AA.callback_data(AA.ACCION_CONFIRMAR_HABILITAR, aviso_id), tg_admin)
    assert r.status_code == 200

    with admin(conn) as cur:
        [aviso] = AC.avisos(cur)
        assert aviso["resuelto_en"] is not None
        assert str(aviso["resuelto_por"]) == admin_id
        cur.execute(
            "select count(*) n from alta_correo_evento "
            "where membership_id = %s and tipo = 'intento_habilitado'", (m,))
        assert cur.fetchone()["n"] == 1
        cur.execute("select texto from aviso_administrativo_respuesta where chat_id = %s",
                   (tg_admin,))
        assert [f["texto"] for f in cur.fetchall()] == [AA.TEXTO_HABILITAR_CONFIRMADO]

    with espacio(conn, ws) as cur:
        cur.execute(
            "select cuerpo from message_outbox where chat_id = %s "
            "order by programado_para", (tg_persona,))
        textos = [f["cuerpo"] for f in cur.fetchall()]
    assert textos[-1] == ACF.texto_reintento_habilitado("taylor.quinn@empresa.com")


def test_confirmar_habilitar_dos_veces_no_duplica_nada(
        cliente_admin, conn, intake_world):
    """Idempotente bajo doble tap: el segundo Confirmar sobre un aviso ya
    resuelto no aplica una segunda vez -- ni un segundo evento, ni un
    segundo aviso a la persona."""
    ws = intake_world["north-lab"]["id"]
    tg_persona = intake_world["north-lab"]["people"]["Taylor Quinn"]["telegram"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    admin_id, tg_admin = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _dejar_pending_verification_con_aviso_agotado(
        conn, ws, m, "Taylor Quinn", correo="taylor.quinn@empresa.com")

    _post_admin_toque(
        cliente_admin, AA.callback_data(AA.ACCION_CONFIRMAR_HABILITAR, aviso_id), tg_admin)
    r2 = _post_admin_toque(
        cliente_admin, AA.callback_data(AA.ACCION_CONFIRMAR_HABILITAR, aviso_id), tg_admin)
    assert r2.status_code == 200

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from alta_correo_evento "
            "where membership_id = %s and tipo = 'intento_habilitado'", (m,))
        assert cur.fetchone()["n"] == 1
        cur.execute("select texto from aviso_administrativo_respuesta where chat_id = %s",
                   (tg_admin,))
        assert [f["texto"] for f in cur.fetchall()] == [AA.TEXTO_HABILITAR_CONFIRMADO]
    with espacio(conn, ws) as cur:
        cur.execute("select count(*) n from message_outbox where chat_id = %s", (tg_persona,))
        assert cur.fetchone()["n"] == 1


def test_confirmar_habilitar_sin_poder_avisar_a_la_persona_no_resuelve_ni_aplica(
        cliente_admin, conn, intake_world):
    """Nunca fallar en silencio: si la persona no se puede avisar (sin
    Telegram vinculado), no se aplica el intento ni se resuelve el aviso, y
    el administrador recibe el aviso neutral -- nunca "Listo, habilitado."
    cuando a la persona no le va a llegar nada."""
    ws = intake_world["north-lab"]["id"]
    persona = intake_world["north-lab"]["people"]["Taylor Quinn"]
    m = persona["membership_id"]
    _, tg_admin = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")
    with admin(conn) as cur:
        cur.execute("update app_user set telegram_user_id = null where id = %s",
                    (persona["app_user_id"],))
    conn.commit()

    r = _post_admin_toque(
        cliente_admin, AA.callback_data(AA.ACCION_CONFIRMAR_HABILITAR, aviso_id), tg_admin)
    assert r.status_code == 200

    with admin(conn) as cur:
        [aviso] = AC.avisos(cur)
        assert aviso["resuelto_en"] is None
        cur.execute(
            "select count(*) n from alta_correo_evento "
            "where membership_id = %s and tipo = 'intento_habilitado'", (m,))
        assert cur.fetchone()["n"] == 0
        cur.execute("select texto from aviso_administrativo_respuesta where chat_id = %s",
                   (tg_admin,))
        assert [f["texto"] for f in cur.fetchall()] == [gateway.NOTICIA_NEUTRA_INCIDENTE]
        cur.execute("select count(*) n from incident where workspace_id is null")
        assert cur.fetchone()["n"] == 1


def test_confirmar_habilitar_serializa_dos_administradores_a_la_vez(
        conn, intake_world, uri):
    """Dos confirmaciones simultáneas sobre el mismo aviso: la segunda
    espera a la primera (candado sobre la fila del aviso) en vez de leer
    los dos "sin resolver" y aplicar dos veces."""
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    admin_id, _ = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")

    primera = conectar(uri)
    resultado_segunda: list = []
    errores: list = []

    def segunda_confirmacion():
        otra = None
        try:
            otra = conectar(uri)
            with admin(otra) as cur2:
                resultado_segunda.append(
                    AA.confirmar_habilitar(cur2, aviso_id, admin_id, ahora=AHORA))
            otra.commit()
        except Exception as exc:  # la prueba revisa que no haya ninguna
            errores.append(exc)
            if otra is not None:
                otra.rollback()
        finally:
            if otra is not None:
                otra.close()

    hilo = threading.Thread(target=segunda_confirmacion)
    try:
        with admin(primera) as cur:
            assert AA.confirmar_habilitar(cur, aviso_id, admin_id, ahora=AHORA) is True
            # La primera sigue abierta: la segunda arranca mientras tanto.
            hilo.start()
            hilo.join(timeout=1)
        primera.commit()
    finally:
        primera.close()
    hilo.join(timeout=30)
    assert not hilo.is_alive(), "la segunda confirmación quedó colgada"

    assert errores == []
    assert resultado_segunda == [False]

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from alta_correo_evento "
            "where membership_id = %s and tipo = 'intento_habilitado'", (m,))
        assert cur.fetchone()["n"] == 1


def test_cancelar_habilitar_no_aplica_nada(cliente_admin, conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    _, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")

    r = _post_admin_toque(
        cliente_admin, AA.callback_data(AA.ACCION_CANCELAR_HABILITAR, aviso_id), tg)
    assert r.status_code == 200

    with admin(conn) as cur:
        [aviso] = AC.avisos(cur)
        assert aviso["resuelto_en"] is None
        cur.execute("select texto from aviso_administrativo_respuesta")
        assert [f["texto"] for f in cur.fetchall()] == [AA.TEXTO_HABILITAR_CANCELADO]
        cur.execute(
            "select count(*) n from alta_correo_evento where tipo = 'intento_habilitado'")
        assert cur.fetchone()["n"] == 0


def test_toque_habilitar_de_un_no_administrador_no_hace_nada(
        cliente_admin, conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    aviso_id = _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")
    ajeno = intake_world["north-lab"]["people"]["Sam North"]["telegram"]

    r = _post_admin_toque(cliente_admin, AA.callback_data(AA.ACCION_HABILITAR, aviso_id), ajeno)
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select count(*) n from aviso_administrativo_respuesta")
        assert cur.fetchone()["n"] == 0
        [aviso] = AC.avisos(cur)
        assert aviso["resuelto_en"] is None


def _hacer_administrador_sin_telegram(conn, nombre: str = "Sin Telegram") -> str:
    """Administrador de plataforma sin ninguna cuenta de Telegram vinculada
    -- `app_user.telegram_user_id` en `null` (G1d-a3, ítem 3)."""
    with admin(conn) as cur:
        cur.execute(
            "insert into app_user (nombre) values (%s) returning id", (nombre,))
        app_user_id = str(cur.fetchone()["id"])
        cur.execute(
            "insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
            (app_user_id,))
    conn.commit()
    return app_user_id


# ===========================================================================
# A. `partes_de_callback` / `callback_data` -- funciones puras
# ===========================================================================


def test_callback_data_y_partes_son_inversas():
    data = AA.callback_data(AA.ACCION_LEIDO, "abc-123")
    assert AA.partes_de_callback(data) == (AA.ACCION_LEIDO, "abc-123")


def test_partes_de_callback_ninguna_para_callback_ajeno():
    assert AA.partes_de_callback("p:algo") is None
    assert AA.partes_de_callback("") is None
    assert AA.partes_de_callback("adm:leido:") is None


# ===========================================================================
# B. `despachar_avisos`
# ===========================================================================


def test_despachar_avisos_entrega_a_cada_administrador_con_telegram(
        conn, intake_world, monkeypatch):
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    ws = intake_world["north-lab"]["id"]
    _, tg_a = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    _, tg_b = _hacer_administrador(conn, intake_world, "north-lab", "Taylor Quinn")
    aviso_id = _crear_aviso(conn, ws)

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        resumen = AA.despachar_avisos(cur, doble, ahora=AHORA)
    conn.commit()

    assert resumen == {"reconciliados": 2, "enviados": 2, "fallidos": 0}
    destinatarios = {e.chat_id for e in doble.enviados}
    assert destinatarios == {tg_a, tg_b}
    [entrega] = [e for e in doble.enviados if e.chat_id == tg_a]
    assert entrega.texto.startswith("🛠️ Administración")
    assert "North Lab" in entrega.texto
    assert "3 integrantes todavía no dieron su correo." in entrega.texto
    assert [b.etiqueta for b in entrega.botones] == [AA.ETIQUETA_MARCAR_LEIDO]
    assert AA.partes_de_callback(entrega.botones[0].callback_data) == (
        AA.ACCION_LEIDO, aviso_id)

    with admin(conn) as cur:
        cur.execute(
            "select estado, delivered_at, telegram_message_id "
            "from aviso_administrativo_entrega where aviso_id = %s", (aviso_id,))
        filas = cur.fetchall()
        assert len(filas) == 2
        for fila in filas:
            assert fila["estado"] == "enviado"
            assert fila["delivered_at"] is not None
            assert fila["telegram_message_id"] is not None


def test_despachar_avisos_no_repite_una_entrega_ya_enviada(conn, intake_world, monkeypatch):
    """Correr el despacho dos veces (dos vueltas del loop) no manda el
    mismo aviso dos veces al mismo administrador."""
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    ws = intake_world["north-lab"]["id"]
    _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    _crear_aviso(conn, ws)

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        AA.despachar_avisos(cur, doble, ahora=AHORA)
    conn.commit()
    with admin(conn) as cur:
        resumen = AA.despachar_avisos(cur, doble, ahora=AHORA)
    conn.commit()

    assert resumen == {"reconciliados": 0, "enviados": 0, "fallidos": 0}
    assert len(doble.enviados) == 1


def test_despachar_avisos_a_administrador_nuevo_no_repite_a_los_ya_entregados(
        conn, intake_world, monkeypatch):
    """Un administrador que se suma después recibe los avisos existentes;
    a quien ya se le entregó no se le vuelve a mandar el mismo."""
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    ws = intake_world["north-lab"]["id"]
    _, tg_a = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    _crear_aviso(conn, ws)

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        AA.despachar_avisos(cur, doble, ahora=AHORA)
    conn.commit()
    assert len(doble.enviados) == 1

    _, tg_b = _hacer_administrador(conn, intake_world, "north-lab", "Taylor Quinn")
    with admin(conn) as cur:
        resumen = AA.despachar_avisos(cur, doble, ahora=AHORA)
    conn.commit()

    assert resumen["enviados"] == 1
    assert {e.chat_id for e in doble.enviados} == {tg_a, tg_b}


def test_reconciliar_entregas_no_crea_para_avisos_ya_resueltos(
        conn, intake_world, monkeypatch):
    """G1d-a2, ítem 3: la reconciliación no recorre toda la historia --
    sólo avisos no resueltos. Uno ya resuelto nunca recibe una entrega
    nueva, aunque siga existiendo."""
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    ws = intake_world["north-lab"]["id"]
    admin_id, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    resuelto_id = _crear_aviso(conn, ws, texto="ya resuelto")
    abierto_id = _crear_aviso(
        conn, ws, tipo="correo_sin_emisor", texto="todavía abierto")
    with admin(conn) as cur:
        AC.marcar_resuelto(cur, resuelto_id, admin_id, ahora=AHORA)
    conn.commit()

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        resumen = AA.despachar_avisos(cur, doble, ahora=AHORA)
    conn.commit()

    assert resumen["reconciliados"] == 1
    with admin(conn) as cur:
        cur.execute(
            "select aviso_id from aviso_administrativo_entrega")
        assert [str(f["aviso_id"]) for f in cur.fetchall()] == [abierto_id]


def test_administrador_nuevo_recibe_avisos_leidos_pero_no_resueltos(
        conn, intake_world, monkeypatch):
    """G1d-a2, ítem 3: leído no es resuelto -- un administrador que se suma
    después sigue recibiendo un aviso que otro administrador ya marcó
    leído, mientras siga sin resolverse."""
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    ws = intake_world["north-lab"]["id"]
    admin_a, tg_a = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _crear_aviso(conn, ws)
    with admin(conn) as cur:
        AA.despachar_avisos(cur, TransporteDePrueba(), ahora=AHORA)
        AC.marcar_leido(cur, aviso_id, admin_a, ahora=AHORA)
    conn.commit()

    admin_b, tg_b = _hacer_administrador(conn, intake_world, "north-lab", "Taylor Quinn")
    doble = TransporteDePrueba()
    with admin(conn) as cur:
        resumen = AA.despachar_avisos(cur, doble, ahora=AHORA)
    conn.commit()

    # `admin_a` ya tenía su entrega desde antes de leerlo; sólo `admin_b`
    # es nuevo acá, y el aviso leído (no resuelto) también cuenta para él.
    assert resumen["reconciliados"] == 1
    assert resumen["enviados"] == 1
    with admin(conn) as cur:
        cur.execute(
            "select app_user_id from aviso_administrativo_entrega "
            "where aviso_id = %s", (aviso_id,))
        entregados = {str(f["app_user_id"]) for f in cur.fetchall()}
    assert entregados == {admin_a, admin_b}
    assert {e.chat_id for e in doble.enviados} == {tg_b}


def test_despachar_avisos_sin_administrador_deja_incidente_y_no_revienta(
        conn, intake_world, monkeypatch):
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    ws = intake_world["north-lab"]["id"]
    _crear_aviso(conn, ws)

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        resumen = AA.despachar_avisos(cur, doble, ahora=AHORA)
    conn.commit()

    assert resumen == {"reconciliados": 0, "enviados": 0, "fallidos": 0}
    assert doble.enviados == []
    with admin(conn) as cur:
        cur.execute("select count(*) n from aviso_administrativo_entrega")
        assert cur.fetchone()["n"] == 0
        cur.execute(
            "select resumen_sanitizado from incident where workspace_id is null")
        [incidente] = cur.fetchall()
        assert "administrador" in incidente["resumen_sanitizado"]


def test_despachar_avisos_sin_administrador_deja_un_solo_incidente_por_causa(
        conn, intake_world, monkeypatch):
    """Mientras la condición no se resuelva, correr esto muchas veces
    (cada vuelta del loop que despacha) no deja un incidente nuevo por
    vuelta -- uno solo, hasta que se resuelva."""
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    ws = intake_world["north-lab"]["id"]
    _crear_aviso(conn, ws)

    doble = TransporteDePrueba()
    for _ in range(3):
        with admin(conn) as cur:
            AA.despachar_avisos(cur, doble, ahora=AHORA)
        conn.commit()

    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id is null")
        assert cur.fetchone()["n"] == 1


def test_incidente_plataforma_persistente_uno_nuevo_pasada_la_ventana(
        conn, intake_world, monkeypatch):
    """G1d-a2, ítem 4: `incident` no tiene estado de "resuelto", así que la
    deduplicación usa una ventana de tiempo
    (`AA.VENTANA_DEDUPE_INCIDENTE_PLATAFORMA`). Si el problema sigue (o
    volvió) después de la ventana, se registra un incidente nuevo -- nunca
    fallar en silencio dejando la condición sin ningún rastro nuevo."""
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    ws = intake_world["north-lab"]["id"]
    _crear_aviso(conn, ws)

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        AA.despachar_avisos(cur, doble, ahora=AHORA)
    conn.commit()

    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id is null")
        assert cur.fetchone()["n"] == 1

    despues = AHORA + AA.VENTANA_DEDUPE_INCIDENTE_PLATAFORMA + timedelta(minutes=1)
    with admin(conn) as cur:
        AA.despachar_avisos(cur, doble, ahora=despues)
    conn.commit()

    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id is null")
        assert cur.fetchone()["n"] == 2


def test_incidente_plataforma_persistente_concurrente_no_duplica(
        conn, intake_world, uri):
    """G1d-a2, ítem 4: dos vueltas del loop que evalúan la MISMA causa casi
    al mismo tiempo, desde conexiones distintas, no pueden las dos ver "no
    hay ninguno reciente" antes de que ninguna inserte -- el candado
    transaccional por causa exacta las serializa."""
    resumen = "causa de prueba concurrente"

    barrier = threading.Barrier(2, timeout=30)
    outcomes: list[str] = []
    failures: list[Exception] = []

    def registrar() -> None:
        other = None
        try:
            other = conectar(uri)
            with admin(other) as cur:
                barrier.wait()
                AA._incidente_plataforma_persistente(cur, resumen, AHORA)
            other.commit()
            outcomes.append("ok")
        except Exception as exc:  # noqa: BLE001 -- justo lo que se prueba que no pase
            failures.append(exc)
            barrier.abort()
            if other is not None:
                other.rollback()
        finally:
            if other is not None:
                other.close()

    threads = [threading.Thread(target=registrar) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert not any(thread.is_alive() for thread in threads), "un hilo quedó colgado"

    assert failures == [], [type(e).__name__ for e in failures]
    assert outcomes == ["ok", "ok"]

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from incident "
            "where workspace_id is null and resumen_sanitizado = %s", (resumen,))
        assert cur.fetchone()["n"] == 1


def test_despachar_avisos_sin_token_deja_incidente_y_no_revienta(
        conn, intake_world, monkeypatch):
    monkeypatch.delenv("PRISMA_BOT_TOKEN_ADMIN", raising=False)
    ws = intake_world["north-lab"]["id"]
    _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    _crear_aviso(conn, ws)

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        resumen = AA.despachar_avisos(cur, doble, ahora=AHORA)
    conn.commit()

    assert resumen["reconciliados"] == 1
    assert resumen["enviados"] == 0
    assert doble.enviados == []
    with admin(conn) as cur:
        cur.execute("select estado from aviso_administrativo_entrega")
        assert [f["estado"] for f in cur.fetchall()] == ["listo"]
        cur.execute(
            "select resumen_sanitizado from incident where workspace_id is null")
        [incidente] = cur.fetchall()
        assert "token" in incidente["resumen_sanitizado"]


def test_despachar_avisos_falla_de_transporte_reintenta_con_espera_creciente_y_agota(
        conn, intake_world, monkeypatch):
    """G1d-a2, ítem 2: después de una falla, la fila no se reintenta en la
    vuelta inmediatamente siguiente -- sólo pasada la espera creciente real
    (`AA._retraso_reintento`); agotados los `MAX_INTENTOS`, queda `fallido`
    con un solo incidente."""
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    ws = intake_world["north-lab"]["id"]
    _, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    _crear_aviso(conn, ws)

    doble = TransporteDePrueba(falla_en={tg})
    momento = AHORA
    for intento in range(1, AA.MAX_INTENTOS + 1):
        with admin(conn) as cur:
            resumen = AA.despachar_avisos(cur, doble, ahora=momento)
        conn.commit()
        reconciliados_esperados = 1 if intento == 1 else 0
        assert resumen == {
            "reconciliados": reconciliados_esperados, "enviados": 0, "fallidos": 1,
        }, intento

        # Inmediatamente después (mismo instante): todavía no toca reintentar.
        with admin(conn) as cur:
            resumen_inmediato = AA.despachar_avisos(cur, doble, ahora=momento)
        conn.commit()
        assert resumen_inmediato == {
            "reconciliados": 0, "enviados": 0, "fallidos": 0,
        }, intento

        momento = momento + AA._retraso_reintento(intento)

    with admin(conn) as cur:
        cur.execute(
            "select estado, intentos, proximo_intento_en "
            "from aviso_administrativo_entrega")
        [fila] = cur.fetchall()
        assert fila["estado"] == "fallido"
        assert fila["intentos"] == AA.MAX_INTENTOS
        assert fila["proximo_intento_en"] is None
        cur.execute(
            "select resumen_sanitizado from incident where workspace_id is null")
        [incidente] = cur.fetchall()
        assert "no se pudo entregar" in incidente["resumen_sanitizado"]

    # Ya agotado: ni pasado más tiempo se lo vuelve a intentar.
    with admin(conn) as cur:
        resumen = AA.despachar_avisos(
            cur, doble, ahora=momento + timedelta(hours=1))
    conn.commit()
    assert resumen == {"reconciliados": 0, "enviados": 0, "fallidos": 0}


def test_despachar_respuestas_falla_de_transporte_reintenta_con_espera_creciente(
        conn, intake_world, monkeypatch):
    """G1d-a2, ítem 2: mismo backoff real para
    `aviso_administrativo_respuesta`."""
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    admin_id, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")

    with admin(conn) as cur:
        AA.responder_texto_libre(cur, tg, 1, ahora=AHORA)

    doble = TransporteDePrueba(falla_en={tg})
    with admin(conn) as cur:
        resumen = AA.despachar_respuestas(cur, doble, ahora=AHORA)
    conn.commit()
    assert resumen == {"enviados": 0, "fallidos": 1}

    # Mismo instante: todavía no toca reintentar.
    with admin(conn) as cur:
        resumen_inmediato = AA.despachar_respuestas(cur, doble, ahora=AHORA)
    conn.commit()
    assert resumen_inmediato == {"enviados": 0, "fallidos": 0}

    # Pasada la espera del primer intento, sí se reintenta.
    momento = AHORA + AA._retraso_reintento(1)
    doble.falla_en.clear()
    with admin(conn) as cur:
        resumen = AA.despachar_respuestas(cur, doble, ahora=momento)
    conn.commit()
    assert resumen == {"enviados": 1, "fallidos": 0}


# ===========================================================================
# B2. Una sola definición de "administrador con Telegram" (G1d-a3, ítem 3)
# ===========================================================================


def test_administrador_sin_telegram_no_recibe_ni_cuenta_disponible(
        conn, intake_world, monkeypatch):
    """`_admins_con_telegram` (despachar) y `_reconciliar_entregas` tienen
    que coincidir sobre quién cuenta como "administrador con Telegram" --
    antes cada uno tenía su propio filtro repetido en SQL. Un administrador
    sin Telegram vinculado nunca aparece en `_admins_con_telegram` ni recibe
    una fila de entrega, y `despachar_avisos` lo trata igual que "no hay
    ningún administrador disponible" (incidente de plataforma, nunca una
    entrega fantasma)."""
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    ws = intake_world["north-lab"]["id"]
    _hacer_administrador_sin_telegram(conn)
    _crear_aviso(conn, ws)

    with admin(conn) as cur:
        admins = AA._admins_con_telegram(cur)
    assert admins == []

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        resumen = AA.despachar_avisos(cur, doble, ahora=AHORA)
    conn.commit()

    assert resumen == {"reconciliados": 0, "enviados": 0, "fallidos": 0}
    assert doble.enviados == []
    with admin(conn) as cur:
        cur.execute("select count(*) n from aviso_administrativo_entrega")
        assert cur.fetchone()["n"] == 0
        cur.execute(
            "select resumen_sanitizado from incident where workspace_id is null")
        [incidente] = cur.fetchall()
        assert "administrador" in incidente["resumen_sanitizado"]


def test_administrador_sin_telegram_conviviendo_con_uno_con_telegram(
        conn, intake_world, monkeypatch):
    """Con un administrador sin Telegram y otro con Telegram vinculado, sólo
    el segundo cuenta y recibe la entrega -- el primero nunca aparece en
    `_admins_con_telegram` ni en `aviso_administrativo_entrega`."""
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    ws = intake_world["north-lab"]["id"]
    sin_telegram = _hacer_administrador_sin_telegram(conn)
    con_telegram, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    _crear_aviso(conn, ws)

    with admin(conn) as cur:
        admins = AA._admins_con_telegram(cur)
    assert [str(a["app_user_id"]) for a in admins] == [con_telegram]

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        resumen = AA.despachar_avisos(cur, doble, ahora=AHORA)
    conn.commit()

    assert resumen["reconciliados"] == 1
    with admin(conn) as cur:
        cur.execute("select app_user_id from aviso_administrativo_entrega")
        assert [str(f["app_user_id"]) for f in cur.fetchall()] == [con_telegram]


# ===========================================================================
# C. Marcar leído / texto libre -- encolan la respuesta puntual
# ===========================================================================


def test_marcar_leido_por_toque_marca_el_aviso_y_encola_confirmacion(
        conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    admin_id, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _crear_aviso(conn, ws)

    with admin(conn) as cur:
        AA.marcar_leido_por_toque(cur, aviso_id, admin_id, tg, ahora=AHORA)
    conn.commit()

    with admin(conn) as cur:
        [aviso] = AC.avisos(cur)
        assert aviso["leido_en"] is not None
        assert str(aviso["leido_por"]) == admin_id
        assert aviso["resuelto_en"] is None

        cur.execute(
            "select chat_id, texto from aviso_administrativo_respuesta")
        [fila] = cur.fetchall()
        assert fila["chat_id"] == tg
        assert fila["texto"] == AA.TEXTO_MARCADO_LEIDO


def test_marcar_leido_por_toque_repetido_no_duplica_la_confirmacion(
        conn, intake_world):
    """Un botón viejo tocado dos veces (doble tap, reintento de Telegram)
    no encola dos confirmaciones -- `on conflict do nothing` sobre la
    clave de dedupe."""
    ws = intake_world["north-lab"]["id"]
    admin_id, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _crear_aviso(conn, ws)

    with admin(conn) as cur:
        AA.marcar_leido_por_toque(cur, aviso_id, admin_id, tg, ahora=AHORA)
        AA.marcar_leido_por_toque(cur, aviso_id, admin_id, tg, ahora=AHORA)
    conn.commit()

    with admin(conn) as cur:
        cur.execute("select count(*) n from aviso_administrativo_respuesta")
        assert cur.fetchone()["n"] == 1


def test_responder_texto_libre_encola_la_guia(conn, intake_world):
    admin_id, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")

    with admin(conn) as cur:
        AA.responder_texto_libre(cur, tg, 42, ahora=AHORA)
    conn.commit()

    with admin(conn) as cur:
        cur.execute("select chat_id, texto from aviso_administrativo_respuesta")
        [fila] = cur.fetchall()
        assert fila["chat_id"] == tg
        assert fila["texto"] == AA.TEXTO_ACCION_LIBRE


# ===========================================================================
# D. `despachar_respuestas`
# ===========================================================================


def test_despachar_respuestas_entrega_lo_encolado(conn, intake_world, monkeypatch):
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    admin_id, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")

    with admin(conn) as cur:
        AA.responder_texto_libre(cur, tg, 1, ahora=AHORA)

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        resumen = AA.despachar_respuestas(cur, doble, ahora=AHORA)
    conn.commit()

    assert resumen == {"enviados": 1, "fallidos": 0}
    [entrega] = doble.enviados
    assert entrega.chat_id == tg
    assert entrega.texto == AA.TEXTO_ACCION_LIBRE


def test_despachar_respuestas_sin_token_deja_incidente_y_no_revienta(
        conn, intake_world, monkeypatch):
    monkeypatch.delenv("PRISMA_BOT_TOKEN_ADMIN", raising=False)
    admin_id, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")

    with admin(conn) as cur:
        AA.responder_texto_libre(cur, tg, 1, ahora=AHORA)

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        resumen = AA.despachar_respuestas(cur, doble, ahora=AHORA)
    conn.commit()

    assert resumen == {"enviados": 0, "fallidos": 0}
    with admin(conn) as cur:
        cur.execute("select estado from aviso_administrativo_respuesta")
        assert [f["estado"] for f in cur.fetchall()] == ["listo"]
        cur.execute(
            "select resumen_sanitizado from incident where workspace_id is null")
        [incidente] = cur.fetchall()
        assert "token" in incidente["resumen_sanitizado"]


def test_despachar_todo_hace_las_dos_cosas(conn, intake_world, monkeypatch):
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    ws = intake_world["north-lab"]["id"]
    admin_id, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    _crear_aviso(conn, ws)
    with admin(conn) as cur:
        AA.responder_texto_libre(cur, tg, 1, ahora=AHORA)

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        resumen = AA.despachar_todo(cur, doble, ahora=AHORA)
    conn.commit()

    assert resumen["avisos"]["enviados"] == 1
    assert resumen["respuestas"]["enviados"] == 1
    assert len(doble.enviados) == 2


# ===========================================================================
# E. Webhook del bot de administración -- `gateway._procesar_admin`/`_toque_admin`
# ===========================================================================


def test_toque_marcar_leido_revalida_administrador_y_encola_confirmacion(
        cliente_admin, conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    admin_id, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _crear_aviso(conn, ws)

    r = _post_admin_toque(cliente_admin, AA.callback_data(AA.ACCION_LEIDO, aviso_id), tg)
    assert r.status_code == 200

    with admin(conn) as cur:
        [aviso] = AC.avisos(cur)
        assert aviso["leido_en"] is not None
        assert str(aviso["leido_por"]) == admin_id
        cur.execute("select texto from aviso_administrativo_respuesta")
        assert [f["texto"] for f in cur.fetchall()] == [AA.TEXTO_MARCADO_LEIDO]


def test_toque_marcar_leido_de_un_no_administrador_no_hace_nada(
        cliente_admin, conn, intake_world):
    """"El canal manda" (`autoridad.py`): alguien que no es administrador
    de plataforma no puede marcar nada leído por acá, aunque conozca el id
    de un aviso real."""
    ws = intake_world["north-lab"]["id"]
    aviso_id = _crear_aviso(conn, ws)
    ajeno = intake_world["north-lab"]["people"]["Sam North"]["telegram"]

    r = _post_admin_toque(cliente_admin, AA.callback_data(AA.ACCION_LEIDO, aviso_id), ajeno)
    assert r.status_code == 200

    with admin(conn) as cur:
        [aviso] = AC.avisos(cur)
        assert aviso["leido_en"] is None
        cur.execute("select count(*) n from aviso_administrativo_respuesta")
        assert cur.fetchone()["n"] == 0


def test_texto_libre_de_administrador_encola_la_guia_breve(
        cliente_admin, conn, intake_world):
    admin_id, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")

    r = _post_admin_texto(cliente_admin, "quiero reenviar el correo de Sam", tg)
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select texto from aviso_administrativo_respuesta")
        assert [f["texto"] for f in cur.fetchall()] == [AA.TEXTO_ACCION_LIBRE]


def test_texto_libre_de_no_administrador_no_responde_nada(
        cliente_admin, conn, intake_world):
    """Mismo comportamiento de siempre: a un desconocido no se le explica
    por qué no se le responde."""
    ajeno = intake_world["north-lab"]["people"]["Sam North"]["telegram"]

    r = _post_admin_texto(cliente_admin, "hola", ajeno)
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select count(*) n from aviso_administrativo_respuesta")
        assert cur.fetchone()["n"] == 0
        cur.execute("select count(*) n from audit_log where accion = 'mensaje_admin'")
        assert cur.fetchone()["n"] == 0


def test_texto_libre_repetido_por_reintento_de_telegram_no_duplica_la_guia(
        cliente_admin, conn, intake_world):
    """El mismo `message_id` (Telegram reintentando el mismo update) no
    encola una segunda guía -- la clave de dedupe incluye el mensaje."""
    admin_id, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")

    _post_admin_texto(cliente_admin, "hola", tg, message_id=7)
    _post_admin_texto(cliente_admin, "hola de nuevo", tg, message_id=7)

    with admin(conn) as cur:
        cur.execute("select count(*) n from aviso_administrativo_respuesta")
        assert cur.fetchone()["n"] == 1


# ===========================================================================
# F. Contención del despacho administrativo (G1d-a2, ítem 1)
# ===========================================================================


def test_tareas_de_fondo_contiene_una_falla_del_despacho_administrativo(
        conn, intake_world, monkeypatch):
    """Si el despacho de avisos administrativos revienta, el despacho del
    espacio -- que ya corrió en la misma vuelta -- no se pierde, la
    conexión compartida sigue usable (nunca queda en transacción abortada),
    y queda un incidente saneado -- nunca frena el ciclo que sigue
    escuchando updates (`local.Escucha.una_vuelta`)."""
    from prisma.local import Escucha
    from prisma.salida import enqueue_outbox

    ws = intake_world["north-lab"]["id"]
    chat_id = intake_world["north-lab"]["people"]["Morgan Hale"]["telegram"]
    with espacio(conn, ws) as cur:
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=chat_id, text="hola",
            message_type="urgente", scheduled_for=AHORA,
            dedupe_key="prueba:contencion-g1d-a2", is_response=True)
    conn.commit()

    def _revienta(cur, ahora=None, lote=50):
        raise RuntimeError("boom")

    monkeypatch.setattr(AA, "despachar_todo", _revienta)

    escucha = Escucha(conn, "north-lab", ws, "prueba:token-espacio")
    escucha.transporte = TransporteDePrueba()

    resumen = escucha.tareas_de_fondo(ahora=AHORA)

    # El despacho del espacio sí ocurrió, en la misma vuelta.
    assert resumen["enviados"] == 1
    assert len(escucha.transporte.enviados) == 1

    # La conexión compartida sigue usable -- ninguna transacción abortada
    # colgando de la falla de arriba.
    with admin(conn) as cur:
        cur.execute("select 1")
        assert cur.fetchone() is not None

    # G1d-a3, ítem 2: el incidente ahora sale por el mismo camino
    # deduplicado que un incidente de plataforma persistente (`AA.
    # reportar_fallo_despacho` / `_incidente_plataforma_persistente`) -- la
    # tabla `incident` sí tiene una columna `etapa` (la usan `_registrar_
    # incidente` y `gateway._reportar_incidente_admin`), pero ESTE camino en
    # particular no la completa: la etapa queda identificable de todos
    # modos, dentro del resumen saneado. El mensaje crudo de la excepción
    # ("boom") nunca entra ahí -- sólo en `referencia_cruda`; la clave
    # exacta de deduplicación es `resumen_sanitizado`, no el detalle crudo.
    with admin(conn) as cur:
        cur.execute(
            "select resumen_sanitizado, referencia_cruda from incident "
            "where workspace_id is null")
        [incidente] = cur.fetchall()
        assert gateway.ETAPA_ADMIN_DESPACHO in incidente["resumen_sanitizado"]
        assert "boom" not in incidente["resumen_sanitizado"]
        assert "boom" in (incidente["referencia_cruda"] or "")


def test_tareas_de_fondo_con_falla_persistente_deja_un_solo_incidente_por_ventana(
        conn, intake_world, monkeypatch):
    """G1d-a3, ítem 2: mientras el despacho administrativo siga fallando,
    cada vuelta del loop (`local.Escucha.tareas_de_fondo`) no puede dejar un
    incidente nuevo -- antes, la contención de G1d-a2 llamaba directamente a
    `gateway._reportar_incidente_admin`, que inserta sin deduplicar, así que
    una falla que persiste por varias vueltas del loop dejaba un incidente
    por vuelta. Deduplicado con la misma ventana que un incidente de
    plataforma persistente, por etapa + tipo de error (`AA.
    VENTANA_DEDUPE_INCIDENTE_PLATAFORMA`)."""
    from prisma.local import Escucha

    ws = intake_world["north-lab"]["id"]

    def _revienta(cur, ahora=None, lote=50):
        raise RuntimeError("boom")

    monkeypatch.setattr(AA, "despachar_todo", _revienta)

    escucha = Escucha(conn, "north-lab", ws, "prueba:token-espacio")
    escucha.transporte = TransporteDePrueba()

    for _ in range(3):
        escucha.tareas_de_fondo(ahora=AHORA)

    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id is null")
        assert cur.fetchone()["n"] == 1

    # Pasada la ventana, si la condición sigue vigente, se registra uno
    # nuevo -- nunca fallar en silencio dejando la condición sin ningún
    # rastro nuevo.
    despues = AHORA + AA.VENTANA_DEDUPE_INCIDENTE_PLATAFORMA + timedelta(minutes=1)
    escucha.tareas_de_fondo(ahora=despues)

    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id is null")
        assert cur.fetchone()["n"] == 2


def test_despachar_cli_contiene_una_falla_del_despacho_administrativo(
        conn, intake_world, monkeypatch, uri):
    """G1d-a3, ítem 4: si el despacho de avisos administrativos revienta
    dentro de `python -m prisma despachar <espacio>`, lo del espacio que ya
    se despachó en la misma corrida sobrevive (se confirma), la conexión
    sigue usable, queda un solo incidente saneado -- y el comando nunca
    revienta ni deja de informar el código de salida de siempre."""
    from prisma import cli, despachador
    from prisma.salida import enqueue_outbox

    monkeypatch.setattr(cli, "conectar", lambda: conn)
    monkeypatch.setenv("PRISMA_BOT_TOKEN_NORTH-LAB", "prueba:token-espacio")
    ws = intake_world["north-lab"]["id"]
    chat_id = intake_world["north-lab"]["people"]["Morgan Hale"]["telegram"]
    # `cli.py despachar` no recibe `ahora`: usa el reloj real de la base
    # (`despachador.despachar` -> `datetime.now(timezone.utc)`), así que el
    # mensaje tiene que estar programado en el pasado real, nunca en la
    # fecha ficticia `AHORA` (2028) que usa el resto de este archivo.
    ya_paso = datetime.now(timezone.utc) - timedelta(minutes=1)
    with espacio(conn, ws) as cur:
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=chat_id, text="hola",
            message_type="urgente", scheduled_for=ya_paso,
            dedupe_key="prueba:contencion-cli-g1d-a3", is_response=True)
    conn.commit()

    doble = TransporteDePrueba()
    monkeypatch.setattr(despachador, "TransporteTelegram", lambda token: doble)

    def _revienta(cur, ahora=None, lote=50):
        raise RuntimeError("boom")

    monkeypatch.setattr(AA, "despachar_todo", _revienta)

    codigo = cli.main(["despachar", "north-lab"])

    assert codigo == 0
    # El despacho del espacio sí ocurrió, en la misma corrida.
    assert len(doble.enviados) == 1

    # La conexión sigue usable -- ninguna transacción abortada colgando.
    with admin(conn) as cur:
        cur.execute("select 1")
        assert cur.fetchone() is not None

    # Durable de verdad, no sólo visible dentro de la misma transacción
    # ambiente -- desde OTRA conexión, el mensaje del espacio ya quedó
    # marcado entregado y el incidente administrativo está ahí, sin espacio
    # propio (G1d-a3, ítem 2/4: el commit intermedio de `cli.py despachar`
    # antes del bloque de administración evita que el disparador
    # `derivar_espacio_registro` le pegue el `workspace_id` de esta corrida
    # al incidente de plataforma).
    other = conectar(uri)
    try:
        with admin(other) as cur:
            cur.execute(
                "select estado from message_outbox where dedupe_key = %s",
                ("prueba:contencion-cli-g1d-a3",))
            assert cur.fetchone()["estado"] == "enviado"
            cur.execute(
                "select resumen_sanitizado from incident where workspace_id is null")
            [incidente] = cur.fetchall()
            assert gateway.ETAPA_ADMIN_DESPACHO in incidente["resumen_sanitizado"]
            assert "boom" not in incidente["resumen_sanitizado"]
    finally:
        other.close()

    # Una segunda corrida, con la misma falla vigente, no deja un segundo
    # incidente (mismo mecanismo de deduplicación de ítem 2).
    codigo = cli.main(["despachar", "north-lab"])
    assert codigo == 0
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id is null")
        assert cur.fetchone()["n"] == 1


def test_reportar_fallo_despacho_deja_rastro_en_stderr_si_tambien_falla_el_registro(
        conn, monkeypatch, capsys):
    """Seguimiento de la revisión de G1d-a3: si ni el incidente se puede
    registrar, `reportar_fallo_despacho` no puede perderse en silencio
    total -- deja una línea saneada en stderr (nunca el mensaje crudo de la
    excepción original) y avisa con su valor de retorno, para que `cli.py`
    no diga "quedó registrado" sin que sea cierto. La conexión sigue
    usable después (nunca queda en transacción abortada)."""
    def _revienta(cur, resumen, ahora, referencia_cruda=None):
        raise RuntimeError("ni esto se pudo")

    monkeypatch.setattr(AA, "_incidente_plataforma_persistente", _revienta)
    # La conexión de la fixture arranca con una transacción implícita
    # abierta (el `set search_path` de `conectar()`, sin confirmar todavía)
    # -- se confirma acá para dejar el punto de partida limpio, como en
    # cualquier uso real (`local.py`/`cli.py` siempre llaman a esto ya sobre
    # una conexión recién confirmada).
    conn.commit()

    aplicado = AA.reportar_fallo_despacho(
        conn, RuntimeError("boom"), "admin_despacho", ahora=AHORA)

    assert aplicado is False
    salida = capsys.readouterr().err
    assert "admin_despacho" in salida
    assert "RuntimeError" in salida
    assert "boom" not in salida        # nunca el mensaje crudo de la excepción original

    with admin(conn) as cur:
        cur.execute("select 1")
        assert cur.fetchone() is not None


def test_cli_despachar_no_dice_quedo_registrado_si_tampoco_se_pudo_registrar(
        conn, intake_world, monkeypatch, uri, capsys):
    """`cli.py despachar` sólo dice "quedó registrado" cuando
    `reportar_fallo_despacho` de verdad lo logró -- con la doble falla,
    dice la verdad."""
    from prisma import cli, despachador

    monkeypatch.setattr(cli, "conectar", lambda: conn)
    monkeypatch.setenv("PRISMA_BOT_TOKEN_NORTH-LAB", "prueba:token-espacio")
    ws = intake_world["north-lab"]["id"]

    def _revienta_despacho(cur, ahora=None, lote=50):
        raise RuntimeError("boom")

    def _revienta_tambien_el_registro(conn_, error, etapa, *, ahora=None):
        return False

    monkeypatch.setattr(AA, "despachar_todo", _revienta_despacho)
    monkeypatch.setattr(AA, "reportar_fallo_despacho", _revienta_tambien_el_registro)

    codigo = cli.main(["despachar", "north-lab"])

    assert codigo == 0
    salida = capsys.readouterr().out
    assert "quedó registrado" not in salida
    assert "tampoco se pudo registrar" in salida


