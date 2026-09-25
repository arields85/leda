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
- [ ] **T3 — Listas como botones.** Una respuesta que presenta tareas para elegir las
  ofrece como botones (por la herramienta de T1 o por la consulta misma).
- [ ] **T4 — Banco.** Escenarios: lista de tareas con botones, tocar una tarea y
  llegar a la vista previa, pregunta de Prisma siempre con opciones; comprobador que
  falla ante una pregunta abierta sin opciones.
- [ ] **T5 — Continuidad.** `docs/capacidades.md`, `docs/STATUS.md`, diseño §4.5 y
  segunda sesión por Telegram.

## Ruta

| Tarea | Ruta | Evidencia del disparador |
|---|---|---|
| T1 | delegada, un escritor | `herramientas.py`, `agente.py`, `gateway.py`, `pendientes.py`, `contexto.py`, pruebas |
| T2 | delegada, un escritor | módulo nuevo o `gateway.py`, `herramientas.py`, pruebas |
| T2b | delegada, un escritor | `herramientas.py`, `gateway.py`, pruebas (3+ archivos de código) |
| T3 | a decidir tras T1 | depende de dónde quede la herramienta |
| T4 | delegada, un escritor | `tests/banco/` |
| T5 | inline | documentación |

## Verificación

- TDD estricto (configuración de la sesión); runner
  `.venv/Scripts/python.exe -m pytest -q`.
- Línea base: 721 passed, 99 deselected (2026-09-24).
- Antes de correr la suite: `pg_isready`.
- Antes de una sesión real: comparar la base local con `db/esquema.sql` y aplicar
  migraciones pendientes (lección de la sesión del 2026-09-25).

## Entrega

Commits sobre `master` por tarea, con pedido explícito del usuario (`AGENTS.md`);
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

