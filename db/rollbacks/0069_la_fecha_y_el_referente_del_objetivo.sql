\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0069_la_fecha_y_el_referente_del_objetivo.sql.
--
-- Borra `opciones_del_objetivo` y `crear_objetivo_web` con la fecha y vuelve a crear las de la
-- 0068, tal cual: sin fecha y con cualquier integrante activo de referente. No toca datos: los
-- objetivos creados con fecha la conservan (la columna `fecha_objetivo` ya existía), y sus claves
-- de creación quedan con la huella que incluye la fecha (un reenvío de ese mismo formulario, ya
-- sin fecha, se rechazaría como "usada con otros datos", nunca crearía otro objetivo).
begin;
set search_path = leda, public;

drop function if exists crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid, date, text,
                                           timestamptz);
drop function if exists opciones_del_objetivo(text, text, uuid, timestamptz);

create or replace function opciones_del_objetivo(
    p_puerta text, p_token_hash text, p_workspace_id uuid)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_quien jsonb;
        v_espacio workspace%rowtype;
        v_resultado jsonb;
begin
  v_quien := quien_crea_el_objetivo(p_puerta, p_token_hash, p_workspace_id);
  if not (v_quien ->> 'ok')::boolean then
    perform set_config('leda.workspace_id', previo, true);
    return v_quien;
  end if;
  select * into v_espacio from workspace w where w.id = (v_quien ->> 'workspace_id')::uuid;
  v_resultado := jsonb_build_object(
    'ok', true,
    'espacio', jsonb_build_object('id', v_espacio.id, 'nombre', v_espacio.nombre),
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
               'tipos', case o.tipo when 'estrategico' then jsonb_build_array('hito', 'operativo')
                                    else jsonb_build_array('operativo') end)
             order by o.titulo, o.id)
        from objective o
       where o.estado in ('activo', 'propuesto') and o.tipo <> 'operativo'), '[]'::jsonb),
    -- El referente: cualquier integrante activo del espacio.
    'integrantes', coalesce((
      select jsonb_agg(jsonb_build_object(
               'membership_id', m.id, 'nombre', u.nombre, 'area', a.nombre)
             order by u.nombre, m.id)
        from membership m
        join app_user u on u.id = m.app_user_id
        left join area a on a.id = m.area_id
       where m.activo), '[]'::jsonb));
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

-- --- La creación ---------------------------------------------------------------------------------

create or replace function crear_objetivo_web(
    p_puerta text, p_token_hash text, p_workspace_id uuid, p_titulo text, p_descripcion text,
    p_parent_id uuid, p_tipo text, p_referente_membership_id uuid, p_clave text)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_quien jsonb;
        v_espacio uuid;
        v_usuario uuid;
        v_padre objective%rowtype;
        v_referente membership%rowtype;
        v_previa creacion_de_objetivo%rowtype;
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
        'referente', p_referente_membership_id)::text, 'UTF8')), 'hex');
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

    -- El referente: cualquier integrante activo de este espacio.
    if p_referente_membership_id is null then
      v_errores := v_errores || jsonb_build_object('campo', 'referente', 'motivo', 'falta');
    else
      select * into v_referente from membership m
       where m.id = p_referente_membership_id and m.activo for share;
      if v_referente.id is null then
        v_errores := v_errores || jsonb_build_object('campo', 'referente',
                                                     'motivo', 'no_es_integrante_activo');
      end if;
    end if;

    if jsonb_array_length(v_errores) > 0 then
      v_resultado := jsonb_build_object('ok', false, 'errores', v_errores);
      exit creacion;
    end if;

    -- Todo en orden: el objetivo, su evento `activo` (el estado es la proyección; lo crea quien
    -- decide), su auditoría y su clave.
    insert into objective (workspace_id, parent_id, tipo, titulo, descripcion,
                           referente_membership_id)
    values (v_espacio, v_padre.id, p_tipo::tipo_objetivo, btrim(p_titulo),
            nullif(btrim(p_descripcion), ''), v_referente.id)
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
        'referente_membership_id', v_referente.id)
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

alter function opciones_del_objetivo(text, text, uuid) owner to leda_owner;
alter function crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid, text)
  owner to leda_owner;
revoke execute on function opciones_del_objetivo(text, text, uuid) from public;
revoke execute on function crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid,
                                              text) from public;
grant execute on function opciones_del_objetivo(text, text, uuid) to leda_app;
grant execute on function crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid,
                                             text) to leda_app;

commit;
