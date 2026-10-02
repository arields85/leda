\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0012_evidencia_pendiente.sql.
--
-- Restores `motivo_no_cierra_tarea` to its pre-0012 body (the inline
-- evidence check, not the call to `evidencia_pendiente`) before dropping
-- the function, so no function is ever left calling one that does not
-- exist.
begin;
set search_path = leda, public;

create or replace function motivo_no_cierra_tarea(p_task uuid)
returns text as $$
declare
  t            task%rowtype;
  aprobador    uuid;
  dep_abiertas integer;
begin
  select * into t from task where id = p_task;
  if not found then return 'La tarea no existe.'; end if;

  -- Que el criterio sea obligatorio lo decide el pack del espacio.
  if coalesce((select valor::text::boolean from workspace_setting
                where workspace_id = t.workspace_id
                  and clave = 'exigir_criterio_aceptacion'), true)
     and (t.criterio_aceptacion is null or btrim(t.criterio_aceptacion) = '') then
    return 'Falta el criterio de aceptación.';
  end if;

  if array_length(t.evidencia_requerida, 1) is not null
     and not exists (select 1 from evidence where task_id = p_task) then
    return 'Falta la evidencia requerida.';
  end if;

  if exists (select 1 from blocker where task_id = p_task and resuelto_en is null) then
    return 'La tarea tiene un bloqueo abierto.';
  end if;

  select count(*) into dep_abiertas
    from dependency d join task o on o.id = d.origen_task_id
   where d.destino_task_id = p_task
     and d.tipo = 'bloqueante'
     and o.estado not in ('terminada', 'cancelada');
  if dep_abiertas > 0 then
    return format('Quedan %s dependencias bloqueantes sin resolver.', dep_abiertas);
  end if;

  -- La aprobación de una tarea la da quien revisa el trabajo de su
  -- responsable. Es por persona, no por área: Marcos aprueba a Nahuel aunque
  -- estén en áreas distintas, y a Marcos lo aprueba Dirección.
  select m.aprobador_membership_id into aprobador
    from membership m where m.id = t.responsable_membership_id;

  if aprobador is not null
     and not exists (
       select 1 from approval a
        where a.sujeto_tipo = 'tarea' and a.sujeto_id = p_task
          and a.decision = 'aprobado'
          and a.aprobador_membership_id = aprobador) then
    return 'Falta la aprobación de quien revisa ese trabajo.';
  end if;

  return null;
end $$ language plpgsql;

drop function if exists evidencia_pendiente(uuid);

commit;
