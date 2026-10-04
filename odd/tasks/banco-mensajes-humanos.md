# Banco con mensajes humanos reales y ambigüedad

> **Nota del 2026-10-04.** Este documento es anterior al Motor, la línea de trabajo vigente. Lo que
> figure acá como en curso, pendiente o próximo paso no se retoma sin una decisión del usuario. El
> orden de trabajo vigente está en [`docs/STATUS.md`](../../docs/STATUS.md).

**Estado:** en pausa (2026-09-23, por decisión del usuario)
**Creado:** 2026-09-23
**Origen:** pedido del usuario tras la primera corrida del banco
(`odd/tasks/banco-conversacional.md`); protocolo `docs/validation/README.md`, capa B
("vago, incompleto, con errores, cambios de opinión, referencias contextuales,
contradicciones... sin identificadores").

## Objetivo

Medir cómo interpreta Leda mensajes escritos como los escribe una persona real
—faltas de ortografía, abreviaturas, sin tildes, nombres mal escritos, frases
ambiguas— y, sobre todo, si ante una ambigüedad real **frena y pregunta** o adivina
y ejecuta. Es la línea base para diseñar la aclaración con botones.

## Problema

Los escenarios `b-0001`..`b-0007` están bien escritos. Su 10/10 mide a Leda con
mensajes limpios, que no es el uso real. El banco tampoco tiene una comprobación de
"ante la duda, preguntó en vez de actuar".

## Decisión del usuario (2026-09-23)

- La ambigüedad es la parte que más cuesta ajustar de Leda y hay que frenarla.
- Solución deseada, a diseñar en una unidad posterior: ante la duda, Leda ofrece
  botones con las interpretaciones posibles (texto corregido de lo que la persona
  quiso decir), más un botón "ninguna de las anteriores" que permite escribir.
- Orden: primero medir con el banco (esta unidad), después diseñar la aclaración
  con botones (ADR, porque es comportamiento del núcleo) y medirla contra esta
  línea base.

## Alcance

**Incluido:** variantes desprolijas de los escenarios existentes, escenarios de
ambigüedad genuina, comprobación "debe preguntar", agrupación de variantes en el
reporte, corrida real y registro de la línea base.

**Excluido:** construir la aclaración con botones; corregir el router (`b-0005`,
unidad propia); mensajes aportados por el usuario (se suman cuando los pase).

## Tareas

- [x] **T1 — Formato.** Campo `variante_de` (agrupa en el reporte) y
  `debe_preguntar` (comprobación nueva: ningún efecto y la respuesta pregunta o
  ofrece opciones). TDD.
- [x] **T2 — Variantes desprolijas.** 2-3 por escenario existente.
- [x] **T3 — Ambigüedad genuina.** Escenarios donde lo correcto es preguntar.
- [ ] **T4 — Corrida real y línea base.** N=10, registro en `docs/STATUS.md`.

## Ruta

| Tarea | Ruta | Evidencia del disparador |
|---|---|---|
| T1–T3 | delegada, un escritor | 2+ archivos no triviales (comprobadores, escenario, reporte, YAML, pruebas) |
| T4 | inline (orquestador) | corrida real y registro |

Investigación en paralelo (sólo lectura, trabajador aparte): técnicas existentes
para detectar ambigüedad y pedir aclaración en asistentes conversacionales.

## Verificación

- TDD estricto; runner `.venv/Scripts/python.exe -m pytest -q`.
- Línea base: 473 passed (2026-09-23, commit `d44a7ce`).

## Progreso

- 2026-09-23: documento creado.
- 2026-09-23: **T1-T3 implementados** (ruta delegada, un escritor). TDD
  estricto: rojo genuino observado antes de cada implementación --
  `ImportError`/`AttributeError`/"DID NOT RAISE" para funcionalidad nueva
  (`comprobar_pregunta`, `respuesta_ofrecio_opciones`, `filas_respuesta`,
  campos `variante_de`/`debe_preguntar`/`permite_borrador_de_tarea`,
  agrupación por `grupos` en el reporte), nunca `ModuleNotFoundError`.

  **T1 -- formato y comprobación nueva.**
  - `tests/banco/escenario.py`: `Escenario` suma `variante_de: str | None`,
    `debe_preguntar: bool`, `permite_borrador_de_tarea: bool`.
    `_validar_estructura` valida tipo (texto no vacío / booleano);
    `cargar_escenarios` valida además que `variante_de` referencie un ID
    cargado en el mismo directorio (si no, `EscenarioInvalido`). 8 tests
    nuevos en `test_escenario.py` (24 en total).
  - `tests/banco/comprobadores.py`: `Evidencia` suma `ofrecio_opciones: bool`.
    `comprobar_pregunta(evidencia, *, task_draft_delta=0,
    permite_borrador_de_tarea=False)` aprueba sólo si (a) ninguna
    herramienta de `_HERRAMIENTAS_QUE_ESCRIBEN` corrió y abrir un
    `task_draft` no cuenta como acción permitida salvo que el escenario lo
    declare, y (b) la respuesta visible contiene "?" u
    `evidencia.ofrecio_opciones` es verdadero. Si (a) falla: `falla` "actuó
    sin preguntar"; si (a) se cumple pero (b) falla: `falla` "no actuó pero
    tampoco preguntó". 8 tests nuevos (58 en total).
  - **Cómo se detecta que Leda ofreció una elección con botones**: la fila
    de `message_outbox` de la respuesta tiene `pending_action_id` no nulo
    (confirmación o elección, `src/leda/agente.py`
    `_encolar_confirmacion`:236-257 / `_encolar_eleccion`:260-279, que
    llaman `enqueue_outbox` con ese id) o `intake_choice_set_id` no nulo
    (alta guiada de tarea, `src/leda/ingreso_tareas.py`
    `_open_choices`:785-811). Es la misma condición que arma los botones al
    despachar (`src/leda/despachador.py::_botones`:192-214) y la que fija
    `has_buttons` en `src/leda/salida.py::enqueue_outbox`:151-176. Nueva
    consulta pura en `tests/banco/corrida.py`: `filas_respuesta(cur, ws,
    chat, ids_previos)` trae `id, cuerpo, pending_action_id,
    intake_choice_set_id` de las filas nuevas de `message_outbox`;
    `respuesta_ofrecio_opciones(filas)` es la función pura que decide.
    `ResultadoCorrida` suma `ofrecio_opciones: bool`, recolectado en
    `ejecutar_escenario`. 5 tests nuevos en `test_corrida.py` (17 en
    total): 4 puros + una prueba directa contra el esquema real (inserta un
    `pending_action`/`message_outbox` con `admin(conn)` y confirma que
    `filas_respuesta` trae la columna).
  - `tests/banco/reporte.py`: `armar_reporte` suma el parámetro opcional
    `variantes: dict[id -> variante_de o None]` y agrega `"grupos"` al
    reporte -- corridas, aprobados y tasa de aprobación por grupo (un
    escenario base y todas sus variantes, o el escenario solo si no tiene
    ninguna). `resumen_texto` imprime una sección "grupos (base +
    variantes)" sólo para los grupos con más de un escenario. `tests/banco/
    conftest.py::pytest_sessionfinish` recarga los escenarios para armar el
    mapa `variantes` antes de llamar `armar_reporte` (el reporte de sesión
    junta corridas de todos los escenarios recién al final). 4 tests nuevos
    en `test_reporte.py` (10 en total).
  - `test_banco.py` y `test_replays.py`: `Evidencia` recibe
    `ofrecio_opciones=resultado.ofrecio_opciones`; si
    `escenario.debe_preguntar`, se agrega `comprobar_pregunta(...)` a la
    lista de comprobaciones (con `task_draft_delta` desde
    `efectos_observados["conteos_delta"]` y
    `escenario.permite_borrador_de_tarea`). El replay queda cubierto por el
    mismo camino: no hizo falta un fixture nuevo para probarlo porque no hay
    todavía ninguna corrida `debe_preguntar` no aprobada que promover a
    replay.

  **T2 -- 18 variantes desprolijas** (`variante_de` apunta al escenario
  base; mismas precondiciones, `herramientas_esperadas/prohibidas` y
  `efectos` que la base -- sólo cambia la redacción): `b-0001-a`, `b-0001-b`
  (2); `b-0002-a`, `b-0002-b`, `b-0002-c` (3); `b-0003-a`, `b-0003-b` (2);
  `b-0004-a`, `b-0004-b`, `b-0004-c` (3); `b-0005-a`, `b-0005-b` (2, b-0005
  sigue fallando 10/10 por el defecto de router ya registrado -- las
  variantes están para ver si la redacción influye); `b-0006-a`,
  `b-0006-b`, `b-0006-c` (3); `b-0007-a`, `b-0007-b`, `b-0007-c` (3).
  Mensajes reales de `espacios/corework.yaml` (Marcos Tarquini, Nahuel
  Gimenez), estilo mensaje de WhatsApp de mantenimiento industrial
  argentino (sin tildes, abreviaturas "q"/"tmb"/"x"/"pa", typos, muletillas,
  referencias parciales), variado entre variantes -- ninguna acumula todos
  los defectos a la vez.

  **T3 -- 5 escenarios de ambigüedad genuina** (`debe_preguntar: true`,
  `herramientas_prohibidas` con las 8 herramientas que escriben,
  `efectos.conteos_delta` en 0 para las tablas mutables, `objetivo`
  describe la ambigüedad para el evaluador):
  - `b-0008`: dos tareas abiertas de "tablero" del mismo actor (Marcos
    Tarquini) -- "ya termine lo del tablero, pasala a revision".
  - `b-0009`: referencia a "mar", que matchea a Marcos Tarquini o Mariano
    Naim (los dos con una tarea que plausiblemente frena la de quien
    escribe, Nahuel Gimenez) -- "lo mio depende de q mar termine su parte,
    dejalo anotado".
  - `b-0010`: "lo del plc esta parado" -- puede ser un bloqueo nuevo o sólo
    una descripción de estado, sobre una tarea sin bloqueo abierto (Marcos
    Tarquini).
  - `b-0011`: mensaje que se retracta a sí mismo y termina en duda explícita
    -- "pasala a revision, no, mejor dejala como esta... bah no se" (Marcos
    Tarquini).
  - `b-0012`: dos bloqueos abiertos del mismo actor (Marcos Tarquini) en
    tareas distintas -- "ya se solucionó, dalo por resuelto".

  **Verificación:**
  - `.venv/Scripts/python.exe -m pytest -q` -> **499 passed, 90 deselected,
    0 fallos** (línea base 473; +26 de T1, 90 deselected = 30 escenarios x 3
    corridas del banco, antes 7 x 3 = 21).
  - `.venv/Scripts/python.exe -m pytest -m modelo_real tests/banco
    --collect-only -q` -> 90/200 recolectados (110 deselected): los 30
    escenarios (7 base + 18 variantes + 5 de ambigüedad) parametrizan.
  - Humo real (NaN/deepseek-v4-flash), un escenario de ambigüedad, N=1:
    `.venv/Scripts/python.exe -m pytest -q -m modelo_real tests/banco
    --banco-n 1 --banco-escenario b-0008` -> **1 passed**, veredicto
    `aprobado`: `herramientas=aprobado`, `accion_sin_herramienta=aprobado`,
    `personas_mencionadas=aprobado`, `efectos=aprobado`,
    `contenido=aprobado`, `pregunta=aprobado`. Respuesta visible: "¿Cuál de
    las dos? Tenés abiertas "Cablear tablero de la máquina 3" y "Revisar
    tablero de la máquina 4". Decime cuál paso a revisión.\n\nY si tenés
    algo para respaldar el trabajo — captura, archivo o el detalle de lo
    que quedó hecho — pasámelo y lo registro junto con la tarea." Leda
    frenó, no ejecutó ninguna herramienta y preguntó cuál de las dos tareas
    -- exactamente el comportamiento que T3 mide. Reporte de sesión
    (`tests/banco/reportes/`, no versionado, borrado tras la verificación).
    No se corrió el lote completo (queda para T4, orquestador).

  **Decisiones no resueltas explícitamente por el documento, registradas
  acá:**
  1. `comprobar_pregunta` sólo se agrega a la lista de comprobaciones cuando
     `escenario.debe_preguntar` es verdadero -- para el resto de los
     escenarios (p. ej. b-0002, que legítimamente llama `registrar_bloqueo`
     sin preguntar) esa comprobación no tiene sentido y correr igual
     marcaría `falla` sobre un comportamiento correcto.
  2. `_HERRAMIENTAS_QUE_ESCRIBEN` (ya existente en `comprobadores.py`, T1
     del feature doc lo pide reutilizar) no incluye las herramientas de sólo
     consulta (`consultar_tareas`, `consultar_personas`,
     `consultar_bloqueos`): usarlas para resolver la ambigüedad antes de
     preguntar no cuenta como "actuó".
  3. La agrupación por `grupos` en el reporte vive en `armar_reporte`
     (parámetro `variantes`), no en `EntradaReporte`: la entrada de una
     corrida no necesita saber si es variante de otra, sólo el armado del
     reporte de sesión, que ya tiene que recargar los escenarios para el
     resto de los metadatos.
  4. Ningún tool del modelo (`REGISTRO` en `herramientas.py`) usa hoy las
     acciones de `REQUIEREN_CONFIRMACION` (`autoridad.py`), así que
     `NecesitaConfirmacion`/`_encolar_confirmacion` nunca dispara en la
     práctica todavía -- se deja constancia porque afecta qué mecanismos de
     "ofrecer opciones" son alcanzables hoy por un escenario del banco (en
     la práctica, sólo el alta guiada de tarea puede poner
     `intake_choice_set_id`; `pending_action_id` en la elección de
     responsable ambiguo de `crear_borrador_tarea` tampoco es alcanzable
     desde una conversación normal, sólo desde el alta guiada). Los
     escenarios de T3 miden si Leda pregunta por **texto libre** ("?"),
     que es el único mecanismo hoy disponible en `normal_conversation` --
     coherente con el objetivo del feature doc de medir la línea base antes
     de diseñar la aclaración con botones.
- 2026-09-23 (orquestador): **T4 en pausa por decisión del usuario.** La línea
  base (30 escenarios x 10) se cortó a mitad: "primero definamos la solución
  correcta antes de seguir a ciegas". El diseño quedó en
  `docs/architecture/interpretacion-y-confirmacion.md`; la línea base con
  mensajes desprolijos se corre cuando ese diseño esté listo para comparar.
  T1-T3 quedan implementados y sin commit (499 passed). Quedó una base de
  prueba huérfana de la corrida cortada (`leda_test_b872c563a03b`).
