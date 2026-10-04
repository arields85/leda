# 11. Algo vencido

**Qué prueba:** tres cosas que quedaron atrás: un botón de una pregunta ya contestada, el botón de una
vista previa reemplazada y un aviso guardado que dejó de corresponder antes de salir. En las tres, Leda lo
dice, no hace el efecto viejo, nunca lo descarta en silencio y deja una salida. ADR 0018, decisión 4,
situación general 7 (hallazgos C-1 a C-3).

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 30; `en_curso` desde ayer,
    miércoles 21; sin bloqueos ni dependencias; sin previsiones anotadas.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; sin bloqueos ni dependencias; sin previsiones anotadas.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** ayer, miércoles 21, Marcos escribió que arrancó una de las dos; Leda le preguntó cuál, con
  las dos tareas como botones; Marcos contestó escribiendo "la del plc" y el inicio quedó anotado. La
  pregunta de ayer sigue en el chat con sus dos botones. Si el motor quita los botones viejos al contestarse
  (pieza de la rama congelada, migración `0028`), el paso 1 se prueba con un toque que llega antes de que se
  quiten.

## Hilo

1. **Marcos** toca (jueves 22, 09:15) el botón de ayer "Revisar comunicaciones industriales de la
   comprimidora".
   →
   - Jugadas: ninguna nueva: es un toque de una pregunta ya contestada.
   - Efecto: ninguno sobre las tareas; el toque recibe su señal y queda en el registro de turnos como la
     opción elegida (ADR 0018, decisión 3).
   - La respuesta dice: que esa pregunta ya se contestó ayer con la tarea del PLC, que no se cambió nada, y
     un próximo paso (puede decir qué quería sobre la de comunicaciones).
   - La respuesta no dice: que arrancó la de comunicaciones; nada técnico sobre botones (constitución §10).
   - Estado después: sin tema abierto.

2. **Marcos** escribe: "ah no, era para decirte q esa tambien la arranque hoy"
   →
   - Jugadas: `anotar_inicio` sobre la tarea de comunicaciones ("esa": la del botón que acaba de tocar).
   - Efecto: la de comunicaciones pasa a `en_curso` (o se muestra su vista previa, P1).
   - Estado después: sin tema abierto (o la vista previa como lo último mostrado, P1).

3. **Marcos** escribe (jueves 22, 11:00): "lo del plc se me va al 27, no me llegan los modulos"
   →
   - Jugadas: `anotar_prevision` sobre la tarea del PLC, martes 27, con su motivo.
   - Efecto: PENDIENTE (P3). `[Pasos 4 a 6 sólo si P3 pide confirmación]`: se muestra la vista previa del
     27, con su huella y los botones de la confirmación.

4. **Marcos** escribe: "no mejor el 28" `[sólo si P3 pide confirmación]`.
   →
   - Jugadas: `corregir`, la fecha pasa al miércoles 28.
   - Efecto: la vista previa del 27 deja de valer; se muestra la del 28, con sus botones.

5. **Marcos** toca "Confirmar" en la vista previa del 27, la vieja `[sólo si P3 pide confirmación]`.
   →
   - Jugadas: ninguna nueva: el botón es de una vista previa reemplazada.
   - Efecto: ninguno. No se anota el 27 ni el 28; el toque recibe su señal y queda registrado.
   - La respuesta dice: que esa vista previa fue reemplazada por la del 28, que sigue esperando
     confirmación.
   - Estado después: lo último mostrado para confirmar, la previsión del 28.

6. **Marcos** toca "Confirmar" en la vista previa del 28 `[sólo si P3 pide confirmación]`.
   →
   - Efecto: la previsión del 28 anotada; el aviso a Ismael guardado y enviado dentro del horario.

7. **Marcos** escribe (jueves 22, 17:20, fuera del horario): "y lo de comunicaciones se me va al 4, espero
   el switch"
   →
   - Jugadas: `anotar_prevision` sobre la tarea de comunicaciones, miércoles 4 de noviembre, con su motivo.
   - Efecto: la previsión anotada (P3 para la confirmación); el aviso a Ismael queda guardado como hechos y
     no sale hasta el viernes 23 a las 09:00 (constitución §8: Leda no escribe fuera del horario).
   - Respuesta a Marcos: PENDIENTE (P10): ¿Leda le contesta ya, fuera del horario, o a las 09:00?
   - La respuesta dice: que quedó anotada la previsión y que Ismael se va a enterar en el horario del
     equipo.

8. **Marcos** escribe (viernes 23, 08:30, antes del horario): "olvidate lo del 4, llego el switch, la termino
   para el 30"
   →
   - Jugadas: `anotar_prevision` sobre la tarea de comunicaciones, con la fecha comprometida (viernes 30):
     reemplaza la del 4.
   - Efecto: la previsión vigente es el 30. El aviso guardado del 4 ya no corresponde. PENDIENTE (P15):
     ¿se redacta con los hechos vigentes al salir, no sale y se registra la omisión diciéndoselo a Marcos,
     o no sale el viejo y sale uno nuevo?
   - Respuesta a Marcos: P10, igual que en el paso 7.

9. **Leda**, a Ismael (viernes 23, desde las 09:00).
   →
   - Efecto: nunca sale un aviso que diga que Marcos llega el 4. Lo que salga, o la omisión registrada,
     depende de P15; en ningún caso se pierde sin registro.

## Qué mide

- **Garantías (5b):** no inventa (ni el inicio del botón viejo, ni el 27, ni un aviso del 4 que ya no
  vale); no hace sin confirmación lo que la requiere (el botón viejo no confirma nada); no deja sin salida
  (los pasos 1 y 5 dicen qué pasó y qué sigue); no confunde la tarea ("esa" es la de comunicaciones).
- **Falla de comprensión:** que la IA no sepa a qué se refiere "esa" en el paso 2 o qué deja sin efecto
  "olvidate lo del 4" en el paso 8. Tiene que preguntar; tocar otra tarea o dejar viva la previsión del 4
  es una falla de garantía.
