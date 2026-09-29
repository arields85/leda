\encoding UTF8
\set ON_ERROR_STOP on

-- G2b (rama auxiliar/alta-y-google) -- credencial de Google por espacio.
-- Decisión del usuario, 2026-09-28: una cuenta de Google por espacio, la de
-- Prisma; la autoriza el administrador con un comando local. Con la clave
-- `google.habilitado` apagada en `workspace_setting` (el valor por defecto),
-- nada de lo de acá abajo se usa.
--
-- Tres tablas, siguiendo los patrones que ya rigen el resto del esquema:
--
--   - `credencial_google`: el payload CIFRADO de la credencial (un token
--     Fernet armado en Python, `google/cifrado.py`), la cuenta autorizada y
--     los permisos concedidos. La base nunca ve el refresh token ni el
--     access token en claro y nunca parsea el payload. Mismo patrón que
--     `acceso_tablero` / `alta_correo_verificacion`: ninguna concesión a
--     `prisma_app`, sólo `execute` sobre funciones `security definer` de
--     `prisma_owner`.
--   - `credencial_google_evento` / `credencial_google_estado`: la misma
--     pareja evento-append-only + proyección-por-disparador que
--     `alta_correo_evento` / `alta_correo_estado` (regla 4 de la frontera).
--     El estado (`vigente`, `requiere_reautorizacion`, `revocada`) es la
--     proyección; "sin autorizar" es no tener ninguna. Nunca un `update`
--     directo. El motivo de un evento es un código corto y saneado, nunca un
--     token ni el cuerpo crudo de un error del proveedor.
--
-- Qué ejecuta cada rol (y por qué):
--
--   - `prisma_app` (el runtime): leer el payload cifrado para usarlo (G2d),
--     marcar "requiere reautorización" cuando Google rechaza el refresh
--     token, y leer el estado. Las tres funciones NO reciben el espacio: lo
--     toman de la sesión (`prisma.workspace_id`, que fija `espacio()`), así
--     que el aislamiento no depende de que quien llama recuerde un filtro.
--   - `prisma_admin` (el camino de operación): guardar/reemplazar la
--     credencial (`google autorizar`, G2c), revocarla, y el re-cifrado de la
--     rotación de claves (`google recifrar`). Estas funciones sí reciben el
--     espacio -- la conexión administrativa no declara ninguno -- y NO las
--     ejecuta `prisma_app`: un runtime comprometido no puede plantar una
--     credencial ni revocar la del espacio. Mismo criterio que
--     `avisar_aviso_administrativo_admin` en 0100.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0101 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'prisma_owner') then
    raise exception '0101 requires 0004_function_ownership.sql';
  end if;
  if to_regclass('prisma.credencial_google') is not null then
    raise exception '0101 ya está aplicada.';
  end if;
end $$;

-- =========================================================================
-- Credencial cifrada
-- =========================================================================

create table credencial_google (
  workspace_id    uuid primary key references workspace(id) on delete cascade,
  token_cifrado   text not null check (token_cifrado <> ''),
  cuenta_email    text not null check (cuenta_email <> ''
                                       and cuenta_email = lower(btrim(cuenta_email))),
  scopes          text[] not null check (cardinality(scopes) > 0),
  autorizado_en   timestamptz not null default now(),
  actualizado_en  timestamptz not null default now()
);

revoke all on credencial_google from public;

comment on table credencial_google is
  'Una credencial de Google por espacio, CIFRADA en la aplicación (Fernet): token_cifrado es opaco para la base, que nunca ve ni parsea el texto plano. Sin ningún privilegio para prisma_app: la única puerta son leer_credencial_google(), guardar_credencial_google(), reemplazar_token_google() y credenciales_google_cifradas(). La revocación borra la fila.';

-- =========================================================================
-- Eventos append-only y su proyección
-- =========================================================================

create table credencial_google_estado (
  workspace_id    uuid primary key references workspace(id) on delete cascade,
  estado          text not null check (estado in (
                     'vigente', 'requiere_reautorizacion', 'revocada')),
  motivo          text,
  actualizado_en  timestamptz not null default now()
);

