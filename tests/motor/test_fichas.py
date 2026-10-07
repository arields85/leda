"""Las jugadas de la lista cerrada y sus fichas (`leda.motor.fichas`; E2-3).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Jugadas" y "Aviso al administrador"); ADR
0018, decisiones 1, 4 y 9 (9a: nada se confirma; 9b: el aviso de una nueva previsión; 9c: el
bloqueo; 9g: lo que no está en la lista). Los datos siguen a `tests/conversaciones/`: Marcos es
el responsable e Ismael, que aprueba su trabajo, el referente. La IA es guionada y el reloj,
fijo: el lunes 5 de octubre de 2026, 10:00 en Buenos Aires.

Portadas de `prueba_chica/test_fichas.py`. Acá, las que corren una jugada sin el turno; las
que pasan por el turno llegan con él.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from leda.db import admin, espacio
from leda.motor.fichas import FICHAS, JUGADAS, Contexto
from leda.motor.ia import Jugada

from tests.motor.ayudantes import AHORA

VIERNES_9 = datetime(2026, 10, 9, 20, 0, tzinfo=timezone.utc)      # 17:00 en Buenos Aires
OFRECIDAS = ("anotar_inicio", "anotar_prevision", "anotar_bloqueo", "anotar_quien_destraba",
             "destrabar", "consultar_pendientes", "informar_avance")


# --- Ayudas ---------------------------------------------------------------------------------

def _uno(conn, sql: str, *params):
    with admin(conn) as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def _cuantas(conn, tabla: str) -> int:
    return _uno(conn, f"select count(*) n from {tabla}")["n"]


def _tarea_nueva(conn, mundo, titulo: str, estado: str = "asignada",
                 fecha: datetime = VIERNES_9, responsable: str = "Marcos") -> str:
    with admin(conn) as cur:
        cur.execute("""select objective_id, area_id from task where id = %s""",
                    (mundo["tarea"],))
        base = cur.fetchone()
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado, fecha_objetivo)
               values (%s, %s, %s, %s, %s, %s, %s) returning id""",
            (mundo["id"], base["objective_id"], titulo, base["area_id"],
             mundo["personas"][responsable]["membership_id"], estado, fecha))
        tarea = str(cur.fetchone()["id"])
    conn.commit()
    return tarea


def _estado_de(conn, tarea: str) -> str:
    return str(_uno(conn, "select estado from task where id = %s", tarea)["estado"])


@pytest.fixture
def otro_espacio(conn) -> dict:
    """Otro cliente, con una tarea asignada, para el aislamiento."""
    with admin(conn) as cur:
        cur.execute("""insert into workspace (slug, nombre, zona_horaria, activo)
                       values ('otro', 'Otro', 'America/Argentina/Buenos_Aires', true)
                       returning id""")
        ws = str(cur.fetchone()["id"])
        cur.execute("""insert into area (workspace_id, slug, nombre)
                       values (%s, 'campo', 'Campo') returning id""", (ws,))
        area = str(cur.fetchone()["id"])
        cur.execute("""insert into rol (workspace_id, slug, nombre, autoridad_final)
                       values (%s, 'lider', 'lider', true) returning id""", (ws,))
        rol = str(cur.fetchone()["id"])
        cur.execute("""insert into app_user (telegram_user_id, nombre)
                       values (82000, 'Nora') returning id""")
        usuario = str(cur.fetchone()["id"])
        cur.execute("""insert into membership (workspace_id, app_user_id, area_id, rol_id)
                       values (%s, %s, %s, %s) returning id""", (ws, usuario, area, rol))
        persona = str(cur.fetchone()["id"])
        cur.execute("""insert into objective (workspace_id, tipo, titulo, estado)
                       values (%s, 'operativo', 'Ajeno', 'activo') returning id""", (ws,))
        objetivo = str(cur.fetchone()["id"])
        cur.execute("""insert into task (workspace_id, objective_id, titulo, area_id,
                                         responsable_membership_id, estado, fecha_objetivo)
                       values (%s, %s, 'Tarea ajena', %s, %s, 'asignada', %s)
                       returning id""", (ws, objetivo, area, persona, VIERNES_9))
        tarea = str(cur.fetchone()["id"])
    conn.commit()
    return {"id": ws, "tarea": tarea}


