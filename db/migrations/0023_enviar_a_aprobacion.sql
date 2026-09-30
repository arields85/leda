\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0022_toque_con_boton.sql. T9-R1c-4 (ADR 0005 decisión 1,
-- precisión del 2026-09-29: quien pide revisa antes de enviar a aprobación).
--
-- Cuando el borrador lo confirma otra persona, quien lo pidió ve primero su
-- propio resumen con Enviar a aprobación, Modificar y Cancelar. Enviar a
-- aprobación no confirma nada: lo intercepta el gateway y nunca llega a la
-- autoridad. Defensa en profundidad: `confirmar_borrador_tarea` sólo distingue
-- `false` (cancelar) de todo lo demás, así que un token de "enviar" que llegara
-- hasta ella convertiría el borrador. La envoltura `resolver_ingreso_borrador`,
-- que ya rechazaba "modificar" (0020), rechaza también "enviar".
--
-- Sólo reemplaza el cuerpo de una función: `create or replace` conserva dueño y
-- privilegios (nada que conceder ni revocar).
--
-- Se deshace con `db/rollbacks/0023_enviar_a_aprobacion.sql`.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0023 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (
      select 1 from information_schema.columns
       where table_schema = 'prisma' and table_name = 'inbound_message'
         and column_name = 'boton_callback') then
    raise exception '0023 requires 0022_toque_con_boton.sql';
  end if;
  if to_regprocedure('prisma.resolver_ingreso_borrador(uuid,text,bigint,bigint)') is null then
    raise exception '0023 requires resolver_ingreso_borrador(uuid,text,bigint,bigint)';
  end if;
end $$;

create or replace function resolver_ingreso_borrador(p_workspace_id uuid, p_token text,
                                          p_telegram_user_id bigint,
                                          p_chat_id bigint)
returns table (resultado text, task_id uuid, pending_action_id uuid, replay boolean)
language plpgsql security definer
set search_path = prisma, public, pg_temp as $$
begin
  perform set_config('prisma.workspace_id', p_workspace_id::text, true);
  -- Modificar (T9-R1c-3) y Enviar a aprobación (T9-R1c-4) no confirman: sus
  -- tokens nunca llegan a la conversión.
  if exists (select 1 from pending_action_option o
              where o.token = p_token and o.workspace_id = p_workspace_id
                and o.valor in (to_jsonb('modificar'::text),
                                to_jsonb('enviar'::text))) then
    return query select 'inexistente'::text, null::uuid, null::uuid, false;
    return;
  end if;
  return query
    select c.resultado, c.task_id, c.pending_action_id, c.replay
      from confirmar_borrador_tarea(
        p_workspace_id, p_token, p_telegram_user_id, p_chat_id) c;
end $$;

commit;
