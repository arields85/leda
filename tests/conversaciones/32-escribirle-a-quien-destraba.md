# 32. Escribirle a quien destraba

**Qué prueba:** Marcos dice quién puede destrabar una tarea suya y Leda le escribe a esa persona,
como Leda y no en nombre de Marcos: quién está trabado, con qué tarea y qué le falta, y para cuándo
lo puede resolver. A Marcos le dice, en la misma respuesta, que le pregunta y que le avisa apenas
sepa algo. Ariel contesta en su propio chat; queda anotado como un hecho del bloqueo y a Marcos le
llega un aviso informativo con lo que dijo. Cuando quien destraba no tiene un chat con Leda, Leda no
promete nada: dice que no le puede escribir. Si Marcos dice "no le escribas, ya hablé" mientras el
mensaje todavía no salió (el margen para corregir), no sale; si ya salió, Leda lo dice, sin hacer
como que lo retira. Desde la C-5b (decisión 37 del usuario, 2026-10-09): a quien destraba sin Leda
conectada Leda no le escribe, le avisa al administrador para que lo conecte (el aviso sale de
verdad, por su canal) y le ofrece a Marcos salidas: otra persona que pueda destrabarlo, o que se lo
pida él y le cuente. Decisión 4 del usuario (`odd/tasks/fase-c.md`, 2026-10-08, opción A), primera
mitad; ADR 0017, decisión 3a (la persecución del bloqueo), y ADR 0018, 9c, paso 2; constitución §7
("antes de prometer un envío, comprueba que el destinatario y el canal estén conectados") y §8.

**Corre desde la porción 1 de la C-5** (`odd/tasks/fase-c.md`), entera, con su YAML.

## La regla (decidida por el usuario, 2026-10-08)

1. **Leda le escribe directo a quien destraba, como Leda** y no en nombre de quien está trabado.
2. **A quien está trabado le dice, en el mismo mensaje, que le pregunta y que le avisa apenas sepa
   algo.**
3. **Si contesta "no le escribas, ya hablé", no le escribe.**
4. Si quien destraba dice que ya habló con el trabado, Leda le pregunta qué arreglaron y para cuándo
   lo destraba, para que quede asentado: **no es de esta conversación** (la segunda mitad de la
   decisión, una porción siguiente de la C-5).

Cómo se leyó lo que la regla no dice (`PENDIENTE` del usuario, en `odd/tasks/fase-c.md`, C-5):

- **El mensaje a quien destraba es una pregunta que espera respuesta**, con su propia espera: si no
  contesta, Leda la repite el día hábil siguiente, como toda pregunta que espera respuesta (9b), y
  con la regla de una pregunta sin contestar (decisión 21). No escala a nadie por eso: lo que pasa
  con un bloqueo que no se mueve es la decisión 7 (el bloqueo viejo), de otra porción.
- **Le llega terminado el margen para corregir** (10 minutos, ADR 0018, 9n): es un mensaje a otra
  persona por algo que dijo Marcos. Así un "no le escribas" dicho enseguida llega a tiempo.
- **Lo que contesta quien destraba le llega a Marcos con el mismo margen**, como información (no le
  pide nada), y **un "ya está" no cierra el bloqueo**: lo cierra Marcos cuando dice que puede seguir
  (`destrabar`). Quien destraba no es quien declaró el bloqueo ni su responsable (la cocina,
  `resolver_bloqueo`).
- **Sin un chat con Leda** (la persona no conectó Telegram) o fuera del equipo, Leda no le escribe y
  lo dice. A alguien de afuera del equipo nunca le escribe (constitución §6); en esta conversación no
  aparece. **Decidido después (decisión 37, 2026-10-09):** a quien no tiene Leda conectada, además,
  el administrador recibe el aviso para conectarlo, y Leda le ofrece a la persona trabada salidas
  (otra persona que pueda destrabarlo, o que se lo pida ella y le cuente), como un tema abierto.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos** (referente Ismael):
  - "Programar PLC de la comprimidora": vence el viernes 30; `en_curso` desde el lunes 19; sin
    bloqueos. Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin
    fallas".
  - "Revisar comunicaciones industriales de la comprimidora": vence el viernes 6 de noviembre;
    `en_curso` desde el lunes 19; sin bloqueos. Criterio de aceptación: "Los equipos de la
    comprimidora se comunican con el PLC por la red de planta sin errores durante una hora".
  - "Instalar el panel HMI de la comprimidora": vence el viernes 6 de noviembre; `en_curso` desde el
    lunes 19; sin bloqueos. Criterio de aceptación: "El panel HMI muestra el estado de la comprimidora
    y permite arrancarla y pararla desde la planta".
