"""Calendario laboral de un espacio.

Toda la escalera de recordatorios se cuenta en días hábiles. Sin esto, una
tarea que vence un viernes escalaría el lunes, cuando en realidad todavía no
pasó ni un día de trabajo.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]


@dataclass(frozen=True)
class Calendario:
    dias: frozenset[int]          # 0 = lunes
    hora_inicio: time
    hora_fin: time
    feriados: frozenset[date]
    zona: ZoneInfo

    @classmethod
    def desde_base(cls, cur, workspace_id: str) -> "Calendario":
        cur.execute(
            """select c.dias, c.hora_inicio, c.hora_fin, w.zona_horaria
                 from work_calendar c join workspace w on w.id = c.workspace_id
                where c.workspace_id = %s""",
            (workspace_id,))
        fila = cur.fetchone()
        if not fila:
            raise LookupError(
                "El espacio no tiene calendario laboral. El núcleo lo exige "
                "porque toda la escalera se calcula sobre él.")
        cur.execute("select fecha from holiday where workspace_id = %s", (workspace_id,))
        feriados = {f["fecha"] for f in cur.fetchall()}
        indices = {DIAS.index(d) for d in fila["dias"] if d in DIAS}
        return cls(frozenset(indices), fila["hora_inicio"], fila["hora_fin"],
                   frozenset(feriados), ZoneInfo(fila["zona_horaria"]))

    # -- consultas ---------------------------------------------------------

    def es_habil(self, d: date) -> bool:
        return d.weekday() in self.dias and d not in self.feriados

    def en_horario(self, momento: datetime) -> bool:
        local = momento.astimezone(self.zona)
        return self.es_habil(local.date()) and self.hora_inicio <= local.time() <= self.hora_fin

    def proximo_habil(self, d: date) -> date:
        while not self.es_habil(d):
            d += timedelta(days=1)
        return d

    def sumar_habiles(self, momento: datetime, dias: int) -> datetime:
        """Suma días hábiles conservando la hora, saltando feriados y fines de
        semana. Con dias=0 devuelve el mismo momento corrido al próximo hábil."""
        local = momento.astimezone(self.zona)
        d = local.date()
        restantes = dias
        while restantes > 0:
            d += timedelta(days=1)
            if self.es_habil(d):
                restantes -= 1
        d = self.proximo_habil(d)
        return datetime.combine(d, local.time(), tzinfo=self.zona)

    def habiles_entre(self, desde: datetime, hasta: datetime) -> int:
        a = desde.astimezone(self.zona).date()
        b = hasta.astimezone(self.zona).date()
        if b < a:
            return -self.habiles_entre(hasta, desde)
        n = 0
        d = a
        while d < b:
            d += timedelta(days=1)
            if self.es_habil(d):
                n += 1
        return n

    def dentro_de_jornada(self, momento: datetime) -> datetime:
        """Corre un momento al próximo instante hábil.

        Prisma no escribe fuera de horario salvo urgencia autorizada; el
        despachador usa esto para postergar en vez de descartar.
        """
        local = momento.astimezone(self.zona)
        if self.es_habil(local.date()):
            if local.time() < self.hora_inicio:
                return datetime.combine(local.date(), self.hora_inicio, tzinfo=self.zona)
            if local.time() <= self.hora_fin:
                return local
        d = self.proximo_habil(local.date() + timedelta(days=1))
        return datetime.combine(d, self.hora_inicio, tzinfo=self.zona)


DIAS_LEGIBLES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado",
                 "domingo"]


def cuando_legible(momento: datetime, ahora: datetime, zona: ZoneInfo) -> str:
    """Un instante como lo dice una persona, en la hora local del espacio: "hoy a
    las 08:00", "mañana a las 08:00", "el lunes a las 08:00" (dentro de la semana)
    o "el 15/10 a las 08:00"."""
    local = momento.astimezone(zona)
    dias = (local.date() - ahora.astimezone(zona).date()).days
    hora = local.strftime("%H:%M")
    if dias <= 0:
        return f"hoy a las {hora}"
    if dias == 1:
        return f"mañana a las {hora}"
    if dias < 7:
        return f"el {DIAS_LEGIBLES[local.weekday()]} a las {hora}"
    return f"el {local.strftime('%d/%m')} a las {hora}"


FERIADOS_AR_2026 = [
    date(2026, 1, 1), date(2026, 2, 16), date(2026, 2, 17), date(2026, 3, 24),
    date(2026, 4, 2), date(2026, 4, 3), date(2026, 5, 1), date(2026, 5, 25),
    date(2026, 6, 15), date(2026, 6, 20), date(2026, 7, 9), date(2026, 8, 17),
    date(2026, 10, 12), date(2026, 11, 23), date(2026, 12, 8), date(2026, 12, 25),
]


def cargar_feriados_ar(cur, workspace_id: str, feriados=FERIADOS_AR_2026) -> None:
    for f in feriados:
        cur.execute(
            "insert into holiday (workspace_id, fecha) values (%s, %s) "
            "on conflict do nothing", (workspace_id, f))
