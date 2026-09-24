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
- [ ] **T2 — Referencias en el enrutador.** `route_intent` devuelve además las
  referencias a trabajos tal como están dichas, en los tres proveedores y con su
  validación.
- [ ] **T3 — Resolver antes de actuar.** En `_turno`, las referencias se resuelven
  contra las tareas activas del espacio. Clara: el agente recibe la tarea resuelta
  como contexto. Una referencia a una tarea existente no arranca el alta de tarea
  nueva (corrige `b-0005`). Jev caído: se pide la referencia.
- [ ] **T4 — Botones de aclaración.** Ambigua: una `pending_action` con una opción
  por candidata y "Ninguna, lo escribo". Elegir retoma el mensaje original con la
  tarea resuelta y termina en la vista previa; "Ninguna" pide el texto.
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
    `gateway`/`agente`; sin commit.
