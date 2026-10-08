# 26. No interrumpir una conversación

**Qué prueba:** un aviso que Leda manda por su cuenta llega a su hora mientras la persona está conversando
con ella. El aviso espera a que la persona deje de escribir un rato y, cuando sale, no repite lo que se
acaba de hablar. Hallazgo de la prueba por Telegram real del 2026-10-08: el aviso de que comunicaciones
vencía en 3 días salió justo después de una respuesta de Leda, en medio de la conversación, repitiendo lo
que se estaba hablando (bitácora de flujos). El usuario: "tiene que esperar a que se cierre el tema, o salir
después de un rato sin respuesta". Constitución §8 (Leda conversa con fluidez y no agrega mensajes que no
aportan) y mecánica §10 (los mensajes automáticos de un día se consolidan).

**Todavía no corre:** la regla no está construida y el rato sin actividad no está decidido. No tiene YAML.

## La regla propuesta (`PENDIENTE` de acuerdo con el usuario)

Una regla general de la cocina, para todos los avisos y todos los circuitos, no un caso del aviso previo:

1. **Leda no le escribe por su cuenta a alguien que está conversando con ella.** Una persona está
   conversando si escribió o tocó algo hace menos de **N minutos** (`PENDIENTE`: el valor lo decide el
   usuario; la propuesta del agente es 5). Cada mensaje nuevo de la persona vuelve a contar los N minutos.
2. **El aviso espera, no se pierde.** Queda guardado y sale cuando pasan N minutos sin que la persona
   escriba: porque el tema se cerró y la persona se fue, o porque dejó de contestar (en ese caso la
   pregunta abierta sigue abierta y el aviso no abre otra: un tema a la vez).
3. **Al salir, el código vuelve a leer** (ADR 0018, decisión 9b), como hoy: si el aviso ya no corresponde,
   no sale y queda registrado por qué. Además, **lo que ya se habló no se repite**: si en la conversación
   la persona habló de esa tarea después de que el aviso se guardó, la parte del aviso sobre esa tarea no
   sale (queda registrada como omitida, con su motivo, nunca en silencio); si el aviso cubría varias
   tareas, salen sólo las demás, juntas en un solo mensaje.
4. **Alcance:** todos los avisos a esa persona, también los de coordinación (una entrega para revisar):
   esperar unos minutos no le quita nada y no la interrumpe. Los avisos a otras personas no cambian: Ismael
   no está conversando aunque Marcos sí.
5. **No es el margen para corregir:** el margen (ADR 0018, 9n) demora el aviso a **otra** persona para que
   quien habló pueda corregirse; esta regla demora el aviso a **la persona que está hablando**. Las dos
   pueden aplicarse al mismo tiempo, cada una a su destinatario.

Dónde iría en la cocina (relevamiento del 2026-10-08): la comprobación antes de mandar cada aviso
(`avisos._preparar`, que hoy ya deja esperando el aviso de alguien ausente) y la omisión de lo ya hablado
con la misma lectura de los turnos que usa el motivo de un atraso (`fichas._siguio_en_la_tarea`). El valor
N, en `workspace_setting`, como el margen para corregir.

## Estado inicial

- **Día:** D = martes 27, dentro del horario. N = 5 minutos (el valor propuesto; si el usuario decide otro,
  cambian las horas de los pasos 4 a 6).
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 30; `en_curso`; sin bloqueos ni
    dependencias; sin previsiones anotadas.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `en_curso`; sin bloqueos ni dependencias; sin previsiones anotadas.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya guardado:** el aviso previo de las dos tareas (vencen en 3 días hábiles), para hoy, martes 27, a las
  10:00, la hora en que salen los mensajes que Leda manda por su cuenta (README, "Datos ficticios").

## Hilo

