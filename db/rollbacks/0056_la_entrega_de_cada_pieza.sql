\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0056_la_entrega_de_cada_pieza.sql.
--
-- Borra `evidence.de_la_entrega`, su clave y la restricción única que la sostiene. Se niega a
-- correr si una pieza ya dice su entrega: borrarlo perdería a qué acto pertenece, y después de
-- una restauración el día de cada pieza no se podría recuperar. Antes de deshacerla en una base
-- con datos, `pg_dump` de `evidence` y la decisión registrada.
begin;
set search_path = leda, public;
-- La comprobación de abajo tiene que ver todas las filas: sin la RLS. Un rol que no la saltea
-- falla acá en lugar de ver la tabla vacía y borrar lo que no vio.
set local row_security = off;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception 'rollback 0056 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'evidence'
                and column_name = 'de_la_entrega')
     and exists (select 1 from evidence where de_la_entrega is not null) then
    raise exception '0056 rollback refused: hay piezas que dicen a qué entrega pertenecen';
  end if;
end $$;

alter table evidence drop constraint if exists evidence_de_la_entrega;
alter table evidence drop constraint if exists evidence_tarea_id_unique;
alter table evidence drop column if exists de_la_entrega;

commit;
