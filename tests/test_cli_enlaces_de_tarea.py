"""Los comandos de la administración sobre la página de una tarea (ADR 0019, 7a y decisión 3;
porción 5 de la C-3): revocar los enlaces de una persona, de una tarea o de un administrador, y
retirar el contenido de una pieza de evidencia. Los corre el administrador de plataforma desde
una terminal (la consola de administración, constitución §2), nunca el bot del espacio.
"""

from __future__ import annotations

import re

import pytest

import leda.cli as cli
from leda import pagina_de_tarea as P
from leda.db import admin

from tests.garantias.test_pagina_de_la_tarea import (  # noqa: F401 -- `mundo` es la fixture
    _emitir, _leer, _leer_archivo, mundo)


@pytest.fixture
def ada(conn, mundo) -> str:
    with admin(conn) as cur:
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (79001, 'Ada Admin') returning id""")
        usuario = str(cur.fetchone()["id"])
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (usuario,))
    conn.commit()
    return usuario


@pytest.fixture
def correr(conn, monkeypatch, capsys):
    monkeypatch.setattr(cli, "conectar", lambda: conn)

    def _correr(*argumentos: str) -> tuple[int, str]:
        codigo = cli.main(list(argumentos))
        return codigo, capsys.readouterr().out

    return _correr


def _auditadas(conn, accion: str) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from audit_log where accion = %s", (accion,))
        n = cur.fetchone()["n"]
    conn.commit()
    return n


# --- Revocar ----------------------------------------------------------------------------------

def test_revocar_los_enlaces_de_una_persona(conn, mundo, correr):
    de_sam = _emitir(conn, mundo, "Sam Noble")
    de_taylor = _emitir(conn, mundo, "Taylor Quinn")
    codigo, salida = correr("revocar-enlaces", "north-lab", "--persona", "Sam Noble")
    assert codigo == 0
    assert "1" in salida and "Sam Noble 1" in salida
    assert _leer(conn, de_sam) is None
    assert _leer(conn, de_taylor) is not None
    assert _auditadas(conn, "revocar_enlaces_de_tarea") == 1


def test_revocar_los_enlaces_de_una_tarea(conn, mundo, correr):
    tokens = [_emitir(conn, mundo, "Sam Noble"), _emitir(conn, mundo, "Morgan Hale")]
    otra = _emitir(conn, mundo, "Morgan Hale", mundo["vecina"])
    codigo, salida = correr("revocar-enlaces", "north-lab", "--tarea", "balanza")
    assert codigo == 0 and "Calibrar la balanza" in salida
    assert all(_leer(conn, t) is None for t in tokens)
    assert _leer(conn, otra) is not None


def test_revocar_una_tarea_que_no_existe_no_toca_nada(conn, mundo, correr):
    token = _emitir(conn, mundo, "Sam Noble")
    codigo, salida = correr("revocar-enlaces", "north-lab", "--tarea", "bomba de agua")
    assert codigo == 1 and "ninguna tarea" in salida
    assert _leer(conn, token) is not None
    assert _auditadas(conn, "revocar_enlaces_de_tarea") == 0


def test_revocar_una_tarea_de_otro_espacio_no_la_encuentra(conn, mundo, correr):
    codigo, salida = correr("revocar-enlaces", "north-lab", "--tarea", "secreto del oeste")
    assert codigo == 1 and "ninguna tarea" in salida


def test_revocar_los_accesos_de_un_administrador(conn, mundo, ada, correr):
    with admin(conn) as cur:
        token = P.emitir_para_administrador(cur, ada, mundo["north-lab"]["id"],
                                            mundo["norte"]["id"])
    conn.commit()
    codigo, salida = correr("revocar-enlaces", "north-lab", "--administrador", "Ada")
    assert codigo == 0 and "Ada Admin" in salida
    assert _leer(conn, token) is None


def test_revocar_pide_un_solo_criterio(conn, mundo, correr):
    with pytest.raises(SystemExit):
        correr("revocar-enlaces", "north-lab")
    with pytest.raises(SystemExit):
        correr("revocar-enlaces", "north-lab", "--persona", "Sam", "--tarea", "balanza")


# --- Retirar contenido ------------------------------------------------------------------------

def _numero(salida: str, nombre: str) -> str:
    return re.search(rf"^\s*(\d+)\. .*{re.escape(nombre)}", salida, re.MULTILINE).group(1)


def test_sin_pieza_lista_lo_que_se_entrego_y_no_cambia_nada(conn, mundo, correr):
    codigo, salida = correr("retirar-contenido", "north-lab", "--tarea", "balanza")
    assert codigo == 0
    for que in ("pantalla.jpg", "informe.pdf", "Quedó andando"):
        assert que in salida
    assert _auditadas(conn, "retirar_contenido_de_evidencia") == 0


def test_retirar_una_pieza_con_quien_y_por_que(conn, mundo, ada, correr):
    _, lista = correr("retirar-contenido", "north-lab", "--tarea", "balanza")
    codigo, salida = correr("retirar-contenido", "north-lab", "--tarea", "balanza",
                            "--pieza", _numero(lista, "pantalla.jpg"),
                            "--administrador", "Ada", "--motivo", "una contraseña en un papel")
    assert codigo == 0 and "retirado" in salida
    token = _emitir(conn, mundo, "Taylor Quinn")
    assert _leer_archivo(conn, token, mundo["norte"]["piezas"]["foto"]) is None
    pieza = next(p for p in _leer(conn, token)["evidencia"]
                 if p["id"] == mundo["norte"]["piezas"]["foto"])
    assert pieza["retirada_por_la_administracion"]
    assert _auditadas(conn, "retirar_contenido_de_evidencia") == 1


def test_retirar_lo_hace_solo_un_administrador_de_plataforma(conn, mundo, ada, correr):
    _, lista = correr("retirar-contenido", "north-lab", "--tarea", "balanza")
    codigo, salida = correr("retirar-contenido", "north-lab", "--tarea", "balanza",
                            "--pieza", _numero(lista, "pantalla.jpg"),
                            "--administrador", "Morgan", "--motivo", "no")
    assert codigo == 1 and "administrador" in salida
    assert _auditadas(conn, "retirar_contenido_de_evidencia") == 0


def test_retirar_una_pieza_pide_quien_y_por_que(conn, mundo, ada, correr):
    codigo, salida = correr("retirar-contenido", "north-lab", "--tarea", "balanza",
                            "--pieza", "1")
    assert codigo == 1 and "--administrador" in salida and "--motivo" in salida
    assert _auditadas(conn, "retirar_contenido_de_evidencia") == 0


def test_un_numero_de_pieza_que_no_existe(conn, mundo, ada, correr):
    codigo, salida = correr("retirar-contenido", "north-lab", "--tarea", "balanza",
                            "--pieza", "9", "--administrador", "Ada", "--motivo", "no")
    assert codigo == 1
    assert _auditadas(conn, "retirar_contenido_de_evidencia") == 0
