\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0005_auxiliary_record_isolation.sql.
--
-- Leaves the auxiliary records writable across workspaces again, which is the
-- state 0005 found them in. Run this only to recover from a failed migration,
-- never as a resting state: it restores cross-tenant audit forgery.
begin;
set search_path = leda, public;

drop policy if exists aislamiento_espacio on incident;
alter table incident no force row level security;
alter table incident disable row level security;

drop policy if exists aislamiento_espacio on audit_log;
alter table audit_log no force row level security;
alter table audit_log disable row level security;

drop policy if exists aislamiento_espacio on absence;
alter table absence no force row level security;
alter table absence disable row level security;

drop trigger if exists trg_derivar_espacio_incidente on incident;
drop trigger if exists trg_derivar_espacio_auditoria on audit_log;
drop trigger if exists trg_derivar_espacio_ausencia on absence;
drop function if exists derivar_espacio_registro();
drop function if exists derivar_espacio_ausencia();

drop index if exists absence_ws;
alter table absence drop column if exists workspace_id;

commit;
