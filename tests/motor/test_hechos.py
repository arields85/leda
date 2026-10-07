"""El vocabulario de los hechos (`leda.motor.hechos`): cada dato que el código le pasa a la IA
dice qué significa.

Revisión del contrato entre la IA y el código (usuario, 2026-10-05; ADR 0018, decisión 9),
después de la primera ronda real: un hecho sin su significado hizo decir algo falso (el atraso
de una previsión contado como el atraso de hoy, conversaciones 15 y 16). Cada clave y cada
código de los hechos tiene su significado en `hechos.py`, y la IA recibe el de todo lo que le
llega en cada pedido. Un hecho sin significado es una falla del motor en la corrida.

Portadas de `prueba_chica/test_hechos.py`. Las que piden la IA real (`ia_real`) o el corredor
esperan a la capa 3; la que pasa por el turno llega con él.
"""

from __future__ import annotations

from leda.motor import hechos
from leda.motor.fichas import GUARDADO_SIN_ENVIAR
from leda.motor.instrucciones import INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION

# --- El vocabulario ---------------------------------------------------------------------------

def test_dos_atrasos_distintos_tienen_dos_claves_distintas():
    """El de hoy (desde la fecha comprometida) y el que tendrá la tarea si se cumple una
    previsión: con una sola clave, la IA contó uno como el otro (ronda 1)."""
    hoy = hechos.significado("atraso_dias_habiles")
    previsto = hechos.significado("atraso_si_se_cumple_la_prevision_dias_habiles")
    assert hoy and previsto and hoy != previsto
    assert "hoy" in hoy and "si se cumple" in previsto


def test_sin_significado_nombra_lo_que_no_esta_en_el_vocabulario():
    valor = {"jugada": "anotar_inicio", "resultado": "anotado", "clave_nueva": 1,
             "tarea": {"alias": "T1", "titulo": "Programar el PLC"},
             "estado": "codigo_nuevo", "texto": "dijo algo con espacios"}

    assert hechos.sin_significado(valor) == {"clave_nueva", "codigo_nuevo"}


def test_el_bloque_de_significados_trae_solo_lo_que_el_pedido_usa():
    pedido = {"hechos": [{"jugada": "anotar_prevision", "resultado": "anotado",
                          "atraso_si_se_cumple_la_prevision_dias_habiles": 3,
                          "aviso_al_referente": {"estado": GUARDADO_SIN_ENVIAR}}]}

    bloque = hechos.bloque(pedido)

    for clave in ("hechos", "jugada", "resultado", "aviso_al_referente", "estado",
                  "atraso_si_se_cumple_la_prevision_dias_habiles", "anotar_prevision",
                  "anotado", GUARDADO_SIN_ENVIAR):
        assert f"- {clave}: {hechos.significado(clave)}" in bloque, clave
    assert "- atraso_dias_habiles:" not in bloque
    assert "- anotar_bloqueo:" not in bloque


# --- La IA real recibe el significado de lo que le llega ------------------------------------

def test_las_instrucciones_remiten_a_los_significados_y_piden_un_proximo_paso():
    """Reglas generales de la redacción (constitución §8 y §10): todo mensaje deja un próximo
    paso o dice que no hace falta nada; nunca se narra cómo funciona el sistema; sin hechos
    nuevos, se contesta desde el registro. Sin frases de las conversaciones."""
    for texto in (INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION):
        assert "lista de significados" in texto
    redaccion = INSTRUCCIONES_REDACCION.lower()
    assert "próximo paso" in redaccion
    assert "por dentro" in redaccion
    assert "últimos turnos" in redaccion
    for frase in ("le avisaste", "switch", "no pude cancelar", "¿te sirve"):
        assert frase not in redaccion, frase


# --- Tercera vuelta de ajuste (usuario, 2026-10-06) ------------------------------------------

def test_los_significados_son_para_entender_y_nunca_para_repetir():
    """Ronda 2: "cambiarla lo decide el referente" se le repitió a la persona. El bloque y las
    instrucciones dicen que los significados son de fondo, y ninguno se lee como una frase para
    decir."""
    assert hechos.bloque({"fecha_comprometida": "2026-10-23"}).startswith(
        hechos.ENCABEZADO_DEL_BLOQUE)
    assert "nunca se le cuenta" in hechos.ENCABEZADO_DEL_BLOQUE
    assert "nunca se los contás" in INSTRUCCIONES_REDACCION
    assert "lo decide el referente" not in hechos.significado("fecha_comprometida")

