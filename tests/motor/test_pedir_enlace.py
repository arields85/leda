"""Pedir por chat el enlace a la página de una tarea (`leda.motor.enlace`; ADR 0019, decisión 7a:
"cualquiera de los que pueden verla, cuando lo pide por chat: una jugada nueva de la lista
cerrada"; conversación 31).

La IA nombra la tarea por su alias, si está en la lista de la persona, o por cómo la dijo
(`como_la_nombra`), si no está: una terminada, una de otra persona. La cocina la busca entre las
tareas del espacio y la base decide si la persona puede verla (`puede_ver_tarea`, 7b). Sólo
entonces la respuesta lleva la marca del enlace (`message_outbox_enlace`), que el despachador
emite al mandar; la IA nunca ve ni escribe una dirección.
"""

from __future__ import annotations

import dataclasses
from datetime import timedelta

import pytest

from leda import config as config_mod
from leda.db import admin
from leda.motor import hechos as hechos_mod
from leda.motor.avisos import LLEVA_EL_ENLACE
from leda.motor.fichas import FICHAS
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.ia_real import DATOS
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_turno

from tests.motor.ayudantes import AHORA, cuantas, todos
from tests.motor.test_aprobacion import _nahuel, _tarea
from tests.motor.test_fichas import otro_espacio  # noqa: F401 -- la fixture del aislamiento

DIRECCION = "https://leda.invalid/"


@pytest.fixture
def direccion(monkeypatch):
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=DIRECCION))


def _pide(conn, escribe, nombre: str, texto: str = "pasame el link", **datos):
    """Un mensaje de `nombre` que la IA lee como `pedir_enlace` con `datos`: los hechos de la
    jugada y lo que la IA recibió para redactar."""
    quien, entrante = escribe(nombre, texto)
    ia = IAGuionada(jugadas=[[Jugada("pedir_enlace", datos)]], redacciones=["Listo."])
    resultado = procesar_turno(conn, quien, entrante, ia, RelojFijo(AHORA))
    conn.commit()
    assert resultado.error is None
    [hecho] = resultado.hechos
    return hecho, ia.pedidos_de_redaccion[-1]


def _enlaces(conn) -> list[dict]:
    """Las marcas de enlace de las respuestas: de qué tarea y para quién."""
    return todos(conn, """select e.task_id::text tarea, e.membership_id::text persona
                            from message_outbox_enlace e
                            join message_outbox o on o.id = e.outbox_id
                           where o.es_respuesta""")


