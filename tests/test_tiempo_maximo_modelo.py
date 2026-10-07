"""T8c-4: cada intento al modelo tiene un tiempo máximo y un reintento acotado.

Evidencia: NaN colgó ~93-95 s el 1,3 % de las llamadas y el cliente esperaba
hasta 600 s. Los proveedores de `llm.py` se retiraron con los flujos A y B (E3-3);
queda la validación de los dos parámetros (`llm._tiempos`), que usa la prueba chica
(`prueba_chica/ia_real.py`).
"""

from __future__ import annotations

import pytest

import leda.llm as llm


def test_valores_por_defecto_documentados():
    assert llm.TIMEOUT_MODELO_S == 20
    assert llm.REINTENTOS_MODELO == 2
    assert llm._tiempos({}) == (20, 2)


@pytest.mark.parametrize("parametros, nombre", [
    ({"timeout_s": None}, "timeout_s"),
    ({"timeout_s": "20"}, "timeout_s"),
    ({"timeout_s": 0}, "timeout_s"),
    ({"timeout_s": -5}, "timeout_s"),
    ({"timeout_s": True}, "timeout_s"),
    ({"timeout_s": float("nan")}, "timeout_s"),
    ({"timeout_s": float("inf")}, "timeout_s"),
    ({"reintentos": None}, "reintentos"),
    ({"reintentos": "2"}, "reintentos"),
    ({"reintentos": -1}, "reintentos"),
    ({"reintentos": 1.5}, "reintentos"),
    ({"reintentos": False}, "reintentos"),
])
def test_parametros_invalidos_fallan_nombrando_el_parametro(parametros, nombre):
    with pytest.raises(ValueError) as exc:
        llm._tiempos(parametros)
    assert nombre in str(exc.value)


def test_parametros_validos_explicitos_se_aceptan():
    assert llm._tiempos({"timeout_s": 7.5, "reintentos": 0}) == (7.5, 0)


# Revisión review-c10ae20ecdf4cfa0: un JSON escrito `2.0` es un entero
# lógico; se acepta y se normaliza a int. `2.5` sigue siendo inválido.
@pytest.mark.parametrize("escrito, esperado", [(2.0, 2), (0.0, 0), (3, 3)])
def test_reintentos_entero_escrito_como_flotante_se_acepta(escrito, esperado):
    _timeout, reintentos = llm._tiempos({"reintentos": escrito})
    assert reintentos == esperado
    assert isinstance(reintentos, int)


@pytest.mark.parametrize("invalido", [2.5, -1.0, float("nan"), float("inf"), "2", True])
def test_reintentos_flotante_no_entero_sigue_invalido(invalido):
    with pytest.raises(ValueError) as exc:
        llm._tiempos({"reintentos": invalido})
    assert "reintentos" in str(exc.value)