- **Ariel De Simone** (Software e interfaz HMI) tiene un chat con Leda y ninguna tarea en esta
  conversación. **Mariano Naim** (Sistemas eléctricos y tableros) no tiene un chat con Leda (en el
  pack, su Telegram está `PENDIENTE`).
- **Estado de la conversación** de Marcos, de Ariel y de Ismael: sin tema abierto, nada para después,
  nada mostrado para confirmar.
- **Ya enviado:** nada en la semana.

## Hilo

1. **Marcos** escribe (martes 20, 10:20): "estoy trabado con el plc me falta la ip del servidor de
   corelabs"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del PLC, con su causa.
   - Efecto: un bloqueo abierto en la tarea del PLC, con su causa; la tarea pasa a `bloqueada`.
     Auditoría. Ningún aviso a Ismael (9c, paso 4).
   - La respuesta dice: que quedó anotado el bloqueo con su causa; una sola pregunta: quién lo
     puede destrabar.
   - Estado después: tema abierto, quién destraba el PLC.

2. **Marcos** escribe (martes 20, 10:22): "eso me lo tiene que pasar ariel"
   →
   - Jugadas: `anotar_quien_destraba`, con Ariel.
   - Efecto: queda anotado que lo destraba Ariel, dicho por Marcos; la pregunta y su espera se
     cierran. Se guarda el mensaje a Ariel, que sale terminado el margen para corregir (10:32).
   - La respuesta dice: que quedó anotado que lo destraba Ariel; que Leda le pregunta a Ariel para
     cuándo y le avisa a Marcos apenas sepa algo.
   - La respuesta no dice: que ya le escribió a Ariel; que le escribe en nombre de Marcos; una fecha
     de Ariel que nadie dio; que Ismael se entera.
   - Estado después: sin tema abierto; ninguna espera de Marcos abierta.

3. **Leda**, por su cuenta, a Ariel (martes 20, 10:32): la pregunta.
   →
   - Efecto: un mensaje privado a Ariel; una pregunta abierta de Ariel sobre la tarea del PLC (para
     cuándo lo destraba), con su espera.
   - El mensaje dice: que Marcos está trabado con la tarea del PLC; lo que le falta, como lo dijo
     Marcos (la IP del servidor de CoreLabs); la pregunta: para cuándo se la puede pasar.
   - El mensaje no dice: que escribe en nombre de Marcos; un reproche; que se va a avisar a alguien
     si no contesta.
   - Estado después (Ariel): tema abierto, para cuándo destraba la tarea del PLC.

4. **Ariel** escribe (martes 20, 11:05): "uh me olvide, mañana a la mañana se la paso"
   →
   - Jugadas: `decir_cuando_destraba` sobre la tarea del PLC, para el miércoles 21.
   - Efecto: queda anotado, como un hecho del bloqueo, que Ariel dice que lo resuelve el miércoles
     21, con sus palabras y atribuido a él; su pregunta y su espera se cierran. Se guarda el aviso
     a Marcos, que sale terminado el margen para corregir (11:15). El bloqueo sigue abierto.
   - La respuesta dice: que quedó anotado; que Marcos se va a enterar.
   - La respuesta no dice: que el bloqueo se cerró; un reproche porque se olvidó.
   - Estado después (Ariel): sin tema abierto.

5. **Leda**, por su cuenta, a Marcos (martes 20, 11:15): lo que dijo Ariel.
   →
   - Efecto: un mensaje privado a Marcos, informativo.
   - El mensaje dice: la tarea del PLC; que Ariel dice que mañana (mié 21/10) a la mañana le pasa
     la IP; que cuando pueda seguir, lo diga; que no hace falta responder.
   - El mensaje no dice: que la tarea se destrabó.

