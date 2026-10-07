# Incremental migrations

Files in this directory are applied directly from disk in lexical order with
`psql -f` and `ON_ERROR_STOP=1`. Set `PGCLIENTENCODING=UTF8` in the invoking
process; in PowerShell, use `$env:PGCLIENTENCODING = "UTF8"`. Never pass a
migration through `Get-Content`, `type`, or another text pipeline: that adds an
uncontrolled decode/encode step before PostgreSQL. They are for existing
databases; `db/esquema.sql` remains the source for clean test databases.

Before applying a migration:

1. Take and verify a backup.
2. Stop application writers and dispatchers.
3. Run the migration against a restored disposable copy first.
4. Run the preflight section separately if the migration documents one.
5. Apply once as the schema owner inside a maintenance window.

Migration `0002_general_task_intake.sql` also pins the `psql` encoding and
aborts transactionally before DDL if its UTF-8 sentinel was decoded incorrectly.

Never use `python -m leda esquema --recrear` on an operational database.

## Reserved numbers

Numbers `0026` to `0029` belong to the frozen branch `feat/flujo-de-un-mensaje` (tag
`respaldo-flujos-antes-de-d`) and are not present here. New migrations on this branch start at
`0030`, so a number never means two different things.

## Dropping the guided task intake (0032)

`0032_borrar_el_alta_guiada.sql` drops the five `task_intake_*` tables that `0002` created,
`message_outbox.intake_choice_set_id`, and the intake updates inside
`confirmar_borrador_tarea()`: tasks are not created by chat (ADR 0017). Drafts, frozen
previews and the confirmed conversion stay. It refuses to run while `task_intake_request`
has rows: back them up (`pg_dump`) and delete them first. Its rollback recreates the tables
empty. Because `0002`'s own rollback needs those tables, roll back `0032` before `0002`.
