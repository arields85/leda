\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0025_rechazar_borrador.sql (0026 to 0029 belong to the frozen branch;
-- `db/migrations/README.md`). El Motor, prueba chica, tarea E2-1
-- (`odd/tasks/prueba-chica-del-motor.md`, sección 5; ADR 0018, decisiones 3 y 8).
--
-- Lo que guarda el motor de conversación: las preguntas de Leda y sus opciones, los
-- avisos guardados como hechos (`scheduled_notice`, precisión del 2026-10-05 a la
-- decisión 8), el estado de cada persona y el registro de turnos.
--
-- - Toda tabla lleva `workspace_id`, RLS forzado y la política de aislamiento de las
--   demás; ninguna lleva `chat_id` ni `callback_data` (reglas 1 a 3 de
--   `docs/architecture/frontera.md`).
-- - Toda referencia es al mismo espacio: la comprobación de una clave foránea no pasa
--   por la RLS, así que sin eso una fila propia podría apuntar a algo de otro cliente.
--   Las referencias entre tablas nuevas, a `task` y a `message_outbox` llevan el
--   espacio en la clave foránea (patrón de `pending_action`; `task` y `message_outbox`
--   ganan una restricción única `(workspace_id, id)`). Las de `membership` e
--   `inbound_message` las comprueba `exigir_referencias_del_espacio()`, porque su
--   restricción `(workspace_id, id)` es de la 0002 y volver atrás la 0002 tiene que
--   seguir siendo posible.
-- - Los momentos no tienen valor por omisión: los pone el motor con su reloj.
-- - El registro de turnos sólo se agrega: `leda_app` lo lee y lo escribe, nunca lo
--   cambia ni lo borra (como `task_state_event`). Preguntas, opciones y avisos se
--   cierran con un `update`, pero no se borran: son la historia de la conversación.
-- - Una sola función nueva, de disparador y sin `security definer`.
--
-- Se deshace con `db/rollbacks/0030_conversacion_del_motor.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0030 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (
      select 1 from information_schema.columns
       where table_schema = 'leda' and table_name = 'message_outbox'
         and column_name = 'es_coordinacion') then
    raise exception '0030 requires 0025_rechazar_borrador.sql';
  end if;
  if to_regclass('leda.conversation_turn') is not null then
    raise exception '0030 ya está aplicada.';
  end if;
end $$;

alter table task
  add constraint task_workspace_id_unique unique (workspace_id, id);
alter table message_outbox
  add constraint message_outbox_workspace_id_unique unique (workspace_id, id);

create table conversation_question (
  id                 uuid primary key default gen_random_uuid(),
  workspace_id       uuid not null references workspace(id) on delete cascade,
  membership_id      uuid not null,
  tipo               text not null,
  task_id            uuid,
  jugada             jsonb,
  se_puede_dejar     boolean not null,
  abierta_en         timestamptz not null,
  para_despues_en    timestamptz,
  cerrada_en         timestamptz,
  cierre             text check (cierre in ('respondida', 'cancelada', 'sin_efecto')),
  cierre_detalle     jsonb,
  constraint conversation_question_workspace_id_unique unique (workspace_id, id),
  constraint conversation_question_membership
    foreign key (membership_id)
    references membership(id) on delete cascade,
  constraint conversation_question_task_workspace
    foreign key (workspace_id, task_id)
    references task(workspace_id, id) on delete cascade,
  constraint conversation_question_cierre check ((cerrada_en is null) = (cierre is null))
);

create index conversation_question_abiertas
  on conversation_question (workspace_id, membership_id) where cerrada_en is null;

create table conversation_option (
  id            uuid primary key default gen_random_uuid(),
  workspace_id  uuid not null references workspace(id) on delete cascade,
  question_id   uuid not null,
  token         text not null unique,
  etiqueta      text not null,
  valor         jsonb not null,
  orden         integer not null,
  elegida_en    timestamptz,
  constraint conversation_option_workspace_id_unique unique (workspace_id, id),
  constraint conversation_option_question_workspace
    foreign key (workspace_id, question_id)
    references conversation_question(workspace_id, id) on delete cascade
);

create index conversation_option_de on conversation_option (question_id, orden);

create table conversation_turn (
  id                  uuid primary key default gen_random_uuid(),
  workspace_id        uuid not null references workspace(id) on delete cascade,
  membership_id       uuid not null,
  sentido             text not null check (sentido in ('entrada', 'salida')),
  inbound_message_id  uuid,
  outbox_id           uuid,
  option_id           uuid,
  jugadas             jsonb,
  resultado           jsonb,
  ia                  text,
  latencia_ms         integer check (latencia_ms >= 0),
  error               text,
  at                  timestamptz not null,
  constraint conversation_turn_workspace_id_unique unique (workspace_id, id),
  constraint conversation_turn_membership
    foreign key (membership_id)
    references membership(id) on delete cascade,
  constraint conversation_turn_inbound
    foreign key (inbound_message_id)
    references inbound_message(id) on delete set null,
  constraint conversation_turn_outbox_workspace
    foreign key (workspace_id, outbox_id)
    references message_outbox(workspace_id, id) on delete set null (outbox_id),
  constraint conversation_turn_option_workspace
    foreign key (workspace_id, option_id)
    references conversation_option(workspace_id, id) on delete set null (option_id),
  constraint conversation_turn_sentido check (
    (sentido = 'entrada' and outbox_id is null) or
    (sentido = 'salida' and inbound_message_id is null and option_id is null))
);

create index conversation_turn_por_persona
  on conversation_turn (workspace_id, membership_id, at desc);

create table scheduled_notice (
  id                          uuid primary key default gen_random_uuid(),
  workspace_id                uuid not null references workspace(id) on delete cascade,
  tipo                        text not null,
  task_id                     uuid,
  destinatario_membership_id  uuid not null,
  turno_id                    uuid,
  hechos                      jsonb not null,
  programado_para             timestamptz not null,
  estado                      text not null default 'guardado'
                              check (estado in ('guardado', 'enviado', 'omitido', 'fallido')),
  intentos                    integer not null default 0 check (intentos >= 0),
  proximo_intento_en          timestamptz,
  motivo_omision              text,
  outbox_id                   uuid,
  dedupe_key                  text not null,
  creado_en                   timestamptz not null,
  resuelto_en                 timestamptz,
  constraint scheduled_notice_workspace_id_unique unique (workspace_id, id),
  constraint scheduled_notice_dedupe unique (workspace_id, dedupe_key),
  constraint scheduled_notice_task_workspace
    foreign key (workspace_id, task_id)
    references task(workspace_id, id) on delete cascade,
  constraint scheduled_notice_recipient
    foreign key (destinatario_membership_id)
    references membership(id) on delete cascade,
  constraint scheduled_notice_turn_workspace
    foreign key (workspace_id, turno_id)
    references conversation_turn(workspace_id, id) on delete set null (turno_id),
  constraint scheduled_notice_outbox_workspace
    foreign key (workspace_id, outbox_id)
    references message_outbox(workspace_id, id) on delete set null (outbox_id),
  constraint scheduled_notice_resuelto check ((estado = 'guardado') = (resuelto_en is null)),
  constraint scheduled_notice_omision check (estado <> 'omitido' or motivo_omision is not null)
);

create index scheduled_notice_por_salir
  on scheduled_notice (workspace_id, programado_para) where estado = 'guardado';

create table conversation_state (
  membership_id            uuid primary key,
  workspace_id             uuid not null references workspace(id) on delete cascade,
  pregunta_abierta_id      uuid,
  ultimo_aviso_id          uuid,
  mostrado_para_confirmar  jsonb,
  huella                   text,
  actualizado_en           timestamptz not null,
  constraint conversation_state_membership
    foreign key (membership_id)
    references membership(id) on delete cascade,
  constraint conversation_state_question_workspace
    foreign key (workspace_id, pregunta_abierta_id)
    references conversation_question(workspace_id, id)
    on delete set null (pregunta_abierta_id),
  constraint conversation_state_notice_workspace
    foreign key (workspace_id, ultimo_aviso_id)
    references scheduled_notice(workspace_id, id) on delete set null (ultimo_aviso_id)
);

comment on table conversation_state is
  'El Motor (ADR 0018, decisión 3.1): una fila por persona. La pregunta abierta, el último aviso que Leda le mandó (su tarea sale del aviso) y, reservadas, lo mostrado para confirmar y su huella. Los temas para después son las preguntas sin cerrar con para_despues_en.';
comment on table conversation_turn is
  'El Motor (ADR 0018, decisión 3.2): el registro de turnos. Sólo se agrega; se conserva como las conversaciones (ADR 0002).';
comment on table conversation_question is
  'El Motor: las preguntas de Leda. Se cierran con cerrada_en y cierre; una pregunta dejada para después lleva para_despues_en.';
comment on table conversation_option is
  'El Motor: las opciones de una duda (situación general 5). El token es único y es lo que vuelve con un toque.';
comment on table scheduled_notice is
  'El Motor (ADR 0018, decisión 8, precisión del 2026-10-05): lo que Leda manda por su cuenta, guardado como hechos. Entra al outbox recién cuando la IA lo redactó.';

-- Las referencias a `membership` y a `inbound_message` son al mismo espacio. No se
-- declaran como clave foránea con el espacio porque la restricción única
-- `(workspace_id, id)` de esas dos tablas es de la 0002, y volver atrás la 0002
-- dejaría de ser posible (mismo motivo que `message_outbox.entrante_id`). Esta
-- función lo comprueba con los privilegios de quien llama: con la RLS, una fila de
-- otro espacio no se encuentra y falla igual que una inventada; la conexión
-- administrativa, que no tiene RLS, compara el espacio. Recibe pares (columna,
-- tabla) y falla como una clave foránea.
create or replace function exigir_referencias_del_espacio() returns trigger as $$
declare
  fila jsonb := to_jsonb(new);
  valor uuid;
  suyo uuid;
  i integer := 0;
begin
  while i < tg_nargs loop
    valor := (fila ->> tg_argv[i])::uuid;
    if valor is not null then
      execute format('select workspace_id from %I where id = $1', tg_argv[i + 1])
        into suyo using valor;
      if suyo is distinct from new.workspace_id then
        raise exception '%: la referencia de % no existe en este espacio',
          tg_table_name, tg_argv[i] using errcode = 'foreign_key_violation';
      end if;
    end if;
    i := i + 2;
  end loop;
  return new;
end $$ language plpgsql;

create trigger trg_exigir_referencias_del_espacio
  before insert or update on conversation_question
  for each row execute function exigir_referencias_del_espacio(
    'membership_id', 'membership');
create trigger trg_exigir_referencias_del_espacio
  before insert or update on conversation_turn
  for each row execute function exigir_referencias_del_espacio(
    'membership_id', 'membership', 'inbound_message_id', 'inbound_message');
create trigger trg_exigir_referencias_del_espacio
  before insert or update on scheduled_notice
  for each row execute function exigir_referencias_del_espacio(
    'destinatario_membership_id', 'membership');
create trigger trg_exigir_referencias_del_espacio
  before insert or update on conversation_state
  for each row execute function exigir_referencias_del_espacio(
    'membership_id', 'membership');

grant all privileges on conversation_question, conversation_option, conversation_turn,
                        scheduled_notice, conversation_state to leda_owner, leda_admin;

do $$
declare t text;
begin
  foreach t in array array['conversation_question', 'conversation_option',
                           'conversation_turn', 'scheduled_notice',
                           'conversation_state']
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

revoke update, delete on conversation_turn from leda_app;
revoke delete on conversation_question, conversation_option, scheduled_notice from leda_app;

commit;
