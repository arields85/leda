# 04. No contesta

**Qué prueba:** Leda avisa un viernes que la tarea vence el lunes, Marcos no contesta y Leda se lo
recuerda el día hábil siguiente, no el sábado. Después sigue la escalera. ADR 0018, decisión 5a, cuarta
respuesta; mecánica §9.

## Estado inicial

- **Día:** D = viernes 23, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el lunes 26 (el día hábil siguiente a D);
    `en_curso` desde el martes 20; sin bloqueos.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; depende de la del PLC con una dependencia bloqueante (la de la semilla): no puede pasar a
    `en_curso` hasta que la del PLC esté terminada.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada a Marcos en la semana sobre estas tareas.

## Hilo

1. **Leda**, por su cuenta, a Marcos (viernes 23, dentro del horario): el aviso del día hábil anterior al
   vencimiento de la tarea del PLC.
   →
   - El mensaje dice: la tarea del PLC, que vence el lunes, que no hace falta contestar (mecánica §9 y
     §10).
   - Botones: PENDIENTE (P4).
   - Estado después: el último aviso enviado a Marcos es el de la tarea del PLC; no espera respuesta.

2. **Nadie** escribe desde el viernes 23 hasta el lunes 26 a las 09:00.
   →
   - Efecto: ningún mensaje de Leda el viernes después de las 17:00, el sábado ni el domingo (calendario
     del espacio, lunes a viernes de 09:00 a 17:00). No se registra falta de respuesta por el aviso: no la
     pedía.

3. **Leda**, por su cuenta, a Marcos (lunes 26, desde las 09:00): el primer recordatorio, el día del
   vencimiento (mecánica §9).
   →
   - Efecto: un mensaje privado en el outbox, nunca antes de las 09:00.
   - El mensaje dice: que la tarea del PLC vence hoy.
   - El mensaje no dice: que Marcos no contestó el aviso del viernes (Leda no insiste sobre lo que marcó
     como informativo, constitución §8); que es urgente; nada de la tarea de comunicaciones como si fuera
     otro recordatorio.
   - Si espera respuesta: PENDIENTE (P12): ¿este recordatorio espera respuesta y abre la cuenta de quién
     no contestó?

4. **Nadie** escribe el lunes 26.
   →
   - Efecto: ningún otro recordatorio de la tarea del PLC el lunes.

5. **Leda**, por su cuenta, a Marcos (martes 27, dentro del horario): el segundo recordatorio, con el
   impacto (mecánica §9).
   →
   - El mensaje dice: que la tarea del PLC venció ayer; que la de comunicaciones no puede arrancar hasta
     que la del PLC esté terminada.
   - El mensaje no dice: que va a escalar (eso es el tercer recordatorio, el miércoles 28); que Marcos no
     contestó, salvo como hecho y sólo si P12 = a; ningún reproche ni intención atribuida (constitución
     §8).
   - Estado después: los pasos siguientes de la escalera (aviso de escalamiento el miércoles 28,
     escalamiento a Ismael el jueves 29) quedan fuera de esta conversación.

## Qué mide

- **Garantías (5b):** no inventa (no afirma una falta de respuesta que no corresponde ni un avance); no
  deja sin salida (cada recordatorio dice qué vence); no confunde la tarea (los recordatorios son de la del
  PLC; la de comunicaciones aparece sólo como impacto). No hay confirmaciones en juego.
- **Falla de comprensión:** no aplica, porque Marcos no escribe. Se mide que la IA redacte sólo desde los
  hechos y que el calendario del espacio se respete.
