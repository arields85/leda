"""Puerto de lectura: el estado consolidado de un espacio.

Es el puerto que `docs/architecture/frontera.md` nombra como Lectura. Sirve a
cualquier superficie que no sea la conversacional —un tablero, una aplicación
móvil, un informe— con consultas agregadas en vez de las respuestas acotadas
que usa el agente.

**El espacio sale de la sesión, nunca de quien llama.** Ninguna función de este
módulo recibe `workspace_id`: todas toman un cursor ya acotado por
`prisma.db.espacio()`, y el aislamiento lo garantiza la política de la base. Si
alguna aceptara el espacio por parámetro, quien la invoque podría pedir el
ajeno, que es exactamente lo que la regla 1 de la frontera prohíbe.

El momento actual también se recibe por parámetro donde hace falta. Leer el
reloj adentro de una consulta vuelve la lectura irreproducible y las pruebas
dependientes de cuándo se corren.
"""

from __future__ import annotations

from datetime import datetime

# Ni terminada ni cancelada: el trabajo que todavía ocupa a alguien.
ESTADOS_ACTIVOS = ("propuesta", "pendiente_aprobacion", "asignada",
                   "en_curso", "bloqueada", "en_revision")


def avance_de_objetivos(cur) -> list[dict]:
    """Objetivos con cuántas de sus tareas están terminadas.

    Incluye los objetivos sin tareas: uno sin trabajo asociado es información
    —alguien lo definió y nadie lo bajó a tareas—, no una fila que se omite.
    De ahí el `left join`.
    """
    cur.execute(
        """select o.id, o.titulo, o.tipo, o.estado,
                  count(t.id)::int as tareas,
                  count(t.id) filter (where t.estado = 'terminada')::int
                    as terminadas
             from objective o
             left join task t on t.objective_id = o.id
            group by o.id, o.titulo, o.tipo, o.estado
            order by o.titulo""")
    return [dict(f) for f in cur.fetchall()]


def tareas_por_estado(cur) -> list[dict]:
    """Cuántas tareas hay en cada estado presente."""
    cur.execute(
        """select estado, count(*)::int as tareas
             from task group by estado order by estado""")
    return [dict(f) for f in cur.fetchall()]


def carga_por_persona(cur) -> list[dict]:
    """Tareas activas por responsable.

    Pasa por la vista `integrante` y no por `app_user`, que es global: es como
    el resto del sistema resuelve nombres sin saltarse el aislamiento.
    """
    cur.execute(
        """select i.nombre, i.membership_id, count(t.id)::int as activas
             from integrante i
             left join task t
               on t.responsable_membership_id = i.membership_id
              and t.estado = any(%s)
            where i.activo
            group by i.nombre, i.membership_id
            order by activas desc, i.nombre""",
        (list(ESTADOS_ACTIVOS),))
    return [dict(f) for f in cur.fetchall()]


def tareas_vencidas(cur, ahora: datetime) -> list[dict]:
    """Tareas cuya fecha objetivo pasó y siguen abiertas."""
    cur.execute(
        """select t.id, t.titulo, t.estado, t.fecha_objetivo, i.nombre,
                  extract(day from %s - t.fecha_objetivo)::int as dias_vencida
             from task t
             left join integrante i
               on i.membership_id = t.responsable_membership_id
            where t.fecha_objetivo < %s
              and t.estado = any(%s)
            order by t.fecha_objetivo""",
        (ahora, ahora, list(ESTADOS_ACTIVOS)))
    return [dict(f) for f in cur.fetchall()]


def bloqueos_abiertos(cur, ahora: datetime) -> list[dict]:
    """Bloqueos sin resolver, con la tarea que traban y su antigüedad."""
    cur.execute(
        """select b.id, b.causa, b.impacto, b.abierto_en,
                  t.id as task_id, t.titulo,
                  extract(day from %s - b.abierto_en)::int as dias
             from blocker b
             join task t on t.id = b.task_id
            where b.resuelto_en is null
            order by b.abierto_en""",
        (ahora,))
    return [dict(f) for f in cur.fetchall()]


def trabajo_esperando_aprobacion(cur) -> list[dict]:
    """Tareas y objetivos detenidos esperando que alguien decida.

    No sale de `approval`: esa tabla registra decisiones ya tomadas —su columna
    `decision` sólo admite `aprobado` o `rechazado`— así que no puede
    representar una aprobación pendiente. Lo que el dominio sí expresa es el
    estado del trabajo: una tarea en `pendiente_aprobacion` o `en_revision`, y
    un objetivo en `completo_pendiente_aprobacion`, están esperando a alguien.
    """
    cur.execute(
        """select 'tarea' as sujeto_tipo, t.id as sujeto_id, t.titulo,
                  t.estado::text as estado, t.actualizado_en as desde,
                  i.nombre as responsable
             from task t
             left join integrante i
               on i.membership_id = t.responsable_membership_id
            where t.estado in ('pendiente_aprobacion', 'en_revision')
           union all
           select 'objetivo', o.id, o.titulo, o.estado::text, o.actualizado_en,
                  i.nombre
             from objective o
             left join integrante i
               on i.membership_id = o.referente_membership_id
            where o.estado = 'completo_pendiente_aprobacion'
            order by desde""")
    return [dict(f) for f in cur.fetchall()]
