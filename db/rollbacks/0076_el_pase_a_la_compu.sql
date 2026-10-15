\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0076_el_pase_a_la_compu.sql: borra la función que emite el pase de la computadora. Los
-- pedidos de entrada que dejó quedan como cualquier pedido: vencen al minuto y se purgan con los
-- demás. La web sigue andando sin ella: el lanzador abre la dirección sola, donde se entra con el
-- QR.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0076 rollback requires an unmodified UTF-8 input stream';
  end if;
end $$;

drop function emitir_pase_a_la_compu(text, text, bigint, text, timestamptz, text, text);

commit;
