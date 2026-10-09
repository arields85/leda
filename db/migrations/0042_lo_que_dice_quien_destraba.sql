\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0041_aislamiento_de_la_configuracion.sql. La persecución del bloqueo, porción 1
-- de la C-5 (`odd/tasks/fase-c.md`, decisión 4; ADR 0017, decisión 3a; conversación 32).
--
-- Cuando la persona trabada dice quién la destraba, Leda le pregunta a esa persona para cuándo lo
-- resuelve. Lo que contesta es un hecho del bloqueo: `dicho_de_quien_destraba`, sobre la fila de
-- `blocker_unblocker` que la nombró (para cuándo, que ya está y sus palabras: al menos uno),
-- atribuido a quien lo dijo. Sólo se agrega: una respuesta nueva es otra fila. Un "ya está" no
-- cierra el bloqueo: lo cierra la persona trabada (`resolver_bloqueo`).
--
-- `blocker_unblocker` gana una restricción única `(workspace_id, id)` para la clave foránea con el
-- espacio. Aislamiento: espacio obligatorio, RLS forzado con su política, y quien lo dijo es del
-- mismo espacio (`exigir_referencias_del_espacio`). `leda_app` sólo agrega y lee.
--
-- Se deshace con `db/rollbacks/0042_lo_que_dice_quien_destraba.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0042 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (select 1 from pg_policy where polrelid = 'leda.model_config'::regclass) then
    raise exception '0042 requires 0041_aislamiento_de_la_configuracion.sql';
  end if;
  if to_regclass('leda.dicho_de_quien_destraba') is not null then
    raise exception '0042 ya está aplicada.';
  end if;
end $$;

alter table blocker_unblocker
  add constraint blocker_unblocker_workspace_id_unique unique (workspace_id, id);

create table dicho_de_quien_destraba (
  id                       uuid primary key default gen_random_uuid(),
  workspace_id             uuid not null references workspace(id) on delete cascade,
  blocker_unblocker_id     uuid not null,
  dicho_por_membership_id  uuid not null,
  para_cuando              date,
  ya_esta                  boolean not null default false,
  lo_que_dice              text check (btrim(lo_que_dice) <> ''),
  at                       timestamptz not null,
  constraint dicho_de_quien_destraba_destraba
    foreign key (workspace_id, blocker_unblocker_id)
    references blocker_unblocker(workspace_id, id) on delete cascade,
  constraint dicho_de_quien_destraba_said_by
    foreign key (dicho_por_membership_id)
    references membership(id) on delete cascade,
  constraint dicho_de_quien_destraba_dice_algo check (
    para_cuando is not null or ya_esta or lo_que_dice is not null)
);

create index dicho_de_quien_destraba_de on dicho_de_quien_destraba (blocker_unblocker_id, at desc);

comment on table dicho_de_quien_destraba is
  'El Motor (C-5, decisión 4; ADR 0017, 3a): lo que dice quien destraba un bloqueo cuando Leda le pregunta -- para cuándo, que ya está o sus palabras, al menos uno --, quién lo dijo y cuándo. No cierra el bloqueo. Sólo se agrega.';

create trigger trg_exigir_referencias_del_espacio
  before insert or update on dicho_de_quien_destraba
  for each row execute function exigir_referencias_del_espacio(
    'dicho_por_membership_id', 'membership');

grant all privileges on dicho_de_quien_destraba to leda_owner, leda_admin;

alter table dicho_de_quien_destraba enable row level security;
alter table dicho_de_quien_destraba force row level security;
create policy aislamiento_espacio on dicho_de_quien_destraba
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
grant select, insert, update, delete on dicho_de_quien_destraba to leda_app;
revoke update, delete on dicho_de_quien_destraba from leda_app;

commit;
