\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0013_aprobacion_no_sobrevive_a_pedir_cambios.sql. Seguimiento
-- de review-c112506a (`odd/tasks/leda-orienta.md` T6b): al volver a
-- entregar después de "Pedir cambios" (`herramientas._pedir_cambios_tarea`,
-- inserta un `approval` 'rechazado' y devuelve la tarea a `en_curso`),
-- `evidencia_pendiente(p_task)` seguía devolviendo `false` porque la
-- evidencia de la PRIMERA entrega todavía existía -- así que
-- `herramientas._actualizar_estado` descartaba en silencio el
-- `evidencia_texto` de la reentrega, aunque la vista previa
-- (`_preparar_actualizar_estado`) y el aviso al aprobador
-- (`_notificar_entrega_al_aprobador`) ya lo mostraban.
--
-- Decisión del usuario (2026-09-27): si se pidieron cambios, la evidencia
-- vieja deja de contar -- hay que volver a mandar evidencia (ejemplo: pintar
-- una pared, al aprobador le faltó una parte, la evidencia nueva muestra esa
-- parte pintada). El cuerpo cambia (`evidencia_pendiente` cuenta sólo
-- evidencia con `at` posterior al último `approval` 'rechazado' de la
-- tarea); la forma de salida no cambia.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0014 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regprocedure('leda.motivo_no_cierra_tarea(uuid)') is null
     or pg_get_functiondef('leda.motivo_no_cierra_tarea(uuid)'::regprocedure)
        not like '%r.decision = ''rechazado''%' then
    raise exception '0014 requires 0013_aprobacion_no_sobrevive_a_pedir_cambios.sql';
  end if;
  if pg_get_functiondef('leda.evidencia_pendiente(uuid)'::regprocedure)
     like '%decision = ''rechazado''%' then
    raise exception '0014 ya está aplicada.';
  end if;
end $$;

-- No es security definer: corre con los privilegios de quien llama, igual
-- que antes de esta migración -- `evidence` y `approval` ya tienen `select`
-- concedido a `leda_app` desde el esquema base, así que no hace falta
-- ninguna concesión nueva.
create or replace function evidencia_pendiente(p_task uuid)
returns boolean as $$
  select array_length(t.evidencia_requerida, 1) is not null
     and not exists (
       select 1 from evidence e
        where e.task_id = t.id
          and e.at > coalesce(
            (select max(r.at) from approval r
              where r.sujeto_tipo = 'tarea' and r.sujeto_id = t.id
                and r.decision = 'rechazado'),
            '-infinity'::timestamptz))
    from task t where t.id = p_task;
$$ language sql stable;

commit;
