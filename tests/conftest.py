"""Base de pruebas: un PostgreSQL real, efímero, con el esquema aplicado.

Las reglas que importan viven en disparadores y funciones de la base, así que
probar contra un doble no serviría de nada.

Hay dos formas de conseguir ese PostgreSQL:

- Por defecto, `pgserver` levanta un servidor descartable dentro de un
  directorio temporal. No hay wheels para Windows.
- Si `LEDA_TEST_DB_URL` está definida, se usa ese servidor: la sesión crea
  una base con nombre irrepetible, la usa y la borra al terminar. Es una base
  aparte a propósito — las pruebas truncan todo entre casos, y apuntar esto a
  una base con datos reales los perdería.

La variable se puede dejar en `.env.test`, que no se versiona:

    LEDA_TEST_DB_URL=postgresql://postgres:CONTRASENA@localhost:5432/postgres

Tiene que ser un usuario con permiso para CREATE DATABASE y CREATE ROLE — el
esquema crea `leda_app` y `leda_admin`, que son del cluster — y apuntar a
la base de mantenimiento, no a la de la aplicación.
"""

from __future__ import annotations

import os
import pathlib
import secrets
import uuid
from collections.abc import Iterator

import pytest

from leda.config import _cargar_dotenv

RAIZ = pathlib.Path(__file__).resolve().parents[1]
ESQUEMA = RAIZ / "db" / "esquema.sql"

if os.environ.get("LEDA_TEST_LOAD_DOTENV", "1") != "0":
    _cargar_dotenv(RAIZ / ".env.test")


class _SensitiveUrl(str):
    def __repr__(self) -> str:
        return "<redacted-db-url>"


def _blindar_contra_saludo(cur, workspace_id: str) -> None:
    """Marca a todas las personas de un espacio como ya saludadas hoy, en una
    fecha muy lejana (saludo diario, pack 06).

    El saludo es una nueva pieza determinística que se antepone a la primera
    respuesta del día de cualquier persona: sin esto, cada prueba que arma un
    `Solicitante` recién creado por estas fixtures compartidas se volvería,
    sin quererlo, una prueba del saludo -- decenas de aserciones de texto
    exacto en pruebas que no tienen nada que ver con el pack 06 empezarían a
    fallar por un "👋 Buen día" que nadie pidió. Una fecha bien futura (nunca
    alcanzada por el `ahora` fijo de ninguna prueba) hace que
    `saludo.reclamar_saludo` nunca vuelva a ganar la reserva para estas
    personas. Las pruebas que SÍ ejercitan el saludo (`tests/test_saludo.py`)
    manejan su propia fila de `greeting_state`, sin pasar por acá."""
    cur.execute(
        """insert into greeting_state (membership_id, workspace_id, ultima_fecha_local)
             select id, workspace_id, date '9999-12-31' from membership
              where workspace_id = %s
           on conflict (membership_id) do nothing""",
        (workspace_id,))


def _aplicar_esquema(url: str) -> None:
    import psycopg

    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute(ESQUEMA.read_text("utf-8"))


def _con_base_efimera(mantenimiento: str) -> Iterator[str]:
    """Crea una base descartable en un servidor que ya está corriendo."""
    import psycopg
    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    from psycopg.sql import SQL, Identifier, Literal

    nombre = f"leda_test_{uuid.uuid4().hex[:12]}"

    with psycopg.connect(mantenimiento, autocommit=True) as conn:
        conn.execute(SQL("create database {}").format(Identifier(nombre)))

    url = make_conninfo(**{**conninfo_to_dict(mantenimiento), "dbname": nombre})
    try:
        _aplicar_esquema(url)
        yield _SensitiveUrl(url)
    finally:
        with psycopg.connect(mantenimiento, autocommit=True) as conn:
            conn.execute(
                SQL("drop database if exists {} with (force)").format(
                    Identifier(nombre)))


def _servidor_efimero(datos: pathlib.Path) -> str:
    """Levanta un PostgreSQL propio para la sesión de pruebas."""
    import pgserver

    servidor = pgserver.get_server(datos)
    url = servidor.get_uri()
    _aplicar_esquema(url)
    return _SensitiveUrl(url)


