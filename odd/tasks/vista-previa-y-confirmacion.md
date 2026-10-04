# Vista previa y confirmación para todo cambio

> **Nota del 2026-10-04.** Este documento es anterior al Motor, la línea de trabajo vigente. Lo que
> figure acá como en curso, pendiente o próximo paso no se retoma sin una decisión del usuario. El
> orden de trabajo vigente está en [`docs/STATUS.md`](../../docs/STATUS.md).

**Estado:** cerrada
**Creado:** 2026-09-24
**Origen:** [`ADR 0005`](../../docs/decisions/0005-interpretacion-y-confirmacion.md),
decisiones 1 y 2; diseño en `docs/architecture/interpretacion-y-confirmacion.md`.

## Objetivo

Que ningún cambio relevante se aplique sin que la persona vea exactamente qué va a
pasar y lo confirme. Es la protección principal contra una mala interpretación.

## Problema (mapa verificado, 2026-09-24)

- Las 8 herramientas que escriben (`registrar_bloqueo`, `resolver_bloqueo`,
  `actualizar_estado`, `crear_dependencia`, `quitar_dependencia`,
  `adjuntar_evidencia`, `aprobar_tarea`, `crear_objetivo`) ejecutan directo.
  Ninguna está en `REQUIEREN_CONFIRMACION` (`autoridad.py:56`).
- Ya existe un camino de confirmación genérico: `NecesitaConfirmacion` →
  `agente._encolar_confirmacion` → `pending_action` con opciones de un solo uso,
  dueño y vencimiento (8 h) → toque → `resolver_pendiente` (SQL atómico: doble
  toque, vencida, ajena) → `H.ejecutar(..., ya_confirmada=True)`, que revalida
  autoridad y relee el estado.
- La vista previa de hoy (`herramientas._resumen`) muestra la descripción de la
  herramienta y los argumentos crudos, no el estado actual frente al nuevo.
- Sólo hay botones Confirmar y Cancelar; no existe Modificar.
- No hay control de "cambió desde la vista previa" (salvo lo que cada handler
  revise por su cuenta).
- Cuatro herramientas validan autoridad dentro del handler
  (`valida_en_handler=True`: `resolver_bloqueo`, `aprobar_tarea`,
  `crear_dependencia`, `quitar_dependencia`): hoy esa validación ocurriría recién
  al confirmar, así que la vista previa podría proponer algo que después se niega.
- Bug: `crear_objetivo` declara la acción `crear_tarea` (`herramientas.py:262`).
- El banco espera efectos directos en el mismo turno.

## Alcance

**Incluido:** vista previa con estado actual y nuevo para las 8 herramientas,
validación de autoridad y reglas antes de mostrar la vista previa, confirmación
obligatoria, control de cambio entre vista previa y confirmación, botón
Modificar, corrección de `crear_objetivo`, banco adaptado, continuidad.

**Excluido:** aclaración con botones-propuesta ante ambigüedad (ADR 0005 punto 3,
unidad siguiente), preguntas de Leda con botones (punto 4), apodos (punto 5),
resolución de referencias (receta 5.1).

## Tareas

- [x] **T1 — Vista previa por herramienta.** Cada una de las 8 herramientas tiene
  una preparación que lee el estado vigente, valida autoridad y reglas (niega
  antes de mostrar si no se puede) y arma una vista previa humana: recurso,
  estado actual, cambio propuesto, "todavía no se aplicó nada". Guarda una huella
  del estado leído.
- [x] **T2 — Confirmación obligatoria.** Las 8 pasan por `pending_action`;
  `crear_objetivo` declara su acción correcta. Al confirmar se recalcula la huella:
  si el estado cambió, no se aplica y se explica. Botones Confirmar / Modificar /
  Cancelar.
- [x] **T3 — Modificar.** Cierra la propuesta sin efecto, pregunta qué cambiar y
  el siguiente mensaje de esa persona en ese chat se interpreta con la propuesta
  anterior como contexto, produciendo una vista previa nueva.
- [x] **T4 — Banco.** El banco confirma las propuestas tocando el botón y
  verifica que antes del toque no hubo ningún efecto.
- [x] **T5 — Continuidad.** `docs/capacidades.md`, `docs/STATUS.md`, diseño §4.5.

## Ruta

