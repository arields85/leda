# 24. Quien aprueba no contesta

**Qué prueba:** dos entregas esperan una decisión que no llega. Leda se lo recuerda a quien aprueba al día
hábil siguiente y otra vez al segundo. Al tercero, si quien aprueba tiene a alguien arriba (Marcos →
Ismael), le avisa a ése que la aprobación está trabada; si no hay nadie arriba (Ismael), sigue con un
recordatorio cordial por día hábil. Al responsable no se le avisa nada: no depende de él
(`odd/tasks/fase-c.md`, decisión 3). Circuito 8 (ADR 0017, decisión 3b); mecánica §7 y §9; constitución
§8 (persistente sin ser hostil).

**Todavía no corre:** el circuito no está construido (`odd/tasks/fase-c.md`, tarea C-3). No tiene YAML.

## Estado inicial

- **Día:** D = lunes 26, dentro del horario.
- **Personas:** Marcos aprueba el trabajo de Nahuel; Ismael aprueba el de Marcos y nadie aprueba el de
  Ismael. Nahuel tiene una cuenta de prueba ficticia.
- **Tareas:**
  - "Actualizar planos eléctricos de la paila 2": de Nahuel, OT; la aprueba Marcos; vence el viernes 30;
    `en_curso`; sin bloqueos ni dependencias.
  - "Programar PLC de la comprimidora": de Marcos, OT; la aprueba Ismael; vence el viernes 30;
    `en_curso`; sin bloqueos ni dependencias.
- **Estado de la conversación de las tres personas:** sin tema abierto, nada para después, nada mostrado
  para confirmar.
- **Ya enviado:** nada en la semana sobre estas tareas.
- **Las dos entregas,** confirmadas con la evidencia completa (como en la conversación 21), forman parte
  del estado inicial y no se repiten acá: la de Nahuel, el lunes 26 a las 11:00; la de Marcos, el lunes 26
  a las 11:30. Las dos tareas, `en_revision`; los dos avisos de entrega salieron enseguida: a Marcos, el
  de Nahuel; a Ismael, el de Marcos.

## Hilo

1. **Nadie** escribe el resto del lunes 26.
   →
   - Efecto: ningún recordatorio el mismo día de la entrega.

2. **Leda**, por su cuenta (martes 27, 10:00), el primer recordatorio a cada uno: a Marcos, de la entrega
   de Nahuel; a Ismael, de la entrega de Marcos.
   →
   - El mensaje dice: la tarea en su renglón con 📋; quién la entregó y cuándo (lun 26/10); que espera su
     decisión; el cierre, aparte: que puede aprobarla o pedir cambios contestando.
   - El mensaje no dice: un reproche; que va a avisarle a otra persona.
   - A Nahuel, nada. A Marcos, nada sobre su propia entrega.
   - Estado después: las dos esperas siguen abiertas; la cuenta de quien no contestó suma uno a cada una.

3. **Leda**, por su cuenta (miércoles 28, 10:00), el segundo recordatorio a cada uno.
   →
   - El mensaje dice: lo mismo que el primero, breve, con que la entrega espera desde el lun 26/10.
   - El mensaje no dice: un reproche; que va a avisarle a otra persona (`PENDIENTE`: si el segundo a
     Marcos avisa que mañana se entera Ismael, como el tercer recordatorio de la mecánica §9).
   - A Nahuel, nada. A Marcos, nada sobre su propia entrega.

4. **Leda**, por su cuenta (jueves 29, 10:00), el tercer día hábil.
   →
   - A Ismael, por la entrega de Nahuel, porque Marcos tiene a alguien arriba: un aviso de que la
     aprobación está trabada. El mensaje dice: que Nahuel entregó la tarea de los planos de la paila 2
     el lun 26/10, con 📋; que Marcos todavía no decidió; que no hace falta que responda, solo en el
     último renglón (`PENDIENTE`: si Ismael puede decidirla él).
   - A Ismael, por la entrega de Marcos, porque no tiene a nadie arriba: un recordatorio cordial. El
     mensaje dice: la tarea del PLC con 📋, que Marcos la entregó el lun 26/10 y que espera su decisión;
     el cierre, aparte, con las dos salidas.
   - Cada tarea, en su bloque y con lo suyo; nunca se mezclan los hechos de una con los de la otra. Si
     van en un mensaje o en dos lo decide la consolidación del día (mecánica §10; `odd/tasks/fase-c.md`,
     pregunta 8).
   - A Nahuel, nada. A Marcos, nada sobre su propia entrega; sobre la de Nahuel, `PENDIENTE` (si sigue un
     recordatorio por día después del aviso a Ismael).
   - Lo que sigue para la entrega de Nahuel (si Ismael se entera cuando Marcos decide, si se le vuelve a
     avisar) es `PENDIENTE`; esta conversación no lo comprueba.

5. **Leda**, por su cuenta, a Ismael (viernes 30, 10:00): el recordatorio cordial de la entrega de
   Marcos.
   →
   - El mensaje dice: lo mismo, breve y cordial, con la entrega del lun 26/10.
   - El mensaje no dice: un reproche; que va a escalar (no hay nadie arriba).
   - A Marcos, nada sobre su entrega.

6. **Nadie** escribe el sábado 31 ni el domingo 1.
   →
   - Efecto: ningún recordatorio: fuera del horario Leda no manda nada por su cuenta.

7. **Ismael** escribe (lunes 2, 09:20): "perdon, estuve a mil. el plc aprobado"
   →
   - Jugadas: `aprobar`, la tarea del PLC (la que tiene esperando a Ismael; la de Nahuel no la aprueba
     él).
   - Efecto: la aprobación; la tarea pasa a `terminada`; la espera de Ismael se cierra y el recordatorio
     del lunes 2 no sale. El aviso a Marcos sale a las 10:00.
   - La respuesta dice: que la tarea del PLC quedó terminada; que Marcos se va a enterar a las 10:00.
   - La respuesta no dice: nada sobre la demora de Ismael.
   - Estado después: sin tema abierto; ningún recordatorio más de esa entrega.

## Qué mide

- **Garantías:** los recordatorios van a quien tiene que decidir, nunca al responsable (no depende de él;
  constitución §8: el seguimiento no es para vigilar); el tercer día hábil se cuenta sobre el calendario
  del espacio (sin el fin de semana); el aviso hacia arriba sale sólo si hay alguien arriba; sin nadie
  arriba, un recordatorio por día hábil y nada más; una decisión corta los recordatorios de esa entrega.
- **El formato:** el de la conversación 20 en cada mensaje.
- **Falla de comprensión:** que la IA tome "el plc aprobado" del paso 7 como otra cosa que la aprobación
  de la tarea del PLC. Aprobar la de Nahuel por Ismael es una falla de garantía.
