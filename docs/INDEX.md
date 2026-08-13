# Documentación de Prisma

Esta base documental permite retomar el proyecto desde el estado vigente sin
reconstruir decisiones desde conversaciones anteriores.

## Camino rápido

1. Leer [`STATUS.md`](STATUS.md).
2. Revisar la fase activa en
   [`phases/01-local-pilot-foundations.md`](phases/01-local-pilot-foundations.md).
3. Consultar [`ROADMAP.md`](ROADMAP.md) para entender qué viene después.
4. Abrir arquitectura, ADR o especificación sólo si la tarea lo requiere.

## Navegación

| Necesidad | Documento |
|---|---|
| Estado, riesgos y próximo paso | [`STATUS.md`](STATUS.md) |
| Secuencia de evolución | [`ROADMAP.md`](ROADMAP.md) |
| Alcance de validación local simulada | [`phases/00-pilot-scope.md`](phases/00-pilot-scope.md) |
| Fundaciones de validación local simulada | [`phases/01-local-pilot-foundations.md`](phases/01-local-pilot-foundations.md) |
| Arquitectura implementada | [`architecture/current-state.md`](architecture/current-state.md) |
| Arquitectura objetivo | [`architecture/target-state.md`](architecture/target-state.md) |
| Decisión sobre borradores | [`decisions/0001-drafts-and-committed-tasks.md`](decisions/0001-drafts-and-committed-tasks.md) |
| Decisión sobre contexto LLM y retención del piloto | [`decisions/0002-pilot-llm-context-and-retention.md`](decisions/0002-pilot-llm-context-and-retention.md) |
| Visión funcional general | [`product/functional-specification.md`](product/functional-specification.md) |
| Reglas para futuras sesiones | [`../AGENTS.md`](../AGENTS.md) |

## Validación

| Necesidad | Documento |
|---|---|
| Protocolo canónico, capas A-E, corpus, rúbrica y gate | [`validation/README.md`](validation/README.md) |
| Ejecución manual por Telegram sin frases guionadas | [`validation/manual-validation-guide.md`](validation/manual-validation-guide.md) |
| Metadatos y cobertura del corpus, sin casos ni secretos | [`validation/corpus-manifest-template.md`](validation/corpus-manifest-template.md) |

## Lectura por horizonte

**Para trabajar ahora:** `STATUS`, Fase 1, ADR 0001 y estado actual.

**Para diseñar la validación:** protocolo canónico, Fase 1 y estado objetivo local.

**Para habilitar el piloto real:** completar la capa E y registrar la aprobación
explícita del usuario; ninguna evaluación automática puede concederla.

**Para preparar despliegue:** roadmap, estado objetivo pre-VPS y criterios de las
fases 7 y 8. No tratar ese horizonte como alcance actual.

## Regla de interpretación

Los documentos separan hechos comprobados, riesgos comprobados, inferencias y
recomendaciones. Si un documento contradice el código o el esquema actual, registrar
la discrepancia en `STATUS.md`; no corregirla por suposición.
