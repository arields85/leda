\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0072_quien_revisa_sigue_activo.sql. Entrar a la web con Telegram: la Mini App en
-- el celular y el QR en la computadora (ADR 0024, aceptado el 2026-10-14; unidad MA de
-- `odd/tasks/plataforma-jerarquias.md`).
--
-- - **Las sesiones ya no nacen sólo de un enlace** (decisión 9): `sesion_web` y
--   `sesion_de_administracion` dejan de exigir `enlace_id` y guardan su `origen`: `mini_app` (la
--   firma de Telegram, validada en el servidor), `qr` (un pedido de entrada aprobado en Telegram)
--   o `enlace` (el de un solo uso, mientras exista). La de la Mini App vence a las 24 horas (se
--   abre otra en cada apertura); la de la computadora, a los días que la administración eligió
--   para el espacio (decisión 5; sin elegir, no vence). Una vencida queda cortada con el motivo
--   `vencio`, como la de quien dejó el equipo.
-- - **La firma de Telegram sirve una vez** (decisión 7): `firma_de_telegram` guarda la huella de
--   cada una hasta que vence. El servidor la valida (HMAC-SHA256 con el token del bot de esa
--   puerta) antes de llamar a la base; la base la gasta, busca la membresía activa del espacio
--   de ese bot (o el rol de plataforma) por `app_user.telegram_user_id` y abre la sesión.
-- - **El pedido de entrada del QR** (decisión 8): `pedido_de_entrada`, con sólo las huellas del
--   código del QR y del secreto que guarda la computadora; vence a los 5 minutos y sirve una vez.
--   Lo aprueba en Telegram quien toca "Entrar en la compu", y la computadora lo canjea por su
--   sesión.
-- - **Cuánto dura la sesión de la computadora**, por espacio (`workspace_setting`,
--   `sesion_en_la_compu_dias`: 1, 7, 30 o 90; sin la fila, sin vencimiento). Sólo la cambia una
--   sesión de administración, y queda auditado.
-- - **Los botones** (decisiones 1, 2 y 10): la marca de la salida (`message_outbox_entrada_web`)
--   dice a dónde lleva el botón de la web (`destino`, y la tarea si es una), o que es el botón
--   "Entrar en la compu" de un pedido; una respuesta del bot de administración lleva su botón
--   (`admin_notice.boton`).
--
-- Ninguna de las tablas nuevas tiene privilegios para `leda_app`: sólo `execute` sobre sus
-- funciones (`security definer`, dueño `leda_owner`). Se deshace con
-- `db/rollbacks/0073_entrar_con_telegram.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0073 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0072 está aplicada y la 0073 no.
do $$ begin
  if position('elegido_activo' in pg_get_functiondef('leda.quien_revisa_la_tarea(uuid)'::regprocedure)) = 0 then
    raise exception '0073 preflight failed: falta la 0072';
  end if;
  if to_regclass('leda.pedido_de_entrada') is not null then
    raise exception '0073 ya está aplicada.';
  end if;
end $$;

-- --- Las sesiones -------------------------------------------------------------------------------

alter table sesion_web alter column enlace_id drop not null;
alter table sesion_web add column origen text not null default 'enlace';
alter table sesion_web add constraint sesion_web_origen
  check (origen in ('mini_app', 'qr', 'enlace'));
alter table sesion_web add constraint sesion_web_enlace_del_origen
  check ((origen = 'enlace') = (enlace_id is not null));
alter table sesion_web drop constraint sesion_web_motivo;
alter table sesion_web add constraint sesion_web_motivo check (motivo_de_corte in (
  'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_el_equipo', 'vencio'));

alter table sesion_de_administracion alter column enlace_id drop not null;
alter table sesion_de_administracion add column origen text not null default 'enlace';
alter table sesion_de_administracion add constraint sesion_de_administracion_origen
  check (origen in ('mini_app', 'qr', 'enlace'));
alter table sesion_de_administracion add constraint sesion_de_administracion_enlace_del_origen
  check ((origen = 'enlace') = (enlace_id is not null));
alter table sesion_de_administracion drop constraint sesion_de_administracion_motivo;
alter table sesion_de_administracion add constraint sesion_de_administracion_motivo
  check (motivo_de_corte in (
    'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_de_ser_administrador',
    'vencio'));

-- --- Cuánto dura la sesión de la computadora (decisión 5) --------------------------------------

alter table workspace_setting add constraint workspace_setting_sesion_en_la_compu check (
  case
    when clave <> 'sesion_en_la_compu_dias' then true
    when jsonb_typeof(valor) <> 'number' then false
    else (valor #>> '{}') in ('1', '7', '30', '90')
  end);

-- --- La firma de Telegram y el pedido de entrada del QR ------------------------------------------

create table firma_de_telegram (
  huella     text primary key,
  puerta     text not null,
  usada_en   timestamptz not null default now(),
  vence_en   timestamptz not null,
  constraint firma_de_telegram_huella check (huella ~ '^[0-9a-f]{64}$'),
  constraint firma_de_telegram_puerta check (puerta in ('equipo', 'administracion'))
);

comment on table firma_de_telegram is
  'ADR 0024, decisión 7: la huella (sha256) de cada firma de Telegram que abrió una sesión, hasta que vence: cada firma sirve una sola vez. Nunca la firma ni los datos de Telegram. leda_app no tiene privilegios: sólo execute sobre las funciones que abren la sesión.';

create table pedido_de_entrada (
  id                          uuid primary key default gen_random_uuid(),
  puerta                      text not null,
  workspace_id                uuid references workspace(id) on delete cascade,
  codigo_hash                 text not null,
  secreto_hash                text not null,
  desde                       text not null,
  estado                      text not null default 'pendiente',
  pedido_en                   timestamptz not null default now(),
  vence_en                    timestamptz not null,
  aprobado_en                 timestamptz,
  aprobado_por_membership_id  uuid,
  aprobado_por_app_user_id    uuid references app_user(id) on delete cascade,
  gastado_en                  timestamptz,
  constraint pedido_de_entrada_codigo_unico unique (codigo_hash),
  constraint pedido_de_entrada_secreto_unico unique (secreto_hash),
  constraint pedido_de_entrada_hashes
    check (codigo_hash ~ '^[0-9a-f]{64}$' and secreto_hash ~ '^[0-9a-f]{64}$'),
  constraint pedido_de_entrada_puerta check (puerta in ('equipo', 'administracion')),
  constraint pedido_de_entrada_espacio_de_la_puerta
    check ((puerta = 'equipo') = (workspace_id is not null)),
  constraint pedido_de_entrada_desde check (length(desde) between 1 and 120),
  constraint pedido_de_entrada_estado
    check (estado in ('pendiente', 'aprobado', 'gastado', 'vencido')),
  constraint pedido_de_entrada_aprobado check (
    (aprobado_en is null) = (aprobado_por_membership_id is null and aprobado_por_app_user_id is null)
    and (aprobado_por_membership_id is null or puerta = 'equipo')
    and (aprobado_por_app_user_id is null or puerta = 'administracion')),
  constraint pedido_de_entrada_gastado
    check ((estado = 'gastado') = (gastado_en is not null)
           and (estado not in ('aprobado', 'gastado') or aprobado_en is not null)),
  constraint pedido_de_entrada_membership
    foreign key (workspace_id, aprobado_por_membership_id) references membership(workspace_id, id)
    on delete cascade
);

comment on table pedido_de_entrada is
  'ADR 0024, decisión 8: el pedido de entrada de una computadora por el QR. Sólo las huellas del código del QR (el que lleva el enlace t.me/<bot>?start=) y del secreto que guarda la computadora; vence a los 5 minutos y sirve una vez. Lo aprueba en Telegram quien toca "Entrar en la compu" (la membresía activa del espacio de ese bot, o el rol de plataforma), y la computadora lo canjea por su sesión. leda_app no tiene privilegios: sólo execute sobre sus funciones.';

-- --- Los botones de la salida --------------------------------------------------------------------

alter table message_outbox_entrada_web add column destino text not null default 'inicio';
alter table message_outbox_entrada_web add column task_id uuid;
alter table message_outbox_entrada_web add column pedido_de_entrada_id uuid;
alter table message_outbox_entrada_web add constraint message_outbox_entrada_web_destino
  check (destino in ('inicio', 'equipo', 'tarea', 'cargar_tarea', 'crear_objetivo',
                     'entrar_en_la_compu'));
alter table message_outbox_entrada_web add constraint message_outbox_entrada_web_tarea
  check ((destino = 'tarea') = (task_id is not null));
alter table message_outbox_entrada_web add constraint message_outbox_entrada_web_pedido
  check ((destino = 'entrar_en_la_compu') = (pedido_de_entrada_id is not null));
alter table message_outbox_entrada_web add constraint message_outbox_entrada_web_task
  foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade;
alter table message_outbox_entrada_web add constraint message_outbox_entrada_web_pedido_de_entrada
  foreign key (pedido_de_entrada_id) references pedido_de_entrada(id) on delete cascade;

comment on table message_outbox_entrada_web is
  'ADR 0024, decisiones 1, 2 y 10 (migración 0073; antes, ADR 0022, decisión 4): la fila de la salida lleva un botón para esta persona: el que abre la web donde corresponde (destino: inicio, equipo, tarea, cargar_tarea o crear_objetivo; es_ofrecimiento, el ofrecimiento de una sola vez) o "Entrar en la compu" de un pedido de entrada. El despachador lo arma al mandar, sólo en un chat privado. Sólo se agrega.';

alter table admin_notice add column boton text;
alter table admin_notice add column pedido_de_entrada_id uuid;
alter table admin_notice add constraint admin_notice_boton
  check (boton in ('administracion', 'entrar_en_la_compu'));
alter table admin_notice add constraint admin_notice_boton_del_pedido
  check ((boton is not distinct from 'entrar_en_la_compu') = (pedido_de_entrada_id is not null));
alter table admin_notice add constraint admin_notice_pedido_de_entrada
  foreign key (pedido_de_entrada_id) references pedido_de_entrada(id) on delete cascade;

-- --- Privilegios de las tablas -------------------------------------------------------------------

grant all privileges on firma_de_telegram, pedido_de_entrada to leda_admin;
revoke all on firma_de_telegram, pedido_de_entrada from public, leda_app;
grant select, insert, delete on firma_de_telegram to leda_owner;
grant select, insert, delete on pedido_de_entrada to leda_owner;
grant update (estado, aprobado_en, aprobado_por_membership_id, aprobado_por_app_user_id,
              gastado_en) on pedido_de_entrada to leda_owner;

-- --- Las funciones -------------------------------------------------------------------------------

create or replace function sesion_vigente(p_token_hash text)
returns table (sesion_id uuid, workspace_id uuid, membership_id uuid)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        sesion sesion_web%rowtype;
        dias integer;
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
  -- Vencida (migración 0073; ADR 0024, decisiones 5 y 9): la de la Mini App, a las 24 horas (se
  -- abre otra en cada apertura); la de la computadora, a los días que eligió la administración
  -- para el espacio (sin elegir, no vence). Queda cortada y no vuelve.
  select (w.valor #>> '{}')::integer into dias from workspace_setting w
   where w.workspace_id = sesion.workspace_id and w.clave = 'sesion_en_la_compu_dias';
  if (sesion.origen = 'mini_app' and sesion.creada_en <= now() - interval '24 hours')
     or (sesion.origen = 'qr' and dias is not null
         and sesion.creada_en <= now() - make_interval(days => dias)) then
    update sesion_web s set cortada_en = now(), motivo_de_corte = 'vencio'
     where s.id = sesion.id and s.cortada_en is null;
    if found then
      perform auditar_acceso_web(
        sesion.workspace_id, null, 'sistema', 'cortar_sesion_web', 'sesion_web', sesion.id,
        jsonb_build_object('motivo', 'vencio', 'membership_id', sesion.membership_id,
                           'origen', sesion.origen));
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
  -- La de la Mini App vence a las 24 horas (migración 0073): se abre otra en cada apertura.
  if sesion.origen = 'mini_app' and sesion.creada_en <= now() - interval '24 hours' then
    update sesion_de_administracion s set cortada_en = now(), motivo_de_corte = 'vencio'
     where s.id = sesion.id and s.cortada_en is null;
    if found then
      perform auditar_acceso_de_administracion(
        null, 'sistema', 'cortar_sesion_de_administracion', 'sesion_de_administracion',
        sesion.id, jsonb_build_object('motivo', 'vencio', 'app_user_id', sesion.app_user_id,
                                      'origen', sesion.origen));
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

-- La firma de Telegram que abre una sesión se gasta una sola vez: `true` si es la primera. Las que
-- vencieron hace más de un día ya no hacen falta (una vencida no abre nada aunque se repita). De
-- uso interno: no la ejecuta nadie más que su dueño.
create or replace function gastar_firma_de_telegram(
    p_huella text, p_puerta text, p_vence_en timestamptz)
returns boolean
language plpgsql set search_path = leda, public, pg_temp as $$
begin
  delete from firma_de_telegram f where f.vence_en < now() - interval '1 day';
  insert into firma_de_telegram (huella, puerta, vence_en)
       values (p_huella, p_puerta, p_vence_en)
  on conflict (huella) do nothing;
  return found;
end $$;

-- La sesión de la puerta del equipo que abre la Mini App (ADR 0024, decisiones 7 y 9). El
-- servidor ya validó la firma con el token del bot del espacio `p_slug`; acá se gasta la firma,
-- se busca la membresía activa de ese espacio por el usuario de Telegram y se abre la sesión,
-- auditada con su origen. El espacio sale del bot que firmó, nunca de otro dato.
create or replace function abrir_sesion_por_telegram(
    p_slug text, p_telegram_user_id bigint, p_huella text, p_vence_en timestamptz,
    p_sesion_token_hash text)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        espacio uuid;
        persona uuid;
        usuario uuid;
        nueva uuid;
begin
  if p_huella is null or p_huella !~ '^[0-9a-f]{64}$'
     or p_sesion_token_hash is null or p_sesion_token_hash !~ '^[0-9a-f]{64}$'
     or p_telegram_user_id is null or p_vence_en is null then
    return jsonb_build_object('ok', false, 'motivo', 'mal_formado');
  end if;
  select w.id into espacio from workspace w where w.slug = p_slug and w.activo;
  if espacio is null then
    return jsonb_build_object('ok', false, 'motivo', 'sin_espacio');
  end if;
  if not gastar_firma_de_telegram(p_huella, 'equipo', p_vence_en) then
    return jsonb_build_object('ok', false, 'motivo', 'firma_usada');
  end if;
  perform set_config('leda.workspace_id', espacio::text, true);
  select m.id, m.app_user_id into persona, usuario
    from membership m join app_user u on u.id = m.app_user_id
   where m.workspace_id = espacio and u.telegram_user_id = p_telegram_user_id and m.activo;
  if persona is null then
    perform set_config('leda.workspace_id', previo, true);
    return jsonb_build_object('ok', false, 'motivo', 'sin_membresia');
  end if;
  insert into sesion_web (workspace_id, membership_id, token_hash, origen)
       values (espacio, persona, p_sesion_token_hash, 'mini_app')
    returning id into nueva;
  perform auditar_acceso_web(
    espacio, usuario, 'persona', 'abrir_sesion_web', 'sesion_web', nueva,
    jsonb_build_object('origen', 'mini_app', 'membership_id', persona));
  perform set_config('leda.workspace_id', previo, true);
  return jsonb_build_object('ok', true, 'sesion_id', nueva);
end $$;

-- Lo mismo por la puerta de administración, con la firma del bot de administración: el rol de
-- plataforma vigente del usuario de Telegram.
create or replace function abrir_sesion_de_administracion_por_telegram(
    p_telegram_user_id bigint, p_huella text, p_vence_en timestamptz, p_sesion_token_hash text)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare usuario uuid;
        nueva uuid;
begin
  if p_huella is null or p_huella !~ '^[0-9a-f]{64}$'
     or p_sesion_token_hash is null or p_sesion_token_hash !~ '^[0-9a-f]{64}$'
     or p_telegram_user_id is null or p_vence_en is null then
    return jsonb_build_object('ok', false, 'motivo', 'mal_formado');
  end if;
  if not gastar_firma_de_telegram(p_huella, 'administracion', p_vence_en) then
    return jsonb_build_object('ok', false, 'motivo', 'firma_usada');
  end if;
  select u.id into usuario from app_user u
   where u.telegram_user_id = p_telegram_user_id and es_administrador_de_plataforma(u.id);
  if usuario is null then
    return jsonb_build_object('ok', false, 'motivo', 'sin_rol');
  end if;
  insert into sesion_de_administracion (app_user_id, token_hash, origen)
       values (usuario, p_sesion_token_hash, 'mini_app')
    returning id into nueva;
  perform auditar_acceso_de_administracion(
    usuario, 'persona', 'abrir_sesion_de_administracion', 'sesion_de_administracion', nueva,
    jsonb_build_object('origen', 'mini_app'));
  return jsonb_build_object('ok', true, 'sesion_id', nueva);
end $$;

-- La computadora pide entrar por el QR (decisión 8): un pedido pendiente que vence a los 5
-- minutos, con las huellas de su código y de su secreto. Para la puerta del equipo, el espacio
-- del bot al que lleva el QR. Sin autenticación: nada se audita hasta que alguien lo aprueba, y
-- hay un tope de pedidos pendientes por puerta y espacio.
create or replace function pedir_entrada_por_qr(
    p_puerta text, p_slug text, p_codigo_hash text, p_secreto_hash text, p_desde text)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare espacio uuid;
        nuevo uuid;
        vence timestamptz := now() + interval '5 minutes';
begin
  if p_puerta is null or p_puerta not in ('equipo', 'administracion')
     or p_codigo_hash is null or p_codigo_hash !~ '^[0-9a-f]{64}$'
     or p_secreto_hash is null or p_secreto_hash !~ '^[0-9a-f]{64}$'
     or p_desde is null or length(p_desde) not between 1 and 120 then
    return jsonb_build_object('ok', false, 'motivo', 'mal_formado');
  end if;
  if p_puerta = 'equipo' then
    select w.id into espacio from workspace w where w.slug = p_slug and w.activo;
    if espacio is null then
      return jsonb_build_object('ok', false, 'motivo', 'sin_espacio');
    end if;
  end if;
  delete from pedido_de_entrada p where p.vence_en < now() - interval '1 day';
  if (select count(*) from pedido_de_entrada p
       where p.puerta = p_puerta and p.workspace_id is not distinct from espacio
         and p.estado = 'pendiente' and p.vence_en > now()) >= 30 then
    return jsonb_build_object('ok', false, 'motivo', 'demasiados');
  end if;
  insert into pedido_de_entrada (puerta, workspace_id, codigo_hash, secreto_hash, desde, vence_en)
       values (p_puerta, espacio, p_codigo_hash, p_secreto_hash, p_desde, vence)
    returning id into nuevo;
  return jsonb_build_object('ok', true, 'pedido_id', nuevo, 'vence_en', vence);
end $$;

-- Lo que el bot muestra antes de "Entrar en la compu": el pedido pendiente de ese código, de esa
-- puerta (y, la del equipo, del espacio de ese bot), con el nombre del espacio y desde dónde se
-- pidió. Nada si venció, ya se usó o es de otra puerta u otro espacio.
create or replace function ver_pedido_de_entrada(
    p_codigo_hash text, p_puerta text, p_slug text)
returns table (pedido_id uuid, espacio text, desde text, pedido_en timestamptz,
               vence_en timestamptz)
language sql stable security definer set search_path = leda, public, pg_temp as $$
  select p.id, w.nombre, p.desde, p.pedido_en, p.vence_en
    from pedido_de_entrada p
    left join workspace w on w.id = p.workspace_id
   where p.codigo_hash = p_codigo_hash and p.puerta = p_puerta
     and p.estado = 'pendiente' and p.vence_en > now()
     and (p.puerta = 'administracion' or w.slug = p_slug);
$$;

-- "Entrar en la compu": quien tocó el botón en Telegram aprueba el pedido, que queda ligado a
-- esa persona (la membresía activa del espacio de ese bot) o, por la puerta de administración, a
-- su rol de plataforma. Una sola vez, y antes de que venza. Queda auditado.
create or replace function aprobar_pedido_de_entrada(
    p_pedido_id uuid, p_puerta text, p_slug text, p_telegram_user_id bigint)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        pedido pedido_de_entrada%rowtype;
        espacio uuid;
        persona uuid;
        usuario uuid;
begin
  select * into pedido from pedido_de_entrada p where p.id = p_pedido_id for update;
  if pedido.id is null or pedido.puerta is distinct from p_puerta then
    return jsonb_build_object('ok', false, 'motivo', 'no_esta');
  end if;
  if p_puerta = 'equipo' then
    select w.id into espacio from workspace w where w.slug = p_slug;
    if espacio is null or espacio <> pedido.workspace_id then
      return jsonb_build_object('ok', false, 'motivo', 'no_esta');
    end if;
  end if;
  if pedido.estado <> 'pendiente' then
    return jsonb_build_object('ok', false, 'motivo', case pedido.estado
      when 'aprobado' then 'ya_aprobado' when 'vencido' then 'vencido' else 'ya_usado' end);
  end if;
  if pedido.vence_en <= now() then
    update pedido_de_entrada p set estado = 'vencido' where p.id = pedido.id;
    return jsonb_build_object('ok', false, 'motivo', 'vencido');
  end if;
  if p_puerta = 'equipo' then
    perform set_config('leda.workspace_id', espacio::text, true);
    select m.id, m.app_user_id into persona, usuario
      from membership m join app_user u on u.id = m.app_user_id
     where m.workspace_id = espacio and u.telegram_user_id = p_telegram_user_id and m.activo;
    if persona is null then
      perform set_config('leda.workspace_id', previo, true);
      return jsonb_build_object('ok', false, 'motivo', 'sin_membresia');
    end if;
    update pedido_de_entrada p
       set estado = 'aprobado', aprobado_en = now(), aprobado_por_membership_id = persona
     where p.id = pedido.id;
    perform auditar_acceso_web(
      espacio, usuario, 'persona', 'aprobar_pedido_de_entrada', 'pedido_de_entrada', pedido.id,
      jsonb_build_object('membership_id', persona, 'desde', pedido.desde));
    perform set_config('leda.workspace_id', previo, true);
  else
    select u.id into usuario from app_user u
     where u.telegram_user_id = p_telegram_user_id and es_administrador_de_plataforma(u.id);
    if usuario is null then
      return jsonb_build_object('ok', false, 'motivo', 'sin_rol');
    end if;
    update pedido_de_entrada p
       set estado = 'aprobado', aprobado_en = now(), aprobado_por_app_user_id = usuario
     where p.id = pedido.id;
    perform auditar_acceso_de_administracion(
      usuario, 'persona', 'aprobar_pedido_de_entrada', 'pedido_de_entrada', pedido.id,
      jsonb_build_object('desde', pedido.desde));
  end if;
  return jsonb_build_object('ok', true);
end $$;

-- La computadora pregunta por su pedido con su secreto: pendiente, vencido o, si ya está
-- aprobado, su sesión (origen `qr`), una sola vez. La membresía (o el rol) se revalida al
-- canjearlo. La sesión nueva queda auditada con su origen.
create or replace function canjear_pedido_de_entrada(
    p_pedido_id uuid, p_puerta text, p_secreto_hash text, p_sesion_token_hash text)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        pedido pedido_de_entrada%rowtype;
        usuario uuid;
        nueva uuid;
begin
  if p_secreto_hash is null or p_secreto_hash !~ '^[0-9a-f]{64}$'
     or p_sesion_token_hash is null or p_sesion_token_hash !~ '^[0-9a-f]{64}$' then
    return jsonb_build_object('estado', 'no_esta');
  end if;
  select * into pedido from pedido_de_entrada p where p.id = p_pedido_id for update;
  if pedido.id is null or pedido.puerta is distinct from p_puerta
     or pedido.secreto_hash <> p_secreto_hash or pedido.estado = 'gastado' then
    return jsonb_build_object('estado', 'no_esta');
  end if;
  if pedido.estado = 'vencido' or pedido.vence_en <= now() then
    update pedido_de_entrada p set estado = 'vencido'
     where p.id = pedido.id and p.estado in ('pendiente', 'aprobado');
    return jsonb_build_object('estado', 'vencido');
  end if;
  if pedido.estado = 'pendiente' then
    return jsonb_build_object('estado', 'pendiente');
  end if;
  if p_puerta = 'equipo' then
    perform set_config('leda.workspace_id', pedido.workspace_id::text, true);
    select m.app_user_id into usuario from membership m
     where m.id = pedido.aprobado_por_membership_id and m.activo;
    if usuario is not null then
      insert into sesion_web (workspace_id, membership_id, token_hash, origen)
           values (pedido.workspace_id, pedido.aprobado_por_membership_id, p_sesion_token_hash,
                   'qr')
        returning id into nueva;
      perform auditar_acceso_web(
        pedido.workspace_id, usuario, 'persona', 'abrir_sesion_web', 'sesion_web', nueva,
        jsonb_build_object('origen', 'qr', 'membership_id', pedido.aprobado_por_membership_id,
                           'pedido_id', pedido.id));
    end if;
    perform set_config('leda.workspace_id', previo, true);
  elsif es_administrador_de_plataforma(pedido.aprobado_por_app_user_id) then
    insert into sesion_de_administracion (app_user_id, token_hash, origen)
         values (pedido.aprobado_por_app_user_id, p_sesion_token_hash, 'qr')
      returning id into nueva;
    perform auditar_acceso_de_administracion(
      pedido.aprobado_por_app_user_id, 'persona', 'abrir_sesion_de_administracion',
      'sesion_de_administracion', nueva,
      jsonb_build_object('origen', 'qr', 'pedido_id', pedido.id));
  end if;
  update pedido_de_entrada p set estado = 'gastado', gastado_en = now() where p.id = pedido.id;
  if nueva is null then
    return jsonb_build_object('estado', 'no_esta');
  end if;
  return jsonb_build_object('estado', 'adentro', 'sesion_id', nueva);
end $$;

-- Cuánto dura la sesión de la computadora en un espacio (decisión 5): 1, 7, 30 o 90 días, o sin
-- vencimiento (`null`). Sólo con una sesión de administración vigente; queda auditado.
create or replace function fijar_sesion_en_la_compu(
    p_token_hash text, p_workspace_id uuid, p_dias integer)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        usuario uuid;
        antes integer;
begin
  select s.app_user_id into usuario from sesion_de_administracion_vigente(p_token_hash) s;
  if usuario is null then
    return jsonb_build_object('ok', false, 'motivo', 'sin_sesion');
  end if;
  if p_dias is not null and p_dias not in (1, 7, 30, 90) then
    return jsonb_build_object('ok', false, 'motivo', 'mal_formado');
  end if;
  if not exists (select 1 from workspace w where w.id = p_workspace_id) then
    return jsonb_build_object('ok', false, 'motivo', 'sin_espacio');
  end if;
  perform set_config('leda.workspace_id', p_workspace_id::text, true);
  select (w.valor #>> '{}')::integer into antes from workspace_setting w
   where w.workspace_id = p_workspace_id and w.clave = 'sesion_en_la_compu_dias';
  if p_dias is null then
    delete from workspace_setting w
     where w.workspace_id = p_workspace_id and w.clave = 'sesion_en_la_compu_dias';
  else
    insert into workspace_setting (workspace_id, clave, valor)
         values (p_workspace_id, 'sesion_en_la_compu_dias', to_jsonb(p_dias))
    on conflict (workspace_id, clave) do update set valor = excluded.valor;
  end if;
  perform auditar_acceso_web(
    p_workspace_id, usuario, 'persona', 'fijar_sesion_en_la_compu', 'workspace',
    p_workspace_id, jsonb_build_object('dias', p_dias, 'antes', antes));
  perform set_config('leda.workspace_id', previo, true);
  return jsonb_build_object('ok', true, 'dias', p_dias);
end $$;

-- Lo que la web de administración muestra de ese ajuste: los días, o `null` sin vencimiento.
create or replace function sesion_en_la_compu(p_token_hash text, p_workspace_id uuid)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        dias integer;
begin
  if not exists (select 1 from sesion_de_administracion_vigente(p_token_hash)) then
    return jsonb_build_object('ok', false, 'motivo', 'sin_sesion');
  end if;
  if not exists (select 1 from workspace w where w.id = p_workspace_id) then
    return jsonb_build_object('ok', false, 'motivo', 'sin_espacio');
  end if;
  perform set_config('leda.workspace_id', p_workspace_id::text, true);
  select (w.valor #>> '{}')::integer into dias from workspace_setting w
   where w.workspace_id = p_workspace_id and w.clave = 'sesion_en_la_compu_dias';
  perform set_config('leda.workspace_id', previo, true);
  return jsonb_build_object('ok', true, 'dias', dias);
end $$;

alter function gastar_firma_de_telegram(text, text, timestamptz) owner to leda_owner;
alter function abrir_sesion_por_telegram(text, bigint, text, timestamptz, text) owner to leda_owner;
alter function abrir_sesion_de_administracion_por_telegram(bigint, text, timestamptz, text)
  owner to leda_owner;
alter function pedir_entrada_por_qr(text, text, text, text, text) owner to leda_owner;
alter function ver_pedido_de_entrada(text, text, text) owner to leda_owner;
alter function aprobar_pedido_de_entrada(uuid, text, text, bigint) owner to leda_owner;
alter function canjear_pedido_de_entrada(uuid, text, text, text) owner to leda_owner;
alter function fijar_sesion_en_la_compu(text, uuid, integer) owner to leda_owner;
alter function sesion_en_la_compu(text, uuid) owner to leda_owner;

revoke execute on function gastar_firma_de_telegram(text, text, timestamptz) from public;
revoke execute on function abrir_sesion_por_telegram(text, bigint, text, timestamptz, text)
  from public;
revoke execute on function abrir_sesion_de_administracion_por_telegram(bigint, text, timestamptz,
                                                                       text) from public;
revoke execute on function pedir_entrada_por_qr(text, text, text, text, text) from public;
revoke execute on function ver_pedido_de_entrada(text, text, text) from public;
revoke execute on function aprobar_pedido_de_entrada(uuid, text, text, bigint) from public;
revoke execute on function canjear_pedido_de_entrada(uuid, text, text, text) from public;
revoke execute on function fijar_sesion_en_la_compu(text, uuid, integer) from public;
revoke execute on function sesion_en_la_compu(text, uuid) from public;
-- La web (`leda_app`): abrir la sesión, pedir y canjear el pedido, y el ajuste de la
-- administración. Los bots: ver y aprobar el pedido (el del equipo corre como `leda_app`, el de
-- administración como `leda_admin`).
grant execute on function abrir_sesion_por_telegram(text, bigint, text, timestamptz, text)
  to leda_app;
grant execute on function abrir_sesion_de_administracion_por_telegram(bigint, text, timestamptz,
                                                                      text) to leda_app;
grant execute on function pedir_entrada_por_qr(text, text, text, text, text) to leda_app;
grant execute on function ver_pedido_de_entrada(text, text, text) to leda_app, leda_admin;
grant execute on function aprobar_pedido_de_entrada(uuid, text, text, bigint)
  to leda_app, leda_admin;
grant execute on function canjear_pedido_de_entrada(uuid, text, text, text) to leda_app;
grant execute on function fijar_sesion_en_la_compu(text, uuid, integer) to leda_app;
grant execute on function sesion_en_la_compu(text, uuid) to leda_app;

commit;
