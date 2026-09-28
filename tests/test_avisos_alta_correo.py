"""Avisos "🛠️ Administración" del alta con correo (rama auxiliar, G1d).

Unificado con T28 (decisión del usuario, 2026-09-28): este módulo ya no tiene
su propia cola de salida del bot de administración. El fan-out de un aviso a
TODOS los administradores alcanzables entrega por `admin_notice`, la misma
cola que usa `incidentes.avisar_incidente_admin`
(`tests/test_avisos_admin.py` cubre esa mitad, genérica a cualquier fila sin
importar su origen: reintentos, backoff, qué pasa si se agotan, sin token,
sin ningún administrador alcanzable). Una respuesta puntual a UN
administrador (confirmación de un botón, guía de texto libre) entrega por
`admin_reply`, aparte a propósito -- ver el comentario de tabla en
`db/esquema.sql` para el porqué. Estas pruebas cubren lo que es propio de
este módulo: los botones de cada tipo de aviso, el recorrido de "Habilitar
un nuevo intento" (G1d-b, acción F), el fan-out de UN aviso administrativo
(`avisar_aviso_administrativo`) y su reconciliación contra administradores
que se vuelven alcanzables después de creado
(`reconciliar_avisos_admin_notice`), y el webhook del bot de administración
(`gateway._procesar_admin`/`_toque_admin`).
"""

from __future__ import annotations

import dataclasses
import threading
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import alta_correo as AC
from prisma import alta_correo_flujo as ACF
from prisma import avisos_admin as AA
from prisma import despachador, gateway
from prisma.db import admin, conectar, espacio, registrar_auditoria
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


