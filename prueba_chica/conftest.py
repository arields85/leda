"""Base de pruebas de la prueba chica: un PostgreSQL real, efímero, con el esquema aplicado.

Copia mínima de `tests/conftest.py` (`_con_base_efimera`), sin importarlo: aquel importa
`gateway`, que la frontera de la prueba chica prohíbe (`test_frontera.py`). Es código
descartable, como toda la carpeta.

- La base sale de `LEDA_TEST_DB_URL` (en `.env.test`, que no se versiona): la sesión crea
  una base con nombre irrepetible, aplica `db/esquema.sql`, la usa y la borra al terminar.
  Sin esa variable, las pruebas que piden la base se saltean.
- El `.env` de la carpeta nunca se carga acá (`LEDA_LOAD_DOTENV=0` antes de importar
  `leda`): apunta a la base de la prueba real, y una prueba no la toca nunca.
"""

from __future__ import annotations

import os
import pathlib
import uuid
from collections.abc import Iterator
from datetime import datetime, timezone

os.environ.setdefault("LEDA_LOAD_DOTENV", "0")

import pytest  # noqa: E402

from leda.config import _cargar_dotenv  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parents[1]
ESQUEMA = RAIZ / "db" / "esquema.sql"
AHORA = datetime(2026, 10, 5, 13, 0, tzinfo=timezone.utc)   # lunes, 10:00 en Buenos Aires

_cargar_dotenv(RAIZ / ".env.test")


class _UrlSensible(str):
    def __repr__(self) -> str:
        return "<redacted-db-url>"


@pytest.fixture(scope="session")
def uri() -> Iterator[str]:
    import psycopg
    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    from psycopg.sql import SQL, Identifier

    mantenimiento = os.environ.get("LEDA_TEST_DB_URL")
    if not mantenimiento:
        pytest.skip("Hace falta LEDA_TEST_DB_URL en .env.test (ver tests/conftest.py).")

    nombre = f"leda_test_{uuid.uuid4().hex[:12]}"
    with psycopg.connect(mantenimiento, autocommit=True) as c:
        c.execute(SQL("create database {}").format(Identifier(nombre)))
    url = make_conninfo(**{**conninfo_to_dict(mantenimiento), "dbname": nombre})
    try:
        with psycopg.connect(url, autocommit=True) as c:
            c.execute(ESQUEMA.read_text("utf-8"))
        yield _UrlSensible(url)
    finally:
        with psycopg.connect(mantenimiento, autocommit=True) as c:
            c.execute(SQL("drop database if exists {} with (force)").format(
                Identifier(nombre)))


@pytest.fixture
def conn(uri):
    from leda.db import conectar

    c = conectar(uri)
    yield c
    c.rollback()
    with c.cursor() as cur:
        cur.execute("set role leda_admin")
        # `cascade` alcanza a toda tabla con alcance de espacio, también las del motor.
        cur.execute("""truncate workspace, app_user, platform_role, audit_log, incident,
                                admin_notice restart identity cascade""")
    c.commit()
    c.close()


@pytest.fixture
def mundo(conn) -> dict:
    """Un espacio con dos personas: Ismael tiene una tarea asignada y Marcos la aprueba."""
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
        for i, (nombre, rol) in enumerate((("Marcos", "lider"), ("Ismael", "integrante"))):
            telegram = 81_000 + i
            cur.execute("""insert into app_user (telegram_user_id, nombre)
                           values (%s, %s) returning id""", (telegram, nombre))
            app_user = str(cur.fetchone()["id"])
            aprobador = personas.get("Marcos", {}).get("membership_id")
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
                    (ws, objetivo, area, personas["Ismael"]["membership_id"],
                     datetime(2026, 10, 9, 20, 0, tzinfo=timezone.utc)))
        tarea = str(cur.fetchone()["id"])
        # Sin esto el despachador antepone el saludo del día (pack 06) y cada texto cambia.
        cur.execute("""insert into greeting_state (membership_id, workspace_id, ultima_fecha_local)
                       select id, workspace_id, date '9999-12-31' from membership
                        where workspace_id = %s""", (ws,))
    conn.commit()
    return {"id": ws, "personas": personas, "tarea": tarea}


@pytest.fixture
def escribe(conn, mundo):
    """Guarda un mensaje de una persona en `inbound_message`, como lo hará el escuchador,
    y devuelve su id y quién lo escribió."""
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
