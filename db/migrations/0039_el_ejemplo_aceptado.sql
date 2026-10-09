\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0038_lo_que_describe_cada_pieza.sql. El ejemplo aceptado de una entrega (D8 de
-- `odd/tasks/fase-c.md`, G2; prueba por Telegram del 2026-10-08).
--
-- Cuando a una entrega le falta algo del criterio de aceptación, Leda propone un ejemplo que la
-- persona acepta o reemplaza por el suyo (decisión 10 del usuario, 2026-10-08). Aceptado, el
-- ejemplo se guardaba como un texto más de la entrega, y quien la revisa leía que la persona lo
-- había escrito ("Marcos escribió que…"). Cada pieza guarda ahora si es un ejemplo que la persona
-- aceptó (`es_ejemplo_aceptado`): vale como lo que describe, pero no lo escribió ella. La página
-- de la tarea lo recibe (`leer_pagina_de_tarea`, `ejemplo_aceptado`) y lo dice así.
--
-- - Sólo un texto puede ser un ejemplo aceptado (`evidence_ejemplo_solo_un_texto`).
-- - Las filas de antes quedan con `false`: no se sabe cuáles lo eran, y no se inventa.
-- - Como el resto de `evidence`, la columna sólo se agrega: `leda_app` no tiene `update` y el
--   disparador `rechazar_cambios_de_evidencia` rechaza cualquier cambio.
--
-- Se deshace con `db/rollbacks/0039_el_ejemplo_aceptado.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0039 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la evidencia ya dice lo que describe cada pieza (migración 0038) y todavía no la
-- columna nueva.
do $$ begin
  if not exists (select 1 from information_schema.columns
                  where table_schema = 'leda' and table_name = 'evidence'
                    and column_name = 'describe_del_criterio') then
    raise exception '0039 preflight failed: falta la 0038 (evidence.describe_del_criterio)';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'evidence'
                and column_name = 'es_ejemplo_aceptado') then
    raise exception '0039 preflight failed: evidence.es_ejemplo_aceptado ya existe';
  end if;
end $$;

alter table evidence
  add column es_ejemplo_aceptado boolean not null default false,
  add constraint evidence_ejemplo_solo_un_texto
    check (clase = 'texto' or not es_ejemplo_aceptado);

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

alter function leer_pagina_de_tarea(text) owner to leda_owner;
revoke execute on function leer_pagina_de_tarea(text) from public;
grant execute on function leer_pagina_de_tarea(text) to leda_app;

commit;
