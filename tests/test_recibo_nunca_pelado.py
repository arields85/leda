"""Nunca un comprobante pelado (T10-2b, U1; ADR 0013 regla 2).

Toda preparación que escribe define su comprobante corto (`Preparacion.hecho`),
y el gateway, si por un descuido llegara vacío, no manda un "Hecho." solo.
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
import textwrap

from leda import herramientas as H
from tests.test_botones import cliente  # noqa: F401
from tests.test_vista_previa_en_filas import _confirmar


def _preparaciones_que_escriben() -> dict[str, object]:
    """Todas las herramientas que confirman con vista previa, halladas por el
    registro: una herramienta nueva con `preparar=` entra sola."""
    return {n: h.preparar for n, h in H.REGISTRO.items() if h.preparar is not None}


def _llamadas_a_preparacion(funcion) -> list[ast.Call]:
    arbol = ast.parse(textwrap.dedent(inspect.getsource(funcion)))
    return [n for n in ast.walk(arbol)
            if isinstance(n, ast.Call)
            and getattr(n.func, "id", None) == "Preparacion"]


def test_hay_preparaciones_que_escriben():
    assert len(_preparaciones_que_escriben()) >= 8


def test_toda_preparacion_que_escribe_define_su_comprobante():
    """Cada `Preparacion(...)` que arma una preparación lleva `hecho=` con algo
    más que una cadena vacía."""
    sin_comprobante = []
    for nombre, preparar in _preparaciones_que_escriben().items():
        llamadas = _llamadas_a_preparacion(preparar)
        if not llamadas:
            sin_comprobante.append(f"{nombre}: no arma ninguna Preparacion")
        for llamada in llamadas:
            kw = {k.arg: k.value for k in llamada.keywords}
            valor = kw.get("hecho")
            vacio = valor is None or (
                isinstance(valor, ast.Constant) and not valor.value)
            if vacio:
                sin_comprobante.append(f"{nombre}: línea {llamada.lineno}")
    assert sin_comprobante == []


def test_el_gateway_no_manda_un_hecho_pelado_si_el_comprobante_llega_vacio(
        cliente, conn, corework, monkeypatch):
    original = H.REGISTRO["registrar_bloqueo"]

    def preparar_sin_comprobante(*args, **kwargs):
        prep = original.preparar(*args, **kwargs)
        return dataclasses.replace(prep, hecho="")

    monkeypatch.setitem(
        H.REGISTRO, "registrar_bloqueo",
        dataclasses.replace(original, preparar=preparar_sin_comprobante))
    cuerpo = _confirmar(
        cliente, conn, corework.workspace_id, "registrar_bloqueo",
        lambda t: {"tarea_id": t, "causa": "falta el switch"})
    assert cuerpo.strip() != "Hecho."
    assert "Programar PLC" in cuerpo
