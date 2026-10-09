# 35. Bloqueos encadenados

**Qué prueba:** los bloqueos se enlazan solos (Marcos ← Ariel ← Lucas). Marcos está trabado esperando
algo de Ariel, y Ariel, a quien Leda le pregunta, está trabado a su vez con la tarea que destraba la de
Marcos. Leda no le pregunta más a Ariel por lo de Marcos y sigue con quien destraba a Ariel; Marcos, que
está más lejos, se entera de cada avance del medio con avisos informativos que no piden respuesta:
que Ariel se trabó, la fecha que da Lucas, que Lucas ya lo resolvió y que Ariel pudo seguir. Con otra
cadena, el enlace lo dice quien destraba ("sigo parado con lo mío"), sin una dependencia cargada.
Decisión 6 del usuario (`odd/tasks/fase-c.md`, 2026-10-08); ADR 0017, decisión 3a; mecánica §4 y §8.

**Corre desde la porción 4 de la C-5** (`odd/tasks/fase-c.md`), entera, con su YAML.

## La regla (decidida por el usuario, 2026-10-08)

1. **Los bloqueos encadenados se enlazan solos** (Marcos ← Juan ← Pedro).
2. **Leda avisa hacia abajo al destrabar.**
3. **Quien está más lejos se entera de todo avance del medio con avisos informativos que no piden
   respuesta** (llegó el repuesto, Juan da fecha, Juan terminó): "son mensajes informativos y aportan
   mucho".

Cómo se leyó lo que la regla no dice (`PENDIENTE` del usuario, en `odd/tasks/fase-c.md`, C-5):

- **Cuándo se enlazan:** el bloqueo de Marcos lo destraba Ariel, y Ariel tiene trabada la tarea que es
  lo que le falta a Marcos: la que tiene cargada como previa de la de Marcos (una dependencia, la
  estructura que viene de la plataforma), o la que Ariel nombra al contestar que está trabado con algo
  suyo. Nunca por adivinar: sin una de las dos, no hay enlace.
- **Lo que pregunta Leda a quien se trabó:** al trabarse Ariel con lo que destraba a Marcos, su
  respuesta a "para cuándo" ya está dada (está trabado): esa pregunta se cierra, y Leda sigue con quien
  destraba a Ariel, como con cualquier bloqueo.
- **Los avances del medio:** que se trabó (con qué y quién lo destraba), lo que dice quien lo destraba,
  que pudo seguir, un día nuevo para terminar, que la entregó y que quedó terminada. Le llegan a cada
  persona trabada que espera, más abajo en la cadena, salvo a quien lo dijo; son de coordinación (fuera
  del tope diario) y salen terminado el margen para corregir, como todo lo que alguien dice.
- **A quien le toca directo** (Ariel, con lo que dice Lucas de la tarea de Ariel) le llega lo de
  siempre (conversación 32); el aviso de un avance es para quienes están más abajo.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tarea de Marcos** (OT; aprueba su trabajo Ismael): "Programar PLC de la comprimidora": vence el
  viernes 30; `en_curso` desde el lunes 19; sin bloqueos. **Depende de** "Configurar el servidor de
  CoreLabs de la comprimidora" (una dependencia bloqueante, cargada por la plataforma).
- **Tarea de Ariel De Simone** (Software e interfaz HMI): "Configurar el servidor de CoreLabs de la
  comprimidora": vence el viernes 6 de noviembre; `en_curso` desde el lunes 19; sin bloqueos.
- **Tarea de Mariano Naim** (Sistemas eléctricos y tableros): "Armar el tablero eléctrico de la
  comprimidora": vence el viernes 30; `en_curso` desde el lunes 19; sin bloqueos.
- **Tarea de Nahuel Gimenez** (OT; aprueba su trabajo Marcos): "Dibujar los planos eléctricos de la
  comprimidora": vence el viernes 30; `en_curso` desde el lunes 19; sin bloqueos. No depende de nada
  cargado.
- **Lucas Natuche** (Infraestructura IT) tiene un chat con Leda y ninguna tarea en esta conversación.
- **Estado de la conversación** de todos: sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada en la semana.

## Hilo

