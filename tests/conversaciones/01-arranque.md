# 01. "Arranqué"

**Qué prueba:** Leda avisa que en tres días hábiles vence una tarea, Marcos contesta que arrancó y Leda
anota el inicio en esa tarea, directo. ADR 0018, decisión 5a, primera respuesta; decisiones 9a y 9b.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (tres días hábiles después
    de D); `asignada`; sin bloqueos ni dependencias.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; sin bloqueos ni dependencias.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada a Marcos en la semana.

## Hilo

1. **Leda**, por su cuenta, a Marcos (martes 20, 10:00): el aviso previo, tres días hábiles antes del
   vencimiento (mecánica §9; decisión 9b).
   →
   - Jugadas: ninguna; el mensaje lo inicia Leda. El código guarda los hechos y la IA lo redacta justo
     antes de enviarlo (ADR 0018, decisión 8).
   - Efecto: un mensaje privado en el outbox para Marcos y su turno en el registro.
   - El mensaje dice: el título de la tarea del PLC, que vence el viernes 23, y que no hace falta contestar
     (mecánica §9 y §10).
   - El mensaje no dice: la tarea de comunicaciones; que es urgente (sólo Dirección declara urgencias);
     ningún avance que nadie informó.
   - Botones: ninguno (decisión 9b).
   - Estado después: el último aviso enviado a Marcos es el de la tarea del PLC; no espera respuesta.

2. **Marcos** escribe (martes 20, 11:15): "arranque hoy a la mañana, ya estoy en eso"
   →
   - Jugadas: `anotar_inicio` sobre "Programar PLC de la comprimidora". La tarea sale del estado: Marcos
     contesta el aviso de esa tarea.
   - Efecto: la tarea pasa de `asignada` a `en_curso`, con un evento atribuido a Marcos, con fecha y
     auditoría.
   - Confirmación: ninguna; el inicio se anota directo (decisión 9a).
   - La respuesta dice: que quedó anotado que arrancó la tarea del PLC, nombrándola.
   - La respuesta no dice: que la tarea está terminada; nada de la tarea de comunicaciones; que la fecha
     cambió.
   - Botones: ninguno.
   - Estado después: sin tema abierto, nada para después.

3. **Leda** no le escribe a Marcos sobre la tarea del PLC el miércoles 21 ni el jueves 22.
   →
   - Efecto: ningún mensaje de esa tarea en el outbox esos días: el aviso previo es uno solo (decisión 9b).

4. **Leda**, por su cuenta, a Marcos (viernes 23, 10:00): el primer recordatorio, el día del vencimiento.
   Arrancar no detiene la escalera: sólo la detiene un bloqueo (mecánica §9).
   →
   - Efecto: un mensaje privado en el outbox; queda abierta la espera de su respuesta (`pending_reply`,
     decisión 9b).
   - El mensaje dice: que la tarea del PLC vence hoy, que está en curso desde el martes, y pide el estado.
   - El mensaje no dice: que no arrancó; que no contestó el aviso (no pedía respuesta); nada que pida
     arrancarla.
   - Botones: ninguno.

## Qué mide

- **Garantías (5b):** no inventa (no da la tarea por terminada ni la fecha por cambiada); no hace sin
  confirmación lo que la requiere (en este circuito nada la requiere, y no se pide ninguna); no deja sin
  salida (cada respuesta deja el próximo paso); no confunde la tarea (el inicio va a la del PLC, nunca a la
  de comunicaciones).
- **Falla de comprensión:** que la IA no reconozca "arranque" como un inicio. Tiene que ser una pregunta
  sobre qué quiso decir; anotar otra cosa (una previsión, una entrega) es una falla de garantía.
