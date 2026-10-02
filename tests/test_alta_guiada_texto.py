"""El alta guiada sobre el flujo de un mensaje (ADR 0014, F3b): un dato con una
sola opción no se pregunta, "Otra opción" sólo aparece si hay otra, y los textos
(preguntas y resumen) salen por `redaccion` sin jerga.

Cubre R4c-H7 (los límites "(hasta N)"), R4c-H8 (claves internas en el resumen),
R4c-H9 (el cierre del resumen de quien pide y "Sin descripción") y R4c-H10 (el
área con una sola opción).
"""

from __future__ import annotations

import pytest

from leda import ingreso_tareas as I
from leda import redaccion
from leda.pendientes import HERRAMIENTA_REVISION_BORRADOR
from leda.db import admin, espacio

from tests.test_alta_eleccion_confirmacion import (_alta_en_confirmacion,
                                                   _alta_enviada, _usuario)
from tests.test_alta_guiada_flujo import (TITULO, _campo, _conjunto_activo,
                                          _elegir, _empezar, _entrante, _slot)
from tests.test_task_intake import NOW, _active_choices, _actor, _choose

OTRA = I.OTHER


def _sin_otros_objetivos(conn, world, dejar: int) -> None:
    """Deja `dejar` objetivos activos en el espacio."""
    ws = world["north-lab"]
    with admin(conn) as cur:
        for objetivo in ws["objectives"][dejar:]:
            cur.execute("update objective set estado = 'cancelado' where id = %s",
                        (objetivo,))


def _como(cur, world, persona: str, **propuestas):
    """El alta de `persona` (no necesariamente quien tiene gente a cargo)."""
    ws = world["north-lab"]
    actor = _actor(cur, world, person=persona)
    chat = ws["people"][persona]["telegram"]
    inbound = _entrante(cur, ws["id"], actor, n=700 + chat % 1000, chat=chat)
    outcome = I.start(cur, actor, chat_id=chat, source_inbound_id=inbound,
                      source_raw_text="Necesito crear una tarea",
                      proposals=propuestas, now=NOW)
    return actor, outcome, chat


# ------------------------------------------------- un dato con una sola opción

def test_el_area_con_una_sola_opcion_no_se_pregunta_y_se_completa_sola(
        intake_world, conn):
    """R4c-H10: "Elegí el área" con una sola opción real más "Otra opción"."""
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, outcome = _empezar(cur, intake_world, title=TITULO)
        rid = outcome.request_id
        _elegir(cur, actor, rid, "Reduce service delay")
        _elegir(cur, actor, rid, "Sam North")
        area = _campo(cur, rid, "area")
        assert area["estado"] == "confirmed" and area["proposed_by"] == "server"
        assert area["valor"]["name"] == "Field Services"
        assert _slot(cur, rid) == "due_date"             # siguió con lo que falta
        cur.execute("""select count(*) n from task_intake_choice_set
                        where request_id = %s and campo = 'area'""", (rid,))
        assert cur.fetchone()["n"] == 0                  # nunca se preguntó


def test_un_objetivo_unico_se_completa_solo(intake_world, conn):
    _sin_otros_objetivos(conn, intake_world, dejar=1)
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world, title=TITULO)
        objetivo = _campo(cur, outcome.request_id, "objective")
        assert objetivo["estado"] == "confirmed"
        assert objetivo["proposed_by"] == "server"
        assert objetivo["valor"]["id"] == intake_world["north-lab"]["objectives"][0]
        assert _conjunto_activo(cur, outcome.request_id) == "responsible"


