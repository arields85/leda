-- =========================================================================
-- Leda — esquema de base de datos
-- PostgreSQL 18 o posterior
--
-- Principios que el esquema hace cumplir, no sólo documenta:
--
--   1. Todo cuelga de un espacio de trabajo y está aislado por RLS.
--   2. El estado de una tarea es una proyección de sus eventos. No se puede
--      escribir directamente: se inserta un evento y un disparador lo aplica.
--   3. Las condiciones de cierre son funciones deterministas. El modelo de
--      lenguaje propone; la base decide.
--   4. La autoridad son filas, no prosa.
--   5. Nada sale a Telegram sin pasar por la cola, con clave de deduplicación.
-- =========================================================================

-- gen_random_uuid() es nativo desde PostgreSQL 13; no hace falta pgcrypto.

create schema if not exists leda;
set search_path = leda, public;

-- =========================================================================
-- Tipos
-- =========================================================================

create type rol_plataforma as enum ('administrador', 'operador');

create type tipo_objetivo as enum ('estrategico', 'hito', 'operativo');

create type estado_objetivo as enum (
  'propuesto', 'activo', 'completo_pendiente_aprobacion',
  'terminado', 'suspendido', 'cancelado');

create type estado_tarea as enum (
  'propuesta', 'pendiente_aprobacion', 'asignada', 'en_curso',
  'bloqueada', 'en_revision', 'terminada', 'cancelada');

create type tipo_dependencia as enum ('bloqueante', 'informativa');

create type tipo_actor as enum ('persona', 'leda', 'sistema');

create type tipo_mensaje as enum (
  'informativo', 'normal', 'seguimiento', 'prioritario', 'urgente');

create type estado_salida as enum (
  'pendiente', 'esperando_confirmacion', 'listo',
  'enviado', 'fallido', 'descartado');

create type estado_pendiente as enum (
  'esperando', 'resuelta', 'cancelada', 'vencida');

create type decision_aprobacion as enum ('aprobado', 'rechazado');

-- =========================================================================
-- Plataforma
--
-- Eje de rol global. Independiente de los espacios: ser administrador no
-- otorga ningún permiso dentro de un equipo.
-- =========================================================================

create table app_user (
  id                uuid primary key default gen_random_uuid(),
  telegram_user_id  bigint unique,
  nombre            text not null,
  creado_en         timestamptz not null default now()
);

create table platform_role (
  app_user_id   uuid not null references app_user(id) on delete cascade,
  rol           rol_plataforma not null,
  otorgado_por  uuid references app_user(id),
  otorgado_en   timestamptz not null default now(),
  primary key (app_user_id, rol)
);

comment on table platform_role is
  'Eje de plataforma. Debe haber al menos dos administradores: uno solo es un punto único de falla.';

-- =========================================================================
-- Espacios de trabajo
-- =========================================================================

create table workspace (
  id             uuid primary key default gen_random_uuid(),
  slug           text not null unique,
  nombre         text not null,
  zona_horaria   text not null default 'America/Argentina/Buenos_Aires',
  bot_token_ref  text,               -- referencia al secreto, nunca el token
  grupo_chat_id  bigint,
  activo         boolean not null default false,
  creado_en      timestamptz not null default now()
);

-- Cada importación de un pack deja una versión. El hash permite saber con qué
-- configuración exacta se tomó cada decisión registrada.
create table workspace_version (
  id            uuid primary key default gen_random_uuid(),
  workspace_id  uuid not null references workspace(id) on delete cascade,
  version       integer not null,
  pack_hash     text not null,
  importado_en  timestamptz not null default now(),
  importado_por uuid references app_user(id),
  aprobado_por  uuid references app_user(id),
  unique (workspace_id, version)
);

create table area (
  id            uuid primary key default gen_random_uuid(),
  workspace_id  uuid not null references workspace(id) on delete cascade,
  slug          text not null,
  nombre        text not null,
  -- ADR 0019, decisión 7b (migración 0036): el referente técnico del área, un dato del
  -- espacio y no el nombre de un rol del pack. Su restricción, después de `membership`.
  referente_membership_id uuid,
  unique (workspace_id, slug)
);

create table rol (
  id               uuid primary key default gen_random_uuid(),
  workspace_id     uuid not null references workspace(id) on delete cascade,
  slug             text not null,
  nombre           text not null,
  autoridad_final  boolean not null default false,
  unique (workspace_id, slug)
);

-- El núcleo exige exactamente una autoridad final por espacio.
create unique index rol_una_autoridad_final
  on rol (workspace_id) where autoridad_final;

create table membership (
  id            uuid primary key default gen_random_uuid(),
  workspace_id  uuid not null references workspace(id) on delete cascade,
  app_user_id   uuid not null references app_user(id) on delete cascade,
  area_id       uuid not null references area(id),
  rol_id        uuid not null references rol(id),
  -- Quién revisa el trabajo de esta persona. La aprobación sube un nivel:
  -- a un integrante lo aprueba su referente, a un referente lo aprueba
  -- Dirección. Null sólo en la raíz de la cadena.
  aprobador_membership_id uuid references membership(id),
  horario       jsonb,
  activo        boolean not null default true,
  unique (workspace_id, app_user_id),
  constraint membership_workspace_id_unique unique (workspace_id, id),
  check (aprobador_membership_id is null or aprobador_membership_id <> id)
);

comment on table membership is
  'Eje de espacio. Una persona puede pertenecer a varios espacios con roles distintos.';

comment on column membership.aprobador_membership_id is
  'La cadena de aprobación es por persona, no por área: Marcos aprueba a Nahuel aunque estén en áreas distintas.';

alter table area add constraint area_referente
  foreign key (workspace_id, referente_membership_id) references membership(workspace_id, id)
  on delete set null (referente_membership_id);

comment on column area.referente_membership_id is
  'ADR 0019, decisión 7b: el referente técnico del área, un dato del espacio (no el nombre de un rol del pack). Ve las páginas de las tareas de su área.';

create table absence (
  id             uuid primary key default gen_random_uuid(),
  workspace_id   uuid not null references workspace(id) on delete cascade,
  membership_id  uuid not null references membership(id) on delete cascade,
  desde          date not null,
  hasta          date,                -- null = indefinida, dispara alerta
  motivo         text
);

create index absence_ws on absence (workspace_id, membership_id);

-- Saludo diario (pack 06; `saludo.py`). Una fila por persona -- nunca por
-- turno ni por chat -- con la última fecha LOCAL (zona del espacio,
-- `workspace.zona_horaria`) en la que ya se le antepuso el saludo a una
-- respuesta. "No saludar de nuevo" es la reserva de esta tabla, nunca una
-- instrucción al modelo (el pack de referencia registra que esa instrucción
-- sola no alcanzaba). `reclamar_saludo` (`saludo.py`) hace el `upsert`
-- atómico; la bienvenida de incorporación (`onboarding.bienvenida`)
-- reclama esta misma fila sin pasar por el saludo por hora -- cuenta como el
-- saludo de esa fecha (pack 06 §3).
create table greeting_state (
  membership_id       uuid primary key references membership(id) on delete cascade,
  workspace_id        uuid not null references workspace(id) on delete cascade,
  ultima_fecha_local  date not null
);

comment on table greeting_state is
  'Saludo diario (pack 06): última fecha local en la que ya se saludó a esta persona. Una fila por membership, nunca por turno -- reclamada atómicamente por saludo.reclamar_saludo.';

-- Telegram no permite que un bot inicie una conversación privada con alguien
-- que nunca le escribió. Cada persona tiene que abrir su enlace una vez.
--
-- Los enlaces se entregan uno a uno, nunca publicados en el grupo: un token
-- a la vista permite que cualquiera reclame la identidad de otro.
create table activation_token (
  id             uuid primary key default gen_random_uuid(),
  workspace_id   uuid not null references workspace(id) on delete cascade,
  membership_id  uuid not null references membership(id) on delete cascade,
  token          text not null unique,
  creado_en      timestamptz not null default now(),
  creado_por     uuid references app_user(id),
  expira_en      timestamptz not null,
  usado_en       timestamptz,
  usado_por      bigint                          -- telegram_user_id que lo canjeó
);

-- Un solo enlace vigente por persona: si se regenera, el anterior deja de servir.
create unique index activation_token_vigente
  on activation_token (membership_id) where usado_en is null;

create table work_calendar (
  workspace_id  uuid primary key references workspace(id) on delete cascade,
  dias          text[] not null,
  hora_inicio   time not null,
  hora_fin      time not null
);

create table holiday (
  workspace_id  uuid not null references workspace(id) on delete cascade,
  fecha         date not null,
  nombre        text,
  primary key (workspace_id, fecha)
);

-- =========================================================================
-- Política — la autoridad como datos
--
-- Reemplaza la matriz de aprobación en prosa del documento original.
-- =========================================================================

create table permission (
  workspace_id  uuid not null references workspace(id) on delete cascade,
  rol_id        uuid not null references rol(id) on delete cascade,
  accion        text not null,
  alcance       text not null default 'area',   -- area | espacio
  primary key (workspace_id, rol_id, accion)
);

create table approval_policy (
  id                        uuid primary key default gen_random_uuid(),
  workspace_id              uuid not null references workspace(id) on delete cascade,
  sujeto                    text not null,        -- tarea | objetivo_operativo | hito | plan
  area_id                   uuid references area(id),
  autoaprobacion_declarada  boolean not null default false,
  motivo                    text,
  unique (workspace_id, sujeto, area_id)
);

comment on column approval_policy.autoaprobacion_declarada is
  'Un área sin requisitos debe declarar la autoaprobación a conciencia. La omisión no puede pasar por decisión.';

create table approval_requirement (
  id                  uuid primary key default gen_random_uuid(),
  approval_policy_id  uuid not null references approval_policy(id) on delete cascade,
  tipo                text not null,   -- rol | area | cada_area_participante
  rol_id              uuid references rol(id),
  area_id             uuid references area(id),
  check (
    (tipo = 'rol'  and rol_id is not null) or
    (tipo = 'area' and area_id is not null) or
    (tipo = 'cada_area_participante')
  )
);

create table escalation_route (
  id                uuid primary key default gen_random_uuid(),
  workspace_id      uuid not null references workspace(id) on delete cascade,
  disparador        text not null,
  area_id           uuid references area(id),
  destino_rol_id    uuid references rol(id),
  destino_membership_id uuid references membership(id),
  orden             integer not null default 1,
  check (destino_rol_id is not null or destino_membership_id is not null)
);

create table glossary_term (
  id                    uuid primary key default gen_random_uuid(),
  workspace_id          uuid not null references workspace(id) on delete cascade,
  termino               text not null,
  definicion            text,
  variantes_incorrectas text[] not null default '{}',
  fuera_de_alcance      boolean not null default false,
  unique (workspace_id, termino)
);

create table message_template (
  workspace_id  uuid not null references workspace(id) on delete cascade,
  clave         text not null,
  cuerpo        text not null,
  variables     text[] not null default '{}',
  primary key (workspace_id, clave)
);

create table persona_config (
  workspace_id    uuid primary key references workspace(id) on delete cascade,
  nombre_visible  text not null default 'Leda',
  registro        text not null default 'vos',
  formalidad      text not null default 'profesional_cordial',
  longitud        text not null default 'breve',
  emojis          boolean not null default false,
  presentacion    text
);

