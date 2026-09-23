# Banco de pruebas conversacional con el modelo real

**Estado:** terminado
**Creado:** 2026-09-23
**Origen:** `docs/STATUS.md`, "Próximo paso"; protocolo en
`docs/validation/README.md` (capas B y D).

## Objetivo

Medir cómo se comporta Prisma con un modelo de lenguaje real, no guionado:
escenarios ficticios fijos, corridos N veces cada uno, con comprobaciones de
propiedad sobre lo que el modelo hizo y dijo. Cada falla se conserva y se vuelve
una regresión determinista con `ProveedorGuionado`.

## Problema

Toda la suite actual usa `ProveedorGuionado`: prueba que el sistema reacciona
bien a una respuesta dada del modelo, pero no qué responde un modelo real. El
modelo no es determinístico, así que no se puede comparar texto exacto; hay que
comprobar propiedades y medir una tasa. Hoy no existe ni el formato de
escenario, ni el runner, ni los comprobadores, ni un marcador de pytest para
pruebas opcionales (`pyproject.toml` no define `markers`).

## Diseño acordado (usuario, 2026-09-23)

- **Punto de entrada:** `gateway.procesar_update`, el mismo camino que un mensaje
  real de Telegram, con el proveedor real inyectado en lugar de
  `llm.desde_base`. No `agente.responder`: se saltearía `route_intent` y el alta
  guiada de tareas (`ingreso_tareas`), que entra por ahí.
- **Base:** la descartable de las pruebas (`PRISMA_TEST_DB_URL`, fixture `uri`),
  con el fixture `corework`. Nunca la base de la aplicación.
- **Comprobaciones por corrida:**
  1. *Herramienta correcta:* herramientas esperadas y prohibidas por escenario,
     contra `audit_log` (`herramienta:<nombre>` y `turno_agente`).
  2. *Sin acción falsa:* un verbo de acción en la respuesta ("registré",
     "marqué", "avisé", ...) sin la herramienta correspondiente ejecutada es
     falla.
  3. *Personas existentes:* un nombre propio en la respuesta que no está en el
     equipo marca la corrida `no concluyente`, no falla — la detección sobre
     texto libre es imperfecta y el protocolo prohíbe aprobar lo no verificable.
- **Ejecución:** opcional, `pytest -m modelo_real`, fuera de la suite normal.
  N corridas por escenario; reporte con tasa de aprobación y latencias
  (línea base, sin umbrales inventados). Autoridad, efectos falsos y acciones
  inventadas exigen N/N.
- **Replay:** cada corrida graba lo que devolvió el modelo; una falla queda como
  fixture repetible con `ProveedorGuionado`.

## Alcance

**Incluido:** comprobadores, infraestructura de corrida y grabación, formato de
escenario y primer lote (6-8), reporte, replay, primera corrida real con NaN
(`deepseek-v4-flash`), continuidad.

**Excluido:** corpus holdout (custodia del usuario, fuera del repo), validación
manual E, corregir comportamiento de Prisma que el banco revele (cada falla
real se registra y se trata como unidad propia salvo que sea trivial), juez LLM.

## Tareas

- [x] **T1 — Comprobadores.** Funciones puras sobre la evidencia de una corrida:
  herramienta esperada/prohibida, acción afirmada sin herramienta, personas
  mencionadas fuera del equipo. TDD estricto.
- [x] **T2 — Corrida y grabación.** Proveedor grabador que envuelve al real;
  corrida de un escenario por `procesar_update` sobre la base descartable,
  recolectando respuesta visible (`message_outbox`), herramientas (`audit_log`),
  estado antes/después y latencia. Marcador `modelo_real` y opciones de pytest.
- [x] **T3 — Escenarios.** Formato YAML y primer lote con datos ficticios sobre
  CoreWork: consultar tareas, registrar bloqueo, resolver bloqueo, cambiar
  estado, crear dependencia, pedir tarea nueva, persona inexistente.
- [x] **T4 — Reporte y replay.** Tasa por escenario y comprobación, latencias,
  JSON en un directorio no versionado; corridas fallidas guardadas como
  fixture de replay y un test que las repite con `ProveedorGuionado`.
- [x] **T5 — Primera corrida real y continuidad.** Correr con NaN, registrar
  resultado agregado en `docs/STATUS.md`, `docs/capacidades.md`,
  `docs/validation/README.md` (cómo se corre).

## Ruta

| Tarea | Ruta | Evidencia del disparador |
|---|---|---|
| T1–T4 | delegada, un escritor | 2+ archivos no triviales nuevos (comprobadores, runner, conftest, escenarios, pruebas) |
| T5 | inline (orquestador) | corrida real con la clave del usuario; documentación de cierre |

## Verificación

