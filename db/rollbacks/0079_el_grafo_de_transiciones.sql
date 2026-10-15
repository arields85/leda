\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0079_el_grafo_de_transiciones.sql: borra los dos disparadores del grafo de transiciones
-- y sus funciones. Los eventos registrados mientras regía no cambian; vuelve a aceptarse cualquier
-- par de estados.
begin;
set search_path = leda, public;

drop trigger if exists trg_encadenar_estado_tarea on task_state_event;
drop trigger if exists trg_encadenar_estado_objetivo on objective_state_event;
drop function if exists exigir_transicion_valida_tarea();
drop function if exists exigir_transicion_valida_objetivo();

commit;
