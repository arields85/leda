"""Entrega de avisos "🛠️ Administración" por el bot de administración
(rama auxiliar, G1d).

`message_outbox` exige `workspace_id` y se despacha por el bot de cada
espacio; estas pruebas ejercitan el camino de salida propio del bot de
administración (`avisos_admin.py`) directo contra la base, con el doble de
transporte que ya usa `despachador.py` -- nunca Telegram real.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import alta_correo as AC
from prisma import avisos_admin as AA
from prisma import gateway
from prisma.db import admin, espacio
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


def test_despachar_avisos_falla_de_transporte_reintenta_y_agota(
        conn, intake_world, monkeypatch):
    monkeypatch.setenv("PRISMA_BOT_TOKEN_ADMIN", "prueba:token-admin")
    ws = intake_world["north-lab"]["id"]
    _, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    _crear_aviso(conn, ws)

    doble = TransporteDePrueba(falla_en={tg})
    for _ in range(5):
        with admin(conn) as cur:
            resumen = AA.despachar_avisos(cur, doble, ahora=AHORA)
        conn.commit()
        assert resumen["fallidos"] == 1

    with admin(conn) as cur:
        cur.execute(
            "select estado, intentos from aviso_administrativo_entrega")
        [fila] = cur.fetchall()
        assert fila["estado"] == "fallido"
        assert fila["intentos"] == 5
        cur.execute(
            "select resumen_sanitizado from incident where workspace_id is null")
        [incidente] = cur.fetchall()
        assert "no se pudo entregar" in incidente["resumen_sanitizado"]

    # Ya agotado: una sexta vuelta no lo vuelve a intentar.
    with admin(conn) as cur:
        resumen = AA.despachar_avisos(cur, doble, ahora=AHORA)
    conn.commit()
    assert resumen == {"reconciliados": 0, "enviados": 0, "fallidos": 0}


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
