\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0083_las_areas_del_equipo.sql. El alta de una persona desde la web (J7-5 de
-- `odd/tasks/plataforma-jerarquias.md`; ADR 0023, decisión 4; ADR 0024; respuesta 6 de la J7):
-- por las dos puertas (Dirección en su espacio, el administrador de plataforma en cualquiera:
-- `quien_organiza_el_equipo`).
--
-- - `vista_previa_de_alta`: lo que haría dar de alta a una persona (nombre, área y rol; quién la
--   aprueba, por omisión el referente activo del área y, sin él, Dirección) o volver a sumar a
--   quien estuvo, con su huella y los problemas del equipo que dejaría. Hace el cambio y lo
--   deshace.
-- - `dar_de_alta` y `reactivar_integrante`: lo confirman con la clave de un solo uso y la huella;
--   cada uno deja una fila en `cambio_del_equipo` y su auditoría, y se niega si el equipo queda con
--   un problema que no tenía. El alta siempre crea una persona nueva: nunca la busca por el nombre.
-- - `emitir_enlace_de_activacion`: un enlace nuevo para quien todavía no conectó su Telegram, que
--   anula el anterior sin usar. El token lo arma la web y se muestra una sola vez; la base recibe y
--   guarda sólo su huella.
-- - Adentro, sin `execute` para nadie más: `cambiar_el_alta` (valida y escribe) y
--   `confirmar_alta` (la clave, la huella y el registro).
-- - `activation_token.token` pasa a `token_hash`: la huella (sha256, en hexadecimal) del token. Los
--   enlaces vigentes siguen sirviendo: se guarda la huella del que tenían.
--
-- Se deshace con `db/rollbacks/0084_el_alta_de_una_persona.sql` (los enlaces sin usar dejan de
-- servir: la huella no devuelve el token).
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0084 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0083 está aplicada y la 0084 no.
do $$ begin
  if to_regprocedure('leda.cambiar_un_area(uuid, text, jsonb, text)') is null then
    raise exception '0084 preflight failed: falta la 0083';
  end if;
  if to_regprocedure('leda.cambiar_el_alta(uuid, text, jsonb, text)') is not null then
    raise exception '0084 ya está aplicada.';
  end if;
end $$;

-- El token de un enlace de activación se guarda como huella (migración 0084; J7-5): quien lea la
-- tabla no puede reclamar la identidad de nadie.
alter table activation_token add column token_hash text;
update activation_token set token_hash = encode(sha256(convert_to(token, 'UTF8')), 'hex');
alter table activation_token alter column token_hash set not null;
alter table activation_token add constraint activation_token_token_hash_key unique (token_hash);
alter table activation_token add constraint activation_token_token_hash
  check (token_hash ~ '^[0-9a-f]{64}$');
alter table activation_token drop column token;

comment on column activation_token.token_hash is
  'J7-5 (migración 0084): la huella (sha256, en hexadecimal) del token del enlace. El token en claro sólo lo ve quien emite el enlace, una vez; la base no lo guarda.';

