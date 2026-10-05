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


def test_los_hechos_esperados_se_comparan_con_el_aviso_de_ese_tipo_y_esa_tarea():
    """En un envío que junta avisos, los hechos esperados de un tipo y una tarea son los de ese
    aviso, no los de cualquiera del envío (revisión de la corrida en seco con las 16)."""
    from prueba_chica.corredor import Salida, _sale_coincide

    previo_com = {"aviso": "vencimiento_proximo", "necesita_respuesta": False,
                  "vence": "2026-11-06"}
    pedido_plc = {"aviso": "pedido_de_estado", "necesita_respuesta": True, "numero": 1}
    junto = Salida("Marcos", "texto", [], False, tareas=["PLC", "COM"],
                   hechos=[pedido_plc, previo_com], tipos=["aviso_previo", "pedido_de_estado"],
                   avisos=[{"tipo": "pedido_de_estado", "tarea": "PLC", "hechos": pedido_plc},
                           {"tipo": "aviso_previo", "tarea": "COM", "hechos": previo_com}])

    assert _sale_coincide({"tipo": "pedido_de_estado", "tareas": ["PLC", "COM"],
                           "hechos": {"numero": 1}}, junto)
    # Los hechos del aviso previo de COM no cumplen lo esperado del pedido de estado.
    assert not _sale_coincide({"tipo": "pedido_de_estado", "tareas": ["PLC", "COM"],
                               "hechos": {"necesita_respuesta": False}}, junto)
    # Con una sola tarea en el foco, sólo cuentan los avisos de esa tarea.
    assert not _sale_coincide({"tarea": "PLC", "hechos": {"vence": "2026-11-06"}}, junto,
                              {"PLC"})
    assert _sale_coincide({"tarea": "PLC", "hechos": {"numero": 1}}, junto, {"PLC"})


def test_cada_aviso_de_un_envio_va_con_sus_propios_hechos():
    """Los avisos de un envío se emparejan con sus hechos por el aviso mismo, no por posición:
    uno sin hechos no corre a los demás (revisión de la corrida en seco con las 16)."""
    from prueba_chica.corredor import _avisos_del_envio

    titulos = {"PLC": "Programar PLC", "COM": "Revisar comunicaciones"}
    avisos = [{"id": "b", "tipo": "pedido_de_estado", "tarea": "PLC",
               "hechos": {"tarea": "Programar PLC", "numero": 1}},
              {"id": "a", "tipo": "aviso_previo", "tarea": "COM", "hechos": None}]

    de_cada_uno, hechos = _avisos_del_envio(avisos, titulos)

    assert de_cada_uno == [
        {"id": "a", "tipo": "aviso_previo", "tarea": "COM", "hechos": None},
        {"id": "b", "tipo": "pedido_de_estado", "tarea": "PLC",
         "hechos": {"tarea": "PLC", "numero": 1}}]
    assert hechos == [{"tarea": "PLC", "numero": 1}]        # sólo los que tienen hechos
