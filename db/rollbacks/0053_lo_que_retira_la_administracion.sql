\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0053_lo_que_retira_la_administracion.sql.
--
-- Devuelve `rechazar_cambios_de_archivo` a como la dejó la 0033 y `leer_pagina_de_tarea` a como la
-- dejó la 0052, y vuelve a hacer obligatorio el contenido de un archivo. Se niega si ya se borró
-- algún contenido o si algo llegó con la huella de uno: el borrado no tiene vuelta atrás, y
-- `contenido` no puede volver a ser obligatorio sin inventar lo que se borró.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception 'rollback 0053 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if exists (select 1 from archivo where contenido is null)
     or exists (select 1 from archivo_de_mensaje where rechazo = 'contenido_retirado') then
    raise exception 'El rollback de la 0053 se niega: la administración ya borró el contenido de algún archivo (no tiene vuelta atrás).';
  end if;
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
  -- La vista de un administrador de plataforma va además a la auditoría (ADR 0019, 7b y 7e;
  -- constitución §12), con la versión del pack del espacio; la del núcleo la pasa quien llama.
  if acceso.admin_app_user_id is not null then
    insert into audit_log (workspace_id, actor_app_user_id, actor_kind, accion, sujeto_tipo,
                           sujeto_id, detalle, pack_hash, nucleo_hash)
    values (acceso.workspace_id, acceso.admin_app_user_id, 'persona', 'ver_pagina_de_tarea',
            'task', acceso.task_id, jsonb_build_object('acceso_tarea_id', acceso.id),
            (select v.pack_hash from workspace_version v
              where v.workspace_id = acceso.workspace_id order by v.version desc limit 1),
            nullif(current_setting('leda.nucleo_hash', true), ''));
  end if;
  select * into t from task where id = acceso.task_id;
  faltan := tipos_de_evidencia_que_faltan(t.id);
  select p.tipos into tipos from task_evidence_policy p
   where p.workspace_id = t.workspace_id and p.area_id = t.area_id;
  select jsonb_build_object(
    'espacio', w.nombre,
    'zona_horaria', w.zona_horaria,
    'persona', coalesce((select u.nombre from membership m
                           join app_user u on u.id = m.app_user_id
                          where m.id = acceso.membership_id),
                        (select u.nombre from app_user u
                          where u.id = acceso.admin_app_user_id)),
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
               'id', e.id, 'clase', e.clase,
               'texto', case when not r.retirada then e.texto end,
               'enlace', case when e.clase = 'enlace' and not r.retirada then e.uri end,
               'nombre', case when not r.retirada then a.nombre_original end,
               'tipo_de_archivo', a.tipo, 'cubre', e.cubre,
               'ejemplo_aceptado', e.es_ejemplo_aceptado, 'quien', u.nombre, 'cuando', e.at,
               'retirada', r.retirada, 'retirada_el', r.retirada_el,
               'retirada_por_la_administracion', r.por_la_administracion)
             order by e.at, e.id)
        from evidence e
        left join archivo a on a.workspace_id = e.workspace_id and a.id = e.archivo_id
        left join membership m on m.id = e.entregado_por
        left join app_user u on u.id = m.app_user_id
        -- Retirada por quien la entregó, o su contenido por la administración: la pieza o
        -- cualquier otra del espacio con el mismo archivo (un archivo se guarda una vez por
        -- huella). De una pieza retirada no sale su contenido (ADR 0019, decisión 3).
        cross join lateral (
          select adm.at is not null or per.at is not null as retirada,
                 coalesce(adm.at, per.at) as retirada_el,
                 adm.at is not null as por_la_administracion
            from (select min(x.at) as at from evidencia_retirada x
                    join evidence o on o.id = x.evidence_id
                   where x.retirada_por_app_user_id is not null
                     and (o.id = e.id
                          or (e.archivo_id is not null and o.workspace_id = e.workspace_id
                              and o.archivo_id = e.archivo_id))) adm,
                 (select min(x.at) as at from evidencia_retirada x
                   where x.evidence_id = e.id
                     and x.retirada_por_membership_id is not null) per) r
       where e.task_id = t.id), '[]'::jsonb))
    into resultado
    from workspace w where w.id = acceso.workspace_id;
  perform set_config('leda.workspace_id', previo, true);
  return resultado;
end $$;
alter function leer_pagina_de_tarea(text) owner to leda_owner;

alter table archivo_de_mensaje drop constraint archivo_de_mensaje_rechazo;
alter table archivo_de_mensaje add constraint archivo_de_mensaje_rechazo check (
    rechazo in ('demasiado_grande', 'tipo_no_admitido'));

create or replace function rechazar_cambios_de_archivo() returns trigger as $$
begin
  raise exception 'archivo: un archivo recibido no se modifica ni se borra';
end $$ language plpgsql;

alter table archivo drop constraint archivo_contenido_o_su_retiro;
alter table archivo drop constraint archivo_tamano_del_contenido;
alter table archivo add constraint archivo_tamano_del_contenido
    check (tamano = octet_length(contenido) and tamano between 1 and 62914560);
alter table archivo drop constraint archivo_huella_del_contenido;
alter table archivo add constraint archivo_huella_del_contenido
    check (sha256 = encode(sha256(contenido), 'hex'));
alter table archivo alter column contenido set not null;
alter table archivo drop column contenido_retirado_en;

commit;
