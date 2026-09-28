\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0019_marca_de_bienvenida.sql.
--
-- Sólo agregó una columna con default, sin tocar privilegios ni dueño: un
-- `drop column` alcanza.
begin;
set search_path = prisma, public;

alter table message_outbox drop column if exists es_bienvenida;

commit;
