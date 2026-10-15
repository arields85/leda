# ADR 0025: Más tiempo y cambio de fecha: un pedido que decide quien revisa, con su informe de "en qué afecta"

- **Estado:** Propuesta (2026-10-15, de noche, redactada por el agente trabajando solo). Las decisiones son
  del usuario (2026-10-14, J5-D1 a J5-D8, y las decisiones 5 a 7 de la J3, en
  `odd/tasks/plataforma-jerarquias.md`); los doce puntos que esas decisiones no fijan están abiertos, con la
  recomendación del agente, en "Para decidir al despertar" ("J5: lo que las decisiones no alcanzan a fijar").
  Se acepta cuando el usuario conteste esos puntos; hasta entonces no se construye nada de conversación.
- **Fecha:** 2026-10-15.
- **Alcance:** qué pasa cuando una tarea necesita más tiempo o cambia su fecha, por el chat y por la web, y la
  fecha prevista de los objetivos ("> aceptar la demora").
- **Enmienda:**
  - el [ADR 0018](0018-motor-de-conversacion.md), 9a y 9i: una fecha **más tarde** que dice quien hace la
    tarea deja de anotarse directo y de mover el seguimiento; pasa a ser un pedido. Una fecha más temprana
    se sigue anotando directo (punto abierto 1);
  - el [ADR 0022](0022-plataforma-web-de-tareas.md), decisión 8: aceptar más tiempo **no cambia** la fecha
    comprometida; anota la fecha prevista (decisión 4, abajo). Cambiar la fecha es otra acción
    (decisión 5).
- **No cambia:** quién revisa una tarea (ADR 0023 y la J4), la escalera de recordatorios (mecánica §9),
  el circuito de lo que falta de otro (`motor/persecucion.py`), la confirmación humana de todo efecto
  (constitución §7) y la auditoría (§12).
- **Evidencia:** el código de hoy (`fichas._anotar_prevision`, `task_forecast`, `ancla.anclaje`,
  `bloquear_estado_directo` en `db/esquema.sql`, que hoy no deja cambiar una fecha; el molde
  `cambio_de_responsable` y `aplicar_cambio_de_responsable`) y la conversación de prueba 02, que prueba el
  comportamiento de hoy.

## Contexto

Hoy, si Nahuel dice "lo termino el 28" de una tarea que vence el 21, Leda lo anota como previsión, le avisa
a Marcos y los recordatorios pasan al 28 (ADR 0018, 9i). El usuario lo cambió (2026-10-14): si un integrante
corre la fecha solo, el plan del referente se mueve sin que nadie lo decida. Además, "trabado" no dice que la
demora depende de otro: una cosa es que falte algo de otra persona y otra que el trabajo propio lleve más.
Y todo cambio de plazo tiene que mostrar antes a quién afecta ("si no, no tiene ningún sentido").

## Decisiones

1. **Dos caminos distintos** (J5-D1), por el chat y por la web:
   - **"> Me falta algo para seguir"**, cuando la demora depende de otro ("no llegó el cable"): es el
     circuito que ya existe de lo que falta, quién se ocupa y la persecución. La demora no es de quien espera.
   - **"> pedir más tiempo"**, sólo cuando la demora es del propio trabajo: ése es el pedido que alguien
     decide. Si se pide más tiempo con un motivo que es de otro, Leda pregunta si le falta algo.
2. **Decide quien revisa la tarea** (J5-D2), con la regla de la J4: si Lucas lo pide, decide Martín. Un
   referente en una tarea suya, o Dirección en una propia, lo cambia sin pedido; Leda lo anota con la fecha
   original y la prevista. Si la fecha nueva pasa la del objetivo, Leda frena, avisa que el objetivo se
   demoraría y lo aprueba además el referente del objetivo; hasta entonces no corre.
3. **Todo pedido de un integrante lo decide su referente**, de 1 o de 10 días (J5-D3). Hasta que decide vale
   la fecha original y los recordatorios siguen sobre ella. El umbral del pack (`corrimiento_de_fecha_dias`)
   no se usa para esto.
4. **"En qué afecta", antes de decidir, en todo cambio de plazo** (J5-D3b y D3c): qué tareas esperan a ésta
   y cómo se correrían, con su responsable, y si llegan justo o se atrasan; si se pasa la fecha de un
   objetivo y quién lo aprueba; o "No demora a nadie más". Va dentro del pedido, antes de "aceptar" o "no";
   y, cuando no hace falta pedido, en la vista previa antes de confirmar. Lo reciben quien decide y los
   referentes de las tareas afectadas; Dirección, sólo si toca la fecha de un objetivo o una cadena que
   cruza áreas. Es una sola regla, en la base, para el chat y para la web.
5. **Aceptar no borra la fecha original** (J5-D4 y decisión 7): queda como compromiso y se anota la fecha
   prevista, con el motivo, quién la aceptó y cuándo. Leda sigue la prevista; la web muestra las dos: "21/10
   → previsto 28/10, aceptado por Marcos: era más trabajo".
6. **Cambiar la fecha cuando cambió el plan** (J5-D5): quien revisa la tarea y Dirección, con "> cambiar la
   fecha", motivo obligatorio y el informe antes de confirmar. La fecha nueva pasa a ser el compromiso, sin
   previsto ni atraso; la anterior queda en el historial. Al responsable le llega el aviso, y si se la
   adelantan, se lo dice claro. En la base es un registro que no se edita ni se borra
   (`cambio_de_fecha`, con el molde de `cambio_de_responsable`): la fecha de una tarea sólo cambia así.
7. **Decir que no lleva motivo y le llega a quien pidió** (J5-D6): "Marcos no aceptó pasar la tarea al 28: la
   necesita para la auditoría del 22. Sigue para el 21/10."
8. **Un pedido sin contestar se recuerda a quien decide, sin escalar, y nunca se acepta solo** (J5-D7); a
   quien pidió le dice que su pedido sigue esperando.
9. **Un pedido nuevo reemplaza al pendiente** (J5-D8, con la J6-D4): a quien decide le llega uno solo, con su
   informe, sin "antes había pedido". Nunca se decide sobre un pedido viejo.
10. **Los objetivos tienen fecha prevista** (decisiones 5 a 7 de la J3): "> aceptar la demora" de un objetivo
    hijo o de una tarea de Dirección deja la fecha del objetivo como compromiso y anota la prevista, con su
    motivo, quién lo decidió y por qué tarea u objetivo; hacia arriba, igual. Sólo Dirección y la
    administración.
11. **Las palabras:** en todo lo que ve la persona no se dice "trabado" ni "bloqueada" (la forma en el chat
    está abierta en "Para decidir"). Los nombres internos no cambian.

## Consecuencias

- La conversación 02 y las que usan `anotar_prevision` con una fecha más tarde cambian: se reescriben como
  conversaciones de prueba antes del código (conversaciones 56 a 62, plan en el documento de la unidad).
- La base necesita: el cambio de fecha auditado; el pedido con su estado (esperando, aceptado, no
  aceptado, reemplazado, ya no hace falta), uno pendiente por tarea; la previsión aceptada con quién y por
  qué pedido; la fecha prevista de los objetivos; y la función de "en qué afecta".
- Cada pieza nueva de la base lleva `security definer` con propietario explícito, `search_path` fijo, RLS
  forzado, su rollback, la paridad con `esquema.sql` y su fila de auditoría.
- Puntos abiertos: los doce de "Para decidir al despertar".
