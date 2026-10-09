# 36. El bloqueo viejo

**Qué prueba:** un bloqueo que sigue abierto a los cinco días hábiles se le informa al referente,
una sola vez, aunque la cadena se mueva (quien lo destraba fue dando fechas): va con la historia
entera y las fechas que dio cada uno, sin pedirle nada. Uno más nuevo, o uno que se cerró antes, no
se informa. Decisión 7 del usuario (`odd/tasks/fase-c.md`, 2026-10-08, opción A); mecánica §8 ("un
bloqueo abierto hace más de [pack] días escala aunque nadie lo pida").

**Corre desde la porción 5 de la C-5** (`odd/tasks/fase-c.md`), entera, con su YAML.

## La regla (decidida por el usuario, 2026-10-08)

1. **A los `bloqueos.escala_solo_a_los_dias` días hábiles** (5 en CoreWork, ajustable desde la
   plataforma) **Leda le informa al referente aunque la cadena se mueva, con la historia y las fechas
   dichas.**
2. "El silencio y no informar es peor que avisos informativos útiles."

Cómo se leyó lo que la regla no dice (`PENDIENTE` del usuario, en `odd/tasks/fase-c.md`, C-5):

- **A quién:** al referente del sector de la tarea trabada; si es la persona trabada misma (Marcos es
  el referente de OT), a quien aprueba su trabajo (Ismael), como la cadena de la conversación 34.
- **Una sola vez por bloqueo**, a la hora en que Leda manda lo suyo, dentro del horario y sin
  interrumpir una conversación. Queda registrado a quién y cuándo se informó.
- **Es información:** no le pide nada. A la persona trabada no le llega nada por esto.
- **Los días se cuentan** desde que se anotó el bloqueo, en días hábiles del espacio.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos** (OT, que tiene a Marcos como referente; aprueba su trabajo Ismael):
  - "Programar PLC de la comprimidora": vence el viernes 6 de noviembre; `en_curso` desde el lunes 19;
    sin bloqueos.
  - "Instalar el panel HMI de la comprimidora": vence el viernes 6 de noviembre; `en_curso` desde el
    lunes 19; sin bloqueos.
- **Ariel De Simone** tiene un chat con Leda y ninguna tarea en esta conversación.
- **Estado de la conversación** de todos: sin tema abierto, nada para después.
- **Ya enviado:** nada en la semana.

## Hilo

1. **Marcos** escribe (martes 20, 10:20): "estoy trabado con el plc me falta la ip del servidor de
   corelabs"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del PLC, con su causa.
   - Efecto: un bloqueo abierto en la tarea del PLC, desde el martes 20.

2. **Marcos** escribe (martes 20, 10:22): "me la tiene q pasar ariel"
   →
   - Jugadas: `anotar_quien_destraba`, con Ariel. Se guarda el mensaje a Ariel, a las 10:32.

3. **Leda**, por su cuenta, a Ariel (martes 20, 10:32): la pregunta.

4. **Ariel** escribe (martes 20, 11:00): "te la paso el jueves"
   →
   - Jugadas: `decir_cuando_destraba` sobre la tarea del PLC, para el jueves 22.
   - Efecto: queda anotado; el aviso a Marcos sale a las 11:10.

5. **Leda**, por su cuenta, a Marcos (martes 20, 11:10): lo que dijo Ariel.

6. **Ariel** escribe (jueves 22, 16:00): "se me complico con otra cosa, no llego, la tengo el lunes"
   →
   - Jugadas: `decir_cuando_destraba` sobre la tarea del PLC, para el lunes 26, con sus palabras.
   - Efecto: queda anotado; el aviso a Marcos sale a las 16:10.

7. **Leda**, por su cuenta, a Marcos (jueves 22, 16:10): lo que dijo Ariel.

8. **Marcos** escribe (lunes 26, 10:20): "el hmi tambien esta parado, ariel tiene q liberar la licencia"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del panel HMI, con su causa, y `anotar_quien_destraba`,
     con Ariel. Se guarda el mensaje a Ariel, a las 10:30.

9. **Leda**, por su cuenta, a Ariel (lunes 26, 10:30): la pregunta por el panel HMI.

10. **Ariel** escribe (lunes 26, 10:45): "la licencia la libero hoy a la tarde"
    →
    - Jugadas: `decir_cuando_destraba` sobre la tarea del panel HMI, para el lunes 26.
    - Efecto: queda anotado; el aviso a Marcos sale a las 10:55.

11. **Leda**, por su cuenta, a Marcos (lunes 26, 10:55): lo que dijo Ariel del panel HMI.
    - El bloqueo del PLC lleva cuatro días hábiles: nada sale por él.

12. **Marcos** escribe (lunes 26, 15:00): "listo ya tengo la licencia sigo con el hmi"
    →
    - Jugadas: `destrabar` sobre la tarea del panel HMI.
    - Efecto: el bloqueo del panel HMI se cierra.

13. **Leda**, por su cuenta, a Ismael (martes 27, 10:00): el bloqueo del PLC lleva cinco días hábiles.
    →
    - Efecto: un mensaje privado a Ismael, informativo; queda registrado que el bloqueo se le informó a
      Ismael, ese día.
    - El mensaje dice: que Marcos está trabado con la tarea del PLC desde el martes 20 (mar 20/10),
      hace cinco días hábiles, porque le falta la IP del servidor de CoreLabs; la historia: Marcos dijo
      que se la pasa Ariel; Ariel dijo que el jueves (jue 22/10) y después que el lunes (lun 26/10),
      porque se le complicó; que no hace falta responder.
    - El mensaje no dice: una pregunta; que Ismael tenga que hacer algo; nada del panel HMI.

14. **Ismael** escribe (martes 27, 10:40): "y eso quien lo tiene q resolver?"
    →
    - Jugadas: ninguna de la lista.
    - La respuesta dice: que lo destraba Ariel, que dio el lunes 26 y todavía no lo resolvió.

15. **Leda**, por su cuenta (miércoles 28, 10:00): nada. El bloqueo del PLC ya se informó: no se informa
    otra vez.

## Qué mide

- **Garantías (5b):** el bloqueo viejo se informa una sola vez y no antes de los cinco días hábiles; uno
  que se cerró o que es más nuevo no se informa; el aviso no pide nada; no inventa una fecha que nadie
  dio; la historia dice lo que dijo cada uno, con sus fechas.
- **Falla de comprensión:** que la IA cuente las fechas que dio Ariel como si se hubieran cumplido, o
  que no responda con lo que ya informó cuando Ismael pregunta.
