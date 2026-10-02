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
- [x] **F3.** (`08f6281`, `74e2918`) Alta guiada con el flujo: título primero y objetivo después (el más probable
  primero), valores por M1, dato con una sola opción completado solo, textos por
  `redaccion`. Retira `_parse_absolute_date` de la ruta del usuario. Ruta: delegada.
- [x] **F6a.** Variante A para el alta guiada: `redactar` del proveedor, verificador y
  registro de rechazos. Ruta: delegada. (`c48f38b` R8; el commit de A y verificador, ver
  progreso.)
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

- 2026-09-30, F3 (ruta: delegada, 2+ archivos no triviales; dos commits).
  **F3a `08f6281`** orden y valores: el alta empieza por "¿Qué hay que hacer?" y sigue con el
  objetivo; un título que trae el mensaje se toma (`proposed` -> `confirmed`, sin repreguntar).
  Los valores salen de `route.valor` y los valida `valores.validar_valor`
  (`consume_pending_text(valor=)`, `resolve_typed_choice(valor=)`): una fecha dicha de cualquier
  forma, una opción por su id ("1", "2", ...), "ninguna" (+ `texto`) para algo que no se ofreció.
  Un valor que no sirve deja la misma pregunta abierta y dice la razón (`Rechazo` en
  `ResultadoTurno`, sin incidente); uno que falta (`SIN_VALOR`) deja la pregunta abierta, registra
  un incidente (`ETAPA_VALOR_SIN_INTERPRETAR`) y antepone el aviso neutro. La fecha que propone el
  ruteo al empezar se valida y, si no sirve, se dice en el primer mensaje
  (`_store_proposals`); el esquema le pide sólo una fecha completa en `AAAA-MM-DD`, sin el día
  de hoy no resuelve relativas (se preguntan después, cuando el código sí tiene el día).
  **F3b `74e2918`** un dato con una sola opción (`_unica_opcion`) se completa solo; "Otra opción"
  sólo si hay otra (`_hay_otra_opcion`); el selector de Modificar no ofrece un dato sin otra
  opción; preguntas y resumen salen por `redaccion` con la variante del espacio
  (`variante_redaccion`), `ResultadoTurno.rechazo` y `.resumen` nuevos, `render_preview` sin
  "Sin descripción", sin "(hasta N)", con el cierre del botón de cada quien
  (`CIERRE_CONFIRMAR`, `cierre_enviar`).
  RED observado: `test_alta_guiada_flujo.py` contra el código anterior: 27 failed, 1 passed;
  `test_redaccion.py` falló al colectar (`ImportError: Rechazo`); `test_alta_guiada_texto.py`
  contra F3a: 11 failed, 3 passed. GREEN y verificación (desde el worktree, runner del
  checkout principal): `pytest -q tests/test_alta_guiada_flujo.py tests/test_redaccion.py` -> 80
  passed (F3a); `pytest -q tests/test_alta_guiada_texto.py tests/test_alta_guiada_flujo.py` -> 42
  passed; suite completa al cierre: `pytest -q` -> 2573 passed, 333 deselected, 0 failed.
  Cobertura de hallazgos: R4c-H4 `test_sin_la_tarea_en_el_mensaje_pregunta_primero...`,
  `test_una_eleccion_escrita_se_resuelve_por_el_id...`; R4c-H5
  `test_pedir_otra_tarea_a_mitad_del_alta_no_reinicia_ni_entra_en_bucle` (ya pasaba con el
  mecanismo de la regla 1: se agregó como prueba, no hubo RED); R4c-H6
  `test_una_fecha_dicha_de_cualquier_forma...` ("4de octubre", "04 / 10" guionados como
  `fecha_iso`), `test_una_fecha_que_no_sirve...`; R4c-H7 `test_ninguna_pregunta_del_alta_lleva_
  limites...`; R4c-H8 `test_el_resumen_nombra_los_tipos_de_evidencia...`; R4c-H9
  `test_el_resumen_de_quien_pide_dice_lo_que_hace_su_boton...`,
  `test_el_resumen_no_dice_sin_descripcion...`; R4c-H10 `test_el_area_con_una_sola_opcion...`,
  `test_un_objetivo_unico...`, `test_quien_solo_puede_asignarse_a_si_mismo...`,
  `test_otra_opcion_solo_aparece_si_hay_otra...`.
  Retirado: `_parse_absolute_date`, `_next_occurrence`, `resolve_date`, `AmbiguousDate`,
  `_MONTHS`, la comparación de etiquetas de `resolve_typed_choice` (`_match_key`,
  `_option_keys`) y el parámetro `buttons_first`. Pruebas viejas que fijaban el orden o los
  textos se actualizaron (título sin confirmar, área que no se elige, "Otra opción" ausente con
  todas las opciones en pantalla, respuestas escritas con `valor` guionado) y las de
  `resolve_date` se reemplazaron por las de M1.
  **No migrado todavía:** (1) un valor escrito que no es una de las opciones se busca con
  `_entity_candidates` / `_resolve_user_entity` (consulta a la base por nombre): es la etapa 3
  del ADR 0014 y pasa a Jev después; (2) el objetivo más probable primero con la estrella: Jev
  no está conectado al alta (hace falta un cliente en `ingreso_tareas`, paginar todos los
  objetivos y no sólo la página, un ícono nuevo en `salida`, un incidente por falta de
  credencial en cada pregunta, y las pruebas con incidentes contados lo sentirían): más que el
  adaptador de ≤ 80 líneas que se autorizó, así que queda el orden actual (por título) y se
  informa como brecha; (3) los nombres legibles de la evidencia: el pack no tiene etiquetas por
  tipo, `redaccion.nombre_legible` sólo separa palabras ("resultado de prueba",
  "explicacion" sin tilde); (4) `pendientes.opcion_escrita` (elecciones de otras ramas) sigue
  comparando etiquetas: es F4/F5, no el alta.
  Decisiones de implementación a revisar: el selector de Modificar deja de ofrecer un dato sin
  otra opción (hoy, siempre "Área"); el título propuesto se toma sin confirmar.

- 2026-10-01, F6a, chequeo de rumbo (escrito antes de empezar; worktree
  `flujo-variante-a`, rama `feat/flujo-variante-a` desde `1832bfe`).
  1. Clase de problema: la redacción de la respuesta (etapa 6): un texto que afirma algo
     fuera de los hechos (un cambio que no ocurrió, otra fecha, un estado inventado) o que
     suena a plantilla. Ya apareció con otras formas (R4b-H2 a H4, R4c-H7 a H9).
  2. Mecanismo general, no un caso: el verificador es determinista y opera sobre los hechos
     estructurados (literales que deben aparecer, fechas y números que no pueden inventarse,
     vocabulario de estados del dominio, verbos de acción en primera persona sólo si hubo un
     cambio, largo), no sobre frases observadas. Límite declarado: no entiende el sentido; lo
     dudoso se rechaza y sale B.
  3. Qué haría innecesaria la próxima ronda: el registro de cada borrador (aceptado,
     rechazado, falló) con su duración. Una familia de rechazo se mira como mecanismo del
     verificador, no se parcha por frase; y A o B se decide con la mediana medida.
  4. Hipótesis vigente: un modelo "flash" redacta sobre hechos con mediana ≤ 5 s (criterio
     del ADR 0014). Se mide, no se asume (AGENTS, "Cómo pensamos juntos", punto 8). Si la
     mediana pasa de 5 s o los rechazos son la regla, se para y se discute con el usuario.

- 2026-10-01, F6a hecho (worktree `flujo-variante-a`, rama `feat/flujo-variante-a`; dos
  commits: `c48f38b` R8 y el de la variante A).
  **Commit 1 (R8).** `redaccion.TextoRedactado` (cuerpo y cierre como partes),
  `render_resumen`, cuerpo guardado en `pending_action.args["cuerpo_resumen"]` de la
  revisión; `send_to_approval` lo usa en vez de cortar el texto. RED: 5 fallas
  (`AttributeError: redactar_partes`, `KeyError: cuerpo_resumen`); GREEN: 255 passed en 6
  archivos. Las filas de revisión viejas (sin `cuerpo_resumen`, vigencia 8 h) fallarían al
  enviar con un `KeyError` (incidente de turno): sólo existen en una base anterior a este commit.
  **Commit 2 (A).** `llm.py`: `redactar(sistema, hechos) -> str` sin herramientas en los cuatro
  proveedores (mismo timeout y reintento del cliente; tope de 400 tokens) y borradores
  guionables en `ProveedorGuionado`. `verificador_redaccion.py`: determinista, sobre los
  hechos (no por frases): números, fechas y meses que los hechos no tienen; vocabulario de
  estados del dominio; acción en primera persona (`-é`/`-í`) sólo con un cambio, valor
  aceptado o resumen que la respalde; claves internas; nombres citados «…», valores aceptados,
  estados y datos del resumen exigidos; lo esencial (≥ 50 % de las raíces) de cambios, "no
  cambió" y rechazos; la pregunta de lo que falta; largo contra la plantilla de B.
  `redaccion.redactar_turno`: con A llama al modelo y verifica; si no sirve o el modelo falla
  sale B (reemplaza, una sola respuesta) y cada intento queda en `audit_log`
  (`redaccion_variante_a`: resultado aceptada/rechazada/error, motivo, `duracion_ms`) y los no
  aceptados además en un incidente de baja severidad, etapa `redaccion_rechazada`, sin aviso a
  la administración. El cierre del resumen es siempre del código; el resumen se redacta una vez
  para los dos cierres. B queda idéntica: `redactar`/`redactar_partes` no llaman al modelo.
  CLI nueva `python -m prisma redaccion <slug>`.
  RED: `test_verificador_redaccion.py` (`ModuleNotFoundError`), `test_llm_redactar.py` (9
  failed), `test_redaccion_a.py` (13 failed, 1 passed), `test_alta_guiada_variante_a.py` (7
  failed, 1 passed: el caso de B), `test_cli.py` (2 failed, `invalid choice: 'redaccion'`).
  El caso "pregunta dicha como instrucción sin signo de pregunta" se agregó después del código
  (sin RED previo). GREEN: focalizadas 155 passed; suite completa desde el worktree
  (`python -m pytest -q`): 2644 passed, 333 deselected, 0 failed (línea base 2573).
  Pruebas viejas actualizadas: `test_alta_guiada_texto` (el espía sigue la función nueva),
  `test_alta_enviar_a_aprobacion` (cuerpo desde `args`), `test_redaccion` (renombrada).
  **Cómo leer la latencia.** `python -m prisma redaccion corework` (con `PYTHONPATH=src` desde
  el worktree): llamadas, aceptadas/rechazadas/errores, mediana (criterio ADR 0014: ≤ 5 s),
  mediana de las aceptadas, p90 y máximo de la llamada de redacción. Los motivos:
  `python -m prisma incidentes corework` (etapa `redaccion_rechazada`). Cada intento es una
  fila de `audit_log` con `accion = 'redaccion_variante_a'` y `detalle->>'duracion_ms'`.
  **Pasar la prueba real a A:** editar `conversacion.redaccion: A` en `espacios/corework.yaml`
  y `python -m prisma importar corework --activar` (reaplica todo el pack, idempotente), o el
  `update` directo de `workspace_setting` (clave `redaccion`, valor `{"variante": "A"}`),
  más acotado. No hace falta reiniciar: la variante se lee de la base en cada turno. El
  listener tiene que correr el código de este worktree (`PYTHONPATH=src`); el del worktree
  `flujo-de-un-mensaje` no trae F6a.
  **Límites declarados del verificador:** la detección de acciones hechas es morfológica y
  rechaza un "Entendí" inocente (cae en B y queda el motivo); un cambio extra dicho con las
  palabras de un cambio real no se distingue. Mirar los motivos registrados antes de tocar
  el verificador (ADR 0013).

## Chequeo de rumbo: correcciones de la corrida B (2026-09-30)

- **Clase de problema.** El contrato del valor del ruteo es binario (hay valor / no hay valor) y
  confirmar un "dudoso" no toma lo confirmado: dos caras de que la respuesta a una pregunta
  pendiente puede ser parcial o confirmada y el sistema sólo sabe "valor o falla". Ya apareció
  antes como R4b-H5 (una respuesta a una pregunta tratada como imposible). Aparte, F-B3
  (enviar a aprobación sigue contando como rama abierta) contradice la enmienda del ADR 0013.
- **Mecanismo o caso.** Mecanismo: un tercer resultado cerrado del valor ("incompleto", con lo
  que falta por tipo), y confirmar toma el texto confirmado. No hay frases ni palabras clave.
  F-B3 es el estado de la rama abierta, no un caso.
- **Qué haría innecesaria la próxima ronda.** Que ninguna respuesta parcial o confirmada acabe
  en incidente y que iniciar otra tarea nunca toque un borrador que espera a otra persona; con
  pruebas por familias de variantes.
- **La hipótesis sigue valiendo.** Sí: la comprensión mejoró ("más fluido y humano"); lo que falla
  es el contrato entre intérprete y código, no el flujo del ADR 0014.

## Correcciones de la corrida B (2026-09-30)

Ruta: inline por un solo escritor (el encargo lo pidió así; tocó `valores.py`, `llm.py`,
`gateway.py`, `ingreso_tareas.py`, `incidentes.py`, `saludo.py` y la migración `0026`). TDD estricto,
runner del checkout principal, RED observado antes de cada implementación.

- [x] **F-B1** (`2ca9664`). Tercer resultado cerrado del `valor` del ruteo: `falta`, de lista cerrada
  por tipo (`valores.FALTAS_POR_TIPO`: fecha `dia`, elección `cual`, texto/referencia `detalle`). El
  código lo trata como conversación (`MotivoRechazo.VALOR_INCOMPLETO`): la misma pregunta queda
  abierta y se repregunta con plantilla propia, sin incidente. El incidente queda para una falla real
  del contrato: `valor` mal formado, una `falta` que no es del tipo, o `responde` sin valor ni `falta`.
  Si trae el dato y la `falta`, vale el dato. RED: `test_valores.py` + `test_router_valor.py` 40
  failed; flujo (`test_alta_guiada_flujo.py`, con el código de `src` anterior) 8 failed. GREEN: 210
  passed (valores y router), `test_alta_guiada_flujo.py` 37 passed.
- [x] **F-B2** (`2ca9664`). "Sí, es eso" toma lo confirmado (`gateway._ruta_de_lo_confirmado`): en un
  campo de texto libre o de referencia el texto confirmado ES el valor (sin segunda llamada al
  modelo, el código lo valida: resuelve también R5 para ese caso); en fecha o elección el modelo
  reinterpreta sabiendo que la persona confirmó (`ValorEsperado.confirmado`) y, si aun así no da un
  valor, es respuesta incompleta (`FALTA_POR_DEFECTO`), no incidente. RED: 6 failed
  (`test_alta_pregunta_pendiente.py`); GREEN: 27 passed en el archivo. Cambia un resultado visible: el
  texto confirmado se toma tal cual lo escribió la persona (antes lo normalizaba el modelo).
  R5 sigue abierto para fecha y elección (el ruteo corre con el cursor de la base abierto).
- [x] **F-B3** (`2bc10a7`, migración `0026`). Existe en `main` (misma `start()` y mismo índice
  `task_intake_one_active`): no lo introdujo esta rama. `task_intake_request.enviada_en` se marca al
  enviar a otra persona; el índice único y toda búsqueda de la rama abierta del pedido
  ignoran las enviadas; la solicitud sigue `active` (la función que confirma o cancela el borrador la
  busca así). RED: las 3 pruebas nuevas de comportamiento fallaron ("Ya hay un borrador…") en
  `test_alta_enviar_a_aprobacion.py`; GREEN: 35 passed; ensayo de
  migración, rollback y paridad con base limpia (`test_task_intake.py -k "migra or instalacion or
  rollback or parity"`, ahora con `task_intake_request` en el retrato): 10 passed. Un borrador
  enviado antes de aplicar la `0026` conserva el comportamiento anterior hasta que termine. El
  arranque (`saludo.verificar_migraciones`) exige la `0026`. El aviso que ya estaba encolado para
  quien aprobaba un borrador cancelado no se entrega: `despachador._preview_vigente` descarta
  la vista previa que dejó de esperar (quien aprueba no se entera de la cancelación).
