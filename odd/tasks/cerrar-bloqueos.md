# Cerrar bloqueos

**Estado:** terminado
**Creado:** 2026-09-22
**Origen:** auditoría completa (`docs/capacidades.md`, fila "Cerrar bloqueos").
Primer punto del orden por daño acordado al cierre de la sesión anterior.

## Objetivo

Que un bloqueo tenga ciclo de vida completo: se abre, se resuelve, y si nadie lo
resuelve escala solo por antigüedad. Hoy se abre y queda abierto para siempre.

## Problema

- `blocker.resuelto_en`, `resolucion`, `escalado_a` y `escalado_en` existen en el
  esquema y ninguna ruta de código los escribe.
- Una tarea que entra en `bloqueada` no puede salir: la escalera la saltea
  mientras tenga un bloqueo abierto, así que la tarea deja de recordarse para
  siempre.
- `espacios/corework.yaml` declara `bloqueos.escala_solo_a_los_dias: 5`; el
  importador lo guarda y nadie lo lee.

## Qué manda el núcleo

- Mecánica §3: salir de `bloqueada` devuelve la tarea al estado que tenía antes,
  no a `asignada`. `bloqueada` requiere un bloqueo abierto asociado.
- Mecánica §8: un bloqueo abierto hace más de **[pack]** días escala aunque nadie
  lo pida. Escala según las rutas del espacio.
- Mecánica §9: los momentos se calculan sobre el calendario laboral del espacio.
- Constitución: la persona responsable informa la resolución en lenguaje natural.

## Alcance

**Incluido:** herramienta para resolver un bloqueo, retorno al estado previo,
escalamiento por antigüedad, corrección de `registrar_bloqueo`, documentación de
capacidades y estado.

**Excluido:** los pasos conversacionales de §8 (pedir información, proponer
soluciones, identificar tareas afectadas en cadena). Dependen de dependencias,
que son la unidad siguiente.

## Tareas

- [x] **T1 — Resolver un bloqueo.** Herramienta `resolver_bloqueo` con
  resolución obligatoria. Cuando se cierra el último bloqueo abierto de la tarea,
  la tarea vuelve al estado previo a `bloqueada`. Corregir `registrar_bloqueo`:
  tarea inexistente, doble entrada a `bloqueada`, consulta suelta.
- [x] **T2 — Escalamiento por antigüedad.** Un bloqueo abierto más de
  `bloqueos.escala_solo_a_los_dias` días hábiles escala una sola vez por la ruta
  del espacio, deja `escalado_a` y `escalado_en`, y sale por outbox.
- [x] **T3 — Continuidad.** `docs/capacidades.md`, `tests/test_capacidades.py` y
  `docs/STATUS.md` (su "Próximo paso" describe trabajo ya terminado).

## Ruta

| Tarea | Ruta | Evidencia del disparador |
|---|---|---|
| T1–T3 | delegada, un escritor | toca 3+ archivos no triviales (`herramientas.py`, `escalera.py`, pruebas, docs) |

## Verificación

- TDD estricto: prueba en rojo observada antes de cada implementación.
- Runner: `.venv/Scripts/python.exe -m pytest -q`.
- Línea base: 336 passed (2026-09-22).

## Entrega

Dos commits por pedido explícito del usuario, sobre `master` como el resto de
la historia:

1. `cc23b50` — resolución de bloqueos, función `estado_previo_a_bloqueo`,
   migración 0007 con su rollback y las pruebas de T1. Verificado en aislamiento
   (worktree desechable en ese commit): 351 passed.
2. El commit siguiente — escalamiento por antigüedad (T2) y continuidad (T3).
   Suite completa: 356 passed.

## Progreso

