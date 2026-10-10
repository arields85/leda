"""La escalera alrededor de un fin de semana (mecánica §9; `docs/STATUS.md`, deuda "Vencimiento en
fin de semana: la escalera no lo tiene probado").

Todos los momentos de la escalera se cuentan sobre el calendario laboral del espacio: "Un
vencimiento el viernes escala el miércoles siguiente, no el lunes". El aviso previo (3 días
hábiles en CoreWork) cruza el fin de semana y los feriados contando sólo días hábiles, y la
escalera comprimida de una tarea corta nunca omite el paso previo al escalamiento.

Octubre de 2026: viernes 9, sábado 10, domingo 11, lunes 12 (feriado del espacio), martes 13,
miércoles 14, jueves 15, viernes 16, sábado 17, domingo 18, lunes 19, martes 20, miércoles 21,
jueves 22. Cada ciclo corre la escalera y manda lo guardado (`ayudantes.Dias`).

Un vencimiento que cae un sábado o un domingo no tiene regla escrita (ni en el núcleo ni en el
código): no se prueba acá hasta que se decida.
"""

from __future__ import annotations

from zoneinfo import ZoneInfo

from tests.motor.ayudantes import (avisos_guardados, cambiar_el_vencimiento, cuantas,
                                   espera_del_estado, lo_que_salio_para, octubre)

BUENOS_AIRES = ZoneInfo("America/Argentina/Buenos_Aires")


def _vence(conn, mundo, dia: int) -> None:
    """La tarea de Marcos vence ese día de octubre, a las 17 (como la del mundo)."""
    cambiar_el_vencimiento(conn, mundo, octubre(dia, 17))


def _aviso(redaccion) -> str:
    return redaccion["hechos"][0]["aviso"]


def _el_fin_de_semana_no_hace_nada(conn, dias, sabado: int) -> None:
    """Ni a primera hora, ni a la de salida, ni a la tarde: nada se guarda ni sale."""
    antes = cuantas(conn, "scheduled_notice")
    for dia in (sabado, sabado + 1):
        for hora in (8, 10, 15):
            assert dias.ciclo(octubre(dia, hora)) == []
    assert cuantas(conn, "scheduled_notice") == antes


def _todo_sale_en_dias_habiles(conn) -> None:
    """Cada aviso guardado sale de lunes a viernes, hora de Buenos Aires, y nunca el feriado."""
    for aviso in avisos_guardados(conn):
        local = aviso["programado_para"].astimezone(BUENOS_AIRES)
        assert local.weekday() < 5 and local.day != 12, (aviso["tipo"], local)


# --- Vence un viernes: escala el miércoles siguiente ------------------------------------------

def test_un_vencimiento_el_viernes_escala_el_miercoles_siguiente(conn, mundo, dias):
    _vence(conn, mundo, 16)

    [previo] = dias.ciclo(octubre(13, 10))          # faltan 3 días hábiles: 14, 15 y 16
    assert _aviso(previo) == "vencimiento_proximo"
    assert previo["hechos"][0]["dias_habiles_hasta_el_vencimiento"] == 3
    for dia in (14, 15):
        assert dias.ciclo(octubre(dia, 10)) == []

    [v] = dias.ciclo(octubre(16, 10))               # V, el viernes
    assert _aviso(v) == "pedido_de_estado" and v["hechos"][0]["numero"] == 1

    _el_fin_de_semana_no_hace_nada(conn, dias, 17)

    [v1] = dias.ciclo(octubre(19, 10))              # V + 1 día hábil, el lunes
    assert v1["hechos"][0]["numero"] == 2 and v1["hechos"][0]["atraso_dias_habiles"] == 1
    assert "si_no_hay_respuesta" not in v1["hechos"][0]
    [v2] = dias.ciclo(octubre(20, 10))              # V + 2, el martes: avisa que va a escalar
    assert v2["hechos"][0]["numero"] == 3 and v2["hechos"][0]["atraso_dias_habiles"] == 2
    assert v2["hechos"][0]["si_no_hay_respuesta"]["se_avisa_a"] == ["Ismael"]

    [v3] = dias.ciclo(octubre(21, 10))              # V + 3, el miércoles: escala

    assert v3["persona"] == "Ismael" and _aviso(v3) == "falta_de_respuesta"
    assert v3["hechos"][0]["atraso_dias_habiles"] == 3
    assert v3["hechos"][0]["pedido_desde"] == "2026-10-16"
    assert espera_del_estado(conn)["escalado_en"] == octubre(21, 10)
    [escalamiento] = avisos_guardados(conn, "escalamiento")
    assert escalamiento["programado_para"] == octubre(21, 10)
    assert dias.ciclo(octubre(22, 10)) == []
    assert len(lo_que_salio_para(conn, mundo, "Marcos")) == 4    # previo y tres pedidos
    assert len(lo_que_salio_para(conn, mundo, "Ismael")) == 1
    _todo_sale_en_dias_habiles(conn)


