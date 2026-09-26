"""Detección de pregunta compartida (T4b, `prisma-orienta`).

`prisma.deteccion_pregunta` es la única implementación de "esto le pregunta
algo a la persona": antes de esta unidad vivía sólo en
`tests/banco/comprobadores.py` (T7); ahora el servidor
(`agente.responder`) la necesita también para el cierre genérico de una
pregunta sin opciones. Estas pruebas repiten, contra el módulo movido, los
casos que ya validaban la heurística en el banco -- si algo se rompió al
mover el código, tiene que fallar acá primero.
"""

from __future__ import annotations

from prisma.deteccion_pregunta import hace_pregunta, pide_elegir_en_imperativo


def test_signo_de_pregunta_alcanza():
    assert hace_pregunta("¿Cómo va?")
    assert not hace_pregunta("Va bien, sin novedades.")


def test_pedido_de_eleccion_en_imperativo_sin_signo():
    assert pide_elegir_en_imperativo("Decime cuál de las dos y lo hago.")
    assert pide_elegir_en_imperativo("Contame qué la está frenando.")
    assert pide_elegir_en_imperativo("Elegí una y seguimos.")
    assert hace_pregunta("Decime cuál de las dos y lo hago.")


def test_verbo_de_pedido_sin_cual_ni_que_no_cuenta():
    # "decime"/"contame"/"confirmame" solos, sin "cuál"/"qué" al lado, no son
    # un pedido de elección -- si no, cualquier cierre cordial contaría.
    assert not pide_elegir_en_imperativo("Decime si necesitás algo más.")
    assert not hace_pregunta("Decime si necesitás algo más.")


def test_que_se_busca_con_borde_de_palabra():
    # "porque"/"aunque" no tienen que disparar un falso positivo por
    # contener "que" como subcadena.
    assert not pide_elegir_en_imperativo("Decime porque me interesa saber.")


def test_negacion_no_es_relevante_para_esta_deteccion():
    # A diferencia de `comprobar_accion_sin_herramienta`, esta detección no
    # mira negaciones: sólo importa si el texto pregunta o pide elegir.
    assert not hace_pregunta("Todo tranquilo, nada que decidir.")
