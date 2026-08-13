"""Base de pruebas: un PostgreSQL real, efímero, con el esquema aplicado.

Las reglas que importan viven en disparadores y funciones de la base, así que
probar contra un doble no serviría de nada.

Hay dos formas de conseguir ese PostgreSQL:

- Por defecto, `pgserver` levanta un servidor descartable dentro de un
  directorio temporal. No hay wheels para Windows.
- Si `PRISMA_TEST_DB_URL` está definida, se usa ese servidor: la sesión crea
  una base con nombre irrepetible, la usa y la borra al terminar. Es una base
  aparte a propósito — las pruebas truncan todo entre casos, y apuntar esto a
  una base con datos reales los perdería.

La variable se puede dejar en `.env.test`, que no se versiona:

    PRISMA_TEST_DB_URL=postgresql://postgres:CONTRASENA@localhost:5432/postgres

Tiene que ser un usuario con permiso para CREATE DATABASE y CREATE ROLE — el
esquema crea `prisma_app` y `prisma_admin`, que son del cluster — y apuntar a
la base de mantenimiento, no a la de la aplicación.
"""

from __future__ import annotations

import os
import pathlib
import secrets
import uuid
from collections.abc import Iterator

import pytest

from prisma.config import _cargar_dotenv

RAIZ = pathlib.Path(__file__).resolve().parents[1]
ESQUEMA = RAIZ / "db" / "esquema.sql"

if os.environ.get("PRISMA_TEST_LOAD_DOTENV", "1") != "0":
    _cargar_dotenv(RAIZ / ".env.test")


class _SensitiveUrl(str):
    def __repr__(self) -> str:
        return "<redacted-db-url>"


def _aplicar_esquema(url: str) -> None:
    import psycopg

    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute(ESQUEMA.read_text("utf-8"))


def _con_base_efimera(mantenimiento: str) -> Iterator[str]:
    """Crea una base descartable en un servidor que ya está corriendo."""
    import psycopg
    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    from psycopg.sql import SQL, Identifier, Literal

    nombre = f"prisma_test_{uuid.uuid4().hex[:12]}"

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
    mantenimiento = os.environ.get("PRISMA_TEST_DB_URL")
    if mantenimiento:
        yield from _con_base_efimera(mantenimiento)
        return

    try:
        import pgserver  # noqa: F401
    except ImportError:
        pytest.skip(
            "Hace falta un PostgreSQL para las pruebas: instalá el extra dev "
            "(trae pgserver, que no corre en Windows) o poné PRISMA_TEST_DB_URL "
            "en .env.test apuntando a un servidor propio.",
            allow_module_level=True)

    yield _servidor_efimero(tmp_path_factory.mktemp("pgdata"))


@pytest.fixture
def conn(uri):
    from prisma.db import conectar

    c = conectar(uri)
    yield c
    with c.cursor() as cur:
        cur.execute("set role prisma_admin")
        cur.execute("""
            truncate task_state_event, objective_state_event, task, task_draft,
                     task_evidence_policy, objective,
                     message_outbox, inbound_message, pending_reply, blocker,
                     evidence, approval, dependency, absence,
                     membership, area, rol, approval_policy, approval_requirement,
                     escalation_route, cadence_job, glossary_term, holiday,
                     work_calendar, persona_config, workspace_setting,
                     workspace_version, workspace, app_user, platform_role,
                     audit_log, incident
            restart identity cascade""")
    c.commit()
    c.close()


@pytest.fixture(scope="session")
def authority_uri(uri) -> Iterator[str]:
    """Ephemeral login with only the task-commitment authority role."""
    import psycopg
    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    from psycopg.sql import SQL, Identifier, Literal

    role = f"prisma_gateway_test_{uuid.uuid4().hex[:12]}"
    password = secrets.token_urlsafe(32)
    with psycopg.connect(uri, autocommit=True) as c:
        c.execute(SQL("create role {} login noinherit password {}").format(
            Identifier(role), Literal(password)))
        c.execute(
            SQL("grant prisma_gateway to {}").format(Identifier(role)))

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
    from prisma.db import conectar_autoridad

    c = conectar_autoridad(authority_uri)
    yield c
    c.close()


@pytest.fixture
def corework(conn, tmp_path):
    """CoreWork importado y activo, con los pendientes completados."""
    import yaml
    from prisma.importador import importar

    import os

    os.environ["PRISMA_BOT_TOKEN_COREWORK"] = "prueba:token"

    pack = yaml.safe_load((RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack["telegram"]["grupo_gestion_id"] = -1001
    for i, p in enumerate(pack["personas"]):
        p["telegram_user_id"] = 9000 + i
    pack["evidencia"]["estructura_drive"] = "drive://corework"

    tmp = tmp_path / "corework.yaml"
    tmp.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    r = importar(conn, tmp, activar=True)
    conn.commit()
    return r
