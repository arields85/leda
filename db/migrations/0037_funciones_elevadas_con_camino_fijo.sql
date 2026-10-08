\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0036_pagina_de_la_tarea.sql. Las funciones elevadas fijan su camino y no las
-- ejecuta cualquiera (impugnación de seguridad de la porción 4 de la C-3, 2026-10-08).
--
-- Una función `security definer` corre con los privilegios de su dueño (`leda_owner`). Dos de
-- ellas no cumplían la regla que cumplen las demás:
--
-- - `resolver_pendiente(text, uuid, timestamptz)` no fijaba `search_path`: resolvía los nombres
--   sin esquema con el camino de quien la llama. `leda_app` puede crear tablas temporales, y una
--   tabla temporal con el nombre de una que la función usa la reemplazaría adentro.
-- - `aplicar_evento_tarea()` lo fijaba sin nombrar `pg_temp`, y Postgres busca las tablas
--   temporales antes que todo lo que el camino nombra salvo que se lo ponga explícitamente: el
--   `update task` del disparador podía caer en una tabla temporal `task` de quien inserta el
--   evento.
-- - Las dos conservaban el `execute` que Postgres da a `public` al crear una función. Se le
--   quita a `public` y se le da sólo a quien la llama hoy: `resolver_pendiente`, a `leda_app`
--   (`pendientes.resolver`, con `db.espacio`); `aplicar_evento_tarea` es un disparador, que corre
--   sin que nadie la llame y no necesita `execute` de nadie.
--
-- La regla general la prueba `tests/garantias/test_aislamiento.py`: toda función `security
-- definer` del esquema `leda` fija `search_path` con `pg_temp` al final y no la ejecuta
-- `public`. Los cuerpos no cambian.
--
-- Se deshace con `db/rollbacks/0037_funciones_elevadas_con_camino_fijo.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0037 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: las dos funciones existen con su firma y son de `leda_owner`. Una función
-- renombrada quedaría sin la regla en silencio.
do $$
declare faltantes text := '';
begin
  if to_regprocedure('leda.resolver_pendiente(text,uuid,timestamptz)') is null
    then faltantes := faltantes || ' resolver_pendiente'; end if;
  if to_regprocedure('leda.aplicar_evento_tarea()') is null
    then faltantes := faltantes || ' aplicar_evento_tarea'; end if;
  if faltantes <> '' then
    raise exception '0037 preflight failed: faltan las funciones%', faltantes;
  end if;
  if exists (select 1 from pg_proc p join pg_roles r on r.oid = p.proowner
              where p.oid in ('leda.resolver_pendiente(text,uuid,timestamptz)'::regprocedure,
                              'leda.aplicar_evento_tarea()'::regprocedure)
                and r.rolname <> 'leda_owner') then
    raise exception '0037 preflight failed: las funciones tienen que ser de leda_owner';
  end if;
end $$;

alter function resolver_pendiente(text, uuid, timestamptz)
  set search_path = leda, public, pg_temp;
alter function aplicar_evento_tarea()
  set search_path = leda, public, pg_temp;

revoke execute on function resolver_pendiente(text, uuid, timestamptz) from public;
grant execute on function resolver_pendiente(text, uuid, timestamptz) to leda_app;
revoke execute on function aplicar_evento_tarea() from public;

commit;
