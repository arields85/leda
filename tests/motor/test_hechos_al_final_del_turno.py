"""Los hechos de un efecto que pasa después dicen cómo quedó al terminar el turno (ADR 0018, 9k).

Un mensaje puede traer varias jugadas: la segunda puede retirar lo que la primera dejó guardado
(un avance o un destrabe guardan el pedido del estado del día hábil siguiente; una fecha en el
mismo mensaje contesta la espera y ese pedido ya no sale). Si el hecho de la primera siguiera
diciendo que el pedido sale, la redacción contaría algo falso. Por eso, después de todas las
jugadas, el turno vuelve a leer de la base cada aviso y cada espera que un hecho nombra y pone su
estado final: un solo paso para todas las jugadas, sin ramas por jugada.

También: destrabarse antes del vencimiento deja que la escalera siga sola (revisión de
`review-e8b69f0cca8677ef`): ningún paso queda detenido por lo que el bloqueo omitió.

El reloj y la tarea son los de `test_escalera.py`: "Revisar el tablero" de Marcos vence el
viernes 9 de octubre de 2026, el aviso previo es a 3 días hábiles y el lunes 12 es feriado.

Portadas de `prueba_chica/test_hechos_al_final_del_turno.py`.
"""

from __future__ import annotations

from datetime import datetime

from leda.motor.escalera import correr_escalera
from leda.motor.fichas import GUARDADO_SIN_ENVIAR
from leda.motor.hechos import sin_significado
from leda.motor.ia import Jugada
from leda.motor.tiempo import RelojFijo

from tests.motor.ayudantes import avisos_guardados, dice, espera_del_estado, octubre, uno


VAGO = "voy bien, la tengo casi lista"
RETIRADO = "retirado_sin_enviar"
DE_UNA_PREGUNTA = ("repregunta", "escalamiento_de_una_pregunta")


def _de_la_tarea(dias, at) -> list[dict]:
    """Lo que salió en un ciclo de la escalera de la tarea (sin la de la pregunta de quién
    destraba, que tiene la suya)."""
    return [p for p in dias.ciclo(at) if p["hechos"][0]["aviso"] not in DE_UNA_PREGUNTA]


def _avance() -> Jugada:
    return Jugada("informar_avance", {"tarea": "T1", "palabras": VAGO})


def _fecha(dia: str) -> Jugada:
    return Jugada("anotar_prevision", {"tarea": "T1", "fecha": dia, "motivo": "falta un repuesto"})


def _bloquear_y_destrabar_el_dia_del_vencimiento(conn, dias, escribe):
    """El pedido del estado de V salió; Marcos se bloquea y, al rato, se destraba."""
    dias.ciclo(octubre(9, 9))
    dice(conn, escribe, Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "falta el PLC"}),
         at=octubre(9, 9, 30))


# --- Dos jugadas en un mensaje: la segunda retira lo que guardó la primera --------------------

def test_avance_y_fecha_en_un_mensaje_no_dicen_que_vuelve_a_pedir_el_estado(conn, mundo, dias,
                                                                            escribe):
    dias.ciclo(octubre(9, 10))                                  # el pedido de estado de V

    resultado = dice(conn, escribe, _avance(), _fecha("2026-10-16"), at=octubre(9, 10, 30))

    avance, prevision = resultado.hechos
    assert avance["jugada"] == "informar_avance"
    # El pedido del día hábil siguiente quedó retirado por la fecha: nunca va a salir.
    vuelve = avance["vuelve_a_pedir_el_estado"]
    assert vuelve["estado"] == RETIRADO and "sale" not in vuelve
    assert vuelve["motivo"] == "ya_respondio"
    assert avance["el_pedido_de_estado"] != "sigue_abierto"
    assert espera_del_estado(conn)["satisfecho_en"] is not None
    [repregunta] = avisos_guardados(conn, "repregunta_de_estado")
    assert (repregunta["estado"], repregunta["motivo_omision"]) == ("omitido", "ya_respondio")
    # La fecha sigue diciendo lo suyo: su aviso al referente sigue guardado.
    assert prevision["aviso_al_referente"]["estado"] == GUARDADO_SIN_ENVIAR
    # Lo que va a la IA y al registro no lleva ids de la base, y todo tiene su significado.
    assert sin_significado(resultado.hechos) == set()
    registrado = uno(conn, """select resultado from conversation_turn
                                where sentido = 'entrada' order by numero desc limit 1""")
    assert registrado["resultado"]["hechos"] == resultado.hechos


def test_destrabar_y_fecha_en_un_mensaje_no_dicen_que_vuelve_a_pedir_el_estado(conn, mundo,
                                                                              dias, escribe):
    _bloquear_y_destrabar_el_dia_del_vencimiento(conn, dias, escribe)

    resultado = dice(conn, escribe, Jugada("destrabar", {"tarea": "T1"}),
                     _fecha("2026-10-16"), at=octubre(9, 10))

    destrabe, prevision = resultado.hechos
    assert destrabe["jugada"] == "destrabar" and destrabe["resultado"] == "anotado"
    vuelve = destrabe["vuelve_a_pedir_el_estado"]
    assert vuelve["estado"] == RETIRADO and "sale" not in vuelve
    assert prevision["resultado"] == "anotado"
    assert all(a["estado"] == "omitido" for a in avisos_guardados(conn, "repregunta_de_estado"))
    assert sin_significado(resultado.hechos) == set()


