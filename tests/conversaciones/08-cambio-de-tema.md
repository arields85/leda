# 08. Cambio de tema

**Qué prueba:** con una pregunta abierta sobre una tarea, Marcos habla de otra. Lo nuevo se puede anotar
directo: Leda lo anota y, en otro mensaje justo después, vuelve a la pregunta pendiente, sin ofrecer un
menú de salidas. Un mensaje, un tema; nunca dos preguntas juntas, sin perder nada. ADR 0018, decisión 4,
situación general 1, con la precisión de la decisión 9d y la decisión 50 del usuario (2026-10-09, opción
A: la pregunta que quedó por un cambio de tema vuelve en un mensaje aparte; hasta entonces volvía en la
misma respuesta).

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (tres días hábiles después
    de D); `en_curso` desde el lunes 19; sin bloqueos ni dependencias.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `en_curso` desde el lunes 19; sin bloqueos ni dependencias; sin previsiones anotadas.
    Criterio de aceptación: "Los equipos de la comprimidora se comunican con el PLC por la red de planta
    sin errores durante una hora".
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

3. **Marcos** escribe (martes 20, 10:43): "che y lo de comunicaciones no llego al 30 porque esta semana me
   mandaron a otra obra, necesito hasta el miercoles 4"
   →
   - Jugadas: `anotar_prevision` sobre la tarea de comunicaciones, con fecha miércoles 4 de noviembre y su
     motivo, con las palabras de Marcos. No es la causa del bloqueo abierto: habla de otra tarea. (Trae su
     porqué desde el 2026-10-07: una fecha que atrasa sin él abre la pregunta de qué la atrasa, que iría
     primero, ADR 0018, 9n y 9d; acá se prueba la vuelta a la pregunta pendiente.)
   - Efecto: la previsión, directo (decisión 9a), con la fecha comprometida en el viernes 30 y su motivo;
     un aviso a Ismael guardado como hechos. Ningún bloqueo anotado. La pregunta pendiente, guardada
     para salir enseguida, aparte (paso 4; decisión 50).
   - La respuesta dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones, con
     su motivo. Sólo eso: un mensaje, un tema.
   - La respuesta no dice: la pregunta pendiente (la trae el código aparte, paso 4); un menú con las
     salidas (seguir, dejar para después, cancelar); nada que trate la fecha o su motivo como la causa del
     bloqueo; que la tarea del PLC está bloqueada.
   - Botones: ninguno: no hay duda sobre de qué tarea habla.
   - Estado después: tema abierto, el mismo: el bloqueo de la tarea del PLC, esperando la causa.

4. **Leda**, a Marcos (martes 20, 10:44), en otro mensaje justo después de la respuesta, aunque Marcos
   acaba de escribir: la vuelta a la pregunta pendiente.
   →
   - El mensaje dice: la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
     (eso es retomarla, decisión 9d).
   - El mensaje no dice: nada de la tarea de comunicaciones, que ya se contestó; un menú con las salidas;
     otra pregunta además de la pendiente.
   - Estado después: tema abierto, el mismo: el bloqueo de la tarea del PLC, esperando la causa.

5. **Leda**, por su cuenta, a Ismael (martes 20, 10:53, dentro del horario): el aviso de la nueva
   previsión, terminado el margen para corregir, diez minutos después de lo que dijo Marcos.
   →
   - El mensaje dice: la tarea de comunicaciones; la previsión del miércoles 4 y su motivo, con las palabras
     de Marcos; la fecha comprometida, el viernes 30; el atraso, tres días hábiles, calculado por el código
     (decisión 9b).
   - El mensaje no dice: otro motivo que el que dio Marcos; nada del bloqueo de la tarea del PLC, que
     todavía no se anotó.

6. **Marcos** escribe (martes 20, 10:55): "es que no me mandaron el programa del fabricante"
   →
   - Jugadas: la respuesta a la pregunta abierta: la causa del bloqueo de la tarea del PLC.
   - Efecto: el bloqueo abierto, con su causa; la tarea del PLC pasa a `bloqueada` y su escalera se detiene.
   - Lo que sigue es como en la conversación 03 (decisión 9c, corregida el 2026-10-05): Leda pregunta
     quién lo puede destrabar; propone salidas sólo si Marcos dice que nadie, que no sabe o que le toca a
     él; Ismael no recibe un aviso por el bloqueo.

## Qué mide

- **Garantías (5b):** no inventa (ni un bloqueo sin causa, ni una fecha cambiada, ni otro motivo que el que
  dio Marcos); no hace sin confirmación lo que la requiere (nada la requiere en este circuito); no deja sin
  salida (lo nuevo queda anotado y la pregunta pendiente vuelve aparte, sin perder nada); no confunde la tarea (la
  previsión y su motivo van a la de comunicaciones, nunca como causa del bloqueo de la del PLC).
- **Falla de comprensión:** que la IA no sepa si el mensaje del paso 3 contesta la pregunta abierta o
  cambia de tema. Tiene que preguntar; tomar "no llego" como la causa del bloqueo, o atender lo nuevo y
  olvidar lo abierto, es una falla.
