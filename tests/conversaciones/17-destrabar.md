# 17. "Llegó el switch, sigo"

**Qué prueba:** la tarea del PLC está trabada porque Marcos espera el switch, y Leda espera que le
diga quién lo puede destrabar. Marcos cuenta que el switch llegó y que sigue. Leda cierra el bloqueo,
directo, y la tarea vuelve al estado que tenía antes de trabarse (mecánica §3); la pregunta de quién lo
destraba y su espera se cierran, y el seguimiento de la tarea vuelve: el día del vencimiento Leda pide
el estado. Ese día Marcos se vuelve a trabar y se destraba otra vez: como el seguimiento ya había
empezado, Leda vuelve a pedir el estado el día hábil siguiente. Decisión del usuario del 2026-10-05: la
jugada nueva `destrabar` (ADR 0018, decisión 9l), que resuelve el `PENDIENTE` de 9k.

## Estado inicial

- **Día:** D = miércoles 21, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (dos días hábiles después
    de D); `en_curso` desde el lunes 19 hasta el martes 20, cuando Marcos escribió "estoy trabado,
    espero el switch": desde entonces, `bloqueada`, con un bloqueo abierto con esa causa.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; depende de la del PLC con una dependencia bloqueante (la de la semilla).
    Criterio de aceptación: "Los equipos de la comprimidora se comunican con el PLC por la red de planta
    sin errores durante una hora".
- **Estado de la conversación de Marcos:** tema abierto, la pregunta de quién puede destrabar el
  bloqueo de la tarea del PLC, hecha el martes 20 a las 10:20; su espera está abierta (9c, paso 2);
  nada para después; nada mostrado para confirmar. **De Ismael:** sin tema abierto.
- **Ya enviado:** a Marcos, el aviso previo de la tarea del PLC (martes 20, 10:00) y la respuesta al
  bloqueo, con la pregunta de quién lo destraba. A Ismael, nada.

## Hilo

1. **Marcos** escribe (miércoles 21, 09:40): "llego el switch, sigo"
   →
   - Jugadas: `destrabar` sobre la tarea del PLC (la pregunta abierta es de esa tarea).
   - Efecto: el bloqueo se cierra, con la resolución en las palabras de Marcos, quién y cuándo; la
     tarea pasa de `bloqueada` a `en_curso`, el estado que tenía antes de trabarse (mecánica §3), con su
     evento y auditoría. La pregunta de quién lo destraba y su espera se cierran: ya no hay nada que
     destrabar. La tarea vuelve al seguimiento: vence el viernes 23 y todavía no le tocaba ningún pedido
     de estado, así que no se guarda nada. Ningún aviso a Ismael.
   - Confirmación: ninguna; se anota directo, como el bloqueo (decisión 9a).
   - La respuesta dice: que quedó anotado que la tarea se destrabó y sigue en curso; el próximo
     paso concreto: que Leda le pide el estado el viernes 23, el día del vencimiento, o que puede avisar si
     se vuelve a trabar.
   - La respuesta no dice: que arrancó la tarea (ya estaba en curso antes de trabarse); una fecha para
     terminarla que nadie dio; otra vez la pregunta de quién lo destraba; que Ismael se enteró.
   - Botones: ninguno.
   - Estado después: sin tema abierto, nada para después; ninguna espera abierta.

2. **Nadie** escribe el resto del miércoles 21 ni el jueves 22.
   →
   - Efecto: Leda no repite la pregunta de quién lo destraba (se cerró) ni le escribe a Marcos sobre la
     tarea del PLC; ningún mensaje a Ismael.

3. **Leda**, por su cuenta, a Marcos (viernes 23, 10:00): el primer pedido de estado de la tarea del PLC
   (mecánica §9): el seguimiento volvió con el bloqueo cerrado.
   →
   - El mensaje dice: que la tarea del PLC vence hoy; pide el estado.
   - El mensaje no dice: que va a avisar a Ismael; nada del bloqueo, que ya se cerró.
   - Botones: ninguno (decisión 9b).
   - Estado después: tema abierto, la pregunta del estado de la tarea del PLC; la espera, abierta.

