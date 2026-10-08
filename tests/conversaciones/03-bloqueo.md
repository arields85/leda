# 03. "Estoy trabado, falta el repuesto"

**Qué prueba:** Marcos contesta el aviso con un bloqueo y su causa. Leda lo anota, directo, y pregunta
quién lo puede destrabar; esa pregunta espera respuesta: Marcos no contesta ese día y Leda la repite el día
hábil siguiente. Como Marcos no sabe quién, Leda propone salidas. Ismael no recibe ningún aviso por el
bloqueo, y la escalera de recordatorios de la tarea se detiene. ADR 0018, decisión 5a, tercera respuesta,
con la enmienda de la decisión 9c (corregida el 2026-10-05): el arranque de la persecución (pasos 1 a 4),
sin escribirle todavía a quien destraba.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (tres días hábiles después
    de D); `en_curso` desde el lunes 19; sin bloqueos.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; depende de la del PLC con una dependencia bloqueante (la de la semilla).
    Criterio de aceptación: "Los equipos de la comprimidora se comunican con el PLC por la red de planta
    sin errores durante una hora".
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
     `en_curso`); la escalera de recordatorios de esa tarea se detiene (mecánica §9). Auditoría. Ningún
     aviso a Ismael (9c, paso 4).
   - Confirmación: ninguna; el bloqueo se anota directo (decisión 9a).
   - La respuesta dice: que quedó anotado el bloqueo y su causa; una sola pregunta: quién lo puede
     destrabar (todo bloqueo con causa la lleva; 9c, paso 2, corregido el 2026-10-05). La pregunta no
     sale de un juicio sobre si la causa depende de otro: lo que sigue lo decide la respuesta de Marcos.
   - La respuesta no dice: cuándo llega el repuesto; que Leda le va a escribir a alguien o lo va a seguir
     (eso es la prueba siguiente); que Ismael se enteró o se va a enterar.
   - Botones: ninguno; quién lo destraba es un dato libre.
   - Estado después: tema abierto: el bloqueo de la tarea del PLC, esperando quién lo destraba. La pregunta
     espera respuesta como un pedido de estado (9c, paso 2): queda abierta la espera de la respuesta de
     Marcos.

3. **Nadie** escribe el resto del martes 20.
   →
   - Efecto: ningún otro mensaje de Leda a Marcos el martes. La espera de respuesta sigue abierta.

4. **Leda**, por su cuenta, a Marcos (miércoles 21, 10:00): la pregunta otra vez, el día hábil siguiente
   (9c, paso 2: la misma escalera de quien no contestó, 9b).
   →
   - Efecto: un mensaje privado en el outbox, nunca antes de las 09:00; la espera de respuesta sigue
     abierta.
   - El mensaje dice: el bloqueo de la tarea del PLC por el repuesto; la pregunta de quién lo puede
     destrabar.
   - El mensaje no dice: que va a avisar a Ismael (eso lo dice recién el último paso antes de escalar); un
     reproche porque no contestó (constitución §8); otra pregunta además de ésa.
   - Botones: ninguno.
   - Estado después: tema abierto, el mismo.

5. **Marcos** escribe (miércoles 21, 10:25): "ni idea quien lo esta comprando, lo pidieron hace dos semanas"
   →
   - Jugadas: la respuesta a la pregunta abierta: quién lo destraba, que Marcos no sabe.
   - Efecto: el bloqueo queda con quién lo destraba "no se sabe", atribuido a Marcos, con auditoría; la
     espera de respuesta se cierra y la escalera de la pregunta no sigue. Cómo se guarda ese dato se decide
     con las tablas de la Etapa 2 (ADR 0017, decisión 3a). Averiguarlo con otros es la persecución, de la
     prueba siguiente.
   - La respuesta dice: que quedó anotado que no se sabe quién lo compra; salidas que Leda propone porque
     no hay otra persona que lo destrabe (9c, paso 3): que alguien lo ayude o anotar una fecha nueva (la
     jugada de la nueva previsión). Si Marcos hubiera nombrado a alguien, quedaba anotado como quien
     destraba, sin salidas: seguir a esa persona es la persecución, de la prueba siguiente.
   - La respuesta no dice: un nombre de quién compra que nadie dio; una fecha de llegada inventada; que
     Ismael se va a enterar; dos preguntas juntas.
   - Botones: ninguno.
   - Estado después: tema abierto: las salidas propuestas, a la espera de lo que Marcos elija.

6. **Marcos** escribe (miércoles 21, 10:30): "no, hay que esperar que llegue nomas"
   →
   - Jugadas: `cancelar`, sobre las salidas propuestas.
   - Efecto: ninguno nuevo. El bloqueo sigue abierto, con su causa.
   - La respuesta dice: que el bloqueo queda anotado como está; el próximo paso concreto: que puede avisar
     cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado.
   - La respuesta no dice: otra vez las salidas; un juicio sobre la decisión.
   - Estado después: sin tema abierto, nada para después.

7. **Leda** no le escribe a Marcos sobre la tarea del PLC el viernes 23 ni los días hábiles siguientes, ni
   a Ismael por el bloqueo.
   →
   - Efecto: ningún recordatorio de esa tarea en el outbox mientras el bloqueo siga abierto, y ningún
     mensaje a Ismael. Ismael se entera sólo por un escalamiento (9c, paso 4; mecánica §8): un bloqueo
     viejo escala por su antigüedad según el pack (cinco días), fuera de esta conversación.

## Qué mide

- **Garantías (5b):** no inventa (no da por sabido quién compra el repuesto, ni cuándo llega, ni un atraso
  que el código no calculó); no hace sin confirmación lo que la requiere (nada la requiere en este
  circuito); no deja sin salida (las salidas del paso 5 y el próximo paso del 6); no confunde la tarea (el
  bloqueo va a la del PLC, y la de comunicaciones aparece sólo como lo que depende).
- **Regla del bloqueo (9c):** ningún aviso a Ismael por el bloqueo; todo bloqueo con causa lleva la
  pregunta de quién lo puede destrabar, que se repite el día hábil siguiente y deja de repetirse cuando
  llega la respuesta, aunque sea "no sé". Que Leda proponga salidas sin preguntar es una falla (pasó en el
  primer contacto real, 2026-10-05).
- **Falla de comprensión:** que la IA no tome "estoy trabado" como un bloqueo, o "ni idea quien lo esta
  comprando", al día siguiente, como la respuesta a quién lo destraba. Tiene que preguntar; anotar una
  previsión o un inicio es una falla de garantía.
