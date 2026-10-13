# ADR 0023: Quién crea objetivos, tareas y jerarquías en la plataforma

- **Estado:** Aceptado por el usuario el 2026-10-13 ("acepto"). Las decisiones 1 a 6 son del
  usuario (2026-10-13); su redacción como enmienda, las lecturas marcadas como tales y la división
  en porciones son del agente. Se construye por porciones, cada una con su prueba real.
- **Fecha:** 2026-10-13.
- **Alcance:** quién crea objetivos, tareas y esperas, y quién organiza el equipo (áreas, roles y
  referentes), desde qué puerta de la plataforma y con qué garantías.
- **Enmienda:**
  - el [ADR 0022](0022-plataforma-web-de-tareas.md), decisiones 3, 6, 9, 10 y 16, y toca la 7 (ver
    `PENDIENTE` 1, resuelto: no cambia); el texto que cambia está citado abajo, en "Qué texto reemplaza a cuál";
  - el [ADR 0017](0017-por-chat-los-hechos-por-la-web-la-estructura.md), decisión 2 (las tareas las
    crea a mano el administrador; la declaración de quién decidió) y decisión 7, punto 1 (la
    aceptación del referente ocurre fuera de Leda).
- **No cambia:** que no se crean tareas ni objetivos por chat (ADR 0017, decisión 1), ni el
  `nucleo/`.
- **Evidencia:** `odd/tasks/plataforma-p2.md`, "Para decidir", puntos 1 a 3, con las palabras del
  usuario; `nucleo/constitucion.md` §2, §3, §7, §12, §13 y §14; `nucleo/mecanica-pm.md` §1, §3, §4 y
  §7; el esquema de hoy (`db/esquema.sql`: `objective`, `task`, `dependency` con
  `evitar_ciclo_dependencia`, `area.referente_membership_id`, `membership.aprobador_membership_id`,
  `rol.autoridad_final` con una sola por espacio, `approval_policy.autoaprobacion_declarada`, y la
  función de carga `cargar_tarea`).

## Contexto

La porción 2 de la plataforma dejó a un administrador de plataforma cargando tareas desde la puerta
de administración, eligiendo un objetivo que ya existe y declarando quién decidió la tarea. Al
revisar lo que quedaba por decidir, el usuario fijó otra forma: la estructura del trabajo la arma
el propio equipo, siguiendo su jerarquía, y el administrador de plataforma queda para lo que es de
toda Leda.

El ejemplo del usuario, que se usa en todo este ADR:

1. Dirección crea el objetivo "Poner el módem colgando en la pared".
2. El referente del área crea la tarea "Comprar el estante", que faltaba para ese objetivo.
3. Un integrante crea para sí mismo "Comprar los tornillos", que queda propuesta hasta que su
   referente la aprueba.
4. "Colocar el estante" espera a "Comprar los tornillos". Si se atrasa, se ve por qué: faltaban los
   tornillos.

## Decisión

### 1. Los objetivos los crea Dirección desde la web (usuario, 2026-10-13)

- Dirección crea los objetivos de su equipo desde la web. El paquete del espacio sigue trayendo los
  iniciales.
- Lo mínimo, como propuesta: el nombre, de qué objetivo cuelga (puede no colgar de ninguno) y su
  referente. Ejemplo: "Poner el módem colgando en la pared", sin objetivo de arriba, referente Marcos.
- El administrador de plataforma también puede crearlos, en cualquier espacio (decisión 5).
- **Lectura del agente:** el usuario dijo primero "obviamente, los crea el administrador" y, ese mismo
  día, al decidir las jerarquías, "Dirección crea objetivos". Se toma la segunda, que no contradice la
  primera porque el administrador puede todo (decisión 5).
- Ningún objetivo tiene dos padres ni cuelga de otro espacio (mecánica §1; aislamiento).

### 2. Las esperas se cargan en el mismo formulario de la tarea (usuario, 2026-10-13)

- Un campo opcional, "espera a", que deja elegir entre las tareas abiertas del mismo espacio.
- Siempre bloqueante: la tarea no puede pasar a en curso hasta que la otra esté terminada (mecánica
  §4). La espera informativa queda para más adelante.
