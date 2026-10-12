\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0061_la_puerta_de_administracion.sql. La carga de una tarea desde la puerta de
-- administración de la plataforma web (ADR 0022, decisiones 9, 11 y 12; ADR 0017, decisión 2;
-- porción 2, tarea P2-2 de `odd/tasks/plataforma-p2.md`).
--
-- - `es_dia_habil(espacio, fecha)`: el día hábil del espacio en SQL, el mismo que
--   `Calendario.es_habil` (`src/leda/calendario.py`): un día de `work_calendar.dias` que no es
--   feriado (`holiday`). Sin calendario, ningún día es hábil (falla cerrado). Corre con la RLS de
--   quien llama; la ejecutan las funciones de abajo (su dueño) y la consola.
-- - `opciones_de_la_carga`: lo que el formulario necesita para un espacio (los objetivos abiertos,
--   los integrantes activos con quién revisaría sus tareas y si tienen Leda conectada, la política
--   de evidencia de cada área y los días hábiles de los próximos seis meses).
-- - `cargar_tarea`: la carga. Comprueba la sesión de administración (el rol de plataforma
--   vigente, `sesion_de_administracion_vigente`) en cada llamada y que el espacio exista, y fija
--   ella misma ese espacio: la RLS no le deja encontrar un objetivo, una persona ni una clave de
--   otro espacio, así que nunca confía en un id sin comprobarlo (riesgo 4 de `docs/STATUS.md`).
--   Lo que no se carga (decisión 9) vuelve todo junto, como datos (`{ok: false, errores: [{campo,
--   motivo}]}`), no como una excepción; lo que se avisa y no bloquea, en `avisos`. Escribe la
--   tarea, su evento `asignada` (el estado sigue siendo la proyección de eventos) y su fila de
--   auditoría en el espacio de la tarea, con quién la cargó, quién la decidió (declarado por quien
--   la carga: nunca una aprobación hecha en Leda) y las versiones del paquete y del núcleo.
-- - Quién revisa una tarea es la regla única de la base (`quien_revisa_la_tarea`): quien aprueba
--   el trabajo del responsable. Sin nadie activo que la revise no se carga: nadie podría
--   aprobarla. La autoridad final sin aprobador se revisaría a sí misma.
-- - La fecha elegida se guarda al cierre de la jornada del espacio, en su zona (como las tareas
--   de las conversaciones de prueba): el día local es el que se eligió.
-- - `carga_de_tarea`: la clave de un solo uso de cada carga (un doble envío del formulario no
--   carga dos tareas). Con espacio y RLS forzada; `leda_app` no tiene ningún privilegio sobre
--   ella, sólo `execute` sobre las dos funciones de la web. La misma clave con los mismos datos
--   devuelve la misma tarea; con otros, se rechaza.
--
-- La versión de cada fila para editar (decisión 15) es de la porción 3: crear no pisa nada.
--
-- No crea, altera ni borra roles. Se deshace con
-- `db/rollbacks/0062_la_carga_de_tareas_desde_la_web.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0062 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0061 está aplicada y la 0062 no.
do $$ begin
  if to_regprocedure('leda.sesion_de_administracion_vigente(text)') is null then
    raise exception '0062 preflight failed: falta la 0061';
  end if;
  if to_regclass('leda.carga_de_tarea') is not null then
    raise exception '0062 ya está aplicada.';
  end if;
end $$;

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

grant all privileges on carga_de_tarea to leda_owner, leda_admin;

alter table carga_de_tarea enable row level security;
alter table carga_de_tarea force row level security;
create policy aislamiento_espacio on carga_de_tarea
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

-- `leda_app`: nada sobre la tabla, sólo `execute` sobre las funciones de la web.
revoke all on carga_de_tarea from public, leda_app;
-- `leda_owner`: lo que necesita `cargar_tarea`, buscar y agregar.
revoke all on carga_de_tarea from leda_owner;
grant select, insert on carga_de_tarea to leda_owner;

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
                  from generate_series(v_hoy, v_hasta, interval '1 day') g) d
         where es_dia_habil(v_espacio.id, d.dia)), '[]'::jsonb)));
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

create or replace function cargar_tarea(
    p_token_hash text, p_workspace_id uuid, p_objective_id uuid, p_titulo text,
    p_descripcion text, p_responsable_membership_id uuid, p_fecha date, p_criterio text,
    p_evidencia text[], p_decidio_membership_id uuid, p_clave text, p_ahora timestamptz)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_sesion uuid;
        v_administrador uuid;
        v_espacio workspace%rowtype;
        v_objetivo objective%rowtype;
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
      v_huella := encode(sha256(convert_to(jsonb_build_object(
        'administrador', v_administrador, 'objetivo', p_objective_id, 'titulo', p_titulo,
        'descripcion', p_descripcion, 'responsable', p_responsable_membership_id,
        'fecha', p_fecha, 'criterio', p_criterio, 'evidencia', to_jsonb(p_evidencia),
        'decidio', p_decidio_membership_id)::text, 'UTF8')), 'hex');
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

    -- La fecha: un día hábil del espacio, hoy o después (hoy, en su zona).
    v_hoy := (coalesce(p_ahora, now()) at time zone v_espacio.zona_horaria)::date;
    if p_fecha is null then
      v_errores := v_errores || jsonb_build_object('campo', 'fecha', 'motivo', 'falta');
    elsif p_fecha < v_hoy then
      v_errores := v_errores || jsonb_build_object('campo', 'fecha', 'motivo', 'en_el_pasado');
    elsif not es_dia_habil(v_espacio.id, p_fecha) then
      v_errores := v_errores || jsonb_build_object('campo', 'fecha', 'motivo', 'no_es_dia_habil');
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

    if jsonb_array_length(v_errores) > 0 then
      v_resultado := jsonb_build_object('ok', false, 'errores', v_errores);
      exit carga;
    end if;

    -- Todo en orden: la tarea, su evento, su auditoría y su clave.
    select c.hora_fin into v_hora_fin from work_calendar c where c.workspace_id = v_espacio.id;
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
        'avisos', v_avisos));
    insert into carga_de_tarea (workspace_id, clave, huella, task_id, avisos)
    values (v_espacio.id, p_clave, v_huella, v_tarea, v_avisos);
    v_resultado := jsonb_build_object('ok', true, 'task_id', v_tarea, 'avisos', v_avisos,
                                      'repetida', false);
  end carga;

  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

alter function es_dia_habil(uuid, date) owner to leda_owner;
alter function opciones_de_la_carga(text, uuid, timestamptz) owner to leda_owner;
alter function cargar_tarea(text, uuid, uuid, text, text, uuid, date, text, text[], uuid, text,
                            timestamptz) owner to leda_owner;

revoke execute on function es_dia_habil(uuid, date) from public;
revoke execute on function opciones_de_la_carga(text, uuid, timestamptz) from public;
revoke execute on function cargar_tarea(text, uuid, uuid, text, text, uuid, date, text, text[],
                                        uuid, text, timestamptz) from public;
-- La consola (`leda_admin`): el día hábil. La web (`leda_app`): las opciones y la carga.
grant execute on function es_dia_habil(uuid, date) to leda_admin;
grant execute on function opciones_de_la_carga(text, uuid, timestamptz) to leda_app;
grant execute on function cargar_tarea(text, uuid, uuid, text, text, uuid, date, text, text[],
                                       uuid, text, timestamptz) to leda_app;

commit;
