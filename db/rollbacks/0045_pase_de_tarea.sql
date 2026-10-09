\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0045_pase_de_tarea.sql.
--
-- Borra `cambio_de_responsable` y `pase_de_tarea` (con sus disparadores, funciones y políticas),
-- `quien_revisa_la_tarea` y la columna `task.revisa_membership_id`, y vuelve a poner las cuatro
-- funciones como las dejó la 0044: quién revisa una tarea vuelve a ser quien aprueba el trabajo de
-- su responsable. Las tareas que cambiaron de manos quedan con quien las tomó, y su trabajo lo pasa
-- a revisar quien aprueba el de esa persona; se pierde la historia de los pases: antes de correrlo
-- en una base con datos, `pg_dump` de las dos tablas.
begin;
set search_path = leda, public;

drop table if exists cambio_de_responsable;
drop table if exists pase_de_tarea;
drop function if exists aplicar_cambio_de_responsable();
drop function if exists vigilar_pase_de_tarea();

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

create or replace function motivo_no_cierra_tarea(p_task uuid)
returns text as $$
declare
  t            task%rowtype;
  aprobador    uuid;
  dep_abiertas integer;
begin
  select * into t from task where id = p_task;
  if not found then return 'La tarea no existe.'; end if;

  -- Que el criterio sea obligatorio lo decide el pack del espacio.
  if coalesce((select valor::text::boolean from workspace_setting
                where workspace_id = t.workspace_id
                  and clave = 'exigir_criterio_aceptacion'), true)
     and (t.criterio_aceptacion is null or btrim(t.criterio_aceptacion) = '') then
    return 'Falta el criterio de aceptación.';
  end if;

  if evidencia_pendiente(p_task) then
    return 'Falta la evidencia requerida.';
  end if;

  if exists (select 1 from blocker where task_id = p_task and resuelto_en is null) then
    return 'La tarea tiene un bloqueo abierto.';
  end if;

  select count(*) into dep_abiertas
    from dependency d join task o on o.id = d.origen_task_id
   where d.destino_task_id = p_task
     and d.tipo = 'bloqueante'
     and o.estado not in ('terminada', 'cancelada');
  if dep_abiertas > 0 then
    return format('Quedan %s dependencias bloqueantes sin resolver.', dep_abiertas);
  end if;

  -- La aprobación de una tarea la da quien revisa el trabajo de su
  -- responsable. Es por persona, no por área: Marcos aprueba a Nahuel aunque
  -- estén en áreas distintas, y a Marcos lo aprueba Dirección.
  select m.aprobador_membership_id into aprobador
    from membership m where m.id = t.responsable_membership_id;

  -- Sólo cuenta si la ÚLTIMA decisión del aprobador sobre esta tarea es
  -- 'aprobado' (review-c112506a): ADR 0009 agregó "Pedir cambios", que
  -- inserta un `approval` 'rechazado' y devuelve la tarea a `en_curso` --
  -- sin este chequeo, una aprobación vieja que no había alcanzado para
  -- cerrar (por ejemplo por un bloqueo abierto)
  -- seguía contando para siempre, y el trabajo corregido podía cerrarse sin
  -- que nadie lo aprobara. Una fila 'aprobado' cuenta sólo si no existe
  -- ningún 'rechazado' del mismo aprobador con `at` posterior o igual: el
  -- empate falla cerrado, nunca aprobado.
  if aprobador is not null
     and not exists (
       select 1 from approval a
        where a.sujeto_tipo = 'tarea' and a.sujeto_id = p_task
          and a.decision = 'aprobado'
          and a.aprobador_membership_id = aprobador
          and not exists (
            select 1 from approval r
             where r.sujeto_tipo = 'tarea' and r.sujeto_id = p_task
               and r.aprobador_membership_id = aprobador
               and r.decision = 'rechazado'
               and r.at >= a.at)) then
    return 'Falta la aprobación de quien revisa ese trabajo.';
  end if;

  return null;
end $$ language plpgsql;

create or replace function puede_ver_tarea(p_membership_id uuid, p_task_id uuid)
returns boolean
language sql stable set search_path = leda, public, pg_temp as $$
  select exists (
    select 1
      from membership m
      join task t on t.workspace_id = m.workspace_id and t.id = p_task_id
      join rol r on r.id = m.rol_id
      join area a on a.id = t.area_id
      left join membership resp on resp.id = t.responsable_membership_id
     where m.id = p_membership_id
       and m.activo
       and (t.responsable_membership_id = m.id
            or resp.aprobador_membership_id = m.id
            or a.referente_membership_id = m.id
            or r.autoridad_final
            or exists (select 1 from approval ap
                        where ap.workspace_id = t.workspace_id
                          and ap.sujeto_tipo = 'tarea' and ap.sujeto_id = t.id
                          and ap.aprobador_membership_id = m.id)));
$$;

create or replace function leer_pagina_de_tarea(p_token_hash text)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        acceso acceso_tarea%rowtype;
        t task%rowtype;
        faltan text[];
        tipos jsonb;
        resultado jsonb;
