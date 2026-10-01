"""Muestra la conversación reciente de la base de prueba (datos ficticios), con los
botones que ofreció cada mensaje y la etiqueta de cada toque.

Herramienta de desarrollo para leer las pruebas por Telegram sin capturas. Usa la base
de `PRISMA_DB_URL` del checkout desde el que se corre (worktree con `PYTHONPATH=src`
para `prisma_flujo`; checkout principal para `prisma`). Sólo lee.

Uso: python tools/leer_conversacion.py [minutos] [desde HH:MM]
"""
import sys

import psycopg

from prisma import config

MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 40
DESDE = sys.argv[2] if len(sys.argv) > 2 else None
Q = """
select cuando, quien, texto, botones from (
  select i.at cuando,
         '>> ' || coalesce(u.nombre, '?') ||
         case when i.boton_callback is not null then ' [TOCÓ]' else '' end quien,
         coalesce(i.texto,
                  (select '«' || o.etiqueta || '»' from prisma.pending_action_option o
                    where o.token = substr(i.boton_callback, 3) limit 1),
                  (select '«' || ch.etiqueta || '»' from prisma.task_intake_choice ch
                    where ch.token = substr(i.boton_callback, 3) limit 1),
                  i.boton_callback) texto,
         '' botones
    from prisma.inbound_message i left join prisma.app_user u on u.id = i.app_user_id
   where i.at > now() - make_interval(mins => %(m)s)
  union all
  select coalesce(o.enviado_en, o.programado_para),
         '<< Prisma -> ' || coalesce(u.nombre, '?') || ' [' || o.estado || ']', o.cuerpo,
         coalesce(
           (select string_agg(op.etiqueta, ' | ' order by op.orden)
              from prisma.pending_action_option op where op.pending_action_id = o.pending_action_id),
           (select string_agg(ch.etiqueta, ' | ' order by ch.orden)
              from prisma.task_intake_choice ch where ch.choice_set_id = o.intake_choice_set_id),
           '')
    from prisma.message_outbox o
    left join prisma.membership m on m.id = o.destinatario_membership_id
    left join prisma.app_user u on u.id = m.app_user_id
   where coalesce(o.enviado_en, o.programado_para) > now() - make_interval(mins => %(m)s)
) t order by cuando
"""
with psycopg.connect(config.config.db_url) as c:
    for cuando, quien, texto, botones in c.execute(Q, {"m": MIN}).fetchall():
        hora = cuando.strftime("%H:%M:%S")
        if DESDE and hora[:5] < DESDE:
            continue
        texto = (texto or "").replace("\n", " / ")
        linea = f"{hora} {quien} | {texto[:400]}"
        if botones:
            linea += f"   [botones: {botones}]"
        print(linea)
