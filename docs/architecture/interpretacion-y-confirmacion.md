# Interpretación, aclaración y confirmación

**Estado:** diseño vivo. Las decisiones de la sección 3 quedaron aceptadas en
[`ADR 0005`](../decisions/0005-interpretacion-y-confirmacion.md); la receta de
resolución (secciones 4 y 5) sigue en validación y se ajusta acá sin reabrirlo.
**Creado:** 2026-09-23
**Origen:** primera corrida del banco conversacional (`docs/STATUS.md`), pedido
del usuario de frenar la ambigüedad con botones, investigación con fuentes y el
paquete de trabajo previo `PRISMA-PACK-VERACIDAD-Y-AMBIGUEDAD-20260923` (externo
al repositorio; usado como experiencia, no como norma).

Este documento se actualiza con cada prueba. Lo que está en "Decidido" lo decidió
el usuario; lo que está en "Diseño propuesto" espera evidencia.

---

## 1. Problema

Las personas escriben como escriben: con faltas, sin tildes, con abreviaturas,
nombrando a medias ("lo del tablero", "marco") o contradiciéndose. Prisma tiene que
entender ese lenguaje sin convertir una interpretación probable en un cambio real.

Hoy falla de dos maneras, las dos verificadas:

- **Adivina.** En el banco, "el cableado del tablero no puede arrancar hasta que yo
  termine de programar el PLC, dejalo anotado" se tomó como pedido de tarea nueva
  en 10 de 10 corridas: el router de intención ve sólo el texto, no las tareas que
  ya existen (`docs/capacidades.md`, "Trampas conocidas").
- **Ejecuta sin mostrar.** Cambiar un estado, registrar o resolver un bloqueo y
  crear una dependencia se aplican en la base en el mismo turno, sin vista previa
  ni confirmación.

La causa de fondo de la primera: hoy la detección de la ambigüedad queda en manos
del modelo, y los modelos, por defecto, eligen la lectura más probable en lugar de
señalar la duda. Corregirlo ajustando el prompt es parchear frase por frase.

## 2. Principios

Tomados del paquete previo y de la investigación; se aplican a todo lo que sigue.

1. **Tolerante con la forma, estricto con las consecuencias.** Prisma entiende
   lenguaje imperfecto; no adivina una decisión que cambia algo.
2. **Sólo la ambigüedad material frena.** Es material si cambia la entidad, el
   estado, la fecha, el responsable, el alcance o el efecto. Una diferencia de
   redacción no justifica una pregunta. Preguntar de más también es un defecto.
3. **El modelo interpreta; el código decide.** El modelo propone lecturas. Si hay
   ambigüedad, qué es material y qué se ejecuta lo decide código determinista
   contra PostgreSQL.
4. **La similitud propone, nunca elige.** Un candidato encontrado por parecido se
   ofrece; no se selecciona solo.
5. **Sin candidatos reales no hay botones.** Si no hay a qué referirse, Prisma pide
   la referencia en texto; no inventa opciones.
6. **Un toque vale sólo para su propuesta exacta.** Mismo actor, misma
   conversación, misma propuesta, sin vencer. Un "dale" suelto no autoriza nada.
7. **Verdad actual → propuesta → efecto real → próxima acción visible.** Toda
   respuesta que cambia algo dice qué hay, qué se propone, si ya se aplicó y qué
   puede hacer la persona ahora.

Tipos de ambigüedad a cubrir (del paquete previo): referencial, de intención,
temporal, de estado, de alcance, de confirmación, de selección, de corrección, de
autoridad, contradictoria y por silencio. Se suma una que aportó el usuario:
**de puntuación**. Mucha gente no usa comas, y la misma secuencia de palabras
cambia de sentido: "no se iso lo que se pidió martin" puede ser "No sé, hizo lo
que pidió Martín" o "No, se hizo lo que pidió Martín". No es de referencia —los
embeddings no la ven— sino de intención: se detecta con la prueba 5.2 y se
aclara con botones que muestran cada lectura escrita con su puntuación.

