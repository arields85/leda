\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0058_quien_ve_que_en_las_listas.sql. La cadena de esperas de una tarea trabada
-- en las listas de la puerta del equipo (ADR 0022, decisiones 3, 11, 13 y 18; porción 1, tarea
-- P1-3 de `odd/tasks/plataforma-p1.md`).
--
-- - `esperas_que_ve(persona, vista, ahora)`: para cada tarea de la vista cuyo bloqueo abierto ve
--   esa persona (`tareas_que_ve` lo devuelve en `bloqueo_abierto`; nulo para quien no ve los
--   atrasos de la tarea, y entonces no hay cadena), el árbol de lo que espera, hacia abajo, con
--   las mismas esperas que lee la 0058 (y el motor, `encadenados.py`):
--   - otra tarea abierta: una dependencia bloqueante, o el bloqueo suyo con el que dijo estar
--     trabado quien destraba (`dicho_de_quien_destraba.espera_su_bloqueo_id`, 0044). El paso es
--     el título de esa tarea y quién la tiene, y la cadena sigue desde ella;
--   - un bloqueo abierto que no lleva a ninguna tarea: el paso es su causa y quién lo destraba
--     según lo último que se dijo (un integrante o alguien de afuera; nulo si nadie lo dijo), y
--     ahí termina.
--   Hasta diez pasos de profundidad y sin vueltas (una tarea no se repite en su rama). Una fila
--   por paso: la tarea trabada de la que cuelga (`raiz`), su lugar en el árbol (`ruta`, con la del
--   paso de arriba en `padre`; nulo, el primero), la profundidad, qué espera y de quién. `ruta` es
--   sólo un orden para armar el árbol: no lleva identificadores que la web tenga que mostrar.
--   `language sql` sin elevar, como `tareas_que_ve`: `leda_app` no la ejecuta.
-- - `esperas_de_la_sesion(token, vista, ahora)`: lo que llama la web, con el patrón de
--   `tareas_de_la_sesion` (0058): `security definer` con dueño `leda_owner`, que no saltea la RLS;
--   la persona sale del hash del token de la sesión por `sesion_vigente` (0057), nunca de un dato
--   del pedido (decisión 11). Una sesión que no entra no ve nada.
--
-- No crea, altera ni borra roles ni tablas. Se deshace con
-- `db/rollbacks/0059_la_cadena_de_esperas.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0059 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0058 está aplicada y la 0059 no.
do $$ begin
  if to_regprocedure('leda.tareas_que_ve(uuid, text, timestamptz)') is null then
    raise exception '0059 preflight failed: falta la 0058';
  end if;
  if to_regprocedure('leda.esperas_que_ve(uuid, text, timestamptz)') is not null then
    raise exception '0059 ya está aplicada.';
  end if;
end $$;

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
           d.origen_task_id as siguiente, o.titulo as que, u.nombre as quien
      from dependency d
      join abiertas o on o.id = d.origen_task_id
      left join membership m on m.id = o.responsable_membership_id
      left join app_user u on u.id = m.app_user_id
     where d.tipo = 'bloqueante'
    union
    select p.task_id, 't' || p.esperada::text, p.esperada, o.titulo, u.nombre
      from por_lo_dicho p
      join abiertas o on o.id = p.esperada
      left join membership m on m.id = o.responsable_membership_id
      left join app_user u on u.id = m.app_user_id
    union
    select b.task_id, 'b' || b.id::text, null::uuid, b.causa,
           coalesce(u.nombre, b.destraba_externo)
      from bloqueos b
      left join membership m on m.id = b.destraba_membership_id
      left join app_user u on u.id = m.app_user_id
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

create or replace function esperas_de_la_sesion(
    p_token_hash text, p_vista text, p_ahora timestamptz)
returns table (raiz uuid, ruta text, padre text, nivel integer, que text, quien text)
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare persona uuid;
begin
  if p_vista is null or p_vista not in ('tus', 'sector', 'equipo') then
    raise exception 'esperas_de_la_sesion: vista desconocida';
  end if;
  -- La persona sale de la sesión, que deja fijado su espacio; si no entra, nada.
  select s.membership_id into persona from sesion_vigente(p_token_hash) s;
  if persona is null then
    return;
  end if;
  return query select q.* from esperas_que_ve(persona, p_vista, p_ahora) q;
end $$;

alter function esperas_que_ve(uuid, text, timestamptz) owner to leda_owner;
alter function esperas_de_la_sesion(text, text, timestamptz) owner to leda_owner;

revoke execute on function esperas_que_ve(uuid, text, timestamptz) from public;
revoke execute on function esperas_de_la_sesion(text, text, timestamptz) from public;
grant execute on function esperas_de_la_sesion(text, text, timestamptz) to leda_app;

commit;
