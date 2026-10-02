\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0015_pedir_cambios_exento_del_gate_de_arranque.sql. T6j
-- (`odd/tasks/leda-orienta.md`, review-5085907d): sólo los cuatro
-- handlers que bloquea `_bloquear_tarea` (`_actualizar_estado`,
-- `_adjuntar_evidencia`, `_aprobar_tarea`, `_pedir_cambios_tarea`,
-- `herramientas.py`) fijan `at = clock_timestamp()` al escribir en
-- `task_state_event`, `evidence` y `approval`; cualquier otro escritor --
-- transiciones del sistema, cargas administrativas -- sigue con el
-- `default now()` de la columna, que en PostgreSQL es la hora de INICIO de
-- la transacción, no la del `insert`. `motivo_no_cierra_tarea`,
-- `evidencia_pendiente` y `estado_previo_a_bloqueo`/`estado_previo_a_revision`
-- (comentario de `_bloquear_tarea`) ordenan o comparan por `at` entre estas
-- tres tablas: un escritor fuera de esos cuatro handlers puede dejar un `at`
-- anterior al de un acto que en verdad se escribió después, el mismo
-- defecto que motivó el lock de T6f pero sin ningún lock que lo cubra.
--
-- `blocker` no entra: `motivo_no_cierra_tarea` sólo comprueba `resuelto_en
-- is null` (una existencia, no un orden por hora) y
-- `estado_previo_a_bloqueo`/`estado_previo_a_revision` ordenan
-- `task_state_event` por su propio `at`, nunca contra `blocker.abierto_en`
-- ni `resuelto_en` -- ninguna de las cuatro funciones compara la hora de
-- `blocker` contra estas tres tablas.
--
-- Cambia el `default` de las tres columnas de `now()` a `clock_timestamp()`
-- para que el orden por `at` valga para todo el que escriba, no sólo para
-- los cuatro handlers bloqueados. Esos cuatro siguen fijándolo explícito
-- (comentario de `_bloquear_tarea`, `herramientas.py`): ya no hace falta
-- para que el orden salga bien, pero documenta en el punto de escritura por
-- qué ese orden importa, y no deja esa garantía dependiendo únicamente de
-- que nadie borre este default más adelante.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0016 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regprocedure('leda.estado_previo_a_revision(uuid)') is null then
    raise exception '0016 requires 0015_pedir_cambios_exento_del_gate_de_arranque.sql';
  end if;
  if (select column_default from information_schema.columns
       where table_schema = 'leda' and table_name = 'task_state_event'
         and column_name = 'at') = 'clock_timestamp()' then
    raise exception '0016 ya está aplicada.';
  end if;
end $$;

-- Un default nuevo sobre una columna que ya existe no toca privilegios ni
-- dueño de la tabla -- sólo lo que PostgreSQL usa cuando el insert no fija
-- `at` por su cuenta. Sin concesión ni `alter ... owner to` que agregar.
alter table task_state_event alter column at set default clock_timestamp();
alter table evidence alter column at set default clock_timestamp();
alter table approval alter column at set default clock_timestamp();

commit;
