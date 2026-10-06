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

import pytest

from leda.salida import (ICONO_TAREA, ICONOS_DE_ACCION_MENU, con_icono,
                         etiqueta_de_accion_menu, etiqueta_sin_icono, etiquetas_coinciden)


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