def test_un_ciclo_que_corre_el_sabado_deja_el_paso_para_el_lunes(conn, mundo, dias):
    """El ciclo parado el viernes que vuelve el sábado guarda el pedido de V para la hora de
    salida del lunes, no para el fin de semana; después, un paso por día hábil, y el que avisa
    que va a escalar nunca se saltea."""
    _vence(conn, mundo, 16)
    dias.ciclo(octubre(13, 10))                     # el aviso previo

    assert dias.ciclo(octubre(17, 10)) == []        # sábado: se guarda, no sale
    [pedido] = avisos_guardados(conn, "pedido_de_estado")
    assert pedido["estado"] == "guardado" and pedido["programado_para"] == octubre(19, 10)
    assert dias.ciclo(octubre(18, 10)) == []

    [v] = dias.ciclo(octubre(19, 10))
    assert v["hechos"][0]["numero"] == 1
    [v1] = dias.ciclo(octubre(20, 10))
    assert v1["hechos"][0]["numero"] == 2
    [v2] = dias.ciclo(octubre(21, 10))
    assert v2["hechos"][0]["numero"] == 3 and "si_no_hay_respuesta" in v2["hechos"][0]
    [v3] = dias.ciclo(octubre(22, 10))
    assert _aviso(v3) == "falta_de_respuesta" and v3["persona"] == "Ismael"
    _todo_sale_en_dias_habiles(conn)


def test_un_ciclo_parado_todo_el_fin_de_semana_retoma_un_paso_por_dia(conn, mundo, dias):
    """Sin ciclos del viernes al lunes: el lunes sale el pedido de V, no un salto al
    escalamiento; la escalera nunca da dos pasos el mismo día hábil."""
    _vence(conn, mundo, 16)
    dias.ciclo(octubre(13, 10))

    [v] = dias.ciclo(octubre(19, 10))
    assert v["hechos"][0]["numero"] == 1
    assert dias.ciclo(octubre(19, 15))[0]["hechos"][0]["aviso"] == "repeticion_del_dia"
    assert dias.ciclo(octubre(19, 16)) == []
    [v1] = dias.ciclo(octubre(20, 10))
    assert v1["hechos"][0]["numero"] == 2
    [v2] = dias.ciclo(octubre(21, 10))
    assert v2["hechos"][0]["numero"] == 3 and "si_no_hay_respuesta" in v2["hechos"][0]
    [v3] = dias.ciclo(octubre(22, 10))
    assert _aviso(v3) == "falta_de_respuesta"


# --- El aviso previo cruza el fin de semana --------------------------------------------------

def test_el_aviso_previo_cuenta_sus_dias_habiles_por_encima_del_fin_de_semana(conn, mundo, dias):
    """Vence el martes 20: los tres días hábiles antes son el viernes 16, el lunes 19 y el
    martes 20, así que el aviso previo sale el jueves 15, no el viernes ni el fin de semana."""
    _vence(conn, mundo, 20)

    assert dias.ciclo(octubre(14, 10)) == []        # faltan 4
    [previo] = dias.ciclo(octubre(15, 10))
    assert _aviso(previo) == "vencimiento_proximo"
    assert previo["hechos"][0]["dias_habiles_hasta_el_vencimiento"] == 3
    assert dias.ciclo(octubre(16, 10)) == []
    _el_fin_de_semana_no_hace_nada(conn, dias, 17)
    assert dias.ciclo(octubre(19, 10)) == []        # uno solo

    [v] = dias.ciclo(octubre(20, 10))
    assert _aviso(v) == "pedido_de_estado" and v["hechos"][0]["numero"] == 1
    assert [a["tipo"] for a in avisos_guardados(conn)] == ["aviso_previo", "pedido_de_estado"]


