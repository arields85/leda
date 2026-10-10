\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0054_la_respuesta_del_bot_de_administracion.sql.
--
-- Borra la marca del enlace y vuelve a hacer obligatorio `admin_notice.incident_id`. Se niega si
-- hay alguna respuesta del bot de administración en la cola: no tiene incidente, y borrarla
-- perdería lo que se le contestó a un administrador. Los accesos ya emitidos (`acceso_tarea`) no
-- se tocan: son de la 0052.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception 'rollback 0054 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if exists (select 1 from admin_notice where es_respuesta) then
    raise exception 'El rollback de la 0054 se niega: hay respuestas del bot de administración en la cola (no tienen incidente).';
  end if;
end $$;

drop table admin_notice_enlace;
alter table admin_notice drop constraint admin_notice_incidente_o_respuesta;
alter table admin_notice drop column es_respuesta;
alter table admin_notice alter column incident_id set not null;

commit;
