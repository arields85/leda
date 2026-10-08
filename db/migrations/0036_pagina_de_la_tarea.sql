\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0035_salida_con_adjuntos.sql. La página de la tarea y su enlace (ADR 0019,
-- decisión 7; porción 4 de la C-3). El ADR la llamaba "0035, la página": la 0035 quedó para la
-- salida con adjuntos.
--
-- - `area.referente_membership_id`: quién es el referente de cada área, como un dato del espacio
--   (no por el nombre de un rol del pack). Lo carga el importador (`areas[].referente`).
-- - `acceso_tarea`: el enlace personal a la página de una tarea, uno por persona y por tarea en su
--   alcance. Sólo el hash del token; sin vencimiento (decisión del usuario, ADR 0019, decisión 1);
--   se puede revocar.
-- - `vista_de_tarea`: cada vista de la página y cada descarga de un archivo, sólo se agrega. Qué
--   acceso, cuándo y qué se sirvió; sin dirección ni navegador (7e).
-- - `message_outbox_enlace`: la fila de la salida que lleva el enlace de una tarea para una persona.
--   El despachador emite el enlace al mandar: ni la salida ni el registro de turnos guardan el
--   enlace, sólo esta marca. `message_outbox` no suma columnas (riesgo 1 de `docs/STATUS.md`).
-- - Las funciones: `puede_ver_tarea` (quién ve: el responsable, quien aprueba su trabajo hoy y
--   quien ya decidió sobre la tarea, el referente del área y la autoridad final del espacio),
--   `emitir_acceso_tarea`, `acceso_tarea_vigente` (sólo para las de lectura), `leer_pagina_de_tarea`
--   y `leer_archivo_de_tarea`. Las que tocan los accesos son `security definer` con dueño
--   `leda_owner`, que no saltea la RLS: reciben el hash del token, fijan el espacio que sale de él,
--   revalidan el derecho a ver y devuelven sólo esa tarea; un archivo, sólo si su evidencia es de
--   esa tarea. Las de lectura devuelven el espacio de la transacción como estaba.
-- - Aislamiento: las tres tablas con `row level security` forzado y la política de siempre.
--   `acceso_tarea` suma una política de lectura sólo para `leda_owner` por el hash del token, que
--   es lo que permite encontrarlo antes de saber su espacio; `leda_app` no tiene ningún privilegio
--   sobre `acceso_tarea` ni sobre `vista_de_tarea`, sólo `execute` sobre las funciones.
--
-- Se deshace con `db/rollbacks/0036_pagina_de_la_tarea.sql`, antes que la vuelta atrás de la 0002:
-- sus claves compuestas apuntan a `membership_workspace_id_unique`, que esa vuelta atrás borra.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0036 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('leda.message_outbox_adjunto') is null then
    raise exception '0036 requires 0035_salida_con_adjuntos.sql';
  end if;
  if to_regclass('leda.acceso_tarea') is not null then
    raise exception '0036 ya está aplicada.';
  end if;
end $$;

alter table area add column referente_membership_id uuid;
alter table area add constraint area_referente
  foreign key (workspace_id, referente_membership_id) references membership(workspace_id, id)
  on delete set null (referente_membership_id);

comment on column area.referente_membership_id is
  'ADR 0019, decisión 7b: el referente técnico del área, un dato del espacio (no el nombre de un rol del pack). Ve las páginas de las tareas de su área.';

create table acceso_tarea (
  id             uuid primary key default gen_random_uuid(),
  workspace_id   uuid not null references workspace(id) on delete cascade,
  membership_id  uuid not null,
  task_id        uuid not null,
  token_hash     text not null,
  emitido_en     timestamptz not null default now(),
  revocado_en    timestamptz,
  constraint acceso_tarea_workspace_id_unique unique (workspace_id, id),
  constraint acceso_tarea_token_unico unique (token_hash),
  constraint acceso_tarea_hash check (token_hash ~ '^[0-9a-f]{64}$'),
  constraint acceso_tarea_membership
    foreign key (workspace_id, membership_id) references membership(workspace_id, id)
    on delete cascade,
  constraint acceso_tarea_task
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade
);

create index acceso_tarea_de on acceso_tarea (task_id, membership_id);

comment on table acceso_tarea is
  'ADR 0019, decisión 7a: el enlace personal a la página de una tarea. Sólo el hash del token; sin vencimiento; el derecho a ver se revalida en cada pedido. leda_app no tiene privilegios: sólo execute sobre sus funciones.';

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

grant all privileges on acceso_tarea, vista_de_tarea, message_outbox_enlace
  to leda_owner, leda_admin;

alter table acceso_tarea enable row level security;
alter table acceso_tarea force row level security;
create policy aislamiento_espacio on acceso_tarea
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
-- Encontrar un token antes de saber su espacio: sólo `leda_owner` (las funciones de abajo), sólo
-- para leer y sólo la fila de ese hash.
create policy resolver_por_token on acceso_tarea for select to leda_owner
  using (token_hash = nullif(current_setting('leda.token_de_tarea', true), ''));

alter table vista_de_tarea enable row level security;
alter table vista_de_tarea force row level security;
create policy aislamiento_espacio on vista_de_tarea
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

alter table message_outbox_enlace enable row level security;
alter table message_outbox_enlace force row level security;
create policy aislamiento_espacio on message_outbox_enlace
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

-- `leda_app`: nada sobre los accesos ni las vistas; la marca del enlace, agregar y leer.
revoke all on acceso_tarea, vista_de_tarea from public, leda_app;
grant select, insert on message_outbox_enlace to leda_app;
-- `leda_owner`: lo que necesitan sus funciones.
revoke all on acceso_tarea, vista_de_tarea from leda_owner;
grant select, insert on acceso_tarea, vista_de_tarea to leda_owner;

create or replace function puede_ver_tarea(p_membership_id uuid, p_task_id uuid)
returns boolean
language sql stable set search_path = leda, public, pg_temp as $$
  select exists (
    select 1
      from membership m
      join task t on t.workspace_id = m.workspace_id and t.id = p_task_id
      join rol r on r.id = m.rol_id
      join area a on a.id = t.area_id
      left join membership resp on resp.id = t.responsable_membership_id
     where m.id = p_membership_id
       and m.activo
       and (t.responsable_membership_id = m.id
            or resp.aprobador_membership_id = m.id
            or a.referente_membership_id = m.id
            or r.autoridad_final
            or exists (select 1 from approval ap
                        where ap.workspace_id = t.workspace_id
                          and ap.sujeto_tipo = 'tarea' and ap.sujeto_id = t.id
                          and ap.aprobador_membership_id = m.id)));
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
  if not puede_ver_tarea(acceso.membership_id, acceso.task_id) then
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
      'quien_aprueba', (select u.nombre from membership r
                          join membership m on m.id = r.aprobador_membership_id
                          join app_user u on u.id = m.app_user_id
                         where r.id = t.responsable_membership_id),
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
               'quien', u.nombre, 'cuando', e.at,
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
       and not exists (select 1 from evidencia_retirada x where x.evidence_id = e.id);
    if v_contenido is not null then
      insert into vista_de_tarea (workspace_id, acceso_tarea_id, que, evidence_id)
           values (acceso.workspace_id, acceso.id, 'archivo', p_evidence_id);
    end if;
  end if;
  perform set_config('leda.workspace_id', previo, true);
  if v_contenido is not null then
    return query select v_contenido, v_tipo, v_clase, v_nombre;
  end if;
end $$;

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

commit;
