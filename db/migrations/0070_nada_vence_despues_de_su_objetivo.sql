\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0069_la_fecha_y_el_referente_del_objetivo.sql. Nada vence después que el objetivo
-- del que forma parte (decisiones 5 y 6 del usuario, 2026-10-14; porción J3 de
-- `odd/tasks/plataforma-jerarquias.md`, tarea J3-3b; mecánica §5: un objetivo no cierra hasta que
-- cierran sus tareas y sus objetivos hijos):
--
-- - `cargar_tarea` rechaza una tarea cuya fecha es posterior a la de su objetivo, cuando el
--   objetivo tiene fecha (los objetivos iniciales del pack no la tienen y no ponen límite), con
--   `fecha`: `vence_despues_del_objetivo` y el día del objetivo en `hasta`. Hasta ahora era el
--   aviso `despues_del_objetivo`, que no bloqueaba. Nada más cambia: la huella de la clave, la
--   auditoría y los demás rechazos quedan como estaban. Seguir con esa fecha pidiéndole la
--   aprobación al referente del objetivo llega con la porción J6.
-- - `crear_objetivo_web` rechaza un objetivo que vence después que el objetivo del que cuelga,
--   cuando ese padre vale como padre y tiene fecha, con `fecha`: `vence_despues_del_padre` y el
--   día del padre en `hasta`. La salida es otra fecha, o colgarlo de otro lugar.
-- - `opciones_del_objetivo` suma a cada padre posible de qué cuelga él (`padre_id`): con su fecha,
--   la web avisa antes de confirmar y "cargarlo aparte" lo pasa a colgar del padre de ese padre.
--
-- Mismas firmas: `create or replace` conserva el dueño (`leda_owner`), el `search_path` fijado y
-- los privilegios (sólo `leda_app`). No toca tablas. Se deshace con
-- `db/rollbacks/0070_nada_vence_despues_de_su_objetivo.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0070 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0067 está aplicada (la carga con la espera existe) y la 0070 no.
do $$ begin
  if to_regprocedure('leda.cargar_tarea(text, uuid, uuid, text, text, uuid, date, text, text[], uuid, text, timestamptz, uuid)') is null then
    raise exception '0070 preflight failed: falta la 0067';
  end if;
  if position('vence_despues_del_objetivo' in
              pg_get_functiondef('leda.cargar_tarea(text, uuid, uuid, text, text, uuid, date, text, text[], uuid, text, timestamptz, uuid)'::regprocedure)) > 0 then
    raise exception '0070 ya está aplicada.';
  end if;
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
    -- Una tarea no vence después que su objetivo (decisión 6 del usuario, 2026-10-14; migración
    -- 0070): el objetivo se demoraría. Antes era un aviso que no bloqueaba; ahora se rechaza, con
    -- el día del objetivo (`hasta`), y la salida es una fecha hasta ese día.
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
    -- tareas), con los tipos que admite. Con su fecha y de qué cuelga él (migración 0070): la web
    -- avisa antes de confirmar que un hijo vencería después, y "cargarlo aparte" lo pasa a colgar
    -- del padre de ese padre.
    'padres', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', o.id, 'titulo', o.titulo, 'tipo', o.tipo, 'estado', o.estado,
               'fecha_objetivo', o.fecha_objetivo, 'padre_id', o.parent_id,
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
    -- Un objetivo no vence después que el objetivo del que cuelga (decisión 5 del usuario,
    -- 2026-10-14; migración 0070): lo que cuelga es parte del padre, y el padre no cierra hasta
    -- que cierran sus hijos (mecánica §5). Sólo si el padre vale como padre y tiene fecha (los
    -- objetivos iniciales del pack no la tienen); con el día del padre (`hasta`).
    elsif v_padre.id is not null and v_padre.estado in ('activo', 'propuesto')
          and v_padre.tipo <> 'operativo' and v_padre.fecha_objetivo is not null
          and p_fecha > v_padre.fecha_objetivo then
      v_errores := v_errores || jsonb_build_object('campo', 'fecha',
                                                   'motivo', 'vence_despues_del_padre',
                                                   'hasta', v_padre.fecha_objetivo);
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

commit;