begin
  acceso := acceso_tarea_vigente(p_token_hash);
  if acceso.id is null then
    perform set_config('leda.workspace_id', previo, true);
    return null;
  end if;
  insert into vista_de_tarea (workspace_id, acceso_tarea_id, que)
       values (acceso.workspace_id, acceso.id, 'pagina');
  select * into t from task where id = acceso.task_id;
  faltan := tipos_de_evidencia_que_faltan(t.id);
  select p.tipos into tipos from task_evidence_policy p
   where p.workspace_id = t.workspace_id and p.area_id = t.area_id;
  select jsonb_build_object(
    'espacio', w.nombre,
    'zona_horaria', w.zona_horaria,
    'persona', (select u.nombre from membership m join app_user u on u.id = m.app_user_id
                 where m.id = acceso.membership_id),
    'tarea', jsonb_build_object(
      'titulo', t.titulo,
      'objetivo', (select o.titulo from objective o where o.id = t.objective_id),
      'area', (select a.nombre from area a where a.id = t.area_id),
      'responsable', (select u.nombre from membership m join app_user u on u.id = m.app_user_id
                       where m.id = t.responsable_membership_id),
      'quien_aprueba', (select u.nombre from membership r
                          join membership m on m.id = r.aprobador_membership_id
                          join app_user u on u.id = m.app_user_id
                         where r.id = t.responsable_membership_id),
      'estado', t.estado,
      'fecha_objetivo', t.fecha_objetivo,
      'criterio_aceptacion', t.criterio_aceptacion,
      'prevision', (select jsonb_build_object('fecha', f.fecha_prevista, 'quien', u.nombre,
                                              'cuando', f.at)
                      from task_forecast f
                      join membership m on m.id = f.dicho_por_membership_id
                      join app_user u on u.id = m.app_user_id
                     where f.task_id = t.id
                       and not exists (select 1 from task_forecast g where g.reemplaza_id = f.id)
                     order by f.at desc limit 1)),
    'pide', coalesce((
      select jsonb_agg(jsonb_build_object(
               'tipo', r.tipo, 'en_palabras', tipos -> r.tipo ->> 'en_palabras',
               'cubierto', not (r.tipo = any(faltan))) order by r.orden)
        from unnest(t.evidencia_requerida) with ordinality as r(tipo, orden)), '[]'::jsonb),
    'historia', coalesce((
      select jsonb_agg(h.dato order by h.cuando, h.orden) from (
        select e.at as cuando, 1 as orden,
               jsonb_build_object('que', 'estado', 'de', e.estado_anterior, 'a', e.estado_nuevo,
                                  'quien', u.nombre, 'actor', e.actor_kind, 'cuando', e.at) as dato
          from task_state_event e left join app_user u on u.id = e.actor_app_user_id
         where e.task_id = t.id
        union all
        select ap.at, 2,
               jsonb_build_object('que', case ap.decision when 'aprobado' then 'aprobacion'
                                                          else 'pedido_de_cambios' end,
                                  'quien', u.nombre, 'comentario', ap.comentario,
                                  'cuando', ap.at)
          from approval ap
          join membership m on m.id = ap.aprobador_membership_id
          join app_user u on u.id = m.app_user_id
         where ap.sujeto_tipo = 'tarea' and ap.sujeto_id = t.id
        union all
        select b.abierto_en, 3,
               jsonb_build_object('que', 'bloqueo', 'causa', b.causa, 'quien', u.nombre,
                                  'cuando', b.abierto_en, 'resuelto_en', b.resuelto_en)
          from blocker b
          left join membership m on m.id = b.abierto_por
          left join app_user u on u.id = m.app_user_id
         where b.task_id = t.id
        union all
        select f.at, 4,
               jsonb_build_object('que', 'prevision', 'fecha', f.fecha_prevista,
                                  'es_correccion', f.es_correccion, 'quien', u.nombre,
                                  'cuando', f.at)
          from task_forecast f
          join membership m on m.id = f.dicho_por_membership_id
          join app_user u on u.id = m.app_user_id
         where f.task_id = t.id) h), '[]'::jsonb),
    'evidencia', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', e.id, 'clase', e.clase, 'texto', e.texto,
               'enlace', case when e.clase = 'enlace' then e.uri end,
               'nombre', a.nombre_original, 'tipo_de_archivo', a.tipo, 'cubre', e.cubre,
               'ejemplo_aceptado', e.es_ejemplo_aceptado, 'quien', u.nombre, 'cuando', e.at,
               'retirada', x.id is not null, 'retirada_el', x.at) order by e.at, e.id)
        from evidence e
        left join archivo a on a.workspace_id = e.workspace_id and a.id = e.archivo_id
        left join membership m on m.id = e.entregado_por
        left join app_user u on u.id = m.app_user_id
        left join evidencia_retirada x on x.evidence_id = e.id
       where e.task_id = t.id), '[]'::jsonb))
    into resultado
    from workspace w where w.id = acceso.workspace_id;
  perform set_config('leda.workspace_id', previo, true);
  return resultado;
end $$;

drop function if exists quien_revisa_la_tarea(uuid);
alter table task drop constraint if exists task_revisa;
alter table task drop column if exists revisa_membership_id;

commit;