## 3. Decidido (usuario, 2026-09-23)

- **Todo cambio relevante lleva vista previa y confirmación**, sea el mensaje claro
  o ambiguo.
- **Ante la duda, botones con propuestas completas.** Cada botón dice la acción
  entera, no sólo el objeto: "Pasar «Cablear tablero máq. 3» a revisión".
  Siempre hay un botón final **Ninguna, lo escribo** que deja escribir de nuevo.
- **Al elegir una propuesta, vista previa con decisión.** Tocar una opción no
  aplica nada: muestra la vista previa con **Confirmar**, **Modificar** y
  **Cancelar**. Cancelar descarta la propuesta sin aplicar nada y lo dice.
- **La vista previa con confirmación es la protección principal** (2026-09-24,
  tras la prueba 5.2). La detección de ambigüedad reduce preguntas y errores,
  pero no se confía en ella para evitar un efecto equivocado: ningún cambio se
  aplica sin que la persona vea exactamente qué va a pasar y lo confirme.
- **Cuando Prisma pregunta, pregunta con botones** (2026-09-24). Las respuestas
  posibles se ofrecen como botones ("¿Terminaste la tarea?" → [Sí] [No] [Todavía
  no sé]) para que la ambigüedad de una respuesta libre no llegue a existir. El
  texto libre queda para lo que no tiene opciones concretas y para "Ninguna, lo
  escribo".
- **Los apodos se aprenden preguntando, no se cargan de antemano** (2026-09-24).
  Una lista fija envejece: la gente cambia de apodo. Cuando una referencia a una
  persona no coincide con nadie ("tincho"), Prisma pregunta quién es con botones
  —las personas del equipo, ordenadas por el contexto del mensaje, más "Ninguno,
  lo escribo"— y, con la respuesta, registra ese apodo para esa persona ("tincho",
  "luquitas", "luki", "nahue").

  Es aprendizaje persistente, que `AGENTS.md` deja fuera del producto sin una
  decisión explícita. Esta es esa decisión, acotada a los apodos: el apodo lo
  confirma una persona, queda visible y se puede borrar, se registra en la
  auditoría con quién lo confirmó, vale dentro del espacio y nunca concede
  identidad ni autoridad —sólo resuelve a quién se refiere un mensaje—. Si un
  apodo aprendido coincide con más de una persona, vuelve a ser ambiguo y se
  pregunta. El ADR lo formaliza.

## 4. Diseño propuesto

### 4.1 Recorrido de un mensaje

```text
Mensaje
  ↓
1. Lectura del modelo: intenciones posibles + referencias tal como se escribieron
  ↓
2. Resolución de referencias en código, contra PostgreSQL
     coincidencia aproximada (faltas) + embeddings (significado) + filtros
     de espacio, alcance y permiso → candidatos con puntaje
  ↓
3. Estabilidad de la intención (sólo si pide un cambio)
     misma lectura en varias clasificaciones → estable; si no → ambigua
  ↓
4. Materialidad, en código
     consulta → responde con todos los candidatos, sin frenar
     cambio   → un candidato claro y una intención estable: vista previa
                varios candidatos o intención inestable: botones-propuesta
                ninguno: pide la referencia en texto
  ↓
5. Propuesta durable (pending_action) → vista previa → Confirmar / Modificar / Cancelar
  ↓
6. Confirmar: relee, revalida autoridad y estado, ejecuta una vez, audita,
   responde con el resultado real
```

El paso 2 también corrige el defecto del router: antes de decidir "tarea nueva",
ya sabe que "cableado del tablero" y "el PLC" son tareas existentes.

### 4.2 Ejemplo: mensaje ambiguo

Marcos tiene dos tareas de tablero abiertas y escribe "ya termine lo del tablero,
pasala a revision".

```text
Prisma: Tenés dos tareas de tablero abiertas. ¿Cuál pasamos a revisión?
  [Pasar «Cablear tablero máq. 3» a revisión]
  [Pasar «Revisar tablero máq. 4» a revisión]
  [Ninguna, lo escribo]
```

