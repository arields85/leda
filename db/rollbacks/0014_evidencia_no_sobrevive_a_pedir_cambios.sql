\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0014_evidencia_no_sobrevive_a_pedir_cambios.sql.
--
-- Restores `evidencia_pendiente` to its pre-0014 body -- byte-for-byte the
-- version 0012 left (the one that counts any `evidence` row for the task,
-- with no check against a later 'rechazado') -- never dropping the
-- function, since `motivo_no_cierra_tarea` and other functions still call
-- it.
begin;
set search_path = leda, public;

create or replace function evidencia_pendiente(p_task uuid)
returns boolean as $$
  select array_length(t.evidencia_requerida, 1) is not null
     and not exists (select 1 from evidence where task_id = t.id)
    from task t where t.id = p_task;
$$ language sql stable;

commit;
