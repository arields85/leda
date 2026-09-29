\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0020_bloque_copiable.sql.
--
-- Quita la columna y devuelve la envoltura `resolver_ingreso_borrador` a su
-- definición de 0002. Antes de correrlo, sin mensajes con bloque copiable por
-- despachar: la columna se pierde con sus datos. `create or replace` conserva
-- dueño y privilegios.
begin;
set search_path = prisma, public;

alter table message_outbox drop column if exists bloque_copiable;

create or replace function resolver_ingreso_borrador(p_workspace_id uuid, p_token text,
                                                     p_telegram_user_id bigint,
                                                     p_chat_id bigint)
returns table (resultado text, task_id uuid, pending_action_id uuid, replay boolean)
language plpgsql security definer
set search_path = prisma, public, pg_temp as $$
begin
  return query
    select c.resultado, c.task_id, c.pending_action_id, c.replay
      from confirmar_borrador_tarea(
        p_workspace_id, p_token, p_telegram_user_id, p_chat_id) c;
end $$;

commit;
