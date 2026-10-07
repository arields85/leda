"""El reloj de Leda en `leda_motor`: adelantarlo para probar el paso de los días (diseño
probado en la Etapa 2, E2-6).

    python -m leda.motor.reloj corework adelantar
    python -m leda.motor.reloj corework estado
    python -m leda.motor.reloj corework volver

`odd/tasks/prueba-chica-del-motor.md`, sección 10, decisión 2 del usuario: en la prueba por
Telegram, los días pasan con un comando que adelanta el reloj de Leda, sólo en `leda_motor` y
con la restricción de horario prendida, para que los días hábiles, el atraso y el horario
salgan como en un equipo real.

- **Qué guarda:** un adelanto en segundos sobre el tiempo real, en `workspace_setting`
  (`CLAVE_ADELANTO`), sin tocar el esquema. El reloj de Leda es el real más el adelanto: sigue
  corriendo.
- **Quién lo lee:** el escuchador, al empezar cada vuelta (`RelojDeLeda.refrescar`). Con ese
  reloj corren el turno, la escalera, los avisos guardados y el despacho, que recibe el momento
  y decide el horario con él (`despachador.despachar` no se toca). Los avisos a la
  administración van con el reloj real (`ciclo.py`). Lo que la base fecha sola
  (`task_state_event.at`, `blocker.abierto_en`) sigue en hora real (plan, sección 11). El
  escuchador es el del motor (`escucha.py`, E3-7).
- **`adelantar`:** al día hábil siguiente del de Leda, a la hora de salida de lo que Leda manda
  por su cuenta (`tiempo.HORA_DE_SALIDA`, 10:00; o al empezar la jornada, si a esa hora no se
  trabaja), con el calendario y los feriados del espacio: lo que se le dijo a la persona que
  sale a esa hora, sale. Correrlo otra vez adelanta otro día.
- **`volver`:** borra el adelanto. Lo escrito con el reloj adelantado queda con su hora: lo
  guardado para "mañana" de Leda sale cuando llegue esa hora real.
- **Sólo en `leda_motor`:** los tres comandos se niegan en otra base, y el reloj del
  escuchador no aplica un adelanto fuera de ella. Nunca imprime la conexión.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta

import psycopg

from ..calendario import Calendario
from ..db import admin, espacio

from .tiempo import Reloj, RelojDelSistema, sale_el

BASE_DEL_MOTOR = "leda_motor"
CLAVE_ADELANTO = "motor_reloj_adelanto_segundos"


class BaseEquivocada(ValueError):
    pass


@dataclass
class RelojDeLeda:
    """El tiempo real más el adelanto guardado. `refrescar` lo vuelve a leer."""

    real: Reloj = field(default_factory=RelojDelSistema)
    base: str = BASE_DEL_MOTOR
    adelanto: timedelta = timedelta(0)

    def ahora(self) -> datetime:
        return self.real.ahora() + self.adelanto

    def medir(self) -> float:
        return self.real.medir()

    def refrescar(self, conn: psycopg.Connection, workspace_id: str) -> bool:
        """Lee el adelanto (cero fuera de `base`). Devuelve si cambió; quien llama confirma."""
        antes = self.adelanto
        self.adelanto = leer_adelanto(conn, workspace_id, base=self.base)
        return self.adelanto != antes


@dataclass(frozen=True)
class EstadoDelReloj:
    real: datetime
    leda: datetime
    adelanto: timedelta
    en_horario: bool
    restriccion_prendida: bool


def leer_adelanto(conn: psycopg.Connection, workspace_id: str, *,
                  base: str = BASE_DEL_MOTOR) -> timedelta:
    if conn.info.dbname != base:
        return timedelta(0)
    with espacio(conn, workspace_id) as cur:
        cur.execute("select valor from workspace_setting where clave = %s", (CLAVE_ADELANTO,))
        fila = cur.fetchone()
    return timedelta(seconds=int(fila["valor"])) if fila else timedelta(0)


def adelantar(conn: psycopg.Connection, workspace_id: str, real: Reloj, *,
              base: str = BASE_DEL_MOTOR) -> EstadoDelReloj:
    """Lleva el reloj de Leda al día hábil siguiente, a la hora de salida (en horario)."""
    _comprobar(conn, base)
    adelanto = leer_adelanto(conn, workspace_id, base=base)
    ahora = real.ahora()
    with admin(conn) as cur:
        cal = Calendario.desde_base(cur, workspace_id)
        dia = (ahora + adelanto).astimezone(cal.zona).date() + timedelta(days=1)
        while not cal.es_habil(dia):
            dia += timedelta(days=1)
        objetivo = sale_el(cal, dia)
        cur.execute(
            """insert into workspace_setting (workspace_id, clave, valor)
               values (%s, %s, %s)
               on conflict (workspace_id, clave) do update set valor = excluded.valor""",
            (workspace_id, CLAVE_ADELANTO, str(round((objetivo - ahora).total_seconds()))))
    conn.commit()
    return estado(conn, workspace_id, real, base=base)


def volver(conn: psycopg.Connection, workspace_id: str, real: Reloj, *,
           base: str = BASE_DEL_MOTOR) -> EstadoDelReloj:
    """El reloj de Leda vuelve al tiempo real."""
    _comprobar(conn, base)
    with admin(conn) as cur:
        cur.execute("delete from workspace_setting where workspace_id = %s and clave = %s",
                    (workspace_id, CLAVE_ADELANTO))
    conn.commit()
    return estado(conn, workspace_id, real, base=base)


def estado(conn: psycopg.Connection, workspace_id: str, real: Reloj, *,
           base: str = BASE_DEL_MOTOR) -> EstadoDelReloj:
    _comprobar(conn, base)
    adelanto = leer_adelanto(conn, workspace_id, base=base)
    with espacio(conn, workspace_id) as cur:
        cal = Calendario.desde_base(cur, workspace_id)
    conn.commit()
    ahora = real.ahora()
    leda = (ahora + adelanto).astimezone(cal.zona)
    # Apagada, el horario es todos los días de 00:00 a 23:59 (`tools/restriccion_horario.py`).
    apagada = (len(cal.dias) == 7 and cal.hora_inicio == time(0, 0)
               and cal.hora_fin.replace(second=0, microsecond=0) == time(23, 59))
    return EstadoDelReloj(ahora.astimezone(cal.zona), leda, adelanto, cal.en_horario(leda),
                          not apagada)


def _comprobar(conn: psycopg.Connection, base: str) -> None:
    if conn.info.dbname != base:
        raise BaseEquivocada(f"El reloj de Leda sólo se mueve en {BASE_DEL_MOTOR!r}; esta base "
                             f"es {conn.info.dbname!r}.")


def _mostrar(e: EstadoDelReloj) -> str:
    dias = e.adelanto.days
    resto = e.adelanto - timedelta(days=dias)
    return "\n".join((
        f"hora real:     {e.real:%a %d/%m %H:%M}",
        f"reloj de Leda: {e.leda:%a %d/%m %H:%M}"
        + (f"  (adelantado {dias} d {resto})" if e.adelanto else "  (tiempo real)"),
        f"horario del espacio: {'en horario' if e.en_horario else 'fuera de horario'}; "
        f"restricción de horario {'prendida' if e.restriccion_prendida else 'APAGADA'}",
    ))


def main(argv: list[str] | None = None) -> int:
    from ..db import conectar

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")    # la consola de Windows no es UTF-8
    p = argparse.ArgumentParser(prog="python -m leda.motor.reloj")
    p.add_argument("slug")
    p.add_argument("accion", choices=("adelantar", "estado", "volver"))
    a = p.parse_args(argv)

    conn = conectar()
    try:
        _comprobar(conn, BASE_DEL_MOTOR)
    except BaseEquivocada as e:
        print(f"STOP: {e}")
        return 1
    with admin(conn) as cur:
        cur.execute("select id from workspace where slug = %s and activo", (a.slug,))
        fila = cur.fetchone()
    conn.commit()
    if fila is None:
        print(f"No hay un espacio activo '{a.slug}'.")
        return 1
    comando = {"adelantar": adelantar, "estado": estado, "volver": volver}[a.accion]
    resultado = comando(conn, str(fila["id"]), RelojDelSistema())
    print(f"base: {conn.info.dbname} · espacio: {a.slug}")
    print(_mostrar(resultado))
    if not resultado.restriccion_prendida:
        print("Ojo: con la restricción apagada todos los días son hábiles. Para esta prueba va "
              "prendida (decisión 10.2): tools/restriccion_horario.py prender " + a.slug)
    if a.accion != "estado":
        print("El escuchador lo toma al empezar su próxima vuelta (hasta 25 segundos).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
