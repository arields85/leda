\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0022_toque_con_boton.sql.
--
-- Sólo agregó una columna nula con su índice, sin tocar privilegios ni dueño:
-- quitar la columna se lleva el índice. Se pierde qué botón tocó cada persona
-- (los toques siguen registrados como actividad, sin el botón).
begin;
set search_path = leda, public;

alter table inbound_message drop column if exists boton_callback;

commit;
