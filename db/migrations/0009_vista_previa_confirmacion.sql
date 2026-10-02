\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0008_task_start_gate.sql. Adds the fingerprint that lets a
-- confirmation detect that the state it previewed changed before the person
-- confirmed it (ADR 0005, decisión 1; docs/decisions/0005-interpretacion-y-
-- confirmacion.md). Without it, `pending_action` only remembered the
-- herramienta and its arguments: two different reads of the same resource,
-- one at preview time and one at confirm time, were indistinguishable.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0009 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'leda_owner') then
    raise exception '0009 requires 0004_function_ownership.sql';
  end if;
  if to_regprocedure('leda.resolver_pendiente(text,uuid,timestamptz)') is null then
    raise exception '0009 requires the base schema pending_action machinery';
  end if;
end $$;

-- Texto opaco: quien arma la huella (`herramientas.py`) decide qué entra. La
-- base no la interpreta, sólo la guarda y la devuelve para comparar.
alter table pending_action add column huella text;

-- Cambia la forma de salida (agrega `huella`), así que no alcanza con
-- `create or replace`: hay que soltarla y volver a crearla.
drop function if exists resolver_pendiente(text, uuid, timestamptz);

create function resolver_pendiente(p_token text, p_app_user_id uuid,
                                   p_ahora timestamptz)
returns table (resultado text, herramienta text, args jsonb,
               cancelada boolean, huella text)
language plpgsql security definer as $$
declare
  o record;
  a record;
  ws uuid := nullif(current_setting('leda.workspace_id', true), '')::uuid;
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
  'Resuelve una acción pendiente por el token de una de sus opciones. Atómica: el doble toque de un botón ejecuta una sola vez. Devuelve la huella guardada para que quien llama detecte si el estado cambió desde la vista previa.';

alter function resolver_pendiente(text, uuid, timestamptz)
  owner to leda_owner;

commit;
