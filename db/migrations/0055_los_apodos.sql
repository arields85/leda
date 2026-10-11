\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0054_la_respuesta_del_bot_de_administracion.sql. Los apodos (ADR 0020, aceptado
-- por el usuario el 2026-10-11; conversación 47).
--
-- Leda reconoce a una persona del equipo cuando la nombran por un apodo: lo aprende por chat,
-- con la confirmación de una persona, y la plataforma los muestra y los deja agregar, cambiar y
-- borrar. Lo guarda:
--
-- - `apodo`: cómo le dicen en el equipo a un integrante (`membership_id`), con las palabras
--   normalizadas como el código compara los nombres (sin mayúsculas ni acentos, separadas por un
--   espacio), quién lo enseñó (`ensenado_por_app_user_id`), cuándo (`at`) y por qué canal
--   (`chat` o `plataforma`). Una persona puede tener varios, y un apodo puede ser de dos
--   personas: vigente, uno por persona y apodo. Un apodo no se borra: se deja de usar, una vez,
--   con quién y cuándo (`borrado_en`, `borrado_por_app_user_id`; `vigilar_apodo`).
--
-- El apodo sirve para entender, nunca para hablar ni para conceder nada (ADR 0020, decisiones 5
-- y 7): ninguna regla de autoridad lo lee. Cada apodo aprendido queda además en `audit_log`, con
-- quién lo enseñó y el canal (decisión 8), en la misma transacción.
--
-- Aislamiento: espacio obligatorio, RLS forzado con su política y la persona del apodo del mismo
-- espacio (clave compuesta). `leda_app` lo lee, lo agrega y lo deja de usar; nunca lo borra. La
-- función nueva no es `security definer`: el disparador corre con el rol de quien escribe, bajo
-- la RLS de su espacio.
--
-- Se deshace con `db/rollbacks/0055_los_apodos.sql`, que se niega si hay algún apodo.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0055 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0054 está aplicada y la 0055 no.
do $$ begin
  if not exists (select 1 from information_schema.columns
                  where table_schema = 'leda' and table_name = 'admin_notice'
                    and column_name = 'es_respuesta') then
    raise exception '0055 preflight failed: falta la 0054';
  end if;
  if to_regclass('leda.apodo') is not null then
    raise exception '0055 ya está aplicada.';
  end if;
end $$;

-- Cómo le dicen en el equipo a un integrante (ADR 0020).
create table apodo (
  id                        uuid primary key default gen_random_uuid(),
  workspace_id              uuid not null references workspace(id) on delete cascade,
  membership_id             uuid not null,
  apodo                     text not null,
  ensenado_por_app_user_id  uuid not null references app_user(id),
  canal                     text not null check (canal in ('chat', 'plataforma')),
  at                        timestamptz not null,
  borrado_en                timestamptz,
  borrado_por_app_user_id   uuid references app_user(id),
  constraint apodo_de_un_integrante
    foreign key (workspace_id, membership_id) references membership(workspace_id, id)
    on delete cascade,
  -- Las palabras normalizadas, separadas por un solo espacio: nada que actúe como comodín.
  constraint apodo_normalizado check (apodo ~ '^[^ ]+( [^ ]+)*$'),
  constraint apodo_borrado check ((borrado_en is null) = (borrado_por_app_user_id is null))
);

-- Vigente, uno por persona y apodo; el mismo apodo puede ser de dos personas.
create unique index apodo_vigente on apodo (workspace_id, membership_id, apodo)
  where borrado_en is null;

comment on table apodo is
  'El Motor (ADR 0020): cómo le dicen en el equipo a un integrante, con las palabras normalizadas como el código compara los nombres; quién lo enseñó, cuándo y por qué canal (chat o plataforma). Sirve para entender, nunca para hablar ni para conceder nada. Sólo se deja de usar, una vez; nunca se borra.';

-- Un apodo nace vigente y lo único que cambia después es dejarlo de usar, una vez, con quién y
-- cuándo (migración 0055).
create or replace function vigilar_apodo() returns trigger as $$
begin
  if tg_op = 'INSERT' then
    if new.borrado_en is not null then
      raise exception 'apodo: un apodo se aprende vigente';
    end if;
    return new;
  end if;
  if new.workspace_id is distinct from old.workspace_id
     or new.membership_id is distinct from old.membership_id
     or new.apodo is distinct from old.apodo
     or new.ensenado_por_app_user_id is distinct from old.ensenado_por_app_user_id
     or new.canal is distinct from old.canal
     or new.at is distinct from old.at then
    raise exception 'apodo: lo aprendido no cambia';
  end if;
  if old.borrado_en is not null and new is distinct from old then
    raise exception 'apodo: ya se dejó de usar';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_vigilar_apodo
  before insert or update on apodo
  for each row execute function vigilar_apodo();

alter table apodo enable row level security;
alter table apodo force row level security;
create policy aislamiento_espacio on apodo
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
grant all privileges on apodo to leda_owner, leda_admin;
grant select, insert, update on apodo to leda_app;

commit;
