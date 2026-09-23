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

import json
from dataclasses import dataclass
from datetime import datetime, timezone

import psycopg

from .calendario import Calendario
from .salida import enqueue_outbox

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


@dataclass
class AccionBloqueo:
    bloqueo_id: str
    task_id: str
    destinatario_membership_id: str
    chat_id: int | None
    cuerpo: str
    dedupe_key: str


@dataclass
class AccionDependencia:
    origen_task_id: str
    # Una persona recibe un solo aviso por (origen, tipo de riesgo): si tiene
    # más de una tarea afectada en la cadena, todas quedan acá, no una por
    # `AccionDependencia`.
    destino_task_ids: list[str]
    destinatario_membership_id: str
    chat_id: int | None
    cuerpo: str
    dedupe_key: str


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


def _ruta_bloqueo_transversal(cur, workspace_id: str):
    """Ruta del bloqueo transversal del espacio (mecánica §8).

    No reutiliza `_ruta_escalamiento`: esa función no filtra por
    `disparador`, así que para una tarea de OT devolvería la ruta de
    `problema_tecnico` de esa área (destino Marcos), que es la escalada
    técnica de un vencimiento, no la de un bloqueo. Un bloqueo escala
    siempre por la ruta transversal, sea cual sea el área de la tarea.
    """
    cur.execute(
        """
        select i.membership_id as id, i.telegram_user_id
          from escalation_route r
          join integrante i
            on (r.destino_membership_id = i.membership_id
                or (r.destino_rol_id is not null and i.rol_id = r.destino_rol_id
                    and i.workspace_id = r.workspace_id))
         where r.workspace_id = %s and r.disparador = 'bloqueo_transversal'
         order by r.orden
         limit 1
        """,
        (workspace_id,))
    return cur.fetchone()


def _dias_escalada_bloqueo(cur, workspace_id: str) -> int | None:
    """Días hábiles de antigüedad a partir de los cuales un bloqueo escala
    solo. Sale de `workspace_setting['bloqueos']`, que el importador guarda
    desde el pack (`bloqueos.escala_solo_a_los_dias`) y hasta ahora nadie
    leía. Sin configuración, no hay escalamiento automático."""
    cur.execute(
        "select valor from workspace_setting "
        "where workspace_id = %s and clave = 'bloqueos'",
        (workspace_id,))
    fila = cur.fetchone()
    if not fila:
        return None
    valor = fila["valor"]
    if isinstance(valor, str):
        valor = json.loads(valor)
    dias = valor.get("escala_solo_a_los_dias")
    return int(dias) if dias is not None else None


def evaluar_bloqueos(cur: psycopg.Cursor, workspace_id: str, cal: Calendario,
                     ahora: datetime | None = None) -> list[AccionBloqueo]:
    """Bloqueos abiertos que ya superaron la antigüedad del pack y todavía no
    escalaron. No envía nada."""
    ahora = ahora or datetime.now(timezone.utc)
    dias = _dias_escalada_bloqueo(cur, workspace_id)
    if dias is None:
        return []

    cur.execute(
        """select b.id, b.task_id, b.causa, b.abierto_en, t.titulo, i.nombre
             from blocker b
             join task t on t.id = b.task_id
             join integrante i on i.membership_id = t.responsable_membership_id
            where b.workspace_id = %s and b.resuelto_en is null
              and b.escalado_en is null""",
        (workspace_id,))
    bloqueos = cur.fetchall()

    acciones: list[AccionBloqueo] = []
    for b in bloqueos:
        # "hace más de [pack] días": al cumplirse justo el umbral todavía no.
        if cal.habiles_entre(b["abierto_en"], ahora) <= dias:
            continue
        destino = _ruta_bloqueo_transversal(cur, workspace_id)
        if destino is None:
            continue
        acciones.append(AccionBloqueo(
            bloqueo_id=str(b["id"]), task_id=str(b["task_id"]),
            destinatario_membership_id=str(destino["id"]),
            chat_id=destino["telegram_user_id"],
            cuerpo=(f"«{b['titulo']}», de {b['nombre']}, tiene un bloqueo sin "
                    f"resolver hace más de {dias} días hábiles: {b['causa']}. "
                    f"Lo escalo."),
            dedupe_key=f"{workspace_id}:bloqueo-escalado:{b['id']}"))
    return acciones


