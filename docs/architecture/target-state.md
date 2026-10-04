# Estado arquitectónico objetivo

> **Nota del 2026-10-04.** Documento anterior al Motor. La arquitectura objetivo de la capa de
> conversación se define en el ADR 0018 (`PENDIENTE`); lo que este documento dice sobre el
> camino de un mensaje no se toma como plan vigente. Estado y orden de trabajo:
> [`../STATUS.md`](../STATUS.md).

La evolución conserva un monolito modular. El objetivo es cerrar invariantes y
límites operativos antes de aumentar infraestructura, no distribuir el sistema.

## Horizonte 1: validación local simulada y piloto controlado

```text
Telegram webhook/polling autenticado por bot
                    |
          leda_ingress + T1 durable
                    |
 recibo inmutable (bot_scope, update_id) + capacidad opaca
                    |
       leda_app + T2 recuperable + LLM/herramientas
                    |
   capacidad -> actor/espacio derivados -> autoridad vigente
                    |
 leda_gateway Unidad 1A + demás límites de dominio
                    |
 PostgreSQL + auditoría autoritativa + outbox
                    |
 leda_dispatcher mínimo -> Telegram/incidentes técnicos
```

Este flujo es el objetivo de
[`ADR 0003`](../decisions/0003-authenticated-inbound-boundary.md), no una descripción
del estado implementado. Antes del piloto puede ejecutarse dentro del mismo monolito,
pero con conexiones y membresías PostgreSQL disjuntas para `leda_ingress`,
`leda_app`, `leda_gateway`, `leda_dispatcher` y `leda_admin`. Ningún login
puede asumir varias de esas fronteras. El proceso de serving o polling no carga la
credencial administrativa.

T1 confirma el recibo antes del LLM y T2 puede recuperarse sin repetir efectos. Las
funciones resuelven actor y espacio desde la capacidad y revalidan autoridad; no
confían en identidad aportada por la aplicación. Un `edited_message` puede conservarse
como historia, pero no produce efectos operativos.

El dispatcher sólo reclama mensajes de outbox ya listos y puede marcar envío,
reintento o fallo y abrir incidentes técnicos de transporte. No redacta contenido,
cambia destinatarios ni escribe dominio. Conversación, auditoría autoritativa e
incidentes técnicos permanecen separados: `leda_app` no puede atribuir acciones
humanas; esa auditoría nace sólo en T2b cercada, gateway de Unidad 1A o una acción
administrativa identificada.

El ingreso histórico anterior a T1 se conserva como conversación legacy de sólo
lectura y no autoritativa. No se elimina ni se convierte en recibo, y no puede
reintentarse o producir efectos.

Antes del piloto real, la validación simulada debe alcanzar:

- un alcance pequeño y explícito, con autoridad, privacidad y escalamiento
  acordados;
- borradores sin efectos y conversión explícita a tareas completas;
- recibos Telegram autenticados, inmutables y aislados de `leda_app`, con secreto
  webhook obligatorio y específico del bot;
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
| Mensajería | Recibo autenticado e idempotente en T1, procesamiento recuperable en T2 y outbox en salida. |
| Confianza | Capacidades opacas, identidad derivada y cinco logins disjuntos; no protege frente al compromiso total del proceso Python. |
| Autoridad de salida | `leda_dispatcher` transporta outbox listo y registra resultado/incidente técnico; no decide contenido, destinatario ni hechos de dominio. |
| Registros | Conversación, auditoría autoritativa e incidentes técnicos tienen escritores y significado separados. |
| LLM | Interpreta y redacta; contratos y políticas controlan hechos y completitud. |
| Configuración | Packs gobernados, versionados, reconciliables y auditables. |
| Multi-tenant | RLS completo y pruebas negativas entre espacios. |
| Despliegue | VPS única para el canary; no microservicios. |

## Fuera de horizonte

No forman parte de la validación, el piloto ni el endurecimiento inicial: UI
administrativa completa, dashboard avanzado, calendarios externos, aprendizaje
persistente, motor genérico de workflows y microservicios.
