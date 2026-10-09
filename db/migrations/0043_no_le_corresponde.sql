\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0042_lo_que_dice_quien_destraba.sql. La persecución del bloqueo, porción 3 de la
-- C-5 (`odd/tasks/fase-c.md`, decisión 5; ADR 0017, decisión 3a, paso 4; conversación 34).
--
-- Quien destraba puede decir que no le corresponde: es un hecho del bloqueo, como lo demás que
-- dice (`dicho_de_quien_destraba.no_le_corresponde`), atribuido a quien lo dijo. Alcanza solo
-- (sin fecha ni palabras) y nunca va con para cuándo lo resuelve ni con que ya está. A quién le
-- toca, si lo dice, es otra fila de `blocker_unblocker`, dicha por esa persona.
--
-- Sin tablas nuevas: el aislamiento, las referencias del mismo espacio y que `leda_app` sólo
-- agregue y lea siguen como los dejó la 0042.
--
-- Se deshace con `db/rollbacks/0043_no_le_corresponde.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0043 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('leda.dicho_de_quien_destraba') is null then
    raise exception '0043 requires 0042_lo_que_dice_quien_destraba.sql';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'dicho_de_quien_destraba'
                and column_name = 'no_le_corresponde') then
    raise exception '0043 ya está aplicada.';
  end if;
end $$;

alter table dicho_de_quien_destraba
  add column no_le_corresponde boolean not null default false;

alter table dicho_de_quien_destraba drop constraint dicho_de_quien_destraba_dice_algo;
alter table dicho_de_quien_destraba add constraint dicho_de_quien_destraba_dice_algo check (
  para_cuando is not null or ya_esta or lo_que_dice is not null or no_le_corresponde);
alter table dicho_de_quien_destraba add constraint dicho_de_quien_destraba_no_le_corresponde
  check (not no_le_corresponde or (para_cuando is null and not ya_esta));

comment on column dicho_de_quien_destraba.no_le_corresponde is
  'El Motor (C-5, decisión 5): quien destraba dice que no le corresponde. Nunca junto con para cuándo ni con que ya está; a quién le toca, si lo dice, es otra fila de blocker_unblocker dicha por esa persona.';

commit;
