# Documentación de Leda

Esta base documental permite retomar el proyecto desde el estado vigente sin
reconstruir decisiones desde conversaciones anteriores.

Leda es un producto de gestión de proyectos multi-tenant. CoreWork es su primer
cliente, no su definición.

## Camino rápido

Desde el 2026-10-04 el trabajo vigente es **el Motor** (definición en [`../AGENTS.md`](../AGENTS.md),
"Nombres que usamos") y está en la rama `feat/motor-de-conversacion` (carpeta
`D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`). Una sesión nueva empieza por
[`STATUS.md`](STATUS.md), "Punto exacto para retomar", y por [`../AGENTS.md`](../AGENTS.md), "Dónde
se trabaja y qué no se hace".

1. Leer [`product/que-es-leda.md`](product/que-es-leda.md) para entender qué es
   el producto.
2. Leer [`architecture/frontera.md`](architecture/frontera.md) para entender dónde
   termina el núcleo y qué reglas lo gobiernan.
3. Consultar [`ROADMAP.md`](ROADMAP.md) para saber qué se aprovecha, qué se corrige y en qué
   orden (criterio del ADR 0017, decisión 5).
4. Abrir [`STATUS.md`](STATUS.md) para el estado operativo, los riesgos y el orden de trabajo
   vigente.
5. Abrir arquitectura detallada o decisiones sólo si la tarea lo requiere.

## Navegación

