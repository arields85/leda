# Estado actual

**Fase activa:** Fase 1, fundaciones de validación local simulada.

**Última actualización documental:** 2026-08-12.

## Resumen

La Fase 0 cerró su contrato documental. La Unidad 1A de Fase 1 está cerrada y
operativa: su implementación, revisión independiente, migración y verificación
posterior finalizaron en `PASS`. La Unidad 1B queda habilitada para planificación,
pero todavía no está activa ni implementada en código.

## Estado comprobado

- Repositorio Git inicializado; base preparada para su primer commit versionado.
- Base documental de continuidad creada.
- Implementación inspeccionada como monolito modular Python/PostgreSQL con Telegram,
  RLS, herramientas autorizadas, outbox, acciones pendientes y memoria reciente.
- Especificación funcional externa incorporada como referencia de producto.
- Unidad 1A implementada y operativa; la migración `0001_task_commitment.sql` fue
  aplicada a la base operativa bajo advisory lock, con 0 escritores activos y backup
  previo verificado.
- RDD clone-local fue desactivado explícitamente; la revisión ordinaria se ejecutó en
  estado `disabled/unmanaged`.

## Baseline de pruebas

Baseline independiente ejecutada después de implementar Unidad 1A. Este resultado,
junto con la activación y verificación operativas, cierra la unidad; no implica que el
proyecto esté listo para la validación manual ni para el piloto real.

| Campo | Valor |
|---|---|
| Fecha | 2026-08-12 |
| Entorno descartable confirmado | Sí; el fixture de sesión completó su mecanismo existente de base efímera. |
| Comando | `.venv\Scripts\python.exe -m pytest` |
| Resultado exacto | 141 passed, 0 failed, 0 skipped, 0 errors; duración: 78.36 s. |
| Fallos o advertencias | Sin fallos ni bloqueos. 1 `StarletteDeprecationWarning` en `fastapi/testclient.py:1`: el uso de `httpx` con `starlette.testclient` está deprecado. |

## Evidencia de Unidad 1A

**Estado:** CLOSED Y OPERATIVA DESDE 2026-08-12.

Este estado distingue cinco resultados que no son intercambiables:

| Capa | Estado | Evidencia |
|---|---|---|
| Implementación | Completa en la fuente | `task_draft` persistente, versionado y protegido por RLS; política de evidencia materializada como snapshot; vista previa privada al aprobador; la raíz sólo actúa como autoridad final; conversión bloqueante, revalidada, atómica e idempotente; `prisma_app` sin `INSERT` directo sobre `task`; acceso residual de `prisma_admin` documentado. |
| Verificación independiente | PASS | Revisión final sin hallazgos `CRITICAL`, `HIGH` ni `MEDIUM`; `migration_readiness: ready`. Suite post-integración: 141 passed, 0 failed, 0 skipped, 0 errors; 1 `StarletteDeprecationWarning`; 78.36 s. Ejecuciones focales: 64 passed y 71 passed. RDD clone-local desactivado explícitamente; revisión ordinaria `disabled/unmanaged`. |
| Ensayo de migración corregida | PASS en clon efímero | Clon obtenido con `pg_dump`/`pg_restore`; fuente intacta; 0 tasks y 8 registros de outbox preservados. Grants, función, RLS, constraints y rollback de borrador comprobados. |
| Despliegue operativo | PASS | Backup sanitizado `prisma-unit1a-20260812T230031Z-83016718.dump` verificado; 0 escritores; migración aplicada bajo advisory lock; login de autoridad separado; pack aprobado reimportado como versión 2 con 6 políticas de evidencia. Historia preservada: 1 workspace, 0 tasks, 8 outbox y 0 pending. |
| Verificación posterior read-only | PASS | Todos los controles de DB, seguridad, configuración y backup pasaron; 0 drafts y 0 efectos nuevos. RDD clone-local permaneció `off` y la revisión ordinaria, `disabled/unmanaged`. |

