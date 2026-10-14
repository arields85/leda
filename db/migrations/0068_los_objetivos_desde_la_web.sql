\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0067_la_espera_al_cargar.sql. Los objetivos desde la web (ADR 0023, decisiones 1
-- y 5 y punto 11; mecánica §1; porción J3 de `odd/tasks/plataforma-jerarquias.md`, tarea J3-2).
--
-- - `objective`: `unique (workspace_id, id)` y claves compuestas para el padre y el referente, así
--   la base misma no deja colgar un objetivo de otro espacio ni nombrar de referente a alguien de
--   otro (reemplazan las dos claves simples).
-- - `creacion_de_objetivo`: la clave de un solo uso de cada creación desde la web, como
--   `carga_de_tarea`: RLS forzada y ningún privilegio para `leda_app`.
-- - `workspace_setting`: la clave `niveles`, los nombres de los niveles de objetivo del pack
--   (`estrategico`, `hito`, `operativo`), que guarda el importador. Sin ella, la web usa los del
--   núcleo. No hay relleno: el YAML no está en la base; se reimporta el pack.
-- - `quien_crea_el_objetivo`: la sesión de una de las dos puertas (`administracion`, cualquier
--   espacio; `equipo`, sólo Dirección, en el suyo) y el espacio, fijado. No es elevada: la llaman
--   las dos de abajo, que ya corren como `leda_owner`.
-- - `opciones_del_objetivo` y `crear_objetivo_web`: las opciones del formulario y la creación,
--   con el patrón de `cargar_tarea` (la sesión en cada llamada, el espacio fijado, la clave, los
--   errores juntos, la fila, su evento `activo` y la auditoría `crear_objetivo`).
--
-- `leda_app` sigue con sus privilegios directos sobre `objective`: los usan pruebas que crean
-- objetivos con esa conexión; ningún camino vivo escribe objetivos como `leda_app` desde que se
-- retiró la herramienta de chat `crear_objetivo`.
--
-- Mismo dueño (`leda_owner`), `search_path` y privilegios (sólo `leda_app`). Se deshace con
-- `db/rollbacks/0068_los_objetivos_desde_la_web.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0068 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0067 está aplicada y la 0068 no; ningún objetivo cuelga de otro espacio ni tiene
-- un referente de otro (las claves compuestas lo rechazarían a mitad de camino).
do $$ begin
  if to_regprocedure('leda.cargar_tarea(text, uuid, uuid, text, text, uuid, date, text, text[], uuid, text, timestamptz, uuid)') is null then
    raise exception '0068 preflight failed: falta la 0067';
  end if;
  if to_regclass('leda.creacion_de_objetivo') is not null then
    raise exception '0068 ya está aplicada.';
  end if;
  if exists (select 1 from objective o join objective p on p.id = o.parent_id
              where p.workspace_id <> o.workspace_id) then
    raise exception '0068 preflight failed: hay objetivos que cuelgan de otro espacio';
  end if;
  if exists (select 1 from objective o join membership m on m.id = o.referente_membership_id
              where m.workspace_id <> o.workspace_id) then
    raise exception '0068 preflight failed: hay objetivos con un referente de otro espacio';
  end if;
end $$;

-- --- El objetivo, del mismo espacio que su padre y su referente ---------------------------------

alter table objective add constraint objective_workspace_id_unique unique (workspace_id, id);
alter table objective drop constraint objective_parent_id_fkey;
alter table objective drop constraint objective_referente_membership_id_fkey;
alter table objective add constraint objective_padre_del_espacio
  foreign key (workspace_id, parent_id) references objective(workspace_id, id) on delete cascade;
alter table objective add constraint objective_referente_del_espacio
  foreign key (workspace_id, referente_membership_id) references membership(workspace_id, id);

-- --- Los nombres de los niveles del pack ---------------------------------------------------------

create or replace function niveles_validos(p_niveles jsonb) returns boolean as $$
  select jsonb_typeof(p_niveles) = 'object'
     and not exists (
       select 1 from jsonb_each(p_niveles) n
        where n.key not in ('estrategico', 'hito', 'operativo')
           or jsonb_typeof(n.value) <> 'string'
           or btrim(n.value #>> '{}') = ''
           or char_length(n.value #>> '{}') > 60);
$$ language sql immutable;

alter table workspace_setting add constraint workspace_setting_niveles check (
  case when clave <> 'niveles' then true else niveles_validos(valor) end);

-- --- La clave de un solo uso de cada creación ----------------------------------------------------

create table creacion_de_objetivo (
  id            uuid primary key default gen_random_uuid(),
  workspace_id  uuid not null references workspace(id) on delete cascade,
  clave         text not null,
  huella        text not null,
  objective_id  uuid not null,
  creada_en     timestamptz not null default now(),
  constraint creacion_de_objetivo_clave_unica unique (workspace_id, clave),
  constraint creacion_de_objetivo_clave check (clave ~ '^[A-Za-z0-9_-]{16,128}$'),
  constraint creacion_de_objetivo_huella check (huella ~ '^[0-9a-f]{64}$'),
  constraint creacion_de_objetivo_objetivo
    foreign key (workspace_id, objective_id) references objective(workspace_id, id)
    on delete cascade
);

comment on table creacion_de_objetivo is
  'ADR 0023, decisión 1 (migración 0068): la clave de un solo uso de cada creación de un objetivo desde la web, con la huella de lo creado. La misma clave con los mismos datos devuelve el mismo objetivo; con otros, se rechaza. leda_app no tiene privilegios: sólo execute sobre crear_objetivo_web.';

grant all privileges on creacion_de_objetivo to leda_owner, leda_admin;

alter table creacion_de_objetivo enable row level security;
alter table creacion_de_objetivo force row level security;
create policy aislamiento_espacio on creacion_de_objetivo
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

-- `leda_app`: nada sobre la tabla, sólo `execute` sobre las funciones de la web.
revoke all on creacion_de_objetivo from public, leda_app;
-- `leda_owner`: lo que necesita `crear_objetivo_web`, buscar y agregar.
revoke all on creacion_de_objetivo from leda_owner;
grant select, insert on creacion_de_objetivo to leda_owner;

-- --- Quién crea, por qué puerta ---------------------------------------------------------------

create or replace function quien_crea_el_objetivo(
    p_puerta text, p_token_hash text, p_workspace_id uuid)
returns jsonb
language plpgsql set search_path = leda, public, pg_temp as $$
declare v_sesion uuid;
        v_espacio uuid;
        v_persona uuid;
        v_usuario uuid;
        v_es_autoridad boolean;
begin
  if p_puerta = 'administracion' then
    -- El administrador de plataforma puede en cualquier espacio (ADR 0023, decisión 5).
    select s.sesion_id, s.app_user_id into v_sesion, v_usuario
      from sesion_de_administracion_vigente(p_token_hash) s;
    if v_usuario is null then
      return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'sesion', 'motivo', 'sin_sesion')));
    end if;
    select w.id into v_espacio from workspace w where w.id = p_workspace_id;
    if v_espacio is null then
      return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'espacio', 'motivo', 'no_existe')));
    end if;
  elsif p_puerta = 'equipo' then
    -- Dirección, sólo en su espacio (ADR 0023, decisión 1): el espacio sale de la sesión, y uno
    -- pedido que no es el suyo no existe para ella.
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
    select m.app_user_id, r.autoridad_final into v_usuario, v_es_autoridad
      from membership m join rol r on r.id = m.rol_id
     where m.id = v_persona and m.activo;
    if not coalesce(v_es_autoridad, false) then
      return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'sesion', 'motivo', 'sin_autoridad')));
    end if;
  else
    return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
      jsonb_build_object('campo', 'sesion', 'motivo', 'sin_sesion')));
  end if;
  -- Desde acá, la RLS acota todo a ese espacio: un id de otro no se encuentra.
  perform set_config('leda.workspace_id', v_espacio::text, true);
  return jsonb_build_object('ok', true, 'puerta', p_puerta, 'sesion_id', v_sesion,
                            'workspace_id', v_espacio, 'app_user_id', v_usuario,
                            'membership_id', v_persona);
end $$;

-- --- Las opciones del formulario ---------------------------------------------------------------

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
        join area a on a.id = m.area_id
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

alter function quien_crea_el_objetivo(text, text, uuid) owner to leda_owner;
alter function opciones_del_objetivo(text, text, uuid) owner to leda_owner;
alter function crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid, text)
  owner to leda_owner;
revoke execute on function quien_crea_el_objetivo(text, text, uuid) from public;
revoke execute on function opciones_del_objetivo(text, text, uuid) from public;
revoke execute on function crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid,
                                              text) from public;
grant execute on function opciones_del_objetivo(text, text, uuid) to leda_app;
grant execute on function crear_objetivo_web(text, text, uuid, text, text, uuid, text, uuid,
                                             text) to leda_app;

commit;
