\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0056_la_entrega_de_cada_pieza.sql. El enlace de un solo uso y la sesión de la
-- puerta del equipo de la plataforma web (ADR 0022, decisiones 4, 11 y 12; porción 1, tarea P1-1
-- de `odd/tasks/plataforma-p1.md`).
--
-- - `enlace_de_entrada`: el enlace que manda Leda para entrar a la web. Sólo el hash SHA-256 del
--   token. Sirve una sola vez: canjearlo abre una sesión en ese celular; si alguien reenvía el
--   mensaje, quien lo recibe no entra. No vence por tiempo, como el enlace personal de la página
--   de una tarea (0036; el ADR 0022 no fija un plazo): deja de servir al canjearlo, cuando se
--   emite otro para la misma persona (queda anulado; uno sin usar por persona) o cuando se cortan
--   las sesiones de la persona.
-- - `sesion_web`: la sesión que abre el canje, de una membresía (la puerta del equipo; la de
--   administración llega en la porción 2). Sólo el hash del token de la cookie. No vence: se
--   revalida en cada pedido (la membresía sigue activa) y anota su último uso; se corta sólo si la
--   corta un administrador, si la persona avisa que perdió el celular o cierra la sesión, o si
--   deja el equipo (se ve en el pedido siguiente). Una sesión cortada no vuelve: con un teléfono
--   nuevo, un enlace nuevo. Un canje, una sesión (`sesion_web_un_canje`).
-- - Las funciones, `security definer` con dueño `leda_owner`, que no saltea la RLS:
--   `emitir_enlace_de_entrada` y las dos de cortar corren en el espacio de quien llama (una
--   membresía o una sesión de otro espacio no se encuentra, igual que una que no existe);
--   `canjear_enlace_de_entrada` y `sesion_vigente` reciben el hash del token y fijan el espacio
--   que sale de él, nunca de lo que diga quien llama (decisión 11). `sesion_vigente` deja ese
--   espacio fijado para el resto del pedido; si el token no entra, devuelve el de antes. El canje
--   no lo deja fijado: sólo abre la sesión.
-- - Auditoría (constitución §12): emitir, canjear y cortar dejan su fila en `audit_log`, con el
--   espacio, la versión del pack y la del núcleo, sin el token ni su hash
--   (`auditar_acceso_web`, de uso interno: no la ejecuta nadie más que su dueño).
-- - Aislamiento: las dos tablas con `row level security` forzado y la política de siempre, más una
--   de lectura sólo para `leda_owner` por el hash del token (`resolver_por_token`), que es lo que
--   permite encontrarlo antes de saber su espacio. `leda_app` no tiene ningún privilegio sobre las
--   tablas, sólo `execute` sobre las cinco funciones.
--
-- No crea, altera ni borra roles. Se deshace con
-- `db/rollbacks/0057_el_enlace_y_la_sesion_de_la_web.sql`, antes que la vuelta atrás de la 0002:
-- sus claves compuestas apuntan a `membership_workspace_id_unique`, que esa vuelta atrás borra.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0057 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0056 está aplicada y la 0057 no.
do $$ begin
  if not exists (select 1 from information_schema.columns
                  where table_schema = 'leda' and table_name = 'evidence'
                    and column_name = 'de_la_entrega') then
    raise exception '0057 preflight failed: falta la 0056';
  end if;
  if to_regclass('leda.enlace_de_entrada') is not null then
    raise exception '0057 ya está aplicada.';
  end if;
end $$;

create table enlace_de_entrada (
  id             uuid primary key default gen_random_uuid(),
  workspace_id   uuid not null references workspace(id) on delete cascade,
  membership_id  uuid not null,
  token_hash     text not null,
  emitido_en     timestamptz not null default now(),
  canjeado_en    timestamptz,
  anulado_en     timestamptz,
  constraint enlace_de_entrada_workspace_id_unique unique (workspace_id, id),
  constraint enlace_de_entrada_token_unico unique (token_hash),
  constraint enlace_de_entrada_hash check (token_hash ~ '^[0-9a-f]{64}$'),
  constraint enlace_de_entrada_canjeado_o_anulado
    check (canjeado_en is null or anulado_en is null),
  constraint enlace_de_entrada_membership
    foreign key (workspace_id, membership_id) references membership(workspace_id, id)
    on delete cascade
);