-- Los nombres de los niveles de objetivo del pack (migración 0068; mecánica §1): un objeto con
-- `estrategico`, `hito` u `operativo` y un nombre de 1 a 60 caracteres cada uno.
create or replace function niveles_validos(p_niveles jsonb) returns boolean as $$
  select jsonb_typeof(p_niveles) = 'object'
     and not exists (
       select 1 from jsonb_each(p_niveles) n
        where n.key not in ('estrategico', 'hito', 'operativo')
           or jsonb_typeof(n.value) <> 'string'
           or btrim(n.value #>> '{}') = ''
           or char_length(n.value #>> '{}') > 60);
$$ language sql immutable;

-- Umbrales y límites del pack: re-aprobación, tope de mensajes, días de
-- escalamiento. Clave-valor para no migrar el esquema cada vez que aparece
-- un parámetro nuevo.
create table workspace_setting (
  workspace_id  uuid not null references workspace(id) on delete cascade,
  clave         text not null,
  valor         jsonb not null,
  primary key (workspace_id, clave),
  -- El Motor (migración 0031; ADR 0018, 9b): cuántos días hábiles antes del
  -- vencimiento sale el aviso previo. Un entero de al menos 1 (mecánica §9); el
  -- valor de cada espacio se carga aparte (en CoreWork, 3).
  constraint workspace_setting_aviso_previo check (
    case
      when clave <> 'aviso_previo_dias_habiles' then true
      when jsonb_typeof(valor) <> 'number' then false
      else (valor #>> '{}')::numeric >= 1 and (valor #>> '{}')::numeric % 1 = 0
    end),
  -- ADR 0019, decisión 2 (migración 0033): el tamaño máximo de un archivo en el
  -- espacio, en MB. Un espacio puede bajar el del producto (60 MB), nunca subirlo.
  constraint workspace_setting_archivo_tamano_maximo check (
    case
      when clave <> 'archivo_tamano_maximo_mb' then true
      when jsonb_typeof(valor) <> 'number' then false
      else (valor #>> '{}')::numeric between 1 and 60
           and (valor #>> '{}')::numeric % 1 = 0
    end),
  -- Decisión 8 del usuario, 2026-10-12 (migración 0060): el usuario público del bot del equipo
  -- (`telegram.bot_usuario` del pack, sin "@"), con el que la web abre el chat con Leda. Va en
  -- una dirección: sólo un usuario de Telegram válido.
  constraint workspace_setting_bot_usuario check (
    case
      when clave <> 'bot_usuario' then true
      when jsonb_typeof(valor) <> 'string' then false
      else (valor #>> '{}') ~ '^[A-Za-z][A-Za-z0-9_]{4,31}$'
    end),
  -- ADR 0023, punto 11 (migración 0068): los nombres de los niveles de objetivo del pack
  -- (`niveles`), que guarda el importador y muestra la web al crear un objetivo.
  constraint workspace_setting_niveles check (
    case when clave <> 'niveles' then true else niveles_validos(valor) end)
);

-- ADR 0019, decisión 5 (migración 0034): por cada tipo de la política, las clases
-- de evidencia que acepta y cómo se dice en palabras de todos los días.
create or replace function tipos_de_evidencia_validos(p_tipos jsonb) returns boolean as $$
  select jsonb_typeof(p_tipos) = 'object'
     and not exists (
       select 1 from jsonb_each(p_tipos) t
        where jsonb_typeof(t.value) <> 'object'
           or jsonb_typeof(t.value -> 'clases') <> 'array'
           or jsonb_array_length(t.value -> 'clases') = 0
           or exists (select 1 from jsonb_array_elements(t.value -> 'clases') c
                       where jsonb_typeof(c) <> 'string'
                          or c #>> '{}' not in ('texto', 'imagen', 'archivo', 'enlace'))
           or jsonb_typeof(t.value -> 'en_palabras') <> 'string'
           or btrim(t.value ->> 'en_palabras') = '');
$$ language sql immutable;

-- Policy imported from evidencia.por_area. An empty array is an explicit
-- no-evidence policy; absence of a row means that policy is unresolved.
-- `tipos` (migración 0034) son las clases que acepta cada tipo, del pack
-- (`evidencia.tipos`): un tipo sin clases no lo cubre nada (falla cerrado).
create table task_evidence_policy (
  workspace_id        uuid not null references workspace(id) on delete cascade,
  area_id             uuid not null references area(id) on delete cascade,
  evidencia_requerida text[] not null,
  version             integer not null default 1 check (version > 0),
  actualizado_en      timestamptz not null default now(),
  tipos               jsonb not null default '{}'::jsonb,
  primary key (workspace_id, area_id),
  constraint task_evidence_policy_tipos check (tipos_de_evidencia_validos(tipos))
);

comment on column task_evidence_policy.tipos is
  'ADR 0019, decisión 5: por cada tipo de la política, las clases de evidencia que acepta (texto, imagen, archivo, enlace) y cómo se dice en palabras de todos los días. Dato del pack; cambia la versión de la política.';

create table cadence_job (
  id              uuid primary key default gen_random_uuid(),
  workspace_id    uuid not null references workspace(id) on delete cascade,
  nombre          text not null,
  cron            text not null,
  audiencia       text not null,      -- grupo | privado_cada_integrante
  plantilla_clave text,
  activo          boolean not null default true,
  ultima_corrida  timestamptz,
  unique (workspace_id, nombre)
);

comment on table cadence_job is
  'El reloj de cadencia. Cambiar un horario es actualizar una fila, no desplegar código.';

-- =========================================================================
-- Trabajo
-- =========================================================================

create table objective (
  id                      uuid primary key default gen_random_uuid(),
  workspace_id            uuid not null references workspace(id) on delete cascade,
  parent_id               uuid,
  tipo                    tipo_objetivo not null,
  titulo                  text not null,
  descripcion             text,
  referente_membership_id uuid,
  estado                  estado_objetivo not null default 'propuesto',
  fecha_objetivo          date,
  creado_en               timestamptz not null default now(),
  actualizado_en          timestamptz not null default now(),
  -- Migración 0068 (ADR 0023, decisión 1): el padre y el referente, del mismo espacio.
  constraint objective_workspace_id_unique unique (workspace_id, id),
  constraint objective_padre_del_espacio
    foreign key (workspace_id, parent_id) references objective(workspace_id, id)
    on delete cascade,
  constraint objective_referente_del_espacio
    foreign key (workspace_id, referente_membership_id) references membership(workspace_id, id)
);

create index objective_ws on objective (workspace_id, estado);
create index objective_parent on objective (parent_id);

create function telegram_utf16_units(p_text text) returns integer
language plpgsql immutable strict parallel safe as $$
declare
  units integer := 0;
  i integer;
begin
  for i in 1..char_length(p_text) loop
    units := units + case when ascii(substr(p_text, i, 1)) > 65535 then 2 else 1 end;
  end loop;
  return units;
end $$;

-- A draft may be incomplete and therefore has no operational effects. The
-- snapshots are the values shown in the preview and revalidated on commit.
create table task_draft (
  id                        uuid primary key default gen_random_uuid(),
  workspace_id              uuid not null references workspace(id) on delete cascade,
  creado_por_membership_id  uuid not null references membership(id),
  objective_id              uuid references objective(id),
  objective_snapshot        jsonb,
  titulo                    text,
  descripcion               text,
  area_id                   uuid references area(id),
  responsable_membership_id uuid references membership(id),
  fecha_objetivo            timestamptz,
  criterio_aceptacion       text,
  evidencia_requerida       text[],
  evidencia_policy_version  integer,
  version                   integer not null default 1 check (version > 0),
  estado                    text not null default 'open'
                            check (estado in ('open', 'cancelled', 'converted')),
  converted_task_id         uuid,
  creado_en                 timestamptz not null default now(),
  actualizado_en            timestamptz not null default now(),
  constraint task_draft_workspace_id_unique unique (workspace_id, id),
  constraint task_draft_creator_workspace
    foreign key (workspace_id, creado_por_membership_id)
    references membership(workspace_id, id),
  constraint task_draft_responsible_workspace
    foreign key (workspace_id, responsable_membership_id)
    references membership(workspace_id, id),
  constraint task_draft_title_payload
    check (titulo is null or telegram_utf16_units(titulo) <= 200),
  constraint task_draft_description_payload
    check (descripcion is null or telegram_utf16_units(descripcion) <= 800),
  constraint task_draft_acceptance_payload
    check (criterio_aceptacion is null
           or telegram_utf16_units(criterio_aceptacion) <= 500),
  check ((evidencia_requerida is null) =
         (evidencia_policy_version is null))
);

create index task_draft_ws on task_draft (workspace_id, creado_en desc);

create table task (
  id                        uuid primary key default gen_random_uuid(),
  workspace_id              uuid not null references workspace(id) on delete cascade,
  objective_id              uuid not null references objective(id) on delete cascade,
  parent_task_id            uuid references task(id) on delete cascade,
  titulo                    text not null,
  descripcion               text,
  area_id                   uuid not null references area(id),
  responsable_membership_id uuid references membership(id),
  prioridad                 integer,
  estado                    estado_tarea not null default 'propuesta',
  fecha_objetivo            timestamptz,
  criterio_aceptacion       text,
  evidencia_requerida       text[] not null default '{}',
  evidencia_policy_version  integer,
  source_draft_id           uuid unique references task_draft(id),
  creado_en                 timestamptz not null default now(),
  actualizado_en            timestamptz not null default now(),
  -- Migraciones 0045 y 0046 (C-7, delegar): de quién era antes de su primer pase.
  era_de_membership_id      uuid,
  -- Migración 0030: para las claves foráneas con el espacio del motor.
  constraint task_workspace_id_unique unique (workspace_id, id)
);

alter table task_draft
  add constraint task_draft_converted_task
  foreign key (converted_task_id) references task(id);

create index task_ws on task (workspace_id, estado);
create index task_responsable on task (responsable_membership_id, estado);
create index task_vencimiento on task (fecha_objetivo)
  where estado in ('asignada', 'en_curso', 'bloqueada');

-- Registro append-only. Es la verdad; task.estado es su proyección.
-- workspace_id no lo aporta quien inserta: lo deriva de la fila padre el
-- disparador derivar_espacio_evento_tarea(), más abajo.
create table task_state_event (
  id               uuid primary key default gen_random_uuid(),
  workspace_id     uuid not null references workspace(id) on delete cascade,
  task_id          uuid not null references task(id) on delete cascade,
  estado_anterior  estado_tarea,
  estado_nuevo     estado_tarea not null,
  actor_kind       tipo_actor not null,
  actor_app_user_id uuid references app_user(id),
  motivo           text,
  -- T6j (`odd/tasks/leda-orienta.md`): `clock_timestamp()`, no `now()` --
  -- `now()` es la hora de INICIO de la transacción, y `motivo_no_cierra_tarea`,
  -- `evidencia_pendiente` y `estado_previo_a_bloqueo`/`estado_previo_a_revision`
  -- ordenan o comparan por `at` entre esta tabla, `evidence` y `approval`.
  at               timestamptz not null default clock_timestamp()
);

create index task_state_event_task on task_state_event (task_id, at desc);
create index task_state_event_ws on task_state_event (workspace_id, at desc);

create table objective_state_event (
  id                uuid primary key default gen_random_uuid(),
  workspace_id      uuid not null references workspace(id) on delete cascade,
  objective_id      uuid not null references objective(id) on delete cascade,
  estado_anterior   estado_objetivo,
  estado_nuevo      estado_objetivo not null,
  actor_kind        tipo_actor not null,
  actor_app_user_id uuid references app_user(id),
  motivo            text,
  at                timestamptz not null default now()
);

create index objective_state_event_ws
  on objective_state_event (workspace_id, at desc);

create table dependency (
  id               uuid primary key default gen_random_uuid(),
  workspace_id     uuid not null references workspace(id) on delete cascade,
  origen_task_id   uuid not null references task(id) on delete cascade,
  destino_task_id  uuid not null references task(id) on delete cascade,
  tipo             tipo_dependencia not null default 'bloqueante',
  unique (origen_task_id, destino_task_id),
  check (origen_task_id <> destino_task_id)
);

create table blocker (
  id            uuid primary key default gen_random_uuid(),
  workspace_id  uuid not null references workspace(id) on delete cascade,
  task_id       uuid not null references task(id) on delete cascade,
  causa         text not null,
  impacto       text,
  abierto_en    timestamptz not null default now(),
  abierto_por   uuid references membership(id),
  resuelto_en   timestamptz,
  resolucion    text,
  escalado_a    uuid references membership(id),
  escalado_en   timestamptz,
  -- Migración 0031: para la clave foránea con el espacio de `blocker_unblocker`.
  constraint blocker_workspace_id_unique unique (workspace_id, id)
);

create index blocker_abiertos on blocker (workspace_id, abierto_en)
  where resuelto_en is null;

create table evidence (
  id             uuid primary key default gen_random_uuid(),
  workspace_id   uuid not null references workspace(id) on delete cascade,
  task_id        uuid not null references task(id) on delete cascade,
  tipo           text not null,
  uri            text,
  drive_file_id  text,
  sha256         text,
  entregado_por  uuid references membership(id),
  -- T6j: mismo motivo que `task_state_event.at`, más arriba.
  at             timestamptz not null default clock_timestamp(),
  -- ADR 0019, decisión 5 (migración 0034): la clase de la pieza, que fija el
  -- código por el contenido; el texto, si es texto; el archivo (la clave foránea
  -- con el espacio va después de `archivo`), si es una imagen o un archivo; y los
  -- tipos de la política que cubre, como los vio la persona al confirmar.
  clase          text not null,
  texto          text,
  archivo_id     uuid,
  cubre          text[] not null default '{}',
  -- C-3d, D3 (migración 0038): los puntos del criterio de aceptación que la persona confirmó
  -- que describe este texto, tal cual el criterio los decía al entregar. Sólo un texto
  -- describe el criterio; las filas de antes de la 0038, `{}`.
  describe_del_criterio text[] not null default '{}',
  -- D8 (migración 0039): si el texto es un ejemplo que Leda propuso para lo que faltaba del
  -- criterio y la persona aceptó tal cual: vale como lo que describe, pero no lo escribió ella.
  -- Sólo un texto; las filas de antes de la 0039, `false`.
  es_ejemplo_aceptado boolean not null default false,
  -- Migración 0056: la entrega a la que pertenece la pieza, por el id de la primera pieza del
  -- acto (ella misma, si es la primera o la única), de la misma tarea. Un dato de la fila, que
  -- viaja con un respaldo (la transacción que la escribió, no). Las filas de antes, nulas.
  de_la_entrega  uuid,
  constraint evidence_workspace_id_unique unique (workspace_id, id),
  constraint evidence_tarea_id_unique unique (workspace_id, task_id, id),
  constraint evidence_de_la_entrega
    foreign key (workspace_id, task_id, de_la_entrega)
    references evidence(workspace_id, task_id, id),
  constraint evidence_task_workspace
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade,
  constraint evidence_clase check (clase in ('texto', 'imagen', 'archivo', 'enlace')),
  constraint evidence_clase_y_contenido check (
    case clase
      when 'texto' then archivo_id is null
      when 'enlace' then archivo_id is null and uri is not null
      else archivo_id is not null
    end),
  constraint evidence_describe_solo_un_texto
    check (clase = 'texto' or describe_del_criterio = '{}'),
  constraint evidence_ejemplo_solo_un_texto
    check (clase = 'texto' or not es_ejemplo_aceptado)
);

comment on column evidence.clase is
  'ADR 0019, decisión 5: texto, imagen, archivo o enlace. La fija el código por el contenido, nunca la IA; la de un archivo la comprueba un disparador contra archivo.clase.';
comment on column evidence.cubre is
  'ADR 0019, decisión 5: los tipos de la política que cubre esta pieza, como los vio la persona en la vista previa de la entrega. Un texto puede cubrir varios.';
comment on column evidence.tipo is
  'Legado: en las filas nuevas es igual a la clase. Los tipos de la política que cubre una pieza están en cubre.';
comment on column evidence.de_la_entrega is
  'Migración 0056: la entrega a la que pertenece esta pieza, por el id de la primera pieza del acto (ella misma, si es la primera o la única), de la misma tarea. La escribe la cocina al entregar; viaja con un respaldo, a diferencia de la transacción que la escribió. Nula en las filas de antes de la 0056: la pieza cuenta como su propio acto.';

create table approval (
  id                     uuid primary key default gen_random_uuid(),
  workspace_id           uuid not null references workspace(id) on delete cascade,
  sujeto_tipo            text not null,      -- tarea | objetivo | plan
  sujeto_id              uuid not null,
  aprobador_membership_id uuid not null references membership(id),
  decision               decision_aprobacion not null,
  comentario             text,
  pack_hash              text,
  nucleo_hash            text,
  -- T6j: mismo motivo que `task_state_event.at`, más arriba.
  at                     timestamptz not null default clock_timestamp()
);

create index approval_sujeto on approval (sujeto_tipo, sujeto_id);

-- Quién le debe una respuesta a Leda. Sin esta tabla la escalera de
-- recordatorios sería una adivinanza del modelo.
create table pending_reply (
  id             uuid primary key default gen_random_uuid(),
  workspace_id   uuid not null references workspace(id) on delete cascade,
  membership_id  uuid not null references membership(id) on delete cascade,
  task_id        uuid references task(id) on delete cascade,
  tipo           text not null,
  preguntado_en  timestamptz not null default now(),
  vence_en       timestamptz not null,
  recordatorios  integer not null default 0,
  satisfecho_en  timestamptz,
  escalado_en    timestamptz
);

create index pending_reply_pendientes on pending_reply (workspace_id, vence_en)
  where satisfecho_en is null;

-- =========================================================================
-- Mensajería
-- =========================================================================

create table inbound_message (
  id                  uuid primary key default gen_random_uuid(),
  workspace_id        uuid not null references workspace(id) on delete cascade,
  telegram_message_id bigint,
  chat_id             bigint not null,
  app_user_id         uuid references app_user(id),
  texto               text,
  intencion           text,
  task_id             uuid references task(id),
  at                  timestamptz not null default now(),
  -- T9-R4 (migración 0022): el callback_data del botón que la persona tocó (una
  -- fila de toque). Nula en un mensaje escrito y en un toque absorbido por
  -- repetido dentro de la ventana.
  boton_callback      text,
  -- El Motor (migración 0031): el bot que recibió el mensaje. Con él, el índice
  -- `inbound_message_unico_por_mensaje` hace que un mensaje de Telegram repetido
  -- se reciba una sola vez. Nulo en los flujos congelados.
  telegram_bot_id     bigint,
  constraint inbound_message_workspace_id_unique unique (workspace_id, id),
  constraint inbound_message_workspace_chat_unique
    unique (workspace_id, id, chat_id)
);

-- Leda nunca llama a Telegram directamente: escribe acá y un worker despacha.
-- dedupe_key es lo que hace que un reinicio no duplique mensajes.
create table message_outbox (
  id                      uuid primary key default gen_random_uuid(),
  workspace_id            uuid not null references workspace(id) on delete cascade,
  chat_id                 bigint not null,
  destinatario_membership_id uuid references membership(id),
  tipo                    tipo_mensaje not null default 'normal',
  cuerpo                  text not null,
  -- Una respuesta a alguien que acaba de escribir sale siempre. La regla de
  -- no escribir fuera de horario es para lo que Leda inicia; dejar a una
  -- persona esperando hasta mañana porque son las 17:05 es peor.
  es_respuesta            boolean not null default false,
  -- Saludo diario (pack 06 §3, T28; revisión 2026-09-28+2): esta fila ES la
  -- bienvenida de incorporación -- el despachador reclama la reserva del día
  -- por ella sin anteponerle nada, nunca una categoría de `tipo` (que la
  -- presentación de grupo también usa como 'informativo' sin ser un saludo).
  es_bienvenida           boolean not null default false,
  -- Aviso de coordinación (migración 0024, decisión del usuario 2026-09-30): lo
  -- que una persona hizo sobre trabajo compartido y otra necesita para actuar o
  -- enterarse (entrega para revisar, cambios pedidos, aprobación, borrador para
  -- confirmar o rechazado). No cuenta contra el tope diario de mensajes
  -- automáticos ni lo posterga; los seguimientos (cadencias, escalera) sí.
  es_coordinacion         boolean not null default false,
  -- T9-R1c-3: lo que la persona había escrito, para que lo copie con un toque --
  -- el final de `cuerpo`. El transporte lo marca como bloque (entidad `pre`) y,
  -- si entra en 256 unidades UTF-16, agrega el botón de copiar.
  bloque_copiable         text,
  -- T9-R2 (migración 0021): el mensaje entrante al que responde esta salida. Se
  -- llena sola con la configuración local `leda.entrante_id` que deja el gateway
  -- al procesar un mensaje; nula fuera de uno (toque, cadencia, escalera). La
  -- clave foránea se declara más abajo, con las demás de la tabla.
  entrante_id             uuid
    default nullif(current_setting('leda.entrante_id', true), '')::uuid,
  -- T9-R2: la respuesta a la que pertenece la fila cuando una respuesta se
  -- encola en varias llamadas (texto en partes y mensaje con botones). Nula: la
  -- fila es su propia respuesta.
  respuesta_grupo         text,
  requiere_confirmacion   boolean not null default false,
  confirmado_por          uuid references app_user(id),
  confirmado_en           timestamptz,
  estado                  estado_salida not null default 'pendiente',
  programado_para         timestamptz not null default now(),
  vence_en                timestamptz,
  enviado_en              timestamptz,
  telegram_message_id     bigint,
  dedupe_key              text not null unique,
  intentos                integer not null default 0,
  ultimo_error            text,
  -- Si el mensaje pregunta algo con opciones, acá está la acción congelada.
  -- La referencia se agrega más abajo: pending_action se declara después.
  pending_action_id       uuid,
  -- Migración 0030: para las claves foráneas con el espacio del motor.
  constraint message_outbox_workspace_id_unique unique (workspace_id, id)
);

create index outbox_despacho on message_outbox (estado, programado_para)
  where estado in ('listo', 'pendiente');

-- =========================================================================
-- Acciones pendientes
-- =========================================================================

-- Trabajo que Leda entendió y todavía no ejecutó, porque falta un acto de
-- una persona: confirmarlo, o elegir entre opciones.
--
-- Sin esta tabla la confirmación humana sólo sabía frenar. El pedido salía a
-- la cola como texto y la herramienta con sus argumentos se descartaba, así
-- que confirmar no tenía nada que ejecutar.
create table pending_action (
  id                  uuid primary key default gen_random_uuid(),
  workspace_id        uuid not null references workspace(id) on delete cascade,
  -- Quién puede resolverla. En un grupo el botón lo ve todo el mundo; sólo
  -- esta persona lo puede apretar.
  membership_id       uuid not null references membership(id) on delete cascade,
  herramienta         text not null,
  args                jsonb not null default '{}'::jsonb,
  -- Qué argumento completa la opción elegida. Nulo cuando lo que se pregunta
  -- es confirmar o cancelar.
  campo               text,
  resumen             text not null,
  estado              estado_pendiente not null default 'esperando',
  creado_en           timestamptz not null default now(),
  -- Obligatorio a propósito: no hay acción pendiente eterna. Un botón se
  -- puede apretar tres días después; el contexto que lo justificaba, no.
  vence_en            timestamptz not null,
  resuelta_en         timestamptz,
  resuelta_por        uuid references app_user(id),
  chat_id             bigint,
  telegram_message_id bigint
  ,resultado           jsonb
  ,draft_id            uuid references task_draft(id)
  ,draft_version       integer
  ,preview             jsonb
  -- Huella del estado que se leyó para armar la vista previa (opaca para la
  -- base; la arma y la interpreta `herramientas.py`). Al confirmar se vuelve
  -- a calcular y, si difiere, no se aplica nada (ADR 0005, decisión 1).
  ,huella              text
  -- Modificar (ADR 0005, decisión 1; T3): cuándo se cerró esta fila porque
  -- la persona apretó Modificar en vez de Confirmar o Cancelar. No es un
  -- estado nuevo de `estado_pendiente` -- queda en 'cancelada', que ya
  -- significa "no se aplicó nada" -- sino la marca de que además hay que
  -- interpretar el próximo mensaje de texto de esa persona en ese chat como
  -- una corrección de esta propuesta: `herramienta`, `args` y `resumen` ya
  -- quedan guardados desde que se armó la vista previa, así que no hace
  -- falta una tabla aparte.
  ,modificar_pedido_en timestamptz
  -- Cuándo se leyó esa corrección para el turno siguiente. Sin esto la misma
  -- fila serviría de contexto para cualquier mensaje posterior dentro de su
  -- vigencia, no sólo el próximo (T3, punto 5).
  ,modificacion_consumida_en timestamptz
  ,constraint pending_action_workspace_id_unique unique (workspace_id, id)
  ,constraint pending_action_membership_workspace
     foreign key (workspace_id, membership_id)
     references membership(workspace_id, id)
  ,constraint pending_action_draft_workspace
     foreign key (workspace_id, draft_id)
     references task_draft(workspace_id, id)
  ,check ((draft_id is null and draft_version is null and preview is null)
       or (draft_id is not null and draft_version is not null and preview is not null))
);

create index pending_action_abiertas on pending_action (workspace_id, vence_en)
  where estado = 'esperando';

-- Una opción por botón. El token es lo que viaja en callback_data, que
-- Telegram corta en 64 bytes: por eso es un identificador corto que apunta
-- acá y no la acción serializada.
create table pending_action_option (
  id                uuid primary key default gen_random_uuid(),
  workspace_id      uuid not null references workspace(id) on delete cascade,
  pending_action_id uuid not null references pending_action(id) on delete cascade,
  token             text not null unique,
  etiqueta          text not null,
  valor             jsonb,
  orden             integer not null default 0,
  activa            boolean not null default true,
  resultado         jsonb,
  constraint pending_action_option_workspace_id_unique unique (workspace_id, id),
  constraint pending_action_option_parent_workspace
    foreign key (workspace_id, pending_action_id)
    references pending_action(workspace_id, id) on delete cascade,
  constraint token_cabe_en_callback_data check (octet_length(token) between 8 and 40),
  constraint pending_action_option_telegram_label
    check (telegram_utf16_units(etiqueta) between 1 and 80)
);

create index pending_action_option_de
  on pending_action_option (pending_action_id, orden);

alter table message_outbox
  add constraint message_outbox_telegram_payload
  check (telegram_utf16_units(cuerpo) between 1 and
         case when pending_action_id is not null then 3900 else 4096 end);

-- Se declara acá y no en la tabla porque message_outbox viene antes. Si la
-- acción se borra, el mensaje queda: es parte del historial de lo que se dijo.
alter table message_outbox
  add constraint message_outbox_pending_action
  foreign key (pending_action_id) references pending_action(id) on delete set null;

alter table message_outbox
  add constraint message_outbox_recipient_workspace
    foreign key (workspace_id, destinatario_membership_id)
    references membership(workspace_id, id),
  add constraint message_outbox_pending_workspace
    foreign key (workspace_id, pending_action_id)
    references pending_action(workspace_id, id) on delete set null (pending_action_id);

-- T9-R2: si la retención borra el mensaje entrante, la salida queda. Sobre la
-- clave primaria y no compuesta con el espacio, como las demás: la compuesta
-- dependería de la restricción única de la 0002 y volver atrás la 0002 dejaría de
-- ser posible. El valor lo pone el gateway con un mensaje del mismo espacio.
alter table message_outbox
  add constraint message_outbox_entrante
    foreign key (entrante_id) references inbound_message(id)
    on delete set null;

create index outbox_por_entrante on message_outbox (entrante_id)
  where entrante_id is not null;

create index inbound_por_boton on inbound_message
  (workspace_id, chat_id, app_user_id, boton_callback, at)
  where boton_callback is not null;

-- El Motor (migración 0031): ejecución única de un mensaje repetido. El número de
-- mensaje es único dentro de una conversación con un bot, así que la identidad del
-- mensaje lleva el bot. Los flujos congelados no lo informan: su recibo repetido
-- pasada la cota de reentrega (`gateway._estado_de_entrega`) sigue entrando.
create unique index inbound_message_unico_por_mensaje
  on inbound_message (workspace_id, telegram_bot_id, chat_id, telegram_message_id)
  where telegram_bot_id is not null and telegram_message_id is not null;

-- Resolver es una sola llamada a propósito: dos toques al mismo botón compiten
-- por la misma fila y sólo uno la mueve de 'esperando'. Si esto se hiciera con
-- un select seguido de un update, la carrera ejecutaría la acción dos veces.
--
-- No lanza excepciones para el control de flujo: devuelve qué pasó, y quien
-- llama decide cómo contarlo. 'ajena' no es un error técnico, es una persona
-- apretando un botón que no le corresponde.
create function resolver_pendiente(p_token text, p_app_user_id uuid,
                                   p_ahora timestamptz)
returns table (resultado text, herramienta text, args jsonb,
               cancelada boolean, huella text)
language plpgsql security definer
set search_path = leda, public, pg_temp as $$
declare
  o record;
  a record;
  ws uuid := nullif(current_setting('leda.workspace_id', true), '')::uuid;
begin
  select * into o from pending_action_option
   where token = p_token and (ws is null or workspace_id = ws);
  if not found then
    return query select 'inexistente'::text, null::text, null::jsonb,
      null::boolean, null::text;
    return;
  end if;

  select * into a from pending_action where id = o.pending_action_id;

  if a.estado <> 'esperando' then
    return query select 'usada'::text, null::text, null::jsonb,
      null::boolean, null::text;
    return;
  end if;

  if a.vence_en <= p_ahora then
    update pending_action set estado = 'vencida' where id = a.id;
    return query select 'vencida'::text, null::text, null::jsonb,
      null::boolean, null::text;
    return;
  end if;

  -- El dueño de la acción es el único que la resuelve. Se resuelve por
  -- membresía, no por identidad de plataforma: el sombrero lo da el espacio.
  if not exists (select 1 from membership m
                  where m.id = a.membership_id and m.app_user_id = p_app_user_id) then
    return query select 'ajena'::text, null::text, null::jsonb,
      null::boolean, null::text;
    return;
  end if;

  -- Modificar (T3, ADR 0005 decisión 1): cierra sin aplicar nada, igual que
  -- Cancelar -- por eso queda en 'cancelada' y no en un estado nuevo -- pero
  -- deja marcado `modificar_pedido_en`: la fila misma es el contexto que va
  -- a leer el próximo turno de esta persona en este chat, porque ya tiene
  -- `herramienta`, `args` y `resumen` de cuando se armó la vista previa.
  if a.campo is null and o.valor = '"modificar"'::jsonb then
    update pending_action
       set estado = 'cancelada', resuelta_en = p_ahora, resuelta_por = p_app_user_id,
           modificar_pedido_en = p_ahora
     where id = a.id and estado = 'esperando';
    if not found then
      return query select 'usada'::text, null::text, null::jsonb,
        null::boolean, null::text;
      return;
    end if;
    -- Sólo puede haber una Modificación abierta por persona y chat: una
    -- nueva deja sin efecto cualquier otra que todavía no se hubiera leído,
    -- para que una corrección nunca se aplique a una propuesta vieja.
    update pending_action
       set modificacion_consumida_en = p_ahora
     where workspace_id = a.workspace_id and membership_id = a.membership_id
       and chat_id = a.chat_id and modificar_pedido_en is not null
       and modificacion_consumida_en is null and id <> a.id;
    return query select 'modificada'::text, a.herramienta, a.args, false, a.huella;
    return;
  end if;

  if a.campo is null and o.valor = 'false'::jsonb then
    update pending_action
       set estado = 'cancelada', resuelta_en = p_ahora, resuelta_por = p_app_user_id
     where id = a.id and estado = 'esperando';
    if not found then
      return query select 'usada'::text, null::text, null::jsonb,
        null::boolean, null::text;
      return;
    end if;
    return query select 'cancelada'::text, null::text, null::jsonb, true,
      null::text;
    return;
  end if;

  update pending_action
     set estado = 'resuelta', resuelta_en = p_ahora, resuelta_por = p_app_user_id
   where id = a.id and estado = 'esperando';
  if not found then
    return query select 'usada'::text, null::text, null::jsonb,
      null::boolean, null::text;
    return;
  end if;

  return query select 'ok'::text, a.herramienta,
    case when a.campo is null then a.args
         else a.args || jsonb_build_object(a.campo, o.valor) end,
    false, a.huella;
end $$;

comment on function resolver_pendiente is
  'Resuelve una acción pendiente por el token de una de sus opciones. Atómica: el doble toque de un botón ejecuta una sola vez. Devuelve la huella guardada para que quien llama detecte si el estado cambió desde la vista previa. "modificada" cierra sin aplicar nada y marca `modificar_pedido_en`, que deja la fila como contexto para el próximo turno de esa persona en ese chat (ADR 0005, decisión 1).';

-- Draft commitment is deliberately separate from generic pending actions. It
-- locks every linked row, revalidates the preview, creates the task and audit,
-- and only then consumes the pending action in the same transaction.
create function confirmar_borrador_tarea(p_workspace_id uuid, p_token text,
                                         p_telegram_user_id bigint,
                                         p_chat_id bigint)
returns table (resultado text, task_id uuid, pending_action_id uuid, replay boolean)
language plpgsql security definer
set search_path = leda, public, pg_temp as $$
declare
  o pending_action_option%rowtype;
  a pending_action%rowtype;
  d task_draft%rowtype;
  obj objective%rowtype;
  responsable membership%rowtype;
  politica task_evidence_policy%rowtype;
  actor_membership uuid;
  actor_app_user_id uuid;
  aprobador_actual uuid;
  nueva_task uuid;
  ahora timestamptz := clock_timestamp();
  preview_actual jsonb;
begin
  perform set_config('leda.workspace_id', p_workspace_id::text, true);
  select * into o from pending_action_option
   where token = p_token and workspace_id = p_workspace_id;
  if not found then
    return query select 'inexistente'::text, null::uuid, null::uuid, false;
    return;
  end if;

  select * into a from pending_action where id = o.pending_action_id for update;
  if a.draft_id is null then
    return query select 'no_es_borrador'::text, null::uuid, a.id, false;
    return;
  end if;
  if a.workspace_id <> p_workspace_id then
    return query select 'inexistente'::text, null::uuid, null::uuid, false;
    return;
  end if;
  if a.chat_id is distinct from p_chat_id then
    return query select 'ajena'::text, null::uuid, a.id, false;
    return;
  end if;

  select m.id, m.app_user_id into actor_membership, actor_app_user_id
    from membership m join app_user u on u.id = m.app_user_id
   where m.workspace_id = p_workspace_id and m.id = a.membership_id
     and u.telegram_user_id = p_telegram_user_id and m.activo;
  if actor_membership is null then
    return query select 'ajena'::text, null::uuid, a.id, false;
    return;
  end if;
  if a.estado <> 'esperando' then
    if a.resultado->>'resultado' in ('ok', 'cancelada') then
      return query select a.resultado->>'resultado',
        nullif(a.resultado->>'task_id', '')::uuid, a.id, true;
    end if;
    return query select 'usada'::text, null::uuid, a.id, false;
    return;
  end if;
  if a.vence_en <= ahora then
    update pending_action set estado = 'vencida' where id = a.id;
    update pending_action_option set activa = false
     where pending_action_option.pending_action_id = a.id;
    return query select 'vencida'::text, null::uuid, a.id, false;
    return;
  end if;

  if o.valor = 'false'::jsonb then
    update pending_action
       set estado = 'cancelada', resuelta_en = ahora,
            resuelta_por = actor_app_user_id,
             resultado = coalesce(pending_action.resultado, '{}'::jsonb)
                         || jsonb_build_object('resultado', 'cancelada')
     where id = a.id;
    update pending_action_option set activa = false
     where pending_action_option.pending_action_id = a.id;
    update task_draft set estado = 'cancelled', actualizado_en = ahora where id = a.draft_id;
    insert into message_outbox
         (workspace_id, chat_id, destinatario_membership_id, tipo, cuerpo,
          estado, programado_para, dedupe_key, es_respuesta)
    values (a.workspace_id, a.chat_id, a.membership_id, 'normal',
            'Listo, cancelé el borrador de la tarea.', 'listo', ahora,
            a.workspace_id || ':intake-terminal:' || a.id || ':cancelled', true)
    on conflict (dedupe_key) do nothing;
    return query select 'cancelada'::text, null::uuid, a.id, false;
    return;
  end if;

  select * into d from task_draft where id = a.draft_id for update;
  if not found or d.converted_task_id is not null or d.version <> a.draft_version
     or d.workspace_id <> a.workspace_id then
    update pending_action set estado = 'vencida' where id = a.id;
    update pending_action_option set activa = false
     where pending_action_option.pending_action_id = a.id;
    return query select 'obsoleta'::text, null::uuid, a.id, false;
    return;
  end if;

  select * into obj from objective where id = d.objective_id for share;
  select * into responsable from membership
   where id = d.responsable_membership_id for share;
  select * into politica from task_evidence_policy
   where workspace_id = d.workspace_id and area_id = d.area_id for share;

  preview_actual := jsonb_build_object(
    'draft_id', d.id::text, 'version', d.version,
    'titulo', d.titulo, 'descripcion', d.descripcion,
    'objetivo', d.objective_snapshot,
    'area_id', d.area_id::text,
    'responsable_membership_id', d.responsable_membership_id::text,
    'fecha_objetivo', d.fecha_objetivo::text,
    'criterio_aceptacion', d.criterio_aceptacion,
    'evidencia_requerida', to_jsonb(d.evidencia_requerida),
    'evidencia_policy_version', d.evidencia_policy_version);

  if a.preview is distinct from preview_actual
     or d.objective_id is null or d.responsable_membership_id is null
     or d.area_id is null or d.fecha_objetivo is null
     or nullif(btrim(d.titulo), '') is null
     or nullif(btrim(d.criterio_aceptacion), '') is null
     or d.evidencia_requerida is null
     or obj.id is null or obj.workspace_id <> d.workspace_id
     or obj.estado not in ('activo', 'propuesto')
     or d.objective_snapshot is distinct from
        jsonb_build_object('id', obj.id, 'titulo', obj.titulo, 'estado', obj.estado)
     or responsable.id is null or not responsable.activo
     or responsable.workspace_id <> d.workspace_id
     or responsable.area_id <> d.area_id
     or politica.area_id is null
     or politica.version <> d.evidencia_policy_version
     or politica.evidencia_requerida is distinct from d.evidencia_requerida then
    update pending_action set estado = 'vencida' where id = a.id;
    update pending_action_option set activa = false
     where pending_action_option.pending_action_id = a.id;
    return query select 'obsoleta'::text, null::uuid, a.id, false;
    return;
  end if;

  aprobador_actual := responsable.aprobador_membership_id;
  if aprobador_actual is null then
    select m.id into aprobador_actual
      from membership m join rol r on r.id = m.rol_id
     where m.workspace_id = d.workspace_id and m.activo and r.autoridad_final;
  end if;
  if aprobador_actual is distinct from a.membership_id
     or aprobador_actual is distinct from actor_membership then
    update pending_action set estado = 'vencida' where id = a.id;
    update pending_action_option set activa = false
     where pending_action_option.pending_action_id = a.id;
    return query select 'obsoleta'::text, null::uuid, a.id, false;
    return;
  end if;

  insert into task
       (workspace_id, objective_id, titulo, descripcion, area_id,
        responsable_membership_id, fecha_objetivo, criterio_aceptacion,
        evidencia_requerida, evidencia_policy_version, source_draft_id)
  values
       (d.workspace_id, d.objective_id, d.titulo, d.descripcion, d.area_id,
        d.responsable_membership_id, d.fecha_objetivo, d.criterio_aceptacion,
        d.evidencia_requerida, d.evidencia_policy_version, d.id)
  returning id into nueva_task;

  insert into task_state_event
       (task_id, estado_nuevo, actor_kind, actor_app_user_id, motivo)
  values (nueva_task, 'asignada', 'persona', actor_app_user_id,
          'borrador confirmado por autoridad vigente');

  insert into audit_log
       (workspace_id, actor_app_user_id, actor_kind, accion, sujeto_tipo,
        sujeto_id, detalle)
  values
       (d.workspace_id, actor_app_user_id, 'persona',
        'confirmar_borrador_tarea', 'task', nueva_task,
        jsonb_build_object(
          'draft_id', d.id, 'draft_version', d.version,
          'pending_action_id', a.id,
          'responsable_membership_id', d.responsable_membership_id,
          'confirmador_membership_id', actor_membership,
          'evidencia_policy_version', d.evidencia_policy_version));

  update task_draft set converted_task_id = nueva_task, estado = 'converted',
                        actualizado_en = ahora
   where id = d.id;
  update pending_action
     set estado = 'resuelta', resuelta_en = ahora,
         resuelta_por = actor_app_user_id,
          resultado = coalesce(pending_action.resultado, '{}'::jsonb)
                      || jsonb_build_object('resultado', 'ok', 'task_id', nueva_task)
   where id = a.id;
  update pending_action_option set activa = false
   where pending_action_option.pending_action_id = a.id;
  insert into message_outbox
       (workspace_id, chat_id, destinatario_membership_id, tipo, cuerpo,
        estado, programado_para, dedupe_key, es_respuesta)
  values (a.workspace_id, a.chat_id, a.membership_id, 'normal',
          'Hecho. La tarea quedó comprometida.', 'listo', ahora,
          a.workspace_id || ':intake-terminal:' || a.id || ':converted', true)
  on conflict (dedupe_key) do nothing;

  return query select 'ok'::text, nueva_task, a.id, false;
end $$;

revoke all on function confirmar_borrador_tarea(uuid, text, bigint, bigint)
  from public;

-- Intake terminal wrapper. Unit 1A still performs the conversion; this layer
-- adds deterministic replay and closes every intake surface atomically.
create function resolver_ingreso_borrador(p_workspace_id uuid, p_token text,
                                          p_telegram_user_id bigint,
                                          p_chat_id bigint)
returns table (resultado text, task_id uuid, pending_action_id uuid, replay boolean)
language plpgsql security definer
set search_path = leda, public, pg_temp as $$
begin
  perform set_config('leda.workspace_id', p_workspace_id::text, true);
  -- Modificar (T9-R1c-3), Enviar a aprobación (T9-R1c-4) y Rechazar (2026-09-30)
  -- no confirman: sus tokens nunca llegan a la conversión.
  if exists (select 1 from pending_action_option o
              where o.token = p_token and o.workspace_id = p_workspace_id
                and o.valor in (to_jsonb('modificar'::text),
                                to_jsonb('enviar'::text),
                                to_jsonb('rechazar'::text))) then
    return query select 'inexistente'::text, null::uuid, null::uuid, false;
    return;
  end if;
  return query
    select c.resultado, c.task_id, c.pending_action_id, c.replay
      from confirmar_borrador_tarea(
        p_workspace_id, p_token, p_telegram_user_id, p_chat_id) c;
end $$;

revoke all on function resolver_ingreso_borrador(uuid, text, bigint, bigint)
  from public;

-- =========================================================================
-- El motor de conversación (El Motor, prueba chica; migraciones 0030 y 0031)
--
-- ADR 0018, decisiones 3, 8 y 9; `odd/tasks/prueba-chica-del-motor.md`,
-- sección 5. Toda tabla lleva `workspace_id` y entra en el bucle de RLS forzado
-- de abajo; ninguna lleva `chat_id` ni `callback_data`. Toda referencia es al
-- mismo espacio (la comprobación de una clave foránea no pasa por la RLS): por la
-- clave foránea con el espacio o, hacia `membership` e `inbound_message`, por
-- `exigir_referencias_del_espacio()` (más abajo, en "Reglas"). Los momentos no tienen valor por omisión: los pone el motor con su
-- reloj. El registro de turnos, las previsiones y quién destraba sólo se
-- agregan; preguntas, opciones y avisos se cierran, pero no se borran.
-- =========================================================================

create table conversation_question (
  id                 uuid primary key default gen_random_uuid(),
  workspace_id       uuid not null references workspace(id) on delete cascade,
  membership_id      uuid not null,
  tipo               text not null,
  task_id            uuid,
  jugada             jsonb,
  se_puede_dejar     boolean not null,
  abierta_en         timestamptz not null,
  para_despues_en    timestamptz,
  cerrada_en         timestamptz,
  cierre             text check (cierre in ('respondida', 'cancelada', 'sin_efecto')),
  cierre_detalle     jsonb,
  preguntada_en      timestamptz,
  vuelve_aparte      boolean not null default false,
  constraint conversation_question_workspace_id_unique unique (workspace_id, id),
  constraint conversation_question_membership
    foreign key (membership_id)
    references membership(id) on delete cascade,
  constraint conversation_question_task_workspace
    foreign key (workspace_id, task_id)
    references task(workspace_id, id) on delete cascade,
  constraint conversation_question_cierre check ((cerrada_en is null) = (cierre is null))
);

create index conversation_question_abiertas
  on conversation_question (workspace_id, membership_id) where cerrada_en is null;

create table conversation_option (
  id            uuid primary key default gen_random_uuid(),
  workspace_id  uuid not null references workspace(id) on delete cascade,
  question_id   uuid not null,
  token         text not null unique,
  etiqueta      text not null,
  valor         jsonb not null,
  orden         integer not null,
  elegida_en    timestamptz,
  constraint conversation_option_workspace_id_unique unique (workspace_id, id),
  constraint conversation_option_question_workspace
    foreign key (workspace_id, question_id)
    references conversation_question(workspace_id, id) on delete cascade
);

create index conversation_option_de on conversation_option (question_id, orden);

create table conversation_turn (
  id                  uuid primary key default gen_random_uuid(),
  workspace_id        uuid not null references workspace(id) on delete cascade,
  membership_id       uuid not null,
  sentido             text not null check (sentido in ('entrada', 'salida')),
  inbound_message_id  uuid,
  outbox_id           uuid,
  option_id           uuid,
  jugadas             jsonb,
  resultado           jsonb,
  ia                  text,
  latencia_ms         integer check (latencia_ms >= 0),
  error               text,
  at                  timestamptz not null,
  -- El Motor (migración 0031): el número del turno en la conversación de la
  -- persona; lo pone el motor y ordena los turnos de la misma hora.
  numero              integer not null check (numero >= 1),
  constraint conversation_turn_workspace_id_unique unique (workspace_id, id),
  constraint conversation_turn_numero_unique unique (membership_id, numero),
  constraint conversation_turn_membership
    foreign key (membership_id)
    references membership(id) on delete cascade,
  constraint conversation_turn_inbound
    foreign key (inbound_message_id)
    references inbound_message(id) on delete set null,
  constraint conversation_turn_outbox_workspace
    foreign key (workspace_id, outbox_id)
    references message_outbox(workspace_id, id) on delete set null (outbox_id),
  constraint conversation_turn_option_workspace
    foreign key (workspace_id, option_id)
    references conversation_option(workspace_id, id) on delete set null (option_id),
  constraint conversation_turn_sentido check (
    (sentido = 'entrada' and outbox_id is null) or
    (sentido = 'salida' and inbound_message_id is null and option_id is null))
);

create index conversation_turn_por_persona
  on conversation_turn (workspace_id, membership_id, at desc);

-- El Motor (migración 0031): un mensaje tiene a lo sumo un turno de entrada.
create unique index conversation_turn_una_entrada_por_mensaje
  on conversation_turn (inbound_message_id) where sentido = 'entrada';

create table scheduled_notice (
  id                          uuid primary key default gen_random_uuid(),
  workspace_id                uuid not null references workspace(id) on delete cascade,
  tipo                        text not null,
  task_id                     uuid,
  -- Nulo sólo en un aviso al grupo del espacio (migración 0048, `al_grupo`).
  destinatario_membership_id  uuid,
  turno_id                    uuid,
  hechos                      jsonb not null,
  programado_para             timestamptz not null,
  estado                      text not null default 'guardado'
                              check (estado in ('guardado', 'enviado', 'omitido', 'fallido')),
  intentos                    integer not null default 0 check (intentos >= 0),
  proximo_intento_en          timestamptz,
  motivo_omision              text,
  outbox_id                   uuid,
  dedupe_key                  text not null,
  creado_en                   timestamptz not null,
  resuelto_en                 timestamptz,
  -- El Motor (migración 0047): lo que llevó la lista de la cadencia, fuera de los hechos.
  tareas_de_la_lista          jsonb,
  -- El Motor (migración 0048): el aviso va al grupo del espacio (el informe al grupo), no a una
  -- persona. El chat no se guarda acá: sale de `workspace.grupo_chat_id` al encolarlo.
  al_grupo                    boolean not null default false,
  constraint scheduled_notice_workspace_id_unique unique (workspace_id, id),
  constraint scheduled_notice_dedupe unique (workspace_id, dedupe_key),
  constraint scheduled_notice_task_workspace
    foreign key (workspace_id, task_id)
    references task(workspace_id, id) on delete cascade,
  constraint scheduled_notice_recipient
    foreign key (destinatario_membership_id)
    references membership(id) on delete cascade,
  constraint scheduled_notice_turn_workspace
    foreign key (workspace_id, turno_id)
    references conversation_turn(workspace_id, id) on delete set null (turno_id),
  constraint scheduled_notice_outbox_workspace
    foreign key (workspace_id, outbox_id)
    references message_outbox(workspace_id, id) on delete set null (outbox_id),
  constraint scheduled_notice_resuelto check ((estado = 'guardado') = (resuelto_en is null)),
  constraint scheduled_notice_omision check (estado <> 'omitido' or motivo_omision is not null),
  -- A una persona o al grupo, nunca a los dos ni a nadie (migración 0048).
  constraint scheduled_notice_destino check (al_grupo = (destinatario_membership_id is null))
);

create index scheduled_notice_por_salir
  on scheduled_notice (workspace_id, programado_para) where estado = 'guardado';

create table conversation_state (
  membership_id            uuid primary key,
  workspace_id             uuid not null references workspace(id) on delete cascade,
  pregunta_abierta_id      uuid,
  ultimo_aviso_id          uuid,
  mostrado_para_confirmar  jsonb,
  huella                   text,
  actualizado_en           timestamptz not null,
  constraint conversation_state_membership
    foreign key (membership_id)
    references membership(id) on delete cascade,
  constraint conversation_state_question_workspace
    foreign key (workspace_id, pregunta_abierta_id)
    references conversation_question(workspace_id, id)
    on delete set null (pregunta_abierta_id),
  constraint conversation_state_notice_workspace
    foreign key (workspace_id, ultimo_aviso_id)
    references scheduled_notice(workspace_id, id) on delete set null (ultimo_aviso_id)
);

comment on table conversation_state is
  'El Motor (ADR 0018, decisión 3.1): una fila por persona. La pregunta abierta, el último aviso que Leda le mandó (su tarea sale del aviso) y, reservadas, lo mostrado para confirmar y su huella. Los temas para después son las preguntas sin cerrar con para_despues_en.';
comment on table conversation_turn is
  'El Motor (ADR 0018, decisión 3.2): el registro de turnos. Sólo se agrega; se conserva como las conversaciones (ADR 0002).';
comment on column conversation_turn.numero is
  'El Motor (E2-3): el número del turno en la conversación de la persona (1, 2, 3...). Lo pone el motor; ordena los turnos de la misma hora.';
comment on table conversation_question is
  'El Motor: las preguntas de Leda. Se cierran con cerrada_en y cierre; una pregunta dejada para después lleva para_despues_en.';
comment on column conversation_question.preguntada_en is
  'La última vez que Leda le hizo la pregunta a la persona (decisión 21 del usuario, 2026-10-08): las 4 horas de una pregunta sin contestar se cuentan desde ahí. Sin valor, desde abierta_en.';
comment on column conversation_question.vuelve_aparte is
  'Una de dos preguntas abiertas a la vez porque un aviso de Leda hizo la segunda (decisión 21): cuando una se cierra, el código trae la otra en un mensaje aparte.';
comment on table conversation_option is
  'El Motor: las opciones de una duda (situación general 5). El token es único y es lo que vuelve con un toque.';
comment on table scheduled_notice is
  'El Motor (ADR 0018, decisión 8, precisión del 2026-10-05): lo que Leda manda por su cuenta, guardado como hechos. Entra al outbox recién cuando la IA lo redactó.';
comment on column scheduled_notice.tareas_de_la_lista is
  'El Motor (C-6, decisiones 31 y 46 del usuario, 2026-10-09): en la lista de la cadencia que salió, las tareas abiertas de la persona en ese momento, cada una con su situación, si se mostró, si se preguntó por ella, desde cuándo no la contesta y cuándo la contestó. Fuera de los hechos: lo lee sólo el código. Nulo en los demás avisos y en las listas de antes.';
comment on column scheduled_notice.al_grupo is
  'El Motor (C-6, decisión 25 del usuario, 2026-10-09): el aviso va al grupo del espacio (el informe al grupo de la cadencia), no a una persona; entonces no tiene destinatario. El chat del grupo no se guarda acá: sale de workspace.grupo_chat_id al encolarlo en el outbox.';

create table task_forecast (
  id                       uuid primary key default gen_random_uuid(),
  workspace_id             uuid not null references workspace(id) on delete cascade,
  task_id                  uuid not null references task(id) on delete cascade,
  fecha_prevista           date not null,
  motivo                   text,
  fecha_comprometida       timestamptz not null,
  atraso_dias_habiles      integer not null,
  reemplaza_id             uuid,
  es_correccion            boolean not null default false,
  dicho_por_membership_id  uuid not null,
  at                       timestamptz not null,
  constraint task_forecast_workspace_id_unique unique (workspace_id, id),
  constraint task_forecast_task_id_unique unique (workspace_id, task_id, id),
  -- Una previsión sólo reemplaza a otra de la misma tarea, del mismo espacio
  -- (revisión de la E2-1). Sin `reemplaza_id` no se comprueba (match simple).
  constraint task_forecast_replaces_same_task
    foreign key (workspace_id, task_id, reemplaza_id)
    references task_forecast(workspace_id, task_id, id),
  constraint task_forecast_member
    foreign key (dicho_por_membership_id)
    references membership(id) on delete cascade
);

create index task_forecast_de on task_forecast (task_id, at desc);

create table blocker_unblocker (
  id                       uuid primary key default gen_random_uuid(),
  workspace_id             uuid not null references workspace(id) on delete cascade,
  blocker_id               uuid not null,
  destraba_membership_id   uuid,
  destraba_externo         text check (btrim(destraba_externo) <> ''),
  no_sabe                  boolean not null default false,
  dicho_por_membership_id  uuid not null,
  at                       timestamptz not null,
  -- Migración 0051: habló del bloqueo sin decir quién lo destraba (decisión 41).
  sin_decir_quien          boolean not null default false,
  constraint blocker_unblocker_blocker_workspace
    foreign key (workspace_id, blocker_id)
    references blocker(workspace_id, id) on delete cascade,
  constraint blocker_unblocker_member
    foreign key (destraba_membership_id)
    references membership(id) on delete cascade,
  constraint blocker_unblocker_said_by
    foreign key (dicho_por_membership_id)
    references membership(id) on delete cascade,
  constraint blocker_unblocker_exactamente_uno check (
    (destraba_membership_id is not null)::int
    + (destraba_externo is not null)::int
    + no_sabe::int
    + sin_decir_quien::int = 1),
  -- Migración 0042: para la clave foránea con el espacio de `dicho_de_quien_destraba`.
  constraint blocker_unblocker_workspace_id_unique unique (workspace_id, id)
);

create index blocker_unblocker_de on blocker_unblocker (blocker_id, at desc);

-- Lo que dice quien destraba cuando Leda le pregunta (migración 0042; C-5, decisión 4).
create table dicho_de_quien_destraba (
  id                       uuid primary key default gen_random_uuid(),
  workspace_id             uuid not null references workspace(id) on delete cascade,
  blocker_unblocker_id     uuid not null,
  dicho_por_membership_id  uuid not null,
  para_cuando              date,
  ya_esta                  boolean not null default false,
  lo_que_dice              text check (btrim(lo_que_dice) <> ''),
  at                       timestamptz not null,
  -- Migración 0043 (C-5, decisión 5): que no le corresponde, nunca con una fecha ni "ya está".
  no_le_corresponde        boolean not null default false,
  -- Migración 0044 (C-5, decisión 6): el bloqueo suyo con el que está trabado quien destraba.
  espera_su_bloqueo_id     uuid,
  constraint dicho_de_quien_destraba_destraba
    foreign key (workspace_id, blocker_unblocker_id)
    references blocker_unblocker(workspace_id, id) on delete cascade,
  constraint dicho_de_quien_destraba_said_by
    foreign key (dicho_por_membership_id)
    references membership(id) on delete cascade,
  constraint dicho_de_quien_destraba_espera_su_bloqueo
    foreign key (workspace_id, espera_su_bloqueo_id)
    references blocker(workspace_id, id) on delete cascade,
  constraint dicho_de_quien_destraba_dice_algo check (
    para_cuando is not null or ya_esta or lo_que_dice is not null or no_le_corresponde
    or espera_su_bloqueo_id is not null),
  constraint dicho_de_quien_destraba_no_le_corresponde check (
    not no_le_corresponde or (para_cuando is null and not ya_esta))
);

create index dicho_de_quien_destraba_de on dicho_de_quien_destraba (blocker_unblocker_id, at desc);

alter table task add constraint task_era_de
  foreign key (workspace_id, era_de_membership_id) references membership(workspace_id, id);
comment on column task.era_de_membership_id is
  'El Motor (C-7, decisión 28): de quién era la tarea antes de su primer pase (lo escribe el cambio de responsable). La revisa quien aprueba el trabajo de esa persona. Nulo: nunca cambió de manos.';

-- Pasarle una tarea a otra persona (migración 0045; C-7, delegar; ADR 0017, enmienda a la
-- decisión 2). Un pase se pide con una vista previa confirmada, lo decide el encargado del sector
-- de quien recibe (si es quien pide, su pedido es la decisión) y lo confirma quien recibe; sólo
-- entonces cambia el responsable, por `cambio_de_responsable`. Un "no" lo termina sin cambiar
-- nada. Nada se borra.
create table pase_de_tarea (
  id                        uuid primary key default gen_random_uuid(),
  workspace_id              uuid not null references workspace(id) on delete cascade,
  task_id                   uuid not null,
  de_membership_id          uuid not null,
  a_membership_id           uuid not null,
  pedido_por_membership_id  uuid not null,
  decide_membership_id      uuid not null,
  estado                    text not null check (estado in (
                              'esperando_decision', 'esperando_que_la_tome', 'la_tomo',
                              'no_lo_aprobo', 'no_la_tomo', 'sin_efecto',
                              'sin_respuesta')),
  pedido_en                 timestamptz not null,
  decidido_en               timestamptz,
  contestado_en             timestamptz,
  motivo                    text check (btrim(motivo) <> ''),
  constraint pase_de_tarea_workspace_id_unique unique (workspace_id, id),
  constraint pase_de_tarea_tarea
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade,
  constraint pase_de_tarea_de
    foreign key (workspace_id, de_membership_id) references membership(workspace_id, id),
  constraint pase_de_tarea_a
    foreign key (workspace_id, a_membership_id) references membership(workspace_id, id),
  constraint pase_de_tarea_pedido_por
    foreign key (workspace_id, pedido_por_membership_id) references membership(workspace_id, id),
  constraint pase_de_tarea_decide
    foreign key (workspace_id, decide_membership_id) references membership(workspace_id, id),
  constraint pase_de_tarea_a_otra_persona check (a_membership_id <> de_membership_id),
  constraint pase_de_tarea_decidido check (
    estado not in ('esperando_que_la_tome', 'la_tomo') or decidido_en is not null)
);

-- Un pase abierto por tarea.
create unique index pase_de_tarea_uno_abierto on pase_de_tarea (task_id)
  where estado in ('esperando_decision', 'esperando_que_la_tome');
create index pase_de_tarea_de_quien on pase_de_tarea (workspace_id, estado);

-- El cambio de responsable que deja un pase: sólo se agrega, y agregarlo es lo único que cambia
-- quién tiene la tarea (`aplicar_cambio_de_responsable`).
create table cambio_de_responsable (
  id                          uuid primary key default gen_random_uuid(),
  workspace_id                uuid not null references workspace(id) on delete cascade,
  task_id                     uuid not null,
  pase_id                     uuid not null,
  anterior_membership_id      uuid not null,
  nuevo_membership_id         uuid not null,
  aceptado_por_membership_id  uuid not null,
  revisa_membership_id        uuid,
  at                          timestamptz not null,
  constraint cambio_de_responsable_tarea
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade,
  constraint cambio_de_responsable_pase
    foreign key (workspace_id, pase_id) references pase_de_tarea(workspace_id, id)
    on delete cascade,
  constraint cambio_de_responsable_anterior
    foreign key (workspace_id, anterior_membership_id) references membership(workspace_id, id),
  constraint cambio_de_responsable_nuevo
    foreign key (workspace_id, nuevo_membership_id) references membership(workspace_id, id),
  constraint cambio_de_responsable_aceptado_por
    foreign key (workspace_id, aceptado_por_membership_id)
    references membership(workspace_id, id),
  constraint cambio_de_responsable_revisa
    foreign key (workspace_id, revisa_membership_id) references membership(workspace_id, id),
  constraint cambio_de_responsable_un_pase unique (pase_id)
);

create index cambio_de_responsable_tarea_at on cambio_de_responsable (task_id, at);

comment on table pase_de_tarea is
  'El Motor (C-7; ADR 0017, enmienda a la decisión 2): el pedido de pasarle una tarea a otra persona, quién lo pidió, quién lo decide (el encargado del sector de quien recibe) y cómo terminó. Cambia de estado sólo hacia adelante; la_tomo, sólo con su cambio_de_responsable.';
comment on table cambio_de_responsable is
  'El Motor (C-7): el cambio de quién tiene una tarea, con el pase que lo autorizó, quién la tenía, quién la tomó y quién revisaba su trabajo en ese momento (después, quien aprueba el trabajo de quien era la tarea, migración 0046). Sólo se agrega; agregarlo aplica el cambio en la tarea.';

-- El detalle de una tarea, a pedido (migración 0050; decisión 33 del usuario): quien no ve una
-- tarea pide su detalle, y lo decide el encargado del sector de la tarea. Un "no" lo termina sin
-- compartir nada. Nada se borra.
create table pedido_de_detalle (
  id                        uuid primary key default gen_random_uuid(),
  workspace_id              uuid not null references workspace(id) on delete cascade,
  task_id                   uuid not null,
  pedido_por_membership_id  uuid not null,
  decide_membership_id      uuid not null,
  estado                    text not null,
  pedido_en                 timestamptz not null,
  decidido_en               timestamptz,
  motivo                    text check (btrim(motivo) <> ''),
  -- Migración 0051: quién lo decidió, el encargado de ahora del sector de la tarea;
  -- decide_membership_id es a quién se le preguntó al pedirlo.
  decidido_por_membership_id uuid,
  constraint pedido_de_detalle_workspace_id_unique unique (workspace_id, id),
  constraint pedido_de_detalle_tarea
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade,
  constraint pedido_de_detalle_pedido_por
    foreign key (workspace_id, pedido_por_membership_id) references membership(workspace_id, id),
  constraint pedido_de_detalle_decide
    foreign key (workspace_id, decide_membership_id) references membership(workspace_id, id),
  constraint pedido_de_detalle_a_otra_persona check (decide_membership_id <> pedido_por_membership_id),
  constraint pedido_de_detalle_decidido check (
    estado = 'esperando_decision' or decidido_en is not null),
  constraint pedido_de_detalle_decidido_por
    foreign key (workspace_id, decidido_por_membership_id) references membership(workspace_id, id),
  constraint pedido_de_detalle_quien_lo_decidio check (
    (estado in ('compartida', 'no_compartida')) = (decidido_por_membership_id is not null)),
  -- Migración 0051: `sin_respuesta`, el pedido que nadie contestó (decisión 26).
  constraint pedido_de_detalle_estado_check check (estado in (
    'esperando_decision', 'compartida', 'no_compartida', 'sin_efecto', 'sin_respuesta'))
);

-- Un pedido abierto por tarea y persona.
create unique index pedido_de_detalle_uno_abierto on pedido_de_detalle (task_id, pedido_por_membership_id)
  where estado = 'esperando_decision';
create index pedido_de_detalle_de_quien on pedido_de_detalle (workspace_id, decide_membership_id, estado);

-- Una tarea compartida con alguien que no la veía: quién, quién la compartió y cuándo; si se dejó
-- de compartir, cuándo y quién. Una vigente por tarea y persona.
create table tarea_compartida (
  id                            uuid primary key default gen_random_uuid(),
  workspace_id                  uuid not null references workspace(id) on delete cascade,
  task_id                       uuid not null,
  membership_id                 uuid not null,
  compartida_por_membership_id  uuid not null,
  pedido_id                     uuid,
  at                            timestamptz not null,
  revocada_en                   timestamptz,
  revocada_por_membership_id    uuid,
  constraint tarea_compartida_tarea
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade,
  constraint tarea_compartida_con
    foreign key (workspace_id, membership_id) references membership(workspace_id, id),
  constraint tarea_compartida_por
    foreign key (workspace_id, compartida_por_membership_id) references membership(workspace_id, id),
  constraint tarea_compartida_pedido
    foreign key (workspace_id, pedido_id) references pedido_de_detalle(workspace_id, id)
    on delete cascade,
  constraint tarea_compartida_revocada_por
    foreign key (workspace_id, revocada_por_membership_id)
    references membership(workspace_id, id),
  constraint tarea_compartida_con_otra_persona check (membership_id <> compartida_por_membership_id),
  constraint tarea_compartida_revocada check (
    (revocada_en is null) = (revocada_por_membership_id is null))
);

create unique index tarea_compartida_vigente on tarea_compartida (task_id, membership_id)
  where revocada_en is null;

comment on table pedido_de_detalle is
  'El Motor (decisión 33 del usuario): el pedido del detalle de una tarea que la persona no ve, quién lo decide (el encargado del sector de la tarea) y cómo terminó. Cambia de estado sólo hacia adelante.';
comment on table tarea_compartida is
  'El Motor (decisión 33 del usuario): una tarea compartida con alguien que no la veía, quién la compartió (el encargado del sector de la tarea) y cuándo. Cuenta para ver la página (puede_ver_tarea). Sólo se revoca, una vez; nunca se borra.';

-- Los apodos (migración 0055; ADR 0020): cómo le dicen en el equipo a un integrante, con las
-- palabras normalizadas como el código compara los nombres; quién lo enseñó, cuándo y por qué
-- canal. Varios por persona; uno puede ser de dos personas. Se deja de usar, nunca se borra.
create table apodo (
  id                        uuid primary key default gen_random_uuid(),
  workspace_id              uuid not null references workspace(id) on delete cascade,
  membership_id             uuid not null,
  apodo                     text not null,
  ensenado_por_app_user_id  uuid not null references app_user(id),
  canal                     text not null check (canal in ('chat', 'plataforma')),
  at                        timestamptz not null,
  borrado_en                timestamptz,
  borrado_por_app_user_id   uuid references app_user(id),
  constraint apodo_de_un_integrante
    foreign key (workspace_id, membership_id) references membership(workspace_id, id)
    on delete cascade,
  -- Las palabras normalizadas, separadas por un solo espacio: nada que actúe como comodín.
  constraint apodo_normalizado check (apodo ~ '^[^ ]+( [^ ]+)*$'),
  constraint apodo_borrado check ((borrado_en is null) = (borrado_por_app_user_id is null))
);

-- Vigente, uno por persona y apodo; el mismo apodo puede ser de dos personas.
create unique index apodo_vigente on apodo (workspace_id, membership_id, apodo)
  where borrado_en is null;

comment on table apodo is
  'El Motor (ADR 0020): cómo le dicen en el equipo a un integrante, con las palabras normalizadas como el código compara los nombres; quién lo enseñó, cuándo y por qué canal (chat o plataforma). Sirve para entender, nunca para hablar ni para conceder nada. Sólo se deja de usar, una vez; nunca se borra.';

comment on table task_forecast is
  'El Motor (ADR 0018, 9b y 9f): las previsiones de una tarea. Sólo se agregan; una corrección reemplaza a otra con una fila nueva. El atraso lo calcula el código en días hábiles del espacio.';
comment on table blocker_unblocker is
  'El Motor (ADR 0018, 9c): quién destraba un bloqueo -- un integrante, alguien de afuera o que no se sabe, exactamente uno --, quién lo dijo y cuándo. Sólo se agrega.';
comment on table dicho_de_quien_destraba is
  'El Motor (C-5, decisión 4; ADR 0017, 3a): lo que dice quien destraba un bloqueo cuando Leda le pregunta -- para cuándo, que ya está o sus palabras, al menos uno --, quién lo dijo y cuándo. No cierra el bloqueo. Sólo se agrega.';
comment on column dicho_de_quien_destraba.no_le_corresponde is
  'El Motor (C-5, decisión 5): quien destraba dice que no le corresponde. Nunca junto con para cuándo ni con que ya está; a quién le toca, si lo dice, es otra fila de blocker_unblocker dicha por esa persona.';
comment on column dicho_de_quien_destraba.espera_su_bloqueo_id is
  'El Motor (C-5, decisión 6): quien destraba dice que está trabado con algo suyo, este bloqueo, del mismo espacio. Enlaza los dos bloqueos: lo que pasa con éste le llega, como información, a quien espera más abajo.';

-- Los archivos recibidos por chat (ADR 0019, decisiones 2 a 4; migración 0033).
-- `archivo` es del dominio: el contenido con su huella, sin ningún identificador
-- del canal (frontera, regla 2), aparte de `evidence` para que ninguna lectura
-- arrastre el contenido. La base garantiza la huella y el tamaño (60 MB, el
-- límite del producto), un archivo por huella y espacio, nunca compartido, y que
-- nada se modifica ni se borra: `leda_app` sólo agrega y lee, y un disparador
-- rechaza el resto (`rechazar_cambios_de_archivo`). La única excepción
-- (decisión 57; migración 0053): la administración borra el contenido de un
-- archivo que retiró; queda la huella y la hora del retiro
-- (`contenido_retirado_en`), sin vuelta atrás.
create table archivo (
  id                         uuid primary key default gen_random_uuid(),
  workspace_id               uuid not null references workspace(id) on delete cascade,
  contenido                  bytea,
  sha256                     text not null,
  tamano                     bigint not null,
  tipo                       text not null,
  clase                      text not null,
  nombre_original            text,
  enviado_por_membership_id  uuid not null references membership(id),
  recibido_en                timestamptz not null,
  contenido_retirado_en      timestamptz,
  constraint archivo_workspace_id_unique unique (workspace_id, id),
  constraint archivo_unico_por_huella unique (workspace_id, sha256),
  constraint archivo_huella_del_contenido
    check (contenido is null or sha256 = encode(sha256(contenido), 'hex')),
  constraint archivo_tamano_del_contenido
    check (tamano between 1 and 62914560
           and (contenido is null or tamano = octet_length(contenido))),
  constraint archivo_contenido_o_su_retiro
    check ((contenido is null) = (contenido_retirado_en is not null)),
  constraint archivo_clase check (
    clase in ('imagen', 'video', 'pdf', 'documento', 'texto', 'comprimido')),
  constraint archivo_nombre_original check (
    btrim(nombre_original) <> '' and char_length(nombre_original) <= 255)
);

-- Del lado del transporte: qué archivo trajo cada mensaje entrante, con los
-- identificadores de Telegram (como `inbound_message` guarda el `chat_id`). Un
-- álbum es un solo mensaje: todas sus fotos apuntan al mismo entrante, cada una
-- con su número de mensaje de Telegram y el grupo del álbum. Lo que llegó y no se
-- guardó (demasiado grande o de un tipo fuera de la lista) queda con su motivo:
-- nunca se descarta en silencio. `at` es la hora de la base, como la del
-- entrante: con ella se mide la espera corta de un álbum.
create table archivo_de_mensaje (
  id                       uuid primary key default gen_random_uuid(),
  workspace_id             uuid not null references workspace(id) on delete cascade,
  inbound_message_id       uuid not null references inbound_message(id) on delete cascade,
  archivo_id               uuid,
  que_llego                text not null,
  nombre_original          text,
  rechazo                  text,
  telegram_message_id      bigint not null,
  telegram_file_id         text not null,
  telegram_file_unique_id  text not null,
  telegram_media_group_id  text,
  at                       timestamptz not null default now(),
  constraint archivo_de_mensaje_archivo
    foreign key (workspace_id, archivo_id) references archivo(workspace_id, id),
  constraint archivo_de_mensaje_unico_por_mensaje
    unique (inbound_message_id, telegram_message_id),
  constraint archivo_de_mensaje_que_llego check (que_llego in ('foto', 'video', 'archivo')),
  constraint archivo_de_mensaje_rechazo check (
    rechazo in ('demasiado_grande', 'tipo_no_admitido', 'contenido_retirado')),
  constraint archivo_de_mensaje_guardado_o_rechazado check (
    (archivo_id is null) <> (rechazo is null))
);

create index archivo_de_mensaje_por_album on archivo_de_mensaje (telegram_media_group_id)
  where telegram_media_group_id is not null;

comment on table archivo is
  'ADR 0019, decisiones 2 y 3: el contenido de cada archivo recibido, con su huella (la garantiza la base). Un archivo por huella y espacio. Sólo se agrega: no se modifica ni se borra.';
comment on column archivo.contenido_retirado_en is
  'Decisión 57 del usuario (porción 5b; migración 0053): cuándo la administración borró el contenido de este archivo al retirarlo. Desde entonces `contenido` es nulo y la fila guarda la huella, para reconocerlo si alguien lo vuelve a mandar. No tiene vuelta atrás.';
comment on table archivo_de_mensaje is
  'ADR 0019, decisión 4: qué archivo trajo cada mensaje entrante, con los identificadores de Telegram, o por qué no se guardó. Un álbum es un solo mensaje.';

-- La evidencia de la entrega (ADR 0019, decisiones 3 a 5; migración 0034). Una
-- pieza que es una imagen o un archivo apunta a `archivo`, con el espacio.
alter table evidence
  add constraint evidence_archivo
    foreign key (workspace_id, archivo_id) references archivo(workspace_id, id);

-- "No, esa foto no era": el retiro de una pieza, por quien la entregó y mientras
-- la tarea no está aprobada. Sólo se agrega: la pieza no se borra, deja de contar.
create table evidencia_retirada (
  id                          uuid primary key default gen_random_uuid(),
  workspace_id                uuid not null references workspace(id) on delete cascade,
  evidence_id                 uuid not null,
  -- Quien la entregó, o la administración de plataforma que retiró su contenido (porción 5;
  -- migración 0052): exactamente uno de los dos.
  retirada_por_membership_id  uuid references membership(id),
  retirada_por_app_user_id    uuid references app_user(id),
  motivo                      text,
  at                          timestamptz not null default clock_timestamp(),
  constraint evidencia_retirada_evidence
    foreign key (workspace_id, evidence_id) references evidence(workspace_id, id)
    on delete cascade,
  constraint evidencia_retirada_de_quien
    check ((retirada_por_membership_id is null) <> (retirada_por_app_user_id is null))
);

-- Una vez por quien la entregó y una vez por la administración.
create unique index evidencia_retirada_una_vez_por_quien_la_entrego
  on evidencia_retirada (evidence_id) where retirada_por_membership_id is not null;
create unique index evidencia_retirada_una_vez_por_la_administracion
  on evidencia_retirada (evidence_id) where retirada_por_app_user_id is not null;

-- Lo que la persona dijo que es de una tarea antes de entregarla ("es del PLC"). No
-- es evidencia: la vista previa de la entrega lo muestra y entra sólo si queda.
create table archivo_de_tarea (
  id                       uuid primary key default gen_random_uuid(),
  workspace_id             uuid not null references workspace(id) on delete cascade,
  archivo_id               uuid not null,
  task_id                  uuid not null,
  dicho_por_membership_id  uuid not null references membership(id),
  at                       timestamptz not null,
  constraint archivo_de_tarea_archivo
    foreign key (workspace_id, archivo_id) references archivo(workspace_id, id),
  constraint archivo_de_tarea_task
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade
);

create index archivo_de_tarea_de on archivo_de_tarea (task_id, at);

comment on table evidencia_retirada is
  'ADR 0019, decisión 3: una pieza de evidencia retirada por quien la entregó (retirada_por_membership_id), mientras la tarea no está aprobada, o su contenido retirado por la administración de plataforma (retirada_por_app_user_id, porción 5): una vez cada uno. Sólo se agrega; la evidencia no se borra, deja de contar para la política y de lo retirado no se muestra el contenido.';
comment on table archivo_de_tarea is
  'ADR 0019, decisión 4: un archivo que la persona dijo que es de una tarea antes de entregarla. No es evidencia: la vista previa de la entrega lo muestra y entra sólo si la persona lo deja.';

-- La salida con adjuntos (migración 0035; ADR 0019, decisión 6): los archivos que lleva
-- una fila de la salida, en orden (hasta diez: un álbum). Apunta a `archivo`, del
-- dominio, nunca a un identificador de Telegram: cómo se manda un adjunto (reusar el
-- identificador que el canal le dio al recibirlo o subir la copia propia) lo decide el
-- despachador. `message_outbox` no suma columnas (riesgo 1 de `docs/STATUS.md`). El
-- texto y su álbum son dos filas de una misma respuesta (`respuesta_grupo`), y el
-- despachador no manda el álbum antes que el texto. Sólo se agrega.
create table message_outbox_adjunto (
  id            uuid primary key default gen_random_uuid(),
  workspace_id  uuid not null references workspace(id) on delete cascade,
  outbox_id     uuid not null,
  archivo_id    uuid not null,
  orden         integer not null,
  constraint message_outbox_adjunto_outbox
    foreign key (workspace_id, outbox_id) references message_outbox(workspace_id, id)
    on delete cascade,
  constraint message_outbox_adjunto_archivo
    foreign key (workspace_id, archivo_id) references archivo(workspace_id, id),
  constraint message_outbox_adjunto_orden check (orden between 1 and 10),
  constraint message_outbox_adjunto_orden_unico unique (outbox_id, orden),
  constraint message_outbox_adjunto_archivo_unico unique (outbox_id, archivo_id)
);

comment on table message_outbox_adjunto is
  'ADR 0019, decisión 6: los archivos que lleva una fila de la salida, en orden (hasta diez, un álbum). Apunta al archivo del dominio, nunca a un identificador de Telegram: cómo se manda lo decide el despachador. Sólo se agrega.';

-- La página de la tarea y su enlace (migración 0036; ADR 0019, decisión 7). `acceso_tarea` es
-- el enlace personal a la página de una tarea, hermano de `acceso_tablero`: sólo el hash, sin
-- vencimiento, revocable, y `leda_app` sin ningún privilegio sobre la tabla. A diferencia del
-- tablero, tiene la política de aislamiento de siempre y una más, de lectura y sólo para
-- `leda_owner`, por el hash del token (`resolver_por_token`): es lo que deja encontrarlo antes de
-- saber su espacio. `vista_de_tarea` registra cada vista y cada descarga (7e).
-- `message_outbox_enlace` es la marca de la fila de la salida que lleva el enlace: el
-- despachador lo emite al mandar, y ni la salida ni el registro de turnos lo guardan.
create table acceso_tarea (
  id             uuid primary key default gen_random_uuid(),
  workspace_id   uuid not null references workspace(id) on delete cascade,
  -- De una persona del equipo o de un administrador de plataforma (porción 5; migración 0052):
  -- exactamente uno de los dos.
  membership_id  uuid,
  admin_app_user_id uuid references app_user(id),
  task_id        uuid not null,
  token_hash     text not null,
  emitido_en     timestamptz not null default now(),
  revocado_en    timestamptz,
  constraint acceso_tarea_workspace_id_unique unique (workspace_id, id),
  constraint acceso_tarea_token_unico unique (token_hash),
  constraint acceso_tarea_hash check (token_hash ~ '^[0-9a-f]{64}$'),
  constraint acceso_tarea_de_quien
    check ((membership_id is null) <> (admin_app_user_id is null)),
  constraint acceso_tarea_membership
    foreign key (workspace_id, membership_id) references membership(workspace_id, id)
    on delete cascade,
  constraint acceso_tarea_task
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade
);

create index acceso_tarea_de on acceso_tarea (task_id, membership_id);

comment on table acceso_tarea is
  'ADR 0019, decisiones 7a y 7b: el enlace personal a la página de una tarea, de una persona del equipo (membership_id) o de un administrador de plataforma (admin_app_user_id, porción 5), exactamente uno. Sólo el hash del token; sin vencimiento; el derecho a ver (o el rol de plataforma) se revalida en cada pedido. leda_app no tiene privilegios: sólo execute sobre sus funciones.';

create table vista_de_tarea (
  id               uuid primary key default gen_random_uuid(),
  workspace_id     uuid not null references workspace(id) on delete cascade,
  acceso_tarea_id  uuid not null,
  at               timestamptz not null default clock_timestamp(),
  que              text not null,
  evidence_id      uuid,
  constraint vista_de_tarea_acceso
    foreign key (workspace_id, acceso_tarea_id) references acceso_tarea(workspace_id, id)
    on delete cascade,
  constraint vista_de_tarea_evidence
    foreign key (workspace_id, evidence_id) references evidence(workspace_id, id),
  constraint vista_de_tarea_que check (
    que in ('pagina', 'archivo') and (que = 'archivo') = (evidence_id is not null))
);

comment on table vista_de_tarea is
  'ADR 0019, decisión 7e: cada vista de la página de una tarea y cada descarga de un archivo. Sólo se agrega; sin dirección ni navegador. El motor no la lee.';

create table message_outbox_enlace (
  id             uuid primary key default gen_random_uuid(),
  workspace_id   uuid not null references workspace(id) on delete cascade,
  outbox_id      uuid not null,
  task_id        uuid not null,
  membership_id  uuid not null,
  constraint message_outbox_enlace_outbox
    foreign key (workspace_id, outbox_id) references message_outbox(workspace_id, id)
    on delete cascade,
  constraint message_outbox_enlace_task
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade,
  constraint message_outbox_enlace_membership
    foreign key (workspace_id, membership_id) references membership(workspace_id, id)
    on delete cascade,
  constraint message_outbox_enlace_uno_por_fila unique (outbox_id)
);

comment on table message_outbox_enlace is
  'ADR 0019, decisión 6: la fila de la salida lleva el enlace de esta tarea para esta persona. El despachador lo emite al mandar; la base guarda sólo su hash (acceso_tarea). Sólo se agrega.';

-- Quién revisa el trabajo de una tarea (migraciones 0045 y 0046; C-7, decisiones 28 y 43): quien
-- aprueba el trabajo de quien era la tarea antes de su primer pase o, si nunca cambió de manos, el
-- de su responsable (`membership.aprobador_membership_id`), leído ahora: si la plataforma lo
-- cambia, la revisión sigue el cambio. Puede ser quien la hace ahora (la tarea de Nahuel que toma
-- Marcos la revisa Marcos). Es la única regla: el cierre, quién ve la página y la aplicación la
-- leen de acá.
create or replace function quien_revisa_la_tarea(p_task uuid)
returns uuid
language sql stable set search_path = leda, public, pg_temp as $$
  select m.aprobador_membership_id
    from task t
    join membership m on m.id = coalesce(t.era_de_membership_id, t.responsable_membership_id)
   where t.id = p_task;
$$;

-- Quién ve la página de una tarea (ADR 0019, 7b) y las funciones que la emiten y la leen
-- (7d). La regla vive acá, no en un filtro de Python: las de lectura reciben el hash del
-- token, fijan el espacio que sale de él, revalidan el derecho a ver en cada pedido y
-- devuelven sólo esa tarea (un archivo, sólo si su evidencia es de esa tarea); al terminar
-- devuelven el espacio de la transacción como estaba. `acceso_tarea_vigente` sólo la llaman
-- ellas: `leda_app` no puede usarla para fijar el espacio de otro.
create or replace function puede_ver_tarea(p_membership_id uuid, p_task_id uuid)
returns boolean
language sql stable set search_path = leda, public, pg_temp as $$
  select exists (
    select 1
      from membership m
      join task t on t.workspace_id = m.workspace_id and t.id = p_task_id
      join rol r on r.id = m.rol_id
      join area a on a.id = t.area_id
     where m.id = p_membership_id
       and m.activo
       and (t.responsable_membership_id = m.id
            or quien_revisa_la_tarea(t.id) = m.id
            or a.referente_membership_id = m.id
            or r.autoridad_final
            or exists (select 1 from approval ap
                        where ap.workspace_id = t.workspace_id
                          and ap.sujeto_tipo = 'tarea' and ap.sujeto_id = t.id
                          and ap.aprobador_membership_id = m.id)
            or exists (select 1 from tarea_compartida c
                        where c.workspace_id = t.workspace_id
                          and c.task_id = t.id and c.membership_id = m.id
                          and c.revocada_en is null)));
$$;

create or replace function emitir_acceso_tarea(
    p_membership_id uuid, p_task_id uuid, p_token_hash text)
returns uuid
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare espacio uuid;
        nuevo uuid;
begin
  if not puede_ver_tarea(p_membership_id, p_task_id) then
    return null;
  end if;
  select m.workspace_id into espacio from membership m where m.id = p_membership_id;
  insert into acceso_tarea (workspace_id, membership_id, task_id, token_hash)
       values (espacio, p_membership_id, p_task_id, p_token_hash)
    returning id into nuevo;
  return nuevo;
end $$;

create or replace function acceso_tarea_vigente(p_token_hash text)
returns acceso_tarea
language plpgsql set search_path = leda, public, pg_temp as $$
declare acceso acceso_tarea%rowtype;
begin
  if p_token_hash is null or p_token_hash !~ '^[0-9a-f]{64}$' then
    return null;
  end if;
  perform set_config('leda.token_de_tarea', p_token_hash, true);
  select * into acceso from acceso_tarea a
   where a.token_hash = p_token_hash and a.revocado_en is null;
  perform set_config('leda.token_de_tarea', '', true);
  if acceso.id is null then
    return null;
  end if;
  perform set_config('leda.workspace_id', acceso.workspace_id::text, true);
  -- El de un administrador de plataforma (porción 5) vale mientras tenga el rol; el de una
  -- persona del equipo, mientras pueda ver la tarea.
  if acceso.admin_app_user_id is not null then
    if not exists (select 1 from platform_role p
                    where p.app_user_id = acceso.admin_app_user_id
                      and p.rol = 'administrador') then
      return null;
    end if;
  elsif not puede_ver_tarea(acceso.membership_id, acceso.task_id) then
    return null;
  end if;
  return acceso;
end $$;

create or replace function leer_pagina_de_tarea(p_token_hash text)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        acceso acceso_tarea%rowtype;
        t task%rowtype;
        faltan text[];
        tipos jsonb;
        resultado jsonb;
begin
  acceso := acceso_tarea_vigente(p_token_hash);
  if acceso.id is null then
    perform set_config('leda.workspace_id', previo, true);
    return null;
  end if;
  insert into vista_de_tarea (workspace_id, acceso_tarea_id, que)
       values (acceso.workspace_id, acceso.id, 'pagina');
  -- La vista de un administrador de plataforma va además a la auditoría (ADR 0019, 7b y 7e;
  -- constitución §12), con la versión del pack del espacio; la del núcleo la pasa quien llama.
  if acceso.admin_app_user_id is not null then
    insert into audit_log (workspace_id, actor_app_user_id, actor_kind, accion, sujeto_tipo,
                           sujeto_id, detalle, pack_hash, nucleo_hash)
    values (acceso.workspace_id, acceso.admin_app_user_id, 'persona', 'ver_pagina_de_tarea',
            'task', acceso.task_id, jsonb_build_object('acceso_tarea_id', acceso.id),
            (select v.pack_hash from workspace_version v
              where v.workspace_id = acceso.workspace_id order by v.version desc limit 1),
            nullif(current_setting('leda.nucleo_hash', true), ''));
  end if;
  select * into t from task where id = acceso.task_id;
  faltan := tipos_de_evidencia_que_faltan(t.id);
  select p.tipos into tipos from task_evidence_policy p
   where p.workspace_id = t.workspace_id and p.area_id = t.area_id;
  select jsonb_build_object(
    'espacio', w.nombre,
    'zona_horaria', w.zona_horaria,
    'persona', coalesce((select u.nombre from membership m
                           join app_user u on u.id = m.app_user_id
                          where m.id = acceso.membership_id),
                        (select u.nombre from app_user u
                          where u.id = acceso.admin_app_user_id)),
    'tarea', jsonb_build_object(
      'titulo', t.titulo,
      'objetivo', (select o.titulo from objective o where o.id = t.objective_id),
      'area', (select a.nombre from area a where a.id = t.area_id),
      'responsable', (select u.nombre from membership m join app_user u on u.id = m.app_user_id
                       where m.id = t.responsable_membership_id),
      'quien_aprueba', (select u.nombre from membership m
                          join app_user u on u.id = m.app_user_id
                         where m.id = quien_revisa_la_tarea(t.id)),
      'estado', t.estado,
      'fecha_objetivo', t.fecha_objetivo,
      'criterio_aceptacion', t.criterio_aceptacion,
      'prevision', (select jsonb_build_object('fecha', f.fecha_prevista, 'quien', u.nombre,
                                              'cuando', f.at)
                      from task_forecast f
                      join membership m on m.id = f.dicho_por_membership_id
                      join app_user u on u.id = m.app_user_id
                     where f.task_id = t.id
                       and not exists (select 1 from task_forecast g where g.reemplaza_id = f.id)
                     order by f.at desc limit 1)),
    'pide', coalesce((
      select jsonb_agg(jsonb_build_object(
               'tipo', r.tipo, 'en_palabras', tipos -> r.tipo ->> 'en_palabras',
               'cubierto', not (r.tipo = any(faltan))) order by r.orden)
        from unnest(t.evidencia_requerida) with ordinality as r(tipo, orden)), '[]'::jsonb),
    'historia', coalesce((
      select jsonb_agg(h.dato order by h.cuando, h.orden) from (
        select e.at as cuando, 1 as orden,
               jsonb_build_object('que', 'estado', 'de', e.estado_anterior, 'a', e.estado_nuevo,
                                  'quien', u.nombre, 'actor', e.actor_kind, 'cuando', e.at) as dato
          from task_state_event e left join app_user u on u.id = e.actor_app_user_id
         where e.task_id = t.id
        union all
        select ap.at, 2,
               jsonb_build_object('que', case ap.decision when 'aprobado' then 'aprobacion'
                                                          else 'pedido_de_cambios' end,
                                  'quien', u.nombre, 'comentario', ap.comentario,
                                  'cuando', ap.at)
          from approval ap
          join membership m on m.id = ap.aprobador_membership_id
          join app_user u on u.id = m.app_user_id
         where ap.sujeto_tipo = 'tarea' and ap.sujeto_id = t.id
        union all
        select b.abierto_en, 3,
               jsonb_build_object('que', 'bloqueo', 'causa', b.causa, 'quien', u.nombre,
                                  'cuando', b.abierto_en, 'resuelto_en', b.resuelto_en)
          from blocker b
          left join membership m on m.id = b.abierto_por
          left join app_user u on u.id = m.app_user_id
         where b.task_id = t.id
        union all
        select f.at, 4,
               jsonb_build_object('que', 'prevision', 'fecha', f.fecha_prevista,
                                  'es_correccion', f.es_correccion, 'quien', u.nombre,
                                  'cuando', f.at)
          from task_forecast f
          join membership m on m.id = f.dicho_por_membership_id
          join app_user u on u.id = m.app_user_id
         where f.task_id = t.id
        union all
        select u.at, 5,
               jsonb_build_object('que', 'quien_destraba', 'quien', pu.nombre,
                                  'destraba', coalesce(du.nombre, u.destraba_externo),
                                  'no_sabe', u.no_sabe,
                                  'nadie_mas', u.destraba_membership_id
                                               = u.dicho_por_membership_id,
                                  'cuando', u.at)
          from blocker_unblocker u
          join blocker b on b.id = u.blocker_id
          join membership pm on pm.id = u.dicho_por_membership_id
          join app_user pu on pu.id = pm.app_user_id
          left join membership dm on dm.id = u.destraba_membership_id
          left join app_user du on du.id = dm.app_user_id
         where b.task_id = t.id
           and not u.sin_decir_quien
        union all
        select d.at, 6,
               jsonb_build_object('que', 'dicho_del_bloqueo', 'quien', pu.nombre,
                                  'para_cuando', d.para_cuando, 'ya_esta', d.ya_esta,
                                  'no_le_corresponde', d.no_le_corresponde,
                                  'lo_que_dice', d.lo_que_dice, 'cuando', d.at)
          from dicho_de_quien_destraba d
          join blocker_unblocker u on u.id = d.blocker_unblocker_id
          join blocker b on b.id = u.blocker_id
          join membership pm on pm.id = d.dicho_por_membership_id
          join app_user pu on pu.id = pm.app_user_id
         where b.task_id = t.id
        union all
        select coalesce((a.detalle ->> 'at')::timestamptz, a.at), 7,
               jsonb_build_object('que', 'asentado',
                                  'por', case a.accion
                                           when 'asentar_bloqueo_que_sigue_abierto'
                                             then 'sigue_trabada'
                                           else 'nadie_lo_toma' end,
                                  'dias_habiles', (a.detalle ->> 'dias_habiles_trabada')::int,
                                  'cuando', coalesce((a.detalle ->> 'at')::timestamptz, a.at))
          from audit_log a
          join blocker b on b.id = a.sujeto_id
         where a.sujeto_tipo = 'blocker' and b.task_id = t.id
           and a.accion in ('asentar_bloqueo_que_sigue_abierto',
                            'informar_la_cadena_del_bloqueo',
                            'asentar_la_cadena_del_bloqueo')) h), '[]'::jsonb),
    'evidencia', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', e.id, 'clase', e.clase,
               'texto', case when not r.retirada then e.texto end,
               'enlace', case when e.clase = 'enlace' and not r.retirada then e.uri end,
               'nombre', case when not r.retirada then a.nombre_original end,
               'tipo_de_archivo', a.tipo, 'cubre', e.cubre,
               'ejemplo_aceptado', e.es_ejemplo_aceptado, 'quien', u.nombre, 'cuando', e.at,
               'retirada', r.retirada, 'retirada_el', r.retirada_el,
               'retirada_por_la_administracion', r.por_la_administracion,
               'motivo_del_retiro', r.motivo_de_la_administracion)
             order by e.at, e.id)
        from evidence e
        left join archivo a on a.workspace_id = e.workspace_id and a.id = e.archivo_id
        left join membership m on m.id = e.entregado_por
        left join app_user u on u.id = m.app_user_id
        -- Retirada por quien la entregó, o su contenido por la administración: la pieza o
        -- cualquier otra del espacio con el mismo archivo (un archivo se guarda una vez por
        -- huella). De una pieza retirada no sale su contenido (ADR 0019, decisión 3). De un
        -- retiro de la administración sale el motivo, nunca quién lo hizo (decisión 59).
        cross join lateral (
          select adm.at is not null or per.at is not null as retirada,
                 coalesce(adm.at, per.at) as retirada_el,
                 adm.at is not null as por_la_administracion,
                 adm.motivo as motivo_de_la_administracion
            from (select min(x.at) as at,
                         (array_agg(x.motivo order by x.at, x.id))[1] as motivo
                    from evidencia_retirada x
                    join evidence o on o.id = x.evidence_id
                   where x.retirada_por_app_user_id is not null
                     and (o.id = e.id
                          or (e.archivo_id is not null and o.workspace_id = e.workspace_id
                              and o.archivo_id = e.archivo_id))) adm,
                 (select min(x.at) as at from evidencia_retirada x
                   where x.evidence_id = e.id
                     and x.retirada_por_membership_id is not null) per) r
       where e.task_id = t.id), '[]'::jsonb))
    into resultado
    from workspace w where w.id = acceso.workspace_id;
  perform set_config('leda.workspace_id', previo, true);
  return resultado;
end $$;

create or replace function leer_archivo_de_tarea(p_token_hash text, p_evidence_id uuid)
returns table (archivo_contenido bytea, archivo_tipo text, archivo_clase text,
               archivo_nombre text)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        acceso acceso_tarea%rowtype;
        v_contenido bytea;
        v_tipo text;
        v_clase text;
        v_nombre text;
begin
  acceso := acceso_tarea_vigente(p_token_hash);
  if acceso.id is not null then
    select a.contenido, a.tipo, a.clase, a.nombre_original
      into v_contenido, v_tipo, v_clase, v_nombre
      from evidence e
      join archivo a on a.workspace_id = e.workspace_id and a.id = e.archivo_id
     where e.id = p_evidence_id
       and e.workspace_id = acceso.workspace_id
       and e.task_id = acceso.task_id
       and not exists (select 1 from evidencia_retirada x where x.evidence_id = e.id)
       -- Un archivo cuyo contenido retiró la administración no se sirve por ninguna pieza.
       and not exists (select 1 from evidencia_retirada x
                         join evidence o on o.id = x.evidence_id
                        where x.retirada_por_app_user_id is not null
                          and o.workspace_id = e.workspace_id
                          and o.archivo_id = e.archivo_id);
    if v_contenido is not null then
      insert into vista_de_tarea (workspace_id, acceso_tarea_id, que, evidence_id)
           values (acceso.workspace_id, acceso.id, 'archivo', p_evidence_id);
    -- La vista de un administrador de plataforma va además a la auditoría (ADR 0019, 7b y 7e;
    -- constitución §12), con la versión del pack del espacio; la del núcleo la pasa quien llama.
    if acceso.admin_app_user_id is not null then
      insert into audit_log (workspace_id, actor_app_user_id, actor_kind, accion, sujeto_tipo,
                             sujeto_id, detalle, pack_hash, nucleo_hash)
      values (acceso.workspace_id, acceso.admin_app_user_id, 'persona', 'bajar_archivo_de_tarea',
              'evidence', p_evidence_id, jsonb_build_object('acceso_tarea_id', acceso.id, 'task_id', acceso.task_id),
              (select v.pack_hash from workspace_version v
                where v.workspace_id = acceso.workspace_id order by v.version desc limit 1),
              nullif(current_setting('leda.nucleo_hash', true), ''));
    end if;
    end if;
  end if;
  perform set_config('leda.workspace_id', previo, true);
  if v_contenido is not null then
    return query select v_contenido, v_tipo, v_clase, v_nombre;
  end if;
end $$;

-- El enlace de un solo uso y la sesión de la puerta del equipo de la plataforma web (migración
-- 0057; ADR 0022, decisiones 4, 11 y 12). `enlace_de_entrada` es el enlace que manda Leda: sólo el
-- hash, sirve una vez y no vence por tiempo (como `acceso_tarea`); uno sin usar por persona.
-- `sesion_web` es la sesión que abre el canje: sólo el hash del token de la cookie, sin
-- vencimiento, revalidada en cada pedido y cortada sólo por un administrador, por la persona o al
-- dejar el equipo. Como `acceso_tarea`: la política de aislamiento de siempre y una de lectura
-- sólo para `leda_owner` por el hash (`resolver_por_token`), y `leda_app` sin ningún privilegio
-- sobre las tablas, sólo `execute` sobre las funciones. El espacio sale de la sesión o de la
-- membresía, nunca de quien llama; emitir, canjear y cortar quedan en `audit_log`.
create table enlace_de_entrada (
  id             uuid primary key default gen_random_uuid(),
  workspace_id   uuid not null references workspace(id) on delete cascade,
  membership_id  uuid not null,
  token_hash     text not null,
  emitido_en     timestamptz not null default now(),
  canjeado_en    timestamptz,
  anulado_en     timestamptz,
  constraint enlace_de_entrada_workspace_id_unique unique (workspace_id, id),
  constraint enlace_de_entrada_token_unico unique (token_hash),
  constraint enlace_de_entrada_hash check (token_hash ~ '^[0-9a-f]{64}$'),
  constraint enlace_de_entrada_canjeado_o_anulado
    check (canjeado_en is null or anulado_en is null),
  constraint enlace_de_entrada_membership
    foreign key (workspace_id, membership_id) references membership(workspace_id, id)
    on delete cascade
);

-- Uno sin usar por persona: emitir otro anula el anterior.
create unique index enlace_de_entrada_sin_usar on enlace_de_entrada (membership_id)
  where canjeado_en is null and anulado_en is null;

comment on table enlace_de_entrada is
  'ADR 0022, decisiones 4 y 12: el enlace de un solo uso para entrar a la web. Sólo el hash del token. Sirve una vez (canjeado_en); el que nadie usó vence a las 24 horas de emitido (0065), sin marcarlo; queda anulado si se emite otro para la misma persona o se cortan sus sesiones. leda_app no tiene privilegios: sólo execute sobre sus funciones.';

create table sesion_web (
  id               uuid primary key default gen_random_uuid(),
  workspace_id     uuid not null references workspace(id) on delete cascade,
  membership_id    uuid not null,
  enlace_id        uuid not null,
  token_hash       text not null,
  creada_en        timestamptz not null default now(),
  ultimo_uso_en    timestamptz not null default now(),
  cortada_en       timestamptz,
  motivo_de_corte  text,
  constraint sesion_web_token_unico unique (token_hash),
  constraint sesion_web_hash check (token_hash ~ '^[0-9a-f]{64}$'),
  constraint sesion_web_un_canje unique (enlace_id),
  constraint sesion_web_corte check ((cortada_en is null) = (motivo_de_corte is null)),
  constraint sesion_web_motivo check (motivo_de_corte in (
    'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_el_equipo')),
  constraint sesion_web_membership
    foreign key (workspace_id, membership_id) references membership(workspace_id, id)
    on delete cascade,
  constraint sesion_web_enlace
    foreign key (workspace_id, enlace_id) references enlace_de_entrada(workspace_id, id)
    on delete cascade
);

create index sesion_web_abierta on sesion_web (membership_id) where cortada_en is null;

comment on table sesion_web is
  'ADR 0022, decisiones 4 y 12: la sesión de la puerta del equipo que abre el canje de un enlace. Sólo el hash del token de la cookie. Sin vencimiento: se revalida en cada pedido (membresía activa) y anota su último uso; se corta (cortada_en, motivo_de_corte) y no vuelve. leda_app no tiene privilegios: sólo execute sobre sus funciones.';

-- La entrada a la web por chat (migración 0066; ADR 0022, decisión 4; decisiones del usuario del
-- 2026-10-12). `message_outbox_entrada_web` es la marca de la fila de la salida que lleva al final
-- el enlace de entrada a la web de una persona, como `message_outbox_enlace` el de la página de una
-- tarea: el despachador lo emite al mandar, y ni la salida ni el registro de turnos lo guardan.
-- `es_ofrecimiento`, si es el ofrecimiento de una sola vez. Un mensaje lleva un solo enlace.
-- `ofrecimiento_web` dice si a una persona ya se le ofreció la entrada (una sola vez): se reserva
-- al armar el turno, queda ofrecida al mandar y se libera si el envío falla sin reintento.
create table message_outbox_entrada_web (
  id               uuid primary key default gen_random_uuid(),
  workspace_id     uuid not null references workspace(id) on delete cascade,
  outbox_id        uuid not null,
  membership_id    uuid not null,
  es_ofrecimiento  boolean not null default false,
  constraint message_outbox_entrada_web_outbox
    foreign key (workspace_id, outbox_id) references message_outbox(workspace_id, id)
    on delete cascade,
  constraint message_outbox_entrada_web_membership
    foreign key (workspace_id, membership_id) references membership(workspace_id, id)
    on delete cascade,
  constraint message_outbox_entrada_web_uno_por_fila unique (outbox_id)
);

comment on table message_outbox_entrada_web is
  'ADR 0022, decisión 4: la fila de la salida lleva al final el enlace de entrada a la web de esta persona (es_ofrecimiento: el ofrecimiento de una sola vez). El despachador lo emite al mandar; la base guarda sólo su hash (enlace_de_entrada). Sólo se agrega.';

create table ofrecimiento_web (
  workspace_id   uuid not null references workspace(id) on delete cascade,
  membership_id  uuid primary key,
  reservado_en   timestamptz not null default now(),
  ofrecido_en    timestamptz,
  constraint ofrecimiento_web_membership
    foreign key (workspace_id, membership_id) references membership(workspace_id, id)
    on delete cascade
);

comment on table ofrecimiento_web is
  'Decisión 2 del usuario (2026-10-12): la entrada a la web se le ofrece a cada persona una sola vez. Se reserva al armar el turno (reservado_en), queda ofrecida al mandar (ofrecido_en) y se libera si el envío falla sin reintento.';

create or replace function auditar_acceso_web(
    p_workspace_id uuid, p_actor_app_user_id uuid, p_actor_kind tipo_actor, p_accion text,
    p_sujeto_tipo text, p_sujeto_id uuid, p_detalle jsonb)
returns void
language plpgsql set search_path = leda, public, pg_temp as $$
begin
  insert into audit_log (workspace_id, actor_app_user_id, actor_kind, accion, sujeto_tipo,
                         sujeto_id, detalle, pack_hash, nucleo_hash)
  values (p_workspace_id, p_actor_app_user_id, p_actor_kind, p_accion, p_sujeto_tipo,
          p_sujeto_id, p_detalle,
          (select v.pack_hash from workspace_version v
            where v.workspace_id = p_workspace_id order by v.version desc limit 1),
          nullif(current_setting('leda.nucleo_hash', true), ''));
end $$;

create or replace function emitir_enlace_de_entrada(
    p_membership_id uuid, p_token_hash text, p_actor_app_user_id uuid)
returns uuid
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare espacio uuid;
        nuevo uuid;
begin
  -- El espacio sale de la membresía, que la RLS acota al espacio de quien llama: una membresía
  -- de otro espacio no se encuentra, igual que una que no existe o que dejó el equipo.
  select m.workspace_id into espacio from membership m
   where m.id = p_membership_id and m.activo;
  if espacio is null then
    return null;
  end if;
  update enlace_de_entrada set anulado_en = now()
   where membership_id = p_membership_id and canjeado_en is null and anulado_en is null;
  insert into enlace_de_entrada (workspace_id, membership_id, token_hash)
       values (espacio, p_membership_id, p_token_hash)
    returning id into nuevo;
  perform auditar_acceso_web(
    espacio, p_actor_app_user_id,
    case when p_actor_app_user_id is null then 'leda' else 'persona' end::tipo_actor,
    'emitir_enlace_de_entrada', 'membership', p_membership_id,
    jsonb_build_object('enlace_id', nuevo));
  return nuevo;
end $$;

create or replace function canjear_enlace_de_entrada(
    p_token_hash text, p_sesion_token_hash text)
returns uuid
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        enlace enlace_de_entrada%rowtype;
        persona uuid;
        nueva uuid;
begin
  if p_token_hash is null or p_token_hash !~ '^[0-9a-f]{64}$'
     or p_sesion_token_hash is null or p_sesion_token_hash !~ '^[0-9a-f]{64}$' then
    return null;
  end if;
  perform set_config('leda.token_de_entrada', p_token_hash, true);
  select * into enlace from enlace_de_entrada e where e.token_hash = p_token_hash;
  perform set_config('leda.token_de_entrada', '', true);
  if enlace.id is null then
    return null;
  end if;
  perform set_config('leda.workspace_id', enlace.workspace_id::text, true);
  select m.app_user_id into persona from membership m
   where m.id = enlace.membership_id and m.activo;
  if persona is not null then
    -- Una sola vez: si llegan dos canjes a la vez, el segundo espera el candado de la fila y ya
    -- no la encuentra sin canjear. Y antes de las 24 horas de emitido (0065): vencido, no abre,
    -- igual que uno ya usado.
    update enlace_de_entrada set canjeado_en = now()
     where id = enlace.id and canjeado_en is null and anulado_en is null
       and emitido_en > now() - interval '24 hours';
    if found then
      insert into sesion_web (workspace_id, membership_id, enlace_id, token_hash)
           values (enlace.workspace_id, enlace.membership_id, enlace.id, p_sesion_token_hash)
        returning id into nueva;
      perform auditar_acceso_web(
        enlace.workspace_id, persona, 'persona', 'canjear_enlace_de_entrada', 'sesion_web',
        nueva, jsonb_build_object('enlace_id', enlace.id,
                                  'membership_id', enlace.membership_id));
    end if;
  end if;
  perform set_config('leda.workspace_id', previo, true);
  return nueva;
end $$;

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

create or replace function cortar_sesion(
    p_sesion_id uuid, p_motivo text, p_actor_app_user_id uuid)
returns boolean
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare cortada sesion_web%rowtype;
begin
  if p_motivo is null or p_motivo not in (
       'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_el_equipo') then
    raise exception 'cortar_sesion: motivo desconocido';
  end if;
  -- La RLS acota la búsqueda al espacio de quien llama: una sesión de otro espacio no se
  -- encuentra, igual que una que no existe o que ya estaba cortada.
  update sesion_web s set cortada_en = now(), motivo_de_corte = p_motivo
   where s.id = p_sesion_id and s.cortada_en is null
  returning * into cortada;
  if cortada.id is null then
    return false;
  end if;
  perform auditar_acceso_web(
    cortada.workspace_id, p_actor_app_user_id,
    case when p_actor_app_user_id is null then 'leda' else 'persona' end::tipo_actor,
    'cortar_sesion_web', 'sesion_web', cortada.id,
    jsonb_build_object('motivo', p_motivo, 'membership_id', cortada.membership_id));
  return true;
end $$;

create or replace function cortar_sesiones_de_membresia(
    p_membership_id uuid, p_motivo text, p_actor_app_user_id uuid)
returns integer
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare cortada record;
        cortadas integer := 0;
        espacio uuid;
        anulados integer;
        actor tipo_actor := case when p_actor_app_user_id is null then 'leda'
                                 else 'persona' end::tipo_actor;
begin
  if p_motivo is null or p_motivo not in (
       'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_el_equipo') then
    raise exception 'cortar_sesiones_de_membresia: motivo desconocido';
  end if;
  -- El espacio sale de la membresía, que la RLS acota al espacio de quien llama: una membresía
  -- de otro espacio no se encuentra, y no se corta ni se audita nada.
  select m.workspace_id into espacio from membership m where m.id = p_membership_id;
  if espacio is null then
    return 0;
  end if;
  -- Con las sesiones, el enlace que estaba sin usar: si se perdió el celular, el mensaje con el
  -- enlace también.
  update enlace_de_entrada e set anulado_en = now()
   where e.membership_id = p_membership_id and e.canjeado_en is null and e.anulado_en is null;
  get diagnostics anulados = row_count;
  for cortada in
    update sesion_web s set cortada_en = now(), motivo_de_corte = p_motivo
     where s.membership_id = p_membership_id and s.cortada_en is null
    returning s.id, s.workspace_id, s.membership_id
  loop
    perform auditar_acceso_web(
      cortada.workspace_id, p_actor_app_user_id, actor, 'cortar_sesion_web', 'sesion_web',
      cortada.id,
      jsonb_build_object('motivo', p_motivo, 'membership_id', cortada.membership_id));
    cortadas := cortadas + 1;
  end loop;
  -- El corte mismo, siempre: también si no había ninguna sesión abierta (0066).
  perform auditar_acceso_web(
    espacio, p_actor_app_user_id, actor, 'cortar_acceso_web', 'membership', p_membership_id,
    jsonb_build_object('motivo', p_motivo, 'sesiones_cortadas', cortadas,
                       'enlace_anulado', anulados > 0));
  return cortadas;
end $$;

-- Lo que la cocina pregunta del acceso de una persona sin leer las tablas (migración 0066):
-- si entró alguna vez y si tiene un enlace sin usar. En el espacio de quien llama.
create or replace function entro_a_la_web(p_membership_id uuid)
returns boolean
language sql stable security definer set search_path = leda, public, pg_temp as $$
  -- La RLS acota las dos lecturas al espacio de quien llama: una membresía de otro espacio da
  -- `false`, igual que una que no existe.
  select exists (select 1 from enlace_de_entrada e
                  where e.membership_id = p_membership_id and e.canjeado_en is not null)
      or exists (select 1 from sesion_web s where s.membership_id = p_membership_id);
$$;

create or replace function tiene_un_enlace_sin_usar(p_membership_id uuid)
returns boolean
language sql stable security definer set search_path = leda, public, pg_temp as $$
  -- El que un enlace nuevo deja sin servir: emitido, sin canjear ni anular (vencido o no).
  select exists (select 1 from enlace_de_entrada e
                  where e.membership_id = p_membership_id
                    and e.canjeado_en is null and e.anulado_en is null);
$$;

-- Quién ve qué en las listas de la puerta del equipo (ADR 0022, decisiones 3, 5, 11 y 13;
-- migraciones 0058 y 0060). `tareas_que_ve` es la regla, una sola y en SQL, que extiende
-- `puede_ver_tarea` de una tarea a la lista de cada vista ("tus", "sector", "equipo"). De una
-- tarea ajena, quien no ve sus atrasos (no es su responsable, el referente de su área ni la
-- autoridad final) ve lo mismo que el informe al grupo: si está trabada, y vencida sólo cuando
-- el atraso ya se habló en privado (una previsión vigente posterior al vencimiento, que también
-- ve, o el escalamiento de ese vencimiento ya salido; decisiones del usuario del 2026-10-12).
-- `vistas_de` dice qué vistas tiene
-- cada persona. Las dos corren con la RLS de quien llama y `leda_app` no las ejecuta: la web
-- llama a `tareas_de_la_sesion` y `vistas_de_la_sesion`, que sacan a la persona del hash del
-- token de la sesión (`sesion_vigente`), nunca de un dato del pedido.
create or replace function tareas_que_ve(
    p_membership_id uuid, p_vista text, p_ahora timestamptz)
returns table (task_id uuid, titulo text, estado text, fecha_objetivo timestamptz,
               asignada_en timestamptz, responsable text, area text, papel text,
               vencida boolean, bloqueo_abierto boolean, ve_la_pagina boolean,
               prevision date)
language sql stable set search_path = leda, public, pg_temp as $$
  with yo as (
    select m.id, m.workspace_id, r.autoridad_final
      from membership m
      join rol r on r.id = m.rol_id
     where m.id = p_membership_id and m.activo
  ),
  abiertas as (
    select t.id, t.workspace_id, t.titulo, t.estado, t.fecha_objetivo, t.creado_en,
           t.area_id, t.responsable_membership_id
      from task t
      join yo on yo.workspace_id = t.workspace_id
     where t.estado not in ('terminada', 'cancelada')
  ),
  -- Quién destraba hoy cada bloqueo abierto: lo último que se dijo.
  destraba as (
    select b.id as blocker_id, b.task_id, u.destraba_membership_id
      from blocker b
      join lateral (select x.destraba_membership_id from blocker_unblocker x
                     where x.blocker_id = b.id
                     order by x.at desc, x.id desc limit 1) u on true
     where b.resuelto_en is null
  ),
  -- Una tarea que espera otra: una dependencia bloqueante, o el bloqueo con el que dijo estar
  -- trabado quien destraba (`dicho_de_quien_destraba.espera_su_bloqueo_id`, 0044).
  esperas as (
    select d.destino_task_id as espera, d.origen_task_id as esperada
      from dependency d
     where d.tipo = 'bloqueante'
    union
    select b.task_id, y.task_id
      from destraba b
      join blocker_unblocker x on x.blocker_id = b.blocker_id
      join dicho_de_quien_destraba dd on dd.blocker_unblocker_id = x.id
      join blocker y on y.id = dd.espera_su_bloqueo_id
      join task o on o.id = y.task_id
     where b.destraba_membership_id = o.responsable_membership_id
       and dd.dicho_por_membership_id = o.responsable_membership_id
  ),
  filas as (
    select t.*, a.nombre as area_nombre, a.referente_membership_id,
           case
             when t.responsable_membership_id = yo.id then 'mia'
             when exists (select 1 from destraba b
                           where b.task_id = t.id and b.destraba_membership_id = yo.id)
                  or exists (select 1 from esperas e
                               join abiertas o on o.id = e.esperada
                              where e.espera = t.id and o.responsable_membership_id = yo.id)
                  or (t.estado = 'en_revision' and quien_revisa_la_tarea(t.id) = yo.id)
               then 'me_esperan'
             when exists (select 1 from esperas e
                            join abiertas w on w.id = e.espera
                           where e.esperada = t.id and w.responsable_membership_id = yo.id)
               then 'espero'
           end as papel,
           coalesce(t.responsable_membership_id = yo.id
                    or a.referente_membership_id = yo.id
                    or yo.autoridad_final, false) as ve_atrasos,
           t.estado in ('asignada', 'en_curso', 'bloqueada') as sigue,
           yo.autoridad_final as es_autoridad,
           yo.id as yo_id
      from abiertas t
      cross join yo
      join area a on a.id = t.area_id
  )
  select f.id, f.titulo, f.estado::text, f.fecha_objetivo,
         coalesce((select min(e.at) from task_state_event e
                    where e.task_id = f.id and e.estado_nuevo = 'asignada'), f.creado_en),
         u.nombre, f.area_nombre, f.papel,
         -- Ya pasó su fecha y, para quien no ve los atrasos de la tarea, el atraso ya se habló
         -- (la regla a o la b del informe al grupo).
         coalesce(f.sigue and d.hoy > d.vence
                  and (f.ve_atrasos
                       or p.fecha_prevista > d.vence
                       or exists (select 1 from scheduled_notice n
                                   where n.task_id = f.id and n.tipo = 'escalamiento'
                                     and n.estado = 'enviado'
                                     and n.hechos ->> 'vence' = to_char(d.vence, 'YYYY-MM-DD'))),
                  false),
         exists (select 1 from blocker b where b.task_id = f.id and b.resuelto_en is null),
         puede_ver_tarea(f.yo_id, f.id),
         case when f.sigue and p.fecha_prevista > d.vence then p.fecha_prevista end
    from filas f
    join workspace w on w.id = f.workspace_id
    cross join lateral (
      select (f.fecha_objetivo at time zone w.zona_horaria)::date as vence,
             (coalesce(p_ahora, now()) at time zone w.zona_horaria)::date as hoy) d
    -- La previsión vigente: la última que ninguna otra reemplaza.
    left join lateral (
      select x.fecha_prevista from task_forecast x
       where x.task_id = f.id
         and not exists (select 1 from task_forecast y where y.reemplaza_id = x.id)
       order by x.at desc limit 1) p on true
    left join membership rm on rm.id = f.responsable_membership_id
    left join app_user u on u.id = rm.app_user_id
   where case p_vista
           when 'tus' then f.papel is not null
           when 'sector' then f.referente_membership_id = f.yo_id
           when 'equipo' then f.es_autoridad
           else false
         end
   order by f.fecha_objetivo nulls last, f.titulo, f.id;
$$;

create or replace function vistas_de(p_membership_id uuid)
returns text[]
language sql stable set search_path = leda, public, pg_temp as $$
  select array['tus']
         || case when exists (select 1 from area a where a.referente_membership_id = m.id)
                 then array['sector'] else array[]::text[] end
         || case when r.autoridad_final then array['equipo'] else array[]::text[] end
    from membership m
    join rol r on r.id = m.rol_id
   where m.id = p_membership_id and m.activo;
$$;

create or replace function tareas_de_la_sesion(
    p_token_hash text, p_vista text, p_ahora timestamptz)
returns table (task_id uuid, titulo text, estado text, fecha_objetivo timestamptz,
               asignada_en timestamptz, responsable text, area text, papel text,
               vencida boolean, bloqueo_abierto boolean, ve_la_pagina boolean,
               prevision date)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare persona uuid;
begin
  if p_vista is null or p_vista not in ('tus', 'sector', 'equipo') then
    raise exception 'tareas_de_la_sesion: vista desconocida';
  end if;
  -- La persona sale de la sesión, que deja fijado su espacio; si no entra, nada.
  select s.membership_id into persona from sesion_vigente(p_token_hash) s;
  if persona is null then
    return;
  end if;
  return query select q.* from tareas_que_ve(persona, p_vista, p_ahora) q;
end $$;

-- Las terminadas de los últimos 30 días de cada vista, con quién las hizo (decisión 3 del
-- usuario, 2026-10-12; migración 0060): `terminadas_que_ve` corre con la RLS de quien llama
-- y `leda_app` no la ejecuta; la web llama a `terminadas_de_la_sesion`, con la persona de la
-- sesión.
create or replace function terminadas_que_ve(
    p_membership_id uuid, p_vista text, p_ahora timestamptz)
returns table (task_id uuid, titulo text, responsable text, area text,
               terminada_en timestamptz)
language sql stable set search_path = leda, public, pg_temp as $$
  with yo as (
    select m.id, m.workspace_id, r.autoridad_final
      from membership m
      join rol r on r.id = m.rol_id
     where m.id = p_membership_id and m.activo
  ),
  terminadas as (
    select t.id, t.titulo, t.area_id, t.responsable_membership_id,
           coalesce((select max(e.at) from task_state_event e
                      where e.task_id = t.id and e.estado_nuevo = 'terminada'),
                    t.actualizado_en) as terminada_en
      from task t
      join yo on yo.workspace_id = t.workspace_id
     where t.estado = 'terminada'
  )
  select x.id, x.titulo, u.nombre, a.nombre, x.terminada_en
    from terminadas x
    cross join yo
    join area a on a.id = x.area_id
    left join membership rm on rm.id = x.responsable_membership_id
    left join app_user u on u.id = rm.app_user_id
   where x.terminada_en >= coalesce(p_ahora, now()) - interval '30 days'
     and case p_vista
           when 'tus' then x.responsable_membership_id = yo.id
           when 'sector' then a.referente_membership_id = yo.id
           when 'equipo' then yo.autoridad_final
           else false
         end
   order by x.terminada_en desc, x.titulo, x.id;
$$;

create or replace function terminadas_de_la_sesion(
    p_token_hash text, p_vista text, p_ahora timestamptz)
returns table (task_id uuid, titulo text, responsable text, area text,
               terminada_en timestamptz)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare persona uuid;
begin
  if p_vista is null or p_vista not in ('tus', 'sector', 'equipo') then
    raise exception 'terminadas_de_la_sesion: vista desconocida';
  end if;
  -- La persona sale de la sesión, que deja fijado su espacio; si no entra, nada.
  select s.membership_id into persona from sesion_vigente(p_token_hash) s;
  if persona is null then
    return;
  end if;
  return query select q.* from terminadas_que_ve(persona, p_vista, p_ahora) q;
end $$;

create or replace function vistas_de_la_sesion(p_token_hash text)
returns table (membership_id uuid, vistas text[])
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare persona uuid;
begin
  select s.membership_id into persona from sesion_vigente(p_token_hash) s;
  if persona is null then
    return;
  end if;
  return query select persona, vistas_de(persona);
end $$;

-- La cadena de esperas de una tarea trabada (ADR 0022, decisiones 3, 13 y 18; migración 0059).
-- `esperas_que_ve` arma, para cada tarea de la vista cuyo bloqueo abierto ve la persona
-- (`tareas_que_ve`), el árbol de lo que espera hacia abajo: otra tarea abierta (una dependencia
-- bloqueante, o el bloqueo con el que dijo estar trabado quien destraba), con su título y quién la
-- tiene, o un bloqueo que no lleva a ninguna, con su causa y quién lo destraba. Corre con la RLS de
-- quien llama y `leda_app` no la ejecuta: la web llama a `esperas_de_la_sesion`, que saca a la
-- persona del hash del token de la sesión (`sesion_vigente`).
create or replace function esperas_que_ve(
    p_membership_id uuid, p_vista text, p_ahora timestamptz)
returns table (raiz uuid, ruta text, padre text, nivel integer, que text, quien text)
language sql stable set search_path = leda, public, pg_temp as $$
  with recursive
  raices as (
    select q.task_id from tareas_que_ve(p_membership_id, p_vista, p_ahora) q
     where q.bloqueo_abierto
  ),
  abiertas as (
    select t.id, t.titulo, t.responsable_membership_id
      from task t
     where t.estado not in ('terminada', 'cancelada')
  ),
  -- Quién destraba hoy cada bloqueo abierto: lo último que se dijo.
  bloqueos as (
    select b.id, b.task_id, b.causa, u.destraba_membership_id, u.destraba_externo
      from blocker b
      left join lateral (select x.destraba_membership_id, x.destraba_externo
                           from blocker_unblocker x
                          where x.blocker_id = b.id
                          order by x.at desc, x.id desc limit 1) u on true
     where b.resuelto_en is null
  ),
  -- El bloqueo con el que dijo estar trabado quien destraba (como `esperas` en la 0058).
  por_lo_dicho as (
    select b.id as blocker_id, b.task_id, y.task_id as esperada
      from bloqueos b
      join blocker_unblocker x on x.blocker_id = b.id
      join dicho_de_quien_destraba dd on dd.blocker_unblocker_id = x.id
      join blocker y on y.id = dd.espera_su_bloqueo_id
      join abiertas o on o.id = y.task_id
     where b.destraba_membership_id = o.responsable_membership_id
       and dd.dicho_por_membership_id = o.responsable_membership_id
  ),
  -- Lo que espera directamente cada tarea: otra tarea abierta, o un bloqueo que no lleva a
  -- ninguna.
  pasos as (
    select d.destino_task_id as tarea, 't' || d.origen_task_id::text as clave,
           d.origen_task_id as siguiente, o.titulo as que, u.nombre as quien
      from dependency d
      join abiertas o on o.id = d.origen_task_id
      left join membership m on m.id = o.responsable_membership_id
      left join app_user u on u.id = m.app_user_id
     where d.tipo = 'bloqueante'
    union
    select p.task_id, 't' || p.esperada::text, p.esperada, o.titulo, u.nombre
      from por_lo_dicho p
      join abiertas o on o.id = p.esperada
      left join membership m on m.id = o.responsable_membership_id
      left join app_user u on u.id = m.app_user_id
    union
    select b.task_id, 'b' || b.id::text, null::uuid, b.causa,
           coalesce(u.nombre, b.destraba_externo)
      from bloqueos b
      left join membership m on m.id = b.destraba_membership_id
      left join app_user u on u.id = m.app_user_id
     where not exists (select 1 from por_lo_dicho p where p.blocker_id = b.id)
  ),
  arbol (raiz, ruta, padre, nivel, siguiente, camino, que, quien) as (
    select r.task_id, '/' || p.clave, null::text, 1, p.siguiente, array[r.task_id],
           p.que, p.quien
      from raices r
      join pasos p on p.tarea = r.task_id
    union all
    select a.raiz, a.ruta || '/' || p.clave, a.ruta, a.nivel + 1, p.siguiente,
           a.camino || a.siguiente, p.que, p.quien
      from arbol a
      join pasos p on p.tarea = a.siguiente
     where a.nivel < 10 and not (a.siguiente = any (a.camino))
  )
  select a.raiz, a.ruta, a.padre, a.nivel, a.que, a.quien
    from arbol a
   order by a.raiz, a.ruta;
$$;

create or replace function esperas_de_la_sesion(
    p_token_hash text, p_vista text, p_ahora timestamptz)
returns table (raiz uuid, ruta text, padre text, nivel integer, que text, quien text)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare persona uuid;
begin
  if p_vista is null or p_vista not in ('tus', 'sector', 'equipo') then
    raise exception 'esperas_de_la_sesion: vista desconocida';
  end if;
  -- La persona sale de la sesión, que deja fijado su espacio; si no entra, nada.
  select s.membership_id into persona from sesion_vigente(p_token_hash) s;
  if persona is null then
    return;
  end if;
  return query select q.* from esperas_que_ve(persona, p_vista, p_ahora) q;
end $$;

-- La puerta de administración de la plataforma web (migración 0061; ADR 0022, decisiones 10, 11
-- y 12). Un administrador de plataforma abarca todos los espacios: su enlace de un solo uso y su
-- sesión son de un `app_user`, sin `workspace_id` ni política por espacio, y `leda_app` no tiene
-- ningún privilegio sobre las tablas (como `acceso_tablero`). Sólo los hashes; el enlace sirve una
-- vez y uno nuevo anula el que estaba sin usar; la sesión no vence, pero el rol `administrador`
-- se revalida en cada pedido y sin él queda cortada (`dejo_de_ser_administrador`). Emitir y cortar
-- todas las sesiones de un administrador, sólo la consola (`leda_admin`); canjear, la sesión
-- vigente y cerrar la propia, sólo la web (`leda_app`). Emitir, canjear y cortar quedan en
-- `audit_log` sin espacio.
create table enlace_de_administracion (
  id            uuid primary key default gen_random_uuid(),
  app_user_id   uuid not null references app_user(id) on delete cascade,
  token_hash    text not null,
  emitido_en    timestamptz not null default now(),
  canjeado_en   timestamptz,
  anulado_en    timestamptz,
  constraint enlace_de_administracion_token_unico unique (token_hash),
  constraint enlace_de_administracion_hash check (token_hash ~ '^[0-9a-f]{64}$'),
  constraint enlace_de_administracion_canjeado_o_anulado
    check (canjeado_en is null or anulado_en is null)
);

-- Uno sin usar por persona: emitir otro anula el anterior.
create unique index enlace_de_administracion_sin_usar on enlace_de_administracion (app_user_id)
  where canjeado_en is null and anulado_en is null;

comment on table enlace_de_administracion is
  'ADR 0022, decisiones 10 y 12: el enlace de un solo uso a la puerta de administración, de un administrador de plataforma (sin espacio: abarca todos). Sólo el hash del token. Sirve una vez; sin vencimiento por tiempo; queda anulado si se emite otro o se cortan sus sesiones. leda_app no tiene privilegios: sólo execute sobre las funciones de la web.';

create table sesion_de_administracion (
  id               uuid primary key default gen_random_uuid(),
  app_user_id      uuid not null references app_user(id) on delete cascade,
  enlace_id        uuid not null references enlace_de_administracion(id) on delete cascade,
  token_hash       text not null,
  creada_en        timestamptz not null default now(),
  ultimo_uso_en    timestamptz not null default now(),
  cortada_en       timestamptz,
  motivo_de_corte  text,
  constraint sesion_de_administracion_token_unico unique (token_hash),
  constraint sesion_de_administracion_hash check (token_hash ~ '^[0-9a-f]{64}$'),
  constraint sesion_de_administracion_un_canje unique (enlace_id),
  constraint sesion_de_administracion_corte
    check ((cortada_en is null) = (motivo_de_corte is null)),
  constraint sesion_de_administracion_motivo check (motivo_de_corte in (
    'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_de_ser_administrador'))
);

create index sesion_de_administracion_abierta on sesion_de_administracion (app_user_id)
  where cortada_en is null;

comment on table sesion_de_administracion is
  'ADR 0022, decisiones 10 y 12: la sesión de la puerta de administración que abre el canje de un enlace. Sólo el hash del token de la cookie. Sin vencimiento, pero el rol de plataforma se revalida en cada pedido: sin él queda cortada (dejo_de_ser_administrador). Una sesión cortada no vuelve. leda_app no tiene privilegios: sólo execute sobre las funciones de la web.';

-- La auditoría de la puerta, sin espacio aunque quien llama tenga uno fijado. De uso interno: no
-- la ejecuta nadie más que su dueño.
create or replace function auditar_acceso_de_administracion(
    p_actor_app_user_id uuid, p_actor_kind tipo_actor, p_accion text, p_sujeto_tipo text,
    p_sujeto_id uuid, p_detalle jsonb)
returns void
language plpgsql set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
begin
  perform set_config('leda.workspace_id', '', true);
  perform auditar_acceso_web(null, p_actor_app_user_id, p_actor_kind, p_accion, p_sujeto_tipo,
                             p_sujeto_id, p_detalle);
  perform set_config('leda.workspace_id', previo, true);
end $$;

create or replace function es_administrador_de_plataforma(p_app_user_id uuid)
returns boolean
language sql stable set search_path = leda, public, pg_temp as $$
  select exists (select 1 from platform_role p
                  where p.app_user_id = p_app_user_id and p.rol = 'administrador');
$$;

create or replace function emitir_enlace_de_administracion(
    p_app_user_id uuid, p_token_hash text, p_actor_app_user_id uuid)
returns uuid
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare nuevo uuid;
begin
  -- Sólo a quien tiene hoy el rol de administrador de plataforma.
  if p_app_user_id is null or not es_administrador_de_plataforma(p_app_user_id) then
    return null;
  end if;
  update enlace_de_administracion set anulado_en = now()
   where app_user_id = p_app_user_id and canjeado_en is null and anulado_en is null;
  insert into enlace_de_administracion (app_user_id, token_hash)
       values (p_app_user_id, p_token_hash)
    returning id into nuevo;
  perform auditar_acceso_de_administracion(
    p_actor_app_user_id,
    case when p_actor_app_user_id is null then 'leda' else 'persona' end::tipo_actor,
    'emitir_enlace_de_administracion', 'app_user', p_app_user_id,
    jsonb_build_object('enlace_id', nuevo));
  return nuevo;
end $$;

create or replace function canjear_enlace_de_administracion(
    p_token_hash text, p_sesion_token_hash text)
returns uuid
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare enlace enlace_de_administracion%rowtype;
        otorgado timestamptz;
        nueva uuid;
begin
  if p_token_hash is null or p_token_hash !~ '^[0-9a-f]{64}$'
     or p_sesion_token_hash is null or p_sesion_token_hash !~ '^[0-9a-f]{64}$' then
    return null;
  end if;
  select * into enlace from enlace_de_administracion e where e.token_hash = p_token_hash;
  if enlace.id is null then
    return null;
  end if;
  select p.otorgado_en into otorgado from platform_role p
   where p.app_user_id = enlace.app_user_id and p.rol = 'administrador';
  if otorgado is null then
    return null;
  end if;
  -- Emitido antes del otorgamiento vigente (el rol se revocó y se volvió a otorgar): no se
  -- canjea, y queda anulado.
  if enlace.emitido_en < otorgado then
    update enlace_de_administracion set anulado_en = now()
     where id = enlace.id and canjeado_en is null and anulado_en is null;
    return null;
  end if;
  -- Una sola vez: si llegan dos canjes a la vez, el segundo espera el candado de la fila y ya no
  -- la encuentra sin canjear.
  update enlace_de_administracion set canjeado_en = now()
   where id = enlace.id and canjeado_en is null and anulado_en is null;
  if not found then
    return null;
  end if;
  insert into sesion_de_administracion (app_user_id, enlace_id, token_hash)
       values (enlace.app_user_id, enlace.id, p_sesion_token_hash)
    returning id into nueva;
  perform auditar_acceso_de_administracion(
    enlace.app_user_id, 'persona', 'canjear_enlace_de_administracion',
    'sesion_de_administracion', nueva, jsonb_build_object('enlace_id', enlace.id));
  return nueva;
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

create or replace function cerrar_sesion_de_administracion(p_token_hash text)
returns boolean
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare cortada sesion_de_administracion%rowtype;
begin
  if p_token_hash is null or p_token_hash !~ '^[0-9a-f]{64}$' then
    return false;
  end if;
  -- Sólo la sesión de ese token: la web corta la propia, nunca una por su id.
  update sesion_de_administracion s set cortada_en = now(), motivo_de_corte = 'cerro_la_sesion'
   where s.token_hash = p_token_hash and s.cortada_en is null
  returning * into cortada;
  if cortada.id is null then
    return false;
  end if;
  perform auditar_acceso_de_administracion(
    cortada.app_user_id, 'persona', 'cortar_sesion_de_administracion',
    'sesion_de_administracion', cortada.id,
    jsonb_build_object('motivo', 'cerro_la_sesion', 'app_user_id', cortada.app_user_id));
  return true;
end $$;

create or replace function cortar_sesiones_de_administrador(
    p_app_user_id uuid, p_motivo text, p_actor_app_user_id uuid)
returns integer
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare cortada record;
        cortadas integer := 0;
begin
  if p_motivo is null or p_motivo not in (
       'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_de_ser_administrador') then
    raise exception 'cortar_sesiones_de_administrador: motivo desconocido';
  end if;
  -- Con las sesiones, el enlace que estaba sin usar: si se perdió el celular, el mensaje con el
  -- enlace también.
  update enlace_de_administracion e set anulado_en = now()
   where e.app_user_id = p_app_user_id and e.canjeado_en is null and e.anulado_en is null;
  for cortada in
    update sesion_de_administracion s set cortada_en = now(), motivo_de_corte = p_motivo
     where s.app_user_id = p_app_user_id and s.cortada_en is null
    returning s.id, s.app_user_id
  loop
    perform auditar_acceso_de_administracion(
      p_actor_app_user_id,
      case when p_actor_app_user_id is null then 'leda' else 'persona' end::tipo_actor,
      'cortar_sesion_de_administracion', 'sesion_de_administracion', cortada.id,
      jsonb_build_object('motivo', p_motivo, 'app_user_id', cortada.app_user_id));
    cortadas := cortadas + 1;
  end loop;
  return cortadas;
end $$;

-- La carga de una tarea desde la puerta de administración (migración 0062; ADR 0022, decisiones
-- 9, 11 y 12; ADR 0017, decisión 2). `es_dia_habil` es el día hábil del espacio en SQL, el mismo
-- que `Calendario.es_habil`: sin calendario, ningún día es hábil. `opciones_de_la_carga` y
-- `cargar_tarea` comprueban la sesión de administración (el rol de plataforma vigente) en cada
-- llamada y que el espacio exista, y fijan ellas mismas ese espacio: la RLS no les deja encontrar
-- un objetivo, una persona ni una clave de otro. Lo que no se carga (decisión 9) vuelve todo junto,
-- como datos; lo que se avisa y no bloquea, en `avisos`. La carga escribe la tarea, su evento
-- `asignada` y su auditoría en el espacio de la tarea, con quién la cargó y quién la decidió
-- (declarado por quien la carga, nunca una aprobación hecha en Leda). Quién la revisa es la regla
-- única (`quien_revisa_la_tarea`): sin nadie activo que la revise, no se carga. La fecha elegida
-- se guarda al cierre de la jornada del espacio, en su zona. `carga_de_tarea` es la clave de un
-- solo uso de cada carga, con RLS forzada y sin ningún privilegio para `leda_app`. La espera
-- (migración 0067; ADR 0023, decisión 2): la carga puede esperar a una tarea comprometida y
-- abierta del espacio, siempre bloqueante; `opciones_de_la_carga` las ofrece en `tareas`.
create table carga_de_tarea (
  id            uuid primary key default gen_random_uuid(),
  workspace_id  uuid not null references workspace(id) on delete cascade,
  clave         text not null,
  huella        text not null,
  task_id       uuid not null,
  avisos        jsonb not null default '[]'::jsonb,
  cargada_en    timestamptz not null default now(),
  constraint carga_de_tarea_clave_unica unique (workspace_id, clave),
  constraint carga_de_tarea_clave check (clave ~ '^[A-Za-z0-9_-]{16,128}$'),
  constraint carga_de_tarea_huella check (huella ~ '^[0-9a-f]{64}$'),
  constraint carga_de_tarea_avisos check (jsonb_typeof(avisos) = 'array'),
  constraint carga_de_tarea_tarea
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade
);

comment on table carga_de_tarea is
  'ADR 0022, decisiones 9 y 11: la clave de un solo uso de cada carga de una tarea desde la web, con la huella de lo cargado y sus avisos. La misma clave con los mismos datos devuelve la misma tarea; con otros, se rechaza. leda_app no tiene privilegios: sólo execute sobre cargar_tarea.';

create or replace function es_dia_habil(p_workspace_id uuid, p_fecha date)
returns boolean
language sql stable set search_path = leda, public, pg_temp as $$
  select coalesce((
    select (array['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'])
             [extract(isodow from p_fecha)::int] = any (c.dias)
           and not exists (select 1 from holiday h
                            where h.workspace_id = c.workspace_id and h.fecha = p_fecha)
      from work_calendar c
     where c.workspace_id = p_workspace_id), false);
$$;

create or replace function opciones_de_la_carga(
    p_token_hash text, p_workspace_id uuid, p_ahora timestamptz)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_administrador uuid;
        v_espacio workspace%rowtype;
        v_hoy date;
        v_desde date;
        v_hora_fin time;
        v_hasta date;
        v_resultado jsonb;
begin
  select s.app_user_id into v_administrador from sesion_de_administracion_vigente(p_token_hash) s;
  if v_administrador is null then
    return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
      jsonb_build_object('campo', 'sesion', 'motivo', 'sin_sesion')));
  end if;
  select * into v_espacio from workspace w where w.id = p_workspace_id;
  if v_espacio.id is null then
    return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
      jsonb_build_object('campo', 'espacio', 'motivo', 'no_existe')));
  end if;
  -- Desde acá, la RLS acota todo a ese espacio.
  perform set_config('leda.workspace_id', v_espacio.id::text, true);
  v_hoy := (coalesce(p_ahora, now()) at time zone v_espacio.zona_horaria)::date;
  v_hasta := (v_hoy + interval '6 months')::date;
  -- Hoy se ofrece sólo si la jornada del espacio no cerró: la tarea vence a esa hora, y cargada
  -- después nacería vencida (migración 0064).
  select c.hora_fin into v_hora_fin from work_calendar c where c.workspace_id = v_espacio.id;
  v_desde := case when v_hora_fin is not null
                       and (coalesce(p_ahora, now()) at time zone v_espacio.zona_horaria)::time
                           >= v_hora_fin
                  then v_hoy + 1 else v_hoy end;
  v_resultado := jsonb_build_object(
    'ok', true,
    'espacio', jsonb_build_object('id', v_espacio.id, 'nombre', v_espacio.nombre,
                                  'zona_horaria', v_espacio.zona_horaria),
    'hoy', v_hoy,
    'objetivos', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', o.id, 'titulo', o.titulo, 'tipo', o.tipo, 'estado', o.estado,
               'fecha_objetivo', o.fecha_objetivo) order by o.titulo, o.id)
        from objective o where o.estado in ('activo', 'propuesto')), '[]'::jsonb),
    -- Las tareas que una nueva puede esperar (migración 0067; ADR 0023, decisión 2): las
    -- comprometidas y abiertas; ni una cerrada ni una propuesta sin aprobar (punto 9).
    'tareas', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', t.id, 'titulo', t.titulo, 'estado', t.estado,
               'fecha_objetivo', (t.fecha_objetivo at time zone v_espacio.zona_horaria)::date,
               'responsable', u.nombre, 'objetivo', o.titulo) order by t.titulo, t.id)
        from task t
        join objective o on o.id = t.objective_id
        left join membership m on m.id = t.responsable_membership_id
        left join app_user u on u.id = m.app_user_id
       where t.estado in ('asignada', 'en_curso', 'bloqueada', 'en_revision')), '[]'::jsonb),
    'integrantes', coalesce((
      select jsonb_agg(jsonb_build_object(
               'membership_id', m.id, 'nombre', u.nombre, 'area_id', a.id, 'area', a.nombre,
               'autoridad_final', r.autoridad_final,
               'conectado', u.telegram_user_id is not null,
               'revisa', case when ap.id is null then null
                              else jsonb_build_object('membership_id', ap.id,
                                                      'nombre', apu.nombre) end)
             order by u.nombre, m.id)
        from membership m
        join app_user u on u.id = m.app_user_id
        join area a on a.id = m.area_id
        join rol r on r.id = m.rol_id
        left join membership ap on ap.id = m.aprobador_membership_id and ap.activo
        left join app_user apu on apu.id = ap.app_user_id
       where m.activo), '[]'::jsonb),
    'politicas', coalesce((
      select jsonb_agg(jsonb_build_object(
               'area_id', p.area_id, 'area', a.nombre,
               'evidencia_requerida', to_jsonb(p.evidencia_requerida),
               'version', p.version, 'tipos', p.tipos) order by a.nombre, a.id)
        from task_evidence_policy p join area a on a.id = p.area_id), '[]'::jsonb),
    'calendario', jsonb_build_object(
      'dias', coalesce((select to_jsonb(c.dias) from work_calendar c
                         where c.workspace_id = v_espacio.id), '[]'::jsonb),
      'hasta', v_hasta,
      'feriados', coalesce((
        select jsonb_agg(jsonb_build_object('fecha', h.fecha, 'nombre', h.nombre)
                         order by h.fecha)
          from holiday h where h.fecha between v_hoy and v_hasta), '[]'::jsonb),
      'dias_habiles', coalesce((
        select jsonb_agg(d.dia order by d.dia)
          from (select g::date as dia
                  from generate_series(v_desde, v_hasta, interval '1 day') g) d
         where es_dia_habil(v_espacio.id, d.dia)), '[]'::jsonb)));
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

