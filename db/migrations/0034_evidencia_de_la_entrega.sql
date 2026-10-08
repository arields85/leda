\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0033_archivos_recibidos.sql. La evidencia de la entrega y la política por tipo
-- (ADR 0019, decisiones 3 a 5; segunda porción).
--
-- - `evidence` guarda la clase de cada pieza (`texto`, `imagen`, `archivo` o `enlace`), que la
--   fija el código por el contenido y nunca la IA; el texto, si es texto; el archivo, si es una
--   imagen o un archivo (clave foránea con el espacio a `archivo`); y qué tipos de la política
--   cubre (`cubre`), que la persona vio en la vista previa de la entrega. Un disparador exige que
--   una pieza `imagen` apunte a una imagen y una `archivo` a un archivo que no lo es. La tarea
--   de una evidencia es del mismo espacio (clave foránea compuesta) y quien la entregó también.
--   `tipo` queda por las filas de antes: en las nuevas es igual a la clase.
-- - `evidencia_retirada`: el retiro de una pieza ("no, esa foto no era"). Sólo se agrega: una
--   pieza retirada no se borra, deja de contar para la política.
-- - `archivo_de_tarea`: lo que la persona dijo que es de una tarea antes de entregarla (una foto
--   del martes, "es del PLC"). No es evidencia: la vista previa de la entrega lo muestra y entra
--   sólo si la persona lo deja (ADR 0019, decisión 4).
-- - Inmutabilidad: `leda_app` sólo agrega y lee las tres tablas, y un disparador rechaza
--   cualquier cambio o borrado de una evidencia o de un retiro, también desde la conexión
--   administrativa (como los eventos de estado).
-- - `task_evidence_policy.tipos`: por cada tipo que pide la política, las clases que acepta y
--   cómo se dice en palabras de todos los días; dato del pack, versionado con la política. Las
--   filas que ya existen quedan con `{}` hasta que se vuelva a importar el pack: mientras tanto
--   ningún tipo se cubre (falla cerrado).
-- - `tipos_de_evidencia_que_faltan(tarea, piezas)`: la única fuente de "qué falta": cada tipo
--   pedido tiene que tener una pieza propia del ciclo vigente (después del último pedido de
--   cambios), no retirada, de una clase que ese tipo acepta. `evidencia_pendiente` pasa a ser
--   "falta alguno"; el cierre (`motivo_no_cierra_tarea`) la sigue usando, así que aprobar sigue
--   exigiendo la política completa.
-- - Aislamiento: `row level security` forzado con la política de siempre en las dos tablas
--   nuevas; sus referencias son del mismo espacio (claves foráneas compuestas y
--   `exigir_referencias_del_espacio()`). Ninguna función nueva es `security definer`.
--
-- Las filas de `evidence` de antes pasan a la clase `enlace` si su `uri` es un enlace y a
-- `texto` si no, con su texto, y sin ningún tipo cubierto: no se sabe qué cubrían.
--
-- Se deshace con `db/rollbacks/0034_evidencia_de_la_entrega.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0034 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('leda.archivo') is null then
    raise exception '0034 requires 0033_archivos_recibidos.sql';
  end if;
  if to_regclass('leda.evidencia_retirada') is not null then
    raise exception '0034 ya está aplicada.';
  end if;
  -- La clave foránea compuesta de la tarea se niega a nacer con una evidencia que apunta a
  -- una tarea de otro espacio: se aborta antes del DDL, con el motivo.
  if exists (select 1 from evidence e join task t on t.id = e.task_id
              where t.workspace_id <> e.workspace_id) then
    raise exception '0034 preflight failed: una evidencia apunta a una tarea de otro espacio';
  end if;
end $$;

-- --- La política por tipo ------------------------------------------------------------------

create or replace function tipos_de_evidencia_validos(p_tipos jsonb) returns boolean as $$
  select jsonb_typeof(p_tipos) = 'object'
     and not exists (
       select 1 from jsonb_each(p_tipos) t
        where jsonb_typeof(t.value) <> 'object'
           or jsonb_typeof(t.value -> 'clases') <> 'array'
           or jsonb_array_length(t.value -> 'clases') = 0
           or exists (select 1 from jsonb_array_elements(t.value -> 'clases') c
                       where jsonb_typeof(c) <> 'string'
                          or c #>> '{}' not in ('texto', 'imagen', 'archivo', 'enlace'))
           or jsonb_typeof(t.value -> 'en_palabras') <> 'string'
           or btrim(t.value ->> 'en_palabras') = '');
$$ language sql immutable;

alter table task_evidence_policy
  add column tipos jsonb not null default '{}'::jsonb,
  add constraint task_evidence_policy_tipos check (tipos_de_evidencia_validos(tipos));

comment on column task_evidence_policy.tipos is
  'ADR 0019, decisión 5: por cada tipo de la política, las clases de evidencia que acepta (texto, imagen, archivo, enlace) y cómo se dice en palabras de todos los días. Dato del pack; cambia la versión de la política.';

-- --- La evidencia --------------------------------------------------------------------------

alter table evidence
  add column clase text,
  add column texto text,
  add column archivo_id uuid,
  add column cubre text[] not null default '{}';

update evidence
   set clase = case when uri ~* '^https?://' then 'enlace' else 'texto' end,
       texto = case when uri ~* '^https?://' then null else uri end;

alter table evidence
  alter column clase set not null,
  add constraint evidence_workspace_id_unique unique (workspace_id, id),
  add constraint evidence_task_workspace
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade,
  add constraint evidence_archivo
    foreign key (workspace_id, archivo_id) references archivo(workspace_id, id),
  add constraint evidence_clase check (clase in ('texto', 'imagen', 'archivo', 'enlace')),
  add constraint evidence_clase_y_contenido check (
    case clase
      when 'texto' then archivo_id is null
      when 'enlace' then archivo_id is null and uri is not null
      else archivo_id is not null
    end);

comment on column evidence.clase is
  'ADR 0019, decisión 5: texto, imagen, archivo o enlace. La fija el código por el contenido, nunca la IA; la de un archivo la comprueba un disparador contra archivo.clase.';
comment on column evidence.cubre is
  'ADR 0019, decisión 5: los tipos de la política que cubre esta pieza, como los vio la persona en la vista previa de la entrega. Un texto puede cubrir varios.';
comment on column evidence.tipo is
  'Legado: en las filas nuevas es igual a la clase. Los tipos de la política que cubre una pieza están en cubre.';

create table evidencia_retirada (
  id                          uuid primary key default gen_random_uuid(),
  workspace_id                uuid not null references workspace(id) on delete cascade,
  evidence_id                 uuid not null,
  retirada_por_membership_id  uuid not null references membership(id),
  motivo                      text,
  at                          timestamptz not null default clock_timestamp(),
  constraint evidencia_retirada_evidence
    foreign key (workspace_id, evidence_id) references evidence(workspace_id, id)
    on delete cascade,
  constraint evidencia_retirada_una_vez unique (evidence_id)
);

create table archivo_de_tarea (
  id                       uuid primary key default gen_random_uuid(),
  workspace_id             uuid not null references workspace(id) on delete cascade,
  archivo_id               uuid not null,
  task_id                  uuid not null,
  dicho_por_membership_id  uuid not null references membership(id),
  at                       timestamptz not null,
  constraint archivo_de_tarea_archivo
    foreign key (workspace_id, archivo_id) references archivo(workspace_id, id),
  constraint archivo_de_tarea_task
    foreign key (workspace_id, task_id) references task(workspace_id, id) on delete cascade
);

create index archivo_de_tarea_de on archivo_de_tarea (task_id, at);

comment on table evidencia_retirada is
  'ADR 0019, decisión 3: una pieza de evidencia retirada por quien la entregó, mientras la tarea no está aprobada. Sólo se agrega; la evidencia no se borra y deja de contar para la política.';
comment on table archivo_de_tarea is
  'ADR 0019, decisión 4: un archivo que la persona dijo que es de una tarea antes de entregarla. No es evidencia: la vista previa de la entrega lo muestra y entra sólo si la persona lo deja.';

create trigger trg_exigir_referencias_del_espacio
  before insert or update on evidence
  for each row execute function exigir_referencias_del_espacio(
    'entregado_por', 'membership');
create trigger trg_exigir_referencias_del_espacio
  before insert or update on evidencia_retirada
  for each row execute function exigir_referencias_del_espacio(
    'retirada_por_membership_id', 'membership');
create trigger trg_exigir_referencias_del_espacio
  before insert or update on archivo_de_tarea
  for each row execute function exigir_referencias_del_espacio(
    'dicho_por_membership_id', 'membership');

create or replace function exigir_clase_de_la_evidencia() returns trigger as $$
declare
  del_archivo text;
begin
  if new.archivo_id is not null and new.clase in ('imagen', 'archivo') then
    select clase into del_archivo from archivo
     where workspace_id = new.workspace_id and id = new.archivo_id;
    -- Un archivo que no es de este espacio lo rechaza la clave foránea.
    if del_archivo is not null
       and (del_archivo = 'imagen') is distinct from (new.clase = 'imagen') then
      raise exception 'evidence: la clase % no es la del archivo', new.clase;
    end if;
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_exigir_clase_de_la_evidencia
  before insert or update on evidence
  for each row execute function exigir_clase_de_la_evidencia();

create or replace function rechazar_cambios_de_evidencia() returns trigger as $$
begin
  raise exception '%: una evidencia no se modifica ni se borra', tg_table_name;
end $$ language plpgsql;

create trigger trg_rechazar_cambios_de_evidencia
  before update or delete on evidence
  for each row execute function rechazar_cambios_de_evidencia();
create trigger trg_rechazar_cambios_de_evidencia
  before update or delete on evidencia_retirada
  for each row execute function rechazar_cambios_de_evidencia();

-- --- Qué falta -----------------------------------------------------------------------------

create or replace function clases_de_un_tipo_de_evidencia(p_task uuid, p_tipo text)
returns text[] as $$
  select coalesce((
    select array(select jsonb_array_elements_text(p.tipos -> p_tipo -> 'clases'))
      from task t
      join task_evidence_policy p on p.workspace_id = t.workspace_id and p.area_id = t.area_id
     where t.id = p_task
       and jsonb_typeof(p.tipos -> p_tipo -> 'clases') = 'array'), '{}');
$$ language sql stable;

create or replace function tipos_que_acepta_la_clase(p_task uuid, p_clase text)
returns text[] as $$
  select coalesce(array(
    select r.tipo
      from task t, unnest(t.evidencia_requerida) with ordinality as r(tipo, orden)
     where t.id = p_task
       and p_clase = any(clases_de_un_tipo_de_evidencia(t.id, r.tipo))
     order by r.orden), '{}');
$$ language sql stable;

create or replace function tipos_de_evidencia_que_faltan(p_task uuid,
                                                         p_piezas jsonb default '[]'::jsonb)
returns text[] as $$
  select coalesce(array(
    select r.tipo
      from task t, unnest(t.evidencia_requerida) with ordinality as r(tipo, orden)
     where t.id = p_task
       and not exists (
         select 1 from evidence e
          where e.task_id = t.id
            and r.tipo = any(e.cubre)
            and e.clase = any(clases_de_un_tipo_de_evidencia(t.id, r.tipo))
            and e.at > coalesce(
              (select max(a.at) from approval a
                where a.sujeto_tipo = 'tarea' and a.sujeto_id = t.id
                  and a.decision = 'rechazado'),
              '-infinity'::timestamptz)
            and not exists (select 1 from evidencia_retirada w where w.evidence_id = e.id))
       and not exists (
         select 1 from jsonb_array_elements(
                          case when jsonb_typeof(p_piezas) = 'array' then p_piezas
                               else '[]'::jsonb end) p
          where p ->> 'clase' = any(clases_de_un_tipo_de_evidencia(t.id, r.tipo))
            and jsonb_typeof(p -> 'cubre') = 'array'
            and p -> 'cubre' ? r.tipo)
     order by r.orden), '{}');
$$ language sql stable;

create or replace function evidencia_pendiente(p_task uuid)
returns boolean as $$
  select cardinality(tipos_de_evidencia_que_faltan(p_task)) > 0;
$$ language sql stable;

-- --- Privilegios y aislamiento -------------------------------------------------------------

grant all privileges on evidencia_retirada, archivo_de_tarea to leda_owner, leda_admin;

do $$
declare t text;
begin
  foreach t in array array['evidencia_retirada', 'archivo_de_tarea']
  loop
    execute format('alter table %I enable row level security', t);
    execute format('alter table %I force row level security', t);
    execute format($f$
      create policy aislamiento_espacio on %I
        using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid)
    $f$, t);
    execute format('grant select, insert, update, delete on %I to leda_app', t);
  end loop;
end $$;

revoke update, delete on evidence, evidencia_retirada, archivo_de_tarea from leda_app;

commit;
