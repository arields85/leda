"""Un avance sin un hecho cierto: la jugada `informar_avance` (decisión del usuario, 2026-10-05).

`tests/conversaciones/15-avance-vago.md`; ADR 0018, decisión 9b. "Voy bien, la tengo casi lista"
ante un pedido de estado: Leda anota el avance con las palabras de la persona (atribuido y
auditado, sin cambiar estado ni fecha), la espera sigue abierta y al día hábil siguiente vuelve
a pedir el estado. Esa respuesta no es silencio: la escalera cuenta sólo los pedidos sin
respuesta, así que el escalamiento o su aviso no salen por ella. A la segunda respuesta sin nada
cierto, Leda pregunta para cuándo; con una fecha, es una nueva previsión.

El reloj se mueve por días como en `test_escalera.py`: la tarea "Revisar el tablero" de Marcos
vence el viernes 9 de octubre de 2026 y el lunes 12 es feriado. La IA es guionada.

Portada de `prueba_chica/test_avance.py` la que no necesita la escalera; las demás (capa 3) se
portan con ella.
"""

from __future__ import annotations

from datetime import datetime

from leda.db import admin
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_turno

from tests.motor.ayudantes import avisos_guardados, cambiar_el_vencimiento, cuantas, octubre

VAGO = "voy bien, la tengo casi lista"
def _escribe(conn, escribe, texto: str, *jugadas: Jugada, at: datetime):
    quien, entrante = escribe("Marcos", texto, at=at)
    resultado = procesar_turno(conn, quien, entrante,
                               IAGuionada(jugadas=[list(jugadas)], redacciones=["Listo."]),
                               RelojFijo(at))
    conn.commit()
    assert resultado.error is None
    return resultado


def _avance(texto: str) -> Jugada:
    return Jugada("informar_avance", {"tarea": "T1", "palabras": texto})


def _repreguntas(conn) -> list[dict]:
    return avisos_guardados(conn, "repregunta_de_estado")


# --- Cuando no hay un pedido siguiente: lo dicen los hechos (revisión de `informar_avance`) ------

def test_sin_fecha_comprometida_el_avance_se_anota_y_dice_que_no_vuelve_a_pedir(conn, mundo,
                                                                                escribe):
    """Una tarea sin vencimiento no tiene escalera: el avance se anota igual, y los hechos dicen
    que no hay un pedido siguiente, nunca en silencio."""
    cambiar_el_vencimiento(conn, mundo, None)
    with admin(conn) as cur:
        cur.execute("""insert into pending_reply (workspace_id, membership_id, task_id, tipo,
                                                  preguntado_en, vence_en)
                       values (%s, %s, %s, 'estado_de_la_tarea', %s, %s)""",
                    (mundo["id"], mundo["personas"]["Marcos"]["membership_id"], mundo["tarea"],
                     octubre(9, 10), octubre(13, 10)))
    conn.commit()

    resultado = _escribe(conn, escribe, VAGO, _avance(VAGO), at=octubre(9, 11))

    [hecho] = resultado.hechos
    assert hecho["resultado"] == "anotado" and hecho["avance"] == {"dijo": VAGO}
    assert hecho["no_vuelve_a_pedir_el_estado"] == {"motivo": "sin_fecha_comprometida"}
    assert "vuelve_a_pedir_el_estado" not in hecho
    assert _repreguntas(conn) == []
    assert cuantas(conn, "audit_log", "accion = 'informar_avance'") == 1


