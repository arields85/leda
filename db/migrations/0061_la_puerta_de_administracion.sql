\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0060_lo_ajeno_como_el_informe_al_grupo.sql. El enlace de un solo uso y la sesión
-- de la puerta de administración de la plataforma web (ADR 0022, decisiones 10, 11 y 12; porción
-- 2, tarea P2-1 de `odd/tasks/plataforma-p2.md`).
--
-- - Sin espacio: un administrador de plataforma abarca todos los espacios, así que su enlace y su
--   sesión no caben en `enlace_de_entrada` ni en `sesion_web` (que son de una membresía). Tablas
--   propias, de un `app_user`, sin `workspace_id` y sin política por espacio: `leda_app` no tiene
--   ningún privilegio sobre ellas (como `acceso_tablero`), sólo `execute` sobre las funciones que
--   la web necesita.
-- - `enlace_de_administracion`: como el de la puerta del equipo (0057). Sólo el hash; sirve una
--   vez; sin vencimiento por tiempo; queda anulado si se emite otro para la misma persona o se
--   cortan sus sesiones.
-- - `sesion_de_administracion`: la sesión que abre el canje. Sólo el hash del token de la cookie.
--   No vence, pero el rol se revalida en cada pedido: sin el rol `administrador` vigente en
--   `platform_role`, la sesión queda cortada (`dejo_de_ser_administrador`) en el pedido
--   siguiente y no vuelve. También se corta si la persona sale, avisa que perdió el celular o la
--   corta otro administrador.
-- - Las funciones, `security definer` con dueño `leda_owner`: emitir y cortar todas las sesiones
--   de un administrador las ejecuta sólo la consola (`leda_admin`); canjear, la sesión vigente y
--   cerrar la sesión propia (por el hash del token, nunca por un id que diga quien llama), sólo
--   la web (`leda_app`).
-- - Auditoría (constitución §12): emitir, canjear y cortar dejan su fila en `audit_log` sin
--   espacio (hechos de alcance global, como `otorgar_administrador`), con la versión del núcleo
--   y sin el token ni su hash. El espacio se vacía para escribirla, aunque quien llama tenga uno
--   fijado: el disparador `derivar_espacio_registro` lo copiaría.
--
-- No crea, altera ni borra roles. Se deshace con `db/rollbacks/0061_la_puerta_de_administracion.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0061 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0060 está aplicada (la 0057 también) y la 0061 no.
do $$ begin
  if to_regprocedure('leda.terminadas_que_ve(uuid, text, timestamptz)') is null
     or to_regprocedure('leda.auditar_acceso_web(uuid, uuid, leda.tipo_actor, text, text, uuid, jsonb)')
        is null then
    raise exception '0061 preflight failed: falta la 0060';
  end if;
  if to_regclass('leda.enlace_de_administracion') is not null then
    raise exception '0061 ya está aplicada.';
  end if;
end $$;

create table enlace_de_administracion (
  id            uuid primary key default gen_random_uuid(),
  app_user_id   uuid not null references app_user(id) on delete cascade,
  token_hash    text not null,
  emitido_en    timestamptz not null default now(),
  canjeado_en   timestamptz,
  anulado_en    timestamptz,
  constraint enlace_de_administracion_token_unico unique (token_hash),
  constraint enlace_de_administracion_hash check (token_hash ~ '^[0-9a-f]{64}$'),
  constraint enlace_de_administracion_canjeado_o_anulado
    check (canjeado_en is null or anulado_en is null)
);

-- Uno sin usar por persona: emitir otro anula el anterior.
create unique index enlace_de_administracion_sin_usar on enlace_de_administracion (app_user_id)
  where canjeado_en is null and anulado_en is null;

comment on table enlace_de_administracion is
  'ADR 0022, decisiones 10 y 12: el enlace de un solo uso a la puerta de administración, de un administrador de plataforma (sin espacio: abarca todos). Sólo el hash del token. Sirve una vez; sin vencimiento por tiempo; queda anulado si se emite otro o se cortan sus sesiones. leda_app no tiene privilegios: sólo execute sobre las funciones de la web.';

create table sesion_de_administracion (
  id               uuid primary key default gen_random_uuid(),
  app_user_id      uuid not null references app_user(id) on delete cascade,
  enlace_id        uuid not null references enlace_de_administracion(id) on delete cascade,
  token_hash       text not null,
  creada_en        timestamptz not null default now(),
  ultimo_uso_en    timestamptz not null default now(),
  cortada_en       timestamptz,
  motivo_de_corte  text,
  constraint sesion_de_administracion_token_unico unique (token_hash),
  constraint sesion_de_administracion_hash check (token_hash ~ '^[0-9a-f]{64}$'),
  constraint sesion_de_administracion_un_canje unique (enlace_id),
  constraint sesion_de_administracion_corte
    check ((cortada_en is null) = (motivo_de_corte is null)),
  constraint sesion_de_administracion_motivo check (motivo_de_corte in (
    'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_de_ser_administrador'))
);

create index sesion_de_administracion_abierta on sesion_de_administracion (app_user_id)
  where cortada_en is null;

comment on table sesion_de_administracion is
  'ADR 0022, decisiones 10 y 12: la sesión de la puerta de administración que abre el canje de un enlace. Sólo el hash del token de la cookie. Sin vencimiento, pero el rol de plataforma se revalida en cada pedido: sin él queda cortada (dejo_de_ser_administrador). Una sesión cortada no vuelve. leda_app no tiene privilegios: sólo execute sobre las funciones de la web.';

grant all privileges on enlace_de_administracion, sesion_de_administracion
  to leda_owner, leda_admin;
-- `leda_app`: nada sobre las tablas, sólo `execute` sobre las funciones de la web.
revoke all on enlace_de_administracion, sesion_de_administracion from public, leda_app;
-- `leda_owner`: lo que necesitan sus funciones; de las columnas, sólo las que cambian.
revoke all on enlace_de_administracion, sesion_de_administracion from leda_owner;
grant select, insert on enlace_de_administracion, sesion_de_administracion to leda_owner;
grant update (canjeado_en, anulado_en) on enlace_de_administracion to leda_owner;
grant update (ultimo_uso_en, cortada_en, motivo_de_corte) on sesion_de_administracion
  to leda_owner;

-- La auditoría de la puerta, sin espacio aunque quien llama tenga uno fijado. De uso interno: no
-- la ejecuta nadie más que su dueño.
create or replace function auditar_acceso_de_administracion(
    p_actor_app_user_id uuid, p_actor_kind tipo_actor, p_accion text, p_sujeto_tipo text,
    p_sujeto_id uuid, p_detalle jsonb)
returns void
language plpgsql set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
begin
  perform set_config('leda.workspace_id', '', true);
  perform auditar_acceso_web(null, p_actor_app_user_id, p_actor_kind, p_accion, p_sujeto_tipo,
                             p_sujeto_id, p_detalle);
  perform set_config('leda.workspace_id', previo, true);
end $$;

create or replace function es_administrador_de_plataforma(p_app_user_id uuid)
returns boolean
language sql stable set search_path = leda, public, pg_temp as $$
  select exists (select 1 from platform_role p
                  where p.app_user_id = p_app_user_id and p.rol = 'administrador');
$$;

create or replace function emitir_enlace_de_administracion(
    p_app_user_id uuid, p_token_hash text, p_actor_app_user_id uuid)
returns uuid
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare nuevo uuid;
begin
  -- Sólo a quien tiene hoy el rol de administrador de plataforma.
  if p_app_user_id is null or not es_administrador_de_plataforma(p_app_user_id) then
    return null;
  end if;
  update enlace_de_administracion set anulado_en = now()
   where app_user_id = p_app_user_id and canjeado_en is null and anulado_en is null;
  insert into enlace_de_administracion (app_user_id, token_hash)
       values (p_app_user_id, p_token_hash)
    returning id into nuevo;
  perform auditar_acceso_de_administracion(
    p_actor_app_user_id,
    case when p_actor_app_user_id is null then 'leda' else 'persona' end::tipo_actor,
    'emitir_enlace_de_administracion', 'app_user', p_app_user_id,
    jsonb_build_object('enlace_id', nuevo));
  return nuevo;
end $$;

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

create or replace function cerrar_sesion_de_administracion(p_token_hash text)
returns boolean
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare cortada sesion_de_administracion%rowtype;
begin
  if p_token_hash is null or p_token_hash !~ '^[0-9a-f]{64}$' then
    return false;
  end if;
  -- Sólo la sesión de ese token: la web corta la propia, nunca una por su id.
  update sesion_de_administracion s set cortada_en = now(), motivo_de_corte = 'cerro_la_sesion'
   where s.token_hash = p_token_hash and s.cortada_en is null
  returning * into cortada;
  if cortada.id is null then
    return false;
  end if;
  perform auditar_acceso_de_administracion(
    cortada.app_user_id, 'persona', 'cortar_sesion_de_administracion',
    'sesion_de_administracion', cortada.id,
    jsonb_build_object('motivo', 'cerro_la_sesion', 'app_user_id', cortada.app_user_id));
  return true;
end $$;

create or replace function cortar_sesiones_de_administrador(
    p_app_user_id uuid, p_motivo text, p_actor_app_user_id uuid)
returns integer
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare cortada record;
        cortadas integer := 0;
begin
  if p_motivo is null or p_motivo not in (
       'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_de_ser_administrador') then
    raise exception 'cortar_sesiones_de_administrador: motivo desconocido';
  end if;
  -- Con las sesiones, el enlace que estaba sin usar: si se perdió el celular, el mensaje con el
  -- enlace también.
  update enlace_de_administracion e set anulado_en = now()
   where e.app_user_id = p_app_user_id and e.canjeado_en is null and e.anulado_en is null;
  for cortada in
    update sesion_de_administracion s set cortada_en = now(), motivo_de_corte = p_motivo
     where s.app_user_id = p_app_user_id and s.cortada_en is null
    returning s.id, s.app_user_id
  loop
    perform auditar_acceso_de_administracion(
      p_actor_app_user_id,
      case when p_actor_app_user_id is null then 'leda' else 'persona' end::tipo_actor,
      'cortar_sesion_de_administracion', 'sesion_de_administracion', cortada.id,
      jsonb_build_object('motivo', p_motivo, 'app_user_id', cortada.app_user_id));
    cortadas := cortadas + 1;
  end loop;
  return cortadas;
end $$;

alter function auditar_acceso_de_administracion(uuid, tipo_actor, text, text, uuid, jsonb)
  owner to leda_owner;
alter function es_administrador_de_plataforma(uuid) owner to leda_owner;
alter function emitir_enlace_de_administracion(uuid, text, uuid) owner to leda_owner;
alter function canjear_enlace_de_administracion(text, text) owner to leda_owner;
alter function sesion_de_administracion_vigente(text) owner to leda_owner;
alter function cerrar_sesion_de_administracion(text) owner to leda_owner;
alter function cortar_sesiones_de_administrador(uuid, text, uuid) owner to leda_owner;

revoke execute on function auditar_acceso_de_administracion(uuid, tipo_actor, text, text, uuid,
                                                            jsonb) from public;
revoke execute on function es_administrador_de_plataforma(uuid) from public;
revoke execute on function emitir_enlace_de_administracion(uuid, text, uuid) from public;
revoke execute on function canjear_enlace_de_administracion(text, text) from public;
revoke execute on function sesion_de_administracion_vigente(text) from public;
revoke execute on function cerrar_sesion_de_administracion(text) from public;
revoke execute on function cortar_sesiones_de_administrador(uuid, text, uuid) from public;
-- La consola (`leda_admin`): emitir y cortar todas. La web (`leda_app`): canjear, la sesión
-- vigente y cerrar la propia.
grant execute on function emitir_enlace_de_administracion(uuid, text, uuid) to leda_admin;
grant execute on function cortar_sesiones_de_administrador(uuid, text, uuid) to leda_admin;
grant execute on function canjear_enlace_de_administracion(text, text) to leda_app;
grant execute on function sesion_de_administracion_vigente(text) to leda_app;
grant execute on function cerrar_sesion_de_administracion(text) to leda_app;

commit;
