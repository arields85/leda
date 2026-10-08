# 11. Algo vencido

**Qué prueba:** dos cosas que quedaron atrás: un botón de una pregunta ya contestada y un aviso guardado que
dejó de corresponder antes de salir. En las dos, Leda no hace el efecto viejo, nunca lo descarta en
silencio y deja una salida. En el medio, Marcos escribe fuera del horario: Leda le contesta enseguida y el
aviso a Ismael espera al horario. ADR 0018, decisión 4, situación general 7 (hallazgos C-1 a C-3), y
decisiones 9b (aviso guardado) y 9e (horario). La vista previa reemplazada, que necesita un circuito que
confirma, queda abajo, en "Para la prueba de la entrega".

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 30; `en_curso` desde ayer,
    miércoles 21; sin bloqueos ni dependencias; sin previsiones anotadas.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; sin bloqueos ni dependencias; sin previsiones anotadas.
    Criterio de aceptación: "Los equipos de la comprimidora se comunican con el PLC por la red de planta
    sin errores durante una hora".
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** ayer, miércoles 21, Marcos escribió que arrancó una de las dos; Leda le preguntó cuál, con
  las dos tareas como botones; Marcos contestó escribiendo "la del plc" y el inicio quedó anotado. La
  pregunta de ayer sigue en el chat con sus dos botones. Si el motor quita los botones viejos al contestarse
  (pieza de la rama congelada, migración `0028`), el paso 1 se prueba con un toque que llega antes de que se
  quiten. El aviso previo de las dos tareas sale recién el martes 27.

## Hilo

1. **Marcos** toca (jueves 22, 09:15) el botón de ayer "Revisar comunicaciones industriales de la
   comprimidora".
   →
   - Jugadas: ninguna nueva: es un toque de una pregunta ya contestada.
   - Efecto: ninguno sobre las tareas; el toque recibe su señal y queda en el registro de turnos como la
     opción elegida (ADR 0018, decisión 3).
   - La respuesta dice: que esa pregunta ya se contestó ayer con la tarea del PLC, que no se cambió nada, y
     el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones.
   - La respuesta no dice: que arrancó la de comunicaciones; nada técnico sobre botones (constitución §10).
   - Estado después: sin tema abierto.

2. **Marcos** escribe: "ah no, era para decirte q esa tambien la arranque hoy"
   →
   - Jugadas: `anotar_inicio` sobre la tarea de comunicaciones ("esa": la del botón que acaba de tocar).
   - Efecto: la de comunicaciones pasa a `en_curso`, directo (decisión 9a), con evento de Marcos.
   - La respuesta dice: que quedó anotado el inicio de la tarea de comunicaciones.
   - Estado después: sin tema abierto.

3. **Marcos** escribe (jueves 22, 17:20, fuera del horario): "y lo de comunicaciones se me va al 4, espero
   el switch"
   →
   - Jugadas: `anotar_prevision` sobre la tarea de comunicaciones, miércoles 4 de noviembre, con su motivo.
   - Efecto: la previsión, directo, con la fecha comprometida en el viernes 30. El aviso a Ismael queda
     guardado como hechos y no sale hasta el viernes 23 a las 10:00, la hora en que salen los mensajes que
     Leda manda por su cuenta (README, "Datos ficticios"): es un mensaje a otra persona y Leda no lo manda
     fuera del horario (decisión 9e).
   - La respuesta, enseguida, aunque sea fuera del horario (decisión 9e): dice que quedó anotada la
     previsión del 4 y que queda informada el viernes a las 10:00, sin nombrar a Ismael.
   - La respuesta no dice: que Ismael ya se enteró.
   - Estado después: sin tema abierto.

4. **Marcos** escribe (viernes 23, 08:30, antes del horario): "olvidate lo del 4, llego el switch, la termino
   para el 30"
   →
   - Jugadas: `anotar_prevision` sobre la tarea de comunicaciones, con la fecha comprometida (viernes 30):
     reemplaza la del 4.
   - Efecto: la previsión vigente es el 30; la del 4 queda en la historia, sin efecto. El aviso guardado
     del 4 sigue sin salir.
   - La respuesta, enseguida (decisión 9e): dice que la previsión del 4 quedó sin efecto y que la vigente es
     el viernes 30.
   - La respuesta no dice: que Ismael se enteró de lo del 4.
   - Estado después: sin tema abierto.

5. **Leda**, al llegar las 10:00 del viernes 23, va a mandar el aviso guardado a Ismael.
   →
   - Efecto: el código vuelve a leer la tarea (decisión 9b). La previsión del 4 ya no existe, así que el
     aviso ya no corresponde: no sale, y la omisión y su motivo quedan registrados (mecánica §12: nunca en
     silencio). Nunca sale un aviso que diga que Marcos llega el 4.
   - Tampoco sale un aviso de que la previsión volvió al viernes 30: para Ismael, que nunca recibió el del
     4, no cambió nada (decisión 9b). La historia guarda la previsión del 4, su corrección y el aviso que no
     salió, con su motivo.
   - Estado de Ismael después: sin tema abierto; ningún mensaje en el outbox para él.

## Qué mide

- **Garantías (5b):** no inventa (ni el inicio del botón viejo, ni un aviso del 4 que ya no vale); no hace
  sin confirmación lo que la requiere (el botón viejo no hace nada, y nada requiere confirmación en este
  circuito); no deja sin salida (el paso 1 dice qué pasó y qué sigue, y las respuestas fuera de horario
  dicen cuándo se entera Ismael); no confunde la tarea ("esa" es la de comunicaciones).
- **Falla de comprensión:** que la IA no sepa a qué se refiere "esa" en el paso 2 o qué deja sin efecto
  "olvidate lo del 4" en el paso 4. Tiene que preguntar; tocar otra tarea o dejar viva la previsión del 4
  es una falla de garantía.

## Para la prueba de la entrega

No corre en la prueba chica: la previsión se anota directo (decisión 9a) y el recordatorio no muestra
vistas previas. Al escribir la conversación de la entrega, estos pasos se pasan a la entrega. Supuestos de
esta parte: la tarea del PLC vence el viernes 23 y lo que se muestra lleva confirmación.

6. **Marcos** escribe (jueves 22, 11:00): "lo del plc se me va al 27, no me llegan los modulos"
   →
   - Jugadas: `anotar_prevision` sobre la tarea del PLC, martes 27, con su motivo.
   - Efecto: se muestra la vista previa del 27, con su huella y los botones de la confirmación.

7. **Marcos** escribe: "no mejor el 28"
   →
   - Jugadas: `corregir`, la fecha pasa al miércoles 28.
   - Efecto: la vista previa del 27 deja de valer; se muestra la del 28, con sus botones.

8. **Marcos** toca "Confirmar" en la vista previa del 27, la vieja.
   →
   - Jugadas: ninguna nueva: el botón es de una vista previa reemplazada.
   - Efecto: ninguno. No se anota el 27 ni el 28; el toque recibe su señal y queda registrado.
   - La respuesta dice: que esa vista previa fue reemplazada por la del 28, que sigue esperando
     confirmación.
   - Estado después: lo último mostrado para confirmar, la previsión del 28.

9. **Marcos** toca "Confirmar" en la vista previa del 28.
   →
   - Efecto: la previsión del 28 anotada; el aviso a Ismael guardado y enviado dentro del horario.

Qué mide esta parte: el botón de una vista previa reemplazada no confirma nada y Leda lo dice.
