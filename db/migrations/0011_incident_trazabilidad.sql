\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0010_modificar_propuesta.sql. Decisión del usuario,
-- 2026-09-25 (T2b, `prisma-orienta`): un error nunca pasa en silencio, y el
-- incidente que queda tiene que hacer encontrable la causa -- sin copiar
-- texto de conversación adentro.
--
-- Agrega a `incident` la trazabilidad que le faltaba: `etapa` (el punto de
-- entrada donde se atrapó la excepción, `gateway.ETAPA_*`),
-- `referencia_tipo`/`referencia_id` (mismo patrón polimórfico que
-- `audit_log.sujeto_tipo`/`sujeto_id`, sin clave foránea -- apuntan al
-- `inbound_message` o a la `pending_action` que originó esto, nunca copian
-- su texto), y `chat_id`/`app_user_id` (quién y dónde). `notificado_en` ya
-- existía sin usar (`docs/capacidades.md`, promesa sin cumplir); esta
-- unidad es la primera que la llena.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0011 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if not exists (
      select 1 from information_schema.tables
       where table_schema = 'prisma' and table_name = 'incident') then
    raise exception '0011 requires the base schema (incident table missing).';
  end if;
  if exists (
      select 1 from information_schema.columns
       where table_schema = 'prisma' and table_name = 'incident'
         and column_name = 'etapa') then
    raise exception '0011 ya está aplicada.';
  end if;
end $$;

alter table incident add column etapa text;
alter table incident add column referencia_tipo text;
alter table incident add column referencia_id uuid;
alter table incident add column chat_id bigint;
alter table incident add column app_user_id uuid references app_user(id) on delete set null;

comment on column incident.etapa is
  'Punto de entrada donde se atrapó la excepción (gateway.ETAPA_*): turno de texto, toque de botón, activación, acción del menú.';
comment on column incident.referencia_tipo is
  'Qué tabla referencia referencia_id: inbound_message o pending_action. Sin clave foránea (mismo patrón que audit_log.sujeto_tipo).';
comment on column incident.referencia_id is
  'Id de la fila que originó el incidente. Nunca se copia su texto acá -- se abre desde esa fila, bajo la retención por cliente de docs/ROADMAP.md.';
comment on column incident.chat_id is
  'El chat de Telegram donde ocurrió, si se conoce.';
comment on column incident.app_user_id is
  'Quién escribió o tocó el botón, si se identificó.';

-- `prisma_app` ya tenía `insert` concedido sobre `incident` desde el
-- esquema base (0000): las columnas nuevas no necesitan una concesión
-- aparte, un `grant insert` cubre la fila entera.

commit;
