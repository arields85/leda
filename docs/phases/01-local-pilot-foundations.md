# Fase 1: fundaciones de validación local simulada

> **Superada por cambio de alcance — 2026-09-22.**
>
> Este plan organiza el trabajo por unidades de un piloto local para un único equipo.
> Leda pasó a ser un producto de gestión de proyectos multi-tenant, y el orden de
> trabajo vigente son unidades con precondición y criterio de cierre, no fases. Se
> conserva como registro histórico y **no debe usarse para decidir**. Para el alcance
> vigente: [`../product/que-es-leda.md`](../product/que-es-leda.md),
> [`../architecture/frontera.md`](../architecture/frontera.md) y
> [`../ROADMAP.md`](../ROADMAP.md).
>
> La evidencia registrada de la Unidad 1A conserva su valor como historia de lo que se
> construyó y verificó.

Este plan endurece la arquitectura existente mediante unidades revisables. No define
código ni reemplaza el diseño detallado de cada unidad. Sus evidencias alimentan las
capas A-D del [`protocolo de validación`](../validation/README.md). Las sesiones
manuales progresivas por circuito no sustituyen la validación integral E, pero tampoco
se posponen hasta completar todas las unidades o fases.

## Estrategia de entrega

La prioridad es el menor circuito útil de extremo a extremo que permita observar si
Leda comprende, responde, coordina y reduce carga humana. Cada circuito incluye sólo
el comportamiento, migración o reconciliación necesaria, verificación focalizada y
actualización de estado. Antes de cerrarlo se registra:

- comando de prueba y resultado exacto;
- escenario operativo ejecutado, o `N/A` con motivo;
- evaluación del gate para una sesión manual progresiva y, si el circuito es elegible,
  escenario ficticio ejercitado por Telegram real con sus cuatro superficies; si no
  es elegible, harness determinista o `TestClient` usado y condición pendiente;
- límite de rollback independiente de que exista un commit;
- riesgos residuales y datos que requieran migración.

Después de la verificación técnica se evalúa la elegibilidad: workspace local o de
prueba controlado, datos exclusivamente ficticios y sin trabajo real, secreto de
Telegram protegido, efectos inspeccionables y reversibles, backup, pausa o rollback
proporcionado al circuito, ninguna operación destructiva y ningún `CRITICAL` o `HIGH`
abierto en ese alcance. La sesión inspecciona respuesta visible, PostgreSQL,
herramientas/efectos y auditoría/historia; alimenta replay, regresión y corpus de
desarrollo, pero no el holdout ni la aprobación del piloto.

La frontera vigente de Unidad 1A es suficiente para preparar un smoke progresivo. Este
documento no afirma que el gate ya se comprobó, que el circuito sea elegible ni que la
sesión se haya ejecutado. Si falta una guarda, se cierra sólo esa condición o se usa un
harness determinista/`TestClient`; si el comportamiento es aceptable, se avanza al
siguiente circuito pequeño y el hardening se amplía sólo según evidencia.

### Horizonte de hardening diferido

ADR 0003, el catálogo exhaustivo y los Cortes 0 a 5, la separación completa de
credenciales y los controles avanzados de privacidad/producción conservan todo su
contrato técnico. No son un bloqueo general para el smoke simulado de Unidad 1A. Deben
retomarse antes del piloto real o la VPS, según corresponda, y antes si una sesión
progresiva demuestra que el riesgo alcanza al circuito ejercitado.

## Unidad 1A cerrada: Contrato de compromiso

**Estado:** CLOSED Y OPERATIVA DESDE 2026-08-12. Implementación, revisión
independiente, migración controlada y verificación posterior completadas en `PASS`.

**Objetivo:** establecer el límite de dominio borrador → tarea comprometida antes de
ampliar máquinas de estado, automatizaciones o contratos conversacionales.

**Estado inicial resuelto en la fuente:** ADR 0001 estaba aceptada, pero una tarea
podía persistirse sin responsable, fecha, criterio de aceptación o política de
evidencia y las rutas de creación no compartían un límite de dominio único.

**Alcance:** persistencia mínima del borrador sin efectos operativos; contrato de
tarea comprometida con objetivo, responsable, fecha, criterio de aceptación y
política de evidencia; vista previa y confirmación explícita; revalidación de versión,
actor y autoridad; conversión única y auditoría enlazable; protección equivalente en
todas las rutas de creación. Antes de endurecer restricciones se deben inventariar
las tareas incompletas existentes y definir su tratamiento, sin presumir una
migración segura.

**Fuera de alcance:** grafo general de estados de tareas y objetivos, vencimiento y
automatización del ciclo completo de borradores, aprobación/cierre, UX definitiva y
taxonomías personalizadas.

**Criterios de aceptación:**

- un pedido incompleto sólo puede persistirse como borrador y no aparece como tarea
  activa ni dispara recordatorios, aprobaciones o efectos;
- ninguna ruta crea o activa una tarea sin los cinco datos obligatorios;
- sólo el actor autorizado puede confirmar la versión vigente mostrada en la vista
  previa;
- una confirmación crea una sola tarea completa y deja borrador, tarea, actor,
  autoridad y confirmación enlazados en auditoría;
- confirmar un borrador ajeno, obsoleto, incompleto o ya convertido no crea otra
  tarea;
- las tareas incompletas existentes tienen inventario y estrategia explícita antes
  de aplicar restricciones.

**Verificación requerida:** pruebas de campos faltantes, actor ajeno, versión
obsoleta, doble confirmación secuencial y concurrente, ruta de creación directa y
tratamiento de datos previos; escenario operativo borrador → vista previa →
confirmación → tarea; comando, resultado exacto y evidencia PostgreSQL registrados.

### Checklist de implementación y evidencia

- [x] `task_draft` persiste borradores versionados y aplica RLS.
- [x] La política de evidencia importada queda fijada como snapshot; una política no
  resuelta bloquea el compromiso.
