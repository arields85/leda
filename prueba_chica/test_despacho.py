"""El despachador manda los mensajes del motor en `leda_motor` (E2-2).

`odd/tasks/prueba-chica-del-motor.md`, sección 11: `despachador` retenía lo que Leda inicia
mientras la persona tenía abierta una rama de los flujos congelados (enredo 2). Esa retención
se retiró con ellos (E3-3); las tablas de esas ramas quedan vacías en `leda_motor`, y con las
tablas del motor en uso (una pregunta abierta, un turno recién registrado) y la persona activa
en el chat, sale todo.
"""

from __future__ import annotations

from prueba_chica.conftest import AHORA
from prueba_chica.ia import IAGuionada
from prueba_chica.tiempo import RelojFijo
from prueba_chica.turno import procesar_turno

from leda.calendario import Calendario
from leda.db import espacio
from leda.despachador import TransporteDePrueba, despachar
from leda.salida import enqueue_outbox

TABLAS_DE_LAS_RAMAS_CONGELADAS = (
    "pending_action", "task_intake_request", "task_intake_choice_set", "pending_reply")


def test_el_despachador_manda_la_respuesta_y_lo_que_leda_inicia(conn, mundo, escribe):
    quien, entrante = escribe("Marcos", "arranqué")    # activo en el chat, a las 10:00
    procesar_turno(conn, quien, entrante, IAGuionada(jugadas=[[]], redacciones=["Anotado."]),
                   RelojFijo(AHORA))
    marcos = mundo["personas"]["Marcos"]
    with espacio(conn, mundo["id"]) as cur:
        cur.execute(
            """insert into conversation_question (workspace_id, membership_id, tipo, task_id,
                                                  se_puede_dejar, abierta_en)
               values (%s, %s, 'quien_destraba', %s, false, %s)""",
            (mundo["id"], marcos["membership_id"], mundo["tarea"], AHORA))
        # Lo que Leda inicia por su cuenta: un aviso, que no es respuesta.
        enqueue_outbox(cur, workspace_id=mundo["id"], chat_id=marcos["telegram"],
                       text="Mañana vence Revisar el tablero.", dedupe_key="motor:aviso:1",
                       recipient_membership_id=marcos["membership_id"],
                       scheduled_for=AHORA)
        for tabla in TABLAS_DE_LAS_RAMAS_CONGELADAS:
            cur.execute(f"select count(*) n from {tabla}")
            assert cur.fetchone()["n"] == 0, tabla
    conn.commit()

    transporte = TransporteDePrueba()
    with espacio(conn, mundo["id"]) as cur:
        resumen = despachar(cur, mundo["id"], transporte,
                            Calendario.desde_base(cur, mundo["id"]), ahora=AHORA)
    conn.commit()

    assert resumen["enviados"] == 2
    assert sorted(e.texto for e in transporte.enviados) == [
        "Anotado.", "Mañana vence Revisar el tablero."]
    assert {e.chat_id for e in transporte.enviados} == {marcos["telegram"]}
