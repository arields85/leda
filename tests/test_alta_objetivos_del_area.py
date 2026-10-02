"""F-B11: el alta ofrece sólo los objetivos del área de quien pide. Lo que cruza
áreas pasa por una dependencia de una tarea propia, no por pedir una tarea de
otro sector. Con un solo objetivo propio se completa solo; el estratégico (y un
objetivo sin área, dato anterior a la migración 0027) sólo se ofrece si el área
no tiene objetivos propios."""

from __future__ import annotations

import pytest

from leda import ingreso_tareas as I
from leda.db import admin, espacio

from tests.test_alta_guiada_flujo import (TITULO, _campo, _conjunto_activo,
                                          _empezar)
from tests.test_task_intake import NOW, _active_choices


def _dar_area(conn, world, area, *titulos, tipo=None):
    ws = world["north-lab"]
    with admin(conn) as cur:
        for titulo in titulos:
            cur.execute(
                """update objective set area_id = %s
                    where workspace_id = %s and titulo = %s""",
                (ws["areas"][area] if area else None, ws["id"], titulo))
    conn.commit()


def _titulos(opciones) -> set[str]:
    return {I.etiqueta_sin_icono(e) for e in opciones} - {"Otra opción", "Ver más"}


def _agregar(conn, world, titulo, tipo, area=None):
    ws = world["north-lab"]
    with admin(conn) as cur:
        cur.execute(
            """insert into objective (workspace_id, tipo, titulo, estado, area_id)
               values (%s, %s, %s, 'activo', %s)""",
            (ws["id"], tipo, titulo, ws["areas"][area] if area else None))
    conn.commit()


def _alta(conn, world):
    """Taylor Quinn (área field) empieza el alta con el título dado."""
    with espacio(conn, world["north-lab"]["id"]) as cur:
        actor, outcome = _empezar(cur, world, title=TITULO)
        return outcome.request_id, _conjunto_activo(cur, outcome.request_id), \
            _active_choices(cur, outcome.request_id), \
            _campo(cur, outcome.request_id, "objective")


def test_con_varios_objetivos_propios_ofrece_solo_los_de_su_area(intake_world, conn):
    _dar_area(conn, intake_world, "field",
              "Reduce service delay 1", "Expand regional coverage 1")
    _dar_area(conn, intake_world, "quality", "Raise delivery quality 1")
    _, activo, opciones, _ = _alta(conn, intake_world)
    assert activo == "objective"
    assert _titulos(opciones) == {"Reduce service delay 1",
                                  "Expand regional coverage 1"}


def test_con_un_solo_objetivo_propio_se_completa_solo(intake_world, conn):
    _dar_area(conn, intake_world, "field", "Reduce service delay 1")
    _dar_area(conn, intake_world, "quality", "Raise delivery quality 1",
              "Expand regional coverage 1")
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        _, outcome = _empezar(cur, intake_world, title=TITULO)
        objetivo = _campo(cur, outcome.request_id, "objective")
        assert objetivo["estado"] == "confirmed"
        assert objetivo["valor"]["title"] == "Reduce service delay 1"
        assert objetivo["proposed_by"] == "server"
        # La pregunta que sigue ya no es la del objetivo.
        assert _conjunto_activo(cur, outcome.request_id) != "objective"


def test_el_estrategico_no_se_ofrece_si_el_area_tiene_objetivos_propios(
        intake_world, conn):
    _agregar(conn, intake_world, "Vincular todo", "estrategico")
    _dar_area(conn, intake_world, "field", "Reduce service delay 1",
              "Expand regional coverage 1")
    _dar_area(conn, intake_world, "quality", "Raise delivery quality 1")
    _, _, opciones, _ = _alta(conn, intake_world)
    assert "Vincular todo" not in _titulos(opciones)


def test_sin_objetivos_propios_se_ofrece_el_estrategico_y_nunca_los_de_otra_area(
        intake_world, conn):
    _agregar(conn, intake_world, "Vincular todo", "estrategico")
    _dar_area(conn, intake_world, "quality", "Reduce service delay 1",
              "Raise delivery quality 1", "Expand regional coverage 1")
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        _, outcome = _empezar(cur, intake_world, title=TITULO)
        objetivo = _campo(cur, outcome.request_id, "objective")
        # El único posible: el estratégico, sin preguntar.
        assert objetivo["estado"] == "confirmed"
        assert objetivo["valor"]["title"] == "Vincular todo"


def test_un_objetivo_sin_area_se_ofrece_solo_si_el_area_no_tiene_propios(
        intake_world, conn):
    # Dato viejo: tres objetivos sin área y ninguno del área de quien pide.
    _, activo, opciones, _ = _alta(conn, intake_world)
    assert activo == "objective"
    assert _titulos(opciones) == {"Reduce service delay 1", "Raise delivery quality 1",
                                  "Expand regional coverage 1"}
    # Apenas el área tiene uno propio, los sin área dejan de ofrecerse.


def test_un_objetivo_sin_area_deja_de_ofrecerse_cuando_el_area_tiene_propios(
        intake_world, conn):
    _dar_area(conn, intake_world, "field", "Reduce service delay 1",
              "Raise delivery quality 1")
    _, _, opciones, _ = _alta(conn, intake_world)
    assert "Expand regional coverage 1" not in _titulos(opciones)


@pytest.mark.parametrize("escrito", ["Raise delivery", "raise delivery quality 1"])
def test_escribir_el_nombre_de_un_objetivo_de_otra_area_no_lo_encuentra(
        escrito, intake_world, conn):
    _dar_area(conn, intake_world, "field", "Reduce service delay 1",
              "Expand regional coverage 1")
    _dar_area(conn, intake_world, "quality", "Raise delivery quality 1")
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        actor, outcome = _empezar(cur, intake_world, title=TITULO)
        I._open_entity_page(cur, I._request(cur, outcome.request_id), actor,
                            "objective", escrito, 0, NOW)
        ofrecidas = _titulos(_active_choices(cur, outcome.request_id))
        assert "Raise delivery quality 1" not in ofrecidas
        assert ofrecidas   # se ofrecen las propias, no un callejón sin salida
