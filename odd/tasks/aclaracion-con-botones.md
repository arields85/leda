# Aclaración con botones

> **Nota del 2026-10-04.** Este documento es anterior al Motor, la línea de trabajo vigente. Lo que
> figure acá como en curso, pendiente o próximo paso no se retoma sin una decisión del usuario. El
> orden de trabajo vigente está en [`docs/STATUS.md`](../../docs/STATUS.md).

**Estado:** cerrada
**Creado:** 2026-09-24
**Origen:** [`ADR 0005`](../../docs/decisions/0005-interpretacion-y-confirmacion.md)
puntos 3 y 4, [`ADR 0006`](../../docs/decisions/0006-jev-para-resolver-referencias-e-intencion.md);
receta en `docs/architecture/interpretacion-y-confirmacion.md` §5.6, §5.8 y §5.9.

## Objetivo

Que Leda sepa a qué tarea se refiere un mensaje antes de actuar, y que ante la
duda pregunte con botones en lugar de adivinar. Hoy el modelo de conversación
extrae y resuelve la referencia a la vez, sin señal de duda.

## Problema (mapa verificado, 2026-09-24)

- `gateway._turno` llama a `route_intent` y, si no es conversación, arranca el
  alta guiada de tarea. `route_intent` no ve las tareas del espacio: un pedido de
  dependencia entre tareas existentes se toma como tarea nueva (`b-0005`, 0 de 10).
- `agente.responder` expone al modelo sólo las tareas propias de quien escribe
  (hasta 15); las herramientas reciben `tarea_id` como texto libre que el modelo
  obtiene de `consultar_tareas`. No hay paso de resolución de referencias.
- `NecesitaElegir` + `pendientes.registrar` + `gateway._toque` ya resuelven una
  elección con botones (hoy sólo personas con nombre repetido). Es el antecedente a
  generalizar. No existe una opción "Ninguna, lo escribo".
- `config.py` no tiene `LEDA_OPENROUTER_API_KEY`; no hay cliente de Jev.

## Alcance

**Incluido:** cliente de Jev y su doble de pruebas; resolución de referencias con
la receta congelada y la verificación; referencias separadas por el enrutador;
resolución antes de actuar, bajo el mismo cursor con RLS del espacio; botones con
propuestas y "Ninguna, lo escribo"; corrección de `b-0005`; respuestas que nombran
la tarea por su título; banco y continuidad.

**Excluido:** aprendizaje de apodos y vocabulario (ADR 0005 punto 5, unidad
propia); detección de intención dudosa como decisión (no es confiable, §5.9: entra
sólo como etiqueta de los botones); decir "no encuentro esa tarea" (§5.9 punto 2).

## Decisiones de esta unidad

- **Etiqueta de los botones.** Cuando la intención es clara, cada botón es una
  propuesta completa ("Pasar «X» a revisión"); cuando no lo es, el botón nombra la
  tarea con su responsable. En los dos casos, elegir lleva a la vista previa de
  siempre, con Confirmar, Modificar y Cancelar.
- **Si Jev no responde,** Leda no adivina: pide que la persona diga a qué tarea
  se refiere.
- **Sólo viajan datos del espacio actual** (títulos, áreas, responsables, glosario
  y el texto del mensaje), leídos bajo el cursor con RLS.

## Tareas

- [x] **T1 — Cliente de Jev y resolución.** `Config.openrouter_api_key`
  (`LEDA_OPENROUTER_API_KEY`); cliente de la API de decisiones de OpenRouter;
  doble guionado para pruebas; función que aplica la receta (alcance, tarea,
  cortes 0,6 / 0,5 / 0,85 con 0,4 de margen / candidatas ≥ 0,1, verificación < 0,5
  → preguntar) y devuelve clara, ambigua o ninguna.
- [x] **T2 — Referencias en el enrutador.** `route_intent` devuelve además las
  referencias a trabajos tal como están dichas, en los tres proveedores y con su
  validación.
- [x] **T3 — Resolver antes de actuar.** En `_turno`, las referencias se resuelven
  contra las tareas activas del espacio. Clara: el agente recibe la tarea resuelta
  como contexto. Una referencia a una tarea existente no arranca el alta de tarea
  nueva (corrige `b-0005`). Jev caído: se pide la referencia.
- [x] **T4 — Botones de aclaración.** Ambigua: una `pending_action` con una opción
  por candidata y "Ninguna, lo escribo". Elegir retoma el mensaje original con la
  tarea resuelta y termina en la vista previa; "Ninguna" pide el texto.
  Además (revisión de T3): la corrección que llega después de Modificar también
  pasa por la resolución de referencias; hoy el modelo la resuelve solo.
- [x] **T5 — Respuestas que nombran la tarea.** Toda respuesta a una consulta
  nombra la tarea por su título (protección de las lecturas, ADR 0006).
- [x] **T7 — Ajustes tras el banco real.** (A) El enrutador separa sólo trabajos,
  no estados ni causas, y una referencia dudosa cuyas candidatas ya quedaron
  resueltas por otra del mismo mensaje se descarta. (B) "Ninguna" no fuerza a
  preguntar si el resto del mensaje es claro. (C) Una referencia que abarca varias
  tareas no abre botones: si es consulta, se responde sobre todas; si es un cambio,
  se pregunta. (D) Para cambiar algo, el modelo llama a la herramienta, que arma la
  vista previa; no pide confirmación con texto. Se vuelve a medir la separación
  sobre los 60 mensajes y se corre el banco real completo (medición y banco real:
  pendientes del orquestador, no de este escritor).
  **Segunda ronda (tras la segunda corrida real, 77/99):** A1 revertida por el
  orquestador (medición propia, ver Progreso) -- `ROUTER_SYSTEM` volvió a la
  redacción de T2. (E) Una referencia de sólo estado nunca llega a Jev. (G)
  Regresión de C: alta de tarea + referencia VARIAS/AMBIGUA sin nada claro
  pregunta con botones, no arranca sola. (H) Las causas de bloqueos abiertos
  viajan en el criterio de Jev (decisión del usuario). (I) El comprobador del
  banco también acepta un pedido de elección en imperativo, sin "?".
  **Tercera ronda (tras la tercera corrida real, 84/99):** (J) Un argumento de
  herramienta inválido no aborta el turno: se valida antes de llamar y vuelve
  como error para que el modelo reintente, sin incidente. (K) Las
  descripciones de `registrar_bloqueo`/`crear_dependencia` distinguen causa
  externa de otra tarea del equipo (alineado con `nucleo/mecanica-pm.md`,
  citado en Progreso). (L) La verificación de una CLARA suma, en la misma
  llamada, una pregunta sobre la subcampeona ("rival"); si es alta, pasa a
  ambigua con las dos (decisión del usuario, "ante la duda se pregunta",
  diseño §5.11). Revisión del orquestador sobre L (mismo día): se sacó el
  corte por `CORTE_CANDIDATA` en la subcampeona -- dejaba afuera justo el
  caso 0,91/0,09 que midió §5.11 (b-0013).
  **Cuarta ronda (tras la cuarta corrida real, 81/99):** (M) "Rival" pasa a
  preguntar por la REFERENCIA, no por el mensaje completo -- la redacción
  vieja hacía que un pedido de dependencia que nombra las dos tareas
  contestara "sí" para las dos referencias (b-0005 9/9, b-0015 3/3 frenaban
  en vez de crear la dependencia); redacción v2 del diseño §5.12
  (orquestador, sin tocar `docs/`). (N) El comprobador del banco también
  acepta "decime qué…"/"contame qué…", no sólo "cuál".
- [x] **T6 — Banco y continuidad.** Grabador de Jev para el banco, escenarios
  ambiguos con botones, `b-0005`; `docs/capacidades.md`, `docs/STATUS.md`, diseño
  §4.5.

## Ruta

| Tarea | Ruta | Evidencia del disparador |
|---|---|---|
| T1 | delegada, un escritor | `config.py`, cliente nuevo, pruebas |
| T2 | delegada, un escritor | `llm.py` (tres proveedores), pruebas |
| T3 | delegada, un escritor | `gateway.py`, `agente.py`, `contexto.py`, pruebas |
| T4 | delegada, un escritor | `gateway.py`, `pendientes.py`, `agente.py`, pruebas |
| T5 | a decidir tras T3 | depende de dónde quede la instrucción |
| T6 | delegada, un escritor | `tests/banco/`, documentación |

## Verificación

- TDD estricto (configuración de la sesión); runner
  `.venv/Scripts/python.exe -m pytest -q`.
- Línea base: 536 passed, 90 deselected (2026-09-24, commit `3c4a9e9`).
- Antes de correr la suite: `pg_isready` (PostgreSQL local no arranca solo).
- Las pruebas unitarias no llaman a Jev ni al modelo: usan dobles guionados.

## Entrega

Commits sobre `master` por tarea, con pedido explícito del usuario (`AGENTS.md`).
Previsión: bastante más de 400 líneas en total, repartidas en seis tareas.

## Progreso

- 2026-09-24: documento creado tras el mapa del recorrido de un mensaje; línea base
  536 passed.
- 2026-09-24: **T1 cerrada.** Ruta: delegada, un escritor (T1 tiene su fila propia
  en "Ruta"; `config.py`, cliente nuevo, pruebas). TDD estricto: RED observado con
  `.venv/Scripts/python.exe -m pytest -q tests/test_jev.py` (`ModuleNotFoundError:
  No module named 'leda.jev'`, 1 error), GREEN con el mismo comando (18 passed).
  Suite completa: `.venv/Scripts/python.exe -m pytest -q` → **554 passed, 90
  deselected** (536 + 18 nuevos, 0 regresiones, 173,87 s).
  - `src/leda/config.py`: agregado `Config.openrouter_api_key` desde
    `LEDA_OPENROUTER_API_KEY`, mismo patrón que `llm_api_key`.
  - `src/leda/jev.py` (nuevo): `ClienteJev` (httpx, `POST
    https://openrouter.ai/api/alpha/decisions`, bearer, reintentos acotados —
    `intentos` por defecto 4 — para timeouts y 429/5xx con espera creciente
    inyectable vía `dormir`; errores no reintentables como 401 no reintentan;
    agotados los intentos lanza `JevError`, nunca infinito); `ClienteJevGuionado`
    (mismo patrón que `ProveedorGuionado` de `llm.py`: cola de respuestas,
    registra `pedidos`, lanza `JevError` si el guion se agota); protocolo `Jev`
    para tipar el colaborador; `TareaCandidata` (id, titulo, area, responsable);
    `ResolucionReferencia` (`TipoResolucion.CLARA/AMBIGUA/NINGUNA`, `tarea_id`,
    `candidatas`); `resolver_referencia_tarea` aplica la receta congelada:
    alcance+tarea en una llamada, ninguna ≥ 0,6 → ninguna, varias ≥ 0,5 →
    ambigua con candidatas ≥ 0,1, top ≥ 0,85 con margen ≥ 0,4 → segunda llamada
    de verificación (Noul), < 0,5 → ambigua con esa tarea como única candidata;
    si no hay tareas, no llama a Jev y devuelve ninguna directamente (principio
    "sin candidatos reales no hay botones"); candidatos que Jev devuelve fuera de
    la lista de entrada se descartan sin romper. Cortes como constantes de
    módulo (`CORTE_NINGUNA`, `CORTE_VARIAS`, `CORTE_CLARA`, `MARGEN_CLARA`,
    `CORTE_CANDIDATA`, `CORTE_VERIFICACION`).
  - `tests/test_jev.py` (nuevo, 18 pruebas): cliente (cuerpo y header
    correctos, fallback sin `answers`, reintento de timeout y de 500 con éxito
    posterior, agotamiento acotado en 4 intentos, no reintento de 401),
    doble guionado (orden, registro de pedidos, `JevError` al agotarse), y la
    receta completa (clara con verificación, ninguna por alcance sin llamar a
    verificación, varias con candidatas ordenadas, sin alcanzar los cortes,
    verificación baja que baja de clara a ambigua, lista vacía sin red, una
    sola tarea sin segunda probabilidad, candidatos ajenos descartados). Sin
    red ni credencial real en ninguna prueba.
  - **Bloqueado:** `.env.ejemplo` no se pudo leer ni editar — el permiso de la
    sesión deniega cualquier archivo `.env*`, incluida la plantilla pública que
    `AGENTS.md` permite explícitamente. No se tocó ese archivo; falta agregar
    `LEDA_OPENROUTER_API_KEY=` a mano o en una sesión con ese permiso
    habilitado.
  - No se conectó a `gateway`/`agente` (es T3). No hubo commit (no pedido
    explícito).
- 2026-09-24: **Revisión del orquestador sobre T1 y corrección.** Dos hallazgos:
  (1) las opciones de la elección "tarea" viajaban con el id real, nunca medido
  como clave de Jev en 5.3-5.9 (esas corridas usaron "T1".."T12"; el id real es
  un UUID); (2) una respuesta de Jev con forma inesperada (falta `alcance`,
  `tarea`, `misma`, `probabilities` o `noul`, o un valor no numérico) rompía con
  `KeyError`/`TypeError` en vez de `JevError`, y T3 sólo va a atrapar `JevError`.
  TDD estricto, mismas reglas (sin commit, sin `.env*`, sin red). RED con
  `.venv/Scripts/python.exe -m pytest -q tests/test_jev.py` → **18 failed, 12
  passed** (las pruebas de la receta esperaban ids reales/claves cortas y las de
  malformado esperaban `JevError` que todavía no se lanzaba). GREEN con el mismo
  comando → **30 passed**. Arreglos en `src/leda/jev.py`:
  - `resolver_referencia_tarea` arma claves cortas `"T1".."Tn"` en el orden de
    `tareas` para el `criteria` de la pregunta "tarea", manda esas claves a Jev,
    y traduce la respuesta de vuelta al `id` real de cada `TareaCandidata`
    (`tarea_id` y `candidatas` siempre llevan el id real, nunca "T1").
  - `_extraer_probabilidades` y `_extraer_noul` (nuevas) validan la forma de
    cada respuesta (`alcance.probabilities`, `tarea.probabilities`,
    `misma.noul`, valores numéricos) y lanzan `JevError` en vez de dejar pasar
    `KeyError`/`TypeError`; se usan en la primera llamada y en la de
    verificación.
  - `tests/test_jev.py`: fixtures de tarea renombradas a ids con forma de
    identificador real (antes "t1".."t3", ahora p. ej. `"8f14e2-tablero-3"`)
    para que la distinción con las claves cortas de wire sea visible; guiones
    actualizados a claves `"T1".."T3"`; prueba nueva
    `test_resolver_referencia_usa_claves_cortas_para_las_opciones_de_jev` (pide
    que `criteria` tenga exactamente `["T1","T2","T3"]` y que el resultado lleve
    el id real); 11 pruebas parametrizadas nuevas de respuesta malformada (7 en
    la primera llamada, 4 en la verificación), todas esperando `JevError`.
  - Suite completa: `.venv/Scripts/python.exe -m pytest -q` → **566 passed, 90
    deselected** (554 + 12 netos, 0 regresiones, 168,39 s).
  - Sigue bloqueado `.env.ejemplo` (mismo motivo que antes); sin cambios a
    `gateway`/`agente`.
  - **Commit:** `158a410` ("feat: add a Jev client that resolves which task a
    reference means"), pedido explícito del usuario -- cierra T1 (incluye
    `.env.ejemplo` con `LEDA_OPENROUTER_API_KEY=`, `src/leda/jev.py`,
    `tests/test_jev.py` y este documento).
