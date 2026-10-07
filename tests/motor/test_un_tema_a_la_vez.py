"""Un tema a la vez, también cuando las reglas comunes de las fichas se juntan (revisión de la
corrida en seco con las 16 conversaciones, 2026-10-05).

ADR 0018, decisiones 4, 9d y 9j; `fichas.correr` y `preguntas.abrir`. Tres reglas generales,
para toda ficha y toda pregunta:

- **Nunca dos preguntas juntas:** si una jugada sobre una tarea vencida lleva la pregunta de
  para cuándo (9j) y además propone algo (`Ficha.propone`), se pregunta la fecha y lo propuesto
  queda para después, sin perder ninguno de los dos en los hechos.
- **Una opción elegida pasa por las mismas comprobaciones de su ficha** que la jugada escrita,
  escrita o tocada: con la tarea vencida, lleva la misma pregunta de para cuándo.
- **Una pregunta que queda para después no cuenta silencio:** su espera (y la escalera que la
  repite) empieza recién cuando Leda la hace, no cuando quedó guardada sin preguntarse.

El reloj es el de `test_escalera.py`: "Revisar el tablero" (T1) de Marcos vence el viernes 9 de
octubre de 2026; el lunes 12 es feriado.

Portada de `prueba_chica/test_un_tema_a_la_vez.py` la que no necesita la escalera; las demás
(capa 3) se portan con ella.
"""

from __future__ import annotations

from leda.motor import fichas

FECHA = "fecha_de_la_tarea"
PROPUESTA = "propuesta"


# --- Una pregunta para después no cuenta silencio ------------------------------------------

def test_cada_clave_de_pregunta_de_los_hechos_tiene_siempre_la_misma_forma():
    hecho: dict = {}
    fichas._nombrar_pregunta(hecho, "pregunta_para_despues", PROPUESTA)
    fichas._nombrar_pregunta(hecho, "pregunta_para_despues", FECHA)
    fichas._nombrar_pregunta(hecho, "pregunta_para_despues", FECHA)

    assert hecho == {"pregunta_para_despues": PROPUESTA,
                     "otras_preguntas_para_despues": [FECHA]}