1. **Marcos** escribe (martes 27, 09:56): "lo de comunicaciones se me va al miercoles 4"
   →
   - Jugadas: `anotar_prevision` sobre la tarea de comunicaciones, miércoles 4 de noviembre, sin motivo.
   - Efecto: la previsión, directo, con la fecha comprometida en el viernes 30. Como la fecha atrasa y no
     hay motivo, el aviso a Ismael queda guardado esperando el motivo (ADR 0018, 9n).
   - La respuesta dice: que quedó anotado que la de comunicaciones llega el miércoles 4, y pregunta qué la
     demora.
   - Estado después: tema abierto, la pregunta del motivo de comunicaciones.

2. **Leda**, al llegar las 10:00 del martes 27, va a mandar el aviso previo de las dos tareas a Marcos.
   →
   - Efecto: Marcos escribió hace 4 minutos: está conversando. El aviso no sale y sigue guardado, a la
     espera (regla, punto 1).
   - Ningún mensaje para Marcos en la salida.

3. **Marcos** escribe (martes 27, 10:02): "espero el switch, no llego"
   →
   - Jugadas: el motivo de la previsión de comunicaciones.
   - Efecto: el motivo queda anotado; el aviso a Ismael sale con el margen para corregir (10 minutos), a
     las 10:12, con la fecha del 4 y el motivo.
   - La respuesta dice: que quedó anotado el motivo y que Ismael va a ser notificado.
   - La respuesta no dice: que comunicaciones vence en 3 días; nada del aviso previo.
   - Estado después: sin tema abierto.

4. **Leda**, a las 10:05 del martes 27, vuelve a revisar los avisos.
   →
   - Efecto: Marcos escribió hace 3 minutos: el aviso previo sigue esperando. Ningún mensaje para Marcos.

5. **Leda**, a las 10:07 del martes 27 (5 minutos sin que Marcos escriba), vuelve a revisar los avisos.
   →
   - Efecto: Marcos ya no está conversando y el aviso previo sale. El código vuelve a leer: después de
     guardado el aviso, Marcos habló de la tarea de comunicaciones (le dio otra fecha y su motivo), así que
     esa parte no sale y queda omitida con su motivo (regla, punto 3). Sale sólo la del PLC.
   - El mensaje a Marcos dice: que la tarea del PLC vence el viernes 30. Sin exigir respuesta (mecánica §9:
     el aviso previo es cordial y no pide nada).
   - El mensaje no dice: que comunicaciones vence en 3 días ni el viernes; nada de lo que Marcos acaba de
     contar.
   - Estado de Marcos después: sin tema abierto.

6. **Leda**, a las 10:12 del martes 27, manda el aviso a Ismael.
   →
   - Efecto: sale como hoy: Ismael no está conversando. La regla no lo demora.
   - El mensaje a Ismael dice: que Marcos prevé terminar la de comunicaciones el miércoles 4, en lugar del
     viernes 30, porque espera el switch.

## Variante: la persona deja de contestar

Con el mismo estado inicial, Marcos no contesta el paso 1 y no escribe nada más.

1. **Leda**, a las 10:00, no manda el aviso previo: Marcos escribió hace 4 minutos.
2. **Leda**, a las 10:01 (5 minutos sin que Marcos escriba), manda el aviso previo.
   →
   - Efecto: el aviso sale aunque la pregunta del motivo sigue abierta: un rato sin respuesta alcanza
     (regla, punto 2). La parte de comunicaciones no sale: Marcos habló de esa tarea después de que el aviso
     se guardó. Sale la del PLC.
   - El mensaje no abre otra pregunta ni repite la del motivo: la pregunta abierta sigue su propio camino
     (se repite como cualquier pregunta sin respuesta, ADR 0018, 9n).
   - Estado después: tema abierto, la misma pregunta del motivo.

## Lo que queda abierto

- **El valor N** (`PENDIENTE`, decisión del usuario).
- **Una conversación que llega al final del horario:** si la persona sigue escribiendo hasta la hora de
  cierre, el aviso pasaría al día hábil siguiente. Hay que ver si eso es aceptable para el aviso previo
  (que es el día antes) o si sale igual al final del último turno del día. `PENDIENTE`.