| Tarea | Ruta | Evidencia del disparador |
|---|---|---|
| T1–T2 | delegada, un escritor | 2+ archivos no triviales (`herramientas.py`, `agente.py`, `autoridad.py`, `pendientes.py`, `gateway.py`, pruebas) |
| T3 | delegada, un escritor | `gateway.py`, `agente.py`, `pendientes.py`, esquema, pruebas |
| T4 | delegada, un escritor | `tests/banco/` |
| T5 | inline | documentación |

## Verificación

- TDD estricto (configuración de la sesión); runner
  `.venv/Scripts/python.exe -m pytest -q`.
- Línea base: 499 passed, 90 deselected (2026-09-24, commit `c2af1cd`).
- Antes de correr la suite: `pg_isready` (PostgreSQL local no arranca solo).
- Propiedad central, con prueba propia: ninguna de las 8 herramientas cambia la
  base sin un Confirmar.

## Entrega

Commits sobre `master` por unidad, con pedido explícito del usuario
(`AGENTS.md`). Previsión: más de 400 líneas en total, repartidas en las tareas.

## Progreso

- 2026-09-24: documento creado; línea base 499 passed.
- 2026-09-24: **T1 y T2 implementados.** Ruta: delegada, un escritor
  (`herramientas.py`, `agente.py`, `autoridad.py`, `pendientes.py`,
  `gateway.py`, `db/esquema.sql`, `db/migrations/rollbacks/0009`, pruebas).

  **Mecanismo (T1).** `Herramienta` ganó un campo `preparar` (hook opcional
  por herramienta, no una lista de acciones por nombre) y un decorador
  `herramienta(..., preparar=...)`. Cada una de las 8 herramientas que
  escriben tiene su `_preparar_<nombre>`: lee el estado vigente reusando los
  mismos helpers que el handler (`_autorizado_para_dependencia`,
  `puede_aprobar_tarea`, `motivo_no_arranca_tarea`/`motivo_no_cierra_tarea`,
  chequeos de tarea cerrada), y devuelve una `Preparacion(cambio, huella)` o,
  si encuentra el mismo rechazo de negocio que encontraría el handler (tarea
  inexistente, ya cerrada, bloqueo ya resuelto, etc.), el mismo dict de error
  que el handler — sin pasar por confirmación, porque confirmar algo
  imposible no tiene sentido. `Preparacion.resumen` agrega siempre "Todavía
  no se aplicó ningún cambio.". La huella es un hash estable
  (`hashlib.sha256`) sobre el estado leído (ids + estados relevantes).

  **Confirmación (T2).** `ejecutar()` ahora decide si una herramienta pide
  confirmación por `h.preparar is not None`, no por `accion` en
  `REQUIEREN_CONFIRMACION` — evita exactamente el desalineamiento que tenía
  `crear_objetivo`. Sin confirmar, levanta `NecesitaConfirmacion` con el
  `resumen` y la `huella` de la preparación. Confirmando
  (`ya_confirmada=True`), vuelve a correr la preparación (revalida autoridad
  y reglas con estado fresco) y compara la huella nueva contra
  `huella_previa`; si difieren, levanta `EstadoCambio` (nueva excepción) sin
  tocar la base. `gateway._toque` la captura, arma una `pending_action`
  nueva con la vista previa y la huella actualizadas, y avisa que la
  situación cambió — nunca aplica sobre una huella vieja. Si coincide, sigue
  al handler y arma un recibo ("Hecho. {cambio}") con la misma descripción
  que ya se había mostrado, no un "Hecho." solo.

  `pending_action` ganó la columna `huella` (migración `0009` +
  `db/rollbacks/0009`, con `resolver_pendiente` recreada — `drop`+`create`,
  no `create or replace`, porque cambia la forma de salida — para devolverla).
  La corrida de la migración/rollback contra la base de prueba real
  (`test_los_rollbacks_devuelven_la_base_al_estado_anterior`) pasó tras
  corregir un comentario que el rollback había perdido al reescribir el
  cuerpo de la función (byte a byte contra la definición original de
  `git show efa8ee2:db/esquema.sql`).

  `agente._encolar_confirmacion` manda `e.resumen` tal cual como mensaje (ya
  es la vista previa completa) en vez de `"Antes de hacerlo, confirmame:
  {resumen}"`, y persiste la huella.

  **`crear_objetivo` — hallazgo confirmado, corregido.** Declaraba
  `accion="crear_tarea"` (`herramientas.py:262` en el código previo a esta
  unidad). No hay ninguna fila de `permission` para `crear_tarea` ni
  `crear_objetivo` en `espacios/corework.yaml`: hoy las dos acciones caen al
  mismo permiso por defecto (cualquier integrante), así que el bug no
  cambiaba quién puede crear un objetivo hoy. Pero sí mezclaba dos acciones
  de dominio distintas bajo un solo nombre: un permiso futuro sobre
  `crear_tarea` alcanzaría también a `crear_objetivo` sin que nadie lo
  hubiera decidido así, y viceversa. Se corrigió a `accion="crear_objetivo"`
  y se agregó `"crear_objetivo"` a la lista de acciones permitidas por
  defecto en `autoridad.verificar` (`src/leda/autoridad.py`), preservando
  el comportamiento actual (cualquier integrante puede proponer un
  objetivo) mientras separa el permiso para el futuro. Ningún test unitario
  dependía del valor viejo; los escenarios del banco
  (`tests/banco/escenarios/b-000{1,6,7,8,9},b-0010,b-0011,b-0012`) sólo
  nombran `crear_objetivo` en `herramientas_ejecutadas`, no en `accion`, así
  que no se vieron afectados.

  **Pruebas.** RED observado por corrida real de pytest antes de cada
  implementación (no transcripto acá por brevedad; ejemplo representativo:
  antes de T1/T2, `actualizar_estado`/`registrar_bloqueo`/etc. ejecutaban
  directo en un turno — `test_lo_que_si_ejecuto_lo_puede_contar` y
  `test_cadena_de_aprobacion` fallaban al adaptarlos a esperar
  `r.confirmaciones` en vez de `r.acciones` hasta reescribirlos). GREEN:
  suite completa 507 passed, 90 deselected (antes: 499 passed) —
  `.venv/Scripts/python.exe -m pytest -q`. `pg_isready`:
  "localhost:5432 - aceptando conexiones".

  Se agregó `tests/test_vista_previa_confirmacion.py`: la prueba de
  propiedad pedida, una por herramienta, que ejercita sin confirmar (sin
  efecto, una sola `pending_action` con vista previa humana y huella),
  confirmar (aplica una vez, el token no vuelve a ejecutar), y huella que no
  coincide (no aplica nada, `EstadoCambio`).

  Se adaptaron sin debilitar lo que afirman: `tests/test_bloqueos.py`
  (14 llamadas), `tests/test_dependencias.py` (29 llamadas + 1 prueba de
  auditoría reescrita para confirmar por botón antes de comprobar
  `audit_log`), `tests/test_agente.py` (confirmación sin el parche manual de
  `REQUIEREN_CONFIRMACION`, cadena de aprobación adaptada a
  `r.confirmaciones`, bloqueo por escalera confirmado antes de comprobar la
  escalera), `tests/test_veracidad.py` (dos pruebas que asumían ejecución
  directa en un turno), `tests/test_task_drafts.py` (una llamada),
  `tests/banco/test_corrida.py` (una llamada). `tests/test_botones.py` y
  `tests/test_pendientes.py` no necesitaron cambios: sus `pending_action`
  construidas a mano no llevan huella, y `huella_previa=None` no dispara la
  comparación (diseño deliberado: no rompe un mecanismo anterior a este).
  El único replay existente (`afirma-resolvio-sin-ejecutar-la-herramienta`)
  no usa ninguna de las 8 herramientas (el modelo no llama nada en esa
  grabación) y no necesitó cambios.

  **Escenarios del banco que van a necesitar un paso de confirmación en T4**
  (cualquier escenario cuyos `herramientas_esperadas` incluyan una de las 8,
  porque hoy quedarían pendientes en vez de ejecutadas):
  `b-0001`/`b-0001-a`/`b-0001-b` (`crear_objetivo`), `b-0003`
  (`resolver_bloqueo`, ya lo prueba el replay existente y no se toca acá),
  `b-0006`/`b-0006-a`/`b-0006-b`/`b-0006-c` (`crear_objetivo`),
  `b-0007`/`b-0007-a`/`b-0007-b`/`b-0007-c` (`crear_objetivo`), `b-0008`
  (`crear_objetivo`), `b-0009` (`crear_objetivo`), `b-0010`
  (`crear_objetivo`), `b-0011` (`crear_objetivo`), `b-0012`
  (`crear_objetivo`). No se tocó ningún YAML de escenario: es trabajo de T4.

  **Decisiones de diseño que el documento no dejaba resueltas:**
  1. *Recibo al confirmar.* El documento pedía "un recibo que cuenta qué
     cambió", sin decir de dónde sale el texto. Se reusa `Preparacion.cambio`
     capturado en el mismo `ejecutar()` que aplica el cambio (parámetro de
     salida `preparacion: dict`, para no romper el contrato de retorno que
     usa `agente.py` con el resultado del handler).
  2. *Forma de "estado cambió".* Se separó en dos casos: (a) la preparación,
     corrida de nuevo, encuentra un rechazo de negocio (tarea cerrada,
     bloqueo ya resuelto) → se devuelve ese resultado directo, sin nueva
     `pending_action`; (b) la preparación sigue siendo válida pero con una
     huella distinta → `EstadoCambio`, nueva `pending_action` con vista
     previa nueva. El documento no distinguía los dos casos.
  3. *Qué entra en la huella.* No hay una receta general; cada
     `_preparar_<nombre>` decide qué campos del estado leído importan (p. ej.
     `resolver_bloqueo` incluye si quedan otros bloqueos abiertos, porque
     afecta a qué estado vuelve la tarea).
  4. `Herramienta.preparar` es un campo del `@dataclass(frozen=True)`
     existente, no un registro paralelo: mantiene una sola fuente de verdad
     por herramienta y no le agrega una segunda estructura al módulo.
