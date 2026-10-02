"""La redacción sigue el tono del pack en emojis (C0-13, 2.ª unidad): el mismo
defecto que el voseo escrito en el código del alta. Con `persona.emojis` en
verdadero, algún emoji ocasional; en falso, sin emojis. Sin Markdown, sin jerga
técnica y sin nombrar botones siguen igual."""

from __future__ import annotations

import json

import pytest

from leda import redaccion
from leda.db import admin
from leda.resultado_turno import Falta, ResultadoTurno
from leda.valores import TipoValor


@pytest.mark.parametrize("sistema", [redaccion.sistema_redaccion,
                                     redaccion.sistema_charla])
def test_con_emojis_la_guia_permite_alguno_ocasional(sistema):
    texto = sistema(emojis=True).lower()
    assert "ocasional" in texto and "adorno" in texto
    assert "sin emojis" not in texto and "ni emojis" not in texto


@pytest.mark.parametrize("sistema", [redaccion.sistema_redaccion,
                                     redaccion.sistema_charla])
def test_sin_emojis_la_guia_lo_dice(sistema):
    texto = sistema(emojis=False).lower()
    assert "sin emojis" in texto and "ocasional" not in texto


def test_la_charla_sigue_sin_markdown_ni_jerga_ni_botones():
    for emojis in (True, False):
        assert ("Sin Markdown, sin jerga técnica y sin nombrar botones"
                in redaccion.sistema_charla(emojis=emojis))


def test_las_constantes_son_la_guia_sin_emojis():
    assert redaccion.SISTEMA_REDACCION == redaccion.sistema_redaccion(emojis=False)
    assert redaccion.SISTEMA_CHARLA == redaccion.sistema_charla(emojis=False)
    assert len(redaccion.sistema_redaccion(emojis=True)) <= 1450
    assert len(redaccion.sistema_redaccion(emojis=True).splitlines()) <= 8


class _Captura:
    def __init__(self, respuesta: str):
        self.respuesta, self.sistemas = respuesta, []

    def redactar(self, sistema, hechos, **_):
        self.sistemas.append(sistema)
        return self.respuesta


def _emojis(conn, ws, valor: bool) -> None:
    with admin(conn) as cur:
        cur.execute("update persona_config set emojis = %s, registro = 'vos' "
                    "where workspace_id = %s",
                    (valor, ws))
    conn.commit()


@pytest.mark.parametrize("valor", [True, False])
def test_la_redaccion_y_la_charla_leen_los_emojis_del_espacio(valor, intake_world,
                                                              conn):
    ws = intake_world["north-lab"]["id"]
    _emojis(conn, ws, valor)
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
        emojis=valor, registro="vos")
    assert charla.sistemas[0] == redaccion.sistema_charla(
        emojis=valor, registro="vos")
