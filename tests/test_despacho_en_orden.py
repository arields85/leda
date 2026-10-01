"""El orden de los mensajes de una misma respuesta (F-A1, ADR 0013 regla 2).

Dos mensajes del mismo turno ("Listo, dejé de lado el borrador…" y la pregunta
nueva) salieron en orden inverso. Causa: dos pasadas del despachador a la vez (el
despacho inmediato de después del webhook y el tick de fondo) toman la fila
siguiente con `for update skip locked`; mientras una está enviando la primera
(con su lock), la otra saltea esa fila y envía la segunda: el orden por
`programado_para` sólo vale dentro de una pasada. El despacho de un espacio se
serializa: una pasada espera a la otra y retoma desde el orden de la cola.

Concurrencia real: dos conexiones y dos hilos, sin esperas a ciegas.
"""

from __future__ import annotations

import threading
import time
from datetime import datetime, timedelta, timezone

from prisma.calendario import Calendario
from prisma.db import conectar, espacio
from prisma.despachador import TransporteDePrueba, despachar
from prisma.salida import enqueue_outbox

CHAT = 76001


class _TransporteQueSeDetiene(TransporteDePrueba):
    """Detiene el primer envío hasta que se lo libere: la pasada que lo envía
    sostiene el lock de esa fila mientras tanto."""

    def __init__(self, orden: list[str]):
        super().__init__()
        self.orden = orden
        self.enviando = threading.Event()
        self.liberar = threading.Event()
        self._primero = True

    def enviar(self, chat_id, texto, *args, **kwargs):
        if self._primero:
            self._primero = False
            self.enviando.set()
            assert self.liberar.wait(timeout=10), "nadie liberó el primer envío"
        self.orden.append(texto)
        return super().enviar(chat_id, texto, *args, **kwargs)


class _TransporteLibre(TransporteDePrueba):
    def __init__(self, orden: list[str]):
        super().__init__()
        self.orden = orden

    def enviar(self, chat_id, texto, *args, **kwargs):
        self.orden.append(texto)
        return super().enviar(chat_id, texto, *args, **kwargs)


def _encolar_la_respuesta(conn, ws, ahora):
    """Las dos partes de una respuesta: la nota (un milisegundo antes, como la
    deja `respuesta_unica.controlar`) y la pregunta."""
    with espacio(conn, ws) as cur:
        enqueue_outbox(cur, workspace_id=ws, chat_id=CHAT, text="NOTA",
                       scheduled_for=ahora - timedelta(milliseconds=1),
                       dedupe_key=f"{ws}:orden:nota", is_response=True,
                       grupo_respuesta="orden")
        enqueue_outbox(cur, workspace_id=ws, chat_id=CHAT, text="PREGUNTA",
                       scheduled_for=ahora, dedupe_key=f"{ws}:orden:pregunta",
                       is_response=True, grupo_respuesta="orden")
    conn.commit()


def _una_pasada(uri, ws, transporte, ahora, hecho: threading.Event, errores: list):
    c = conectar(uri)
    try:
        with espacio(c, ws) as cur:
            cal = Calendario.desde_base(cur, ws)
            despachar(cur, ws, transporte, cal, ahora)
        c.commit()
    except Exception as exc:  # noqa: BLE001 -- el hilo lo reporta a la prueba
        errores.append(exc)
    finally:
        c.close()
        hecho.set()


def _esperar(condicion, *, timeout=5.0):
    limite = time.monotonic() + timeout
    while time.monotonic() < limite:
        if condicion():
            return True
        time.sleep(0.01)
    return False


def test_dos_pasadas_concurrentes_no_invierten_el_orden_de_una_respuesta(
        corework, conn, uri):
    ws = corework.workspace_id
    ahora = datetime.now(timezone.utc) - timedelta(seconds=5)
    _encolar_la_respuesta(conn, ws, ahora)
    orden: list[str] = []
    errores: list[Exception] = []
    primera = _TransporteQueSeDetiene(orden)
    segunda = _TransporteLibre(orden)
    hecho1, hecho2 = threading.Event(), threading.Event()
    ahora_pasada = datetime.now(timezone.utc)

    h1 = threading.Thread(target=_una_pasada,
                          args=(uri, ws, primera, ahora_pasada, hecho1, errores))
    h2 = threading.Thread(target=_una_pasada,
                          args=(uri, ws, segunda, ahora_pasada, hecho2, errores))
    h1.start()
    try:
        assert primera.enviando.wait(timeout=10)       # la primera está enviando la nota
        h2.start()
        # La segunda no puede adelantarse: o ya terminó (el defecto) o espera.
        _esperar(lambda: hecho2.is_set() or orden, timeout=1.5)
        primera.liberar.set()
        assert hecho1.wait(timeout=10) and hecho2.wait(timeout=10)
    finally:
        primera.liberar.set()
        h1.join(timeout=10)
        h2.join(timeout=10)

    assert errores == []
    assert orden == ["NOTA", "PREGUNTA"]


def test_el_despacho_serializado_no_bloquea_a_otro_espacio(corework, conn, uri):
    """El lock es por espacio: la pasada de otro espacio no espera."""
    from tests.test_ciclo import _espacio_activo

    ws = corework.workspace_id
    with conn.cursor() as cur:
        cur.execute("set role prisma_admin")
        otro = _espacio_activo(cur, "otro-orden")
    conn.commit()
    ahora = datetime.now(timezone.utc) - timedelta(seconds=5)
    _encolar_la_respuesta(conn, ws, ahora)
    orden: list[str] = []
    errores: list[Exception] = []
    primera = _TransporteQueSeDetiene(orden)
    hecho1, hecho2 = threading.Event(), threading.Event()
    ahora_pasada = datetime.now(timezone.utc)
    h1 = threading.Thread(target=_una_pasada,
                          args=(uri, ws, primera, ahora_pasada, hecho1, errores))
    h1.start()
    try:
        assert primera.enviando.wait(timeout=10)
        h2 = threading.Thread(target=_una_pasada, args=(
            uri, otro, _TransporteLibre(orden), ahora_pasada, hecho2, errores))
        h2.start()
        assert hecho2.wait(timeout=5)                  # no esperó a la primera
        h2.join(timeout=5)
    finally:
        primera.liberar.set()
        h1.join(timeout=10)
    assert errores == []
