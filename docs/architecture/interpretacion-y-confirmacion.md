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

- ~~Paso 1: referencias separadas por el modelo~~: construido (2026-09-24), en la
  misma llamada de `route_intent` (`trabajos`, `personas`).
- ~~Paso 2: resolución de referencias~~: construido con Jev y la verificación
  (§5.6, §5.8 a §5.10); dudas con botones, "Ninguna, lo escribo" y "Es una tarea
  nueva"; respuestas que nombran la tarea. Pendiente: resolver personas y apodos
  (ADR 0005 punto 5), y decir "no encuentro esa tarea" en vez de ofrecer una
  parecida.
- Paso 3: estabilidad de la intención (requiere la prueba de 5.2).
- Paso 4: la regla de materialidad.
- ~~Paso 5 para mensajes claros~~: construido (2026-09-24). Las 8 herramientas
  que escriben pasan por vista previa con Confirmar, Modificar y Cancelar
  (`Herramienta.preparar`, `pending_action`); ver `docs/capacidades.md`.
- ~~Detección de estado cambiado entre vista previa y confirmación~~: construido
  con una huella del estado leído por cada preparación, sin versión en `task`.
- Pendiente de la vista previa: un ciclo de dependencias se detecta recién al
  confirmar (lo frena la base), no en la vista previa.
- ~~Botón "Ninguna, lo escribo"~~: construido; espera la aclaración 30 minutos,
  como Modificar. La propuesta vence a las 8 h heredadas de `pending_action`; el
  plazo por defecto sigue abierto (§7).

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

**Resultado (quinta corrida, 2026-09-24): lote nuevo, no visto — la receta no
generaliza.** 15 mensajes nuevos escritos por el usuario, con la receta de la
cuarta corrida sin ningún cambio.

| Resultado | Mensajes |
|---|---|
| Correcto | 7 de 15 |
| **Inseguro** (elige sin preguntar) | **3**: "lo de los planos" → T6 (eran T5 o T6); "lo de dashboar" → T9 (eran T9 o T10); "las cosas de IT" → sin referente (eran cuatro tareas de IT) |
| Incompleto (no encuentra la tarea; Prisma preguntaría) | 3: "lo del wifi", "la migración", "la red que había quedado pendiente" |
| Pregunta de más | 2: "el tablero de la 3"; una referencia del mensaje largo |

Personas: "mariano" bien; "marquitos" y "Luquitas" sin coincidencia, que es lo
correcto con apodos todavía no aprendidos; "nahual" (falta de tipeo de Nahuel)
tampoco coincide —el corte de parecido de nombres no lo alcanza—.

Corrección de etiqueta hecha por el usuario: el diseñador había marcado "lo de
dashboar" como clara hacia T9 porque la palabra aparece en ese título. Es un error
de concepto: **"dashboard", "interfaz HMI" y "CoreLabs" son nombres que la gente
usa para lo mismo**, como un apodo. La etiqueta correcta es T9 o T10.

Lectura:

1. **Las reglas por palabras sobreajustaron.** La regla de "sin referente" por
   falta de palabras en común se equivoca con sinónimos ("wifi" o "red" por
   access points) y con variantes ("migración" frente a "Migrar"). La del ancla
   se equivoca con el vocabulario del equipo: una palabra que aparece en un solo
   título no garantiza que la persona hable de esa tarea.