Toca la primera:

```text
Prisma: Tarea: Cablear tablero máq. 3
        Estado actual: En curso
        Nuevo estado: En revisión
        Todavía no se aplicó ningún cambio.
  [Confirmar] [Modificar] [Cancelar]
```

Confirma:

```text
Prisma: Listo: «Cablear tablero máq. 3» pasó de En curso a En revisión.
```

Un mensaje claro empieza directamente en la vista previa.

### 4.3 Vista previa y decisiones

- **Confirmar:** relee el recurso, verifica que la propuesta siga vigente, que la
  persona siga autorizada y que el estado no haya cambiado desde la vista previa;
  ejecuta una sola vez y audita. Un segundo toque devuelve el mismo resultado sin
  repetir el efecto.
- **Modificar:** pregunta qué cambiar, conserva lo válido y arma una vista previa
  nueva; la anterior queda reemplazada.
- **Cancelar:** descarta la propuesta, no toca el recurso y responde que no se
  aplicó nada y cuál sigue siendo el estado vigente.
- **Ninguna, lo escribo:** descarta las opciones y queda esperando el texto,
  conservando la intención que sí estaba clara.
- **Vencimiento:** una propuesta vence (`pending_action.vence_en` ya es
  obligatorio). Tocar un botón vencido explica que venció y no aplica nada.

### 4.4 Qué se reutiliza

- `pending_action` y `pending_action_option` (`db/esquema.sql`): dueño, vencimiento
  obligatorio, opciones con token de un solo uso y estados `inexistente`, `usada`,
  `vencida`, `obsoleta` (`src/prisma/pendientes.py`).
- `NecesitaElegir` (`src/prisma/herramientas.py`) y `_ambiguos`
  (`src/prisma/contexto.py`): hoy resuelven sólo el caso de una persona con nombre
  repetido; son el antecedente a generalizar.
- Botones y salida (`despachador._botones`, `salida.enqueue_outbox`).
- El banco (`tests/banco/`) con la comprobación `debe_preguntar` para medir.

### 4.5 Qué falta construir

- Paso 1: que el modelo devuelva lecturas y referencias, no una decisión.
- Paso 2: resolución de referencias con puntaje (requiere la prueba de 5.1).
- Paso 3: estabilidad de la intención (requiere la prueba de 5.2).
- Paso 4: la regla de materialidad.
- Paso 5 para mensajes claros: hoy las herramientas que escriben ejecutan directo.
- Detección de estado cambiado entre vista previa y confirmación: `PENDIENTE`
  verificar si `task` tiene una versión utilizable o hace falta agregarla.

## 5. Pruebas de concepto

Cada una se corre antes de construir el paso que la necesita, fuera del código de
Prisma, y su resultado se registra acá.

### 5.1 ¿Los embeddings separan lo claro de lo ambiguo?

**Pregunta:** con el modelo de embeddings de NaN (`qwen3-embedding`), ¿el puntaje
de parecido entre una referencia desprolija y las tareas existentes distingue un
caso claro (un candidato muy por encima del resto) de uno ambiguo (dos candidatos
parejos)?

**Método:**

1. Tareas y personas ficticias de CoreWork, con pares deliberadamente parecidos
   (dos tareas de tablero, Marcos y Mariano).
2. Entre 20 y 30 referencias desprolijas, cada una etiquetada de antemano como
   clara (con su tarea correcta), ambigua (con sus candidatas) o sin referente.
3. Para cada una: puntaje de cada tarea con embeddings solos, con coincidencia
   aproximada sola y con las dos combinadas; y con el `rerank` de NaN.

**Qué se mide:**

- aciertos del primer candidato en las claras;
- diferencia entre el primer y el segundo puntaje en claras frente a ambiguas;
- si existe un corte que separe claras de ambiguas sin mezclarlas.

No se fija un umbral antes de ver los datos: el corte sale de la prueba.