def _terminada(conn, mundo, titulo: str) -> str:
    """Una tarea de Marcos que ya quedó terminada, con la aprobación de Ismael que su cierre
    exige."""
    tarea = _tarea(conn, mundo, titulo=titulo)
    with admin(conn) as cur:
        cur.execute("""insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                             aprobador_membership_id, decision)
                       values (%s, 'tarea', %s, %s, 'aprobado')""",
                    (mundo["id"], tarea, mundo["personas"]["Ismael"]["membership_id"]))
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind, motivo, at)
                       values (%s, 'en_curso', 'terminada', 'persona', 'prueba', %s)""",
                    (tarea, AHORA - timedelta(days=1)))
    conn.commit()
    return tarea


# --- La ficha --------------------------------------------------------------------------------

def test_pedir_el_enlace_es_una_ficha_de_la_lista_cerrada():
    ficha = FICHAS["pedir_enlace"]
    assert ficha.se_ofrece and not ficha.del_responsable
    assert ficha.necesita == () and set(ficha.opcional) == {"tarea", "como_la_nombra"}
    assert DATOS["como_la_nombra"][0] == "string"
    # La redacción la recibe por lo que hace, y sus códigos tienen significado.
    assert hechos_mod.es_un_concepto_de_la_cocina("pedir_enlace")
    assert "pedir_enlace" in hechos_mod.PARA_LA_REDACCION
    for codigo in ("como_la_nombra", "no_puede_ver_esa_tarea", "ninguna_tarea_con_ese_nombre",
                   "la_pagina_no_esta_disponible", "ya_lleva_el_enlace_de_otra_tarea"):
        assert hechos_mod.significado(codigo), codigo


# --- Quien puede verla recibe su enlace ------------------------------------------------------

def test_una_tarea_suya_por_su_alias_lleva_su_enlace(conn, mundo, escribe, direccion):
    hecho, pedido = _pide(conn, escribe, "Marcos", tarea="T1")
    assert hecho == {"jugada": "pedir_enlace", "resultado": "leido",
                     "tarea": {"alias": "T1", "titulo": "Revisar el tablero"},
                     LLEVA_EL_ENLACE: True}
    assert _enlaces(conn) == [{"tarea": mundo["tarea"],
                               "persona": mundo["personas"]["Marcos"]["membership_id"]}]
    # La IA nunca ve una dirección: sabe que el código la agrega.
    assert "http" not in repr(pedido) and "leda.invalid" not in repr(pedido)


def test_una_de_otra_persona_fuera_de_su_lista_por_como_la_nombra(conn, mundo, escribe,
                                                                   direccion):
    """Ismael no tiene tareas ni entregas para revisar: la nombra por cómo la dijo, con el
    nombre de quien la tiene."""
    hecho, _ = _pide(conn, escribe, "Ismael", como_la_nombra="la del tablero de marcos")
    assert hecho["resultado"] == "leido" and hecho[LLEVA_EL_ENLACE] is True
    assert hecho["tarea"] == {"titulo": "Revisar el tablero"}
    assert hecho["responsable"] == "Marcos"
    assert _enlaces(conn) == [{"tarea": mundo["tarea"],
                               "persona": mundo["personas"]["Ismael"]["membership_id"]}]


def test_una_terminada_tambien_se_encuentra(conn, mundo, escribe, direccion):
    terminada = _terminada(conn, mundo, "Revisar comunicaciones industriales")
    hecho, _ = _pide(conn, escribe, "Marcos", como_la_nombra="Comunicación industrial")
    assert hecho["resultado"] == "leido"
    assert hecho["tarea"] == {"titulo": "Revisar comunicaciones industriales"}
    assert "responsable" not in hecho          # es suya
    assert [e["tarea"] for e in _enlaces(conn)] == [terminada]


def test_se_busca_por_palabras_enteras_sin_mayusculas_ni_acentos(conn, mundo, escribe,
                                                                 direccion):
    """Lo que la persona dice tiene que estar en el nombre de la tarea o de quien la tiene; las
    palabras de unión no cuentan. "Tab" no es "tablero"."""
    _tarea(conn, mundo, titulo="Pintar el galpón")
    hecho, _ = _pide(conn, escribe, "Ismael", como_la_nombra="TABLERO")
    assert hecho["tarea"] == {"titulo": "Revisar el tablero"}
    hecho, _ = _pide(conn, escribe, "Ismael", como_la_nombra="galpon")
    assert hecho["tarea"] == {"titulo": "Pintar el galpón"}
    hecho, _ = _pide(conn, escribe, "Ismael", como_la_nombra="tab")
    assert hecho["resultado"] == "no_se_puede"
    assert hecho["motivo"] == "ninguna_tarea_con_ese_nombre"


# --- Quien no puede verla no recibe nada -----------------------------------------------------

def test_quien_no_puede_verla_no_recibe_el_enlace(conn, mundo, escribe, direccion):
    """Nahuel no es su responsable, no aprueba el trabajo de Marcos ni decidió sobre ella, no
    es referente del área ni la autoridad final (ADR 0019, 7b)."""
    _nahuel(conn, mundo)
    hecho, pedido = _pide(conn, escribe, "Nahuel", como_la_nombra="tablero de marcos")
    assert hecho == {"jugada": "pedir_enlace", "resultado": "no_se_puede",
                     "motivo": "no_puede_ver_esa_tarea",
                     "tarea": {"titulo": "Revisar el tablero"}}
    assert _enlaces(conn) == []
    # Nada dice quién sí la ve (decisión 11), ni un nombre de la base (constitución §10).
    assert "Ismael" not in repr(pedido) and "puede_ver_tarea" not in repr(pedido)


def test_entre_varias_que_coinciden_sale_la_unica_que_puede_ver(conn, mundo, escribe,
                                                                direccion):
    _nahuel(conn, mundo)
    suya = _tarea(conn, mundo, titulo="Cablear el tablero", quien="Nahuel")
    hecho, _ = _pide(conn, escribe, "Nahuel", como_la_nombra="tablero")
    assert hecho["resultado"] == "leido"
    assert hecho["tarea"]["titulo"] == "Cablear el tablero"
    assert [e["tarea"] for e in _enlaces(conn)] == [suya]


def test_si_puede_ver_varias_que_coinciden_pregunta_cual(conn, mundo, escribe, direccion):
    _tarea(conn, mundo, titulo="Cablear el tablero")
    hecho, _ = _pide(conn, escribe, "Ismael", como_la_nombra="tablero")
    assert hecho["resultado"] == "falta_dato" and hecho["falta"] == ["tarea"]
    assert sorted(c["titulo"] for c in hecho["coinciden"]) == ["Cablear el tablero",
                                                               "Revisar el tablero"]
    assert _enlaces(conn) == []


def test_sin_nombrar_ninguna_falta_cual(conn, mundo, escribe, direccion):
    hecho, _ = _pide(conn, escribe, "Ismael")
    assert hecho == {"jugada": "pedir_enlace", "resultado": "falta_dato", "falta": ["tarea"]}
    assert _enlaces(conn) == []


def test_una_tarea_de_otro_espacio_nunca_se_encuentra(conn, mundo, escribe, direccion,
                                                       otro_espacio):  # noqa: F811
    """La busca en el espacio de quien escribe (la RLS y el filtro): la de otro espacio no
    existe para ella, aunque se llame igual."""
    hecho, _ = _pide(conn, escribe, "Ismael", como_la_nombra="tarea ajena")
    assert hecho["motivo"] == "ninguna_tarea_con_ese_nombre"
    assert _enlaces(conn) == []
    assert cuantas(conn, "message_outbox_enlace", "task_id = %s", otro_espacio["tarea"]) == 0


def test_sin_la_direccion_publica_no_hay_enlace_y_lo_dice(conn, mundo, escribe, monkeypatch):
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=""))
    hecho, _ = _pide(conn, escribe, "Marcos", tarea="T1")
    assert hecho["resultado"] == "no_se_puede"
    assert hecho["motivo"] == "la_pagina_no_esta_disponible"
    assert LLEVA_EL_ENLACE not in hecho
    assert _enlaces(conn) == []


def test_pedir_el_enlace_no_cambia_nada(conn, mundo, escribe, direccion):
    antes = {t: cuantas(conn, t) for t in ("task_state_event", "scheduled_notice",
                                           "conversation_question", "audit_log")}
    _pide(conn, escribe, "Marcos", tarea="T1")
    assert {t: cuantas(conn, t) for t in antes} == antes


def test_un_solo_enlace_por_mensaje(conn, mundo, escribe, direccion):
    """La respuesta lleva un enlace al final: el de otra tarea en el mismo mensaje no se
    promete."""
    otra = _tarea(conn, mundo, titulo="Probar las comunicaciones")
    quien, entrante = escribe("Marcos", "pasame los dos links")
    ia = IAGuionada(jugadas=[[Jugada("pedir_enlace", {"tarea": "T1"}),
                              Jugada("pedir_enlace", {"tarea": "T2"})]],
                    redacciones=["Listo."])
    resultado = procesar_turno(conn, quien, entrante, ia, RelojFijo(AHORA))
    conn.commit()
    primera, segunda = resultado.hechos
    assert primera[LLEVA_EL_ENLACE] is True
    assert segunda["resultado"] == "no_se_puede"
    assert segunda["motivo"] == "ya_lleva_el_enlace_de_otra_tarea"
    assert [e["tarea"] for e in _enlaces(conn)] != [otra]
    assert len(_enlaces(conn)) == 1
