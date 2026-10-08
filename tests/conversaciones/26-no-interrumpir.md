# 26. No interrumpir una conversación

**Qué prueba:** un aviso que Leda manda por su cuenta llega a su hora mientras la persona está conversando
con ella, o mientras tiene una pregunta de Leda sin contestar. El aviso espera, nunca se mezcla con otro
tema y, cuando sale, no repite lo que se acaba de hablar. Hallazgo de la prueba por Telegram real del
2026-10-08: el aviso de que comunicaciones vencía en 3 días salió justo después de una respuesta de Leda,
en medio de la conversación, repitiendo lo que se estaba hablando (bitácora de flujos). Constitución §8
(Leda conversa con fluidez y no agrega mensajes que no aportan), mecánica §10 y la regla de un tema a la
vez (ADR 0018, decisión 4).

**Corre desde la D5 de la C-3d** (`odd/tasks/fase-c.md`): el hilo principal, con su YAML; las variantes
1 a 3 arrancan del mismo estado inicial y las prueban las pruebas del motor
(`tests/motor/test_no_interrumpir.py`).

## La regla (decidida por el usuario, 2026-10-08)

Una regla general de la cocina, para todos los avisos y todos los circuitos, no un caso del aviso previo:

1. **Mientras la persona está conversando, Leda no le escribe por su cuenta.** Está conversando si
   escribió o tocó algo hace menos de **30 minutos** (usuario, 2026-10-08: 5 era poco). Cada mensaje nuevo
   de la persona vuelve a contar los 30 minutos.
2. **Un tema a la vez, también en los avisos.** Mientras la persona tiene una pregunta de Leda sin
   contestar, ningún aviso sale junto con esa pregunta: lo único que le llega de ese tema es la pregunta,
   cuando Leda la repite (y sigue su propio seguimiento hasta escalar, ADR 0018, 9n).