**Resultado (primera corrida, 2026-09-23):** los embeddings sirven para encontrar
la tarea correcta y para detectar la ambigüedad entre tareas; para personas sirve
la coincidencia aproximada, no los embeddings; el `rerank` no sirve como señal de
duda.

Datos: 12 tareas ficticias con pares parecidos a propósito, las 7 personas reales
del pack, 23 referencias a tareas (13 claras, 6 ambiguas, 4 sin referente) y 10 a
personas, etiquetadas **antes** de correr. Métodos: coincidencia aproximada
(`rapidfuzz` `WRatio`), embeddings (`qwen3-embedding` con instrucción de
búsqueda), los dos promediados y `rerank`. Señal de duda: el cociente entre el
segundo y el primer puntaje (cerca de 1 = dos candidatos parejos).

| Referencias a tareas | Acierto en claras | Cociente en claras | Cociente en ambiguas | Primer puntaje sin referente |
|---|---|---|---|---|
| Embeddings | 13/13 | 0,53 – 0,97 (mediana 0,74) | 0,89 – 0,99 | 0,30 – 0,45 (claras: desde 0,45) |
| Rerank | 13/13 | 0,00 – 0,59 | 0,09 – 0,91 | 0,00 – 0,12 (claras: desde 0,00) |
| Coincidencia aproximada | 5/13 | saturada en 0,855 | saturada | saturada |

| Referencias a personas | Acierto en claras | Cociente en claras | "mar" | Primer puntaje sin referente |
|---|---|---|---|---|
| Coincidencia aproximada | 7/7 | 0,40 – 0,83 | empate exacto entre Martín, Marcos y Mariano | 0,39 – 0,43 (claras: 0,90) |
| Embeddings | 7/7 | 0,79 – 0,98 | no separa | no separa |
| Rerank | 7/7 | 0,00 – 0,05 | puntajes casi nulos | 0,00 |

Lectura:

1. **Tareas, embeddings.** Aciertan la tarea en las 13 claras. Con un corte de
   cociente alrededor de 0,88, las 6 ambiguas quedan todas del lado "preguntar" y
   11 de 13 claras del lado "seguir". Las 2 claras que caen del lado "preguntar"
   son "el tablro de la maq 3" (máq. 3 frente a máq. 4) y "los planos de la paila"
   (dos tareas de planos): los embeddings casi no distinguen un número. El error es
   del lado seguro —pregunta de más, con la opción correcta primera—, nunca actúa
   sobre la tarea equivocada.
2. **Sin referente, débil.** El primer puntaje de "lo del horno" (0,45) queda
   pegado al de la clara más baja ("lo de los aps", 0,45). Un corte absoluto no
   alcanza para decir "no hay a qué referirse".
3. **Rerank, sobreconfiado.** Ordena bien cuando hay una sola respuesta, pero ante
   referencias ambiguas elige una con fuerza: "los planos" dio un cociente de 0,09
   y "lo del tablero" puso primero la tarea de la estufa. Usarlo como señal haría
   que Prisma actúe sin preguntar. Sirve, a lo sumo, para ordenar las opciones.
4. **Personas, coincidencia aproximada.** Separa limpio: las claras dan 0,90, los
   nombres ajenos 0,39–0,43, y "mar" empata exactamente entre los tres nombres que
   empiezan así, que es la señal de duda correcta. Los embeddings no sirven para
   nombres.
5. **Coincidencia aproximada para tareas, mal elegida.** `WRatio` se satura con
   referencias cortas; el resultado dice más del método elegido que de la técnica.

Límites: muestra chica, etiquetada por el mismo que diseñó la prueba, con un error
de etiqueta encontrado —"mar" también alcanza a Martín: la ambigüedad es de tres,
no de dos—. Es evidencia de dirección, no un umbral para fijar en código.

**Siguiente corrida** (pendiente):

