\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0101_credencial_google.sql.
--
-- Removes the per-workspace Google credential schema entirely: the encrypted
-- payload, its events and their projection. Any authorized credential is
-- lost, which is the safe direction for a rollback of a credential store --
-- same reasoning as 0100's rollback of the verification tokens: the
-- administrator authorizes again once the schema is back.
--
-- With `google.habilitado` apagada (el estado por defecto), nada de esto se
-- usa, así que este rollback no le devuelve nada a `main`: sólo saca el
-- esquema que la rama auxiliar agregó.
begin;
set search_path = prisma, public;

-- Las tablas primero: el borrado se lleva sus disparadores, políticas e
-- índices, y las funciones de disparador quedan sin dependientes.
drop table if exists credencial_google_evento;
drop table if exists credencial_google_estado;
drop table if exists credencial_google;

drop function if exists reemplazar_token_google(uuid, text, text);
drop function if exists credenciales_google_cifradas();
drop function if exists revocar_credencial_google(uuid, text);
drop function if exists guardar_credencial_google(uuid, text, text, text[]);
drop function if exists marcar_reautorizacion_google(text);
drop function if exists estado_credencial_google();
drop function if exists leer_credencial_google();

drop function if exists bloquear_actualizacion_directa_credencial_google();
drop function if exists aplicar_evento_credencial_google();
drop function if exists preparar_evento_credencial_google();

commit;
