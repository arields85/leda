from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
        assert "revoke update, delete on task from prisma_app" in sql
        assert "to prisma_gateway" in sql
        assert ("grant execute on function "
                 "confirmar_borrador_tarea(uuid, text, bigint)\n  to prisma_app") \
            not in sql
    assert "revoke execute on function confirmar_borrador_tarea" in migration_2


def test_commit_function_uses_database_time_and_frozen_preview():
    schema = (ROOT / "db" / "esquema.sql").read_text("utf-8")
    assert "ahora timestamptz := clock_timestamp()" in schema
    assert "a.preview is distinct from preview_actual" in schema
    assert "p_telegram_user_id bigint" in schema
    assert "language plpgsql security definer" in schema
    assert "create role prisma_gateway nologin noinherit;" in schema
    assert "alter role prisma_gateway noinherit nobypassrls" in schema


def test_dispatch_and_gateway_contain_stale_preview_and_callback_guards():
    dispatch = (ROOT / "src" / "prisma" / "despachador.py").read_text("utf-8")
    gateway = (ROOT / "src" / "prisma" / "gateway.py").read_text("utf-8")
    assert "def _preview_vigente" in dispatch
    assert "clock_timestamp()" in dispatch
    assert "update message_outbox set estado = 'descartado'" in dispatch
    draft_callback = gateway.split("def _resolver_toque_borrador", 1)[1]
    assert "with espacio(conn, workspace_id)" in draft_callback
    callback_body = draft_callback.split("def _responder", 1)[0]
    assert "The Unit 1A authority function persisted the terminal visible outbox" \
        in callback_body
    assert "if resuelta is not None" in callback_body
