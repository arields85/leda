# Flujo de un mensaje (ADR 0014), aplicación acotada y experimento A/B

## Objetivo

Aplicar el flujo del [`ADR 0014`](../../docs/decisions/0014-flujo-de-un-mensaje.md) a los
caminos de los hallazgos pendientes de la ronda 4, con la redacción de la respuesta
seleccionable entre A (el modelo redacta sobre el resultado del turno, con verificación
del código) y B (plantillas para los efectos), y comparar ambas por Telegram real.

## Problema y porqué

La conversación se siente robótica y cada ronda deja hallazgos nuevos del mismo tipo. El
principio "el modelo interpreta, el código garantiza" se aplicaba sólo al comando, no a
los valores ni a la redacción. Decisión del usuario del 2026-09-30: dejar de parchar,
definir el flujo y medirlo con pruebas reales.

## Alcance autorizado

- Caminos: alta guiada; datos pedidos del menú de una tarea (motivo de "Pedir cambios",
  evidencia, causa y resolución de un bloqueo, motivo de un rechazo); lectura de la
  evidencia; reentrega tras cambios pedidos; vista previa de Aprobar.
- Interruptor A/B como dato del espacio (`workspace_setting`, clave `redaccion`), sembrado
  desde el paquete. Sin la clave o con un valor desconocido: B, y queda registrado.
- Fuera de alcance: el resto de los caminos (siguen como están, ADR 0014); R4b-H6
  (horario del despachador) y R4b-H7 (grupo de Telegram inexistente, configuración).

## Restricciones

- Moratoria de parches: ningún mecanismo por frase o por caso (ADR 0013). Los hallazgos
  son el guion de la prueba, no una lista de correcciones.
- Nunca fallar en silencio: si el modelo no interpreta un valor, la pregunta queda
  abierta, se registra el incidente y sale el aviso neutro.
- Una respuesta visible por mensaje (`respuesta_unica.py`): el texto de A o B y sus
  botones van en el mismo grupo de respuesta; con A, el verificador corre antes de
  encolar y el respaldo de B reemplaza al texto rechazado, no se suma.
- `main` queda intacto para el circuito C de la ronda 4 (01/10 09:00).
- Trabajo en el worktree `D:\Proyectos\Prisma-PM-worktrees\flujo-de-un-mensaje`, rama
  `feat/flujo-de-un-mensaje`. El paquete `prisma` está instalado en modo editable desde
  el checkout principal: pytest usa el `src/` del worktree (`pythonpath = ["src"]`), pero
  `python -m prisma` necesita `PYTHONPATH=src` para correr el código del worktree.

## TDD

- Modo: estricto (activado en la configuración del usuario, `CLAUDE.md` global).
- Runner: `D:\Proyectos\Prisma-PM\.venv\Scripts\python.exe -m pytest` desde el worktree.
- RED observado antes de cada implementación, después GREEN y REFACTOR.

## Mecanismos

- **M1. Valores normalizados (etapas 2 y 4).** Con pregunta pendiente, el ruteo devuelve
  además `valor` (`fecha_iso`, `opcion_id` o `texto`) según el tipo que declara la
  pregunta (`_Pregunta.tipo_valor`) y las opciones ofrecidas con sus ids. `valores.py`
  valida: fecha ISO válida y no pasada, opción entre las ofrecidas, texto no vacío y
  dentro del límite. Las expresiones regulares y la coincidencia exacta de etiqueta
  dejan de interpretar texto libre en estos caminos.
- **M2. Resultado del turno (etapa 6).** `resultado_turno.py`: qué cambió, qué no y por
  qué, el estado leído de la base, qué falta, las opciones posibles y los valores
  aceptados.
- **M3. Variante B.** `redaccion.py` con plantillas para los efectos, el estado y lo que
  falta; sin jerga ("(hasta N)"), sin claves internas, sin textos que no corresponden.
- **M4. Variante A.** El modelo redacta a partir del resultado del turno (llamada sin
  herramientas); un verificador en código rechaza afirmaciones fuera del resultado; el
  respaldo es B y el rechazo queda registrado.
- **M5. Botones desde el resultado.** En los turnos con resultado, las opciones salen de
  `ResultadoTurno.opciones`, no de detectar una pregunta en el texto del modelo.
  Aprobar no ofrece Modificar (la herramienta declara si es modificable) y ofrece ver
  la evidencia.