- 2026-09-24: **T2 cerrada.** Ruta: delegada, un escritor (T2 tiene su fila
  propia en "Ruta"; `llm.py` en los tres proveedores, pruebas). TDD estricto:
  RED observado con `.venv/Scripts/python.exe -m pytest -q
  tests/test_llm_protocol.py` (`AttributeError: module 'leda.llm' has no
  attribute 'MAX_LONGITUD_REFERENCIA'`, error de colección) y con
  `.venv/Scripts/python.exe -m pytest -q tests/banco/test_corrida.py -k
  "trabajos_y_personas or grabacion_vieja"` (2 failed:
  `TypeError: IntentRoute.__init__() got an unexpected keyword argument
  'trabajos'` y `AttributeError: 'IntentRoute' object has no attribute
  'trabajos'`). GREEN con `tests/banco tests/test_llm_protocol.py` → **225
  passed, 90 deselected**. Suite completa: `.venv/Scripts/python.exe -m
  pytest -q` → **605 passed, 90 deselected** (566 + 39 nuevas, 0 regresiones,
  179,10 s).
  - `src/leda/llm.py`: `IntentRoute` gana `trabajos` y `personas` (tuplas
    inmutables, default `()`); `ROUTER_TOOL["input_schema"]` gana las
    propiedades `trabajos`/`personas` (`array` de `string`, no requeridas) --
    las tres implementaciones de `route_intent` (`ProveedorAnthropic`,
    `ProveedorGemini`, `ProveedorCompatible`) ya arman `Llamada.args` a partir
    de lo que el modelo devuelve para `ROUTER_TOOL`, así que no necesitaron
    tocarse: el esquema y `RouteEnvelope.validate()` compartidos alcanzan.
    `ROUTER_SYSTEM` suma, como párrafo aparte, la instrucción medida del
    enunciado de la tarea ("Separás las referencias de un mensaje de
    trabajo...", en español, verbatim -- es la que las pruebas de concepto
    validaron para el paso de separación de DeepSeek en §5.6, ahora dentro
    del mismo llamado a `route_intent`, sin llamado aparte al modelo).
  - **Política de validación (decisión inicial de esta tarea, superada el
    mismo día -- ver "Revisión del orquestador sobre T2" más abajo):** mismo
    criterio que ya aplica `validate()` al resto del sobre -- cualquier forma
    inesperada **rechaza el sobre entero** con `RoutingError`, nunca se
    descarta en silencio una entrada rara. `trabajos`/`personas` son
    opcionales (ausentes = tupla vacía); si están, tienen que ser una lista
    de strings no vacíos (recortados con `.strip()`), acotada en cantidad
    (`MAX_REFERENCIAS_POR_CAMPO = 20`) y en longitud por entrada
    (`MAX_LONGITUD_REFERENCIA = 200`) -- constantes nuevas en `llm.py`, sin
    equivalente medido en las pruebas de concepto; elegidas para acotar lo que
    un modelo adversarial puede mandar en el mismo sobre, sin límite realista
    para un mensaje humano. `campos_conocidos` en `validate()` ahora incluye
    las dos claves nuevas (antes sólo `action`/`task`), y una entrada fuera de
    ese conjunto sigue rechazando el sobre -- esta parte no cambió con la
    revisión.
  - `ProveedorGuionado.route_intent`: cuando el guion es un `IntentRoute` con
    `trabajos`/`personas`, los arma en el payload igual que ya hacía con
    `task`, para que el guion pase por `validate()` sin cambiar el
    comportamiento de los guiones existentes (sin esos campos, el payload no
    los incluye y `validate()` los devuelve vacíos).
  - `tests/banco/corrida.py`: `_ruta_a_dict`/`_dict_a_ruta` serializan y
    recargan `trabajos`/`personas`; `_dict_a_ruta` usa `.get(..., ())` para
    que una grabación de antes de T2 (sin esas claves) siga cargando con
    referencias vacías -- probado con una grabación armada a mano sin las
    claves nuevas (`test_grabacion_vieja_sin_trabajos_ni_personas_sigue_cargando`).
  - `tests/test_llm_protocol.py` (nuevas): un caso por adaptador
    (`anthropic`/`gemini`/`openai`/`guided`) que confirma que las cuatro
    implementaciones devuelven las mismas referencias recortadas para el
    mismo sobre; un caso por adaptador con los campos ausentes (default
    vacío); redondeo por `ProveedorGuionado`; siete formas inválidas nuevas
    agregadas a la matriz `INVALID_ENVELOPES` (no-lista, entrada no-string,
    entrada vacía tras `.strip()`, entrada más larga que la cota, más
    entradas que la cota, para `trabajos` y `personas`), cada una corrida
    contra los cuatro adaptadores -- **estos siete casos se movieron fuera de
    `INVALID_ENVELOPES` en la revisión del mismo día** (ver más abajo); ya no
    describen el comportamiento vigente.
  - `tests/banco/test_corrida.py` (nuevas): round-trip de `trabajos`/
    `personas` por `ProveedorGrabador` → JSON → `guionado_desde_grabacion`;
    carga de una grabación vieja sin esas claves.
  - No se usaron los campos nuevos en `gateway`/`agente` (es T3); no cambió
    el comportamiento de enrutamiento. Sin llamada real a ningún modelo ni a
    Jev en ninguna prueba. Sin commit (no pedido explícito todavía).
