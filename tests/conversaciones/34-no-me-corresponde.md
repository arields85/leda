# 34. No me corresponde

**Qué prueba:** a quien Leda le pregunta por un bloqueo dice que no le corresponde. Leda le pregunta
quién se encarga y sigue con esa persona, como siguió con la primera: le escribe como Leda, y a quien
está trabado le cuenta lo que pasó, como información. La cadena llega hasta tres personas
preguntadas: si la tercera tampoco lo toma (no le corresponde, no sabe o nombra a otra), Leda no da
más vueltas. Antes de asentar un "ni idea", Leda le pregunta a quien está trabado si se le ocurre
otra persona; si no, queda asentado. Al cortarse, le informa la cadena entera a quien decide quién lo
resuelve, sin pedirle nada y nunca a alguien de la cadena; a quien está trabado le dice que quedó
asentado, sin decir que le informa a alguien ni nombrar a nadie por su cuenta. Decisión 5 del
usuario (`odd/tasks/fase-c.md`, 2026-10-08, opción A con límite), con su límite cambiado por la
decisión 51 (hasta tres personas) y las decisiones 24 (a quién va) y 49 (antes de asentar un "ni
idea"), del 2026-10-09; ADR 0017, decisión 3a, paso 4; ADR 0018, 9c, con la precisión del
2026-10-09 (el tercer aviso al referente, informativo); decisión 11 (no nombrar al referente por su
cuenta) y decisión 35 ("quedó asentado", no "lo informé").

**Corre desde la porción 3 de la C-5** (`odd/tasks/fase-c.md`), entera, con su YAML; desde la C-5d,
con las decisiones 24, 49 y 51.

## La regla (decidida por el usuario, 2026-10-08 y 2026-10-09)

1. **Leda le pregunta quién se encarga y sigue con esa persona.**
2. **La cadena llega hasta tres personas preguntadas** (decisión 51): Ariel dice que es de Mariano y
   Leda le pregunta a Mariano; Mariano dice que es de Pedro y Leda le pregunta a Pedro. Si Pedro se
   hace cargo, se resolvió; si no sabe, no le corresponde o nombra a otro, ahí se corta y queda
   asentado, con lo que dijo cada uno.
3. **Antes de asentar un "ni idea", Leda le pregunta a la persona trabada** (decisión 49) si se le
   ocurre otra persona; si nombra a alguien, sigue con esa persona; si no, queda asentado: en la
   historia de la tarea, le llega a quien decide quién lo resuelve, figura en el próximo informe al
   grupo y a la persona trabada se le dice con la forma de la decisión 35.
4. **A quién va lo asentado** (decisión 24): nunca a alguien que es parte de la cadena. Va al
   referente de la tarea trabada; si ése es la persona trabada o alguien de la cadena, a quien
   aprueba el trabajo de la persona trabada.

Cómo se leyó lo que la regla no dice (`PENDIENTE` del usuario, en `odd/tasks/fase-c.md`, C-5):

- **"No me corresponde" sin decir de quién,** mientras haya lugar en la cadena: Leda pregunta una
  vez quién se encarga, y la pregunta sigue abierta. Si contesta que no sabe, o vuelve a decir que
  no le corresponde sin nombrar a nadie, es un "ni idea". Con las tres personas ya preguntadas, no
  se pregunta: se corta.
- **Lo que contesta la persona trabada** cuando Leda le pregunta si se le ocurre otra persona sigue
  la misma cadena: cuenta para las tres.
- **A quien está trabado le llega cada paso como información:** que la primera dijo que le toca a otra
  y que Leda le pregunta a esa otra; y, al cortarse la cadena, lo que dijo la última y que quedó
  asentado (decisión 35; sin informe al grupo en esta conversación, nada del equipo). No le pide
  nada, salvo la pregunta de si se le ocurre otra persona.
- **El aviso a quien decide no pide nada:** es información, con el margen para corregir, como todo
  aviso a otra persona por algo que alguien dijo.

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
     Mariano y su espera se cierran. Es un "ni idea" con lugar en la cadena (dos personas
     preguntadas): todavía no se asienta. Se guarda un mensaje a Nahuel, que sale a las 11:50: lo
     que dijo Mariano y si se le ocurre otra persona que pueda destrabarlo.
   - La respuesta dice: que quedó anotado; que Nahuel se va a enterar.
   - La respuesta no dice: el nombre de Marcos; que se lo informa a alguien.

8. **Leda**, por su cuenta, a Nahuel (martes 20, 11:50):
   →
   - Efecto: un mensaje privado a Nahuel; abre su pregunta de quién lo destraba, con su espera.
   - El mensaje dice: que Mariano dice que no le corresponde y no sabe de quién es; una sola pregunta:
     si se le ocurre otra persona que pueda destrabarlo.

8b. **Nahuel** escribe (martes 20, 12:00): "no, no se me ocurre nadie"
   →
   - Jugadas: `anotar_quien_destraba`, sin saber quién.
   - Efecto: queda anotado que Nahuel no sabe; su pregunta y su espera se cierran. Queda asentado: se
     guarda el mensaje a Marcos, el referente de OT (no es parte de la cadena), con la cadena entera,
     que sale a las 12:10.
   - La respuesta dice: que quedó asentado; que cuando pueda seguir, lo diga.
   - La respuesta no dice: que Leda se lo informa a alguien, ni a quién (no lo preguntó); otras
     salidas.

8c. **Leda**, por su cuenta, a Marcos (martes 20, 12:10):
   →
   - Informativo: Nahuel está trabado con la tarea de los planos por la lista de componentes del
     tablero; dijo que la tenía Ariel, Ariel que la maneja Mariano, Mariano que no sabe, y Nahuel
     tampoco sabe de otra persona; para que determine quién lo resuelve. No le pide nada; que no hace
     falta responder.

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
    - Efecto: queda anotado que Martín dice que no le corresponde y que es de Mariano. Es la segunda
      persona preguntada: Leda sigue con Mariano, la tercera. Se guardan los mensajes a Mariano (la
      pregunta, diciendo que Martín lo nombró) y a Nahuel (lo que dijo Martín y que Leda le pregunta
      a Mariano), que salen a las 15:10.
    - La respuesta dice: que quedó anotado; que Leda le pregunta a Mariano.

15. **Leda**, por su cuenta (martes 20, 15:10): a Mariano, la pregunta; a Nahuel, lo que dijo Martín.

16. **Mariano** escribe (martes 20, 15:30): "no es mio, eso lo ve ismael"
    →
    - Jugadas: `decir_que_no_le_toca` sobre la tarea de la digitalización, con Ismael.
    - Efecto: queda anotado que Mariano dice que no le corresponde y que lo ve Ismael. Es la tercera
      persona preguntada: Leda no le escribe a Ismael. Queda asentado: se guardan los mensajes que
      salen a las 15:40: a Marcos, el referente de OT (la tarea trabada es de OT y Marcos no es parte
      de la cadena; nunca a Mariano, que dijo que no es suyo, aunque sea el referente de lo
      eléctrico), la cadena entera; a Nahuel, lo que dijo Mariano y que quedó asentado.
    - La respuesta dice: que quedó anotado; que Nahuel se va a enterar.
    - La respuesta no dice: el nombre de Marcos.

17. **Leda**, por su cuenta (martes 20, 15:40): a Marcos, la cadena (Nahuel dijo Lucas, Lucas dijo
    Martín, Martín dijo Mariano, Mariano dijo Ismael), informativa; a Nahuel, lo que dijo Mariano y
    que quedó asentado.

## Qué mide

- **Garantías (5b):** no le escribe a una cuarta persona de la cadena (el límite de tres); no asienta
  un "ni idea" sin preguntarle antes a la persona trabada, si hay lugar; no le pide nada a quien
  decide; lo asentado nunca le llega a alguien de la cadena; no nombra a quien decide por su cuenta
  ante quien está trabado; no da por cerrado ni destrabado nada; no le escribe a nadie en nombre de
  otra persona; no inventa de quién es lo que falta.
- **Falla de comprensión:** que la IA no tome "no me corresponde eso", "lo maneja mariano", "ni idea
  yo eso no lo manejo", "eso no es mio, lo ve martin" o "no es mio, eso lo ve ismael" como lo que
  dice quien destraba sobre que no le toca; que tome "lo maneja mariano" como para cuándo; o que no
  tome "no, no se me ocurre nadie" como que Nahuel no sabe quién lo destraba.
