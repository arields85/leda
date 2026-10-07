"""Los avisos de coordinación quedan fuera del tope diario (decisión del usuario,
2026-09-30: "deben llegar todos los avisos").

`nucleo/mecanica-pm.md` §10 (volumen de contacto) limita los mensajes
automáticos por persona y por día (3 en corework). Ese tope es para los
seguimientos: cadencias, recordatorios de la escalera. Lo que una persona hizo
sobre trabajo compartido y otra necesita para actuar o enterarse -- una entrega
para revisar, cambios pedidos, una aprobación, un borrador para confirmar, un
borrador rechazado -- no cuenta contra el tope ni lo posterga (`es_coordinacion`).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from leda import herramientas as H
from leda.autoridad import Canal, identificar
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.despachador import TransporteDePrueba, despachar
from leda.salida import enqueue_outbox

# Lo que sigue venía de `tests/test_ramas_cerradas_al_terminar_el_flujo.py`, que se
# retiró con los flujos A y B (E3-4).

# La pasada del despachador corre a una hora FIJA de la jornada -- un martes a las
# 10:00 de Buenos Aires, en el pasado de cualquier ejecución --, no a la que marque
# el reloj de quien corre la suite.
_AHORA_FIJO = datetime(2026, 9, 29, 13, 0, tzinfo=timezone.utc)

_FILAS_A_MOVER = (
    ("inbound_message", ("at",)),
    ("message_outbox", ("programado_para", "vence_en")),
    ("pending_action", ("vence_en",)),
)


class _Reloj:
    """Lleva lo que la prueba escribió con el reloj real a la hora fija de la pasada,
    sin cambiar las distancias entre la actividad de la persona, los avisos y sus
    vencimientos: sólo cambia la hora del día. Cada fila se mueve UNA vez, aunque
    `en_horario` se llame varias veces en la misma prueba."""

    def __init__(self, conn, ws) -> None:
        self._conn = conn
        self._ws = ws
        self._movidas: dict[str, set] = {tabla: set() for tabla, _ in _FILAS_A_MOVER}
        with espacio(conn, ws) as cur:
            self._cal = Calendario.desde_base(cur, ws)
        # Un `ahora` fuera de la jornada volvería a mover las filas hasta la
        # próxima: la prueba se rompería por el calendario, no por lo que prueba.
        assert self._cal.en_horario(self.ahora), "la hora fija dejó de ser laboral"

    @property
    def ahora(self) -> datetime:
        return _AHORA_FIJO + timedelta(seconds=5)

    def en_horario(self) -> datetime:
        desfase = _AHORA_FIJO - datetime.now(timezone.utc)
        with admin(self._conn) as cur:
            for tabla, columnas in _FILAS_A_MOVER:
                cur.execute(f"select id from {tabla} where workspace_id = %s",
                            (self._ws,))
                nuevas = ({f["id"] for f in cur.fetchall()} - self._movidas[tabla])
                if not nuevas:
                    continue
                cambios = ", ".join(f"{c} = {c} + %(d)s" for c in columnas)
                cur.execute(f"update {tabla} set {cambios} where id = any(%(ids)s)",
                            {"d": desfase, "ids": list(nuevas)})
                self._movidas[tabla] |= nuevas
        self._conn.commit()
        return self.ahora


@pytest.fixture
def reloj(conn, corework) -> _Reloj:
    return _Reloj(conn, corework.workspace_id)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _pasada(conn, ws, ahora):
    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        resumen = despachar(cur, ws, transporte, cal, ahora)
    conn.commit()
    return resumen, transporte


def _enviados_a(transporte, chat_id: int) -> list[str]:
    return [e.texto for e in transporte.enviados if e.chat_id == chat_id]


def _seguimientos(cur, ws, tg, membership_id, n, *, prefijo):
    for i in range(n):
        enqueue_outbox(cur, workspace_id=ws, chat_id=tg, text=f"Seguimiento {i}",
                       recipient_membership_id=membership_id,
                       message_type="seguimiento",
                       scheduled_for=datetime.now(timezone.utc)
                       - timedelta(minutes=2), dedupe_key=f"{prefijo}:s{i}")


def _avisos(cur, ws, quien, membership_id, n, *, prefijo):
    for i in range(n):
        H._avisar(cur, quien, membership_id, f"Aviso de coordinación {i}",
                  dedupe_key=f"{ws}:{prefijo}:c{i}")


def _nahuel(conn, ws):
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        cur.execute("select telegram_user_id t from integrante where nombre = %s",
                    ("Nahuel Gimenez",))
        return quien, cur.fetchone()["t"]


def test_cinco_avisos_de_coordinacion_en_un_dia_salen_todos(corework, conn, reloj):
    ws = corework.workspace_id
    nahuel, tg = _nahuel(conn, ws)
    with espacio(conn, ws) as cur:
        _avisos(cur, ws, nahuel, nahuel.membership_id, 5, prefijo="tope-c")
    conn.commit()

    resumen, transporte = _pasada(conn, ws, reloj.en_horario())

    enviados = [t for t in _enviados_a(transporte, tg) if "coordinación" in t]
    assert len(enviados) == 5
    assert resumen["pospuestos"] == 0


def test_los_seguimientos_siguen_deteniendose_en_el_tope(corework, conn, reloj):
    ws = corework.workspace_id
    nahuel, tg = _nahuel(conn, ws)
    with espacio(conn, ws) as cur:
        _seguimientos(cur, ws, tg, nahuel.membership_id, 5, prefijo="tope-s")
    conn.commit()

    resumen, transporte = _pasada(conn, ws, reloj.en_horario())

    assert len([t for t in _enviados_a(transporte, tg)
                if t.startswith("Seguimiento")]) == 3
    assert resumen["pospuestos"] == 2


def test_un_aviso_de_coordinacion_no_consume_la_cuota_de_los_seguimientos(
        corework, conn, reloj):
    """La lectura conservadora: no cuenta en absoluto. Cinco avisos de coordinación
    ya enviados hoy no le quitan a la persona ninguno de sus tres seguimientos."""
    ws = corework.workspace_id
    nahuel, tg = _nahuel(conn, ws)
    ahora = reloj.en_horario()
    with espacio(conn, ws) as cur:
        _avisos(cur, ws, nahuel, nahuel.membership_id, 5, prefijo="cuota")
    conn.commit()
    _pasada(conn, ws, ahora)
    with espacio(conn, ws) as cur:
        _seguimientos(cur, ws, tg, nahuel.membership_id, 4, prefijo="cuota")
    ahora = reloj.en_horario()

    resumen, transporte = _pasada(conn, ws, ahora)

    assert len([t for t in _enviados_a(transporte, tg)
                if t.startswith("Seguimiento")]) == 3
    assert resumen["pospuestos"] == 1


def test_las_herramientas_que_avisan_de_un_acto_ajeno_marcan_el_aviso(
        corework, conn):
    ws = corework.workspace_id
    nahuel, tg = _nahuel(conn, ws)
    with espacio(conn, ws) as cur:
        H._avisar(cur, nahuel, nahuel.membership_id, "Marcos aprobó «X»",
                  dedupe_key=f"{ws}:marca:1")
        cur.execute("select es_coordinacion from message_outbox "
                    "where dedupe_key = %s", (f"{ws}:marca:1",))
        assert cur.fetchone()["es_coordinacion"] is True
        enqueue_outbox(cur, workspace_id=ws, chat_id=tg, text="Recordatorio",
                       dedupe_key=f"{ws}:marca:2")
        cur.execute("select es_coordinacion from message_outbox "
                    "where dedupe_key = %s", (f"{ws}:marca:2",))
        assert cur.fetchone()["es_coordinacion"] is False
