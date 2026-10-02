\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0007_blocker_resolution.sql.
--
-- Drops the function entirely. After this, `resolver_bloqueo` fails with
-- "function does not exist" again -- the same failure this migration exists
-- to close -- which is the safe direction for a rollback: no half-applied
-- function left behind with the wrong owner or privileges.
begin;
set search_path = leda, public;

drop function if exists estado_previo_a_bloqueo(uuid);

commit;
