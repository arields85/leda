"""El bloqueo viejo (`leda.motor.bloqueo_viejo`; C-5, porción 5; decisión 7 del usuario,
2026-10-08, opción A; mecánica §8; conversación 36).

Un bloqueo que sigue abierto a los días hábiles del espacio (`bloqueos.escala_solo_a_los_dias`;
5 si no está) se le informa al referente de la tarea, una sola vez, aunque la cadena se mueva,
con la historia y las fechas que dio cada uno; si el referente es la persona trabada, a quien
aprueba su trabajo. No le pide nada. Queda registrado a quién y cuándo. Uno que se cerró antes,
no; y al salir se vuelve a mirar.
"""

from __future__ import annotations

import json
from datetime import timedelta

import pytest

from leda.db import admin
from leda.motor import hechos as hechos_mod
from leda.motor.avisos import TIPOS
from leda.motor.ia import Jugada

from tests.motor.ayudantes import AHORA, avisos_guardados, cuantas, octubre, uno
from tests.motor.test_aprobacion import Turnos
from tests.motor.test_cadena_del_bloqueo import _integrante, _membresia, _referente

CAUSA = "me falta la ip del servidor"
VIEJO = "bloqueo_que_sigue_abierto"
ARIEL, LUCAS = "Ariel De Simone", "Lucas Natuche"


