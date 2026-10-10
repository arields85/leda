\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0053_lo_que_retira_la_administracion.sql. La respuesta del bot de administración
-- sale por la cola, y el enlace se emite al mandarla (la corrección chica de la Fase C; el
-- `PENDIENTE` de la porción 5 de la C-3; `odd/tasks/fase-c.md`).
--
-- Hasta acá la respuesta al pedido `/enlace` salía directo, sin cola: la cola del bot de
-- administración (`admin_notice`) guarda el texto, y el token en claro no puede quedar en la base
-- (ADR 0019, 7a). Ahora, como el enlace de una persona del equipo (`message_outbox_enlace`):
--
-- 1. `admin_notice` lleva también las respuestas del bot de administración (`es_respuesta`), que
--    no son incidentes: `incident_id` admite nulo, y una fila es exactamente una de las dos
--    cosas (`admin_notice_incidente_o_respuesta`).
-- 2. `admin_notice_enlace`: la marca de que esa respuesta lleva el enlace de esta tarea de este
--    espacio para este administrador de plataforma. El despachador lo emite al mandarla
--    (`pagina_de_tarea.emitir_para_administrador`, que revalida el rol), dentro del punto de
--    retorno del envío: la base guarda sólo su hash (`acceso_tarea`), y un envío que falla no
--    deja ningún acceso. Sólo se agrega.
--
-- Aislamiento: como `admin_notice`, sin política por espacio y sin ningún privilegio para
-- `leda_app` (ni para `leda_gateway`): la escribe y la despacha la conexión administrativa
-- (`leda_admin`). La tarea de la marca es del espacio de la marca (clave compuesta, como
-- `message_outbox_enlace`). Excepción declarada en `tests/garantias/test_aislamiento.py`.
--
-- Se deshace con `db/rollbacks/0054_la_respuesta_del_bot_de_administracion.sql`, que se niega si
-- hay alguna respuesta en la cola (la vuelta atrás volvería obligatorio `incident_id`).
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0054 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0053 está aplicada y la 0054 no.
do $$ begin
  if not exists (select 1 from information_schema.columns
                  where table_schema = 'leda' and table_name = 'archivo'
                    and column_name = 'contenido_retirado_en') then
    raise exception '0054 preflight failed: falta la 0053';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'admin_notice'
                and column_name = 'es_respuesta') then
    raise exception '0054 ya está aplicada.';
  end if;
end $$;

-- 1. Una fila de la cola es un incidente o una respuesta.
alter table admin_notice alter column incident_id drop not null;
alter table admin_notice add column es_respuesta boolean not null default false;
alter table admin_notice add constraint admin_notice_incidente_o_respuesta
  check ((incident_id is null) = es_respuesta);
comment on column admin_notice.es_respuesta is
  'La respuesta del bot de administración a un pedido de un administrador (migración 0054), no un aviso de incidente: sin incident_id. Si lleva el enlace de una tarea, su marca está en admin_notice_enlace y el despachador lo emite al mandarla.';

-- 2. La marca del enlace.
create table admin_notice_enlace (
  id                 uuid primary key default gen_random_uuid(),
  admin_notice_id    uuid not null references admin_notice(id) on delete cascade,
  workspace_id       uuid not null references workspace(id) on delete cascade,
  task_id            uuid not null,
  admin_app_user_id  uuid not null references app_user(id) on delete cascade,
  constraint admin_notice_enlace_task
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade,
  constraint admin_notice_enlace_uno_por_aviso unique (admin_notice_id)
);

comment on table admin_notice_enlace is
  'Migración 0054 (ADR 0019, 7a y 7b): la respuesta del bot de administración lleva el enlace de esta tarea para este administrador de plataforma. El despachador lo emite al mandar; la base guarda sólo su hash (acceso_tarea). Sin privilegio para leda_app. Sólo se agrega.';

revoke all on admin_notice_enlace from public;
grant all on admin_notice_enlace to leda_admin;

commit;