- **M6. Lecturas y reentrega desde el código.** Ver la evidencia se resuelve con la
  lectura de la tarea y entra como hecho al resultado; la reentrega tras cambios pedidos
  es una sola vista previa.

## Hallazgo → mecanismo (guion de la prueba)

| Hallazgo | Mecanismo |
|---|---|
| R4c-H4 orden del alta, "No encontré esa opción" | Título primero (decisión del usuario) + M1 |
| R4c-H5 bucle al pedir una tarea nueva a mitad del alta | M1 + rama abierta |
| R4c-H6 fecha "4de octubre", "04 / 10" | M1 |
| R4c-H7 jerga "(hasta N)" | M3 / M4 |
| R4c-H8 claves internas en el resumen | M3 / M4 |
| R4c-H9 "Al confirmar…", "Sin descripción" | M3 / M4 |
| R4c-H10 área con una sola opción | M2 (un dato con una sola opción no se pregunta) |
| R4b-H5 motivo tomado como pedido imposible | M1 (con pregunta de texto, el valor es la respuesta) |
| R4c-H3 "No puedo mostrarte la evidencia" | M6 + M2 + M5 |
| R4c-H1 dos confirmaciones en la reentrega | M6 |
| R4c-H2 Aprobar con Modificar y sin evidencia | M5 |
| R4b-H1 "quiero entregar…" sin intento | M6 |
| R4b-H2 a H4 forma de los avisos | M3 / M4 |

## Tareas

Corte 1, para la primera prueba real (alta guiada con A y B):

- [x] **F1.** Interruptor (`1d848ab`; verificado con base, ver progreso) `redaccion` en `workspace_setting` (paquete e importador),
  `resultado_turno.py` y `redaccion.py` con la variante B. Ruta: delegada (2+ archivos
  no triviales).
- [x] **F2.** M1 en el ruteo (`3ff59af`, doble de prueba corregido en `f6e6c19`) (`llm.py`: esquema, validación, proveedor simulado con valor
  guionable, instrucciones por tipo) y `valores.py`. Ruta: delegada.
- [ ] **F3.** Alta guiada con el flujo: título primero y objetivo después (el más probable
  primero), valores por M1, dato con una sola opción completado solo, textos por
  `redaccion`. Retira `_parse_absolute_date` de la ruta del usuario. Ruta: delegada.
- [ ] **F6a.** Variante A para el alta guiada: `redactar` del proveedor, verificador y
  registro de rechazos. Ruta: delegada.
- [ ] **F7.** Base nueva para la prueba (`PRUEBA-LOCAL.md` §5), listener del worktree con
  `PYTHONPATH=src`. Ruta: inline (operativa, sin código).
- [ ] **F8a.** Guion del corte 1 (R4c-H4 a H10) con columna mejoró / empeoró / igual y
  registro de latencia, llamadas al modelo, incidentes y rechazos de A. Ruta: inline.

Corte 2, después de la primera prueba:

- [ ] **F4.** Datos del menú por M1 (R4b-H5).
- [ ] **F5.** Evidencia, reentrega y Aprobar (R4c-H3, R4c-H1, R4c-H2, R4b-H1) con M5 y M6.
- [ ] **F6b.** Variante A extendida a los caminos de F4 y F5.
- [ ] **F8b.** Guion del corte 2 y prueba A/B.
- [ ] **F9.** Enmienda del ADR 0014 con el resultado del experimento.

## Checks aplicables

- Suite enfocada en cada tarea y suite completa al cerrar cada tarea
  (`-m pytest -q`; la línea base de `main` es 2279 passed, 333 deselected).
- RDD sobre cada commit de trabajo según `gentle-ai review assess`.

## Entrega

Previsión: bastante más de 400 líneas en total; cada tarea es una unidad de commit. No hay
PR planificado: la integración a `main` la decide el usuario después del experimento.

## Progreso y evidencia

- 2026-09-30: documento creado. ADR 0014 aceptado (`7c1e17b`). Plan de mecanismos por
  lectura de código (agente de planificación): el interruptor no necesita migración
  (`workspace_setting` es clave-valor, `db/esquema.sql:296`; importador en
  `importador.py:591-616`). Pendiente verificar si el importador rechaza claves de
  paquete desconocidas.

