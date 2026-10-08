# 28. Las entregas para revisar, en una lista

**Qué prueba:** a Ismael le llegan juntas tres entregas para revisar y Leda las manda en un solo
mensaje, una lista con un botón por tarea; al tocar una, aparece esa entrega con sus fotos, el
enlace a la página de la tarea y los botones Aprobar y Pedir cambios. Escribir "mostrame la del
plc" vale igual que el botón. Después de decidir una, Leda muestra lo que queda por revisar, sin
insistir ese día, y lo que queda entra en los recordatorios del día hábil siguiente, también en una
lista con un botón por tarea. Y lo que admite dos lecturas lleva una sola pregunta: si la respuesta
no elige, Leda no decide ni la repite; la entrega sigue esperando su decisión, con los dos botones.
Decisiones 12, 17 y 18 del usuario (2026-10-08; `odd/tasks/fase-c.md`, C-3d, D4); mecánica §10
(el tope diario cuenta mensajes, no lo que trae cada uno); ADR 0018, decisión 2 (los botones son
atajos).

## Estado inicial

- **Día:** D = viernes 23, dentro del horario.
- **Personas:** Ismael aprueba el trabajo de Marcos, Mariano y Ariel (`aprobado_por: ismael`).
- **Tareas**, todas `en_curso` desde el lunes 19, sin bloqueos ni dependencias:
  - "Programar PLC de la comprimidora" (Marcos, OT), vence el viernes 30.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Cablear tablero de la máquina 3" (Mariano, electricidad), vence el viernes 30.
    Criterio de aceptación: "El tablero de la máquina 3 queda cableado según su diagrama y pasa la
    prueba de continuidad y de aislación".
  - "Dashboard de lotes en CoreLabs" (Ariel, CoreLabs), vence el viernes 6.
    Criterio de aceptación: "El dashboard muestra los lotes del día con su cantidad y su estado, y
    coinciden con el registro de producción".
- **Ya pasó** (el viernes 23, entre las 15:00 y las 15:06): Marcos entregó la del PLC con una foto,
  Mariano la del tablero con dos y Ariel la del dashboard sin fotos; cada uno describió su criterio
  y confirmó. Los tres avisos a Ismael esperan el margen para corregir (diez minutos).
- **Estado de la conversación de Ismael:** sin tema abierto.

## Hilo

1. **Leda**, por su cuenta, a Ismael (viernes 23, 15:20): los tres avisos, que salen juntos.
   →
   - El mensaje dice: que le entregaron 3 tareas para revisar; cada una en su renglón con 📋, con
     quién la entregó y cuántas fotos trae (el dashboard, ninguna); el cierre, aparte: que toque una
     para verla. Nunca "para aprobar" (decisión 18).
   - El mensaje no dice: lo entregado pieza por pieza (eso se ve al tocar); que ya las aprobó.
   - Botones: uno por tarea, en el orden de la lista ([Ver PLC] [Ver tablero] [Ver dashboard]). Sin
     fotos adjuntas, sin enlace y sin Aprobar ni Pedir cambios: son de cada entrega.
   - Es un solo mensaje: el tope diario cuenta mensajes, no lo que trae cada uno, y los avisos de
     coordinación nunca cuentan (mecánica §10).

2. **Ismael** toca (15:25) "Ver tablero".
   →
   - Jugadas: `ver_entrega`, la tarea del tablero. El botón es un atajo de lo escrito.
   - Efecto: ninguno.
   - La respuesta dice: la tarea del tablero en su renglón con 📋; que la entregó Mariano; lo que
     describió; que van dos fotos adjuntas; el cierre: que puede aprobarla o pedir cambios.
   - Sale además: las dos fotos, en un álbum después del texto, y al final del texto el enlace a la
     página de la tarea, que agrega el código.
   - Botones: Aprobar y Pedir cambios.

3. **Ismael** escribe (15:30): "esta bien pero que mariano revise el rotulo de los cables"
   →
   - Jugadas: `aprobar` y `pedir_cambios`, la tarea del tablero: admite dos lecturas (ADR 0018,
     decisión 2), así que no se hace ninguna. Si la IA elige sólo `aprobar` con el comentario (la
     ronda D7, 1 de 5), pasa lo mismo: una aprobación con un comentario para el responsable nunca
     cierra directo (decisión 22 del usuario, 2026-10-08; lo decide el código). El corredor espera
     las dos jugadas: no admite dos lecturas válidas para un paso.
   - Efecto: ninguno; la tarea sigue `en_revision`.
   - La respuesta dice: una sola pregunta, cuál de las dos: aprobarla y pasarle el comentario a
     Mariano, o pedirle el cambio primero.
   - Botones: Aprobar y Pedir cambios.
   - Estado después: tema abierto, la decisión sobre la tarea del tablero.

