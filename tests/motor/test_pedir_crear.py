"""Crear una tarea o un objetivo por chat: la jugada `pedir_crear` (J4b; decisión D12 del usuario,
2026-10-14; ADR 0017, decisión 2: por chat, hechos del trabajo; por la web, su estructura; ADR 0018,
decisión 1: una jugada de la lista cerrada, que la IA elige por su definición).

Nada se crea por chat. La cocina dice, según quién es la persona y qué quiere crear:

- **Una tarea:** a Dirección y a un referente, que la crea en su web, con el enlace de entrada al
  final (la mecánica de `pedir_acceso_web`, uno por mensaje); a un integrante, sin enlace, quiénes
  las cargan (su referente y Dirección) y que pronto podrá proponerlas.
- **Un objetivo:** a Dirección, el enlace; a un referente, que los crea Dirección; a un integrante,
  lo mismo que con una tarea.
- Ya no es algo "fuera de la lista": no deja el incidente de una jugada que falta.
"""

from __future__ import annotations

import dataclasses

import pytest

from leda import config as config_mod
from leda.db import admin
from leda.motor.fichas import FICHAS
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_turno

from tests.motor.ayudantes import AHORA, cuantas, todos, ya_ofrecida_la_web

ENLACE = {"lleva_el_enlace_de_entrada_a_la_web": True, "sirve_una_sola_vez": True,
          "vence_a_las_24_horas": True}


@pytest.fixture
def equipo(conn, mundo) -> dict:
    """El mundo del motor con Marcos como referente de su área (Campo) y Nahuel, de su gente."""
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = %s where id = %s",
                    (mundo["personas"]["Marcos"]["membership_id"], mundo["area"]))
        cur.execute("select rol_id from membership where id = %s",
                    (mundo["personas"]["Marcos"]["membership_id"],))
        rol = cur.fetchone()["rol_id"]
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (81019, 'Nahuel') returning id""")
        usuario = str(cur.fetchone()["id"])
        cur.execute("""insert into membership (workspace_id, app_user_id, area_id, rol_id,
                                               aprobador_membership_id)
                       values (%s, %s, %s, %s, %s) returning id""",
                    (mundo["id"], usuario, mundo["area"], rol,
                     mundo["personas"]["Marcos"]["membership_id"]))
        mundo["personas"]["Nahuel"] = {"app_user_id": usuario, "telegram": 81019,
                                       "membership_id": str(cur.fetchone()["id"])}
        cur.execute("""insert into greeting_state (membership_id, workspace_id, ultima_fecha_local)
                       values (%s, %s, date '9999-12-31')""",
                    (mundo["personas"]["Nahuel"]["membership_id"], mundo["id"]))
        ya_ofrecida_la_web(cur, mundo["id"])
    conn.commit()
    return mundo


@pytest.fixture
def con_la_web(monkeypatch):
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url="https://leda.invalid/"))


def _pide(conn, escribe, nombre: str, que: str | None) -> tuple[dict, list[dict]]:
    """`nombre` pide crear algo; la IA guionada elige la jugada. Sus hechos y las marcas del
    enlace de entrada que lleva la respuesta."""
    quien, entrante = escribe(nombre, "quiero crear algo")
    datos = {} if que is None else {"que_quiere_crear": que}
    ia = IAGuionada(jugadas=[[Jugada("pedir_crear", datos)]], redacciones=["Listo."])
    resultado = procesar_turno(conn, quien, entrante, ia, RelojFijo(AHORA))
    conn.commit()
    assert resultado.error is None
    [hecho] = resultado.hechos
    marcas = todos(conn, """select w.membership_id::text persona from message_outbox_entrada_web w
                             join message_outbox o on o.id = w.outbox_id where o.es_respuesta""")
    return hecho, marcas


def test_es_una_jugada_de_la_lista_cerrada_sin_tarea_que_no_se_ofrece():
    ficha = FICHAS["pedir_crear"]
    assert ficha.necesita == ("que_quiere_crear",) and ficha.opcional == ()
    assert ficha.se_ofrece is False
    assert ficha.es and "crear" in ficha.es


@pytest.mark.usefixtures("con_la_web")
def test_direccion_crea_tareas_y_objetivos_en_su_web(conn, equipo, escribe):
    for que in ("tarea", "objetivo"):
        hecho, marcas = _pide(conn, escribe, "Ismael", que)
        assert hecho == {"jugada": "pedir_crear", "resultado": "se_crea_en_la_web",
                         "que_quiere_crear": que, "puede_hacerlo_en_la_web": True, **ENLACE,
                         "el_anterior_ya_no_sirve": False}
    assert [m["persona"] for m in marcas] == [equipo["personas"]["Ismael"]["membership_id"]] * 2
    # Ya no es algo fuera de la lista.
    assert cuantas(conn, "incident") == 0


@pytest.mark.usefixtures("con_la_web")
def test_un_referente_crea_tareas_y_los_objetivos_los_crea_direccion(conn, equipo, escribe):
    hecho, marcas = _pide(conn, escribe, "Marcos", "tarea")
    assert hecho["puede_hacerlo_en_la_web"] is True and hecho["sirve_una_sola_vez"] is True
    assert len(marcas) == 1
    hecho, marcas = _pide(conn, escribe, "Marcos", "objetivo")
    assert hecho == {"jugada": "pedir_crear", "resultado": "se_crea_en_la_web",
                     "que_quiere_crear": "objetivo", "puede_hacerlo_en_la_web": False,
                     "lo_hacen": ["Ismael"]}
    assert len(marcas) == 1, "el pedido de un objetivo no lleva enlace"


@pytest.mark.usefixtures("con_la_web")
def test_un_integrante_no_recibe_enlace_y_sabe_quien_las_carga(conn, equipo, escribe):
    for que in ("tarea", "objetivo"):
        hecho, marcas = _pide(conn, escribe, "Nahuel", que)
        assert hecho == {"jugada": "pedir_crear", "resultado": "se_crea_en_la_web",
                         "que_quiere_crear": que, "puede_hacerlo_en_la_web": False,
                         "lo_hacen": ["Marcos", "Ismael"], "pronto_podra_proponerlo": True}
        assert marcas == []


def test_sin_la_direccion_publica_ningun_enlace_se_promete(conn, equipo, escribe):
    hecho, marcas = _pide(conn, escribe, "Ismael", "tarea")
    assert hecho["puede_hacerlo_en_la_web"] is True
    assert hecho["el_enlace_no_va"] == "la_pagina_no_esta_disponible"
    assert "lleva_el_enlace_de_entrada_a_la_web" not in hecho and marcas == []


def test_sin_decir_que_quiere_crear_falta_el_dato(conn, equipo, escribe):
    hecho, marcas = _pide(conn, escribe, "Marcos", None)
    assert hecho["resultado"] == "falta_dato" and hecho["falta"] == ["que_quiere_crear"]
    assert marcas == []