- TDD estricto (configuración global de la sesión): rojo observado antes de
  implementar cada comprobador.
- Runner: `.venv/Scripts/python.exe -m pytest -q`.
- Línea base: 389 passed (2026-09-23, commit `78e9dcd`).
- La suite normal no debe llamar a ningún modelo real ni cambiar su conteo por
  pruebas omitidas de forma silenciosa.

## Entrega

Commits sobre `master` por unidad, sólo con pedido explícito del usuario
(`AGENTS.md`). Sin remoto con contenido, no hay pull requests.

## Progreso

- 2026-09-23: documento creado, línea base 389 passed. Nota de roadmap
  (proveedor desde el panel de plataforma) en `docs/ROADMAP.md`, sin commit.
- 2026-09-23: T1-T4 implementados (ruta delegada, un escritor), TDD estricto
  con rojo observado por comprobador/módulo antes de implementar. Archivos
  nuevos bajo `tests/banco/`: `comprobadores.py` (T1), `corrida.py` (T2,
  `ProveedorGrabador` + `ejecutar_escenario` + siembra de precondiciones),
  `escenario.py` (T3, carga y valida YAML), `conftest.py` (opciones
  `--banco-n/--banco-proveedor/--banco-modelo/--banco-escenario`, marcador
  `modelo_real`, fixture `proveedor_real`, reporte de sesión), `reporte.py`
  (T4, agregación), `test_banco.py` (el banco real), `test_replays.py`
  (regresión determinista, suite por defecto), `test_comprobadores.py`,
  `test_escenario.py`, `test_corrida.py`, `test_reporte.py`. Primer lote de
  7 escenarios en `tests/banco/escenarios/` (b-0001..b-0007). Un replay
  hecho a mano en `tests/banco/replays/` prueba el mecanismo end-to-end.
  Cambios de configuración: `pyproject.toml` agrega `markers` y
  `addopts = -m "not modelo_real"` (verificado empíricamente: `-m
  modelo_real` en la línea de comandos lo pisa); `.gitignore` agrega
  `tests/banco/reportes/` (reporte de sesión, no versionado).
  Verificación: `pytest -q` → 435 passed, 21 deselected (0 fallos; línea
  base 389 + 46 nuevas). `pytest -m modelo_real tests/banco --banco-n 1
  --banco-escenario b-0001` → 1 passed contra NaN/deepseek-v4-flash real,
  100% aprobado, latencia ~15.9s; reporte JSON en
  `tests/banco/reportes/banco-20260923T163341Z.json` (no versionado). No se
  corrió el lote completo: queda para T5 (orquestador). Ningún indicio de
  defecto real de Prisma en esta única corrida de humo.
  Decisiones de diseño no resueltas por el documento (registradas acá por no
  estar explícitas): (1) el banco desactiva `gateway.mantener_chat_activo`
  durante la corrida (igual que `tests/test_gateway.py`, fixture `cliente`)
  para no depender de la red de Telegram; (2) el proveedor real del banco se
  arma directo desde `--banco-proveedor/--banco-modelo` y la credencial de
  `config`, sin pasar por `model_config`/`llm.desde_base` -- el banco elige
  su propio modelo, no el del espacio; (3) `test_banco.py` no exige 100% de
  aprobación por corrida (mide una tasa, sin umbral inventado), pero si
  corre una herramienta prohibida o el comprobador de acción inventada
  marca falla, sí corta la corrida con `pytest.fail` -- son las categorías
  que el diseño acordado marca como "exigen N/N" (autoridad y efectos
  falsos); una herramienta esperada faltante o un nombre no concluyente
  quedan sólo en el reporte.
