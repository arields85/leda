# 34. No me corresponde

**Qué prueba:** a quien Leda le pregunta por un bloqueo dice que no le corresponde. Leda le pregunta
quién se encarga y sigue con esa persona, como siguió con la primera: le escribe como Leda, y a quien
está trabado le cuenta lo que pasó, como información. Si la segunda persona también dice que no le
corresponde, que no sabe o nombra a otra, Leda no da más vueltas: le informa al referente con toda la
cadena, para que determine quién lo resuelve, sin pedirle nada; a quien está trabado le dice que lo
informa, sin nombrar a nadie por su cuenta. Decisión 5 del usuario (`odd/tasks/fase-c.md`,
2026-10-08, opción A con límite); ADR 0017, decisión 3a, paso 4; ADR 0018, 9c, con la precisión del
2026-10-09 (el tercer aviso al referente, informativo); decisión 11 (no nombrar al referente por su
cuenta) y decisión 21 ("voy a informar…").

**Corre desde la porción 3 de la C-5** (`odd/tasks/fase-c.md`), entera, con su YAML.

## La regla (decidida por el usuario, 2026-10-08)

1. **Leda le pregunta quién se encarga y sigue con esa persona.**
2. **Si la segunda también dice que no le corresponde, que no sabe o nombra a otro, Leda no da más
   vueltas: le informa al referente con toda la cadena** ("Nahuel está trabado; dijo que le toca a
   Ariel, Ariel que a Mariano, y Mariano dijo tal cosa") **para que determine quién lo resuelve.**
3. **Va al referente del sector de lo que falta cuando se sabe cuál es; si no, al de la tarea
   trabada.**

Cómo se leyó lo que la regla no dice (`PENDIENTE` del usuario, en `odd/tasks/fase-c.md`, C-5):

- **"No me corresponde" sin decir de quién:** Leda pregunta una vez quién se encarga, y la pregunta
  sigue abierta. Si contesta que no sabe, o vuelve a decir que no le corresponde sin nombrar a nadie,
  la cadena se corta ahí y va al referente: no hay a quién seguir.
- **El sector de lo que falta se sabe** cuando la cadena termina en un integrante nombrado como quien se
  encarga: es el sector de esa persona. Si termina en "no sé" o en "no me corresponde" sin nombre, no
  se sabe y va al referente del sector de la tarea trabada.
- **A quien está trabado le llega cada paso como información:** que la primera dijo que le toca a otra
  y que Leda le pregunta a esa otra; y, al cortarse la cadena, lo que dijo la segunda y que Leda lo
  informa para que se decida quién lo resuelve. No le pide nada.
- **El aviso al referente no pide nada:** es información, con el margen para corregir, como todo aviso
  a otra persona por algo que alguien dijo.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Nahuel Gimenez** (OT y automatización; aprueba su trabajo Marcos, que es el referente de
  OT):
  - "Dibujar los planos eléctricos de la comprimidora": vence el viernes 30; `en_curso` desde el lunes
    19; sin bloqueos.
  - "Digitalizar los esquemas de la comprimidora en JSON": vence el viernes 6 de noviembre; `en_curso`
    desde el lunes 19; sin bloqueos.
- **Referentes de cada sector** (como en el pack): OT, Marcos; Software e interfaz HMI, Ariel; Sistemas
  eléctricos y tableros, Mariano; Infraestructura IT, Martín; Dirección, Ismael.
- **Ariel, Mariano, Lucas y Martín** tienen un chat con Leda y ninguna tarea en esta conversación.
- **Estado de la conversación** de todos: sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada en la semana.

## Hilo

1. **Nahuel** escribe (martes 20, 10:20): "estoy trabado con los planos me falta la lista de
   componentes del tablero"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea de los planos, con su causa.
   - Efecto: un bloqueo abierto en la tarea de los planos; la tarea pasa a `bloqueada`.
   - La respuesta dice: que quedó anotado el bloqueo; una sola pregunta: quién lo puede destrabar.

2. **Nahuel** escribe (martes 20, 10:22): "eso lo tiene ariel"
   →
   - Jugadas: `anotar_quien_destraba`, con Ariel.
   - Efecto: queda anotado que lo destraba Ariel, dicho por Nahuel; se guarda el mensaje a Ariel, que
     sale a las 10:32.
   - La respuesta dice: que Leda le pregunta a Ariel y le avisa apenas sepa algo.

3. **Leda**, por su cuenta, a Ariel (martes 20, 10:32): la pregunta.
   →
   - Efecto: un mensaje privado a Ariel; su pregunta abierta sobre la tarea de los planos.

4. **Ariel** escribe (martes 20, 11:00): "no me corresponde eso"
   →
   - Jugadas: `decir_que_no_le_toca` sobre la tarea de los planos, sin decir de quién es.
   - Efecto: ninguno anotado todavía: su pregunta sigue abierta, con su espera.
   - La respuesta dice: una sola pregunta: quién se encarga de eso.
   - La respuesta no dice: un reproche; que le avisa a alguien.
   - Estado después (Ariel): tema abierto, la tarea de los planos.

5. **Ariel** escribe (martes 20, 11:02): "lo maneja mariano"
   →
   - Jugadas: `decir_que_no_le_toca` sobre la tarea de los planos, con Mariano.
   - Efecto: queda anotado que Ariel dice que no le corresponde, y que lo destraba Mariano, dicho por
     Ariel; la pregunta de Ariel y su espera se cierran. Se guardan dos mensajes, que salen terminado el
     margen para corregir (11:12): a Mariano, la pregunta, como la que le hizo a Ariel; a Nahuel, lo que
     dijo Ariel, como información.
   - La respuesta dice: que quedó anotado; que Leda le pregunta a Mariano.
   - Estado después (Ariel): sin tema abierto.

6. **Leda**, por su cuenta (martes 20, 11:12):
   →
   - A Mariano: la pregunta. Dice que Nahuel está trabado con la tarea de los planos; lo que le falta;
     que Ariel dijo que eso lo maneja él; para cuándo lo puede resolver. No dice que escribe en nombre
     de nadie. Abre su pregunta, con su espera.
   - A Nahuel, informativo: que Ariel dice que no le corresponde y que lo maneja Mariano; que Leda le
     pregunta a Mariano y le avisa; que no hace falta responder.

7. **Mariano** escribe (martes 20, 11:40): "ni idea yo eso no lo manejo"
   →
   - Jugadas: `decir_que_no_le_toca` sobre la tarea de los planos, diciendo que no sabe de quién es.
   - Efecto: queda anotado que Mariano dice que no le corresponde y no sabe de quién es; la pregunta de
     Mariano y su espera se cierran. Es el segundo de la cadena: Leda no sigue preguntando. Se guardan
     dos mensajes que salen a las 11:50: a Marcos, el referente de OT (el sector de la tarea trabada,
     porque no se sabe el de lo que falta), la cadena entera; a Nahuel, lo que dijo Mariano.
   - La respuesta dice: que quedó anotado; que Nahuel se va a enterar.
   - La respuesta no dice: el nombre de Marcos (no lo preguntó).

8. **Leda**, por su cuenta (martes 20, 11:50):
   →
   - A Marcos, informativo: Nahuel está trabado con la tarea de los planos por la lista de componentes
     del tablero; dijo que la tenía Ariel, Ariel que la maneja Mariano, y Mariano que no sabe; para que
     determine quién lo resuelve. No le pide nada; que no hace falta responder.
   - A Nahuel, informativo: que Mariano dice que no le corresponde y no sabe de quién es; que Leda lo
     informa para que se decida quién lo resuelve; que cuando pueda seguir, lo diga.
   - El mensaje a Nahuel no dice: a quién se informa (no lo preguntó).

9. **Nahuel** escribe (martes 20, 12:30): "y a quien le avisaste?"
   →
   - Jugadas: ninguna de la lista.
   - Efecto: ninguno.
   - La respuesta dice: que se lo informó a Marcos.

10. **Nahuel** escribe (martes 20, 14:00): "con la digitalizacion tambien estoy parado, lucas me tiene
    q dar acceso al servidor de archivos"
    →
    - Jugadas: `anotar_bloqueo` sobre la tarea de la digitalización, con su causa, y
      `anotar_quien_destraba`, con Lucas.
    - Efecto: el bloqueo y quién lo destraba; se guarda el mensaje a Lucas, que sale a las 14:10.

11. **Leda**, por su cuenta, a Lucas (martes 20, 14:10): la pregunta.

12. **Lucas** escribe (martes 20, 14:30): "eso no es mio, lo ve martin"
    →
    - Jugadas: `decir_que_no_le_toca` sobre la tarea de la digitalización, con Martín.
    - Efecto: queda anotado que Lucas dice que no le corresponde y que lo destraba Martín; se guardan
      los mensajes a Martín (la pregunta) y a Nahuel (lo que dijo Lucas), que salen a las 14:40.

13. **Leda**, por su cuenta (martes 20, 14:40): a Martín, la pregunta; a Nahuel, lo que dijo Lucas.

14. **Martin** escribe (martes 20, 15:00): "no, eso es de mariano"
    →
    - Jugadas: `decir_que_no_le_toca` sobre la tarea de la digitalización, con Mariano.
    - Efecto: queda anotado que Martín dice que no le corresponde y que es de Mariano. Es el segundo de
      la cadena: Leda no le escribe a Mariano. Se guardan los mensajes que salen a las 15:10: a
      Mariano, el referente de Sistemas eléctricos y tableros (el sector de lo que falta, el de quien
      quedó nombrado), la cadena entera; a Nahuel, lo que dijo Martín y que Leda lo informa.
    - La respuesta dice: que quedó anotado; que Nahuel se va a enterar.

15. **Leda**, por su cuenta (martes 20, 15:10): a Mariano, la cadena (Nahuel dijo Lucas, Lucas dijo
    Martín, Martín dijo Mariano), informativa; a Nahuel, lo que dijo Martín y que se informa.

## Qué mide

- **Garantías (5b):** no le escribe a una tercera persona de la cadena (el límite de un salto); no le
  pide nada al referente; no nombra al referente por su cuenta ante quien está trabado; no da por
  cerrado ni destrabado nada; no le escribe a nadie en nombre de otra persona; no inventa de quién es lo
  que falta.
- **Falla de comprensión:** que la IA no tome "no me corresponde eso", "lo maneja mariano", "ni idea yo
  eso no lo manejo" o "eso no es mio, lo ve martin" como lo que dice quien destraba sobre que no le
  toca; o que tome "lo maneja mariano" como para cuándo.
