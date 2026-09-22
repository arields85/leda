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
| Lectura | Expone consultas agregadas del estado para cualquier superficie de lectura. Implementado en `src/prisma/lectura.py`; ninguna de sus funciones recibe el espacio, lo toman de la sesión. |
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

Esta tabla es el estado real, no el deseado. Dos de las seis reglas siguen
incumplidas hoy, y una es parcial.

| Regla | Estado | Evidencia |
|---|---|---|
| 1. Aislamiento entre clientes | **Cumplida** | Migración `0003`: ambas tablas de eventos llevan `workspace_id`, con RLS forzado y política de aislamiento. El valor lo deriva un disparador `before insert` desde la fila padre, con privilegios del llamador, de modo que una tarea de otro espacio y una inexistente fallan idéntico. Migración `0004`: las cuatro funciones `security definer` pertenecen a `prisma_owner`, que no inicia sesión, no tiene miembros y no saltea la RLS. Migración `0005`: `audit_log`, `incident` y `absence` quedan bajo política; el espacio de la auditoría lo fija la sesión, nunca quien escribe. |
| 2. El núcleo no conoce el transporte | **Incumplida** | `message_outbox` tiene `chat_id` y `telegram_message_id` y no tiene columna de canal (`db/esquema.sql:533,548`). |
| 3. Límites de transporte fuera del negocio | **Incumplida** | `telegram_utf16_units` (`src/prisma/salida.py:39`) se usa para decidir la validez de datos de negocio en `src/prisma/ingreso_tareas.py:532,547,554,1118`. |
| 4. Estado por eventos | **Cumplida** | `bloquear_estado_directo()` impide el `update` directo sobre la tarea (`db/esquema.sql:1231`); el estado es proyección. |
| 5. Configuración como dato versionado | **Cumplida** | `area` y `rol` son tablas con alcance de espacio (`db/esquema.sql:106,114`); el importador de paquetes es genérico (`src/prisma/importador.py:211`). |
| 6. Autoridad revalidada en la frontera | **Parcial** | Existe la resolución de identidad y autoridad (`src/prisma/autoridad.py`) y el límite dedicado de conversión. Falta el grafo de transiciones: `actualizar_estado` acepta cualquier destino del tipo enumerado sin validar que la transición sea legítima (`src/prisma/herramientas.py:464-491`). |

### Cómo se cerró la regla 1

El propietario efectivo de las funciones elevadas **se midió**, no se supuso: eran
propiedad de `postgres`, superusuario y `bypassrls`. Adentro de sus cuerpos la RLS
no aplicaba. Eso cierra el `PENDIENTE` que este documento registraba antes.

Al quitarles ese privilegio apareció una dependencia oculta: el disparador que
proyecta `task.estado` se apoyaba en saltear la RLS. La conexión administrativa no
define espacio alguno, así que su `update` pasó a no encontrar ninguna fila y a
fallar **en silencio**. Ahora se acota al espacio del propio evento, ya derivado, y
restaura el valor previo para no angostar el resto de la transacción.

Dos verificaciones sostienen la regla, ambas contra bases reales: el rechazo del
cruce con indistinguibilidad frente a un identificador inexistente, y la
convergencia entre instalación limpia y base migrada leyendo el catálogo efectivo.

Límite que se conserva: la propiedad se verifica sobre una base nueva dentro de un
clúster existente. Un ensayo sobre un clúster enteramente limpio sigue siendo una
comprobación más fuerte y está `PENDIENTE`.

`confirmar_borrador_tarea` todavía fija el espacio con el valor que recibe de quien
la llama. Está acotada a `prisma_gateway` y fuera del alcance de `prisma_app`, pero
es el patrón que la regla 6 rechaza; pertenece al ingreso autenticado, no a esta
regla.

## Cómo se usa esta frontera

Antes de escribir código nuevo, ubicarlo: ¿es núcleo, puerto o adaptador? Si una
corrección obliga a que el núcleo conozca un detalle de canal, la corrección está mal
ubicada.

Antes de aceptar un requisito de un cliente, aplicar la tabla de
[`product/que-es-prisma.md`](../product/que-es-prisma.md): ¿es configuración de ese
cliente o es núcleo del producto?
