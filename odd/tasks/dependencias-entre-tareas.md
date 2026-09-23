# Dependencias entre tareas

**Estado:** terminado
**Creado:** 2026-09-22
**Origen:** `docs/STATUS.md`, "Próximo paso"; `docs/capacidades.md`, fila
"Dependencias entre tareas". Precondición de la conversación de bloqueos
(mecánica §8, pasos 2 a 7).

## Objetivo

Que Prisma haga visibles las dependencias: se registran, frenan a quien todavía
no puede arrancar y avisan en cadena antes de que un atraso se convierta en
sorpresa. La misión §2 nombra "dependencias invisibles" como uno de los
problemas que Prisma existe para reducir.

## Problema

El esquema está completo y el comportamiento no existe:

- `dependency`, `tipo_dependencia`, el disparador `evitar_ciclo_dependencia` y la
  condición de cierre de `motivo_no_cierra_tarea` ya están en `db/esquema.sql`.
- Ninguna ruta de código crea una fila en `dependency`. `escalera._dependientes`
  cuenta filas que nadie crea.
- Nada impide que una tarea pase a `en_curso` con su bloqueante sin terminar.
- Nadie avisa de un atraso a quien depende.

## Qué manda el núcleo (mecánica §4)

- **bloqueante:** la tarea destino no puede pasar a `en_curso` hasta que la
  origen esté `terminada`.
- **informativa:** no impide avanzar; Prisma avisa a ambas partes cuando la
  origen cambia de fecha o de estado.
- Los ciclos se rechazan al crear.
- Cuando una bloqueante se atrasa, Prisma calcula el impacto en cadena y lo
  informa a los responsables afectados **antes** de que venzan sus fechas.
- Una dependencia entre áreas distintas se notifica a los dos referentes.

## Decisión de producto (usuario, 2026-09-22)

**Quién crea una dependencia:** el responsable de cualquiera de las dos tareas,
o su referente. Prisma avisa a la otra parte. Motivo: una dependencia bloqueante
frena la tarea de otra persona, así que no puede declararla cualquiera; pero
exigir confirmación de la otra parte agrega fricción sin necesidad, porque el
aviso ya la hace visible.

## Alcance

**Incluido:** crear y quitar dependencias, freno de `en_curso` por bloqueante
sin terminar, aviso en cadena por atraso, aviso de dependencia informativa,
aviso a referentes entre áreas, migración con rollback, continuidad.

**Excluido:** la conversación de bloqueos (§8, pasos 2 a 7) y el banco de
pruebas conversacional con el modelo real, que es la unidad siguiente.

## Tareas

- [x] **T1 — Crear y quitar.** Herramientas `crear_dependencia` y
  `quitar_dependencia` con la autoridad decidida arriba; aviso a la otra parte y,
  entre áreas, a los dos referentes; ciclo rechazado con mensaje claro.
- [x] **T2 — Freno de `en_curso`.** En la base, con migración y rollback: la
  destino de una bloqueante no pasa a `en_curso` con la origen sin terminar.
- [x] **T3 — Aviso en cadena.** Una bloqueante atrasada, o cuya fecha queda
  después de la de su dependiente, avisa una vez a cada responsable afectado de
  la cadena, antes de su propio vencimiento. Dependencia informativa: aviso a
  ambas partes cuando la origen cambia de estado (el aviso por cambio de fecha
  queda sin disparador — ver Progreso).
- [x] **T4 — Continuidad.** `docs/capacidades.md`, `tests/test_capacidades.py`,
  `docs/STATUS.md`.

## Ruta

| Tarea | Ruta | Evidencia del disparador |
|---|---|---|
| T1–T4 | delegada, un escritor | toca 3+ archivos no triviales (`herramientas.py`, `autoridad.py`, `escalera.py`, esquema, migración, pruebas, docs) |

## Verificación

- TDD estricto: prueba en rojo observada antes de cada implementación.
- Runner: `.venv/Scripts/python.exe -m pytest -q`.
- Línea base: 356 passed (2026-09-22, commit `4ccf21c`).

