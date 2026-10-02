\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0021_respuesta_atada_al_mensaje.sql.
--
-- Sólo agregó dos columnas nulas con su clave foránea y su índice, sin tocar
-- privilegios ni dueño: quitar las columnas se lleva la clave y el índice. Se
-- pierde el vínculo de cada salida con el mensaje al que respondía.
begin;
set search_path = leda, public;

alter table message_outbox
  drop column if exists entrante_id,
  drop column if exists respuesta_grupo;

commit;
