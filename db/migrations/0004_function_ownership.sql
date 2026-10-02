\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0003_state_event_isolation.sql. The four security definer
-- functions had no declared owner, so they belonged to whoever ran the schema.
-- On a standard install that is a superuser, which ignores row level security:
-- the isolation policies did not apply inside those function bodies at all.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0004 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (select 1 from information_schema.columns
                  where table_schema = 'leda'
                    and table_name = 'task_state_event'
                    and column_name = 'workspace_id') then
    raise exception '0004 requires 0003_state_event_isolation.sql';
  end if;
end $$;

-- Preflight: every elevated function this migration claims to reassign must
-- exist with the expected signature. A renamed or resignatured function would
-- otherwise be left silently owned by a superuser.
do $$
declare faltantes text := '';
begin
  if to_regprocedure('leda.resolver_pendiente(text,uuid,timestamptz)') is null
    then faltantes := faltantes || ' resolver_pendiente'; end if;
  if to_regprocedure('leda.confirmar_borrador_tarea(uuid,text,bigint,bigint)') is null
    then faltantes := faltantes || ' confirmar_borrador_tarea'; end if;
  if to_regprocedure('leda.resolver_ingreso_borrador(uuid,text,bigint,bigint)') is null
    then faltantes := faltantes || ' resolver_ingreso_borrador'; end if;
  if to_regprocedure('leda.aplicar_evento_tarea()') is null
    then faltantes := faltantes || ' aplicar_evento_tarea'; end if;
  if faltantes <> '' then
    raise exception '0004 preflight failed: missing elevated function(s):%', faltantes;
  end if;
end $$;

-- A dedicated owner for the elevated functions. It cannot log in, nobody is a
-- member of it, and -- the point of this migration -- it does not bypass row
-- level security, so the isolation policy applies inside every function body.
do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'leda_owner') then
    create role leda_owner nologin noinherit;
  end if;
end $$;
alter role leda_owner nologin noinherit nobypassrls nosuperuser;

-- Row level security, not the grant list, is what contains this role. An
-- exact hand-kept list of what each body touches would rot on the next change
-- and fail closed in production; the containment that matters is nobypassrls,
-- no login and no membership.
grant usage on schema leda to leda_owner;
grant all privileges on all tables in schema leda to leda_owner;
grant all privileges on all sequences in schema leda to leda_owner;

-- The projection trigger was silently relying on bypassing row level
-- security: the administrative connection sets no workspace at all, so once
-- the owner stops bypassing RLS the update matches no row and the state never
-- projects. Scope it to the event's own workspace, which the derivation
-- trigger from 0003 already resolved from the parent task, and restore the
-- previous value so the rest of the transaction keeps its original breadth.
create or replace function aplicar_evento_tarea() returns trigger
security definer set search_path = leda, public as $$
declare espacio_anterior text := current_setting('leda.workspace_id', true);
begin
  perform set_config('leda.workspace_id', new.workspace_id::text, true);
  perform set_config('leda.aplicando_evento', '1', true);
  update task
     set estado = new.estado_nuevo,
         actualizado_en = new.at
   where id = new.task_id;
  perform set_config('leda.aplicando_evento', '0', true);
  perform set_config('leda.workspace_id', coalesce(espacio_anterior, ''), true);
  return new;
end $$ language plpgsql;

alter function resolver_pendiente(text, uuid, timestamptz)
  owner to leda_owner;
alter function confirmar_borrador_tarea(uuid, text, bigint, bigint)
  owner to leda_owner;
alter function resolver_ingreso_borrador(uuid, text, bigint, bigint)
  owner to leda_owner;
alter function aplicar_evento_tarea()
  owner to leda_owner;

commit;
