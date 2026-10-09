# 43. Cerrar el tema para todos

**Qué prueba:** nunca queda un tema abierto sin que todos sepan cómo se cerró. Ariel iba a conseguir
el cable que le falta a Marcos; Marcos lo consigue por otro lado y Leda le avisa a Ariel que ya no
hace falta, y deja de preguntarle. Ariel contesta algo que afecta a Marcos ("ya lo pedí, no lo puedo
cancelar"): Leda se lo lleva a Marcos, que decide, y su respuesta le llega a Ariel, que cierra el tema
para los dos. Con otra tarea, Marcos pide que Leda no le escriba más a Ariel después de que la
pregunta ya le llegó: Leda deja de preguntarle y le cierra el tema. Y con una tercera, Marcos se lo
pide él mismo a quien destraba ("se lo pido yo y te cuento"): Leda no le escribe a nadie y al día
hábil siguiente le pregunta a Marcos cómo le fue. Decisión 39 del usuario (`odd/tasks/fase-c.md`,
2026-10-09, opción A ampliada; regla general), con lo derivado de ella para "no le escribas"
(decisión 47) y la salida "se lo pido yo y te cuento" de la decisión 37; ADR 0017, decisión 3a.

**Corre desde la C-5c** (`odd/tasks/fase-c.md`), entera, con su YAML.

## La regla (decidida por el usuario, 2026-10-09)

1. **Si el bloqueo se resuelve por otro lado, Leda le avisa a quien le estaba preguntando** que ya no
   hace falta, y deja de preguntarle.
2. **Si esa persona contesta algo que afecta a otro, Leda se lo lleva a quien decide** y les cierra el
   tema a los dos.
3. **"No le escribas" después de que la pregunta salió:** Leda deja de preguntarle a quien destraba y
   le cierra el tema (derivado de la decisión 39 en la 47).
4. **"Se lo pido yo y te cuento"** (la salida de la decisión 37): Leda lo anota, no le escribe a quien
   destraba y, al día hábil siguiente, le pregunta a la persona trabada cómo le fue (la pregunta de lo
   que arreglaron, con la escalera de las preguntas, que nunca la abandona: decisión 38).

Cómo se leyó lo que la regla no dice:

- **Quién tiene el tema abierto:** a quien Leda le preguntó, o que ya habló de ese bloqueo, mientras
  lo último que dijo no sea que ya está (eso lo cerró él) ni que no le corresponde (ya se fue de la
  cadena). A quien Leda todavía no le escribió no hay nada que cerrarle: su mensaje no sale.
- **Lo que le lleva a quien decide no lo obliga a contestar:** si quiere decir algo, Leda se lo pasa;
  su respuesta cierra el tema y no le pide nada más a nadie.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos** (referente Ismael), todas `en_curso` desde el lunes 19 y sin bloqueos:
  - "Programar PLC de la comprimidora": vence el viernes 30. Criterio de aceptación: "La
    comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Instalar el panel HMI de la comprimidora": vence el viernes 6 de noviembre. Criterio de
    aceptación: "El panel HMI muestra el estado de la comprimidora y permite arrancarla y pararla
    desde la planta".
  - "Cablear tablero de la máquina 3": vence el viernes 6 de noviembre. Criterio de aceptación: "El
    tablero de la máquina 3 queda cableado y probado con la máquina en marcha".
- **Ariel De Simone** tiene un chat con Leda y ninguna tarea en esta conversación. **Mariano Naim**
  no tiene un chat con Leda (en el pack, su Telegram está `PENDIENTE`).
- **Estado de la conversación** de Marcos y de Ariel: sin tema abierto, nada para después, nada
  mostrado para confirmar.
- **Ya enviado:** nada en la semana.

## Hilo

1. **Marcos** escribe (martes 20, 10:20): "estoy trabado con el plc, me falta el cable de
   programacion. lo consigue ariel"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del PLC, con su causa, y `anotar_quien_destraba`, con
     Ariel.
   - Efecto: el bloqueo y quién lo destraba; se guarda el mensaje a Ariel, que sale a las 10:30.
   - La respuesta dice: que quedó anotado; que le pregunta a Ariel y le avisa apenas sepa algo.

2. **Leda**, por su cuenta, a Ariel (martes 20, 10:30): la pregunta.
   →
   - Efecto: un mensaje privado a Ariel; una pregunta abierta de Ariel sobre la tarea del PLC, con su
     espera.

3. **Ariel** escribe (martes 20, 10:50): "lo compro mañana y se lo llevo el jueves"
   →
   - Jugadas: `decir_cuando_destraba` sobre la tarea del PLC, para el jueves 22.
   - Efecto: queda anotado, atribuido a Ariel; su pregunta y su espera se cierran; se guarda el aviso
     a Marcos, que sale a las 11:00, y la pregunta a Ariel de si ya lo llevó, para el jueves 22 a las
     10:00 (decisión 42, C-5e; no sale: el bloqueo se cierra antes).
   - La respuesta dice: que quedó anotado; que Marcos se va a enterar.

4. **Leda**, por su cuenta, a Marcos (martes 20, 11:00): lo que dijo Ariel.
   →
   - Efecto: un mensaje privado a Marcos, informativo.

5. **Marcos** escribe (martes 20, 14:00): "ya consegui el cable, lucas tenia uno. sigo con el plc"
   →
   - Jugadas: `destrabar` sobre la tarea del PLC.
   - Efecto: el bloqueo se cierra y la tarea vuelve a `en_curso`. Se guarda el aviso a Ariel de que
     ya no hace falta (se resolvió por otro lado), que sale terminado el margen para corregir (14:10).
   - La respuesta dice: que quedó anotado que puede seguir; que Ariel se va a enterar de que ya no
     hace falta.

6. **Leda**, por su cuenta, a Ariel (martes 20, 14:10): que ya no hace falta.
   →
   - Efecto: un mensaje privado a Ariel, informativo.
   - El mensaje dice: la tarea del PLC; que ya se resolvió por otro lado; que no hace falta que
     consiga el cable; que no hace falta responder.
   - El mensaje no dice: un reproche; quién se lo resolvió, si no lo pregunta.

7. **Ariel** escribe (martes 20, 14:30): "uh ya lo pedi, no lo puedo cancelar"
   →
   - Jugadas: `decir_cuando_destraba` sobre la tarea del PLC, con sus palabras.
   - Efecto: queda anotado lo que dice, atribuido a Ariel. Se guarda el aviso a Marcos, que decide,
     con lo que dijo Ariel (sale a las 14:40): si quiere decirle algo, Leda se lo pasa.
   - La respuesta dice: que Marcos se va a enterar.

8. **Leda**, por su cuenta, a Marcos (martes 20, 14:40): lo que dijo Ariel.
   →
   - Efecto: un mensaje privado a Marcos, informativo.
   - El mensaje dice: la tarea del PLC; que Ariel ya pidió el cable y no lo puede cancelar; que si
     quiere decirle algo, Leda se lo pasa; si no, no hace falta que haga nada.

9. **Marcos** escribe (martes 20, 15:00): "que llegue nomas, queda de repuesto"
   →
   - Jugadas: `contar_lo_que_arreglaron` sobre la tarea del PLC, con sus palabras.
   - Efecto: queda anotado lo que dice, atribuido a Marcos. Se guarda el aviso a Ariel con lo que
     dijo Marcos, que sale a las 15:10 y cierra el tema para los dos.
   - La respuesta dice: que Ariel se va a enterar.

10. **Leda**, por su cuenta, a Ariel (martes 20, 15:10): lo que dijo Marcos.
    →
    - Efecto: un mensaje privado a Ariel, informativo.
    - El mensaje dice: la tarea del PLC; que Marcos dice que llegue nomás, que queda de repuesto;
      que no hace falta responder.

11. **Marcos** escribe (martes 20, 15:20): "el panel hmi tambien esta parado, ariel tiene q liberar la
    licencia"
    →
    - Jugadas: `anotar_bloqueo` sobre la tarea del panel HMI, con su causa, y
      `anotar_quien_destraba`, con Ariel.
    - Efecto: el bloqueo y quién lo destraba; se guarda el mensaje a Ariel, que sale a las 15:30.

12. **Leda**, por su cuenta, a Ariel (martes 20, 15:30): la pregunta por el panel HMI.
    →
    - Efecto: un mensaje privado a Ariel; una pregunta abierta de Ariel sobre la tarea del panel HMI.

13. **Marcos** escribe (martes 20, 15:45): "no le escribas mas a ariel por la licencia, ya lo hable
    yo"
    →
    - Jugadas: `no_escribirle`, sobre la tarea del panel HMI.
    - Efecto: la pregunta ya le había llegado a Ariel: Leda deja de preguntarle (su pregunta y su
      espera se cierran) y se guarda el aviso a Ariel de que ya no le pregunta, que sale a las 15:55.
      Quién destraba sigue anotado; el bloqueo, abierto.
    - La respuesta dice: que a Ariel la pregunta ya le había llegado; que no le pregunta más y se lo
      dice.

14. **Leda**, por su cuenta, a Ariel (martes 20, 15:55): que no le pregunta más.
    →
    - Efecto: un mensaje privado a Ariel, informativo.
    - El mensaje dice: la tarea del panel HMI; que Marcos dice que ya lo hablaron, así que no le
      pregunta más; que no hace falta responder.

15. **Marcos** escribe (miércoles 21, 10:20): "con el tablero estoy trabado, falta que mariano termine
    el cableado"
    →
    - Jugadas: `anotar_bloqueo` sobre la tarea del tablero, con su causa, y `anotar_quien_destraba`,
      con Mariano.
    - Efecto: el bloqueo y quién lo destraba; a Mariano no se le escribe (no tiene un chat con Leda);
      el aviso al administrador para que lo conecte (decisión 37).
    - La respuesta dice: que a Mariano todavía no le puede escribir; que ya se lo avisó al
      administrador; una sola pregunta, con las salidas: otra persona que pueda destrabarlo, o que
      se lo pida Marcos y le cuente.
    - Estado después: tema abierto, las salidas.

16. **Marcos** escribe (miércoles 21, 10:25): "se lo pido yo y te cuento"
    →
    - Jugadas: `pedirselo_y_contar` sobre la tarea del tablero.
    - Efecto: queda anotado (auditado) que se lo pide él; las salidas se cierran; a nadie se le
      escribe. Se guarda la pregunta a Marcos de cómo le fue, para el día hábil siguiente (jueves 22,
      10:00).
    - La respuesta dice: que mañana le pregunta cómo le fue.
    - Estado después: sin tema abierto.

17. **Leda**, por su cuenta, a Marcos (jueves 22, 10:00): cómo le fue con Mariano.
    →
    - Efecto: un mensaje privado a Marcos; una pregunta abierta de Marcos sobre la tarea del tablero
      (qué arregló con Mariano), con su espera.

18. **Marcos** escribe (jueves 22, 10:40): "si, hable con mariano, me lo termina el viernes"
    →
    - Jugadas: `contar_lo_que_arreglaron` sobre la tarea del tablero, para el viernes 23.
    - Efecto: queda anotado, atribuido a Marcos; su pregunta y su espera se cierran. A Mariano no se
      le escribe (no tiene un chat con Leda).
    - La respuesta dice: que quedó anotado.
    - Estado después: sin tema abierto.

## Qué mide

- **Garantías (5b):** a quien Leda le preguntaba se le avisa cómo se cerró el tema y no se le vuelve a
  preguntar; lo que contesta le llega a quien decide; la respuesta de quien decide le llega y cierra el
  tema; "se lo pido yo" no le escribe a nadie y no se olvida: al día hábil siguiente pregunta cómo le
  fue; nunca se le promete un mensaje a quien no tiene Leda conectada.
- **Falla de comprensión:** que la IA no tome "uh ya lo pedi, no lo puedo cancelar" como lo que dice
  quien destrababa, "que llegue nomas, queda de repuesto" como lo que contesta Marcos, "se lo pido yo
  y te cuento" como que se lo pide él, o "si, hable con mariano, me lo termina el viernes" como lo que
  arregló.