6. **Marcos** escribe (martes 20, 11:40): "con comunicaciones tambien estoy parado, falta que
   mariano termine el cableado del tablero"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea de comunicaciones, con su causa, y
     `anotar_quien_destraba`, con Mariano.
   - Efecto: el bloqueo de la tarea de comunicaciones, con su causa; queda anotado que lo destraba
     Mariano. **Ningún mensaje a Mariano**: no tiene un chat con Leda. **El aviso al administrador
     para que lo conecte** sale de verdad, por su canal (un incidente con su aviso; decisión 37).
   - La respuesta dice: que quedó anotado el bloqueo y que lo destraba Mariano; que a Mariano Leda
     todavía no le puede escribir; que ya se lo avisó al administrador para que lo conecte; una sola
     pregunta, con las salidas: si hay otra persona que pueda destrabarlo, o si se lo pide Marcos y
     le cuenta.
   - La respuesta no dice: que le va a preguntar a Mariano o que le avisa cuando sepa algo de él.
   - Estado después: tema abierto, las salidas del bloqueo de comunicaciones.

6b. **Marcos** escribe (martes 20, 11:43): "pedile a lucas, el tambien sabe del tablero"
    →
    - Jugadas: `anotar_quien_destraba` sobre la tarea de comunicaciones, con Lucas.
    - Efecto: queda anotado que lo destraba Lucas, dicho por Marcos; las salidas se cierran. Se
      guarda el mensaje a Lucas, que sale terminado el margen para corregir (11:53).
    - La respuesta dice: que quedó anotado que lo destraba Lucas; que Leda le pregunta a Lucas para
      cuándo y le avisa a Marcos apenas sepa algo.
    - La respuesta no dice: que ya le escribió a Lucas; que le escribe en nombre de Marcos.
    - Estado después: sin tema abierto.

6c. **Leda**, por su cuenta, a Lucas (martes 20, 11:53): la pregunta.
    →
    - Efecto: un mensaje privado a Lucas; una pregunta abierta de Lucas sobre la tarea de
      comunicaciones (para cuándo la destraba), con su espera.
    - El mensaje dice: que Marcos está trabado con la tarea de comunicaciones; lo que le falta, como
      lo dijo Marcos; la pregunta: para cuándo lo puede destrabar.
    - El mensaje no dice: que escribe en nombre de Marcos; un reproche.

7. **Marcos** escribe (martes 20, 14:00): "el panel hmi tambien esta trabado, ariel tiene que
   liberar la licencia"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del panel HMI, con su causa, y
     `anotar_quien_destraba`, con Ariel.
   - Efecto: el bloqueo y quién lo destraba; se guarda el mensaje a Ariel, que sale a las 14:10.
   - La respuesta dice: que quedó anotado; que le pregunta a Ariel y le avisa apenas sepa algo.

8. **Marcos** escribe (martes 20, 14:03): "no le escribas a ariel, ya hable con el recien"
   →
   - Jugadas: `no_escribirle`, sobre la tarea del panel HMI.
   - Efecto: el mensaje a Ariel no sale: queda retirado con su motivo (Marcos pidió que no le
     escriba), nunca borrado. Auditoría. El bloqueo y quién lo destraba siguen anotados.
   - La respuesta dice: que no le escribe a Ariel; el próximo paso: que Marcos avise cuando se
     destrabe.
   - La respuesta no dice: que ya le escribió.

9. **Nadie** escribe hasta las 14:10.
   →
   - Efecto: ningún mensaje a Ariel.

10. **Marcos** escribe (martes 20, 15:00): "y por lo del plc tampoco le escribas a ariel, ya lo
    hablamos"
    →
    - Jugadas: `no_escribirle`, sobre la tarea del PLC.
    - Efecto: ninguno: ese mensaje ya le llegó a Ariel a las 10:32.
    - La respuesta dice: que a Ariel ya le escribió esta mañana, y que no se puede retirar.
    - La respuesta no dice: que lo retiró o que no le va a llegar.

## Qué mide

- **Garantías (5b):** no promete un mensaje que no va a salir (Mariano, sin chat; el que Marcos
  pidió que no saliera); no dice que avisó al administrador si el aviso no salió; no dice que salió lo que todavía no salió; no hace como que retira lo que ya
  llegó; no da por cerrado un bloqueo que sólo quien está trabado puede dar por cerrado; no le
  escribe a Ariel en nombre de Marcos; no inventa una fecha.
- **Falla de comprensión:** que la IA no tome "eso me lo tiene que pasar ariel" como quién destraba,
  "mañana a la mañana se la paso" como lo que dice quien destraba, o "no le escribas a ariel" como el
  pedido de no escribirle.
