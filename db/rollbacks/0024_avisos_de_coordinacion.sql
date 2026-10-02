\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0024_avisos_de_coordinacion.sql.
--
-- Sólo agregó una columna booleana con valor por omisión, sin tocar privilegios
-- ni dueño. Se pierde qué filas eran avisos de coordinación: al deshacer, todas
-- vuelven a contar contra el tope diario (y a ser pospuestas por él).
begin;
set search_path = leda, public;

alter table message_outbox drop column if exists es_coordinacion;

commit;