revoke all on credencial_google_estado from public;

comment on table credencial_google_estado is
  'Proyección del estado de la credencial de Google de un espacio (sin fila = sin autorizar). Nunca se escribe con update directo: la escribe aplicar_evento_credencial_google(), disparada por credencial_google_evento. bloquear_actualizacion_directa_credencial_google() lo hace cumplir.';

create table credencial_google_evento (
  id            uuid primary key default gen_random_uuid(),
  workspace_id  uuid not null references workspace(id) on delete cascade,
  tipo          text not null check (tipo in (
                   'autorizada', 'reautorizacion_requerida', 'revocada')),
  motivo        text check (motivo ~ '^[a-z0-9_]{1,64}$'),
  actor_kind    tipo_actor not null,
  at            timestamptz not null default now(),
  check (tipo = 'autorizada' or motivo is not null)
);

revoke all on credencial_google_evento from public;

create index credencial_google_evento_ws on credencial_google_evento (workspace_id, at desc);

comment on table credencial_google_evento is
  'Registro append-only. Es la verdad; credencial_google_estado es su proyección. motivo es un código corto y saneado (minúsculas, dígitos y guion bajo), nunca un token ni el cuerpo crudo de un error del proveedor.';

-- --- La transición se valida ANTES de insertar ------------------------------
--
-- Security definer por el mismo motivo que preparar_evento_alta_correo(): el
-- `for update` sobre la proyección exige `update`, que `prisma_app` no tiene.
-- El dueño (`prisma_owner`) no saltea la RLS, así que se fija el espacio del
-- propio evento sólo para esa lectura (la conexión administrativa no declara
-- ninguno) y se restaura enseguida.
--
-- Autorizar es válido desde cualquier estado (primera vez, reautorización,
-- volver a autorizar tras revocar). Pedir reautorización sólo desde
-- `vigente`; revocar sólo si hay algo que revocar.
create or replace function preparar_evento_credencial_google() returns trigger
security definer set search_path = prisma, public, pg_temp as $$
declare
  espacio_anterior text := current_setting('prisma.workspace_id', true);
  actual credencial_google_estado%rowtype;
  encontrada boolean;
begin
  perform set_config('prisma.workspace_id', new.workspace_id::text, true);
  select * into actual from credencial_google_estado
   where workspace_id = new.workspace_id
   for update;
  encontrada := found;
  perform set_config('prisma.workspace_id', coalesce(espacio_anterior, ''), true);

  if new.tipo = 'reautorizacion_requerida' then
    if not encontrada or actual.estado <> 'vigente' then
      raise exception
        'credencial_google_evento: sólo una credencial vigente puede pasar a requerir reautorización';
    end if;
  elsif new.tipo = 'revocada' then
    if not encontrada or actual.estado not in ('vigente', 'requiere_reautorizacion') then
      raise exception
        'credencial_google_evento: no hay una credencial que revocar';
    end if;
  end if;

  return new;
end $$ language plpgsql;

create trigger trg_preparar_evento_credencial_google
  before insert on credencial_google_evento
  for each row execute function preparar_evento_credencial_google();

-- --- La proyección la escribe únicamente el disparador ----------------------
--
-- GUC propia (`prisma.aplicando_evento_credencial_google`), separada de las
-- de tareas y del alta con correo. La revocación borra el payload cifrado en
-- el mismo disparador: el invariante "revocada => sin credencial guardada"
-- vale por cualquier camino que inserte el evento, no sólo por la función.
create or replace function aplicar_evento_credencial_google() returns trigger
security definer set search_path = prisma, public, pg_temp as $$
declare espacio_anterior text := current_setting('prisma.workspace_id', true);
begin
  perform set_config('prisma.workspace_id', new.workspace_id::text, true);
  perform set_config('prisma.aplicando_evento_credencial_google', '1', true);

  if new.tipo = 'autorizada' then
    insert into credencial_google_estado (workspace_id, estado, motivo, actualizado_en)
      values (new.workspace_id, 'vigente', null, new.at)
    on conflict (workspace_id) do update
      set estado = 'vigente', motivo = null, actualizado_en = new.at;
  elsif new.tipo = 'reautorizacion_requerida' then
    update credencial_google_estado
       set estado = 'requiere_reautorizacion', motivo = new.motivo,
           actualizado_en = new.at
     where workspace_id = new.workspace_id;
  elsif new.tipo = 'revocada' then
    update credencial_google_estado
       set estado = 'revocada', motivo = new.motivo, actualizado_en = new.at
     where workspace_id = new.workspace_id;
    delete from credencial_google where workspace_id = new.workspace_id;
  end if;

  perform set_config('prisma.aplicando_evento_credencial_google', '0', true);
  perform set_config('prisma.workspace_id', coalesce(espacio_anterior, ''), true);
  return new;
