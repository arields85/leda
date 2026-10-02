"""Un ícono por acción en el menú de una tarea (R4-H6, decisión del usuario,
2026-09-30).

Antes todas las acciones del menú llevaban el ícono de categoría 📋 ("una acción
sobre una tarea"), así que no se distinguían a simple vista. La tabla aprobada:
📋 Ver detalle / Ver detalle y evidencia, ▶️ Empezar, 🏁 Ya la terminé, ⛔ Informar un
bloqueo, 🔗 Depende de otra tarea, ✅ Aprobar, ✏️ Pedir cambios. Se define en un solo
lugar (`salida.ICONOS_DE_ACCION_MENU`) y nada compara el texto de la etiqueta: cada
opción se identifica por su código (`{"accion": ...}`) o su token.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from leda import gateway
from leda.db import admin, espacio
from leda.salida import (ICONO_TAREA, ICONOS_DE_ACCION_MENU, con_icono,
                           etiqueta_de_accion_menu, etiqueta_sin_icono,
                           etiquetas_coinciden)

from tests.banco.corrida import sembrar_precondiciones
from tests.test_menu_tarea import _quien

TABLA_APROBADA = {
    "ver_detalle": "📋", "ver_detalle_evidencia": "📋", "empezar": "▶️",
    "terminar": "🏁", "informar_bloqueo": "⛔", "depende_de_otra": "🔗",
    "aprobar": "✅", "pedir_cambios": "✏️",
}


def test_la_tabla_de_iconos_es_la_aprobada():
    for codigo, icono in TABLA_APROBADA.items():
        assert ICONOS_DE_ACCION_MENU[codigo] == icono


def test_una_accion_sin_icono_propio_conserva_el_de_categoria():
    assert etiqueta_de_accion_menu("adjuntar_evidencia", "Adjuntar evidencia") == (
        con_icono("Adjuntar evidencia", ICONO_TAREA))


@pytest.mark.parametrize("codigo, icono", sorted(TABLA_APROBADA.items()))
def test_etiqueta_sin_icono_saca_cada_icono_de_la_tabla(codigo, icono):
    etiqueta = etiqueta_de_accion_menu(codigo, "Lo que sea")

    assert etiqueta == f"{icono} Lo que sea"
    assert etiqueta_sin_icono(etiqueta) == "Lo que sea"
    assert etiquetas_coinciden(etiqueta, "Lo que sea")


def _etiquetas_del_menu(conn, ws, persona, tarea_id) -> dict[str, str]:
    """codigo de accion -> etiqueta real del botón del menú de la tarea."""
    tg = None
    with espacio(conn, ws) as cur:
        quien = _quien(cur, persona, ws)
        cur.execute("select telegram_user_id t from integrante where nombre = %s",
                    (persona,))
        tg = cur.fetchone()["t"]
        gateway._abrir_menu_tarea(cur, quien, ws, tg, tarea_id,
                                  datetime.now(timezone.utc))
    with admin(conn) as cur:
        cur.execute(
            """select o.etiqueta, o.valor from pending_action_option o
                 join pending_action p on p.id = o.pending_action_id
                where p.workspace_id = %s and p.chat_id = %s
                order by p.creado_en desc, o.orden""", (ws, tg))
        filas = cur.fetchall()
    return {f["valor"].get("accion"): f["etiqueta"] for f in filas[:12]}


def test_el_menu_del_responsable_lleva_un_icono_por_accion(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {"tareas": [{
            "id": "t1", "titulo": "Programar HMI", "area": "ot",
            "responsable": "Nahuel Gimenez"}]})
    conn.commit()

    etiquetas = _etiquetas_del_menu(conn, ws, "Nahuel Gimenez", ids["t1"])

    for codigo in ("ver_detalle", "empezar", "terminar", "informar_bloqueo",
                   "depende_de_otra"):
        assert etiquetas[codigo].startswith(f"{TABLA_APROBADA[codigo]} "), codigo
    # Ya no todas son 📋: la lista de iconos del menú tiene más de uno.
    assert len({e.split(" ", 1)[0] for e in etiquetas.values()}) > 1


def test_el_menu_del_aprobador_lleva_un_icono_por_accion(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = sembrar_precondiciones(cur, ws, {"tareas": [{
            "id": "t1", "titulo": "Programar PLC", "area": "ot",
            "responsable": "Nahuel Gimenez", "estado": "en_revision",
            "evidencia_requerida": []}]})
    conn.commit()

    etiquetas = _etiquetas_del_menu(conn, ws, "Marcos Tarquini", ids["t1"])

    for codigo in ("ver_detalle_evidencia", "aprobar", "pedir_cambios"):
        assert etiquetas[codigo].startswith(f"{TABLA_APROBADA[codigo]} "), codigo


def test_el_menu_del_borrador_en_curso_lleva_icono_en_sus_tres_botones(
        intake_world, conn):
    """(i) "Continuar borrador" y "Empezar otro" salían sin ícono mientras
    "Cancelar borrador" sí lo llevaba. Mismas constantes de `salida`, sin literales:
    ▶️ seguir (el de empezar/retomar) y ➕ uno nuevo (el de agregar)."""
    from leda.salida import ICONO_CANCELAR, ICONO_EMPEZAR, ICONO_VER_MAS

    from tests.test_task_intake import _active_choices, _start

    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        _, primero = _start(cur, intake_world)
        _start(cur, intake_world, raw="Otra tarea", title="Calibrar el sensor")
        etiquetas = _active_choices(cur, primero.request_id)

    assert sorted(etiquetas) == sorted([
        f"{ICONO_EMPEZAR} Continuar borrador",
        f"{ICONO_CANCELAR} Cancelar borrador",
        f"{ICONO_VER_MAS} Empezar otro"])
