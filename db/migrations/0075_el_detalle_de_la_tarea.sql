\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0074_la_revision_de_la_entrada_con_telegram.sql. El detalle completo de una tarea
-- (MA-2; prueba en el celular de la J4, hallazgo 9): la página que abren las tarjetas y "Ver la
-- tarea" dice también quién la pidió, lo que espera y lo que la espera, con la misma regla de quién
-- ve qué que la página (`puede_ver_tarea`). Una función nueva, aparte de `leer_pagina_de_tarea`,
-- que no cambia.
--
-- Se deshace con `db/rollbacks/0075_el_detalle_de_la_tarea.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0075 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0071 (quién la pidió) está aplicada y la 0075 no.
do $$ begin
  if not exists (select 1 from information_schema.columns
                  where table_schema = 'leda' and table_name = 'task'
                    and column_name = 'pedida_por_membership_id') then
    raise exception '0075 requires 0071 (task.pedida_por_membership_id)';
  end if;
  if to_regprocedure('leda.relaciones_de_la_pagina_de_tarea(text)') is not null then
    raise exception '0075 is already applied';
  end if;
end $$;

-- Lo que la página de una tarea suma desde la 0075 (MA-2; prueba en el celular de la J4, hallazgo
-- 9): quién la pidió, lo que espera y lo que la espera, con el mismo token y la misma regla que la
-- página (`acceso_tarea_vigente`: quien ya no puede verla, nada). De cada tarea relacionada, el
-- título, el estado y quién la hace sólo si quien mira también puede verla (`puede_ver_tarea`; un
-- administrador de plataforma, todas); si no, sólo que hay una tarea que no ve. Sólo las esperas
-- que traban (`bloqueante`). No deja una vista registrada: la deja `leer_pagina_de_tarea`.
create or replace function relaciones_de_la_pagina_de_tarea(p_token_hash text)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        acceso acceso_tarea%rowtype;
        resultado jsonb;
begin
  acceso := acceso_tarea_vigente(p_token_hash);
  if acceso.id is null then
    perform set_config('leda.workspace_id', previo, true);
    return null;
  end if;
  select jsonb_build_object(
    'pidio', (select u.nombre from membership m join app_user u on u.id = m.app_user_id
               where m.id = t.pedida_por_membership_id),
    'volver', case when acceso.admin_app_user_id is not null then '/app/admin/'
                   else '/app/e/' || w.slug || '/' end,
    'espera_a', coalesce((
      select jsonb_agg(r.dato order by r.ve desc, r.titulo, r.id) from (
        select o.id, o.titulo, v.ve,
               case when v.ve then jsonb_build_object(
                      've', true, 'titulo', o.titulo, 'estado', o.estado,
                      'responsable', (select u.nombre from membership m
                                        join app_user u on u.id = m.app_user_id
                                       where m.id = o.responsable_membership_id))
                    else jsonb_build_object('ve', false) end as dato
          from dependency d
          join task o on o.id = d.origen_task_id and o.workspace_id = d.workspace_id
          cross join lateral (
            select acceso.admin_app_user_id is not null
                   or puede_ver_tarea(acceso.membership_id, o.id) as ve) v
         where d.workspace_id = acceso.workspace_id and d.destino_task_id = t.id
           and d.tipo = 'bloqueante') r), '[]'::jsonb),
    'la_esperan', coalesce((
      select jsonb_agg(r.dato order by r.ve desc, r.titulo, r.id) from (
        select o.id, o.titulo, v.ve,
               case when v.ve then jsonb_build_object(
                      've', true, 'titulo', o.titulo, 'estado', o.estado,
                      'responsable', (select u.nombre from membership m
                                        join app_user u on u.id = m.app_user_id
                                       where m.id = o.responsable_membership_id))
                    else jsonb_build_object('ve', false) end as dato
          from dependency d
          join task o on o.id = d.destino_task_id and o.workspace_id = d.workspace_id
          cross join lateral (
            select acceso.admin_app_user_id is not null
                   or puede_ver_tarea(acceso.membership_id, o.id) as ve) v
         where d.workspace_id = acceso.workspace_id and d.origen_task_id = t.id
           and d.tipo = 'bloqueante') r), '[]'::jsonb))
    into resultado
    from task t join workspace w on w.id = t.workspace_id
   where t.id = acceso.task_id and t.workspace_id = acceso.workspace_id;
  perform set_config('leda.workspace_id', previo, true);
  return resultado;
end $$;

alter function relaciones_de_la_pagina_de_tarea(text) owner to leda_owner;
revoke execute on function relaciones_de_la_pagina_de_tarea(text) from public;
grant execute on function relaciones_de_la_pagina_de_tarea(text) to leda_app;

commit;
