"""Lo anunciado en un turno anterior y lo que sigue (tercera vuelta de ajuste, usuario,
2026-10-06; ADR 0018, decisión 9).

- **Lo anunciado antes.** Ronda 2, conversación 16, vez 5: un turno anunció que Leda volvía a
  pedir el estado al día siguiente; en el turno siguiente la persona dio una fecha, que contesta
  esa espera, y Leda volvió a anunciar el pedido que ya no iba a salir. La relectura del final
  del turno (9k) cubría sólo lo que nombraba el mismo turno. Ahora cada turno guarda, fuera de
  sus hechos, lo que dejó anunciado y pendiente; el turno siguiente lo vuelve a mirar con la
  misma regla y dice una sola vez lo que ya no va a pasar (`ya_no_sale`). Vale para cualquier
  aviso que un hecho anunció, sin una rama por jugada.
- **Lo que sigue.** Todo mensaje termina con un próximo paso concreto (definición del usuario):
  lo que Leda va a hacer lo dicen los hechos, cuando el código lo sabe, para que la IA no lo
  invente: el próximo aviso guardado para la persona, que el seguimiento se detiene mientras la
  tarea siga trabada, o el día en que Leda le va a pedir el estado.

El reloj y la tarea son los de `test_escalera.py`: "Revisar el tablero" de Marcos vence el
viernes 9 de octubre de 2026, el aviso previo es a 3 días hábiles y el lunes 12 es feriado.
"""

from __future__ import annotations

import re

from prueba_chica.efectos import ANUNCIADOS, YA_NO_SALE
from prueba_chica.escalera import correr_escalera
from prueba_chica.hechos import sin_significado
from prueba_chica.ia import Jugada
from prueba_chica.test_avisos import _dice, _hora
from prueba_chica.test_escalera import (  # noqa: F401 (las fixtures se usan por su nombre)
    _avisos, dias, espacio_con_escalera)
from prueba_chica.test_situaciones import _uno
from prueba_chica.tiempo import RelojFijo

VAGO = "voy bien, la tengo casi lista"
RETIRADO = "retirado_sin_enviar"
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def _avance() -> Jugada:
    return Jugada("informar_avance", {"tarea": "T1", "palabras": VAGO})


def _fecha(dia: str) -> Jugada:
    return Jugada("anotar_prevision", {"tarea": "T1", "fecha": dia})


def _registrado(conn) -> dict:
    """El resultado registrado del último turno de la persona."""
    return _uno(conn, """select resultado from conversation_turn
                          where sentido = 'entrada' order by numero desc limit 1""")["resultado"]


# --- Lo anunciado en un turno anterior ------------------------------------------------------

def test_una_fecha_dice_que_ya_no_sale_el_pedido_que_anuncio_el_turno_anterior(conn, mundo,
                                                                              dias, escribe):
    dias.ciclo(_hora(9, 10))                                    # el pedido de estado de V
    antes = _dice(conn, escribe, _avance(), at=_hora(9, 10, 30))
    assert antes.hechos[0]["vuelve_a_pedir_el_estado"]["estado"] == "guardado_sin_enviar"
    assert [a["clave"] for a in _registrado(conn)[ANUNCIADOS]] == ["vuelve_a_pedir_el_estado"]

    resultado = _dice(conn, escribe, _fecha("2026-10-16"), at=_hora(9, 11))

    registrado = _registrado(conn)
    assert resultado.ya_no_sale == registrado[YA_NO_SALE]
    assert registrado[YA_NO_SALE] == [{"anuncio": "vuelve_a_pedir_el_estado",
                                       "tarea": "Revisar el tablero", "estado": RETIRADO,
                                       "motivo": "ya_respondio"}]
    # Se retiró ahora, con el motivo con que se habría omitido al salir.
    [repregunta] = _avisos(conn, "repregunta_de_estado")
    assert (repregunta["estado"], repregunta["motivo_omision"]) == ("omitido", "ya_respondio")
    assert sin_significado(registrado[YA_NO_SALE]) == set()
    # Los hechos no llevan ids, y los últimos turnos que recibe la IA tampoco.
    assert not UUID.search(str(registrado["hechos"]))


def test_lo_que_sigue_pendiente_pasa_al_turno_siguiente_y_lo_retirado_se_dice_una_vez(
        conn, mundo, dias, escribe):
    dias.ciclo(_hora(9, 10))
    _dice(conn, escribe, _avance(), at=_hora(9, 10, 30))
    _dice(conn, escribe, Jugada("consultar_pendientes"), at=_hora(9, 10, 40))
    sigue = _registrado(conn)
    assert YA_NO_SALE not in sigue
    assert [a["clave"] for a in sigue[ANUNCIADOS]] == ["vuelve_a_pedir_el_estado"]

    _dice(conn, escribe, _fecha("2026-10-16"), at=_hora(9, 11))
    assert [x["anuncio"] for x in _registrado(conn)[YA_NO_SALE]] == ["vuelve_a_pedir_el_estado"]

    _dice(conn, escribe, Jugada("consultar_pendientes"), at=_hora(9, 11, 10))
    assert YA_NO_SALE not in _registrado(conn)


