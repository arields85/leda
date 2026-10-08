\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0037_funciones_elevadas_con_camino_fijo.sql. Lo que describe cada pieza de una
-- entrega del criterio de aceptación de su tarea (decisión 10 del usuario, 2026-10-08; C-3d,
-- unidad D3 de `odd/tasks/fase-c.md`).
--
-- La entrega se compara con el criterio de aceptación: lo que la persona escribe tiene que decir
-- cada punto del criterio antes de que la tarea pase a revisión. Cada texto de una entrega guarda
-- los puntos que la persona confirmó en la vista previa que ese texto describe, tal cual el
-- criterio los decía al entregarla (`describe_del_criterio`). Así, si después retira un texto, el
-- sistema sabe qué deja de estar dicho y Leda le pide lo que falta (decisión 15 del usuario).
--
-- - Sólo un texto describe el criterio: una foto, un archivo o un enlace no lo certifican (la
--   clase la fija la cocina; la restricción `evidence_describe_solo_un_texto`).
-- - Las filas de antes quedan con `{}`: no se sabe qué describían, y no se inventa.
-- - Como el resto de `evidence`, la columna sólo se agrega: `leda_app` no tiene `update` y el
--   disparador `rechazar_cambios_de_evidencia` rechaza cualquier cambio.
--
-- Se deshace con `db/rollbacks/0038_lo_que_describe_cada_pieza.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0038 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la evidencia tiene su clase (migración 0034) y todavía no la columna nueva.
do $$ begin
  if not exists (select 1 from information_schema.columns
                  where table_schema = 'leda' and table_name = 'evidence'
                    and column_name = 'clase') then
    raise exception '0038 preflight failed: falta la 0034 (evidence.clase)';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'evidence'
                and column_name = 'describe_del_criterio') then
    raise exception '0038 preflight failed: evidence.describe_del_criterio ya existe';
  end if;
end $$;

alter table evidence
  add column describe_del_criterio text[] not null default '{}',
  add constraint evidence_describe_solo_un_texto
    check (clase = 'texto' or describe_del_criterio = '{}');

commit;
