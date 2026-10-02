\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0005_auxiliary_record_isolation.sql. Adds the credential that
-- lets a person open the dashboard from a browser, where none of the identity
-- Telegram provides exists.
--
-- The link is a credential: only its hash is stored, it expires, and the
-- workspace travels inside it rather than in the URL. A URL carrying the
-- workspace would repeat the mistake the boundary already rejects -- trusting
-- the caller for the space it operates on.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0006 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'leda_owner') then
    raise exception '0006 requires 0004_function_ownership.sql';
  end if;
end $$;

-- --- La tabla -------------------------------------------------------------

create table acceso_tablero (
  id             uuid primary key default gen_random_uuid(),
  workspace_id   uuid not null references workspace(id) on delete cascade,
  membership_id  uuid not null references membership(id) on delete cascade,
  token_hash     text not null unique,
  emitido_en     timestamptz not null default now(),
  vence_en       timestamptz not null
);

create index acceso_tablero_vencimiento on acceso_tablero (vence_en);

-- Sin política de aislamiento, a propósito y a diferencia del resto del
-- esquema: la búsqueda del token ocurre ANTES de saber a qué espacio
-- pertenece, así que una política por espacio no tendría contra qué comparar.
-- Lo que protege esta tabla es que nadie la consulta: `leda_app` no recibe
-- ningún privilegio sobre ella, sólo `execute` sobre las dos funciones de
-- abajo, que son la única puerta.
revoke all on acceso_tablero from public;

-- --- Emisión --------------------------------------------------------------

-- El espacio no se recibe: sale de la membresía. Como `leda_owner` no
-- saltea la RLS, esa búsqueda queda filtrada al espacio de la sesión, así que
-- una membresía de otro cliente no se encuentra y falla idéntico a una
-- inexistente. Decir "no tenés permiso" confirmaría que existe.
create or replace function emitir_acceso_tablero(
    p_membership_id uuid, p_token_hash text, p_vence_en timestamptz)
returns uuid
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare espacio uuid;
        nuevo uuid;
begin
  select m.workspace_id into espacio
    from membership m where m.id = p_membership_id and m.activo;
  if espacio is null then
    raise exception 'acceso_tablero: no existe la membresía %', p_membership_id;
  end if;

  insert into acceso_tablero (workspace_id, membership_id, token_hash, vence_en)
       values (espacio, p_membership_id, p_token_hash, p_vence_en)
    returning id into nuevo;
  return nuevo;
end $$;

-- --- Resolución -----------------------------------------------------------

-- Devuelve filas sólo si el token existe, no venció, y la membresía sigue
-- activa. Tener un token vigente no alcanza: la autoridad se revalida en cada
-- pedido, no sólo al emitir.
--
-- El `set_config` es seguro porque el espacio sale del token, resuelto del
-- lado del servidor, y no de nada que haya aportado quien llama. Recién
-- después de fijarlo se comprueba la membresía, de modo que esa comprobación
-- ya corre acotada al espacio correcto.
create or replace function resolver_acceso_tablero(p_token_hash text)
returns table (workspace_id uuid, membership_id uuid)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare acceso acceso_tablero%rowtype;
begin
  select * into acceso from acceso_tablero a
   where a.token_hash = p_token_hash and a.vence_en > now();
  if not found then
    return;
  end if;

  perform set_config('leda.workspace_id', acceso.workspace_id::text, true);

  if not exists (select 1 from membership m
                  where m.id = acceso.membership_id and m.activo) then
    return;
  end if;

  return query select acceso.workspace_id, acceso.membership_id;
end $$;

-- --- Propiedad y privilegios ----------------------------------------------

-- Las concesiones generales del esquema alcanzaron a las tablas que existían
-- cuando se ejecutaron; esta es nueva y necesita las suyas explícitas. Sin la
-- de `leda_owner` fallan las funciones, y sin la de `leda_admin` una base
-- migrada diverge de una instalación limpia, donde el `grant all on all
-- tables` del final del esquema sí la alcanza.
grant select, insert on acceso_tablero to leda_owner;
grant all on acceso_tablero to leda_admin;

alter function emitir_acceso_tablero(uuid, text, timestamptz)
  owner to leda_owner;
alter function resolver_acceso_tablero(text)
  owner to leda_owner;

revoke execute on function emitir_acceso_tablero(uuid, text, timestamptz)
  from public;
revoke execute on function resolver_acceso_tablero(text) from public;
grant execute on function emitir_acceso_tablero(uuid, text, timestamptz)
  to leda_app;
grant execute on function resolver_acceso_tablero(text) to leda_app;

commit;