create or replace function cargar_tarea(
    p_token_hash text, p_workspace_id uuid, p_objective_id uuid, p_titulo text,
    p_descripcion text, p_responsable_membership_id uuid, p_fecha date, p_criterio text,
    p_evidencia text[], p_decidio_membership_id uuid, p_clave text, p_ahora timestamptz,
    p_espera_task_id uuid default null)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_sesion uuid;
        v_administrador uuid;
        v_espacio workspace%rowtype;
        v_objetivo objective%rowtype;
        v_espera task%rowtype;
        v_responsable membership%rowtype;
        v_revisa membership%rowtype;
        v_politica task_evidence_policy%rowtype;
        v_previa carga_de_tarea%rowtype;
        v_es_autoridad boolean;
        v_conectado boolean;
        v_hoy date;
        v_hora_fin time;
        v_huella text;
        v_tarea uuid;
        v_errores jsonb := '[]'::jsonb;
        v_avisos jsonb := '[]'::jsonb;
        v_resultado jsonb;
begin
  -- La sesión, en cada llamada: sin el rol de plataforma vigente, nada.
  select s.sesion_id, s.app_user_id into v_sesion, v_administrador
    from sesion_de_administracion_vigente(p_token_hash) s;
  if v_administrador is null then
    return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
      jsonb_build_object('campo', 'sesion', 'motivo', 'sin_sesion')));
  end if;
  select * into v_espacio from workspace w where w.id = p_workspace_id;
  if v_espacio.id is null then
    return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
      jsonb_build_object('campo', 'espacio', 'motivo', 'no_existe')));
  end if;
  -- Desde acá, la RLS acota todo a ese espacio: un id de otro no se encuentra.
  perform set_config('leda.workspace_id', v_espacio.id::text, true);

  <<carga>>
  begin
    -- La clave de un solo uso: la misma carga dos veces devuelve la misma tarea.
    if nullif(btrim(p_clave), '') is null then
      v_errores := v_errores || jsonb_build_object('campo', 'clave', 'motivo', 'falta');
    elsif p_clave !~ '^[A-Za-z0-9_-]{16,128}$' then
      v_errores := v_errores || jsonb_build_object('campo', 'clave', 'motivo', 'mal_formada');
    else
      perform pg_advisory_xact_lock(hashtextextended(v_espacio.id::text || ':' || p_clave, 0));
      v_huella := encode(sha256(convert_to((jsonb_build_object(
        'administrador', v_administrador, 'objetivo', p_objective_id, 'titulo', p_titulo,
        'descripcion', p_descripcion, 'responsable', p_responsable_membership_id,
        'fecha', p_fecha, 'criterio', p_criterio, 'evidencia', to_jsonb(p_evidencia),
        'decidio', p_decidio_membership_id)
        -- La espera entra en la huella sólo si la hay: una carga sin espera tiene la huella de
        -- antes de la 0067.
        || case when p_espera_task_id is null then '{}'::jsonb
                else jsonb_build_object('espera', p_espera_task_id) end)::text,
        'UTF8')), 'hex');
      select * into v_previa from carga_de_tarea c where c.clave = p_clave;
      if v_previa.id is not null then
        if v_previa.huella = v_huella then
          v_resultado := jsonb_build_object('ok', true, 'task_id', v_previa.task_id,
                                            'avisos', v_previa.avisos, 'repetida', true);
        else
          v_resultado := jsonb_build_object('ok', false, 'errores', jsonb_build_array(
            jsonb_build_object('campo', 'clave', 'motivo', 'usada_con_otros_datos')));
        end if;
        exit carga;
      end if;
    end if;

    -- El objetivo: de este espacio y abierto.
    if p_objective_id is null then
      v_errores := v_errores || jsonb_build_object('campo', 'objetivo', 'motivo', 'falta');
    else
      select * into v_objetivo from objective o where o.id = p_objective_id for share;
      if v_objetivo.id is null then
        v_errores := v_errores || jsonb_build_object('campo', 'objetivo', 'motivo', 'no_existe');
      elsif v_objetivo.estado not in ('activo', 'propuesto') then
        v_errores := v_errores
                     || jsonb_build_object('campo', 'objetivo', 'motivo', 'no_esta_abierto');
      end if;
    end if;

    -- Los textos (los mismos topes que el borrador de una tarea).
    if nullif(btrim(p_titulo), '') is null then
      v_errores := v_errores || jsonb_build_object('campo', 'titulo', 'motivo', 'falta');
    elsif char_length(btrim(p_titulo)) > 200 then
      v_errores := v_errores || jsonb_build_object('campo', 'titulo', 'motivo', 'demasiado_largo');
    end if;
    if char_length(btrim(coalesce(p_descripcion, ''))) > 800 then
      v_errores := v_errores
                   || jsonb_build_object('campo', 'descripcion', 'motivo', 'demasiado_largo');
    end if;

    -- El responsable: integrante activo de este espacio, con alguien activo que no sea él para
    -- revisar su trabajo (la regla única: quien aprueba el trabajo del responsable).
    if p_responsable_membership_id is null then
      v_errores := v_errores || jsonb_build_object('campo', 'responsable', 'motivo', 'falta');
    else
      select * into v_responsable from membership m
       where m.id = p_responsable_membership_id and m.activo for share;
      if v_responsable.id is null then
        v_errores := v_errores || jsonb_build_object('campo', 'responsable',
                                                     'motivo', 'no_es_integrante_activo');
      else
        select * into v_revisa from membership m
         where m.id = v_responsable.aprobador_membership_id and m.activo;
        select r.autoridad_final into v_es_autoridad from rol r where r.id = v_responsable.rol_id;
        if v_revisa.id = v_responsable.id
           or (v_revisa.id is null and v_responsable.aprobador_membership_id is null
               and coalesce(v_es_autoridad, false)) then
          v_errores := v_errores || jsonb_build_object('campo', 'responsable',
                                                       'motivo', 'la_hace_y_la_revisa');
        elsif v_revisa.id is null then
          v_errores := v_errores || jsonb_build_object('campo', 'responsable',
                                                       'motivo', 'sin_quien_la_revise');
        end if;
        select u.telegram_user_id is not null into v_conectado
          from app_user u where u.id = v_responsable.app_user_id;
        if not coalesce(v_conectado, false) then
          v_avisos := v_avisos || jsonb_build_object('campo', 'responsable',
                                                     'motivo', 'sin_conectar');
        end if;
      end if;
    end if;

    -- La fecha: un día hábil del espacio, hoy o después (hoy, en su zona). Hoy, sólo si la
    -- jornada no cerró: la tarea vence al cierre y nacería vencida (migración 0064).
    v_hoy := (coalesce(p_ahora, now()) at time zone v_espacio.zona_horaria)::date;
    select c.hora_fin into v_hora_fin from work_calendar c where c.workspace_id = v_espacio.id;
    if p_fecha is null then
      v_errores := v_errores || jsonb_build_object('campo', 'fecha', 'motivo', 'falta');
    elsif p_fecha < v_hoy then
      v_errores := v_errores || jsonb_build_object('campo', 'fecha', 'motivo', 'en_el_pasado');
    elsif not es_dia_habil(v_espacio.id, p_fecha) then
      v_errores := v_errores || jsonb_build_object('campo', 'fecha', 'motivo', 'no_es_dia_habil');
    elsif p_fecha = v_hoy and v_hora_fin is not null
          and (coalesce(p_ahora, now()) at time zone v_espacio.zona_horaria)::time >= v_hora_fin then
      v_errores := v_errores || jsonb_build_object('campo', 'fecha', 'motivo', 'ya_cerro_el_dia');
    elsif v_objetivo.fecha_objetivo is not null and p_fecha > v_objetivo.fecha_objetivo then
      v_avisos := v_avisos || jsonb_build_object('campo', 'fecha',
                                                 'motivo', 'despues_del_objetivo');
    end if;

    if nullif(btrim(p_criterio), '') is null then
      v_errores := v_errores || jsonb_build_object('campo', 'criterio', 'motivo', 'falta');
    elsif char_length(btrim(p_criterio)) > 500 then
      v_errores := v_errores
                   || jsonb_build_object('campo', 'criterio', 'motivo', 'demasiado_largo');
    end if;

    -- La evidencia: la política del área del responsable tiene que conocer cada tipo (uno que no
    -- conoce no lo cubre ninguna pieza: la tarea no se cerraría nunca). Vacía, sólo si el área
    -- decidió no pedir evidencia.
    if p_evidencia is null then
      v_errores := v_errores || jsonb_build_object('campo', 'evidencia', 'motivo', 'falta');
    elsif v_responsable.id is not null then
      select * into v_politica from task_evidence_policy p
       where p.area_id = v_responsable.area_id for share;
      if v_politica.area_id is null then
        v_errores := v_errores || jsonb_build_object('campo', 'evidencia',
                                                     'motivo', 'sin_politica_del_area');
      elsif cardinality(p_evidencia) = 0 and cardinality(v_politica.evidencia_requerida) > 0 then
        v_errores := v_errores || jsonb_build_object('campo', 'evidencia', 'motivo', 'falta');
      elsif exists (select 1 from unnest(p_evidencia) e(tipo)
                     where not (e.tipo = any (v_politica.evidencia_requerida)
                                or v_politica.tipos ? e.tipo)) then
        v_errores := v_errores || jsonb_build_object('campo', 'evidencia',
                                                     'motivo', 'tipo_no_es_de_la_politica');
      end if;
    end if;

    -- Quién la decidió (ADR 0017, decisión 2): un integrante activo de este espacio.
    if p_decidio_membership_id is null then
      v_errores := v_errores || jsonb_build_object('campo', 'decidio', 'motivo', 'falta');
    elsif not exists (select 1 from membership m
                       where m.id = p_decidio_membership_id and m.activo) then
      v_errores := v_errores || jsonb_build_object('campo', 'decidio',
                                                   'motivo', 'no_es_integrante_activo');
    end if;

    -- La espera (migración 0067; ADR 0023, decisión 2; mecánica §4): opcional, una sola y
    -- siempre bloqueante, sobre una tarea comprometida y abierta de este espacio (la RLS no
    -- encuentra una de otro). Leída `for share`: no se cierra entre esta comprobación y la espera.
    if p_espera_task_id is not null then
      select * into v_espera from task t where t.id = p_espera_task_id for share;
      if v_espera.id is null then
        v_errores := v_errores || jsonb_build_object('campo', 'espera', 'motivo', 'no_existe');
      elsif v_espera.estado in ('terminada', 'cancelada') then
        v_errores := v_errores || jsonb_build_object('campo', 'espera', 'motivo', 'esta_cerrada');
      elsif v_espera.estado not in ('asignada', 'en_curso', 'bloqueada', 'en_revision') then
        -- Una propuesta sin aprobar nunca traba una tarea comprometida (ADR 0023, punto 9).
        v_errores := v_errores
                     || jsonb_build_object('campo', 'espera', 'motivo', 'no_esta_comprometida');
      end if;
    end if;

    if jsonb_array_length(v_errores) > 0 then
      v_resultado := jsonb_build_object('ok', false, 'errores', v_errores);
      exit carga;
    end if;

    -- Todo en orden: la tarea, su evento, su espera, su auditoría y su clave. Si la guarda de los
    -- ciclos salta (al cargar no puede: nadie espera todavía a la tarea nueva), no queda nada y
    -- vuelve como un rechazo más, nunca como un error crudo.
    begin
      insert into task (workspace_id, objective_id, titulo, descripcion, area_id,
                        responsable_membership_id, fecha_objetivo, criterio_aceptacion,
                        evidencia_requerida, evidencia_policy_version)
      values (v_espacio.id, v_objetivo.id, btrim(p_titulo), nullif(btrim(p_descripcion), ''),
              v_responsable.area_id, v_responsable.id,
              (p_fecha + v_hora_fin) at time zone v_espacio.zona_horaria, btrim(p_criterio),
              p_evidencia, v_politica.version)
      returning id into v_tarea;
      insert into task_state_event (task_id, estado_nuevo, actor_kind, actor_app_user_id, motivo)
      values (v_tarea, 'asignada', 'persona', v_administrador,
              'cargada desde la web por un administrador de plataforma');
      if v_espera.id is not null then
        insert into dependency (workspace_id, origen_task_id, destino_task_id, tipo)
        values (v_espacio.id, v_espera.id, v_tarea, 'bloqueante');
      end if;
      perform auditar_acceso_web(
        v_espacio.id, v_administrador, 'persona', 'cargar_tarea', 'task', v_tarea,
        jsonb_build_object(
          'origen', 'web',
          'cargada_por_app_user_id', v_administrador,
          'decidida_por_membership_id', p_decidio_membership_id,
          'decision_declarada_al_cargar', true,
          'responsable_membership_id', v_responsable.id,
          'revisa_membership_id', v_revisa.id,
          'objective_id', v_objetivo.id,
          'evidencia_policy_version', v_politica.version,
          'sesion_de_administracion_id', v_sesion,
          'avisos', v_avisos)
        || case when v_espera.id is null then '{}'::jsonb
                else jsonb_build_object('espera_task_id', v_espera.id,
                                        'espera_tipo', 'bloqueante') end);
      insert into carga_de_tarea (workspace_id, clave, huella, task_id, avisos)
      values (v_espacio.id, p_clave, v_huella, v_tarea, v_avisos);
      v_resultado := jsonb_build_object('ok', true, 'task_id', v_tarea, 'avisos', v_avisos,
                                        'repetida', false);
    exception when raise_exception then
      if sqlerrm is distinct from 'La dependencia crea un ciclo.' then
        raise;
      end if;
      v_resultado := jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'espera', 'motivo', 'haria_un_ciclo')));
    end;
  end carga;

  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

