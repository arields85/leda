\encoding UTF8
\set ON_ERROR_STOP on

-- G1a (rama auxiliar/alta-y-google) -- esquema del alta con correo
-- verificado. Se suma al enlace de activación existente (`activation_token`),
-- no lo reemplaza: con la clave `correo_verificacion.habilitado` apagada en
-- `workspace_setting`, nada de lo de acá abajo se usa y `onboarding.activar`
-- sigue igual.
--
-- Tres conceptos, tres tablas, siguiendo los patrones que ya rigen el resto
-- del esquema:
--
--   - `alta_correo_evento` / `alta_correo_estado`: la misma pareja
--     evento-append-only + proyección-por-disparador que `task_state_event` /
--     `task` (regla 4 de la frontera). Los cinco estados de
--     `01-INCORPORACION-E-IDENTIDAD.md` §4 son la proyección; nunca un
--     `update` directo. A diferencia de `actualizar_estado` sobre `task`
--     (que la frontera documenta como incompleto: acepta cualquier destino
--     del enum sin validar la transición), acá el grafo de transiciones se
--     valida en la base, porque el pack lo exige explícitamente.
--   - `alta_correo_verificacion`: mismo patrón que `acceso_tablero` --
--     ninguna concesión a `prisma_app`, sólo `execute` sobre tres funciones
--     `security definer`. Guarda el hash SHA-256, nunca el token en claro.
--   - `alta_correo_contacto`: un correo verificado por integrante, con alta
--     sólo por función.
--   - `aviso_administrativo`: los avisos "🛠️ Administración" persistentes
--     (leído ≠ resuelto) que entregará G1d por el bot de administración.
--
-- Decisión del usuario para G1 (documento de la rama, "Decisiones del
-- usuario para G1"): a quien ya estaba activo se le pide el correo una vez,
-- sin bloquearlo (`modo = 'existente'`); las altas nuevas con la clave
-- encendida sí bloquean el despacho de negocio hasta verificar
-- (`modo = 'alta'`). Ese control de despacho es de G1b/G1c; acá sólo se
-- guarda el modo por ciclo para que puedan leerlo.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0100 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'prisma_owner') then
    raise exception '0100 requires 0004_function_ownership.sql';
  end if;
  if to_regclass('prisma.alta_correo_evento') is not null then
    raise exception '0100 ya está aplicada.';
  end if;
end $$;

-- =========================================================================
-- Proyección del ciclo de alta con correo
-- =========================================================================

create table alta_correo_estado (
  membership_id            uuid primary key
                             references membership(id) on delete cascade,
  workspace_id             uuid not null references workspace(id) on delete cascade,
  ciclo                    integer not null check (ciclo > 0),
  modo                     text not null check (modo in ('alta', 'existente')),
  estado                   text not null check (estado in (
                              'pending_welcome', 'awaiting_email',
                              'pending_email_verification', 'active', 'revoked')),
  review_required          boolean not null default false,
  review_required_causa    text,
  review_required_desde    timestamptz,
  bienvenida_entregada_en  timestamptz,
  actualizado_en           timestamptz not null default now(),
  check (review_required = (review_required_causa is not null))
);

comment on table alta_correo_estado is
  'Proyección del ciclo de alta con correo de una membresía. Nunca se '
  'escribe con update directo: la escribe aplicar_evento_alta_correo(), '
  'disparada por alta_correo_evento. bloquear_actualizacion_directa_alta_correo() '
  'lo hace cumplir.';

-- =========================================================================
-- Eventos append-only que la proyectan
-- =========================================================================

create table alta_correo_evento (
  id                uuid primary key default gen_random_uuid(),
  workspace_id      uuid not null references workspace(id) on delete cascade,
  membership_id     uuid not null references membership(id) on delete cascade,
  ciclo             integer not null check (ciclo > 0),
  tipo              text not null default 'transicion'
                      check (tipo in ('transicion', 'marca_revision',
                                       'resuelta_revision', 'bienvenida_entregada',
                                       'intento_habilitado')),
  modo              text check (modo in ('alta', 'existente')),
  estado_anterior   text,
  estado_nuevo      text,
  causa             text,
  actor_kind        tipo_actor not null,
  actor_app_user_id uuid references app_user(id),
  at                timestamptz not null default now(),
  check (tipo <> 'transicion' or (estado_nuevo is not null and modo is not null)),
  check (tipo <> 'marca_revision' or causa is not null)
);

comment on table alta_correo_evento is
  'Registro append-only. Es la verdad; alta_correo_estado es su proyección. '
  'workspace_id no lo aporta quien inserta: lo deriva preparar_evento_alta_correo() '
  'de la membresía, igual que derivar_espacio_evento_tarea() para las tareas.';

