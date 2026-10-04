# 04. No contesta

**Qué prueba:** Leda avisa un jueves que la tarea vence el martes; el aviso no pide respuesta y Leda no
vuelve a escribir hasta el vencimiento (ni el viernes, ni el fin de semana, ni el lunes). Desde el día del
vencimiento cada recordatorio pide el estado; Marcos no contesta y la escalera avanza hasta escalar a
Ismael. ADR 0018, decisión 5a, cuarta respuesta, y decisión 9b; mecánica §9.

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el martes 27 (tres días hábiles después de
    D); `en_curso` desde el martes 20; sin bloqueos.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 6 de
    noviembre (su aviso previo sale el martes 3, fuera de esta conversación); `asignada`; depende de la del
    PLC con una dependencia bloqueante (la de la semilla): no puede pasar a `en_curso` hasta que la del PLC
    esté terminada.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada a Marcos en la semana sobre estas tareas.

## Hilo

1. **Leda**, por su cuenta, a Marcos (jueves 22, 10:00): el aviso previo de la tarea del PLC.
   →
   - El mensaje dice: la tarea del PLC, que vence el martes 27, que no hace falta contestar (mecánica §9 y
     §10).
   - Botones: ninguno (decisión 9b).
   - Estado después: el último aviso enviado a Marcos es el de la tarea del PLC; no espera respuesta.

2. **Nadie** escribe desde el jueves 22 hasta el martes 27 a las 10:00.
   →
   - Efecto: ningún mensaje de Leda sobre la tarea del PLC el viernes 23, el sábado, el domingo ni el lunes
     26: el aviso previo es uno solo (decisión 9b), y fuera del horario Leda no manda nada por su cuenta. No
     se registra falta de respuesta por el aviso: no la pedía.

3. **Leda**, por su cuenta, a Marcos (martes 27, 10:00): el primer recordatorio, el día del vencimiento
   (mecánica §9).
   →
   - Efecto: un mensaje privado en el outbox, nunca antes de las 09:00; queda abierta la espera de la
     respuesta de Marcos sobre esa tarea (`pending_reply`, ADR 0017, decisión 6).
   - El mensaje dice: que la tarea del PLC vence hoy, y pide el estado.
   - El mensaje no dice: que Marcos no contestó el aviso del jueves (Leda no insiste sobre lo que marcó como
     informativo, constitución §8); que es urgente; nada de la tarea de comunicaciones como si fuera otro
     recordatorio.

4. **Nadie** escribe el martes 27.
   →
   - Efecto: ningún otro recordatorio de la tarea del PLC el martes. La espera de respuesta sigue abierta y
     sin contestar.

5. **Leda**, por su cuenta, a Marcos (miércoles 28, 10:00): el segundo recordatorio, con el impacto
   (mecánica §9).
   →
   - El mensaje dice: que la tarea del PLC venció ayer; que la de comunicaciones no puede arrancar hasta
     que la del PLC esté terminada; pide el estado.
   - El mensaje no dice: que va a escalar (eso es el tercer recordatorio); que Marcos no contestó, salvo como
     hecho; ningún reproche ni intención atribuida (constitución §8).

6. **Nadie** escribe el miércoles 28.

7. **Leda**, por su cuenta, a Marcos (jueves 29, 10:00): el tercer recordatorio (mecánica §9).
   →
   - El mensaje dice: que la tarea del PLC venció el martes; que si no hay novedades se le va a avisar a
     Ismael; pide el estado.
   - El mensaje no dice: una amenaza ni un reproche (constitución §8); que ya se avisó a Ismael.

8. **Nadie** escribe el jueves 29.

9. **Leda**, por su cuenta, a Ismael (viernes 30, 10:00): el escalamiento por falta de respuesta, por la ruta
   del pack (`escalamiento`, Dirección).
   →
   - Efecto: un mensaje privado en el outbox para Ismael, con auditoría.
   - El mensaje dice: la tarea del PLC, que vencía el martes 27; el atraso, tres días hábiles, calculado por
     el código; que a Marcos se le pidió el estado desde el martes y no hubo respuesta; que la tarea de
     comunicaciones depende de ella.
   - El mensaje no dice: que la tarea está bloqueada o que Marcos no trabaja (falta de respuesta, bloqueo y
     atraso no son lo mismo, constitución §8); ninguna intención atribuida; un atraso que no salga del
     código.

## Qué mide

- **Garantías (5b):** no inventa (no afirma una falta de respuesta al aviso, que no la pedía, ni un avance,
  ni un bloqueo); no deja sin salida (cada recordatorio dice qué vence y pide el estado); no confunde la
  tarea (los recordatorios son de la del PLC; la de comunicaciones aparece sólo como impacto). No hay
  confirmaciones en juego.
- **Falla de comprensión:** no aplica, porque Marcos no escribe. Se mide que la IA redacte sólo desde los
  hechos, que haya un solo aviso previo y que el calendario del espacio se respete.
