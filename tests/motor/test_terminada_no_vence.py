"""Una tarea terminada no "vence" (`odd/tasks/correcciones-prueba-telegram.md`, T5).

Prueba por Telegram del 2026-10-12: a "pasame el link del dashboard de lotes", una tarea ya
terminada, el hecho `{resultado: solo_el_resumen, estado: terminada, vence: "2026-10-16", …}` hizo
escribir a Leda "La tarea está terminada y aprobada. … vence pasado mañana." Un vencimiento no dice
nada de una tarea que ya se cerró.

La regla, una sola vez, en el borde de la redacción (`hechos.para_redactar`), como los avisos sin
nombre ni hora (T3): un hecho que dice que su tarea está en un estado final (`terminada`,
`cancelada`) no le pasa a la IA cuándo vencía (`vence`, `fecha_objetivo`), ni el día de esa
fecha en `dias`. Los hechos de la cocina no cambian: la base, el registro de turnos, las pruebas y
la auditoría los leen. La pregunta al encargado por el detalle de una tarea (`detalle.py`) dice el
estado de la tarea, para que la regla también la alcance.
"""

from __future__ import annotations

import copy
import json

import pytest

from leda.motor import hechos
from leda.motor.ia import Jugada

from tests.conversaciones.carga import cargar
from tests.motor.ayudantes import (ProveedorFalso, avisos_guardados, ia_real_falsa,
                                   respuesta_de_texto)
from tests.motor.test_aprobacion import Turnos
from tests.motor.test_pedir_el_detalle import direccion  # noqa: F401 -- el fixture

HOY = "2026-10-14"
VENCE = "2026-10-16"
DASHBOARD = "Armar el dashboard de lotes"


def _lo_que_recibe_la_redaccion(pedido: dict) -> dict:
    """Los datos que la IA real recibe para redactar (con `dias`, como en `ia_real.redactar`)."""
    proveedor = ProveedorFalso([respuesta_de_texto("Hola.")])
    ia_real_falsa(proveedor).redactar(pedido)
    _, usuario = proveedor.pedidos[0]["cuerpo"]["messages"]
    return json.loads(usuario["content"])


def _pedido(*hechos_: dict) -> dict:
    return {"hoy": HOY, "persona": "Nahuel", "mensaje": "pasame el link del dashboard de lotes",
            "hechos": list(hechos_), "pregunta": None, "ultimos_turnos": []}


def _resumen(estado: str, **mas) -> dict:
    return {"jugada": "pedir_enlace", "resultado": "solo_el_resumen",
            "tarea": {"titulo": DASHBOARD}, "responsable": "Ariel De Simone",
            "estado": estado, "vence": VENCE, **mas}


# --- El borde de la redacción ------------------------------------------------------------------

@pytest.mark.parametrize("estado", ["terminada", "cancelada"])
def test_una_tarea_en_un_estado_final_no_le_dice_a_la_ia_cuando_vencia(estado):
    recibido = _lo_que_recibe_la_redaccion(_pedido(_resumen(estado)))
    texto = json.dumps(recibido["hechos"], ensure_ascii=False)
    assert VENCE not in texto
    # Tampoco el día de esa fecha ("vie 16/10, pasado mañana"): no queda nada que lo nombre.
    assert not [d for d in recibido["dias"] if d.startswith(VENCE)]
    # Lo demás del resumen, igual.
    [hecho] = recibido["hechos"]
    assert hecho["responsable"] == "Ariel De Simone"


def test_una_tarea_abierta_sigue_diciendo_cuando_vence():
    recibido = _lo_que_recibe_la_redaccion(_pedido(_resumen("en_curso")))
    [hecho] = recibido["hechos"]
    assert VENCE in json.dumps(hecho)
    assert [d for d in recibido["dias"] if d.startswith(VENCE)]


def test_en_una_lista_sale_el_vencimiento_solo_de_las_tareas_cerradas():
    otra = "2026-10-23"
    lista = {"resultado": "leido", "tareas": [
        {"titulo": DASHBOARD, "estado": "terminada", "vence": VENCE},
        {"titulo": "Cablear la bomba", "estado": "en_curso", "vence": otra}]}
    recibido = _lo_que_recibe_la_redaccion(_pedido(lista))
    texto = json.dumps(recibido["hechos"])
    assert VENCE not in texto and otra in texto
    assert not [d for d in recibido["dias"] if d.startswith(VENCE)]
    assert [d for d in recibido["dias"] if d.startswith(otra)]


def test_la_fecha_objetivo_de_una_tarea_cerrada_tampoco_llega():
    hecho = {"titulo": DASHBOARD, "estado": "terminada",
             "fecha_objetivo": f"{VENCE}T17:00:00-03:00"}
    recibido = _lo_que_recibe_la_redaccion(_pedido(hecho))
    assert VENCE not in json.dumps(recibido["hechos"])


def test_si_otro_dato_del_pedido_trae_la_misma_fecha_su_dia_queda():
    """Sólo sale el día de la fecha que ya no nombra nadie: si otro hecho trae ese mismo día,
    la IA lo sigue teniendo."""
    otro = {"resultado": "anotado", "tarea": {"titulo": "Cablear la bomba"},
            "fecha_prevista": VENCE}
    recibido = _lo_que_recibe_la_redaccion(_pedido(_resumen("terminada"), otro))
    assert [d for d in recibido["dias"] if d.startswith(VENCE)]


def test_los_hechos_de_la_cocina_no_cambian():
    pedido = _pedido(_resumen("terminada"))
    antes = copy.deepcopy(pedido)
    hechos.para_redactar(pedido)
    assert pedido == antes


# --- Por el motor ---------------------------------------------------------------------------

@pytest.fixture
def equipo(conn, direccion):  # noqa: F811 -- el fixture importado
    """Una tarea terminada de Lucas (Infraestructura IT), que Nahuel (OT) no ve."""
    mundo = cargar(conn, {"tareas": {
        "DASH": {"titulo": DASHBOARD, "responsable": "Lucas", "vence": VENCE,
                 "estado": "terminada", "desde": "2026-10-01"},
    }})
    t = Turnos(conn, {"id": mundo.workspace_id, "personas": mundo.personas})
    t.carga = mundo
    return t


def test_el_resumen_de_una_tarea_terminada_no_le_dice_a_la_ia_cuando_vencia(conn, equipo):
    r = equipo.dice("Nahuel", Jugada("pedir_enlace", {"como_la_nombra": "dashboard"}),
                    texto="pasame el link del dashboard de lotes")
    [hecho] = r.hechos
    # La cocina dice lo que es; el borde de la redacción, lo que la IA cuenta.
    assert (hecho["resultado"], hecho["estado"], hecho["vence"]) == (
        "solo_el_resumen", "terminada", VENCE)
    para_la_ia = hechos.para_redactar(equipo.redaccion)
    assert VENCE not in json.dumps(para_la_ia["hechos"])


def test_la_pregunta_al_encargado_por_una_tarea_terminada_no_dice_cuando_vencia(conn, equipo):
    equipo.dice("Nahuel", Jugada("pedir_enlace", {"como_la_nombra": "dashboard"}),
                texto="pasame el link del dashboard de lotes")
    equipo.dice("Nahuel", Jugada("pedir_el_detalle", {}), texto="si dale")
    [aviso] = avisos_guardados(conn, "pedido_del_detalle")
    assert aviso["hechos"]["estado"] == "terminada" and aviso["hechos"]["vence"] == VENCE
    assert VENCE not in json.dumps(hechos.para_redactar(aviso["hechos"]))
