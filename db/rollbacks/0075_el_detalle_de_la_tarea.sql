\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0075_el_detalle_de_la_tarea.sql: borra la función que suma al detalle de una tarea quién
-- la pidió, lo que espera y lo que la espera. No toca datos. La web sigue andando sin ella: la
-- página de la tarea sale sin esas tres cosas (`pagina_de_tarea.leer`).
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0075 rollback requires an unmodified UTF-8 input stream';
  end if;
end $$;

drop function relaciones_de_la_pagina_de_tarea(text);

commit;
