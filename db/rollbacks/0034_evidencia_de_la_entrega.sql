\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0034_evidencia_de_la_entrega.sql.
--
-- Borra `archivo_de_tarea` y `evidencia_retirada`, las columnas nuevas de `evidence` (clase,
-- texto, archivo y lo que cubre) y de `task_evidence_policy` (`tipos`), sus disparadores y
-- funciones, y devuelve `evidencia_pendiente` a la regla de la 0014 (alcanza con una evidencia
-- cualquiera del ciclo vigente). `leda_app` vuelve a tener `update` y `delete` sobre `evidence`.
--
-- Se niega a correr si se perdería algo que la regla vieja no sabe representar: una evidencia
-- que apunta a un archivo, un retiro o un archivo dicho de una tarea. Antes de deshacerla en una
-- base con datos, `pg_dump` de esas tablas y borrar esas filas a mano.
begin;
set search_path = leda, public;

do $$ begin
  if exists (select 1 from evidence where archivo_id is not null)
     or exists (select 1 from evidencia_retirada)
     or exists (select 1 from archivo_de_tarea) then
    raise exception '0034 rollback refused: hay evidencias con archivo, retiros o archivos '
                    'dichos de una tarea; respaldalos y borralos primero';
  end if;
end $$;

drop table if exists archivo_de_tarea;
drop table if exists evidencia_retirada;

drop trigger if exists trg_rechazar_cambios_de_evidencia on evidence;
drop trigger if exists trg_exigir_clase_de_la_evidencia on evidence;
drop trigger if exists trg_exigir_referencias_del_espacio on evidence;
drop function if exists rechazar_cambios_de_evidencia();
drop function if exists exigir_clase_de_la_evidencia();

create or replace function evidencia_pendiente(p_task uuid)
returns boolean as $$
  select array_length(t.evidencia_requerida, 1) is not null
     and not exists (
       select 1 from evidence e
        where e.task_id = t.id
          and e.at > coalesce(
            (select max(r.at) from approval r
              where r.sujeto_tipo = 'tarea' and r.sujeto_id = t.id
                and r.decision = 'rechazado'),
            '-infinity'::timestamptz))
    from task t where t.id = p_task;
$$ language sql stable;

drop function if exists tipos_de_evidencia_que_faltan(uuid, jsonb);
drop function if exists tipos_que_acepta_la_clase(uuid, text);
drop function if exists clases_de_un_tipo_de_evidencia(uuid, text);

alter table evidence
  drop constraint if exists evidence_clase_y_contenido,
  drop constraint if exists evidence_clase,
  drop constraint if exists evidence_archivo,
  drop constraint if exists evidence_task_workspace,
  drop constraint if exists evidence_workspace_id_unique,
  drop column if exists cubre,
  drop column if exists archivo_id,
  drop column if exists texto,
  drop column if exists clase;
comment on column evidence.tipo is null;

alter table task_evidence_policy
  drop constraint if exists task_evidence_policy_tipos,
  drop column if exists tipos;
drop function if exists tipos_de_evidencia_validos(jsonb);

grant update, delete on evidence to leda_app;

commit;
