"""Vista previa en filas y recibo corto (T10-4, R3-H11, H14 y H9).

La vista previa de una herramienta que escribe pone un dato por línea, armada
en un solo lugar (`herramientas._filas`); el recibo al confirmar cuenta lo que
pasó en una oración, no repite la vista previa; y el estado se nombra de una
forma que se lee bien con cualquiera ("y vuelve a estar en curso", nunca "vuelve
a en curso").
"""

from __future__ import annotations

from pathlib import Path

import pytest

from leda import herramientas as H

ROOT = Path(__file__).resolve().parents[1]


def test_filas_pone_un_dato_por_linea():
    assert H._filas(("Tarea", "Programar PLC"), ("Estado actual", "Asignada")) == (
        "Tarea: Programar PLC\nEstado actual: Asignada")


def test_filas_admite_una_frase_suelta_y_saltea_lo_que_no_hay():
    assert H._filas(("Tarea", "X"), ("Impacto", None), (None, "La tarea sigue bloqueada.")) == (
        "Tarea: X\nLa tarea sigue bloqueada.")


def test_ninguna_preparacion_junta_datos_con_puntos_medios():
    """Un dato por línea sale de `_filas`, no de cada llamada: ningún texto de
    `herramientas.py` vuelve a juntar campos con " · "."""
    lineas = [
        f"{n}: {linea.strip()}"
        for n, linea in enumerate(
            (ROOT / "src" / "leda" / "herramientas.py").read_text(encoding="utf-8").splitlines(), 1)
        if "·" in linea and not linea.lstrip().startswith("#")]
    assert lineas == []


@pytest.mark.parametrize("estado", sorted(H.ESTADOS_LEGIBLES))
def test_el_estado_se_nombra_bien_con_cualquiera(estado):
    frase = f"La tarea vuelve a {H._estar(estado)}."
    assert frase == f"La tarea vuelve a estar {H.ESTADOS_LEGIBLES[estado].lower()}."
    assert "vuelve a en " not in frase


def test_el_recibo_de_una_entrega_agradece_y_no_nombra_estado_en_mayuscula():
    recibo = H.recibo_de_estado("Programar HMI línea 2", "en_revision")
    assert recibo == "Gracias. La tarea «Programar HMI línea 2» pasó a revisión."


@pytest.mark.parametrize("estado", ["asignada", "en_curso", "bloqueada", "terminada"])
def test_el_recibo_de_otro_estado_no_lleva_el_estado_en_mayuscula(estado):
    recibo = H.recibo_de_estado("Programar PLC", estado)
    assert recibo == (
        f"La tarea «Programar PLC» pasó a estar {H.ESTADOS_LEGIBLES[estado].lower()}.")
