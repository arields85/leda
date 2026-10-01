# Roadmap

Prisma es un producto multi-tenant (ver [`product/que-es-prisma.md`](product/que-es-prisma.md))
y este roadmap ordena el trabajo que falta para que el código lo sostenga.

El orden no son fases del proyecto: son unidades de trabajo con precondición y
criterio de cierre. Una unidad se cierra por su criterio, no por cantidad de tareas
completadas.

**La entrevista de alta se antepuso al tablero de cliente.** Dos razones. Sin ella,
cada cliente nuevo exige que alguien que conozca al equipo escriba un paquete a mano,
y eso no es un producto: es una instalación a medida. **Prisma no se puede vender dos
veces sin la entrevista.** Y además es la que define qué configuración existe —sus
ocho bloques son exactamente lo que el tablero debería dejar editar—, así que
construir el tablero antes sería adivinar esa lista.

## Qué se aprovecha tal cual

Buena parte de lo construido sirve sin cambios para un producto multi-tenant. Esto no
se rehace.

| Activo | Por qué sirve |
|---|---|
| Aislamiento por `row level security` | 34 tablas con RLS forzado y política contra el espacio actual (`db/esquema.sql:2104-2160`, recontadas el 2026-09-30). El aislamiento lo garantiza la base, no el cuidado de quien escribe la consulta. |
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

**Congelamiento de funcionalidad nueva (decisión del usuario, 2026-09-30).** No se
construye funcionalidad nueva hasta que el alta de tareas, la entrega con evidencia y la
aprobación cumplan en una prueba real los criterios del
[`ADR 0014`](decisions/0014-flujo-de-un-mensaje.md). Queda congelado: flujos nuevos (la
rama de correo verificado, Google y agenda del ADR 0010), capacidades nuevas en medio de
una ronda, el tablero y el panel. Sigue abierto: mejorar esos tres caminos, corregir
fallas reales y anotar ideas en este roadmap sin construirlas. Motivo: cada ronda
probaba superficie nueva y los hallazgos no bajaban; una función construida sobre una
conversación que todavía no funciona hereda sus problemas. Se levanta al cumplir los
criterios.

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

### Puerto de lectura — entregado

**Entregado** en `70685f3`: seis consultas agregadas en `src/prisma/lectura.py`
—avance de objetivos, tareas por estado, carga por persona, vencidas, bloqueos
abiertos y trabajo esperando aprobación—. Ninguna recibe el espacio: lo toman de la
sesión, y el aislamiento queda a cargo de la política.

**Su adaptador HTTP no existe**, así que todavía ninguna superficie ajena al canal
conversacional lee nada. Eso pertenece al tablero de cliente.

Nota sobre la dependencia que este roadmap declaraba: decía depender del desacople
del transporte, y no era cierto. `message_outbox` es la cola de notificaciones
empujadas a personas; un tablero no recibe notificaciones, lee estado. El desacople
habilita un segundo canal de notificación, no una superficie de lectura.

### Entrevista de alta de espacios

**Entrega:** la implementación de [`nucleo/alta-de-equipo.md`](../nucleo/alta-de-equipo.md),
hoy diseñado en detalle y sin una sola línea de código. Sus ocho bloques producen un
paquete de espacio que un administrador de plataforma lee y aprueba antes de activar.

**Depende de:** el panel de plataforma, que es donde vive.

**Cierre:** se da de alta un espacio nuevo sin que nadie escriba un paquete a mano, y
las validaciones del documento distinguen lo que impide activar de lo que sólo
advierte.

### Panel de plataforma

**Entrega:** la superficie que aloja la entrevista de alta y el alta de clientes, y
su autenticación. También la elección de proveedor y modelo de lenguaje: hoy se
fija por consola (`python -m prisma modelo <id> --proveedor <p>`, que escribe
`model_config`), y tiene que poder cambiarse desde el panel, con el cambio atribuido
en la auditoría. Va en el panel y no en el tablero de cliente porque el modelo
global alcanza a todos los espacios.

