"""Las palabras de la redacción: ningún nombre que la IA recibe para redactar nombra un concepto
de la cocina (`leda.motor.hechos`).

Las palabras de todos los días (usuario, 2026-10-07; conversación 19): con los significados ya
reescritos, la IA real seguía escribiendo "si se cumple esa previsión", porque el pedido de
redacción traía claves y códigos con el nombre del concepto (`prevision`,
`atraso_si_se_cumple_la_prevision_dias_habiles`, `nueva_prevision`, `"jugada":
"anotar_prevision"`). Lo que la IA lee como nombre, lo repite como palabra.

Se recorren las tablas reales del motor, no una lista a mano: cada clave y cada código con
significado, cada jugada, cada tipo de pregunta y de aviso, cada dato de una jugada y lo que un
aviso dice de si llega.
"""

from __future__ import annotations

import json
import re

from leda.motor import avisos, hechos, preguntas
from leda.motor.fichas import (ESPERA_ALGO_CIERTO, FICHAS, LLEGA, NO_LE_LLEGO, NO_LE_VA_A_LLEGAR,
                               SALIDAS_DE_UN_BLOQUEO, YA_LE_LLEGO)
from leda.motor.ia_real import DATOS
from leda.motor.instrucciones import INSTRUCCIONES_REDACCION

from tests.motor.ayudantes import (ProveedorFalso, a_la_vista, ia_real_falsa, respuesta_de_texto,
                                   solo_si_pregunta)

NOMBRES = sorted(set(hechos.SIGNIFICADOS) | set(FICHAS) | set(preguntas.TIPOS)
                 | set(avisos.TIPOS) | set(DATOS)
                 | {LLEGA, YA_LE_LLEGO, NO_LE_VA_A_LLEGAR, NO_LE_LLEGO}
                 | set(SALIDAS_DE_UN_BLOQUEO) | set(ESPERA_ALGO_CIERTO))


def _lo_que_recibe_la_redaccion(pedido: dict) -> tuple[dict, str]:
    """Los datos y las instrucciones (con la lista de significados) que la IA real recibe."""
    proveedor = ProveedorFalso([respuesta_de_texto("Hola.")])
    ia_real_falsa(proveedor).redactar(pedido)
    sistema, usuario = proveedor.pedidos[0]["cuerpo"]["messages"]
    return json.loads(usuario["content"]), sistema["content"]


def _con_todos_los_nombres() -> dict:
    """Un pedido de redacción con cada nombre del motor como clave y como código, en los
    hechos y en los últimos turnos."""
    todos = [{nombre: nombre} for nombre in NOMBRES]
    return {"hoy": "2026-10-20", "persona": "Marcos", "mensaje": None, "hechos": todos,
            "pregunta": None,
            "ultimos_turnos": [{"sentido": "salida", "texto": "Anotado.", "hechos": todos}]}


def test_ningun_nombre_que_recibe_la_redaccion_es_un_concepto_de_la_cocina():
    recibido, _ = _lo_que_recibe_la_redaccion(_con_todos_los_nombres())

    conceptos = {n for n in hechos._nombres(recibido) if hechos.es_un_concepto_de_la_cocina(n)}
    assert not conceptos, sorted(conceptos)


def test_cada_nombre_que_recibe_la_redaccion_tiene_su_significado():
    recibido, sistema = _lo_que_recibe_la_redaccion(_con_todos_los_nombres())

    assert hechos.sin_significado(recibido) == set()
    lista = sistema.split(hechos.ENCABEZADO_DEL_BLOQUE, 1)[1].split("\n\n", 1)[0]
    explicados = [linea[2:].split(":", 1)[0] for linea in lista.strip().splitlines()]
    assert set(explicados) == set(hechos._nombres(recibido))
    for nombre in explicados:
        assert f"- {nombre}: {hechos.significado(nombre)}" in lista.splitlines(), nombre
    assert not [n for n in explicados if hechos.es_un_concepto_de_la_cocina(n)]


