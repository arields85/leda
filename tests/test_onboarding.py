"""Pruebas del alta de integrantes.

El foco está en lo que puede salir mal: un enlace que se filtra al grupo, uno
que se reutiliza, o alguien que intenta hacerse pasar por otro.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from leda.db import admin
from leda.onboarding import (ActivacionInvalida, activar, encolar_presentacion,
                               generar_enlaces, pendientes_de_activar)

AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=timezone.utc)


@pytest.fixture
def sin_activar(conn, tmp_path):
    """CoreWork activo con nadie vinculado a Telegram todavía."""
    import yaml

    from leda.importador import importar
    from tests.conftest import RAIZ

    import os

    os.environ["LEDA_BOT_TOKEN_COREWORK"] = "prueba:token"

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
        enlaces = generar_enlaces(cur, ws, "leda_corework_bot", ahora=AHORA)
    assert len(enlaces) == 7
    assert all(e.url.startswith("https://t.me/leda_corework_bot?start=") for e in enlaces)
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
        assert "Leda" in fila["cuerpo"]
        # La presentación no lleva enlaces: esos van uno a uno.
        assert "t.me" not in fila["cuerpo"] and "start=" not in fila["cuerpo"]
        assert not encolar_presentacion(cur, ws, ahora=AHORA)   # no duplica
