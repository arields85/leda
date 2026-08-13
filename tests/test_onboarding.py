"""Pruebas del alta de integrantes.

El foco está en lo que puede salir mal: un enlace que se filtra al grupo, uno
que se reutiliza, o alguien que intenta hacerse pasar por otro.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import gateway
from prisma.db import admin, espacio
from prisma.llm import ProveedorGuionado, Respuesta
from prisma.onboarding import (ActivacionInvalida, activar, encolar_presentacion,
                               generar_enlaces, pendientes_de_activar)

AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=timezone.utc)


@pytest.fixture
def sin_activar(conn, tmp_path):
    """CoreWork activo con nadie vinculado a Telegram todavía."""
    import yaml

    from prisma.importador import importar
    from tests.conftest import RAIZ

    import os

    os.environ["PRISMA_BOT_TOKEN_COREWORK"] = "prueba:token"

    pack = yaml.safe_load((RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack["telegram"]["grupo_gestion_id"] = -1001
    pack["evidencia"]["estructura_drive"] = "drive://corework"
    # Nadie vinculado todavía: los identificadores llegan por activación.
    for p in pack["personas"]:
        p["telegram_user_id"] = "PENDIENTE"
    ruta = tmp_path / "cw.yaml"
    ruta.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    r = importar(conn, ruta, activar=True)
    conn.commit()
    return r


def test_el_espacio_activa_sin_que_nadie_haya_activado(sin_activar):
    """Los identificadores llegan por el enlace, no por el pack."""
    assert sin_activar.activo
    assert any("activaron su enlace" in a for a in sin_activar.advertencias)


def test_genera_un_enlace_por_persona(sin_activar, conn):
    ws = sin_activar.workspace_id
    with admin(conn) as cur:
        enlaces = generar_enlaces(cur, ws, "prisma_corework_bot", ahora=AHORA)
    assert len(enlaces) == 7
    assert all(e.url.startswith("https://t.me/prisma_corework_bot?start=") for e in enlaces)
    # Tokens distintos y largos: no se adivinan.
    tokens = {e.token for e in enlaces}
    assert len(tokens) == 7 and all(len(t) >= 24 for t in tokens)


def test_piloto_con_algunos(sin_activar, conn):
    ws = sin_activar.workspace_id
    with admin(conn) as cur:
        enlaces = generar_enlaces(cur, ws, "bot", solo=["Marcos", "Nahuel"],
                                  ahora=AHORA)
    assert {e.nombre for e in enlaces} == {"Marcos Tarquini", "Nahuel Gimenez"}


def test_activa_y_queda_vinculado(sin_activar, conn):
    ws = sin_activar.workspace_id
    with admin(conn) as cur:
        enlaces = generar_enlaces(cur, ws, "bot", solo=["Marcos"], ahora=AHORA)
        nombre = activar(cur, ws, enlaces[0].token, 555001, ahora=AHORA)
        assert nombre == "Marcos Tarquini"
        cur.execute("select telegram_user_id t from app_user where nombre = %s",
                    (nombre,))
        assert cur.fetchone()["t"] == 555001
        assert "Marcos Tarquini" not in pendientes_de_activar(cur, ws)


def test_el_enlace_sirve_una_sola_vez(sin_activar, conn):
    ws = sin_activar.workspace_id
    with admin(conn) as cur:
        enlaces = generar_enlaces(cur, ws, "bot", solo=["Marcos"], ahora=AHORA)
        activar(cur, ws, enlaces[0].token, 555001, ahora=AHORA)
        with pytest.raises(ActivacionInvalida, match="ya se usó"):
            activar(cur, ws, enlaces[0].token, 555999, ahora=AHORA)


def test_enlace_vencido(sin_activar, conn):
    ws = sin_activar.workspace_id
    with admin(conn) as cur:
        enlaces = generar_enlaces(cur, ws, "bot", solo=["Marcos"], ahora=AHORA)
        with pytest.raises(ActivacionInvalida, match="venció"):
            activar(cur, ws, enlaces[0].token, 555001,
                    ahora=AHORA + timedelta(days=30))


def test_una_cuenta_no_puede_tomar_dos_identidades(sin_activar, conn):
    """El escenario que hace peligroso publicar los enlaces en el grupo."""
    ws = sin_activar.workspace_id
    with admin(conn) as cur:
        enlaces = generar_enlaces(cur, ws, "bot", solo=["Marcos", "Nahuel"],
                                  ahora=AHORA)
        por_nombre = {e.nombre: e for e in enlaces}
        activar(cur, ws, por_nombre["Marcos Tarquini"].token, 555001, ahora=AHORA)
        with pytest.raises(ActivacionInvalida, match="ya está en uso"):
            activar(cur, ws, por_nombre["Nahuel Gimenez"].token, 555001,
                    ahora=AHORA)


def test_regenerar_invalida_el_anterior(sin_activar, conn):
    ws = sin_activar.workspace_id
    with admin(conn) as cur:
        viejo = generar_enlaces(cur, ws, "bot", solo=["Marcos"], ahora=AHORA)[0]
        generar_enlaces(cur, ws, "bot", solo=["Marcos"], ahora=AHORA)
        with pytest.raises(ActivacionInvalida, match="no es válido"):
            activar(cur, ws, viejo.token, 555001, ahora=AHORA)


def test_token_inventado(sin_activar, conn):
    ws = sin_activar.workspace_id
    with admin(conn) as cur:
        with pytest.raises(ActivacionInvalida, match="no es válido"):
            activar(cur, ws, "cualquier-cosa", 555001, ahora=AHORA)


def test_presentacion_va_al_grupo(sin_activar, conn):
    ws = sin_activar.workspace_id
    with admin(conn) as cur:
        assert encolar_presentacion(cur, ws, ahora=AHORA)
        cur.execute("select chat_id, cuerpo, tipo from message_outbox")
        fila = cur.fetchone()
        assert fila["chat_id"] == -1001
        assert fila["tipo"] == "informativo"
        assert "Prisma" in fila["cuerpo"]
        # La presentación no lleva enlaces: esos van uno a uno.
        assert "t.me" not in fila["cuerpo"] and "start=" not in fila["cuerpo"]
        assert not encolar_presentacion(cur, ws, ahora=AHORA)   # no duplica


# ---------------------------------------------------------------------------
# Circuito completo por el webhook
# ---------------------------------------------------------------------------

@pytest.fixture
def cliente(sin_activar, conn, monkeypatch):
    import dataclasses

    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    monkeypatch.setattr(
        "prisma.llm.desde_base",
        lambda cur, ws, key: ProveedorGuionado([Respuesta(texto="Anotado.")]))
    return TestClient(gateway.app)


def _post(cliente, texto, user_id):
    return cliente.post(
        "/telegram/corework",
        json={"message": {"message_id": 1, "text": texto,
                          "chat": {"id": user_id}, "from": {"id": user_id}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _token_vigente(cur, ws, persona: str) -> str:
    """Un enlace que todavía sirve cuando lo activa el webhook.

    Un enlace vale VIGENCIA días desde que se emite. Cuando la activación
    entra por el gateway, `activar` la valida contra el reloj real: nadie le
    pasa un `ahora`. Así que un enlace fechado en una constante del pasado se
    vence solo con el correr de los días y la prueba se cae sin que nadie haya
    tocado una línea de código.

    Los enlaces que se activan por el webhook nacen del mismo reloj que los
    valida. Para lo que se prueba contra un momento fijo —que un enlace
    vencido se rechace, que uno usado no se reutilice— sigue estando AHORA.
    """
    return generar_enlaces(cur, ws, "bot", solo=[persona],
                           ahora=datetime.now(timezone.utc))[0].token


def test_start_activa_y_da_la_bienvenida(cliente, conn, sin_activar):
    ws = sin_activar.workspace_id
    with admin(conn) as cur:
        token = _token_vigente(cur, ws, "Marcos")
    conn.commit()

    assert _post(cliente, f"/start {token}", 555001).status_code == 200

    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user where nombre = 'Marcos Tarquini'")
        assert cur.fetchone()["t"] == 555001
        cur.execute("select cuerpo from message_outbox order by id desc limit 1")
        assert "Marcos" in cur.fetchone()["cuerpo"]


def test_antes_de_activar_no_lo_reconoce_y_despues_si(cliente, conn, sin_activar):
    ws = sin_activar.workspace_id

    # Sin activar: es un desconocido, no se registra ni se le responde.
    _post(cliente, "hola", 555002)
    with admin(conn) as cur:
        cur.execute("select count(*) n from inbound_message")
        assert cur.fetchone()["n"] == 0

    with admin(conn) as cur:
        token = _token_vigente(cur, ws, "Nahuel")
    conn.commit()
    _post(cliente, f"/start {token}", 555002)

    # Activado: ahora sí conversa.
    _post(cliente, "hola", 555002)
    with admin(conn) as cur:
        cur.execute("select texto from inbound_message")
        assert cur.fetchone()["texto"] == "hola"


def test_start_con_token_invalido_no_vincula(cliente, conn):
    _post(cliente, "/start basura", 555003)
    with admin(conn) as cur:
        cur.execute("select count(*) n from app_user where telegram_user_id = 555003")
        assert cur.fetchone()["n"] == 0
        cur.execute("select cuerpo from message_outbox")
        assert "no es válido" in cur.fetchone()["cuerpo"]


def test_start_pelado_no_hace_nada(cliente, conn):
    _post(cliente, "/start", 555004)
    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox")
        assert cur.fetchone()["n"] == 0


def test_activado_recibe_cadencia(cliente, conn, sin_activar):
    """Después de activar, la persona entra en el seguimiento privado."""
    from prisma import reloj
    from prisma.calendario import Calendario

    ws = sin_activar.workspace_id
    with admin(conn) as cur:
        token = _token_vigente(cur, ws, "Marcos")
    conn.commit()
    _post(cliente, f"/start {token}", 555001)

    with admin(conn) as cur:
        cur.execute(
            """insert into objective (workspace_id, tipo, titulo)
               values (%s, 'operativo', 'Integrar comprimidora 3') returning id""",
            (ws,))
        obj = cur.fetchone()["id"]
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, fecha_objetivo,
                                 criterio_aceptacion, evidencia_requerida)
               values (%s, %s, 'Programar PLC',
                       (select id from area where workspace_id = %s and slug = 'ot'),
                       (select m.id from membership m join app_user u on u.id = m.app_user_id
                         where m.workspace_id = %s and u.nombre = 'Marcos Tarquini'),
                        '2026-08-14', 'Resultado verificado',
                        array['resultado_de_prueba']) returning id""",
            (ws, obj, ws, ws))
        t = cur.fetchone()["id"]
        cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                    "values (%s, 'asignada', 'prisma')", (t,))

    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        lunes = datetime(2026, 8, 3, 9, 15, tzinfo=cal.zona)
        # Sólo Marcos activó: es el único que recibe privado.
        assert reloj.ejecutar_cadencia(cur, ws, "objetivos_semanales", cal, lunes) == 1


def test_start_sin_token_saluda_a_quien_ya_esta_vinculado(cliente, conn, sin_activar):
    """Si el identificador vino en el pack, no hace falta enlace: alcanza con
    que la persona le escriba al bot una vez."""
    ws = sin_activar.workspace_id
    with admin(conn) as cur:
        cur.execute(
            """update app_user set telegram_user_id = 777001
                where nombre = 'Marcos Tarquini'""")
    conn.commit()

    _post(cliente, "/start", 777001)

    with admin(conn) as cur:
        cur.execute("select cuerpo from message_outbox")
        fila = cur.fetchone()
        assert fila and "Marcos" in fila["cuerpo"]


def test_start_sin_token_de_un_desconocido_no_responde(cliente, conn):
    _post(cliente, "/start", 999999)
    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox")
        assert cur.fetchone()["n"] == 0