- 2026-09-30, F1 (ruta: delegada, 2+ archivos no triviales). Verificado: el importador
  no rechaza claves de pack desconocidas (sólo `CLAVES_PROHIBIDAS`), no hace falta
  migración; `prisma.__file__` resuelve dentro del worktree durante pytest.
  Hecho: sección `conversacion.redaccion` en `espacios/corework.yaml` (B), siembra en
  `importador._importar_ajustes` y advertencia en `validar` ante una variante
  desconocida; `redaccion.py` (`variante_redaccion(cur, workspace_id)`,
  `interpretar_variante`, `redactar`, variante B; A cae en B),
  `resultado_turno.py`, `valores.py` (sólo `TipoValor`, F2 lo amplía).
  RED: `tests/test_redaccion.py` falló por módulo inexistente (`ImportError` al
  colectar, después `AttributeError` del stub); con los módulos, 3 pruebas del
  importador fallaron antes de implementarlo (`{} != {'redaccion': ...}`, `KeyError:
  'redaccion'`, sin advertencia). GREEN: `pytest -q tests/test_redaccion.py` ->
  30 passed, 17 skipped.
  **Límite de la verificación:** las 17 pruebas con base (`corework`, `conn`) quedaron
  SALTADAS: el worktree no tiene `.env.test` (no versionado) y el agente no puede leer
  ni copiar el de `main` (regla de denegación). Esas pruebas no se ejecutaron: F1 queda
  sin tildar hasta correrlas con `PRISMA_TEST_DB_URL`.

- 2026-09-30, F2 (ruta: delegada, 2+ archivos no triviales). Hecho: `valores.py`
  (`TipoValor`, `Opcion`, `opciones_numeradas`, `ValorEsperado`, `validar_valor` ->
  `Aceptado | Rechazado` con `motivo`, `razon`, `se_acepta`); `llm.py` (`IntentRoute.valor`,
  objeto cerrado `valor` en el esquema con `opcion_id` de lista cerrada, bloque de sistema
  por tipo con el día de hoy, `RouteEnvelope.validate(con_valor=)`, degradación de un
  `valor` mal formado a `{}`, `route_intent(..., valor_esperado=)` en los cuatro
  proveedores, `ProveedorGuionado.esperados` y `valor` guionable); `gateway.py`
  (`_Pregunta.valor_esperado` en cada adaptador, `_valor_esperado_de` con el día de hoy
  de la zona del espacio, `_rutear` lo pasa sólo si hay uno); `tests/banco/corrida.py`
  (el grabador reenvía y graba `valor`). No cambia qué consume cada pregunta.
  RED: `test_valores.py` y `test_router_valor.py` fallaron al colectar (`ImportError` /
  `AttributeError: MAX_LONGITUD_VALOR`); `test_pregunta_valor_esperado.py` 27 failed
  (sin `valor_esperado` ni `_valor_esperado_de`); el grabador del banco falló con
  `TypeError` (sin `valor_esperado`). GREEN: `pytest -q tests/test_valores.py
  tests/test_router_valor.py tests/test_pregunta_valor_esperado.py` -> 199 passed
  ; suite completa sin base: 1001 passed, 1531 skipped.
  **Sin base no se pudo correr la suite completa** (ver F1): tareas F1 y F2 sin tildar
  hasta correr `pytest -q` con `PRISMA_TEST_DB_URL` (línea base de `main`: 2279 passed).

- 2026-09-30, verificación de F1 y F2 con base (`.env.test` ya en el worktree). Suite
  completa desde el worktree: 58 fallas, todas por el mismo defecto de prueba, no de código:
  el doble `_RoutingProvider` de `tests/test_task_intake.py` no aceptaba `valor_esperado`,
  que el gateway ahora le pasa siempre a las preguntas del alta (F2), así que el ruteo
  fallaba dos veces y las pruebas del alta veían "proposed" en vez de "confirmed".
  Corrección (`f6e6c19`, sólo el doble). Con ella, suite completa: 2531 passed, 1 failed,
  333 deselected. La falla
  (`test_aviso_incidente_legible::test_ningun_incidente_se_registra_sin_etapa`) la causó una
  edición en curso de `redaccion.py` (con error de sintaxis) mientras corría la suite, porque
  esa prueba lee `src/` como texto; vuelta a correr en limpio, junto con `test_task_intake.py`:
  97 passed. La línea base de `main` (2279) más las pruebas nuevas de F1 y F2 da lo observado.

## Próximo paso

F3.
