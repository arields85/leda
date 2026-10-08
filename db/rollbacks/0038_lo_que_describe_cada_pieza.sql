\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0038_lo_que_describe_cada_pieza.sql.
--
-- Borra `evidence.describe_del_criterio` y su restricción. Se niega a correr si una pieza ya dice
-- qué describe del criterio de aceptación: borrarlo perdería lo que la persona confirmó al
-- entregar, y una entrega a la que después se le retire un texto ya no sabría qué le falta. Antes
-- de deshacerla en una base con datos, `pg_dump` de `evidence` y la decisión registrada.
begin;
set search_path = leda, public;
-- La comprobación de abajo tiene que ver todas las filas: sin la RLS. Un rol que no la saltea
-- falla acá en lugar de ver la tabla vacía y borrar lo que no vio.
set local row_security = off;

do $$ begin
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'evidence'
                and column_name = 'describe_del_criterio')
     and exists (select 1 from evidence where describe_del_criterio <> '{}') then
    raise exception '0038 rollback refused: hay piezas que dicen qué describen del criterio de aceptación';
  end if;
end $$;

alter table evidence drop constraint if exists evidence_describe_solo_un_texto;
alter table evidence drop column if exists describe_del_criterio;

commit;
