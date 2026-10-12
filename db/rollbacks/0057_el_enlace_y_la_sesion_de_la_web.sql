\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0057_el_enlace_y_la_sesion_de_la_web.sql.
--
-- Borra las funciones del enlace y de la sesión, `sesion_web` y `enlace_de_entrada`. Se niega a
-- correr si eso perdiera datos: un enlace emitido (dejaría de abrir sin aviso) o una sesión (la
-- persona quedaría afuera sin saber por qué, y se perdería cuándo se abrió, se usó y se cortó).
-- Lo que quedó en `audit_log` no se toca. Antes de correrlo en una base con datos, `pg_dump` de
-- esas tablas y vaciarlas a mano, con la decisión registrada.
begin;
set search_path = leda, public;
-- Las comprobaciones de abajo tienen que ver todas las filas: sin la RLS. Un rol que no la
-- saltea falla acá en lugar de ver las tablas vacías y borrar lo que no vio.
set local row_security = off;

do $$ begin
  if to_regclass('leda.enlace_de_entrada') is not null and (
       exists (select 1 from enlace_de_entrada)
       or exists (select 1 from sesion_web)) then
    raise exception '0057 rollback refused: hay enlaces de entrada emitidos o sesiones de la web';
  end if;
end $$;

drop function if exists cortar_sesiones_de_membresia(uuid, text, uuid);
drop function if exists cortar_sesion(uuid, text, uuid);
drop function if exists sesion_vigente(text);
drop function if exists canjear_enlace_de_entrada(text, text);
drop function if exists emitir_enlace_de_entrada(uuid, text, uuid);
drop function if exists auditar_acceso_web(uuid, uuid, tipo_actor, text, text, uuid, jsonb);

drop table if exists sesion_web;
drop table if exists enlace_de_entrada;

commit;
