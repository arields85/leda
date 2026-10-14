\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0071_la_carga_del_equipo.sql. Quien se eligió al cargar una tarea para revisarla
-- deja de trabarla si ya no está en el equipo (porción J4b de `odd/tasks/plataforma-jerarquias.md`;
-- revisión de la J4a, advertencia "quién revisa queda fijo").
--
-- Desde la 0071, cada tarea puede guardar quién la revisa (`task.revisor_membership_id`), elegido al
-- cargarla, y `quien_revisa_la_tarea` lo lee primero. Si esa persona deja el equipo (su membresía
-- deja de estar activa), la aprobación esperaba a alguien que ya no puede darla, sin que nadie lo
-- supiera. Ahora:
--
-- - **Si quien se eligió ya no está activo**, revisa quien aprueba el trabajo de quien era la tarea
--   (la regla de siempre, la de antes de la 0071), si esa persona está activa.
-- - **Si tampoco hay nadie activo por esa regla** (por ejemplo, la tarea propia de Dirección, D13,
--   que no tiene a nadie arriba), sigue siendo quien se eligió: la aprobación sigue exigiéndose,
--   nunca se saltea (constitución §3 y §11). El motor no lo deja en silencio: la escalera de las
--   decisiones registra un incidente para la administración, una vez por tarea y por persona, en
--   lugar de recordarle la decisión a quien ya no está (`motor/escalera.py`).
--
-- Reasignar quién revisa (por ejemplo, cuando la persona sigue en el equipo pero deja de ser
-- referente) es de la J7, con las jerarquías desde la web. Se deshace con
-- `db/rollbacks/0072_quien_revisa_sigue_activo.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0072 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0071 está aplicada y la 0072 no.
do $$ begin
  if to_regclass('leda.reapertura_de_tarea') is null then
    raise exception '0072 preflight failed: falta la 0071';
  end if;
  if position('elegido_activo' in pg_get_functiondef('leda.quien_revisa_la_tarea(uuid)'::regprocedure)) > 0 then
    raise exception '0072 ya está aplicada.';
  end if;
end $$;

-- Quién revisa una tarea: el elegido al cargarla, si sigue activo (migraciones 0071 y 0072); si no,
-- o si no se eligió a nadie, la regla de siempre (quien aprueba el trabajo de quien era la tarea),
-- si esa persona está activa; si nadie de las dos está activo, el elegido, que sigue exigiéndose.
create or replace function quien_revisa_la_tarea(p_task uuid)
returns uuid
language sql stable set search_path = leda, public, pg_temp as $$
  select case
           when t.revisor_membership_id is null then m.aprobador_membership_id
           when elegido_activo.id is not null then t.revisor_membership_id
           when regla_activa.id is not null then regla_activa.id
           else t.revisor_membership_id
         end
    from task t
    left join membership m on m.id = coalesce(t.era_de_membership_id, t.responsable_membership_id)
    left join membership elegido_activo
           on elegido_activo.id = t.revisor_membership_id and elegido_activo.activo
    left join membership regla_activa
           on regla_activa.id = m.aprobador_membership_id and regla_activa.activo
   where t.id = p_task;
$$;

commit;