# --- La lista cerrada -----------------------------------------------------------------------

SITUACIONES = ("elegir", "corregir", "cancelar", "dejar_para_despues")


def test_la_lista_cerrada_tiene_una_ficha_por_jugada_del_recordatorio():
    """Las del recordatorio y las de las situaciones generales (E2-4), que no se ofrecen como
    algo que Leda puede hacer."""
    assert sorted(JUGADAS) == sorted(FICHAS) == sorted(
        OFRECIDAS + ("entregar", "pedir_reasignacion") + SITUACIONES)
    assert not any(FICHAS[n].se_ofrece for n in SITUACIONES)
    for ficha in FICHAS.values():
        assert ficha.para_que and ficha.comprueba and ficha.hace and ficha.despues


# --- Aislamiento ----------------------------------------------------------------------------

def _contexto(cur, quien, entrante: str, tarea_id: str) -> Contexto:
    """Un contexto con una tarea que no es de la persona, como si le llegara con alias."""
    return Contexto(cur=cur, quien=quien, entrante_id=entrante, chat_id=0, texto="-",
                    ahora=AHORA, estado=None, ultimos_turnos=(),
                    tareas=({"alias": "T1", "id": tarea_id, "titulo": "Ajena",
                             "estado": "asignada", "fecha_objetivo": None},))


@pytest.mark.parametrize("jugada", [
    Jugada("anotar_inicio", {"tarea": "T1"}),
    Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-13"}),
    Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "faltan cables"}),
])
def test_una_jugada_nunca_toca_una_tarea_de_otro_espacio(conn, mundo, escribe, otro_espacio,
                                                         jugada):
    quien, entrante = escribe("Marcos", "-")
    with espacio(conn, mundo["id"]) as cur:
        hecho = JUGADAS[jugada.nombre](_contexto(cur, quien, entrante, otro_espacio["tarea"]),
                                       jugada)
    conn.commit()

    assert hecho["resultado"] == "no_se_puede"
    assert hecho["motivo"] in ("tarea_desconocida", "no_autorizado")
    assert _estado_de(conn, otro_espacio["tarea"]) == "asignada"
    for tabla in ("task_state_event", "task_forecast", "blocker", "scheduled_notice",
                  "conversation_question"):
        assert _cuantas(conn, tabla) == 0, tabla


# --- Lo que la operación del dominio contesta (revisión de la E2-3) -------------------------

def _tarea_cerrada_con_alias(conn, mundo, estado: str) -> str:
    """Una tarea de Marcos ya cerrada que, como si se hubiera cerrado durante el turno,
    todavía le llega a la ficha con alias."""
    return _tarea_nueva(conn, mundo, "Tarea cerrada", estado=estado)


@pytest.mark.parametrize("estado", ["terminada", "cancelada"])
@pytest.mark.parametrize("jugada", [
    Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-13"}),
    Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "faltan cables"}),
])
def test_una_tarea_cerrada_no_acepta_prevision_ni_bloqueo(conn, mundo, escribe, estado,
                                                          jugada):
    tarea = _tarea_cerrada_con_alias(conn, mundo, estado)
    quien, entrante = escribe("Marcos", "-")
    with espacio(conn, mundo["id"]) as cur:
        hecho = JUGADAS[jugada.nombre](_contexto(cur, quien, entrante, tarea), jugada)
    conn.commit()

    assert hecho["resultado"] == "no_se_puede" and hecho["motivo"] == "estado"
    assert hecho["estado"] == estado
    for tabla in ("task_forecast", "scheduled_notice", "blocker", "conversation_question"):
        assert _cuantas(conn, tabla) == 0, tabla

