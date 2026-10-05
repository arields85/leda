"""Las reglas de comparación del corredor, sin base (revisión de la E2-7).

`prueba_chica/comprobar.py`: lo esperado de un paso contra lo que pasó, y cómo se clasifica cada
diferencia (garantía, comprensión o motor).
"""

from __future__ import annotations

from prueba_chica import comprobar as cp


def _hubo(**mas) -> dict:
    vacio = {"estados": {}, "previsiones": [], "bloqueos": [], "bloqueos_resueltos": [],
             "destraban": [], "avisos_guardados": [], "salidas": [], "incidentes": [],
             "avisos_al_administrador": 0, "avances": []}
    return {**vacio, **mas}


def test_un_bloqueo_resuelto_que_falta_es_de_comprension_y_uno_de_mas_de_garantia():
    falta = cp.Comprobacion()
    de_mas, falto = cp.comprobar_efectos(falta, {"bloqueos_resueltos": ["PLC"]}, _hubo(), {})
    assert (de_mas, falto) == (False, True)
    assert [(f.clase, f.que) for f in falta.fallas] == [
        (cp.COMPRENSION, "falta un efecto: bloqueo resuelto")]

    sobra = cp.Comprobacion()
    de_mas, falto = cp.comprobar_efectos(sobra, {}, _hubo(bloqueos_resueltos=["PLC"]), {})
    assert (de_mas, falto) == (True, False)
    assert [(f.clase, f.que) for f in sobra.fallas] == [
        (cp.GARANTIA, "efecto de más: bloqueo resuelto")]


def test_el_emparejamiento_no_se_deja_ganar_por_el_primero_que_coincide():
    """Un esperado general no se queda con el real que otro esperado más preciso necesita."""
    esperados = [{"tarea": "PLC"}, {"tarea": "PLC", "fecha": "2026-10-27"}]
    reales = [{"tarea": "PLC", "fecha": "2026-10-27"}, {"tarea": "PLC", "fecha": "2026-10-30"}]

    assert cp._emparejar(esperados, reales) == ([], [])


def test_un_envio_que_junto_avisos_de_dos_tareas_cumple_lo_esperado_de_las_dos():
    """Un mensaje de Leda por su cuenta puede juntar avisos de varias tareas (mecánica §10):
    el corredor lo compara con todas, no con una sola (revisión de la E2-7)."""
    from prueba_chica.corredor import Salida, _sale_coincide

    junto = Salida("Marcos", "texto", [], False, tipo="aviso_previo", tareas=["PLC", "COM"],
                   hechos=[{"tarea": "PLC", "vence": "2026-10-23"},
                           {"tarea": "COM", "vence": "2026-10-23"}], tipos=["aviso_previo"])

    assert _sale_coincide({"a": "Marcos", "tipo": "aviso_previo", "tareas": ["PLC", "COM"]},
                          junto)
    assert _sale_coincide({"tipo": "aviso_previo", "tareas": ["COM", "PLC"],
                           "hechos": {"tarea": "COM"}}, junto)
    # Con una sola tarea de la conversación en el foco, el envío cumple lo de esa tarea.
    assert _sale_coincide({"tarea": "PLC", "hechos": {"vence": "2026-10-23"}}, junto, {"PLC"})
    assert not _sale_coincide({"tarea": "PLC"}, junto)