- La base ya guarda las esperas (`dependency`) y rechaza los ciclos (`evitar_ciclo_dependencia`).
  Ejemplo: si "Comprar los tornillos" espera a "Colocar el estante" y alguien quiere que "Colocar el
  estante" espere a "Comprar los tornillos", la carga se rechaza y se dice por qué.

### 3. Crear tareas sigue la jerarquía del equipo (usuario, 2026-10-13)

Reemplaza el campo libre "quién la decidió" del formulario.

- **Dirección** crea objetivos y las tareas que considera necesarias, en cualquier área de su equipo.
- **El referente de un área** crea tareas para su área, también las que faltaban para un objetivo de
  Dirección ("Comprar el estante"). **Entran directo**, comprometidas, sin aprobación de Dirección
  (usuario: "directo"), **sin aviso a Dirección** (usuario: "sin aviso"; respeta la decisión 7 del
  ADR 0022): Dirección las ve en la web, con quién las creó, y en el resumen semanal. El umbral de re-aprobación de la
  mecánica §7 (una tarea fuera del plan que consume más esfuerzo del umbral) queda para cuando haga
  falta.
- **Un integrante** crea tareas para sí mismo ("Comprar los tornillos"). Quedan en `propuesta`
  ("sugerida, todavía no evaluada", mecánica §3) hasta que las aprueba quien revisa su trabajo (`PENDIENTE` 3, resuelto). Mientras son
  propuesta no tienen seguimiento: ni recordatorios, ni escalera, ni cuentan como compromiso.
- **"Quién la decidió" sale de los hechos**, no de un campo: la decidió quien la creó, si es
  Dirección o el referente; si es una propuesta, la decidió el referente que la aprobó. La
  auditoría guarda quién la creó y quién la decidió (constitución §12).
- **La aprobación del referente es la conversión** de propuesta a tarea comprometida: explícita, con
  vista previa y confirmación, y auditada (invariante de `AGENTS.md`). Con esto vuelve a aplicarse,
  para estas tareas, la constitución §3: "los referentes aceptan las tareas vinculadas a su área".

### 4. Las jerarquías las maneja Dirección desde la web del equipo (usuario, 2026-10-13)

- Dirección organiza su equipo: las áreas, los roles y quién es referente de qué. No depende del
  administrador de plataforma ni sólo del paquete. En palabras del usuario: "es su equipo de trabajo
  y él decide cómo organizarlo".
- Las garantías de la mecánica las exige el código, no quien carga:
  - toda área tiene un aprobador declarado o la declaración explícita de que se autoaprueba
    (mecánica §7);
  - el espacio nunca queda sin una autoridad final (hoy la base admite exactamente una por espacio);
  - la cadena de quién aprueba a quién no tiene ciclos ni deja a nadie sin aprobador, salvo la
    autoridad final.
- Ejemplo: Dirección quiere borrar el área de OT con Nahuel adentro. No se puede hasta que Nahuel
  tenga otra área; la web dice por qué.

### 5. Quién puede qué (usuario, 2026-10-13)

- **El administrador de plataforma** puede todo, en todos los espacios; también organizar la
  jerarquía de un equipo si se lo piden.
- **Dirección** puede todo lo de su equipo (jerarquías, áreas, personas, cadencias), y sólo de su
  equipo.
- **Dos límites**, aceptados por el usuario:
  - el núcleo no lo cambia nadie desde la plataforma (constitución §14);
  - ampliar la autoridad de Leda lleva las dos firmas (constitución §2).
- En palabras del usuario: "si son funciones nuevas, obviamente tiene que pedirlas a administración
  de la plataforma, pero si son funciones disponibles, las puede ajustar como guste". **Lectura:** el
  administrador habilita una función para el espacio (la firma de quien aplica) y Dirección la usa y
  la ajusta (la de quien decide). Ejemplo: cambiar el día del informe semanal es ajustar algo
  disponible; que Leda escriba fuera del horario ante una urgencia (constitución §8) es una función
  nueva y pasa por las dos firmas.
- Esto dice quién puede, no qué se construye ahora: la configuración desde la web (cadencias,
  horarios y lo demás del inventario) sigue esperando la segunda versión (ADR 0022, decisión 1).

