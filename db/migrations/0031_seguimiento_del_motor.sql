\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0030_conversacion_del_motor.sql. El Motor, prueba chica, tarea E2-1
-- (`odd/tasks/prueba-chica-del-motor.md`, sección 5; ADR 0018, decisión 9).
--
-- Los hechos del seguimiento que el motor anota y la entrada de sus mensajes:
--
-- - `task_forecast`: las previsiones de una tarea (9b, 9f). Sólo se agregan; una
--   corrección es una fila nueva que reemplaza a otra. Su espacio no lo declara quien
--   escribe: lo deriva de la tarea `derivar_espacio_prevision()`, con los privilegios
--   de quien llama (como `derivar_espacio_evento_tarea()`): una tarea de otro espacio
--   falla igual que una inventada.
-- - `blocker_unblocker`: quién destraba un bloqueo (9c; ADR 0017, decisión 3a):
--   exactamente uno de un integrante, alguien de afuera o "no sabe". Sólo se agrega.
--   `blocker` gana una restricción única `(workspace_id, id)` para la clave foránea
--   con el espacio.
-- - El aviso previo (9b) es el ajuste `aviso_previo_dias_habiles` de cada espacio en
--   `workspace_setting`: un entero de al menos 1 (mecánica §9). El valor de cada
--   espacio no lo pone esta migración (en CoreWork, 3; se carga al preparar la base).
-- - Ejecución única de un mensaje repetido: `inbound_message.telegram_bot_id` y un
--   índice único por espacio, bot, chat y mensaje de Telegram. El número de mensaje
--   es único dentro de una conversación con un bot, así que sin el bot la clave no es
--   la identidad del mensaje. Los flujos congelados no informan el bot y siguen como
--   antes (su recibo repetido pasada la cota de reentrega es deliberado,
--   `gateway._estado_de_entrega`); las filas existentes quedan con el bot nulo, así
--   que ninguna choca con el índice.
--
-- Se deshace con `db/rollbacks/0031_seguimiento_del_motor.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0031 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('leda.conversation_turn') is null then
    raise exception '0031 requires 0030_conversacion_del_motor.sql';
  end if;
  if to_regclass('leda.task_forecast') is not null then
    raise exception '0031 ya está aplicada.';
  end if;
  -- Un valor previo de la clave nueva que no cumpla el mínimo aborta antes del DDL.
  if exists (
      select 1 from workspace_setting
       where clave = 'aviso_previo_dias_habiles'
         and not case
               when jsonb_typeof(valor) <> 'number' then false
               else (valor #>> '{}')::numeric >= 1 and (valor #>> '{}')::numeric % 1 = 0
             end) then
    raise exception '0031 preflight failed: aviso_previo_dias_habiles inválido en workspace_setting';
  end if;
end $$;

alter table blocker
  add constraint blocker_workspace_id_unique unique (workspace_id, id);

create table task_forecast (
  id                       uuid primary key default gen_random_uuid(),
  workspace_id             uuid not null references workspace(id) on delete cascade,
  task_id                  uuid not null references task(id) on delete cascade,
  fecha_prevista           date not null,
  motivo                   text,
  fecha_comprometida       timestamptz not null,
  atraso_dias_habiles      integer not null,
  reemplaza_id             uuid,
  es_correccion            boolean not null default false,
  dicho_por_membership_id  uuid not null,
  at                       timestamptz not null,
  constraint task_forecast_workspace_id_unique unique (workspace_id, id),
  constraint task_forecast_replaces_workspace
    foreign key (workspace_id, reemplaza_id)
    references task_forecast(workspace_id, id),
  constraint task_forecast_member
    foreign key (dicho_por_membership_id)
    references membership(id) on delete cascade
);

create index task_forecast_de on task_forecast (task_id, at desc);

create table blocker_unblocker (
  id                       uuid primary key default gen_random_uuid(),
  workspace_id             uuid not null references workspace(id) on delete cascade,
  blocker_id               uuid not null,
  destraba_membership_id   uuid,
  destraba_externo         text check (btrim(destraba_externo) <> ''),
  no_sabe                  boolean not null default false,
  dicho_por_membership_id  uuid not null,
  at                       timestamptz not null,
  constraint blocker_unblocker_blocker_workspace
    foreign key (workspace_id, blocker_id)
    references blocker(workspace_id, id) on delete cascade,
  constraint blocker_unblocker_member
    foreign key (destraba_membership_id)
    references membership(id) on delete cascade,
  constraint blocker_unblocker_said_by
    foreign key (dicho_por_membership_id)
    references membership(id) on delete cascade,
  constraint blocker_unblocker_exactamente_uno check (
    (destraba_membership_id is not null)::int
    + (destraba_externo is not null)::int
    + no_sabe::int = 1)
);

create index blocker_unblocker_de on blocker_unblocker (blocker_id, at desc);

comment on table task_forecast is
  'El Motor (ADR 0018, 9b y 9f): las previsiones de una tarea. Sólo se agregan; una corrección reemplaza a otra con una fila nueva. El atraso lo calcula el código en días hábiles del espacio.';
comment on table blocker_unblocker is
  'El Motor (ADR 0018, 9c): quién destraba un bloqueo -- un integrante, alguien de afuera o que no se sabe, exactamente uno --, quién lo dijo y cuándo. Sólo se agrega.';

create or replace function derivar_espacio_prevision() returns trigger as $$
begin
  select t.workspace_id into new.workspace_id
    from task t where t.id = new.task_id;
  if new.workspace_id is null then
    raise exception 'task_forecast: la tarea referida no existe';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_derivar_espacio_prevision
  before insert on task_forecast
  for each row execute function derivar_espacio_prevision();

-- Después de `trg_derivar_espacio_prevision`: los disparadores corren por orden de
-- nombre, así que el espacio ya está derivado de la tarea cuando se comprueba.
create trigger trg_exigir_referencias_del_espacio
  before insert or update on task_forecast
  for each row execute function exigir_referencias_del_espacio(
    'dicho_por_membership_id', 'membership');
create trigger trg_exigir_referencias_del_espacio
  before insert or update on blocker_unblocker
  for each row execute function exigir_referencias_del_espacio(
    'destraba_membership_id', 'membership', 'dicho_por_membership_id', 'membership');

grant all privileges on task_forecast, blocker_unblocker to leda_owner, leda_admin;

do $$
declare t text;
begin
  foreach t in array array['task_forecast', 'blocker_unblocker']
  loop
    execute format('alter table %I enable row level security', t);
    execute format('alter table %I force row level security', t);
    execute format($f$
      create policy aislamiento_espacio on %I
        using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid)
    $f$, t);
    execute format('grant select, insert, update, delete on %I to leda_app', t);
  end loop;
end $$;

revoke update, delete on task_forecast, blocker_unblocker from leda_app;

alter table workspace_setting
  add constraint workspace_setting_aviso_previo check (
    case
      when clave <> 'aviso_previo_dias_habiles' then true
      when jsonb_typeof(valor) <> 'number' then false
      else (valor #>> '{}')::numeric >= 1 and (valor #>> '{}')::numeric % 1 = 0
    end);

alter table inbound_message add column telegram_bot_id bigint;

create unique index inbound_message_unico_por_mensaje
  on inbound_message (workspace_id, telegram_bot_id, chat_id, telegram_message_id)
  where telegram_bot_id is not null and telegram_message_id is not null;

comment on column inbound_message.telegram_bot_id is
  'El Motor (E2-1): el bot que recibió el mensaje. Con él, el índice inbound_message_unico_por_mensaje hace que un mensaje de Telegram repetido se reciba una sola vez. Nulo en los flujos congelados.';

commit;
