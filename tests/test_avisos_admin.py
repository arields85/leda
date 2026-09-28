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

    with admin(conn) as cur:
        cur.execute(
            "select resumen_sanitizado, referencia_cruda, etapa from incident "
            "where workspace_id is null")
        [incidente] = cur.fetchall()
        assert incidente["etapa"] == gateway.ETAPA_ADMIN_DESPACHO
        assert "boom" not in incidente["resumen_sanitizado"]
        assert "boom" in (incidente["referencia_cruda"] or "")