-- `intento_habilitado` (G1d-b, acción F de la administración sobre "envíos
-- agotados"): un hecho más, nunca una transición de estado -- el ciclo sigue
-- exactamente donde estaba, `alta_correo_estado.estado` no cambia (por eso
-- `aplicar_evento_alta_correo()` no tiene ninguna rama para este tipo). Lo
-- único que hace es marcar, dentro del ciclo vigente, desde cuándo volver a
-- contar el cupo de 5 envíos: `emitir_verificacion_correo()` sólo cuenta los
-- envíos posteriores al último evento de este tipo. El límite de 3 por hora
-- no se toca -- sigue contando sobre todos los envíos, honesto incluso justo
-- después de habilitar.

-- Sólo una marca de "bienvenida entregada" por ciclo: es un hecho, no una
-- cola de reintentos -- el reintento de la entrega en sí lo maneja el
-- outbox (`message_outbox`), esto es apenas su registro.
create unique index alta_correo_evento_bienvenida_unica
  on alta_correo_evento (membership_id, ciclo) where tipo = 'bienvenida_entregada';

create index alta_correo_evento_membership on alta_correo_evento (membership_id, at desc);
create index alta_correo_evento_ws on alta_correo_evento (workspace_id, at desc);

-- --- El espacio se deriva y la transición se valida ANTES de insertar -----
--
-- Security definer -- a diferencia de derivar_espacio_evento_tarea() -- por
-- una razón puntual: el `for update` sobre la proyección exige privilegio de
-- `update`, no sólo `select`, y prisma_app no lo tiene sobre
-- alta_correo_estado (revocado a propósito, para que nadie la escriba
-- salvo por evento). El dueño (`prisma_owner`) no saltea la RLS, así que la
-- comprobación sigue acotada al espacio de la sesión: una membresía de otro
-- espacio, o su proyección, quedan ocultas igual que si no existieran.
create or replace function preparar_evento_alta_correo() returns trigger
security definer set search_path = prisma, public, pg_temp as $$
declare
  actual alta_correo_estado%rowtype;
  encontrada boolean;
begin
  select m.workspace_id into new.workspace_id
    from membership m where m.id = new.membership_id;
  if new.workspace_id is null then
    raise exception 'alta_correo_evento: no existe la membresía %', new.membership_id;
  end if;

  select * into actual from alta_correo_estado
   where membership_id = new.membership_id
   for update;
  encontrada := found;

  if new.tipo = 'transicion' then
    if not encontrada then
      if new.ciclo is distinct from 1 or new.estado_anterior is not null
         or new.estado_nuevo not in ('pending_welcome', 'awaiting_email') then
        raise exception
          'alta_correo_evento: el primer ciclo sólo puede empezar en pending_welcome o awaiting_email';
      end if;
    elsif new.ciclo = actual.ciclo then
      if new.estado_anterior is distinct from actual.estado then
        raise exception
          'alta_correo_evento: el estado anterior (%) no coincide con el proyectado (%)',
          new.estado_anterior, actual.estado;
      end if;
      if new.modo is distinct from actual.modo then
        raise exception 'alta_correo_evento: el modo no cambia dentro de un mismo ciclo';
      end if;
      if not (
           (actual.estado = 'pending_welcome' and new.estado_nuevo = 'awaiting_email')
        or (actual.estado = 'awaiting_email' and new.estado_nuevo = 'pending_email_verification')
        or (actual.estado = 'pending_email_verification' and new.estado_nuevo in ('active', 'awaiting_email'))
        or (actual.estado = 'active' and new.estado_nuevo = 'revoked')
      ) then
        raise exception 'alta_correo_evento: transición inválida de % a %',
          actual.estado, new.estado_nuevo;
      end if;
    elsif new.ciclo = actual.ciclo + 1 then
      if actual.estado <> 'revoked' then
        raise exception
          'alta_correo_evento: no se puede abrir un ciclo nuevo sin revocar el anterior';
      end if;
      if new.estado_anterior is not null
         or new.estado_nuevo not in ('pending_welcome', 'awaiting_email') then
        raise exception
          'alta_correo_evento: un ciclo nuevo sólo puede empezar en pending_welcome o awaiting_email';
      end if;
    else
      raise exception 'alta_correo_evento: número de ciclo inválido';
    end if;
  else
    if not encontrada then
      raise exception 'alta_correo_evento: no hay ciclo de alta abierto para esta membresía';
    end if;
    if new.ciclo is distinct from actual.ciclo then
      raise exception 'alta_correo_evento: el ciclo no coincide con el vigente';
    end if;
  end if;

  return new;
end $$ language plpgsql;

create trigger trg_preparar_evento_alta_correo
  before insert on alta_correo_evento
  for each row execute function preparar_evento_alta_correo();

-- --- La proyección la escribe únicamente el disparador ---------------------
--
-- Security definer por el mismo motivo que aplicar_evento_tarea(): la
-- conexión administrativa no define espacio alguno, y sin fijarlo acá el
-- insert/update de abajo no encontraría fila. GUC propia
-- (`prisma.aplicando_evento_alta_correo`), separada de la de tareas, para no
-- acoplar los dos disparadores de "sólo por evento".
create or replace function aplicar_evento_alta_correo() returns trigger
security definer set search_path = prisma, public, pg_temp as $$
declare espacio_anterior text := current_setting('prisma.workspace_id', true);
begin
  perform set_config('prisma.workspace_id', new.workspace_id::text, true);
  perform set_config('prisma.aplicando_evento_alta_correo', '1', true);

  if new.tipo = 'transicion' then
    insert into alta_correo_estado
        (membership_id, workspace_id, ciclo, modo, estado, actualizado_en)
      values (new.membership_id, new.workspace_id, new.ciclo, new.modo,
              new.estado_nuevo, new.at)
    on conflict (membership_id) do update
      set ciclo = excluded.ciclo,
          modo = excluded.modo,
          estado = excluded.estado,
          actualizado_en = new.at,
          -- Un ciclo nuevo empieza limpio: la marca de revisión y la
          -- bienvenida entregada son del ciclo anterior, no de éste.
          review_required = case when excluded.ciclo <> alta_correo_estado.ciclo
                                  then false else alta_correo_estado.review_required end,
          review_required_causa = case when excluded.ciclo <> alta_correo_estado.ciclo
                                  then null else alta_correo_estado.review_required_causa end,
          review_required_desde = case when excluded.ciclo <> alta_correo_estado.ciclo
                                  then null else alta_correo_estado.review_required_desde end,
          bienvenida_entregada_en = case when excluded.ciclo <> alta_correo_estado.ciclo
                                  then null else alta_correo_estado.bienvenida_entregada_en end;
  elsif new.tipo = 'marca_revision' then
    update alta_correo_estado
       set review_required = true, review_required_causa = new.causa,
           review_required_desde = new.at, actualizado_en = new.at
     where membership_id = new.membership_id;
  elsif new.tipo = 'resuelta_revision' then
    update alta_correo_estado
       set review_required = false, review_required_causa = null,
           review_required_desde = null, actualizado_en = new.at
     where membership_id = new.membership_id;
  elsif new.tipo = 'bienvenida_entregada' then
    update alta_correo_estado
       set bienvenida_entregada_en = new.at, actualizado_en = new.at
     where membership_id = new.membership_id;
  end if;

  perform set_config('prisma.aplicando_evento_alta_correo', '0', true);
  perform set_config('prisma.workspace_id', coalesce(espacio_anterior, ''), true);
  return new;
end $$ language plpgsql;

create trigger trg_aplicar_evento_alta_correo
  after insert on alta_correo_evento
  for each row execute function aplicar_evento_alta_correo();

create or replace function bloquear_actualizacion_directa_alta_correo() returns trigger as $$
begin
  if coalesce(current_setting('prisma.aplicando_evento_alta_correo', true), '0') <> '1' then
    raise exception
      'El estado del alta con correo no se escribe directamente. Insertá una fila en alta_correo_evento.';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_bloquear_actualizacion_directa_alta_correo
  before update on alta_correo_estado
  for each row execute function bloquear_actualizacion_directa_alta_correo();

-- =========================================================================
-- Contacto verificado
-- =========================================================================

create table alta_correo_contacto (
  membership_id   uuid primary key references membership(id) on delete cascade,
  workspace_id    uuid not null references workspace(id) on delete cascade,
  email           text not null check (email = lower(btrim(email))),
  verificado_en   timestamptz not null default now(),
  actualizado_en  timestamptz not null default now()
);

create unique index alta_correo_contacto_email_unico_por_espacio
  on alta_correo_contacto (workspace_id, email);

comment on table alta_correo_contacto is
  'Un correo verificado por integrante. Sólo lo escribe completar_verificacion_correo(); '
  'prisma_app no tiene insert ni update directos sobre esta tabla.';

-- =========================================================================
-- Token de verificación -- mismo patrón que acceso_tablero: ninguna
-- concesión a prisma_app, sólo execute sobre las tres funciones de abajo.
-- =========================================================================

create table alta_correo_verificacion (
  id                            uuid primary key default gen_random_uuid(),
  workspace_id                  uuid not null references workspace(id) on delete cascade,
  membership_id                 uuid not null references membership(id) on delete cascade,
  ciclo                         integer not null check (ciclo > 0),
  email                         text not null check (email = lower(btrim(email))),
  token_hash                    text not null unique,
  proveedor_referencia          text,
  vigente                       boolean not null default true,
  emitido_en                    timestamptz not null default now(),
  expira_en                     timestamptz not null,
  reservado_por_membership_id   uuid references membership(id),
  reservado_hasta               timestamptz,
  consumido_en                  timestamptz
);

create unique index alta_correo_verificacion_vigente_unica
  on alta_correo_verificacion (membership_id, ciclo) where vigente;
create index alta_correo_verificacion_hora on alta_correo_verificacion (membership_id, emitido_en);

revoke all on alta_correo_verificacion from public;

comment on table alta_correo_verificacion is
  'Sólo el hash SHA-256 del token, nunca el valor en claro. Lo protege no '
  'tener ningún privilegio concedido a prisma_app: la única puerta son '
  'emitir_verificacion_correo(), reservar_verificacion_correo() y '
  'completar_verificacion_correo().';

-- --- Emisión (y reenvío) ---------------------------------------------------
--
-- Límites de `01-INCORPORACION-E-IDENTIDAD.md` §6: 3 envíos por hora y 5 por
-- ciclo, contando el inicial. Se cuentan sobre las filas ya insertadas --
-- append-only de hecho, aunque la tabla admita update para la reserva --
-- nunca sobre un contador mutable que alguien podría perder junto con una
-- fila. El correo activo de otro integrante del espacio se rechaza acá,
-- antes de gastar un envío; completar_verificacion_correo() lo vuelve a
-- comprobar al confirmar, porque pudo cambiar entre medio.
create or replace function emitir_verificacion_correo(
    p_membership_id uuid, p_email text, p_token_hash text,
    p_proveedor_referencia text, p_ahora timestamptz)
returns table (ok boolean, motivo text, id uuid)
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare
  espacio uuid;
  ciclo_actual integer;
  estado_actual text;
  envios_hora integer;
  envios_ciclo integer;
  desde_habilitado timestamptz;
  nuevo uuid;
begin
  if p_email <> lower(btrim(p_email)) then
    raise exception 'emitir_verificacion_correo: el correo tiene que llegar normalizado';
  end if;

  select m.workspace_id into espacio
    from membership m where m.id = p_membership_id and m.activo;
  if espacio is null then
    return query select false, 'verification_membership_invalid'::text, null::uuid;
    return;
  end if;

  -- El `for update` bloquea la proyección de esta membresía hasta el final
  -- de la transacción: dos emisiones concurrentes para la misma persona se
  -- serializan acá, así los límites de 3/hora y 5/ciclo cuentan sobre un
  -- estado que no puede cambiar debajo de la cuenta (G1a2, hallazgo de la
  -- revisión).
  select e.ciclo, e.estado into ciclo_actual, estado_actual
    from alta_correo_estado e
   where e.membership_id = p_membership_id
   for update;
  if ciclo_actual is null then
    return query select false, 'verification_no_cycle'::text, null::uuid;
    return;
  end if;
  if estado_actual not in ('awaiting_email', 'pending_email_verification') then
    return query select false, 'verification_state_invalid'::text, null::uuid;
    return;
  end if;

  if exists (
       select 1 from alta_correo_contacto c
        where c.workspace_id = espacio and c.email = p_email
          and c.membership_id <> p_membership_id) then
    return query select false, 'email_in_use'::text, null::uuid;
    return;
  end if;

  select count(*) into envios_hora from alta_correo_verificacion
   where membership_id = p_membership_id and emitido_en > p_ahora - interval '1 hour';
  if envios_hora >= 3 then
    return query select false, 'verification_rate_limited'::text, null::uuid;
    return;
  end if;

  -- G1d-b (acción F): un `intento_habilitado` reabre el cupo del ciclo
  -- vigente -- sólo cuentan los envíos posteriores al último de esos
  -- eventos (si nunca hubo uno, cuentan todos, como siempre). El límite de
  -- 3 por hora de arriba no mira esto: sigue contando sobre todos los
  -- envíos, sin excepción.
  select max(ev.at) into desde_habilitado
    from alta_correo_evento ev
   where ev.membership_id = p_membership_id and ev.ciclo = ciclo_actual
     and ev.tipo = 'intento_habilitado';

  select count(*) into envios_ciclo from alta_correo_verificacion
   where membership_id = p_membership_id and ciclo = ciclo_actual
     and (desde_habilitado is null or emitido_en > desde_habilitado);
  if envios_ciclo >= 5 then
    return query select false, 'verification_send_limit'::text, null::uuid;
    return;
  end if;

  update alta_correo_verificacion
     set vigente = false
   where membership_id = p_membership_id and ciclo = ciclo_actual and vigente;

  -- El lock de arriba ya vuelve esto inalcanzable en la práctica; queda como
  -- defensa en profundidad: si de algún modo dos emisiones llegaran a
  -- competir por el mismo (membership_id, ciclo) vigente, la base devuelve
  -- un motivo tipado, nunca una excepción cruda.
  begin
    insert into alta_correo_verificacion
        (workspace_id, membership_id, ciclo, email, token_hash,
         proveedor_referencia, vigente, emitido_en, expira_en)
      values (espacio, p_membership_id, ciclo_actual, p_email, p_token_hash,
              p_proveedor_referencia, true, p_ahora, p_ahora + interval '24 hours')
      returning alta_correo_verificacion.id into nuevo;
  exception when unique_violation then
    return query select false, 'verification_conflict'::text, null::uuid;
    return;
  end;

  return query select true, null::text, nuevo;
end $$;

-- --- Reserva (5 minutos) ---------------------------------------------------
--
-- El `for update` evita que dos reservas concurrentes por el mismo token se
-- crucen. La membresía que reclama tiene que ser la que originó el token: un
-- enlace reenviado a otra cuenta de Telegram no verifica (A04).
--
-- G1t/B6 (textos aprobados por el usuario, 2026-09-28): el dueño equivocado
-- (integrante o no) se rechaza SEGUNDO, inmediatamente después de "no
-- existe" -- antes de mirar si está consumido, vigente o vencido. Antes esos
-- tres chequeos corrían primero, así que quien abre un token ajeno recibía
-- un motivo distinto según el estado interno del token de otra persona
-- (`verification_token_consumed`/`_invalid`/`_expired`) -- una filtración
-- más fina de lo que A04 permite. Con el dueño equivocado cortando temprano,
-- `verification_token_superseded` (más abajo) y `verification_token_expired`
-- sólo los ve nunca nadie más que el dueño real.
create or replace function reservar_verificacion_correo(
    p_token_hash text, p_membership_id uuid, p_ahora timestamptz)
returns table (ok boolean, motivo text, workspace_id uuid, ciclo integer, email text)
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare
  v alta_correo_verificacion%rowtype;
  espacio_anterior text := current_setting('prisma.workspace_id', true);
  membresia_activa boolean;
begin
  select * into v from alta_correo_verificacion a
   where a.token_hash = p_token_hash
   for update;

  if not found then
    return query select false, 'verification_token_invalid'::text,
                        null::uuid, null::integer, null::text;
    return;
  end if;
  if v.membership_id <> p_membership_id then
    return query select false, 'verification_token_invalid'::text,
                        null::uuid, null::integer, null::text;
    return;
  end if;
  if v.consumido_en is not null then
    return query select false, 'verification_token_consumed'::text,
                        null::uuid, null::integer, null::text;
    return;
  end if;
  if not v.vigente then
    -- El token es real y es de quien lo abre, pero un envío posterior (un
    -- reenvío, un cambio de dirección) ya lo reemplazó (B7b): distinto de
    -- "inválido" -- la persona tiene un enlace más nuevo esperándola.
    return query select false, 'verification_token_superseded'::text,
                        null::uuid, null::integer, null::text;
    return;
  end if;
  if v.expira_en < p_ahora then
    return query select false, 'verification_token_expired'::text,
                        null::uuid, null::integer, null::text;
    return;
  end if;

  -- `membership` lleva política de aislamiento y esta función puede llegar
  -- sin ningún espacio declarado en la sesión (el `/start pv_{token}` de
  -- Telegram, antes de saber a qué equipo pertenece). Fija el espacio del
  -- token sólo para esta lectura y lo restaura enseguida: nada más abajo
  -- necesita RLS (G1a2, hallazgo de la revisión).
  perform set_config('prisma.workspace_id', v.workspace_id::text, true);
  membresia_activa := exists (select 1 from membership m
                                where m.id = p_membership_id and m.activo);
  perform set_config('prisma.workspace_id', coalesce(espacio_anterior, ''), true);

  if not membresia_activa then
    return query select false, 'verification_token_invalid'::text,
                        null::uuid, null::integer, null::text;
    return;
  end if;
  -- La reserva es de exclusión mutua, no de propiedad: mientras esté viva
  -- (5 minutos), NADIE puede volver a reservar el mismo token -- ni
  -- siquiera la propia membresía que la abrió -- para que dos procesos
  -- concurrentes no se crucen a mitad de la verificación.
  if v.reservado_hasta is not null and v.reservado_hasta > p_ahora then
    return query select false, 'verification_token_busy'::text,
                        null::uuid, null::integer, null::text;
    return;
  end if;

  update alta_correo_verificacion
     set reservado_por_membership_id = p_membership_id,
         reservado_hasta = p_ahora + interval '5 minutes'
   where id = v.id;

  return query select true, null::text, v.workspace_id, v.ciclo, v.email;
end $$;

-- --- Consumo ----------------------------------------------------------------
--
-- Escribe el contacto verificado y el evento a `active` en la misma
-- transacción de la función: si el contacto choca contra un correo activo de
-- otro integrante (pudo cambiar entre la reserva y acá), libera la reserva y
-- devuelve un estado recuperable en vez de abortar a mitad de camino.
create or replace function completar_verificacion_correo(
    p_token_hash text, p_membership_id uuid, p_ahora timestamptz)
returns table (ok boolean, motivo text)
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare
  v alta_correo_verificacion%rowtype;
  espacio_anterior text := current_setting('prisma.workspace_id', true);
  proyeccion alta_correo_estado%rowtype;
begin
  select * into v from alta_correo_verificacion a
   where a.token_hash = p_token_hash
   for update;

  if not found then
    return query select false, 'verification_token_invalid'::text;
    return;
  end if;
  if v.consumido_en is not null then
    return query select false, 'verification_token_consumed'::text;
    return;
  end if;
  if not v.vigente then
    return query select false, 'verification_token_invalid'::text;
    return;
  end if;
  if v.expira_en < p_ahora then
    return query select false, 'verification_token_expired'::text;
    return;
  end if;
  if v.membership_id <> p_membership_id then
    return query select false, 'verification_token_invalid'::text;
    return;
  end if;
  if v.reservado_por_membership_id is distinct from p_membership_id
     or v.reservado_hasta is null or v.reservado_hasta < p_ahora then
    return query select false, 'verification_token_busy'::text;
    return;
  end if;

  -- Desde acá se leen y escriben tablas con política de aislamiento
  -- (`membership`, `alta_correo_estado`, `alta_correo_contacto`): el espacio
  -- se fija ANTES de tocarlas, para que llamar sin espacio declarado en la
  -- sesión (el `/start pv_{token}` de Telegram, antes de saber a qué equipo
  -- pertenece) resuelva el camino feliz y no choque contra la RLS. Se
  -- restaura en cada salida de acá en adelante, no sólo al final (G1a2,
  -- hallazgo de la revisión).
  perform set_config('prisma.workspace_id', v.workspace_id::text, true);

  if not exists (select 1 from membership m
                  where m.id = p_membership_id and m.activo) then
    perform set_config('prisma.workspace_id', coalesce(espacio_anterior, ''), true);
    return query select false, 'verification_token_invalid'::text;
    return;
  end if;

  -- El estado se comprueba (y se bloquea) antes de escribir el contacto:
  -- una salida por estado cambiado no deja un correo verificado a medias.
  select * into proyeccion from alta_correo_estado
   where membership_id = p_membership_id
   for update;
  if not found or proyeccion.estado <> 'pending_email_verification' then
    update alta_correo_verificacion set reservado_hasta = null where id = v.id;
    perform set_config('prisma.workspace_id', coalesce(espacio_anterior, ''), true);
    return query select false, 'verification_state_changed'::text;
    return;
  end if;

  begin
    insert into alta_correo_contacto
        (membership_id, workspace_id, email, verificado_en, actualizado_en)
      values (p_membership_id, v.workspace_id, v.email, p_ahora, p_ahora)
    on conflict (membership_id) do update
      set email = excluded.email, verificado_en = excluded.verificado_en,
          actualizado_en = excluded.actualizado_en;
  exception when unique_violation then
    update alta_correo_verificacion set reservado_hasta = null where id = v.id;
    perform set_config('prisma.workspace_id', coalesce(espacio_anterior, ''), true);
    return query select false, 'email_in_use'::text;
    return;
  end;

  insert into alta_correo_evento
      (membership_id, ciclo, tipo, modo, estado_anterior, estado_nuevo, actor_kind)
    values (p_membership_id, v.ciclo, 'transicion', proyeccion.modo,
            'pending_email_verification', 'active', 'persona');
  perform set_config('prisma.workspace_id', coalesce(espacio_anterior, ''), true);

  update alta_correo_verificacion
     set consumido_en = p_ahora, reservado_hasta = null, vigente = false
   where id = v.id;

  return query select true, null::text;
end $$;

-- --- Candado de la proyección ------------------------------------------------
--
-- Serializa lecturas que deciden si hace falta escribir
-- (`alta_correo.estado(..., bloquear=True)`, usado por
-- `alta_correo_flujo._completar_bienvenida` y por `abrir_ciclo_alta` antes de
-- abrir el ciclo). Vive en una función para no conceder `update` a
-- `prisma_app`: con ese privilegio podría fijar la marca de sesión que
-- desactiva el disparador y escribir la proyección directamente.
create or replace function bloquear_alta_correo_estado(p_membership_id uuid)
returns void
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
begin
  -- Candado transaccional por membresía (G1d-a2, ítem 6), no un `for update`
  -- sobre la fila: tiene que serializar TAMBIÉN cuando la fila todavía no
  -- existe (la proyección se crea recién con el primer evento -- quien abre
  -- el ciclo toma este candado ANTES de `iniciar_ciclo`) o cuando quien
  -- llama no declaró ningún espacio en la sesión (`admin()`, sin
  -- `prisma.workspace_id`): un `for update` sobre `alta_correo_estado` no
  -- encuentra ninguna fila en esos dos casos -- en el segundo, porque
  -- `prisma_owner` no ignora la RLS y la política de aislamiento compara
  -- contra `NULL`, aunque la fila exista -- y entonces no serializa nada. El
  -- advisory lock no pasa por la tabla ni por la RLS: sólo depende de
  -- `p_membership_id`, así que sirve en los dos casos. Es transaccional
  -- (`_xact_`): se libera solo al terminar la transacción de quien llama,
  -- nunca hay que soltarlo a mano, y es reentrante dentro de la misma
  -- transacción (mismo patrón que ya usa `cli._correo_verificacion` para su
  -- propio bloqueo consultivo). La clave lleva un espacio de nombres propio
  -- (G1d-a3, ítem 5, prefijo `'alta_correo_estado:'`) para no compartir
  -- claves con otro candado que hashee el mismo texto crudo (`membership_id`
  -- a secas) para un propósito distinto -- mismo motivo que ya distingue
  -- `task:<id>` de `task-intake:<espacio>:<membresía>:<chat>` en
  -- `herramientas.py`/`ingreso_tareas.py`.
  perform pg_advisory_xact_lock(
    hashtextextended('alta_correo_estado:' || p_membership_id::text, 0));
end $$;

-- --- Lectura del envío vigente ----------------------------------------------
--
-- Sólo lo necesita el flujo conversacional (G1b) para saber si un correo
-- tipeado mientras hay una verificación pendiente es igual al que ya se
-- pidió verificar, o es una dirección distinta que hay que proponer antes de
-- cambiarla. Nunca expone el hash del token: sólo el correo y su vencimiento.
create or replace function verificacion_vigente_correo(p_membership_id uuid)
returns table (email text, expira_en timestamptz)
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
begin
  return query
    select a.email, a.expira_en from alta_correo_verificacion a
     where a.membership_id = p_membership_id and a.vigente
     order by a.emitido_en desc limit 1;
end $$;

-- --- Existencia, sin revelar nada más ---------------------------------------
--
-- G1t/B6 (textos aprobados por el usuario, 2026-09-28): distinguir un enlace
-- roto (nunca existió, o un typo) de uno real abierto por la cuenta
-- equivocada necesita saber si el token EXISTE, sin filtrar a quién
-- pertenece, su correo ni su estado -- ninguna otra cosa. Nunca hashtext ni
-- comparación en Python: el hash ya viaja hasheado (`alta_correo.hash_token`)
-- y esto sólo devuelve un booleano.
create or replace function existe_verificacion_correo(p_token_hash text)
returns boolean
language sql security definer set search_path = prisma, public, pg_temp as $$
  select exists (select 1 from alta_correo_verificacion where token_hash = p_token_hash);
$$;

-- --- Cuándo se puede volver a reenviar (B11) --------------------------------
--
-- El límite de 3 por hora es una ventana corrediza, no una hora de reloj: se
-- puede volver a enviar recién cuando el envío MÁS VIEJO dentro de la última
-- hora sale de esa ventana. `null` si no hay ningún envío en la última hora
-- (nada que esperar).
create or replace function proximo_reenvio_correo(p_membership_id uuid, p_ahora timestamptz)
returns timestamptz
language sql security definer set search_path = prisma, public, pg_temp as $$
  select min(emitido_en) + interval '1 hour'
    from alta_correo_verificacion
   where membership_id = p_membership_id and emitido_en > p_ahora - interval '1 hour';
$$;

-- =========================================================================
-- Avisos administrativos -- "🛠️ Administración" (G1d los entrega)
-- =========================================================================

create table aviso_administrativo (
  id               uuid primary key default gen_random_uuid(),
  workspace_id     uuid not null references workspace(id) on delete cascade,
  tipo             text not null,
  texto_saneado    text not null,
  referencia_tipo  text,
  referencia_id    uuid,
  creado_en        timestamptz not null default now(),
  leido_en         timestamptz,
  leido_por        uuid references app_user(id),
  resuelto_en      timestamptz,
  resuelto_por     uuid references app_user(id),
  check (leido_en is not null or leido_por is null),
  check (resuelto_en is not null or resuelto_por is null)
);

create index aviso_administrativo_pendientes
  on aviso_administrativo (workspace_id, creado_en) where resuelto_en is null;

-- Idempotencia bajo concurrencia (G1d, ítem 4): dos disparadores del mismo
-- aviso (mismo tipo, misma referencia) casi al mismo tiempo -- p. ej. dos
-- mensajes que agotan el límite de reenvío en la misma ventana -- no pueden
-- crear dos filas mientras la primera siga sin resolver. Sólo se aplica
-- cuando hay una referencia real: `referencia_tipo`/`referencia_id` en
-- `null` (un aviso sin referencia puntual) nunca colisiona entre sí, porque
-- Postgres trata cada `null` como distinto en un índice único -- mismo
-- comportamiento que ya tenía `aviso_pendiente()` en Python, ahora también
-- garantizado por la base bajo carrera. `workspace_id` va primero en el
-- índice (G1d-a2, ítem 5): el aislamiento entre clientes es el invariante
-- número uno del producto, y no puede depender de que `referencia_id` sea,
-- por casualidad, distinto entre espacios -- dos espacios con el mismo
-- (tipo, referencia) son dos avisos independientes, nunca uno "pisando" al
-- otro.
create unique index aviso_administrativo_pendiente_unico
  on aviso_administrativo (workspace_id, tipo, referencia_tipo, referencia_id)
  where resuelto_en is null;

comment on table aviso_administrativo is
  'Avisos "🛠️ Administración". Leído no es resuelto: se conservan hasta '
  'marcarse explícitamente, así el futuro panel de plataforma también podrá '
  'listarlos.';

-- El espacio no lo declara quien inserta: lo fija la sesión, igual que
-- audit_log e incident. Reutiliza la función existente -- es genérica, no
-- hace falta declarar otra.
create trigger trg_derivar_espacio_aviso_administrativo
  before insert on aviso_administrativo
  for each row execute function derivar_espacio_registro();

-- =========================================================================
-- Entrega de avisos por el bot de administración (G1d)
-- =========================================================================
--
-- `message_outbox` exige `workspace_id` y se despacha por el bot de CADA
-- espacio (`despachador.despachar(cur, workspace_id, transporte, ...)`); el
-- bot de administración es uno solo para toda la plataforma, así que
-- necesita su propio camino de salida -- reusar `message_outbox` mandaría
-- el aviso por el bot equivocado.
--
-- Una fila por (aviso, administrador): permite reintentos y backoff por
-- destinatario, igual que `despachador._fallo`, sin que la falla de
-- entregarle a uno bloquee a los demás. `proximo_intento_en` (G1d-a2, ítem
-- 2) es la espera creciente real entre reintentos -- `null` significa
-- "listo para intentarse ya"; el despacho sólo toma filas cuya marca ya
-- pasó, en vez de reintentar en cada vuelta del loop.
create table aviso_administrativo_entrega (
  id                  uuid primary key default gen_random_uuid(),
  workspace_id        uuid not null references workspace(id) on delete cascade,
  aviso_id            uuid not null references aviso_administrativo(id) on delete cascade,
  app_user_id         uuid not null references app_user(id) on delete cascade,
  estado              text not null default 'listo'
                        check (estado in ('listo', 'enviado', 'fallido')),
  intentos            integer not null default 0,
  ultimo_error        text,
  proximo_intento_en  timestamptz,
  telegram_message_id bigint,
  delivered_at        timestamptz,
  creado_en           timestamptz not null default now(),
  check (estado <> 'enviado' or delivered_at is not null)
);

create unique index aviso_administrativo_entrega_unica
  on aviso_administrativo_entrega (aviso_id, app_user_id);
create index aviso_administrativo_entrega_pendientes
  on aviso_administrativo_entrega (estado) where estado = 'listo';

comment on table aviso_administrativo_entrega is
  'Entrega por integrante administrador de un aviso "🛠️ Administración" -- ver el comentario de arriba sobre por qué no reusa message_outbox.';

-- Cola de salida del bot de administración para respuestas puntuales (la
-- confirmación de "Marcar leído", la guía a quien escribe texto libre):
-- mismo motivo que la tabla de arriba -- no hay ningún espacio al que
-- mandarle esto por message_outbox. No lleva alcance de espacio: es un
-- mensaje suelto a un chat de administración, no una fila con dueño de
-- espacio (mismo motivo por el que app_user y platform_role tampoco
-- llevan workspace_id).
create table aviso_administrativo_respuesta (
  id                  uuid primary key default gen_random_uuid(),
  chat_id             bigint not null,
  texto               text not null,
  -- Botones opcionales de esta respuesta puntual (G1d-b: la vista previa de
  -- "Habilitar un nuevo intento" trae Confirmar/Cancelar) -- lista de
  -- `{"etiqueta": ..., "callback_data": ...}`, en el mismo orden en que se
  -- muestran. `null`/`[]` es una respuesta sin botones, como todas las de
  -- antes de G1d-b.
  botones             jsonb,
  estado              text not null default 'listo'
                        check (estado in ('listo', 'enviado', 'fallido')),
  intentos            integer not null default 0,
  ultimo_error        text,
  proximo_intento_en  timestamptz,
  telegram_message_id bigint,
  enviado_en          timestamptz,
  dedupe_key          text not null,
  creado_en           timestamptz not null default now()
);

create unique index aviso_administrativo_respuesta_dedupe
  on aviso_administrativo_respuesta (dedupe_key);
create index aviso_administrativo_respuesta_pendientes
  on aviso_administrativo_respuesta (estado) where estado = 'listo';

comment on table aviso_administrativo_respuesta is
  'Respuestas puntuales del bot de administración (confirmación de botón, guía de texto libre). Sin alcance de espacio: ver el comentario de aviso_administrativo_entrega.';

-- =========================================================================
-- Aislamiento entre espacios
-- =========================================================================

alter table alta_correo_estado enable row level security;
alter table alta_correo_estado force row level security;
create policy aislamiento_espacio on alta_correo_estado
  using (workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid);
-- Sólo `select`: el candado de fila se toma con
-- `bloquear_alta_correo_estado()`, nunca con `update` concedido acá.
grant select on alta_correo_estado to prisma_app;

alter table alta_correo_evento enable row level security;
alter table alta_correo_evento force row level security;
create policy aislamiento_espacio on alta_correo_evento
  using (workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid);
grant insert on alta_correo_evento to prisma_app;

alter table alta_correo_contacto enable row level security;
alter table alta_correo_contacto force row level security;
create policy aislamiento_espacio on alta_correo_contacto
  using (workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid);
grant select on alta_correo_contacto to prisma_app;

alter table aviso_administrativo enable row level security;
alter table aviso_administrativo force row level security;
create policy aislamiento_espacio on aviso_administrativo
  using (workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid);
-- Sin `update` (G1d, ítem 3): los flujos que crean avisos siguen
-- insertando (`alta_correo.crear_aviso`), pero marcarlos leídos o
-- resueltos es sólo del camino de administración, que corre bajo
-- `prisma_admin` (ya tiene `all` más abajo) -- nunca `prisma_app`.
grant select, insert on aviso_administrativo to prisma_app;

alter table aviso_administrativo_entrega enable row level security;
alter table aviso_administrativo_entrega force row level security;
create policy aislamiento_espacio on aviso_administrativo_entrega
  using (workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid);
-- Nada para `prisma_app`: sólo lo toca el despacho del bot de
-- administración, que corre bajo `prisma_admin`.

-- `aviso_administrativo_respuesta` no lleva RLS: no tiene `workspace_id`
-- (ver su comentario de tabla, arriba).

-- alta_correo_verificacion no lleva política: igual que acceso_tablero, lo
-- que la protege es que nadie la consulta.

-- --- Propiedad y privilegios de prisma_owner --------------------------------

grant select, insert, update on alta_correo_estado to prisma_owner;
-- `select` (G1d-b/G1t): `emitir_verificacion_correo()` ahora lee sus propios
-- eventos para saber desde cuándo volver a contar el cupo del ciclo tras un
-- `intento_habilitado` (acción F). Sigue sin ningún privilegio para
-- `prisma_app` -- sólo `insert`, arriba.
grant select, insert on alta_correo_evento to prisma_owner;
grant select, insert, update on alta_correo_contacto to prisma_owner;
grant select, insert, update on alta_correo_verificacion to prisma_owner;
grant all on alta_correo_estado, alta_correo_evento, alta_correo_contacto,
             alta_correo_verificacion, aviso_administrativo,
             aviso_administrativo_entrega, aviso_administrativo_respuesta
             to prisma_admin;

alter function preparar_evento_alta_correo() owner to prisma_owner;
alter function aplicar_evento_alta_correo() owner to prisma_owner;
alter function emitir_verificacion_correo(uuid, text, text, text, timestamptz)
  owner to prisma_owner;
alter function reservar_verificacion_correo(text, uuid, timestamptz)
  owner to prisma_owner;
alter function completar_verificacion_correo(text, uuid, timestamptz)
  owner to prisma_owner;
alter function verificacion_vigente_correo(uuid) owner to prisma_owner;
alter function bloquear_alta_correo_estado(uuid) owner to prisma_owner;
alter function existe_verificacion_correo(text) owner to prisma_owner;
alter function proximo_reenvio_correo(uuid, timestamptz) owner to prisma_owner;

revoke execute on function emitir_verificacion_correo(uuid, text, text, text, timestamptz)
  from public;
revoke execute on function reservar_verificacion_correo(text, uuid, timestamptz)
  from public;
revoke execute on function completar_verificacion_correo(text, uuid, timestamptz)
  from public;
revoke execute on function verificacion_vigente_correo(uuid) from public;
revoke execute on function bloquear_alta_correo_estado(uuid) from public;
revoke execute on function existe_verificacion_correo(text) from public;
revoke execute on function proximo_reenvio_correo(uuid, timestamptz) from public;
grant execute on function emitir_verificacion_correo(uuid, text, text, text, timestamptz)
  to prisma_app;
grant execute on function reservar_verificacion_correo(text, uuid, timestamptz)
  to prisma_app;
grant execute on function completar_verificacion_correo(text, uuid, timestamptz)
  to prisma_app;
grant execute on function verificacion_vigente_correo(uuid) to prisma_app;
-- G1d-b: `avisos_admin.confirmar_habilitar` lee el correo vigente para
-- avisarle a la persona -- corre bajo `prisma_admin` (el canal de
-- administración), no dentro de `espacio()`.
grant execute on function verificacion_vigente_correo(uuid) to prisma_admin;
grant execute on function bloquear_alta_correo_estado(uuid) to prisma_app;
grant execute on function bloquear_alta_correo_estado(uuid) to prisma_admin;
grant execute on function existe_verificacion_correo(text) to prisma_app;
grant execute on function proximo_reenvio_correo(uuid, timestamptz) to prisma_app;

commit;
