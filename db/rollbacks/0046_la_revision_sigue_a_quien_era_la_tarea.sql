\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0046_la_revision_sigue_a_quien_era_la_tarea.sql.
--
-- Vuelve a poner `task.revisa_membership_id` (quién revisa una tarea que cambió de manos, fijo
-- desde su último pase, como lo guardó `cambio_de_responsable`) y las cuatro funciones como las
-- dejó la 0045. Un pase que terminó sin respuesta queda sin efecto (la 0045 no conoce
-- `sin_respuesta`); la tarea ya seguía con quien la tenía. Se corre antes que la vuelta atrás de
-- la 0045.
begin;
set search_path = leda, public;

do $$ begin
  if not exists (select 1 from information_schema.columns
                  where table_schema = 'leda' and table_name = 'task'
                    and column_name = 'era_de_membership_id') then
    raise exception 'La 0046 no está aplicada.';
  end if;
end $$;

alter table pase_de_tarea disable trigger trg_vigilar_pase_de_tarea;
update pase_de_tarea set estado = 'sin_efecto' where estado = 'sin_respuesta';
alter table pase_de_tarea enable trigger trg_vigilar_pase_de_tarea;
alter table pase_de_tarea drop constraint pase_de_tarea_estado_check;
alter table pase_de_tarea add constraint pase_de_tarea_estado_check check (estado in (
  'esperando_decision', 'esperando_que_la_tome', 'la_tomo', 'no_lo_aprobo', 'no_la_tomo',
  'sin_efecto'));

alter table task rename column era_de_membership_id to revisa_membership_id;
alter table task rename constraint task_era_de to task_revisa;
comment on column task.revisa_membership_id is
  'El Motor (C-7, delegar): quién revisa el trabajo de la tarea desde que cambió de manos (lo escribe el cambio de responsable). Nulo: quien aprueba el trabajo de su responsable.';
comment on table cambio_de_responsable is
  'El Motor (C-7): el cambio de quién tiene una tarea, con el pase que lo autorizó, quién la tenía, quién la tomó y quién revisa su trabajo desde entonces. Sólo se agrega; agregarlo aplica el cambio en la tarea.';

-- Quién revisa el trabajo de una tarea (migración 0045; C-7, delegar): el que quedó escrito en la
-- tarea cuando cambió de manos o, si nunca cambió, quien aprueba el trabajo de su responsable
-- (`membership.aprobador_membership_id`). Es la única regla: el cierre, quién ve la página y la
-- aplicación la leen de acá.
create or replace function quien_revisa_la_tarea(p_task uuid)
returns uuid
language sql stable set search_path = leda, public, pg_temp as $$
  select coalesce(t.revisa_membership_id, m.aprobador_membership_id)
    from task t
    left join membership m on m.id = t.responsable_membership_id
   where t.id = p_task;
$$;

create or replace function bloquear_estado_directo() returns trigger as $$
begin
  if new.objective_id is distinct from old.objective_id
     or new.titulo is distinct from old.titulo
     or new.descripcion is distinct from old.descripcion
     or new.area_id is distinct from old.area_id
     or new.fecha_objetivo is distinct from old.fecha_objetivo
     or new.criterio_aceptacion is distinct from old.criterio_aceptacion
     or new.evidencia_requerida is distinct from old.evidencia_requerida
     or new.evidencia_policy_version is distinct from old.evidencia_policy_version
     or new.source_draft_id is distinct from old.source_draft_id then
    raise exception 'Los campos de compromiso de una tarea son inmutables.';
  end if;
  -- Quién la tiene y quién revisa su trabajo cambian sólo con un pase confirmado por quien lo
  -- pidió, quien lo decidió y quien la toma (migración 0045; C-7, delegar): lo aplica
  -- `aplicar_cambio_de_responsable`, al agregarse el cambio en `cambio_de_responsable`.
  if (new.responsable_membership_id is distinct from old.responsable_membership_id
      or new.revisa_membership_id is distinct from old.revisa_membership_id)
     and coalesce(current_setting('leda.aplicando_pase', true), '0') <> '1' then
    raise exception 'Los campos de compromiso de una tarea son inmutables.';
  end if;
  if new.estado is distinct from old.estado
     and coalesce(current_setting('leda.aplicando_evento', true), '0') <> '1' then
    raise exception
      'El estado de una tarea no se escribe directamente. Insertá una fila en task_state_event.';
  end if;
  return new;
end $$ language plpgsql;

