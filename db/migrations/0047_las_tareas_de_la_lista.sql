\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0046_la_revision_sigue_a_quien_era_la_tarea.sql. Las listas de la cadencia de la
-- semana (C-6; decisiones 31 y 46 del usuario, 2026-10-09; `odd/tasks/fase-c.md`; conversación de
-- prueba 40):
--
-- - **La primera lista de la semana es completa; las otras, sólo lo que falta** (decisión 46): el
--   miércoles y el viernes van sólo las tareas que cambiaron o que la persona no contestó. Para
--   saberlo, cada lista que sale guarda las tareas abiertas de la persona en ese momento, cada una
--   con su situación, si se mostró, si se preguntó por ella y desde cuándo no la contesta.
-- - **Lo contestado no se vuelve a preguntar** (decisión 31): cuando la persona cuenta cómo viene
--   una tarea, su renglón de la última lista queda contestado, con la situación de después.
--
-- Va fuera de los hechos del aviso (`scheduled_notice.hechos`), que son lo que recibió la IA para
-- redactarlo: esto lo lee sólo el código.
--
-- Se deshace con `db/rollbacks/0047_las_tareas_de_la_lista.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0047 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: los avisos del motor existen (migración 0030) y todavía no la columna nueva.
do $$ begin
  if to_regclass('leda.scheduled_notice') is null then
    raise exception '0047 preflight failed: falta la 0030 (scheduled_notice)';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'scheduled_notice'
                and column_name = 'tareas_de_la_lista') then
    raise exception '0047 ya está aplicada.';
  end if;
end $$;

alter table scheduled_notice add column tareas_de_la_lista jsonb;

comment on column scheduled_notice.tareas_de_la_lista is
  'El Motor (C-6, decisiones 31 y 46 del usuario, 2026-10-09): en la lista de la cadencia que salió, las tareas abiertas de la persona en ese momento, cada una con su situación, si se mostró, si se preguntó por ella, desde cuándo no la contesta y cuándo la contestó. Fuera de los hechos: lo lee sólo el código. Nulo en los demás avisos y en las listas de antes.';

commit;
