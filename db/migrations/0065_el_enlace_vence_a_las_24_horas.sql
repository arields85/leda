\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0064_hoy_no_despues_del_cierre.sql. El enlace de entrada a la web que nadie usó
-- vence a las 24 horas de emitido (decisión del usuario del 2026-10-12, precisión de la decisión 4
-- del ADR 0022; tarea A-2 de `odd/tasks/acceso-por-chat.md`).
--
-- La 0057 dejó el enlace sin vencimiento por tiempo. Ahora:
--
-- - `canjear_enlace_de_entrada`: un enlace emitido hace 24 horas o más no se canjea. Para quien
--   llama es lo mismo que un enlace ya usado o anulado: devuelve `null`, no abre ninguna sesión
--   y no deja fila de auditoría (la 0057 no audita un canje que no abre). El vencimiento no se
--   guarda: se deduce de `emitido_en`, así que el enlace vencido sigue siendo el que estaba sin
--   usar y pedir otro lo anula como siempre. Se decide dentro del mismo `update` del canje, que
--   toma el candado de la fila: dos canjes a la vez siguen abriendo una sola sesión.
-- - La sesión que abrió un enlace no vence (ADR 0022, decisión 12): esto no la toca.
-- - La puerta de administración (`canjear_enlace_de_administracion`, 0061 y 0063) no cambia: su
--   enlace sale por la consola y la decisión es sobre el que Leda manda por chat.
--
-- Misma firma, dueño y privilegios. Se deshace con
-- `db/rollbacks/0065_el_enlace_vence_a_las_24_horas.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0065 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0064 está aplicada (y la 0057).
do $$ begin
  if to_regprocedure('leda.canjear_enlace_de_entrada(text, text)') is null
     or to_regclass('leda.enlace_de_entrada') is null then
    raise exception '0065 preflight failed: falta la 0057';
  end if;
  if to_regprocedure('leda.opciones_de_la_carga(text, uuid, timestamptz)') is null then
    raise exception '0065 preflight failed: falta la 0064';
  end if;
end $$;

comment on table enlace_de_entrada is
  'ADR 0022, decisiones 4 y 12: el enlace de un solo uso para entrar a la web. Sólo el hash del token. Sirve una vez (canjeado_en); el que nadie usó vence a las 24 horas de emitido (0065), sin marcarlo; queda anulado si se emite otro para la misma persona o se cortan sus sesiones. leda_app no tiene privilegios: sólo execute sobre sus funciones.';

create or replace function canjear_enlace_de_entrada(
    p_token_hash text, p_sesion_token_hash text)
returns uuid
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare previo text := coalesce(current_setting('leda.workspace_id', true), '');
        enlace enlace_de_entrada%rowtype;
        persona uuid;
        nueva uuid;
begin
  if p_token_hash is null or p_token_hash !~ '^[0-9a-f]{64}$'
     or p_sesion_token_hash is null or p_sesion_token_hash !~ '^[0-9a-f]{64}$' then
    return null;
  end if;
  perform set_config('leda.token_de_entrada', p_token_hash, true);
  select * into enlace from enlace_de_entrada e where e.token_hash = p_token_hash;
  perform set_config('leda.token_de_entrada', '', true);
  if enlace.id is null then
    return null;
  end if;
  perform set_config('leda.workspace_id', enlace.workspace_id::text, true);
  select m.app_user_id into persona from membership m
   where m.id = enlace.membership_id and m.activo;
  if persona is not null then
    -- Una sola vez: si llegan dos canjes a la vez, el segundo espera el candado de la fila y ya
    -- no la encuentra sin canjear. Y antes de las 24 horas de emitido (0065): vencido, no abre,
    -- igual que uno ya usado.
    update enlace_de_entrada set canjeado_en = now()
     where id = enlace.id and canjeado_en is null and anulado_en is null
       and emitido_en > now() - interval '24 hours';
    if found then
      insert into sesion_web (workspace_id, membership_id, enlace_id, token_hash)
           values (enlace.workspace_id, enlace.membership_id, enlace.id, p_sesion_token_hash)
        returning id into nueva;
      perform auditar_acceso_web(
        enlace.workspace_id, persona, 'persona', 'canjear_enlace_de_entrada', 'sesion_web',
        nueva, jsonb_build_object('enlace_id', enlace.id,
                                  'membership_id', enlace.membership_id));
    end if;
  end if;
  perform set_config('leda.workspace_id', previo, true);
  return nueva;
end $$;

alter function canjear_enlace_de_entrada(text, text) owner to leda_owner;
revoke execute on function canjear_enlace_de_entrada(text, text) from public;
grant execute on function canjear_enlace_de_entrada(text, text) to leda_app;

commit;
