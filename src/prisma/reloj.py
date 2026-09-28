"""Reloj de cadencia.

Los horarios no están en el código: son filas de `cadence_job`, que salen del
pack del espacio. Cambiar el lunes de 09:15 a 09:30 es actualizar una fila.

Este módulo hace dos cosas y ninguna de ellas es enviar:
  - dispara las cadencias que corresponden y deja los mensajes en la cola;
  - corre la escalera de vencimientos.

El despachador es quien entrega.
"""

from __future__ import annotations

from datetime import datetime, timezone

import psycopg
from apscheduler.schedulers.background import BackgroundScheduler

from . import escalera
from .calendario import Calendario
from .salida import enqueue_outbox


def _plantilla(cur, workspace_id: str, clave: str) -> str | None:
    cur.execute(
        "select cuerpo from message_template where workspace_id = %s and clave = %s",
        (workspace_id, clave))
    fila = cur.fetchone()
    return fila["cuerpo"] if fila else None


def ejecutar_cadencia(cur: psycopg.Cursor, workspace_id: str, nombre: str,
                      cal: Calendario, ahora: datetime | None = None) -> int:
    """Arma los mensajes de una cadencia y los deja en la cola."""
    ahora = ahora or datetime.now(timezone.utc)

    cur.execute(
        "select * from cadence_job where workspace_id = %s and nombre = %s and activo",
        (workspace_id, nombre))
    job = cur.fetchone()
    if not job:
        return 0

    ventana = ahora.astimezone(cal.zona).strftime("%G-W%V-%u")
    encolados = 0

    if job["audiencia"] == "grupo":
        cur.execute("select grupo_chat_id from workspace where id = %s", (workspace_id,))
        chat = cur.fetchone()["grupo_chat_id"]
        if chat:
            cuerpo = _plantilla(cur, workspace_id, job["plantilla_clave"]) \
                or _resumen_grupal(cur, workspace_id)
            encolados += _encolar(cur, workspace_id, chat, None, cuerpo,
                                  f"{workspace_id}:{nombre}:{ventana}", cal, ahora)
    else:
        cur.execute(
            """select membership_id as id, telegram_user_id
                 from integrante
                where workspace_id = %s and activo
                  and telegram_user_id is not null""",
            (workspace_id,))
        for p in cur.fetchall():
            if _ausente(cur, p["id"], ahora):
                continue
            cuerpo = _resumen_personal(cur, workspace_id, p["id"], nombre)
            if cuerpo is None:
                continue
            encolados += _encolar(
                cur, workspace_id, p["telegram_user_id"], p["id"], cuerpo,
                f"{workspace_id}:{nombre}:{p['id']}:{ventana}", cal, ahora)

    cur.execute("update cadence_job set ultima_corrida = %s where id = %s",
                (ahora, job["id"]))
    return encolados


def _ausente(cur, membership_id, ahora) -> bool:
    cur.execute(
        """select 1 from absence where membership_id = %s and desde <= %s
             and (hasta is null or hasta >= %s) limit 1""",
        (membership_id, ahora.date(), ahora.date()))
    return cur.fetchone() is not None


def _encolar(cur, workspace_id, chat_id, membership_id, cuerpo, dedupe,
             cal: Calendario, ahora) -> int:
    return enqueue_outbox(
        cur, workspace_id=workspace_id, chat_id=chat_id, text=cuerpo,
        recipient_membership_id=membership_id, message_type="seguimiento",
        scheduled_for=cal.dentro_de_jornada(ahora), dedupe_key=dedupe,
        allow_split=True,
    )


