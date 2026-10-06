# ADR 0018: El motor de conversación

- **Estado:** propuesta. El usuario aceptó su diseño para la prueba el 2026-10-04 (paso M1), con
  las decisiones 1 a 8. Queda como propuesta hasta que pase la prueba chica de la Etapa 2. La
  decisión 9 (usuario, 2026-10-04) precisa lo que dejaron abierto las conversaciones de prueba;
  el 2026-10-05 el usuario le sumó 9h, 9i y 9j, después de la primera ronda real, la revisión
  del contrato entre la IA y el código (9k), y la jugada `destrabar` (9l).
- **Fecha:** abierta el 2026-10-04.
- **Alcance:** cómo procesa Leda cada mensaje y cada toque en el seguimiento por chat (ADR 0017,
  decisión 3): quién decide qué, el estado de la conversación, los circuitos, las situaciones
  generales, la IA que se usa y los criterios de la prueba chica. Es el mecanismo que, comparado
  con los flujos A, B y C, se llama flujo D.
- **Evidencia:** `docs/research/gestion-del-dialogo-y-arquitecturas-de-agentes.md` (secciones 2,
  "Arquitecturas", y 3, "Confiabilidad"); ADR 0013 (reglas generales de la conversación) y
  ADR 0014 (flujo de un mensaje), superados en parte; `docs/product/bitacora-de-flujos.md`;
  `odd/tasks/motor-de-conversacion.md`, "Preguntas a resolver con el usuario".

> **Cómo se lee este borrador.** El ADR se escribe con el usuario, una decisión por vez. Cada
> decisión lleva la fecha en que el usuario la tomó. Lo que figura como `PENDIENTE` no está
> decidido y no se actúa sobre ello. Ningún código de conversación se escribe antes del paso M1.

## Contexto

La conversación de Leda se escribió a mano, situación por situación, y falló en cada prueba real
(flujos A, B y C1 a C6). El relevamiento del 2026-10-04 encontró tres formas de organizar un
asistente de tareas: la IA conduce con herramientas vigiladas; la IA traduce cada mensaje en
comandos de una lista cerrada y un gestor determinista los ejecuta con flujos declarados; o el
código escribe un camino por situación. Leda tenía la segunda en la intención (ADR 0013 y 0014) y
la tercera en la implementación.

## Decisiones

### 1. La IA elige jugadas de una lista cerrada; el código las ejecuta (usuario, 2026-10-04)

Ejemplo. Ismael escribe: "Terminé lo del tablero. Lo de los planos sigo trabado, falta el
repuesto". La IA lo traduce en dos jugadas: entrega de la tarea del tablero, y bloqueo en la tarea
de los planos porque falta el repuesto. El código ejecuta cada jugada siempre de la misma manera:
atiende primero la entrega (si falta la foto que pide la tarea, eso es lo que falta) y deja el
bloqueo anotado para retomarlo enseguida. La IA escribe la respuesta, con naturalidad, a partir
de lo que el código informa que pasó.

- **La IA interpreta y elige.** Traduce cada mensaje (y cada texto escrito en lugar de tocar un
  botón) en una o más jugadas de una lista cerrada declarada en el código, con sus datos: qué
  tarea, qué evidencia, qué bloqueo.
- **El código decide y ejecuta.** Comprueba que cada jugada sea posible en el estado actual, que
  la persona tenga autoridad y que los datos existan; aplica las situaciones generales una sola
  vez para todos los circuitos; y ejecuta los efectos con las operaciones del dominio, con la
  confirmación cuando corresponde.
- **La IA redacta desde los hechos.** La respuesta sale de lo que el código informa: qué pasó, qué
  falta, qué se puede hacer. Nunca inventa datos ni efectos.
- **Lo que no está en la lista no se hace.** Leda dice con honestidad qué puede hacer, como en el
  ADR 0017, decisión 1.