La Unidad 1A cerró después de activar y validar el contrato en la base operativa bajo
la ventana autorizada. El detalle está en la
[`Unidad 1A`](phases/01-local-pilot-foundations.md#unidad-1a-cerrada-contrato-de-compromiso).

**Riesgos residuales LOW:** una preview puede enviarse desactualizada si cambia el
contenido antes del despacho, aunque la confirmación rechaza esa versión; además, un
ACK posterior puede indicar que la acción ya no está vigente, aunque la idempotencia
evita crear una tarea duplicada. Ambos son conocidos, no bloqueantes y aceptados para
el cierre.

**Nota de proceso:** el verificador posterior ejecutó accidentalmente `uv run`, que
sincronizó `.venv` y creó un lock transitorio luego eliminado. No produjo cambios en
DB, código, configuración ni staging, y no invalida la verificación read-only. La
desviación queda registrada para evitar repetirla.

**Límite de la evidencia Git:** el repositorio aún no tiene `HEAD` y sus archivos
están untracked. Por eso `git diff --check` no inspecciona efectivamente ese contenido;
la documentación requiere además una validación equivalente directa de Markdown.

## Decisiones confirmadas

- Antes de cualquier trabajo real habrá una validación local simulada sin duración
  fija. Usará identidades, roles, áreas y autoridad vigentes de CoreWork, pero
  objetivos, tareas, bloqueos, evidencias y situaciones totalmente ficticios,
  identificados como simulados y aislados del trabajo real.
- Después vendrá un piloto controlado real; luego el endurecimiento/preparación VPS y
  finalmente canary/producción. Estas etapas no se mezclan.
- La validación sigue las capas A-E del
  [`protocolo canónico`](validation/README.md): invariantes deterministas, evaluación
  end-to-end natural, holdout, replay/regresión y validación manual del usuario.
- Las pruebas automatizadas y evaluaciones del asistente no son validación definitiva
  ni pueden aprobar el piloto real. Sólo el usuario puede aprobar ese gate mediante
  Telegram real y no puede haber defectos críticos o altos abiertos en alcance.
- Cada escenario verifica respuesta visible, PostgreSQL, herramientas/efectos y
  auditoría. Una respuesta correcta con un efecto incorrecto falla.
- El proceso es evaluación y mejora del sistema, no fine-tuning. El fine-tuning queda
  fuera de alcance salvo evidencia y decisión futuras.
- La arquitectura se endurece y extiende; no se reescribe.
- Una solicitud incompleta es un borrador sin efectos.
- Una tarea sólo queda comprometida con objetivo, responsable, fecha objetivo,
  criterio de aceptación y política de evidencia.
- La conversión es explícita, confirmada y auditable.
- El roadmap vigente sigue las fases 0 a 8 de `docs/ROADMAP.md`.
- El objetivo arquitectónico sigue siendo un monolito modular, no microservicios.
- La autoridad de la validación y del piloto sigue una cadena simple: cada integrante
  actúa sobre el trabajo propio; el referente confirma, asigna y aprueba en su área;
  Dirección define prioridades, urgencias y cancelaciones y aprueba a referentes.
  Los cambios de pack requieren autorización de Dirección y aplicación
  administrativa; no existe suplencia automática.
- El escalamiento comienza en privado. Publicar en el grupo requiere confirmación
  explícita de Dirección; la falta persistente exige dos contactos privados y
  vencimiento comprobado, salvo urgencia declarada por Dirección.
- Anthropic es el proveedor LLM inicial. Una futura interfaz podrá seleccionar
  proveedor y modelo usando únicamente métodos oficiales de autenticación, pero esa
  capacidad no se considera implementada.
- Durante la validación simulada y el piloto se usará contexto operativo amplio,
  sin minimización funcional prematura y con las fronteras obligatorias de
  [`ADR 0002`](decisions/0002-pilot-llm-context-and-retention.md).
- Las conversaciones almacenadas por Prisma tienen retención indefinida hasta su
  eliminación por un administrador autorizado. Los participantes no pueden pedir
  borrado; el acceso y la eliminación administrativos deben restringirse y
  auditarse. La retención externa depende del proveedor y debe informarse.
- UI completa, dashboard avanzado, agenda externa, aprendizaje persistente y motor
  genérico de workflows quedan fuera del alcance actual.

Estas decisiones describen la política aceptada, no demuestran que sus controles
estén implementados.

## Cierre de Fase 0

- **Fecha:** 2026-08-12.
- **Criterio:** alcance simulado, métricas no compensatorias, pausa/reanudación,
  gobierno separado del corpus y gate manual exclusivo del usuario quedaron
  definidos sin crear escenarios ni afirmar controles implementados.
- **Resultado:** Fase 1 habilitada. Las obligaciones del piloto real y la VPS siguen
  en sus horizontes y no bloquean este cierre.

## Pendientes reservados para el piloto real

Estos puntos no bloquean Fase 0 ni la validación simulada:

- Definir para el futuro piloto real los tipos de trabajo aceptados, participantes,
  alcance temporal u operativo y métricas de aceptación o abandono.
- Obtener la aceptación organizacional de participantes y responsables sobre
  autoridad, privacidad y escalamiento antes del piloto real.
- Informar las condiciones externas vigentes de Anthropic antes del piloto real.

La topología inicial sigue pendiente antes de Fase 7 y tampoco bloquea la validación
simulada.

## Revisión pendiente del contexto LLM

- Comparar calidad, completitud, costo, latencia y exposición del contexto amplio
  frente a variantes reducidas o adaptativas.
- Diseñar y validar contexto adaptativo por intención sólo si la evidencia lo
  justifica; no es todavía una política aprobada.
- Iniciar la revisión con evidencia de validación simulada y ampliarla durante el
  piloto real sólo si hace falta. Registrar la decisión en una nueva ADR antes de
  Fase 7. Esta deuda no cierra la Fase 0.

## Riesgos prioritarios

1. Inbound Telegram no idempotente.
2. Ausencia de máquina de estados general.
3. Estado de objetivo mutable directamente.
4. Respuestas operativas sin contratos tipados ni frescura obligatoria.
5. Escalera que afirma falta de respuesta sin `pending_reply` operativo completo.
6. Modo local sin ejecución automática de cadencias.
7. Reimportación con reconciliación incompleta.
8. Cobertura RLS incompleta.

Pre-VPS se agregan: ACK rápido y cola/worker de entrada, pool DB, secreto de webhook
obligatorio, migraciones, TLS, observabilidad, backups/restore y rollback.

Antes de ejecutar la validación debe implementarse y verificarse un mecanismo para
congelar confirmaciones, cadencias, despachos y nuevos efectos sin destruir
conversación, PostgreSQL, logs ni auditoría. Es un requisito futuro de Fase 1, no un
control disponible hoy ni un bloqueo para el cierre documental de Fase 0.

## Próximo paso

Planificar la Unidad 1B, integridad del ciclo de vida y estados, como la próxima unidad
revisable. Está habilitada por el cierre de 1A, pero no debe declararse activa ni
implementada hasta acordar su alcance y comenzar trabajo de código explícitamente.
