"""El registro de turnos (`leda.motor.registro`; ADR 0018, decisión 3.2).

En la prueba chica estas funciones vivían en `turno.py` y se probaban a través del turno; acá
se fijan solas: cada turno con su número, los últimos turnos en orden y con su texto, y una
redacción vacía como una IA que no respondió.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from leda.db import espacio
from leda.motor import registro
from leda.motor.ia import Jugada
from leda.salida import enqueue_outbox

from tests.motor.ayudantes import AHORA, todos


def test_cada_turno_lleva_su_numero_y_los_ultimos_salen_en_orden(conn, mundo, escribe):
    quien, entrante = escribe("Marcos", "arranqué con el tablero")
    with espacio(conn, mundo["id"]) as cur:
        turno = registro.registrar_entrada(
            cur, workspace_id=mundo["id"], membership_id=quien.membership_id,
            entrante_id=entrante, ahora=AHORA,
            jugadas=[Jugada("iniciar_tarea", {"tarea": "T1"})],
            resultado={"hechos": [{"resultado": "anotado"}]}, ia_nombre="guionada",
            latencia_ms=12, error=None)
        enqueue_outbox(cur, workspace_id=mundo["id"], chat_id=mundo["personas"]["Marcos"]["telegram"],
                       text="Anotado.", dedupe_key="motor:respuesta:prueba",
                       recipient_membership_id=quien.membership_id, is_response=True,
                       scheduled_for=AHORA)
        cur.execute("select id from message_outbox where dedupe_key = 'motor:respuesta:prueba'")
        registro.registrar_salida(cur, mundo["id"], quien.membership_id,
                                  str(cur.fetchone()["id"]), "guionada",
                                  AHORA + timedelta(seconds=1))
        ultimos = registro.leer_ultimos_turnos(cur, quien.membership_id)

    filas = todos(conn, "select id, sentido, numero, jugadas from conversation_turn order by numero")
    assert [(f["sentido"], f["numero"]) for f in filas] == [("entrada", 1), ("salida", 2)]
    assert str(filas[0]["id"]) == turno
    assert filas[0]["jugadas"] == [{"nombre": "iniciar_tarea", "datos": {"tarea": "T1"}}]
    assert [(t["sentido"], t["texto"]) for t in ultimos] == [
        ("entrada", "arranqué con el tablero"), ("salida", "Anotado.")]
    assert ultimos[0]["hechos"] == [{"resultado": "anotado"}]
    assert "toco" not in ultimos[0]


def test_los_ultimos_turnos_son_los_diez_mas_nuevos(conn, mundo):
    marcos = mundo["personas"]["Marcos"]["membership_id"]
    with espacio(conn, mundo["id"]) as cur:
        for n in range(registro.ULTIMOS_TURNOS + 2):
            registro.registrar_entrada(
                cur, workspace_id=mundo["id"], membership_id=marcos, entrante_id=None,
                ahora=AHORA + timedelta(minutes=n), jugadas=None, resultado=None,
                ia_nombre="guionada", latencia_ms=0, error="ia_no_respondio")
        ultimos = registro.leer_ultimos_turnos(cur, marcos)
        siguiente = registro.siguiente_numero(cur, marcos)

    assert len(ultimos) == registro.ULTIMOS_TURNOS
    momentos = [datetime.fromisoformat(t["at"]) for t in ultimos]
    assert momentos == [AHORA + timedelta(minutes=n) for n in range(2, 12)]
    assert siguiente == registro.ULTIMOS_TURNOS + 3


def test_una_redaccion_vacia_es_una_ia_que_no_respondio():
    assert registro.no_vacio("  Listo.\n") == "Listo."
    for vacia in ("", "   ", None):
        with pytest.raises(ValueError):
            registro.no_vacio(vacia)
