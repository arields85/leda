from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_migration_constraint_checks_are_scoped_to_relation():
    migration = (ROOT / "db" / "migrations" /
                 "0001_task_commitment.sql").read_text("utf-8")
    assert "conrelid = 'task_draft'::regclass" in migration
    assert "conrelid = 'pending_action'::regclass" in migration


def test_clean_schema_and_migration_expose_only_trusted_commit_signature():
    schema = (ROOT / "db" / "esquema.sql").read_text("utf-8")
    migration = (ROOT / "db" / "migrations" /
                 "0001_task_commitment.sql").read_text("utf-8")
    signature = "confirmar_borrador_tarea(uuid, text, bigint)"
    old_signature = "confirmar_borrador_tarea(text, uuid, timestamptz)"
    assert signature in schema and signature in migration
    assert old_signature not in schema
    assert f"drop function if exists {old_signature}" in migration


def test_app_cannot_mutate_tasks_or_execute_commit_function():
    schema = (ROOT / "db" / "esquema.sql").read_text("utf-8")
    migration = (ROOT / "db" / "migrations" /
                 "0001_task_commitment.sql").read_text("utf-8")
    for sql in (schema, migration):
        assert "revoke update, delete on task from prisma_app" in sql
        assert "to prisma_gateway" in sql
        assert ("grant execute on function "
                "confirmar_borrador_tarea(uuid, text, bigint)\n  to prisma_app") \
            not in sql


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
    assert callback_body.index("with espacio(conn, workspace_id)") < \
        callback_body.index("conn.commit()")
