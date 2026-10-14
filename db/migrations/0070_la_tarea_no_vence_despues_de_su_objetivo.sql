\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0069_la_fecha_y_el_referente_del_objetivo.sql. Una tarea no vence después que su
-- objetivo (decisión 6 del usuario, 2026-10-14; porción J3 de `odd/tasks/plataforma-jerarquias.md`,
-- tarea J3-3b; mecánica §5: el objetivo no cierra hasta que cierran sus tareas):
--
-- - `cargar_tarea` rechaza una tarea cuya fecha es posterior a la de su objetivo, cuando el
--   objetivo tiene fecha (los objetivos iniciales del pack no la tienen y no ponen límite), con
--   `fecha`: `vence_despues_del_objetivo` y el día del objetivo en `hasta`. Hasta ahora era el
--   aviso `despues_del_objetivo`, que no bloqueaba. Nada más cambia: la huella de la clave, la
--   auditoría y los demás rechazos quedan como estaban. Seguir con esa fecha pidiéndole la
--   aprobación al referente del objetivo llega con la porción J6.
--
-- Misma firma: `create or replace` conserva el dueño (`leda_owner`), el `search_path` fijado y los
-- privilegios (sólo `leda_app`). No toca tablas. Se deshace con
-- `db/rollbacks/0070_la_tarea_no_vence_despues_de_su_objetivo.sql`.
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

commit;
