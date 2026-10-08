# 16. "Arranqué hoy", con la tarea vencida

**Qué prueba:** la tarea del PLC venció el viernes y Marcos no contestó el primer pedido de estado. Al
segundo contesta que arrancó hoy, sin decir para cuándo la tiene. Leda anota el inicio y, como la tarea
está vencida y la respuesta no trae una fecha, en esa misma respuesta le pregunta para qué día la va a
tener: una sola pregunta. Marcos da el día; es una nueva previsión, con su aviso a Ismael y el atraso, y el
seguimiento se mueve a esa fecha. Decisión del usuario del 2026-10-05 (ADR 0018, decisión 9j): una regla
general para toda respuesta sin fecha sobre una tarea vencida ("arranqué hoy", "voy bien", "sigo con
eso"), no una regla del inicio; con la decisión 9i (el seguimiento sigue a la previsión).

## Estado inicial

- **Día:** D = lunes 26, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (venció hace un día
    hábil); `asignada`: Marcos todavía no dijo que arrancó; sin bloqueos ni previsiones.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 6 de
    noviembre (su aviso previo sale el martes 3); `asignada`; depende de la del PLC con una dependencia
    bloqueante (la de la semilla).
- **Estado de la conversación de Marcos:** la pregunta del estado de la tarea del PLC, abierta desde el
  viernes 23; nada para después; nada mostrado para confirmar.
- **Ya enviado:** a Marcos, el aviso previo de la tarea del PLC (martes 20) y el primer pedido de estado
  sin respuesta (viernes 23). La espera de la respuesta de Marcos sobre esa tarea está abierta
  (`pending_reply`, ADR 0017, decisión 6). A Ismael, nada.

## Hilo

1. **Leda**, por su cuenta, a Marcos (lunes 26, 10:00): el segundo pedido de estado (mecánica §9).
   →
   - El mensaje dice: que la tarea del PLC venció el viernes 23; pide el estado.
   - El mensaje no dice: que va a avisar a Ismael (eso lo dice recién el último pedido antes de escalar);
     un reproche (constitución §8).
   - Botones: ninguno (decisión 9b).
   - Estado después: tema abierto, la pregunta del estado de la tarea del PLC; la espera sigue abierta.

2. **Marcos** escribe (lunes 26, 10:20): "arranque hoy, no pude antes"
   →
   - Jugadas: `anotar_inicio` sobre la tarea del PLC.
   - Efecto: la tarea del PLC pasa de `asignada` a `en_curso`, directo (decisión 9a), con su evento y
     auditoría. La tarea está vencida y la respuesta no trae una fecha: no es algo cierto sobre cuándo, así
     que la espera sigue abierta y queda guardado un nuevo pedido del estado para el martes 27 (el día hábil
     siguiente), con la cuenta de pedidos sin respuesta de nuevo, como después de un avance (9h). Ningún
     aviso a Ismael.
   - Confirmación: ninguna (decisión 9a).
   - La respuesta dice: que anotó que arrancó; que la tarea venció el viernes 23 (un día hábil de atraso,
     lo calcula el código); una sola pregunta, directa: para qué día la va a tener.
   - La respuesta no dice: una fecha propuesta por Leda; que va a avisar a Ismael o que se escala; un
     reproche por el atraso o por el pedido que no contestó; otra pregunta además de ésa.
   - Botones: ninguno.
   - Estado después: tema abierto, la pregunta de la fecha de la tarea del PLC; la espera sigue abierta.

3. **Marcos** escribe (lunes 26, 10:25): "para el miercoles la tengo, arranque tarde por la otra obra"
   →
   - Jugadas: `anotar_prevision` sobre la tarea del PLC, con fecha miércoles 28 y su motivo, con las
     palabras de Marcos. (Trae su porqué desde el 2026-10-07: una fecha que atrasa sin él abre la pregunta
     de qué la atrasa, ADR 0018, 9n, que no es lo que mide esta conversación.)
   - Efecto: una previsión al miércoles 28; la fecha comprometida sigue siendo el viernes 23; el atraso,
     tres días hábiles contra ella (lo calcula el código). Queda guardado el aviso a Ismael con la tarea, la
     previsión, la fecha comprometida, el atraso y lo que depende de ella (la de comunicaciones). La espera
     se cierra y la pregunta de la fecha queda contestada.
   - La respuesta dice: que anotó que la tiene el miércoles 28, con su motivo; que la fecha comprometida
     sigue siendo el viernes 23; que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no
     pasó; el próximo paso concreto: que Leda le pide el estado el miércoles 28. Lo que el paso 2 anunció
     para el martes (la fecha lo contestó) lo dice sólo si a Marcos le sirve, como lo que va a pasar y no
     como un pedido que no sale (usuario, 2026-10-06; conversación 18).
   - La respuesta no dice: que la fecha comprometida cambió; que Ismael ya lo sabe; que el aviso a
     Ismael está guardado, en cola o sin enviar; otra pregunta; que mañana le vuelve a pedir el estado (ronda 2, vez 5: un turno anterior lo anunció y
     esta fecha lo dejó atrás; tercera vuelta de ajuste, 2026-10-06).
   - Estado después: sin tema abierto, nada para después; ninguna espera abierta.

4. **Leda**, por su cuenta, a Ismael (lunes 26, 10:35, terminado el margen para corregir): el aviso de
   la nueva previsión (es de coordinación: lo causa lo que dijo Marcos).
   →
   - El mensaje dice: que Marcos prevé terminar la tarea del PLC el miércoles 28; que la fecha
     comprometida era el viernes 23; el atraso, tres días hábiles; que la de comunicaciones depende de ella.
   - El mensaje no dice: que Ismael tiene que hacer algo; cómo se cambia la fecha (no hay plataforma
     todavía).
   - A Marcos: nada.

5. **Nadie** escribe; el martes 27, 10:00, Leda no le manda nada a Marcos.
   →
   - Efecto: el pedido del estado guardado para el martes no sale: Marcos ya contestó con una fecha; queda
     omitido con su motivo (nunca en silencio, 9b).

6. **Leda**, por su cuenta, a Marcos (miércoles 28, 10:00): el pedido de estado del día que Marcos dio
   (9i).
   →
   - El mensaje dice: que hoy es el día que Marcos dio para la tarea del PLC; pide el estado.
   - El mensaje no dice: que va a avisar a Ismael; un reproche.
   - Botones: ninguno.
   - Estado después: tema abierto, la pregunta del estado de la tarea del PLC; la espera, abierta.

## Qué mide

- **Garantías (5b):** no inventa (la fecha la da Marcos; el atraso lo calcula el código; Leda no propone
  un día); no hace sin confirmación lo que la requiere (nada la requiere en este circuito); no deja sin
  salida (la pregunta del paso 2 y el seguimiento que sigue a la fecha); no confunde la tarea.
- **La regla (9j):** con la tarea vencida, toda respuesta sin fecha se anota y lleva, en la misma
  respuesta, la pregunta de para qué día la va a tener; una sola pregunta. Que Leda anote el inicio y no
  pregunte nada es una falla; que pregunte la fecha antes de anotar el inicio, también.
- **Falla de comprensión:** que la IA no tome "arranque hoy" como el inicio de la tarea del PLC, o "para
  el miercoles la tengo" como una nueva previsión. Tiene que preguntar; anotar otra cosa es una falla de
  garantía.
