"""Los comandos de la consola para la puerta del equipo de la plataforma web (ADR 0022,
decisiones 4 y 12; porción 1, tarea P1-3): emitir el enlace de entrada de una persona, para
probar sin el chat, y cortar todas sus sesiones. Los corre el administrador de plataforma desde
una terminal (la consola de administración, constitución §2), como `leda_app` dentro del espacio:
las funciones de la 0057 sólo las ejecuta ese rol.
"""

from __future__ import annotations

import dataclasses
import re

import pytest

import leda.cli as cli

from tests.garantias.test_api_de_la_plataforma import web  # noqa: F401 -- la fixture
from tests.garantias.test_quien_ve_que import mundo  # noqa: F401 -- la fixture

from leda.db import admin

DIRECCION = "https://leda.example"


@pytest.fixture
def correr(conn, monkeypatch, capsys):
    monkeypatch.setattr(cli, "conectar", lambda: conn)
    monkeypatch.setattr(cli, "config", dataclasses.replace(cli.config, base_url=DIRECCION + "/"))

    def _correr(*argumentos: str) -> tuple[int, str]:
        codigo = cli.main(list(argumentos))
        return codigo, capsys.readouterr().out

    return _correr


def _token(salida: str) -> str:
    hallado = re.search(re.escape(DIRECCION) + r"/app/entrar/([A-Za-z0-9_-]+)", salida)
    assert hallado, salida
    return hallado.group(1)


def _auditadas(conn, accion: str) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select detalle, nucleo_hash from audit_log where accion = %s", (accion,))
        filas = cur.fetchall()
    conn.commit()
    return filas


def test_el_enlace_de_una_persona_abre_su_sesion(conn, mundo, correr, web):
    codigo, salida = correr("enlace-web", "north-lab", "--persona", "Sam North")
    assert codigo == 0 and "Sam North 1" in salida
    navegador = web()
    assert navegador.get(f"/app/entrar/{_token(salida)}").status_code == 303
    assert navegador.get("/app/api/yo").json()["persona"] == "Sam North 1"
    emitidos = _auditadas(conn, "emitir_enlace_de_entrada")
    assert len(emitidos) == 1 and emitidos[0]["nucleo_hash"]


def test_otro_enlace_anula_el_anterior(conn, mundo, correr, web):
    _, primera = correr("enlace-web", "north-lab", "--persona", "Sam North")
    _, segunda = correr("enlace-web", "north-lab", "--persona", "Sam North")
    assert web().get(f"/app/entrar/{_token(primera)}").status_code == 404
    assert web().get(f"/app/entrar/{_token(segunda)}").status_code == 303


def test_sin_la_direccion_publica_no_emite_nada(conn, mundo, correr, monkeypatch):
    monkeypatch.setattr(cli, "config", dataclasses.replace(cli.config, base_url=""))
    codigo, salida = correr("enlace-web", "north-lab", "--persona", "Sam North")
    assert codigo == 1 and "LEDA_BASE_URL" in salida
    assert _auditadas(conn, "emitir_enlace_de_entrada") == []


def test_un_nombre_ambiguo_o_de_otro_espacio_no_emite_nada(conn, mundo, correr):
    codigo, salida = correr("enlace-web", "north-lab", "--persona", "Sam")
    assert codigo == 1 and "ambiguo" in salida
    codigo, salida = correr("enlace-web", "north-lab", "--persona", "Sam North 2")
    assert codigo == 1 and "No hay ningún" in salida
    assert _auditadas(conn, "emitir_enlace_de_entrada") == []


def test_cortar_las_sesiones_de_una_persona(conn, mundo, correr, web):
    _, de_sam = correr("enlace-web", "north-lab", "--persona", "Sam North")
    _, de_taylor = correr("enlace-web", "north-lab", "--persona", "Taylor Quinn")
    sam, taylor = web(), web()
    sam.get(f"/app/entrar/{_token(de_sam)}")
    taylor.get(f"/app/entrar/{_token(de_taylor)}")
    _, sin_usar = correr("enlace-web", "north-lab", "--persona", "Sam North")
    codigo, salida = correr("cortar-sesiones-web", "north-lab", "--persona", "Sam North")
    assert codigo == 0 and "1 sesión" in salida and "Sam North 1" in salida
    assert sam.get("/app/api/yo").status_code == 401
    assert taylor.get("/app/api/yo").status_code == 200
    # El enlace que no había usado tampoco sirve: si perdió el celular, perdió el mensaje.
    assert web().get(f"/app/entrar/{_token(sin_usar)}").status_code == 404
    cortes = _auditadas(conn, "cortar_sesion_web")
    assert [c["detalle"]["motivo"] for c in cortes] == ["administrador"]
    codigo, salida = correr("cortar-sesiones-web", "north-lab", "--persona", "Sam North")
    assert codigo == 0 and "no tenía sesiones abiertas" in salida


def test_cortar_en_un_espacio_no_toca_el_otro(conn, mundo, correr, web):
    _, oeste = correr("enlace-web", "west-studio", "--persona", "Sam North")
    navegador = web()
    navegador.get(f"/app/entrar/{_token(oeste)}")
    correr("cortar-sesiones-web", "north-lab", "--persona", "Sam North")
    assert navegador.get("/app/api/yo").json()["espacio"] == "West Studio"