def test_lo_que_ya_dice_un_hecho_del_mismo_turno_no_se_repite(conn, mundo, dias, escribe):
    """El avance y la fecha en un mismo mensaje: el hecho del avance ya dice que el pedido se
    retiró (9k); nada de un turno anterior lo repite."""
    dias.ciclo(_hora(9, 10))
    _dice(conn, escribe, _avance(), _fecha("2026-10-16"), at=_hora(9, 10, 30))
    assert YA_NO_SALE not in _registrado(conn)


def test_el_aviso_al_referente_anunciado_que_otra_fecha_deja_atras_se_dice(conn, mundo,
                                                                          escribe):
    _dice(conn, escribe, _fecha("2026-10-14"), at=_hora(10, 18))
    assert [a["a"] for a in _registrado(conn)[ANUNCIADOS]] == ["Ismael"]

    _dice(conn, escribe, _fecha("2026-10-16"), at=_hora(10, 18, 5))

    [ya_no] = _registrado(conn)[YA_NO_SALE]
    assert ya_no == {"anuncio": "aviso_al_referente", "tarea": "Revisar el tablero",
                     "a": "Ismael", "estado": RETIRADO,
                     "motivo": "hay_una_prevision_mas_nueva"}


# --- Lo que sigue ---------------------------------------------------------------------------

def test_un_inicio_antes_del_vencimiento_dice_cuando_se_pide_el_estado(conn, mundo, escribe):
    [hecho] = _dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"})).hechos

    assert hecho["lo_que_sigue"] == {"pide_el_estado_el": {"fecha": "2026-10-09",
                                                           "estado": "todavia_no"}}
    assert sin_significado(hecho) == set()


def test_una_prevision_mueve_lo_que_sigue_al_dia_previsto(conn, mundo, escribe):
    [hecho] = _dice(conn, escribe, _fecha("2026-10-16")).hechos

    assert hecho["lo_que_sigue"] == {"pide_el_estado_el": {"fecha": "2026-10-16",
                                                           "estado": "todavia_no"}}


def test_un_bloqueo_dice_que_el_seguimiento_espera_que_se_destrabe(conn, mundo, escribe):
    [hecho] = _dice(conn, escribe, Jugada("anotar_bloqueo",
                                          {"tarea": "T1", "causa": "falta el PLC"})).hechos

    assert hecho["lo_que_sigue"] == {"seguimiento": "detenido_mientras_siga_trabada"}
    assert sin_significado(hecho) == set()


def test_un_aviso_guardado_para_la_persona_es_lo_que_sigue(conn, mundo, espacio_con_escalera,
                                                          escribe):
    correr_escalera(conn, mundo["id"], RelojFijo(_hora(6, 7)))     # el aviso previo, guardado
    conn.commit()

    [hecho] = _dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}),
                    at=_hora(6, 8)).hechos

    sigue = hecho["lo_que_sigue"]["proximo_aviso"]
    assert (sigue["aviso"], sigue["estado"]) == ("aviso_previo", "guardado_sin_enviar")
    assert sigue["sale"].startswith("2026-10-06T09:00")
    assert sin_significado(hecho) == set()


def test_lo_que_un_hecho_ya_nombra_no_se_repite_como_lo_que_sigue(conn, mundo, dias, escribe):
    dias.ciclo(_hora(9, 10))

    [hecho] = _dice(conn, escribe, _avance(), at=_hora(9, 10, 30)).hechos

    assert hecho["vuelve_a_pedir_el_estado"]["estado"] == "guardado_sin_enviar"
    assert "lo_que_sigue" not in hecho


def test_lo_que_sigue_va_en_el_ultimo_hecho_de_cada_tarea(conn, mundo, escribe):
    inicio, prevision = _dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}),
                              _fecha("2026-10-16")).hechos

    assert "lo_que_sigue" not in inicio
    assert prevision["lo_que_sigue"]["pide_el_estado_el"]["fecha"] == "2026-10-16"


def test_lo_que_no_se_anoto_no_lleva_lo_que_sigue(conn, mundo, escribe):
    [hecho] = _dice(conn, escribe, Jugada("anotar_bloqueo", {"tarea": "T1"})).hechos

    assert hecho["resultado"] == "falta_dato"
    assert "lo_que_sigue" not in hecho


# --- Lo que dicen las instrucciones de la redacción -----------------------------------------

def test_la_redaccion_termina_con_un_proximo_paso_concreto_sin_frases():
    """La definición del usuario (2026-10-06), descrita en general: lo que Leda va a hacer sólo
    si un hecho lo dice, lo que la persona puede hacer, o que no queda nada pendiente con lo que
    sigue; "no hace falta responder" solo no cuenta, salvo en un aviso que no pide respuesta."""
    from prueba_chica.instrucciones import INSTRUCCIONES_REDACCION as texto

    for dato in ("lo_que_sigue", "ya_no_sale", "necesita_respuesta", "próximo paso concreto"):
        assert dato in texto, dato
    assert "Si no hace falta nada más" not in texto
    for frase in ("te aviso", "avisame", "cualquier cosa"):
        assert frase not in texto.lower(), frase
