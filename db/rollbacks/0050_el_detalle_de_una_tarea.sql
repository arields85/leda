\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0050_el_detalle_de_una_tarea.sql.
--
-- Devuelve `puede_ver_tarea` a como la dejó la 0045 (lo compartido deja de contar para ver la
-- página) y borra los pedidos del detalle y las tareas compartidas, con sus disparadores. Se niega
-- si hay alguna tarea compartida o algún pedido: borrarlos perdería quién compartió qué con quién,
-- que es auditoría (constitución §12).
begin;
set search_path = leda, public;

do $$ begin
  if exists (select 1 from tarea_compartida) or exists (select 1 from pedido_de_detalle) then
    raise exception 'El rollback de la 0050 se niega: hay pedidos del detalle o tareas compartidas.';
  end if;
end $$;

create or replace function puede_ver_tarea(p_membership_id uuid, p_task_id uuid)
returns boolean
language sql stable set search_path = leda, public, pg_temp as $$
  select exists (
    select 1
      from membership m
      join task t on t.workspace_id = m.workspace_id and t.id = p_task_id
      join rol r on r.id = m.rol_id
      join area a on a.id = t.area_id
     where m.id = p_membership_id
       and m.activo
       and (t.responsable_membership_id = m.id
            or quien_revisa_la_tarea(t.id) = m.id
            or a.referente_membership_id = m.id
            or r.autoridad_final
            or exists (select 1 from approval ap
                        where ap.workspace_id = t.workspace_id
                          and ap.sujeto_tipo = 'tarea' and ap.sujeto_id = t.id
                          and ap.aprobador_membership_id = m.id)));
$$;

alter function puede_ver_tarea(uuid, uuid) owner to leda_owner;
revoke execute on function puede_ver_tarea(uuid, uuid) from public;
grant execute on function puede_ver_tarea(uuid, uuid) to leda_app;

drop table tarea_compartida;
drop table pedido_de_detalle;
drop function vigilar_tarea_compartida();
drop function vigilar_pedido_de_detalle();

commit;
