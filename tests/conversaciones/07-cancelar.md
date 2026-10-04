# 07. "Dejá, no importa"

**Qué prueba:** Marcos empieza a contar un bloqueo, Leda le pregunta lo que falta y Marcos lo deja sin
efecto. No queda nada anotado, el tema se cierra y Leda no insiste. ADR 0018, decisión 4, situación
general 4, y la excepción de la decisión 9b: una pregunta para entender algo que la persona empezó se puede
dejar sin efecto.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (tres días hábiles después
    de D); `en_curso` desde el
    lunes 19; sin bloqueos ni dependencias.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; sin bloqueos ni dependencias.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada a Marcos en la semana.

## Hilo

1. **Leda**, por su cuenta, a Marcos (martes 20, 10:00): el aviso previo de la tarea del PLC.
   →
   - El mensaje dice: la tarea del PLC, que vence el viernes 23, que no hace falta contestar.
   - Botones: ninguno (decisión 9b).
   - Estado después: el último aviso enviado a Marcos es el de la tarea del PLC.

2. **Marcos** escribe (martes 20, 11:30): "estoy medio trabado con esto"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del PLC, sin causa.
   - Efecto: ninguno todavía. Sin causa no hay bloqueo (mecánica §3), así que no se anota nada.
   - La respuesta dice: una pregunta por lo único que falta, la causa (decisión 9c, paso 1).
   - La respuesta no dice: que el bloqueo quedó anotado; nada que suene a reproche.
   - Botones: ninguno; la causa es un dato libre.
   - Estado después: tema abierto: el bloqueo de la tarea del PLC, esperando la causa.

3. **Marcos** escribe (martes 20, 11:34): "dejá, no importa"
   →
   - Jugadas: `cancelar`, sobre el tema abierto.
   - Efecto: ninguno. No se anota un bloqueo; la tarea del PLC sigue `en_curso`; la escalera sigue igual.
   - La respuesta dice: que no quedó nada anotado; un próximo paso (que puede avisar si se traba).
   - La respuesta no dice: otra vez la pregunta por la causa; un juicio sobre la decisión. Leda no vuelve
     a preguntar por la causa más tarde (decisión 9b).
   - Estado después: sin tema abierto; nada para después (cancelar no es dejarlo para después).

4. **Leda**, por su cuenta, a Marcos (viernes 23, 10:00): el recordatorio del día del
   vencimiento de la tarea del PLC. Sigue, porque no se anotó ningún bloqueo.
   →
   - El mensaje dice: que la tarea del PLC vence hoy; pide el estado (decisión 9b).
   - El mensaje no dice: que Marcos está trabado; nada que retome el tema cancelado.

## Qué mide

- **Garantías (5b):** no inventa (ningún bloqueo sin causa ni cancelado aparece como hecho); no hace sin
  confirmación lo que la requiere (nada la requiere en este circuito, y no hay efecto); no deja sin salida (la respuesta del paso 3 deja el
  próximo paso); no confunde la tarea.
- **Falla de comprensión:** que la IA no tome "dejá, no importa" como cancelar. Tiene que preguntar si lo
  deja; anotar el bloqueo o seguir pidiendo la causa como si nada es una falla.
