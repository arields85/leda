"""Los hechos de un efecto que pasa después dicen cómo quedó al terminar el turno (ADR 0018, 9k).

Un mensaje puede traer varias jugadas: la segunda puede retirar lo que la primera dejó guardado
(un avance o un destrabe guardan el pedido del estado del día hábil siguiente; una fecha en el
mismo mensaje contesta la espera y ese pedido ya no sale). Si el hecho de la primera siguiera
diciendo que el pedido sale, la redacción contaría algo falso. Por eso, después de todas las
jugadas, el turno vuelve a leer de la base cada aviso y cada espera que un hecho nombra y pone su
estado final: un solo paso para todas las jugadas, sin ramas por jugada.

También: destrabarse antes del vencimiento deja que la escalera siga sola (revisión de
`review-e8b69f0cca8677ef`): ningún paso queda detenido por lo que el bloqueo omitió.

El reloj y la tarea son los de `test_escalera.py`: "Revisar el tablero" de Marcos vence el
viernes 9 de octubre de 2026, el aviso previo es a 3 días hábiles y el lunes 12 es feriado.

Portada de `prueba_chica/test_hechos_al_final_del_turno.py` la que no necesita la escalera; las
demás (capa 3) se portan con ella.
"""

from __future__ import annotations

from leda.motor.fichas import GUARDADO_SIN_ENVIAR
from leda.motor.hechos import sin_significado
from leda.motor.ia import Jugada

from tests.motor.ayudantes import dice, octubre

RETIRADO = "retirado_sin_enviar"
def _fecha(dia: str) -> Jugada:
    return Jugada("anotar_prevision", {"tarea": "T1", "fecha": dia, "motivo": "falta un repuesto"})


# --- Dos jugadas en un mensaje: la segunda retira lo que guardó la primera --------------------

def test_dos_fechas_en_un_mensaje_retiran_el_aviso_de_la_primera(conn, mundo, escribe):
    """El mismo paso vale para cualquier aviso que un hecho nombra: el de la primera previsión
    queda atrás por la segunda, y su hecho lo dice."""
    resultado = dice(conn, escribe, _fecha("2026-10-14"), _fecha("2026-10-16"),
                     at=octubre(6, 10))

    primera, segunda = resultado.hechos
    assert primera["aviso_al_referente"]["estado"] == RETIRADO
    assert primera["aviso_al_referente"]["motivo"] == "hay_una_prevision_mas_nueva"
    assert "sale" not in primera["aviso_al_referente"]
    assert segunda["aviso_al_referente"]["estado"] == GUARDADO_SIN_ENVIAR
    assert sin_significado(resultado.hechos) == set()


