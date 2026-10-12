\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0057_el_enlace_y_la_sesion_de_la_web.sql. Quién ve qué en las listas de la puerta
-- del equipo de la plataforma web (ADR 0022, decisiones 3, 5, 11 y 13; porción 1, tarea P1-2 de
-- `odd/tasks/plataforma-p1.md`).
--
-- - `tareas_que_ve(persona, vista, ahora)`: la regla, una sola y en SQL (decisión 13). Extiende
--   `puede_ver_tarea` (ADR 0019) de una tarea a la lista de cada vista, sólo con las tareas
--   abiertas (ni terminadas ni canceladas):
--   - "tus" (todo integrante): las suyas ("mia"); las de otros que esperan algo suyo
--     ("me_esperan": un bloqueo abierto que destraba, según lo último que se dijo; una tarea suya
--     de la que dependen; una entrega que revisa); y las de otros que espera ("espero": una
--     dependencia bloqueante, o el bloqueo con el que dijo estar trabado quien le destraba la
--     suya, como lo lee el motor).
--   - "sector" (el referente, `area.referente_membership_id`): todas las de sus áreas.
--   - "equipo" (la autoridad final, `rol.autoridad_final`): todas las del espacio.
--   Una fila por tarea, sin cuentas ni orden por persona (constitución §15, principio 14). El
--   atraso (`vencida`) y el bloqueo abierto (`bloqueo_abierto`) sólo los ve quien puede ver los
--   atrasos de esa tarea: su responsable, el referente de su área o la autoridad final; para
--   cualquier otro van nulos (decisión 3: un integrante no ve los atrasos de los demás;
--   constitución §8: los atrasos se tratan primero en privado). `ve_la_pagina` dice si además
--   abre la página de la tarea (`puede_ver_tarea`, que no cambia).
-- - `vistas_de(persona)`: qué vistas tiene: "tus" siempre; "sector" si es referente de un área;
--   "equipo" si es la autoridad final (decisión 5).
-- - Las dos, `language sql` sin elevar: corren con la RLS de quien las llama. `leda_app` no las
--   ejecuta: no elige a la persona. Las llaman las de la sesión.
-- - `tareas_de_la_sesion(token, vista, ahora)` y `vistas_de_la_sesion(token)`: lo que llama la
--   web. `security definer` con dueño `leda_owner`, que no saltea la RLS. La persona sale del
--   hash del token de la sesión por `sesion_vigente` (0057), que revalida la membresía, anota el
--   último uso y deja fijado el espacio de la sesión; nunca de un dato del pedido (decisión 11).
--   Una sesión que no entra no ve nada. `ahora` es el reloj de Leda, que la API lee (puede ir
--   adelantado en una prueba); nulo, la hora de la base.
--
-- No crea, altera ni borra roles ni tablas. Se deshace con
-- `db/rollbacks/0058_quien_ve_que_en_las_listas.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0058 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0057 está aplicada y la 0058 no.
do $$ begin
  if to_regclass('leda.sesion_web') is null then
    raise exception '0058 preflight failed: falta la 0057';
  end if;
  if to_regprocedure('leda.tareas_que_ve(uuid, text, timestamptz)') is not null then
    raise exception '0058 ya está aplicada.';
  end if;
end $$;

create or replace function tareas_que_ve(
    p_membership_id uuid, p_vista text, p_ahora timestamptz)
returns table (task_id uuid, titulo text, estado text, fecha_objetivo timestamptz,
               asignada_en timestamptz, responsable text, area text, papel text,
               vencida boolean, bloqueo_abierto boolean, ve_la_pagina boolean)
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
         case when f.ve_atrasos then
           coalesce(f.estado in ('asignada', 'en_curso', 'bloqueada')
                    and (f.fecha_objetivo at time zone w.zona_horaria)::date
                        < (coalesce(p_ahora, now()) at time zone w.zona_horaria)::date,
                    false)
         end,
         case when f.ve_atrasos then
           exists (select 1 from blocker b where b.task_id = f.id and b.resuelto_en is null)
         end,
         puede_ver_tarea(f.yo_id, f.id)
    from filas f
    join workspace w on w.id = f.workspace_id
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

create or replace function vistas_de(p_membership_id uuid)
returns text[]
language sql stable set search_path = leda, public, pg_temp as $$
  select array['tus']
         || case when exists (select 1 from area a where a.referente_membership_id = m.id)
                 then array['sector'] else array[]::text[] end
         || case when r.autoridad_final then array['equipo'] else array[]::text[] end
    from membership m
    join rol r on r.id = m.rol_id
   where m.id = p_membership_id and m.activo;
$$;

create or replace function tareas_de_la_sesion(
    p_token_hash text, p_vista text, p_ahora timestamptz)
returns table (task_id uuid, titulo text, estado text, fecha_objetivo timestamptz,
               asignada_en timestamptz, responsable text, area text, papel text,
               vencida boolean, bloqueo_abierto boolean, ve_la_pagina boolean)
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

create or replace function vistas_de_la_sesion(p_token_hash text)
returns table (membership_id uuid, vistas text[])
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare persona uuid;
begin
  select s.membership_id into persona from sesion_vigente(p_token_hash) s;
  if persona is null then
    return;
  end if;
  return query select persona, vistas_de(persona);
end $$;

alter function tareas_que_ve(uuid, text, timestamptz) owner to leda_owner;
alter function vistas_de(uuid) owner to leda_owner;
alter function tareas_de_la_sesion(text, text, timestamptz) owner to leda_owner;
alter function vistas_de_la_sesion(text) owner to leda_owner;

revoke execute on function tareas_que_ve(uuid, text, timestamptz) from public;
revoke execute on function vistas_de(uuid) from public;
revoke execute on function tareas_de_la_sesion(text, text, timestamptz) from public;
revoke execute on function vistas_de_la_sesion(text) from public;
grant execute on function tareas_de_la_sesion(text, text, timestamptz) to leda_app;
grant execute on function vistas_de_la_sesion(text) to leda_app;

commit;