def encolar_bloqueos(cur: psycopg.Cursor, workspace_id: str,
                     acciones: list[AccionBloqueo],
                     ahora: datetime | None = None) -> int:
    """Deja los bloqueos escalados en la cola y deja constancia en la fila.

    Igual que `encolar`: la marca de escalado se pone aunque el mensaje se
    deduplique, porque lo que importa acá es que no se vuelva a evaluar este
    bloqueo, no si esta corrida en particular pudo mandar el aviso.
    """
    ahora = ahora or datetime.now(timezone.utc)
    encoladas = 0
    for a in acciones:
        if a.chat_id is None:
            continue  # todavía no activó su enlace de Telegram
        encoladas += enqueue_outbox(
            cur, workspace_id=workspace_id, chat_id=a.chat_id, text=a.cuerpo,
            recipient_membership_id=a.destinatario_membership_id,
            message_type="prioritario", scheduled_for=ahora,
            dedupe_key=a.dedupe_key,
        )
        cur.execute(
            "update blocker set escalado_a = %s, escalado_en = %s where id = %s",
            (a.destinatario_membership_id, ahora, a.bloqueo_id))
    return encoladas


def encolar(cur: psycopg.Cursor, workspace_id: str, acciones: list[Accion],
            cal: Calendario, ahora: datetime | None = None) -> int:
    """Deja las acciones en la cola. La clave de deduplicación hace que un
    reinicio no vuelva a mandar lo mismo."""
    ahora = ahora or datetime.now(timezone.utc)
    encoladas = 0
    for a in acciones:
        if a.chat_id is None:
            continue  # todavía no activó su enlace de Telegram
        encoladas += enqueue_outbox(
            cur, workspace_id=workspace_id, chat_id=a.chat_id, text=a.cuerpo,
            recipient_membership_id=a.destinatario_membership_id,
            message_type=a.tipo, scheduled_for=cal.dentro_de_jornada(ahora),
            dedupe_key=a.dedupe_key, allow_split=True,
        )

        if a.paso.startswith("recordar") or a.paso == "escalar":
            cur.execute(
                """update pending_reply
                      set recordatorios = recordatorios + 1,
                          escalado_en = case when %s then now() else escalado_en end
                    where task_id = %s and satisfecho_en is null""",
                (a.escalamiento, a.task_id))
    return encoladas


# ---------------------------------------------------------------------------
# Dependencias bloqueantes en riesgo (mecánica §4)
# ---------------------------------------------------------------------------

def _en_riesgo_por_fecha_posterior(cur, origen_id: str, origen_fecha,
                                   ahora: datetime) -> bool:
    """La origen no está vencida todavía, pero su fecha queda después de la
    de algún dependiente directo que todavía la necesita (no terminado ni
    cancelado): ese dependiente se va a atrasar antes de que la origen
    siquiera venza."""
    cur.execute(
        """select exists (
             select 1 from dependency d join task t on t.id = d.destino_task_id
              where d.origen_task_id = %s and d.tipo = 'bloqueante'
                and t.estado not in ('terminada', 'cancelada')
                and t.fecha_objetivo is not null
                and t.fecha_objetivo < %s
           ) as riesgo""",
        (origen_id, origen_fecha))
    return cur.fetchone()["riesgo"]


def _cadena_de_dependientes(cur, origen_id: str):
    """Todos los que dependen de `origen_id` en cadena por dependencias
    `bloqueante` (no sólo los directos), todavía no terminados ni cancelados,
    con si la dependencia es directa o llega por un tramo intermedio (para
    poder decirlo en el aviso). Es el "impacto en cadena" de mecánica §4.

    Un mismo `t` puede aparecer por más de un camino (directo y, a la vez,
    indirecto por otra rama); `distinct on` se queda con la fila directa
    cuando existe, porque es la más precisa de las dos."""
    cur.execute(
        """with recursive cadena as (
             select d.destino_task_id as t, true as directo from dependency d
              where d.origen_task_id = %s and d.tipo = 'bloqueante'
             union
             select d.destino_task_id, false from dependency d
               join cadena c on d.origen_task_id = c.t
              where d.tipo = 'bloqueante'
           )
           select distinct on (t.id) t.id, t.titulo, t.responsable_membership_id,
                  c.directo
             from cadena c join task t on t.id = c.t
            where t.estado not in ('terminada', 'cancelada')
            order by t.id, c.directo desc""",
        (origen_id,))
    return cur.fetchall()


