\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0059_la_cadena_de_esperas.sql. Lo que la puerta del equipo muestra de una tarea
-- ajena, las terminadas de los últimos 30 días y el bot del equipo (decisiones del usuario del
-- 2026-10-12, 1 a 8; porción 1, tarea P1-6 de `odd/tasks/plataforma-p1.md`). Criterio común del
-- usuario: la web informa lo mismo que el informe al grupo (`motor/informe_al_grupo.py`).
--
-- - `tareas_que_ve(persona, vista, ahora)` (0058) cambia en dos cosas, y suma una columna:
--   - `bloqueo_abierto` llega para toda tarea de la lista: quien espera una tarea ajena, o quien
--     la destraba, ve que está trabada (decisión 7), como el grupo la ve en el informe. Con eso,
--     la cadena de esperas de la 0059, que cuelga de las tareas cuyo bloqueo ve la persona, se
--     ve también en las ajenas (decisión 6).
--   - `vencida`, para quien ve los atrasos de la tarea (su responsable, el referente de su área,
--     la autoridad final), como hasta ahora: ya pasó su fecha. Para cualquier otro, recién
--     cuando el atraso ya se habló en privado con quien la tiene (constitución §8; informe al
--     grupo, `_sin_entregar`), y ya pasó su fecha:
--     a. su previsión vigente (`task_forecast` que ninguna otra reemplaza, la última; como
--        `ancla.prevision_vigente`) es posterior al día en que vence; o
--     b. salió el escalamiento por falta de respuesta de ese vencimiento (`scheduled_notice`
--        `escalamiento`, `enviado`, con `hechos.vence` ese día; como
--        `informe_al_grupo._quedo_asentado_el_atraso`).
--     Si no, la fecha sola (decisión 1). Sólo para una tarea que sigue (asignada, en curso o
--     trabada): una entregada ya no es un atraso que siga. Trabada y vencida a la vez lleva las
--     dos marcas (decisión 5): las dos columnas son independientes.
--   - `prevision` (nueva): la previsión vigente de una tarea que sigue, cuando es posterior al
--     día en que vence (la regla a); si no, nula. La ve quien ve la tarea en la lista.
-- - `terminadas_que_ve(persona, vista, ahora)`: las terminadas de los últimos 30 días, cada vista
--   en su alcance ("tus": las suyas; "sector": las de sus áreas; "equipo": todas), con quién la
--   hizo (decisión 3); las canceladas, no. Cuándo se terminó: el evento que la terminó, como lo
--   proyecta la tarea (su última actualización, si no hay evento). `language sql` sin elevar:
--   `leda_app` no la ejecuta.
-- - `tareas_de_la_sesion` (0058) cambia sólo por la columna nueva, y `terminadas_de_la_sesion`
--   sigue su patrón: `security definer` con dueño `leda_owner`, que no saltea la RLS; la persona
--   sale del hash del token de la sesión por `sesion_vigente` (0057), nunca de un dato del pedido
--   (ADR 0022, decisión 11). Una sesión que no entra no ve nada.
-- - `workspace_setting` admite `bot_usuario`, el usuario público del bot del equipo (sin "@"),
--   que el pack declara en `telegram.bot_usuario` y la web usa para abrir el chat con Leda
--   (decisión 8): sólo un usuario de Telegram válido (5 a 32 letras, números o "_", empezando
--   con una letra), porque va en una dirección.
--
-- Esperar una tarea sigue sin abrir su página (decisión 2): `puede_ver_tarea` no cambia.
-- No crea, altera ni borra roles ni tablas. Se deshace con
-- `db/rollbacks/0060_lo_ajeno_como_el_informe_al_grupo.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0060 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0059 está aplicada y la 0060 no; ningún ajuste guardado rompe la restricción.
do $$ begin
  if to_regprocedure('leda.esperas_que_ve(uuid, text, timestamptz)') is null then
    raise exception '0060 preflight failed: falta la 0059';
  end if;
  if to_regprocedure('leda.terminadas_que_ve(uuid, text, timestamptz)') is not null then
    raise exception '0060 ya está aplicada.';
  end if;
  if exists (select 1 from workspace_setting where clave = 'bot_usuario') then
    raise exception '0060 preflight failed: ya hay un ajuste bot_usuario';
  end if;
end $$;

-- La columna nueva cambia lo que devuelven: se borran y se vuelven a crear. La 0059 llama a
-- `tareas_que_ve` por su nombre, sin depender de ella en el catálogo.
drop function tareas_de_la_sesion(text, text, timestamptz);
drop function tareas_que_ve(uuid, text, timestamptz);

create function tareas_que_ve(
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
         u.nombre, f.area_nombre, f.papel,
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
    left join app_user u on u.id = rm.app_user_id
   where case p_vista
           when 'tus' then f.papel is not null
           when 'sector' then f.referente_membership_id = f.yo_id
           when 'equipo' then f.es_autoridad
           else false
         end
   order by f.fecha_objetivo nulls last, f.titulo, f.id;
$$;

create function tareas_de_la_sesion(
    p_token_hash text, p_vista text, p_ahora timestamptz)
returns table (task_id uuid, titulo text, estado text, fecha_objetivo timestamptz,
               asignada_en timestamptz, responsable text, area text, papel text,
               vencida boolean, bloqueo_abierto boolean, ve_la_pagina boolean,
               prevision date)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare persona uuid;
begin
  if p_vista is null or p_vista not in ('tus', 'sector', 'equipo') then
    raise exception 'tareas_de_la_sesion: vista desconocida';
  end if;
  -- La persona sale de la sesión, que deja fijado su espacio; si no entra, nada.
  select s.membership_id into persona from sesion_vigente(p_token_hash) s;
  if persona is null then
    return;
  end if;
  return query select q.* from tareas_que_ve(persona, p_vista, p_ahora) q;
end $$;

create function terminadas_que_ve(
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
  select x.id, x.titulo, u.nombre, a.nombre, x.terminada_en
    from terminadas x
    cross join yo
    join area a on a.id = x.area_id
    left join membership rm on rm.id = x.responsable_membership_id
    left join app_user u on u.id = rm.app_user_id
   where x.terminada_en >= coalesce(p_ahora, now()) - interval '30 days'
     and case p_vista
           when 'tus' then x.responsable_membership_id = yo.id
           when 'sector' then a.referente_membership_id = yo.id
           when 'equipo' then yo.autoridad_final
           else false
         end
   order by x.terminada_en desc, x.titulo, x.id;
$$;

create function terminadas_de_la_sesion(
    p_token_hash text, p_vista text, p_ahora timestamptz)
returns table (task_id uuid, titulo text, responsable text, area text,
               terminada_en timestamptz)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare persona uuid;
begin
  if p_vista is null or p_vista not in ('tus', 'sector', 'equipo') then
    raise exception 'terminadas_de_la_sesion: vista desconocida';
  end if;
  -- La persona sale de la sesión, que deja fijado su espacio; si no entra, nada.
  select s.membership_id into persona from sesion_vigente(p_token_hash) s;
  if persona is null then
    return;
  end if;
  return query select q.* from terminadas_que_ve(persona, p_vista, p_ahora) q;
end $$;

alter function tareas_que_ve(uuid, text, timestamptz) owner to leda_owner;
alter function tareas_de_la_sesion(text, text, timestamptz) owner to leda_owner;
alter function terminadas_que_ve(uuid, text, timestamptz) owner to leda_owner;
alter function terminadas_de_la_sesion(text, text, timestamptz) owner to leda_owner;

revoke execute on function tareas_que_ve(uuid, text, timestamptz) from public;
revoke execute on function tareas_de_la_sesion(text, text, timestamptz) from public;
revoke execute on function terminadas_que_ve(uuid, text, timestamptz) from public;
revoke execute on function terminadas_de_la_sesion(text, text, timestamptz) from public;
grant execute on function tareas_de_la_sesion(text, text, timestamptz) to leda_app;
grant execute on function terminadas_de_la_sesion(text, text, timestamptz) to leda_app;

-- El usuario público del bot del equipo: va en una dirección (`https://t.me/<usuario>`).
alter table workspace_setting add constraint workspace_setting_bot_usuario check (
  case
    when clave <> 'bot_usuario' then true
    when jsonb_typeof(valor) <> 'string' then false
    else (valor #>> '{}') ~ '^[A-Za-z][A-Za-z0-9_]{4,31}$'
  end);

commit;