def _post_admin_toque(cliente_admin, callback, user_id, chat_id=None, toque_id="cb1"):
    """`toque_id` (G1d-b2, ítem 6) simula el `callback_query.id` real de
    Telegram: el mismo valor en dos llamadas simula una redelivery exacta
    del mismo webhook (una sola respuesta esperada); valores distintos
    simulan dos toques genuinos distintos (una respuesta cada uno)."""
    return cliente_admin.post(
        "/telegram/admin",
        json={"callback_query": {"id": toque_id, "data": callback,
                                 "from": {"id": user_id},
                                 "message": {"chat": {"id": chat_id or user_id}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _hacer_administrador(conn, intake_world, workspace_key: str, persona: str) -> tuple[str, int]:
    """Da rol de plataforma `administrador` a alguien que ya tiene Telegram
    vinculado (por `intake_world`) Y deja constancia de que ya le escribió
    al bot de administración (`audit_log`, `accion='mensaje_admin'`) --
    unificación con T28 (decisión del usuario, 2026-09-28): "alcanzable" para
    `avisar_aviso_administrativo_admin` es exactamente lo mismo que para
    `avisar_incidente_admin` (`tests/test_avisos_admin.py`, `_administrador`):
    haberle escrito al bot de administración alguna vez, no sólo tener
    Telegram vinculado. Devuelve `(app_user_id, telegram_user_id)`."""
    datos = intake_world[workspace_key]["people"][persona]
    with admin(conn) as cur:
        cur.execute(
            "insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
            (datos["app_user_id"],))
        registrar_auditoria(
            cur, accion="mensaje_admin", actor_app_user_id=datos["app_user_id"],
            actor_kind="persona", detalle={"chat_id": datos["telegram"]})
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
    """Deja una membresía en `pending_email_verification` con el cupo de 5
    envíos del ciclo REALMENTE agotado, y el aviso `correo_limite_agotado`
    ya creado -- el escenario de partida de "Habilitar un nuevo intento"
    (G1d-b, acción F).

    Los 5 envíos van espaciados más de una hora entre sí para no chocar con
    el límite de 3/hora (mismo patrón que
    `test_habilitar_intento_reabre_el_cupo_de_cinco_del_ciclo`,
    `test_alta_correo.py`)."""
    with espacio(conn, ws) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        for i in range(5):
            instante = AHORA + timedelta(hours=2 * i)
            resultado = AC.emitir_verificacion(
                cur, m, correo, f"token-agotado-{i}", ahora=instante)
            assert resultado.ok, resultado.motivo
        aviso_id = AC.crear_aviso(
            cur, AC.TIPO_CORREO_LIMITE_AGOTADO,
            f"{nombre} agotó los 5 envíos del correo de verificación.",
            referencia_tipo="membership", referencia_id=m, ahora=AHORA)
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
# B. Fan-out y reconciliación -- `avisar_aviso_administrativo`,
# `reconciliar_avisos_admin_notice` (unificado con T28: `admin_notice`,
# nunca una cola propia)
# ===========================================================================


def test_avisar_aviso_administrativo_encola_uno_por_administrador_alcanzable(
        conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    _, tg_a = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    _, tg_b = _hacer_administrador(conn, intake_world, "north-lab", "Taylor Quinn")
    aviso_id = _crear_aviso(conn, ws)

    with admin(conn) as cur:
        avisados = AA.avisar_aviso_administrativo(cur, aviso_id, ahora=AHORA)
    conn.commit()

    assert len(avisados) == 2
    with admin(conn) as cur:
        cur.execute(
            "select chat_id, cuerpo, botones from admin_notice "
            "where aviso_administrativo_id = %s order by chat_id", (aviso_id,))
        filas = cur.fetchall()
    assert {f["chat_id"] for f in filas} == {tg_a, tg_b}
    [fila] = [f for f in filas if f["chat_id"] == tg_a]
    assert fila["cuerpo"].startswith("🛠️ Administración · North Lab")
    assert "3 integrantes todavía no dieron su correo." in fila["cuerpo"]
    assert [b["etiqueta"] for b in fila["botones"]] == [AA.ETIQUETA_MARCAR_LEIDO]


def test_avisar_aviso_administrativo_de_envios_agotados_incluye_habilitar(
        conn, intake_world):
    """F (textos aprobados por el usuario, 2026-09-28): este tipo de aviso
    suma "Habilitar un nuevo intento" -- el resto sigue sólo con "Marcar
    leído" (prueba de arriba)."""
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")

    with admin(conn) as cur:
        AA.avisar_aviso_administrativo(cur, aviso_id, ahora=AHORA)
        cur.execute(
            "select botones from admin_notice where aviso_administrativo_id = %s",
            (aviso_id,))
        [fila] = cur.fetchall()
    conn.commit()

    assert [b["etiqueta"] for b in fila["botones"]] == [
        AA.ETIQUETA_HABILITAR, AA.ETIQUETA_MARCAR_LEIDO]


def test_avisar_aviso_administrativo_no_duplica_al_repetirse(conn, intake_world):
    """Correr el fan-out dos veces sobre el mismo aviso (dos vueltas del
    despacho, o la reconciliación encontrándolo de nuevo) no le duplica el
    aviso a nadie -- dedupe por `(aviso, administrador)`."""
    ws = intake_world["north-lab"]["id"]
    _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _crear_aviso(conn, ws)

    with admin(conn) as cur:
        primero = AA.avisar_aviso_administrativo(cur, aviso_id, ahora=AHORA)
        segundo = AA.avisar_aviso_administrativo(cur, aviso_id, ahora=AHORA)
    conn.commit()

    assert len(primero) == 1
    assert segundo == []
    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from admin_notice where aviso_administrativo_id = %s",
            (aviso_id,))
        assert cur.fetchone()["n"] == 1


def test_avisar_aviso_administrativo_resuelto_no_encola_nada(conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    admin_id, _ = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _crear_aviso(conn, ws)
    with admin(conn) as cur:
        AC.marcar_resuelto(cur, aviso_id, admin_id, ahora=AHORA)
    conn.commit()

    with admin(conn) as cur:
        avisados = AA.avisar_aviso_administrativo(cur, aviso_id, ahora=AHORA)
    conn.commit()

    assert avisados == []
    with admin(conn) as cur:
        cur.execute("select count(*) n from admin_notice")
        assert cur.fetchone()["n"] == 0


def test_avisar_aviso_administrativo_sin_ningun_administrador_alcanzable_no_rompe(
        conn, intake_world):
    """Nadie le escribió todavía al bot de administración (o no hay ningún
    administrador de plataforma): no se encola nada y no revienta -- el
    aviso sigue abierto para cuando alguien se vuelva alcanzable
    (`reconciliar_avisos_admin_notice`)."""
    ws = intake_world["north-lab"]["id"]
    aviso_id = _crear_aviso(conn, ws)

    with admin(conn) as cur:
        avisados = AA.avisar_aviso_administrativo(cur, aviso_id, ahora=AHORA)
    conn.commit()

    assert avisados == []


def test_reconciliar_avisos_admin_notice_alcanza_a_un_administrador_nuevo(
        conn, intake_world):
    """Un administrador que se vuelve alcanzable DESPUÉS de creado el aviso
    también lo recibe -- mismo papel que cumplía `_reconciliar_entregas`
    antes de esta unificación, ahora sobre `admin_reply`."""
    ws = intake_world["north-lab"]["id"]
    aviso_id = _crear_aviso(conn, ws)
    _, tg_a = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")

    with admin(conn) as cur:
        total = AA.reconciliar_avisos_admin_notice(cur, ahora=AHORA)
    conn.commit()
    assert total == 1

    _, tg_b = _hacer_administrador(conn, intake_world, "north-lab", "Taylor Quinn")
    with admin(conn) as cur:
        total = AA.reconciliar_avisos_admin_notice(cur, ahora=AHORA)
    conn.commit()

    assert total == 1  # sólo el administrador nuevo, nunca el ya avisado de nuevo
    with admin(conn) as cur:
        cur.execute(
            "select chat_id from admin_notice where aviso_administrativo_id = %s",
            (aviso_id,))
        assert {f["chat_id"] for f in cur.fetchall()} == {tg_a, tg_b}


def test_reconciliar_avisos_admin_notice_ignora_los_ya_resueltos(conn, intake_world):
    """G1d-a2, ítem 3 (heredado): la reconciliación no recorre toda la
    historia -- sólo avisos no resueltos. Uno ya resuelto nunca recibe un
    aviso nuevo, aunque siga existiendo."""
    ws = intake_world["north-lab"]["id"]
    admin_id, _ = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    resuelto_id = _crear_aviso(conn, ws, texto="ya resuelto")
    abierto_id = _crear_aviso(conn, ws, tipo="correo_sin_emisor", texto="todavía abierto")
    with admin(conn) as cur:
        AC.marcar_resuelto(cur, resuelto_id, admin_id, ahora=AHORA)
    conn.commit()

    with admin(conn) as cur:
        AA.reconciliar_avisos_admin_notice(cur, ahora=AHORA)
        cur.execute("select aviso_administrativo_id from admin_notice")
        assert [str(f["aviso_administrativo_id"]) for f in cur.fetchall()] == [abierto_id]
    conn.commit()


def test_despachar_avisos_admin_entrega_un_aviso_administrativo_con_sus_botones(
        conn, intake_world):
    """`despachador.despachar_avisos_admin` es el único despacho hacia la
    administración -- entrega tanto avisos de incidente (`botones=null`, ya
    cubierto en `tests/test_avisos_admin.py`) como avisos "🛠️
    Administración", con los botones que les correspondan."""
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        AA.reconciliar_avisos_admin_notice(cur, ahora=AHORA)
        despachador.despachar_avisos_admin(cur, doble, ahora=AHORA)
    conn.commit()

    [entrega] = doble.enviados
    assert entrega.texto.startswith("🛠️ Administración · North Lab")
    assert [b.etiqueta for b in entrega.botones] == [
        AA.ETIQUETA_HABILITAR, AA.ETIQUETA_MARCAR_LEIDO]


# ===========================================================================
# C. G1d-b/F: "Habilitar un nuevo intento" sobre el aviso de envíos agotados
# ===========================================================================


def test_aviso_de_limite_agotado_trae_habilitar_y_marcar_leido(
        conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")

    doble = TransporteDePrueba()
    with admin(conn) as cur:
        AA.reconciliar_avisos_admin_notice(cur, ahora=AHORA)
        despachador.despachar_avisos_admin(cur, doble, ahora=AHORA)
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
        cur.execute("select cuerpo, botones from admin_reply")
        [fila] = cur.fetchall()
        assert "Taylor Quinn" in fila["cuerpo"]
        assert "@" not in fila["cuerpo"]       # nunca el correo -- administración no lo necesita
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
        cur.execute("select cuerpo, botones from admin_reply")
        [fila] = cur.fetchall()
        assert fila["cuerpo"] == AA.TEXTO_HABILITAR_YA_RESUELTO
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
        cur.execute("select cuerpo from admin_reply where chat_id = %s",
                   (tg_admin,))
        assert [f["cuerpo"] for f in cur.fetchall()] == [AA.TEXTO_HABILITAR_CONFIRMADO]

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
    _, tg_admin = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
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
        cur.execute("select cuerpo from admin_reply where chat_id = %s",
                   (tg_admin,))
        assert [f["cuerpo"] for f in cur.fetchall()] == [AA.TEXTO_HABILITAR_CONFIRMADO]
    with espacio(conn, ws) as cur:
        cur.execute("select count(*) n from message_outbox where chat_id = %s", (tg_persona,))
        assert cur.fetchone()["n"] == 1


def test_confirmar_habilitar_sin_poder_avisar_a_la_persona_no_resuelve_ni_aplica(
        cliente_admin, conn, intake_world):
    """Nunca fallar en silencio: si la persona no se puede avisar (sin
    Telegram vinculado), no se aplica el intento ni se resuelve el aviso, el
    administrador recibe el aviso neutral -- nunca "Listo, habilitado."
    cuando a la persona no le va a llegar nada -- y el incidente sale por
    `incidentes.registrar_incidente` (único punto de escritura en
    `incident`, unificación con T28)."""
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
        cur.execute("select cuerpo from admin_reply where chat_id = %s",
                   (tg_admin,))
        assert [f["cuerpo"] for f in cur.fetchall()] == [gateway.NOTICIA_NEUTRA_INCIDENTE]
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
            assert (AA.confirmar_habilitar(cur, aviso_id, admin_id, ahora=AHORA)
                    == AA.RESULTADO_HABILITAR_APLICADO)
            # La primera sigue abierta: la segunda arranca mientras tanto.
            hilo.start()
            hilo.join(timeout=1)
            # G1d-b2, ítem 7: comprueba que el candado REALMENTE bloqueó a
            # la segunda (no que, por casualidad de scheduling, corrió
            # después) -- mientras la transacción de la primera sigue
            # abierta, el hilo de la segunda tiene que seguir vivo, esperando.
            assert hilo.is_alive(), "la segunda confirmación no se bloqueó: falta el candado"
        primera.commit()
    finally:
        primera.close()
    hilo.join(timeout=30)
    assert not hilo.is_alive(), "la segunda confirmación quedó colgada"

    assert errores == []
    assert resultado_segunda == [AA.RESULTADO_HABILITAR_YA_RESUELTO]

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from alta_correo_evento "
            "where membership_id = %s and tipo = 'intento_habilitado'", (m,))
        assert cur.fetchone()["n"] == 1


# ===========================================================================
# G1d-b2, ítem 3: "Habilitar" comprueba el ciclo vigente, no sólo el aviso
# ===========================================================================


def test_confirmar_habilitar_con_ciclo_ya_active_resuelve_sin_aplicar_nada(
        cliente_admin, conn, intake_world):
    """Si la persona ya se verificó sola por otro camino mientras el aviso
    de "envíos agotados" seguía sin resolver, "Habilitar un nuevo intento"
    no tiene nada que habilitar -- el aviso se resuelve solo (ya no
    describe nada vigente), pero nunca se abre un intento nuevo ni se le
    manda nada a la persona. La respuesta al administrador es "No se
    habilitó nada." -- cierta: ningún intento nuevo se abrió."""
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    _, tg_admin = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")
    with espacio(conn, ws) as cur:
        AC.transicionar(cur, m, "active", ahora=AHORA)
    conn.commit()

    r = _post_admin_toque(
        cliente_admin, AA.callback_data(AA.ACCION_CONFIRMAR_HABILITAR, aviso_id), tg_admin)
    assert r.status_code == 200

    with admin(conn) as cur:
        [aviso] = AC.avisos(cur)
        assert aviso["resuelto_en"] is not None          # se resolvió solo
        cur.execute(
            "select count(*) n from alta_correo_evento "
            "where membership_id = %s and tipo = 'intento_habilitado'", (m,))
        assert cur.fetchone()["n"] == 0                  # nunca se abrió un intento nuevo
        cur.execute("select cuerpo from admin_reply where chat_id = %s",
                   (tg_admin,))
        assert [f["cuerpo"] for f in cur.fetchall()] == [AA.TEXTO_HABILITAR_CANCELADO]
    with espacio(conn, ws) as cur:
        cur.execute("select count(*) n from message_outbox")
        assert cur.fetchone()["n"] == 0                  # nada nuevo a la persona


def test_confirmar_habilitar_con_ciclo_ya_no_pendiente_no_aplica_ni_resuelve(
        cliente_admin, conn, intake_world):
    """Si el ciclo pasó a otra cosa que no es `active` ni `pending_email_
    verification` con el cupo agotado (acá, `awaiting_email` -- la persona
    pidió cambiar de correo antes de que administración llegara a tocar el
    botón), no se aplica nada Y el aviso queda tal cual -- nunca "ya
    estaba resuelto" (no lo estaba) ni "habilitado" (nada se habilitó)."""
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    _, tg_admin = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")
    with espacio(conn, ws) as cur:
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
    conn.commit()

    r = _post_admin_toque(
        cliente_admin, AA.callback_data(AA.ACCION_CONFIRMAR_HABILITAR, aviso_id), tg_admin)
    assert r.status_code == 200

    with admin(conn) as cur:
        [aviso] = AC.avisos(cur)
        assert aviso["resuelto_en"] is None               # sigue abierto, tal cual
        cur.execute(
            "select count(*) n from alta_correo_evento "
            "where membership_id = %s and tipo = 'intento_habilitado'", (m,))
        assert cur.fetchone()["n"] == 0
        cur.execute("select cuerpo from admin_reply where chat_id = %s",
                   (tg_admin,))
        assert [f["cuerpo"] for f in cur.fetchall()] == [AA.TEXTO_HABILITAR_CANCELADO]


def test_confirmar_habilitar_con_cupo_no_agotado_de_verdad_no_aplica_ni_resuelve(
        cliente_admin, conn, intake_world):
    """El ciclo puede seguir en `pending_email_verification` con el aviso
    todavía sin resolver aunque el cupo de 5 YA NO esté realmente agotado
    (un solo envío, acá) -- "Habilitar" no tiene que abrir un intento
    nuevo sin necesidad; el aviso queda tal cual."""
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    _, tg_admin = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    with espacio(conn, ws) as cur:
        AC.iniciar_ciclo(cur, m, "alta", ahora=AHORA)
        AC.transicionar(cur, m, "awaiting_email", ahora=AHORA)
        AC.transicionar(cur, m, "pending_email_verification", ahora=AHORA)
        AC.emitir_verificacion(cur, m, "taylor.quinn@empresa.com", "token-unico", ahora=AHORA)
        aviso_id = AC.crear_aviso(
            cur, AC.TIPO_CORREO_LIMITE_AGOTADO,
            "Taylor Quinn agotó los 5 envíos del correo de verificación.",
            referencia_tipo="membership", referencia_id=m, ahora=AHORA)
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
        cur.execute("select cuerpo from admin_reply where chat_id = %s",
                   (tg_admin,))
        assert [f["cuerpo"] for f in cur.fetchall()] == [AA.TEXTO_HABILITAR_CANCELADO]


def test_preview_habilitar_con_ciclo_ya_active_resuelve_y_no_ofrece_botones(
        cliente_admin, conn, intake_world):
    """La vista previa (primer toque de "Habilitar") aplica la misma
    comprobación de ciclo que la confirmación -- no tiene sentido ofrecer
    Confirmar/Cancelar para un intento que, al confirmarlo, no haría nada."""
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    _, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")
    with espacio(conn, ws) as cur:
        AC.transicionar(cur, m, "active", ahora=AHORA)
    conn.commit()

    r = _post_admin_toque(cliente_admin, AA.callback_data(AA.ACCION_HABILITAR, aviso_id), tg)
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select cuerpo, botones from admin_reply")
        [fila] = cur.fetchall()
        assert fila["cuerpo"] == AA.TEXTO_HABILITAR_CANCELADO
        assert not fila["botones"]
        [aviso] = AC.avisos(cur)
        assert aviso["resuelto_en"] is not None


def test_preview_habilitar_sobre_aviso_de_otro_tipo_no_dice_que_ya_estaba_resuelto(
        cliente_admin, conn, intake_world):
    """G1d-b2, ítem 7: antes, cualquier motivo por el que la vista previa
    no correspondía (aviso inexistente, de otro tipo, sin `membership`) caía
    en el mismo texto que un aviso REALMENTE resuelto ("Ese aviso ya
    estaba resuelto."), que sería falso acá -- este aviso nunca estuvo
    resuelto."""
    ws = intake_world["north-lab"]["id"]
    _, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _crear_aviso(conn, ws)   # tipo por defecto: no es de envíos agotados

    r = _post_admin_toque(cliente_admin, AA.callback_data(AA.ACCION_HABILITAR, aviso_id), tg)
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select cuerpo, botones from admin_reply")
        [fila] = cur.fetchall()
        assert fila["cuerpo"] == AA.TEXTO_HABILITAR_CANCELADO
        assert not fila["botones"]


def test_preview_habilitar_sobre_aviso_inexistente_no_dice_que_ya_estaba_resuelto(
        cliente_admin, conn, intake_world):
    """Mismo ítem 7, para un `aviso_id` que directamente no existe (botón
    de una versión vieja, o un aviso borrado) -- tampoco puede citarlo desde
    `admin_reply.aviso_administrativo_id` (esa columna lleva `on delete
    cascade`, así que un id inexistente rompería el insert si se pasara)."""
    _, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")

    r = _post_admin_toque(
        cliente_admin, AA.callback_data(AA.ACCION_HABILITAR, str(uuid.uuid4())), tg)
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select cuerpo, botones, aviso_administrativo_id from admin_reply")
        [fila] = cur.fetchall()
        assert fila["cuerpo"] == AA.TEXTO_HABILITAR_CANCELADO
        assert not fila["botones"]
        assert fila["aviso_administrativo_id"] is None


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
        cur.execute("select cuerpo from admin_reply")
        assert [f["cuerpo"] for f in cur.fetchall()] == [AA.TEXTO_HABILITAR_CANCELADO]
        cur.execute(
            "select count(*) n from alta_correo_evento where tipo = 'intento_habilitado'")
        assert cur.fetchone()["n"] == 0


# ===========================================================================
# G1d-b2, ítem 6: las respuestas de administración no se pierden por dedupe
# ===========================================================================


def test_cancelar_habilitar_dos_administradores_reciben_cada_uno_su_respuesta(
        cliente_admin, conn, intake_world):
    """Antes, la clave de dedupe de Cancelar era sólo `aviso_id` -- sin el
    administrador ni el toque, el segundo Cancelar sobre el MISMO aviso se
    perdía en silencio contra `on conflict (dedupe_key) do nothing` (la
    fila ya existía con la respuesta del primero)."""
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    _, tg1 = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    _, tg2 = _hacer_administrador(conn, intake_world, "north-lab", "Sam North")
    aviso_id = _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")

    r1 = _post_admin_toque(
        cliente_admin, AA.callback_data(AA.ACCION_CANCELAR_HABILITAR, aviso_id), tg1,
        toque_id="cb-admin-1")
    r2 = _post_admin_toque(
        cliente_admin, AA.callback_data(AA.ACCION_CANCELAR_HABILITAR, aviso_id), tg2,
        toque_id="cb-admin-2")
    assert r1.status_code == 200 and r2.status_code == 200

    with admin(conn) as cur:
        cur.execute("select chat_id, cuerpo from admin_reply")
        filas = cur.fetchall()
        assert sorted(f["chat_id"] for f in filas) == sorted([tg1, tg2])
        assert all(f["cuerpo"] == AA.TEXTO_HABILITAR_CANCELADO for f in filas)


def test_cancelar_habilitar_mismo_administrador_dos_previews_recibe_dos_respuestas(
        cliente_admin, conn, intake_world):
    """El mismo administrador, tocando "Habilitar" dos veces (dos vistas
    previas genuinas, cada una con su propio `callback_query.id` real de
    Telegram) y cancelando las dos, tiene que recibir una respuesta por
    cada Cancelar -- no es el mismo botón reenviado, son dos decisiones
    distintas."""
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    _, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")

    _post_admin_toque(
        cliente_admin, AA.callback_data(AA.ACCION_CANCELAR_HABILITAR, aviso_id), tg,
        toque_id="cb-preview-1")
    _post_admin_toque(
        cliente_admin, AA.callback_data(AA.ACCION_CANCELAR_HABILITAR, aviso_id), tg,
        toque_id="cb-preview-2")

    with admin(conn) as cur:
        cur.execute("select cuerpo from admin_reply where chat_id = %s", (tg,))
        assert len(cur.fetchall()) == 2


def test_cancelar_habilitar_redelivery_exacta_sigue_deduplicando_a_una_sola(
        cliente_admin, conn, intake_world):
    """La corrección de arriba no pierde la protección original: una
    redelivery EXACTA del mismo webhook (Telegram reenvía el mismo
    `callback_query.id` porque no recibió el ACK a tiempo) sigue
    deduplicando a una sola respuesta."""
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    _, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")
    aviso_id = _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")

    _post_admin_toque(
        cliente_admin, AA.callback_data(AA.ACCION_CANCELAR_HABILITAR, aviso_id), tg,
        toque_id="cb-redelivery")
    _post_admin_toque(
        cliente_admin, AA.callback_data(AA.ACCION_CANCELAR_HABILITAR, aviso_id), tg,
        toque_id="cb-redelivery")

    with admin(conn) as cur:
        cur.execute("select cuerpo from admin_reply where chat_id = %s", (tg,))
        assert len(cur.fetchall()) == 1


def test_toque_habilitar_de_un_no_administrador_no_hace_nada(
        cliente_admin, conn, intake_world):
    ws = intake_world["north-lab"]["id"]
    m = intake_world["north-lab"]["people"]["Taylor Quinn"]["membership_id"]
    aviso_id = _dejar_pending_verification_con_aviso_agotado(conn, ws, m, "Taylor Quinn")
    ajeno = intake_world["north-lab"]["people"]["Sam North"]["telegram"]

    r = _post_admin_toque(cliente_admin, AA.callback_data(AA.ACCION_HABILITAR, aviso_id), ajeno)
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select count(*) n from admin_reply")
        assert cur.fetchone()["n"] == 0
        [aviso] = AC.avisos(cur)
        assert aviso["resuelto_en"] is None


# ===========================================================================
# D. Marcar leído / texto libre -- encolan la respuesta puntual en admin_reply
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

        cur.execute("select chat_id, cuerpo, aviso_administrativo_id from admin_reply")
        [fila] = cur.fetchall()
        assert fila["chat_id"] == tg
        assert fila["cuerpo"] == AA.TEXTO_MARCADO_LEIDO
        assert str(fila["aviso_administrativo_id"]) == aviso_id


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
        cur.execute("select count(*) n from admin_reply")
        assert cur.fetchone()["n"] == 1


def test_responder_texto_libre_encola_la_guia(conn, intake_world):
    _, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")

    with admin(conn) as cur:
        AA.responder_texto_libre(cur, tg, 42, ahora=AHORA)
    conn.commit()

    with admin(conn) as cur:
        cur.execute("select chat_id, cuerpo from admin_reply")
        [fila] = cur.fetchall()
        assert fila["chat_id"] == tg
        assert fila["cuerpo"] == AA.TEXTO_ACCION_LIBRE


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
        cur.execute("select cuerpo from admin_reply")
        assert [f["cuerpo"] for f in cur.fetchall()] == [AA.TEXTO_MARCADO_LEIDO]


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
        cur.execute("select count(*) n from admin_reply")
        assert cur.fetchone()["n"] == 0


def test_texto_libre_de_administrador_encola_la_guia_breve(
        cliente_admin, conn, intake_world):
    admin_id, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")

    r = _post_admin_texto(cliente_admin, "quiero reenviar el correo de Sam", tg)
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select cuerpo from admin_reply")
        assert [f["cuerpo"] for f in cur.fetchall()] == [AA.TEXTO_ACCION_LIBRE]


def test_texto_libre_de_no_administrador_no_responde_nada(
        cliente_admin, conn, intake_world):
    """Mismo comportamiento de siempre: a un desconocido no se le explica
    por qué no se le responde."""
    ajeno = intake_world["north-lab"]["people"]["Sam North"]["telegram"]

    r = _post_admin_texto(cliente_admin, "hola", ajeno)
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute("select count(*) n from admin_reply")
        assert cur.fetchone()["n"] == 0
        cur.execute("select count(*) n from audit_log where accion = 'mensaje_admin'")
        assert cur.fetchone()["n"] == 0


def test_texto_libre_repetido_por_reintento_de_telegram_no_duplica_la_guia(
        cliente_admin, conn, intake_world):
    """El mismo `message_id` (Telegram reintentando el mismo update) no
    encola una segunda guía -- la clave de dedupe incluye el mensaje."""
    _, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")

    _post_admin_texto(cliente_admin, "hola", tg, message_id=7)
    _post_admin_texto(cliente_admin, "hola de nuevo", tg, message_id=7)

    with admin(conn) as cur:
        cur.execute("select count(*) n from admin_reply")
        assert cur.fetchone()["n"] == 1


def test_error_no_manejado_del_canal_admin_pasa_por_registrar_incidente(
        cliente_admin, conn, intake_world, monkeypatch):
    """Unificación con T28 (decisión del usuario, 2026-09-28):
    `gateway._reportar_incidente_admin` -- la red de contención del canal de
    administración -- ya no inserta a mano en `incident` ni encola su propia
    respuesta: pasa por `incidentes.registrar_incidente`, el único punto de
    escritura, que arma su propio aviso a cada administrador alcanzable."""
    admin_id, tg = _hacer_administrador(conn, intake_world, "north-lab", "Morgan Hale")

    def _explota(cur, chat_id, mensaje_id, *, ahora=None):
        raise RuntimeError("falla inesperada de prueba")

    monkeypatch.setattr(AA, "responder_texto_libre", _explota)

    r = _post_admin_texto(cliente_admin, "hola", tg)
    assert r.status_code == 200

    with admin(conn) as cur:
        cur.execute(
            "select resumen_sanitizado, referencia_cruda from incident "
            "where workspace_id is null")
        [incidente] = cur.fetchall()
        assert gateway.ETAPA_ADMIN in incidente["resumen_sanitizado"]
        assert "falla inesperada de prueba" not in incidente["resumen_sanitizado"]
        assert "falla inesperada de prueba" in (incidente["referencia_cruda"] or "")
        # `registrar_incidente` ya avisó -- por `admin_notice` (fan-out a
        # todos los alcanzables), no por `admin_reply` -- el propio
        # administrador que disparó el error es, acá, el único alcanzable.
        cur.execute("select cuerpo from admin_notice where chat_id = %s", (tg,))
        [aviso] = cur.fetchall()
        assert f"'{gateway.ETAPA_ADMIN}'" in aviso["cuerpo"]
