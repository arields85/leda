"""Fixtures de las pruebas del motor.

La base efímera y la conexión son las de `tests/conftest.py` (`uri`, `conn`); acá va el
mundo de las conversaciones de prueba, el mismo de `prueba_chica/conftest.py`: un espacio con
dos personas, Ismael, referente y autoridad, y Marcos, con una tarea asignada que vence el
viernes 9 de octubre de 2026. También sus dos tareas (`tareas`), sus turnos (`marcos`) y la
duda de un toque: Marcos arrancó sin decir cuál, y Leda le preguntó con sus dos tareas. Y la
escalera: el espacio con su configuración (`espacio_con_escalera`) y sus ciclos día por día
(`dias`).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from leda.motor.ia import Jugada

from tests.motor.ayudantes import AHORA, Charla, Dias, nueva_tarea, todos


@pytest.fixture
def mundo(conn) -> dict:
    from leda.db import admin

    with admin(conn) as cur:
        cur.execute("""insert into workspace (slug, nombre, zona_horaria, activo)
                       values ('prueba', 'Prueba', 'America/Argentina/Buenos_Aires', true)
                       returning id""")
        ws = str(cur.fetchone()["id"])
        cur.execute("""insert into work_calendar (workspace_id, dias, hora_inicio, hora_fin)
                       values (%s, array['lunes','martes','miercoles','jueves','viernes'],
                               '09:00', '17:00')""", (ws,))
        cur.execute("insert into persona_config (workspace_id) values (%s)", (ws,))
        cur.execute("""insert into workspace_version (workspace_id, version, pack_hash)
                       values (%s, 1, 'hash-prueba')""", (ws,))
        cur.execute("""insert into area (workspace_id, slug, nombre)
                       values (%s, 'campo', 'Campo') returning id""", (ws,))
        area = str(cur.fetchone()["id"])
        roles = {}
        for slug, final in (("lider", True), ("integrante", False)):
            cur.execute("""insert into rol (workspace_id, slug, nombre, autoridad_final)
                           values (%s, %s, %s, %s) returning id""", (ws, slug, slug, final))
            roles[slug] = str(cur.fetchone()["id"])
        personas = {}
        for i, (nombre, rol) in enumerate((("Ismael", "lider"), ("Marcos", "integrante"))):
            telegram = 81_000 + i
            cur.execute("""insert into app_user (telegram_user_id, nombre)
                           values (%s, %s) returning id""", (telegram, nombre))
            app_user = str(cur.fetchone()["id"])
            aprobador = personas.get("Ismael", {}).get("membership_id")
            cur.execute("""insert into membership (workspace_id, app_user_id, area_id, rol_id,
                                                   aprobador_membership_id)
                           values (%s, %s, %s, %s, %s) returning id""",
                        (ws, app_user, area, roles[rol], aprobador))
            personas[nombre] = {"app_user_id": app_user, "telegram": telegram,
                                "membership_id": str(cur.fetchone()["id"])}
        cur.execute("""insert into objective (workspace_id, tipo, titulo, estado)
                       values (%s, 'operativo', 'Tablero nuevo', 'activo') returning id""",
                    (ws,))
        objetivo = str(cur.fetchone()["id"])
        cur.execute("""insert into task (workspace_id, objective_id, titulo, area_id,
                                         responsable_membership_id, estado, fecha_objetivo)
                       values (%s, %s, 'Revisar el tablero', %s, %s, 'asignada', %s)
                       returning id""",
                    (ws, objetivo, area, personas["Marcos"]["membership_id"],
                     datetime(2026, 10, 9, 20, 0, tzinfo=timezone.utc)))
        tarea = str(cur.fetchone()["id"])
        # Sin esto el despachador antepone el saludo del día (pack 06) y cada texto cambia.
        cur.execute("""insert into greeting_state (membership_id, workspace_id, ultima_fecha_local)
                       select id, workspace_id, date '9999-12-31' from membership
                        where workspace_id = %s""", (ws,))
    conn.commit()
    return {"id": ws, "personas": personas, "tarea": tarea, "objetivo": objetivo,
            "area": area}


@pytest.fixture
def escribe(conn, mundo):
    """Guarda un mensaje de una persona en `inbound_message`, como lo hará el escuchador, y
    devuelve quién lo escribió y el id del mensaje."""
    from leda.autoridad import identificar_en_espacio
    from leda.db import espacio

    def _escribe(nombre: str, texto: str, at: datetime = AHORA):
        persona = mundo["personas"][nombre]
        with espacio(conn, mundo["id"]) as cur:
            quien = identificar_en_espacio(cur, persona["telegram"], mundo["id"])
            cur.execute(
                """insert into inbound_message (workspace_id, telegram_message_id, chat_id,
                                                app_user_id, texto, at)
                   values (%s, %s, %s, %s, %s, %s) returning id""",
                (mundo["id"], uuid.uuid4().int % 1_000_000, persona["telegram"],
                 persona["app_user_id"], texto, at))
            entrante = str(cur.fetchone()["id"])
        conn.commit()
        return quien, entrante

    return _escribe


@pytest.fixture
def duda(conn, mundo, escribe) -> dict:
    """Marcos dijo que arrancó sin decir cuál: Leda le preguntó con las dos tareas."""
    t2 = nueva_tarea(conn, mundo, "Probar las comunicaciones")
    Charla(conn, escribe).dice(Jugada("anotar_inicio", {}), texto="hoy arranque")
    tokens = {o["orden"]: o["token"] for o in todos(conn, "select orden, token "
                                                          "from conversation_option")}
    return {"T1": mundo["tarea"], "T2": t2, "O1": tokens[1], "O2": tokens[2]}


@pytest.fixture
def tareas(conn, mundo) -> dict[str, str]:
    """Las dos tareas de Marcos: "Revisar el tablero" (T1) y "Probar las comunicaciones" (T2)."""
    return {"T1": mundo["tarea"], "T2": nueva_tarea(conn, mundo, "Probar las comunicaciones")}


@pytest.fixture
def marcos(conn, escribe) -> Charla:
    """Los turnos de Marcos, uno por mensaje (`ayudantes.Charla`)."""
    return Charla(conn, escribe)


@pytest.fixture
def espacio_con_escalera(conn, mundo) -> dict:
    """CoreWork en chico: aviso previo a 3 días hábiles, el feriado del lunes 12 y la falta de
    respuesta escalada a quien lidera (Ismael)."""
    from leda.db import admin

    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'aviso_previo_dias_habiles', '3')""", (mundo["id"],))
        cur.execute("insert into holiday (workspace_id, fecha) values (%s, '2026-10-12')",
                    (mundo["id"],))
        cur.execute("""insert into escalation_route (workspace_id, disparador, destino_rol_id)
                       select %s, 'falta_persistente_de_respuesta', id from rol
                        where workspace_id = %s and slug = 'lider'""",
                    (mundo["id"], mundo["id"]))
    conn.commit()
    return mundo


@pytest.fixture
def dias(conn, espacio_con_escalera) -> Dias:
    """Los ciclos de la escalera, día por día (`ayudantes.Dias`)."""
    return Dias(conn, espacio_con_escalera)
