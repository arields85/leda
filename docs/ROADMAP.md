# Roadmap de evolución

El roadmap ordena resultados verificables. Cada fase se cierra por criterios de
salida, no por cantidad de tareas completadas.

## Fase 0: alcance de validación local simulada

**Objetivo:** acordar qué se validará con datos ficticios, bajo qué autoridad y con
qué métricas, pausas y protección del corpus.

**Entregables:** alcance simulado, protocolo de validación, definición del dataset y
criterios de éxito, pausa y gate manual.

**Salida:** checklist de [`phases/00-pilot-scope.md`](phases/00-pilot-scope.md)
resuelto; ningún supuesto crítico queda delegado al modelo.

## Fase 1: integridad para la validación

**Objetivo:** impedir estados y compromisos inválidos antes de optimizar respuestas.

**Entregables:** borradores, conversión auditable, tareas completas, transiciones
válidas, inbound idempotente, evidencia/aprobación coherentes, pending replies
operativos, RLS y reconciliación.

**Salida:** invariantes demostradas con pruebas contra PostgreSQL y escenarios de
concurrencia; ver [`phases/01-local-pilot-foundations.md`](phases/01-local-pilot-foundations.md).

## Fase 2: lecturas deterministas para la validación

**Objetivo:** obtener la misma conclusión operativa ante los mismos datos y permisos.

**Entregables:** contratos tipados por intención, lecturas frescas, completitud,
distinción entre vacío/error/sin permiso y presentación controlada.

**Salida:** pruebas comparan la respuesta estructurada con PostgreSQL y detectan
omisiones, no sólo texto esperado.

## Fase 3: efectos completos e idempotentes para la validación

**Objetivo:** asegurar que cada efecto confirmado ocurra una sola vez y pueda
explicarse.

**Entregables:** ciclo propuesta-modificación-cancelación-confirmación, revalidación,
auditoría y verificación de resultados para todas las acciones en alcance.

**Salida:** reintentos, doble toque, vencimiento y concurrencia no duplican efectos ni
usan propuestas obsoletas.

## Fase 4: automatización local veraz para la validación

**Objetivo:** ejecutar localmente las cadencias y escalamientos que debe evaluar la
validación simulada.

**Entregables:** planificador local, solicitudes de respuesta reales, reloj
controlable y observabilidad operativa básica.

**Salida:** escenarios con tiempo simulado prueban envío, silencio, respuesta,
bloqueo, ausencia, deduplicación y escalamiento.

## Fase 5: validación local simulada

**Objetivo:** demostrar corrección y resiliencia sin usar objetivos, tareas ni
situaciones de trabajo real.

**Entregables:** capas A-D del
[`protocolo`](validation/README.md), corpus de desarrollo y holdout separados,
replays/regresiones y luego validación manual E por Telegram real.

**Salida:** cero defectos críticos o altos abiertos en alcance y aprobación explícita
del usuario. Las pruebas y evaluaciones del asistente sólo habilitan la capa E; no
aprueban el pase al piloto real.

### Revisión inicial: contexto LLM

Tras la validación simulada, revisar inicialmente el contexto amplio con su evidencia
de calidad, completitud, costo, latencia y exposición. Si la evidencia no alcanza,
la revisión puede continuar durante el piloto controlado real. La decisión que
adopte, ajuste o reemplace la política temporal de
[`ADR 0002`](decisions/0002-pilot-llm-context-and-retention.md) debe quedar cerrada
en una ADR posterior antes de iniciar Fase 7. El contexto adaptativo por intención
sigue siendo una alternativa a evaluar, no una política aprobada.

## Fase 6: piloto controlado real

**Objetivo:** validar utilidad, tono, carga de contacto y confianza con trabajo real
de alcance acordado y radio de impacto limitado.

**Entrada obligatoria:** aprobación humana de Fase 5; ningún agente o LLM puede
concederla.

**Entregables:** ejecución controlada, aceptación e información de participantes,
registro de incidentes y feedback, revisión de métricas y evidencia adicional para
la política de contexto LLM si fuera necesaria.

**Salida:** criterios del piloto cumplidos, sin defectos críticos o altos abiertos, y
decisión humana explícita de preparar VPS.

## Fase 7: endurecimiento y preparación VPS

**Objetivo:** preparar operación segura y recuperable en internet.

**Entregables:** ACK y cola de entrada, workers, pool, secreto obligatorio,
migraciones, TLS, observabilidad, backups/restore y rollback.

**Salida:** ensayo reproducible de despliegue, migración, restore y rollback; controles
de seguridad y capacidad aprobados.

## Fase 8: canary y producción VPS

**Objetivo:** exponer la operación en VPS con el menor radio de impacto y ampliar
sólo con evidencia estable.

**Entregables:** despliegue canary, monitoreo, runbooks e incident review.

**Salida:** ventana canary estable y decisión explícita de ampliar a producción,
corregir o volver atrás.

## Horizonte futuro: capacidades posteriores

**Objetivo:** ampliar producto sólo con evidencia de necesidad.

**Entregables posibles:** administración asistida, informes más ricos, agenda e
integraciones, aprendizaje gobernado u otras capacidades priorizadas.

Cada capacidad requiere un problema probado, decisión propia y criterios de éxito.
No se adopta microservicios por defecto.
