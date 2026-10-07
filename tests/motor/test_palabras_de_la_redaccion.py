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

from leda.motor import avisos, hechos, preguntas
from leda.motor.fichas import (ESPERA_ALGO_CIERTO, FICHAS, LLEGA, NO_LE_LLEGO, NO_LE_VA_A_LLEGAR,
                               SALIDAS_DE_UN_BLOQUEO, YA_LE_LLEGO)
from leda.motor.ia_real import DATOS

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
