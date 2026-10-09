\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0042_lo_que_dice_quien_destraba.sql.
--
-- Borra `dicho_de_quien_destraba` (con su disparador y su política) y la restricción única
-- `(workspace_id, id)` de `blocker_unblocker`. Se pierde lo que dijo cada quien destraba: antes
-- de correrlo en una base con datos, `pg_dump` de la tabla.
begin;
set search_path = leda, public;

drop table if exists dicho_de_quien_destraba;

alter table blocker_unblocker drop constraint if exists blocker_unblocker_workspace_id_unique;

commit;
