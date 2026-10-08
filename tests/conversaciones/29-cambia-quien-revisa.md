# 29. Cambia quién revisa

**Qué prueba:** mientras dos entregas de Mariano esperan, la plataforma cambia quién aprueba su
trabajo (de Ismael a Marcos). El aviso de una entrega va a quien aprueba en el momento de salir (se
relee): el que todavía no había salido le llega a Marcos. El que ya le había llegado a Ismael no se
pierde: a Marcos le llega el aviso de lo que espera su decisión, y si Ismael toca un botón del
aviso viejo, Leda le dice que esa tarea ya no la revisa él, sin cambiar nada. Decisión 16 del
usuario (2026-10-08; `odd/tasks/fase-c.md`, C-3d, D4); mecánica §7 (la aprobación es de quien la
política designa); constitución §4 (Leda nunca da por hecha una aprobación).

## Estado inicial

- **Día:** D = viernes 23, dentro del horario.
- **Personas:** Ismael aprueba el trabajo de Mariano (`aprobado_por: ismael`) y el de Marcos.
- **Tareas de Mariano**, `en_curso` desde el lunes 19, sin bloqueos ni dependencias:
  - "Cablear tablero de la máquina 3", vence el viernes 30.
    Criterio de aceptación: "El tablero de la máquina 3 queda cableado según su diagrama y pasa la
    prueba de continuidad y de aislación".
  - "Revisar el motor de la cinta 2", vence el viernes 30.
    Criterio de aceptación: "El motor de la cinta 2 gira sin ruidos y su consumo queda dentro de lo
    que dice su placa".
- **Ya pasó** (viernes 23): a las 15:00 Mariano entregó la del tablero y a las 15:20 el aviso le
  llegó a Ismael, con Aprobar y Pedir cambios; a las 15:30 entregó la del motor, y su aviso espera el
  margen para corregir (sale a las 15:41).
- **Estado de la conversación de Ismael y de Marcos:** sin tema abierto.

## Hilo

1. **La plataforma** (15:35): desde ahora, el trabajo de Mariano lo aprueba Marcos.
   →
   - Efecto: ninguno en las tareas; las dos siguen `en_revision`.

2. **Leda**, por su cuenta, a Marcos (15:36): el aviso de la entrega del tablero, que ya le había
   llegado a Ismael.
   →
   - El mensaje dice: la tarea del tablero en su renglón con 📋; que la entregó Mariano y lo que
     describió; que la entrega ya esperaba y ahora la revisa él; el cierre: que puede aprobarla o
     pedir cambios.
   - Botones: Aprobar y Pedir cambios. Al final, el enlace a la página de la tarea.
   - A Ismael no le llega nada.

3. **Leda**, por su cuenta (15:42): el aviso de la entrega del motor, que todavía no había salido,
   le llega a Marcos, que es quien aprueba al salir; a Ismael, nada.

4. **Ismael** toca (15:50) "Aprobar" en el aviso viejo de la entrega del tablero.
   →
   - Jugadas: `aprobar`, la tarea del tablero, por el botón.
   - Efecto: ninguno; la tarea sigue `en_revision`, sin la aprobación de Ismael.
   - La respuesta dice: que esa tarea ya no la revisa él; que no cambió nada.
   - La respuesta no dice: que la aprobó; quién la revisa ahora (no lo preguntó).

5. **Marcos** escribe (16:00): "lo del tablero de mariano aprobado"
   →
   - Jugadas: `aprobar`, la tarea del tablero.
   - Efecto: la aprobación de Marcos; la tarea pasa a `terminada`. El aviso a Mariano sale
     enseguida.
   - La respuesta dice: que la del tablero quedó terminada y que Mariano se entera ahora; que le
     queda por revisar la del motor.
   - Botones: uno, para ver la que queda.

## Qué mide

- **Garantías:** la aprobación es de quien aprueba hoy (paso 4: el botón viejo no aprueba nada); el
  aviso va a quien aprueba al salir (pasos 2 y 3); nadie se queda sin enterarse de lo que espera su
  decisión.
- **Las palabras:** a Ismael no se le nombra quién la revisa ahora si no lo pregunta; "revisar" para
  lo que espera.
- **El formato:** el de la conversación 20 en cada mensaje.
