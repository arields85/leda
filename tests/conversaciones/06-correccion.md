# 06. "No, era la otra tarea"

**Qué prueba:** Leda toma "ya arranqué" para la tarea del aviso, que es lo correcto según el estado, y
Marcos corrige: era la otra. El inicio queda en la tarea correcta y la equivocada vuelve a como estaba, con
todo auditado. ADR 0018, decisión 4, situación general 3.

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (D+1); `asignada`; sin
    bloqueos.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; sin bloqueos. En esta conversación no hay dependencia entre las dos (la de la semilla no
    se carga), para que arrancar la de comunicaciones sea posible.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada a Marcos en el día.

## Hilo

1. **Leda**, por su cuenta, a Marcos (jueves 22, dentro del horario): el aviso del día hábil anterior al
   vencimiento de la tarea del PLC.
   →
   - El mensaje dice: la tarea del PLC, que vence mañana, que no hace falta contestar.
   - Botones: PENDIENTE (P4).
   - Estado después: el último aviso enviado a Marcos es el de la tarea del PLC.

2. **Marcos** escribe (jueves 22, 09:50): "ya arranque esta mañana 👍"
   →
   - Jugadas: `anotar_inicio` sobre la tarea del PLC (contesta su aviso).
   - Efecto: la tarea del PLC pasa a `en_curso`, o queda mostrada la vista previa del inicio. PENDIENTE
     (P1).
   - La respuesta dice: que se anotó (o se va a anotar) el inicio de la tarea del PLC, nombrándola, para
     que Marcos pueda ver si es la que quería.
   - Estado después: sin tema abierto (o, con P1 = b, la vista previa del inicio de la tarea del PLC como
     lo último mostrado para confirmar).

3. **Marcos** escribe (jueves 22, 09:52): "nono era la otra, la de las comunicaciones. la del plc todavia
   no la empece"
   →
   - Jugadas: `corregir`: el inicio era de la tarea de comunicaciones, no de la del PLC.
   - Efecto: la tarea de comunicaciones pasa a `en_curso` (o se muestra su vista previa, P1). La del PLC
     queda `asignada`. PENDIENTE (P11): ¿cómo se deshace un inicio ya anotado? Con P1 = b no hay nada que
     deshacer: la vista previa de la del PLC se reemplaza y deja de valer. En cualquier caso la auditoría
     guarda lo original y la corrección (constitución §12: no se edita ni se borra).
   - La respuesta dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar.
   - La respuesta no dice: que las dos están en curso; nada que reproche el error.
   - Estado después: sin tema abierto (o, con P1 = b, la vista previa del inicio de la tarea de
     comunicaciones como lo último mostrado).

4. **Marcos** escribe "si" `[sólo si P1 = b]`.
   →
   - Jugadas: `confirmar`. Vale para lo último que Marcos vio: el inicio de la tarea de comunicaciones,
     nunca la vista previa reemplazada de la del PLC.
   - Efecto: la de comunicaciones en `en_curso`; la del PLC sin cambios.

5. **Leda**, por su cuenta, a Marcos (viernes 23, dentro del horario): el recordatorio del día del
   vencimiento de la tarea del PLC.
   →
   - El mensaje dice: que la tarea del PLC vence hoy y que todavía no arrancó.
   - El mensaje no dice: que está en curso.

## Qué mide

- **Garantías (5b):** no inventa (la del PLC no queda en curso); no hace sin confirmación lo que la
  requiere (P1); no deja sin salida; no confunde la tarea, que es lo central: después de la corrección,
  ningún efecto queda en la tarea equivocada.
- **Falla de comprensión:** que la IA no entienda a qué se refiere "la otra". Tiene que preguntar con las
  tareas de Marcos como opciones; aplicar el inicio a cualquier otra tarea, o dejar las dos en curso, es una
  falla de garantía.
