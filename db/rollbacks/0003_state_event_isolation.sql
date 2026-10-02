\set ON_ERROR_STOP on

begin;
set search_path = leda, public;
select pg_advisory_xact_lock(hashtextextended('leda:0003_state_event_isolation', 0));

lock table task_state_event, objective_state_event in access exclusive mode;

-- Este rollback no necesita guarda. Todo lo que 0003 agregó es derivado: el
-- workspace_id de un evento sale de su fila padre y se puede reconstruir en
-- cualquier momento. No hay dato propio que se pierda al revertir.
--
-- Lo que sí se pierde es el aislamiento: al quitar la política, leda_app
-- vuelve a poder insertar eventos contra tareas de otro espacio. Revertir esto
-- reabre la escritura cruzada.

drop policy if exists aislamiento_espacio on objective_state_event;
alter table objective_state_event no force row level security;
alter table objective_state_event disable row level security;

drop policy if exists aislamiento_espacio on task_state_event;
alter table task_state_event no force row level security;
alter table task_state_event disable row level security;

drop trigger if exists trg_derivar_espacio_evento_objetivo on objective_state_event;
drop trigger if exists trg_derivar_espacio_evento_tarea on task_state_event;
drop function if exists derivar_espacio_evento_objetivo();
drop function if exists derivar_espacio_evento_tarea();

drop index if exists objective_state_event_ws;
drop index if exists task_state_event_ws;

alter table objective_state_event drop column if exists workspace_id;
alter table task_state_event drop column if exists workspace_id;

-- leda_app conserva exactamente lo que tenía antes de 0003: insert y nada
-- más. No se le devuelve ningún acceso nuevo.

commit;
