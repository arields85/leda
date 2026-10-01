# Guion de la prueba real, corte 1 (alta guiada)

Base `prisma_flujo` (esquema completo, paquete, feriados, semilla ficticia, modelo
`nan`/`deepseek-v4-flash`, variante `redaccion` = B). Cuentas vinculadas: Ariel, Ismael,
Marcos. Listener del worktree (`PYTHONPATH=src`).

Por cada paso, anotar: **mejoró / empeoró / igual** respecto de la ronda 4, y si la
respuesta tardó (sí / no). Los mensajes son ejemplos: escribirlos como los escribiría
la persona, desprolijos.

| # | Quién | Mensaje | Qué se espera | Hallazgo | Resultado |
|---|---|---|---|---|---|
| 1 | Marcos | "quiero crear una tarea nueva" | Pregunta primero qué hay que hacer, sin "(hasta N)" | R4c-H4, H7 | |
| 2 | Marcos | "revisar el variador de la comprimidora" | Lo toma como título y pasa al objetivo con botones | R4c-H4 | |
| 3 | Marcos | El objetivo escrito con sus palabras, sin tocar el botón | Lo entiende; no dice "No encontré esa opción" | R4c-H4 | |
| 4 | — | (Marcos sólo puede asignar en OT) | No pregunta el área; aparece en el resumen | R4c-H10 | |
| 5 | Marcos | Fecha: "4de octubre" | La acepta y la muestra | R4c-H6 | |
| 6 | Marcos | En otra alta: "04 / 10", "el viernes", "la semana que viene" | Las acepta y muestra la fecha interpretada | R4c-H6 | |
| 7 | Marcos | Una fecha pasada: "ayer" | Dice por qué no sirve y qué sirve, sin jerga | R4c-H6 | |
| 8 | Marcos | A mitad del alta: "ah, y necesito otra tarea para Nahuel" | No reinicia ni entra en bucle: una sola pregunta por la rama | R4c-H5 | |
| 9 | Marcos | Llegar al resumen | Sin claves internas, sin "Sin descripción", el cierre coincide con "Enviar a aprobación" | R4c-H8, H9 | |
| 10 | Marcos | "necesito crear una tarea: calibrar los sensores de la línea 2" | Toma el título y salta al objetivo | R4c-H4 | |
| 11 | Ariel | Alta para sí mismo, hasta Confirmar | El cierre dice "Con Confirmar se crea la tarea…"; la tarea queda creada | R4c-H9 | |

**Huecos conocidos (no son hallazgos nuevos):**

- (Resuelto en la rama, ver "Corrida siguiente") El objetivo más probable primero (⭐)
  no estaba construido: los objetivos salían en el orden de siempre.
- Una fecha relativa en el primer mensaje ("…para el viernes") no se toma todavía: se
  pregunta después.
- Los tipos de evidencia salen sin tilde ("explicacion").
- Fuera del horario laboral, lo que inicia Prisma (el borrador que le llega a Ismael)
  queda en la cola hasta las 09:00 (R4b-H6). Las respuestas a lo que uno escribe salen
  en el momento.

**Además registrar:** incidentes nuevos (`python -m prisma incidentes corework`), y
cualquier respuesta que se sienta robótica aunque no esté en la lista: se anota y se
clasifica por etapa del ADR 0014, sin corregir durante la prueba (moratoria).

## Corrida B, 2026-09-30 21:53-22:06 (Marcos)

| # | Resultado | Nota |
|---|---|---|
| 1 | Mejoró | "¿Qué hay que hacer?" primero, sin jerga. |
| 2 | Mejoró | Tomó la frase como título. |
| 3 | Mejoró | "lo de conectar los equipos" → objetivo correcto, sin "No encontré esa opción". Los nombres de objetivo salen cortados con "…" en los botones. |
| 4 | Mejoró | No preguntó el área; aparece en el resumen. |
| 5 | Mejoró | "4 oct" → 04/10/2026. |
| 6 | Mixto | "el miercoles que viene" → aceptada. "la semana que viene" → **incidente** (ver F-B1). |
| 9 | Mejoró casi todo | Sin "Sin descripción"; el cierre coincide con "Enviar a aprobación"; el criterio se normalizó ("porque voy a…" → "voy a…"). Evidencia sin tilde (hueco conocido). |

