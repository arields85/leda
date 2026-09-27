# ADR 0009: Entrega con evidencia y revisión

- **Estado:** aceptada (usuario, 2026-09-27)
- **Fecha:** 2026-09-27
- **Alcance:** `actualizar_estado`, `aprobar_tarea`, `pedir_cambios_tarea`
  (nueva) en `src/prisma/herramientas.py`; el menú de tarea en
  `src/prisma/menu_tarea.py`; el camino del menú en `src/prisma/gateway.py`;
  `evidencia_pendiente` en `db/esquema.sql`.
- **Evidencia:** sesión 2 por Telegram real, 2026-09-27, hallazgos 8 y 9
  (`odd/tasks/prisma-orienta.md`).

## Contexto

Ariel, el responsable, tocó "Ya la terminé" sobre una tarea cuya política
exige evidencia (`evidencia_requerida = ['explicacion']`). Prisma la pasó a
`en_revision` sin pedir ni registrar ninguna evidencia. Ismael, el aprobador,
tocó "Aprobar" → vista previa → Confirmar; Prisma contestó "Se aprueba «…»;
para cerrarla todavía falta: Falta la evidencia requerida." -- con la palabra
"falta" repetida -- y confirmó igual: aprobó a ciegas un trabajo sin ninguna
evidencia que revisar.

Una revisión de código aparte encontró el defecto de fondo detrás de eso:
`_aprobar_tarea`/`_preparar_aprobar_tarea` no verificaban que la tarea
estuviera `en_revision`. Por texto libre, el modelo podía aprobar (y de paso
cerrar, por ADR 0008) una tarea todavía `asignada`, o volver a aprobar una
que ya estaba `terminada` -- el menú nunca ofrecía ese botón fuera de
`en_revision`, pero "ofrecer no autoriza" corre en los dos sentidos: que el
menú no lo ofrezca no puede ser lo único que impida una acción que la
herramienta sí permite por texto libre.

## Decisión

1. **La entrega pide la evidencia que falta, en el mismo paso.** Si la
   tarea exige evidencia (`task.evidencia_requerida`) y todavía no tiene
   ninguna, "Ya la terminé" (menú) la pide con el mismo mecanismo que
   "Informar un bloqueo" (`_pedir_dato_menu_tarea`, texto libre) -- "Contame
   brevemente qué hiciste o pasame un link." -- y arma UNA sola vista previa
   que registra la evidencia y mueve el estado a `en_revision` juntos, en el
   mismo Confirmar. Sin evidencia, la tarea no llega a `en_revision` por el
   menú. Por texto libre, `actualizar_estado(estado="en_revision")` sin
   evidencia y sin evidencia ya registrada devuelve un `falta` verdadero
   (nunca mueve la tarea); con `evidencia_texto` en el mismo pedido, hace las
   dos cosas en el mismo acto -- mismo patrón que ADR 0008 (aprobar + cerrar,
   dos filas, un acto). Fotos y archivos quedan fuera de esta unidad (la
   unidad de aportes sobre tareas del roadmap).
2. **"Aprobar" sólo se permite sobre una tarea `en_revision` y con la
   evidencia que exige su política ya registrada.** El menú (`calcular_menu`)
   sólo ofrece el botón cuando las dos condiciones se cumplen; la
   herramienta (`preparar` y el handler, los dos, mismo patrón que el resto
   de las verificaciones de autoridad de este archivo) las vuelve a exigir
   para quien llegue por texto libre. Si no, rechaza con un mensaje humano:
   "Sólo se aprueba una tarea en revisión; hoy está asignada." o "Todavía no
   tiene la evidencia que exige; pedísela a <responsable>." Esto también
   cierra el defecto de la revisión: ya no se puede aprobar (ni cerrar) una
   tarea `asignada` o volver a aprobar una `terminada` por texto libre.
3. **Quien aprueba se entera de la entrega, con botones.** Al llegar a
   `en_revision`, se avisa al aprobador (`membership.aprobador_membership_id`,
   la misma cadena de un solo nivel que `autoridad.puede_aprobar_tarea`) por
   outbox: "«responsable» entregó «título»" + el texto de la evidencia, con
   los botones "Aprobar" y "Pedir cambios" -- una `pending_action` con el
   mismo sentinel que el menú de tarea (`SENTINEL_MENU_TAREA`), así que
   tocar "Aprobar" corre exactamente el mismo camino que tocarlo desde el
   menú (vista previa, Confirmar, cierre de ADR 0008). Se omite en silencio
   si el aprobador no tiene chat vinculado, igual que cualquier otro aviso
   automático; el dedupe usa el id de la evidencia recién registrada cuando
   la hay, nunca la hora. **Pendiente:** un enlace al detalle de la tarea en
   el aviso -- hoy no existe una vista de una tarea puntual (sólo el tablero
   de sólo lectura `/tablero/{token}`, sin URL por tarea); queda un punto de
   enganche nombrado (`_enlace_portal_tarea`, hoy devuelve `None`) para
   cuando exista, sin inventar ninguna URL mientras tanto.