### 6. El canal: sólo la web por ahora (usuario, 2026-10-13)

- Objetivos, tareas, esperas y jerarquías se crean desde la web.
- Crear tareas por chat queda para más adelante: está en `docs/ROADMAP.md`, "Anotado para más
  adelante" (los borradores de tarea del flujo congelado, adaptados al motor). Hasta entonces sigue
  la decisión 1 del ADR 0017: un pedido de tarea nueva por chat se deriva, sin efectos.

## Qué texto reemplaza a cuál

Los textos anteriores no se borran de sus ADR. Cada uno ya lleva una línea que remite acá, como
propuesta; al aceptarse este ADR, esa línea pasa a decir que la enmienda rige.

**ADR 0022**

- Decisión 3, el puesto del administrador: "**administrador:** todo, y además carga y cambia
  (decisión 6)". Pasa a: el administrador ve todo y puede todo; **Dirección y los referentes también
  cargan**, cada uno dentro de su puesto (decisión 3 de este ADR), y un integrante propone para sí.
  Lo que cada uno ve no cambia.
- Decisión 6, "**Para más adelante:** con clientes, alguien de cada empresa querrá cargar sus
  tareas. Será un rol del espacio, con acceso sólo a su empresa". Se adelanta: ese rol es Dirección,
  con su equipo y sólo su equipo, por la puerta del equipo.
- Decisión 7, "La autoridad final no recibe un mensaje por tarea". Sigue valiendo: una tarea que
  crea un referente no le manda un aviso a Dirección (`PENDIENTE` 1, resuelto).
- Decisión 9, el formulario: el campo "quién la decidió" deja de existir en la puerta del equipo
  (sale de quién crea y quién aprueba). Se suma el campo opcional "espera a" (decisión 2). Los demás
  controles siguen igual, para las tareas que entran comprometidas y para las propuestas al
  aprobarse.
- Decisión 10, "**La puerta del equipo** se abre sólo con el enlace de Leda del bot del espacio y
  muestra sólo ese espacio". Pasa a: muestra sólo ese espacio y **deja crear lo que el puesto de
  cada uno permite** (decisiones 1 a 4).
- Decisión 10, "**La puerta de administración** ... Es la única que carga tareas, gestiona
  integrantes y ve más de un espacio". Pasa a: es la única que ve más de un espacio y la única que
  habilita funciones nuevas para un espacio. Cargar objetivos y tareas y organizar un equipo se
  hacen también por la puerta del equipo, según el puesto.
- Decisión 10, el ejemplo "para cargar una tarea entra por la puerta de administración". Pasa a:
  desde la puerta del equipo Ariel propone tareas para sí mismo, como cualquier integrante; para
  cargar como administrador, en cualquier espacio, entra por la puerta de administración.
- Decisión 16, el orden de las porciones: se suman las de la sección "Porciones" de abajo.

**ADR 0017**

- Decisión 2, "En la primera etapa del Motor ninguna persona del equipo crea tareas. Las crea a
  mano el administrador de plataforma designado, desde la plataforma web". Pasa a: las personas del
  equipo crean tareas desde la web, según su puesto (decisión 3 de este ADR); el administrador de
  plataforma también puede.
- Decisión 2, "La auditoría guarda quién cargó y quién decidió, esto último como declaración de
  quien carga ... Leda nunca lo presenta como una aprobación hecha en Leda". Pasa a: por la puerta
  del equipo, la decisión **ocurre en Leda** (la toma Dirección o el referente al crear, o el
  referente al aprobar una propuesta), y Leda puede decirlo así porque es verdad. Por la puerta de
  administración, si el administrador carga en nombre de otro, la regla anterior sigue: ver
  `PENDIENTE` 2.
- Decisión 2, "**Anotado para más adelante: la aceptación dentro de Leda** ... Se retoma cuando
  exista el formulario web". Se retoma acá, para las propuestas de un integrante, por la web.
- Decisión 7, punto 1, "en esta etapa la aceptación ocurre fuera de Leda y se declara al cargar la
  tarea". Pasa a: vuelve a aplicarse la constitución §3 para las propuestas, que el referente acepta
  en Leda; sigue declarándose sólo en la carga por administración.