end $$ language plpgsql;

create trigger trg_aplicar_evento_credencial_google
  after insert on credencial_google_evento
  for each row execute function aplicar_evento_credencial_google();

create or replace function bloquear_actualizacion_directa_credencial_google()
returns trigger as $$
begin
  if coalesce(current_setting('prisma.aplicando_evento_credencial_google', true), '0') <> '1' then
    raise exception
      'El estado de la credencial de Google no se escribe directamente. Insertá una fila en credencial_google_evento.';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_bloquear_actualizacion_directa_credencial_google
  before update on credencial_google_estado
  for each row execute function bloquear_actualizacion_directa_credencial_google();

-- =========================================================================
-- Funciones del runtime (prisma_app): el espacio sale de la sesión
-- =========================================================================
--
-- Ninguna recibe el espacio ni confía en nada aportado por quien llama: sin
-- `prisma.workspace_id` declarado fallan (nunca devuelven "sin autorizar",
-- porque no poder consultar no equivale a que no exista). La RLS ya acota
-- cada consulta al espacio de la sesión; el filtro explícito es defensa en
-- profundidad.

create or replace function leer_credencial_google()
returns table (token_cifrado text, cuenta_email text, scopes text[], estado text)
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare espacio uuid := nullif(current_setting('prisma.workspace_id', true), '')::uuid;
begin
  if espacio is null then
    raise exception 'leer_credencial_google: no hay un espacio declarado en la sesión';
  end if;
  return query
    select c.token_cifrado, c.cuenta_email, c.scopes, e.estado
      from credencial_google c
      join credencial_google_estado e on e.workspace_id = c.workspace_id
     where c.workspace_id = espacio;
end $$;

create or replace function estado_credencial_google()
returns text
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare
  espacio uuid := nullif(current_setting('prisma.workspace_id', true), '')::uuid;
  actual text;
begin
  if espacio is null then
    raise exception 'estado_credencial_google: no hay un espacio declarado en la sesión';
  end if;
  select e.estado into actual from credencial_google_estado e
   where e.workspace_id = espacio;
  return coalesce(actual, 'sin_autorizar');
end $$;

-- Google rechazó el refresh token (`invalid_grant`): la credencial guardada
-- ya no sirve y hace falta volver a autorizar. Devuelve `true` sólo si
-- efectivamente pasó de `vigente` a `requiere_reautorizacion`; si ya estaba
-- así (o no hay credencial) no repite el evento. El candado consultivo
-- serializa dos avisos simultáneos del mismo espacio.
create or replace function marcar_reautorizacion_google(p_motivo text)
returns boolean
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare
  espacio uuid := nullif(current_setting('prisma.workspace_id', true), '')::uuid;
  actual text;
begin
  if espacio is null then
    raise exception 'marcar_reautorizacion_google: no hay un espacio declarado en la sesión';
  end if;
  perform pg_advisory_xact_lock(
    hashtextextended('credencial_google:' || espacio::text, 0));

  select e.estado into actual from credencial_google_estado e
   where e.workspace_id = espacio;
  if actual is distinct from 'vigente' then
    return false;
  end if;

  insert into credencial_google_evento (workspace_id, tipo, motivo, actor_kind)
    values (espacio, 'reautorizacion_requerida', p_motivo, 'sistema');
  return true;
