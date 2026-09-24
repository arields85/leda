# Aclaración con botones

**Estado:** en curso
**Creado:** 2026-09-24
**Origen:** [`ADR 0005`](../../docs/decisions/0005-interpretacion-y-confirmacion.md)
puntos 3 y 4, [`ADR 0006`](../../docs/decisions/0006-jev-para-resolver-referencias-e-intencion.md);
receta en `docs/architecture/interpretacion-y-confirmacion.md` §5.6, §5.8 y §5.9.

## Objetivo

Que Prisma sepa a qué tarea se refiere un mensaje antes de actuar, y que ante la
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
- `config.py` no tiene `PRISMA_OPENROUTER_API_KEY`; no hay cliente de Jev.

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
- **Si Jev no responde,** Prisma no adivina: pide que la persona diga a qué tarea
  se refiere.
- **Sólo viajan datos del espacio actual** (títulos, áreas, responsables, glosario
  y el texto del mensaje), leídos bajo el cursor con RLS.

## Tareas

- [x] **T1 — Cliente de Jev y resolución.** `Config.openrouter_api_key`
  (`PRISMA_OPENROUTER_API_KEY`); cliente de la API de decisiones de OpenRouter;
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
- [ ] **T4 — Botones de aclaración.** Ambigua: una `pending_action` con una opción
  por candidata y "Ninguna, lo escribo". Elegir retoma el mensaje original con la
  tarea resuelta y termina en la vista previa; "Ninguna" pide el texto.
  Además (revisión de T3): la corrección que llega después de Modificar también
  pasa por la resolución de referencias; hoy el modelo la resuelve solo.
- [ ] **T5 — Respuestas que nombran la tarea.** Toda respuesta a una consulta
  nombra la tarea por su título (protección de las lecturas, ADR 0006).
- [ ] **T6 — Banco y continuidad.** Grabador de Jev para el banco, escenarios
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
  No module named 'prisma.jev'`, 1 error), GREEN con el mismo comando (18 passed).
  Suite completa: `.venv/Scripts/python.exe -m pytest -q` → **554 passed, 90
  deselected** (536 + 18 nuevos, 0 regresiones, 173,87 s).
  - `src/prisma/config.py`: agregado `Config.openrouter_api_key` desde
    `PRISMA_OPENROUTER_API_KEY`, mismo patrón que `llm_api_key`.
  - `src/prisma/jev.py` (nuevo): `ClienteJev` (httpx, `POST
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
    `PRISMA_OPENROUTER_API_KEY=` a mano o en una sesión con ese permiso
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
  comando → **30 passed**. Arreglos en `src/prisma/jev.py`:
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
    `.env.ejemplo` con `PRISMA_OPENROUTER_API_KEY=`, `src/prisma/jev.py`,
    `tests/test_jev.py` y este documento).
- 2026-09-24: **T2 cerrada.** Ruta: delegada, un escritor (T2 tiene su fila
  propia en "Ruta"; `llm.py` en los tres proveedores, pruebas). TDD estricto:
  RED observado con `.venv/Scripts/python.exe -m pytest -q
  tests/test_llm_protocol.py` (`AttributeError: module 'prisma.llm' has no
  attribute 'MAX_LONGITUD_REFERENCIA'`, error de colección) y con
  `.venv/Scripts/python.exe -m pytest -q tests/banco/test_corrida.py -k
  "trabajos_y_personas or grabacion_vieja"` (2 failed:
  `TypeError: IntentRoute.__init__() got an unexpected keyword argument
  'trabajos'` y `AttributeError: 'IntentRoute' object has no attribute
  'trabajos'`). GREEN con `tests/banco tests/test_llm_protocol.py` → **225
  passed, 90 deselected**. Suite completa: `.venv/Scripts/python.exe -m
  pytest -q` → **605 passed, 90 deselected** (566 + 39 nuevas, 0 regresiones,
  179,10 s).
  - `src/prisma/llm.py`: `IntentRoute` gana `trabajos` y `personas` (tuplas
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
    el docstring de `_referencias_o_vacio` en `src/prisma/llm.py`.
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
    (incluye `src/prisma/llm.py`, `tests/test_llm_protocol.py`,
    `tests/banco/corrida.py`, `tests/banco/test_corrida.py` y este
    documento).
- 2026-09-24: **T3 cerrada.** Ruta: delegada, un escritor (T3 tiene su fila
  propia en "Ruta"; `gateway.py`, `agente.py`, `contexto.py`, pruebas --
  también `jev.py` y `tests/banco/corrida.py`, extensión natural de la
  fábrica de Jev y del banco). TDD estricto: RED observado con
  `.venv/Scripts/python.exe -m pytest -q tests/test_resolucion_referencias.py`
  (`AttributeError: <module 'prisma.jev' ...> has no attribute 'desde_base'`,
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
    tarea):** sin `PRISMA_OPENROUTER_API_KEY`, Prisma **no** sigue como si
    Jev no existiera. Con referencias en el mensaje, la falta de credencial
    se trata igual que un `JevError` en cada una -- se le pide al modelo que
    pregunte, nunca que elija solo -- y además deja un incidente (sin
    secretos ni texto del mensaje) para que la falta de configuración no
    pase inadvertida. Un mensaje sin referencias no se toca. Reemplaza el
    criterio original de T3 ("si la clave está vacía, saltear la resolución
    por completo... para que las pruebas y los despliegues sin la clave no
    cambien"): ese criterio hubiera dejado a Prisma adivinando en cualquier
    despliegue sin la clave configurada, que es justo lo que esta unidad
    existe para evitar.
  - `src/prisma/jev.py`: `desde_base(api_key) -> Jev | None` -- `None` si
    `api_key` está vacía, si no un `ClienteJev`. Mismo patrón de reemplazo
    que `llm.desde_base`: un import local en `_turno` lee este nombre del
    módulo en cada turno, así que alcanza con reemplazar
    `prisma.jev.desde_base` para las pruebas y para que el banco no llame a
    Jev de verdad por defecto.
  - `src/prisma/contexto.py`: extraídas `_glosario_filas` y `_lineas_glosario`
    de adentro de `construir()`, y agregada `vocabulario(cur, workspace_id)
    -> str` (mismo glosario en texto plano, vacío si no hay) -- para no
    repetir la consulta y para que `gateway.py` pueda pasarle el mismo
    vocabulario del equipo a Jev (ADR 0006, "sólo viajan datos del espacio
    actual"). `construir()` se comporta igual que antes (probado por
    `test_contexto_lleva_nucleo_glosario_y_equipo`, sin tocar).
  - `src/prisma/agente.py`: `responder()` gana `contexto_referencias: str |
    None = None`, agregado al sistema igual que `modificacion` -- contexto
    de confianza del servidor, nunca texto de la persona.
  - `src/prisma/gateway.py`, en `_turno` (después de `route_intent`, antes
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
    explícito, nunca `None` (que desde esta unidad hace que Prisma pida en
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