- [x] La vista previa es privada para el aprobador vigente; la raíz sólo confirma
  cuando constituye la autoridad final.
- [x] La conversión revalida versión, actor y autoridad, y es bloqueante, atómica e
  idempotente.
- [x] Borrador, tarea, actor, autoridad y confirmación quedan enlazados; `leda_app`
  no conserva `INSERT` directo sobre `task` y el acceso residual de `leda_admin`
  está documentado.
- [x] Suite post-integración completa: 141 passed, 0 failed, 0 errors, 0 skipped; 1
  `StarletteDeprecationWarning`; 78.36 s.
- [x] Ejecuciones focales: 64 passed y 71 passed.
- [x] RDD clone-local desactivado explícitamente; revisión ordinaria ejecutada como
  `disabled/unmanaged`.
- [x] Revisión independiente final: PASS, 0 hallazgos `CRITICAL`, `HIGH` o `MEDIUM`;
  `migration_readiness: ready`.
- [x] Migración corregida ensayada sin aplicarla a la fuente: clon efímero creado con
  `pg_dump`/`pg_restore`, fuente intacta, 0 tasks y 8 registros de outbox preservados;
  grants, función, RLS, constraints y rollback de borrador comprobados.
- [x] Ventana operativa autorizada; backup sanitizado
  `leda-unit1a-20260812T230031Z-83016718.dump` comprobado; 0 escritores; migración
  aplicada bajo advisory lock.
- [x] Login de autoridad separado configurado; pack aprobado reimportado como versión
  2 con 6 políticas de evidencia.
- [x] Historia preservada: 1 workspace, 0 tasks, 8 outbox y 0 pending.
- [x] Verificación posterior read-only: `PASS` en controles de DB, seguridad,
  configuración y backup; 0 drafts y 0 efectos nuevos.
- [x] RDD clone-local `off`; revisión ordinaria `disabled/unmanaged`.

### Riesgos residuales aceptados al cierre

- **LOW:** una preview puede enviarse desactualizada si cambia el contenido antes del
  despacho, pero la confirmación rechaza esa versión.
- **LOW:** un ACK posterior puede mostrar que la acción ya no está vigente, aunque la
  idempotencia evita crear una tarea duplicada.

Estos riesgos son conocidos, no bloqueantes y aceptados para el cierre de la unidad.

### Corrección posterior al primer smoke progresivo

El 2026-08-14 se inició y detuvo un smoke progresivo de Unidad 1A. Antes de cualquier
confirmación se observaron un crash del listener bajo stdout redirigido no UTF-8 y una
preview textual sin borrador ni acción pendiente, junto con selección y fecha no
confiables. La base preservó cero tareas y la sesión no fue reanudada.

Las primeras correcciones que intentaron reemplazar esta ruta por un intake de tareas
propiedad del servidor no superaron revisión independiente. El candidato final
conservaba dos defectos `HIGH`: `Otra opción` podía dejar confirmable una propuesta
rechazada y una preview podía superar el límite de mensaje de Telegram. Por decisión
explícita ese candidato completo, su migración y sus pruebas fueron retirados.

Sobre esa base limpia se implementó después un intake general nuevo y más acotado. El
servidor limita un request activo por espacio, membresía y chat privado, persiste cada
campo como missing/proposed/confirmed con procedencia, resuelve entidades mediante
candidatos propios, consume choice sets completos y abre slots exactos de texto libre.
La preview incluye todos los campos y snapshots comprometidos, se mide como Telegram
la renderiza y rechaza más de 3900 unidades UTF-16. La conversión continúa atravesando
la autoridad de Unidad 1A; `crear_tarea` no se expone al modelo ni a callbacks legacy.

La revisión independiente posterior encontró que el límite de candidatos podía ocultar
objetivos, que una preview larga no siempre convergía, y que faltaban correlaciones en
concurrencia, chat, tenant, migración, rollback y Unicode. La única corrección acotada
permitida reemplazó el recorte por páginas con continuación, identifica y reabre el
campo exacto que excede la preview, serializa inicios equivalentes, vincula callbacks y
children al chat/espacio, preserva ZWJ y hace equivalentes instalación limpia y
`0001 -> 0002`. El rollback toma advisory y locks de tablas antes de su guard y falla
cerrado ante un escritor concurrente.

La revisión final de esa corrección la descartó por tres defectos `HIGH`: área o
evidencia configuradas podían empujar a la persona a un campo que no controla; prompts
intermedios podían superar Telegram; y `0002` no representaba exactamente drafts,
estados y previews Unit1A ya existentes. Una autorización explícita y separada habilitó
una última unidad exclusivamente para ese contrato global y el preflight legacy, sin
agregar estados ni cambiar la arquitectura conversacional.

Todos los productores y el transporte usan ahora un renderer NFC y UTF-16 común. Los
mensajes con botones no se dividen y usan 3900 unidades como margen seguro; los
informativos sin botones pueden dividirse determinísticamente hasta 4096 con partes y
dedupe propios. Constraints de PostgreSQL cubren también las salidas terminales SQL.
Título, descripción, criterio, fecha y búsquedas tienen límites conservadores; sólo esos
campos controlables se reabren. Objetivo, persona, área y evidencia inválidos generan un
error genérico acotado, incidente y auditoría, con cancelación como única salida.

Antes de DDL, `0002` bloquea e inventaría drafts, pending, previews, opciones y outbox.
Completa `descripcion` sólo en previews legacy exactas, deriva converted/cancelled/open
desde hechos existentes y aborta toda la migración ante cualquier forma incompatible.
El rollback conserva su guard, revierte sólo backfills marcados e impide restaurar una
fila que cambió después.

