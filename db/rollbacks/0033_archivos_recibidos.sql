\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0033_archivos_recibidos.sql.
--
-- Borra `archivo_de_mensaje` y `archivo` (con sus disparadores y la función que rechaza los
-- cambios de un archivo) y el rango de `archivo_tamano_maximo_mb` en `workspace_setting` (las
-- filas de esa clave quedan). Se pierden los archivos recibidos, que el disparador protege de
-- un borrado pero no de que se borre la tabla: antes de correrlo en una base con datos,
-- `pg_dump` de esas dos tablas.
begin;
set search_path = leda, public;

alter table workspace_setting
  drop constraint if exists workspace_setting_archivo_tamano_maximo;

drop table if exists archivo_de_mensaje;
drop table if exists archivo;
drop function if exists rechazar_cambios_de_archivo();

commit;
