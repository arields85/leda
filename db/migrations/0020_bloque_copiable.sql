\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0019_marca_de_bienvenida.sql. T9-R1c-3 (ADR 0005 decisión 1,
-- precisión del 2026-09-29: Modificar en el borrador del alta guiada).
--
-- Un dato de texto del borrador se le muestra a la persona en un bloque que se
-- copia con un toque (entidad `pre` de Telegram) y, si entra en 256
-- caracteres, con el botón de copiar (`copy_text`), para que lo pegue, lo
-- corrija y lo mande. El bloque es el final del texto del mensaje: la columna
-- guarda el bloque mismo y el transporte calcula su posición sobre el texto
-- que de verdad manda, con el saludo diario ya antepuesto.
--
-- Además, la vista previa del borrador gana el botón Modificar, cuya opción
-- (`pending_action_option.valor = "modificar"`) no es una confirmación. La
-- función que convierte el borrador (`confirmar_borrador_tarea`) sólo
-- distingue `false` (cancelar) de todo lo demás, así que un token de Modificar
-- que llegara hasta ella convertiría el borrador. El gateway lo intercepta
-- antes; esta migración cierra la misma puerta en la base: la envoltura
-- `resolver_ingreso_borrador` trata ese token como inexistente. Un
-- `create or replace` conserva dueño y privilegios.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0020 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (
      select 1 from information_schema.columns
       where table_schema = 'prisma' and table_name = 'message_outbox'
         and column_name = 'es_bienvenida') then
    raise exception '0020 requires 0019_marca_de_bienvenida.sql';
  end if;
  if exists (
      select 1 from information_schema.columns
       where table_schema = 'prisma' and table_name = 'message_outbox'
         and column_name = 'bloque_copiable') then
    raise exception '0020 ya está aplicada.';
  end if;
  if to_regprocedure('prisma.resolver_ingreso_borrador(uuid,text,bigint,bigint)') is null then
    raise exception '0020 requires resolver_ingreso_borrador(uuid,text,bigint,bigint)';
  end if;
end $$;

-- Una columna nueva, nula por omisión, no toca privilegios ni dueño de la
-- tabla: prisma_app ya tiene el juego completo sobre message_outbox (bucle
-- genérico de `db/esquema.sql`). Sin concesión que agregar.
alter table message_outbox add column bloque_copiable text;

comment on column message_outbox.bloque_copiable is
  'T9-R1c-3: lo que la persona había escrito, para que lo copie con un toque -- el final de cuerpo. El transporte lo marca como bloque (entidad pre) y, si entra en 256 unidades UTF-16, agrega el botón de copiar.';

create or replace function resolver_ingreso_borrador(p_workspace_id uuid, p_token text,
                                                     p_telegram_user_id bigint,
                                                     p_chat_id bigint)
returns table (resultado text, task_id uuid, pending_action_id uuid, replay boolean)
language plpgsql security definer
set search_path = prisma, public, pg_temp as $$
begin
  perform set_config('prisma.workspace_id', p_workspace_id::text, true);
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
