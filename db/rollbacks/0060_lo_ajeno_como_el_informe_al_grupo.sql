\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0060_lo_ajeno_como_el_informe_al_grupo.sql.
--
-- Vuelve a dejar `tareas_que_ve` y `tareas_de_la_sesion` como las dejó la 0058 (sin la
-- previsión, y sin el atraso ni el bloqueo para quien no ve los atrasos de la tarea), borra las
-- dos funciones de las terminadas y la restricción del usuario del bot. Antes, borra los ajustes
-- `bot_usuario` que haya: son del pack, que los vuelve a cargar al importarse con la 0060. No
-- guardan otros datos: no se pierde nada más.
begin;
set search_path = leda, public;

drop function if exists terminadas_de_la_sesion(text, text, timestamptz);
drop function if exists terminadas_que_ve(uuid, text, timestamptz);
drop function if exists tareas_de_la_sesion(text, text, timestamptz);
drop function if exists tareas_que_ve(uuid, text, timestamptz);

delete from workspace_setting where clave = 'bot_usuario';
alter table workspace_setting drop constraint if exists workspace_setting_bot_usuario;

-- Las dos de la 0058, como estaban.
create or replace function tareas_que_ve(
    p_membership_id uuid, p_vista text, p_ahora timestamptz)
returns table (task_id uuid, titulo text, estado text, fecha_objetivo timestamptz,
               asignada_en timestamptz, responsable text, area text, papel text,
               vencida boolean, bloqueo_abierto boolean, ve_la_pagina boolean)
language sql stable set search_path = leda, public, pg_temp as $$
  with yo as (
    select m.id, m.workspace_id, r.autoridad_final
      from membership m
      join rol r on r.id = m.rol_id
     where m.id = p_membership_id and m.activo
  ),
  abiertas as (
    select t.id, t.workspace_id, t.titulo, t.estado, t.fecha_objetivo, t.creado_en,
           t.area_id, t.responsable_membership_id
      from task t
      join yo on yo.workspace_id = t.workspace_id
     where t.estado not in ('terminada', 'cancelada')
  ),
  -- Quién destraba hoy cada bloqueo abierto: lo último que se dijo.
  destraba as (
    select b.id as blocker_id, b.task_id, u.destraba_membership_id
      from blocker b
      join lateral (select x.destraba_membership_id from blocker_unblocker x
                     where x.blocker_id = b.id
                     order by x.at desc, x.id desc limit 1) u on true
     where b.resuelto_en is null
  ),
  -- Una tarea que espera otra: una dependencia bloqueante, o el bloqueo con el que dijo estar
  -- trabado quien destraba (`dicho_de_quien_destraba.espera_su_bloqueo_id`, 0044).
  esperas as (
    select d.destino_task_id as espera, d.origen_task_id as esperada
      from dependency d
     where d.tipo = 'bloqueante'
    union
    select b.task_id, y.task_id
      from destraba b
      join blocker_unblocker x on x.blocker_id = b.blocker_id
      join dicho_de_quien_destraba dd on dd.blocker_unblocker_id = x.id
      join blocker y on y.id = dd.espera_su_bloqueo_id
      join task o on o.id = y.task_id
     where b.destraba_membership_id = o.responsable_membership_id
       and dd.dicho_por_membership_id = o.responsable_membership_id
  ),
  filas as (
    select t.*, a.nombre as area_nombre, a.referente_membership_id,
           case
             when t.responsable_membership_id = yo.id then 'mia'
             when exists (select 1 from destraba b
                           where b.task_id = t.id and b.destraba_membership_id = yo.id)
                  or exists (select 1 from esperas e
                               join abiertas o on o.id = e.esperada
                              where e.espera = t.id and o.responsable_membership_id = yo.id)
                  or (t.estado = 'en_revision' and quien_revisa_la_tarea(t.id) = yo.id)
               then 'me_esperan'
             when exists (select 1 from esperas e
                            join abiertas w on w.id = e.espera
                           where e.esperada = t.id and w.responsable_membership_id = yo.id)
               then 'espero'
           end as papel,
           coalesce(t.responsable_membership_id = yo.id
                    or a.referente_membership_id = yo.id
                    or yo.autoridad_final, false) as ve_atrasos,
           yo.autoridad_final as es_autoridad,
           yo.id as yo_id
      from abiertas t
      cross join yo
      join area a on a.id = t.area_id
  )
  select f.id, f.titulo, f.estado::text, f.fecha_objetivo,
         coalesce((select min(e.at) from task_state_event e
                    where e.task_id = f.id and e.estado_nuevo = 'asignada'), f.creado_en),
         u.nombre, f.area_nombre, f.papel,
         case when f.ve_atrasos then
           coalesce(f.estado in ('asignada', 'en_curso', 'bloqueada')
                    and (f.fecha_objetivo at time zone w.zona_horaria)::date
                        < (coalesce(p_ahora, now()) at time zone w.zona_horaria)::date,
                    false)
         end,
         case when f.ve_atrasos then
           exists (select 1 from blocker b where b.task_id = f.id and b.resuelto_en is null)
         end,
         puede_ver_tarea(f.yo_id, f.id)
    from filas f
    join workspace w on w.id = f.workspace_id
    left join membership rm on rm.id = f.responsable_membership_id
    left join app_user u on u.id = rm.app_user_id
   where case p_vista
           when 'tus' then f.papel is not null
           when 'sector' then f.referente_membership_id = f.yo_id
           when 'equipo' then f.es_autoridad
           else false
         end
   order by f.fecha_objetivo nulls last, f.titulo, f.id;
$$;

create or replace function tareas_de_la_sesion(
    p_token_hash text, p_vista text, p_ahora timestamptz)
returns table (task_id uuid, titulo text, estado text, fecha_objetivo timestamptz,
               asignada_en timestamptz, responsable text, area text, papel text,
               vencida boolean, bloqueo_abierto boolean, ve_la_pagina boolean)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare persona uuid;
begin
  if p_vista is null or p_vista not in ('tus', 'sector', 'equipo') then
    raise exception 'tareas_de_la_sesion: vista desconocida';
  end if;
  -- La persona sale de la sesión, que deja fijado su espacio; si no entra, nada.
  select s.membership_id into persona from sesion_vigente(p_token_hash) s;
  if persona is null then
    return;
  end if;
  return query select q.* from tareas_que_ve(persona, p_vista, p_ahora) q;
end $$;

alter function tareas_que_ve(uuid, text, timestamptz) owner to leda_owner;
alter function tareas_de_la_sesion(text, text, timestamptz) owner to leda_owner;

revoke execute on function tareas_que_ve(uuid, text, timestamptz) from public;
revoke execute on function tareas_de_la_sesion(text, text, timestamptz) from public;
grant execute on function tareas_de_la_sesion(text, text, timestamptz) to leda_app;

commit;