Se preservaron únicamente mejoras independientes: consola Unicode degradable sin
alterar el update, indicador `typing` compartido por polling/webhook con cleanup
acotado, e identidad humana derivada de membresía Telegram activa expuesta al contexto.
También se conserva el reloj determinista de fecha, hora y zona del workspace, aislado
de cualquier parser de intake. Foco retenido del 2026-08-14:
`.venv\Scripts\python.exe -m pytest tests\test_smoke_runtime.py tests\test_gateway.py
tests\test_personas.py -q` -> 25 passed en 11.53 s.

La unidad separada final pasó 64 pruebas de salida e intake, 6 escenarios focales de
migración y 213 pruebas en la suite completa. El listener, el replay y el smoke
continúan pausados hasta una revisión read-only final; no se afirma elegibilidad ni
aceptación del comportamiento por Telegram.

El segundo smoke posterior no abrió ese flujo: cinco formulaciones fueron respondidas
por el agente como conversación sin efecto, sin borrador ni botones. La causa no estaba
en el estado persistido sino antes de él: el prompt sugería una herramienta, pero el
proveedor podía devolver sólo texto. El reemplazo introduce un router semántico tipado
antes del turno ordinario y apertura directa del primer paso propiedad del servidor.
Anthropic, Gemini, OpenAI-compatible y el proveedor guionado comparten un validador de
envolvente cerrado y un único reintento. Si ya hay un paso activo, no se vuelve a llamar
a ningún modelo.

Una propuesta de entidad sin coincidencias conserva botones con candidatos vigentes,
paginación y `Otra opción`; un conjunto vacío ofrece sólo cancelación. La salida
normaliza Unicode sin reemplazar términos aportados por la persona y muestra un único
estado server-owned de no-efecto cuando hubo un intento fallido o falló el router. El
indicador `typing` es cosmético: sus fallos de setup degradan a no-op y su cleanup es
acotado.

El foco de routing, intake, gateway, salida, `typing`, veracidad, personas y borradores
pasó 219 pruebas en 95.31 s. No hubo cambios de DDL ni operación: listener, replay y
smoke siguen pausados hasta revisar esta corrección y volver a evaluar el gate
progresivo.

### Evidencia operativa y rollback

La migración `0001_task_commitment.sql` fue aplicada a la base operativa durante una
ventana autorizada, con backup previo comprobado, 0 escritores y advisory lock. La
reimportación dejó el pack en versión 2 y la verificación posterior read-only confirmó
el contrato, los controles y la ausencia de efectos nuevos.

Si la aplicación o la verificación falla antes de reabrir escritores, mantenerlos
detenidos, no declarar activa la unidad y conservar la base fallida para diagnóstico.
Restaurar el backup previo en un destino aislado, verificar su integridad y autorizar
el retorno operativo sólo después de esa comprobación. Si hubiera escrituras
posteriores a la ventana, no hacer una restauración ciega: pausar y definir una
reconciliación específica para no perder datos.

**Desviación de proceso registrada:** el verificador posterior ejecutó accidentalmente
`uv run`, sincronizó `.venv` y creó un lock transitorio que luego fue eliminado. No
hubo cambios en DB, código, configuración ni staging. La desviación no fue funcional
ni invalida los controles read-only, pero debe evitarse en futuras verificaciones.

**Condición de cierre cumplida:** todas las rutas de creación atraviesan el mismo
contrato; la evidencia demuestra que un borrador no se confunde con trabajo
comprometido; la migración está aplicada y validada en la base operativa.

## Unidad 1B: integridad del ciclo de vida y estados

**Estado:** 1B.1 acordada y no implementada; las demás porciones continúan en
planificación.

**Dependencia:** Unidad 1A está cerrada. Antes de implementar hechos de tarea debe
implementarse y verificarse el ingreso autenticado de
[`ADR 0003`](../decisions/0003-authenticated-inbound-boundary.md).

**Objetivo:** completar el ciclo de borradores y validar transiciones de tareas y
objetivos en el límite de dominio.

La unidad se divide para no mezclar invariantes revisables: frontera autenticada,
ciclo posterior de borradores, ciclo de vida de tareas y ciclo de vida de objetivos.
1B.1 se entrega en dos cortes ordenados: primero autentica el ingreso mediante los
subcortes 0 a 5 de 1B.1-A; sólo después incorpora hechos de tarea en 1B.1-B. Las
porciones posteriores de 1B conservarán el objetivo de
modificación, cancelación y vencimiento de borradores y el grafo de objetivos, con su
propio alcance, pruebas y rollback.

### Unidad 1B.1 planificada: ciclo de vida de tareas derivado de hechos

**Estado:** contrato aceptado; Cortes 0 a 5 de 1B.1-A y 1B.1-B planificados y no
implementados. El candidato ejecutable de Cut 0 fue retirado y debe reconstruirse
sobre PostgreSQL 18 limpio antes de habilitar el Corte 1.

#### Horizonte aceptado de 1B.1-A: ingreso autenticado

**Objetivo:** implementar la ADR 0003 como prerrequisito arquitectónico sin agregar
todavía hechos de tarea.

**Punto de entrada al retomar este horizonte:** la inspección estática ya identificó 26
tablas directamente mutables por `leda_app`, mutación indirecta de tarea mediante
eventos, ACL potencial de funciones por `PUBLIC` y riesgo de credencial superusuario
compartida en Docker. Esto no prueba el catálogo efectivo de producción. Antes de
implementar ingress, el Corte 0 debe convertir el inventario en catálogo ejecutable y
verificar el entorno objetivo; después deben cerrarse las rutas que omitan recibo,
capacidad o aplicación cercada.

**Alcance:** secreto webhook obligatorio y específico del bot; T1 durable con recibo
inmutable `(bot_scope, update_id)` e identificador estable de despacho exclusivo de
ingreso; ledger `pending`/`interpreting`/terminal; T2 recuperable con generación
monotónica y capacidad opaca por claim, almacenada sólo mediante su hash y rotada al
reclamar; identidad y espacio derivados dentro de la frontera; logins y membresías
disjuntos para `leda_ingress`, `leda_app`, `leda_gateway`,
`leda_dispatcher` y `leda_admin`; serving y polling sin credencial administrativa;
dispatcher limitado a outbox e incidentes técnicos; Unidad 1A adaptada para que
`leda_gateway` consuma el recibo autenticado. El monolito se conserva y no se agrega
otro proceso antes del piloto.

