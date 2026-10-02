\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0025_rechazar_borrador.sql. Hallazgo F-B3 de la corrida B
-- (2026-09-30): ADR 0013, enmienda de la rama abierta ("un borrador que espera la
-- confirmación de otra persona no es una rama abierta de quien lo pidió").
--
-- Hasta ahora una solicitud del alta quedaba `active` después de "Enviar a
-- aprobación" y el índice único `task_intake_one_active` (una `active` por
-- persona y chat) hacía que pedir otra tarea chocara con ella: "Ya hay un borrador
-- en curso" y, con "Cancelar", el borrador que esperaba a otra persona terminaba
-- cancelado. La solicitud sigue `active` (la función que confirma o cancela el
-- borrador la busca así), pero ahora lleva `enviada_en` y el índice sólo cuenta
-- las que no se enviaron.
--
-- Un borrador enviado antes de aplicar esta migración conserva el comportamiento
-- anterior hasta que termine: no se reescribe ninguna fila.
--
-- Se deshace con `db/rollbacks/0026_borrador_enviado_no_es_rama_abierta.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0026 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('leda.task_intake_request') is null then
    raise exception '0026 requires task_intake_request (0002_general_task_intake.sql)';
  end if;
  if exists (
      select 1 from information_schema.columns
       where table_schema = 'leda' and table_name = 'task_intake_request'
         and column_name = 'enviada_en') then
    raise exception '0026 ya está aplicada.';
  end if;
end $$;

-- Una columna nueva, nula por omisión, no toca privilegios, dueño ni la
-- seguridad por filas de la tabla.
alter table task_intake_request add column enviada_en timestamptz;

comment on column task_intake_request.enviada_en is
  'F-B3: cuándo quien pidió el borrador lo envió a otra persona para que lo confirme. Con ella, la solicitud sigue active (la conversión la busca así) pero deja de ser la rama abierta de quien la pidió.';

drop index task_intake_one_active;
create unique index task_intake_one_active
  on task_intake_request (workspace_id, membership_id, chat_id)
  where estado = 'active' and enviada_en is null;

commit;
