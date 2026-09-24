\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0009_vista_previa_confirmacion.sql.
--
-- Restores `resolver_pendiente` to its pre-0009 signature (no `huella`
-- column in its output) before dropping the column it read from, so no
-- function is ever left pointing at a column that does not exist.
begin;
set search_path = prisma, public;

drop function if exists resolver_pendiente(text, uuid, timestamptz);

create function resolver_pendiente(p_token text, p_app_user_id uuid,
                                   p_ahora timestamptz)
returns table (resultado text, herramienta text, args jsonb, cancelada boolean)
language plpgsql security definer as $$
declare
  o record;
  a record;
  ws uuid := nullif(current_setting('prisma.workspace_id', true), '')::uuid;
begin
  select * into o from pending_action_option
   where token = p_token and (ws is null or workspace_id = ws);
  if not found then
    return query select 'inexistente'::text, null::text, null::jsonb, null::boolean;
    return;
  end if;

  select * into a from pending_action where id = o.pending_action_id;

  if a.estado <> 'esperando' then
    return query select 'usada'::text, null::text, null::jsonb, null::boolean;
    return;
  end if;

  if a.vence_en <= p_ahora then
    update pending_action set estado = 'vencida' where id = a.id;
    return query select 'vencida'::text, null::text, null::jsonb, null::boolean;
    return;
  end if;

  -- El dueño de la acción es el único que la resuelve. Se resuelve por
  -- membresía, no por identidad de plataforma: el sombrero lo da el espacio.
  if not exists (select 1 from membership m
                  where m.id = a.membership_id and m.app_user_id = p_app_user_id) then
    return query select 'ajena'::text, null::text, null::jsonb, null::boolean;
    return;
  end if;

  if a.campo is null and o.valor = 'false'::jsonb then
    update pending_action
       set estado = 'cancelada', resuelta_en = p_ahora, resuelta_por = p_app_user_id
     where id = a.id and estado = 'esperando';
    if not found then
      return query select 'usada'::text, null::text, null::jsonb, null::boolean;
      return;
    end if;
    return query select 'cancelada'::text, null::text, null::jsonb, true;
    return;
  end if;

  update pending_action
     set estado = 'resuelta', resuelta_en = p_ahora, resuelta_por = p_app_user_id
   where id = a.id and estado = 'esperando';
  if not found then
    return query select 'usada'::text, null::text, null::jsonb, null::boolean;
    return;
  end if;

  return query select 'ok'::text, a.herramienta,
    case when a.campo is null then a.args
         else a.args || jsonb_build_object(a.campo, o.valor) end,
    false;
end $$;

comment on function resolver_pendiente is
  'Resuelve una acción pendiente por el token de una de sus opciones. Atómica: el doble toque de un botón ejecuta una sola vez.';

alter function resolver_pendiente(text, uuid, timestamptz)
  owner to prisma_owner;

alter table pending_action drop column if exists huella;

commit;