| Necesidad | Documento |
|---|---|
| Definición del producto y alcance | [`product/que-es-leda.md`](product/que-es-leda.md) |
| Documento de la unidad en curso, el Motor (sólo en la rama `feat/motor-de-conversacion`) | [`../odd/tasks/motor-de-conversacion.md`](../odd/tasks/motor-de-conversacion.md) |
| Qué se probó de cada flujo y modelo, y la conclusión vigente | [`product/bitacora-de-flujos.md`](product/bitacora-de-flujos.md) |
| Análisis adversarial del 2026-10-04: mercado, arquitecturas de agentes, confiabilidad, revisión interna y Engram | [`research/gestion-del-dialogo-y-arquitecturas-de-agentes.md`](research/gestion-del-dialogo-y-arquitecturas-de-agentes.md) |
| Qué tiene que permitir configurar la plataforma (inventario) | [`product/plataforma-pendientes.md`](product/plataforma-pendientes.md) |
| Frontera entre núcleo y adaptadores | [`architecture/frontera.md`](architecture/frontera.md) |
| Qué se aprovecha, corrige y descarta; criterio y orden del ADR 0017 (decisión 5) y la lista "Anotado para más adelante" | [`ROADMAP.md`](ROADMAP.md) |
| Estado, riesgos, orden de trabajo vigente y próximo paso | [`STATUS.md`](STATUS.md) |
| Arquitectura implementada | [`architecture/current-state.md`](architecture/current-state.md) |
| Interpretación, aclaración y confirmación (diseño de los flujos anteriores al Motor, vivo hasta el 2026-09-29; gobiernan los ADR que cita) | [`architecture/interpretacion-y-confirmacion.md`](architecture/interpretacion-y-confirmacion.md) |
| Arquitectura objetivo previa | [`architecture/target-state.md`](architecture/target-state.md) |
| Decisión sobre borradores | [`decisions/0001-drafts-and-committed-tasks.md`](decisions/0001-drafts-and-committed-tasks.md) |
| Decisión sobre contexto LLM y retención | [`decisions/0002-pilot-llm-context-and-retention.md`](decisions/0002-pilot-llm-context-and-retention.md) |
| Decisión sobre las dos superficies web separadas | [`decisions/0004-dos-superficies-separadas.md`](decisions/0004-dos-superficies-separadas.md) |
| Decisión sobre interpretación, confirmación y aclaración con botones | [`decisions/0005-interpretacion-y-confirmacion.md`](decisions/0005-interpretacion-y-confirmacion.md) |
| Decisión sobre Jev para resolver referencias y detectar la duda de intención | [`decisions/0006-jev-para-resolver-referencias-e-intencion.md`](decisions/0006-jev-para-resolver-referencias-e-intencion.md) |
| Decisión sobre Leda que orienta con opciones concretas, no charla | [`decisions/0007-leda-orienta-no-charla.md`](decisions/0007-leda-orienta-no-charla.md) |
| Decisión sobre que aprobar cierra la tarea, en el mismo acto, si se puede | [`decisions/0008-la-aprobacion-cierra-la-tarea.md`](decisions/0008-la-aprobacion-cierra-la-tarea.md) |
| Decisión sobre entrega con evidencia y revisión | [`decisions/0009-entrega-con-evidencia-y-revision.md`](decisions/0009-entrega-con-evidencia-y-revision.md) |
| Decisión sobre correo verificado y Google (propuesta) | [`decisions/0010-correo-verificado-y-google-en-el-producto.md`](decisions/0010-correo-verificado-y-google-en-el-producto.md) |
| Decisión sobre respuesta inmediata e indicador de actividad | [`decisions/0011-respuesta-inmediata-e-indicador-de-actividad.md`](decisions/0011-respuesta-inmediata-e-indicador-de-actividad.md) |
| Decisión sobre ruteo en paralelo con la primera respuesta | [`decisions/0012-ruteo-en-paralelo-con-la-primera-respuesta.md`](decisions/0012-ruteo-en-paralelo-con-la-primera-respuesta.md) |
| Decisión sobre las reglas generales de la conversación (superada en parte el 2026-10-04; ver su nota) | [`decisions/0013-reglas-generales-de-la-conversacion.md`](decisions/0013-reglas-generales-de-la-conversacion.md) |
| Decisión sobre el flujo de un mensaje, con un dueño por etapa, y el experimento A/B (superada en parte el 2026-10-04; ver su nota. Sus flujos C1 a C6 quedaron congelados) | [`decisions/0014-flujo-de-un-mensaje.md`](decisions/0014-flujo-de-un-mensaje.md) |
| Decisión sobre el renombre del producto a Leda | [`decisions/0015-renombre-del-producto-a-leda.md`](decisions/0015-renombre-del-producto-a-leda.md) |
| Decisión sobre los avisos a otras personas guardados como hechos (implementada sólo en la rama congelada; el ADR 0018, decisión 8, trae su mecanismo; ver su nota) | [`decisions/0016-avisos-a-otras-personas-desde-hechos.md`](decisions/0016-avisos-a-otras-personas-desde-hechos.md) |
| Decisión sobre el alcance del Motor: por chat, los hechos del trabajo; por la web, su estructura (aceptada en el paso M1, 2026-10-04) | [`decisions/0017-por-chat-los-hechos-por-la-web-la-estructura.md`](decisions/0017-por-chat-los-hechos-por-la-web-la-estructura.md) |
| Decisión sobre el motor de conversación (aceptada el 2026-10-06, después de que pasó la prueba chica) | [`decisions/0018-motor-de-conversacion.md`](decisions/0018-motor-de-conversacion.md) |
| Relevamientos de proyectos externos (Hermes Agent) | [`research/hermes-agent.md`](research/hermes-agent.md) |
| Relevamiento de NotebookLM y respuestas ancladas en fuentes | [`research/notebooklm-y-grounding.md`](research/notebooklm-y-grounding.md) |
| Aprendizajes del `SOUL.md` y del contexto operativo de Prisma en Hermes (trabajo anterior del usuario) | [`research/soul-y-contexto-de-prisma-en-hermes.md`](research/soul-y-contexto-de-prisma-en-hermes.md) |
| Copias de documentos anteriores: `STATUS` y `AGENTS` hasta el 2026-09-30, hasta el 2026-10-04 y hasta el paso M1; el documento de la unidad del Motor hasta el paso M1; y el diario de Leda orienta. Son historia, no instrucciones vigentes | [`historial/`](historial/) |
| Reglas para futuras sesiones | [`../AGENTS.md`](../AGENTS.md) |
| Configuración del primer cliente | [`../espacios/corework.yaml`](../espacios/corework.yaml) |

Los ADR 0016, 0017 y 0018 están también en `main`, que recibió los documentos del Motor por
avance rápido. El ADR 0016 nació en la rama de flujo congelada, donde está implementado.

## Validación

| Necesidad | Documento |
|---|---|
| Protocolo canónico, capas A-E, corpus, rúbrica y gate | [`validation/README.md`](validation/README.md) |
| Ejecución manual por Telegram sin frases guionadas | [`validation/manual-validation-guide.md`](validation/manual-validation-guide.md) |
| Metadatos y cobertura del corpus, sin casos ni secretos | [`validation/corpus-manifest-template.md`](validation/corpus-manifest-template.md) |

