"""La redacción sigue el trato del pack (0-13): el mismo defecto que el voseo que
estaba escrito en el código del alta. `SISTEMA_REDACCION` y `SISTEMA_CHARLA`
decían "con voseo" para cualquier espacio; ahora el registro sale de
`persona_config.registro`, por la misma fuente que el alta
(`instrucciones.tono_del_espacio`). Sin tono configurado, no se inventa un trato."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from leda import redaccion
from leda.db import admin
from leda.resultado_turno import Falta, ResultadoTurno
from leda.valores import TipoValor

RAIZ = Path(__file__).resolve().parent.parent
GUIAS = [redaccion.sistema_redaccion, redaccion.sistema_charla]


def test_el_voseo_no_esta_escrito_en_la_redaccion():
    fuente = (RAIZ / "src" / "leda" / "redaccion.py").read_text(encoding="utf-8")
    assert "voseo" not in fuente.lower()


@pytest.mark.parametrize("guia", GUIAS)
def test_con_registro_usted_la_guia_trata_de_usted(guia):
    texto = guia(emojis=False, registro="usted").lower()
    assert "de usted" in texto and "de vos" not in texto


@pytest.mark.parametrize("guia", GUIAS)
def test_con_registro_vos_la_guia_trata_de_vos(guia):
    texto = guia(emojis=False, registro="vos").lower()
    assert "de vos" in texto and "de usted" not in texto


@pytest.mark.parametrize("guia", GUIAS)
def test_sin_registro_no_se_inventa_un_trato(guia):
    texto = guia(emojis=False).lower()
    assert "de vos" not in texto and "de usted" not in texto


def test_el_resto_de_la_guia_no_cambia_con_el_trato():
    usted = redaccion.sistema_charla(emojis=False, registro="usted")
    assert "Sin Markdown, sin jerga técnica y sin nombrar botones" in usted
    assert "cálida y sin vueltas" in usted
    guia = redaccion.sistema_redaccion(emojis=False, registro="usted")
    assert "cordial, clara y breve (una a tres oraciones)" in guia
    assert len(guia) <= 1450 and len(guia.splitlines()) <= 8


class _Captura:
    def __init__(self, respuesta: str):
        self.respuesta, self.sistemas = respuesta, []

    def redactar(self, sistema, hechos, **_):
        self.sistemas.append(sistema)
        return self.respuesta


@pytest.mark.parametrize("registro", ["usted", "vos"])
def test_la_redaccion_y_la_charla_leen_el_registro_del_espacio(registro,
                                                               intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with admin(conn) as cur:
        cur.execute("update persona_config set registro = %s, emojis = false "
                    "where workspace_id = %s", (registro, ws))
    conn.commit()
    turno = _Captura(json.dumps({"texto": "¿Qué hay que hacer?",
                                 "pregunta": "title", "afirma": []}))
    charla = _Captura("Hola, un gusto.")
    resultado = ResultadoTurno(falta=Falta("el título", TipoValor.TEXTO,
                                           pregunta="¿Qué hay que hacer?",
                                           campo="title"))
    with admin(conn) as cur:
        redaccion.redactar_turno(cur, ws, resultado, "A", proveedor=turno)
        redaccion.redactar_charla(cur, ws, "hola", "¿Qué hay que hacer?",
                                  proveedor=charla)
    assert turno.sistemas[0] == redaccion.sistema_redaccion(
        emojis=False, registro=registro)
    assert charla.sistemas[0] == redaccion.sistema_charla(
        emojis=False, registro=registro)
