\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0063_la_sesion_es_del_rol_vigente.sql.
--
-- Devuelve `canjear_enlace_de_administracion` y `sesion_de_administracion_vigente` a como las
-- dejó la 0061 (sólo miran que el rol esté vigente ahora). No toca datos: las sesiones cortadas
-- y los enlaces anulados por la 0063 siguen así, y su auditoría queda.
begin;
set search_path = leda, public;

create or replace function canjear_enlace_de_administracion(
    p_token_hash text, p_sesion_token_hash text)
returns uuid
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare enlace enlace_de_administracion%rowtype;
        nueva uuid;
begin
  if p_token_hash is null or p_token_hash !~ '^[0-9a-f]{64}$'
     or p_sesion_token_hash is null or p_sesion_token_hash !~ '^[0-9a-f]{64}$' then
    return null;
  end if;
  select * into enlace from enlace_de_administracion e where e.token_hash = p_token_hash;
  if enlace.id is null or not es_administrador_de_plataforma(enlace.app_user_id) then
    return null;
  end if;
  -- Una sola vez: si llegan dos canjes a la vez, el segundo espera el candado de la fila y ya no
  -- la encuentra sin canjear.
  update enlace_de_administracion set canjeado_en = now()
   where id = enlace.id and canjeado_en is null and anulado_en is null;
  if not found then
    return null;
  end if;
  insert into sesion_de_administracion (app_user_id, enlace_id, token_hash)
       values (enlace.app_user_id, enlace.id, p_sesion_token_hash)
    returning id into nueva;
  perform auditar_acceso_de_administracion(
    enlace.app_user_id, 'persona', 'canjear_enlace_de_administracion',
    'sesion_de_administracion', nueva, jsonb_build_object('enlace_id', enlace.id));
  return nueva;
end $$;

create or replace function sesion_de_administracion_vigente(p_token_hash text)
returns table (sesion_id uuid, app_user_id uuid, nombre text)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare sesion sesion_de_administracion%rowtype;
begin
  if p_token_hash is null or p_token_hash !~ '^[0-9a-f]{64}$' then
    return;
  end if;
  select * into sesion from sesion_de_administracion s
   where s.token_hash = p_token_hash and s.cortada_en is null;
  if sesion.id is null then
    return;
  end if;
  -- El rol se revalida en cada pedido: quien dejó de ser administrador ya no entra, y su sesión
  -- queda cortada. Si vuelve a serlo, pide un enlace nuevo.
  if not es_administrador_de_plataforma(sesion.app_user_id) then
    update sesion_de_administracion s
       set cortada_en = now(), motivo_de_corte = 'dejo_de_ser_administrador'
     where s.id = sesion.id and s.cortada_en is null;
    if found then
      perform auditar_acceso_de_administracion(
        null, 'sistema', 'cortar_sesion_de_administracion', 'sesion_de_administracion',
        sesion.id, jsonb_build_object('motivo', 'dejo_de_ser_administrador',
                                      'app_user_id', sesion.app_user_id));
    end if;
    return;
  end if;
  -- Cortada mientras tanto: no entra.
  update sesion_de_administracion s set ultimo_uso_en = now()
   where s.id = sesion.id and s.cortada_en is null;
  if not found then
    return;
  end if;
  return query select sesion.id, sesion.app_user_id, u.nombre
                 from app_user u where u.id = sesion.app_user_id;
end $$;

alter function canjear_enlace_de_administracion(text, text) owner to leda_owner;
alter function sesion_de_administracion_vigente(text) owner to leda_owner;
revoke execute on function canjear_enlace_de_administracion(text, text) from public;
revoke execute on function sesion_de_administracion_vigente(text) from public;
grant execute on function canjear_enlace_de_administracion(text, text) to leda_app;
grant execute on function sesion_de_administracion_vigente(text) to leda_app;

commit;
