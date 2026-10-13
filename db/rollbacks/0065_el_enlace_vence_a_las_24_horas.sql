\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0065_el_enlace_vence_a_las_24_horas.sql.
--
-- Devuelve `canjear_enlace_de_entrada` y el comentario de `enlace_de_entrada` a como los dejó la
-- 0057 (el enlace sin usar no vence por tiempo). No toca datos: un enlace que había vencido sin
-- usarse vuelve a servir.
begin;
set search_path = leda, public;

comment on table enlace_de_entrada is
  'ADR 0022, decisiones 4 y 12: el enlace de un solo uso para entrar a la web. Sólo el hash del token. Sirve una vez (canjeado_en); sin vencimiento por tiempo; queda anulado si se emite otro para la misma persona o se cortan sus sesiones. leda_app no tiene privilegios: sólo execute sobre sus funciones.';

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
    -- no la encuentra sin canjear.
    update enlace_de_entrada set canjeado_en = now()
     where id = enlace.id and canjeado_en is null and anulado_en is null;
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
