# 40. La semana de las listas

**Qué prueba:** con los tres pedidos de estado de la semana (lunes, miércoles y viernes), la lista del
lunes trae todas las tareas abiertas de la persona, cada una con su situación, también la trabada y la
entregada; lo que la persona contestó en la lista no se le vuelve a preguntar mientras no cambie nada;
"viene bien" de una tarea que vence en la semana deja como próximo contacto el aviso previo de siempre;
y las listas del miércoles y del viernes traen sólo lo que cambió o no se contestó. Decisiones 31, 32,
44 y 46 del usuario (`odd/tasks/fase-c.md`, 2026-10-09, todas opción A), sobre la C-6 (decisión 8;
conversación 37).

**Corre desde la C-6** (`odd/tasks/fase-c.md`), entera, con su YAML.

## La regla (decidida por el usuario, 2026-10-09)

1. **La lista de los lunes trae todas las tareas abiertas, cada una con su situación** (decisión 32):
   también las trabadas (sigue trabada, con lo que la traba) y las entregadas (esperando revisión),
   para que la persona vea todo junto y avise si algo cambió. Leda pregunta cómo vienen sólo por las
   que se pueden mover (asignadas o en curso, sin un bloqueo).
2. **Lo contestado en la lista no se vuelve a preguntar** (decisión 31): si Marcos contó en la lista
   del lunes cómo viene una tarea que vence el martes, el martes no le llega aparte "hoy vence". La
   tarea vuelve sólo si no contestó o si cambió algo.
3. **"Viene bien" en la lista: la próxima vez es el aviso previo de siempre** (decisión 44): tres días
   hábiles antes del vencimiento en CoreWork, nunca recién en una lista en la que ya habría vencido.
