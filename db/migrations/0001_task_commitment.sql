\set ON_ERROR_STOP on

begin;
set search_path = leda, public;

do $$
declare incompatible bigint;
begin
  select count(*) into incompatible
    from task
   where objective_id is null
      or responsable_membership_id is null
      or fecha_objetivo is null
      or nullif(btrim(titulo), '') is null
      or nullif(btrim(criterio_aceptacion), '') is null
      or evidencia_requerida is null;
  if incompatible > 0 then
    raise exception
      'Preflight failed: % existing task(s) lack the commitment contract. Inventory and reconcile them before migration.',
      incompatible;
  end if;
end $$;

create table if not exists task_evidence_policy (
  workspace_id        uuid not null references workspace(id) on delete cascade,
  area_id             uuid not null references area(id) on delete cascade,
  evidencia_requerida text[] not null,
  version             integer not null default 1 check (version > 0),
  actualizado_en      timestamptz not null default now(),
  primary key (workspace_id, area_id)
);

-- Policy rows are populated by re-importing the approved workspace pack after
-- this schema migration. Until then, new requests remain drafts because a
-- missing row means unresolved policy.

create table if not exists task_draft (
  id                        uuid primary key default gen_random_uuid(),
  workspace_id              uuid not null references workspace(id) on delete cascade,
  creado_por_membership_id  uuid not null references membership(id),
  objective_id              uuid references objective(id),
  objective_snapshot        jsonb,
  titulo                    text,
  descripcion               text,
  area_id                   uuid references area(id),
  responsable_membership_id uuid references membership(id),
  fecha_objetivo            timestamptz,
  criterio_aceptacion       text,
  evidencia_requerida       text[],
  evidencia_policy_version  integer,
  version                   integer not null default 1 check (version > 0),
  converted_task_id         uuid,
  creado_en                 timestamptz not null default now(),
  actualizado_en            timestamptz not null default now(),
  check ((evidencia_requerida is null) =
         (evidencia_policy_version is null))
);

create index if not exists task_draft_ws
  on task_draft (workspace_id, creado_en desc);

alter table task
  add column if not exists evidencia_policy_version integer,
  add column if not exists source_draft_id uuid references task_draft(id);
create unique index if not exists task_source_draft_unique
  on task (source_draft_id);

-- Existing rows predate this contract and intentionally keep source_draft_id
-- null. The preflight guarantees they are complete; new application rows must
-- carry a draft link because leda_app loses direct INSERT below.

do $$ begin
  if not exists (
    select 1 from pg_constraint
     where conname = 'task_draft_converted_task'
       and conrelid = 'task_draft'::regclass
  ) then
    alter table task_draft
      add constraint task_draft_converted_task
      foreign key (converted_task_id) references task(id);
  end if;
end $$;

alter table pending_action
  add column if not exists draft_id uuid references task_draft(id),
  add column if not exists draft_version integer,
  add column if not exists preview jsonb;

do $$ begin
  if not exists (
    select 1 from pg_constraint
     where conname = 'pending_action_draft_preview'
       and conrelid = 'pending_action'::regclass
  ) then
    alter table pending_action add constraint pending_action_draft_preview
      check ((draft_id is null and draft_version is null and preview is null)
          or (draft_id is not null and draft_version is not null and preview is not null));
  end if;
end $$;

alter table task_draft enable row level security;
alter table task_draft force row level security;
alter table task_evidence_policy enable row level security;
alter table task_evidence_policy force row level security;

do $$ begin
  if not exists (select 1 from pg_policy
                  where polname = 'aislamiento_espacio'
                    and polrelid = 'task_draft'::regclass) then
    create policy aislamiento_espacio on task_draft
      using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
  end if;
  if not exists (select 1 from pg_policy
                  where polname = 'aislamiento_espacio'
                    and polrelid = 'task_evidence_policy'::regclass) then
    create policy aislamiento_espacio on task_evidence_policy
      using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
  end if;
end $$;

grant select, insert on task_draft to leda_app;
grant select on task_evidence_policy to leda_app;
grant all on task_draft, task_evidence_policy to leda_admin;
revoke insert on task from leda_app;
revoke update, delete on task from leda_app;
grant select on task to leda_app;

-- Remove the previous caller-controlled actor/time boundary if this correction
-- is applied over an earlier 0001 installation.
drop function if exists confirmar_borrador_tarea(text, uuid, timestamptz);

