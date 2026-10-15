\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0077_el_cambio_de_fecha.sql. Una base migrada desde el principio converge a la
-- matriz de privilegios de la instalación limpia (`db/esquema.sql`): T8 de
-- `odd/tasks/aislamiento-entre-clientes.md`. El ensayo sobre un clúster limpio (T6) encontró tres
-- diferencias, todas de roles sin login o con `bypassrls`; ninguna toca a `leda_app` ni a
-- `leda_gateway`. En las tres vale lo de la instalación limpia, que sigue la regla del resto del
-- esquema:
--
-- - `admin_notice_enlace` (migración 0054): `leda_owner` tiene todos los privilegios sobre todas
--   las tablas del esquema (`grant all privileges on all tables in schema leda to leda_owner`);
--   la 0054 se los dio sólo a `leda_admin` y el `grant` general de la 0004 corrió antes de que la
--   tabla existiera.
-- - `greeting_state` (migración 0018): `leda_admin` tiene todos los privilegios sobre todas las
--   tablas (`grant all on all tables in schema leda to leda_admin`); la 0018 se los dio a
--   `leda_owner` y a `leda_app`, no a `leda_admin`.
-- - la vista `integrante`: ninguna función de `leda_owner` la lee, y en la instalación limpia no
--   tiene privilegios suyos (se crea después del `grant` general). En la migrada los recibió del
--   `grant` general de la 0004, que corrió con la vista ya creada: se le quitan (menor privilegio).
--
-- Concesiones y revocaciones idempotentes: en una base creada desde `esquema.sql` no cambian nada.
-- Se deshace con `db/rollbacks/0078_la_matriz_de_privilegios_converge.sql`.
begin;
set search_path = leda, public;

-- Preflight: la 0077 está aplicada.
do $$ begin
  if to_regclass('leda.cambio_de_fecha') is null then
    raise exception '0078 preflight failed: falta la 0077';
  end if;
end $$;

grant all privileges on admin_notice_enlace to leda_owner;
grant all privileges on greeting_state to leda_admin;
revoke all privileges on integrante from leda_owner;

commit;
