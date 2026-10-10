\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0052_el_acceso_del_administrador.sql. Lo que retira la administración se borra
-- de verdad (decisiones 57 a 59 del usuario, 2026-10-10; porción 5b de la C-3;
-- `odd/tasks/fase-c.md`).
--
-- 1. `archivo.contenido` puede quedar vacío, sólo con la hora del retiro
--    (`contenido_retirado_en`): uno de los dos, siempre. La fila queda con su huella, su tamaño,
--    su tipo y quién lo mandó, para reconocerlo si alguien lo vuelve a mandar y para la
--    auditoría. Los archivos que la administración ya había retirado (0052) se vacían acá.
-- 2. `rechazar_cambios_de_archivo`: la única excepción a que un archivo guardado no cambia.
--    Sólo la conexión administrativa (`leda_admin`), sólo para vaciar el contenido de un
--    archivo que la administración retiró (hay un retiro suyo de una pieza con ese archivo), y
--    nada más: ni la huella ni ninguna otra columna, ni volver a poner un contenido, ni borrar
--    la fila. No tiene vuelta atrás.
-- 3. `archivo_de_mensaje.rechazo`: `contenido_retirado`, lo que llega con la huella de un
--    archivo cuyo contenido retiró la administración (no se guarda otra vez).
-- 4. `leer_pagina_de_tarea`: de un retiro de la administración, también el motivo
--    (`motivo_del_retiro`), nunca quién lo hizo (decisión 59).
--
-- Aislamiento: sin tablas nuevas ni privilegios nuevos; `leda_app` sigue sin poder cambiar ni
-- borrar un archivo. La función de la página sigue siendo de `leda_owner`.
--
-- Se deshace con `db/rollbacks/0053_lo_que_retira_la_administracion.sql`, que se niega si ya se
-- borró algún contenido: el borrado no tiene vuelta atrás.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0053 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0052 está aplicada y la 0053 no.
do $$ begin
  if not exists (select 1 from information_schema.columns
                  where table_schema = 'leda' and table_name = 'evidencia_retirada'
                    and column_name = 'retirada_por_app_user_id') then
    raise exception '0053 preflight failed: falta la 0052';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'archivo'
                and column_name = 'contenido_retirado_en') then
    raise exception '0053 ya está aplicada.';
  end if;
end $$;

-- 1. El contenido o la hora en que se retiró.
alter table archivo add column contenido_retirado_en timestamptz;
alter table archivo alter column contenido drop not null;
alter table archivo drop constraint archivo_huella_del_contenido;
alter table archivo add constraint archivo_huella_del_contenido
  check (contenido is null or sha256 = encode(sha256(contenido), 'hex'));
alter table archivo drop constraint archivo_tamano_del_contenido;
alter table archivo add constraint archivo_tamano_del_contenido
  check (tamano between 1 and 62914560
         and (contenido is null or tamano = octet_length(contenido)));
alter table archivo add constraint archivo_contenido_o_su_retiro
  check ((contenido is null) = (contenido_retirado_en is not null));
comment on column archivo.contenido_retirado_en is
  'Decisión 57 del usuario (porción 5b; migración 0053): cuándo la administración borró el contenido de este archivo al retirarlo. Desde entonces `contenido` es nulo y la fila guarda la huella, para reconocerlo si alguien lo vuelve a mandar. No tiene vuelta atrás.';

-- Lo que la administración ya había retirado con la 0052 se borra ahora, con la hora de su
-- primer retiro.
alter table archivo disable trigger trg_rechazar_cambios_de_archivo;
update archivo a
   set contenido = null,
       contenido_retirado_en = (select min(x.at) from evidencia_retirada x
                                  join evidence e on e.id = x.evidence_id
                                 where x.retirada_por_app_user_id is not null
                                   and e.workspace_id = a.workspace_id
                                   and e.archivo_id = a.id)
 where exists (select 1 from evidencia_retirada x
                 join evidence e on e.id = x.evidence_id
                where x.retirada_por_app_user_id is not null
                  and e.workspace_id = a.workspace_id and e.archivo_id = a.id);
alter table archivo enable trigger trg_rechazar_cambios_de_archivo;

-- 2. La única excepción a que un archivo no cambia.
-- Un archivo recibido no se modifica ni se borra (ADR 0019, decisión 3). Es una garantía aparte
-- de los privilegios de `leda_app`: vale también para la conexión administrativa. La única
-- excepción (decisión 57; migración 0053): la conexión administrativa vacía el contenido de un
-- archivo que la administración retiró (`evidencia_retirada.retirada_por_app_user_id` de una
-- pieza con ese archivo) y anota cuándo; nada más cambia, y no se vuelve atrás. Las columnas se
-- comparan una por una para no copiar el contenido entero.
create or replace function rechazar_cambios_de_archivo() returns trigger as $$
begin
  if tg_op = 'UPDATE' and current_user = 'leda_admin'
     and old.contenido is not null and new.contenido is null
     and new.contenido_retirado_en is not null
     and (new.id, new.workspace_id, new.sha256, new.tamano, new.tipo, new.clase,
          new.nombre_original, new.enviado_por_membership_id, new.recibido_en)
         is not distinct from
         (old.id, old.workspace_id, old.sha256, old.tamano, old.tipo, old.clase,
          old.nombre_original, old.enviado_por_membership_id, old.recibido_en)
     and exists (select 1 from evidencia_retirada x
                   join evidence e on e.id = x.evidence_id
                  where x.retirada_por_app_user_id is not null
                    and e.workspace_id = old.workspace_id and e.archivo_id = old.id) then
    return new;
  end if;
  raise exception 'archivo: un archivo recibido no se modifica ni se borra (sólo la administración vacía el contenido de uno que retiró)';
end $$ language plpgsql;

-- 3. Lo que llega con la huella de un contenido retirado.
alter table archivo_de_mensaje drop constraint archivo_de_mensaje_rechazo;
alter table archivo_de_mensaje add constraint archivo_de_mensaje_rechazo check (
  rechazo in ('demasiado_grande', 'tipo_no_admitido', 'contenido_retirado'));

-- 4. La página: el motivo de un retiro de la administración.
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
               'retirada_por_la_administracion', r.por_la_administracion,
               'motivo_del_retiro', r.motivo_de_la_administracion)
             order by e.at, e.id)
        from evidence e
        left join archivo a on a.workspace_id = e.workspace_id and a.id = e.archivo_id
        left join membership m on m.id = e.entregado_por
        left join app_user u on u.id = m.app_user_id
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
alter function leer_pagina_de_tarea(text) owner to leda_owner;

commit;
