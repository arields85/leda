# La frontera

Este documento define dónde termina el núcleo de Prisma y dónde empiezan sus
adaptadores. Gobierna a los demás documentos de arquitectura: ante una discrepancia,
prevalece esta frontera.

## Por qué existe

Sin una frontera declarada, cada falla operativa empuja la lógica hacia donde
resulta más fácil escribirla. Eso ya ocurrió en este proyecto.

Dos ejercicios progresivos fallaron porque el modelo no iniciaba de forma confiable
el circuito de creación de tareas. En ambos casos la corrección movió autoridad hacia
el servidor. El resultado acumulado es que `src/prisma/ingreso_tareas.py` tiene 1218
líneas, más que `src/prisma/agente.py` (290) y `src/prisma/herramientas.py` (573)
sumados.

Cada una de esas correcciones fue técnicamente razonable. Ninguna fue una decisión
de arquitectura tomada de frente. La frontera existe para que la próxima corrección
tenga un lugar declarado al que pertenecer.

## Mapa

```text
        ┌─────────────────────────────────────────────────┐
        │                  ADAPTADORES                    │
        │                                                 │
        │   Telegram    HTTP lectura    Móvil    Packs    │
        │   Proveedores LLM                               │
        └────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────────────────────────────────────┐
        │                    PUERTOS                      │
        │                                                 │
        │  Intención   Notificación   Lectura             │
        │  Configuración   Razonamiento                   │
        └────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────────────────────────────────────┐
        │                     NÚCLEO                      │
        │                                                 │
        │  Objetivos e hitos      Autoridad y membresías  │
        │  Tareas y estados       Seguimiento             │
        │  Dependencias           Cadencias               │
        │  Bloqueos               Evidencias              │
        │  Aprobaciones           Auditoría               │
        └─────────────────────────────────────────────────┘
```

## Núcleo de dominio

El núcleo contiene el modelo de gestión de proyectos y las reglas que lo hacen
confiable:

- objetivos, hitos y objetivos operativos;
- tareas, y su estado como **proyección de eventos**, nunca como campo editable;
- dependencias entre trabajos y entre áreas;
- bloqueos, con causa, impacto y antigüedad;
- evidencias y aprobaciones;
- autoridad, membresías y revalidación de permisos;
- el ciclo de seguimiento y la escalera de recordatorios;
- las cadencias y el calendario laboral.

**Regla del núcleo:** no sabe qué es Telegram. No conoce un `chat_id`, un botón, un
límite de caracteres ni un identificador de mensaje de un canal concreto. Si el
núcleo necesita avisarle algo a una persona, expresa *a quién* y *qué*, nunca *por
dónde* ni *con qué formato*.

## Puertos

Un puerto es un contrato que el núcleo define y un adaptador implementa.

| Puerto | Contrato |
|---|---|
| Intención | Recibe la intención de una persona ya identificada y autorizada, sin formato de canal. |
| Notificación | Entrega un mensaje dirigido a una persona, sin conocer su transporte. |
| Lectura | Expone consultas agregadas del estado para cualquier superficie de lectura. |
| Configuración | Carga el paquete versionado de un cliente y lo materializa en el modelo. |
| Razonamiento | Interpreta lenguaje natural y devuelve salida tipada y validada. |

## Adaptadores

| Adaptador | Estado | Evidencia |
|---|---|---|
| Telegram | Existe | `src/prisma/despachador.py:66` |
| Proveedores LLM | Existen | `src/prisma/llm.py` |
| Importador de paquetes | Existe | `src/prisma/importador.py:211` |
| HTTP de lectura | No existe | Sólo hay webhook y salud en `src/prisma/gateway.py:47,434` |
| Aplicación móvil | No existe | — |

El adaptador de Telegram está bien construido: `TransporteTelegram` queda aislado
detrás de una interfaz de envío y tiene un doble de prueba equivalente. El problema
no es el adaptador, es que el núcleo lo conoce.

## Reglas invariantes

