# Estado arquitectónico actual

> **Nota del 2026-10-04.** Este documento describe el código de `main`. Su capa de
> conversación (los flujos A y B) está congelada: no se corrige ni se extiende, y se borra en
> la Etapa 3 del Motor. La capa de garantías que describe sigue vigente. No es la base para
> diseñar la conversación nueva: eso se decide en el ADR 0018 (`PENDIENTE`). Estado y orden
> de trabajo: [`../STATUS.md`](../STATUS.md).

Leda es hoy un monolito modular en Python, con PostgreSQL como fuente operativa y
Telegram como interfaz principal. Esta descripción contrasta inspección estática con
la evidencia operativa y la baseline registradas en `docs/STATUS.md`.

## Resumen implementado

```text
Telegram webhook o polling local
              |
              v
       gateway compartido
              |
       identidad + autoridad
              |
   estado exacto o router tipado
              |
   agente ordinario si corresponde
              |
    herramientas autorizadas
              |
          PostgreSQL
              |
       message_outbox
              |
      despachador Telegram
```

| Área | Implementación observada |
|---|---|
| Entrada | FastAPI recibe webhooks; el modo local usa `getUpdates`. Ambos llaman al mismo procesamiento. |
| Identidad y autoridad | El canal fija el espacio; la autoridad se valida en servidor y nuevamente al ejecutar acciones pendientes. |
| Routing | Sin un paso conversacional exacto ya activo, todos los adaptadores atraviesan el mismo validador cerrado: una llamada a `route_intent`, cero contenido lateral, argumentos objeto y acción enumerada. La creación abre el ledger directamente; sólo `normal_conversation` entra al agente ordinario. |
| Agente | Construye contexto de núcleo, espacio y momento; usa un proveedor de LLM detrás de una interfaz. |
| Efectos | El modelo solicita herramientas registradas; no escribe directamente en PostgreSQL. |
| Persistencia | SQL explícito con Psycopg, sin ORM. El esquema contiene reglas, funciones y triggers. |
| Estado | Tareas y objetivos proyectan eventos append-only. La escritura directa está bloqueada sólo para tareas; el límite de dominio acordado para 1B.1 todavía no está implementado. |
| Confirmación | Las acciones pendientes congelan herramienta y argumentos; las opciones de botón se resuelven atómicamente. |
| Intake de tareas | Un ledger server-owned limita un request activo por espacio, membresía y chat privado; campos, candidatos paginados, slots libres, preview acotada y resultados terminales son persistidos. Una búsqueda sin coincidencias sigue mostrando candidatos vigentes y `Otra opción`; un conjunto vacío sólo permite cancelar. La conversión final sigue en Unidad 1A y valida actor, espacio, token y chat. |
| Salida | Un renderer/validador común normaliza y mide UTF-16 sin reemplazar vocabulario legítimo antes de encolar y al transportar. Mensajes con botones usan un margen indivisible de 3900; informativos sin botones pueden dividirse determinísticamente hasta 4096 con dedupe por parte. El estado server-owned de no-efecto se agrega sólo cuando corresponde y se deduplica semánticamente. PostgreSQL impide cualquier fila fuera del contrato. |
| Memoria | El turno carga una ventana reciente del chat; sólo considera salidas efectivamente enviadas. |
| Automatización | APScheduler monta cadencias y escalera en modo servidor; el polling local ejecuta escalera y despacho. |
| Configuración | Packs YAML importan equipo, autoridad, cadencias, rutas, glosario y ajustes; se registra versión y hash. |
| Aislamiento | `leda_app` usa RLS por `workspace_id`; `leda_admin` se reserva para importación y consola. |

La separación objetivo en cinco credenciales técnicas todavía no existe. En
particular, no existe el rol dedicado `leda_dispatcher`; el gateway actual no debe
interpretarse como autoridad general más allá del límite ya implementado de Unidad 1A.

## Reglas comprobadas por lectura

- Las tareas requieren un objetivo y un área en el esquema.
- En la tabla `task`, responsable, fecha y criterio de aceptación conservan
  anulabilidad física. Eso no define el contrato operativo: Unidad 1A obliga a que una
  tarea comprometida tenga objetivo, responsable, fecha, criterio de aceptación y
  política de evidencia, y la conversión desde `task_draft` revalida esos datos.
- Unidad 1A materializa la política de evidencia como snapshot y `leda_app` no tiene
  `INSERT` directo sobre `task`; el acceso administrativo residual no equivale a una
  ruta operativa autorizada.