1. **Marcos** escribe (martes 20, 10:20): "estoy trabado con el plc me falta la ip del servidor de
   corelabs"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del PLC, con su causa.
   - Efecto: un bloqueo abierto en la tarea del PLC; la tarea pasa a `bloqueada`.
   - La respuesta dice: que quedó anotado; una sola pregunta: quién lo puede destrabar.

2. **Marcos** escribe (martes 20, 10:22): "me la tiene q pasar ariel"
   →
   - Jugadas: `anotar_quien_destraba`, con Ariel.
   - Efecto: queda anotado que lo destraba Ariel; se guarda el mensaje a Ariel, que sale a las 10:32.
   - La respuesta dice: que Leda le pregunta a Ariel y le avisa apenas sepa algo.

3. **Leda**, por su cuenta, a Ariel (martes 20, 10:32): la pregunta.
   →
   - Efecto: un mensaje privado a Ariel; su pregunta abierta sobre la tarea del PLC, con su espera.

4. **Ariel** escribe (martes 20, 11:00): "todavia no la tengo, estoy parado con el servidor xq falta
   el switch nuevo, lo pone lucas"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del servidor, con su causa, y `anotar_quien_destraba`,
     con Lucas.
   - Efecto: un bloqueo abierto en la tarea del servidor, que pasa a `bloqueada`, y que lo destraba
     Lucas, dicho por Ariel. Los dos bloqueos quedan enlazados (la tarea del PLC depende de la del
     servidor y la destraba Ariel): la pregunta de Ariel sobre la tarea del PLC y su espera se
     cierran. Se guardan el mensaje a Lucas y el aviso a Marcos de que Ariel se trabó, los dos a las
     11:10.
   - La respuesta dice: que quedó anotado que está trabado y que lo destraba Lucas; que Leda le
     pregunta a Lucas; que Marcos se va a enterar.
   - La respuesta no dice: una pregunta por la tarea del PLC.
   - Estado después (Ariel): sin tema abierto.

5. **Leda**, por su cuenta (martes 20, 11:10):
   →
   - A Lucas: la pregunta por la tarea del servidor de Ariel (quién está trabado, qué le falta y para
     cuándo lo puede resolver).
   - A Marcos, informativo: que Ariel, que tiene que pasarle la IP, está trabado con la tarea del
     servidor porque falta el switch nuevo, y que lo destraba Lucas; que no hace falta responder.

6. **Lucas** escribe (martes 20, 11:30): "el switch llega el jueves, a la tarde lo dejo andando"
   →
   - Jugadas: `decir_cuando_destraba` sobre la tarea del servidor, para el jueves 22, con sus palabras.
   - Efecto: queda anotado lo que dice Lucas; se guardan el aviso a Ariel con lo que dijo Lucas (lo de
     siempre) y el aviso a Marcos de ese avance del medio, los dos a las 11:40.
   - La respuesta dice: que quedó anotado; que Ariel se va a enterar.

7. **Leda**, por su cuenta (martes 20, 11:40):
   →
   - A Ariel, informativo: que Lucas dice que deja el switch andando el jueves (jue 22/10) a la tarde.
   - A Marcos, informativo: lo mismo, como un avance de lo que espera su tarea (la del servidor de
     Ariel); que no hace falta responder.

8. **Lucas** escribe (jueves 22, 15:00): "listo ya quedo instalado el switch"
   →
   - Jugadas: `decir_cuando_destraba` sobre la tarea del servidor, que ya está.
   - Efecto: queda anotado; se guardan el aviso a Ariel y el aviso a Marcos, a las 15:10. El bloqueo
     de Ariel sigue abierto: lo cierra Ariel.

9. **Leda**, por su cuenta (jueves 22, 15:10):
   →
   - A Ariel: que Lucas dice que ya está; que cuando pueda seguir, lo diga.
   - A Marcos, informativo: que Lucas dice que el switch ya está instalado; que no hace falta responder.

10. **Ariel** escribe (jueves 22, 15:30): "buenisimo ya sigo con el servidor"
    →
    - Jugadas: `destrabar` sobre la tarea del servidor.
    - Efecto: el bloqueo del servidor se cierra y la tarea vuelve a `en_curso`; se guarda el aviso a
      Marcos de que Ariel pudo seguir, a las 15:40.
    - La respuesta dice: que quedó anotado; que Marcos se va a enterar.