- [x] **F-B4** (`9c3fe7b`). `armar_aviso_admin` no completaba `{nombre}` en "Qué pasó" (sólo en "Qué
  vio" y "Qué hacer"); ahora lo hace y una prueba recorre todas las etapas sin dejar marcadores. El
  incidente `valor_sin_interpretar` lleva `referencia_tipo`/`referencia_id` del mensaje y el chat.
  RED: 2 failed en `test_aviso_incidente_legible.py` y 4 en `test_alta_guiada_flujo.py`; GREEN: 15 y 4
  passed.
- [x] **F-B5** (worktree `flujo-variante-a`, `49e81bb`). "voy a enviar videos" volvió a mostrar la
  misma pregunta y nada más: de los comandos de `_atender_pregunta_pendiente`, el único que repregunta
  sin prefijo ni botones es `charla`. Brecha de mecanismo: el ADR 0013 (regla 1) dice de `charla`
  "respuesta breve y la pregunta pendiente se vuelve a hacer"; el código sólo la volvía a hacer.
  Decisión (ADR 0014, ya aceptado: "el modelo redacta sólo la charla y las preguntas"): la respuesta
  breve la redacta el modelo en las dos variantes (`redaccion.redactar_charla`) y sale delante de la
  pregunta, en la misma respuesta visible (prefijo de `_repreguntar`). Si el modelo falla o su texto
  no es una oración corta sin pregunta (`motivo_de_charla_invalida`), sale sólo la pregunta y queda un
  incidente de baja severidad (`charla_sin_respuesta`, sin aviso a la administración). Además, el
  ruteo define de forma general `responde` (contenido que podría responder la pregunta; si no está
  claro, `dudoso`, no `charla`) y limita `charla` a saludos, agradecimientos y conversación suelta
  sin relación (`ROUTER_SYSTEM_PENDIENTE`); sin listas de frases.
  RED (con `src` sin los cambios): 18 failed en `tests/test_charla_breve.py`. GREEN: 18 passed. Una prueba
  existente (`test_rama_eleccion`, elección larga) ahora guiona la respuesta breve. Caracterización
  (ya verde tras el merge, sin código nuevo): `tests/test_valor_incompleto_variante_a.py` (4 passed)
  prueba que la repregunta de `valor.falta` (F-B1) sale por `redactar_turno`: plantilla en B, modelo
  más verificador en A, de B si falla.

- 2026-10-01, F-B5 y merge, chequeo de rumbo (escrito antes de implementar).
  1. Clase de problema: un comando cerrado del ruteo con manejo incompleto respecto del ADR 0013
     (`charla` sin respuesta breve) y una definición del comando demasiado laxa que clasifica como
     charla un mensaje con contenido ("voy a enviar videos").
  2. Mecanismo, no caso: la respuesta breve sale del modelo con un verificador determinista de forma
     (no de frases) y las definiciones del ruteo son semánticas generales; ninguna lista de palabras.
  3. Qué haría innecesaria la próxima ronda: el incidente `charla_sin_respuesta` (motivo) y las
     pruebas por familias; el comando que devolvió el modelo sigue sin registrarse (hueco conocido).
  4. Hipótesis: el modelo redacta una oración breve y fiel sin hechos que verificar; si los
     rechazos fueran la regla, se mira el motivo antes de tocar el verificador.

Verificación (desde el worktree, runner del checkout principal): `pytest -q` completo ->
**2634 passed, 333 deselected, 0 failed** (línea base anterior 2573; +61 pruebas). Antes, enfocada:
494 passed (alta, aprobación, rechazo, banco, aviso, saludo). Una corrida completa anterior se
cortó por el límite de tiempo de la herramienta, no por una falla; se repitió en segundo plano.
No se vio `tuple concurrently updated`.
Para reanudar la prueba real: aplicar `db/migrations/0026_borrador_enviado_no_es_rama_abierta.sql`
a `prisma_flujo` (con `psql -f`, `PGCLIENTENCODING=UTF8`, ver `db/migrations/README.md`) y reiniciar
el listener; sin la `0026` el listener no arranca (`verificar_migraciones`).

## Próximo paso

F7/F8a: la segunda vuelta de la prueba real con A (etapa 6 completa): reiniciar el
listener del worktree (`PYTHONPATH=src`), repetir el guion y leer
`python -m prisma redaccion corework` (llamadas, aceptadas, rechazadas, errores,
timeouts, mediana) y `python -m prisma incidentes corework` (motivos de
`redaccion_rechazada`); comparar contra la línea base de 8,7 s.

## Revisión RDD por commit (2026-10-01)

La rama entera excede el contexto del revisor (`lens_context_budget_exceeded`); se revisó
cada commit de trabajo por separado. Los cinco quedaron aprobados y reconocidos, sin
hallazgos bloqueantes: `1d848ab` (`review-d25378527c903723`), `3ff59af`
(`review-27d88ea41c9d51d2`), `9a8262f` (`review-8b857fb3b3ffd1fd`), `08f6281`
(`review-a6314b41a447d7af`), `74e2918` (`review-afb810857a8849ed`). Frontera de revisión
de la rama: `74e2918`.

Advertencias no bloqueantes, a resolver después de la primera prueba real:

- [ ] R1. `importador.py:617-618`: `conversacion` que no es un mapa rompe el import sin
  aviso claro.
- [ ] R2. `redaccion.py:59-63`: un string jsonb con un objeto escapado se acepta como
  variante válida.
- [ ] R3. `gateway.py:1904-1906`: el respaldo de `_rutear` para proveedores viejos quedó
  sin efecto porque toda pregunta define `valor_esperado`.
- [x] R4 (corrida B, `2ca9664`: una respuesta parcial o ambigua es `falta`, no incidente; sigue habiendo incidente si `responde` no trae ni valor ni `falta`). `ingreso_tareas.py:534-540`: `SIN_VALOR` registra incidente y aviso neutro
  también cuando la respuesta fue vaga ("mmm"); una respuesta vaga es conversación, no
  una falla. Observar en la prueba.
- [ ] R5 (parcial, `2ca9664`: un texto libre confirmado ya no llama al modelo; falta para fecha y elección). `gateway.py:2020-2029`: "Sí, es eso" llama al ruteo con el cursor abierto; si el
  proveedor está lento, el toque falla con el aviso de ruteo caído.
- [ ] R6. `ingreso_tareas.py:1393-1404`: la rama de confirmación del título quedó sin uso
  (`_CONFIRMA_EL_CAMPO` conserva `title`): retirarla.
- [ ] R7. `ingreso_tareas.py:1194-1198` y `:456`: centinela `Rechazado` con campos vacíos y
  `valor=None` por defecto en `consume_pending_text` (un llamador que no lo pase convierte
  toda respuesta en `SIN_VALOR`).
- [x] R8. `ingreso_tareas.py:2074-2078`: `_con_cierre` corta el resumen en el último doble
  salto de línea; con otra redacción (variante A) el cuerpo puede quedar vacío. Resolver
  antes de F6a. Resuelto en F6a (commit 1): `redaccion.TextoRedactado` (cuerpo y cierre
  como partes), `render_resumen`, y el cuerpo se guarda en `pending_action.args`
  (`cuerpo_resumen`) de la revisión; `send_to_approval` ya no corta el texto. RED: 5
  pruebas fallaron (`AttributeError: redactar_partes`, `KeyError: cuerpo_resumen`);
  GREEN: 255 passed en los 6 archivos enfocados.
- [ ] R9. `ingreso_tareas.py:1459-1471`: el dato de una sola opción pisa sin comparar un
  valor que la persona propuso (por ejemplo, un responsable nombrado); debería decir que
  esa opción no es posible.

Verificación de la rama `feat/flujo-variante-a` tras el merge de F-B1..F-B4 (`b87f1cb`) y F-B5
(`49e81bb`): `pytest -q` completo -> **2705 passed** tras el merge (sin conflictos de código; sólo
este documento) y **2727 passed, 333 deselected, 0 failed** tras F-B5. Para probar la variante A en
vivo: escucha con `PYTHONPATH=src` desde este worktree y `redaccion = {"variante": "A"}` en el
espacio; el `.env` no se copia al worktree.

## Revisión RDD por commit, segunda tanda (2026-10-01)

`2ca9664`, `9c3fe7b`, `c48f38b`, `49e81bb`: medio, `under_budget`. `2bc10a7`
(`review-0f71d0ec0d8f5d39`) y `ed0270a` (`review-14ee7d7af0001c72`): alto, 4 lentes,
aprobados y reconocidos, sin correcciones. Advertencias no bloqueantes:

- [ ] R10. `0026` no rellena `enviada_en` para borradores ya enviados al desplegar (siguen
  contando como rama abierta hasta terminar). El rollback falla si hay dos activas.
- [ ] R11. `ingreso_tareas.py:1054-1059`: `enviada_en` nunca se limpia; si el aprobador
  devuelve el borrador a edición, la solicitud queda invisible para el solicitante. Sin
  pruebas de rechazo ni de vencimiento. Verificar contra "Rechazar con motivo" (`0025`).
- [x] R12 (`2c42650`; segunda revisión: el plazo era un timeout por fase de httpx y la llamada podía tardar 6-9 s; `fa86a53` lo acota en total, con un hilo, y lo sube a 4 s tras la medición en vivo; antes: plazo propio de 3 s sin reintentos y caída inmediata a B; la llamada sigue dentro de la transacción del turno, acotada a 3 s: ver "Etapa 6 completa"). `redaccion.py:272-282`: con A, la llamada al modelo corre dentro de la
  transacción del turno con los reintentos completos del proveedor; ante una caída, cada
  turno espera todo antes de caer a B. Plazo propio corto o cortar A tras N errores.
- [x] R13 (`afa5718`: el verificador se rehízo sobre salida estructurada, sin morfología ni listas, y corre dentro del `try` que cae a B). Segunda revisión: rechazaba «Prisma» y el nombre de la persona; `f9f574e` los incorpora como nombres conocidos del turno (`ResultadoTurno.nombres_conocidos`, `NOMBRE_ASISTENTE`). `verificador_redaccion.py:202-203`: "hace la pregunta" se cumple con cualquier
  "?" ("Gracias. ¿Todo bien?" pasa sin la fecha). `:149-152`: la detección de acciones en
  primera persona no descuenta nombres de los hechos ("José"). `redaccion.py:285`:
  `verificar` fuera del try que cae a B.
- [x] R14 (`afa5718`: el motivo de una falla guarda el tipo de la excepción, no su texto; sólo las excepciones propias, `LookupError` y `ValueError`, llevan su mensaje). Segunda revisión: quedaba parcial porque muchos errores de HTTP, URL y JSON heredan de `ValueError`; `f9f574e` guarda el tipo y, sólo para `LookupError`/`ValueError`/`KeyError` exactos, una razón corta sin direcciones, parámetros ni identificadores opacos. `redaccion.py:278-281`: el texto completo de una excepción del proveedor va a
  `audit_log`/`incident`; confirmar que ninguna URL con credencial pueda terminar ahí.

## Etapa 6 completa con A y menos latencia (2026-10-01, decisión del usuario)

Chequeo de rumbo (escrito antes de empezar; ADR 0014, "Resultado de la primera vuelta A/B").

1. Clase de problema: la redacción de A quedó a medias (el modelo escribía una frase
   delante de una pregunta de plantilla: "mitad planilla, mitad modelo"), el verificador
   rechazó falsamente 3 de 18 borradores (heurística morfológica de primera persona) y
   cada texto y cada toque pagaba una llamada lenta (10,3 s y 7,8 s de mediana). Además
   el orden de dos mensajes de un mismo turno salió invertido (F-A1) y la charla breve
   sonó rara (F-A2).
2. Mecanismo, no caso: (a) el modelo escribe el mensaje entero desde el resultado del
   turno, con salida estructurada `{texto, pregunta, afirma}`; (b) el verificador sólo
   comprueba lo verificable contra hechos estructurados (fechas, números, nombres y
   títulos que existen en los hechos; `pregunta` es el campo que falta y el texto
   pregunta; `afirma` es un subconjunto de `cambios`), sin listas de palabras ni
   morfología; (c) plazo propio corto sin reintentos y caída inmediata a la plantilla;
   (d) F-A1: el despacho se serializa por espacio (dos pasadas concurrentes y
   `skip locked` saltaban la fila que la otra estaba enviando).
3. Qué haría innecesaria la próxima ronda: la tabla de motivos de rechazo y la mediana de
   la llamada de redacción (`python -m prisma redaccion corework`); ningún rechazo por
   una forma verbal; ningún par de mensajes del turno en orden inverso.
4. Hipótesis vigente: un modelo flash redacta el mensaje entero sobre hechos dentro de
   un plazo de 3 s con pocas caídas a B, y un pedido corto baja la mediana. Se mide, no
   se asume; si el plazo corta la mayoría de las redacciones, se para y se discute.

### Tareas de la etapa 6 completa

- [x] **F-A3** (`afa5718`). Salida estructurada `{texto, pregunta, afirma}` y verificador
  rehecho (R13, R14). Ruta: inline por un solo escritor (el encargo lo pidió así).
- [x] **F-A4** (`39d29cb`, `3ddee06`). El modelo escribe el mensaje entero con A: preguntas,
  rechazo con su pregunta, aviso de envío (efecto) y charla con la pregunta pendiente
  (F-A2). El resumen: apertura del modelo, datos y cierre del código.
- [x] **F-A5** (`2c42650`). Plazo propio sin reintentos, caída inmediata a B (R12).
- [x] **F-A1** (`485aa5c`). Despacho serializado por espacio.

### Qué quedó construido

- **Verificador** (`verificador_redaccion.py`): el modelo contesta JSON. El código verifica
  sólo contra los hechos: fechas, números y meses; cada título entre «» y cada nombre
  propio a mitad de oración (mayúscula inicial fuera de comillas, salvo al empezar una
  oración) tiene que existir en los hechos (incluidas las etiquetas de las opciones);
  `pregunta` es el `campo` de lo que falta y el texto pregunta (si no falta nada, ni
  `pregunta` ni signo de pregunta); `afirma` es exactamente el conjunto de `cambios`;
  se exigen los nombres citados de los hechos, los valores aceptados (también lo que se
  pide confirmar, de cualquier largo), lo entendido si es corto (<= 80 caracteres) y lo
  esencial de un rechazo o un "no cambió" (mitad de las raíces). Se retiraron la
  heurística de primera persona (`-é`/`-í`), el vocabulario de estados y la pregunta
  "dicha como instrucción".
- **Mensaje entero** (`ingreso_tareas._decir_pregunta`, `_rechazo_entero`, `_decir_envio`;
  `redaccion.redactar_charla_con_pregunta`): hechos nuevos `ResultadoTurno.entendido`
  (lo que la persona dio en este turno, leído de `task_intake_field` por la hora del
  turno, sin lo que completa el código) y `.charla`; `Falta.campo` y `Cambio.id`; las
  opciones llegan como etiquetas de contexto. Los botones siguen saliendo del código.
  B no cambia: `_decir_pregunta` devuelve el texto de siempre sin llamar al modelo, y
  con A el texto de siempre es la base de caída.
- **Latencia**: `redaccion.PLAZO_REDACCION_S = 3.0` (parámetro `plazo` de `redactar_turno`),
  `llm._con_plazo` (cliente por llamada con ese tiempo y sin reintentos; Gemini, un solo
  intento), tope de salida 256 tokens (antes 400), un timeout se registra con resultado
  `timeout` y se cuenta aparte en `python -m prisma redaccion corework`.
- **F-A1**: causa en el código, reproducida con dos conexiones y dos hilos
  (`tests/test_despacho_en_orden.py`: sin el lock salió `['PREGUNTA', 'NOTA']`). Dos
  pasadas concurrentes del despachador (el despacho inmediato de después del webhook y
  el tick de fondo) toman la fila siguiente con `for update skip locked`; la que llega
  con la primera fila bloqueada por la otra envía la segunda. `despachar` toma ahora
  `pg_advisory_xact_lock` por espacio y espera. No se leyó la base del usuario: la causa
  sale de la lectura del código y de la reproducción.

### RED observado y verificación

- F-A3: `tests/test_verificador_redaccion.py` falló al colectar (`ImportError: Borrador`);
  `tests/test_redaccion_a.py` con el código anterior: 9 failed, 10 passed. GREEN: 59
  passed (verificador) y 19 passed (redacción A).
- F-A4: `tests/test_alta_guiada_mensaje_entero.py` y `tests/test_charla_breve.py`: 13 failed
  contra el código anterior; GREEN: 35 passed. Después, la confirmación de un valor
  propuesto: 2 failed, GREEN 14 passed en el archivo.
- F-A5: `tests/test_llm_redactar.py` y `tests/test_redaccion_plazo.py`: 12 failed, 12 passed
  (las de tamaño ya cumplían); GREEN 99 passed con los archivos de A y el CLI.
- F-A1: `tests/test_despacho_en_orden.py`: `assert ['PREGUNTA', 'NOTA'] == ['NOTA',
  'PREGUNTA']`; GREEN 2 passed.
- Suite completa (`python -m pytest -q` desde el worktree, runner del checkout
  principal): 2791 passed, 333 deselected, 0 failed tras F-A1 (antes de `3ddee06`);
  corrida final tras `3ddee06`: **2793 passed, 333 deselected, 0 failed** (línea previa
  2727; 16 min 54 s).

### Medición (lo observado en pruebas, no en vivo)

- Pedido de redacción: guía de voz 935 caracteres antes y 1032 ahora (el contrato JSON
  suma ~100); con los hechos de un turno típico, ~1330 caracteres (~380 tokens). El pedido
  ya era corto antes (nunca llevó el núcleo ni el historial): el cambio de latencia no
  viene de achicar la entrada.
- Lo que sí cambia: una sola llamada por turno donde A hacía dos (el rechazo y la
  pregunta, o la charla y la pregunta), un plazo de 3 s en vez de 20 s por intento y 2
  reintentos (peor caso antes: ~60 s; ahora 3 s más la plantilla), tope de salida 256.
- Con el plazo, un modelo que tarda más de 3 s cae a B en el acto y queda como
  `timeout`: la mediana de las redacciones aceptadas anteriores era 4,5 s, así que la
  prueba real va a mostrar cuántas caen. Si son muchas, el plazo es un dato para decidir
  (PENDIENTE: medir en la corrida y decidir con el usuario si se sube).

### Decisiones tomadas por el escritor (a revisar)

- El cierre del resumen sigue siendo del código: cambia por destinatario (`con_cierre`,
  R8) y es la frase que nombra el botón real; el modelo escribe la apertura.
- La transacción sigue abierta durante la llamada del modelo: sacarla de ahí exige
  separar la lectura de hechos de la escritura de cada camino del alta
  (`task_intake_request ... for update` está tomado). No era seguro dentro de esta
  unidad; con el plazo la espera está acotada a 3 s.
- Un efecto contado en el texto y omitido de `afirma` no se detecta (sin morfología ni
  listas, el código no lee el sentido): límite declarado del verificador.
- No se agregó un modelo propio para redactar (opcional): `proveedor_de_redaccion` usa el
  conversacional.
- Sin cambios: `pendientes`/menú de una tarea, evidencia, reentrega y Aprobar (F4/F5), el
  texto "Hecho. La tarea quedó comprometida." (lo escribe una función de la base).

## Prisma propone (2026-10-01): F-B7, F-B8, F-B10, F-B11

Chequeo de rumbo (registrado en el documento al cerrar la unidad; la clasificación se
hizo al leer el encargo, antes de escribir código).

1. Clase de problema: Prisma sólo dirige. Pregunta lo que falta y no propone ni acota
   lo que sabe: ofrece los objetivos de todos los sectores en el mismo orden diga lo que
   diga la tarea (F-B10, F-B11), acepta un criterio de aceptación vacío de contenido
   (F-B7) y arrastra una propuesta de otro mensaje a otra tarea (F-B8). Principio
   constitucional "Prisma ayuda y facilita, no sólo dirige" (`nucleo/constitucion.md`
   §8); `nucleo/mecanica-pm.md` §4 (lo que cruza áreas va por dependencias) y §13.2
   ("¿El resultado esperado es concreto y verificable?").
2. Mecanismo, no caso: (a) el objetivo tiene área como DATO (migración `0027`), y la
   consulta de candidatos del alta ofrece sólo los del área de quien pide; (b) Jev
   (etapa 3) ordena los candidatos que salen de la base, el código fija los cortes
   (los de una referencia a tarea) y sólo una decisión clara destaca el primero;
   (c) el juicio de "verificable" es un campo cerrado del valor del ruteo
   (`verificable` si/no, `propuesta`), validado por el código, y la propuesta sale por
   los botones de siempre (Sí / No / Otra opción), con una sola propuesta por alta;
   (d) una propuesta queda ligada a la tarea que su mensaje pedía: un título que llega
   como pedido de tarea nueva descarta las propuestas sin confirmar de otros mensajes.
   Ninguna lista de frases ni palabras clave.
3. Qué haría innecesaria la próxima ronda: el guion "Corrida siguiente" del archivo de
   guion; incidentes `objetivo_sin_ordenar` y `criterio_sin_propuesta`.
4. Hipótesis vigente: con el área en los datos, Jev ordena bien objetivos de pocos
   candidatos con un título claro (se mide: ⭐ presente o no); un modelo flash juzga
   bien "verificable" con el título como contexto (se mide con la corrida real).

### Tareas

- [x] **P1** (`712b9fe`) Migración `0027` (`objective.area_id`, FK compuesta al espacio,
  `area_workspace_id_unique`), rollback, `db/esquema.sql`, importador (área de cada
  frente del pack; reimportar completa las que faltan sin pisar). Ruta: inline por un
  solo escritor (el encargo lo pidió así).
- [x] **P2** (`0d75586`) F-B11: el alta ofrece sólo los objetivos del área de quien pide;
  un solo objetivo propio se completa solo; el estratégico y un objetivo sin área sólo
  si el área no tiene propios; los de otra área, nunca. Ajusta dos pruebas del banco
  que suponían los cinco objetivos del pack para Ismael (Dirección).
- [x] **P3** (`8717026`) F-B10: `jev.ordenar_objetivos` (una llamada, claves `O1..On`,
  cortes de una referencia a tarea), ⭐ en el primero con decisión clara, una sola
  pregunta igual; falla de Jev o duda: orden de siempre, sin ⭐ y registrado
  (`objetivo_sin_ordenar`, baja, sin aviso a administración; la falta de credencial,
  una vez por espacio y proceso). Y la nota 5: "Opciones que coinciden con «…»" ->
  "Para «…» encontré estas opciones. ¿A qué objetivo pertenece la tarea?".
- [x] **P4** (`c88ce03`) F-B7: `valor.verificable` y `valor.propuesta` (sólo en la
  pregunta del criterio), la propuesta validada por el código (no vacía, <= 500, distinta
  de lo dicho; si no sirve, se toma lo escrito y queda `criterio_sin_propuesta`); sale por
  la plantilla B o por A con la propuesta literal; también al confirmar con "Sí, es eso".
- [x] **P5** (`b102eec`) F-B8: `consume_pending_text(propuestas=...)`: un título que llega como pedido de tarea nueva (`start_task_intake`) descarta las propuestas sin confirmar de otros mensajes y toma las del mensaje nuevo.

### RED observado y verificación

- P1: `tests/test_objetivo_con_area.py`: 2 failed, 3 passed (las tres que sólo dependen
  del esquema); GREEN 54 passed con paridad y rollbacks (`-k` objetivo/rollbacks/
  convergen/aislamiento) y las pruebas del esqueleto y la siembra.
- P2: `tests/test_alta_objetivos_del_area.py`: 7 failed, 1 passed (el caso de datos
  viejos); GREEN 8 passed. Regresión: 746 passed en las pruebas del alta; el banco mostró
  2 fallos por el supuesto de cinco objetivos (corregido en el mismo commit): 361 passed.
- P3: `tests/test_jev.py` + `tests/test_alta_objetivo_probable.py` contra el código
  anterior: 15 failed, 50 passed; GREEN 80 passed (con `test_aviso_incidente_legible`).
- P4: la colección de `tests/test_alta_criterio_verificable.py` falló
  (`TypeError: ValorEsperado.__init__() got an unexpected keyword argument
  'juzga_verificable'`); GREEN 68 passed con `test_pregunta_valor_esperado` y
  `test_aviso_incidente_legible`. Regresión: 1784 passed (alta, task_intake, llm, router,
  valores, rama, gateway, agente, redacción, verificador, banco).
- P5: `tests/test_alta_propuestas_ligadas_a_su_tarea.py` contra el código anterior: 3
  failed, 1 passed (el control: un título que no pide otra tarea conserva la propuesta);
  GREEN 4 passed. Regresión: 1131 passed (alta, task_intake, rama, pregunta, gateway,
  agente, botones, toque, banco).
- Suite completa: ver "Resultado final" más abajo.

### Decisiones tomadas por el escritor (a revisar)

- F-B8 (ambigüedad de producto, devuelta al orquestador): "otra tarea para Nahuel" y el
  título que llega después SON una sola tarea cuando el título no pide otra; la
  propuesta cae sólo cuando el mensaje que da el título es en sí un pedido de tarea nueva
  (la acción `start_task_intake` del ruteo). Es una señal del modelo (cerrada), no una
  frase. Si el usuario quiere que NINGUNA propuesta de un mensaje dejado de lado sobreviva
  a un título dado después, es una regla más fuerte: se cambia en `_seguir_con_el_campo_del_alta`.
- F-B7: sin `verificable` en el valor (el modelo no juzgó) el texto se acepta como
  siempre; con "no" y una propuesta que no sirve se acepta lo escrito y queda un
  incidente de baja severidad. Una sola propuesta por alta: se cuenta por haber ofrecido
  ya una elección del criterio (también la de una propuesta del primer mensaje).
- F-B10: sólo se ordena la primera página (hasta 7 candidatos) y sin búsqueda escrita.
  Con duda, el orden es el de siempre (no se reordena sin decisión clara).
- F-B11: un objetivo estratégico es el que no tiene área; se ofrece, junto con los
  objetivos sin área de datos viejos, sólo si el área de quien pide no tiene propios.
  Se usa el área de quien pide (no la del responsable: el objetivo se pregunta antes).

### Resultado final

- Suite completa (`python -m pytest -q` desde el worktree, runner del checkout principal): **2852 passed, 333 deselected, 0 failed** (17 min 48 s; línea previa 2793).
- PENDIENTE (orquestador): aplicar `0027` a `prisma_flujo` y dar el área a los objetivos existentes; la prueba real de "Corrida siguiente".

## Correcciones de la revisión RDD de la etapa 6 completa (2026-10-01)

Chequeo de rumbo (escrito antes de escribir código; ADR 0014, "Resultado de la primera
vuelta A/B").

1. Clase de problema: garantías de A que valían en el papel y no en el reloj o en el
   contrato. El "plazo de 3 s" era un timeout escalar de httpx por fase (hasta 6-9 s
   reales); el motivo de una falla guardaba mensajes de `ValueError` (R14 quedó a medias);
   el verificador rechazaba nombres conocidos del turno; el proveedor sin `plazo=` degradaba
   en silencio. Ya apareció antes con otra forma: R12/R13/R14 de la revisión anterior, es
   decir, la misma clase en dos rondas (disparador 4 de "Cómo pensamos juntos"). Se revisa
   el mecanismo, no el caso: el plazo pasa a acotar el tiempo total, y los motivos de falla
   y el conjunto de nombres permitidos pasan a ser reglas generales.
2. Mecanismo general, no caso: (a) plazo total de la llamada (hilo y espera acotada, la
   respuesta tardía se descarta); (b) clasificación de timeouts por tipo de excepción;
   (c) contrato explícito `redactar(..., plazo=...)` con una prueba por clase de proveedor;
   (d) motivo de falla = clase de la excepción + razón corta depurada (sin nada parecido a
   una URL ni a un parámetro); (e) nombres permitidos = conocidos del turno (quien escribe,
   el nombre del asistente, los de los hechos); (f) "este turno" derivado del origen, no de
   igualdad de marcas de tiempo, y un campo sin mapeo cae a B; (g) comprobar que la elección
   sigue abierta antes de llamar al modelo. Ninguna lista de frases.
3. Qué haría innecesaria la próxima ronda: la tabla de rechazos de
   `python -m prisma redaccion corework` sin rechazos por "Prisma" ni por el nombre de la
   persona; la mediana y el porcentaje de `timeout` con el plazo de 4 s; ninguna redacción
   de más de ~4 s a la vista de la persona.
4. Hipótesis vigente: un modelo flash redacta el mensaje entero dentro de un plazo. Medido
   en vivo con `nan`/`deepseek-v4-flash`: p50 0,93 s, p90 3,06 s, máx. 6,6 s; con 3 s caerían
   ~10 % de los turnos, con 4 s ~4 %. Vale; el plazo pasa a 4 s y se sigue midiendo.

### Tareas

- [x] **C1** (`fa86a53`) Plazo total (4 s por defecto), timeouts por tipo, contrato `plazo=` (puntos 1-3).
- [x] **C2** (`f9f574e`) R14 completo y regla de nombres propios del verificador (puntos 4-5).
- [x] **C3** (`0fbd292`) `_entendido_del_turno` robusto y chequeo de elección abierta antes del modelo (puntos 6-7).

### Correcciones de la revisión RDD de `712b9fe` y `c88ce03` (ítems 8 y 9)

Chequeo de rumbo (escrito antes de escribir código).

1. Clase de problema: un dato que el código resuelve en silencio (el área de un frente
   del pack con un slug que no existe queda `NULL`, y el alta lo trata como estratégico)
   y una confirmación de la persona que el modelo puede pisar (`_ruta_de_lo_confirmado`
   toma la ruta del modelo sin mirar su acción, y puede reescribir el texto). Ya apareció
   antes con otra forma: "nunca fallar en silencio" (valores sin interpretar, R14) y
   "el código garantiza, el modelo interpreta" (ADR 0014, M1): el valor de un campo de
   texto confirmado es el texto tal cual (F-B2).
2. Mecanismo general, no caso: (a) un solo auxiliar que resuelve el slug de área de un
   frente y falla (`PackInvalido`) si no existe, usado por la inserción y por el
   completado; `validar` lo reporta como bloqueante; el completado informa cuántas filas
   actualizó y qué frentes no encontró; (b) del juicio del modelo sobre lo confirmado
   sólo se toma el veredicto (`verificable`, `propuesta`), validado por la acción y la
   respuesta a la pregunta; el texto es siempre el confirmado; (c) el aviso de rechazo
   del criterio va ligado a su campo, no a la primera propuesta que se abra.
3. Qué haría innecesaria la próxima ronda: ningún objetivo operativo sin área después de
   importar un pack válido (y un pack con un slug mal escrito que no se importa); ninguna
   respuesta confirmada que cambie de texto o desaparezca.
4. Hipótesis vigente: vale. El área es un dato del pack y el criterio confirmado es
   del usuario; el modelo sólo juzga.

- [x] **C4** (`18317e2`, ítem 8) Slug de área del frente: auxiliar único, fallo y advertencia
  bloqueante, informe del completado, `COMMENT` en `db/esquema.sql`.
- [x] **C5** (`3d1c944`, ítem 9) `_ruta_de_lo_confirmado` conserva el texto confirmado y valida la
  acción; el rechazo del criterio va al campo del criterio.

### Qué quedó construido (correcciones)

- **Plazo total** (`llm.llamar_con_plazo`, `llm.PlazoAgotado`): la llamada de redacción
  corre en un hilo y se deja de esperar al vencer el plazo (`redactar_turno` y
  `redactar_charla`); la respuesta tardía se descarta y el intento queda como `timeout`.
  `PLAZO_REDACCION_S = 4.0` (medido en vivo con `nan`/`deepseek-v4-flash`: p50 0,93 s,
  p90 3,06 s, máx. 6,6 s; con 3 s caerían ~10 % de los turnos, con 4 s ~4 %). El plazo se
  sigue pasando al proveedor (acota el hilo que queda colgado).
- **Timeouts por tipo** (`redaccion._timeout_de`): `PlazoAgotado`, `TimeoutError`,
  `httpx.TimeoutException`, también si un cliente los envuelve (`__cause__`). "más de N s
  sin respuesta" sólo para el plazo propio; los demás dicen su tipo.
- **Contrato `plazo=`**: una prueba por clase de `llm` con `redactar` comprueba que lo
  acepta como argumento con nombre y por omisión `None` (esa prueba nació en verde: ya se
  cumplía; protege el contrato).
- **R14**: `_motivo_de_error` guarda siempre el tipo y, sólo de `LookupError`,
  `ValueError` y `KeyError` exactos, una razón de <= 120 caracteres sin direcciones,
  credenciales, `clave=valor`, `?consulta` ni identificadores opacos.
- **Verificador**: nombres conocidos del turno = quien escribe (leído de `integrante`),
  el asistente y los de los hechos; los de otras personas siguen rechazados. No se le
  cuentan al modelo.
- **`_entendido_del_turno`**: un dato dado por el mensaje al que está atado el turno
  cuenta aunque la hora no coincida; un toque sigue por la hora del turno; un campo sin
  sujeto cae a B con un incidente de baja severidad (`campo: <campo>`), sin `KeyError`.
- **`_rechazo_entero`**: comprueba que la elección siga abierta antes de llamar al modelo.
- **Ítem 8**: `importador._area_del_frente` (único, falla con `PackInvalido`), `validar`
  lo reporta como bloqueante, el completado informa cuántos objetivos completó y los
  frentes sin objetivo; `COMMENT` de `objective.area_id` en `db/esquema.sql`.
- **Ítem 9**: `_ruta_de_lo_confirmado` toma del modelo sólo el veredicto (`verificable`,
  `propuesta`) y sólo si la acción es conversación normal y el comando `responde`; el
  texto es el confirmado. `_advance(..., campo_del_rechazo=...)` ata el aviso del criterio
  a su campo.

### RED observado y verificación (correcciones)

- C1: `tests/test_redaccion_plazo.py` contra el código anterior: 11 failed, 13 passed (el
  plazo de 4 s, el corte del tiempo total, los timeouts por tipo; el contrato de
  `plazo=` pasó desde el inicio). GREEN: 24 passed; con los archivos de A, charla y
  `llm_redactar`: 95 passed.
- C2: 32 failed, 104 passed antes de implementar (verificador y `redactar_turno`); GREEN
  135 passed; la prueba de integración del alta (`nombrar_a_quien_escribe`) falló sin el
  cambio de `ingreso_tareas` y pasa con él. Regresión: 261 passed (+1 que cambió: la
  prueba de los campos de `ResultadoTurno` ya incluye `nombres_conocidos`).
- C3: `tests/test_alta_guiada_mensaje_entero.py`: 4 failed, 18 passed contra el código
  anterior; GREEN 22 passed; regresión 101 passed (alta, charla, redacción A).
- C4: `tests/test_objetivo_con_area.py`: 11 failed, 7 passed; GREEN 18 passed; con esqueleto,
  siembra, onboarding, administrador y esquema de compromiso: 110 passed.
- C5: `tests/test_alta_criterio_verificable.py`: 11 failed, 29 passed; la prueba de
  "sólo `falta`" ya pasaba (control); GREEN 40 passed; con alta guiada y mensaje entero:
  108 passed.

### Resultado final (correcciones)

- Suite completa (`python -m pytest -q` desde el worktree, runner del checkout principal):
  **2955 passed, 333 deselected, 0 failed** (18 min 37 s; línea previa 2852).
- Próximo paso: reiniciar el listener del worktree (`PYTHONPATH=src`) y medir en la prueba
  real la tabla de `python -m prisma redaccion corework` (timeouts con 4 s, rechazos).

## Revisión RDD, noche del 2026-10-01

- Etapa 6 completa: `afa5718` (`review-ce7f8b8be7d5e437`), `39d29cb`
  (`review-d1214d3160ab10c3`), `2c42650` (`review-59a22c8a9bcf050d`) aprobados; `485aa5c`,
  `3ddee06` bajo presupuesto.
- "Prisma propone": `712b9fe` (`review-34750754b99bf9da`), `c88ce03`
  (`review-304fabe95eb22a6e`) aprobados; `0d75586`, `8717026`, `b102eec` bajo presupuesto.
- Correcciones de la revisión: tramo `c88ce03..16cc7cf` (1343 líneas) revisado como un solo
  candidato, aprobado y reconocido (`review-1c13a9b74afef99c`). Frontera de revisión de la
  rama: `16cc7cf`. Notas no bloqueantes: `R3-incidente-campo-sin-sujeto`
  (`ingreso_tareas.py:744-755`, WARNING) y `R3-rechazo-sin-campo` (`:1627-1629`).

## Conversación con memoria y modelo puro (2026-10-01, F-C6)

Chequeo de rumbo (escrito antes de escribir código; ADR 0014 etapa 1, hallazgo F-C6 del
guion "08:22-08:32").

1. Clase de problema: una etapa del flujo sin el contexto que el ADR 0014 le promete. La
   etapa 1 dice que el contexto incluye "el historial reciente de lo que efectivamente se
   dijo", pero sólo `agente.responder` lo recibe (`contexto.historial`); el ruteo
   (`route_intent`) y la redacción (`redactar`) reciben el mensaje o los hechos sueltos. Ya
   apareció antes con otra forma: la pregunta pendiente como contexto (ADR 0013 regla 1)
   se resolvió describiéndola en el sistema del ruteo, sin la conversación; "ayudame, que
   puedo poner?" y "por que anda" se clasificaron como `otro_tema` por eso. La misma clase
   en la redacción: el modelo repite "Entendí que…" porque no ve lo que ya dijo. Y dos
   garantías que valían en el papel: "Dejarlo" destruía el borrador (un efecto
   irreversible detrás de una clasificación que puede fallar) y el plazo de 4 s caía a
   una plantilla (la protección de latencia que el usuario quiere apagar por ahora).
2. Mecanismo general, no caso: (a) el historial reciente (misma fuente y límites que
   `contexto.historial`: sólo lo enviado, en orden, sin el mensaje entrante) entra como
   mensajes previos a los dos proveedores de todo tipo, con reglas semánticas generales en
   las instrucciones (interpretar el mensaje en el contexto de la conversación; no repetir
   fórmulas ya dichas), sin listas de frases; (b) dejar una rama para ver otra cosa
   conserva el trabajo y sólo un Cancelar explícito lo borra; (c) el plazo propio y el
   respaldo de plantilla pasan a una constante/ajuste restaurable, con regeneración
   acotada y falla visible (incidente + aviso neutro), nunca silenciosa; (d) F-A1, F-C5,
   F-B9 y F-C1 se corrigen por la regla de su etapa (orden de envío, cierre del resumen
   como parte propia, normalización en la etapa 2, intención de crear sin búsqueda).
3. Qué haría innecesaria la próxima ronda: que "ayudame, que puedo poner?" y una respuesta
   como "por que anda" no se clasifiquen como otro tema cuando la pregunta pendiente es el
   criterio (se ve en el historial que recibe el ruteo); ningún borrador perdido por
   "Dejarlo"; ninguna redacción de A que repita la apertura del turno anterior; ningún
   resumen sin cierre; sin vencimientos del plazo ni respaldos de plantilla en A.
4. Hipótesis vigente: un modelo flash que ve la conversación clasifica y redacta bien sin
   que el código le describa cada caso. Vale como hipótesis a medir (no está probada):
   la prueba real "Corrida siguiente 2" del guion la mide. Con la protección de latencia
   apagada (decisión del usuario, a restaurar) la latencia pasa a ser la del modelo.

Cambio de alcance (orquestador, decisión del usuario, 2026-10-01): el alta guiada se
rediseña a continuación como conversación conducida por el modelo (con el historial y el
estado del borrador; el código valida, persiste, pone botones y la confirmación final).
Por eso esta unidad hace sólo lo que ese rediseño también necesita. **Se hace:** historial
al ruteo y a la redacción (T1, T2); conservar el borrador al dejarlo (T3); modelo puro sin
plazo propio ni plantilla de respaldo, una regeneración (T4); F-A1, F-C5, F-B9, F-C1 (T5).
**No se hace (se reemplaza con el rediseño):** ayuda dentro de la rama y rediseño de la
propuesta de criterio (F-B7/F-C3), pasar por el modelo el resto de las plantillas del alta
("¿Seguimos?", la confirmación `dudoso`, la aclaración dentro del alta, apertura y cierre
del resumen, "Listo, dejé de lado…"), y F-C2 (descripción igual al título).

### Tareas

- [x] **T1.** (`6978a1b`) Historial al ruteo (todos los proveedores) + instrucciones generales.
- [x] **T2.** (`a865a49`) Historial a la redacción + guía ("seguila, no repitas, sólo lo nuevo").
- [x] **T3.** (`d820a57`) Dejarlo y ver lo otro conserva el borrador (pausado); el próximo
  "quiero crear una tarea" ofrece continuarlo.
- [x] **T4.** (`644b60a`) Modelo puro: sin plazo propio, sin respaldo de plantilla, dos
  intentos con el motivo del rechazo, incidente + aviso neutro si falla.
- [x] **T5.** F-A1 (`36a09e9`), F-C5 (`caf5e2a`), F-C1 (`abffd0a`), F-B9 (`c3540cc`).
- [x] **T6.** (`04a2c87`) Guion "Corrida siguiente 2" y cierre del documento.

Ruta declarada: un solo escritor (el encargo lo pidió así: "execute directly"); disparador
de escritura de 2+ archivos no triviales cubierto por esa instrucción explícita.
TDD: estricto (configuración global del usuario); runner
`D:\Proyectos\Prisma-PM\.venv\Scripts\python.exe -m pytest` desde el worktree.

### Qué quedó construido (conversación con memoria y modelo puro)

- **T1, historial al ruteo.** `route_intent(..., historial=)` en los cuatro proveedores
  (`llm.py`): la conversación reciente (misma fuente y límites que `contexto.historial`:
  sólo lo enviado, en orden, sin el mensaje entrante) como mensajes previos antes del
  texto actual (un arranque de Prisma se descarta; si la persona tenía un mensaje sin
  responder, el actual se le suma). `ROUTER_SYSTEM_CONVERSACION` (sólo con historial) y
  una regla general en `otro_tema`: pedir ayuda con la pregunta, comentarla o decir que no
  se sabe responderla pertenece a ella, nunca es otro tema. `gateway._rutear` pasa
  `historial` sólo si hay; `_historial_del_turno` en `_turno`, el toque de `dudoso` y
  "Dejarlo". El grabador del banco y los dobles de prueba aceptan `historial`.
- **T2, historial a la redacción.** `redactar(..., historial=)`: transcripción
  ("Persona:" / "Prisma:") delante de los hechos, dentro del único mensaje (no turnos
  previos: el modelo contesta un JSON y turnos en prosa le enseñarían a contestar en
  prosa). La guía: seguir la conversación, no repetir aperturas ni fórmulas, decir sólo lo
  nuevo; la conversación es contexto, nunca una fuente de hechos (el verificador no
  cambia). Pasa por el alta (preguntas, rechazos, aviso de envío, resumen) y por la charla.
  La guía creció de ~1100 a ~1350 caracteres (las cotas de `test_redaccion_plazo` se
  ajustaron: 1450 y 1700).
- **T3, Dejarlo conserva el borrador.** `ingreso_tareas.pause_from_intake_question`:
  invalida la pregunta abierta y los botones (sube la versión), deja la solicitud
  `active` con la marca `pausado` en `terminal_result` (sin cambiar el esquema) y audita
  `pausar_ingreso_tarea`. `handle_active_text` no se traga los mensajes de un borrador
  pausado. "Continuar borrador" (`resolve_choice`) quita la marca. Aviso:
  `gateway.AVISO_ALTA_PAUSADA` ("Listo, dejé guardado el borrador de la tarea «…».
  Cuando quieras, lo retomamos."). Sólo "Dejarlo y ver lo otro" y "No, es otra cosa"
  guardan; "mejor dejalo / cancelá todo" (`cancela`) y los botones de cancelar siguen
  cancelando.
- **T4, modelo puro.** `redaccion.MODELO_PURO = True` (restaura el plazo de
  `PLAZO_REDACCION_S` y el respaldo de B con `False`), `INTENTOS_MODELO_PURO = 2`.
  Sin plazo propio (queda el timeout HTTP del proveedor); un rechazo del verificador se
  corrige una vez (el modelo ve `correccion.motivo` y su `texto_anterior`); un error del
  modelo no se reintenta; si no sale texto: incidente `redaccion_fallida` (media, con
  aviso a la administración, motivos de los intentos) y `NOTICIA_NEUTRA_INCIDENTE`
  (`TextoRedactado.fallida`). Lo único que sale además del aviso es lo que la persona
  necesita para decidir con los botones: el resumen (datos y cierre, del código) y el valor
  que se pide confirmar. Cada intento sigue dejando su fila de auditoría con la duración.
  `redactar_charla` (la charla de B) conserva su plazo: B no cambia.
- **F-A1.** La causa de las 08:32:34 no se pudo confirmar sin las filas de la cola (ver
  decisiones). El mecanismo que sí se encontró y corrigió: un envío fallido de una parte se
  reprogramaba al reloj de la pasada (detrás de las demás) y la pasada seguía con la
  siguiente del mismo chat. Ahora el chat con un envío fallido no recibe más en esa pasada
  y una respuesta fallida conserva su `programado_para` (`despachador.despachar`, `_fallo`).
- **F-C5.** `render_resumen` comprueba que el texto termina en su cierre; si algún camino
  lo perdió, lo vuelve a poner y registra `resumen_sin_cierre`. La causa de las 08:18:47 no
  se reprodujo: todos los caminos de la redacción (acepta, rechaza dos veces, error,
  timeout, defecto del verificador) devuelven el cierre; queda la garantía estructural.
- **F-C1.** `_resolver_referencias_del_turno` descarta de `trabajos` la frase que repite
  `task.title` con intención de crear (comparación sin tildes, mayúsculas ni puntuación) y
  `ROUTER_SYSTEM` dice que la tarea nueva y su título no son una referencia. Lo demás que
  el mensaje menciona se sigue resolviendo.
- **F-B9.** La instrucción del valor de texto libre pide corregir sólo errores de tipeo
  obvios sin cambiar sentido ni nombres propios; entidades, fechas y opciones no cambian.
  El resumen muestra el valor guardado, cambiable con Modificar. Alcance: título,
  descripción y criterio del alta; los motivos del menú de una tarea todavía toman el texto
  crudo (F4 de este documento, pendiente).

### RED observado y verificación (conversación con memoria y modelo puro)

- T1: `tests/test_router_historial.py` contra el código anterior: 20 failed, 1 passed (el
  control del proveedor viejo); GREEN 21 passed. Regresión: 667 passed (router, protocolo,
  banco) y 857 passed (alta, rama, pregunta, gateway, agente, botones...); tres dobles de
  prueba con firma vieja se actualizaron.
- T2: `tests/test_redaccion_historial.py`: 14 failed, 1 passed; GREEN 16 passed. Regresión:
  1103 passed (alta, banco, charla, gateway, pregunta, rama).
- T3: `tests/test_alta_dejarlo_conserva_el_borrador.py`: 6 failed, 2 passed (los controles
  de cancelar); GREEN 8 passed. Siete pruebas anteriores que afirmaban "Dejarlo cancela el
  borrador" ahora afirman que lo guarda (`test_alta_eleccion_confirmacion`,
  `test_rama_abierta`, `banco/test_corrida` y el escenario `b-0021-i`): 470 passed.
- T4: `tests/test_redaccion_modelo_puro.py`: 12 failed, 1 passed (B); GREEN 13 passed. Las
  pruebas del plazo y del respaldo (`test_redaccion_plazo`, `test_redaccion_a`,
  `test_alta_guiada_variante_a`, `test_alta_guiada_mensaje_entero`, `test_charla_breve`,
  `test_valor_incompleto_variante_a`) corren con el fixture `con_respaldo_de_plantilla`
  (`MODELO_PURO = False`).
- F-A1: `tests/test_despacho_en_orden.py`: 2 failed, 2 passed; GREEN 4 passed (con
  `test_ciclo`, `test_retencion_por_rama`, `test_avisos_admin`, `test_botones`,
  `test_esqueleto`, `test_smoke_runtime`, `test_saludo`: 89 y 242 passed).
- F-C5: `tests/test_resumen_nunca_sin_cierre.py`: 1 failed, 12 passed (la garantía ya
  valía en todos los caminos probados; falló sólo la defensa con un camino que lo pierde);
  GREEN 13 passed.
- F-C1: `tests/test_crear_no_busca_el_titulo.py`: 6 failed, 2 passed; GREEN 8 passed (con
  resolución de referencias y aclaración con botones: 166 passed).
- F-B9: `tests/test_texto_sin_errores_de_tipeo.py`: 2 failed, 2 passed; GREEN 4 passed (con
  `test_router_valor`: 127 passed).

### Decisiones del escritor (a revisar)

- **Pausa sin migración.** La marca `pausado` vive en `terminal_result` de la solicitud
  activa. Alternativa descartada: una columna o un estado nuevo (migración y cambio de
  `check`). Si se prefiere un estado propio, es un cambio chico en `ingreso_tareas`.
- **Retomar.** Mínimo seguro: el próximo "quiero crear una tarea" ofrece "Continuar
  borrador / Cancelar borrador / Empezar otro". Costo: si la persona dejó el borrador
  justamente para pedir OTRA tarea ("ah, y necesito otra tarea para Nahuel"), ahora ve
  ese paso de elección en vez de empezar directo (antes el borrador viejo se cancelaba).
- **Ayuda con la pregunta.** No hay un comando nuevo: un mensaje de ayuda sobre la
  pregunta pendiente es `dudoso` (o `responde`), no `otro_tema`; con `dudoso` sale la
  confirmación "¿Esto es el criterio…?" (Sí / No, es otra cosa). No es la ayuda de F-C3
  (queda para el rediseño) pero ya no pierde nada.
- **Modelo puro: qué sale si falla.** Sólo el aviso neutro; la pregunta que quedó abierta
  no se dice (sin plantilla, como se pidió), así que con una elección con botones la
  persona ve el aviso y los botones sin la pregunta. Lo único que se agrega es el resumen y
  el valor que se pide confirmar (para no confirmar a ciegas). Severidad del incidente:
  media, con aviso a la administración (el aviso neutro promete "quedó registrado para que
  lo revise un administrador"); con un modelo caído puede generar muchos avisos.
- **Historial en la redacción** como transcripción dentro del mensaje, no como turnos.
- **F-A1: causa sin confirmar.** El bloqueo por espacio ya estaba (`485aa5c`) y no cubre
  un listener de un solo hilo; se corrigió el mecanismo que sí se encontró (envío fallido).
  Hay que mirar en `prisma_flujo`, de sólo lectura, `intentos` y `ultimo_error` de las dos
  filas de `message_outbox` del turno de las 08:32:34: si la nota de "Dejarlo" tiene
  `intentos > 0`, es esta causa.
- **F-C5: causa sin aislar** (ver arriba): garantía estructural más incidente.

### Resultado final (conversación con memoria y modelo puro)

- Suite completa (`python -m pytest -q` desde el worktree, runner del checkout principal): **3040 passed, 333 deselected, 0 failed** (23 min 17 s; línea previa 2955).
- Próximo paso: reiniciar el listener del worktree (`PYTHONPATH=src`) y correr "Corrida siguiente 2" del guion. Sin migración.

## Alta conducida por el modelo (2026-10-01, M1-M3)

Chequeo de rumbo (escrito antes de escribir código; enmienda del 2026-10-01 del ADR 0014,
decisión del usuario "que se comporte como vos").

1. Clase de problema: dónde participa el modelo, no la falta de reglas. El alta es un
   formulario de un campo por turno: cada mensaje pasa por una clasificación cerrada que
   se hace sin ver el borrador, y lo que la persona dice de más (varios datos juntos, una
   corrección, una duda) se pierde o se clasifica mal. Ya apareció antes con otra forma:
   la pregunta pendiente como contexto (ADR 0013 regla 1), el historial al ruteo (F-C6),
   "Dejarlo" que destruía el borrador. Es la tercera ronda con la misma clase.
2. Mecanismo general, no caso: un contrato de turno único (el modelo ve conversación +
   borrador + faltantes + opciones permitidas y devuelve valores, intención, texto y
   botones en salida estructurada cerrada); el código valida cada valor contra lo que
   recalcula en ese turno (opciones por id corto, fechas con el día de hoy, límites),
   persiste lo válido, pone los botones y el resumen exacto, y nada se compromete sin
   Confirmar. No hay frase ni palabra clave en el código: se reemplaza el camino, no se
   parcha. Detrás de un interruptor del espacio (`alta = conversada`) para que lo viejo
   siga disponible hasta medir (punto 7 de "Cómo pensamos juntos": lo viejo se retira
   cuando la prueba real lo justifique, no antes).
3. Qué haría innecesaria la próxima ronda: que varios datos en un mensaje, una corrección
   ("no, el responsable es Nahuel"), una duda ("ayudame, ¿qué puedo poner?"), un
   "no sé" o un cambio de tema se resuelvan sin una regla por caso; que dejar el alta o
   cambiar de tema nunca pierda el borrador y no pregunte "¿Seguimos?".
4. Hipótesis vigente: un modelo flash que ve conversación y borrador conduce bien el alta
   si el código le da lo posible y valida lo que devuelve. Es una hipótesis a medir con la
   prueba real "Corrida conversada" del guion, no un hecho. Riesgos declarados: latencia
   (una llamada por turno, sin plazo propio) y el límite de lo que el verificador puede
   comprobar de un texto libre (fechas, nombres y números fuera de los hechos; no el
   sentido).

Prueba real más temprana: M3 (esqueleto andante) en `prisma_flujo` con `alta = conversada`.

### Tareas

- [x] **M1.** (`16fa0ff`) Contrato del turno (`src/prisma/alta_turno.py`, puro): hechos, salida
  estructurada cerrada, validación y aplicación de valores (fechas, ids cortos, límites,
  correcciones, criterio con propuesta).
- [x] **M2.** (`03263de`) `conducir_alta(sistema, historial, hechos)` en los cuatro proveedores (salida
  estructurada forzada), historial a prueba de roles no alternados y una guía de voz.
- [x] **M3.** (`deaade0`, 1969 líneas con pruebas: pasa el heurístico de 400 porque es el
  esqueleto completo y casi todo son pruebas y el módulo nuevo) Esqueleto andante: interruptor
  `alta` del espacio, turno por mensaje y por toque, botones desde el conjunto de opciones,
  resumen del código con frase del modelo, cancelar / dejar / otro tema, una respuesta visible
  por mensaje, falla visible.

### RED observado y verificación (M1-M3)

- M1: `tests/test_alta_turno.py` falló al colectar (`ImportError`, módulo inexistente); GREEN
  97 passed (incluye el RED separado de "Modificar con todo completo" y de "conversación
  permitida en la verificación"). Verificador: `verificar_afirmaciones` extraído sin cambiar
  `verificar` (100 passed en las pruebas del verificador y la redacción).
- M2: `tests/test_conducir_alta_proveedores.py` falló al colectar (`ImportError`); GREEN 19
  passed; con las del ruteo y el protocolo: 376 passed.
- M3: `tests/test_alta_conducida.py` falló al colectar (`ImportError`); GREEN 41 passed.
- Suite completa (`python -m pytest -q`, runner del checkout principal, 24 min): 3195 passed,
  333 deselected, **2 failed**: (1) `test_capacidades::test_las_promesas_sin_cumplir...` por mi
  vocabulario (`intencion` aparece en `src/`): corregida en el commit de M3 excluyendo los
  módulos del alta conducida; (2) `test_redaccion_modelo_puro::test_si_el_verificador_rechaza...`
  es una prueba inestable que ya existía (ordena filas de auditoría por `at`, que es igual
  dentro de una transacción): falló en la suite y pasa sola y en la corrida enfocada.
  Después de la corrección: 169 passed en las pruebas del alta, capacidades, incidentes y
  modelo puro.
- Suite completa repetida (2026-10-01, mismo comando, 22 min): 3196 passed, 333 deselected,
  **1 failed**: otra vez `test_si_el_verificador_rechaza...` (`['aceptada', 'rechazada']`).
  Dos fallas en dos suites completas: no es "intermitente", es un defecto de la prueba. Las
  dos filas de auditoría comparten `at` (`now()` de una sola transacción) y `id` es un
  `uuid` aleatorio, así que la lectura no tiene orden. Corregida comparando sin orden (el
  orden de los intentos ya lo prueba `modelo.hechos`); el código no cambia ni depende de
  ese orden (`resumen_latencia` sólo cuenta). `tests/test_redaccion_modelo_puro.py`: 13
  passed. Con eso la suite queda sin fallas conocidas.

### Revisión RDD de M1-M3 (2026-10-01)

El tramo `b7ed862..f60c3ca` entero (3714 líneas) superó el presupuesto de contexto del
revisor (`lens_context_budget_exceeded`, sin autoridad creada); se revisó commit por commit.
Las cuatro revisiones quedaron aprobadas y reconocidas; la frontera de revisión pasa a
`f60c3ca`.

| Tramo | Linaje | Observaciones (ninguna bloquea) |
|---|---|---|
| M1 `b7ed862..16fa0ff` | `review-fa1481ce471e6c1a` | 1 WARNING, 2 SUGGESTION |
| M2 `16fa0ff..03263de` | `review-7a12ce5c67834bf0` | 1 WARNING |
| M3 `03263de..deaade0` | `review-c76e05130ebb23d3` | 2 WARNING, 3 SUGGESTION |
| docs y prueba `deaade0..f60c3ca` | `review-2ef17df9f6de4697` | 1 SUGGESTION |

Disposición de las WARNING:

- **M1, valores rechazados y texto de éxito** (`alta_turno.py:478`): resuelta por M3, que el
  revisor de M1 no veía: cualquier rechazo convierte el intento en rechazado y se vuelve a
  pedir (`alta_conducida.py:345`).
- **M2, argumentos JSON que no son objeto** (`llm.py:582-587`): inofensiva; `leer_salida`
  rechaza todo lo que no sea un objeto (`alta_turno.py:272`) y el intento se repite.
- **M3, un intento sin fila de auditoría** (`alta_conducida.py:339-344`): si `_completar`
  devuelve un problema de estado real después de guardar, se retorna sin `_auditar`; esa
  llamada falta en la latencia del experimento. Pendiente, chica.
- **M3, el freno de avisos sobrevive a un rollback** (`alta_conducida.py:686-707`): el
  instante del último aviso se fija en memoria antes del incidente; si la transacción
  vuelve atrás, se pierden incidente y aviso, y durante 10 minutos las fallas siguientes del
  espacio se dan por avisadas. Roza "nunca fallar en silencio". Pendiente: fijar el freno
  sólo después de confirmar.

Las SUGGESTION (comparar `acepta_propuesta` con su tipo, cobertura de `verificar` tras el
refactor, caché de Jev sin invalidar, nota del incidente de ajuste anómalo, caminos de falla
sin prueba) quedan como deuda menor de esta rama.

### Decisiones del usuario (2026-10-01)

- **Modelo puro, sin red** en el alta conducida: sin plazo propio ni plantillas que tapen al
  modelo; ante una falla, el aviso neutro (constitución §10) y el incidente. Confirma la
  decisión del escritor de abajo.
- **Primero fluidez y facilidad de uso, después latencia** (tras la primera corrida
  conversada: "fluidez increíble", latencias de 5 a 58 s por respuesta). El criterio de 5 s
  del ADR 0014 sigue vigente: cambia el orden, no el criterio. Hasta que el alta conversada
  funcione de punta a punta, los hallazgos de latencia se registran y no se atacan; los
  reintentos por contrato sí se corrigen, porque son a la vez fallas de uso.
- **El tope de 7 botones no es una decisión real:** CoreWork tiene 5 objetivos operativos, a
  lo sumo 2 por área, y el alta ofrece sólo los del área de quien pide. El tope de 40
  opciones es un techo técnico. Un objetivo es algo a cumplir con muchas tareas debajo; más
  de ~4 por persona sería inmanejable.

### Decisiones del escritor (a revisar)

- **Interruptor:** `workspace_setting` `alta`, valor `"conversada"` (o `{"modo": "conversada"}`);
  ausente o `"guiada"` es el alta de siempre; un valor desconocido es lo de siempre más un
  incidente (`interruptor_alta`).
- **Sin plazo propio, siempre:** `MODELO_PURO=False` no restaura nada en el alta conducida.
- **La propuesta de criterio ya hecha** vive en `terminal_result` de la solicitud
  (`criterio_propuesto`), junto a la pausa, sin cambiar el esquema; `prisma_app` no puede leer
  `audit_log`.
- **Botones:** hasta 7 por dato; el modelo conoce todas las opciones (hasta 40).
- **Modificar** del resumen no abre el selector: lo conversa el modelo.
- **Verificación del texto:** puede repetir lo ya dicho en la conversación y nombrar los botones
  del resumen; no puede inventar fechas, números ni nombres.
- **Fallas:** incidente `alta_conducida_fallida` (media) por cada una; aviso a la administración
  uno por espacio cada 10 minutos. Tras una falla: aviso neutro + "Pendiente: el dato" (con
  botones si es objetivo o responsable; el resumen si ya estaba todo).
- **Pendiente:** el área sigue saliendo de quien es responsable; sin Jev, los objetivos salen sin
  ⭐ y queda el incidente de siempre.

Ruta declarada: un solo escritor (el encargo lo pidió así); disparador de escritura de 2+
archivos no triviales cubierto por esa instrucción explícita.
TDD: estricto (configuración global del usuario); runner
`D:\Proyectos\Prisma-PM\.venv\Scripts\python.exe -m pytest` desde el worktree.
Delivery: ~400 líneas por commit como heurística; M1, M2 y M3 (posible M3a/M3b) son
unidades de commit propias.

### Hallazgo de la corrida conversada: propuesta sin registro (2026-10-01)

- **Causa.** El contrato daba dos caminos para aceptar un criterio propuesto: `{acepta_propuesta: true}`
  (sólo válido con una propuesta registrada) y mandar el texto (la guía lo pedía para la propuesta hecha
  sólo en la charla). El modelo usó el primero con una propuesta no registrada; `_criterio` lo rechazó
  ("no hay una propuesta vigente para aceptar") en cada intento y el alta cayó al aviso neutro: callejón
  sin salida. Regla ADR 0013 "estado real": el contrato ofrecía una acción que el estado no siempre permite.
- **Arreglo (mecanismo).** `acepta_propuesta` se retiró del contrato (`_CLAVES_DEL_CRITERIO`, esquema de
  `conducir_alta`, `leer_salida`, `_criterio`). Hay un solo camino: aceptar una propuesta (registrada o
  hecha en la charla) es mandar su texto como `texto` del criterio; un criterio `proposed` pasa a
  `confirmed` por el camino normal (`_ya_confirmado` sólo frena a `confirmado`). `SISTEMA_ALTA` describe
  ese camino. `llm.py` no duplica este esquema (importa de `alta_turno`).
- **RED.** `tests/test_alta_turno.py tests/test_alta_conducida.py`: 2 failed, 141 passed (la clave retirada
  sin rechazar en `leer_salida`, y la guía/esquema que aún la nombran). Los casos de extremo a extremo con
  `{texto}` ya pasaban antes: confirman que ese camino es el que funciona.
- **GREEN.** `tests/test_alta_turno.py tests/test_alta_conducida.py tests/test_conducir_alta_proveedores.py
  tests/test_capacidades.py tests/test_redaccion_modelo_puro.py`: 178 passed.
- **Pruebas cambiadas.** `test_aceptar_la_propuesta_confirma_el_texto_guardado...` pasó a
  `test_aceptar_la_propuesta_vigente_es_mandar_su_texto_como_criterio`; se quitó
  `test_aceptar_sin_propuesta_vigente_se_rechaza` (ya no hay acción de aceptar); el caso de
  `acepta_propuesta` suelto se suma a los rechazos de formato; en
  `test_un_criterio_que_no_se_puede_comprobar_se_propone_otro_y_se_acepta` el modelo acepta con `{texto}`.

### Hallazgo: el verificador cuidaba estilo, no sólo invariantes (2026-10-01)

- **Caso observado.** En una prueba real la persona tocó Modificar y dijo "cambiá la fecha al 15 de
  agosto" (una fecha pasada). El código rechazó el valor, con razón, y el modelo, con razón, pidió otra
  fecha. `verificar_turno` rechazó los dos intentos con `pregunta_fuera_de_faltan: due_date`: la fecha no
  "faltaba" (seguía guardada la vieja del viernes). La persona recibió el aviso neutro de falla. De 10
  intentos rechazados ese día, 6 eran reglas de estilo.
- **Razonamiento del disparador (AGENTS.md, "Cómo pensamos juntos", punto 4).** Se iba a agregar un segundo
  caso especial junto al de Modificar (`h.evento.get("toque") != "modificar"` en `pregunta_sin_falta`), y era
  el segundo arreglo seguido en este módulo. Se paró y se revisó el mecanismo, no el caso. Punto 6: "las
  instrucciones gobiernan el comportamiento; el código y la base, lo que no puede pasar nunca". Las reglas de
  estilo heredadas del alta por formulario no son garantías: rechazan comportamiento correcto del modelo.
- **Decisión del usuario.** El verificador del alta conducida guarda sólo invariantes y coherencia de la
  interfaz de texto.
- **Se conserva.** `verificar_afirmaciones` (ni fechas, números ni nombres inventados; largo);
  `falta_pregunta` (si algo sigue faltando tras el turno, la respuesta pregunta: ningún mensaje deja a la
  persona sin próximo paso); `botones_sin_pregunta` (los botones son de un dato por el que la respuesta
  pregunta: lo que se muestra coincide con lo que se dice); los retornos tempranos `otro_tema`, `cancelar`
  y `dejar`.
- **Se quita.** `pregunta_fuera_de_faltan` (preguntar por un dato que no falta, por ejemplo uno que se
  corrige); `pregunta_sin_falta` con su excepción de Modificar (preguntar sin que falte nada);
  `botones_fuera_de_faltan` (botones de un dato que se corrige). `SISTEMA_ALTA` ya no dice "sólo de lo que
  falte DESPUÉS de este mensaje": pedí lo que falta; si la persona cambia un dato o un valor se rechazó,
  podés volver a pedirlo.
- **Botones de un dato confirmado.** Las opciones siguen saliendo sólo del conjunto del código
  (`_opciones_de_ahora`). El toque (`conducir_toque`) guarda con `_guardar` directo, sin pasar por
  `_ya_confirmado`: no hace falta `corrige` para que un toque aplique. Sí había un hueco en `_responder`: con
  nada faltando, la rama `not faltan` devolvía antes de armar `salida.botones`, así que el texto prometía
  botones que no salían. Arreglo mínimo: con nada faltando y sin cambio aplicado, los botones se arman; con un
  cambio aplicado sigue saliendo el resumen. Además, una pregunta del modelo (`salida.pregunta`) con nada
  faltando ya no arma el resumen detrás de la pregunta: se dice la pregunta y el resumen vuelve cuando se
  aplica un cambio (antes, tras Modificar, la pregunta habría salido pegada a un resumen con Confirmar).
- **Riesgo aceptado.** El modelo puede volver a preguntar un dato ya confirmado, o preguntar sin que falte
  nada. Ninguna garantía se rompe: el código sigue validando cada valor, el límite de autoridad de las
  opciones y el botón Confirmar como único camino a la tarea. Tras una pregunta con nada faltando la persona
  queda sin resumen a la vista hasta su próxima respuesta.
- **RED.** `tests/test_alta_turno.py tests/test_alta_conducida.py`: 11 failed, 140 passed (9 de unidad:
  pregunta de dato confirmado, pregunta con nada faltando, valor rechazado de fecha, objetivo y responsable
  que se vuelve a pedir, botones de objetivo y responsable confirmados, y el motivo `botones_sin_pregunta`;
  2 de extremo a extremo: Modificar + fecha pasada, y Modificar + botones de responsable + toque).
- **GREEN.** `tests/test_alta_turno.py tests/test_alta_conducida.py tests/test_conducir_alta_proveedores.py
  tests/test_capacidades.py tests/test_redaccion_modelo_puro.py`: 186 passed;
  `tests/test_verificador_redaccion.py` (otro verificador, el del camino anterior, con su propio
  `pregunta_sin_falta` que no se toca): 68 passed.
- **Pruebas cambiadas.** `test_la_pregunta_tiene_que_ser_de_algo_que_falta` pasó a
  `test_se_puede_preguntar_por_un_dato_que_ya_esta_confirmado`;
  `test_lo_que_se_acaba_de_completar_ya_no_se_puede_preguntar` pasó a
  `test_preguntar_por_lo_que_se_acaba_de_completar_no_lo_rechaza_el_verificador`; en
  `test_con_todo_completo_el_texto_no_pregunta` la aserción de `pregunta_sin_falta` pasó a
  `test_con_todo_completo_una_pregunta_no_se_rechaza`; `test_los_botones_son_de_un_dato_con_opciones_y_que_se_pregunta`
  espera ahora `botones_sin_pregunta` (el caso de botones de un dato confirmado ya no se rechaza). Todas
  afirmaban reglas retiradas.
- **Hallazgos pendientes de la misma corrida (no se arreglan ahora).**
  - (a) Con `intencion: dejar`, la respuesta prometió "la retomamos el lunes": un compromiso a futuro para el
    que Prisma no tiene mecanismo (constitución §4).
  - (b) Tras pausar, "¿qué tarea dejaste para el lunes?" fue al camino general, que no conoce el borrador
    pausado y ofreció tareas que no tenían que ver.

### Tanda 1-4 de la corrida conversada (2026-10-01)

Cuatro defectos de la corrida real por Telegram. Chequeo de rumbo: los cuatro son la misma clase que ya
apareció (el contrato o el flujo prometen lo que el estado no hace, ADR 0013 "estado real y sólo opciones
posibles"; "una respuesta visible por mensaje"); se arreglaron los mecanismos, no las frases observadas.
Ruta declarada: un solo escritor (encargo explícito). TDD estricto; runner
`PYTHONPATH=src ...\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`.

- **1a. El botón que el texto nombra.**
  - *Causa.* El modelo decía "confirmá con el botón Confirmar" aunque el resumen de quien necesita
    aprobación trae Enviar a aprobación; la guía fijaba "Confirmar" y los hechos no decían qué botón saldría.
  - *Mecanismo.* El código calcula el botón de cierre con la política que ya decide el resumen
    (`ingreso_tareas.boton_final_de`, que usa `requiere_aprobacion`, la misma comparación de `_finalize`) y
    lo expone en los hechos: `boton_final` en cada opción de `responsible` y arriba cuando el responsable ya
    está confirmado (`alta_turno.OpcionAlta.boton_final`). `BOTONES_DEL_RESUMEN` se reemplazó por
    `BOTONES_SIEMPRE` (Modificar, Cancelar) más el botón aplicable; el verificador rechaza con
    `boton_inexistente: X` un botón de cierre que el texto nombra (con mayúscula, en medio de una oración) y
    el resumen no va a mostrar, contando el responsable que el propio turno asigna (`boton_final_tras`). Sin
    responsable determinado no se nombra ninguno. `SISTEMA_ALTA` remite a `boton_final`.
  - *RED.* `tests/test_alta_turno.py tests/test_alta_conducida.py tests/test_conducir_alta_proveedores.py
    tests/test_capacidades.py tests/test_redaccion_modelo_puro.py`: 26 failed, 188 passed (todo el RED de la
    tanda junto; de esos, 17 son de este ítem).
- **1b. Las fechas.**
  - *Causa.* El esquema decía "tomada de `hoy` y `proximos_dias`" y el modelo concluyó que sólo valían esos 14
    días ("pasame una fecha dentro de los próximos días" ante "el 15 de agosto"). El código acepta cualquier
    fecha desde hoy (`validar_valor` con `hoy`).
  - *Mecanismo.* La regla real está en los hechos (`fechas`, `REGLA_DE_FECHAS`), en el esquema y en la guía:
    cualquier fecha desde hoy en adelante, una pasada no vale, `proximos_dias` es una ayuda de calendario y no
    un límite. El verificador ya dejaba nombrar una fecha asignada fuera de la ventana (`mostrado`) o dicha
    por la persona (`evento`): se agregaron pruebas (3 fechas lejanas y una pasada rechazada) que ya pasaban.
  - *RED.* 1 failed (la regla en hechos/esquema/guía); las pruebas de aceptación y de verificador pasaban
    antes: confirman que el límite estaba sólo en el texto del contrato.
- **2. Una frase del modelo es de la persona para la que se escribió.**
  - *Causa.* `_finalize` guardaba `resumen.cuerpo` (con la apertura del turno de quien pide) en los `args` de
    la revisión, y Enviar a aprobación se lo mandaba tal cual a quien confirma.
  - *Mecanismo.* Con `apertura`, el cuerpo que se guarda para quien confirma es el del resumen sin esa frase
    (`render_resumen(**datos).cuerpo`, el encabezado "Resumen para revisar" y los datos que también recibe
    quien confirma en el alta guiada con plantilla B; en el alta guiada no se tocó nada). Quien pidió conserva
    su resumen con su frase; quien confirma recibe los datos con el cierre de SU botón.
  - *RED.* 1 failed (extremo a extremo: resumen con apertura y luego Enviar a aprobación; el cuerpo del
    aprobador no debe llevar la apertura y debe llevar los datos y su cierre).
- **3. Una respuesta visible por mensaje.**
  - *Causa.* El aviso de la pausa (`dejar_nota`) y la respuesta del camino normal eran dos filas del mismo
    grupo: una sola respuesta para el control, pero dos mensajes de Telegram.
  - *Mecanismo.* `dejar_nota(..., unida=True)`: `respuesta_unica.controlar` antepone la nota al texto del
    primer mensaje de la respuesta que conserva (`_unir_al_mensaje`, el mismo patrón de
    `_offer_current_review`: si juntos no entran en un mensaje, sale como parte aparte del mismo grupo). Sólo
    lo usa `_atender_otro_tema_del_alta`; el aviso de "dejarlo y ver lo otro" del alta guiada sigue siendo
    una parte aparte (no cambia el guiado).
  - *RED.* 5 failed (la prueba existente de otro tema y 4 nuevas: 3 mensajes distintos de la familia y el caso
    que no entra junto).
- **4. Rechazos diagnosticables sin guardar conversación.**
  - *Causa.* Un intento rechazado guardaba sólo el motivo; no se veía por qué `falta_pregunta: el objetivo`
    caía en el primer mensaje de cada alta.
  - *Mecanismo.* La auditoría `alta_conducida_turno` de un intento rechazado lleva `salida` con la forma
    estructural (`_forma_de`): `intencion`, `pregunta`, `botones`, los nombres de `valores` y `corrige`,
    `texto_tiene_pregunta`, `texto_largo` y `faltan_tras` (nombres de datos que seguían faltando; agregado
    porque es lo que decide `falta_pregunta` y no es texto libre). Ningún texto del modelo ni de la persona;
    con formato roto sólo el motivo, como antes. `falta_pregunta` no se tocó.
  - *RED.* 2 failed (forma estructural sin texto libre; formato roto sólo con motivo).
- **Hallazgo del ítem 4: el primer mensaje.** Sin evidencia todavía. Los hechos del primer turno
  (`arrancar`) se arman con el mismo `_hechos` que cualquier turno: mismas claves, mismo `evento`
  (`mensaje_de_la_persona`), `faltan` completo y conversación vacía (prueba
  `test_los_hechos_del_primer_mensaje_son_los_de_cualquier_turno`, que ya pasaba). Hipótesis a confirmar con
  la próxima corrida y el nuevo `salida` de auditoría, ninguna probada: (1) el modelo, al abrir el alta con un
  mensaje que trae el título, contesta "anotado" y deja `botones="objective"` sin `pregunta` o sin signo de
  pregunta, y con la conversación vacía no tiene un ejemplo previo del formato; (2) en el intento 2 los
  valores válidos del intento 1 ya se guardaron (`_guardar` corre antes de verificar), así que el modelo ve
  el título confirmado con sólo el motivo y puede repetir la omisión. La auditoría nueva distingue las dos
  (`pregunta` vacía, `botones` puesto, `texto_tiene_pregunta`).
- **Pruebas existentes cambiadas.** `test_los_botones_del_resumen_se_pueden_nombrar` pasó a las familias
  `test_los_botones_que_el_resumen_va_a_mostrar...` (el botón nombrable ahora depende de `boton_final`);
  `test_la_guia_de_voz_dice_lo_esencial` pide `boton_final` y no "Confirmar" (la guía ya no lo fija);
  `test_una_duda_con_el_resumen_a_la_vista_no_arma_otro_resumen` hace que el modelo nombre Enviar a
  aprobación (el botón real de ese mundo; con Confirmar ahora se rechaza con razón);
  `test_otro_tema_pausa_el_borrador...` espera un solo mensaje (aviso + respuesta).
- **Hallazgos pendientes de la misma corrida (sin arreglar).**
  - Los nombres de la evidencia en el resumen salen con las claves crudas ("explicacion, captura").
  - El modelo aceptó "envío videos" como criterio de aceptación: es evidencia, no un resultado verificable
    (mecánica §13, pregunta 2). Es comportamiento del modelo: medirlo con el banco antes de tocar la guía.
  - La rama de aclaración falsa tras una pausa queda abierta y reaparece.
  - (a) y (b) de la entrada anterior (promesa a futuro con `dejar`; la pausa que el camino general no
    conoce) siguen sin arreglar.
- **GREEN (toda la tanda).** `tests/test_alta_turno.py tests/test_alta_conducida.py tests/test_conducir_alta_proveedores.py tests/test_capacidades.py tests/test_redaccion_modelo_puro.py`: 214 passed. Alta guiada y caminos vecinos (`tests/test_task_intake.py`, `test_alta_guiada_variante_a`, `test_alta_modificar`, `test_alta_enviar_a_aprobacion`, `test_alta_eleccion_confirmacion`, `test_alta_estado_real`, `test_alta_guiada_mensaje_entero`, `test_aviso_incidente_legible`, `test_despacho_en_orden`, `test_pregunta_pendiente_otras`, `test_rama_vista_previa`, `test_respuesta_unica_caminos`, `test_rama_abierta_guarda`, `test_rama_abierta`, `test_rama_eleccion`, `test_router_historial`, `test_router_pendiente`, `test_una_respuesta`, `test_toque_idempotente`): 637 passed. No se corrió la suite completa.

### Revisión RDD de las correcciones de la corrida (2026-10-01)

Tramo `f60c3ca..51fa9e6` (`81bb60a`, `9d1bee2`, `20cd9c8`, `51fa9e6`; 994 líneas), linaje
`review-8e3878791b775ddf`: aprobada y reconocida; la frontera de revisión pasa a `51fa9e6`.

- WARNING `alta_turno.py:533-536`: el control `boton_inexistente` no detecta un botón
  nombrado al empezar una oración ("Confirmar crea la tarea."). Real y chica; pendiente.
- WARNING `respuesta_unica.py:190-191` (nota unida perdida sin respuesta): no se cumple.
  Sin respuesta, `controlar` encola el aviso neutro, relee las respuestas y recién después
  une las notas; la nota de la pausa sale igual.
- SUGGESTION: falta una prueba del caso en que el primer mensaje ya no está `listo` al unir.

### Margen máximo de la fecha de una tarea (ajuste del espacio) (2026-10-01)

- **Decisión del usuario.** La fecha objetivo de una tarea va de hoy a hoy más N meses; N = 2 por
  omisión y es configuración del espacio, no una constante del núcleo. Los objetivos pueden ser más
  largos: la regla es sólo para tareas.
- **Por qué.** Saca la ambigüedad del año. Una fecha sin año tiene a lo sumo UNA lectura válida: la
  próxima que llega dentro del margen. Caso de la prueba real: "para el 15 de agosto" lo resolvió el
  modelo a 2027 (hoy 2026-10-01) y la tarea quedó a casi un año. Ahora eso queda fuera del margen:
  Prisma dice hasta dónde llega una tarea, sugiere dividirla o tomarla como objetivo, y pide una fecha
  dentro del rango. En diciembre, "10 de enero" es el próximo enero sin preguntar nada.
- **Definición.** N meses de calendario: hoy + N meses, recortado al último día del mes
  (2026-12-31 + 2 = 2027-02-28); el límite se incluye (`valores.sumar_meses`).
- **Dónde y cómo se cambia.** Clave del pack `horizonte_tarea: {meses: N}` (en `espacios/corework.yaml`,
  sembrada en 2). El importador la guarda en `workspace_setting['horizonte_tarea']`. La administración
  de plataforma lo cambia editando el pack y volviendo a importarlo (todavía no hay consola). Sin el
  ajuste, 2. Valor inválido: usa 2, deja un incidente (`horizonte_tarea`, una vez por proceso) y el
  importador advierte.
- **Mecanismo.** `ValorEsperado.hasta` y `MotivoRechazo.FECHA_LEJANA` en `valores.py` (razón propia, nombra
  el límite en dd/mm/aaaa). `ingreso_tareas.meses_de_horizonte`/`limite_de_fecha` leen el ajuste;
  `_esperado_del_campo` lo aplica en el alta guiada (valor del ruteo y propuestas del modelo) y
  `alta_turno` en la conducida (`HechosTurno.limite_fecha`, `meses_horizonte`). La regla de fechas de los
  hechos y `SISTEMA_ALTA` reemplazan la de 51fa9e6 ("cualquier fecha desde hoy"); el verificador permite
  nombrar el límite y los meses.
- **Pruebas existentes cambiadas.** `test_los_hechos_dicen_que_sirve_cualquier_fecha_desde_hoy...` pasó a
  `test_los_hechos_dicen_el_margen_de_la_fecha_de_una_tarea` (la regla ahora lleva el límite). Fechas
  fijas lejanas movidas dentro del margen de `NOW` (2028-02-28): `2028-10-04` a `2028-04-04`
  (y "4 de octubre" a "4 de abril") en `test_alta_guiada_flujo`, `test_alta_guiada_mensaje_entero` y
  `test_alta_criterio_verificable`. `test_alta_modificar` (`_modificar`) y `tests/banco/test_corrida.py`
  (`_margen_amplio`) usan fechas fijas con el reloj real: se les da un margen de 120 meses en el
  espacio.
- **RED.** `tests/test_valores_margen.py` y `tests/test_horizonte_tarea.py`: error de importación
  (`sumar_meses` no existía); `tests/test_alta_turno.py`: 6 failed, 123 passed.
- **GREEN.** `tests/test_valores_margen.py tests/test_horizonte_tarea.py tests/test_alta_turno.py tests/test_valores.py`:
  257 passed. Tanda enfocada completa más todo archivo que toca `validar_valor`, `TipoValor.FECHA`,
  importador o fechas objetivo: 1672 passed (9 min), sin fallas; antes de mover fechas fijas de pruebas existentes habia 25 failed, 1647 passed.


### Revisión del margen y hallazgos de la prueba siguiente (2026-10-01)

- RDD `324670a..13c7ae5`, linaje `review-bf6f7c2a3a43c18c`: aprobada y reconocida. Su
  WARNING (un margen enorme, `meses: 100000`, rompía el cálculo del límite en cada pregunta
  de fecha en vez de usar 2 meses con incidente) se corrigió: tope `HORIZONTE_MAXIMO = 120`
  en el lector y en el importador. RED 3 failed (valores 121 y 100000, y el importador),
  GREEN `tests/test_horizonte_tarea.py tests/test_valores_margen.py`: 45 passed. Quedan las
  dos SUGGESTION (la marca de anomalía antes de confirmar la transacción; una aserción que
  no puede fallar en `test_sin_margen_los_hechos_no_ponen_limite_superior`).
- Prueba real 16:02-16:05: fecha, criterio, "Enviar a aprobación" nombrado bien, e Ismael
  recibió sólo el resumen (sin la frase del turno de Marcos) y confirmó. Todo al primer
  intento.
- Hallazgos nuevos, del circuito de aprobación que comparten las dos altas (pendientes):
  (c) cuando quien confirma aprueba el borrador, a quien lo pidió no le llega ningún aviso:
  no sabe que su tarea existe (mecánica §10, avisos de coordinación; el rechazo sí avisa);
  (d) el pedido de aprobación no dice quién lo manda: arranca en "Resumen para revisar".

### Hallazgo: "?" no es una invariante (2026-10-01, prueba con Ismael)

- Observado con la auditoría estructural nueva: el primer mensaje de Ismael se rechazó con
  `falta_pregunta` declarando `pregunta: [due_date, acceptance_criterion]` y
  `texto_tiene_pregunta: False` (pidió en imperativo). A Ismael, de Dirección, el código le
  completó el objetivo (el único que tiene: el estratégico), así que le faltaban fecha y
  criterio; a Marcos le faltaba el objetivo y el modelo preguntó con signos. Es la causa
  probable de los primeros mensajes rechazados de toda la corrida.
- Disparador del punto 4 (tercera corrección de `verificar_turno` en el día): no es un caso
  nuevo sino un resto de la decisión "sólo invariantes" mal clasificado. La invariante es que
  la respuesta pida algo cuando falta un dato, y eso lo declara `pregunta`; el "?" es forma.
  Cambio: `falta_pregunta` comprueba sólo `pregunta` (se descartó exigir que cubra un dato
  faltante: rompía la corrección de un dato confirmado mientras falta otro). RED 4 failed
  (familia de pedidos en imperativo), GREEN 255 passed.
- Repaso completo de los controles que quedan, uno por uno: botón inexistente (estado
  real), texto vacío, llaves y claves internas (opacidad, §10), número, fecha, mes, título
  o nombre que no está en los hechos (§4), botones sin pregunta (lo que se muestra coincide
  con lo que se dice) y largo máximo de 700 caracteres (tope de seguridad, sin rechazos
  observados). Ninguno es de estilo.
- Pendiente (e): alguien de un área sin objetivos operativos (Dirección) recibe el objetivo
  estratégico completado solo; revisar con el usuario si es lo que corresponde.
- Verificado en real (16:44): el primer mensaje de Ismael entró al primer intento tras
  `bdc2905` (pidió el criterio en la misma respuesta).
- Pendiente (f): el modelo ofrece capacidades que Prisma no tiene: "si necesitás más tiempo,
  lo tomamos como objetivo" (no existe; roadmap "Objetivo propuesto desde el alta") y "la
  retomamos el lunes" (pendiente a). Misma clase: prometer algo sin mecanismo (§4).
- Pendiente (g), observado por el usuario: el indicador "escribiendo…" aparece y se va antes
  de la respuesta. Existe el mecanismo del ADR 0011 (`sendChatAction` con refresco y el
  borrador nativo `sendMessageDraft` en privado, `despachador.mantener_chat_activo`); el
  modelo tarda 5-38 s y Telegram apaga el typing a los ~5 s sin refresco. Sin investigar:
  sospecha en el intervalo de refresco o en el retiro del borrador.


### Aviso de aprobación a quien pidió y quién manda el pedido (2026-10-01)

- Resuelve los pendientes (c) y (d) de la prueba real (circuito de aprobación que comparten el
  alta guiada y la conversacional).
- **Causa (c).** La conversión del borrador la hace la función de la autoridad en la base
  (`confirmar_borrador_tarea`), que sólo deja la fila terminal para quien confirma. El rechazo
  sí avisaba a quien pidió (`reject_draft`, aviso de coordinación); la aprobación no tenía
  ningún aviso equivalente: quien pidió no se enteraba de que su tarea existía.
- **Arreglo (c).** `ingreso_tareas.notify_requester_of_approval`, llamada desde
  `gateway._resolver_toque_borrador` cuando el toque convirtió el borrador (no replay): encola un
  aviso de coordinación (`es_coordinacion`, fuera del tope diario, mismo camino de salida y
  estilo que el del rechazo), código y sin modelo, con `dedupe_key`
  `intake:<solicitud>:approved-notice` (una sola vez aunque se repita el toque) y auditoría
  `avisar_aprobacion_ingreso_tarea`. Si quien pidió es quien confirma, no manda nada. Texto:
  `<Quien confirmó> confirmó el borrador de la tarea «<título>»: la tarea quedó creada.` Sin
  migración: no hizo falta un tipo de salida nuevo.
- **Causa y arreglo (d).** El pedido de aprobación arrancaba en "Resumen para revisar" (se arma
  en `_send_to_confirmer`, común a las dos altas). Ahora, si confirma otra persona, se antepone
  `<Nombre> te manda esta tarea para que la confirmes.` más una línea en blanco; el resumen y
  el cierre de quien confirma no cambian, y el resumen de quien pidió tampoco.
- **RED.** `tests/test_aviso_de_aprobacion.py` (nuevo): 4 failed, 1 passed (el de
  autoaprobación, que protege que no se agregue un aviso de más); `test_alta_enviar_a_aprobacion`:
  1 failed (línea de quien pide); `test_alta_conducida`: 1 failed (misma línea, alta
  conversacional). Total 6 failed.
- **GREEN.** Tanda enfocada (los tres archivos del circuito, `test_task_intake`,
  `test_avisos_de_coordinacion_fuera_del_tope`, `test_alta_turno`, `test_salida`,
  `test_rechazar_borrador`, el banco y todo archivo que menciona "Enviar a aprobación",
  `confirmar_borrador`, `send_to_confirmer` o `_offer_review`): primera corrida 780 passed,
  2 failed (dos pruebas existentes que comparaban el texto de quien confirma);
  corregidas, esos archivos más los nuevos: 64 passed.
  Existentes cambiados: `test_alta_enviar_a_aprobacion` (dos pruebas comparaban el texto de
  quien confirma sin la línea nueva), `test_alta_guiada_variante_a` y `test_alta_guiada_texto`
  (lo mismo: ahora el texto de quien confirma empieza con la línea de quien lo manda) y
  `test_alta_conducida` (el aprobador ve la línea y luego el resumen).
- Pendientes (c) y (d): resueltos.


### Aviso de asignación al responsable (2026-10-01)

- **Hallazgo (prueba real).** Ismael creó una tarea para Ariel y Marcos una para Nahuel;
  cada uno la confirmó directo (es el aprobador de ese responsable). Ni Ariel ni Nahuel
  recibieron nada: no existía ningún aviso de asignación. Que Ismael no se entere de la
  tarea de Nahuel es por diseño (mecánica §7: la autoridad del espacio no aprueba tareas
  menores; el pack dice que Marcos aprueba a Nahuel).
- **Arreglo.** `ingreso_tareas.notify_responsible_of_assignment`, llamada desde
  `gateway._resolver_toque_borrador` junto al aviso de aprobación (toque que convirtió el
  borrador, no replay; vale para el alta guiada y la conversacional, que convergen ahí):
  encola un aviso de coordinación (`es_coordinacion`, fuera del tope diario), de código y
  sin modelo, con `dedupe_key` `intake:<solicitud>:assigned-notice` y auditoría
  `avisar_asignacion_ingreso_tarea`. No manda nada si el responsable es quien confirma o
  quien pidió (a quien pidió ya le llega el aviso de aprobación). Texto: `<Quien pidió> te
  asignó la tarea «<título>», para el <dd/mm/aaaa>. Se da por hecha cuando: <criterio>.`
  Sin botones ni acciones nuevas. Responsable sin chat activado (constitución §7): no se
  encola nada, igual que `herramientas._avisar`, pero queda la auditoría
  `omitir_aviso_asignacion_ingreso_tarea` con `motivo: sin_chat`. Sin migración.
- **Límite.** Hoy el selector sólo ofrece a quien pide y a sus reportes, y la autoridad
  exige que confirme el aprobador del responsable: un responsable distinto de quien pide
  Y de quien confirma no se alcanza desde la interfaz. La regla se prueba a nivel de la
  función; el caso real es el Confirmar directo.
- **RED.** `tests/test_aviso_de_asignacion.py` (nuevo): 7 failed, 2 passed (los dos que
  protegen que no se avise de más).
- **GREEN.** Los 9 del archivo nuevo; tanda enfocada (nuevo, `test_aviso_de_aprobacion`,
  `test_alta_enviar_a_aprobacion`, `test_alta_conducida`, `test_rechazar_borrador`,
  `test_task_intake`, `test_avisos_de_coordinacion_fuera_del_tope`, `test_salida` y todo
  archivo que menciona "Hecho. La tarea quedó comprometida", `confirmar_borrador` o
  `_resolver_toque_borrador`): 498 passed. Ninguna prueba existente cambió.
- RDD `8cf3fa7..3bd7f85`, linaje `review-bcbc908a89c8c112`: aprobada y reconocida. Sus dos
  WARNING se corrigieron: (1) los avisos de aprobación y de asignación corrían en la misma
  transacción que la respuesta de quien confirma; si uno fallaba, se perdía también
  "Hecho" y el toque siguiente era repetición (nada se reintentaba, falla silenciosa).
  Ahora cada aviso va en su savepoint (`gateway._aviso_aislado`) y, si falla, queda un
  incidente `aviso_coordinacion`; (2) el aviso de asignación no nombra la fecha si la
  tarea no tiene (un espacio puede no exigirla). RED 2 failed, GREEN 135 passed
  (asignación, aprobación, enviar a aprobación, incidentes legibles, rechazo, conducida).
- Pendiente (h) (RESUELTO, ver "Estado real para quien confirma, evidencia legible e íconos"): si el responsable no activó su chat, el aviso no sale y sólo queda en la
  auditoría; a quien creó la tarea no se le dice que el otro no se enteró.


### Chequeo de rumbo: el camino general ve el borrador pausado (2026-10-01)

Hallazgo de la prueba real (pendiente (b)): tras pausar el borrador, "¿qué tarea dejaste para el lunes?" fue al
camino general, que sólo conoce `task`, y abrió una aclaración con tareas ajenas que quedó como rama abierta.
Diseño B elegido por el usuario. Ruta declarada: un solo escritor (encargo explícito); TDD estricto.

- **¿Qué clase de problema es, y ya apareció?** Coexistencia entre el flujo nuevo y el camino viejo (punto 7): el
  alta conducida creó un estado (el borrador pausado) que el camino general no conoce. Ya apareció con otra forma:
  la rama falsa tras una pausa y el "Ya hay un borrador" que nunca se alcanzaba. En todas, un camino decide sin un
  hecho que otro camino creó.
- **¿Mecanismo general o caso?** Mecanismo: una sola función (`ingreso_tareas.borrador_pausado`) da el hecho a quien
  interpreta (ruteo y modelo que responde), y el ruteo devuelve un comando de la lista cerrada (ADR 0013 regla 1)
  que el código ejecuta con el menú que ya existe. Ninguna lista de frases.
- **¿Qué haría innecesaria la próxima ronda?** Que cualquier camino que interprete un mensaje reciba los hechos de
  la persona (borrador guardado) en vez de inferirlos de lo que ve. Si el hallazgo vuelve con otra forma (otra rama
  que el camino general no ve), el mecanismo no alcanza y hay que revisar la precedencia de ramas, no el caso.
- **¿Sigue valiendo la hipótesis?** Sí: la lección del día es que el modelo interpreta bien cuando tiene los
  hechos; acá le faltaba uno. Se mide en la próxima prueba real, no se presume.

### El camino general ve el borrador pausado (diseño B, 2026-10-01)

- **Causa.** Pausar un borrador (`pause_request`) lo saca de las ramas abiertas, así que el mensaje siguiente va al
  camino general (`_turno` → `_rutear` → Jev contra `task`). Ahí nada sabía que el borrador existía: "¿qué tarea
  dejaste para el lunes?" abrió una aclaración con tareas ajenas (rama abierta falsa) y el menú "Ya hay un borrador
  en curso" nunca se alcanzaba.
- **Diseño (un solo mecanismo).**
  1. `ingreso_tareas.borrador_pausado(cur, quien, chat_id=None)`: la única lectura del estado (id y título
     confirmado, o `None`), con `_TITLE_OF_REQUEST`.
  2. El hecho llega como dato al ruteo (`route_intent(..., borrador_pausado=hecho)`, en los tres proveedores y en
     `ProveedorGuionado.borradores_pausados`) y al modelo que responde (bloque "Borrador de tarea guardado" en
     `contexto.construir`). Línea exacta: `La persona tiene guardado, en pausa, el borrador de la tarea «<título>».`;
     sin título: `La persona tiene guardado, en pausa, un borrador de tarea que estaba armando.`
  3. Comando cerrado nuevo `IntentAction.PAUSED_DRAFT` (`paused_draft`): sólo está en el esquema del ruteo y en su
     sistema cuando hay hecho. El código lo ejecuta en `_seguir_camino_normal`, antes de Jev: reutiliza
     `_iniciar_alta_guiada` → `ingreso_tareas.start` y su menú (Continuar borrador / Cancelar borrador / Empezar
     otro), con la pregunta redactada por el código en UNA respuesta: `Quedó guardado el borrador de la tarea
     «<título>». Elegí cómo seguir.` (sin título: `Quedó guardado un borrador de tarea que estabas armando. Elegí
     cómo seguir.`). Pedir crear una tarea sigue por `start_task_intake` y su texto de siempre.
  4. Red de seguridad: un `paused_draft` sin borrador (o con Modificar de por medio) se atiende como
     conversación normal.
- **Deliberadamente no se hizo.** (A) Ampliar el conjunto de candidatas de Jev con el borrador (descartado por el
  usuario). Ni se tocó la precedencia de las ramas abiertas: sin la aclaración falsa no hay rama que la discuta.
  Tampoco listas de frases: el ruteo decide el comando y el código sólo lo ejecuta. El hecho sólo se le da al
  ruteo del camino general (`_turno` sin pregunta abierta); el ruteo contra una pregunta pendiente no lo recibe.
- **Límite conocido.** "Empezar otro" desde `paused_draft` abre el alta con el texto de la pregunta como mensaje
  de origen (igual que con "quiero crear una tarea" abre con ese texto); el modelo conducido pregunta lo que falte.
- **RED.** `tests/test_borrador_pausado_camino_general.py` (nuevo): 9 failed, 1 passed (el de "sin borrador
  pausado", que protege que no cambie el camino general).
- **GREEN.** El archivo nuevo, 11 passed. Tanda enfocada (`test_alta_conducida`, `test_alta_dejarlo_conserva_el_borrador`,
  el nuevo, `test_rama_abierta`, `test_rama_eleccion`, `test_rama_abierta_guarda`, `test_aclaracion_botones`,
  `test_resolucion_referencias`, `test_task_intake`, `test_alta_turno`, `test_una_respuesta` y todo archivo con
  `_bloque_contexto_referencias`, `_resolver_referencias_del_turno` o `START_TASK_INTAKE`): primera corrida 897
  passed, 2 failed (dobles de ruteo sin el parámetro nuevo); corregidos, los archivos afectados (dejarlo, el nuevo,
  `banco/test_corrida`, `test_llm_protocol`, `test_task_intake`): 331 passed. No se corrió la suite completa ni el
  banco real (`modelo_real`).
- **Pruebas/dobles cambiados.** `tests/test_task_intake.py::_RoutingProvider.route_intent` y
  `tests/banco/corrida.py::ProveedorGrabador.route_intent` aceptan `borrador_pausado` (el segundo lo reenvía y lo
  anota en la grabación sólo si viene); ninguna aserción existente cambió. Los replays del banco no traen hecho, así
  que no cambian.
- Pendiente (b) de la corrida del 2026-10-01 ("la pausa que el camino general no conoce"): resuelto. Falta
  confirmarlo en una prueba real por Telegram.
- RDD `3bd7f85..7faead3` (cuatro lentes), linaje `review-9b9e456cc4c197c1`: aprobada y
  reconocida. Corregido después: (1) el contexto de quien responde leía el borrador pausado
  de cualquier chat y el ruteo sólo del chat actual (en un grupo, el modelo podía nombrar un
  borrador sobre el que el código no actúa): ahora `contexto.construir` recibe el `chat_id`
  del turno; (2) el incidente `aviso_coordinacion` no decía qué aviso falló ni de qué
  pedido: ahora nombra al destinatario (pasado de forma explícita, no por el nombre de la
  función) y apunta al `pending_action`. RED 2 failed, GREEN 139 passed. (3) Por qué salió
  `source_draft_id` de `PROMESAS_SIN_CUMPLIR` (`cfa5450`): el aviso de asignación lo lee
  para ir del borrador a la tarea (`ingreso_tareas.py`, `join task t on t.source_draft_id`)
  y el esquema lo completa al convertir; la trazabilidad dejó de ser una promesa.
  Quedan las SUGGESTION (imports locales, comentario de la etapa, conteo del RED, probar
  que si falla el primer aviso el segundo sale).
- Verificado en real (18:47-18:49): con el borrador pausado, "¿qué tarea dejaste guardada?"
  respondió el borrador con Continuar / Cancelar / Empezar otro en un solo mensaje, sin
  aclaración equivocada; Cancelar lo canceló. Pendiente (b) cerrado en real.
- Pendiente (i), visual (RESUELTO, ver la misma entrada): en ese menú "Continuar borrador" y "Empezar otro" salen sin ícono
  (Cancelar sí lo tiene).

### Lo que Prisma puede ofrecer, como hecho (2026-10-01)

- **Causa.** En el alta conducida el modelo no sabía qué puede ofrecer Prisma en ese punto y rellenaba con lo que
  haría una persona: con `dejar`, "la retomamos el lunes"; tras una fecha fuera del margen, "lo tomamos como
  objetivo". Ninguna de las dos existe (constitución §4). Además tres textos escritos por el código lo sugerían
  ellos mismos: `regla_de_fechas`, la guía `SISTEMA_ALTA` y el rechazo `FECHA_LEJANA` de `valores.py`.
- **Arreglo (un hecho, no una regla del verificador).** `alta_turno.lo_que_se_puede_ofrecer(h)` arma, con el estado
  del turno, una lista cerrada que `hechos_a_json` entrega como `podes_ofrecer`: guardar el borrador (se retoma
  cuando la persona lo pida), cambiar cualquier dato, cancelar la tarea; con todo completo y responsable conocido,
  "el botón <boton_final> del resumen" (reusa `HechosTurno.boton_final`); con margen de fecha, "elegir una fecha
  hasta el <límite>, o dividir el trabajo en tareas más cortas". Se retiró "tomarlo como un objetivo" de los tres
  textos. Línea nueva en `SISTEMA_ALTA`: ofrecer sólo lo de `podes_ofrecer` y no prometer acciones futuras que no
  estén ahí (retomar un día, recordar, crear un objetivo). La respuesta de `dejar` la escribe el modelo, así que la
  misma lista la cubre; el camino general (`contexto.py`) sólo da el hecho del borrador pausado y la oferta de
  seguirlo es un texto del código sin día, por lo que no cambió.
- **Deliberadamente no se hizo.** Un chequeo del verificador que detecte promesas en el texto libre (decisión del
  usuario: nada de reglas por frases; el verificador sigue con invariantes). Tampoco se ofrece crear un objetivo
  (congelado), retomar en un día dado ni recordatorios a pedido.
- **Límite honesto.** Esto guía al modelo; una prueba unitaria no puede demostrar que dejará de prometer. La
  verificación es la próxima corrida real por Telegram.
- **RED.** `tests/test_alta_turno.py` + `tests/test_valores_margen.py`: 11 failed (10 nuevos y el existente que
  exigía "objetivo" en la regla de fechas), 146 passed.
- **GREEN.** Los dos archivos, 157 passed. Tanda enfocada (`test_alta_turno`, `test_alta_conducida`,
  `test_conducir_alta_proveedores`, `test_horizonte_tarea`, `test_borrador_pausado_camino_general`,
  `test_capacidades`, `test_valores_margen`): 278 passed. No se corrió la suite completa.
- **Pruebas cambiadas.** `test_los_hechos_dicen_el_margen_de_la_fecha_de_una_tarea` ahora afirma que la regla NO
  nombra "objetivo" (afirmaba la oferta retirada).
- Pendientes (a) y (f): corregidos, pendientes de verificar en real.

### Sólo opciones posibles en la fecha fuera del margen (2026-10-01)

- **Hallazgo (Telegram real, 19:01).** Ante "revisar el variador de la cinta 2, la hago yo, para el 15 de agosto"
  (pasado el horizonte de 2 meses) el modelo respondió que la fecha quedaba fuera del rango, que eligiera otra y que
  "si es mucho para un solo tramo, conviene partirla en tareas más cortas", y en el mismo mensaje preguntó por el
  objetivo. La persona no supo cómo aceptar la división ni dónde aprobarla.
- **Causa.** La lista `podes_ofrecer` (commit `eed3b80`) incluía una opción que nadie puede disparar: dividir la
  tarea no existe. El mismo texto estaba en `regla_de_fechas`, en `SISTEMA_ALTA` y en el rechazo `FECHA_LEJANA` de
  `valores.py`. Además mezclaba dos temas (la fecha rechazada y el objetivo faltante), contra ADR 0013.
- **Arreglo.** Se retiró "dividir / tareas más cortas" de los cuatro lugares. La oferta con margen pasó a: "si la
  fecha no entra: proponer una fecha concreta hasta el límite (por ejemplo el <límite>) para que la persona la
  acepte con un sí, u otra fecha que ella diga". Aceptar la propuesta es mandar su valor (`due_date.fecha_iso`), el
  mismo camino único que el criterio propuesto (`81bb60a`); el límite se incluye y valida. Rechazo `FECHA_LEJANA`:
  "Decime una fecha hasta el <límite> (puede ser esa misma)." Guía nueva en `SISTEMA_ALTA`: si lo rechazado es un
  valor que la persona dio, ocuparse sólo de eso y no preguntar además por otro dato faltante. Es guía más hechos,
  no una regla del verificador (`falta_pregunta` se cumple pidiendo la fecha, que sigue faltando).
- **RED.** Tanda enfocada (`test_alta_turno`, `test_alta_conducida`, `test_valores_margen`, `test_horizonte_tarea`,
  `test_task_intake`, `test_valores`): 6 failed, 403 passed.
- **GREEN.** La misma tanda: 409 passed. No se corrió la suite completa.
- **Pruebas cambiadas.** `test_los_hechos_dicen_el_margen_de_la_fecha_de_una_tarea` (la regla ya no nombra dividir;
  afirma la propuesta aceptada con un sí), la prueba de la oferta con margen (renombrada), `_PROHIBIDO_OFRECER`
  (suma dividir/partir/tareas más cortas) y `test_el_rechazo_por_fecha_lejana_no_ofrece_tomarla_como_objetivo`
  (afirmaba "dividila"). Nuevas: la guía de un tema a la vez y el extremo a extremo en `test_alta_conducida`.
- **Límite honesto.** Guía al modelo; se confirma en la próxima corrida real por Telegram.
- Verificado en real (19:19-19:21, tras `fbe92b3`): fecha fuera del margen → "la dejo para el
  01/12/2026, o decime otra fecha", sólo sobre la fecha; "si" → tomó el límite y recién
  después preguntó el objetivo; "dejala para después" → "lo retomamos cuando quieras", sin
  prometer un día; el menú del borrador y Cancelar, bien. Cuatro turnos, todos al primer
  intento. Pendientes (a) y (f) cerrados en real. Queda el detalle de "rango" como palabra
  técnica.

### Estado real para quien confirma, evidencia legible e íconos (2026-10-01)

- **(h) Quien confirma sabe si, y cuándo, se enteran los demás.**
  - **Causa.** La respuesta "Hecho. La tarea quedó comprometida." la escribe la autoridad
    (`db/esquema.sql`) antes de que el gateway encole los avisos, y los avisos salían con
    `scheduled_for=now`: fuera de horario el despachador los posterga recién al enviar
    (constitución §8), así que ni la fila ni la respuesta decían nada; sin chat activado sólo
    quedaba la auditoría. Caso real: Ismael confirmó a las 18:00 y el aviso a Ariel quedó para el
    02/10 09:00 sin que él lo supiera.
  - **Arreglo.** Los dos avisos (`notify_requester_of_approval`, `notify_responsible_of_assignment`)
    se encolan en `_inicio_de_jornada` (próximo instante hábil; es el mismo que calcularía el
    despachador), de modo que la fila guarda la hora real. `ingreso_tareas.linea_de_estado_de_avisos`
    lee ese estado (hora de la fila, o responsable sin chat) y el gateway suma la línea a la fila
    terminal con `_sumar_a_la_respuesta_terminal`: sigue siendo UN mensaje visible (ADR 0013 regla 2),
    con estado real (regla 3). Textos: "<Nombre> lo va a ver mañana a las 08:00, cuando empiece el
    horario." (también "el lunes a las 08:00", "el 15/10 a las 08:00"; `calendario.cuando_legible`) y
    "<Nombre> todavía no activó su chat con Prisma, así que no le pude avisar." Si el aviso sale ya,
    no se agrega nada; si un aviso falló, tampoco (su incidente ya lo cubre; `_aviso_aislado` intacto).
    El aviso de aprobación a quien pidió usa la misma línea (era igual de simple).
  - **Límite.** Si la fila terminal ya salió antes de sumarle la línea (ventana de milisegundos con
    el despachador), no se toca ni se manda un segundo mensaje: queda un incidente `baja`.
  - **RED.** `tests/test_aviso_de_asignacion.py` (nuevos): 4 failed, 4 passed (las otras dos nuevas,
    "dentro de horario no agrega nada" y "aviso fallido no agrega nada", son guardas que ya pasaban).
  - **GREEN.** El archivo: 17 passed.
- **Evidencia con nombres legibles.**
  - **Causa.** `nombre_legible` sólo reemplazaba guiones bajos: `explicacion` salía sin tilde ni
    mayúscula porque el pack no trae etiquetas por tipo de evidencia (PENDIENTE) y no había tabla.
  - **Arreglo en el origen.** `redaccion.ETIQUETAS_DE_EVIDENCIA` (explicacion, resultado_de_prueba,
    captura, archivo, foto -> "Explicación", "Resultado de prueba", "Captura", "Archivo", "Foto");
    un tipo fuera de la tabla conserva el comportamiento anterior (no se inventa). Cubre el resumen
    y el hecho que ve el modelo en el alta conducida.
  - **RED.** `test_redaccion.py -k nombre_interno`: 5 failed, 1 passed. **GREEN.** La tanda enfocada.
- **(i) Íconos del menú del borrador en curso.** Causa: las etiquetas eran literales sin ícono.
  Arreglo: `ingreso_tareas.CONTINUAR_BORRADOR = con_icono(..., ICONO_EMPEZAR)` (▶️) y
  `EMPEZAR_OTRO = con_icono(..., ICONO_VER_MAS)` (➕); no hay un ícono propio de "seguir" ni de
  "nuevo", se reutilizaron los más cercanos sin inventar lenguaje visual. RED
  `tests/test_iconos_del_menu.py`: 1 failed, 12 passed; GREEN (más `test_task_intake`, conducida,
  dejarlo, pausado): 166 passed.
- **Pruebas cambiadas.** `test_task_intake.py` (dos aserciones de etiquetas: ahora las constantes
  con ícono), `test_alta_dejarlo_conserva_el_borrador.py` (la etiqueta con ícono),
  `test_alta_guiada_texto.py` (evidencia "Explicación, Resultado de prueba, Captura"),
  `test_redaccion.py` (la tabla legible con mayúscula).
- **Tanda enfocada** (10 archivos pedidos más los de `rg -l "explicacion|nombre_legible|Continuar
  borrador|Empezar otro"`, 32 archivos): 853 passed. No se corrió la suite completa.
- Pendientes (h) e (i): resueltos, a verificar en la próxima corrida real.

### Respuesta en stream real (experimento)

- **Decisión del usuario (2026-10-01).** Probar stream real ya, para verlo en Telegram real: en un
  chat privado, mientras el modelo escribe la respuesta de un turno del alta conducida, la persona ve
  el texto aparecer en el borrador nativo (`sendMessageDraft`, el mismo que usa el indicador de
  actividad).
- **Riesgo aceptado.** El texto que se ve en el borrador todavía no pasó el verificador. Si el
  verificador lo rechaza, la persona ve que el reintento lo reemplaza. La variante "mostrar de a poco
  sólo después de verificar" queda PENDIENTE para el trabajo de latencia; no se construyó.
- **Qué se ve y qué nunca.** Sólo el campo `texto` de primer nivel de la salida estructurada
  (constitución §10): nunca JSON crudo, otros campos, nombres de herramienta ni razonamiento. Un
  `texto` anidado (`valores.title.texto`) no cuenta. Hasta que `texto` empieza no se muestra nada
  nuevo. El borrador es efímero: no es un mensaje, no pasa por la cola, no lleva botones. El mensaje
  FINAL es el verificado, por la cola, como siempre.
- **Mecanismo.** `llm.texto_parcial` / `LectorDeTexto` extraen el valor parcial de `texto` del JSON
  que llega en fragmentos (escapes, `\n`, unicode, pares sustitutos, cortes dentro de un escape).
  `ProveedorCompatible.conducir_alta(..., al_avanzar=cb)` (NaN y el resto de los compatibles) pide
  `stream: true`, junta los argumentos de la llamada y devuelve exactamente los mismos argumentos que
  sin stream; el timeout es el del cliente (con `plazo`, el mismo sin reintentos). Anthropic y Gemini
  aceptan el argumento y lo ignoran (sin stream: mismo resultado, sin borrador progresivo).
  Costura: `despachador.mantener_chat_activo` ahora entrega un `IndicadorDeActividad` (`draft_id`,
  `actualizar_borrador(texto)`, con candado) y lo deja en un `ContextVar`; `alta_conducida._conducir`
  lo toma con `despachador.indicador_actual()`, así el `gateway` no cambia. La actualización usa el
  MISMO `draft_id` de la semilla (la semilla no tapa el texto) y el retiro es el de siempre (con el
  typing posterior, 0d86349). Una a lo sumo cada 0,7 s; una falla se reporta una vez por turno
  (`indicador de actividad (stream)`) y no se insiste en ese turno. Con un reintento, el texto nuevo
  reemplaza al anterior en el borrador.
- **Ajuste.** `workspace_setting` clave `stream`: `true` o `{"activo": true}` lo enciende; ausente o
  `false`, apagado; un valor inválido es apagado más un incidente `interruptor_stream` (baja, una vez
  por proceso). Sólo en chat privado y sólo para la llamada `conducir_alta`.

  ```sql
  -- Encender (prisma_flujo; PGCLIENTENCODING=UTF8)
  insert into workspace_setting (workspace_id, clave, valor)
  select id, 'stream', 'true'::jsonb from workspace where slug = 'corework'
  on conflict (workspace_id, clave) do update set valor = excluded.valor;
  -- Apagar
  delete from workspace_setting
   where clave = 'stream' and workspace_id = (select id from workspace where slug = 'corework');
  ```
- **Pendiente.** La variante "progresivo después de verificar" (con el trabajo de latencia); la
  prueba real en Telegram para medir cuánto se ve y si los límites de `sendMessageDraft` alcanzan.
- **RED.** `tests/test_respuesta_en_stream.py` (nuevo, 63 pruebas) contra el código de HEAD: no
  colecciona (ImportError de `LectorDeTexto`); 0 de 63 corren. **GREEN.** El archivo: 63 passed; con
  `test_smoke_runtime`, `test_conducir_alta_proveedores`, `test_alta_conducida`, `test_alta_turno`,
  `test_llm_protocol` y `test_ciclo`: 473 passed. No se corrió la suite completa.
- Nota del padre sobre el TDD de esta unidad: el código se escribió antes que las pruebas y
  el RED se obtuvo después contra HEAD (no colectaba: `ImportError` de `LectorDeTexto`). Las
  63 pruebas cubren lo pedido, pero no guiaron el diseño; queda registrado como desvío del
  modo estricto.
- Indicador "escribiendo…" (`0d86349`, inline del padre): tras retirar el borrador se manda
  un typing más y el refresco pasa a 3 s; causa deducida del código (el retiro manda y borra
  un mensaje, eso apaga el typing, y la respuesta sale después). RED 2 failed, GREEN 96
  passed. Pendiente (g) corregido, pendiente de verificar en real.
- RDD `1ddf179..83743a2` (cuatro lentes), linaje `review-16296c4f68eaa688`: aprobada y
  reconocida. Corregidas después dos WARNING: (1) actualizar el borrador esperaba a Telegram
  en el hilo que lee el stream del modelo (la latencia de Telegram pasaba a ser latencia del
  turno): ahora el envío corre en su propio hilo, una actualización con otra en vuelo se
  saltea y el cierre toma el candado antes de retirar; (2) si el calendario fallaba, el aviso
  de coordinación no se encolaba: ahora se encola para "ahora" (en su savepoint) y el
  despachador lo posterga igual. RED 2 failed, GREEN 165 passed. Quedan como sugerencias: la
  rama "la fila terminal ya salió" sin prueba, claves de aviso duplicadas, el ícono de
  Empezar otro, ramas de `texto_parcial`, elección del índice de la herramienta en el stream.
- Prueba real del stream con Ariel (celular, 21:51): se veían sólo las primeras letras
  ("List…") y después el mensaje final; la animación "…" del borrador y el "escribiendo…"
  sí funcionaron y se mantuvieron hasta la respuesta (pendiente (g) verificado en real).
  Causa: la regulación de envíos descartaba lo que llegaba con un envío en vuelo o antes
  del intervalo, sin guardar el último texto. Corregido: un solo trabajador en segundo plano
  manda siempre el texto más reciente, a lo sumo cada 0,7 s; lo intermedio ya superado no se
  manda, lo último sí. El usuario quiere ver los textos intermedios ("lo hace más dinámico,
  se ve algo mientras piensa"): se conservan. RED 1 failed; GREEN 143 passed; se reescribió
  `test_el_texto_se_acota_a_una_actualizacion_por_intervalo`, que afirmaba el descarte.
