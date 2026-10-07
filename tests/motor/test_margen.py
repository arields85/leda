"""El margen para corregir (`leda.motor.margen`; decisión del usuario, 2026-10-07).

Prueba por Telegram real del 2026-10-07 (conversación 25): la IA anotó la fecha de Marcos en la
tarea equivocada y el aviso a Ismael salió un minuto después, antes de que Marcos pudiera leer la
respuesta de Leda y corregirla. Lo que una persona dice y le llega a otra espera un margen
(10 minutos, o el del espacio) antes de salir: una corrección dentro de ese margen retira el
aviso equivocado antes de que salga. Las respuestas de Leda y lo que manda por su cuenta (la
escalera) no esperan. Encima del margen sigue valiendo el horario: nunca sale fuera de él.

El reloj es el de las pruebas del motor: el lunes 5 de octubre de 2026, en Buenos Aires, con
el horario de 09:00 a 17:00 de lunes a viernes.
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.motor.margen import CLAVE_MARGEN, MARGEN_POR_OMISION, margen_para_corregir, \
    sale_con_margen

from tests.motor.ayudantes import octubre


def _configurar(conn, mundo, valor: str) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, %s, %s)""", (mundo["id"], CLAVE_MARGEN, valor))
    conn.commit()


def _margen(conn, mundo) -> timedelta:
    with espacio(conn, mundo["id"]) as cur:
        margen = margen_para_corregir(cur, mundo["id"])
    conn.commit()
    return margen


def _sale(conn, mundo, ahora):
    with espacio(conn, mundo["id"]) as cur:
        cal = Calendario.desde_base(cur, mundo["id"])
        sale = sale_con_margen(cur, cal, mundo["id"], ahora)
    conn.commit()
    return sale


def test_sin_configurar_el_margen_es_de_diez_minutos(conn, mundo):
    assert MARGEN_POR_OMISION == timedelta(minutes=10)
    assert _margen(conn, mundo) == timedelta(minutes=10)


@pytest.mark.parametrize("valor, minutos", [("3", 3), ("30", 30), ("0", 0)])
def test_el_espacio_cambia_el_margen(conn, mundo, valor, minutos):
    _configurar(conn, mundo, valor)
    assert _margen(conn, mundo) == timedelta(minutes=minutos)


@pytest.mark.parametrize("valor", ['"diez"', "-5", "true", "null"])
def test_un_margen_que_no_vale_usa_el_del_producto(conn, mundo, valor):
    """Del lado seguro: un valor que no es un número de minutos no deja salir antes el aviso."""
    _configurar(conn, mundo, valor)
    assert _margen(conn, mundo) == MARGEN_POR_OMISION


@pytest.mark.parametrize("ahora, sale", [
    (octubre(5, 10, 30), octubre(5, 10, 40)),       # en la jornada: el margen, nada más
    (octubre(5, 9, 30), octubre(5, 10)),            # nunca antes de la hora de salida
    (octubre(5, 9, 55), octubre(5, 10, 5)),         # ni antes del margen
    (octubre(5, 16, 55), octubre(6, 10)),           # el margen termina fuera del horario
    (octubre(9, 16, 55), octubre(12, 10)),          # viernes: el lunes siguiente
    (octubre(5, 20), octubre(6, 10)),               # de noche: el día hábil siguiente
], ids=["jornada", "antes-de-la-hora", "margen-pasa-la-hora", "fin-de-jornada", "viernes",
        "noche"])
def test_sale_despues_del_margen_y_dentro_del_horario(conn, mundo, ahora, sale):
    assert _sale(conn, mundo, ahora) == sale


def test_el_margen_del_espacio_cuenta_para_cuando_sale(conn, mundo):
    _configurar(conn, mundo, "3")
    assert _sale(conn, mundo, octubre(5, 10, 30)) == octubre(5, 10, 33)
