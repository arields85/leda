\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0039_el_ejemplo_aceptado.sql. Una pregunta de Leda sin contestar (decisión 21 del
-- usuario, 2026-10-08; C-3d, unidad D5b de `odd/tasks/fase-c.md`; conversación de prueba 30).
--
-- Una pregunta sin contestar frena los otros temas de la persona hasta que Leda la repite, una vez
-- en el día, a las 4 horas; 4 horas después de la repetición sale aparte el tema siguiente, y las
-- dos preguntas quedan abiertas a la vez (una para después). Para eso cada pregunta guarda:
--
-- - `preguntada_en`: la última vez que Leda se la hizo a la persona (en una respuesta o en un
--   aviso). Las 4 horas se cuentan desde ahí. Las filas de antes quedan sin ella y se cuenta desde
--   `abierta_en`: no se sabe cuándo se repitieron, y no se inventa.
-- - `vuelve_aparte`: si es una de las dos preguntas que quedaron abiertas a la vez porque un aviso
--   de Leda hizo la segunda. Cuando una se cierra, el código trae la otra en un mensaje aparte.
--
-- Se deshace con `db/rollbacks/0040_pregunta_sin_contestar.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0040 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: las preguntas del motor existen (migración 0030) y todavía no las columnas nuevas.
do $$ begin
  if to_regclass('leda.conversation_question') is null then
    raise exception '0040 preflight failed: falta la 0030 (conversation_question)';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'conversation_question'
                and column_name in ('preguntada_en', 'vuelve_aparte')) then
    raise exception '0040 preflight failed: conversation_question ya tiene las columnas nuevas';
  end if;
end $$;

alter table conversation_question
  add column preguntada_en timestamptz,
  add column vuelve_aparte boolean not null default false;

comment on column conversation_question.preguntada_en is
  'La última vez que Leda le hizo la pregunta a la persona (decisión 21 del usuario, 2026-10-08): las 4 horas de una pregunta sin contestar se cuentan desde ahí. Sin valor, desde abierta_en.';
comment on column conversation_question.vuelve_aparte is
  'Una de dos preguntas abiertas a la vez porque un aviso de Leda hizo la segunda (decisión 21): cuando una se cierra, el código trae la otra en un mensaje aparte.';

commit;
