"""El encabezado del menú de una tarea, un dato por línea (R4-H5, decisión del usuario
en la cuarta ronda por Telegram, 2026-09-30).

Antes: "«Programar PLC» · Ariel De Simone · En revisión", con puntos medios y el
estado en mayúscula en medio de la oración. Ahora sale con el mismo mecanismo que
las vistas previas (`herramientas._filas`): la tarea, quién la tiene y el estado,
cada uno en su renglón, sin " · ".
"""

from __future__ import annotations

from prisma import menu_tarea as M
from prisma.db import admin, espacio

from tests.banco.corrida import sembrar_precondiciones
from tests.test_menu_tarea import _quien


def _menu(conn, ws, persona, **tarea):
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {"tareas": [{
            "id": "t1", "titulo": "Programar PLC", "area": "ot",
            "responsable": "Nahuel Gimenez", **tarea}]})
    conn.commit()
    with espacio(conn, ws) as cur:
        return M.calcular_menu(cur, _quien(cur, persona, ws), ids["t1"])


def test_el_encabezado_lleva_un_dato_por_linea_sin_puntos_medios(corework, conn):
    ws = corework.workspace_id
    menu = _menu(conn, ws, "Marcos Tarquini", estado="en_revision",
                 evidencia_requerida=[])

    encabezado = M.encabezado_menu(menu)

    assert "·" not in encabezado
    assert encabezado.splitlines() == [
        "«Programar PLC»", "Responsable: Nahuel Gimenez", "Estado: En revisión"]


def test_para_quien_la_tiene_dice_vos(corework, conn):
    ws = corework.workspace_id
    menu = _menu(conn, ws, "Nahuel Gimenez", estado="en_curso")

    assert M.encabezado_menu(menu).splitlines() == [
        "«Programar PLC»", "Responsable: vos", "Estado: En curso"]


def test_los_cambios_pedidos_siguen_en_su_propia_linea(corework, conn):
    ws = corework.workspace_id
    menu = _menu(conn, ws, "Nahuel Gimenez", estado="asignada",
                 cambios_pedidos={"por": "Marcos Tarquini", "motivo": "falta la hora"})

    lineas = M.encabezado_menu(menu).splitlines()

    assert lineas[-1] == "Cambios pedidos por Marcos Tarquini: falta la hora"
    assert len(lineas) == 4
