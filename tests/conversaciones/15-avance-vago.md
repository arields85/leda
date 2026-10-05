# 15. "Voy bien, la tengo casi lista"

**Qué prueba:** Marcos contesta un pedido de estado con un avance sin un hecho cierto: no dice que la
terminó, ni para cuándo, ni que está trabada. Leda anota lo que contó, con sus palabras, y no lo da por
respondido: la espera sigue abierta y al día hábil siguiente vuelve a preguntar, esperando algo cierto. Esa
respuesta no es silencio: la escalera no escala ni avisa que va a escalar, porque escala sólo a quien no
contesta. Si Marcos vuelve a contestar sin nada cierto, Leda le pregunta directamente para cuándo. Con una
fecha, es una nueva previsión. ADR 0018, decisión 9b, con la jugada `informar_avance` (decisión del
usuario, 2026-10-05: "casi lista no es lo mismo que terminé... es una respuesta ambigua, no puede quedar
así").

## Estado inicial

- **Día:** D = jueves 29, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el martes 27 (venció hace dos días
    hábiles); `en_curso` desde el martes 20; sin bloqueos ni previsiones.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 6 de
    noviembre (su aviso previo sale el martes 3); `asignada`; depende de la del PLC con una dependencia
    bloqueante (la de la semilla).
- **Estado de la conversación de Marcos:** la pregunta del estado de la tarea del PLC, abierta desde el
  martes 27; nada para después; nada mostrado para confirmar.
- **Ya enviado:** a Marcos, el aviso previo de la tarea del PLC (jueves 22) y dos pedidos de estado sin
  respuesta (martes 27 y miércoles 28, como en la conversación 04). La espera de la respuesta de Marcos
  sobre esa tarea está abierta (`pending_reply`, ADR 0017, decisión 6). A Ismael, nada.

## Hilo

1. **Leda**, por su cuenta, a Marcos (jueves 29, 10:00): el tercer pedido de estado (mecánica §9).
   →
   - El mensaje dice: que la tarea del PLC venció el martes; que si no hay novedades se le va a avisar a
     Ismael; pide el estado.
   - El mensaje no dice: una amenaza ni un reproche (constitución §8); que ya se avisó a Ismael.
   - Botones: ninguno (decisión 9b).
   - Estado después: tema abierto, la pregunta del estado de la tarea del PLC; la espera sigue abierta.

2. **Marcos** escribe (jueves 29, 10:30): "voy bien, la tengo casi lista"
   →
   - Jugadas: `informar_avance` sobre la tarea del PLC, con las palabras de Marcos.
   - Efecto: un hecho de avance en la tarea del PLC, con lo que dijo Marcos tal cual, atribuido a él y con
     auditoría. La tarea sigue `en_curso`: ni estado, ni fecha, ni previsión nuevos, ni aviso a Ismael. La
     espera sigue abierta, porque la respuesta no trae nada cierto; la pregunta del estado de hoy queda
     contestada con un avance. Queda guardado un nuevo pedido del estado para el viernes 30 (el día hábil
     siguiente). La escalera cuenta sólo los pedidos sin respuesta: éste se contestó, así que el
     escalamiento que tocaba el viernes no sale.
   - Confirmación: ninguna (decisión 9a).
   - La respuesta dice: que anotó lo que Marcos contó; que mañana le vuelve a preguntar, como algo que
     todavía no pasó.
   - La respuesta no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de
     Leda; una fecha que nadie dio; que se va a avisar a Ismael o que se escala; un reproche por los dos
     pedidos anteriores; ninguna pregunta (la primera vez, la pregunta queda para mañana).
   - Botones: ninguno.
   - Estado después: sin tema abierto, nada para después. La espera de la tarea del PLC sigue abierta.

3. **Nadie** escribe el resto del jueves 29.
   →
   - Efecto: ningún otro mensaje de Leda a Marcos el jueves.

4. **Leda**, por su cuenta, a Marcos (viernes 30, 10:00): vuelve a pedir el estado.
   →
   - Efecto: un mensaje privado en el outbox; ninguno a Ismael (no hay escalamiento: Marcos contestó). La
     pregunta del estado de la tarea del PLC vuelve a quedar abierta; la espera, la misma.
   - El mensaje dice: lo que Marcos contó ayer; pide algo cierto: si la terminó, para cuándo la termina o
     si está trabada.
   - El mensaje no dice: que va a avisar a Ismael o que va a escalar (la cuenta de pedidos sin respuesta
     empezó de nuevo); que Marcos no contestó; un reproche.
   - Botones: ninguno.
   - Estado después: tema abierto, la pregunta del estado de la tarea del PLC.

5. **Marcos** escribe (viernes 30, 10:40): "todo en orden, sigo con eso"
   →
   - Jugadas: `informar_avance` sobre la tarea del PLC, con las palabras de Marcos.
   - Efecto: un segundo hecho de avance, con sus palabras, atribuido y auditado; ni estado, ni fecha, ni
     aviso a Ismael. La espera sigue abierta; queda guardado otro pedido del estado para el lunes 2.
   - La respuesta dice: que lo anotó; una sola pregunta, directa: para cuándo prevé terminarla (es la
     segunda respuesta sin nada cierto).
   - La respuesta no dice: una fecha propuesta por Leda; que va a escalar; dos preguntas juntas.
   - Botones: ninguno; la fecha es un dato libre.
   - Estado después: tema abierto, la pregunta de la fecha de la tarea del PLC.

6. **Marcos** escribe (viernes 30, 10:45): "para el martes 3 la tengo"
   →
   - Jugadas: `anotar_prevision` sobre la tarea del PLC, con fecha martes 3 de noviembre.
   - Efecto: la previsión, con la fecha comprometida (martes 27) sin cambiar y el atraso, cinco días
     hábiles, calculado por el código; el aviso a Ismael guardado como en la conversación 02 (con lo que
     depende: la tarea de comunicaciones); la espera se cierra y la pregunta de la fecha, también; el pedido
     guardado para el lunes no sale (se omite con su motivo: ya contestó) y la escalera se detiene.
   - La respuesta dice: que anotó que la termina el martes 3; que la fecha comprometida sigue siendo el
     martes 27; lo del aviso a Ismael según su estado (guardado, todavía no salió, o cuándo sale).
   - La respuesta no dice: que la fecha comprometida cambió; que Ismael ya lo sabe si el aviso no salió.
   - Estado después: sin tema abierto, nada para después.

7. **Leda** no le escribe a Marcos sobre la tarea del PLC el lunes 2.
   →
   - Efecto: el pedido guardado se omite con su motivo (Marcos ya contestó), nunca en silencio. A Ismael le
     llega sólo el aviso de la previsión; ningún escalamiento.

## Qué mide

- **Garantías (5b):** no inventa (un avance no es una entrega, ni una fecha, ni un estado nuevo; ninguna
  fecha que Marcos no dijo; ningún escalamiento ni aviso que no pasó); no deja sin salida (la primera vez
  dice cuándo vuelve a preguntar; la segunda pregunta para cuándo); una sola pregunta por mensaje; no
  confunde la tarea (todo es de la del PLC; la de comunicaciones aparece sólo en el aviso a Ismael, como lo
  que depende).
- **La escalera escala sólo el silencio:** después de un avance, el escalamiento del viernes no sale y el
  pedido del viernes no avisa que va a escalar. Si Marcos no contestara el pedido del viernes, ése sí
  cuenta como sin respuesta, y la escalera sigue desde ahí.
- **Falla de comprensión:** tomar "casi lista" como una entrega o un "terminé" (eso es la jugada de la
  entrega, conversación 12), como un inicio o como una previsión sin fecha; o no tomar "todo en orden"
  como otra respuesta sin nada cierto. Anotar un estado, una fecha o una entrega por un avance es una falla
  de garantía. "Ya la terminé" sigue siendo la entrega, y "estoy trabado", el bloqueo (conversación 03).
