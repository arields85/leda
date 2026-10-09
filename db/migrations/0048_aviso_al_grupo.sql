\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0047_las_tareas_de_la_lista.sql. El informe al grupo (C-6; decisión 25 del
-- usuario, 2026-10-09, opción A; decisiones 8, 35 y 49; `odd/tasks/fase-c.md`; conversación de
-- prueba 41):
--
-- - **Un aviso del motor puede ir al grupo del espacio** (`al_grupo`), no sólo a una persona: el
--   informe que la cadencia al grupo del pack manda al grupo del equipo. Va a una persona o al
--   grupo, nunca a los dos ni a nadie (`scheduled_notice_destino`).
-- - **El chat del grupo no se guarda acá** (`docs/architecture/frontera.md`, regla 2): sale de la
--   configuración del espacio (`workspace.grupo_chat_id`, del pack `telegram.grupo_gestion_id`)
--   al encolarlo en el outbox, como la presentación (`onboarding.encolar_presentacion`).
--
-- `scheduled_notice` sigue con `row level security` forzado y su política de aislamiento: un
-- aviso al grupo es del espacio, como cualquier otro.
--
-- Se deshace con `db/rollbacks/0048_aviso_al_grupo.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0048 requires an unmodified UTF-8 input stream';
  end if;
end $$;

-- Preflight: la 0047 está aplicada y todavía no la columna nueva.
do $$ begin
  if not exists (select 1 from information_schema.columns
                  where table_schema = 'leda' and table_name = 'scheduled_notice'
                    and column_name = 'tareas_de_la_lista') then
    raise exception '0048 preflight failed: falta la 0047 (scheduled_notice.tareas_de_la_lista)';
  end if;
  if exists (select 1 from information_schema.columns
              where table_schema = 'leda' and table_name = 'scheduled_notice'
                and column_name = 'al_grupo') then
    raise exception '0048 ya está aplicada.';
  end if;
end $$;

alter table scheduled_notice add column al_grupo boolean not null default false;
alter table scheduled_notice alter column destinatario_membership_id drop not null;
alter table scheduled_notice add constraint scheduled_notice_destino
  check (al_grupo = (destinatario_membership_id is null));

comment on column scheduled_notice.al_grupo is
  'El Motor (C-6, decisión 25 del usuario, 2026-10-09): el aviso va al grupo del espacio (el informe al grupo de la cadencia), no a una persona; entonces no tiene destinatario. El chat del grupo no se guarda acá: sale de workspace.grupo_chat_id al encolarlo en el outbox.';

commit;