-- Un pase sólo se pide sobre una tarea asignada, en curso o trabada, de quien la tiene, y sólo
-- avanza: los datos del pedido no cambian, uno terminado no se reabre y `la_tomo` lo escribe sólo
-- el cambio de responsable (migración 0045).
create or replace function vigilar_pase_de_tarea() returns trigger as $$
declare t task%rowtype;
begin
  if tg_op = 'INSERT' then
    if new.estado not in ('esperando_decision', 'esperando_que_la_tome') then
      raise exception 'pase_de_tarea: un pase nuevo empieza esperando la decisión o que la tomen';
    end if;
    select * into t from task where id = new.task_id;
    if not found or t.responsable_membership_id is distinct from new.de_membership_id
       or t.estado not in ('asignada', 'en_curso', 'bloqueada') then
      raise exception 'pase_de_tarea: la tarea no se puede pasar';
    end if;
    return new;
  end if;
  if new.workspace_id is distinct from old.workspace_id
     or new.task_id is distinct from old.task_id
     or new.de_membership_id is distinct from old.de_membership_id
     or new.a_membership_id is distinct from old.a_membership_id
     or new.pedido_por_membership_id is distinct from old.pedido_por_membership_id
     or new.decide_membership_id is distinct from old.decide_membership_id
     or new.pedido_en is distinct from old.pedido_en then
    raise exception 'pase_de_tarea: los datos del pedido no cambian';
  end if;
  if old.estado not in ('esperando_decision', 'esperando_que_la_tome')
     and new is distinct from old then
    raise exception 'pase_de_tarea: el pase ya terminó';
  end if;
  if new.estado = 'la_tomo' and old.estado <> 'la_tomo'
     and coalesce(current_setting('leda.aplicando_pase', true), '0') <> '1' then
    raise exception 'pase_de_tarea: sólo el cambio de responsable lo da por tomado';
  end if;
  if old.estado = 'esperando_que_la_tome'
     and new.estado not in ('esperando_que_la_tome', 'la_tomo', 'no_la_tomo', 'sin_efecto') then
    raise exception 'pase_de_tarea: el pase ya se decidió';
  end if;
  if old.estado = 'esperando_decision' and new.estado in ('la_tomo', 'no_la_tomo')
     and old.decide_membership_id <> old.a_membership_id then
    raise exception 'pase_de_tarea: falta la decisión';
  end if;
  return new;
end $$ language plpgsql;

-- Agregar un cambio de responsable lo aplica: comprueba que el pase espera que lo tome quien lo
-- recibe (con la decisión ya dada, o dada con su respuesta si es quien decide), que la tarea
-- sigue en manos de quien la tenía y en un estado que se pasa, escribe quién revisa su trabajo
-- desde ahora (quien lo revisaba; si es quien la toma, quien aprueba el trabajo de esa persona),
-- cambia la tarea y da el pase por tomado. Corre con los privilegios de `leda_owner`, que no
-- saltea la RLS: sólo ve el espacio de la transacción.
create or replace function aplicar_cambio_de_responsable() returns trigger
security definer set search_path = leda, public, pg_temp as $$
declare p pase_de_tarea%rowtype;
        t task%rowtype;
        revisa uuid;
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
  revisa := coalesce(t.revisa_membership_id,
                     (select m.aprobador_membership_id from membership m
                       where m.id = t.responsable_membership_id));
  if revisa = p.a_membership_id then
    revisa := (select m.aprobador_membership_id from membership m
                where m.id = p.a_membership_id);
  end if;
  new.revisa_membership_id := revisa;
  perform set_config('leda.aplicando_pase', '1', true);
  update task
     set responsable_membership_id = p.a_membership_id,
         revisa_membership_id = revisa,
         actualizado_en = new.at
   where id = t.id;
  update pase_de_tarea
     set estado = 'la_tomo', contestado_en = new.at,
         decidido_en = coalesce(decidido_en, new.at)
   where id = p.id;
  perform set_config('leda.aplicando_pase', '0', true);
  return new;
end $$ language plpgsql;

alter function aplicar_cambio_de_responsable() owner to leda_owner;
revoke execute on function aplicar_cambio_de_responsable() from public;

-- Quién revisa cada tarea que cambió de manos, como la 0045: el que quedó escrito en su último
-- cambio de responsable. Con la regla de la 0045 nadie revisa lo suyo: si quien quedó escrito es
-- quien la tiene (la 0046 lo permite, decisión 28: la de Nahuel que tomó Marcos la revisa Marcos),
-- la revisa quien aprueba el trabajo de esa persona, como lo habría escrito la 0045 al pasarla.
select set_config('leda.aplicando_pase', '1', true);
update task t
   set revisa_membership_id = (
         select case when c.revisa_membership_id = t.responsable_membership_id
                     then (select m.aprobador_membership_id from membership m
                            where m.id = t.responsable_membership_id)
                     else c.revisa_membership_id end
           from cambio_de_responsable c
          where c.task_id = t.id order by c.at desc, c.id desc limit 1)
 where t.revisa_membership_id is not null;
select set_config('leda.aplicando_pase', '0', true);

commit;
