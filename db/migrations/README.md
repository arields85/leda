# Incremental migrations

Files in this directory are applied in lexical order with `psql` and
`ON_ERROR_STOP=1`. They are for existing databases; `db/esquema.sql` remains
the source for clean test databases.

Before applying a migration:

1. Take and verify a backup.
2. Stop application writers and dispatchers.
3. Run the migration against a restored disposable copy first.
4. Run the preflight section separately if the migration documents one.
5. Apply once as the schema owner inside a maintenance window.

Never use `python -m prisma esquema --recrear` on an operational database.
