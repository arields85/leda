\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0044_espera_su_bloqueo.sql. Delegar por chat, la C-7 (`odd/tasks/fase-c.md`,
-- decisión 9; ADR 0017, enmienda a la decisión 2, aceptada el 2026-10-09; conversación 38).
--
-- Una tarea pasa a otra persona sólo con tres confirmaciones: la vista previa de quien lo pide, la
-- decisión del encargado del sector de quien recibe (si es quien pide, su pedido es la decisión;
-- si es quien recibe, decide con su respuesta) y la de quien la toma (constitución §7; mecánica §7,
-- la re-aprobación de un cambio de responsable). Lo guardan:
--
-- - `pase_de_tarea`: el pedido, quién lo decide y cómo terminó, sólo hacia adelante
--   (`vigilar_pase_de_tarea`); uno abierto por tarea.
-- - `cambio_de_responsable`: sólo se agrega; agregarlo es lo único que cambia quién tiene la tarea
--   (`aplicar_cambio_de_responsable`, `security definer` de `leda_owner`), y sólo si el pase espera
--   que la tome esa persona y la tarea sigue con quien la tenía, asignada, en curso o trabada.
-- - `task.revisa_membership_id`: el trabajo lo sigue revisando quien lo revisaba antes del pase (la
--   enmienda, "lo que no cambia"); si es quien la toma, quien aprueba el trabajo de esa persona,
--   para que nadie revise su propio trabajo. `quien_revisa_la_tarea` es la regla única, y la leen
--   el cierre (`motivo_no_cierra_tarea`), quién ve la página (`puede_ver_tarea`) y la página
--   (`leer_pagina_de_tarea`). `bloquear_estado_directo` deja cambiar quién la tiene y quién la
--   revisa sólo dentro de ese cambio.
--
-- Aislamiento: espacio obligatorio, RLS forzado con su política y todas las referencias con el
-- espacio. `leda_app` agrega y lee los dos; cambia el estado de un pase, nunca lo borra.
--
-- Se deshace con `db/rollbacks/0045_pase_de_tarea.sql`, antes que la vuelta atrás de la 0036 y la
-- de la 0002: sus claves compuestas apuntan a `membership_workspace_id_unique`, que la de la 0002
-- borra, y vuelve a dejar las funciones de la página como las dejó la 0036.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0045 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (select 1 from information_schema.columns
                  where table_schema = 'leda' and table_name = 'dicho_de_quien_destraba'
                    and column_name = 'espera_su_bloqueo_id') then
    raise exception '0045 requires 0044_espera_su_bloqueo.sql';
  end if;
  if to_regclass('leda.pase_de_tarea') is not null then
    raise exception '0045 ya está aplicada.';
  end if;
end $$;

alter table task add column revisa_membership_id uuid;
alter table task add constraint task_revisa
  foreign key (workspace_id, revisa_membership_id) references membership(workspace_id, id);
comment on column task.revisa_membership_id is
  'El Motor (C-7, delegar): quién revisa el trabajo de la tarea desde que cambió de manos (lo escribe el cambio de responsable). Nulo: quien aprueba el trabajo de su responsable.';

-- Quién revisa el trabajo de una tarea (migración 0045; C-7, delegar): el que quedó escrito en la
-- tarea cuando cambió de manos o, si nunca cambió, quien aprueba el trabajo de su responsable
-- (`membership.aprobador_membership_id`). Es la única regla: el cierre, quién ve la página y la
-- aplicación la leen de acá.
create or replace function quien_revisa_la_tarea(p_task uuid)
returns uuid
language sql stable set search_path = leda, public, pg_temp as $$
  select coalesce(t.revisa_membership_id, m.aprobador_membership_id)
    from task t
    left join membership m on m.id = t.responsable_membership_id
   where t.id = p_task;