- El cierre consulta criterio, evidencia configurada, bloqueos, dependencias y
  aprobación aplicable.
- Las acciones pendientes vencen y sólo su destinatario puede resolverlas.
- Dos resoluciones compiten por la misma fila y una sola cambia el estado.
- Outbox evita duplicados por una clave única.
- La conversación no escribe fuera del catálogo de herramientas.

## Riesgos comprobados

Estos huecos se observan directamente en el código o esquema actual:

| Riesgo | Evidencia estática |
|---|---|
| Inbound duplicable | `inbound_message.telegram_message_id` no tiene restricción única y la inserción no maneja conflicto. |
| Validación pendiente del ingreso de tareas | El segundo smoke probó que el agente podía omitir la herramienta sugerida. El contrato común del router, el bypass de estado activo, los botones y la copia visible pasan su foco local, pero requieren revisión final antes de cualquier replay o Telegram real. |
| Ciclo de tarea sin límite de dominio | `actualizar_estado` todavía admite selección manual de estado y no aplica el grafo ni la autoridad acordados para 1B.1. |
| Estado de objetivo sin límite simétrico | `objective_state_event` conserva el mecanismo previo; su grafo pertenece a otra porción de 1B. |
| Estado de objetivo mutable | El trigger que bloquea escritura directa existe para `task`, no para `objective`. |
| Respuestas pendientes incompletas | Existe `pending_reply` y la escalera la actualiza, pero el inbound no crea ni satisface el ciclo operativo. |
| Afirmación de silencio no sustentada | La escalera dice “sin respuesta” sin comprobar una solicitud pendiente vigente y su respuesta posterior. |
| Cadencias locales manuales | El loop local corre escalera y despacho; las cadencias sólo se disparan mediante comando explícito. |
| Reimportación parcial | El upsert de workspace no reconcilia `activo` ni `grupo_chat_id`; varias colecciones se reemplazan y otras sólo se agregan/actualizan. |
| RLS incompleto | La lista de tablas protegidas no incluye todas las tablas con alcance de espacio, eventos o auditoría. |
| Webhook opcionalmente inseguro | El secreto sólo se valida cuando está configurado; vacío deja la ruta sin esa verificación. |
| Conexión no preparada para carga | El gateway conserva una única conexión, sin pool ni worker de entrada separado. |
| Superficie DML legacy amplia | El análisis estático identifica 26 tablas directamente mutables por `leda_app`; además, insertar eventos puede mutar indirectamente la proyección de tarea. El número no incluye funciones, secuencias, owners ni herencia. |
| ACL implícita de funciones | La disponibilidad potencial de `EXECUTE` mediante `PUBLIC` impide tratar los revokes nominales de tablas como cierre exhaustivo. |
| Riesgo de superusuario compartido | La topología Docker declarada puede compartir una credencial con capacidad de superusuario entre caminos; los roles lógicos no aíslan una sesión que pueda asumirlos o eludirlos. |
| Registros con autoridad mezclable | La aplicación actual puede escribir conversación, auditoría e incidentes sin la separación objetivo que reserva auditoría autoritativa a T2b, gateway o administración identificada. |

Estos cuatro hallazgos son conclusiones de inspección estática del repositorio. No
demuestran los grants, membresías, owners, atributos ni credenciales efectivamente
activos en producción; ese catálogo requiere el Corte 0 verificable de ADR 0003.

## Riesgos inferidos o por verificar

- La experiencia del piloto puede generar omisiones o conclusiones variables porque
  todavía no hay contratos tipados de respuesta para intenciones operativas.
- La cobertura real de aislamiento, concurrencia y reimportación debe confirmarse
  ejecutando pruebas específicas contra PostgreSQL.
- El registro automático de webhooks al desplegar no se observa conectado al comando
  de servidor; debe verificarse el procedimiento operativo antes de VPS.
- La baseline registrada después de Unidad 1A pasó, pero el contrato posterior de
  Unidad 1B.1 no está implementado y requiere sus propias pruebas de grafo, autoridad,
  bypass y concurrencia.
- El inbound histórico carece de la raíz autenticada futura. Su conservación como
  conversación legacy no permite promoverlo, reintentarlo ni derivar efectos.

## Límites de esta descripción

No se inspeccionaron secretos ni archivos `.env*` manualmente. Las pruebas registradas
en `docs/STATUS.md` usaron el fixture efímero existente; no se accedió a la base
operativa, Telegram ni Docker.
