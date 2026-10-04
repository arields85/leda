# 14. Jev: dos tareas parecidas, y el estado dice cuál

**Qué prueba:** Marcos tiene dos tareas "de la comprimidora", pero Leda sólo le avisó de una. Cuando dice
que arrancó "la de la comprimidora", **la respuesta correcta es la tarea del aviso**: el estado de la
conversación sabe qué tarea acaba de mencionar Leda (ADR 0018, decisión 3). Después dice "la otra", que
sólo se entiende con lo anterior. Mide si Jev, que elige sin ese contexto, aporta algo (ADR 0018,
decisión 7).

**Jev corre en paralelo y no decide nada.** En los pasos 2 y 4 se registra, en cada corrida, qué tarea eligió
la IA principal (o si preguntó) y la probabilidad que Jev da a cada tarea. Nada de lo que Leda hace o dice
depende de Jev.

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (D+1); `asignada`; sin
    bloqueos.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; sin bloqueos. En esta conversación no hay dependencia entre las dos.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada a Marcos en el día.

## Hilo

1. **Leda**, por su cuenta, a Marcos (jueves 22, dentro del horario): el aviso del día hábil anterior al
   vencimiento de la tarea del PLC. La de comunicaciones no vence mañana y no se menciona.
   →
   - El mensaje dice: la tarea del PLC, que vence mañana, que no hace falta contestar.
   - El mensaje no dice: la tarea de comunicaciones.
   - Botones: PENDIENTE (P4).
   - Estado después: el último aviso enviado a Marcos es el de la tarea del PLC.

2. **Marcos** escribe (jueves 22, 09:45): "dale, ya arranque con la de la comprimidora"
   →
   - Jugadas: `anotar_inicio` sobre la tarea del PLC: Marcos contesta el aviso de esa tarea, y "la de la
     comprimidora" coincide con ella.
   - Efecto: la tarea del PLC pasa a `en_curso` (o se muestra su vista previa, P1).
   - La respuesta dice: que quedó anotado (o se va a anotar) el inicio de la tarea del PLC, nombrándola.
   - Estado después: sin tema abierto (o la vista previa como lo último mostrado, P1).
   - **Respuesta correcta para medir:** la tarea del PLC. Si la IA pregunta cuál, es una falla de
     comprensión (cuenta para el 4 de 5) pero no de garantía. Elegir la de comunicaciones es una falla de
     garantía. Jev, sin el contexto del aviso, puede quedar repartida entre las dos.

3. **Marcos** toca "Confirmar" `[sólo si P1 = b]`.
   →
   - Jugadas: `confirmar`, con la guarda de la decisión 2.
   - Efecto: la del PLC en `en_curso`, una sola vez.

4. **Marcos** escribe (jueves 22, 15:00): "y la otra de la comprimidora tambien la empece"
   →
   - Jugadas: `anotar_inicio` sobre la tarea de comunicaciones: es "la otra" frente a la del PLC, ya
     arrancada esta mañana.
   - Efecto: la tarea de comunicaciones pasa a `en_curso` (o se muestra su vista previa, P1).
   - La respuesta dice: que quedó anotado (o se va a anotar) el inicio de la tarea de comunicaciones.
   - La respuesta no dice: que la del PLC se volvió a arrancar.
   - **Respuesta correcta para medir:** la tarea de comunicaciones. Preguntar es una falla de comprensión;
     volver a anotar la del PLC es una falla de garantía.

5. **Marcos** toca "Confirmar" `[sólo si P1 = b]`.
   →
   - Efecto: la de comunicaciones en `en_curso`, una sola vez.

## Qué mide

- **Garantías (5b):** no confunde la tarea, que es lo central; no inventa; no hace sin confirmación lo que
  la requiere (P1); no deja sin salida.
- **Falla de comprensión:** preguntar cuál en el paso 2 o en el 4, cuando el estado ya lo dice. Sigue siendo
  una pregunta y no otra acción, así que no rompe las garantías.
- **Jev:** se compara, corrida por corrida, contra la respuesta correcta de los pasos 2 y 4.
