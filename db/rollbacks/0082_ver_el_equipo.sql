\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0082_ver_el_equipo.sql: borra `equipo_de`, `cambios_del_equipo` y
-- `quien_organiza_el_equipo`. Sólo funciones: no se pierde ningún dato.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0082 rollback requires an unmodified UTF-8 input stream';
  end if;
end $$;

drop function if exists cambios_del_equipo(text, text, uuid);
drop function if exists equipo_de(text, text, uuid);
drop function if exists quien_organiza_el_equipo(text, text, uuid);

commit;