4. **La primera lista de la semana es completa; las otras, sólo lo que falta** (decisión 46): el
   miércoles y el viernes van sólo las tareas que cambiaron o que no se contestaron ("del motor no me
   contaste el lunes"); si no hay nada, no sale nada.
5. La hora de salida es una sola (decisión 45, ya construida): la cadencia antes de las 10:00 sale a
   las 10:00; la del miércoles a las 11:30 y la del viernes a las 11:00 salen a su hora, y lo que la
   escalera tenía para ese día sobre esas tareas espera y va en la lista.

Cómo se leyó lo que la regla no dice (decidido por el coordinador a partir de las decisiones 31, 44 y
46; `odd/tasks/fase-c.md`, C-6):

- **"Cambió algo"** es un cambio en la situación de la tarea: su estado (también que se trabó, se
  destrabó o se entregó), el bloqueo que la traba, el día que la persona dio para terminarla, o que
  pasó el día del seguimiento sin entregarse (quedó atrasada). Que llegue el día en que vence no es un
  cambio: es lo que la persona ya sabía al contestar.
- **Lo contestado cubre hasta la lista siguiente.** El pedido de estado del día del vencimiento no
  sale si la persona contó cómo viene esa tarea después de la última lista y no cambió nada; si entre
  la respuesta y el vencimiento hay otra lista (o la hay ese mismo día), el pedido sale, dentro de esa
  lista. Una respuesta vaga ("ya casi") también es contar cómo viene.
- **Una sola regla, en la lista o fuera de ella** (corrección de la C-6, del coordinador): lo que la
  persona cuenta de una tarea por su cuenta tiene el mismo efecto que contestarlo en la lista; no se
  le vuelve a preguntar en la lista siguiente ni el día del vencimiento.
- **La escalera sigue anclada al vencimiento** (mecánica §9): el pedido del día del vencimiento que no
  sale queda dado por contestado, con su motivo, como el primer paso. Si la tarea sigue sin entregar,
  el día hábil siguiente sale el segundo pedido y el escalamiento llega el mismo día que sin la lista
  (al tercer día hábil del vencimiento), nunca uno después.
- **Un día dado en la lista es una previsión como cualquier otra** ("lo termino el miércoles"): la
  misma jugada que fuera de la lista y el mismo seguimiento; ese día Leda pregunta.

## Estado inicial

- **Día:** D = lunes 2 de noviembre, 09:00, dentro del horario.
- **Cadencias del espacio:** las tres a cada integrante en privado del pack: lunes 09:15
  (`objetivos_semanales`), miércoles 11:30 (`estado_medio_semana`) y viernes 11:00 (`cierre_semanal`).
  Las del grupo se suponen apagadas.
- **Tareas de Marcos** (OT; aprueba su trabajo Ismael):
  - "Programar PLC de la comprimidora": vence el martes 3; `en_curso` desde el lunes 26. Su aviso
    previo (tres días hábiles antes, el miércoles 28) no salió: la escalera lo da enseguida.
  - "Instalar el panel HMI de la comprimidora": vence el viernes 6; `en_revision` (entregada) desde el
    viernes 30.
  - "Revisar comunicaciones industriales de la comprimidora": vence el viernes 6; `asignada`. Su aviso
    previo toca el martes 3.
  - "Cablear el tablero de la línea 2": vence el viernes 13; `bloqueada` desde el lunes 2, esperando el
    repuesto.
  - "Cambiar el motor de la cinta 4": vence el viernes 13; `asignada`.
- **Estado de la conversación** de Marcos: sin tema abierto, nada para después.
- **Ya enviado:** nada.

## Hilo

1. **Leda**, por su cuenta (lunes 2, 10:00): la lista del lunes, a Marcos.
   →
   - Efecto: un mensaje privado con las cinco tareas, cada una con su situación: el PLC vence mañana
     (con su aviso previo adentro), el panel HMI entregado y esperando revisión, las comunicaciones
     vencen el viernes, el tablero sigue trabado esperando el repuesto, el motor vence el viernes 13.
   - El mensaje dice: cada tarea con su situación; una sola pregunta, al final, por cómo vienen el PLC,
     las comunicaciones y el motor.
   - El mensaje no dice: una pregunta por el tablero o por el panel HMI; un reproche.
   - Estado después: Marcos tiene abierta la pregunta de cómo vienen sus tareas.

2. **Marcos** escribe (lunes 2, 10:30): "el plc viene bien y las comunicaciones tambien"
   →
   - Jugadas: `informar_avance` sobre el PLC y `informar_avance` sobre las comunicaciones, cada una con
     sus palabras.
   - Efecto: los dos avances anotados. Ninguna espera abierta.
   - La respuesta dice: lo anotado de las dos; del PLC, que si para el miércoles no lo entregó le
     pregunta en la lista del miércoles; de las comunicaciones, que el martes le recuerda que vencen el
     viernes y que le pregunta el viernes; y una sola pregunta, al final, por el motor de la cinta 4.
   - La respuesta no dice: que mañana le recuerda que vence el PLC; una pregunta por el tablero o por el
     panel HMI.
   - Estado después: la pregunta de cómo vienen sus tareas sigue abierta, con el motor.

3. **Leda**, por su cuenta (martes 3, 10:00): el aviso previo de las comunicaciones (vencen el
   viernes), que no pide respuesta. Del PLC, que vence hoy, nada: Marcos ya contó cómo viene. El
   pedido de ese día queda dado por contestado, con su motivo: el primer paso de su escalera.

4. **Leda**, por su cuenta (miércoles 4, 10:00 y 11:30): a las 10:00, nada (el pedido de estado del
   PLC, que venció ayer, espera la lista); a las 11:30, la lista del miércoles, sólo con lo que falta.
   →
   - Efecto: un mensaje privado con dos tareas: el PLC, que venció ayer sin entregarse (cambió), con el
     pedido de estado de su escalera adentro (el segundo: la escalera sigue anclada al vencimiento);
     y el motor, del que no contestó el lunes. Ni las comunicaciones (contestadas, sin cambios), ni
     el tablero ni el panel HMI (sin cambios).
   - Estado después: la pregunta de cómo vienen sus tareas, abierta; la espera del estado del PLC,
     abierta.

5. **Marcos** escribe (miércoles 4, 12:00): "el motor ya lo arranque"
   →
   - Jugadas: `anotar_inicio` sobre el motor de la cinta 4.
   - Efecto: el motor, en curso.
   - La respuesta dice: que quedó anotado que arrancó el motor; y una sola pregunta, al final, por el
     PLC.
   - Estado después: la pregunta de cómo vienen sus tareas sigue abierta, con el PLC.

6. **Leda**, por su cuenta (jueves 5, 10:00): el tercer pedido de estado del PLC, aparte (no hay lista
   los jueves), que avisa que si sigue igual va a quedar asentado que está atrasada.

7. **Leda**, por su cuenta (viernes 6, 10:00 y 11:00): a las 10:00, al tercer día hábil del
   vencimiento del PLC, el escalamiento a Ismael, como si no hubiera habido lista; a las 11:00, la
   lista del viernes, sólo con lo que falta.
   →
   - Efecto: a Ismael, que el PLC sigue sin novedades. A Marcos, un mensaje privado con dos tareas: el
     PLC, del que no contestó desde el miércoles; y las comunicaciones, que vencen hoy, con su
     pedido de estado adentro (la respuesta del lunes cubría hasta la lista del miércoles). Ni el motor
     (contestado el miércoles, sin cambios), ni el tablero ni el panel HMI.
   - Estado después: la espera del estado del PLC y la de las comunicaciones, abiertas.

## Qué mide

- **Garantías (5b):** la lista del lunes con todas las tareas abiertas, cada una con su situación;
  una sola pregunta por lista y sólo por las que se pueden mover; nada aparte por lo que ya contestó;
  las listas siguientes sólo con lo que cambió o no se contestó; el aviso previo de siempre; la
  escalera anclada al vencimiento (el escalamiento no se corre); ninguna fecha que nadie dio.
- **Falla de comprensión:** que la IA reparta mal lo que Marcos dijo entre las tareas, o que tome
  "viene bien" como que la tarea está terminada.
