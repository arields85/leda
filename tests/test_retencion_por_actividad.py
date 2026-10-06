"""La retención acotada por la actividad de la persona y por una pasada acotada
(T9-R1d-2b, ADR 0013 regla 1, "Precisión (2026-09-29, decisión del usuario)").

Lo que inicia Leda se retiene sólo mientras la persona está ACTIVA en la rama:
escribió o tocó algo en ese chat en los últimos `VENTANA_DE_ACTIVIDAD` (30
minutos). Una rama abierta pero abandonada no retiene nada, ni siquiera un aviso
urgente: sale en el momento y la rama sigue abierta. Con esa ventana también
retienen las preguntas del alta guiada, que no vencen.

Además, la pasada de `despachar` examina a lo sumo `lote` filas, retenidas o no,
y lo retenido no deja sin servicio a lo que viene detrás.

Las pruebas que abrían ramas con el alta guiada y el menú de tarea se retiraron con los
flujos A y B (E3-4); la retención misma sale del despachador con el enredo 2 (E3-3).
"""

from __future__ import annotations

from datetime import timedelta

from leda.despachador import VENTANA_DE_ACTIVIDAD


def test_la_ventana_de_actividad_es_de_30_minutos():
    assert VENTANA_DE_ACTIVIDAD == timedelta(minutes=30)
