\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0017_aviso_incidente_administracion.sql. Pack 06
-- (decisión del usuario, 2026-09-28): saludo diario determinístico por hora
-- local del espacio, como mucho una vez por persona y por fecha local.
-- `docs/decisions/0010-correo-verificado-y-google-en-el-producto.md` deja
-- esto explícitamente fuera de su alcance ("unidades de la línea principal,
-- no de esta decisión"): esta migración aplica sobre `main`, no sobre la
-- rama auxiliar de correo y Google.
--
-- Agrega `greeting_state`: una fila por persona (`membership_id`) con la
-- última fecha LOCAL en la que ya se le antepuso el saludo a una respuesta
-- -- nunca por turno ni por chat. `saludo.reclamar_saludo` hace el `upsert`
-- atómico que decide "no saludar de nuevo" en el servidor, nunca con una
-- instrucción al modelo: el pack de referencia
-- (`LEDA-PACK-RECONSTRUCCION-20260925/06-SALUDOS-TONO-E-ICONOGRAFIA.md`)
-- registra que esa instrucción sola no alcanzaba. Sin política especial
-- (regla 1 de `frontera.md`, patrón general): `leda_app` recibe el mismo
-- juego de privilegios que cualquier tabla operativa con alcance de espacio
-- -- a diferencia de `admin_notice` (0017) o una credencial, esta fila no es
-- un secreto ni tiene alcance de plataforma.
--
-- Documentado en detalle en `db/esquema.sql` (misma sección, mismos
-- comentarios) -- esta migración es su aplicación incremental sobre una base
-- existente.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0018 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regprocedure('leda.avisar_incidente_admin(uuid, uuid, text)') is null then
    raise exception '0018 requires 0017_aviso_incidente_administracion.sql';
  end if;
  if to_regclass('leda.greeting_state') is not null then
    raise exception '0018 ya está aplicada.';
  end if;
end $$;

create table greeting_state (
  membership_id       uuid primary key references membership(id) on delete cascade,
  workspace_id        uuid not null references workspace(id) on delete cascade,
  ultima_fecha_local  date not null
);

comment on table greeting_state is
  'Saludo diario (pack 06): última fecha local en la que ya se saludó a esta persona. Una fila por membership, nunca por turno -- reclamada atómicamente por saludo.reclamar_saludo.';

grant all privileges on greeting_state to leda_owner;

alter table greeting_state enable row level security;
alter table greeting_state force row level security;
create policy aislamiento_espacio on greeting_state
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
grant select, insert, update, delete on greeting_state to leda_app;

commit;