## Lo que no cambia

Las invariantes vigentes (`AGENTS.md`) rigen igual:

- **Una tarea comprometida exige** objetivo, responsable, fecha objetivo, criterio de aceptación y
  política de evidencia, venga de Dirección, de un referente, de una propuesta aprobada o de la
  puerta de administración.
- **Una propuesta no tiene efectos** sobre nadie más hasta su conversión, y la conversión es
  explícita, confirmada y auditada: es la aprobación del referente.
- **El aislamiento entre espacios:** cada escritura es una función de la base con dueño explícito,
  con `row level security` forzado; el espacio sale de la sesión del lado del servidor, nunca del
  formulario (ADR 0022, decisión 11). Dirección de un espacio no ve ni toca otro.
- **La auditoría** guarda quién creó, quién decidió y quién aprobó, con las versiones del núcleo y
  del paquete (constitución §12).
- **El sombrero lo define el canal** (constitución §2): la puerta del equipo nunca da funciones de
  plataforma. Ariel, administrador de Leda e integrante de CoreWork, en la puerta del equipo puede
  lo que puede un integrante; habilitar una función o ver otro espacio, sólo por la de administración.
- **Vista previa y confirmación** antes de cada cambio (constitución §7), con la protección de dos
  cambios a la vez (ADR 0022, decisión 15).
- **Los avisos** salen por la cola de salida, redactados desde hechos (ADR 0022, decisión 14); los
  de coordinación quedan fuera del tope de contacto (mecánica §10).

## `PENDIENTE`: lo que estas decisiones no resuelven

Los once, preguntados de a uno y decididos por el usuario el 2026-10-13.

1. ~~**Cómo se entera Dirección de una tarea que crea un referente.**~~ **Decidido (usuario,
   2026-10-13): "sin aviso".** Ismael la ve en la web, con quién la creó, y en el resumen semanal; la
   decisión 7 del ADR 0022 sigue valiendo. **Precisión del usuario (2026-10-13):** "se debería poder elegir desde la web de
   dirección como quiere recibir ese tipo de notificaciones y lo ajusta a su gusto". Sin aviso es lo que
   viene de fábrica; Dirección lo cambia desde su web (por ejemplo: al momento, juntas en el resumen o
   ninguna). Es una función disponible que ajusta como quiere (decisión 5); los avisos siguen el tope
   de contacto de la mecánica §10. Las opciones exactas, en el diseño corto de su porción.
2. ~~**La carga por administración en nombre de otro.**~~ **Decidido (usuario, 2026-10-13): "la
   primera".** Como hoy, quien carga por la puerta de administración declara quién la decidió y la
   auditoría guarda las dos cosas (la cargó Ariel, la decidió Ismael); sólo se puede elegir a quien
   tiene autoridad sobre esa tarea según la jerarquía: Dirección o el referente del área.
3. ~~**Quién es "su referente" para aprobar una propuesta.**~~ **Decidido (usuario, 2026-10-13):
   "quien revisa su trabajo".** La propuesta de un integrante la aprueba quien revisa su trabajo (el
   `aprobado_por` de la persona en el pack, el mismo que aprueba sus entregas; en una tarea prestada,
   quien revisa esa tarea: punto 7), no el referente del área. Cuando coinciden, que es lo normal, no cambia nada; así proponer, entregar y aprobar pasan
   por la misma persona.
