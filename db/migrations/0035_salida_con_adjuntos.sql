\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0034_evidencia_de_la_entrega.sql. La salida con adjuntos (ADR 0019, decisión 6;
-- porción 3a de la C-3: el aviso a quien aprueba con las fotos, todavía sin el enlace).
--
-- - `message_outbox_adjunto`: los archivos que lleva una fila de la salida, con su orden. Apunta
--   a `archivo`, que es del dominio, nunca a un identificador de Telegram: cómo se manda un
--   adjunto (reusar el identificador que el canal le dio al recibirlo o subir la copia propia)
--   lo decide el despachador al mandar. `message_outbox` no suma ninguna columna (riesgo 1 de
--   `docs/STATUS.md`: la salida ya está atada a un transporte, y esto no la ata más).
-- - Orden: de 1 a 10 por fila (un álbum de Telegram lleva hasta diez), sin repetir ni el orden ni
--   el archivo. El texto y su álbum son dos filas de una misma respuesta (`respuesta_grupo`); que
--   el álbum no salga antes que el texto lo garantiza el despachador.
-- - Aislamiento: `row level security` forzado con la política de siempre; la fila de la salida
--   y el archivo, con claves foráneas compuestas por espacio: un adjunto nunca apunta a un archivo
--   ni a una fila de salida de otro espacio (la comprobación de una clave foránea no pasa por la
--   RLS; la clave lleva el espacio).
-- - Sólo se agrega: `leda_app` agrega y lee; lo que lleva un mensaje no cambia.
--
-- El enlace a la página de la tarea (lo que la fila necesita para que el despachador lo emita al
-- mandar) es de la porción 4, con su migración.
--
-- Se deshace con `db/rollbacks/0035_salida_con_adjuntos.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0035 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('leda.evidencia_retirada') is null then
    raise exception '0035 requires 0034_evidencia_de_la_entrega.sql';
  end if;
  if to_regclass('leda.message_outbox_adjunto') is not null then
    raise exception '0035 ya está aplicada.';
  end if;
end $$;

create table message_outbox_adjunto (
  id            uuid primary key default gen_random_uuid(),
  workspace_id  uuid not null references workspace(id) on delete cascade,
  outbox_id     uuid not null,
  archivo_id    uuid not null,
  orden         integer not null,
  constraint message_outbox_adjunto_outbox
    foreign key (workspace_id, outbox_id) references message_outbox(workspace_id, id)
    on delete cascade,
  constraint message_outbox_adjunto_archivo
    foreign key (workspace_id, archivo_id) references archivo(workspace_id, id),
  constraint message_outbox_adjunto_orden check (orden between 1 and 10),
  constraint message_outbox_adjunto_orden_unico unique (outbox_id, orden),
  constraint message_outbox_adjunto_archivo_unico unique (outbox_id, archivo_id)
);

comment on table message_outbox_adjunto is
  'ADR 0019, decisión 6: los archivos que lleva una fila de la salida, en orden (hasta diez, un álbum). Apunta al archivo del dominio, nunca a un identificador de Telegram: cómo se manda lo decide el despachador. Sólo se agrega.';

grant all privileges on message_outbox_adjunto to leda_owner, leda_admin;

alter table message_outbox_adjunto enable row level security;
alter table message_outbox_adjunto force row level security;
create policy aislamiento_espacio on message_outbox_adjunto
  using (workspace_id = nullif(current_setting('leda.workspace_id', true), '')::uuid);
grant select, insert, update, delete on message_outbox_adjunto to leda_app;
revoke update, delete on message_outbox_adjunto from leda_app;

commit;
