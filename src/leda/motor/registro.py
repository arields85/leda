"""El registro de turnos del motor (`conversation_turn`; ADR 0018, decisión 3).

Cada mensaje o toque de la persona (`entrada`) y cada mensaje de Leda (`salida`) queda en su
registro de turnos, con su número en la conversación de la persona: ordena los últimos turnos
aunque tengan la misma hora. Lo escriben el turno y los avisos guardados, y lo leen los dos
para darle a la IA los últimos turnos.

En la prueba chica estas funciones vivían en `turno.py` y los avisos las importaban de ahí, con
un ciclo `turno` → `efectos` → `avisos` → `turno` que se cortaba con un import dentro de una
función. En su propio módulo, el ciclo no existe. El comportamiento es el mismo; la entrada
recibe sus datos uno por uno, en lugar del contexto del turno.
"""

from __future__ import annotations

import dataclasses
import json
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from .ia import Jugada

ULTIMOS_TURNOS = 10


def leer_ultimos_turnos(cur, membership_id: str) -> tuple[dict[str, Any], ...]:
    """Los últimos turnos de la persona, del más viejo al más nuevo, con su texto; un toque,
    con la etiqueta de la opción que tocó (`toco`)."""
    cur.execute("""select t.sentido, coalesce(i.texto, o.cuerpo) texto, t.jugadas,
                          t.resultado -> 'hechos' as hechos, t.at, op.etiqueta toco
                     from conversation_turn t
                     left join inbound_message i on i.id = t.inbound_message_id
                     left join message_outbox o on o.id = t.outbox_id
                     left join conversation_option op on op.id = t.option_id
                    where t.membership_id = %s
                    order by t.numero desc
                    limit %s""", (membership_id, ULTIMOS_TURNOS))
    return tuple(
        {"sentido": t["sentido"], "texto": t["texto"], "jugadas": t["jugadas"],
         "hechos": t["hechos"], "at": t["at"].isoformat(),
         **({"toco": t["toco"]} if t["toco"] else {})}
        for t in reversed(cur.fetchall()))


def no_vacio(texto: str) -> str:
    """El texto que redactó la IA, sin espacios a los costados; una respuesta vacía es una IA
    que no respondió."""
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("La IA devolvió una respuesta vacía.")
    return texto.strip()


def registrar_salida(cur, workspace_id: str, membership_id: str, outbox_id: str,
                     ia_nombre: str | None, ahora: datetime) -> None:
    """Un mensaje de Leda a la persona, en su registro de turnos."""
    cur.execute(
        """insert into conversation_turn (workspace_id, membership_id, sentido, outbox_id,
                                          ia, at, numero)
           values (%s, %s, 'salida', %s, %s, %s, %s)""",
        (workspace_id, membership_id, outbox_id, ia_nombre, ahora,
         siguiente_numero(cur, membership_id)))


def registrar_entrada(cur, *, workspace_id: str, membership_id: str,
                      entrante_id: str | None, ahora: datetime,
                      jugadas: Sequence[Jugada] | None, resultado: dict | None,
                      ia_nombre: str, latencia_ms: int, error: str | None,
                      option_id: str | None = None) -> str:
    """Un mensaje o un toque de la persona, en su registro de turnos (un toque, con la opción
    tocada). `jugadas` en `None`: la IA no llegó a elegir. Devuelve el id del turno."""
    cur.execute(
        """insert into conversation_turn (workspace_id, membership_id, sentido,
                                          inbound_message_id, option_id, jugadas, resultado,
                                          ia, latencia_ms, error, at, numero)
           values (%s, %s, 'entrada', %s, %s, %s, %s, %s, %s, %s, %s, %s)
           returning id""",
        (workspace_id, membership_id, entrante_id, option_id,
         _json([dataclasses.asdict(j) for j in jugadas] if jugadas is not None else None),
         _json(resultado), ia_nombre, latencia_ms, error, ahora,
         siguiente_numero(cur, membership_id)))
    return str(cur.fetchone()["id"])


def siguiente_numero(cur, membership_id: str) -> int:
    """El número del próximo turno de la persona; el candado del turno lo hace único."""
    cur.execute("""select coalesce(max(numero), 0) + 1 as n from conversation_turn
                    where membership_id = %s""", (membership_id,))
    return cur.fetchone()["n"]


def _json(valor: Any) -> str | None:
    return None if valor is None else json.dumps(valor, ensure_ascii=False, default=str)