#### Experiencia temporal y registros

Durante los subcortes, consultas, conversación y Unidad 1A continúan. La creación de
objetivos, los cambios de estado de tarea, bloqueos, evidencias y aprobaciones fallan
cerrado desde el Corte 3 hasta que cada capacidad se reabra en su unidad. Las nuevas
activaciones `/start` se pausan entre la separación de credenciales del Corte 2 y la
aceptación del onboarding autenticado del Corte 4; los usuarios ya activados continúan.

Inbound y outbox registran conversación, no autoridad humana. Sólo T2b cercada, el
gateway de Unidad 1A y acciones administrativas identificadas originan auditoría
autoritativa. Los incidentes técnicos son otro registro y no prueban hechos de dominio.
`leda_app` no puede fabricar auditoría humana. El inbound histórico permanece como
legacy de sólo lectura y no autoritativo: no se elimina, promueve, reintenta ni produce
efectos.

#### Secuencia obligatoria al retomar 1B.1-A

La secuencia no altera el orden general del roadmap. La tabla resume el contrato; el
detalle normativo, las matrices y el rollback están en
[`ADR 0003`](../decisions/0003-authenticated-inbound-boundary.md#secuencia-normativa-de-endurecimiento).

| Corte | Objetivo y alcance | Preservado | Degradación temporal | Aceptación | Migración y rollback | Dependencia |
|---|---|---|---|---|---|---|
| 0. Catálogo, PLANIFICADO | Catalogar de forma ejecutable objetos, funciones, eventos, roles, owners, ACL explícita/efectiva, `PUBLIC`, superusuario y credenciales; agregar pruebas negativas. | Todo el comportamiento actual. | Ninguna. | Catálogo y matriz negativa aceptados contra una instalación PostgreSQL 18 limpia, con roles provisionados canónicamente y sin residuos globales. | Incorporar catálogo y pruebas antes de migrar ACL. Rollback: retirar sólo el arnés defectuoso; conservar la evidencia conceptual y no cambiar privilegios para satisfacer expectativas. | Ninguna. |
| 1. ACL | Revocar `PUBLIC` y quitar DML de app demostrado como no usado, con owner y `search_path` seguros. | Comportamiento legítimo actual y Unidad 1A. | Ninguna prevista. | Baseline preservada; ausencia de ACL implícita y paridad instalación/migración. | Migración versionada; rollback sólo de ACL nominadas del Corte 0, sin grants amplios. | Corte 0. |
| 2. Credenciales | Provisionar cinco logins disjuntos reales; serving/polling sin admin; dispatcher sólo para outbox listo e incidentes de transporte. | Activados, consultas, conversación, Unidad 1A y despacho. | Nuevos `/start` pausados. | Credencial única por camino; sin `SET ROLE`, ownership o superusuario; gateway y dispatcher mínimos. | Provisión de clúster separada; rollback vuelve a matriz nominada del Corte 1 y detiene avance. | Corte 1. |
| 3. Fail-closed | Cerrar creación de objetivos, estado de tarea, bloqueos, evidencia y aprobaciones; revocar DML de eventos de dominio. | Consultas, conversación, activados, Unidad 1A y outbox. | Cinco familias sin escritura; `/start` sigue pausado. | Bypass por DML, función, evento, GUC o actor forjado falla sin efecto, auditoría autoritativa ni outbox de éxito. | Activación conjunta de ACL y rutas; rollback seguro conserva fail-closed salvo reversión explícita anterior a ingress. | Corte 2. |
| 4. Ingress | Implementar T1/T2a/T2b, onboarding autenticado y adaptación de Unidad 1A; preservar inbound histórico como legacy. | Consultas, conversación, activados, Unidad 1A y dispatcher. | Efectos del Corte 3 siguen cerrados; ingreso se pausa durante migración. | Fencing, replay, rollback, recuperación, bots, onboarding, gateway, privilegios y conexiones pasan; `/start` reabre al aceptar. | Rollback vuelve a Corte 3, pausa onboarding y conserva recibos/resultados sin promover legacy. | Corte 3. |
| 5. Capacidades | Reabrir por separado objetivos, estados, bloqueos, evidencia y aprobaciones en su unidad de dominio. | Cortes previos y capacidades ya aceptadas. | Cada familia pendiente sigue cerrada. | Pruebas nominadas de identidad, autoridad, concurrencia, replay, auditoría, outbox y atomicidad por familia. | Una migración por capacidad, sin DML app; rollback revoca sólo esa capacidad y vuelve a fail-closed. | Corte 4 y unidad correspondiente. |

Cada corte registra comando, resultado exacto, entorno descartable o escenario
operativo aplicable, evidencia sanitizada y límite de rollback. Ningún corte está
implementado. Cut 0 debe convertir el inventario conceptual en un catálogo ejecutable
contra PostgreSQL 18 limpio e incluir todos los principals no internos,
objetos/ACL/owners en schemas no sistema, extensiones, large objects, default ACL y
membresías relevantes, excluyendo sólo catálogos PostgreSQL, toast y schemas
temporales. Debe distinguir la provisión canónica de roles de cualquier residuo global
del clúster. Hasta su aceptación no se habilita el Corte 1 ni se declara una mejora de
seguridad.

**Políticas:** `leda_app` no crea, modifica ni enumera recibos. T2a reclama en una
transacción corta con `READ COMMITTED`, row lock y `SKIP LOCKED`; confirma el incremento
de generación y la rotación de capacidad antes de interpretar fuera de transacción. El
heartbeat opcional usa otra conexión, no revive leases vencidos y no es un control de
seguridad. El lease sólo habilita reclaim; la generación confirmada produce la
revocación. `edited_message` puede conservarse como historia, pero no produce efectos;
un cambio operativo exige un mensaje nuevo.

Cada frontera ofrece una sola función superior `SECURITY DEFINER` en T2b:
`leda_app` presenta el plan a su función de aplicación y `leda_gateway` ejecuta el
callback de Unidad 1A. La función bloquea el procesamiento, comprueba hash de capacidad,
generación, estado y lease, deriva identidad, revalida autoridad y confirma de forma
atómica inbound, efectos, ledger de operación, auditoría, outbox, resultado y
finalización condicional. Unidad 1A incluye tarea, auditoría, resultado y outbox en la
misma T2b. Un fence inválido lanza excepción y revierte todas las escrituras; los
logins llamadores no tienen DML directo ni acceso a funciones internas que permita
omitir la finalización.

Interpretación y LLM no mantienen transacciones abiertas. Claim, heartbeat, aplicación
y recuperación usan conexiones separadas. Los resultados y claves de operación son
deterministas por recibo y objeto de dominio; no dependen de timestamps, IDs de tool
calls ni identificadores nuevos de cada interpretación. La recuperación trata los
fallos por recibo y resuelve commits ambiguos consultando el resultado persistido antes
de reinterpretar.

**Criterios de aceptación:**

- T1 sobrevive a la caída posterior y una reentrega converge al recibo inmutable sin
  exponer el identificador privado de despacho fuera de `leda_ingress`;
- cada claim incrementa la generación y rota la capacidad; sólo se almacena su hash y
  un heartbeat no revive un lease vencido ni una generación ya reclamada;
- en la carrera crítica, si el reclaimer bloquea primero el worker obsoleto falla antes
  de escribir; si T2b bloquea primero, el reclaimer no incrementa y el worker puede
  terminar atómicamente;
- cada fallo inyectado después de una escritura de T2b revierte efectos, operación,
  auditoría, outbox, resultado y finalización completos;
- un commit ambiguo, retry o recuperación devuelve el resultado determinista por
  recibo/operación y no duplica ni reinterpreta un efecto terminal;
- no existe una conexión `idle in transaction` durante el LLM y claim, heartbeat,
  aplicación y recuperación no comparten conexión;
- la única T2b de `leda_gateway` conserva la semántica de Unidad 1A y confirma tarea,
  auditoría, resultado, outbox y finalización como una unidad;
- los fallos de recuperación quedan aislados por recibo;
- los logins `NOINHERIT` tienen membresías disjuntas, los owners no son asumibles,
  los revokes impiden DML o funciones internas de bypass y serving/polling no cargan
  administración;
- `leda_dispatcher` sólo reclama outbox listo, marca envío, reintento o fallo y abre
  incidentes técnicos de transporte; no crea contenido, cambia destinatarios ni toca
  dominio o auditoría humana;
- instalación limpia y migración producen privilegios equivalentes; avance, rollback,
  provisión separada de roles de clúster y restore pasan en un clúster aislado
  representativo.

**Criterio de salida:** los Cortes 0 a 4 están aceptados y el Corte 5 queda como regla
obligatoria para cada reapertura posterior; migración, matriz negativa de privilegios,
pruebas de
claim/generación/heartbeat, carrera A/B del lease, fallos después de cada escritura,
reentrega y recuperación, commit ambiguo, aislamiento entre bots, webhook, Unidad 1A,
ausencia de transacción durante el LLM, escenario operativo y rollback pasan contra
PostgreSQL descartable confirmado. La provisión y el restore de roles se ensayan en un
clúster aislado representativo y se demuestra paridad entre instalación limpia y
migración. El detalle normativo de secuencia, invariantes, pruebas y rollback está en
ADR 0003. Hasta cumplir este criterio no se implementa 1B.1-B.

#### Corte 1B.1-B: ciclo de vida de tareas derivado de hechos

**Dependencia:** 1B.1-A implementado, verificado y aprobado. La capacidad autenticada
es la única fuente admisible de actor, espacio y recibo para los efectos de este corte.

**Objetivo:** reemplazar la selección manual y genérica de estados por un único límite
de dominio que derive el ciclo de una tarea desde hechos autorizados, rechace cualquier
salto inválido y preserve una auditoría suficiente para explicar quién informó qué,
qué regla produjo la transición y con qué estado vigente.

#### Invariante de producto

Las personas realizan el trabajo, informan hechos concretos y aportan evidencia; las
decisiones que requieren autoridad o juicio siguen siendo humanas. Leda absorbe el
seguimiento y la coordinación operativa, convierte hechos autorizados en transiciones
deterministas y dirige las decisiones al actor vigente. Un referente acepta tareas
vinculadas a su área y, cuando corresponda, aprueba o rechaza lo entregado: no persigue
el avance ni administra estados intermedios.

Unidad 1A no cambia. Cualquier integrante puede proponer trabajo propio; un referente
puede proponer trabajo para sus supervisados directos; Dirección puede proponer
trabajo propio o para sus supervisados directos. La aprobación sube un nivel y un
borrador completo de Dirección para sí misma requiere igualmente autoconfirmación
explícita. La propuesta, la vista previa y la aceptación permanecen en `task_draft`.

#### Estado inicial comprobado

- `actualizar_estado` admite una selección de estado y está permitida por defecto a
  cualquier integrante, sin limitar la tarea al responsable ni reservar cancelación a
  Dirección;
- la herramienta inserta `task_state_event` y `leda_app` conserva permiso de
  inserción directa sobre esa tabla;
- el esquema proyecta cada evento sobre `task.estado`, pero no valida el grafo completo,
  el estado anterior vigente, los no-op ni la irreversibilidad de estados terminales;
- las tareas comprometidas por Unidad 1A nacen completas, pero el catálogo físico aún
  contiene `propuesta` y `pendiente_aprobacion`, y la semántica conversacional sigue
  exponiendo cambios manuales de estado.

#### Alcance

- introducir un único límite autorizado para todos los cambios de estado de tareas,
  con lectura bloqueante del estado vigente, validación de transición, actor, causa y
  autoridad, escritura única del evento y auditoría enlazada;
- hacer que toda tarea comprometida por `task_draft` comience efectivamente en
  `asignada`; `propuesta` y `pendiente_aprobacion` no forman parte de este flujo
  operativo;
- derivar transiciones desde hechos en lenguaje natural informados por el responsable:
  inicio, bloqueo, resolución del bloqueo y entrega; la persona no elige el nombre del
  estado;
- conservar el estado operativo previo al entrar en `bloqueada` y restaurarlo sólo
  cuando se resuelve el último bloqueo abierto;
- reservar la cancelación ejecutable a Dirección, con motivo obligatorio y auditado;
  cualquier otra persona sólo puede solicitarla y esa solicitud no cambia el estado;
- impedir bypass por `UPDATE task`, inserción directa de eventos, actor declarado por
  el llamador o cualquier ruta administrativa ordinaria no autorizada;
- mantener aislamiento por espacio, idempotencia o control de concurrencia del efecto
  y trazabilidad entre recibo, hecho, transición y auditoría;
- aceptar como máximo un hecho que cambie estado por `(receipt, task)`, con resultado
  persistido; un recibo puede contener hechos para varias tareas distintas, pero dos
  cambios secuenciales para una misma tarea exigen aclaración y un mensaje nuevo.

#### Grafo exacto

Una tarea comprometida entra en `asignada`. Sólo se permiten estas transiciones:

```text
asignada    -> en_curso | bloqueada | cancelada
en_curso    -> bloqueada | en_revision | cancelada
en_revision -> en_curso | bloqueada | terminada | cancelada
bloqueada   -> estado operativo previo | cancelada
```

El estado operativo previo a `bloqueada` sólo puede ser `asignada`, `en_curso` o
`en_revision`, según el estado vigente al abrir el primer bloqueo. La restauración
ocurre al resolverse el último bloqueo abierto, no al cerrar uno entre varios.
`terminada` y `cancelada` son irreversibles. Toda transición no listada y todo cambio
al mismo estado son inválidos.

#### Hechos y autoridad

| Hecho o decisión | Actor humano | Efecto autorizado de 1B.1 |
|---|---|---|
| Trabajo iniciado | Responsable vigente | `asignada -> en_curso` |
| Bloqueo informado | Responsable vigente | Estado operativo vigente `-> bloqueada`, con causa factual |
| Último bloqueo resuelto | Responsable vigente; Leda verifica los bloqueos persistidos | `bloqueada -> estado operativo previo` |
| Trabajo entregado | Responsable vigente | `en_curso -> en_revision`; no implica aprobación ni cierre |
| Trabajo rechazado | Aprobador vigente | `en_revision -> en_curso`; la decisión y su mecánica completa pertenecen a Unidad 4 |
| Trabajo aprobado y cierre válido | Aprobador vigente y mecanismo de cierre autorizado | `en_revision -> terminada`; evidencia, aprobación y cierre completos pertenecen a Unidad 4 |
| Cancelación | Sólo Dirección | Cualquier estado no terminal `-> cancelada`, con motivo obligatorio y auditado |

Leda puede interpretar la expresión natural y coordinar el próximo paso, pero no
inventa el hecho, la decisión ni la autoridad. Un integrante ajeno, el referente como
seguidor, el modelo o un caller técnico no pueden declarar inicio, entrega, rechazo,
aprobación o cancelación en nombre del actor correspondiente.

#### Criterios de aceptación

- una tarea recién comprometida queda en `asignada` sin pasar por `propuesta` ni
  `pendiente_aprobacion`;
- cada arco del grafo se acepta sólo con estado vigente, hecho y actor autorizados;
  cualquier otro arco, no-op, estado anterior forjado o transición desde un terminal
  falla sin producir evento, proyección ni auditoría de éxito;
- sólo los hechos del responsable vigente derivan inicio, bloqueo, desbloqueo y
  entrega sobre su tarea; ni otro integrante ni el referente realizan seguimiento
  mediante cambios manuales de estado;
- `bloqueada` conserva el estado operativo previo y sólo sale cuando no queda ningún
  bloqueo abierto;
- únicamente Dirección ejecuta cancelación y debe aportar un motivo no vacío; una
  solicitud de cancelación de otro actor no cambia la tarea;
- `en_revision` no equivale a evidencia suficiente, aprobación ni cierre, y el límite
  no ofrece un atajo genérico hacia `terminada`;
- todas las rutas de aplicación atraviesan el mismo límite y `leda_app` no puede
  insertar `task_state_event` ni mutar `task.estado` directamente;
- reintentos y carreras no aplican dos veces el mismo hecho ni aceptan una transición
  calculada sobre un estado obsoleto;
- retries o reinterpretaciones del mismo recibo y tarea devuelven el resultado o
  conflicto persistido, sin ejecutar otro efecto;
- el evento y la auditoría permiten reconstruir tarea, espacio, estado anterior y
  nuevo, hecho o decisión, actor humano, autoridad aplicada, motivo cuando corresponda
  e instante;
- el contrato de compromiso y la matriz de propuesta/aprobación de Unidad 1A continúan
  pasando sin cambios.

#### Pruebas esperadas

- prueba tabular de cada arco permitido, cada salto prohibido, no-op y reintento desde
  `terminada` o `cancelada`;
- compromiso desde `task_draft` con estado inicial `asignada` y regresión completa de
  la autoridad de Unidad 1A, incluida la autoconfirmación de Dirección;
- inicio, bloqueo, último desbloqueo y entrega expresados con variantes de lenguaje
  natural por el responsable, verificando la transición estructurada y no palabras
  exactas;
- múltiples bloqueos y carreras entre resolución, entrega, nuevo bloqueo y cancelación;
- actor ajeno, responsable reemplazado, referente que intenta mover estado, Dirección
  y no Dirección intentando cancelar, motivo vacío y solicitud sin efecto;
- rechazo y cierre invocados sólo mediante la autoridad reservada, con precondiciones
  de Unidad 4 simuladas o fijadas, sin implementar en esta unidad su ciclo completo;
- intentos de `UPDATE task`, `INSERT task_state_event`, actor forjado, estado anterior
  forjado y acceso cruzado entre espacios usando los roles reales;
- evidencia PostgreSQL de un único evento y una única auditoría por efecto exitoso, y
  ausencia de ambos ante un rechazo del límite;
- un mensaje con hechos inequívocos para tareas distintas, dos cambios secuenciales
  para una misma tarea y `edited_message`, verificando respectivamente efectos
  separados, aclaración sin segundo efecto y ausencia total de efecto operativo.

#### Escenario operativo requerido

En PostgreSQL descartable confirmado, comprometer una tarea por el flujo vigente de
Unidad 1A y comprobar que nace `asignada`. Como responsable, informar en lenguaje
natural que se inició, que apareció un bloqueo, que el bloqueo se resolvió y que el
trabajo fue entregado; comprobar después de cada mensaje el hecho persistido, el evento,
la proyección y la auditoría, hasta `en_revision`. Verificar que Leda no la presenta
como aprobada ni terminada. En una segunda tarea, comprobar que una solicitud de
cancelación de un actor sin autoridad no cambia el estado y que Dirección puede
cancelarla una sola vez únicamente con motivo. Registrar comando, resultado exacto y
filas sanitizadas; no usar datos de trabajo real.

#### Límites con otras unidades

- **Unidad 1A:** no cambia creación, completitud, política de evidencia, vista previa,
  autoridad de propuesta/aceptación, confirmación ni conversión atómica. 1B.1 sólo
  adapta su gateway dedicado para derivar identidad del recibo autenticado y luego
  fija el estado inicial y el ciclo posterior de la tarea comprometida.
- **Unidad 2:** conserva el cierre integral de idempotencia inbound para todos los
  tipos y resultados. 1B.1-A adelanta únicamente la frontera autenticada mínima que
  necesitan los efectos de 1B.1; no cambia la secuencia del roadmap.
- **Otras porciones de 1B:** modificación, cancelación y vencimiento de `task_draft`, y
  estados de objetivos, conservan alcance, contrato, pruebas y rollback propios. No se
  incorporan a 1B.1.
- **Unidad 4:** implementará evidencia entregada, presentación automática al aprobador
  vigente, rechazo, aprobación y cierre con sus versiones y precondiciones. 1B.1 sólo
  protege los arcos reservados y garantiza que entrega, revisión, aprobación y cierre
  no sean sinónimos.
- **Unidad 5:** implementará solicitudes pendientes, plazos, cadencias, recordatorios,
  seguimiento y escalamiento. 1B.1 no crea ese ciclo ni hace que una solicitud de
  cancelación equivalga a cancelación ejecutada.

#### Rollback

Antes de abrir escritores, retirar la nueva ruta y sus privilegios, restaurar la
versión anterior de las funciones o grants afectados y comprobar que Unidad 1A sigue
impidiendo crear tareas incompletas o por inserción directa. Conservar eventos y
auditoría producidos por 1B.1 para diagnóstico; no reescribirlos ni restaurar una base
sobre escrituras posteriores. Si la migración cambió estados o privilegios, definir y
ensayar la reconciliación inversa en un clon con inventario previo. Un rollback no
puede reabrir `INSERT task` a `leda_app` ni debilitar la conversión autorizada de
`task_draft`.

**Condición de cierre:** 1B.1-A está implementado y verificado; código, esquema,
permisos y todas las rutas de 1B.1-B aplican el grafo y la autoridad anteriores; las
pruebas focales y la baseline pasan contra PostgreSQL descartable; el escenario
operativo y el rollback de cada corte quedan ejecutados y registrados. El diseño y el
contrato acordados por sí solos no cumplen esta condición.

### Contrato pendiente para las demás porciones de 1B

**Alcance conservado:** modificación, cancelación y vencimiento de borradores; grafo y
autoridad de objetivos; protección simétrica contra escritura directa. Su diseño no se
presume resuelto por 1B.1.

**Criterios de aceptación:**

- modificar, cancelar o vencer un borrador no crea efectos operativos;
- las transiciones inválidas de objetivos fallan en el límite de dominio, no sólo en
  el prompt;
- los objetivos sólo cambian estado por el mecanismo autorizado.

**Pruebas esperadas:** modificación, cancelación y vencimiento de borrador; transición
válida e inválida y escritura directa de objetivos.

**Rollback:** retirar cada nuevo ciclo y sus restricciones sin debilitar el contrato de
compromiso establecido por Unidad 1A ni el contrato acordado para 1B.1.

## Unidad 2: idempotencia inbound

**Objetivo:** procesar cada update de Telegram como máximo una vez por la clave estable
`(bot_scope, update_id)`.

**Dependencia conservada:** extender el recibo autenticado de ADR 0003 sin reemplazar
su raíz de confianza ni conceder a `leda_app` acceso general a recibos.

**Alcance:** completar para todos los tipos de update la restricción persistente,
clasificación, resultado repetible y auditoría sin duplicar turnos ni efectos. El tipo,
actor y espacio son atributos autenticados del recibo, no partes elegibles de la clave.

**Criterios de aceptación:**

- repetir exactamente un mensaje no crea dos inbound, respuestas o herramientas;
- repetir un callback no ejecuta dos acciones;
- dos bots no colisionan por `update_id` coincidente y cambiar tipo, actor o espacio
  declarados para la misma clave produce conflicto, no otro recibo;
- un fallo después de recibir permite reintento seguro sin perder el update;
- la deduplicación sobrevive reinicios y concurrencia.

**Pruebas esperadas:** replay secuencial, replay concurrente, mismo identificador en
`bot_scope` distintos, colisión incompatible, rollback transaccional y callback ya
resuelto.

**Rollback:** retirar sólo las extensiones de Unidad 2 y su manejo adicional de
resultados, sin retirar el recibo autenticado requerido por 1B.1 ni tocar la
idempotencia existente de outbox y acciones pendientes.

## Unidad 3: contratos de respuesta y frescura

**Objetivo:** separar hechos estructurados de redacción natural.

**Alcance:** contratos iniciales para las intenciones operativas de la validación,
lectura vigente autorizada, campos obligatorios, orden, completitud y tratamiento
distinto de vacío, error, ambigüedad y falta de permiso.

**Criterios de aceptación:**

- los mismos datos, actor, permiso e intención producen la misma conclusión;
- una referencia conversacional se vuelve a resolver contra PostgreSQL;
- una fuente no disponible nunca se presenta como una lista vacía;
- la respuesta estructurada conserva cantidad y campos obligatorios;
- el modelo puede variar redacción, pero no hechos, omisiones ni próximo paso.

**Pruebas esperadas:** lenguaje humano vago, datos concurrentemente modificados,
resultado vacío, error de base, permiso insuficiente, referencia ambigua, múltiples
categorías pendientes y validación contra filas reales.

**Rollback:** desactivar el enrutamiento hacia contratos nuevos por intención sin
alterar datos del dominio.

## Unidad 4: evidencia, aprobación y cierre

**Objetivo:** hacer ejecutable la política de evidencia y evaluar decisiones contra
el estado vigente.

**Alcance:** registro y validación de evidencia entregada contra la política fijada al
comprometer el trabajo, presentación para revisión, aprobador vigente, rechazo,
invalidación o nueva aprobación cuando cambia materialmente el trabajo y cierre
separado.

**Criterios de aceptación:**

- toda tarea comprometida conserva la política de evidencia aplicable;
- evidencia entregada no equivale a aprobación ni cierre;
- sólo el aprobador vigente y autorizado decide;
- cambios relevantes posteriores no reutilizan silenciosamente una aprobación vieja;
- el cierre comprueba evidencia, aprobación, bloqueos, dependencias y estado actual;
- la auditoría identifica política y versiones relevantes.

**Pruebas esperadas:** evidencia ausente, tipo incorrecto, actor no autorizado,
autoaprobación, cambio de responsable o criterio, aprobación obsoleta, doble decisión,
dependencias abiertas y cierre concurrente.

**Rollback:** conservar evidencia y auditoría existentes; retirar sólo la nueva
evaluación/política según una migración reversible definida.

## Unidad 5: pending replies y cadencias veraces

**Objetivo:** recordar y escalar únicamente solicitudes reales que siguen sin
respuesta, y ejecutar las cadencias de validación local automáticamente.

**Alcance:** creación de solicitud pendiente, plazo, satisfacción por respuesta
relevante, cancelación, recordatorios, escalamiento, pausas y planificador local.

**Criterios de aceptación:**

- cada recordatorio referencia una solicitud clara que requería respuesta;
- una respuesta posterior satisface la solicitud correcta de forma auditable;
- avisos informativos no crean deuda de respuesta;
- ausencia, bloqueo, cancelación, reasignación o respuesta detienen el seguimiento;
- el escalamiento informa hechos comprobados y corta recordatorios equivalentes;
- el modo local ejecuta cadencias configuradas sin comando manual;
- reinicios o dos vueltas simultáneas no duplican mensajes.

**Pruebas esperadas:** reloj controlado, respuesta antes/después del plazo, mensaje no
relacionado, solicitud múltiple, ausencia, bloqueo, reasignación, duplicación,
reinicio y escalamiento con contenido factual.

**Rollback:** volver al disparo manual de cadencias sin perder solicitudes ni
auditoría; no reactivar afirmaciones de silencio no demostrables.

## Unidad 6: RLS y reconciliación de packs

**Objetivo:** asegurar aislamiento total y convergencia de configuración al
reimportar.

**Alcance:** inventario de tablas/vistas/funciones por tenant, políticas completas,
pruebas negativas, reconciliación de workspace y colecciones, eliminación o
desactivación explícita y trazabilidad de cambios.

**Criterios de aceptación:**

- el rol de aplicación no lee ni modifica filas de otro espacio por ninguna ruta;
- tablas de eventos, auditoría y configuración tienen el tratamiento deliberado que
  corresponda, documentado y probado;
- reimportar el mismo pack no cambia el estado ni crea duplicados;
- cambiar grupo, activación, personas, roles, rutas o cadencias converge al pack;
- retirar configuración tiene semántica explícita: borrar, desactivar o preservar;
- una reimportación fallida es atómica y conserva la versión anterior operativa.

**Pruebas esperadas:** lectura/escritura cruzada, funciones con privilegios, vistas,
dos espacios con datos homónimos, reimportación idéntica, cambios y retiros,
referencias existentes y fallo a mitad de importación.

**Rollback:** restaurar la versión anterior del pack y sus datos derivados mediante
un procedimiento probado, sin desactivar RLS globalmente.

## Cierre de Fase 1

- todas las unidades cumplen sus criterios con evidencia registrada;
- la baseline completa pasa contra PostgreSQL descartable confirmado;
- no quedan tareas comprometidas inválidas ni updates duplicables conocidos;
- RLS y reimportación tienen pruebas negativas y de convergencia;
- existe un mecanismo operativo para congelar confirmaciones, cadencias, despachos y
  nuevos efectos sin destruir conversación, PostgreSQL, logs ni auditoría;
- `docs/STATUS.md` habilita Fase 2 y enumera riesgos residuales.
