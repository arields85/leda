# 10. Escribir en lugar de tocar un botón

**Qué prueba:** lo que hace un botón vale igual escrito. En la prueba chica, los únicos botones son las
tareas como opciones de una duda (decisiones 9b y 9d): elegir escribiendo vale siempre. Confirmar
escribiendo, con la guarda de la decisión 2, se prueba con el primer circuito que confirma, la entrega
(decisión 9a); sus pasos quedan abajo, en "Para la prueba de la entrega". ADR 0018, decisión 4, situación
general 6.

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 30; `asignada`; sin bloqueos
    ni dependencias.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; sin bloqueos ni dependencias; sin previsiones anotadas.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada a Marcos en la semana (el aviso previo de las dos sale el martes 27).

## Hilo

1. **Marcos** escribe (jueves 22, 09:30): "arranque una de las de la comprimidora"
   →
   - Jugadas: `anotar_inicio`, sin tarea: las dos son "de la comprimidora" y las dos se pueden arrancar.
   - Efecto: ninguno.
   - La respuesta dice: una pregunta por cuál de las dos.
   - Botones: las dos tareas (constitución §8: algo con más de una lectura; situación general 5).
   - Estado después: tema abierto: el inicio, esperando la elección.

2. **Marcos** escribe, sin tocar ningún botón: "la del plc"
   →
   - Jugadas: `elegir`, la tarea del PLC. Vale igual que tocar el botón.
   - Efecto: la tarea del PLC pasa a `en_curso`, directo (decisión 9a), con evento de Marcos y auditoría; la
     de comunicaciones sigue `asignada`.
   - La respuesta dice: que quedó anotado el inicio de la tarea del PLC.
   - Estado después: sin tema abierto; los botones de la pregunta ya contestada quedan viejos (si se tocan,
     es la conversación 11).

## Qué mide

- **Garantías (5b):** no inventa; no hace sin confirmación lo que la requiere (nada la requiere en este
  circuito); no deja sin salida (la pregunta trae las opciones); no confunde la tarea ("la del plc" es la
  del PLC, nunca la de comunicaciones).
- **Falla de comprensión:** que la IA no tome "la del plc" como la elección. Tiene que volver a preguntar;
  elegir la otra tarea es una falla de garantía.

## Para la prueba de la entrega

No corre en la prueba chica. Se escribió sobre la nueva previsión, cuando todavía se pensaba que llevaba
confirmación; la previsión se anota directo (decisión 9a), así que al escribir la conversación de la
entrega estos pasos se pasan a la entrega con su evidencia: mostrar, corregir, confirmar escribiendo y un
cambio en el medio que hace fallar la guarda. Supuestos de esta parte: la tarea de comunicaciones vence el
viernes 23 y lo que se muestra lleva confirmación.

3. **Marcos** escribe (jueves 22, 11:10): "lo de comunicaciones va a ser para el martes 27, me falta un
   modulo que no llego"
   →
   - Jugadas: `anotar_prevision` sobre la tarea de comunicaciones, martes 27, motivo "falta un módulo que
     no llegó".
   - Efecto: ninguno todavía; se muestra la vista previa (supuesto de esta parte), con su huella.
   - Botones: los de la confirmación (constitución §7).
   - Estado después: lo último mostrado para confirmar: la previsión del martes 27.

4. **Marcos** escribe: "mm no, poné el 28 mejor por las dudas"
   →
   - Jugadas: `corregir`, la fecha pasa al miércoles 28.
   - Efecto: la vista previa del 27 deja de valer; se muestra la del 28, con huella nueva.
   - Estado después: lo último mostrado para confirmar: la previsión del miércoles 28.

5. **Marcos** escribe, sin tocar el botón: "ok"
   →
   - Jugadas: `confirmar`. El código comprueba la guarda: lo último que Marcos vio es la previsión del 28 y
     no cambió.
   - Efecto: se anota la previsión del miércoles 28 con su motivo, nunca la del 27; el aviso a Ismael se
     guarda; la fecha comprometida sigue en el viernes 23.
   - La respuesta dice: que quedó anotada la previsión del 28.
   - Estado después: nada mostrado para confirmar.

6. **Marcos** escribe (jueves 22, 14:00): "y la del plc capaz que tambien se corre, ponele el 3"
   →
   - Jugadas: `anotar_prevision` sobre la tarea del PLC, martes 3 de noviembre, sin motivo.
   - Efecto: ninguno todavía; se muestra la vista previa, con su huella.
   - Estado después: lo último mostrado para confirmar: la previsión del PLC para el martes 3.

7. **El administrador**, fuera del chat (jueves 22, 14:02), cancela la tarea del PLC, con su motivo. En la
   prueba, el arnés hace el cambio en la base con su evento y su auditoría; cómo lo hará la plataforma es de
   su ADR.
   →
   - Efecto: la vista previa del paso 6 ya no corresponde a lo que hay en la base.

8. **Marcos** escribe: "dale"
   →
   - Jugadas: `confirmar`. La guarda falla: lo que vio cambió.
   - Efecto: ninguno. No se anota la previsión.
   - La respuesta dice: que la tarea del PLC cambió desde que se le mostró (está cancelada) y que por eso no
     se anotó nada.
   - La respuesta no dice: que la previsión quedó anotada; detalles técnicos de la huella (constitución
     §10).
   - Estado después: nada mostrado para confirmar; la vista previa vieja, descartada y registrada.

Qué mide esta parte: el "ok" del paso 5 vale sólo para lo último mostrado y el "dale" del paso 8 no vale;
confirmar algo que no es lo último que la persona vio, o que cambió, es una falla de garantía.
