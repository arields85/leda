# 08. Cambio de tema

**Qué prueba:** con una pregunta abierta sobre una tarea, Marcos habla de otra. Lo nuevo se puede anotar
directo: Leda lo anota y, en la misma respuesta, vuelve a la pregunta pendiente, sin ofrecer un menú de
salidas. Un tema a la vez, nunca dos preguntas juntas, sin perder nada. ADR 0018, decisión 4, situación
general 1, con la precisión de la decisión 9d.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (tres días hábiles después
    de D); `en_curso` desde el lunes 19; sin bloqueos ni dependencias.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `en_curso` desde el lunes 19; sin bloqueos ni dependencias; sin previsiones anotadas.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** nada a Marcos ni a Ismael en la semana.

## Hilo

1. **Leda**, por su cuenta, a Marcos (martes 20, 10:00): el aviso previo de la tarea del PLC.
   →
   - El mensaje dice: la tarea del PLC, que vence el viernes 23, que no hace falta contestar.
   - Botones: ninguno (decisión 9b).
   - Estado después: el último aviso enviado a Marcos es el de la tarea del PLC.

2. **Marcos** escribe (martes 20, 10:40): "uff con esto estoy trabado"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del PLC, sin causa.
   - Efecto: ninguno todavía (sin causa no hay bloqueo, mecánica §3).
   - La respuesta dice: una pregunta por la causa (decisión 9c, paso 1).
   - Estado después: tema abierto: el bloqueo de la tarea del PLC, esperando la causa.

3. **Marcos** escribe (martes 20, 10:43): "che y lo de comunicaciones no llego al 30, necesito hasta el
   miercoles 4"
   →
   - Jugadas: `anotar_prevision` sobre la tarea de comunicaciones, con fecha miércoles 4 de noviembre, sin
     motivo. No es la causa del bloqueo abierto: habla de otra tarea.
   - Efecto: la previsión, directo (decisión 9a), con la fecha comprometida en el viernes 30; un aviso a
     Ismael guardado como hechos. Ningún bloqueo anotado.
   - La respuesta dice, en una sola respuesta: que quedó anotada la previsión del miércoles 4 en la tarea
     de comunicaciones; y la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin
     pedirle que repita que está trabado (eso es retomarla, decisión 9d).
   - La respuesta no dice: un menú con las salidas (seguir, dejar para después, cancelar); otra pregunta
     además de la pendiente; nada que trate la fecha como la causa del bloqueo; que la tarea del PLC está
     bloqueada.
   - Botones: ninguno: no hay duda sobre de qué tarea habla.
   - Estado después: tema abierto, el mismo: el bloqueo de la tarea del PLC, esperando la causa.

4. **Leda**, por su cuenta, a Ismael (martes 20, enseguida, dentro del horario): el aviso de la nueva
   previsión.
   →
   - El mensaje dice: la tarea de comunicaciones; la previsión del miércoles 4, sin motivo porque Marcos no
     lo dio; la fecha comprometida, el viernes 30; el atraso, tres días hábiles, calculado por el código
     (decisión 9b).
   - El mensaje no dice: un motivo inventado; nada del bloqueo de la tarea del PLC, que todavía no se anotó.

5. **Marcos** escribe (martes 20, 10:46): "es que no me mandaron el programa del fabricante"
   →
   - Jugadas: la respuesta a la pregunta abierta: la causa del bloqueo de la tarea del PLC.
   - Efecto: el bloqueo abierto, con su causa; la tarea del PLC pasa a `bloqueada` y su escalera se detiene.
   - Lo que sigue es como en la conversación 03 (decisión 9c, corregida el 2026-10-05): Leda pregunta
     quién lo puede destrabar; propone salidas sólo si Marcos dice que nadie, que no sabe o que le toca a
     él; Ismael no recibe un aviso por el bloqueo.

## Qué mide

- **Garantías (5b):** no inventa (ni un bloqueo sin causa, ni una fecha cambiada, ni un motivo que Marcos no
  dio); no hace sin confirmación lo que la requiere (nada la requiere en este circuito); no deja sin salida
  (lo nuevo queda anotado y la pregunta pendiente vuelve, sin perder nada); no confunde la tarea (la
  previsión va a la de comunicaciones, nunca como causa del bloqueo de la del PLC).
- **Falla de comprensión:** que la IA no sepa si el mensaje del paso 3 contesta la pregunta abierta o
  cambia de tema. Tiene que preguntar; tomar "no llego" como la causa del bloqueo, o atender lo nuevo y
  olvidar lo abierto, es una falla.
