\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0032_borrar_el_alta_guiada.sql.
--
-- Vuelve a crear las cinco tablas `task_intake_*` como las dejó la 0002 (vacías: lo que
-- tenían antes de la 0032 no vuelve), con su aislamiento y sus privilegios;
-- `message_outbox.intake_choice_set_id` con sus claves foráneas y su rama del límite de
-- texto, y `confirmar_borrador_tarea()` con lo que cerraba la solicitud del alta.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception 'rollback of 0032 requires an unmodified UTF-8 input stream';
  end if;
end $$;

create table task_intake_request (
  id                    uuid primary key default gen_random_uuid(),
  workspace_id          uuid not null references workspace(id) on delete cascade,
  membership_id         uuid not null,
  chat_id               bigint not null check (chat_id > 0),
  task_draft_id         uuid not null unique,
  estado                text not null default 'active'
                        check (estado in ('active', 'cancelled', 'converted')),
  version               integer not null default 1 check (version > 0),
  source_inbound_id     uuid not null,
  source_raw_text       text not null,
  terminal_result       jsonb,
  creado_en             timestamptz not null default now(),
  actualizado_en        timestamptz not null default now(),
  constraint task_intake_request_workspace_id_unique unique (workspace_id, id),
  constraint task_intake_request_membership_workspace
    foreign key (workspace_id, membership_id)
    references membership(workspace_id, id) on delete cascade,
  constraint task_intake_request_draft_workspace
    foreign key (workspace_id, task_draft_id)
    references task_draft(workspace_id, id),
  constraint task_intake_request_source_workspace_chat
    foreign key (workspace_id, source_inbound_id, chat_id)
    references inbound_message(workspace_id, id, chat_id)
);

create unique index task_intake_one_active
  on task_intake_request (workspace_id, membership_id, chat_id)
  where estado = 'active';

create table task_intake_field (
  request_id          uuid not null,
  workspace_id        uuid not null references workspace(id) on delete cascade,
  campo               text not null check (campo in (
                        'title', 'description', 'objective', 'responsible', 'area',
                        'evidence', 'due_date', 'acceptance_criterion')),
  estado              text not null default 'missing'
                      check (estado in ('missing', 'proposed', 'confirmed')),
  valor               jsonb,
  proposed_by         text check (proposed_by in ('model', 'server', 'user')),
  source_inbound_id   uuid references inbound_message(id),
  source_raw_text     text,
  source_choice_id    uuid,
  version             integer not null default 1 check (version > 0),
  actualizado_en      timestamptz not null default now(),
  primary key (request_id, campo),
  constraint task_intake_field_workspace_id_unique unique (workspace_id, request_id, campo),
  constraint task_intake_field_request_workspace
    foreign key (workspace_id, request_id)
    references task_intake_request(workspace_id, id) on delete cascade,
  constraint task_intake_field_source_workspace
    foreign key (workspace_id, source_inbound_id)
    references inbound_message(workspace_id, id),
  check ((source_inbound_id is null) = (source_raw_text is null)),
  check ((estado = 'missing' and valor is null) or
         (estado <> 'missing' and valor is not null))
);

create table task_intake_choice_set (
  id                uuid primary key default gen_random_uuid(),
  workspace_id      uuid not null references workspace(id) on delete cascade,
  request_id        uuid not null,
  campo             text,
  request_version   integer not null,
  tipo              text not null,
  estado            text not null default 'active'
                    check (estado in ('active', 'consumed', 'invalidated')),
  resultado         jsonb,
  creado_en         timestamptz not null default now(),
  constraint task_intake_choice_set_workspace_id_unique unique (workspace_id, id),
  constraint task_intake_choice_set_request_workspace
    foreign key (workspace_id, request_id)
    references task_intake_request(workspace_id, id) on delete cascade
);

create unique index task_intake_one_active_choice_set
  on task_intake_choice_set (request_id) where estado = 'active';

create table task_intake_choice (
  id                uuid primary key default gen_random_uuid(),
  workspace_id      uuid not null references workspace(id) on delete cascade,
  choice_set_id     uuid not null,
  token             text not null unique,
  etiqueta          text not null,
  accion            text not null,
  valor             jsonb,
  orden             integer not null default 0,
  activa            boolean not null default true,
  elegida           boolean not null default false,
  resultado         jsonb,
  constraint task_intake_choice_workspace_id_unique unique (workspace_id, id),
  constraint task_intake_choice_set_workspace
    foreign key (workspace_id, choice_set_id)
    references task_intake_choice_set(workspace_id, id) on delete cascade,
  constraint intake_token_cabe_en_callback check (octet_length(token) between 8 and 40),
  constraint task_intake_choice_telegram_label
    check (telegram_utf16_units(etiqueta) between 1 and 80)
);

