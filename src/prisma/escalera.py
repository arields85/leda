"""Escalera de recordatorios y escalamiento.

Implementa la sección 9 de `nucleo/mecanica-pm.md`. Los pasos se anclan al
vencimiento de cada tarea, no a intervalos sueltos, y se cuentan en días
hábiles del espacio.

    V − 1 hábil   aviso, no exige respuesta
    V             primer recordatorio
    V + 1 hábil   segundo, con el impacto
    V + 2 hábiles tercero, avisando que se escala
    V + 3 hábiles escalamiento según la ruta del área

Reglas que este módulo hace cumplir:
  - los cuatro primeros pasos son siempre privados;
  - una persona ausente no recibe nada y su escalera no avanza;
  - una tarea bloqueada sale de la escalera y entra al flujo de bloqueos;
  - nada se envía directo: todo va a la cola con clave de deduplicación.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import psycopg

from .calendario import Calendario

PASOS = [
    (-1, "aviso",     "informativo"),
    (0,  "recordar1", "normal"),
    (1,  "recordar2", "normal"),
    (2,  "recordar3", "prioritario"),
    (3,  "escalar",   "prioritario"),
]


@dataclass
class Accion:
    task_id: str
    paso: str
    tipo: str
    destinatario_membership_id: str
    chat_id: int | None
    cuerpo: str
    dedupe_key: str
    escalamiento: bool = False


def _paso_correspondiente(cal: Calendario, vence: datetime, ahora: datetime) -> tuple[str, str] | None:
    """Devuelve el paso que toca hoy, o None si todavía no toca ninguno."""
    transcurridos = cal.habiles_entre(vence, ahora)
    elegido = None
    for offset, nombre, tipo in PASOS:
        if transcurridos >= offset:
            elegido = (nombre, tipo)
    return elegido


def _ausente(cur, membership_id: str, ahora: datetime) -> bool:
    cur.execute(
        """select 1 from absence
            where membership_id = %s and desde <= %s
              and (hasta is null or hasta >= %s) limit 1""",
        (membership_id, ahora.date(), ahora.date()))
    return cur.fetchone() is not None


def evaluar(cur: psycopg.Cursor, workspace_id: str, cal: Calendario,
            ahora: datetime | None = None) -> list[Accion]:
    """Calcula qué recordatorios corresponden ahora. No envía nada."""
    ahora = ahora or datetime.now(timezone.utc)
    acciones: list[Accion] = []

    cur.execute(
        """
        select t.id, t.titulo, t.fecha_objetivo, t.area_id,
               t.responsable_membership_id as resp,
               i.telegram_user_id, i.nombre,
               (select count(*) from blocker b
                 where b.task_id = t.id and b.resuelto_en is null) as bloqueos
          from task t
          join integrante i on i.membership_id = t.responsable_membership_id
         where t.workspace_id = %s
           and t.estado in ('asignada', 'en_curso')
           and t.fecha_objetivo is not null
        """,
        (workspace_id,))
    tareas = cur.fetchall()

    for t in tareas:
        # Una tarea bloqueada no se recuerda: se trabaja el bloqueo.
        if t["bloqueos"]:
            continue
        if _ausente(cur, t["resp"], ahora):
            continue

        paso = _paso_correspondiente(cal, t["fecha_objetivo"], ahora)
        if paso is None:
            continue
        nombre, tipo = paso

        dedupe = f"{workspace_id}:escalera:{t['id']}:{nombre}"

        if nombre == "escalar":
            destino = _ruta_escalamiento(cur, workspace_id, t["area_id"])
            if destino is None:
                continue
            acciones.append(Accion(
                task_id=str(t["id"]), paso=nombre, tipo=tipo,
                destinatario_membership_id=str(destino["id"]),
                chat_id=destino["telegram_user_id"],
                cuerpo=(f"Escalo «{t['titulo']}», de {t['nombre']}. "
                        f"Venció el {t['fecha_objetivo']:%d/%m} y llevo tres "
                        f"recordatorios sin respuesta."),
                dedupe_key=dedupe, escalamiento=True))
        else:
            acciones.append(Accion(
                task_id=str(t["id"]), paso=nombre, tipo=tipo,
                destinatario_membership_id=str(t["resp"]),
                chat_id=t["telegram_user_id"],
                cuerpo=_texto(nombre, t, cur),
                dedupe_key=dedupe))

    return acciones


def _texto(paso: str, t, cur) -> str:
    titulo = t["titulo"]
    vence = t["fecha_objetivo"]
    if paso == "aviso":
        return (f"Mañana vence «{titulo}». Si vas bien, no hace falta que "
                f"contestes este mensaje.")
    if paso == "recordar1":
        return f"Hoy vence «{titulo}». ¿Cómo viene?"
    if paso == "recordar2":
        dependientes = _dependientes(cur, t["id"])
        if dependientes:
            return (f"Sigo sin novedades de «{titulo}», que venció el "
                    f"{vence:%d/%m}. Hay {dependientes} tarea(s) esperando "
                    f"que termine.")
        return (f"Sigo sin novedades de «{titulo}», que venció el {vence:%d/%m}. "
                f"¿Necesitás mover la fecha o hay algo trabando?")
    return (f"«{titulo}» lleva tres días vencida sin respuesta. Si no tengo "
            f"novedades hoy, lo escalo. Decime si preferís que lo hablemos antes.")


def _dependientes(cur, task_id) -> int:
    cur.execute(
        """select count(*) n from dependency
            where origen_task_id = %s and tipo = 'bloqueante'""", (task_id,))
    return cur.fetchone()["n"]


def _ruta_escalamiento(cur, workspace_id: str, area_id: str):
    cur.execute(
        """
        select i.membership_id as id, i.telegram_user_id
          from escalation_route r
          join integrante i
            on (r.destino_membership_id = i.membership_id
                or (r.destino_rol_id is not null and i.rol_id = r.destino_rol_id
                    and i.workspace_id = r.workspace_id))
         where r.workspace_id = %s
           and (r.area_id = %s or r.area_id is null)
         order by (r.area_id is null), r.orden
         limit 1
        """,
        (workspace_id, area_id))
    return cur.fetchone()


def encolar(cur: psycopg.Cursor, workspace_id: str, acciones: list[Accion],
            cal: Calendario, ahora: datetime | None = None) -> int:
    """Deja las acciones en la cola. La clave de deduplicación hace que un
    reinicio no vuelva a mandar lo mismo."""
    ahora = ahora or datetime.now(timezone.utc)
    encoladas = 0
    for a in acciones:
        if a.chat_id is None:
            continue  # todavía no activó su enlace de Telegram
        cur.execute(
            """
            insert into message_outbox
              (workspace_id, chat_id, destinatario_membership_id, tipo, cuerpo,
               estado, programado_para, dedupe_key)
            values (%s, %s, %s, %s, %s, 'listo', %s, %s)
            on conflict (dedupe_key) do nothing
            """,
            (workspace_id, a.chat_id, a.destinatario_membership_id, a.tipo,
             a.cuerpo, cal.dentro_de_jornada(ahora), a.dedupe_key))
        encoladas += cur.rowcount

        if a.paso.startswith("recordar") or a.paso == "escalar":
            cur.execute(
                """update pending_reply
                      set recordatorios = recordatorios + 1,
                          escalado_en = case when %s then now() else escalado_en end
                    where task_id = %s and satisfecho_en is null""",
                (a.escalamiento, a.task_id))
    return encoladas
