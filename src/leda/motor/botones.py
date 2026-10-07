"""Los botones de una duda, al despachar (diseño probado en la Etapa 2, E2-4).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Las ocho situaciones, una vez", 5); ADR 0018,
decisiones 4 y 9d (los únicos botones de la prueba chica: las tareas como opciones de una duda).
La respuesta sale por el outbox como todas; el despachador (`leda.despachador`, que no se toca)
arma botones sólo para los flujos congelados, así que el motor le pasa un transporte que los
agrega: al entregar una respuesta, si su destinatario tiene abierta una pregunta con opciones
desde antes de que se escribiera esa respuesta, salen sus opciones, cada una con su token como
`callback_data` (`preguntas.callback`). Se leen al entregar, no al encolar, como hace el
despachador: si la pregunta se cerró en el medio, ya no salen. Lo que Leda manda por su cuenta
nunca lleva botones (9b).
"""

from __future__ import annotations

from typing import Any

from ..despachador import Boton, Transporte

from .preguntas import callback


class ConOpciones:
    """Un transporte que agrega las opciones de la pregunta abierta a la respuesta que se
    está entregando. `cur` es el cursor de la pasada del despachador, en su transacción."""

    def __init__(self, transporte: Transporte, cur) -> None:
        self.transporte = transporte
        self.cur = cur

    def enviar(self, chat_id: int, texto: str, botones: list[Boton] | None = None,
               **mas: Any) -> int:
        if not botones:
            botones = self._opciones(chat_id, texto)
        return self.transporte.enviar(chat_id, texto, botones, **mas)

    def _opciones(self, chat_id: int, texto: str) -> list[Boton]:
        with self.cur.connection.cursor() as cur:
            # La respuesta que se está entregando: el despachador ya la marcó enviada y todavía
            # no guardó su id de Telegram. El texto que llega puede llevar el saludo adelante.
            cur.execute("""select cuerpo, destinatario_membership_id, programado_para
                             from message_outbox
                            where chat_id = %s and estado = 'enviado' and es_respuesta
                              and telegram_message_id is null
                              and destinatario_membership_id is not null
                            order by enviado_en desc""", (chat_id,))
            fila = next((f for f in cur.fetchall() if texto.endswith(f["cuerpo"])), None)
            if fila is None:
                return []
            cur.execute("""select o.etiqueta, o.token
                             from conversation_state s
                             join conversation_question q on q.id = s.pregunta_abierta_id
                             join conversation_option o on o.question_id = q.id
                            where s.membership_id = %s and q.cerrada_en is null
                              and q.abierta_en <= %s
                            order by o.orden""",
                        (fila["destinatario_membership_id"], fila["programado_para"]))
            return [Boton(o["etiqueta"], callback(o["token"])) for o in cur.fetchall()]