- mensajes escritos por el usuario, no por el diseñador;
- otra medida de coincidencia aproximada para tareas (por tokens, no `WRatio`);
- una regla general para identificadores exactos: si la referencia trae un número
  o código que aparece en una sola candidata, ese dato decide (ataca "máq. 3" sin
  parchear la frase);
- una señal propia para "sin referente".

Artefactos: `dataset.json`, `poc.py` y `resultados.json`, hoy en la carpeta
temporal de la sesión; `PENDIENTE` decidir si se versionan.

**Resultado (segunda corrida, 2026-09-24):** 15 mensajes completos escritos y
etiquetados por el usuario, con los cortes de la primera corrida fijados antes de
verlos (cociente ≥ 0,88 = ambigua; primer puntaje < 0,45 = sin referente).

| Mensajes | Embeddings | Qué pasó |
|---|---|---|
| Claros de una sola tarea (8) | 6 bien; 2 preguntarían de más | "ya termine de integrar la comprimidora" y "planos de la paila": pregunta de más, del lado seguro |
| Ambiguos (3) | 2 detectados; 1 no | "como viene lo del tablero?" dio 0,86: quedó como clara hacia la máq. 4, apenas debajo del corte |
| Con varias tareas en el mismo mensaje (2) | marcados como ambiguos | "el dashboard ... hasta que tincho termine lo del eppi" nombra dos tareas; el método no distingue "dos referencias" de "una referencia dudosa" |
| Sin tarea, con persona (1) | bien | "Preguntale a Mar si terminó" no apunta a ninguna tarea |
| Sin referente (1) | mal | "lo del horno de la línea 2": 0,46, apenas sobre el corte; ofrecería tareas de planos |

| Personas | Resultado |
|---|---|
| Nombre escrito (martin, nahuel, lucas) | 4 de 4, palabra por palabra contra nombre y apellido |
| "Mar" | empate exacto entre Martín, Marcos y Mariano |
| "tincho" (apodo de Martín) | no se detecta: ninguna comparación de texto lo relaciona |

Lectura:

1. **Hay que resolver cada referencia por separado, no el mensaje entero.** Los
   mensajes reales nombran varias cosas a la vez. El paso 1 del recorrido tiene
   que devolver cada referencia suelta ("el dashboard", "lo del eppi", "tincho") y
   el paso 2 resolver cada una. Con referencias sueltas la primera corrida separó
   bien; con mensajes enteros, no.
2. **Ningún corte separa todo.** Los cocientes de claras y ambiguas se solapan
   ("integrar la comprimidora" 0,99 frente a "lo del tablero" 0,86). Conviene un
   corte más bajo, del lado de preguntar (alrededor de 0,85), y apoyarse en la
   vista previa con confirmación como red: si el detector cree que es clara y se
   equivoca, la persona ve la tarea equivocada en la vista previa y cancela antes
   de que se aplique nada.
3. **La regla de números, descartada tal como se escribió.** Empeoró dos
   mensajes: "línea 2" eligió "paila 2" y, en el mensaje largo, el "3" dejó sólo una
   de tres tareas. Un número sirve pegado a su sustantivo ("máq. 3"), y eso sale
   solo al resolver cada referencia por separado.
4. **Apodos: no se pueden deducir.** "tincho" no se relaciona con "Martín" por
   ninguna comparación. Decisión del usuario (sección 3): se pregunta y se
   aprende, no se carga una lista de antemano.
5. **"Sin referente" sigue débil.** Hace falta otra señal además del puntaje.
6. **Coincidencia por tokens para tareas (`token_set_ratio`), descartada**: peor
   que los embeddings en casi todos los mensajes.

**Resultado (tercera corrida, 2026-09-24):** los mismos 15 mensajes, ahora como
va a funcionar el recorrido. Paso 1: `deepseek-v4-flash` (temperatura 0, sin ver
tareas ni equipo) separa las referencias de cada mensaje tal como están
escritas. Paso 2: cada referencia se resuelve por separado.

