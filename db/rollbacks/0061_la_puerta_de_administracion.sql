\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0061_la_puerta_de_administracion.sql.
--
-- Borra las funciones de la puerta de administración, `sesion_de_administracion` y
-- `enlace_de_administracion`. Se niega a correr si eso perdiera datos: un enlace emitido
-- (dejaría de abrir sin aviso) o una sesión (el administrador quedaría afuera sin saber por qué,
-- y se perdería cuándo se abrió, se usó y se cortó). Lo que quedó en `audit_log` no se toca.
-- Antes de correrlo en una base con datos, `pg_dump` de esas tablas y vaciarlas a mano, con la
-- decisión registrada.
begin;
set search_path = leda, public;

do $$ begin
  if to_regclass('leda.enlace_de_administracion') is not null and (
       exists (select 1 from enlace_de_administracion)
       or exists (select 1 from sesion_de_administracion)) then
    raise exception '0061 rollback refused: hay enlaces o sesiones de la puerta de administración';
  end if;
end $$;

drop function if exists cortar_sesiones_de_administrador(uuid, text, uuid);
drop function if exists cerrar_sesion_de_administracion(text);
drop function if exists sesion_de_administracion_vigente(text);
drop function if exists canjear_enlace_de_administracion(text, text);
drop function if exists emitir_enlace_de_administracion(uuid, text, uuid);
drop function if exists es_administrador_de_plataforma(uuid);
drop function if exists auditar_acceso_de_administracion(uuid, tipo_actor, text, text, uuid, jsonb);

drop table if exists sesion_de_administracion;
drop table if exists enlace_de_administracion;

commit;
