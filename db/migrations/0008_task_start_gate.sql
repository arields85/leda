\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0007_blocker_resolution.sql. Adds the gate that mecánica §4
-- names and no code enforced: the destino of a `bloqueante` dependency could
-- not pass to `en_curso` until the origen was `terminada`, and nothing in the
-- database or the application stopped it. `dependency`,
-- `evitar_ciclo_dependencia` and `motivo_no_cierra_tarea` (the closing-time
-- check for the same rule) already existed; this adds the matching
-- starting-time check.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0008 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regprocedure('prisma.estado_previo_a_bloqueo(uuid)') is null then
    raise exception '0008 requires 0007_blocker_resolution.sql';
  end if;
end $$;

-- No es security definer: corre con los privilegios de quien llama, igual
-- que `motivo_no_cierra_tarea`. `task` y `dependency` ya tienen select
-- concedido a `prisma_app` desde el bucle de aislamiento del esquema base,
-- así que no hace falta ninguna concesión nueva.
--
-- `cancelada` libera el freno igual que `terminada`, con el mismo criterio
-- que `motivo_no_cierra_tarea` usa para las dependencias bloqueantes
-- abiertas: una origen cancelada nunca va a terminar, y tratarla como
-- abierta bloquearía la destino para siempre.
--
-- Corrección tras revisión: el freno es para ARRANCAR, no para volver de un
-- bloqueo. Mecánica §3 dice que salir de `bloqueada` devuelve la tarea al
-- estado que tenía antes -- es una restauración, no un arranque nuevo -- y
-- ese estado previo ya había pasado (o no necesitaba pasar) este mismo
-- chequeo la primera vez. Sin esta excepción, bloquear una tarea que ya
-- estaba `en_curso` con una dependencia bloqueante todavía abierta (algo que
-- T1 permite a propósito, sin mover la tarea retroactivamente) volvía
-- irresoluble el bloqueo: `resolver_bloqueo` intenta el insert `bloqueada ->
-- en_curso` y el disparador lo rechazaba, dejando el bloqueo abierto para
-- siempre.
--
-- Segunda corrección tras revisión: eximir por `new.estado_anterior =
-- 'bloqueada'` solo era demasiado amplio -- dejaba pasar una tarea que
-- NUNCA había arrancado: `asignada` -> `registrar_bloqueo` -> `bloqueada` ->
-- `actualizar_estado(en_curso)` quedaba exenta igual, exactamente lo que
-- mecánica §4 prohíbe. La restauración legítima es más angosta: sólo
-- cuando el estado anterior a la ÚLTIMA entrada a `bloqueada` -- no el
-- evento inmediatamente anterior a este, sino el que tenía la tarea justo
-- antes de bloquearse -- era `en_curso`. Por eso se consulta
-- `estado_previo_a_bloqueo` (0007, preflight arriba), no `new.estado_anterior`
-- a secas.
create or replace function motivo_no_arranca_tarea(p_task uuid)
returns text as $$
declare
  dep_abiertas integer;
begin
  if not exists (select 1 from task where id = p_task) then
    return 'La tarea no existe.';
  end if;

  select count(*) into dep_abiertas
    from dependency d join task o on o.id = d.origen_task_id
   where d.destino_task_id = p_task
     and d.tipo = 'bloqueante'
     and o.estado not in ('terminada', 'cancelada');
  if dep_abiertas > 0 then
    return format('Quedan %s dependencias bloqueantes sin resolver.', dep_abiertas);
  end if;

  return null;
end $$ language plpgsql;

-- No es security definer: corre con los privilegios de quien inserta. Sólo
-- necesita ejecutar `estado_previo_a_bloqueo` cuando la transición realmente
-- sale de `bloqueada`; `prisma_app` -- el único rol que hoy hace pasar una
-- tarea a `en_curso`, vía `resolver_bloqueo` o `actualizar_estado` -- ya
-- tiene `execute` concedido sobre ella desde 0007.
create or replace function exigir_dependencias_resueltas() returns trigger as $$
declare
  motivo text;
  restaura_en_curso boolean := false;
begin
  if new.estado_nuevo = 'en_curso' then
    if new.estado_anterior = 'bloqueada' then
      restaura_en_curso := estado_previo_a_bloqueo(new.task_id) = 'en_curso';
    end if;
    if not restaura_en_curso then
      motivo := motivo_no_arranca_tarea(new.task_id);
      if motivo is not null then
        raise exception 'No se puede pasar la tarea a en curso: %', motivo;
      end if;
    end if;
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_exigir_dependencias_resueltas
  before insert on task_state_event
  for each row execute function exigir_dependencias_resueltas();

commit;
