\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0032_borrar_el_alta_guiada.sql. Los archivos recibidos por chat (ADR 0019,
-- decisiones 2 a 4; primera porción: recibir y guardar, sin evidencia todavía).
--
-- - `archivo`: el contenido de cada archivo recibido (`bytea`), su huella, su tamaño, el tipo
--   que detectó el código, el nombre con que llegó, quién lo mandó y cuándo. Del dominio:
--   ningún identificador de Telegram (frontera, regla 2). La base garantiza que la huella es la
--   del contenido y el tamaño el suyo, de 1 byte a 60 MB (el límite del producto), y que un
--   mismo archivo se guarda una vez por espacio, nunca compartido entre espacios.
-- - `archivo_de_mensaje`: del lado del transporte, qué archivo trajo cada mensaje entrante,
--   con los identificadores de Telegram, o por qué no se guardó (demasiado grande o de un tipo
--   fuera de la lista). Un álbum es un solo mensaje: sus fotos apuntan al mismo entrante.
-- - Inmutabilidad: `leda_app` sólo agrega y lee las dos tablas, y un disparador rechaza
--   cualquier cambio o borrado de un archivo, también desde la conexión administrativa.
-- - Aislamiento: `row level security` forzado con la política de siempre en las dos; las
--   referencias a `membership` y a `inbound_message` se comprueban del mismo espacio con
--   `exigir_referencias_del_espacio()` (el motivo de no usar una clave foránea con el espacio
--   está en la 0030); la del archivo, con una clave foránea compuesta.
-- - El ajuste `archivo_tamano_maximo_mb` de `workspace_setting`: un entero de 1 a 60, con el
--   que un espacio baja el límite del producto. Esta migración no pone ningún valor.
--
-- La evidencia (columnas nuevas de `evidence`, `evidencia_retirada`, las clases de cada tipo
-- de la política y la nueva `evidencia_pendiente`) es la porción siguiente, con su migración.
--
-- Se deshace con `db/rollbacks/0033_archivos_recibidos.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0033 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('leda.task_forecast') is null then
    raise exception '0033 requires 0031_seguimiento_del_motor.sql';
  end if;
  if to_regclass('leda.archivo') is not null then
    raise exception '0033 ya está aplicada.';
  end if;
  -- Un valor previo de la clave nueva que no cumpla el rango aborta antes del DDL.
  if exists (
      select 1 from workspace_setting
       where clave = 'archivo_tamano_maximo_mb'
         and not case
               when jsonb_typeof(valor) <> 'number' then false
               else (valor #>> '{}')::numeric between 1 and 60
                    and (valor #>> '{}')::numeric % 1 = 0
             end) then
    raise exception '0033 preflight failed: archivo_tamano_maximo_mb inválido en workspace_setting';
  end if;
end $$;

create table archivo (
  id                         uuid primary key default gen_random_uuid(),
  workspace_id               uuid not null references workspace(id) on delete cascade,
  contenido                  bytea not null,
  sha256                     text not null,
  tamano                     bigint not null,
  tipo                       text not null,
  clase                      text not null,
  nombre_original            text,
  enviado_por_membership_id  uuid not null references membership(id),
  recibido_en                timestamptz not null,
  constraint archivo_workspace_id_unique unique (workspace_id, id),
  constraint archivo_unico_por_huella unique (workspace_id, sha256),
  constraint archivo_huella_del_contenido
    check (sha256 = encode(sha256(contenido), 'hex')),
  constraint archivo_tamano_del_contenido
    check (tamano = octet_length(contenido) and tamano between 1 and 62914560),
  constraint archivo_clase check (
    clase in ('imagen', 'video', 'pdf', 'documento', 'texto', 'comprimido')),
  constraint archivo_nombre_original check (
    btrim(nombre_original) <> '' and char_length(nombre_original) <= 255)
);

create table archivo_de_mensaje (
  id                       uuid primary key default gen_random_uuid(),
  workspace_id             uuid not null references workspace(id) on delete cascade,
  inbound_message_id       uuid not null references inbound_message(id) on delete cascade,
  archivo_id               uuid,
  que_llego                text not null,
  nombre_original          text,
  rechazo                  text,
  telegram_message_id      bigint not null,
  telegram_file_id         text not null,
  telegram_file_unique_id  text not null,
  telegram_media_group_id  text,
  at                       timestamptz not null default now(),
  constraint archivo_de_mensaje_archivo
    foreign key (workspace_id, archivo_id) references archivo(workspace_id, id),
  constraint archivo_de_mensaje_unico_por_mensaje
    unique (inbound_message_id, telegram_message_id),
  constraint archivo_de_mensaje_que_llego check (que_llego in ('foto', 'video', 'archivo')),
  constraint archivo_de_mensaje_rechazo check (
    rechazo in ('demasiado_grande', 'tipo_no_admitido')),
  constraint archivo_de_mensaje_guardado_o_rechazado check (
    (archivo_id is null) <> (rechazo is null))
);

create index archivo_de_mensaje_por_album on archivo_de_mensaje (telegram_media_group_id)
  where telegram_media_group_id is not null;

comment on table archivo is
  'ADR 0019, decisiones 2 y 3: el contenido de cada archivo recibido, con su huella (la garantiza la base). Un archivo por huella y espacio. Sólo se agrega: no se modifica ni se borra.';
comment on table archivo_de_mensaje is
  'ADR 0019, decisión 4: qué archivo trajo cada mensaje entrante, con los identificadores de Telegram, o por qué no se guardó. Un álbum es un solo mensaje.';

create trigger trg_exigir_referencias_del_espacio
  before insert or update on archivo
  for each row execute function exigir_referencias_del_espacio(
    'enviado_por_membership_id', 'membership');
create trigger trg_exigir_referencias_del_espacio
  before insert or update on archivo_de_mensaje
  for each row execute function exigir_referencias_del_espacio(
    'inbound_message_id', 'inbound_message');

create or replace function rechazar_cambios_de_archivo() returns trigger as $$
begin
  raise exception 'archivo: un archivo recibido no se modifica ni se borra';
end $$ language plpgsql;

create trigger trg_rechazar_cambios_de_archivo
  before update or delete on archivo
  for each row execute function rechazar_cambios_de_archivo();

grant all privileges on archivo, archivo_de_mensaje to leda_owner, leda_admin;

do $$
declare t text;
begin
  foreach t in array array['archivo', 'archivo_de_mensaje']
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

revoke update, delete on archivo, archivo_de_mensaje from leda_app;

alter table workspace_setting
  add constraint workspace_setting_archivo_tamano_maximo check (
    case
      when clave <> 'archivo_tamano_maximo_mb' then true
      when jsonb_typeof(valor) <> 'number' then false
      else (valor #>> '{}')::numeric between 1 and 60
           and (valor #>> '{}')::numeric % 1 = 0
    end);

commit;
