\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0008_task_start_gate.sql.
--
-- Drops the trigger before the functions it depends on, and both functions
-- entirely: `exigir_dependencias_resueltas()` (the trigger function itself)
-- and `motivo_no_arranca_tarea(uuid)` (the check it calls). After this, a
-- task can move to `en_curso` again with an unresolved `bloqueante`
-- dependency -- the same gap this migration exists to close, which is the
-- safe direction for a rollback: no half-applied trigger left pointing at a
-- dropped function.
--
-- `exigir_dependencias_resueltas()` was missing from this rollback until
-- ADR 0009 (migración 0012) widened `tests/test_task_intake.py::
-- _retrato_de_funciones` to compare every function in the schema, not only
-- `security definer` ones -- this trigger function isn't one, so the
-- narrower check never saw that the rollback left it behind. Found and
-- fixed incidentally while verifying 0012's own round-trip, unrelated to
-- ADR 0009's behavior.
begin;
set search_path = leda, public;

drop trigger if exists trg_exigir_dependencias_resueltas on task_state_event;
drop function if exists exigir_dependencias_resueltas();
drop function if exists motivo_no_arranca_tarea(uuid);

commit;
