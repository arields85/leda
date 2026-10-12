\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0062_la_carga_de_tareas_desde_la_web.sql. La sesión y el enlace de la puerta de
-- administración son del otorgamiento del rol en que nacieron (revisión RDD
-- `review-2bb3704b62fcce34` de la 0061; ADR 0022, decisiones 10 y 12).
--
-- La 0061 revalida el rol en cada pedido, pero sólo mira que esté vigente ahora: si a un
-- administrador le revocan el rol y se lo vuelven a otorgar antes del pedido siguiente de su
-- sesión, la sesión vieja seguía abriendo la puerta, y un enlace emitido antes de la revocación
-- todavía se canjeaba. Ahora:
--
-- - `sesion_de_administracion_vigente`: una sesión creada antes del `otorgado_en` del rol
--   `administrador` vigente queda cortada, con el mismo motivo que la de un rol revocado
--   (`dejo_de_ser_administrador`: entre su apertura y hoy, la persona dejó de serlo) y la misma
--   auditoría.
-- - `canjear_enlace_de_administracion`: un enlace emitido antes del otorgamiento vigente no se
--   canjea y queda anulado.
--
-- Revocar es borrar la fila de `platform_role` y otorgar es insertarla (`otorgado_en` es la hora
-- del otorgamiento). Mismas firmas, dueño y privilegios. Se deshace con
-- `db/rollbacks/0063_la_sesion_es_del_rol_vigente.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0063 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0062 está aplicada.
do $$ begin
  if to_regclass('leda.carga_de_tarea') is null
     or to_regprocedure('leda.sesion_de_administracion_vigente(text)') is null then
    raise exception '0063 preflight failed: falta la 0062';
  end if;
end $$;

create or replace function canjear_enlace_de_administracion(
    p_token_hash text, p_sesion_token_hash text)
returns uuid
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare enlace enlace_de_administracion%rowtype;
        otorgado timestamptz;
        nueva uuid;
begin
  if p_token_hash is null or p_token_hash !~ '^[0-9a-f]{64}$'
     or p_sesion_token_hash is null or p_sesion_token_hash !~ '^[0-9a-f]{64}$' then
    return null;
  end if;
  select * into enlace from enlace_de_administracion e where e.token_hash = p_token_hash;
  if enlace.id is null then
    return null;
  end if;
  select p.otorgado_en into otorgado from platform_role p
   where p.app_user_id = enlace.app_user_id and p.rol = 'administrador';
  if otorgado is null then
    return null;
  end if;
  -- Emitido antes del otorgamiento vigente (el rol se revocó y se volvió a otorgar): no se
  -- canjea, y queda anulado.
  if enlace.emitido_en < otorgado then
    update enlace_de_administracion set anulado_en = now()
     where id = enlace.id and canjeado_en is null and anulado_en is null;
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
        otorgado timestamptz;
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
  -- queda cortada. Si vuelve a serlo, pide un enlace nuevo. La sesión es del otorgamiento en que
  -- se abrió: una anterior al vigente (el rol se revocó y se volvió a otorgar sin que la sesión
  -- pidiera nada en el medio) también queda cortada.
  select p.otorgado_en into otorgado from platform_role p
   where p.app_user_id = sesion.app_user_id and p.rol = 'administrador';
  if otorgado is null or sesion.creada_en < otorgado then
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

-- `create or replace` conserva dueño y privilegios; se repiten para que la migración no dependa
-- de eso.
alter function canjear_enlace_de_administracion(text, text) owner to leda_owner;
alter function sesion_de_administracion_vigente(text) owner to leda_owner;
revoke execute on function canjear_enlace_de_administracion(text, text) from public;
revoke execute on function sesion_de_administracion_vigente(text) from public;
grant execute on function canjear_enlace_de_administracion(text, text) to leda_app;
grant execute on function sesion_de_administracion_vigente(text) to leda_app;

commit;
