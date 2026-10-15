\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0078_la_matriz_de_privilegios_converge.sql. El grafo de transiciones de estado,
-- parte 1: sólo lo que dice explícitamente la mecánica (`nucleo/mecanica-pm.md` §3; riesgo 3 de
-- `docs/STATUS.md`). Hasta acá nada miraba el par de estados de un evento ni que su
-- `estado_anterior` fuera el estado vigente.
--
-- - `exigir_transicion_valida_tarea` y `exigir_transicion_valida_objetivo`, disparadores
--   `before insert` `security definer` de `leda_owner` (con `search_path` fijado y sin `execute`
--   para `public`) sobre `task_state_event` y `objective_state_event`: el evento sale del estado
--   vigente (la fila tomada `for update`; sin `estado_anterior` sólo el que la crea, cuando no
--   tiene ningún evento), `cancelada` y `cancelado` son terminales, y una tarea sale de
--   `bloqueada` al estado que tenía antes (`estado_previo_a_bloqueo`) o a `cancelada`.
--
-- No decide quién cancela, ni otros saltos, ni la máquina de estados de un objetivo: esperan al
-- usuario. Sólo mira los eventos nuevos; los ya registrados no cambian. Se deshace con
-- `db/rollbacks/0079_el_grafo_de_transiciones.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0079 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0077 está aplicada y la 0079 no.
do $$ begin
  if to_regclass('leda.cambio_de_fecha') is null then
    raise exception '0079 preflight failed: falta la 0077';
  end if;
  if to_regprocedure('leda.exigir_transicion_valida_tarea()') is not null then
    raise exception '0079 preflight failed: ya está aplicada';
  end if;
end $$;

-- --- El grafo de transiciones, parte 1: lo que dice la mecánica (migración 0079) ---
-- Mecánica §3, sólo lo explícito; el resto del grafo (quién cancela, qué otros saltos valen, la
-- máquina de estados de un objetivo) espera decisiones del usuario
-- (`odd/tasks/plataforma-jerarquias.md`, "Grafo de transiciones"):
--
-- 1. un evento sale del estado vigente: su `estado_anterior` es el `estado` de la fila ahora, con
--    la fila tomada `for update` para que dos actos pensados sobre el mismo estado no se apliquen
--    los dos. Sólo el evento que la crea (sin `estado_anterior`) puede no decirlo, y sólo si la
--    fila todavía no tiene ningún evento;
-- 2. `cancelada` y `cancelado` son terminales: ningún evento sale de ellos;
-- 3. salir de `bloqueada` devuelve la tarea al estado que tenía antes de bloquearse
--    (`estado_previo_a_bloqueo`), o la cancela. Con varios bloqueos, `resolver_bloqueo` sólo la
--    saca de `bloqueada` con el último, y siempre al estado previo: la misma regla.
--
-- `security definer`, de `leda_owner`, por lo mismo que `aplicar_evento_tarea`: `leda_app` no lee
-- `task_state_event` ni puede tomar `task` `for update`, y la conexión administrativa no fija
-- espacio. Se acota al espacio del propio evento, que el disparador de derivación ya resolvió
-- desde la fila padre (una tarea de otro espacio falla antes, igual que un id inventado), y se
-- restaura el espacio previo. Los nombres de los disparadores los ponen después de la derivación
-- y antes de los `trg_exigir_*`.
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

create trigger trg_encadenar_estado_tarea
  before insert on task_state_event
  for each row execute function exigir_transicion_valida_tarea();

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

create trigger trg_encadenar_estado_objetivo
  before insert on objective_state_event
  for each row execute function exigir_transicion_valida_objetivo();

alter function exigir_transicion_valida_tarea() owner to leda_owner;
alter function exigir_transicion_valida_objetivo() owner to leda_owner;
revoke execute on function exigir_transicion_valida_tarea() from public;
revoke execute on function exigir_transicion_valida_objetivo() from public;

commit;
