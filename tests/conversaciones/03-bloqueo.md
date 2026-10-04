# 03. "Estoy trabado, falta el repuesto"

**Qué prueba:** Marcos contesta el aviso con un bloqueo y su causa. Leda lo anota, directo; pregunta quién
se encarga de destrabarlo; como Marcos no puede resolverlo solo, propone salidas; avisa a Ismael; y la
escalera de recordatorios se detiene. ADR 0018, decisión 5a, tercera respuesta, con la enmienda de la
decisión 9c: el arranque de la persecución (pasos 1 a 4), sin escribirle todavía a quien se encarga.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (tres días hábiles después
    de D); `en_curso` desde el lunes 19; sin bloqueos.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; depende de la del PLC con una dependencia bloqueante (la de la semilla).
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** nada a Marcos ni a Ismael en la semana.

## Hilo

1. **Leda**, por su cuenta, a Marcos (martes 20, 10:00): el aviso previo de la tarea del PLC.
   →
   - El mensaje dice: la tarea del PLC, que vence el viernes 23, que no hace falta contestar.
   - Botones: ninguno (decisión 9b).
   - Estado después: el último aviso enviado a Marcos es el de la tarea del PLC.

2. **Marcos** escribe (martes 20, 10:20): "estoy trabado, falta el repuesto"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del PLC, con causa "falta el repuesto". Trae causa, así que
     el paso 1 de 9c (pedir la explicación) no hace falta; lo prueban las conversaciones 07 y 08.
   - Efecto: un bloqueo abierto en la tarea del PLC, con causa, fecha y quién lo declaró; la tarea pasa de
     `en_curso` a `bloqueada` (mecánica §3: no hay bloqueo sin causa, y salir de `bloqueada` la devuelve a
     `en_curso`); la escalera de recordatorios de esa tarea se detiene (mecánica §9). Auditoría. Un aviso a
     Ismael guardado como hechos (ADR 0018, decisión 8).
   - Confirmación: ninguna; el bloqueo se anota directo (decisión 9a).
   - La respuesta dice: que quedó anotado el bloqueo y su causa; una sola pregunta: quién se encarga de
     conseguir el repuesto (la causa depende de otra persona, 9c, paso 2).
   - La respuesta no dice: cuándo llega el repuesto; que Leda le va a escribir a alguien o lo va a seguir
     (eso es la prueba siguiente); que Ismael ya se enteró.
   - Botones: ninguno; quién se encarga es un dato libre.
   - Estado después: tema abierto: el bloqueo de la tarea del PLC, esperando quién se encarga.

3. **Marcos** escribe (martes 20, 10:25): "ni idea quien lo esta comprando, lo pidieron hace dos semanas"
   →
   - Jugadas: la respuesta a la pregunta abierta: quién se encarga de destrabarlo, que Marcos no sabe.
   - Efecto: el bloqueo queda con quién se encarga "no se sabe", atribuido a Marcos, con auditoría. Cómo se
     guarda ese dato se decide con las tablas de la Etapa 2 (ADR 0017, decisión 3a).
   - La respuesta dice: que quedó anotado que no se sabe quién lo compra; salidas que Leda propone porque
     Marcos no puede resolverlo solo (9c, paso 3): que alguien lo ayude o anotar una fecha nueva (la
     jugada de la nueva previsión); que Ismael se va a enterar, sólo si el código lo informa.
   - La respuesta no dice: un nombre de quién compra que nadie dio; una fecha de llegada inventada; dos
     preguntas juntas.
   - Botones: ninguno.
   - Estado después: tema abierto: las salidas propuestas, a la espera de lo que Marcos elija.

4. **Leda**, por su cuenta, a Ismael (martes 20, enseguida, dentro del horario): el aviso del bloqueo
   (9c, paso 4).
   →
   - Efecto: un mensaje privado en el outbox para Ismael, redactado justo antes de enviarlo con los hechos
     de ese momento (9b).
   - El mensaje dice: la tarea del PLC, que está bloqueada y por qué (falta el repuesto); el atraso según
     el código (ninguno todavía: vence el viernes 23); que la tarea de comunicaciones depende de ella; que
     Marcos no sabe quién se encarga de comprar el repuesto.
   - El mensaje no dice: que alguien está comprando el repuesto; un reproche a Marcos; nada que Marcos no
     dijo.
   - PENDIENTE: si Marcos no contestara quién se encarga, cuándo sale el aviso (enseguida con lo que se
     sabe, o después de un plazo). En este hilo contesta antes, así que el aviso lleva su respuesta.
   - Estado de Ismael después: sin tema abierto; el aviso no espera respuesta por chat.

5. **Marcos** escribe (martes 20, 10:30): "no, hay que esperar que llegue nomas"
   →
   - Jugadas: `cancelar`, sobre las salidas propuestas.
   - Efecto: ninguno nuevo. El bloqueo sigue abierto, con su causa.
   - La respuesta dice: que el bloqueo queda anotado como está; un próximo paso (puede avisar cuando llegue
     el repuesto).
   - La respuesta no dice: otra vez las salidas; un juicio sobre la decisión.
   - Estado después: sin tema abierto, nada para después.

6. **Leda** no le escribe a Marcos sobre la tarea del PLC el viernes 23 ni los días hábiles siguientes.
   →
   - Efecto: ningún recordatorio de esa tarea en el outbox mientras el bloqueo siga abierto. Un bloqueo
     viejo escala por su antigüedad según el pack (cinco días), fuera de esta conversación.

## Qué mide

- **Garantías (5b):** no inventa (no da por sabido quién compra el repuesto, ni cuándo llega, ni un atraso
  que el código no calculó); no hace sin confirmación lo que la requiere (nada la requiere en este
  circuito); no deja sin salida (las salidas del paso 3 y el próximo paso del 5); no confunde la tarea (el
  bloqueo va a la del PLC, y la de comunicaciones aparece sólo como lo que depende).
- **Falla de comprensión:** que la IA no tome "estoy trabado" como un bloqueo, o "ni idea quien lo esta
  comprando" como la respuesta a quién se encarga. Tiene que preguntar; anotar una previsión o un inicio es
  una falla de garantía.