create index task_intake_choice_de
  on task_intake_choice (choice_set_id, orden);

create table task_intake_free_text_slot (
  id                  uuid primary key default gen_random_uuid(),
  workspace_id        uuid not null references workspace(id) on delete cascade,
  request_id          uuid not null,
  campo               text not null,
  request_version     integer not null,
  estado              text not null default 'active'
                      check (estado in ('active', 'consumed', 'invalidated')),
  source_inbound_id   uuid,
  source_raw_text     text,
  resultado           jsonb,
  creado_en           timestamptz not null default now(),
  consumido_en        timestamptz,
  constraint task_intake_free_text_workspace_id_unique unique (workspace_id, id),
  constraint task_intake_free_text_request_workspace
    foreign key (workspace_id, request_id)
    references task_intake_request(workspace_id, id) on delete cascade,
  constraint task_intake_free_text_source_workspace
    foreign key (workspace_id, source_inbound_id)
    references inbound_message(workspace_id, id),
  check ((source_inbound_id is null) = (source_raw_text is null))
);

create unique index task_intake_one_active_text_slot
  on task_intake_free_text_slot (request_id) where estado = 'active';

alter table task_intake_field
  add constraint task_intake_field_source_choice
  foreign key (workspace_id, source_choice_id)
  references task_intake_choice(workspace_id, id);

alter table message_outbox
  add column intake_choice_set_id uuid references task_intake_choice_set(id)
  on delete set null;
alter table message_outbox drop constraint message_outbox_telegram_payload;
alter table message_outbox
  add constraint message_outbox_telegram_payload
  check (telegram_utf16_units(cuerpo) between 1 and
         case when pending_action_id is not null or intake_choice_set_id is not null
              then 3900 else 4096 end);
alter table message_outbox
  add constraint message_outbox_choice_workspace
    foreign key (workspace_id, intake_choice_set_id)
    references task_intake_choice_set(workspace_id, id)
    on delete set null (intake_choice_set_id);