-- Uno sin usar por persona: emitir otro anula el anterior.
create unique index enlace_de_entrada_sin_usar on enlace_de_entrada (membership_id)
  where canjeado_en is null and anulado_en is null;

comment on table enlace_de_entrada is
  'ADR 0022, decisiones 4 y 12: el enlace de un solo uso para entrar a la web. Sólo el hash del token. Sirve una vez (canjeado_en); sin vencimiento por tiempo; queda anulado si se emite otro para la misma persona o se cortan sus sesiones. leda_app no tiene privilegios: sólo execute sobre sus funciones.';

create table sesion_web (
  id               uuid primary key default gen_random_uuid(),
  workspace_id     uuid not null references workspace(id) on delete cascade,
  membership_id    uuid not null,
  enlace_id        uuid not null,
  token_hash       text not null,
  creada_en        timestamptz not null default now(),
  ultimo_uso_en    timestamptz not null default now(),
  cortada_en       timestamptz,
  motivo_de_corte  text,
  constraint sesion_web_token_unico unique (token_hash),
  constraint sesion_web_hash check (token_hash ~ '^[0-9a-f]{64}$'),
  constraint sesion_web_un_canje unique (enlace_id),
  constraint sesion_web_corte check ((cortada_en is null) = (motivo_de_corte is null)),
  constraint sesion_web_motivo check (motivo_de_corte in (
    'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_el_equipo')),
  constraint sesion_web_membership
    foreign key (workspace_id, membership_id) references membership(workspace_id, id)
    on delete cascade,
  constraint sesion_web_enlace
    foreign key (workspace_id, enlace_id) references enlace_de_entrada(workspace_id, id)
    on delete cascade
);

create index sesion_web_abierta on sesion_web (membership_id) where cortada_en is null;

comment on table sesion_web is
  'ADR 0022, decisiones 4 y 12: la sesión de la puerta del equipo que abre el canje de un enlace. Sólo el hash del token de la cookie. Sin vencimiento: se revalida en cada pedido (membresía activa) y anota su último uso; se corta (cortada_en, motivo_de_corte) y no vuelve. leda_app no tiene privilegios: sólo execute sobre sus funciones.';

grant all privileges on enlace_de_entrada, sesion_web to leda_owner, leda_admin;

alter table enlace_de_entrada enable row level security;
alter table enlace_de_entrada force row level security;
create policy aislamiento_espacio on enlace_de_entrada
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
-- Encontrar un enlace antes de saber su espacio: sólo `leda_owner` (el canje), sólo para leer y
-- sólo la fila de ese hash.
create policy resolver_por_token on enlace_de_entrada for select to leda_owner
  using (token_hash = nullif(current_setting('leda.token_de_entrada', true), ''));

alter table sesion_web enable row level security;
alter table sesion_web force row level security;
create policy aislamiento_espacio on sesion_web
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
-- Lo mismo con una sesión: sólo `sesion_vigente`.
create policy resolver_por_token on sesion_web for select to leda_owner
  using (token_hash = nullif(current_setting('leda.token_de_sesion', true), ''));

-- `leda_app`: nada sobre los enlaces ni las sesiones, sólo `execute` sobre sus funciones.
revoke all on enlace_de_entrada, sesion_web from public, leda_app;
-- `leda_owner`: lo que necesitan sus funciones; de las columnas, sólo las que cambian.
revoke all on enlace_de_entrada, sesion_web from leda_owner;
grant select, insert on enlace_de_entrada, sesion_web to leda_owner;
grant update (canjeado_en, anulado_en) on enlace_de_entrada to leda_owner;
grant update (ultimo_uso_en, cortada_en, motivo_de_corte) on sesion_web to leda_owner;

