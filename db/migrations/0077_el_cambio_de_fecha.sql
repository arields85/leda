\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0076_el_pase_a_la_compu.sql. El cambio de fecha auditado (ADR 0025, decisión 6;
-- porción S2 de la J5 en `odd/tasks/plataforma-jerarquias.md`), con el molde de
-- `cambio_de_responsable` (migración 0045):
--
-- - `cambio_de_fecha`: sólo se agrega (`leda_app` agrega y lee; nadie la edita ni la borra), con
--   la fecha que tenía la tarea, la nueva, el motivo (obligatorio), quién lo hizo, quién lo decidió
--   y su clase (`cambio_directo`). RLS forzada, con la política de aislamiento de siempre.
-- - `aplicar_cambio_de_fecha`, su disparador `security definer` de `leda_owner`: rechaza un cambio
--   pensado sobre otra fecha, una tarea cerrada o de otro espacio (no la encuentra, como un id
--   inventado) y una fecha nueva que ya pasó o no es un día hábil del espacio (`es_dia_habil`), y
--   aplica la fecha nueva en la tarea.
-- - `bloquear_estado_directo`: la fecha de una tarea deja de ser inmutable sólo para ese
--   disparador (la marca `leda.aplicando_cambio_de_fecha`); los demás campos, igual que antes.
--
-- Quién puede cambiar una fecha lo deciden las funciones que la usen (porción S6); esta migración
-- es sólo el mecanismo. Se deshace con `db/rollbacks/0077_el_cambio_de_fecha.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0077 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0076 está aplicada y la 0077 no.
do $$ begin
  if to_regprocedure('leda.emitir_pase_a_la_compu(text, text, bigint, text, timestamptz, text, text)')
     is null then
    raise exception '0077 preflight failed: falta la 0076';
  end if;
  if to_regclass('leda.cambio_de_fecha') is not null then
    raise exception '0077 ya está aplicada.';
  end if;
end $$;

-- El cambio de fecha de una tarea (migración 0077; ADR 0025, decisión 6; J5, porción S2), con el
-- molde de `cambio_de_responsable`: sólo se agrega, y agregarlo es lo único que cambia la fecha de
-- una tarea (`aplicar_cambio_de_fecha`). Dice la fecha que tenía la tarea (uno viejo se rechaza),
-- la nueva, el motivo, quién lo hizo (un usuario: también el administrador de plataforma, que no
-- es miembro del espacio, como en `cargar_tarea`) y quién lo decidió. Quién puede cambiar una
-- fecha lo deciden las funciones que lo escriban (porción S6), no esta tabla. `clase` deja lugar a
-- otras formas de cambiarla; aceptar más tiempo no es una (ADR 0025, decisión 5: anota la fecha
-- prevista y la fecha comprometida queda).
create table cambio_de_fecha (
  id                          uuid primary key default gen_random_uuid(),
  workspace_id                uuid not null references workspace(id) on delete cascade,
  task_id                     uuid not null,
  fecha_anterior              timestamptz,
  fecha_nueva                 timestamptz not null,
  motivo                      text not null,
  clase                       text not null,
  cambiada_por_app_user_id    uuid not null references app_user(id),
  decidida_por_membership_id  uuid not null,
  at                          timestamptz not null,
  constraint cambio_de_fecha_tarea
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade,
  constraint cambio_de_fecha_decidida_por
    foreign key (workspace_id, decidida_por_membership_id)
    references membership(workspace_id, id),
  constraint cambio_de_fecha_motivo
    check (btrim(motivo) <> '' and char_length(motivo) <= 500),
  constraint cambio_de_fecha_clase check (clase in ('cambio_directo')),
  constraint cambio_de_fecha_cambia check (fecha_nueva is distinct from fecha_anterior)
);

create index cambio_de_fecha_tarea_at on cambio_de_fecha (task_id, at);

comment on table cambio_de_fecha is
  'J5 (ADR 0025, decisión 6; migración 0077): el cambio de la fecha comprometida de una tarea, con la fecha que tenía, la nueva, el motivo, quién lo hizo y quién lo decidió. Sólo se agrega; agregarlo aplica la fecha en la tarea (aplicar_cambio_de_fecha), y es lo único que la cambia.';

-- Agregar un cambio de fecha aplica la fecha nueva en la tarea (migración 0077; ADR 0025, decisión
-- 6). Comprueba que la tarea sea del espacio del cambio y siga abierta, que la fecha anterior sea la
-- que tiene la tarea ahora (un cambio pensado sobre otra fecha se rechaza, nunca se pisa) y que la
-- nueva sea un día hábil del espacio (`es_dia_habil`, la misma regla de la carga; decisión 56) de
-- hoy en adelante, en su zona. Corre con los privilegios de `leda_owner`, que no saltea la RLS: sólo
-- ve el espacio de la transacción, así que una tarea de otro espacio no existe, igual que un id
-- inventado. La marca `leda.aplicando_cambio_de_fecha` abre sólo la fecha
-- (`bloquear_estado_directo`).
create or replace function aplicar_cambio_de_fecha() returns trigger
security definer set search_path = leda, public, pg_temp as $$
declare t task%rowtype;
        zona text;
        dia date;
begin
  select * into t from task where id = new.task_id for update;
  if not found or t.workspace_id <> new.workspace_id then
    raise exception 'cambio_de_fecha: la tarea no existe';
  end if;
  if t.estado not in ('asignada', 'en_curso', 'bloqueada', 'en_revision') then
    raise exception 'cambio_de_fecha: la tarea ya no cambia de fecha';
  end if;
  if t.fecha_objetivo is distinct from new.fecha_anterior then
    raise exception 'cambio_de_fecha: la fecha de la tarea ya cambió';
  end if;
  select w.zona_horaria into zona from workspace w where w.id = t.workspace_id;
  dia := (new.fecha_nueva at time zone zona)::date;
  if dia < (new.at at time zone zona)::date then
    raise exception 'cambio_de_fecha: la fecha nueva ya pasó';
  end if;
  if not es_dia_habil(t.workspace_id, dia) then
    raise exception 'cambio_de_fecha: la fecha nueva no es un día hábil del espacio';
  end if;
  perform set_config('leda.aplicando_cambio_de_fecha', '1', true);
  update task
     set fecha_objetivo = new.fecha_nueva,
         actualizado_en = new.at
   where id = t.id;
  perform set_config('leda.aplicando_cambio_de_fecha', '0', true);
  return new;
end $$ language plpgsql;

create trigger trg_aplicar_cambio_de_fecha
  before insert on cambio_de_fecha
  for each row execute function aplicar_cambio_de_fecha();

alter function aplicar_cambio_de_fecha() owner to leda_owner;
revoke execute on function aplicar_cambio_de_fecha() from public;

create or replace function bloquear_estado_directo() returns trigger as $$
begin
  if new.objective_id is distinct from old.objective_id
     or new.titulo is distinct from old.titulo
     or new.descripcion is distinct from old.descripcion
     or new.area_id is distinct from old.area_id
     or new.criterio_aceptacion is distinct from old.criterio_aceptacion
     or new.evidencia_requerida is distinct from old.evidencia_requerida
     or new.evidencia_policy_version is distinct from old.evidencia_policy_version
     or new.source_draft_id is distinct from old.source_draft_id then
    raise exception 'Los campos de compromiso de una tarea son inmutables.';
  end if;
  -- La fecha cambia sólo con un cambio de fecha (migración 0077; ADR 0025, decisión 6): lo aplica
  -- `aplicar_cambio_de_fecha`, al agregarse el cambio en `cambio_de_fecha`.
  if new.fecha_objetivo is distinct from old.fecha_objetivo
     and coalesce(current_setting('leda.aplicando_cambio_de_fecha', true), '0') <> '1' then
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

alter table cambio_de_fecha enable row level security;
alter table cambio_de_fecha force row level security;
create policy aislamiento_espacio on cambio_de_fecha
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
grant all privileges on cambio_de_fecha to leda_owner, leda_admin;
grant select, insert on cambio_de_fecha to leda_app;

commit;
