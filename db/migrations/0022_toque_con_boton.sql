\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0021_respuesta_atada_al_mensaje.sql. T9-R4 (ADR 0013 regla 4:
-- todo toque tiene señal inmediata y es idempotente).
--
-- Cada toque de botón ya deja una fila textless en `inbound_message` (es
-- actividad, T9-R1d-2b). Para absorber el segundo toque del MISMO botón de la
-- misma persona dentro de una ventana corta hace falta saber qué botón fue:
-- `boton_callback` guarda el `callback_data` que mandó Telegram (lleva el token
-- de la opción, único por botón). Nula en un mensaje escrito y en un toque
-- absorbido, así que un toque absorbido no prolonga la ventana del primero.
--
-- Columna nula por omisión: no toca privilegios ni dueño de la tabla.
--
-- Se deshace con `db/rollbacks/0022_toque_con_boton.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0022 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (
      select 1 from information_schema.columns
       where table_schema = 'leda' and table_name = 'message_outbox'
         and column_name = 'entrante_id') then
    raise exception '0022 requires 0021_respuesta_atada_al_mensaje.sql';
  end if;
  if exists (
      select 1 from information_schema.columns
       where table_schema = 'leda' and table_name = 'inbound_message'
         and column_name = 'boton_callback') then
    raise exception '0022 ya está aplicada.';
  end if;
end $$;

alter table inbound_message add column boton_callback text;

create index inbound_por_boton on inbound_message
  (workspace_id, chat_id, app_user_id, boton_callback, at)
  where boton_callback is not null;

comment on column inbound_message.boton_callback is
  'T9-R4: el callback_data del botón que la persona tocó (una fila de toque). Nula en un mensaje escrito y en un toque absorbido por repetido dentro de la ventana.';

commit;
