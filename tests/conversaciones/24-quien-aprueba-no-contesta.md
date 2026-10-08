# 24. Quien aprueba no contesta

**Qué prueba:** dos entregas esperan una decisión que no llega. Leda se lo recuerda a quien aprueba al día
hábil siguiente y otra vez al segundo; si tiene a alguien arriba (Marcos → Ismael), el segundo le dice que
al día siguiente se entera ése. Al tercero, le avisa a quien está arriba que la aprobación está trabada,
sólo para que lo sepa: no le pide nada ni lo convierte en aprobador. Quien aprueba sigue con un
recordatorio cordial por día hábil hasta decidir y, cuando decide, a quien está arriba le llega que se
destrabó. Si no hay nadie arriba (Ismael), un recordatorio cordial por día hábil. Al responsable no se le
avisa nada: no depende de él (`odd/tasks/fase-c.md`, decisión 3). Circuito 8 (ADR 0017, decisión 3b); mecánica §7 y §9; constitución
§8 (persistente sin ser hostil).

**Corre desde la porción 3c de la C-3** (`24-quien-aprueba-no-contesta.yaml`; `odd/tasks/fase-c.md`). El YAML
suma lo que el hilo da por hecho: el lunes 2 a las 09:00 la escalera ya guardó los recordatorios del día, el
aviso de la aprobación a Nahuel sale con el de Ismael (paso 10) y los dos días siguientes no sale nada.

## Estado inicial

- **Día:** D = lunes 26, dentro del horario.
- **Personas:** Marcos aprueba el trabajo de Nahuel; Ismael aprueba el de Marcos y nadie aprueba el de
  Ismael. Nahuel tiene una cuenta de prueba ficticia.
- **Tareas:**
  - "Actualizar planos eléctricos de la paila 2": de Nahuel, OT; la aprueba Marcos; vence el viernes 30;
    `en_curso`; sin bloqueos ni dependencias.
    Criterio de aceptación: "Los planos eléctricos de la paila 2 coinciden con la instalación actual y
    quedan cargados en la carpeta de planos".
  - "Programar PLC de la comprimidora": de Marcos, OT; la aprueba Ismael; vence el viernes 30;
    `en_curso`; sin bloqueos ni dependencias.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
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
   - A Marcos, por la entrega de Nahuel, el mensaje dice: lo mismo que el primero, breve, con que la
     entrega espera desde el lun 26/10; y, aparte, que si mañana sigue sin decidir se va a informar,
     sin nombrar a Ismael (como el tercer recordatorio de la mecánica §9; decisión 11 del 2026-10-08).
   - A Ismael, por la entrega de Marcos, el mensaje dice: lo mismo que el primero, breve, con que la
     entrega espera desde el lun 26/10.
   - El mensaje no dice: un reproche; a Marcos, que Ismael va a decidir la tarea de Nahuel; a Ismael,
     que va a avisarle a otra persona (no hay nadie arriba).
   - A Nahuel, nada. A Marcos, nada sobre su propia entrega.

4. **Leda**, por su cuenta (jueves 29, 10:00), el tercer día hábil.
   →
   - A Ismael, por la entrega de Nahuel, porque Marcos tiene a alguien arriba: un aviso, sólo
     informativo, de que la aprobación está trabada. Es una sola vez. El mensaje dice: que Nahuel
     entregó la tarea de los planos de la paila 2 el lun 26/10, con 📋; que Marcos todavía no decidió y
     que Leda se lo sigue recordando; que le avisa cuando se destrabe; que no hace falta que responda,
     solo en el último renglón.
   - Ese aviso no dice: que Ismael la puede aprobar o pedir cambios; que haga algo con Marcos; un
     reproche a Marcos. No lleva botones: Ismael no es quien aprueba esa tarea, y el aviso no lo
     convierte en aprobador (usuario: el responsable del sector se hace cargo de las tareas de su gente).
   - A Marcos, por la entrega de Nahuel: el recordatorio cordial del día. El mensaje dice: la tarea con
     📋, que Nahuel la entregó el lun 26/10 y que espera su decisión; el cierre, aparte, con las dos
     salidas. No dice: un reproche.
   - A Ismael, por la entrega de Marcos, porque no tiene a nadie arriba: un recordatorio cordial. El
     mensaje dice: la tarea del PLC con 📋, que Marcos la entregó el lun 26/10 y que espera su decisión;
     el cierre, aparte, con las dos salidas.
   - Cada tarea, en su bloque y con lo suyo; nunca se mezclan los hechos de una con los de la otra. Si
     van en un mensaje o en dos lo decide la consolidación del día (mecánica §10; `odd/tasks/fase-c.md`,
     pregunta 8).
   - A Nahuel, nada. A Marcos, nada sobre su propia entrega.

