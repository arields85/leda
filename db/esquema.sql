-- =========================================================================
-- Prisma — esquema de base de datos
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

create schema if not exists prisma;
set search_path = prisma, public;

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

create type tipo_actor as enum ('persona', 'prisma', 'sistema');

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
  nombre_visible  text not null default 'Prisma',
  registro        text not null default 'vos',
  formalidad      text not null default 'profesional_cordial',
  longitud        text not null default 'breve',
  emojis          boolean not null default false,
  presentacion    text
);

-- Umbrales y límites del pack: re-aprobación, tope de mensajes, días de
-- escalamiento. Clave-valor para no migrar el esquema cada vez que aparece
-- un parámetro nuevo.
create table workspace_setting (
  workspace_id  uuid not null references workspace(id) on delete cascade,
  clave         text not null,
  valor         jsonb not null,
  primary key (workspace_id, clave)
);

-- Policy imported from evidencia.por_area. An empty array is an explicit
-- no-evidence policy; absence of a row means that policy is unresolved.
create table task_evidence_policy (
  workspace_id        uuid not null references workspace(id) on delete cascade,
  area_id             uuid not null references area(id) on delete cascade,
  evidencia_requerida text[] not null,
  version             integer not null default 1 check (version > 0),
  actualizado_en      timestamptz not null default now(),
  primary key (workspace_id, area_id)
);

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
  parent_id               uuid references objective(id) on delete cascade,
  tipo                    tipo_objetivo not null,
  titulo                  text not null,
  descripcion             text,
  referente_membership_id uuid references membership(id),
  estado                  estado_objetivo not null default 'propuesto',
  fecha_objetivo          date,
  creado_en               timestamptz not null default now(),
  actualizado_en          timestamptz not null default now()
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
  actualizado_en            timestamptz not null default now()
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
  -- T6j (`odd/tasks/prisma-orienta.md`): `clock_timestamp()`, no `now()` --
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
  escalado_en   timestamptz
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
  at             timestamptz not null default clock_timestamp()
);

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

-- Quién le debe una respuesta a Prisma. Sin esta tabla la escalera de
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
  constraint inbound_message_workspace_id_unique unique (workspace_id, id),
  constraint inbound_message_workspace_chat_unique
    unique (workspace_id, id, chat_id)
);

-- Prisma nunca llama a Telegram directamente: escribe acá y un worker despacha.
-- dedupe_key es lo que hace que un reinicio no duplique mensajes.
create table message_outbox (
  id                      uuid primary key default gen_random_uuid(),
  workspace_id            uuid not null references workspace(id) on delete cascade,
  chat_id                 bigint not null,
  destinatario_membership_id uuid references membership(id),
  tipo                    tipo_mensaje not null default 'normal',
  cuerpo                  text not null,
  -- Una respuesta a alguien que acaba de escribir sale siempre. La regla de
  -- no escribir fuera de horario es para lo que Prisma inicia; dejar a una
  -- persona esperando hasta mañana porque son las 17:05 es peor.
  es_respuesta            boolean not null default false,
  -- Saludo diario (pack 06 §3, T28; revisión 2026-09-28+2): esta fila ES la
  -- bienvenida de incorporación -- el despachador reclama la reserva del día
  -- por ella sin anteponerle nada, nunca una categoría de `tipo` (que la
  -- presentación de grupo también usa como 'informativo' sin ser un saludo).
  es_bienvenida           boolean not null default false,
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
  pending_action_id       uuid
);

create index outbox_despacho on message_outbox (estado, programado_para)
  where estado in ('listo', 'pendiente');

-- =========================================================================
-- Acciones pendientes
-- =========================================================================

-- Trabajo que Prisma entendió y todavía no ejecutó, porque falta un acto de
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

