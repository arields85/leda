\set ON_ERROR_STOP on

begin;
set search_path = prisma, public;
select pg_advisory_xact_lock(hashtextextended('prisma:0002_general_task_intake', 0));

lock table task_intake_request, task_intake_field, task_intake_choice_set,
           task_intake_choice, task_intake_free_text_slot
  in access exclusive mode;
lock table task_draft in share row exclusive mode;

-- Guarded rollback: intake lineage is not disposable after use. A converted
-- draft in particular can never be detached from its committed task.
do $$ begin
  if exists (select 1 from task_intake_request)
     or exists (select 1 from task_draft
                 where converted_task_id is not null and estado = 'converted')
     or exists (
       select 1 from pending_action
        where draft_id is not null and preview ? 'descripcion'
          and coalesce(resultado->>'preview_description_backfilled', 'false') <> 'true')
     or exists (
       select 1 from pending_action p join task_draft d on d.id = p.draft_id
        where p.resultado->>'preview_description_backfilled' = 'true'
          and (p.estado::text is distinct from p.resultado->>'legacy_estado'
               or p.preview is distinct from jsonb_build_object(
                 'draft_id', d.id::text, 'version', d.version,
                 'titulo', d.titulo, 'descripcion', d.descripcion,
                 'objetivo', d.objective_snapshot,
                 'area_id', d.area_id::text,
                 'responsable_membership_id', d.responsable_membership_id::text,
                 'fecha_objetivo', d.fecha_objetivo::text,
                 'criterio_aceptacion', d.criterio_aceptacion,
                 'evidencia_requerida', to_jsonb(d.evidencia_requerida),
                 'evidencia_policy_version', d.evidencia_policy_version))) then
    raise exception
      'Rollback 0002 refused: task intake data exists. Reconcile it explicitly.';
  end if;
end $$;

update pending_action p
   set preview = p.preview - 'descripcion', resultado = null
  from task_draft d
 where p.draft_id = d.id
   and p.resultado->>'preview_description_backfilled' = 'true'
   and p.estado::text = p.resultado->>'legacy_estado'
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

-- Restore only legacy rows that 0002 itself reconciled and that nobody changed
-- afterwards. Every outbox state comes from the snapshot stored by migration.
do $$
declare p record;
declare item record;
begin
  for p in select id, resultado from pending_action
            where estado = 'cancelada' and resultado->>'migration' = '0002'
  loop
    for item in select * from jsonb_each_text(coalesce(p.resultado->'outbox', '{}'))
    loop
      update message_outbox set estado = item.value::estado_salida
       where id = item.key::uuid and estado = 'descartado';
    end loop;
    update pending_action set estado = 'esperando', resuelta_en = null,
                              resultado = null where id = p.id;
    update pending_action_option set activa = true
     where pending_action_id = p.id;
  end loop;
end $$;

drop function if exists resolver_ingreso_borrador(uuid, text, bigint, bigint);
drop function if exists confirmar_borrador_tarea(uuid, text, bigint, bigint);
alter table message_outbox
  drop constraint if exists message_outbox_telegram_payload;
alter table message_outbox drop column if exists intake_choice_set_id;
drop table if exists task_intake_free_text_slot;
drop table if exists task_intake_field;
drop table if exists task_intake_choice;
drop table if exists task_intake_choice_set;
drop table if exists task_intake_request;

alter table message_outbox
  drop constraint if exists message_outbox_choice_workspace,
  drop constraint if exists message_outbox_pending_workspace,
  drop constraint if exists message_outbox_recipient_workspace;
alter table pending_action_option
  drop constraint if exists pending_action_option_telegram_label,
  drop constraint if exists pending_action_option_parent_workspace,
  drop constraint if exists pending_action_option_workspace_id_unique;
alter table pending_action
  drop constraint if exists pending_action_draft_workspace,
  drop constraint if exists pending_action_membership_workspace,
  drop constraint if exists pending_action_workspace_id_unique;
alter table task_draft
  drop constraint if exists task_draft_acceptance_payload,
  drop constraint if exists task_draft_description_payload,
  drop constraint if exists task_draft_title_payload,
  drop constraint if exists task_draft_responsible_workspace,
  drop constraint if exists task_draft_creator_workspace,
  drop constraint if exists task_draft_workspace_id_unique;
alter table inbound_message
  drop constraint if exists inbound_message_workspace_chat_unique,
  drop constraint if exists inbound_message_workspace_id_unique;
alter table membership
  drop constraint if exists membership_workspace_id_unique;

revoke update on task_draft from prisma_app;
grant select, insert on task_draft to prisma_app;
alter table pending_action_option
  drop column if exists resultado,
  drop column if exists activa;
alter table pending_action drop column if exists resultado;
alter table task_draft drop column if exists estado;
drop function if exists telegram_utf16_units(text);

create function confirmar_borrador_tarea(
  p_workspace_id uuid, p_token text, p_telegram_user_id bigint
)
returns table (resultado text, task_id uuid)
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
revoke execute on function confirmar_borrador_tarea(uuid, text, bigint)
  from prisma_app;
grant execute on function confirmar_borrador_tarea(uuid, text, bigint)
  to prisma_gateway;

commit;