def test_cada_nombre_para_redactar_dice_lo_mismo_y_no_choca_con_otro():
    """Un nombre de la cocina y el suyo para redactar significan lo mismo; ninguno para
    redactar es un nombre de la cocina, ni de otra cosa, ni nombra un concepto."""
    cocina = set(NOMBRES)
    para = hechos.PARA_LA_REDACCION
    assert len(set(para.values())) == len(para)
    assert not set(para.values()) & cocina
    assert set(para) <= cocina
    for de, a in para.items():
        assert hechos.significado(a) == hechos.significado(de), de
        assert hechos._CODIGO.match(a), a           # como valor, también se lee como código
        assert not hechos.es_un_concepto_de_la_cocina(a), a
    assert {n for n in NOMBRES if hechos.es_un_concepto_de_la_cocina(n)} == set(para)


def test_lo_que_alguien_escribio_llega_tal_cual():
    """El mensaje de la persona y los textos de los últimos turnos son lo que alguien escribió:
    nunca se traducen, aunque nombren un concepto o sean una sola palabra de la cocina."""
    pedido = {"hoy": "2026-10-20", "persona": "Marcos", "mensaje": "escalamiento",
              "hechos": [{"jugada": "anotar_prevision", "prevision": "2026-10-27",
                          "motivo": "el proveedor se demoró"}],
              "pregunta": None,
              "ultimos_turnos": [{"sentido": "entrada", "texto": "que es prevision?"},
                                 {"sentido": "salida", "texto": "reencuadre"}]}

    recibido, _ = _lo_que_recibe_la_redaccion(pedido)

    assert recibido["mensaje"] == "escalamiento"
    assert [t["texto"] for t in recibido["ultimos_turnos"]] == ["que es prevision?",
                                                               "reencuadre"]
    assert recibido["hechos"] == [{"jugada": "anotar_para_cuando_la_termina",
                                   "dia_que_dio_para_terminarla": "2026-10-27",
                                   "motivo": "el proveedor se demoró"}]
    assert pedido["hechos"][0]["jugada"] == "anotar_prevision"      # el original, sin tocar


def test_la_instruccion_de_redaccion_no_nombra_un_concepto_de_la_cocina():
    """Si la instrucción nombrara una clave por su nombre de la cocina, la IA no la
    encontraría en los datos."""
    palabras = set(re.findall(r"[a-z_]+", INSTRUCCIONES_REDACCION))
    # Los verbos sueltos de algunas jugadas también son palabras de la instrucción.
    verbos = {"elegir", "corregir", "cancelar", "destrabar", "entregar"}
    assert not palabras & (set(hechos.PARA_LA_REDACCION) - verbos)


# --- Quien aprueba el trabajo de la persona, sólo si lo pregunta (usuario, 2026-10-08) --------

def test_quien_aprueba_el_trabajo_de_la_persona_llega_a_la_redaccion_solo_si_pregunta():
    """Decisión 11: Leda no nombra por su cuenta a quien aprueba el trabajo de la persona a la
    que le escribe, ni como motivo ni al contar un hecho. Cada dato de la cocina que lo nombra
    le llega a la redacción con el nombre dentro de `solo_si_pregunta`, en el mismo lugar; lo
    demás del dato, a la vista."""
    aviso = {"a": "Ismael", "llega": "2026-10-20T15:50:00-03:00"}
    pedido = {"hoy": "2026-10-20", "persona": "Marcos", "mensaje": None, "pregunta": None,
              "hechos": [{"jugada": "anotar_prevision", "aviso_al_referente": aviso,
                          "correccion_al_referente": aviso,
                          "aviso_de_la_prevision_corregida": aviso,
                          "aviso_de_la_prevision_anterior": aviso},
                         {"jugada": "confirmar", "resultado": "entregada",
                          "queda_esperando_la_aprobacion_de": "Ismael",
                          "aviso_a_quien_aprueba": aviso},
                         {"jugada": "aprobar", "aviso_de_que_se_destrabo": aviso},
                         {"no_vuelve_a_pedir_el_estado": {
                             "motivo": "ya_se_escalo",
                             "escalado_a": [{"a": "Ismael", "llega": "ya_le_llego"}]}},
                         {"aviso": "pedido_de_estado",
                          "si_no_hay_respuesta": {"se_avisa_a": ["Ismael"]}},
                         {"aviso": "recordatorio_de_la_decision",
                          "si_sigue_sin_decidir": {"se_avisa_a": ["Ismael"],
                                                   "fecha": "2026-10-21"}},
                         {"aviso": "tarea_aprobada", "aprobada_por": "Ismael"},
                         {"aviso": "pedido_de_cambios", "pidio_cambios": "Ismael",
                          "comentario": "falta el diagrama"}],
              "ultimos_turnos": [{"sentido": "entrada", "texto": "llego el 27",
                                  "hechos": [{"aviso_al_referente": aviso}]}]}

    recibido, _ = _lo_que_recibe_la_redaccion(pedido)

    assert "Ismael" not in a_la_vista(recibido), a_la_vista(recibido)
    assert solo_si_pregunta(recibido).count("Ismael") == 13
    assert recibido["hechos"][0]["aviso_a_quien_aprueba_su_trabajo"] == {
        "llega": "2026-10-20T15:50:00-03:00", "solo_si_pregunta": {"a": "Ismael"}}
    assert recibido["hechos"][4]["si_no_hay_respuesta"] == {
        "solo_si_pregunta": {"se_avisa_a": ["Ismael"]}}
    assert recibido["hechos"][5]["si_sigue_sin_decidir"] == {
        "fecha": "2026-10-21", "solo_si_pregunta": {"se_avisa_a": ["Ismael"]}}
    assert recibido["hechos"][7]["solo_si_pregunta"] == {"pidio_cambios": "Ismael"}
    assert recibido["hechos"][7]["comentario"] == "falta el diagrama"
    assert pedido["hechos"][1]["queda_esperando_la_aprobacion_de"] == "Ismael"   # sin tocar


