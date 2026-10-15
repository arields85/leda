\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0078_la_matriz_de_privilegios_converge.sql en una base migrada desde el principio: le
-- quita a `leda_owner` los privilegios sobre `admin_notice_enlace` y a `leda_admin` los de
-- `greeting_state`, y le devuelve a `leda_owner` los de la vista `integrante`. En una base creada
-- desde `esquema.sql` no hace falta (la 0078 no le cambió nada) y la dejaría distinta de la
-- instalación limpia.
begin;
set search_path = leda, public;

revoke all privileges on admin_notice_enlace from leda_owner;
revoke all privileges on greeting_state from leda_admin;
grant all privileges on integrante to leda_owner;

commit;
