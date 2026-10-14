\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0074_la_revision_de_la_entrada_con_telegram.sql.
--
-- Devuelve las funciones y las restricciones a como las dejó la 0073. Se niega a correr si una marca
-- o una respuesta quedó con el pedido en nulo (la 0073 lo exige).
--
-- Vuelta atrás de una sola vía después de la primera purga (revisión de la MA-2). Desde la 0074,
-- cada pedido de entrada nuevo borra los pedidos vencidos hace más de un día y deja en nulo el
-- pedido de sus marcas y respuestas (`pedir_entrada_por_qr`), y cada firma nueva borra las huellas
-- de firmas vencidas hace más de un día. Lo purgado no vuelve con esta vuelta atrás: los pedidos y
-- las huellas viejos ya no existen, y en cuanto hay una marca o una respuesta con el pedido en nulo
-- este archivo se niega (abajo). Para volver a la 0073 después de eso, hay que restaurar el
-- respaldo de antes de la 0074 (`leda_motor-antes-0074-20261014.dump`, en `db/respaldos/`) o
-- decidir a mano qué hacer con esas filas; ni las marcas ni las respuestas se borran desde acá.
begin;
set search_path = leda, public;
set local row_security = off;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0074 rollback requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if exists (select 1 from message_outbox_entrada_web
              where destino = 'entrar_en_la_compu' and pedido_de_entrada_id is null)
     or exists (select 1 from admin_notice
                 where boton = 'entrar_en_la_compu' and pedido_de_entrada_id is null) then
    raise exception '0074 rollback refused: hay botones de pedidos de entrada ya purgados';
  end if;
end $$;

alter table message_outbox_entrada_web
  drop constraint message_outbox_entrada_web_pedido_de_entrada;
alter table message_outbox_entrada_web add constraint message_outbox_entrada_web_pedido_de_entrada
  foreign key (pedido_de_entrada_id) references pedido_de_entrada(id) on delete cascade;
alter table message_outbox_entrada_web drop constraint message_outbox_entrada_web_pedido;
alter table message_outbox_entrada_web add constraint message_outbox_entrada_web_pedido
  check ((destino = 'entrar_en_la_compu') = (pedido_de_entrada_id is not null));

alter table admin_notice drop constraint admin_notice_pedido_de_entrada;
alter table admin_notice add constraint admin_notice_pedido_de_entrada
  foreign key (pedido_de_entrada_id) references pedido_de_entrada(id) on delete cascade;
alter table admin_notice drop constraint admin_notice_boton_del_pedido;
alter table admin_notice add constraint admin_notice_boton_del_pedido
  check ((boton is not distinct from 'entrar_en_la_compu') = (pedido_de_entrada_id is not null));

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

commit;