create or replace function aplicar_evento_tarea() returns trigger
security definer set search_path = leda, public as $$
begin
  perform set_config('leda.aplicando_evento', '1', true);
  update task
     set estado = new.estado_nuevo,
         actualizado_en = new.at
   where id = new.task_id;
  perform set_config('leda.aplicando_evento', '0', true);
  return new;
end $$ language plpgsql;

create or replace function bloquear_estado_directo() returns trigger as $$
begin
  if new.objective_id is distinct from old.objective_id
     or new.titulo is distinct from old.titulo
     or new.descripcion is distinct from old.descripcion
     or new.area_id is distinct from old.area_id
     or new.responsable_membership_id is distinct from old.responsable_membership_id
     or new.fecha_objetivo is distinct from old.fecha_objetivo
     or new.criterio_aceptacion is distinct from old.criterio_aceptacion
     or new.evidencia_requerida is distinct from old.evidencia_requerida
     or new.evidencia_policy_version is distinct from old.evidencia_policy_version
     or new.source_draft_id is distinct from old.source_draft_id then
    raise exception 'Los campos de compromiso de una tarea son inmutables.';
  end if;
  if new.estado is distinct from old.estado
     and coalesce(current_setting('leda.aplicando_evento', true), '0') <> '1' then
    raise exception
      'El estado de una tarea no se escribe directamente. Insertá una fila en task_state_event.';
  end if;
  return new;
end $$ language plpgsql;

create or replace function confirmar_borrador_tarea(
  p_workspace_id uuid, p_token text, p_telegram_user_id bigint
)
returns table (resultado text, task_id uuid)
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
    return query select 'inexistente'::text, null::uuid;
    return;
  end if;

  select * into a from pending_action where id = o.pending_action_id for update;
  if a.draft_id is null then
    return query select 'no_es_borrador'::text, null::uuid;
    return;
  end if;
  if a.estado <> 'esperando' then
    return query select 'usada'::text, null::uuid;
    return;
  end if;
  if a.workspace_id <> p_workspace_id then
    return query select 'inexistente'::text, null::uuid;
    return;
  end if;
  if a.vence_en <= ahora then
    update pending_action set estado = 'vencida' where id = a.id;
    return query select 'vencida'::text, null::uuid;
    return;
  end if;

  select m.id, m.app_user_id into actor_membership, actor_app_user_id
    from membership m join app_user u on u.id = m.app_user_id
   where m.workspace_id = p_workspace_id and m.id = a.membership_id
     and u.telegram_user_id = p_telegram_user_id and m.activo;
  if actor_membership is null then
    return query select 'ajena'::text, null::uuid;
    return;
  end if;

  if o.valor = 'false'::jsonb then
    update pending_action
       set estado = 'cancelada', resuelta_en = ahora,
           resuelta_por = actor_app_user_id
     where id = a.id;
    return query select 'cancelada'::text, null::uuid;
    return;
  end if;

  select * into d from task_draft where id = a.draft_id for update;
  if not found or d.converted_task_id is not null or d.version <> a.draft_version
     or d.workspace_id <> a.workspace_id then
    update pending_action set estado = 'vencida' where id = a.id;
    return query select 'obsoleta'::text, null::uuid;
    return;
  end if;

  select * into obj from objective where id = d.objective_id for share;
  select * into responsable from membership
   where id = d.responsable_membership_id for share;
  select * into politica from task_evidence_policy
   where workspace_id = d.workspace_id and area_id = d.area_id for share;

  preview_actual := jsonb_build_object(
    'draft_id', d.id::text, 'version', d.version,
    'titulo', d.titulo, 'objetivo', d.objective_snapshot,
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
    return query select 'obsoleta'::text, null::uuid;
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
    return query select 'obsoleta'::text, null::uuid;
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

  update task_draft set converted_task_id = nueva_task,
                        actualizado_en = ahora
   where id = d.id;
  update pending_action
     set estado = 'resuelta', resuelta_en = ahora,
         resuelta_por = actor_app_user_id
   where id = a.id;

  return query select 'ok'::text, nueva_task;
end $$;

revoke all on function confirmar_borrador_tarea(uuid, text, bigint)
  from public;

do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'leda_gateway') then
    create role leda_gateway nologin noinherit;
  end if;
end $$;
alter role leda_gateway noinherit nobypassrls;

revoke execute on function confirmar_borrador_tarea(uuid, text, bigint)
  from leda_app;
grant usage on schema leda to leda_gateway;
grant execute on function confirmar_borrador_tarea(uuid, text, bigint)
  to leda_gateway;

commit;
