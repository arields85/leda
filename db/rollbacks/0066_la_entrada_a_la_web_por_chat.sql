\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0066_la_entrada_a_la_web_por_chat.sql.
--
-- Borra `entro_a_la_web`, `tiene_un_enlace_sin_usar`, `ofrecimiento_web` y
-- `message_outbox_entrada_web`, y devuelve `cortar_sesiones_de_membresia` a como la dejó la 0057
-- (sin la fila del corte cuando no había sesiones). Se niega a correr si eso perdiera datos: una
-- marca del enlace de entrada (un mensaje que dice que lleva el enlace saldría sin él) o un
-- ofrecimiento (se le volvería a ofrecer la web a quien ya se le ofreció). Lo que quedó en
-- `audit_log` no se toca. Antes de correrlo en una base con datos, `pg_dump` de esas tablas y
-- vaciarlas a mano, con la decisión registrada.
begin;
set search_path = leda, public;
-- Las comprobaciones de abajo tienen que ver todas las filas: sin la RLS. Un rol que no la
-- saltea falla acá en lugar de ver las tablas vacías y borrar lo que no vio.
set local row_security = off;

do $$ begin
  if to_regclass('leda.message_outbox_entrada_web') is not null and (
       exists (select 1 from message_outbox_entrada_web)
       or exists (select 1 from ofrecimiento_web)) then
    raise exception '0066 rollback refused: hay marcas del enlace de entrada o ofrecimientos de la web';
  end if;
end $$;

create or replace function cortar_sesiones_de_membresia(
    p_membership_id uuid, p_motivo text, p_actor_app_user_id uuid)
returns integer
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare cortada record;
        cortadas integer := 0;
begin
  if p_motivo is null or p_motivo not in (
       'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_el_equipo') then
    raise exception 'cortar_sesiones_de_membresia: motivo desconocido';
  end if;
  -- Con las sesiones, el enlace que estaba sin usar: si se perdió el celular, el mensaje con el
  -- enlace también.
  update enlace_de_entrada e set anulado_en = now()
   where e.membership_id = p_membership_id and e.canjeado_en is null and e.anulado_en is null;
  for cortada in
    update sesion_web s set cortada_en = now(), motivo_de_corte = p_motivo
     where s.membership_id = p_membership_id and s.cortada_en is null
    returning s.id, s.workspace_id, s.membership_id
  loop
    perform auditar_acceso_web(
      cortada.workspace_id, p_actor_app_user_id,
      case when p_actor_app_user_id is null then 'leda' else 'persona' end::tipo_actor,
      'cortar_sesion_web', 'sesion_web', cortada.id,
      jsonb_build_object('motivo', p_motivo, 'membership_id', cortada.membership_id));
    cortadas := cortadas + 1;
  end loop;
  return cortadas;
end $$;

alter function cortar_sesiones_de_membresia(uuid, text, uuid) owner to leda_owner;
revoke execute on function cortar_sesiones_de_membresia(uuid, text, uuid) from public;
grant execute on function cortar_sesiones_de_membresia(uuid, text, uuid) to leda_app;

drop function if exists tiene_un_enlace_sin_usar(uuid);
drop function if exists entro_a_la_web(uuid);

drop table if exists ofrecimiento_web;
drop table if exists message_outbox_entrada_web;

commit;
