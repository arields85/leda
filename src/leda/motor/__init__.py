"""El motor de conversación de Leda (ADR 0018; `odd/tasks/motor-definitivo.md`, E3-5).

La IA elige jugadas de una lista cerrada y redacta desde los hechos; el código decide si
valen, las maneja y ejecuta por la cocina (`herramientas.ejecutar`, con su confirmación y su
auditoría). Es el diseño que pasó la prueba real de la Etapa 2, portado por capas desde
`prueba_chica/`, que queda intacta hasta la E3-8:

1. contratos y partes puras: `tiempo`, `ia`, `ancla`, `cambios_de_estado`, `preguntas`,
   `instrucciones` y `registro` (el registro de turnos);
2. turnos: fichas, situaciones, hechos, avisos, efectos y el turno;
3. tiempo y afuera: escalera, botones, ciclo, reloj e IA real;
4. la entrada (E3-7): lo que se hace con cada update (`recibir`), igual por el escuchador
   (`escucha`) y por el webhook de `leda.entrada`.

Qué puede alcanzar de `leda` y qué tablas toca lo fija `tests/motor/test_frontera.py`.
"""
