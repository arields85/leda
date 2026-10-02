\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0023_enviar_a_aprobacion.sql.
--
-- Devuelve la envoltura `resolver_ingreso_borrador` a la definición de 0020, que
-- sólo rechaza "modificar". Antes de correrlo, sin borradores del alta que
-- esperen la revisión de quien los pidió (sus tokens de "enviar" llegarían a la
-- conversión). `create or replace` conserva dueño y privilegios.
begin;
set search_path = leda, public;

create or replace function resolver_ingreso_borrador(p_workspace_id uuid, p_token text,
                                          p_telegram_user_id bigint,
                                          p_chat_id bigint)
returns table (resultado text, task_id uuid, pending_action_id uuid, replay boolean)
language plpgsql security definer
set search_path = leda, public, pg_temp as $$
begin
  perform set_config('leda.workspace_id', p_workspace_id::text, true);
  -- Modificar no confirma (T9-R1c-3): su token nunca llega a la conversión.
  if exists (select 1 from pending_action_option o
              where o.token = p_token and o.workspace_id = p_workspace_id
                and o.valor = to_jsonb('modificar'::text)) then
    return query select 'inexistente'::text, null::uuid, null::uuid, false;
    return;
  end if;
  return query
    select c.resultado, c.task_id, c.pending_action_id, c.replay
      from confirmar_borrador_tarea(
        p_workspace_id, p_token, p_telegram_user_id, p_chat_id) c;
end $$;

commit;
