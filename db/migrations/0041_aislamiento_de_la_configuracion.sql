\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0040_pregunta_sin_contestar.sql. El aislamiento de la configuración de cada espacio
-- (C-3, porción 4, notas de seguridad de `odd/tasks/fase-c.md`).
--
-- `AGENTS.md` ("Invariantes vigentes"): ninguna tabla con alcance de espacio queda sin
-- `workspace_id` ni sin `row level security` forzado. Cinco tablas con `workspace_id` que
-- `leda_app` lee directamente (sólo `select`) no tenían política, y su aislamiento dependía del
-- `where workspace_id = %s` de cada lector:
--
-- - `work_calendar` y `holiday`: el calendario laboral y los feriados (`calendario.Calendario`);
-- - `persona_config`: el tono del pack (`motor.instrucciones.tono_del_espacio`);
-- - `workspace_version`: la versión del pack que firma la auditoría (`versiones.pack_hash`);
-- - `model_config`: la IA de cada espacio (`motor.ia_real.desde_base`). Admite espacio nulo para
--   el modelo global (`ambito = 'global'`), que ve todo espacio: la política es la de `audit_log`
--   e `incident`, nulo o el espacio activo.
--
-- Todas las escrituras son de la conexión administrativa (`leda_admin`, `bypassrls`), y ninguna
-- función `security definer` las lee, así que la política no cambia lo que hace ninguna. Los
-- privilegios de `leda_app` no cambian: sigue con `select` solamente.
--
-- Las otras cinco tablas con `workspace_id` y sin política (`acceso_tablero`, `activation_token`,
-- `admin_notice`, `conversation_access_log` y `learning`) no se tocan: ni `leda_app` ni
-- `leda_gateway` tienen privilegios sobre ellas. Son excepciones declaradas, con su motivo, en
-- `tests/garantias/test_aislamiento.py`.
--
-- Se deshace con `db/rollbacks/0041_aislamiento_de_la_configuracion.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0041 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: las cinco tablas existen y ninguna tiene todavía una política.
do $$ begin
  if exists (select 1 from unnest(array['work_calendar', 'holiday', 'persona_config',
                                        'workspace_version', 'model_config']) t
              where to_regclass('leda.' || t) is null) then
    raise exception '0041 preflight failed: falta alguna de las tablas de configuración';
  end if;
  if exists (select 1 from pg_policy
              where polrelid in ('leda.work_calendar'::regclass, 'leda.holiday'::regclass,
                                 'leda.persona_config'::regclass,
                                 'leda.workspace_version'::regclass,
                                 'leda.model_config'::regclass)) then
    raise exception '0041 preflight failed: alguna tabla de configuración ya tiene política';
  end if;
end $$;

alter table work_calendar enable row level security;
alter table work_calendar force row level security;
create policy aislamiento_espacio on work_calendar
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

alter table holiday enable row level security;
alter table holiday force row level security;
create policy aislamiento_espacio on holiday
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

alter table persona_config enable row level security;
alter table persona_config force row level security;
create policy aislamiento_espacio on persona_config
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

alter table workspace_version enable row level security;
alter table workspace_version force row level security;
create policy aislamiento_espacio on workspace_version
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

alter table model_config enable row level security;
alter table model_config force row level security;
create policy aislamiento_espacio on model_config
  using (workspace_id is null
         or workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);

commit;
