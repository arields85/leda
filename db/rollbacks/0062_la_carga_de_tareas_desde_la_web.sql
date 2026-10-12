\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0062_la_carga_de_tareas_desde_la_web.sql.
--
-- Borra `cargar_tarea`, `opciones_de_la_carga`, `es_dia_habil` y `carga_de_tarea`. Se niega a
-- correr si eso perdiera datos: una clave de carga guardada (sin ella, un formulario reenviado
-- volvería a cargar la misma tarea, y se perdería qué clave cargó cada una). Las tareas cargadas,
-- sus eventos y lo que quedó en `audit_log` no se tocan. Antes de correrlo en una base con datos,
-- `pg_dump` de esa tabla y vaciarla a mano, con la decisión registrada.
begin;
set search_path = leda, public;

do $$ begin
  if to_regclass('leda.carga_de_tarea') is not null
     and exists (select 1 from carga_de_tarea) then
    raise exception '0062 rollback refused: hay claves de tareas cargadas desde la web';
  end if;
end $$;

drop function if exists cargar_tarea(text, uuid, uuid, text, text, uuid, date, text, text[],
                                     uuid, text, timestamptz);
drop function if exists opciones_de_la_carga(text, uuid, timestamptz);
drop function if exists es_dia_habil(uuid, date);

drop table if exists carga_de_tarea;

commit;
