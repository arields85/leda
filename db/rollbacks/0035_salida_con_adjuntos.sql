\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0035_salida_con_adjuntos.sql.
--
-- Borra `message_outbox_adjunto`. Las filas de la salida quedan: un álbum que todavía no salió
-- quedaría como una fila sin adjuntos, que el despachador mandaría como texto. Por eso se niega
-- a correr mientras haya un adjunto de una fila que no se mandó; las de filas ya mandadas se
-- pierden (antes de correrlo en una base con datos, `pg_dump` de la tabla).
begin;
set search_path = leda, public;

do $$ begin
  if to_regclass('leda.message_outbox_adjunto') is not null and exists (
      select 1 from message_outbox_adjunto a
        join message_outbox o on o.id = a.outbox_id
       where o.estado in ('pendiente', 'esperando_confirmacion', 'listo')) then
    raise exception '0035 rollback refused: hay adjuntos de mensajes que todavía no salieron';
  end if;
end $$;

drop table if exists message_outbox_adjunto;

commit;
