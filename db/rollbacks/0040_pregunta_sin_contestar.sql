\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0040_pregunta_sin_contestar.sql.
--
-- Borra `conversation_question.preguntada_en` y `conversation_question.vuelve_aparte`. No se niega
-- a correr: lo que se pierde es cuándo se repitió cada pregunta abierta y qué par de preguntas
-- vuelve aparte, que sólo ordenan los próximos avisos (el código anterior no los lee). Antes de
-- deshacerla en una base con datos, `pg_dump` de `conversation_question` y la decisión registrada.
begin;
set search_path = leda, public;

alter table conversation_question
  drop column if exists preguntada_en,
  drop column if exists vuelve_aparte;

commit;
