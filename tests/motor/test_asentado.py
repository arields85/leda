"""Quedó asentado (`leda.motor.asentado`; decisión 35 del usuario, 2026-10-09).

Leda no dice que informó a alguien ni nombra a nadie por su cuenta: dice que quedó asentado y,
sólo si es verdad que va a figurar en el informe al grupo del espacio, que es para que el equipo
esté al tanto. Si la persona pregunta a quién se le avisó, Leda dice la verdad. Vale para todo
aviso a una persona sobre su propio atraso o su propio bloqueo (decisiones 21 y 34).

La cocina, no frases: los hechos traen que queda asentado (`queda_asentado`) y si figura en el
informe al grupo (`figura_en_el_informe_al_grupo`), un hecho del código: el espacio tiene un
grupo y una cadencia activa al grupo (`asentado.hay_informe_al_grupo`). El nombre de a quién le
llega va dentro de `solo_si_pregunta`.
"""

from __future__ import annotations

from leda.db import admin
from leda.motor import hechos as hechos_mod
from leda.motor.asentado import (FIGURA_EN_EL_INFORME_AL_GRUPO, QUEDA_ASENTADO,
                                 hay_informe_al_grupo)

from tests.motor.ayudantes import octubre


def informe_al_grupo(conn, mundo, *, grupo: bool = True, cadencia: bool = True,
                     activa: bool = True) -> None:
    """El espacio con su grupo de Telegram y una cadencia al grupo, como en el pack."""
    with admin(conn) as cur:
        if grupo:
            cur.execute("update workspace set grupo_chat_id = -1001 where id = %s",
                        (mundo["id"],))
        if cadencia:
            cur.execute("""insert into cadence_job (workspace_id, nombre, cron, audiencia,
                                                   plantilla_clave, activo)
                           values (%s, 'informe_semanal', '15 16 * * 5', 'grupo',
                                   'informe_semanal', %s)""", (mundo["id"], activa))
    conn.commit()


def _hay(conn, mundo) -> bool:
    with admin(conn) as cur:
        return hay_informe_al_grupo(cur, mundo["id"])


def test_sin_grupo_ni_cadencia_al_grupo_no_hay_informe(conn, mundo):
    assert _hay(conn, mundo) is False


def test_con_grupo_y_cadencia_al_grupo_hay_informe(conn, mundo):
    informe_al_grupo(conn, mundo)
    assert _hay(conn, mundo) is True


def test_un_grupo_sin_cadencia_al_grupo_no_es_informe(conn, mundo):
    informe_al_grupo(conn, mundo, cadencia=False)
    assert _hay(conn, mundo) is False


def test_una_cadencia_al_grupo_sin_grupo_no_es_informe(conn, mundo):
    informe_al_grupo(conn, mundo, grupo=False)
    assert _hay(conn, mundo) is False


def test_una_cadencia_al_grupo_apagada_no_es_informe(conn, mundo):
    informe_al_grupo(conn, mundo, activa=False)
    assert _hay(conn, mundo) is False


def test_una_cadencia_en_privado_no_es_informe_al_grupo(conn, mundo):
    informe_al_grupo(conn, mundo, cadencia=False)
    with admin(conn) as cur:
        cur.execute("""insert into cadence_job (workspace_id, nombre, cron, audiencia)
                       values (%s, 'objetivos_semanales', '15 9 * * 1',
                               'privado_cada_integrante')""", (mundo["id"],))
    conn.commit()
    assert _hay(conn, mundo) is False


def test_los_datos_tienen_su_significado_y_el_nombre_va_aparte():
    for codigo in (QUEDA_ASENTADO, FIGURA_EN_EL_INFORME_AL_GRUPO):
        assert hechos_mod.significado(codigo), codigo
    assert hechos_mod.NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO[QUEDA_ASENTADO] == "a"
    redactado = hechos_mod.para_redactar(
        {QUEDA_ASENTADO: {FIGURA_EN_EL_INFORME_AL_GRUPO: True, "a": "Ismael"}})
    assert redactado[QUEDA_ASENTADO] == {FIGURA_EN_EL_INFORME_AL_GRUPO: True,
                                         "solo_si_pregunta": {"a": "Ismael"}}


def test_lo_que_pasa_si_no_contesta_queda_asentado():
    """Decisión 21 con la forma de la 35: "si mañana sigue igual, va a quedar asentado que está
    atrasada"; nunca que se informa a alguien."""
    dicho = hechos_mod.significado("si_no_hay_respuesta")
    assert "va a quedar asentado que la tarea está atrasada" in dicho
    assert "se informa" not in dicho
    assert "nadie toma la tarea" in dicho


def _hasta_el_tercer_pedido(dias) -> dict:
    """La escalera de "Revisar el tablero" (vence el viernes 9) sin respuesta, hasta el tercer
    pedido de estado, el miércoles 14, que dice lo que pasa si no contesta."""
    for momento in (octubre(6, 10), octubre(9, 10), octubre(9, 15), octubre(13, 10)):
        dias.ciclo(momento)
    [tercero] = dias.ciclo(octubre(14, 10))
    return tercero["hechos"][0]


def test_el_tercer_pedido_dice_que_va_a_quedar_asentado(conn, mundo, dias):
    hechos = _hasta_el_tercer_pedido(dias)

    assert hechos["numero"] == 3
    assert hechos["si_no_hay_respuesta"] == {
        QUEDA_ASENTADO: {FIGURA_EN_EL_INFORME_AL_GRUPO: False}, "se_avisa_a": ["Ismael"]}
    # A la redacción, el nombre sólo si pregunta.
    redactado = hechos_mod.para_redactar(hechos)["si_no_hay_respuesta"]
    assert redactado == {QUEDA_ASENTADO: {FIGURA_EN_EL_INFORME_AL_GRUPO: False},
                         "solo_si_pregunta": {"se_avisa_a": ["Ismael"]}}


def test_con_informe_al_grupo_el_equipo_esta_al_tanto(conn, mundo, dias):
    informe_al_grupo(conn, mundo)

    hechos = _hasta_el_tercer_pedido(dias)

    assert hechos["si_no_hay_respuesta"][QUEDA_ASENTADO] == {FIGURA_EN_EL_INFORME_AL_GRUPO: True}
