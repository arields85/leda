\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0055_los_apodos.sql. A qué entrega pertenece cada pieza (revisión
-- `review-1831155009989b77` de `65086af`; `odd/tasks/fase-c.md`, "Las conversaciones 48 y 49").
--
-- El aviso del retiro de la administración dice qué día se entregó cada pieza retirada, con el
-- reloj de Leda: el del aviso de esa entrega a quien la revisa, cuya clave se ata a la primera
-- pieza del acto (`herramientas._entregar_tarea`). Para encontrarlo, las piezas de un mismo acto
-- se agrupaban por la transacción que las escribió (`xmin`). Después de restaurar un respaldo,
-- todas las filas comparten la misma transacción, y la pieza de una entrega posterior salía con
-- el día de la primera. Ahora cada pieza guarda su entrega (`de_la_entrega`): el id de la
-- primera pieza del acto, ella misma si es la primera o la única. Es un dato de la fila: viaja
-- con el respaldo.
--
-- - La escribe la cocina, en la misma transacción que la pieza (`_insertar_evidencia`).
-- - La entrega es una pieza de la misma tarea y del mismo espacio (clave compuesta; por eso la
--   restricción única nueva sobre `(workspace_id, task_id, id)`).
-- - Las filas de antes quedan nulas: no se sabe a qué acto pertenecían sin la transacción, y no
--   se inventa. Una pieza sin entrega cuenta como su propio acto.
-- - Como el resto de `evidence`, la columna sólo se agrega: `leda_app` no tiene `update` y el
--   disparador `rechazar_cambios_de_evidencia` rechaza cualquier cambio. La RLS forzada y los
--   privilegios de la tabla no cambian.
--
-- Se deshace con `db/rollbacks/0056_la_entrega_de_cada_pieza.sql`, que se niega si una pieza ya
-- dice su entrega.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0056 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0055 está aplicada y la 0056 no.
do $$ begin
  if to_regclass('leda.apodo') is null then
    raise exception '0056 preflight failed: falta la 0055';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'evidence'
                and column_name = 'de_la_entrega') then
    raise exception '0056 ya está aplicada.';
  end if;
end $$;

alter table evidence
  add column de_la_entrega uuid,
  add constraint evidence_tarea_id_unique unique (workspace_id, task_id, id),
  add constraint evidence_de_la_entrega
    foreign key (workspace_id, task_id, de_la_entrega)
    references evidence(workspace_id, task_id, id);

comment on column evidence.de_la_entrega is
  'Migración 0056: la entrega a la que pertenece esta pieza, por el id de la primera pieza del acto (ella misma, si es la primera o la única), de la misma tarea. La escribe la cocina al entregar; viaja con un respaldo, a diferencia de la transacción que la escribió. Nula en las filas de antes de la 0056: la pieza cuenta como su propio acto.';

commit;