También la vista de incidentes (pedido del usuario, 2026-09-24): hoy cada falla
queda en la tabla `incident` (espacio, severidad, resumen sin datos sensibles, fecha)
y sólo se consulta por consola (`python -m prisma incidentes <espacio>`). El
administrador tiene que poder ver desde el panel dónde está fallando el sistema y qué
lo hizo fallar: enrutamiento, Jev caído o sin clave, errores del modelo, despacho.
Cada incidente apunta al mensaje que lo causó en lugar de copiar su texto: quien
tenga permiso llega desde el incidente a la conversación, y si esa conversación se
borró, el incidente conserva qué falló pero ya no muestra el texto. Así el texto vive
en un solo lugar, con un solo control de acceso y de borrado.

La retención y la visibilidad de las conversaciones pasan a ser configuración de
cada cliente (pedido del usuario, 2026-09-24): cuánto tiempo se guardan y quién puede
verlas lo decide quien contrata Prisma o administra el equipo. Hoy lo fija para el
piloto [`ADR 0002`](decisions/0002-pilot-llm-context-and-retention.md) (retención
indefinida hasta que un administrador autorizado borre; acceso y borrado restringidos
y auditados); el cambio requiere un ADR nuevo que la reemplace en ese punto.

`PENDIENTE` para ese punto:

- si el tablero de cada cliente muestra también sus propios incidentes, o sólo el
  panel de plataforma;
- dónde vive la clave de cada proveedor, hoy una única `PRISMA_LLM_API_KEY` en
  `.env` que se lee al arrancar el proceso;
- si el ajuste por espacio que `model_config` ya admite se expone, y en qué
  superficie.

**Depende de:** nada en el código; sí de una decisión abierta sobre cómo se autentica
quien opera Prisma. El enlace por Telegram no sirve acá: autentica contra una
membresía, y en el alta el espacio todavía no existe.

**Cierre:** quien opera Prisma entra, da de alta un espacio y lo activa.

### Tablero de cliente

**Entrega:** la superficie que consume el puerto de lectura y permite al cliente
ajustar su propia configuración, con cada cambio atribuido en la auditoría. Incluye
las cadencias del bloque 5 de la entrevista de alta (`nucleo/alta-de-equipo.md`):
qué días y a qué hora Prisma pide estado, el resumen grupal y el tope de mensajes
automáticos por persona. Un cambio de cadencia toma efecto sin reiniciar el proceso.

**Depende de:** puerto de lectura (hecho) y su credencial de acceso, cuya
implementación quedó en pausa sin comitear.

**Cierre:** un integrante abre su enlace, ve el estado de su espacio y sólo el suyo,
y un cambio de configuración queda registrado con su autor.

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

### Prisma orienta

**Entrega:** [`ADR 0007`](decisions/0007-prisma-orienta-no-charla.md): cada respuesta que
espera algo cierra con botones concretos y una salida; las listas de tareas son botones
y tocar una ofrece las acciones del diseño §4.6 que ya tienen herramienta. Tras la
tercera ronda por Telegram (2026-09-28), las cuatro reglas generales de la conversación
del [`ADR 0013`](decisions/0013-reglas-generales-de-la-conversacion.md) (pregunta pendiente
como contexto con una sola rama abierta, una respuesta visible por mensaje y toque, estado
real, toques con señal e idempotentes), implementadas el 2026-09-29, y la forma de las
respuestas (T10 de `odd/tasks/prisma-orienta.md`).

**Cierre:** la segunda sesión por Telegram real se hizo (2026-09-27) y la tercera
(2026-09-28) mostró que la conversación seguía perdiéndose; el cierre pasa a ser la
cuarta ronda (T11), que muestre menos preguntas innecesarias, ninguna respuesta vaga que
haya que interpretar y ninguna conversación con dos temas abiertos a la vez.

### Aportes sobre tareas

