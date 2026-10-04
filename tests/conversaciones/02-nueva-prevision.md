# 02. "Llego el 27, el proveedor se demoró"

**Qué prueba:** Marcos contesta el aviso con una fecha nueva y un motivo. Leda anota la nueva previsión,
avisa al referente y la fecha comprometida no cambia. ADR 0018, decisión 5a, segunda respuesta; ADR 0017,
decisión 4.

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (D+1); `en_curso` desde el
    lunes 19; sin bloqueos ni dependencias; sin previsiones anotadas.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; sin bloqueos ni dependencias.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** nada a Marcos ni a Ismael en el día.

## Hilo

1. **Leda**, por su cuenta, a Marcos (jueves 22, dentro del horario): el aviso del día hábil anterior al
   vencimiento de la tarea del PLC.
   →
   - Efecto: un mensaje privado en el outbox para Marcos.
   - El mensaje dice: la tarea del PLC, que vence mañana, que no hace falta contestar.
   - El mensaje no dice: la tarea de comunicaciones.
   - Botones: PENDIENTE (P4).
   - Estado después: el último aviso enviado a Marcos es el de la tarea del PLC.

2. **Marcos** escribe (jueves 22, 15:40): "llego el 27, el proveedor se demoró"
   →
   - Jugadas: `anotar_prevision` sobre la tarea del PLC, con fecha martes 27 y motivo "el proveedor se
     demoró".
   - Efecto: un hecho de nueva previsión con su motivo, atribuido a Marcos, con auditoría. La fecha
     comprometida sigue siendo el viernes 23. Un aviso a Ismael guardado como hechos (ADR 0018,
     decisión 8), que queda además donde la plataforma lo va a mostrar. No se anota un bloqueo: Marcos
     informa un atraso con fecha, no que no puede avanzar (constitución §8 distingue bloqueo de atraso).
   - Confirmación: PENDIENTE (P3): ¿anotar la previsión y avisar a Ismael lleva confirmación de Marcos, o
     borrador y pregunta de atribución? Hasta decidirlo, el efecto ocurre en este paso o en el 3.
   - La respuesta dice: la previsión del 27 y su motivo; que la fecha comprometida sigue siendo el 23; que
     Ismael se entera, sólo si el código informa que el aviso quedó guardado.
   - La respuesta no dice: que la fecha cambió; que Ismael aceptó; que la tarea está bloqueada.
   - Botones: ninguno, salvo los de la confirmación si P3 la pide.
   - Estado después: sin tema abierto, nada para después.

3. **Marcos** escribe "si dale" `[sólo si P3 pide confirmación]`.
   →
   - Jugadas: `confirmar`, con la guarda de la decisión 2 (lo último que vio, sin cambios).
   - Efecto: el del paso 2, una sola vez.
   - Estado después: nada mostrado para confirmar.

4. **Leda**, por su cuenta, a Ismael (jueves 22, enseguida, dentro del horario): el aviso de la nueva
   previsión.
   →
   - Efecto: un mensaje privado en el outbox para Ismael, redactado justo antes de enviarlo.
   - El mensaje dice: que Marcos prevé llegar el martes 27 con la tarea del PLC y por qué. PENDIENTE (P6):
     ¿lleva también la fecha comprometida y que la fecha se cambia en la plataforma?
   - El mensaje no dice: que la fecha ya cambió; nada que Marcos no dijo.
   - Botones: ninguno para aceptar o cambiar la fecha: esa operación no existe por chat (ADR 0017,
     decisión 4).
   - Estado de Ismael después: sin tema abierto; el aviso no espera respuesta por chat.

5. **Leda**, por su cuenta, a Marcos (viernes 23, dentro del horario): el recordatorio del día del
   vencimiento. Sigue contra la fecha comprometida (ADR 0017, decisión 4).
   →
   - El mensaje dice: que la tarea del PLC vence hoy; que Marcos ya dio el 27 como previsión y que Ismael
     está al tanto.
   - El mensaje no dice: nada que trate a Marcos como si no hubiera avisado; un pedido de fecha nueva; que
     la fecha cambió.

## Qué mide

- **Garantías (5b):** no inventa (la fecha comprometida no cambia y nadie aceptó nada); no hace sin
  confirmación lo que la requiere (P3); no deja sin salida; no confunde la tarea (la previsión va a la del
  PLC).
- **Falla de comprensión:** que la IA no tome "llego el 27" como una fecha nueva. Tiene que preguntar;
  anotar un inicio, un bloqueo o cambiar la fecha es una falla de garantía.
