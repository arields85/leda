# 36. El bloqueo viejo

**Qué prueba:** un bloqueo que sigue abierto a los cinco días hábiles se le informa al referente
aunque la cadena se mueva (quien lo destraba fue dando fechas): va con la historia entera y las
fechas que dio cada uno, sin pedirle nada. A la persona trabada se le dice, en un mensaje corto, que
quedó asentado y, como el espacio tiene informe al grupo, que es para que el equipo esté al tanto,
sin nombrar a quién le llegó. Mientras siga trabado, cada cinco días hábiles se vuelve a asentar,
con lo que pasó desde la vez anterior. Uno más nuevo, o uno que se cerró antes, no se informa.
Decisión 7 del usuario (`odd/tasks/fase-c.md`, 2026-10-08, opción A) y decisiones 34, 35 y 36
(2026-10-09, C-5a); mecánica §8 ("un bloqueo abierto hace más de [pack] días escala aunque nadie
lo pida").

**Corre desde la porción 5 de la C-5** (`odd/tasks/fase-c.md`), entera, con su YAML.

## La regla (decidida por el usuario, 2026-10-08)

1. **A los `bloqueos.escala_solo_a_los_dias` días hábiles** (5 en CoreWork, ajustable desde la
   plataforma) **Leda le informa al referente aunque la cadena se mueva, con la historia y las fechas
   dichas.**
2. "El silencio y no informar es peor que avisos informativos útiles."
3. **Se le cuenta a la persona trabada** (decisión 34, 2026-10-09): cuando Leda informa un bloqueo
   que lleva los días del espacio, se lo dice a la persona en un mensaje corto, con la forma de la
   decisión 35.
4. **"Quedó asentado", no "lo informé"** (decisión 35): Leda no dice que informó a alguien ni nombra
   a nadie por su cuenta; dice que quedó asentado y, sólo si es verdad que va a figurar en el
   informe al grupo del espacio, que es para que el equipo esté al tanto. Si la persona pregunta a
   quién se le avisó, Leda dice la verdad.
5. **Se vuelve a asentar mientras siga** (decisión 36): cada `bloqueos.escala_solo_a_los_dias` días
   hábiles mientras siga trabado, con lo que pasó desde la vez anterior.

Cómo se leyó lo que la regla no dice (`PENDIENTE` del usuario, en `odd/tasks/fase-c.md`, C-5):

- **A quién:** al referente del sector de la tarea trabada; si es la persona trabada misma (Marcos es
  el referente de OT), a quien aprueba su trabajo (Ismael), como la cadena de la conversación 34.
- **Cada vez**, a la hora en que Leda manda lo suyo, dentro del horario y sin interrumpir una
  conversación. Queda registrado a quién y cuándo se informó.
- **Es información:** no le pide nada, ni al referente ni a la persona trabada.
- **Los días se cuentan** desde que se anotó el bloqueo y, después, desde la vez anterior, en días
  hábiles del espacio.
- **"Va a figurar en el informe al grupo"** es un hecho del código: el espacio tiene su grupo y una
  cadencia al grupo, como CoreWork en el pack (`telegram.grupo_gestion_id` e `informe_semanal`).

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **El espacio** tiene su grupo y el informe semanal al grupo (viernes 16:15), como en el pack.
- **Tareas de Marcos** (OT, que tiene a Marcos como referente; aprueba su trabajo Ismael):
  - "Programar PLC de la comprimidora": vence el viernes 13 de noviembre; `en_curso` desde el lunes
    19; sin bloqueos.
  - "Instalar el panel HMI de la comprimidora": vence el viernes 13 de noviembre; `en_curso` desde el
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
    - **A Marcos**, a la vez, un mensaje corto e informativo: que quedó asentado que el PLC lleva cinco
      días hábiles trabado, para que el equipo esté al tanto; que no hace falta responder.
    - El mensaje a Marcos no dice: que se le informó a alguien; el nombre de Ismael; una pregunta.

14. **Ismael** escribe (martes 27, 10:40): "y eso quien lo tiene q resolver?"
    →
    - Jugadas: ninguna de la lista.
    - La respuesta dice: que lo destraba Ariel, que dio el lunes 26 y todavía no lo resolvió.

15. **Leda**, por su cuenta (miércoles 28, 10:00): nada. El bloqueo del PLC ya se informó: no se informa
    otra vez hasta dentro de cinco días hábiles.

16. **Ariel** escribe (jueves 29, 11:00): "todavia no la consegui, el lunes 2 sin falta"
    →
    - Jugadas: `decir_cuando_destraba` sobre la tarea del PLC, para el lunes 2, con sus palabras.
    - Efecto: queda anotado; el aviso a Marcos sale a las 11:10.

17. **Leda**, por su cuenta, a Marcos (jueves 29, 11:10): lo que dijo Ariel.

18. **Leda**, por su cuenta (lunes 2, 10:00): nada. Desde la vez anterior van cuatro días hábiles.

19. **Leda**, por su cuenta (martes 3, 10:00): el bloqueo del PLC lleva diez días hábiles y sigue
    abierto: se vuelve a asentar.
    →
    - A Ismael, informativo: que Marcos sigue trabado con la tarea del PLC desde el martes 20, hace
      diez días hábiles; lo que pasó desde la vez anterior (mar 27/10): Ariel dijo el jueves 29 que
      todavía no la consiguió y que el lunes 2 sin falta; que no hace falta responder.
    - El mensaje a Ismael no dice: una pregunta; la historia anterior al martes 27 como si fuera nueva.
    - A Marcos, informativo y corto: que volvió a quedar asentado que el PLC sigue trabado, ya diez
      días hábiles, para que el equipo esté al tanto; que no hace falta responder.
    - El mensaje a Marcos no dice: que se le informó a alguien; el nombre de Ismael.

## Qué mide

- **Garantías (5b):** el bloqueo viejo se asienta cada cinco días hábiles mientras siga abierto, nunca
  antes; uno que se cerró o que es más nuevo no se informa; los avisos no piden nada; no inventa una
  fecha que nadie dio; la historia dice lo que dijo cada uno, con sus fechas, y la segunda vez sólo lo
  que pasó desde la primera; a Marcos le llega cada vez, sin que se le nombre a nadie.
- **Falla de comprensión:** que la IA cuente las fechas que dio Ariel como si se hubieran cumplido;
  que no responda con lo que ya informó cuando Ismael pregunta; que a Marcos le diga que le informó
  a alguien, o que no diga que es para que el equipo esté al tanto.
