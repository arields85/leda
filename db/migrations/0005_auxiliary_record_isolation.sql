\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0004_function_ownership.sql. Closes the last isolation gap in
-- the auxiliary records: audit_log, incident and absence all granted insert to
-- leda_app with no isolation policy, so a connection bound to one workspace
-- could attribute an audit entry, an incident or an absence to another.
--
-- The audit log is the record a client is shown as evidence. If another client
-- can write into it, it stops being evidence.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0005 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'leda_owner') then
    raise exception '0005 requires 0004_function_ownership.sql';
  end if;
end $$;

-- Preflight before any DDL: every absence must resolve to its membership, or
-- the backfill below would leave rows this migration cannot attribute.
do $$
declare huerfanas bigint;
begin
  select count(*) into huerfanas
    from absence a left join membership m on m.id = a.membership_id
   where m.id is null;
  if huerfanas > 0 then
    raise exception '0005 preflight failed: % absence row(s) without a membership', huerfanas;
  end if;
end $$;

-- --- absence: no tenía espacio propio; se deriva de la membresía ----------

alter table absence add column workspace_id uuid references workspace(id)
  on delete cascade;
update absence a set workspace_id = m.workspace_id
  from membership m where m.id = a.membership_id;
alter table absence alter column workspace_id set not null;
create index absence_ws on absence (workspace_id, membership_id);

-- Privilegios del llamador a propósito, igual que en 0003: así la RLS esconde
-- la membresía de otro espacio, el select no la encuentra, y una ajena falla
-- idéntico a una inexistente. Decir "no tenés permiso" confirmaría que existe.
create or replace function derivar_espacio_ausencia() returns trigger as $$
begin
  select m.workspace_id into new.workspace_id
    from membership m where m.id = new.membership_id;
  if new.workspace_id is null then
    raise exception 'absence: no existe la membresía %', new.membership_id;
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_derivar_espacio_ausencia
  before insert on absence
  for each row execute function derivar_espacio_ausencia();

-- --- audit_log e incident: el espacio lo fija la sesión, no quien escribe --

create or replace function derivar_espacio_registro() returns trigger as $$
declare actual text := nullif(current_setting('leda.workspace_id', true), '');
begin
  -- Cuando la sesión declara un espacio, ése manda: no se acepta el que
  -- aporte quien escribe. Cuando no lo declara --la conexión administrativa--
  -- se conserva lo suministrado, que es como se registran los hechos de
  -- alcance global que no pertenecen a ningún cliente.
  if actual is not null then
    new.workspace_id := actual::uuid;
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_derivar_espacio_auditoria
  before insert on audit_log
  for each row execute function derivar_espacio_registro();

create trigger trg_derivar_espacio_incidente
  before insert on incident
  for each row execute function derivar_espacio_registro();

-- --- Políticas ------------------------------------------------------------

alter table absence enable row level security;
alter table absence force row level security;
create policy aislamiento_espacio on absence
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

-- `audit_log` e `incident` admiten espacio nulo para los hechos de alcance
-- global, que sólo origina la conexión administrativa. Una fila sin espacio no
-- queda atribuida a ningún cliente, así que no puede falsificar su registro.
alter table audit_log enable row level security;
alter table audit_log force row level security;
create policy aislamiento_espacio on audit_log
  using (workspace_id is null
         or workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

alter table incident enable row level security;
alter table incident force row level security;
create policy aislamiento_espacio on incident
  using (workspace_id is null
         or workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

commit;
