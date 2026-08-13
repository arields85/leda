# Estado arquitectónico objetivo

La evolución conserva un monolito modular. El objetivo es cerrar invariantes y
límites operativos antes de aumentar infraestructura, no distribuir el sistema.

## Horizonte 1: validación local simulada y piloto controlado

```text
Telegram polling
      |
 inbound idempotente
      |
 intención + contrato operativo
      |
 lectura vigente autorizada
      |
 borrador -> confirmación -> tarea comprometida
      |
 herramientas + reglas de dominio
      |
 PostgreSQL + auditoría + outbox
      |
 escalera/cadencias verificables
```

Antes del piloto real, la validación simulada debe alcanzar:

- un alcance pequeño y explícito, con autoridad, privacidad y escalamiento
  acordados;
- borradores sin efectos y conversión explícita a tareas completas;
- idempotencia de updates entrantes y efectos salientes;
- máquina de estados y cierre coherentes para tareas y objetivos;
- contratos estructurados para respuestas operativas, con lectura fresca obligatoria;
- política de evidencia materializada y aprobaciones evaluadas contra estado vigente;
- solicitudes de respuesta persistidas, satisfechas y escaladas con hechos reales;
- cadencias automáticas reales en el modo que usará el piloto;
- RLS y reconciliación de configuración verificadas;
- trazas operativas suficientes para explicar decisiones sin exponer secretos.

La topología local puede seguir siendo un proceso de escucha más PostgreSQL mientras
los efectos sean fieles al comportamiento que se pretende validar. El piloto
controlado real sólo comienza después de la aprobación manual del usuario y reutiliza
estos controles con alcance real limitado.

## Horizonte 2: preparación pre-VPS

El mismo monolito modular se separa por procesos operativos, no por servicios de
dominio:

```text
Telegram -> HTTPS/webhook -> ACK rápido -> cola de entrada -> worker de aplicación
                                                       |
                                                PostgreSQL con pool
                                                       |
                                            outbox -> worker de salida
```

Antes de exponerlo en una VPS se requiere:

- secreto de webhook obligatorio y validado al arrancar;
- TLS y superficie de red mínima;
- ACK rápido, cola de entrada durable y worker idempotente;
- pool de conexiones y límites explícitos;
- migraciones versionadas, con avance y rollback ensayados;
- logs estructurados, métricas, salud útil y alertas accionables;
- backups externos, retención definida y restore probado;
- despliegue reproducible y procedimiento de rollback;
- canary con alcance reducido antes de ampliar usuarios o espacios.

## Decisiones de diseño

| Tema | Dirección |
|---|---|
| Arquitectura | Monolito modular con procesos operativos separados cuando haga falta. |
| Datos | PostgreSQL continúa como fuente de verdad y límite transaccional. |
| Mensajería | Idempotencia en entrada y outbox en salida. |
| LLM | Interpreta y redacta; contratos y políticas controlan hechos y completitud. |
| Configuración | Packs gobernados, versionados, reconciliables y auditables. |
| Multi-tenant | RLS completo y pruebas negativas entre espacios. |
| Despliegue | VPS única para el canary; no microservicios. |

## Fuera de horizonte

No forman parte de la validación, el piloto ni el endurecimiento inicial: UI
administrativa completa, dashboard avanzado, calendarios externos, aprendizaje
persistente, motor genérico de workflows y microservicios.
