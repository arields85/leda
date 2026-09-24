\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0009_vista_previa_confirmacion.sql. Adds the third preview
-- button, Modificar (T3, ADR 0005 decisión 1; odd/tasks/
-- vista-previa-y-confirmacion.md). Tapping it closes the proposal without
-- any effect and leaves the row as the context that the next free-text
-- message from that person, in that chat, gets interpreted against.
--
-- Deliberately not a new `estado_pendiente` value: the row still ends in
-- 'cancelada', which already means "nothing was applied" and needs no
-- special-casing anywhere that reads that column. `modificar_pedido_en`
-- carries the one new fact -- that this particular close was a request to
-- correct something, not to drop it -- and reuses `herramienta`, `args` and
-- `resumen`, already on the row from when the preview was built, instead of
-- a parallel table.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0010 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'prisma_owner') then
    raise exception '0010 requires 0004_function_ownership.sql';
  end if;
  if not exists (
      select 1 from information_schema.columns
       where table_schema = 'prisma' and table_name = 'pending_action'
         and column_name = 'huella') then
    raise exception '0010 requires 0009_vista_previa_confirmacion.sql';
  end if;
end $$;

alter table pending_action add column modificar_pedido_en timestamptz;
alter table pending_action add column modificacion_consumida_en timestamptz;

-- La forma de salida no cambia (resultado, herramienta, args, cancelada,
-- huella): alcanza con reemplazar el cuerpo, no hace falta soltar la función.
create or replace function resolver_pendiente(p_token text, p_app_user_id uuid,
                                              p_ahora timestamptz)
returns table (resultado text, herramienta text, args jsonb,
               cancelada boolean, huella text)
language plpgsql security definer as $$
declare
  o record;
  a record;
  ws uuid := nullif(current_setting('prisma.workspace_id', true), '')::uuid;
begin
  select * into o from pending_action_option
   where token = p_token and (ws is null or workspace_id = ws);
  if not found then
    return query select 'inexistente'::text, null::text, null::jsonb,
      null::boolean, null::text;
    return;
  end if;

  select * into a from pending_action where id = o.pending_action_id;

  if a.estado <> 'esperando' then
    return query select 'usada'::text, null::text, null::jsonb,
      null::boolean, null::text;
    return;
  end if;

  if a.vence_en <= p_ahora then
    update pending_action set estado = 'vencida' where id = a.id;
    return query select 'vencida'::text, null::text, null::jsonb,
      null::boolean, null::text;
    return;
  end if;

  -- El dueño de la acción es el único que la resuelve. Se resuelve por
  -- membresía, no por identidad de plataforma: el sombrero lo da el espacio.
  if not exists (select 1 from membership m
                  where m.id = a.membership_id and m.app_user_id = p_app_user_id) then
    return query select 'ajena'::text, null::text, null::jsonb,
      null::boolean, null::text;
    return;
  end if;

  -- Modificar (T3, ADR 0005 decisión 1): cierra sin aplicar nada, igual que
  -- Cancelar -- por eso queda en 'cancelada' y no en un estado nuevo -- pero
  -- deja marcado `modificar_pedido_en`: la fila misma es el contexto que va
  -- a leer el próximo turno de esta persona en este chat, porque ya tiene
  -- `herramienta`, `args` y `resumen` de cuando se armó la vista previa.
  if a.campo is null and o.valor = '"modificar"'::jsonb then
    update pending_action
       set estado = 'cancelada', resuelta_en = p_ahora, resuelta_por = p_app_user_id,
           modificar_pedido_en = p_ahora
     where id = a.id and estado = 'esperando';
    if not found then
      return query select 'usada'::text, null::text, null::jsonb,
        null::boolean, null::text;
      return;
    end if;
    -- Sólo puede haber una Modificación abierta por persona y chat: una
    -- nueva deja sin efecto cualquier otra que todavía no se hubiera leído,
    -- para que una corrección nunca se aplique a una propuesta vieja.
    update pending_action
       set modificacion_consumida_en = p_ahora
     where workspace_id = a.workspace_id and membership_id = a.membership_id
       and chat_id = a.chat_id and modificar_pedido_en is not null
       and modificacion_consumida_en is null and id <> a.id;
    return query select 'modificada'::text, a.herramienta, a.args, false, a.huella;
    return;
  end if;

  if a.campo is null and o.valor = 'false'::jsonb then
    update pending_action
       set estado = 'cancelada', resuelta_en = p_ahora, resuelta_por = p_app_user_id
     where id = a.id and estado = 'esperando';
    if not found then
      return query select 'usada'::text, null::text, null::jsonb,
        null::boolean, null::text;
      return;
    end if;
    return query select 'cancelada'::text, null::text, null::jsonb, true,
      null::text;
    return;
  end if;

  update pending_action
     set estado = 'resuelta', resuelta_en = p_ahora, resuelta_por = p_app_user_id
   where id = a.id and estado = 'esperando';
  if not found then
    return query select 'usada'::text, null::text, null::jsonb,
      null::boolean, null::text;
    return;
  end if;

  return query select 'ok'::text, a.herramienta,
    case when a.campo is null then a.args
         else a.args || jsonb_build_object(a.campo, o.valor) end,
    false, a.huella;
end $$;

comment on function resolver_pendiente is
  'Resuelve una acción pendiente por el token de una de sus opciones. Atómica: el doble toque de un botón ejecuta una sola vez. Devuelve la huella guardada para que quien llama detecte si el estado cambió desde la vista previa. "modificada" cierra sin aplicar nada y marca `modificar_pedido_en`, que deja la fila como contexto para el próximo turno de esa persona en ese chat (ADR 0005, decisión 1).';

alter function resolver_pendiente(text, uuid, timestamptz)
  owner to prisma_owner;

commit;
