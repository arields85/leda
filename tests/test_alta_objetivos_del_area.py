"""Los objetivos que ofrece el alta guiada: los operativos del área de la tarea (C0-1
y C0-2, 2026-10-02; reemplaza la regla F-B11 de "los del área de quien pide").

Antes de elegir responsable, la tarea puede ser del área de cualquiera de las
personas que pueden serlo; acá Taylor Quinn (field) sólo puede asignarse a gente de
field (Sam Noble, de quality, queda inactivo), así que la tarea es de field. Una
tarea cuelga sólo de un objetivo operativo: el estratégico y un objetivo sin área
(dato anterior a la migración 0027) no se ofrecen nunca, ni siquiera si el área no
tiene ninguno propio; entonces se dice el estado real.
"""

from __future__ import annotations

import pytest

from leda import ingreso_tareas as I
from leda.db import admin, espacio

from tests.test_alta_guiada_flujo import (TITULO, _campo, _conjunto_activo,
                                          _cuerpos, _empezar)
from tests.test_task_intake import NOW, _active_choices


@pytest.fixture
def solo_field(intake_world, conn):
    """Taylor Quinn sólo puede asignar tareas en field."""
    ws = intake_world["north-lab"]
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (ws["people"]["Sam Noble"]["membership_id"],))
    conn.commit()
    return intake_world


def _dar_area(conn, world, area, *titulos):
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


def test_con_varios_operativos_del_area_ofrece_solo_esos(solo_field, conn):
    _dar_area(conn, solo_field, "field",
              "Reduce service delay 1", "Expand regional coverage 1")
    _dar_area(conn, solo_field, "quality", "Raise delivery quality 1")
    _, activo, opciones, _ = _alta(conn, solo_field)
    assert activo == "objective"
    assert _titulos(opciones) == {"Reduce service delay 1",
                                  "Expand regional coverage 1"}


def test_con_un_solo_operativo_del_area_se_completa_solo(solo_field, conn):
    _dar_area(conn, solo_field, "field", "Reduce service delay 1")
    _dar_area(conn, solo_field, "quality", "Raise delivery quality 1",
              "Expand regional coverage 1")
    with espacio(conn, solo_field["north-lab"]["id"]) as cur:
        _, outcome = _empezar(cur, solo_field, title=TITULO)
        objetivo = _campo(cur, outcome.request_id, "objective")
        assert objetivo["estado"] == "confirmed"
        assert objetivo["valor"]["title"] == "Reduce service delay 1"
        assert objetivo["proposed_by"] == "server"
        # La pregunta que sigue ya no es la del objetivo.
        assert _conjunto_activo(cur, outcome.request_id) != "objective"


def test_el_estrategico_no_se_ofrece_aunque_haya_operativos(solo_field, conn):
    _agregar(conn, solo_field, "Vincular todo", "estrategico")
    _, _, opciones, _ = _alta(conn, solo_field)
    assert "Vincular todo" not in _titulos(opciones)
    assert len(_titulos(opciones)) == 3


@pytest.mark.parametrize("de_otra_area", ["quality", None],
                         ids=["de_otra_area", "sin_area"])
def test_sin_operativos_del_area_dice_el_estado_real_y_nunca_completa_otro(
        de_otra_area, solo_field, conn):
    """Ni el estratégico ni los de otra área ni los sin área: el estado real."""
    _agregar(conn, solo_field, "Vincular todo", "estrategico")
    _dar_area(conn, solo_field, de_otra_area, "Reduce service delay 1",
              "Raise delivery quality 1", "Expand regional coverage 1")
    with espacio(conn, solo_field["north-lab"]["id"]) as cur:
        _, outcome = _empezar(cur, solo_field, title=TITULO)
        assert _campo(cur, outcome.request_id, "objective")["estado"] == "missing"
        assert _titulos(_active_choices(cur, outcome.request_id)) == {
            "Cancelar borrador"}
        assert any("objetivo operativo" in c for c in _cuerpos(cur, outcome.request_id))


@pytest.mark.parametrize("escrito", ["Raise delivery", "raise delivery quality 1"])
def test_escribir_el_nombre_de_un_objetivo_de_otra_area_no_lo_encuentra(
        escrito, solo_field, conn):
    _dar_area(conn, solo_field, "field", "Reduce service delay 1",
              "Expand regional coverage 1")
    _dar_area(conn, solo_field, "quality", "Raise delivery quality 1")
    with espacio(conn, solo_field["north-lab"]["id"]) as cur:
        actor, outcome = _empezar(cur, solo_field, title=TITULO)
        I._open_entity_page(cur, I._request(cur, outcome.request_id), actor,
                            "objective", escrito, 0, NOW)
        ofrecidas = _titulos(_active_choices(cur, outcome.request_id))
        assert "Raise delivery quality 1" not in ofrecidas
        assert ofrecidas   # se ofrecen las propias, no un callejón sin salida
