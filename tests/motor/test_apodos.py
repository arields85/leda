"""Los apodos (`leda.motor.apodos`; ADR 0020; conversación 47).

Leda reconoce a una persona del equipo cuando la nombran por un apodo: en un solo lugar
(`fichas.integrantes_que_coinciden`), con las mismas palabras que los nombres. Una persona puede
tener varios apodos y uno puede ser de dos personas; el apodo sirve para entender, nunca para
hablar, y cada uno aprendido queda auditado.

El mundo es el de las conversaciones (`tests.conversaciones.carga`): Mariano Naim es el encargado
de Electricidad, Martín Forte el de IT, Marcos Tarquini el de OT; Nahuel y Lucas, integrantes.
"""

from __future__ import annotations

import pytest

from leda.db import admin, espacio
from leda.motor import apodos
from leda.motor.fichas import integrantes_que_coinciden

from tests.conversaciones.carga import cargar
from tests.motor.ayudantes import AHORA, todos, uno

MARIANO, MARTIN, MARCOS = "Mariano Naim", "Martín Forte", "Marcos Tarquini"


@pytest.fixture
def equipo(conn):
    """CoreWork en chico: las personas de las conversaciones, sin tareas."""
    return cargar(conn, {"inicio": "2026-10-20 09:00", "tareas": {}})


def _coinciden(conn, equipo, dicho: str) -> list[str]:
    with espacio(conn, equipo.workspace_id) as cur:
        nombres = [c["nombre"] for c in integrantes_que_coinciden(cur, dicho)]
    conn.commit()
    return nombres


def _solicitante(conn, equipo, corto: str):
    from leda.autoridad import identificar_en_espacio
    with espacio(conn, equipo.workspace_id) as cur:
        quien = identificar_en_espacio(cur, equipo.personas[corto]["telegram"],
                                       equipo.workspace_id)
    conn.commit()
    return quien


def _aprender(conn, equipo, quien: str, de: str, dicho: str) -> bool:
    solicitante = _solicitante(conn, equipo, quien)
    with espacio(conn, equipo.workspace_id) as cur:
        hecho = apodos.aprender(cur, solicitante, equipo.personas[de]["membership_id"], dicho,
                                AHORA)
    conn.commit()
    return hecho


# --- Reconocer a una persona -------------------------------------------------------------------

def test_sin_apodos_se_reconoce_por_el_nombre_como_siempre(conn, equipo):
    assert _coinciden(conn, equipo, "mariano") == [MARIANO]
    assert _coinciden(conn, equipo, "el tano") == []


def test_un_apodo_aprendido_reconoce_a_su_persona_con_las_palabras_de_los_nombres(conn, equipo):
    """"el tano", "Tano" y "EL TANO" son el mismo apodo: sin mayúsculas ni acentos, cada palabra
    entera. Una palabra que no es del apodo no lo es ("tanito")."""
    assert _aprender(conn, equipo, "Nahuel", "Mariano", "El Tano")

    for dicho in ("el tano", "Tano", "EL TANO", "el Tanó"):
        assert _coinciden(conn, equipo, dicho) == [MARIANO], dicho
    for dicho in ("tanito", "el tano de compras", "ta"):
        assert _coinciden(conn, equipo, dicho) == [], dicho


def test_una_persona_puede_tener_varios_apodos(conn, equipo):
    _aprender(conn, equipo, "Nahuel", "Mariano", "el tano")
    _aprender(conn, equipo, "Lucas", "Mariano", "el chino")

    assert _coinciden(conn, equipo, "el tano") == [MARIANO]
    assert _coinciden(conn, equipo, "el chino") == [MARIANO]


def test_un_apodo_de_dos_personas_son_las_dos(conn, equipo):
    _aprender(conn, equipo, "Nahuel", "Martin", "el flaco")
    _aprender(conn, equipo, "Lucas", "Marcos", "el flaco")

    assert _coinciden(conn, equipo, "el flaco") == [MARCOS, MARTIN]


def test_un_apodo_que_coincide_con_el_nombre_de_otra_persona_son_las_dos(conn, equipo):
    """ADR 0020, decisión 3: Leda nunca elige entre el nombre de una y el apodo de otra."""
    _aprender(conn, equipo, "Nahuel", "Mariano", "marcos")

    assert _coinciden(conn, equipo, "marcos") == [MARCOS, MARIANO]


def test_un_apodo_dejado_de_usar_o_de_alguien_inactivo_no_reconoce_a_nadie(conn, equipo):
    _aprender(conn, equipo, "Nahuel", "Mariano", "el tano")
    _aprender(conn, equipo, "Nahuel", "Martin", "el flaco")
    with admin(conn) as cur:
        cur.execute("""update apodo set borrado_en = %s, borrado_por_app_user_id = %s
                        where apodo = 'el tano'""",
                    (AHORA, equipo.personas["Ismael"]["app_user_id"]))
        cur.execute("update membership set activo = false where id = %s",
                    (equipo.personas["Martin"]["membership_id"],))
    conn.commit()

    assert _coinciden(conn, equipo, "el tano") == []
    assert _coinciden(conn, equipo, "el flaco") == []


# --- Aprenderlo --------------------------------------------------------------------------------

def test_aprender_un_apodo_lo_guarda_normalizado_y_lo_audita(conn, equipo):
    assert _aprender(conn, equipo, "Nahuel", "Mariano", "El Tano")

    fila = uno(conn, "select * from apodo")
    assert fila["apodo"] == "el tano" and fila["canal"] == "chat"
    assert str(fila["membership_id"]) == equipo.personas["Mariano"]["membership_id"]
    assert str(fila["ensenado_por_app_user_id"]) == equipo.personas["Nahuel"]["app_user_id"]
    assert fila["at"] == AHORA and fila["borrado_en"] is None
    [auditoria] = todos(conn, "select * from audit_log where accion = 'aprender_apodo'")
    assert str(auditoria["actor_app_user_id"]) == equipo.personas["Nahuel"]["app_user_id"]
    assert auditoria["actor_kind"] == "persona" and auditoria["sujeto_tipo"] == "apodo"
    assert str(auditoria["sujeto_id"]) == str(fila["id"])
    assert auditoria["pack_hash"] and auditoria["nucleo_hash"]
    detalle = auditoria["detalle"]
    assert detalle["apodo"] == "el tano" and detalle["canal"] == "chat"
    assert detalle["membership_id"] == equipo.personas["Mariano"]["membership_id"]
    assert detalle["ensenado_por_membership_id"] == equipo.personas["Nahuel"]["membership_id"]


def test_aprender_el_mismo_apodo_otra_vez_no_cambia_nada(conn, equipo):
    assert _aprender(conn, equipo, "Nahuel", "Mariano", "el tano")
    assert not _aprender(conn, equipo, "Lucas", "Mariano", "El TANO")

    assert uno(conn, "select count(*) n from apodo")["n"] == 1
    assert uno(conn, "select count(*) n from audit_log where accion = 'aprender_apodo'")["n"] == 1


def test_el_apodo_cargado_por_la_plataforma_tambien_reconoce(conn):
    """El estado inicial de una conversación puede traer apodos cargados por la plataforma
    (ADR 0020, decisión 4; la 47, paso 9)."""
    mundo = cargar(conn, {"inicio": "2026-10-20 09:00", "tareas": {},
                          "apodos": [{"apodo": "el flaco", "de": "Martin"},
                                     {"apodo": "el flaco", "de": "Marcos"}]})

    assert _coinciden(conn, mundo, "el flaco") == [MARCOS, MARTIN]
    assert {f["canal"] for f in todos(conn, "select canal from apodo")} == {"plataforma"}
