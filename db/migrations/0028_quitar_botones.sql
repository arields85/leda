\encoding UTF8
\set ON_ERROR_STOP on

-- Applied after 0027_objetivo_con_area.sql. C0-6 (ronda C0-C, 2026-10-02,
-- hallazgo H4): un resumen ya confirmado siguió mostrando sus botones en Telegram
-- y Leda ofrecía así lo que ya no se podía hacer (ADR 0013, regla 3). El
-- despachador ahora le quita los botones a un mensaje ya entregado cuando su acción
-- pendiente o su elección del alta deja de valer, y esta columna es la marca de que
-- eso ya se resolvió: una sola vez por mensaje.
--
-- Los mensajes ya entregados cuya acción o elección ya no valía al aplicar esta
-- migración quedan marcados sin tocar Telegram: son historia anterior al cambio, y un
-- toque sobre ellos lo contesta el gateway con el estado real (C0-5). Lo que sigue
-- esperando al aplicarla queda sin marcar y pierde sus botones cuando se resuelva.
--
-- Se deshace con `db/rollbacks/0028_quitar_botones.sql`.
begin;
set search_path = leda, public;

-- Fail closed if an invoking text pipeline decoded the UTF-8 file incorrectly.
-- chr() builds the expected value independently from non-ASCII source bytes.
do $$ begin
  if 'Codificación UTF-8: áéíóú ñ ¿' is distinct from
     ('Codificaci' || chr(243) || 'n UTF-8: ' || chr(225) || chr(233)
      || chr(237) || chr(243) || chr(250) || ' ' || chr(241) || ' '
      || chr(191)) then
    raise exception '0028 requires an unmodified UTF-8 input stream';
  end if;
end $$;

do $$ begin
  if to_regclass('leda.message_outbox') is null
     or to_regclass('leda.task_intake_choice_set') is null then
    raise exception '0028 requires message_outbox and task_intake_choice_set';
  end if;
  if exists (
      select 1 from information_schema.columns
       where table_schema = 'leda' and table_name = 'message_outbox'
         and column_name = 'botones_quitados_en') then
    raise exception '0028 ya está aplicada.';
  end if;
end $$;

-- Una columna y un índice nuevos no tocan privilegios, dueño ni la seguridad por
-- filas de `message_outbox` (aislamiento por espacio, forzado): `leda_app` ya puede
-- actualizar la tabla dentro de su espacio.
alter table message_outbox add column botones_quitados_en timestamptz;

create index outbox_botones_por_quitar on message_outbox (workspace_id, enviado_en)
  where estado = 'enviado' and botones_quitados_en is null
    and telegram_message_id is not null
    and (pending_action_id is not null or intake_choice_set_id is not null);

comment on column message_outbox.botones_quitados_en is
  'C0-6: cuándo el despachador resolvió quitar los botones de este mensaje en Telegram porque su acción o su elección ya no vale: se quitaron, Telegram dijo que ya no había nada que quitar, o falló y quedó un incidente. Nula mientras no hubo nada que quitar.';

-- Lo anterior a esta migración que ya no valía: marcado, sin tocar Telegram.
update message_outbox m
   set botones_quitados_en = now()
 where m.estado = 'enviado' and m.telegram_message_id is not null
   and (exists (select 1 from pending_action p
                 where p.id = m.pending_action_id
                   and (p.estado <> 'esperando' or p.vence_en <= now()))
        or exists (select 1 from task_intake_choice_set s
                    where s.id = m.intake_choice_set_id and s.estado <> 'active'));

commit;
