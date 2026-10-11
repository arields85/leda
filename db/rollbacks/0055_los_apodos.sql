\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0055_los_apodos.sql.
--
-- Borra los apodos y su disparador. Se niega si hay alguno, vigente o dejado de usar: borrarlo
-- perdería quién lo enseñó y cuándo, que es auditoría (constitución §12).
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception 'rollback 0055 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if exists (select 1 from apodo) then
    raise exception 'El rollback de la 0055 se niega: hay apodos aprendidos.';
  end if;
end $$;

drop table apodo;
drop function vigilar_apodo();

commit;
