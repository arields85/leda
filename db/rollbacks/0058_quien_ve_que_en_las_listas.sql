\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0058_quien_ve_que_en_las_listas.sql.
--
-- Borra las cuatro funciones de quién ve qué en las listas de la web. No guardan datos: no se
-- pierde nada. `puede_ver_tarea` no se toca (la 0058 no la cambió).
begin;
set search_path = leda, public;

drop function if exists vistas_de_la_sesion(text);
drop function if exists tareas_de_la_sesion(text, text, timestamptz);
drop function if exists vistas_de(uuid);
drop function if exists tareas_que_ve(uuid, text, timestamptz);

commit;
