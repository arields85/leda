\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0020_bloque_copiable.sql. T9-R2 (ADR 0013 regla 2: cada mensaje
-- recibe exactamente una respuesta visible).
--
-- El control estructural que corre al terminar de procesar un mensaje necesita
-- saber qué se encoló COMO respuesta a ese mensaje. Hasta ahora `message_outbox`
-- no lo decía (sólo `chat_id` y la hora): no hay forma fiable de atar una salida
-- a su entrante por horario o por clave de deduplicación.
--
-- `entrante_id` se llena sola: el gateway deja el id del mensaje en la
-- configuración de la transacción (`leda.entrante_id`, local) y el valor por
-- omisión de la columna la lee, así que cualquier `insert` de esa transacción
-- (Python o una función de la base) queda atado sin pasar el dato por cada
-- llamada. Fuera de un mensaje (un toque, una cadencia, la escalera) la
-- configuración no existe y la columna queda nula.
--
-- `respuesta_grupo` nombra la respuesta a la que pertenece una fila cuando una
-- respuesta se encola en varias llamadas (el texto en partes y aparte el mensaje
-- con los botones): las filas con el mismo grupo son partes de UNA respuesta.
-- Nula: la fila es su propia respuesta (o las partes de un texto partido, que
-- comparten el prefijo de su clave).
--
-- Se deshace con `db/rollbacks/0021_respuesta_atada_al_mensaje.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0021 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (
      select 1 from information_schema.columns
       where table_schema = 'leda' and table_name = 'message_outbox'
         and column_name = 'bloque_copiable') then
    raise exception '0021 requires 0020_bloque_copiable.sql';
  end if;
  if exists (
      select 1 from information_schema.columns
       where table_schema = 'leda' and table_name = 'message_outbox'
         and column_name = 'entrante_id') then
    raise exception '0021 ya está aplicada.';
  end if;
end $$;

-- Columnas nuevas, nulas por omisión: no tocan privilegios ni dueño de la tabla
-- (leda_app ya tiene el juego completo sobre message_outbox, bucle genérico de
-- `db/esquema.sql`). La clave foránea es sobre la clave primaria de `inbound_message`
-- (no compuesta con el espacio, como las demás de la tabla): la compuesta
-- dependería de `inbound_message_workspace_id_unique`, que es de la 0002, y
-- volver atrás la 0002 dejaría de ser posible sin quitar antes esta. El valor lo
-- pone el gateway con un mensaje del mismo espacio (`db.atar_al_entrante`); si la
-- retención borra el mensaje entrante, la salida queda.
alter table message_outbox
  add column entrante_id uuid
    default nullif(current_setting('leda.entrante_id', true), '')::uuid,
  add column respuesta_grupo text;

alter table message_outbox
  add constraint message_outbox_entrante
    foreign key (entrante_id) references inbound_message(id)
    on delete set null;

create index outbox_por_entrante on message_outbox (entrante_id)
  where entrante_id is not null;

comment on column message_outbox.entrante_id is
  'T9-R2: el mensaje entrante (inbound_message) al que responde esta salida. Se llena sola con la configuración local leda.entrante_id que deja el gateway al procesar un mensaje; nula fuera de un mensaje (toque, cadencia, escalera).';
comment on column message_outbox.respuesta_grupo is
  'T9-R2: nombre de la respuesta a la que pertenece la fila cuando una respuesta se encola en varias llamadas (texto en partes y mensaje con botones). Nula: la fila es su propia respuesta.';

commit;
