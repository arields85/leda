\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0041_aislamiento_de_la_configuracion.sql.
--
-- Borra la política `aislamiento_espacio` de `work_calendar`, `holiday`, `persona_config`,
-- `workspace_version` y `model_config`, y les quita la `row level security`. No toca datos ni
-- privilegios. Deshacerla vuelve a dejar el aislamiento de esas cinco tablas en manos del
-- `where workspace_id = %s` de cada lector: sólo con la decisión registrada.
begin;
set search_path = leda, public;

drop policy if exists aislamiento_espacio on work_calendar;
alter table work_calendar no force row level security;
alter table work_calendar disable row level security;

drop policy if exists aislamiento_espacio on holiday;
alter table holiday no force row level security;
alter table holiday disable row level security;

drop policy if exists aislamiento_espacio on persona_config;
alter table persona_config no force row level security;
alter table persona_config disable row level security;

drop policy if exists aislamiento_espacio on workspace_version;
alter table workspace_version no force row level security;
alter table workspace_version disable row level security;

drop policy if exists aislamiento_espacio on model_config;
alter table model_config no force row level security;
alter table model_config disable row level security;

commit;
