\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0026_borrador_enviado_no_es_rama_abierta.sql. Hallazgo F-B11 de la
-- corrida A (2026-10-01): una persona no pide tareas de otro sector, y para
-- ofrecerle sólo los objetivos de su área el objetivo tiene que saber de qué área
-- es. Hasta ahora `objective` no tenía área: la relación sólo se podía inferir de
-- las tareas.
--
-- `area_id` es nula por omisión y no se rellena acá: un objetivo sin área es un
-- dato viejo, y el alta lo trata con cautela (sólo lo ofrece si el área de quien
-- pide no tiene objetivos propios). Para dar el área a los objetivos que ya
-- existen, reimportar el pack (`python -m prisma importar <espacio>`): el
-- importador completa `area_id` de los frentes que todavía no la tienen, sin
-- tocar los que ya la tienen.
--
-- La clave foránea es compuesta (espacio, área) para que un objetivo nunca apunte
-- al área de otro cliente; con `area_id` nula no se comprueba nada.
--
-- Se deshace con `db/rollbacks/0027_objetivo_con_area.sql`.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0027 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('prisma.objective') is null then
    raise exception '0027 requires objective (0001_task_commitment.sql)';
  end if;
  if exists (
      select 1 from information_schema.columns
       where table_schema = 'prisma' and table_name = 'objective'
         and column_name = 'area_id') then
    raise exception '0027 ya está aplicada.';
  end if;
end $$;

-- Nuevas columnas y restricciones no tocan privilegios, dueño ni la seguridad por
-- filas de `objective` (aislamiento por espacio, forzado).
alter table area
  add constraint area_workspace_id_unique unique (workspace_id, id);

alter table objective add column area_id uuid;
alter table objective
  add constraint objective_area_workspace
  foreign key (workspace_id, area_id) references area (workspace_id, id);

create index objective_area on objective (workspace_id, area_id);

comment on column objective.area_id is
  'F-B11: el área a la que pertenece el objetivo. Nula en un objetivo estratégico (es de todas las áreas) o en un dato anterior a esta columna.';

commit;
