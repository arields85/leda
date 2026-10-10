\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0052_el_acceso_del_administrador.sql.
--
-- Devuelve `acceso_tarea_vigente`, `leer_pagina_de_tarea` y `leer_archivo_de_tarea` a como las
-- dejaron la 0036 y la 0051, borra la guarda y las columnas nuevas y vuelve a poner
-- `evidencia_retirada_una_vez`. Se niega si hay un acceso de un administrador o un retiro de la
-- administración: borrarlos perdería auditoría (constitución §12).
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception 'rollback 0052 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if exists (select 1 from acceso_tarea where admin_app_user_id is not null)
     or exists (select 1 from evidencia_retirada where retirada_por_app_user_id is not null) then
    raise exception 'El rollback de la 0052 se niega: hay accesos de un administrador de plataforma o retiros de contenido por la administración.';
  end if;
end $$;

create or replace function acceso_tarea_vigente(p_token_hash text)
returns acceso_tarea
language plpgsql set search_path = leda, public, pg_temp as $$
declare acceso acceso_tarea%rowtype;
begin
  if p_token_hash is null or p_token_hash !~ '^[0-9a-f]{64}$' then
    return null;
  end if;
  perform set_config('leda.token_de_tarea', p_token_hash, true);
  select * into acceso from acceso_tarea a
   where a.token_hash = p_token_hash and a.revocado_en is null;
  perform set_config('leda.token_de_tarea', '', true);
  if acceso.id is null then
    return null;
  end if;
  perform set_config('leda.workspace_id', acceso.workspace_id::text, true);
  if not puede_ver_tarea(acceso.membership_id, acceso.task_id) then
    return null;
  end if;
  return acceso;
end $$;

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
      'quien_aprueba', (select u.nombre from membership m
                          join app_user u on u.id = m.app_user_id
                         where m.id = quien_revisa_la_tarea(t.id)),
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
         where f.task_id = t.id
        union all
        select u.at, 5,
               jsonb_build_object('que', 'quien_destraba', 'quien', pu.nombre,
                                  'destraba', coalesce(du.nombre, u.destraba_externo),
                                  'no_sabe', u.no_sabe,
                                  'nadie_mas', u.destraba_membership_id
                                               = u.dicho_por_membership_id,
                                  'cuando', u.at)
          from blocker_unblocker u
          join blocker b on b.id = u.blocker_id
          join membership pm on pm.id = u.dicho_por_membership_id
          join app_user pu on pu.id = pm.app_user_id
          left join membership dm on dm.id = u.destraba_membership_id
          left join app_user du on du.id = dm.app_user_id
         where b.task_id = t.id
           and not u.sin_decir_quien
        union all
        select d.at, 6,
               jsonb_build_object('que', 'dicho_del_bloqueo', 'quien', pu.nombre,
                                  'para_cuando', d.para_cuando, 'ya_esta', d.ya_esta,
                                  'no_le_corresponde', d.no_le_corresponde,
                                  'lo_que_dice', d.lo_que_dice, 'cuando', d.at)
          from dicho_de_quien_destraba d
          join blocker_unblocker u on u.id = d.blocker_unblocker_id
          join blocker b on b.id = u.blocker_id
          join membership pm on pm.id = d.dicho_por_membership_id
          join app_user pu on pu.id = pm.app_user_id
         where b.task_id = t.id
        union all
        select coalesce((a.detalle ->> 'at')::timestamptz, a.at), 7,
               jsonb_build_object('que', 'asentado',
                                  'por', case a.accion
                                           when 'asentar_bloqueo_que_sigue_abierto'
                                             then 'sigue_trabada'
                                           else 'nadie_lo_toma' end,
                                  'dias_habiles', (a.detalle ->> 'dias_habiles_trabada')::int,
                                  'cuando', coalesce((a.detalle ->> 'at')::timestamptz, a.at))
          from audit_log a
          join blocker b on b.id = a.sujeto_id
         where a.sujeto_tipo = 'blocker' and b.task_id = t.id
           and a.accion in ('asentar_bloqueo_que_sigue_abierto',
                            'informar_la_cadena_del_bloqueo',
                            'asentar_la_cadena_del_bloqueo')) h), '[]'::jsonb),
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

create or replace function leer_archivo_de_tarea(p_token_hash text, p_evidence_id uuid)
returns table (archivo_contenido bytea, archivo_tipo text, archivo_clase text,
               archivo_nombre text)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        acceso acceso_tarea%rowtype;
        v_contenido bytea;
        v_tipo text;
        v_clase text;
        v_nombre text;
begin
  acceso := acceso_tarea_vigente(p_token_hash);
  if acceso.id is not null then
    select a.contenido, a.tipo, a.clase, a.nombre_original
      into v_contenido, v_tipo, v_clase, v_nombre
      from evidence e
      join archivo a on a.workspace_id = e.workspace_id and a.id = e.archivo_id
     where e.id = p_evidence_id
       and e.workspace_id = acceso.workspace_id
       and e.task_id = acceso.task_id
       and not exists (select 1 from evidencia_retirada x where x.evidence_id = e.id);
    if v_contenido is not null then
      insert into vista_de_tarea (workspace_id, acceso_tarea_id, que, evidence_id)
           values (acceso.workspace_id, acceso.id, 'archivo', p_evidence_id);
    end if;
  end if;
  perform set_config('leda.workspace_id', previo, true);
  if v_contenido is not null then
    return query select v_contenido, v_tipo, v_clase, v_nombre;
  end if;
end $$;

alter function acceso_tarea_vigente(text) owner to leda_owner;
alter function leer_pagina_de_tarea(text) owner to leda_owner;
alter function leer_archivo_de_tarea(text, uuid) owner to leda_owner;

drop trigger trg_exigir_administrador_de_plataforma on acceso_tarea;
drop trigger trg_exigir_administrador_de_plataforma on evidencia_retirada;
drop function exigir_administrador_de_plataforma();

drop index evidencia_retirada_una_vez_por_quien_la_entrego;
drop index evidencia_retirada_una_vez_por_la_administracion;
alter table evidencia_retirada drop constraint evidencia_retirada_de_quien;
alter table evidencia_retirada drop column retirada_por_app_user_id;
alter table evidencia_retirada alter column retirada_por_membership_id set not null;
alter table evidencia_retirada add constraint evidencia_retirada_una_vez unique (evidence_id);
comment on table evidencia_retirada is
  'ADR 0019, decisión 3: una pieza de evidencia retirada por quien la entregó, mientras la tarea no está aprobada. Sólo se agrega; la evidencia no se borra y deja de contar para la política.';

alter table acceso_tarea drop constraint acceso_tarea_de_quien;
alter table acceso_tarea drop column admin_app_user_id;
alter table acceso_tarea alter column membership_id set not null;
comment on table acceso_tarea is
  'ADR 0019, decisión 7a: el enlace personal a la página de una tarea. Sólo el hash del token; sin vencimiento; el derecho a ver se revalida en cada pedido. leda_app no tiene privilegios: sólo execute sobre sus funciones.';

commit;
