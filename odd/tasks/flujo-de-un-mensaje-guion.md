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

- El objetivo más probable primero (⭐) no está construido: los objetivos salen en el
  orden de siempre.
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
| 10 | Mejoró | "necesito crear una tarea: calibrar los sensores de la linea 2" como respuesta a "¿Qué hay que hacer?" → pasó al objetivo. El "para Nahuel" del mensaje guardado llegó como propuesta de responsable. |
| 11 | Mejoró | Ariel: área y responsable completados solos (una sola opción), "manana" → 01/10/2026, resumen y "Enviar a aprobación" a Ismael. El guion esperaba "Confirmar": era un error del guion; quien crea una tarea para sí necesita la aprobación de su aprobador (Marcos creando para Nahuel sí confirmó directo). |

Observaciones:

- **F-B8.** Con el responsable propuesto desde el mensaje ("para Nahuel"), la pregunta fue
  "Opciones que coinciden con «Nahuel»." con botones: texto de sistema, no de persona. Con
  una sola coincidencia, el principio "ayuda y facilita" pide proponerla directamente.
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
