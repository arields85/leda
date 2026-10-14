\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0068_los_objetivos_desde_la_web.sql.
--
-- Borra `crear_objetivo_web`, `opciones_del_objetivo`, `quien_crea_el_objetivo`,
-- `creacion_de_objetivo`, la restricción de `niveles` en `workspace_setting` y `niveles_validos`,
-- vuelve a las claves simples del padre y del referente de `objective` y le devuelve a `leda_app`
-- la escritura directa de `objective`. Se niega a correr si eso
-- perdiera datos: una clave de creación guardada (sin ella, un formulario reenviado volvería a
-- crear el mismo objetivo). Los objetivos creados, sus eventos, lo que quedó en `audit_log` y las
-- filas `niveles` de `workspace_setting` no se tocan (sin la restricción, son un ajuste más que
-- nadie lee). Antes de correrlo en una base con datos, `pg_dump` de esa tabla y vaciarla a mano,
-- con la decisión registrada.
begin;
set search_path = leda, public;

do $$ begin
  if to_regclass('leda.creacion_de_objetivo') is not null
     and exists (select 1 from creacion_de_objetivo) then
    raise exception '0068 rollback refused: hay claves de objetivos creados desde la web';
  end if;
end $$;

drop function if exists crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid, text);
drop function if exists opciones_del_objetivo(text, text, uuid);
drop function if exists quien_crea_el_objetivo(text, text, uuid);

drop table if exists creacion_de_objetivo;

alter table workspace_setting drop constraint if exists workspace_setting_niveles;
drop function if exists niveles_validos(jsonb);

alter table objective drop constraint if exists objective_padre_del_espacio;
alter table objective drop constraint if exists objective_referente_del_espacio;
alter table objective add constraint objective_parent_id_fkey
  foreign key (parent_id) references objective(id) on delete cascade;
alter table objective add constraint objective_referente_membership_id_fkey
  foreign key (referente_membership_id) references membership(id);
alter table objective drop constraint if exists objective_workspace_id_unique;

grant insert, update, delete on objective to leda_app;

commit;