$$;

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
  -- Quién la tiene y quién revisa su trabajo cambian sólo con un pase confirmado por quien lo
  -- pidió, quien lo decidió y quien la toma (migración 0045; C-7, delegar): lo aplica
  -- `aplicar_cambio_de_responsable`, al agregarse el cambio en `cambio_de_responsable`.
  if (new.responsable_membership_id is distinct from old.responsable_membership_id
      or new.revisa_membership_id is distinct from old.revisa_membership_id)
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
                          and ap.aprobador_membership_id = m.id)));
$$;

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
  select * into t from task where id = acceso.task_id;
  faltan := tipos_de_evidencia_que_faltan(t.id);
  select p.tipos into tipos from task_evidence_policy p
   where p.workspace_id = t.workspace_id and p.area_id = t.area_id;
  select jsonb_build_object(
    'espacio', w.nombre,
    'zona_horaria', w.zona_horaria,
    'persona', (select u.nombre from membership m join app_user u on u.id = m.app_user_id
                 where m.id = acceso.membership_id),
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
         where f.task_id = t.id) h), '[]'::jsonb),
    'evidencia', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', e.id, 'clase', e.clase, 'texto', e.texto,
               'enlace', case when e.clase = 'enlace' then e.uri end,
               'nombre', a.nombre_original, 'tipo_de_archivo', a.tipo, 'cubre', e.cubre,
               'ejemplo_aceptado', e.es_ejemplo_aceptado, 'quien', u.nombre, 'cuando', e.at,
               'retirada', x.id is not null, 'retirada_el', x.at) order by e.at, e.id)
        from evidence e
        left join archivo a on a.workspace_id = e.workspace_id and a.id = e.archivo_id
        left join membership m on m.id = e.entregado_por
        left join app_user u on u.id = m.app_user_id
        left join evidencia_retirada x on x.evidence_id = e.id
       where e.task_id = t.id), '[]'::jsonb))
    into resultado
    from workspace w where w.id = acceso.workspace_id;
  perform set_config('leda.workspace_id', previo, true);
  return resultado;
end $$;

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
                              'no_lo_aprobo', 'no_la_tomo', 'sin_efecto')),
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
  'El Motor (C-7): el cambio de quién tiene una tarea, con el pase que lo autorizó, quién la tenía, quién la tomó y quién revisa su trabajo desde entonces. Sólo se agrega; agregarlo aplica el cambio en la tarea.';

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
     and new.estado not in ('esperando_que_la_tome', 'la_tomo', 'no_la_tomo', 'sin_efecto') then
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
-- sigue en manos de quien la tenía y en un estado que se pasa, escribe quién revisa su trabajo
-- desde ahora (quien lo revisaba; si es quien la toma, quien aprueba el trabajo de esa persona),
-- cambia la tarea y da el pase por tomado. Corre con los privilegios de `leda_owner`, que no
-- saltea la RLS: sólo ve el espacio de la transacción.
create or replace function aplicar_cambio_de_responsable() returns trigger
security definer set search_path = leda, public, pg_temp as $$
declare p pase_de_tarea%rowtype;
        t task%rowtype;
        revisa uuid;
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
  revisa := coalesce(t.revisa_membership_id,
                     (select m.aprobador_membership_id from membership m
                       where m.id = t.responsable_membership_id));
  if revisa = p.a_membership_id then
    revisa := (select m.aprobador_membership_id from membership m
                where m.id = p.a_membership_id);
  end if;
  new.revisa_membership_id := revisa;
  perform set_config('leda.aplicando_pase', '1', true);
  update task
     set responsable_membership_id = p.a_membership_id,
         revisa_membership_id = revisa,
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

alter function aplicar_cambio_de_responsable() owner to leda_owner;
revoke execute on function aplicar_cambio_de_responsable() from public;

alter table pase_de_tarea enable row level security;
alter table pase_de_tarea force row level security;
create policy aislamiento_espacio on pase_de_tarea
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
alter table cambio_de_responsable enable row level security;
alter table cambio_de_responsable force row level security;
create policy aislamiento_espacio on cambio_de_responsable
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
grant all privileges on pase_de_tarea, cambio_de_responsable to leda_owner, leda_admin;
grant select, insert, update on pase_de_tarea to leda_app;
grant select, insert on cambio_de_responsable to leda_app;

commit;
