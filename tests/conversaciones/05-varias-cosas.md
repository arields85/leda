# 05. Varias cosas en un mensaje

**Qué prueba:** Marcos contesta el aviso con dos hechos de dos tareas distintas. Leda atiende uno, deja el
otro anotado para enseguida, no pierde ninguno y no los cruza. ADR 0018, decisión 4, situación general 2.

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (D+1); `asignada`; sin
    bloqueos ni dependencias.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `en_curso` desde el lunes 19; sin bloqueos ni dependencias; sin previsiones anotadas.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** nada a Marcos ni a Ismael en el día.

## Hilo

1. **Leda**, por su cuenta, a Marcos (jueves 22, dentro del horario): el aviso del día hábil anterior al
   vencimiento de la tarea del PLC.
   →
   - El mensaje dice: la tarea del PLC, que vence mañana, que no hace falta contestar.
   - Botones: PENDIENTE (P4).
   - Estado después: el último aviso enviado a Marcos es el de la tarea del PLC.

2. **Marcos** escribe (jueves 22, 10:05): "arranque con el plc recien. y lo de las comunicaciones no llego
   al 30, va a ser el miercoles 4 xq espero el switch nuevo"
   →
   - Jugadas: dos. `anotar_inicio` sobre la tarea del PLC; `anotar_prevision` sobre la de comunicaciones,
     con fecha miércoles 4 de noviembre y motivo "espera el switch nuevo".
   - Efecto al terminar el paso: una de las dos atendida (hecha, o mostrada para confirmar según P1 o P3);
     la otra guardada en los temas para después de Marcos, con su tarea, su fecha y su motivo, para que
     Marcos no tenga que repetirlos. PENDIENTE (P5): ¿cuál va primero, y la segunda va en la misma
     respuesta si la primera no pide nada?
   - No se anota un bloqueo: esperar el switch con fecha es un atraso, no un "no puedo avanzar".
   - La respuesta dice: lo que se hizo o se muestra para confirmar, y que lo otro sigue enseguida.
   - La respuesta no dice: que la fecha de la tarea de comunicaciones cambió; un inicio en la de
     comunicaciones o una previsión en la del PLC.
   - Estado después: un tema abierto (el que se atiende) y uno para después, o ninguno si P5 resuelve que
     las dos van juntas sin confirmación.

3. **Marcos** escribe "dale" `[sólo si P1 o P3 piden confirmación; una vez por cada vista previa]`.
   →
   - Jugadas: `confirmar`. Vale para lo último que Marcos vio, sin cambios (decisión 2); nunca para las
     dos a la vez si se le mostró una sola.
   - Efecto: el de lo confirmado. Si quedaba la otra, Leda sigue con ella desde los temas para después, sin
     pedirle a Marcos los datos de nuevo.

4. **Al terminar las dos**, sin que Marcos escriba nada más que las confirmaciones que pidan P1 y P3.
   →
   - Efecto: la tarea del PLC en `en_curso`, con evento de Marcos; en la de comunicaciones, la previsión
     del miércoles 4 con su motivo, con la fecha comprometida en el viernes 30; un solo aviso a Ismael, sólo
     de la previsión de la tarea de comunicaciones (P6 para su contenido). Auditoría de todo.
   - Estado después: sin tema abierto, nada para después, nada mostrado para confirmar.

## Qué mide

- **Garantías (5b):** no inventa (ninguna fecha cambia); no hace sin confirmación lo que la requiere (P1,
  P3); no deja sin salida (lo pendiente se dice y se retoma); no confunde la tarea (el inicio a la del PLC,
  la previsión a la de comunicaciones).
- **Falla de comprensión:** que la IA tome sólo uno de los dos hechos, o dude de cuál tarea es cada uno.
  Tiene que preguntar por lo que no entendió; perder uno de los dos sin decir nada no es una pregunta y
  cuenta como falla.