do $$
declare table_name text;
begin
  foreach table_name in array array[
    'task_intake_request', 'task_intake_field', 'task_intake_choice_set',
    'task_intake_choice', 'task_intake_free_text_slot'
  ] loop
    execute format('alter table %I enable row level security', table_name);
    execute format('alter table %I force row level security', table_name);
    execute format(
      'create policy aislamiento_espacio on %I using '
      '(workspace_id = nullif(current_setting(''leda.workspace_id'', true), '''')::uuid)',
      table_name);
    execute format('grant select, insert, update, delete on %I to leda_app',
                   table_name);
    execute format('grant all on %I to leda_admin', table_name);
    execute format('grant all privileges on %I to leda_owner', table_name);
  end loop;
end $$;

create or replace function confirmar_borrador_tarea(p_workspace_id uuid, p_token text,
                                         p_telegram_user_id bigint,
                                         p_chat_id bigint)
returns table (resultado text, task_id uuid, pending_action_id uuid, replay boolean)
language plpgsql security definer
set search_path = leda, public, pg_temp as $$
declare
  o pending_action_option%rowtype;
  a pending_action%rowtype;
  d task_draft%rowtype;
  obj objective%rowtype;
  responsable membership%rowtype;
  politica task_evidence_policy%rowtype;
  actor_membership uuid;
  actor_app_user_id uuid;
  aprobador_actual uuid;
  nueva_task uuid;
  ahora timestamptz := clock_timestamp();
  preview_actual jsonb;
begin
  perform set_config('leda.workspace_id', p_workspace_id::text, true);
  select * into o from pending_action_option
   where token = p_token and workspace_id = p_workspace_id;
  if not found then
    return query select 'inexistente'::text, null::uuid, null::uuid, false;
    return;
  end if;

  select * into a from pending_action where id = o.pending_action_id for update;
  if a.draft_id is null then
    return query select 'no_es_borrador'::text, null::uuid, a.id, false;
    return;
  end if;
  if a.workspace_id <> p_workspace_id then
    return query select 'inexistente'::text, null::uuid, null::uuid, false;
    return;
  end if;
  if a.chat_id is distinct from p_chat_id then
    return query select 'ajena'::text, null::uuid, a.id, false;
    return;
  end if;

  select m.id, m.app_user_id into actor_membership, actor_app_user_id
    from membership m join app_user u on u.id = m.app_user_id
   where m.workspace_id = p_workspace_id and m.id = a.membership_id
     and u.telegram_user_id = p_telegram_user_id and m.activo;
  if actor_membership is null then
    return query select 'ajena'::text, null::uuid, a.id, false;
    return;
  end if;
  if a.estado <> 'esperando' then
    if a.resultado->>'resultado' in ('ok', 'cancelada') then
      return query select a.resultado->>'resultado',
        nullif(a.resultado->>'task_id', '')::uuid, a.id, true;
    end if;
    return query select 'usada'::text, null::uuid, a.id, false;
    return;
  end if;
  if a.vence_en <= ahora then
    update pending_action set estado = 'vencida' where id = a.id;
    update pending_action_option set activa = false
     where pending_action_option.pending_action_id = a.id;
    return query select 'vencida'::text, null::uuid, a.id, false;
    return;
  end if;

  if o.valor = 'false'::jsonb then
    update pending_action
       set estado = 'cancelada', resuelta_en = ahora,
            resuelta_por = actor_app_user_id,
             resultado = coalesce(pending_action.resultado, '{}'::jsonb)
                         || jsonb_build_object('resultado', 'cancelada')
     where id = a.id;
    update pending_action_option set activa = false
     where pending_action_option.pending_action_id = a.id;
    update task_draft set estado = 'cancelled', actualizado_en = ahora where id = a.draft_id;
    update task_intake_request
       set estado = 'cancelled', actualizado_en = ahora,
           terminal_result = jsonb_build_object('resultado', 'cancelada',
                                                 'pending_action_id', a.id)
     where task_draft_id = a.draft_id and estado = 'active';
    update task_intake_choice set activa = false where choice_set_id in
      (select s.id from task_intake_choice_set s join task_intake_request r
         on r.id = s.request_id where r.task_draft_id = a.draft_id);
    update task_intake_choice_set set estado = 'invalidated'
     where request_id in (select id from task_intake_request
                           where task_draft_id = a.draft_id)
       and estado = 'active';
    update task_intake_free_text_slot set estado = 'invalidated'
     where request_id in (select id from task_intake_request
                           where task_draft_id = a.draft_id)
       and estado = 'active';
    insert into audit_log
         (workspace_id, actor_app_user_id, actor_kind, accion, sujeto_tipo,
          sujeto_id, detalle)
    select a.workspace_id, actor_app_user_id, 'persona',
           'cancelar_ingreso_tarea', 'task_draft', a.draft_id,
           jsonb_build_object('pending_action_id', a.id)
     where exists (select 1 from task_intake_request
                    where task_draft_id = a.draft_id);
    insert into message_outbox
         (workspace_id, chat_id, destinatario_membership_id, tipo, cuerpo,
          estado, programado_para, dedupe_key, es_respuesta)
    values (a.workspace_id, a.chat_id, a.membership_id, 'normal',
            'Listo, cancelé el borrador de la tarea.', 'listo', ahora,
            a.workspace_id || ':intake-terminal:' || a.id || ':cancelled', true)
    on conflict (dedupe_key) do nothing;
    return query select 'cancelada'::text, null::uuid, a.id, false;
    return;
  end if;

  select * into d from task_draft where id = a.draft_id for update;
  if not found or d.converted_task_id is not null or d.version <> a.draft_version
     or d.workspace_id <> a.workspace_id then
    update pending_action set estado = 'vencida' where id = a.id;
    update pending_action_option set activa = false
     where pending_action_option.pending_action_id = a.id;
    return query select 'obsoleta'::text, null::uuid, a.id, false;
    return;
  end if;

  select * into obj from objective where id = d.objective_id for share;
  select * into responsable from membership
   where id = d.responsable_membership_id for share;
  select * into politica from task_evidence_policy
   where workspace_id = d.workspace_id and area_id = d.area_id for share;

  preview_actual := jsonb_build_object(
    'draft_id', d.id::text, 'version', d.version,
    'titulo', d.titulo, 'descripcion', d.descripcion,
    'objetivo', d.objective_snapshot,
    'area_id', d.area_id::text,
    'responsable_membership_id', d.responsable_membership_id::text,
    'fecha_objetivo', d.fecha_objetivo::text,
    'criterio_aceptacion', d.criterio_aceptacion,
    'evidencia_requerida', to_jsonb(d.evidencia_requerida),
    'evidencia_policy_version', d.evidencia_policy_version);

  if a.preview is distinct from preview_actual
     or d.objective_id is null or d.responsable_membership_id is null
     or d.area_id is null or d.fecha_objetivo is null
     or nullif(btrim(d.titulo), '') is null
     or nullif(btrim(d.criterio_aceptacion), '') is null
     or d.evidencia_requerida is null
     or obj.id is null or obj.workspace_id <> d.workspace_id
     or obj.estado not in ('activo', 'propuesto')
     or d.objective_snapshot is distinct from
        jsonb_build_object('id', obj.id, 'titulo', obj.titulo, 'estado', obj.estado)
     or responsable.id is null or not responsable.activo
     or responsable.workspace_id <> d.workspace_id
     or responsable.area_id <> d.area_id
     or politica.area_id is null
     or politica.version <> d.evidencia_policy_version
     or politica.evidencia_requerida is distinct from d.evidencia_requerida then
    update pending_action set estado = 'vencida' where id = a.id;
    update pending_action_option set activa = false
     where pending_action_option.pending_action_id = a.id;
    return query select 'obsoleta'::text, null::uuid, a.id, false;
    return;
  end if;

  aprobador_actual := responsable.aprobador_membership_id;
  if aprobador_actual is null then
    select m.id into aprobador_actual
      from membership m join rol r on r.id = m.rol_id
     where m.workspace_id = d.workspace_id and m.activo and r.autoridad_final;
  end if;
  if aprobador_actual is distinct from a.membership_id
     or aprobador_actual is distinct from actor_membership then
    update pending_action set estado = 'vencida' where id = a.id;
    update pending_action_option set activa = false
     where pending_action_option.pending_action_id = a.id;
    return query select 'obsoleta'::text, null::uuid, a.id, false;
    return;
  end if;

  insert into task
       (workspace_id, objective_id, titulo, descripcion, area_id,
        responsable_membership_id, fecha_objetivo, criterio_aceptacion,
        evidencia_requerida, evidencia_policy_version, source_draft_id)
  values
       (d.workspace_id, d.objective_id, d.titulo, d.descripcion, d.area_id,
        d.responsable_membership_id, d.fecha_objetivo, d.criterio_aceptacion,
        d.evidencia_requerida, d.evidencia_policy_version, d.id)
  returning id into nueva_task;

  insert into task_state_event
       (task_id, estado_nuevo, actor_kind, actor_app_user_id, motivo)
  values (nueva_task, 'asignada', 'persona', actor_app_user_id,
          'borrador confirmado por autoridad vigente');

  insert into audit_log
       (workspace_id, actor_app_user_id, actor_kind, accion, sujeto_tipo,
        sujeto_id, detalle)
  values
       (d.workspace_id, actor_app_user_id, 'persona',
        'confirmar_borrador_tarea', 'task', nueva_task,
        jsonb_build_object(
          'draft_id', d.id, 'draft_version', d.version,
          'pending_action_id', a.id,
          'responsable_membership_id', d.responsable_membership_id,
          'confirmador_membership_id', actor_membership,
          'evidencia_policy_version', d.evidencia_policy_version));

  update task_draft set converted_task_id = nueva_task, estado = 'converted',
                        actualizado_en = ahora
   where id = d.id;
  update pending_action
     set estado = 'resuelta', resuelta_en = ahora,
         resuelta_por = actor_app_user_id,
          resultado = coalesce(pending_action.resultado, '{}'::jsonb)
                      || jsonb_build_object('resultado', 'ok', 'task_id', nueva_task)
   where id = a.id;
  update pending_action_option set activa = false
   where pending_action_option.pending_action_id = a.id;
  update task_intake_request
     set estado = 'converted', actualizado_en = ahora,
         terminal_result = jsonb_build_object('resultado', 'ok',
                                               'task_id', nueva_task,
                                               'pending_action_id', a.id)
   where task_draft_id = a.draft_id and estado = 'active';
  update task_intake_choice set activa = false where choice_set_id in
    (select s.id from task_intake_choice_set s join task_intake_request r
       on r.id = s.request_id where r.task_draft_id = a.draft_id);
  update task_intake_choice_set set estado = 'invalidated'
   where request_id in (select id from task_intake_request
                         where task_draft_id = a.draft_id)
     and estado = 'active';
  update task_intake_free_text_slot set estado = 'invalidated'
   where request_id in (select id from task_intake_request
                         where task_draft_id = a.draft_id)
     and estado = 'active';
  insert into message_outbox
       (workspace_id, chat_id, destinatario_membership_id, tipo, cuerpo,
        estado, programado_para, dedupe_key, es_respuesta)
  values (a.workspace_id, a.chat_id, a.membership_id, 'normal',
          'Hecho. La tarea quedó comprometida.', 'listo', ahora,
          a.workspace_id || ':intake-terminal:' || a.id || ':converted', true)
  on conflict (dedupe_key) do nothing;

  return query select 'ok'::text, nueva_task, a.id, false;
end $$;

commit;
