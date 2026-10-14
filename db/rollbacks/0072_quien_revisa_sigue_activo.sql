\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0072_quien_revisa_sigue_activo.sql.
--
-- Devuelve `quien_revisa_la_tarea` a como la dejó la 0071: el elegido al cargar la tarea, esté o no
-- activo, y si no se eligió a nadie, la regla de siempre. No se pierde ningún dato: la 0072 sólo
-- cambia cómo se lee quién revisa.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0072 rollback requires an unmodified UTF-8 input stream';
  end if;
end $$;

create or replace function quien_revisa_la_tarea(p_task uuid)
returns uuid
language sql stable set search_path = leda, public, pg_temp as $$
  select coalesce(t.revisor_membership_id, m.aprobador_membership_id)
    from task t
    left join membership m on m.id = coalesce(t.era_de_membership_id, t.responsable_membership_id)
   where t.id = p_task;
$$;

commit;
