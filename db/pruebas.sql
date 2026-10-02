-- =========================================================================
-- Pruebas del esquema
--
-- Cada bloque comprueba que una regla del núcleo se cumple en la base y no
-- depende del criterio del modelo de lenguaje. Un fallo aborta el archivo.
--
--   \i esquema.sql
--   \i pruebas.sql
-- =========================================================================

set search_path = leda, public;

create or replace function debe_fallar(sql text, esperado text)
returns void as $$
begin
  begin
    execute sql;
  exception when others then
    if position(lower(esperado) in lower(sqlerrm)) = 0 then
      raise exception 'Falló distinto de lo esperado. Esperaba "%", vino "%"', esperado, sqlerrm;
    end if;
    raise notice 'OK  rechazado: %', esperado;
    return;
  end;
  raise exception 'FALLA: se esperaba un rechazo por "%" y la operación pasó', esperado;
end $$ language plpgsql;

-- -------------------------------------------------------------------------
-- Datos mínimos de CoreWork
-- -------------------------------------------------------------------------

insert into app_user (id, telegram_user_id, nombre) values
  ('11111111-1111-1111-1111-111111111111', 1001, 'Ismael Soschinski'),
  ('22222222-2222-2222-2222-222222222222', 1002, 'Ariel De Simone'),
  ('33333333-3333-3333-3333-333333333333', 1003, 'Marcos Tarquini'),
  ('44444444-4444-4444-4444-444444444444', 1004, 'Nahuel Gimenez');

-- Ariel es administrador de plataforma. Eso no le da nada dentro de CoreWork:
-- ahí es referente de CoreLabs y nada más.
insert into platform_role (app_user_id, rol)
  values ('22222222-2222-2222-2222-222222222222', 'administrador');

insert into workspace (id, slug, nombre) values
  ('c0000000-0000-0000-0000-000000000001', 'corework', 'CoreWork'),
  ('c0000000-0000-0000-0000-000000000002', 'mantenimiento', 'Mantenimiento');

insert into area (id, workspace_id, slug, nombre) values
  ('a0000000-0000-0000-0000-000000000001','c0000000-0000-0000-0000-000000000001','direccion','Dirección'),
  ('a0000000-0000-0000-0000-000000000002','c0000000-0000-0000-0000-000000000001','ot','OT'),
  ('a0000000-0000-0000-0000-000000000003','c0000000-0000-0000-0000-000000000001','planos','Planos'),
  ('a0000000-0000-0000-0000-000000000004','c0000000-0000-0000-0000-000000000001','corelabs','CoreLabs');

insert into rol (id, workspace_id, slug, nombre, autoridad_final) values
  ('b0000000-0000-0000-0000-000000000001','c0000000-0000-0000-0000-000000000001','direccion','Dirección',true),
  ('b0000000-0000-0000-0000-000000000002','c0000000-0000-0000-0000-000000000001','referente','Referente',false),
  ('b0000000-0000-0000-0000-000000000003','c0000000-0000-0000-0000-000000000001','integrante','Integrante',false);

insert into membership (id, workspace_id, app_user_id, area_id, rol_id) values
  ('d0000000-0000-0000-0000-000000000001','c0000000-0000-0000-0000-000000000001','11111111-1111-1111-1111-111111111111','a0000000-0000-0000-0000-000000000001','b0000000-0000-0000-0000-000000000001'),
  ('d0000000-0000-0000-0000-000000000002','c0000000-0000-0000-0000-000000000001','22222222-2222-2222-2222-222222222222','a0000000-0000-0000-0000-000000000004','b0000000-0000-0000-0000-000000000002'),
  ('d0000000-0000-0000-0000-000000000003','c0000000-0000-0000-0000-000000000001','33333333-3333-3333-3333-333333333333','a0000000-0000-0000-0000-000000000002','b0000000-0000-0000-0000-000000000002'),
  ('d0000000-0000-0000-0000-000000000004','c0000000-0000-0000-0000-000000000001','44444444-4444-4444-4444-444444444444','a0000000-0000-0000-0000-000000000003','b0000000-0000-0000-0000-000000000003');

-- Los planos de Nahuel los aprueba un referente: Marcos.
insert into approval_policy (id, workspace_id, sujeto, area_id) values
  ('e0000000-0000-0000-0000-000000000001','c0000000-0000-0000-0000-000000000001','tarea','a0000000-0000-0000-0000-000000000003');
insert into approval_requirement (approval_policy_id, tipo, rol_id) values
  ('e0000000-0000-0000-0000-000000000001','rol','b0000000-0000-0000-0000-000000000002');