## Documentos superados

Se conservan como registro histórico. **No describen el alcance vigente y no deben
usarse para decidir.** El motivo de las cuatro primeras filas está en
[`ROADMAP.md`](ROADMAP.md#qué-queda-superado); el de las demás, en su propia fila.

| Documento | Motivo resumido |
|---|---|
| [`decisions/0003-authenticated-inbound-boundary.md`](decisions/0003-authenticated-inbound-boundary.md) | Modelo de amenaza escrito para un asistente interno de un solo equipo. En un producto multi-tenant la amenaza principal es el cruce entre clientes. |
| [`phases/00-pilot-scope.md`](phases/00-pilot-scope.md) | Alcance de piloto local para un único equipo. |
| [`phases/01-local-pilot-foundations.md`](phases/01-local-pilot-foundations.md) | Organizado por unidades de piloto local, superadas por el orden de entrega vigente. |
| [`product/functional-specification.md`](product/functional-specification.md) | Genérica por intención, pero precede al modelo multi-tenant: no separa configuración de cliente de núcleo del producto ni trata el aislamiento como garantía. |
| [`traspaso/2026-10-01-alta-conducida.md`](traspaso/2026-10-01-alta-conducida.md), [`traspaso/2026-10-02-renombre-a-leda.md`](traspaso/2026-10-02-renombre-a-leda.md) y [`traspaso/2026-10-02-flujo-c4.md`](traspaso/2026-10-02-flujo-c4.md) | Traspasos de las jornadas del flujo C y del renombre. Dejaron de ser puntos de retorno el 2026-10-04: sus pendientes y su forma de trabajar quedaron congelados o superados (ver [`STATUS.md`](STATUS.md), "Qué quedó congelado o superado"). |
| [`historial/STATUS-hasta-2026-10-04.md`](historial/STATUS-hasta-2026-10-04.md) y [`historial/AGENTS-hasta-2026-10-04.md`](historial/AGENTS-hasta-2026-10-04.md) | Copias del estado y de las reglas de trabajo antes del cambio de rumbo del 2026-10-04, literales salvo el aviso de archivo de su primera línea. Sus órdenes de trabajo y sus puntos de retorno ya no rigen. |
| [`historial/STATUS-hasta-M1.md`](historial/STATUS-hasta-M1.md), [`historial/AGENTS-hasta-M1.md`](historial/AGENTS-hasta-M1.md) y [`historial/motor-de-conversacion-hasta-M1.md`](historial/motor-de-conversacion-hasta-M1.md); y [`historial/AGENTS-antes-de-reducir.md`](historial/AGENTS-antes-de-reducir.md), la versión larga de `AGENTS.md` antes de reducirlo a lo que sirve | Copias del estado, de las reglas de trabajo y del documento de la unidad del Motor hasta el paso M1 (2026-10-04), antes de condensarlos; literales salvo el aviso de archivo de su primera línea. Lo que figura ahí como pendiente o próximo paso ya no rige: lo vigente está en `STATUS.md`, en el documento de la unidad y en los ADR 0017 y 0018. |

Superados en parte por los ADR 0017 y 0018, con una nota del 2026-10-04 al comienzo que dice qué
sigue vigente: los ADR [`0013`](decisions/0013-reglas-generales-de-la-conversacion.md) y
[`0014`](decisions/0014-flujo-de-un-mensaje.md).

Los documentos de `../odd/tasks/` que están en `main` son los diarios de las unidades anteriores
al Motor. Cada uno lleva una nota del 2026-10-04 al comienzo: lo que figure ahí como en curso,
pendiente o próximo paso no se retoma sin una decisión del usuario.

Parte del contenido de la decisión 0003 se reutiliza: su inventario de autoridad y
privilegios alimenta el cierre del aislamiento entre clientes.

## Regla de interpretación

Los documentos separan hechos comprobados, riesgos comprobados, inferencias y
recomendaciones. Si un documento contradice el código o el esquema actual, registrar
la discrepancia en `STATUS.md`; no corregirla por suposición.

Ante una discrepancia entre documentos de arquitectura, prevalece
[`architecture/frontera.md`](architecture/frontera.md).
