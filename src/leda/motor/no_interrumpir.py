"""No interrumpir una conversación: lo que Leda manda por su cuenta espera a que la persona no
esté hablando con ella.

Decisión del usuario (2026-10-08; `odd/tasks/fase-c.md`, decisión 13; conversación 26), del
hallazgo de la prueba por Telegram real de ese día: el aviso de que una tarea vencía en 3 días
salió justo después de una respuesta de Leda, en medio de la conversación, repitiendo lo que se
estaba hablando. Es una regla general de la cocina, para todos los avisos guardados
(`avisos.py`) y todos los circuitos, no un caso del aviso previo ni una regla para la IA.

**Cuánto:** 30 minutos desde lo último que la persona escribió o tocó (`ESPERA_POR_OMISION`), o
los del espacio en `workspace_setting` (`no_interrumpir_minutos`, un número de minutos, 0 o
más; 0 no espera). Un valor que no es eso usa el del producto: del lado seguro, nunca deja salir
antes un aviso. Cada mensaje nuevo vuelve a contar.

**Cuándo sale:** terminada la espera, con las reglas de siempre encima (`tiempo.sale`): nunca
antes de la hora de salida del día ni fuera del horario. Si la espera cruza el cierre, sale el
día hábil siguiente a la hora en que Leda escribe por su cuenta, releído ese día.

**Sólo la persona que conversa:** un aviso a otra persona no espera por ella (Ismael no está
conversando aunque Marcos sí). Vale para todos los avisos a la persona, también los de
coordinación. No es el margen para corregir (`margen.py`): el margen demora el aviso a otra
persona para que quien habló pueda corregirse; esta regla demora el aviso a quien está hablando.

La espera vive en el envío (`avisos._preparar`).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from .tiempo import sale

CLAVE = "no_interrumpir_minutos"
ESPERA_POR_OMISION = timedelta(minutes=30)


def espera_sin_interrumpir(cur, workspace_id: str) -> timedelta:
    """La espera del espacio, o la del producto si no la configuró (o configuró algo que no es
    un número de minutos, 0 o más)."""
    cur.execute("select valor from workspace_setting where workspace_id = %s and clave = %s",
                (workspace_id, CLAVE))
    fila = cur.fetchone()
    valor = fila["valor"] if fila else None
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor < 0:
        return ESPERA_POR_OMISION
    return timedelta(minutes=valor)


def ultimo_mensaje(cur, persona: str) -> datetime | None:
    """Cuándo escribió o tocó algo la persona por última vez (su último turno de entrada)."""
    cur.execute("""select max(at) as at from conversation_turn
                    where membership_id = %s and sentido = 'entrada'""", (persona,))
    fila = cur.fetchone()
    return fila["at"] if fila else None


def libre_desde(cur, cal, workspace_id: str, persona: str, *,
                tambien: datetime | None = None) -> datetime | None:
    """Desde cuándo se le puede escribir por su cuenta a la persona: terminada la espera desde su
    último mensaje y dentro del horario (`tiempo.sale`); `None` si nunca escribió. `tambien`: un
    mensaje suyo que todavía no está en el registro de turnos (el del turno en curso)."""
    ultimo = ultimo_mensaje(cur, persona)
    if tambien is not None and (ultimo is None or tambien > ultimo):
        ultimo = tambien
    if ultimo is None:
        return None
    return sale(cal, ultimo + espera_sin_interrumpir(cur, workspace_id))


def cuando_sale(cur, cal, workspace_id: str, aviso: dict[str, Any], *,
                escribe: tuple[str, datetime] | None = None) -> datetime:
    """Cuándo sale de verdad un aviso guardado: a su hora o, si quien lo recibe está
    conversando, cuando termine su espera. Es lo que dicen los hechos (`llega`): a una persona se
    le cuenta cuándo se entera de verdad la otra, como con el margen para corregir. `escribe`:
    quién escribe en el turno en curso y cuándo (su mensaje todavía no está en el registro)."""
    persona = str(aviso["destinatario_membership_id"])
    tambien = escribe[1] if escribe is not None and escribe[0] == persona else None
    libre = libre_desde(cur, cal, workspace_id, persona, tambien=tambien)
    a_su_hora = aviso["programado_para"]
    return libre if libre is not None and libre > a_su_hora else a_su_hora


def conversando(cur, cal, workspace_id: str, persona: str, ahora: datetime) -> bool:
    """Si la persona está conversando con Leda: su espera todavía no terminó."""
    libre = libre_desde(cur, cal, workspace_id, persona)
    return libre is not None and ahora < libre

