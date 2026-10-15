\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0082_ver_el_equipo.sql. Las áreas desde la web (J7-4 de
-- `odd/tasks/plataforma-jerarquias.md`; ADR 0023, decisión 4; mecánica §7): crear, renombrar y
-- archivar un área, por las dos puertas (Dirección en su espacio, el administrador de plataforma
-- en cualquiera: `quien_organiza_el_equipo`).
--
-- - `vista_previa_de_area`: lo que cambiaría, con su huella, y los problemas del equipo que
--   dejaría. Hace el cambio de verdad y lo deshace: lo que muestra es lo que se confirmaría.
-- - `crear_area`, `renombrar_area` y `archivar_area`: lo confirman con la clave de un solo uso y la
--   huella de la vista previa; cada uno deja una fila en `cambio_del_equipo` y su auditoría, y se
--   niega si el equipo queda con un problema que no tenía.
-- - `opciones_de_areas`: los tipos de evidencia del espacio, para elegir los de un área nueva.
-- - Adentro, sin `execute` para nadie más: `cambiar_un_area` (valida y escribe),
--   `confirmar_cambio_de_area` (la clave, la huella y el registro) y
--   `tipos_de_evidencia_del_espacio`.
--
-- Sólo funciones: no toca tablas ni datos. Se deshace con
-- `db/rollbacks/0083_las_areas_del_equipo.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0083 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0082 está aplicada y la 0083 no.
do $$ begin
  if to_regprocedure('leda.equipo_de(text, text, uuid)') is null then
    raise exception '0083 preflight failed: falta la 0082';
  end if;
  if to_regprocedure('leda.cambiar_un_area(uuid, text, jsonb, text)') is not null then
    raise exception '0083 ya está aplicada.';
  end if;
end $$;

-- Las áreas desde la web (migración 0083; J7-4; ADR 0023, decisión 4; mecánica §7).
-- - `tipos_de_evidencia_del_espacio`: los tipos que conoce alguna política de evidencia del
--   espacio (los del pack, con sus palabras), para elegir los que pide un área nueva.
-- - `cambiar_un_area`: valida y hace un cambio de un área (`crear`, `renombrar` o `archivar`)
--   en el espacio de la transacción; devuelve el antes y el después en palabras, y la huella de
--   lo que se va a hacer. Con `p_huella`, sólo lo hace si es la misma de la vista previa.
-- - `vista_previa_de_area`: el cambio, hecho y deshecho, con los problemas del equipo que dejaría.
-- - `confirmar_cambio_de_area`: la clave de un solo uso, el cambio, la comprobación del equipo,
--   `cambio_del_equipo` y la auditoría. La llaman `crear_area`, `renombrar_area` y
--   `archivar_area`.
create or replace function tipos_de_evidencia_del_espacio(p_espacio uuid)
returns jsonb
language sql stable set search_path = leda, public, pg_temp as $$
  -- Cada tipo, con sus palabras (las del pack; sin ellas, el nombre del tipo), una sola vez.
  select coalesce(jsonb_agg(jsonb_build_object('tipo', x.tipo, 'en_palabras', x.en_palabras)
                            order by x.en_palabras, x.tipo), '[]'::jsonb)
    from (select n.tipo,
                 coalesce((select p.tipos -> n.tipo ->> 'en_palabras'
                             from task_evidence_policy p
                            where p.workspace_id = p_espacio and p.tipos ? n.tipo
                            order by p.actualizado_en desc, p.area_id
                            limit 1),
                          replace(n.tipo, '_', ' ')) as en_palabras
            from (select distinct t.tipo
                    from task_evidence_policy p
                    cross join lateral (
                      select jsonb_object_keys(p.tipos) as tipo
                      union
                      select unnest(p.evidencia_requerida)) t
                   where p.workspace_id = p_espacio) n) x;
$$;

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
          select m.id, u.nombre into v_referente, v_referente_nombre
            from membership m join app_user u on u.id = m.app_user_id
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

create or replace function vista_previa_de_area(
    p_puerta text, p_token_hash text, p_workspace_id uuid, p_accion text, p_datos jsonb)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_quien jsonb;
        v_espacio uuid;
        v_cambio jsonb;
        v_antes jsonb;
        v_despues jsonb := '[]'::jsonb;
        v_resultado jsonb;
begin
  v_quien := quien_organiza_el_equipo(p_puerta, p_token_hash, p_workspace_id);
  if not (v_quien ->> 'ok')::boolean then
    perform set_config('leda.workspace_id', previo, true);
    return v_quien;
  end if;
  v_espacio := (v_quien ->> 'workspace_id')::uuid;
  v_antes := problemas_del_equipo(v_espacio);
  -- El cambio se hace de verdad, para ver cómo queda el equipo, y se deshace: la vista previa no
  -- escribe nada.
  begin
    v_cambio := cambiar_un_area(v_espacio, p_accion, p_datos, null);
    if (v_cambio ->> 'ok')::boolean then
      v_despues := problemas_del_equipo(v_espacio);
    end if;
    raise exception using errcode = 'LDPRV', message = 'vista previa de un área: se deshace';
  exception when sqlstate 'LDPRV' then
    null;
  end;
  if not (v_cambio ->> 'ok')::boolean then
    v_resultado := jsonb_build_object('ok', false, 'errores', v_cambio -> 'errores');
  else
    v_resultado := jsonb_build_object(
      'ok', true, 'accion', p_accion,
      'antes', v_cambio -> 'antes', 'despues', v_cambio -> 'despues',
      'huella', v_cambio ->> 'huella',
      'problemas', v_despues,
      'problemas_nuevos', coalesce((
        select jsonb_agg(p) from jsonb_array_elements(v_despues) p
         where not v_antes @> jsonb_build_array(p)), '[]'::jsonb));
  end if;
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

create or replace function confirmar_cambio_de_area(
    p_puerta text, p_token_hash text, p_workspace_id uuid, p_accion text, p_datos jsonb,
    p_clave text, p_huella text)
returns jsonb
language plpgsql set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_quien jsonb;
        v_espacio uuid;
        v_usuario uuid;
        v_clase text;
        v_previa cambio_del_equipo%rowtype;
        v_errores jsonb := '[]'::jsonb;
        v_antes jsonb;
        v_cambio jsonb;
        v_nuevos jsonb := '[]'::jsonb;
        v_despues jsonb;
        v_resultado jsonb;
begin
  -- La sesión, en cada llamada, y el espacio, fijado.
  v_quien := quien_organiza_el_equipo(p_puerta, p_token_hash, p_workspace_id);
  if not (v_quien ->> 'ok')::boolean then
    perform set_config('leda.workspace_id', previo, true);
    return v_quien;
  end if;
  v_espacio := (v_quien ->> 'workspace_id')::uuid;
  v_usuario := (v_quien ->> 'app_user_id')::uuid;
  v_clase := case p_accion when 'crear' then 'area_creada'
                           when 'renombrar' then 'area_renombrada'
                           when 'archivar' then 'area_archivada' end;

  <<cambio>>
  begin
    -- La clave de un solo uso y la huella de la vista previa que se confirma.
    if nullif(btrim(p_clave), '') is null then
      v_errores := v_errores || jsonb_build_object('campo', 'clave', 'motivo', 'falta');
    elsif p_clave !~ '^[A-Za-z0-9_-]{16,128}$' then
      v_errores := v_errores || jsonb_build_object('campo', 'clave', 'motivo', 'mal_formada');
    end if;
    if nullif(btrim(p_huella), '') is null then
      v_errores := v_errores || jsonb_build_object('campo', 'huella', 'motivo', 'falta');
    elsif p_huella !~ '^[0-9a-f]{64}$' then
      v_errores := v_errores || jsonb_build_object('campo', 'huella', 'motivo', 'mal_formada');
    end if;
    if jsonb_array_length(v_errores) > 0 then
      v_resultado := jsonb_build_object('ok', false, 'errores', v_errores);
      exit cambio;
    end if;

    -- La misma clave con la misma huella devuelve lo que ya se hizo; con otra, se rechaza.
    perform pg_advisory_xact_lock(hashtextextended(v_espacio::text || ':' || p_clave, 0));
    select * into v_previa from cambio_del_equipo c
     where c.workspace_id = v_espacio and c.clave = p_clave;
    if v_previa.id is not null then
      if v_previa.huella = p_huella and v_previa.clase is not distinct from v_clase then
        v_resultado := jsonb_build_object('ok', true, 'repetida', true,
                                          'area_id', v_previa.despues -> 'area_id');
      else
        v_resultado := jsonb_build_object('ok', false, 'errores', jsonb_build_array(
          jsonb_build_object('campo', 'clave', 'motivo', 'usada_con_otros_datos')));
      end if;
      exit cambio;
    end if;

    -- El cambio, y el equipo tiene que seguir cuadrando: un problema que no tenía lo deshace.
    v_antes := problemas_del_equipo(v_espacio);
    begin
      v_cambio := cambiar_un_area(v_espacio, p_accion, p_datos, p_huella);
      if not (v_cambio ->> 'ok')::boolean then
        v_resultado := jsonb_build_object('ok', false, 'errores', v_cambio -> 'errores');
      else
        select coalesce(jsonb_agg(p), '[]'::jsonb) into v_nuevos
          from jsonb_array_elements(problemas_del_equipo(v_espacio)) p
         where not v_antes @> jsonb_build_array(p);
        if jsonb_array_length(v_nuevos) > 0 then
          raise exception using errcode = 'LDEQP',
                                message = 'el cambio de un área deja el equipo sin cuadrar';
        end if;
        v_despues := (v_cambio -> 'despues')
                     || jsonb_build_object('area_id', v_cambio -> 'area_id');
        insert into cambio_del_equipo (workspace_id, clase, puerta, hecho_por_app_user_id,
                                       hecho_por_membership_id, antes, despues, clave, huella,
                                       at)
        values (v_espacio, v_clase, p_puerta, v_usuario,
                (v_quien ->> 'membership_id')::uuid, v_cambio -> 'antes', v_despues, p_clave,
                p_huella, now());
        perform auditar_acceso_web(
          v_espacio, v_usuario, 'persona', v_clase, 'area', (v_cambio ->> 'area_id')::uuid,
          jsonb_build_object(
            'origen', 'web',
            'puerta', p_puerta,
            'hecho_por_app_user_id', v_usuario,
            'hecho_por_membership_id', v_quien -> 'membership_id',
            'antes', v_cambio -> 'antes',
            'despues', v_despues)
          || case p_puerta
               when 'equipo' then jsonb_build_object('sesion_web_id', v_quien -> 'sesion_id')
               else jsonb_build_object('sesion_de_administracion_id', v_quien -> 'sesion_id')
             end);
        v_resultado := jsonb_build_object('ok', true, 'repetida', false,
                                          'area_id', v_cambio -> 'area_id');
      end if;
    exception when sqlstate 'LDEQP' then
      v_resultado := jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'equipo', 'motivo', 'no_cuadra')), 'problemas', v_nuevos);
    end;
  end cambio;

  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

create or replace function crear_area(
    p_puerta text, p_token_hash text, p_workspace_id uuid, p_nombre text, p_aprobacion text,
    p_referente_membership_id uuid, p_evidencia text[], p_sin_evidencia boolean, p_clave text,
    p_huella text)
returns jsonb
language sql security definer set search_path = leda, public, pg_temp as $$
  select confirmar_cambio_de_area(
    p_puerta, p_token_hash, p_workspace_id, 'crear',
    jsonb_build_object('nombre', p_nombre, 'aprobacion', p_aprobacion,
                       'referente_id', p_referente_membership_id,
                       'evidencia', to_jsonb(p_evidencia),
                       'sin_evidencia', coalesce(p_sin_evidencia, false)),
    p_clave, p_huella);
$$;

create or replace function renombrar_area(
    p_puerta text, p_token_hash text, p_workspace_id uuid, p_area_id uuid, p_nombre text,
    p_clave text, p_huella text)
returns jsonb
language sql security definer set search_path = leda, public, pg_temp as $$
  select confirmar_cambio_de_area(
    p_puerta, p_token_hash, p_workspace_id, 'renombrar',
    jsonb_build_object('area_id', p_area_id, 'nombre', p_nombre), p_clave, p_huella);
$$;

create or replace function archivar_area(
    p_puerta text, p_token_hash text, p_workspace_id uuid, p_area_id uuid, p_clave text,
    p_huella text)
returns jsonb
language sql security definer set search_path = leda, public, pg_temp as $$
  select confirmar_cambio_de_area(
    p_puerta, p_token_hash, p_workspace_id, 'archivar',
    jsonb_build_object('area_id', p_area_id), p_clave, p_huella);
$$;

create or replace function opciones_de_areas(
    p_puerta text, p_token_hash text, p_workspace_id uuid)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_quien jsonb;
        v_resultado jsonb;
begin
  v_quien := quien_organiza_el_equipo(p_puerta, p_token_hash, p_workspace_id);
  if not (v_quien ->> 'ok')::boolean then
    perform set_config('leda.workspace_id', previo, true);
    return v_quien;
  end if;
  v_resultado := jsonb_build_object(
    'ok', true,
    'tipos_de_evidencia',
    tipos_de_evidencia_del_espacio((v_quien ->> 'workspace_id')::uuid));
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

comment on function vista_previa_de_area(text, text, uuid, text, jsonb) is
  'J7-4 (migración 0083; ADR 0023, decisión 4): lo que cambiaría crear, renombrar o archivar un área, con su huella y los problemas del equipo que dejaría. Hace el cambio y lo deshace: no escribe nada.';
comment on function crear_area(text, text, uuid, text, text, uuid, text[], boolean, text, text) is
  'J7-4 (migración 0083; mecánica §7): crea un área con quién aprueba su trabajo (su referente, el área misma o Dirección) y su evidencia (tipos del espacio o ninguna, a propósito), con la clave de un solo uso y la huella de la vista previa.';
comment on function renombrar_area(text, text, uuid, uuid, text, text, text) is
  'J7-4 (migración 0083): cambia sólo el nombre que se ve de un área; el slug no cambia.';
comment on function archivar_area(text, text, uuid, uuid, text, text) is
  'J7-4 (migración 0083; ADR 0023, decisión 4): archiva un área sin gente activa ni tareas abiertas. Un área nunca se borra.';
comment on function opciones_de_areas(text, text, uuid) is
  'J7-4 (migración 0083): los tipos de evidencia del espacio, para elegir los de un área nueva.';

alter function tipos_de_evidencia_del_espacio(uuid) owner to leda_owner;
alter function cambiar_un_area(uuid, text, jsonb, text) owner to leda_owner;
alter function vista_previa_de_area(text, text, uuid, text, jsonb) owner to leda_owner;
alter function confirmar_cambio_de_area(text, text, uuid, text, jsonb, text, text)
  owner to leda_owner;
alter function crear_area(text, text, uuid, text, text, uuid, text[], boolean, text, text)
  owner to leda_owner;
alter function renombrar_area(text, text, uuid, uuid, text, text, text) owner to leda_owner;
alter function archivar_area(text, text, uuid, uuid, text, text) owner to leda_owner;
alter function opciones_de_areas(text, text, uuid) owner to leda_owner;
revoke execute on function tipos_de_evidencia_del_espacio(uuid) from public;
revoke execute on function cambiar_un_area(uuid, text, jsonb, text) from public;
revoke execute on function vista_previa_de_area(text, text, uuid, text, jsonb) from public;
revoke execute on function confirmar_cambio_de_area(text, text, uuid, text, jsonb, text, text)
  from public;
revoke execute on function crear_area(text, text, uuid, text, text, uuid, text[], boolean, text,
                                      text) from public;
revoke execute on function renombrar_area(text, text, uuid, uuid, text, text, text) from public;
revoke execute on function archivar_area(text, text, uuid, uuid, text, text) from public;
revoke execute on function opciones_de_areas(text, text, uuid) from public;
grant execute on function vista_previa_de_area(text, text, uuid, text, jsonb) to leda_app;
grant execute on function crear_area(text, text, uuid, text, text, uuid, text[], boolean, text,
                                     text) to leda_app;
grant execute on function renombrar_area(text, text, uuid, uuid, text, text, text) to leda_app;
grant execute on function archivar_area(text, text, uuid, uuid, text, text) to leda_app;
grant execute on function opciones_de_areas(text, text, uuid) to leda_app;

commit;