- 2026-09-22: documento creado, línea base 336 passed.
- 2026-09-22: T1, T2 y T3 implementadas con TDD estricto (rojo observado por
  comportamiento, luego verde). Suite completa: 353 passed (17 pruebas nuevas
  en `tests/test_bloqueos.py`, cero regresiones).

  **T1.** `resolver_bloqueo(bloqueo_id, resolucion)` en `src/prisma/herramientas.py`,
  `valida_en_handler=True`: autoriza al responsable de la tarea, a quien abrió el
  bloqueo o a quien se escaló; cualquier otra persona del equipo recibe `Denegado`.
  Bloqueo de otro espacio o inexistente devuelve `"no existe"` (RLS ya lo deja
  invisible, sin filtro manual); ya resuelto devuelve `"ya estaba resuelto"`;
  resolución vacía o sólo espacios levanta `Denegado`. Al cerrar el último bloqueo
  abierto de la tarea, inserta un `task_state_event` de vuelta al estado que tenía
  el último evento antes de `bloqueada` — nunca `asignada` fija (mecánica §3).
  `registrar_bloqueo` corregido: tarea inexistente devuelve `"no existe"` sin
  insertar nada; tarea `terminada`/`cancelada` rechaza el bloqueo nuevo; sobre una
  tarea ya `bloqueada` el bloqueo se suma sin duplicar el evento
  `bloqueada -> bloqueada`; se sacó el `select estado` suelto que no se usaba.

  **Decisión de esquema:** `prisma_app` tiene el `select` revocado sobre
  `task_state_event` (append-only, por diseño — comentario en
  `db/esquema.sql:1687-1691`), así que no hay forma de leer "el estado antes del
  último evento" desde la herramienta sin una puerta nueva. Se agregó
  `estado_previo_a_bloqueo(p_task uuid)`, función `security definer` con el mismo
  patrón que `emitir_acceso_tablero`/`resolver_acceso_tablero` (dueño
  `prisma_owner`, `execute` revocado de `public` y concedido sólo a `prisma_app`).
  Es el mínimo necesario para que "volver al estado previo" no dependa de leer la
  tabla append-only directamente.

  **T2.** `escalera.evaluar_bloqueos` / `escalera.encolar_bloqueos`: un bloqueo
  abierto, no escalado, con más de `bloqueos.escala_solo_a_los_dias` días hábiles
  de antigüedad (calendario del espacio, igual que la escalera de vencimientos)
  escala una vez, deja `escalado_a`/`escalado_en` y encola por outbox con
  `dedupe_key` propia. Sin configuración de `bloqueos` en `workspace_setting`, no
  escala. Enganchado en `reloj.ejecutar_escalera`, no en un scheduler nuevo.

  **Decisión de ruta de escalamiento:** `_ruta_escalamiento` (la que ya usa la
  escalera de vencimientos) no filtra por `disparador`, así que para una tarea de
  OT devolvería la ruta de `problema_tecnico` de esa área — la escalada técnica de
  un vencimiento, no la de un bloqueo. Un bloqueo escala siempre por la ruta
  transversal del pack, sea cual sea el área. Se agregó `_ruta_bloqueo_transversal`,
  que sí filtra `disparador = 'bloqueo_transversal'`, en vez de reutilizar la
  existente con un resultado incorrecto.

  **Decisión de umbral:** mecánica §8 dice "hace **más de** [pack] días", a
  diferencia de la escalera de vencimientos (§9), que dispara en el momento exacto
  `V + 3`. Implementado como `> dias`, no `>= dias`: a los días exactos todavía no
  escala.

  **T3.** `docs/capacidades.md`: fila "Cerrar bloqueos" movida de "Diseñado y sin
  construir" a "Construido y sólido"; la fila de dependencias se renombró a
  "Conversación de bloqueos" para cubrir lo que sigue sin construir (mecánica §8,
  pasos 2 a 7, que dependen de la unidad de dependencias); se sacó la trampa "Un
  bloqueo no se puede cerrar", ya resuelta. `tests/test_capacidades.py`: se
  sacaron `resolucion` y `escalado_a` de `PROMESAS_SIN_CUMPLIR` (la prueba lo pidió
  al implementarse). `docs/STATUS.md`: "Próximo paso" describía la línea base
  versionada y el cierre del aislamiento, ambos ya hechos (sección "Cerrado:
  aislamiento entre clientes"); se reemplazó por el paso real: dependencias entre
  tareas (mecánica §4) — crearlas con rechazo de ciclos, y avisar en cadena a los
  responsables afectados antes de que venza una tarea bloqueante atrasada.

  **Decisión de alcance en pruebas:** no se agregó un escenario de aislamiento
  entre espacios dedicado a cada camino de `resolver_bloqueo`/`registrar_bloqueo`;
  se agregó uno (`test_resolver_bloqueo_de_otro_espacio_dice_que_no_existe`, con
  `intake_world`) para confirmar que RLS cubre también este par de herramientas,
  y se confió en la cobertura de aislamiento ya existente en el resto de la suite
  para el resto de los casos, en vez de duplicar el mismo chequeo en cada test.

  **Gaps:** ninguno detectado que requiriera parar un sub-ítem. Los pasos
  conversacionales de §8 (pedir información, proponer soluciones, preguntar por
  ayuda, identificar tareas en cadena, proponer reasignaciones) quedan fuera de
  alcance según el documento, y dependen de dependencias.

  **Comandos ejecutados:**
  - `.venv/Scripts/python.exe -m pytest -q tests/test_bloqueos.py` → 17 passed
    (rojo previo observado con `AttributeError`/`Denegado: No existe la
    herramienta`/`AssertionError` según el caso, antes de cada implementación).
  - `.venv/Scripts/python.exe -m pytest -q tests/test_capacidades.py` → verde tras
    sacar `resolucion`/`escalado_a` de la lista (rojo previo observado:
    `AssertionError` listando ambas claves como ya implementadas).
  - `.venv/Scripts/python.exe -m pytest -q` (suite completa, final) → 353 passed
    en 108.47s.
  - `git status --short` / `git diff --stat` → 7 archivos modificados, 2 nuevos
    (`tests/test_bloqueos.py` y este documento); sin commitear, según lo pactado.

## Corrección tras revisión

- 2026-09-22: la revisión del padre encontró dos defectos y un chequeo
  faltante sobre el trabajo de T1/T2 de arriba. Corregidos con TDD estricto
  (rojo observado por comportamiento real contra Postgres, no supuesto).
  Suite completa: **356 passed** (353 + 3 pruebas nuevas, cero regresiones).
  Sin commits, sin lectura de `.env*`, sin SQL destructivo fuera de fixtures.

  **Defecto 1 — migración faltante (bloqueante).** `estado_previo_a_bloqueo`
  sólo existía en `db/esquema.sql`. Por `db/migrations/README.md`,
  `esquema.sql` es la fuente para bases limpias de prueba nada más: una base
  existente (CoreWork) se actualiza con `db/migrations/`, no con
  `esquema.sql`. Contra esa base real, `resolver_bloqueo` habría fallado con
  "function does not exist".
  - Agregados `db/migrations/0007_blocker_resolution.sql` (nombrado en
    secuencia con 0003–0006) y su rollback en `db/rollbacks/0007_blocker_resolution.sql`
    — **no** en `db/migrations/rollback/` como sugería el mensaje de revisión:
    la convención real del repo, confirmada en `db/README.md` y en el propio
    directorio, es `db/rollbacks/<mismo nombre>`. Misma estructura que
    0004/0006: `\encoding UTF8`, `\set ON_ERROR_STOP on`, chequeo de
    codificación, `begin`/`commit`, preflight (`prisma_owner` existe, si no
    exige 0004), `alter function ... owner to prisma_owner`, `revoke execute
    ... from public`, `grant execute ... to prisma_app`.
  - Las migraciones se descubren del directorio, no a mano — el trap que
    avisaba el mensaje de revisión (cuatro veces nombradas y desactualizadas):
    usé el mismo mecanismo ya existente, `_migraciones_posteriores_a()` en
    `tests/test_task_intake.py:40`, que hace `sorted((ROOT / "db" /
    "migrations").glob("0*.sql"))`. Por eso `0007` ya quedó ejercitado sin
    tocar código de prueba en:
    - `test_los_rollbacks_devuelven_la_base_al_estado_anterior` (genérica:
      exige que exista el rollback, que la migración cambie algo observable
      — el catálogo de funciones `security definer` cambia solo al agregar
      una — y que el rollback devuelva la base a su estado anterior);
    - `test_instalacion_limpia_y_base_migrada_convergen_en_el_aislamiento`
      (aplica la cadena completa desde 0001 y compara instalación limpia
      contra migrada).
  - Agregada además una prueba específica,
    `test_0007_estado_previo_a_bloqueo_llega_por_migracion_con_dueno_correcto`
    en `tests/test_task_intake.py` (mismo estilo que las otras pruebas de
    migración: base descartable vía `PRISMA_TEST_DB_URL`, `git show` del
    esquema pre-0002, cadena de migraciones aplicada, base borrada al
    terminar): confirma `to_regprocedure` no nulo (la falla original) y que
    el dueño efectivo es `prisma_owner`, `public` sin `execute` y `prisma_app`
    con `execute`, leído del catálogo real, no del texto del archivo.
  - Rojo observado: `AssertionError: estado_previo_a_bloqueo no llegó por la
    cadena de migraciones` (`to_regprocedure(...) is None`) antes de crear
    `0007_blocker_resolution.sql`.

  **Defecto 2 — consulta de estado previo incorrecta (corrección).**
  `estado_previo_a_bloqueo` leía el `estado_anterior` del ÚLTIMO evento de la
  tarea, no del último evento que ENTRÓ a `bloqueada`. `actualizar_estado` no
  exige bloqueos cerrados para salir de `bloqueada` (deuda ya registrada en
  `docs/STATUS.md` "Pendiente": no hay disparador que valide transiciones
  todavía), así que una tarea bloqueada puede salir por ese camino mientras un
  bloqueo sigue abierto. Resolver ese bloqueo después reproducía exactamente
  el escenario que describe el mensaje de revisión.
  - Rojo observado (no el que anticipé por prosa — el real): al ejecutar el
    escenario bloquear → `actualizar_estado` a `en_curso` → resolver, el
    código anterior no dejaba la tarea mal bloqueada silenciosamente: el
    disparador `exigir_bloqueo_abierto` (exige un bloqueo abierto para poder
    *entrar* a `bloqueada`) lo rechazaba de una, porque para el momento en que
    intentaba reinsertar el evento hacia `bloqueada` el único bloqueo ya
    estaba resuelto. Rojo real: `psycopg.errors.RaiseException: No se puede
    bloquear una tarea sin un bloqueo abierto que la explique.` — un choque
    en vez de una corrupción silenciosa, pero sigue siendo un fallo: la
    herramienta debía dejar la tarea en `en_curso` sin reventar.
  - `estado_previo_a_bloqueo` (en `esquema.sql` y en `0007`) agrega `where
    estado_nuevo = 'bloqueada'` a la búsqueda: devuelve el `estado_anterior`
    de la última vez que la tarea entró a `bloqueada`, no de cualquier evento
    posterior.
  - `_resolver_bloqueo` en `src/prisma/herramientas.py` ahora lee
    `task.estado` (columna que `prisma_app` sí puede leer) antes de emitir el
    evento de retorno, y sólo lo emite si la tarea sigue `bloqueada` en este
    momento. Si ya salió por otro camino, resolver el último bloqueo no la
    mueve — se devuelve `{"resuelto": True, "tarea_desbloqueada": False}` sin
    tocar `task_state_event`.
  - Si la tarea sigue `bloqueada` pero la función devuelve `null` (no debería
    ocurrir en el flujo normal — exigiría un primer evento de la tarea que ya
    fuera `bloqueada`, sin bloqueo previo), no se inserta un estado nulo ni se
    asume `asignada` por defecto: se levanta `Denegado`. Como cada llamada a
    una herramienta corre dentro de su propio punto de retorno
    (`cur.connection.transaction(...)` en `agente.py:173`), la excepción
    deshace también el `update blocker set resuelto_en = ...` ya ejecutado —
    la resolución del bloqueo no queda a medias.
  - Prueba de regresión agregada:
    `test_resolver_bloqueo_no_reingresa_a_bloqueada_si_ya_salio_por_otro_camino`
    en `tests/test_bloqueos.py`: bloquear → `actualizar_estado` a `en_curso` →
    resolver → la tarea queda en `en_curso`, sin evento nuevo hacia
    `bloqueada` (se cuenta 1 solo evento `estado_nuevo = 'bloqueada'`: el de
    entrada original).

  **Defecto 3 — chequeo de aislamiento faltante (invariante #1 de
  AGENTS.md).** Agregada
  `test_estado_previo_a_bloqueo_respeta_el_aislamiento_entre_espacios` en
  `tests/test_bloqueos.py`, con la fixture de dos espacios `intake_world`:
  llama `estado_previo_a_bloqueo` con el id de una tarea del espacio B desde
  una sesión acotada al espacio A y confirma que devuelve `null`. A diferencia
  de los otros dos defectos, esta prueba **pasó en verde ya en su primera
  corrida**, sin cambiar código de producción: la RLS forzada sobre
  `task_state_event` y `prisma_owner nobypassrls` ya contenían el caso. No fue
  un defecto en sí — era un chequeo que faltaba para dejarlo demostrado en vez
  de asumido, que es exactamente lo que pedía el pedido de revisión. Se
  registra igual como evidencia honesta: no todo lo señalado por la revisión
  resultó ser un bug de producción.

  **Comandos ejecutados:**
  - `.venv/Scripts/python.exe -m pytest -q tests/test_task_intake.py -k
    test_0007_estado_previo_a_bloqueo_llega_por_migracion_con_dueno_correcto`
    → rojo (`AssertionError: estado_previo_a_bloqueo no llegó por la cadena de
    migraciones`) antes de `0007_blocker_resolution.sql`; verde después.
  - `.venv/Scripts/python.exe -m pytest -q tests/test_bloqueos.py -k
    "no_reingresa or estado_previo_a_bloqueo_respeta"` → rojo
    (`psycopg.errors.RaiseException`) antes de la corrección de
    `_resolver_bloqueo`/`estado_previo_a_bloqueo`; verde después (la prueba de
    aislamiento ya estaba en verde desde su primera corrida).
  - `.venv/Scripts/python.exe -m pytest -q
    tests/test_task_intake.py::test_los_rollbacks_devuelven_la_base_al_estado_anterior
    tests/test_task_intake.py::test_instalacion_limpia_y_base_migrada_convergen_en_el_aislamiento
    tests/test_task_intake.py::test_ninguna_funcion_elevada_pertenece_a_un_rol_que_ignora_la_rls`
    → 3 passed: la cadena genérica de migraciones/rollbacks ya ejercita 0007
    sin código de prueba dedicado.
  - `.venv/Scripts/python.exe -m pytest -q` (suite completa, final) → **356
    passed** en 124.45s.
  - `git status --short` → 8 archivos modificados, 4 nuevos (`db/migrations/
    0007_blocker_resolution.sql`, `db/rollbacks/0007_blocker_resolution.sql`,
    `tests/test_bloqueos.py`, este documento); sin commitear.