def _resumen_personal(cur, workspace_id: str, membership_id: str,
                      cadencia: str) -> str | None:
    cur.execute(
        """select titulo, fecha_objetivo, estado from task
            where workspace_id = %s and responsable_membership_id = %s
              and estado in ('asignada', 'en_curso', 'bloqueada')
            order by fecha_objetivo nulls last limit 10""",
        (workspace_id, membership_id))
    tareas = cur.fetchall()
    if not tareas:
        return None
    lineas = [
        f"· {t['titulo']}" + (f" — vence {t['fecha_objetivo']:%d/%m}"
                              if t["fecha_objetivo"] else "")
        for t in tareas
    ]
    encabezado = {
        "objetivos_semanales": "Arranca la semana. Esto es lo que tenés abierto:",
        "estado_medio_semana": "Mitad de semana. ¿Cómo viene esto?",
        "cierre_semanal": "Cierre de semana. ¿Qué queda de acá?",
    }.get(cadencia, "Tus tareas abiertas:")
    return encabezado + "\n" + "\n".join(lineas)


def _resumen_grupal(cur, workspace_id: str) -> str:
    cur.execute(
        """select estado, count(*) n from task where workspace_id = %s
            group by estado""", (workspace_id,))
    por_estado = {f["estado"]: f["n"] for f in cur.fetchall()}
    cur.execute(
        """select count(*) n from blocker
            where workspace_id = %s and resuelto_en is null""", (workspace_id,))
    bloqueos = cur.fetchone()["n"]
    partes = [f"{n} {e}" for e, n in sorted(por_estado.items())]
    texto = "Estado del equipo: " + (", ".join(partes) or "sin tareas cargadas")
    if bloqueos:
        texto += f"\nHay {bloqueos} bloqueo(s) abierto(s)."
    return texto


def ejecutar_escalera(cur: psycopg.Cursor, workspace_id: str,
                      cal: Calendario, ahora: datetime | None = None) -> int:
    acciones = escalera.evaluar(cur, workspace_id, cal, ahora)
    encoladas = escalera.encolar(cur, workspace_id, acciones, cal, ahora)

    # Los bloqueos abiertos escalan por su propia antigüedad, no por el
    # vencimiento de la tarea: la mecánica §8 los trata aparte de la
    # escalera de recordatorios, pero corren en la misma pasada.
    bloqueos = escalera.evaluar_bloqueos(cur, workspace_id, cal, ahora)
    encoladas += escalera.encolar_bloqueos(cur, workspace_id, bloqueos, ahora)

    # Dependencias bloqueantes en riesgo (mecánica §4): mismo criterio, misma
    # pasada.
    dependencias = escalera.evaluar_dependencias_en_riesgo(cur, workspace_id, cal, ahora)
    encoladas += escalera.encolar_dependencias(cur, workspace_id, dependencias, ahora)
    return encoladas


# ---------------------------------------------------------------------------
# Planificador
# ---------------------------------------------------------------------------

def montar(conn_factory, scheduler: BackgroundScheduler | None = None, *,
          con_cadencias: bool = True,
          intervalo_segundos: int | None = None) -> BackgroundScheduler:
    """Arranca el ciclo compartido (cadencias vencidas + escalera + despacho,
    por espacio, más el aviso a la administración) a intervalos regulares.

    Un solo job de intervalo, no uno por cadencia ni uno de escalera por
    espacio: cada pasada relee `cadence_job` y la lista de espacios activos
    de la base (`ciclo.Ciclo.tick`), así que un pack reimportado o un
    espacio nuevo se aplican solos, sin reiniciar el proceso ni volver a
    llamar a `montar`. `con_cadencias=False` corre escalera y despacho igual,
    sin encolar ninguna cadencia -- el interruptor que expone `--sin-cadencias`.
    """
    from .ciclo import Ciclo, INTERVALO_SEGUNDOS

    sched = scheduler or BackgroundScheduler(timezone="UTC")
    ciclo_obj = Ciclo(conn_factory)
    sched.add_job(
        ciclo_obj.tick, "interval",
        seconds=intervalo_segundos or INTERVALO_SEGUNDOS,
        kwargs={"con_cadencias": con_cadencias}, id="ciclo", replace_existing=True)
    return sched
