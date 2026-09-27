\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0015_pedir_cambios_exento_del_gate_de_arranque.sql.
--
-- Restores `exigir_dependencias_resueltas` a su cuerpo previo -- byte a
-- byte la versión que dejó 0008 (sólo la restauración desde `bloqueada`
-- está exenta del gate de arranque) -- y elimina `estado_previo_a_revision`
-- por completo. Después de este rollback, `herramientas._pedir_cambios_
-- tarea` volvería a fallar contra la base con "function
-- estado_previo_a_revision(uuid) does not exist" -- el mismo defecto que
-- esta migración cierra -- que es la dirección segura para un rollback: no
-- deja el disparador apuntando a una función eliminada, ni una función a
-- medio aplicar.
begin;
set search_path = prisma, public;

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

drop function if exists estado_previo_a_revision(uuid);

commit;
