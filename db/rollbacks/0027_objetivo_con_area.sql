\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0027_objetivo_con_area.sql.
--
-- Quita el área de los objetivos (se pierde el dato: el importador del pack puede
-- volver a darla al reaplicar la migración) y la restricción única de `area` que
-- sostenía la clave foránea.
begin;
set search_path = prisma, public;

drop index if exists objective_area;
alter table objective drop constraint if exists objective_area_workspace;
alter table objective drop column if exists area_id;
alter table area drop constraint if exists area_workspace_id_unique;

commit;