@pytest.fixture(scope="session")
def uri(tmp_path_factory) -> Iterator[str]:
    mantenimiento = os.environ.get("LEDA_TEST_DB_URL")
    if mantenimiento:
        yield from _con_base_efimera(mantenimiento)
        return

    try:
        import pgserver  # noqa: F401
    except ImportError:
        pytest.skip(
            "Hace falta un PostgreSQL para las pruebas: instalá el extra dev "
            "(trae pgserver, que no corre en Windows) o poné LEDA_TEST_DB_URL "
            "en .env.test apuntando a un servidor propio.",
            allow_module_level=True)

    yield _servidor_efimero(tmp_path_factory.mktemp("pgdata"))


@pytest.fixture(autouse=True)
def _sin_fallidos_de_huerfanos_de_otra_prueba():
    """`huerfanos._FALLIDOS` (la deduplicación en memoria del reporte de un aviso
    fallido) vive por proceso: una prueba no hereda las marcas de otra (T9-H19h)."""
    from leda import huerfanos

    huerfanos._FALLIDOS.clear()
    yield
    huerfanos._FALLIDOS.clear()


@pytest.fixture
def conn(uri):
    from leda.db import conectar

    c = conectar(uri)
    yield c
    with c.cursor() as cur:
        cur.execute("set role leda_admin")
        cur.execute("""
            truncate task_intake_free_text_slot, task_intake_field,
                     task_intake_choice, task_intake_choice_set,
                     task_intake_request,
                     task_state_event, objective_state_event, task, task_draft,
                     task_evidence_policy, objective,
                     message_outbox, inbound_message, pending_reply, blocker,
                     evidence, approval, dependency, absence,
                     membership, area, rol, approval_policy, approval_requirement,
                     escalation_route, cadence_job, glossary_term, holiday,
                     work_calendar, persona_config, workspace_setting,
                     workspace_version, workspace, app_user, platform_role,
                     audit_log, incident, admin_notice
            restart identity cascade""")
    c.commit()
    c.close()


@pytest.fixture(scope="session")
def authority_uri(uri) -> Iterator[str]:
    """Ephemeral login with only the task-commitment authority role."""
    import psycopg
    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    from psycopg.sql import SQL, Identifier, Literal

    role = f"leda_gateway_test_{uuid.uuid4().hex[:12]}"
    password = secrets.token_urlsafe(32)
    with psycopg.connect(uri, autocommit=True) as c:
        c.execute(SQL("create role {} login noinherit password {}").format(
            Identifier(role), Literal(password)))
        c.execute(
            SQL("grant leda_gateway to {}").format(Identifier(role)))

    authority_url = make_conninfo(
        **{**conninfo_to_dict(uri), "user": role, "password": password})
    try:
        yield _SensitiveUrl(authority_url)
    finally:
        with psycopg.connect(str(uri), autocommit=True) as c:
            c.execute(
                SQL("drop role if exists {}").format(Identifier(role)))


@pytest.fixture
def authority_conn(authority_uri):
    from leda.db import conectar_autoridad

    c = conectar_autoridad(authority_uri)
    yield c
    c.close()


