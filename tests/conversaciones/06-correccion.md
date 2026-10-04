# 06. "No, era la otra tarea"

**Qué prueba:** Leda toma "ya arranqué" para la tarea del aviso, que es lo correcto según el estado, y lo
anota directo. Marcos corrige: era la otra. Se agrega un hecho de corrección: la tarea equivocada vuelve a
como estaba, el inicio queda en la correcta y nada se borra. ADR 0018, decisión 4, situación general 3, y
decisión 9f.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (tres días hábiles después
    de D); `asignada`; sin bloqueos.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; sin bloqueos. En esta conversación no hay dependencia entre las dos (la de la semilla no
    se carga), para que arrancar la de comunicaciones sea posible.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada a Marcos en la semana.

## Hilo

1. **Leda**, por su cuenta, a Marcos (martes 20, 10:00): el aviso previo de la tarea del PLC.
   →
   - El mensaje dice: la tarea del PLC, que vence el viernes 23, que no hace falta contestar.
   - Botones: ninguno (decisión 9b).
   - Estado después: el último aviso enviado a Marcos es el de la tarea del PLC.

2. **Marcos** escribe (martes 20, 10:50): "ya arranque esta mañana 👍"
   →
   - Jugadas: `anotar_inicio` sobre la tarea del PLC (contesta su aviso).
   - Efecto: la tarea del PLC pasa a `en_curso`, directo (decisión 9a), con evento de Marcos y auditoría.
   - La respuesta dice: que se anotó el inicio de la tarea del PLC, nombrándola, para que Marcos pueda ver
     si es la que quería.
   - Estado después: sin tema abierto.

3. **Marcos** escribe (martes 20, 10:52): "nono era la otra, la de las comunicaciones. la del plc todavia
   no la empece"
   →
   - Jugadas: `corregir`: el inicio era de la tarea de comunicaciones, no de la del PLC.
   - Efecto: se agrega un hecho de corrección (decisión 9f): la tarea del PLC vuelve a `asignada` y la de
     comunicaciones pasa a `en_curso`, las dos con su evento atribuido a Marcos. El inicio original y la
     corrección quedan en la historia, con auditoría; nada se edita ni se borra (constitución §12; el estado
     es la proyección de los eventos). Un inicio no genera avisos, así que no hay aviso que corregir.
   - La respuesta dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar.
   - La respuesta no dice: que las dos están en curso; nada que reproche el error.
   - Estado después: sin tema abierto.

4. **Leda**, por su cuenta, a Marcos (viernes 23, 10:00): el recordatorio del día del vencimiento de la
   tarea del PLC.
   →
   - El mensaje dice: que la tarea del PLC vence hoy y que todavía no arrancó; pide el estado (decisión 9b).
   - El mensaje no dice: que está en curso; nada del inicio corregido como si hubiera valido.

## Qué mide

- **Garantías (5b):** no inventa (la del PLC no queda en curso); no hace sin confirmación lo que la
  requiere (nada la requiere en este circuito); no deja sin salida; no confunde la tarea, que es lo central:
  después de la corrección, ningún efecto queda vigente en la tarea equivocada, y la historia guarda los dos
  hechos.
- **Falla de comprensión:** que la IA no entienda a qué se refiere "la otra". Tiene que preguntar con las
  tareas de Marcos como opciones; aplicar el inicio a cualquier otra tarea, o dejar las dos en curso, es una
  falla de garantía.
