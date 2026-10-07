"""Los cambios pedidos vigentes de una tarea (T9-R3, ADR 0013 regla 3, H16).

Era el menú de acciones de una tarea (T2, ADR 0007), que se retiró con los flujos
A y B (E3-3): sólo lo mostraba la conversación vieja. Queda lo que las lecturas de
tareas de `herramientas` siguen usando: el motivo vigente de "Pedir cambios".
"""

from __future__ import annotations

from typing import NamedTuple

import psycopg

# Cuánto del motivo de "Pedir cambios" entra en una lectura de la tarea: un motivo
# muy largo se acorta en vez de dejar la lectura sin salir (límite de Telegram).
LIMITE_MOTIVO_CAMBIOS = 300


class CambiosPedidos(NamedTuple):
    """Los cambios pedidos vigentes de una tarea: `motivo` (el texto que dejó quien
    los pidió, en una línea y acotado) y `linea`, lo que se muestra. `por` es
    quien los pidió (`None` si no se sabe) y `completo` el motivo entero, sin
    acotar."""
    motivo: str
    linea: str
    por: str | None = None
    completo: str = ""


def cambios_pedidos(cur: psycopg.Cursor, tarea_id: str) -> str | None:
    """La línea de los cambios pedidos vigentes de la tarea, lista para mostrar;
    `None` si no hay pedido vigente (`cambios_pedidos_vigentes`)."""
    pedido = cambios_pedidos_vigentes(cur, tarea_id)
    return pedido.linea if pedido else None


def cambios_pedidos_vigentes(cur: psycopg.Cursor,
                             tarea_id: str) -> CambiosPedidos | None:
    """El motivo vigente de "Pedir cambios" (T9-R3, ADR 0013 regla 3, H16): lo que
    falta en la tarea se ve en toda lectura de ella, no sólo en el aviso que se
    mandó. Vigente = el último `rechazado` de la tarea mientras ésta esté por
    hacerse (`asignada`/`en_curso`): "Pedir cambios" es lo único que la devuelve
    a ese estado desde la revisión, y la nueva entrega la vuelve a `en_revision`,
    que cierra el pedido. Es la única fuente: las lecturas de tareas
    (`herramientas._consultar_tareas`) leen de acá.
    `None` si no hay pedido vigente."""
    cur.execute(
        """select a.comentario, i.nombre
             from approval a
             join task t on t.id = a.sujeto_id
             left join integrante i on i.membership_id = a.aprobador_membership_id
            where a.sujeto_tipo = 'tarea' and a.sujeto_id = %s
              and a.decision = 'rechazado' and t.estado in ('asignada', 'en_curso')
            order by a.at desc limit 1""", (tarea_id,))
    fila = cur.fetchone()
    motivo = " ".join((fila["comentario"] or "").split()) if fila else ""
    if not motivo:
        return None
    completo = motivo
    if len(motivo) > LIMITE_MOTIVO_CAMBIOS:
        motivo = motivo[:LIMITE_MOTIVO_CAMBIOS - 1].rstrip() + "…"
    quien = f" por {fila['nombre']}" if fila["nombre"] else ""
    return CambiosPedidos(motivo=motivo, linea=f"Cambios pedidos{quien}: {motivo}",
                          por=fila["nombre"] or None, completo=completo)
