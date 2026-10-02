\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0028_quitar_botones.sql.
--
-- Quita la marca de los botones ya resueltos y su índice. El despachador de antes
-- de C0-6 no la usa; los botones que ya se quitaron en Telegram siguen quitados.
begin;
set search_path = leda, public;

drop index if exists outbox_botones_por_quitar;
alter table message_outbox drop column if exists botones_quitados_en;

commit;
