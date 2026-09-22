\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0006_dashboard_access.sql.
--
-- Removes the dashboard credential entirely. Any link already handed out stops
-- working, which is the safe direction for a rollback of an access mechanism.
begin;
set search_path = prisma, public;

drop function if exists resolver_acceso_tablero(text);
drop function if exists emitir_acceso_tablero(uuid, text, timestamptz);

drop index if exists acceso_tablero_vencimiento;
drop table if exists acceso_tablero;

commit;
