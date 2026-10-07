"""Lo que la cocina le pasa a la IA: la hora de lo que Leda manda y lo que sabe de la tarea.

Cuarta vuelta de ajuste (2026-10-06), después de la ronda 3: la regla del mozo (`AGENTS.md`,
"Cómo pensamos juntos", punto 11): si dice algo mal, primero se mira si la cocina le pasó el
hecho correcto. Mecanismos generales, sin frases ni ramas por conversación:

1. **Una sola hora** para lo que Leda manda por su cuenta (`tiempo.HORA_DE_SALIDA`): la usan la
   escalera, los avisos guardados, el reloj adelantado y los hechos que dicen cuándo sale algo.
   Antes, el pedido que sigue a un avance decía "mañana a las 9" y el reloj adelantado (y las
   conversaciones) llegaban a las 10.
2. **Desde cuándo la tarea está en su estado**, cuando el código lo sabe por lo que anotó el
   motor (`cambios_de_estado.py`), o `desconocido` (conversaciones 01, paso 4, y 12, paso 3).
3. **El vencimiento** también en la escalera de una pregunta (la repregunta y su escalamiento).
4. **El estado real** en un pedido de estado: lo que se espera saber depende del estado
   (`espera_algo_cierto`), y una tarea que espera a otra lo dice (`espera_a`).
5. **Una entrega que no se recibe por chat** dice si hay otra forma definida de hacerla.

El reloj es el de `test_escalera.py`: "Revisar el tablero" (T1) de Marcos vence el viernes 9 de
octubre de 2026; el lunes 12 es feriado.

Portadas de `prueba_chica/test_lo_que_sabe_la_cocina.py`. Las que necesitan la escalera (capa 3)
se portan con ella.
"""

from __future__ import annotations

from datetime import datetime

from leda.motor.ia import Jugada

from tests.motor.ayudantes import T1, dice, octubre


# --- 1. Una sola hora ---------------------------------------------------------------------------

def test_el_aviso_al_referente_fuera_de_horario_sale_a_la_hora_de_salida(conn, mundo, escribe):
    r = dice(conn, escribe, Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-14"}),
             at=octubre(5, 17, 20))

    sale = r.hechos[0]["aviso_al_referente"]["sale"]
    assert datetime.fromisoformat(sale) == octubre(6, 10)


# --- 2. Desde cuándo está en su estado ---------------------------------------------------------

def test_un_inicio_que_no_se_puede_anotar_dice_desde_cuando_esta_en_curso(conn, mundo, escribe):
    """Conversación 12, paso 3: "ya la arranqué" de una tarea en curso."""
    dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(6, 11))

    r = dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(7, 11))

    assert r.hechos == [{"jugada": "anotar_inicio", "resultado": "no_se_puede",
                         "motivo": "estado", "tarea": T1, "estado": "en_curso",
                         "estado_desde": "2026-10-06"}]


# --- 5. Una entrega que no se recibe por chat -------------------------------------------------

def test_una_entrega_que_no_se_recibe_dice_que_no_hay_otra_forma_definida(conn, mundo, escribe):
    """Conversación 12, paso 6: la IA dijo "presentala por fuera de este chat", un canal que
    nadie definió. El hecho lo dice: no hay otra forma definida (ADR 0018, 9g)."""
    dice(conn, escribe, Jugada("anotar_inicio", {"tarea": "T1"}), at=octubre(6, 11))

    r = dice(conn, escribe, Jugada("entregar", {"tarea": "T1"}), at=octubre(6, 16))

    assert r.hechos == [{"jugada": "entregar", "resultado": "no_por_chat",
                         "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": T1,
                         "otra_forma_de_hacerlo": "ninguna_definida"}]
