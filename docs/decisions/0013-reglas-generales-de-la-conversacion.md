# ADR 0013: Reglas generales de la conversación

- **Estado:** aceptada
- **Fecha:** 2026-09-29
- **Alcance:** el camino de cada mensaje y de cada toque: `gateway` (`procesar_update`,
  `_turno`, `_toque`, los retomes de preguntas pendientes), `pendientes`,
  `ingreso_tareas`, `agente`, `contexto` y las herramientas que informan efectos.
- **Evidencia:** tercera ronda por Telegram (hallazgos R3-H5, H13, H15, H16, H17, H18,
  H19 y H20 en `odd/tasks/prisma-orienta.md`); mapeo de causas del 2026-09-29 por
  lectura de código; manual de personalidad, voz y comportamiento del usuario (§13-§16,
  §20, §27), contrastado con el corpus del repo.

## Contexto

Los hallazgos de la ronda 3 parecen distintos, pero son pocas clases de falla que se
repiten en caminos distintos:

- Cuando Prisma espera un dato, el mensaje siguiente se toma como ese dato sin
  interpretarlo: un "hola" quedó como evidencia (H17), y probablemente de ahí salieron
  dos respuestas para un mismo mensaje (H19).
- Hay caminos donde un mensaje no produce ninguna respuesta (H15: foto, archivo o audio)
  o produce dos (H19).
- Prisma deja la situación sin decir cómo quedó: evidencia registrada sobre una tarea
  que sigue en curso sin avisarlo (H20), el motivo de "Pedir cambios" invisible fuera de
  un aviso efímero (H16), opciones que el sistema no puede cumplir (H18).
- Un toque de botón no da ninguna señal mientras se procesa (H5) y el segundo toque
  responde con un error (H13).

Arreglar cada hallazgo por separado (por ejemplo, una lista de saludos que "no cuentan"
como dato) no termina nunca: las variantes de una conversación son infinitas. El manual
del usuario lo dice en §27: corregir el mecanismo general, no agregar frases especiales
ni palabras clave para que pase el caso conocido.

El reparto que sigue es el de siempre en Prisma: el modelo interpreta las variantes del
lenguaje; el código garantiza las invariantes.

## Decisión

Cuatro reglas generales. Cada una se implementa con un mecanismo en el código, no con
casos.

