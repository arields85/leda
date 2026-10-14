\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0068_los_objetivos_desde_la_web.sql. Las decisiones del usuario del 2026-10-14
-- sobre los objetivos desde la web (porción J3 de `odd/tasks/plataforma-jerarquias.md`, tarea
-- J3-2b; ADR 0023, decisión 1):
--
-- - **El objetivo lleva fecha, obligatoria,** con el mismo calendario que las tareas: un día hábil
--   del espacio (`es_dia_habil`), hoy o después, y hoy sólo si la jornada del espacio no cerró;
--   los mismos rechazos que `cargar_tarea` (`falta`, `en_el_pasado`, `no_es_dia_habil`,
--   `ya_cerro_el_dia`). Se guarda en `objective.fecha_objetivo` y entra en la huella de la clave.
-- - **El referente es siempre un referente activo de un área** del espacio
--   (`area.referente_membership_id`, ADR 0019, decisión 7b), no cualquier integrante: uno que no
--   lo es se rechaza con `no_es_referente_de_un_area`.
-- - `opciones_del_objetivo` ofrece, en lugar de `integrantes`, `referentes` (con las áreas de cada
--   uno), y además `hoy` y el `calendario` (los días hábiles de hoy a un año, los feriados y los
--   días de la semana que se trabaja), como `opciones_de_la_carga`.
--
-- Las dos funciones cambian de firma (`p_fecha` y `p_ahora`, el reloj del espacio, como en
-- `cargar_tarea`): se borran las de la 0068 y se crean las nuevas, con el mismo dueño
-- (`leda_owner`), `security definer`, `search_path` fijado y `execute` sólo para `leda_app`. No
-- toca tablas: los objetivos ya creados quedan como estaban (sin fecha, si se crearon sin ella).
-- Se deshace con `db/rollbacks/0069_la_fecha_y_el_referente_del_objetivo.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0069 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0068 está aplicada y la 0069 no.
do $$ begin
  if to_regprocedure('leda.crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid, text)')
     is null then
    if to_regprocedure('leda.crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid, date, text, timestamptz)')
       is not null then
      raise exception '0069 ya está aplicada.';
    end if;
    raise exception '0069 preflight failed: falta la 0068';
  end if;
end $$;

drop function crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid, text);
drop function opciones_del_objetivo(text, text, uuid);

-- --- Las opciones del formulario ---------------------------------------------------------------

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

-- --- La creación ---------------------------------------------------------------------------------

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

alter function opciones_del_objetivo(text, text, uuid, timestamptz) owner to leda_owner;
alter function crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid, date, text,
                                  timestamptz) owner to leda_owner;
revoke execute on function opciones_del_objetivo(text, text, uuid, timestamptz) from public;
revoke execute on function crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid,
                                              date, text, timestamptz) from public;
grant execute on function opciones_del_objetivo(text, text, uuid, timestamptz) to leda_app;
grant execute on function crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid,
                                             date, text, timestamptz) to leda_app;

commit;
