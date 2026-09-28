\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0100_alta_con_correo.sql.
--
-- Removes the onboarding-with-email schema entirely: the projection, its
-- events, the verification token, the verified contact and the
-- administrative notices. Any verification link already handed out stops
-- working, which is the safe direction for a rollback of a credential
-- mechanism -- same reasoning as 0006's rollback of acceso_tablero.
--
-- With `correo_verificacion.habilitado` apagada (el estado por defecto),
-- nada de esto se usa, así que este rollback no le devuelve nada a `main`:
-- sólo saca el esquema que la rama auxiliar agregó.
begin;
set search_path = prisma, public;

-- Borra admin_reply primero: no depende de nada de la rama auxiliar salvo
-- aviso_administrativo_id (más su propia tabla se borra igual, completa).
drop index if exists admin_reply_pendientes;
drop table if exists admin_reply;

-- Revierte la extensión de admin_notice (0017) ANTES de borrar
-- aviso_administrativo: aviso_administrativo_id la referencia, y `drop
-- table` de abajo fallaría por esa dependencia si no se quita primero. Borra
-- también las filas que sólo existían por esa extensión (un aviso
-- administrativo nunca tuvo incident_id) -- mismo criterio que el resto de
-- este rollback: se retira el esquema entero de la rama auxiliar, sin
-- devolverle nada a `main`.
drop function if exists avisar_aviso_administrativo_admin(uuid, uuid, text, jsonb);
delete from admin_notice where incident_id is null;
alter table admin_notice drop constraint if exists admin_notice_una_referencia;
alter table admin_notice drop column if exists botones;
alter table admin_notice drop column if exists aviso_administrativo_id;
alter table admin_notice alter column incident_id set not null;

drop trigger if exists trg_derivar_espacio_aviso_administrativo on aviso_administrativo;
drop index if exists aviso_administrativo_pendiente_unico;
drop index if exists aviso_administrativo_pendientes;
drop table if exists aviso_administrativo;

drop function if exists proximo_reenvio_correo(uuid, timestamptz);
drop function if exists existe_verificacion_correo(text);
drop function if exists verificacion_vigente_correo(uuid);
drop function if exists bloquear_alta_correo_estado(uuid);
drop function if exists completar_verificacion_correo(text, uuid, timestamptz);
drop function if exists reservar_verificacion_correo(text, uuid, timestamptz);
drop function if exists emitir_verificacion_correo(uuid, text, text, text, timestamptz);

drop index if exists alta_correo_verificacion_hora;
drop index if exists alta_correo_verificacion_vigente_unica;
drop table if exists alta_correo_verificacion;

drop index if exists alta_correo_contacto_email_unico_por_espacio;
drop table if exists alta_correo_contacto;

drop trigger if exists trg_bloquear_actualizacion_directa_alta_correo on alta_correo_estado;
drop function if exists bloquear_actualizacion_directa_alta_correo();

drop trigger if exists trg_aplicar_evento_alta_correo on alta_correo_evento;
drop function if exists aplicar_evento_alta_correo();

drop trigger if exists trg_preparar_evento_alta_correo on alta_correo_evento;
drop function if exists preparar_evento_alta_correo();

drop index if exists alta_correo_evento_ws;
drop index if exists alta_correo_evento_membership;
drop index if exists alta_correo_evento_bienvenida_unica;
drop table if exists alta_correo_evento;

drop table if exists alta_correo_estado;

commit;