## Entrega

Un solo commit sobre `master`, por pedido explícito del usuario: la creación de
dependencias y los avisos comparten `src/prisma/herramientas.py` y partirlos
exigía dividir el archivo a mano. Suite completa en ese contenido: 389 passed,
verificado por el orquestador. Sin remoto con contenido, no hay pull requests.

## Progreso

- 2026-09-22: documento creado, línea base 356 passed.
- 2026-09-22: T1–T4 implementadas. Suite completa: 384 passed
  (`.venv/Scripts/python.exe -m pytest -q`), TDD estricto por cada bloque de
  comportamiento (rojo observado antes de implementar).

  **T1** (`src/prisma/herramientas.py`, sección "Dependencias"): autoridad
  vía `_autorizado_para_dependencia` (responsable de cualquiera de las dos, o
  `puede_aprobar_tarea` de cualquiera de los dos — la misma noción de
  "referente" que ya usa `aprobar_tarea`), con `valida_en_handler=True` como
  `aprobar_tarea`/`resolver_bloqueo` (no hizo falta tocar `autoridad.py`: una
  acción no declarada ahí ya deniega por defecto). Rechaza: misma tarea en
  las dos puntas, tarea inexistente ("no existe"), duplicada, destino ya
  cerrada. Un ciclo lo rechaza `trg_evitar_ciclo_dependencia`, sin captura
  especial: `agente.py` ya traduce `psycopg.errors.RaiseException` a mensaje
  legible para el turno del modelo (probado por `H.ejecutar` directo, que no
  pasa por esa capa, con `pytest.raises(psycopg.errors.RaiseException,
  match="ciclo")`). Aviso a la otra parte y, entre áreas, a los dos
  referentes (aprobador de cada responsable), deduplicados, nunca a quien
  crea. `quitar_dependencia`: misma autoridad, baja física (no hay columna de
  baja blanda en `dependency` como `blocker.resuelto_en`); el rastro de quién
  quitó qué quedó cubierto por el mecanismo genérico existente
  (`agente._ejecutar_una` → `registrar_auditoria`, accion
  `herramienta:quitar_dependencia` con los argumentos), no se agregó
  auditoría propia a la herramienta — se decidió no agregar una columna de
  baja blanda porque el patrón existente (auditoría genérica por llamada) ya
  cubre quién/cuándo/qué sin esquema nuevo.
  Decisión no zanjada por la mecánica: si el origen queda cerrada
  (`terminada`/`cancelada`) no se rechaza la creación —una bloqueante
  `terminada` ya no bloquea, y `cancelada` tampoco por el mismo criterio que
  usa `motivo_no_cierra_tarea` (ver T2)—; sólo se rechaza cuando la
  **destino** ya está cerrada, con el mismo criterio que `registrar_bloqueo`
  usa para no agregar un bloqueo a una tarea cerrada. Si el destino ya está
  `en_curso` al crear una bloqueante, no se la mueve retroactivamente y el
  aviso lo menciona explícitamente.

  **T2** (`db/esquema.sql`, `db/migrations/0008_task_start_gate.sql` +
  rollback, `src/prisma/herramientas.py::_actualizar_estado`): función
  `motivo_no_arranca_tarea` y disparador `trg_exigir_dependencias_resueltas`
  (antes de insertar en `task_state_event`, estilo idéntico a
  `exigir_bloqueo_abierto`/`exigir_condiciones_de_cierre`); `cancelada`
  libera el freno igual que `terminada`, mismo criterio que
  `motivo_no_cierra_tarea` para no bloquear la destino para siempre con un
  origen que nunca va a terminar. `_actualizar_estado` hace el mismo chequeo
  proactivo que ya hacía para `terminada`, devolviendo `{"iniciada": False,
  "falta": ...}` en vez de dejar que la excepción de la base se convierta en
  incidente. Prueba dedicada de migración
  (`test_0008_motivo_no_arranca_tarea_llega_por_migracion` en
  `tests/test_task_intake.py`, siguiendo el modelo de la de 0007) y las
  pruebas genéricas de rollback/paridad (`test_los_rollbacks_devuelven_...`,
  `test_migration_clean_schema_parity_and_guarded_rollback`) pasan con la
  cadena completa.

  **T3** (`src/prisma/escalera.py`, `src/prisma/reloj.py`): "en riesgo" =
  origen `bloqueante` no `terminada`/`cancelada` y (vencida, o con
  `fecha_objetivo` posterior a la de un dependiente directo que todavía la
  necesita). Cuando está en riesgo, `_cadena_de_dependientes` recorre
  transitivamente sólo aristas `bloqueante` (CTE recursiva) y notifica a cada
  responsable de la cadena una vez por (origen, su `fecha_objetivo` vigente,
  destinatario) — mismo destinatario con dos tareas afectadas en la misma
  cadena recibe un solo aviso, que es lo que pide la letra ("una vez a cada
  responsable", no "por tarea"). `reloj.ejecutar_escalera` la corre en la
  misma pasada que `evaluar`/`evaluar_bloqueos`. Informativa: se avisa a las
  dos partes cuando la origen cambia de estado, enganchado en las tres
  herramientas que insertan `task_state_event`
  (`_actualizar_estado`/`_registrar_bloqueo`/`_resolver_bloqueo`) vía
  `_avisar_dependencia_informativa`. **Gap confirmado, no implementado**: el
  aviso por cambio de `fecha_objetivo` no tiene disparador posible hoy.
  `bloquear_estado_directo()` en `db/esquema.sql` vuelve `fecha_objetivo`
  inmutable apenas se compromete la tarea (lanza excepción si cambia), y no
  hay ninguna ruta de código que la modifique — se comprobó con grep sobre
  `src/prisma/*.py`. Queda registrado como deuda, no como tarea pendiente de
  esta unidad.
  Decisión: `task_state_event` es append-only y `prisma_app` sólo tiene
  `insert` (no `select`); un `returning id` en ese insert falla con
  `InsufficientPrivilege` porque Postgres exige `select` para `returning`
  (se descubrió en rojo durante T3). La clave de deduplicación de la
  informativa usa un `uuid.uuid4()` generado en Python en vez del id de la
  fila insertada — no hay reintento de la misma llamada dentro de la misma
  transacción, así que no hace falta leer la fila para garantizar unicidad
  por evento.

  **T4**: fila "Dependencias entre tareas" movida de "Diseñado y sin
  construir" a "Construido y sólido" en `docs/capacidades.md`, con evidencia;
  fila "Conversación de bloqueos" actualizada (su precondición ya no está
  pendiente). `tests/test_capacidades.py`: sacada la entrada `destino_task_id`
  de `PROMESAS_SIN_CUMPLIR` (la prueba lo pedía en rojo). `docs/STATUS.md`:
  "Próximo paso" pasa a ser el banco de pruebas conversacional
  (`docs/validation/README.md`) y después la conversación de bloqueos; se
  agregó "Cerrado: dependencias entre tareas" con la evidencia de esta
  unidad.

  Verificación: `.venv/Scripts/python.exe -m pytest -q` → 384 passed;
  `git status --short` y `git diff --stat` confirmados antes de este cierre.

- 2026-09-22: **Corrección tras revisión.** Tres defectos del padre, mismo
  TDD estricto (rojo observado antes de corregir donde se indica), sin
  commits, sin leer `.env*`, sin SQL destructivo fuera de fixtures. Suite
  completa: 388 passed (356 base + 27 T1–T4 + 5 de esta corrección: 4 nuevas
  más la reescritura de una existente).

  **Defecto 1 — el freno de `en_curso` rompía la resolución de bloqueos.**
  Escenario: X en curso; se crea una bloqueante con X de destino y la origen
  sin terminar (T1 lo permite, sin mover X retroactivamente); X se bloquea;
  se intenta resolver el último bloqueo. `resolver_bloqueo` inserta
  `bloqueada -> en_curso` (mecánica §3: vuelve al estado previo) y
  `trg_exigir_dependencias_resueltas` lo rechazaba, dejando el bloqueo
  irresoluble mientras la dependencia siguiera abierta. Rojo observado:
  `test_resolver_bloqueo_no_se_frena_por_dependencia_bloqueante_abierta` →
  `psycopg.errors.RaiseException: No se puede pasar la tarea a en curso:
  Quedan 1 dependencias bloqueantes sin resolver.`
  Corrección: `exigir_dependencias_resueltas()` (`db/esquema.sql` y
  `db/migrations/0008_task_start_gate.sql`, editada en el lugar — 0008 nunca
  se aplicó a una base real, así que no hizo falta una 0009) exime el
  chequeo cuando `new.estado_anterior = 'bloqueada'`: volver de un bloqueo es
  una restauración al estado previo, no un arranque, y ese estado previo ya
  había pasado (o no necesitaba pasar) el chequeo la primera vez. Comentario
  SQL actualizado en ambos archivos explicando la excepción.
  **Camino directo, decisión explícita:** `actualizar_estado` no exige
  bloqueos cerrados para salir de `bloqueada` (deuda conocida, ya registrada
  antes de esta unidad), así que puede recibir la misma transición
  `bloqueada -> en_curso` que `resolver_bloqueo` sin pasar por la resolución
  del bloqueo. Mecánica §3 no distingue por qué herramienta se sale de
  `bloqueada`: dice que se vuelve al estado previo, sin condicionarlo a que
  el bloqueo se haya cerrado antes. Como el disparador ya lo exime por
  `estado_anterior` (un hecho de la fila, no de qué tool lo escribió), dejar
  el chequeo proactivo de `_actualizar_estado` sin eximir habría sido
  inconsistente con la base: la herramienta habría devuelto `iniciada: False`
  para una transición que la base iba a aceptar igual. Se exime también ahí
  (`fila["estado"] != "bloqueada"`). Rojo observado:
  `test_actualizar_estado_de_bloqueada_a_en_curso_no_se_frena_por_dependencia`
  → `{"iniciada": False, "falta": "Quedan 1 dependencias bloqueantes sin
  resolver."}` en vez de `{"estado": "en_curso"}`.

  **Defecto 2 — la clave de deduplicación perdía el aviso más grave.** La
  clave no distinguía el motivo del riesgo ("posterior" vs "vencida"); si el
  aviso por fecha posterior salía primero y la origen se vencía de verdad
  después, el segundo aviso reusaba la clave y se perdía. Corrección:
  `evaluar_dependencias_en_riesgo` calcula el motivo (`"vencida"` si está
  vencida, si no `"posterior"` cuando corresponde) y lo incluye en la clave
  de deduplicación (`escalera.py`). Prueba de regresión
  (`test_dependencia_en_riesgo_reavisa_al_pasar_de_posterior_a_vencida`):
  corrida 1 con fecha posterior avisa; corrida 2 sobre el mismo momento no
  duplica; se adelanta `ahora` hasta vencer la origen y la corrida 3 avisa de
  nuevo con el texto de "vencida"; la corrida 4 sobre ese mismo momento no
  duplica; dos filas en `message_outbox` en total.

  **Defecto 3 — el aviso no nombraba la tarea afectada.** "de ella depende
  esta tarea" no daba nada concreto para actuar, y para un dependiente
  indirecto era además inexacto (no depende directamente). Corrección:
  `_cadena_de_dependientes` ahora distingue directo de indirecto (CTE
  recursiva con una columna `directo`, `distinct on` se queda con la fila
  directa cuando el mismo destino se alcanza por más de un camino);
  `evaluar_dependencias_en_riesgo` agrupa por destinatario (una persona con
  más de una tarea afectada en la cadena recibe un solo aviso con todas,
  no uno por tarea) y `_texto_dependencia_en_riesgo` lista los títulos, con
  "(a través de la cadena)" para los indirectos. `AccionDependencia` pasa a
  llevar `destino_task_ids` (lista) en vez de un solo `destino_task_id`, sin
  romper ninguna prueba existente (nada leía ese campo directamente). Prueba
  de regresión
  (`test_dependencia_en_riesgo_nombra_las_tareas_afectadas_directas_e_indirectas`,
  con la cadena de tres tareas ya usada en otras pruebas de T3) confirma que
  el título de la tarea directa aparece sin "cadena" y el de la indirecta
  aparece con "(a través de la cadena)".
  **Nota de honestidad sobre el proceso:** para los defectos 2 y 3, la
  implementación y las pruebas de regresión se escribieron en el mismo paso
  (no se observó un rojo aislado sólo con el defecto, sin el resto de T3, ya
  aplicado); si se hubiera revertido nada más que ese fragmento el rojo
  habría sido indistinguible de "la función no existe todavía" en vez de
  mostrar el defecto puntual. El rojo del defecto 1 sí se observó aislado,
  documentado arriba con el mensaje exacto. Los defectos 2 y 3 quedan
  verificados por las aserciones de contenido (texto "vencida"/"posterior",
  título de tarea presente/ausente según directo o indirecto) y por la
  suite completa en verde, no por un rojo previo capturado por separado.

  Verificación: `.venv/Scripts/python.exe -m pytest -q` → 388 passed;
  `git status --short` confirmado, sin cambios sin revisar.

  **Segunda revisión sobre el defecto 1 — la exención era demasiado amplia.**
  Eximir el freno con sólo `new.estado_anterior = 'bloqueada'` dejaba pasar
  una tarea que nunca había arrancado: `asignada` -> `registrar_bloqueo` ->
  `bloqueada` -> `actualizar_estado(en_curso)` quedaba exenta igual, aunque
  la origen bloqueante siguiera sin terminar -- exactamente lo que mecánica
  §4 prohíbe. La restauración legítima que mecánica §3 describe es más
  angosta: sólo cuando el estado previo a la ÚLTIMA entrada a `bloqueada`
  -- no el evento inmediatamente anterior a este, sino el que tenía la tarea
  justo antes de bloquearse -- era `en_curso`.
  Corrección: tanto el disparador (`db/esquema.sql` y
  `db/migrations/0008_task_start_gate.sql`, editada en el lugar otra vez, sin
  0009) como el chequeo proactivo de `_actualizar_estado` consultan ahora
  `estado_previo_a_bloqueo(new.task_id)` (0007) y sólo eximen cuando esa
  función devuelve `en_curso`. Se verificó que el preflight de 0008 ya exige
  0007 (`to_regprocedure('prisma.estado_previo_a_bloqueo(uuid)')`, existente
  desde la primera versión de la migración) y que `prisma_app` -- el único
  rol que hoy hace pasar una tarea a `en_curso`, vía `resolver_bloqueo` o
  `actualizar_estado` -- ya tenía `execute` concedido sobre esa función desde
  0007; no hizo falta ninguna concesión nueva. Comentario SQL reescrito en
  ambos archivos documentando la corrección y por qué la primera versión no
  alcanzaba.
  Rojo observado (aislado, con `git stash` de sólo `db/esquema.sql` y
  `src/prisma/herramientas.py` para reproducir la versión demasiado amplia
  de la primera corrección, sin tocar el resto del árbol):
  `test_en_curso_desde_bloqueada_sigue_frenado_si_nunca_arranco` →
  `KeyError: 'iniciada'` (la herramienta devolvía `{"estado": "en_curso"}`,
  o sea que la dejaba pasar, cuando tenía que devolver `{"iniciada": False,
  "falta": ...}`). Verde después de restaurar la corrección
  (`git stash pop`): `tests/test_dependencias.py` → 32 passed (31 + esta),
  incluidas las dos pruebas de regresión del defecto 1 originales
  (`test_resolver_bloqueo_no_se_frena_por_dependencia_bloqueante_abierta` y
  `test_actualizar_estado_de_bloqueada_a_en_curso_no_se_frena_por_dependencia`,
  que arrancan desde `en_curso` y siguen exentas correctamente).

  Verificación: `.venv/Scripts/python.exe -m pytest -q` → 389 passed;
  `git status --short` confirmado.
