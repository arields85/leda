\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0073_entrar_con_telegram.sql. La revisión de la MA (RDD de la unidad, 2026-10-14):
--
-- - **Purgar un pedido viejo no borra mensajes** (R3-cascade-purge-deletes-notices): la purga de
--   los pedidos de entrada vencidos hace más de un día (`pedir_entrada_por_qr`) borraba en cascada
--   la marca del botón de la salida y las respuestas del bot de administración que lo nombraban.
--   Ahora el pedido sólo queda en nulo (un botón de un pedido que ya no existe no sale).
-- - **La base exige que la firma de Telegram esté vigente** (R3-firma-expiry-not-enforced): no sólo
--   el servidor; una vencida, o una que dice vencer más allá de 10 minutos, no abre una sesión.
-- - **El tope de pedidos pendientes no se pasa con pedidos al mismo tiempo**
--   (R3-pending-cap-race): un candado por puerta y espacio antes de contar.
--
-- Se deshace con `db/rollbacks/0074_la_revision_de_la_entrada_con_telegram.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0074 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0073 está aplicada y la 0074 no.
do $$ begin
  if to_regclass('leda.pedido_de_entrada') is null then
    raise exception '0074 preflight failed: falta la 0073';
  end if;
  if position('firma_vencida' in pg_get_functiondef(
       'leda.abrir_sesion_por_telegram(text, bigint, text, timestamptz, text)'::regprocedure)) > 0 then
    raise exception '0074 ya está aplicada.';
  end if;
end $$;

alter table message_outbox_entrada_web
  drop constraint message_outbox_entrada_web_pedido_de_entrada;
alter table message_outbox_entrada_web add constraint message_outbox_entrada_web_pedido_de_entrada
  foreign key (pedido_de_entrada_id) references pedido_de_entrada(id) on delete set null;
alter table message_outbox_entrada_web drop constraint message_outbox_entrada_web_pedido;
alter table message_outbox_entrada_web add constraint message_outbox_entrada_web_pedido
  check (pedido_de_entrada_id is null or destino = 'entrar_en_la_compu');

alter table admin_notice drop constraint admin_notice_pedido_de_entrada;
alter table admin_notice add constraint admin_notice_pedido_de_entrada
  foreign key (pedido_de_entrada_id) references pedido_de_entrada(id) on delete set null;
alter table admin_notice drop constraint admin_notice_boton_del_pedido;
alter table admin_notice add constraint admin_notice_boton_del_pedido
  check (pedido_de_entrada_id is null or boton = 'entrar_en_la_compu');

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
  -- La firma vale 10 minutos desde que Telegram la emitió (migración 0074, revisión
  -- R3-firma-expiry-not-enforced): la base también lo exige, no sólo el servidor.
  if p_vence_en <= now() or p_vence_en > now() + interval '11 minutes' then
    return jsonb_build_object('ok', false, 'motivo', 'firma_vencida');
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
  -- La firma vale 10 minutos desde que Telegram la emitió (migración 0074, revisión
  -- R3-firma-expiry-not-enforced): la base también lo exige, no sólo el servidor.
  if p_vence_en <= now() or p_vence_en > now() + interval '11 minutes' then
    return jsonb_build_object('ok', false, 'motivo', 'firma_vencida');
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
  -- Uno a la vez por puerta y espacio, así el tope no se pasa con pedidos al mismo tiempo
  -- (migración 0074, revisión R3-pending-cap-race).
  perform pg_advisory_xact_lock(hashtextextended(
    'pedido_de_entrada:' || p_puerta || ':' || coalesce(espacio::text, ''), 0));
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

commit;