create or replace function auditar_acceso_web(
    p_workspace_id uuid, p_actor_app_user_id uuid, p_actor_kind tipo_actor, p_accion text,
    p_sujeto_tipo text, p_sujeto_id uuid, p_detalle jsonb)
returns void
language plpgsql set search_path = leda, public, pg_temp as $$
begin
  insert into audit_log (workspace_id, actor_app_user_id, actor_kind, accion, sujeto_tipo,
                         sujeto_id, detalle, pack_hash, nucleo_hash)
  values (p_workspace_id, p_actor_app_user_id, p_actor_kind, p_accion, p_sujeto_tipo,
          p_sujeto_id, p_detalle,
          (select v.pack_hash from workspace_version v
            where v.workspace_id = p_workspace_id order by v.version desc limit 1),
          nullif(current_setting('leda.nucleo_hash', true), ''));
end $$;

create or replace function emitir_enlace_de_entrada(
    p_membership_id uuid, p_token_hash text, p_actor_app_user_id uuid)
returns uuid
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare espacio uuid;
        nuevo uuid;
begin
  -- El espacio sale de la membresía, que la RLS acota al espacio de quien llama: una membresía
  -- de otro espacio no se encuentra, igual que una que no existe o que dejó el equipo.
  select m.workspace_id into espacio from membership m
   where m.id = p_membership_id and m.activo;
  if espacio is null then
    return null;
  end if;
  update enlace_de_entrada set anulado_en = now()
   where membership_id = p_membership_id and canjeado_en is null and anulado_en is null;
  insert into enlace_de_entrada (workspace_id, membership_id, token_hash)
       values (espacio, p_membership_id, p_token_hash)
    returning id into nuevo;
  perform auditar_acceso_web(
    espacio, p_actor_app_user_id,
    case when p_actor_app_user_id is null then 'leda' else 'persona' end::tipo_actor,
    'emitir_enlace_de_entrada', 'membership', p_membership_id,
    jsonb_build_object('enlace_id', nuevo));
  return nuevo;
end $$;

create or replace function canjear_enlace_de_entrada(
    p_token_hash text, p_sesion_token_hash text)
returns uuid
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        enlace enlace_de_entrada%rowtype;
        persona uuid;
        nueva uuid;
begin
  if p_token_hash is null or p_token_hash !~ '^[0-9a-f]{64}$'
     or p_sesion_token_hash is null or p_sesion_token_hash !~ '^[0-9a-f]{64}$' then
    return null;
  end if;
  perform set_config('leda.token_de_entrada', p_token_hash, true);
  select * into enlace from enlace_de_entrada e where e.token_hash = p_token_hash;
  perform set_config('leda.token_de_entrada', '', true);
  if enlace.id is null then
    return null;
  end if;
  perform set_config('leda.workspace_id', enlace.workspace_id::text, true);
  select m.app_user_id into persona from membership m
   where m.id = enlace.membership_id and m.activo;
  if persona is not null then
    -- Una sola vez: si llegan dos canjes a la vez, el segundo espera el candado de la fila y ya
    -- no la encuentra sin canjear.
    update enlace_de_entrada set canjeado_en = now()
     where id = enlace.id and canjeado_en is null and anulado_en is null;
    if found then
      insert into sesion_web (workspace_id, membership_id, enlace_id, token_hash)
           values (enlace.workspace_id, enlace.membership_id, enlace.id, p_sesion_token_hash)
        returning id into nueva;
      perform auditar_acceso_web(
        enlace.workspace_id, persona, 'persona', 'canjear_enlace_de_entrada', 'sesion_web',
        nueva, jsonb_build_object('enlace_id', enlace.id,
                                  'membership_id', enlace.membership_id));
    end if;
  end if;
  perform set_config('leda.workspace_id', previo, true);
  return nueva;
end $$;

