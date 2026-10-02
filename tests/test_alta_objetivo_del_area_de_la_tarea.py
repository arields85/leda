"""C0-1 y C0-2 (ronda C0-A, 2026-10-02): los objetivos que ofrece el alta salen del
área de la TAREA, que es la de quien es responsable (igual que el área y el
aprobador), no del área de quien escribe. Y una tarea cuelga sólo de un objetivo
operativo (mecánica §1): el estratégico y los objetivos sin área no se ofrecen nunca.

Falla real: Ismael (Dirección, sin objetivos propios) pidió una tarea para Marcos
(OT). La búsqueda cayó en los objetivos sin área, el estratégico era la única opción
y se completó solo: el resumen decía "Área: OT" con el objetivo estratégico.

Acá quien escribe es Taylor Quinn (área field) y la tarea es para Sam Noble (área
quality). El modelo se guiona; todo pasa por el webhook real.
"""

from __future__ import annotations

import pytest
from psycopg.types.json import Jsonb

from leda import ingreso_tareas as I
from leda.db import admin, espacio

from tests.test_alta_conducida import Chat, _cuerpos, _en, _modelo, salida
from tests.test_alta_conducida import conversada  # noqa: F401  (fixture)
from tests.test_alta_guiada_flujo import TITULO, _empezar

ESTRATEGICO = "Vincular todo"


def _objetivos(conn, world, **por_area):
    """Pone el área (o ninguna, con `None`) de los objetivos operativos del espacio y
    agrega el estratégico, que nunca tiene área."""
    ws = world["north-lab"]
    with admin(conn) as cur:
        for titulo, area in por_area.items():
            cur.execute(
                """update objective set area_id = %s
                    where workspace_id = %s and titulo = %s""",
                (ws["areas"][area] if area else None, ws["id"],
                 titulo.replace("_", " ")))
        cur.execute(
            """insert into objective (workspace_id, tipo, titulo, estado)
               values (%s, 'estrategico', %s, 'activo')""",
            (ws["id"], ESTRATEGICO))
    conn.commit()


def _sin_icono(etiquetas) -> list[str]:
    return [I.etiqueta_sin_icono(e) for e in etiquetas]


def _para_sam_noble(c: Chat, texto="Anotado. ¿A qué objetivo pertenece?"):
    """Primero el pedido; después, en un segundo mensaje, para quién es."""
    c.modelo.conducciones.append(salida("¿Qué hay que hacer?", pregunta=["title"]))
    c.escribir("necesito crear una tarea")
    id_noble = c.id_de("responsible", "Sam Noble")
    c.modelo.conducciones.append(salida(
        texto, valores={"title": {"texto": "Calibrar los sensores"},
                        "responsible": {"opcion_id": id_noble}},
        pregunta=["objective"], botones="objective"))
    return c.escribir("calibrar los sensores, la hace Sam Noble")


# ------------------------------------------- C0-1: el área de quien es responsable

def test_pedida_para_otra_area_ofrece_los_objetivos_operativos_del_responsable(
        conversada, conn, monkeypatch):  # noqa: F811
    _objetivos(conn, conversada, Reduce_service_delay_1="quality",
               Raise_delivery_quality_1="quality", Expand_regional_coverage_1=None)
    c = Chat(conn, monkeypatch, conversada, _modelo())

    _para_sam_noble(c)

    assert c.campo("objective")["estado"] == "missing"
    assert _sin_icono(c.etiquetas()) == ["Raise delivery quality 1",
                                         "Reduce service delay 1"]
    # El turno siguiente ve sólo esos dos: ni el estratégico ni el objetivo sin área.
    c.modelo.conducciones.append(salida("¿A cuál?", pregunta=["objective"],
                                        botones="objective"))
    c.escribir("no sé cuál")
    titulos = {o["titulo"] for o in c.hechos()["opciones"]["objective"]}
    assert titulos == {"Raise delivery quality 1", "Reduce service delay 1"}


def test_con_un_solo_operativo_del_area_se_completa_ese_y_nunca_el_estrategico(
        conversada, conn, monkeypatch):  # noqa: F811
    _objetivos(conn, conversada, Reduce_service_delay_1="quality",
               Raise_delivery_quality_1="field", Expand_regional_coverage_1="field")
    c = Chat(conn, monkeypatch, conversada, _modelo())

    _para_sam_noble(c)
    c.modelo.conducciones.append(salida("¿Para cuándo?", pregunta=["due_date"]))
    c.escribir("dale")

    objetivo = c.campo("objective")
    assert objetivo["estado"] == "confirmed"
    assert objetivo["valor"]["title"] == "Reduce service delay 1"


def test_antes_de_saber_el_responsable_se_ofrecen_los_de_las_areas_posibles(
        conversada, conn):  # noqa: F811
    """Taylor puede asignarse a sí misma (field) o a quienes aprueba (field y
    quality): la tarea puede ser de cualquiera de las dos áreas. Nunca el
    estratégico ni un objetivo sin área."""
    _objetivos(conn, conversada, Reduce_service_delay_1="quality",
               Raise_delivery_quality_1="field", Expand_regional_coverage_1=None)
    with espacio(conn, conversada["north-lab"]["id"]) as cur:
        actor, outcome = _empezar(cur, conversada, title=TITULO)
        request = I._request(cur, outcome.request_id)
        candidatas, _ = I._entity_candidates(cur, request, actor, "objective", None)
    assert {c[0] for c in candidatas} == {"Reduce service delay 1",
                                          "Raise delivery quality 1"}


# ------------------------------------------- C0-2: sin operativo, el estado real

