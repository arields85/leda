\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0037_funciones_elevadas_con_camino_fijo.sql.
--
-- Vuelve el camino de las dos funciones al de antes (`resolver_pendiente` sin camino fijo;
-- `aplicar_evento_tarea` con `leda, public`) y su `execute` al de omisión, para `public`.
--
-- El privilegio de omisión no se recupera con `grant`: una vez que una función tiene una lista
-- de privilegios explícita, devolverle `execute` a `public` la deja explícita, distinta de la de
-- antes. Por eso cada función se vuelve a crear desde su propia definición (con el cuerpo
-- intacto, tomado del catálogo), con su dueño, su comentario y los disparadores que la usan.
-- Vuelve a abrir el hueco que la 0037 cerró: sólo para volver atrás una base de prueba.
begin;
set search_path = leda, public;

do $$
declare
  f record;
  firma text;
  definicion text;
  comentario text;
  disparadores text[];
  d text;
begin
  for f in select * from (values
             ('leda.resolver_pendiente(text,uuid,timestamptz)'::regprocedure, null::text),
             ('leda.aplicar_evento_tarea()'::regprocedure, 'leda, public')) as v(fn, camino)
  loop
    firma := f.fn::text;
    if f.camino is null then
      execute format('alter function %s reset search_path', firma);
    else
      execute format('alter function %s set search_path = %s', firma, f.camino);
    end if;
    definicion := pg_get_functiondef(f.fn);
    comentario := obj_description(f.fn, 'pg_proc');
    select coalesce(array_agg(pg_get_triggerdef(t.oid) order by t.tgname), '{}')
      into disparadores
      from pg_trigger t where t.tgfoid = f.fn and not t.tgisinternal;
    execute format('drop function %s cascade', firma);
    execute definicion;
    execute format('alter function %s owner to leda_owner', firma);
    if comentario is not null then
      execute format('comment on function %s is %L', firma, comentario);
    end if;
    foreach d in array disparadores loop
      execute d;
    end loop;
  end loop;
end $$;

commit;
