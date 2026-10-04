# 08. Cambio de tema

**Qué prueba:** con una pregunta abierta sobre una tarea, Marcos habla de otra. Leda no atiende lo nuevo
de entrada: le recuerda lo abierto y le ofrece seguir, dejarlo para después o cancelarlo; con la salida
elegida, atiende lo nuevo sin pedirle que lo repita. Un tema a la vez, sin perder nada. ADR 0018,
decisión 4, situación general 1.

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (D+1); `en_curso` desde el
    lunes 19; sin bloqueos ni dependencias.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `en_curso` desde el martes 20; sin bloqueos ni dependencias; sin previsiones anotadas.
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

2. **Marcos** escribe (jueves 22, 10:40): "uff con esto estoy trabado"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del PLC, sin causa.
   - Efecto: ninguno todavía (sin causa no hay bloqueo, mecánica §3).
   - La respuesta dice: una pregunta por la causa.
   - Estado después: tema abierto: el bloqueo de la tarea del PLC, esperando la causa.

3. **Marcos** escribe (jueves 22, 10:43): "che y lo de comunicaciones no llego al 30, necesito hasta el
   miercoles 4"
   →
   - Jugadas: `anotar_prevision` sobre la tarea de comunicaciones, con fecha miércoles 4 de noviembre. No
     es la causa del bloqueo abierto: habla de otra tarea.
   - Efecto: ninguno todavía. El mensaje queda guardado con su jugada y sus datos.
   - La respuesta dice: qué quedó abierto (el bloqueo de la tarea del PLC, sin causa) y las tres salidas:
     seguir con eso, dejarlo para después o cancelarlo.
   - La respuesta no dice: que anotó la previsión; nada que trate la fecha como la causa del bloqueo.
   - Botones: PENDIENTE (P13): ¿las tres salidas van con botones?
   - Estado después: tema abierto, el mismo; el mensaje nuevo, guardado a la espera de la salida.

4. **Marcos** escribe (jueves 22, 10:44): "despues lo vemos"
   →
   - Jugadas: `dejar_para_despues`, sobre el bloqueo sin causa.
   - Efecto: el bloqueo sin causa pasa a los temas para después de Marcos (no se anota ningún bloqueo).
     Leda atiende el mensaje guardado: la previsión del miércoles 4 en la tarea de comunicaciones, con
     su aviso a Ismael (P3 para la confirmación, P6 para el contenido del aviso). La fecha comprometida
     sigue en el viernes 30.
   - La respuesta dice: que lo de la tarea del PLC quedó para después; lo que pasó con la previsión.
   - La respuesta no dice: que la tarea del PLC está bloqueada.
   - Estado después: tema abierto, la previsión si P3 pide confirmación; para después, el bloqueo de la
     tarea del PLC.

5. **Marcos** escribe "si" `[sólo si P3 pide confirmación]`.
   →
   - Jugadas: `confirmar`, con la guarda de la decisión 2.
   - Efecto: la previsión anotada y el aviso a Ismael guardado.

6. **Cerrada la previsión**, el tema que quedó para después.
   →
   - PENDIENTE (P14): ¿cuándo lo retoma Leda: apenas se cierra la previsión, en el próximo contacto con
     Marcos, o sólo si Marcos lo saca?
   - Cuando se retoma, la pregunta es la misma que quedó abierta (la causa del bloqueo de la tarea del PLC),
     sin pedirle a Marcos que repita que está trabado.

## Qué mide

- **Garantías (5b):** no inventa (ni un bloqueo sin causa ni una fecha cambiada); no hace sin confirmación
  lo que la requiere (P3); no deja sin salida (las tres salidas, y nada queda perdido); no confunde la
  tarea (la previsión va a la de comunicaciones, nunca como causa del bloqueo de la del PLC).
- **Falla de comprensión:** que la IA no sepa si el mensaje del paso 3 contesta la pregunta abierta o
  cambia de tema. Tiene que preguntar; tomar "no llego" como la causa del bloqueo, o atender lo nuevo y
  olvidar lo abierto, es una falla.