def test_sin_objetivo_operativo_en_el_area_no_completa_y_dice_el_estado_real(
        conversada, conn, monkeypatch):  # noqa: F811
    _objetivos(conn, conversada, Reduce_service_delay_1="field",
               Raise_delivery_quality_1="field", Expand_regional_coverage_1="field")
    c = Chat(conn, monkeypatch, conversada, _modelo())

    nuevas = _para_sam_noble(c)

    assert c.campo("objective")["estado"] == "missing"
    (texto,) = _cuerpos(nuevas)
    assert "Quality Guild" in texto and "objetivo operativo" in texto
    assert "decime" in texto                # otra persona, de un área con objetivos
    assert _sin_icono(c.etiquetas()) == ["Cancelar borrador"]
    # La conversación sigue abierta: el mensaje siguiente lo atiende el modelo, y
    # con un responsable de otra área la pregunta del objetivo sigue normal.
    llamadas = len(c.modelo.conducidos)
    id_north = c.id_de("responsible", "Sam North")
    c.modelo.conducciones.append(salida(
        "Listo, la hace Sam North. ¿A qué objetivo pertenece?", intencion="corrige",
        corrige=["responsible"], valores={"responsible": {"opcion_id": id_north}},
        pregunta=["objective"], botones="objective"))
    nuevas = c.escribir("entonces que la haga Sam North")
    assert len(c.modelo.conducidos) == llamadas + 1
    assert _cuerpos(nuevas) == ["Listo, la hace Sam North. ¿A qué objetivo pertenece?"]
    assert len(c.etiquetas()) == 3


def test_sin_objetivo_operativo_el_modelo_no_puede_pedir_el_objetivo(
        conversada, conn, monkeypatch):  # noqa: F811
    _objetivos(conn, conversada, Reduce_service_delay_1="field",
               Raise_delivery_quality_1="field", Expand_regional_coverage_1="field")
    c = Chat(conn, monkeypatch, conversada, _modelo())
    _para_sam_noble(c)

    # El aviso ya se dio: el modelo sigue la charla, pero si pide el objetivo, que
    # no tiene de dónde salir, la respuesta es otra vez el estado real.
    c.modelo.conducciones.append(salida(
        "Dale. ¿A qué objetivo pertenece?", valores={"due_date": {"fecha_iso": _en(3)}},
        pregunta=["objective"], botones="objective"))
    nuevas = c.escribir("para el viernes")

    assert c.campo("due_date")["estado"] == "confirmed"
    (texto,) = _cuerpos(nuevas)
    assert "Quality Guild" in texto and "objetivo operativo" in texto
    assert _sin_icono(c.etiquetas()) == ["Cancelar borrador"]
    # Y se puede cancelar escribiendo.
    c.modelo.conducciones.append(salida("Listo, la cancelo.", intencion="cancelar"))
    c.escribir("cancelala")
    assert c.estado() == "cancelled"


# ---------------------------- el objetivo de otra área se saca, y se dice

def test_cambiar_el_responsable_a_otra_area_saca_el_objetivo_y_lo_dice(
        conversada, conn, monkeypatch):  # noqa: F811
    _objetivos(conn, conversada, Reduce_service_delay_1="field",
               Raise_delivery_quality_1="quality", Expand_regional_coverage_1="quality")
    c = Chat(conn, monkeypatch, conversada, _modelo(
        salida("¿Qué hay que hacer?", pregunta=["title"])))
    c.escribir("necesito crear una tarea")
    id_yo = next(o["id"] for o in c.hechos()["opciones"]["responsible"]
                 if o.get("es_quien_escribe"))
    c.modelo.conducciones.append(salida(
        "Anotado. ¿Para cuándo?",
        valores={"title": {"texto": "Calibrar los sensores"},
                 "responsible": {"opcion_id": id_yo}},
        pregunta=["due_date"]))
    c.escribir("calibrar los sensores, la hago yo")
    # Field tiene un solo operativo: se completó solo.
    assert c.campo("objective")["valor"]["title"] == "Reduce service delay 1"

    id_noble = c.id_de("responsible", "Sam Noble")
    c.modelo.conducciones.append(salida(
        "Listo, la hace Sam Noble. ¿Para cuándo?", intencion="corrige",
        corrige=["responsible"], valores={"responsible": {"opcion_id": id_noble}},
        pregunta=["due_date"]))
    nuevas = c.escribir("no, mejor que la haga Sam Noble")

    assert c.campo("objective")["estado"] == "missing"
    (texto,) = _cuerpos(nuevas)
    assert "Reduce service delay 1" in texto and "Quality Guild" in texto
    assert sorted(_sin_icono(c.etiquetas())) == ["Expand regional coverage 1",
                                                 "Raise delivery quality 1"]


@pytest.mark.parametrize("responsable", ["Taylor Quinn", "Sam North"])
def test_un_area_sin_operativos_no_ofrece_nada_ni_el_estrategico(
        responsable, conversada, conn):  # noqa: F811
    """Quien escribe y responsable de un área sin operativos propios (como
    Dirección): ninguna opción, nunca el estratégico."""
    _objetivos(conn, conversada, Reduce_service_delay_1="quality",
               Raise_delivery_quality_1="quality", Expand_regional_coverage_1="quality")
    persona = conversada["north-lab"]["people"][responsable]
    with espacio(conn, conversada["north-lab"]["id"]) as cur:
        actor, outcome = _empezar(cur, conversada, title=TITULO)
        cur.execute(
            """update task_intake_field set estado = 'confirmed', valor = %s
                where request_id = %s and campo = 'responsible'""",
            (Jsonb({"id": persona["membership_id"], "name": persona["name"]}),
             outcome.request_id))
        request = I._request(cur, outcome.request_id)
        candidatas, _ = I._entity_candidates(cur, request, actor, "objective", None)
        assert candidatas == []
        assert I._unica_opcion(cur, request, actor, "objective") is None
