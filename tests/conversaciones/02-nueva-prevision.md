# 02. "Llego el 27, el proveedor se demoró"

**Qué prueba:** Marcos contesta el aviso con una fecha nueva y un motivo. Leda anota la nueva previsión,
directo, y avisa al referente con el atraso que calcula el código y lo que depende de la tarea; la fecha
comprometida no cambia. Desde ahí el seguimiento se mueve a la previsión: el día del vencimiento, un
solo recordatorio que no pide nada; el día de la previsión, el pedido de estado, y sin respuesta, la escalera
desde esa fecha. ADR 0018, decisión 5a, segunda respuesta, y decisiones 9a, 9b y 9i; ADR 0017, decisión 4.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (tres días hábiles después
    de D); `en_curso` desde el lunes 19; sin bloqueos; sin previsiones anotadas.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; depende de la del PLC con una dependencia bloqueante (la de la semilla).
    Criterio de aceptación: "Los equipos de la comprimidora se comunican con el PLC por la red de planta
    sin errores durante una hora".
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** nada a Marcos ni a Ismael en la semana.

## Hilo

1. **Leda**, por su cuenta, a Marcos (martes 20, 10:00): el aviso previo de la tarea del PLC.
   →
   - Efecto: un mensaje privado en el outbox para Marcos.
   - El mensaje dice: la tarea del PLC, que vence el viernes 23, que no hace falta contestar.
   - El mensaje no dice: la tarea de comunicaciones.
   - Botones: ninguno (decisión 9b).
   - Estado después: el último aviso enviado a Marcos es el de la tarea del PLC.

2. **Marcos** escribe (martes 20, 15:40): "llego el 27, el proveedor se demoró"
   →
   - Jugadas: `anotar_prevision` sobre la tarea del PLC, con fecha martes 27 y motivo "el proveedor se
     demoró".
   - Efecto: un hecho de nueva previsión con su motivo, atribuido a Marcos, con auditoría. La fecha
     comprometida sigue siendo el viernes 23. Un aviso a Ismael guardado como hechos (ADR 0018,
     decisión 8), que queda además donde la plataforma lo va a mostrar. No se anota un bloqueo: Marcos
     informa un atraso con fecha, no que no puede avanzar (constitución §8 distingue bloqueo de atraso).
   - Confirmación: ninguna; la previsión y su aviso se anotan directo (decisión 9a).
   - La respuesta dice: la previsión del 27 y su motivo; que la fecha comprometida sigue siendo el 23; que
     Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó.
   - La respuesta no dice: que la fecha cambió; que Ismael aceptó; que la tarea está bloqueada; que
     el aviso a Ismael está guardado, en cola o sin enviar (conversación 18).
   - Botones: ninguno.
   - Estado después: sin tema abierto, nada para después.

3. **Leda**, por su cuenta, a Ismael (martes 20, 15:50, dentro del horario): el aviso de la nueva
   previsión, terminado el margen para corregir, diez minutos después de lo que dijo Marcos.
   →
   - Efecto: un mensaje privado en el outbox para Ismael, redactado justo antes de enviarlo con los hechos
     de ese momento.
   - El mensaje dice: la tarea del PLC; que Marcos prevé llegar el martes 27 y por qué; que la fecha
     comprometida es el viernes 23; el atraso, dos días hábiles, calculado por el código; que la tarea de
     comunicaciones depende de ella (decisión 9b).
   - El mensaje no dice: que la fecha ya cambió; cómo se cambia la fecha (la plataforma no existe); un
     atraso que no salga del código; nada que Marcos no dijo.
   - Botones: ninguno para aceptar o cambiar la fecha: esa operación no existe por chat (ADR 0017,
     decisión 4).
   - Estado de Ismael después: sin tema abierto; el aviso no espera respuesta por chat.

4. **Leda**, por su cuenta, a Marcos (viernes 23, 10:00): un solo recordatorio del día del vencimiento.
   Hay una previsión posterior, así que el seguimiento sigue la previsión (decisión 9i) y la fecha
   comprometida no cambia (ADR 0017, decisión 4).
   →
   - Efecto: un mensaje privado en el outbox para Marcos. No abre una espera ni una pregunta: no pide nada.
     Ninguno a Ismael (ya está al tanto por el aviso del paso 3).
   - El mensaje dice: que la tarea del PLC vencía hoy; que Marcos dio el 27 como previsión y que Ismael está
     al tanto (ya le llegó el aviso); que el martes 27 le va a pedir el estado, como algo que todavía
     no pasó.
   - El mensaje no dice: que la fecha cambió; nada que trate a Marcos como si no hubiera avisado; que va a
     escalar; una pregunta.
   - Botones: ninguno.
   - Estado después: sin tema abierto; ninguna espera abierta.

5. **Nadie** escribe del viernes 23 al martes 27 a las 10:00.
   →
   - Efecto: ningún mensaje de Leda sobre la tarea del PLC el lunes 26: hasta la previsión no pide nada
     cada día.

6. **Leda**, por su cuenta, a Marcos (martes 27, 10:00): el pedido de estado del día de la previsión, como
   si fuera el del vencimiento.
   →
   - Efecto: un mensaje privado en el outbox; queda abierta la espera de su respuesta (decisión 9b) y la
     pregunta del estado de la tarea del PLC.
   - El mensaje dice: que hoy es el día que Marcos previó para la tarea del PLC; que la fecha comprometida
     era el viernes 23 y el atraso, dos días hábiles, calculado por el código; pide el estado.
   - El mensaje no dice: que la fecha comprometida cambió; que va a escalar; un reproche.
   - Botones: ninguno.

7. **Nadie** escribe del martes 27 al viernes 30.
   →
   - Efecto: la escalera sigue desde el 27, como la de la conversación 04 desde el vencimiento: el miércoles
     28, el segundo pedido; el jueves 29, el tercero, que avisa que se le va a avisar a Ismael; el viernes
     30, el escalamiento a Ismael por falta de respuesta, con la previsión, la fecha comprometida y el
     atraso del código. Es información: no le pide a Ismael que persiga ni que resuelva nada.

## Qué mide

- **Garantías (5b):** no inventa (la fecha comprometida no cambia, nadie aceptó nada y el atraso es el del
  código); no hace sin confirmación lo que la requiere (nada la requiere en este circuito); no deja sin
  salida; no confunde la tarea (la previsión va a la del PLC, y la de comunicaciones aparece sólo como lo que
  depende).
- **El seguimiento sigue la previsión (9i):** el día del vencimiento, un solo recordatorio que no pide nada;
  ningún pedido diario hasta la previsión; el día de la previsión, el pedido de estado; sin respuesta, la
  escalera desde esa fecha. El atraso sigue visible contra la fecha comprometida.
- **Falla de comprensión:** que la IA no tome "llego el 27" como una fecha nueva. Tiene que preguntar;
  anotar un inicio, un bloqueo o cambiar la fecha es una falla de garantía.