4. **Ismael** escribe (15:31): "y bueno fijate vos"
   →
   - Jugadas: ninguna de la lista: no elige. La IA real la deja fuera de la lista como respuesta a
     la pregunta abierta (`contesta_la_pregunta`, 4 de 5 en la ronda D7), y eso espera el YAML; sin
     jugada es lo mismo.
   - Efecto: ninguno; la tarea sigue `en_revision`. La pregunta se cierra sin elegir: se hace una
     sola vez (decisión 12). Es la respuesta a la pregunta abierta, no un pedido nuevo: nunca le
     llega un aviso a la administración, aunque la IA la deje fuera de la lista (C-3d, D7: con la IA
     real, 5 de 5; la maneja la pregunta abierta, como un mensaje sin jugada).
   - La respuesta dice: que Leda no decide por él; que la entrega del tablero sigue esperando su
     decisión, con los botones para cuando quiera, o escribiéndolo.
   - La respuesta no dice: la misma pregunta otra vez; que la aprobó; que le pidió el cambio.
   - Botones: Aprobar y Pedir cambios.
   - Estado después: sin tema abierto.

5. **Ismael** toca (15:40) "Aprobar", el botón de la respuesta anterior.
   →
   - Jugadas: `aprobar`, la tarea del tablero, con el comentario que había dicho ("que mariano revise
     el rotulo de los cables"): la decisión, lo demás va como comentario, no como un pedido de
     cambios.
   - Efecto: la aprobación con el comentario; el código comprueba el cierre y la tarea pasa a
     `terminada`. El aviso a Mariano sale enseguida.
   - La respuesta dice: que la del tablero quedó terminada y que Mariano se entera ahora, con el
     comentario; que le quedan por revisar la del PLC (Marcos) y la del dashboard (Ariel).
   - Botones: uno por cada una que queda ([Ver PLC] [Ver dashboard]).
   - Leda no insiste ese día: lo que queda entra en los recordatorios del día hábil siguiente.

6. **Leda**, por su cuenta, a Mariano (15:41): el aviso de la aprobación, con el comentario de los
   rótulos como algo para mirar, no como un cambio pendiente; que no hace falta que responda. Al
   final, el enlace a la página de la tarea.

7. **Ismael** escribe (15:45): "mostrame la del plc"
   →
   - Jugadas: `ver_entrega`, la tarea del PLC: escribir vale igual que el botón.
   - Efecto: ninguno.
   - La respuesta dice: la del PLC, que la entregó Marcos, lo que describió y que va una foto
     adjunta; que puede aprobarla o pedir cambios.
   - Sale además: la foto, en el álbum que sigue al texto, y el enlace a la página de la tarea.
   - Botones: Aprobar y Pedir cambios.

8. **Leda**, por su cuenta, a Ismael (lunes 26, 10:00): el primer recordatorio de las dos que
   siguen esperando, en un solo mensaje.
   →
   - El mensaje dice: que esperan su revisión desde el vie 23/10; cada una en su renglón con 📋,
     con quién la entregó; el cierre: que puede tocar una para verla, o contestar.
   - Botones: uno por tarea ([Ver dashboard] [Ver PLC]), en el orden de la lista.

9. **Ismael** toca (10:05) "Ver dashboard", el botón del recordatorio.
   →
   - Jugadas: `ver_entrega`, la tarea del dashboard.
   - La respuesta dice: la del dashboard, que la entregó Ariel, lo que describió, sin fotos; que
     puede aprobarla o pedir cambios.
   - Sale además: el enlace a la página de la tarea; ninguna foto.
   - Botones: Aprobar y Pedir cambios.

## Qué mide

- **Garantías:** nada se aprueba ni se devuelve sin la decisión de quien aprueba; con dos lecturas,
  no se hace ninguna y la pregunta es una sola (pasos 3 y 4); el botón de la respuesta decide sobre
  lo que mostró (ADR 0018, decisión 2); el comentario de una aprobación no es un pedido de cambios
  (paso 5); un aviso de coordinación agrupado sigue fuera del tope diario.
- **Las listas:** un mensaje por envío, con un botón por tarea (pasos 1 y 8); el botón y lo escrito
  muestran lo mismo (pasos 2 y 7); después de decidir, lo que queda (paso 5).
- **Las palabras:** "revisar" para lo que espera; Leda no nombra por su cuenta a quien aprueba el
  trabajo de nadie (los mensajes son para Ismael, que es quien aprueba).
- **El formato:** el de la conversación 20 en cada mensaje.
- **Falla de comprensión:** que la IA tome "y bueno fijate vos" como una de las dos decisiones, o
  "mostrame la del plc" como otra cosa que ver la entrega.
