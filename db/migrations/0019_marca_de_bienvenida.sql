\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0018_saludo_diario.sql. Revisión 2026-09-28+2 sobre e83a280
-- (T7b/T7b-follow-up, decisión del usuario): el saludo diario se decide al
-- DESPACHAR (`despachador._intentar_envio`), no al armar la respuesta --
-- cadencias, recordatorios de la escalera y avisos que dispara otra persona
-- también pueden ser el primer contacto del día, y sólo el despachador sabe
-- qué sale primero de verdad.
--
-- La bienvenida de incorporación (`onboarding.bienvenida`) sigue contando
-- como el saludo de esa fecha (pack 06 §3, T28), pero ya no lo reclama ella
-- misma al encolar: el despachador reclama por ella, sin anteponerle nada
-- -- ese texto ya es su propio saludo fijo. Necesita distinguir esa fila de
-- cualquier otro mensaje `informativo` (`onboarding.encolar_presentacion`,
-- la presentación de grupo, usa el mismo `tipo` sin ser un saludo), así que
-- agrega una marca dedicada en vez de reusar `tipo` -- mismo patrón que
-- `es_respuesta`, ya en esta tabla, para una distinción de despacho que no
-- es una categoría de mensaje.
begin;
set search_path = prisma, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0019 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('prisma.greeting_state') is null then
    raise exception '0019 requires 0018_saludo_diario.sql';
  end if;
  if exists (
      select 1 from information_schema.columns
       where table_schema = 'prisma' and table_name = 'message_outbox'
         and column_name = 'es_bienvenida') then
    raise exception '0019 ya está aplicada.';
  end if;
end $$;

-- Una columna nueva con default no toca privilegios ni dueño de la tabla --
-- prisma_app ya tiene el juego completo sobre message_outbox (bucle genérico
-- de `db/esquema.sql`). Sin concesión que agregar.
alter table message_outbox add column es_bienvenida boolean not null default false;

comment on column message_outbox.es_bienvenida is
  'Saludo diario (pack 06 §3, T28): esta fila ES la bienvenida de incorporación -- el despachador reclama la reserva del día por ella sin anteponerle nada, nunca una categoría de tipo_mensaje (informativo se comparte con la presentación de grupo).';

commit;
