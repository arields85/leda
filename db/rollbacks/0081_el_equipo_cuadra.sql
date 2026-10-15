\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0081_el_equipo_cuadra.sql: borra `cambio_del_equipo` (con su disparador, su función y su
-- política), `problemas_del_equipo`, `unir_nombres` y `area.archivada_en`, y le devuelve a
-- `leda_app` la escritura de `area`, `rol`, `membership`, `approval_policy` y `escalation_route`.
-- Se pierden la historia de los cambios del equipo y la marca de las áreas archivadas (que vuelven
-- a contar como áreas vigentes): antes de correrlo en una base con datos, `pg_dump` de
-- `cambio_del_equipo` y de `area`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0081 rollback requires an unmodified UTF-8 input stream';
  end if;
end $$;

drop table if exists cambio_del_equipo;
drop function if exists rechazar_cambios_del_equipo();
drop function if exists problemas_del_equipo(uuid);
drop function if exists unir_nombres(text[]);
alter table area drop column if exists archivada_en;

-- Quitar el `update` de la tabla se lleva también el de la columna `workspace_id`.
revoke update on membership from leda_app;
grant insert, update, delete on area, rol, membership, approval_policy, escalation_route
  to leda_app;

commit;
