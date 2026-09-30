# Prisma orienta

**Estado:** en curso
**Creado:** 2026-09-25
**Origen:** [`ADR 0007`](../../docs/decisions/0007-prisma-orienta-no-charla.md);
acciones por tarea en `docs/architecture/interpretacion-y-confirmacion.md` §4.6;
evidencia en §5.13 (primera sesión por Telegram real).

## Objetivo

Que Prisma oriente a las personas con opciones concretas en lugar de preguntas
abiertas: cada respuesta que espera algo cierra con botones y una salida, las listas
de tareas son botones y tocar una tarea ofrece lo que se puede hacer con ella.

## Problema (sesión del 2026-09-25)

- El modelo pregunta con texto abierto ("¿Querés que vea…?", "decime y la paso a
  revisión", "¿Qué querés cambiar?"); las respuestas vagas que eso invita se
  interpretan mal ("la tarea" tomada como nombre de una tarea).
- Presentó una suposición como hecho ("claramente va detrás").
- Las aclaraciones con botones fueron innecesarias porque la persona hablaba de una
  tarea que Prisma acababa de listar como texto.
- Hoy sólo existen botones para confirmar, para la duda de referencia y para el alta
  guiada de tareas.

## Alcance

**Incluido:** herramienta para que el modelo ofrezca opciones validadas por el
servidor; menú de acciones al tocar una tarea (diseño §4.6, sólo las acciones con
herramienta); listas de tareas como botones; reglas del contexto (no preguntar con
texto abierto, no presentar suposiciones como hechos); banco y continuidad.

**Excluido:** aportes sobre tareas (texto, foto, video; unidad propia en el roadmap);
las propuestas a medir aparte (filtro de tareas propias en autoinformes, hilo de la
conversación para Jev, referencias genéricas fuera de Jev); opciones en el grupo de
gestión.

## Tareas

- [x] **T1 — Opciones del modelo.** Herramienta con la que el modelo pide una
  elección: pregunta y opciones (texto o tarea por id). El servidor valida las tareas
  contra PostgreSQL bajo RLS, arma los botones con "Quiero consultar otra cosa" y una
  `pending_action` de un solo uso. Tocar una opción equivale a que la persona la haya
  elegido: el turno siguiente la recibe con la tarea resuelta, sin pasar por Jev.
  Reglas en el contexto: no preguntar con texto abierto; no presentar suposiciones
  como hechos.
- [x] **T2 — Menú de tarea.** Tocar una tarea ofrece las acciones del diseño §4.6
  según estado y relación (responsable, aprobador, otra persona), calculadas por
  código. Cada acción sigue su camino: ver detalle (lectura), acciones que cambian
  (herramienta con vista previa), acciones que necesitan un dato (por ejemplo la causa
  de un bloqueo) lo piden.
- [x] **T2b — Autoridad sobre tareas ajenas.** Hallazgo del orquestador tras T2
  (`0814fa3`): `actualizar_estado`, `registrar_bloqueo` y `adjuntar_evidencia` no
  verificaban que quien las llama tenga algo que ver con la tarea -- cualquier
  integrante autenticado del espacio podía mover el estado, declarar un bloqueo o
  adjuntar evidencia sobre la tarea de otra persona. En la sesión real por Telegram
  sólo la reticencia del modelo lo evitó ("Ese no es tuyo"), no el servidor. Se agrega
  el chequeo de autoridad a las tres herramientas (responsable, y además el aprobador
  para evidencia) y se corrigen dos defectos que la revisión RDD de T2 encontró en
  `gateway._ejecutar_accion_menu` (no atajaba `Denegado`; el rechazo de la base corría
  sin punto de retorno).
- [x] **T3 — Listas como botones.** Una respuesta que presenta tareas para elegir las
  ofrece como botones (por la herramienta de T1 o por la consulta misma).
- [x] **T4 — Banco.** Escenarios: lista de tareas con botones, tocar una tarea y
  llegar a la vista previa, pregunta de Prisma siempre con opciones; comprobador que
  falla ante una pregunta abierta sin opciones.
- [x] **T4b — Cierre genérico de una pregunta sin opciones.** Decisión del usuario
  (2026-09-26, evidencia real b-0007): si el turno cierra preguntando en texto
  abierto y sin ningún juego de botones propio, el servidor agrega un juego fijo de
  tres botones ("Es una tarea nueva", "Es sobre una tarea existente", "Quiero
  consultar otra cosa"); regla reforzada en el contexto para que el modelo llame a
  `ofrecer_opciones` igual sin opciones concretas.
- [ ] **T5 — Continuidad.** `docs/capacidades.md`, `docs/STATUS.md`, diseño §4.5 y
  segunda sesión por Telegram.
  - [x] Documentación (2026-09-26, ver Progreso).
  - [ ] Segunda sesión real por Telegram, datos ficticios (necesita al usuario).
- [x] **T7 — Base nueva y siembra reproducible para la tercera ronda por Telegram.**
  Decisión del usuario (2026-09-27): base dedicada nueva (`prisma`) creada desde
  `db/esquema.sql` completo (ya con 0013-0016), sembrada con un comando reproducible
  (mismas personas del pack y mismas tareas ficticias, títulos sin "(simulado)",
  `evidencia_requerida` coherente con la política del pack, estados iniciales que
  permitan probar la entrega con evidencia y "Pedir cambios"). La base actual
  (`postgres`, con los datos de las sesiones 1 y 2) queda intacta como respaldo. El
  usuario cambia el nombre de la base en su `.env`; las cuentas de Telegram se
  vuelven a vincular con `enlaces`.
- [ ] **T6 — Seguimientos de review-c112506a (entrega con evidencia).**
  - [x] **T6a — Una aprobación anterior no sobrevive a "Pedir cambios".**
    `motivo_no_cierra_tarea` acepta cualquier `approval` `aprobado` del
    aprobador, de cualquier momento: si una aprobación no cerró la tarea
    (dependencia o bloqueo abierto) y después el aprobador pidió cambios, al
    volver a entregar la tarea puede cerrarse sin que nadie apruebe el trabajo
    corregido. Cuenta sólo si la última decisión del aprobador sobre la tarea
    es `aprobado` (empate de `at` = no aprobada). Migración `0013`.
  - [x] **T6b — Después de "Pedir cambios", la entrega pide evidencia nueva.**
    Defecto: al volver a entregar, `evidencia_pendiente` ya es falso (quedó la
    evidencia de la primera entrega), así que `_actualizar_estado` descarta el
    `evidencia_texto` nuevo aunque la vista previa y el aviso al aprobador lo
    muestran. Decisión del usuario (2026-09-27): si se pidieron cambios, la
    evidencia vieja deja de contar y hay que volver a enviar evidencia (ejemplo:
    pintar una pared, el aprobador dice que faltó una parte, la evidencia nueva
    muestra esa parte pintada). `evidencia_pendiente` cuenta sólo evidencia con
    `at` posterior al último `rechazado`; la evidencia enviada en la entrega se
    registra siempre. Migración `0014`; enmienda en ADR 0009.
  - [x] **T6c — "Pedir cambios" con una dependencia bloqueante abierta.** Hoy la
    vuelta a `en_curso` la rechaza el disparador de `0008` y el aprobador no puede
    pedir cambios. Decisión del usuario (2026-09-27): vuelve al estado que tenía
    antes de la última entrada a `en_revision` -- `en_curso` si estaba en curso (es
    una restauración, exenta del gate de arranque, igual que salir de `bloqueada`),
    `asignada` si se entregó sin haber arrancado ("Ya la terminé" se ofrece desde
    `asignada`). Enmienda la decisión 4 de ADR 0009 ("vuelve a `en_curso`").
  - [x] **T6d — Dedupe estable del aviso de entrega.** `_notificar_entrega_al_aprobador`
    recibe `evidencia_id or uuid.uuid4()`: sin evidencia, la clave es aleatoria y no
    deduplica nada. Derivarla de la identidad del acto de entrega.
  - [x] **T6e — Prueba de punta a punta de "Pedir cambios".**
  - [x] **T6f — Serializar las decisiones y avisos concurrentes sobre una misma tarea**
    (review-3cf89bef, review-ae0ab510). "Aprobar" y "Pedir cambios" simultáneos, y dos
    evidencias simultáneas sobre una tarea en revisión (cada transacción retira los
    avisos que ve y crea el suyo: el aprobador puede quedar con dos avisos esperando,
    uno sin toda la evidencia). Bloquear la fila de `task` al empezar esos actos.
    Sumar pruebas: el menú general del aprobador sobre la misma tarea no se retira;
    la evidencia previa a un 'rechazado' no aparece en el aviso (con un texto
    distintivo, no uno por defecto).
  - [x] **T6g — Empate de evidencia y entrega repetida en `en_revision`** (review-e719d807,
    review-09452c69). Una entrega repetida sobre una tarea ya `en_revision` inserta
    un evento `en_revision -> en_revision`: además de sumar evidencia, hace que
    `estado_previo_a_revision` devuelva `en_revision` y que "Pedir cambios" mande a
    `asignada` una tarea que estaba en curso (y el empate de `at` en una misma
    transacción queda sin desempate). Decisión del usuario (2026-09-27): sobre una
    tarea que ya está `en_revision`, "ya la terminé" no registra ningún cambio de
    estado; la evidencia que llegue se suma como un adjunto más (igual que "Adjuntar
    evidencia") y Prisma avisa que ya está en revisión y que sumó la evidencia para
    quien la revisa.
    Sumar pruebas: previo nulo -> `asignada`; rama `en_revision` de
    `_preparar_actualizar_estado` sin confirmar.
  - [x] **T6j — La hora de escritura como regla del esquema** (review-5085907d).
    Sólo los cuatro actos bloqueados fijan `at = clock_timestamp()`; el resto de
    quienes escriben `task_state_event`, `evidence` y `approval` (transiciones del
    sistema, cargas administrativas) sigue con `now()`. Cambiar el `default` de
    esas columnas a `clock_timestamp()` en una migración para que el orden por `at`
    valga para todos, y reforzar la prueba de T6h: la `pending_action` que queda
    tiene que estar `esperando` y ser la del único mensaje.
  - [x] **T6i — Evidencia nueva en revisión reemplaza el aviso del aprobador.**
    Decisión del usuario (2026-09-27): cuando llega evidencia nueva a una tarea
    `en_revision` (entrega repetida o "Adjuntar evidencia") de alguien que no es el
    aprobador, se retiran los botones del aviso que el aprobador tiene esperando y
    sale un aviso nuevo con toda la evidencia y "Aprobar"/"Pedir cambios". Así nunca
    aprueba sin ver la evidencia vigente (ADR 0009).
  - [x] **T6h — Seguimientos de review-6b1efba1 sobre el aviso de entrega.** (1) Dos
    entregas reales en una misma transacción colapsan en un solo aviso y la prueba
    lo da por correcto sin verificar que no queden `pending_action` de botones
    huérfanas; (2) `pg_current_xact_id()` se consulta aunque haya `evidencia_id` y
    exige PostgreSQL 13+: consultarla sólo sin evidencia y fijar la versión mínima;
    (3) ninguna prueba verifica la forma de la clave (`tarea_id` + transacción) ni
    que dos tareas en la misma transacción no colisionen.
- [x] **T8 — Latencia de la ronda 3 (R3-H21).** Orden decidido por el usuario el
  2026-09-28: después de leer el manual de personalidad (hecho el 2026-09-28, ver
  Progreso).
  - [x] **T8a — Clave del proveedor conversacional según el proveedor.** Hoy
    `llm.desde_base` recibe siempre `PRISMA_LLM_API_KEY` (`gateway.py`, banco,
    `modelos`): con `openrouter` le mandaría a OpenRouter la clave de otro proveedor.
    OpenRouter usa `PRISMA_OPENROUTER_API_KEY` (la misma de Jev); si falta la clave del
    proveedor configurado, error claro, nunca la otra clave.
  - [x] **T8b — Medir y elegir el modelo.** Con el banco real, `google/gemini-3.8-flash`
    y `openai/gpt-6-luna` contra `nan/deepseek-v4-flash`: latencia por llamada (ruteo y
    respuesta) y escenarios. Objetivo: menos de 4 s por turno sin empeorar ningún
    escenario. Elige el usuario; se configura con `python -m prisma modelo`.
    Resultado (ver Progreso): ningún modelo llega a 4 s porque cada turno hace unas tres
    llamadas seguidas. Decisión del usuario (2026-09-28): se mantiene
    `nan/deepseek-v4-flash` y se ataca la cantidad de llamadas (T8c).
  - [x] **T8c — Menos llamadas seguidas por turno.** Diseñar antes de escribir código
    cómo bajar las llamadas al modelo de cada turno (hoy: una de ruteo tipado más una
    mediana de dos del ciclo de herramientas, hasta cuatro), sin perder las garantías
    del ruteo ni de las herramientas; medir con el mismo banco y el mismo complemento de
    latencias. Evidencia (banco con nombres de herramientas, 2026-09-28): en 24 de 27
    turnos que pasan por el responder la última llamada sigue a una herramienta que ya
    cerró el turno (`ofrecer_opciones` 10, vistas previas 14), tarda ~2,8 s y su texto se
    descarta (`agente.py:191-222`). Orden aprobado por el usuario, un commit por paso:
    - [x] **T8c-1 — Cortar el ciclo cuando la vuelta deja algo pendiente.** Si una vuelta
      registró una vista previa, un `NecesitaElegir` o `ofrecer_opciones`, el turno
      termina sin volver a llamar al modelo. Un rechazo (sin nada pendiente) sigue
      volviendo al modelo para que lo explique.
    - [x] **T8c-2 — Razonamiento configurable.** Descartada con evidencia (2026-09-28):
      la documentación de NaN (`/docs/models`) dice que en `deepseek-v4-flash` el
      razonamiento es adaptativo y el parámetro "no tiene efecto"; la sonda (8 pedidos
      por variante, con herramientas) muestra que `reasoning_effort: "none"` sí lo apaga
      (0 tokens en 8/8) pero no acelera: por defecto 2,90 s, `none` 2,27 s, `high` 1,81 s
      de mediana. La variación del servidor pesa más que ~100 tokens de razonamiento, y
      apagarlo arriesga la calidad.
    - [x] ~~**T8c-3 — Ruteo en paralelo con la primera llamada del responder**~~ **Revertida el 2026-09-29** (`ccf5c73`, ver Progreso y ADR 0012)., sólo en
      conversación normal sin referencias a tareas; se descarta si el ruteo elige otro
      camino.
    - [x] **T8c-4 — Tiempo máximo por llamada al modelo.** NaN cuelga a veces un pedido
      unos 93-95 s (~1,3 % de las llamadas en serie) y el cliente hoy espera hasta 600 s.
      Acotar cada intento (~20 s, configurable en `model_config.parametros`) con
      reintento, para que un cuelgue cueste ~20 s y no más de 90.
- [ ] **T8d — Responder en un solo viaje (postergada).** Decisión del usuario
  (2026-09-29): es una optimización; va después de T11 (la prioridad es que Prisma
  responda y se comporte como se espera: T9, T10 y la cuarta ronda). Evitar la vuelta de datos del responder
  (`consultar_tareas` y similares) cuando el dato ya viaja en el contexto, reconstruyendo
  los botones de lista desde el contexto (ADR 0007 §3). Es la palanca que puede acercar
  el turno a menos de 4 s; medir con el banco.
- [ ] **T9 — Estado de la conversación (ronda 3), por reglas generales**
  ([`ADR 0013`](../../docs/decisions/0013-reglas-generales-de-la-conversacion.md)).
  Decisión del usuario (2026-09-29): no parchear caso por caso; cada regla con su
  mecanismo, los hallazgos R3 como casos de prueba y familias de variantes. Mapeo de
  causas en Progreso.
  - [ ] **T9-R1 — Una pregunta pendiente es contexto, no una trampa** (H17, H19
    probable, parte de H20). Hoy `_resumir_dato_menu_tarea` acepta cualquier texto no
    vacío (`gateway.py:1831-1858`) y la marca se consume antes de interpretar; el alta
    guiada (`ingreso_tareas.handle_active_text`) también toma el mensaje siguiente. El
    ruteo tipado recibe la pregunta pendiente y devuelve un comando de una lista cerrada
    (responde, corrige, cancela, otro tema con retome, charla, dudoso, no puedo; patrón
    de "conversation repair" de los asistentes de tareas, ADR 0013), cada uno con un
    manejo determinista. Por etapas, un commit cada una:
    - [x] **T9-R1a — Contrato del ruteo y dato pedido desde el menú** (el caso de H17:
      evidencia, causa y resolución de bloqueo, motivo de cambios, adjuntar evidencia).
      - [x] **T9-R1a-1** — contrato del ruteo con pregunta pendiente y comandos
        responde, cancela, charla, no puedo y otro tema (corrige y dudoso vuelven a
        preguntar, interino).
      - [x] **T9-R1a-2** — dudoso con botones, retome "¿seguimos?" después de otro tema,
        corrige, y escenarios del banco con familias de variantes (medir el prompt).
        Seguimientos de `review-c10ae20ecdf4cfa0` (aprobada; frontera en `8c53652`): prueba
        del caso en que otro turno consumió la pregunta antes de `responde` (una sola
        respuesta); `cancela` debe mirar el resultado del consumo antes de decir "dejé de
        lado"; `reintentos` entero escrito como `2.0` debe aceptarse.
    - [x] **T9-R1b — Corrección abierta** (Modificar y "Ninguna, lo escribo"). Incluye los
      seguimientos de `review-dd7cd3c9cb7e8575`: el arnés del banco manda los mensajes
      posteriores a los toques con el mismo `message_id`; falta la prueba del botón "No,
      es otra cosa" cuando falla el ruteo.
    - [x] **T9-R1b-2 — Contestar una pregunta pendiente no abre una búsqueda de tareas;
      otro tema no la vuelve a proponer** (precisión del ADR 0013 regla 1, banco `b-0020`).
      Más los seguimientos de `review-e95b2d47b01f0161`: prueba de "Sí, es eso" con el
      ruteo caído (Modificar y "Ninguna"); una ruta con contexto que resuelva referencias.
    - [ ] **T9-R1c — Preguntas del alta guiada** (`ingreso_tareas.handle_active_text`).
      Hoy el alta corre antes de `_turno` y fuera del ruteo tipado: el campo de texto
      libre toma el mensaje siguiente sin interpretarlo, y con botones o confirmación
      abiertos el mensaje se traga con un recordatorio.
      - [x] **T9-R1c-0** — seguimientos de `review-34b692649e0734e7`: guarda de
        `otro_tema` para "destrabar" (clave `bloqueo_id`) y para Modificar de una
        herramienta cuyo id no es `tarea_id` (`resolver_bloqueo`); `resolucion is None`
        en el filtro `solo_claras`; aserción positiva del caso "otra tarea" del dato
        del menú.
      - [ ] **T9-R1c-1** — el campo de texto libre del alta pasa por el manejo genérico
        (`_atender_pregunta_pendiente` con un adaptador en `_pregunta_de`), con su
        familia del banco. `cancela` cancela el borrador (el mismo camino del botón
        Cancelar del alta: sin la pregunta el alta no puede seguir); `corrige` usa un
        camino de cambio de campo si el alta lo tiene, si no los botones de `dudoso`.
      - [x] **T9-R1c-2** — texto con botones del alta o confirmación abiertos: la misma
        regla, en vez de tragarse el mensaje con un recordatorio. Más los seguimientos no
        bloqueantes de `review-06b7019b060dbffb`: una prueba que ate las claves de
        `FREE_TEXT_NAMES` a las de `USER_FIELD_LIMITS` (hoy son las mismas 7; un campo
        nuevo sin nombre rompería cada mensaje del chat); aclarar el comentario de
        `_CAMPOS_DE_ID` (hoy ninguna herramienta cruza el orden: `crear_dependencia` usa
        `origen_tarea_id`/`destino_tarea_id`, `quitar_dependencia` sólo `dependencia_id`);
        el campo `pending_action_id` de `ModificacionAbierta` lleva el id del campo del
        alta (nombre neutro o tipo propio); afirmar la respuesta exacta del segundo toque
        de "Dejarlo" y de "Sí, es eso" tardíos en `test_alta_pregunta_pendiente.py`.
        Compromiso aceptado por la regla 1 (R4): el alta ahora depende del ruteo; con el
        ruteo caído el campo queda abierto y cada campo suma una llamada de ruteo.
  - [x] **T9-R1d — Una sola rama de conversación abierta** (enmienda del ADR 0013 regla
    1, decisión del usuario del 2026-09-29). Con una pregunta abierta, `otro_tema` ya no
    se atiende: una pregunta con botones **[Seguir con …]** / **[Dejar … y ver lo
    otro]**; Seguir repite la pregunta pendiente; Dejar cierra lo pendiente como
    `cancela` y atiende el mensaje guardado en la misma respuesta. "No, es otra cosa" de
    `dudoso` es la misma salida. Una rama está abierta sólo para quien debe responderla
    (el borrador que espera a otro aprobador no bloquea a quien lo pidió). Quitar el
    retome posterior (`_retomar_dato_pendiente`, `retomar` en `_turno`) y la guarda
    `agente.NoProponer` de R1b-3. Actualizar `b-0020`, `b-0021-c` y `b-0022-b` a la
    regla nueva. Va después de T9-R1c-2b (mismos archivos). Los mensajes que inicia
    Prisma (cadencias, avisos, escalera) dirigidos a quien tiene una rama abierta quedan
    retenidos hasta que se cierra (decisión del usuario, opción A); la retención termina
    al vencer la pregunta pendiente (a definir un vencimiento donde no lo haya). Puede
    partirse en R1d-1 (la pregunta de la rama) y R1d-2 (retención en el despacho).
    - [x] **T9-R1d-1a** — la pregunta de la rama para las preguntas pendientes que ya
      pasan por `_atender_pregunta_pendiente`; "No, es otra cosa" de `dudoso`; quitar
      el retome y `agente.NoProponer`; el borrador que espera a otro aprobador no es rama
      de quien lo pidió; escenarios `b-0020`, `b-0021-c`, `b-0022-b` a la regla nueva.
    - [x] **T9-R1d-1a-fix** — reponer la guarda contra volver a proponer lo que la persona
      acaba de dejar, en el camino "Dejarlo y ver lo otro" (banco `b-0020-f` 0/3: tras
      dejar el bloqueo, el responder lo volvió a proponer desde el historial); el toque
      "dejar" sólo con su valor explícito (`review-2282ebc46e7a48e1`, R3).
    - [x] **T9-R1d-1b** — la vista previa de un cambio que la persona pidió y espera su
      Confirmar pasa a ser rama (hoy el texto sigue el turno normal). Más los seguimientos
      de `review-ed284b3aec853536`: probar la guarda para las acciones del menú
      `destrabar`, `informar_bloqueo`, `adjuntar_evidencia` y `pedir_cambios` (que sus
      argumentos lleven el id que la guarda compara), y la guarda al retomar tras botones
      de aclaración.
    - [x] **T9-R1d-1c** — la aclaración con botones ("¿A cuál te referís?", elección de
      herramienta con `campo`) también es rama, y un turno nunca abre dos cosas: si una
      llamada a herramienta abre una pregunta (elección o vista previa), el turno termina
      ahí (banco `b-0023`: el responder abrió la aclaración y además la vista previa en el
      mismo turno). Más los seguimientos de `review-0c99f611fc23e0cd`: prueba del caso en
      que la vista previa no entra con botones, y de las vistas previas armadas desde el
      menú (y con `bloqueo_id`).
    - [x] **T9-R1d-2b** — tras `review-080f1ef080f22e16`: acotar la pasada de
      `despachar` (hoy, con filas retenidas, sigue pidiendo lotes sin tope dentro de una
      sola transacción con bloqueos y envíos), alinear su comentario, hacer explícito que
      una respuesta nunca se retiene, y la ventana de retención decidida por el usuario
      (2026-09-29): retener sólo si la persona escribió o tocó algo en ese chat en los
      últimos 30 minutos; así también retienen las preguntas del alta (sin vencimiento) y
      un urgente no espera horas por una rama abandonada.
    - [x] **T9-R1d-2** — retención de los mensajes que inicia Prisma mientras la persona
      tiene una rama abierta, hasta que vence la pregunta. Más los seguimientos de
      `review-faccc0e9d83561b3`: controlar que una elección sin prefijo entre con sus
      botones al volver a mostrarla; probar la guarda de un turno con una elección
      (`NecesitaElegir`) primero; que la siembra de la aclaración del banco no copie a
      mano el estado interno de `_preguntar_por_botones`.
  - [x] **T9-R1c-3 — Modificar en la vista previa del alta** (precisión del ADR 0005
    decisión 1, decisión del usuario del 2026-09-29). La vista previa del borrador pasa
    a **[Confirmar] [Modificar] [Cancelar]**; Modificar pregunta qué dato cambiar (un
    botón por dato); un dato de texto muestra lo escrito en un bloque copiable (y
    `copy_text` si entra en 256 caracteres) para pegarlo, corregirlo y mandarlo; un dato
    con opciones vuelve a mostrar sus botones; cambia sólo ese dato y vuelve la vista
    previa actualizada. `corrige` sobre la vista previa lleva a este camino en vez de
    `AVISO_ALTA_NO_SE_CORRIGE`. Después de T9-R1d. Más los seguimientos de
    `review-3ebe127d376a4d18`: probar que el mensaje que muestra la elección del alta no
    se retiene contra su propia rama; que el conteo de `retenidos` respete el vencimiento
    y el bloqueo de las filas (y que lo vencido de alguien retenido se descarte igual);
    un reloj único en la prueba del toque; y la prueba del aprobador sin nombre legible.
  - [x] **T9-R1c-3b — Ajustes de Modificar en el alta.** La vista previa que sigue a
    Modificar, cuando quien pide es quien confirma, sale como respuesta (hoy es un mensaje
    que inicia Prisma y queda sujeto a horario, tope diario y retención: fuera de horario la
    persona no recibiría el resumen corregido); botón [Volver al resumen] en el selector
    (hoy salir sólo se puede cancelando el borrador); la fecha objetivo se muestra en
    formato de la persona, no ISO; al repreguntar un campo tras una charla vuelve el bloque
    copiable; y los seguimientos de `review-8563632f45a44f88` (campo sin fila en
    `_ask_field_change`; un solo reloj en el conteo de `retenidos`). Pendiente de
    decisión del usuario: Modificar cuando confirma otra persona.
  - [x] **T9-R2 — Cada mensaje recibe exactamente una respuesta visible** (H15, H19).
    Ojo: desde `3255418` cada toque deja una fila de `inbound_message` sin texto (para
    medir la actividad); el control de una respuesta por mensaje tiene que contemplarlas.
    `procesar_update` sólo lee `text` (`gateway.py:213`); control estructural al cerrar
    el mensaje; epígrafe como texto; comprobación del banco y del validador.
  - [x] **T9-R2b — Seguimientos de la respuesta única.** Encontrar los caminos que encolan
    más de una respuesta independiente para un mismo mensaje sin marcarlas como grupo (el
    control ahora descarta todas menos una, con incidente) y agruparlos; revisar los caminos
    que a propósito no responden (sobre todo en grupos, donde ahora saldría el aviso neutro);
    y las pruebas débiles de `review-cfe9d0884f17b144` (aserción vacía del epígrafe; la
    prueba del toque en el banco no toca nada). Evidencia: banco completo con la
    comprobación nueva. Más: tras "Dejarlo y ver lo otro" sobre una pregunta del alta, el
    responder vuelve a proponer el alta (`b-0021-i`: "Para armar la tarea nueva, necesito
    saber dónde cuelga"); causa general: en ese turno el modelo no ve el "dejé de lado"
    (el historial sólo cuenta lo enviado) y la guarda no cubre el alta.
  - [x] **T9-R3 — Decir el estado real y ofrecer sólo lo posible** (H20, H18, H16).
    Incluye (de T9-R2b): cuando quien pide el alta no es quien confirma, al terminar el alta
    no le sale ninguna respuesta y el control le manda "No pude completar eso" aunque salió
    bien (tiene que decir a quién se le mandó para confirmar); tres resultados del alta
    ("No hay una política de evidencia vigente…", "Alguna opción confirmada ya no está
    vigente.", "No hay una autoridad activa…") devuelven un texto que nadie encola; tras
    "Dejarlo" con la guarda, el modelo afirmó "registré" lo que la guarda le rechazó
    (`b-0020-f-1`). Y las pruebas pendientes de `review-467d41b3f96573d5`.
    Incluye (de `review-2282ebc46e7a48e1`): quien pidió un borrador que espera a otro
    aprobador no recibe un aviso determinista de quién confirma cuando escribe sobre él.
    `adjuntar_evidencia` sobre una tarea en curso deja evidencia sin decirlo
    (`herramientas.py:1552-1559`); `contexto.PREAMBULO` obliga a inventar opciones
    (`contexto.py:70-77`); el motivo de "Pedir cambios" no está en ninguna lectura.
  - [x] **T9-R4 — Todo toque tiene señal inmediata y es idempotente** (H5, H13). Incluye
    también: la respuesta de "Dejarlo y ver lo otro" (dos mensajes sin agrupar, fuera del
    control porque es un toque); el control de una respuesta extendido a los toques; y
    `review-324fcff7f93c7f19` R3-001: un reintento con el mismo estado trabado del alta se
    descarta como duplicado y queda sin respuesta (la clave debe incluir el mensaje o toque
    que lo dispara); y el seguimiento de `review-e11061770c5f40ae`: la referencia del reenvío de una
    elección sin `entrante_id` sale de un conteo y no es idempotente ante un callback
    repetido (derivarla del evento que la dispara). El
    indicador sólo envuelve `_turno` (`gateway.py:333`); el segundo toque responde "ya no
    está vigente"; ventana de 10 s para la misma persona.
  - [ ] **T9-R4b — Seguimientos de `review-d9a1348555f00ca4`.** En el toque sobre un
    borrador, la marca de "botón ya tocado" se confirma antes de la resolución con
    autoridad: si ésta falla, el reintento o el reenvío de Telegram se absorbe en silencio
    (la marca tiene que confirmarse con el efecto, o no absorber si el primero no terminó);
    la clave de la fila terminal de la autoridad se rearma a mano en el gateway (compartirla
    con quien la produce); en `resend_choice_prompt` una `ref` explícita debe ganarle al
    evento atado; el 11 de las pruebas derivado de `VENTANA_TOQUE_REPETIDO`; nombre del
    comprobador del banco (cubre toques).
  - [ ] **T9-R1c-4 — Quien pide revisa antes de enviar a aprobación** (precisión del ADR
    0005, decisión del usuario del 2026-09-29, opción A). Cuando confirma otra persona, quien
    pide ve su resumen con [Enviar a aprobación] [Modificar] [Cancelar] (mismo selector de
    datos que T9-R1c-3); al enviar, le llega a quien confirma con Confirmar y Cancelar y a
    quien pide "Le mandé el borrador a {nombre}…". Hasta enviar es rama de quien pide.
  - [ ] **T9-H19 — Reproducir H19 después de R1 y R2**; si persiste, clasificarlo por
    regla antes de corregir.

- [ ] **T10 — Forma de las respuestas (ronda 3).** R3-H1, H2, H3/H7, H8, H9, H10, H11,
  H12, H14 y H4.
- [ ] **T11 — Cuarta ronda por Telegram**, en horario laboral, con los circuitos A y B.

## Ruta

| Tarea | Ruta | Evidencia del disparador |
|---|---|---|
| T1 | delegada, un escritor | `herramientas.py`, `agente.py`, `gateway.py`, `pendientes.py`, `contexto.py`, pruebas |
| T2 | delegada, un escritor | módulo nuevo o `gateway.py`, `herramientas.py`, pruebas |
| T2b | delegada, un escritor | `herramientas.py`, `gateway.py`, pruebas (3+ archivos de código) |
| T3 | a decidir tras T1 | depende de dónde quede la herramienta |
| T4 | delegada, un escritor | `tests/banco/` |
| T5 | inline | documentación |
| T6a | delegada, un escritor | `db/esquema.sql`, migración y rollback `0013`, pruebas (4 archivos) |
| T6b | delegada, un escritor | `db/esquema.sql`, migración y rollback `0014`, `herramientas.py`, ADR 0009, pruebas |
| T6d | delegada, un escritor | lectura de `herramientas.py`/`gateway.py`/`pendientes.py` para ubicar la identidad del acto + pruebas |
| T8a | delegada, un escritor | `config.py`, `llm.py`, `gateway.py` (3 llamadas), `cli.py`, `tests/banco/conftest.py`, pruebas |
| T8b | inline, corridas del banco real | medición; sin cambios de código |
| T8c-1 | delegada, un escritor | `agente.py` y pruebas de varios módulos (ciclo del responder) |
| T9-R1a-1 | delegada, un escritor | `llm.py`, `pendientes.py`, `gateway.py`, arnés del banco, pruebas |
| T8c-3 | delegada, un escritor | `gateway.py`, `agente.py`, `llm.py`, arnés del banco, pruebas, ADR 0012 |
| T9-R1c-0/1 | delegada, un escritor | `gateway.py`, `ingreso_tareas.py`, arnés y escenarios del banco, pruebas |
| T9-R1c-2 | delegada, un escritor | `gateway.py`, `ingreso_tareas.py`, `pendientes.py`, arnés y escenarios del banco, pruebas |
| T9-R1c-2b | delegada, un escritor | `gateway.py`, `ingreso_tareas.py`, `pendientes.py`, `llm.py` probable, arnés del banco, pruebas |

## Verificación

- TDD estricto (configuración de la sesión); runner
  `.venv/Scripts/python.exe -m pytest -q`.
- Línea base: 721 passed, 99 deselected (2026-09-24).
- Antes de correr la suite: `pg_isready`.
- Antes de una sesión real: comparar la base local con `db/esquema.sql` y aplicar
  migraciones pendientes (lección de la sesión del 2026-09-25).

## Entrega

Commits sobre `main` (renombrada desde `master` el 2026-09-25) por tarea, con pedido explícito del usuario (`AGENTS.md`);
cada commit con código pasa por la evaluación de RDD.

## Progreso

- 2026-09-25: documento creado; acciones por tarea decididas con el usuario (diseño
  §4.6).
- 2026-09-25: **T1 cerrada.** Ruta: delegada, un escritor (disparador de mapeo: 6
  archivos de código + pruebas).

  Archivos:
  - `src/prisma/herramientas.py`: herramienta `ofrecer_opciones` (`accion="consultar"`,
    sin `preparar`: no escribe nada), `MAX_OPCIONES_MODELO = 4`, `OpcionOfrecida`,
    excepción `NecesitaOpciones`, `_tareas_activas_por_id` (valida cada `tarea_id`
    contra PostgreSQL bajo el cursor con RLS del turno; activas del espacio, id de
    otro espacio o cerrado queda simplemente afuera).
  - `src/prisma/agente.py`: `_ejecutar_una` atrapa `NecesitaOpciones` y la reusa como
    `elecciones` (mismo cierre de turno sin texto que `NecesitaElegir`/
    `NecesitaConfirmacion`); `_encolar_opciones_modelo` arma la `pending_action` con
    el sentinel `pendientes.SENTINEL_OPCIONES_MODELO`, agrega siempre "Quiero
    consultar otra cosa" y la encola por outbox.
  - `src/prisma/gateway.py`: `_toque` intercepta el sentinel antes de `H.ejecutar`
    (mismo patrón que `_SENTINEL_ACLARACION`); `_resolver_toque_opcion_modelo` audita
    (tipo + id de tarea, nunca texto), cierra sin efecto en "Quiero consultar otra
    cosa" invitando a escribir, y para tarea/texto retoma llamando a
    `agente.responder` directo -- nunca a `_turno`/`route_intent`/Jev -- con la
    elección como contexto de confianza del servidor (`contexto_referencias`) y,
    para una tarea, `tareas_resueltas_claras` (protección T5 existente).
  - `src/prisma/pendientes.py`: `SENTINEL_OPCIONES_MODELO`, constante compartida
    entre `agente.py` (arma) y `gateway.py` (intercepta) -- vive acá porque ninguno
    de los dos módulos puede importar del otro sin ciclo.
  - `src/prisma/salida.py`: `TRUNCAR_ETIQUETA_BOTON` + `truncar_etiqueta_boton()`,
    extraídos de la regla de truncado que ya tenía `gateway._etiqueta_boton`, para
    reusarla en `ofrecer_opciones` en vez de duplicarla.
  - `src/prisma/gateway.py`: `TRUNCAR_TITULO_BOTON` pasa a ser alias de
    `salida.TRUNCAR_ETIQUETA_BOTON` (mismo valor, 48) y `_etiqueta_boton` llama a
    `truncar_etiqueta_boton` -- refactor de compatibilidad, las pruebas existentes
    de `test_aclaracion_botones.py` siguen referenciando `gateway.TRUNCAR_TITULO_BOTON`
    sin cambios.
  - `src/prisma/contexto.py`: tres reglas nuevas en `PREAMBULO` (usar
    `ofrecer_opciones` en vez de preguntar en texto abierto; ofrecer listas de tareas
    como opciones; no presentar una suposición como un hecho, ofrecerla para
    confirmar).
  - `tests/test_opciones_modelo.py` (nuevo, 13 pruebas).

  Decisiones de diseño:
  - **Reuso, no un mecanismo paralelo.** `ofrecer_opciones` es una herramienta más
    del `REGISTRO` (como pidió el enunciado): el modelo la llama con `pregunta` +
    `opciones` (cada una `texto` o `tarea_id` con `etiqueta` opcional), el handler
    valida y arma `NecesitaOpciones` -- misma familia que `NecesitaConfirmacion`/
    `NecesitaElegir`, mismo `pending_action`/`pending_action_option` de siempre
    (sin migración: no hizo falta ningún cambio de esquema).
  - **Por qué no reusar `NecesitaElegir` tal cual.** Tocar una opción de
    `NecesitaElegir` vuelve a llamar a la MISMA herramienta con el argumento ya
    resuelto (p. ej. "¿A quién le asigno la tarea?" -> `crear_borrador_tarea` de
    nuevo). Acá tocar una opción retoma la CONVERSACIÓN con el modelo, no vuelve a
    llamar a `ofrecer_opciones` -- son dos continuaciones distintas, así que
    necesitan una excepción y un sentinel propios; el body de `NecesitaElegir` (que
    sólo guarda un valor de texto suelto) tampoco alcanza para distinguir "tarea" de
    "texto" al resolver -- por eso `Opcion.valor` de cada opción es un dict con
    `tipo`.
  - **Por qué un sentinel y no una herramienta real en `pending_action.herramienta`.**
    Mismo motivo que `_SENTINEL_ACLARACION`: si el toque llamara de nuevo a
    `H.ejecutar("ofrecer_opciones", ...)`, el turno no avanzaría -- volvería a
    preguntar. El sentinel deja que `gateway._toque` lo intercepte antes de llegar a
    `H.ejecutar`.
  - **Validación de tareas.** `_tareas_activas_por_id` filtra ids que no son UUID
    válidos en Python (evita que un id inventado por el modelo rompa el `::uuid[]`
    de Postgres para toda la lista) y consulta `task` bajo el cursor con RLS del
    turno, sólo activas (`not in ('terminada','cancelada')`) del espacio: id
    inexistente, cerrado o de otro espacio se rechaza igual -- `Denegado` vuelve al
    modelo como error de argumento, para que reintente, nunca lo inventa.
  - **Tope de opciones.** `MAX_OPCIONES_MODELO = 4` (ADR 0007, "hasta cuatro
    opciones más la salida"); la salida "Quiero consultar otra cosa" la agrega
    siempre `_encolar_opciones_modelo`, no cuenta para el tope.
  - **Sin Jev al retomar una tarea.** El toque ya trae `tarea_id` + `titulo`
    resueltos por el propio `ofrecer_opciones` (validados contra la base al
    ofrecerlos); `_resolver_toque_opcion_modelo` llama a `agente.responder`
    directo, nunca a `gateway._turno`/`route_intent`, así que ni el enrutador ni Jev
    se consultan.
  - **Ventana de 30 minutos de "Ninguna, lo escribo" (T4).** No aplica acá: "Quiero
    consultar otra cosa" no dice que el próximo mensaje sea una corrección de nada
    puntual -- es un cierre limpio ("invita a escribir", enunciado punto 2) y el
    siguiente mensaje se rutea como un turno común, sin marca especial. Más simple
    que reusar `marcar_para_corregir`, y consistente con lo que pide el enunciado.

  RED (antes de implementar, `tests/test_opciones_modelo.py` contra el código sin
  la herramienta):
  `.venv/Scripts/python.exe -m pytest -q tests/test_opciones_modelo.py` ->
  `11 failed, 2 passed` (los 2 que ya pasaban en rojo son los de rechazo de un
  `tarea_id` inexistente/ajeno: sin la herramienta, `ofrecer_opciones` no existe y
  tampoco se arma ninguna `pending_action`, que es justo la aserción -- quedaron
  confirmados igual una vez implementada la herramienta, ya no por la ausencia).

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_opciones_modelo.py` ->
    `13 passed`.
  - `.venv/Scripts/python.exe -m pytest -q tests/test_opciones_modelo.py tests/banco`
    -> `169 passed, 99 deselected`.
  - `.venv/Scripts/python.exe -m pytest -q` (suite completa) ->
    `734 passed, 99 deselected` (línea base 721 + 13 pruebas nuevas de T1).

  Abierto: T2 (menú de tarea) no se tocó -- tocar una tarea ofrecida por T1 sólo
  retoma con la tarea resuelta, no abre ningún menú de acciones todavía. T3 (listas
  como botones) queda "a decidir tras T1"; con `ofrecer_opciones` ya construida como
  herramienta del `REGISTRO`, la vía más directa es que el modelo la llame también
  para listar tareas, sin una segunda herramienta -- a confirmar al empezar T3.
- 2026-09-25 (orquestador): T1 commiteada (`1db9e1f` documentación, `c253d27` código). Revisión
  RDD de fiabilidad aprobada y reconocida (`review-995bc30d2d0df7e8`). Observaciones no
  bloqueantes: `herramientas.py:281` (un id de tarea en mayúsculas no coincide al validar;
  se corrige en T2), `gateway.py:854-856` (verificar que la respuesta al retomar tras tocar
  una opción siempre se entregue; se revisa en T2), `agente.py:420-421` (sugerencia: la
  clave de deduplicación usa la marca de tiempo).
- 2026-09-25: **T2 cerrada.** Ruta: delegada, un escritor (disparador de mapeo: 6+ archivos
  de código + pruebas, igual que T1).

  Archivos:
  - `src/prisma/menu_tarea.py` (nuevo): `calcular_menu` (el menú determinístico de §4.6
    según estado y relación -- responsable/aprobador/otra persona --, calculada por
    código, nunca por el modelo), `detalle_tarea` (la lectura de "Ver detalle"/"Ver
    detalle y evidencia"), `bloqueos_abiertos`, `tareas_activas_de` (candidatas para
    una dependencia, tope `MAX_CANDIDATAS_DEPENDENCIA = 4`, mismo tope que T1).
  - `src/prisma/gateway.py`: sección nueva "Menú de acciones de una tarea" --
    `_encolar_menu_tarea`/`_abrir_menu_tarea` (arma o rearma el menú con sus botones),
    `_encolar_vista_previa_menu` (la vista previa de una acción del menú, mismos tres
    botones que `agente._encolar_confirmacion`), `_ejecutar_accion_menu` (corre una
    herramienta que ya existe sin `ya_confirmada`), `_pedir_dato_menu_tarea` (pide un
    dato en texto libre), `_pedir_eleccion_dependencia` (pide con botones cuál otra
    tarea), `_resolver_toque_menu_tarea`, `_resolver_toque_dato_menu_tarea`,
    `_resumir_dato_menu_tarea` -- más las dos correcciones de revisión de T1 (abajo) y
    el cableado nuevo en `_toque` (dos `elif` más, por `P.SENTINEL_MENU_TAREA` y
    `P.SENTINEL_DATO_MENU_TAREA`) y en `_turno` (reclama `SENTINEL_DATO_MENU_TAREA`
    antes de rutear, igual que "Ninguna, lo escribo").
  - `src/prisma/pendientes.py`: `SENTINEL_MENU_TAREA`, `SENTINEL_DATO_MENU_TAREA`,
    `ETIQUETA_SALIR_OPCIONES` (la etiqueta de salida de T1, movida acá para que el
    menú de T2 la reuse sin duplicarla).
  - `src/prisma/agente.py`: `_encolar_opciones_modelo` usa `P.ETIQUETA_SALIR_OPCIONES`
    en vez de su propia constante privada (refactor de compatibilidad, mismo valor).
  - `src/prisma/herramientas.py`: `ofrecer_opciones` gana un campo opcional `accion`
    por opción de tarea (`"responder"`, el de siempre, o `"menu"`, que abre el menú en
    vez de retomar la conversación); `_uuid_normalizado` (nuevo) + corrección de
    revisión de T1 sobre `_tareas_activas_por_id`/`_ofrecer_opciones` (abajo).
  - `tests/test_menu_tarea.py` (nuevo, 21 pruebas).

  Decisiones de diseño:
  - **Cómo se llega al menú.** El enunciado pedía "un nuevo tipo de opción en
    `ofrecer_opciones` o una entrada dedicada" -- se eligió lo primero: una opción de
    tarea de `ofrecer_opciones` (T1) gana un campo opcional `accion` (`"responder"` por
    defecto, o `"menu"`). El modelo sigue siendo quien ofrece la tarea como botón (T1
    ya la valida contra PostgreSQL); tocarla con `accion: "menu"` no retoma la
    conversación -- abre el menú que calcula `menu_tarea.calcular_menu`, sin llamar al
    modelo. Es el mismo mecanismo que reusará T3 para listar tareas como botones: no
    hizo falta una segunda herramienta ni un segundo camino de validación de tareas.
  - **Un sentinel para el menú, otro para el dato que le falta a una acción.**
    `SENTINEL_MENU_TAREA` es el menú en sí -- tocar una opción nunca resume al modelo,
    a diferencia de `SENTINEL_OPCIONES_MODELO` (T1). `SENTINEL_DATO_MENU_TAREA` es
    el dato que le falta a una acción para armar su vista previa, y tiene dos formas
    -- un texto libre (la causa de un bloqueo, su resolución, la evidencia) o una
    elección entre tareas conocidas (para una dependencia) -- porque se resuelven por
    dos caminos distintos del gateway (turno vs. toque, ver el punto siguiente). Los
    dos sentinelas viven en `pendientes.py`, igual que el de T1, porque las dos puntas
    (armar/interceptar) están en `gateway.py` pero en funciones distintas.
  - **Cómo se captura un dato en texto libre.** Se pidió explícitamente "el mismo
    patrón que 'Ninguna, lo escribo'" (T4, `aclaracion-con-botones`): en vez de un
    tercer mecanismo, `_pedir_dato_menu_tarea` registra una `pending_action` sin
    botones (`opciones=[]`) y la marca de inmediato con `marcar_para_corregir` -- la
    misma función que usa "Ninguna, lo escribo" para dejar el próximo mensaje de esa
    persona, en ese chat, como la respuesta. `_turno` la reclama con
    `reclamar_modificacion_abierta` antes de rutear (antes de `route_intent`, antes de
    Jev): el texto pasa directo como argumento de la herramienta -- causa, resolución,
    evidencia son datos que se pidieron, no una referencia que interpretar, así que no
    hace falta consultar al modelo para retomar.
  - **Cómo se captura una elección entre tareas (dependencias).** Distinto del texto
    libre: "de cuál otra tarea depende" tiene candidatas conocidas (las otras tareas
    activas de la persona, `menu_tarea.tareas_activas_de`, tope 4), así que se ofrecen
    con botones -- una `pending_action` con `campo="eleccion"`, igual que
    `NecesitaElegir`. Sin candidatas, no se inventa ninguna: se le dice a la persona
    que escriba y ese mensaje se rutea como un turno común.
  - **"Ya se destrabó" con más de un bloqueo abierto.** `registrar_bloqueo` permite
    sumar bloqueos a una tarea ya bloqueada, así que puede haber más de uno abierto a
    la vez -- el caso raro. En vez de inventar una forma de elegir cuál, se le pide a
    la persona que lo cuente completo en texto libre (el modelo ya tiene
    `consultar_bloqueos` y `resolver_bloqueo`); con exactamente uno abierto, va directo
    a pedir la resolución.
  - **Reuso de `motivo_no_arranca_tarea`.** "Empezar" no se ofrece con una dependencia
    bloqueante sin terminar (§4): en vez de reimplementar el chequeo, `_puede_empezar`
    llama a la misma función SQL que ya usa `herramientas._actualizar_estado` antes de
    intentar el pase a `en_curso` -- una sola fuente de verdad.
  - **Vista previa del menú, no `agente._encolar_confirmacion`.** Las acciones que
    cambian algo (Empezar, Ya la terminé, Aprobar, una dependencia) llaman a
    `herramientas.ejecutar` sin `ya_confirmada`, que frena en `NecesitaConfirmacion`
    porque las cuatro declaran `preparar` (ADR 0005, decisión 1): nada se aplica hasta
    la vista previa. `_encolar_vista_previa_menu` arma esa vista previa con los mismos
    tres botones que `agente._encolar_confirmacion`, pero es una función propia -- el
    menú nunca pasa por `agente.responder`, así que no hay una vuelta del modelo a la
    que devolverle el resultado.
  - **Ofrecer no autoriza.** El menú sólo determina qué botones aparecen; cada acción
    que escribe pasa igual por `herramientas.ejecutar`, que vuelve a verificar
    autoridad (`aprobar_tarea` rechaza la auto-aprobación, `crear_dependencia` exige
    ser responsable o referente de alguna de las dos tareas) sin importar qué mostró
    el menú.
  - **Dedupe key por id de acción pendiente, no por marca de tiempo.** Durante el
    desarrollo, varias pruebas fallaban de forma intermitente: dos toques seguidos
    dentro de la misma prueba podían compartir el mismo microsegundo de
    `ahora.timestamp()`, y `enqueue_outbox` descarta un mensaje con clave de
    deduplicación repetida (`on conflict do nothing`) -- el mensaje del toque siguiente
    se perdía en silencio. Las claves nuevas de T2 (`_encolar_menu_tarea`,
    `_encolar_vista_previa_menu`, `_pedir_dato_menu_tarea`, `_pedir_eleccion_dependencia`)
    usan el id de la `pending_action` recién creada (siempre distinto) en vez de la
    marca de tiempo. Es la misma clase de fragilidad que ya había señalado la revisión
    de T1 sobre `agente.py:420-421` (sugerencia, no bloqueante); acá se corrigió donde
    tocaba escribir de todos modos. Las claves existentes de T1 no se tocaron -- no era
    parte del pedido de esta unidad y su patrón (una sola respuesta por turno) no
    mostró el problema en la práctica.

  Revisión del orquestador sobre T1, resuelta en esta unidad:
  - **(a) Id de tarea en mayúsculas.** `_tareas_activas_por_id` guardaba el id tal como
    lo mandaba el modelo; Postgres compara `uuid` por valor (encuentra la fila
    igual), pero el diccionario que arma esa función lo indexaba por `str(fila["id"])`,
    que psycopg siempre devuelve en minúsculas -- así que `_ofrecer_opciones` buscaba
    después con el id tal cual llegó y no coincidía nunca si venía en mayúsculas.
    `_uuid_normalizado` (nuevo) normaliza a la forma canónica en el único lugar que
    valida un id entrante, y `_ofrecer_opciones` guarda y busca con esa misma forma.
    Prueba: `test_tarea_id_en_mayusculas_coincide_al_validar`.
  - **(b) Respuesta que no se entregaba ante una falla del proveedor.**
    `_resolver_toque_opcion_modelo` construía el calendario y el proveedor (`desde_base`)
    ANTES de llamar a `agente.responder` -- que sí atrapa que falle el proveedor
    DENTRO de la conversación (constante `DISCULPA`) --, así que una falla en esa
    construcción se escapaba hasta `procesar_update`, que revierte toda la transacción
    (incluido el toque ya resuelto) sin dejar ninguna respuesta en la cola: la persona
    se quedaba sin nada, y el toque podía volver a dispararse en un reintento del
    webhook. Ahora ese tramo está en un `try`/`except` que registra un incidente y
    encola una disculpa. Prueba:
    `test_retomar_una_opcion_entrega_respuesta_aunque_falle_el_proveedor`.

  Abierto (no en el alcance de esta unidad, observado al reusar herramientas
  existentes): `actualizar_estado` no verifica que quien la llama sea el responsable
  de la tarea -- cualquier integrante autenticado puede mover el estado de cualquier
  tarea del espacio, tanto desde el menú como si el modelo la llamara directo. El menú
  sólo ofrece el botón a quien corresponde, pero la herramienta en sí no lo exige; es
  una brecha preexistente (de antes de T1), no introducida acá, y tocarla es un cambio
  de autoridad que excede el pedido de esta unidad.

  RED (antes de implementar, `tests/test_menu_tarea.py` contra el código sin el menú):
  `.venv/Scripts/python.exe -m pytest -q tests/test_menu_tarea.py` ->
  `21 failed` (todas por el motivo esperado: atributos que todavía no existían en
  `pendientes`/`menu_tarea`, o `psycopg.errors` por columnas/opciones que el código
  viejo no reconocía).

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_menu_tarea.py` -> `21 passed`.
  - `.venv/Scripts/python.exe -m pytest -q tests/test_menu_tarea.py tests/test_opciones_modelo.py tests/banco`
    -> `190 passed, 99 deselected`.
  - `.venv/Scripts/python.exe -m pytest -q` (suite completa) -> `755 passed, 99 deselected`
    (línea base 734 + 21 pruebas nuevas de T2), reproducido dos veces en soledad
    (170.74s y 220.11s). Una corrida intermedia, lanzada por error en paralelo con otra
    sobre la misma base de pruebas, mostró una sola falla ajena
    (`test_task_intake.py::test_migration_reconciles_legacy_and_guarded_rollback_restores_it`,
    `psycopg.errors.InternalError_: tuple concurrently updated`) -- contención de dos
    sesiones de pytest corriendo a la vez, no una regresión; no se repitió en ninguna de
    las corridas en soledad.
- 2026-09-25: **T2b cerrada.** Ruta: delegada, un escritor (disparador de mapeo: 3+
  archivos de código -- `herramientas.py`, `gateway.py`, dos archivos de prueba
  existentes con datos que dependían del hueco -- más dos archivos de prueba nuevos).

  Archivos:
  - `src/prisma/herramientas.py`: chequeo de autoridad por tarea en `_preparar_
    actualizar_estado`/`_actualizar_estado`, `_preparar_registrar_bloqueo`/
    `_registrar_bloqueo` y `_preparar_adjuntar_evidencia`/`_adjuntar_evidencia` --
    duplicado en `preparar` y en el handler, mismo patrón que `_resolver_bloqueo`/
    `_aprobar_tarea`. Ninguna herramienta cambió su `accion` ni ganó
    `valida_en_handler`: las tres ya estaban en el conjunto de permiso por omisión de
    `autoridad.verificar` (`"actualizar_estado", "registrar_bloqueo",
    "adjuntar_evidencia"`), y esa verificación genérica de rol sigue corriendo antes
    -- el chequeo nuevo es una autoridad adicional, por tarea, no un reemplazo; una
    regla explícita de permiso del pack (`permission`) sigue pudiendo ampliar el nivel
    de rol como hasta ahora.
  - `src/prisma/gateway.py`: `_ejecutar_accion_menu` corre `H.ejecutar` dentro de un
    punto de retorno (`cur.connection.transaction(force_rollback=False)`, mismo
    patrón que `agente._ejecutar_una`) y atrapa `Denegado` respondiendo con el texto
    humano de la excepción; `_mensaje_resultado_menu` deja de colapsar cualquier
    resultado no reconocido en "No se aplicó ningún cambio." -- ahora exige `falta` o
    `error` y levanta `AssertionError` si no los encuentra (el `except Exception` de
    quien llama lo convierte en incidente + disculpa genérica, nunca en un mensaje
    engañoso).
  - `tests/test_autoridad_tarea.py` (nuevo, 14 pruebas): rechazo por tarea ajena,
    aprobador incluido, para las tres herramientas; que el responsable sí puede;
    consistencia con `menu_tarea.calcular_menu` (lo que el menú ofrece, la
    herramienta lo permite; lo que no ofrece, la herramienta lo rechaza); que la
    llamada del modelo a una tarea ajena no llega a armar ninguna vista previa
    (`pending_action`).
  - `tests/test_menu_tarea.py` (3 pruebas nuevas, revisión del orquestador sobre
    `0814fa3`): `_ejecutar_accion_menu` no rompe la respuesta ante un `Denegado`;
    recupera de un rechazo genuino de la base (ciclo de dependencias) sin dejar la
    transacción abortada; `_mensaje_resultado_menu` no dice "no se aplicó" para un
    resultado que no reconoce.
  - `tests/test_veracidad.py` y `tests/test_task_drafts.py`: dos pruebas existentes
    adaptadas -- ver "Pruebas adaptadas" abajo.

  Decisiones (citas de `nucleo/`):
  - **`actualizar_estado`/`registrar_bloqueo`: sólo el responsable, sin ampliar al
    aprobador.** El enunciado dejaba abierto si el aprobador/autoridad puede mover
    ciertos estados (p. ej. "volver de revisión"). `nucleo/constitucion.md` §3: "la
    persona responsable informa hechos como inicio, bloqueo, resolución y entrega en
    lenguaje natural"; los referentes "aceptan las tareas... y luego aprueban o
    rechazan el trabajo entregado. **No persiguen avances ni administran estados
    intermedios**". `nucleo/mecanica-pm.md` §3 no describe ninguna transición de
    vuelta desde `en_revision` que no sea `aprobar_tarea` (que ya verifica su propia
    autoridad) -- no hay ninguna transición del núcleo que un aprobador necesite y
    `actualizar_estado` sea el único camino para ella. Coincide con el menú ya
    aceptado en T2 (`test_menu_aprobador_en_revision`, `test_menu_aprobador_
    otro_estado`): el aprobador nunca ve un botón que cambie el estado, sólo
    "Aprobar". `registrar_bloqueo` sigue la misma cita de §3 ("bloqueo" está en la
    misma lista de hechos que informa el responsable) y el menú tampoco le ofrece
    "Informar un bloqueo" al aprobador.
  - **`adjuntar_evidencia`: responsable O aprobador.** A diferencia de las otras dos,
    `nucleo/mecanica-pm.md` §6 lista explícitamente "confirmación del referente"
    entre la evidencia que Prisma solicita -- el aprobador de la tarea
    (`autoridad.puede_aprobar_tarea`, un solo nivel: a un integrante lo aprueba su
    referente) también puede adjuntarla, no sólo el responsable. El menú (T2) todavía
    no le ofrece un botón de "Adjuntar evidencia" al aprobador (sólo "Ver detalle y
    evidencia" + "Aprobar" en `en_revision`), pero eso es alcance de un futuro ajuste
    del menú, no de esta herramienta: "ofrecer no autoriza" corre en los dos
    sentidos -- que el menú no ofrezca un botón no puede ser lo único que impida una
    acción que la herramienta sí permite por texto libre.
  - **No se tocó `cancelada`.** `mecánica-pm.md` §3 dice que `cancelada` "requiere
    razón y autoridad", sin precisar si esa autoridad es la del responsable o una
    superior -- el hueco verificado por el orquestador era sobre tareas ajenas, no
    sobre quién cancela la propia. Se deja con la misma regla que el resto de
    `actualizar_estado` (sólo el responsable) por consistencia interna, sin resolver
    la pregunta de si una autoridad superior debería poder cancelar una tarea que no
    es suya -- **PENDIENTE**, no se inventa una respuesta sin decisión explícita.
  - **`_ejecutar_accion_menu`: `Denegado` y punto de retorno.** Verificado por
    lectura de código (`gateway._resolver_toque_menu_tarea`, `_resolver_toque_dato_
    menu_tarea`, `_resumir_dato_menu_tarea`): las tres funciones que llaman a
    `_ejecutar_accion_menu` ya envuelven esa llamada en `try`/`except Denegado`/
    `except Exception`, así que hoy un `Denegado` que se escape de
    `_ejecutar_accion_menu` sigue llegando a la persona con su mensaje -- por esa
    redundancia, no hubo forma de escribir un caso de punta a punta (HTTP) que
    mostrara la diferencia sin forzar una carrera artificial. La prueba nueva
    (`test_ejecutar_accion_menu_deniega_sin_romper_la_respuesta`) llama a
    `_ejecutar_accion_menu` directo, sin pasar por esas tres funciones, para probar
    que la función es correcta también por sí sola -- que es exactamente lo que pidió
    la revisión, y protege contra una futura acción del menú que no pase por uno de
    esos tres caminos.
  - **`_ejecutar_accion_menu`: el punto de retorno sí es necesario, pero por un
    camino distinto al que parecía.** Se verificó por lectura de `herramientas.
    ejecutar`: como `_ejecutar_accion_menu` nunca pasa `ya_confirmada`, y las cinco
    herramientas que ofrece el menú (`actualizar_estado`, `registrar_bloqueo`,
    `adjuntar_evidencia`, `aprobar_tarea`, `crear_dependencia`) declaran `preparar`,
    `ejecutar()` corta siempre en `NecesitaConfirmacion` antes de tocar el handler --
    el `except psycopg.errors.RaiseException` de `_ejecutar_accion_menu` era código
    muerto en la práctica (el disparador de ciclo vive en el `insert` del handler,
    nunca alcanzable sin confirmar). Se mantiene igual el resguardo -- correcto por
    diseño, igual que `agente._ejecutar_una`, y necesario en cuanto alguna vez se
    confirme por este camino -- y la prueba nueva
    (`test_ejecutar_accion_menu_recupera_de_un_rechazo_de_la_base`) fuerza
    `ya_confirmada=True` por monkeypatch para ejercitar el rechazo genuino del
    disparador de la base (`trg_evitar_ciclo_dependencia`) y probar la recuperación
    real, no una simulada.
  - **`_mensaje_resultado_menu`: por qué `AssertionError` y no un texto genérico.**
    Mismo análisis: como el handler nunca se alcanza sin confirmar, todo lo que
    `_ejecutar_accion_menu` recibe sin excepción es el rechazo de negocio de
    `preparar` (siempre con `falta` o `error`) -- nunca el resultado de un handler
    que aplicó algo. En vez de asumir "no se aplicó ningún cambio" para lo que no se
    reconoce (que sería silenciosamente incorrecto si alguna vez deja de ser cierto),
    se levanta y el `except Exception` de quien llama ya sabe convertirlo en
    incidente + disculpa genérica -- ruidoso en vez de engañoso.

  Pruebas adaptadas (dependían del hueco, no de una aserción débil):
  - `tests/test_veracidad.py::_tarea`: creaba la tarea bajo `admin(conn)` resolviendo
    el responsable por la vista `integrante` (`select membership_id from integrante
    where nombre = 'Marcos Tarquini'`). Esa vista filtra por
    `current_setting('prisma.workspace_id', true)` (`db/esquema.sql`), que sólo fija
    `db.espacio` -- bajo `admin` queda sin definir y la vista no devuelve filas, así
    que la subconsulta resolvía en `null` y la tarea quedaba **sin responsable real**,
    invisible porque nada lo verificaba antes. Con el chequeo nuevo,
    `test_no_anuncia_como_hecho_lo_que_quedo_esperando_confirmacion` empezó a fallar
    -- no por una regresión, sino porque `Denegado` (autoridad) reemplazó a
    `NecesitaConfirmacion` (que sí alimenta la lista `confirmaciones` que protege esa
    prueba) y el resultado visible pasó a construirse por el camino de
    `with_no_effect_status` en vez de descartarse entero. Corregido resolviendo el
    `membership_id` por `membership`/`app_user` directo (mismo patrón que
    `test_bloqueos.py`/`test_dependencias.py`), sin depender de `prisma.workspace_id`.
  - `tests/test_task_drafts.py::test_prisma_app_no_puede_borrar_task_y_evento_
    autorizado_sigue_operando`: la tarea la crea `_crear_preview` con responsable
    "Nahuel Gimenez" (default de `_args`); el test usaba a "Marcos Tarquini" (quien
    sólo confirmó el borrador) para el `actualizar_estado` final, que no prueba
    autoridad sobre la tarea -- prueba que la conexión sigue operando después del
    intento de `delete` rechazado por RLS. Corregido usando a Nahuel (el responsable
    real); la aserción no cambió.

  RED (antes de implementar, con el código de `herramientas.py`/`gateway.py`
  apartado temporalmente por `git stash push -- src/prisma/gateway.py src/prisma/
  herramientas.py`, los archivos de prueba ya escritos):
  `.venv/Scripts/python.exe -m pytest -q tests/test_autoridad_tarea.py
  tests/test_menu_tarea.py` -> `12 failed, 26 passed` -- las 12 fallas son
  exactamente las nueve de autoridad (aceptaba lo que debía rechazar) más las tres
  de la revisión del orquestador, incluida una reproducción real de
  `psycopg.errors.InFailedSqlTransaction` en la prueba del punto de retorno (no
  simulada: el disparador de la base la generó de verdad). `git stash pop` restauró
  la implementación antes de seguir.

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_autoridad_tarea.py
    tests/test_menu_tarea.py` -> `38 passed`.
  - `.venv/Scripts/python.exe -m pytest -q tests/test_bloqueos.py
    tests/test_dependencias.py tests/test_botones.py
    tests/test_vista_previa_confirmacion.py tests/test_agente.py
    tests/test_aclaracion_botones.py tests/test_opciones_modelo.py
    tests/test_modificar.py tests/test_task_intake.py
    tests/test_respuestas_nombran_tarea.py tests/test_veracidad.py
    tests/test_menu_tarea.py tests/test_autoridad_tarea.py tests/test_task_drafts.py
    tests/test_resolucion_referencias.py tests/test_pendientes.py tests/test_salida.py
    tests/test_personas.py tests/test_memoria.py` -> `383 passed` (barrido de
    regresión sobre todo lo que llama a las tres herramientas o a
    `_ejecutar_accion_menu`).
  - `.venv/Scripts/python.exe -m pytest -q` (suite completa) -> `772 passed,
    99 deselected` (línea base 755 + 17 pruebas nuevas de T2b: 14 en
    `test_autoridad_tarea.py` + 3 en `test_menu_tarea.py`).

  Abierto: `cancelada` no se revisó (ver decisión arriba, **PENDIENTE**); el menú
  (T2) todavía no ofrece "Adjuntar evidencia" al aprobador aunque la herramienta ya
  lo permite -- ajuste de UX para una unidad futura, no un hueco de autoridad.
- 2026-09-25: **T2b extendida (dos correcciones del usuario, antes de commitear).**
  Ruta: delegada, un escritor (mismo disparador que el resto de T2b).

  **Decisión del usuario (1): un error nunca pasa en silencio.** Todo error tiene
  que quedar registrado como incidente Y comunicado a la persona. Se pidió
  reemplazar el `AssertionError` de `_mensaje_resultado_menu` (T2b original, punto
  3) por incidente + aviso neutro, y una regla general para todo punto de entrada
  que procesa un mensaje o un toque: excepción inesperada -> (a) revertir la
  transacción que falló, (b) registrar un incidente en una transacción nueva
  (sanitizado, sin texto de mensajes, acotado al espacio), (c) avisar con un texto
  neutro cuando se puede identificar a quien escribió (chat y membresía), sin
  filtrar detalle técnico. Evidencia citada: en la sesión real por Telegram un
  `UndefinedColumn` hacía que Prisma saltara mensajes sin respuesta ni incidente.

  **Decisión del usuario (2, corrección sobre la anterior): el incidente tiene que
  hacer encontrable la causa.** No alcanza con un resumen sanitizado: cada
  incidente de la red general (y el del menú) tiene que llevar una referencia a lo
  que lo originó (`inbound_message` o, para un toque, `pending_action`/callback),
  fecha y hora, la persona (`app_user_id`), el chat, la etapa donde falló (nombrada,
  no texto libre) y el error técnico completo en el campo administrativo
  (`referencia_cruda`) -- nunca el texto del mensaje copiado adentro: la referencia
  apunta a `inbound_message`, que ya tiene su propia retención por cliente
  (`docs/ROADMAP.md`). Se pidió una migración + rollback en `db/migrations/` +
  (la ubicación exacta se verificó contra el repo, ver más abajo), actualizar
  `db/esquema.sql`, y `python -m prisma incidentes` (`cli.py`).

  **Verificación contra el repo antes de escribir la migración (el usuario dijo
  `db/migrations/rollback/`; no existe esa carpeta).** Los rollbacks ya
  establecidos en este repo viven en `db/rollbacks/<mismo nombre>.sql`, hermano de
  `db/migrations/`, no anidado adentro -- confirmado por `tests/test_task_intake.py`
  (`_migraciones_posteriores_a`, `test_los_rollbacks_devuelven_la_base_al_estado_
  anterior`, `test_migration_clean_schema_parity_and_guarded_rollback`) y por los
  diez pares `0001`..`0010` ya existentes. Se siguió la convención real del repo
  (`db/rollbacks/0011_incident_trazabilidad.sql`), no la ruta tal como la escribió
  el usuario.

  Archivos:
  - `db/esquema.sql`: `incident` gana `etapa text`, `referencia_tipo text`,
    `referencia_id uuid` (mismo patrón polimórfico que `audit_log.sujeto_tipo`/
    `sujeto_id`, sin clave foránea), `chat_id bigint`, `app_user_id uuid references
    app_user(id) on delete set null`. `notificado_en` ya existía sin usar
    (`docs/capacidades.md`, promesa sin cumplir) -- esta unidad es la primera que lo
    llena.
  - `db/migrations/0011_incident_trazabilidad.sql` / `db/rollbacks/
    0011_incident_trazabilidad.sql` (nuevos): agregan/revierten las cinco columnas.
    Sin cambio de `grant`: `prisma_app` ya tenía `insert` sobre toda la fila desde
    el esquema base.
  - `src/prisma/gateway.py`:
    - Constantes nuevas: `ETAPA_TURNO_TEXTO`, `ETAPA_TOQUE_BOTON`,
      `ETAPA_ACTIVACION`, `ETAPA_ACCION_MENU` (puntos de entrada de la red general,
      no cada paso interno -- los incidentes puntuales que ya existían
      `_routing_incident`/`agente._incidente` no se tocaron); `REFERENCIA_INBOUND_
      MESSAGE`, `REFERENCIA_PENDING_ACTION`.
    - `_registrar_incidente` (ya existía desde el punto 1) gana los parámetros
      nuevos.
    - `reportar_incidente_no_manejado` reescrita: primero intenta avisar (en su
      propia transacción), después registra el incidente una sola vez con el
      resultado del aviso ya resuelto (`notificado_en` o una nota en el resumen) --
      no dos filas por fallo, ver decisión de diseño abajo.
    - `_mensaje_resultado_menu`: el `AssertionError` (T2b original) se reemplaza por
      `_registrar_incidente` + `NOTICIA_NEUTRA_INCIDENTE`, con `etapa=
      ETAPA_ACCION_MENU` y la referencia a la `pending_action`, cuando se conoce.
    - `procesar_update`: la rama de mensaje se parte en dos fases (ver decisión de
      diseño); la rama de `/start` y la de toque quedan envueltas con el mismo
      resguardo.
    - `_toque`: envuelta entera (después de las guardas tempranas) en un
      `try`/`except` que anota `pending_action_id` en la excepción y vuelve a
      levantarla -- `procesar_update` sigue siendo quien revierte/confirma (ver
      decisión de diseño sobre `conn.commit()`). Búsqueda del id real corregida (ver
      "defecto encontrado" abajo). `_resolver_toque_menu_tarea`/`_resolver_toque_
      dato_menu_tarea`/`_ejecutar_accion_menu`/`_mensaje_resultado_menu` ganan un
      parámetro `pending_action_id`/`referencia_id` opcional, hilado desde `_toque`
      (toque) o `modificacion.pending_action_id` (texto libre tras "Ninguna, lo
      escribo" del menú).
  - `src/prisma/local.py`: `Escucha.recibir` importa las constantes de etapa y las
    pasa a `reportar_incidente_no_manejado` (toque vs. turno, según el update).
  - `src/prisma/cli.py`: `python -m prisma incidentes` imprime `etapa`,
    `referencia_tipo=referencia_id`, `chat_id` y si se avisó -- nunca un secreto.
  - `tests/test_capacidades.py`: se saca `"notificado_en"` de `PROMESAS_SIN_CUMPLIR`
    (ya se implementa); las cinco columnas nuevas quedan referenciadas en
    `gateway.py`, así que `test_no_hay_esquema_nuevo_sin_uso_ni_declarado` las
    reconoce sin agregarlas a la lista.
  - `tests/test_menu_tarea.py`: las tres pruebas del punto 1 (revisión del
    orquestador) se actualizan para verificar `etapa`/`referencia_tipo`/
    `referencia_id`/`notificado_en`, no sólo que no levanten. `test_mensaje_
    resultado_menu_...` gana una verificación de `etapa`.
  - `tests/test_task_intake.py`: `test_objective_callback_failure_rolls_back_
    before_outer_commit` (ya adaptada en el punto 1) se extiende para confirmar
    `incident` +1 antes/después.

  Decisiones de diseño:
  - **Notificar antes de registrar, no una fila y después una actualización.**
    `prisma_app` sólo tiene `insert` sobre `incident` (`grant insert on ... incident
    ... to prisma_app`, sin `update`) -- mismo espíritu que `task_state_event`
    append-only. Grabar el incidente primero y actualizar `notificado_en` después
    habría necesitado ese `update`, ampliando un privilegio que el esquema niega a
    propósito. Se intenta avisar primero (transacción propia, con su propio
    `try`/`except`) y se registra el incidente una sola vez al final, con el
    resultado del aviso ya resuelto -- si el aviso falla, una nota se agrega al
    `resumen_sanitizado` y `notificado_en` queda `null`; nunca dos filas para un
    mismo fallo, y "no reintentar" queda garantizado por construcción (una sola
    pasada, sin bucle).
  - **`_toque` no puede revertir/confirmar por sí sola.** Se intentó primero que
    `_toque` manejara su propio `conn.rollback()`/`reportar_incidente_no_manejado`
    internamente (para tener a `resuelta` a mano). Verificado con una prueba directa
    contra Postgres: `conn.commit()`/`conn.rollback()` explícitos dentro de un
    `with conn.transaction():` todavía abierto levantan `psycopg.errors.
    ProgrammingError: Explicit commit() forbidden within a Transaction context`, y
    un `return` temprano desde adentro de ese `with` nunca llega a un commit puesto
    después (salta directo afuera de la función). Por eso el commit/rollback sigue
    viviendo en `procesar_update`, exactamente como antes de esta unidad; `_toque`
    sólo anota `e.pending_action_id` en la excepción, sin revertir ni confirmar
    nada, y vuelve a levantarla.
  - **Fase 1 (recibir) y fase 2 (interpretar) del turno de texto, separadas y cada
    una con su propio commit.** Antes de esta corrección, `inbound_message` se
    revertía junto con todo lo demás si `_turno` fallaba -- exactamente lo que la
    corrección de trazabilidad pide evitar: sin esa fila, el incidente no tiene a
    qué apuntar. Ahora identificar a quien escribe, insertar `inbound_message` y
    auditar "mensaje_recibido" se confirman aparte, antes de intentar interpretar el
    texto; si la interpretación (`_turno`/`handle_active_text`) falla, sólo esa
    parte se revierte -- el recibo del mensaje sobrevive.
  - **Defecto encontrado al escribir la prueba del toque: `Resuelta.pending_
    action_id` nunca se completa.** `pendientes.resolver()` construye `Resuelta(...)`
    sin pasar `pending_action_id` en ninguna de sus tres ramas -- el campo existe en
    el dataclass pero queda siempre en su default (`None`). Corregido sin tocar
    `pendientes.py`: `_toque` busca el id aparte con `P.pending_action_id_de(cur,
    token)` (ya existía, la usa T4 para "Ninguna, lo escribo") justo después de
    resolver, porque la fila de `pending_action_option` sigue existiendo después de
    resolverse -- sólo cambia el estado de la acción, no se borra la opción.
  - **Etapas nombradas, con alcance acotado a esta unidad.** El enunciado nombraba
    como ejemplo "enrutar, resolver referencias, armar la vista previa, el turno del
    modelo, correr una herramienta, mandar la respuesta". Se agregaron sólo las
    cuatro etapas que esta unidad realmente instrumenta (los puntos de entrada de la
    red general y el incidente del menú), sin reinstrumentar cada incidente puntual
    que ya existía (`_routing_incident`, `_incidente_jev_no_configurado`,
    `agente._incidente`) -- seguirían sin `etapa` ni referencia estructurada; ese
    trabajo queda fuera del alcance de esta corrección y no se inventó.

  RED (`git stash push -- src/prisma/gateway.py src/prisma/local.py`, primer envío
  del punto 1 -- el mecanismo de incidente en sí):
  `.venv/Scripts/python.exe -m pytest -q tests/test_autoridad_tarea.py
  tests/test_menu_tarea.py` -> `12 failed, 26 passed` (incluye una reproducción real
  de `psycopg.errors.InFailedSqlTransaction`, no simulada).

  RED (extensión de trazabilidad, `git stash push -- src/prisma/gateway.py
  src/prisma/local.py src/prisma/cli.py`, con `db/esquema.sql` ya con las columnas
  nuevas):
  `.venv/Scripts/python.exe -m pytest -q tests/test_menu_tarea.py
  tests/test_task_intake.py::test_objective_callback_failure_rolls_back_before_
  outer_commit tests/test_capacidades.py` -> `8 failed, 23 passed` -- incluye
  `test_no_hay_esquema_nuevo_sin_uso_ni_declarado` señalando las cinco columnas
  nuevas como sin uso (correcto: el código que las llena todavía no existía) y el
  toque de intake volviendo a dar 500 (el re-levantamiento viejo). `git stash pop`
  restauró la implementación en los dos casos antes de seguir.

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_menu_tarea.py
    tests/test_task_intake.py::test_objective_callback_failure_rolls_back_before_
    outer_commit tests/test_capacidades.py` -> `31 passed`.
  - `.venv/Scripts/python.exe -m pytest -q tests/test_autoridad_tarea.py
    tests/test_menu_tarea.py tests/test_bloqueos.py tests/test_dependencias.py
    tests/test_botones.py tests/test_vista_previa_confirmacion.py tests/test_agente.py
    tests/test_aclaracion_botones.py tests/test_opciones_modelo.py
    tests/test_modificar.py tests/test_task_intake.py
    tests/test_respuestas_nombran_tarea.py tests/test_veracidad.py
    tests/test_task_drafts.py tests/test_resolucion_referencias.py
    tests/test_pendientes.py tests/test_salida.py tests/test_personas.py
    tests/test_memoria.py tests/test_smoke_runtime.py tests/test_capacidades.py`
    -> `397 passed` (barrido de regresión).
  - `.venv/Scripts/python.exe -m pytest -q` (suite completa) -> `775 passed,
    99 deselected`.

  Abierto: los pares `0001`..`0002` gated por `PRISMA_TEST_DB_URL` (`test_los_
  rollbacks_devuelven_la_base_al_estado_anterior`,
  `test_migration_reconciles_legacy_and_guarded_rollback_restores_it`, y afines) no
  corrieron -- esa variable no está configurada en este entorno; se verificó en su
  lugar con `test_capacidades.py` (que sí corrió, sin ese servidor) que las columnas
  nuevas quedan declaradas y usadas, y por lectura que `0011` sigue exactamente el
  formato de `0008`/`0009`/`0010` (`\encoding UTF8`, sentinela UTF-8, precondición,
  `begin`/`commit`) y que su rollback sólo suelta columnas que nada más referencia
  (sin función que reconstruir, a diferencia de `0010`). No se ejercitó
  migración-arriba/rollback-abajo contra una base real: queda como
  **PENDIENTE** de una sesión con `PRISMA_TEST_DB_URL` configurado, igual que ya
  está pendiente para `0001`..`0010`. `docs/capacidades.md` no se actualizó (fuera
  del alcance autorizado para esta unidad, "no tocar docs/"): sigue mencionando
  `notificado_en` como promesa sin cumplir aunque `tests/test_capacidades.py` ya no
  lo liste así -- desalineación conocida, no silenciada.
- 2026-09-25 (orquestador): **T2b commiteada** (`fd4e2a6`; migración `0011` aplicada también en
  la base local, con copia previa). Revisión RDD de riesgo alto con cuatro lentes, aprobada y
  reconocida (`review-9ac0b4b8afec17ee`), con consentimiento previo del usuario para este
  cambio. Observaciones no bloqueantes: **`gateway.py` ~1905-1925 (resiliencia y
  fiabilidad): `notificado_en` se marca aunque la persona no se haya identificado y no se le
  haya avisado; contradice "nunca mentir", va primero en la próxima sesión**;
  `local.py:110-117` (el `except` del bucle de escucha puede volver a levantar si falla el
  registro del incidente); `gateway.py:1826-1832` (incidente de enrutamiento duplicado);
  `gateway.py:1117-1148` (efecto lateral en `_mensaje_resultado_menu`); `gateway.py:156-161`
  (cobertura de las redes nuevas); migración `0011` no ejercitada contra una base de ensayo
  (`PRISMA_TEST_DB_URL` sin configurar); `cli.py:367-369` y `tests/test_menu_tarea.py:959-960`
  (código muerto). Pendiente de T2b: autoridad para `cancelada`.
- 2026-09-25 (orquestador): **`notificado_en` falso corregido** (`b4e5973`). Cambio encontrado
  sin commitear tras el cierre de sesión, de origen desconocido; verificado antes de aceptarlo.
  `reportar_incidente_no_manejado` sólo completa `notificado_en` si el aviso se encoló y la
  transacción se confirmó. Prueba nueva:
  `test_reportar_incidente_no_manejado_no_marca_avisado_si_no_identifica`.
  - RED (con `gateway.py` de `ea931ee`): `1 failed` (`notificado_en` con fecha sin aviso).
  - GREEN: `tests/test_menu_tarea.py` -> `28 passed`; suite completa -> `776 passed,
    99 deselected` (180 s).
  - RDD: `gentle-ai review assess --base-ref ea931ee --committed-only` -> riesgo `medium`,
    `review_due: false` (`under_budget`, 39 líneas); queda pendiente en el tramo, frontera de
    revisión sigue en `ea931ee`.
- 2026-09-25: **Decisiones del usuario para T3.**
  1. **El servidor garantiza la lista como botones**, no el modelo: cuando en un turno el
     modelo usa `consultar_tareas` y responde, el servidor agrega un botón por tarea y
     tocarlo abre el menú de T2 (ADR 0007 puntos 3 y 4). No depende de que el modelo
     obedezca la regla del contexto. Costo aceptado: también lleva botones una respuesta
     que sólo daba un conteo.
  2. **Más de 4 tareas: páginas con "Ver más".** 4 tareas en el orden de la consulta,
     más "Ver más" y la salida; "Ver más" trae las 4 siguientes sin pasar por el modelo.
     Se descartó agrupar por estado (un toque más siempre, y un grupo grande vuelve a
     necesitar páginas).
  Ruta: delegada, un escritor (`agente.py`, `gateway.py`, `contexto.py`, pruebas).
- 2026-09-25: **T3 cerrada.** Ruta: delegada, un escritor (disparador de mapeo: 4
  archivos de código + pruebas).

  Archivos:
  - `src/prisma/agente.py`: `_ejecutar_una` gana un acumulador más,
    `ultima_lista_tareas` (mismo patrón mutable que `acciones`/`confirmaciones`/
    `elecciones`) -- se sobrescribe sólo cuando una llamada a `consultar_tareas`
    devuelve filas, así que si hay varias en el turno gana la ÚLTIMA que trajo
    algo, no la última llamada a secas. `responder`, al cerrar con una respuesta
    visible normal (nunca si el turno ya terminó con `confirmaciones`/
    `elecciones`: ese camino ya devuelve antes), llama a
    `_encolar_respuesta_con_tareas` en vez de `_encolar_respuesta` cuando esa
    lista no está vacía. `_opciones_lista_tareas` arma hasta
    `H.MAX_OPCIONES_MODELO` botones de tarea (mismo tope y forma de valor que
    una opción de `ofrecer_opciones` con `accion: "menu"`, T1/T2) y agrega
    "Ver más" con los ids restantes cuando sobran; `_encolar_respuesta_con_tareas`
    arma la `pending_action` (sentinel compartido `SENTINEL_OPCIONES_MODELO`) y
    la encola con el MISMO texto que ya iba a mandar el modelo.
  - `src/prisma/gateway.py`: `_resolver_toque_opcion_modelo` gana un tercer tipo
    de elección, `"ver_mas"`, que despacha a la función nueva
    `_mostrar_mas_tareas` sin retomar la conversación (ni con el modelo, ni con
    Jev, ni con `route_intent`). `_mostrar_mas_tareas` revalida los ids
    restantes contra PostgreSQL bajo el cursor con RLS del toque, reusando
    `herramientas._tareas_activas_por_id` (T1) -- la misma función que ya valida
    las tareas que ofrece el modelo --, arma la página siguiente (hasta 4 +
    "Ver más" si sobra más + la salida) y la encola con el mismo sentinel.
  - `src/prisma/pendientes.py`: `ETIQUETA_VER_MAS = "Ver más"`, al lado de
    `ETIQUETA_SALIR_OPCIONES`, por el mismo motivo (que `agente.py`, que arma la
    primera página, y `gateway.py`, que arma las siguientes, muestren la misma
    etiqueta).
  - `src/prisma/contexto.py`: la regla del `PREAMBULO` sobre listar tareas se
    reescribe -- ya no le pide al modelo llamar a `ofrecer_opciones` para que
    una lista de `consultar_tareas` salga como botones (eso ahora lo garantiza
    el servidor); sigue pidiéndole usar `ofrecer_opciones` para el resto de las
    elecciones concretas y seguir sin preguntar en texto abierto. La prueba
    `test_opciones_modelo.py::test_reglas_del_contexto_piden_ofrecer_opciones`
    no se tocó: sólo comprueba que "ofrecer_opciones" siga apareciendo en el
    `PREAMBULO` y la regla de no presentar una suposición como un hecho, ninguna
    de las dos afectada por este reemplazo.
  - `tests/test_lista_botones.py` (nuevo, 7 pruebas).

  Decisiones de diseño:
  - **Reuso, no un mecanismo paralelo.** La lista se arma como una
    `pending_action` más del sentinel de T1 (`SENTINEL_OPCIONES_MODELO`), con
    opciones de tarea `accion: "menu"` -- el mismo mecanismo que T2 ya usa para
    abrir el menú al tocar una opción de `ofrecer_opciones`. No hizo falta un
    sentinel nuevo ni una segunda función de validación de tareas: "Ver más" (el
    único elemento nuevo) es sólo un tercer tipo de elección (`"ver_mas"`) sobre
    el mismo sentinel, resuelto en el mismo lugar
    (`gateway._resolver_toque_opcion_modelo`) que ya resolvía `"salida"` y
    `"tarea"`.
  - **`calcular_menu` sí soporta tareas cerradas -- verificado, no supuesto.**
    El enunciado pedía comprobar si el menú de T2 soporta `terminada`/
    `cancelada` antes de decidir si hay que excluirlas de los botones.
    `menu_tarea.calcular_menu` (relación "responsable") ofrece "Ver detalle" para
    cualquier estado, incluidos `terminada`/`cancelada` -- el comentario del
    código ya lo decía ("terminada/cancelada: sólo Ver detalle, ya agregado
    arriba") y las otras dos relaciones (aprobador, otra persona) también caen
    siempre a "Ver detalle" cuando no hay una acción más específica. Por eso la
    PRIMERA página (las filas que acaba de devolver `consultar_tareas`, en la
    misma transacción) no filtra por estado: si el modelo pidió expresamente
    tareas terminadas, cada una igual sale como botón y tocarla abre un menú
    válido (sólo "Ver detalle"). Costo aceptado explícito del enunciado: una
    respuesta que sólo dio un conteo también lleva estos botones.
  - **"Ver más" revalida existencia, no estado -- corregido tras revisión del
    orquestador.** La primera implementación reusaba
    `herramientas._tareas_activas_por_id` (T1) en `_mostrar_mas_tareas`, que
    sólo devuelve tareas `not in ('terminada', 'cancelada')`, con la idea de
    que la asimetría con la primera página era intencional (la primera se arma
    con datos recién leídos en la misma transacción; "Ver más" puede tocarse
    horas después, `VIGENCIA_PENDIENTE` 8 horas, así que ahí sí hacía falta
    revalidar). La revisión encontró el defecto: la PRIMERA página también
    puede traer tareas terminadas -- `consultar_tareas` acepta
    `estado="terminada"` y no filtra nada --, así que alguien que pide sus
    tareas terminadas, ve más de cuatro y toca "Ver más" se encontraba con
    "Esas tareas ya no están disponibles", un mensaje falso: esas tareas nunca
    dejaron de existir, sólo están cerradas, que es exactamente lo que la
    persona pidió ver. La página siguiente tiene que ser consistente con la
    primera, no más estricta.

    Regla corregida: `_mostrar_mas_tareas` revalida con la función nueva
    `herramientas._tareas_existentes_por_id` -- existencia y espacio (mismo id
    normalizado, mismo `workspace_id = %s` bajo el cursor con RLS del toque),
    sin filtrar por estado, devolviendo el título ACTUAL. Sólo desaparece un
    id que no es un UUID válido, que no existe, o que es de otro espacio; una
    tarea que se cierra entre que se listó y que se tocó "Ver más" se queda en
    la lista -- tocarla abre el menú, que sí recalcula por el estado ACTUAL
    (cerrada -> sólo "Ver detalle", `menu_tarea.calcular_menu`). El chequeo de
    estado vive una sola vez, en el menú, no duplicado en la paginación.
    `_tareas_activas_por_id` (T1) queda sin tocar -- su regla es distinta y
    correcta para su caso: una opción que el modelo ACABA de ofrecer siempre
    tiene que seguir abierta para que "elegirla" tenga sentido, algo que no
    aplica a una lista que la persona pidió ver tal cual está.
  - **Dónde van los botones: la MISMA respuesta del modelo, no un mensaje
    aparte.** `enqueue_outbox` decide `has_buttons` por `pending_action_id`
    presente, y un mensaje con botones tiene un tope más chico
    (`BUTTON_TEXT_LIMIT`, 3900 unidades UTF-16) y NUNCA se parte en varias partes
    aunque se pida `allow_split=True` (a diferencia de `_encolar_respuesta`, que
    sí puede partir una respuesta larga). Es la misma limitación que ya aceptan
    todas las demás respuestas con botones de este proyecto (confirmación, menú,
    opciones de T1) -- ninguna usa `allow_split`--, así que adjuntar los botones
    a la respuesta del modelo no es una regla nueva, es la regla de siempre
    aplicada a un mensaje más. Se prefirió sobre un segundo mensaje separado
    porque evita dos mensajes por turno (uno con el texto, otro con los
    botones) y reusa `_encolar_respuesta_con_tareas`/`P.registrar` tal cual el
    resto del sentinel.
  - **`args={"pregunta": texto}` es inerte para esta lista.** Se guarda por
    consistencia con la forma que ya tiene `pending_action.args` para
    `SENTINEL_OPCIONES_MODELO` (T1), pero ninguna rama de una lista de tareas la
    lee: una tarea con `accion: "menu"` nunca retoma la conversación, "Ver más"
    pagina, y la salida cierra sin efecto. Sólo el camino de T1 (una opción de
    texto libre, o una tarea sin `accion: "menu"`) usa `pregunta` para reconstruir
    el contexto que ve el modelo al retomar.
  - **Dedupe key por id de la `pending_action`, no por marca de tiempo.** Mismo
    criterio que T2 (revisión del orquestador sobre T1,
    `agente.py:420-421`): `_encolar_respuesta_con_tareas` y `_mostrar_mas_tareas`
    usan `f"...:{p.id}"`, nunca `ahora.timestamp()`.
  - **Regla del contexto reescrita, no eliminada.** El modelo sigue sin poder
    preguntar en texto abierto; sólo deja de necesitar `ofrecer_opciones` para
    el caso puntual de listar tareas que ya listó con `consultar_tareas`, porque
    ese caso ahora lo garantiza el servidor sin depender de que el modelo
    obedezca.

  RED (antes de implementar -- `git stash push -- src/prisma/agente.py
  src/prisma/gateway.py src/prisma/pendientes.py src/prisma/contexto.py`, con
  `tests/test_lista_botones.py` ya escrito):
  `.venv/Scripts/python.exe -m pytest -q tests/test_lista_botones.py` ->
  `5 failed, 2 passed` -- los 2 que ya pasaban en rojo son "lista vacía no arma
  botones" y "un turno con otras opciones no agrega botones de lista": con el
  código viejo tampoco se arma ninguna `pending_action` de lista (todavía no
  existe el mecanismo), así que la aserción "no hay una segunda" se cumple por
  ausencia, no por la regla; quedaron confirmadas igual una vez implementada la
  función, ya no por la ausencia. Las 5 fallas restantes son exactamente las
  esperadas: sin la función, no se arma ninguna `pending_action` de lista
  (`TypeError: 'NoneType' object is not subscriptable` al buscarla) y
  `gateway._mostrar_mas_tareas` no existe (`AttributeError`). `git stash pop`
  restauró la implementación antes de seguir.

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_lista_botones.py` ->
    `7 passed`.
  - `.venv/Scripts/python.exe -m pytest -q tests/test_menu_tarea.py
    tests/test_opciones_modelo.py tests/test_agente.py tests/test_botones.py
    tests/test_aclaracion_botones.py tests/test_autoridad_tarea.py
    tests/test_lista_botones.py tests/banco` -> `263 passed, 99 deselected`
    (barrido de regresión sobre todo lo que llama a las tres piezas que se
    tocaron: el sentinel de T1, el menú de T2 y el contexto).
  - `.venv/Scripts/python.exe -m pytest -q` (suite completa) -> `783 passed,
    99 deselected` (línea base 776 + 7 pruebas nuevas de T3), 181 s.

  Corrección tras revisión del orquestador (mismo día, misma unidad -- ver
  arriba, "«Ver más» revalida existencia, no estado"):

  Archivos: `src/prisma/herramientas.py` (función nueva
  `_tareas_existentes_por_id`, al lado de `_tareas_activas_por_id`),
  `src/prisma/gateway.py` (`_mostrar_mas_tareas` llama a la función nueva),
  `tests/test_lista_botones.py` (test nuevo
  `test_ver_mas_de_tareas_terminadas_no_dice_que_ya_no_estan_disponibles`;
  `test_ver_mas_descarta_una_tarea_que_se_cerro_mientras_tanto` reescrito como
  `test_ver_mas_tarea_que_se_cierra_mientras_tanto_se_queda_en_la_pagina`, que
  ahora comprueba que la tarea se QUEDA en la página y que su menú, al
  abrirse, recalcula a sólo "Ver detalle").

  RED (antes del arreglo -- reversión quirúrgica de las dos ediciones en
  `herramientas.py`/`gateway.py`, dejando el resto de T3 intacto, con los dos
  tests ya escritos/reescritos):
  `.venv/Scripts/python.exe -m pytest -q
  tests/test_lista_botones.py::test_ver_mas_de_tareas_terminadas_no_dice_que_ya_no_estan_disponibles
  tests/test_lista_botones.py::test_ver_mas_tarea_que_se_cierra_mientras_tanto_se_queda_en_la_pagina
  tests/test_lista_botones.py::test_ver_mas_nunca_muestra_una_tarea_de_otro_espacio`
  -> `2 failed, 1 passed`: el de tenencia entre espacios seguía pasando (no
  tocado por el defecto); el de tareas terminadas fallaba con
  `['Quiero consultar otra cosa'] == ['Tarea terminada 5', 'Tarea terminada 6',
  ...]` (la página volvía vacía, "ya no están disponibles"); el de "se cierra
  mientras tanto" fallaba porque "Tarea 5" ya no aparecía (`['Tarea 6', ...]
  == ['Tarea 5', 'Tarea 6', ...]`) -- exactamente el defecto reportado.

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_lista_botones.py` ->
    `8 passed`.
  - Barrido de regresión (mismo comando de arriba) -> `264 passed,
    99 deselected`.
  - Suite completa -> `784 passed, 99 deselected` (783 previos + 1 prueba
    nueva), 180 s.

  Abierto: ninguno nuevo. La brecha de `cancelada` (autoridad, T2b) y la falta
  de "Adjuntar evidencia" para el aprobador en el menú (T2) siguen igual,
  fuera del alcance de esta unidad.
- 2026-09-25 (orquestador): **T3 commiteada** (`5e47038`, en `main`). Evaluación RDD
  `--base-ref ea931ee --committed-only`: riesgo `medium`, `review_due: true`
  (`slice_budget_reached`, 916 líneas, incluye `b4e5973`). Revisión con consentimiento del
  usuario, una lente (fiabilidad), aprobada y reconocida (`review-112e1420d47dd637`,
  autoridad consumida). La frontera de revisión avanza a `5e47038`.
  Observaciones no bloqueantes:
  - **T3a (advertencia, confirmada por lectura de `salida.prepare_payload`):** un mensaje
    con botones no puede superar `BUTTON_TEXT_LIMIT` (3900 unidades UTF-16) y nunca se
    parte; `_encolar_respuesta_con_tareas` manda el texto del modelo con los botones, así
    que una respuesta de lista más larga que eso levanta `PayloadValidationError` y la
    persona recibe el aviso neutro en vez de la lista. Antes de T3 se partía. Corrección
    propuesta: si el texto excede el límite, mandarlo partido como antes y los botones en
    un mensaje corto aparte. Sin prueba todavía.
  - `gateway._mostrar_mas_tareas`: sin prueba la rama "Esas tareas ya no están
    disponibles" ni la segunda página con su propio "Ver más" (más de 8 tareas).
- 2026-09-25: **T3a cerrada.** Ruta: delegada, mismo escritor (defecto confirmado por el
  orquestador contra `salida.prepare_payload`, más las dos pruebas de cobertura
  sugeridas en la misma revisión).

  Archivos: `src/prisma/agente.py` (`_encolar_respuesta_con_tareas` reescrita;
  constante nueva `_TEXTO_BOTONES_LISTA_TAREAS`; import de `BUTTON_TEXT_LIMIT` y
  `telegram_utf16_units` desde `.salida`), `tests/test_lista_botones.py` (cuatro
  pruebas nuevas: `test_lista_con_respuesta_larga_se_parte_y_los_botones_van_aparte`,
  `test_lista_con_respuesta_corta_sigue_yendo_junto_con_los_botones`,
  `test_mostrar_mas_tareas_sin_sobrevivientes_dice_que_ya_no_estan_disponibles`,
  `test_ver_mas_de_mas_de_ocho_tareas_arma_una_tercera_pagina`; helper nuevo `_outbox`).

  Decisión (defecto 1, respuesta de lista larga):

  - **La primera corrección que se probó estaba incompleta -- lo encontró la propia
    prueba RED.** La primera versión sólo movía la decisión de "¿entra con botones?" a
    `enqueue_outbox`, pero seguía pasando el `texto` completo del modelo como `resumen`
    a `P.registrar`. `pendientes.registrar` valida ese `resumen` contra
    `BUTTON_TEXT_LIMIT` SIN excepción (línea `prepare_payload(resumen, dedupe_key="pending",
    has_buttons=True)`, incondicional) porque `resumen` es el texto que se manda junto
    con los botones de esa `pending_action` -- así que la excepción seguía saltando, sólo
    que un `P.registrar` antes de lo que se había movido. La prueba
    `test_lista_con_respuesta_larga_se_parte_y_los_botones_van_aparte`, corrida contra
    esa primera corrección, falló con el mismo `PayloadValidationError`
    (`pendientes.py:166`), lo que mostró el problema antes de darlo por cerrado.
  - **Corrección final: la decisión se toma ANTES de llamar a `registrar`, sobre `texto`
    crudo.** Si `texto` (normalizado, medido con `telegram_utf16_units` -- la misma regla
    UTF-16 de `prepare_payload`) entra en `BUTTON_TEXT_LIMIT`, `resumen` es el texto del
    modelo tal cual (comportamiento de siempre, botones en el mismo mensaje). Si no entra,
    `resumen` pasa a ser `_TEXTO_BOTONES_LISTA_TAREAS` ("Elegí una tarea:") -- un texto
    corto fijo que siempre entra --, y el texto completo del modelo sale ANTES, en un
    mensaje aparte sin botones y con `allow_split=True` (exactamente como lo mandaría
    `_encolar_respuesta`). `args={"pregunta": texto}` sigue guardando el texto completo
    pase lo que pase con `resumen`: nada de este sentinel lo lee para una lista de tareas
    (T3), pero mantiene el registro de auditoría fiel a lo que dijo el modelo.
  - **Orden determinístico por `programado_para`, no por casualidad.** `message_outbox.id`
    es un `uuid` al azar (`gen_random_uuid()`), no sirve de desempate, y
    `despachador.despachar` ordena sólo `by programado_para` (`despachador.py:299`), sin
    una columna de desempate. Las partes del texto comparten el mismo `programado_para
    = ahora` que ya usaba `_encolar_respuesta`; el mensaje de botones se programa un
    instante después (`ahora + timedelta(microseconds=1)`), así que la comparación de
    esa columna sola ya garantiza texto-antes-que-botones, sin depender del orden físico
    en que Postgres devuelva filas con el mismo valor.
  - **Dedupe keys por id de la `pending_action`, no por marca de tiempo**, en las dos
    partes nuevas (`...:{p.id}:texto`, `...:{p.id}:botones`) -- misma lección que T1/T2/T3.

  Decisión (defecto 2, cobertura sugerida): las dos pruebas nuevas sobre
  `gateway._mostrar_mas_tareas` (sin sobrevivientes; tercera página con más de ocho
  tareas) pasaron contra el código YA corregido de T3 sin tocar nada -- confirman que esas
  dos ramas, señaladas sin prueba en la revisión, ya funcionan como corresponde; no eran
  un defecto, sólo huecos de cobertura.

  RED (defecto 1 -- reversión quirúrgica de `src/prisma/agente.py` a `5e47038`, con las
  cuatro pruebas nuevas ya escritas):
  `.venv/Scripts/python.exe -m pytest -q
  tests/test_lista_botones.py::test_lista_con_respuesta_larga_se_parte_y_los_botones_van_aparte
  tests/test_lista_botones.py::test_lista_con_respuesta_corta_sigue_yendo_junto_con_los_botones
  tests/test_lista_botones.py::test_mostrar_mas_tareas_sin_sobrevivientes_dice_que_ya_no_estan_disponibles
  tests/test_lista_botones.py::test_ver_mas_de_mas_de_ocho_tareas_arma_una_tercera_pagina`
  -> `1 failed, 3 passed`: la de respuesta larga falló con
  `prisma.salida.PayloadValidationError: Un mensaje con botones no puede exceder 3900
  unidades UTF-16` (`pendientes.py:166`, dentro de `P.registrar`) -- exactamente el
  defecto reportado; las otras tres ya pasaban contra el código sin tocar, confirmando que
  sólo eran cobertura.

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_lista_botones.py` -> `12 passed`
    (8 de T3 + 4 nuevas de T3a).
  - Barrido de regresión (`tests/test_menu_tarea.py tests/test_opciones_modelo.py
    tests/test_agente.py tests/test_botones.py tests/test_aclaracion_botones.py
    tests/test_autoridad_tarea.py tests/test_lista_botones.py tests/test_salida.py
    tests/banco`, con `test_salida.py` sumado por tocar `salida.py`/`BUTTON_TEXT_LIMIT`
    en el razonamiento aunque no en el código) -> `285 passed, 99 deselected`.
  - Suite completa -> `788 passed, 99 deselected` (784 previos + 4 pruebas nuevas), 183 s.

  Abierto: ninguno nuevo. Mismas brechas fuera de alcance que T3 (`cancelada` en T2b,
  "Adjuntar evidencia" del aprobador en T2).
- 2026-09-26: **Banco: corridas con el proveedor caído quedan bloqueadas.** Ruta:
  delegada, un escritor (disparador de mapeo: 5 archivos entre código y pruebas).
  Fuera de la secuencia T1-T4: hallazgo del orquestador sobre una corrida real
  (`.venv/Scripts/python.exe -m pytest -m modelo_real tests/banco --banco-n 3
  --banco-proveedor nan --banco-modelo deepseek-v4-flash`) que coincidió con el
  proveedor devolviendo 404 en cada `chat completion`.

  Problema: `gateway.procesar_update` ataja el fallo del proveedor adentro (nunca
  propaga la excepción) y responde con un mensaje sin efectos -- por
  `gateway._routing_incident` cuando falla `route_intent`, o por `agente._incidente`
  + `agente.DISCULPA` cuando falla `proveedor.responder` dentro del turno.
  `tests/banco/corrida.py::ejecutar_escenario` sólo marcaba `bloqueado` si
  `gateway.procesar_update` propagaba una excepción -- nunca pasaba con el
  proveedor caído, así que escenarios que sólo esperaban "sin herramientas / sin
  efectos" (b-0007..b-0014) quedaban `aprobado` sin que ningún modelo hubiera
  decidido nada. Contradice el invariante "no poder consultar no equivale a que no
  haya nada que hacer" y la regla del usuario de nunca fallar en silencio.

  Archivos:
  - `tests/banco/corrida.py`: `_MARCA_ENRUTAMIENTO_CAIDO` / `_MARCA_TURNO_CAIDO`
    (los prefijos estables y sin secretos de `gateway._routing_incident` y
    `agente._incidente`) y `_incidentes_de_proveedor_caido` (compara los `incident`
    del espacio antes/después de la corrida). `ejecutar_escenario` guarda
    `ids_incidentes_previos` junto con `ids_previos`, y después de armar
    `respuesta_texto` -- sólo si no quedó `bloqueado` ya por una excepción propia --
    busca un incidente nuevo que matchee alguna marca y, si lo encuentra, marca
    `bloqueado=True` con ese resumen (ya sanitizado) como `motivo_bloqueo`. La marca
    de `agente._incidente` sólo cuenta si además `agente.DISCULPA` está en
    `respuesta_texto`: esa función también se usa dentro de `_ejecutar_una` para un
    `psycopg.Error` de una sola herramienta -- un fallo de esa fila que el turno
    sigue procesando con normalidad, no "no se pudo consultar al proveedor" -- y
    ese camino nunca deja `DISCULPA` como respuesta visible.
  - `tests/banco/test_corrida.py`: dos proveedores falsos nuevos
    (`_ProveedorCaidoAlRutear`, `_ProveedorCaidoAlResponder`) y tres pruebas
    (`test_ejecutar_escenario_proveedor_caido_al_rutear_queda_bloqueado`,
    `test_ejecutar_escenario_proveedor_caido_al_responder_queda_bloqueado`,
    `test_ejecutar_escenario_corrida_sana_no_queda_bloqueada_por_el_chequeo_nuevo`).

  Decisión: no se usó el texto de exención "El turno agotó N vueltas sin cerrar"
  (mismo `agente._incidente`, agotamiento de `MAX_VUELTAS`) como marca de proveedor
  caído -- es un comportamiento del modelo, no evidencia de que no se lo pudo
  consultar -- y `_incidente_jev_no_configurado` tiene su propio resumen, sin
  relación con esto. `reporte.py`/`test_banco.py` ya excluían `bloqueado` del
  numerador de `tasa_aprobacion` y ya cortaban la corrida con `pytest.fail`; no hizo
  falta tocarlos.

  RED:
  `.venv/Scripts/python.exe -m pytest -q tests/banco/test_corrida.py -k
  "proveedor_caido or corrida_sana"` -> `2 failed, 1 passed` (las dos corridas con
  proveedor caído seguían `bloqueado=False`; la corrida sana ya pasaba, confirmando
  que el chequeo nuevo no tenía por qué tocarla).

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q tests/banco/test_corrida.py -k
    "proveedor_caido or corrida_sana"` -> `3 passed`.
  - `.venv/Scripts/python.exe -m pytest -q tests/banco tests/test_jev.py
    tests/test_config.py` -> `209 passed, 99 deselected`.
  - Suite completa -> `793 passed, 99 deselected` (788 previos + 5 pruebas nuevas
    de esta sesión, entre esta unidad y la siguiente), 189 s.

  Abierto: ninguno nuevo. No se corrió el banco real (`-m modelo_real`): el
  proveedor sigue caído, y la corrección se probó entera con proveedores falsos.

- 2026-09-26: **Clave de Jev fuera del repr.** Ruta: delegada, un escritor
  (disparador de mapeo: 3 archivos entre código y pruebas). Fuera de la secuencia
  T1-T4: hallazgo del orquestador -- `ClienteJev` es un dataclass cuyo `repr` por
  defecto incluye `api_key`, y una traza de pytest sin capturar la imprimió
  entera.

  Archivos:
  - `src/prisma/jev.py`: `ClienteJev.api_key` pasa a `field(repr=False)`.
  - `src/prisma/config.py`: mismo repaso sobre `Config` (dataclass, singleton de
    módulo que circula por todo el proceso): `db_url`, `authority_db_url`,
    `llm_api_key`, `openrouter_api_key` y `webhook_secret` pasan a
    `field(repr=False, default=...)`. `base_url` queda igual (no es secreto).
  - `tests/test_jev.py`: `test_cliente_jev_repr_no_incluye_la_clave`.
  - `tests/test_config.py` (nuevo): `test_config_repr_no_incluye_credenciales`.

  Decisión: se revisaron además `ProveedorAnthropic`, `ProveedorCompatible`,
  `ProveedorGemini` (`llm.py`) y `Escucha` (`local.py`) -- ninguno es dataclass;
  guardan la credencial sólo para pasarla al cliente HTTP de la librería (`httpx`,
  `anthropic`, `openai`), y el repr por defecto de una clase común no expone
  atributos, así que no hay fuga ahí. `Opcion.token` (`pendientes.py`) y
  `Enlace.token` (`onboarding.py`) quedaron afuera a propósito: el primero es un
  identificador de botón que Telegram ya devuelve tal cual al servidor (no es un
  secreto adicional); el segundo es el enlace de activación que el comando
  `python -m prisma enlaces` imprime a propósito para distribuirlo -- ocultarlo del
  repr rompería el único uso que tiene.

  RED: `.venv/Scripts/python.exe -m pytest -q tests/test_jev.py::test_cliente_jev_repr_no_incluye_la_clave`
  -> `1 failed`: `AssertionError`, la clave aparecía en el repr
  (`ClienteJev(api_key='secreto-de-prueba', ...)`).
  `.venv/Scripts/python.exe -m pytest -q tests/test_config.py` -> `1 failed`: mismo
  patrón, las cinco credenciales aparecían en `repr(Config(...))`.

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_config.py tests/test_jev.py`
    -> `50 passed`.
  - Suite completa -> `793 passed, 99 deselected` (ver entrada anterior; ambas
    unidades se verificaron juntas contra la suite completa).

  Abierto: ninguno.
- 2026-09-26 (orquestador): commits `45552d0` (T3a), `4967b90` (claves fuera del repr) y
  `23fc6f6` (banco con proveedor caído). Evaluación RDD `--base-ref 5e47038`: riesgo
  `medium`, 636 líneas, `slice_budget_reached`. Revisión con consentimiento del usuario, una
  lente (fiabilidad), aprobada y reconocida (`review-0ea0c4be83f8e6d9`). La frontera de
  revisión avanza a `23fc6f6`. Observaciones no bloqueantes:
  - `tests/test_lista_botones.py:511-512` (advertencia): la prueba de respuesta larga
    compara las partes `(i/n)` en el orden de `_outbox`, que sólo ordena por
    `programado_para`; todas las partes comparten ese valor y el id es un uuid, así que el
    orden entre partes no está garantizado (prueba intermitente). El mismo empate existe
    en producción para cualquier respuesta partida (preexistente, `_encolar_respuesta`):
    el despachador podría mandar las partes desordenadas.
  - `tests/banco/test_corrida.py:309-316` (sugerencia): falta la prueba de que un
    incidente de herramienta con la marca de turno caído pero sin `DISCULPA` no bloquea la
    corrida.
  Banco real: el proveedor `nan` sigue devolviendo 404 en toda llamada de chat
  (re-probado 2026-09-26); la corrida se repite cuando vuelva.
- 2026-09-26: **Orden de las partes de una respuesta partida.** Ruta: delegada, un
  escritor (defecto de producción pre-existente, señalado en la revisión del orquestador
  del 2026-09-26 sobre T3a/T3, primera de las dos observaciones no bloqueantes).

  Problema: `salida.enqueue_outbox` mandaba todas las partes de un mensaje partido
  (`allow_split=True`) con el mismo `programado_para`, y `despachador.despachar` sólo
  ordena `by programado_para` (`despachador.py:299`) -- el `id` de `message_outbox` es un
  `uuid` al azar que no desempata. El orden de entrega entre partes quedaba librado al
  azar del orden físico con el que Postgres devolviera las filas empatadas; lo mismo hacía
  intermitente `tests/test_lista_botones.py:511-512` (helper `_outbox`, que sólo ordena por
  esa columna). Con varias partes compartiendo `ahora`, el mensaje de botones de T3a
  (`agente._encolar_respuesta_con_tareas`, programado `ahora + 1 microsegundo`) podía
  incluso empatar con partes siguientes o llegar antes que ellas.

  Archivos:
  - `src/prisma/salida.py` (`enqueue_outbox`): cada parte se programa ahora en
    `base + microsegundos(índice)`, con `base` fijada una sola vez en Python
    (`scheduled_for` o, si no vino, `datetime.now(timezone.utc)`) -- no con
    `coalesce(%s, now())` en SQL, porque `now()` devuelve la hora de inicio de la
    transacción, la misma para todas las filas del bucle, y no serviría para desempatar.
  - `src/prisma/agente.py` (`_encolar_respuesta_con_tareas`): el mensaje de botones ahora
    se programa `len(partes)` microsegundos después de `ahora` -- después de la ÚLTIMA
    parte del texto (índices `0..len(partes)-1`), no de la primera. `partes` se recalcula
    con `salida.prepare_payload` (la misma función determinística que usa `enqueue_outbox`
    por dentro) sólo para contar cuántas partes van a salir: el valor de retorno de
    `enqueue_outbox` no sirve para esto, porque son filas efectivamente insertadas
    (`escalera.encolar` y otras llamadas lo suman para saber cuánto entregaron de verdad
    pese al `on conflict (dedupe_key) do nothing`, y ese conteo tiene que seguir
    reflejando inserciones reales, no partes intentadas).
  - `tests/test_salida.py`: `test_split_outbox_parts_get_strictly_increasing_schedule`
    (nueva) -- llama a `enqueue_outbox` directo con un texto largo y comprueba, ordenando
    por `dedupe_key` (que codifica el índice de cada parte de forma estable, no por la
    columna que se está corrigiendo), que `programado_para` queda estrictamente creciente
    y sin empates.
  - `tests/test_lista_botones.py`: `test_lista_con_respuesta_larga_se_parte_y_los_botones_van_aparte`
    ya no asume que el `order by programado_para` de `_outbox` alcanza por casualidad --
    ordena explícitamente las partes por esa columna dentro de la prueba y comprueba
    primero que la marca sea estrictamente creciente y sin empates, antes de comparar las
    etiquetas `(i/n)`.

  Decisión: no se construyó ningún mecanismo de reintento con orden garantizado.
  `despachador._fallo` (despachador.py:371-388) reprograma `programado_para` de la fila
  que falló, sola, a `cal.dentro_de_jornada(ahora)` -- independiente del resto de las
  partes de ese mismo mensaje. Si una parte falla y las demás no, la reprogramada puede
  volver a quedar antes o después de sus hermanas: el orden estrictamente creciente que
  esta corrección garantiza es el de la primera pasada del despachador sobre un lote
  recién encolado, no el de una entrega que ya pasó por un reintento. Queda documentado
  como límite conocido, no corregido -- el alcance pedido fue documentarlo, no construir
  un mecanismo de orden para reintentos.

  RED: `.venv/Scripts/python.exe -m pytest -q
  tests/test_salida.py::test_split_outbox_parts_get_strictly_increasing_schedule` (contra
  `enqueue_outbox` revertido a antes de esta corrección, con la prueba ya escrita) ->
  `1 failed`: `AssertionError` en `len(set(marcas)) == len(marcas)` -- las 13 partes
  generadas por el texto de prueba compartían un único valor de `programado_para` (el
  defecto reportado, reproducido).

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q
    tests/test_salida.py::test_split_outbox_parts_get_strictly_increasing_schedule` ->
    `1 passed`.
  - `.venv/Scripts/python.exe -m pytest -q tests/test_salida.py tests/test_lista_botones.py
    tests/test_agente.py tests/test_botones.py` -> `59 passed`.
  - `tests/test_lista_botones.py` corrida 5 veces seguidas (chequeo de intermitencia
    pedido por el usuario) -> `12 passed` las 5 veces.
  - Barrido de regresión: `.venv/Scripts/python.exe -m pytest -q tests/test_salida.py
    tests/test_lista_botones.py tests/banco tests/test_agente.py tests/test_botones.py`
    -> `219 passed, 99 deselected`.
  - Suite completa -> `795 passed, 99 deselected` (793 previos + 2 pruebas nuevas, entre
    esta unidad y la siguiente), 192 s.

  Abierto: ninguno nuevo. El límite de orden tras un reintento (arriba) queda
  documentado, no resuelto -- no es un defecto de esta corrección, es el alcance que se
  pidió.
- 2026-09-26: **Banco: cobertura del carve-out de proveedor caído.** Ruta: delegada, un
  escritor (cobertura sugerida en la misma revisión del orquestador, segunda observación
  no bloqueante). Fuera de la secuencia T1-T4.

  Problema: `tests/banco/corrida.py::_incidentes_de_proveedor_caido` sólo cuenta un
  incidente con la marca de `agente._incidente` (`_MARCA_TURNO_CAIDO`, "Falló un turno de
  conversación (") como proveedor caído si además `agente.DISCULPA` está en la respuesta
  visible -- esa misma marca también se genera dentro de `_ejecutar_una` para un
  `psycopg.Error` de una sola herramienta, que el turno sigue procesando con normalidad y
  nunca deja `DISCULPA` como respuesta. No había ninguna prueba que ejercitara ese segundo
  camino ni que probara que el bloqueo del primero viene realmente de esa marca.

  Archivos: `tests/banco/test_corrida.py` --
  `test_ejecutar_escenario_incidente_de_herramienta_sin_disculpa_no_bloquea` (nueva:
  `herramientas.ejecutar` reemplazado por `monkeypatch` para levantar
  `psycopg.OperationalError` dentro de una llamada a `consultar_tareas`, con un
  `ProveedorGuionado` de dos vueltas -- la herramienta que falla y un cierre de texto
  normal sin `DISCULPA` -- comprueba que la corrida NO queda bloqueada aunque el incidente
  con la marca de turno caído sí se registre); `test_ejecutar_escenario_proveedor_caido_al_responder_queda_bloqueado`
  (reforzada: ahora comprueba además que `motivo_bloqueo` empieza con `_MARCA_TURNO_CAIDO`,
  no sólo que sea una cadena no vacía).

  Decisión: se comprobó con una mutación deliberada que la prueba nueva depende de la
  guarda -- sacando temporalmente `and DISCULPA in respuesta_texto` de
  `_incidentes_de_proveedor_caido`, la prueba pasó a fallar (`assert r.bloqueado is False`
  con `bloqueado=True`), confirmando que sin esa guarda la corrida se bloquearía por un
  fallo de herramienta que no es un proveedor caído; se restauró la guarda de inmediato.
  Ningún archivo de producción cambió en esta unidad: es cobertura, no corrección.

  RED/mutación: `.venv/Scripts/python.exe -m pytest -q
  tests/banco/test_corrida.py::test_ejecutar_escenario_incidente_de_herramienta_sin_disculpa_no_bloquea`
  con la guarda quitada -> `1 failed`: `AssertionError: assert True is False`
  (`r.bloqueado`). Con la guarda restaurada, mismo comando -> `1 passed`.

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q tests/banco/test_corrida.py -k
    "proveedor_caido or corrida_sana or incidente_de_herramienta"` -> `4 passed`.
  - `.venv/Scripts/python.exe -m pytest -q tests/banco/test_corrida.py` -> `34 passed`.
  - Barrido de regresión (junto con la unidad anterior): `.venv/Scripts/python.exe -m
    pytest -q tests/test_salida.py tests/test_lista_botones.py tests/banco
    tests/test_agente.py tests/test_botones.py` -> `219 passed, 99 deselected`.
  - Suite completa -> `795 passed, 99 deselected` (ver entrada anterior; ambas unidades se
    verificaron juntas contra la suite completa).

  Abierto: ninguno. Banco real: el proveedor `nan` sigue devolviendo 404 en toda llamada
  de chat (no se volvió a probar en esta unidad).
- 2026-09-26 (orquestador): **corrección sobre el orden de las partes.** La versión del
  escritor fijaba la base con `datetime.now()` de la aplicación cuando no llegaba
  `scheduled_for`; antes la ponía `now()` de PostgreSQL, que es la fuente oficial del
  estado. Se restituyó la hora de la base: `coalesce(%s, now()) + %s * interval
  '1 microsecond'`, con el índice de la parte como desplazamiento (que `now()` sea igual
  para todas las filas de la transacción no impide desempatar: el desplazamiento lo hace).
  Verificación: `tests/test_salida.py tests/test_lista_botones.py tests/banco/test_corrida.py`
  -> `64 passed`; suite completa -> `795 passed, 99 deselected` (192 s).
  Banco real: `nan` sigue en 404; una clave inválida también da 404, así que el servicio
  rechaza el pedido antes de autenticar (falla del proveedor, no de la cuenta del usuario,
  que está activa). La URL usada coincide con la documentación de `nan.builders/docs`.
- 2026-09-26: **T4 cerrada.** Ruta: delegada, un escritor (disparador de mapeo:
  código y pruebas del banco en `tests/banco/` -- `escenario.py`, `corrida.py`,
  `comprobadores.py`, `test_banco.py`, `test_replays.py`, más los archivos de
  prueba correspondientes).

  Unidades (para que el orquestador pueda commitear por separado):
  1. **Extensión de esquema y corredor (`toques` genéricos).**
     `tests/banco/escenario.py` (campo `toques`, validación), `tests/banco/corrida.py`
     (`_pendiente_actual`, `_resolver_opcion_toque`, `_tocar_opcion`, y el bloque
     nuevo en `ejecutar_escenario`), `tests/banco/test_escenario.py` y
     `tests/banco/test_corrida.py` (pruebas nuevas de esta unidad).
  2. **Comprobador `comprobar_pregunta_con_opciones`.** `tests/banco/comprobadores.py`
     (`_hace_pregunta` extraída, `comprobar_pregunta_con_opciones`,
     `escenario.py` campo `permite_pregunta_sin_opciones`), `tests/banco/test_banco.py`
     y `tests/banco/test_replays.py` (wiring, activo por defecto), pruebas nuevas en
     `tests/banco/test_comprobadores.py` y `tests/banco/test_escenario.py`.
  3. **Escenarios nuevos.** `tests/banco/escenarios/b-0016.yaml` (lista de tareas
     como botones, sin pregunta abierta), `b-0017.yaml` (tocar una tarea -> menú ->
     acción -> vista previa, sin efecto antes de Confirmar, usando `toques`),
     `b-0018.yaml` (referencia ambigua: la elección se ofrece con botones, no en
     texto abierto).

  Decisiones de diseño:
  - **`toques` genéricos, no un mecanismo por caso.** El enunciado pedía "tocar el
    botón cuya etiqueta es X / la N-ésima tarea / la acción del menú X" de forma
    genérica. Se agregó un solo campo de escenario, `toques: [{"etiqueta": ...} |
    {"indice": ...}]`, resuelto EN ORDEN por `corrida._pendiente_actual` (la última
    `pending_action` "esperando" del chat, sin importar qué la armó) +
    `corrida._resolver_opcion_toque` (busca la opción REAL por etiqueta exacta o por
    posición 0-based en `pending_action_option.orden`) + `corrida._tocar_opcion`
    (el mismo `callback_query` sintético que ya usan Confirmar y la aclaración con
    botones). Nunca se arma ni se acepta un token inventado: si un toque no
    resuelve (no hay ninguna acción pendiente, o la que hay no ofrece esa
    etiqueta/índice), se levanta `LookupError` -- capturado como el resto de fallas
    de infraestructura del escenario, la corrida queda `bloqueado` con el motivo
    exacto, nunca inventa un toque ni cae en silencio.
  - **Dónde se insertan los toques.** Después de la aclaración con botones (T6, si
    la hay) y ANTES de capturar `herramientas_antes_del_toque`/`conteos_antes_del_
    toque` -- la propiedad central de T4 original (nada se aplica antes de
    Confirmar) tiene que seguir valiendo con estos pasos de más en el medio, igual
    que ya valía con la aclaración. El toque automático en Confirmar de siempre
    (T1, sin tocar en esta unidad) sigue corriendo DESPUÉS de los `toques` del
    escenario: si el último toque declarado llega a una vista previa, ese Confirmar
    la resuelve solo, y `conteos_antes_del_toque` queda capturado justo antes de
    ese Confirmar -- exactamente el punto que pide el enunciado ("con NO efecto en
    PostgreSQL antes de confirmar").
  - **`comprobar_pregunta_con_opciones` reusa la detección existente, no una
    heurística nueva.** Se extrajo `_hace_pregunta(texto)` (`"?" in texto or
    _pide_elegir_en_imperativo(texto)`) de adentro de `comprobar_pregunta` (T7) --
    la misma detección, ahora compartida. El comprobador nuevo es la mitad que
    faltaba: `comprobar_pregunta` (activo sólo con `debe_preguntar: true`) aprueba
    tanto una pregunta con botones como una en texto abierto, porque su pregunta es
    "¿frenó en vez de actuar?"; `comprobar_pregunta_con_opciones` (activo por
    defecto en TODO escenario) es estricto sobre la FORMA -- si pregunta, tiene que
    ofrecer botones (ADR 0007 puntos 1 y 5) -- y no mira en absoluto qué
    herramientas se ejecutaron. Una respuesta que no pregunta nada (ADR 0007, punto
    pendiente "si una respuesta puede cerrar sin opciones") aprueba sin condición:
    esta comprobación no toma partido sobre ese punto, sigue abierto.
  - **Alcance de la comprobación nueva: por defecto en todo escenario, con
    opt-out explícito.** Se agregó `Escenario.permite_pregunta_sin_opciones`
    (default `False`) y se comprobó ANTES de activarla por defecto cuántos
    escenarios existentes cambiarían de veredicto: el único escenario que hoy se
    gradúa de verdad en la suite por defecto (sin proveedor real) es el replay
    `tests/banco/replays/afirma-resolvio-sin-ejecutar-la-herramienta.json`
    (`b-0003`) -- su respuesta grabada ("Listo, ya resolví el bloqueo.") no
    pregunta nada (`_hace_pregunta` da `False`), así que la comprobación nueva
    aprueba sin condición y el veredicto esperado ("falla", por las otras dos
    comprobaciones) no cambió; se verificó corriendo `tests/banco/test_replays.py`
    con la comprobación ya activada -- pasa igual. Los 33 escenarios YAML
    preexistentes sólo corren contra el modelo real (`-m modelo_real`, fuera de la
    suite por defecto) y el proveedor sigue caído (ver más abajo): no se puede
    correr ninguno para confirmar si cambiarían de veredicto. Los seis con
    `debe_preguntar: true` (`b-0008` a `b-0012`, `b-0014`) son los más expuestos --
    si alguno pregunta en texto abierto sin ofrecer botones, la comprobación nueva
    lo marcará `falla` por primera vez, que es exactamente el comportamiento que
    pide ADR 0007; no se les agregó `permite_pregunta_sin_opciones` de antemano,
    sin evidencia de que lo necesiten -- **PENDIENTE**: revisar sus resultados en
    la primera corrida real después de esta unidad y decidir el opt-out sólo si
    alguno lo necesita genuinamente (no como default preventivo).
  - **Escenarios nuevos: estructura, no ejecución.** El proveedor real (`nan`)
    sigue devolviendo 404 (re-confirmado en la sesión anterior), así que
    `b-0016`/`b-0017`/`b-0018` sólo se validaron estructuralmente
    (`cargar_escenarios`, sin `EscenarioInvalido`) y quedan en `tests/banco/
    escenarios/` para correr contra el modelo real cuando el proveedor vuelva --
    **PENDIENTE**. `b-0017` es la prueba de aceptación pensada para la propiedad
    de punta a punta (lista -> menú -> acción -> vista previa): los dos `toques`
    ("indice: 0" y la etiqueta del menú) los simula el corredor en nombre de la
    persona, no el modelo -- el modelo sólo decide llamar o no `consultar_tareas`;
    si no la llama (porque ya tiene las tareas en contexto y contesta sin volver a
    consultarlas), T3 no arma ninguna lista de botones y el primer toque queda
    `bloqueado` por "no hay ninguna acción pendiente" -- limitación inherente a un
    escenario contra un modelo real, documentada, no corregida acá.
  - **Prueba de punta a punta en la suite por defecto (reemplaza un replay
    fabricado).** El enunciado pedía "al menos un replay o una corrida guionada"
    probando el circuito completo. No se fabricó un archivo de replay (un replay
    representa una corrida real ya evaluada; no hubo ninguna, con el proveedor
    caído, y fabricar uno sería presentar como evidencia real algo que no lo es).
    En cambio, `tests/banco/test_corrida.py::
    test_ejecutar_escenario_toques_lista_tarea_menu_accion_llega_a_la_vista_previa`
    corre con `ProveedorGuionado` (sin red) el circuito completo: el modelo llama
    `consultar_tareas`, T3 arma la lista con un botón por tarea, un toque genérico
    (`{"indice": 0}`) abre el menú de esa tarea (T2), otro (`{"etiqueta": "Ya la
    terminé"}`) llega a la vista previa de `actualizar_estado` -- se verifica que
    nada de lo que las 8 herramientas escriben cambió antes de ese punto
    (`conteos_antes_del_toque == conteos_antes` en las tablas que escriben) y que
    el Confirmar automático de siempre aplica el cambio real después (la tarea
    queda en `en_revision`).

  RED (`git stash push -- tests/banco/escenario.py tests/banco/comprobadores.py
  tests/banco/corrida.py`, con los archivos de prueba ya escritos):
  - `tests/banco/test_escenario.py` -> `11 failed, 30 passed` (los 11 nuevos de
    `toques`/`permite_pregunta_sin_opciones`; el resto de la suite de ese archivo
    ya pasaba, sin tocar).
  - `tests/banco/test_comprobadores.py` y `tests/banco/test_corrida.py`:
    `ImportError` al recolectar (`comprobar_pregunta_con_opciones`,
    `_pendiente_actual` todavía no existían) -- exactamente el motivo esperado.
  `git stash pop` restauró la implementación antes de seguir.

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q tests/banco/test_escenario.py
    tests/banco/test_comprobadores.py tests/banco/test_corrida.py` -> `174 passed`.
  - `.venv/Scripts/python.exe -m pytest -q tests/banco` -> `187 passed,
    108 deselected` (99 previos + 9 nuevos: 3 escenarios × `--banco-n` 3 por
    defecto).
  - `.venv/Scripts/python.exe -m pytest -q` (suite completa) -> `822 passed,
    108 deselected` (795 previos + 27 pruebas nuevas de T4: 7 en
    `test_comprobadores.py`, 11 en `test_escenario.py`, 9 en `test_corrida.py`),
    197 s.

  Nota para el orquestador (fuera del alcance autorizado, "no tocar docs/"):
  `docs/validation/README.md`, sección "Banco conversacional (capas B y D)",
  podría sumar una mención corta de los campos de escenario nuevos (`toques`,
  `permite_pregunta_sin_opciones`) y del comprobador `pregunta_con_opciones` --
  se deja a criterio del orquestador, no se editó.

  Abierto:
  - **PENDIENTE**: corrida contra el modelo real cuando vuelva `nan`, para
    `b-0016`/`b-0017`/`b-0018` y para confirmar si alguno de los seis escenarios
    `debe_preguntar: true` necesita `permite_pregunta_sin_opciones` de verdad.
  - Punto pendiente de ADR 0007 ("si una respuesta puede cerrar sin opciones")
    sigue sin resolver -- no era parte del pedido de esta unidad; se verificó que
    `comprobar_pregunta_con_opciones` no fuerza una respuesta al respecto (una
    respuesta que no pregunta nada aprueba sin condición).
  - Mismas brechas fuera de alcance de unidades anteriores sin cambios:
    autoridad para `cancelada` (T2b) y "Adjuntar evidencia" del aprobador en el
    menú (T2).
- 2026-09-26 (orquestador): commits `4b90984`, `07f1f8a`, `6517faa` (toques genéricos y
  comprobador de pregunta sin opciones) y `4dc1997` (escenarios b-0016 a b-0018).
  Evaluación RDD `--base-ref 23fc6f6`: riesgo `medium`, 1096 líneas,
  `slice_budget_reached`. Revisión con consentimiento del usuario, una lente (fiabilidad),
  aprobada y reconocida (`review-356a9a31c3d84353`); la frontera de revisión avanza a
  `4dc1997`. Observaciones no bloqueantes:
  - `tests/banco/corrida.py:467-471` (advertencia): `_pendiente_actual` elige con `order by
    creado_en desc limit 1` sin desempate; dos `pending_action` esperando creadas en la
    misma transacción comparten `creado_en` y el toque genérico se resolvería contra
    cualquiera de las dos. Pendiente.
  - `tests/banco/test_replays.py:97-100` (sugerencia): sin prueba de punta a punta de la
    exclusión `permite_pregunta_sin_opciones` ni de que el comprobador activo cambie el
    veredicto. Pendiente.
  - `src/prisma/salida.py:199` (sugerencia, verificada sin cambio): el desplazamiento por
    parte aplica a todos los llamadores; el único que encola un mensaje detrás de un texto
    partido es `agente._encolar_respuesta_con_tareas` (`agente.py:565`), que ya se programa
    después de la última parte. Los demás llamadores con `allow_split=True`
    (`gateway.py:270,289,553`, `reloj.py:93`, `escalera.py:319`, `onboarding.py:188`,
    `agente.py:356,544`) encolan un único mensaje, sin seguimiento.
  `nan` volvió a responder (06:24Z; chat 200 con la clave real); banco real en curso.
- 2026-09-26: **Tres correcciones del banco (falsos rechazos de `ofrecer_opciones`,
  desempate de `_pendiente_actual`, puerta de `permite_pregunta_sin_opciones` sin
  prueba de punta a punta).** Ruta: delegada, un escritor (disparador de mapeo:
  código y pruebas del banco en `tests/banco/` -- `corrida.py`, `comprobadores.py`,
  `test_corrida.py`, `test_replays.py`, `test_banco.py`, `test_comprobadores.py`).
  Sólo `tests/banco/`; ningún cambio de esquema ni de `src/`.

  **1. El comprobador y el corredor ignoraban las opciones que ofrece el modelo
  (falsos rechazos).** Corrida real `tests/banco/reportes/banco-20260926T112553Z.json`,
  escenario `b-0013` (2/3 falló). "lo del dashboard" es ambiguo entre dos tareas
  sembradas; en las corridas que fallaron el MODELO llamó `ofrecer_opciones`
  ofreciendo las dos tareas como botones (comportamiento correcto, ADR 0007), pero
  `comprobar_aclaracion` marcaba "no ofreció botón para [...] (ofrecidas: [])" porque
  sólo reconocía la aclaración con botones del servidor (`_SENTINEL_ACLARACION`), y el
  corredor nunca tapeaba la elección del modelo (`pendientes.SENTINEL_OPCIONES_MODELO`),
  así que `actualizar_estado` nunca corría. Evidencia de la forma real del problema:
  `tests/banco/reportes/replay-candidato-b-0013-0.json` grabó al modelo ofreciendo una
  tarea por `tarea_id` (etiqueta propia, sin el sufijo "(simulado)" del título real) y
  la otra por `texto` (nombra la tarea pero no la resuelve); `replay-candidato-b-0013-2.json`
  grabó al modelo ofreciendo las DOS por `tarea_id` -- el caso que tiene que aprobar.

  Archivos: `tests/banco/corrida.py` (`_aclaracion_para_elegir` reconoce ahora
  cualquiera de las dos formas -- devuelve `(pending_action_id, herramienta)` en vez de
  sólo el id --, `_opciones_pendiente` trae también `valor`, y el bloque de
  `ejecutar_escenario` que arma `etiquetas_aclaracion_ofrecidas` y decide qué tapear
  distingue el mecanismo); `tests/banco/test_corrida.py` (dos pruebas nuevas).

  Decisiones:
  - **Match por título (`valor.titulo`), no por la etiqueta del botón.** La corrida
    real mostró por qué: el modelo puso una etiqueta propia ("Actualizar el dashboard
    de HMI", sin "(simulado)") para una opción de tarea -- si el corredor comparara por
    etiqueta, no reconocería esa tarea contra `aclaracion_esperada.candidatas` (siempre
    títulos completos). `valor.titulo` es el título real que `ofrecer_opciones` ya
    validó contra PostgreSQL (`herramientas._tareas_activas_por_id`), sin depender de
    qué etiqueta haya elegido el modelo.
  - **Una opción de `texto` que sólo nombra la tarea no cuenta como ofrecida.** Tal
    cual lo pidió el enunciado: el servidor sólo puede resolver una opción de tarea
    real (`tipo: "tarea"`, con `tarea_id` validado); una opción de `texto` sigue siendo
    un botón tocable (retoma la conversación con ese texto), pero no es prueba de que
    el servidor haya reconocido esa tarea, así que no cuenta para
    `etiquetas_aclaracion_ofrecidas` ni es candidata a tapear como "elegir".
  - **`comprobar_aclaracion` no cambió.** Toda la corrección vive en cómo
    `corrida.py` arma `etiquetas_aclaracion_ofrecidas` -- el comprobador sigue
    comparando una lista de strings contra `candidatas_esperadas`, sin saber de
    mecanismos ni de tipos de opción.
  - **No se agregó el replay real de b-0013 a `tests/banco/replays/`.** Se
    consideró, tal como sugiere el enunciado. Se descartó: el guión grabado de
    `replay-candidato-b-0013-2.json` (el caso que ofrece las dos tareas por `tarea_id`)
    tiene sólo dos respuestas del proveedor -- las que se usaron para llegar a
    `ofrecer_opciones` -- porque en la corrida real nunca se tapeó nada. Para un replay
    de punta a punta que además pruebe que el tap llega a `actualizar_estado` hacen
    falta más respuestas grabadas (las del turno que retoma tras el toque), que esa
    corrida real jamás produjo. Un archivo de replay tiene que representar una corrida
    ya evaluada de verdad (T4, mismo criterio ya usado con `b-0016`-`b-0018`); en vez
    de fabricar las respuestas faltantes, las dos pruebas nuevas usan un
    `ProveedorGuionado` propio con guión completo.

  RED (`git stash push -- tests/banco/corrida.py`, con las pruebas ya escritas):
  `tests/banco/test_corrida.py -k "opciones_modelo_ofrece or texto_no_cuenta"` ->
  `2 failed` -- las dos por el motivo esperado (`etiquetas_aclaracion_ofrecidas`
  vacío: el corredor no reconocía la elección del modelo). `git stash pop` restauró
  la implementación.

  GREEN:
  - `tests/banco/test_corrida.py -k "opciones_modelo_ofrece or texto_no_cuenta"` ->
    `2 passed`.
  - `tests/banco/test_corrida.py` completo -> `47 passed`.
  - `tests/banco` -> `189 passed, 108 deselected`.

  **2. `_pendiente_actual` sin desempate (hallazgo del orquestador,
  `tests/banco/corrida.py:467-471`).** `order by creado_en desc limit 1` no desata un
  empate: dos `pending_action` 'esperando' creadas en la MISMA transacción comparten
  `creado_en` (`now()` de Postgres es constante dentro de una transacción) -- puede
  pasar si un turno del modelo llama a dos herramientas y cada una deja su propia
  acción pendiente. Verificado que el hallazgo es real, no sólo teórico: una prueba que
  fuerza el empate y corre contra el código sin corregir devuelve la PRIMERA acción en
  vez de la segunda (ver RED abajo).

  Archivos: `tests/banco/corrida.py` (`_pendiente_actual` agrega `ctid desc` como
  segundo criterio de orden); `tests/banco/test_corrida.py` (una prueba nueva).

  Decisión: **desempatar por `ctid`, no por una columna nueva.** Sin cambio de
  esquema (fuera de alcance), ninguna columna existente de `pending_action` sirve:
  `id` es un UUID aleatorio (`gen_random_uuid()`, sin orden), y el `xmin` de la
  transacción es igual para las dos filas (es la misma transacción). `ctid` -- la
  posición física de la fila -- sí crece con el orden real de inserción dentro de una
  misma transacción; alcanza para el banco porque corre en serie, sin otra transacción
  escribiendo la tabla al mismo tiempo -- no es una garantía general de Postgres bajo
  escritura concurrente, pero el banco nunca la tiene. Se consideró "la acción
  referenciada por el mensaje más reciente en `message_outbox`" (sugerido en el
  enunciado): se descartó porque `message_outbox.programado_para` tiene el mismo
  problema (también `now()` de la misma transacción) y `message_outbox.id` es otro
  UUID aleatorio -- no resuelve el empate, sólo lo traslada a otra tabla.

  RED (`git stash push -- tests/banco/corrida.py`, con la prueba ya escrita, que
  registra dos `pending_action` 'esperando' en la misma transacción y confirma que
  comparten `creado_en` antes de comprobar cuál devuelve `_pendiente_actual`):
  `tests/banco/test_corrida.py -k desempata_por_orden` -> `1 failed` -- devolvía la
  primera acción registrada, no la segunda (reproducción real del empate, no
  simulada). `git stash pop` restauró la implementación. Repetida 5 veces en soledad
  tras la corrección: estable, sin parpadeo.

  GREEN:
  - `tests/banco/test_corrida.py -k desempata_por_orden` -> `1 passed` (x5, sin
    parpadeo).
  - `tests/banco` -> `190 passed, 108 deselected`.

  **3. Puerta de `permite_pregunta_sin_opciones` sin prueba de punta a punta
  (hallazgo del orquestador, `tests/banco/test_replays.py:97-100`).** El campo tenía
  prueba de que se parsea bien (`test_escenario.py`) y `comprobar_pregunta_con_opciones`
  tenía prueba sola (`test_comprobadores.py`), pero nada ejercitaba la puerta
  (`if not escenario.permite_pregunta_sin_opciones: comprobaciones.append(...)`,
  repetida igual en `test_banco.py` y `test_replays.py`) sobre una corrida real de
  `ejecutar_escenario`, con los dos valores del campo.

  Archivos: `tests/banco/comprobadores.py` (`comprobaciones_pregunta_con_opciones`,
  nueva -- la puerta en una sola función, para que tenga una sola implementación
  comprobable); `tests/banco/test_replays.py` y `tests/banco/test_banco.py` (los dos
  llamadores reales pasan a usarla, mismo comportamiento); `tests/banco/test_replays.py`
  (dos pruebas de punta a punta nuevas, con `ProveedorGuionado`); `tests/banco/test_comprobadores.py`
  (dos pruebas unitarias nuevas de la función).

  Decisiones:
  - **Extraer la puerta en vez de duplicar la prueba.** `test_banco.py` (marcador
    `modelo_real`, fuera de la suite por defecto) y `test_replays.py` repetían el
    mismo `if`/`append` -- probarlo sólo en un test propio, sin tocar ese código, no
    hubiera probado que los llamadores reales lo usan bien. Extraída a
    `comprobaciones_pregunta_con_opciones(evidencia, *, permite_pregunta_sin_opciones)`,
    los dos llamadores la usan igual y la prueba de punta a punta corre contra la
    función real.
  - **Sin replay fabricado.** Mismo criterio que el punto 1 y que T4 con
    `b-0016`-`b-0018`: un replay representa una corrida ya evaluada de verdad. Las
    pruebas de punta a punta corren un `ProveedorGuionado` directo (sin red, en la
    suite por defecto) contra una respuesta que pregunta en texto abierto sin botones,
    y comparan `comprobaciones_pregunta_con_opciones` con los dos valores del campo.
  - **Comprobación por mutación, no sólo RED/GREEN.** La puerta ya funcionaba bien
    (hallazgo de cobertura, no de comportamiento) -- las pruebas nuevas pasaron ya en
    su primera corrida. Para probar que de verdad hubieran atrapado una puerta rota,
    se invirtió la condición de `comprobaciones_pregunta_con_opciones` a propósito, se
    confirmó que las dos pruebas nuevas fallan, y se restauró la función.

  RED: no aplica -- la puerta ya era correcta (hallazgo de cobertura). Mutación
  temporal (`if permite_pregunta_sin_opciones` invertido en
  `comprobaciones_pregunta_con_opciones`): `tests/banco/test_replays.py -k
  "permite_pregunta or pregunta_con_opciones_activa"` -> `2 failed` (las dos nuevas,
  por el motivo esperado). Función restaurada.

  GREEN:
  - `tests/banco/test_replays.py` -> `3 passed`.
  - `tests/banco/test_comprobadores.py` -> `92 passed`.
  - `tests/banco/test_banco.py --collect-only` -> recolecta sin error de import (108
    deselected, `modelo_real`; no se pudo correr contra el modelo real, fuera de
    alcance de esta unidad).
  - `tests/banco` -> `194 passed, 108 deselected`.

  **Verificación final (suite completa):**
  `.venv/Scripts/python.exe -m pytest -q` -> `829 passed, 108 deselected` (línea base
  822 + 7 pruebas nuevas: 2 del punto 1, 1 del punto 2, 2+2 del punto 3), 221s.

  Abierto:
  - Ninguna de las tres correcciones tocó `src/` ni el esquema -- las tres eran
    defectos/huecos del arnés de pruebas del banco, no del producto.
  - El desempate por `ctid` (punto 2) es válido para el banco (corre en serie); si
    algún día el banco corre corridas en paralelo sobre el mismo chat, hay que
    revisarlo -- no es el caso hoy (`--banco-n` corre corridas secuenciales por
    escenario).
  - `test_banco.py` (punto 3) no se pudo ejecutar contra el modelo real en esta
    unidad (fuera del pedido: sólo se verificó que sigue recolectando).
- 2026-09-26: **T4b cerrada.** Ruta: delegada, un escritor (disparador de mapeo: 4
  archivos de código -- `agente.py`, `gateway.py`, `contexto.py`,
  `deteccion_pregunta.py` -- más pruebas nuevas y adaptadas).

  Decisión del usuario: evidencia real de banco
  (`tests/banco/reportes/replay-candidato-b-0007-*.json`) mostró al modelo
  preguntando en texto abierto ("¿De qué se trata? Contame…") ante una persona sin
  tarea que coincidiera ("lo del proveedor"). Se agrega un cierre GENÉRICO de tres
  botones -- "Es una tarea nueva", "Es sobre una tarea existente", "Quiero
  consultar otra cosa" (`pendientes.ETIQUETA_SALIR_OPCIONES`) -- cuando el turno
  cierra preguntando sin ningún juego de botones propio; texto libre sigue
  disponible. Ambas partes de la decisión: refuerzo del contexto (el modelo debería
  llamar a `ofrecer_opciones` igual, aun sin opciones concretas) Y el servidor
  agrega el cierre si aun así pregunta en texto abierto.

  Archivos:
  - `src/prisma/deteccion_pregunta.py` (nuevo): `hace_pregunta`/
    `pide_elegir_en_imperativo`, movidas de `tests/banco/comprobadores.py` (T7) --
    una sola implementación en `src/prisma/`, porque el servidor la necesita en
    tiempo de ejecución y `tests/banco` puede importar de `src/prisma/`, nunca al
    revés (`AGENTS.md`).
  - `src/prisma/agente.py`: `responder` gana una rama `elif hace_pregunta(salida)`
    después de la de T3 (lista de tareas) y antes de `_encolar_respuesta` -- nunca
    compite con confirmaciones/elecciones (ya cerraron el turno antes) ni con la
    lista de T3 (mismo `if`/`elif`). `_encolar_texto_con_opciones` (nuevo): el
    armado de "¿entra con los botones? si no, texto partido aparte + botones
    cortos después" que tenía `_encolar_respuesta_con_tareas` (T3a), extraído para
    que T4b lo reuse sin duplicarlo; `_encolar_respuesta_con_tareas` queda como una
    envoltura fina sobre el helper. `_encolar_opciones_genericas` (nuevo): arma las
    tres opciones (`tipo`: `tarea_nueva`/`tarea_existente`/`salida`) y guarda
    `entrante_id`/`mensaje_original` en `args` (iguales para las tres, no por
    opción) para que "Es una tarea nueva" pueda arrancar el alta guiada.
  - `src/prisma/gateway.py`: `_resolver_toque_opcion_modelo` gana dos `tipo` más --
    `tarea_nueva` llama a `_iniciar_alta_guiada` (la misma que ya usa "Es una tarea
    nueva" de la aclaración con botones, T4) con `route_task={}` (sin propuestas:
    el alta guiada las pide todas); `tarea_existente` llama a
    `_mostrar_tareas_propias` (nueva), que lista las tareas ACTIVAS de la propia
    persona bajo RLS y reusa `agente._opciones_lista_tareas` (el armador de página
    + "Ver más" de T3) en vez de duplicarlo. Sin tareas activas, sólo la salida.
  - `src/prisma/contexto.py`: nueva regla en `PREAMBULO` -- sin opciones concretas,
    llamar a `ofrecer_opciones` igual con las más razonables; nunca cerrar en texto
    abierto.
  - `tests/banco/comprobadores.py`: `_hace_pregunta`/`_pide_elegir_en_imperativo`
    pasan a importarse de `prisma.deteccion_pregunta` (con esos mismos nombres,
    para no tocar el resto del archivo) en vez de definirse acá.
  - `tests/test_deteccion_pregunta.py` (nuevo, 5 pruebas): la detección movida,
    contra los mismos casos que ya la validaban en el banco.
  - `tests/test_pregunta_sin_opciones.py` (nuevo, 14 pruebas): cierre genérico
    agregado/no agregado (aviso sin pregunta, lista de T3 con pregunta,
    `ofrecer_opciones` con pregunta -- nunca dos juegos de botones), texto
    largo/corto, los tres toques (alta guiada, sin `entrante_id` no falla en
    silencio, lista propia con paginación y sin tareas, salida), auditoría sin
    texto.

  Pruebas adaptadas (regresión real, no debilitada):
  - `tests/test_task_intake.py::test_no_mutating_tool_output_is_truth_marked_and_
    has_no_buttons`: el texto guionado terminaba en "Confirm?" -- incidental al
    propósito de la prueba (que un texto plano sin herramienta no quede marcado
    con un `pending_action_id` ajeno), pero desde T4b esa "?" agrega el cierre
    genérico. Se sacó el "?" del texto; la aserción original no cambió.
  - `tests/banco/test_replays.py::test_pregunta_con_opciones_activa_por_defecto_
    falla_la_misma_corrida` -> renombrada
    `test_pregunta_con_opciones_activa_ahora_aprueba_porque_el_servidor_ya_cierra_
    con_botones`: esta prueba corría una corrida real con una pregunta en texto
    abierto para probar que `comprobar_pregunta_con_opciones` la marca `falla` --
    exactamente el hueco que T4b cierra en el servidor. Con T4b, la misma corrida
    ya ofrece opciones (el servidor las agrega), así que el veredicto pasa a
    `aprobado` -- no porque el comprobador se haya debilitado (sigue fallando ante
    una `Evidencia` armada a mano sin botones, `test_comprobadores.py`), sino
    porque el defecto que medía ya no existe. Docstrings actualizados para dejar
    constancia del cambio de sentido.

  Decisiones de diseño:
  - **Detección de pregunta: una sola implementación, movida a `src/prisma/`.**
    `_hace_pregunta`/`_pide_elegir_en_imperativo` vivían sólo en
    `tests/banco/comprobadores.py` (T7); el servidor las necesita ahora en tiempo
    de ejecución. Se mueven a `deteccion_pregunta.py` (nunca al revés: `src/`
    nunca importa de `tests/`) y el banco las importa con los mismos nombres
    privados para no reescribir el resto del archivo.
  - **Reuso del armado de texto+botones de T3a, no una segunda heurística.** T3a ya
    había resuelto "texto que puede superar `BUTTON_TEXT_LIMIT`, junto con
    botones" para la lista de tareas; T4b necesita exactamente lo mismo para el
    cierre genérico. Se extrajo `_encolar_texto_con_opciones` en vez de copiar el
    bloque.
  - **`args` del cierre genérico lleva `entrante_id`/`mensaje_original`, no una
    opción puntual.** Las tres opciones de un mismo cierre comparten el mismo
    `pending_action.args` (T1); sólo "Es una tarea nueva" los lee, pero viajan ahí
    -- igual que "Es una tarea nueva" de la aclaración con botones ya guarda
    `entrante_id`/`mensaje` en el estado de esa pregunta.
  - **Sin `route_task` (propuestas) para el alta guiada del cierre genérico.** A
    diferencia de la aclaración con botones (que sí rutea antes), este cierre
    nunca pasó por el enrutador -- no hay ninguna propuesta que ofrecerle al alta
    guiada. Verificado contra `ingreso_tareas.start`/`_store_proposals`: un
    `proposals={}` no rompe nada, sólo no pre-llena ningún campo.
  - **Nunca se inventa un mensaje de origen sin `entrante_id`.** Si el turno que
    armó el cierre genérico no tenía un `inbound_message` propio (p. ej. al
    retomar otra opción), `_iniciar_alta_guiada` ya registra incidente + aviso
    neutro (patrón existente, sin cambios) -- nunca se lo inventa.
  - **Nunca dos juegos de botones.** La rama nueva es un `elif` después de la de
    T3 (lista de tareas); confirmaciones/elecciones de una herramienta ya cierran
    el turno antes (`if confirmaciones or elecciones: return ...`), así que nunca
    llegan a `hace_pregunta`.

  RED (antes de implementar, `git stash push -- src/prisma/agente.py
  src/prisma/gateway.py src/prisma/contexto.py`, con las pruebas nuevas ya
  escritas y `deteccion_pregunta.py` ya creado):
  `.venv/Scripts/python.exe -m pytest -q tests/test_pregunta_sin_opciones.py
  tests/test_deteccion_pregunta.py` -> `11 failed, 8 passed` -- las 11 fallas son
  exactamente las que dependen del cierre genérico (sin él, ninguna `pending_action`
  de `SENTINEL_OPCIONES_MODELO` se arma); las 8 que ya pasaban son las 5 de
  detección (movida, no depende del cambio) más las 3 que verifican que NO se
  agregan botones de más (ciertas igual sin la funcionalidad). `git stash pop`
  restauró la implementación antes de seguir.

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_pregunta_sin_opciones.py
    tests/test_deteccion_pregunta.py` -> `19 passed`.
  - `.venv/Scripts/python.exe -m pytest -q tests/test_lista_botones.py
    tests/test_opciones_modelo.py tests/test_menu_tarea.py tests/test_agente.py
    tests/test_aclaracion_botones.py tests/test_task_intake.py tests/banco
    tests/test_pregunta_sin_opciones.py tests/test_deteccion_pregunta.py` ->
    primera corrida `2 failed` (las dos regresiones reales de arriba, encontradas
    por el barrido, no simuladas), corregidas las pruebas afectadas -> segunda
    corrida `384 passed, 108 deselected`.
  - `.venv/Scripts/python.exe -m pytest -q` (suite completa) -> `848 passed,
    108 deselected` (línea base 829 + 19 pruebas nuevas de T4b), 200s.

  Abierto:
  - Punto pendiente de ADR 0007 ("si una respuesta puede cerrar sin opciones")
    sigue sin resolver -- T4b no lo decide, sólo actúa cuando SÍ pregunta.
  - `docs/validation/README.md` podría sumar una mención corta del cierre
    genérico y de `deteccion_pregunta.py` -- se deja a criterio del orquestador
    (no se tocó `docs/`, fuera de alcance de esta unidad).
  - No se corrió el banco real contra el modelo (`-m modelo_real`) para esta
    unidad -- queda para el próximo paso, junto con `b-0007` de vuelta.
  - Mismas brechas fuera de alcance de unidades anteriores sin cambios: autoridad
    para `cancelada` (T2b), "Adjuntar evidencia" del aprobador en el menú (T2).
- 2026-09-26: **Un rechazo de `preparar` se auditaba y contaba como ejecutado
  (defecto de producto preexistente desde ADR 0005, hallazgo del orquestador
  sobre el banco real `b-0005-a`).** Ruta: delegada, un escritor (disparador
  de mapeo: `agente.py`, `herramientas.py`, más pruebas).

  Evidencia (orquestador, banco real 2026-09-26 `b-0005-a`, reproducida
  determinísticamente): `herramientas.ejecutar` devuelve tal cual el dict de
  rechazo de negocio que arma `preparar` (`herramientas.py:445-452`, p. ej.
  `{"error": ...}` cuando un id de tarea no resuelve). `agente._ejecutar_una`
  trataba cualquier valor sin excepción como una ejecución real: lo sumaba a
  `acciones` y auditaba `herramienta:<nombre>` -- `crear_dependencia` quedaba
  auditado como ejecutado sin ninguna fila en `dependency`, y como
  `acciones` ya no estaba vacía, `with_no_effect_status` ("Estado: sin
  cambios") no se aplicaba: el modelo podía decir "Anoté…" sin la advertencia.

  Archivos: `src/prisma/agente.py` (`_ejecutar_una`, un bloque nuevo antes
  del chequeo de `consultar_tareas`); `tests/test_agente.py` (dos pruebas
  nuevas).

  Decisión: **señal precisa, sin marcador nuevo.** `_ejecutar_una` nunca pasa
  `ya_confirmada` a `H.ejecutar` (queda en su default `False`). Con eso fijo,
  `herramientas.ejecutar` (línea 445-452) sólo puede devolver un dict SIN
  excepción, para una herramienta que declara `preparar`, cuando `preparar`
  encontró el mismo rechazo de negocio que encontraría el handler -- con una
  preparación que sí puede seguir, siempre levanta `NecesitaConfirmacion`
  antes de tocar el handler. Es una señal exacta (`H.REGISTRO[c.nombre].
  preparar is not None` + resultado es dict), no un heurístico sobre la
  forma del dict (`error`/`falta`): no hizo falta agregar ningún marcador a
  `herramientas.ejecutar`, y `gateway._ejecutar_accion_menu`/
  `_mensaje_resultado_menu` (que también consumen estos dicts, sin
  `ya_confirmada`, y nunca auditaban en ese camino) siguen sin tocar. El
  rechazo se audita con una acción distinta y verdadera,
  `herramienta_rechazada:<nombre>` -- el banco (`_herramientas_registradas`)
  sólo lee `herramienta:%`, así que un rechazo ya no cuenta como ejecutado
  ahí tampoco -- y vuelve al modelo con `is_error: true`. Al no sumarse a
  `acciones`, `with_no_effect_status` (ya existente, sin tocar) se aplica
  solo con la condición que ya tenía: hubo un intento de mutación y ninguna
  acción no-consultar se ejecutó.

  RED (`git stash push -- src/prisma/agente.py`, con las pruebas ya
  escritas): `tests/test_agente.py -k rechazo_de_preparacion_no_se_audita`
  -> `1 failed` (`r.acciones == ['crear_dependencia']`, no `[]`). `git stash
  pop` restauró la implementación.

  GREEN:
  - `tests/test_agente.py -k rechazo_de_preparacion` -> `2 passed`.
  - `tests/test_agente.py tests/test_dependencias.py tests/test_menu_tarea.py
    tests/test_vista_previa_confirmacion.py` -> `89 passed`.

  Abierto:
  - `gateway.py:426-462` (la confirmación por botón, `ya_confirmada=True`)
    audita `herramienta:<nombre>` INCONDICIONALMENTE apenas vuelve de
    `H.ejecutar` sin excepción, antes de mirar si `resultado` es en realidad
    un rechazo de negocio (`preparar`, corrido de nuevo al confirmar,
    encontró un impedimento nuevo). Mismo defecto de fondo que el corregido
    acá, en otro camino -- fuera del pedido de esta unidad (que acotaba el
    alcance a `_ejecutar_una`); no se tocó. Queda para que el usuario decida
    si se corrige en una unidad aparte.
- 2026-09-26: **Se descartaba el texto informativo del modelo cuando además
  ofrecía opciones (defecto de producto, hallazgo del orquestador sobre el
  banco real `b-0001-a`; ADR 0007 punto 2).** Ruta: delegada, un escritor
  (mismo disparador de mapeo que la unidad anterior: `agente.py`, más
  pruebas).

  Evidencia: banco real `b-0001-a`
  (`tests/banco/reportes/replay-candidato-b-0001-a-*.json`): el modelo
  contestó "Tenés dos tareas abiertas: «Programar PLC…» y «Revisar
  comunicaciones…», sin fecha…" Y llamó a `ofrecer_opciones` en la misma
  respuesta. Desde T1, `NecesitaOpciones` se sumaba a `elecciones`, y
  `responder` cerraba el turno con `if confirmaciones or elecciones: return
  Resultado("", ...)` -- el texto que había escrito el modelo no se mandaba
  nunca: la persona sólo recibía la pregunta con botones y perdía la
  información (ADR 0007 punto 2: "el texto da el contexto; la elección se
  hace tocando").

  Archivos: `src/prisma/agente.py` (`responder`: nuevas variables de
  seguimiento del turno, `elegir_pendiente`/`opciones_pendientes`/
  `texto_al_ofrecer`, y el bloque que decide `confirmaciones or elecciones`
  reescrito; `_ejecutar_una`: dos parámetros nuevos, las ramas `except
  H.NecesitaElegir`/`except H.NecesitaOpciones` ajustadas; `_encolar_
  opciones_modelo`: gana un parámetro `texto` y pasa a reusar `_encolar_
  texto_con_opciones` en vez de armar el `enqueue_outbox` a mano);
  `tests/test_opciones_modelo.py` (tres pruebas nuevas, import de
  `BUTTON_TEXT_LIMIT`/`telegram_utf16_units`).

  Decisiones:
  - **La pregunta con botones se sigue encolando siempre; sólo se decide si
    el texto la acompaña.** `_ejecutar_una` ya no encola nada al atrapar
    `NecesitaOpciones` (antes lo hacía ahí mismo, sin saber todavía si el
    resto del turno iba a dejar además una confirmación u otra elección
    pendiente): guarda la excepción en `opciones_pendientes` y `responder`
    decide recién al cerrar el turno completo. Esto es necesario porque
    `test_retomar_con_un_cambio_sigue_pidiendo_confirmar` (T1, ya existente)
    prueba que la pregunta de `ofrecer_opciones` de una vuelta se puede
    tocar aunque una vuelta POSTERIOR del mismo turno deje además una
    confirmación esperando -- si se difiriera también CUÁNDO se encola (no
    sólo el texto), esa acción pendiente dejaría de crearse.
  - **`elecciones` no cambia de forma (contrato externo de
    `Resultado.elecciones`, ya probado).** Mezcla `NecesitaElegir` y
    `NecesitaOpciones` desde T1; se agregó `elegir_pendiente` aparte (sólo
    `NecesitaElegir`) para poder distinguir "la única interacción pendiente
    del turno es `ofrecer_opciones`" sin tocar qué hay en `elecciones`.
  - **El texto es el de la vuelta que llamó a `ofrecer_opciones`, no el de
    una vuelta posterior.** El modelo suele repetir "Listo, ahí tenés las
    opciones" en la vuelta siguiente (la que cierra el turno sin llamadas) --
    ese texto no describe nada; se descarta a propósito. Se captura con un
    antes/después de `len(opciones_pendientes)` por vuelta, quedándose con
    la primera vez que crece.
  - **`ofrecer_opciones` no cuenta como "mutación intentada" para
    `with_no_effect_status`.** Es la pregunta, no un intento de cambio que
    haya fallado -- `intentos_mutacion` la incluye igual (cualquier
    herramienta que no empiece con `consultar_`), así que se filtra antes de
    decidir si corresponde agregar "Estado: sin cambios." Sin este filtro,
    `test_opciones_de_texto_arman_botones_con_la_salida` (T1, ya existente:
    `ofrecer_opciones` solo, sin texto) hubiera roto -- pasaba de `r.texto
    == ""` a `r.texto == "Estado: sin cambios."`, un aviso falso (nada se
    intentó cambiar).
  - **Mismo armado de T3a/T4b, reusado, no una tercera heurística.**
    `_encolar_opciones_modelo` arma `texto_combinado = f"{texto}\n\n
    {e.pregunta}"` y se lo pasa a `_encolar_texto_con_opciones` (el mismo
    helper de T3a/lista-de-tareas y T4b/cierre-genérico): si entra en
    `BUTTON_TEXT_LIMIT` va todo junto; si no, el texto sale partido aparte,
    primero, y los botones -- con la pregunta sola como resumen corto --
    después de la última parte. `pending_action.args` sigue guardando sólo
    `{"pregunta": e.pregunta}`: es lo único que lee `gateway._resolver_
    toque_opcion_modelo` al retomar, sin cambios ahí.

  RED (`git stash push -- src/prisma/agente.py`, con las pruebas ya
  escritas): `tests/test_opciones_modelo.py -k
  "texto_del_modelo_acompana or texto_largo_con_opciones"` -> `2 failed`
  (`r.texto == ''` en vez del texto del modelo; 0 partes de texto en vez de
  >=2) -- la tercera prueba nueva (texto se descarta si además queda una
  confirmación pendiente) ya pasaba sin el fix, como corresponde a una
  prueba de regresión. `git stash pop` restauró la implementación.

  GREEN:
  - `tests/test_opciones_modelo.py` -> `16 passed`.
  - `tests/test_agente.py tests/test_opciones_modelo.py
    tests/test_lista_botones.py tests/test_pregunta_sin_opciones.py
    tests/test_menu_tarea.py tests/test_veracidad.py
    tests/test_vista_previa_confirmacion.py tests/test_dependencias.py
    tests/banco` -> `334 passed, 108 deselected`.

  Abierto:
  - El orden de entrega entre la pregunta de `ofrecer_opciones` (ahora
    encolada al cerrar el turno) y una confirmación de una vuelta posterior
    del MISMO turno puede quedar invertido frente al de antes cuando
    comparten el mismo `scheduled_for` (los dos usan el mismo `ahora` de
    `responder`, como ya pasaba con `_encolar_confirmacion`/`_encolar_
    eleccion`/la vieja `_encolar_opciones_modelo` desde antes de esta
    unidad): el desempate entre mensajes con igual `programado_para` no está
    definido (`despachador.despachar` sólo ordena por esa columna). No es
    una regresión de esta unidad -- el empate ya existía --, pero esta
    unidad lo hace más frecuente al diferir el encolado. Ningún escenario ni
    prueba depende del orden entre esos dos mensajes; se deja constancia
    para que el usuario decida si amerita una unidad aparte.
  - Punto pendiente de ADR 0007 ("si una respuesta puede cerrar sin
    opciones") sigue sin resolver -- no era parte de esta unidad.
- 2026-09-26: **El banco adivinaba entre varias acciones pendientes en
  espera (hallazgo de revisión).** Ruta: delegada, un escritor (disparador
  de mapeo: `tests/banco/corrida.py`, `tests/banco/test_corrida.py`). Sólo
  `tests/banco/`; ningún cambio de esquema ni de `src/`.

  Hallazgo (revisión del orquestador, `tests/banco/corrida.py:467-471`):
  `_pendiente_actual` desataba el empate entre acciones pendientes
  'esperando' del mismo chat con `order by creado_en desc, ctid desc` --
  `creado_en` es igual para dos filas creadas en la MISMA transacción
  (`now()` de Postgres es constante dentro de una transacción; puede pasar
  si un turno del modelo llama a dos herramientas y cada una deja su propia
  acción pendiente), y `ctid` no es una garantía general de Postgres bajo
  escritura concurrente (sólo "funcionaba" porque el banco corre en serie) --
  además de no ser ningún criterio de negocio, sólo posición física.
  `_aclaracion_para_elegir` (los dos sentinels de aclaración) no tenía
  NINGÚN desempate (`order by creado_en desc limit 1` a secas). Y
  `o["valor"]["titulo"]` podía levantar `KeyError` ante una opción de tarea
  sin título.

  Archivos: `tests/banco/corrida.py` (`_pendiente_actual` eliminada,
  reemplazada por `_resolver_toque_generico`; `_aclaracion_para_elegir`
  eliminada, reemplazada por `_aclaraciones_para_elegir` -- devuelve TODAS,
  no una sola --; `_candidatas_tarea_por_titulo`, nueva, extraída para poder
  probarla sola; `_resolver_opcion_toque` sin cambios de comportamiento;
  `ejecutar_escenario` reescribe los dos bloques que resuelven "aclaración
  esperada" y "toques genéricos"); `tests/banco/test_corrida.py` (import
  actualizado; las tres pruebas de `_pendiente_actual` reemplazadas por
  cinco de `_resolver_toque_generico`; una prueba nueva de
  `_candidatas_tarea_por_titulo`).

  Decisiones:
  - **Resolver contra la UNIÓN de todas las acciones 'esperando' del chat,
    nunca contra una elegida por orden.** `_resolver_toque_generico` reúne
    los ids de TODAS las acciones pendientes 'esperando' de ese chat (sin
    `order by` ni límite), les aplica `_resolver_opcion_toque` (sin cambios)
    una por una, y junta las coincidencias. Exactamente una coincidencia ->
    se tapea. Ninguna coincidencia, o ninguna acción pendiente -> `LookupError`
    (como ya pasaba: la corrida queda `bloqueado`, nunca `aprobado` por una
    adivinanza). Más de una coincidencia EN ACCIONES PENDIENTES DISTINTAS ->
    `LookupError` nuevo ("ambiguo, no se adivina cuál"): antes esto eligía
    en silencio cualquiera de las dos por `ctid`.
  - **Se quitó `ctid` del `order by` por completo, no se lo reemplazó por
    otra columna.** El enunciado lo pedía explícitamente; con la resolución
    por unión + conteo de coincidencias, ya no hace falta ningún desempate
    por orden -- el criterio pasó a ser "cuántas acciones pendientes
    distintas ofrecen lo que pide el escenario", no "cuál se insertó
    después".
  - **Misma lógica para la aclaración esperada (`aclaracion_esperada`).**
    `_aclaraciones_para_elegir` devuelve TODAS las acciones pendientes de
    aclaración (con su `herramienta`, para saber qué semántica de comparación
    usar -- título de tarea para `SENTINEL_OPCIONES_MODELO`, etiqueta para
    la aclaración de botones de siempre); `ejecutar_escenario` arma las
    coincidencias de la misma manera (una por acción pendiente, unidas) y
    aplica el mismo criterio: una -> tapea, más de una en acciones distintas
    -> `LookupError`.
  - **`_candidatas_tarea_por_titulo` extraída para poder probar el `.get`
    sin `ejecutar_escenario` completo.** Antes vivía inline; con
    `.get("titulo")` en vez de `["titulo"]` (pedido del enunciado), una
    opción de tarea sin título queda afuera de las candidatas en vez de
    romper la corrida con un `KeyError` -- probado directo, con una lista de
    opciones armada a mano, sin necesitar un escenario ni Postgres.

  RED (`git stash push -- tests/banco/corrida.py`, con las pruebas ya
  escritas): `tests/banco/test_corrida.py -k "resolver_toque_generico or
  candidatas_tarea_por_titulo"` -> error de colección (`ImportError:
  cannot import name '_candidatas_tarea_por_titulo'`) -- las funciones
  nuevas todavía no existían. `git stash pop` restauró la implementación.

  GREEN:
  - `tests/banco/test_corrida.py -k "resolver_toque_generico or
    candidatas_tarea_por_titulo"` -> `6 passed`.
  - `tests/banco` -> `197 passed, 108 deselected`.

  Abierto:
  - Ninguna de las tres correcciones tocó `src/` ni el esquema -- las tres
    eran del arnés del banco.
  - `_pendiente_para_confirmar` (el paso de Confirmar, distinto del toque
    genérico y de la aclaración) sigue con `order by creado_en desc limit 1`
    sin desempate -- fuera del pedido de esta unidad (el enunciado nombraba
    sólo `_pendiente_actual` y `_aclaracion_para_elegir`); no se tocó. Mismo
    tipo de hallazgo, potencialmente, si alguna vez dos herramientas que
    piden confirmación quedan esperando a la vez en el mismo chat.

**Verificación final de las tres unidades (suite completa):**
`.venv/Scripts/python.exe -m pytest -q` -> `856 passed, 108 deselected`
(línea base 848 + 8 pruebas nuevas: 2 del rechazo de preparación, 3 del
texto con opciones, +3 netas del banco -- 6 nuevas de `_resolver_toque_
generico`/`_candidatas_tarea_por_titulo` menos 3 quitadas de
`_pendiente_actual`), 200s.

- 2026-09-26: **Ocho correcciones de seguimiento sobre revisiones ya
  aprobadas.** Ruta: delegada, un escritor, unidades separadas para que el
  orquestador commitee cada una aparte. Línea base 856 passed, 108
  deselected.

  **(a) Un solo juego de botones por turno (`agente._ejecutar_una`).**
  Si el modelo llamaba a `ofrecer_opciones` más de una vez en el mismo
  turno, `responder` sólo encolaba `opciones_pendientes[0]`, pero
  `_ejecutar_una` le devolvía a CADA llamada el mismo texto de éxito ("Le
  voy a mostrar los botones...") -- una mentira al modelo para la segunda
  llamada, que nunca se mostró. Corrección: si `opciones_pendientes` ya
  tiene una entrada, una llamada de más se rechaza con
  `is_error: true` ("ya ofreciste opciones en este turno; no se mostraron
  estas") y no se suma ni a `elecciones` ni a `opciones_pendientes` (ADR
  0007, ninguna herramienta nueva, ningún marcador nuevo). Archivo:
  `src/prisma/agente.py`. Prueba:
  `tests/test_opciones_modelo.py::test_segunda_llamada_a_ofrecer_opciones_en_el_mismo_turno_no_se_muestra`
  (dos llamadas en la misma vuelta; verifica `r.elecciones == ["ofrecer_opciones"]`,
  una sola `pending_action`, y que el segundo `tool_result` sea
  `is_error: true` con la explicación).
  RED (código revertido con `git stash`): `1 failed` (elecciones duplicada).
  GREEN: `tests/test_opciones_modelo.py` -> `17 passed`; barrido
  (`test_agente.py test_opciones_modelo.py test_menu_tarea.py
  test_lista_botones.py test_pregunta_sin_opciones.py tests/banco`) ->
  `289 passed, 108 deselected`.

  **(b) El Confirmar por botón auditaba un rechazo como ejecutado
  (`gateway.py` ~426-462, mismo defecto de fondo que el ya corregido en
  `agente._ejecutar_una`).** Al confirmar (`ya_confirmada=True`),
  `H.ejecutar` puede devolver sin excepción el rechazo de negocio de
  `preparar` corrido de nuevo (la situación cambió entre la vista previa y
  el toque, sin llegar a `EstadoCambio` porque la huella puede seguir
  coincidiendo) -- el código auditaba `herramienta:<nombre>`
  INCONDICIONALMENTE antes de mirar si el resultado era en realidad ese
  rechazo. Corrección: se decide primero si `resultado` es un rechazo
  (`error`/`cerrada is False`/`iniciada is False`, la misma detección que ya
  usaba el mensaje de abajo); si lo es, se audita
  `herramienta_rechazada:<nombre>` y el mensaje a la persona es el motivo
  específico (`falta`/`error`, mismo criterio que
  `_mensaje_resultado_menu`) en vez del genérico "No se aplicó el cambio.";
  si no, sigue el camino de siempre (`herramienta:<nombre>`, "Hecho."/borrador).
  Archivo: `src/prisma/gateway.py`. Prueba nueva en `tests/test_botones.py`
  (`test_confirmar_una_preparacion_que_rechaza_no_se_audita_como_ejecutada`):
  crea una dependencia bloqueante DESPUÉS de armar la vista previa de
  `actualizar_estado` (mismo `tarea_id`/`estado`, huella sin cambiar) y
  confirma por HTTP -- verifica cero filas `herramienta:actualizar_estado`,
  una `herramienta_rechazada:actualizar_estado` con el rechazo en el
  detalle, la tarea intacta y el mensaje sin "Hecho.".
  RED: `1 failed` (`n == 1` en vez de `0` para `herramienta:actualizar_estado`).
  GREEN: `tests/test_botones.py` -> `11 passed`; barrido (`test_botones.py
  test_menu_tarea.py test_vista_previa_confirmacion.py test_dependencias.py
  test_bloqueos.py test_autoridad_tarea.py test_agente.py test_task_intake.py
  test_task_drafts.py`) -> `253 passed`.

  **(c) Falsos positivos de `deteccion_pregunta.py`.** Tres correcciones,
  sin tocar los casos reales que ya protegía el banco
  (`tests/banco/test_comprobadores.py`, sin cambios, `101 passed` junto con
  las pruebas nuevas): un "?" dentro de una URL (`?id=5&modo=ver`) ya no
  cuenta como pregunta (se descarta la URL, `https?://\S+|www\.\S+`, antes
  de buscar "?"); "elegi"/"cual" pasan a buscarse con borde de palabra
  (`\belegi\b`, `\bcual\b`) en vez de subcadena, así que "elegido"/"elegida"/
  "elegimos"/"elegible" y "cualquier"/"cualquiera" dejan de disparar un
  pedido de elección falso. Archivo: `src/prisma/deteccion_pregunta.py`.
  Pruebas nuevas en `tests/test_deteccion_pregunta.py` (URL con "?", pregunta
  real junto a una URL sigue contando, las cuatro formas de "elegi" como
  subcadena, dos formas de "cualquier"). RED: `3 failed` (las tres exactas).
  GREEN: `tests/test_deteccion_pregunta.py tests/banco/test_comprobadores.py`
  -> `101 passed`; barrido (+ `test_pregunta_sin_opciones.py test_agente.py
  tests/banco test_task_intake.py`) -> `324 passed, 108 deselected`.

  **(d) `gateway._mostrar_tareas_propias` (T4b): tres correcciones.**
  1. Se agregó `menu_tarea.tareas_activas_de_persona` -- la regla
  compartida de "tarea activa" (`estado not in ('terminada','cancelada')`),
  con `excluir_tarea_id`/`limite` opcionales -- y tanto `tareas_activas_de`
  (T2, elección de dependencia) como `_mostrar_tareas_propias` la llaman en
  vez de cada una tener su propia consulta duplicada. 2. Orden
  determinístico: se agrega `id` como segundo criterio después de
  `fecha_objetivo nulls last` (antes, sin desempate, el orden entre tareas
  sin fecha o con la misma fecha dependía del orden físico de Postgres).
  3. El `limit 25` que cortaba en silencio se saca: se piden TODAS las
  tareas activas y se pagina con el armador ya existente de T3
  (`agente._opciones_lista_tareas`, "Ver más" con el resto) -- los ids
  viajan en `pending_action_option.valor` (columna del servidor), nunca en
  el `callback_data` de Telegram, así que no hay límite de payload que una
  página más pueda superar. Además: "Es una tarea nueva" ya no se ofrece en
  el cierre genérico cuando `entrante_id is None` (un turno resumido desde
  un toque, p. ej. `_resolver_toque_opcion_modelo` llama a `responder` sin
  `entrante_id`) -- ese botón tiene garantizado fallar
  (`_iniciar_alta_guiada` exige un `inbound_message` persistido y levanta
  antes de intentar nada sin uno); sólo quedan las otras dos opciones.
  Archivos: `src/prisma/menu_tarea.py`, `src/prisma/gateway.py`,
  `src/prisma/agente.py`. Pruebas nuevas/adaptadas en
  `tests/test_pregunta_sin_opciones.py`: `test_sin_entrante_id_no_ofrece_es_una_tarea_nueva`
  (reemplaza la prueba anterior, que esperaba el botón ofrecido y fallando
  recién al tocarlo);
  `test_tocar_es_sobre_una_tarea_existente_pagina_mas_alla_del_limite_viejo`
  (26 tareas, todas visibles tocando "Ver más" las veces que hagan falta);
  `test_tocar_es_sobre_una_tarea_existente_orden_deterministico_sin_fecha`
  (5 tareas sin fecha, dos corridas independientes, mismo orden). Dos
  pruebas existentes (`test_pedido_de_eleccion_en_imperativo_tambien_agrega_el_cierre`,
  `test_pregunta_larga_se_parte_y_los_botones_van_aparte`) se adaptaron para
  pasar `entrante_id` (su propósito no era este botón, así que se preserva
  el caso de 3 opciones que ya probaban). RED: `2 failed` (paginación
  cortada en 25; botón ofrecido sin `entrante_id`). GREEN:
  `tests/test_pregunta_sin_opciones.py` -> `16 passed`; barrido (+
  `test_menu_tarea.py test_lista_botones.py test_dependencias.py
  test_autoridad_tarea.py test_agente.py test_opciones_modelo.py
  test_botones.py tests/banco`) -> `348 passed, 108 deselected`.
  **Regresión de barrido completo encontrada aparte** (no en el barrido de
  la unidad, en la suite completa):
  `tests/test_task_intake.py::test_no_mutating_tool_output_is_truth_marked_and_has_no_buttons`
  esperaba las 3 opciones del cierre genérico sin pasar `entrante_id` --
  adaptada a esperar sólo las 2 que corresponden ahora (su propósito, que
  "Confirm?" del modelo nunca termine en una confirmación real, no cambió).

  **(e) `test_rechazo_de_preparacion_no_bloquea_una_ejecucion_real_despues`
  (tautológica) reemplazada.** La versión anterior escribía ELLA MISMA la
  fila `herramienta:crear_dependencia` con `registrar_auditoria` en vez de
  producirla por un camino real -- no probaba nada que `_ejecutar_una`/
  `gateway._toque` pudieran romper. Reemplazada por dos pasos reales con la
  MISMA herramienta: (1) el modelo llama `crear_dependencia` con un destino
  inexistente, vía `agente.responder` -- se audita
  `herramienta_rechazada:crear_dependencia` y el modelo recibe
  `is_error: true`; (2) el modelo la llama de nuevo con argumentos válidos
  -- queda esperando Confirmar -- y la persona confirma por botón, el mismo
  camino HTTP de `gateway._toque` (unidad (b) de esta sesión). Sólo la
  segunda escribe la fila `dependency` y se audita
  `herramienta:crear_dependencia`. Archivo: `tests/test_agente.py`.
  Decisión de implementación: la vista previa (paso 2) se arma con
  `ahora=datetime.now(timezone.utc)` real, no la `AHORA` fija en el pasado
  que usa el resto del archivo -- si no, la `pending_action` ya está
  `vencida` para cuando el toque HTTP (que sí usa la hora real) intenta
  resolverla. Verificado que la prueba pasa igual contra el código previo a
  las unidades (a)/(b) de esta sesión (no depende de ninguna de las dos:
  reemplaza el antipatrón, no fija un defecto nuevo de esas dos). GREEN:
  `tests/test_agente.py` -> `2 passed` (la nueva + su vecina de rechazo);
  barrido (`test_agente.py test_dependencias.py test_botones.py
  test_vista_previa_confirmacion.py`) -> `72 passed`.

  **(f) Prueba multi-vuelta para `agente.py`: qué texto queda con las
  opciones.** Cobertura, no corrección -- el código ya elegía bien
  (`texto_al_ofrecer`, fijado la primera vez que crece
  `opciones_pendientes`, nunca sobrescrito por una vuelta posterior). Prueba
  nueva: dos vueltas, la primera llama a `ofrecer_opciones` con un texto que
  describe contexto, la segunda (sin llamadas, cierra el turno) repite un
  relleno ("Listo, ahí tenés las opciones.") -- se verifica que el texto
  que viaja con los botones es el de la PRIMERA vuelta. Archivo:
  `tests/test_opciones_modelo.py`
  (`test_texto_de_una_vuelta_posterior_a_ofrecer_opciones_se_descarta`).
  Comprobado por mutación (no por RED, la implementación ya era correcta):
  se cambió `texto_al_ofrecer` por `salida` (el último texto del turno) en
  `agente.responder`, la prueba nueva pasó a fallar con el texto de relleno
  en vez del real, se restauró la línea. GREEN:
  `tests/test_opciones_modelo.py` -> `18 passed`.

  **(g) Banco: `_pendiente_para_confirmar` sin el mismo filtro de corrida
  que ya tenían `_resolver_toque_generico`/`_aclaraciones_para_elegir`
  (hallazgo del orquestador).** Las tres funciones resuelven contra
  acciones pendientes 'esperando' de un chat; sólo las últimas dos ya
  restringían la unión a lo creado durante la corrida actual (unidad previa
  del 2026-09-26). Se agrega `desde` (capturado con `clock_timestamp()` de
  Postgres, no `now()` -- `now()` queda fijo al inicio de la transacción y
  no serviría para el corte -- justo antes de correr los mensajes del
  escenario) a las tres funciones: `creado_en >= desde` en la consulta, y
  `_pendiente_para_confirmar` pasa de "la última por `order by` " a la
  UNIÓN + ambigüedad (más de una `pending_action` distinta que ofrezca
  Confirmar en esta corrida levanta `LookupError`, igual criterio que
  `_resolver_toque_generico`) en vez de adivinar con
  `order by creado_en desc limit 1`. Archivo: `tests/banco/corrida.py`
  (sólo `tests/banco/`, sin tocar `src/` ni el esquema). Pruebas nuevas en
  `tests/banco/test_corrida.py`: exclusión de una pendiente anterior a
  `desde` (dos, una por función) y ambigüedad con dos pendientes de esta
  corrida (dos, una por función); las pruebas existentes de las tres
  funciones se actualizaron para pasar el parámetro nuevo (`_MUY_ANTES`,
  una fecha del año 2000, cuando el filtro no es lo que se está probando).
  RED (`git stash` de `corrida.py`): `12 failed`
  (`TypeError: takes N positional arguments but N+1 were given`, las nueve
  llamadas ya adaptadas más las tres pruebas nuevas). GREEN:
  `tests/banco/test_corrida.py` -> `53 passed`; `tests/banco` ->
  `201 passed, 108 deselected`.

  **(h) Investigación: `b-0005-b` falla 3/3 en todo banco real (evidencia:
  `tests/banco/reportes/replay-candidato-b-0005-b-{0,1,2}.json`).**

  Causa real, verificada replayando las tres grabaciones
  (`tests/banco/replays/`, temporal, borrado después) contra
  `tests/banco/test_replays.py`: el router clasificó correctamente el
  mensaje ("che, anota q lo del cableado del tablero depende de q termine
  primero el plc") como `normal_conversation`, con dos `trabajos` a
  resolver ("lo del cableado del tablero", "el plc"). Jev resolvió "lo del
  cableado del tablero" CLARA (T2, 0,99 de probabilidad) pero "el plc" sólo
  llegó a 0,76 de probabilidad / 0,53 de confianza para T1 -- por debajo de
  `jev.CORTE_CLARA = 0,85` -- así que quedó AMBIGUA. Con una referencia
  ambigua y candidatas reales, el servidor abre la aclaración con botones
  (ADR 0006) ANTES de llegar a `agente.responder`: el modelo nunca se llega
  a consultar (`"respuestas": []` en la grabación) y `crear_dependencia`
  nunca se llama. El escenario `b-0005-b.yaml` no declara
  `aclaracion_esperada` ni un toque que conteste esa pregunta, así que la
  corrida termina ahí, con `herramientas: []` y sin la dependencia --
  exactamente el `falla` que reporta cada corrida real.

  **Esto es comportamiento de Jev (el modelo), evaluado contra un umbral ya
  codificado a propósito (`CORTE_CLARA`), no un defecto de Prisma ni del
  router** -- "el plc" es una referencia genuinamente informal para
  "Programar PLC de la comprimidora (simulado)" y Jev no llegó al 85% que
  exige el diseño para no preguntar. **No se cambiaron las expectativas del
  escenario** (sigue esperando `crear_dependencia`/la dependencia, con
  severidad "media"): documentar que Jev necesita más contexto o ajustar el
  umbral es una decisión de producto/tuning que excede esta investigación,
  no un código a corregir. `b-0005-b` sigue confirmando lo mismo que
  documentó su creación: la variante de redacción no cambia el resultado, y
  el motivo real (acá) resultó distinto del defecto histórico documentado
  para `b-0005` (`odd/tasks/banco-conversacional.md`: aquel era el router
  clasificando como `start_task_intake`; éste es la confianza de Jev para
  una referencia terca, con el router ya clasificando bien).

  **Defecto real encontrado y corregido durante la investigación, ajeno al
  veredicto de `b-0005-b`: `ClienteJevGuionado` (una sola cola FIFO) puede
  cruzar las respuestas grabadas entre dos referencias del mismo mensaje.**
  `gateway._resolver_en_paralelo` resuelve cada referencia en su propio
  hilo (`ThreadPoolExecutor`, T3); con una cola compartida, el hilo que
  llega primero a `decidir()` se lleva la respuesta grabada para la
  referencia que sea -- reproducido de forma determinística (5/5): el
  replay de `b-0005-b` pedía siempre la aclaración sobre "lo del cableado
  del tablero" (la CLARA real) en vez de "el plc" (la AMBIGUA real). El
  verdicto final no cambiaba (seguía `falla`), pero un replay tiene que
  reproducir la MISMA resolución, no una intercambiada por el orden de
  scheduling de los hilos -- afecta a cualquier escenario guionado con 2+
  `trabajos` en el mismo mensaje, no sólo a `b-0005-b`. Corrección: nueva
  `ClienteJevGuionadoPorReferencia` (`tests/banco/corrida.py`, sólo el
  arnés de pruebas -- `ClienteJevGuionado` en `src/prisma/jev.py` sigue
  igual, la usan decenas de pruebas unitarias de una sola referencia que no
  tienen este problema) que agrupa las respuestas grabadas por
  `state["referencia"]` en colas propias, con lock; `jev_guionado_desde_grabacion`
  la usa en vez de una `ClienteJevGuionado` plana. Pruebas nuevas en
  `tests/banco/test_corrida.py`: mapeo correcto sin importar el orden de
  llamada; una referencia agotada no afecta a otra; registro de pedidos
  intacto; y una de punta a punta contra `gateway._resolver_en_paralelo`
  real (20 repeticiones) con las probabilidades reales de la grabación de
  `b-0005-b`, verificando que "el plc" siempre sale AMBIGUA y "lo del
  cableado del tablero" siempre CLARA→T2. Dos pruebas existentes
  (`test_jev_grabacion_json_es_serializable_y_recargable`,
  `test_jev_grabacion_vieja_sin_clave_jev_sigue_cargando`) se actualizaron
  para el tipo nuevo. Comprobado por mutación: con la clase vieja
  (`ClienteJevGuionado` plana) en la prueba de punta a punta, "el plc" sale
  CLARA→T2 (cruzada) -- falla exactamente como se esperaba; restaurada la
  clase nueva. RED (función revertida a la cola plana): `2 failed`
  (las dos pruebas adaptadas, por `isinstance`). GREEN:
  `tests/banco/test_corrida.py -k jev` -> `7 passed`; `tests/banco` ->
  `205 passed, 108 deselected`.

  **Verificación final de las ocho unidades:**
  `.venv/Scripts/python.exe -m pytest -q` -> primera corrida `1 failed,
  872 passed, 108 deselected` (regresión real de la unidad (d) sobre
  `test_task_intake.py`, corregida arriba); segunda corrida ->
  `873 passed, 108 deselected` (línea base 856 + 17 pruebas nuevas: 1(a) +
  1(b) + 5(c, 5 nuevas) + 3(d, netas: 1 reemplazada + 2 nuevas) + 0(e,
  reemplazo sin cambiar la cuenta) + 1(f) + 4(g) + 6(h, netas: 4 nuevas +
  2 adaptadas sin cambio de cuenta), 208s en total.

  Abierto (ninguno bloquea T5):
  - `b-0005`/`b-0005-b`: siguen documentados como fallas reales del banco,
    de origen distinto (router vs. confianza de Jev) -- **PENDIENTE** de
    una decisión de producto sobre `jev.CORTE_CLARA` o sobre enriquecer el
    contexto que recibe Jev para referencias informales de una sola
    palabra clave ("el plc"), fuera del alcance de esta sesión.
  - Mismas brechas fuera de alcance de unidades anteriores sin cambios:
    autoridad para `cancelada` (T2b), "Adjuntar evidencia" del aprobador en
    el menú (T2).
  - No se corrió el banco real (`-m modelo_real`) en esta sesión.

- 2026-09-26: **T5, parte documental cerrada.** Ruta: inline (documentación pura, sin
  cambio de lógica, esquema, dependencias ni arquitectura, `AGENTS.md`). Verificado
  contra el código, git y el banco antes de escribir; nada se afirmó sin evidencia.

  Archivos:
  - `docs/STATUS.md`: fecha de actualización, hecho de commits/rama corregido (67
    commits en `main`, renombrada desde `master` el 2026-09-25, sin push — no "un
    único commit `efa8ee2`"), tabla de línea base de pruebas actualizada (876 passed,
    108 deselected, 2026-09-26), sección nueva "Cerrado: Prisma orienta (T1-T4b)" con
    la evidencia de suite y banco real, y "Próximo paso" reescrito.
  - `docs/capacidades.md`: la fila "Prisma orienta con opciones (parcial)" pasa a
    fila completa con lo construido en T2/T3/T4b (menú, listas con "Ver más", cierre
    genérico); autoridad sobre la propia tarea anota el hueco de `cancelada`; fallas
    con aviso y trazabilidad describe `notificado_en` correcto y
    `herramienta_rechazada:<nombre>`.
  - `docs/decisions/0007-prisma-orienta-no-charla.md`: "Pendiente" registra la
    decisión del usuario del 2026-09-26 (cierre genérico con tres opciones) como
    resuelta, y dejó explícito que "cerrar sin preguntar nada, sin botones" es el
    comportamiento implementado hoy, no una confirmación explícita del usuario —
    sigue esa confirmación como pendiente real.
  - `docs/architecture/interpretacion-y-confirmacion.md` §4.5: bullet nuevo marcando
    T1-T4b construidos con el rango de commits, remitiendo a §4.6 y dejando
    `cancelada`, "Adjuntar evidencia" del aprobador y la segunda sesión como
    pendientes.
  - `docs/validation/README.md`: sección "Banco conversacional" gana `toques`,
    `permite_pregunta_sin_opciones`, el comprobador `comprobar_pregunta_con_opciones`,
    `bloqueado` por fallo del proveedor, y que la aclaración acepta una opción de
    tarea ofrecida por el modelo.
  - `odd/tasks/prisma-orienta.md` (este archivo): T5 dividida en su parte documental
    (hecha) y la sesión por Telegram (pendiente); esta entrada de Progreso; "Próximo
    paso al retomar" reescrito.

  Verificación:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_capacidades.py` (`pg_isready`
    antes) -> `3 passed` (cruza `docs/capacidades.md`/`PROMESAS_SIN_CUMPLIR` contra el
    esquema; no falla con la reescritura de la fila de Prisma orienta).
  - `.venv/Scripts/python.exe -m pytest -q` (suite completa, reejecutada para esta
    unidad) -> `876 passed, 108 deselected` (206 s) — confirma el número que ya
    figuraba como hecho de la sesión.
  - `tests/banco/reportes/banco-20260926T155611Z.json` releído y agregado en Python:
    84 aprobado, 3 falla, 21 no_concluyente, 0 bloqueado de 108; la única falla es
    `b-0005-b` (3/3) — confirma el hecho de la sesión antes de llevarlo a `STATUS.md`.
  - `git log`/`git branch -a`/`git rev-list --count HEAD`/`git ls-remote --heads
    origin`: rama `main`, 67 commits, HEAD `9681973`, remoto sin ninguna rama —
    confirma el hecho de la sesión antes de reemplazar la línea vieja de
    `docs/STATUS.md`.
  - `db/migrations/`: sin ninguna migración posterior a `0011` — confirma "sin cambio
    de esquema esta sesión".

  No verificable / no verificado en esta unidad (queda `PENDIENTE`, no se inventó):
  - Los 7 ids de revisión RDD que el orquestador entregó como hecho de la sesión
    (`review-4a429367dd7cfdc8`, `review-231a98f5d94099c9`, `review-d81552b4b65f4be5`,
    `review-42b7c7c32af6e755`) no aparecen en `odd/tasks/prisma-orienta.md` ni en
    ningún mensaje de commit de este repositorio (`git log --all`, buscado); sólo hay
    evidencia escrita de cinco (`review-995bc30d2d0df7e8`, `review-9ac0b4b8afec17ee`,
    `review-112e1420d47dd637`, `review-0ea0c4be83f8e6d9`, `review-356a9a31c3d84353`,
    todos ya registrados arriba en este documento). No se escribió ningún id sin
    evidencia en `docs/STATUS.md`.
  - El commit `9681973` ("fix: keep a question that ends with a link and ignore words
    inside links") no tiene una entrada de unidad propia en este documento — su
    trabajo (URLs terminando en "?", palabras dentro de una URL) extiende la
    corrección (c) de la sesión anterior, y sus 3 pruebas nuevas explican la
    diferencia entre el `873 passed` de esa sección y el `876 passed` verificado
    arriba, pero no se reconstruyó su RED/GREEN ni sus decisiones de diseño porque no
    se registraron en su momento. Al usuario le puede convenir completar esa entrada
    o confirmar que el registro de esta corrección quedó incompleto a propósito.

- 2026-09-26 (orquestador): **registro que faltaba de revisiones y del commit `9681973`**
  (lo señaló el escritor de T5; la evidencia son las salidas de `gentle-ai review` de esta
  sesión, que no habían quedado escritas acá).
  - `review-4a429367dd7cfdc8` sobre `d193b61` (aclaración con `ofrecer_opciones`,
    desempate, exclusión): una lente (fiabilidad), aprobada y reconocida. Observaciones:
    `ctid` no es orden de inserción; `_aclaracion_para_elegir` sin desempate; `KeyError`
    sin `titulo` -> corregidas en `e0de2d4` y `633ec39`.
  - `review-231a98f5d94099c9` sobre `6ef68cb`/`76341fe` (T4b), riesgo alto, cuatro lentes,
    aprobada y reconocida. Observaciones: falsos positivos del detector en producción,
    "Es una tarea nueva" sin `entrante_id`, límite 25 silencioso y regla de tarea activa
    duplicada en `_mostrar_tareas_propias` -> corregidas en `ad8a48b` y `fd1287c`.
  - `review-d81552b4b65f4be5` sobre `86a40c6`/`e0de2d4`: una lente (fiabilidad), aprobada y
    reconocida. Observaciones: `ofrecer_opciones` repetido en un turno, prueba
    tautológica, unión de toques con acciones viejas, ronda de texto sin prueba ->
    corregidas en `fd1287c` y `633ec39`.
  - `review-42b7c7c32af6e755` sobre `ad8a48b`/`fd1287c`/`633ec39` (unidad de cierre),
    riesgo alto, cuatro lentes, aprobada y reconocida; frontera de revisión en `633ec39`.
    Observaciones: el "?" pegado al final de una URL se perdía (falso negativo) y la señal
    imperativa seguía mirando dentro de las URLs -> corregidas en `9681973`; quedan como
    sugerencias menores sin corregir: comentarios con referencias a la sesión ("esta
    unidad", "hallazgo del orquestador") en `menu_tarea.py`, `gateway.py` y
    `tests/banco/corrida.py`; import local y referencia a líneas en
    `tests/test_agente.py:554-559`; la prueba de orden determinístico de
    `tests/test_pregunta_sin_opciones.py:500-528` no prueba el desempate.
  - `9681973` (orquestador, inline): `_URL` ya no se lleva la puntuación final de la
    frase; `hace_pregunta` cuenta también "¿"; `pide_elegir_en_imperativo` descarta las
    URLs antes de buscar. RED: `tests/test_deteccion_pregunta.py` -> `3 failed, 9 passed`.
    GREEN: `tests/test_deteccion_pregunta.py tests/banco/test_comprobadores.py
    tests/test_pregunta_sin_opciones.py` -> `120 passed`; suite completa -> `876 passed,
    108 deselected` (208 s). Evaluación RDD `--base-ref 633ec39`: `medium`, 52 líneas,
    `under_budget` (pendiente en el tramo).

- 2026-09-26 (orquestador, inline): **las tres sugerencias menores pendientes de
  `review-42b7c7c32af6e755` quedaron corregidas.**
  - Comentarios con referencias a la sesión ("esta unidad", "hallazgo del
    orquestador", "revisión del orquestador") en `menu_tarea.py`, `gateway.py` y
    `tests/banco/corrida.py`: reescritos para que cada uno diga la razón en términos
    del código (por ejemplo, por qué `id` desempata en `tareas_activas_de_persona`),
    sin tocar las referencias durables a ADR/T-labels/commits (ADR 0007, T1-T6,
    `0814fa3`).
  - `tests/test_agente.py`: el `from datetime import timezone` a mitad de función se
    movió al import de módulo (`from datetime import datetime, timezone`); la
    referencia a `gateway.py ~426-462` en el docstring pasó a nombrar la rama real
    (`gateway._toque`, la que llama a `H.ejecutar` con `ya_confirmada=True`).
  - `tests/test_pregunta_sin_opciones.py`: la prueba de orden determinístico no
    ejercitaba el desempate -- ni siquiera tocaba "Es sobre una tarea existente", así
    que comparaba dos veces el mismo menú fijo de cierre genérico. Se reemplazó por
    `test_tocar_es_sobre_una_tarea_existente_orden_deterministico_por_id`: cuatro
    tareas con `id` explícito (`_tarea` ahora acepta `tarea_id` y `fecha_objetivo`),
    dos con la misma `fecha_objetivo` y dos sin ninguna, insertadas en un orden que no
    coincide con el esperado; se toca el botón real y se compara la lista resultante
    contra el orden `(fecha_objetivo nulls last, id)` calculado a mano.
  - Prueba de mutación (registrada tal como se pidió): se quitó `, id` del `order by`
    en `menu_tarea.tareas_activas_de_persona` y se corrió sólo la prueba nueva ->
    `1 failed` (`'Con fecha, id alto' != 'Con fecha, id bajo'`, el orden pasó a
    depender de la inserción). Se restauró el `order by fecha_objetivo nulls last,
    id` y se volvió a correr -> `1 passed`.
  - Verificación: `tests/test_pregunta_sin_opciones.py tests/test_agente.py` -> `37
    passed`; suite completa -> `876 passed, 108 deselected` (205 s), igual que la
    base registrada arriba. Sin cambio de comportamiento en `src/`: sólo comentarios y
    docstrings.

- 2026-09-26 (orquestador): commits `ec41640` (comentarios) y `fc4b5db` (prueba del
  desempate). Evaluación RDD `--base-ref 633ec39`: `medium`, 623 líneas,
  `slice_budget_reached` (incluye `9681973` y `dd031a9`). Revisión con consentimiento del
  usuario, una lente (fiabilidad), aprobada y reconocida (`review-6333bc5a1ab13726`); la
  frontera de revisión avanza a `fc4b5db`. Observaciones:
  - `tests/test_pregunta_sin_opciones.py:535-538` (advertencia): ids literales con
    `commit` podían chocar si la prueba se repetía sobre la misma base -> corregido en
    `9896ba7` con cuatro `uuid4` al azar, ordenados (el orden de texto en minúsculas
    coincide con el orden de `uuid` en PostgreSQL); la prueba pasó tres veces seguidas.
  - `src/prisma/deteccion_pregunta.py:49` (sugerencia, aceptada sin cambio): una URL cuyo
    último carácter sea su propio "?" (query vacía) seguida de más texto deja ese "?"
    afuera y cuenta como pregunta. Caso raro; el costo es un cierre genérico de más, no
    una respuesta perdida.

- 2026-09-27 (orquestador): **Sesión 2 por Telegram, hallazgo 1 -- botones de una
  lista armada con varias consultas mostraban sólo la última.** Evidencia en
  `audit_log`: Ismael escribió "quiero ver todas las tareas que hay para el
  equipo"; el modelo llamó a `consultar_tareas` 7 veces en el mismo turno -- una
  sin filtro (sus propias tareas: ninguna) y una por cada una de las 6 personas
  del equipo (`responsable=<nombre>`). El texto de la respuesta nombró las 12
  tareas de todo el equipo, pero los botones sólo ofrecían las 2 de Ariel (+
  salida), porque `agente.responder`/`_ejecutar_una` (T3, ADR 0007 punto 3)
  guardaban sólo las filas de la ÚLTIMA llamada a `consultar_tareas` que trajo
  algo ("gana la última con filas"), no las de todas.

  **Cambio de regla (decisión del orquestador):** se acumulan las filas de TODAS
  las llamadas a `consultar_tareas` del turno que devolvieron algo -- unión
  deduplicada por id de tarea, en orden de primera aparición -- en vez de
  quedarse con la última. El resto de T3/T3a no cambia: paginado con "Ver más" (4
  por página), el texto largo se sigue partiendo aparte de los botones, y nunca
  compiten dos juegos de botones en el mismo turno. Motivo: el modelo arma una
  lista de "todo el equipo" con varias consultas encadenadas (una por persona),
  no con una sola llamada amplia -- la regla vieja asumía lo segundo.

  **Costo aceptado:** una consulta amplia seguida de una más angosta (p. ej. "mis
  tareas" sin filtro, después "las de Ariel" por otra razón dentro del mismo
  turno) ahora deja ambas en los botones -- de más, nunca de menos. Antes el
  costo era el inverso y más grave: tareas que el texto nombraba desaparecían de
  los botones sin aviso.

  Se renombró el acumulador `ultima_lista_tareas` a `tareas_listadas` (ya no
  describe "la última", sino la unión) y se actualizaron los comentarios que
  explicaban la regla vieja en `src/prisma/agente.py` (declaración cerca de
  `responder`, `_ejecutar_una`, y los docstrings de `_opciones_lista_tareas`;
  `_encolar_respuesta_con_tareas` no mencionaba la regla vieja, no hizo falta
  tocarlo).

  Archivos:
  - `src/prisma/agente.py`: acumulación por unión deduplicada (ver arriba) y
    renombre `ultima_lista_tareas` -> `tareas_listadas`.
  - `tests/test_lista_botones.py`: `test_ultima_llamada_con_filas_gana` (afirmaba
    la regla vieja a propósito) se reemplazó por
    `test_varias_llamadas_con_filas_se_unen_por_orden_de_aparicion`, que reproduce
    la forma real del turno de Ismael (una consulta sin filtro vacía + varias por
    persona, con una repetida) y prueba la unión en orden de primera aparición,
    con paginado "Ver más" al pasar de 4. El docstring de la prueba nueva deja
    explícito que es un cambio de regla, no un debilitamiento.

  - RED (con `agente.py` sin el cambio, `tests/test_lista_botones.py` con la
    prueba nueva): `1 failed` -- los botones traían sólo la última consulta
    ("Tarea Lucas 5"), no la unión.
  - GREEN: `tests/test_lista_botones.py tests/test_agente.py
    tests/test_opciones_modelo.py tests/test_pregunta_sin_opciones.py` -> `67
    passed`; suite completa -> `876 passed, 108 deselected` (233 s), igual que la
    base registrada arriba.

- 2026-09-27 (orquestador): **Sesión 2 por Telegram, hallazgos 2, 3 y 4.**
  Confirmados por el usuario sobre la misma sesión real que dio el hallazgo 1.

  **Hallazgo 2 -- el saludo hacía dos preguntas seguidas.** Evidencia: "¿En qué
  te ayudo? ¿Por dónde arrancamos?" y, en otra vuelta, "¿Con qué te doy una
  mano? ¿Qué necesitás?". Regla nueva en `contexto.PREAMBULO`: una respuesta
  nunca hace más de una pregunta en el mismo turno -- si va a llamar a
  `ofrecer_opciones`, esa pregunta (con sus botones) es la única, sin otra en
  el texto que la acompaña. Archivo: `src/prisma/contexto.py`. Prueba:
  `tests/test_opciones_modelo.py::test_reglas_del_contexto_piden_ofrecer_opciones`,
  assertion nueva sobre `"más de una pregunta" in PREAMBULO.lower()`. RED
  verificado a mano contra el `PREAMBULO` de `HEAD` (sin la frase, `False`);
  GREEN: `1 passed` (42 s, incluye la construcción de contexto contra
  PostgreSQL).

  **Hallazgo 3 -- etiquetas de botón truncadas a mitad de palabra.** Evidencia:
  "Revisar comunicaciones industriales de la compr…" (recorte de
  `salida.TRUNCAR_ETIQUETA_BOTON`, 48 caracteres, a mitad de "compresora").
  Los títulos de tarea de la sesión terminaban en " (simulado)"; no se trató
  como caso especial -- el corte por límite de palabra simplemente lo deja
  afuera la mayoría de las veces, igual que cualquier otro sufijo largo.

  Decisiones:
  - `salida.OBJETIVO_ETIQUETA_BOTON = 30`: un botón inline de Telegram ocupa
    el ancho del chat; en una pantalla de referencia angosta (iPhone SE,
    ~320pt) el texto de un botón con su padding entra sin ajustar renglón
    hasta unos 28-32 caracteres con la tipografía de sistema -- 30 queda en
    el medio, con margen para acentos y mayúsculas más anchas. Bastante más
    chico que `TRUNCAR_ETIQUETA_BOTON` (48), que pasa a ser sólo el último
    recurso: cuando ni una palabra entera entra en el objetivo, o para
    desambiguar dos títulos que colisionan.
  - `salida.acortar_etiqueta_boton(texto, *, objetivo=30, limite=48)`: corta
    en el último límite de palabra que entra en `objetivo`; sin "…" si no
    hizo falta cortar nada; si la primera palabra sola ya supera `objetivo`,
    cae al corte duro de siempre (`truncar_etiqueta_boton`) en vez de dejar
    una etiqueta vacía.
  - `salida.etiquetas_boton_distinguibles(titulos, *, fijas=None)`: la
    versión de CONJUNTO -- si acortar dos títulos distintos los deja
    iguales (el propio ejemplo del usuario: "...máquina 3" y "...máquina 4"
    cortando los dos en "...máquina…"), las que colisionan se extienden
    palabra por palabra, contra todo el conjunto, hasta `limite` (48).
    `fijas[i]` marca una etiqueta que ya vino elegida (la que puso el modelo
    en `ofrecer_opciones`): nunca se hace crecer, sólo cuenta como obstáculo
    para que las demás no la pisen. Último recurso si dos títulos son
    indistinguibles incluso enteros: se numeran (` (2)`, ` (3)`...) -- nunca
    dos botones ambiguos en el mismo mensaje.

  Aplicado a los seis lugares que arman botones de tarea a partir de un
  título: `agente._opciones_lista_tareas` (T3, primera página) y
  `gateway._mostrar_mas_tareas` (T3, "Ver más") corren
  `etiquetas_boton_distinguibles` sobre toda la página; `gateway.
  _mostrar_tareas_propias` reusa `_opciones_lista_tareas`;
  `gateway._candidatas_para_botones` (aclaración con botones, T4) ahora
  acorta y desambigua los títulos como un solo conjunto ANTES de repartirlos
  entre propias/ajenas -- `_etiqueta_boton` sólo agrega el sufijo `— nombre`
  sobre el título ya corto, nunca lo vuelve a truncar;
  `gateway._pedir_eleccion_dependencia` (candidatas de dependencia, T2) igual;
  `herramientas._ofrecer_opciones` (T1) trata la `etiqueta` del modelo como
  fija (obstáculo, nunca se hace crecer) cuando ya es corta (<=
  `OBJETIVO_ETIQUETA_BOTON`), y si falta o es más larga que el objetivo,
  deriva y desambigua a partir de esa base -- una opción de texto libre
  sigue con el corte duro de siempre, sin cambios (T1: "cuando el modelo
  elige su propia etiqueta, está bien").

  Archivos: `src/prisma/salida.py` (funciones nuevas),
  `src/prisma/agente.py`, `src/prisma/gateway.py`, `src/prisma/herramientas.py`
  (los seis sitios de arriba).

  Adaptaciones deliberadas de pruebas existentes (título afectado por el
  cambio de límite, no un debilitamiento):
  - `tests/test_aclaracion_botones.py::test_botones_propia_primero_ajena_con_nombre_y_titulo_truncado`:
    la etiqueta esperada del título largo pasó del corte duro a 48
    (`"Actualizar toda la documentaci…"`, cortado a mitad de palabra) al
    corte por palabra a 30 (`"Actualizar toda la…"`), calculado con
    `salida.acortar_etiqueta_boton` en vez de a mano; docstring nuevo que
    explica el cambio.
  - `tests/banco/test_corrida.py::test_ejecutar_escenario_aclaracion_tapea_la_candidata_elegida_sin_aplicar_nada`:
    mismo motivo -- las candidatas de la aclaración con botones
    (`_SENTINEL_ACLARACION`) ahora son `"Cablear tablero máq. 3…"` /
    `"Revisar tablero máq. 4…"` (el corte por palabra deja afuera
    "(simulado)"), no el título completo. No afecta a `b-0013.yaml` ni a las
    pruebas de `ofrecer_opciones` (`test_ejecutar_escenario_opciones_modelo_
    ofrece_tareas_y_tapea_para_actualizar_estado` y análogas): esas
    resuelven la aclaración por TÍTULO (`valor.titulo`, `_candidatas_tarea_
    por_titulo`), no por etiqueta de botón, así que no les importa cómo se
    acorta la etiqueta visible.

  Pruebas nuevas (RED verificado antes de implementar):
  - `tests/test_salida.py`: `acortar_etiqueta_boton` (no corta si ya entra,
    corta en límite de palabra con "…", primera palabra larga cae al corte
    duro, seguro para `prepare_buttons` con acentos) y
    `etiquetas_boton_distinguibles` (extiende las que colisionan, no toca
    las que no colisionan, respeta `fijas` como obstáculo). RED:
    `ImportError: cannot import name 'OBJETIVO_ETIQUETA_BOTON'`. GREEN:
    `tests/test_salida.py` -> `25 passed`.
  - `tests/test_lista_botones.py::test_titulos_parecidos_y_largos_producen_etiquetas_distintas`:
    circuito de punta a punta de T3 -- dos tareas con títulos parecidos y
    largos ("Revisar tablero de la máquina 3/4") producen etiquetas
    distintas en la misma página de botones. GREEN: `tests/test_lista_botones.py`
    -> `13 passed`.

  Bug encontrado y corregido durante el TDD de `etiquetas_boton_distinguibles`
  (no llegó a versión publicada): la primera implementación comparaba cada
  etiqueta contra `resultado` mientras lo iba mutando en la misma pasada del
  `while` -- la primera etiqueta del grupo que crecía dejaba de "colisionar
  contra sí misma" y las siguientes del mismo grupo se salteaban sin crecer
  (dos etiquetas iguales quedaban con una sola distinguida). Corregido
  comparando contra una foto (`list(resultado)`) tomada al arranque de cada
  pasada, no contra el arreglo mutándose en vivo.

  **Hallazgo 4 -- con la lista en botones, el texto seguía enumerando cada
  tarea, y el menú de una tarea no decía de quién era ni en qué estado
  estaba.** Evidencia: con T3 ya armando un botón por tarea (hallazgo 1), el
  modelo además enumeraba las 12 en el texto ("- Backup de servidores de
  producción (simulado) — asignada" x 12) -- ADR 0007 punto 2 ("el texto da
  el contexto; la elección se hace tocando") pide lo contrario: texto corto,
  elección por botón. Al dejar de enumerar, lo único que el texto viejo
  aportaba y los botones no -- de quién es cada tarea y en qué estado está --
  se perdía.

  Decisiones:
  - `contexto.PREAMBULO`: al listar tareas con `consultar_tareas`, el texto
    resume -- cuántas son y, si hace falta, sólo lo notable (bloqueada, en
    revisión, vencida) -- nunca la lista completa de títulos. Si son de
    varias personas, nombra a alguien sólo cuando importa (quién tiene la
    bloqueada) o lo da como conteo ("dos por persona"), nunca enumerando
    quién tiene cada una.
  - `menu_tarea.encabezado_menu(menu)`: el menú de una tarea (T2) antepone
    una línea corta -- `«título» · quién · estado` -- a su única pregunta
    ("¿Qué querés hacer?"), en vez de "¿Qué querés hacer con «título»?" a
    secas. "tuya" cuando quien toca ES la responsable (nunca su propio
    nombre); el nombre real para un aprobador o para otra persona. Requirió
    sumar `responsable_nombre` a `MenuTarea` y el `join` a `integrante` en
    `menu_tarea._tarea_para_menu` (antes sólo traía el `membership_id`).
    Sigue siendo una sola pregunta por mensaje (regla del hallazgo 2).

  Archivos: `src/prisma/contexto.py` (regla nueva), `src/prisma/menu_tarea.py`
  (`responsable_nombre`, `encabezado_menu`), `src/prisma/gateway.py`
  (`_encolar_menu_tarea` arma la pregunta con el encabezado nuevo).

  Bench (`tests/banco`, sólo corre contra un modelo real, fuera de la suite
  por defecto): se agregó `respuesta_no_contiene_patron` a
  `tests/banco/escenarios/b-0016.yaml` (lista de tareas propias, T3) contra
  los dos títulos de tarea del escenario -- ninguna de las dos tiene un
  estado notable, así que una respuesta que cumple la regla no tiene motivo
  para nombrar a ninguna por su título; que aparezca cualquiera de las dos
  es indicio de que las enumeró. No se tocaron `b-0009.yaml`/`b-0017.yaml`
  (no declaran candidatas/etiquetas afectadas) ni `b-0013.yaml` (su
  aclaración real se resuelve por `ofrecer_opciones`, que compara por
  título, no por etiqueta de botón -- ver hallazgo 3 arriba).

  Pruebas nuevas (RED verificado antes de implementar):
  - `tests/test_opciones_modelo.py::test_reglas_del_contexto_piden_ofrecer_opciones`:
    assertion nueva sobre `"no las enumeres" in PREAMBULO.lower()`. RED
    verificado a mano contra el `PREAMBULO` de `HEAD` (`False`).
  - `tests/test_menu_tarea.py::test_encabezado_del_menu_muestra_responsable_y_estado`
    y `::test_encabezado_del_menu_dice_tuya_para_la_propia_responsable`: RED
    -- `AssertionError: assert 'Mariano Naim' in '¿Qué querés hacer con
    «Programar HMI línea 2»?'` (el encabezado viejo no traía responsable ni
    estado) y el análogo con "tuya". GREEN: `tests/test_menu_tarea.py` ->
    `30 passed`.

  Verificación de la unidad completa (hallazgos 2, 3 y 4 juntos):
  - `tests/test_salida.py tests/test_aclaracion_botones.py
    tests/banco/test_corrida.py tests/test_menu_tarea.py
    tests/test_autoridad_tarea.py tests/test_pregunta_sin_opciones.py
    tests/test_opciones_modelo.py tests/test_lista_botones.py` -> `281
    passed` (antes de sumar `tests/test_menu_tarea.py`, corrida aparte:
    `30 passed`).
  - Suite completa: `.venv/Scripts/python.exe -m pytest -q` -> `886 passed,
    108 deselected` (207 s) -- `876` de base + 10 pruebas nuevas (7 de
    `salida`, 2 de `menu_tarea`, 1 de `lista_botones`); mismo `108
    deselected` (el banco contra modelo real, sin tocar).

- 2026-09-27 (orquestador): **Sesión 2 por Telegram, hallazgo 5 -- aprobar no
  cerraba la tarea, ni avisaba a nadie.** Evidencia en `audit_log`: Ismael (el
  aprobador) tocó el menú de una tarea -> "Aprobar" -> vista previa -> Confirmar;
  el bot contestó "Hecho. Tarea: Dashboard de lotes en CoreLabs (simulado) ·
  Estado actual: En revisión · se aprueba el trabajo". `audit_log` registró
  `herramienta:aprobar_tarea` y `approval` tiene la fila, pero la tarea siguió
  `en_revision`: `herramientas._aprobar_tarea` sólo insertaba en `approval`,
  nunca corría `motivo_no_cierra_tarea` ni escribía en `task_state_event`. El
  menú del responsable en `en_revision` sólo ofrece "Adjuntar evidencia" --
  nadie podía cerrarla tocando -- y nadie le avisó a Ariel (el responsable) que
  su tarea había sido aprobada. Mismo hallazgo, defecto más chico: el mensaje
  posterior a Confirmar repetía el texto de la vista previa ("Estado actual: En
  revisión") en vez de describir el resultado, tanto para `aprobar_tarea` como
  para `actualizar_estado`.

  **Decisión del usuario, 2026-09-27 (ADR 0008):** aprobar registra la
  aprobación Y, si con ella alcanzan las condiciones de cierre (mecánica §5 --
  comprobado con `motivo_no_cierra_tarea(tarea_id)`, la misma función que ya
  gobierna el cierre por `actualizar_estado`), registra la transición
  `en_revision -> terminada` en el mismo acto: dos registros distintos
  (`approval` y `task_state_event`), un solo toque. Si falta algo, la tarea
  queda `en_revision` con la aprobación igual registrada, y Prisma dice
  exactamente qué falta -- nunca una pregunta abierta. Se avisa al responsable
  por outbox en cualquiera de los dos casos (dedupe por el id de la
  aprobación, nunca por la hora; se omite en silencio sólo si no tiene chat
  vinculado). Principio del usuario: Prisma ayuda y orienta, nunca agrega
  burocracia -- pero "aprobación y cierre son hechos distintos"
  (`AGENTS.md`/constitución §3) sigue valiendo como dos REGISTROS distintos,
  no dos actos separados que exigirían un segundo toque para algo que la base
  ya puede decidir sola. Detalle de la interpretación y las alternativas
  consideradas en el ADR.

  Archivos:
  - `src/prisma/herramientas.py`: constante `_MOTIVO_FALTA_APROBACION` (el
    texto exacto que devuelve `motivo_no_cierra_tarea` cuando lo único que
    falta es esta aprobación); `_preparar_aprobar_tarea` predice el resultado
    corriendo esa misma función SQL antes de escribir nada (preview: "Se
    aprueba «X» y queda terminada." / "...; para cerrarla todavía falta:
    ..."); `_aprobar_tarea` inserta la aprobación, vuelve a preguntarle a
    `motivo_no_cierra_tarea` (ya con la aprobación adentro, sin necesidad de
    predecir), inserta el `task_state_event` sólo si cierra, avisa la
    dependencia informativa si corresponde, y notifica al responsable por
    `_avisar`. Devuelve `{"aprobada": True, "cerrada": bool, "falta": motivo o
    None, "titulo": ...}` en vez de `{"aprobada": True}`.
  - `src/prisma/gateway.py`: el camino de confirmación por botón distingue
    `aprobar_tarea` (donde `cerrada: False` significa "se escribió la
    aprobación, pero no alcanzó para cerrar", no "no se escribió nada") del
    resto de las herramientas con `preparar`, para no auditarla como
    `herramienta_rechazada`; agrega el fraseo del resultado para
    `aprobar_tarea` ("Listo: aprobaste «X». Quedó terminada." / "...; para
    cerrarla falta: ...") y para `actualizar_estado` ("Listo: «X» pasó a
    <estado>."), leyendo el título aparte porque `_actualizar_estado` no lo
    devuelve (otros tests comparan su resultado con `{"estado": ...}` exacto).
    También se agregó el mapeo de la acción de menú `cerrar_tarea` a
    `actualizar_estado(estado="terminada")` en `_resolver_toque_menu_tarea`.
  - `src/prisma/menu_tarea.py`: `_puede_cerrar` (reusa `motivo_no_cierra_tarea`,
    igual que `_puede_empezar` reusa `motivo_no_arranca_tarea`) y el botón
    "Cerrar tarea" en el menú del responsable cuando la tarea está
    `en_revision` y ya no falta ninguna condición.
  - `docs/decisions/0008-la-aprobacion-cierra-la-tarea.md` (nuevo) y
    `docs/INDEX.md` (fila agregada a la tabla de decisiones).

  Pruebas nuevas (RED verificado antes de implementar, revirtiendo sólo los
  tres archivos de `src/prisma/` con `git stash` y corriendo las pruebas
  nuevas contra el código viejo):
  - `tests/test_aprobacion_cierra_tarea.py` (nuevo):
    `test_aprobar_tarea_cierra_cuando_las_condiciones_estan`,
    `test_aprobar_tarea_registra_pero_no_cierra_si_falta_evidencia`,
    `test_aprobar_tarea_no_cierra_con_dependencia_bloqueante_sin_resolver`,
    `test_mensaje_post_confirmacion_aprobar_tarea_que_cierra`,
    `test_mensaje_post_confirmacion_aprobar_tarea_que_no_cierra`,
    `test_mensaje_post_confirmacion_actualizar_estado`.
  - `tests/test_menu_tarea.py`:
    `test_menu_responsable_en_revision_ofrece_cerrar_tarea_si_ya_alcanza`,
    `test_menu_responsable_en_revision_sin_aprobacion_no_ofrece_cerrar_tarea`,
    `test_cerrar_tarea_desde_el_menu_termina_en_vista_previa`.
  - RED (código de `src/prisma/` en el estado anterior a esta unidad): `8
    failed, 1 passed` -- las 6 de `test_aprobacion_cierra_tarea.py` (tarea
    seguía `en_revision`/mensaje seguía siendo la vista previa) y 2 de las 3
    nuevas de `test_menu_tarea.py` (`Cerrar tarea` no aparecía en el menú ni
    en la vista previa del toque); la de "no ofrece" ya pasaba porque el
    botón nuevo directamente no existía.
  - GREEN: `tests/test_aprobacion_cierra_tarea.py tests/test_menu_tarea.py`
    -> `39 passed`; adyacentes
    (`tests/test_vista_previa_confirmacion.py tests/test_botones.py
    tests/test_autoridad_tarea.py tests/test_dependencias.py
    tests/test_task_drafts.py tests/test_task_intake.py`) -> `185 passed`;
    `tests/banco` -> `205 passed, 108 deselected`.
  - Suite completa: `.venv/Scripts/python.exe -m pytest -q` -> `895 passed,
    108 deselected` (241 s) -- `886` de base + 9 pruebas nuevas (6 de
    `test_aprobacion_cierra_tarea.py`, 3 de `test_menu_tarea.py`); mismo `108
    deselected`.

  **Preguntas de producto abiertas (no bloquean esta unidad, quedan
  `PENDIENTE`):** si el mismo tratamiento ("aprobar cierra si alcanza")
  conviene para `motivo_no_cierra_objetivo` (cierre de objetivo, hito o plan) --
  constitución §7 reserva esa aprobación final para decisiones de otro peso, y
  hoy no hay una herramienta `aprobar_objetivo` equivalente para decidirlo en
  código; queda anotado en el ADR, no implementado.

- 2026-09-27: **Sesión 2 por Telegram, hallazgos 6 y 7, y seguimientos de la
  revisión de etiquetas.** Ruta: delegada, un escritor (disparador de mapeo:
  `agente.py`, `salida.py`, lectura de `herramientas.py`/`gateway.py`, y
  cinco archivos de prueba).

  **Hallazgo 6 -- dos preguntas seguidas.** Evidencia real, confirmada por el
  usuario: "Hola Ismael. ¿Con qué te ayudo?\n\n¿Qué querés hacer?". Desde
  `86a40c6` el texto del modelo se manda junto con `ofrecer_opciones`
  (`agente._encolar_opciones_modelo`), y esa función le agregaba encima la
  `pregunta` de las opciones sin mirar si el texto ya preguntaba algo.
  Corregido: si el texto ya pregunta (`deteccion_pregunta.hace_pregunta`, ya
  usada en T4b), sale solo -- introduce los botones sin repetir la pregunta
  aparte; si no pregunta, se sigue agregando `e.pregunta` como siempre.
  `e.pregunta` sigue guardada en `args` para `gateway._resolver_toque_
  opcion_modelo`, sin cambios ahí.

  **Hallazgo 7 -- palabra de función antes de la elipsis.** Evidencia real:
  "Backup de servidores de…", "Configurar access points de…", "Cambiar
  switch industrial de…". `salida.acortar_etiqueta_boton` ya cortaba en
  límite de palabra (sesión 1) pero podía dejar una preposición o un
  artículo suelto justo antes de "…". Corregido con `_PALABRAS_FUNCION_
  FINALES` (lista chica y cerrada: de, del, la, el, los, las, en, al, a, y,
  e, o, u, para, con, por, sin, sobre, un, una) y `_sin_palabras_funcion_
  finales`, que saca palabras del final una por una sin dejar nunca la
  etiqueta vacía.

  **Seguimientos de la revisión de etiquetas (review-af418dd9):**
  - (a) `truncar_etiqueta_boton` ganó un parámetro `limite` -- antes
    ignoraba el `limite` de quien la llamaba y el corte duro quedaba
    siempre en 48; `acortar_etiqueta_boton` se lo pasa ahora en su propio
    corte duro.
  - (b) La numeración de último recurso de `etiquetas_boton_distinguibles`
    (cuando dos títulos son indistinguibles incluso enteros) no tenía
    ninguna prueba. Corregida para no colisionar con una etiqueta ya
    presente en el conjunto (salta el número ocupado) y para no numerar
    nunca una etiqueta `fija`; si una movible coincide con una fija, se
    numera la movible (nunca queda igual a la fija, que no se puede tocar).
  - (c) `etiquetas_boton_distinguibles` levanta `ValueError` si `fijas` no
    tiene el mismo largo que `titulos`, en vez de descartar etiquetas en
    silencio por el `zip` corto.
  - (d) Pruebas nuevas a través de la herramienta (`ofrecer_opciones`, no
    llamando directo a `herramientas._ofrecer_opciones`): etiqueta del
    modelo ≤ 30 se respeta exacta; etiqueta del modelo > 30 se acorta en
    límite de palabra; sin etiqueta propia, sale del título.
  - (e) Pruebas nuevas sobre los otros dos lugares que arman botones de
    tarea: la página de "Ver más" (`gateway._mostrar_mas_tareas`) y las
    candidatas de una dependencia (`gateway._pedir_eleccion_dependencia`).

  Archivos:
  - `src/prisma/agente.py`: `_encolar_opciones_modelo` (hallazgo 6).
  - `src/prisma/salida.py`: `truncar_etiqueta_boton` (seguimiento a);
    `_PALABRAS_FUNCION_FINALES` + `_sin_palabras_funcion_finales` +
    `acortar_etiqueta_boton` (hallazgo 7); `etiquetas_boton_distinguibles`
    (seguimientos b y c).
  - `tests/test_opciones_modelo.py`: `test_no_duplica_la_pregunta_si_el_
    texto_del_modelo_ya_pregunta` (hallazgo 6);
    `test_etiqueta_del_modelo_corta_se_respeta_tal_cual`,
    `test_etiqueta_del_modelo_larga_se_acorta_en_limite_de_palabra`,
    `test_etiqueta_de_tarea_sin_etiqueta_propia_sale_del_titulo`
    (seguimiento d).
  - `tests/test_salida.py`: `test_acortar_etiqueta_boton_no_termina_en_
    palabra_de_funcion` (parametrizada, 3 casos) y `test_acortar_etiqueta_
    boton_nunca_deja_vacio_si_todo_es_funcion` (hallazgo 7);
    `test_acortar_etiqueta_boton_corte_duro_honra_un_limite_no_default` y
    `test_truncar_etiqueta_boton_honra_un_limite_no_default` (seguimiento
    a); `test_etiquetas_boton_distinguibles_fijas_de_otro_largo_levanta_
    error` (seguimiento c); `test_etiquetas_boton_distinguibles_numera_
    titulos_identicos`, `test_etiquetas_boton_distinguibles_numera_
    saltando_una_colision_existente`, `test_etiquetas_boton_distinguibles_
    nunca_numera_ni_modifica_una_fija` (seguimiento b).
  - `tests/test_lista_botones.py`: `test_mostrar_mas_tareas_acorta_titulos_
    largos_en_limite_de_palabra`, `test_mostrar_mas_tareas_distingue_
    titulos_que_colisionan_al_acortar` (seguimiento e).
  - `tests/test_menu_tarea.py`: `test_pedir_eleccion_dependencia_acorta_y_
    distingue_titulos_largos` (seguimiento e).
  - `tests/test_aclaracion_botones.py`: `test_botones_propia_primero_ajena_
    con_nombre_y_titulo_truncado` adaptada -- su título de prueba
    ("Actualizar toda la documentación técnica del área completa") cortaba
    justo en "la" antes de esta corrección; la aserción pasa de "Actualizar
    toda la…" a "Actualizar toda…" (era exactamente el hallazgo 7, no una
    aserción débil que se relaje).

  RED (`tests/test_opciones_modelo.py::test_no_duplica_la_pregunta_si_el_
  texto_del_modelo_ya_pregunta` y `tests/test_salida.py::test_acortar_
  etiqueta_boton_no_termina_en_palabra_de_funcion` contra el código sin
  estas correcciones, con `agente.py`/`salida.py` apartados temporalmente
  por `git stash push -- src/prisma/agente.py src/prisma/salida.py`, los
  archivos de prueba ya escritos):
  `.venv/Scripts/python.exe -m pytest -q tests/test_opciones_modelo.py::
  test_no_duplica_la_pregunta_si_el_texto_del_modelo_ya_pregunta
  "tests/test_salida.py::test_acortar_etiqueta_boton_no_termina_en_palabra_
  de_funcion"` -> `4 failed` (la de hallazgo 6, y las 3 variantes
  parametrizadas de hallazgo 7) -- exactamente por el motivo esperado: el
  mensaje traía la pregunta duplicada (`'Hola Ismael. ¿Con qué te
  ayudo?\n\n¿Qué querés hacer?'` en vez del texto solo), y la etiqueta corta
  terminaba en "de la"/"de" antes de "…" (`'Backup de servidores de la…'`,
  `'Configurar access points de la…'`, `'Cambiar switch industrial de…'`).
  `git stash pop` restauró la implementación antes de seguir.

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_opciones_modelo.py
    tests/test_menu_tarea.py tests/test_lista_botones.py tests/test_salida.py`
    -> `106 passed, 1 warning`.
  - `.venv/Scripts/python.exe -m pytest -q tests/test_aclaracion_botones.py
    tests/test_pregunta_sin_opciones.py tests/test_botones.py
    tests/test_vista_previa_confirmacion.py tests/test_agente.py
    tests/test_deteccion_pregunta.py tests/test_autoridad_tarea.py
    tests/test_task_intake.py tests/test_modificar.py
    tests/test_respuestas_nombran_tarea.py tests/test_veracidad.py
    tests/test_resolucion_referencias.py tests/test_pendientes.py
    tests/test_personas.py tests/test_memoria.py tests/test_capacidades.py
    tests/test_opciones_modelo.py tests/test_menu_tarea.py
    tests/test_lista_botones.py tests/test_salida.py tests/banco` ->
    `586 passed, 108 deselected, 1 warning` (barrido de regresión).
  - Suite completa: `.venv/Scripts/python.exe -m pytest -q` -> `912 passed,
    108 deselected, 1 warning` (216 s) -- línea base 895 + 17 pruebas nuevas
    de esta unidad (4 en `test_opciones_modelo.py`, 10 en `test_salida.py`,
    2 en `test_lista_botones.py`, 1 en `test_menu_tarea.py`); mismo `108
    deselected`.

  Abierto: ninguno de los hallazgos/seguimientos restantes de la sesión 2
  (más allá de 6 y 7) ni la segunda sesión real por Telegram -- siguen en
  "Próximo paso al retomar", sin tocar acá.

- 2026-09-27: **Sesión 2 por Telegram, hallazgos 8 y 9: entrega con evidencia y
  revisión (ADR 0009).** Ruta: delegada, un escritor (disparador de mapeo:
  `herramientas.py`, `menu_tarea.py`, `gateway.py`, `db/esquema.sql` + migración,
  ocho archivos de prueba existentes adaptados + un archivo nuevo).

  **Evidencia real:** Ariel tocó "Ya la terminé" sobre una tarea que exige
  evidencia (`evidencia_requerida = ['explicacion']`); Prisma la pasó a
  `en_revision` sin pedir ni registrar ninguna. Ismael, el aprobador, tocó
  "Aprobar" → vista previa → Confirmar y Prisma lo dejó aprobar a ciegas,
  contestando "Se aprueba «…»; para cerrarla todavía falta: Falta la evidencia
  requerida." -- con "falta" repetida. Una revisión de código aparte encontró el
  defecto de fondo: `_aprobar_tarea`/`_preparar_aprobar_tarea` no exigían que la
  tarea estuviera `en_revision` -- por texto libre se podía aprobar (y cerrar,
  por ADR 0008) una tarea `asignada`, o volver a aprobar una `terminada`.

  **Decisión del usuario (ADR 0009):** 1) "Ya la terminé" pide la evidencia que
  falta en el mismo paso (mismo patrón que "Informar un bloqueo") y arma UNA
  vista previa que registra la evidencia y mueve el estado juntos, en el mismo
  Confirmar -- sin evidencia, la tarea no llega a `en_revision` por el menú; por
  texto libre, `actualizar_estado(estado="en_revision")` sin evidencia devuelve
  un `falta` verdadero, nunca mueve la tarea. 2) "Aprobar" sólo se permite sobre
  una tarea `en_revision` y con la evidencia ya registrada -- el menú y la
  herramienta (`preparar` y el handler) lo exigen los dos. 3) Quien aprueba se
  entera de la entrega con botones ("Aprobar"/"Pedir cambios"), no sólo el
  responsable con un aviso de texto. 4) "Pedir cambios" (acción nueva del
  aprobador en `en_revision`) pide el comentario, arma vista previa y al
  confirmar registra `approval.decision = 'rechazado'` y devuelve la tarea a
  `en_curso` con el comentario como motivo. 5) La palabra "falta" no queda
  repetida en ningún mensaje. Fotos/archivos como evidencia quedan fuera
  (unidad de aportes sobre tareas del roadmap). Detalle completo, alternativas
  consideradas y lo pendiente en `docs/decisions/0009-entrega-con-evidencia-y-revision.md`.

  Archivos:
  - `db/esquema.sql`, `db/migrations/0012_evidencia_pendiente.sql` / `db/rollbacks/
    0012_evidencia_pendiente.sql` (nuevos): `evidencia_pendiente(p_task uuid)
    returns boolean` -- única fuente de verdad de "a esta tarea le falta la
    evidencia que exige su política" -- y `motivo_no_cierra_tarea` refactorizada
    para llamarla en vez de repetir el chequeo inline (mismo criterio que
    `motivo_no_arranca_tarea`/`estado_previo_a_bloqueo`: una función, no una
    regla duplicada en Python).
  - `src/prisma/herramientas.py`: `_MOTIVO_FALTA_EVIDENCIA_ENTREGA`;
    `actualizar_estado` gana el parámetro opcional `evidencia_texto`;
    `_preparar_actualizar_estado`/`_actualizar_estado` piden/registran la
    evidencia junto con el cambio a `en_revision` (dos filas, un acto, mismo
    patrón que ADR 0008) y notifican al aprobador; `_exigir_puede_aprobarse`
    (nuevo, usado por `preparar` y el handler de `aprobar_tarea`) exige
    `en_revision` + evidencia; `_enlace_portal_tarea` (hoy `None`, punto de
    enganche nombrado para cuando exista una vista de tarea individual) y
    `_notificar_entrega_al_aprobador` (arma la `pending_action` con
    `SENTINEL_MENU_TAREA`, botones "Aprobar"/"Pedir cambios" -- mismo camino que
    el menú de tarea T2); herramienta nueva `pedir_cambios_tarea` con su
    `_preparar_pedir_cambios_tarea`/`_exigir_puede_pedirse_cambios`; wording de
    "falta" corregido en `_preparar_aprobar_tarea` y el aviso de `_aprobar_tarea`;
    `_avisar_dependencia_informativa` en `_aprobar_tarea` usa `aprobacion_id` en
    vez de `uuid.uuid4()` (revisión review-ec6f7d80, decisión 6 del enunciado).
  - `src/prisma/menu_tarea.py`: `evidencia_pendiente` (envoltorio de la función
    SQL, mismo patrón que `_puede_cerrar`/`_puede_empezar`); el menú del
    aprobador en `en_revision` sólo ofrece "Aprobar" sin evidencia pendiente, y
    siempre ofrece "Pedir cambios".
  - `src/prisma/gateway.py`: `_resolver_toque_menu_tarea` -- "terminar" pide la
    evidencia primero si falta (`_pedir_dato_menu_tarea`) y agrega la acción
    "pedir_cambios"; `_resumir_dato_menu_tarea` mapea esos dos datos a
    `actualizar_estado(evidencia_texto=...)`/`pedir_cambios_tarea`; wording de
    "falta" corregido en el mensaje posterior a confirmar `aprobar_tarea`;
    `_toque` reconoce `en_revision: False` como rechazo (igual que
    `cerrada`/`iniciada` en `False`) para no mostrar la vista previa vieja como si
    hubiera aplicado algo.
  - `tests/test_entrega_con_evidencia.py` (nuevo, 12 pruebas): la entrega pide/
    registra evidencia, notifica al aprobador con botones, tocar "Aprobar" desde
    esa notificación llega a la vista previa de ADR 0008; el gate de "Aprobar"
    (por estado y por evidencia); `pedir_cambios_tarea` completo y sus rechazos;
    la palabra "falta" no se repite.
  - `tests/test_menu_tarea.py` (+4 pruebas: `test_menu_aprobador_en_revision_
    sin_evidencia_no_ofrece_aprobar`,
    `test_ya_la_termine_pasa_directo_a_vista_previa_si_ya_tiene_evidencia`, y dos
    reemplazos sin cambiar la cuenta neta): `test_menu_aprobador_en_revision`
    gana evidencia + "Pedir cambios" en la aserción;
    `test_ya_la_termine_pasa_a_en_revision_por_vista_previa` reemplazada por
    `test_ya_la_termine_pide_evidencia_si_falta_y_termina_en_vista_previa` (pide
    el dato, UNA vista previa combinada); `test_aprobar_termina_en_vista_previa`
    gana evidencia en la precondición (si no, "Aprobar" ya no aparece).
  - `tests/test_aprobacion_cierra_tarea.py` (+1 prueba neta):
    `test_aprobar_tarea_registra_pero_no_cierra_si_falta_evidencia` reemplazada
    por `test_aprobar_tarea_rechaza_si_falta_la_evidencia_que_exige` (ahora
    rechaza, no registra); `test_mensaje_post_confirmacion_aprobar_tarea_que_
    no_cierra` reemplazada por la versión que rechaza, y se agregó
    `test_mensaje_post_confirmacion_aprobar_tarea_que_no_cierra_por_dependencia`
    (evidencia presente, bloqueada por una dependencia, para seguir cubriendo el
    wording de "todavía: …" sin evidencia de por medio);
    `test_mensaje_post_confirmacion_actualizar_estado` exime la evidencia
    (`evidencia_requerida=None`) porque prueba el fraseo del mensaje, no el gate
    nuevo; `_tarea` corrige un bug latente (`None` en vez de `[]` para "sin
    evidencia", violaba el `not null` de la columna -- no se había ejercitado
    hasta ahora).
  - Pruebas adaptadas para seguir pasando el gate nuevo sin evidencia de por
    medio (tareas ya `en_revision`/con evidencia agregada en la precondición, o
    `evidencia_texto` agregado al llamado): `tests/test_agente.py`
    (`test_cadena_de_aprobacion`, prueba la cadena de autoridad, no el gate --
    nuevo helper `_en_revision_con_evidencia`), `tests/test_vista_previa_
    confirmacion.py` (`test_propiedad_aprobar_tarea`), `tests/test_dependencias.py`
    (`test_dependencia_informativa_no_avisa_dos_veces_por_el_mismo_evento`),
    `tests/test_aclaracion_botones.py`
    (`test_elegir_candidata_retoma_y_llega_a_la_vista_previa_sin_aplicar_nada`),
    `tests/test_opciones_modelo.py` (`test_retomar_con_un_cambio_sigue_pidiendo_
    confirmar`), `tests/banco/test_corrida.py` (dos escenarios con
    `actualizar_estado` del modelo ganan `evidencia_texto`; el escenario de
    toques genéricos y `tests/banco/escenarios/b-0004*.yaml`/`b-0013.yaml`/
    `b-0017.yaml` ganan `evidencia_requerida: []` en la precondición -- **no**
    se extendió el corredor con un paso de texto libre intercalado entre dos
    toques porque no existe ese tipo de paso hoy (`tests/banco/corrida.py`,
    `_resolver_toque_generico` sólo resuelve botones); extenderlo queda
    **PENDIENTE**, reportado en el ADR, fuera de esta unidad.
  - `tests/banco/corrida.py`: `_crear_tarea_semilla`/`sembrar_precondiciones`
    ganan el parámetro opcional `evidencia_requerida` (por omisión sigue siendo
    `['explicacion']`, sin cambio para ningún escenario que no lo declare).

  **Hallazgo incidental, ajeno a ADR 0009, corregido en la misma unidad:**
  ampliar `tests/test_task_intake.py::_retrato_de_funciones` (la comparación de
  paridad migración/rollback) para que ya no filtre por `security definer` --
  `evidencia_pendiente` y la nueva rama de `motivo_no_cierra_tarea` no lo son, y
  con el filtro viejo la migración `0012` no cambiaba "nada observable" para esa
  prueba, aunque sí cambiaba algo real -- expuso que el rollback de
  `0008_task_start_gate.sql` nunca borraba `exigir_dependencias_resueltas()` (la
  función del disparador, sólo se borraba el disparador y `motivo_no_arranca_
  tarea`): un defecto de fidelidad preexistente, ajeno a esta sesión, que la
  comprobación vieja (filtrada a funciones `security definer`) nunca podía ver.
  Corregido agregando el `drop function` que faltaba en
  `db/rollbacks/0008_task_start_gate.sql`, con la evidencia del diagnóstico
  documentada en el propio archivo. Verificado con un guión aparte que aplica
  cada migración + su rollback en cadena, contra una base descartable, y compara
  el catálogo antes/después: limpio para las doce migraciones tras la
  corrección (antes, sólo fallaba `0008` -- y, mientras se escribía la migración
  `0012`, el mismo guión encontró dos comentarios que se habían perdido al
  transcribir el rollback de `0012`, ya corregidos ahí mismo).

  RED (`git stash push -- src/prisma/herramientas.py src/prisma/menu_tarea.py
  src/prisma/gateway.py`, con `db/esquema.sql` ya con `evidencia_pendiente` y
  los archivos de prueba ya escritos):
  `.venv/Scripts/python.exe -m pytest -q tests/test_entrega_con_evidencia.py` ->
  `7 failed, 5 passed` (los 5 que ya pasaban son los que no dependen del cambio
  de comportamiento -- p. ej. el gate cuando la tarea ya está en el estado
  correcto). `git stash pop` restauró la implementación antes de seguir.

  GREEN:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_entrega_con_evidencia.py`
    -> `12 passed`.
  - `.venv/Scripts/python.exe -m pytest -q tests/banco/test_corrida.py
    tests/test_aclaracion_botones.py tests/test_agente.py
    tests/test_aprobacion_cierra_tarea.py tests/test_dependencias.py
    tests/test_menu_tarea.py tests/test_opciones_modelo.py
    tests/test_task_intake.py tests/test_vista_previa_confirmacion.py
    tests/test_entrega_con_evidencia.py` -> `292 passed`.
  - Suite completa: `.venv/Scripts/python.exe -m pytest -q` -> `927 passed,
    108 deselected` (216 s) -- línea base 912 + 15 pruebas nuevas (12 de
    `test_entrega_con_evidencia.py`, 2 de `test_menu_tarea.py`, 1 de
    `test_aprobacion_cierra_tarea.py`); mismo `108 deselected`.

  Abierto (documentado como PENDIENTE en el ADR, no bloquea el cierre de esta
  unidad): enlace al detalle de la tarea en el aviso de entrega (no existe vista
  de tarea individual todavía); fotos/archivos como evidencia (unidad de
  aportes sobre tareas); extender `tests/banco/corrida.py` con un paso de texto
  libre intercalado entre dos toques.

- 2026-09-27 (orquestador): **cierre de la segunda sesión real por Telegram.** Datos
  ficticios en la base local (copias `db/respaldos/prisma-antes-sesion2-20260927.dump` y
  `prisma-antes-0012-20260927.dump`); cero incidentes en toda la sesión. Diez hallazgos:
  1 (botones de lista sólo con la última consulta, `efb4feb`), 2 y 6 (dos preguntas: regla
  del contexto `dafe87e` y la causa real, el servidor pegaba texto y pregunta, `2bee9a9`),
  3 y 7 (etiquetas cortas por palabra sin palabra de enlace final, `e7071eb`, `2bee9a9`),
  4 (resumen en vez de enumerar y encabezado del menú con responsable y estado, `e7071eb`,
  `dafe87e`), 5 (aprobar cierra la tarea si se cumplen las condiciones, `d6885d7`, ADR 0008),
  8 y 9 (entrega con evidencia y revisión, `739f441`, `8835ad9`, ADR 0009, migración `0012`
  aplicada en la base local con `psql` y verificada), 10 (retoma una pregunta descartada,
  pendiente). Probados en vivo: 1 a 7. Sin probar en vivo: 8 y 9. Revisiones de la sesión
  aprobadas y reconocidas: review-af418dd93b4b39ea, review-ec6f7d80b7e7e7b4,
  review-149a33fa3aa53447, review-c112506ab1690225 (riesgo alto, cuatro lentes); frontera
  de revisión en `e8dbc24`. Suite completa: `927 passed, 108 deselected` (escritor de la
  entrega con evidencia, reproducida dos veces). Decisiones del usuario de la sesión:
  unión de consultas para los botones; aprobar cierra (ADR 0008); entrega con evidencia y
  aprobador que ve la evidencia antes de aprobar, "Pedir cambios" (ADR 0009); referencias
  reformuladas por el modelo como el trabajo al que apuntan, sin bajar el umbral de Jev ni
  pasarle más contexto, adoptable sólo si el banco real completo no empeora ningún
  escenario; principio "Prisma ayuda y dirige, firme donde importa, sin burocracia".
  Los títulos de las tareas ficticias conservan "(simulado)": el esquema protege los campos
  de compromiso como inmutables y no se forzó; sembrarlas sin sufijo en la próxima base de
  prueba.

- **Próximo paso al retomar:** (1) seguimientos de review-c112506a — prioridad: una
  aprobación anterior sigue valiendo después de "Pedir cambios"; la evidencia nueva se
  descarta al volver a entregar; `pedir_cambios_tarea` sin chequeo de dependencias; dedupe
  del aviso de entrega con `uuid4`; prueba de punta a punta de "Pedir cambios"; (2) hallazgo
  10 y seguimientos de review-149a33fa (etiquetas repetidas del modelo, pregunta suprimida,
  asserts); (3) referencias reformuladas por el modelo (`b-0005-b`) con banco real antes y
  después y casos de guarda; (4) tercera ronda corta por Telegram para la entrega con
  evidencia y "Pedir cambios". Antes de una sesión real: base local contra
  `db/esquema.sql` (al día hasta `0012`).
  **Resolver antes de la próxima sesión real — títulos "(simulado)":** las 12 tareas
  ficticias de la base local terminan en " (simulado)" y el usuario pidió que no. No se
  pueden renombrar: el título es un campo de compromiso y `bloquear_estado_directo` lo
  protege como inmutable (se intentó el 2026-09-27 y la base lo rechazó, correctamente;
  no se fuerza). Tampoco hay un script de siembra en el repositorio: se cargaron a mano en
  la sesión 1. Solución: un script de siembra reproducible de datos ficticios (mismas
  personas y tareas, títulos sin sufijo, con `evidencia_requerida` coherente con la
  política del pack) que cargue una base de prueba nueva o restaurada, nunca editando
  campos inmutables; documentar su uso en `PRUEBA-LOCAL.md`.

- 2026-09-27: **T6a cerrada — una aprobación anterior no sobrevive a "Pedir
  cambios"** (seguimiento de review-c112506a). Ruta: delegada, un escritor
  (`db/esquema.sql`, migración y rollback `0013`, pruebas). `motivo_no_cierra_tarea`
  cuenta un `approval` 'aprobado' sólo si no hay un 'rechazado' del mismo aprobador
  con `at` posterior o igual (el empate falla cerrado). Migración
  `db/migrations/0013_aprobacion_no_sobrevive_a_pedir_cambios.sql` y su rollback
  (restaura el cuerpo de `0012`); **no aplicada todavía a la base local**.
  Pruebas nuevas en `tests/test_entrega_con_evidencia.py` (sección 5): escenario
  completo con un bloqueo abierto, empate de `at`, y regresión de aprobación simple.
  Hallazgo del escritor: el escenario con una dependencia bloqueante abierta no se
  puede reproducir hoy, porque "Pedir cambios" devuelve la tarea a `en_curso` y el
  disparador de `0008` rechaza esa transición con la dependencia abierta -- es
  exactamente el seguimiento T6c. Fuera de alcance, anotado:
  `motivo_no_cierra_objetivo` tiene el mismo patrón ("cualquier 'aprobado' cuenta
  para siempre"), sin camino de rechazo para objetivos hoy.
  RED: `pytest -q tests/test_entrega_con_evidencia.py -k "pedir_cambios_invalida or
  empate_de_at or plana_sigue"` -> `2 failed, 1 passed`. GREEN: mismo comando ->
  `3 passed`. Enfocada (reejecutada por el orquestador): `pytest -q
  tests/test_entrega_con_evidencia.py tests/test_aprobacion_cierra_tarea.py
  tests/test_task_intake.py tests/test_menu_tarea.py` -> `141 passed` (incluye el
  ensayo migración/rollback, que descubre `0013` solo). Suite completa (escritor):
  `.venv/Scripts/python.exe -m pytest -q` -> `930 passed, 108 deselected`.
  Commit `f6c282a`. RDD: `review assess --base-ref e8dbc24 --committed-only` ->
  medio, `review_due` (`slice_budget_reached`); consentimiento del usuario: revisar.
  Revisión review-3cf89bef5f7c1c09 (una lente, confiabilidad) aprobada y reconocida
  (autoridad quemada); frontera de revisión en `f6c282a`. Hallazgo no bloqueante
  (WARNING, inferencial): `approval.at` es `now()`, la hora de inicio de la
  transacción; un "Pedir cambios" que empieza antes y confirma después de un
  "Aprobar" concurrente del mismo aprobador quedaría con `at` anterior y la
  aprobación seguiría contando. La mitad del hallazgo sobre `at` nulo no aplica:
  la columna es `not null` (`db/esquema.sql`, `create table approval`). Seguimiento
  **PENDIENTE**: serializar las decisiones sobre una misma tarea (bloqueo de la fila
  de `task` en `aprobar_tarea`/`pedir_cambios_tarea`) o volver a leer el estado
  dentro del mismo acto.

- 2026-09-27: **T6b cerrada — después de "Pedir cambios", la entrega pide evidencia
  nueva** (seguimiento de review-c112506a + decisión del usuario del mismo día).
  Ruta: delegada, un escritor. `evidencia_pendiente` cuenta sólo evidencia con `at`
  estrictamente posterior al último `approval` 'rechazado' de la tarea (de cualquier
  aprobador; empate falla cerrado; sin 'rechazado', sin cambio). `_actualizar_estado`
  registra siempre el `evidencia_texto` no vacío de la entrega (antes se descartaba
  en silencio si ya había evidencia). El gate de "Aprobar", el cierre y el menú
  ("Ya la terminé" vuelve a pedir evidencia) siguen solos porque llaman a la misma
  función. Migración `db/migrations/0014_evidencia_no_sobrevive_a_pedir_cambios.sql`
  y su rollback; **no aplicada todavía a la base local**. Enmienda fechada en ADR
  0009 (T6a y T6b). Cinco pruebas nuevas en `tests/test_entrega_con_evidencia.py`
  (sección 6); dos pruebas de T6a ajustadas para mandar evidencia nueva después del
  'rechazado' (siguen probando el empate y la aprobación vieja). Límite anotado: una
  evidencia que adjunta el aprobador después de pedir cambios también cuenta, igual
  que antes de esta unidad.
  RED (stash de `db/esquema.sql`/`herramientas.py`, pruebas nuevas presentes): `5
  failed, 1 passed`. GREEN enfocada (reejecutada por el orquestador): `pytest -q
  tests/test_entrega_con_evidencia.py tests/test_aprobacion_cierra_tarea.py
  tests/test_task_intake.py tests/test_menu_tarea.py` -> `146 passed`. Suite
  completa (escritor): `935 passed, 108 deselected`.
  Commit `12aecaa`. RDD: `review assess --base-ref f6c282a --committed-only` ->
  medio, `review_due` (`slice_budget_reached`); consentimiento del usuario: revisar.
  Revisión review-e719d807bbe9f356 (una lente, confiabilidad) aprobada y reconocida
  (autoridad quemada); frontera de revisión en `12aecaa`. Dos sugerencias no
  bloqueantes, seguimiento **PENDIENTE** (T6g): (1) falta una prueba del empate de
  evidencia (`evidence.at = rechazado.at` en la misma transacción -> sigue pendiente),
  para que un cambio de `>` a `>=` no pase inadvertido; (2) al registrar siempre el
  `evidencia_texto`, un `actualizar_estado(en_revision)` repetido sobre una tarea que
  ya está `en_revision` (por texto libre; la confirmación ya es de ejecución única)
  agrega otra fila de evidencia junto con el evento de mismo estado -- ligado al
  riesgo 3 de `docs/STATUS.md` (no hay grafo de transiciones), sin prueba hoy.

- 2026-09-27: **T6d cerrada — dedupe estable del aviso de entrega** (seguimiento de
  review-c112506a). Ruta: delegada, un escritor. Sin evidencia nueva, la clave del
  aviso al aprobador pasa de `uuid.uuid4()` a `f"{tarea_id}:{pg_current_xact_id()}"`
  (con evidencia sigue siendo `evidencia_id`): igual dentro del mismo acto, distinta
  entre actos. El orquestador rechazó una primera versión que derivaba la clave de
  la tarea, el estado de origen y el texto: entrega -> "Pedir cambios" -> reentrega
  sin evidencia repetía la clave y, como `message_outbox.dedupe_key` es `unique`,
  la segunda entrega quedaba sin avisar en silencio. La repetición del mismo acto
  entre transacciones no la cubre esta clave sino la ejecución única de la
  `pending_action` confirmada. `pg_current_xact_id()` exige PostgreSQL 13+
  (desarrollo: 18). Pruebas en `tests/test_entrega_con_evidencia.py` sección 7:
  repetición en la misma transacción -> un aviso; tarea sin política de evidencia,
  entrega -> pedir cambios -> reentrega -> dos avisos (RED contra la primera versión:
  `1 failed, 1 passed`); dos entregas con evidencia -> dos avisos. Seguimiento
  anotado, sin cambiar: `_avisar_dependencia_informativa` sigue recibiendo
  `uuid.uuid4()` desde `_actualizar_estado`, `_registrar_bloqueo` y
  `_resolver_bloqueo`.
  GREEN enfocada (reejecutada por el orquestador): `pytest -q
  tests/test_entrega_con_evidencia.py tests/test_menu_tarea.py
  tests/test_aprobacion_cierra_tarea.py` -> `66 passed`. Suite completa (escritor):
  `938 passed, 108 deselected`.
  Commit `2ab76bf`. RDD: `review assess --base-ref 12aecaa --committed-only` -> medio,
  `review_due` falso (`under_budget`, 236 líneas): queda pendiente en el tramo hasta
  que un commit siguiente alcance el presupuesto; la frontera sigue en `12aecaa`.

- 2026-09-27: **Revisión del tramo `12aecaa..dec6ae9`** (T6d `2ab76bf` + ADR 0010 y
  `odd/tasks/alta-y-google.md`). RDD: medio, `review_due` (`slice_budget_reached`,
  837 líneas); consentimiento del usuario: revisar. review-6b1efba15aab793d (una
  lente, confiabilidad) aprobada y reconocida (autoridad quemada); frontera en
  `dec6ae9`. Un WARNING y dos sugerencias no bloqueantes -> T6h.
- 2026-09-27: **Rama auxiliar creada.** `auxiliar/alta-y-google` en
  `D:\Proyectos\Prisma-PM-worktrees\alta-y-google`, desde `main` en `dec6ae9`
  (`aux` es un nombre reservado de Windows y git no pudo crear la carpeta de la
  referencia; se renombró). Alcance, contrato y fuentes en
  `odd/tasks/alta-y-google.md`; ADR 0010 en propuesta. `main` no cambia de
  comportamiento hasta la integración.

- 2026-09-27: **T6c cerrada — "Pedir cambios" vuelve al estado previo a la entrega.**
  Ruta: delegada, un escritor. Función nueva `estado_previo_a_revision` (misma puerta
  angosta que `estado_previo_a_bloqueo`: `security definer`, dueña `prisma_owner`,
  `execute` sólo para `prisma_app`); `exigir_dependencias_resueltas` exime
  `en_revision -> en_curso` cuando el estado previo a la revisión era `en_curso`;
  `_pedir_cambios_tarea` devuelve a `en_curso` o a `asignada` (cualquier otro previo
  -> `asignada`, que nunca saltea el gate), con vista previa, huella y aviso que
  nombran el destino; el chequeo previo de `_actualizar_estado` quedó consistente
  con el disparador. Migración `db/migrations/0015_pedir_cambios_exento_del_gate_de_arranque.sql`
  y su rollback; **no aplicada todavía a la base local** (tampoco 0013 y 0014).
  Enmienda de ADR 0009 ampliada. Seis pruebas nuevas (sección 8 de
  `tests/test_entrega_con_evidencia.py`); el helper `_tarea` de ese archivo ahora
  siembra un evento `en_curso` previo en las tareas `en_revision`.
  RED (stash de esquema y herramientas): `6 failed`. GREEN: `6 passed`. Enfocada
  (reejecutada por el orquestador): `pytest -q tests/test_entrega_con_evidencia.py
  tests/test_dependencias.py tests/test_task_intake.py` -> `144 passed`. Suite
  completa (escritor): `944 passed, 108 deselected`.
  Commit `9d400c8`. RDD: medio, `review_due` (`slice_budget_reached`, 538 líneas);
  consentimiento del usuario: revisar. review-09452c696da77aaa (una lente,
  confiabilidad) aprobada y reconocida; frontera en `9d400c8`. Un WARNING
  (eventos `en_revision -> en_revision` confunden a `estado_previo_a_revision`) y
  dos sugerencias de pruebas -> sumados a T6g. La cuarta sugerencia (la migración
  no se ejercita) no aplica: el ensayo de `tests/test_task_intake.py` aplica cada
  migración y su rollback y los comparó contra el esquema en esta misma suite.

- 2026-09-27: **T6e cerrada — "Pedir cambios" de punta a punta por Telegram.** Ruta:
  delegada, un escritor (sólo pruebas). `tests/test_pedir_cambios_extremo_a_extremo.py`
  maneja `POST /telegram/corework` con `TestClient` (toques y texto libre; el modelo
  sólo abre el menú, con `ProveedorGuionado`): entrega con evidencia -> aviso con
  botones al aprobador -> "Pedir cambios" con comentario y destino en la vista previa
  -> vuelve a `en_curso` y avisa al responsable -> reentrega que pide evidencia nueva
  (T6b) con un segundo aviso de clave distinta (T6d) -> "Aprobar" cierra la tarea
  (T6a, ADR 0008). Variante con dependencia bloqueante abierta (T6c). Sin defectos.
  Resultados: el archivo -> `2 passed` (reejecutado por el orquestador); suite
  completa (escritor): `946 passed, 108 deselected`.
  Commit `5c4f72a`. RDD: medio, `review_due` (`slice_budget_reached`, 426 líneas);
  consentimiento del usuario: revisar. review-8b7dde285b819238 (confiabilidad)
  aprobada y reconocida; frontera en `5c4f72a`. Un WARNING y una sugerencia sobre la
  prueba, sumados a T6g: (1) "el último mensaje" se elige con `order by
  programado_para desc limit 1` sin desempate, y dos filas pueden compartir hora;
  (2) no se verifica qué pasa con los botones del primer aviso después de "Pedir
  cambios" y de la reentrega.

- 2026-09-27: **T6g cerrada — entrega repetida sobre una tarea ya en revisión.** Ruta:
  delegada, un escritor. `_preparar_actualizar_estado`/`_actualizar_estado`: si la
  tarea ya está `en_revision`, no se inserta ningún `task_state_event`; con texto de
  evidencia, vista previa ("ya está en revisión · se suma la evidencia para quien la
  revisa") y al confirmar una fila de `evidence` más (igual que `_adjuntar_evidencia`,
  que no avisa a nadie); sin texto, "Esa tarea ya está en revisión.". Sin migración:
  la guarda sigue la convención de `_registrar_bloqueo` (no insertar un segundo
  evento del mismo estado) y ese insert es el único camino que produce
  `estado_nuevo = 'en_revision'`; `estado_previo_a_revision` queda igual. Siete
  pruebas nuevas (sección 9 de `tests/test_entrega_con_evidencia.py`): entrega
  repetida con y sin texto, "Pedir cambios" después de una entrega repetida sigue
  volviendo a `en_curso`, previo nulo -> `asignada`, vista previa sin confirmar de la
  restauración `en_revision -> en_curso`, empate de evidencia. Prueba de punta a
  punta: desempate por `dedupe_key` en "el último mensaje" y verificación de que los
  botones del primer aviso mueren al tocar "Pedir cambios" (`resolver_pendiente`
  resuelve la fila entera).
  Observación del escritor: si llega evidencia por una entrega repetida mientras el
  primer aviso sigue esperando, el aprobador puede aprobar desde ese aviso sin que
  nadie le haya mostrado la evidencia nueva (la aprobación lee la evidencia vigente;
  el aviso no se reenvía). Queda para decisión del usuario.
  RED (stash de herramientas): `4 failed` (las otras 3 cubren comportamiento que ya
  era correcto). GREEN enfocada (reejecutada por el orquestador):
  `tests/test_entrega_con_evidencia.py tests/test_pedir_cambios_extremo_a_extremo.py`
  -> `38 passed`. Suite completa (escritor): `953 passed, 108 deselected`.
  Commit `c9f1d1c`. RDD: medio, `review_due` falso (`under_budget`, 368 líneas):
  queda pendiente en el tramo desde `5c4f72a`.

- 2026-09-27: **T6i cerrada — evidencia nueva en revisión reemplaza el aviso del
  aprobador.** Ruta: delegada, un escritor; ajuste del orquestador antes del commit.
  `_avisar_evidencia_nueva_en_revision` (desde la entrega repetida de T6g y desde
  `_adjuntar_evidencia` cuando la tarea está `en_revision`): si quien suma la
  evidencia no es el aprobador, `pendientes.retirar_avisos_de_entrega` vence el aviso
  esperando (`estado = 'vencida'`, opciones inactivas; tocarlo contesta "ya no está
  vigente") y sale uno nuevo con la clave `evidencia_id`. El aviso lista ahora toda
  la evidencia del ciclo vigente (`_evidencia_vigente`: posterior al último
  'rechazado'), también en la primera entrega. El orquestador cambió cómo se
  reconoce el aviso: el escritor lo distinguía del menú general por la ausencia del
  botón "Quiero consultar otra cosa"; ahora el aviso lleva `args.aviso =
  AVISO_ENTREGA` y el filtro es por esa marca (los avisos ya registrados sin marca
  no se retiran; sólo existen en la base local de datos ficticios). Límite: el
  mensaje viejo sigue visible en Telegram con sus botones inertes, porque el
  transporte no sabe editar mensajes (`despachador.Transporte` sólo envía). Enmienda
  de ADR 0009, punto 4.
  RED (fuente revertida con `git show HEAD:<ruta>`): 4 de 5 pruebas nuevas fallaron
  (la quinta, el aprobador suma su propia evidencia, pasa también con el código
  viejo porque antes nunca se avisaba). GREEN tras el ajuste del orquestador:
  `pytest -q tests/test_entrega_con_evidencia.py tests/test_pedir_cambios_extremo_a_extremo.py
  tests/test_menu_tarea.py tests/test_aclaracion_botones.py` -> `95 passed`. Suite
  completa (escritor, antes del ajuste): `957 passed, 1 failed, 108 deselected`; la
  falla, `test_task_intake.py::test_migration_preflight_fails_before_ddl_for_incompatible_unit1a_rows[converted_waiting]`
  (`tuple concurrently updated`), coincidió con el experimento 1 aplicando
  migraciones en el mismo servidor (catálogo de roles compartido por el clúster);
  reejecutado aparte, `tests/test_task_intake.py` completo junto con las pruebas de
  T6i -> `126 passed`.
  Commit `d6c08ac`. RDD sobre el tramo `5c4f72a..d6c08ac` (T6g + T6i): medio,
  `review_due` (`slice_budget_reached`, 880 líneas); consentimiento del usuario:
  revisar. review-ae0ab5100f07401d (confiabilidad) aprobada y reconocida; frontera en
  `d6c08ac`. Dos WARNING y una sugerencia, sumados a T6f (concurrencia de avisos y
  pruebas faltantes).

- 2026-09-27: **Experimento 1 — validador de invariantes sobre una copia de la base
  local** (sólo lectura: `pg_dump` de la base local, restaurada en una base
  descartable ya borrada; ningún texto de mensaje en el informe). Las migraciones
  `0013`, `0014` y `0015` aplicaron limpio sobre la copia con datos de forma real.
  De trece chequeos, uno encontró algo: dos tareas `en_revision` con una aprobación
  y ninguna evidencia aunque su política la exige; son los hallazgos 8 y 9 de la
  sesión 2 (aprobar a ciegas), anteriores a ADR 0009 -- el cierre las siguió frenando.
  El resto en cero (cierre, proyección del estado, bloqueos, gate de arranque
  reconstruido por hora, cadena de aprobación, pendientes, cola de salida, personas
  sin respuesta, incidentes sin aviso, `workspace_id` cruzado). Dos datos laterales:
  (1) la base local con los datos de las sesiones es la base de mantenimiento
  `postgres` del servidor, la misma a la que apunta `PRISMA_TEST_DB_URL` (las
  pruebas crean bases propias y no escriben ahí, pero conviven en el mismo lugar);
  (2) quedan bases residuales `prisma_diag_*`/`prisma_test_*` de corridas viejas.
  Chequeos que valen para un validador diario: evidencia faltante en revisión,
  gate de arranque por hora, `workspace_id` cruzado (hoy sin constraint en esas
  tablas), proyección del estado, personas sin respuesta.

- 2026-09-27: **Experimento 3 — opinión sombra Jev contra el modelo en el banco real.**
  Sin tocar el repositorio (plugin de medición en el scratchpad, cargado con `-p`).
  Comando: `pytest -m modelo_real tests/banco -p exp3_instrumentacion --banco-n 1
  --banco-proveedor nan --banco-modelo deepseek-v4-flash -k "<14 escenarios con
  referencias>"` -> `12 passed, 2 failed` (163 s); veredictos: aprobado 10,
  no_concluyente 2 (`b-0002`, `b-0003`), falla 2 (`b-0005-b`, `b-0013`).
  Resultado: **cero desacuerdos**; el modelo nunca actuó sobre una tarea distinta de
  la que Jev resolvió clara. No es una señal independiente: la resolución clara de
  Jev entra al turno como instrucción ("Usá esa tarea; no la vuelvas a resolver",
  `gateway.py`), así que un desacuerdo mediría desobediencia, no una segunda
  opinión. La idea, en su forma original, no se adopta. Hallazgos laterales del
  banco: (1) `b-0013` falla porque el comprobador compara la etiqueta del botón
  entera y ahora las etiquetas se acortan con "…" (efecto de `e7071eb`/`2bee9a9`
  sobre el comprobador, no sobre Prisma); (2) `b-0002`/`b-0003` quedan no
  concluyentes porque el comprobador de nombres toma "Bloqueada Todavía" y
  "Asignada Todavía" como nombres propios (falso positivo); (3) `b-0005-b`, ya
  conocido. `audit_log` ya guarda la resolución de Jev y cada llamada del modelo,
  pero sin una clave de turno que las una.

- 2026-09-27: **T6f y T6h cerradas — actos serializados por tarea y seguimientos del
  aviso de entrega.** Ruta: delegada, un escritor; una corrección pedida por el
  orquestador antes del commit. `_bloquear_tarea` toma `pg_advisory_xact_lock` por
  tarea al empezar `_actualizar_estado`, `_adjuntar_evidencia`, `_aprobar_tarea` y
  `_pedir_cambios_tarea` (`prisma_app` no tiene `update` sobre `task`, así que `for
  update` falla por permisos; el bloqueo consultivo es el mismo recurso que ya usa
  `ingreso_tareas.start`). Corrección del orquestador: el bloqueo ordena los actos,
  pero `approval.at`, `evidence.at` y `task_state_event.at` tomaban `now()`, la hora
  de inicio de la transacción, que en el gateway empieza mucho antes de la
  herramienta; un "Pedir cambios" que arrancó antes y esperó el bloqueo quedaba con
  hora anterior a la aprobación que ganó. Ahora esas ocho escrituras fijan
  `at = clock_timestamp()` después del bloqueo. T6h: `pg_current_xact_id()` sólo sin
  `evidencia_id`; `_notificar_entrega_al_aprobador` no registra botones si el aviso
  con esa clave ya existe (antes quedaba una `pending_action` esperando sin mensaje:
  defecto real que marcó review-6b1efba1); pruebas de la forma de la clave, del menú
  general del aprobador que no se retira y de la evidencia previa al 'rechazado' que
  no aparece en el aviso. PostgreSQL mínimo: `db/esquema.sql` ya fija 18 o posterior.
  RED: `3 failed, 3 passed` (sin el arreglo; las 3 que pasan fijan comportamiento que
  ya era correcto) y, para la corrección, las dos pruebas nuevas fallan con el bloqueo
  pero sin `clock_timestamp()` (`at_rechazado > at_aprobado` falso). GREEN enfocada
  (reejecutada por el orquestador): `tests/test_entrega_con_evidencia.py
  tests/test_aprobacion_cierra_tarea.py tests/test_pedir_cambios_extremo_a_extremo.py`
  -> `58 passed`. Suite completa (escritor): `966 passed, 108 deselected`.
  Commit `48b6c8a`. RDD sobre `d6c08ac..48b6c8a`: medio, `review_due`
  (`slice_budget_reached`, 1091 líneas con la documentación de los experimentos);
  consentimiento del usuario: revisar. review-5085907da1b3a798 (confiabilidad)
  aprobada y reconocida; frontera en `48b6c8a`. Un WARNING (prueba de botones
  huérfanos sin chequear el estado de la acción que queda) y una sugerencia (relojes
  mezclados entre escritores) -> T6j.

- 2026-09-27: **T6j cerrada — la hora de escritura como regla del esquema.** Ruta:
  delegada, un escritor. El `default` de `at` en `task_state_event`, `evidence` y
  `approval` pasa de `now()` a `clock_timestamp()`
  (`db/migrations/0016_hora_de_escritura_como_regla_del_esquema.sql` y su rollback;
  **no aplicada todavía a la base local**, igual que 0013-0015). Los cuatro actos
  bloqueados conservan su `clock_timestamp()` explícito. `blocker` no hace falta:
  nadie lo ordena por `at` contra esas tablas. Pruebas: la de botones huérfanos
  ahora exige que la acción que queda esté `esperando` y sea la del único mensaje;
  una nueva prueba que el `default` ordena por hora de escritura entre dos
  transacciones; la prueba del empate de evidencia fuerza el empate a mano, porque
  con `clock_timestamp()` dos filas de una misma transacción ya no comparten hora.
  `tests/test_task_intake.py::_retrato_de_aislamiento` suma `column_default`: sin eso,
  una migración que sólo cambia un `default` no cambiaba "nada observable" para el
  ensayo de rollback. Enfocada (reejecutada por el orquestador, junto con el banco):
  `288 passed`. Suite completa (escritor): `974 passed, 108 deselected`.

- 2026-09-27: **Banco: comprobadores al día** (hallazgos laterales del experimento 3).
  Ruta: delegada, el mismo escritor. `comprobar_aclaracion` acepta la etiqueta
  acortada por palabra con "…" (misma regla que `truncar_etiqueta_boton`) y sigue
  rechazando una tarea equivocada; `comprobar_personas_mencionadas` suma los estados
  legibles y "Todavía" al vocabulario conocido, sin dejar de detectar nombres
  inventados. Sólo `tests/banco/`. Pruebas unitarias del banco: `tests/banco/test_corrida.py`
  -> `57 passed` (escritor); RED/GREEN sobre las cuatro pruebas positivas nuevas.
  No se corrió el banco real.
  Revisión del tramo `48b6c8a..86a55d9` (T6j + comprobadores): RDD **alto**
  (`process_boundary`: `tests/test_task_intake.py` lanza procesos), `review_due`;
  consentimiento del usuario: revisar. review-2c5b0ffee96f45c2, cuatro lentes
  (riesgo, resiliencia, legibilidad, confiabilidad), aprobada y reconocida; frontera
  en `86a55d9`. Sin bloqueantes. Seguimientos **PENDIENTE** (T6k): (1) el comprobador
  de aclaración no empareja candidatas y etiquetas uno a uno, así que una etiqueta
  acortada que comparte palabras iniciales puede satisfacer dos candidatas y dar un
  falso "aprobado"; (2) la prueba nueva de dos conexiones entra y sale del contexto
  de administración a mano, sin `try/finally`, y una falla a mitad puede dejar una
  transacción abierta que traba el teardown; (3) la prueba que dice cubrir el corte
  en palabra no llega a esa rama; (4) el `- 1` del corte duro sin explicar, la
  importación del privado `_ESTADOS_LEGIBLES` y el registro que acredita las pruebas
  del banco a `test_corrida.py` cuando están en `test_comprobadores.py`.

- 2026-09-27: **T7 cerrada — base nueva y siembra reproducible.** Ruta: delegada, un
  escritor; dos agregados pedidos por el orquestador. `espacios/corework.semilla-ficticia.yaml`
  (12 tareas extraídas en sólo lectura de la base de las sesiones, títulos sin
  "(simulado)", cada una colgada de un frente real del pack, fecha objetivo relativa
  al día de siembra, `evidencia_requerida: [explicacion]`), `src/prisma/siembra.py` y
  el comando `python -m prisma sembrar corework --semilla <archivo>`. Estados
  iniciales: seis `en_curso` (una por responsable; una con dependencia bloqueante
  abierta, creada después de arrancar, sin saltear el gate) y seis `asignada`; ninguna
  aprobada ni en revisión. Todo por eventos (`bloquear_estado_directo` rechaza la
  escritura directa incluso como administrador). Camino: inserts administrativos, no
  `confirmar_borrador_tarea` (ese es el compromiso de un borrador por Telegram, con su
  vista previa y la conexión de autoridad). Rechaza si el espacio ya tiene tareas o
  no existe; una sola transacción. Agregados del orquestador: una fila de
  `audit_log` por siembra (`siembra_ficticia`, `actor_kind='sistema'`, sólo
  cantidades y el nombre del archivo) y `evidencia_policy_version` tomada de
  `task_evidence_policy` del área, igual que el alta real (el vacío que encontró el
  experimento 1 era de la carga a mano). Pasos para el usuario en `PRUEBA-LOCAL.md`
  §5 (respaldo, `create database prisma`, cambiar sólo el nombre de la base en
  `PRISMA_DB_URL` y, si apunta a la misma base, en `PRISMA_AUTHORITY_DB_URL`,
  `esquema`, `importar`, `feriados`, `sembrar`, `enlaces`, `escuchar`).
  RED: sin `siembra.py` no se recolectan las pruebas; para los agregados, `3 failed`.
  GREEN (reejecutado por el orquestador): `tests/test_siembra.py tests/test_esqueleto.py
  tests/test_onboarding.py` -> `51 passed`. Suite completa (escritor): `988 passed,
  108 deselected`.
  Commit `e71cfa0`. RDD sobre `86a55d9..e71cfa0`: **alto** (`process_boundary` en
  `src/prisma/cli.py`), `review_due`; consentimiento del usuario: revisar.
  review-943484ef642de774, cuatro lentes, aprobada y reconocida; frontera en
  `e71cfa0`. Seguimientos atendidos en T7b antes de que el usuario corra los pasos:
  errores del comando sin traza cruda (podía mostrar títulos en el DETAIL de la
  base), validación completa antes del primer insert (títulos repetidos,
  dependencias a títulos inexistentes, estados permitidos sólo `asignada`/`en_curso`),
  día de siembra en la zona horaria del espacio, pruebas que prometían más de lo que
  chequeaban, y la redacción de `PRUEBA-LOCAL.md` sobre cuál es el respaldo real. No
  aplica la observación sobre la versión de política "arbitraria":
  `task_evidence_policy` tiene clave primaria `(workspace_id, area_id)`.

- 2026-09-27: **T7b cerrada — endurecimiento de `sembrar`** (seguimientos de
  review-943484ef). Ruta: delegada, un escritor. El comando termina con mensaje claro
  y código 1 ante archivo faltante, YAML vacío o mal formado, clave faltante o rechazo
  de la base, y nunca imprime el DETAIL de la base (podía contener títulos); vuelve
  atrás la conexión. `sembrar` valida todo antes del primer insert (claves, títulos
  repetidos -- antes se chequeaba después de insertar --, estados permitidos
  `asignada`/`en_curso`, área, objetivo, responsable, política y dependencias); el
  día de siembra se calcula en la zona horaria del espacio; `objective.titulo` no es
  único en el esquema, así que un objetivo ambiguo se rechaza en vez de elegir uno.
  Pruebas: la de orden legal ahora compara el orden de escritura (`dependency` no
  tiene columna de hora; se usa `cmin` dentro de la misma transacción), seis
  `en_curso` y seis `asignada`, y tres pruebas del comando por `prisma.cli.main`.
  `PRUEBA-LOCAL.md` §5 aclara que el respaldo real es el `pg_dump` del paso 1.
  RED: `18 failed, 16 passed`. GREEN (reejecutado por el orquestador):
  `tests/test_siembra.py tests/test_esqueleto.py tests/test_onboarding.py` ->
  `71 passed`. Suite completa (escritor, corrida aislada): `1008 passed, 108 deselected`.
  Commit `4885703`. RDD sobre `e71cfa0..4885703`: **alto** (`cli.py`), `review_due`;
  consentimiento del usuario: revisar. review-05906dd38845fe09, cuatro lentes,
  aprobada y reconocida; frontera en `4885703`. Seguimientos no bloqueantes
  **PENDIENTE** (T7c): el `rollback` dentro de los `except` puede fallar si la
  conexión se cortó y dejar una traza cruda; valores de YAML que no son texto
  (listas o mapas en `titulo`/`estado_inicial`/dependencias, `tareas` escalar) escapan
  como `TypeError`; criterio único sobre si los títulos pueden salir en los mensajes
  de validación; falta una prueba del día de siembra en la zona del espacio; las
  pruebas del comando buscan "Traceback" en `stdout` cuando va a `stderr`; tipar las
  tareas validadas. Ninguno afecta una siembra con el archivo versionado.

- 2026-09-28 (orquestador): **pasos 1 y 2 de `PRUEBA-LOCAL.md` §5 hechos.** Respaldo
  `db/respaldos/prisma-antes-base-nueva-20260928.dump` (263.842 bytes, formato
  personalizado de `pg_dump` sobre la base `postgres`; `pg_restore -l` lo lee: 46
  entradas de datos, entre ellas `task`, `task_state_event`, `approval`, `evidence`;
  no se ensayó una restauración completa de este archivo). Base vacía `prisma`
  creada en el mismo servidor. La base `postgres` sigue intacta (12 tareas). Sin
  imprimir la URL ni credenciales (cargadas como las carga la suite). Quedan para el
  usuario los pasos 3 a 7.

- 2026-09-28 (usuario): **base nueva lista y listener corriendo.** El usuario cambió
  `PRISMA_DB_URL` y `PRISMA_AUTHORITY_DB_URL` a la base `prisma` y corrió `esquema`
  ("Esquema aplicado."), `importar corework --activar` (v1, activo; 4 personas sin
  Telegram), `feriados corework`, `sembrar` ("12 tareas y 1 dependencias sembradas.
  asignada: 6, en_curso: 6") y `escuchar corework`. `enlaces --solo Ismael Ariel Marcos`
  respondió "No hay nadie pendiente de activar": el pack ya trae el
  `telegram_user_id` de esas tres personas, así que el import las dejó vinculadas.
  Tercera ronda en curso.

- 2026-09-28: **T6k cerrada — seguimientos de review-2c5b0ffe.** Ruta: delegada, un
  escritor. `comprobar_aclaracion` empareja candidatas y etiquetas uno a uno (una
  etiqueta acortada ya no satisface dos candidatas con el mismo comienzo); la prueba
  de dos conexiones usa `ExitStack` + `try/finally`; una prueba nueva cubre de verdad
  el corte a mitad de palabra; `_LARGO_MAXIMO_PREFIJO_CORTE_DURO` nombra el `- 1`;
  `herramientas.ESTADOS_LEGIBLES` pasa a ser público y el banco lo importa por ese
  nombre. RED/GREEN observado. Enfocada: `tests/banco/test_comprobadores.py
  tests/banco/test_corrida.py tests/test_entrega_con_evidencia.py` -> `208 passed`
  (escritor); reejecutada por el orquestador junto con T7c -> `195 passed`
  (`test_comprobadores`, `test_siembra`, `test_entrega_con_evidencia`). Suite completa
  (escritor): `1021 passed, 108 deselected`.

- 2026-09-28: **T7c cerrada — seguimientos de review-05906dd3 sobre `sembrar`.** Ruta:
  delegada, el mismo escritor. `rollback` protegido (`cli._revertir_sin_traza`) para
  que una conexión cortada no termine en traza cruda; tipos validados antes de
  cualquier comparación (listas y textos), siempre `SiembraInvalida`; regla única en
  el módulo: los mensajes de validación pueden nombrar valores del archivo de
  siembra, los errores de la base nunca muestran su DETAIL; `sembrar(ahora=...)`
  inyectable y prueba del día en la zona del espacio (01:00 UTC del 1/1 sigue siendo
  31/12 en Buenos Aires); las pruebas del comando miran también `stderr`;
  `_TareaPreparada` en lugar de diccionarios. RED/GREEN observado. `tests/test_siembra.py`
  -> `44 passed` (escritor). Suite completa (escritor): `1021 passed, 108 deselected`.
  Commits `3140a45` (T6k) y `cb9cd2d` (T7c). RDD sobre `4885703..cb9cd2d`: **alto**
  (`cli.py`), `review_due`; consentimiento del usuario: revisar.
  review-022fb782dc763215, cuatro lentes, aprobada y reconocida; frontera en
  `cb9cd2d`. Sugerencias menores sobre `sembrar` (T7d, sin urgencia: `ahora` sin zona
  aceptado en silencio, `tareas: {}` falsos aceptados como lista vacía, el `except`
  amplio de `_revertir_sin_traza`, el nombre `_LARGO_MAXIMO_...` usado como mínimo) y
  una advertencia sobre `docs/STATUS.md` con la línea base vieja (se corrige al cierre).

- 2026-09-28: **Hallazgo 10 cerrado y seguimientos de review-149a33fa.** Ruta: delegada,
  un escritor. Causa real: al tocar "Quiero consultar otra cosa" sobre una pregunta del
  modelo, `gateway._resolver_toque_opcion_modelo` cerraba con un texto fijo ("Dale,
  escribime qué necesitás."), y `contexto.historial` -- que se arma sólo con
  `message_outbox`/`inbound_message` -- no mostraba que la pregunta se había
  descartado; un saludo alcanzaba para que el modelo la reabriera. Arreglo: el cierre
  nombra la pregunta descartada ("Dale, dejamos de lado «…». Escribime qué
  necesitás.", `_texto_cierre_opciones`), en la misma fila de la cola que el historial
  ya lee, y el preámbulo le dice al modelo que no la reabra salvo que la persona vuelva
  al tema. Seguimientos: (1) *pregunta suprimida*: con texto largo que se parte, el
  rótulo de los botones volvía a poner la pregunta; ahora usa "Elegí una opción:"
  (`agente._encolar_opciones_modelo`); (2) *etiquetas repetidas del modelo*:
  `_ofrecer_opciones` rechaza dos botones con la misma etiqueta final para que el
  modelo reintente; (3) *asserts*: las dos pruebas de `2bee9a9` comparan ahora contra el
  valor exacto de `etiquetas_boton_distinguibles`. RED/GREEN observado por separado en
  cada arreglo. Enfocada (reejecutada por el orquestador): `tests/test_opciones_modelo.py
  tests/test_memoria.py tests/test_lista_botones.py tests/test_menu_tarea.py
  tests/test_pregunta_sin_opciones.py` -> `101 passed`. Suite completa (escritor):
  `1027 passed, 108 deselected`.

- 2026-09-28: **`b-0005-b` cerrado — el router reformula cada referencia como el
  trabajo al que apunta** (decisión del usuario del 2026-09-27: ni bajar
  `jev.CORTE_CLARA` ni darle más contexto a Jev). Ruta: delegada, un escritor.
  `llm.ROUTER_TOOL`/`ROUTER_SYSTEM`: en `trabajos` va el trabajo (acción + objeto, en
  el idioma del mensaje) en lugar de la copia literal, con guardas explícitas: no
  inventar detalles, nombres de personas sólo en `personas`, una mención vaga sigue
  igual de vaga (no elegir candidata), y ningún trabajo inventado cuando la mención
  no apunta a trabajo real. Banco real completo n=1 (`nan`/`deepseek-v4-flash`, 36
  escenarios), mismo código salvo el cambio: antes
  `banco-20260928T111730Z.json` -> 29 aprobado, 7 falla (b-0001, b-0001-a, b-0001-b,
  b-0002-c, b-0005-b, b-0013, b-0016); después `banco-20260928T113448Z.json` -> 32
  aprobado, 4 falla (b-0001, b-0001-a, b-0002-c, b-0013, las cuatro ya fallaban antes).
  Ningún escenario empeoró; mejoraron b-0001-b, b-0005-b y b-0016. Los de guarda
  (b-0008, b-0009, b-0010, b-0014) siguieron aprobados: Prisma sigue preguntando en vez
  de adivinar. Límite honesto: una sola corrida por escenario (n=1), así que las
  mejoras de b-0001-b y b-0016 pueden ser ruido; no se corrió n=3. **Abierto**: b-0001,
  b-0001-a, b-0002-c y b-0013 fallan en las dos corridas, sin relación con las
  referencias; revisar por qué (b-0013 sigue fallando después de arreglar su
  comprobador). Determinista: `tests/test_llm_protocol.py
  tests/test_resolucion_referencias.py` -> `139 passed` (reejecutado por el
  orquestador); suite completa (escritor): `1027 passed, 108 deselected`.

- 2026-09-28 (usuario): **la tercera ronda por Telegram queda pendiente para la próxima
  sesión.** No se llegó a probar ningún circuito. La base `prisma` queda lista y
  sembrada (12 tareas: seis `en_curso`, seis `asignada`, una dependencia bloqueante),
  con Ismael, Ariel y Marcos ya vinculados. Guion de la ronda: circuito A (Ariel
  entrega "Dashboard de lotes en CoreLabs" con evidencia -> Ismael pide cambios -> Ariel
  vuelve a entregar con evidencia nueva -> el botón viejo del aviso dice que ya no
  está vigente -> Ismael aprueba desde el aviso nuevo y la tarea se cierra) y circuito
  B (Marcos entrega "Revisar comunicaciones industriales de la comprimidora", que
  depende de "Programar PLC" sin terminar -> Ismael pide cambios y la tarea vuelve a
  `en_curso`). Antes de arrancar: reiniciar el listener para que cargue el código ya
  commiteado.

- 2026-09-28: **#28 cerrada — cada incidente se avisa también al administrador de
  plataforma** (decisión del usuario; `nucleo/constitucion.md` §10 ya lo exigía y no se
  cumplía: hasta hoy sólo se avisaba a la persona afectada). Ruta: delegada, un
  escritor; corrección del usuario a mitad de camino: el aviso incluye el texto que
  disparó la falla (constitución §2: el administrador accede a las conversaciones;
  §12: ese acceso se audita). `message_outbox` no sirve para esto (exige espacio y
  membresía; los administradores son globales), así que hay tabla nueva
  `admin_notice` y función `security definer` `avisar_incidente_admin` (mismo patrón
  que `emitir_acceso_tablero`), columna `incident.notificado_admin_en`, migración
  `db/migrations/0017_aviso_incidente_administracion.sql` y su rollback. Un único punto
  de entrada, `src/prisma/incidentes.registrar_incidente()`, reemplaza los `insert into
  incident` repartidos. El aviso lleva el texto de la persona (o el resumen de la acción
  tocada) hasta 1000 caracteres, quién, etapa, severidad, resumen saneado, id,
  espacio y hora; nunca `referencia_cruda` (puede traer secretos). Cada aviso deja una
  fila de `audit_log` (`aviso_incidente_admin`, sólo ids). Alcanzable = el
  administrador ya le escribió alguna vez al bot de administración (Telegram no deja
  que un bot inicie la conversación). `local.tareas_de_fondo` despacha los avisos
  con `despachador.despachar_avisos_admin`; sin `PRISMA_BOT_TOKEN_ADMIN` quedan en cola.
  Hallazgo lateral: en modo `servir` nadie despacha `message_outbox` ni
  `admin_notice` (`reloj.py` sólo encola) -- entra en #29. RED/GREEN observado (el RED
  encontró que la auditoría no recibía la referencia). Enfocada (reejecutada por el
  orquestador): `tests/test_avisos_admin.py tests/test_gateway.py
  tests/test_capacidades.py tests/test_task_intake.py` -> `102 passed`. Suite completa
  (escritor, dos veces): `1037 passed, 108 deselected`. **Migración 0017 no aplicada a
  la base `prisma`**: aplicarla antes de reiniciar el listener.
  Revisión del tramo `cb9cd2d..dd6ab0a` (hallazgo 10, `b-0005-b`, #28): medio,
  `review_due`; consentimiento del usuario: revisar. review-1b0a5a4777341c90
  (confiabilidad) aprobada y reconocida; frontera en `dd6ab0a`. Dos WARNING reales
  -> **#28b**, primero en la próxima sesión: sin espera entre reintentos, un aviso al
  administrador que agota sus intentos queda `fallido` sin incidente ni aviso (viola
  "nunca fallar en silencio"); `local._obtener_transporte_admin` cachea la ausencia del
  token para toda la vida del proceso.

- 2026-09-28: **Cierre de sesión.** Punto exacto para retomar en `docs/STATUS.md`
  ("Punto exacto para retomar"). Tercera ronda por Telegram pendiente.

- 2026-09-28: **#28b cerrada — los avisos al administrador ya no fallan en silencio.**
  Ruta: delegada, un escritor (4 archivos de código y pruebas: disparador de escritura).
  TDD estricto: ROJO observado (`ImportError` de `BACKOFF_MINUTOS_AVISO_ADMIN`), VERDE
  tras la implementación. `despachar_avisos_admin` pospone cada reintento 1, 2, 4 y 8
  minutos; un aviso que agota `MAX_INTENTOS` deja un incidente de severidad alta
  (`referencia_tipo = 'admin_notice'`, texto libre sin restricción en el esquema) con
  `registrar_incidente(..., avisar_admin=False)`: sin ese freno, el incidente encolaría
  otro aviso por el mismo canal caído y se encadenaría sin fin. `notificado_admin_en`
  queda nulo y el resumen lo dice. El listener imprime cada aviso agotado.
  `_obtener_transporte_admin` ya no cachea la falta del token: relee `.env` (sin pisar
  el entorno) como mucho una vez por minuto y avisa una sola vez por consola.
  `tests/test_avisos_admin.py` -> `14 passed`; con `tests/test_capacidades.py` ->
  `17 passed`. Suite completa (escritor): `1037 passed, 108 deselected, 4 failed`; las
  4 son `test_aprobacion_cierra_tarea.py::test_mensaje_post_confirmacion_*`, que fijan
  `AHORA = 2026-09-27 10:00` y vencen con el reloj real desde el 2026-09-28 10:00
  (Buenos Aires), ajenas a este cambio -> tarea nueva. Confirmado sin tocar:
  `despachador._fallo` (`message_outbox`) también reintenta sin espera en horario
  laboral, porque `cal.dentro_de_jornada(ahora)` devuelve `ahora`.
  Migración `0017` aplicada a la base `prisma` con respaldo previo
  (`db/respaldos/prisma-antes-0017-20260928.dump`). Hallazgo al preparar la ronda: en
  modo local el administrador no es alcanzable. La base `prisma` no tiene ningún
  `platform_role` 'administrador' y ningún comando lo asigna, y `escuchar` no lee el bot
  de administración (`mensaje_admin` sólo se registra por el webhook de `servir`) ->
  tarea nueva, antes de la ronda.
  Decisión del usuario: la tercera ronda por Telegram va al final, después de los
  íconos por categoría (pack 06), el indicador de "pensando" (pack 05) y el resto de
  lo pendiente, para probar todo junto.
  Revisión de `ce771be` (#28b): medio, `review_due` (`slice_budget_reached`);
  consentimiento del usuario: revisar. review-cc9552ab8c6e284c (confiabilidad)
  aprobada y reconocida; frontera en `ce771be`. Dos hallazgos no bloqueantes -> #28c.

- 2026-09-28: **Fecha fija en `tests/test_aprobacion_cierra_tarea.py`.** Ruta:
  delegada, un escritor. `AHORA = datetime.now(BA)`: el webhook resuelve el pendiente
  contra el reloj real, así que un `AHORA` fijo nacía vencido. ROJO `4 failed, 3
  passed`; VERDE `7 passed`. Suite completa (escritor): `1041 passed, 108 deselected`.
  Con el mismo patrón de fecha fija, sin romperse hoy porque no pasan por el reloj
  real: `tests/test_botones.py:84`, `tests/test_modificar.py:142`,
  `tests/test_pendientes.py:43` y `:182`.
  Evaluación de `d50b385` contra la frontera `ce771be`: medio, `under_budget` (27
  líneas), queda pendiente en la rebanada.

- 2026-09-28: **#28c cerrada — seguimientos de review-cc9552ab.** Ruta: delegada, un
  escritor. R3-001: la prueba del `.env` releído dejaba `PRISMA_BOT_TOKEN_ADMIN` en el
  entorno (`delenv(raising=False)` sin nada que restaurar y `recargar_dotenv` escribe
  con `setdefault`); ahora `setenv` + `delenv` registran siempre el deshacer. R3-002:
  el incidente de un aviso agotado se escribe dentro de un savepoint; si falla, el lote
  se confirma igual (los avisos ya entregados no se reenvían), se cuenta en
  `incidentes_sin_registrar`, el listener lo imprime y `ultimo_error` lleva una marca.
  ROJO/VERDE observados por el escritor. `tests/test_avisos_admin.py` -> `15 passed`;
  suite completa (escritor): `1042 passed, 108 deselected`. Incidente de seguridad de
  la sesión: una aserción sobre `os.environ` hizo que pytest imprimiera el entorno
  completo, con el token real del bot de administración, en la salida de una
  herramienta del escritor; se reescribió la aserción para que no pueda volver a
  imprimirlo y se recomendó al usuario rotar el token.

- 2026-09-28: **Administrador alcanzable en modo local (T11 de la sesión).** Ruta:
  delegada, un escritor (el primer intento se cortó por el límite de uso, sin dejar
  cambios; se relanzó igual). `python -m prisma administrador <espacio> <nombre>`:
  busca entre los integrantes activos por fragmento del nombre, prefiere la
  coincidencia exacta (ajuste del orquestador: es un rol privilegiado), frena si hay
  cero o varias, otorga `platform_role` de forma idempotente y audita
  `otorgar_administrador` sólo cuando es nuevo. `Escucha.recibir_admin` sondea el bot de
  administración con `timeout=0` y offset propio, y enruta cada update por
  `procesar_update(conn, "admin", ...)`; un error queda como incidente global.
  Ajuste del orquestador por seguridad: los errores de red se imprimen sin su mensaje
  (`_error_sin_url`), porque el de httpx trae la URL y la URL lleva el token; también
  en `recibir`, que ya lo hacía antes. ROJO/VERDE del escritor (comando inexistente,
  método inexistente) y del orquestador para la coincidencia exacta (`«mar» es
  ambiguo`, 3 personas); la prueba de `_error_sin_url` se escribió después del cambio.
  Suite completa del escritor: `1051 passed, 108 deselected`; con los ajustes y sus
  dos pruebas, orquestador: `1053 passed, 108 deselected`. Pendiente del
  administrador: el bot no le responde nada cuando le escribe (sólo identifica y
  audita), así que no hay confirmación visible de que quedó vinculado.
  Revisión de `d50b385..ce78ba4`: alto (`high_risk`, 914 líneas); consentimiento del
  usuario: revisar. review-ba8899a3e4982579 (4 lentes) aprobada y reconocida; frontera
  en `ce78ba4`. Hallazgos no bloqueantes -> #11b.

- 2026-09-28: **#11b cerrada — seguimientos de review-ba8899a3.** Ruta: delegada, un
  escritor. R1-001/R4-001/R3-002: `escuchar` ya no borra a ciegas el webhook del bot de
  administración; consulta `getWebhookInfo` y, si hay uno puesto, no lo toca ni sondea,
  avisa una vez (sólo el host) y vuelve a consultar cada minuto; una consulta fallida se
  avisa y se reintenta. R2-001: `_token_admin_resuelto` hace explícito el token.
  R2-002/R2-003: docstrings corregidos. R3-001: la prueba del savepoint ahora falla
  dentro de la base (`select 1/0`); sin el savepoint da `InFailedSqlTransaction` (ROJO
  observado), con él pasa. `PRUEBA-LOCAL.md` explica cómo sacar a mano un webhook viejo
  del bot de administración local. Suite completa (escritor): `1056 passed, 108
  deselected`. Sin cambios: el `deleteWebhook` del bot del espacio al arrancar
  `escuchar`, anterior a esta unidad.
  Revisión de `1117e5d`: alto (`high_risk`); consentimiento del usuario: revisar.
  review-c4440d6c45ac75c2 (4 lentes) aprobada y reconocida; frontera en `1117e5d`.
  Hallazgos no bloqueantes -> #11c.

- 2026-09-28: **#11c cerrada — seguimientos de review-c4440d6c.** Ruta: delegada, un
  escritor. El aviso de consola y `PRUEBA-LOCAL.md` dicen que un webhook sacado a mano
  se detecta dentro de un minuto (no "la vuelta siguiente"); `getWebhookInfo` baja a 5 s
  de timeout; token y transporte del bot de administración viven juntos en `_AdminBot`,
  sin la guarda muerta; `_obtener_transporte_admin(ahora=...)` permite probar la espera
  de un minuto: ROJO observado anulando la condición (`2 == 1`), VERDE con ella. Suite
  completa (orquestador): `1057 passed, 108 deselected`. La corrida del escritor tuvo 2
  fallas `tuple concurrently updated` en `tests/test_task_intake.py` que pasan aisladas
  (la intermitencia ya documentada).
  Decisión del usuario: las cadencias se configuran desde la plataforma (tablero de
  cliente) y un cambio toma efecto sin reiniciar; quedó explícito en
  `docs/ROADMAP.md` (`94a323d`) y es requisito de #29.
  Evaluación de `a46d92c` contra la frontera `1117e5d`: medio, `under_budget`.

- 2026-09-28: **#29 cerrada — una sola rutina de fondo para `escuchar` y `servir`.**
  Ruta: mapeo delegado (sólo lectura) y un escritor; dos pasadas. Módulo nuevo
  `src/prisma/ciclo.py` (`reloj.py` sigue sin enviar nada): por espacio, cadencias
  vencidas + escalera + `despachar`; una vez por pasada, `despachar_avisos_admin`.
  `Escucha.tareas_de_fondo` y `servir` (un único job de APScheduler cada 20 s, vía
  `reloj.montar`) usan el mismo código. Las cadencias se releen de `cadence_job` en cada
  pasada y disparan si su cron cayó entre la última corrida (o el arranque del proceso)
  y ahora: un cambio en la base toma efecto sin reiniciar, y al arrancar no se reponen
  disparos viejos. `--sin-cadencias` en `escuchar` y `servir` (parámetro, no variable de
  entorno, por la política de `config.py`). La escalera corre para todo espacio activo,
  no sólo para los que tienen cadencias. Bug encontrado: `CronTrigger.from_crontab` de
  APScheduler 3.11.3 numera los días con lunes=0, así que `'15 9 * * 1'` (lunes en cron
  estándar, lo que escribe `importador._a_cron`) disparaba el martes (verificado por el
  orquestador: próximo disparo desde el 28/9 = martes 29/9); `_dia_semana_apscheduler`
  convierte rangos, listas, pasos, domingo 0/7 y deja pasar nombres.
  Segunda pasada, por revisión del orquestador: una cadencia mal escrita o que falla al
  ejecutarse no frena la escalera ni el despacho de su equipo (savepoint por cadencia:
  sin él, `InFailedSqlTransaction`, ROJO observado por el orquestador); una falla que
  persiste se reporta una sola vez hasta que se recupera (`SupresorDeRepetidos`), no
  cada 20 s; `escuchar` sobrevive a una pasada que falla; `servir` reutiliza un
  transporte por espacio y cierra el anterior si cambia el token. Pruebas nuevas en
  `tests/test_ciclo.py` y `tests/test_cli.py` (las primeras de `cli.py`), incluida una de
  concurrencia (`for update skip locked`: `servir` y `escuchar` a la vez no duplican
  envíos). Suite completa del escritor: `1099 passed, 108 deselected`; con la prueba
  del savepoint por cadencia, orquestador: `1100 passed, 108 deselected`. Juicio del
  escritor, aceptado: si las cadencias se reactivan tras un tiempo apagadas, la pasada
  siguiente puede encolar la de la semana en curso (la deduplicación semanal evita el
  doble envío).
  Decisión del usuario: orden del resto de la sesión confirmado (ver `docs/STATUS.md`).
  Revisión de `94a323d..10950c6`: alto (`high_risk`, 1807 líneas); consentimiento del
  usuario: revisar. review-6d62b73c11f777b8 (4 lentes) aprobada y reconocida; frontera
  en `10950c6`. Hallazgos no bloqueantes -> #29b (R1-001, texto crudo del error en
  `incident.referencia_cruda`, va con la tarea del token en los errores de Telegram).

- 2026-09-28: **#29b cerrada — seguimientos de review-6d62b73c.** Ruta: delegada, un
  escritor; ROJO observado por ítem (15 fallas antes de implementar). Envío y marca de
  `enviado` de cada mensaje en un savepoint propio dentro de `despachar`: una falla
  posterior ya no devuelve a 'listo' lo que salió (queda la ventana inevitable entre
  enviar y confirmar: entrega al menos una vez). `Ciclo` reutiliza una conexión y
  reconecta si se cae; una base inalcanzable se avisa una vez, sin traza cada 20 s.
  `cadencias_vencidas` busca desde el mayor entre la última corrida y el arranque (no
  repone un lunes perdido tras reiniciar). Días: `1-7`, `5-7`, `0-7` bien; valores fuera
  de 0-7 se rechazan como cadencia rota. Causa distinta en el incidente para cron
  inválido y para falla al ejecutarse. Un solo `reportar_cadencias_rotas` para
  `escuchar` y `servir`, que imprime sólo cuando reporta. El supresor marca un fallo
  como reportado sólo después de escribir el incidente. Probado sin cambios de código:
  dos conexiones evaluando la misma cadencia a la vez no la encolan dos veces
  (`dedupe_key` único). Suite completa del escritor: `1113 passed, 108 deselected`.
  Revisión de `a46d92c..c4e877e`: medio (`slice_budget_reached`, 714 líneas);
  consentimiento del usuario: revisar. review-f51cb1e4b748702a (confiabilidad) aprobada y
  reconocida; frontera en `c4e877e`. Hallazgos no bloqueantes -> #29c.

- 2026-09-28: **#29c cerrada — seguimientos de review-f51cb1e4.** Ruta: delegada, un
  escritor. `despachar` marca `enviado` antes de enviar, dentro del savepoint: si el
  envío falla, se deshace la marca; si falla guardar el `telegram_message_id` (su propio
  savepoint), la marca queda y el mensaje no se reenvía. `Ciclo` cierra la conexión que
  descarta. La prueba de dos conexiones espera el bloqueo real en `pg_stat_activity` en
  vez de dormir 200 ms; pruebas nuevas de reconexión. ROJO observado (3 pruebas) antes de
  la corrección. Suite completa del escritor: `1118 passed, 108 deselected`.
  Decisión del usuario: íconos de los botones aprobados (📋 tarea, ➕ Ver más, 💬 Quiero
  consultar otra cosa, ✅ Confirmar, ✖️ Cancelar, ✏️ Otra opción) y el saludo diario va
  con la unidad del pack 06 (ya registrado en STATUS, ADR 0010 y
  `odd/tasks/alta-y-google.md`).
  Evaluación de `55e3512` contra la frontera `c4e877e`: medio, `under_budget` (353).

- 2026-09-28: **Token del bot fuera de los errores de Telegram (tarea de seguridad).**
  Ruta: delegada, el mismo escritor de #29c. El mensaje de `httpx.HTTPStatusError`
  incluye la URL, que lleva el token, y se guardaba en `message_outbox.ultimo_error`
  (desde antes de hoy), `admin_notice.ultimo_error` e `incident.referencia_cruda`
  (hallazgo R1-001 de review-6d62b73c). Corregido en el origen: `pedido_telegram`
  convierte cualquier falla de una llamada a Telegram en `ErrorTelegram` (tipo, código
  HTTP y `description`, `from None`), en los 12 llamados de `src/prisma/`
  (despachador, local, gateway, cli). Defensa en profundidad:
  `incidentes.redactar_secreto_telegram` tapa `api.telegram.org/bot...` y
  `bot<dígitos>:<token>` en `referencia_cruda` y `ultimo_error`. ROJO de las 18 pruebas
  nuevas con los archivos de `HEAD`, VERDE con el cambio. Suite completa del escritor:
  `1136 passed, 108 deselected`. Las bases locales `prisma` y `postgres` no tenían filas
  con el token (consulta de conteo del orquestador).
  Revisión de `c4e877e..5a6c82a` (#29c y el token): alto (`high_risk`, 967 líneas);
  consentimiento del usuario: revisar. review-709174f82057e0c2 (4 lentes) aprobada y
  reconocida; frontera en `5a6c82a`. Seguimientos aplicados inline por el orquestador:
  R3-001/R4-001, la conexión rota se cierra y descarta en un `finally` aunque falle el
  reporte (ROJO `0 == 1`, VERDE); R2-001, el docstring de `_intentar_envio` dice que la
  falla al guardar el id sólo se imprime. Sin cambios: R3-002 (nadie en `src/` atrapa
  excepciones de `httpx` por tipo) y R2-002 (alias `_error_sin_url`, cosmético).
  `tests/test_ciclo.py tests/test_avisos_admin.py` -> `100 passed`; la suite completa
  queda para después de #7, que corre en paralelo.

- 2026-09-28: **#7 cerrada — íconos en los botones y saludo diario (pack 06).** Ruta:
  mapeo delegado (sólo lectura) y un escritor. Íconos aprobados por el usuario en
  `salida.py` (fuente única: `con_icono`, `costo_icono` en unidades UTF-16,
  `etiquetas_coinciden`): el ícono entra en el mismo límite de la etiqueta, la
  desambiguación trabaja sobre el texto y un toque se resuelve con o sin ícono.
  Saludo diario (`saludo.py`, migración `0018_saludo_diario`, tabla `greeting_state`
  con `workspace_id` y RLS forzada): "👋 Buen día" 05-11:59, "👋 Buenas tardes"
  12-19:59, "👋 Buenas noches" 20-04:59 en la zona del espacio; una reserva atómica por
  persona y fecha local (`insert ... on conflict ... where ... > ...`), dentro de la
  misma transacción que la respuesta. La bienvenida del alta reclama el saludo del día.
  Juicio del escritor, pendiente de confirmar por el usuario: no saludan las cadencias,
  la escalera ni los avisos que dispara otra persona (pedido de aprobación, entrega al
  aprobador, presentación al grupo). `tests/conftest.py` reserva el saludo de todos los
  sembrados para que las pruebas ajenas no saluden. Un solo commit: íconos y saludo
  comparten hunks en `agente.py`, `gateway.py` e `ingreso_tareas.py`. Suite completa del
  escritor: `1164 passed, 108 deselected`.
  Decisión del usuario: la tercera ronda se adelanta y va después de #7 y #9; el
  validador, el banco y T7d quedan para después.
  Revisión de `5a6c82a..e83a280`: alto (`high_risk`, 1575 líneas); consentimiento del
  usuario: revisar. review-8d6f0278927a99b8 (4 lentes) aprobada y reconocida; frontera
  en `e83a280`. Hallazgos no bloqueantes -> #7b.

- 2026-09-28: **#7b cerrada — el saludo se decide al despachar.** Decisión del usuario:
  el primer mensaje del día a cada persona lleva el saludo, sea respuesta, cadencia,
  recordatorio o aviso que dispara otro, y no se repite ese día aunque la persona
  conteste. Por eso el saludo pasó de los enganches al armar la respuesta (agente,
  gateway, ingreso) a un único punto en `despachador._intentar_envio`: se reclama con la
  fecha local del envío real, dentro del mismo savepoint que marca y envía (un envío
  fallido deshace el reclamo; un mensaje postergado o descartado no lo gasta). Un
  mensaje al grupo no saluda ni gasta el saludo de nadie (criterio del orquestador, a
  confirmar). La bienvenida del alta se marca con `message_outbox.es_bienvenida`
  (migración `0019`) y reclama el día sin prefijo. `enqueue_outbox` reserva
  `MARGEN_SALUDO` en los mensajes personales para no pasar el límite de Telegram. Si el
  saludo falla (sin tabla, zona inválida), el mensaje sale sin saludo y se reporta una
  vez. Resueltos también: el saludo ya no queda guardado en la pregunta (R3-001/R3-002);
  `salida.etiquetas_de_tarea` es la única receta de botones de tarea con ícono (R2-002),
  incluido el alta, que pasaba el límite (R3-003, ROJO `PayloadValidationError` con 82
  unidades, VERDE); docstring de `con_icono`; prueba de la activación con token;
  `SALUDO_NOCHE`. Suite completa del escritor: `1178 passed, 108 deselected`.
  Revisión de `eb16f87`: alto (`high_risk`, 1353 líneas); consentimiento del usuario:
  revisar. review-2b75c37b8ba42aaa (4 lentes) aprobada y reconocida; frontera en
  `eb16f87`. Hallazgos no bloqueantes -> #7c.

- 2026-09-28: **#7c cerrada — seguimientos de review-2b75c37b.** Ruta: el mismo
  escritor. `escuchar` y `servir` se niegan a arrancar si falta una migración que el
  código necesita, y nombran el archivo (sin ella, toda la mensajería fallaba). Un
  mensaje donde el saludo no entra en el límite de Telegram sale sin saludo y no gasta el
  del día; `cabe_en_mensaje` es la única medida de si un texto entra con botones. La
  falla del saludo se reporta después de resolver el envío, así no se pierde si el envío
  falla, y una sola vez. Pruebas sin dependencia del orden ni de la medianoche. ROJO
  observado (prueba de arranque, fila sin margen, reporte perdido). Suite completa del
  escritor: `1185 passed, 108 deselected`.
  Revisión de `d1e3e1e`: alto (`high_risk`, 583 líneas); consentimiento del usuario:
  revisar. review-2b89536f9f52c5de (4 lentes) aprobada y reconocida; frontera en
  `d1e3e1e`. Aplicado inline por el orquestador: R4-001/R3-001, el reporte de la falla
  del saludo corre en su propio savepoint después del envío y una falla suya ya no deshace
  la marca de un mensaje entregado (ROJO: la excepción escapaba del despacho; VERDE).
  Quedan para después de la ronda (menores): R2-001 segunda medida de "entra en el
  mensaje" dentro de `saludo._reclamar_protegido`, R3-002 la prueba cuenta todos los
  incidentes del espacio, R2-002/R2-004/R2-005/R3-003/R3-004 docstrings y pruebas.

- 2026-09-28: **#9 cerrada — respuesta inmediata e indicador de actividad (pack 05,
  ADR 0011).** Ruta: mapeo delegado y un escritor. La respuesta se despacha apenas
  termina `procesar_update` (en `Escucha.recibir`, update por update, y en la ruta del
  webhook de `servir`), en vez de esperar el fin del lote o la pasada de 20 s.
  `mantener_chat_activo` arranca "escribiendo…" y el borrador nativo sólo si el turno
  pasa de 1,5 s (inyectable), con `draft_id` aleatorio por turno, y los retira al
  terminar (mensaje transitorio silencioso + `deleteMessage`). Por revisión del
  orquestador, sus fallas ya no son silenciosas: una línea por tipo y por turno, y un
  retiro fallido deja un incidente deduplicado. Hallazgo aparte: `_activacion` no hace
  commit explícito en /start sin token (tarea nueva). ROJO/VERDE observados. Suite
  completa del escritor: `1199 passed, 108 deselected`. Pendiente: verificación visual
  en Telegram real, en la ronda.
  Base `prisma`: respaldo `db/respaldos/prisma-antes-0018-0019-20260928.dump` y
  migraciones `0018` y `0019` aplicadas; `saludo.verificar_migraciones` -> `None`.
  Revisión de `d1e3e1e..e2a094e`: medio (`slice_budget_reached`, 1025 líneas);
  consentimiento del usuario: revisar. review-2758883d40d83428 (confiabilidad)
  aprobada y reconocida; frontera en `e2a094e`. Hallazgos no bloqueantes -> #9b.

- 2026-09-28: **#9b cerrada — seguimientos de review-2758883d.** Ruta: el mismo
  escritor. El retiro del borrador espera a que termine el envío del borrador (acotado a
  5 s) o lo abandona reportándolo: ya no puede llegar antes y dejarlo visible. Costo
  aceptado y registrado en ADR 0011: si Telegram tarda en recibir el borrador, el turno
  puede demorar hasta 5 s más en ese caso. El incidente de un retiro fallido va en su
  propio savepoint. En `servir`, el despacho inmediato corre como tarea de fondo con su
  propia conexión, después del ACK del webhook. Pruebas del indicador con eventos en vez
  de esperas fijas. ROJO/VERDE observados. Suite completa del escritor: `1202 passed,
  108 deselected`.
  Revisión de `04878c8`: medio (`slice_budget_reached`, 521 líneas); consentimiento del
  usuario: revisar. review-587f6330bf9c64b9 (confiabilidad) aprobada y reconocida;
  frontera en `04878c8`. Hallazgos no bloqueantes, para después de la ronda (afectan a
  `servir`, no a `escuchar`): R3-001 la espera del retiro (hasta 5 s) corre dentro del
  turno y en `servir` bloquea el bucle de eventos; R3-004 despacho concurrente en tareas
  de fondo (confirmar que `for update skip locked` lo cubre, ya probado en #29); R3-002
  falta la prueba del borrador abandonado; R3-003 una prueba con espera fija de 30 ms.

- 2026-09-28: **Cierre de sesión.** Punto exacto para retomar y guion de la tercera ronda
  en `docs/STATUS.md`. La ronda va en horario laboral (09:00-17:00), porque fuera de
  horario los avisos que no son respuesta se postergan.

- 2026-09-28 (noche): **Tercera ronda por Telegram — cortada por el usuario, con
  hallazgos.** Base local `prisma`, `escuchar corework --sin-cadencias`, 21:00-21:46
  (fuera del horario laboral 09:00-17:00: los avisos que no son respuesta quedaron
  postergados). Participaron Ariel e Ismael; el circuito B no se llegó a correr.
  Evaluación del usuario: "tarda mucho en responder, se pierde en la conversación, no es
  para nada fluido".

  **Funcionó:** vinculación del bot de administración (`mensaje_admin` con chat_id) y el
  aviso de un incidente llegó al administrador por ese bot; saludo "👋 Buenas noches" una
  sola vez por persona; animación de "escribiendo…" en turnos de texto; íconos; menú con
  responsable y estado; "💬 Quiero consultar otra cosa" cierra bien; el hallazgo 10 de
  la sesión 2 se sostiene; entrega con evidencia de texto -> vista previa -> `en_revision`;
  el aviso al aprobador se postergó a las 09:00 del día hábil; Ismael encontró la entrega
  preguntando; "Pedir cambios" devolvió la tarea a `en_curso`.

  **Medición (auditoría y cola):** respuesta cuando decide el código (menús, botones,
  vistas previas): 0 s; cuando interviene el modelo (`nan` / `deepseek-v4-flash`):
  9,8 / 10,5 / 11,7 / 15,9 / 17,4 / 9,6 s; la foto: nunca.

  **Hallazgos (R3-H):**
  - H1. El aviso de incidente al administrador necesita explicación humana. Formato
    aprobado por el usuario: "⚠️ Prisma no pudo responderle a X" / Qué pasó / Qué vio X /
    Qué hacer / Mensaje / Detalle técnico (hora local del espacio, no UTC). Qué pasó y
    Qué hacer salen de una tabla determinista de causas conocidas, no del modelo.
  - H2. El mensaje neutro a la persona es poco claro. Texto nuevo aprobado: "Tuve un
    problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un
    administrador." (`gateway.NOTICIA_NEUTRA_INCIDENTE`).
  - H3. Lista ambigua: "una todavía asignada y la otra ya en curso" sin decir cuál.
  - H4. El ícono acorta las etiquetas ("Dashboard de lotes en CoreLabs" ->
    "Dashboard de lotes…").
  - H5. El indicador sólo cubre turnos de texto (único punto: `gateway.py:333`); al tocar
    un botón no hay ninguna señal y la persona toca dos veces.
  - H6. Preparación: la base nueva no tenía `model_config` (cada texto terminaba en
    incidente `LookupError`). Resuelto en vivo con `python -m prisma modelo
    deepseek-v4-flash --proveedor nan` (el de la base vieja) y `PRUEBA-LOCAL.md` §5 paso 5b.
  - H7. Regla del usuario: con hasta 3 tareas el texto las nombra enteras; con más,
    resume y los nombres quedan en los botones. Siempre igual (hoy el modelo alterna).
  - H8. Regla del usuario: un "hola" suelto tras cerrar un tema se contesta con saludo y
    pregunta abierta ("Hola, Ariel. ¿En qué te ayudo?"), sin repetir la lista.
  - H9. La confirmación de una entrega debe decir algo como "Gracias. La tarea pasó a
    revisión.", sin nombrar a quien revisa ni horarios (usuario).
  - H10. "Modificar" sin ícono al lado de ✅ Confirmar y ✖️ Cancelar (✏️).
  - H11. La vista previa es un renglón denso separado por puntos; un dato por línea.
  - H12. Información no pedida: "Los objetivos están todos activos, ninguno esperando
    cierre" en la respuesta sobre qué aprobar.
  - H13. Un segundo toque sobre un botón recién usado muestra "Ese pedido ya no está
    vigente…"; para la misma persona y un toque reciente, absorberlo en silencio.
  - H14. Redacción: "vuelve a en curso"; el "Hecho." repite la vista previa entera.
  - H15. **Crítico.** Un mensaje sin texto (foto, archivo, audio) no recibe ninguna
    respuesta ni deja incidente; el pie de foto también se pierde. Fotos y archivos como
    evidencia quedaron fuera de ADR 0009 (unidad de aportes del roadmap), pero nunca en
    silencio: como mínimo, responder que todavía no se pueden recibir y pedir texto o link.
  - H16. Después de "Pedir cambios", el responsable no ve qué le pidieron: ni la lista ni
    el menú muestran el motivo, y el modelo dijo "figura todavía en curso, no en
    revisión", que confunde.
  - H17. **Crítico.** Con la entrega esperando la evidencia, el "hola" siguiente se tomó
    como evidencia ("Evidencia: hola").
  - H18. El modelo ofreció "Adjunto una captura o archivo", una opción que el sistema no
    puede cumplir.
  - H19. Un mismo mensaje (el link) produjo dos respuestas en paralelo: una aclaración
    ("¿A cuál te referís con «subir las capturas»?") y la vista previa.
  - H20. **Crítico.** La nueva entrega después de "Pedir cambios" terminó como "Nueva
    evidencia" y la tarea quedó `en_curso` (dos evidencias: el texto de 21:25 y el link de
    21:45 como tipo `capturas`): el aprobador no tiene nada para aprobar; el circuito se
    corta.
  - H21. **Crítico.** Latencia de 10-17 s en cada turno con modelo.

  **Causas de fondo:** (1) latencia del modelo; (2) manejo del estado de la conversación
  (un slot pendiente se traga cualquier texto, caminos paralelos para un mismo mensaje,
  la nueva entrega no vuelve a revisión, opciones que no se pueden cumplir, mensajes sin
  texto ignorados); (3) ninguna señal al tocar botones.

  **Decisiones del usuario para retomar:** cambiar el modelo a uno rápido por OpenRouter
  (ya hay clave, `PRISMA_OPENROUTER_API_KEY`; el usuario propone Gemini 3.8 o GPT Luna
  6: verificar los identificadores reales con `python -m prisma modelos --proveedor
  openrouter`, medir y elegir); leer como insumo el manual de personalidad, voz y
  comportamiento del trabajo anterior del usuario con otra IA
  (`D:\Proyectos\PRISMA-PACK-VERACIDAD-Y-AMBIGUEDAD-20260923\PRISMA-MANUAL-PERSONALIDAD-VOZ-Y-COMPORTAMIENTO-20260928.md`),
  medido contra el corpus del repo como pide `AGENTS.md`.

  **Operación:** listener detenido. Los dos avisos postergados a las 09:00 ("Ariel
  entregó…", "Ismael pidió cambios…") quedaron `descartado` (ya no reflejaban el estado;
  cambio reversible sobre datos ficticios). "Dashboard de lotes en CoreLabs" queda
  `en_curso` con dos evidencias. Consola de la ronda en el scratchpad de la sesión (no
  versionada).

- 2026-09-28 (noche, después de la ronda 3): **Manual de personalidad leído y T8a.**
  El manual del usuario se contrastó con `nucleo/`, ADR 0007/0008/0009/0011, el
  `PREAMBULO` y R3-H1..H21. Da criterio, no mecanismo, para los críticos de estado de la
  conversación (H15, H17, H19, H20, H13, H5, H16). Sus preguntas de cierre en texto
  abierto contradicen ADR 0007 (prevalece el repo). Probable causa de H18:
  `contexto.PREAMBULO` obliga a llamar a `ofrecer_opciones` "con las opciones más
  razonables que se te ocurran" aunque no haya opciones reales (manual §13: sólo
  opciones reales). Fuera de alcance: ejemplos de agenda, audio, §28 aprendizaje
  persistente.
  T8a: `Config.clave_llm`/`variable_clave_llm`; `llm.desde_base(cur, ws, claves)`
  resuelve la clave del proveedor configurado y, si falta, `LookupError` con el nombre
  de la variable (incidente por los tres caminos: `gateway.py:347`, `:261`, `:1256`);
  `gateway` pasa `config`; `modelos`/`modelo` y el banco usan la clave del proveedor.
  TDD: RED `pytest -q tests/test_clave_proveedor.py` -> 6 failed; GREEN enfocadas
  (`tests/test_clave_proveedor.py tests/banco/test_conftest.py tests/test_llm_protocol.py`)
  -> 112 passed (escritor y repetida por el orquestador); suite completa `pytest -q`
  -> 1208 passed, 108 deselected. Pendiente: `.env.ejemplo` no se pudo revisar (el
  sistema de permisos niega su lectura); el usuario confirma si su comentario dice que
  `PRISMA_OPENROUTER_API_KEY` es sólo para Jev.
  Candidatos en OpenRouter verificados en el catálogo público:
  `google/gemini-3.8-flash` y `openai/gpt-6-luna` (ambos con herramientas).
  PostgreSQL local estaba colgado desde las 22:02 (autovacuum terminó con 0xC0000142 y
  el postmaster no pudo reiniciar hijos); se cerró el proceso y la recuperación desde WAL
  terminó limpia.
  Commit `beda9a5`. RDD: riesgo alto (`cli.py`, frontera de proceso), consentimiento del
  usuario, `review-291d29d62a75ce69` con cuatro lentes, aprobada y reconocida (autoridad
  consumida); frontera de revisión en `beda9a5`. Siete sugerencias no bloqueantes, para
  después: el mapeo proveedor -> clave está escrito dos veces en `config.py` (una tabla
  única); `desde_base` sin tipo en `claves`; comentar por qué las pruebas comparan con
  `is True` (no imprimir claves); ninguna prueba recorre los tres caminos de `gateway`
  con la clave faltante; faltan casos `gemini`/`anthropic` en `desde_base`; con un
  proveedor desconocido y sin clave, el error nombra la clave en vez del proveedor
  (verificar la dirección antes que la clave); la clave faltante ahora corta el turno al
  construir el proveedor (antes fallaba en la llamada), con el mismo incidente.

- 2026-09-28 (noche): **T8b — medición de modelos con el banco real.** Una corrida por
  escenario (36), latencia de cada llamada volcada por un complemento de pytest del
  scratchpad (no versionado) desde la grabación del banco (`rutas`/`respuestas`).
  `nan/deepseek-v4-flash`: 33/36 aprobados (fallan b-0001-a, b-0001-b, b-0013); ruteo
  mediana 2,8 s (p90 4,7); respuesta 3,1 s (p90 5,4); modelo por turno 10,0 s (p90
  17,4). `openrouter google/gemini-3.8-flash`: 29/36 (suma fallas en b-0001, b-0005-b,
  b-0011, b-0016); ruteo 3,8 s; respuesta 3,3 s; por turno 14,2 s. `openrouter
  openai/gpt-6-luna`: 7/36, 25 bloqueados por `RoutingError` y 3 por `RateLimitError`;
  causa verificada con una sonda directa: en una conversación normal manda el objeto
  `task` con todos los campos vacíos y la validación del ruteo lo rechaza ("Normal
  conversation cannot contain task proposals."); donde anduvo, ruteo 1,9 s y respuesta
  2,9 s. Cada turno hace una llamada de ruteo tipado y una mediana de dos del ciclo de
  herramientas (hasta cuatro), en serie; el modelo conversacional es el 96 % del tiempo
  del escenario. Con 2-3 s por llamada ningún modelo llega a menos de 4 s por turno.
  Decisión del usuario: se mantiene deepseek y se diseña cómo bajar las llamadas (T8c).

- 2026-09-28 (noche): **T8c-1 — el ciclo del responder corta cuando la vuelta deja algo
  pendiente.** `agente.responder` cuenta confirmaciones, `NecesitaElegir` y
  `ofrecer_opciones` antes y después de cada vuelta; si crecieron, termina sin otra
  llamada al modelo. Un rechazo sigue volviendo al modelo. TDD: RED
  `pytest -q tests/test_agente.py -k "cierra_el_turno or vuelve_al_modelo or sigue_llamando"`
  -> 3 failed (`assert 2 == 1` llamadas), 2 passed (rechazo y consulta, sin cambio);
  GREEN enfocadas `tests/test_agente.py tests/test_opciones_modelo.py
  tests/banco/test_replays.py tests/banco/test_corrida.py` -> 114 passed (repetida por el
  orquestador); suite completa -> 1213 passed, 108 deselected. Ajustes: una prueba de
  `test_opciones_modelo.py` leía los resultados de la segunda llamada, ahora los captura
  envolviendo `_ejecutar_una`; `tests/banco/test_corrida.py` tenía una respuesta de
  cierre guionada que ya no se pide. Quedan dos pruebas con una respuesta final guionada
  que no se usa (pasan igual).
  Latencia (T8c-2 descartada): NaN `deepseek-v4-flash` es la versión 4.1 (panel del
  usuario; mismos conteos de tokens que `deepseek/deepseek-v4.1-flash` de OpenRouter).
  Llamada simple ~1 s en NaN, ~2,5 s por OpenRouter 4.1.
  Commit `6c3c936`; RDD: riesgo medio, bajo presupuesto (177 líneas), queda pendiente en
  la rebanada desde `154101a`. Banco real después de T8c-1 (deepseek por NaN, n=1): 33/36
  aprobados; en los 27 turnos que pasan por el responder, llamadas por turno de 4 a 3
  (mediana) y tiempo del modelo por turno de 10,7 s a 7,9 s (-26 %). Falla nueva b-0016
  (contenido): el modelo nombró las dos tareas en el texto; camino `consultar_tareas` ->
  texto, que T8c-1 no toca, así que es variación del modelo. Además el escenario
  contradice R3-H7 (con hasta 3 tareas el texto las nombra enteras): actualizarlo en T10.

- 2026-09-28 (noche): **T8c-3 — ruteo en paralelo con la primera llamada del responder**
  ([`ADR 0012`](../../docs/decisions/0012-ruteo-en-paralelo-con-la-primera-respuesta.md)).
  `agente.preparar` hace las lecturas de la base en el hilo principal; `Especulacion`
  lanza la primera llamada en un `ThreadPoolExecutor` de 4 hilos (sólo HTTP) mientras
  corre el ruteo; `_avanzar_aclaracion` la usa sólo en el caso simple (conversación
  normal, sin referencias, sin corrección abierta) y `_turno` la descarta en cualquier
  otro camino. Opt-in por proveedor (`admite_especulacion`); el guionado no especula; el
  grabador del banco retira las respuestas descartadas. TDD: RED
  `pytest -q tests/test_especulacion.py` sin el código -> 12 failed, 2 passed; GREEN
  enfocadas -> 144 passed; suite completa (corrida por el orquestador) -> 1227 passed,
  108 deselected. Ajuste: el simulacro de Anthropic de `tests/test_task_intake.py`
  reconoce el ruteo por `tool_choice` y admite una llamada especulativa extra.
  Seguimiento menor: `ProveedorGrabador.descartar_respuesta` quita la entrada con
  `list.remove` (igualdad, no identidad).

- 2026-09-29: **T8c-3 revertida (decisión del usuario) y T8c-4 abierta.** RDD de la
  rebanada `154101a..46278f3` (riesgo alto, cuatro lentes, `review-31b767dbe1a4c1f6`):
  aprobada y reconocida, frontera en `46278f3`, con avisos sobre el pool compartido de la
  especulación, una carrera en el grabador del banco y una prueba frágil. Banco: la
  especulación sólo aplica en 10 de 36 escenarios (conversación normal sin referencias; la
  mayoría nombra una tarea y pasa por Jev). A/B con el mismo código, 10 escenarios x 3:
  pared mediana 9,9 s apagada y 9,4 s encendida (-1,1 s mediano por escenario). NaN
  cuelga pedidos ~93-95 s: 5 de 385 llamadas en serie, 7 de 180 con especulación. Se
  revierte el código de `46278f3` (archivos idénticos a `16ec246`); ADR 0012 queda como
  revertida con la evidencia. En su lugar, T8c-4.

- 2026-09-29: **T8c-4 — tiempo máximo por llamada al modelo.** `llm.TIMEOUT_MODELO_S = 20`
  y `REINTENTOS_MODELO = 2`, ajustables con `timeout_s`/`reintentos` en
  `model_config.parametros`; `ProveedorCompatible` y `ProveedorAnthropic` los pasan al SDK
  (verificado en el código instalado de openai 3.17.0: un timeout con reintentos
  disponibles se reintenta); `ProveedorGemini` usa el timeout en su `httpx.Client` y
  reintenta sólo ante timeout. Un timeout agotado sigue el camino de siempre (incidente y
  disculpa; en el ruteo, sus dos intentos y el incidente de ruteo). Peor caso: una llamada
  ~61 s (3 x 20 s), ruteo totalmente caído ~123 s (sus dos intentos multiplican los del
  SDK); un cuelgue típico (~1,3 %) pasa de ~93 s a ~20 s más el reintento. TDD: RED
  `pytest -q tests/test_tiempo_maximo_modelo.py` -> 8 failed, 3 passed (el SDK ya
  reintentaba timeouts; faltaban los límites); GREEN enfocadas -> 121 passed (repetida por
  el orquestador); suite completa -> 1224 passed, 108 deselected. `PRUEBA-LOCAL.md`
  documenta los parámetros. Sin medición con el banco: los cuelgues son ~1,3 % y una
  corrida de ~100 llamadas no los reproduce de forma confiable. Revisión de la reversión
  (`review-c6ae4f044c96005a`, cuatro lentes) aprobada y reconocida; frontera en `ccf5c73`.
  T8 queda cerrada: turno de ~12,6 s a ~9,4 s de mediana en el banco (T8c-1) y sin cuelgues
  de más de ~20 s por intento (T8c-4). Próximo: T9.

- 2026-09-29: **T9 replanteada por reglas generales.** Mapeo de causas por lectura de
  código (explorador de sólo lectura): H17 verificado (`_resumir_dato_menu_tarea` acepta
  cualquier texto no vacío; la marca `modificar_pedido_en` se consume en
  `reclamar_modificacion_abierta` antes de interpretar); H20 mecanismo verificado y
  disparo inferido (`adjuntar_evidencia` sobre `en_curso` sólo inserta la evidencia);
  H16 verificado; H15 verificado (sólo se lee `text`); H19 sin causa confirmada; H18
  inferido (regla del `PREAMBULO`); H5 y H13 verificados. El usuario objetó arreglar
  casos puntuales ("podrías estar así hasta el infinito"): se adoptan cuatro reglas
  generales ([`ADR 0013`](../../docs/decisions/0013-reglas-generales-de-la-conversacion.md)),
  con el costo aceptado de ~2 s de ruteo en las respuestas a un dato pedido. Se descarta
  la lista de saludos como mecanismo.

- 2026-09-29: **T9-R1a-1 — la pregunta pendiente del menú se interpreta (ADR 0013 regla 1).**
  `route_intent(texto, pendiente=...)` en todos los proveedores: con pregunta pendiente el
  prompt del ruteo (`ROUTER_SYSTEM_PENDIENTE`) la incluye y el esquema exige
  `respecto_pendiente` de la lista cerrada (responde, corrige, cancela, otro_tema, charla,
  dudoso, no_puedo); la validación tipada lo exige sólo con pregunta pendiente.
  `pendientes.ver_modificacion_abierta` (sin consumir) y `consumir_modificacion` (un solo
  uso, `update ... where modificacion_consumida_en is null`). `gateway._atender_dato_pendiente`
  con un manejo por comando; la pregunta sólo se consume con responde o cancela; si el
  ruteo falla queda abierta. Modificar y "Ninguna, lo escribo" siguen igual (R1b). Suite
  antes de esta unidad: 1235 passed (validación de parámetros, `ee5b848`). TDD: RED por
  importación faltante y, con el comportamiento viejo restituido a mano, 13 de 14 pruebas
  de `tests/test_pregunta_pendiente.py` fallaron; GREEN enfocadas 275 passed (repetidas por
  el orquestador: 165 passed); suite completa 1309 passed, 108 deselected. El prompt del
  ruteo con pregunta pendiente todavía no se midió con el modelo real (R1a-2).

- 2026-09-29: **Orden de trabajo (decisión del usuario).** Primero comportamiento: T9
  (R1a-2, R1b, R1c, R2, R3, R4, H19) y T10; después T11 (cuarta ronda por Telegram). Las
  mejoras y optimizaciones (T8d y el resto) quedan para después de T11.

- 2026-09-29: **T9-R1a-2 y cierre de T9-R1a.** Commit `6164554`: `dudoso` y `corrige` con
  botones ("✅ Sí, es eso" / "✏️ No, es otra cosa", `SENTINEL_RESPUESTA_DATO_MENU`, un solo
  uso); después de `otro_tema`, el retome "¿Seguimos con …?" con "✖️ Dejarlo" como otra parte
  de la misma respuesta, sólo si el turno no dejó otra interacción pendiente (cuenta de filas
  de `message_outbox` con botones y altas activas, antes y después); `cancela` ya no dice
  "dejé de lado" si otro turno consumió la pregunta; `reintentos` acepta `2.0`. Banco: campo
  `mensajes_tras_toques` y familia `b-0019` (saludo, charla, agradecimiento, otro pedido,
  link, cancelación, ambiguo). Suite completa del escritor: 1344 passed, 129 deselected.
  RDD `review-dd7cd3c9cb7e8575` (medio, una lente) aprobada y reconocida; frontera en
  `6164554`. Banco real con deepseek (n=3): 18/21; las 3 fallas fueron el link como
  evidencia, clasificado `dudoso` (seguro, pero con un toque de más) porque el ruteo sólo
  veía la descripción y no la pregunta hecha. Arreglo general (`44a5bbc`): el ruteo recibe
  la descripción más la pregunta literal (`_pendiente_para_ruteo`); TDD con una prueba nueva
  (RED y GREEN, 124 passed en el grupo). Banco real otra vez: **21/21**; ruteo con pregunta
  pendiente 1,1-2,5 s. Pendiente para R2: el retome es otra fila de la cola sin vínculo
  explícito con el mensaje entrante; R2 debe contarla como parte de la misma respuesta.

- 2026-09-29: **T9-R1b.** Commit `5371921`: un solo manejo genérico de preguntas pendientes
  (`_atender_pregunta_pendiente` con el adaptador `_pregunta_de`) para el dato del menú,
  Modificar y "Ninguna, lo escribo"; ids de mensaje únicos en el banco; familia `b-0020`.
  Suite del escritor 1376 passed, 147 deselected; enfocadas repetidas 211 passed. RDD
  `review-e95b2d47b01f0161` (medio) aprobada y reconocida; frontera en `5371921`. Banco real
  (n=3): 12/18. El ruteo acertó siempre (`corrige`, `otro_tema`); las fallas son después: (1)
  la corrección "se rompió el variador" sacó "el variador roto" como referencia a tarea, Jev
  no la resolvió y Prisma preguntó "¿A cuál te referís?" en vez de corregir (mismo mecanismo
  probable de H19); (2) con `otro_tema`, el modelo volvió a proponer el bloqueo por su cuenta
  (el banco confirma al final y quedó el efecto). Precisión del ADR 0013 regla 1 y T9-R1b-2.

- 2026-09-29: **T9-R1b-2 y T9-R1b-3.** `1950278`: al contestar una pregunta pendiente
  (`responde`, `corrige`, "Sí, es eso"), la tarea de la pregunta es el sujeto por defecto;
  Jev se sigue consultando y sólo una resolución CLARA cambia el sujeto; una referencia
  ambigua o sin resolver no abre "¿A cuál te referís?" (`_resolver_referencias_del_turno(
  ..., solo_claras=...)`; si falta la credencial de Jev igual se registra el incidente y todo
  queda en la auditoría). Con `otro_tema`, el responder recibe el bloque de confianza "#
  Pregunta pendiente". Precisión escrita en ADR 0013 regla 1. Suite 1389 passed. Banco real
  `b-0020` (n=3): 15/18 (la corrección real pasó de 0/3 a 3/3); "otro tema" seguía
  volviendo a proponer el bloqueo pese a la instrucción (0/3). `3bcaa99` (R1b-3): guarda
  determinista en el ciclo del responder (`agente.NoProponer`, `repite_lo_pendiente`): en un
  turno de `otro_tema` (y "No, es otra cosa") se rechaza, antes de ejecutarla, la misma
  herramienta sobre la misma tarea que la pregunta pendiente (Modificar: la herramienta de
  la propuesta; dato del menú: `_HERRAMIENTA_DE_DATO_MENU`; "Ninguna" sin guarda), con un
  resultado de rechazo al modelo y registro en la auditoría. Suite 1396 passed, 147
  deselected. Banco real `b-0020`: **17/18**; la única falla (b-0020-c-2) es de redacción: la
  respuesta resumió la lista sin nombrar "Cablear tablero" (regla de listas R3-H7, T10).
  Notado para después: cuando `otro_tema` lista tareas, sus botones cuentan como interacción
  pendiente y no sale el "¿seguimos?" (la pregunta sigue abierta igual).

- 2026-09-29: **Cierre de sesión — punto exacto para retomar.** Árbol limpio en `main`,
  por delante de `origin/main` (sin push; lo decide el usuario). Hecho: T8 (latencia) y de
  T9 las etapas R1a, R1b, R1b-2 y R1b-3 (regla 1 del ADR 0013 para el dato del menú,
  Modificar y "Ninguna, lo escribo"). **Próximo: T9-R1c** — aplicar el manejo genérico
  (`gateway._atender_pregunta_pendiente` con un adaptador nuevo en `_pregunta_de`) a las
  preguntas del alta guiada (`ingreso_tareas.handle_active_text`, que hoy toma el mensaje
  siguiente como el campo pedido), con su familia de escenarios del banco y los
  seguimientos de la revisión de R1b-2/3 (`review-34b692649e0734e7`, aprobada y reconocida;
  frontera de revisión en `3bcaa99`): probar la guarda para "destrabar" (clave
  `bloqueo_id`) y para Modificar de una herramienta cuyo id no es `tarea_id` (p. ej.
  `resolver_bloqueo`); controlar `resolucion is None` en el filtro `solo_claras`; aserción
  positiva del caso "otra tarea" del dato del menú. Después, en orden: T9-R2 (una respuesta visible
  por mensaje; incluye atar el "¿seguimos?" al mensaje entrante), T9-R3, T9-R4, T9-H19
  (reproducir), T10 (incluye actualizar b-0016 y los fragmentos de redacción que usan
  b-0019/b-0020), T11 (cuarta ronda), y recién después optimizaciones (T8d). Método que
  funcionó: un escritor por unidad con TDD, commit, RDD, y la familia del banco real contra
  `nan/deepseek-v4-flash` (n=3) antes de cerrar cada regla.

- 2026-09-29: **T9-R1c-0 y T9-R1c-1.** `73f54f2` (R1c-0): la guarda de `otro_tema` toma
  el id de cada herramienta (`_CAMPOS_DE_ID`: `tarea_id`, `bloqueo_id`,
  `dependencia_id`; con dos ids o ninguno, sin guarda), y un `(None, None)` de Jev se trata
  como resolución fallida en la auditoría y en `solo_claras`. `24fe1e3` (R1c-1): el campo de
  texto libre del alta ya no se toma en `procesar_update`; `_turno` lo lee con
  `_ver_pregunta_abierta` (sólo en chat privado, el alta primero) y pasa por
  `_atender_pregunta_pendiente` con el adaptador `_SENTINEL_ALTA_TEXTO_LIBRE`; consumir,
  dejar de lado y seguir se generalizaron (`_consumir_pregunta`, `_dejar_de_lado`,
  `_seguir_con_el_campo_del_alta`). `cancela` cancela el borrador (`_cancel` sin encolar;
  "Listo, dejé de lado el borrador de la tarea «título»."); `corrige` va a los botones de
  `dudoso` porque el alta no tiene camino para cambiar un campo ya confirmado desde texto.
  Familia `b-0021` (9 escenarios); el arnés del banco toca los botones del alta y manda
  `type: private`. Ruta: delegada, un escritor (el primero se frenó por accidente después
  del commit de R1c-0; un segundo terminó R1c-1). TDD: RED 18 failed / 2 passed, GREEN 23
  passed. Verificación del padre: enfocadas (alta, intake, guarda, otras) 161 passed. Suite
  del escritor 1427 passed, 1 failed (`test_migration_preflight_fails_before_ddl_for_
  incompatible_unit1a_rows[converted_waiting]`, pasó sola y en la corrida del padre).
  RDD: R1c-0 solo medio bajo el umbral; el tramo `3bcaa99..24fe1e3` alto (1528 líneas),
  consentida por el usuario, revisión `review-06b7019b060dbffb` (4 lentes) **aprobada y
  reconocida**; frontera de revisión en `24fe1e3`. Ocho observaciones no bloqueantes,
  anotadas como seguimientos en T9-R1c-2. Suite completa del padre: 1427 passed, 1 failed
  (la misma prueba de migración) y en una segunda corrida **1428 passed, 174 deselected**:
  es intermitente (2 de 3 corridas completas; sola siempre pasa) y no toca este código
  (arma su base desde `BASELINE_REF` y aplica `0002`); falta capturar su traceback.
  Banco real `b-0021` (n=3, `nan/deepseek-v4-flash`): **24/27**. El ruteo acertó siempre
  (`otro_tema` 3/3 en `b-0021-c`). Las 3 fallas son `b-0021-c`: la consulta "¿qué tareas
  tengo abiertas?" responde con la lista de tareas, que siempre lleva botones
  (`agente._opciones_lista_tareas`), y por la condición de la regla 1 ("si la respuesta no
  dejó otra interacción pendiente") no sale el retome; la pregunta del título sigue
  abierta. Es lo mismo que se notó en `b-0020`. El escenario espera algo que la regla
  excluye: decisión pedida al usuario (retome sin botones cuando la respuesta ya trae los
  suyos, o ajustar el escenario). Además, `b-0021-c-2` resumió sin nombrar la tarea
  (redacción, R3-H7, T10).

- 2026-09-29: **T9-R1c-2.** Ruta: delegada, un escritor. `1eb0323` (seguimientos de
  `review-06b7019b060dbffb`: claves de `FREE_TEXT_NAMES` atadas a `USER_FIELD_LIMITS`,
  comentario de `_CAMPOS_DE_ID`, doble sentido de `pending_action_id` documentado; el
  segundo toque del mismo botón responde "Ese pedido ya no está vigente…" desde `_toque`,
  no `AVISO_DATO_YA_NO_PENDIENTE`, y así quedó afirmado). `331a5f6`: la elección con
  botones del alta (`task_intake_choice_set`) y el borrador esperando confirmación (la
  `pending_action` de la vista previa, con Confirmar y Cancelar, dirigida al aprobador)
  pasan por el manejo genérico (`ingreso_tareas.open_intake_question`, centinelas
  `_SENTINEL_ALTA_ELECCION` y `_SENTINEL_ALTA_CONFIRMACION`, `_pregunta_del_alta`,
  `_repreguntar`). Elección: `responde` resuelve la opción sólo si el texto coincide con
  exactamente una (etiqueta normalizada o nombre completo de la entidad, sin coincidencia
  parcial; el modelo nunca elige); si no, se reenvía la elección con sus botones. El
  ruteo recibe la lista de opciones. Confirmación: ningún mensaje convierte el borrador
  (invariante de conversión explícita); `responde` y `charla` dicen que se confirma con el
  botón; `corrige` dice que el borrador no se cambia desde un mensaje
  (`AVISO_ALTA_NO_SE_CORRIGE`: cancelarlo y armarlo de nuevo); `cancela` lo cancela.
  TDD: RED 18 failed / 11 passed, GREEN 32 passed. Suite del escritor 1466 passed, 198
  deselected. Padre: enfocadas del alta 56 passed. RDD: tramo `24fe1e3..331a5f6` alto
  (1609 líneas), consentida por el usuario, `review-2435c6d8256a609c` (4 lentes)
  **aprobada y reconocida**; frontera en `331a5f6`. Banco real `b-0022` (n=3): **16/24**.
  `b-0022-a` (la opción escrita en minúsculas): `RoutingError` 3/3, defecto real (la
  grabación no guarda la ruta que falló). `b-0022-e`/`-f` (vista previa): 5 corridas
  bloqueadas en la preparación (el modelo no armó el alta completa de un mensaje y los
  toques no encontraron sus botones), no en el comportamiento. Decisiones abiertas del
  escritor: `corrige` sobre la vista previa del alta (hoy "cancelalo y armalo de nuevo";
  la vista previa del alta no tiene Modificar), y quién confirma cuando quien escribe no
  es el aprobador (la respuesta no lo dice; regla 3).
  - [x] **T9-R1c-2b** — `RoutingError` de `b-0022-a`; `b-0022-e`/`-f` con el borrador
    sembrado en la base en vez de recorrer el alta con el modelo; la respuesta dice quién
    confirma cuando no es quien escribe; y seguimientos de `review-2435c6d8256a609c`:
    `_TIPO_DE_ALTA` con las constantes `QUESTION_*`; campo neutro para
    `pending_action_id` (señalado dos veces); consulta del primer cuerpo de una elección
    en un solo helper; referencia determinista para el reenvío sin `entrante_id` y prueba
    del reenvío de una elección ya cerrada; afirmar la respuesta al escribir la opción;
    falla ruidosa si un campo de texto libre no tiene nombre.

- 2026-09-29: **Decisión del usuario — una sola rama de conversación abierta.** A partir
  de `b-0021-c` (la respuesta al otro tema traía sus botones y el retome no salía), el
  usuario rechazó el recordatorio en texto y decidió cortar de raíz: no se abre una rama
  nueva hasta cerrar la que empezó (continuar, cancelar o dejarla para hacer otra cosa).
  Ajuste aceptado: "Dejar y ver lo otro" cierra lo pendiente y atiende en la misma
  respuesta lo que la persona preguntó, sin que lo repita. Registrado como enmienda del
  ADR 0013 regla 1 y en `AGENTS.md`; tarea T9-R1d.

- 2026-09-29: **T9-R1c-2b.** Ruta: delegada, un escritor. `9441796`: causa del
  `RoutingError`: con una pregunta pendiente, el ruteo devolvía `normal_conversation` con
  propuestas de tarea (el mensaje parecía un título) y `RouteEnvelope.validate` lo
  rechazaba en los dos intentos; con pregunta pendiente esas propuestas se descartan (sin
  pregunta, la validación no cambia). Evidencia: 6 fallas idénticas capturadas con un
  gancho temporal; el grabador del banco ahora guarda el intento de ruteo fallido.
  `7b95664`: precondición `borrador_de_alta` que siembra el borrador esperando
  confirmación con el código real (`_advance`, `_finalize`). `8b63aee`: si quien escribe
  no es el aprobador, la respuesta dice de quién espera la confirmación (regla 3).
  `f284b27`: seguimientos (`QUESTION_*`, `pending_action_id` → `pregunta_id`, helper del
  primer cuerpo de una elección, referencia del reenvío sin reloj, falla ruidosa del campo
  sin nombre, aserciones exactas). Suite del escritor 1491 passed, 198 deselected. Padre:
  enfocadas 203 passed. RDD: tramo `331a5f6..f284b27` medio, 897 líneas
  (`slice_budget_reached`), consentida, `review-e11061770c5f40ae` (confiabilidad)
  **aprobada y reconocida**; frontera en `f284b27`. Banco real `b-0022` (n=3): **24/24**
  (antes 16/24). Seguimientos no bloqueantes: idempotencia del reenvío (a T9-R4); prueba
  del aprobador sin nombre legible (a T9-R1c-3).

- 2026-09-29: **T9-R1d-1a.** Ruta: delegada, un escritor. `ed02e06`: con una pregunta
  abierta, `otro_tema` recibe la pregunta de la rama ("Estábamos con {nombre}. ¿Seguimos con
  eso?" [✅ Seguir con eso] [✖️ Dejarlo y ver lo otro]) sin llamar al responder; Dejar cierra
  como `cancela` y atiende el mensaje guardado en la misma respuesta; "No, es otra cosa" de
  `dudoso` es Dejar; una sola pregunta de rama viva por chat; el borrador que espera a otro
  aprobador no es rama de quien lo pidió. Se quitaron el retome posterior, el bloque "#
  Pregunta pendiente" y `agente.NoProponer` (722 líneas agregadas, 1014 quitadas).
  `e46d157`: escenarios del banco a la regla nueva y cinco nuevos. Suite del escritor 1529
  passed, 213 deselected; padre: enfocadas 155 passed. RDD: tramo `f284b27..e46d157` medio,
  2326 líneas, consentida, `review-2282ebc46e7a48e1` (confiabilidad) **aprobada y
  reconocida**; frontera en `e46d157`. Banco real (n=3, 11 escenarios): **28/33**.
  `b-0020-f` 0/3: tras "Dejarlo y ver lo otro" sobre un Modificar de `registrar_bloqueo`, el
  responder atendió "¿qué tareas tengo abiertas?" y además volvió a proponer el bloqueo desde
  el historial: quitar la guarda fue prematuro (T9-R1d-1a-fix). `b-0021-i` 1/3: redacción,
  resume sin nombrar la tarea (T10).

- 2026-09-29: **T9-R1d-1a-fix.** `fe2c8ea`: guarda repuesta sólo en el camino "Dejarlo y
  ver lo otro" (y "No, es otra cosa"): el responder no puede volver a proponer la misma
  herramienta sobre el mismo objetivo que la persona acaba de dejar; el toque de dejar
  sólo con su valor explícito (`dejar`, y `no` de botones viejos), cualquier otro valor
  recibe "ya no está vigente" y la pregunta sigue abierta. Suite del escritor 1543 passed,
  213 deselected; padre: enfocadas 66 passed. RDD: tramo `e46d157..fe2c8ea` medio, 471
  líneas, consentida, `review-ed284b3aec853536` **aprobada y reconocida**; frontera en
  `fe2c8ea` (la observación del `NameError` por la anotación se descartó: `agente.py` tiene
  `from __future__ import annotations`). Banco real (n=3, 11 escenarios de rama): **33/33**
  (antes 28/33).

- 2026-09-29: **T9-R1d-1b.** Ruta: delegada, un escritor. `d863f38` (pruebas de la guarda
  para `destrabar`, `informar_bloqueo`, `adjuntar_evidencia`, `pedir_cambios` y al retomar
  tras aclaración; no hizo falta corregir), `6a424f1` (la vista previa de un cambio que la
  persona pidió y espera su Confirmar es rama: `responde` no aplica nada y vuelve a mostrar
  la vista previa con sus botones; `corrige` va a Modificar con el mensaje como corrección;
  `cancela` la cancela; `otro_tema` hace la pregunta de la rama con la guarda en Dejar),
  `487bff9` (familia `b-0023`). Suite del escritor 1584 passed, 228 deselected; padre:
  enfocadas 101 passed. RDD: tramo `fe2c8ea..487bff9` medio, 1350 líneas, consentida,
  `review-0c99f611fc23e0cd` **aprobada y reconocida**; frontera en `487bff9`. Banco real
  `b-0023` (n=3): 10/15; banco completo (n=1): 71/76. Fallan `b-0001-a`, `b-0001-b` y
  `b-0013`, que ya fallaban antes (sin regresión), y `b-0023`/`b-0023-e`: en un mismo turno
  el responder llamó a `registrar_bloqueo` con el título como id (abrió la aclaración "¿A
  cuál te referís?") y siguió hasta armar la vista previa; la aclaración no era rama y el
  mensaje siguiente pasó de largo con dos cosas abiertas (T9-R1d-1c).

- 2026-09-29: **T9-R1d-1c.** Ruta: delegada, un escritor. El escritor corrigió el
  diagnóstico del padre: en `b-0023` el primer turno sólo abrió la aclaración "¿A cuál te
  referís?" (Jev dejó la referencia ambigua); el segundo mensaje pasó de largo porque esa
  aclaración no era rama. `4ab92a8`: un turno termina en la primera pregunta que abre (una
  llamada posterior que escribe o pregunta se rechaza antes de ejecutarse; las lecturas
  siguen). `d398e4d`: si el aviso y la vista previa no entran juntos, salen en dos partes.
  `9e0d82a`: la elección con botones que pidió Prisma (aclaración, elección de la otra
  tarea de una dependencia, elección de herramienta) es rama; las ofertas de navegación
  (listas, menú de una tarea, `ofrecer_opciones`) no. `21884dd`: siembra de la pregunta
  abierta en el banco y familia `b-0024`. Suite del escritor 1680 passed, 234 deselected;
  padre: enfocadas 187 passed. RDD: tramo `487bff9..21884dd` medio, 2339 líneas,
  consentida, `review-faccc0e9d83561b3` **aprobada y reconocida**; frontera en `21884dd`.
  Banco real `b-0023`/`b-0024` (n=3): **18/21**; las 3 fallas son de redacción (tras
  "Dejarlo y ver lo otro" la consulta se responde, pero resume sin nombrar las tareas en el
  texto; R3-H7, T10).

- 2026-09-29: **T9-R1d-2.** Ruta: delegada, un escritor. `6d78229`: `despachar` retiene
  lo que inicia Prisma (no las respuestas) mientras el destinatario tiene una rama abierta
  en ese chat; una sola definición de rama (`pendientes.ver_rama_abierta`, usada también por
  `gateway._ver_pregunta_abierta`); la fila retenida queda `listo` y sale en orden al
  cerrarse o vencer la pregunta; `despachar` informa `retenidos`. Vencimientos: dato
  pedido por escrito 30 min, elección y vista previa 8 h; las preguntas del alta no vencen,
  así que todavía no retienen (decisión pedida al usuario). `2109fc9`: una elección larga
  vuelve a mostrarse en partes; la siembra de la aclaración del banco usa el constructor
  real. Suite del escritor 1702 passed, 234 deselected; padre: enfocadas 98 passed. RDD:
  tramo `21884dd..2109fc9` alto, 793 líneas, consentida, `review-080f1ef080f22e16` (4
  lentes) **aprobada y reconocida**; frontera en `2109fc9`. Observaciones no bloqueantes:
  la pasada de `despachar` quedó sin tope con filas retenidas (T9-R1d-2b), un urgente se
  retiene igual que el resto (decisión del usuario), comentario del lazo, `Solicitante`
  vacío si falta la membresía, orden por milisegundos en el reenvío en partes.

- 2026-09-29: **T9-R1d-2b.** Ruta: delegada, un escritor. `3255418`: se retiene sólo si
  la persona escribió o tocó algo en ese chat en los últimos 30 minutos
  (`VENTANA_DE_ACTIVIDAD`); la actividad sale de `inbound_message` y cada toque ahora deja
  una fila sin texto (el historial del modelo ya filtraba `texto` vacío); las preguntas
  del alta entran en la definición única de rama (`RAMA_ALTA`) y retienen, acotadas por la
  actividad; la pasada de `despachar` examina como mucho `lote` filas (una fila por vez,
  y las de alguien retenido se excluyen de la consulta); una respuesta nunca se retiene,
  explícito en el helper; sin membresía, no se retiene. Suite del escritor 1719 passed, 234
  deselected; padre: enfocadas 92 passed. RDD: tramo `2109fc9..3255418` medio, 734 líneas,
  `review-3ebe127d376a4d18` **aprobada y reconocida**; frontera en `3255418`. Con esto
  T9-R1d queda completo. El usuario dio consentimiento permanente para las revisiones
  ("aprobar de ahora en adelante las revisiones de forma automática").

- 2026-09-29: **T9-R1c-3.** Ruta: delegada, un escritor. `7bd7c0e`: el transporte manda un
  bloque copiable (entidad `pre` al final del mensaje, desplazamientos en UTF-16) y un
  botón `copy_text` cuando el valor entra en 256; migración `0020_bloque_copiable`
  (`message_outbox.bloque_copiable`, con rollback; **pendiente de aplicar en la base local**:
  `escuchar` y `servir` no arrancan sin ella). `5f232b9`: la vista previa del borrador tiene
  [Confirmar] [Modificar] [Cancelar] cuando quien pide es quien confirma; Modificar (o
  `corrige` escrito) abre el selector de 7 datos; un dato de texto muestra lo escrito en el
  bloque copiable y reemplaza sólo ese dato; uno con opciones vuelve a sus botones; vuelve
  la vista previa actualizada; sólo Confirmar convierte (guarda: un token `modificar` nunca
  convierte). `a96f77d`: `retenidos` cuenta sólo lo realmente retenido y lo vencido de
  alguien retenido se descarta igual. `820c403`: familia `b-0025`. Suite del escritor 1784
  passed, 243 deselected; padre: enfocadas 69 passed. RDD: tramo `3255418..126839f` medio,
  2078 líneas, `review-8563632f45a44f88` **aprobada y reconocida** (consentimiento
  permanente); frontera en `126839f`. Banco real `b-0025` y `b-0022-f` (n=3): **12/12**.

- 2026-09-29: **T9-R1c-3b.** Ruta: delegada, un escritor. `26ec717` (la vista previa
  del borrador sale como respuesta cuando quien pide es quien confirma), `6d096d9` (un solo
  reloj en el despacho), `d1fc9bd` (campo sin fila en Modificar), `3b1b228` (fecha objetivo
  DD/MM/AAAA en la vista previa y el bloque), `0d8a509` (el bloque copiable vuelve al
  repreguntar), `37aa450` ([Volver al resumen] en el selector), `89e2be5` (`b-0025-d`,
  `-e`). Suite del escritor 1806 passed, 249 deselected; padre: enfocadas 73 passed. RDD:
  tramo `126839f..89e2be5` alto, 617 líneas, `review-5125015caf2e7767` (4 lentes)
  **aprobada y reconocida**; frontera en `89e2be5`. Banco real `b-0025` (n=3): **15/15**.
  Seguimientos (a T9-R2): una fecha vacía se mostraría como "None" en la vista previa; la
  prueba parametrizada de repreguntar no controla el campo de la fecha. Sigue pendiente
  la decisión del usuario sobre Modificar cuando confirma otra persona (A: quien pide
  revisa antes de enviar; B: el aprobador modifica; C: como está).

- 2026-09-29: **T9-R2.** Ruta: delegada, un escritor. `050646e` (fecha vacía sin "None";
  la prueba de repreguntar controla el campo que parametriza). `1dbafa5`: migración `0021`
  (`message_outbox.entrante_id` y `respuesta_grupo`; **pendiente de aplicar en la base local
  junto con `0020`**); cada fila encolada en la fase 2 queda atada al mensaje entrante;
  `respuesta_unica.controlar` al cerrar el mensaje: sin respuesta, aviso neutro e incidente
  `sin_respuesta`; con más de una respuesta independiente, queda la que tiene botones (o la
  primera) y las demás se descartan con incidente `respuesta_duplicada`; las partes y los
  grupos cuentan como una. Adjuntos (H15): con epígrafe se procesa el texto y se avisa que
  el adjunto no se guarda; sin epígrafe, "Todavía no puedo recibir fotos, archivos ni
  audios…" (repregunta si hay una pregunta abierta). Los toques quedan fuera del control.
  `09f2fea`: la comprobación de una respuesta por mensaje en todos los escenarios del banco
  y la familia `b-0026`. Hallazgo del escritor: la prueba de migración intermitente falla
  con `tuple concurrently updated` cuando dos sesiones de pytest usan el servidor a la vez.
  Padre: suite completa sola **1858 passed, 264 deselected**. RDD: tramo `89e2be5..09f2fea`
  medio, 1403 líneas, `review-cfe9d0884f17b144` **aprobada y reconocida**; frontera en
  `09f2fea`. Advertencias: caminos con varias respuestas sin agrupar perderían contenido;
  en grupos, un mensaje que a propósito no se respondía ahora recibe el aviso neutro
  (T9-R2b).

- 2026-09-29: **Banco completo (n=1) con la comprobación de una respuesta por mensaje:**
  76/88. Nuevas fallas: la familia `b-0019` entera, `b-0021` y `b-0025-e` con `RoutingError`
  ("Malformed router tool arguments/payload": el proveedor devolvió JSON roto, dos veces
  seguidas); `llm.py` no cambió desde el banco verde anterior, y al repetirlos (n=3) pasaron
  52/54: inestabilidad del proveedor, sin regresión. Las 2 fallas restantes (`b-0021-i`)
  muestran que tras dejar el alta el responder la vuelve a proponer (T9-R2b). Ninguna
  corrida falló la comprobación de una respuesta por mensaje. Siguen `b-0001`, `b-0001-a`,
  `b-0013` (ya fallaban) y `b-0024-b` (redacción).

- 2026-09-29: **T9-R2b.** Ruta: delegada, un escritor. `da04e13`: tras dejar una pregunta,
  el responder recibe un bloque "Lo que la persona acaba de dejar de lado" y, si era del
  alta, la guarda rechaza reabrirla (`crear_tarea`, u `ofrecer_opciones` salvo que todas las
  opciones sean tareas existentes). `d816f81`, `a6056ff`: pruebas reales del epígrafe, del
  toque y de cada camino con varios mensajes (todos ya estaban agrupados). Hallazgo: cuando
  quien pide el alta no es quien confirma, al terminar no le sale nada y el control manda "No
  pude completar eso" (a T9-R3). Suite del escritor 1883 passed, 264 deselected; padre:
  enfocadas 67 passed. RDD: tramo `09f2fea..a6056ff` medio, 615 líneas,
  `review-467d41b3f96573d5` **aprobada y reconocida**; frontera en `a6056ff`. Banco real
  (n=3): `b-0021-i` 3/3 (antes 1/3); `b-0020-f` 2/3 (una corrida afirmó "registré" lo que
  la guarda rechazó, a T9-R3); `b-0024-b` 1/3 (redacción).

- 2026-09-29: **T9-R3.** Ruta: delegada, un escritor. `a90212d`: quien pide un alta que
  confirma otra persona recibe "Le mandé el borrador de la tarea a {nombre} para que lo
  confirme…" (antes, nada y el aviso de falla); los tres estados inertes del alta se
  encolan como respuesta. `38a13c2`: un turno que intentó un cambio sin que se ejecutara
  nada (rechazo de la guarda o error) reescribe su respuesta una vez con la corrección del
  servidor, derivada de los resultados de herramientas y no de frases, y sale con "Estado:
  sin cambios."; los turnos con vista previa no pasan por ahí. `4bf717c`: evidencia sobre
  una tarea sin entregar dice que quedó registrada y que la tarea sigue en su estado, con
  "Ya la terminé" si el menú lo ofrece; el motivo de "Pedir cambios" en el encabezado del
  menú y en el detalle. `48e110e`: el preámbulo no ofrece archivos ni inventa opciones; el
  cierre genérico ofrece "Es una tarea nueva" sólo en privado y no tras dejar el alta.
  `426509f`: familia `b-0027`. Suite del escritor 1940 passed, 276 deselected; padre:
  enfocadas 51 passed. RDD: tramo `a6056ff..426509f` medio, 1645 líneas,
  `review-324fcff7f93c7f19` **aprobada y reconocida**; frontera en `426509f`. Banco real
  `b-0027`, `b-0020-f`, `b-0021-i` (n=3): **18/18**.

- 2026-09-29: **T9-R4.** Ruta: delegada, un escritor. `761f572`: cada toque se acusa antes
  de cualquier trabajo y corre bajo el indicador de ADR 0011; el mismo `callback_data` de la
  misma persona en el mismo chat dentro de 10 s se absorbe (sólo acuse y auditoría);
  migración `0022` (`inbound_message.boton_callback`; **pendiente de aplicar en la base
  local junto con `0020` y `0021`**); el control de una respuesta cubre los toques; "Dejarlo
  y ver lo otro" es una sola respuesta; la clave del estado real del alta y la referencia
  del reenvío salen del evento que los dispara. `89992a6`: familia `b-0028`. Suite del
  escritor 1975 passed, 288 deselected; padre: enfocadas 91 passed. Precisión de la regla 4
  en el ADR 0013 (`f97c5b7`). RDD: tramo `426509f..89992a6` alto, 1336 líneas,
  `review-d9a1348555f00ca4` (4 lentes) **aprobada y reconocida**; frontera en `89992a6`.
  Advertencia importante a T9-R4b: en el toque sobre un borrador, si la resolución falla
  después de marcar el botón, el reintento se absorbe en silencio.

- 2026-09-29: **Decisión del usuario — quien pide revisa antes de enviar (opción A).**
  Precisión del ADR 0005; tarea T9-R1c-4. Además autorizó aplicar `0020`, `0021` y `0022` en
  la base local: respaldo `db/respaldos/prisma-antes-0020-0022-20260929.dump` (525 entradas
  legibles con `pg_restore -l`).