def test_a_quien_aprueba_se_le_nombra_a_la_persona_responsable_y_a_terceros():
    """La regla es sobre quien aprueba el trabajo de la persona a la que Leda le escribe: a quien
    aprueba se le nombra a la persona responsable ("Marcos te entregó…", y que Marcos se va a
    enterar de la decisión); a quien está arriba, quién tiene trabada la decisión; y a quien
    pide algo que decide otro, quién lo decide."""
    pedido = {"hoy": "2026-10-20", "persona": "Ismael", "mensaje": None, "pregunta": None,
              "hechos": [{"jugada": "aprobar",
                          "aviso_al_responsable": {"a": "Marcos", "llega": "ya_le_llego"}},
                         {"aviso": "aprobacion_trabada", "quien_aprueba": "Marcos",
                          "responsable": "Ariel"},
                         {"jugada": "aprobar", "resultado": "no_se_puede",
                          "motivo": "no_es_quien_aprueba", "quien_aprueba": "Marcos"},
                         {"jugada": "pedir_reasignacion", "resultado": "no_por_chat",
                          "quien_decide": "Marcos"}],
              "ultimos_turnos": []}

    recibido, _ = _lo_que_recibe_la_redaccion(pedido)

    assert solo_si_pregunta(recibido) == "[]"
    assert a_la_vista(recibido).count("Marcos") == 4


def test_lo_que_espera_una_decision_se_dice_revision():
    """Decisión 18: lo que espera es una revisión ("Te entregaron 2 tareas para revisar", "pasa a
    revisión"); "aprobar" queda para la decisión misma. Los nombres de la cocina que dicen la
    espera como aprobación son conceptos de la cocina y la redacción recibe el suyo."""
    for de, para in (("queda_esperando_la_aprobacion_de", "queda_esperando_la_revision_de"),
                     ("entrega_para_aprobar", "entrega_para_revisar"),
                     ("aprobacion_trabada", "revision_trabada"),
                     ("aprobacion_destrabada", "revision_destrabada")):
        assert hechos.es_un_concepto_de_la_cocina(de), de
        assert hechos.para_redactar(de) == para
    for decision in ("aprobar", "tarea_aprobada", "cerrada_con_la_aprobacion", "ya_la_aprobo"):
        assert "revis" not in hechos.para_redactar(decision), decision
    for nombre in ("queda_esperando_la_aprobacion_de", "entregada", "ya_no_esta_entregada",
                   "entrega_para_aprobar", "recordatorio_de_la_decision", "aprobacion_trabada",
                   "aprobacion_destrabada", "para_decidir"):
        assert "revis" in hechos.significado(nombre), nombre
        assert "esperando la aprobación" not in hechos.significado(nombre), nombre
        assert "espera su aprobación" not in hechos.significado(nombre), nombre


def test_lo_que_la_persona_entrega_lo_describe():
    """Decisión 10: "describir", no "contar", en lo que la IA lee sobre la entrega."""
    for texto in (hechos.significado("el_texto_cubre"), DATOS["el_texto_cubre"][1]):
        assert "describe" in texto and "cont" not in texto, texto
