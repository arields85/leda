\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0080_el_grafo_en_una_sola_sentencia.sql: los disparadores del grafo y
-- `estado_previo_a_bloqueo` vuelven a como los dejó la 0079 (comparan contra el estado proyectado
-- y ordenan por la hora), y se borran el número de cada evento y sus índices.
begin;
set search_path = leda, public;

create or replace function estado_previo_a_bloqueo(p_task uuid)
returns estado_tarea
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo estado_tarea;
begin
  select estado_anterior into previo
    from task_state_event
   where task_id = p_task and estado_nuevo = 'bloqueada'
   order by at desc
   limit 1;
  return previo;
end $$;

create or replace function exigir_transicion_valida_tarea() returns trigger
security definer set search_path = leda, public, pg_temp as $$
declare
  espacio_anterior text := current_setting('leda.workspace_id', true);
  v_actual estado_tarea;
  v_con_historia boolean;
  v_previo estado_tarea;
begin
  perform set_config('leda.workspace_id', new.workspace_id::text, true);
  select t.estado into v_actual from task t where t.id = new.task_id for update;
  select exists (select 1 from task_state_event e where e.task_id = new.task_id)
    into v_con_historia;
  if new.estado_anterior is null then
    if v_con_historia then
      raise exception 'transicion_invalida: la tarea ya tiene estados registrados; el evento tiene que decir de cuál sale (está en %)',
        v_actual;
    end if;
  else
    if new.estado_anterior is distinct from v_actual then
      raise exception 'transicion_invalida: el evento sale de % pero la tarea está en %',
        new.estado_anterior, v_actual;
    end if;
    if new.estado_anterior = 'cancelada' and new.estado_nuevo <> 'cancelada' then
      raise exception 'transicion_invalida: una tarea cancelada no cambia de estado';
    end if;
    if new.estado_anterior = 'bloqueada'
       and new.estado_nuevo not in ('bloqueada', 'cancelada') then
      v_previo := estado_previo_a_bloqueo(new.task_id);
      if v_previo is null or new.estado_nuevo <> v_previo then
        raise exception 'transicion_invalida: una tarea bloqueada vuelve al estado que tenía antes (%) o se cancela, no pasa a %',
          coalesce(v_previo::text, 'sin registrar'), new.estado_nuevo;
      end if;
    end if;
  end if;
  perform set_config('leda.workspace_id', coalesce(espacio_anterior, ''), true);
  return new;
end $$ language plpgsql;

create or replace function exigir_transicion_valida_objetivo() returns trigger
security definer set search_path = leda, public, pg_temp as $$
declare
  espacio_anterior text := current_setting('leda.workspace_id', true);
  v_actual estado_objetivo;
  v_con_historia boolean;
begin
  perform set_config('leda.workspace_id', new.workspace_id::text, true);
  select o.estado into v_actual from objective o where o.id = new.objective_id for update;
  select exists (select 1 from objective_state_event e where e.objective_id = new.objective_id)
    into v_con_historia;
  if new.estado_anterior is null then
    if v_con_historia then
      raise exception 'transicion_invalida: el objetivo ya tiene estados registrados; el evento tiene que decir de cuál sale (está en %)',
        v_actual;
    end if;
  else
    if new.estado_anterior is distinct from v_actual then
      raise exception 'transicion_invalida: el evento sale de % pero el objetivo está en %',
        new.estado_anterior, v_actual;
    end if;
    if new.estado_anterior = 'cancelado' and new.estado_nuevo <> 'cancelado' then
      raise exception 'transicion_invalida: un objetivo cancelado no cambia de estado';
    end if;
  end if;
  perform set_config('leda.workspace_id', coalesce(espacio_anterior, ''), true);
  return new;
end $$ language plpgsql;

drop index if exists task_state_event_numero;
drop index if exists objective_state_event_numero;
alter table task_state_event drop column if exists numero;
alter table objective_state_event drop column if exists numero;

commit;
