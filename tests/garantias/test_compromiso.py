"""El compromiso de una tarea: sólo la función autorizada la crea, con actor y reloj de la
base y la vista previa congelada; la aplicación no puede insertarla ni mutarla, y el login
de autoridad es exclusivo.

Movidas desde `tests/test_task_commitment_schema.py` y `tests/test_task_drafts.py` (E3-1).
"""

from __future__ import annotations

from pathlib import Path

import psycopg
import pytest

from leda.db import admin, autoridad, espacio


ROOT = Path(__file__).resolve().parents[2]


def _objetivo(cur, ws):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo, estado)
           values (%s, 'operativo', 'Objetivo simulado', 'activo') returning id""",
        (ws,))
    return str(cur.fetchone()["id"])


def test_migration_constraint_checks_are_scoped_to_relation():
    migration = (ROOT / "db" / "migrations" /
                 "0001_task_commitment.sql").read_text("utf-8")
    assert "conrelid = 'task_draft'::regclass" in migration
    assert "conrelid = 'pending_action'::regclass" in migration


def test_clean_schema_and_migrations_expose_only_trusted_commit_signatures():
    schema = (ROOT / "db" / "esquema.sql").read_text("utf-8")
    migration_1 = (ROOT / "db" / "migrations" /
                   "0001_task_commitment.sql").read_text("utf-8")
    migration_2 = (ROOT / "db" / "migrations" /
                   "0002_general_task_intake.sql").read_text("utf-8")
    unit_1a_signature = "confirmar_borrador_tarea(uuid, text, bigint)"
    intake_signature = "confirmar_borrador_tarea(uuid, text, bigint, bigint)"
    old_signature = "confirmar_borrador_tarea(text, uuid, timestamptz)"
    assert intake_signature in schema and intake_signature in migration_2
    assert unit_1a_signature in migration_1
    assert f"drop function {unit_1a_signature}" in migration_2
    assert old_signature not in schema
    assert f"drop function if exists {old_signature}" in migration_1


def test_app_cannot_mutate_tasks_or_execute_commit_function():
    schema = (ROOT / "db" / "esquema.sql").read_text("utf-8")
    migration_1 = (ROOT / "db" / "migrations" /
                   "0001_task_commitment.sql").read_text("utf-8")
    migration_2 = (ROOT / "db" / "migrations" /
                   "0002_general_task_intake.sql").read_text("utf-8")
    for sql in (schema, migration_1):
        assert "revoke update, delete on task from leda_app" in sql
        assert "to leda_gateway" in sql
        assert ("grant execute on function "
                 "confirmar_borrador_tarea(uuid, text, bigint)\n  to leda_app") \
            not in sql
    assert "revoke execute on function confirmar_borrador_tarea" in migration_2


def test_commit_function_uses_database_time_and_frozen_preview():
    schema = (ROOT / "db" / "esquema.sql").read_text("utf-8")
    assert "ahora timestamptz := clock_timestamp()" in schema
    assert "a.preview is distinct from preview_actual" in schema
    assert "p_telegram_user_id bigint" in schema
    assert "language plpgsql security definer" in schema
    assert "create role leda_gateway nologin noinherit;" in schema
    assert "alter role leda_gateway noinherit nobypassrls" in schema


def test_ruta_directa_de_aplicacion_no_puede_insertar_tareas(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        objetivo = _objetivo(cur, ws)
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute(
                """insert into task
                     (workspace_id, objective_id, titulo, area_id,
                      responsable_membership_id, fecha_objetivo,
                      criterio_aceptacion, evidencia_requerida)
                   values (%s, %s, 'atajo',
                     (select id from area where slug = 'ot'),
                     (select membership_id from integrante where nombre = 'Nahuel Gimenez'),
                     '2026-08-20', 'criterio', array['explicacion'])""",
                (ws, objetivo))


def test_login_autoridad_es_exclusivo_y_no_administra_tablas(
        corework, conn, authority_conn):
    with authority_conn.cursor() as cur:
        cur.execute("select session_user as login")
        login = cur.fetchone()["login"]

    with admin(conn) as cur:
        cur.execute(
            """select array_agg(parent.rolname order by parent.rolname) as roles
                 from pg_auth_members am
                 join pg_roles parent on parent.oid = am.roleid
                 join pg_roles member on member.oid = am.member
                where member.rolname = %s""", (login,))
        assert cur.fetchone()["roles"] == ["leda_gateway"]

    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        with authority_conn.transaction():
            authority_conn.execute("select count(*) from leda.task")

    with autoridad(authority_conn) as cur:
        cur.execute(
            """select has_function_privilege(
                 current_user,
                 'leda.confirmar_borrador_tarea(uuid,text,bigint,bigint)',
                 'EXECUTE') as puede,
               has_table_privilege(current_user, 'leda.task', 'SELECT')
                 as lee_task""")
        permisos = cur.fetchone()
        assert permisos == {"puede": True, "lee_task": False}