- 2026-09-24: **Revisión del orquestador sobre T2 y corrección.** Motivo:
  `gateway._turno` reintenta `route_intent` dos veces y, agotado, registra un
  incidente de enrutamiento y responde sin efecto -- con la política inicial
  (rechazar el sobre entero), una forma rara en `trabajos`/`personas` (un
  string vacío, 21 elementos) disparaba esa vía para un campo que sólo es
  asesor; el comportamiento de hoy sin referencias tiene que seguir siendo el
  resultado por omisión. TDD estricto, mismas reglas (sin commit, sin
  `.env*`, sin modelo real). RED con `.venv/Scripts/python.exe -m pytest -q
  tests/test_llm_protocol.py -k "degrade_to_empty"` → **32 failed** (una
  `RoutingError` por caso, p. ej. `'personas' entries must not be empty.`, la
  política vieja seguía rechazando el sobre). GREEN con
  `.venv/Scripts/python.exe -m pytest -q tests/test_llm_protocol.py` → **103
  passed**. Verificación pedida:
  - `.venv/Scripts/python.exe -m pytest -q tests/banco tests/test_llm_protocol.py`
    → **229 passed, 90 deselected**.
  - `.venv/Scripts/python.exe -m pytest -q` → **609 passed, 90 deselected**
    (605 + 4 netos -- se sacaron 7 casos × 4 adaptadores de
    `INVALID_ENVELOPES` y entraron 8 casos × 4 adaptadores de degradación, 0
    regresiones, 184,02 s).
  - **Política nueva:** `action`/`task` siguen estrictos, sin cambios. Para
    `trabajos`/`personas`, `_referencias_o_vacio` (antes `_validar_referencias`,
    renombrada porque ya no valida en el sentido de rechazar) nunca lanza
    `RoutingError`: cualquier forma inesperada en ese campo -- no es lista,
    algún ítem no es string, algún ítem queda vacío tras `.strip()`, algún
    ítem supera `MAX_LONGITUD_REFERENCIA`, o la lista supera
    `MAX_REFERENCIAS_POR_CAMPO` -- degrada **el campo entero** a `()`; no hay
    rescate ítem por ítem (todo o nada, simple y predecible, como pidió la
    revisión). Ausente sigue siendo `()`. La política queda documentada en
    el docstring de `_referencias_o_vacio` en `src/leda/llm.py`.
  - `tests/test_llm_protocol.py`: los siete casos de `trabajos`/`personas`
    salieron de `INVALID_ENVELOPES`; entraron a `DEGRADED_REFERENCE_PAYLOADS`
    (ocho casos -- se sumó `personas-blank-entry` para dejar a `personas` con
    la misma cobertura que `trabajos` en el caso vacío) y a
    `test_malformed_references_degrade_to_empty_instead_of_rejecting_the_route`,
    que corre cada caso contra los cuatro adaptadores y comprueba que la ruta
    se devuelve igual (`action` correcta) con `trabajos == ()` y
    `personas == ()`.
  - **Medición del orquestador con el enrutador real** (NaN,
    `deepseek-v4-flash`) sobre los 60 mensajes de los lotes 1 a 4
    (`docs/architecture/interpretacion-y-confirmacion.md` §5.6-§5.9): las
    referencias separadas por `route_intent` coincidieron con la extracción
    separada medida en 57 de 60 mensajes (3 diferencias sin consecuencia),
    **0 errores de validación**, y aplicando la receta de Jev con
    verificación sobre esas referencias, **0 elecciones inseguras sin
    preguntar** (45 de 60 correctas, el resto preguntas de más) -- evidencia
    de que unir la separación de referencias al mismo llamado de
    `route_intent` no perdió lo que medían §5.6-§5.9 por separado. Medición
    del orquestador, no de este escritor; no hay un comando de esta sesión
    que la reproduzca.
  - **Commit:** `0dcef8b` ("feat: make the intent router return the
    references it mentions"), pedido explícito del usuario -- cierra T2
    (incluye `src/leda/llm.py`, `tests/test_llm_protocol.py`,
    `tests/banco/corrida.py`, `tests/banco/test_corrida.py` y este
    documento).
- 2026-09-24: **T3 cerrada.** Ruta: delegada, un escritor (T3 tiene su fila
  propia en "Ruta"; `gateway.py`, `agente.py`, `contexto.py`, pruebas --
  también `jev.py` y `tests/banco/corrida.py`, extensión natural de la
  fábrica de Jev y del banco). TDD estricto: RED observado con
  `.venv/Scripts/python.exe -m pytest -q tests/test_resolucion_referencias.py`
  (`AttributeError: <module 'leda.jev' ...> has no attribute 'desde_base'`,
  7 failed / 1 passed -- la prueba que pasaba de entrada fue la de "sin
  credencial", antes de la corrección del usuario, porque no hacía falta
  código nuevo para no cambiar nada). GREEN con el mismo comando -- **9
  passed**. Verificación pedida:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_resolucion_referencias.py
    tests/test_gateway.py tests/test_agente.py tests/test_jev.py tests/banco`
    → **184 passed, 90 deselected**.
  - `.venv/Scripts/python.exe -m pytest -q` → **618 passed, 90 deselected**
    (609 + 9 nuevas, 0 regresiones, 249,41 s).
  - **Decisión del usuario, 2026-09-24 (cambio de requisito a mitad de
    tarea):** sin `LEDA_OPENROUTER_API_KEY`, Leda **no** sigue como si
    Jev no existiera. Con referencias en el mensaje, la falta de credencial
    se trata igual que un `JevError` en cada una -- se le pide al modelo que
    pregunte, nunca que elija solo -- y además deja un incidente (sin
    secretos ni texto del mensaje) para que la falta de configuración no
    pase inadvertida. Un mensaje sin referencias no se toca. Reemplaza el
    criterio original de T3 ("si la clave está vacía, saltear la resolución
    por completo... para que las pruebas y los despliegues sin la clave no
    cambien"): ese criterio hubiera dejado a Leda adivinando en cualquier
    despliegue sin la clave configurada, que es justo lo que esta unidad
    existe para evitar.
  - `src/leda/jev.py`: `desde_base(api_key) -> Jev | None` -- `None` si
    `api_key` está vacía, si no un `ClienteJev`. Mismo patrón de reemplazo
    que `llm.desde_base`: un import local en `_turno` lee este nombre del
    módulo en cada turno, así que alcanza con reemplazar
    `leda.jev.desde_base` para las pruebas y para que el banco no llame a
    Jev de verdad por defecto.
  - `src/leda/contexto.py`: extraídas `_glosario_filas` y `_lineas_glosario`
    de adentro de `construir()`, y agregada `vocabulario(cur, workspace_id)
    -> str` (mismo glosario en texto plano, vacío si no hay) -- para no
    repetir la consulta y para que `gateway.py` pueda pasarle el mismo
    vocabulario del equipo a Jev (ADR 0006, "sólo viajan datos del espacio
    actual"). `construir()` se comporta igual que antes (probado por
    `test_contexto_lleva_nucleo_glosario_y_equipo`, sin tocar).
  - `src/leda/agente.py`: `responder()` gana `contexto_referencias: str |
    None = None`, agregado al sistema igual que `modificacion` -- contexto
    de confianza del servidor, nunca texto de la persona.
  - `src/leda/gateway.py`, en `_turno` (después de `route_intent`, antes
    de decidir alta guiada vs. `agente.responder`):
    `_resolver_referencias_del_turno` arma las tareas activas del espacio
    (`_tareas_activas`: `estado not in ('terminada', 'cancelada')`, con
    título/área/responsable, bajo el mismo cursor con RLS que ya tiene
    `_turno`) y el vocabulario, resuelve cada referencia con
    `jev.resolver_referencia_tarea` en un `ThreadPoolExecutor` chico
    (`_resolver_en_paralelo`, sin tocar la base), arma el bloque de
    contexto (`_bloque_contexto_referencias`: clara dice qué tarea usar,
    ambigua lista candidatas y pide preguntar sin elegir, ninguna dice que
    no invente, y una referencia con `JevError` -- Jev caído, respuesta
    malformada, o sin credencial -- pide aclaración) y dejar una única
    entrada de auditoría por turno (`_auditar_resolucion`: `accion =
    "resolucion_referencias"`, por referencia sólo el tipo y los ids de
    tarea/candidatas, nunca el mensaje ni el texto de la referencia). Sin
    referencias, `_resolver_referencias_del_turno` devuelve `None` sin
    tocar la base ni la red.
  - **b-0005 corregida:** si la acción del enrutador es
    `START_TASK_INTAKE` pero al menos una referencia resolvió **clara** a
    una tarea existente, no arranca el alta guiada: va a
    `agente.responder` con la tarea resuelta como contexto (puede llamar
    `crear_dependencia`, etc.). Ambigua, ninguna, o sin resolver mantiene el
    ruteo de siempre (T4 va a agregar la opción explícita "Crear una tarea
    nueva" para el caso mixto).
  - **Decisión de esta unidad -- Modificar sin resolución.** El camino de
    `reclamar_modificacion_abierta` sigue directo a `agente.responder`, sin
    pasar por resolución de referencias: hacerlo exigiría rutear ese
    mensaje aparte sólo para separarlas (`route_intent` no corre en esa
    rama), lo que no es el caso simple que este bullet pedía preferir. Ese
    mensaje además ya lleva su propio contexto de confianza
    (`modificacion`, la propuesta que se está corrigiendo). Documentado acá
    como decisión, no como pendiente.
  - `tests/banco/corrida.py`: `ejecutar_escenario` gana `cliente_jev`
    opcional y reemplaza `jev.desde_base` con el mismo patrón que ya usa
    para `llm.desde_base` (guardar el original, reemplazar, restaurar en el
    `finally`). Por defecto es un `ClienteJevGuionado(guion=[])` --
    explícito, nunca `None` (que desde esta unidad hace que Leda pida en
    vez de adivinar) -- pero sin ninguna respuesta preparada, así que el
    banco no llama a la red por defecto; ningún escenario actual trae
    `trabajos` que lo ejerciten (T6 va a agregar un grabador real de Jev).
    Replays existentes sin tocar, siguen pasando.
  - `tests/test_resolucion_referencias.py` (nuevo, 9 pruebas, contra
    `gateway._turno` con `corework`/`intake_world`, proveedor y Jev
    guionados, sin red): sin credencial + con referencias → pregunta y dos
    aserciones de auditoría/incidente sin secretos ni texto (decisión del
    usuario); sin credencial y sin referencias → nada cambia; clara → el
    bloque de contexto llega al modelo con título e id; ambigua → pregunta
    sin elegir, sin `"Usá esa tarea"`; ninguna → no inventa y no llama a
    Jev (lista de tareas vacía, principio "sin candidatos no hay red");
    Jev caído (guion agotado) → pide la referencia, el turno sigue y
    responde igual; b-0005 → ninguna fila en `task_intake_request`, pasa a
    `agente.responder` con la tarea resuelta; RLS con `intake_world` (dos
    espacios reales) → sólo el título del espacio activo llega a
    `criteria`, nunca el del otro; auditoría → una sola entrada, `detalle`
    sin el texto del mensaje ni el de la referencia.
  - T4/T5 quedan igual que estaban: sin botones (T4) y sin la instrucción
    de nombrar la tarea en las consultas (T5). No hubo commit (no pedido
    explícito todavía).
- 2026-09-24 (orquestador): revisión de T3. Control: `pytest -q
  tests/test_resolucion_referencias.py tests/banco` → 135 passed, 90 deselected.
  Hallazgos anotados: (1) la corrección después de Modificar no pasa por Jev: el
  modelo resuelve solo la tarea; se agrega a T4. (2) El banco con modelo real usa por
  defecto un Jev guionado vacío: un escenario con referencias termina preguntando
  hasta que T6 agregue el grabador de Jev; el banco real no se corre antes de T6.
  (3) El texto de la referencia entra en el bloque de sistema entre comillas; viene
  del mismo mensaje de quien escribe y las herramientas revalidan autoridad, así que
  el riesgo queda acotado a su propio turno. (4) Sin tope de tareas: el límite de
  ~700 de la ventana de Jev sigue pendiente (ADR 0006 punto 5).
  **Commit de T3:** `cb51f06` ("feat: resolve task references with Jev before
  acting"), pedido explícito del usuario -- faltaba registrarlo acá.
- 2026-09-24: **Decisiones del usuario para T4** (quedan incorporadas al
  encabezado de la tarea T4 y a "Decisiones de esta unidad" más arriba, y acá
  como referencia rápida de lo que pidió el usuario, palabra por palabra en
  sustancia):
  1. `jev.resolver_referencia_tarea` gana `quien_escribe` opcional (nombre de
     quien escribe); si se pasa, viaja como campo `quien_escribe` del
     `state` en las DOS llamadas (alcance/tarea y verificación) -- sin texto
     ni pista agregada a las instrucciones (medido en §5.10: la pista
     empeoró la receta, el dato solo es seguro). `_turno` manda el nombre de
     quien escribe.
  2. Ambigua con candidatas: en vez de la pregunta en texto, una
     `pending_action` (reusando `pendientes.registrar`/`_crear_opcion`/
     outbox/`gateway._toque`; dueño, vencimiento, tokens de un solo uso,
     sólo la misma persona) con un botón por candidata -- el título de la
     tarea, y " — <primer nombre del responsable>" sólo cuando la tarea es
     de otra persona, nunca de quien escribe -- en orden: las tareas propias
     primero, después el resto en el orden de Jev; títulos largos truncados
     con "…" a una constante con nombre (~48 caracteres), sin recortar nunca
     el sufijo del responsable. Último botón siempre "Ninguna, lo escribo".
     Caso mixto de b-0005: si la acción del enrutador era alta de tarea y
     hay una referencia ambigua, se agrega "Es una tarea nueva", que sigue
     al alta guiada tal como la hubiera arrancado la ruta original.
  3. Elegir una candidata retoma el mensaje ORIGINAL: `agente.responder`
     corre con la referencia ya resuelta como contexto, así que el camino de
     siempre (herramienta → vista previa → Confirmar/Modificar/Cancelar)
     sigue igual. El toque en sí no aplica nada. Si quedan más referencias
     ambiguas, se pregunta la siguiente con botones antes de retomar -- una
     pregunta a la vez. Lo necesario para retomar (texto original, datos de
     la ruta, lo ya resuelto) se guarda en los `args` de la `pending_action`
     -- nunca en logs ni auditoría.
  4. "Ninguna, lo escribo": cierra la acción pendiente sin efecto, pide el
     texto, y el próximo mensaje de esa persona en ese chat dentro de la
     misma ventana de 30 minutos de Modificar (`pendientes.
     VENTANA_MODIFICACION`) se interpreta con el mensaje original como
     contexto -- reusando el mecanismo de Modificar en vez de inventar uno
     paralelo.
  5. La corrección que llega después de Modificar (hallazgo de la revisión
     de T3) también pasa por resolución: se rutea (`route_intent`) para
     sacar sus referencias, y se resuelven con Jev como en cualquier turno,
     antes de que `agente.responder` reciba el contexto de Modificar.
  6. Auditoría: qué tipo de opción se eligió y, si aplica, el id de tarea --
     nunca el mensaje ni el texto de la referencia.
  7. Ambigua sin candidatas, ninguna, y Jev caído mantienen el comportamiento
     de T3 (pregunta en texto, sin adivinar).
- 2026-09-24: **T4 cerrada.** Ruta: delegada, un escritor (T4 tiene su fila
  propia en "Ruta"; `gateway.py`, `pendientes.py`, pruebas -- también
  `jev.py`, extensión natural del cliente). TDD estricto: RED observado con
  `.venv/Scripts/python.exe -m pytest -q tests/test_jev.py -k quien_escribe`
  (`TypeError: resolver_referencia_tarea() got an unexpected keyword
  argument 'quien_escribe'`, 1 failed / 1 passed -- la prueba que pasaba de
  entrada confirmaba el comportamiento sin el campo, sin código nuevo) y con
  `tests/test_aclaracion_botones.py` recién creado contra el `gateway.py` de
  T3 (10 de 14 pruebas fallaban: `AttributeError` por `herramienta` sin
  reconocer, `pending_action` inexistente, o el texto de siempre en vez de
  botones). GREEN con
  `.venv/Scripts/python.exe -m pytest -q tests/test_aclaracion_botones.py
  tests/test_jev.py tests/test_resolucion_referencias.py tests/test_modificar.py
  tests/test_gateway.py tests/test_agente.py tests/banco` → **215 passed, 90
  deselected**. Suite completa: `.venv/Scripts/python.exe -m pytest -q` →
  **634 passed, 90 deselected** (618 + 16 nuevas, 0 regresiones, 138,51 s).
  - `src/leda/jev.py`: `resolver_referencia_tarea` gana `quien_escribe:
    str | None = None`; si se pasa, entra como `state["quien_escribe"]` en
    las dos llamadas (alcance/tarea y verificación) -- nunca como texto
    agregado a `INSTRUCCION_ALCANCE`/`INSTRUCCION_TAREA`/
    `INSTRUCCION_VERIFICACION` (§5.10: la pista empeoró la receta). Nuevo
    campo `TareaCandidata.responsable_membership_id` (opcional, default
    `None`) -- no entra en `criterio()` (lo único que viaja a Jev), sólo
    sirve del lado de `gateway.py` para ordenar los botones.
  - `src/leda/gateway.py` (la mayor parte de esta unidad):
    - Constantes nuevas: `_SENTINEL_ACLARACION` (el `herramienta` de una
      `pending_action` de aclaración -- nunca un nombre real de
      `herramientas.REGISTRO`, así que `_toque` la intercepta antes de
      `H.ejecutar`, que si no la rechazaría), `_OPCION_NINGUNA`/
      `_OPCION_NUEVA` (valores reservados de botón, nunca un id de tarea
      real -- los ids son UUID), `TRUNCAR_TITULO_BOTON = 48`.
    - `_tareas_activas` suma `responsable_membership_id` a la consulta.
      `_resolver_en_paralelo` y `_resolver_referencias_del_turno` mandan
      `quien_escribe=quien.nombre` a Jev.
    - `_ReferenciasResueltas` gana `resueltas_claras` (referencia → id de
      tarea, sólo las claras) y `pendientes_boton` (referencia → candidatas
      ya armadas para botón, en el orden del enrutador) -- una referencia
      ambigua CON candidatas ya no entra en el bloque de texto de siempre
      (`_bloque_contexto_referencias` corre sólo sobre lo que sigue siendo
      terminal en este turno: clara, ninguna, ambigua sin candidatas, Jev
      caído).
    - `_candidatas_para_botones`/`_etiqueta_boton` arman la lista y el texto
      de cada botón: las tareas de quien escribe primero (comparando
      `responsable_membership_id` contra `quien.membership_id`), el resto
      después, cada grupo en el orden de Jev (`resolucion.candidatas` ya
      viene ordenada por probabilidad); el título se trunca a
      `TRUNCAR_TITULO_BOTON` con "…" antes de agregar " — <primer nombre>",
      que nunca se recorta, y sólo se agrega cuando la tarea es ajena.
    - `_turno` queda reorganizado alrededor de un estado que sigue el
      mensaje mientras se preguntan botones: `_estado_inicial_aclaracion`
      arma ese estado (mensaje, `entrante_id`, acción y propuesta de tarea
      del enrutador, lo ya resuelto, el bloque de texto de lo terminal, si
      hay clara, y lo pendiente de preguntar); `_avanzar_aclaracion` decide,
      con ese estado, si falta preguntar (`_preguntar_por_botones`, una
      referencia a la vez) o si ya se puede retomar -- a Modificar si hay
      corrección de por medio, al alta guiada (b-0005, sólo sin ninguna
      referencia resuelta) o al agente, con el contexto acumulado.
      `_iniciar_alta_guiada` es el mismo camino que ya tenía `_turno`,
      extraído para que también lo use "Es una tarea nueva".
    - `_preguntar_por_botones` arma las opciones (una por candidata, "Es una
      tarea nueva" sólo sin Modificar de por medio y con el enrutador
      pidiendo alta de tarea, y "Ninguna, lo escribo" siempre al final) y
      registra la `pending_action` con `campo="eleccion"` -- así
      `resolver_pendiente` devuelve, en `args["eleccion"]`, qué botón se
      tocó, reusando el mecanismo genérico de elección sin tocar SQL.
    - `_toque` intercepta `resuelta.herramienta == _SENTINEL_ACLARACION`
      antes de `H.ejecutar` y llama a `_resolver_toque_aclaracion`, que
      audita la elección (`accion="aclaracion_referencia"`, `detalle` con
      el tipo y, si aplica, el id de tarea -- nunca mensaje ni referencia,
      decisión 6) y bifurca en tres: "Ninguna, lo escribo" marca para
      corregir (`pendientes.marcar_para_corregir`) y responde pidiendo el
      texto; "Es una tarea nueva" va directo a `_iniciar_alta_guiada`; una
      candidata arma el estado con esa referencia resuelta (título sacado
      de los propios `args["candidatas"]`, sin volver a tocar la base) y
      sigue por `_avanzar_aclaracion` -- a la siguiente pregunta si queda
      otra ambigua, o a retomar si no queda ninguna.
    - `_resumir_aclaracion_ninguna`: cuando `_turno` reclama una
      Modificación abierta cuyo `herramienta` es el centinela de
      aclaración, no vuelve a rutear ni a llamar a Jev -- arma un bloque de
      contexto con el mensaje original (mismo patrón que
      `_bloque_modificacion`) y llama a `agente.responder` con el mensaje
      nuevo como texto de la persona.
    - **Revisión de T3 (corrección de esta unidad):** `_turno` ya no
      devuelve apenas detecta una Modificación real -- ahora corre
      `route_intent` y `_resolver_referencias_del_turno` igual que
      cualquier turno, y sólo entonces, si había una corrección real (no la
      de "Ninguna"), llama a `agente.responder(modificacion=...,
      contexto_referencias=...)`. Las semánticas de Modificar no cambiaron:
      sigue sin arrancar el alta guiada nunca, sigue yendo siempre a
      `agente.responder`; lo nuevo es que ese mensaje ya no le llega al
      modelo a resolver solo.
    - `src/leda/pendientes.py`: `pending_action_id_de` (el id de la
      acción pendiente dueña de un token) y `marcar_para_corregir` (deja
      `modificar_pedido_en`/invalida cualquier otra Modificación sin leer de
      la misma persona y chat) -- **decisión de reuso, no de SQL nueva:** no
      se pudo reusar la rama de `resolver_pendiente` que hace esto mismo
      para Modificar tal cual, porque esa rama exige `campo is null` para
      reconocer el valor especial `"modificar"`, y la fila de aclaración ya
      usa `campo="eleccion"` para que la elección del botón vuelva en
      `args`. Se marca en Python, después de resolver, con el mismo efecto
      en las mismas dos columnas -- `reclamar_modificacion_abierta` no mira
      `estado`, así que funciona igual aunque la fila haya quedado
      `resuelta` en vez de `cancelada`. Sin cambios a SQL ni migración: no
      hizo falta.
  - `tests/test_jev.py` (+2): `quien_escribe` viaja en el `state` de las dos
    llamadas cuando se pasa; sin pasarlo, ni el campo ni ninguna pista nueva
    en las instrucciones.
  - `tests/test_resolucion_referencias.py`: la prueba de T3
    `test_referencia_ambigua_pregunta_sin_actuar` probaba exactamente el
    escenario que esta unidad reemplaza (ambigua con dos candidatas por
    encima del corte) -- pasó a
    `test_referencia_ambigua_sin_candidatas_pregunta_en_texto`, con
    probabilidades por debajo de `CORTE_CANDIDATA` para seguir cubriendo el
    requisito 7 (sin candidatas, sigue el texto de T3, cero
    `pending_action`).
  - `tests/test_aclaracion_botones.py` (nuevo, 14 pruebas, contra
    `gateway._turno`/`gateway._toque` vía `procesar_update` con
    `callback_query`, proveedor y Jev guionados, sin red): `quien_escribe`
    llega a Jev desde el turno; orden y etiqueta de los botones (propia sin
    nombre, ajena con el primer nombre, título largo truncado sin recortar
    el sufijo -- con Jev devolviendo las candidatas en un orden que no es
    "propia primero", para probar que el reordenamiento es del lado de
    `gateway.py`); elegir candidata retoma y llega a la vista previa de
    `actualizar_estado` sin aplicar nada (estado de la tarea sin tocar
    hasta Confirmar); dos referencias ambiguas preguntan una por vez (la
    segunda pregunta reemplaza a la primera, no coexisten); "Ninguna, lo
    escribo" cierra sin efecto y marca `modificar_pedido_en`, el siguiente
    mensaje dentro de la ventana usa el original como contexto sin volver a
    llamar a Jev, y pasada la ventana (simulada por SQL, no por `sleep`) el
    siguiente mensaje es un turno común; "Es una tarea nueva" sigue al alta
    guiada (y no aparece cuando la ruta es conversación normal); la
    corrección después de Modificar se rutea y se resuelve con Jev antes de
    llegar a `agente.responder` con el contexto de Modificar (revisión de
    T3); toque de otro integrante, vencido, y repetido -- las garantías
    existentes de `pending_action`/`resolver_pendiente`, reusadas sin
    cambios para las filas de aclaración; auditoría de la elección sin
    mensaje ni texto de la referencia.
  - **T5 sigue igual que estaba** (sin la instrucción de nombrar la tarea en
    las consultas). **T6 sin tocar** (banco real, grabador de Jev). No hubo
    commit (no pedido explícito todavía).
- 2026-09-24 (orquestador): revisión de T4 y corrección. Hallazgo: al retomar
  después de "Ninguna, lo escribo", `_resumir_aclaracion_ninguna` no volvía a
  rutear ni a llamar a Jev sobre el mensaje de aclaración -- lo trataba sólo
  como texto libre con un bloque de contexto fijo, así que si la persona
  nombraba la tarea con sus propias palabras ("es la de máq. 3") esa
  referencia nunca se resolvía. TDD estricto, mismas reglas (sin commit, sin
  `.env*`, sin modelo real, sin tocar el documento de diseño). RED con
  `.venv/Scripts/python.exe -m pytest -q tests/test_aclaracion_botones.py -k
  ninguna` → **2 failed, 2 passed** (el mensaje de aclaración nunca llegaba a
  `route_intent`, y una referencia nueva en ese mensaje no se resolvía).
  GREEN con el mismo comando → **4 passed**. Arreglo en
  `src/leda/gateway.py`: `_resumir_aclaracion_ninguna` ahora rutea
  (`route_intent`) y resuelve (`_resolver_referencias_del_turno`) el mensaje
  de aclaración como cualquier turno -- mismo camino que ya usa la
  corrección real de Modificar -- y arma su propio bloque de contexto (no
  `_bloque_modificacion`, que hubiera hablado de una vista previa y una
  herramienta que no existen) que nombra la referencia sin resolver y el
  mensaje original, conserva lo ya resuelto de otras referencias en ese
  turno (`bloque_base` guardado en `args`), y fuerza `route_action` a
  conversación normal para que este retomo nunca dispare el alta guiada.
  Verificación pedida:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_aclaracion_botones.py
    tests/test_modificar.py tests/test_resolucion_referencias.py tests/banco`
    → **165 passed, 90 deselected**.
  - `.venv/Scripts/python.exe -m pytest -q` → **635 passed, 90 deselected**
    (634 + 1 neta, 0 regresiones, 142,18 s).
  - `tests/test_aclaracion_botones.py`: la prueba de la ventana ahora
    comprueba el bloque nuevo (sin "Modificar" ni el nombre del centinela,
    con la referencia y el mensaje original, y `proveedor.ruteados[-1]`
    igual al mensaje de aclaración); prueba nueva
    `test_ninguna_el_siguiente_mensaje_puede_traer_su_propia_referencia`
    (la aclaración nombra la tarea con otras palabras, Jev la resuelve, y el
    bloque de sistema dice "Usá esa tarea"). La prueba de Modificar real
    (`test_correccion_de_modificar_pasa_por_route_intent_y_jev`) sigue sin
    tocar y sigue pasando: ese camino no cambió.
  - **Commit de T4:** `9ee5d54` ("feat: ask with buttons when a task
    reference is ambiguous") -- faltaba registrarlo acá.
- 2026-09-24: **T5 cerrada.** Ruta: delegada, un escritor (T5 tiene su fila
  propia en "Ruta"; `agente.py`, `contexto.py`, `gateway.py`, pruebas). TDD
  estricto: RED observado guardando (`git stash`) los tres archivos de
  `src/leda` tocados por esta unidad y corriendo
  `.venv/Scripts/python.exe -m pytest -q tests/test_respuestas_nombran_tarea.py
  tests/test_resolucion_referencias.py` sobre el código de T4 sin tocar --
  **6 failed, 9 passed** (los 4 casos nuevos de `test_respuestas_nombran_
  tarea.py` que sí dependen del guardia, más las dos aserciones nuevas de
  `test_resolucion_referencias.py` sobre la instrucción y el turno completo;
  los otros 2 casos nuevos -- "sin referencia resuelta" y la aserción vieja
  de "Usá esa tarea" -- ya pasaban sin código nuevo, como corresponde). GREEN
  restaurando la implementación (`git stash pop`) con el mismo comando --
  **15 passed**. Verificación pedida:
  - `.venv/Scripts/python.exe -m pytest -q tests/test_respuestas_nombran_tarea.py
    tests/banco` → **131 passed, 90 deselected**.
  - `.venv/Scripts/python.exe -m pytest -q` → **641 passed, 90 deselected**
    (635 + 6 nuevas, 0 regresiones, 134,45 s).
  - **Dos capas, como pedía la tarea:**
    1. *Instrucción* (contexto de confianza, nunca garantía): `contexto.py`
       `PREAMBULO` gana una viñeta ("Cuando contestes algo sobre una tarea
       puntual, nombrala por su título exacto..."); la línea CLARA de
       `gateway._bloque_contexto_referencias` (T3) suma "Si contestás algo
       sobre ella, nombrala por su título exacto." a la instrucción que ya
       tenía ("Usá esa tarea; no la vuelvas a resolver.").
    2. *Guardia determinística* (la protección real): `agente.responder` gana
       `tareas_resueltas_claras: tuple[str, ...] = ()` -- los ids que el
       turno resolvió CLARA vía Jev (T3/T4; en la práctica, el mismo
       `estado["resueltas"]` que ya arma `gateway._avanzar_aclaracion` a
       partir de `_ReferenciasResueltas.resueltas_claras`, que también
       incluye una candidata elegida por botón en T4 -- una elección
       explícita de la persona es, si acaso, más confiable que una CLARA de
       Jev, así que compartir el mismo dato es la extensión natural, no un
       agregado aparte). `gateway.py` pasa
       `tareas_resueltas_claras=tuple(estado["resueltas"].values())` en los
       dos lugares donde ya llamaba a `agente.responder` (con Modificar y
       sin Modificar).
  - **Punto más angosto elegido para el guardia:** dentro de `responder()`,
    justo después de `normalize_visible_text(revisar_salida(...))` y antes de
    `with_no_effect_status`/`_encolar_respuesta` -- es el único lugar donde
    ya existe el texto final de la vuelta que cerró el turno (`cerro`) y
    antes de que ese texto se escriba en el outbox o se audite. Las dos
    salidas tempranas (confirmaciones/elecciones con vista previa, y el
    turno que se queda sin vueltas) devuelven antes de llegar ahí, así que
    quedan protegidas por construcción, sin condición extra: nunca hay una
    vista previa ni una pregunta que lleve la línea de T5.
  - **Qué cuenta como "la tarea la devolvió `consultar_*`":** sólo
    `consultar_tareas`, no las otras tres herramientas `consultar_*`. Es la
    única cuyo campo `"id"` del resultado es de verdad un id de tarea;
    `consultar_bloqueos` también devuelve `"id"`+`"titulo"` en cada fila,
    pero ese `"id"` es el id del bloqueo, no el de la tarea que nombra
    `"titulo"` -- tratarlas igual hubiera podido, en teoría, cruzar un id de
    bloqueo con un id de tarea que casualmente resolvió Jev. `_ejecutar_una`
    ahora recibe un `tareas_consultadas: dict[str, str]` que sólo se llena
    cuando `c.nombre == "consultar_tareas"` y cada fila trae `id` y `titulo`.
  - **Comparación:** `_normalizar_comparacion` (nuevo, `agente.py`) usa
    `unicodedata.normalize("NFKD", ...)` para sacar los acentos, colapsa
    espacios y aplica `casefold()` -- sin acentos, sin mayúsculas, sin
    depender del espaciado exacto que haya usado el modelo.
    `_nombrar_tareas_sin_mencionar` compara el título así normalizado contra
    la respuesta completa así normalizada (substring, no exacto: "CABLEAR
    TABLERO maq. 3" dentro de una frase más larga sigue contando como
    nombrada). Si falta más de un título, antepone una línea por cada uno,
    en el orden de `tareas_resueltas_claras`, antes de un salto de línea
    doble y el texto del modelo tal cual -- nunca reescribe lo demás.
  - **`salida.py` sin cambios:** revisado, no hizo falta tocarlo. El prefijo
    que antepone el guardia es corto (una línea por título faltante) y
    `_encolar_respuesta` ya llama a `enqueue_outbox` con `allow_split=True`,
    así que aunque el prefijo empujara un texto ya cerca del límite de 4096
    unidades UTF-16, `prepare_payload`/`_split` lo parte igual que a
    cualquier respuesta larga -- no hay un límite nuevo que cuidar.
  - `tests/test_respuestas_nombran_tarea.py` (nuevo, 5 pruebas, contra
    `agente.responder` directo -- mismo patrón que `tests/test_agente.py`,
    sin Jev ni red, `tareas_resueltas_claras` pasado a mano): título ausente
    → se antepone "Sobre «título»:"; título presente con mayúsculas y sin el
    acento de «máq.» → no se toca; sin `tareas_resueltas_claras` (default) →
    no se toca aunque `consultar_tareas` haya traído la tarea; herramienta de
    escritura con vista previa (`actualizar_estado`) → `r.texto == ""` y el
    cuerpo de la vista previa sale tal cual, sin la línea de T5; dos tareas
    resueltas, una sin nombrar → sólo se antepone esa.
  - `tests/test_resolucion_referencias.py` (+2, sobre `gateway._turno`
    completo): la prueba de T3 de la instrucción CLARA suma la aserción de
    la frase nueva; prueba nueva
    `test_referencia_clara_protege_la_respuesta_que_no_nombra_la_tarea`
    (clara vía Jev + `consultar_tareas` + respuesta del modelo sin el título
    → el outbox lleva "Sobre «Cablear tablero máq. 3»:" antepuesto) --
    confirma que el cableado de `gateway.py` (pasar `tareas_resueltas_
    claras` en los dos lugares que llaman a `agente.responder`) funciona de
    punta a punta, no sólo la función aislada.
  - No hubo commit (no pedido explícito todavía). **T6 sigue sin tocar**
    (banco real, grabador de Jev).
- 2026-09-24 (orquestador): revisión de T5 y corrección. Motivo: la primera
  versión sólo protegía una respuesta cuando, además de resolver CLARA la
  referencia, `consultar_tareas` la había devuelto en ese mismo turno -- una
  respuesta armada con otro contexto del sistema (p. ej. el bloque de "tareas
  abiertas" que ya trae `contexto.construir`, o cualquier otra herramienta
  `consultar_*`) quedaba sin proteger, justo el caso que T5 existe para
  cubrir. Nueva condición: por cada tarea que el turno resolvió CLARA (T3) o
  por botón (T4), si el turno cierra con una respuesta visible y esa
  respuesta no nombra la tarea por su título exacto, se antepone la línea --
  sin depender de qué herramienta corrió, ni de que haya corrido alguna. TDD
  estricto, sin `git stash` (pedido del orquestador): RED se observó
  agregando primero la prueba nueva contra el código sin tocar --
  `.venv/Scripts/python.exe -m pytest -q tests/test_respuestas_nombran_tarea.py::test_titulo_ausente_sin_llamar_a_ninguna_herramienta_se_antepone`
  → **1 failed** (la respuesta salía sin la línea "Sobre «…»:", porque sin
  llamar a `consultar_tareas` la condición vieja nunca se cumplía). GREEN
  implementando la corrección con el mismo comando.
  - `src/leda/agente.py`: `responder` cambia `tareas_resueltas_claras` de
    `tuple[str, ...]` (sólo ids) a `dict[str, str]` (id de tarea → título);
    se eliminó por completo `tareas_consultadas` -- el parámetro nuevo de
    `_ejecutar_una`, el bloque que lo llenaba sólo para `consultar_tareas`, y
    su paso por el bucle de vueltas -- porque ya no hace falta: el título
    viaja en `tareas_resueltas_claras` mismo, no hay que reconstruirlo de lo
    que devolvió una herramienta. `_nombrar_tareas_sin_mencionar` queda con
    una sola entrada, sin el chequeo `or not tareas_consultadas` que antes
    apagaba la protección sin tool call.
  - `src/leda/gateway.py`: `_ReferenciasResueltas` gana
    `titulos_resueltas: dict[str, str]` (id de tarea → título, sólo las
    claras), calculado en `_resolver_referencias_del_turno` desde `por_id`
    (las tareas activas del espacio, ya cargadas para armar el bloque de
    sistema -- no hace falta una consulta nueva). `_estado_inicial_
    aclaracion` lo guarda en `estado["titulos_resueltas"]`; `_resolver_
    toque_aclaracion` lo actualiza también cuando la persona elige una
    candidata por botón (mismo patrón que ya usaba `estado["resueltas"]`,
    con el título que esa función ya tenía calculado para el texto del
    botón). Los dos lugares donde `_avanzar_aclaracion` llama a
    `agente.responder` pasan `tareas_resueltas_claras=estado["titulos_
    resueltas"]` en vez de `tuple(estado["resueltas"].values())`.
  - Capa de instrucción: la línea CLARA de `_bloque_contexto_referencias` y
    el bloque que arma `_resolver_toque_aclaracion` para una candidata
    elegida por botón suman ambas "Si contestás algo sobre ella, nombrala
    por su título exacto." -- antes sólo la primera lo tenía.
  - `tests/test_respuestas_nombran_tarea.py`: reescrito sobre el contrato
    nuevo (`tareas_resueltas_claras` como `dict[str, str]`). Prueba nueva
    `test_titulo_ausente_sin_llamar_a_ninguna_herramienta_se_antepone` (el
    modelo cierra con texto propio, sin ninguna llamada a herramienta,
    tarea resuelta sin nombrar → se antepone igual) y
    `test_titulo_ausente_con_una_herramienta_distinta_igual_se_antepone`
    (llama a `consultar_personas`, no a `consultar_tareas` → se antepone
    igual, prueba explícita de "no depende de qué herramienta corrió"). Las
    demás pruebas se adaptaron al contrato nuevo, conservando el mismo
    comportamiento cubierto: título presente con otra forma → sin tocar;
    sin `tareas_resueltas_claras` → sin tocar; herramienta de escritura con
    vista previa → sin tocar; dos tareas resueltas, una ausente → nombra
    sólo esa.
  - `tests/test_resolucion_referencias.py`: sin cambios sobre la revisión
    anterior -- la prueba de gateway completo
    (`test_referencia_clara_protege_la_respuesta_que_no_nombra_la_tarea`)
    sigue pasando tal cual, porque `estado["titulos_resueltas"]` reemplaza a
    `tuple(estado["resueltas"].values())` sin cambiar lo que esa prueba
    observa (el cuerpo del outbox).
  - Verificación pedida:
    `.venv/Scripts/python.exe -m pytest -q tests/test_respuestas_nombran_tarea.py
    tests/test_resolucion_referencias.py tests/test_aclaracion_botones.py
    tests/banco` → **157 passed, 90 deselected**.
    `.venv/Scripts/python.exe -m pytest -q` → **642 passed, 90 deselected**
    (641 + 1 neta -- el archivo de T5 pasó de 5 a 6 pruebas: se sacó una y
    entraron dos nuevas -- 0 regresiones, 147,54 s).
  - Sin commit (no pedido explícito todavía). Sin `.env*` tocado, sin modelo
    real, sin `git stash` en esta revisión.
  - **Commit de T5:** `3ed3956` ("feat: name the resolved task in every
    answer about it") -- faltaba registrarlo acá.
- 2026-09-24: **T6 (banco) en curso -- parte del banco cerrada, falta la
  documental.** Ruta: delegada, un escritor (T6 tiene su fila propia en
  "Ruta"; `tests/banco/`; la documentación -- `docs/capacidades.md`,
  `docs/STATUS.md`, diseño §4.5 -- la hace el orquestador aparte, sin
  tocarse en esta unidad). TDD estricto, cinco rondas (una por
  comportamiento), cada una con RED real antes de implementar:
  1. `Escenario.aclaracion_esperada` -- RED con
     `.venv/Scripts/python.exe -m pytest -q tests/banco/test_escenario.py -k aclaracion_esperada`
     → **6 failed** (el campo no existía: `AttributeError`/`DID NOT RAISE`).
     GREEN con el mismo comando → **6 passed**.
  2. `comprobadores.comprobar_aclaracion` -- RED con
     `.venv/Scripts/python.exe -m pytest -q tests/banco/test_comprobadores.py -k aclaracion`
     → **error de colección** (`ImportError: cannot import name
     'comprobar_aclaracion'`). GREEN con
     `.venv/Scripts/python.exe -m pytest -q tests/banco/test_comprobadores.py`
     → **71 passed**.
  3. `corrida.JevGrabador` / `jev_guionado_desde_grabacion` -- RED con
     `.venv/Scripts/python.exe -m pytest -q tests/banco/test_corrida.py -k jev_grab`
     → **error de colección** (`ImportError: cannot import name
     'JevGrabador'`). GREEN con el mismo comando → **3 passed**.
  4. `ejecutar_escenario` con `aclaracion_esperada` y grabación de Jev --
     RED con
     `.venv/Scripts/python.exe -m pytest -q tests/banco/test_corrida.py -k "aclaracion or jev_vacio"`
     → **3 failed** (`TypeError` por el kwarg nuevo, y
     `AttributeError: 'ResultadoCorrida' object has no attribute
     'etiquetas_aclaracion_ofrecidas'`). GREEN con
     `.venv/Scripts/python.exe -m pytest -q tests/banco/test_corrida.py`
     → **30 passed**.
  5. `conftest._cliente_jev_real_o_falla` / fixture `cliente_jev_real` --
     RED con
     `.venv/Scripts/python.exe -m pytest -q tests/banco/test_conftest.py`
     (archivo nuevo) → **error de colección** (`ImportError: cannot import
     name '_cliente_jev_real_o_falla'`). GREEN con el mismo comando →
     **2 passed**.
  - **Grabador de Jev (punto 1 del encargo).** `tests/banco/corrida.py`:
    `JevGrabador` (mismo patrón que `ProveedorGrabador`) envuelve cualquier
    `Jev` -- real o guionado -- y graba cada `(state, preguntas, respuesta)`
    en `pedidos`; nunca lleva la credencial, sólo lo que
    `jev.resolver_referencia_tarea` manda de verdad (mensaje, referencia,
    vocabulario del equipo, quién escribe) y lo que Jev responde.
    `ejecutar_escenario` ahora envuelve SIEMPRE lo que reciba en
    `cliente_jev` (real o el guionado vacío por defecto) en un
    `JevGrabador` -- mismo criterio que ya usa con `proveedor_real` -- y
    `ResultadoCorrida.grabacion` suma la clave `"jev"` con
    `JevGrabador.a_json()`. `jev_guionado_desde_grabacion(grabacion)`
    reconstruye un `ClienteJevGuionado` desde esa clave para el replay; una
    grabación de antes de T6 no la tiene y sigue cargando con guión vacío
    (nunca llama a Jev de verdad, lo mismo que si el escenario no hubiera
    traído ninguna referencia). `tests/banco/test_replays.py` arma ese
    guionado y lo pasa como `cliente_jev` -- el replay existente
    (`afirma-resolvio-sin-ejecutar-la-herramienta.json`, b-0003, sin
    `trabajos` en su ruta grabada) sigue pasando sin cambios, porque nunca
    llegó a llamar a Jev ni antes ni ahora.
  - **Jev real en el modelo real (punto 2).** `tests/banco/conftest.py`:
    `_cliente_jev_real_o_falla(config, *, desde_base=None)` (función pura,
    testeada con un `Config` fabricado, sin red) -- sin
    `LEDA_OPENROUTER_API_KEY` llama a `pytest.fail` con un mensaje que
    explica por qué (nunca degrada al guionado vacío, que haría que
    cualquier escenario con referencia termine preguntando siempre -- el
    defecto que esta unidad corrige, visible en vez de silencioso, como
    pide `AGENTS.md` para una guarda que falta). Con credencial, llama a
    `jev.desde_base(api_key)`. Fixture `cliente_jev_real` la usa con la
    `config` real. `tests/banco/test_banco.py::test_escenario_contra_modelo_real`
    ahora pide esa fixture y pasa `cliente_jev=cliente_jev_real` a
    `ejecutar_escenario` -- la suite por defecto sigue sin red (esa prueba
    lleva el marcador `modelo_real`, excluido por `addopts`).
  - **Botones de aclaración en el corredor (punto 3).** `Escenario` gana
    `aclaracion_esperada: dict` (vacío por defecto; si viene, valida
    `candidatas` -- lista no vacía de texto -- y `elegir` -- texto,
    tiene que ser una de `candidatas`). `ejecutar_escenario` gana el mismo
    parámetro: si viene, busca la `pending_action` de aclaración
    (`herramienta == gateway._SENTINEL_ACLARACION`, `estado='esperando'`) que
    el turno haya dejado, junta las etiquetas de sus opciones en
    `ResultadoCorrida.etiquetas_aclaracion_ofrecidas`, y si alguna etiqueta
    coincide con `elegir` la tapea -- por `gateway.procesar_update` con un
    `callback_query`, exactamente como ya hace con Confirmar (mismo
    `CALLBACK_PREFIJO`, mismo armado de `toque`). Si no aparece ninguna
    coincidencia, no tapea nada -- no adivina cuál tocar -- y la falta queda
    visible en las etiquetas grabadas para que
    `comprobadores.comprobar_aclaracion` (nueva; séptima comprobación,
    aprobado sólo si todas las `candidatas_esperadas` están entre las
    ofrecidas; una de más -- otro orden de Jev, o "Es una tarea nueva" --
    no es problema) la marque como falla en vez de bloquear la corrida.
    **Decisión de dónde tapear:** el paso de aclaración corre ANTES de
    capturar `herramientas_antes_del_toque`/`conteos_antes_del_toque` (el
    chequeo de "nada se aplica antes de Confirmar" de T4) -- así esa
    propiedad sigue valiendo con el paso nuevo en el medio, no sólo hasta
    la aclaración; lo prueba
    `test_ejecutar_escenario_aclaracion_tapea_la_candidata_elegida_sin_aplicar_nada`
    contra el circuito real (dos tareas propias ambiguas, Jev guionado,
    tapea la elegida, llega a la vista previa de `actualizar_estado` sin
    que ninguna de las 8 tablas cambie hasta el Confirmar real).
    `tests/banco/test_banco.py` y `tests/banco/test_replays.py` pasan
    `aclaracion_esperada=escenario.aclaracion_esperada or None` a
    `ejecutar_escenario` y agregan `comprobar_aclaracion` a la lista de
    comprobaciones cuando el escenario lo declara.
  - **Escenarios nuevos (punto 4), ids b-0013 a b-0015 (siguientes libres
    después de b-0012):**
    - `b-0013`: referencia ambigua entre dos tareas propias de Ariel De
      Simone ("Actualizar el dashboard de HMI" / "Revisar gráficos del
      dashboard HMI", área `corelabs`, para no repetir el dominio
      tablero/PLC de los escenarios existentes) -- `aclaracion_esperada`
      con las dos candidatas y `elegir` la primera; espera
      `actualizar_estado` sobre esa tarea. Deliberadamente NO reusa el
      mensaje de b-0008 (que es idéntico en texto y en tareas de
      precondición, pero verifica lo contrario: que Leda frene y
      pregunte en texto, sin tocar nada) -- son la misma ambigüedad
      probada de dos maneras: b-0008 se queda en la pregunta, b-0013 sigue
      la aclaración con botones hasta el final.
    - `b-0014`: "el tablero de la maq 5" -- una referencia parecida a dos
      tareas existentes (máquina 3 y 4) pero de una máquina que no está en
      el equipo; `debe_preguntar: true`, prohíbe las 8 herramientas que
      escriben y exige `conteos_delta` en cero (incluido `task_draft`):
      Jev tiene que resolver esto como "ninguna", no inventar una
      candidata de las que sí existen.
    - `b-0015`: dependencia entre dos tareas existentes de otra área (`it`,
      Martín Forte/Lucas Natuche, "migrar el servidor" bloqueando
      "actualizar los accesos VPN") -- mismo defecto que documenta
      `b-0005` en "Problema" de este mismo archivo (el enrutador tomaba un
      pedido de dependencia como alta de tarea nueva), verificado con un
      dominio y una redacción distintos, con `conteos_delta.task_draft: 0`
      explícito.
  - **Cambio de expectativa en escenarios existentes (revisión pedida por
    el encargo, "list every such change and why; never weaken a check"):**
    `b-0005.yaml`, `b-0005-a.yaml`, `b-0005-b.yaml` suman
    `efectos.conteos_delta.task_draft: 0` -- no reemplaza nada, sólo agrega
    una comprobación más estricta. Motivo: son justo los escenarios que
    "Problema" de este documento cita como el síntoma original del defecto
    de enrutamiento ("b-0005, 0 de 10"); hasta ahora sólo probaban la
    ausencia indirecta de las 8 herramientas que escriben, nunca que
    tampoco se hubiera abierto el alta guiada de tarea nueva -- el efecto
    concreto del defecto. El resto del corpus (b-0001 a b-0012) se revisó
    mensaje por mensaje: los que mencionan una tarea existente por
    descripción (b-0002 a b-0005, b-0008 a b-0012) siempre tuvieron sólo
    una tarea de la persona que encaja con lo que describen (o, en b-0008/
    b-0009, la ambigüedad ya es justo lo que se está probando con
    `debe_preguntar`), así que pasar de verdad por Jev no debería cambiar
    su resultado esperado -- no se tocó ninguna otra expectativa: no hay
    evidencia (no se corrió el banco real en esta unidad) de que alguna
    necesite ajustarse, y `AGENTS.md` pide no inventar hipótesis como
    hecho.
  - **Unidades nuevas (punto 5):** `tests/banco/test_escenario.py` (+6),
    `tests/banco/test_comprobadores.py` (+4), `tests/banco/test_corrida.py`
    (+6: 3 de `JevGrabador`/replay, 3 de `ejecutar_escenario` con
    aclaración), `tests/banco/test_conftest.py` (nuevo, 2) -- 18 pruebas
    nuevas, todas con dobles/fakes, sin red ni credencial real.
  - Verificación pedida:
    - `.venv/Scripts/python.exe -m pytest -q tests/banco` → **144 passed,
      99 deselected** (99 = 90 + 9: tres escenarios nuevos × `--banco-n 3`
      por defecto).
    - `.venv/Scripts/python.exe -m pytest -q` → **660 passed, 99
      deselected** (642 + 18 nuevas, 0 regresiones, 169,91 s).
    - `.venv/Scripts/python.exe -m pytest -m modelo_real --collect-only -q
      tests/banco` → **33/177 tests collected (144 deselected)**, con
      `b-0013-0`, `b-0014-0` y `b-0015-0` entre los recolectados (sólo
      colección, sin llamar al modelo).
  - **No se corrió el banco contra el modelo real** (pedido explícito del
    encargo). Comando sugerido para que el orquestador corra los
    escenarios nuevos y los que cambiaron de expectativa:
    `.venv/Scripts/python.exe -m pytest -m modelo_real tests/banco --banco-n 10 --banco-proveedor nan --banco-modelo deepseek-v4-flash --banco-escenario b-0013`
    (repetir con `b-0014`, `b-0015`, `b-0005`, `b-0005-a`, `b-0005-b`; sin
    `--banco-escenario` corre todo el corpus). Requiere
    `LEDA_OPENROUTER_API_KEY` configurada -- sin ella, `cliente_jev_real`
    hace fallar la corrida con un mensaje claro en vez de dejarla preguntar
    siempre.
  - No se tocó `docs/` (documentación de T6 es tarea aparte del
    orquestador). No hubo commit (no pedido explícito todavía). No se leyó
    ni se tocó ningún `.env*`.
- 2026-09-24 (orquestador): **primera corrida del banco real con Jev** (NaN
  `deepseek-v4-flash` + Jev real, 33 escenarios x 3, base descartable de pruebas):
  `.venv/Scripts/python.exe -m pytest -m modelo_real tests/banco --banco-proveedor nan
  --banco-modelo deepseek-v4-flash -q` → 41 failed, 58 passed. Causas observadas en
  las grabaciones (`tests/banco/reportes/replay-candidato-*.json`, sin versionar):
  (A) el enrutador separa como trabajos cosas que no lo son: estados ("revisión"),
  causas ("el plano que prometieron", "el switch que faltaba") o partes de la misma
  referencia ("el tablero"); cada una termina en botones o en una pregunta aunque la
  tarea principal quedó clara (b-0002, b-0003, b-0004, b-0005-b). (B) El bloque de
  "ninguna" le ordena al modelo preguntar aunque el resto del mensaje sea claro. (C)
  Una referencia genérica ("algo pendiente esta semana") abre botones en vez de
  responder sobre todas (b-0001-b). (D) El modelo pide confirmación con texto en vez
  de llamar a la herramienta que arma la vista previa, y en un caso afirmó "quedó
  registrado" sin haber registrado nada (b-0008, b-0013); no se había corrido el banco
  real después de la unidad de vista previa. (E) Jev eligió claro "lo del tablero" y
  "lo del dashboard" donde el escenario espera duda (b-0008, b-0013); la vista previa
  lo frena. (F) b-0015: el modelo registró un bloqueo en vez de una dependencia. T6
  queda abierta hasta corregir y volver a correr.
- 2026-09-24: **T7 cerrada (A-D).** Ruta: delegada, un escritor (T7 no tiene fila
  propia en "Ruta" -- se agrega acá: `src/leda/llm.py`, `src/leda/jev.py`,
  `src/leda/gateway.py`, `src/leda/contexto.py`, pruebas en
  `tests/test_llm_protocol.py`, `tests/test_jev.py`,
  `tests/test_resolucion_referencias.py`, `tests/test_aclaracion_botones.py`,
  `tests/test_agente.py`, `tests/banco/test_corrida.py`). No se tocó `docs/`
  (pedido explícito del encargo) ni ningún `.env*`. Postgres local verificado con
  `pg_isready` antes de empezar. TDD estricto, RED real antes de cada
  comportamiento (A1, A2+C juntos por la dependencia del enum, B, D):
  1. **A1 (enrutador).** RED con
     `.venv/Scripts/python.exe -m pytest -q tests/test_llm_protocol.py -k router_system_excludes`
     → **1 failed**. GREEN con
     `.venv/Scripts/python.exe -m pytest -q tests/test_llm_protocol.py` → **104
     passed**.
  2. **A2 + C (dedupe y "varias tareas").** RED en dos pasos: `test_jev.py -k varias`
     → **1 failed** (`AttributeError: type object 'TipoResolucion' has no
     attribute 'VARIAS'`); después de agregar el enum, `test_resolucion_referencias.py`
     completo → **4 failed** (varias-tareas sin botones, dedupe con clara, dedupe
     seguro -- este último ya pasaba sin código nuevo, correctamente, porque sin
     dedupe nunca se descarta nada -- y la reescritura de "ninguna" del punto B).
     GREEN con
     `.venv/Scripts/python.exe -m pytest -q tests/test_resolucion_referencias.py tests/test_aclaracion_botones.py tests/test_jev.py`
     → **61 passed**.
  3. **B (ninguna).** Cubierto por el mismo ciclo RED/GREEN del punto anterior
     (dos aserciones nuevas en la prueba existente del horno más una prueba
     nueva de mensaje mixto).
  4. **D (preámbulo).** RED con
     `.venv/Scripts/python.exe -m pytest -q tests/test_agente.py -k test_contexto_lleva_nucleo_glosario_y_equipo`
     → **1 failed**. GREEN con
     `.venv/Scripts/python.exe -m pytest -q tests/test_agente.py tests/test_personas.py`
     → **26 passed**.
  - Verificación pedida:
    `.venv/Scripts/python.exe -m pytest -q tests/test_resolucion_referencias.py tests/test_aclaracion_botones.py tests/test_llm_protocol.py tests/test_respuestas_nombran_tarea.py tests/banco`
    → **283 passed, 99 deselected**.
    `.venv/Scripts/python.exe -m pytest -q` → **665 passed, 99 deselected** (660 +
    5 netas -- test_llm_protocol.py +1, test_resolucion_referencias.py +4; el resto
    de los archivos tocados sólo reescribió pruebas existentes o ajustó fixtures --
    0 regresiones, 200,52 s).
  - **A1 -- `llm.ROUTER_SYSTEM` (`src/leda/llm.py`):** una sola oración nueva,
    en el mismo párrafo medido en T2, sin tocar el resto: "no separes un estado
    (\"revisión\", \"terminado\"), una causa o algo que falta (\"el plano que
    prometieron\", \"el switch que faltaba\"), ni una segunda mención de la
    misma referencia." -- toma las palabras textuales de las causas A que
    anotó el orquestador sobre el banco real.
  - **A2 -- dedupe determinístico (`gateway._resolver_referencias_del_turno`):**
    después de calcular `resueltas_claras`, una referencia cuyo `resolucion.tipo
    is AMBIGUA` con `candidatas` no vacías, y cuyas candidatas son subconjunto de
    `set(resueltas_claras.values())`, se saca de `resultados` antes de calcular
    `con_botones`/`sin_boton`/`pendientes_boton` -- no entra ni como botón ni
    como línea del bloque de texto. Nunca toca `AMBIGUA` sin candidatas, `VARIAS`,
    `NINGUNA` ni los `JevError` (Jev caído nunca expone candidatas, así que no hay
    nada que comparar). La auditoría (`_auditar_resolucion`) sigue corriendo
    sobre `resultados` completo, sin dedupe -- registra lo que Jev respondió de
    verdad, no lo que se terminó preguntando.
  - **C -- `TipoResolucion.VARIAS` (`src/leda/jev.py`):** el alcance
    "varias_tareas" (un área, lo de una persona, algo genérico) ahora devuelve
    `ResolucionReferencia(TipoResolucion.VARIAS, candidatas=...)` en vez de
    `AMBIGUA` -- son conceptualmente distintos (abarca varias tareas de verdad,
    contra "es una sola tarea pero no sé cuál") y sólo el segundo abre botones
    (T4). `gateway._bloque_contexto_referencias` gana la rama `VARIAS`: con
    candidatas, lista las tareas y pide responder sobre todas si consultan o
    preguntar cuál (en texto) si piden un cambio; sin candidatas, pide no
    inventar. `con_botones` en `_resolver_referencias_del_turno` sigue
    comprobando sólo `AMBIGUA`, así que `VARIAS` queda afuera sin tocar esa
    línea.
  - **Blast radius de C, mayor al previsto: 15 sitios de prueba usaban
    `varias_tareas` sólo como gatillo de "ambigua con candidatas" (nunca para
    probar el alcance "varias" en sí).** Antes de esta unidad, todo T4
    (`tests/test_aclaracion_botones.py`, 13 sitios) y una prueba de T3/T4
    (`tests/test_resolucion_referencias.py::test_referencia_ambigua_sin_candidatas_pregunta_en_texto`)
    simulaban la ambigüedad de una sola tarea con el alcance equivocado
    ("varias_tareas" en vez de "una_tarea"); con la corrección de C esos
    escenarios dejarían de abrir botones, que es justo lo que esas pruebas
    verifican. Se cambió el disparador (`_alcance(varias_tareas=0.7)` →
    `_alcance(una_tarea=0.8)`, mecánico, mismas probabilidades de "tarea") en
    los 13 sitios de `test_aclaracion_botones.py`, en el sitio de
    `test_resolucion_referencias.py`, y en el dict crudo equivalente de
    `tests/banco/test_corrida.py::test_ejecutar_escenario_aclaracion_tapea_la_candidata_elegida_sin_aplicar_nada`.
    Se agregó una prueba nueva y propia para el alcance "varias" real
    (`test_referencia_varias_tareas_no_abre_botones_y_llega_como_contexto`,
    con el pedido genérico "algo pendiente esta semana" del hallazgo C del
    banco real) y se renombró/ajustó la prueba unitaria de `jev.py`
    (`test_resolver_referencia_varias_da_ambigua_con_candidatas_ordenadas` →
    `..._da_varias_con_candidatas_ordenadas`, tipo esperado `VARIAS`). Ninguna
    prueba perdió cobertura: siguen verificando exactamente lo mismo (botones
    para ambigüedad real de una tarea), sólo con el alcance correcto.
  - **Doble de Jev nuevo para pruebas con más de una referencia
    (`tests/test_resolucion_referencias.py::_JevPorReferencia`):**
    `_resolver_en_paralelo` corre las referencias de un mismo turno en un
    `ThreadPoolExecutor`, así que el orden real de las llamadas a la red no es
    determinístico; el guión FIFO único de `ClienteJevGuionado` alcanza cuando
    todas las referencias necesitan la misma forma de respuesta (como ya hacía
    T4), pero no sirve para un escenario con dos referencias que necesitan
    cantidades de llamadas distintas (p. ej. una CLARA con verificación, dos
    llamadas, y otra ambigua, una sola) -- las pruebas nuevas de A2 y B lo
    necesitaban. `_JevPorReferencia` responde según `state["referencia"]`
    (presente en las dos llamadas de `resolver_referencia_tarea`), no según el
    orden global de llamadas, así que cada referencia consume su propia cola
    sin importar qué hilo la ejecuta primero.
  - **B -- "ninguna" (`gateway._bloque_contexto_referencias`):** la rama
    `NINGUNA` cambia "No inventes una tarea para eso: preguntá." (orden
    incondicional) por "No es una tarea: no la inventes ni la trates como una.
    Si hace falta para responder o actuar y no tenés otra cosa clara para usar,
    preguntá." -- condicional, en vez de mandato. Se conservó la frase
    "no coincide con ninguna tarea activa del espacio" tal cual (la prueba del
    horno la usaba como ancla) y se sumaron dos aserciones a esa misma prueba
    más una prueba nueva de mensaje mixto (una referencia CLARA y otra
    NINGUNA en el mismo turno) que comprueba la ausencia de la frase vieja.
    Es un cambio puramente de redacción del bloque de sistema -- no hay lógica
    nueva que decida "preguntar o no" según lo demás resuelto en el turno; es
    el modelo el que ahora lee una instrucción condicional en vez de una
    orden.
  - **D -- preámbulo (`src/leda/contexto.py`, `PREAMBULO`):** la viñeta que
    sólo cubría la creación de una tarea ("La creación de una tarea se resuelve
    antes de este turno...") se reemplaza por una general: "Para cambiar algo
    -- crear, actualizar, asignar, cerrar, lo que sea -- llamá a la herramienta
    correspondiente: el servidor arma la vista previa con Confirmar, Modificar
    y Cancelar. Nunca pidas confirmación en texto ni digas que algo quedó
    registrado, creado o cambiado si no llamaste a esa herramienta." Cubre
    directamente las causas D del banco real (pedir confirmación en texto, y
    afirmar "quedó registrado" sin tool call en b-0008/b-0013). El vocabulario
    "vista previa con Confirmar, Modificar y Cancelar" no es nuevo: coincide
    con `docs/architecture/interpretacion-y-confirmacion.md` (§"Al elegir una
    propuesta"), sólo se lo mueve al preámbulo para que valga siempre, no sólo
    para la creación de tareas.
  - **Efecto secundario de D, corregido en la prueba correspondiente:**
    `tests/test_aclaracion_botones.py::test_ninguna_dentro_de_la_ventana_el_siguiente_mensaje_usa_el_original`
    comprobaba `"Modificar" not in sistema` para probar que el bloque propio de
    `_resumir_aclaracion_ninguna` no se confunde con una corrección real de
    Modificar (`agente._bloque_modificacion`); como el preámbulo ahora nombra
    los tres botones por su nombre en todo turno, esa palabra sola dejó de
    alcanzar. Se angostó la aserción al marcador real que
    `_bloque_modificacion` usa y que este camino evita a propósito ("#
    Corrección a una propuesta anterior", "apretó Modificar") -- mismo
    chequeo, ya no falso positivo por el preámbulo.
  - **nucleo/ revisado, sin conflicto y sin tocar** (pedido del encargo):
    `nucleo/constitucion.md` §7 ("Leda prepara un borrador, pide confirmación
    y sólo entonces ejecuta...") y `nucleo/mecanica-pm.md` §12 ("Un mensaje que
    requiere confirmación humana espera en la cola...") describen la
    obligación de confirmar a nivel de negocio, sin fijar el medio (texto vs.
    botones) -- compatibles con el mecanismo de vista previa con botones que ya
    implementa `PREAMBULO`/`herramientas.NecesitaConfirmacion` desde antes de
    esta unidad. No instruyen al modelo a pedir confirmación en texto en
    ningún punto; no hubo que reportar conflicto.
  - **Pendiente, del orquestador, no de este escritor:** volver a medir la
    separación de referencias sobre los 60 mensajes y correr el banco real
    completo (T7 lo pide explícitamente); T6 sigue abierta hasta esa corrida.
  - No hubo commit (no pedido explícito todavía).
- 2026-09-24 (orquestador): **A1 revertida.** Motivo: medición propia del
  orquestador con el enrutador real sobre los 60 mensajes -- la instrucción de
  A1 (excluir estados/causas/segunda mención del párrafo de T2) mejoraba la
  separación en algunos casos pero perdía tareas reales: 55 de 60 iguales a la
  extracción separada, contra 57 de 60 con la redacción medida en T2 sin tocar;
  el caso concreto perdido fue "el switch" en "El switch ya se cambio ahora
  queda el tablero de la 4". `src/leda/llm.py`: `ROUTER_SYSTEM` vuelve a la
  redacción exacta de T2 (revierte la oración agregada por A1). `tests/
  test_llm_protocol.py`: `test_router_system_excludes_states_causes_and_
  repeated_mentions` (A1) se reemplaza por `test_router_system_keeps_the_
  measured_reference_wording`, que fija la redacción de T2 como guarda para
  que no se vuelva a tocar por accidente. Las referencias que sobran (estados,
  causas, segundas menciones) las descarta el código, no el modelo -- A2 (T7)
  ya cubre el caso de "revisión"/estados repetidos por dedupe; E (segunda
  ronda, más abajo) cubre el caso de una referencia que es sólo un estado.
- 2026-09-24: **T7, segunda ronda (E, G, H, I) cerrada.** Motivo: segunda
  corrida del banco real (77 passed, 22 failed) tras la primera tanda de
  arreglos. Ruta: delegada, un escritor (misma fila de T7 en "Ruta", se
  extiende a `src/leda/gateway.py`, `src/leda/jev.py`,
  `tests/banco/comprobadores.py`, pruebas en `tests/test_resolucion_
  referencias.py`, `tests/test_aclaracion_botones.py`, `tests/test_jev.py`,
  `tests/banco/test_comprobadores.py`). No se tocó `docs/` ni `nucleo/`
  (pedido explícito), ni ningún `.env*`. `pg_isready` verificado antes de
  empezar. TDD estricto, RED real antes de cada punto, dobles/fakes
  solamente, sin modelo ni Jev real, sin commit/stage/stash:
  1. **E (referencias de sólo estado).** RED con
     `.venv/Scripts/python.exe -m pytest -q tests/test_resolucion_referencias.py -k "solo_estado or referencia_de_estado"`
     → **16 failed, 1 passed** (la única que pasaba de entrada,
     `test_referencia_de_estado_no_confunde_una_referencia_real`, confirmaba
     que "el switch" -- causa, no estado -- seguía yendo a Jev sin tocar
     nada). GREEN con
     `.venv/Scripts/python.exe -m pytest -q tests/test_resolucion_referencias.py`
     → **31 passed**.
  2. **G (regresión de C).** RED con
     `.venv/Scripts/python.exe -m pytest -q tests/test_aclaracion_botones.py -k varias_pregunta`
     → **1 failed** (`TypeError: 'NoneType' object is not subscriptable` --
     nunca se abrió la `pending_action` de aclaración: el alta guiada
     arrancaba sola). GREEN con el mismo comando → **1 passed**.
  3. **H (bloqueos en el criterio).** RED en dos pasos: unitario primero --
     `.venv/Scripts/python.exe -m pytest -q tests/test_jev.py -k criterio` →
     **4 failed, 1 passed** (`TypeError: TareaCandidata.__init__() got an
     unexpected keyword argument 'causas_bloqueo'`; la única que pasaba,
     `test_criterio_sin_bloqueos_no_cambia`, no necesitaba código nuevo) --
     GREEN con el mismo comando → **5 passed**. Después, extremo a extremo --
     `.venv/Scripts/python.exe -m pytest -q tests/test_resolucion_referencias.py -k bloqueo`
     → **2 failed, 2 passed** (las dos negativas, sin bloqueo y bloqueo ya
     resuelto, ya pasaban sin tocar `_tareas_activas`) -- GREEN con el mismo
     comando → **4 passed**.
  4. **I (comprobador del banco).** RED con
     `.venv/Scripts/python.exe -m pytest -q tests/banco/test_comprobadores.py -k imperativo`
     → **5 failed, 3 passed** (las tres negativas/de orden -- "decime si
     necesitás algo más" con y sin herramienta, y el imperativo con
     herramienta que escribe -- ya pasaban con el código de antes, como tenía
     que ser). GREEN con
     `.venv/Scripts/python.exe -m pytest -q tests/banco/test_comprobadores.py`
     → **79 passed**.
  - Verificación pedida:
    `.venv/Scripts/python.exe -m pytest -q tests/test_resolucion_referencias.py tests/test_aclaracion_botones.py tests/test_jev.py tests/test_llm_protocol.py tests/banco`
    → **344 passed, 99 deselected**.
    `.venv/Scripts/python.exe -m pytest -q` → **700 passed, 99 deselected**
    (665 + 35 nuevas -- E 17 (16 con estados parametrizados + 2 sueltas, una
    ya contada en el RED como pasando de entrada), G 1, H 9 (5 unitarias de
    `criterio()` + 4 de `_tareas_activas`), I 8 -- 0 regresiones, 159,94 s).
  - **E -- `gateway.ESTADOS_REFERENCIA_SOLA`/`_es_referencia_de_estado`:**
    vocabulario cerrado a partir de `estado_tarea` (`db/esquema.sql`:
    'propuesta', 'pendiente_aprobacion', 'asignada', 'en_curso', 'bloqueada',
    'en_revision', 'terminada', 'cancelada') más sus formas humanas dadas por
    el encargo (revisión/revision, en revisión, terminado/terminada, listo,
    hecho, en curso, bloqueado/bloqueada, pendiente, resuelto, cancelado) con
    sus pares de género obvios (lista, hecha, resuelta) -- nunca frases de un
    escenario del banco, como pedía el encargo. `_normalizar_referencia_
    estado` (minúsculas, sin acentos, recorta un artículo/preposición líder
    de `("a","la","el","en")`) reduce "en revisión"/"en curso" a
    "revision"/"curso" -- por eso el vocabulario lleva "curso" y "revision"
    sueltos, no las frases con "en". `_resolver_referencias_del_turno`
    descarta esas referencias de `route.trabajos` ANTES de pedir la
    credencial o tocar la base -- si no queda ninguna, se comporta exactamente
    como "sin referencias" (`None`, sin bloque, sin auditoría). El resto de la
    función (crédito ausente, dedupe A2, botones) sigue usando la lista ya
    filtrada (`trabajos`), no `route.trabajos`.
  - **G -- `_resolver_referencias_del_turno`, `con_botones`:** cuando
    `route.action is IntentAction.START_TASK_INTAKE` y nada quedó CLARA
    (`hay_clara` falso), una referencia VARIAS con candidatas también entra a
    `con_botones` -- fuera de ese caso (consulta normal), sigue sin abrir
    botón nunca, como fija C. Con eso ya alcanza: `_avanzar_aclaracion`
    pregunta antes que nada si `estado["pendientes"]` no está vacío (T4),
    así que el b-0005 mixto (alta silenciosa) queda cubierto sin tocar esa
    función; `_preguntar_por_botones` ya agregaba "Es una tarea nueva" y
    "Ninguna, lo escribo" para cualquier pendiente con el enrutador pidiendo
    alta, así que tampoco hizo falta tocarla -- las candidatas de VARIAS
    llegan ya recortadas a >= 0,1 por `jev.resolver_referencia_tarea`
    (`candidatas_por_umbral`), y `_candidatas_para_botones` las ordena
    propias primero sin cambios. **Alcance deliberado, no evidenciado más
    allá:** no se tocó el caso VARIAS/AMBIGUA sin ninguna candidata mezclado
    con alta de tarea (sigue arrancando el alta sola, como ya hacía AMBIGUA
    sin candidatas antes de esta unidad) -- el encargo y la evidencia
    (b-0009) hablan de candidatas reales, no inventé un caso sin evidencia.
  - **H -- `jev.TareaCandidata.causas_bloqueo` + `criterio()`:** campo nuevo
    (`str | None`, default `None`); `criterio()` agrega
    " — bloqueada: <causas>" sólo si hay valor, acotado a
    `MAX_LONGITUD_CAUSAS_BLOQUEO = 200` con "…" (`_acotar`, nuevo, module-
    level). Como la verificación ya arma su `state` con
    `top_tarea.criterio()`, un solo punto de cambio alcanza para las dos
    llamadas (probado de punta a punta en `test_criterio_de_verificacion_
    tambien_lleva_el_bloqueo`). `gateway._tareas_activas`: la consulta suma
    una subconsulta (`string_agg(b.causa, '; ' order by b.abierto_en)` desde
    `blocker` donde `resuelto_en is null`, agrupada por tarea vía subquery
    correlacionada) bajo el mismo cursor con RLS que ya tenía -- sin conexión
    ni consulta aparte. Varios bloqueos abiertos se unen con "; "; uno
    resuelto no cuenta.
  - **I -- `comprobadores._pide_elegir_en_imperativo`:** lista chica y
    cerrada (`_VERBOS_PEDIDO_ELECCION = ("decime", "decinos", "contame",
    "confirmame")`) que sólo cuenta como pedido de elección junto con la
    palabra "cual" (normalizada, sin tilde) en el mismo texto -- "elegí" es la
    única excepción, alcanza sola porque el verbo ya es la acción de elegir.
    Ese diseño es justamente lo que separa "decime cuál doy por resuelto"
    (aprueba) de "decime si necesitás algo más" (no aprueba): las dos
    empiezan con "decime", sólo la primera tiene "cuál". `comprobar_pregunta`
    suma esta condición al `or` que ya tenía ("?" / `ofrecio_opciones`) --
    **nunca antes** del corte por `escribio`, que sigue evaluándose primero y
    solo, así que "actuó sin preguntar" no se debilita (probado en
    `test_pregunta_imperativo_con_herramienta_que_escribe_sigue_fallando`,
    mismo texto que aprueba solo, pero con una herramienta que escribe
    ejecutada -- sigue siendo `falla`).
  - No hubo commit (no pedido explícito todavía); no se leyó ni se tocó
    ningún `.env*`; `docs/` y `nucleo/` sin tocar en esta unidad.
- 2026-09-24: **T7, tercera ronda (J, K, L) cerrada.** Motivo: tercera corrida
  del banco real (84 passed, 15 failed) tras la segunda tanda de arreglos.
  Ruta: delegada, un escritor (misma fila de T7 en "Ruta", se extiende a
  `src/leda/herramientas.py`, `src/leda/jev.py`, pruebas en
  `tests/test_agente.py`, `tests/test_jev.py`). No se tocó `docs/` (el
  orquestador ya había sumado el diseño §5.11) ni `nucleo/` -- se lo leyó
  para K, ver más abajo -- ni ningún `.env*`. `pg_isready` verificado antes de
  empezar. TDD estricto, RED real antes de cada punto, dobles/fakes
  solamente, sin modelo ni Jev real, sin commit/stage/stash:
  1. **J (argumentos inválidos).** RED con
     `.venv/Scripts/python.exe -m pytest -q tests/test_agente.py -k argumento`
     → **3 failed, 1 passed** (la que pasaba de entrada,
     `test_argumentos_correctos_no_se_ven_afectados`, confirmaba que una
     llamada válida no cambiaba; las otras tres mostraban el `TypeError` sin
     atrapar -- `_preparar_registrar_bloqueo() missing 1 required positional
     argument: 'causa'` -- y el turno completo cayendo a incidente/disculpa).
     GREEN con `.venv/Scripts/python.exe -m pytest -q tests/test_agente.py`
     → **17 passed**.
  2. **K (bloqueo vs. dependencia).** RED con
     `.venv/Scripts/python.exe -m pytest -q tests/test_agente.py -k descripcion_de`
     → **2 failed**. GREEN con el mismo comando → **2 passed**.
  3. **L (subcampeona/rival).** RED con
     `.venv/Scripts/python.exe -m pytest -q tests/test_jev.py -k "rival or subcampeona"`
     → **7 failed, 2 passed** (las dos que pasaban de entrada -- candidata
     débil y una sola tarea -- confirmaban que el comportamiento de siempre
     seguía igual sin subcampeona real, antes de tocar nada). GREEN con
     `.venv/Scripts/python.exe -m pytest -q tests/test_jev.py` → **46 passed**.
  - Verificación pedida:
    `.venv/Scripts/python.exe -m pytest -q tests/test_jev.py tests/test_agente.py tests/test_resolucion_referencias.py tests/test_aclaracion_botones.py tests/banco`
    → **268 passed, 99 deselected**.
    `.venv/Scripts/python.exe -m pytest -q` → **715 passed, 99 deselected**
    (700 + 15 nuevas -- J 4, K 2, L 9 -- 0 regresiones, 162,79 s).
  - **J -- `herramientas._validar_argumentos` + `ejecutar`:** un punto único
    de validación, antes de `preparar`/`handler`, contra `h.parametros` (la
    misma fuente que ya arma `esquemas()` para el modelo) -- cubre las dos
    rutas de llamada de una sola vez. Chequea sólo nombres: argumentos que el
    modelo mandó y la herramienta no declara ("no reconocidos"), y
    argumentos `requerido: True` que faltan ("faltan") -- no valida tipos,
    la evidencia (b-0002) es de un parámetro inexistente, no de un tipo mal
    puesto. **Decisión: validar antes de llamar, no atrapar `TypeError`
    genérico** (la alternativa que ofrecía el encargo) -- atrapar `TypeError`
    en `agente._ejecutar_una` también taparía un bug real dentro de un
    handler que por su cuenta levante un `TypeError` no relacionado con
    argumentos, mientras que la validación previa sólo dispara para el fallo
    exacto que pide J. **Decisión: reusar `Denegado`, no una excepción
    nueva, y sin incidente.** `agente._ejecutar_una` ya atrapa `Denegado` y
    lo devuelve como `tool_result` de error sin incidente (`except Denegado
    as e: return bloque({"permitido": False, "explicacion": str(e)},
    error=True)`) -- el mismo camino que ya usaba "No existe la
    herramienta", un error de modelo estructuralmente igual (llamó algo que
    no existe/no encaja) al de un argumento inválido; no hizo falta tocar
    `agente.py` en absoluto. El mensaje empieza con "argumentos no válidos
    para '<herramienta>' (...)" y termina listando los parámetros aceptados,
    sin ningún detalle técnico (nombre de excepción, traceback). **No se
    agregó `tarea_id` a `consultar_tareas`**: el pedido explícito era no
    hacerlo salvo que fuera la opción más limpia, y no lo es -- el problema
    es genérico (cualquier herramienta, cualquier argumento inventado), no
    algo que un parámetro nuevo en una sola herramienta resuelva.
  - **K -- descripciones de `registrar_bloqueo`/`crear_dependencia`:**
    `nucleo/mecanica-pm.md` §4 ("Dependencias") define la dependencia
    explícitamente entre dos tareas: "Una dependencia relaciona dos tareas y
    tiene un tipo: **bloqueante** — la tarea destino no puede pasar a
    `en_curso` hasta que la origen esté `terminada`." El bloqueo (§8) nunca
    se describe así -- es "causa, impacto y fecha", con pasos de gestión
    (proponer soluciones, preguntar si otro integrante puede ayudar,
    escalar) que sólo tienen sentido para algo fuera del control directo del
    equipo; `constitucion.md` §6 ya decía que ante un bloqueo Leda "no
    intenta resolver técnicamente... actuando sobre los sistemas", coherente
    con una causa externa. Ninguna sección usa la frase "causa externa"
    textualmente -- la redacción de las dos herramientas es una síntesis de
    lo que §4 y §8 ya distinguen, no una cita literal. `nucleo/` se leyó,
    no se tocó. Descripciones nuevas: `registrar_bloqueo` -- "Registra que
    una tarea está trabada por una causa externa al equipo -- algo que
    falta, una persona fuera del equipo, un permiso -- con su causa e
    impacto. Si lo que la frena es otra tarea del equipo, no es un bloqueo:
    usá crear_dependencia."; `crear_dependencia` -- "Declara que una tarea
    depende de otra tarea del equipo -- es lo que corresponde cuando lo que
    frena una tarea es otra tarea, no una causa externa (eso es
    registrar_bloqueo). 'bloqueante' frena..." (resto sin cambios). Cada una
    nombra a la otra, para que el modelo la encuentre esté evaluando
    cualquiera de las dos. **No hizo falta una línea en el contexto de
    confianza** (la alternativa que ofrecía el encargo): la elección de
    herramienta es responsabilidad de la descripción de la herramienta, no
    del preámbulo general -- mismo criterio que ya separa "qué hace cada
    herramienta" (`herramientas.py`) de "reglas de comportamiento general"
    (`contexto.PREAMBULO`).
  - **L -- subcampeona/rival (`jev.resolver_referencia_tarea`):**
    `INSTRUCCION_RIVAL` y `CORTE_RIVAL = 0.5` (constantes nuevas). Cuando la
    receta iba a decidir clara, si `ordenadas` tiene una segunda entrada con
    probabilidad `>= CORTE_CANDIDATA` (el mismo corte que ya separa una
    candidata real de ruido en el resto de la receta -- **decisión de esta
    unidad**, no dicha explícitamente por el encargo: una segunda
    probabilidad ínfima, como las de 0.05 que ya usaban las pruebas de T1,
    no es una subcampeona de verdad y no debía sumar la pregunta), se agrega
    "rival" a las `preguntas` de la MISMA llamada de verificación (nunca una
    llamada aparte) y `tarea_elegida`/`otra_tarea` (`criterio()`, con el
    sufijo de bloqueo de H si corresponde) al `state` -- **sólo cuando hay
    subcampeona**; el campo `tarea` que ya usaba "misma" no se tocó, para no
    romper lo que ya dependía de él (T7 H, `test_criterio_de_
    verificacion_tambien_lleva_el_bloqueo`). Si "misma" no alcanza el corte
    de siempre, sigue exactamente igual que antes (ambigua con sólo la
    elegida, sin mirar "rival" -- semántica de la verificación sin tocar,
    como pedía el encargo). Si "misma" pasa y hay subcampeona, "rival" >=
    `CORTE_RIVAL` baja a ambigua con `[elegida, subcampeona]`; si no hay
    subcampeona, o "rival" queda debajo del corte, sigue clara -- el
    comportamiento de siempre. "Rival" malformado (falta, sin `noul`, no
    numérico, no es un objeto) lanza `JevError` con `_extraer_noul`, la
    misma función que ya validaba "misma" -- sin código nuevo de validación.
  - No hubo commit (no pedido explícito todavía); no se leyó ni se tocó
    ningún `.env*`; `docs/` y `nucleo/` sin tocar (nucleo/ leído para K,
    citado arriba, nunca editado).
- 2026-09-24 (orquestador): **revisión de L y corrección -- se saca el corte
  por `CORTE_CANDIDATA` en la subcampeona.** Motivo: ese corte (decisión de
  esta unidad, no pedida por el encargo original) dejaba afuera justo el caso
  que §5.11 midió -- b-0013, Jev devolvió 0,91 / 0,09 para las dos tareas del
  dashboard, y 0,09 queda por debajo de `CORTE_CANDIDATA` (0,1) -- así que
  "rival" nunca se preguntaba y la referencia se resolvía sola. El diseño
  medido (PoC de scratchpad y §5.11) pregunta por la segunda más probable
  siempre que Jev haya devuelto al menos dos, sin condicionarlo a su
  probabilidad. TDD estricto, mismas reglas (sin commit, sin `.env*`, sin
  llamadas reales): RED con
  `.venv/Scripts/python.exe -m pytest -q tests/test_jev.py -k "b0013 or rival_baja_probabilidad"`
  → **2 failed** (una prueba nueva con 0,91/0,09 esperando ambigua seguía
  dando clara; otra esperando que "rival" viajara igual con una subcampeona
  débil no lo encontraba en la llamada). GREEN sacando el corte en
  `src/leda/jev.py` (`if len(ordenadas) > 1:` en vez de `if len(ordenadas) >
  1 and ordenadas[1][1] >= CORTE_CANDIDATA:`) con el mismo comando → **2
  passed**.
  - `tests/test_jev.py`: prueba nueva
    `test_resolver_referencia_rival_baja_probabilidad_igual_pide_y_puede_ambiguar_b0013`
    (0,91/0,09 tal como lo midió §5.11, respuesta de "rival" alta → ambigua
    con las dos). La prueba que fijaba el corte viejo
    (`test_resolver_referencia_candidata_debil_no_cuenta_como_rival`, que
    afirmaba que una subcampeona débil NO sumaba "rival") se reemplaza por
    `test_resolver_referencia_rival_baja_probabilidad_se_pide_y_puede_seguir_
    clara`, que prueba lo contrario correcto: se pregunta igual, y una
    respuesta baja de "rival" (0,1) es lo que mantiene la referencia clara --
    tal como pedía la revisión ("adapta las pruebas de clara que usaban un
    0,05 de relleno scripteando una respuesta baja de rival"). Se adaptaron
    las otras cuatro pruebas de clara que tenían una segunda probabilidad
    (0,05) sin "rival" en el guión de verificación --
    `test_resolver_referencia_clara_llama_verificacion_y_confirma`,
    `test_resolver_referencia_usa_claves_cortas_para_las_opciones_de_jev`,
    `test_quien_escribe_viaja_en_el_state_de_las_dos_llamadas_cuando_se_pasa`,
    `test_sin_quien_escribe_no_agrega_el_campo_ni_cambia_las_instrucciones` --
    sumando `"rival": {"noul": 0.1}` a su respuesta de verificación; el
    resultado esperado (clara) no cambió en ninguna. Se auditaron a mano
    todas las demás respuestas de verificación de una sola "misma" en
    `tests/test_jev.py`, `tests/test_resolucion_referencias.py`,
    `tests/test_aclaracion_botones.py` y `tests/banco/test_corrida.py`: el
    resto usa `tarea` con una sola clave (sin segunda probabilidad, nunca
    hay subcampeona) o falla antes de llegar a "rival" porque "misma" ya es
    baja o está malformada (`test_resolver_referencia_verificacion_baja_pasa_
    a_ambigua_con_esa_tarea`, `test_resolver_referencia_verificacion_
    malformada_lanza_jeverror`) -- ninguna de esas necesitó cambios.
  - Verificación pedida:
    `.venv/Scripts/python.exe -m pytest -q tests/test_jev.py tests/test_resolucion_referencias.py tests/test_aclaracion_botones.py tests/banco`
    → **250 passed, 99 deselected**.
    `.venv/Scripts/python.exe -m pytest -q` → **716 passed, 99 deselected**
    (715 + 1 neta -- dos pruebas nuevas de b-0013/rival-débil menos una
    prueba vieja del corte que se reemplazó -- 0 regresiones, 163,89 s).
  - No hubo commit (no pedido explícito todavía); no se leyó ni se tocó
    ningún `.env*`; `docs/` y `nucleo/` sin tocar.
- 2026-09-24: **T7, cuarta ronda (M, N) cerrada.** Motivo: cuarta corrida del
  banco real (81 passed, 18 failed). Hallazgo nuevo sobre las grabaciones: la
  pregunta "rival" (T7, punto L) se disparaba mal en pedidos de dependencia
  que nombran las dos tareas ("el cableado del tablero no puede arrancar
  hasta que yo termine de programar el PLC") -- cada referencia tiene a la
  otra tarea como subcampeona, y "rival" (que preguntaba por el MENSAJE
  completo) contestaba que sí para las dos (0,54-0,56), así que las dos
  referencias quedaban ambiguas y b-0005 (9/9) y b-0015 (3/3) preguntaban en
  vez de crear la dependencia. El orquestador midió tres redacciones (diseño
  §5.12, sin commitear -- no se tocó `docs/`) y adoptó la v2, que pregunta
  por la REFERENCIA en vez del mensaje. Ruta: delegada, un escritor (misma
  fila de T7 en "Ruta", se extiende a `src/leda/jev.py`,
  `tests/banco/comprobadores.py`, pruebas en `tests/test_jev.py`,
  `tests/banco/test_comprobadores.py`). No se tocó `docs/` ni `nucleo/` ni
  ningún `.env*`. `pg_isready` verificado antes de empezar. TDD estricto,
  RED real antes de cada punto, dobles/fakes solamente, sin modelo ni Jev
  real, sin commit/stage/stash:
  1. **M (redacción v2 de "rival").** RED con
     `.venv/Scripts/python.exe -m pytest -q tests/test_jev.py -k instruccion_rival_pregunta`
     → **1 failed** (`INSTRUCCION_RIVAL` seguía con la redacción vieja, "¿El
     mensaje también podría..."). GREEN con
     `.venv/Scripts/python.exe -m pytest -q tests/test_jev.py` → **48
     passed**.
  2. **N (comprobador del banco, "qué").** RED con
     `.venv/Scripts/python.exe -m pytest -q tests/banco/test_comprobadores.py -k que`
     → **2 failed, 18 passed** (las dos nuevas positivas de "qué" fallaban;
     las negativas -- incluida una nueva contra "porque" como falso
     positivo de subcadena -- ya pasaban de entrada, como tenía que ser).
     GREEN con
     `.venv/Scripts/python.exe -m pytest -q tests/banco/test_comprobadores.py`
     → **83 passed**.
  - Verificación pedida:
    `.venv/Scripts/python.exe -m pytest -q tests/test_jev.py tests/banco`
    → **204 passed, 99 deselected**.
    `.venv/Scripts/python.exe -m pytest -q` → **721 passed, 99 deselected**
    (716 + 5 nuevas -- M 1, N 4 -- 0 regresiones, 157,35 s).
  - **M -- `jev.INSTRUCCION_RIVAL`:** redacción reemplazada exactamente por
    la que pidió el encargo -- "¿La referencia, tal como está dicha, también
    podría estar hablando de esta otra tarea en lugar de la elegida?
    Respondé que sí sólo si una persona del equipo podría entender esa
    referencia como cualquiera de las dos." `CORTE_RIVAL`, los campos del
    `state` (`tarea_elegida`/`otra_tarea`) y el resto de la lógica de L no
    se tocaron -- cambio de una sola constante. Prueba nueva
    `test_instruccion_rival_pregunta_por_la_referencia_no_por_el_mensaje`
    fija la redacción exacta y confirma que la frase vieja ("El mensaje
    también podría") ya no está.
  - **N -- `comprobadores._pide_elegir_en_imperativo`:** se agrega "qué"
    como segundo marcador junto a "cuál" (además del verbo). **Decisión de
    esta unidad, no dicha por el encargo:** "qué" se busca con borde de
    palabra (`re.compile(r"\bque\b")`), no como subcadena como ya hacía
    "cuál" -- "porque" y "aunque" contienen "que" como subcadena, y
    cualquier cierre cordial con esas palabras habría contado como pedido
    de elección; con borde de palabra, "porque" no matchea pero "decime qué
    preferís" sí. Prueba nueva
    `test_pregunta_imperativo_porque_no_es_un_falso_positivo_de_que` cubre
    justo ese caso. Las dos evidencias del encargo
    (`test_pregunta_imperativo_contame_que_la_esta_frenando_aprueba`,
    `test_pregunta_imperativo_decime_que_preferis_aprueba`) y el negativo
    pedido (`decime si necesitás algo más`, ya existente y sin tocar) pasan
    igual.
  - No hubo commit (no pedido explícito todavía); no se leyó ni se tocó
    ningún `.env*`; `docs/` y `nucleo/` sin tocar.
- 2026-09-24 (orquestador): **cierre.** Banco real con Jev, cinco corridas: 58, 77, 84,
  81 y 96 de 99 aprobadas (`.venv/Scripts/python.exe -m pytest -m modelo_real
  tests/banco --banco-proveedor nan --banco-modelo deepseek-v4-flash -q`). Las 3 que
  fallan son `b-0005-b` ("el plc" entre 0,79 y 0,84, corte 0,85): pregunta de más,
  segura, queda como límite conocido. Mediciones de la segunda candidata en diseño
  §5.11 y §5.12. Continuidad: `docs/capacidades.md`, `docs/STATUS.md`, diseño §4.5,
  `docs/ROADMAP.md` (incidentes, retención por cliente, aprendizaje de apodos y
  aclaraciones con Engram y Obsidian como insumos). Suite: 721 passed, 99 deselected.
- 2026-09-24 (orquestador): **commits y revisión RDD.** El commit único de T6+T7
  excedía el presupuesto de contexto del revisor (`lens_context_budget_exceeded`, 31
  archivos, 2865 líneas); con autorización del usuario se rehízo el historial local, no
  publicado, en trozos: `97f8f7b` (banco), `e31f702` (herramientas), `8ea8d86`
  (resolución) y `79222c1` (documentación). Revisión de fiabilidad sobre `97f8f7b`:
  aprobada y reconocida (`review-6539bc79b03fec85`). Revisión sobre `e31f702`+`8ea8d86`
  (1126 líneas): aprobada y reconocida (`review-bcea0cbe2601ab6b`). La documentación se
  evaluó pasiva, sin revisión. Los trozos intermedios no se probaron uno por uno; la
  suite pasa sobre el estado final.

  Observaciones no bloqueantes, pendientes para una unidad posterior:
  `tests/banco/corrida.py:519-528` (sugerencia: aclaración esperada sin objetivo);
  `tests/banco/comprobadores.py:445-455` (advertencia: el imperativo compara por
  subcadena); `tests/banco/corrida.py:124-128` (sugerencia: grabador de Jev y la
  referencia); `tests/test_resolucion_referencias.py:329-351` (advertencia: la prueba de
  descarte de redundantes usa "revisión", que ahora descarta el filtro de estados, así
  que no prueba el descarte); `src/leda/gateway.py:968-982` (advertencia: el
  vocabulario de estados puede descartar una referencia real como "la lista").

