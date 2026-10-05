"""El ancla de la escalera: la fecha desde la que se hace el seguimiento de una tarea.

ADR 0018, decisión 9i (usuario, 2026-10-05); mecánica §9; ADR 0017, decisión 4.

**Con una previsión válida, el seguimiento se mueve a la previsión, sin tocar la fecha
comprometida.** El ancla es la fecha comprometida (V) o, si la previsión vigente es posterior, la
fecha prevista (F). La escalera corre sobre el ancla: el día del ancla pide el estado como si
fuera V y, sin respuesta, sigue el paso a paso hasta escalar. Una previsión más nueva mueve el
ancla; una que vuelve a la fecha comprometida (o anterior) la devuelve a V. La fecha comprometida
no cambia por chat: el atraso se sigue contando contra ella y su cambio es del referente, en la
plataforma.

Cada paso de la escalera lleva su anclaje en la clave (cuarta parte): un anclaje nuevo es una
escalera nueva, con su propia cuenta, y un paso guardado de otro anclaje ya no corresponde al
salir. **Un anclaje es una racha de la misma fecha** (revisión del ancla, 2026-10-05): empieza
con la previsión que llevó el ancla a esa fecha y sigue mientras las previsiones siguientes la
dejen igual. Volver a una fecha ya usada (la comprometida, después de que su escalera empezó, o
una previsión anterior) es un anclaje nuevo: la escalera vieja, contestada o escalada, no la
apaga. Repetir la misma fecha no lo es. La clave del anclaje es la fecha sola mientras no hubo
ninguna previsión que la moviera (la escalera de V de siempre), o la fecha y la previsión con que
empezó la racha (`fecha+id`). El aviso previo es de la fecha comprometida, no de un anclaje: es
uno solo.

Lo comparten la escalera (`escalera.py`), los avisos (`avisos.py`) y la ficha del avance
(`fichas.py`), por eso vive acá y no importa a ninguno de ellos.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Any

# Un avance sin un hecho cierto (`informar_avance`, 9h): el pedido del día hábil siguiente, y el
# motivo con que quedan atrás los pasos guardados que reemplaza.
REPREGUNTA_DE_ESTADO = "repregunta_de_estado"
REEMPLAZADO_POR_UN_AVANCE = "reemplazado_por_un_avance"
REEMPLAZADO = "reemplazado_por_el_reencuadre"
# Los pasos que no salieron porque otro los reemplazó: no cuentan como dados.
NO_DADOS = frozenset({REEMPLAZADO, REEMPLAZADO_POR_UN_AVANCE})

# Los pasos de la escalera de un ancla.
TIPOS_DE_LA_ESCALERA = ("aviso_previo", "pedido_de_estado", "reencuadre", "escalamiento",
                        REPREGUNTA_DE_ESTADO)
# Con el ancla en una previsión, el único aviso del día del vencimiento: un recordatorio que no
# pide nada (9i). Es de la fecha comprometida, no de la escalera del ancla.
VENCIMIENTO_CON_PREVISION = "vencimiento_con_prevision"


def prevision_vigente(cur, task_id) -> dict[str, Any] | None:
    """La última previsión de la tarea: la que ninguna otra reemplaza."""
    cur.execute("""select f.* from task_forecast f
                    where f.task_id = %s
                      and not exists (select 1 from task_forecast g where g.reemplaza_id = f.id)
                    order by f.at desc limit 1""", (str(task_id),))
    return cur.fetchone()


@dataclass(frozen=True)
class Anclaje:
    """La fecha del seguimiento y la clave de su escalera (la cuarta parte de cada paso).
    `legado`: la clave que tenían los pasos de esta escalera antes de la revisión del ancla
    (la fecha sola, también con el ancla en una previsión); un paso guardado así en una base de
    antes sigue siendo de esta escalera (revisión de la E2-7). Sólo con el ancla en una
    previsión: con la fecha comprometida, la fecha sola es la escalera de siempre."""

    fecha: date
    clave: str
    legado: str | None = None

    @property
    def claves(self) -> tuple[str, ...]:
        """Las claves de los pasos de esta escalera: la de ahora y, si hay, la de antes."""
        return (self.clave,) if self.legado is None else (self.clave, self.legado)


SEPARADOR = "+"      # entre la fecha y la previsión que empezó el anclaje, en la clave


def anclaje(cur, task_id, comprometida: date) -> Anclaje:
    """El anclaje vigente: la fecha (la previsión vigente si es posterior a la comprometida; si
    no, la comprometida) y la clave de la racha de esa fecha en la cadena de previsiones."""
    vigente = prevision_vigente(cur, task_id)

    def fecha_de(f) -> date:
        return max(f["fecha_prevista"], comprometida) if f is not None else comprometida

    fecha = fecha_de(vigente)
    if vigente is None:
        return Anclaje(fecha, fecha.isoformat())
    cur.execute("select id, fecha_prevista, reemplaza_id from task_forecast where task_id = %s",
                (str(task_id),))
    cadena = {str(f["id"]): f for f in cur.fetchall()}
    inicio, f = vigente, vigente
    recorridas: set[str] = set()
    # Una cadena rota que vuelve sobre sí misma (dos previsiones que se reemplazan una a la otra)
    # no cuelga la escalera: el recorrido para en la primera que repite (revisión de la E2-7).
    while f is not None and fecha_de(f) == fecha and str(f["id"]) not in recorridas:
        recorridas.add(str(f["id"]))
        inicio = f
        f = cadena.get(str(f["reemplaza_id"])) if f["reemplaza_id"] is not None else None
    if f is None and fecha == comprometida:
        return Anclaje(fecha, fecha.isoformat())    # ninguna previsión movió el ancla
    return Anclaje(fecha, f"{fecha.isoformat()}{SEPARADOR}{inicio['id']}",
                   legado=fecha.isoformat() if fecha != comprometida else None)


def ancla(cur, task_id, comprometida: date) -> date:
    """La fecha del seguimiento: la previsión vigente si es posterior a la comprometida; si no,
    la comprometida."""
    return anclaje(cur, task_id, comprometida).fecha


def clave_del_anclaje(aviso: dict[str, Any]) -> str:
    """El anclaje de un paso de la escalera, que está en su clave."""
    return aviso["dedupe_key"].split(":")[3]


def fecha_de_la_clave(aviso: dict[str, Any]) -> date:
    """La fecha del anclaje de un paso de la escalera."""
    return date.fromisoformat(clave_del_anclaje(aviso).split(SEPARADOR)[0])


def al_mediodia(dia: date, zona) -> datetime:
    """Un momento del día, para contar días hábiles hasta o desde una fecha sin hora."""
    return datetime.combine(dia, time(12), zona)


def pasos(cur, task_id, de: Anclaje | date) -> list[dict[str, Any]]:
    """Los avisos de la escalera de la tarea de un anclaje (está en su clave). Con una fecha,
    los de todos los anclajes de esa fecha."""
    if isinstance(de, Anclaje):
        condicion, valor = "split_part(dedupe_key, ':', 4) = any(%s)", list(de.claves)
    else:
        condicion, valor = f"split_part(split_part(dedupe_key, ':', 4), '{SEPARADOR}', 1) = %s",             de.isoformat()
    cur.execute(f"""select * from scheduled_notice
                     where task_id = %s and tipo = any(%s) and {condicion}
                     order by creado_en, dedupe_key""",
                (str(task_id), list(TIPOS_DE_LA_ESCALERA), valor))
    return cur.fetchall()


def escalo(escalon: list[dict[str, Any]], espera: dict[str, Any] | None) -> bool:
    """La escalera de un ancla termina al escalar (mecánica §9): con su aviso de escalamiento o,
    sin ruta, con la espera escalada. Un escalamiento cuenta sólo si se dio: uno guardado todavía
    puede quedar reemplazado (por un reencuadre o un avance), y uno reemplazado no salió. La
    espera cuenta sólo si la abrió esta escalera: la de un ancla anterior, escalada y sin
    contestar, no frena a la nueva, que empieza de cero."""
    if any(a["tipo"] == "escalamiento" and a["estado"] != "guardado"
           and a["motivo_omision"] not in NO_DADOS for a in escalon):
        return True
    pedidos = [a for a in escalon if a["tipo"] != "aviso_previo"]
    if espera is None or espera["escalado_en"] is None or not pedidos:
        return False
    return espera["preguntado_en"] >= min(a["creado_en"] for a in pedidos)


def candado(cur, task_id, *, esperar: bool = True) -> bool:
    """La tarea, tomada hasta el final de la transacción: la escalera y el avance que reemplaza
    sus pasos guardados la tocan de a uno, así ninguno guarda un paso que el otro no ve. El turno
    espera (`esperar`); la escalera no: si la tarea está tomada, la deja para la vuelta siguiente
    del ciclo (devuelve `False`), y nunca espera con otras tareas tomadas."""
    clave = f"motor:escalera:{task_id}"
    if esperar:
        cur.execute("select pg_advisory_xact_lock(hashtextextended(%s, 0))", (clave,))
        return True
    cur.execute("select pg_try_advisory_xact_lock(hashtextextended(%s, 0)) as tomada", (clave,))
    return bool(cur.fetchone()["tomada"])
