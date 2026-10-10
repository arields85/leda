\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0049_lo_asentado_en_la_historia.sql. El resumen para cualquiera, el detalle a
-- pedido (decisión 33 del usuario, 2026-10-09; `odd/tasks/fase-c.md`; conversación 45).
--
-- El resumen de una tarea (qué tarea, de quién, para cuándo, cómo quedó) lo ve cualquiera del
-- equipo; el detalle (la página: fotos, archivos, correcciones pedidas) sólo quienes tienen que
-- ver con la tarea (ADR 0019, 7b, igual). Quien no la ve puede pedir el detalle, y lo decide el
-- encargado del sector de la tarea (el referente de su área). Compartirla con alguien de otro
-- sector es nuevo. Lo guardan:
--
-- - `pedido_de_detalle`: quién pidió el detalle de qué tarea, quién lo decide y cómo terminó,
--   sólo hacia adelante (`vigilar_pedido_de_detalle`); uno abierto por tarea y persona.
-- - `tarea_compartida`: con quién se compartió una tarea, quién la compartió (sólo el encargado
--   del sector de la tarea) y cuándo; revocable una sola vez (por el encargado o por quien la
--   compartió), nunca borrada (`vigilar_tarea_compartida`). Una vigente por tarea y persona.
-- - `puede_ver_tarea` la cuenta: la página y su enlace la honran, y cada vista queda registrada
--   como cualquier otra (`vista_de_tarea`, 7e).
--
-- Aislamiento: espacio obligatorio, RLS forzado con su política y todas las referencias con el
-- espacio. `leda_app` agrega, lee y cambia los dos (un pedido avanza, lo compartido se revoca);
-- nunca los borra. Ninguna función nueva es `security definer`: los disparadores corren con el
-- rol de quien escribe, bajo la RLS de su espacio.
--
-- Se deshace con `db/rollbacks/0050_el_detalle_de_una_tarea.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0050 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0049 está aplicada y la 0050 no.
do $$ begin
  if position('quien_destraba' in
              pg_get_functiondef('leda.leer_pagina_de_tarea(text)'::regprocedure)) = 0 then
    raise exception '0050 preflight failed: falta la 0049 (lo asentado en la historia)';
  end if;
  if to_regclass('leda.tarea_compartida') is not null then
    raise exception '0050 ya está aplicada.';
  end if;
end $$;

-- El detalle de una tarea, a pedido (migración 0050; decisión 33 del usuario): quien no ve una
-- tarea pide su detalle, y lo decide el encargado del sector de la tarea. Un "no" lo termina sin
-- compartir nada. Nada se borra.
create table pedido_de_detalle (
  id                        uuid primary key default gen_random_uuid(),
  workspace_id              uuid not null references workspace(id) on delete cascade,
  task_id                   uuid not null,
  pedido_por_membership_id  uuid not null,
  decide_membership_id      uuid not null,
  estado                    text not null check (estado in (
                              'esperando_decision', 'compartida', 'no_compartida',
                              'sin_efecto')),
  pedido_en                 timestamptz not null,
  decidido_en               timestamptz,
  motivo                    text check (btrim(motivo) <> ''),
  constraint pedido_de_detalle_workspace_id_unique unique (workspace_id, id),
  constraint pedido_de_detalle_tarea
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade,
  constraint pedido_de_detalle_pedido_por
    foreign key (workspace_id, pedido_por_membership_id) references membership(workspace_id, id),
  constraint pedido_de_detalle_decide
    foreign key (workspace_id, decide_membership_id) references membership(workspace_id, id),
  constraint pedido_de_detalle_a_otra_persona check (decide_membership_id <> pedido_por_membership_id),
  constraint pedido_de_detalle_decidido check (
    estado = 'esperando_decision' or decidido_en is not null)
);

-- Un pedido abierto por tarea y persona.
create unique index pedido_de_detalle_uno_abierto on pedido_de_detalle (task_id, pedido_por_membership_id)
  where estado = 'esperando_decision';
create index pedido_de_detalle_de_quien on pedido_de_detalle (workspace_id, decide_membership_id, estado);

-- Una tarea compartida con alguien que no la veía: quién, quién la compartió y cuándo; si se dejó
-- de compartir, cuándo y quién. Una vigente por tarea y persona.
create table tarea_compartida (
  id                            uuid primary key default gen_random_uuid(),
  workspace_id                  uuid not null references workspace(id) on delete cascade,
  task_id                       uuid not null,
  membership_id                 uuid not null,
  compartida_por_membership_id  uuid not null,
  pedido_id                     uuid,
  at                            timestamptz not null,
  revocada_en                   timestamptz,
  revocada_por_membership_id    uuid,
  constraint tarea_compartida_tarea
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade,
  constraint tarea_compartida_con
    foreign key (workspace_id, membership_id) references membership(workspace_id, id),
  constraint tarea_compartida_por
    foreign key (workspace_id, compartida_por_membership_id) references membership(workspace_id, id),
  constraint tarea_compartida_pedido
    foreign key (workspace_id, pedido_id) references pedido_de_detalle(workspace_id, id)
    on delete cascade,
  constraint tarea_compartida_revocada_por
    foreign key (workspace_id, revocada_por_membership_id)
    references membership(workspace_id, id),
  constraint tarea_compartida_con_otra_persona check (membership_id <> compartida_por_membership_id),
  constraint tarea_compartida_revocada check (
    (revocada_en is null) = (revocada_por_membership_id is null))
);

create unique index tarea_compartida_vigente on tarea_compartida (task_id, membership_id)
  where revocada_en is null;

comment on table pedido_de_detalle is
  'El Motor (decisión 33 del usuario): el pedido del detalle de una tarea que la persona no ve, quién lo decide (el encargado del sector de la tarea) y cómo terminó. Cambia de estado sólo hacia adelante.';
comment on table tarea_compartida is
  'El Motor (decisión 33 del usuario): una tarea compartida con alguien que no la veía, quién la compartió (el encargado del sector de la tarea) y cuándo. Cuenta para ver la página (puede_ver_tarea). Sólo se revoca, una vez; nunca se borra.';

-- Un pedido del detalle lo decide el encargado del sector de la tarea, empieza esperando su
-- decisión y sólo avanza: los datos del pedido no cambian y uno terminado no se reabre
-- (migración 0050).
create or replace function vigilar_pedido_de_detalle() returns trigger as $$
begin
  if tg_op = 'INSERT' then
    if new.estado <> 'esperando_decision' then
      raise exception 'pedido_de_detalle: un pedido nuevo espera la decisión';
    end if;
    if new.decide_membership_id is distinct from (
         select a.referente_membership_id from task t join area a on a.id = t.area_id
          where t.id = new.task_id and t.workspace_id = new.workspace_id) then
      raise exception 'pedido_de_detalle: lo decide el encargado del sector de la tarea';
    end if;
    return new;
  end if;
  if new.workspace_id is distinct from old.workspace_id
     or new.task_id is distinct from old.task_id
     or new.pedido_por_membership_id is distinct from old.pedido_por_membership_id
     or new.decide_membership_id is distinct from old.decide_membership_id
     or new.pedido_en is distinct from old.pedido_en then
    raise exception 'pedido_de_detalle: los datos del pedido no cambian';
  end if;
  if old.estado <> 'esperando_decision' and new is distinct from old then
    raise exception 'pedido_de_detalle: el pedido ya terminó';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_vigilar_pedido_de_detalle
  before insert or update on pedido_de_detalle
  for each row execute function vigilar_pedido_de_detalle();

-- Una tarea se comparte vigente y sólo la comparte el encargado del sector de la tarea; si viene
-- de un pedido, es lo que se pidió. Después, lo único que cambia es dejarla de compartir, una
-- vez, por el encargado o por quien la compartió (migración 0050).
create or replace function vigilar_tarea_compartida() returns trigger as $$
declare encargado uuid;
begin
  select a.referente_membership_id into encargado
    from task t join area a on a.id = t.area_id
   where t.id = new.task_id and t.workspace_id = new.workspace_id;
  if tg_op = 'INSERT' then
    if new.revocada_en is not null then
      raise exception 'tarea_compartida: una tarea se comparte vigente';
    end if;
    if encargado is null or new.compartida_por_membership_id is distinct from encargado then
      raise exception 'tarea_compartida: la comparte el encargado del sector de la tarea';
    end if;
    if new.pedido_id is not null and not exists (
         select 1 from pedido_de_detalle p
          where p.id = new.pedido_id and p.task_id = new.task_id
            and p.pedido_por_membership_id = new.membership_id) then
      raise exception 'tarea_compartida: no es lo que se pidió';
    end if;
    return new;
  end if;
  if new.workspace_id is distinct from old.workspace_id
     or new.task_id is distinct from old.task_id
     or new.membership_id is distinct from old.membership_id
     or new.compartida_por_membership_id is distinct from old.compartida_por_membership_id
     or new.pedido_id is distinct from old.pedido_id
     or new.at is distinct from old.at then
    raise exception 'tarea_compartida: lo compartido no cambia';
  end if;
  if old.revocada_en is not null then
    if new is distinct from old then
      raise exception 'tarea_compartida: ya se dejó de compartir';
    end if;
    return new;
  end if;
  if new.revocada_en is not null
     and new.revocada_por_membership_id is distinct from encargado
     and new.revocada_por_membership_id is distinct from old.compartida_por_membership_id then
    raise exception 'tarea_compartida: la deja de compartir el encargado del sector de la tarea';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_vigilar_tarea_compartida
  before insert or update on tarea_compartida
  for each row execute function vigilar_tarea_compartida();

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

alter function puede_ver_tarea(uuid, uuid) owner to leda_owner;
revoke execute on function puede_ver_tarea(uuid, uuid) from public;
grant execute on function puede_ver_tarea(uuid, uuid) to leda_app;

alter table pedido_de_detalle enable row level security;
alter table pedido_de_detalle force row level security;
create policy aislamiento_espacio on pedido_de_detalle
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
alter table tarea_compartida enable row level security;
alter table tarea_compartida force row level security;
create policy aislamiento_espacio on tarea_compartida
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
grant all privileges on pedido_de_detalle, tarea_compartida to leda_owner, leda_admin;
grant select, insert, update on pedido_de_detalle, tarea_compartida to leda_app;

commit;