**Entrega:** texto, foto, video o archivo que una persona suma a una tarea con un motivo:
avisar un avance, sumar información a un bloqueo, devolver una revisión con
observaciones, responder un pedido de estado (diseño §4.6). Recibir archivos de
Telegram y guardarlos por referencia con verificación de integridad, sin interpretarlos;
un aporte no es evidencia. Incluye la transición de revisión a en curso al devolver y el
pedido de estado de Prisma al responsable, respetando el volumen de contacto (mecánica
§10).

**Depende de:** Prisma orienta.

### Aprendizaje de apodos y de aclaraciones

**Entrega:** Prisma aprende de lo que ya preguntó, para preguntar menos (pedido del
usuario, 2026-09-24). Dos partes: los apodos y el vocabulario del equipo ("tincho" es
Martín; "dashboard", "interfaz HMI" y "CoreLabs" son lo mismo), que ADR 0005 ya
decide aprender preguntando; y las aclaraciones de tareas: si una persona eligió
"Actualizar el dashboard de HMI" para "lo del dashboard" y lo confirmó, la próxima
vez esa referencia llega a Jev con ese dato.

Reglas propuestas, a fijar en un ADR que amplíe la excepción de ADR 0005 al
aprendizaje persistente:

- sólo se aprende de una elección confirmada en la vista previa, nunca de un toque
  suelto ni de una propuesta cancelada;
- lo aprendido es una pista para Jev, no una decisión: siguen la verificación, la
  pregunta por la segunda candidata y la vista previa;
- una aclaración aprendida vence cuando su tarea termina o se cancela, para no
  elegir con confianza una tarea vieja cuando aparece otra parecida;
- alcance por persona o por equipo según el caso;
- lo aprendido queda a la vista y se puede borrar, desde el panel cuando exista.