4. **Marcos** escribe (viernes 23, 10:20): "se quemo la fuente, otra vez parado"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del PLC, con causa "se quemo la fuente".
   - Efecto: un bloqueo nuevo, con su causa; la tarea pasa de `en_curso` a `bloqueada`; la espera del
     estado se cierra (contestó) y la escalera de la tarea se detiene (mecánica §9). Ningún aviso a
     Ismael (9c, paso 4).
   - La respuesta dice: que quedó anotado el bloqueo y su causa; una sola pregunta: quién lo puede
     destrabar (9c, paso 2).
   - La respuesta no dice: que Ismael se enteró o se va a enterar; el bloqueo anterior, que ya se cerró.
   - Estado después: tema abierto, la pregunta de quién lo destraba; su espera, abierta.

5. **Marcos** escribe (viernes 23, 11:30): "ya cambie la fuente, sigo"
   →
   - Jugadas: `destrabar` sobre la tarea del PLC.
   - Efecto: el bloqueo de la fuente se cierra y la tarea vuelve a `en_curso`; la pregunta de quién lo
     destraba y su espera se cierran. Esta vez el seguimiento ya había empezado (la tarea vence hoy y
     Leda ya le pidió el estado): Marcos contestó, pero no dijo nada cierto sobre cuándo la termina, así
     que la espera del estado queda abierta y la cuenta de pedidos empieza de nuevo, como después de un
     avance (9h): Leda le va a volver a pedir el estado el lunes 26, el día hábil siguiente. La tarea
     todavía no está vencida (vence hoy), así que no lleva la pregunta de para cuándo (9j).
   - La respuesta dice: que quedó anotado que la tarea se destrabó y sigue en curso; que el lunes le
     vuelve a pedir el estado, como algo que todavía no pasó.
   - La respuesta no dice: una fecha para terminarla; que va a avisar a Ismael o que se escala; un
     reproche; otra pregunta.
   - Botones: ninguno.
   - Estado después: sin tema abierto; la espera del estado de la tarea del PLC, abierta.

6. **Leda**, por su cuenta, a Marcos (lunes 26, 10:00): el pedido de estado del día hábil siguiente.
   →
   - El mensaje dice: que la tarea del PLC venció el viernes 23; lo que Marcos contó (que se destrabó);
     pide el estado: si la terminó, para cuándo o si está trabada.
   - El mensaje no dice: que va a avisar a Ismael (es el primer pedido de la cuenta nueva); un reproche.
   - Botones: ninguno.
   - Estado después: tema abierto, la pregunta del estado de la tarea del PLC; la espera, abierta.

## Qué mide

- **Garantías (5b):** no inventa (no da por empezada una tarea que ya estaba en curso, ni una fecha que
  nadie dio, ni cierra un bloqueo que la persona no dio por resuelto); no hace sin confirmación lo que la
  requiere (nada la requiere en este circuito); no deja sin salida (los pasos 1 y 5 dicen qué sigue); no
  confunde la tarea.
- **La jugada `destrabar`:** cierra el bloqueo y la tarea vuelve al estado de antes; cierra la pregunta
  de quién lo destraba y su espera (ninguna repregunta el miércoles 21); el seguimiento vuelve: antes de
  su fecha, la escalera sigue sola (paso 3); con el seguimiento ya empezado, Leda vuelve a pedir el
  estado el día hábil siguiente (pasos 5 y 6).
- **Falla de comprensión:** que la IA tome "llego el switch, sigo" o "ya cambie la fuente, sigo" como un
  inicio, una previsión o un avance, y no como el fin del bloqueo; o "se quemo la fuente, otra vez
  parado" como otra cosa que un bloqueo. Si no entiende, pregunta; anotar un inicio, una fecha o un
  aviso a Ismael es una falla de garantía.