5. **Leda**, por su cuenta (viernes 30, 10:00), el recordatorio cordial del día a cada uno: a Marcos, de
   la entrega de Nahuel; a Ismael, de la entrega de Marcos.
   →
   - El mensaje dice: lo mismo, breve y cordial, con la entrega del lun 26/10.
   - El mensaje no dice: un reproche; que va a escalar (a Ismael: no hay nadie arriba; a Marcos: Ismael
     ya está enterado y no se le vuelve a avisar).
   - A Ismael, nada más sobre la entrega de Nahuel. A Nahuel, nada. A Marcos, nada sobre su entrega.

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
   - La respuesta no dice: nada sobre la demora de Ismael; nada sobre la entrega de Nahuel.
   - Estado después: sin tema abierto; ningún recordatorio más de esa entrega.

8. **Leda**, por su cuenta, a Marcos (lunes 2, 10:00): el aviso de la aprobación del PLC y el
   recordatorio cordial del día de la entrega de Nahuel.
   →
   - Cada tarea, en su bloque y con lo suyo, como en el paso 4; si van en un mensaje o en dos lo decide
     la consolidación del día.
   - El recordatorio dice: lo mismo, breve y cordial, con la entrega del lun 26/10. No dice: un reproche.
   - A Ismael, nada. A Nahuel, nada.

9. **Marcos** escribe (10:40): "uh perdon, se me paso. lo de nahuel aprobado"
   →
   - Jugadas: `aprobar`, la tarea de los planos de la paila 2 (la que tiene esperando a Marcos).
   - Efecto: la aprobación; el código comprueba el cierre y la tarea pasa a `terminada`, con evento de
     Marcos y auditoría; la espera de Marcos se cierra y no sale ningún recordatorio más. Salen
     enseguida el aviso de la aprobación a Nahuel (como en la conversación 23) y el de que se destrabó a
     Ismael.
   - La respuesta dice: que la tarea de los planos de la paila 2 quedó terminada; que Nahuel se va a
     enterar ahora; si dice que se informa que ya decidió, sin nombrar a Ismael.
   - La respuesta no dice: nada sobre la demora de Marcos.
   - Estado después: sin tema abierto.

10. **Leda**, por su cuenta, a Ismael (10:40): el aviso de que se destrabó.
    →
    - El mensaje dice, breve: que Marcos aprobó la tarea de los planos de la paila 2 de Nahuel, con 📋,
      y que quedó terminada; que no hace falta que responda, solo en el último renglón.
    - El mensaje no dice: un reproche a Marcos; cuánto tardó.
    - Estado de Ismael después: sin tema abierto; nada más sobre esa entrega.

## Qué mide

- **Garantías:** los recordatorios van a quien tiene que decidir, nunca al responsable (no depende de él;
  constitución §8: el seguimiento no es para vigilar); el tercer día hábil se cuenta sobre el calendario
  del espacio (sin el fin de semana); el segundo recordatorio dice que al día siguiente se entera quien
  está arriba, y el aviso hacia arriba sale sólo si hay alguien arriba, una sola vez, sólo informativo:
  no le pide nada ni lo convierte en aprobador; quien aprueba sigue con un recordatorio cordial por día
  hábil hasta decidir; sin nadie arriba, un recordatorio por día hábil y nada más; una decisión corta los
  recordatorios de esa entrega y, si se había avisado arriba, le llega que se destrabó.
- **El formato:** el de la conversación 20 en cada mensaje.
- **Falla de comprensión:** que la IA tome "el plc aprobado" del paso 7 o "lo de nahuel aprobado" del
  paso 9 como otra cosa que la aprobación de esa tarea. Aprobar la de Nahuel por Ismael es una falla de
  garantía.
