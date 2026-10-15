\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0075_el_detalle_de_la_tarea.sql. El pase de la computadora (MA-5; ADR 0024,
-- precisión del 2026-10-14, noche): en Telegram de la computadora (escritorio o Telegram Web), el
-- lanzador manda la firma de Telegram al servidor, que la valida como la puerta de la Mini App
-- (HMAC con el token del bot de esa puerta, 10 minutos); la base la gasta (una sola vez, en
-- `firma_de_telegram`, la misma que gasta la Mini App), busca la membresía activa del espacio de
-- ese bot (o el rol de plataforma) y deja un pedido de entrada YA APROBADO por esa persona, que
-- vence al minuto, con sólo la huella del pase. El navegador lo canjea con
-- `canjear_pedido_de_entrada` (la misma del QR): la sesión es la de la computadora (origen `qr`,
-- dura lo que eligió el espacio), y el pedido se gasta. No hay tablas nuevas.
--
-- Se deshace con `db/rollbacks/0076_el_pase_a_la_compu.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0076 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0075 está aplicada y la 0076 no.
do $$ begin
  if to_regprocedure('leda.relaciones_de_la_pagina_de_tarea(text)') is null then
    raise exception '0076 preflight failed: falta la 0075';
  end if;
  if to_regprocedure('leda.emitir_pase_a_la_compu(text, text, bigint, text, timestamptz, text, text)')
     is not null then
    raise exception '0076 ya está aplicada.';
  end if;
end $$;

-- El pase de la computadora. El servidor ya validó la firma con el token del bot de esa puerta
-- (el del espacio `p_slug`, o el de administración); acá se exige que siga vigente, se gasta, se
-- revisa quién es y se deja el pedido aprobado, auditado. El código del pedido (el que llevaría
-- un QR) es al azar y nadie lo conoce: el pase no se ve ni se aprueba desde un bot.
create or replace function emitir_pase_a_la_compu(
    p_puerta text, p_slug text, p_telegram_user_id bigint, p_huella text, p_vence_en timestamptz,
    p_pase_hash text, p_desde text)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        espacio uuid;
        persona uuid;
        usuario uuid;
        nuevo uuid;
        codigo text := encode(sha256(convert_to(gen_random_uuid()::text || clock_timestamp()::text,
                                                'UTF8')), 'hex');
begin
  if p_puerta is null or p_puerta not in ('equipo', 'administracion')
     or p_huella is null or p_huella !~ '^[0-9a-f]{64}$'
     or p_pase_hash is null or p_pase_hash !~ '^[0-9a-f]{64}$'
     or p_telegram_user_id is null or p_vence_en is null
     or p_desde is null or length(p_desde) not between 1 and 120 then
    return jsonb_build_object('ok', false, 'motivo', 'mal_formado');
  end if;
  -- La firma vale 10 minutos desde que Telegram la emitió (como en la 0074).
  if p_vence_en <= now() or p_vence_en > now() + interval '11 minutes' then
    return jsonb_build_object('ok', false, 'motivo', 'firma_vencida');
  end if;
  if p_puerta = 'equipo' then
    select w.id into espacio from workspace w where w.slug = p_slug and w.activo;
    if espacio is null then
      return jsonb_build_object('ok', false, 'motivo', 'sin_espacio');
    end if;
  end if;
  if not gastar_firma_de_telegram(p_huella, p_puerta, p_vence_en) then
    return jsonb_build_object('ok', false, 'motivo', 'firma_usada');
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
  else
    select u.id into usuario from app_user u
     where u.telegram_user_id = p_telegram_user_id and es_administrador_de_plataforma(u.id);
    if usuario is null then
      return jsonb_build_object('ok', false, 'motivo', 'sin_rol');
    end if;
  end if;
  insert into pedido_de_entrada (puerta, workspace_id, codigo_hash, secreto_hash, desde, estado,
                                 vence_en, aprobado_en, aprobado_por_membership_id,
                                 aprobado_por_app_user_id)
       values (p_puerta, espacio, codigo, p_pase_hash, p_desde, 'aprobado',
               now() + interval '1 minute', now(), persona,
               case when p_puerta = 'administracion' then usuario end)
    returning id into nuevo;
  if p_puerta = 'equipo' then
    perform auditar_acceso_web(
      espacio, usuario, 'persona', 'emitir_pase_a_la_compu', 'pedido_de_entrada', nuevo,
      jsonb_build_object('membership_id', persona, 'desde', p_desde));
    perform set_config('leda.workspace_id', previo, true);
  else
    perform auditar_acceso_de_administracion(
      usuario, 'persona', 'emitir_pase_a_la_compu', 'pedido_de_entrada', nuevo,
      jsonb_build_object('desde', p_desde));
  end if;
  return jsonb_build_object('ok', true, 'pedido_id', nuevo);
end $$;

alter function emitir_pase_a_la_compu(text, text, bigint, text, timestamptz, text, text)
  owner to leda_owner;
revoke execute on function emitir_pase_a_la_compu(text, text, bigint, text, timestamptz, text,
                                                  text) from public;
-- La web (`leda_app`): la llama el lanzador, después de validar la firma.
grant execute on function emitir_pase_a_la_compu(text, text, bigint, text, timestamptz, text, text)
  to leda_app;

commit;