**Insumo a profundizar: Engram** (memoria persistente de gentle-ai,
[github.com/Gentleman-Programming/engram](https://github.com/Gentleman-Programming/engram),
MIT). Relevamiento inicial, 2026-09-24: binario Go con SQLite y búsqueda de texto
(FTS5), sin búsqueda por significado; la unidad es una observación tipada con
`topic_key` que actualiza en lugar de duplicar; resúmenes de sesión y veredictos
sobre conflictos entre observaciones. Es local y de un solo usuario por defecto,
separa por proyecto y no por cliente, y su modo multiusuario es una capa en la nube
aparte. Lectura inicial: usarlo como componente sumaría un segundo almacén y otro
modelo de aislamiento, frente a PostgreSQL como única fuente de verdad y RLS por
espacio; sus ideas (clave de tema con actualización, observaciones con tipo y
vencimiento, búsqueda de texto) se pueden llevar a PostgreSQL. `PENDIENTE`, a
profundizar antes del ADR de esta unidad: el modo en la nube y su control de acceso
por proyecto, cómo decide `mem_judge` los conflictos, y si conviene como
componente, como servicio aparte o sólo como referencia de diseño.

**Insumo: Hermes Agent** (Nous Research, MIT; relevamiento del 2026-09-30 en
[`research/hermes-agent.md`](research/hermes-agent.md)). No sirve como base: agente
personal, memoria en archivos y SQLite, aislamiento por perfil y no por espacio, y
aprende solo por defecto. Sí aporta el mecanismo de esta unidad: después de un turno en
el que la persona corrigió a Prisma, un paso aparte detecta qué se podría aprender (un
apodo, un sinónimo del equipo, la tarea a la que apuntaba una referencia) y lo
**propone**; se guarda sólo cuando alguien lo confirma, con las reglas de arriba. En el
flujo del [`ADR 0014`](decisions/0014-flujo-de-un-mensaje.md), lo aprendido vive en
PostgreSQL (etapa 1) y le llega a Jev como pista (etapa 3).

**Idea a investigar, no decidida: memoria por integrante** (propuesta del usuario,
2026-09-24, inspirada en los proyectos de Engram). Tratar la conversación de cada
integrante como un espacio de memoria propio, para que Prisma recuerde lo que habló
con esa persona. Es una hipótesis a evaluar, no una decisión de usar Engram ni de
construirla. Condiciones que la investigación tiene que respetar:

- memoria por persona dentro de su espacio, con RLS; lo que una persona le dijo a
  Prisma nunca aparece en la respuesta a otra;
- guarda lo que la base no tiene (lo conversado, preferencias, compromisos dichos al
  pasar, apodos y aclaraciones), nunca el estado de las tareas, que se lee en el
  momento: la memoria no reemplaza una lectura vigente;
- se guarda todo lo permitido, pero al modelo le llega sólo lo relacionado con cada
  mensaje (resúmenes por conversación y búsqueda), no el historial completo;
- retención y visibilidad según lo que decida cada cliente.

`PENDIENTE`: medir si mejora las respuestas frente al historial actual de 6 horas
(`contexto.historial`), y definirlo en el mismo ADR que amplíe la excepción de
ADR 0005.

**Insumo a profundizar: Obsidian** ([obsidian.md](https://obsidian.md)). Relevamiento
inicial, 2026-09-24: aplicación de escritorio sobre una carpeta de archivos Markdown
con enlaces, propiedades y extensiones; gratis también para uso comercial
([licencia](https://obsidian.md/license)). No tiene modo servidor ni permisos por
usuario: `obsidian-headless` (beta, 2026) sólo sincroniza con Obsidian Sync, y darle
memoria a un agente se hace con la extensión comunitaria Local REST API, que corre
dentro de la aplicación abierta, una carpeta por instancia. Lectura inicial: como
memoria del núcleo choca igual que Engram (segundo almacén, aislamiento por carpeta
y no por RLS, aplicación de escritorio en un servidor). Único uso con sentido: como
formato en el que un cliente redacte documentación de su proyecto y Prisma la lea
como archivos Markdown, sin la aplicación en el servidor. `PENDIENTE`: si existen
bóvedas compartidas con permisos, los términos de Sync y Publish para un servicio
con varios clientes, y si la extensión funciona sin entorno gráfico.

**Depende de:** aclaración con botones (entregada) y la sesión por Telegram real con
datos ficticios, que muestra qué dudas se repiten.

**Cierre:** medido con mensajes reales, las preguntas repetidas bajan sin ninguna
elección equivocada sin preguntar.

### Objetivo propuesto desde el alta

**Entrega:** cuando el trabajo que alguien pide no entra en el margen máximo de una
tarea (ajuste del espacio, 2 meses por omisión; decisión del usuario del 2026-10-01),
Prisma ofrece dos salidas y la persona elige: dividirlo en tareas dentro del objetivo
que ya existe, o proponer un objetivo nuevo, que se crea en estado `propuesto` y va a
aprobación según la política del espacio (mecánica §3 y §7) hasta quedar `activo`. Pedido
del usuario del 2026-10-01, anotado bajo el congelamiento. Corrige de paso una
diferencia con el núcleo: hoy `crear_objetivo` crea el objetivo directamente `activo`,
sin aprobación (`src/prisma/herramientas.py`, `_crear_objetivo`).

**Depende de:** el congelamiento levantado (alta, entrega y aprobación cumpliendo el ADR
0014) y el margen máximo de la fecha de una tarea (rama `feat/flujo-de-un-mensaje`).

**Cierre:** en una prueba real, un pedido de trabajo largo termina en tareas dentro del
margen o en un objetivo propuesto que la autoridad aprueba; ningún objetivo queda
`activo` sin esa aprobación.

## Horizonte posterior

No se abordan hasta que las unidades anteriores estén cerradas, y cada uno requiere
su propia decisión:

- aplicación móvil;
- exportación de la configuración de un espacio al formato de paquete, que es la
  portabilidad que pide el §17 del documento del primer cliente;
- capacidades de producción para operar en internet: cola de entrada, pool de
  conexiones, secreto obligatorio de webhook, observabilidad, respaldo y restauración.

La incorporación de un segundo cliente dejó de ser horizonte posterior: es
exactamente lo que habilitan la entrevista de alta y el panel de plataforma, ya
ordenados arriba.
