# Estado arquitectónico actual

Prisma es hoy un monolito modular en Python, con PostgreSQL como fuente operativa y
Telegram como interfaz principal. Esta descripción surge de inspección estática; la
baseline de ejecución permanece pendiente.

## Resumen implementado

```text
Telegram webhook o polling local
              |
              v
       gateway compartido
              |
       identidad + autoridad
              |
   contexto + proveedor de LLM
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
| Agente | Construye contexto de núcleo, espacio y momento; usa un proveedor de LLM detrás de una interfaz. |
| Efectos | El modelo solicita herramientas registradas; no escribe directamente en PostgreSQL. |
| Persistencia | SQL explícito con Psycopg, sin ORM. El esquema contiene reglas, funciones y triggers. |
| Estado | Tareas y objetivos proyectan eventos append-only. La escritura directa está bloqueada sólo para tareas. |
| Confirmación | Las acciones pendientes congelan herramienta y argumentos; las opciones de botón se resuelven atómicamente. |
| Salida | Los mensajes visibles se encolan con clave de deduplicación, reintentos, horario y límite de contacto. |
| Memoria | El turno carga una ventana reciente del chat; sólo considera salidas efectivamente enviadas. |
| Automatización | APScheduler monta cadencias y escalera en modo servidor; el polling local ejecuta escalera y despacho. |
| Configuración | Packs YAML importan equipo, autoridad, cadencias, rutas, glosario y ajustes; se registra versión y hash. |
| Aislamiento | `prisma_app` usa RLS por `workspace_id`; `prisma_admin` se reserva para importación y consola. |

## Reglas comprobadas por lectura

- Las tareas requieren un objetivo y un área en el esquema.
- El responsable, la fecha y el criterio de aceptación todavía pueden ser nulos.
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
| Tareas huérfanas | `responsable_membership_id` es opcional y la herramienta permite crear sin responsable. |
| Compromiso incompleto | Fecha, criterio y política de evidencia no son obligatorios al crear una tarea. |
| Estados sin grafo | Se registran eventos, pero no existe validación general de transiciones permitidas. |
| Estado de objetivo mutable | El trigger que bloquea escritura directa existe para `task`, no para `objective`. |
| Evidencia no materializada | La tarea tiene `evidencia_requerida`, pero la creación no la carga desde una política del pack. |
| Respuestas pendientes incompletas | Existe `pending_reply` y la escalera la actualiza, pero el inbound no crea ni satisface el ciclo operativo. |
| Afirmación de silencio no sustentada | La escalera dice “sin respuesta” sin comprobar una solicitud pendiente vigente y su respuesta posterior. |
| Cadencias locales manuales | El loop local corre escalera y despacho; las cadencias sólo se disparan mediante comando explícito. |
| Reimportación parcial | El upsert de workspace no reconcilia `activo` ni `grupo_chat_id`; varias colecciones se reemplazan y otras sólo se agregan/actualizan. |
| RLS incompleto | La lista de tablas protegidas no incluye todas las tablas con alcance de espacio, eventos o auditoría. |
| Webhook opcionalmente inseguro | El secreto sólo se valida cuando está configurado; vacío deja la ruta sin esa verificación. |
| Conexión no preparada para carga | El gateway conserva una única conexión, sin pool ni worker de entrada separado. |

## Riesgos inferidos o por verificar

- La experiencia del piloto puede generar omisiones o conclusiones variables porque
  todavía no hay contratos tipados de respuesta para intenciones operativas.
- La cobertura real de aislamiento, concurrencia y reimportación debe confirmarse
  ejecutando pruebas específicas contra PostgreSQL.
- El registro automático de webhooks al desplegar no se observa conectado al comando
  de servidor; debe verificarse el procedimiento operativo antes de VPS.
- La suite y los comandos de puesta en marcha pueden haber derivado respecto de la
  documentación. La baseline está marcada como pendiente en `STATUS.md`.

## Límites de esta descripción

No se inspeccionaron secretos ni archivos `.env*`. No se ejecutó la aplicación, la
base, Telegram ni la suite durante esta tarea documental.