def test_una_pregunta_que_el_mismo_mensaje_contesto_no_se_nombra_como_pregunta(conn, mundo,
                                                                              dias, escribe):
    """Destrabar una tarea vencida abre la pregunta de para cuándo (9j); la fecha del mismo
    mensaje la contesta: el hecho del destrabe dice que ya se cerró, no que se pregunta."""
    _bloquear_y_destrabar_el_dia_del_vencimiento(conn, dias, escribe)

    resultado = dice(conn, escribe, Jugada("destrabar", {"tarea": "T1"}),
                     _fecha("2026-10-16"), at=octubre(13, 10))

    destrabe, _ = resultado.hechos
    assert "vencida" in destrabe
    assert "pregunta" not in destrabe and "pregunta_para_despues" not in destrabe
    assert destrabe["preguntas_ya_cerradas"] == ["fecha_de_la_tarea"]
    assert resultado.pregunta is None
    assert sin_significado(resultado.hechos) == set()


def test_una_sola_jugada_deja_su_efecto_como_estaba(conn, mundo, dias, escribe):
    dias.ciclo(octubre(9, 10))

    resultado = dice(conn, escribe, _avance(), at=octubre(9, 10, 30))

    [hecho] = resultado.hechos
    vuelve = hecho["vuelve_a_pedir_el_estado"]
    assert vuelve["estado"] == GUARDADO_SIN_ENVIAR
    assert datetime.fromisoformat(vuelve["sale"]) == octubre(13, 10)
    assert hecho["el_pedido_de_estado"] == "sigue_abierto"
    [repregunta] = avisos_guardados(conn, "repregunta_de_estado")
    assert repregunta["estado"] == "guardado"
    assert sin_significado(resultado.hechos) == set()


def test_dos_fechas_en_un_mensaje_retiran_el_aviso_de_la_primera(conn, mundo, escribe):
    """El mismo paso vale para cualquier aviso que un hecho nombra: el de la primera previsión
    queda atrás por la segunda, y su hecho lo dice."""
    resultado = dice(conn, escribe, _fecha("2026-10-14"), _fecha("2026-10-16"),
                     at=octubre(6, 10))

    primera, segunda = resultado.hechos
    assert primera["aviso_al_referente"]["estado"] == RETIRADO
    assert primera["aviso_al_referente"]["motivo"] == "hay_una_prevision_mas_nueva"
    assert "sale" not in primera["aviso_al_referente"]
    assert segunda["aviso_al_referente"]["estado"] == GUARDADO_SIN_ENVIAR
    assert sin_significado(resultado.hechos) == set()


# --- Destrabarse antes del vencimiento: la escalera sigue sola --------------------------------

def test_destrabar_antes_del_vencimiento_la_escalera_sigue_sola(conn, mundo, dias, escribe):
    """El aviso previo quedó guardado, la tarea se bloqueó antes de que saliera (se omitió por
    el bloqueo) y Marcos se destrabó antes del vencimiento: el aviso previo sale mientras siga
    siendo previo, y el día del vencimiento sale el pedido del estado."""
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(6, 7)))  # el aviso previo, guardado
    conn.commit()
    dice(conn, escribe, Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "falta el PLC"}),
         at=octubre(6, 8))
    assert _de_la_tarea(dias, octubre(6, 10)) == []
    [omitido] = avisos_guardados(conn, "aviso_previo")
    assert omitido["motivo_omision"] == "bloqueo_abierto"

    resultado = dice(conn, escribe, Jugada("destrabar", {"tarea": "T1"}), at=octubre(7, 9))
    assert "vuelve_a_pedir_el_estado" not in resultado.hechos[0]

    [previo] = _de_la_tarea(dias, octubre(7, 10))
    assert previo["hechos"][0]["aviso"] == "vencimiento_proximo"
    assert _de_la_tarea(dias, octubre(8, 10)) == []
    [pedido] = _de_la_tarea(dias, octubre(9, 10))
    assert pedido["hechos"][0]["aviso"] == "pedido_de_estado"
    assert pedido["hechos"][0]["numero"] == 1
    [segundo] = _de_la_tarea(dias, octubre(13, 10))                     # sin respuesta, sigue
    assert segundo["hechos"][0]["aviso"] == "pedido_de_estado"


def test_un_bloqueo_antes_de_que_se_guarde_nada_no_detiene_la_escalera(conn, mundo, dias,
                                                                      escribe):
    dice(conn, escribe, Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "falta el PLC"}),
         at=octubre(5, 10))
    assert _de_la_tarea(dias, octubre(6, 10)) == []                     # bloqueada: no se sigue
    dice(conn, escribe, Jugada("destrabar", {"tarea": "T1"}), at=octubre(7, 9))

    [previo] = _de_la_tarea(dias, octubre(7, 10))
    assert previo["hechos"][0]["aviso"] == "vencimiento_proximo"
    [pedido] = _de_la_tarea(dias, octubre(9, 10))
    assert pedido["hechos"][0]["aviso"] == "pedido_de_estado"
