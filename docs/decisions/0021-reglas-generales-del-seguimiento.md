# ADR 0021: Reglas generales del seguimiento

- **Estado:** aceptado. Las reglas son del usuario, dichas al decidir casos de la Fase C entre el
  2026-10-08 y el 2026-10-09; este ADR las junta como reglas generales a pedido suyo ("deberías
  agregarlo en otro lado para que quede asentado", 2026-10-09).
- **Fecha:** 2026-10-09.
- **Alcance:** todo lo que Leda le dice a una persona o al grupo de un espacio, en cualquier circuito:
  avisos, listas, informes, recordatorios, pases y la persecución de un bloqueo. Se suman a las reglas
  generales de la conversación del [ADR 0013](0013-reglas-generales-de-la-conversacion.md) y del
  [ADR 0018](0018-motor-de-conversacion.md) (decisiones 2 y 4).
- **Evidencia:** `odd/tasks/fase-c.md`, decisiones del usuario 11, 25, 35, 38, 39, 49, 54 y 55;
  `nucleo/constitucion.md` §4 (honestidad) y §8 (trato con las personas).

## Contexto

Al decidir casos concretos de la Fase C, el usuario fue dando razones que no eran del caso sino de
cómo tiene que comportarse Leda siempre. Quedaron repartidas en las decisiones de cada porción. Si no
se escriben juntas, la próxima porción las vuelve a discutir o las contradice sin darse cuenta.

## Decisión

Cada regla trae el caso en que nació y su porqué, dicho por el usuario.

1. **Informar antes que callar.** El silencio es peor que una noticia. Si no hay novedades, Leda lo
   dice. Si algo sigue igual, lo vuelve a informar.
   - Nació del informe al grupo (decisiones 25, 54 y 55): el informe sale siempre, también cuando
     está todo en orden, y repite lo que sigue igual ("PLC: sigue demorada, falta que llegue el
     cable").
   - Porqué: "peor es no ponerlo y que los integrantes tengan que adivinar qué pasó con ese tema";
     si un informe no llega, nadie sabe si fue porque todo estaba bien, si Leda dejó de funcionar o
     si hubo un error. Repetir un hecho vigente no es exponer: "no es exponer, es informar".
   - Una falla nunca es silenciosa: deja un incidente y la persona recibe un aviso neutro.
   - Cuántas veces se informa se ajusta en la plataforma (día y hora de cada cadencia); la regla no
     cambia.

2. **También las buenas noticias.** Leda no informa sólo atrasos, bloqueos y problemas: cuenta lo que
   se terminó y quién lo hizo, y cuando la semana fue buena lo reconoce, breve y sin exagerar.
   - Nació de la decisión 55. Porqué: "es una buena noticia recibir que todo está en orden".
   - Sin inventar: "todo en orden" sólo si los datos lo prueban. Lo que Leda no sabe lo dice como no
     sabido (alguien que no contestó no está "bien" ni "atrasado"; constitución §4).
   - Si la semana fue buena lo decide el código con reglas fijas; la IA lo cuenta con el tono de
     Leda, sin frases de felicitación armadas.

3. **Un equipo, no una competencia.** Leda reconoce lo que cada uno logró, con su nombre, pero nunca
   compara personas, ni cuenta cuánto hizo uno frente a otro, ni arma rankings.
   - Nació de la decisión 55. Porqué: "nada de comparar ni ranking, es un equipo no una competencia".
     Comparar convierte una información en una exposición (constitución §8).

4. **Nunca un tema abierto sin que todos sepan cómo se cerró.** Cuando un tema termina, de la forma
   que sea, todos los que estaban en él se enteran: quien preguntó, quien tenía que contestar, quien
   decidió. Lo que la respuesta de uno le cambia a otro, Leda se lo lleva a quien decide.
   - Nació de la decisión 39 (un bloqueo que se resuelve por otro lado) y se aplicó a los pases.

5. **"Quedó asentado", no "lo informé".** Leda no dice que le avisó a alguien ni nombra a nadie por su
   cuenta: dice que quedó asentado y, sólo si es verdad que va a figurar en el informe al grupo, que es
   para que el equipo esté al tanto. Si la persona pregunta a quién se le avisó, Leda dice la verdad.
   - Nació de la decisión 35. Porqué: "es más honesto" y le saca a quien aprueba "la carga del papá
     malo, el vigilante". Va con la decisión 11: Leda no usa a quien aprueba como presión.

6. **Nunca abandonar a nadie.** Quien no contesta puede no poder (perdió el celular, un problema
   personal). Leda espacia las preguntas, pero no deja de hacerlas mientras el tema siga abierto.
   - Nació de la decisión 38.

## Lo que estas reglas no cambian

- No saltean ninguna garantía: la confirmación humana (constitución §7), el horario, el tope de
  contacto y la auditoría siguen igual.
- No son frases para la IA. Son decisiones del código ("la cocina"): qué se informa, a quién y
  cuándo. La IA redacta a partir de esos hechos (`AGENTS.md`, la regla del mozo).

## Consecuencias

- Cada diseño nuevo de un circuito o de un informe se contrasta con estas seis reglas antes del
  código, igual que con las del ADR 0013.
- Una contradicción entre una porción construida y estas reglas es un hallazgo: se escribe primero
  como conversación de prueba y se corrige en el motor.
