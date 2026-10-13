"""El reloj de Leda en `leda_motor`: adelantarlo para probar el paso de los días (diseño
probado en la Etapa 2, E2-6).

    python -m leda.motor.reloj corework adelantar
    python -m leda.motor.reloj corework estado
    python -m leda.motor.reloj corework hora 22:30
    python -m leda.motor.reloj corework volver [--forzar]

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
- **`hora HH:MM`:** lleva el reloj de Leda a esa hora del día en que está, sólo hacia adelante.
- **`volver`:** borra el adelanto. Lo escrito con el reloj adelantado queda con su hora: lo
  guardado para "mañana" de Leda sale cuando llegue esa hora real.
- **Nunca antes de lo registrado** (T6, prueba por Telegram del 2026-10-12): `volver` y después
  `adelantar` llevaron a Leda del miércoles al martes del lunes real, con turnos ya fechados el
  martes más tarde; lo registrado quedó en su futuro y las reglas que lo leen se confundieron
  (la de no interrumpir anunció "hoy a las 12:15"). El piso (`ultimo_registrado`) es lo último
  que Leda fechó con su reloj en el espacio: `adelantar` y `hora` no llevan el reloj antes de él
  (`HoraAtrasada`), y `volver` se niega si la hora real queda antes, salvo con `--forzar`, que es
  sólo para empezar de cero con la base recreada.
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


class HoraAtrasada(ValueError):
    """El reloj de Leda nunca va para atrás: lo ya registrado quedaría en el futuro."""


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


def ultimo_registrado(conn: psycopg.Connection, workspace_id: str) -> datetime | None:
    """El piso del reloj: lo último que Leda fechó con su propio reloj en el espacio, o `None`
    si todavía no fechó nada. Sólo cuentan las columnas que se escriben siempre con
    `reloj.ahora()` del motor: `conversation_turn.at` (`registro.py`) y
    `scheduled_notice.creado_en` (`avisos.guardar` y `fichas.py`). Quedan afuera
    `programado_para`, que mira al futuro a propósito, y `message_outbox.enviado_en`, que el
    despacho de la consola (`cli.py despachar`) fecha con el reloj real. Con la RLS del espacio,
    como `leer_adelanto`."""
    with espacio(conn, workspace_id) as cur:
        cur.execute("""select greatest((select max(at) from conversation_turn),
                                        (select max(creado_en) from scheduled_notice)) as piso""")
        fila = cur.fetchone()
    return fila["piso"] if fila else None


def _no_antes_del_piso(conn: psycopg.Connection, workspace_id: str, objetivo: datetime,
                       zona, *, porque: str = "el reloj no va antes de eso.") -> None:
    piso = ultimo_registrado(conn, workspace_id)
    if piso is not None and objetivo < piso:
        raise HoraAtrasada(
            f"Leda ya registró hasta el {piso.astimezone(zona):%a %d/%m %H:%M}; {porque}")


def adelantar(conn: psycopg.Connection, workspace_id: str, real: Reloj, *,
              base: str = BASE_DEL_MOTOR) -> EstadoDelReloj:
    """Lleva el reloj de Leda al día hábil siguiente, a la hora de salida (en horario). Nunca
    antes de lo ya registrado (`HoraAtrasada`)."""
    _comprobar(conn, base)
    adelanto = leer_adelanto(conn, workspace_id, base=base)
    ahora = real.ahora()
    with admin(conn) as cur:
        cal = Calendario.desde_base(cur, workspace_id)
        dia = (ahora + adelanto).astimezone(cal.zona).date() + timedelta(days=1)
        while not cal.es_habil(dia):
            dia += timedelta(days=1)
        objetivo = sale_el(cal, dia)
    conn.commit()
    _no_antes_del_piso(conn, workspace_id, objetivo, cal.zona)
    with admin(conn) as cur:
        cur.execute(
            """insert into workspace_setting (workspace_id, clave, valor)
               values (%s, %s, %s)
               on conflict (workspace_id, clave) do update set valor = excluded.valor""",
            (workspace_id, CLAVE_ADELANTO, str(round((objetivo - ahora).total_seconds()))))
    conn.commit()
    return estado(conn, workspace_id, real, base=base)


def a_la_hora(conn: psycopg.Connection, workspace_id: str, real: Reloj, hora: time, *,
              base: str = BASE_DEL_MOTOR) -> EstadoDelReloj:
    """Lleva el reloj de Leda a `hora` del día en que está, para probar de noche sin esperar
    (usuario, 2026-10-07). Sólo hacia adelante y nunca antes de lo ya registrado
    (`HoraAtrasada`)."""
    _comprobar(conn, base)
    adelanto = leer_adelanto(conn, workspace_id, base=base)
    ahora = real.ahora()
    with admin(conn) as cur:
        cal = Calendario.desde_base(cur, workspace_id)
    conn.commit()
    leda = (ahora + adelanto).astimezone(cal.zona)
    objetivo = datetime.combine(leda.date(), hora, cal.zona)
    if objetivo <= leda:
        raise HoraAtrasada(f"El reloj de Leda ya está en {leda:%H:%M}; sólo va hacia adelante.")
    _no_antes_del_piso(conn, workspace_id, objetivo, cal.zona)
    with admin(conn) as cur:
        cur.execute(
            """insert into workspace_setting (workspace_id, clave, valor)
               values (%s, %s, %s)
               on conflict (workspace_id, clave) do update set valor = excluded.valor""",
            (workspace_id, CLAVE_ADELANTO, str(round((objetivo - ahora).total_seconds()))))
    conn.commit()
    return estado(conn, workspace_id, real, base=base)


def volver(conn: psycopg.Connection, workspace_id: str, real: Reloj, *,
           base: str = BASE_DEL_MOTOR, forzar: bool = False) -> EstadoDelReloj:
    """El reloj de Leda vuelve al tiempo real. Se niega si la hora real queda antes de lo ya
    registrado (`HoraAtrasada`), salvo con `forzar`, sólo para empezar de cero con la base
    recreada."""
    _comprobar(conn, base)
    if not forzar:
        with espacio(conn, workspace_id) as cur:
            zona = Calendario.desde_base(cur, workspace_id).zona
        conn.commit()
        _no_antes_del_piso(conn, workspace_id, real.ahora(), zona,
                           porque="volver al tiempo real la dejaría antes. Sólo con --forzar, "
                                  "para empezar de cero con la base recreada.")
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
    p.add_argument("accion", choices=("adelantar", "estado", "volver", "hora"))
    p.add_argument("hhmm", nargs="?", help='con "hora": la hora del mismo día, por ejemplo 22:30')
    p.add_argument("--forzar", action="store_true",
                   help="con volver: aunque Leda quede antes de lo ya registrado (sólo para "
                        "empezar de cero con la base recreada)")
    a = p.parse_args(argv)
    if a.forzar and a.accion != "volver":
        print("--forzar va sólo con volver.")
        return 1
    if a.accion == "hora":
        try:
            hora = datetime.strptime(a.hhmm or "", "%H:%M").time()
        except ValueError:
            print('Falta la hora, como "22:30".')
            return 1

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
    ws = str(fila["id"])
    try:
        if a.accion == "hora":
            resultado = a_la_hora(conn, ws, RelojDelSistema(), hora)
        elif a.accion == "volver":
            resultado = volver(conn, ws, RelojDelSistema(), forzar=a.forzar)
        else:
            resultado = {"adelantar": adelantar, "estado": estado}[a.accion](
                conn, ws, RelojDelSistema())
    except HoraAtrasada as e:
        print(f"STOP: {e}")
        return 1
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