-- Los objetivos desde la web (migración 0068; ADR 0023, decisiones 1 y 5 y punto 11; mecánica §1).
-- `quien_crea_el_objetivo` resuelve la puerta: la de administración, en cualquier espacio; la del
-- equipo, sólo Dirección (el rol con autoridad final), en el suyo. `opciones_del_objetivo` ofrece
-- de qué puede colgar (un objetivo abierto que no sea operativo, con los tipos que admite), los
-- referentes de área activos para el referente, los nombres de los niveles del pack y los días
-- hábiles para la fecha. `crear_objetivo_web` crea con el patrón de `cargar_tarea`: el objetivo,
-- su evento `activo`, la auditoría `crear_objetivo` (quién y por qué puerta) y su clave de un solo
-- uso en `creacion_de_objetivo`. Migración 0069 (decisiones del usuario del 2026-10-14): el
-- objetivo lleva fecha, obligatoria, con el calendario de las tareas, y su referente es siempre un
-- referente activo de un área del espacio.
create table creacion_de_objetivo (
  id            uuid primary key default gen_random_uuid(),
  workspace_id  uuid not null references workspace(id) on delete cascade,
  clave         text not null,
  huella        text not null,
  objective_id  uuid not null,
  constraint creacion_de_objetivo_clave_unica unique (workspace_id, clave),
  constraint creacion_de_objetivo_clave check (clave ~ '^[A-Za-z0-9_-]{16,128}$'),
  constraint creacion_de_objetivo_huella check (huella ~ '^[0-9a-f]{64}$'),
  constraint creacion_de_objetivo_objetivo
    foreign key (workspace_id, objective_id) references objective(workspace_id, id)
    on delete cascade
);

