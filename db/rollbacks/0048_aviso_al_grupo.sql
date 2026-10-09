\encoding UTF8
\set ON_ERROR_STOP on

-- Reverts 0048_aviso_al_grupo.sql.
--
-- Borra `scheduled_notice.al_grupo` y su restricción, y vuelve obligatorio el destinatario.
--
-- Se niega a correr si hay algún aviso al grupo (un informe al grupo guardado, enviado u omitido):
-- sin destinatario, la regla vieja no lo sabe representar y deshacerla lo perdería sin avisar.
-- Antes de deshacerla en una base con datos, `pg_dump` de `scheduled_notice` y borrar esas filas
-- a mano, con la decisión registrada.
begin;
set search_path = leda, public;

do $$ begin
  if exists (select 1 from scheduled_notice where al_grupo) then
    raise exception '0048 rollback refused: hay avisos al grupo guardados; respaldalos y '
                    'borralos primero';
  end if;
end $$;

alter table scheduled_notice drop constraint if exists scheduled_notice_destino;
alter table scheduled_notice alter column destinatario_membership_id set not null;
alter table scheduled_notice drop column if exists al_grupo;

commit;
