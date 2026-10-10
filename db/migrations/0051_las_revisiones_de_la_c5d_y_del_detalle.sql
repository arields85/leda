\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0050_el_detalle_de_una_tarea.sql. Lo que dejaron las revisiones de la C-5d y del
-- detalle a pedido (2026-10-09; `odd/tasks/fase-c.md`).
--
-- 1. Quien habla de un bloqueo sin decir quién lo destraba (`blocker_unblocker.sin_decir_quien`;
--    decisión 41, revisión de la C-5d): a quien Leda le informó que una tarea sigue trabada puede
--    decir algo de eso ("llega mañana") aunque nadie haya dicho nunca quién la destraba. Lo que
--    dice queda anotado sobre una fila que dice eso mismo: que habló sin decir quién la destraba.
--    Antes, la fila decía que la destrababa esa persona, un hecho que nadie dijo (constitución
--    §4). Es la cuarta forma de la fila: exactamente una de las cuatro. La historia de la página
--    de la tarea (`leer_pagina_de_tarea`) no la muestra como quién la destraba; lo que dijo, sí.
-- 2. El pedido del detalle sigue al encargado de ahora (decisión 33, con la 16 y la 43; revisión
--    del detalle a pedido): lo decide el encargado del sector de la tarea en el momento de
--    decidir, nunca uno anterior, ni que sí ni que no. Queda escrito quién lo decidió
--    (`decidido_por_membership_id`) y la base lo comprueba (`vigilar_pedido_de_detalle`).
--    `decide_membership_id` sigue siendo a quién se le preguntó al pedirlo.
-- 3. Un pedido que nadie contesta termina (decisión 26, la misma regla que los pases): el estado
--    `sin_respuesta`.
--
-- Aislamiento: sin tablas nuevas; la referencia nueva es con el espacio. La página sigue siendo
-- de `leda_owner`, `security definer`, con sus mismos privilegios.
--
-- Se deshace con `db/rollbacks/0051_las_revisiones_de_la_c5d_y_del_detalle.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0051 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0050 está aplicada y la 0051 no.
do $$ begin
  if to_regclass('leda.tarea_compartida') is null then
    raise exception '0051 preflight failed: falta la 0050 (el detalle de una tarea)';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'blocker_unblocker'
                and column_name = 'sin_decir_quien') then
    raise exception '0051 ya está aplicada.';
  end if;
end $$;

-- 1. Quien habla de un bloqueo sin decir quién lo destraba.
alter table blocker_unblocker add column sin_decir_quien boolean not null default false;
alter table blocker_unblocker drop constraint blocker_unblocker_exactamente_uno;
alter table blocker_unblocker add constraint blocker_unblocker_exactamente_uno check (
    (destraba_membership_id is not null)::int
    + (destraba_externo is not null)::int
    + no_sabe::int
    + sin_decir_quien::int = 1);

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

alter function leer_pagina_de_tarea(text) owner to leda_owner;
revoke execute on function leer_pagina_de_tarea(text) from public;
grant execute on function leer_pagina_de_tarea(text) to leda_app;

-- 2 y 3. El pedido del detalle: quién lo decidió (el encargado de ahora) y sin respuesta.
alter table pedido_de_detalle add column decidido_por_membership_id uuid;
alter table pedido_de_detalle add constraint pedido_de_detalle_decidido_por
  foreign key (workspace_id, decidido_por_membership_id) references membership(workspace_id, id);
-- Los ya decididos los decidió a quien se le preguntó: hasta la 0051 nadie más podía.
alter table pedido_de_detalle disable trigger trg_vigilar_pedido_de_detalle;
update pedido_de_detalle set decidido_por_membership_id = decide_membership_id
 where estado in ('compartida', 'no_compartida');
alter table pedido_de_detalle enable trigger trg_vigilar_pedido_de_detalle;
alter table pedido_de_detalle add constraint pedido_de_detalle_quien_lo_decidio check (
    (estado in ('compartida', 'no_compartida')) = (decidido_por_membership_id is not null));
alter table pedido_de_detalle drop constraint pedido_de_detalle_estado_check;
alter table pedido_de_detalle add constraint pedido_de_detalle_estado_check check (estado in (
    'esperando_decision', 'compartida', 'no_compartida', 'sin_efecto', 'sin_respuesta'));

create or replace function vigilar_pedido_de_detalle() returns trigger as $$
declare encargado uuid;
begin
  select a.referente_membership_id into encargado
    from task t join area a on a.id = t.area_id
   where t.id = new.task_id and t.workspace_id = new.workspace_id;
  if tg_op = 'INSERT' then
    if new.estado <> 'esperando_decision' then
      raise exception 'pedido_de_detalle: un pedido nuevo espera la decisión';
    end if;
    if new.decide_membership_id is distinct from encargado then
      raise exception 'pedido_de_detalle: lo decide el encargado del sector de la tarea';
    end if;
    return new;
  end if;
  if new.workspace_id is distinct from old.workspace_id
     or new.task_id is distinct from old.task_id
     or new.pedido_por_membership_id is distinct from old.pedido_por_membership_id
     or new.decide_membership_id is distinct from old.decide_membership_id
     or new.pedido_en is distinct from old.pedido_en then
    raise exception 'pedido_de_detalle: los datos del pedido no cambian';
  end if;
  if old.estado <> 'esperando_decision' and new is distinct from old then
    raise exception 'pedido_de_detalle: el pedido ya terminó';
  end if;
  -- Lo decide el encargado de ahora del sector de la tarea, nunca uno anterior: el pedido sigue
  -- al encargado (migración 0051).
  if new.estado in ('compartida', 'no_compartida')
     and new.decidido_por_membership_id is distinct from encargado then
    raise exception 'pedido_de_detalle: lo decide el encargado de ahora del sector de la tarea';
  end if;
  return new;
end $$ language plpgsql;

commit;
