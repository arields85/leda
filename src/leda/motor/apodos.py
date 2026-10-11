"""Los apodos: Leda reconoce a una persona del equipo cuando la nombran por un apodo (ADR 0020;
conversación 47).

En un equipo real la gente se nombra como se habla ("el Tano", "Pato"). Un apodo es del espacio
(decisión 6): lo que enseñó una persona lo entiende Leda con todo el equipo de ese espacio, y
nunca en otro (la tabla `apodo`, con RLS forzado, migración 0055). Una persona puede tener varios
(decisión 2) y un apodo puede ser de dos personas (decisión 3).

**Se reconoce en un solo lugar** (`fichas.integrantes_que_coinciden`, que usan todas las jugadas
que nombran a alguien): los integrantes cuyo nombre tiene, como palabras enteras, todas las
palabras de lo dicho, y los que tienen un apodo vigente con todas esas palabras. Se compara con
las mismas palabras que los nombres (`fichas.palabras`: sin mayúsculas ni acentos), así "el tano"
y "Tano" son el mismo apodo "el tano", y nada de lo dicho actúa como comodín. Si un apodo es de
dos personas, o coincide con el nombre de otra, son dos: Leda pregunta (decisión 3).

**El apodo sirve para entender, nunca para hablar** (decisión 5): lo que se reconoce es el
integrante, con su nombre; los hechos que llegan a la IA lo nombran por su nombre. **Y no concede
nada** (decisión 7): ninguna regla de autoridad lo lee.

**Se aprende con la confirmación de una persona** (decisión 1; `aprender`): cada apodo aprendido
queda en `apodo`, con quién lo enseñó, cuándo y por qué canal, y en `audit_log` (decisión 8).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import psycopg

from ..autoridad import Solicitante
from .auditoria import auditar

CHAT = "chat"
PLATAFORMA = "plataforma"


def normalizar(dicho: str) -> str:
    """Las palabras de lo dicho como el código compara los nombres, separadas por un espacio:
    "El Tano" es "el tano"."""
    from .fichas import palabras        # fichas importa este módulo
    return " ".join(palabras(dicho))


def vigentes(cur: psycopg.Cursor) -> list[dict[str, Any]]:
    """Los apodos vigentes de los integrantes activos del espacio (la vista `integrante` lo acota
    al espacio de la transacción, también con la conexión de administración)."""
    cur.execute("""select a.membership_id, a.apodo
                     from apodo a
                     join integrante i on i.membership_id = a.membership_id
                    where a.borrado_en is null and i.activo""")
    return cur.fetchall()


def aprender(cur: psycopg.Cursor, quien: Solicitante, membership_id: str, dicho: str,
             ahora: datetime, *, inbound_message_id: str | None = None) -> bool:
    """El apodo aprendido por chat para ese integrante, con quien lo enseñó, y su fila de
    auditoría (ADR 0020, decisiones 1 y 8). Si ya lo tenía vigente, no cambia nada. Devuelve si
    lo aprendió ahora."""
    apodo = normalizar(dicho)
    if not apodo:
        return False
    cur.execute("""select 1 from apodo
                    where membership_id = %s and apodo = %s and borrado_en is null""",
                (membership_id, apodo))
    if cur.fetchone() is not None:
        return False
    cur.execute(
        """insert into apodo (workspace_id, membership_id, apodo, ensenado_por_app_user_id,
                              canal, at)
           values (%s, %s, %s, %s, %s, %s) returning id""",
        (quien.workspace_id, membership_id, apodo, quien.app_user_id, CHAT, ahora))
    apodo_id = cur.fetchone()["id"]
    auditar(cur, accion="aprender_apodo", workspace_id=quien.workspace_id,
            sujeto_tipo="apodo", sujeto_id=apodo_id, quien=quien,
            detalle={"membership_id": membership_id, "apodo": apodo, "canal": CHAT,
                     "ensenado_por_membership_id": quien.membership_id,
                     "at": ahora.isoformat(), "inbound_message_id": inbound_message_id})
    return True