4. ~~**Qué le falta a una propuesta.**~~ **Decidido (usuario, 2026-10-13): la persona describe y
   Leda completa.** Ni burocracia para quien propone ni para quien aprueba (el usuario: "le sacamos la
   burocracia a nahuel y se la pasamos al que aprueba"). Nahuel elige la tarea que destraba y describe
   como habla ("faltan los tornillos para colgar el estante, necesito 12 de 8 mm"); con eso la IA
   propone el título y el criterio, y la web pone el responsable (él), el objetivo (el de la tarea que
   destraba), una fecha antes de su vencimiento y la evidencia que pide su área. Él corrige y la manda;
   quien la aprueba lee una propuesta completa. Garantías, las de la entrega por chat: lo que propone la
   IA cuenta sólo si la persona lo acepta; el código rechaza un criterio con un número o un nombre que
   nadie dijo; nada se compromete incompleto. La misma ayuda, para Dirección y los referentes al cargar
   (usuario: "hace la tarea que tiene que hacer leda, que es facilitar y ayudar"). Es la IA dentro de la
   web, nueva: va en su propia porción, con su prueba.
5. ~~**El rechazo de una propuesta.**~~ **Decidido (usuario, 2026-10-13: "si").** Quien aprueba
   pone el motivo (mecánica §3: no se cierra sin razón); a quien la propuso le llega un aviso de Leda
   por chat con el motivo, de coordinación (mecánica §10: "le rechazaron uno" llega siempre y no cuenta
   para el tope); la propuesta queda `cancelada`, con quién y por qué, en la auditoría y visible en la
   web. Si la idea sirve pero no así, quien aprueba la corrige y la aprueba (punto 4).
6. ~~**Cómo se entera quien aprueba de una propuesta.**~~ **Decidido (usuario, 2026-10-13: "si").**
   Un aviso de Leda por chat, de coordinación (mecánica §10: "le llegó un borrador para confirmar"),
   con el enlace a la propuesta en la web y sin botón de aprobar: se aprueba en la web, donde se ve
   completa y se puede corregir (ADR 0017: "en el formulario web; nunca por chat"). En la web, arriba
   de todo en "Tu sector" hasta que la decida; varias del mismo día, juntas en un mensaje, como las
   entregas para revisar.
7. ~~**Dirección crea una tarea en un área.**~~ **Decidido (usuario, 2026-10-13), con el préstamo de
   personas.** Una persona pertenece a un sector (Nahuel, a OT, con Marcos de referente) y eso no
   cambia; otro referente puede pedirla prestada para una tarea de su sector, y esa tarea la revisa él
   (Martín, en una de Infraestructura); las demás de Nahuel las sigue revisando Marcos. **Cuando alguien
   que no es su referente le asigna una tarea** (Dirección o Martín), a Marcos le llega el aviso: le
   están usando a alguien de su sector. **Lo que pasa dentro de esa tarea** (una propuesta como la de
   los tornillos, entregas, avances) es entre Nahuel y Martín, y a Marcos no le llega nada (usuario: "no
   tiene sentido molestarlo a marcos con un aviso que no va a entender de que tornillos se refiere").
   Una propuesta dentro de la tarea prestada la aprueba quien revisa esa tarea (punto 3). **Cambio en
   la base:** hoy quién revisa es un dato de la persona (`aprobado_por`), no de cada tarea; el préstamo
   necesita quién revisa una tarea en particular, `PENDIENTE` de diseño en su porción.
8. ~~**Un referente crea una tarea para sí mismo.**~~ **Decidido (usuario, 2026-10-13): "directo".**
   Entra directo, como las de su área; su entrega la aprueba quien revisa el trabajo del referente
   (en CoreWork, Dirección: "a los referentes los aprueba Dirección"), así nadie se aprueba a sí mismo;
   Dirección se entera según lo que eligió en su web (punto 1).
9. ~~**Una espera sobre una propuesta.**~~ **Decidido (usuario, 2026-10-13: "si"): la espera empieza
   a contar recién cuando la propuesta se aprueba.** Mientras espera, "Colocar el estante" no figura
   trabada: la web dice que tiene una propuesta esperando aprobación. Aprobada, figura esperando a
   "Comprar los tornillos" y un atraso se explica por eso. Rechazada, la espera desaparece con ella y la
   tarea sigue normal. Una propuesta sin aprobar nunca traba una tarea comprometida.
10. ~~**Cambiar quién es la autoridad final.**~~ **Decidido (usuario, 2026-10-13: "si").** Lo hace
    Dirección sola desde su web, con dos cuidados: quien la recibe tiene que aceptar (el cambio vale
    recién entonces, y el espacio nunca queda sin autoridad final: Ismael sigue hasta que Martín
    acepta), y al administrador de plataforma le llega un aviso sólo informativo. Así una sesión
    abierta en un celular perdido no entrega el equipo sin que la otra persona acepte.
11. ~~**El tipo del objetivo.**~~ **Decidido (usuario, 2026-10-13: "si").** La web ofrece sólo los
    tipos que tienen sentido según dónde cuelga: sin padre, estratégico, sin preguntar; colgado de un
    estratégico, hito u operativo, con operativo marcado; colgado de un hito, operativo, sin preguntar.
    Con los nombres del pack del espacio (mecánica §1: un nivel se puede saltear).

## Porciones sugeridas (sin código; cada una con su prueba real antes de la siguiente)

Siguen el método del ADR 0022, decisión 16, y van después de sus porciones 3 y 4 o intercaladas,
como diga el usuario.

1. **Los objetivos desde la web** (decisión 1): crear un objetivo con nombre, de dónde cuelga y
   referente, por la puerta del equipo (Dirección) y por la de administración. Garantías: un
   integrante o un referente no crea objetivos; un objetivo no cuelga de otro espacio ni de dos
   padres; la auditoría guarda quién lo creó; una sesión de un espacio no crea en otro.
2. **Las esperas en el formulario** (decisión 2): el campo "espera a". Garantías: no se elige una
   tarea de otro espacio ni una cerrada; un ciclo se rechaza con su motivo; la tarea que espera no
   pasa a en curso mientras la otra no está terminada.
3. **La carga por la puerta del equipo, para Dirección y referentes** (decisión 3): el mismo
   formulario de la porción 2 de la plataforma, sin "quién la decidió". Garantías: un referente no
   crea fuera de su área; un integrante no crea comprometidas; quien la crea queda como quien la
   decidió; los controles del ADR 0022, decisión 9, siguen todos; la puerta del equipo no da
   funciones de plataforma aunque la persona sea administradora.
4. **La propuesta y su aprobación** (decisión 3, integrantes): el integrante propone para sí; el
   referente la aprueba con vista previa y confirmación. Garantías: una propuesta no tiene
   seguimiento ni avisos a otros; la aprueba sólo quien corresponde; la aprobación pide los cinco
   datos de una tarea comprometida; la auditoría separa quién propuso y quién aprobó; dos
   aprobaciones a la vez no cargan dos tareas. Necesita resueltos los `PENDIENTE` 3 a 6.
5. **Las jerarquías por Dirección** (decisión 4): áreas, roles y referentes desde la web del
   equipo. Garantías: ninguna área sin aprobador ni declaración de autoaprobación; el espacio nunca
   sin autoridad final; la cadena de aprobación sin ciclos; Dirección no toca otro espacio ni el
   núcleo; cada cambio auditado. Necesita resuelto el `PENDIENTE` 10.

Habilitar funciones nuevas con las dos firmas (decisión 5) llega con la configuración desde la web,
en la segunda versión.

## Consecuencias

- **La puerta del equipo deja de ser sólo de lectura.** Sus escrituras usan las mismas funciones de
  la base con dueño explícito que la de administración, y cada una revalida el puesto de la persona
  en la base en cada pedido.
- **La aceptación dentro de Leda vuelve** (ADR 0017, decisión 2, "Anotado para más adelante") para
  las propuestas, por la web; por chat sigue fuera.
- **El chat no cambia, pero sí lo que dice al derivar.** Un pedido de tarea nueva por chat sigue sin
  efectos (ADR 0017, decisión 1); ahora quien la carga puede ser la misma persona, desde "Tus
  tareas", o su referente. Necesita su conversación de prueba antes de tocar el motor.
- **Al aceptarse**, `AGENTS.md` ("Invariantes vigentes") tiene que decir que la tarea que carga el
  administrador entra comprometida por declaración, y la que se crea por la puerta del equipo, por
  la decisión de quien la crea o la aprueba en Leda; y "Qué no se hace" tiene que nombrar este ADR
  junto al 0022. La línea de los ADR 0017 y 0022 que remite acá pasa de "propuesta" a "rige", y
  la fila de este ADR en `docs/INDEX.md`, de "propuesta" a "aceptado".
- **Riesgo:** más personas escriben en la base. Lo compensan las garantías en las funciones de la
  base, no en la web, y la auditoría de cada cambio.
