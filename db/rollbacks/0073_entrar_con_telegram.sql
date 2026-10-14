\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0073_entrar_con_telegram.sql.
--
-- Borra las funciones de la entrada con Telegram, `firma_de_telegram` y `pedido_de_entrada`, los
-- botones de la salida (`destino`, la tarea y el pedido de `message_outbox_entrada_web`; el botón
-- de `admin_notice`), el ajuste de la sesión de la computadora, y devuelve las sesiones y
-- `sesion_vigente` y `sesion_de_administracion_vigente` a como las dejaron la 0057 y la 0061. Se
-- niega a correr si eso perdiera datos: una sesión que no nació de un enlace (volvería a exigirlo),
-- una cortada por vencida, una marca con otro destino que el de siempre, un botón del bot de
-- administración o el ajuste de un espacio. Lo que quedó en `audit_log` no se toca. Antes de
-- correrlo en una base con datos, `pg_dump` de esas tablas y vaciarlas a mano, con la decisión
-- registrada.
begin;
set search_path = leda, public;
-- Las comprobaciones de abajo tienen que ver todas las filas: sin la RLS. Un rol que no la
-- saltea falla acá en lugar de ver las tablas vacías y borrar lo que no vio.
set local row_security = off;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0073 rollback requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('leda.pedido_de_entrada') is not null and (
       exists (select 1 from sesion_web where origen <> 'enlace' or motivo_de_corte = 'vencio')
       or exists (select 1 from sesion_de_administracion
                   where origen <> 'enlace' or motivo_de_corte = 'vencio')
       or exists (select 1 from message_outbox_entrada_web where destino <> 'inicio')
       or exists (select 1 from admin_notice where boton is not null)
       or exists (select 1 from workspace_setting where clave = 'sesion_en_la_compu_dias')) then
    raise exception '0073 rollback refused: hay sesiones o botones de la entrada con Telegram, o el ajuste de la sesión de la computadora';
  end if;
end $$;

drop function if exists sesion_en_la_compu(text, uuid);
drop function if exists fijar_sesion_en_la_compu(text, uuid, integer);
drop function if exists canjear_pedido_de_entrada(uuid, text, text, text);
drop function if exists aprobar_pedido_de_entrada(uuid, text, text, bigint);
drop function if exists ver_pedido_de_entrada(text, text, text);
drop function if exists pedir_entrada_por_qr(text, text, text, text, text);
drop function if exists abrir_sesion_de_administracion_por_telegram(bigint, text, timestamptz,
                                                                    text);
drop function if exists abrir_sesion_por_telegram(text, bigint, text, timestamptz, text);
drop function if exists gastar_firma_de_telegram(text, text, timestamptz);

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

alter table admin_notice drop constraint admin_notice_pedido_de_entrada;
alter table admin_notice drop constraint admin_notice_boton_del_pedido;
alter table admin_notice drop constraint admin_notice_boton;
alter table admin_notice drop column pedido_de_entrada_id;
alter table admin_notice drop column boton;

alter table message_outbox_entrada_web drop constraint message_outbox_entrada_web_pedido_de_entrada;
alter table message_outbox_entrada_web drop constraint message_outbox_entrada_web_task;
alter table message_outbox_entrada_web drop constraint message_outbox_entrada_web_pedido;
alter table message_outbox_entrada_web drop constraint message_outbox_entrada_web_tarea;
alter table message_outbox_entrada_web drop constraint message_outbox_entrada_web_destino;
alter table message_outbox_entrada_web drop column pedido_de_entrada_id;
alter table message_outbox_entrada_web drop column task_id;
alter table message_outbox_entrada_web drop column destino;

comment on table message_outbox_entrada_web is
  'ADR 0022, decisión 4: la fila de la salida lleva al final el enlace de entrada a la web de esta persona (es_ofrecimiento: el ofrecimiento de una sola vez). El despachador lo emite al mandar; la base guarda sólo su hash (enlace_de_entrada). Sólo se agrega.';

drop table if exists pedido_de_entrada;
drop table if exists firma_de_telegram;

alter table workspace_setting drop constraint workspace_setting_sesion_en_la_compu;

alter table sesion_de_administracion drop constraint sesion_de_administracion_motivo;
alter table sesion_de_administracion add constraint sesion_de_administracion_motivo
  check (motivo_de_corte in (
    'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_de_ser_administrador'));
alter table sesion_de_administracion drop constraint sesion_de_administracion_enlace_del_origen;
alter table sesion_de_administracion drop constraint sesion_de_administracion_origen;
alter table sesion_de_administracion drop column origen;
alter table sesion_de_administracion alter column enlace_id set not null;

alter table sesion_web drop constraint sesion_web_motivo;
alter table sesion_web add constraint sesion_web_motivo check (motivo_de_corte in (
  'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_el_equipo'));
alter table sesion_web drop constraint sesion_web_enlace_del_origen;
alter table sesion_web drop constraint sesion_web_origen;
alter table sesion_web drop column origen;
alter table sesion_web alter column enlace_id set not null;

commit;
