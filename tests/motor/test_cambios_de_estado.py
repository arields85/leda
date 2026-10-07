"""Desde cuándo una tarea está en su estado (`leda.motor.cambios_de_estado`).

En la prueba chica se probaba a través del pedido de estado (`test_lo_que_sabe_la_cocina.py`);
acá se fijan sus dos partes: los cambios de un turno y la lectura de `desde`.
"""

from __future__ import annotations

from datetime import timedelta
from zoneinfo import ZoneInfo

from leda.db import admin, espacio
from leda.motor import cambios_de_estado as cambios
from leda.motor import registro

from tests.motor.ayudantes import AHORA

BA = ZoneInfo("America/Argentina/Buenos_Aires")


def _mover(conn, tarea: str, estado: str) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind, at)
                       values (%s, (select estado from task where id = %s), %s, 'persona',
                               clock_timestamp())""", (tarea, tarea, estado))


def _turno_con(conn, mundo, lista, at) -> None:
    with espacio(conn, mundo["id"]) as cur:
        registro.registrar_entrada(
            cur, workspace_id=mundo["id"],
            membership_id=mundo["personas"]["Marcos"]["membership_id"], entrante_id=None,
            ahora=at, jugadas=[], resultado={"hechos": [], cambios.CLAVE: lista},
            ia_nombre="guionada", latencia_ms=0, error=None)


def _desde(conn, mundo, estado):
    with espacio(conn, mundo["id"]) as cur:
        return cambios.desde(cur, mundo["tarea"], mundo["personas"]["Marcos"]["membership_id"],
                             estado, BA)


def test_los_cambios_del_turno_comparan_el_estado_al_empezar_y_al_terminar(conn, mundo):
    tareas = [{"id": mundo["tarea"], "estado": "asignada"}]
    with espacio(conn, mundo["id"]) as cur:
        assert cambios.del_turno(cur, tareas) == []
        assert cambios.del_turno(cur, []) == []
    _mover(conn, mundo["tarea"], "en_curso")
    with espacio(conn, mundo["id"]) as cur:
        assert cambios.del_turno(cur, tareas) == [
            {"task_id": mundo["tarea"], "de": "asignada", "a": "en_curso"}]


def test_desde_cuando_lo_sabe_el_motor_por_lo_que_anoto(conn, mundo):
    tarea = mundo["tarea"]
    assert _desde(conn, mundo, "asignada") is None          # como llega: no se dice
    assert _desde(conn, mundo, "en_curso") == cambios.DESCONOCIDO

    _turno_con(conn, mundo, [{"task_id": tarea, "de": "asignada", "a": "en_curso"}], AHORA)
    assert _desde(conn, mundo, "en_curso") == "2026-10-05"

    # Un bloqueo y su salida no cambian desde cuándo está en curso.
    _turno_con(conn, mundo, [{"task_id": tarea, "de": "en_curso", "a": "bloqueada"}],
               AHORA + timedelta(days=1))
    assert _desde(conn, mundo, "bloqueada") == "2026-10-06"
    _turno_con(conn, mundo, [{"task_id": tarea, "de": "bloqueada", "a": "en_curso"}],
               AHORA + timedelta(days=2))
    assert _desde(conn, mundo, "en_curso") == "2026-10-05"


def test_un_cambio_que_el_motor_no_explica_no_se_adivina(conn, mundo):
    _turno_con(conn, mundo, [{"task_id": mundo["tarea"], "de": "en_curso",
                              "a": "en_revision"}], AHORA)
    assert _desde(conn, mundo, "en_curso") == cambios.DESCONOCIDO
