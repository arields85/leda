\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0004_function_ownership.sql.
--
-- Ownership of the four elevated functions returns to the role running this
-- script, which is the state 0004 found them in. That state is insecure by
-- design of the original schema: if the invoker is a superuser, row level
-- security stops applying inside those function bodies. Run this only to
-- recover from a failed migration, never as a resting state.
begin;
set search_path = prisma, public;

-- Restore the projection trigger exactly as 0004 found it. Without this the
-- rollback would be partial: ownership would revert while the body kept the
-- workspace scoping that only exists because the owner stopped bypassing RLS.
create or replace function aplicar_evento_tarea() returns trigger
security definer set search_path = prisma, public as $$
begin
  perform set_config('prisma.aplicando_evento', '1', true);
  update task
     set estado = new.estado_nuevo,
         actualizado_en = new.at
   where id = new.task_id;
  perform set_config('prisma.aplicando_evento', '0', true);
  return new;
end $$ language plpgsql;

do $$
declare invocante text := quote_ident(current_user);
begin
  if to_regprocedure('prisma.resolver_pendiente(text,uuid,timestamptz)') is not null then
    execute 'alter function prisma.resolver_pendiente(text, uuid, timestamptz) owner to ' || invocante;
  end if;
  if to_regprocedure('prisma.confirmar_borrador_tarea(uuid,text,bigint,bigint)') is not null then
    execute 'alter function prisma.confirmar_borrador_tarea(uuid, text, bigint, bigint) owner to ' || invocante;
  end if;
  if to_regprocedure('prisma.resolver_ingreso_borrador(uuid,text,bigint,bigint)') is not null then
    execute 'alter function prisma.resolver_ingreso_borrador(uuid, text, bigint, bigint) owner to ' || invocante;
  end if;
  if to_regprocedure('prisma.aplicar_evento_tarea()') is not null then
    execute 'alter function prisma.aplicar_evento_tarea() owner to ' || invocante;
  end if;
end $$;

revoke all privileges on all sequences in schema prisma from prisma_owner;
revoke all privileges on all tables in schema prisma from prisma_owner;
revoke usage on schema prisma from prisma_owner;

-- The role itself is left in place. Dropping a cluster role is an operational
-- decision separate from the schema: other databases in the same cluster may
-- reference it, and the schema creates every role with `if not exists`.

commit;