comment on table creacion_de_objetivo is
  'ADR 0023, decisión 1 (migración 0068): la clave de un solo uso de cada creación de un objetivo desde la web, con la huella de lo creado. La misma clave con los mismos datos devuelve el mismo objetivo; con otros, se rechaza. leda_app no tiene privilegios: sólo execute sobre crear_objetivo_web.';

create or replace function quien_crea_el_objetivo(
    p_puerta text, p_token_hash text, p_workspace_id uuid)
returns jsonb
language plpgsql set search_path = leda, public, pg_temp as $$
declare v_sesion uuid;
        v_espacio uuid;
        v_persona uuid;
        v_usuario uuid;
        v_es_autoridad boolean;
begin
  if p_puerta = 'administracion' then
    -- El administrador de plataforma puede en cualquier espacio (ADR 0023, decisión 5).
    select s.sesion_id, s.app_user_id into v_sesion, v_usuario
      from sesion_de_administracion_vigente(p_token_hash) s;
    if v_usuario is null then
      return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'sesion', 'motivo', 'sin_sesion')));
    end if;
    select w.id into v_espacio from workspace w where w.id = p_workspace_id;
    if v_espacio is null then
      return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'espacio', 'motivo', 'no_existe')));
    end if;
  elsif p_puerta = 'equipo' then
    -- Dirección, sólo en su espacio (ADR 0023, decisión 1): el espacio sale de la sesión, y uno
    -- pedido que no es el suyo no existe para ella.
    select s.sesion_id, s.workspace_id, s.membership_id into v_sesion, v_espacio, v_persona
      from sesion_vigente(p_token_hash) s;
    if v_persona is null then
      return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'sesion', 'motivo', 'sin_sesion')));
    end if;
    if p_workspace_id is not null and p_workspace_id <> v_espacio then
      return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'espacio', 'motivo', 'no_existe')));
    end if;
    perform set_config('leda.workspace_id', v_espacio::text, true);
    select m.app_user_id, r.autoridad_final into v_usuario, v_es_autoridad
      from membership m join rol r on r.id = m.rol_id
     where m.id = v_persona and m.activo;
    if not coalesce(v_es_autoridad, false) then
      return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'sesion', 'motivo', 'sin_autoridad')));
    end if;
  else
    return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
      jsonb_build_object('campo', 'sesion', 'motivo', 'sin_sesion')));
  end if;
  -- Desde acá, la RLS acota todo a ese espacio: un id de otro no se encuentra.
  perform set_config('leda.workspace_id', v_espacio::text, true);
  return jsonb_build_object('ok', true, 'puerta', p_puerta, 'sesion_id', v_sesion,
                            'workspace_id', v_espacio, 'app_user_id', v_usuario,
                            'membership_id', v_persona);
