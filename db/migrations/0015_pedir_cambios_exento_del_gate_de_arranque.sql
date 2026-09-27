\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0014_evidencia_no_sobrevive_a_pedir_cambios.sql. Seguimiento
-- de review-c112506a (`odd/tasks/prisma-orienta.md` T6c): el disparador
-- `exigir_dependencias_resueltas` (0008) rechaza CUALQUIER llegada a
-- `en_curso` con una dependencia bloqueante todavía abierta, salvo la
-- restauración desde `bloqueada`. "Pedir cambios"
-- (`herramientas._pedir_cambios_tarea`) siempre devolvía la tarea a
-- `en_curso` -- con esa dependencia abierta, el insert chocaba con el
-- disparador y el aprobador no podía pedir cambios en absoluto.
--
-- Decisión del usuario (2026-09-27): la tarea vuelve al estado que tenía
-- antes de la ÚLTIMA entrada a `en_revision` -- `en_curso` si estaba en
-- curso (una restauración, exenta del gate igual que salir de `bloqueada`),
-- `asignada` si se entregó sin haber arrancado nunca ("Ya la terminé" se
-- ofrece desde `asignada`). Enmienda la decisión 4 de ADR 0009 ("vuelve a
-- en_curso").
--
-- Agrega `estado_previo_a_revision` (misma puerta angosta que
-- `estado_previo_a_bloqueo`, 0007) y la rama que exime esa restauración en
-- el disparador.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0015 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regprocedure('prisma.exigir_dependencias_resueltas()') is null then
    raise exception '0015 requires 0008_task_start_gate.sql';
  end if;
  if to_regprocedure('prisma.estado_previo_a_revision(uuid)') is not null then
    raise exception '0015 ya está aplicada.';
  end if;
end $$;

-- Misma puerta angosta que `estado_previo_a_bloqueo` (0007), para la
-- ÚLTIMA entrada a `en_revision` en vez de a `bloqueada`. `task_state_event`
-- es append-only y `prisma_app` no lo lee directo; esta función security
-- definer es la única puerta.
create or replace function estado_previo_a_revision(p_task uuid)
returns estado_tarea
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare previo estado_tarea;
begin
  select estado_anterior into previo
    from task_state_event
   where task_id = p_task and estado_nuevo = 'en_revision'
   order by at desc
   limit 1;
  return previo;
end $$;

alter function estado_previo_a_revision(uuid)
  owner to prisma_owner;

revoke execute on function estado_previo_a_revision(uuid) from public;
grant execute on function estado_previo_a_revision(uuid) to prisma_app;

-- No es security definer: mismo motivo que 0008 -- corre con los
-- privilegios de quien inserta, y sólo necesita ejecutar
-- `estado_previo_a_revision` (arriba), no leer `task_state_event` directo.
-- `prisma_app` -- el único rol que hoy hace pasar una tarea a `en_curso`,
-- vía `resolver_bloqueo`, `pedir_cambios_tarea` o `actualizar_estado` -- ya
-- tiene `execute` concedido sobre ella desde la concesión de arriba.
create or replace function exigir_dependencias_resueltas() returns trigger as $$
declare
  motivo text;
  restaura_en_curso boolean := false;
begin
  if new.estado_nuevo = 'en_curso' then
    if new.estado_anterior = 'bloqueada' then
      restaura_en_curso := estado_previo_a_bloqueo(new.task_id) = 'en_curso';
    elsif new.estado_anterior = 'en_revision' then
      restaura_en_curso := estado_previo_a_revision(new.task_id) = 'en_curso';
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

commit;
