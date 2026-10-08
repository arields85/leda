# 15. "Voy bien, la tengo casi lista"

**Qué prueba:** el día del vencimiento, cuando la tarea todavía no venció, Marcos contesta el pedido de
estado con un avance sin un hecho cierto: no dice que la terminó, ni para cuándo, ni que está trabada. Leda
anota lo que contó, con sus palabras, y no lo da por respondido: la espera sigue abierta y al día hábil
siguiente vuelve a preguntar, esperando algo cierto. Esa respuesta no es silencio: la escalera no avisa que
va a escalar, porque escala sólo a quien no contesta. Al día siguiente la tarea ya venció y Marcos vuelve a
contestar sin nada cierto: Leda lo anota y, en esa misma respuesta, le pregunta para qué día la va a tener
(con la tarea vencida, la decisión 9j, que acá coincide con "a la segunda, para cuándo" de la 9h). Con una
fecha, es una nueva previsión y el seguimiento se mueve a ella (9i). ADR 0018, decisiones 9b y 9h, con la
jugada `informar_avance` (decisión del usuario, 2026-10-05: "casi lista no es lo mismo que terminé... es una
respuesta ambigua, no puede quedar así"), y 9j.

## Estado inicial

- **Día:** D = martes 27, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence hoy, martes 27; `en_curso` desde el
    martes 20; sin bloqueos ni previsiones.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 6 de
    noviembre (su aviso previo sale el martes 3); `asignada`; depende de la del PLC con una dependencia
    bloqueante (la de la semilla).
- **Estado de la conversación de Marcos:** sin tema abierto; nada para después; nada mostrado para
  confirmar.
- **Ya enviado:** a Marcos, el aviso previo de la tarea del PLC (jueves 22), que no pide respuesta. Ninguna
  espera abierta. A Ismael, nada.

## Hilo

1. **Leda**, por su cuenta, a Marcos (martes 27, 10:00): el primer pedido de estado, el día del
   vencimiento (mecánica §9).
   →
   - Efecto: abre la espera de la respuesta de Marcos sobre la tarea del PLC (`pending_reply`, ADR 0017,
     decisión 6).
   - El mensaje dice: que la tarea del PLC vence hoy; pide el estado.
   - El mensaje no dice: que va a avisar a Ismael; un reproche (constitución §8).
   - Botones: ninguno (decisión 9b).
   - Estado después: tema abierto, la pregunta del estado de la tarea del PLC; la espera, abierta.

2. **Marcos** escribe (martes 27, 10:30): "voy bien, la tengo casi lista"
   →
   - Jugadas: `informar_avance` sobre la tarea del PLC, con las palabras de Marcos.
   - Efecto: un hecho de avance en la tarea del PLC, con lo que dijo Marcos tal cual, atribuido a él y con
     auditoría. La tarea sigue `en_curso`: ni estado, ni fecha, ni previsión nuevos, ni aviso a Ismael. La
     tarea todavía no venció (vence hoy), así que no lleva la pregunta de la fecha (9j). La espera sigue
     abierta, porque la respuesta no trae nada cierto; la pregunta del estado de hoy queda contestada con
     un avance. Queda guardado un nuevo pedido del estado para el miércoles 28 (el día hábil siguiente),
     con la cuenta de pedidos sin respuesta de nuevo.
   - Confirmación: ninguna (decisión 9a).
   - La respuesta dice: que anotó lo que Marcos contó; que mañana le vuelve a preguntar, como algo que
     todavía no pasó.
   - La respuesta no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de
     Leda; una fecha que nadie dio; que se va a avisar a Ismael o que se escala; ninguna pregunta (la
     primera vez, con la tarea sin vencer, la pregunta queda para mañana).
   - Botones: ninguno.
   - Estado después: sin tema abierto, nada para después. La espera de la tarea del PLC sigue abierta.

3. **Nadie** escribe el resto del martes 27.
   →
   - Efecto: ningún otro mensaje de Leda a Marcos el martes.

4. **Leda**, por su cuenta, a Marcos (miércoles 28, 10:00): vuelve a pedir el estado; la tarea ya venció.
   →
   - Efecto: un mensaje privado en el outbox; ninguno a Ismael. La pregunta del estado de la tarea del PLC
     vuelve a quedar abierta; la espera, la misma.
   - El mensaje dice: lo que Marcos contó ayer; pide algo cierto: si la terminó, para cuándo la termina o
     si está trabada.
   - El mensaje no dice: que va a avisar a Ismael o que va a escalar (la cuenta de pedidos sin respuesta
     empezó de nuevo); que Marcos no contestó; un reproche.
   - Botones: ninguno.
   - Estado después: tema abierto, la pregunta del estado de la tarea del PLC.

5. **Marcos** escribe (miércoles 28, 10:40): "todo en orden, sigo con eso"
   →
   - Jugadas: `informar_avance` sobre la tarea del PLC, con las palabras de Marcos.
   - Efecto: un segundo hecho de avance, con sus palabras, atribuido y auditado; ni estado, ni fecha, ni
     aviso a Ismael. La tarea está vencida (un día hábil de atraso, lo calcula el código) y la respuesta no
     trae una fecha: la espera sigue abierta y queda guardado otro pedido del estado para el jueves 29.
   - La respuesta dice: que lo anotó; que la tarea venció el martes 27; una sola pregunta, directa: para
     qué día la va a tener (9j; es también la segunda respuesta sin nada cierto, 9h).
   - La respuesta no dice: una fecha propuesta por Leda; que va a escalar; un reproche por el atraso; dos
     preguntas juntas.
   - Botones: ninguno; la fecha es un dato libre.
   - Estado después: tema abierto, la pregunta de la fecha de la tarea del PLC; la espera sigue abierta.

6. **Marcos** escribe (miércoles 28, 10:45): "para el martes 3 la tengo"
   →
   - Jugadas: `anotar_prevision` sobre la tarea del PLC, con fecha martes 3 de noviembre y sin motivo.
   - Efecto: la previsión, con la fecha comprometida (martes 27) sin cambiar y el atraso, cinco días
     hábiles, calculado por el código; el aviso a Ismael guardado como en la conversación 02 (con lo que
     depende: la tarea de comunicaciones); la espera se cierra y la pregunta de la fecha, también; el pedido
     guardado para el jueves no sale (se omite con su motivo: ya contestó). El seguimiento se mueve al
     martes 3, la fecha que dio Marcos (9i).
   - La respuesta dice: que anotó que la termina el martes 3; que la fecha comprometida sigue siendo el
     martes 27; que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó.
   - La respuesta no dice: que la fecha comprometida cambió; que Ismael ya lo sabe; que el aviso a
     Ismael está guardado, en cola o sin enviar (conversación 18); otra pregunta.
   - Estado después: sin tema abierto, nada para después; ninguna espera abierta.

7. **Nadie** escribe; del miércoles 28 al lunes 2, Leda no le escribe a Marcos sobre la tarea del PLC.
   →
   - Efecto: el aviso de la previsión le llega a Ismael a las 10:55, terminado el margen para corregir
     (es de coordinación, dentro del horario); ningún escalamiento. El pedido guardado para el jueves se omite con su motivo (Marcos ya contestó),
     nunca en silencio, y no hay pedidos cada día hasta la fecha que dio (9i).

8. **Leda**, por su cuenta, a Marcos (martes 3, 10:00): el pedido de estado del día que Marcos dio (9i),
   en el mismo envío que el aviso previo de la tarea de comunicaciones (los avisos automáticos del día van
   juntos, mecánica §10).
   →
   - El mensaje dice: que hoy es el día que Marcos dio para la tarea del PLC; pide el estado; que la de
     comunicaciones vence el viernes 6, sin pedir respuesta por ella.
   - El mensaje no dice: que va a avisar a Ismael; un reproche; dos preguntas.
   - Botones: ninguno.
   - Estado después: tema abierto, la pregunta del estado de la tarea del PLC; la espera, abierta.

## Qué mide

- **Garantías (5b):** no inventa (un avance no es una entrega, ni una fecha, ni un estado nuevo; ninguna
  fecha que Marcos no dijo; ningún escalamiento ni aviso que no pasó); no deja sin salida (la primera vez
  dice cuándo vuelve a preguntar; la segunda pregunta para qué día); una sola pregunta por mensaje; no
  confunde la tarea (todo es de la del PLC; la de comunicaciones aparece sólo en el aviso a Ismael, como lo
  que depende, y en su propio aviso previo).
- **La escalera escala sólo el silencio:** después de un avance, el pedido del miércoles no avisa que va a
  escalar. Si Marcos no contestara ese pedido, ése sí cuenta como sin respuesta, y la escalera sigue desde
  ahí.
- **La regla de la tarea vencida (9j):** el martes, sin vencer, el avance no lleva pregunta; el miércoles,
  vencida, la lleva en la misma respuesta. Que Leda pregunte la fecha el martes es una falla; que no la
  pregunte el miércoles, también.
- **Falla de comprensión:** tomar "casi lista" como una entrega o un "terminé" (eso es la jugada de la
  entrega, conversación 12), como un inicio o como una previsión sin fecha; o no tomar "todo en orden"
  como otra respuesta sin nada cierto. Anotar un estado, una fecha o una entrega por un avance es una falla
  de garantía. "Ya la terminé" sigue siendo la entrega, y "estoy trabado", el bloqueo (conversación 03).
