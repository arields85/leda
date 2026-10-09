\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0043_no_le_corresponde.sql. La persecución del bloqueo, porción 4 de la C-5
-- (`odd/tasks/fase-c.md`, decisión 6, bloqueos encadenados; ADR 0017, decisión 3a;
-- conversación 35).
--
-- Quien destraba puede decir que no puede porque está trabado con algo suyo: es un hecho del
-- bloqueo que le preguntan, como lo demás que dice (`dicho_de_quien_destraba`), y nombra el
-- bloqueo suyo con el que está trabado (`espera_su_bloqueo_id`). Con eso los dos bloqueos quedan
-- enlazados sin una tabla nueva: lo que pasa con el suyo le llega, como información, a quien
-- espera más abajo. El bloqueo nombrado es del mismo espacio (la referencia lleva el espacio).
-- Alcanza solo como algo dicho.
--
-- Sin tablas nuevas: el aislamiento, las referencias del mismo espacio y que `leda_app` sólo
-- agregue y lea siguen como los dejó la 0042.
--
-- Se deshace con `db/rollbacks/0044_espera_su_bloqueo.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0044 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (select 1 from information_schema.columns
                  where table_schema = 'leda' and table_name = 'dicho_de_quien_destraba'
                    and column_name = 'no_le_corresponde') then
    raise exception '0044 requires 0043_no_le_corresponde.sql';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'dicho_de_quien_destraba'
                and column_name = 'espera_su_bloqueo_id') then
    raise exception '0044 ya está aplicada.';
  end if;
end $$;

alter table dicho_de_quien_destraba add column espera_su_bloqueo_id uuid;
alter table dicho_de_quien_destraba add constraint dicho_de_quien_destraba_espera_su_bloqueo
  foreign key (workspace_id, espera_su_bloqueo_id)
  references blocker(workspace_id, id) on delete cascade;

alter table dicho_de_quien_destraba drop constraint dicho_de_quien_destraba_dice_algo;
alter table dicho_de_quien_destraba add constraint dicho_de_quien_destraba_dice_algo check (
  para_cuando is not null or ya_esta or lo_que_dice is not null or no_le_corresponde
  or espera_su_bloqueo_id is not null);

comment on column dicho_de_quien_destraba.espera_su_bloqueo_id is
  'El Motor (C-5, decisión 6): quien destraba dice que está trabado con algo suyo, este bloqueo, del mismo espacio. Enlaza los dos bloqueos: lo que pasa con éste le llega, como información, a quien espera más abajo.';

commit;
