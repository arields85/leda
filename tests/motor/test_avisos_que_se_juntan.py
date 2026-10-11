"""Los límites de qué avisos se juntan en un envío (decisión 72 del usuario, 2026-10-11;
`avisos._envios` y `avisos._se_junta`; revisión de `6886ea8`).

Se juntan sólo los informativos de coordinación que causó un mismo mensaje (el mismo turno), a la
misma persona y sobre la misma tarea. Un turno distinto, otra tarea u otra persona salen aparte, y
nunca se junta un aviso que pide respuesta, abre una pregunta, ofrece decidir, recuerda una
decisión, lleva botones, adjuntos o el enlace, deja una oferta o sale solo. Son reglas puras sobre
los avisos ya vigentes: no hace falta una base.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from leda.motor.avisos import TipoDeAviso, _envios, _Listo

INFORMATIVO = TipoDeAviso("prueba_informativo", "informativo", lambda m, a: (None, {}),
                          es_coordinacion=True)


def _listo(n: int, *, turno: str = "t1", tarea: str = "T1", a: str = "marcos",
           tipo: TipoDeAviso = INFORMATIVO, solo: bool = False) -> _Listo:
    return _Listo(aviso={"id": f"a{n}", "turno_id": turno, "task_id": tarea},
                  tipo=tipo, destinatario={"membership_id": a}, hechos={"n": n}, solo=solo)


def _ids(envios: list[list[_Listo]]) -> list[list[str]]:
    return [[x.aviso["id"] for x in envio] for envio in envios]


def test_los_del_mismo_turno_a_la_misma_persona_sobre_la_misma_tarea_van_en_uno():
    assert _ids(_envios(None, [_listo(1), _listo(2), _listo(3)])) == [["a1", "a2", "a3"]]


@pytest.mark.parametrize("distinto", [{"turno": "t2"}, {"tarea": "T2"}, {"a": "ariel"}])
def test_un_turno_otra_tarea_u_otra_persona_salen_aparte(distinto):
    assert _ids(_envios(None, [_listo(1), _listo(2, **distinto)])) == [["a1"], ["a2"]]


def test_sin_turno_o_sin_tarea_no_se_junta():
    sin_turno = replace(_listo(2), aviso={"id": "a2", "turno_id": None, "task_id": "T1"})
    sin_tarea = replace(_listo(3), aviso={"id": "a3", "turno_id": "t1", "task_id": None})

    assert _ids(_envios(None, [_listo(1), sin_turno, sin_tarea])) == [["a1"], ["a2"], ["a3"]]


@pytest.mark.parametrize("cambio", [
    {"tipo_de_mensaje": "normal"},                      # pide respuesta
    {"es_coordinacion": False},                         # seguimiento, cuenta para el tope
    {"abre": lambda m, a: ("cuando_se_destraba", {})},  # abre una pregunta
    {"ofrece": ("aprobar",)},                           # ofrece decidir, con botones
    {"opciones": lambda m, a: ("propuesta", {}, [])},   # sus propias opciones, con botones
    {"recuerda": "decidir_el_pase"},                    # recuerda una decisión abierta
    {"ofrece_ver": True},                               # un botón para ver la entrega
    {"adjuntos": lambda m, a: []},
    {"enlace": "destinatario"},
    {"deja_una_oferta": lambda m, a: {"nombre": "pasarle_algo"}},
], ids=lambda c: next(iter(c)))
def test_un_aviso_con_algo_propio_de_salir_solo_nunca_se_junta(cambio):
    propio = replace(INFORMATIVO, nombre="prueba_propio", **cambio)

    envios = _envios(None, [_listo(1), _listo(2, tipo=propio), _listo(3)])

    assert ["a2"] in _ids(envios)
    assert ["a1", "a3"] in _ids(envios)


def test_una_oferta_que_esta_vez_no_ofrece_nada_se_junta():
    sin_oferta = replace(INFORMATIVO, deja_una_oferta=lambda m, a: None)

    assert _ids(_envios(None, [_listo(1), _listo(2, tipo=sin_oferta)])) == [["a1", "a2"]]


def test_la_pregunta_repetida_sale_sola():
    assert _ids(_envios(None, [_listo(1), _listo(2, solo=True)])) == [["a1"], ["a2"]]