- **Y se le informa al administrador** (usuario, 2026-10-04). Cuando un mensaje no entra en
  ninguna jugada de la lista, Leda le avisa al administrador qué situación fue y qué mensaje de
  la conversación la provocó, para que se analice y se agregue, y la próxima vez Leda sepa
  responder. Precisiones:
  - Se informa sólo lo que no entra en ninguna jugada. Una jugada que existe pero no se puede
    hacer en ese momento (por ejemplo, aprobar una tarea que todavía no se entregó) no es una
    situación nueva: Leda explica por qué no se puede.
  - El aviso puede llevar el mensaje: el administrador de plataforma puede ver las conversaciones
    y ese acceso queda registrado (constitución §2 y §12).
  - Este aviso es la primera forma del autoaprendizaje de Leda, que el usuario quiere. La
    constitución lo permite con un límite (§5 y mecánica §14): el aprendizaje puede ajustar cómo
    Leda entiende, comunica y estima, pero no lo que tiene permitido hacer. Por eso:
    - entender una forma nueva de decir algo que ya es una jugada (por ejemplo, que "ya lo
      liquidé" quiere decir "terminé") lo puede aprender Leda sola. Cómo, es la memoria, la
      tercera parte del motor de conversación, con su propio ADR;
    - una jugada nueva, que hace algo que Leda no hacía (por ejemplo, pasarle una tarea a otra
      persona), Leda la propone con este aviso y una persona decide si se agrega. Se escribe
      primero como conversación de prueba y después se declara.
  - Por qué canal llega el aviso y cómo se agrupan los repetidos: `PENDIENTE`. Para la prueba
    chica, lo decide la decisión 9g.
- **Enmienda la regla del mozo** (`AGENTS.md`, "Cómo pensamos juntos", punto 11). Su núcleo sigue
  vigente: la IA no inventa datos ni efectos, una propuesta suya es una sugerencia, sus
  instrucciones describen su trabajo y no casos, y la cocina no corrige lo que el mozo escuchó con
  heurísticas. Lo que cambia es la extensión que estaba en revisión ("la IA no toma decisiones"):
  la IA elige qué jugada corresponde y cómo decirlo; el código decide si la jugada vale, cómo se
  maneja cada jugada y cada situación general, y ejecuta.
- Qué declara un circuito y cuáles son las situaciones generales: decisión 4.

**Alternativas descartadas:**

- **La IA conduce con herramientas.** Se adapta sola a lo imprevisto con poco código, pero cumple
  las reglas de forma probabilística: en la tabla de τ-bench, los modelos que resuelven bien una
  tarea una vez fallan al repetirla cuatro veces. Además cuesta más y tarda más (la prueba de Rasa
  informa 0,04 dólares y 2,1 s por mensaje con comandos, contra 0,10 dólares y 7,4 s con un
  agente que llama funciones).
- **Un camino escrito a mano por situación.** Es lo que falló en cada prueba real.

### 2. Una confirmación escrita vale como el botón, con una guarda (usuario, 2026-10-04)

Ejemplo. Leda le muestra a Marcos "Ismael entregó 'Revisar el tablero eléctrico' con esta foto",
con los botones Aprobar y Pedir cambios. Marcos no toca el botón: escribe "aprobado".

- **Vale igual que tocar el botón** si se cumplen las dos condiciones: lo que confirma es lo último
  que la persona vio, y no cambió desde que se le mostró. La vista previa con huella que ya existe
  en la base (`Preparacion`, `pendientes.registrar` y `pendientes.resolver`) comprueba lo segundo.
- **Si cambió, no vale.** Por ejemplo, si Ismael mandó otra foto en el medio, Leda le muestra a
  Marcos lo nuevo.
- **Ante cualquier duda, Leda pregunta y no confirma.** "Aprobado, pero que revise el cable" no es
  una confirmación.
- En términos de la decisión 1: "confirmar" es una jugada que la IA elige sólo cuando el texto es
  claramente una confirmación, y el código comprueba la guarda antes de ejecutar.
- Resuelve lo que estaba `PENDIENTE` sobre "los botones son atajos" (`AGENTS.md`; nota del
  ADR 0013): la regla alcanza también a las confirmaciones que crean o cambian algo.

**Alternativa descartada:** que una confirmación valga sólo con el botón. No deja dudas sobre qué
se confirmó, pero va contra "los botones son atajos" y suma un paso cada vez.

### 3. Qué guarda el motor de conversación (usuario, 2026-10-04)

Las tres partes que el usuario definió el 2026-10-04:

1. **El estado de cada conversación.** Para cada persona, en todo momento: el tema abierto (por
   ejemplo, "esperando la foto de la entrega del tablero"), los temas que quedaron para después y
   lo último que Leda mostró para confirmar, con su huella. Leda deja de deducir el estado en cada
   mensaje: lo lee. Ejemplo: Ismael manda una foto con "acá está", y Leda sabe que es la del
   tablero porque el estado dice que la estaba esperando.
2. **El registro de cada turno.** Cada mensaje que entra y sale, cada toque (registrado como la
   opción elegida), las jugadas que eligió la IA y lo que hizo el código. Sirve para leer una
   prueba real, para el aviso al administrador de lo que no está en la lista (decisión 1) y, más
   adelante, para el autoaprendizaje. Se conserva como las conversaciones (ADR 0002): sin
   vencimiento hasta que un administrador autorizado lo borre, con el acceso y el borrado
   registrados; y Leda lo informa si se lo preguntan (constitución §9).
3. **La memoria (el autoaprendizaje).** Se le reserva el lugar, pero no se construye en esta
   etapa: va con su propio ADR.

- **Las tres quedan en la base, separadas por espacio:** toda tabla nueva lleva `workspace_id` y
  `row level security` forzado, y ninguna lleva `chat_id` ni `callback_data` (reglas 2 y 3 de
  `docs/architecture/frontera.md`).
- `PENDIENTE`: las tablas y columnas concretas se escriben al diseñar la Etapa 2, con migraciones
  desde la `0030`.

### 4. Qué declara un circuito y cuáles son las situaciones generales (usuario, 2026-10-04)

**Un circuito se declara con una ficha en el código**, no con caminos. Cada una de las ocho cosas
del ADR 0017 (decisión 3) es un circuito. Su ficha dice, por cada jugada: qué datos necesita, qué
comprueba el código, qué efecto hace y si lleva confirmación, y qué pasa después. Ejemplo, la
entrega:

- jugada: entregar una tarea;
- necesita: cuál es la tarea y la evidencia, si la tarea la pide;
- comprueba: que quien entrega sea el responsable y que la tarea esté en curso;
- hace: pasa la tarea a revisión, con confirmación;
- después: le avisa a quien la tiene que aprobar.

Sumar una capacidad es escribir una ficha nueva. Las fichas son un conjunto cerrado declarado en
el código, nunca configuración de un cliente (`AGENTS.md`, "Límites de alcance": no es un motor
genérico de workflows).

**Las situaciones generales se resuelven una sola vez y valen para todos los circuitos.** Son
ocho, y casi todas salen de fallas de las pruebas reales:

1. **Cambio de tema:** un tema a la vez, con tres salidas (seguir, retomarlo después o
   cancelarlo). Precisada en la decisión 9d: las salidas no se ofrecen como menú.
2. **Varias cosas en un mensaje:** Leda atiende una y deja anotadas las otras para enseguida.
   Precisada en la decisión 9d: vale sólo cuando una de ellas necesita una pregunta.
3. **Corrección:** "no, era la otra tarea".
4. **Cancelar:** "dejá, no importa".
5. **Duda:** si Leda no sabe de qué tarea se habla, pregunta con opciones para elegir.
6. **Escribir en lugar de tocar un botón:** vale igual, con la guarda de la decisión 2.
7. **Algo vencido:** un botón viejo, una vista previa que ya no corresponde o un aviso que quedó
   atrás. Leda lo dice; nunca lo descarta en silencio ni deja a la persona sin salida (hallazgos
   C-1 a C-3).
8. **Algo que no está en la lista:** Leda dice qué puede hacer y le avisa al administrador
   (decisión 1).

La lista puede crecer: una situación general nueva se agrega con el mismo procedimiento que una
jugada nueva (decisión 1).

### 5. La prueba chica

#### 5a. Qué se prueba: el recordatorio y lo que la persona contesta (usuario, 2026-10-04)

Leda le escribe a Ismael que mañana vence una tarea, e Ismael contesta lo que le sale:

- "arranqué": Leda anota el inicio;
- "llego el 27, el proveedor se demoró": Leda anota la nueva previsión y avisa al referente
  (ADR 0017, decisión 4);
- "estoy trabado, falta el repuesto": Leda anota el bloqueo (el primer paso de la decisión 3a del
  ADR 0017, sin la persecución);
- no contesta: Leda se lo recuerda al día siguiente.

Por qué este circuito: es el corazón del seguimiento (Leda arranca la conversación y tiene que
entender cualquier respuesta en contexto), es lo que los flujos anteriores nunca resolvieron (no
sabían a qué recordatorio respondía la persona) y tiene pocos efectos, todos simples. La entrega
con aprobación y el bloqueo perseguido van en las pruebas siguientes: el bloqueo perseguido es el
más importante, pero también el más grande.

> **Enmienda (usuario, 2026-10-04; decisión 9).** El bloqueo entra **con el arranque de la
> persecución**, no "sin la persecución": Leda pide la causa si falta, pregunta quién se encarga
> de destrabarlo y propone salidas (9c; el aviso al referente que decía esta enmienda se corrigió
> el mismo día: el referente se entera sólo por un escalamiento). Escribirle a quien se encarga y
> seguirlo queda para la prueba siguiente. Además, el aviso sale tres días hábiles antes del
> vencimiento, no "mañana" (9b), y el "se lo recuerda al día siguiente" es la escalera que pide
> el estado desde el día del vencimiento (9b).

#### 5b. Cuándo se da por aprobada (usuario, 2026-10-04)

Los criterios se escriben antes de la prueba, para que no se acomoden a lo que salga. La prueba se
aprueba si se cumplen los tres:

1. **Conversaciones de prueba, cinco corridas cada una contra la IA real.** Son doce: las cuatro
   respuestas de 5a más las situaciones generales que aplican (varias cosas en un mensaje,
   corrección, cancelar, cambio de tema, duda, escribir en lugar de tocar un botón, algo vencido
   y algo que no está en la lista).
   - **Las garantías, 5 de 5 en cada conversación:** Leda no inventa un dato, no hace sin
     confirmación algo que la requiere, no deja a la persona sin salida y no confunde a qué tarea
     responde la persona.
   - **La comprensión, al menos 4 de 5 en cada conversación:** y la vez que no entiende,
     pregunta; nunca hace otra cosa.
2. **Una prueba por Telegram real** con el usuario operando las cuentas de prueba: en toda la
   prueba Leda no se pierde ni se traba ninguna vez.
3. **El usuario dice que se siente natural.** Es subjetivo a propósito: quien usa a Leda es una
   persona, no una prueba automática.

El tiempo de respuesta se mide y se registra, pero no es criterio de aprobación en esta primera
prueba. Una suite en verde no cuenta como evidencia (`AGENTS.md`, "Cómo pensamos juntos",
punto 12).

#### 5c. Cuándo se frena (usuario, 2026-10-04)

Estos criterios no dicen si la prueba pasó: dicen cuándo se deja de arreglar y se revisa el
diseño, para no repetir lo de los flujos anteriores (arreglar falla tras falla mientras parecía
que se avanzaba). Se frena si pasa cualquiera de estas tres cosas:

1. **Aparece un caso especial.** Si para que una situación general funcione hay que escribir algo
   puntual para un circuito (una frase, una condición o un camino para el caso observado), el
   diseño no está resolviendo las situaciones una sola vez. Ejemplo: para que "dejá, no importa"
   funcione en el recordatorio hay que agregar una regla sólo para el recordatorio.
2. **La misma clase de falla vuelve después de un arreglo.** Si después de arreglar el mecanismo la
   prueba real vuelve a perderse o a trabarse, no se propone otro arreglo: se revisa el diseño con
   el usuario (`AGENTS.md`, "Cómo pensamos juntos", punto 4).
3. **Dos vueltas sin llegar.** Si después de dos vueltas de ajustes las conversaciones de prueba no
   alcanzan los criterios de 5b, se revisa con el usuario si el problema es el diseño o la IA
   (decisión 6).

Al frenar, el resultado se registra igual en `docs/product/bitacora-de-flujos.md`: el paso M2 se
cumple con el resultado registrado, pase o no.

### 6. La IA: arranca GPT-6 sol y se mide luna en paralelo (usuario, 2026-10-04)

- **La prueba chica arranca con GPT-6 sol**, la más fiel a los hechos en la prueba real del
  2026-10-03 (`docs/product/bitacora-de-flujos.md`, "Modelos").
- **GPT-6 luna corre las mismas conversaciones de prueba en paralelo.** En el flujo C6 confundió
  quién hizo qué e inventó un dato, pero es unas 23 veces más barata y algo más rápida (USD 0,0007
  contra 0,016 por mensaje; unos 8 s contra 11). Esas mediciones son de una sola corrida y del
  flujo C6; con el motor de conversación la IA hace otro trabajo (elige jugadas de una lista
  cerrada y redacta desde hechos que le da el código), así que hay que volver a medir.
- **Si luna alcanza los criterios de 5b**, el agente le presenta al usuario los números y el
  usuario decide si se cambia.

### 7. Jev se mide en paralelo y se queda sólo si aporta (usuario, 2026-10-04)

Jev (ADR 0006) es una IA chica que sólo elige: de qué tarea habla un mensaje, con una probabilidad
por opción; si no está segura, Leda pregunta. Con el motor de conversación, la IA principal ya
elige la tarea al elegir la jugada, y en la prueba chica el estado casi siempre la sabe (Leda le
acaba de escribir a la persona sobre esa tarea).

- **La prueba arranca sin Jev:** elige la tarea la IA principal.
- **Jev corre en paralelo sobre las mismas conversaciones, sin decidir nada.** Se suman un par de
  conversaciones difíciles a propósito, con dos tareas parecidas.
- **Si Jev evita errores que la IA principal comete sola, se queda; si no, se retira.** Es una
  pieza y un proveedor menos. La deuda `b-0005-b` (Jev duda con "el plc") se resuelve con esta
  medición.

### 8. Cuando la IA falla (usuario, 2026-10-04)

La IA es un servicio externo y a veces no responde. Nunca se falla en silencio.

**Caso 1: la persona escribe y la IA no responde.** Ejemplo: Ismael escribe "arranqué" y la IA no
contesta.

- Leda reintenta una vez, enseguida.
- Si vuelve a fallar, no se ejecuta nada: sin IA no hay jugada, y nada se hace adivinando.
- La persona recibe un mensaje neutro: no fue posible completarlo y el caso quedó registrado
  (constitución §10). Ese texto es fijo en el código, porque no hay IA para escribirlo.
- El administrador recibe el aviso de la falla, como incidente.
- El mensaje queda en el registro de turnos (decisión 3): nada se pierde.

**Caso 2: los mensajes que Leda manda por su cuenta** (recordatorios, el aviso al referente de un
pedido de más tiempo). Se trae de la rama congelada el mecanismo del ADR 0016:

- el mensaje se guarda como hechos y la IA lo redacta justo antes de enviarlo;
- si la IA falla, el mensaje espera y se reintenta a los 1, 2, 4 y 8 minutos;
- al quinto fallo queda guardado con sus hechos (no se pierde), se registra un incidente para el
  administrador, y quien causó el aviso, si lo hay, recibe el aviso de falla con lo pendiente;
  nunca sale un texto armado a mano.
- Las columnas de la migración `0029` se traen con una migración nueva, desde la `0030`, y el
  redactor se rehace dentro del motor de conversación (`odd/tasks/motor-de-conversacion.md`, "Qué
  se trae de la rama congelada").
  **Precisión (usuario, 2026-10-05):** en lugar de esas columnas en `message_outbox`, los avisos
  guardados van en una tabla propia (`scheduled_notice`); al llegar su hora el código relee la tarea,
  la IA redacta y recién entonces el mensaje entra al outbox, ya con su texto. Así el despachador no
  cambia y no se suman columnas a una tabla atada a Telegram. Lo demás de este caso sigue igual
  (`odd/tasks/prueba-chica-del-motor.md`).

### 9. Precisiones de las conversaciones de prueba (usuario, 2026-10-04)

Las conversaciones de `tests/conversaciones/` dejaron 16 preguntas abiertas (P1 a P16). El
usuario las decidió el mismo día; acá quedan agrupadas. Principio del usuario: menos pasos, menos
burocracia, y todo lo que evite un menú y sea conversación es mejor, siempre que se llegue al
mismo resultado.

#### 9a. El recordatorio no confirma nada (P1, P2, P3)

- **El inicio, el bloqueo y la nueva previsión se anotan directo**, sin vista previa ni
  confirmación, y también el aviso al referente que sale de la previsión. La respuesta de Leda
  le dice a la persona qué quedó anotado; si algo está mal, la persona lo dice (situación general
  3, corrección). En palabras del usuario: anota y le contesta que anotó.
- **Consecuencia:** el circuito del recordatorio no tiene nada que confirmar. La guarda de la
  decisión 2 (la confirmación escrita) se prueba con el primer circuito que confirma, la entrega,
  y no en la prueba chica.

#### 9b. Avisos y tiempos (P4, P6, P12, P15 y el aviso previo)

- **Un solo aviso previo, tres días hábiles antes del vencimiento** para CoreWork, no uno por
  día. Es un valor de cada espacio en el pack (mecánica §9 permite alargar los intervalos, con un
  mínimo de un día hábil) y después de la plataforma (`docs/product/plataforma-pendientes.md`);
  hoy el código lo tiene fijo en un día (`escalera.py`). Una tarea creada con menos de tres días
  hábiles por delante comprime la escalera, como dice el núcleo. Enmienda el ADR 0017, decisión
  3b, punto 1.
- **El aviso previo no pide respuesta** (mecánica §9: sin exigir respuesta). **Desde el
  recordatorio del día del vencimiento, cada recordatorio pide el estado y espera respuesta**; si
  no llega, la escalera avanza: el día hábil siguiente, el segundo; a los dos, el tercero, que
  avisa que se va a escalar; a los tres, el escalamiento. Es la cuenta de quién no contestó
  (`pending_reply`, ADR 0017, decisión 6). Con una previsión posterior al vencimiento, esta
  escalera corre desde la fecha prevista y el día del vencimiento lleva un solo recordatorio que
  no pide nada (9i, 2026-10-05). Excepción: una pregunta que Leda hace para entender
  algo que la persona empezó se puede dejar sin efecto ("dejá, no importa") y Leda no insiste.
- **Sin botones** en el aviso previo ni en los recordatorios (constitución §8): la prueba mide si
  Leda entiende el texto libre, y un botón queda viejo. Se pueden sumar después como atajos si la
  prueba real se siente pesada.
- **El aviso al referente de una nueva previsión** lleva la tarea, la previsión y su motivo, la
  fecha comprometida, los días hábiles de atraso y las tareas que dependen de ella (mecánica §4,
  impacto en cadena). El atraso lo calcula el código, nunca la IA: es importantísimo calcularlo e
  informarlo, en palabras del usuario. Mientras no exista la plataforma, no dice cómo se cambia la
  fecha.
- **Un aviso guardado para salir más tarde** (decisión 8): al enviarlo, el código vuelve a leer
  la tarea. Si todavía corresponde, se redacta con los hechos de ese momento. Si ya no
  corresponde, no sale, y la omisión y su motivo quedan registrados (mecánica §12: nunca en
  silencio). Si el hecho nuevo merece su propio aviso, ése sale con su propia regla.
- **Una previsión que vuelve a la fecha comprometida antes de que salga el aviso guardado** no
  genera aviso al referente (usuario, 2026-10-04): para él no cambió nada y sería ruido. La
  historia guarda la previsión, su corrección y el aviso que no salió, con su motivo.

#### 9c. Bloqueos: "estoy trabado" nunca queda suelto (P9)

1. Sin causa, Leda pide la explicación.
2. Con la causa, anota el bloqueo y **pregunta quién lo puede destrabar, en todo bloqueo**. Esa
   pregunta espera respuesta como un pedido de estado (9b), no como las que se pueden dejar sin
   efecto: si no llega, Leda la repite el día hábil siguiente y sigue la misma escalera de quien
   no contestó. **La respuesta de la persona decide lo que sigue.** Si nombra a alguien, queda
   anotado como quien destraba: es el primer eslabón de la cadena, y escribirle y seguirlo es la
   persecución, de la prueba siguiente.
3. Si dice que nadie, que no sabe o que lo tiene que resolver ella, queda anotado y Leda propone
   salidas: que alguien ayude, o más tiempo, que es la jugada de la nueva previsión. Por ejemplo,
   "estoy trabado, no sé configurar el protocolo": Leda anota el bloqueo y pregunta quién lo puede
   destrabar; "nadie, me falta saber cómo": Leda lo anota y ofrece que alguien lo ayude.
4. **El referente no recibe un aviso por el bloqueo.** Leda lo trabaja con la persona, para
   destrabarlo sin llevarle el problema al referente (constitución §3: los referentes no
   persiguen avances). El referente se entera sólo por un escalamiento (mecánica §8): un bloqueo
   abierto más días que los del pack (ya existe en el código) o la escalera de la pregunta del
   paso 2 agotada sin respuesta. El aviso de una nueva previsión sigue (9b): la fecha comprometida
   la decide el referente (ADR 0017, decisión 4).

> **Corrección (usuario, 2026-10-04).** Más temprano ese mismo día, el paso 4 decía que Leda
> avisaba al referente con la causa, el atraso, las tareas que dependen y quién se encarga. El
> usuario lo corrigió: la idea es que Leda ayude a solucionar el inconveniente y no le lleve
> problemas al referente, que con ese aviso sólo ganaba tener que actuar.

> **Corrección (usuario, 2026-10-05; primer contacto real).** Hasta ese día, el paso 2 preguntaba
> quién destraba sólo si la causa dependía de otra persona, y eso lo juzgaba la IA. En el primer
> contacto real, con "estoy trabado, falta el repuesto", la IA juzgó que no dependía de otro y
> Leda propuso salidas en lugar de preguntar quién consigue el repuesto. El usuario sacó ese
> juicio: Leda pregunta quién lo puede destrabar en todo bloqueo con causa, y lo que sigue lo
> decide la respuesta de la persona, que sabe quién es, y no una lectura de la causa. La
> persecución completa (ADR 0017, decisión 3a) sigue siendo de la prueba siguiente, no de la
> Etapa 2.

La escalera de recordatorios de la tarea se detiene. Escribirle a quien se encarga y seguirlo
(la persecución completa del ADR 0017, decisión 3a) queda para la prueba siguiente. Enmienda la
decisión 5a. Cómo se guarda quién destraba (`PENDIENTE` del ADR 0017, decisión 3a) se resuelve
al diseñar las tablas de la Etapa 2.

#### 9d. Situaciones generales (P5, P13, P14)

- **Varias cosas en un mensaje:** Leda anota en una sola respuesta todo lo que se puede anotar
  directo. Si alguna necesita algo (un dato que falta, una duda sobre la tarea), primero anota lo
  que se resuelve solo y después pregunta una cosa por vez, en el orden en que la persona las
  dijo. La situación general 2 ("atiende una y deja las otras") vale sólo cuando una de ellas
  necesita una pregunta.
- **Cambio de tema mientras Leda espera una respuesta:** las tres salidas existen, pero no se
  ofrecen como menú. Si lo nuevo se puede anotar directo, Leda lo anota y en la misma respuesta
  vuelve a la pregunta pendiente, y eso es retomarla; la persona contesta o dice que lo deja
  (cancelar, sin insistir). Botones sólo si hay una duda real sobre de qué tarea habla (situación
  general 5, con las tareas como opciones). Sigue valiendo un tema a la vez: nunca dos preguntas
  juntas. Precisa la situación general 1.
- **Si lo nuevo también necesita una pregunta, Leda sigue a la persona** (usuario, 2026-10-04):
  pregunta por lo nuevo; la pregunta pendiente queda para después (la guarda el estado por
  persona, decisión 3) y, cuando lo nuevo se cierra, Leda vuelve a ella. Nunca dos preguntas
  juntas.

#### 9e. Horario: Leda contesta las 24 horas (P10)

Leda está disponible las 24 horas para contestar a quien le escribe; el horario laboral rige sólo
para los mensajes que Leda manda por su cuenta. Los avisos a otras personas que dispara ese
mensaje esperan al horario (las 09:00 del día hábil siguiente), y Leda se lo dice a la persona.
En palabras del usuario: Leda respeta el horario para enviar mensajes, no para responder si
alguien le pregunta. Es la lectura del usuario de la constitución §8 ("escribe fuera del
horario"), en línea con la mecánica §10, que separa la respuesta del mensaje automático.

#### 9f. Correcciones: se agrega, no se borra (P11)

Un hecho anotado en la tarea equivocada se corrige **agregando un hecho de corrección**: la tarea
vuelve a su estado anterior y el hecho va a la tarea correcta. No se borra nada; los dos quedan
en la historia (constitución §12; el estado es una proyección de los eventos). Si el error generó
un aviso que todavía no salió, sale corregido; si ya salió, el referente recibe una corrección
breve.

#### 9g. Lo que no está en la lista (P7, P8, P16)

- **El aviso al administrador** llega por el bot de administración. En la prueba chica no se
  agrupan los repetidos. A la persona no se le dice que se avisó, salvo que lo pregunte (la misma
  lógica de la constitución §9 sobre el registro de las conversaciones). Leda dice qué puede
  hacer y, si se sabe, quién se ocupa de eso.
- **La IA conoce las ocho cosas por chat** del ADR 0017 (decisión 3b), pero en la prueba chica
  sólo se ejecutan las del recordatorio (inicio, nueva previsión, bloqueo) y "qué tengo
  pendiente", que sólo lee y ya existe. "Ya la terminé" se reconoce como una entrega: Leda dice
  con honestidad que todavía no la puede recibir por acá, y no avisa al administrador (es
  conocida, no una situación nueva).
- **Un pedido de reasignación** ("pasale lo del PLC a Nahuel"): Leda dice que no lo puede hacer y
  quién lo decide (en CoreWork, Ismael, que aprueba el trabajo de Marcos y es la autoridad del
  espacio). No pasa el pedido (pasar pedidos espera; ADR 0017, decisión 1) y no avisa al
  administrador: es una exclusión deliberada, como la entrega. Si el motivo es que no llega a
  tiempo, ofrece anotar una nueva previsión.

#### 9h. Un avance sin un hecho cierto (usuario, 2026-10-05)

Una jugada nueva, decidida por el usuario y escrita primero como la conversación de prueba 15
(`tests/conversaciones/15-avance-vago.md`): `informar_avance`, la respuesta a un pedido de estado
que cuenta un avance sin nada cierto ("voy bien, la tengo casi lista"). En palabras del usuario:
casi lista no es lo mismo que terminé; es una respuesta ambigua y no puede quedar así.

- **Leda la anota con las palabras de la persona**, atribuida y auditada, sin cambiar el estado
  ni la fecha.
- **La espera sigue abierta**, porque la respuesta no es cierta, y **el día hábil siguiente Leda
  vuelve a pedir el estado**, esperando algo cierto: que la terminó, para cuándo o que está
  trabada. La respuesta lo dice como algo que todavía no pasó.
- **No es silencio.** La escalera escala sólo a quien no contesta: un avance contesta el pedido,
  así que la cuenta de pedidos sin respuesta empieza de nuevo y el pedido siguiente no avisa que
  se va a escalar. Si ese pedido queda sin respuesta, sí cuenta, y la escalera sigue desde ahí.
- **Si vuelve a contestar sin nada cierto**, Leda le pregunta directamente para cuándo, en esa
  misma respuesta (una sola pregunta).
- Lo demás no cambia: una fecha es la nueva previsión; "ya la terminé", la entrega, que la prueba
  chica reconoce y todavía no recibe (9g); "estoy trabado", el bloqueo (9c).
- **Si no hay un pedido siguiente, se dice** (2026-10-05, revisión de la jugada): con la tarea sin
  vencimiento, o con la escalera de su ancla ya escalada (9i), el avance se anota igual, no se
  guarda otro pedido y los hechos dicen por qué y a quién ya se le avisó. Nunca en silencio.

#### 9i. Con una previsión, el seguimiento se mueve a la previsión (usuario, 2026-10-05)

Hasta ese día, una previsión detenía la escalera y nada decía qué seguía cuando llegaba la fecha
prevista. El usuario lo decidió con un ejemplo: la tarea vence el jueves 15 y el 5 Marcos dijo
"llego el 27". El 15 Leda le manda **un solo recordatorio** (vencía hoy, ya dio el 27 y el
referente está al tanto) y no le pregunta nada cada día hasta el 27. **El 27 le pide el estado como
si fuera el vencimiento**; sin respuesta, corre la escalera normal desde esa fecha (los pedidos,
el aviso de que se va a escalar y el escalamiento).

- **La fecha comprometida no cambia** y el atraso se sigue contando contra ella: cambiarla es
  decisión del referente, en la plataforma (ADR 0017, decisión 4).
- **El ancla de la escalera** es la fecha comprometida o, si la previsión vigente es posterior, la
  fecha prevista. Una previsión más nueva mueve el ancla y empieza una escalera nueva; una que
  vuelve a la fecha comprometida (o anterior) la devuelve al vencimiento. Un aviso guardado de otra
  ancla no sale, con su motivo (9b).
- **El recordatorio del vencimiento** sale sólo si la escalera del vencimiento no había empezado (si
  la previsión llegó después del primer pedido, ya está contestado). Con el ancla en la previsión
  no hay aviso previo: la fecha la dio la persona.
- **Leda es la PM** (principio del usuario, 2026-10-05): el referente recibe información y las
  decisiones que son suyas, nunca trabajo de gestión. Revisados los avisos al referente de la
  escalera: el aviso de una nueva previsión y su corrección (información; la fecha es su
  decisión) y el escalamiento por falta de respuesta (información, mecánica §9). Ninguno le pide
  perseguir a nadie ni resolver nada.

#### 9j. Con la tarea vencida, una respuesta sin fecha lleva la pregunta de para cuándo (usuario, 2026-10-05)

Decidida por el usuario y escrita primero como la conversación de prueba 16
(`tests/conversaciones/16-vencida-sin-fecha.md`). Con la tarea vencida (pasada su fecha de
seguimiento: la comprometida o, si es posterior, la previsión, que es el ancla de 9i), **lo que la
persona contesta se anota igual y, si no trae una fecha** ("arranqué hoy", "voy bien", "sigo con
eso"), **Leda le pregunta en esa misma respuesta para qué día la va a tener**: una sola pregunta.

- **La respuesta es una previsión**: con su aviso al referente y el atraso, que calcula el código
  contra la fecha comprometida (9b), y el seguimiento se mueve a esa fecha (9i).
- **Es una regla general para toda jugada sobre una tarea vencida, no para una.** Una fecha y un
  bloqueo son algo cierto y no la llevan; el bloqueo sigue con su pregunta de quién lo destraba
  (9c). Un inicio o un avance no lo son.
- **Mientras no llega la fecha, no es silencio, pero tampoco algo cierto sobre cuándo**: la
  espera del estado sigue abierta y, si no contesta, Leda vuelve a pedir el estado el día hábil
  siguiente con la cuenta de pedidos de nuevo, como después de un avance (9h).
- **Precisa 9h**: con la tarea vencida, el avance lleva la pregunta de para cuándo ya desde la
  primera vez; "a la segunda" queda para la tarea que todavía no venció. La conversación 15 prueba
  las dos: el primer avance, el día del vencimiento, sin pregunta; el segundo, ya vencida, con la
  pregunta de para cuándo.

> **Precisiones de la corrida en seco de la E2-7 (usuario, 2026-10-05).** Tres hallazgos del motor,
> resueltos como reglas generales. (1) **Toda pregunta cuya ficha dice que espera respuesta abre
> una espera y la repite la escalera** de quien no contestó: el día hábil siguiente, otra vez al
> otro avisando a quién se va a escalar, y al siguiente escala; la de quién destraba es una de
> ellas (9c, paso 2; conversación 03). (2) **Todo lo que Leda le propone a la persona queda como
> tema abierto** (ADR 0013: la pregunta pendiente es el contexto): las salidas de un bloqueo y la
> previsión ofrecida en lugar de una reasignación se contestan haciendo una de ellas, se pueden
> cancelar y siguen la regla de un tema a la vez (conversaciones 03 y 12). (3) **Los mensajes
> automáticos del día a una persona salen en un solo envío** (mecánica §10), redactado desde los
> hechos de todos y con una sola pregunta; los de coordinación y las respuestas, aparte
> (conversación 13).

#### 9k. Revisión del contrato entre la IA y el código (usuario, 2026-10-05)

La primera ronda real (GPT-6 sol y luna, cinco veces cada una de las 16 conversaciones;
`prueba_chica/resultados/ronda1-sol.md` y `ronda1-luna.md`) mostró fallas de comprensión que no
eran de una conversación sino del contrato entre la IA y el código: lo que el código le pasa y lo
que le pide. Se revisó entero, con reglas generales y sin ningún caso (5c.1):

1. **Los hechos dicen qué significan.** Dos cosas distintas nunca comparten un nombre: el atraso
   de hoy y el que tendrá la tarea si se cumple una previsión tienen claves distintas (la ronda
   le contó al referente el segundo como si fuera el primero, conversaciones 15 y 16). Cada clave
   y cada código tiene su significado una sola vez, en el vocabulario de los hechos
   (`prueba_chica/hechos.py`), y la IA recibe, en los dos pedidos, el significado de todo lo que
   le llega. Un hecho sin significado es una falla del motor en la corrida.
2. **Cada jugada se define por lo que la distingue de las parecidas**, desde el núcleo (mecánica
   §3 y §8), y ofrece sólo sus datos. Una previsión es una fecha para terminar, con su porqué o
   sin él: un atraso, no un bloqueo. Un bloqueo es que la persona dice que no puede avanzar. Un
   avance no trae fecha, ni bloqueo, ni inicio. Corregir es decir que lo anotado estaba mal; dar
   un hecho nuevo es la jugada de ese hecho. Cada dato dice qué es y va sólo si la persona lo dijo
   (una causa es lo que falta o frena el trabajo). Lo que la persona dijo una vez va en una sola
   jugada.
3. **La duda llega al código.** Si la jugada es clara y la tarea no, la IA elige la jugada sin la
   tarea y el código pregunta cuál, con botones (situación general 5). Ninguna jugada, sólo cuando
   el mensaje no dice ni pide nada que una jugada haga.
4. **Una pregunta sobre la conversación o sobre lo que Leda hizo no es una jugada:** se contesta
   desde el registro de turnos y sus hechos, también lo que se dice sólo si se pregunta (9g). Lo
   que no está en la lista es sólo un pedido de hacer algo, y sólo eso avisa al administrador.
5. **Todo mensaje deja un próximo paso** (constitución §8): la pregunta que se hace, lo que va a
   pasar y cuándo, o lo que la persona puede hacer; o dice que no hace falta nada. **Y nunca se
   narra cómo funciona el sistema** (§10): ni lo que intentó o no pudo hacer por dentro; se cuenta
   lo que cambia para la persona, lo que falta y lo que sigue. Todo lo que quedó anotado o cambió
   se cuenta.

**Precisión (2026-10-05, antes de la segunda ronda): los hechos de lo que pasa después se
calculan al final del turno.** Una jugada puede dejar sin efecto lo que otra del mismo mensaje
dejó para después (un avance o un destrabe guardan el pedido del estado del día siguiente; una
fecha en el mismo mensaje contesta la espera y ese pedido ya no sale). Cada hecho nombra por su
id los avisos, las esperas y las preguntas que deja para después, y después de todas las jugadas
el turno los vuelve a leer de la base y pone su estado final (un aviso que ya no corresponde se
retira en ese momento, con su motivo) antes de pedir la redacción. Un solo paso para todas las
jugadas (`prueba_chica/efectos.py`); las ids no llegan a la IA ni al registro de turnos.

Cerrar un bloqueo cuando su causa desaparece quedó `PENDIENTE` de una decisión del usuario; la
tomó el mismo día: es la jugada `destrabar` (9l).

#### 9l. Destrabar: la causa del bloqueo ya no está (usuario, 2026-10-05)

Una jugada nueva, decidida por el usuario (decisión 1: una jugada nueva la decide una persona) y
escrita primero como la conversación de prueba 17 (`tests/conversaciones/17-destrabar.md`):
`destrabar`, cuando la persona dice que la causa de un bloqueo abierto ya no está ("llego el
switch, sigo").

- **Leda cierra el bloqueo, directo**, como lo anotó (9a), con la operación del dominio
  (`resolver_bloqueo`), atribuido y auditado: la tarea vuelve al estado que tenía antes de
  bloquearse (mecánica §3).
- **Lo que esperaba algo del bloqueo se cierra con él**: la pregunta de quién lo destraba (9c,
  paso 2) y su espera, y lo propuesto para salir de él (9c, paso 3).
- **El seguimiento vuelve.** Antes de su fecha, la escalera sigue sola. Si el seguimiento ya había
  empezado (hoy es su fecha, o la pasó), destrabarse no es algo cierto sobre cuándo la termina: la
  espera del estado queda abierta y Leda vuelve a pedirlo el día hábil siguiente, con la cuenta de
  nuevo, como después de un avance (9h); vencida, además, la pregunta de para cuándo (9j). Lo que
  había detenido la cuenta anterior (un paso que no salió porque la tarea se bloqueó) no detiene la
  nueva. Antes de su fecha, tampoco (revisión, 2026-10-05): un aviso previo que no salió porque la
  tarea estaba bloqueada vuelve a salir mientras siga siendo previo.
- **Se distingue de las parecidas** (9k.2): salir de un bloqueo no es empezar la tarea, ni dar una
  fecha, ni contar un avance; si el mensaje trae además uno de esos hechos, es otra jugada.
- La respuesta dice qué quedó anotado y el próximo paso. Con más de un bloqueo abierto en la tarea,
  Leda no elige cuál se resolvió: lo dice, con sus causas, y no cierra ninguno.

## Consecuencias

- **Decisión 1:** cada jugada de la lista y cada situación general se declaran y se prueban una
  vez; sumar un circuito es declarar sus jugadas, no escribir ramas.
- **Decisión 1:** al aceptar este ADR (tarea E1-4), el punto 11 de `AGENTS.md` se reescribe con la
  enmienda.
- **Decisión 9:** el plan de la Etapa 2 parte de un recordatorio sin confirmaciones; el aviso
  previo deja de ser fijo en `escalera.py` y pasa a ser un valor del pack; el bloqueo de la prueba
  chica suma el arranque de la persecución.
