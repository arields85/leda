\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0043_no_le_corresponde.sql.
--
-- Borra la columna `no_le_corresponde` de `dicho_de_quien_destraba` y vuelve a la restricción de
-- la 0042 (para cuándo, que ya está o sus palabras: al menos uno). Lo que sólo decía que no le
-- corresponde, sin palabras, no entra en esa restricción y se borra: antes de correrlo en una
-- base con datos, `pg_dump` de la tabla.
begin;
set search_path = leda, public;

alter table dicho_de_quien_destraba
  drop constraint if exists dicho_de_quien_destraba_no_le_corresponde;
alter table dicho_de_quien_destraba drop constraint if exists dicho_de_quien_destraba_dice_algo;
delete from dicho_de_quien_destraba
 where para_cuando is null and not ya_esta and lo_que_dice is null;
alter table dicho_de_quien_destraba drop column if exists no_le_corresponde;
alter table dicho_de_quien_destraba add constraint dicho_de_quien_destraba_dice_algo check (
  para_cuando is not null or ya_esta or lo_que_dice is not null);

commit;
