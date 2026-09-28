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

drop index if exists aviso_administrativo_respuesta_pendientes;
drop index if exists aviso_administrativo_respuesta_dedupe;
drop table if exists aviso_administrativo_respuesta;

drop index if exists aviso_administrativo_entrega_pendientes;
drop index if exists aviso_administrativo_entrega_unica;
drop table if exists aviso_administrativo_entrega;

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