end $$;

-- =========================================================================
-- Funciones de operación (prisma_admin): el espacio se recibe
-- =========================================================================
--
-- La conexión administrativa no declara ningún espacio, y `prisma_owner` no
-- saltea la RLS: cada función fija el espacio recibido sólo mientras toca las
-- tablas y lo restaura al salir, igual que completar_verificacion_correo().

-- Guarda (o reemplaza) la credencial cifrada y emite el evento de
-- autorización: el estado pasa a `vigente` desde cualquier estado anterior.
create or replace function guardar_credencial_google(
    p_workspace_id uuid, p_token_cifrado text, p_cuenta_email text,
    p_scopes text[])
returns void
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare espacio_anterior text := current_setting('prisma.workspace_id', true);
begin
  if p_workspace_id is null
     or not exists (select 1 from workspace w where w.id = p_workspace_id) then
    raise exception 'guardar_credencial_google: no existe el espacio %', p_workspace_id;
  end if;
  perform pg_advisory_xact_lock(
    hashtextextended('credencial_google:' || p_workspace_id::text, 0));
  perform set_config('prisma.workspace_id', p_workspace_id::text, true);

  insert into credencial_google
      (workspace_id, token_cifrado, cuenta_email, scopes)
    values (p_workspace_id, p_token_cifrado, p_cuenta_email, p_scopes)
  on conflict (workspace_id) do update
    set token_cifrado = excluded.token_cifrado,
        cuenta_email = excluded.cuenta_email,
        scopes = excluded.scopes,
        autorizado_en = now(),
        actualizado_en = now();

  insert into credencial_google_evento (workspace_id, tipo, actor_kind)
    values (p_workspace_id, 'autorizada', 'persona');

  perform set_config('prisma.workspace_id', coalesce(espacio_anterior, ''), true);
end $$;

-- Revoca: el evento borra el payload cifrado (lo hace el disparador).
-- Devuelve `false`, sin emitir nada, si no había nada que revocar.
create or replace function revocar_credencial_google(
    p_workspace_id uuid, p_motivo text)
returns boolean
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare
  espacio_anterior text := current_setting('prisma.workspace_id', true);
  actual text;
begin
  perform pg_advisory_xact_lock(
    hashtextextended('credencial_google:' || p_workspace_id::text, 0));
  perform set_config('prisma.workspace_id', p_workspace_id::text, true);

  select e.estado into actual from credencial_google_estado e
   where e.workspace_id = p_workspace_id;
  if actual is null or actual = 'revocada' then
    perform set_config('prisma.workspace_id', coalesce(espacio_anterior, ''), true);
    return false;
  end if;

  insert into credencial_google_evento (workspace_id, tipo, motivo, actor_kind)
    values (p_workspace_id, 'revocada', p_motivo, 'persona');

  perform set_config('prisma.workspace_id', coalesce(espacio_anterior, ''), true);
  return true;
end $$;

-- --- Re-cifrado (`python -m prisma google recifrar`) ---------------------------
--
-- Lista los payloads cifrados de TODOS los espacios para que la rotación de
-- claves los vuelva a cifrar en Python. Sólo `prisma_admin`: recorre los
-- espacios fijando cada uno por vez, porque `prisma_owner` no saltea la RLS.
create or replace function credenciales_google_cifradas()
returns table (workspace_id uuid, slug text, token_cifrado text)
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare
  espacio_anterior text := current_setting('prisma.workspace_id', true);
  w record;
  cifrado text;
begin
  for w in select ws.id, ws.slug from workspace ws order by ws.slug loop
    perform set_config('prisma.workspace_id', w.id::text, true);
    select c.token_cifrado into cifrado from credencial_google c
     where c.workspace_id = w.id;
    if found then
      workspace_id := w.id;
      slug := w.slug;
      token_cifrado := cifrado;
      return next;
    end if;
  end loop;
  perform set_config('prisma.workspace_id', coalesce(espacio_anterior, ''), true);
end $$;