@pytest.fixture
def corework(conn, tmp_path):
    """CoreWork importado y activo, con los pendientes completados."""
    import yaml
    from leda.importador import importar

    import os

    os.environ["LEDA_BOT_TOKEN_COREWORK"] = "prueba:token"

    pack = yaml.safe_load((RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack["telegram"]["grupo_gestion_id"] = -1001
    for i, p in enumerate(pack["personas"]):
        p["telegram_user_id"] = 9000 + i
    pack["evidencia"]["estructura_drive"] = "drive://corework"

    tmp = tmp_path / "corework.yaml"
    tmp.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    r = importar(conn, tmp, activar=True)
    from leda.db import admin

    with admin(conn) as cur:
        _blindar_contra_saludo(cur, r.workspace_id)
    conn.commit()
    return r


@pytest.fixture
def intake_world(conn):
    """Dos espacios completos e independientes.

    Vive acá y no en un archivo de pruebas porque la usan varios: mover
    una fixture compartida a conftest es cómo pytest la resuelve sola.
    """
    from leda.db import admin

    workspaces: dict[str, dict] = {}
    with admin(conn) as cur:
        for index, (slug, label, tz) in enumerate((
            ("north-lab", "North Lab", "America/Argentina/Buenos_Aires"),
            ("west-studio", "West Studio", "Europe/Madrid"),
        )):
            cur.execute(
                """insert into workspace (slug, nombre, zona_horaria, activo)
                   values (%s, %s, %s, true) returning id""",
                (slug, label, tz),
            )
            ws = str(cur.fetchone()["id"])
            cur.execute(
                """insert into work_calendar
                     (workspace_id, dias, hora_inicio, hora_fin)
                   values (%s, array['lunes','martes','miercoles','jueves','viernes'],
                           '08:00', '18:00')""",
                (ws,),
            )
            cur.execute(
                "insert into persona_config (workspace_id) values (%s)", (ws,)
            )
            cur.execute(
                """insert into workspace_version (workspace_id, version, pack_hash)
                   values (%s, 1, %s)""",
                (ws, f"hash-{index}"),
            )

            areas = {}
            for area_slug, area_name in (("field", "Field Services"),
                                         ("quality", "Quality Guild")):
                cur.execute(
                    """insert into area (workspace_id, slug, nombre)
                       values (%s, %s, %s) returning id""",
                    (ws, area_slug, area_name),
                )
                areas[area_slug] = str(cur.fetchone()["id"])

            roles = {}
            for role_slug, role_name, final in (
                ("director", "Director", True),
                ("lead", "Lead", False),
                ("member", "Member", False),
            ):
                cur.execute(
                    """insert into rol
                         (workspace_id, slug, nombre, autoridad_final)
                       values (%s, %s, %s, %s) returning id""",
                    (ws, role_slug, role_name, final),
                )
                roles[role_slug] = str(cur.fetchone()["id"])

            people = {}
            seed = index * 100
            for offset, name in enumerate(("Morgan Hale", "Taylor Quinn",
                                           "Sam North", "Sam Noble")):
                cur.execute(
                    """insert into app_user (telegram_user_id, nombre)
                       values (%s, %s) returning id""",
                    (71000 + seed + offset, f"{name} {index + 1}"),
                )
                people[name] = {
                    "app_user_id": str(cur.fetchone()["id"]),
                    "telegram": 71000 + seed + offset,
                    "name": f"{name} {index + 1}",
                }

            def membership(person, area, role, approver=None):
                cur.execute(
                    """insert into membership
                         (workspace_id, app_user_id, area_id, rol_id,
                          aprobador_membership_id)
                       values (%s, %s, %s, %s, %s) returning id""",
                    (ws, people[person]["app_user_id"], areas[area], roles[role],
                     approver),
                )
                people[person]["membership_id"] = str(cur.fetchone()["id"])

            membership("Morgan Hale", "field", "director")
            membership("Taylor Quinn", "field", "lead",
                       people["Morgan Hale"]["membership_id"])
            membership("Sam North", "field", "member",
                       people["Taylor Quinn"]["membership_id"])
            membership("Sam Noble", "quality", "member",
                       people["Taylor Quinn"]["membership_id"])

            for area_id in areas.values():
                cur.execute(
                    """insert into task_evidence_policy
                         (workspace_id, area_id, evidencia_requerida, version)
                       values (%s, %s, array['test record'], 1)""",
                    (ws, area_id),
                )

            objectives = []
            for title in ("Reduce service delay", "Raise delivery quality",
                          "Expand regional coverage"):
                cur.execute(
                    """insert into objective (workspace_id, tipo, titulo, estado)
                       values (%s, 'operativo', %s, 'activo') returning id""",
                    (ws, f"{title} {index + 1}"),
                )
                objectives.append(str(cur.fetchone()["id"]))
            _blindar_contra_saludo(cur, ws)
            workspaces[slug] = {
                "id": ws, "areas": areas, "people": people,
                "objectives": objectives,
            }
    conn.commit()
    return workspaces

