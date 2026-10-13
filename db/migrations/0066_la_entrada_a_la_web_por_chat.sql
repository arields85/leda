\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0065_el_enlace_vence_a_las_24_horas.sql. La entrada a la plataforma web por chat
-- (ADR 0022, decisión 4; decisiones del usuario del 2026-10-12; tarea A-3 de
-- `odd/tasks/acceso-por-chat.md`, decisiones técnicas 1 a 3 del coordinador).
--
-- - `message_outbox_entrada_web`: la fila de la salida que lleva al final el enlace de entrada a
--   la web de una persona, como `message_outbox_enlace` lleva el de la página de una tarea (cuyo
--   `task_id` es obligatorio). La salida guarda sólo esta marca: el despachador emite el enlace al
--   mandar (`emitir_enlace_de_entrada`, dentro del punto de retorno del envío) y la base guarda
--   sólo su hash. `es_ofrecimiento` dice si es el ofrecimiento de una sola vez (tarea A-4) y no un
--   pedido de la persona. Un mensaje lleva un solo enlace: la salida rechaza las dos marcas
--   juntas. `leda_app` agrega y lee; `leda_admin` también agrega (la bienvenida se escribe desde
--   la conexión administrativa).
-- - `ofrecimiento_web`: si a una persona ya se le ofreció la entrada a la web (decisión 2 del
--   usuario: una sola vez). Se reserva al armar el turno (`reservado_en`) y queda ofrecido al
--   mandar (`ofrecido_en`); si el envío falla y no se reintenta, se libera. Lo usa la A-4.
-- - `entro_a_la_web(membresía)`: si la persona entró alguna vez a la web (canjeó un enlace o tuvo
--   una sesión). `tiene_un_enlace_sin_usar(membresía)`: si tiene un enlace emitido que nadie usó
--   ni se anuló (vencido o no), el que un enlace nuevo deja sin servir. `leda_app` no lee
--   `enlace_de_entrada` ni `sesion_web`: las dos son `security definer` con dueño `leda_owner`,
--   que no saltea la RLS, así que responden sólo por el espacio de quien llama (una membresía de
--   otro espacio da `false`, igual que una que no existe).
-- - `cortar_sesiones_de_membresia`: el corte deja siempre su fila en `audit_log`
--   (`cortar_acceso_web`, sobre la membresía, con el motivo, quién, cuántas sesiones cortó y si
--   anuló un enlace sin usar), también si la persona no tenía ninguna sesión abierta (antes, anular
--   sólo el enlace no dejaba rastro). Las filas de cada sesión cortada (`cortar_sesion_web`) siguen
--   como estaban. Una membresía de otro espacio no se encuentra: no corta ni audita nada. Misma
--   firma, dueño y privilegios.
--
-- Aislamiento: las dos tablas con `workspace_id` obligatorio, `row level security` forzado y la
-- política de siempre. No crea, altera ni borra roles. Se deshace con
-- `db/rollbacks/0066_la_entrada_a_la_web_por_chat.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0066 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0065 está aplicada y la 0066 no.
do $$ begin
  if to_regprocedure('leda.canjear_enlace_de_entrada(text, text)') is null
     or position('24 hours' in pg_get_functiondef(
          'leda.canjear_enlace_de_entrada(text, text)'::regprocedure)) = 0 then
    raise exception '0066 preflight failed: falta la 0065';
  end if;
  if to_regclass('leda.message_outbox_entrada_web') is not null then
    raise exception '0066 ya está aplicada.';
  end if;
end $$;

create table message_outbox_entrada_web (
  id               uuid primary key default gen_random_uuid(),
  workspace_id     uuid not null references workspace(id) on delete cascade,
  outbox_id        uuid not null,
  membership_id    uuid not null,
  es_ofrecimiento  boolean not null default false,
  constraint message_outbox_entrada_web_outbox
    foreign key (workspace_id, outbox_id) references message_outbox(workspace_id, id)
    on delete cascade,
  constraint message_outbox_entrada_web_membership
    foreign key (workspace_id, membership_id) references membership(workspace_id, id)
    on delete cascade,
  constraint message_outbox_entrada_web_uno_por_fila unique (outbox_id)
);

comment on table message_outbox_entrada_web is
  'ADR 0022, decisión 4: la fila de la salida lleva al final el enlace de entrada a la web de esta persona (es_ofrecimiento: el ofrecimiento de una sola vez). El despachador lo emite al mandar; la base guarda sólo su hash (enlace_de_entrada). Sólo se agrega.';

create table ofrecimiento_web (
  workspace_id   uuid not null references workspace(id) on delete cascade,
  membership_id  uuid primary key,
  reservado_en   timestamptz not null default now(),
  ofrecido_en    timestamptz,
  constraint ofrecimiento_web_membership
    foreign key (workspace_id, membership_id) references membership(workspace_id, id)
    on delete cascade
);

comment on table ofrecimiento_web is
  'Decisión 2 del usuario (2026-10-12): la entrada a la web se le ofrece a cada persona una sola vez. Se reserva al armar el turno (reservado_en), queda ofrecida al mandar (ofrecido_en) y se libera si el envío falla sin reintento.';

grant all privileges on message_outbox_entrada_web, ofrecimiento_web to leda_owner, leda_admin;

alter table message_outbox_entrada_web enable row level security;
alter table message_outbox_entrada_web force row level security;
create policy aislamiento_espacio on message_outbox_entrada_web
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

alter table ofrecimiento_web enable row level security;
alter table ofrecimiento_web force row level security;
create policy aislamiento_espacio on ofrecimiento_web
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

-- `leda_app`: la marca del enlace de entrada, agregar y leer; el ofrecimiento, reservarlo,
-- marcarlo ofrecido y liberarlo.
revoke all on message_outbox_entrada_web, ofrecimiento_web from public;
grant select, insert on message_outbox_entrada_web to leda_app;
grant select, insert, update, delete on ofrecimiento_web to leda_app;

create or replace function entro_a_la_web(p_membership_id uuid)
returns boolean
language sql stable security definer set search_path = leda, public, pg_temp as $$
  -- La RLS acota las dos lecturas al espacio de quien llama: una membresía de otro espacio da
  -- `false`, igual que una que no existe.
  select exists (select 1 from enlace_de_entrada e
                  where e.membership_id = p_membership_id and e.canjeado_en is not null)
      or exists (select 1 from sesion_web s where s.membership_id = p_membership_id);
$$;

create or replace function tiene_un_enlace_sin_usar(p_membership_id uuid)
returns boolean
language sql stable security definer set search_path = leda, public, pg_temp as $$
  -- El que un enlace nuevo deja sin servir: emitido, sin canjear ni anular (vencido o no).
  select exists (select 1 from enlace_de_entrada e
                  where e.membership_id = p_membership_id
                    and e.canjeado_en is null and e.anulado_en is null);
$$;

create or replace function cortar_sesiones_de_membresia(
    p_membership_id uuid, p_motivo text, p_actor_app_user_id uuid)
returns integer
language plpgsql security definer set search_path = leda, public, pg_temp as $$
declare cortada record;
        cortadas integer := 0;
        espacio uuid;
        anulados integer;
        actor tipo_actor := case when p_actor_app_user_id is null then 'leda'
                                 else 'persona' end::tipo_actor;
begin
  if p_motivo is null or p_motivo not in (
       'administrador', 'perdio_el_celular', 'cerro_la_sesion', 'dejo_el_equipo') then
    raise exception 'cortar_sesiones_de_membresia: motivo desconocido';
  end if;
  -- El espacio sale de la membresía, que la RLS acota al espacio de quien llama: una membresía
  -- de otro espacio no se encuentra, y no se corta ni se audita nada.
  select m.workspace_id into espacio from membership m where m.id = p_membership_id;
  if espacio is null then
    return 0;
  end if;
  -- Con las sesiones, el enlace que estaba sin usar: si se perdió el celular, el mensaje con el
  -- enlace también.
  update enlace_de_entrada e set anulado_en = now()
   where e.membership_id = p_membership_id and e.canjeado_en is null and e.anulado_en is null;
  get diagnostics anulados = row_count;
  for cortada in
    update sesion_web s set cortada_en = now(), motivo_de_corte = p_motivo
     where s.membership_id = p_membership_id and s.cortada_en is null
    returning s.id, s.workspace_id, s.membership_id
  loop
    perform auditar_acceso_web(
      cortada.workspace_id, p_actor_app_user_id, actor, 'cortar_sesion_web', 'sesion_web',
      cortada.id,
      jsonb_build_object('motivo', p_motivo, 'membership_id', cortada.membership_id));
    cortadas := cortadas + 1;
  end loop;
  -- El corte mismo, siempre: también si no había ninguna sesión abierta (0066).
  perform auditar_acceso_web(
    espacio, p_actor_app_user_id, actor, 'cortar_acceso_web', 'membership', p_membership_id,
    jsonb_build_object('motivo', p_motivo, 'sesiones_cortadas', cortadas,
                       'enlace_anulado', anulados > 0));
  return cortadas;
end $$;

alter function entro_a_la_web(uuid) owner to leda_owner;
alter function tiene_un_enlace_sin_usar(uuid) owner to leda_owner;
alter function cortar_sesiones_de_membresia(uuid, text, uuid) owner to leda_owner;

revoke execute on function entro_a_la_web(uuid) from public;
revoke execute on function tiene_un_enlace_sin_usar(uuid) from public;
revoke execute on function cortar_sesiones_de_membresia(uuid, text, uuid) from public;
grant execute on function entro_a_la_web(uuid) to leda_app;
grant execute on function tiene_un_enlace_sin_usar(uuid) to leda_app;
grant execute on function cortar_sesiones_de_membresia(uuid, text, uuid) to leda_app;

commit;
