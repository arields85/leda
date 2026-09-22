\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0001_task_commitment.sql. This migration adds only the
-- bounded, server-owned general task-intake path; Unit 1A remains authoritative.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0002 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('prisma.task_draft') is null
     or to_regprocedure('prisma.confirmar_borrador_tarea(uuid,text,bigint)') is null then
    raise exception '0002 requires 0001_task_commitment.sql';
  end if;
end $$;

select pg_advisory_xact_lock(hashtextextended('prisma:0002_general_task_intake', 0));
lock table task_draft, pending_action, pending_action_option, message_outbox
  in share row exclusive mode;

-- Fail before DDL. Every legacy Unit 1A draft, pending preview and visible
-- outbox row must have one exact representation under the new contract.
do $$
declare
  item record;
  old_preview jsonb;
  new_preview jsonb;
  units integer;
  i integer;
  field_index integer;
  values_to_check text[];
  limits_to_check integer[] := array[200, 800, 500];
begin
  for item in select id, titulo, descripcion, criterio_aceptacion from task_draft loop
    values_to_check := array[item.titulo, item.descripcion, item.criterio_aceptacion];
    for field_index in 1..3 loop
      if values_to_check[field_index] is null then
        continue;
      end if;
      units := 0;
      for i in 1..char_length(values_to_check[field_index]) loop
        units := units + case
          when ascii(substr(values_to_check[field_index], i, 1)) > 65535
          then 2 else 1 end;
      end loop;
      if units > limits_to_check[field_index] then
        raise exception
          '0002 preflight failed: legacy Unit1A draft % exceeds the bounded field contract.',
          item.id;
      end if;
    end loop;
  end loop;

  if exists (
    select 1 from task_draft d
     where (d.converted_task_id is not null and exists (
              select 1 from pending_action p
               where p.draft_id = d.id and p.estado = 'esperando'))
        or (d.converted_task_id is null and exists (
              select 1 from pending_action p
               where p.draft_id = d.id and p.estado = 'resuelta'))
        or (select count(*) from pending_action p
             where p.draft_id = d.id and p.estado = 'esperando') > 1
        or (d.converted_task_id is null and exists (
              select 1 from pending_action p
               where p.draft_id = d.id and p.estado = 'esperando')
            and exists (
              select 1 from pending_action p
               where p.draft_id = d.id and p.estado = 'cancelada'))
  ) then
    raise exception
      '0002 preflight failed: a legacy Unit1A draft/pending state cannot be represented exactly.';
  end if;

  for item in
    select p.id pending_id, p.preview, d.id draft_id, d.version,
           d.titulo, d.descripcion, d.objective_snapshot, d.area_id,
           d.responsable_membership_id, d.fecha_objetivo,
           d.criterio_aceptacion, d.evidencia_requerida,
           d.evidencia_policy_version
      from pending_action p join task_draft d on d.id = p.draft_id
  loop
    old_preview := jsonb_build_object(
      'draft_id', item.draft_id::text, 'version', item.version,
      'titulo', item.titulo, 'objetivo', item.objective_snapshot,
      'area_id', item.area_id::text,
      'responsable_membership_id', item.responsable_membership_id::text,
      'fecha_objetivo', item.fecha_objetivo::text,
      'criterio_aceptacion', item.criterio_aceptacion,
      'evidencia_requerida', to_jsonb(item.evidencia_requerida),
      'evidencia_policy_version', item.evidencia_policy_version);
    new_preview := old_preview || jsonb_build_object('descripcion', item.descripcion);
    if item.preview is distinct from old_preview
       and item.preview is distinct from new_preview then
      raise exception
        '0002 preflight failed: legacy Unit1A pending preview % cannot be revalidated exactly.',
        item.pending_id;
    end if;
  end loop;

  for item in select id, cuerpo, pending_action_id from message_outbox loop
    units := 0;
    for i in 1..char_length(item.cuerpo) loop
      units := units + case
        when ascii(substr(item.cuerpo, i, 1)) > 65535 then 2 else 1 end;
    end loop;
    if units < 1 or units > (case when item.pending_action_id is null
                                   then 4096 else 3900 end) then
      raise exception
        '0002 preflight failed: legacy outbox row % exceeds the Telegram payload contract.',
        item.id;
    end if;
  end loop;

  for item in select id, token, etiqueta from pending_action_option loop
    units := 0;
    for i in 1..char_length(item.etiqueta) loop
      units := units + case
        when ascii(substr(item.etiqueta, i, 1)) > 65535 then 2 else 1 end;
    end loop;
    if units not between 1 and 80 or octet_length('p:' || item.token) > 64 then
      raise exception
        '0002 preflight failed: legacy pending option % is not Telegram-deliverable.',
        item.id;
    end if;
  end loop;
