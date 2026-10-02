\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0023_enviar_a_aprobacion.sql. Decisión del usuario (2026-09-30):
-- los avisos de coordinación quedan fuera del tope diario de mensajes
-- automáticos (`nucleo/mecanica-pm.md` §10).
--
-- `es_coordinacion` marca la fila de `message_outbox` que es un aviso causado
-- directamente por el acto de otra persona sobre trabajo compartido (entrega para
-- revisar, cambios pedidos, aprobación, borrador para confirmar o rechazado):
-- `despachador._ya_recibio` no la cuenta y el tope no la posterga. Los
-- seguimientos (cadencias, escalera) quedan en falso y siguen bajo el tope.
--
-- Columna no nula con valor por omisión falso: las filas existentes quedan como
-- seguimientos, que es lo que eran. No toca privilegios ni dueño de la tabla.
--
-- Se deshace con `db/rollbacks/0024_avisos_de_coordinacion.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0024 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (
      select 1 from information_schema.columns
       where table_schema = 'leda' and table_name = 'inbound_message'
         and column_name = 'boton_callback') then
    raise exception '0024 requires 0022_toque_con_boton.sql';
  end if;
  if exists (
      select 1 from information_schema.columns
       where table_schema = 'leda' and table_name = 'message_outbox'
         and column_name = 'es_coordinacion') then
    raise exception '0024 ya está aplicada.';
  end if;
end $$;

alter table message_outbox
  add column es_coordinacion boolean not null default false;

comment on column message_outbox.es_coordinacion is
  'Aviso de coordinación: causado directamente por el acto de otra persona sobre trabajo compartido. No cuenta contra el tope diario de mensajes automáticos ni lo posterga.';

commit;
