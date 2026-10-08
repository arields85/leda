# 19. Palabras de todos los días, no los nombres del sistema

**Qué prueba:** Leda no nombra los conceptos del sistema: dice el hecho concreto (qué, cuándo, quién) con
las palabras de todos los días. Los nombres de los datos y de las jugadas que recibe (la previsión, la fecha
comprometida, el pedido de estado, el escalamiento, el referente, las tareas dependientes) son de la cocina y
nunca se dicen como palabras. Vale cuando cuenta lo que anotó, cuando ofrece anotar algo, en lo que manda por
su cuenta y cuando la persona pregunta qué quiere decir algo: lo explica con el hecho, no con una definición.
Decisión del usuario del 2026-10-07, de la prueba por Telegram real (Marcos preguntó "que es prevision?").

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23; `en_curso` desde el lunes 19;
    sin bloqueos ni previsiones.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 6 de
    noviembre (su aviso previo sale el martes 3, fuera de este hilo); `asignada`; depende de la del PLC con
    una dependencia bloqueante (la de la semilla).
- **Personas:** Nahuel Gimenez es integrante de OT. Ismael aprueba el trabajo de Marcos.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** a Marcos, el aviso previo de la tarea del PLC (martes 20, 10:00), que no pide respuesta.
  A Ismael, nada.

## Hilo

1. **Marcos** escribe (martes 20, 11:00): "me la podes pasar a nahuel?"
   →
   - Jugadas: la reasignación, que Leda reconoce y no hace (como en la conversación 12).
   - Efecto: ninguno sobre la tarea; ningún aviso al administrador.
   - La respuesta dice: que eso no lo puede hacer y que lo decide Ismael; ofrece anotar para qué día la
     va a terminar, con palabras de todos los días. Marcos no da un porqué: en la ronda roja, con "no llego
     con los tiempos", la IA lo llevó como motivo de la fecha del paso 2, que es lo que la conversación
     dice, y no es lo que esta conversación mide.
   - La respuesta no dice: "previsión" ni otro nombre de un dato o de una jugada; que la tarea pasó a
     Nahuel.
   - Estado después: tema abierto, lo que Leda ofreció.

2. **Marcos** escribe (martes 20, 11:05): "dale, para el martes 27, estoy tapado con la puesta en marcha"
   →
   - Jugadas: `anotar_prevision` sobre la tarea del PLC, con fecha martes 27 y su motivo, con las palabras
     de Marcos. (Trae su porqué desde el 2026-10-07: una fecha que atrasa sin él abre la pregunta de qué la
     atrasa, ADR 0018, 9n, que no es lo que mide esta conversación.)
   - Efecto: una previsión al martes 27; la fecha comprometida sigue siendo el viernes 23. Ismael se entera
     hoy, con la fecha nueva, la del vencimiento, el atraso y lo que depende de la tarea.
   - La respuesta dice: que anotó que la del PLC la termina el martes 27, con su motivo; que el
     vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba; que Ismael se va a
     enterar hoy; el próximo paso concreto: que el martes 27 le pregunta cómo viene.
   - La respuesta no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de
     un dato o de una jugada; que la fecha de la tarea cambió.
   - Estado después: sin tema abierto, nada para después.

3. **Leda**, por su cuenta, a Ismael (martes 20, a la hora que dicen los hechos): el aviso de la fecha nueva.
   A Marcos, nada.
   →
   - El mensaje dice: que Marcos la termina el martes 27; que vencía el viernes 23; el atraso, dos días
     hábiles; que la de comunicaciones depende de ella; que no hace falta que conteste.
   - El mensaje no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un
     dato o de una jugada; que Ismael tiene que hacer algo.

4. **Marcos** escribe (martes 20, 11:15): "que es prevision?"
   →
   - Jugadas: ninguna de la lista: es una pregunta sobre la conversación y se contesta desde los últimos
     turnos (ADR 0018, 9k.4).
   - Efecto: ninguno.
   - La respuesta dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para
     terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia.
   - La respuesta no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo
     guarda o lo usa Leda); otra pregunta.
   - Estado después: sin tema abierto.

5. **Leda**, por su cuenta, a Marcos (viernes 23, 10:00): la tarea del PLC vence hoy y Marcos ya dio su
   fecha.
   →
   - El mensaje dice: que la tarea del PLC vence hoy; que tiene anotado que la termina el martes 27 y que
     Ismael ya lo sabe; que el martes 27 le pregunta cómo viene; que no hace falta contestar.
   - El mensaje no dice: "previsión", "fecha comprometida", "pedido de estado", "referente", "dependiente"
     ni otro nombre de un dato o de una jugada; un reproche; una pregunta.

6. **Nadie** escribe del viernes 23 al martes 27 a las 10:00.

7. **Leda**, por su cuenta, a Marcos (martes 27, 10:00): pide el estado, el día que Marcos dio (9i).
   →
   - El mensaje dice: que hoy es el día que Marcos dio para terminar la tarea del PLC; pregunta cómo viene.
   - El mensaje no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento",
     "referente", "dependiente" ni otro nombre de un dato o de una jugada; un reproche.
   - Estado después: tema abierto, la pregunta del estado de la tarea del PLC; la espera, abierta.

## Qué mide

- **La regla (usuario, 2026-10-07):** Leda dice el hecho concreto con las palabras de todos los días y nunca
  nombra un concepto del sistema. Es una falla que una respuesta o un aviso use como palabra el nombre de un
  dato o de una jugada ("previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente",
  "dependiente" como sustantivo), y que ante "qué es" conteste con una definición en lugar del hecho.
- **Garantías (5b):** no inventa (lo que todavía no pasó va en futuro); no deja sin salida (cada mensaje
  termina con su próximo paso); no confunde la tarea.
- **Falla de comprensión:** que la IA no tome "me la podes pasar a nahuel?" como una reasignación, "dale, para
  el martes 27" como una fecha nueva para terminar, o "que es prevision?" como una pregunta sobre la
  conversación.