end $$;

create or replace function opciones_del_objetivo(
    p_puerta text, p_token_hash text, p_workspace_id uuid, p_ahora timestamptz)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_quien jsonb;
        v_espacio workspace%rowtype;
        v_hoy date;
        v_desde date;
        v_hora_fin time;
        v_hasta date;
        v_resultado jsonb;
begin
  v_quien := quien_crea_el_objetivo(p_puerta, p_token_hash, p_workspace_id);
  if not (v_quien ->> 'ok')::boolean then
    perform set_config('leda.workspace_id', previo, true);
    return v_quien;
  end if;
  select * into v_espacio from workspace w where w.id = (v_quien ->> 'workspace_id')::uuid;
  -- El calendario de la carga de tareas (migraciones 0062 y 0064): hoy, en la zona del espacio,
  -- sólo si su jornada no cerró. Un objetivo puede ir más lejos que una tarea: hasta un año.
  v_hoy := (coalesce(p_ahora, now()) at time zone v_espacio.zona_horaria)::date;
  v_hasta := (v_hoy + interval '1 year')::date;
  select c.hora_fin into v_hora_fin from work_calendar c where c.workspace_id = v_espacio.id;
  v_desde := case when v_hora_fin is not null
                       and (coalesce(p_ahora, now()) at time zone v_espacio.zona_horaria)::time
                           >= v_hora_fin
                  then v_hoy + 1 else v_hoy end;
  v_resultado := jsonb_build_object(
    'ok', true,
    'espacio', jsonb_build_object('id', v_espacio.id, 'nombre', v_espacio.nombre,
                                  'zona_horaria', v_espacio.zona_horaria),
    'hoy', v_hoy,
    -- Los nombres del pack (`niveles`), sobre los del núcleo (mecánica §1).
    'niveles', jsonb_build_object('estrategico', 'objetivo estratégico', 'hito', 'hito',
                                  'operativo', 'objetivo operativo')
               || coalesce((select s.valor from workspace_setting s
                             where s.workspace_id = v_espacio.id and s.clave = 'niveles'),
                           '{}'::jsonb),
    -- Sin padre, sólo un estratégico (punto 11).
    'sin_padre', jsonb_build_array('estrategico'),
    -- De qué puede colgar: un objetivo abierto que no sea operativo (debajo de un operativo van
    -- tareas), con los tipos que admite.
    'padres', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', o.id, 'titulo', o.titulo, 'tipo', o.tipo, 'estado', o.estado,
               'fecha_objetivo', o.fecha_objetivo,
               'tipos', case o.tipo when 'estrategico' then jsonb_build_array('hito', 'operativo')
                                    else jsonb_build_array('operativo') end)
             order by o.titulo, o.id)
        from objective o
       where o.estado in ('activo', 'propuesto') and o.tipo <> 'operativo'), '[]'::jsonb),
    -- El referente: un referente activo de un área del espacio (decisión del usuario,
    -- 2026-10-14), con las áreas de las que es referente.
    'referentes', coalesce((
      select jsonb_agg(jsonb_build_object(
               'membership_id', m.id, 'nombre', u.nombre,
               'areas', (select jsonb_agg(a.nombre order by a.nombre, a.id)
                           from area a where a.referente_membership_id = m.id))
             order by u.nombre, m.id)
        from membership m
        join app_user u on u.id = m.app_user_id
       where m.activo
         and exists (select 1 from area a where a.referente_membership_id = m.id)), '[]'::jsonb),
    'calendario', jsonb_build_object(
      'dias', coalesce((select to_jsonb(c.dias) from work_calendar c
                         where c.workspace_id = v_espacio.id), '[]'::jsonb),
      'hasta', v_hasta,
      'feriados', coalesce((
        select jsonb_agg(jsonb_build_object('fecha', h.fecha, 'nombre', h.nombre)
                         order by h.fecha)
          from holiday h where h.fecha between v_hoy and v_hasta), '[]'::jsonb),
      'dias_habiles', coalesce((
        select jsonb_agg(d.dia order by d.dia)
          from (select g::date as dia
                  from generate_series(v_desde, v_hasta, interval '1 day') g) d
         where es_dia_habil(v_espacio.id, d.dia)), '[]'::jsonb)));
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

create or replace function crear_objetivo_web(
    p_puerta text, p_token_hash text, p_workspace_id uuid, p_titulo text, p_descripcion text,
    p_parent_id uuid, p_tipo text, p_referente_membership_id uuid, p_fecha date, p_clave text,
    p_ahora timestamptz)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_quien jsonb;
        v_espacio uuid;
        v_zona text;
        v_usuario uuid;
        v_padre objective%rowtype;
        v_referente membership%rowtype;
        v_previa creacion_de_objetivo%rowtype;
        v_hoy date;
        v_hora_fin time;
        v_huella text;
        v_objetivo uuid;
        v_errores jsonb := '[]'::jsonb;
        v_resultado jsonb;
begin
  -- La sesión, en cada llamada, y el espacio, fijado.
  v_quien := quien_crea_el_objetivo(p_puerta, p_token_hash, p_workspace_id);
  if not (v_quien ->> 'ok')::boolean then
    perform set_config('leda.workspace_id', previo, true);
    return v_quien;
  end if;
  v_espacio := (v_quien ->> 'workspace_id')::uuid;
  v_usuario := (v_quien ->> 'app_user_id')::uuid;
  select w.zona_horaria into v_zona from workspace w where w.id = v_espacio;

  <<creacion>>
  begin
    -- La clave de un solo uso: la misma creación dos veces devuelve el mismo objetivo.
    if nullif(btrim(p_clave), '') is null then
      v_errores := v_errores || jsonb_build_object('campo', 'clave', 'motivo', 'falta');
    elsif p_clave !~ '^[A-Za-z0-9_-]{16,128}$' then
      v_errores := v_errores || jsonb_build_object('campo', 'clave', 'motivo', 'mal_formada');
    else
      perform pg_advisory_xact_lock(hashtextextended(v_espacio::text || ':' || p_clave, 0));
      v_huella := encode(sha256(convert_to(jsonb_build_object(
        'puerta', p_puerta, 'app_user_id', v_usuario,
        'membership_id', v_quien -> 'membership_id', 'titulo', p_titulo,
        'descripcion', p_descripcion, 'padre', p_parent_id, 'tipo', p_tipo,
        'referente', p_referente_membership_id, 'fecha', p_fecha)::text, 'UTF8')), 'hex');
      select * into v_previa from creacion_de_objetivo c where c.clave = p_clave;
      if v_previa.id is not null then
        if v_previa.huella = v_huella then
          v_resultado := jsonb_build_object('ok', true, 'objective_id', v_previa.objective_id,
                                            'repetida', true);
        else
          v_resultado := jsonb_build_object('ok', false, 'errores', jsonb_build_array(
            jsonb_build_object('campo', 'clave', 'motivo', 'usada_con_otros_datos')));
        end if;
        exit creacion;
      end if;
    end if;

    -- El nombre y la descripción (los topes de la tarea).
    if nullif(btrim(p_titulo), '') is null then
      v_errores := v_errores || jsonb_build_object('campo', 'titulo', 'motivo', 'falta');
    elsif char_length(btrim(p_titulo)) > 200 then
      v_errores := v_errores || jsonb_build_object('campo', 'titulo', 'motivo', 'demasiado_largo');
    end if;
    if char_length(btrim(coalesce(p_descripcion, ''))) > 800 then
      v_errores := v_errores
                   || jsonb_build_object('campo', 'descripcion', 'motivo', 'demasiado_largo');
    end if;

    -- De qué cuelga: de ninguno o de un objetivo abierto de este espacio (la RLS no encuentra uno
    -- de otro) que no sea operativo. Leído `for share`: no se cierra mientras tanto.
    if p_parent_id is not null then
      select * into v_padre from objective o where o.id = p_parent_id for share;
      if v_padre.id is null then
        v_errores := v_errores || jsonb_build_object('campo', 'padre', 'motivo', 'no_existe');
      elsif v_padre.estado not in ('activo', 'propuesto') then
        v_errores := v_errores || jsonb_build_object('campo', 'padre', 'motivo', 'no_esta_abierto');
      elsif v_padre.tipo = 'operativo' then
        v_errores := v_errores || jsonb_build_object('campo', 'padre', 'motivo', 'es_operativo');
      end if;
    end if;

    -- El tipo, según dónde cuelga (punto 11): sin padre, estratégico; de un estratégico, hito u
    -- operativo; de un hito, operativo.
    if nullif(btrim(p_tipo), '') is null then
      v_errores := v_errores || jsonb_build_object('campo', 'tipo', 'motivo', 'falta');
    elsif p_tipo not in ('estrategico', 'hito', 'operativo') then
      v_errores := v_errores || jsonb_build_object('campo', 'tipo', 'motivo', 'no_existe');
    elsif (p_parent_id is null and p_tipo <> 'estrategico')
          or (v_padre.tipo = 'estrategico' and p_tipo not in ('hito', 'operativo'))
          or (v_padre.tipo = 'hito' and p_tipo <> 'operativo') then
      v_errores := v_errores || jsonb_build_object('campo', 'tipo', 'motivo', 'no_corresponde');
    end if;

    -- El referente: un integrante activo de este espacio que sea referente de un área (decisión
    -- del usuario, 2026-10-14). Las áreas se leen `for share`: no deja de serlo mientras tanto.
    if p_referente_membership_id is null then
      v_errores := v_errores || jsonb_build_object('campo', 'referente', 'motivo', 'falta');
    else
      select * into v_referente from membership m
       where m.id = p_referente_membership_id and m.activo for share;
      if v_referente.id is null then
        v_errores := v_errores || jsonb_build_object('campo', 'referente',
                                                     'motivo', 'no_es_integrante_activo');
      else
        perform 1 from area a where a.referente_membership_id = v_referente.id for share;
        if not found then
          v_errores := v_errores || jsonb_build_object('campo', 'referente',
                                                       'motivo', 'no_es_referente_de_un_area');
        end if;
      end if;
    end if;

    -- La fecha, con el calendario de las tareas (`cargar_tarea`): un día hábil del espacio, hoy o
    -- después (hoy, en su zona), y hoy sólo si la jornada no cerró.
    v_hoy := (coalesce(p_ahora, now()) at time zone v_zona)::date;
    select c.hora_fin into v_hora_fin from work_calendar c where c.workspace_id = v_espacio;
    if p_fecha is null then
      v_errores := v_errores || jsonb_build_object('campo', 'fecha', 'motivo', 'falta');
    elsif p_fecha < v_hoy then
      v_errores := v_errores || jsonb_build_object('campo', 'fecha', 'motivo', 'en_el_pasado');
    elsif not es_dia_habil(v_espacio, p_fecha) then
      v_errores := v_errores || jsonb_build_object('campo', 'fecha', 'motivo', 'no_es_dia_habil');
    elsif p_fecha = v_hoy and v_hora_fin is not null
          and (coalesce(p_ahora, now()) at time zone v_zona)::time >= v_hora_fin then
      v_errores := v_errores || jsonb_build_object('campo', 'fecha', 'motivo', 'ya_cerro_el_dia');
    end if;

    if jsonb_array_length(v_errores) > 0 then
      v_resultado := jsonb_build_object('ok', false, 'errores', v_errores);
      exit creacion;
    end if;

    -- Todo en orden: el objetivo, su evento `activo` (el estado es la proyección; lo crea quien
    -- decide), su auditoría y su clave.
    insert into objective (workspace_id, parent_id, tipo, titulo, descripcion,
                           referente_membership_id, fecha_objetivo)
    values (v_espacio, v_padre.id, p_tipo::tipo_objetivo, btrim(p_titulo),
            nullif(btrim(p_descripcion), ''), v_referente.id, p_fecha)
    returning id into v_objetivo;
    insert into objective_state_event (objective_id, estado_nuevo, actor_kind,
                                       actor_app_user_id, motivo)
    values (v_objetivo, 'activo', 'persona', v_usuario,
            case p_puerta when 'equipo' then 'creado desde la web por Dirección'
                          else 'creado desde la web por un administrador de plataforma' end);
    perform auditar_acceso_web(
      v_espacio, v_usuario, 'persona', 'crear_objetivo', 'objective', v_objetivo,
      jsonb_build_object(
        'origen', 'web',
        'puerta', p_puerta,
        'creado_por_app_user_id', v_usuario,
        'creado_por_membership_id', v_quien -> 'membership_id',
        'tipo', p_tipo,
        'parent_id', v_padre.id,
        'referente_membership_id', v_referente.id,
        'fecha_objetivo', p_fecha)
      || case p_puerta
           when 'equipo' then jsonb_build_object('sesion_web_id', v_quien -> 'sesion_id')
           else jsonb_build_object('sesion_de_administracion_id', v_quien -> 'sesion_id') end);
    insert into creacion_de_objetivo (workspace_id, clave, huella, objective_id)
    values (v_espacio, p_clave, v_huella, v_objetivo);
    v_resultado := jsonb_build_object('ok', true, 'objective_id', v_objetivo,
                                      'repetida', false);
  end creacion;

  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

-- =========================================================================
-- Sistema
-- =========================================================================

-- El modelo NO se configura en el pack ni en el núcleo. Vive acá, editable
-- desde la consola. La clave de API vive en el archivo de secretos.
create table model_config (
  id            uuid primary key default gen_random_uuid(),
  ambito        text not null default 'global',   -- global | espacio
  workspace_id  uuid references workspace(id) on delete cascade,
  proveedor     text not null,
  modelo        text not null,
  parametros    jsonb not null default '{}',
  activo        boolean not null default true,
  check (ambito = 'global' or workspace_id is not null)
);

create unique index model_config_un_global on model_config (ambito)
  where ambito = 'global' and activo;

create table learning (
  id            uuid primary key default gen_random_uuid(),
  workspace_id  uuid references workspace(id) on delete cascade,
  contenido     text not null,
  fuente        text,
  confianza     numeric(3,2),
  alcance       text,
  aprobado_por  uuid references app_user(id),
  creado_en     timestamptz not null default now(),
  expira_en     timestamptz,
  activo        boolean not null default true
);

comment on table learning is
  'El aprendizaje ajusta cómo Leda comunica y estima. Nunca modifica autoridad ni reglas.';

create table incident (
  id                   uuid primary key default gen_random_uuid(),
  workspace_id         uuid references workspace(id) on delete set null,
  severidad            text not null,
  resumen_sanitizado   text not null,
  referencia_cruda     text,
  at                   timestamptz not null default now(),
  notificado_en        timestamptz,
  -- Aviso a la administración de plataforma (Constitución §10; T28, decisión
  -- del usuario, 2026-09-28): igual que `notificado_en` para la persona
  -- afectada, nunca queda puesto si nadie fue avisado de verdad. Lo llena
  -- `incidentes.registrar_incidente`, nunca a mano.
  notificado_admin_en  timestamptz,
  -- Trazabilidad (T2b, corrección del usuario sobre incidentes, 2026-09-25):
  -- el incidente tiene que hacer encontrable la causa, sin copiar texto de
  -- conversación. `etapa` es el punto de entrada donde se atrapó la
  -- excepción (`gateway.ETAPA_*`); `referencia_tipo`/`referencia_id` apuntan
  -- -- mismo patrón polimórfico que `audit_log.sujeto_tipo`/`sujeto_id`,
  -- sin clave foránea -- a la fila que originó esto (`inbound_message` o
  -- `pending_action`): el texto se abre desde ahí, bajo la retención por
  -- cliente de docs/ROADMAP.md, nunca copiado acá. `chat_id`/`app_user_id`
  -- ubican a quién y dónde, igual que en `inbound_message`.
  etapa                text,
  referencia_tipo      text,
  referencia_id        uuid,
  chat_id              bigint,
  app_user_id          uuid references app_user(id) on delete set null
);

-- Credencial para abrir el tablero desde un navegador, donde no existe nada de
-- la identidad que aporta Telegram. El enlace es una credencial: sólo se
-- guarda su hash, vence, y el espacio viaja adentro y no en la URL.
--
-- Sin política de aislamiento, a propósito y a diferencia del resto del
-- esquema: la búsqueda del token ocurre ANTES de saber a qué espacio
-- pertenece, así que una política por espacio no tendría contra qué comparar.
-- Lo que protege esta tabla es que nadie la consulta: `leda_app` no recibe
-- ningún privilegio sobre ella, sólo `execute` sobre las dos funciones que son
-- su única puerta.
create table acceso_tablero (
  id             uuid primary key default gen_random_uuid(),
  workspace_id   uuid not null references workspace(id) on delete cascade,
  membership_id  uuid not null references membership(id) on delete cascade,
  token_hash     text not null unique,
  emitido_en     timestamptz not null default now(),
  vence_en       timestamptz not null
);

create index acceso_tablero_vencimiento on acceso_tablero (vence_en);

revoke all on acceso_tablero from public;

-- El espacio no se recibe: sale de la membresía. Como `leda_owner` no
-- saltea la RLS, esa búsqueda queda filtrada al espacio de la sesión, así que
-- una membresía de otro cliente no se encuentra y falla idéntico a una
-- inexistente. Decir "no tenés permiso" confirmaría que existe.
create or replace function emitir_acceso_tablero(
    p_membership_id uuid, p_token_hash text, p_vence_en timestamptz)
returns uuid
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare espacio uuid;
        nuevo uuid;
begin
  select m.workspace_id into espacio
    from membership m where m.id = p_membership_id and m.activo;
  if espacio is null then
    raise exception 'acceso_tablero: no existe la membresía %', p_membership_id;
  end if;

  insert into acceso_tablero (workspace_id, membership_id, token_hash, vence_en)
       values (espacio, p_membership_id, p_token_hash, p_vence_en)
    returning id into nuevo;
  return nuevo;
end $$;

-- Devuelve filas sólo si el token existe, no venció, y la membresía sigue
-- activa. Tener un token vigente no alcanza: la autoridad se revalida en cada
-- pedido, no sólo al emitir.
--
-- El `set_config` es seguro porque el espacio sale del token, resuelto del
-- lado del servidor, y no de nada que haya aportado quien llama. Recién
-- después de fijarlo se comprueba la membresía, de modo que esa comprobación
-- ya corre acotada al espacio correcto.
create or replace function resolver_acceso_tablero(p_token_hash text)
returns table (workspace_id uuid, membership_id uuid)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare acceso acceso_tablero%rowtype;
begin
  select * into acceso from acceso_tablero a
   where a.token_hash = p_token_hash and a.vence_en > now();
  if not found then
    return;
  end if;

  perform set_config('leda.workspace_id', acceso.workspace_id::text, true);

  if not exists (select 1 from membership m
                  where m.id = acceso.membership_id and m.activo) then
    return;
  end if;

  return query select acceso.workspace_id, acceso.membership_id;
end $$;

create table audit_log (
  id                uuid primary key default gen_random_uuid(),
  at                timestamptz not null default now(),
  workspace_id      uuid references workspace(id) on delete set null,
  actor_app_user_id uuid references app_user(id),
  actor_kind        tipo_actor not null,
  accion            text not null,
  sujeto_tipo       text,
  sujeto_id         uuid,
  detalle           jsonb,
  pack_hash         text,
  nucleo_hash       text
);

create index audit_ws on audit_log (workspace_id, at desc);

-- El acceso del administrador a conversaciones también se registra.
create table conversation_access_log (
  id                  uuid primary key default gen_random_uuid(),
  at                  timestamptz not null default now(),
  admin_app_user_id   uuid not null references app_user(id),
  workspace_id        uuid not null references workspace(id),
  sujeto_app_user_id  uuid references app_user(id),
  motivo              text
);

-- =========================================================================
-- Aviso de incidentes a la administración de plataforma
--
-- Constitución §10: "Los incidentes se registran sanitizados y se avisan al
-- administrador de plataforma por su canal." T28 (decisión del usuario,
-- 2026-09-28) es la primera unidad que lo cumple: hasta acá sólo se avisaba
-- a la persona afectada (`gateway.NOTICIA_NEUTRA_INCIDENTE`) y quien
-- administra la plataforma tenía que correr `python -m leda incidentes
-- <slug>` para enterarse.
-- =========================================================================

-- Cola de salida del bot de administración. Vive aparte de `message_outbox`
-- a propósito: esa cola es por espacio (`workspace_id not null`, y
-- `destinatario_membership_id` referencia una `membership`, que también es
-- por espacio), y un administrador de plataforma no tiene por qué ser
-- integrante de ningún equipo -- se lo identifica por `platform_role` +
-- `app_user`, ambas globales. `incident_id` no lleva clave foránea a
-- propósito, mismo patrón que `incident.referencia_id`: lo llena
-- `avisar_incidente_admin` ANTES de que exista la fila de `incident` (la
-- arma la misma transacción, en ese orden, porque el texto del aviso no
-- necesita el resumen que arma Python del lado de la aplicación) y una
-- clave foránea en ese sentido rompería el insert.
-- La migración 0054 suma las respuestas del bot de administración (`es_respuesta`), que no son
-- incidentes: `incident_id` admite nulo, y una fila es exactamente una de las dos cosas.
create table admin_notice (
  id                       uuid primary key default gen_random_uuid(),
  incident_id              uuid,
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
  ultimo_error             text,
  es_respuesta             boolean not null default false,
  constraint admin_notice_incidente_o_respuesta
    check ((incident_id is null) = es_respuesta)
);

comment on table admin_notice is
  'Cola de salida del bot de administración: un aviso por incidente y por administrador de plataforma alcanzable. Sin política de aislamiento por espacio -- no tiene un único espacio dueño -- y sin concesión a leda_app: sólo la escribe avisar_incidente_admin() (security definer) y sólo la despacha leda_admin (despachador.despachar_avisos_admin).';
comment on column admin_notice.es_respuesta is
  'La respuesta del bot de administración a un pedido de un administrador (migración 0054), no un aviso de incidente: sin incident_id. Si lleva el enlace de una tarea, su marca está en admin_notice_enlace y el despachador lo emite al mandarla.';

-- La respuesta del bot de administración que lleva el enlace de una tarea (migración 0054; ADR
-- 0019, 7a y 7b): la marca, como `message_outbox_enlace` para una persona del equipo. El
-- despachador emite el acceso al mandarla (`pagina_de_tarea.emitir_para_administrador`, que
-- revalida el rol), dentro del punto de retorno del envío: la base guarda sólo su hash y un
-- envío que falla no deja ningún acceso. Sin política por espacio ni privilegio para leda_app,
-- como `admin_notice`; la tarea es del espacio de la marca (clave compuesta).
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