-- Reemplazo por comparación: sólo escribe si el payload sigue siendo el que
-- se leyó. El re-cifrado lee y escribe en pasos distintos; si mientras tanto
-- se volvió a autorizar (o se revocó), no pisa lo nuevo. No es un cambio de
-- estado, así que no emite eventos.
create or replace function reemplazar_token_google(
    p_workspace_id uuid, p_token_viejo text, p_token_nuevo text)
returns boolean
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare
  espacio_anterior text := current_setting('prisma.workspace_id', true);
  reemplazado boolean;
begin
  perform pg_advisory_xact_lock(
    hashtextextended('credencial_google:' || p_workspace_id::text, 0));
  perform set_config('prisma.workspace_id', p_workspace_id::text, true);

  update credencial_google c
     set token_cifrado = p_token_nuevo, actualizado_en = now()
   where c.workspace_id = p_workspace_id and c.token_cifrado = p_token_viejo;
  reemplazado := found;

  perform set_config('prisma.workspace_id', coalesce(espacio_anterior, ''), true);
  return reemplazado;
end $$;

-- =========================================================================
-- Aislamiento entre espacios
-- =========================================================================

alter table credencial_google enable row level security;
alter table credencial_google force row level security;
create policy aislamiento_espacio on credencial_google
  using (workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid);

alter table credencial_google_estado enable row level security;
alter table credencial_google_estado force row level security;
create policy aislamiento_espacio on credencial_google_estado
  using (workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid);

alter table credencial_google_evento enable row level security;
alter table credencial_google_evento force row level security;
create policy aislamiento_espacio on credencial_google_evento
  using (workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid);

-- Ninguna concesión a prisma_app sobre ninguna de las tres tablas.

-- --- Propiedad y privilegios ---------------------------------------------------

grant select, insert, update, delete on credencial_google to prisma_owner;
grant select, insert, update on credencial_google_estado to prisma_owner;
grant select, insert on credencial_google_evento to prisma_owner;
-- prisma_admin no escribe estas tablas directamente (sólo por las funciones
-- de operación, que validan y emiten el evento): lee, para auditar, y
-- `truncate`, que necesita el borrado en cascada de un espacio de pruebas.
grant select, truncate on credencial_google, credencial_google_estado,
                          credencial_google_evento to prisma_admin;

alter function preparar_evento_credencial_google() owner to prisma_owner;
alter function aplicar_evento_credencial_google() owner to prisma_owner;
alter function leer_credencial_google() owner to prisma_owner;
alter function estado_credencial_google() owner to prisma_owner;
alter function marcar_reautorizacion_google(text) owner to prisma_owner;
alter function guardar_credencial_google(uuid, text, text, text[]) owner to prisma_owner;
alter function revocar_credencial_google(uuid, text) owner to prisma_owner;
alter function credenciales_google_cifradas() owner to prisma_owner;
alter function reemplazar_token_google(uuid, text, text) owner to prisma_owner;

revoke execute on function leer_credencial_google() from public;
revoke execute on function estado_credencial_google() from public;
revoke execute on function marcar_reautorizacion_google(text) from public;
revoke execute on function guardar_credencial_google(uuid, text, text, text[]) from public;
revoke execute on function revocar_credencial_google(uuid, text) from public;
revoke execute on function credenciales_google_cifradas() from public;
revoke execute on function reemplazar_token_google(uuid, text, text) from public;

-- Runtime: usar la credencial, avisar que ya no sirve, saber en qué estado está.
grant execute on function leer_credencial_google() to prisma_app;
grant execute on function estado_credencial_google() to prisma_app;
grant execute on function marcar_reautorizacion_google(text) to prisma_app;
-- Operación: autorizar, revocar y rotar claves. Nunca prisma_app.
grant execute on function guardar_credencial_google(uuid, text, text, text[]) to prisma_admin;
grant execute on function revocar_credencial_google(uuid, text) to prisma_admin;
grant execute on function credenciales_google_cifradas() to prisma_admin;
grant execute on function reemplazar_token_google(uuid, text, text) to prisma_admin;

commit;
