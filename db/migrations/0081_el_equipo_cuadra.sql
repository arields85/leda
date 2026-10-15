\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0080_el_grafo_en_una_sola_sentencia.sql. El equipo cuadra (J7-1 de
-- `odd/tasks/plataforma-jerarquias.md`; ADR 0023, decisión 4; mecánica §7): la base de las
-- jerarquías y los integrantes desde la web de Dirección.
--
-- - `problemas_del_equipo(uuid)`: las reglas del equipo de `importador.validar`, sobre las tablas
--   vivas. Una sola persona activa con la autoridad final; cada otra persona activa, con un
--   aprobador activo; sin vueltas en la cadena de quién aprueba a quién (ni nadie que se apruebe
--   a sí mismo); cada área sin archivar, con un referente activo, la autoaprobación declarada o
--   sin referente (la decide Dirección, J6-D6); y nadie activo en un área archivada. Devuelve la
--   lista de problemas, cada uno con su código y en palabras de todos los días; vacía, el equipo
--   cuadra. Las reglas no se pueden exigir en las tablas (las pruebas y el importador pasan por
--   estados intermedios): cada función de la J7 la vuelve a correr dentro de su transacción.
-- - `area.archivada_en`: un área nunca se borra, se archiva (las tareas cerradas la siguen
--   nombrando).
-- - `cambio_del_equipo`: cada cambio del equipo, con el antes y el después, quién lo hizo y por qué
--   puerta, su clave de un solo uso y la huella de la vista previa. Sólo se agrega (nadie la edita
--   ni la borra, tampoco la administración); la escriben las funciones de la J7, no `leda_app`.
-- - `leda_app` deja de escribir `area`, `rol`, `membership`, `approval_policy` y
--   `escalation_route`: el equipo lo escriben el importador (`leda_admin`) y las funciones de la
--   J7. De `membership` le queda `update` sólo sobre `workspace_id`, que la política del espacio
--   no deja cambiar: es lo que pide `select ... for share`, con el que el despachador lee a la
--   persona y a quien la aprueba (`despachador._preview_vigente`).
--
-- Se deshace con `db/rollbacks/0081_el_equipo_cuadra.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0081 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0080 está aplicada y la 0081 no.
do $$ begin
  if not exists (select 1 from information_schema.columns
                  where table_schema = 'leda' and table_name = 'task_state_event'
                    and column_name = 'numero') then
    raise exception '0081 preflight failed: falta la 0080';
  end if;
  if to_regclass('leda.cambio_del_equipo') is not null then
    raise exception '0081 ya está aplicada.';
  end if;
end $$;

-- Un área se archiva, no se borra (migración 0081; J7-1).
alter table area add column archivada_en timestamptz;

comment on column area.archivada_en is
  'J7-1 (migración 0081): cuándo se archivó el área. Un área nunca se borra (las tareas cerradas la siguen nombrando); archivada, no cuenta para las reglas del equipo y nadie activo queda en ella.';

-- Cada cambio del equipo (migración 0081; J7-1), con el molde de `carga_de_tarea` y
-- `cambio_de_fecha`: sólo se agrega. Dice qué clase de cambio fue, por qué puerta entró (la web del
-- equipo, Dirección; o la de administración, el administrador de plataforma, que no es miembro
-- del espacio), quién lo hizo, el antes y el después, la clave de un solo uso del pedido y la
-- huella de la vista previa que se confirmó.
create table cambio_del_equipo (
  id                       uuid primary key default gen_random_uuid(),
  workspace_id             uuid not null references workspace(id) on delete cascade,
  clase                    text not null,
  puerta                   text not null,
  hecho_por_app_user_id    uuid not null references app_user(id),
  hecho_por_membership_id  uuid,
  antes                    jsonb,
  despues                  jsonb,
  clave                    text not null,
  huella                   text not null,
  at                       timestamptz not null,
  constraint cambio_del_equipo_clave_unica unique (workspace_id, clave),
  constraint cambio_del_equipo_clave check (clave ~ '^[A-Za-z0-9_-]{16,128}$'),
  constraint cambio_del_equipo_huella check (huella ~ '^[0-9a-f]{64}$'),
  constraint cambio_del_equipo_clase check (clase in (
    'alta', 'baja', 'reactivacion', 'cambio_de_area', 'cambio_de_rol', 'cambio_de_aprobador',
    'nombrar_referente', 'pase_de_autoridad_final', 'area_creada', 'area_renombrada',
    'area_archivada')),
  constraint cambio_del_equipo_puerta check (puerta in ('equipo', 'administracion')),
  constraint cambio_del_equipo_quien
    check ((puerta = 'equipo') = (hecho_por_membership_id is not null)),
  constraint cambio_del_equipo_algo check (antes is not null or despues is not null),
  constraint cambio_del_equipo_hecho_por
    foreign key (workspace_id, hecho_por_membership_id) references membership(workspace_id, id)
);

create index cambio_del_equipo_at on cambio_del_equipo (workspace_id, at);

comment on table cambio_del_equipo is
  'J7-1 (migración 0081; ADR 0023, decisión 4): cada cambio del equipo, con el antes y el después, quién lo hizo y por qué puerta, la clave de un solo uso y la huella de la vista previa. Sólo se agrega: nadie la edita ni la borra. La escriben las funciones de la J7; leda_app no tiene privilegios.';

-- Un cambio del equipo no se edita ni se borra (migración 0081), como una evidencia: vale también
-- para la conexión administrativa.
create or replace function rechazar_cambios_del_equipo() returns trigger as $$
begin
  raise exception 'cambio_del_equipo: un cambio del equipo no se modifica ni se borra';
end $$ language plpgsql;

create trigger trg_rechazar_cambios_del_equipo
  before update or delete on cambio_del_equipo
  for each row execute function rechazar_cambios_del_equipo();

-- "Ariel, Martín y Marcos" (migración 0081): los nombres de una lista, para los problemas del
-- equipo.
create or replace function unir_nombres(p_nombres text[]) returns text
language sql immutable set search_path = leda, public, pg_temp as $$
  select case when cardinality(p_nombres) > 1
              then array_to_string(p_nombres[1:cardinality(p_nombres) - 1], ', ')
                   || ' y ' || p_nombres[cardinality(p_nombres)]
              else p_nombres[1] end;
$$;

-- Los problemas del equipo de un espacio (migración 0081; J7-1; ADR 0023, decisión 4; mecánica
-- §7): las reglas de `importador.validar`, sobre las tablas vivas. Una lista de objetos con
-- `codigo`, `mensaje` (en palabras de todos los días) y, según el caso, `membership_id`,
-- `membership_ids` o `area_id`; vacía, el equipo cuadra. Corre con los privilegios de
-- `leda_owner`, que no saltea la RLS, y sólo para el espacio de la transacción: otro espacio se
-- rechaza (no se consulta el equipo de otro cliente pasando su id).
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
  select coalesce(array_agg(u.nombre order by u.nombre), array[]::text[]) into v_finales
    from membership m
    join rol r on r.id = m.rol_id
    join app_user u on u.id = m.app_user_id
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
    select m.id, u.nombre, m.aprobador_membership_id as aprobador, r.autoridad_final,
           coalesce(a.activo, false) as aprobador_activo, ua.nombre as aprobador_nombre
      from membership m
      join rol r on r.id = m.rol_id
      join app_user u on u.id = m.app_user_id
      left join membership a
        on a.id = m.aprobador_membership_id and a.workspace_id = m.workspace_id
      left join app_user ua on ua.id = a.app_user_id
     where m.workspace_id = p_workspace_id and m.activo
     order by u.nombre, m.id
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
        select array_agg(u.nombre order by u.nombre) into v_nombres
          from membership m join app_user u on u.id = m.app_user_id
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
    select a.id, a.nombre, u.nombre as referente
      from area a
      join membership r on r.id = a.referente_membership_id
      join app_user u on u.id = r.app_user_id
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
    select m.id, u.nombre, a.id as area_id, a.nombre as area
      from membership m
      join area a on a.id = m.area_id
      join app_user u on u.id = m.app_user_id
     where m.workspace_id = p_workspace_id and m.activo and a.archivada_en is not null
     order by u.nombre, m.id
  loop
    v_problemas := v_problemas || jsonb_build_array(jsonb_build_object(
      'codigo', 'integrante_en_area_archivada', 'membership_id', v_fila.id,
      'area_id', v_fila.area_id,
      'mensaje', format('%s está en %s, un área archivada.', v_fila.nombre, v_fila.area)));
  end loop;

  return v_problemas;
end $$;

comment on function problemas_del_equipo(uuid) is
  'J7-1 (migración 0081; ADR 0023, decisión 4; mecánica §7): los problemas del equipo del espacio de la transacción, cada uno con su código y en palabras de todos los días; vacía, el equipo cuadra. Cada función de la J7 la vuelve a correr dentro de su transacción y se niega si no está vacía.';

alter function problemas_del_equipo(uuid) owner to leda_owner;
revoke execute on function problemas_del_equipo(uuid) from public;
grant execute on function problemas_del_equipo(uuid) to leda_app, leda_admin;

alter table cambio_del_equipo enable row level security;
alter table cambio_del_equipo force row level security;
create policy aislamiento_espacio on cambio_del_equipo
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
grant all privileges on cambio_del_equipo to leda_owner, leda_admin;
revoke all on cambio_del_equipo from public, leda_app;
-- De la tabla, `leda_owner` (el dueño de las funciones de la J7) sólo lee y agrega.
revoke all on cambio_del_equipo from leda_owner;
grant select, insert on cambio_del_equipo to leda_owner;

-- `leda_app` deja de escribir el equipo. De `membership` le queda `update` sólo sobre
-- `workspace_id`, que la política del espacio no deja cambiar: lo pide `select ... for share`.
revoke insert, update, delete on area, rol, membership, approval_policy, escalation_route
  from leda_app;
grant update (workspace_id) on membership to leda_app;

commit;