4. **"Pedir cambios" es la acción nueva del aprobador en `en_revision`.**
   Mismo patrón que "Informar un bloqueo": pide el comentario en texto
   libre, arma una vista previa, y al confirmar registra la decisión
   (`approval.decision = 'rechazado'` -- el único otro valor de
   `decision_aprobacion`, `db/esquema.sql`; no se agrega un tercero) y
   devuelve la tarea a `en_curso` con el comentario como `motivo`
   (`nucleo/mecanica-pm.md` §3 no define una transición de vuelta más
   específica que ésa, y no hay ningún disparador que la prohíba). Avisa al
   responsable con el comentario.
5. **La palabra "falta" no queda repetida.** El conector que introduce lo
   que devuelve `motivo_no_cierra_tarea` (que ya empieza diciendo qué falta)
   pasa de "para cerrarla todavía falta: Falta la evidencia requerida." a
   "para cerrarla todavía: Falta la evidencia requerida." -- en la vista
   previa de `aprobar_tarea`, en el aviso al responsable y en el mensaje
   posterior a confirmar por botón.

## Por qué una sola función SQL, no una regla duplicada

`evidencia_pendiente(p_task uuid)` (migración `0012`) extrae la pregunta "¿a
esta tarea le falta la evidencia que exige su política?" de
`motivo_no_cierra_tarea` (mecánica §5) a su propia función, y
`motivo_no_cierra_tarea` pasa a llamarla. La entrega a `en_revision` y el
gate de "Aprobar" necesitan la misma pregunta, pero no las demás condiciones
de cierre (un bloqueo abierto o una dependencia bloqueante no impiden
entregar ni aprobar, sólo cerrar) -- reimplementarla en Python, o duplicarla
en una segunda función SQL, habría dejado dos lugares que decidir "qué es
evidencia pendiente" y que alguien tendría que acordarse de mantener
sincronizados. Mismo criterio que ya usan `motivo_no_arranca_tarea` y
`estado_previo_a_bloqueo` para sus propias preguntas.

## Alternativas consideradas

- **Pedir la evidencia con un mensaje aparte, antes del menú, en vez de en
  el mismo paso que "Ya la terminé".** Un paso más sin necesidad: el menú ya
  sabe que falta (`evidencia_pendiente`) en el momento de tocar la acción;
  pedirla ahí mismo evita una vuelta extra. Rechazada por el mismo principio
  que ADR 0008 ("Prisma ayuda y orienta, nunca agrega burocracia").
- **Aprobar con evidencia faltante, pero marcando la aprobación como
  "condicional".** Habría exigido un tercer valor de `decision_aprobacion`
  o un campo nuevo, para un caso que la constitución ya resuelve más
  simple: "Prisma no acepta como evidencia una afirmación cuando la política
  pide un artefacto" (mecánica §6) -- no hay aprobación posible sin la
  evidencia que la política exige. Rechazada.
- **"Pedir cambios" como un tercer valor de `decision_aprobacion` en vez de
  reusar `rechazado`.** Habría requerido una migración de tipo enum
  (`alter type ... add value`, que en PostgreSQL no puede revertirse dentro
  de una transacción) para una distinción que el campo `comentario` ya
  cubre -- "rechazado" con un comentario que pide cambios es, en los
  hechos, exactamente eso. Rechazada mientras no aparezca una razón real
  para distinguirlos en una consulta.

## Consecuencias

- `actualizar_estado` gana un parámetro opcional `evidencia_texto`; sin él,
  y con evidencia pendiente, el estado nunca pasa a `en_revision`.
- `aprobar_tarea` puede rechazar con `Denegado` en casos que antes
  aceptaba (una tarea que no está `en_revision`, o que no tiene su
  evidencia) -- corrige el defecto de revisión (aprobar/cerrar tareas
  `asignada`/`terminada` por texto libre), pero es un cambio de
  comportamiento observable para cualquier integración que dependiera de
  la conducta vieja.
- Herramienta nueva `pedir_cambios_tarea`, con su propio `preparar` y
  autoridad (misma cadena que `aprobar_tarea`: `puede_aprobar_tarea`).
- El menú de una tarea en `en_revision`, para el aprobador, pasa a tener
  hasta tres acciones: "Ver detalle y evidencia", "Aprobar" (sólo si ya
  tiene la evidencia) y "Pedir cambios" (siempre).
- **Pendiente:** un enlace al detalle de la tarea en el aviso de entrega
  (punto 3, arriba) -- sin vista de tarea individual todavía. Fotos y
  archivos como evidencia (constitución/mecánica §6: "los archivos se
  guardan por referencia con verificación de integridad") quedan para la
  unidad de aportes sobre tareas del roadmap, no en ésta.
- **Pendiente, ajeno a esta decisión:** `tests/banco/corrida.py` no tiene un
  tipo de paso para responder con texto libre entre dos toques -- un
  escenario que combine "tocar una tarea → Ya la terminé → escribir la
  evidencia → Confirmar automático" no se puede representar todavía
  (`tests/banco/escenarios/b-0017.yaml` y el escenario nuevo de toques
  genéricos se adaptaron eximiendo la evidencia a propósito, no extendiendo
  el corredor). Extenderlo queda fuera del alcance de esta unidad.