-- Conversational task intake is server-owned. Model output may propose values,
-- but only an exact free-text reply or a single-use server choice confirms one.
create table task_intake_request (
  id                    uuid primary key default gen_random_uuid(),
  workspace_id          uuid not null references workspace(id) on delete cascade,
  membership_id         uuid not null,
  chat_id               bigint not null check (chat_id > 0),
  task_draft_id         uuid not null unique,
  estado                text not null default 'active'
                        check (estado in ('active', 'cancelled', 'converted')),
  version               integer not null default 1 check (version > 0),
  source_inbound_id     uuid not null,
  source_raw_text       text not null,
  terminal_result       jsonb,
  creado_en             timestamptz not null default now(),
  actualizado_en        timestamptz not null default now(),
  constraint task_intake_request_workspace_id_unique unique (workspace_id, id),
  constraint task_intake_request_membership_workspace
    foreign key (workspace_id, membership_id)
    references membership(workspace_id, id) on delete cascade,
  constraint task_intake_request_draft_workspace
    foreign key (workspace_id, task_draft_id)
    references task_draft(workspace_id, id),
  constraint task_intake_request_source_workspace_chat
    foreign key (workspace_id, source_inbound_id, chat_id)
    references inbound_message(workspace_id, id, chat_id)
);

create unique index task_intake_one_active
  on task_intake_request (workspace_id, membership_id, chat_id)
  where estado = 'active';

create table task_intake_field (
  request_id          uuid not null,
  workspace_id        uuid not null references workspace(id) on delete cascade,
  campo               text not null check (campo in (
                        'title', 'description', 'objective', 'responsible', 'area',
                        'evidence', 'due_date', 'acceptance_criterion')),
  estado              text not null default 'missing'
                      check (estado in ('missing', 'proposed', 'confirmed')),
  valor               jsonb,
  proposed_by         text check (proposed_by in ('model', 'server', 'user')),
  source_inbound_id   uuid references inbound_message(id),
  source_raw_text     text,
  source_choice_id    uuid,
  version             integer not null default 1 check (version > 0),
  actualizado_en      timestamptz not null default now(),
  primary key (request_id, campo),
  constraint task_intake_field_workspace_id_unique unique (workspace_id, request_id, campo),
  constraint task_intake_field_request_workspace
    foreign key (workspace_id, request_id)
    references task_intake_request(workspace_id, id) on delete cascade,
  constraint task_intake_field_source_workspace
    foreign key (workspace_id, source_inbound_id)
    references inbound_message(workspace_id, id),
  check ((source_inbound_id is null) = (source_raw_text is null)),
  check ((estado = 'missing' and valor is null) or
         (estado <> 'missing' and valor is not null))
);

create table task_intake_choice_set (
  id                uuid primary key default gen_random_uuid(),
  workspace_id      uuid not null references workspace(id) on delete cascade,
  request_id        uuid not null,
  campo             text,
  request_version   integer not null,
  tipo              text not null,
  estado            text not null default 'active'
                    check (estado in ('active', 'consumed', 'invalidated')),
  resultado         jsonb,
  creado_en         timestamptz not null default now(),
  constraint task_intake_choice_set_workspace_id_unique unique (workspace_id, id),
  constraint task_intake_choice_set_request_workspace
    foreign key (workspace_id, request_id)
    references task_intake_request(workspace_id, id) on delete cascade
);

create unique index task_intake_one_active_choice_set
  on task_intake_choice_set (request_id) where estado = 'active';

create table task_intake_choice (
  id                uuid primary key default gen_random_uuid(),
  workspace_id      uuid not null references workspace(id) on delete cascade,
  choice_set_id     uuid not null,
  token             text not null unique,
  etiqueta          text not null,
  accion            text not null,
  valor             jsonb,
  orden             integer not null default 0,
  activa            boolean not null default true,
  elegida           boolean not null default false,
  resultado         jsonb,
  constraint task_intake_choice_workspace_id_unique unique (workspace_id, id),
  constraint task_intake_choice_set_workspace
    foreign key (workspace_id, choice_set_id)
    references task_intake_choice_set(workspace_id, id) on delete cascade,
  constraint intake_token_cabe_en_callback check (octet_length(token) between 8 and 40),
  constraint task_intake_choice_telegram_label
    check (telegram_utf16_units(etiqueta) between 1 and 80)
);

