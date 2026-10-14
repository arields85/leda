\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0071_la_carga_del_equipo.sql.
--
-- Borra la carga por la puerta del equipo (`cargar_tarea_web`, `opciones_de_la_carga_del_equipo`
-- y sus ayudantes), la reapertura (`reabrir_tarea`, `reapertura_de_tarea`), lo pedido
-- (`pedidas_de_la_sesion`) y las dos columnas de la tarea, y devuelve a como las dejó la cadena
-- antes de la 0071: `quien_revisa_la_tarea`, `puede_ver_tarea` y `aplicar_cambio_de_responsable`
-- (0046 y 0050), `motivo_no_cierra_tarea` (0045), `tipos_de_evidencia_que_faltan` (0034),
-- `opciones_de_la_carga` (0067) y `cargar_tarea` (0070). Se niega si alguna tarea guarda quién la
-- revisa o quién la pidió, o si alguna se reabrió: se perderían.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0071 rollback requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if exists (select 1 from task
              where revisor_membership_id is not null or pedida_por_membership_id is not null)
     or exists (select 1 from reapertura_de_tarea) then
    raise exception '0071 rollback refused: hay tareas cargadas por la puerta del equipo, con quién las revisa o quién las pidió, o reabiertas; respaldalas y sacalas primero';
  end if;
end $$;

drop function pedidas_de_la_sesion(text, timestamptz);
drop function pedidas_que_ve(uuid, timestamptz);
drop function reabrir_tarea(text, uuid, text);
drop function opciones_de_la_carga_del_equipo(text, timestamptz);
drop function quien_carga_en_el_equipo(text, uuid);
drop function quien_revisaria(uuid, uuid, text);
drop function como_carga(uuid, uuid);

create or replace function quien_revisa_la_tarea(p_task uuid)
returns uuid
language sql stable set search_path = leda, public, pg_temp as $$
  select m.aprobador_membership_id
    from task t
    join membership m on m.id = coalesce(t.era_de_membership_id, t.responsable_membership_id)
   where t.id = p_task;
$$;

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
  new.revisa_membership_id := (select m.aprobador_membership_id from membership m
                                where m.id = era);
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
            and e.at > coalesce(
              (select max(a.at) from approval a
                where a.sujeto_tipo = 'tarea' and a.sujeto_id = t.id
                  and a.decision = 'rechazado'),
              '-infinity'::timestamptz)
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

create or replace function opciones_de_la_carga(
    p_token_hash text, p_workspace_id uuid, p_ahora timestamptz)
returns jsonb
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        v_administrador uuid;
        v_espacio workspace%rowtype;
        v_hoy date;
        v_desde date;
        v_hora_fin time;
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
  -- Hoy se ofrece sólo si la jornada del espacio no cerró: la tarea vence a esa hora, y cargada
  -- después nacería vencida (migración 0064).
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
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
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

drop function cargar_tarea_web(text, text, uuid, uuid, text, text, uuid, date, text, text[], uuid,
                               uuid, text, timestamptz, uuid);
drop function opciones_de_la_carga_en(uuid, timestamptz);
drop function puede_ser_quien_revisa(uuid);

drop table reapertura_de_tarea;
alter table task drop constraint task_pedida_por;
alter table task drop constraint task_revisor;
alter table task drop column pedida_por_membership_id;
alter table task drop column revisor_membership_id;

commit;