| Resultado | Mensajes |
|---|---|
| Correcto | **11 de 15** |
| Inseguro (elige una tarea equivocada o no pregunta ante la duda) | **0** |
| Pregunta de más, del lado seguro | 2: "integrar la comprimidora", "los planos de la paila" |
| Pregunta innecesaria | 1: "lo del horno" ofrece tres tareas que no son |
| Incompleto | 1: "lo que estaba haciendo del eppi" quedó como sin referente |

Los cortes 0,88 y 0,85 dieron exactamente lo mismo.

Lectura:

1. **Separar las referencias resolvió los mensajes con varias tareas.** El mensaje
   largo por voz sacó sus tres tareas bien; el modelo extrajo referencias limpias
   en los 15 mensajes, incluso con faltas ("la integrasion de la comprimidor en
   corelavs"), y no se desvió.
2. **Cero errores inseguros.** Ningún mensaje terminó en una tarea equivocada ni
   dejó de preguntar ante un caso ambiguo.
3. **Lo que falla ahora es el borde "sin referente", en los dos sentidos.** "lo
   que estaba haciendo del eppi" quedó debajo del corte absoluto aunque "EPPI"
   está literal en una sola tarea; "lo del horno" quedó arriba aunque "horno" no
   está en ninguna. Hipótesis a probar, general y no por frase: una palabra
   distintiva de la referencia que aparece en una sola tarea es señal fuerte
   ("eppi"), y una referencia cuyas palabras distintivas no aparecen en ninguna es
   señal de "sin referente" ("horno").
4. **"tincho" quedó sin resolver**, que con la decisión de la sección 3 es lo
   correcto: Prisma pregunta quién es.

Límites: la extracción se corrió una vez; falta medir si es estable entre
corridas. El corte 0,85 se propuso después de ver la segunda corrida.

**Resultado (cuarta corrida, 2026-09-24): señal de palabras distintivas.** Regla
general, aplicada a cada referencia antes de los embeddings:

- **Ancla:** una palabra de la referencia que coincide —tolerando faltas y
  variantes ("bakup", "servidores")— con palabras de **una sola** tarea decide esa
  tarea. Si dos palabras anclan tareas distintas, es ambigua. Los números no
  anclan.
- **Sin referente:** si ninguna palabra de la referencia coincide con ninguna
  palabra de ninguna tarea y el mejor puntaje es bajo (< 0,55), no hay a qué
  referirse.
- Si no aplica ninguna de las dos, deciden los embeddings (cociente ≥ 0,88 =
  ambigua).

| Conjunto | Correctos | Inseguros | Resto |
|---|---|---|---|
| Mensajes del usuario (15) | **15** | **0** | — |
| Referencias de la corrida 1 (23) | 21 | **0** | "el tablro de la maq 3" pregunta de más; "lo de los aps" queda sin referente (Prisma pregunta a qué se refiere) |

La extracción del paso 1 resultó estable: 0 de 15 mensajes cambiaron en 3
repeticiones, y una segunda tanda de 3 dio lo mismo.

El primer intento de esta corrida tuvo un defecto de la regla —contaba
"servidor" y "servidores" como palabras distintas y ancló mal "lo de los
servidores", un resultado inseguro—, corregido midiendo la coincidencia desde la
referencia. Ese mismo intento mostró en el mensaje 15 puntajes corridos una
posición; no se reprodujo aislado ni al repetir la corrida, y los embeddings
dieron los mismos valores en llamadas separadas. Queda sin explicar y a vigilar.

Límites: la regla y los cortes se ajustaron mirando estos mismos dos conjuntos.
Que den bien acá no prueba que generalicen; hace falta un conjunto nuevo, no
visto, con mensajes reales.

**Receta que queda para el paso 2**, sujeta a esa confirmación:

1. el modelo separa las referencias del mensaje, sin ver tareas ni equipo;
2. cada referencia a tarea: ancla por palabra distintiva → si no, sin referente
   por falta de coincidencia → si no, embeddings con cociente;
3. cada referencia a persona: coincidencia por palabra contra nombre y apellido,
   más los apodos aprendidos; sin coincidencia, se pregunta quién es;
4. `rerank` no interviene en la decisión.

### 5.2 ¿Clasificar varias veces detecta la intención dudosa?

**Pregunta:** si se clasifica el mismo mensaje varias veces, ¿los mensajes
ambiguos ("lo del plc está parado", "pasala a revisión, no, mejor dejala... bah
no sé") producen lecturas distintas y los claros no?

**Método:** mensajes claros y ambiguos del banco, clasificados 5 veces cada uno;
medir el acuerdo por mensaje y la latencia agregada.

**Resultado (2026-09-24):** ninguno de los dos métodos detecta la duda de
intención de forma confiable con `deepseek-v4-flash`. La protección real es la
vista previa con confirmación.

Datos: 18 mensajes (10 claros, 8 ambiguos), con la última pregunta de Prisma como
contexto cuando la hubo; incluye el ejemplo del usuario sin coma ("no se iso lo que
se pidió martin") y su versión con coma como control. Etiquetas del diseñador,
discutibles en tres casos (8, 17 y 18). Dos métodos:

- **A — clasificar 5 veces** (temperatura 0,3, la de producción, y 0,7).
- **B — pedir todas las lecturas razonables** en una llamada, cada una con el
  mensaje reescrito con puntuación.

| Método | Ambiguos detectados | Claros con duda falsa | Latencia |
|---|---|---|---|
| A, t=0,3 | **0 de 8** | 0 de 10 | 6–17 s por las 5 llamadas |
| A, t=0,7 | **0 de 8** | 0 de 10 | 6–19 s |
| B | 4 de 8 | 1 de 10 | **4–73 s** por una llamada |

Lectura:

1. **Clasificar varias veces no sirve con este modelo.** Respondió lo mismo las 5
   veces en los 18 mensajes, incluso a temperatura 0,7: se equivoca siempre del
   mismo modo, con seguridad. Es lo contrario de lo que la investigación daba como
   señal práctica; queda descartado para este modelo.
2. **Pedir las lecturas detecta la mitad y falla en el caso clave.** Detectó
   "lo del plc esta parado" (bloqueo o pregunta), "pasala a revision, no, mejor
   dejala... bah no se" y "despues habria q revisarlo". Pero el ejemplo sin coma
   del usuario salió con una sola lectura, y equivocada ("No se hizo lo que se
   pidió, Martín."), mientras que la versión con coma —la clara— salió como dudosa.
   Además inventó lecturas absurdas ("No puedo. Avanza con el dashboard...") y su
   latencia, de hasta 73 segundos, la hace inviable en cada mensaje.
3. **Las reescrituras sí sirven para botones** cuando la lectura es buena ("No sé
   si pasarla a revisión o dejarla como está."; "Sí, pasala a revisión.").

Consecuencias de diseño:

- **La vista previa con confirmación es la protección, no la detección.** Si
  Prisma entendió mal la intención, la vista previa lo muestra ("Nuevo estado: En
  revisión") y la persona cancela o modifica antes de que se aplique nada. Por eso
  la decisión de confirmar todo cambio relevante es la pieza que sostiene el
  diseño.
- **Evitar el texto libre cuando Prisma pregunta.** El ejemplo de la coma nace de
  una respuesta libre a "¿Terminaste la tarea?". Si esa pregunta llega con botones
  ([Sí] [No] [Todavía no sé]), la ambigüedad no llega a existir.
- **La detección de intención queda como mejora, no como garantía.** Se puede
  volver a probar con otro modelo o con otro planteo; no bloquea el resto del
  diseño.

## 6. Cómo se mide el diseño terminado

Con el banco (`docs/validation/README.md`, "Banco conversacional") y, después, por
Telegram real:

- **Aclaración:** en los escenarios ambiguos, Prisma no aplica nada y ofrece
  botones o pregunta.
- **Preguntas de más:** en los escenarios claros, no pregunta; va a la vista previa.
- **Ningún efecto sin confirmación:** ningún escenario cambia la base sin un
  Confirmar.
- **Acierto:** la vista previa propone la tarea y el cambio correctos.

La línea base con mensajes desprolijos se corre recién con el diseño listo para
comparar, no antes.

## 7. Preguntas abiertas

- **Qué es un cambio relevante.** Propuesto: toda herramienta que escribe
  (`registrar_bloqueo`, `resolver_bloqueo`, `actualizar_estado`,
  `crear_dependencia`, `quitar_dependencia`, `adjuntar_evidencia`,
  `aprobar_tarea`, `crear_objetivo`). `PENDIENTE`.
- **pgvector.** Prisma va a correr en un servidor, así que el destino natural es
  guardar un vector por tarea en PostgreSQL con pgvector, sin un servicio aparte.
  Las pruebas hasta ahora no usan pgvector: calculan los parecidos en memoria. Datos
  verificados (2026-09-24): pgvector soporta PostgreSQL 13 a 18 y busca exacto sin
  índice; guarda hasta 16.000 dimensiones, pero sus índices aceptan hasta 2.000
  (4.000 en media precisión); `qwen3-embedding` devuelve 4.096, y NaN acepta pedir
  menos (`dimensions: 1024` probado). Con decenas o cientos de tareas por espacio
  la búsqueda exacta sin índice alcanza. `PENDIENTE`: repetir la prueba 5.1 con
  1.024 dimensiones para ver si se pierde precisión; instalar pgvector en local
  (en Windows se compila con Visual Studio) o usar un contenedor; qué pasa con los
  vectores cuando una tarea cambia de título.
- **Costo del paso 3.** Clasificar varias veces agrega latencia. Se decide con el
  resultado de 5.2: siempre, o sólo cuando el mensaje pide un cambio.
- **Cantidad de botones.** Propuesto: hasta cuatro propuestas más "Ninguna, lo
  escribo". No hay estudios controlados; se ajusta con uso real.
- **Vencimiento de una propuesta.** `PENDIENTE` el plazo por defecto.

## 8. Fuera de alcance por ahora

- Recuperar documentos o evidencias por significado (RAG sobre archivos).
- Lectura de fotos o PDFs de evidencia.
- Verificación de identidad por correo en el alta de integrantes: pertenece al
  panel de plataforma.

## 9. Historial

| Fecha | Cambio |
|---|---|
| 2026-09-23 | Versión inicial: problema, principios, decisiones del usuario, diseño propuesto y pruebas 5.1 y 5.2 pendientes |
| 2026-09-23 | El usuario confirma Cancelar junto a Confirmar y Modificar: pasa de pregunta abierta a decidido |
| 2026-09-23 | Primera corrida de la prueba 5.1: embeddings útiles para tareas, coincidencia aproximada para personas, rerank descartado como señal de duda |
| 2026-09-24 | Segunda corrida con mensajes del usuario: resolver cada referencia por separado; corte más bajo apoyado en la vista previa; regla de números descartada; apodos por persona; ambigüedad de puntuación agregada |
| 2026-09-24 | Decisión del usuario: los apodos se aprenden preguntando, con alcance acotado (excepción explícita al aprendizaje persistente) |
| 2026-09-24 | Tercera corrida con referencias extraídas por el modelo: 11 de 15 correctos, 0 inseguros; el borde "sin referente" queda como lo pendiente |
| 2026-09-24 | Cuarta corrida con palabras distintivas: 15 de 15 en mensajes del usuario y 21 de 23 en la corrida 1, 0 inseguros; extracción estable; falta un conjunto nuevo no visto |
| 2026-09-24 | Prueba 5.2: ni clasificar 5 veces (0 de 8) ni pedir lecturas (4 de 8, hasta 73 s) detectan la duda de intención con fiabilidad; la vista previa con confirmación queda como la protección y se evita el texto libre en las preguntas de Prisma |
| 2026-09-24 | El usuario confirma: la vista previa con confirmación es la protección principal y las preguntas de Prisma van con botones |
