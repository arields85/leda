# Documentación de Prisma

Esta base documental permite retomar el proyecto desde el estado vigente sin
reconstruir decisiones desde conversaciones anteriores.

Prisma es un producto de gestión de proyectos multi-tenant. CoreWork es su primer
cliente, no su definición.

## Camino rápido

1. Leer [`product/que-es-prisma.md`](product/que-es-prisma.md) para entender qué es
   el producto.
2. Leer [`architecture/frontera.md`](architecture/frontera.md) para entender dónde
   termina el núcleo y qué reglas lo gobiernan.
3. Consultar [`ROADMAP.md`](ROADMAP.md) para saber qué se aprovecha, qué se corrige y
   en qué orden.
4. Abrir [`STATUS.md`](STATUS.md) para el estado operativo y los riesgos vigentes.
5. Abrir arquitectura detallada o decisiones sólo si la tarea lo requiere.

## Navegación

| Necesidad | Documento |
|---|---|
| Definición del producto y alcance | [`product/que-es-prisma.md`](product/que-es-prisma.md) |
| Frontera entre núcleo y adaptadores | [`architecture/frontera.md`](architecture/frontera.md) |
| Qué se aprovecha, corrige y descarta, y en qué orden | [`ROADMAP.md`](ROADMAP.md) |
| Estado, riesgos y próximo paso | [`STATUS.md`](STATUS.md) |
| Arquitectura implementada | [`architecture/current-state.md`](architecture/current-state.md) |
| Arquitectura objetivo previa | [`architecture/target-state.md`](architecture/target-state.md) |
| Decisión sobre borradores | [`decisions/0001-drafts-and-committed-tasks.md`](decisions/0001-drafts-and-committed-tasks.md) |
| Decisión sobre contexto LLM y retención | [`decisions/0002-pilot-llm-context-and-retention.md`](decisions/0002-pilot-llm-context-and-retention.md) |
| Decisión sobre las dos superficies web separadas | [`decisions/0004-dos-superficies-separadas.md`](decisions/0004-dos-superficies-separadas.md) |
| Reglas para futuras sesiones | [`../AGENTS.md`](../AGENTS.md) |
| Configuración del primer cliente | [`../espacios/corework.yaml`](../espacios/corework.yaml) |

## Validación

| Necesidad | Documento |
|---|---|
| Protocolo canónico, capas A-E, corpus, rúbrica y gate | [`validation/README.md`](validation/README.md) |
| Ejecución manual por Telegram sin frases guionadas | [`validation/manual-validation-guide.md`](validation/manual-validation-guide.md) |
| Metadatos y cobertura del corpus, sin casos ni secretos | [`validation/corpus-manifest-template.md`](validation/corpus-manifest-template.md) |

## Documentos superados

Se conservan como registro histórico. **No describen el alcance vigente y no deben
usarse para decidir.** El motivo de cada uno está en
[`ROADMAP.md`](ROADMAP.md#qué-queda-superado).

| Documento | Motivo resumido |
|---|---|
| [`decisions/0003-authenticated-inbound-boundary.md`](decisions/0003-authenticated-inbound-boundary.md) | Modelo de amenaza escrito para un asistente interno de un solo equipo. En un producto multi-tenant la amenaza principal es el cruce entre clientes. |
| [`phases/00-pilot-scope.md`](phases/00-pilot-scope.md) | Alcance de piloto local para un único equipo. |
| [`phases/01-local-pilot-foundations.md`](phases/01-local-pilot-foundations.md) | Organizado por unidades de piloto local, superadas por el orden de entrega vigente. |
| [`product/functional-specification.md`](product/functional-specification.md) | Genérica por intención, pero precede al modelo multi-tenant: no separa configuración de cliente de núcleo del producto ni trata el aislamiento como garantía. |

Parte del contenido de la decisión 0003 se reutiliza: su inventario de autoridad y
privilegios alimenta el cierre del aislamiento entre clientes.

## Regla de interpretación

Los documentos separan hechos comprobados, riesgos comprobados, inferencias y
recomendaciones. Si un documento contradice el código o el esquema actual, registrar
la discrepancia en `STATUS.md`; no corregirla por suposición.

Ante una discrepancia entre documentos de arquitectura, prevalece
[`architecture/frontera.md`](architecture/frontera.md).
