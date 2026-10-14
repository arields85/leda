\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0070_nada_vence_despues_de_su_objetivo.sql. La carga de tareas por la puerta del
-- equipo, para Dirección y los referentes (ADR 0023, decisión 3; porción J4 de
-- `odd/tasks/plataforma-jerarquias.md`, tarea J4a, con las decisiones del usuario del 2026-10-14
-- D1b, D3, D4, D10, D13 y D14; mecánica §3, §5 y §7).
--
-- - **Quién le carga a quién** (`como_carga`): Dirección, a cualquier integrante activo, también a
--   sí misma (D13); el referente de un área, a la gente de su área y a sí mismo, al referente de
--   otra área como un pedido a esa área (D14: lo de otra área se le pide a su referente, nunca
--   directo a su gente) y a Dirección como un pedido a Dirección (D1b). Un integrante, a nadie
--   (la propuesta llega con la J6).
-- - **Quién la revisa, guardado en cada tarea** (`task.revisor_membership_id`): el referente que
--   carga para su gente o para sí mismo; Dirección, para sí misma; lo que Dirección le carga a otra
--   persona, quien ella elija (D3: preseleccionado el referente del área de esa persona; puede ser
--   ella misma u otro referente, nunca quien la hace); un pedido a otra área, su referente, también
--   después de pasársela a alguien de su gente (D14); un pedido a Dirección, el referente que lo
--   pidió (D1b). `quien_revisa_la_tarea` lee primero el de la tarea y, sin él, la regla de
--   siempre (quien aprueba el trabajo de quien era la tarea): la visibilidad, la escalera y la
--   aprobación la siguen sin cambiar nada más. El pase lo conserva.
-- - **Quién la pidió** (`task.pedida_por_membership_id`): el referente que la pidió desde otra área
--   o a Dirección. La ve (`puede_ver_tarea`, `pedidas_de_la_sesion`) y es el único que la puede
--   reabrir cuando está terminada (`reabrir_tarea`, D14 paso 5): vuelve a `asignada`, con el
--   referente del área de la tarea como responsable (él decide quién la retoma), y queda escrita
--   en `reapertura_de_tarea` con su motivo. Desde la reapertura, la aprobación y la evidencia de
--   antes ya no cuentan para cerrarla (`motivo_no_cierra_tarea`, `tipos_de_evidencia_que_faltan`).
-- - **La carga por las dos puertas** (`cargar_tarea_web`, con el patrón de `crear_objetivo_web`): la
--   de administración, como hasta ahora, con D10 ("quién la decidió" es Dirección o el referente
--   del área de la tarea) y la elección de quién la revisa de D3; la del equipo, con la sesión de
--   la persona, que queda como quien la decidió. `cargar_tarea` queda como la puerta de
--   administración sin elegir quién la revisa. `opciones_de_la_carga_del_equipo` ofrece sólo a
--   quienes esa persona les puede cargar, con quién revisaría cada tarea; las dos opciones suman
--   las áreas con su referente y quiénes pueden revisar (D3).
--
-- Las funciones de la web son `security definer` de `leda_owner` y sólo las ejecuta `leda_app`; sus
-- ayudantes, nadie más que su dueño. Se deshace con `db/rollbacks/0071_la_carga_del_equipo.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0071 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0070 está aplicada y la 0071 no.
do $$ begin
  if to_regprocedure('leda.cargar_tarea(text, uuid, uuid, text, text, uuid, date, text, text[], uuid, text, timestamptz, uuid)') is null
     or position('vence_despues_del_objetivo' in
                 pg_get_functiondef('leda.cargar_tarea(text, uuid, uuid, text, text, uuid, date, text, text[], uuid, text, timestamptz, uuid)'::regprocedure)) = 0 then
    raise exception '0071 preflight failed: falta la 0070';
  end if;
  if to_regclass('leda.reapertura_de_tarea') is not null then
    raise exception '0071 ya está aplicada.';
  end if;
end $$;

-- --- Quién la revisa y quién la pidió, en cada tarea ----------------------------------------------

alter table task add column revisor_membership_id uuid;
alter table task add column pedida_por_membership_id uuid;
alter table task add constraint task_revisor
  foreign key (workspace_id, revisor_membership_id) references membership(workspace_id, id);
alter table task add constraint task_pedida_por
  foreign key (workspace_id, pedida_por_membership_id) references membership(workspace_id, id);
comment on column task.revisor_membership_id is
  'J4 (ADR 0023, decisión 3; decisiones D3, D4, D13 y D14 del usuario, migración 0071): quién revisa esta tarea, elegido al cargarla. Nulo: la regla de siempre, quien aprueba el trabajo de quien era la tarea (quien_revisa_la_tarea).';
comment on column task.pedida_por_membership_id is
  'J4 (decisiones D1b y D14 del usuario, migración 0071): el referente que la pidió desde otra área o a Dirección. La ve, y es el único que la reabre cuando está terminada (reabrir_tarea).';

-- --- La reapertura de una tarea pedida ------------------------------------------------------------

create table reapertura_de_tarea (
  id                                  uuid primary key default gen_random_uuid(),
  workspace_id                        uuid not null references workspace(id) on delete cascade,
  task_id                             uuid not null,
  pedida_por_membership_id            uuid not null,
  responsable_anterior_membership_id  uuid,
  responsable_membership_id           uuid not null,
  motivo                              text not null,
  at                                  timestamptz not null default clock_timestamp(),
  constraint reapertura_de_tarea_tarea
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade,
  constraint reapertura_de_tarea_pedida_por
    foreign key (workspace_id, pedida_por_membership_id) references membership(workspace_id, id),
  constraint reapertura_de_tarea_anterior
    foreign key (workspace_id, responsable_anterior_membership_id)
    references membership(workspace_id, id),
  constraint reapertura_de_tarea_responsable
    foreign key (workspace_id, responsable_membership_id) references membership(workspace_id, id),
  constraint reapertura_de_tarea_motivo
    check (btrim(motivo) <> '' and char_length(motivo) <= 500)
);

create index reapertura_de_tarea_tarea_at on reapertura_de_tarea (task_id, at);

comment on table reapertura_de_tarea is
  'J4 (decisión D14 del usuario, paso 5; migración 0071): quien pidió una tarea desde otra área la reabre, terminada, con su motivo; vuelve al referente del área de la tarea. Sólo se agrega, por reabrir_tarea. Desde la última, la aprobación y la evidencia de antes no cuentan para cerrarla.';

grant all privileges on reapertura_de_tarea to leda_owner, leda_admin;

alter table reapertura_de_tarea enable row level security;
alter table reapertura_de_tarea force row level security;
create policy aislamiento_espacio on reapertura_de_tarea
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

-- `leda_app` la lee (el cierre y, en la J4b, los avisos) y no la escribe: la escribe
-- `reabrir_tarea`. `leda_owner`, buscar y agregar.
revoke all on reapertura_de_tarea from public, leda_app;
grant select on reapertura_de_tarea to leda_app;
revoke all on reapertura_de_tarea from leda_owner;
grant select, insert on reapertura_de_tarea to leda_owner;

-- --- Quién revisa, quién ve, el pase y el cierre ----------------------------------------------------

-- Quién revisa una tarea: el elegido al cargarla (migración 0071) o, sin él, la regla de siempre.
create or replace function quien_revisa_la_tarea(p_task uuid)
returns uuid
language sql stable set search_path = leda, public, pg_temp as $$
  select coalesce(t.revisor_membership_id, m.aprobador_membership_id)
    from task t
    left join membership m on m.id = coalesce(t.era_de_membership_id, t.responsable_membership_id)
   where t.id = p_task;
$$;

-- Quién ve la página: también quien la pidió (migración 0071).
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
            or t.pedida_por_membership_id = m.id
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

-- El pase conserva quién revisa (migración 0071).
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
  -- Quien la revisaba la sigue revisando: el elegido al cargarla (migración 0071) o, sin él,
  -- quien aprueba el trabajo de quien era la tarea.
  new.revisa_membership_id := coalesce(t.revisor_membership_id,
                                       (select m.aprobador_membership_id from membership m
                                         where m.id = era));
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

-- El cierre: la aprobación, posterior a la última reapertura (migración 0071).
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
          -- Desde que quien la pidió la reabrió (migración 0071), sólo cuenta una aprobación
          -- posterior.
          and a.at > coalesce((select max(x.at) from reapertura_de_tarea x
                                where x.task_id = p_task), '-infinity'::timestamptz)
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

-- La evidencia, también posterior a la última reapertura (migración 0071).
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
            and e.at > greatest(
              coalesce((select max(a.at) from approval a
                         where a.sujeto_tipo = 'tarea' and a.sujeto_id = t.id
                           and a.decision = 'rechazado'),
                       '-infinity'::timestamptz),
              -- Ni la de antes de que quien la pidió la reabriera (migración 0071).
              coalesce((select max(x.at) from reapertura_de_tarea x where x.task_id = t.id),
                       '-infinity'::timestamptz))
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

-- --- Quién le carga a quién y quién la revisaría ----------------------------------------------------

-- Cómo le carga una tarea `p_quien` a `p_responsable` por la puerta del equipo (ADR 0023, decisión
-- 3; decisiones D1b, D4, D13 y D14 del usuario): `propia` (Dirección o un referente, a sí mismo),
-- `direccion` (Dirección, a cualquier otro integrante activo), `su_area` (un referente, a alguien de
-- un área de la que es referente), `pedido_a_direccion` (un referente, a Dirección) y
-- `pedido_a_otra_area` (un referente, al referente de otra área). Nulo: no le puede cargar (un
-- integrante, o un referente a alguien de otra área que no es su referente). Corre con la RLS de
-- quien llama, dentro de las funciones de la web, con el espacio ya fijado.
create or replace function como_carga(p_quien uuid, p_responsable uuid)
returns text
language sql stable set search_path = leda, public, pg_temp as $$
  with quien as (
    select m.id, r.autoridad_final,
           array(select a.id from area a where a.referente_membership_id = m.id) as areas
      from membership m join rol r on r.id = m.rol_id
     where m.id = p_quien and m.activo
  ),
  responsable as (
    select m.id, m.area_id, r.autoridad_final,
           exists (select 1 from area a where a.referente_membership_id = m.id) as es_referente
      from membership m join rol r on r.id = m.rol_id
     where m.id = p_responsable and m.activo
  )
  select case
           when q.id = p.id and (q.autoridad_final or cardinality(q.areas) > 0) then 'propia'
           when q.autoridad_final then 'direccion'
           when cardinality(q.areas) = 0 then null
           when p.area_id = any (q.areas) then 'su_area'
           when p.autoridad_final then 'pedido_a_direccion'
           when p.es_referente then 'pedido_a_otra_area'
         end
    from quien q cross join responsable p;
$$;

-- Quién revisaría la tarea que `p_quien` le carga a `p_responsable` (`p_como`, de `como_carga`):
-- quien la carga, si es suya, de su gente o un pedido a Dirección (D4, D13 y D1b); el referente que
-- la recibe, si es un pedido a otra área (D14); y lo que Dirección le carga a otra persona, el
-- referente del área de esa persona (lo que la web le preselecciona, D3) o, si ese referente es
-- quien la hace o no está activo, la misma Dirección.
create or replace function quien_revisaria(p_quien uuid, p_responsable uuid, p_como text)
returns uuid
language sql stable set search_path = leda, public, pg_temp as $$
  select case p_como
           when 'propia' then p_quien
           when 'su_area' then p_quien
           when 'pedido_a_direccion' then p_quien
           when 'pedido_a_otra_area' then p_responsable
           when 'direccion' then coalesce(
             (select a.referente_membership_id
                from membership m
                join area a on a.id = m.area_id
                join membership ref on ref.id = a.referente_membership_id and ref.activo
               where m.id = p_responsable and a.referente_membership_id <> p_responsable),
             p_quien)
         end;
$$;

-- Quién puede ser elegido para revisar una tarea (D3): un integrante activo que es Dirección o el
-- referente de un área.
create or replace function puede_ser_quien_revisa(p_membership_id uuid)
returns boolean
language sql stable set search_path = leda, public, pg_temp as $$
  select exists (
    select 1 from membership m join rol r on r.id = m.rol_id
     where m.id = p_membership_id and m.activo
       and (r.autoridad_final
            or exists (select 1 from area a where a.referente_membership_id = m.id)));
$$;

-- Quién carga por la puerta del equipo: la persona de la sesión (que deja fijado su espacio), si
-- sigue activa y es Dirección o el referente de un área. Un espacio pedido que no es el suyo no
-- existe para ella. Como `quien_crea_el_objetivo`: la llaman las funciones de la web.
create or replace function quien_carga_en_el_equipo(p_token_hash text, p_workspace_id uuid)
returns jsonb
language plpgsql set search_path = leda, public, pg_temp as $$
declare v_sesion uuid;
        v_espacio uuid;
        v_persona uuid;
        v_usuario uuid;
        v_es_autoridad boolean;
        v_es_referente boolean;
begin
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
  select m.app_user_id, r.autoridad_final,
         exists (select 1 from area a where a.referente_membership_id = m.id)
    into v_usuario, v_es_autoridad, v_es_referente
    from membership m join rol r on r.id = m.rol_id
   where m.id = v_persona and m.activo;
  if v_usuario is null then
    return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
      jsonb_build_object('campo', 'sesion', 'motivo', 'sin_sesion')));
  end if;
  if not (coalesce(v_es_autoridad, false) or coalesce(v_es_referente, false)) then
    return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
      jsonb_build_object('campo', 'sesion', 'motivo', 'sin_autoridad')));
  end if;
  return jsonb_build_object('ok', true, 'puerta', 'equipo', 'sesion_id', v_sesion,
                            'workspace_id', v_espacio, 'app_user_id', v_usuario,
                            'membership_id', v_persona, 'autoridad_final', v_es_autoridad);
end $$;

-- --- Las opciones de la carga, por las dos puertas ---------------------------------------------------

-- Lo que el formulario necesita para cargar en un espacio (migraciones 0062, 0064 y 0067), con el
-- espacio ya fijado por quien llama: los objetivos abiertos, las tareas que se pueden esperar, los
-- integrantes activos (con quién revisaría sus tareas por la regla de siempre y si tienen Leda
-- conectada), la evidencia de cada área y los días hábiles. Migración 0071: las áreas con su
-- referente (D10 y la explicación de D14) y quiénes pueden revisar una tarea (D3).
create or replace function opciones_de_la_carga_en(p_workspace_id uuid, p_ahora timestamptz)
returns jsonb
language plpgsql stable set search_path = leda, public, pg_temp as $$
declare v_espacio workspace%rowtype;
        v_hoy date;
        v_desde date;
        v_hora_fin time;
        v_hasta date;
begin
  select * into v_espacio from workspace w where w.id = p_workspace_id;
  v_hoy := (coalesce(p_ahora, now()) at time zone v_espacio.zona_horaria)::date;
  v_hasta := (v_hoy + interval '6 months')::date;
  -- Hoy se ofrece sólo si la jornada del espacio no cerró: la tarea vence a esa hora, y cargada
  -- después nacería vencida (migración 0064).
  select c.hora_fin into v_hora_fin from work_calendar c where c.workspace_id = v_espacio.id;
  v_desde := case when v_hora_fin is not null
                       and (coalesce(p_ahora, now()) at time zone v_espacio.zona_horaria)::time
                           >= v_hora_fin
                  then v_hoy + 1 else v_hoy end;
  return jsonb_build_object(
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
    -- Las áreas con su referente activo (migración 0071): quién decide en cada una (D10) y a quién
    -- se le pide lo de otra área (D14).
    'areas', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', a.id, 'nombre', a.nombre,
               'referente', case when ref.id is null then null
                                 else jsonb_build_object('membership_id', ref.id,
                                                         'nombre', refu.nombre) end)
             order by a.nombre, a.id)
        from area a
        left join membership ref on ref.id = a.referente_membership_id and ref.activo
        left join app_user refu on refu.id = ref.app_user_id), '[]'::jsonb),
    -- Quiénes pueden revisar una tarea si quien carga lo elige (D3; migración 0071): Dirección y
    -- los referentes de área activos.
    'revisores', coalesce((
      select jsonb_agg(jsonb_build_object(
               'membership_id', m.id, 'nombre', u.nombre,
               'autoridad_final', r.autoridad_final,
               'areas', coalesce((select jsonb_agg(a.nombre order by a.nombre, a.id)
                                    from area a where a.referente_membership_id = m.id),
                                 '[]'::jsonb))
             order by u.nombre, m.id)
        from membership m
        join app_user u on u.id = m.app_user_id
        join rol r on r.id = m.rol_id
       where m.activo and puede_ser_quien_revisa(m.id)), '[]'::jsonb),
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
end $$;

-- La puerta de administración: la sesión de administración vigente y el espacio, como siempre.
create or replace function opciones_de_la_carga(
    p_token_hash text, p_workspace_id uuid, p_ahora timestamptz)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_administrador uuid;
        v_espacio workspace%rowtype;
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
  v_resultado := opciones_de_la_carga_en(v_espacio.id, p_ahora);
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

-- La puerta del equipo (migración 0071): sólo Dirección y los referentes, en su espacio. Los
-- integrantes son sólo aquellos a quienes esa persona les puede cargar (`como_carga`), cada uno
-- con cómo (`como`) y con quién revisaría la tarea (`revisa`: para Dirección, el que se le
-- preselecciona). `yo` dice quién carga y si elige quién revisa (Dirección, D3).
create or replace function opciones_de_la_carga_del_equipo(p_token_hash text, p_ahora timestamptz)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_quien jsonb;
        v_persona uuid;
        v_resultado jsonb;
begin
  v_quien := quien_carga_en_el_equipo(p_token_hash, null);
  if not (v_quien ->> 'ok')::boolean then
    perform set_config('leda.workspace_id', previo, true);
    return v_quien;
  end if;
  v_persona := (v_quien ->> 'membership_id')::uuid;
  v_resultado := opciones_de_la_carga_en((v_quien ->> 'workspace_id')::uuid, p_ahora);
  v_resultado := v_resultado || jsonb_build_object(
    'integrantes', coalesce((
      select jsonb_agg(i.fila || jsonb_build_object(
               'como', c.como,
               'revisa', (select jsonb_build_object('membership_id', ref.id, 'nombre', u.nombre)
                            from membership ref join app_user u on u.id = ref.app_user_id
                           where ref.id = quien_revisaria(v_persona, c.id, c.como)))
             order by i.orden)
        from jsonb_array_elements(v_resultado -> 'integrantes') with ordinality i(fila, orden)
        cross join lateral (select (i.fila ->> 'membership_id')::uuid as id) m
        cross join lateral (select m.id, como_carga(v_persona, m.id) as como) c
       where c.como is not null), '[]'::jsonb),
    'yo', (select jsonb_build_object('membership_id', m.id, 'nombre', u.nombre,
                                     'autoridad_final', r.autoridad_final,
                                     'elige_quien_revisa', r.autoridad_final)
             from membership m join app_user u on u.id = m.app_user_id
             join rol r on r.id = m.rol_id
            where m.id = v_persona));
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

-- --- La carga, por las dos puertas ---------------------------------------------------------------------

-- La carga de una tarea comprometida desde la web (migraciones 0062, 0064, 0067 y 0070; migración
-- 0071, J4). `p_puerta`: `administracion` (la sesión de administración, en el espacio pedido; quién
-- la decidió lo declara quien carga, y tiene que ser Dirección o el referente del área de la tarea,
-- D10; quién la revisa se puede elegir, D3, o es la regla de siempre) o `equipo` (la sesión de
-- Dirección o de un referente, en su espacio; sólo a quienes les puede cargar, `como_carga`; quien
-- carga es quien la decidió; quién la revisa sale de `quien_revisaria`, y Dirección lo puede
-- elegir, D3). Todo lo demás, como siempre: la clave de un solo uso, los rechazos todos juntos, la
-- espera, el evento `asignada` y la auditoría `cargar_tarea`, con la puerta, la sesión, quién la
-- pidió y quién la revisa.
create or replace function cargar_tarea_web(
    p_puerta text, p_token_hash text, p_workspace_id uuid, p_objective_id uuid, p_titulo text,
    p_descripcion text, p_responsable_membership_id uuid, p_fecha date, p_criterio text,
    p_evidencia text[], p_decidio_membership_id uuid, p_revisa_membership_id uuid, p_clave text,
    p_ahora timestamptz, p_espera_task_id uuid default null)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_quien jsonb;
        v_sesion uuid;
        v_usuario uuid;
        v_persona uuid;
        v_espacio workspace%rowtype;
        v_objetivo objective%rowtype;
        v_espera task%rowtype;
        v_responsable membership%rowtype;
        v_revisa membership%rowtype;
        v_politica task_evidence_policy%rowtype;
        v_previa carga_de_tarea%rowtype;
        v_es_autoridad boolean;
        v_conectado boolean;
        v_como text;
        v_revisa_id uuid;
        v_pedida_por uuid;
        v_hoy date;
        v_hora_fin time;
        v_huella text;
        v_tarea uuid;
        v_errores jsonb := '[]'::jsonb;
        v_avisos jsonb := '[]'::jsonb;
        v_resultado jsonb;
begin
  -- La sesión de la puerta, en cada llamada.
  if p_puerta = 'administracion' then
    select s.sesion_id, s.app_user_id into v_sesion, v_usuario
      from sesion_de_administracion_vigente(p_token_hash) s;
    if v_usuario is null then
      return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'sesion', 'motivo', 'sin_sesion')));
    end if;
    select * into v_espacio from workspace w where w.id = p_workspace_id;
    if v_espacio.id is null then
      return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'espacio', 'motivo', 'no_existe')));
    end if;
  elsif p_puerta = 'equipo' then
    v_quien := quien_carga_en_el_equipo(p_token_hash, p_workspace_id);
    if not (v_quien ->> 'ok')::boolean then
      perform set_config('leda.workspace_id', previo, true);
      return v_quien;
    end if;
    v_sesion := (v_quien ->> 'sesion_id')::uuid;
    v_usuario := (v_quien ->> 'app_user_id')::uuid;
    v_persona := (v_quien ->> 'membership_id')::uuid;
    select * into v_espacio from workspace w where w.id = (v_quien ->> 'workspace_id')::uuid;
  else
    return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
      jsonb_build_object('campo', 'sesion', 'motivo', 'sin_sesion')));
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
      -- La huella de la puerta de administración es la de antes (la espera y quién la revisa
      -- entran sólo si los hay): una carga de antes de la 0071 tiene la misma huella.
      v_huella := encode(sha256(convert_to((
        case p_puerta
          when 'administracion' then jsonb_build_object(
            'administrador', v_usuario, 'objetivo', p_objective_id, 'titulo', p_titulo,
            'descripcion', p_descripcion, 'responsable', p_responsable_membership_id,
            'fecha', p_fecha, 'criterio', p_criterio, 'evidencia', to_jsonb(p_evidencia),
            'decidio', p_decidio_membership_id)
          else jsonb_build_object(
            'puerta', 'equipo', 'persona', v_persona, 'objetivo', p_objective_id,
            'titulo', p_titulo, 'descripcion', p_descripcion,
            'responsable', p_responsable_membership_id, 'fecha', p_fecha,
            'criterio', p_criterio, 'evidencia', to_jsonb(p_evidencia),
            'decidio', p_decidio_membership_id)
        end
        || case when p_espera_task_id is null then '{}'::jsonb
                else jsonb_build_object('espera', p_espera_task_id) end
        || case when p_revisa_membership_id is null then '{}'::jsonb
                else jsonb_build_object('revisa', p_revisa_membership_id) end)::text,
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

    -- Quién la revisa, si se eligió (D3): Dirección o el referente de un área, activo, y nunca
    -- quien la hace. Por la puerta del equipo lo elige sólo Dirección; un referente, no.
    if p_revisa_membership_id is not null and not puede_ser_quien_revisa(p_revisa_membership_id)
    then
      v_errores := v_errores || jsonb_build_object('campo', 'revisa',
                                                   'motivo', 'no_puede_revisarla');
    end if;

    -- El responsable: integrante activo de este espacio.
    if p_responsable_membership_id is null then
      v_errores := v_errores || jsonb_build_object('campo', 'responsable', 'motivo', 'falta');
    else
      select * into v_responsable from membership m
       where m.id = p_responsable_membership_id and m.activo for share;
      if v_responsable.id is null then
        v_errores := v_errores || jsonb_build_object('campo', 'responsable',
                                                     'motivo', 'no_es_integrante_activo');
      elsif p_puerta = 'equipo' then
        -- A quién le puede cargar quien carga, y quién la revisaría (ADR 0023, decisión 3).
        v_como := como_carga(v_persona, v_responsable.id);
        if v_como is null then
          v_errores := v_errores || jsonb_build_object('campo', 'responsable',
                                                       'motivo', 'no_le_puede_cargar');
        else
          v_revisa_id := quien_revisaria(v_persona, v_responsable.id, v_como);
          if p_revisa_membership_id is not null then
            if v_como <> 'direccion' then
              if p_revisa_membership_id <> v_revisa_id then
                v_errores := v_errores || jsonb_build_object('campo', 'revisa',
                                                             'motivo', 'no_corresponde');
              end if;
            elsif p_revisa_membership_id = v_responsable.id then
              v_errores := v_errores || jsonb_build_object('campo', 'revisa',
                                                           'motivo', 'es_quien_la_hace');
            else
              v_revisa_id := p_revisa_membership_id;
            end if;
          end if;
          if v_como in ('pedido_a_otra_area', 'pedido_a_direccion') then
            v_pedida_por := v_persona;
          end if;
        end if;
      elsif p_revisa_membership_id is not null then
        -- La puerta de administración elige quién la revisa como Dirección (D3).
        if p_revisa_membership_id = v_responsable.id then
          v_errores := v_errores || jsonb_build_object('campo', 'revisa',
                                                       'motivo', 'es_quien_la_hace');
        else
          v_revisa_id := p_revisa_membership_id;
        end if;
      else
        -- La regla de siempre: alguien activo que no sea él revisa su trabajo.
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
      end if;
      if v_responsable.id is not null then
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
    -- Una tarea no vence después que su objetivo (decisión 6 del usuario, 2026-10-14; migración
    -- 0070): el objetivo se demoraría. La salida es una fecha hasta ese día (`hasta`).
    elsif v_objetivo.fecha_objetivo is not null and p_fecha > v_objetivo.fecha_objetivo then
      v_errores := v_errores || jsonb_build_object('campo', 'fecha',
                                                   'motivo', 'vence_despues_del_objetivo',
                                                   'hasta', v_objetivo.fecha_objetivo);
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

    -- Quién la decidió. Por la puerta de administración lo declara quien carga (ADR 0017,
    -- decisión 2): un integrante activo que es Dirección o el referente del área de la tarea (D10).
    -- Por la del equipo, quien carga (ADR 0023, decisión 3): no se declara otro.
    if p_puerta = 'equipo' then
      if p_decidio_membership_id is not null and p_decidio_membership_id <> v_persona then
        v_errores := v_errores || jsonb_build_object('campo', 'decidio',
                                                     'motivo', 'no_corresponde');
      end if;
    elsif p_decidio_membership_id is null then
      v_errores := v_errores || jsonb_build_object('campo', 'decidio', 'motivo', 'falta');
    elsif not exists (select 1 from membership m
                       where m.id = p_decidio_membership_id and m.activo) then
      v_errores := v_errores || jsonb_build_object('campo', 'decidio',
                                                   'motivo', 'no_es_integrante_activo');
    elsif not exists (
        select 1 from membership m join rol r on r.id = m.rol_id
         where m.id = p_decidio_membership_id
           and (r.autoridad_final
                or exists (select 1 from area a
                            where a.referente_membership_id = m.id
                              and (v_responsable.id is null
                                   or a.id = v_responsable.area_id)))) then
      v_errores := v_errores || jsonb_build_object('campo', 'decidio',
                                                   'motivo', 'no_puede_decidirla');
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
                        evidencia_requerida, evidencia_policy_version, revisor_membership_id,
                        pedida_por_membership_id)
      values (v_espacio.id, v_objetivo.id, btrim(p_titulo), nullif(btrim(p_descripcion), ''),
              v_responsable.area_id, v_responsable.id,
              (p_fecha + v_hora_fin) at time zone v_espacio.zona_horaria, btrim(p_criterio),
              p_evidencia, v_politica.version, v_revisa_id, v_pedida_por)
      returning id into v_tarea;
      insert into task_state_event (task_id, estado_nuevo, actor_kind, actor_app_user_id, motivo)
      values (v_tarea, 'asignada', 'persona', v_usuario,
              case p_puerta
                when 'equipo' then case v_como
                  when 'pedido_a_otra_area' then 'pedida desde la web por el referente de otra área'
                  when 'pedido_a_direccion' then 'pedida a Dirección desde la web por un referente'
                  when 'direccion' then 'cargada desde la web por Dirección'
                  else 'cargada desde la web del equipo' end
                else 'cargada desde la web por un administrador de plataforma' end);
      if v_espera.id is not null then
        insert into dependency (workspace_id, origen_task_id, destino_task_id, tipo)
        values (v_espacio.id, v_espera.id, v_tarea, 'bloqueante');
      end if;
      perform auditar_acceso_web(
        v_espacio.id, v_usuario, 'persona', 'cargar_tarea', 'task', v_tarea,
        case p_puerta
          when 'equipo' then jsonb_build_object(
            'origen', 'web',
            'puerta', 'equipo',
            'sesion_web_id', v_sesion,
            'cargada_por_app_user_id', v_usuario,
            'cargada_por_membership_id', v_persona,
            'decidida_por_membership_id', v_persona,
            'decision_declarada_al_cargar', false,
            'como', v_como,
            'responsable_membership_id', v_responsable.id,
            'revisa_membership_id', v_revisa_id,
            'revisa_elegido', p_revisa_membership_id is not null,
            'pedida_por_membership_id', v_pedida_por,
            'objective_id', v_objetivo.id,
            'evidencia_policy_version', v_politica.version,
            'avisos', v_avisos)
          else jsonb_build_object(
            'origen', 'web',
            'puerta', 'administracion',
            'cargada_por_app_user_id', v_usuario,
            'decidida_por_membership_id', p_decidio_membership_id,
            'decision_declarada_al_cargar', true,
            'responsable_membership_id', v_responsable.id,
            'revisa_membership_id', coalesce(v_revisa_id, v_revisa.id),
            'revisa_elegido', p_revisa_membership_id is not null,
            'objective_id', v_objetivo.id,
            'evidencia_policy_version', v_politica.version,
            'sesion_de_administracion_id', v_sesion,
            'avisos', v_avisos)
        end
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

-- La de antes, por la puerta de administración y sin elegir quién la revisa: la misma carga.
create or replace function cargar_tarea(
    p_token_hash text, p_workspace_id uuid, p_objective_id uuid, p_titulo text,
    p_descripcion text, p_responsable_membership_id uuid, p_fecha date, p_criterio text,
    p_evidencia text[], p_decidio_membership_id uuid, p_clave text, p_ahora timestamptz,
    p_espera_task_id uuid default null)
returns jsonb
language sql security definer set search_path = leda, public, pg_temp as $$
  select cargar_tarea_web('administracion', p_token_hash, p_workspace_id, p_objective_id,
                          p_titulo, p_descripcion, p_responsable_membership_id, p_fecha,
                          p_criterio, p_evidencia, p_decidio_membership_id, null, p_clave,
                          p_ahora, p_espera_task_id);
$$;

-- --- La reapertura y lo que pidió cada uno --------------------------------------------------------

-- Quien pidió una tarea desde otra área (o a Dirección) la reabre, terminada, con su motivo (D14,
-- paso 5): vuelve a `asignada`, con el referente del área de la tarea como responsable, que decide
-- quién la retoma (si la tenía otro, ese cambio de manos lo hace la base, como un pase aplicado).
-- Queda en `reapertura_de_tarea`, con su evento de estado y su auditoría. Desde ahí, la aprobación y
-- la evidencia de antes no cuentan para cerrarla.
create or replace function reabrir_tarea(p_token_hash text, p_task_id uuid, p_motivo text)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_sesion uuid;
        v_espacio uuid;
        v_persona uuid;
        v_usuario uuid;
        v_tarea task%rowtype;
        v_referente uuid;
        v_reapertura uuid;
        v_errores jsonb := '[]'::jsonb;
        v_resultado jsonb;
begin
  select s.sesion_id, s.workspace_id, s.membership_id into v_sesion, v_espacio, v_persona
    from sesion_vigente(p_token_hash) s;
  if v_persona is null then
    return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
      jsonb_build_object('campo', 'sesion', 'motivo', 'sin_sesion')));
  end if;
  perform set_config('leda.workspace_id', v_espacio::text, true);

  <<reapertura>>
  begin
    select m.app_user_id into v_usuario from membership m where m.id = v_persona and m.activo;
    if v_usuario is null then
      v_resultado := jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'sesion', 'motivo', 'sin_sesion')));
      exit reapertura;
    end if;
    select * into v_tarea from task t where t.id = p_task_id for update;
    -- Sólo quien la pidió: para cualquier otro, como si no existiera.
    if v_tarea.id is null or v_tarea.pedida_por_membership_id is distinct from v_persona then
      v_resultado := jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'tarea', 'motivo', 'no_la_pediste')));
      exit reapertura;
    end if;
    if v_tarea.estado <> 'terminada' then
      v_errores := v_errores || jsonb_build_object('campo', 'tarea', 'motivo', 'no_esta_terminada');
    end if;
    if nullif(btrim(p_motivo), '') is null then
      v_errores := v_errores || jsonb_build_object('campo', 'motivo', 'motivo', 'falta');
    elsif char_length(btrim(p_motivo)) > 500 then
      v_errores := v_errores || jsonb_build_object('campo', 'motivo', 'motivo', 'demasiado_largo');
    end if;
    select a.referente_membership_id into v_referente
      from area a join membership m on m.id = a.referente_membership_id and m.activo
     where a.id = v_tarea.area_id;
    if v_referente is null then
      v_errores := v_errores || jsonb_build_object('campo', 'tarea', 'motivo', 'sin_referente');
    end if;
    if jsonb_array_length(v_errores) > 0 then
      v_resultado := jsonb_build_object('ok', false, 'errores', v_errores);
      exit reapertura;
    end if;

    insert into reapertura_de_tarea (workspace_id, task_id, pedida_por_membership_id,
                                     responsable_anterior_membership_id,
                                     responsable_membership_id, motivo)
    values (v_espacio, v_tarea.id, v_persona, v_tarea.responsable_membership_id, v_referente,
            btrim(p_motivo))
    returning id into v_reapertura;
    if v_tarea.responsable_membership_id is distinct from v_referente then
      perform set_config('leda.aplicando_pase', '1', true);
      update task
         set responsable_membership_id = v_referente,
             era_de_membership_id = coalesce(era_de_membership_id, responsable_membership_id),
             actualizado_en = clock_timestamp()
       where id = v_tarea.id;
      perform set_config('leda.aplicando_pase', '0', true);
    end if;
    insert into task_state_event (task_id, estado_anterior, estado_nuevo, actor_kind,
                                  actor_app_user_id, motivo)
    values (v_tarea.id, 'terminada', 'asignada', 'persona', v_usuario,
            'reabierta por quien la pidió');
    perform auditar_acceso_web(
      v_espacio, v_usuario, 'persona', 'reabrir_tarea', 'task', v_tarea.id,
      jsonb_build_object(
        'origen', 'web',
        'puerta', 'equipo',
        'sesion_web_id', v_sesion,
        'reapertura_id', v_reapertura,
        'pedida_por_membership_id', v_persona,
        'responsable_anterior_membership_id', v_tarea.responsable_membership_id,
        'responsable_membership_id', v_referente,
        'revisa_membership_id', quien_revisa_la_tarea(v_tarea.id)));
    v_resultado := jsonb_build_object('ok', true, 'task_id', v_tarea.id,
                                      'reapertura_id', v_reapertura,
                                      'responsable_membership_id', v_referente);
  end reapertura;

  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

-- Lo que pidió una persona desde otra área o a Dirección (D14 y D1b): las abiertas y las terminadas
-- de los últimos 30 días, con su estado y quién la tiene. Corre con la RLS de quien llama y
-- `leda_app` no la ejecuta: la web llama a `pedidas_de_la_sesion`, con la persona de la sesión.
create or replace function pedidas_que_ve(p_membership_id uuid, p_ahora timestamptz)
returns table (task_id uuid, titulo text, estado text, fecha_objetivo timestamptz,
               responsable text, area text, terminada_en timestamptz)
language sql stable set search_path = leda, public, pg_temp as $$
  select x.id, x.titulo, x.estado, x.fecha_objetivo, x.responsable, x.area, x.terminada_en
    from (
      select t.id, t.titulo, t.estado::text as estado, t.fecha_objetivo, u.nombre as responsable,
             a.nombre as area,
             case when t.estado = 'terminada' then
               coalesce((select max(e.at) from task_state_event e
                          where e.task_id = t.id and e.estado_nuevo = 'terminada'),
                        t.actualizado_en) end as terminada_en
        from task t
        join membership yo on yo.id = p_membership_id and yo.activo
                          and yo.workspace_id = t.workspace_id
        join area a on a.id = t.area_id
        left join membership rm on rm.id = t.responsable_membership_id
        left join app_user u on u.id = rm.app_user_id
       where t.pedida_por_membership_id = yo.id
         and t.estado <> 'cancelada') x
   where x.terminada_en is null
      or x.terminada_en >= coalesce(p_ahora, now()) - interval '30 days'
   order by x.terminada_en is not null, x.fecha_objetivo nulls last, x.titulo, x.id;
$$;

create or replace function pedidas_de_la_sesion(p_token_hash text, p_ahora timestamptz)
returns table (task_id uuid, titulo text, estado text, fecha_objetivo timestamptz,
               responsable text, area text, terminada_en timestamptz)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare persona uuid;
begin
  -- La persona sale de la sesión, que deja fijado su espacio; si no entra, nada.
  select s.membership_id into persona from sesion_vigente(p_token_hash) s;
  if persona is null then
    return;
  end if;
  return query select q.* from pedidas_que_ve(persona, p_ahora) q;
end $$;

-- --- Dueños y privilegios ----------------------------------------------------------------------------

alter function como_carga(uuid, uuid) owner to leda_owner;
alter function quien_revisaria(uuid, uuid, text) owner to leda_owner;
alter function puede_ser_quien_revisa(uuid) owner to leda_owner;
alter function quien_carga_en_el_equipo(text, uuid) owner to leda_owner;
alter function opciones_de_la_carga_en(uuid, timestamptz) owner to leda_owner;
alter function opciones_de_la_carga_del_equipo(text, timestamptz) owner to leda_owner;
alter function cargar_tarea_web(text, text, uuid, uuid, text, text, uuid, date, text, text[],
                                uuid, uuid, text, timestamptz, uuid) owner to leda_owner;
alter function reabrir_tarea(text, uuid, text) owner to leda_owner;
alter function pedidas_que_ve(uuid, timestamptz) owner to leda_owner;
alter function pedidas_de_la_sesion(text, timestamptz) owner to leda_owner;

revoke execute on function como_carga(uuid, uuid) from public;
revoke execute on function quien_revisaria(uuid, uuid, text) from public;
revoke execute on function puede_ser_quien_revisa(uuid) from public;
revoke execute on function quien_carga_en_el_equipo(text, uuid) from public;
revoke execute on function opciones_de_la_carga_en(uuid, timestamptz) from public;
revoke execute on function opciones_de_la_carga_del_equipo(text, timestamptz) from public;
revoke execute on function cargar_tarea_web(text, text, uuid, uuid, text, text, uuid, date, text,
                                            text[], uuid, uuid, text, timestamptz, uuid)
  from public;
revoke execute on function reabrir_tarea(text, uuid, text) from public;
revoke execute on function pedidas_que_ve(uuid, timestamptz) from public;
revoke execute on function pedidas_de_la_sesion(text, timestamptz) from public;
grant execute on function opciones_de_la_carga_del_equipo(text, timestamptz) to leda_app;
grant execute on function cargar_tarea_web(text, text, uuid, uuid, text, text, uuid, date, text,
                                           text[], uuid, uuid, text, timestamptz, uuid)
  to leda_app;
grant execute on function reabrir_tarea(text, uuid, text) to leda_app;
grant execute on function pedidas_de_la_sesion(text, timestamptz) to leda_app;

commit;
