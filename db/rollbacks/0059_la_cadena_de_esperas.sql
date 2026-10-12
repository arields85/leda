\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0059_la_cadena_de_esperas.sql.
--
-- Borra las dos funciones de la cadena de esperas de la web. No guardan datos: no se pierde
-- nada. Las de la 0058 no se tocan.
begin;
set search_path = leda, public;

drop function if exists esperas_de_la_sesion(text, text, timestamptz);
drop function if exists esperas_que_ve(uuid, text, timestamptz);

commit;