def _texto_dependencia_en_riesgo(origen_titulo: str, vencida: bool, tareas) -> str:
    """Nombra la o las tareas del destinatario afectadas -- sin eso, el aviso
    no da nada para actuar -- y, para un dependiente indirecto, aclara que es
    por la cadena y no por una dependencia declarada directamente con esa
    tarea."""
    motivo = (f"«{origen_titulo}» está vencida." if vencida else
             f"«{origen_titulo}» tiene una fecha que queda después de la tuya.")
    lineas = [
        f"· {t['titulo']}" + ("" if t["directo"] else " (a través de la cadena)")
        for t in tareas
    ]
    return f"{motivo} Depende de ella:\n" + "\n".join(lineas)


def evaluar_dependencias_en_riesgo(cur: psycopg.Cursor, workspace_id: str,
                                   cal: Calendario,
                                   ahora: datetime | None = None) -> list[AccionDependencia]:
    """Bloqueantes en riesgo (mecánica §4): no terminadas y, o vencidas, o con
    fecha posterior a la de un dependiente. Avisa a cada responsable de la
    cadena completa de dependientes, una vez por (origen, tipo de riesgo, su
    fecha objetivo actual): "vencida" y "posterior" son motivos distintos y
    no comparten clave, porque el segundo puede convertirse en el primero
    más adelante y esa escalada tiene que volver a avisar, no quedar
    deduplicada contra el aviso anterior. No envía nada."""
    ahora = ahora or datetime.now(timezone.utc)

    cur.execute(
        """select distinct o.id, o.titulo, o.fecha_objetivo
             from task o
             join dependency d on d.origen_task_id = o.id and d.tipo = 'bloqueante'
            where o.workspace_id = %s
              and o.estado not in ('terminada', 'cancelada')
              and o.fecha_objetivo is not null""",
        (workspace_id,))
    origenes = cur.fetchall()

    acciones: list[AccionDependencia] = []
    for o in origenes:
        vencida = o["fecha_objetivo"] < ahora
        if vencida:
            tipo_riesgo = "vencida"
        elif _en_riesgo_por_fecha_posterior(cur, o["id"], o["fecha_objetivo"], ahora):
            tipo_riesgo = "posterior"
        else:
            continue

        # Se agrupa por destinatario: si tiene más de una tarea afectada en
        # la cadena, todas van en un solo aviso -- la letra pide un aviso por
        # (origen, tipo de riesgo) por persona, no uno por tarea.
        por_destinatario: dict[str, list] = {}
        for dependiente in _cadena_de_dependientes(cur, o["id"]):
            destinatario = dependiente["responsable_membership_id"]
            if destinatario is None:
                continue
            por_destinatario.setdefault(str(destinatario), []).append(dependiente)

        dedupe_base = (f"{workspace_id}:dependencia-riesgo:{o['id']}:{tipo_riesgo}:"
                       f"{o['fecha_objetivo'].isoformat()}")
        for destinatario, tareas in por_destinatario.items():
            cur.execute(
                "select telegram_user_id from integrante where membership_id = %s",
                (destinatario,))
            persona = cur.fetchone()
            acciones.append(AccionDependencia(
                origen_task_id=str(o["id"]),
                destino_task_ids=[str(t["id"]) for t in tareas],
                destinatario_membership_id=destinatario,
                chat_id=persona["telegram_user_id"] if persona else None,
                cuerpo=_texto_dependencia_en_riesgo(o["titulo"], vencida, tareas),
                dedupe_key=f"{dedupe_base}:{destinatario}"))
    return acciones


def encolar_dependencias(cur: psycopg.Cursor, workspace_id: str,
                         acciones: list[AccionDependencia],
                         ahora: datetime | None = None) -> int:
    """Deja los avisos de dependencias en riesgo en la cola. La clave de
    deduplicación incluye la fecha objetivo vigente de la origen: si cambiara,
    volvería a avisar; una corrida repetida sobre el mismo momento, no."""
    ahora = ahora or datetime.now(timezone.utc)
    encoladas = 0
    for a in acciones:
        if a.chat_id is None:
            continue
        encoladas += enqueue_outbox(
            cur, workspace_id=workspace_id, chat_id=a.chat_id, text=a.cuerpo,
            recipient_membership_id=a.destinatario_membership_id,
            message_type="normal", scheduled_for=ahora, dedupe_key=a.dedupe_key,
        )
    return encoladas