-- El alta de una persona (migración 0084; J7-5; ADR 0023, decisión 4; respuesta 6 de la J7).
-- - `cambiar_el_alta`: valida y hace el alta de una persona nueva (`alta`) o vuelve a sumar a una
--   que estuvo (`reactivar`), en el espacio de la transacción; devuelve el antes y el después en
--   palabras, quién la aprueba y la huella de lo que se va a hacer. Con `p_huella`, sólo lo hace
--   si es la misma de la vista previa.
-- - `vista_previa_de_alta`: el cambio, hecho y deshecho, con los problemas del equipo que dejaría.
-- - `confirmar_alta`: la clave de un solo uso, el cambio, la comprobación del equipo,
--   `cambio_del_equipo` y la auditoría. La llaman `dar_de_alta` y `reactivar_integrante`.
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
          select u.nombre into v_nombre from app_user u where u.id = v_persona.app_user_id;
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
        select m.id, u.nombre into v_aprobador, v_aprobador_nombre
          from membership m join app_user u on u.id = m.app_user_id
         where m.id = v_texto::uuid and m.workspace_id = p_espacio and m.activo
           for share of m;
        if v_aprobador is null then
          v_errores := v_errores || jsonb_build_object('campo', 'aprobador',
                                                       'motivo', 'no_es_integrante_activo');
        end if;
      end if;
    elsif v_area.id is not null and v_area.archivada_en is null then
      v_por_omision := true;
      select r.id, u.nombre into v_aprobador, v_aprobador_nombre
        from membership r join app_user u on u.id = r.app_user_id
       where r.id = v_area.referente_membership_id and r.workspace_id = p_espacio and r.activo
         and r.id is distinct from v_persona.id
         for share of r;
      if v_aprobador is null then
        select m.id, u.nombre into v_aprobador, v_aprobador_nombre
          from membership m
          join rol x on x.id = m.rol_id
          join app_user u on u.id = m.app_user_id
         where m.workspace_id = p_espacio and m.activo and x.autoridad_final
           and m.id is distinct from v_persona.id
         order by u.nombre, m.id
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
    if exists (select 1 from membership m join app_user u on u.id = m.app_user_id
                where m.workspace_id = p_espacio and m.activo
                  and lower(u.nombre) = lower(v_nombre)) then
      v_avisos := v_avisos || jsonb_build_object(
        'codigo', 'mismo_nombre',
        'mensaje', format('Ya hay alguien en el equipo que se llama %s: si es la misma persona, '
                          'no hace falta darla de alta.', v_nombre));
    elsif exists (select 1 from membership m join app_user u on u.id = m.app_user_id
                   where m.workspace_id = p_espacio and not m.activo
                     and lower(u.nombre) = lower(v_nombre)) then
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
    insert into membership (workspace_id, app_user_id, area_id, rol_id, aprobador_membership_id)
    values (p_espacio, v_usuario, v_area.id, v_rol.id, v_aprobador)
    returning id into v_id;
  else
    v_id := v_persona.id;
    v_antes := jsonb_build_object(
      'nombre', v_nombre,
      'area', (select a.nombre from area a where a.id = v_persona.area_id),
      'rol', (select r.nombre from rol r where r.id = v_persona.rol_id),
      'quien_aprueba', (select u.nombre from membership m join app_user u on u.id = m.app_user_id
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

create or replace function vista_previa_de_alta(
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
  -- El alta se hace de verdad, para ver cómo queda el equipo, y se deshace: la vista previa no
  -- escribe nada.
  begin
    v_cambio := cambiar_el_alta(v_espacio, p_accion, p_datos, null);
    if (v_cambio ->> 'ok')::boolean then
      v_despues := problemas_del_equipo(v_espacio);
    end if;
    raise exception using errcode = 'LDPRV', message = 'vista previa de un alta: se deshace';
  exception when sqlstate 'LDPRV' then
    null;
  end;
  if not (v_cambio ->> 'ok')::boolean then
    v_resultado := jsonb_build_object('ok', false, 'errores', v_cambio -> 'errores');
  else
    v_resultado := jsonb_build_object(
      'ok', true, 'accion', p_accion,
      'antes', v_cambio -> 'antes', 'despues', v_cambio -> 'despues',
      'aprobador', v_cambio -> 'aprobador', 'avisos', v_cambio -> 'avisos',
      'huella', v_cambio ->> 'huella',
      'problemas', v_despues,
      'problemas_nuevos', coalesce((
        select jsonb_agg(p) from jsonb_array_elements(v_despues) p
         where not v_antes @> jsonb_build_array(p)), '[]'::jsonb));
  end if;
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

create or replace function confirmar_alta(
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
  v_clase := case p_accion when 'alta' then 'alta' when 'reactivar' then 'reactivacion' end;

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
                                          'membership_id', v_previa.despues -> 'membership_id');
      else
        v_resultado := jsonb_build_object('ok', false, 'errores', jsonb_build_array(
          jsonb_build_object('campo', 'clave', 'motivo', 'usada_con_otros_datos')));
      end if;
      exit cambio;
    end if;

    -- El alta, y el equipo tiene que seguir cuadrando: un problema que no tenía lo deshace.
    v_antes := problemas_del_equipo(v_espacio);
    begin
      v_cambio := cambiar_el_alta(v_espacio, p_accion, p_datos, p_huella);
      if not (v_cambio ->> 'ok')::boolean then
        v_resultado := jsonb_build_object('ok', false, 'errores', v_cambio -> 'errores');
      else
        select coalesce(jsonb_agg(p), '[]'::jsonb) into v_nuevos
          from jsonb_array_elements(problemas_del_equipo(v_espacio)) p
         where not v_antes @> jsonb_build_array(p);
        if jsonb_array_length(v_nuevos) > 0 then
          raise exception using errcode = 'LDEQP',
                                message = 'el alta deja el equipo sin cuadrar';
        end if;
        v_despues := (v_cambio -> 'despues')
                     || jsonb_build_object('membership_id', v_cambio -> 'membership_id');
        insert into cambio_del_equipo (workspace_id, clase, puerta, hecho_por_app_user_id,
                                       hecho_por_membership_id, antes, despues, clave, huella,
                                       at)
        values (v_espacio, v_clase, p_puerta, v_usuario,
                (v_quien ->> 'membership_id')::uuid, v_cambio -> 'antes', v_despues, p_clave,
                p_huella, now());
        perform auditar_acceso_web(
          v_espacio, v_usuario, 'persona', v_clase, 'membership',
          (v_cambio ->> 'membership_id')::uuid,
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
                                          'membership_id', v_cambio -> 'membership_id');
      end if;
    exception when sqlstate 'LDEQP' then
      v_resultado := jsonb_build_object('ok', false, 'errores', jsonb_build_array(
        jsonb_build_object('campo', 'equipo', 'motivo', 'no_cuadra')), 'problemas', v_nuevos);
    end;
  end cambio;

  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

create or replace function dar_de_alta(
    p_puerta text, p_token_hash text, p_workspace_id uuid, p_nombre text, p_area_id uuid,
    p_rol_id uuid, p_aprobador_membership_id uuid, p_clave text, p_huella text)
returns jsonb
language sql security definer set search_path = leda, public, pg_temp as $$
  select confirmar_alta(
    p_puerta, p_token_hash, p_workspace_id, 'alta',
    jsonb_build_object('nombre', p_nombre, 'area_id', p_area_id, 'rol_id', p_rol_id,
                       'aprobador_id', p_aprobador_membership_id),
    p_clave, p_huella);
$$;

create or replace function reactivar_integrante(
    p_puerta text, p_token_hash text, p_workspace_id uuid, p_membership_id uuid,
    p_area_id uuid, p_rol_id uuid, p_aprobador_membership_id uuid, p_clave text, p_huella text)
returns jsonb
language sql security definer set search_path = leda, public, pg_temp as $$
  select confirmar_alta(
    p_puerta, p_token_hash, p_workspace_id, 'reactivar',
    jsonb_build_object('membership_id', p_membership_id, 'area_id', p_area_id,
                       'rol_id', p_rol_id, 'aprobador_id', p_aprobador_membership_id),
    p_clave, p_huella);
$$;

-- El enlace de activación de quien todavía no conectó su Telegram (migración 0084; J7-5; ADR
-- 0024). Anula el anterior sin usar (uno vigente por persona) y vence a los 14 días, como
-- `onboarding.generar_enlaces`. Recibe la huella del token, nunca el token: el enlace lo arma la
-- web con el usuario del bot del espacio, que devuelve esta función.
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
    select m.id, m.activo, u.nombre, u.telegram_user_id into v_persona
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

comment on function vista_previa_de_alta(text, text, uuid, text, jsonb) is
  'J7-5 (migración 0084; ADR 0023, decisión 4): lo que haría dar de alta a una persona o volver a sumar a quien estuvo, con quién la aprueba, su huella y los problemas del equipo que dejaría. Hace el cambio y lo deshace: no escribe nada.';
comment on function dar_de_alta(text, text, uuid, text, uuid, uuid, uuid, text, text) is
  'J7-5 (migración 0084; respuesta 6 de la J7): da de alta a una persona nueva (nombre, área, rol y quién la aprueba; por omisión el referente activo del área o, sin él, Dirección), sin conectar hasta que abra su enlace, con la clave de un solo uso y la huella de la vista previa. Nunca la busca por el nombre.';
comment on function reactivar_integrante(text, text, uuid, uuid, uuid, uuid, uuid, text, text) is
  'J7-5 (migración 0084): vuelve a sumar al equipo a quien lo dejó, con su membresía de antes, en el área, el rol y con quien la aprueba que se eligen.';
comment on function emitir_enlace_de_activacion(text, text, uuid, uuid, text) is
  'J7-5 (migración 0084; ADR 0024): un enlace de activación nuevo para quien todavía no conectó su Telegram; anula el anterior sin usar y vence a los 14 días. Recibe y guarda sólo la huella del token.';

alter function cambiar_el_alta(uuid, text, jsonb, text) owner to leda_owner;
alter function vista_previa_de_alta(text, text, uuid, text, jsonb) owner to leda_owner;
alter function confirmar_alta(text, text, uuid, text, jsonb, text, text) owner to leda_owner;
alter function dar_de_alta(text, text, uuid, text, uuid, uuid, uuid, text, text)
  owner to leda_owner;
alter function reactivar_integrante(text, text, uuid, uuid, uuid, uuid, uuid, text, text)
  owner to leda_owner;
alter function emitir_enlace_de_activacion(text, text, uuid, uuid, text) owner to leda_owner;
revoke execute on function cambiar_el_alta(uuid, text, jsonb, text) from public;
revoke execute on function vista_previa_de_alta(text, text, uuid, text, jsonb) from public;
revoke execute on function confirmar_alta(text, text, uuid, text, jsonb, text, text) from public;
revoke execute on function dar_de_alta(text, text, uuid, text, uuid, uuid, uuid, text, text)
  from public;
revoke execute on function reactivar_integrante(text, text, uuid, uuid, uuid, uuid, uuid, text,
                                                text) from public;
revoke execute on function emitir_enlace_de_activacion(text, text, uuid, uuid, text) from public;
grant execute on function vista_previa_de_alta(text, text, uuid, text, jsonb) to leda_app;
grant execute on function dar_de_alta(text, text, uuid, text, uuid, uuid, uuid, text, text)
  to leda_app;
grant execute on function reactivar_integrante(text, text, uuid, uuid, uuid, uuid, uuid, text,
                                               text) to leda_app;
grant execute on function emitir_enlace_de_activacion(text, text, uuid, uuid, text) to leda_app;

commit;
