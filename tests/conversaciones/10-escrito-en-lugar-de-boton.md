# 10. Escribir en lugar de tocar un botón

**Qué prueba:** lo que hace un botón vale igual escrito. Para elegir, siempre. Para confirmar, con la
guarda: lo confirmado es lo último que la persona vio y no cambió desde que se le mostró; si cambió, no
vale y Leda muestra lo nuevo. ADR 0018, decisión 4, situación general 6, y decisión 2.

**Supuesto:** la segunda parte (pasos 3 a 7) necesita una confirmación dentro del circuito. Se escribe
sobre la nueva previsión, como si P3 la pidiera. PENDIENTE (P3): si P3 = a y tampoco P1 ni P2 piden
confirmación, el recordatorio no tiene confirmaciones y esa parte se prueba en el primer circuito que las
tenga.

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 30; `asignada`; sin bloqueos
    ni dependencias.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 23
    (D+1); `asignada`; sin bloqueos ni dependencias; sin previsiones anotadas.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** nada a Marcos en el día.

## Hilo

1. **Marcos** escribe (jueves 22, 09:30): "arranque una de las de la comprimidora"
   →
   - Jugadas: `anotar_inicio`, sin tarea: las dos son "de la comprimidora" y las dos se pueden arrancar.
   - Efecto: ninguno.
   - La respuesta dice: una pregunta por cuál de las dos.
   - Botones: las dos tareas (constitución §8: algo con más de una lectura).
   - Estado después: tema abierto: el inicio, esperando la elección.

2. **Marcos** escribe, sin tocar ningún botón: "la del plc"
   →
   - Jugadas: `elegir`, la tarea del PLC. Vale igual que tocar el botón.
   - Efecto: la tarea del PLC pasa a `en_curso` (o se muestra su vista previa y Marcos la confirma
     escribiendo, con la misma guarda; P1).
   - La respuesta dice: que quedó anotado el inicio de la tarea del PLC.
   - Estado después: sin tema abierto, nada mostrado para confirmar.

3. **Marcos** escribe (jueves 22, 11:10): "lo de comunicaciones va a ser para el martes 27, me falta un
   modulo que no llego"
   →
   - Jugadas: `anotar_prevision` sobre la tarea de comunicaciones, martes 27, motivo "falta un módulo que
     no llegó".
   - Efecto: ninguno todavía; se muestra la vista previa (supuesto P3), con su huella.
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

## Qué mide

- **Garantías (5b):** no inventa (no anota una previsión que la guarda rechazó); no hace sin confirmación
  lo que la requiere: el "ok" del paso 5 vale sólo para la previsión del 28 y el "dale" del paso 8 no vale;
  no deja sin salida (el paso 8 explica qué pasó); no confunde la tarea.
- **Falla de comprensión:** que la IA dude de si "la del plc", "ok" o "dale" son una elección o una
  confirmación. Tiene que preguntar; confirmar algo que no es lo último que Marcos vio es una falla de
  garantía.