-- Fan-out del aviso de un incidente a cada administrador de plataforma
-- alcanzable. `security definer`, mismo motivo que `emitir_acceso_tablero`/
-- `resolver_acceso_tablero`: necesita leer `platform_role` y `audit_log`
-- (tablas globales, o sin concesión de lectura a leda_app, que leda_app
-- no puede consultar directamente -- mismo motivo por el que existe la
-- vista `integrante`) desde una sesión que puede estar acotada a un espacio,
-- o a ninguno (un incidente global, sin cliente en particular).
--
-- El texto del aviso (`p_cuerpo`) lo arma Python (`incidentes.py`) ANTES de
-- llamar acá -- decisión del usuario, 2026-09-28, corrigiendo el alcance
-- original de esta unidad: el aviso SÍ tiene que incluir qué lo disparó
-- (Constitución §2, el administrador "accede a las conversaciones privadas
-- entre Leda y los integrantes"; §10 exige avisarle sanitizado, no
-- ocultarle el disparador). Armarlo en Python, no acá, es porque necesita
-- leer `inbound_message`/`pending_action` (ya concedidas a `leda_app`,
-- sin falta de elevación) y la vista `integrante` -- nada que justifique
-- `security definer` para esa parte.
--
-- "Alcanzable" es haberle escrito al menos una vez al bot de administración
-- (`gateway.procesar_update`, canal ADMINISTRACION, `accion = 'mensaje_admin'`
-- en `audit_log`): Telegram no deja que un bot le escriba primero a alguien
-- que nunca le escribió, así que sin ese registro no hay a qué chat_id
-- mandarle nada. Se toma el chat_id del `mensaje_admin` más reciente de
-- cada administrador.
--
-- Devuelve el `app_user_id` de cada administrador AL QUE RECIÉN SE LE
-- ENCOLÓ un aviso nuevo (nunca el de uno que ya lo tenía por un
-- reprocesamiento -- `if found` después del `insert ... on conflict do
-- nothing` lo distingue): Python usa esa lista, y sólo ésa, para dejar un
-- `audit_log` por cada aviso de verdad nuevo (Constitución §12, "el acceso
-- del administrador a conversaciones también se registra").
--
-- Dedupe por incidente + administrador (`admin_notice.dedupe_key`, único):
-- reprocesar el mismo incidente no le duplica el aviso a nadie, pero cada
-- administrador alcanzable recibe el suyo -- por eso la clave combina el id
-- del incidente con el del administrador, no sólo el primero.
create function avisar_incidente_admin(
    p_incident_id uuid, p_workspace_id uuid, p_cuerpo text)
returns table(app_user_id uuid)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
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

-- =========================================================================
-- Reglas
-- =========================================================================

-- --- El espacio de un evento se deriva, no se declara ---------------------

-- Estas dos funciones NO son security definer, y eso es deliberado. Corren con
-- los privilegios de quien llama, así que la RLS de la tabla padre esconde una
-- fila de otro espacio: el select no la encuentra y el insert falla.
--
-- De ahí que el mensaje sea neutro y no nombre el identificador. Uno que dijera
-- "permiso insuficiente", o que distinguiera entre ajena e inexistente, sería
-- en sí mismo un oráculo: confirmaría que esa fila existe pero pertenece a otro
-- cliente. Un identificador ajeno tiene que fallar idéntico a uno inventado.
create or replace function derivar_espacio_evento_tarea() returns trigger as $$
begin
  select t.workspace_id into new.workspace_id
    from task t where t.id = new.task_id;
  if new.workspace_id is null then
    raise exception 'task_state_event: la tarea referida no existe';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_derivar_espacio_evento_tarea
  before insert on task_state_event
  for each row execute function derivar_espacio_evento_tarea();

create or replace function derivar_espacio_evento_objetivo() returns trigger as $$
begin
  select o.workspace_id into new.workspace_id
    from objective o where o.id = new.objective_id;
  if new.workspace_id is null then
    raise exception 'objective_state_event: el objetivo referido no existe';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_derivar_espacio_evento_objetivo
  before insert on objective_state_event
  for each row execute function derivar_espacio_evento_objetivo();

-- Misma regla para las ausencias: el espacio sale de la membresía, no de quien
-- escribe. Privilegios del llamador, así una membresía ajena falla idéntico a
-- una inexistente.
create or replace function derivar_espacio_ausencia() returns trigger as $$
begin
  select m.workspace_id into new.workspace_id
    from membership m where m.id = new.membership_id;
  if new.workspace_id is null then
    raise exception 'absence: no existe la membresía %', new.membership_id;
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_derivar_espacio_ausencia
  before insert on absence
  for each row execute function derivar_espacio_ausencia();

-- Misma regla para las previsiones del motor (migración 0031): el espacio sale de
-- la tarea, con los privilegios de quien llama.
create or replace function derivar_espacio_prevision() returns trigger as $$
begin
  select t.workspace_id into new.workspace_id
    from task t where t.id = new.task_id;
  if new.workspace_id is null then
    raise exception 'task_forecast: la tarea referida no existe';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_derivar_espacio_prevision
  before insert on task_forecast
  for each row execute function derivar_espacio_prevision();

-- Las referencias a `membership` y a `inbound_message` son al mismo espacio. No se
-- declaran como clave foránea con el espacio porque la restricción única
-- `(workspace_id, id)` de esas dos tablas es de la 0002, y volver atrás la 0002
-- dejaría de ser posible (mismo motivo que `message_outbox.entrante_id`). Esta
-- función lo comprueba con los privilegios de quien llama: con la RLS, una fila de
-- otro espacio no se encuentra y falla igual que una inventada; la conexión
-- administrativa, que no tiene RLS, compara el espacio. Recibe pares (columna,
-- tabla) y falla como una clave foránea.
create or replace function exigir_referencias_del_espacio() returns trigger as $$
declare
  fila jsonb := to_jsonb(new);
  valor uuid;
  suyo uuid;
  i integer := 0;
begin
  while i < tg_nargs loop
    valor := (fila ->> tg_argv[i])::uuid;
    if valor is not null then
      execute format('select workspace_id from %I where id = $1', tg_argv[i + 1])
        into suyo using valor;
      if suyo is distinct from new.workspace_id then
        raise exception '%: la referencia de % no existe en este espacio',
          tg_table_name, tg_argv[i] using errcode = 'foreign_key_violation';
      end if;
    end if;
    i := i + 2;
  end loop;
  return new;
end $$ language plpgsql;

create trigger trg_exigir_referencias_del_espacio
  before insert or update on conversation_question
  for each row execute function exigir_referencias_del_espacio(
    'membership_id', 'membership');
create trigger trg_exigir_referencias_del_espacio
  before insert or update on conversation_turn
  for each row execute function exigir_referencias_del_espacio(
    'membership_id', 'membership', 'inbound_message_id', 'inbound_message');
create trigger trg_exigir_referencias_del_espacio
  before insert or update on scheduled_notice
  for each row execute function exigir_referencias_del_espacio(
    'destinatario_membership_id', 'membership');
create trigger trg_exigir_referencias_del_espacio
  before insert or update on conversation_state
  for each row execute function exigir_referencias_del_espacio(
    'membership_id', 'membership');

-- Después de `trg_derivar_espacio_prevision`: los disparadores corren por orden de
-- nombre, así que el espacio ya está derivado de la tarea cuando se comprueba.
create trigger trg_exigir_referencias_del_espacio
  before insert or update on task_forecast
  for each row execute function exigir_referencias_del_espacio(
    'dicho_por_membership_id', 'membership');
create trigger trg_exigir_referencias_del_espacio
  before insert or update on blocker_unblocker
  for each row execute function exigir_referencias_del_espacio(
    'destraba_membership_id', 'membership', 'dicho_por_membership_id', 'membership');
-- Lo que dice quien destraba (migración 0042): quien lo dijo es del mismo espacio.
create trigger trg_exigir_referencias_del_espacio
  before insert or update on dicho_de_quien_destraba
  for each row execute function exigir_referencias_del_espacio(
    'dicho_por_membership_id', 'membership');

-- Un pase sólo se pide sobre una tarea asignada, en curso o trabada, de quien la tiene, y sólo
-- avanza: los datos del pedido no cambian, uno terminado no se reabre y `la_tomo` lo escribe sólo
-- el cambio de responsable (migración 0045).
create or replace function vigilar_pase_de_tarea() returns trigger as $$
declare t task%rowtype;
begin
  if tg_op = 'INSERT' then
    if new.estado not in ('esperando_decision', 'esperando_que_la_tome') then
      raise exception 'pase_de_tarea: un pase nuevo empieza esperando la decisión o que la tomen';
    end if;
    select * into t from task where id = new.task_id;
    if not found or t.responsable_membership_id is distinct from new.de_membership_id
       or t.estado not in ('asignada', 'en_curso', 'bloqueada') then
      raise exception 'pase_de_tarea: la tarea no se puede pasar';
    end if;
    return new;
  end if;
  if new.workspace_id is distinct from old.workspace_id
     or new.task_id is distinct from old.task_id
     or new.de_membership_id is distinct from old.de_membership_id
     or new.a_membership_id is distinct from old.a_membership_id
     or new.pedido_por_membership_id is distinct from old.pedido_por_membership_id
     or new.decide_membership_id is distinct from old.decide_membership_id
     or new.pedido_en is distinct from old.pedido_en then
    raise exception 'pase_de_tarea: los datos del pedido no cambian';
  end if;
  if old.estado not in ('esperando_decision', 'esperando_que_la_tome')
     and new is distinct from old then
    raise exception 'pase_de_tarea: el pase ya terminó';
  end if;
  if new.estado = 'la_tomo' and old.estado <> 'la_tomo'
     and coalesce(current_setting('leda.aplicando_pase', true), '0') <> '1' then
    raise exception 'pase_de_tarea: sólo el cambio de responsable lo da por tomado';
  end if;
  if old.estado = 'esperando_que_la_tome'
     and new.estado not in ('esperando_que_la_tome', 'la_tomo', 'no_la_tomo', 'sin_efecto',
                            'sin_respuesta') then
    raise exception 'pase_de_tarea: el pase ya se decidió';
  end if;
  if old.estado = 'esperando_decision' and new.estado in ('la_tomo', 'no_la_tomo')
     and old.decide_membership_id <> old.a_membership_id then
    raise exception 'pase_de_tarea: falta la decisión';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_vigilar_pase_de_tarea
  before insert or update on pase_de_tarea
  for each row execute function vigilar_pase_de_tarea();

-- Agregar un cambio de responsable lo aplica: comprueba que el pase espera que lo tome quien lo
-- recibe (con la decisión ya dada, o dada con su respuesta si es quien decide), que la tarea
-- sigue en manos de quien la tenía y en un estado que se pasa, deja escrito de quién era la tarea
-- antes de su primer pase y quién la revisa desde ahora (quien aprueba el trabajo de esa persona),
-- cambia la tarea y da el pase por tomado. Corre con los privilegios de `leda_owner`, que no
-- saltea la RLS: sólo ve el espacio de la transacción.
create or replace function aplicar_cambio_de_responsable() returns trigger
security definer set search_path = leda, public, pg_temp as $$
declare p pase_de_tarea%rowtype;
        t task%rowtype;
        era uuid;
begin
  select * into p from pase_de_tarea where id = new.pase_id for update;
  if not found or p.workspace_id <> new.workspace_id or p.task_id <> new.task_id then
    raise exception 'cambio_de_responsable: el pase no existe';
  end if;
  if not (p.estado = 'esperando_que_la_tome'
          or (p.estado = 'esperando_decision' and p.decide_membership_id = p.a_membership_id)) then
    raise exception 'cambio_de_responsable: el pase no espera que la tomen';
  end if;
  if new.anterior_membership_id <> p.de_membership_id
     or new.nuevo_membership_id <> p.a_membership_id
     or new.aceptado_por_membership_id <> p.a_membership_id then
    raise exception 'cambio_de_responsable: no es el pase que se pidió';
  end if;
  select * into t from task where id = new.task_id for update;
  if t.responsable_membership_id is distinct from p.de_membership_id
     or t.estado not in ('asignada', 'en_curso', 'bloqueada') then
    raise exception 'cambio_de_responsable: la tarea ya no se puede pasar';
  end if;
  era := coalesce(t.era_de_membership_id, t.responsable_membership_id);
  new.revisa_membership_id := (select m.aprobador_membership_id from membership m
                                where m.id = era);
  perform set_config('leda.aplicando_pase', '1', true);
  update task
     set responsable_membership_id = p.a_membership_id,
         era_de_membership_id = era,
         actualizado_en = new.at
   where id = t.id;
  update pase_de_tarea
     set estado = 'la_tomo', contestado_en = new.at,
         decidido_en = coalesce(decidido_en, new.at)
   where id = p.id;
  perform set_config('leda.aplicando_pase', '0', true);
  return new;
end $$ language plpgsql;

create trigger trg_aplicar_cambio_de_responsable
  before insert on cambio_de_responsable
  for each row execute function aplicar_cambio_de_responsable();

-- Un pedido del detalle lo decide el encargado del sector de la tarea, empieza esperando su
-- decisión y sólo avanza: los datos del pedido no cambian y uno terminado no se reabre
-- (migración 0050). Lo decide el encargado de ahora, nunca uno anterior (migración
-- 0051).
create or replace function vigilar_pedido_de_detalle() returns trigger as $$
declare encargado uuid;
begin
  select a.referente_membership_id into encargado
    from task t join area a on a.id = t.area_id
   where t.id = new.task_id and t.workspace_id = new.workspace_id;
  if tg_op = 'INSERT' then
    if new.estado <> 'esperando_decision' then
      raise exception 'pedido_de_detalle: un pedido nuevo espera la decisión';
    end if;
    if new.decide_membership_id is distinct from encargado then
      raise exception 'pedido_de_detalle: lo decide el encargado del sector de la tarea';
    end if;
    return new;
  end if;
  if new.workspace_id is distinct from old.workspace_id
     or new.task_id is distinct from old.task_id
     or new.pedido_por_membership_id is distinct from old.pedido_por_membership_id
     or new.decide_membership_id is distinct from old.decide_membership_id
     or new.pedido_en is distinct from old.pedido_en then
    raise exception 'pedido_de_detalle: los datos del pedido no cambian';
  end if;
  if old.estado <> 'esperando_decision' and new is distinct from old then
    raise exception 'pedido_de_detalle: el pedido ya terminó';
  end if;
  -- Lo decide el encargado de ahora del sector de la tarea, nunca uno anterior: el pedido sigue
  -- al encargado (migración 0051).
  if new.estado in ('compartida', 'no_compartida')
     and new.decidido_por_membership_id is distinct from encargado then
    raise exception 'pedido_de_detalle: lo decide el encargado de ahora del sector de la tarea';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_vigilar_pedido_de_detalle
  before insert or update on pedido_de_detalle
  for each row execute function vigilar_pedido_de_detalle();

-- Una tarea se comparte vigente y sólo la comparte el encargado del sector de la tarea; si viene
-- de un pedido, es lo que se pidió. Después, lo único que cambia es dejarla de compartir, una
-- vez, por el encargado o por quien la compartió (migración 0050).
create or replace function vigilar_tarea_compartida() returns trigger as $$
declare encargado uuid;
begin
  select a.referente_membership_id into encargado
    from task t join area a on a.id = t.area_id
   where t.id = new.task_id and t.workspace_id = new.workspace_id;
  if tg_op = 'INSERT' then
    if new.revocada_en is not null then
      raise exception 'tarea_compartida: una tarea se comparte vigente';
    end if;
    if encargado is null or new.compartida_por_membership_id is distinct from encargado then
      raise exception 'tarea_compartida: la comparte el encargado del sector de la tarea';
    end if;
    if new.pedido_id is not null and not exists (
         select 1 from pedido_de_detalle p
          where p.id = new.pedido_id and p.task_id = new.task_id
            and p.pedido_por_membership_id = new.membership_id) then
      raise exception 'tarea_compartida: no es lo que se pidió';
    end if;
    return new;
  end if;
  if new.workspace_id is distinct from old.workspace_id
     or new.task_id is distinct from old.task_id
     or new.membership_id is distinct from old.membership_id
     or new.compartida_por_membership_id is distinct from old.compartida_por_membership_id
     or new.pedido_id is distinct from old.pedido_id
     or new.at is distinct from old.at then
    raise exception 'tarea_compartida: lo compartido no cambia';
  end if;
  if old.revocada_en is not null then
    if new is distinct from old then
      raise exception 'tarea_compartida: ya se dejó de compartir';
    end if;
    return new;
  end if;
  if new.revocada_en is not null
     and new.revocada_por_membership_id is distinct from encargado
     and new.revocada_por_membership_id is distinct from old.compartida_por_membership_id then
    raise exception 'tarea_compartida: la deja de compartir el encargado del sector de la tarea';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_vigilar_tarea_compartida
  before insert or update on tarea_compartida
  for each row execute function vigilar_tarea_compartida();

-- Un apodo nace vigente y lo único que cambia después es dejarlo de usar, una vez, con quién y
-- cuándo (migración 0055).
create or replace function vigilar_apodo() returns trigger as $$
begin
  if tg_op = 'INSERT' then
    if new.borrado_en is not null then
      raise exception 'apodo: un apodo se aprende vigente';
    end if;
    return new;
  end if;
  if new.workspace_id is distinct from old.workspace_id
     or new.membership_id is distinct from old.membership_id
     or new.apodo is distinct from old.apodo
     or new.ensenado_por_app_user_id is distinct from old.ensenado_por_app_user_id
     or new.canal is distinct from old.canal
     or new.at is distinct from old.at then
    raise exception 'apodo: lo aprendido no cambia';
  end if;
  if old.borrado_en is not null and new is distinct from old then
    raise exception 'apodo: ya se dejó de usar';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_vigilar_apodo
  before insert or update on apodo
  for each row execute function vigilar_apodo();

-- Los archivos recibidos (migración 0033): quién lo mandó y el mensaje que lo trajo
-- son del mismo espacio.
create trigger trg_exigir_referencias_del_espacio
  before insert or update on archivo
  for each row execute function exigir_referencias_del_espacio(
    'enviado_por_membership_id', 'membership');
create trigger trg_exigir_referencias_del_espacio
  before insert or update on archivo_de_mensaje
  for each row execute function exigir_referencias_del_espacio(
    'inbound_message_id', 'inbound_message');

-- Un archivo recibido no se modifica ni se borra (ADR 0019, decisión 3). Es una garantía aparte
-- de los privilegios de `leda_app`: vale también para la conexión administrativa. La única
-- excepción (decisión 57; migración 0053): la conexión administrativa vacía el contenido de un
-- archivo que la administración retiró (`evidencia_retirada.retirada_por_app_user_id` de una
-- pieza con ese archivo) y anota cuándo; nada más cambia, y no se vuelve atrás. Las columnas se
-- comparan una por una para no copiar el contenido entero.
create or replace function rechazar_cambios_de_archivo() returns trigger as $$
begin
  if tg_op = 'UPDATE' and current_user = 'leda_admin'
     and old.contenido is not null and new.contenido is null
     and new.contenido_retirado_en is not null
     and (new.id, new.workspace_id, new.sha256, new.tamano, new.tipo, new.clase,
          new.nombre_original, new.enviado_por_membership_id, new.recibido_en)
         is not distinct from
         (old.id, old.workspace_id, old.sha256, old.tamano, old.tipo, old.clase,
          old.nombre_original, old.enviado_por_membership_id, old.recibido_en)
     and exists (select 1 from evidencia_retirada x
                   join evidence e on e.id = x.evidence_id
                  where x.retirada_por_app_user_id is not null
                    and e.workspace_id = old.workspace_id and e.archivo_id = old.id) then
    return new;
  end if;
  raise exception 'archivo: un archivo recibido no se modifica ni se borra (sólo la administración vacía el contenido de uno que retiró)';
end $$ language plpgsql;

create trigger trg_rechazar_cambios_de_archivo
  before update or delete on archivo
  for each row execute function rechazar_cambios_de_archivo();

-- La evidencia de la entrega (migración 0034): quien la entregó, quien la retiró y
-- quien dijo de qué tarea es un archivo son del mismo espacio.
create trigger trg_exigir_referencias_del_espacio
  before insert or update on evidence
  for each row execute function exigir_referencias_del_espacio(
    'entregado_por', 'membership');
create trigger trg_exigir_referencias_del_espacio
  before insert or update on evidencia_retirada
  for each row execute function exigir_referencias_del_espacio(
    'retirada_por_membership_id', 'membership');

-- El acceso de un administrador de plataforma a la página de una tarea y el retiro de contenido
-- por la administración (porción 5 de la C-3; migración 0052): sólo los escribe la conexión
-- administrativa y sólo para quien tiene el rol de plataforma. Vale también contra una
-- aplicación que nombre a un administrador de verdad: `leda_app` puede agregar retiros, los de
-- quien entregó la pieza. Sólo al agregar: revocar el enlace de quien ya no es administrador
-- tiene que poder hacerse.
create or replace function exigir_administrador_de_plataforma() returns trigger as $$
declare usuario uuid := (to_jsonb(new) ->> tg_argv[0])::uuid;
begin
  if usuario is not null then
    if current_user <> 'leda_admin' then
      raise exception '%: lo de un administrador de plataforma lo escribe sólo la administración',
        tg_table_name;
    end if;
    if not exists (select 1 from platform_role p
                    where p.app_user_id = usuario and p.rol = 'administrador') then
      raise exception '%: % no es administrador de plataforma', tg_table_name, tg_argv[0];
    end if;
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_exigir_administrador_de_plataforma
  before insert on acceso_tarea
  for each row execute function exigir_administrador_de_plataforma('admin_app_user_id');
create trigger trg_exigir_administrador_de_plataforma
  before insert on evidencia_retirada
  for each row execute function exigir_administrador_de_plataforma('retirada_por_app_user_id');
create trigger trg_exigir_referencias_del_espacio
  before insert or update on archivo_de_tarea
  for each row execute function exigir_referencias_del_espacio(
    'dicho_por_membership_id', 'membership');

-- La clase de una pieza que apunta a un archivo es la del archivo (ADR 0019,
-- decisión 5): `imagen` si el archivo es una imagen, `archivo` si no. La fija el
-- código por el contenido; la base no deja que diga otra.
create or replace function exigir_clase_de_la_evidencia() returns trigger as $$
declare
  del_archivo text;
begin
  if new.archivo_id is not null and new.clase in ('imagen', 'archivo') then
    select clase into del_archivo from archivo
     where workspace_id = new.workspace_id and id = new.archivo_id;
    -- Un archivo que no es de este espacio lo rechaza la clave foránea.
    if del_archivo is not null
       and (del_archivo = 'imagen') is distinct from (new.clase = 'imagen') then
      raise exception 'evidence: la clase % no es la del archivo', new.clase;
    end if;
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_exigir_clase_de_la_evidencia
  before insert or update on evidence
  for each row execute function exigir_clase_de_la_evidencia();

-- Una evidencia no se edita ni se borra (ADR 0019, decisión 3), como los eventos de
-- estado: una pieza equivocada se retira (`evidencia_retirada`), y un retiro
-- tampoco se deshace. Vale también para la conexión administrativa.
create or replace function rechazar_cambios_de_evidencia() returns trigger as $$
begin
  raise exception '%: una evidencia no se modifica ni se borra', tg_table_name;
end $$ language plpgsql;

create trigger trg_rechazar_cambios_de_evidencia
  before update or delete on evidence
  for each row execute function rechazar_cambios_de_evidencia();
create trigger trg_rechazar_cambios_de_evidencia
  before update or delete on evidencia_retirada
  for each row execute function rechazar_cambios_de_evidencia();

-- La auditoría autoritativa es la evidencia que se le muestra a un cliente. Su
-- espacio lo fija la sesión, nunca quien escribe: si otro cliente pudiera
-- atribuirse una entrada, el registro dejaría de ser evidencia. Sin espacio en
-- la sesión --la conexión administrativa-- se conserva lo suministrado, que es
-- como se registran los hechos de alcance global.
create or replace function derivar_espacio_registro() returns trigger as $$
declare actual text := nullif(current_setting('leda.workspace_id', true), '');
begin
  if actual is not null then
    new.workspace_id := actual::uuid;
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_derivar_espacio_auditoria
  before insert on audit_log
  for each row execute function derivar_espacio_registro();

create trigger trg_derivar_espacio_incidente
  before insert on incident
  for each row execute function derivar_espacio_registro();

-- --- El estado es una proyección, no un campo editable -------------------

create or replace function aplicar_evento_tarea() returns trigger
security definer set search_path = leda, public, pg_temp as $$
declare espacio_anterior text := current_setting('leda.workspace_id', true);
begin
  -- El dueño de esta función no saltea la RLS, así que este `update` queda
  -- sujeto a la política de aislamiento. Se acota al espacio del propio
  -- evento, que el disparador de derivación ya resolvió desde la tarea: no se
  -- confía en nada aportado por quien llama. Hace falta fijarlo porque la
  -- conexión administrativa no define espacio alguno, y sin esto la proyección
  -- no encontraría la fila y fallaría en silencio. El valor previo se
  -- restaura para no angostar el resto de la transacción.
  perform set_config('leda.workspace_id', new.workspace_id::text, true);
  perform set_config('leda.aplicando_evento', '1', true);
  update task
     set estado = new.estado_nuevo,
         actualizado_en = new.at
   where id = new.task_id;
  perform set_config('leda.aplicando_evento', '0', true);
  perform set_config('leda.workspace_id', coalesce(espacio_anterior, ''), true);
  return new;
end $$ language plpgsql;

create trigger trg_aplicar_evento_tarea
  after insert on task_state_event
  for each row execute function aplicar_evento_tarea();

create or replace function bloquear_estado_directo() returns trigger as $$
begin
  if new.objective_id is distinct from old.objective_id
     or new.titulo is distinct from old.titulo
     or new.descripcion is distinct from old.descripcion
     or new.area_id is distinct from old.area_id
     or new.fecha_objetivo is distinct from old.fecha_objetivo
     or new.criterio_aceptacion is distinct from old.criterio_aceptacion
     or new.evidencia_requerida is distinct from old.evidencia_requerida
     or new.evidencia_policy_version is distinct from old.evidencia_policy_version
     or new.source_draft_id is distinct from old.source_draft_id then
    raise exception 'Los campos de compromiso de una tarea son inmutables.';
  end if;
  -- Quién la tiene y de quién era cambian sólo con un pase confirmado por quien lo pidió, quien
  -- lo decidió y quien la toma (migraciones 0045 y 0046; C-7, delegar): lo aplica
  -- `aplicar_cambio_de_responsable`, al agregarse el cambio en `cambio_de_responsable`.
  if (new.responsable_membership_id is distinct from old.responsable_membership_id
      or new.era_de_membership_id is distinct from old.era_de_membership_id)
     and coalesce(current_setting('leda.aplicando_pase', true), '0') <> '1' then
    raise exception 'Los campos de compromiso de una tarea son inmutables.';
  end if;
  if new.estado is distinct from old.estado
     and coalesce(current_setting('leda.aplicando_evento', true), '0') <> '1' then
    raise exception
      'El estado de una tarea no se escribe directamente. Insertá una fila en task_state_event.';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_bloquear_estado_directo
  before update on task
  for each row execute function bloquear_estado_directo();

create or replace function aplicar_evento_objetivo() returns trigger
security definer set search_path = leda, public, pg_temp as $$
declare espacio_anterior text := current_setting('leda.workspace_id', true);
begin
  -- Como `aplicar_evento_tarea` (migración 0068): `leda_app` agrega el evento pero no escribe
  -- `objective`, así que la proyección la aplica el dueño, que no saltea la RLS. Se acota al
  -- espacio del propio evento, que el disparador de derivación ya resolvió desde el objetivo, y se
  -- restaura el espacio previo.
  perform set_config('leda.workspace_id', new.workspace_id::text, true);
  perform set_config('leda.aplicando_evento', '1', true);
  update objective
     set estado = new.estado_nuevo, actualizado_en = new.at
   where id = new.objective_id;
  perform set_config('leda.aplicando_evento', '0', true);
  perform set_config('leda.workspace_id', coalesce(espacio_anterior, ''), true);
  return new;
end $$ language plpgsql;

create trigger trg_aplicar_evento_objetivo
  after insert on objective_state_event
  for each row execute function aplicar_evento_objetivo();

-- --- Sin ciclos en las dependencias --------------------------------------

create or replace function evitar_ciclo_dependencia() returns trigger as $$
declare hay_ciclo boolean;
begin
  with recursive alcanzables as (
    select new.origen_task_id as t
    union
    select d.origen_task_id
      from dependency d join alcanzables a on d.destino_task_id = a.t
  )
  select exists (select 1 from alcanzables where t = new.destino_task_id)
    into hay_ciclo;

  if hay_ciclo then
    raise exception 'La dependencia crea un ciclo.';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_evitar_ciclo_dependencia
  before insert or update on dependency
  for each row execute function evitar_ciclo_dependencia();

-- --- Un bloqueo no existe sin causa --------------------------------------

create or replace function exigir_bloqueo_abierto() returns trigger as $$
begin
  if new.estado_nuevo = 'bloqueada'
     and not exists (select 1 from blocker
                      where task_id = new.task_id and resuelto_en is null) then
    raise exception 'No se puede bloquear una tarea sin un bloqueo abierto que la explique.';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_exigir_bloqueo_abierto
  before insert on task_state_event
  for each row execute function exigir_bloqueo_abierto();

-- --- No se arranca con una bloqueante sin terminar ------------------------
-- Mecánica §4: "la tarea destino no puede pasar a en_curso hasta que la
-- origen esté terminada". `cancelada` cuenta igual que `terminada` para
-- liberar el freno, con el mismo criterio que `motivo_no_cierra_tarea` usa
-- para las dependencias bloqueantes abiertas: una origen cancelada nunca va
-- a terminar, y tratarla como abierta bloquearía la destino para siempre.
--
-- Corrección tras revisión: el freno es para ARRANCAR, no para volver de un
-- bloqueo. Mecánica §3 dice que salir de `bloqueada` devuelve la tarea al
-- estado que tenía antes -- es una restauración, no un arranque nuevo -- y
-- ese estado previo ya había pasado (o no necesitaba pasar) este mismo
-- chequeo la primera vez. Sin esta excepción, bloquear una tarea que ya
-- estaba `en_curso` con una dependencia bloqueante todavía abierta (algo que
-- T1 permite a propósito, sin mover la tarea retroactivamente) volvía
-- irresoluble el bloqueo: `resolver_bloqueo` intenta el insert `bloqueada ->
-- en_curso` y el disparador lo rechazaba, dejando el bloqueo abierto para
-- siempre.
--
-- Segunda corrección tras revisión: eximir por `new.estado_anterior =
-- 'bloqueada'` solo era demasiado amplio -- dejaba pasar una tarea que
-- NUNCA había arrancado: `asignada` -> `registrar_bloqueo` -> `bloqueada` ->
-- `actualizar_estado(en_curso)` quedaba exenta igual, exactamente lo que
-- mecánica §4 prohíbe. La restauración legítima es más angosta: sólo
-- cuando el estado anterior a la ÚLTIMA entrada a `bloqueada` -- no el
-- evento inmediatamente anterior a este, sino el que tenía la tarea justo
-- antes de bloquearse -- era `en_curso`. Por eso se consulta
-- `estado_previo_a_bloqueo` (0007), no `new.estado_anterior` a secas.
--
-- T6c (`odd/tasks/leda-orienta.md`): mismo criterio para la vuelta desde
-- `en_revision`. Decisión del usuario (2026-09-27): "Pedir cambios"
-- (`herramientas._pedir_cambios_tarea`) devuelve la tarea al estado que
-- tenía antes de la ÚLTIMA entrada a `en_revision` -- `en_curso` si estaba
-- en curso, exento por la misma razón que salir de `bloqueada`; `asignada`
-- si se entregó sin haber arrancado nunca, sin ninguna excepción. Por eso
-- se consulta `estado_previo_a_revision` (abajo), no `new.estado_anterior`
-- a secas.

create or replace function motivo_no_arranca_tarea(p_task uuid)
returns text as $$
declare
  dep_abiertas integer;
begin
  if not exists (select 1 from task where id = p_task) then
    return 'La tarea no existe.';
  end if;

  select count(*) into dep_abiertas
    from dependency d join task o on o.id = d.origen_task_id
   where d.destino_task_id = p_task
     and d.tipo = 'bloqueante'
     and o.estado not in ('terminada', 'cancelada');
  if dep_abiertas > 0 then
    return format('Quedan %s dependencias bloqueantes sin resolver.', dep_abiertas);
  end if;

  return null;
end $$ language plpgsql;

-- No es security definer: corre con los privilegios de quien inserta. Sólo
-- necesita ejecutar `estado_previo_a_bloqueo` y `estado_previo_a_revision`
-- (tampoco security definer para quien las llama desde acá, sólo para lo
-- que leen adentro) cuando la transición realmente sale de `bloqueada` o de
-- `en_revision`; `leda_app` -- el único rol que hoy hace pasar una tarea a
-- `en_curso`, vía `resolver_bloqueo`, `pedir_cambios_tarea` o
-- `actualizar_estado` -- ya tiene `execute` concedido sobre las dos (0007 y
-- T6c más abajo).
create or replace function exigir_dependencias_resueltas() returns trigger as $$
declare
  motivo text;
  restaura_en_curso boolean := false;
begin
  if new.estado_nuevo = 'en_curso' then
    if new.estado_anterior = 'bloqueada' then
      restaura_en_curso := estado_previo_a_bloqueo(new.task_id) = 'en_curso';
    elsif new.estado_anterior = 'en_revision' then
      restaura_en_curso := estado_previo_a_revision(new.task_id) = 'en_curso';
    end if;
    if not restaura_en_curso then
      motivo := motivo_no_arranca_tarea(new.task_id);
      if motivo is not null then
        raise exception 'No se puede pasar la tarea a en curso: %', motivo;
      end if;
    end if;
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_exigir_dependencias_resueltas
  before insert on task_state_event
  for each row execute function exigir_dependencias_resueltas();

-- --- Condiciones de cierre -----------------------------------------------
-- Devuelven null si se puede cerrar, o el motivo por el que no.
-- Esto es lo que impide que el modelo de lenguaje dé por terminada una tarea.

-- ADR 0009: única fuente de verdad de "a esta tarea le falta la evidencia
-- que exige su política" -- la usa `motivo_no_cierra_tarea` (cierre) y
-- también `herramientas._actualizar_estado`/`menu_tarea.calcular_menu`
-- (entrega a `en_revision` y el gate de "Aprobar"), que antes no tenían
-- ninguna forma de hacer la misma pregunta sin reimplementar el criterio.
--
-- Migración 0014 (T6b, `odd/tasks/leda-orienta.md`): decisión del usuario
-- (2026-09-27) -- si el aprobador pidió cambios, la evidencia vieja deja de
-- contar; hay que volver a mandar evidencia (ejemplo: pintar una pared, al
-- aprobador le faltó una parte, la evidencia nueva muestra esa parte
-- pintada). Antes, cualquier fila de `evidence` de la tarea -- aunque fuera
-- de antes del "Pedir cambios" -- alcanzaba para que esta función devolviera
-- `false`, y `herramientas._actualizar_estado` descartaba en silencio la
-- evidencia nueva de la reentrega. Ahora sólo cuenta evidencia con `at`
-- estrictamente posterior al último `approval` 'rechazado' de la tarea (de
-- cualquier aprobador: no hace falta que sea el mismo de `motivo_no_cierra_
-- tarea`, alcanza con que alguien haya pedido cambios); el empate (`evidence.
-- at = rechazado.at`) falla cerrado, igual que el empate de 0013. Sin ningún
-- 'rechazado', el comportamiento no cambia: cualquier evidencia cuenta.
--
-- Migración 0034 (ADR 0019, decisión 5): la política se cumple por tipo. Cada
-- tipo que pide la tarea tiene que tener una pieza propia (su `cubre` lo nombra)
-- del ciclo vigente, no retirada, de una clase que ese tipo acepta (las clases,
-- del pack, en `task_evidence_policy.tipos`). Una frase sola ya no cubre una
-- foto: es la mecánica §6, no se acepta una afirmación cuando la política pide un
-- artefacto. `tipos_de_evidencia_que_faltan` es la fuente de "qué falta" y acepta
-- también las piezas de una entrega todavía sin confirmar (`p_piezas`, cada una
-- con su `clase` y su `cubre`), para decirlo antes de escribir nada.
create or replace function clases_de_un_tipo_de_evidencia(p_task uuid, p_tipo text)
returns text[] as $$
  select coalesce((
    select array(select jsonb_array_elements_text(p.tipos -> p_tipo -> 'clases'))
      from task t
      join task_evidence_policy p on p.workspace_id = t.workspace_id and p.area_id = t.area_id
     where t.id = p_task
       and jsonb_typeof(p.tipos -> p_tipo -> 'clases') = 'array'), '{}');
$$ language sql stable;

create or replace function tipos_que_acepta_la_clase(p_task uuid, p_clase text)
returns text[] as $$
  select coalesce(array(
    select r.tipo
      from task t, unnest(t.evidencia_requerida) with ordinality as r(tipo, orden)
     where t.id = p_task
       and p_clase = any(clases_de_un_tipo_de_evidencia(t.id, r.tipo))
     order by r.orden), '{}');
$$ language sql stable;

create or replace function tipos_de_evidencia_que_faltan(p_task uuid,
                                                         p_piezas jsonb default '[]'::jsonb)
returns text[] as $$
  select coalesce(array(
    select r.tipo
      from task t, unnest(t.evidencia_requerida) with ordinality as r(tipo, orden)
     where t.id = p_task
       and not exists (
         select 1 from evidence e
          where e.task_id = t.id
            and r.tipo = any(e.cubre)
            and e.clase = any(clases_de_un_tipo_de_evidencia(t.id, r.tipo))
            and e.at > coalesce(
              (select max(a.at) from approval a
                where a.sujeto_tipo = 'tarea' and a.sujeto_id = t.id
                  and a.decision = 'rechazado'),
              '-infinity'::timestamptz)
            and not exists (select 1 from evidencia_retirada w where w.evidence_id = e.id))
       and not exists (
         select 1 from jsonb_array_elements(
                          case when jsonb_typeof(p_piezas) = 'array' then p_piezas
                               else '[]'::jsonb end) p
          where p ->> 'clase' = any(clases_de_un_tipo_de_evidencia(t.id, r.tipo))
            and jsonb_typeof(p -> 'cubre') = 'array'
            and p -> 'cubre' ? r.tipo)
     order by r.orden), '{}');
$$ language sql stable;

create or replace function evidencia_pendiente(p_task uuid)
returns boolean as $$
  select cardinality(tipos_de_evidencia_que_faltan(p_task)) > 0;
$$ language sql stable;

create or replace function motivo_no_cierra_tarea(p_task uuid)
returns text as $$
declare
  t            task%rowtype;
  aprobador    uuid;
  dep_abiertas integer;
begin
  select * into t from task where id = p_task;
  if not found then return 'La tarea no existe.'; end if;

  -- Que el criterio sea obligatorio lo decide el pack del espacio.
  if coalesce((select valor::text::boolean from workspace_setting
                where workspace_id = t.workspace_id
                  and clave = 'exigir_criterio_aceptacion'), true)
     and (t.criterio_aceptacion is null or btrim(t.criterio_aceptacion) = '') then
    return 'Falta el criterio de aceptación.';
  end if;

  if evidencia_pendiente(p_task) then
    return 'Falta la evidencia requerida.';
  end if;

  if exists (select 1 from blocker where task_id = p_task and resuelto_en is null) then
    return 'La tarea tiene un bloqueo abierto.';
  end if;

  select count(*) into dep_abiertas
    from dependency d join task o on o.id = d.origen_task_id
   where d.destino_task_id = p_task
     and d.tipo = 'bloqueante'
     and o.estado not in ('terminada', 'cancelada');
  if dep_abiertas > 0 then
    return format('Quedan %s dependencias bloqueantes sin resolver.', dep_abiertas);
  end if;

  -- La aprobación de una tarea la da quien revisa el trabajo de su
  -- responsable. Es por persona, no por área: Marcos aprueba a Nahuel aunque
  -- estén en áreas distintas, y a Marcos lo aprueba Dirección. Una tarea que
  -- cambió de manos la sigue revisando quien la revisaba (migración 0045).
  aprobador := quien_revisa_la_tarea(p_task);

  -- Sólo cuenta si la ÚLTIMA decisión del aprobador sobre esta tarea es
  -- 'aprobado' (migración 0013, review-c112506a): ADR 0009 agregó "Pedir
  -- cambios", que inserta un `approval` 'rechazado' y devuelve la tarea a
  -- `en_curso` -- sin este chequeo, una aprobación vieja que no había
  -- alcanzado para cerrar (por ejemplo por un bloqueo abierto) seguía
  -- contando para siempre, y el trabajo corregido
  -- podía cerrarse sin que nadie lo aprobara. Una fila 'aprobado' cuenta
  -- sólo si no existe ningún 'rechazado' del mismo aprobador con `at`
  -- posterior o igual: el empate falla cerrado, nunca aprobado.
  if aprobador is not null
     and not exists (
       select 1 from approval a
        where a.sujeto_tipo = 'tarea' and a.sujeto_id = p_task
          and a.decision = 'aprobado'
          and a.aprobador_membership_id = aprobador
          and not exists (
            select 1 from approval r
             where r.sujeto_tipo = 'tarea' and r.sujeto_id = p_task
               and r.aprobador_membership_id = aprobador
               and r.decision = 'rechazado'
               and r.at >= a.at)) then
    return 'Falta la aprobación de quien revisa ese trabajo.';
  end if;

  return null;
end $$ language plpgsql;

-- El estado de una tarea es la proyección del último evento, y `leda_app`
-- no puede leer `task_state_event` directamente: es un registro append-only,
-- con el `select` revocado más abajo. Sin esta puerta angosta, salir de
-- `bloqueada` no tendría forma de saber a qué estado volver sin adivinar
-- `asignada`, que la mecánica §3 prohíbe explícitamente.
--
-- Filtra por `estado_nuevo = 'bloqueada'` a propósito: no alcanza con "el
-- último evento de la tarea". `actualizar_estado` no exige bloqueos cerrados
-- para salir de `bloqueada` (deuda conocida, no hay todavía un disparador que
-- valide transiciones), así que el último evento puede ser una salida hacia
-- otro estado con el bloqueo todavía abierto. Lo que hace falta acá es el
-- `estado_anterior` de la última vez que la tarea ENTRÓ a `bloqueada`, no el
-- de cualquier evento posterior. Quien llama sigue teniendo que comprobar
-- que la tarea esté bloqueada *ahora* antes de usar este valor.
create or replace function estado_previo_a_bloqueo(p_task uuid)
returns estado_tarea
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo estado_tarea;
begin
  select estado_anterior into previo
    from task_state_event
   where task_id = p_task and estado_nuevo = 'bloqueada'
   order by at desc
   limit 1;
  return previo;
end $$;

-- T6c (`odd/tasks/leda-orienta.md`): la misma puerta angosta que
-- `estado_previo_a_bloqueo`, pero para la ÚLTIMA entrada a `en_revision` en
-- vez de a `bloqueada` -- la necesita `herramientas._pedir_cambios_tarea`
-- para saber a qué estado devolver la tarea al pedirle cambios, y
-- `exigir_dependencias_resueltas` (arriba) para eximir esa restauración del
-- mismo freno que exime salir de `bloqueada`.
--
-- Filtra por `estado_nuevo = 'en_revision'` a propósito, con el mismo
-- criterio que `estado_previo_a_bloqueo`: hace falta el `estado_anterior`
-- de la última vez que la tarea ENTRÓ a `en_revision`, no el de cualquier
-- evento posterior. Quien llama sigue teniendo que comprobar que la tarea
-- esté en revisión *ahora* antes de usar este valor.
create or replace function estado_previo_a_revision(p_task uuid)
returns estado_tarea
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo estado_tarea;
begin
  select estado_anterior into previo
    from task_state_event
   where task_id = p_task and estado_nuevo = 'en_revision'
   order by at desc
   limit 1;
  return previo;
end $$;

create or replace function motivo_no_cierra_objetivo(p_obj uuid)
returns text as $$
declare
  o            objective%rowtype;
  hijas        integer;
  sub          integer;
  areas_faltan integer;
begin
  select * into o from objective where id = p_obj;
  if not found then return 'El objetivo no existe.'; end if;

  select count(*) into hijas from task
   where objective_id = p_obj and estado not in ('terminada', 'cancelada');
  if hijas > 0 then
    return format('Quedan %s tareas sin terminar.', hijas);
  end if;

  select count(*) into sub from objective
   where parent_id = p_obj and estado not in ('terminado', 'cancelado');
  if sub > 0 then
    return format('Quedan %s objetivos hijos sin terminar.', sub);
  end if;

  -- Cada área que participó tiene que haber aprobado su componente.
  select count(*) into areas_faltan
    from (select distinct area_id from task
           where objective_id = p_obj and estado = 'terminada') part
   where not exists (
     select 1 from approval a
       join membership m on m.id = a.aprobador_membership_id
      where a.sujeto_tipo = 'objetivo' and a.sujeto_id = p_obj
        and a.decision = 'aprobado' and m.area_id = part.area_id);
  if areas_faltan > 0 then
    return format('Faltan %s áreas por aprobar su componente.', areas_faltan);
  end if;

  -- Y la autoridad final del espacio.
  if not exists (
    select 1 from approval a
      join membership m on m.id = a.aprobador_membership_id
      join rol r on r.id = m.rol_id
     where a.sujeto_tipo = 'objetivo' and a.sujeto_id = p_obj
       and a.decision = 'aprobado' and r.autoridad_final) then
    return 'Falta la aprobación final.';
  end if;

  return null;
end $$ language plpgsql;

-- El disparador que hace que la regla no se pueda saltear.
create or replace function exigir_condiciones_de_cierre() returns trigger as $$
declare motivo text;
begin
  if new.estado_nuevo = 'terminada' then
    motivo := motivo_no_cierra_tarea(new.task_id);
    if motivo is not null then
      raise exception 'No se puede cerrar la tarea: %', motivo;
    end if;
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_exigir_condiciones_de_cierre
  before insert on task_state_event
  for each row execute function exigir_condiciones_de_cierre();

create or replace function exigir_condiciones_de_cierre_obj() returns trigger as $$
declare motivo text;
begin
  if new.estado_nuevo = 'terminado' then
    motivo := motivo_no_cierra_objetivo(new.objective_id);
    if motivo is not null then
      raise exception 'No se puede cerrar el objetivo: %', motivo;
    end if;
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_exigir_condiciones_de_cierre_obj
  before insert on objective_state_event
  for each row execute function exigir_condiciones_de_cierre_obj();

-- =========================================================================
-- Aislamiento entre espacios
--
-- El agente se conecta con leda_app y sólo ve el espacio que declara en
-- leda.workspace_id. El aislamiento no depende de que el modelo se acuerde.
-- =========================================================================

do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'leda_app') then
    create role leda_app nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'leda_admin') then
    create role leda_admin nologin bypassrls;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'leda_gateway') then
    create role leda_gateway nologin noinherit;
  end if;
  -- Dueño de las funciones `security definer`. Sin él, esas funciones quedan a
  -- nombre de quien corra este script -- en la práctica un superusuario, que
  -- ignora la RLS: adentro de sus cuerpos el aislamiento no existiría.
  if not exists (select 1 from pg_roles where rolname = 'leda_owner') then
    create role leda_owner nologin noinherit;
  end if;
