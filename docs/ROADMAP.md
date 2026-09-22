# Roadmap

Prisma es un producto multi-tenant (ver [`product/que-es-prisma.md`](product/que-es-prisma.md))
y este roadmap ordena el trabajo que falta para que el código lo sostenga.

El orden no son fases del proyecto: son unidades de trabajo con precondición y
criterio de cierre. Una unidad se cierra por su criterio, no por cantidad de tareas
completadas.

## Qué se aprovecha tal cual

Buena parte de lo construido sirve sin cambios para un producto multi-tenant. Esto no
se rehace.

| Activo | Por qué sirve |
|---|---|
| Aislamiento por `row level security` | 28 tablas con RLS forzado y política contra el espacio actual (`db/esquema.sql:1474-1492`). El aislamiento lo garantiza la base, no el cuidado de quien escribe la consulta. |
| Modelo de roles y membresías | Separa persona, membresía y autoridad; funciona igual para cualquier cliente. |
| Tablas de configuración por cliente | `area` y `rol` son datos con alcance de espacio (`db/esquema.sql:106,114`), no tipos enumerados. |
| Estado como proyección de eventos | `bloquear_estado_directo()` impide la escritura directa (`db/esquema.sql:1231`). Es exactamente lo que necesita una superficie de lectura. |
| Paquetes de configuración versionados | El importador es genérico por diseño (`src/prisma/importador.py:211`) y registra versión y hash. |
| `TransporteTelegram` como adaptador | Aislado detrás de una interfaz de envío (`src/prisma/despachador.py:66`), con doble de prueba equivalente. |
| Router tipado multiproveedor | Un validador cerrado compartido por todos los proveedores (`src/prisma/llm.py`). |
| Renderer único de salida | Normalización y medición centralizadas (`src/prisma/salida.py`). Se conserva; cambia dónde se aplica. |
| Escalera y cadencias como datos | Configurables por cliente, no codificadas. |

## Qué se corrige

| Defecto | Regla de la frontera que incumple |
|---|---|
| Las tablas de eventos de estado no tienen `workspace_id` ni RLS, y el disparador que proyecta el estado no valida el espacio | Regla 1 |
| `message_outbox` está atado a un transporte: tiene `chat_id` y no tiene columna de canal | Regla 2 |
| Un límite de tamaño de Telegram decide si un dato de negocio es válido | Regla 3 |
| No existe grafo de transiciones de estado: cualquier destino del tipo enumerado es aceptado | Regla 6 |

El detalle y la evidencia de cada uno están en
[`architecture/frontera.md`](architecture/frontera.md).

## Qué queda superado

Estos documentos se conservan como registro histórico. No describen el alcance
vigente y no deben usarse para decidir.

| Documento | Motivo |
|---|---|
| [`decisions/0003-authenticated-inbound-boundary.md`](decisions/0003-authenticated-inbound-boundary.md) | El modelo de amenaza cambió. Fue escrito para un asistente interno de un solo equipo, donde la amenaza principal era el compromiso de la credencial de aplicación. En un producto multi-tenant la amenaza principal es el cruce entre clientes. Su análisis de capacidades y credenciales conserva valor; su secuencia y su prioridad no. |
| [`phases/00-pilot-scope.md`](phases/00-pilot-scope.md) | Alcance de piloto local para un único equipo. |
| [`phases/01-local-pilot-foundations.md`](phases/01-local-pilot-foundations.md) | Fundaciones organizadas por unidades de piloto local, superadas por este orden de entrega. |
| [`product/functional-specification.md`](product/functional-specification.md) | Ya se proponía describir a Prisma con independencia de una empresa concreta, y esa intención sigue siendo correcta. Lo superado es su modelo: precede a la definición como producto multi-tenant, no distingue configuración de cliente frente a núcleo del producto y no trata el aislamiento entre clientes como garantía. Su descripción de comportamiento conserva valor como insumo, contrastada contra la frontera. |

Nada de esto se borra. La parte del inventario de autoridad de la decisión 0003 se
reutiliza al cerrar el aislamiento entre clientes.

## Orden de entrega

### Línea base versionada

**Entrega:** el trabajo acumulado queda registrado en un commit con historia
recuperable.

**Depende de:** nada.

**Cierre:** el árbol de trabajo está limpio y existe un punto al que volver antes de
refactorizar.

### Cierre del aislamiento entre clientes

**Entrega:** `workspace_id` y política de RLS en las tablas de eventos de estado;
propietario explícito para cada función `security definer`; verificación del
propietario efectivo en una instalación limpia.

**Depende de:** línea base versionada.

**Cierre:** una prueba demuestra que una conexión asociada a un espacio no puede
insertar un evento que referencie una tarea de otro espacio, ni observar por efecto
lateral que ese identificador existe.

### Base documental

**Entrega:** definición de producto, frontera y este roadmap.

**Depende de:** nada.

**Cierre:** un lector nuevo entiende qué es Prisma y dónde termina el núcleo sin
recurrir a documentación superada. *Unidad en curso.*

### Desacople del transporte

**Entrega:** `canal` y `destino` genéricos en `message_outbox` en lugar de `chat_id`;
los límites de tamaño y división se trasladan al adaptador de salida; las reglas de
negocio dejan de medir en unidades de un canal.

**Depende de:** línea base versionada y base documental.

**Cierre:** el núcleo puede encolar una notificación sin conocer el canal, y una
prueba demuestra que un dato de negocio válido deja de rechazarse por un límite de
transporte. Es la precondición de toda superficie que no sea conversacional.

### API de lectura

**Entrega:** consultas agregadas de objetivos, avance, tareas por estado y por
responsable, cumplimiento, bloqueos y carga, expuestas por el puerto de lectura.

**Depende de:** cierre del aislamiento y desacople del transporte.

**Cierre:** una superficie ajena al canal conversacional puede leer el estado
completo de un espacio, y sólo de ese espacio.

### Grafo de transiciones de estado

**Entrega:** transiciones válidas declaradas y aplicadas, con la autoridad requerida
para cada una.

**Depende de:** cierre del aislamiento.

**Cierre:** una transición inválida o sin autoridad falla, y la prueba lo demuestra
por cada par de estados.

### Ciclo de seguimiento operativo

**Entrega:** el ingreso crea y satisface solicitudes de respuesta pendientes, de modo
que la escalera afirme silencio sobre evidencia real.

**Depende de:** grafo de transiciones y desacople del transporte.

**Cierre:** un escenario con tiempo simulado demuestra envío, silencio, respuesta,
ausencia y escalamiento sobre solicitudes reales.

## Horizonte posterior

No se abordan hasta que las unidades anteriores estén cerradas, y cada uno requiere
su propia decisión:

- dashboard sobre la API de lectura;
- aplicación móvil;
- incorporación de un segundo cliente, con el proceso de alta que eso exija;
- capacidades de producción para operar en internet: cola de entrada, pool de
  conexiones, secreto obligatorio de webhook, observabilidad, respaldo y restauración.
