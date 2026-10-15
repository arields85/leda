\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0077_el_cambio_de_fecha.sql: borra `cambio_de_fecha` (con su disparador, su función y su
-- política) y vuelve a poner `bloquear_estado_directo` como la dejó la 0046, con la fecha de una
-- tarea inmutable. Las tareas cuya fecha cambió se quedan con la fecha nueva; se pierde la historia
-- de los cambios: antes de correrlo en una base con datos, `pg_dump` de la tabla.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0077 rollback requires an unmodified UTF-8 input stream';
  end if;
end $$;

drop table if exists cambio_de_fecha;
drop function if exists aplicar_cambio_de_fecha();

create or replace function bloquear_estado_directo() returns trigger as $$
begin
  if new.objective_id is distinct from old.objective_id
     or new.titulo is distinct from old.titulo
     or new.descripcion is distinct from old.descripcion
     or new.area_id is distinct from old.area_id
     or new.fecha_objetivo is distinct from old.fecha_objetivo
     or new.criterio_aceptacion is distinct from old.criterio_aceptacion
     or new.evidencia_requerida is distinct from old.evidencia_requerida
     or new.evidencia_policy_version is distinct from old.evidencia_policy_version
     or new.source_draft_id is distinct from old.source_draft_id then
    raise exception 'Los campos de compromiso de una tarea son inmutables.';
  end if;
  -- Quién la tiene y de quién era cambian sólo con un pase confirmado por quien lo pidió, quien
  -- lo decidió y quien la toma (migraciones 0045 y 0046; C-7, delegar): lo aplica
  -- `aplicar_cambio_de_responsable`, al agregarse el cambio en `cambio_de_responsable`.
  if (new.responsable_membership_id is distinct from old.responsable_membership_id
      or new.era_de_membership_id is distinct from old.era_de_membership_id)
     and coalesce(current_setting('leda.aplicando_pase', true), '0') <> '1' then
    raise exception 'Los campos de compromiso de una tarea son inmutables.';
  end if;
  if new.estado is distinct from old.estado
     and coalesce(current_setting('leda.aplicando_evento', true), '0') <> '1' then
    raise exception
      'El estado de una tarea no se escribe directamente. Insertá una fila en task_state_event.';
  end if;
  return new;
end $$ language plpgsql;

commit;
