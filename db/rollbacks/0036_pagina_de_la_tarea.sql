\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0036_pagina_de_la_tarea.sql.
--
-- Borra las funciones de la página, `message_outbox_enlace`, `vista_de_tarea`, `acceso_tarea` y
-- `area.referente_membership_id`. Se niega a correr si eso perdiera datos: un enlace emitido
-- (dejaría de abrir su página sin aviso), una vista registrada (el registro de quién miró no se
-- borra), una fila de la salida que lleva el enlace, o un referente cargado en un área (vuelve con
-- el pack, pero no sin reimportarlo). Antes de correrlo en una base con datos, `pg_dump` de esas
-- tablas y vaciarlas a mano, con la decisión registrada.
begin;
set search_path = leda, public;
-- Las comprobaciones de abajo tienen que ver todas las filas: sin la RLS. Un rol que no la
-- saltea falla acá en lugar de ver las tablas vacías y borrar lo que no vio.
set local row_security = off;

do $$ begin
  if to_regclass('leda.acceso_tarea') is not null and (
       exists (select 1 from acceso_tarea)
       or exists (select 1 from vista_de_tarea)
       or exists (select 1 from message_outbox_enlace)) then
    raise exception '0036 rollback refused: hay enlaces a la página de una tarea, vistas registradas o mensajes que llevan el enlace';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'area'
                and column_name = 'referente_membership_id')
     and exists (select 1 from area where referente_membership_id is not null) then
    raise exception '0036 rollback refused: hay áreas con su referente cargado';
  end if;
end $$;

drop function if exists leer_archivo_de_tarea(text, uuid);
drop function if exists leer_pagina_de_tarea(text);
drop function if exists acceso_tarea_vigente(text);
drop function if exists emitir_acceso_tarea(uuid, uuid, text);
drop function if exists puede_ver_tarea(uuid, uuid);

drop table if exists message_outbox_enlace;
drop table if exists vista_de_tarea;
drop table if exists acceso_tarea;

alter table area drop constraint if exists area_referente;
alter table area drop column if exists referente_membership_id;

commit;
