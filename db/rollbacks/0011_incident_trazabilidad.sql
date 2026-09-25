\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0011_incident_trazabilidad.sql.
--
-- Drops the five traceability columns it added to `incident`. Nothing else
-- references them (no trigger, no view, no function), so plain drops are
-- enough -- unlike 0010's rollback, there is no function body to restore
-- first.
begin;
set search_path = prisma, public;

alter table incident drop column if exists app_user_id;
alter table incident drop column if exists chat_id;
alter table incident drop column if exists referencia_id;
alter table incident drop column if exists referencia_tipo;
alter table incident drop column if exists etapa;

commit;
