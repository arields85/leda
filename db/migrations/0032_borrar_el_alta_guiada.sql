\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0031_seguimiento_del_motor.sql. El Motor, Etapa 3, tareas E3-3 y E3-4
-- (`odd/tasks/motor-definitivo.md`): borra el alta guiada de tareas por chat (flujo A,
-- migración 0002), cuyo código se retiró con los flujos A y B. Las tareas no se crean
-- por chat (ADR 0017, decisiones 1 y 2).
--
-- - Las cinco tablas `task_intake_*` (la solicitud, sus campos, sus elecciones con
--   botones y su texto libre).
-- - `message_outbox.intake_choice_set_id`, con sus dos claves foráneas y su rama del
--   límite de texto: un mensaje con botones es sólo el de una acción pendiente.
-- - `confirmar_borrador_tarea()` sin lo que cerraba la solicitud del alta al convertir o
--   cancelar un borrador. La conversión y la cancelación siguen iguales; la cancelación
--   ya no escribe la fila de auditoría `cancelar_ingreso_tarea`, que sólo se escribía
--   para un borrador del alta.
--
-- Quedan `task_draft`, la vista previa en `pending_action` y la conversión confirmada por
-- la autoridad vigente: son la garantía del compromiso de una tarea.
--
-- No borra historia en silencio: si quedan solicitudes del alta, se detiene antes de
-- tocar el esquema. Quien la corra en una base con datos los respalda (`pg_dump` de las
-- cinco tablas) y los borra a mano antes. Se deshace con
-- `db/rollbacks/0032_borrar_el_alta_guiada.sql` (las tablas vuelven vacías).
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0032 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('leda.task_forecast') is null then
    raise exception '0032 requires 0031_seguimiento_del_motor.sql';
  end if;
  if to_regclass('leda.task_intake_request') is null then
    raise exception '0032 ya está aplicada.';
  end if;
  if exists (select 1 from task_intake_request) then
    raise exception '0032 preflight failed: quedan solicitudes del alta guiada; respaldalas y borralas antes';
  end if;
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
  insert into message_outbox
       (workspace_id, chat_id, destinatario_membership_id, tipo, cuerpo,
        estado, programado_para, dedupe_key, es_respuesta)
  values (a.workspace_id, a.chat_id, a.membership_id, 'normal',
          'Hecho. La tarea quedó comprometida.', 'listo', ahora,
          a.workspace_id || ':intake-terminal:' || a.id || ':converted', true)
  on conflict (dedupe_key) do nothing;

  return query select 'ok'::text, nueva_task, a.id, false;
end $$;

alter table message_outbox drop constraint message_outbox_choice_workspace;
alter table message_outbox drop constraint message_outbox_telegram_payload;
alter table message_outbox drop column intake_choice_set_id;
alter table message_outbox
  add constraint message_outbox_telegram_payload
  check (telegram_utf16_units(cuerpo) between 1 and
         case when pending_action_id is not null then 3900 else 4096 end);

drop table task_intake_field;
drop table task_intake_free_text_slot;
drop table task_intake_choice;
drop table task_intake_choice_set;
drop table task_intake_request;

commit;
