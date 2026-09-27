\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0011_incident_trazabilidad.sql. ADR 0009 (entrega con
-- evidencia y revisión): la entrega a `en_revision` (`actualizar_estado`) y
-- el gate de "Aprobar" (`menu_tarea.calcular_menu`, `aprobar_tarea`)
-- necesitan preguntar "¿a esta tarea le falta la evidencia que exige su
-- política?" -- la misma pregunta que ya resolvía, inline, una rama de
-- `motivo_no_cierra_tarea` (mecánica §5). En vez de repetir el criterio en
-- Python o duplicarlo en otra función SQL, se extrae a
-- `evidencia_pendiente(p_task)` y `motivo_no_cierra_tarea` pasa a llamarla:
-- una sola fuente de verdad, igual que ya son `motivo_no_arranca_tarea` y
-- `estado_previo_a_bloqueo` para sus propias preguntas.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0012 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (
      select 1 from pg_proc p join pg_namespace n on n.oid = p.pronamespace
       where n.nspname = 'prisma' and p.proname = 'motivo_no_cierra_tarea') then
    raise exception '0012 requires the base schema (motivo_no_cierra_tarea missing).';
  end if;
  if exists (
      select 1 from pg_proc p join pg_namespace n on n.oid = p.pronamespace
       where n.nspname = 'prisma' and p.proname = 'evidencia_pendiente') then
    raise exception '0012 ya está aplicada.';
  end if;
end $$;

create function evidencia_pendiente(p_task uuid)
returns boolean as $$
  select array_length(t.evidencia_requerida, 1) is not null
     and not exists (select 1 from evidence where task_id = t.id)
    from task t where t.id = p_task;
$$ language sql stable;

comment on function evidencia_pendiente(uuid) is
  'True si la tarea exige evidencia y todavía no tiene ninguna registrada. Única fuente de verdad para esa pregunta -- la usa motivo_no_cierra_tarea (cierre) y la entrega a en_revision / el gate de Aprobar (ADR 0009).';

-- El cuerpo cambia (la rama de evidencia llama a la función nueva en vez de
-- repetir el chequeo inline); la forma de salida no cambia.
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

  if evidencia_pendiente(p_task) then
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

commit;
