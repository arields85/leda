\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0008_task_start_gate.sql.
--
-- Drops the trigger before the function it calls, and the function entirely.
-- After this, a task can move to `en_curso` again with an unresolved
-- `bloqueante` dependency -- the same gap this migration exists to close,
-- which is the safe direction for a rollback: no half-applied trigger left
-- pointing at a dropped function.
begin;
set search_path = prisma, public;

drop trigger if exists trg_exigir_dependencias_resueltas on task_state_event;
drop function if exists motivo_no_arranca_tarea(uuid);

commit;
