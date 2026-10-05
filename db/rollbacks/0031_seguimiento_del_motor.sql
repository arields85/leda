\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0031_seguimiento_del_motor.sql.
--
-- Borra `task_forecast` (con su disparador y su función) y `blocker_unblocker`, la
-- restricción única `(workspace_id, id)` de `blocker`, el mínimo del aviso previo en
-- `workspace_setting` (las filas de esa clave quedan) y `inbound_message.telegram_bot_id`
-- con su índice único: sin él, un mensaje repetido del motor vuelve a poder entrar dos
-- veces. Se pierden las previsiones y quién destraba cada bloqueo: antes de correrlo en
-- una base con datos, `pg_dump` de esas tablas.
begin;
set search_path = leda, public;

drop index if exists inbound_message_unico_por_mensaje;
alter table inbound_message drop column if exists telegram_bot_id;

alter table workspace_setting drop constraint if exists workspace_setting_aviso_previo;

drop table if exists blocker_unblocker;
drop table if exists task_forecast;
drop function if exists derivar_espacio_prevision();

alter table blocker drop constraint if exists blocker_workspace_id_unique;

commit;
