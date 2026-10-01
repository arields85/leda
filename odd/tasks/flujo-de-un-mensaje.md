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