Hallazgos (clasificados por etapa del ADR 0014; disparadores de "Cómo pensamos juntos"):

- **F-B1 (etapa 2/4, mecanismo).** Una respuesta con un valor incompleto o ambiguo ("la
  semana que viene": ¿qué día?) se trata como falla técnica: incidente
  `valor_sin_interpretar` y "Tuve un problema y no pude responder tu mensaje", más la
  misma pregunta. El contrato del valor es binario (hay valor / no hay valor) y no tiene
  forma de decir "falta precisar esto". Misma clase que R4b-H5 de la ronda 4 (una
  respuesta a una pregunta pendiente tratada como imposible): **disparador "misma clase
  en dos rondas"**. Era la advertencia R4 de la revisión.
- **F-B2 (etapa 2, mecanismo).** Ante "porque enviare vide y foto" para el criterio de
  aceptación, el modelo dudó (`dudoso`, "¿Esto es el criterio…?"); al tocar "Sí, es eso"
  (`respuesta_dato_menu` 22:05:22 y 22:06:27) el sistema vuelve a rutear el texto, el
  modelo vuelve a no dar valor y sale el incidente. Confirmar con el botón no toma el
  texto que la persona confirmó. Era la advertencia R5.
- **F-B3 (contradice ADR 0013, enmienda de la rama abierta).** Con el primer borrador ya
  enviado a Ismael, "quiero crear otra tarea" respondió "Ya hay un borrador de tarea en
  curso" con Continuar / Cancelar / Empezar otro, y el borrador **enviado a aprobación
  quedó cancelado** (22:02:16, `cancelar_ingreso_tarea`; `task_intake_request` y
  `task_draft` en `cancelled`). El ADR 0013 dice que un borrador que espera la
  confirmación de otra persona no es una rama abierta de quien lo pidió. Probablemente
  anterior a esta rama (estado `active` después de "Enviar a aprobación", migración
  `0023`): `PENDIENTE` verificar en `main`. **Disparador "contradice un ADR".**
- **F-B4 (incidentes).** El aviso al administrador de `valor_sin_interpretar` muestra el
  marcador `{nombre}` sin reemplazar y "sin referencia al mensaje".
- **F-B5 (observación).** "voy a enviar videos" volvió a mostrar la misma pregunta sin
  decir nada (22:05:44): sin incidente ni explicación.

Nota de experiencia del usuario: "se sintió más fluido y humano este flujo"; los textos se
sintieron muy estructurados. Explicación: en la variante B todos los textos visibles del alta
son plantillas del código; el modelo sólo interpretó (etapa 2). La comprensión mejoró la
experiencia aun con redacción plantillada; la variante A prueba la redacción.

## Corrida B con F-B1 a F-B4, 2026-09-30 23:12-23:25 (Marcos)

Leída de la base (`inbound_message`, `message_outbox`, `audit_log`); sin incidentes nuevos.

| # | Resultado | Nota |
|---|---|---|
| 6 | Mejoró | "la semana que viene" → repregunta el día exacto, sin incidente (F-B1). "el miercoles que viene" → 07/10/2026; "el viernes" → 02/10/2026; "07-10" aceptada. |
| 7 | Mejoró | "ayer" → "Esa fecha ya pasó. Decime una fecha desde hoy en adelante." |
| 7b | Mejoró | "no lo se, voy a ver" → "¿Esto es el criterio…?" → "Sí, es eso" lo tomó, sin incidente (F-B2). |
| 8 | Mejoró | "ah, y necesito otra tarea para Nahuel" en la revisión → una sola pregunta por la rama, sin bucle. |
| 8b | Mejoró | Con "poner un cable" enviado a Ismael, "ahora quiero hacer otra tarea" arrancó la nueva sin tocar la enviada (F-B3). El borrador cancelado a las 22:02 quedó `descartado` en la cola de Ismael. |

Observaciones (no son fallas del mecanismo):

- **F-B6.** Con la pregunta "¿Qué hay que hacer?" abierta, "quiero crear otra tarea" contestó
  "Estábamos con el título de la tarea nueva. ¿Seguimos con eso?": la persona repite la
  misma intención y la rama le pide confirmar. Fricción menor (regla de una rama).
- **F-B7 (producto).** "no lo se, voy a ver" quedó como criterio de aceptación porque la
  persona lo confirmó. El invariante exige un criterio, y Prisma lo aceptó vacío de
  contenido. **Respuesta del usuario (2026-09-30): sí; Prisma ayuda y facilita, no sólo
  dirige, y sin burocracia.** Ya está mandado en `nucleo/mecanica-pm.md` §13.2 ("¿El
  resultado esperado es concreto y verificable?… Si alguna respuesta falta, Prisma
  pregunta antes de crear"): es una brecha entre núcleo y código, no una decisión nueva.
  Mecanismo (etapa 2): el modelo evalúa si el criterio es verificable y, si no lo es,
  propone uno a partir del título y de lo que la persona dijo, con botones para usarlo o
  escribir otro; el código no crea la tarea con un criterio que la persona no eligió.

## Corrida B, pasos 9 a 11, 2026-09-30 23:46-23:52 (Marcos y Ariel)

| # | Resultado | Nota |
|---|---|---|
| 9 | Mejoró | Resumen sin "Sin descripción"; el cierre coincide con el botón. |
| 10 | No probado | El mensaje llegó como respuesta a un "¿Qué hay que hacer?" que Prisma ya había preguntado (al atender el mensaje dejado de lado), así que no probó el salto de esa pregunta. El título sí quedó bien extraído ("calibrar los sensores de la linea 2", sin "necesito crear una tarea:"). El responsable salió contaminado por el mensaje dejado de lado (F-B8). Observación del usuario: el objetivo se pregunta siempre igual, sin importar el título (hueco ⭐, ver F-B10). Repetir en la corrida A como primer mensaje. |
| 11 | Mejoró | Ariel: área y responsable completados solos (una sola opción), "manana" → 01/10/2026, resumen y "Enviar a aprobación" a Ismael. El guion esperaba "Confirmar": era un error del guion; quien crea una tarea para sí necesita la aprobación de su aprobador (Marcos creando para Nahuel sí confirmó directo). |

Observaciones:

- **F-B8 (etapa 1/2, mecanismo).** Un dato de un mensaje que la persona dejó de lado
  ("ah, y necesito otra tarea para Nahuel", 23:25) contaminó la tarea siguiente, que era
  otra ("calibrar los sensores…", 23:47): el responsable se preguntó como "Opciones que
  coinciden con «Nahuel»" y Marcos eligió "Para mí". Al "dejar y ver lo otro", el mensaje
  guardado se atiende, pero sus propuestas no pueden sobrevivir a una tarea distinta.
  Además, el texto "Opciones que coinciden con «…»" es de sistema, no de persona.
- **Lección de método.** La lectura desde la base mostraba los toques como códigos
  (`p:…`, `i:…`) y sin los botones ofrecidos; una conclusión (paso 10) salió al revés. El
  lector ahora resuelve cada toque a su etiqueta y muestra los botones de cada mensaje.
- **F-B9.** El valor se normaliza distinto según el campo: el criterio corrigió un error de
  tipeo ("andadndo" → "andando") y el título quedó tal cual ("la ainterfaz"). Pregunta de
  producto: ¿Prisma corrige errores de tipeo obvios en los textos (visible en el resumen,
  cambiable con Modificar) o respeta lo escrito?
- No se probó el caso exacto "4de octubre" (R4c-H6): queda para la corrida A.

**Latencia por respuesta** (mensaje entrante → primera respuesta enviada, de la base):
textos n=34, mediana 8,7 s, p90 13,7 s, ninguno ≤ 5 s; toques n=23, mediana 0,9 s. En la
ronda 4 (base `prisma`, 2026-09-30) la mediana de textos fue la misma, 8,7 s (p90 18,6 s,
ninguno ≤ 5 s). B no agregó latencia, pero el criterio "mediana ≤ 5 s" del ADR 0014 no se
cumplía tampoco antes: se fijó sin línea base.

- **F-B10 (usuario, 2026-10-01; etapa 3).** El título no influye en el objetivo: siempre
  aparece la misma lista, en el mismo orden, diga lo que diga la tarea. Es el hueco del
  objetivo más probable primero (⭐, decisión del usuario para R4c-H4), y con el principio
  constitucional "ayuda y facilita" pasa a ser el hueco más visible del alta: con un título
  claro, Prisma tendría que proponer el objetivo (Jev elige entre los candidatos de la base).
- **F-B11 (usuario, 2026-10-01; etapas 1 y 3).** A Ariel (área Software e interfaz HMI)
  el alta le ofreció los seis objetivos del espacio, de todas las áreas. Por las tareas
  sembradas: "Conectar y automatizar equipos…" y "Planos eléctricos…" son de OT,
  "Construir o adaptar tableros…" de Sistemas eléctricos, "Fortalecer servidores…" de
  Infraestructura IT; sólo "Robustecer la plataforma…" es de Software, y "Vincular los
  equipos…" es el estratégico, de todos. Causa en los datos: `objective` no tiene área y
  la semilla deja `referente_membership_id` vacío, así que hoy el sistema no puede saber
  qué objetivo es de qué área (la relación sólo se infiere de las tareas). Va con F-B10.
  **Decisión del usuario (2026-10-01):** una persona no pide tareas de otro sector. Lo que
  cruza áreas pasa por una dependencia de una tarea propia ("Depende de otra tarea" del
  menú, `menu_tarea.py:135`; `nucleo/mecanica-pm.md` §4: una dependencia entre áreas se
  notifica a los dos referentes). Por lo tanto el alta ofrece sólo los objetivos del área
  de quien pide, no los de otras. Propuesta a confirmar en la implementación: si el área
  tiene un solo objetivo operativo, se completa solo (misma regla que R4c-H10); el
  estratégico sólo si el área no tiene objetivos propios. Requiere que el objetivo tenga
  área en los datos (hoy no la tiene).

## Corrida A, 2026-10-01 00:22-00:37 (Marcos y Ariel)

**Impresión del usuario:** se sintió mejor y menos robótico (saludó a Ariel por su nombre),
pero "todavía capado": la respuesta se siente mitad planilla y mitad modelo.

**Lo que muestra la base (por qué se siente mitad y mitad):** la variante A, tal como está
construida, deja que el modelo escriba sólo una frase delante de la pregunta de plantilla:
"Me falta el título. ¿Qué hay que hacer?", "Todavía no puedo avanzar porque me falta un
dato. ¿A qué objetivo pertenece la tarea?". La pregunta, el resumen y el cierre siguen
siendo del código, y la frase del modelo repite "me falta…" en casi todos los turnos.
La etapa 6 del ADR 0014 (redactar a partir del resultado del turno) quedó a medias.

**Números:**

- Redacciones de A: 18; aceptadas 15; rechazadas 3, las tres falsas: el verificador tomó
  el imperativo "Escribí" como una acción en primera persona (`accion_no_ocurrida`), la
  debilidad anticipada (R13). Duración de la llamada de redacción: mediana 4,5 s, p90 6,7 s.
- Latencia por respuesta: textos n=15, mediana 10,3 s (B: 8,7 s), p90 16,4 s; **toques
  n=11, mediana 7,8 s (B: 0,9 s)**: con A cada toque espera una llamada al modelo.

**Observaciones:**

- **F-A1.** El orden de dos mensajes del mismo turno salió invertido: "Me falta el
  título… ¿Qué hay que hacer?" llegó antes que "Listo, dejé de lado el borrador…".
- **F-A2.** La respuesta breve a la charla funciona (F-B5) pero suena rara: "Hola, qué
  bueno tenerte por acá, seguimos en un momento." y después la pregunta.
- El paso 1 (la tarea en el primer mensaje) otra vez no se probó como primer mensaje:
  había una rama abierta. "4de octubre" tampoco se probó.
- "voy a enviar videos" volvió a quedar como criterio tras "Sí, es eso" (F-B7).

**Propuesta del usuario (2026-10-01):** el modelo como intermediario al principio y al
final: humano → modelo → lógica lo más determinista posible (Jev, SQL, reglas) → resultado
→ modelo → humano. Es el diseño del ADR 0014 (etapas 2 y 6); lo que falta es que la etapa
6 sea completa: que el modelo redacte el mensaje entero a partir del resultado del turno,
no una frase delante de una plantilla.

## Corrida siguiente: "Prisma propone" (F-B7, F-B8, F-B10, F-B11) y lo que falta probar

Antes: aplicar la migración `0027` a `prisma_flujo` y dar su área a los objetivos
existentes (el orquestador lo hace; ver el reporte del commit). Con `variante`
A o B, a elección. Anotar por paso: mejoró / empeoró / igual, y si tardó.

| # | Quién | Mensaje | Qué se espera | Hallazgo |
|---|---|---|---|---|
| 1 | Marcos | PRIMER mensaje de la sesión, sin rama abierta: "necesito crear una tarea: calibrar los sensores de la línea 2" | Toma el título y salta al objetivo, sin preguntar "¿Qué hay que hacer?" | R4c-H4 (no probado) |
| 2 | Marcos (OT: dos objetivos propios) | Seguir hasta el objetivo | Sólo los dos objetivos de OT; ninguno de otra área ni el estratégico. Con un título claro, el más probable va primero con ⭐ y se pregunta igual; con uno ambiguo, sin ⭐, en el orden de siempre | F-B10, F-B11 |
| 3 | Marcos | Escribir parte del nombre de un objetivo de otra área ("servidores") | No lo encuentra: ofrece los de OT con "Para «servidores» encontré estas opciones. ¿A qué objetivo…?" (ya no "Opciones que coinciden con…") | F-B11, nota F-B8 |
| 4 | Ariel (Software: un solo objetivo propio) | Alta para sí mismo | El objetivo se completa solo y aparece en el resumen; no se pregunta | F-B11 |
| 5 | Marcos | Fecha: "4de octubre" | La acepta y la muestra (04/10) | R4c-H6 (no probado) |
| 6 | Marcos | Criterio de aceptación: "no lo sé, voy a ver" (y probar "por fotos") | No lo compromete: dice que todavía no dice cómo se comprueba y propone uno armado con el título, con Sí / No / Otra opción | F-B7 |
| 7 | Marcos | En el paso 6 tocar "Sí" | El criterio propuesto queda; el resumen lo muestra | F-B7 |
| 8 | Marcos | En otra alta, tocar "Otra opción" y volver a escribir "no lo sé" | Lo acepta tal cual (una sola propuesta, sin bucle) | F-B7 |
| 9 | Marcos | A mitad de un alta: "ah, y necesito otra tarea para Nahuel" -> "Dejarlo y ver lo otro" -> a "¿Qué hay que hacer?" contestar "necesito crear una tarea: calibrar los sensores" | El responsable NO viene precargado con Nahuel (es otra tarea); se pregunta normal. Variante: contestar sólo "calibrar los sensores" (sin "necesito crear una tarea") -> el responsable sí sigue siendo Nahuel | F-B8 |

**Además registrar:** incidentes nuevos (`python -m prisma incidentes corework`),
en particular `objetivo_sin_ordenar` (Jev sin credencial o caído: los objetivos
salen en el orden de siempre, sin ⭐) y `criterio_sin_propuesta`; y cualquier
respuesta que se sienta robótica aunque no esté en la lista.

**Decisión del usuario sobre F-B9 (2026-10-01):** Prisma corrige los errores de tipeo
obvios en los textos que la persona dicta (título, criterio, motivo): el modelo normaliza
el valor en la etapa 2 y la corrección queda a la vista en el resumen, cambiable con
Modificar. Pendiente de implementar después de esta corrida (hoy el título queda tal cual
y el criterio a veces se corrige).

## Corrida siguiente, 2026-10-01 08:11-08:19 (Marcos, variante A)

Leída de la base con los botones resueltos.

| # | Resultado | Nota |
|---|---|---|
| 1 | Falló (F-C1) | "necesito crear una tarea: calibrar los sensores de la línea 2" como primer mensaje → "¿A cuál te referís con «…»?" con dos tareas existentes + "Es una tarea nueva". Con "Es una tarea nueva" siguió, y el título se tomó (no preguntó "¿Qué hay que hacer?"). |
| 2 | Mejoró | Sólo los dos objetivos de OT, con ⭐ en "Conectar y automatizar equipos…" y el texto "Con ⭐ marqué el que más se parece a la tarea." |
| 3 | Mejoró | "servidores" → "No encontré nada parecido a «servidores». Estas son las opciones que hay." con los dos de OT. |
| 4 | Mejoró | "4de octubre" → 04/10/2026 (R4c-H6 cerrado en vivo). |
| 5 | Falló (F-C3) | "no lo sé, voy a ver" → "¿Esto es el criterio…?" (Sí, es eso / No, es otra cosa) → "Sí, es eso" → quedó como criterio, sin propuesta. |

Hallazgos:

- **F-C1 (etapas 2 y 3, contradice ADR 0014).** Con la intención de crear dicha
  explícitamente, el título de la tarea nueva se trató además como referencia a una tarea
  existente y Jev abrió una aclaración. Dos dueños para lo mismo: con intención de crear,
  el título no se busca entre las existentes.
- **F-C2 (bureaucracia, principio "ayuda y facilita").** Después del objetivo preguntó
  "¿Confirmás esta descripción?" (Sí / No / ✏️ Otra opción) con la descripción igual al
  título, y el resumen muestra título y descripción duplicados. Una pregunta que no aporta.
- **F-C3 (etapa 2, mecanismo).** La propuesta de criterio verificable (F-B7) sólo corre
  cuando el ruteo devuelve `responde`; con `dudoso` → "Sí, es eso", el texto se toma tal
  cual sin juzgar si es verificable. Confirmar que es la respuesta no es confirmar que es
  verificable.
- **F-C4 (redacción A).** Casi todos los mensajes empiezan con "Entendí que…": otra
  muletilla que suena a planilla.
- **F-C5.** El resumen de las 08:18:47 salió sin el cierre que nombra el botón (termina
  en una línea vacía); coincide con un vencimiento del plazo de redacción a las 08:18.
- **Latencia en vivo.** 4 vencimientos del plazo de 4 s esta mañana (08:15, 08:16, 08:18 y
  uno más); la medición en banco (p50 0,9 s) no se reprodujo en vivo. `prisma redaccion`
  acumulado: 25 llamadas, 18 aceptadas, 3 rechazadas (anoche), 4 vencidas; mediana 4,0 s.
- No hubo saludo del día: Marcos ya lo había recibido a las 00:23 (regla vigente, un
  saludo por día local).

## Corrida siguiente, 08:22-08:32 (Marcos): el flujo se traba

- "no lo sé" → "Eso es muy general para usarlo así. Contame un poco más de detalle": no
  propuso un criterio (F-B7 sigue sin aparecer en vivo).
- **"ayudame, que puedo poner?"** (pedido de ayuda SOBRE la pregunta abierta) → el ruteo lo
  tomó como otro tema → "Estábamos con el criterio… ¿Seguimos con eso?"; con "Dejarlo y ver
  lo otro" **se perdió el borrador entero** y recién ahí Prisma ayudó con ejemplos de
  criterio, ya sin tarea.
- **"por que anda"** (respuesta al criterio) → otra vez otro tema → "¿Seguimos?" → Dejarlo
  → **se perdió el borrador** "calibrar los sensores" y salió "No te sigo. ¿Qué querés
  saber que anda?". Dos mensajes del mismo turno otra vez en orden invertido (08:32:34).
- Un toque viejo ("Para mí") → "Ese pedido ya no está vigente…".

**Diagnóstico (F-C6, mecanismo).** La conversación del alta es un formulario de un campo
por turno, gobernado por una clasificación cerrada del mensaje (responde / otro tema /
charla…) que hace un modelo chico sin entender la conversación. Cuando clasifica mal, la
regla de una sola rama convierte una respuesta o un pedido de ayuda en "¿Seguimos?", y
"Dejarlo" borra el trabajo. Las muletillas ("Entendí que…", "Me falta…") vienen de que el
modelo redacta campo por campo. Pedido del usuario: desactivar la protección de latencia,
ver al modelo 100 % sin plantillas, y que la conversación fluya "como cuando hablo con
vos".