2. **Hacen falta dos fuentes que no son palabras sueltas:**
   - **vocabulario del equipo aprendido**, igual que los apodos: "dashboard",
     "interfaz HMI" y "CoreLabs" nombran lo mismo; "wifi" y "red" son los access
     points. Se aprende preguntando la primera vez;
   - **referencias a un área o a una persona** ("las cosas de IT", "lo de
     Mariano") que abarcan todas sus tareas y se resuelven preguntando cuál.
3. **La protección sigue siendo la vista previa.** Los tres casos inseguros
   habrían terminado en una vista previa con la tarea equivocada, que la persona
   cancela o modifica. Ninguno aplica nada solo.
4. **Lo que sí se sostuvo:** la separación de referencias por el modelo, los
   embeddings para encontrar candidatas y la coincidencia de nombres.

Próximo paso de la prueba: rediseñar la decisión —el ancla no decide sola; "sin
referente" no se declara sólo por falta de palabras en común; vocabulario y
referencias por área o persona— y validar con un tercer lote no visto, no con
estos.

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

### 5.3 ¿Jev detecta la duda de intención que DeepSeek no detecta?

**Pregunta:** Jev (TypeSafe AI) elige una opción de una lista y devuelve una
probabilidad por opción. ¿Esa probabilidad separa los mensajes ambiguos de los
claros, donde `deepseek-v4-flash` falló (prueba 5.2)?

**Verificado (2026-09-24):** está en OpenRouter como `typesafe/jev-1.13` (alias
`~typesafe/jev-latest`), por una API propia de OpenRouter
(`POST https://openrouter.ai/api/v1/systemone`), no por la de chat; el tipo
**Choice** devuelve la opción elegida, una probabilidad por opción y una
confianza. La documentación no dice cuántas opciones admite ni qué idiomas.

**Según la investigación, sin verificar una por una:** el propio proveedor aclara
que la calibración vale en conjunto y no por respuesta; una evaluación de terceros
encontró sobreconfianza justo en preguntas ambiguas (44,7 % de acierto con 0,74 de
confianza media); no hay evidencia en español; la velocidad y el costo sí
coinciden con lo anunciado en una prueba independiente.

**Método:** los mismos 18 mensajes de 5.2 como una elección entre las 12
intenciones; medir ambiguos detectados por probabilidad máxima o diferencia entre
las dos primeras, falsas alarmas en claros, acierto en claros, latencia y costo.
Los cortes salen de los datos.

**Criterio:** se adopta para la detección de intención sólo si detecta la mayoría
de los ambiguos con pocas falsas alarmas, acierta en los claros al menos como
DeepSeek y maneja el español desprolijo. Si no, sigue DeepSeek con la vista previa
como protección.

**Requiere:** una clave de OpenRouter. Primer paso sólo con datos ficticios.

**Resultado (2026-09-24):** Jev sirve para **elegir la tarea** —mucho mejor que las
reglas por palabras en el lote no visto— y da una señal de duda de intención
mejor que DeepSeek, pero insuficiente como garantía. Datos ficticios; 0,35–0,51 s
por llamada; alrededor de USD 0,000014 por llamada.

Parte A — intención, los 18 mensajes de 5.2 (Choice entre 12 intenciones):

| Corte (duda si la probabilidad más alta es menor) | Ambiguos detectados | Claros con duda falsa |
|---|---|---|
| 0,6 | 3 de 8 | 0 de 10 |
| 0,8 | 4 de 8 | 2 de 10 |
| 0,9 | 5 de 8 | 2 de 10 |

Acierto en claros: 8 de 10 (los dos desvíos son etiquetas discutibles: "xq martin
no me paso la informacion" como dependencia; "dalo x resuelto" como cambio de
estado). El ejemplo sin comas del usuario sigue sin detectarse (0,98 "no
terminado"). DeepSeek, en la misma prueba: 0 de 8 clasificando cinco veces.

Parte B — tareas, Choice entre las 12 tareas más "ninguna", sobre las referencias
ya separadas por DeepSeek:

| Lote 2 (no visto por nadie) | Reglas por palabras (corrida 5) | Jev |
|---|---|---|
| Claras (9) | 4 bien, 3 sin encontrar, 2 preguntan de más | **9 bien** ("wifi", "la red", "la migración", "copia de seguridad", "el tablero de la 3") |
| "lo de los planos" (T5 o T6) | elige T6: inseguro | reparte 0,37 / 0,32 / 0,31: **duda correcta** |
| "lo de dashboar" (T9 o T10) | elige T9: inseguro | elige T9 con 0,95: **inseguro** |
| "las cosas de IT" (cuatro tareas) | sin referente | "ninguna" con 1,0: no encuentra |
| "lo de mariano" (sus dos tareas) | resuelve la persona | "ninguna" con 1,0 |
| "la cámara de frío" (no existe) | sin referente | "ninguna" con 0,95: bien |

En el lote 1 acertó todas las claras, pero ante las referencias vagas ("lo del
tablero", "lo de la comprimidora", "lo de los servidores") respondió "ninguna"
(0,65–0,73) en lugar de repartir entre las candidatas.

Lectura:

1. **Jev entiende sinónimos y variantes que las reglas no alcanzaban** ("wifi" y
   "red" por access points, "la interfaz" por CoreLabs, "migración" por
   "Migrar"). Pasa a ser el candidato para decidir la tarea, en lugar de las
   reglas por palabras.
2. **Sigue sin saber lo que sólo sabe el equipo.** "dashboard" por CoreLabs, las
   áreas ("las cosas de IT") y "lo de Mariano" necesitan que las opciones lleven
   más datos —área, responsable, vocabulario aprendido— o una pregunta aparte.
3. **La opción "ninguna" absorbe lo vago.** Conviene separar dos preguntas: si la
   referencia apunta a una tarea concreta (sí o no) y, si apunta, cuál; y mostrar
   las candidatas cuando se reparte.
4. **Para la intención, la vista previa sigue siendo la protección.** Jev da una
   señal graduada que DeepSeek no daba y se puede usar para decidir cuándo
   ofrecer botones, pero falla el caso clave de puntuación.
5. **Español desprolijo, bien** en esta muestra: faltas, sin tildes, abreviaturas.

Límites: muestras chicas; ningún corte fijado; Jev está en beta. Antes de usar
datos reales hay que decidir si se aceptan los términos de privacidad de TypeSafe
para mandar títulos de tareas y nombres del equipo.

**Segunda versión (2026-09-24): opciones enriquecidas y dos preguntas.** Cada
tarea lleva área y responsable; el vocabulario del equipo va como contexto ("a
CoreLabs también le dicen dashboard o interfaz HMI", simulando lo aprendido o
cargado en el alta); en la misma llamada, dos preguntas: si la referencia apunta a
una tarea, a varias (un área, una persona) o a ninguna, y a cuál.

Regla de decisión: "ninguna" ≥ 0,6 → sin referente; "varias" ≥ 0,5 → preguntar
entre las tareas con probabilidad ≥ 0,1; la tarea más probable ≥ 0,85 con 0,4 de
diferencia → clara; si no, preguntar. El corte de 0,85 se eligió mirando los lotes
1 y 2 (con 0,75 quedaban dos inseguros) y **queda congelado** para el lote 3.

| Con el corte congelado | Lotes 1 y 2 (30 mensajes) |
|---|---|
| Correctos | 24 |
| Inseguros | **0** |
| Preguntas de más | 4 |
| Preguntas innecesarias ("lo del horno", "la cámara de frío") | 2 |

Lo que resolvió respecto de la primera versión: "lo de Mariano" y "las cosas de
IT" ahora preguntan entre sus tareas; "lo de dashboar" pregunta, con el
vocabulario en contexto. Lo que empeoró: con opciones más cargadas, Jev dejó de
reconocer lo que no existe ("horno", "cámara de frío" ya no salen como
"ninguna"); con el corte de 0,85 terminan en una pregunta, no en un efecto.

**Próximo paso:** tercer lote no visto con esta configuración congelada.

### 5.4 ¿Combinar las tres modalidades de Jev da una señal más certera?

**Pregunta (propuesta del usuario):** preguntar lo mismo de varias formas a la vez
—Choice entre las opciones, un Noul (sí o no) por opción y un Score de claridad—
y decidir por el acuerdo entre ellas.

**Fundamento:** la documentación de TypeSafe recomienda "partir una pregunta
difícil en preguntas angostas, cada una sobre una sola propiedad" y combinarlas en
el código; van todas en una misma llamada y corren en paralelo.

**Regla, sin pesos y con cortes redondos fijados antes de correr:** clara sólo si
Choice ≥ 0,8, los Noul ≥ 0,5 son exactamente la opción del Choice y el Score pone
≥ 0,6 en "clara"; ninguna (sólo tareas) si ningún Noul llega a 0,5 y el Score pone
≥ 0,6 en "no corresponde"; si no, duda, con candidatas = los Noul ≥ 0,5 más las dos
primeras del Choice.

**Resultado (2026-09-24):**

| Intención (18 mensajes) | DeepSeek (5.2) | Choice solo (5.3) | Combinado (5.4) |
|---|---|---|---|
| Ambiguos detectados | 0 de 8 | 4 de 8 | **8 de 8** |
| Claros con duda falsa | 0 de 10 | 2 de 10 | **5 de 10** |

| Tareas, lotes 1 y 2 (30 mensajes) | Choice enriquecido (5.3 v2) | Combinado (5.4) |
|---|---|---|
| Correctos | **24** | 14 |
| Inseguros | 0 | 0 |
| Preguntas de más o innecesarias | 6 | 16 |

Lectura:

1. **Para la intención, combinar funciona**: detecta todos los ambiguos, incluido
   el ejemplo sin comas del usuario. El costo son falsas alarmas, y su causa es del
   diseño de la prueba, no de Jev: las 12 intenciones se superponen ("voy por la
   mitad" es a la vez "avance parcial" y "no terminado", y ambas son ciertas). Esa
   duda no es material: las dos lecturas llevan a la misma acción. Corrección, que
   sale del principio de ambigüedad material y no de ajustar números: agrupar las
   intenciones por la acción que disparan y marcar duda sólo cuando las lecturas
   altas apuntan a acciones distintas.
2. **Para las tareas, combinar es demasiado cauteloso.** Los Noul por tarea salen
   bajos incluso ante referencias claras (0,45–0,75) y el Score rara vez llega a
   "clara". Choice con opciones enriquecidas sigue siendo mejor.
3. **Ambigüedad real del idioma:** "tablero" también se usa por "dashboard", así
   que "el tablero de la 3" levantó el Noul de CoreLabs. Es vocabulario del equipo.

**Próximo paso:** intención combinada con agrupación por acción; tareas con Choice
enriquecido; congelar ambas y validar con el lote 3.

### 5.5 Las siete combinaciones de modalidades

**Pregunta (propuesta del usuario):** probar cada modalidad sola y todas sus
combinaciones. Una sola ronda de llamadas (cada una trae las tres respuestas) y
las siete combinaciones evaluadas sobre las mismas respuestas. Reglas fijadas antes
de correr: Choice decide si la primera tiene ≥ 0,8 y 0,4 de diferencia; Noul, si
exactamente una opción tiene ≥ 0,5; Score, si pone ≥ 0,6 en "clara" (sólo detecta,
no elige). Una combinación decide sólo si todas sus modalidades dicen "clara" y
eligen lo mismo. En intención, "avance parcial" y "no terminado" cuentan como la
misma acción; "no sé" queda aparte.

| Intención (18) | Ambiguos detectados | Falsas alarmas |
|---|---|---|
| Choice | 5 de 8 | 2 de 10 |
| Noul | 5 de 8 | 3 de 10 |
| Score | 5 de 8 | 3 de 10 |
| **Choice + Noul** | **7 de 8** | **3 de 10** |
| Choice + Score | 6 de 8 | 5 de 10 |
| Noul + Score | 8 de 8 | 6 de 10 |
| Las tres | 8 de 8 | 6 de 10 |

| Tareas, lotes 1 y 2 (30) | Correctos | Inseguros |
|---|---|---|
| Choice | 26 | 3 |
| Noul | 15 | 4 |
| Choice + Noul | 14 | 2 |
| Choice + Score | 17 | 0 |
| Noul + Score | 10 | 1 |
| Las tres | 14 | 0 |
| Choice enriquecido con pregunta de alcance (5.3 v2) | **24** | **0** |

Lectura:

1. **Intención: combinar mejora la detección.** Choice + Noul es el mejor
   equilibrio. Sumar Score detecta todo, pero pregunta en 6 de cada 10 mensajes
   claros.
2. **Tareas: combinar no supera a Choice enriquecido con la pregunta de alcance**
   ("¿una tarea, varias o ninguna?"). Choice solo acierta más pero con tres
   inseguros; las combinaciones con Noul o Score se vuelven demasiado cautelosas.
3. **Variación entre corridas:** la combinación de las tres dio 5 falsas alarmas en
   5.4 y 6 acá, con las mismas preguntas. Jev no responde idéntico en cada llamada;
   los resultados se leen como tendencia, no como cifra exacta.

**Configuración congelada para el lote 3:** intención con Choice + Noul y
agrupación por acción; tareas con Choice enriquecido y pregunta de alcance (5.3
v2, corte 0,85).

### 5.6 Validación con el lote 3, no visto

15 mensajes nuevos del usuario, con dos casos de intención marcados por él: sin
signo de pregunta, "que onda con lo eléctrico falta mucho" y "esta listo lo de las
comunicaciones" se pueden leer como pregunta o como afirmación. Configuración
congelada, sin ningún cambio (2026-09-24).

| Tareas | Mensajes |
|---|---|
| Correctos | **11 de 15** |
| **Inseguros** | **0** |
| Pregunta de más, con la correcta entre las opciones | 2 ("esta listo lo de las comunicaciones"; "el dash de lotes") |
| Pregunta innecesaria | 2 ("el techo del galpón", "los compresores de aire": ofrece tareas que no son; nada se aplica y está "Ninguna, lo escribo") |

| Intención | Resultado |
|---|---|
| Ambiguos marcados por el usuario | **2 de 2 detectados** |
| Claros con duda falsa | 4 de 13 |
| Claros bien resueltos | 9 de 13 |

Personas: "Lucas" y "Nahuel" bien; "tincho" sin coincidencia, que con la decisión de
aprender apodos lleva a preguntar quién es.

Lectura:

1. **La configuración generaliza en lo que importa:** cero inseguros en tareas con
   mensajes que ninguna versión vio, frente a tres de las reglas por palabras en
   el lote 2. Lo que queda son preguntas de más, del lado seguro. El doble control
   de 5.8 mostró que este cero no era estable en los lotes 1 y 2; se corrigió con
   una pregunta de verificación.
2. **"No existe" sigue siendo el punto débil:** ante algo que no está en la lista,
   Jev ofrece tareas parecidas en lugar de decir que no hay. Seguro, pero molesto.
3. **La intención detecta la duda que el usuario señaló** —preguntas sin signo—
   con un costo de una falsa alarma cada tres o cuatro mensajes claros.
4. **Hipótesis para bajar falsas alarmas, sin probar:** agrupar las intenciones
   por la herramienta que disparan, no por intención. "Terminé con el plc" dudó
   entre "informar terminado" y "pedir cambio de estado", que llevan a la misma
   propuesta (pasar a revisión). Este lote ya fue visto: la hipótesis se valida
   con otro.

**Receta resultante para el paso 2**, sujeta a esa mejora:

1. DeepSeek separa las referencias del mensaje, sin ver tareas ni equipo.
2. Por cada referencia a tarea, Jev en una llamada: Choice de alcance (una tarea,
   varias, ninguna) y Choice entre las tareas con título, área y responsable, con
   el vocabulario del equipo como contexto. "Ninguna" ≥ 0,6 → no existe; "varias"
   ≥ 0,5 → preguntar entre las tareas con ≥ 0,1; la primera ≥ 0,85 con 0,4 de
   diferencia → clara; si no, preguntar.
   **Verificación (agregada en 5.8):** si decidió clara, una segunda llamada con
   un Noul sobre la tarea elegida: ¿la referencia habla exactamente de esta tarea
   y no de otra parecida? Con menos de 0,5, en lugar de elegirla se pregunta con
   esa tarea como opción.
3. Por mensaje, Jev en una llamada: Choice entre intenciones y un Noul por
   intención; decide sólo si ambos coinciden en una acción; si no, preguntar con
   las lecturas como botones.
4. Personas por coincidencia de nombres y apodos aprendidos; sin coincidencia,
   preguntar quién es.
5. Toda propuesta termina en vista previa con Confirmar, Modificar y Cancelar.

Términos de privacidad de TypeSafe aceptados por el usuario el 2026-09-24
([`ADR 0006`](../decisions/0006-jev-para-resolver-referencias-e-intencion.md)).

### 5.7 Escala: 12 tareas frente a 200

**Pregunta (planteada por el usuario):** el diseñador había afirmado, sin medirlo,
que con muchas tareas Jev sería caro y elegiría peor. Se midió con las referencias
del lote 3, la configuración congelada y dos universos: las 12 tareas de siempre, y
200 (las 12 más 188 ficticias realistas, con muchas parecidas a propósito).

| | 12 tareas | 200 tareas |
|---|---|---|
| Latencia por llamada (mediana) | 0,39 s | 0,46 s |
| Tokens de entrada por llamada | ~964 | ~8.819 |
| Costo por llamada | US$ 0,00004 | US$ 0,00037 |
| Eligió una tarea equivocada sin preguntar | 0 | **0** |
| Correctos | 9 de 15 | 6 de 15 |
| Preguntas de más o innecesarias | 5 | 7 |

Lectura:

1. **Latencia y costo escalan bien:** la afirmación previa del diseñador era
   incorrecta.
2. **Con más tareas pregunta más,** en parte con razón: con varias tareas de PLC,
   "terminé con el plc" es ambiguo de verdad.
3. **Sigue sin elegir mal** con 200 tareas; con 12, el doble control de 5.8
   encontró un caso repetido.
4. **Límite real:** la ventana de 32.000 tokens de Jev, unas 700 tareas.
5. **Variación entre corridas:** con 12 tareas y la misma configuración dio 9
   correctos; en 5.6 había dado 11. Los resultados se leen como tendencia.

### 5.8 Doble control y pregunta de verificación

**Pregunta (planteada por el usuario):** antes de fijar la base, ¿los resultados se
sostienen si se repiten? Se repitió cinco veces la configuración congelada sobre los
45 mensajes de los lotes 1 a 3, con 12 y con 200 tareas, y la intención sobre 33
mensajes (2026-09-24).

| Configuración congelada, 5 repeticiones | Resultado |
|---|---|
| Tareas, 12: correctos | 35 a 37 de 45 |
| Tareas, 12: **eligió mal sin preguntar** | **1 en 4 de las 5 repeticiones** |
| Tareas, 200: correctos | 24 a 26 de 45 |
| Tareas, 200: eligió mal sin preguntar | 0 |
| Intención: ambiguos detectados | 9 de 10 en todas |
| Intención: claros con duda falsa | 8 o 9 de 23 |

El error es siempre el mismo mensaje del lote 1: "ya esta listo lo del horno de la
línea 2? falta mucho?". No existe una tarea del horno; Jev eligió "Relevar planos
del tablero de la estufa" con confianza. El cero de corridas anteriores fue suerte.
Además del riesgo en un cambio, que la vista previa frena, el riesgo mayor está en
una consulta: sin vista previa, Prisma respondería sobre la estufa como si fuera el
horno.

**Arreglo probado:** cuando la receta decide clara, una segunda llamada con un Noul
sobre la tarea elegida ("¿la referencia habla exactamente de esta tarea, y no de otra
cosa parecida o del mismo tipo?"). Con menos de 0,5 se pregunta en lugar de elegir.
Mismas 5 repeticiones:

| | Sin verificación | Con verificación |
|---|---|---|
| Eligió mal sin preguntar, 12 tareas | 1 en 4 de 5 | **0 en las 5** |
| Eligió mal sin preguntar, 200 tareas | 0 | 0 |
| Correctos, 12 / 200 | 34–37 / 24–28 | iguales |
| Probabilidad de "misma" en elecciones correctas | — | mínimo 0,51; mediana 0,87 (255 casos) |
| Probabilidad de "misma" en la elección equivocada | — | 0,26 a 0,32 |

Lectura:

1. **La verificación frena el caso y no frena ninguna elección correcta.**
2. **El margen es fino:** la correcta más baja dio 0,51, al lado del corte.
3. **Se midió sobre mensajes ya vistos y con un solo caso fallido.** Se confirma con
   un lote nuevo, no con esta prueba.
4. **Cuesta una llamada más, de unos 0,4 s,** sólo cuando Prisma está por decidir
   solo: la tarea a verificar no se conoce hasta que Jev la elige.
5. **Toda respuesta a una consulta nombra la tarea por su título,** para que la
   persona note si Prisma entendió otra cosa; es la protección de las lecturas, que
   no pasan por vista previa.

### 5.9 Lote 4, no visto: confirmación de la verificación

15 mensajes nuevos, escritos por el usuario sobre una plantilla: cinco cosas que no
existen pero se parecen a una tarea ("el tablero de la maq 5", "el switc de la ofi de
administrasion", "el bacap de las notebooks"), cinco claras dichas con otras palabras
("el wifi de la planta", "el respaldo de los servers", "la red de la comprimidora"),
dos ambiguas y tres directas. Receta y corte de verificación congelados, cinco
repeticiones (2026-09-24).

| 5 repeticiones | 12 tareas | 200 tareas |
|---|---|---|
| Eligió mal sin preguntar, sin verificación | 2 en cada una | 2 en cada una |
| **Eligió mal sin preguntar, con verificación** | **0** | **0** |
| Correctos | 8 a 10 de 15 | 7 de 15 |
| Elecciones correctas frenadas por la verificación | 0 | 0 |
| Probabilidad de "misma" en elecciones correctas | mínimo 0,61; mediana 0,82 | mínimo 0,61; mediana 0,87 |
| Probabilidad de "misma" en elecciones equivocadas | 0,18 a 0,24 | 0,17 a 0,23 |

Las dos elecciones equivocadas sin verificación son "el switc de la ofi de
administrasion" (asignado al switch de la sala de servidores) y "el bacap de las
notebooks" (asignado al backup de servidores): el mismo patrón que "el horno".

| Intención, 5 repeticiones | Resultado |
|---|---|
| Ambiguo marcado por el usuario ("se hizo el bacap de las notebooks", sin signo de pregunta) | detectado en 3 de 5 |
| Claros con duda falsa | 5 o 6 de 14 |

Lectura:

1. **La verificación queda confirmada con mensajes no vistos:** frena los dos casos
   en todas las repeticiones y no frena ninguna elección correcta. El margen es más
   amplio que en 5.8: 0,24 la equivocada más alta, 0,61 la correcta más baja.
2. **"No existe" termina en pregunta, no en "no hay":** las cinco cosas inexistentes
   terminan ofreciendo la tarea parecida con "Ninguna, lo escribo". Seguro, pero
   molesto; decir "no encuentro esa tarea" sigue pendiente.
3. **Con 200 tareas pregunta más:** "lo del tablero" pregunta entre tableros sin
   incluir los dos correctos, porque el universo grande tiene muchos tableros.
4. **La intención dudosa no es confiable:** el caso marcado se detectó en 3 de 5 y
   las falsas alarmas rondan 1 de cada 3. No aplica nada: un cambio mal leído termina
   en la vista previa, y una consulta mal leída se ve en el título que nombra la
   respuesta. La hipótesis de agrupar por herramienta (5.6) sigue sin probar.

### 5.10 ¿Saber quién escribe ayuda a Jev?

**Pregunta (planteada por el usuario):** Prisma sabe quién escribe por su cuenta de
Telegram, pero Jev no lo recibía. Se asignó un autor verosímil a los 60 mensajes de
los lotes 1 a 4 (quien cuenta avances de su trabajo, un referente que pregunta por
tareas de otros, y casos adversariales: alguien que nombra algo inexistente parecido
a una tarea propia). Receta con verificación, 12 tareas, 5 repeticiones
(2026-09-24).

| 5 repeticiones | Correctos | Eligió mal sin preguntar |
|---|---|---|
| Sin autor | 41 a 44 de 60 | 0 |
| Autor + pista en la instrucción ("cuando cuenta que terminó suele hablar de sus tareas") | 41 a 43 | **1 o 2 en cada repetición** |
| Sólo el autor como dato, sin pista | 43 a 45 | 0 |

El error con pista: "como va lo del tablero", escrito por un referente, terminó
asignado al dashboard de lotes (tablero es también sinónimo de dashboard).

Lectura:

1. **La pista empeora:** empuja a Jev a decidir y rompe el cero de inseguros.
2. **El autor como dato es seguro y aporta poco:** uno o dos correctos más, dentro
   de lo que varía entre corridas.
3. **Donde más aporta quién escribe es en la pantalla:** ordenar primero las tareas
   propias entre los botones y mostrar el responsable sólo cuando la tarea es de otra
   persona.

### 5.11 La segunda candidata: duda que la verificación no ve

**Pregunta:** en el banco real, "ya arregle lo del dashboard, pasalo a revision",
con "Actualizar el dashboard de HMI" y "Revisar gráficos del dashboard HMI", Jev
eligió la primera con 0,91 y la verificación la confirmó con 0,89. El usuario
decidió que ese mensaje tiene que preguntar: "ante la duda se pregunta"
(2026-09-24). La verificación pregunta si la tarea elegida es la misma cosa; no
pregunta si también podría ser otra.

**Prueba:** cuando la receta decide clara, un Noul más sobre la segunda tarea más
probable: "¿el mensaje también podría estar hablando de esta otra tarea?"; con 0,5
o más, se pregunta entre las dos. 60 mensajes de los lotes 1 a 4 más cuatro casos
del banco, 3 repeticiones.

| 3 repeticiones | Sin segunda candidata | Con segunda candidata (corte 0,5) |
|---|---|---|
| Correctos, lotes 1 a 4 | 42 de 60 | 38 o 39 |
| Eligió mal sin preguntar | 0 | 0 |
| "lo del dashboard" (b-0013) | elige | **pregunta en las 3** (0,70) |
| "los accesos vpn" (b-0015, claro) | elige | pregunta (0,52 a 0,53) |

Lectura:

1. **Detecta el caso que la verificación no veía,** de forma estable.
2. **Cuesta entre 5 y 6 preguntas de más cada 60 mensajes,** con dos botones. La
   separación es débil: las elecciones correctas llegan hasta 0,63.
3. **El corte queda en 0,5, el neutro, sin ajustarlo a estos datos:** subirlo para
   dejar pasar "los accesos vpn" sería ajustar al caso visto. El usuario prefiere
   preguntar de más.
4. **Va en la misma llamada que la verificación:** la segunda candidata ya se
   conoce, así que no suma demora.

### 5.12 La segunda candidata, corregida: mirar la referencia

**Hallazgo del banco real:** con la pregunta de 5.11, los pedidos de dependencia
("el cableado del tablero no puede arrancar hasta que yo termine de programar el
PLC") empezaron a preguntar en las 9 corridas. El mensaje nombra las dos tareas, y
para cada referencia la segunda candidata es justamente la otra: la pregunta miraba
el mensaje ("¿el mensaje también podría estar hablando de esta otra tarea?"), y el
mensaje sí habla de las dos. En 5.11 ya se veía en los mensajes con varias
referencias de los lotes, sin que se leyera así.

**Prueba (2026-09-24):** tres redacciones, 60 mensajes de los lotes 1 a 4 más siete
casos del banco, 3 repeticiones.

| Redacción | Correctos, lotes | Eligió mal sin preguntar | "lo del dashboard" | Dependencias (4 casos) |
|---|---|---|---|---|
| v1: mira el mensaje (5.11) | 37 a 39 | 0 | pregunta (0,71 a 0,73) | 3 de 4 mal |
| **v2: mira la referencia** | 39 a 40 | 0 | pregunta (0,69 a 0,72) | 4 de 4 bien |
| v3: la referencia, y "que el mensaje nombre la otra tarea en otra parte no cuenta" | 42 | 0 | pregunta (0,58 a 0,61) | 4 de 4 bien |

Se adopta **v2**: corrige las dependencias y detecta la duda del dashboard con
margen. v3 pregunta menos, pero queda al borde del corte en el único caso de duda
real medido; con "ante la duda se pregunta", el margen pesa más que dos o tres
preguntas de más cada 60 mensajes.

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
| 2026-09-24 | Quinta corrida con un lote no visto: 7 de 15, 3 inseguros; las reglas por palabras sobreajustaron; hacen falta vocabulario del equipo aprendido y referencias por área o persona |
| 2026-09-24 | Prueba 5.3 con Jev: 9 de 9 claras en el lote no visto y duda correcta en "los planos"; falla vocabulario del equipo y áreas; para intención, 4 de 8 al corte 0,8 frente a 0 de 8 de DeepSeek |
| 2026-09-24 | Pruebas 5.4 a 5.7: combinaciones de modalidades de Jev, validación con el lote 3 (11 de 15, 0 inseguros) y escala a 200 tareas |
| 2026-09-24 | Prueba 5.8: cinco repeticiones muestran un caso inseguro repetido ("el horno" asignado a "la estufa"); se agrega una pregunta de verificación que lo frena sin frenar elecciones correctas; falta confirmarla con un lote nuevo |
| 2026-09-24 | Prueba 5.9, lote 4 no visto: la verificación frena los dos casos inseguros en todas las repeticiones, sin frenar elecciones correctas; la duda de intención se detecta en 3 de 5 |
