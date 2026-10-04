# 01. "Arranqué"

**Qué prueba:** Leda avisa que mañana vence una tarea, Marcos contesta que arrancó y Leda anota el inicio
en esa tarea. ADR 0018, decisión 5a, primera respuesta.

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (D+1); `asignada`; sin
    bloqueos ni dependencias.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; sin bloqueos ni dependencias.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada a Marcos en el día.

## Hilo

1. **Leda**, por su cuenta, a Marcos (jueves 22, dentro del horario): el aviso del día hábil anterior al
   vencimiento (mecánica §9).
   →
   - Jugadas: ninguna; el mensaje lo inicia Leda. El código guarda los hechos y la IA lo redacta justo
     antes de enviarlo (ADR 0018, decisión 8).
   - Efecto: un mensaje privado en el outbox para Marcos y su turno en el registro.
   - El mensaje dice: el título de la tarea del PLC, que vence mañana, y que no hace falta contestar
     (mecánica §9 y §10).
   - El mensaje no dice: la tarea de comunicaciones; que es urgente (sólo Dirección declara urgencias);
     ningún avance que nadie informó.
   - Botones: PENDIENTE (P4): ¿el aviso lleva botones?
   - Estado después: el último aviso enviado a Marcos es el de la tarea del PLC; no espera respuesta.

2. **Marcos** escribe (jueves 22, 11:15): "arranque hoy a la mañana, ya estoy en eso"
   →
   - Jugadas: `anotar_inicio` sobre "Programar PLC de la comprimidora". La tarea sale del estado: Marcos
     contesta el aviso de esa tarea.
   - Efecto: la tarea pasa de `asignada` a `en_curso`, con un evento atribuido a Marcos, con fecha y
     auditoría.
   - Confirmación: PENDIENTE (P1): ¿anotar el inicio lleva vista previa y confirmación? Hasta decidirlo,
     vale una de dos: el inicio queda anotado en este paso, o queda mostrada su vista previa y se anota en
     el paso 3.
   - La respuesta dice: que quedó anotado que arrancó la tarea del PLC (o, con P1 = b, qué se va a anotar).
   - La respuesta no dice: que la tarea está terminada; nada de la tarea de comunicaciones; que la fecha
     cambió.
   - Botones: ninguno, salvo los de la confirmación si P1 = b.
   - Estado después: sin tema abierto, nada para después.

3. **Marcos** toca "Confirmar" `[sólo si P1 = b]`.
   →
   - Jugadas: `confirmar`. El código comprueba la guarda: es lo último que Marcos vio y no cambió.
   - Efecto: el del paso 2, una sola vez; el toque recibe su señal y tocarlo de nuevo no repite el efecto
     (ADR 0013, regla 4).
   - La respuesta dice: que quedó anotado el inicio.
   - Estado después: sin tema abierto, nada mostrado para confirmar.

4. **Leda**, por su cuenta, a Marcos (viernes 23, dentro del horario): el primer recordatorio, el día del
   vencimiento. Arrancar no detiene la escalera: sólo la detiene un bloqueo (mecánica §9).
   →
   - Efecto: un mensaje privado en el outbox.
   - El mensaje dice: que la tarea del PLC vence hoy y que está en curso desde ayer.
   - El mensaje no dice: que no arrancó; que no contestó; nada que pida arrancarla.

## Qué mide

- **Garantías (5b):** no inventa (no da la tarea por terminada ni la fecha por cambiada); no hace sin
  confirmación lo que la requiere (P1); no deja sin salida (cada respuesta deja el próximo paso); no
  confunde la tarea (el inicio va a la del PLC, nunca a la de comunicaciones).
- **Falla de comprensión:** que la IA no reconozca "arranque" como un inicio. Tiene que ser una pregunta
  sobre qué quiso decir; anotar otra cosa (una previsión, una entrega) es una falla de garantía.
