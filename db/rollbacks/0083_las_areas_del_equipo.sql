\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0083_las_areas_del_equipo.sql: borra las funciones de las áreas desde la web. Sólo
-- funciones: las áreas creadas, renombradas o archivadas y sus cambios del equipo quedan.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0083 rollback requires an unmodified UTF-8 input stream';
  end if;
end $$;

drop function if exists opciones_de_areas(text, text, uuid);
drop function if exists archivar_area(text, text, uuid, uuid, text, text);
drop function if exists renombrar_area(text, text, uuid, uuid, text, text, text);
drop function if exists crear_area(text, text, uuid, text, text, uuid, text[], boolean, text, text);
drop function if exists confirmar_cambio_de_area(text, text, uuid, text, jsonb, text, text);
drop function if exists vista_previa_de_area(text, text, uuid, text, jsonb);
drop function if exists cambiar_un_area(uuid, text, jsonb, text);
drop function if exists tipos_de_evidencia_del_espacio(uuid);

commit;
