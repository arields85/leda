\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0030_conversacion_del_motor.sql. Requires 0031 to be reverted first.
--
-- Borra las cinco tablas del motor de conversación (con sus políticas, privilegios e
-- índices), la función que comprueba sus referencias a `membership` e
-- `inbound_message` y las dos restricciones únicas `(workspace_id, id)` que 0030 agregó a
-- `task` y `message_outbox`. Se pierde lo que el motor haya guardado: el estado de
-- cada persona, el registro de turnos, las preguntas y los avisos guardados. Antes de
-- correrlo en una base con datos, `pg_dump` de esas tablas.
begin;
set search_path = leda, public;

do $$ begin
  if to_regclass('leda.task_forecast') is not null then
    raise exception 'Deshacer primero 0031_seguimiento_del_motor.sql';
  end if;
end $$;

drop table if exists conversation_state;
drop table if exists scheduled_notice;
drop table if exists conversation_turn;
drop table if exists conversation_option;
drop table if exists conversation_question;
drop function if exists exigir_referencias_del_espacio();

alter table message_outbox drop constraint if exists message_outbox_workspace_id_unique;
alter table task drop constraint if exists task_workspace_id_unique;

commit;
