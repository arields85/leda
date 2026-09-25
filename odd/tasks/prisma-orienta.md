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
- [ ] **T2 — Menú de tarea.** Tocar una tarea ofrece las acciones del diseño §4.6
  según estado y relación (responsable, aprobador, otra persona), calculadas por
  código. Cada acción sigue su camino: ver detalle (lectura), acciones que cambian
  (herramienta con vista previa), acciones que necesitan un dato (por ejemplo la causa
  de un bloqueo) lo piden.
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
