"""Turns the working-hours restriction of a workspace off or on, for development.

"Apagá la restricción de horario" means: let Leda send every message at any time,
so a real Telegram test does not wait for working hours. The restriction is not a
code rule: it is the workspace's working calendar (`work_calendar`, loaded from the
pack's `calendario`), and constitution §8 only forbids writing outside *that*
calendar. Turning it off sets the calendar to every day, 00:00-23:59; turning it on
restores it from the pack.

Usage, from the worktree whose database is the target, with PYTHONPATH=src:
  python tools/restriccion_horario.py apagar <espacio>
  python tools/restriccion_horario.py prender <espacio> [--pack espacios/<espacio>.yaml]
  python tools/restriccion_horario.py estado <espacio>

Only works on the development databases (`leda`, `leda_flujo`, `leda_motor`). Side
effect while off: every day counts as a working day, so reminder deadlines in working
days get shorter. Prints only the database name and the calendar, never the
connection. In `leda_motor` the Motor's small test keeps the restriction on and moves
Leda's clock instead (`python -m leda.motor.reloj`, user decision 10.2 in
`odd/tasks/prueba-chica-del-motor.md`).
"""
import pathlib
import sys

import yaml

from leda.db import conectar

BASES_DE_DESARROLLO = {"leda", "leda_flujo", "leda_motor"}
TODOS_LOS_DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]


def _calendario(cur, ws):
    cur.execute("select dias, hora_inicio, hora_fin from work_calendar where workspace_id = %s",
                (ws,))
    return cur.fetchone()


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in {"apagar", "prender", "estado"}:
        print(__doc__)
        return 2
    accion, espacio = sys.argv[1], sys.argv[2]
    conn = conectar()
    base = conn.info.dbname
    if base not in BASES_DE_DESARROLLO:
        print(f"STOP: {base!r} no es una base de desarrollo ({sorted(BASES_DE_DESARROLLO)}).")
        return 1
    with conn, conn.cursor() as cur:
        cur.execute("select id from workspace where slug = %s", (espacio,))
        fila = cur.fetchone()
        if not fila:
            print(f"STOP: no existe el espacio {espacio!r} en {base}.")
            return 1
        ws = fila["id"]
        antes = _calendario(cur, ws)
        if accion == "apagar":
            cur.execute("""update work_calendar set dias = %s, hora_inicio = '00:00',
                                  hora_fin = '23:59' where workspace_id = %s""",
                        (TODOS_LOS_DIAS, ws))
        elif accion == "prender":
            ruta = pathlib.Path(sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == "--pack"
                                else f"espacios/{espacio}.yaml")
            cal = (yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}).get("calendario") or {}
            if not cal.get("dias") or "-" not in str(cal.get("horario", "")):
                print(f"STOP: el pack {ruta} no tiene un calendario completo.")
                return 1
            inicio, _, fin = str(cal["horario"]).partition("-")
            cur.execute("""update work_calendar set dias = %s, hora_inicio = %s, hora_fin = %s
                            where workspace_id = %s""",
                        (cal["dias"], inicio.strip(), fin.strip(), ws))
        despues = _calendario(cur, ws)
    print(f"base: {base} · espacio: {espacio}")
    print(f"antes:   {antes['dias']} {antes['hora_inicio']:%H:%M}-{antes['hora_fin']:%H:%M}")
    if accion != "estado":
        print(f"después: {despues['dias']} {despues['hora_inicio']:%H:%M}-{despues['hora_fin']:%H:%M}")
    apagada = (len(despues["dias"]) == 7 and despues["hora_inicio"].strftime("%H:%M") == "00:00"
               and despues["hora_fin"].strftime("%H:%M") == "23:59")
    print("restricción de horario:", "APAGADA" if apagada else "prendida")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
