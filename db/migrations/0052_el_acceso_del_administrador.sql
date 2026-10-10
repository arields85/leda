\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0051_las_revisiones_de_la_c5d_y_del_detalle.sql. El acceso del administrador de
-- plataforma a la página de una tarea y el retiro de contenido por la administración (ADR 0019,
-- decisiones 3 y 7b; porción 5 de la C-3; `odd/tasks/fase-c.md`).
--
-- 1. `acceso_tarea.admin_app_user_id`: un enlace atado al usuario de plataforma y a una tarea de
--    un espacio, no a una membresía (un administrador no tiene por qué ser del equipo).
--    Exactamente uno de los dos, `membership_id` o `admin_app_user_id`. Lo emite la conexión
--    administrativa, cuando lo pide por el bot de administración (`leda.motor.administracion`),
--    nunca por el del espacio (constitución §2).
-- 2. `evidencia_retirada.retirada_por_app_user_id`: el retiro del contenido de una pieza por la
--    administración (ADR 0019, decisión 3), con quién y por qué. La pieza y su archivo no se
--    borran; una vez por quien la entregó y una vez por la administración (dos índices únicos
--    parciales en lugar de `evidencia_retirada_una_vez`).
-- 3. `exigir_administrador_de_plataforma`: lo de un administrador sólo lo escribe `leda_admin` y
--    sólo para quien tiene el rol de plataforma.
-- 4. Las funciones de la página: `acceso_tarea_vigente` revalida el rol de plataforma en cada
--    pedido; `leer_pagina_de_tarea` y `leer_archivo_de_tarea` dejan cada vista y cada descarga
--    del administrador también en `audit_log` (7b, 7e; constitución §12), y de una pieza
--    retirada no devuelven su contenido (ni texto, ni enlace, ni nombre); un archivo cuyo
--    contenido retiró la administración no se sirve por ninguna pieza del espacio.
--
-- Aislamiento: sin tablas nuevas; el enlace de un administrador sigue atado a una tarea de un
-- espacio por la clave compuesta de siempre, y la página lee sólo esa tarea. Las funciones siguen
-- siendo de `leda_owner`, con sus mismos privilegios.
--
-- Se deshace con `db/rollbacks/0052_el_acceso_del_administrador.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0052 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0051 está aplicada y la 0052 no.
do $$ begin
  if not exists (select 1 from information_schema.columns
                  where table_schema = 'leda' and table_name = 'pedido_de_detalle'
                    and column_name = 'decidido_por_membership_id') then
    raise exception '0052 preflight failed: falta la 0051';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'acceso_tarea'
                and column_name = 'admin_app_user_id') then
    raise exception '0052 ya está aplicada.';
  end if;
end $$;

-- 1. El acceso de un administrador de plataforma.
alter table acceso_tarea add column admin_app_user_id uuid references app_user(id);
alter table acceso_tarea alter column membership_id drop not null;
alter table acceso_tarea add constraint acceso_tarea_de_quien
  check ((membership_id is null) <> (admin_app_user_id is null));
comment on table acceso_tarea is
  'ADR 0019, decisiones 7a y 7b: el enlace personal a la página de una tarea, de una persona del equipo (membership_id) o de un administrador de plataforma (admin_app_user_id, porción 5), exactamente uno. Sólo el hash del token; sin vencimiento; el derecho a ver (o el rol de plataforma) se revalida en cada pedido. leda_app no tiene privilegios: sólo execute sobre sus funciones.';

-- 2. El retiro de contenido por la administración.
alter table evidencia_retirada add column retirada_por_app_user_id uuid references app_user(id);
alter table evidencia_retirada alter column retirada_por_membership_id drop not null;
alter table evidencia_retirada add constraint evidencia_retirada_de_quien
  check ((retirada_por_membership_id is null) <> (retirada_por_app_user_id is null));
alter table evidencia_retirada drop constraint evidencia_retirada_una_vez;
create unique index evidencia_retirada_una_vez_por_quien_la_entrego
  on evidencia_retirada (evidence_id) where retirada_por_membership_id is not null;
create unique index evidencia_retirada_una_vez_por_la_administracion
  on evidencia_retirada (evidence_id) where retirada_por_app_user_id is not null;
comment on table evidencia_retirada is
  'ADR 0019, decisión 3: una pieza de evidencia retirada por quien la entregó (retirada_por_membership_id), mientras la tarea no está aprobada, o su contenido retirado por la administración de plataforma (retirada_por_app_user_id, porción 5): una vez cada uno. Sólo se agrega; la evidencia no se borra, deja de contar para la política y de lo retirado no se muestra el contenido.';

-- 3. Lo de un administrador, sólo de la administración.
-- El acceso de un administrador de plataforma a la página de una tarea y el retiro de contenido
-- por la administración (porción 5 de la C-3; migración 0052): sólo los escribe la conexión
-- administrativa y sólo para quien tiene el rol de plataforma. Vale también contra una
-- aplicación que nombre a un administrador de verdad: `leda_app` puede agregar retiros, los de
-- quien entregó la pieza. Sólo al agregar: revocar el enlace de quien ya no es administrador
-- tiene que poder hacerse.
create or replace function exigir_administrador_de_plataforma() returns trigger as $$
declare usuario uuid := (to_jsonb(new) ->> tg_argv[0])::uuid;
begin
  if usuario is not null then
    if current_user <> 'leda_admin' then
      raise exception '%: lo de un administrador de plataforma lo escribe sólo la administración',
        tg_table_name;
    end if;
    if not exists (select 1 from platform_role p
                    where p.app_user_id = usuario and p.rol = 'administrador') then
      raise exception '%: % no es administrador de plataforma', tg_table_name, tg_argv[0];
    end if;
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_exigir_administrador_de_plataforma
  before insert on acceso_tarea
  for each row execute function exigir_administrador_de_plataforma('admin_app_user_id');
create trigger trg_exigir_administrador_de_plataforma
  before insert on evidencia_retirada
  for each row execute function exigir_administrador_de_plataforma('retirada_por_app_user_id');

-- 4. Las funciones de la página.
create or replace function acceso_tarea_vigente(p_token_hash text)
returns acceso_tarea
language plpgsql set search_path = leda, public, pg_temp as $$
declare acceso acceso_tarea%rowtype;
begin
  if p_token_hash is null or p_token_hash !~ '^[0-9a-f]{64}$' then
    return null;
  end if;
  perform set_config('leda.token_de_tarea', p_token_hash, true);
  select * into acceso from acceso_tarea a
   where a.token_hash = p_token_hash and a.revocado_en is null;
  perform set_config('leda.token_de_tarea', '', true);
  if acceso.id is null then
    return null;
  end if;
  perform set_config('leda.workspace_id', acceso.workspace_id::text, true);
  -- El de un administrador de plataforma (porción 5) vale mientras tenga el rol; el de una
  -- persona del equipo, mientras pueda ver la tarea.
  if acceso.admin_app_user_id is not null then
    if not exists (select 1 from platform_role p
                    where p.app_user_id = acceso.admin_app_user_id
                      and p.rol = 'administrador') then
      return null;
    end if;
  elsif not puede_ver_tarea(acceso.membership_id, acceso.task_id) then
    return null;
  end if;
  return acceso;
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
    'persona', coalesce((select u.nombre from membership m
                           join app_user u on u.id = m.app_user_id
                          where m.id = acceso.membership_id),
                        (select u.nombre from app_user u
                          where u.id = acceso.admin_app_user_id)),
    'tarea', jsonb_build_object(
      'titulo', t.titulo,
      'objetivo', (select o.titulo from objective o where o.id = t.objective_id),
      'area', (select a.nombre from area a where a.id = t.area_id),
      'responsable', (select u.nombre from membership m join app_user u on u.id = m.app_user_id
                       where m.id = t.responsable_membership_id),
      'quien_aprueba', (select u.nombre from membership m
                          join app_user u on u.id = m.app_user_id
                         where m.id = quien_revisa_la_tarea(t.id)),
      'estado', t.estado,
      'fecha_objetivo', t.fecha_objetivo,
      'criterio_aceptacion', t.criterio_aceptacion,
      'prevision', (select jsonb_build_object('fecha', f.fecha_prevista, 'quien', u.nombre,
                                              'cuando', f.at)
                      from task_forecast f
                      join membership m on m.id = f.dicho_por_membership_id
                      join app_user u on u.id = m.app_user_id
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
                                  'quien', u.nombre, 'actor', e.actor_kind, 'cuando', e.at) as dato
          from task_state_event e left join app_user u on u.id = e.actor_app_user_id
         where e.task_id = t.id
        union all
        select ap.at, 2,
               jsonb_build_object('que', case ap.decision when 'aprobado' then 'aprobacion'
                                                          else 'pedido_de_cambios' end,
                                  'quien', u.nombre, 'comentario', ap.comentario,
                                  'cuando', ap.at)
          from approval ap
          join membership m on m.id = ap.aprobador_membership_id
          join app_user u on u.id = m.app_user_id
         where ap.sujeto_tipo = 'tarea' and ap.sujeto_id = t.id
        union all
        select b.abierto_en, 3,
               jsonb_build_object('que', 'bloqueo', 'causa', b.causa, 'quien', u.nombre,
                                  'cuando', b.abierto_en, 'resuelto_en', b.resuelto_en)
          from blocker b
          left join membership m on m.id = b.abierto_por
          left join app_user u on u.id = m.app_user_id
         where b.task_id = t.id
        union all
        select f.at, 4,
               jsonb_build_object('que', 'prevision', 'fecha', f.fecha_prevista,
                                  'es_correccion', f.es_correccion, 'quien', u.nombre,
                                  'cuando', f.at)
          from task_forecast f
          join membership m on m.id = f.dicho_por_membership_id
          join app_user u on u.id = m.app_user_id
         where f.task_id = t.id
        union all
        select u.at, 5,
               jsonb_build_object('que', 'quien_destraba', 'quien', pu.nombre,
                                  'destraba', coalesce(du.nombre, u.destraba_externo),
                                  'no_sabe', u.no_sabe,
                                  'nadie_mas', u.destraba_membership_id
                                               = u.dicho_por_membership_id,
                                  'cuando', u.at)
          from blocker_unblocker u
          join blocker b on b.id = u.blocker_id
          join membership pm on pm.id = u.dicho_por_membership_id
          join app_user pu on pu.id = pm.app_user_id
          left join membership dm on dm.id = u.destraba_membership_id
          left join app_user du on du.id = dm.app_user_id
         where b.task_id = t.id
           and not u.sin_decir_quien
        union all
        select d.at, 6,
               jsonb_build_object('que', 'dicho_del_bloqueo', 'quien', pu.nombre,
                                  'para_cuando', d.para_cuando, 'ya_esta', d.ya_esta,
                                  'no_le_corresponde', d.no_le_corresponde,
                                  'lo_que_dice', d.lo_que_dice, 'cuando', d.at)
          from dicho_de_quien_destraba d
          join blocker_unblocker u on u.id = d.blocker_unblocker_id
          join blocker b on b.id = u.blocker_id
          join membership pm on pm.id = d.dicho_por_membership_id
          join app_user pu on pu.id = pm.app_user_id
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
               'ejemplo_aceptado', e.es_ejemplo_aceptado, 'quien', u.nombre, 'cuando', e.at,
               'retirada', r.retirada, 'retirada_el', r.retirada_el,
               'retirada_por_la_administracion', r.por_la_administracion)
             order by e.at, e.id)
        from evidence e
        left join archivo a on a.workspace_id = e.workspace_id and a.id = e.archivo_id
        left join membership m on m.id = e.entregado_por
        left join app_user u on u.id = m.app_user_id
        -- Retirada por quien la entregó, o su contenido por la administración: la pieza o
        -- cualquier otra del espacio con el mismo archivo (un archivo se guarda una vez por
        -- huella). De una pieza retirada no sale su contenido (ADR 0019, decisión 3).
        cross join lateral (
          select adm.at is not null or per.at is not null as retirada,
                 coalesce(adm.at, per.at) as retirada_el,
                 adm.at is not null as por_la_administracion
            from (select min(x.at) as at from evidencia_retirada x
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

create or replace function leer_archivo_de_tarea(p_token_hash text, p_evidence_id uuid)
returns table (archivo_contenido bytea, archivo_tipo text, archivo_clase text,
               archivo_nombre text)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        acceso acceso_tarea%rowtype;
        v_contenido bytea;
        v_tipo text;
        v_clase text;
        v_nombre text;
begin
  acceso := acceso_tarea_vigente(p_token_hash);
  if acceso.id is not null then
    select a.contenido, a.tipo, a.clase, a.nombre_original
      into v_contenido, v_tipo, v_clase, v_nombre
      from evidence e
      join archivo a on a.workspace_id = e.workspace_id and a.id = e.archivo_id
     where e.id = p_evidence_id
       and e.workspace_id = acceso.workspace_id
       and e.task_id = acceso.task_id
       and not exists (select 1 from evidencia_retirada x where x.evidence_id = e.id)
       -- Un archivo cuyo contenido retiró la administración no se sirve por ninguna pieza.
       and not exists (select 1 from evidencia_retirada x
                         join evidence o on o.id = x.evidence_id
                        where x.retirada_por_app_user_id is not null
                          and o.workspace_id = e.workspace_id
                          and o.archivo_id = e.archivo_id);
    if v_contenido is not null then
      insert into vista_de_tarea (workspace_id, acceso_tarea_id, que, evidence_id)
           values (acceso.workspace_id, acceso.id, 'archivo', p_evidence_id);
    -- La vista de un administrador de plataforma va además a la auditoría (ADR 0019, 7b y 7e;
    -- constitución §12), con la versión del pack del espacio; la del núcleo la pasa quien llama.
    if acceso.admin_app_user_id is not null then
      insert into audit_log (workspace_id, actor_app_user_id, actor_kind, accion, sujeto_tipo,
                             sujeto_id, detalle, pack_hash, nucleo_hash)
      values (acceso.workspace_id, acceso.admin_app_user_id, 'persona', 'bajar_archivo_de_tarea',
              'evidence', p_evidence_id, jsonb_build_object('acceso_tarea_id', acceso.id, 'task_id', acceso.task_id),
              (select v.pack_hash from workspace_version v
                where v.workspace_id = acceso.workspace_id order by v.version desc limit 1),
              nullif(current_setting('leda.nucleo_hash', true), ''));
    end if;
    end if;
  end if;
  perform set_config('leda.workspace_id', previo, true);
  if v_contenido is not null then
    return query select v_contenido, v_tipo, v_clase, v_nombre;
  end if;
end $$;

alter function acceso_tarea_vigente(text) owner to leda_owner;
alter function leer_pagina_de_tarea(text) owner to leda_owner;
alter function leer_archivo_de_tarea(text, uuid) owner to leda_owner;

commit;
