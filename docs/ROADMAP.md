# Roadmap

> **Nota del 2026-10-04.** El usuario cambió el rumbo de la conversación de Leda con una línea de
> trabajo que llama **el Motor** (definición en [`../AGENTS.md`](../AGENTS.md), "Nombres que
> usamos"): los flujos A, B y C quedaron congelados, se construye un motor chico de conversación y
> el alcance se recorta al seguimiento (por ahora Leda no crea tareas ni objetivos por chat). Este
> roadmap conserva sus unidades, pero **su orden y el criterio del congelamiento los fija el
> [ADR 0017](decisions/0017-por-chat-los-hechos-por-la-web-la-estructura.md), decisión 5**
> ("Criterio y orden vigentes", abajo). El orden de trabajo del día es el de
> [`STATUS.md`](STATUS.md), "Próximo paso", y ninguna unidad de abajo se empieza por su cuenta.

Leda es un producto multi-tenant (ver [`product/que-es-leda.md`](product/que-es-leda.md))
y este roadmap ordena el trabajo que falta para que el código lo sostenga.

El orden no son fases del proyecto: son unidades de trabajo con precondición y
criterio de cierre. Una unidad se cierra por su criterio, no por cantidad de tareas
completadas.

*Orden anterior al Motor, que ya no rige (lo reemplaza el ADR 0017, decisión 5):* **la entrevista
de alta se antepuso al tablero de cliente.** Dos razones. Sin ella,
cada cliente nuevo exige que alguien que conozca al equipo escriba un paquete a mano,
y eso no es un producto: es una instalación a medida. **Leda no se puede vender dos
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
| Paquetes de configuración versionados | El importador es genérico por diseño (`src/leda/importador.py:211`) y registra versión y hash. |
| `TransporteTelegram` como adaptador | Aislado detrás de una interfaz de envío (`src/leda/despachador.py:66`), con doble de prueba equivalente. |
| Router tipado multiproveedor | Un validador cerrado compartido por todos los proveedores (`src/leda/llm.py`). |
| Renderer único de salida | Normalización y medición centralizadas (`src/leda/salida.py`). Se conserva; cambia dónde se aplica. |
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
| [`product/functional-specification.md`](product/functional-specification.md) | Ya se proponía describir a Leda con independencia de una empresa concreta, y esa intención sigue siendo correcta. Lo superado es su modelo: precede a la definición como producto multi-tenant, no distingue configuración de cliente frente a núcleo del producto y no trata el aislamiento entre clientes como garantía. Su descripción de comportamiento conserva valor como insumo, contrastada contra la frontera. |

Nada de esto se borra. La parte del inventario de autoridad de la decisión 0003 se
reutiliza al cerrar el aislamiento entre clientes.

## Orden de entrega

### Criterio y orden vigentes (ADR 0017, decisión 5, aceptada el 2026-10-04)

- **Se construyen dos cosas:** el seguimiento por chat (las ocho cosas de la decisión 3b, con las
  cuatro piezas que le faltan, decisión 6) y la plataforma web de tareas.
- **La plataforma lleva su propio ADR antes del código:** quién entra, cómo se identifica, qué ve
  y qué puede hacer cada uno, y cómo se cumplen el aislamiento entre espacios y la auditoría en una
  superficie web que escribe en la base. Se descartó cargar tareas con una planilla y un comando.
- **Todo lo demás espera** hasta que Leda haga bien el seguimiento en pruebas reales por
  Telegram, con los criterios de la prueba del [ADR 0018](decisions/0018-motor-de-conversacion.md)
  (decisión 5b). Va a "Anotado para más adelante", abajo; su orden se decide al llegar a ese
  punto.
- **La prueba chica de la Etapa 2 no espera a la plataforma:** usa tareas ficticias cargadas con
  `sembrar`.
- El código de conversación sigue la regla de `AGENTS.md`: nada sin su diseño aceptado, y el motor
  de conversación definitivo recién en la Etapa 3.

Etapas y criterios de paso a `main` (M1 a M3): [`STATUS.md`](STATUS.md), "Próximo paso".

### Anotado para más adelante

Lo que se pide de pasada desde el Motor; se retoma cuando Leda haga bien el seguimiento en pruebas
reales. Las unidades de abajo que no son el seguimiento ni la plataforma también esperan.

| Capacidad | Origen |
|---|---|
| Leda le pasa el pedido de una tarea nueva a quien la carga, con confirmación de quien pide | ADR 0017, decisión 1 (se reevalúa si una prueba real muestra que los pedidos se pierden) |
| Quien decide las tareas las acepta dentro de Leda, en el formulario web; nunca por chat | ADR 0017, decisión 2 |
| Leda le pregunta al referente si acepta una fecha nueva y, si confirma, la cambia ella misma | ADR 0017, decisión 4 (pedido explícito del usuario) |
| Delegar por chat. Un referente le pasa una tarea a un integrante de su sector; Leda le pregunta a ese integrante si la acepta y le avisa a quien delegó cuando aceptó. Ejemplo: Marcos le pasa "Revisar comunicaciones" a Nahuel, que está a su cargo. | Usuario, 2026-10-07, a partir de la prueba por Telegram de la E2-9. Cambia la decisión 2 del ADR 0017 (reasignar queda fuera del chat): lleva su enmienda antes del código. Un cambio de responsable exige confirmación humana (constitución §7) y cruza el umbral de re-aprobación (mecánica §7). Decidido por el usuario (2026-10-07):
<br>(1) decide quien manda sobre el que recibe. Un referente le delega a su gente, y el que recibe confirma que la toma. Un par le delega a la gente de otro par, y decide ese par: Marcos le pasa una tarea a Lucas, decide Martín y, si acepta, Leda avisa a Marcos y a Lucas.
<br>(2) si no acepta, la tarea sigue con quien la tenía y Leda se lo dice.
<br>(3) el trabajo lo aprueba el aprobador de la tarea original.
<br>`PENDIENTE`, para verlo más adelante: si el referente original (Ismael) tiene que intervenir. La mecánica §7 pide re-aprobación ante un cambio de responsable. El usuario no quiere que la delegación dependa de que Ismael toque algo. |

### Antecedentes

**Congelamiento de funcionalidad nueva (decisión del usuario, 2026-09-30; reemplazado el
2026-10-04 por el ADR 0017, decisión 5).** No se construía funcionalidad nueva ni código de
conversación. Quedaba congelado: flujos nuevos (la rama de correo verificado, Google y agenda del
ADR 0010), capacidades nuevas en medio de una ronda, el tablero y el panel. Lo único que se podía
hacer con una idea nueva era anotarla en este roadmap, sin construirla. Motivo original: cada
ronda probaba superficie nueva y los hallazgos no bajaban; una función construida sobre una
conversación que todavía no funciona hereda sus problemas.

*Historia del criterio, que ya no rige.* Del 2026-09-30 al 2026-10-04, el congelamiento se
levantaba cuando el alta de tareas, la entrega con evidencia y la aprobación cumplieran en una
prueba real los criterios del [`ADR 0014`](decisions/0014-flujo-de-un-mensaje.md), y mientras
tanto se permitía mejorar esos tres caminos y corregir sus fallas. Una precisión del usuario del
2026-10-02 lo ataba a los circuitos 0, 1 y 2 de `odd/tasks/circuitos-al-flujo-nuevo.md`, en la
rama de flujo, sin esperar a la prueba final con alguien que no conociera el guion. El 2026-10-04
el alta por chat salió del alcance y esos caminos quedaron congelados: ya no se mejoran ni se
corrigen, y ese criterio dejó de describir cómo se levanta el congelamiento.

**El Motor: recorte de alcance y motor de conversación (decisión del usuario, 2026-10-04).** Por
ahora Leda no crea tareas ni objetivos por chat: hace seguimiento. Principio: *por chat, hechos
del trabajo; por la web, su estructura.* El cimiento de la conversación pasa a ser un motor chico
dentro de Leda, sin marcos de terceros. El usuario llama **el Motor** a toda esta línea de
trabajo. Las decisiones quedaron escritas en el paso M1: el ADR 0017 (alcance, aceptado) fija las
ocho cosas por chat (decisión 3b) y que las tareas las carga el administrador con un formulario en
la plataforma web (decisiones 2 y 5; se descartó la importación por archivo que se había pensado
primero); el ADR 0018 (motor de conversación, aceptado el 2026-10-06 después de la prueba chica)
fija cómo se procesa cada mensaje. Evidencia y razones:
[`research/gestion-del-dialogo-y-arquitecturas-de-agentes.md`](research/gestion-del-dialogo-y-arquitecturas-de-agentes.md).

**Alta con correo verificado y Google (ADR 0010): se integra a `main` y continúa desde ahí**
(decisión del usuario, 2026-10-02). El trabajo avanzado de la rama `auxiliar/alta-y-google`
se integra a `main` con el procedimiento R12 de
[`../odd/tasks/renombre-a-leda.md`](../odd/tasks/renombre-a-leda.md), que incluye primero el
renombre a Leda. Desde ahí se continúa en `main`, no en una rama aparte. Es una tarea
pendiente: su construcción espera bajo el criterio vigente (ADR 0017, decisión 5), y el momento
lo decide el usuario. **Desde el 2026-10-04 no se retoma** antes del paso M3 del Motor, salvo decisión del
usuario.

**Idea anotada, congelada (decisión del usuario, 2026-10-04): reemplazar una tarea por otra
más urgente.** Cuando quien confirma toca "Rechazar y cancelar" sobre el borrador de otra
persona, Leda le ofrece en la misma respuesta armarle otra tarea a esa persona (alta normal
con ese responsable, sus datos completos y su confirmación). No se edita la tarea cancelada:
son dos actos separados, para que la auditoría muestre qué se canceló, por qué y qué se creó
en su lugar. Pertenece al alta por chat, que ese mismo día quedó fuera del alcance: "Rechazar y
cancelar" se empezó a construir (tarea 0-36 de la rama de flujo), se detuvo y no se retoma; su
trabajo parcial quedó archivado, sólo para consulta, en la etiqueta `respaldo-0-36-en-pausa`. La
idea queda anotada. El ADR 0017 (decisiones 1 y 2) sacó del chat la creación de tareas y no
prevé que vuelva: si volviera, por decisión del usuario, la idea se reevalúa con ella.

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

**Cierre:** un lector nuevo entiende qué es Leda y dónde termina el núcleo sin
recurrir a documentación superada.

**Nota (2026-10-04):** esta unidad figuraba como la que estaba en marcha. Ya no lo está: el
trabajo vigente es el Motor. La definición de producto, la frontera y este roadmap se
actualizaron con los ADR 0017 y 0018 después del paso M1 (tarea E1-4 del Motor).

### Desacople del transporte

**Entrega:** `canal` y `destino` genéricos en `message_outbox` en lugar de `chat_id`;
los límites de tamaño y división se trasladan al adaptador de salida; las reglas de
negocio dejan de medir en unidades de un canal.

**Depende de:** línea base versionada y base documental.

**Cierre:** el núcleo puede encolar una notificación sin conocer el canal, y una
prueba demuestra que un dato de negocio válido deja de rechazarse por un límite de
transporte. Es la precondición de toda superficie que no sea conversacional.

### Puerto de lectura — entregado

**Entregado** en `70685f3`: seis consultas agregadas en `src/leda/lectura.py`
—avance de objetivos, tareas por estado, carga por persona, vencidas, bloqueos
abiertos y trabajo esperando aprobación—. Ninguna recibe el espacio: lo toman de la
sesión, y el aislamiento queda a cargo de la política.

**Su adaptador HTTP no existe**, así que todavía ninguna superficie ajena al canal
conversacional lee nada. Eso pertenece al tablero de cliente.

**Nota (2026-10-04):** el párrafo de arriba quedó atrasado. Desde el commit `48da6fb` existe
`GET /tablero/{token}` (`src/leda/gateway.py`, `_servir_tablero`), una vista de sólo lectura que
arma su página con las seis consultas de este puerto. No existe una API de lectura para otras
superficies.

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

**Nota (2026-10-04):** espera. La entrevista por chat no aplica en esta etapa y los integrantes
se gestionan desde la plataforma web de tareas (ADR 0017, decisiones 5 y 7).

### Panel de plataforma

**Entrega:** la superficie que aloja la entrevista de alta y el alta de clientes, y
su autenticación. También la elección de proveedor y modelo de lenguaje: hoy se
fija por consola (`python -m leda modelo <id> --proveedor <p>`, que escribe
`model_config`), y tiene que poder cambiarse desde el panel, con el cambio atribuido
en la auditoría. Va en el panel y no en el tablero de cliente porque el modelo
global alcanza a todos los espacios.

También la vista de incidentes (pedido del usuario, 2026-09-24): hoy cada falla
queda en la tabla `incident` (espacio, severidad, resumen sin datos sensibles, fecha)
y sólo se consulta por consola (`python -m leda incidentes <espacio>`). El
administrador tiene que poder ver desde el panel dónde está fallando el sistema y qué
lo hizo fallar: enrutamiento, Jev caído o sin clave, errores del modelo, despacho.
Cada incidente apunta al mensaje que lo causó en lugar de copiar su texto: quien
tenga permiso llega desde el incidente a la conversación, y si esa conversación se
borró, el incidente conserva qué falló pero ya no muestra el texto. Así el texto vive
en un solo lugar, con un solo control de acceso y de borrado.

La retención y la visibilidad de las conversaciones pasan a ser configuración de
cada cliente (pedido del usuario, 2026-09-24): cuánto tiempo se guardan y quién puede
verlas lo decide quien contrata Leda o administra el equipo. Hoy lo fija para el
piloto [`ADR 0002`](decisions/0002-pilot-llm-context-and-retention.md) (retención
indefinida hasta que un administrador autorizado borre; acceso y borrado restringidos
y auditados); el cambio requiere un ADR nuevo que la reemplace en ese punto.

`PENDIENTE` para ese punto:

- si el tablero de cada cliente muestra también sus propios incidentes, o sólo el
  panel de plataforma;
- dónde vive la clave de cada proveedor, hoy una única `LEDA_LLM_API_KEY` en
  `.env` que se lee al arrancar el proceso;
- si el ajuste por espacio que `model_config` ya admite se expone, y en qué
  superficie.

**Depende de:** nada en el código; sí de una decisión abierta sobre cómo se autentica
quien opera Leda. El enlace por Telegram no sirve acá: autentica contra una
membresía, y en el alta el espacio todavía no existe.

Inventario completo de lo que tiene que poder configurarse, con dónde vive hoy cada
cosa: [`product/plataforma-pendientes.md`](product/plataforma-pendientes.md).

**Cierre:** quien opera Leda entra, da de alta un espacio y lo activa.

### Tablero de cliente

**Entrega:** la superficie que consume el puerto de lectura y permite al cliente
ajustar su propia configuración, con cada cambio atribuido en la auditoría. Incluye
las cadencias del bloque 5 de la entrevista de alta (`nucleo/alta-de-equipo.md`):
qué días y a qué hora Leda pide estado, el resumen grupal y el tope de mensajes
automáticos por persona. Un cambio de cadencia toma efecto sin reiniciar el proceso.

**Depende de:** puerto de lectura (hecho) y su credencial de acceso (hecha: tabla
`acceso_tablero` y migración `0006`, commit `5b1be50`).

**Estado comprobado el 2026-10-04:** la parte de lectura existe. La persona pide su enlace por
chat privado (`pedir_tablero`), lo abre en `GET /tablero/{token}` (commit `48da6fb`) y ve el
estado de su espacio; lo cubre `tests/test_tablero.py`. La parte de configuración (que el cliente
ajuste sus datos, con cada cambio atribuido) no tiene código.

**Cierre:** un integrante abre su enlace, ve el estado de su espacio y sólo el suyo,
y un cambio de configuración queda registrado con su autor.

**Nota (2026-10-04):** el ADR 0017 (decisión 5) descartó la importación por archivo: las tareas
se cargan con un formulario en una plataforma web de tareas, que lleva su propio ADR antes del
código. Si esa plataforma es parte de este tablero, del panel o una superficie aparte, y si hay
que revisar el [`ADR 0004`](decisions/0004-dos-superficies-separadas.md), está `PENDIENTE` en ese
ADR. La parte de configuración de este tablero espera (ADR 0017, decisión 5).

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

**Nota (2026-10-04):** el alcance se recortó al seguimiento, y esta unidad es seguimiento. Hoy
`pending_reply` nunca se escribe y no hay enlace entre la respuesta de una persona y el
recordatorio que la originó. El ADR 0017 (decisión 6) pone esas dos piezas dentro del
seguimiento que se construye ahora; cómo, lo define el ADR 0018. Si antes se exigen las
dependencias que declara esta unidad (grafo de transiciones y desacople del transporte) no lo
decide ningún ADR: `PENDIENTE`, para el plan de la Etapa 2 o el de la Etapa 3.

### Leda orienta

**Entrega:** [`ADR 0007`](decisions/0007-leda-orienta-no-charla.md): cada respuesta que
espera algo cierra con botones concretos y una salida; las listas de tareas son botones
y tocar una ofrece las acciones del diseño §4.6 que ya tienen herramienta. Tras la
tercera ronda por Telegram (2026-09-28), las cuatro reglas generales de la conversación
del [`ADR 0013`](decisions/0013-reglas-generales-de-la-conversacion.md) (pregunta pendiente
como contexto con una sola rama abierta, una respuesta visible por mensaje y toque, estado
real, toques con señal e idempotentes), implementadas el 2026-09-29, y la forma de las
respuestas (T10 de `odd/tasks/leda-orienta.md`).

**Cierre:** la segunda sesión por Telegram real se hizo (2026-09-27) y la tercera
(2026-09-28) mostró que la conversación seguía perdiéndose; el cierre pasa a ser la
cuarta ronda (T11), que muestre menos preguntas innecesarias, ninguna respuesta vaga que
haya que interpretar y ninguna conversación con dos temas abiertos a la vez.

**Nota (2026-10-04):** esta unidad es del flujo B, congelado: no se sigue trabajando sobre su
código. Las reglas del ADR 0013 siguen vigentes como reglas de comportamiento y pasan al diseño
del motor de conversación (ADR 0018).

### Aportes sobre tareas

**Entrega:** texto, foto, video o archivo que una persona suma a una tarea con un motivo:
avisar un avance, sumar información a un bloqueo, devolver una revisión con
observaciones, responder un pedido de estado (diseño §4.6). Recibir archivos de
Telegram y guardarlos por referencia con verificación de integridad, sin interpretarlos;
un aporte no es evidencia. Incluye la transición de revisión a en curso al devolver y el
pedido de estado de Leda al responsable, respetando el volumen de contacto (mecánica
§10).

**Depende de:** Leda orienta.

**Nota (2026-10-04):** el ADR 0017 no la nombra. Parte se superpone con el seguimiento de la
decisión 3b (responder un pedido de estado, sumar información a un bloqueo, pedir cambios en una
revisión) y se construiría con él; lo demás espera (decisión 5). Qué parte es cuál: `PENDIENTE`.

### Aprendizaje de apodos y de aclaraciones

**Entrega:** Leda aprende de lo que ya preguntó, para preguntar menos (pedido del
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
vencimiento, búsqueda de texto) se pueden llevar a PostgreSQL. **Verificado el 2026-10-04**
(repositorio, `DOCS.md` y la versión 3.0.0 instalada; detalle en la sección 7 de
[`research/gestion-del-dialogo-y-arquitecturas-de-agentes.md`](research/gestion-del-dialogo-y-arquitecturas-de-agentes.md)):
licencia MIT; SQLite con FTS5; el token opcional de su API HTTP local sólo protege los
borrados, la exportación y la importación; los datos se separan por nombre de proyecto y nada
impide leer otro proyecto en la misma base; Engram Cloud se puede alojar por cuenta propia
sobre PostgreSQL, con permisos por proyecto denegados por omisión, pero es una capa de
sincronización y la base SQLite local sigue siendo la autoritativa; las relaciones entre
observaciones las juzga el agente con el modelo (`mem_judge`); la búsqueda documentada es FTS5.
**Decisión del usuario (2026-10-04):** Engram se toma sólo como referencia de diseño, no como
componente.

**Insumo: Hermes Agent** (Nous Research, MIT; relevamiento del 2026-09-30 en
[`research/hermes-agent.md`](research/hermes-agent.md)). No sirve como base: agente
personal, memoria en archivos y SQLite, aislamiento por perfil y no por espacio, y
aprende solo por defecto. Sí aporta el mecanismo de esta unidad: después de un turno en
el que la persona corrigió a Leda, un paso aparte detecta qué se podría aprender (un
apodo, un sinónimo del equipo, la tarea a la que apuntaba una referencia) y lo
**propone**; se guarda sólo cuando alguien lo confirma, con las reglas de arriba. En el
flujo del [`ADR 0014`](decisions/0014-flujo-de-un-mensaje.md), lo aprendido vive en
PostgreSQL (etapa 1) y le llega a Jev como pista (etapa 3).

**Idea a investigar, no decidida: memoria por integrante** (propuesta del usuario,
2026-09-24, inspirada en los proyectos de Engram). Tratar la conversación de cada
integrante como un espacio de memoria propio, para que Leda recuerde lo que habló
con esa persona. Es una hipótesis a evaluar, no una decisión de usar Engram ni de
construirla. Condiciones que la investigación tiene que respetar:

- memoria por persona dentro de su espacio, con RLS; lo que una persona le dijo a
  Leda nunca aparece en la respuesta a otra;
- guarda lo que la base no tiene (lo conversado, preferencias, compromisos dichos al
  pasar, apodos y aclaraciones), nunca el estado de las tareas, que se lee en el
  momento: la memoria no reemplaza una lectura vigente;
- se guarda todo lo permitido, pero al modelo le llega sólo lo relacionado con cada
  mensaje (resúmenes por conversación y búsqueda), no el historial completo;
- retención y visibilidad según lo que decida cada cliente.

`PENDIENTE`: medir si mejora las respuestas frente al historial actual de 6 horas
(`contexto.historial`), y definirlo en el mismo ADR que amplíe la excepción de
ADR 0005.

**Precisión (2026-10-04).** La memoria por integrante queda prevista como la tercera parte del
diseño del motor de conversación (estado exacto, registro completo de la conversación y
memoria). Se construye más adelante y con su propio ADR: el aprendizaje persistente sigue
fuera del alcance hasta esa decisión. No reemplaza al estado de la conversación, que tiene que
ser exacto y es lo que falla hoy.

**Insumo a profundizar: Obsidian** ([obsidian.md](https://obsidian.md)). Relevamiento
inicial, 2026-09-24: aplicación de escritorio sobre una carpeta de archivos Markdown
con enlaces, propiedades y extensiones; gratis también para uso comercial
([licencia](https://obsidian.md/license)). No tiene modo servidor ni permisos por
usuario: `obsidian-headless` (beta, 2026) sólo sincroniza con Obsidian Sync, y darle
memoria a un agente se hace con la extensión comunitaria Local REST API, que corre
dentro de la aplicación abierta, una carpeta por instancia. Lectura inicial: como
memoria del núcleo choca igual que Engram (segundo almacén, aislamiento por carpeta
y no por RLS, aplicación de escritorio en un servidor). Único uso con sentido: como
formato en el que un cliente redacte documentación de su proyecto y Leda la lea
como archivos Markdown, sin la aplicación en el servidor. `PENDIENTE`: si existen
bóvedas compartidas con permisos, los términos de Sync y Publish para un servicio
con varios clientes, y si la extensión funciona sin entorno gráfico.

**Depende de:** aclaración con botones (entregada) y la sesión por Telegram real con
datos ficticios, que muestra qué dudas se repiten.

**Cierre:** medido con mensajes reales, las preguntas repetidas bajan sin ninguna
elección equivocada sin preguntar.

### Trabajo que no entra en una tarea

**Entrega:** cuando el trabajo que alguien pide no entra en el margen máximo de una
tarea (ajuste del espacio `horizonte_tarea`, 2 meses por omisión; decisión del usuario del
2026-10-01), Leda ofrece salidas reales y la persona elige. Tres candidatas, pedidas
por el usuario el 2026-10-01 y anotadas bajo el congelamiento:

- **Pedir una extensión:** la fecha fuera del margen se acepta como excepción con
  aprobación explícita, en la línea del umbral de re-aprobación de la mecánica (§7: un
  corrimiento de fecha mayor al umbral del pack requiere aprobación). Decisión pendiente:
  quién aprueba la excepción cuando quien pide ya es el aprobador del responsable (él
  mismo, el nivel siguiente o la autoridad del espacio).
- **Dividirlo en tareas** dentro del objetivo que ya existe: Leda propone las partes y
  la persona confirma cada una. Hoy no existe; en la prueba real del 2026-10-01 ofrecerlo
  sin mecanismo confundió al usuario ("¿dónde apruebo eso?") y se retiró.
- **Proponer un objetivo nuevo:** se crea en estado `propuesto` y va a aprobación según
  la política del espacio (mecánica §3 y §7) hasta quedar `activo`. Corrige de paso una
  diferencia con el núcleo: hoy `crear_objetivo` crea el objetivo directamente `activo`,
  sin aprobación (`src/leda/herramientas.py`, `_crear_objetivo`).

Mientras tanto, la única salida es una fecha dentro del margen, que Leda propone
concreta para aceptarla con un sí.

**Regla de fondo decidida (usuario, 2026-10-01), a construir con esta unidad:** la fecha
de una tarea no puede pasar la del objetivo al que contribuye; si ese objetivo no tiene
fecha, vale la del objetivo de arriba. El margen del espacio (`horizonte_tarea`) queda
como red de seguridad para cuando ningún objetivo de la cadena tiene fecha. Requiere que
los objetivos tengan fecha (hoy ninguno de CoreWork la tiene: el pack declara
`horizonte_meses: 12` en el estratégico y el importador no la convierte) y validar la
fecha cuando se conocen fecha y objetivo, sin importar el orden en que la persona los dé.
Topes, márgenes y fechas de objetivos son configuración del espacio, a cambiar desde la
plataforma cuando exista: no se ajusta el comportamiento de Leda a sus valores actuales.

**Depende de:** el congelamiento levantado (alta, entrega y aprobación cumpliendo el ADR
0014) y el margen máximo de la fecha de una tarea (rama `feat/flujo-de-un-mensaje`).

**Cierre:** en una prueba real, un pedido de trabajo largo termina en una de las salidas
elegida por la persona; ninguna se ofrece sin un mecanismo detrás, y ningún objetivo ni
excepción queda vigente sin la aprobación que corresponde.

**Nota (2026-10-04):** esta unidad nació del alta por chat, que quedó fuera del alcance por
ahora, y dependía de la rama de flujo, que quedó congelada. Espera (ADR 0017, decisión 5). Si la
regla de fondo sobre la fecha de una tarea y la de su objetivo se aplica a las tareas que se
cargan en la plataforma está `PENDIENTE` en el ADR de la plataforma.

### Respuesta que se va escribiendo

**Entrega:** en chat privado, la respuesta de Leda aparece de a poco, como si la fuera
escribiendo, en vez de llegar de golpe (pedido del usuario del 2026-10-01, anotado bajo el
congelamiento). La base existe: el borrador nativo de Telegram (`sendMessageDraft`) que ya
usa el indicador de actividad del ADR 0011. Decisión pendiente antes de construir: hoy el
texto se verifica antes de salir (no inventa fechas, nombres ni botones, constitución §4);
mostrarlo mientras el modelo escribe enseña texto sin verificar. Mostrarlo progresivo
después de verificar es seguro pero no adelanta la respuesta.

**Depende de:** el congelamiento levantado y la unidad de latencia (decisión del usuario:
primero fluidez, después latencia).

**Estado (2026-10-01, decisión del usuario):** se adelanta el **stream real** como
experimento, detrás del ajuste `stream` del espacio, sólo en el alta conversada y en chat
privado, para verlo en Telegram real; el mensaje final sigue siendo el verificado y sale
por el outbox. **Pendiente:** probar la otra variante (mostrar progresivo después de
verificar) cuando se trabaje la latencia, y elegir entre las dos viéndolas en real.
Probado en real el 2026-10-01 (se ve el texto crecer y hasta el reintento del verificador);
queda **encendido** en `leda_flujo` porque ayuda a ver cómo se comporta Leda (decisión
del usuario); en la rama sigue apagado por omisión.

**Nota (2026-10-04):** el experimento vivía en el alta conversada del flujo C, congelado. El
ADR 0018 no lo incluye: queda fuera de la prueba chica y se decide después (documento de la
unidad del Motor, "Qué se trae de la rama congelada").

### Mensajes de voz

**Entrega:** la persona manda un audio con lo que quiere o necesita, Leda lo convierte a
texto y lo procesa por el mismo flujo que un mensaje escrito (pedido del usuario del
2026-10-02, anotado bajo el congelamiento). Hoy un audio recibe respuesta (regla 2 del
ADR 0013), pero no se transcribe: sólo se procesa su epígrafe como texto.

**Por qué la conversación por texto es la base:** un audio transcrito es texto libre,
hablado como habla la persona, con varias cosas juntas y sin seguir los pasos del alta.
Cuanto más humana y fluida sea Leda por texto (enmienda del ADR 0013 del 2026-10-02,
"botones para elegir, texto para decir", y el paso de los circuitos al flujo del
ADR 0014), más resuelto queda el camino para los audios: la transcripción entra como un
mensaje más. Por eso los circuitos se pasan al flujo nuevo antes.

**Decisiones pendientes antes de construir:** qué servicio transcribe y dónde vive su
clave (ajuste de la plataforma); qué se guarda del audio y por cuánto tiempo (retención,
hoy fijada por el ADR 0002); qué hace Leda cuando la transcripción sale dudosa o vacía
(nunca fallar en silencio). Las confirmaciones de la constitución §7 siguen igual: un
efecto se confirma con su vista previa, venga el pedido escrito o hablado.

**Depende de:** el congelamiento levantado y los circuitos del alta, la entrega y la
aprobación en el flujo nuevo (`odd/tasks/circuitos-al-flujo-nuevo.md`, rama de flujo).

**Nota (2026-10-04):** esa dependencia nombraba los circuitos del flujo C, congelado. Espera
(ADR 0017, decisión 5); de qué depende con el motor de conversación se fija al ordenar "Anotado
para más adelante" (`PENDIENTE`).

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
