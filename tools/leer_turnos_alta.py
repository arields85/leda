"""Muestra los turnos del alta conducida por el modelo y los incidentes recientes de
la base de prueba: por cada intento del modelo, el resultado, la duración y, si se
rechazó, el motivo y la forma de la salida (sin texto libre). Es lo que permite saber
POR QUÉ un turno terminó en "Tuve un problema…".

Herramienta de desarrollo, sólo lee. Usa la base de `PRISMA_DB_URL` del checkout desde
el que se corre (worktree con `PYTHONPATH=src` para `prisma_flujo`). Nunca imprime
valores del `.env`: sólo el nombre de la base, para confirmar cuál es.

Uso: python tools/leer_turnos_alta.py [minutos]
"""
import sys

import psycopg
from psycopg.rows import dict_row

from prisma import config

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 40

with psycopg.connect(config.config.db_url, row_factory=dict_row) as c:
    base = c.execute("select current_database() as db").fetchone()["db"]
    print(f"base: {base}")
    print("-- turnos del alta conducida (alta_conducida_turno)")
    for r in c.execute(
            """select at, detalle from prisma.audit_log
                where accion = 'alta_conducida_turno'
                  and at > now() - make_interval(mins => %(m)s) order by at""",
            {"m": MIN}).fetchall():
        print(r["at"].strftime("%H:%M:%S"), r["detalle"])
    print("-- incidentes")
    for r in c.execute(
            """select at, etapa, severidad, resumen_sanitizado from prisma.incident
                where at > now() - make_interval(mins => %(m)s) order by at""",
            {"m": MIN}).fetchall():
        print(r["at"].strftime("%H:%M:%S"), r["etapa"], r["severidad"],
              r["resumen_sanitizado"])
