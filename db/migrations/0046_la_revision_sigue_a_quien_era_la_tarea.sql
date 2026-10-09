\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0045_pase_de_tarea.sql. Las decisiones 26 y 28 del usuario sobre delegar (C-7;
-- `odd/tasks/fase-c.md`, 2026-10-09), con la 43 derivada de la 28:
--
-- - **La revisión sigue a quien era la tarea, no a quien la termina haciendo** (decisión 28). Una
--   tarea que cambió de manos la revisa quien aprueba el trabajo de quien la tenía antes de su
--   primer pase (`task.era_de_membership_id`, que reemplaza a `task.revisa_membership_id`), aunque
--   ésa sea la persona que ahora la hace: la tarea de Nahuel que toma Marcos la revisa Marcos. Se
--   lee en el momento (`quien_revisa_la_tarea`), así que si la plataforma cambia quién aprueba a
--   esa persona, la revisión sigue el cambio (decisión 43). `cambio_de_responsable.
--   revisa_membership_id` sigue guardando quién la revisaba en el momento del pase.
-- - **Un pase que nadie contesta termina** (decisión 26): el estado `sin_respuesta`, terminal,
--   que deja la tarea con quien la tenía.
--
-- Se deshace con `db/rollbacks/0046_la_revision_sigue_a_quien_era_la_tarea.sql`, antes que la
-- vuelta atrás de la 0045.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0046 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('leda.pase_de_tarea') is null then
    raise exception '0046 requires 0045_pase_de_tarea.sql';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'task'
                and column_name = 'era_de_membership_id') then
    raise exception '0046 ya está aplicada.';
  end if;
end $$;

alter table task rename column revisa_membership_id to era_de_membership_id;
alter table task rename constraint task_revisa to task_era_de;
comment on column task.era_de_membership_id is
  'El Motor (C-7, decisión 28): de quién era la tarea antes de su primer pase (lo escribe el cambio de responsable). La revisa quien aprueba el trabajo de esa persona. Nulo: nunca cambió de manos.';

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
  -- Quién la tiene y de quién era cambian sólo con un pase confirmado por quien lo pidió, quien
  -- lo decidió y quien la toma (migraciones 0045 y 0046; C-7, delegar): lo aplica
  -- `aplicar_cambio_de_responsable`, al agregarse el cambio en `cambio_de_responsable`.
  if (new.responsable_membership_id is distinct from old.responsable_membership_id
      or new.era_de_membership_id is distinct from old.era_de_membership_id)
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

-- De quién era cada tarea que ya cambió de manos: quien la tenía en su primer pase. La columna
-- traía quién la revisaba según la 0045, que deja de valer.
select set_config('leda.aplicando_pase', '1', true);
update task t
   set era_de_membership_id = (select c.anterior_membership_id from cambio_de_responsable c
                                where c.task_id = t.id order by c.at, c.id limit 1)
 where t.era_de_membership_id is not null
    or exists (select 1 from cambio_de_responsable c where c.task_id = t.id);
select set_config('leda.aplicando_pase', '0', true);

-- Quién revisa el trabajo de una tarea (migraciones 0045 y 0046; C-7, decisiones 28 y 43): quien
-- aprueba el trabajo de quien era la tarea antes de su primer pase o, si nunca cambió de manos, el
-- de su responsable (`membership.aprobador_membership_id`), leído ahora: si la plataforma lo
-- cambia, la revisión sigue el cambio. Puede ser quien la hace ahora (la tarea de Nahuel que toma
-- Marcos la revisa Marcos). Es la única regla: el cierre, quién ve la página y la aplicación la
-- leen de acá.
create or replace function quien_revisa_la_tarea(p_task uuid)
returns uuid
language sql stable set search_path = leda, public, pg_temp as $$
  select m.aprobador_membership_id
    from task t
    join membership m on m.id = coalesce(t.era_de_membership_id, t.responsable_membership_id)
   where t.id = p_task;
$$;

-- Agregar un cambio de responsable lo aplica: comprueba que el pase espera que lo tome quien lo
-- recibe (con la decisión ya dada, o dada con su respuesta si es quien decide), que la tarea
-- sigue en manos de quien la tenía y en un estado que se pasa, deja escrito de quién era la tarea
-- antes de su primer pase y quién la revisa desde ahora (quien aprueba el trabajo de esa persona),
-- cambia la tarea y da el pase por tomado. Corre con los privilegios de `leda_owner`, que no
-- saltea la RLS: sólo ve el espacio de la transacción.
create or replace function aplicar_cambio_de_responsable() returns trigger
security definer set search_path = leda, public, pg_temp as $$
declare p pase_de_tarea%rowtype;
        t task%rowtype;
        era uuid;
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
  era := coalesce(t.era_de_membership_id, t.responsable_membership_id);
  new.revisa_membership_id := (select m.aprobador_membership_id from membership m
                                where m.id = era);
  perform set_config('leda.aplicando_pase', '1', true);
  update task
     set responsable_membership_id = p.a_membership_id,
         era_de_membership_id = era,
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

comment on table cambio_de_responsable is
  'El Motor (C-7): el cambio de quién tiene una tarea, con el pase que lo autorizó, quién la tenía, quién la tomó y quién revisaba su trabajo en ese momento (después, quien aprueba el trabajo de quien era la tarea, migración 0046). Sólo se agrega; agregarlo aplica el cambio en la tarea.';

-- Un pase que nadie contesta termina sin respuesta (decisión 26): terminal, como los demás.
alter table pase_de_tarea drop constraint pase_de_tarea_estado_check;
alter table pase_de_tarea add constraint pase_de_tarea_estado_check check (estado in (
  'esperando_decision', 'esperando_que_la_tome', 'la_tomo', 'no_lo_aprobo', 'no_la_tomo',
  'sin_efecto', 'sin_respuesta'));

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
     and new.estado not in ('esperando_que_la_tome', 'la_tomo', 'no_la_tomo', 'sin_efecto',
                            'sin_respuesta') then
    raise exception 'pase_de_tarea: el pase ya se decidió';
  end if;
  if old.estado = 'esperando_decision' and new.estado in ('la_tomo', 'no_la_tomo')
     and old.decide_membership_id <> old.a_membership_id then
    raise exception 'pase_de_tarea: falta la decisión';
  end if;
  return new;
end $$ language plpgsql;

commit;