def _dias_del_espacio(conn, mundo, valor) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'bloqueos', %s)""", (mundo["id"], json.dumps(valor)))
    conn.commit()


@pytest.fixture
def equipo(conn, espacio_con_escalera) -> Turnos:
    """Ariel y Lucas; Lucas es el referente del área de la tarea de Marcos."""
    mundo = espacio_con_escalera
    _integrante(conn, mundo, "Ariel", ARIEL, 81_040)
    _integrante(conn, mundo, "Lucas", LUCAS, 81_041)
    _referente(conn, mundo["area"], _membresia(mundo, "Lucas"))
    return Turnos(conn, mundo)


def _marcos_trabado(t: Turnos) -> None:
    """Marcos se traba el lunes 5, dice que lo destraba Ariel, y Ariel da una fecha."""
    t.dice("Marcos", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": CAUSA}))
    t.dice("Marcos", Jugada("anotar_quien_destraba", {"quien": "ariel"}))
    t.dice("Ariel", Jugada("decir_cuando_destraba",
                           {"tarea": "T1", "para_cuando": "2026-10-08",
                            "lo_que_dice": "te la paso el jueves"}))


def _viejos(conn) -> list[dict]:
    return avisos_guardados(conn, VIEJO)


def _para(dias, nombre: str) -> list[dict]:
    return [h for p in dias.ia.pedidos_de_redaccion if p["persona"] == nombre
            for h in p["hechos"] if h.get("aviso") == VIEJO]


def test_el_aviso_esta_declarado_con_su_significado():
    tipo = TIPOS[VIEJO]
    assert tipo.tipo_de_mensaje == "informativo" and not tipo.es_coordinacion
    for codigo in (VIEJO, "trabada_desde", "dias_habiles_trabada", "historia"):
        assert hechos_mod.significado(codigo), codigo


def test_a_los_dias_del_espacio_se_le_informa_una_vez_al_referente(conn, mundo, equipo, dias):
    _dias_del_espacio(conn, mundo, {"escala_solo_a_los_dias": 5})
    _marcos_trabado(equipo)

    # El viernes 9 lleva cuatro días hábiles (el lunes 12 es feriado): nada.
    dias.ciclo(octubre(9, 10))
    dias.ciclo(octubre(12, 10))
    assert _viejos(conn) == []

    # El martes 13, cinco: al referente del área, una vez, con la historia.
    dias.ciclo(octubre(13, 10))

    [aviso] = _viejos(conn)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Lucas")
    assert aviso["estado"] == "enviado"
    [hechos] = _para(dias, LUCAS)
    assert hechos["necesita_respuesta"] is False
    assert (hechos["tarea"], hechos["responsable"], hechos["causa"]) == (
        "Revisar el tablero", "Marcos", CAUSA)
    assert hechos["trabada_desde"] == "2026-10-05"
    assert hechos["dias_habiles_trabada"] == 5
    assert hechos["historia"] == [
        {"el": "2026-10-05", "de": "Marcos", "le_toca_a": ARIEL},
        {"el": "2026-10-05", "de": ARIEL, "para_cuando": "2026-10-08",
         "lo_que_dice": "te la paso el jueves"}]
    # Queda registrado a quién y cuándo se informó, con su auditoría.
    bloqueo = uno(conn, "select escalado_a::text a, escalado_en from blocker")
    assert bloqueo == {"a": _membresia(mundo, "Lucas"), "escalado_en": octubre(13, 10)}
    assert cuantas(conn, "audit_log", "accion = 'informar_bloqueo_que_sigue_abierto'") == 1
    # Nada a Marcos por esto, y no se repite.
    assert _para(dias, "Marcos") == []
    dias.ciclo(octubre(14, 10))
    dias.ciclo(octubre(15, 10))
    assert len(_viejos(conn)) == 1


def test_aunque_la_cadena_se_mueva_se_informa(conn, mundo, equipo, dias):
    _marcos_trabado(equipo)
    equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                {"tarea": "T1", "para_cuando": "2026-10-14",
                                 "lo_que_dice": "se me complico"}),
                at=octubre(12, 15))

    dias.ciclo(octubre(13, 10))

    [hechos] = _para(dias, LUCAS)
    assert hechos["historia"][-1] == {"el": "2026-10-12", "de": ARIEL,
                                      "para_cuando": "2026-10-14", "lo_que_dice": "se me complico"}


def test_si_el_referente_es_la_persona_trabada_va_a_quien_aprueba_su_trabajo(conn, mundo, equipo,
                                                                             dias):
    _referente(conn, mundo["area"], _membresia(mundo, "Marcos"))
    _marcos_trabado(equipo)

    dias.ciclo(octubre(13, 10))

    [aviso] = _viejos(conn)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Ismael")


def test_un_bloqueo_que_se_cerro_antes_no_se_informa(conn, mundo, equipo, dias):
    _marcos_trabado(equipo)
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}), texto="ya la tengo",
                at=octubre(8, 11))

    dias.ciclo(octubre(13, 10))

    assert _viejos(conn) == []


@pytest.mark.parametrize("valor", [None, {"escala_solo_a_los_dias": 0},
                                   {"escala_solo_a_los_dias": "cinco"},
                                   {"escala_solo_a_los_dias": True}, ["5"]])
def test_sin_un_valor_valido_del_espacio_vale_el_del_producto(conn, mundo, equipo, dias, valor):
    if valor is not None:
        _dias_del_espacio(conn, mundo, valor)
    _marcos_trabado(equipo)

    dias.ciclo(octubre(9, 10))
    assert _viejos(conn) == []
    dias.ciclo(octubre(13, 10))
    assert len(_viejos(conn)) == 1


def test_los_dias_son_los_del_espacio(conn, mundo, equipo, dias):
    _dias_del_espacio(conn, mundo, {"escala_solo_a_los_dias": 2})
    _marcos_trabado(equipo)

    dias.ciclo(octubre(6, 10))
    assert _viejos(conn) == []
    dias.ciclo(octubre(7, 10))
    assert len(_viejos(conn)) == 1


def test_al_salir_se_vuelve_a_mirar(conn, mundo, equipo, dias):
    _marcos_trabado(equipo)
    # Antes del horario se guarda para las 10:00; Marcos se destraba antes de que salga.
    dias.ciclo(octubre(13, 8))
    [aviso] = _viejos(conn)
    assert aviso["estado"] == "guardado"
    assert aviso["programado_para"] == octubre(13, 10)
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}), texto="ya la tengo",
                at=octubre(13, 8, 30))

    dias.ciclo(octubre(13, 10))

    [aviso] = _viejos(conn)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "ya_se_destrabo")
    assert uno(conn, "select escalado_en from blocker")["escalado_en"] is None
    assert _para(dias, LUCAS) == []


def test_va_a_quien_es_referente_al_salir(conn, mundo, equipo, dias):
    _marcos_trabado(equipo)
    dias.ciclo(octubre(13, 8))
    _referente(conn, mundo["area"], _membresia(mundo, "Ariel"))

    dias.ciclo(octubre(13, 10))

    [aviso] = _viejos(conn)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Ariel")
    assert uno(conn, "select escalado_a::text a from blocker")["a"] == _membresia(mundo, "Ariel")
