# ADR 0008: Aprobar cierra la tarea, en el mismo acto, si se puede

- **Estado:** aceptada (usuario, 2026-09-27)
- **Fecha:** 2026-09-27
- **Alcance:** `aprobar_tarea` (`src/prisma/herramientas.py`), el menú de tarea en
  `en_revision` (`src/prisma/menu_tarea.py`) y los mensajes posteriores a confirmar por
  botón (`src/prisma/gateway.py`)
- **Evidencia:** sesión 2 por Telegram real, 2026-09-27, hallazgo 5 (`odd/tasks/prisma-orienta.md`)

## Contexto

Ismael, el aprobador, tocó el menú de una tarea → "Aprobar" → vista previa → Confirmar.
Prisma contestó "Hecho. Tarea: Dashboard de lotes en CoreLabs (simulado) · Estado
actual: En revisión · se aprueba el trabajo". La base quedó así:

- `audit_log` registró `herramienta:aprobar_tarea`;
- `approval` tiene la fila de la aprobación;
- la tarea siguió en `en_revision`: `herramientas._aprobar_tarea` sólo insertaba en
  `approval`, nunca corría `motivo_no_cierra_tarea` ni insertaba en
  `task_state_event`;
- el menú del responsable en `en_revision` sólo ofrece "Adjuntar evidencia" -- no hay
  ningún botón que mueva la tarea a `terminada` después de aprobada;
- nadie avisó al responsable que su tarea había sido aprobada.

El mismo hallazgo detectó un segundo defecto, más chico, en el mismo camino: el
mensaje que sigue a Confirmar reusaba el texto de la vista previa en vez de describir
el resultado -- "Estado actual: En revisión" después de que la aprobación (o cualquier
`actualizar_estado`) ya se aplicó.

## Decisión

1. **`aprobar_tarea` siempre registra la aprobación.** Eso no cambia: sigue siendo un
   insert en `approval`, con su propia autoridad (`puede_aprobar_tarea`) verificada
   antes.
2. **Si con esa aprobación se cumplen las condiciones de cierre de mecánica §5, la
   misma llamada también cierra la tarea.** El cierre es una segunda fila -- un
   insert en `task_state_event` con `estado_nuevo = 'terminada'` -- nunca el mismo
   registro que la aprobación. Constitución §3 dice "actualización, evidencia,
   aprobación y cierre son hechos distintos"; esta decisión los mantiene como hechos
   distintos, no como un mismo acto disfrazado de dos.
3. **La comprobación es la misma función determinista que ya gobierna el cierre**:
   `motivo_no_cierra_tarea(tarea_id)` (`db/esquema.sql`), la que corre
   `actualizar_estado` para transicionar a `terminada`. No hay una segunda regla de
   negocio para "cerrar por aprobación": es la regla de cierre de siempre, ejecutada
   una vez más, después de insertar la aprobación.
4. **Si falta algo más, la tarea queda en `en_revision`, con la aprobación igual
   registrada, y Prisma dice exactamente qué falta.** No es una pregunta abierta: es
   el mismo texto que devuelve `motivo_no_cierra_tarea` (evidencia, un bloqueo, una
   dependencia bloqueante).
5. **El responsable se entera.** Un aviso por outbox, con el mismo mecanismo que el
   resto de los avisos automáticos (se omite en silencio si no tiene chat vinculado;
   nunca falla en silencio por otra causa), deduplicado por el id de la aprobación,
   nunca por la hora.
6. **El menú de `en_revision` ofrece "Cerrar tarea" cuando ya se puede.** Cubre el
   caso en que la aprobación llegó antes que otra condición (evidencia, un bloqueo que
   se resuelve después) y esa condición se completa más tarde: sin este botón, nadie
   podía cerrar la tarea tocando, sólo escribiendo. Se calcula con la misma
   `motivo_no_cierra_tarea`, nunca una copia de la regla.
7. **El mensaje después de confirmar describe el resultado, en pasado, no la vista
   previa.** Al menos para `aprobar_tarea` ("Listo: aprobaste «X». Quedó terminada."
   o "…; para cerrarla falta: …") y `actualizar_estado` ("Listo: «X» pasó a En
   revisión."). El resto de las herramientas del menú conserva el recibo genérico
   existente.

## Por qué "hechos distintos" no es "actos distintos"

La lectura más simple de constitución §3 sería exigir un segundo toque: aprobar deja
la tarea `en_revision`, y el responsable (o el aprobador) tiene que volver a tocar
"Cerrar tarea" para terminarla. Se descartó: mecánica §5 ya define el cierre como una
comprobación determinista sobre condiciones que **ya están cumplidas o no** en el
momento de aprobar -- no depende de ningún juicio adicional que el segundo toque
fuera a aportar. Pedirlo igual es la burocracia que el principio del usuario
("Prisma ayuda y orienta, nunca agrega burocracia") rechaza explícitamente: un paso
mecánico, sin criterio propio, que sólo repite lo que la base ya puede decidir sola.

Lo que la constitución protege -- que aprobar y cerrar queden como hechos auditables
por separado, cada uno con su propio registro y su propio momento -- se preserva
enteramente con dos filas (`approval` y `task_state_event`) dentro del mismo acto.
Nada se pierde: quien audite sigue viendo cuándo se aprobó y cuándo se cerró, y en
este caso son el mismo instante porque no había ninguna otra condición pendiente.

## Alternativas consideradas

- **El responsable cierra con un toque extra** ("Cerrar tarea" siempre aparece tras la
  aprobación, incluso si ya se puede cerrar en el momento de aprobar). Más fiel a una
  lectura literal de "hechos distintos", pero agrega un paso sin criterio -- la
  condición ya se evaluó al aprobar -- y deja una ventana en la que la tarea aparenta
  seguir "en revisión" cuando en los hechos ya no falta nada. Rechazada por el
  principio de no agregar burocracia.
- **Actos separados, con Prisma preguntando "¿la cierro también?"** Vuelve a
  `nucleo/mecanica-pm.md`: "Prisma nunca cambia un estado por inferencia" no aplica
  acá (el cierre sigue siendo la comprobación determinista, no una inferencia), pero
  la pregunta abierta contradice ADR 0007 ("Prisma orienta, no charla"): si la
  condición ya se puede evaluar, no hace falta preguntar para saber la respuesta.
  Rechazada.

## Consecuencias

- `herramientas._aprobar_tarea` devuelve `{"aprobada": True, "cerrada": bool,
  "falta": <motivo o None>, "titulo": <título>}` en vez de `{"aprobada": True}`. Ningún
  test existente comparaba ese dict por igualdad exacta.
- El camino de confirmación por botón (`gateway.py`) distingue explícitamente
  `aprobar_tarea` del resto: `cerrada: False` ahí significa "se escribió la
  aprobación, pero no alcanzó para cerrar", no "no se escribió nada", que es lo que
  significa en cualquier otra herramienta que declara `preparar`.
- El menú de `en_revision` puede mostrar hasta tres acciones para el responsable:
  "Ver detalle", "Adjuntar evidencia" y, sólo si ya se puede, "Cerrar tarea".
- Queda **pendiente** si conviene el mismo tratamiento para el cierre de objetivo
  (`motivo_no_cierra_objetivo`, mecánica §5, "Cierre de objetivo") -- constitución §7
  reserva la aprobación final para "planes, hitos, objetivos integrales, prioridades y
  decisiones relevantes", y esa aprobación pasa por un camino distinto
  (`aprobar_objetivo`, sin implementación equivalente hoy). No se toca en esta
  unidad.
