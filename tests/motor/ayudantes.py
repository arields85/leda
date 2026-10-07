"""Lo que comparten las pruebas del motor: el momento fijo, el contexto mínimo de un turno,
lecturas cortas de la base y los turnos de Marcos con la IA guionada.

Las pruebas de `prueba_chica/` se importaban unas a otras como bibliotecas de ayudantes; acá
lo compartido vive en este módulo, y ningún archivo de prueba importa otro. Los nombres de
allá, sin el guion bajo: `_tarea` es `nueva_tarea`, `_hora` es `octubre`, `_dice` es `dice`,
`_prevision` es `jugada_prevision`, `_quien` es `solicitante` y `_toca`, `toca`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from leda.autoridad import identificar_en_espacio
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.motor.avisos import enviar_avisos
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_toque, procesar_turno

AHORA = datetime(2026, 10, 5, 13, 0, tzinfo=timezone.utc)   # lunes, 10:00 en Buenos Aires
VIERNES_16 = datetime(2026, 10, 16, 20, 0, tzinfo=timezone.utc)
# Las dos tareas de Marcos en las conversaciones: la del mundo y la que agrega `nueva_tarea`.
T1 = {"alias": "T1", "titulo": "Revisar el tablero"}
T2 = {"alias": "T2", "titulo": "Probar las comunicaciones"}


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


# --- Las tareas -------------------------------------------------------------------------------

def nueva_tarea(conn, mundo, titulo: str, estado: str = "asignada",
                fecha: datetime = VIERNES_16) -> str:
    """Otra tarea de Marcos, en el objetivo y el área de la del mundo."""
    with admin(conn) as cur:
        cur.execute("select objective_id, area_id from task where id = %s", (mundo["tarea"],))
        base = cur.fetchone()
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado, fecha_objetivo)
               values (%s, %s, %s, %s, %s, %s, %s) returning id""",
            (mundo["id"], base["objective_id"], titulo, base["area_id"],
             mundo["personas"]["Marcos"]["membership_id"], estado, fecha))
        tarea = str(cur.fetchone()["id"])
    conn.commit()
    return tarea


def estado_de(conn, tarea: str) -> str:
    return uno(conn, "select estado::text e from task where id = %s", tarea)["e"]






# --- Los turnos de Marcos y lo que Leda manda por su cuenta ----------------------------------

def octubre(dia: int, hora: int, minuto: int = 0) -> datetime:
    """Octubre de 2026, hora de Buenos Aires."""
    return datetime(2026, 10, dia, hora + 3, minuto, tzinfo=timezone.utc)


def dice(conn, escribe, *jugadas: Jugada, at: datetime = AHORA):
    """Un mensaje de Marcos, con las jugadas que elige la IA guionada."""
    quien, entrante = escribe("Marcos", "-", at=at)
    resultado = procesar_turno(conn, quien, entrante,
                               IAGuionada(jugadas=[list(jugadas)], redacciones=["Listo."]),
                               RelojFijo(at))
    conn.commit()
    assert resultado.error is None
    return resultado


def enviar(conn, mundo, ia: IAGuionada, at: datetime) -> dict:
    """Manda los avisos guardados cuya hora llegó (`avisos.enviar_avisos`)."""
    resumen = enviar_avisos(conn, mundo["id"], ia, RelojFijo(at))
    conn.commit()
    return resumen


def jugada_prevision(tarea: str, fecha: str, motivo: str | None = None) -> Jugada:
    return Jugada("anotar_prevision", {"tarea": tarea, "fecha": fecha,
                                       **({"motivo": motivo} if motivo else {})})



class Charla:
    """Los turnos de Marcos, uno por mensaje, con la IA guionada de cada uno."""

    def __init__(self, conn, escribe) -> None:
        self.conn, self.escribe = conn, escribe
        self.ia: IAGuionada | None = None

    def dice(self, *jugadas: Jugada, texto: str = "-"):
        quien, entrante = self.escribe("Marcos", texto)
        self.ia = IAGuionada(jugadas=[list(jugadas)], redacciones=["Listo."])
        resultado = procesar_turno(self.conn, quien, entrante, self.ia, RelojFijo(AHORA))
        self.conn.commit()
        assert resultado.error is None
        return resultado

    @property
    def redaccion(self) -> dict:
        return self.ia.pedidos_de_redaccion[-1]

    @property
    def situacion(self) -> dict:
        return self.ia.pedidos_de_jugadas[-1]


def solicitante(conn, mundo, nombre: str = "Marcos"):
    """Quién es la persona en el espacio, como la identifica el escuchador."""
    with espacio(conn, mundo["id"]) as cur:
        quien = identificar_en_espacio(cur, mundo["personas"][nombre]["telegram"], mundo["id"])
    conn.commit()
    return quien


def toca(conn, mundo, token: str, ia: IAGuionada | None = None, nombre: str = "Marcos"):
    """Un toque de la opción `token`; devuelve el resultado del turno y la IA guionada."""
    ia = ia or IAGuionada(redacciones=["Listo."])
    resultado = procesar_toque(conn, solicitante(conn, mundo, nombre), token,
                               mundo["personas"][nombre]["telegram"], ia, RelojFijo(AHORA))
    conn.commit()
    return resultado, ia
