\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0024_avisos_de_coordinacion.sql. Decisión del usuario
-- (2026-09-30): quien confirma el borrador de OTRA persona lo rechaza con un
-- motivo, y a quien lo pidió se le avisa.
--
-- Rechazar no cancela de inmediato: el gateway lo intercepta, pide el motivo y
-- cancela con él (`ingreso_tareas.reject_draft`). Nunca llega a la autoridad.
-- Defensa en profundidad (como 0023 con "enviar"): `confirmar_borrador_tarea` sólo
-- distingue `false` (cancelar) de todo lo demás, así que un token de "rechazar"
-- que llegara hasta ella convertiría el borrador. La envoltura
-- `resolver_ingreso_borrador`, que ya rechazaba "modificar" y "enviar", rechaza
-- también "rechazar".
--
-- Sólo reemplaza el cuerpo de una función: `create or replace` conserva dueño y
-- privilegios (nada que conceder ni revocar).
--
-- Se deshace con `db/rollbacks/0025_rechazar_borrador.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0025 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (
      select 1 from information_schema.columns
       where table_schema = 'leda' and table_name = 'message_outbox'
         and column_name = 'es_coordinacion') then
    raise exception '0025 requires 0024_avisos_de_coordinacion.sql';
  end if;
  if to_regprocedure('leda.resolver_ingreso_borrador(uuid,text,bigint,bigint)') is null then
    raise exception '0025 requires resolver_ingreso_borrador(uuid,text,bigint,bigint)';
  end if;
end $$;

create or replace function resolver_ingreso_borrador(p_workspace_id uuid, p_token text,
                                          p_telegram_user_id bigint,
                                          p_chat_id bigint)
returns table (resultado text, task_id uuid, pending_action_id uuid, replay boolean)
language plpgsql security definer
set search_path = leda, public, pg_temp as $$
begin
  perform set_config('leda.workspace_id', p_workspace_id::text, true);
  -- Modificar (T9-R1c-3), Enviar a aprobación (T9-R1c-4) y Rechazar (2026-09-30)
  -- no confirman: sus tokens nunca llegan a la conversión.
  if exists (select 1 from pending_action_option o
              where o.token = p_token and o.workspace_id = p_workspace_id
                and o.valor in (to_jsonb('modificar'::text),
                                to_jsonb('enviar'::text),
                                to_jsonb('rechazar'::text))) then
    return query select 'inexistente'::text, null::uuid, null::uuid, false;
    return;
  end if;
  return query
    select c.resultado, c.task_id, c.pending_action_id, c.replay
      from confirmar_borrador_tarea(
        p_workspace_id, p_token, p_telegram_user_id, p_chat_id) c;
end $$;

commit;
