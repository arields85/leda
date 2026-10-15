\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0081_el_equipo_cuadra.sql. Ver el equipo (J7-3 de
-- `odd/tasks/plataforma-jerarquias.md`; ADR 0023, decisiones 4 y 5): la vista "Equipo" de la web,
-- por las dos puertas, sin cambiar nada todavía.
--
-- - `quien_organiza_el_equipo`: la puerta de las funciones de la J7 (Dirección en su espacio, el
--   administrador de plataforma en cualquiera). No es elevada ni la ejecuta `leda_app`.
-- - `equipo_de` y `cambios_del_equipo`: lo que la vista muestra y la historia de los cambios del
--   equipo. `security definer` de `leda_owner`, con el camino fijado, sólo para `leda_app`;
--   comprueban la sesión en cada llamada y fijan ellas mismas el espacio.
--
-- Sólo funciones: no toca tablas ni datos. Se deshace con
-- `db/rollbacks/0082_ver_el_equipo.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0082 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0081 está aplicada y la 0082 no.
do $$ begin
  if to_regprocedure('leda.problemas_del_equipo(uuid)') is null then
    raise exception '0082 preflight failed: falta la 0081';
  end if;
  if to_regprocedure('leda.equipo_de(text, text, uuid)') is not null then
    raise exception '0082 ya está aplicada.';
  end if;
end $$;

-- Ver el equipo (migración 0082; J7-3; ADR 0023, decisiones 4 y 5): quién organiza el equipo de un
-- espacio y lo que ve de él. Nada cambia el equipo todavía.
-- - `quien_organiza_el_equipo`: la puerta de todas las funciones de la J7, con la regla de
--   `quien_crea_el_objetivo` (la de administración, en cualquier espacio; la del equipo, sólo
--   Dirección, en el suyo). No es elevada: la llaman funciones que ya corren como `leda_owner`.
-- - `equipo_de`: las áreas (su referente, si declararon la autoaprobación, su gente, cuántas
--   tareas abiertas tienen y si están archivadas), las personas (área, rol, quién las aprueba, si
--   siguen en el equipo y si conectaron Leda), los roles y los problemas del equipo
--   (`problemas_del_equipo`).
-- - `cambios_del_equipo`: la historia de `cambio_del_equipo` del espacio, lo más nuevo primero.
create or replace function quien_organiza_el_equipo(
    p_puerta text, p_token_hash text, p_workspace_id uuid)
returns jsonb
language plpgsql set search_path = leda, public, pg_temp as $$
begin
  -- Organiza el equipo quien tiene la autoridad final (ADR 0023, decisión 4) y el administrador de
  -- plataforma, en cualquier espacio (decisión 5): las mismas puertas que crear un objetivo.
  return quien_crea_el_objetivo(p_puerta, p_token_hash, p_workspace_id);
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
                                                         'nombre', ur.nombre,
                                                         'activo', r.activo) end,
               'autoaprobacion', exists (
                 select 1 from approval_policy p
                  where p.workspace_id = v_espacio and p.area_id = a.id
                    and p.autoaprobacion_declarada),
               'personas', coalesce((
                 select jsonb_agg(m.id order by u.nombre, m.id)
                   from membership m join app_user u on u.id = m.app_user_id
                  where m.workspace_id = v_espacio and m.area_id = a.id and m.activo),
                 '[]'::jsonb),
               'tareas_abiertas', (
                 select count(*) from task t
                  where t.workspace_id = v_espacio and t.area_id = a.id
                    and t.estado not in ('terminada', 'cancelada')))
             order by a.archivada_en is not null, a.nombre, a.id)
        from area a
        left join membership r on r.id = a.referente_membership_id
        left join app_user ur on ur.id = r.app_user_id
       where a.workspace_id = v_espacio), '[]'::jsonb),
    -- Las personas: las que siguen en el equipo primero. «Sin conectar» es quien todavía no
    -- activó su enlace (`onboarding.pendientes_de_activar`): sin cuenta de Telegram.
    'personas', coalesce((
      select jsonb_agg(jsonb_build_object(
               'membership_id', m.id, 'nombre', u.nombre, 'activo', m.activo,
               'conectado', u.telegram_user_id is not null,
               'area_id', m.area_id, 'area', a.nombre,
               'rol_id', m.rol_id, 'rol', r.nombre, 'autoridad_final', r.autoridad_final,
               'aprobador', case when ap.id is null then null
                                 else jsonb_build_object('membership_id', ap.id,
                                                         'nombre', ua.nombre,
                                                         'activo', ap.activo) end,
               'referente_de', coalesce((
                 select jsonb_agg(x.nombre order by x.nombre, x.id)
                   from area x
                  where x.workspace_id = v_espacio and x.referente_membership_id = m.id
                    and x.archivada_en is null), '[]'::jsonb))
             order by not m.activo, u.nombre, m.id)
        from membership m
        join app_user u on u.id = m.app_user_id
        join area a on a.id = m.area_id
        join rol r on r.id = m.rol_id
        left join membership ap on ap.id = m.aprobador_membership_id
        left join app_user ua on ua.id = ap.app_user_id
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
               'id', c.id, 'clase', c.clase, 'puerta', c.puerta, 'quien', u.nombre,
               'at', c.at, 'antes', c.antes, 'despues', c.despues)
             order by c.at desc, c.id)
        from cambio_del_equipo c
        join app_user u on u.id = c.hecho_por_app_user_id
       where c.workspace_id = v_espacio), '[]'::jsonb));
  perform set_config('leda.workspace_id', previo, true);
  return v_resultado;
end $$;

comment on function equipo_de(text, text, uuid) is
  'J7-3 (migración 0082; ADR 0023, decisiones 4 y 5): el equipo del espacio para la vista "Equipo" de la web: áreas, personas, roles y problemas. Sólo Dirección, por la puerta del equipo, y el administrador de plataforma, por la suya.';
comment on function cambios_del_equipo(text, text, uuid) is
  'J7-3 (migración 0082): la historia de cambio_del_equipo del espacio, lo más nuevo primero, para quienes organizan el equipo.';

alter function quien_organiza_el_equipo(text, text, uuid) owner to leda_owner;
alter function equipo_de(text, text, uuid) owner to leda_owner;
alter function cambios_del_equipo(text, text, uuid) owner to leda_owner;
revoke execute on function quien_organiza_el_equipo(text, text, uuid) from public;
revoke execute on function equipo_de(text, text, uuid) from public;
revoke execute on function cambios_del_equipo(text, text, uuid) from public;
grant execute on function equipo_de(text, text, uuid) to leda_app;
grant execute on function cambios_del_equipo(text, text, uuid) to leda_app;

commit;