1. **Una pregunta pendiente es contexto, no una trampa.** Cuando Prisma espera un dato
   (la evidencia de una entrega, la causa de un bloqueo, su resolución, el motivo de
   "Pedir cambios", una corrección, un campo del alta de una tarea), el mensaje
   siguiente se interpreta. Se adopta el patrón probado de los asistentes de tareas
   (por ejemplo, los "conversation repair patterns" de Rasa): el modelo sólo traduce el
   mensaje a un **comando de una lista cerrada**, relativo a la pregunta pendiente, y el
   código ejecuta un manejo determinista por comando. El ruteo tipado recibe la pregunta
   pendiente y devuelve uno de estos comandos:
   - **responde**: el mensaje trae el dato; se consume la pregunta y sigue el camino del
     dato (con su validación y su vista previa de siempre).
   - **corrige**: cambia un dato o una propuesta anterior; se reconstruye la vista previa
     (el mismo camino que Modificar).
   - **cancela**: la persona deja lo pendiente; se cierra y se dice qué se dejó de lado.
   - **otro tema** (reemplazado por la enmienda del 2026-09-29, abajo): se atiende el
     mensaje por el camino normal y la pregunta queda abierta; al terminar, si la
     respuesta no dejó otra interacción pendiente, Prisma retoma dentro de la misma
     respuesta ("¿seguimos con …?") con botones.
   - **charla** (saludo, agradecimiento, algo fuera de tema): respuesta breve y la
     pregunta pendiente se vuelve a hacer; no se consume.
   - **dudoso**: una sola pregunta con botones para saber si el mensaje es el dato o es
     otra cosa.
   - **no puedo**: el mensaje pide algo que Prisma no puede hacer; lo dice una vez,
     ofrece la alternativa real si existe y la pregunta queda abierta.
   **Precisión (2026-09-29, banco real `b-0020`).** Al responder o corregir una
   pregunta pendiente, la tarea de esa pregunta es el sujeto por defecto. Jev sigue
   resolviendo las referencias del mensaje, y sólo una resolución clara cambia el
   sujeto (una corrección puede apuntar a otra tarea). Una referencia ambigua o sin
   resolver, como un sustantivo de la corrección ("el variador"), no abre una
   aclaración mientras se responde una pregunta pendiente: el turno sigue con el
   sujeto por defecto, como si esa referencia no estuviera. Y con `otro tema`, el
   responder sabe que hay una pregunta pendiente que el sistema retoma solo y no la
   vuelve a proponer por su cuenta.
   Ningún camino consume una pregunta pendiente sin ese comando. Los errores internos
   siguen el camino de siempre (regla 2). El modelo nunca decide el efecto: sólo el
   comando.

   **Enmienda (2026-09-29, decisión del usuario): una sola rama de conversación
   abierta.** No se abre una rama nueva de conversación hasta cerrar la que empezó.
   Una rama se cierra de tres maneras: se continúa (la persona da el dato), se cancela,
   o se deja para hacer otra cosa. Prisma dirige (ADR 0007): no atiende otro tema con
   una pregunta abierta. Evidencia: banco real `b-0021-c` y `b-0020`, donde la respuesta
   al otro tema traía sus propios botones, el retome no podía salir (un solo juego de
   botones por respuesta, regla 2) y la pregunta quedaba abierta sin que la persona lo
   supiera. Con esta enmienda, **otro tema** pasa a ser:
   - Prisma no atiende el mensaje todavía. Responde una sola pregunta con botones sobre
     lo pendiente, por ejemplo "Estábamos armando una tarea nueva y me falta el título.
     ¿Seguimos con eso?" con **[Seguir con la tarea]** y **[Dejarla y ver lo otro]** (la
     redacción final es de T10).
   - **Seguir**: vuelve a hacer la pregunta pendiente (una elección, con sus botones).
   - **Dejar y ver lo otro**: cierra lo pendiente por el mismo camino que `cancela` y,
     en la misma respuesta, atiende el mensaje que quedó guardado por el camino normal,
     sin pedirle a la persona que lo repita.
   - Si en vez de tocar un botón la persona escribe, el mensaje se interpreta otra vez
     contra la misma pregunta pendiente (la pregunta de la rama no es una rama nueva).
   - En `dudoso`, "No, es otra cosa" es la misma salida que "Dejar y ver lo otro".
   - `charla` y `no puedo` no cambian: vuelven a hacer la pregunta pendiente.
   - Una rama está abierta para quien tiene que responderla: un borrador que espera la
     confirmación de otra persona no es una rama abierta de quien lo pidió.
   - Qué es una rama: algo que la persona empezó en ese chat y que Prisma espera de ella
     para terminarlo. Lo son un dato pedido (el del menú, Modificar, "Ninguna, lo
     escribo", un campo o una elección del alta), la vista previa de un cambio que ella
     pidió y espera su Confirmar, y la propia pregunta de la rama. No lo son los botones
     que sólo ofrecen caminos (una lista de tareas, el menú de una tarea), ni lo que
     empezó otra persona y le llega para decidir (una aprobación que le piden): eso es
     un mensaje que inicia Prisma, se retiene mientras ella tenga una rama abierta y
     sigue la escalera si queda sin respuesta, pero no le impide hablar de otra cosa.
   - El retome posterior ("¿seguimos con …?") y la guarda que impedía volver a proponer
     lo pendiente durante otro tema quedan sin uso, porque el responder ya no corre con
     una pregunta abierta.
   - Los mensajes que Prisma inicia por su cuenta (cadencias, avisos, escalera) también
     esperan (decisión del usuario, 2026-09-29): mientras una persona tiene una rama
     abierta, lo que Prisma le iba a mandar queda retenido y sale apenas la rama se
     cierra. Sólo se retiene lo dirigido a esa persona; a las demás les sigue saliendo.
     Para que una rama abandonada no silencie el seguimiento, la retención termina
     cuando la pregunta pendiente vence (su vencimiento de siempre); si un tipo de
     pregunta no tiene vencimiento, se le define uno antes de retener por él.
     **Precisión (2026-09-29, decisión del usuario):** se retiene sólo mientras la
     persona está activa en la rama, es decir, si escribió o tocó algo en ese chat en
     los últimos 30 minutos. Una rama abierta pero abandonada no retiene nada: lo que
     Prisma inicia sale en el momento (un aviso urgente no espera horas) y la rama sigue
     abierta para cuando la persona vuelva. Con esto las preguntas del alta, que no
     vencen, también retienen, acotadas por la actividad.
2. **Cada mensaje recibe exactamente una respuesta visible.** Al terminar de procesar un
   mensaje entrante, un control estructural verifica lo encolado para ese mensaje: si
   no salió nada, sale el aviso neutro y se registra el incidente; nunca sale más de una
   respuesta (una respuesta puede tener varias partes y un juego de botones). El saludo
   del día va dentro de la respuesta y el indicador de actividad (ADR 0011) no es una
   respuesta. Los mensajes sin texto entran en la regla: el epígrafe de una foto o un
   archivo se procesa como texto y Prisma avisa que el adjunto todavía no se guarda; sin
   epígrafe, Prisma dice que todavía no puede recibir fotos, archivos ni audios y pide el
   texto o un link.
3. **Decir el estado real y ofrecer sólo lo posible.** Después de cualquier acción, o de
   una acción que no se hizo, la respuesta dice cómo quedó la tarea (estado vigente
   leído de la base) y qué falta, con el próximo paso como opción real. Por ejemplo,
   evidencia enviada sobre una tarea en curso: "quedó registrada; la tarea sigue en
   curso", con el botón para entregarla (la entrega sigue siendo explícita). Las
   opciones que ofrece el modelo salen de las capacidades del sistema: no se ofrece nada
   que el sistema no pueda hacer (hoy, por ejemplo, adjuntar archivos). Lo que falta en
   una tarea, como el motivo de "Pedir cambios" hasta la nueva entrega, se ve en toda
   lectura de la tarea (encabezado del menú y detalle), no sólo en un aviso.
4. **Todo toque tiene señal inmediata y es idempotente.** Cada toque de botón recibe una
   señal visible mientras se procesa, con el mismo criterio que ADR 0011. Tocar dos
   veces el mismo botón no produce un error ni un efecto duplicado: el segundo toque de
   la misma persona dentro de una ventana corta (10 segundos) se absorbe; fuera de esa
   ventana, o de otra persona, se responde como hoy.

**Cómo se prueba.** Cada regla con su mecanismo, el caso de la ronda 3 y familias de
variantes (distintas formas de saludar, cambiar de tema, responder a medias, mandar un
audio o una foto, tocar dos veces) en pruebas deterministas y en el banco. La regla 2 se
agrega además como comprobación del banco y del validador de invariantes
(`odd/tasks/validador-invariantes.md`).

## Consecuencias

- Una respuesta a un dato pedido, que hoy no pasa por el modelo (0 s), pasa a costar una
  llamada de ruteo (~2 s en NaN). Decisión del usuario: se acepta por generalidad.
- Las listas de palabras (saludos, confirmaciones) quedan descartadas como mecanismo.
- Con la enmienda de una sola rama abierta, cambiar de tema con una pregunta abierta
  cuesta un toque; a cambio, ese turno no llama al modelo que redacta la respuesta
  hasta que la persona decide, y desaparecen el retome posterior y la guarda contra
  volver a proponer lo pendiente.
- Los hallazgos futuros se clasifican primero por regla; si no entran en ninguna, se
  discute si hace falta una regla nueva antes de parchear.
- No hace imposible todo error de conversación: la redacción y algunas decisiones de
  producto siguen siendo caso por caso. Lo que cambia es que cada clase de falla queda
  cerrada por un mecanismo o se detecta sola.

## Alternativas consideradas

- **Arreglar cada hallazgo por separado** (lista de saludos para H17, excepciones por
  camino para H15 y H19). Rechazada: no escala y contradice el manual §27.
- **Adoptar un framework de asistentes (Rasa, Dialogflow CX) como dependencia.**
  Rechazada: `AGENTS.md` deja fuera del producto un motor genérico de workflows; se
  adopta el patrón (comandos cerrados más manejo determinista) dentro del monolito.
- **Decidir la regla 1 sin el modelo**, con heurísticas deterministas para no sumar
  latencia. Rechazada por el usuario: menos general; se acepta el costo de una llamada.