def test_quien_solo_puede_asignarse_a_si_mismo_no_elige_responsable_ni_area(
        intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, outcome, chat = _como(cur, intake_world, "Sam North", title=TITULO)
        rid = outcome.request_id
        _elegir(cur, actor, rid, "Reduce service delay", chat=chat)
        responsable = _campo(cur, rid, "responsible")
        assert responsable["estado"] == "confirmed"
        assert responsable["proposed_by"] == "server"
        assert responsable["valor"]["id"] == str(actor.membership_id)
        assert _campo(cur, rid, "area")["estado"] == "confirmed"
        assert _slot(cur, rid) == "due_date"


# ----------------------------------------------------------- "Otra opción"

def test_otra_opcion_solo_aparece_si_hay_otra_que_elegir(intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        _, todas = _empezar(cur, intake_world, chat=72101, title=TITULO)
        # Los tres objetivos entran en la pantalla: no hay otra opción posible.
        opciones = _active_choices(cur, todas.request_id)
        assert len(opciones) == 3 and OTRA not in opciones
        # Una propuesta que filtra a una sola de las tres: hay otras.
        _, filtrada = _empezar(cur, intake_world, chat=72102, title=TITULO,
                               objective="service delay")
        opciones = _active_choices(cur, filtrada.request_id)
        assert len(opciones) == 2 and OTRA in opciones


def test_con_mas_opciones_de_las_que_entran_hay_otra_y_ver_mas(intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with admin(conn) as cur:
        for n in range(12):
            cur.execute("""insert into objective (workspace_id, tipo, titulo, estado)
                           values (%s, 'operativo', %s, 'activo')""",
                        (ws, f"Objetivo de relleno {n:02d}"))
    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world, title=TITULO)
        opciones = _active_choices(cur, outcome.request_id)
        assert I.VER_MAS in opciones and OTRA in opciones


def test_modificar_no_ofrece_el_dato_que_no_tiene_otra_opcion(intake_world, conn):
    """Regla 3 del ADR 0013: sólo opciones posibles. El área sale de la persona
    responsable: con una sola, no hay nada que cambiar."""
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        actor = _actor(cur, intake_world)
        resultado = I.open_modify_picker(cur, actor, pid, NOW, via="boton")
        assert resultado is not None
        etiquetas = list(_active_choices(cur, rid))
    assert "Área" not in etiquetas
    assert {"Título", "Objetivo", "Responsable", "Fecha objetivo",
            "Criterio de aceptación", I.BACK_TO_SUMMARY} <= set(etiquetas)


# --------------------------------------------------------------- el resumen

def _resumen(conn, pid) -> str:
    with admin(conn) as cur:
        cur.execute("select resumen from pending_action where id = %s", (pid,))
        return cur.fetchone()["resumen"]


def test_el_resumen_no_dice_sin_descripcion_de_algo_que_nunca_se_pidio(
        intake_world, conn):
    """R4c-H9: "Descripción: Sin descripción" sin haberla preguntado."""
    _, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    resumen = _resumen(conn, pid)
    assert "Descripción" not in resumen and "Sin descripción" not in resumen
    assert "Título: Inspect relief valve" in resumen


def test_el_resumen_si_muestra_la_descripcion_que_la_persona_dio(
        intake_world, conn):
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North",
                                     description="Revisar antes del viernes")
    assert "Descripción: Revisar antes del viernes" in _resumen(conn, pid)


def test_el_resumen_nombra_los_tipos_de_evidencia_como_los_lee_una_persona(
        intake_world, conn):
    """R4c-H8: "Evidencia: explicacion, resultado_de_prueba, captura, archivo". Los
    nombres con tilde y mayúscula inicial: "Explicación, Resultado de prueba..."."""
    ws = intake_world["north-lab"]
    with admin(conn) as cur:
        cur.execute("""update task_evidence_policy
                          set evidencia_requerida =
                              array['explicacion', 'resultado_de_prueba', 'captura']
                        where workspace_id = %s""", (ws["id"],))
    _, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    resumen = _resumen(conn, pid)
    assert "Evidencia: Explicación, Resultado de prueba, Captura" in resumen
    assert "resultado_de_prueba" not in resumen and "explicacion" not in resumen


def test_el_resumen_de_quien_pide_dice_lo_que_hace_su_boton_y_el_de_quien_confirma_el_suyo(
        intake_world, conn):
    """R4c-H9: "Al confirmar se comprometen todos los datos mostrados." a quien
    sólo puede tocar Enviar a aprobación."""
    rid, para_confirmar = _alta_enviada(conn, intake_world)
    with admin(conn) as cur:
        cur.execute(
            """select p.resumen from pending_action p
                 join task_intake_request r on r.task_draft_id = p.draft_id
                where r.id = %s and p.herramienta = %s""",
            (rid, HERRAMIENTA_REVISION_BORRADOR))
        de_quien_pide = cur.fetchone()["resumen"]
    ultima = de_quien_pide.split("\n\n")[-1]
    assert "Enviar a aprobación" in ultima and "Morgan Hale 1" in ultima
    assert "Al confirmar" not in de_quien_pide and "Confirmar" not in ultima
    assert de_quien_pide.startswith("Resumen para revisar\n")
    de_quien_confirma = _resumen(conn, para_confirmar)
    ultima = de_quien_confirma.split("\n\n")[-1]
    assert "Confirmar" in ultima and "Enviar a aprobación" not in ultima
    # Los mismos datos, sólo cambia lo que se dice del botón y la primera línea que
    # le dice a quien confirma quién se lo manda (hallazgo (d), 2026-10-01).
    linea, _, sin_la_linea = de_quien_confirma.partition("\n\n")
    assert linea.endswith(" te manda esta tarea para que la confirmes.")
    assert (de_quien_pide.rpartition("\n\n")[0]
            == sin_la_linea.rpartition("\n\n")[0])


def test_quien_confirma_lo_suyo_ve_confirmar(intake_world, conn):
    _, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    assert _resumen(conn, pid).split("\n\n")[-1].startswith("Con Confirmar")


# ------------------------------------------------------------ las preguntas

def test_ninguna_pregunta_del_alta_lleva_limites_ni_pide_valores_exactos():
    textos = list(I._PREGUNTA_DEL_CAMPO.values())
    textos += [I.modify_text_prompt(campo, "lo que tenía")
               for campo in I.FREE_TEXT_NAMES]
    textos += [I._candidate_prompt(c) for c in ("objective", "responsible", "area")]
    textos += [I._proposal_prompt(c, "valor") for c in I._CONFIRMA_EL_CAMPO]
    for texto in textos:
        assert "hasta" not in texto and "exact" not in texto, texto


@pytest.mark.parametrize("variante", ["A", "B"])
def test_las_preguntas_y_el_resumen_leen_la_variante_del_espacio(
        variante, intake_world, conn, monkeypatch):
    """El alta lee la variante del espacio en cada pregunta y en el resumen."""
    ws = intake_world["north-lab"]["id"]
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'redaccion', %s::jsonb)""",
                    (ws, f'{{"variante": "{variante}"}}'))
    vistas = []
    real = redaccion.redactar_turno

    def espia(cur, workspace_id, resultado, v, **kw):
        vistas.append(v)
        # Sin modelo: con A, `proveedor` guionado vacío cae en la plantilla.
        return real(cur, workspace_id, resultado, "B")

    monkeypatch.setattr(I, "redactar_turno", espia)
    with espacio(conn, ws) as cur:
        _empezar(cur, intake_world, chat=72201)          # la pregunta del título
    _alta_en_confirmacion(conn, intake_world, responsable="Sam North")  # el resumen
    assert vistas and set(vistas) == {variante}
