"""El margen para corregir: lo que una persona dice y le llega a otra espera un rato antes de salir.

Decisión del usuario (2026-10-07), de la prueba por Telegram real (conversación 25): la IA anotó
la fecha de Marcos en la tarea equivocada y el aviso a Ismael salió un minuto después, antes de
que Marcos pudiera leer la respuesta de Leda y corregirla. La corrección ya retiraba el aviso
que todavía no había salido (`fichas._deshacer_prevision`, 9f); le faltaba tiempo. Es un
mecanismo general de la cocina, no una regla para la IA ni un caso para ese mensaje.

**Qué espera el margen:** los avisos guardados a otra persona que causa lo que dijo alguien en
un turno: el aviso al referente de una previsión nueva (`nueva_prevision`, también el que una
corrección vuelve a guardar) y el de su corrección (`correccion_de_prevision`). Lo demás no:

- las respuestas de Leda salen enseguida (ADR 0011, decisión 1);
- lo que Leda manda por su cuenta (la escalera, sus repreguntas y escalamientos, el pedido que
  sigue a un avance) no sale de algo que alguien acaba de decir: no hay nada que corregir, y
  sale a su hora (`tiempo.sale`);
- el aviso de una falla (`falla_de_aviso`) va a la misma persona que lo causó.

**Cuánto:** 10 minutos (`MARGEN_POR_OMISION`), o los del espacio en `workspace_setting`
(`margen_para_corregir_minutos`, un número de minutos, 0 o más). Un valor que no es eso usa el
del producto: del lado seguro, nunca deja salir antes un aviso.

**Cuándo sale:** al terminar el margen, con las reglas de siempre encima (`tiempo.sale`): nunca
antes de la hora de salida del día ni fuera del horario del espacio (9e). Esa es la hora que se
guarda en el aviso y, por eso, la que dicen los hechos (`llega`): lo que se le cuenta a la
persona es cuándo se entera de verdad la otra.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from .tiempo import sale

CLAVE_MARGEN = "margen_para_corregir_minutos"
MARGEN_POR_OMISION = timedelta(minutes=10)


def margen_para_corregir(cur, workspace_id: str) -> timedelta:
    """El margen del espacio, o el del producto si no lo configuró (o configuró algo que no es
    un número de minutos, 0 o más)."""
    cur.execute("select valor from workspace_setting where workspace_id = %s and clave = %s",
                (workspace_id, CLAVE_MARGEN))
    fila = cur.fetchone()
    valor = fila["valor"] if fila else None
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor < 0:
        return MARGEN_POR_OMISION
    return timedelta(minutes=valor)


def sale_con_margen(cur, cal, workspace_id: str, ahora: datetime) -> datetime:
    """Cuándo sale un aviso a otra persona que causa lo que alguien dijo en `ahora`: terminado
    el margen para corregir y dentro del horario (`tiempo.sale`)."""
    return sale(cal, ahora + margen_para_corregir(cur, workspace_id))