end $$;
alter role leda_gateway noinherit nobypassrls;
alter role leda_owner nologin noinherit nobypassrls nosuperuser;

do $$
declare t text;
begin
  foreach t in array array[
    'area','rol','membership','objective','task','task_draft',
    'task_evidence_policy','dependency','blocker',
    'task_state_event','objective_state_event',
    'evidence','approval','pending_reply','inbound_message','message_outbox',
    'pending_action','pending_action_option',
    'cadence_job','escalation_route','glossary_term','approval_policy',
    'workspace_setting','message_template','permission','greeting_state',
    'conversation_question','conversation_option','conversation_turn',
    'scheduled_notice','conversation_state','task_forecast','blocker_unblocker',
    'archivo','archivo_de_mensaje','evidencia_retirada','archivo_de_tarea',
    'message_outbox_adjunto','acceso_tarea','vista_de_tarea','message_outbox_enlace',
    'dicho_de_quien_destraba','pase_de_tarea','cambio_de_responsable',
    'pedido_de_detalle','tarea_compartida','apodo',
    'enlace_de_entrada','sesion_web','carga_de_tarea',
    'message_outbox_entrada_web','ofrecimiento_web','creacion_de_objetivo']
  loop
    execute format('alter table %I enable row level security', t);
    execute format('alter table %I force row level security', t);
    execute format($f$
      create policy aislamiento_espacio on %I
        using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid)
    $f$, t);
    execute format('grant select, insert, update, delete on %I to leda_app', t);
  end loop;
end $$;

-- Committed tasks are created only by confirmar_borrador_tarea(). The admin
-- role keeps direct access for controlled maintenance and legacy test data.
revoke insert on task from leda_app;
revoke update, delete on task from leda_app;
grant select on task to leda_app;
-- Los objetivos, igual (migración 0068): los crea `crear_objetivo_web` (ADR 0023, decisión 1) y
-- el importador; `leda_app` sólo los lee.
revoke insert, update, delete on objective from leda_app;
revoke update, delete on task_draft from leda_app;
grant update (objective_id, objective_snapshot, titulo, descripcion, area_id,
              responsable_membership_id, fecha_objetivo,
              criterio_aceptacion, evidencia_requerida,
              evidencia_policy_version, version, estado, actualizado_en)
  on task_draft to leda_app;
revoke insert, update, delete on task_evidence_policy from leda_app;
-- Los eventos de estado son append-only y leda_app no los lee: sólo escribe
-- hechos. Están en el arreglo de arriba por su política de aislamiento, que es
-- lo que impide escribir contra una tarea de otro espacio; el bucle concede el
-- juego completo, así que acá se recorta al insert que es lo único legítimo.
revoke select, update, delete on task_state_event from leda_app;
revoke select, update, delete on objective_state_event from leda_app;
-- El motor (migraciones 0030 y 0031): el registro de turnos, las previsiones y
-- quién destraba sólo se agregan; preguntas, opciones y avisos no se borran.
revoke update, delete on conversation_turn, task_forecast, blocker_unblocker
  from leda_app;
revoke delete on conversation_question, conversation_option, scheduled_notice
  from leda_app;
-- Los archivos recibidos (migración 0033) sólo se agregan y se leen.
revoke update, delete on archivo, archivo_de_mensaje from leda_app;
-- La evidencia, sus retiros y los archivos dichos de una tarea (migración 0034),
-- también: una pieza equivocada se retira, no se borra (ADR 0019, decisión 3).
revoke update, delete on evidence, evidencia_retirada, archivo_de_tarea from leda_app;
-- Lo que lleva un mensaje (migración 0035) no cambia: sólo se agrega y se lee.
revoke update, delete on message_outbox_adjunto from leda_app;
-- Lo que dice quien destraba (migración 0042) sólo se agrega y se lee.
revoke update, delete on dicho_de_quien_destraba from leda_app;
-- Los pases (migración 0045): un pase cambia de estado, nunca se borra; un cambio de responsable
-- sólo se agrega.
revoke delete on pase_de_tarea from leda_app;
revoke update, delete on cambio_de_responsable from leda_app;
-- El detalle de una tarea (migración 0050): un pedido avanza y lo compartido se revoca; nada
-- se borra.
revoke delete on pedido_de_detalle, tarea_compartida from leda_app;
-- Los apodos (migración 0055): se aprenden y se dejan de usar; nada se borra.
revoke delete on apodo from leda_app;
-- La página de la tarea (migración 0036): `leda_app` no tiene nada sobre los accesos ni las
-- vistas, sólo `execute` sobre sus funciones; la marca del enlace en la salida, agregar y leer.
revoke all on acceso_tarea, vista_de_tarea from public, leda_app;
revoke update, delete on message_outbox_enlace from leda_app;
-- La marca del enlace de entrada a la web (migración 0066): agregar y leer.
revoke update, delete on message_outbox_entrada_web from leda_app;
-- Encontrar un token antes de saber su espacio: sólo `leda_owner` (las funciones de la página),
-- sólo para leer y sólo la fila de ese hash.
create policy resolver_por_token on acceso_tarea for select to leda_owner
  using (token_hash = nullif(current_setting('leda.token_de_tarea', true), ''));
-- El enlace de entrada y la sesión de la web (migración 0057): lo mismo. `leda_app` no tiene nada
-- sobre las tablas; el canje y `sesion_vigente` encuentran el token antes de saber su espacio.
revoke all on enlace_de_entrada, sesion_web from public, leda_app;
create policy resolver_por_token on enlace_de_entrada for select to leda_owner
  using (token_hash = nullif(current_setting('leda.token_de_entrada', true), ''));
create policy resolver_por_token on sesion_web for select to leda_owner
  using (token_hash = nullif(current_setting('leda.token_de_sesion', true), ''));
-- La clave de cada carga desde la web (migración 0062): `leda_app` no tiene nada sobre ella, sólo
-- `execute` sobre `cargar_tarea`.
revoke all on carga_de_tarea from public, leda_app;
-- La clave de cada creación de un objetivo desde la web (migración 0068): lo mismo, sólo
-- `execute` sobre `crear_objetivo_web`.
revoke all on creacion_de_objetivo from public, leda_app;

-- Registros auxiliares. Quedan fuera del bucle de arriba porque `audit_log` e
-- `incident` admiten espacio nulo para los hechos de alcance global, que sólo
-- origina la conexión administrativa: una fila sin espacio no queda atribuida
-- a ningún cliente y por eso no puede falsificar su registro.
alter table absence enable row level security;
alter table absence force row level security;
create policy aislamiento_espacio on absence
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

alter table audit_log enable row level security;
alter table audit_log force row level security;
create policy aislamiento_espacio on audit_log
  using (workspace_id is null
         or workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

alter table incident enable row level security;
alter table incident force row level security;
create policy aislamiento_espacio on incident
  using (workspace_id is null
         or workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

-- La configuración de cada espacio (migración 0041): `leda_app` la lee directamente, con
-- `select` solamente (la concesión está más abajo), y la escribe sólo la conexión
-- administrativa. Fuera del bucle de arriba porque el bucle concede el juego completo.
-- `model_config` admite espacio nulo para el modelo global, que ve todo espacio.
alter table work_calendar enable row level security;
alter table work_calendar force row level security;
create policy aislamiento_espacio on work_calendar
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

alter table holiday enable row level security;
alter table holiday force row level security;
create policy aislamiento_espacio on holiday
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

alter table persona_config enable row level security;
alter table persona_config force row level security;
create policy aislamiento_espacio on persona_config
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

alter table workspace_version enable row level security;
alter table workspace_version force row level security;
create policy aislamiento_espacio on workspace_version
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

alter table model_config enable row level security;
alter table model_config force row level security;
create policy aislamiento_espacio on model_config
  using (workspace_id is null
         or workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

grant execute on function confirmar_borrador_tarea(uuid, text, bigint, bigint)
  to leda_gateway;
grant execute on function resolver_ingreso_borrador(uuid, text, bigint, bigint)
  to leda_gateway;
revoke execute on function confirmar_borrador_tarea(uuid, text, bigint, bigint)
  from leda_app;
revoke execute on function resolver_ingreso_borrador(uuid, text, bigint, bigint)
  from leda_app;

-- Una función `security definer` corre con los privilegios de su dueño. Si ese
-- dueño fuera superusuario, la RLS no aplicaría dentro de ella y el
-- aislamiento entre clientes se caería por adentro. Lo que contiene a
-- `leda_owner` es la RLS, no la lista de privilegios: por eso no inicia
-- sesión, nadie es miembro suyo y no puede saltear la política. Una lista
-- exacta de lo que toca cada cuerpo se desactualizaría en el próximo cambio.
grant usage on schema leda to leda_owner;
grant all privileges on all tables in schema leda to leda_owner;
grant all privileges on all sequences in schema leda to leda_owner;

alter function resolver_pendiente(text, uuid, timestamptz)
  owner to leda_owner;
alter function confirmar_borrador_tarea(uuid, text, bigint, bigint)
  owner to leda_owner;
alter function resolver_ingreso_borrador(uuid, text, bigint, bigint)
  owner to leda_owner;
alter function aplicar_evento_tarea()
  owner to leda_owner;
alter function aplicar_evento_objetivo()
  owner to leda_owner;
alter function aplicar_cambio_de_responsable()
  owner to leda_owner;
alter function estado_previo_a_bloqueo(uuid)
  owner to leda_owner;
alter function estado_previo_a_revision(uuid)
  owner to leda_owner;

-- Ninguna función elevada la ejecuta `public` (migración 0037): `resolver_pendiente`, sólo
-- `leda_app`; `aplicar_evento_tarea` es un disparador y no la llama nadie.
revoke execute on function resolver_pendiente(text, uuid, timestamptz) from public;
grant execute on function resolver_pendiente(text, uuid, timestamptz) to leda_app;
revoke execute on function aplicar_evento_tarea() from public;
revoke execute on function aplicar_evento_objetivo() from public;
revoke execute on function aplicar_cambio_de_responsable() from public;
revoke execute on function estado_previo_a_bloqueo(uuid) from public;
grant execute on function estado_previo_a_bloqueo(uuid) to leda_app;
revoke execute on function estado_previo_a_revision(uuid) from public;
grant execute on function estado_previo_a_revision(uuid) to leda_app;

-- La concesión general de arriba alcanzó a `acceso_tablero` por haberse
-- definido antes. Se la acota a lo que sus dos funciones necesitan, que es lo
-- mismo que concede la migración `0006`: sin esto, instalación limpia y base
-- migrada divergirían en los privilegios de esta tabla.
revoke all on acceso_tablero from leda_owner;
grant select, insert on acceso_tablero to leda_owner;

-- La página de la tarea (migración 0036): lo mismo que el tablero, acotado a lo que necesitan
-- sus funciones.
revoke all on acceso_tarea, vista_de_tarea from leda_owner;
grant select, insert on acceso_tarea, vista_de_tarea to leda_owner;

-- El enlace de entrada y la sesión de la web (migración 0057): lo que necesitan sus funciones; de
-- las columnas, sólo las que cambian.
revoke all on enlace_de_entrada, sesion_web from leda_owner;
grant select, insert on enlace_de_entrada, sesion_web to leda_owner;
grant update (canjeado_en, anulado_en) on enlace_de_entrada to leda_owner;
grant update (ultimo_uso_en, cortada_en, motivo_de_corte) on sesion_web to leda_owner;

alter function puede_ver_tarea(uuid, uuid) owner to leda_owner;
alter function emitir_acceso_tarea(uuid, uuid, text) owner to leda_owner;
alter function acceso_tarea_vigente(text) owner to leda_owner;
alter function leer_pagina_de_tarea(text) owner to leda_owner;
alter function leer_archivo_de_tarea(text, uuid) owner to leda_owner;

revoke execute on function puede_ver_tarea(uuid, uuid) from public;
revoke execute on function emitir_acceso_tarea(uuid, uuid, text) from public;
revoke execute on function acceso_tarea_vigente(text) from public;
revoke execute on function leer_pagina_de_tarea(text) from public;
revoke execute on function leer_archivo_de_tarea(text, uuid) from public;
grant execute on function puede_ver_tarea(uuid, uuid) to leda_app;
grant execute on function emitir_acceso_tarea(uuid, uuid, text) to leda_app;
grant execute on function leer_pagina_de_tarea(text) to leda_app;
grant execute on function leer_archivo_de_tarea(text, uuid) to leda_app;

alter function auditar_acceso_web(uuid, uuid, tipo_actor, text, text, uuid, jsonb)
  owner to leda_owner;
alter function emitir_enlace_de_entrada(uuid, text, uuid) owner to leda_owner;
alter function canjear_enlace_de_entrada(text, text) owner to leda_owner;
alter function sesion_vigente(text) owner to leda_owner;
alter function cortar_sesion(uuid, text, uuid) owner to leda_owner;
alter function cortar_sesiones_de_membresia(uuid, text, uuid) owner to leda_owner;

revoke execute on function auditar_acceso_web(uuid, uuid, tipo_actor, text, text, uuid, jsonb)
  from public;
revoke execute on function emitir_enlace_de_entrada(uuid, text, uuid) from public;
revoke execute on function canjear_enlace_de_entrada(text, text) from public;
revoke execute on function sesion_vigente(text) from public;
revoke execute on function cortar_sesion(uuid, text, uuid) from public;
revoke execute on function cortar_sesiones_de_membresia(uuid, text, uuid) from public;
grant execute on function emitir_enlace_de_entrada(uuid, text, uuid) to leda_app;
grant execute on function canjear_enlace_de_entrada(text, text) to leda_app;
grant execute on function sesion_vigente(text) to leda_app;
grant execute on function cortar_sesion(uuid, text, uuid) to leda_app;
grant execute on function cortar_sesiones_de_membresia(uuid, text, uuid) to leda_app;

alter function entro_a_la_web(uuid) owner to leda_owner;
alter function tiene_un_enlace_sin_usar(uuid) owner to leda_owner;
revoke execute on function entro_a_la_web(uuid) from public;
revoke execute on function tiene_un_enlace_sin_usar(uuid) from public;
grant execute on function entro_a_la_web(uuid) to leda_app;
grant execute on function tiene_un_enlace_sin_usar(uuid) to leda_app;

alter function tareas_que_ve(uuid, text, timestamptz) owner to leda_owner;
alter function vistas_de(uuid) owner to leda_owner;
alter function tareas_de_la_sesion(text, text, timestamptz) owner to leda_owner;
alter function vistas_de_la_sesion(text) owner to leda_owner;

revoke execute on function tareas_que_ve(uuid, text, timestamptz) from public;
revoke execute on function vistas_de(uuid) from public;
revoke execute on function tareas_de_la_sesion(text, text, timestamptz) from public;
revoke execute on function vistas_de_la_sesion(text) from public;
grant execute on function tareas_de_la_sesion(text, text, timestamptz) to leda_app;
grant execute on function vistas_de_la_sesion(text) to leda_app;

alter function terminadas_que_ve(uuid, text, timestamptz) owner to leda_owner;
alter function terminadas_de_la_sesion(text, text, timestamptz) owner to leda_owner;

revoke execute on function terminadas_que_ve(uuid, text, timestamptz) from public;
revoke execute on function terminadas_de_la_sesion(text, text, timestamptz) from public;
grant execute on function terminadas_de_la_sesion(text, text, timestamptz) to leda_app;

alter function esperas_que_ve(uuid, text, timestamptz) owner to leda_owner;
alter function esperas_de_la_sesion(text, text, timestamptz) owner to leda_owner;

revoke execute on function esperas_que_ve(uuid, text, timestamptz) from public;
revoke execute on function esperas_de_la_sesion(text, text, timestamptz) from public;
grant execute on function esperas_de_la_sesion(text, text, timestamptz) to leda_app;

-- La puerta de administración (migración 0061): lo que necesitan sus funciones; de las columnas,
-- sólo las que cambian. `leda_app`, nada sobre las tablas.
revoke all on enlace_de_administracion, sesion_de_administracion from leda_owner;
grant select, insert on enlace_de_administracion, sesion_de_administracion to leda_owner;
grant update (canjeado_en, anulado_en) on enlace_de_administracion to leda_owner;
grant update (ultimo_uso_en, cortada_en, motivo_de_corte) on sesion_de_administracion
  to leda_owner;

alter function auditar_acceso_de_administracion(uuid, tipo_actor, text, text, uuid, jsonb)
  owner to leda_owner;
alter function es_administrador_de_plataforma(uuid) owner to leda_owner;
alter function emitir_enlace_de_administracion(uuid, text, uuid) owner to leda_owner;
alter function canjear_enlace_de_administracion(text, text) owner to leda_owner;
alter function sesion_de_administracion_vigente(text) owner to leda_owner;
alter function cerrar_sesion_de_administracion(text) owner to leda_owner;
alter function cortar_sesiones_de_administrador(uuid, text, uuid) owner to leda_owner;

revoke execute on function auditar_acceso_de_administracion(uuid, tipo_actor, text, text, uuid,
                                                            jsonb) from public;
revoke execute on function es_administrador_de_plataforma(uuid) from public;
revoke execute on function emitir_enlace_de_administracion(uuid, text, uuid) from public;
revoke execute on function canjear_enlace_de_administracion(text, text) from public;
revoke execute on function sesion_de_administracion_vigente(text) from public;
revoke execute on function cerrar_sesion_de_administracion(text) from public;
revoke execute on function cortar_sesiones_de_administrador(uuid, text, uuid) from public;
-- La consola (`leda_admin`): emitir y cortar todas. La web (`leda_app`): canjear, la sesión
-- vigente y cerrar la propia.
grant execute on function emitir_enlace_de_administracion(uuid, text, uuid) to leda_admin;
grant execute on function cortar_sesiones_de_administrador(uuid, text, uuid) to leda_admin;
grant execute on function canjear_enlace_de_administracion(text, text) to leda_app;
grant execute on function sesion_de_administracion_vigente(text) to leda_app;
grant execute on function cerrar_sesion_de_administracion(text) to leda_app;

-- La carga de una tarea desde la web (migración 0062): de la clave, `leda_owner` sólo busca y
-- agrega. La consola (`leda_admin`): el día hábil. La web (`leda_app`): las opciones y la carga.
revoke all on carga_de_tarea from leda_owner;
grant select, insert on carga_de_tarea to leda_owner;

alter function es_dia_habil(uuid, date) owner to leda_owner;
alter function opciones_de_la_carga(text, uuid, timestamptz) owner to leda_owner;
alter function cargar_tarea(text, uuid, uuid, text, text, uuid, date, text, text[], uuid, text,
                            timestamptz, uuid) owner to leda_owner;

revoke execute on function es_dia_habil(uuid, date) from public;
revoke execute on function opciones_de_la_carga(text, uuid, timestamptz) from public;
revoke execute on function cargar_tarea(text, uuid, uuid, text, text, uuid, date, text, text[],
                                        uuid, text, timestamptz, uuid) from public;
grant execute on function es_dia_habil(uuid, date) to leda_admin;
grant execute on function opciones_de_la_carga(text, uuid, timestamptz) to leda_app;
grant execute on function cargar_tarea(text, uuid, uuid, text, text, uuid, date, text, text[],
                                       uuid, text, timestamptz, uuid) to leda_app;

-- Los objetivos desde la web (migración 0068): de la clave, `leda_owner` sólo busca y agrega. La
-- web (`leda_app`): las opciones y la creación; quién crea se resuelve adentro de las dos.
revoke all on creacion_de_objetivo from leda_owner;
grant select, insert on creacion_de_objetivo to leda_owner;

alter function quien_crea_el_objetivo(text, text, uuid) owner to leda_owner;
alter function opciones_del_objetivo(text, text, uuid, timestamptz) owner to leda_owner;
alter function crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid, date, text,
                                  timestamptz) owner to leda_owner;
revoke execute on function quien_crea_el_objetivo(text, text, uuid) from public;
revoke execute on function opciones_del_objetivo(text, text, uuid, timestamptz) from public;
revoke execute on function crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid,
                                              date, text, timestamptz) from public;
grant execute on function opciones_del_objetivo(text, text, uuid, timestamptz) to leda_app;
grant execute on function crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid,
                                             date, text, timestamptz) to leda_app;

alter function emitir_acceso_tablero(uuid, text, timestamptz)
  owner to leda_owner;
alter function resolver_acceso_tablero(text)
  owner to leda_owner;

revoke execute on function emitir_acceso_tablero(uuid, text, timestamptz)
  from public;
revoke execute on function resolver_acceso_tablero(text) from public;
grant execute on function emitir_acceso_tablero(uuid, text, timestamptz)
  to leda_app;
grant execute on function resolver_acceso_tablero(text) to leda_app;

-- Aviso de incidentes a la administración de plataforma (T28). Mismo motivo
-- que las dos funciones de arriba: `security definer`, dueño `leda_owner`,
-- ejecutable por `leda_app` (la mayoría de los incidentes se registran
-- desde una sesión acotada a un espacio) y por `leda_admin` (la consola y
-- el validador de invariantes, que corren sin espacio fijado).
alter function avisar_incidente_admin(uuid, uuid, text)
  owner to leda_owner;

revoke execute on function avisar_incidente_admin(uuid, uuid, text)
  from public;
grant execute on function avisar_incidente_admin(uuid, uuid, text)
  to leda_app, leda_admin;

-- El agente no consulta app_user directamente: lo haría por encima del
-- aislamiento, porque esa tabla es global. Usa esta vista, que pasa por
-- membership y por lo tanto queda acotada al espacio activo.
create view integrante with (security_barrier = true) as
  select m.id            as membership_id,
         m.workspace_id,
         m.area_id,
         m.rol_id,
         m.aprobador_membership_id,
         m.activo,
         u.id            as app_user_id,
         u.telegram_user_id,
         u.nombre
    from membership m
    join app_user u on u.id = m.app_user_id
   where m.workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid;

comment on view integrante is
  'Personas del espacio activo. La vista corre con permisos de su dueño, así que app_user nunca se expone a leda_app; el filtro explícito es lo que acota al espacio. Sin leda.workspace_id definido no devuelve nada.';

grant usage on schema leda to leda_app, leda_admin;
grant usage on schema leda to leda_gateway;
-- approval_requirement no lleva workspace_id: sólo se llega a ella por
-- approval_policy, que sí tiene RLS. Las tablas de configuración de esta lista
-- tienen su política desde la migración 0041.
grant select on workspace, work_calendar, holiday, persona_config,
                integrante, absence, model_config, workspace_version,
                approval_requirement to leda_app;
-- task_state_event y objective_state_event ya reciben su insert por el bucle de
-- aislamiento, que además les instala la política.
grant insert on audit_log, incident, absence to leda_app;
grant all on all tables in schema leda to leda_admin;
grant all on integrante to leda_admin;