create index task_intake_choice_de
  on task_intake_choice (choice_set_id, orden);

create table task_intake_free_text_slot (
  id                  uuid primary key default gen_random_uuid(),
  workspace_id        uuid not null references workspace(id) on delete cascade,
  request_id          uuid not null,
  campo               text not null,
  request_version     integer not null,
  estado              text not null default 'active'
                      check (estado in ('active', 'consumed', 'invalidated')),
  source_inbound_id   uuid,
  source_raw_text     text,
  resultado           jsonb,
  creado_en           timestamptz not null default now(),
  consumido_en        timestamptz,
  constraint task_intake_free_text_workspace_id_unique unique (workspace_id, id),
  constraint task_intake_free_text_request_workspace
    foreign key (workspace_id, request_id)
    references task_intake_request(workspace_id, id) on delete cascade,
  constraint task_intake_free_text_source_workspace
    foreign key (workspace_id, source_inbound_id)
    references inbound_message(workspace_id, id),
  check ((source_inbound_id is null) = (source_raw_text is null))
);

create unique index task_intake_one_active_text_slot
  on task_intake_free_text_slot (request_id) where estado = 'active';

alter table task_intake_field
  add constraint task_intake_field_source_choice
  foreign key (workspace_id, source_choice_id)
  references task_intake_choice(workspace_id, id);

alter table message_outbox
  add column intake_choice_set_id uuid references task_intake_choice_set(id)
  on delete set null;

alter table message_outbox
  add constraint message_outbox_telegram_payload
  check (telegram_utf16_units(cuerpo) between 1 and
         case when pending_action_id is not null or intake_choice_set_id is not null
              then 3900 else 4096 end);

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
    references pending_action(workspace_id, id) on delete set null (pending_action_id),
  add constraint message_outbox_choice_workspace
    foreign key (workspace_id, intake_choice_set_id)
    references task_intake_choice_set(workspace_id, id)
    on delete set null (intake_choice_set_id);

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
language plpgsql security definer as $$
declare
  o record;
  a record;
  ws uuid := nullif(current_setting('prisma.workspace_id', true), '')::uuid;
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
set search_path = prisma, public, pg_temp as $$
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
  perform set_config('prisma.workspace_id', p_workspace_id::text, true);
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
    update task_intake_request
       set estado = 'cancelled', actualizado_en = ahora,
           terminal_result = jsonb_build_object('resultado', 'cancelada',
                                                 'pending_action_id', a.id)
     where task_draft_id = a.draft_id and estado = 'active';
    update task_intake_choice set activa = false where choice_set_id in
      (select s.id from task_intake_choice_set s join task_intake_request r
         on r.id = s.request_id where r.task_draft_id = a.draft_id);
    update task_intake_choice_set set estado = 'invalidated'
     where request_id in (select id from task_intake_request
                           where task_draft_id = a.draft_id)
       and estado = 'active';
    update task_intake_free_text_slot set estado = 'invalidated'
     where request_id in (select id from task_intake_request
                           where task_draft_id = a.draft_id)
       and estado = 'active';
    insert into audit_log
         (workspace_id, actor_app_user_id, actor_kind, accion, sujeto_tipo,
          sujeto_id, detalle)
    select a.workspace_id, actor_app_user_id, 'persona',
           'cancelar_ingreso_tarea', 'task_draft', a.draft_id,
           jsonb_build_object('pending_action_id', a.id)
     where exists (select 1 from task_intake_request
                    where task_draft_id = a.draft_id);
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
  update task_intake_request
     set estado = 'converted', actualizado_en = ahora,
         terminal_result = jsonb_build_object('resultado', 'ok',
                                               'task_id', nueva_task,
                                               'pending_action_id', a.id)
   where task_draft_id = a.draft_id and estado = 'active';
  update task_intake_choice set activa = false where choice_set_id in
    (select s.id from task_intake_choice_set s join task_intake_request r
       on r.id = s.request_id where r.task_draft_id = a.draft_id);
  update task_intake_choice_set set estado = 'invalidated'
   where request_id in (select id from task_intake_request
                         where task_draft_id = a.draft_id)
     and estado = 'active';
  update task_intake_free_text_slot set estado = 'invalidated'
   where request_id in (select id from task_intake_request
                         where task_draft_id = a.draft_id)
     and estado = 'active';
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
set search_path = prisma, public, pg_temp as $$
begin
  return query
    select c.resultado, c.task_id, c.pending_action_id, c.replay
      from confirmar_borrador_tarea(
        p_workspace_id, p_token, p_telegram_user_id, p_chat_id) c;