1. **El aislamiento entre clientes es la invariante número uno.** Toda tabla con
   alcance de espacio lleva `workspace_id`, tiene `row level security` forzado y una
   política de aislamiento. Ninguna función `security definer` queda sin propietario
   explícito y verificado.
2. **El núcleo no conoce el transporte.** Ningún identificador propio de un canal
   cruza hacia el dominio ni hacia el modelo de datos de dominio.
3. **Ningún límite de transporte decide la validez de un dato de negocio.** Los
   límites de tamaño, formato y división pertenecen al adaptador de salida.
4. **El estado se escribe por eventos.** Nunca por `update` directo sobre la
   proyección.
5. **La configuración del cliente es dato versionado.** Nunca código, nunca tipo
   enumerado, nunca constante.
6. **La autoridad se revalida en la frontera.** Nunca se confía en el actor, el
   espacio ni el permiso que declare el llamador.

## Cumplimiento actual

Esta tabla es el estado real, no el deseado. Tres de las seis reglas están
incumplidas hoy.

| Regla | Estado | Evidencia |
|---|---|---|
| 1. Aislamiento entre clientes | **Incumplida** | `task_state_event` y `objective_state_event` no tienen `workspace_id` (`db/esquema.sql:413-422,426-435`), no figuran en el arreglo de tablas con RLS (`db/esquema.sql:1474-1482`) y sin embargo reciben `grant insert` para `prisma_app` (`db/esquema.sql:1542`). El disparador `aplicar_evento_tarea()` es `security definer` y actualiza la proyección sin validar el espacio (`db/esquema.sql:1215-1225`). Además, el esquema versionado no contiene ninguna sentencia `alter ... owner to`, por lo que el propietario de esas funciones queda determinado por quien ejecute el esquema. |
| 2. El núcleo no conoce el transporte | **Incumplida** | `message_outbox` tiene `chat_id` y `telegram_message_id` y no tiene columna de canal (`db/esquema.sql:533,548`). |
| 3. Límites de transporte fuera del negocio | **Incumplida** | `telegram_utf16_units` (`src/prisma/salida.py:39`) se usa para decidir la validez de datos de negocio en `src/prisma/ingreso_tareas.py:532,547,554,1118`. |
| 4. Estado por eventos | **Cumplida** | `bloquear_estado_directo()` impide el `update` directo sobre la tarea (`db/esquema.sql:1231`); el estado es proyección. |
| 5. Configuración como dato versionado | **Cumplida** | `area` y `rol` son tablas con alcance de espacio (`db/esquema.sql:106,114`); el importador de paquetes es genérico (`src/prisma/importador.py:211`). |
| 6. Autoridad revalidada en la frontera | **Parcial** | Existe la resolución de identidad y autoridad (`src/prisma/autoridad.py`) y el límite dedicado de conversión. Falta el grafo de transiciones: `actualizar_estado` acepta cualquier destino del tipo enumerado sin validar que la transición sea legítima (`src/prisma/herramientas.py:464-491`). |

### Consecuencia de la regla 1 incumplida

Una conexión asociada a un espacio puede insertar un evento de estado que referencia
una tarea de otro espacio. La restricción de clave foránea confirma la existencia de
esa tarea, de modo que el incumplimiento habilita además la enumeración de
identificadores ajenos.

El alcance exacto de la mutación depende del propietario efectivo de las funciones
`security definer` en cada instalación, que el esquema versionado no fija. Esa
verificación es parte del trabajo de cierre del aislamiento descrito en
[`ROADMAP.md`](../ROADMAP.md).

## Cómo se usa esta frontera

Antes de escribir código nuevo, ubicarlo: ¿es núcleo, puerto o adaptador? Si una
corrección obliga a que el núcleo conozca un detalle de canal, la corrección está mal
ubicada.

Antes de aceptar un requisito de un cliente, aplicar la tabla de
[`product/que-es-prisma.md`](../product/que-es-prisma.md): ¿es configuración de ese
cliente o es núcleo del producto?