insert into objective (id, workspace_id, tipo, titulo) values
  ('f0000000-0000-0000-0000-000000000001','c0000000-0000-0000-0000-000000000001','estrategico','Vincular Steigen con CoreLabs'),
  ('f0000000-0000-0000-0000-000000000002','c0000000-0000-0000-0000-000000000001','operativo','Integrar comprimidora 3');
update objective set parent_id = 'f0000000-0000-0000-0000-000000000001'
  where id = 'f0000000-0000-0000-0000-000000000002';

insert into task (id, workspace_id, objective_id, titulo, area_id, responsable_membership_id, fecha_objetivo, criterio_aceptacion, evidencia_requerida) values
  ('10000000-0000-0000-0000-000000000001','c0000000-0000-0000-0000-000000000001','f0000000-0000-0000-0000-000000000002','Relevar plano del tablero','a0000000-0000-0000-0000-000000000003','d0000000-0000-0000-0000-000000000004','2026-08-20','Plano revisado','{archivo}'),
  ('10000000-0000-0000-0000-000000000002','c0000000-0000-0000-0000-000000000001','f0000000-0000-0000-0000-000000000002','Programar PLC','a0000000-0000-0000-0000-000000000002','d0000000-0000-0000-0000-000000000003','2026-08-20','PLC probado','{}');

-- =========================================================================
-- 1. Un espacio no puede tener dos autoridades finales
-- =========================================================================
select debe_fallar($$
  insert into rol (workspace_id, slug, nombre, autoridad_final)
  values ('c0000000-0000-0000-0000-000000000001','jefatura','Jefatura',true)
$$, 'rol_una_autoridad_final');

-- =========================================================================
-- 2. El estado no se escribe directamente: se inserta un evento
-- =========================================================================
select debe_fallar($$
  update task set estado = 'terminada' where id = '10000000-0000-0000-0000-000000000001'
$$, 'no se escribe directamente');

-- =========================================================================
-- 3. No se puede bloquear sin un bloqueo que lo explique
-- =========================================================================
select debe_fallar($$
  insert into task_state_event (task_id, estado_nuevo, actor_kind)
  values ('10000000-0000-0000-0000-000000000001','bloqueada','leda')
$$, 'sin un bloqueo abierto');

-- =========================================================================
-- 4. No cierra sin criterio, sin evidencia ni sin aprobación
-- =========================================================================

insert into task_state_event (task_id, estado_anterior, estado_nuevo, actor_kind) values
  ('10000000-0000-0000-0000-000000000001', null, 'asignada','leda'),
  ('10000000-0000-0000-0000-000000000001','asignada','en_curso','persona'),
  ('10000000-0000-0000-0000-000000000001','en_curso','en_revision','persona');

select debe_fallar($$
  insert into task_state_event (task_id, estado_anterior, estado_nuevo, actor_kind)
  values ('10000000-0000-0000-0000-000000000001','en_revision','terminada','leda')
$$, 'criterio de aceptación');

update task set criterio_aceptacion = 'Plano en DWG revisado y versionado'
  where id = '10000000-0000-0000-0000-000000000001';

select debe_fallar($$
  insert into task_state_event (task_id, estado_anterior, estado_nuevo, actor_kind)
  values ('10000000-0000-0000-0000-000000000001','en_revision','terminada','leda')
$$, 'evidencia requerida');

insert into evidence (workspace_id, task_id, tipo, uri, entregado_por)
  values ('c0000000-0000-0000-0000-000000000001','10000000-0000-0000-0000-000000000001','archivo','drive://plano-t3.dwg','d0000000-0000-0000-0000-000000000004');

select debe_fallar($$
  insert into task_state_event (task_id, estado_anterior, estado_nuevo, actor_kind)
  values ('10000000-0000-0000-0000-000000000001','en_revision','terminada','leda')
$$, 'aprobaciones');

-- Marcos aprueba. Recién ahora cierra.
insert into approval (workspace_id, sujeto_tipo, sujeto_id, aprobador_membership_id, decision)
  values ('c0000000-0000-0000-0000-000000000001','tarea','10000000-0000-0000-0000-000000000001','d0000000-0000-0000-0000-000000000003','aprobado');

insert into task_state_event (task_id, estado_anterior, estado_nuevo, actor_kind)
  values ('10000000-0000-0000-0000-000000000001','en_revision','terminada','leda');

do $$ begin
  if (select estado from task where id='10000000-0000-0000-0000-000000000001') <> 'terminada' then
    raise exception 'FALLA: la proyección del estado no se aplicó';
  end if;
  raise notice 'OK  la tarea cerró y el estado se proyectó desde el evento';
end $$;

