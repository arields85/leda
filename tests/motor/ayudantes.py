"""Lo que comparten las pruebas del motor: el momento fijo, el contexto mínimo de un turno y
lecturas cortas de la base.

Las pruebas de `prueba_chica/` se importaban unas a otras como bibliotecas de ayudantes; acá
lo compartido vive en este módulo, y ningún archivo de prueba importa otro.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from leda.calendario import Calendario
from leda.db import admin

AHORA = datetime(2026, 10, 5, 13, 0, tzinfo=timezone.utc)   # lunes, 10:00 en Buenos Aires


@dataclass
class Quien:
    """Lo que el motor lee de quien escribe: su espacio y su membresía."""

    workspace_id: str
    membership_id: str
    nombre: str = ""


@dataclass
class ContextoMinimo:
    """Lo que `preguntas` lee del contexto de un turno (`fichas.Contexto`, en la capa 2): el
    cursor, quién, el momento, sus tareas y las preguntas de este mensaje."""

    cur: Any
    quien: Quien
    ahora: datetime
    calendario: Calendario
    tareas: list[dict[str, Any]] = field(default_factory=list)
    preguntas_del_turno: list[str] = field(default_factory=list)
    dejadas: list[str] = field(default_factory=list)


def contexto(cur, mundo: dict, persona: str = "Marcos", ahora: datetime = AHORA,
             tareas: list[dict[str, Any]] | None = None) -> ContextoMinimo:
    quien = Quien(mundo["id"], mundo["personas"][persona]["membership_id"], persona)
    return ContextoMinimo(cur, quien, ahora, Calendario.desde_base(cur, mundo["id"]),
                          tareas=list(tareas or []))


def uno(conn, sql: str, *args) -> dict | None:
    with admin(conn) as cur:
        cur.execute(sql, args)
        return cur.fetchone()


def todos(conn, sql: str, *args) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(sql, args)
        return cur.fetchall()


def cuantas(conn, tabla: str, donde: str = "true", *args) -> int:
    fila = uno(conn, f"select count(*) n from {tabla} where {donde}", *args)
    return fila["n"]
