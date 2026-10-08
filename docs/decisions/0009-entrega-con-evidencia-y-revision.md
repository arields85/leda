# ADR 0009: Entrega con evidencia y revisión

- **Estado:** aceptada (usuario, 2026-09-27)
- **Fecha:** 2026-09-27
- **Alcance:** `actualizar_estado`, `aprobar_tarea`, `pedir_cambios_tarea`
  (nueva) en `src/leda/herramientas.py`; el menú de tarea en
  `src/leda/menu_tarea.py`; el camino del menú en `src/leda/gateway.py`;
  `evidencia_pendiente` en `db/esquema.sql`.
- **Evidencia:** sesión 2 por Telegram real, 2026-09-27, hallazgos 8 y 9
  (`odd/tasks/leda-orienta.md`).

## Contexto

Ariel, el responsable, tocó "Ya la terminé" sobre una tarea cuya política
exige evidencia (`evidencia_requerida = ['explicacion']`). Leda la pasó a
`en_revision` sin pedir ni registrar ninguna evidencia. Ismael, el aprobador,
tocó "Aprobar" → vista previa → Confirmar; Leda contestó "Se aprueba «…»;
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
  que ADR 0008 ("Leda ayuda y orienta, nunca agrega burocracia").
- **Aprobar con evidencia faltante, pero marcando la aprobación como
  "condicional".** Habría exigido un tercer valor de `decision_aprobacion`
  o un campo nuevo, para un caso que la constitución ya resuelve más
  simple: "Leda no acepta como evidencia una afirmación cuando la política
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

## Enmienda (2026-09-27): "Pedir cambios" no deja sobrevivir lo anterior

Seguimiento de review-c112506a (`odd/tasks/leda-orienta.md` T6). "Pedir
cambios" (decisión 4, arriba) devuelve la tarea a `en_curso` para que se
corrija, pero dos cosas de la entrega original seguían contando para
siempre, como si nunca se hubiera pedido cambios:

1. **T6a -- una aprobación anterior no sobrevive a "Pedir cambios".**
   `motivo_no_cierra_tarea` contaba cualquier `approval` 'aprobado' del
   aprobador, de cualquier momento: si esa aprobación no había alcanzado
   para cerrar (por ejemplo por un bloqueo abierto) y después el aprobador
   pedía cambios, el trabajo corregido podía cerrarse sin que nadie lo
   aprobara. Ahora una fila 'aprobado' cuenta sólo si es la ÚLTIMA decisión
   del aprobador sobre la tarea -- el empate de `at` falla cerrado, nunca
   aprobado. Migración `0013_aprobacion_no_sobrevive_a_pedir_cambios.sql`.
2. **T6b -- la entrega pide evidencia nueva.** `evidencia_pendiente`
   contaba cualquier fila de `evidence` de la tarea, aunque fuera de antes
   del "Pedir cambios": la evidencia de la primera entrega alcanzaba para
   que `_actualizar_estado` no pidiera nada, y descartaba en silencio el
   `evidencia_texto` de la reentrega. Decisión del usuario (2026-09-27): si
   se pidieron cambios, la evidencia vieja deja de contar -- ejemplo,
   pintar una pared, al aprobador le faltó una parte, la evidencia nueva
   tiene que mostrar esa parte pintada. Ahora `evidencia_pendiente` cuenta
   sólo evidencia con `at` estrictamente posterior al último `approval`
   'rechazado' de la tarea (de cualquier aprobador, el empate falla
   cerrado igual que en T6a); sin ningún 'rechazado', el comportamiento no
   cambia. `_actualizar_estado` pasa a registrar el `evidencia_texto` de la
   reentrega siempre que llegue, no sólo cuando `evidencia_pendiente` es
   verdadero -- así deja de descartarlo en silencio incluso fuera del caso
   de "Pedir cambios" (por ejemplo, alguien que manda evidencia otra vez
   sin que se la hayan pedido). Migración
   `0014_evidencia_no_sobrevive_a_pedir_cambios.sql`.

Las dos migraciones tocan sólo el cuerpo de su función (no son `security
definer`; corren con los privilegios de quien llama, y `evidence`/
`approval` ya tienen `select` concedido a `leda_app`); el menú de tarea
(`menu_tarea.evidencia_pendiente`) y el gate de "Aprobar"
(`_exigir_puede_aprobarse`) heredan la corrección sin cambiar, porque las
dos llaman a la misma función SQL.

