\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0018_saludo_diario.sql.
--
-- Sólo hay una tabla nueva, sin ninguna función ni columna agregada en otra
-- tabla existente: un `drop table` alcanza, arrastra su política, sus
-- privilegios y su índice implícito (la primary key) con él -- mismo
-- criterio que el rollback de 0011.
begin;
set search_path = prisma, public;

drop table if exists greeting_state;

commit;
