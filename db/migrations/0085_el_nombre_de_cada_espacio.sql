\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0084_el_alta_de_una_persona.sql. Cada espacio ve su propio nombre para una persona
-- (J7-5b de `odd/tasks/plataforma-jerarquias.md`; constitución §13). Desde la 0084, quien abre el
-- enlace de activación con un Telegram que ya es de alguien de otro espacio queda unido a esa
-- cuenta (`app_user`), y el nombre de la cuenta es uno solo en toda Leda: el espacio nuevo veía el
-- que le había puesto el otro.
--
-- - `membership.nombre`: cómo se llama la persona en este espacio. Se llena con el de la cuenta
--   y, para quien llegó por un alta desde la web, con el que escribió Dirección
--   (`cambio_del_equipo`, clase `alta`).
-- - Todo lo que un espacio muestra de una persona sale de ahí: la vista `integrante`, el equipo,
--   sus problemas y sus cambios, el alta, el enlace de activación, la página de la tarea, las
--   listas y lo que se ofrece al cargar. `app_user.nombre` queda interno, de la plataforma.
-- - El alta escribe el nombre en la membresía; unirse a una cuenta no lo pisa.
--
-- Se deshace con `db/rollbacks/0085_el_nombre_de_cada_espacio.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0085 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0084 está aplicada y la 0085 no.
do $$ begin
  if to_regprocedure('leda.cambiar_el_alta(uuid, text, jsonb, text)') is null then
    raise exception '0085 preflight failed: falta la 0084';
  end if;
  if exists (select 1 from pg_attribute
              where attrelid = 'leda.membership'::regclass and attname = 'nombre'
                and not attisdropped) then
    raise exception '0085 ya está aplicada.';
  end if;
end $$;

alter table membership add column nombre text;
update membership m set nombre = u.nombre from app_user u where u.id = m.app_user_id;
-- Quien llegó por un alta desde la web (0084) se llama como lo escribió Dirección, aunque después
-- haya quedado unido a la cuenta de alguien de otro espacio.
update membership m set nombre = c.despues ->> 'nombre'
  from cambio_del_equipo c
 where c.workspace_id = m.workspace_id and c.clase = 'alta'
   and c.despues ->> 'membership_id' = m.id::text
   and nullif(btrim(c.despues ->> 'nombre'), '') is not null;
alter table membership alter column nombre set not null;

comment on column membership.nombre is
  'J7-5b (migración 0085): cómo se llama la persona en este espacio. Todo lo que un espacio muestra de una persona sale de acá, nunca de app_user.nombre: una cuenta unida a varios espacios (J7-5) tiene un nombre en cada uno, y ninguno ve el de otro (constitución §13).';

comment on column app_user.nombre is
  'J7-5b (migración 0085): el nombre de la cuenta, interno y de la plataforma (el administrador de plataforma, la consola). Ningún espacio lo muestra: cada uno nombra a la persona por membership.nombre.';

create or replace view integrante with (security_barrier = true) as
  select m.id            as membership_id,
         m.workspace_id,
         m.area_id,
         m.rol_id,
         m.aprobador_membership_id,
         m.activo,
         u.id            as app_user_id,
         u.telegram_user_id,
         m.nombre
    from membership m
    join app_user u on u.id = m.app_user_id
   where m.workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid;

create or replace function problemas_del_equipo(p_workspace_id uuid)
returns jsonb
language plpgsql stable security definer set search_path = leda, public, pg_temp as $$
declare
  v_espacio uuid := nullif(current_setting('leda.workspace_id', true), '')::uuid;
  v_problemas jsonb := '[]'::jsonb;
  v_fila record;
  v_finales text[];
  v_inicio uuid;
  v_actual uuid;
  v_visto uuid[];
  v_vuelta uuid[];
  v_clave text;
  v_vueltas text[] := array[]::text[];
  v_nombres text[];
begin
  if p_workspace_id is null or p_workspace_id is distinct from v_espacio then
    raise exception 'problemas_del_equipo: el espacio no es el de esta transacción';
  end if;

  -- Una sola persona activa con la autoridad final.
  select coalesce(array_agg(m.nombre order by m.nombre), array[]::text[]) into v_finales
    from membership m
    join rol r on r.id = m.rol_id
   where m.workspace_id = p_workspace_id and m.activo and r.autoridad_final;
  if cardinality(v_finales) = 0 then
    v_problemas := v_problemas || jsonb_build_array(jsonb_build_object(
      'codigo', 'sin_autoridad_final',
      'mensaje', 'Nadie del equipo tiene la autoridad final: tiene que haber una persona que '
                 'decida en última instancia.'));
  elsif cardinality(v_finales) > 1 then
    v_problemas := v_problemas || jsonb_build_array(jsonb_build_object(
      'codigo', 'mas_de_una_autoridad_final',
      'mensaje', format('%s tienen la autoridad final del equipo: tiene que tenerla una sola '
                        'persona.', unir_nombres(v_finales))));
  end if;

  -- Cada persona activa, salvo la autoridad final, con un aprobador activo del equipo.
  for v_fila in
    select m.id, m.nombre, m.aprobador_membership_id as aprobador, r.autoridad_final,
           coalesce(a.activo, false) as aprobador_activo, a.nombre as aprobador_nombre
      from membership m
      join rol r on r.id = m.rol_id
      left join membership a
        on a.id = m.aprobador_membership_id and a.workspace_id = m.workspace_id
     where m.workspace_id = p_workspace_id and m.activo
     order by m.nombre, m.id
  loop
    if v_fila.aprobador is null then
      if not v_fila.autoridad_final then
        v_problemas := v_problemas || jsonb_build_array(jsonb_build_object(
          'codigo', 'sin_aprobador', 'membership_id', v_fila.id,
          'mensaje', format('Nadie aprueba el trabajo de %s.', v_fila.nombre)));
      end if;
    elsif not v_fila.aprobador_activo then
      v_problemas := v_problemas || jsonb_build_array(jsonb_build_object(
        'codigo', 'aprobador_inactivo', 'membership_id', v_fila.id,
        'mensaje', format('El trabajo de %s lo aprueba %s, que ya no está en el equipo.',
                          v_fila.nombre, coalesce(v_fila.aprobador_nombre, 'alguien'))));
    end if;
  end loop;

  -- Sin vueltas en la cadena de quién aprueba a quién: cada vuelta se dice una vez.
  for v_inicio in
    select m.id from membership m
     where m.workspace_id = p_workspace_id and m.activo
     order by m.id
  loop
    v_visto := array[]::uuid[];
    v_actual := v_inicio;
    while v_actual is not null and not v_actual = any(v_visto) loop
      v_visto := v_visto || v_actual;
      select m.aprobador_membership_id into v_actual
        from membership m
       where m.id = v_actual and m.workspace_id = p_workspace_id and m.activo;
    end loop;
    if v_actual is not null then
      v_vuelta := v_visto[array_position(v_visto, v_actual):];
      select string_agg(x::text, ',' order by x) into v_clave from unnest(v_vuelta) x;
      if not v_clave = any(v_vueltas) then
        v_vueltas := v_vueltas || v_clave;
        select array_agg(m.nombre order by m.nombre) into v_nombres
          from membership m
         where m.id = any(v_vuelta);
        if cardinality(v_vuelta) = 1 then
          v_problemas := v_problemas || jsonb_build_array(jsonb_build_object(
            'codigo', 'se_aprueba_a_si_mismo', 'membership_id', v_vuelta[1],
            'mensaje', format('%s aprueba su propio trabajo.', v_nombres[1])));
        else
          v_problemas := v_problemas || jsonb_build_array(jsonb_build_object(
            'codigo', 'ciclo_de_aprobacion',
            'membership_ids', (select jsonb_agg(x order by x) from unnest(v_vuelta) x),
            'mensaje', format('La cadena de quién aprueba a quién da una vuelta: %s se aprueban '
                              'entre sí.', unir_nombres(v_nombres))));
        end if;
      end if;
    end if;
  end loop;

  -- Cada área sin archivar, con un referente activo, la autoaprobación declarada o sin referente
  -- (la decide Dirección, J6-D6).
  for v_fila in
    select a.id, a.nombre, r.nombre as referente
      from area a
      join membership r on r.id = a.referente_membership_id
     where a.workspace_id = p_workspace_id and a.archivada_en is null and not r.activo
       and not exists (select 1 from approval_policy p
                        where p.workspace_id = a.workspace_id and p.area_id = a.id
                          and p.autoaprobacion_declarada)
     order by a.nombre, a.id
  loop
    v_problemas := v_problemas || jsonb_build_array(jsonb_build_object(
      'codigo', 'referente_inactivo', 'area_id', v_fila.id,
      'mensaje', format('El referente de %s, %s, ya no está en el equipo.',
                        v_fila.nombre, v_fila.referente)));
  end loop;

  -- Nadie activo en un área archivada.
  for v_fila in
    select m.id, m.nombre, a.id as area_id, a.nombre as area
      from membership m
      join area a on a.id = m.area_id
     where m.workspace_id = p_workspace_id and m.activo and a.archivada_en is not null
     order by m.nombre, m.id
  loop
    v_problemas := v_problemas || jsonb_build_array(jsonb_build_object(
      'codigo', 'integrante_en_area_archivada', 'membership_id', v_fila.id,
      'area_id', v_fila.area_id,
      'mensaje', format('%s está en %s, un área archivada.', v_fila.nombre, v_fila.area)));
  end loop;

  return v_problemas;
end $$;

create or replace function equipo_de(p_puerta text, p_token_hash text, p_workspace_id uuid)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_quien jsonb;
        v_espacio uuid;
        v_resultado jsonb;
begin
  v_quien := quien_organiza_el_equipo(p_puerta, p_token_hash, p_workspace_id);
  if not (v_quien ->> 'ok')::boolean then
    perform set_config('leda.workspace_id', previo, true);
    return v_quien;
  end if;
  -- Desde acá, la RLS acota todo a ese espacio; el filtro explícito, además.
  v_espacio := (v_quien ->> 'workspace_id')::uuid;
  v_resultado := jsonb_build_object(
    'ok', true,
    'espacio', (select jsonb_build_object('id', w.id, 'nombre', w.nombre)
                  from workspace w where w.id = v_espacio),
    -- Las áreas vigentes primero; una archivada (nunca se borra), al final y marcada.
    'areas', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', a.id, 'slug', a.slug, 'nombre', a.nombre,
               'archivada', a.archivada_en is not null,
               'referente', case when r.id is null then null
                                 else jsonb_build_object('membership_id', r.id,
                                                         'nombre', r.nombre,
                                                         'activo', r.activo) end,
               'autoaprobacion', exists (
                 select 1 from approval_policy p
                  where p.workspace_id = v_espacio and p.area_id = a.id
                    and p.autoaprobacion_declarada),
               'personas', coalesce((
                 select jsonb_agg(m.id order by m.nombre, m.id)
                   from membership m
                  where m.workspace_id = v_espacio and m.area_id = a.id and m.activo),
                 '[]'::jsonb),
               'tareas_abiertas', (
                 select count(*) from task t
                  where t.workspace_id = v_espacio and t.area_id = a.id
                    and t.estado not in ('terminada', 'cancelada')))
             order by a.archivada_en is not null, a.nombre, a.id)
        from area a
        left join membership r on r.id = a.referente_membership_id
       where a.workspace_id = v_espacio), '[]'::jsonb),
    -- Las personas: las que siguen en el equipo primero. «Sin conectar» es quien todavía no
    -- activó su enlace (`onboarding.pendientes_de_activar`): sin cuenta de Telegram.
    'personas', coalesce((
      select jsonb_agg(jsonb_build_object(
               'membership_id', m.id, 'nombre', m.nombre, 'activo', m.activo,
               'conectado', u.telegram_user_id is not null,
               'area_id', m.area_id, 'area', a.nombre,
               'rol_id', m.rol_id, 'rol', r.nombre, 'autoridad_final', r.autoridad_final,
               'aprobador', case when ap.id is null then null
                                 else jsonb_build_object('membership_id', ap.id,
                                                         'nombre', ap.nombre,
                                                         'activo', ap.activo) end,
               'referente_de', coalesce((
                 select jsonb_agg(x.nombre order by x.nombre, x.id)
                   from area x
                  where x.workspace_id = v_espacio and x.referente_membership_id = m.id
                    and x.archivada_en is null), '[]'::jsonb))
             order by not m.activo, m.nombre, m.id)
        from membership m
        join app_user u on u.id = m.app_user_id
        join area a on a.id = m.area_id
        join rol r on r.id = m.rol_id
        left join membership ap on ap.id = m.aprobador_membership_id
       where m.workspace_id = v_espacio), '[]'::jsonb),
    'roles', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', r.id, 'slug', r.slug, 'nombre', r.nombre,
               'autoridad_final', r.autoridad_final,
               'personas', (select count(*) from membership m
                             where m.workspace_id = v_espacio and m.rol_id = r.id
                               and m.activo))
             order by r.autoridad_final desc, r.nombre, r.id)
        from rol r
       where r.workspace_id = v_espacio), '[]'::jsonb),
    'problemas', problemas_del_equipo(v_espacio));
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

create or replace function cambios_del_equipo(p_puerta text, p_token_hash text, p_workspace_id uuid)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_quien jsonb;
        v_espacio uuid;
        v_resultado jsonb;
begin
  v_quien := quien_organiza_el_equipo(p_puerta, p_token_hash, p_workspace_id);
  if not (v_quien ->> 'ok')::boolean then
    perform set_config('leda.workspace_id', previo, true);
    return v_quien;
  end if;
  v_espacio := (v_quien ->> 'workspace_id')::uuid;
  -- Quién lo hizo, por su nombre, y por qué puerta: el administrador de plataforma no es miembro.
  v_resultado := jsonb_build_object(
    'ok', true,
    'cambios', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', c.id, 'clase', c.clase, 'puerta', c.puerta, 'quien', coalesce(hm.nombre, u.nombre),
               'at', c.at, 'antes', c.antes, 'despues', c.despues)
             order by c.at desc, c.id)
        from cambio_del_equipo c
        join app_user u on u.id = c.hecho_por_app_user_id
        -- Como lo nombra este espacio, aunque haya entrado por la puerta de administración; el
        -- administrador de plataforma que no es del equipo, por su nombre de la plataforma (J7-5b).
        left join membership hm
          on hm.workspace_id = c.workspace_id and hm.app_user_id = c.hecho_por_app_user_id
       where c.workspace_id = v_espacio), '[]'::jsonb));
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

create or replace function cambiar_un_area(
    p_espacio uuid, p_accion text, p_datos jsonb, p_huella text)
returns jsonb
language plpgsql set search_path = leda, public, pg_temp as $$
declare
  c_uuid constant text :=
    '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$';
  v_datos jsonb := coalesce(p_datos, '{}'::jsonb);
  v_errores jsonb := '[]'::jsonb;
  v_area area%rowtype;
  v_texto text;
  v_nombre text;
  v_aprobacion text;
  v_referente uuid;
  v_referente_nombre text;
  v_sin_evidencia boolean;
  v_evidencia text[] := '{}';
  v_tipos_del_espacio jsonb;
  v_base text;
  v_slug text;
  v_n integer := 1;
  v_personas integer;
  v_tareas integer;
  v_plan jsonb;
  v_huella text;
  v_antes jsonb;
  v_despues jsonb;
  v_id uuid;
begin
  -- Un cambio de área a la vez en cada espacio: dos no se pisan el nombre ni el slug.
  perform pg_advisory_xact_lock(hashtextextended(p_espacio::text || ':areas', 0));

  if p_accion is null or p_accion not in ('crear', 'renombrar', 'archivar') then
    return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
      jsonb_build_object('campo', 'accion', 'motivo', 'no_existe')));
  end if;

  -- El área que se cambia (renombrar y archivar): de este espacio, leída `for update`.
  if p_accion in ('renombrar', 'archivar') then
    if coalesce(jsonb_typeof(v_datos -> 'area_id'), 'null') not in ('string', 'null') then
      v_errores := v_errores || jsonb_build_object('campo', 'area', 'motivo', 'mal_formada');
    else
      v_texto := nullif(btrim(v_datos ->> 'area_id'), '');
      if v_texto is null then
        v_errores := v_errores || jsonb_build_object('campo', 'area', 'motivo', 'falta');
      elsif v_texto !~ c_uuid then
        v_errores := v_errores || jsonb_build_object('campo', 'area', 'motivo', 'mal_formada');
      else
        select * into v_area from area a
         where a.id = v_texto::uuid and a.workspace_id = p_espacio for update;
        if v_area.id is null then
          v_errores := v_errores || jsonb_build_object('campo', 'area', 'motivo', 'no_existe');
        elsif v_area.archivada_en is not null then
          v_errores := v_errores || jsonb_build_object(
            'campo', 'area',
            'motivo', case p_accion when 'archivar' then 'ya_archivada' else 'archivada' end);
        end if;
      end if;
    end if;
  end if;

  -- El nombre (crear y renombrar): sin espacios de más, hasta 80 caracteres, sin repetir el de
  -- otra área vigente (mayúsculas aparte). Uno archivado se puede volver a usar.
  if p_accion in ('crear', 'renombrar') then
    if coalesce(jsonb_typeof(v_datos -> 'nombre'), 'null') not in ('string', 'null') then
      v_errores := v_errores || jsonb_build_object('campo', 'nombre', 'motivo', 'mal_formado');
    else
      v_nombre := regexp_replace(btrim(coalesce(v_datos ->> 'nombre', '')), '\s+', ' ', 'g');
      if v_nombre = '' then
        v_errores := v_errores || jsonb_build_object('campo', 'nombre', 'motivo', 'falta');
      elsif char_length(v_nombre) > 80 then
        v_errores := v_errores || jsonb_build_object('campo', 'nombre',
                                                     'motivo', 'demasiado_largo');
      elsif p_accion = 'renombrar' and v_area.id is not null and v_area.nombre = v_nombre then
        v_errores := v_errores || jsonb_build_object('campo', 'nombre', 'motivo', 'sin_cambio');
      elsif exists (select 1 from area a
                     where a.workspace_id = p_espacio and a.archivada_en is null
                       and lower(a.nombre) = lower(v_nombre)
                       and a.id is distinct from v_area.id) then
        v_errores := v_errores || jsonb_build_object('campo', 'nombre', 'motivo', 'ya_existe');
      end if;
    end if;
  end if;

  if p_accion = 'crear' then
    -- Quién aprueba su trabajo (mecánica §7): su referente, un integrante activo del espacio; el
    -- área misma, declarado a propósito; o, sin referente, lo decide Dirección (J6-D6).
    if coalesce(jsonb_typeof(v_datos -> 'aprobacion'), 'null') not in ('string', 'null') then
      v_errores := v_errores || jsonb_build_object('campo', 'aprobacion',
                                                   'motivo', 'mal_formada');
    else
      v_aprobacion := nullif(btrim(v_datos ->> 'aprobacion'), '');
      if v_aprobacion is null then
        v_errores := v_errores || jsonb_build_object('campo', 'aprobacion', 'motivo', 'falta');
      elsif v_aprobacion not in ('referente', 'autoaprobacion', 'direccion') then
        v_errores := v_errores || jsonb_build_object('campo', 'aprobacion',
                                                     'motivo', 'no_existe');
      end if;
    end if;
    v_texto := null;
    if coalesce(jsonb_typeof(v_datos -> 'referente_id'), 'null') not in ('string', 'null') then
      v_errores := v_errores || jsonb_build_object('campo', 'referente', 'motivo', 'mal_formado');
    else
      v_texto := nullif(btrim(v_datos ->> 'referente_id'), '');
      if v_texto is not null and v_texto !~ c_uuid then
        v_errores := v_errores || jsonb_build_object('campo', 'referente',
                                                     'motivo', 'mal_formado');
      elsif v_aprobacion = 'referente' then
        if v_texto is null then
          v_errores := v_errores || jsonb_build_object('campo', 'referente', 'motivo', 'falta');
        else
          -- Leído `for share`: no deja el equipo mientras tanto.
          select m.id, m.nombre into v_referente, v_referente_nombre
            from membership m
           where m.id = v_texto::uuid and m.workspace_id = p_espacio and m.activo
             for share of m;
          if v_referente is null then
            v_errores := v_errores || jsonb_build_object('campo', 'referente',
                                                         'motivo', 'no_es_integrante_activo');
          end if;
        end if;
      elsif v_texto is not null and v_aprobacion in ('autoaprobacion', 'direccion') then
        v_errores := v_errores || jsonb_build_object('campo', 'referente',
                                                     'motivo', 'no_corresponde');
      end if;
    end if;

    -- Su evidencia, elegida a propósito: tipos del espacio, o «no pide evidencia». Sin una de las
    -- dos, sus tareas no se podrían cargar (`sin_politica_del_area`).
    v_tipos_del_espacio := tipos_de_evidencia_del_espacio(p_espacio);
    v_sin_evidencia := case coalesce(jsonb_typeof(v_datos -> 'sin_evidencia'), 'null')
                         when 'boolean' then (v_datos ->> 'sin_evidencia')::boolean
                         when 'null' then false end;
    if v_sin_evidencia is null
       or coalesce(jsonb_typeof(v_datos -> 'evidencia'), 'null') not in ('array', 'null')
       or exists (select 1
                    from jsonb_array_elements(case jsonb_typeof(v_datos -> 'evidencia')
                                                when 'array' then v_datos -> 'evidencia'
                                                else '[]'::jsonb end) e
                   where jsonb_typeof(e) <> 'string') then
      v_errores := v_errores || jsonb_build_object('campo', 'evidencia', 'motivo', 'mal_formada');
    else
      -- Cada tipo una vez, en el orden en que se eligió.
      select coalesce(array_agg(x.tipo order by x.primera), '{}') into v_evidencia
        from (select btrim(e.tipo) as tipo, min(e.orden) as primera
                from jsonb_array_elements_text(case jsonb_typeof(v_datos -> 'evidencia')
                                                 when 'array' then v_datos -> 'evidencia'
                                                 else '[]'::jsonb end)
                     with ordinality e(tipo, orden)
               where btrim(e.tipo) <> ''
               group by btrim(e.tipo)) x;
      if v_sin_evidencia and cardinality(v_evidencia) > 0 then
        v_errores := v_errores || jsonb_build_object('campo', 'evidencia',
                                                     'motivo', 'contradice');
      elsif not v_sin_evidencia and cardinality(v_evidencia) = 0 then
        v_errores := v_errores || jsonb_build_object('campo', 'evidencia', 'motivo', 'falta');
      elsif exists (select 1 from unnest(v_evidencia) e(tipo)
                     where not exists (select 1 from jsonb_array_elements(v_tipos_del_espacio) t
                                        where t ->> 'tipo' = e.tipo)) then
        v_errores := v_errores || jsonb_build_object('campo', 'evidencia',
                                                     'motivo', 'no_es_del_espacio');
      end if;
    end if;
  end if;

  -- Archivar (ADR 0023, decisión 4): sólo sin gente activa ni tareas abiertas. La evidencia del
  -- área se lee `for update`: la carga de una tarea la lee `for share`, así que no entra una
  -- mientras tanto.
  if p_accion = 'archivar' and v_area.id is not null and v_area.archivada_en is null then
    perform 1 from task_evidence_policy p where p.area_id = v_area.id for update;
    select count(*) into v_personas from membership m
     where m.workspace_id = p_espacio and m.area_id = v_area.id and m.activo;
    select count(*) into v_tareas from task t
     where t.workspace_id = p_espacio and t.area_id = v_area.id
       and t.estado not in ('terminada', 'cancelada');
    if v_personas > 0 then
      v_errores := v_errores || jsonb_build_object('campo', 'area', 'motivo', 'tiene_personas',
                                                   'cuantas', v_personas);
    end if;
    if v_tareas > 0 then
      v_errores := v_errores || jsonb_build_object('campo', 'area',
                                                   'motivo', 'tiene_tareas_abiertas',
                                                   'cuantas', v_tareas);
    end if;
  end if;

  if jsonb_array_length(v_errores) > 0 then
    return jsonb_build_object('ok', false, 'errores', v_errores);
  end if;

  -- El slug de un área nueva sale de su nombre y no cambia más: sin tildes, minúsculas y
  -- guiones; si ya lo tiene otra (aunque esté archivada), con un número.
  if p_accion = 'crear' then
    v_base := btrim(regexp_replace(
                translate(lower(v_nombre), 'áàäâãéèëêíìïîóòöôõúùüûñç',
                          'aaaaaeeeeiiiiooooouuuunc'),
                '[^a-z0-9]+', '-', 'g'), '-');
    v_base := btrim(left(coalesce(nullif(v_base, ''), 'area'), 60), '-');
    v_slug := v_base;
    while exists (select 1 from area a where a.workspace_id = p_espacio and a.slug = v_slug) loop
      v_n := v_n + 1;
      v_slug := v_base || '-' || v_n;
    end loop;
  end if;

  -- Lo que se va a hacer, con lo que el equipo tiene hoy: si cambia entre la vista previa y la
  -- confirmación, la huella no es la misma.
  v_plan := case p_accion
    when 'crear' then jsonb_build_object(
      'accion', p_accion, 'nombre', v_nombre, 'slug', v_slug, 'aprobacion', v_aprobacion,
      'referente_id', v_referente, 'evidencia', to_jsonb(v_evidencia),
      'sin_evidencia', v_sin_evidencia)
    when 'renombrar' then jsonb_build_object(
      'accion', p_accion, 'area_id', v_area.id, 'nombre_antes', v_area.nombre,
      'nombre', v_nombre)
    else jsonb_build_object('accion', p_accion, 'area_id', v_area.id, 'nombre', v_area.nombre)
  end;
  v_huella := encode(sha256(convert_to(v_plan::text, 'UTF8')), 'hex');
  if p_huella is not null and p_huella is distinct from v_huella then
    return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
      jsonb_build_object('campo', 'huella', 'motivo', 'el_equipo_cambio')));
  end if;

  -- El antes y el después, en palabras: lo que muestra la vista previa y guarda el cambio.
  if p_accion = 'crear' then
    v_antes := null;
    v_despues := jsonb_build_object(
      'nombre', v_nombre,
      'referente', v_referente_nombre,
      'quien_aprueba', case v_aprobacion when 'referente' then 'su referente'
                                         when 'autoaprobacion' then 'el área misma'
                                         else 'Dirección' end,
      'evidencia', case when cardinality(v_evidencia) = 0 then 'no pide evidencia'
                        else (select string_agg(coalesce(
                                       (select t ->> 'en_palabras'
                                          from jsonb_array_elements(v_tipos_del_espacio) t
                                         where t ->> 'tipo' = e.tipo), e.tipo), ', '
                                       order by e.orden)
                                from unnest(v_evidencia) with ordinality e(tipo, orden)) end);
    insert into area (workspace_id, slug, nombre, referente_membership_id)
    values (p_espacio, v_slug, v_nombre, v_referente)
    returning id into v_id;
    if v_aprobacion = 'autoaprobacion' then
      insert into approval_policy (workspace_id, sujeto, area_id, autoaprobacion_declarada,
                                   motivo)
      values (p_espacio, 'tarea', v_id, true, 'Declarada al crear el área desde la web.');
    end if;
    -- Las clases y las palabras de cada tipo, las del espacio (como el importador: cada área
    -- conoce todos los tipos).
    insert into task_evidence_policy (workspace_id, area_id, evidencia_requerida, tipos)
    values (p_espacio, v_id, v_evidencia, coalesce((
      select jsonb_object_agg(x.tipo, x.definicion)
        from (select distinct on (t.key) t.key as tipo, t.value as definicion
                from task_evidence_policy p cross join lateral jsonb_each(p.tipos) t
               where p.workspace_id = p_espacio
               order by t.key, p.actualizado_en desc, p.area_id) x), '{}'::jsonb));
  elsif p_accion = 'renombrar' then
    v_id := v_area.id;
    v_antes := jsonb_build_object('nombre', v_area.nombre);
    v_despues := jsonb_build_object('nombre', v_nombre);
    update area set nombre = v_nombre where id = v_id;
  else
    v_id := v_area.id;
    v_antes := jsonb_build_object('nombre', v_area.nombre, 'estado', 'vigente');
    v_despues := jsonb_build_object('nombre', v_area.nombre, 'estado', 'archivada');
    update area set archivada_en = now() where id = v_id;
  end if;

  return jsonb_build_object('ok', true, 'area_id', v_id, 'antes', v_antes,
                            'despues', v_despues, 'huella', v_huella);
end $$;

create or replace function cambiar_el_alta(
    p_espacio uuid, p_accion text, p_datos jsonb, p_huella text)
returns jsonb
language plpgsql set search_path = leda, public, pg_temp as $$
declare
  c_uuid constant text :=
    '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$';
  v_datos jsonb := coalesce(p_datos, '{}'::jsonb);
  v_errores jsonb := '[]'::jsonb;
  v_avisos jsonb := '[]'::jsonb;
  v_texto text;
  v_nombre text;
  v_persona membership%rowtype;
  v_area area%rowtype;
  v_rol rol%rowtype;
  v_aprobador uuid;
  v_aprobador_nombre text;
  v_por_omision boolean := false;
  v_plan jsonb;
  v_huella text;
  v_antes jsonb;
  v_despues jsonb;
  v_usuario uuid;
  v_id uuid;
begin
  -- Un cambio de personas a la vez en cada espacio, y no mientras se archiva un área.
  perform pg_advisory_xact_lock(hashtextextended(p_espacio::text || ':areas', 0));
  perform pg_advisory_xact_lock(hashtextextended(p_espacio::text || ':personas', 0));

  if p_accion is null or p_accion not in ('alta', 'reactivar') then
    return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
      jsonb_build_object('campo', 'accion', 'motivo', 'no_existe')));
  end if;

  -- Quien vuelve (reactivar): una membresía de este espacio que dejó el equipo, leída
  -- `for update`. Se la nombra por su id, nunca por el nombre.
  if p_accion = 'reactivar' then
    if coalesce(jsonb_typeof(v_datos -> 'membership_id'), 'null') not in ('string', 'null') then
      v_errores := v_errores || jsonb_build_object('campo', 'persona', 'motivo', 'mal_formada');
    else
      v_texto := nullif(btrim(v_datos ->> 'membership_id'), '');
      if v_texto is null then
        v_errores := v_errores || jsonb_build_object('campo', 'persona', 'motivo', 'falta');
      elsif v_texto !~ c_uuid then
        v_errores := v_errores || jsonb_build_object('campo', 'persona', 'motivo', 'mal_formada');
      else
        select * into v_persona from membership m
         where m.id = v_texto::uuid and m.workspace_id = p_espacio for update;
        if v_persona.id is null then
          v_errores := v_errores || jsonb_build_object('campo', 'persona', 'motivo', 'no_existe');
        elsif v_persona.activo then
          v_errores := v_errores || jsonb_build_object('campo', 'persona',
                                                       'motivo', 'ya_esta_en_el_equipo');
        else
          select m.nombre into v_nombre from membership m where m.id = v_persona.id;
        end if;
      end if;
    end if;
  end if;

  -- El nombre (alta): sin espacios de más, hasta 80 caracteres. Puede repetir el de otra persona:
  -- es otra persona (se avisa, no se impide).
  if p_accion = 'alta' then
    if coalesce(jsonb_typeof(v_datos -> 'nombre'), 'null') not in ('string', 'null') then
      v_errores := v_errores || jsonb_build_object('campo', 'nombre', 'motivo', 'mal_formado');
    else
      v_nombre := regexp_replace(btrim(coalesce(v_datos ->> 'nombre', '')), '\s+', ' ', 'g');
      if v_nombre = '' then
        v_errores := v_errores || jsonb_build_object('campo', 'nombre', 'motivo', 'falta');
      elsif char_length(v_nombre) > 80 then
        v_errores := v_errores || jsonb_build_object('campo', 'nombre',
                                                     'motivo', 'demasiado_largo');
      end if;
    end if;
  end if;

  -- El área: de este espacio y sin archivar, leída `for share` (no se archiva mientras tanto).
  if coalesce(jsonb_typeof(v_datos -> 'area_id'), 'null') not in ('string', 'null') then
    v_errores := v_errores || jsonb_build_object('campo', 'area', 'motivo', 'mal_formada');
  else
    v_texto := nullif(btrim(v_datos ->> 'area_id'), '');
    if v_texto is null then
      v_errores := v_errores || jsonb_build_object('campo', 'area', 'motivo', 'falta');
    elsif v_texto !~ c_uuid then
      v_errores := v_errores || jsonb_build_object('campo', 'area', 'motivo', 'mal_formada');
    else
      select * into v_area from area a
       where a.id = v_texto::uuid and a.workspace_id = p_espacio for share;
      if v_area.id is null then
        v_errores := v_errores || jsonb_build_object('campo', 'area', 'motivo', 'no_existe');
      elsif v_area.archivada_en is not null then
        v_errores := v_errores || jsonb_build_object('campo', 'area', 'motivo', 'archivada');
      end if;
    end if;
  end if;

  -- El rol: de este espacio. La autoridad final no se da con un alta: se pasa (ADR 0023,
  -- punto 10).
  if coalesce(jsonb_typeof(v_datos -> 'rol_id'), 'null') not in ('string', 'null') then
    v_errores := v_errores || jsonb_build_object('campo', 'rol', 'motivo', 'mal_formado');
  else
    v_texto := nullif(btrim(v_datos ->> 'rol_id'), '');
    if v_texto is null then
      v_errores := v_errores || jsonb_build_object('campo', 'rol', 'motivo', 'falta');
    elsif v_texto !~ c_uuid then
      v_errores := v_errores || jsonb_build_object('campo', 'rol', 'motivo', 'mal_formado');
    else
      select * into v_rol from rol r where r.id = v_texto::uuid and r.workspace_id = p_espacio;
      if v_rol.id is null then
        v_errores := v_errores || jsonb_build_object('campo', 'rol', 'motivo', 'no_existe');
      elsif v_rol.autoridad_final then
        v_errores := v_errores || jsonb_build_object('campo', 'rol', 'motivo', 'es_de_direccion');
      end if;
    end if;
  end if;

  -- Quién la aprueba: el elegido, un integrante activo del espacio (leído `for share`: no deja
  -- el equipo mientras tanto); por omisión, el referente activo del área y, sin él, Dirección
  -- (J6-D6).
  if coalesce(jsonb_typeof(v_datos -> 'aprobador_id'), 'null') not in ('string', 'null') then
    v_errores := v_errores || jsonb_build_object('campo', 'aprobador', 'motivo', 'mal_formado');
  else
    v_texto := nullif(btrim(v_datos ->> 'aprobador_id'), '');
    if v_texto is not null and v_texto !~ c_uuid then
      v_errores := v_errores || jsonb_build_object('campo', 'aprobador', 'motivo', 'mal_formado');
    elsif v_texto is not null then
      if v_persona.id is not null and v_texto::uuid = v_persona.id then
        v_errores := v_errores || jsonb_build_object('campo', 'aprobador',
                                                     'motivo', 'es_la_misma_persona');
      else
        select m.id, m.nombre into v_aprobador, v_aprobador_nombre
          from membership m
         where m.id = v_texto::uuid and m.workspace_id = p_espacio and m.activo
           for share of m;
        if v_aprobador is null then
          v_errores := v_errores || jsonb_build_object('campo', 'aprobador',
                                                       'motivo', 'no_es_integrante_activo');
        end if;
      end if;
    elsif v_area.id is not null and v_area.archivada_en is null then
      v_por_omision := true;
      select r.id, r.nombre into v_aprobador, v_aprobador_nombre
        from membership r
       where r.id = v_area.referente_membership_id and r.workspace_id = p_espacio and r.activo
         and r.id is distinct from v_persona.id
         for share of r;
      if v_aprobador is null then
        select m.id, m.nombre into v_aprobador, v_aprobador_nombre
          from membership m
          join rol x on x.id = m.rol_id
         where m.workspace_id = p_espacio and m.activo and x.autoridad_final
           and m.id is distinct from v_persona.id
         order by m.nombre, m.id
         limit 1
           for share of m;
      end if;
      if v_aprobador is null then
        v_errores := v_errores || jsonb_build_object('campo', 'aprobador', 'motivo', 'falta');
      end if;
    end if;
  end if;

  if jsonb_array_length(v_errores) > 0 then
    return jsonb_build_object('ok', false, 'errores', v_errores);
  end if;

  -- Lo que se va a hacer, con lo que el equipo tiene hoy: si cambia entre la vista previa y la
  -- confirmación (otro referente, quien vuelve ya volvió), la huella no es la misma.
  v_plan := jsonb_build_object(
    'accion', p_accion, 'membership_id', v_persona.id, 'nombre', v_nombre,
    'area_id', v_area.id, 'rol_id', v_rol.id, 'aprobador_id', v_aprobador,
    'por_omision', v_por_omision);
  v_huella := encode(sha256(convert_to(v_plan::text, 'UTF8')), 'hex');
  if p_huella is not null and p_huella is distinct from v_huella then
    return jsonb_build_object('ok', false, 'errores', jsonb_build_array(
      jsonb_build_object('campo', 'huella', 'motivo', 'el_equipo_cambio')));
  end if;

  -- Un alta con el nombre de alguien del equipo es otra persona: se avisa, por si es la misma
  -- (alguien que sigue, o que estuvo y se puede volver a sumar).
  if p_accion = 'alta' then
    if exists (select 1 from membership m
                where m.workspace_id = p_espacio and m.activo
                  and lower(m.nombre) = lower(v_nombre)) then
      v_avisos := v_avisos || jsonb_build_object(
        'codigo', 'mismo_nombre',
        'mensaje', format('Ya hay alguien en el equipo que se llama %s: si es la misma persona, '
                          'no hace falta darla de alta.', v_nombre));
    elsif exists (select 1 from membership m
                   where m.workspace_id = p_espacio and not m.activo
                     and lower(m.nombre) = lower(v_nombre)) then
      v_avisos := v_avisos || jsonb_build_object(
        'codigo', 'estuvo_en_el_equipo',
        'mensaje', format('%s estuvo en el equipo: si es la misma persona, volvé a sumarla desde '
                          '«Ya no están en el equipo».', v_nombre));
    end if;
  end if;

  -- El antes y el después, en palabras: lo que muestra la vista previa y guarda el cambio.
  v_despues := jsonb_build_object('nombre', v_nombre, 'area', v_area.nombre, 'rol', v_rol.nombre,
                                  'quien_aprueba', v_aprobador_nombre);
  if p_accion = 'alta' then
    v_antes := null;
    insert into app_user (nombre) values (v_nombre) returning id into v_usuario;
    insert into membership (workspace_id, app_user_id, nombre, area_id, rol_id,
                            aprobador_membership_id)
    values (p_espacio, v_usuario, v_nombre, v_area.id, v_rol.id, v_aprobador)
    returning id into v_id;
  else
    v_id := v_persona.id;
    v_antes := jsonb_build_object(
      'nombre', v_nombre,
      'area', (select a.nombre from area a where a.id = v_persona.area_id),
      'rol', (select r.nombre from rol r where r.id = v_persona.rol_id),
      'quien_aprueba', (select m.nombre from membership m
                         where m.id = v_persona.aprobador_membership_id),
      'estado', 'fuera del equipo');
    v_despues := v_despues || jsonb_build_object('estado', 'en el equipo');
    update membership
       set activo = true, area_id = v_area.id, rol_id = v_rol.id,
           aprobador_membership_id = v_aprobador
     where id = v_id;
  end if;

  return jsonb_build_object(
    'ok', true, 'membership_id', v_id, 'antes', v_antes, 'despues', v_despues,
    'aprobador', jsonb_build_object('membership_id', v_aprobador, 'nombre', v_aprobador_nombre,
                                    'por_omision', v_por_omision),
    'avisos', v_avisos, 'huella', v_huella);
end $$;

create or replace function emitir_enlace_de_activacion(
    p_puerta text, p_token_hash text, p_workspace_id uuid, p_membership_id uuid,
    p_enlace_hash text)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_quien jsonb;
        v_espacio uuid;
        v_usuario uuid;
        v_errores jsonb := '[]'::jsonb;
        v_persona record;
        v_bot text;
        v_id uuid;
        v_expira timestamptz;
        v_resultado jsonb;
begin
  v_quien := quien_organiza_el_equipo(p_puerta, p_token_hash, p_workspace_id);
  if not (v_quien ->> 'ok')::boolean then
    perform set_config('leda.workspace_id', previo, true);
    return v_quien;
  end if;
  v_espacio := (v_quien ->> 'workspace_id')::uuid;
  v_usuario := (v_quien ->> 'app_user_id')::uuid;

  if p_enlace_hash is null or p_enlace_hash !~ '^[0-9a-f]{64}$' then
    v_errores := v_errores || jsonb_build_object('campo', 'enlace', 'motivo', 'mal_formado');
  end if;
  if p_membership_id is null then
    v_errores := v_errores || jsonb_build_object('campo', 'persona', 'motivo', 'falta');
  else
    -- La persona, de este espacio, leída `for update`: dos enlaces a la vez no se pisan.
    select m.id, m.activo, m.nombre, u.telegram_user_id into v_persona
      from membership m join app_user u on u.id = m.app_user_id
     where m.id = p_membership_id and m.workspace_id = v_espacio
       for update of m;
    if v_persona.id is null then
      v_errores := v_errores || jsonb_build_object('campo', 'persona', 'motivo', 'no_existe');
    elsif not v_persona.activo then
      v_errores := v_errores || jsonb_build_object('campo', 'persona',
                                                   'motivo', 'no_esta_en_el_equipo');
    elsif v_persona.telegram_user_id is not null then
      v_errores := v_errores || jsonb_build_object('campo', 'persona', 'motivo', 'ya_conectada');
    end if;
  end if;
  -- El usuario del bot del espacio: sin él no hay enlace, y no se anula el que había.
  select s.valor #>> '{}' into v_bot from workspace_setting s
   where s.workspace_id = v_espacio and s.clave = 'bot_usuario';
  if v_bot is null or v_bot !~ '^[A-Za-z][A-Za-z0-9_]{4,31}$' then
    v_errores := v_errores || jsonb_build_object('campo', 'bot', 'motivo', 'sin_usuario');
  end if;

  if jsonb_array_length(v_errores) > 0 then
    v_resultado := jsonb_build_object('ok', false, 'errores', v_errores);
  else
    delete from activation_token where membership_id = p_membership_id and usado_en is null;
    insert into activation_token (workspace_id, membership_id, token_hash, expira_en, creado_por)
    values (v_espacio, p_membership_id, p_enlace_hash, now() + interval '14 days', v_usuario)
    returning id, expira_en into v_id, v_expira;
    perform auditar_acceso_web(
      v_espacio, v_usuario, 'persona', 'enlace_de_activacion', 'membership', p_membership_id,
      jsonb_build_object('origen', 'web', 'puerta', p_puerta, 'enlace_id', v_id,
                         'expira_en', v_expira)
      || case p_puerta
           when 'equipo' then jsonb_build_object('sesion_web_id', v_quien -> 'sesion_id')
           else jsonb_build_object('sesion_de_administracion_id', v_quien -> 'sesion_id')
         end);
    v_resultado := jsonb_build_object('ok', true, 'membership_id', p_membership_id,
                                      'nombre', v_persona.nombre, 'bot_usuario', v_bot,
                                      'expira_en', v_expira);
  end if;
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

create or replace function relaciones_de_la_pagina_de_tarea(p_token_hash text)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        acceso acceso_tarea%rowtype;
        resultado jsonb;
begin
  acceso := acceso_tarea_vigente(p_token_hash);
  if acceso.id is null then
    perform set_config('leda.workspace_id', previo, true);
    return null;
  end if;
  select jsonb_build_object(
    'pidio', (select m.nombre from membership m
               where m.id = t.pedida_por_membership_id),
    'volver', case when acceso.admin_app_user_id is not null then '/app/admin/'
                   else '/app/e/' || w.slug || '/' end,
    'espera_a', coalesce((
      select jsonb_agg(r.dato order by r.ve desc, r.titulo, r.id) from (
        select o.id, o.titulo, v.ve,
               case when v.ve then jsonb_build_object(
                      've', true, 'titulo', o.titulo, 'estado', o.estado,
                      'responsable', (select m.nombre from membership m
                                       where m.id = o.responsable_membership_id))
                    else jsonb_build_object('ve', false) end as dato
          from dependency d
          join task o on o.id = d.origen_task_id and o.workspace_id = d.workspace_id
          cross join lateral (
            select acceso.admin_app_user_id is not null
                   or puede_ver_tarea(acceso.membership_id, o.id) as ve) v
         where d.workspace_id = acceso.workspace_id and d.destino_task_id = t.id
           and d.tipo = 'bloqueante') r), '[]'::jsonb),
    'la_esperan', coalesce((
      select jsonb_agg(r.dato order by r.ve desc, r.titulo, r.id) from (
        select o.id, o.titulo, v.ve,
               case when v.ve then jsonb_build_object(
                      've', true, 'titulo', o.titulo, 'estado', o.estado,
                      'responsable', (select m.nombre from membership m
                                       where m.id = o.responsable_membership_id))
                    else jsonb_build_object('ve', false) end as dato
          from dependency d
          join task o on o.id = d.destino_task_id and o.workspace_id = d.workspace_id
          cross join lateral (
            select acceso.admin_app_user_id is not null
                   or puede_ver_tarea(acceso.membership_id, o.id) as ve) v
         where d.workspace_id = acceso.workspace_id and d.origen_task_id = t.id
           and d.tipo = 'bloqueante') r), '[]'::jsonb))
    into resultado
    from task t join workspace w on w.id = t.workspace_id
   where t.id = acceso.task_id and t.workspace_id = acceso.workspace_id;
  perform set_config('leda.workspace_id', previo, true);
  return resultado;
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
  -- La vista de un administrador de plataforma va además a la auditoría (ADR 0019, 7b y 7e;
  -- constitución §12), con la versión del pack del espacio; la del núcleo la pasa quien llama.
  if acceso.admin_app_user_id is not null then
    insert into audit_log (workspace_id, actor_app_user_id, actor_kind, accion, sujeto_tipo,
                           sujeto_id, detalle, pack_hash, nucleo_hash)
    values (acceso.workspace_id, acceso.admin_app_user_id, 'persona', 'ver_pagina_de_tarea',
            'task', acceso.task_id, jsonb_build_object('acceso_tarea_id', acceso.id),
            (select v.pack_hash from workspace_version v
              where v.workspace_id = acceso.workspace_id order by v.version desc limit 1),
            nullif(current_setting('leda.nucleo_hash', true), ''));
  end if;
  select * into t from task where id = acceso.task_id;
  faltan := tipos_de_evidencia_que_faltan(t.id);
  select p.tipos into tipos from task_evidence_policy p
   where p.workspace_id = t.workspace_id and p.area_id = t.area_id;
  select jsonb_build_object(
    'espacio', w.nombre,
    'zona_horaria', w.zona_horaria,
    'persona', coalesce((select m.nombre from membership m
                          where m.id = acceso.membership_id),
                        (select u.nombre from app_user u
                          where u.id = acceso.admin_app_user_id)),
    'tarea', jsonb_build_object(
      'titulo', t.titulo,
      'objetivo', (select o.titulo from objective o where o.id = t.objective_id),
      'area', (select a.nombre from area a where a.id = t.area_id),
      'responsable', (select m.nombre from membership m
                       where m.id = t.responsable_membership_id),
      'quien_aprueba', (select m.nombre from membership m
                         where m.id = quien_revisa_la_tarea(t.id)),
      'estado', t.estado,
      'fecha_objetivo', t.fecha_objetivo,
      'criterio_aceptacion', t.criterio_aceptacion,
      'prevision', (select jsonb_build_object('fecha', f.fecha_prevista, 'quien', m.nombre,
                                              'cuando', f.at)
                      from task_forecast f
                      join membership m on m.id = f.dicho_por_membership_id
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
                                  'quien', coalesce(em.nombre, adm.nombre), 'actor', e.actor_kind,
                                  'cuando', e.at) as dato
          from task_state_event e
          -- Quien lo hizo, como lo nombra este espacio; el administrador de plataforma, que no
          -- es del equipo, por su nombre de la plataforma (J7-5b).
          left join membership em
            on em.workspace_id = t.workspace_id and em.app_user_id = e.actor_app_user_id
          left join app_user adm
            on adm.id = e.actor_app_user_id and em.id is null
           and es_administrador_de_plataforma(adm.id)
         where e.task_id = t.id
        union all
        select ap.at, 2,
               jsonb_build_object('que', case ap.decision when 'aprobado' then 'aprobacion'
                                                          else 'pedido_de_cambios' end,
                                  'quien', m.nombre, 'comentario', ap.comentario,
                                  'cuando', ap.at)
          from approval ap
          join membership m on m.id = ap.aprobador_membership_id
         where ap.sujeto_tipo = 'tarea' and ap.sujeto_id = t.id
        union all
        select b.abierto_en, 3,
               jsonb_build_object('que', 'bloqueo', 'causa', b.causa, 'quien', m.nombre,
                                  'cuando', b.abierto_en, 'resuelto_en', b.resuelto_en)
          from blocker b
          left join membership m on m.id = b.abierto_por
         where b.task_id = t.id
        union all
        select f.at, 4,
               jsonb_build_object('que', 'prevision', 'fecha', f.fecha_prevista,
                                  'es_correccion', f.es_correccion, 'quien', m.nombre,
                                  'cuando', f.at)
          from task_forecast f
          join membership m on m.id = f.dicho_por_membership_id
         where f.task_id = t.id
        union all
        select u.at, 5,
               jsonb_build_object('que', 'quien_destraba', 'quien', pm.nombre,
                                  'destraba', coalesce(dm.nombre, u.destraba_externo),
                                  'no_sabe', u.no_sabe,
                                  'nadie_mas', u.destraba_membership_id
                                               = u.dicho_por_membership_id,
                                  'cuando', u.at)
          from blocker_unblocker u
          join blocker b on b.id = u.blocker_id
          join membership pm on pm.id = u.dicho_por_membership_id
          left join membership dm on dm.id = u.destraba_membership_id
         where b.task_id = t.id
           and not u.sin_decir_quien
        union all
        select d.at, 6,
               jsonb_build_object('que', 'dicho_del_bloqueo', 'quien', pm.nombre,
                                  'para_cuando', d.para_cuando, 'ya_esta', d.ya_esta,
                                  'no_le_corresponde', d.no_le_corresponde,
                                  'lo_que_dice', d.lo_que_dice, 'cuando', d.at)
          from dicho_de_quien_destraba d
          join blocker_unblocker u on u.id = d.blocker_unblocker_id
          join blocker b on b.id = u.blocker_id
          join membership pm on pm.id = d.dicho_por_membership_id
         where b.task_id = t.id
        union all
        select coalesce((a.detalle ->> 'at')::timestamptz, a.at), 7,
               jsonb_build_object('que', 'asentado',
                                  'por', case a.accion
                                           when 'asentar_bloqueo_que_sigue_abierto'
                                             then 'sigue_trabada'
                                           else 'nadie_lo_toma' end,
                                  'dias_habiles', (a.detalle ->> 'dias_habiles_trabada')::int,
                                  'cuando', coalesce((a.detalle ->> 'at')::timestamptz, a.at))
          from audit_log a
          join blocker b on b.id = a.sujeto_id
         where a.sujeto_tipo = 'blocker' and b.task_id = t.id
           and a.accion in ('asentar_bloqueo_que_sigue_abierto',
                            'informar_la_cadena_del_bloqueo',
                            'asentar_la_cadena_del_bloqueo')) h), '[]'::jsonb),
    'evidencia', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', e.id, 'clase', e.clase,
               'texto', case when not r.retirada then e.texto end,
               'enlace', case when e.clase = 'enlace' and not r.retirada then e.uri end,
               'nombre', case when not r.retirada then a.nombre_original end,
               'tipo_de_archivo', a.tipo, 'cubre', e.cubre,
               'ejemplo_aceptado', e.es_ejemplo_aceptado, 'quien', m.nombre, 'cuando', e.at,
               'retirada', r.retirada, 'retirada_el', r.retirada_el,
               'retirada_por_la_administracion', r.por_la_administracion,
               'motivo_del_retiro', r.motivo_de_la_administracion)
             order by e.at, e.id)
        from evidence e
        left join archivo a on a.workspace_id = e.workspace_id and a.id = e.archivo_id
        left join membership m on m.id = e.entregado_por
        -- Retirada por quien la entregó, o su contenido por la administración: la pieza o
        -- cualquier otra del espacio con el mismo archivo (un archivo se guarda una vez por
        -- huella). De una pieza retirada no sale su contenido (ADR 0019, decisión 3). De un
        -- retiro de la administración sale el motivo, nunca quién lo hizo (decisión 59).
        cross join lateral (
          select adm.at is not null or per.at is not null as retirada,
                 coalesce(adm.at, per.at) as retirada_el,
                 adm.at is not null as por_la_administracion,
                 adm.motivo as motivo_de_la_administracion
            from (select min(x.at) as at,
                         (array_agg(x.motivo order by x.at, x.id))[1] as motivo
                    from evidencia_retirada x
                    join evidence o on o.id = x.evidence_id
                   where x.retirada_por_app_user_id is not null
                     and (o.id = e.id
                          or (e.archivo_id is not null and o.workspace_id = e.workspace_id
                              and o.archivo_id = e.archivo_id))) adm,
                 (select min(x.at) as at from evidencia_retirada x
                   where x.evidence_id = e.id
                     and x.retirada_por_membership_id is not null) per) r
       where e.task_id = t.id), '[]'::jsonb))
    into resultado
    from workspace w where w.id = acceso.workspace_id;
  perform set_config('leda.workspace_id', previo, true);
  return resultado;
end $$;

create or replace function tareas_que_ve(
    p_membership_id uuid, p_vista text, p_ahora timestamptz)
returns table (task_id uuid, titulo text, estado text, fecha_objetivo timestamptz,
               asignada_en timestamptz, responsable text, area text, papel text,
               vencida boolean, bloqueo_abierto boolean, ve_la_pagina boolean,
               prevision date)
language sql stable set search_path = leda, public, pg_temp as $$
  with yo as (
    select m.id, m.workspace_id, r.autoridad_final
      from membership m
      join rol r on r.id = m.rol_id
     where m.id = p_membership_id and m.activo
  ),
  abiertas as (
    select t.id, t.workspace_id, t.titulo, t.estado, t.fecha_objetivo, t.creado_en,
           t.area_id, t.responsable_membership_id
      from task t
      join yo on yo.workspace_id = t.workspace_id
     where t.estado not in ('terminada', 'cancelada')
  ),
  -- Quién destraba hoy cada bloqueo abierto: lo último que se dijo.
  destraba as (
    select b.id as blocker_id, b.task_id, u.destraba_membership_id
      from blocker b
      join lateral (select x.destraba_membership_id from blocker_unblocker x
                     where x.blocker_id = b.id
                     order by x.at desc, x.id desc limit 1) u on true
     where b.resuelto_en is null
  ),
  -- Una tarea que espera otra: una dependencia bloqueante, o el bloqueo con el que dijo estar
  -- trabado quien destraba (`dicho_de_quien_destraba.espera_su_bloqueo_id`, 0044).
  esperas as (
    select d.destino_task_id as espera, d.origen_task_id as esperada
      from dependency d
     where d.tipo = 'bloqueante'
    union
    select b.task_id, y.task_id
      from destraba b
      join blocker_unblocker x on x.blocker_id = b.blocker_id
      join dicho_de_quien_destraba dd on dd.blocker_unblocker_id = x.id
      join blocker y on y.id = dd.espera_su_bloqueo_id
      join task o on o.id = y.task_id
     where b.destraba_membership_id = o.responsable_membership_id
       and dd.dicho_por_membership_id = o.responsable_membership_id
  ),
  filas as (
    select t.*, a.nombre as area_nombre, a.referente_membership_id,
           case
             when t.responsable_membership_id = yo.id then 'mia'
             when exists (select 1 from destraba b
                           where b.task_id = t.id and b.destraba_membership_id = yo.id)
                  or exists (select 1 from esperas e
                               join abiertas o on o.id = e.esperada
                              where e.espera = t.id and o.responsable_membership_id = yo.id)
                  or (t.estado = 'en_revision' and quien_revisa_la_tarea(t.id) = yo.id)
               then 'me_esperan'
             when exists (select 1 from esperas e
                            join abiertas w on w.id = e.espera
                           where e.esperada = t.id and w.responsable_membership_id = yo.id)
               then 'espero'
           end as papel,
           coalesce(t.responsable_membership_id = yo.id
                    or a.referente_membership_id = yo.id
                    or yo.autoridad_final, false) as ve_atrasos,
           t.estado in ('asignada', 'en_curso', 'bloqueada') as sigue,
           yo.autoridad_final as es_autoridad,
           yo.id as yo_id
      from abiertas t
      cross join yo
      join area a on a.id = t.area_id
  )
  select f.id, f.titulo, f.estado::text, f.fecha_objetivo,
         coalesce((select min(e.at) from task_state_event e
                    where e.task_id = f.id and e.estado_nuevo = 'asignada'), f.creado_en),
         rm.nombre, f.area_nombre, f.papel,
         -- Ya pasó su fecha y, para quien no ve los atrasos de la tarea, el atraso ya se habló
         -- (la regla a o la b del informe al grupo).
         coalesce(f.sigue and d.hoy > d.vence
                  and (f.ve_atrasos
                       or p.fecha_prevista > d.vence
                       or exists (select 1 from scheduled_notice n
                                   where n.task_id = f.id and n.tipo = 'escalamiento'
                                     and n.estado = 'enviado'
                                     and n.hechos ->> 'vence' = to_char(d.vence, 'YYYY-MM-DD'))),
                  false),
         exists (select 1 from blocker b where b.task_id = f.id and b.resuelto_en is null),
         puede_ver_tarea(f.yo_id, f.id),
         case when f.sigue and p.fecha_prevista > d.vence then p.fecha_prevista end
    from filas f
    join workspace w on w.id = f.workspace_id
    cross join lateral (
      select (f.fecha_objetivo at time zone w.zona_horaria)::date as vence,
             (coalesce(p_ahora, now()) at time zone w.zona_horaria)::date as hoy) d
    -- La previsión vigente: la última que ninguna otra reemplaza.
    left join lateral (
      select x.fecha_prevista from task_forecast x
       where x.task_id = f.id
         and not exists (select 1 from task_forecast y where y.reemplaza_id = x.id)
       order by x.at desc limit 1) p on true
    left join membership rm on rm.id = f.responsable_membership_id
   where case p_vista
           when 'tus' then f.papel is not null
           when 'sector' then f.referente_membership_id = f.yo_id
           when 'equipo' then f.es_autoridad
           else false
         end
   order by f.fecha_objetivo nulls last, f.titulo, f.id;
$$;

create or replace function terminadas_que_ve(
    p_membership_id uuid, p_vista text, p_ahora timestamptz)
returns table (task_id uuid, titulo text, responsable text, area text,
               terminada_en timestamptz)
language sql stable set search_path = leda, public, pg_temp as $$
  with yo as (
    select m.id, m.workspace_id, r.autoridad_final
      from membership m
      join rol r on r.id = m.rol_id
     where m.id = p_membership_id and m.activo
  ),
  terminadas as (
    select t.id, t.titulo, t.area_id, t.responsable_membership_id,
           coalesce((select max(e.at) from task_state_event e
                      where e.task_id = t.id and e.estado_nuevo = 'terminada'),
                    t.actualizado_en) as terminada_en
      from task t
      join yo on yo.workspace_id = t.workspace_id
     where t.estado = 'terminada'
  )
  select x.id, x.titulo, rm.nombre, a.nombre, x.terminada_en
    from terminadas x
    cross join yo
    join area a on a.id = x.area_id
    left join membership rm on rm.id = x.responsable_membership_id
   where x.terminada_en >= coalesce(p_ahora, now()) - interval '30 days'
     and case p_vista
           when 'tus' then x.responsable_membership_id = yo.id
           when 'sector' then a.referente_membership_id = yo.id
           when 'equipo' then yo.autoridad_final
           else false
         end
   order by x.terminada_en desc, x.titulo, x.id;
$$;

create or replace function esperas_que_ve(
    p_membership_id uuid, p_vista text, p_ahora timestamptz)
returns table (raiz uuid, ruta text, padre text, nivel integer, que text, quien text)
language sql stable set search_path = leda, public, pg_temp as $$
  with recursive
  raices as (
    select q.task_id from tareas_que_ve(p_membership_id, p_vista, p_ahora) q
     where q.bloqueo_abierto
  ),
  abiertas as (
    select t.id, t.titulo, t.responsable_membership_id
      from task t
     where t.estado not in ('terminada', 'cancelada')
  ),
  -- Quién destraba hoy cada bloqueo abierto: lo último que se dijo.
  bloqueos as (
    select b.id, b.task_id, b.causa, u.destraba_membership_id, u.destraba_externo
      from blocker b
      left join lateral (select x.destraba_membership_id, x.destraba_externo
                           from blocker_unblocker x
                          where x.blocker_id = b.id
                          order by x.at desc, x.id desc limit 1) u on true
     where b.resuelto_en is null
  ),
  -- El bloqueo con el que dijo estar trabado quien destraba (como `esperas` en la 0058).
  por_lo_dicho as (
    select b.id as blocker_id, b.task_id, y.task_id as esperada
      from bloqueos b
      join blocker_unblocker x on x.blocker_id = b.id
      join dicho_de_quien_destraba dd on dd.blocker_unblocker_id = x.id
      join blocker y on y.id = dd.espera_su_bloqueo_id
      join abiertas o on o.id = y.task_id
     where b.destraba_membership_id = o.responsable_membership_id
       and dd.dicho_por_membership_id = o.responsable_membership_id
  ),
  -- Lo que espera directamente cada tarea: otra tarea abierta, o un bloqueo que no lleva a
  -- ninguna.
  pasos as (
    select d.destino_task_id as tarea, 't' || d.origen_task_id::text as clave,
           d.origen_task_id as siguiente, o.titulo as que, m.nombre as quien
      from dependency d
      join abiertas o on o.id = d.origen_task_id
      left join membership m on m.id = o.responsable_membership_id
     where d.tipo = 'bloqueante'
    union
    select p.task_id, 't' || p.esperada::text, p.esperada, o.titulo, m.nombre
      from por_lo_dicho p
      join abiertas o on o.id = p.esperada
      left join membership m on m.id = o.responsable_membership_id
    union
    select b.task_id, 'b' || b.id::text, null::uuid, b.causa,
           coalesce(m.nombre, b.destraba_externo)
      from bloqueos b
      left join membership m on m.id = b.destraba_membership_id
     where not exists (select 1 from por_lo_dicho p where p.blocker_id = b.id)
  ),
  arbol (raiz, ruta, padre, nivel, siguiente, camino, que, quien) as (
    select r.task_id, '/' || p.clave, null::text, 1, p.siguiente, array[r.task_id],
           p.que, p.quien
      from raices r
      join pasos p on p.tarea = r.task_id
    union all
    select a.raiz, a.ruta || '/' || p.clave, a.ruta, a.nivel + 1, p.siguiente,
           a.camino || a.siguiente, p.que, p.quien
      from arbol a
      join pasos p on p.tarea = a.siguiente
     where a.nivel < 10 and not (a.siguiente = any (a.camino))
  )
  select a.raiz, a.ruta, a.padre, a.nivel, a.que, a.quien
    from arbol a
   order by a.raiz, a.ruta;
$$;

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
               'responsable', m.nombre, 'objetivo', o.titulo) order by t.titulo, t.id)
        from task t
        join objective o on o.id = t.objective_id
        left join membership m on m.id = t.responsable_membership_id
       where t.estado in ('asignada', 'en_curso', 'bloqueada', 'en_revision')), '[]'::jsonb),
    'integrantes', coalesce((
      select jsonb_agg(jsonb_build_object(
               'membership_id', m.id, 'nombre', m.nombre, 'area_id', a.id, 'area', a.nombre,
               'autoridad_final', r.autoridad_final,
               'conectado', u.telegram_user_id is not null,
               'revisa', case when ap.id is null then null
                              else jsonb_build_object('membership_id', ap.id,
                                                      'nombre', ap.nombre) end)
             order by m.nombre, m.id)
        from membership m
        join app_user u on u.id = m.app_user_id
        join area a on a.id = m.area_id
        join rol r on r.id = m.rol_id
        left join membership ap on ap.id = m.aprobador_membership_id and ap.activo
       where m.activo), '[]'::jsonb),
    -- Las áreas con su referente activo (migración 0071): quién decide en cada una (D10) y a quién
    -- se le pide lo de otra área (D14).
    'areas', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', a.id, 'nombre', a.nombre,
               'referente', case when ref.id is null then null
                                 else jsonb_build_object('membership_id', ref.id,
                                                         'nombre', ref.nombre) end)
             order by a.nombre, a.id)
        from area a
        left join membership ref on ref.id = a.referente_membership_id and ref.activo), '[]'::jsonb),
    -- Quiénes pueden revisar una tarea si quien carga lo elige (D3; migración 0071): Dirección y
    -- los referentes de área activos.
    'revisores', coalesce((
      select jsonb_agg(jsonb_build_object(
               'membership_id', m.id, 'nombre', m.nombre,
               'autoridad_final', r.autoridad_final,
               'areas', coalesce((select jsonb_agg(a.nombre order by a.nombre, a.id)
                                    from area a where a.referente_membership_id = m.id),
                                 '[]'::jsonb))
             order by m.nombre, m.id)
        from membership m
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
               'revisa', (select jsonb_build_object('membership_id', ref.id, 'nombre', ref.nombre)
                            from membership ref
                           where ref.id = quien_revisaria(v_persona, c.id, c.como)))
             order by i.orden)
        from jsonb_array_elements(v_resultado -> 'integrantes') with ordinality i(fila, orden)
        cross join lateral (select (i.fila ->> 'membership_id')::uuid as id) m
        cross join lateral (select m.id, como_carga(v_persona, m.id) as como) c
       where c.como is not null), '[]'::jsonb),
    'yo', (select jsonb_build_object('membership_id', m.id, 'nombre', m.nombre,
                                     'autoridad_final', r.autoridad_final,
                                     'elige_quien_revisa', r.autoridad_final)
             from membership m
             join rol r on r.id = m.rol_id
            where m.id = v_persona));
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

create or replace function pedidas_que_ve(p_membership_id uuid, p_ahora timestamptz)
returns table (task_id uuid, titulo text, estado text, fecha_objetivo timestamptz,
               responsable text, area text, terminada_en timestamptz)
language sql stable set search_path = leda, public, pg_temp as $$
  select x.id, x.titulo, x.estado, x.fecha_objetivo, x.responsable, x.area, x.terminada_en
    from (
      select t.id, t.titulo, t.estado::text as estado, t.fecha_objetivo, rm.nombre as responsable,
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
       where t.pedida_por_membership_id = yo.id
         and t.estado <> 'cancelada') x
   where x.terminada_en is null
      or x.terminada_en >= coalesce(p_ahora, now()) - interval '30 days'
   order by x.terminada_en is not null, x.fecha_objetivo nulls last, x.titulo, x.id;
$$;

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
               'membership_id', m.id, 'nombre', m.nombre,
               'areas', (select jsonb_agg(a.nombre order by a.nombre, a.id)
                           from area a where a.referente_membership_id = m.id))
             order by m.nombre, m.id)
        from membership m
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

commit;