3. **T6c -- "Pedir cambios" con una dependencia bloqueante abierta.**
   `pedir_cambios_tarea` siempre devolvía la tarea a `en_curso` (decisión 4,
   arriba); el disparador `exigir_dependencias_resueltas` (0008) rechaza
   CUALQUIER llegada a `en_curso` con una dependencia bloqueante todavía
   abierta, salvo la restauración desde `bloqueada` -- así que con esa
   dependencia abierta, el insert chocaba con el disparador y el aprobador
   no podía pedir cambios en absoluto (hallazgo anotado al cerrar T6a).
   Enmienda a la decisión 4: la tarea vuelve al estado que tenía antes de
   la ÚLTIMA entrada a `en_revision` -- `en_curso` si estaba en curso (una
   restauración, exenta del gate igual que salir de `bloqueada`),
   `asignada` en cualquier otro caso (se entregó sin haber arrancado nunca,
   o no hay un evento anterior registrado -- "Ya la terminé" se ofrece
   desde `asignada`). Función nueva `estado_previo_a_revision` (misma
   puerta angosta que `estado_previo_a_bloqueo`, 0007: `security definer`,
   dueño `leda_owner`, sin `execute` para `public`), y la misma rama de
   excepción en el disparador. El chequeo proactivo de
   `_actualizar_estado`/`_preparar_actualizar_estado` para `en_curso` gana
   la misma rama, por consistencia con el disparador. Migración
   `0015_pedir_cambios_exento_del_gate_de_arranque.sql`.

4. **T6i -- evidencia nueva en revisión no deja aprobar sin verla.** El
   aviso de entrega (decisión 3, arriba) queda esperando en el chat del
   aprobador con "Aprobar"/"Pedir cambios" -- pero si entre que se manda y
   que se toca llega evidencia nueva sobre la misma tarea, todavía
   `en_revision` -- una entrega repetida (T6g) o "Adjuntar evidencia" --, el
   aviso queda desactualizado: sus botones siguen respondiendo sobre la
   evidencia vieja, y "Aprobar" podía cerrar sin que el aprobador hubiera
   visto la nueva. Decisión del usuario (2026-09-27): si esa evidencia la
   manda alguien que NO es el aprobador, el aviso que tiene esperando queda
   retirado (`pendientes.retirar_avisos_de_entrega`, el mismo criterio
   'vencida' que usa `despachador._preview_vigente` para una vista previa
   superada -- tocar su "Aprobar" viejo responde "ya no está vigente", nunca
   aplica nada) y sale un aviso nuevo con TODA la evidencia vigente del
   ciclo actual (`_evidencia_vigente`, mismo corte que `evidencia_pendiente`,
   enmienda T6b) y los mismos botones. El dedupe del aviso nuevo usa el id
   de esta evidencia, nunca el del aviso que reemplaza. Si quien manda la
   evidencia es el propio aprobador, no hay a quién avisar de nuevo -- ya lo
   sabe -- y el aviso que esperaba sigue como estaba. El retiro nunca toca
   el menú general de la tarea (`_encolar_menu_tarea`, mismo
   `SENTINEL_MENU_TAREA`): se distingue porque ese menú siempre ofrece
   "Quiero consultar otra cosa" y el aviso de entrega nunca. Sin migración
   -- sólo `src/leda/herramientas.py` (`_notificar_entrega_al_aprobador`,
   `_evidencia_vigente`, `_avisar_evidencia_nueva_en_revision`) y
   `src/leda/pendientes.py` (`retirar_avisos_de_entrega`). Hoy no existe
   edición del lado de Telegram para borrar los botones del mensaje viejo ya
   entregado (el transporte sólo manda, `despachador.Transporte.enviar`) --
   el mensaje viejo puede seguir visible en el chat, pero tocar sus botones
   ya no aplica nada.

## Nota (2026-10-08): la evidencia por tipo y la entrega por el motor (ADR 0019)

El [ADR 0019](0019-evidencia-y-pagina-de-la-tarea.md) (decisiones 3 y 5, migración `0034`) cambia lo
que este ADR llamaba "la evidencia que exige su política": `evidencia_pendiente` sigue siendo la única
fuente, pero la política se cumple por tipo (cada tipo pedido, una pieza propia del ciclo vigente, no
retirada, de una clase que ese tipo acepta), así que una frase sola ya no cubre una foto. La evidencia
deja de ser sólo texto (texto, imagen, archivo o enlace, con la clase que fija el código) y no se edita
ni se borra: una pieza equivocada se retira. La entrega por chat la recibe el motor
(`src/leda/motor/entrega.py`), con vista previa y confirmación, y la cocina la escribe en un solo acto
(`entregar_tarea`). Lo que este ADR dejaba fuera sigue pendiente en las porciones siguientes del ADR
0019: el aviso a quien aprueba sigue siendo el de texto fijo de `_notificar_entrega_al_aprobador`, sin
las fotos (porción 3), y `_enlace_portal_tarea` sigue sin inventar ninguna URL hasta que exista la página
de la tarea (porción 4; constitución §4).