end $$;

create function telegram_utf16_units(p_text text) returns integer
language plpgsql immutable strict parallel safe as $$
declare
  units integer := 0;
  i integer;
begin
  for i in 1..char_length(p_text) loop
    units := units + case when ascii(substr(p_text, i, 1)) > 65535 then 2 else 1 end;
  end loop;
  return units;
end $$;

alter table task_draft
  add column estado text;
alter table pending_action add column resultado jsonb;
alter table pending_action_option
  add column activa boolean not null default true,
  add column resultado jsonb;

update task_draft d
   set estado = case
     when d.converted_task_id is not null then 'converted'
     when exists (select 1 from pending_action p
                   where p.draft_id = d.id and p.estado = 'cancelada')
          then 'cancelled'
     else 'open'
   end;
alter table task_draft alter column estado set default 'open';
alter table task_draft alter column estado set not null;
alter table task_draft add constraint task_draft_estado_check
  check (estado in ('open', 'cancelled', 'converted'));

update pending_action p
   set resultado = jsonb_build_object(
         'migration', '0002', 'preview_description_preexisting', true,
         'legacy_estado', p.estado::text)
  from task_draft d
 where p.draft_id = d.id
   and p.preview = jsonb_build_object(
     'draft_id', d.id::text, 'version', d.version,
     'titulo', d.titulo, 'descripcion', d.descripcion,
     'objetivo', d.objective_snapshot,
     'area_id', d.area_id::text,
     'responsable_membership_id', d.responsable_membership_id::text,
     'fecha_objetivo', d.fecha_objetivo::text,
     'criterio_aceptacion', d.criterio_aceptacion,
     'evidencia_requerida', to_jsonb(d.evidencia_requerida),
     'evidencia_policy_version', d.evidencia_policy_version);

update pending_action p
   set preview = p.preview || jsonb_build_object('descripcion', d.descripcion),
       resultado = jsonb_build_object(
         'migration', '0002', 'preview_description_backfilled', true,
         'legacy_estado', p.estado::text)
  from task_draft d
 where p.draft_id = d.id
   and p.resultado is null
   and p.preview = jsonb_build_object(
     'draft_id', d.id::text, 'version', d.version,
     'titulo', d.titulo, 'objetivo', d.objective_snapshot,
     'area_id', d.area_id::text,
     'responsable_membership_id', d.responsable_membership_id::text,
     'fecha_objetivo', d.fecha_objetivo::text,
     'criterio_aceptacion', d.criterio_aceptacion,
     'evidencia_requerida', to_jsonb(d.evidencia_requerida),
     'evidencia_policy_version', d.evidencia_policy_version);

alter table membership
  add constraint membership_workspace_id_unique unique (workspace_id, id);
alter table task_draft
  add constraint task_draft_workspace_id_unique unique (workspace_id, id),
  add constraint task_draft_creator_workspace
    foreign key (workspace_id, creado_por_membership_id)
    references membership(workspace_id, id),
  add constraint task_draft_responsible_workspace
    foreign key (workspace_id, responsable_membership_id)
    references membership(workspace_id, id),
  add constraint task_draft_title_payload
    check (titulo is null or telegram_utf16_units(titulo) <= 200),
  add constraint task_draft_description_payload
    check (descripcion is null or telegram_utf16_units(descripcion) <= 800),
  add constraint task_draft_acceptance_payload
    check (criterio_aceptacion is null
           or telegram_utf16_units(criterio_aceptacion) <= 500);
alter table inbound_message
  add constraint inbound_message_workspace_id_unique unique (workspace_id, id),
  add constraint inbound_message_workspace_chat_unique
    unique (workspace_id, id, chat_id);
alter table pending_action
  add constraint pending_action_workspace_id_unique unique (workspace_id, id),
  add constraint pending_action_membership_workspace
    foreign key (workspace_id, membership_id)
    references membership(workspace_id, id),
  add constraint pending_action_draft_workspace
    foreign key (workspace_id, draft_id)
    references task_draft(workspace_id, id);