-- =========================================================================
-- 5. Sin ciclos en dependencias
-- =========================================================================
insert into dependency (workspace_id, origen_task_id, destino_task_id)
  values ('c0000000-0000-0000-0000-000000000001','10000000-0000-0000-0000-000000000001','10000000-0000-0000-0000-000000000002');

select debe_fallar($$
  insert into dependency (workspace_id, origen_task_id, destino_task_id)
  values ('c0000000-0000-0000-0000-000000000001','10000000-0000-0000-0000-000000000002','10000000-0000-0000-0000-000000000001')
$$, 'ciclo');

-- =========================================================================
-- 6. Un objetivo no cierra con partes abiertas ni sin aprobaciones
-- =========================================================================
select debe_fallar($$
  insert into objective_state_event (objective_id, estado_nuevo, actor_kind)
  values ('f0000000-0000-0000-0000-000000000002','terminado','leda')
$$, 'tareas sin terminar');

update task set criterio_aceptacion = 'PLC responde por Modbus'
  where id = '10000000-0000-0000-0000-000000000002';
insert into task_state_event (task_id, estado_nuevo, actor_kind)
  values ('10000000-0000-0000-0000-000000000002','terminada','leda');

select debe_fallar($$
  insert into objective_state_event (objective_id, estado_nuevo, actor_kind)
  values ('f0000000-0000-0000-0000-000000000002','terminado','leda')
$$, 'áreas por aprobar');

insert into approval (workspace_id, sujeto_tipo, sujeto_id, aprobador_membership_id, decision) values
  ('c0000000-0000-0000-0000-000000000001','objetivo','f0000000-0000-0000-0000-000000000002','d0000000-0000-0000-0000-000000000004','aprobado'),
  ('c0000000-0000-0000-0000-000000000001','objetivo','f0000000-0000-0000-0000-000000000002','d0000000-0000-0000-0000-000000000003','aprobado');

select debe_fallar($$
  insert into objective_state_event (objective_id, estado_nuevo, actor_kind)
  values ('f0000000-0000-0000-0000-000000000002','terminado','leda')
$$, 'aprobación final');

insert into approval (workspace_id, sujeto_tipo, sujeto_id, aprobador_membership_id, decision)
  values ('c0000000-0000-0000-0000-000000000001','objetivo','f0000000-0000-0000-0000-000000000002','d0000000-0000-0000-0000-000000000001','aprobado');

insert into objective_state_event (objective_id, estado_nuevo, actor_kind)
  values ('f0000000-0000-0000-0000-000000000002','terminado','leda');

do $$ begin raise notice 'OK  el objetivo cerró sólo con todas las partes y aprobaciones'; end $$;

-- =========================================================================
-- 7. La cola no duplica tras un reinicio
-- =========================================================================
insert into message_outbox (workspace_id, chat_id, cuerpo, dedupe_key)
  values ('c0000000-0000-0000-0000-000000000001', 500, 'Objetivos de la semana', 'corework:1003:lunes:2026-W31');

select debe_fallar($$
  insert into message_outbox (workspace_id, chat_id, cuerpo, dedupe_key)
  values ('c0000000-0000-0000-0000-000000000001', 500, 'Objetivos de la semana', 'corework:1003:lunes:2026-W31')
$$, 'dedupe_key');

-- =========================================================================
-- 8. Aislamiento entre espacios
-- =========================================================================
insert into area (workspace_id, slug, nombre)
  values ('c0000000-0000-0000-0000-000000000002','preventivo','Preventivo');

set role leda_app;
set "leda.workspace_id" = 'c0000000-0000-0000-0000-000000000001';

do $$
declare n integer;
begin
  select count(*) into n from area;
  if n <> 4 then raise exception 'FALLA: se ven % áreas, deberían ser 4', n; end if;
  select count(*) into n from task;
  if n <> 2 then raise exception 'FALLA: se ven % tareas, deberían ser 2', n; end if;
  raise notice 'OK  con CoreWork activo se ven sólo sus 4 áreas y 2 tareas';
end $$;

set "leda.workspace_id" = 'c0000000-0000-0000-0000-000000000002';

do $$
declare n integer;
begin
  select count(*) into n from area;
  if n <> 1 then raise exception 'FALLA: se ven % áreas, debería ser 1', n; end if;
  select count(*) into n from task;
  if n <> 0 then raise exception 'FALLA: Mantenimiento ve % tareas de otro espacio', n; end if;
  raise notice 'OK  Mantenimiento no ve nada de CoreWork';
end $$;

reset role;

do $$ begin raise notice '=== todas las pruebas pasaron ==='; end $$;
