# 03. "Estoy trabado, falta el repuesto"

**Qué prueba:** Marcos contesta el aviso con un bloqueo y su causa. Leda anota el bloqueo y la escalera de
recordatorios se detiene. ADR 0018, decisión 5a, tercera respuesta: el primer paso de la decisión 3a del
ADR 0017, sin la persecución.

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (D+1); `en_curso` desde el
    lunes 19; sin bloqueos ni dependencias.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; sin bloqueos ni dependencias.
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

2. **Marcos** escribe (jueves 22, 10:20): "estoy trabado, falta el repuesto"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del PLC, con causa "falta el repuesto".
   - Efecto: un bloqueo abierto en la tarea del PLC, con causa, fecha y quién lo declaró; la tarea pasa de
     `en_curso` a `bloqueada` (mecánica §3: no hay bloqueo sin causa, y salir de `bloqueada` la devuelve a
     `en_curso`); la escalera de recordatorios de esa tarea se detiene (mecánica §9). Auditoría.
   - Confirmación: PENDIENTE (P2): ¿anotar el bloqueo lleva vista previa y confirmación?
   - Después de anotarlo: PENDIENTE (P9): ¿Leda pregunta algo más (lo mínimo para entenderlo) o avisa a
     Ismael?
   - La respuesta dice: que quedó anotado el bloqueo y su causa.
   - La respuesta no dice: quién va a conseguir el repuesto ni cuándo llega; que Leda lo va a perseguir (la
     persecución no entra en la prueba chica); que avisó a alguien, salvo que el código lo informe (P9).
   - Botones: ninguno, salvo los de la confirmación si P2 la pide.
   - Estado después: sin tema abierto (o, con P9 = b, esperando el dato que Leda pidió).

3. **Marcos** toca "Confirmar" `[sólo si P2 = b]`.
   →
   - Jugadas: `confirmar`, con la guarda de la decisión 2.
   - Efecto: el del paso 2, una sola vez; el toque recibe su señal.

4. **Leda** no le escribe a Marcos sobre la tarea del PLC el viernes 23 ni los días hábiles siguientes.
   →
   - Efecto: ningún recordatorio de esa tarea en el outbox mientras el bloqueo siga abierto. Un bloqueo
     viejo escala por su antigüedad según el pack (cinco días), fuera de esta conversación.

## Qué mide

- **Garantías (5b):** no inventa (no promete el repuesto ni una persecución); no hace sin confirmación lo
  que la requiere (P2); no deja sin salida; no confunde la tarea (el bloqueo va a la del PLC).
- **Falla de comprensión:** que la IA no tome "estoy trabado" como un bloqueo. Tiene que preguntar; anotar
  una previsión o un inicio es una falla de garantía.