3. **Una tarea distinta se trata aparte.** Un aviso de otra tarea que no pide respuesta ("vence el
   viernes") sale en su propio mensaje cuando pasan los 30 minutos, aunque la pregunta de la otra tarea
   siga abierta. Uno que pide respuesta ("¿cómo viene?") espera a que esa pregunta se cierre: la persona
   nunca tiene dos preguntas de Leda abiertas a la vez.
4. **El aviso espera, no se pierde, y nunca sale fuera del horario.** Si la espera cruza el fin del
   horario, sale el próximo día hábil a la hora en que Leda escribe por su cuenta.
5. **Al salir, el código vuelve a leer** (ADR 0018, decisión 9b), como hoy: si el aviso ya no corresponde,
   no sale y queda registrado por qué; si sus datos cambiaron, sale con los de ese momento. Además, **lo
   que ya se habló no se repite**: si la persona habló de esa tarea después de que el aviso se guardó, la
   parte del aviso sobre esa tarea no sale (queda omitida, con su motivo, nunca en silencio).
6. **Alcance:** todos los avisos a esa persona, también los de coordinación. Los avisos a otras personas
   no cambian: Ismael no está conversando aunque Marcos sí.
7. **No es el margen para corregir:** el margen (ADR 0018, 9n) demora el aviso a **otra** persona para que
   quien habló pueda corregirse; esta regla demora el aviso a **la persona que está hablando**.

Dónde va en la cocina (construido en la D5, 2026-10-08; `leda.motor.no_interrumpir`): la comprobación
antes de mandar cada aviso (`avisos._preparar`, que ya dejaba esperando el aviso de alguien ausente), el
reparto de lo que sale con una pregunta abierta (`avisos.enviar_avisos`) y la omisión de lo ya hablado con
la misma lectura de los turnos que usa el motivo de un atraso (los hechos de cada mensaje de la persona
que nombran la tarea). Los 30 minutos, en `workspace_setting` (`no_interrumpir_minutos`), como el margen
para corregir.

Cómo se leyó lo que la regla no dice (`PENDIENTE` del usuario, en `odd/tasks/fase-c.md`, D5; en cada
caso, la lectura que no interrumpe y no pierde nada):

- **Qué es "pide respuesta":** un aviso que hace una pregunta (el pedido de estado, la repregunta, el
  recordatorio de una decisión) o que ofrece decidir (la entrega para revisar). Espera a que se cierre la
  pregunta abierta, aunque pase de un día a otro. La pregunta abierta misma, cuando la escalera la
  repite, sale sola.
- **Lo ya hablado** (punto 5) omite sólo los avisos que recuerdan algo de la propia tarea de la persona y
  no traen nada nuevo (el aviso previo y el recordatorio del vencimiento con una previsión). Los que traen
  el acto de otra persona (una decisión, una previsión, un escalamiento) o piden algo no se omiten:
  esperan y salen releídos.
- **Un aviso que no pide respuesta, de la misma tarea que la pregunta abierta,** espera a que se cierre
  (lo único que le llega de ese tema es la pregunta).

## Estado inicial

- **Día:** D = martes 27, dentro del horario, hasta las 17:00.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 30; `en_curso`; sin bloqueos ni
    dependencias; sin previsiones anotadas.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `en_curso`; sin bloqueos ni dependencias; sin previsiones anotadas.
    Criterio de aceptación: "Los equipos de la comprimidora se comunican con el PLC por la red de planta
    sin errores durante una hora".
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya guardado:** el aviso previo de las dos tareas (vencen en 3 días hábiles), para hoy, martes 27, a las
  10:00, la hora en que salen los mensajes que Leda manda por su cuenta (README, "Datos ficticios").

## Hilo

1. **Marcos** escribe (martes 27, 09:56): "lo de comunicaciones se me va al miercoles 4"
   →
   - Jugadas: `anotar_prevision` sobre la tarea de comunicaciones, miércoles 4 de noviembre, sin motivo.
   - Efecto: la previsión, directo, con la fecha comprometida en el viernes 30. Como la fecha atrasa y no
     hay motivo, el aviso al referente queda guardado esperando el motivo (ADR 0018, 9n).
   - La respuesta dice: que quedó anotado que la de comunicaciones llega el miércoles 4, y pregunta qué la
     atrasa.
   - Estado después: tema abierto, la pregunta del motivo de comunicaciones.

2. **Leda**, al llegar las 10:00 del martes 27, va a mandar el aviso previo de las dos tareas a Marcos.
   →
   - Efecto: Marcos escribió hace 4 minutos: está conversando. El aviso no sale y sigue guardado (regla,
     punto 1). Ningún mensaje para Marcos.

3. **Marcos** escribe (martes 27, 10:02): "espero el switch, no llego"
   →
   - Jugadas: el motivo de la previsión de comunicaciones.
   - Efecto: el motivo queda anotado; el aviso al referente sale con el margen para corregir, a las 10:12,
     con la fecha del 4 y el motivo.
   - La respuesta dice: que quedó anotado el motivo y que la nueva fecha queda informada, sin nombrar a
     quién (`odd/tasks/fase-c.md`, decisión 11).
   - La respuesta no dice: que comunicaciones vence en 3 días; nada del aviso previo; el nombre de Ismael.
   - Estado después: sin tema abierto.

4. **Leda**, a las 10:12 del martes 27, manda el aviso a Ismael.
   →
   - Efecto: sale como hoy: Ismael no está conversando. La regla no lo demora. El aviso previo de Marcos
     sigue esperando: escribió hace 10 minutos.
   - El mensaje a Ismael dice: que Marcos prevé terminar la de comunicaciones el miércoles 4, en lugar del
     viernes 30, porque espera el switch.

5. **Leda**, a las 10:15 del martes 27, vuelve a revisar los avisos.
   →
   - Efecto: Marcos escribió hace 13 minutos: el aviso previo sigue esperando. Ningún mensaje para Marcos.

6. **Leda**, a las 10:32 del martes 27 (30 minutos sin que Marcos escriba), vuelve a revisar los avisos.
   →
   - Efecto: Marcos ya no está conversando y el aviso previo sale. El código vuelve a leer: la parte de
     comunicaciones ya no corresponde (Marcos le dio otra fecha, y el seguimiento se movió a ella) y,
     además, Marcos habló de esa tarea después de que el aviso se guardó (regla, punto 5): no sale y queda
     omitida con su motivo. Sale sólo la del PLC.
   - El mensaje a Marcos dice: que la tarea del PLC vence el viernes 30, sin exigir respuesta (mecánica
     §9: el aviso previo es cordial y no pide nada).
   - El mensaje no dice: que comunicaciones vence; nada de lo que Marcos acaba de contar.
   - Estado de Marcos después: sin tema abierto.

## Variante 1: la persona deja de contestar

Con el mismo estado inicial, Marcos no contesta el paso 1 y no escribe nada más.

1. **Leda**, a las 10:00, no manda el aviso previo: Marcos escribió hace 4 minutos.
2. **Leda**, a las 10:26 (30 minutos sin que Marcos escriba), manda el aviso previo, en su propio mensaje.
   →
   - Efecto: la parte de comunicaciones no sale: Marcos habló de esa tarea después de que el aviso se
     guardó, y su tema sigue abierto (regla, punto 2). Sale la del PLC, que es otra tarea y no pide
     respuesta (regla, punto 3).
   - El mensaje no repite la pregunta del motivo ni abre otra.
   - Estado después: tema abierto, la misma pregunta del motivo.
3. **Leda**, el miércoles 28 a las 10:00, repite sólo la pregunta del motivo de comunicaciones, sin ningún
   aviso de otro tema en el mismo mensaje.

## Variante 2: un aviso de otra tarea que pide respuesta

Con la pregunta del motivo de comunicaciones abierta, a Marcos le toca un pedido de estado del PLC ("¿cómo
viene?"). No sale mientras la pregunta de comunicaciones siga abierta (regla, punto 3): sale cuando Marcos
la contesta y pasan los 30 minutos, con los datos de ese momento.

## Variante 3: la conversación llega al cierre del horario

Marcos conversa con Leda hasta las 16:50 del martes 27. El aviso que esperaba no sale a las 17:20, fuera
del horario: sale el miércoles 28 a la hora en que Leda escribe por su cuenta, con lo que el código lea ese
día (regla, punto 4). Un "vence mañana" que llega al día del vencimiento queda reemplazado por el
recordatorio de ese día.
