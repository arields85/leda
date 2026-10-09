\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0044_espera_su_bloqueo.sql.
--
-- Borra la columna `espera_su_bloqueo_id` de `dicho_de_quien_destraba` y vuelve a la restricción
-- de la 0043 (para cuándo, que ya está, sus palabras o que no le corresponde: al menos uno). Lo
-- que sólo decía con qué bloqueo suyo estaba trabado, sin palabras, no entra en esa restricción
-- y se borra, y los bloqueos que enlazaba dejan de estar enlazados: antes de correrlo en una base
-- con datos, `pg_dump` de la tabla.
begin;
set search_path = leda, public;

alter table dicho_de_quien_destraba drop constraint if exists dicho_de_quien_destraba_dice_algo;
delete from dicho_de_quien_destraba
 where para_cuando is null and not ya_esta and lo_que_dice is null and not no_le_corresponde;
alter table dicho_de_quien_destraba
  drop constraint if exists dicho_de_quien_destraba_espera_su_bloqueo;
alter table dicho_de_quien_destraba drop column if exists espera_su_bloqueo_id;
alter table dicho_de_quien_destraba add constraint dicho_de_quien_destraba_dice_algo check (
  para_cuando is not null or ya_esta or lo_que_dice is not null or no_le_corresponde);

commit;
