\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0017_aviso_incidente_administracion.sql.
--
-- Drops the function first (it owns no data), then the table it wrote to,
-- then the column it read from `incident`. Nothing else references any of
-- these -- no view, no other function, no trigger -- so plain drops are
-- enough, same as 0011's rollback.
begin;
set search_path = leda, public;

drop function if exists avisar_incidente_admin(uuid, uuid, text);
drop table if exists admin_notice;
alter table incident drop column if exists notificado_admin_en;

commit;
