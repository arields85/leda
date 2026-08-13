# Fase 1: fundaciones de validación local simulada

Este plan endurece la arquitectura existente mediante unidades revisables. No define
código ni reemplaza el diseño detallado de cada unidad. Sus evidencias alimentan la
capa A y preparan las capas B-D del
[`protocolo de validación`](../validation/README.md); no sustituyen la validación
manual E.

## Estrategia de entrega

Cada unidad debe incluir comportamiento, migración o reconciliación necesaria,
pruebas y actualización de estado. Antes de cerrarla se registra:

- comando de prueba y resultado exacto;
- escenario operativo ejecutado, o `N/A` con motivo;
- límite de rollback independiente de que exista un commit;
- riesgos residuales y datos que requieran migración.

No iniciar una unidad dependiente hasta que la anterior proteja su invariante.

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
- [x] Borrador, tarea, actor, autoridad y confirmación quedan enlazados; `prisma_app`
  no conserva `INSERT` directo sobre `task` y el acceso residual de `prisma_admin`
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
  `prisma-unit1a-20260812T230031Z-83016718.dump` comprobado; 0 escritores; migración
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

**Estado:** habilitada para planificación; no activa ni implementada en código.

**Dependencia:** cumplida por el cierre operativo de Unidad 1A.

**Objetivo:** completar el ciclo de borradores y validar transiciones de tareas y
objetivos en el límite de dominio.

**Alcance:** modificación, cancelación y vencimiento de borradores; transiciones
permitidas para tareas y objetivos; protección simétrica contra escritura directa.

**Criterios de aceptación:**

- transiciones inválidas fallan en el límite de dominio, no sólo en el prompt;
- tareas y objetivos sólo cambian estado por el mecanismo de eventos autorizado;
- modificar, cancelar o vencer un borrador no crea efectos operativos.

**Pruebas esperadas:** modificación, cancelación y vencimiento de borrador,
transición válida e inválida y escritura directa de tareas y objetivos.

**Rollback:** retirar el nuevo ciclo y sus restricciones de transición sin debilitar
el contrato de compromiso establecido por la Unidad 1A.

## Unidad 2: idempotencia inbound

**Objetivo:** procesar cada update de Telegram como máximo una vez por bot/espacio y
tipo de update.

**Alcance:** identidad estable del update, restricción persistente, inserción
atómica, resultado repetible y auditoría sin duplicar turnos ni efectos.

**Criterios de aceptación:**

- repetir exactamente un mensaje no crea dos inbound, respuestas o herramientas;
- repetir un callback no ejecuta dos acciones;
- dos espacios o bots no colisionan por identificadores coincidentes;
- un fallo después de recibir permite reintento seguro sin perder el update;
- la deduplicación sobrevive reinicios y concurrencia.

**Pruebas esperadas:** replay secuencial, replay concurrente, mismo identificador en
alcances distintos, rollback transaccional y callback ya resuelto.

**Rollback:** retirar la nueva clave y manejo de conflicto sin tocar la idempotencia
existente de outbox y acciones pendientes.

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

**Alcance:** materialización de evidencia requerida al comprometer trabajo,
presentación para revisión, aprobador vigente, invalidación o nueva aprobación cuando
cambia materialmente el trabajo y cierre separado.

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
