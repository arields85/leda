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

Never use `python -m prisma esquema --recrear` on an operational database.