- 2026-09-24 (orquestador): revisión de T1-T2. La preparación de las cuatro
  herramientas con `valida_en_handler` valida permisos antes de la vista previa
  (`_preparar_resolver_bloqueo`, `_preparar_aprobar_tarea`,
  `_preparar_crear_dependencia`, `_preparar_quitar_dependencia`). Control:
  `tests/test_vista_previa_confirmacion.py` 8 passed; suite completa 507 passed,
  90 deselected. Pendiente anotado: un ciclo de dependencia se detecta recién al
  confirmar (lo controla el disparador de la base), no en la vista previa.
  Commit `2bd2200` "feat: require a preview and confirmation before every change".
  Siguen T3 (Modificar), T4 (banco) y T5 (continuidad).
- 2026-09-24: **T3 implementado.** Ruta: delegada, un escritor (`db/esquema.sql`,
  `db/migrations/0010_modificar_propuesta.sql`,
  `db/rollbacks/0010_modificar_propuesta.sql`, `src/leda/pendientes.py`,
  `src/leda/agente.py`, `src/leda/gateway.py`, `tests/test_modificar.py`).

  **Mecanismo elegido para el contexto de Modificar.** Se evaluaron las dos
  alternativas que sugería la tarea y se descartó inventar una tercera:
  - `pending_reply`: no encaja. Su forma es la de la escalera de
    recordatorios (`tipo`, `recordatorios`, `escalado_en`, ligada a
    `task_id`), no tiene `chat_id` ni referencia a `pending_action`, y
    reusarla habría mezclado dos dominios distintos —una fila de esa tabla
    hoy significa "Leda le debe una pregunta sobre una tarea a esta
    persona", no "esta persona pidió corregir una propuesta"— además de
    arriesgar que `escalera.py` la contara para la escalada.
  - `pending_action` (elegida): la fila que ya representa la propuesta
    original tiene exactamente lo que hace falta —`herramienta`, `args`,
    `resumen`, `workspace_id`, `membership_id`, `chat_id`, `vence_en`— desde
    que T1 arma la vista previa. No hace falta una tabla nueva: alcanza con
    dejar esa misma fila marcada.

  **Alternativa al valor de enum sugerido por la tarea, justificada.** La
  tarea sugería "un nuevo valor de `estado_pendiente` como `modificada`".
  Se optó por NO agregar un valor al enum y en cambio reusar `'cancelada'`
  (que ya significa "no se aplicó nada") más dos columnas nuevas,
  nullable, en `pending_action`:
  - `modificar_pedido_en timestamptz`: marca que este cierre en particular
    fue un pedido de corrección, no un Cancelar liso.
  - `modificacion_consumida_en timestamptz`: marca que esa corrección ya se
    leyó para un turno (de un solo uso).

  Motivo: `estado_pendiente` sólo se usa en esta columna
  (`grep` confirmó que ninguna otra tabla ni firma de función lo usa), así
  que técnicamente agregar un valor era viable, pero requería (a) dos
  transacciones separadas en la migración —Postgres no permite usar un
  valor de enum recién agregado con `ALTER TYPE ... ADD VALUE` en la misma
  transacción que lo agrega— y (b) para el rollback, recrear el tipo entero
  (`rename` + `create` + `alter column ... using` + `drop`), porque
  Postgres no tiene `DROP VALUE`. Las dos columnas nullable logran lo mismo
  —diferenciar "Cancelar" de "Modificar" y "todavía no se leyó" de "ya se
  leyó"— con el mismo patrón que ya usa el esquema para otras marcas
  temporales opcionales (`resuelta_en`, `escalado_en`, `satisfecho_en`), sin
  tocar el tipo de la columna `estado` ni su índice parcial
  (`pending_action_abiertas`), y con una migración y un rollback de una sola
  transacción cada uno.

  **Botón Modificar.** `Herramienta` no cambió: el discriminador de quién
  gana el tercer botón es `e.huella is not None` dentro de
  `agente._encolar_confirmacion` —las 8 herramientas con `preparar` siempre
  llegan con huella (T1), y es exactamente el mismo criterio que ya
  distinguía la vista previa "de verdad" del resto—. La rama de
  `H.EstadoCambio` en `gateway._toque` (vista previa nueva tras un cambio de
  estado detectado al confirmar) también pasa las tres opciones, porque por
  construcción sólo la levanta una herramienta con `preparar`. Los demás
  caminos (confirmación vieja sin `preparar` —hoy sin ninguna herramienta
  real, `REQUIEREN_CONFIRMACION` sigue vacía de handlers—, `NecesitaElegir`,
  y el borrador guiado de tarea) no se tocaron: siguen con sus botones de
  siempre porque no pasan por `_encolar_confirmacion` con huella, o no pasan
  por ahí en absoluto.

  `resolver_pendiente` (0010, `create or replace`: la forma de salida no
  cambió, no hizo falta `drop`) suma la rama de `o.valor = '"modificar"'`,
  antes de la de Cancelar: pone `estado = 'cancelada'` +
  `modificar_pedido_en`, y en la misma sentencia invalida
  (`modificacion_consumida_en`) cualquier otra Modificación de la misma
  persona y chat que siguiera sin leerse, para que sólo pueda haber una
  abierta a la vez.

  **`pendientes.reclamar_modificacion_abierta`.** Reclama de forma atómica
  ("`for update skip locked`" sobre una subconsulta con `limit 1`) la
  Modificación más reciente, sin leer y sin vencer, de una persona en un
  chat, y la marca consumida en la misma sentencia (un solo uso, se use o
  no lo que trae). `Resuelta` ganó el campo `modificada: bool`.

  **El turno con contexto.** `gateway._turno` reclama la Modificación
  abierta antes de rutear (`route_intent` no se llama para ese turno: es
  una corrección, no un pedido nuevo a clasificar) y, si hay una, llama
  directo a `agente.responder(..., modificacion=...)`. `responder` arma un
  bloque de sistema con la herramienta, los argumentos originales y la
  vista previa que se había mostrado, y lo agrega a `ctx.sistema` —nunca al
  mensaje del usuario— antes de llamar al proveedor. Si el modelo vuelve a
  llamar a la herramienta, el camino normal de `preparar`/confirmar arma la
  vista previa nueva; si el mensaje era sobre otra cosa, no pasa nada y la
  propuesta vieja queda cerrada como estaba.

  **Pruebas.** RED observado por corrida real de pytest antes de implementar
  (11 de 13 pruebas nuevas fallaban por `LookupError: ... no ofrece
  'Modificar'` o por el toque contra el webhook real; ver historial de la
  sesión). GREEN: `tests/test_modificar.py` 13 passed; suite completa 520
  passed, 90 deselected (antes: 507 passed) —
  `.venv/Scripts/python.exe -m pytest -q`. `pg_isready`: "localhost:5432 -
  aceptando conexiones". La corrida de migración/rollback contra la base de
  prueba real (`test_los_rollbacks_devuelven_la_base_al_estado_anterior`,
  que descubre `0010_modificar_propuesta.sql` del directorio) pasó.

  Textos verificados con datos ficticios (corework, "Marcos Tarquini",
  `registrar_bloqueo`): vista previa con sus tres botones en orden
  `["Confirmar", "Modificar", "Cancelar"]`; tras Modificar, "¿Qué querés
  cambiar?"; el siguiente turno con corrección arma una vista previa nueva
  con el cambio corregido ("... Causa del bloqueo: falta el cable, no el
  switch ... Todavía no se aplicó ningún cambio.") sin aplicar nada.

  **Pendiente anotado:** el gap conocido de T1-T2 sobre ciclos de
  dependencia (se detectan al confirmar, no en la vista previa) sigue sin
  tocar; T3 no lo alcanza. Sigue T4 (banco) y T5 (continuidad).
- 2026-09-24 (orquestador): revisión de T3. Riesgo encontrado: la corrección
  después de Modificar se aceptaba mientras la propuesta estuviera vigente
  (hasta 8 h), y ese mensaje saltea el enrutador de intención, así que un pedido
  no relacionado horas después se habría tomado como corrección. Decisión del
  usuario: ventana de 30 minutos (`pendientes.VENTANA_MODIFICACION`, filtro en
  `reclamar_modificacion_abierta`). Rojo observado:
  `test_la_modificacion_se_cierra_pasada_la_ventana` (a los 31 minutos todavía
  se reclamaba); verde: `tests/test_modificar.py` 15 passed; suite completa 522
  passed, 90 deselected.
- 2026-09-24: **T4 implementado.** Ruta: delegada, un escritor
  (`tests/banco/corrida.py`, `tests/banco/comprobadores.py`,
  `tests/banco/test_corrida.py`, `tests/banco/test_comprobadores.py`,
  `tests/banco/test_replays.py`, `tests/banco/test_banco.py`; disparador:
  2+ archivos no triviales en `tests/banco/`).

  **Camino del toque, sin inventar uno paralelo.** `gateway.procesar_update`
  ya es el único punto de entrada tanto para un mensaje como para un
  `callback_query` (`gateway.py:58`, "La usan el webhook y el modo local por
  polling"); `corrida.py::ejecutar_escenario` ya lo llama directo para los
  mensajes, sin pasar por `TestClient`/FastAPI (a diferencia de
  `tests/test_botones.py`/`tests/test_modificar.py`, que sí usan
  `TestClient` porque además prueban el secreto del webhook). Se mantuvo esa
  misma forma para el toque: un `update` con `callback_query` armado igual
  que en esos tests (`data: f"p:{token}"`, `from.id`, `message.chat.id`) y
  pasado al mismo `gateway.procesar_update` — cae en `gateway._toque`, la
  función real que atiende un toque, no un atajo que llame a
  `herramientas.ejecutar` directo. Se agregó un parche de
  `gateway.acusar_toque` (con guardado/restauración manual, igual que ya
  hacía `mantener_chat_activo`) para no salir a la red real por cada
  confirmación del banco; su falla ya es cosmética y no afecta el resultado
  (`_toque` la ignora con un `except Exception: pass`), así que el parche
  sólo evita la demora del timeout, no cambia comportamiento.

  **Decisión de diseño: el banco confirma siempre, sin flag de YAML.** La
  tarea preguntaba si hacía falta un `confirmar: true` por escenario. Se
  decidió que no: `ejecutar_escenario` detecta sola, después del/de los
  turno(s) de mensajes, si quedó una `pending_action` en `'esperando'` que
  ofrece un botón "Confirmar" (`_pendiente_para_confirmar`, nueva función:
  la última `pending_action` de ese chat con esa opción) y la toca. Una
  `NecesitaElegir` (candidatos ambiguos, p. ej. a quién asignar) no tiene esa
  opción y no se toca — el banco no adivina una elección por la persona.

  Motivo (verificado contra `agente.py:250`, `agente.py:118-132`): el
  registro `herramienta:<nombre>` en `audit_log` que arma
  `herramientas_ejecutadas` sólo se escribe cuando una herramienta se
  ejecuta de verdad (o al confirmar en `gateway._toque:336`) — nunca cuando
  sólo levanta `NecesitaConfirmacion`. Antes de T4, una propuesta que
  quedaba sin confirmar era invisible tanto para `herramientas_esperadas`
  (b-0002/b-0004/b-0005, que esperan `registrar_bloqueo`/`actualizar_estado`/
  `crear_dependencia` — hoy quedarían pendientes en vez de ejecutadas, y el
  escenario fallaría por "no ejecutó las esperadas") como para
  `herramientas_prohibidas` (b-0001/b-0006 a b-0012, que prohíben
  `crear_objetivo` entre otras — si el modelo la llamaba por error, con T1/T2
  solas se quedaba pendiente sin confirmar y la prohibición dejaba de
  detectar el error, un hueco de cobertura peor que el que había antes de
  esta unidad). Confirmar siempre que aparece un botón Confirmar cierra las
  dos puntas con el cambio más chico: no hace falta declarar por escenario
  cuál de las 8 herramientas corresponde ni tocar ningún YAML existente.

  **Propiedad central: sin efectos antes de confirmar.** Nueva
  `comprobadores.comprobar_sin_efectos_antes_de_confirmar(conteos_antes,
  conteos_antes_del_toque)`: compara, tabla por tabla, los conteos de antes
  de la corrida contra los de justo antes del toque (nuevo campo
  `ResultadoCorrida.conteos_antes_del_toque`, `None` si no hubo propuesta) y
  falla si alguna de las tablas que las 8 herramientas escriben cambió
  (`task`, `blocker`, `dependency`, `task_state_event`, `objective`,
  `evidence`, `approval` — deliberadamente sin `message_outbox`, porque la
  vista previa misma sale por la cola antes del toque, ni `task_draft`,
  porque el alta guiada de tarea no es ninguna de las 8). Se agregaron
  `objective`, `evidence` y `approval` a `corrida.TABLAS_ESTADO`: sin esto,
  `_conteos`/`conteos_delta` nunca habían visto los efectos de
  `crear_objetivo`, `adjuntar_evidencia` ni `aprobar_tarea`, en ningún
  escenario, ni antes ni después del toque. El comprobador se agregó,
  incondicional (no depende de `debe_preguntar` ni de ninguna otra
  bandera), a las listas de `comprobaciones` de `test_replays.py` y
  `test_banco.py`.

  **Pruebas.** RED observado por corrida real de pytest antes de
  implementar: `tests/banco/test_comprobadores.py` — `ImportError: cannot
  import name 'comprobar_sin_efectos_antes_de_confirmar'` (colección
  fallida, 1 error). Verde tras implementarlo:
  `.venv/Scripts/python.exe -m pytest -q tests/banco/test_comprobadores.py`
  → 64 passed. Luego `tests/banco/test_corrida.py` —
  `ImportError: cannot import name '_pendiente_para_confirmar'` (colección
  fallida, 1 error); verde tras implementar `_pendiente_para_confirmar` y el
  toque automático en `ejecutar_escenario`:
  `.venv/Scripts/python.exe -m pytest -q tests/banco/test_corrida.py` →
  22 passed (dos ajustes sobre la marcha: los tests nuevos que llaman
  `identificar`/`P.registrar` necesitaban cursor de `espacio(conn, ws)`, no
  de `admin(conn)` — mismo motivo que ya usan `test_botones.py`/
  `test_modificar.py`; y la comparación "sin efectos antes del toque" no
  podía exigir el dict completo igual, porque `message_outbox` sí cambia
  legítimamente por la vista previa encolada).

  GREEN de todo el paquete del banco:
  `.venv/Scripts/python.exe -m pytest -q tests/banco` → 121 passed, 90
  deselected (incluye el replay existente `b-0003`, que sigue sin tocar un
  toque porque en esa grabación el modelo no llama ninguna herramienta).
  GREEN de la suite completa:
  `.venv/Scripts/python.exe -m pytest -q` → 533 passed, 90 deselected,
  1 warning (173.04s) — exactamente 522 + 11 (las 6 pruebas nuevas de
  `test_comprobadores.py` más las 5 de `test_corrida.py`), sin
  regresiones. `pg_isready`: PostgreSQL local ya estaba arriba (verificado
  al principio de la unidad).

  **`test_replays.py` sin cambios de comportamiento.** El único replay
  (`afirma-resolvio-sin-ejecutar-la-herramienta`, escenario b-0003) sigue
  pasando sin tocar ningún botón: la grabación no incluye ninguna llamada a
  herramienta, así que `_pendiente_para_confirmar` no encuentra nada que
  confirmar — exactamente lo que ya anotaba T1-T2 sobre este replay.

- 2026-09-24 (orquestador): revisión de T4, dos huecos encontrados en
  `comprobar_sin_efectos_antes_de_confirmar` y corregidos con TDD estricto.

  1. **Sin propuesta, aprobaba sin más.** Cuando el turno no dejaba ninguna
     `pending_action` con Confirmar, `conteos_antes_del_toque` quedaba en
     `None` y la función aprobaba directo — exactamente el caso que la
     propiedad central tiene que atrapar: una de las 8 herramientas
     ejecutándose sin que nadie haya confirmado nada. Corregido: sin toque,
     la comparación pasa a ser `conteos_antes` contra `conteos_despues` (la
     corrida entera, no sólo hasta un toque que nunca pasó). Nuevo parámetro
     obligatorio `conteos_despues`.
  2. **Un conteo por tabla no ve un `UPDATE`.** `resolver_bloqueo` marca
     `resuelto_en` sobre una fila que ya existía; `actualizar_estado` puede
     cambiar `estado` sin insertar ninguna fila — ninguno de los dos mueve
     un conteo por tabla. Señal primaria agregada: `ResultadoCorrida` suma
     `herramientas_antes_del_toque` (`corrida.py`, nueva
     `_herramientas_registradas`, reusada también para el
     `herramientas_ejecutadas` final), las herramientas que ya tenían su
     entrada `herramienta:<nombre>` en `audit_log` en el momento justo antes
     de cualquier toque posible — se captura siempre, haya o no propuesta,
     porque el hueco 1 es justo la ejecución que nunca llega a proponer
     nada. Verificado contra el código (`agente.py:250`,
     `gateway.py:336`): esa entrada sólo se escribe al ejecutar de verdad,
     nunca al levantar `NecesitaConfirmacion`. El comprobador falla si
     cualquiera de esas herramientas está en `_HERRAMIENTAS_QUE_ESCRIBEN`
     (reusada tal cual de `comprobadores.py`, mismo conjunto de 8 que ya
     usaba `comprobar_accion_sin_herramienta` — no hizo falta una lista
     nueva). El conteo por tabla queda como señal secundaria.

  **Pruebas.** RED observado por corrida real de pytest antes de
  implementar: `tests/banco/test_comprobadores.py`, 9 fallos —
  `TypeError: comprobar_sin_efectos_antes_de_confirmar() takes 2 positional
  arguments but 3 were given` / `got an unexpected keyword argument
  'herramientas_antes_del_toque'` (firma vieja no aceptaba los parámetros
  nuevos que los tests ya pedían, incluidos los dos que ejercitan los
  huecos: uno sin propuesta con cambio en `conteos_despues`, otro con
  `resolver_bloqueo` en `herramientas_antes_del_toque` y conteos sin ningún
  cambio). Verde:
  `.venv/Scripts/python.exe -m pytest -q tests/banco/test_comprobadores.py`
  → 67 passed. Luego `tests/banco/test_corrida.py`:
  `AttributeError: 'ResultadoCorrida' object has no attribute
  'herramientas_antes_del_toque'` (2 fallos) antes de agregar el campo y su
  captura en `ejecutar_escenario`; verde:
  `.venv/Scripts/python.exe -m pytest -q tests/banco/test_corrida.py` →
  22 passed. `test_replays.py` y `test_banco.py` actualizados para pasar
  `conteos_despues` y `herramientas_antes_del_toque` en su llamada (sin
  cambio de comportamiento: ningún escenario ni replay actual pisa ninguno
  de los dos huecos).

  GREEN de todo el paquete del banco:
  `.venv/Scripts/python.exe -m pytest -q tests/banco` → 124 passed, 90
  deselected. GREEN de la suite completa:
  `.venv/Scripts/python.exe -m pytest -q` → 536 passed, 90 deselected,
  1 warning (178.12s) — 533 → 536: +3 pruebas nuevas en
  `test_comprobadores.py` (de 6 a 9 sobre este comprobador); en
  `test_corrida.py` no se agregó ninguna prueba nueva, sólo una aserción
  sobre `herramientas_antes_del_toque` en cada una de las dos pruebas ya
  existentes. Sin regresiones. `pg_isready`: PostgreSQL local seguía
  arriba.

  **Pendiente anotado, no de esta unidad:** el gap de T1-T2 sobre ciclos de
  dependencia (se detectan al confirmar, no en la vista previa) sigue sin
  tocar. Sigue T5 (continuidad: `docs/capacidades.md`, `docs/STATUS.md`,
  diseño §4.5).
- 2026-09-24 (orquestador): **T5.** `docs/capacidades.md` (fila nueva), `docs/STATUS.md`
  (próximo paso: aclaración con botones; sección de cierre) y diseño §4.5. Control del
  orquestador: `.venv/Scripts/python.exe -m pytest -q tests/banco` → 124 passed, 90
  deselected. Unidad cerrada.
