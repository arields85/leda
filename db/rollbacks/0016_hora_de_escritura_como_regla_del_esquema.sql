\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0016_hora_de_escritura_como_regla_del_esquema.sql.
--
-- Restores the three column defaults to `now()`, exactly what `db/esquema.sql`
-- carried before this migration. No function, trigger, or privilege to
-- undo: the migration touched no ACL or ownership, only the three defaults.
begin;
set search_path = prisma, public;

alter table task_state_event alter column at set default now();
alter table evidence alter column at set default now();
alter table approval alter column at set default now();

commit;