create or replace function sesion_vigente(p_token_hash text)
returns table (sesion_id uuid, workspace_id uuid, membership_id uuid)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        sesion sesion_web%rowtype;
begin
  if p_token_hash is null or p_token_hash !~ '^[0-9a-f]{64}$' then
    return;
  end if;
  perform set_config('leda.token_de_sesion', p_token_hash, true);
  select * into sesion from sesion_web s
   where s.token_hash = p_token_hash and s.cortada_en is null;
  perform set_config('leda.token_de_sesion', '', true);
  if sesion.id is null then
    return;
  end if;
  perform set_config('leda.workspace_id', sesion.workspace_id::text, true);
  -- Quien dejó el equipo ya no entra, y su sesión queda cortada: si vuelve, pide un enlace nuevo.
  if not exists (select 1 from membership m
                  where m.id = sesion.membership_id and m.activo) then
    update sesion_web s set cortada_en = now(), motivo_de_corte = 'dejo_el_equipo'
     where s.id = sesion.id and s.cortada_en is null;
    if found then
      perform auditar_acceso_web(
        sesion.workspace_id, null, 'sistema', 'cortar_sesion_web', 'sesion_web', sesion.id,
        jsonb_build_object('motivo', 'dejo_el_equipo', 'membership_id', sesion.membership_id));
    end if;
    perform set_config('leda.workspace_id', previo, true);
    return;
  end if;
  -- Cortada mientras tanto: no entra.
  update sesion_web s set ultimo_uso_en = now()
   where s.id = sesion.id and s.cortada_en is null;
  if not found then
    perform set_config('leda.workspace_id', previo, true);
    return;
  end if;
  return query select sesion.id, sesion.workspace_id, sesion.membership_id;
end $$;

create or replace function cortar_sesion(
    p_sesion_id uuid, p_motivo text, p_actor_app_user_id uuid)
returns boolean
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare cortada sesion_web%rowtype;
begin
  if p_motivo is null or p_motivo not in (
       'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_el_equipo') then
    raise exception 'cortar_sesion: motivo desconocido';
  end if;
  -- La RLS acota la búsqueda al espacio de quien llama: una sesión de otro espacio no se
  -- encuentra, igual que una que no existe o que ya estaba cortada.
  update sesion_web s set cortada_en = now(), motivo_de_corte = p_motivo
   where s.id = p_sesion_id and s.cortada_en is null
  returning * into cortada;
  if cortada.id is null then
    return false;
  end if;
  perform auditar_acceso_web(
    cortada.workspace_id, p_actor_app_user_id,
    case when p_actor_app_user_id is null then 'leda' else 'persona' end::tipo_actor,
    'cortar_sesion_web', 'sesion_web', cortada.id,
    jsonb_build_object('motivo', p_motivo, 'membership_id', cortada.membership_id));
  return true;
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

alter function auditar_acceso_web(uuid, uuid, tipo_actor, text, text, uuid, jsonb)
  owner to leda_owner;
alter function emitir_enlace_de_entrada(uuid, text, uuid) owner to leda_owner;
alter function canjear_enlace_de_entrada(text, text) owner to leda_owner;
alter function sesion_vigente(text) owner to leda_owner;
alter function cortar_sesion(uuid, text, uuid) owner to leda_owner;
alter function cortar_sesiones_de_membresia(uuid, text, uuid) owner to leda_owner;

revoke execute on function auditar_acceso_web(uuid, uuid, tipo_actor, text, text, uuid, jsonb)
  from public;
revoke execute on function emitir_enlace_de_entrada(uuid, text, uuid) from public;
revoke execute on function canjear_enlace_de_entrada(text, text) from public;
revoke execute on function sesion_vigente(text) from public;
revoke execute on function cortar_sesion(uuid, text, uuid) from public;
revoke execute on function cortar_sesiones_de_membresia(uuid, text, uuid) from public;
grant execute on function emitir_enlace_de_entrada(uuid, text, uuid) to leda_app;
grant execute on function canjear_enlace_de_entrada(text, text) to leda_app;
grant execute on function sesion_vigente(text) to leda_app;
grant execute on function cortar_sesion(uuid, text, uuid) to leda_app;
grant execute on function cortar_sesiones_de_membresia(uuid, text, uuid) to leda_app;

commit;
