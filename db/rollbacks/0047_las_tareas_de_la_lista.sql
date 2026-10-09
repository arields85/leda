\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0047_las_tareas_de_la_lista.sql.
--
-- Borra `scheduled_notice.tareas_de_la_lista`. No se niega a correr: lo que se pierde es qué llevó
-- cada lista de la cadencia y qué contestó la persona de cada tarea, que sólo decide qué va en las
-- listas siguientes de la semana y si el pedido del día del vencimiento sale (el código anterior no
-- lo lee). Antes de deshacerla en una base con datos, `pg_dump` de `scheduled_notice` y la decisión
-- registrada.
begin;
set search_path = leda, public;

alter table scheduled_notice drop column if exists tareas_de_la_lista;

commit;
