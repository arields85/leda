\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0012_evidencia_pendiente.sql. Revisión review-c112506a
-- (seguimiento, `odd/tasks/prisma-orienta.md` T6a): `motivo_no_cierra_tarea`
-- contaba cualquier `approval` 'aprobado' del aprobador, de cualquier
-- momento. ADR 0009 agregó "Pedir cambios" (`herramientas._pedir_cambios_
-- tarea`), que inserta un `approval` 'rechazado' y devuelve la tarea a
-- `en_curso` -- pero no invalidaba ninguna aprobación anterior. Escenario:
-- el aprobador aprueba una entrega que no cierra (por ejemplo por un
-- bloqueo abierto); después pide cambios; el
-- responsable vuelve a entregar -- la aprobación vieja seguía contando, y el
-- trabajo corregido podía cerrarse sin que nadie lo aprobara.
--
-- El cuerpo cambia (la condición de aprobación pasa a exigir que sea la
-- ÚLTIMA decisión del aprobador sobre la tarea); la forma de salida no
-- cambia.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0013 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regprocedure('prisma.evidencia_pendiente(uuid)') is null then
    raise exception '0013 requires 0012_evidencia_pendiente.sql';
  end if;
  if pg_get_functiondef('prisma.motivo_no_cierra_tarea(uuid)'::regprocedure)
     like '%r.decision = ''rechazado''%' then
    raise exception '0013 ya está aplicada.';
  end if;
end $$;

-- No es security definer: corre con los privilegios de quien llama, igual
-- que antes de esta migración -- `approval` ya tiene `select` concedido a
-- `prisma_app` desde el esquema base, así que no hace falta ninguna
-- concesión nueva.
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

  -- Sólo cuenta si la ÚLTIMA decisión del aprobador sobre esta tarea es
  -- 'aprobado' (review-c112506a): ADR 0009 agregó "Pedir cambios", que
  -- inserta un `approval` 'rechazado' y devuelve la tarea a `en_curso` --
  -- sin este chequeo, una aprobación vieja que no había alcanzado para
  -- cerrar (por ejemplo por un bloqueo abierto)
  -- seguía contando para siempre, y el trabajo corregido podía cerrarse sin
  -- que nadie lo aprobara. Una fila 'aprobado' cuenta sólo si no existe
  -- ningún 'rechazado' del mismo aprobador con `at` posterior o igual: el
  -- empate falla cerrado, nunca aprobado.
  if aprobador is not null
     and not exists (
       select 1 from approval a
        where a.sujeto_tipo = 'tarea' and a.sujeto_id = p_task
          and a.decision = 'aprobado'
          and a.aprobador_membership_id = aprobador
          and not exists (
            select 1 from approval r
             where r.sujeto_tipo = 'tarea' and r.sujeto_id = p_task
               and r.aprobador_membership_id = aprobador
               and r.decision = 'rechazado'
               and r.at >= a.at)) then
    return 'Falta la aprobación de quien revisa ese trabajo.';
  end if;

  return null;
end $$ language plpgsql;

commit;