end $$;

revoke all on function resolver_ingreso_borrador(uuid, text, bigint, bigint)
  from public;

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
  'El aprendizaje ajusta cómo Prisma comunica y estima. Nunca modifica autoridad ni reglas.';

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
-- Lo que protege esta tabla es que nadie la consulta: `prisma_app` no recibe
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

-- El espacio no se recibe: sale de la membresía. Como `prisma_owner` no
-- saltea la RLS, esa búsqueda queda filtrada al espacio de la sesión, así que
-- una membresía de otro cliente no se encuentra y falla idéntico a una
-- inexistente. Decir "no tenés permiso" confirmaría que existe.
create or replace function emitir_acceso_tablero(
    p_membership_id uuid, p_token_hash text, p_vence_en timestamptz)
returns uuid
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
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
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare acceso acceso_tablero%rowtype;
begin
  select * into acceso from acceso_tablero a
   where a.token_hash = p_token_hash and a.vence_en > now();
  if not found then
    return;
  end if;

  perform set_config('prisma.workspace_id', acceso.workspace_id::text, true);

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
-- administra la plataforma tenía que correr `python -m prisma incidentes
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

-- Fan-out del aviso de un incidente a cada administrador de plataforma
-- alcanzable. `security definer`, mismo motivo que `emitir_acceso_tablero`/
-- `resolver_acceso_tablero`: necesita leer `platform_role` y `audit_log`
-- (tablas globales, o sin concesión de lectura a prisma_app, que prisma_app
-- no puede consultar directamente -- mismo motivo por el que existe la
-- vista `integrante`) desde una sesión que puede estar acotada a un espacio,
-- o a ninguno (un incidente global, sin cliente en particular).
--
-- El texto del aviso (`p_cuerpo`) lo arma Python (`incidentes.py`) ANTES de
-- llamar acá -- decisión del usuario, 2026-09-28, corrigiendo el alcance
-- original de esta unidad: el aviso SÍ tiene que incluir qué lo disparó
-- (Constitución §2, el administrador "accede a las conversaciones privadas
-- entre Prisma y los integrantes"; §10 exige avisarle sanitizado, no
-- ocultarle el disparador). Armarlo en Python, no acá, es porque necesita
-- leer `inbound_message`/`pending_action` (ya concedidas a `prisma_app`,
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

-- La auditoría autoritativa es la evidencia que se le muestra a un cliente. Su
-- espacio lo fija la sesión, nunca quien escribe: si otro cliente pudiera
-- atribuirse una entrada, el registro dejaría de ser evidencia. Sin espacio en
-- la sesión --la conexión administrativa-- se conserva lo suministrado, que es
-- como se registran los hechos de alcance global.
create or replace function derivar_espacio_registro() returns trigger as $$
declare actual text := nullif(current_setting('prisma.workspace_id', true), '');
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
security definer set search_path = prisma, public as $$
declare espacio_anterior text := current_setting('prisma.workspace_id', true);
begin
  -- El dueño de esta función no saltea la RLS, así que este `update` queda
  -- sujeto a la política de aislamiento. Se acota al espacio del propio
  -- evento, que el disparador de derivación ya resolvió desde la tarea: no se
  -- confía en nada aportado por quien llama. Hace falta fijarlo porque la
  -- conexión administrativa no define espacio alguno, y sin esto la proyección
  -- no encontraría la fila y fallaría en silencio. El valor previo se
  -- restaura para no angostar el resto de la transacción.
  perform set_config('prisma.workspace_id', new.workspace_id::text, true);
  perform set_config('prisma.aplicando_evento', '1', true);
  update task
     set estado = new.estado_nuevo,
         actualizado_en = new.at
   where id = new.task_id;
  perform set_config('prisma.aplicando_evento', '0', true);
  perform set_config('prisma.workspace_id', coalesce(espacio_anterior, ''), true);
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
     or new.responsable_membership_id is distinct from old.responsable_membership_id
     or new.fecha_objetivo is distinct from old.fecha_objetivo
     or new.criterio_aceptacion is distinct from old.criterio_aceptacion
     or new.evidencia_requerida is distinct from old.evidencia_requerida
     or new.evidencia_policy_version is distinct from old.evidencia_policy_version
     or new.source_draft_id is distinct from old.source_draft_id then
    raise exception 'Los campos de compromiso de una tarea son inmutables.';
  end if;
  if new.estado is distinct from old.estado
     and coalesce(current_setting('prisma.aplicando_evento', true), '0') <> '1' then
    raise exception
      'El estado de una tarea no se escribe directamente. Insertá una fila en task_state_event.';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_bloquear_estado_directo
  before update on task
  for each row execute function bloquear_estado_directo();

create or replace function aplicar_evento_objetivo() returns trigger as $$
begin
  perform set_config('prisma.aplicando_evento', '1', true);
  update objective
     set estado = new.estado_nuevo, actualizado_en = new.at
   where id = new.objective_id;
  perform set_config('prisma.aplicando_evento', '0', true);
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
-- T6c (`odd/tasks/prisma-orienta.md`): mismo criterio para la vuelta desde
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
-- `en_revision`; `prisma_app` -- el único rol que hoy hace pasar una tarea a
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
-- Migración 0014 (T6b, `odd/tasks/prisma-orienta.md`): decisión del usuario
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
create or replace function evidencia_pendiente(p_task uuid)
returns boolean as $$
  select array_length(t.evidencia_requerida, 1) is not null
     and not exists (
       select 1 from evidence e
        where e.task_id = t.id
          and e.at > coalesce(
            (select max(r.at) from approval r
              where r.sujeto_tipo = 'tarea' and r.sujeto_id = t.id
                and r.decision = 'rechazado'),
            '-infinity'::timestamptz))
    from task t where t.id = p_task;
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
  -- estén en áreas distintas, y a Marcos lo aprueba Dirección.
  select m.aprobador_membership_id into aprobador
    from membership m where m.id = t.responsable_membership_id;

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

-- El estado de una tarea es la proyección del último evento, y `prisma_app`
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
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
declare previo estado_tarea;
begin
  select estado_anterior into previo
    from task_state_event
   where task_id = p_task and estado_nuevo = 'bloqueada'
   order by at desc
   limit 1;
  return previo;
end $$;

-- T6c (`odd/tasks/prisma-orienta.md`): la misma puerta angosta que
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
language plpgsql security definer set search_path = prisma, public, pg_temp as $$
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
-- El agente se conecta con prisma_app y sólo ve el espacio que declara en
-- prisma.workspace_id. El aislamiento no depende de que el modelo se acuerde.
-- =========================================================================

do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'prisma_app') then
    create role prisma_app nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'prisma_admin') then
    create role prisma_admin nologin bypassrls;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'prisma_gateway') then
    create role prisma_gateway nologin noinherit;
  end if;
  -- Dueño de las funciones `security definer`. Sin él, esas funciones quedan a
  -- nombre de quien corra este script -- en la práctica un superusuario, que
  -- ignora la RLS: adentro de sus cuerpos el aislamiento no existiría.
  if not exists (select 1 from pg_roles where rolname = 'prisma_owner') then
    create role prisma_owner nologin noinherit;
  end if;
end $$;
alter role prisma_gateway noinherit nobypassrls;
alter role prisma_owner nologin noinherit nobypassrls nosuperuser;

do $$
declare t text;
begin
  foreach t in array array[
    'area','rol','membership','objective','task','task_draft',
    'task_evidence_policy','dependency','blocker',
    'task_state_event','objective_state_event',
    'evidence','approval','pending_reply','inbound_message','message_outbox',
    'pending_action','pending_action_option','task_intake_request',
    'task_intake_field','task_intake_choice_set','task_intake_choice',
    'task_intake_free_text_slot',
    'cadence_job','escalation_route','glossary_term','approval_policy',
    'workspace_setting','message_template','permission','greeting_state']
  loop
    execute format('alter table %I enable row level security', t);
    execute format('alter table %I force row level security', t);
    execute format($f$
      create policy aislamiento_espacio on %I
        using (workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid)
    $f$, t);
    execute format('grant select, insert, update, delete on %I to prisma_app', t);
  end loop;
end $$;

-- Committed tasks are created only by confirmar_borrador_tarea(). The admin
-- role keeps direct access for controlled maintenance and legacy test data.
revoke insert on task from prisma_app;
revoke update, delete on task from prisma_app;
grant select on task to prisma_app;
revoke update, delete on task_draft from prisma_app;
grant update (objective_id, objective_snapshot, titulo, descripcion, area_id,
              responsable_membership_id, fecha_objetivo,
              criterio_aceptacion, evidencia_requerida,
              evidencia_policy_version, version, estado, actualizado_en)
  on task_draft to prisma_app;
revoke insert, update, delete on task_evidence_policy from prisma_app;
-- Los eventos de estado son append-only y prisma_app no los lee: sólo escribe
-- hechos. Están en el arreglo de arriba por su política de aislamiento, que es
-- lo que impide escribir contra una tarea de otro espacio; el bucle concede el
-- juego completo, así que acá se recorta al insert que es lo único legítimo.
revoke select, update, delete on task_state_event from prisma_app;
revoke select, update, delete on objective_state_event from prisma_app;

-- Registros auxiliares. Quedan fuera del bucle de arriba porque `audit_log` e
-- `incident` admiten espacio nulo para los hechos de alcance global, que sólo
-- origina la conexión administrativa: una fila sin espacio no queda atribuida
-- a ningún cliente y por eso no puede falsificar su registro.
alter table absence enable row level security;
alter table absence force row level security;
create policy aislamiento_espacio on absence
  using (workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid);

alter table audit_log enable row level security;
alter table audit_log force row level security;
create policy aislamiento_espacio on audit_log
  using (workspace_id is null
         or workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid);

alter table incident enable row level security;
alter table incident force row level security;
create policy aislamiento_espacio on incident
  using (workspace_id is null
         or workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid);

grant execute on function confirmar_borrador_tarea(uuid, text, bigint, bigint)
  to prisma_gateway;
grant execute on function resolver_ingreso_borrador(uuid, text, bigint, bigint)
  to prisma_gateway;
revoke execute on function confirmar_borrador_tarea(uuid, text, bigint, bigint)
  from prisma_app;
revoke execute on function resolver_ingreso_borrador(uuid, text, bigint, bigint)
  from prisma_app;

-- Una función `security definer` corre con los privilegios de su dueño. Si ese
-- dueño fuera superusuario, la RLS no aplicaría dentro de ella y el
-- aislamiento entre clientes se caería por adentro. Lo que contiene a
-- `prisma_owner` es la RLS, no la lista de privilegios: por eso no inicia
-- sesión, nadie es miembro suyo y no puede saltear la política. Una lista
-- exacta de lo que toca cada cuerpo se desactualizaría en el próximo cambio.
grant usage on schema prisma to prisma_owner;
grant all privileges on all tables in schema prisma to prisma_owner;
grant all privileges on all sequences in schema prisma to prisma_owner;

alter function resolver_pendiente(text, uuid, timestamptz)
  owner to prisma_owner;
alter function confirmar_borrador_tarea(uuid, text, bigint, bigint)
  owner to prisma_owner;
alter function resolver_ingreso_borrador(uuid, text, bigint, bigint)
  owner to prisma_owner;
alter function aplicar_evento_tarea()
  owner to prisma_owner;
alter function estado_previo_a_bloqueo(uuid)
  owner to prisma_owner;
alter function estado_previo_a_revision(uuid)
  owner to prisma_owner;

revoke execute on function estado_previo_a_bloqueo(uuid) from public;
grant execute on function estado_previo_a_bloqueo(uuid) to prisma_app;
revoke execute on function estado_previo_a_revision(uuid) from public;
grant execute on function estado_previo_a_revision(uuid) to prisma_app;

-- La concesión general de arriba alcanzó a `acceso_tablero` por haberse
-- definido antes. Se la acota a lo que sus dos funciones necesitan, que es lo
-- mismo que concede la migración `0006`: sin esto, instalación limpia y base
-- migrada divergirían en los privilegios de esta tabla.
revoke all on acceso_tablero from prisma_owner;
grant select, insert on acceso_tablero to prisma_owner;

alter function emitir_acceso_tablero(uuid, text, timestamptz)
  owner to prisma_owner;
alter function resolver_acceso_tablero(text)
  owner to prisma_owner;

revoke execute on function emitir_acceso_tablero(uuid, text, timestamptz)
  from public;
revoke execute on function resolver_acceso_tablero(text) from public;
grant execute on function emitir_acceso_tablero(uuid, text, timestamptz)
  to prisma_app;
grant execute on function resolver_acceso_tablero(text) to prisma_app;

-- Aviso de incidentes a la administración de plataforma (T28). Mismo motivo
-- que las dos funciones de arriba: `security definer`, dueño `prisma_owner`,
-- ejecutable por `prisma_app` (la mayoría de los incidentes se registran
-- desde una sesión acotada a un espacio) y por `prisma_admin` (la consola y
-- el validador de invariantes, que corren sin espacio fijado).
alter function avisar_incidente_admin(uuid, uuid, text)
  owner to prisma_owner;

revoke execute on function avisar_incidente_admin(uuid, uuid, text)
  from public;
grant execute on function avisar_incidente_admin(uuid, uuid, text)
  to prisma_app, prisma_admin;

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
   where m.workspace_id = nullif(current_setting('prisma.workspace_id', true), '')::uuid;

comment on view integrante is
  'Personas del espacio activo. La vista corre con permisos de su dueño, así que app_user nunca se expone a prisma_app; el filtro explícito es lo que acota al espacio. Sin prisma.workspace_id definido no devuelve nada.';

grant usage on schema prisma to prisma_app, prisma_admin;
grant usage on schema prisma to prisma_gateway;
-- approval_requirement no lleva workspace_id: sólo se llega a ella por
-- approval_policy, que sí tiene RLS.
grant select on workspace, work_calendar, holiday, persona_config,
                integrante, absence, model_config, workspace_version,
                approval_requirement to prisma_app;
-- task_state_event y objective_state_event ya reciben su insert por el bucle de
-- aislamiento, que además les instala la política.
grant insert on audit_log, incident, absence to prisma_app;
grant all on all tables in schema prisma to prisma_admin;
grant all on integrante to prisma_admin;
