# Fase 0: alcance de validación local simulada

> **Superada por cambio de alcance — 2026-09-22.**
>
> Este documento define el alcance de un piloto local para un único equipo. Prisma
> pasó a ser un producto de gestión de proyectos multi-tenant, y el trabajo ya no se
> organiza por fases de piloto. Se conserva como registro histórico y **no debe usarse
> para decidir**. Para el alcance vigente:
> [`../product/que-es-prisma.md`](../product/que-es-prisma.md),
> [`../architecture/frontera.md`](../architecture/frontera.md) y
> [`../ROADMAP.md`](../ROADMAP.md).

**Estado:** cerrada el 2026-08-12. Se cerraron alcance, métricas, pausa y
reanudación, gobierno del corpus y gate humano. Los pendientes reservados para el
piloto real o la VPS no bloquean este cierre.

La fase termina cuando el alcance, las métricas, las pausas y la protección del
corpus de validación simulada son explícitos. No requiere implementar código, crear
todavía los escenarios ni volver a decidir contratos ya aprobados.

## Resultado esperado

Una validación local segura y evaluable, sin plazo fijo, que usa identidades, roles,
áreas y autoridad actuales de CoreWork con objetivos, tareas, bloqueos, evidencias y
situaciones ficticios, identificados como simulados y aislados del trabajo real.

## Alcance propuesto

- [x] Usar únicamente el workspace CoreWork.
- [x] Usar identidades, roles, áreas y autoridad vigentes de CoreWork.
- [x] Usar sólo objetivos, tareas, bloqueos, evidencias y situaciones ficticios,
  marcados como simulados y aislados del trabajo real.
- [x] Cerrar la etapa por criterios y gate manual, sin duración fija.
- [x] Excluir explícitamente UI completa, dashboard avanzado, agenda externa,
  aprendizaje persistente, workflows genéricos y microservicios.
- [x] Definir métricas duras, criterios conversacionales y baselines operativos sin
  promedios compensatorios ni umbrales arbitrarios.
- [x] Definir condiciones para pausar, reanudar o terminar la validación.
- [x] Definir separación, custodia, versionado y renovación del corpus de desarrollo
  y del holdout sin crear aún sus escenarios.

El protocolo aplicable es [`../validation/README.md`](../validation/README.md). Las
pruebas y evaluaciones automatizadas sólo habilitan la validación manual E; no
aprueban el piloto real.

## Cinco decisiones del cierre

### 1. Contrato de compromiso

**RESUELTA.** Aplicar ADR 0001: un pedido incompleto es borrador. La tarea sólo se
compromete con objetivo, responsable, fecha, criterio de aceptación y política de
evidencia; la conversión es explícita, confirmada y auditable.

- [x] No volver a pedir esta decisión.
- [ ] Confirmar únicamente el vocabulario visible que usará el equipo para
  “borrador” y “tarea comprometida”, si difiere.

El vocabulario visible puede ajustarse durante el diseño conversacional; no cambia
el contrato de dominio ni bloquea el cierre de esta fase.

### 2. Autoridad inicial

**RESUELTA COMO POLÍTICA; PENDIENTE DE IMPLEMENTACIÓN Y VALIDACIÓN.** Durante la
validación simulada y el futuro piloto:

- [x] cada integrante puede proponer trabajo y actualizar únicamente el propio;
- [x] el referente confirma y asigna trabajo de su área y aprueba a sus integrantes;
- [x] Dirección define prioridades, urgencias y cancelaciones, y aprueba a los
  referentes;
- [x] cambiar el pack requiere autorización de Dirección y aplicación del
  administrador;
- [x] no existe suplencia automática: Dirección resuelve cada ausencia de forma
  explícita y auditable.

La conversación no amplía autoridad. Toda excepción debe ser explícita y auditable.

### 3. Escalamiento público

**RESUELTA COMO POLÍTICA; PENDIENTE DE IMPLEMENTACIÓN Y VALIDACIÓN.** Prisma
contacta primero en privado:

- [x] los problemas técnicos pueden elevarse en privado al referente;
- [x] los bloqueos transversales, desacuerdos o falta persistente de respuesta
  pueden prepararse para Dirección;
- [x] publicar en el grupo requiere confirmación explícita de Dirección;
- [x] la falta persistente exige dos contactos privados y vencimiento comprobado;
- [x] una urgencia declarada por Dirección puede omitir la espera;
- [x] el contenido se limita al trabajo afectado, plazo, gestiones previas, impacto
  comprobado y decisión requerida;
- [x] nunca se incluyen conversaciones privadas, datos personales, excusas ni
  juicios;
- [x] al escalar se detienen los recordatorios equivalentes.

El silencio por sí solo no cambia estado ni prueba atraso o bloqueo.

### 4. Privacidad y retención del LLM

**RESUELTA COMO POLÍTICA.** Aplicar
[`ADR 0002`](../decisions/0002-pilot-llm-context-and-retention.md): Anthropic es el
proveedor inicial y estas primeras etapas usan contexto operativo amplio, sin
minimización funcional prematura. Esto no permite enviar secretos o credenciales,
datos de otros espacios ni información que el actor no esté autorizado a usar.

- [x] Las conversaciones en almacenamiento local o VPS tienen retención indefinida
  hasta su eliminación por un administrador autorizado.
- [x] Los participantes no pueden solicitar el borrado.
- [x] El acceso y la eliminación administrativos deben estar restringidos y
  auditados como política.
- [x] La retención externa depende del proveedor y debe informarse.
- [ ] Antes del piloto real, informar las condiciones vigentes de
  retención, entrenamiento y ubicación de datos ofrecidas por Anthropic.
- [ ] Implementar y verificar la restricción y auditoría del acceso y la eliminación
  administrativos; esta decisión no prueba esos controles.
- [ ] Revisar inicialmente el contexto con evidencia de validación simulada y cerrar
  la decisión antes de Fase 7, usando evidencia del piloto real sólo si hace falta.

No incluir secretos en conversaciones ni documentación.

### 5. Topología VPS

**RECOMENDACIÓN NO BLOQUEANTE PARA LA VALIDACIÓN SIMULADA.** Mantener una VPS única
con monolito modular, PostgreSQL y procesos separados de entrada/salida cuando llegue
el momento. No adoptar microservicios.

- [ ] Antes de Fase 7, confirmar proveedor, región, dominio y responsables operativos.
- [ ] Antes de Fase 7, definir TLS, backups externos, restore, observabilidad y rollback.
- [ ] Antes de Fase 8, definir alcance y duración del canary.

## Pendientes reservados para el piloto real

Estos puntos no bloquean la validación simulada:

- [ ] enumerar tipos de trabajo real aceptados y exclusiones;
- [ ] acordar participantes, responsables y alcance temporal u operativo;
- [ ] obtener aceptación sobre autoridad, privacidad y escalamiento;
- [ ] informar condiciones vigentes del proveedor y retención;
- [ ] definir métricas de aceptación y abandono del piloto real.

## Criterios de salida

- [x] Workspace, identidades y separación de datos simulados están resueltos.
- [x] Las decisiones aplicables a la validación están registradas sin ambigüedad.
- [x] Existen métricas y condiciones de pausa, reanudación y finalización.
- [x] Corpus de desarrollo y holdout están gobernados sin crear escenarios ni
  exponer contenido reservado.
- [x] El gate exige capa E manual y aprobación explícita exclusiva del usuario, sin
  defectos críticos o altos abiertos.
- [x] No quedan capacidades fuera de alcance presentadas como prerequisito.
- [x] `docs/STATUS.md` refleja las decisiones y habilita Fase 1.
