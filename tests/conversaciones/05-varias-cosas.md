# 05. Varias cosas en un mensaje

**Qué prueba:** Marcos contesta el aviso con dos hechos de dos tareas distintas que se anotan directo: Leda
anota los dos en una sola respuesta, sin perder ni cruzar ninguno. Después escribe uno que necesita una
pregunta junto a otro que no: Leda anota primero lo que se resuelve solo y pregunta una sola cosa. ADR 0018,
decisión 4, situación general 2, con la precisión de la decisión 9d.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (tres días hábiles después
    de D); `asignada`; sin bloqueos ni dependencias.
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

2. **Marcos** escribe (martes 20, 10:05): "arranque con el plc recien. y lo de las comunicaciones no llego
   al 30, va a ser el miercoles 4 xq espero el switch nuevo"
   →
   - Jugadas: dos. `anotar_inicio` sobre la tarea del PLC; `anotar_prevision` sobre la de comunicaciones,
     con fecha miércoles 4 de noviembre y motivo "espera el switch nuevo".
   - Efecto: las dos, directo y en este paso (decisiones 9a y 9d): la tarea del PLC en `en_curso`, con
     evento de Marcos; en la de comunicaciones, la previsión del miércoles 4 con su motivo, con la fecha
     comprometida en el viernes 30; un solo aviso a Ismael, sólo de la previsión. Auditoría de todo.
   - No se anota un bloqueo: esperar el switch con fecha es un atraso, no un "no puedo avanzar".
   - La respuesta dice, en una sola respuesta: los dos hechos anotados, cada uno con su tarea.
   - La respuesta no dice: que la fecha de la tarea de comunicaciones cambió; un inicio en la de
     comunicaciones o una previsión en la del PLC; que falta algo.
   - Estado después: sin tema abierto, nada para después.

3. **Leda**, por su cuenta, a Ismael (martes 20, 10:15, dentro del horario): el aviso de la nueva
   previsión, terminado el margen para corregir, diez minutos después de lo que dijo Marcos.
   →
   - El mensaje dice: la tarea de comunicaciones; la previsión del miércoles 4 y su motivo; la fecha
     comprometida, el viernes 30; el atraso, tres días hábiles, calculado por el código (decisión 9b).
     Ninguna tarea depende de ella en esta conversación, así que no nombra ninguna.
   - El mensaje no dice: nada de la tarea del PLC (un inicio no genera aviso); que la fecha cambió.

4. **Marcos** escribe (martes 20, 10:50): "me trabe con el plc. y lo de comunicaciones al final es el jueves
   5, no el 4"
   →
   - Jugadas: dos. `anotar_bloqueo` sobre la tarea del PLC, sin causa; `anotar_prevision` sobre la de
     comunicaciones, con fecha jueves 5 de noviembre (reemplaza la del 4; el motivo sigue siendo el switch).
   - Efecto: la previsión del jueves 5, directo, con el motivo del paso 2: Marcos lo dio hace menos de una
     hora, así que Leda no se lo vuelve a preguntar (usuario, 2026-10-07; pasada la hora, preguntaría qué
     la atrasa, ADR 0018, 9n); y un aviso nuevo a Ismael con ella (el atraso pasa a cuatro días hábiles;
     el del 4 ya salió). El bloqueo, todavía no: sin causa no hay bloqueo (mecánica §3).
   - La respuesta dice: primero, que quedó anotada la previsión del jueves 5; después, una sola pregunta:
     la causa del bloqueo de la tarea del PLC (decisión 9d; decisión 9c, paso 1).
   - La respuesta no dice: que el bloqueo quedó anotado; dos preguntas juntas.
   - Estado después: tema abierto: el bloqueo de la tarea del PLC, esperando la causa.

5. **Marcos** escribe (martes 20, 10:55): "falta que martin de IT me habilite el acceso a la red de planta"
   →
   - Jugadas: la respuesta a la pregunta abierta: la causa del bloqueo y, en el mismo mensaje, quién lo
     destraba (Martín, que Marcos nombra). La pregunta de quién lo destraba (9c, paso 2) queda contestada
     en el mismo turno.
   - Efecto: el bloqueo abierto en la tarea del PLC, con su causa y con Martín como quien lo destraba; la
     tarea pasa a `bloqueada` y su escalera se detiene. Ningún aviso a Ismael por el bloqueo (decisión 9c,
     paso 4). Como hay otra persona que lo destraba, Leda no propone salidas (9c, corregida el 2026-10-05).
   - La respuesta no dice: que Leda le escribió a Martín o lo va a seguir (eso es la prueba siguiente); la
     pregunta de quién lo destraba, que Marcos ya contestó.

## Qué mide

- **Garantías (5b):** no inventa (ninguna fecha comprometida cambia, el atraso es el del código y no hay
  bloqueo sin causa); no hace sin confirmación lo que la requiere (nada la requiere en este circuito); no deja
  sin salida (lo que falta se pregunta y nada se pierde); no confunde la tarea (el inicio y el bloqueo a la
  del PLC, la previsión a la de comunicaciones).
- **Falla de comprensión:** que la IA tome sólo uno de los dos hechos, o dude de cuál tarea es cada uno.
  Tiene que preguntar por lo que no entendió; perder uno de los dos sin decir nada no es una pregunta y
  cuenta como falla.
