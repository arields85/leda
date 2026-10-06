"""Las jugadas de un mensaje se aplican en orden (tercera vuelta de ajuste, usuario, 2026-10-06;
ADR 0018, decisión 9).

Una frase puede traer dos hechos distintos, cada uno en su jugada: "falta que martin de IT me
habilite el acceso" es la causa de un bloqueo y, a la vez, quién lo destraba (conversación 05,
paso 5). Las jugadas de un mensaje se aplican en el orden en que vienen, en la misma
transacción, así que una jugada posterior se apoya en lo que anotó una anterior: el bloqueo que
anotó la primera es el bloqueo abierto de la segunda, con su tarea o sin ella (por la pregunta
de quién lo destraba que abrió la primera). La regla vale para cualquier par de jugadas, no para
una conversación.

Lo que impide anotar dos veces una misma cosa (conversación 11, paso 3: una previsión con su
porqué no es además un bloqueo) son las definiciones de las jugadas, no una regla de "una sola
jugada": la IA guionada elige las jugadas naturales y el código hace lo de cada una.
"""

from __future__ import annotations

from prueba_chica.fichas import FICHAS
from prueba_chica.hechos import sin_significado
from prueba_chica.ia import Jugada
from prueba_chica.instrucciones import INSTRUCCIONES_JUGADAS
from prueba_chica.test_avisos import _dice, _hora
from prueba_chica.test_situaciones import _uno

CAUSA = "falta que martin de IT me habilite el acceso a la red de planta"


def _bloqueo() -> Jugada:
    return Jugada("anotar_bloqueo", {"tarea": "T1", "causa": CAUSA})


def _destraba(**datos) -> Jugada:
    return Jugada("anotar_quien_destraba", {"quien": "martin de IT", **datos})


def _pregunta_de_quien_destraba(conn) -> dict | None:
    return _uno(conn, """select cerrada_en, cierre from conversation_question
                          where tipo = 'quien_destraba' order by abierta_en desc limit 1""")


def test_la_causa_y_quien_destraba_en_una_frase_se_anotan_las_dos(conn, mundo, escribe):
    resultado = _dice(conn, escribe, _bloqueo(), _destraba(tarea="T1"), at=_hora(6, 16, 35))

    bloqueo, destraba = resultado.hechos
    assert bloqueo["resultado"] == destraba["resultado"] == "anotado"
    assert destraba["quien_destraba"] == {"externo": "martin de IT"}
    assert "salidas" not in destraba
    # La pregunta que abrió el bloqueo ya la contestó la jugada siguiente: no se hace.
    assert "pregunta" not in bloqueo
    assert bloqueo["preguntas_ya_cerradas"] == ["quien_destraba"]
    assert resultado.pregunta is None
    assert _pregunta_de_quien_destraba(conn)["cerrada_en"] is not None
    assert _uno(conn, "select destraba_externo from blocker_unblocker")["destraba_externo"] \
        == "martin de IT"
    assert sin_significado(resultado.hechos) == set()


def test_quien_destraba_sin_tarea_se_apoya_en_el_bloqueo_que_anoto_la_jugada_anterior(
        conn, mundo, escribe):
    resultado = _dice(conn, escribe, _bloqueo(), _destraba(), at=_hora(6, 16, 35))

    _, destraba = resultado.hechos
    assert destraba["resultado"] == "anotado"
    assert destraba["tarea"]["alias"] == "T1"
    assert resultado.pregunta is None


def test_destrabar_se_apoya_en_el_bloqueo_que_anoto_la_jugada_anterior(conn, mundo, escribe):
    """Trabarse y destrabarse en un mismo mensaje: el orden de las jugadas manda."""
    resultado = _dice(conn, escribe, _bloqueo(), Jugada("destrabar", {"tarea": "T1"}),
                      at=_hora(6, 16, 35))

    bloqueo, destrabe = resultado.hechos
    assert bloqueo["resultado"] == destrabe["resultado"] == "anotado"
    assert destrabe["bloqueo_resuelto"] == {"causa": CAUSA}
    assert _uno(conn, "select estado from task where id = %s",
                mundo["tarea"])["estado"] == "asignada"
    assert resultado.pregunta is None


def test_el_orden_importa_quien_destraba_antes_del_bloqueo_no_tiene_bloqueo(conn, mundo,
                                                                           escribe):
    """En el orden inverso, la segunda jugada no ve nada que no exista todavía: lo dice."""
    resultado = _dice(conn, escribe, _destraba(tarea="T1"), _bloqueo(), at=_hora(6, 16, 35))

    destraba, bloqueo = resultado.hechos
    assert destraba == {"jugada": "anotar_quien_destraba", "resultado": "no_se_puede",
                        "motivo": "sin_bloqueo_abierto",
                        "tarea": {"alias": "T1", "titulo": "Revisar el tablero"}}
    assert bloqueo["resultado"] == "anotado"


# --- Lo que dicen las instrucciones y las fichas ---------------------------------------------

def test_las_instrucciones_describen_jugadas_en_orden_sin_la_regla_de_una_sola_jugada():
    assert "una sola jugada" not in INSTRUCCIONES_JUGADAS
    assert "nunca se anota como dos hechos" not in INSTRUCCIONES_JUGADAS
    assert "en orden" in INSTRUCCIONES_JUGADAS
    assert "anterior" in INSTRUCCIONES_JUGADAS


def test_las_jugadas_sobre_un_bloqueo_admiten_el_que_anota_el_mismo_mensaje():
    for nombre in ("anotar_quien_destraba", "destrabar"):
        assert "mismo mensaje" in FICHAS[nombre].es, nombre
