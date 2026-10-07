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

from tests.motor.ayudantes import ProveedorFalso, ia_real_falsa, respuesta_de_texto

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