11. **Leda**, por su cuenta, a Marcos (jueves 22, 15:40): informativo, que Ariel ya pudo seguir con la
    tarea del servidor; que no hace falta responder.
    - El mensaje no dice: que la tarea del PLC se destrabó.

12. **Ariel** escribe (jueves 22, 15:45): "la ip se la paso a marcos mañana temprano"
    →
    - Jugadas: `decir_cuando_destraba` sobre la tarea del PLC, para el viernes 23.
    - Efecto: queda anotado; se guarda el aviso a Marcos con lo que dijo (lo de siempre), a las 15:55.

13. **Leda**, por su cuenta, a Marcos (jueves 22, 15:55): que Ariel dice que le pasa la IP mañana
    (vie 23/10) temprano; que cuando pueda seguir, lo diga.

**La otra cadena: el enlace lo dice quien destraba.**

14. **Mariano** escribe (viernes 23, 10:20): "estoy parado con el tablero me faltan los guardamotores,
    los pide lucas"
    →
    - Jugadas: `anotar_bloqueo` sobre la tarea del tablero, con su causa, y `anotar_quien_destraba`, con
      Lucas.
    - Efecto: el bloqueo y quién lo destraba; se guarda el mensaje a Lucas, a las 10:30.

15. **Leda**, por su cuenta, a Lucas (viernes 23, 11:15): la pregunta por el tablero de Mariano.

16. **Nahuel** escribe (viernes 23, 10:45): "estoy trabado con los planos necesito el tablero armado,
    eso lo tiene mariano"
    →
    - Jugadas: `anotar_bloqueo` sobre la tarea de los planos, con su causa, y `anotar_quien_destraba`,
      con Mariano.
    - Efecto: el bloqueo y quién lo destraba; se guarda el mensaje a Mariano, a las 10:55.

17. **Leda**, por su cuenta, a Mariano (viernes 23, 10:55): la pregunta por los planos de Nahuel.

18. **Mariano** escribe (viernes 23, 11:15): "no puedo hasta tener los guardamotores, sigo parado con el
    tablero"
    →
    - Jugadas: `decir_cuando_destraba` sobre la tarea de los planos, diciendo que está trabado con la
      tarea del tablero (una tarea suya), con sus palabras.
    - Efecto: queda anotado lo que dice, con el enlace: lo que le falta a Nahuel espera el bloqueo del
      tablero de Mariano. Se guarda el aviso a Nahuel, a las 11:25, con lo que dijo y con qué está
      trabado Mariano (los guardamotores, que pide Lucas).
    - La respuesta dice: que quedó anotado; que Nahuel se va a enterar.

19. **Leda**, por su cuenta, a Nahuel (viernes 23, 11:25): que Mariano no puede hasta tener los
    guardamotores, que está trabado con el tablero y que eso lo destraba Lucas; que no hace falta
    responder.

20. **Lucas** escribe (viernes 23, 11:40): "los guardamotores llegan el lunes"
    →
    - Jugadas: `decir_cuando_destraba` sobre la tarea del tablero, para el lunes 26.
    - Efecto: queda anotado; se guardan el aviso a Mariano (lo de siempre) y el aviso a Nahuel de ese
      avance del medio, los dos a las 11:50.

21. **Leda**, por su cuenta (viernes 23, 11:50):
    →
    - A Mariano: que Lucas dice que los guardamotores llegan el lunes (lun 26/10).
    - A Nahuel, informativo: lo mismo, como un avance de lo que espera su tarea (el tablero de
      Mariano); que no hace falta responder.

## Qué mide

- **Garantías (5b):** nunca da por destrabada la tarea de Marcos porque se destrabó la de Ariel; no
  enlaza dos bloqueos sin una dependencia cargada o sin que lo diga quien destraba; no le pregunta a
  Ariel por lo de Marcos mientras está trabado con eso; ningún aviso del medio pide respuesta; nunca
  inventa una fecha que nadie dio; no le avisa a quien hizo el avance de su propio avance.
- **Falla de comprensión:** que la IA no tome "estoy parado con el servidor xq falta el switch nuevo,
  lo pone lucas" como un bloqueo de su tarea y quién lo destraba; o "sigo parado con el tablero" como
  lo que dice sobre los planos de Nahuel, con su tarea trabada.
