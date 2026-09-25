# ADR 0007: Prisma orienta, no charla

- **Estado:** aceptada (usuario, 2026-09-25)
- **Fecha:** 2026-09-25
- **Alcance:** toda respuesta de Prisma que espera algo de la persona, en chat privado
- **Amplía:** [`ADR 0005`](0005-interpretacion-y-confirmacion.md), punto 4
- **Evidencia:** [`architecture/interpretacion-y-confirmacion.md`](../architecture/interpretacion-y-confirmacion.md), §5.13 (primera sesión por Telegram real)

## Decisión

1. **Cada respuesta que espera algo de la persona cierra con opciones concretas como
   botones,** no con una pregunta abierta. Siempre hay una salida, "Quiero consultar
   otra cosa", y escribir libremente sigue siendo posible en cualquier momento.
2. **Si Prisma nombra opciones, esas opciones son botones.** El texto da el contexto;
   la elección se hace tocando. "¿Cuál querés ver, el Dashboard de lotes o la
   Integración de datos?" se escribe como "Tenés dos tareas abiertas:" y dos botones.
3. **Una lista de tareas se ofrece como botones.** Tocar una tarea abre lo que se
   puede hacer con ella según su estado y la autoridad de quien toca: ver el detalle,
   avisar un avance, informar un bloqueo, pasarla a revisión. Lo que la persona no
   puede hacer no se ofrece.
4. **Un botón lleva la entidad resuelta por el servidor.** Tocar una tarea la
   identifica por su id: no hay referencia que interpretar ni consulta a Jev. Si el
   toque lleva a un cambio, termina en la vista previa de siempre (ADR 0005, punto 1).
5. **El modelo no pregunta con texto abierto.** Cuando necesita una elección, la pide
   al servidor con sus opciones y el servidor arma los botones con la salida del
   punto 1. Las opciones que son tareas o personas se validan contra PostgreSQL antes
   de mostrarse; el modelo no inventa candidatos.
6. **Una suposición no se presenta como hecho.** Si el modelo infiere algo que no está
   en los datos (que una tarea depende de otra, por ejemplo), lo ofrece como opción
   para confirmar, no lo afirma.

## Por qué

En la primera sesión por Telegram real, las preguntas abiertas de Prisma fueron el
origen de casi todos los problemas: "¿Querés que vea si alguna depende de otra?"
recibió "si, revisa", que el modelo completó con una dependencia inventada ("claramente
va detrás"); "decime y la paso a revisión" obligó a escribir y abrió otra aclaración;
"¿Qué querés cambiar?" recibió "la tarea", que se interpretó como el nombre de una
tarea y ofreció tres al azar. En los tres casos Prisma ya conocía las opciones.

Las 3 aclaraciones con botones de la sesión fueron innecesarias: la persona hablaba de
una tarea que Prisma acababa de listar. Con la lista como botones, la referencia no
existe: el toque ya dice cuál es.

## Alternativas consideradas

- **Mejorar la interpretación del texto libre** (hilo de la conversación para Jev,
  filtro de tareas propias, referencias genéricas fuera de Jev): reduce errores, pero
  sigue interpretando algo que podía no hacer falta interpretar. Se mide igual, como
  complemento, para los mensajes que la persona escribe por su cuenta.
- **Un menú fijo, sin conversación:** más predecible, pero rígido; la persona tiene
  que poder escribir lo que quiera, y Prisma interpretarlo.

## Consecuencias

- **Más mensajes con botones y menos interpretación.** El texto libre queda para lo
  que la persona inicia por su cuenta y para "Quiero consultar otra cosa".
- **Límites de Telegram:** los botones se cortan en el celular. Etiquetas cortas,
  hasta cuatro opciones más la salida (diseño §7, "Cantidad de botones"); con más
  opciones, se agrupan o se piden en dos pasos.
- **Los botones vencen** como cualquier `pending_action`; tocar uno vencido explica que
  venció y vuelve a ofrecer las opciones vigentes.
- **Se mide en una segunda sesión por Telegram,** contando preguntas que la persona
  considera innecesarias y respuestas vagas que hubo que interpretar.

## Pendiente

- Qué acciones ofrece cada estado de tarea y para qué roles.
- Si una respuesta puede cerrar sin opciones (un aviso que no espera nada).
- Cómo se ven las opciones en el grupo de gestión, fuera del chat privado.