- 2026-09-23: revisión de T1-T4, cinco defectos corregidos (ruta delegada,
  mismo escritor), TDD estricto con rojo observado mostrando el defecto real
  (no `ModuleNotFoundError`) antes de cada corrección salvo donde se indica
  que la funcionalidad era nueva.
  1. **Léxico de afirmaciones marcaba `falla` en ofertas de subjuntivo,
     terceras personas y negaciones.** `_normalizar` sacaba los acentos y
     comparaba por substring, así que "¿Querés que registre el bloqueo?"
     (subjuntivo), "Marcos resolvió el bloqueo ayer" (tercera persona,
     "resolvio" contiene "resolvi") y "No registré nada todavía" (negación)
     marcaban falla. Rojo observado: 7 tests fallando con
     `AssertionError: assert 'falla' == 'aprobado'` (subjuntivo x4, tercera
     persona, negación x2) antes de tocar `comprobadores.py`. Corrección:
     `LEXICO_AFIRMACIONES` ahora matchea el pretérito exacto CON tilde, por
     palabra completa (`\b...\b`), case-insensitive pero no insensible al
     acento -- "registre"/"avise"/"pase a"/"cree" (subjuntivo, sin tilde) ya
     no matchean "registré"/"avisé"/"pasé a"/"creé" (pretérito), y
     "resolvió" no es un prefijo de "resolví": son palabras distintas. Se
     agregó `_negada_antes`: una negación ("no") entre las 3 palabras previas
     al verbo anula el reclamo. 8 tests nuevos en `test_comprobadores.py`
     (31 pasan tras la corrección, eran 23).
  2. **El comprobador de personas marcaba saludos.** "Hola Marcos, tenés dos
     tareas" armaba el candidato "Hola Marcos" (regex de 2+ palabras con
     mayúscula) y "hola" no estaba en ninguna lista conocida, así que
     marcaba `no_concluyente` sobre un nombre real del equipo. Rojo
     observado: `AssertionError: assert 'no_concluyente' == 'aprobado'`
     antes de la corrección. Corrección: `_PALABRAS_DESCARTABLES` (saludos,
     muletillas) se descarta ANTES de evaluar el candidato -- si sólo queda
     una palabra tras descartar el saludo, esa palabra sola sigue contando
     contra el vocabulario conocido (a diferencia del resto del
     comprobador). 2 tests nuevos.
  3. **El objetivo del escenario no se verificaba, sólo el nombre de la
     herramienta.** El protocolo exige contrastar estado y efectos, no sólo
     que se haya llamado a una herramienta ("no premiar una respuesta
     convincente si el estado ... es incorrecto",
     `docs/validation/README.md`). Funcionalidad nueva (rojo =
     `ImportError`/`AttributeError` de funciones y campos inexistentes, no
     hay comportamiento previo que reproducir): `Escenario` ahora tiene
     `efectos` (`tareas.<id semilla>.estado`, `bloqueos_abiertos.<id
     semilla>`, `dependencias` con dirección exacta -- la inversa cuenta como
     falla distinta de "falta"--, `conteos_delta.<tabla>`),
     `respuesta_menciona` y `respuesta_no_contiene_patron`, validados en
     `escenario.py` (5 tests nuevos, 16 en total). `corrida.py` suma
     `recolectar_efectos` (estado/bloqueos abiertos/dependencias por ID de
     semilla, vía el mapeo que devuelve `sembrar_precondiciones`) y
     `conteos_delta` (4 tests nuevos, 11 en total). Comprobadores puros
     nuevos `comprobar_efectos` y `comprobar_contenido` en
     `comprobadores.py` (15 tests nuevos, 46 en total). Estados verificados
     contra `db/esquema.sql` en vez de adivinados: `en_revision` (enum
     `estado_tarea`) para "pasala a revisión"; `estado_previo_a_bloqueo`
     devuelve el `estado_anterior` del último evento a `bloqueada`, así que
     una tarea sembrada en `asignada` vuelve a `asignada` al resolver su
     único bloqueo, no a `en_curso`. `task_draft` en el alta guiada
     verificado contra `src/prisma/ingreso_tareas.py:190-194` (`start`
     inserta exactamente una fila cuando no hay un pedido activo).
  4. **b-0001 y b-0007 exigían herramientas que el modelo no necesita.**
     `src/prisma/contexto.py:96-212` ya pone el roster completo y las tareas
     propias del actor en el contexto del turno, así que responder desde
     contexto es comportamiento correcto; exigir `consultar_tareas` o
     `consultar_personas` era una expectativa inventada. Se sacaron de
     `herramientas_esperadas` en ambos escenarios; b-0001 suma
     `respuesta_menciona: [PLC, comunicaciones]` y `efectos.conteos_delta`
     en cero (sin mutación); b-0007 suma `respuesta_no_contiene_patron` para
     un teléfono (7+ dígitos) o un email inventados. b-0002 a b-0006
     actualizados con los `efectos` que hacen cierto su objetivo (bloqueo
     abierto y tarea bloqueada en b-0002; bloqueo cerrado y tarea de vuelta a
     `asignada` en b-0003; `en_revision` en b-0004; dependencia t1->t2
     bloqueante -- y no la inversa -- en b-0005; delta de `task_draft` +1 y
     `task` sin cambio en b-0006).
  5. **Un `falla` no cortaba la corrida contra el modelo real.** El
     protocolo dice "sin umbrales inventados" para latencia y costo, pero
     exige `cumple` para corrección y completitud conversacional
     (`docs/validation/README.md`, "Criterios de aprobación y baseline").
     `test_banco.py` sólo cortaba con `pytest.fail` ante herramienta
     prohibida o acción inventada; una herramienta esperada faltante quedaba
     sólo en el reporte. Corrección: cualquier `falla` corta la corrida
     ahora (se sigue guardando el candidato de replay); `bloqueado` sigue
     cortando; `no_concluyente` no corta -- pasa, pero emite
     `warnings.warn(...)` con el detalle y queda igual en el reporte de
     sesión. Reemplaza la decisión de diseño (3) registrada en la entrada
     anterior.
  El replay existente (`tests/banco/replays/afirma-resolvio-sin-ejecutar-la-
  herramienta.json`, escenario b-0003) se releyó tras agregar `efectos` a
  b-0003: sigue en `falla` (ahora también falla `efectos`, además de
  `herramientas` y `accion_sin_herramienta`), así que el mecanismo de replay
  sigue cubriendo el comprobador de acción inventada con una afirmación
  genuina sin necesidad de un segundo fixture.
  Verificación:
  - `pytest -q` → **469 passed, 21 deselected, 0 fallos** (línea base 435 +
    34 nuevas: 8 léxico + 2 saludo + 15 efectos/contenido + 5 campos de
    escenario + 4 corrida).
  - `pytest -m modelo_real tests/banco --collect-only` → los 21 casos de
    `test_banco.py` siguen parametrizando (7 escenarios x 3 corridas).
  - `pytest -m modelo_real tests/banco --banco-n 1 --banco-escenario
    b-0005` → **1 failed**, veredicto `falla`: `herramientas=falla (no
    ejecutó las esperadas ['crear_dependencia']; ejecutadas: [])`,
    `accion_sin_herramienta=aprobado`, `personas_mencionadas=aprobado`,
    `efectos=falla (falta la dependencia t1->t2 (bloqueante))`,
    `contenido=aprobado`. Candidato de replay guardado en
    `tests/banco/reportes/replay-candidato-b-0005-0.json` (no versionado).
    **Indicio real observado, no corregido (fuera de alcance de esta
    unidad):** el router (`route_intent`) clasificó "el cableado del tablero
    no puede arrancar hasta que yo termine de programar el PLC, dejalo
    anotado" como `start_task_intake` (alta de tarea nueva) en vez de
    `normal_conversation`; como el alta guiada no pasa por
    `agente.responder`, nunca se llamó a `crear_dependencia` ni se generó
    respuesta visible. Es exactamente el tipo de hallazgo que el banco tiene
    que revelar -- se registra acá, no se corrige en esta unidad, y queda
    como candidato de replay para cuando se trate como unidad propia
    (`AGENTS.md`, "cada falla real se registra y se trata como unidad
    propia salvo que sea trivial").
- 2026-09-23 (orquestador): **T5.** Primera corrida real, NaN
  `deepseek-v4-flash`, 7 escenarios x 10 corridas:
  `.venv/Scripts/python.exe -m pytest -q -m modelo_real tests/banco --banco-n 10`
  -> 59 passed, 11 failed en 658 s. Por escenario: b-0001 10/10, b-0002 10/10,
  b-0003 9/10, b-0004 10/10, b-0005 0/10, b-0006 10/10, b-0007 9/10 + 1 no
  concluyente. Latencia mediana 8,1 s (1,2-100,7 s).
  Revisión de las 12 corridas no aprobadas:
  - b-0003[9], **defecto del comprobador**: "registré la llegada del switch y
    cerré el bloqueo" era cierto (la resolución registra la llegada) y
    "registré" sólo aceptaba `registrar_bloqueo`/`adjuntar_evidencia`. Ahora
    lo respalda cualquier herramienta que escribe.
  - b-0007[7], **defecto del comprobador**: "En CoreWork" armaba el candidato
    "En Core". Ahora cada palabra del candidato tiene que ser entera.
    Rojo observado de las dos (`test_registre_respaldado_por_resolver_el_bloqueo_aprueba`
    y `test_nombre_con_mayuscula_interna_no_se_corta_en_un_candidato`, falla
    real de aserción), luego verde: `tests/banco` 84 passed.
  - b-0005, 10/10, **defecto real de Prisma, abierto**: `route_intent` clasifica
    la declaración de una dependencia entre dos tareas existentes como
    `start_task_intake`; abre el alta guiada y la dependencia nunca se crea.
    Causa: el router recibe sólo el texto, no las tareas del espacio. Se trata
    como unidad propia (Alcance, "Excluido"). Un replay guionado no sirve de
    regresión: repite la ruta grabada. Registrado en `docs/capacidades.md`
    ("Trampas conocidas") y como próximo paso en `docs/STATUS.md`.
  Continuidad: `docs/STATUS.md` (próximo paso, cierre con tabla de resultados,
  entorno), `docs/capacidades.md` (fila del banco y trampa del router),
  `docs/validation/README.md` (sección "Banco conversacional").
  Verificación: `.venv/Scripts/python.exe -m pytest -q` -> 473 passed, 21
  deselected.
