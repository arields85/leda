\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0016_hora_de_escritura_como_regla_del_esquema.sql. T28
-- (decisión del usuario, 2026-09-28): Constitución §10, "Los incidentes se
-- registran sanitizados y se avisan al administrador de plataforma por su
-- canal." Hasta acá sólo se avisaba a la persona afectada
-- (`gateway.NOTICIA_NEUTRA_INCIDENTE`); quien administra la plataforma tenía
-- que correr `python -m prisma incidentes <slug>` para enterarse.
--
-- Corrección del usuario sobre el alcance original de esta unidad (mismo
-- día): el aviso SÍ tiene que incluir qué lo disparó -- el texto del
-- mensaje de la persona, o la acción tocada -- porque la Constitución §2 ya
-- le da al administrador acceso a las conversaciones privadas, y §12 dice
-- que ESE acceso se audita, no que haya que ocultárselo acá. §10 exige un
-- incidente sanitizado (sin secretos), no un aviso sin disparador.
--
-- Agrega:
--   - `incident.notificado_admin_en`, igual que `notificado_en` pero para el
--     aviso a la administración -- nunca queda puesto si nadie fue avisado.
--   - `admin_notice`, la cola de salida del bot de administración. Aparte de
--     `message_outbox` a propósito: esa cola es por espacio y un
--     administrador no tiene por qué ser integrante de ningún equipo.
--   - `avisar_incidente_admin(uuid, uuid, text)`, `security definer` como
--     `emitir_acceso_tablero`/`resolver_acceso_tablero`: hace el fan-out a
--     cada administrador alcanzable (que ya le escribió al bot de
--     administración alguna vez) porque necesita leer `platform_role` y
--     `audit_log`, sin concesión de lectura a `prisma_app`. El texto del
--     aviso (con el disparador) lo arma Python antes de llamar -- eso no
--     necesita elevación, `prisma_app` ya puede leer `inbound_message`,
--     `pending_action` y la vista `integrante`.
--
-- Todas las piezas nuevas están documentadas en detalle en `db/esquema.sql`
-- (misma sección, mismos comentarios) -- esta migración es su aplicación
-- incremental sobre una base existente.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0017 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if (select column_default from information_schema.columns
       where table_schema = 'prisma' and table_name = 'task_state_event'
         and column_name = 'at') is distinct from 'clock_timestamp()' then
    raise exception '0017 requires 0016_hora_de_escritura_como_regla_del_esquema.sql';
  end if;
  if exists (
      select 1 from information_schema.columns
       where table_schema = 'prisma' and table_name = 'incident'
         and column_name = 'notificado_admin_en') then
    raise exception '0017 ya está aplicada.';
  end if;
end $$;

alter table incident add column notificado_admin_en timestamptz;

comment on column incident.notificado_admin_en is
  'Aviso a la administración de plataforma (Constitución §10). Igual que notificado_en para la persona afectada, nunca queda puesto si nadie fue avisado de verdad. Lo llena incidentes.registrar_incidente, nunca a mano.';

create table admin_notice (
  id                       uuid primary key default gen_random_uuid(),
  incident_id              uuid not null,
  workspace_id             uuid references workspace(id) on delete set null,
  destinatario_app_user_id uuid not null references app_user(id) on delete cascade,
  chat_id                  bigint not null,
  cuerpo                   text not null,
  estado                   estado_salida not null default 'listo',
  programado_para          timestamptz not null default now(),
  enviado_en               timestamptz,
  telegram_message_id      bigint,
  dedupe_key               text not null unique,
  intentos                 integer not null default 0,
  ultimo_error             text
);

comment on table admin_notice is
  'Cola de salida del bot de administración: un aviso por incidente y por administrador de plataforma alcanzable. Sin política de aislamiento por espacio -- no tiene un único espacio dueño -- y sin concesión a prisma_app: sólo la escribe avisar_incidente_admin() (security definer) y sólo la despacha prisma_admin (despachador.despachar_avisos_admin).';

-- `db/esquema.sql` cubre esto con la concesión general sobre "all tables in
-- schema prisma" porque esa sentencia corre DESPUÉS de crear esta tabla, en
-- una instalación limpia. Acá, sobre una base existente, esa concesión ya
-- corrió hace tiempo y no alcanza a una tabla nueva -- hay que repetirla
-- para esta tabla sola.
grant all privileges on admin_notice to prisma_owner;
grant all on admin_notice to prisma_admin;

create function avisar_incidente_admin(
    p_incident_id uuid, p_workspace_id uuid, p_cuerpo text)
returns table(app_user_id uuid)
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare v_admin record;
begin
  for v_admin in
    select distinct on (p.app_user_id) p.app_user_id as app_user_id,
           nullif(a.detalle->>'chat_id', '')::bigint as chat_id
      from platform_role p
      join audit_log a on a.actor_app_user_id = p.app_user_id
                       and a.accion = 'mensaje_admin'
     where p.rol = 'administrador'
     order by p.app_user_id, a.at desc
  loop
    if v_admin.chat_id is not null then
      insert into admin_notice
        (incident_id, workspace_id, destinatario_app_user_id, chat_id, cuerpo,
         dedupe_key)
      values
        (p_incident_id, p_workspace_id, v_admin.app_user_id, v_admin.chat_id,
         p_cuerpo,
         'aviso-admin:' || p_incident_id::text || ':' || v_admin.app_user_id::text)
      on conflict (dedupe_key) do nothing;
      if found then
        app_user_id := v_admin.app_user_id;
        return next;
      end if;
    end if;
  end loop;
end $$;

alter function avisar_incidente_admin(uuid, uuid, text)
  owner to prisma_owner;

revoke execute on function avisar_incidente_admin(uuid, uuid, text)
  from public;
grant execute on function avisar_incidente_admin(uuid, uuid, text)
  to prisma_app, prisma_admin;

commit;
