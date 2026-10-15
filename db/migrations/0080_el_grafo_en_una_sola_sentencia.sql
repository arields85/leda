\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0079_el_grafo_de_transiciones.sql. El grafo de transiciones, varios eventos en una
-- sola sentencia: la advertencia de la revisión del grafo (`36c6120a`, R3-multirow-chain-bypass).
-- La proyección se aplica al final de cada sentencia, así que en un `insert` de varias filas cada
-- una se comparaba contra el estado de antes de la sentencia, y dos saltos desde el mismo estado
-- pasaban los dos (cancelar y entregar juntos dejaba la tarea fuera de `cancelada`).
--
-- - `task_state_event.numero` y `objective_state_event.numero`: el lugar del evento en la historia
--   de su tarea u objetivo, que pone la base (únicos por tarea y por objetivo). Los eventos de
--   antes de la 0080 quedan sin número.
-- - `exigir_transicion_valida_tarea` y `exigir_transicion_valida_objetivo` comparan contra el
--   último evento numerado, que dentro de la misma sentencia sí se ve, y numeran el nuevo.
-- - `estado_previo_a_bloqueo` ordena por ese número antes que por la hora.
--
-- Se deshace con `db/rollbacks/0080_el_grafo_en_una_sola_sentencia.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0080 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0079 está aplicada y la 0080 no.
do $$ begin
  if to_regprocedure('leda.exigir_transicion_valida_tarea()') is null then
    raise exception '0080 preflight failed: falta la 0079';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'task_state_event'
                and column_name = 'numero') then
    raise exception '0080 preflight failed: ya está aplicada';
  end if;
end $$;

alter table task_state_event add column numero integer;
alter table objective_state_event add column numero integer;
create unique index task_state_event_numero on task_state_event (task_id, numero);
create unique index objective_state_event_numero
  on objective_state_event (objective_id, numero);

create or replace function estado_previo_a_bloqueo(p_task uuid)
returns estado_tarea
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo estado_tarea;
begin
  select estado_anterior into previo
    from task_state_event
   where task_id = p_task and estado_nuevo = 'bloqueada'
   order by numero desc nulls last, at desc
   limit 1;
  return previo;
end $$;

-- --- El grafo de transiciones: varios eventos en una sola sentencia (migración 0080) ---
-- Why: the projection (`aplicar_evento_tarea` / `aplicar_evento_objetivo`) is an AFTER ROW trigger,
-- so `task.estado` / `objective.estado` only change at the END of the inserting statement. Under
-- 0079, every row of a multi-row INSERT was checked against the state from before the statement:
-- two events leaving the same state both passed (e.g. en_curso->cancelada and
-- en_curso->en_revision), and the task left `cancelada`.
--
-- Fix: each event gets a per-task/per-objective sequence number, `numero`, assigned here (any value
-- the caller sends is overwritten) as max(numero) + 1 while the parent row is held `for update`.
-- A VOLATILE function called from a row-level BEFORE trigger sees the rows already inserted by
-- the same command (PostgreSQL, "Visibility of Data Changes"), so the latest numbered event is
-- the real current state, including earlier rows of the same statement. `at` cannot order them:
-- `objective_state_event.at` defaults to `now()` (equal for the whole transaction) and callers
-- may send `at` explicitly; the random uuid `id` and `ctid` carry no order either. Taking the
-- parent row lock BEFORE reading max(numero) serializes concurrent writers of the same task, so
-- numbers follow the real order of events. Events from before 0080 keep `numero` null: when a
-- task has no numbered event, its projected `estado` is still the current state (every earlier
-- statement already applied its events). A valid chain in one statement (asignada->en_curso,
-- en_curso->en_revision) passes, and the AFTER triggers project it in row order.
create or replace function exigir_transicion_valida_tarea() returns trigger
security definer set search_path = leda, public, pg_temp as $$
declare
  espacio_anterior text := current_setting('leda.workspace_id', true);
  v_actual estado_tarea;
  v_ultimo integer;
  v_ultimo_estado estado_tarea;
  v_con_historia boolean;
  v_previo estado_tarea;
begin
  perform set_config('leda.workspace_id', new.workspace_id::text, true);
  select t.estado into v_actual from task t where t.id = new.task_id for update;
  select e.numero, e.estado_nuevo into v_ultimo, v_ultimo_estado
    from task_state_event e
   where e.task_id = new.task_id and e.numero is not null
   order by e.numero desc
   limit 1;
  if v_ultimo is not null then
    v_actual := v_ultimo_estado;
  end if;
  new.numero := coalesce(v_ultimo, 0) + 1;
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
  v_ultimo integer;
  v_ultimo_estado estado_objetivo;
  v_con_historia boolean;
begin
  perform set_config('leda.workspace_id', new.workspace_id::text, true);
  select o.estado into v_actual from objective o where o.id = new.objective_id for update;
  select e.numero, e.estado_nuevo into v_ultimo, v_ultimo_estado
    from objective_state_event e
   where e.objective_id = new.objective_id and e.numero is not null
   order by e.numero desc
   limit 1;
  if v_ultimo is not null then
    v_actual := v_ultimo_estado;
  end if;
  new.numero := coalesce(v_ultimo, 0) + 1;
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

commit;
