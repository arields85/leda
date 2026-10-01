\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0026_borrador_enviado_no_es_rama_abierta.sql.
--
-- Quita la columna y devuelve el índice único a su definición de 0002 (una
-- solicitud `active` por persona y chat). Antes de correrlo, sin una persona con
-- una solicitud enviada a aprobación y otra `active` a la vez: el índice no se
-- podría crear y el rollback abortaría sin tocar nada.
begin;
set search_path = prisma, public;

drop index if exists task_intake_one_active;
alter table task_intake_request drop column if exists enviada_en;
create unique index task_intake_one_active
  on task_intake_request (workspace_id, membership_id, chat_id)
  where estado = 'active';

commit;