alter table pending_action_option
  add constraint pending_action_option_workspace_id_unique unique (workspace_id, id),
  add constraint pending_action_option_parent_workspace
    foreign key (workspace_id, pending_action_id)
    references pending_action(workspace_id, id) on delete cascade,
  add constraint pending_action_option_telegram_label
    check (telegram_utf16_units(etiqueta) between 1 and 80);

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
create index task_intake_choice_de on task_intake_choice (choice_set_id, orden);

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
alter table message_outbox
  add constraint message_outbox_telegram_payload
  check (telegram_utf16_units(cuerpo) between 1 and
         case when pending_action_id is not null or intake_choice_set_id is not null
              then 3900 else 4096 end);
alter table message_outbox
  add constraint message_outbox_recipient_workspace
    foreign key (workspace_id, destinatario_membership_id)
    references membership(workspace_id, id),
  add constraint message_outbox_pending_workspace
    foreign key (workspace_id, pending_action_id)
    references pending_action(workspace_id, id) on delete set null (pending_action_id),
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
      '(workspace_id = nullif(current_setting(''prisma.workspace_id'', true), '''')::uuid)',
      table_name);
    execute format('grant select, insert, update, delete on %I to prisma_app',
                   table_name);
    execute format('grant all on %I to prisma_admin', table_name);
  end loop;
end $$;

grant update (objective_id, objective_snapshot, titulo, descripcion, area_id,
              responsable_membership_id, fecha_objetivo,
              criterio_aceptacion, evidencia_requerida,
              evidencia_policy_version, version, estado, actualizado_en)
  on task_draft to prisma_app;

-- Reconcile any waiting legacy crear_tarea callback. It is cancelled rather
-- than reinterpreted because its model-selected arguments lack intake lineage.
update pending_action p
   set estado = 'cancelada', resuelta_en = clock_timestamp(),
       resultado = jsonb_build_object(
         'migration', '0002', 'resultado', 'legacy_cancelled',
         'outbox', coalesce((
           select jsonb_object_agg(o.id::text, o.estado::text)
             from message_outbox o
            where o.pending_action_id = p.id
              and o.estado in ('pendiente','esperando_confirmacion','listo')
         ), '{}'::jsonb))
 where p.herramienta = 'crear_tarea' and p.estado = 'esperando';
update pending_action_option set activa = false
 where pending_action_id in (
   select id from pending_action where resultado->>'migration' = '0002');
update message_outbox set estado = 'descartado'
 where pending_action_id in (
   select id from pending_action where resultado->>'migration' = '0002')
   and estado in ('pendiente','esperando_confirmacion','listo');

create function confirmar_borrador_tarea(p_workspace_id uuid, p_token text,
                                         p_telegram_user_id bigint,
                                         p_chat_id bigint)
returns table (resultado text, task_id uuid, pending_action_id uuid, replay boolean)
language plpgsql security definer
set search_path = prisma, public, pg_temp as $$
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
  perform set_config('prisma.workspace_id', p_workspace_id::text, true);
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

revoke all on function confirmar_borrador_tarea(uuid, text, bigint, bigint)
  from public;
revoke execute on function confirmar_borrador_tarea(uuid, text, bigint, bigint)
  from prisma_app;
grant execute on function confirmar_borrador_tarea(uuid, text, bigint, bigint)
  to prisma_gateway;
drop function confirmar_borrador_tarea(uuid, text, bigint);

create function resolver_ingreso_borrador(p_workspace_id uuid, p_token text,
                                          p_telegram_user_id bigint,
                                          p_chat_id bigint)
returns table (resultado text, task_id uuid, pending_action_id uuid, replay boolean)
language plpgsql security definer
set search_path = prisma, public, pg_temp as $$
begin
  return query
    select c.resultado, c.task_id, c.pending_action_id, c.replay
      from confirmar_borrador_tarea(
        p_workspace_id, p_token, p_telegram_user_id, p_chat_id) c;
end $$;

revoke all on function resolver_ingreso_borrador(uuid, text, bigint, bigint)
  from public;
revoke execute on function resolver_ingreso_borrador(uuid, text, bigint, bigint)
  from prisma_app;
grant execute on function resolver_ingreso_borrador(uuid, text, bigint, bigint)
  to prisma_gateway;

commit;
