"""Los textos que la persona dicta salen sin errores de tipeo obvios (F-B9,
decisión del usuario del 2026-10-01).

El modelo normaliza el valor en la etapa 2 (ADR 0014, M1): para un texto libre
(el título, la descripción, el criterio de aceptación) corrige sólo los errores de
tipeo obvios, sin cambiar el sentido ni los nombres, y la corrección queda a la
vista en el resumen (que muestra el valor guardado), cambiable con Modificar. Es
una regla general de la instrucción, no una lista de palabras. Las referencias a
algo que ya existe (una persona, un objetivo, una tarea) siguen "tal como se
escribe": corregirlas sería elegir por la persona.

Este módulo prueba la instrucción; que el código guarda el valor que el modelo
devuelve ya lo prueban `test_alta_guiada_flujo` y `test_router_valor`.
"""

from __future__ import annotations

import prisma.llm as llm
from prisma.valores import TipoValor, ValorEsperado

PENDIENTE = "el título de la tarea nueva"


def _sistema(esperado: ValorEsperado) -> str:
    return llm._sistema_del_ruteo(PENDIENTE, esperado)


def test_el_texto_libre_se_normaliza_sin_errores_de_tipeo_obvios():
    sistema = _sistema(ValorEsperado(TipoValor.TEXTO))
    assert "errores de tipeo obvios" in sistema
    # Sólo eso: ni reescribir, ni resumir, ni agregar, ni tocar nombres.
    assert "sin cambiar el sentido" in sistema
    assert "nombres propios" in sistema
    assert "tal como lo dijo, sin agregar, resumir ni corregir nada" not in sistema


def test_el_criterio_de_aceptacion_tambien_se_normaliza():
    sistema = _sistema(ValorEsperado(TipoValor.TEXTO, juzga_verificable=True,
                                     contexto="Calibrar sensores"))
    assert "errores de tipeo obvios" in sistema


def test_las_referencias_a_lo_que_ya_existe_siguen_tal_como_se_escriben():
    sistema = _sistema(ValorEsperado(TipoValor.ENTIDAD))
    assert "tal como el mensaje la escribe" in sistema
    assert "tipeo" not in sistema


def test_la_fecha_y_la_opcion_no_dicen_nada_de_corregir_texto():
    from datetime import date

    assert "tipeo" not in _sistema(ValorEsperado(TipoValor.FECHA, hoy=date(2026, 10, 1)))
