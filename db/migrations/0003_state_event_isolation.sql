\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0002_general_task_intake.sql. Closes cross-tenant writes on the
-- two append-only state-event tables. They carried no workspace_id and no
-- isolation policy while still granting insert to prisma_app, so a connection
-- bound to one workspace could insert an event against another workspace's task
-- and move its state. The foreign key confirmed the identifier existed, which
-- also made the tables an enumeration oracle.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0003 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('prisma.task_intake_request') is null then
    raise exception '0003 requires 0002_general_task_intake.sql';
  end if;
end $$;

-- Preflight before any DDL. The workspace of an event is derived from its
-- parent row, so an event without one could not be backfilled and would block
-- the not-null constraint halfway through.
do $$
declare huerfanos_tarea bigint;
declare huerfanos_objetivo bigint;
begin
  select count(*) into huerfanos_tarea
    from task_state_event e
    left join task t on t.id = e.task_id
   where t.id is null;
  select count(*) into huerfanos_objetivo
    from objective_state_event e
    left join objective o on o.id = e.objective_id
   where o.id is null;
  if huerfanos_tarea > 0 or huerfanos_objetivo > 0 then
    raise exception
      '0003 preflight failed: % task state event(s) and % objective state event(s) have no parent row. Inventory and reconcile them before migration.',
      huerfanos_tarea, huerfanos_objetivo;
  end if;
end $$;

lock table task_state_event, objective_state_event in access exclusive mode;

-- --- El espacio pasa a ser explícito en cada evento -----------------------

alter table task_state_event
  add column if not exists workspace_id uuid references workspace(id)
    on delete cascade;
update task_state_event e
   set workspace_id = t.workspace_id
  from task t
 where t.id = e.task_id and e.workspace_id is distinct from t.workspace_id;
alter table task_state_event alter column workspace_id set not null;

create index if not exists task_state_event_ws
  on task_state_event (workspace_id, at desc);

alter table objective_state_event
  add column if not exists workspace_id uuid references workspace(id)
    on delete cascade;
update objective_state_event e
   set workspace_id = o.workspace_id
  from objective o
 where o.id = e.objective_id and e.workspace_id is distinct from o.workspace_id;
alter table objective_state_event alter column workspace_id set not null;

create index if not exists objective_state_event_ws
  on objective_state_event (workspace_id, at desc);

-- --- El espacio se deriva del padre; nunca se confía a quien llama --------

-- Estas dos funciones NO son security definer, y eso es deliberado. Corren con
-- los privilegios de quien llama, así que la RLS de la tabla padre esconde una
-- fila de otro espacio: el select no la encuentra y el insert falla.
--
-- De ahí que el mensaje sea neutro y no nombre el identificador. Uno que dijera
-- "permiso insuficiente", o que distinguiera entre ajena e inexistente, sería
-- en sí mismo un oráculo: confirmaría que esa fila existe pero pertenece a otro
-- cliente. Un identificador ajeno tiene que fallar idéntico a uno inventado.
create or replace function derivar_espacio_evento_tarea() returns trigger as $$
begin
  select t.workspace_id into new.workspace_id
    from task t where t.id = new.task_id;
  if new.workspace_id is null then
    raise exception 'task_state_event: la tarea referida no existe';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_derivar_espacio_evento_tarea
  before insert on task_state_event
  for each row execute function derivar_espacio_evento_tarea();

create or replace function derivar_espacio_evento_objetivo() returns trigger as $$
begin
  select o.workspace_id into new.workspace_id
    from objective o where o.id = new.objective_id;
  if new.workspace_id is null then
    raise exception 'objective_state_event: el objetivo referido no existe';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_derivar_espacio_evento_objetivo
  before insert on objective_state_event
  for each row execute function derivar_espacio_evento_objetivo();

-- --- Aislamiento por espacio ----------------------------------------------

-- Misma política que el resto del esquema. Sin with check explícito, la
-- expresión using también gobierna las filas nuevas.
alter table task_state_event enable row level security;
alter table task_state_event force row level security;
create policy aislamiento_espacio on task_state_event
  using (workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid);

alter table objective_state_event enable row level security;
alter table objective_state_event force row level security;
create policy aislamiento_espacio on objective_state_event
  using (workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid);

-- Los privilegios de prisma_app no cambian: estas tablas son append-only y ya
-- tenía insert y nada más. La política es lo único que se agrega.

commit;