def test_el_aviso_previo_salta_el_fin_de_semana_y_el_feriado(conn, mundo, dias):
    """Vence el miércoles 14: el sábado 10, el domingo 11 y el feriado del lunes 12 no cuentan;
    los tres días hábiles antes son el viernes 9, el martes 13 y el miércoles 14."""
    _vence(conn, mundo, 14)

    assert dias.ciclo(octubre(7, 10)) == []         # faltan 4: 8, 9, 13 y 14
    [previo] = dias.ciclo(octubre(8, 10))
    assert previo["hechos"][0]["dias_habiles_hasta_el_vencimiento"] == 3
    for momento in (octubre(9, 10), octubre(10, 10), octubre(11, 10), octubre(12, 10),
                    octubre(13, 10)):
        assert dias.ciclo(momento) == []
    [v] = dias.ciclo(octubre(14, 10))
    assert _aviso(v) == "pedido_de_estado"


# --- La escalera comprimida de una tarea corta, a través del fin de semana --------------------

def test_una_tarea_cargada_el_viernes_que_vence_el_lunes_no_saltea_ningun_paso(conn, mundo,
                                                                                  dias):
    """Un solo día hábil por delante: el aviso previo sale enseguida (comprimido), y después de V
    los pasos siguen uno por día hábil, con el que avisa que va a escalar antes del escalamiento."""
    _vence(conn, mundo, 19)

    [previo] = dias.ciclo(octubre(16, 11))
    assert _aviso(previo) == "vencimiento_proximo"
    assert previo["hechos"][0]["dias_habiles_hasta_el_vencimiento"] == 1
    _el_fin_de_semana_no_hace_nada(conn, dias, 17)

    pasos = [dias.ciclo(octubre(dia, 10)) for dia in (19, 20, 21, 22)]

    assert [[(p["persona"], _aviso(p)) for p in paso] for paso in pasos] == [
        [("Marcos", "pedido_de_estado")], [("Marcos", "pedido_de_estado")],
        [("Marcos", "pedido_de_estado")], [("Ismael", "falta_de_respuesta")]]
    assert "si_no_hay_respuesta" in pasos[2][0]["hechos"][0]
    assert dias.ciclo(octubre(23, 10)) == []
    _todo_sale_en_dias_habiles(conn)


def test_una_tarea_cargada_el_sabado_que_vence_el_lunes_no_recibe_un_previo_vencido(conn, mundo,
                                                                                     dias):
    """Cargada en el fin de semana, el aviso previo se guarda para el lunes, que ya es V: un
    aviso previo que llega al vencimiento ya no es previo (`avisos`, `ya_vencio`) y se omite;
    ese lunes sale sólo el pedido de estado, y la escalera sigue completa."""
    _vence(conn, mundo, 19)

    assert dias.ciclo(octubre(17, 11)) == []
    [previo] = avisos_guardados(conn, "aviso_previo")
    assert previo["estado"] == "guardado" and previo["programado_para"] == octubre(19, 10)

    [v] = dias.ciclo(octubre(19, 10))

    assert _aviso(v) == "pedido_de_estado" and v["hechos"][0]["numero"] == 1
    [previo] = avisos_guardados(conn, "aviso_previo")
    assert previo["estado"] == "omitido" and previo["motivo_omision"] == "ya_vencio"
    [v1] = dias.ciclo(octubre(20, 10))
    [v2] = dias.ciclo(octubre(21, 10))
    assert "si_no_hay_respuesta" in v2["hechos"][0]
    [v3] = dias.ciclo(octubre(22, 10))
    assert _aviso(v3) == "falta_de_respuesta"
    assert v1["hechos"][0]["numero"] == 2
