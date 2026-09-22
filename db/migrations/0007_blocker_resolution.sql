\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0006_dashboard_access.sql. Adds the narrow read that
-- `resolver_bloqueo` needs: what state a task had right before it last
-- entered `bloqueada`.
--
-- `task_state_event` is append-only and `prisma_app` has no `select` on it
-- (see 0003/the base schema, "los eventos de estado son append-only y
-- prisma_app no los lee"). Without this function, closing the last open
-- blocker of a task has no way to know which state to return it to without
-- guessing `asignada`, which mecánica §3 explicitly forbids.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0007 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'prisma_owner') then
    raise exception '0007 requires 0004_function_ownership.sql';
  end if;
end $$;

-- Filtra por `estado_nuevo = 'bloqueada'` a propósito: no alcanza con "el
-- último evento de la tarea". `actualizar_estado` no exige bloqueos cerrados
-- para salir de `bloqueada` (deuda conocida, no hay todavía un disparador que
-- valide transiciones), así que el último evento puede ser una salida hacia
-- otro estado con el bloqueo todavía abierto. Lo que hace falta acá es el
-- `estado_anterior` de la última vez que la tarea ENTRÓ a `bloqueada`, no el
-- de cualquier evento posterior. Quien llama sigue teniendo que comprobar
-- que la tarea esté bloqueada *ahora* antes de usar este valor.
create or replace function estado_previo_a_bloqueo(p_task uuid)
returns estado_tarea
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare previo estado_tarea;
begin
  select estado_anterior into previo
    from task_state_event
   where task_id = p_task and estado_nuevo = 'bloqueada'
   order by at desc
   limit 1;
  return previo;
end $$;

alter function estado_previo_a_bloqueo(uuid)
  owner to prisma_owner;

revoke execute on function estado_previo_a_bloqueo(uuid) from public;
grant execute on function estado_previo_a_bloqueo(uuid) to prisma_app;

commit;
